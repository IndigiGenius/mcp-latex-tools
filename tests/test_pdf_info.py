"""Tests for PDF info extraction tool."""

import tempfile
from pathlib import Path

import pytest

from mcp_latex_tools.tools.pdf_info import extract_pdf_info, PDFInfoError, PDFInfoResult


class TestExtractPDFInfo:
    """Test PDF info extraction functionality."""

    def test_extract_pdf_info_with_valid_file_returns_metadata(self):
        """Test PDF info extraction from a valid PDF file."""
        # Use the simple.pdf fixture
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        result = extract_pdf_info(str(pdf_path))
        
        assert isinstance(result, PDFInfoResult)
        assert result.success is True
        assert result.error_message is None
        assert result.file_path == str(pdf_path)
        assert result.file_size_bytes > 0
        assert result.page_count > 0
        assert result.page_dimensions is not None
        assert len(result.page_dimensions) == result.page_count
        assert result.creation_date is not None
        assert result.modification_date is not None
        assert result.title is not None or result.title == ""
        assert result.author is not None or result.author == ""
        assert result.subject is not None or result.subject == ""
        assert result.producer is not None or result.producer == ""
        assert result.creator is not None or result.creator == ""
        assert result.extraction_time_seconds is not None
        assert result.extraction_time_seconds > 0

    def test_extract_pdf_info_with_multipage_pdf_returns_all_pages(self):
        """Test PDF info extraction handles multiple pages correctly."""
        # Create a temporary multi-page PDF for testing
        # This would normally be a more complex PDF, but we'll use simple.pdf
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        result = extract_pdf_info(str(pdf_path))
        
        assert isinstance(result, PDFInfoResult)
        assert result.success is True
        assert result.page_count >= 1
        assert len(result.page_dimensions) == result.page_count
        
        # Check that all page dimensions are valid
        for i, dimensions in enumerate(result.page_dimensions):
            assert "width" in dimensions
            assert "height" in dimensions
            assert dimensions["width"] > 0
            assert dimensions["height"] > 0
            assert "unit" in dimensions
            assert dimensions["unit"] in ["pt", "mm", "in", "cm"]

    def test_extract_pdf_info_includes_detailed_metadata(self):
        """Test that PDF info extraction includes comprehensive metadata."""
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        result = extract_pdf_info(str(pdf_path))
        
        assert isinstance(result, PDFInfoResult)
        assert result.success is True
        
        # Check file-level metadata
        assert result.file_size_bytes > 0
        assert result.pdf_version is not None
        assert result.is_encrypted is not None
        assert result.is_linearized is not None
        
        # Check document metadata
        assert hasattr(result, 'creation_date')
        assert hasattr(result, 'modification_date')
        assert hasattr(result, 'title')
        assert hasattr(result, 'author')
        assert hasattr(result, 'subject')
        assert hasattr(result, 'keywords')
        assert hasattr(result, 'producer')
        assert hasattr(result, 'creator')

    def test_extract_pdf_info_with_nonexistent_file_raises_error(self):
        """Test PDF info extraction with non-existent file."""
        with pytest.raises(PDFInfoError) as excinfo:
            extract_pdf_info("/nonexistent/file.pdf")
        
        assert "not found" in str(excinfo.value).lower()

    def test_extract_pdf_info_with_empty_path_raises_error(self):
        """Test PDF info extraction with empty file path."""
        with pytest.raises(PDFInfoError) as excinfo:
            extract_pdf_info("")
        
        assert "cannot be empty" in str(excinfo.value).lower()

    def test_extract_pdf_info_with_none_path_raises_error(self):
        """Test PDF info extraction with None file path."""
        with pytest.raises(PDFInfoError) as excinfo:
            extract_pdf_info(None)
        
        assert "cannot be none" in str(excinfo.value).lower()

    def test_extract_pdf_info_with_invalid_pdf_file_returns_error(self):
        """Test PDF info extraction with invalid PDF file."""
        # Create a temporary file with invalid PDF content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("This is not a valid PDF file")
            invalid_pdf_path = f.name
        
        try:
            result = extract_pdf_info(invalid_pdf_path)
            
            assert isinstance(result, PDFInfoResult)
            assert result.success is False
            assert result.error_message is not None
            assert "invalid" in result.error_message.lower() or "corrupt" in result.error_message.lower() or "valid" in result.error_message.lower()
            assert result.file_path == invalid_pdf_path
            assert result.page_count == 0
            assert result.page_dimensions == []
            
        finally:
            Path(invalid_pdf_path).unlink()

    def test_extract_pdf_info_with_non_pdf_file_returns_error(self):
        """Test PDF info extraction with non-PDF file."""
        # Use a text file instead of PDF
        tex_path = Path(__file__).parent / "fixtures" / "simple.tex"
        
        result = extract_pdf_info(str(tex_path))
        
        assert isinstance(result, PDFInfoResult)
        assert result.success is False
        assert result.error_message is not None
        assert "not a valid pdf" in result.error_message.lower()

    def test_extract_pdf_info_with_include_text_flag(self):
        """Test PDF info extraction with text content extraction."""
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        result = extract_pdf_info(str(pdf_path), include_text=True)
        
        assert isinstance(result, PDFInfoResult)
        assert result.success is True
        assert result.text_content is not None
        assert isinstance(result.text_content, list)
        assert len(result.text_content) == result.page_count
        
        # Check that text content is extracted for each page
        for page_text in result.text_content:
            assert isinstance(page_text, str)

    def test_extract_pdf_info_without_include_text_flag(self):
        """Test PDF info extraction without text content extraction."""
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        result = extract_pdf_info(str(pdf_path), include_text=False)
        
        assert isinstance(result, PDFInfoResult)
        assert result.success is True
        assert result.text_content is None

    def test_extract_pdf_info_with_password_protected_pdf(self):
        """Test PDF info extraction with password-protected PDF."""
        # This test would require a password-protected PDF fixture
        # For now, we'll test the parameter structure
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        # Test with wrong password - should handle gracefully
        result = extract_pdf_info(str(pdf_path), password="wrongpassword")
        
        assert isinstance(result, PDFInfoResult)
        # Should still succeed for non-encrypted PDF
        assert result.success is True

    def test_extract_pdf_info_performance_timing(self):
        """Test that PDF info extraction includes timing information."""
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        result = extract_pdf_info(str(pdf_path))
        
        assert isinstance(result, PDFInfoResult)
        assert result.success is True
        assert result.extraction_time_seconds is not None
        assert result.extraction_time_seconds > 0
        assert result.extraction_time_seconds < 5.0  # Should be fast

    def test_pdf_info_result_properties(self):
        """Test PDFInfoResult dataclass properties."""
        result = PDFInfoResult(
            success=True,
            error_message=None,
            file_path="/test/file.pdf",
            file_size_bytes=1024,
            page_count=2,
            page_dimensions=[
                {"width": 612, "height": 792, "unit": "pt"},
                {"width": 612, "height": 792, "unit": "pt"}
            ],
            pdf_version="1.4",
            is_encrypted=False,
            is_linearized=True,
            creation_date="2023-01-01T00:00:00Z",
            modification_date="2023-01-01T00:00:00Z",
            title="Test PDF",
            author="Test Author",
            subject="Test Subject",
            keywords="test, pdf",
            producer="Test Producer",
            creator="Test Creator",
            text_content=["Page 1 text", "Page 2 text"],
            extraction_time_seconds=0.5
        )
        
        assert result.success is True
        assert result.error_message is None
        assert result.file_path == "/test/file.pdf"
        assert result.file_size_bytes == 1024
        assert result.page_count == 2
        assert len(result.page_dimensions) == 2
        assert result.pdf_version == "1.4"
        assert result.is_encrypted is False
        assert result.is_linearized is True
        assert result.title == "Test PDF"
        assert result.author == "Test Author"
        assert result.text_content == ["Page 1 text", "Page 2 text"]
        assert result.extraction_time_seconds == 0.5

    def test_pdf_info_error_exception(self):
        """Test PDFInfoError exception."""
        error = PDFInfoError("Test PDF info error")
        assert str(error) == "Test PDF info error"
        assert isinstance(error, Exception)

    def test_extract_pdf_info_with_detailed_page_info(self):
        """Test that page dimensions include detailed information."""
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        result = extract_pdf_info(str(pdf_path))
        
        assert isinstance(result, PDFInfoResult)
        assert result.success is True
        
        for page_dim in result.page_dimensions:
            assert "width" in page_dim
            assert "height" in page_dim
            assert "unit" in page_dim
            assert isinstance(page_dim["width"], (int, float))
            assert isinstance(page_dim["height"], (int, float))
            assert page_dim["unit"] in ["pt", "mm", "in", "cm"]
            assert page_dim["width"] > 0
            assert page_dim["height"] > 0

    def test_extract_pdf_info_handles_permission_errors(self):
        """Test PDF info extraction handles permission errors gracefully."""
        # This test would require a file with restricted permissions
        # For now, we'll test the basic error handling structure
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        result = extract_pdf_info(str(pdf_path))
        
        # Should succeed with normal permissions
        assert isinstance(result, PDFInfoResult)
        assert result.success is True