"""
Document Parsers
Extract text content from various file formats (PDF, DOCX, TXT)
"""
import os
from typing import Optional
import PyPDF2
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text content
    """
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from DOCX file
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        Extracted text content
    """
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")


def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from TXT file
    
    Args:
        file_path: Path to TXT file
        
    Returns:
        Extracted text content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text.strip()
    except UnicodeDecodeError:
        # Try alternative encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from TXT: {str(e)}")
    except Exception as e:
        raise Exception(f"Error extracting text from TXT: {str(e)}")


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from file based on extension
    
    Args:
        file_path: Path to file
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If file type is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Route to appropriate parser
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def validate_text_content(text: str, min_length: int = 10) -> bool:
    """
    Validate that extracted text is meaningful
    
    Args:
        text: Extracted text
        min_length: Minimum acceptable text length
        
    Returns:
        True if text is valid, False otherwise
    """
    if not text or len(text.strip()) < min_length:
        return False
    return True
