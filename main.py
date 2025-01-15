from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader
from docx import Document
from fpdf import FPDF
import os
import uuid

app = FastAPI()

TEMP_DIR = "./temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# PDF to DOC route
@app.post("/convert/pdf-to-doc")
async def convert_pdf_to_doc(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a PDF.")
    
    try:
        # Save the uploaded file
        input_file_path = f"{TEMP_DIR}/{uuid.uuid4()}.pdf"
        with open(input_file_path, "wb") as f:
            f.write(file.file.read())

        # Convert PDF to DOC
        reader = PdfReader(input_file_path)
        doc = Document()
        for page in reader.pages:
            doc.add_paragraph(page.extract_text())
        
        # Save DOC file
        output_file_path = f"{TEMP_DIR}/{uuid.uuid4()}.docx"
        doc.save(output_file_path)

        return FileResponse(output_file_path, filename="converted.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    finally:
        # Cleanup
        if os.path.exists(input_file_path):
            os.remove(input_file_path)

@app.post("/convert/doc-to-pdf")
async def convert_doc_to_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a DOCX.")
    
    try:
        # Save the uploaded file
        input_file_path = f"{TEMP_DIR}/{uuid.uuid4()}.docx"
        with open(input_file_path, "wb") as f:
            f.write(file.file.read())

        # Read DOCX and convert to PDF
        doc = Document(input_file_path)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for paragraph in doc.paragraphs:
            text = paragraph.text.encode("utf-8", "ignore").decode("utf-8")
            pdf.multi_cell(0, 10, text)

        # Save PDF file
        output_file_path = f"{TEMP_DIR}/{uuid.uuid4()}.pdf"
        pdf.output(output_file_path)

        return FileResponse(output_file_path, filename="converted.pdf", media_type="application/pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    finally:
        # Cleanup
        if os.path.exists(input_file_path):
            os.remove(input_file_path)


@app.on_event("shutdown")
def cleanup_temp_files():
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
