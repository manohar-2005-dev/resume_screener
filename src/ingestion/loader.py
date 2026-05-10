import logging # this helps in track application flow , debug errors , monitor systems , record events
from pathlib import Path# this module provides an object-oriented interface for working with filesystem paths, making it easier to manipulate and interact with file paths in a platform-independent way.
from typing import Optional# this module provides support for type hints, allowing you to specify the expected types of variables, function parameters, and return values, which can improve code readability and help with static type checking.

import pypdf 
import docx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: Path) -> str:
    
    try:
        reader = pypdf.PdfReader(file_path)
        pages_text =[]
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                pages_text.append(extracted)
        return "\n".join(pages_text)
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""
def extract_text_from_docx(file_path: Path) -> str:
    
    try:
        doc = docx.Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""
def extract_text_from_txt(file_path: Path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {e}")
        return ""
def load_resume(file_path: Path) -> Optional[dict]:
    #main entry point for resume ingestion 
    #accepts pdf, docx , txt formats
    
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    
    extension = path.suffix.lower()
    extractors ={
        ".pdf": extract_text_from_pdf,
        ".docx": extract_text_from_docx,
        ".txt": extract_text_from_txt
    }
    
    if extension not in extractors:
        logger.error(f"Unsupported file format: {extension}")
        return None
    try:
        raw_text = extractors[extension](path)
        
        # warn if little text was extracted
        if len(raw_text.strip()) < 50:
            logger.warning(f" very little text exttracted from {path.name}")
            
        return {
            "file_name": path.name,
            "file_type": extension.lstrip("."),
            "raw_text": raw_text,
            "status": "success" if raw_text.strip() else "empty"
        }
    except Exception as e:
        logger.error(f"Error loading resume: {e}")
        return None 