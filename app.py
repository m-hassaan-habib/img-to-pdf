import os
from flask import Flask, render_template, request, send_file
from PIL import Image
from reportlab.pdfgen import canvas

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

A4_WIDTH, A4_HEIGHT = 2480, 3508

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("images")
    if len(files) < 1 or len(files) > 9:
        return "Please upload 1 to 9 images.", 400

    image_paths = []
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        image_paths.append(file_path)

    pdf_path = generate_pdf(image_paths)
    return send_file(pdf_path, as_attachment=True)

def generate_pdf(image_paths):
    images = [Image.open(img).convert("RGB") for img in image_paths]

    row_height = A4_HEIGHT // 3
    col_width = A4_WIDTH // 3

    a4_canvas = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")
    x_offset, y_offset = 0, 0

    for i, img in enumerate(images):
        img_resized = img.resize((col_width, row_height))
        a4_canvas.paste(img_resized, (x_offset, y_offset))

        x_offset += col_width
        if (i + 1) % 3 == 0:
            x_offset = 0
            y_offset += row_height

    output_pdf = os.path.join(OUTPUT_FOLDER, "output.pdf")
    temp_image_path = os.path.join(OUTPUT_FOLDER, "output_a4.jpg")
    a4_canvas.save(temp_image_path, "JPEG")

    c = canvas.Canvas(output_pdf, pagesize=(A4_WIDTH, A4_HEIGHT))
    c.drawImage(temp_image_path, 0, 0, A4_WIDTH, A4_HEIGHT)
    c.save()

    return output_pdf

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
