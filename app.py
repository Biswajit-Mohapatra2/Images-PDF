from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import io
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Set up logging
logging.basicConfig(level=logging.DEBUG)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def images_to_pdf(images):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    for image in images:
        try:
            img = Image.open(image)
            img_width, img_height = img.size
            aspect_ratio = img_height / float(img_width)
            c.drawImage(image, 0, 0, width=letter[0], height=letter[0] * aspect_ratio)
            c.showPage()
        except Exception as e:
            logging.error(f"Error processing image {image}: {str(e)}")
    c.save()
    buffer.seek(0)
    return buffer

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            logging.warning("No file part in the request")
            return redirect(request.url)
        
        files = request.files.getlist('file')
        images = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                images.append(filepath)
        
        if images:
            output_filename = request.form.get('output_filename', 'output')
            try:
                pdf_buffer = images_to_pdf(images)
                
                # Clean up uploaded files
                for image in images:
                    os.remove(image)
                
                return send_file(
                    pdf_buffer,
                    as_attachment=True,
                    download_name=f"{output_filename}.pdf",
                    mimetype='application/pdf'
                )
            except Exception as e:
                logging.error(f"Error generating PDF: {str(e)}")
                return "Error generating PDF", 500
        else:
            logging.warning("No valid images uploaded")
            return "No valid images uploaded", 400
        
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)