"""PDF metadata extraction tool for getting document information."""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PDFInfoError(Exception):
    """Exception raised for PDF info extraction errors."""

    pass


@dataclass
class PDFInfoResult:
    """Result of PDF metadata extraction."""

    success: bool
    error_message: Optional[str]
    file_path: str
    file_size_bytes: int
    page_count: int
    page_dimensions: List[Dict[str, Any]]
    pdf_version: Optional[str]
    is_encrypted: bool
    is_linearized: Optional[bool]
    creation_date: Optional[str]
    modification_date: Optional[str]
    title: Optional[str]
    author: Optional[str]
    subject: Optional[str]
    keywords: Optional[str]
    producer: Optional[str]
    creator: Optional[str]
    text_content: Optional[List[str]]
    extraction_time_seconds: Optional[float]


def extract_pdf_info(
    file_path: Optional[str],
    include_text: bool = False,
    password: Optional[str] = None,
) -> PDFInfoResult:
    """
    Extract metadata and information from a PDF file.

    Args:
        file_path: Path to the PDF file to analyze
        include_text: If True, extract text content from all pages
        password: Password for encrypted PDFs (if needed)

    Returns:
        PDFInfoResult containing PDF metadata and information

    Raises:
        PDFInfoError: If file path is invalid or file cannot be read
    """
    start_time = time.time()

    # Validate input
    if file_path is None:
        raise PDFInfoError("File path cannot be None")
    if not file_path:
        raise PDFInfoError("File path cannot be empty")

    path = Path(file_path)
    
    # Check file existence and get file size
    try:
        file_size = path.stat().st_size
    except FileNotFoundError:
        raise PDFInfoError(f"File not found: {file_path}")
    except PermissionError as e:
        raise PDFInfoError(f"Cannot access file: {e}")
    except Exception as e:
        raise PDFInfoError(f"Cannot access file: {e}")

    # Initialize result with error state
    result = PDFInfoResult(
        success=False,
        error_message=None,
        file_path=file_path,
        file_size_bytes=file_size,
        page_count=0,
        page_dimensions=[],
        pdf_version=None,
        is_encrypted=False,
        is_linearized=None,
        creation_date=None,
        modification_date=None,
        title=None,
        author=None,
        subject=None,
        keywords=None,
        producer=None,
        creator=None,
        text_content=None,
        extraction_time_seconds=None,
    )

    try:
        # Open and read PDF
        with open(file_path, "rb") as file:
            pdf_reader = PdfReader(file)

            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                result.is_encrypted = True
                if password:
                    try:
                        pdf_reader.decrypt(password)
                    except Exception as e:
                        result.error_message = f"Failed to decrypt PDF: {e}"
                        result.extraction_time_seconds = time.time() - start_time
                        return result
                elif not password:
                    # For non-encrypted PDFs, this should not happen
                    # But if it does, we'll try to continue
                    pass

            # Get basic PDF information
            result.page_count = len(pdf_reader.pages)
            # Get PDF version from document info
            try:
                result.pdf_version = getattr(pdf_reader, "pdf_version", None)
                if not result.pdf_version:
                    # Try alternative approach
                    result.pdf_version = getattr(pdf_reader, "pdf_header", None)
            except Exception:
                result.pdf_version = None

            # Extract metadata
            metadata = pdf_reader.metadata
            if metadata:
                result.creation_date = _format_pdf_date(metadata.get("/CreationDate"))
                result.modification_date = _format_pdf_date(metadata.get("/ModDate"))
                result.title = metadata.get("/Title", "")
                result.author = metadata.get("/Author", "")
                result.subject = metadata.get("/Subject", "")
                result.keywords = metadata.get("/Keywords", "")
                result.producer = metadata.get("/Producer", "")
                result.creator = metadata.get("/Creator", "")

            # Extract page dimensions
            page_dimensions = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    # Get page dimensions (in points)
                    mediabox = page.mediabox
                    width = float(mediabox.width)
                    height = float(mediabox.height)

                    page_dimensions.append({
                        "width": width,
                        "height": height,
                        "unit": "pt"
                    })
                except Exception:
                    # If we can't get dimensions for a page, use default
                    page_dimensions.append({
                        "width": 612.0,  # Default letter size
                        "height": 792.0,
                        "unit": "pt"
                    })

            result.page_dimensions = page_dimensions

            # Extract text content if requested
            if include_text:
                text_content = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        text_content.append(text)
                    except Exception:
                        # If text extraction fails for a page, add empty string
                        text_content.append("")
                result.text_content = text_content

            # Check if PDF is linearized (fast web view)
            # This is a simple heuristic - proper detection would require
            # more detailed PDF structure analysis
            result.is_linearized = False  # Default to False for now

            result.success = True

    except PdfReadError as e:
        result.error_message = f"Not a valid PDF file: {e}"
    except Exception as e:
        result.error_message = f"Failed to read PDF: {e}"

    result.extraction_time_seconds = time.time() - start_time
    return result


def _format_pdf_date(pdf_date: Optional[str]) -> Optional[str]:
    """
    Format PDF date string to ISO format.
    
    PDF dates are often in format: D:YYYYMMDDHHmmSSOHH'mm'
    where O is the timezone offset indicator (+ or -)
    """
    if not pdf_date:
        return None
    
    try:
        # Remove D: prefix if present
        if pdf_date.startswith("D:"):
            pdf_date = pdf_date[2:]
        
        # Extract basic date components (YYYYMMDDHHMMSS)
        if len(pdf_date) >= 14:
            year = pdf_date[0:4]
            month = pdf_date[4:6]
            day = pdf_date[6:8]
            hour = pdf_date[8:10]
            minute = pdf_date[10:12]
            second = pdf_date[12:14]
            
            # Check for timezone information
            timezone_str = ""
            if len(pdf_date) > 14:
                # Look for timezone offset (e.g., +05'30' or -08'00')
                tz_part = pdf_date[14:]
                if tz_part.startswith(('+', '-')):
                    # Extract timezone
                    tz_sign = tz_part[0]
                    tz_hours = tz_part[1:3] if len(tz_part) > 2 else "00"
                    # Look for minutes part after apostrophe
                    if "'" in tz_part and len(tz_part) > tz_part.index("'") + 2:
                        tz_mins = tz_part[tz_part.index("'") + 1:tz_part.index("'") + 3]
                    else:
                        tz_mins = "00"
                    timezone_str = f"{tz_sign}{tz_hours}:{tz_mins}"
                else:
                    timezone_str = "Z"
            else:
                timezone_str = "Z"
            
            # Create ISO format date with timezone
            return f"{year}-{month}-{day}T{hour}:{minute}:{second}{timezone_str}"
        elif len(pdf_date) >= 8:
            # Just date without time
            year = pdf_date[0:4]
            month = pdf_date[4:6]
            day = pdf_date[6:8]
            return f"{year}-{month}-{day}T00:00:00Z"
        else:
            return None
    except Exception:
        # If date parsing fails, return the original string
        return pdf_date