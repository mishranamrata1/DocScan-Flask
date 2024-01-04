from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from scanner import scan_document  # Import the scan_document function from scanner.py
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

RESULTS_FOLDER = 'results'
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        scanned_filename = scan_document(filename)  # Call your scanning function from scanner.py
        scanned_filename = scanned_filename.replace('\\', '/')
        # return redirect(url_for('show_scanned', filename=scanned_filename))
        return render_template('scanned.html', filename=scanned_filename)

@app.route('/show_scanned/<path:filename>')
def show_scanned(filename):
    print(filename)
    file_path = os.path.join(filename)
    app.logger.debug("File Path: %s", file_path)
    print(file_path)
    if os.path.isfile(file_path):
        return send_file(file_path)
    else:
        app.logger.error("File not found: %s", file_path)
        return "File not found", 404


if __name__ == '__main__':
    app.run(debug=True)
