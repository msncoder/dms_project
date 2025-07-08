# documents/ocr_utils.py

from PIL import Image
import pytesseract
import os

def extract_text(image_path):
    """
    Extract text from a given image or scanned PDF file using Tesseract OCR.
    """
    if not os.path.exists(image_path):
        return "Image path not found."

    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        return f"OCR error: {e}"
