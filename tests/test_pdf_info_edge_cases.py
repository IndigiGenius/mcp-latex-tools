"""Test PDF info extraction edge cases and error handling paths."""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from dataclasses import dataclass

import pytest
from pypdf.errors import PdfReadError

from mcp_latex_tools.tools.pdf_info import extract_pdf_info, _format_pdf_date, PDFInfoError


class TestPDFInfoFileAccessErrors:
    """Test PDF info extraction file access error handling."""
    
    def test_extract_pdf_info_with_file_permission_error(self):
        """Test PDF info extraction when file permissions prevent access."""
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()
            
            # Mock path.stat() to raise permission error
            with patch('pathlib.Path.stat', side_effect=PermissionError("Permission denied")):
                with pytest.raises(PDFInfoError, match="Cannot access file"):
                    extract_pdf_info(tmp_file.name)
            
            # Clean up
            Path(tmp_file.name).unlink()
    
    def test_extract_pdf_info_with_file_system_error(self):
        """Test PDF info extraction when file system error occurs."""
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()
            
            # Mock path.stat() to raise OS error
            with patch('pathlib.Path.stat', side_effect=OSError("Disk error")):
                with pytest.raises(PDFInfoError, match="Cannot access file"):
                    extract_pdf_info(tmp_file.name)
            
            # Clean up
            Path(tmp_file.name).unlink()


class TestPDFInfoEncryptedPDFs:
    """Test PDF info extraction with encrypted PDFs."""
    
    def test_extract_pdf_info_with_encrypted_pdf_no_password(self):
        """Test PDF info extraction with encrypted PDF but no password."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock encrypted PDF content")
            tmp_file.flush()
            
            # Mock PdfReader to indicate encrypted PDF
            with patch('mcp_latex_tools.tools.pdf_info.PdfReader') as mock_reader:
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = True
                mock_pdf.metadata = {}
                mock_pdf.pages = []
                mock_reader.return_value = mock_pdf
                
                result = extract_pdf_info(tmp_file.name)
                
                assert result.success
                assert result.is_encrypted
                assert result.page_count == 0
            
            # Clean up
            Path(tmp_file.name).unlink()
    
    def test_extract_pdf_info_with_encrypted_pdf_wrong_password(self):
        """Test PDF info extraction with encrypted PDF and wrong password."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock encrypted PDF content")
            tmp_file.flush()
            
            # Mock PdfReader to indicate encrypted PDF with failed decryption
            with patch('mcp_latex_tools.tools.pdf_info.PdfReader') as mock_reader:
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = True
                mock_pdf.decrypt.side_effect = Exception("Invalid password")
                mock_reader.return_value = mock_pdf
                
                result = extract_pdf_info(tmp_file.name, password="wrongpassword")
                
                assert not result.success
                assert "Failed to decrypt PDF" in result.error_message
                assert "Invalid password" in result.error_message
                assert result.extraction_time_seconds is not None
            
            # Clean up
            Path(tmp_file.name).unlink()
    
    def test_extract_pdf_info_with_encrypted_pdf_correct_password(self):
        """Test PDF info extraction with encrypted PDF and correct password."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock encrypted PDF content")
            tmp_file.flush()
            
            # Mock PdfReader to indicate encrypted PDF with successful decryption
            with patch('mcp_latex_tools.tools.pdf_info.PdfReader') as mock_reader:
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = True
                mock_pdf.decrypt.return_value = True
                mock_pdf.metadata = {'Title': 'Test Document'}
                mock_pdf.pages = [MagicMock(), MagicMock()]  # 2 pages
                mock_reader.return_value = mock_pdf
                
                result = extract_pdf_info(tmp_file.name, password="correctpassword")
                
                assert result.success
                assert result.is_encrypted
                assert result.page_count == 2
                assert result.title == "Test Document"
            
            # Clean up
            Path(tmp_file.name).unlink()


class TestPDFInfoVersionDetection:
    """Test PDF version detection edge cases."""
    
    def test_extract_pdf_info_with_pdf_version_detection_failure(self):
        """Test PDF info extraction when PDF version cannot be determined."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()
            
            # Mock PdfReader to raise exception when accessing version
            with patch('mcp_latex_tools.tools.pdf_info.PdfReader') as mock_reader:
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = False
                mock_pdf.metadata = {}
                mock_pdf.pages = []
                
                # Make both pdf_version and pdf_header raise exceptions
                type(mock_pdf).pdf_version = MagicMock(side_effect=Exception("Version error"))
                type(mock_pdf).pdf_header = MagicMock(side_effect=Exception("Header error"))
                
                mock_reader.return_value = mock_pdf
                
                result = extract_pdf_info(tmp_file.name)
                
                assert result.success
                assert result.pdf_version is None
            
            # Clean up
            Path(tmp_file.name).unlink()


class TestPDFInfoPageProcessing:
    """Test PDF page processing edge cases."""
    
    def test_extract_pdf_info_with_corrupted_page_dimensions(self):
        """Test PDF info extraction when page dimensions cannot be read."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()
            
            # Mock PdfReader with page that has corrupted dimensions
            with patch('mcp_latex_tools.tools.pdf_info.PdfReader') as mock_reader:
                mock_page = MagicMock()
                mock_page.mediabox = MagicMock(side_effect=Exception("Corrupted mediabox"))
                
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = False
                mock_pdf.metadata = {}
                mock_pdf.pages = [mock_page]
                mock_reader.return_value = mock_pdf
                
                result = extract_pdf_info(tmp_file.name, extract_dimensions=True)
                
                assert result.success
                assert result.page_count == 1
                assert len(result.page_dimensions) == 1
                # Should use default dimensions
                assert result.page_dimensions[0]['width'] == 612.0
                assert result.page_dimensions[0]['height'] == 792.0
                assert result.page_dimensions[0]['unit'] == 'pt'
            
            # Clean up
            Path(tmp_file.name).unlink()
    
    def test_extract_pdf_info_with_text_extraction_failure(self):
        """Test PDF info extraction when text extraction fails for some pages."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()
            
            # Mock PdfReader with pages where text extraction fails
            with patch('mcp_latex_tools.tools.pdf_info.PdfReader') as mock_reader:
                mock_page1 = MagicMock()
                mock_page1.extract_text.return_value = "Page 1 content"
                
                mock_page2 = MagicMock()
                mock_page2.extract_text.side_effect = Exception("Text extraction failed")
                
                mock_page3 = MagicMock()
                mock_page3.extract_text.return_value = "Page 3 content"
                
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = False
                mock_pdf.metadata = {}
                mock_pdf.pages = [mock_page1, mock_page2, mock_page3]
                mock_reader.return_value = mock_pdf
                
                result = extract_pdf_info(tmp_file.name, extract_text=True)
                
                assert result.success
                assert result.page_count == 3
                assert len(result.page_texts) == 3
                assert result.page_texts[0] == "Page 1 content"
                assert result.page_texts[1] == ""  # Empty due to extraction failure
                assert result.page_texts[2] == "Page 3 content"
            
            # Clean up
            Path(tmp_file.name).unlink()


class TestPDFInfoGeneralErrors:
    """Test PDF info extraction general error handling."""
    
    def test_extract_pdf_info_with_pdf_read_error(self):
        """Test PDF info extraction when PdfReader raises PdfReadError."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"Not a valid PDF file")
            tmp_file.flush()
            
            # Mock PdfReader to raise PdfReadError
            with patch('mcp_latex_tools.tools.pdf_info.PdfReader', side_effect=PdfReadError("Invalid PDF")):
                result = extract_pdf_info(tmp_file.name)
                
                assert not result.success
                assert "Failed to read PDF" in result.error_message
                assert "Invalid PDF" in result.error_message
                assert result.extraction_time_seconds is not None
            
            # Clean up
            Path(tmp_file.name).unlink()
    
    def test_extract_pdf_info_with_unexpected_exception(self):
        """Test PDF info extraction when unexpected exception occurs."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()
            
            # Mock PdfReader to raise unexpected exception
            with patch('mcp_latex_tools.tools.pdf_info.PdfReader', side_effect=RuntimeError("Unexpected error")):
                result = extract_pdf_info(tmp_file.name)
                
                assert not result.success
                assert "Failed to read PDF" in result.error_message
                assert "Unexpected error" in result.error_message
                assert result.extraction_time_seconds is not None
            
            # Clean up
            Path(tmp_file.name).unlink()


class TestPDFDateFormatting:
    """Test PDF date formatting edge cases."""
    
    def test_format_pdf_date_with_none_input(self):
        """Test PDF date formatting with None input."""
        result = _format_pdf_date(None)
        assert result is None
    
    def test_format_pdf_date_with_empty_string(self):
        """Test PDF date formatting with empty string."""
        result = _format_pdf_date("")
        assert result is None
    
    def test_format_pdf_date_with_whitespace_only(self):
        """Test PDF date formatting with whitespace only."""
        result = _format_pdf_date("   ")
        assert result is None
    
    def test_format_pdf_date_with_short_string(self):
        """Test PDF date formatting with string shorter than 8 characters."""
        result = _format_pdf_date("D:2023")
        assert result is None
    
    def test_format_pdf_date_with_date_only_format(self):
        """Test PDF date formatting with date-only format (8 characters)."""
        result = _format_pdf_date("D:20231201")
        assert result == "2023-12-01T00:00:00Z"
    
    def test_format_pdf_date_with_date_only_no_prefix(self):
        """Test PDF date formatting with date-only format without D: prefix."""
        result = _format_pdf_date("20231201")
        assert result == "2023-12-01T00:00:00Z"
    
    def test_format_pdf_date_with_full_datetime_format(self):
        """Test PDF date formatting with full datetime format."""
        result = _format_pdf_date("D:20231201143000+05'30'")
        assert result == "2023-12-01T14:30:00+05:30"
    
    def test_format_pdf_date_with_malformed_datetime_raises_exception(self):
        """Test PDF date formatting with malformed datetime that raises exception."""
        # Mock datetime.strptime to raise exception
        with patch('datetime.datetime.strptime', side_effect=ValueError("Invalid date")):
            result = _format_pdf_date("D:20231301")  # Invalid month
            # Should return original string when parsing fails
            assert result == "D:20231301"
    
    def test_format_pdf_date_with_timezone_parsing_error(self):
        """Test PDF date formatting when timezone parsing fails."""
        with patch('mcp_latex_tools.tools.pdf_info.datetime.strptime') as mock_strptime:
            mock_strptime.side_effect = Exception("Timezone parsing error")
            result = _format_pdf_date("D:20231201143000+05'30'")
            # Should return original string when parsing fails
            assert result == "D:20231201143000+05'30'"


class TestPDFInfoIntegration:
    """Test PDF info extraction integration scenarios."""
    
    def test_extract_pdf_info_with_all_features_and_errors(self):
        """Test PDF info extraction with all features enabled and mixed errors."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()
            
            # Mock PdfReader with mixed success/failure scenarios
            with patch('mcp_latex_tools.tools.pdf_info.PdfReader') as mock_reader:
                # Mock page 1: successful dimension extraction, failed text extraction
                mock_page1 = MagicMock()
                mock_page1.mediabox = MagicMock()
                mock_page1.mediabox.width = 612
                mock_page1.mediabox.height = 792
                mock_page1.extract_text.side_effect = Exception("Text extraction failed")
                
                # Mock page 2: failed dimension extraction, successful text extraction
                mock_page2 = MagicMock()
                mock_page2.mediabox = MagicMock(side_effect=Exception("Dimension extraction failed"))
                mock_page2.extract_text.return_value = "Page 2 content"
                
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = False
                mock_pdf.metadata = {
                    'Title': 'Test Document',
                    'Author': 'Test Author',
                    'CreationDate': 'D:20231201143000+05\'30\''
                }
                mock_pdf.pages = [mock_page1, mock_page2]
                
                # Mock version detection to fail
                type(mock_pdf).pdf_version = MagicMock(side_effect=Exception("Version error"))
                type(mock_pdf).pdf_header = MagicMock(side_effect=Exception("Header error"))
                
                mock_reader.return_value = mock_pdf
                
                result = extract_pdf_info(
                    tmp_file.name,
                    extract_dimensions=True,
                    extract_text=True
                )
                
                assert result.success
                assert result.page_count == 2
                assert result.title == "Test Document"
                assert result.author == "Test Author"
                assert result.creation_date == "2023-12-01T14:30:00+05:30"
                assert result.pdf_version is None  # Failed to detect
                
                # Check dimension extraction results
                assert len(result.page_dimensions) == 2
                assert result.page_dimensions[0]['width'] == 612.0
                assert result.page_dimensions[0]['height'] == 792.0
                # Second page should have default dimensions due to error
                assert result.page_dimensions[1]['width'] == 612.0
                assert result.page_dimensions[1]['height'] == 792.0
                
                # Check text extraction results
                assert len(result.page_texts) == 2
                assert result.page_texts[0] == ""  # Failed extraction
                assert result.page_texts[1] == "Page 2 content"
            
            # Clean up
            Path(tmp_file.name).unlink()
    
    def test_extract_pdf_info_timing_accuracy(self):
        """Test that extraction timing is accurate even with errors."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()
            
            # Mock PdfReader to raise exception after some delay
            def delayed_exception(*args, **kwargs):
                time.sleep(0.1)  # Simulate some processing time
                raise Exception("Simulated error")
            
            with patch('mcp_latex_tools.tools.pdf_info.PdfReader', side_effect=delayed_exception):
                result = extract_pdf_info(tmp_file.name)
                
                assert not result.success
                assert result.extraction_time_seconds is not None
                assert result.extraction_time_seconds >= 0.1  # Should include the delay
            
            # Clean up
            Path(tmp_file.name).unlink()