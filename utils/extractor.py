"""
utils/extractor.py

Handles pulling raw text out of uploaded resume files.
Supports PDF, DOCX, and plain text. 
"""

import os
import re

# lazy imports so we don't crash if one lib is missing
def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.pdf':
        return _extract_pdf(filepath)
    elif ext in ('.docx', '.doc'):
        return _extract_docx(filepath)
    elif ext == '.txt':
        return _extract_txt(filepath)
    else:
        return ""


def _extract_pdf(filepath):
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        # fallback to PyPDF2
        try:
            import PyPDF2
            text = ""
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text.strip()
        except Exception:
            return ""


def _extract_docx(filepath):
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception:
        return ""


def _extract_txt(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ""


def clean_text(text):
    """Basic cleanup - remove extra whitespace etc"""
    if not text:
        return ""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def extract_email(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None


def extract_phone(text):
    pattern = r'(\+91[\-\s]?)?[6-9]\d{9}|(\+1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}'
    matches = re.findall(pattern, text)
    if matches:
        # flatten tuple matches
        for m in matches:
            val = ''.join(m).strip()
            if val:
                return val
    return None


def extract_linkedin(text):
    pattern = r'linkedin\.com/in/[\w\-]+'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None
