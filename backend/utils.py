# backend/utils.py

import fitz  # pymupdf
from docx import Document


def extract_text_from_pdf(file_path):
    """Извлекает текст из PDF с помощью pymupdf (fitz)"""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_docx(file_path):
    """Извлекает текст из .docx"""
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_txt(file_path):
    """Извлекает текст из .txt"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_text(file_path):
    """Определяет тип файла и вызывает соответствующий парсер"""
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")