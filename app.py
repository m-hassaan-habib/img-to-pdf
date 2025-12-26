import io
import time
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024

A4_WIDTH, A4_HEIGHT = 2480, 3508

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/upload")
def upload_files():
    files = request.files.getlist("images")
    if not files or len(files) < 1 or len(files) > 9:
        return "Please upload 1 to 9 images.", 400

    images = []
    for f in files:
        try:
            img = Image.open(f.stream).convert("RGB")
            images.append(img)
        except Exception:
            return "One or more files are not valid images.", 400

    pdf_bytes = build_pdf(images)
    filename = f"images_a4_{int(time.time())}.pdf"

    return send_file(
        pdf_bytes,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
        max_age=0,
    )

def build_pdf(images):
    row_height = A4_HEIGHT // 3
    col_width = A4_WIDTH // 3

    a4_img = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")
    x_offset, y_offset = 0, 0

    for i, img in enumerate(images[:9]):
        img_resized = img.resize((col_width, row_height))
        a4_img.paste(img_resized, (x_offset, y_offset))

        x_offset += col_width
        if (i + 1) % 3 == 0:
            x_offset = 0
            y_offset += row_height

    jpg_buf = io.BytesIO()
    a4_img.save(jpg_buf, format="JPEG", quality=92, optimize=True)
    jpg_buf.seek(0)

    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=(A4_WIDTH, A4_HEIGHT))
    c.drawImage(ImageReader(jpg_buf), 0, 0, A4_WIDTH, A4_HEIGHT)
    c.showPage()
    c.save()

    pdf_buf.seek(0)
    return pdf_buf

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
