# documents/tasks.py
from celery import shared_task
from .models import Document
from .ocr_utils import extract_text, extract_pdf_text, extract_scanned_pdf_text, extract_docx_text, extract_excel_text, extract_pptx_text, generate_summary
import os
from .ai_summarizer import generate_summary

@shared_task
def process_document(document_id, file_path):
    from .models import Document  # Avoid circular import
    doc = Document.objects.get(id=document_id)
    ext = os.path.splitext(file_path)[1].lower()
    extracted_text = ""

    try:
        if ext in ['.jpg', '.jpeg', '.png']:
            extracted_text = extract_text(file_path)
        elif ext == '.pdf':
            try:
                extracted_text = extract_pdf_text(file_path)
                if not extracted_text.strip():
                    raise ValueError("Empty PDF text, fallback to OCR")
            except:
                extracted_text = extract_scanned_pdf_text(file_path)
        elif ext == '.docx':
            extracted_text = extract_docx_text(file_path)
        elif ext in ['.xls', '.xlsx']:
            extracted_text = extract_excel_text(file_path)
        elif ext in ['.ppt', '.pptx']:
            extracted_text = extract_pptx_text(file_path)
        else:
            extracted_text = "Unsupported file type."

        summary = generate_summary(extracted_text)

        doc.extracted_text = extracted_text
        doc.summary = summary
        doc.save()

    except Exception as e:
        doc.extracted_text = f"Extraction failed: {str(e)}"
        doc.summary = "Summary skipped due to error."
        doc.save()
