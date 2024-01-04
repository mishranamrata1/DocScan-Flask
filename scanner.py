import cv2
import os
import numpy as np

def scan_document(file_path):

    if not os.path.exists(file_path):
        return None


    img=cv2.imread(file_path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blockSize = 5
    C = 2
    _, otsu_threshold = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((5, 5))
    eroded_image = cv2.erode(otsu_threshold, kernel, iterations=1)
    closed_image = cv2.morphologyEx(eroded_image, cv2.MORPH_CLOSE, kernel,otsu_threshold, iterations=5)
    contours, _ = cv2.findContours(closed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    initialimage = img
    # final = cv2.drawContours(initialimage, contours, -1,(255,0,0),40)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Get the biggest contour (first contour in the sorted list)
    if contours:
        biggest_contour = contours[0]
        print("Area of the biggest contour:", cv2.contourArea(biggest_contour))
        print("Number of vertices:", len(biggest_contour))
    else:
        print("No contours found.")

    # Draw the biggest contour on a separate image
    contour_image = cv2.cvtColor(closed_image, cv2.COLOR_GRAY2BGR)

    if contours:
        biggest_contour = contours[0]
        
        # Approximate the biggest contour with a polygon
        epsilon = 0.01 * cv2.arcLength(biggest_contour, True)
        approx_polygon = cv2.approxPolyDP(biggest_contour, epsilon, True)
        mask = np.zeros_like(gray_image)

        # Convert the polygon to a list of corner points
        corner_points = [point[0] for point in approx_polygon]
        region_of_interest = cv2.bitwise_and(img, img, mask=mask)

        # Print the corner points
        print("Corner Points:")
        for point in corner_points:
            print(point)
            
        # Calculate the centroid of corner points
        centroid = np.mean(corner_points, axis=0)

        # Divide corner points into top and bottom groups
        top_corners = [point for point in corner_points if point[1] < centroid[1]]
        bottom_corners = [point for point in corner_points if point[1] >= centroid[1]]

        # Sort each group based on x-coordinate
        top_corners = sorted(top_corners, key=lambda x: x[0])
        bottom_corners = sorted(bottom_corners, key=lambda x: x[0])

        # Assign sorted corners
        top_left = top_corners[0]
        top_right = top_corners[1]
        bottom_left = bottom_corners[0]
        bottom_right = bottom_corners[1]

        # Define the target rectangle size for perspective transformation
        target_width = 4000
        target_height = 4000
        target_points = np.array([[0, 0], [target_width - 1, 0], [target_width - 1, target_height - 1], [0, target_height - 1]], dtype=np.float32)

        # Compute the perspective transformation matrix
        src_points = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)
        matrix = cv2.getPerspectiveTransform(src_points, target_points)

        #   matrix = cv2.getPerspectiveTransform(approx_polygon.astype(np.float32), target_points)

        # Apply the perspective transformation to the original image
        transformed_image = cv2.warpPerspective(img, matrix, (target_width, target_height))

    scanned_filename = 'scanned_' + os.path.basename(file_path)
    scanned_file_path = os.path.join('results', scanned_filename)
    cv2.imwrite(scanned_file_path, transformed_image)

    return scanned_file_path