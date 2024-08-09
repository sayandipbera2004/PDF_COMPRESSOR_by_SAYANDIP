import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import subprocess
import uuid

app = Flask(__name__)

# Configuration for file storage
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['COMPRESSED_FOLDER'] = 'compressed/'

# Ensure the upload and compressed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['COMPRESSED_FOLDER'], exist_ok=True)

def compress_pdf(input_file_path, output_file_path, compression_level):
    # Compression settings based on user selection
    quality = {
        "high": "/screen",    # high compression, lower quality
        "medium": "/ebook",   # medium compression, good quality
        "low": "/prepress"    # low compression, best quality
    }[compression_level]

    command = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={quality}",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_file_path}", input_file_path
    ]

    subprocess.run(command, check=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        compression = request.form['compression']

        if file and file.filename.endswith('.pdf'):
            # Secure the filename and generate unique name to avoid conflicts
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            output_file_path = os.path.join(app.config['COMPRESSED_FOLDER'], unique_filename)

            # Save the uploaded file
            file.save(input_file_path)

            # Apply compression
            compress_pdf(input_file_path, output_file_path, compression)

            # Return the compressed file for download
            return send_file(output_file_path, as_attachment=True, download_name=f"compressed_{original_filename}")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
