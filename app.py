from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def images_to_pdf(images, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    for image in images:
        img = Image.open(image)
        img_width, img_height = img.size
        aspect_ratio = img_height / float(img_width)
        c.drawImage(image, 0, 0, width=letter[0], height=letter[0] * aspect_ratio)
        c.showPage()
    c.save()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('file')
        images = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                images.append(filepath)
        if images:
            output_filename = request.form['output_filename']
            output_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{output_filename}.pdf')
            images_to_pdf(images, output_pdf_path)
            return send_file(output_pdf_path, as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
