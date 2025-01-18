from flask import Flask, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from docx import Document
from pdf2docx import Converter
from fpdf import FPDF
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set upload and output folder paths
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Helper function: Convert DOC to PDF
def doc_to_pdf(doc_path, pdf_path):
    document = Document(doc_path)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for paragraph in document.paragraphs:
        pdf.multi_cell(0, 10, paragraph.text.encode("latin1", errors="replace").decode("latin1"))

    pdf.output(pdf_path)

# Helper function: Convert PDF to DOC
def pdf_to_doc(pdf_path, doc_path):
    cv = Converter(pdf_path)
    cv.convert(doc_path, start=0, end=None)
    cv.close()

@app.route("/convert/doc-to-pdf", methods=["POST"])
def convert_doc_to_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith(".docx"):
        return jsonify({"error": "Invalid file type. Only .docx files are supported."}), 400

    # Save the uploaded DOC file
    filename = secure_filename(file.filename)
    doc_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(doc_path)

    # Convert DOC to PDF
    pdf_filename = filename.rsplit(".", 1)[0] + ".pdf"
    pdf_path = os.path.join(OUTPUT_FOLDER, pdf_filename)
    doc_to_pdf(doc_path, pdf_path)

    # Delete the uploaded DOC file to save space
    os.remove(doc_path)

    # Send the converted file and delete it afterwards
    response = send_file(pdf_path, as_attachment=True)
    os.remove(pdf_path)
    return response

@app.route("/convert/pdf-to-doc", methods=["POST"])
def convert_pdf_to_doc():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Invalid file type. Only .pdf files are supported."}), 400

    # Save the uploaded PDF file
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(pdf_path)

    # Convert PDF to DOC
    doc_filename = filename.rsplit(".", 1)[0] + ".docx"
    doc_path = os.path.join(OUTPUT_FOLDER, doc_filename)
    pdf_to_doc(pdf_path, doc_path)

    # Delete the uploaded PDF file to save space
    os.remove(pdf_path)

    # Send the converted file and delete it afterwards
    response = send_file(doc_path, as_attachment=True)
    os.remove(doc_path)
    return response

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "API is running"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
