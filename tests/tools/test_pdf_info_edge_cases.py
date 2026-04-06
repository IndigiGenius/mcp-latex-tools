"""Test PDF info extraction edge cases and error handling paths."""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from pypdf.errors import PdfReadError

from mcp_latex_tools.tools.pdf_info import (
    extract_pdf_info,
    _format_pdf_date,
    PDFInfoError,
)


class TestPDFInfoFileAccessErrors:
    """Test PDF info extraction file access error handling."""

    def test_extract_pdf_info_with_file_permission_error(self):
        """Test PDF info extraction when file permissions prevent access."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()

            with patch(
                "pathlib.Path.stat", side_effect=PermissionError("Permission denied")
            ):
                with pytest.raises(PDFInfoError, match="Cannot access file"):
                    extract_pdf_info(tmp_file.name)

            Path(tmp_file.name).unlink()

    def test_extract_pdf_info_with_file_system_error(self):
        """Test PDF info extraction when file system error occurs."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()

            with patch("pathlib.Path.stat", side_effect=OSError("Disk error")):
                with pytest.raises(PDFInfoError, match="Cannot access file"):
                    extract_pdf_info(tmp_file.name)

            Path(tmp_file.name).unlink()


class TestPDFInfoEncryptedPDFs:
    """Test PDF info extraction with encrypted PDFs."""

    def test_extract_pdf_info_with_encrypted_pdf_no_password(self):
        """Test PDF info extraction with encrypted PDF but no password."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock encrypted PDF content")
            tmp_file.flush()

            with patch("mcp_latex_tools.tools.pdf_info.PdfReader") as mock_reader:
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = True
                mock_pdf.metadata = {}
                mock_pdf.pages = []
                mock_reader.return_value = mock_pdf

                result = extract_pdf_info(tmp_file.name)

                assert result.success
                assert result.is_encrypted
                assert result.page_count == 0

            Path(tmp_file.name).unlink()

    def test_extract_pdf_info_with_encrypted_pdf_wrong_password(self):
        """Test PDF info extraction with encrypted PDF and wrong password."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock encrypted PDF content")
            tmp_file.flush()

            with patch("mcp_latex_tools.tools.pdf_info.PdfReader") as mock_reader:
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = True
                mock_pdf.decrypt.side_effect = Exception("Invalid password")
                mock_reader.return_value = mock_pdf

                result = extract_pdf_info(tmp_file.name, password="wrongpassword")

                assert not result.success
                assert "Failed to decrypt PDF" in result.error_message
                assert result.extraction_time_seconds is not None

            Path(tmp_file.name).unlink()

    def test_extract_pdf_info_with_encrypted_pdf_correct_password(self):
        """Test PDF info extraction with encrypted PDF and correct password."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock encrypted PDF content")
            tmp_file.flush()

            with patch("mcp_latex_tools.tools.pdf_info.PdfReader") as mock_reader:
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = True
                mock_pdf.decrypt.return_value = True
                mock_pdf.metadata = {"/Title": "Test Document"}
                mock_pdf.pages = [MagicMock(), MagicMock()]
                mock_reader.return_value = mock_pdf

                result = extract_pdf_info(tmp_file.name, password="correctpassword")

                assert result.success
                assert result.is_encrypted
                assert result.page_count == 2
                assert result.title == "Test Document"

            Path(tmp_file.name).unlink()


class TestPDFInfoVersionDetection:
    """Test PDF version detection edge cases."""

    def test_extract_pdf_info_with_pdf_version_detection_failure(self):
        """Test PDF info extraction when PDF version cannot be determined."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()

            with patch("mcp_latex_tools.tools.pdf_info.PdfReader") as mock_reader:
                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = False
                mock_pdf.metadata = {}
                mock_pdf.pages = []
                mock_pdf.pdf_version = None
                mock_pdf.pdf_header = None
                mock_reader.return_value = mock_pdf

                result = extract_pdf_info(tmp_file.name)

                assert result.success
                assert result.pdf_version is None

            Path(tmp_file.name).unlink()


class TestPDFInfoPageProcessing:
    """Test PDF page processing edge cases."""

    def test_extract_pdf_info_with_corrupted_page_dimensions(self):
        """Test PDF info extraction when page dimensions cannot be read."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()

            with patch("mcp_latex_tools.tools.pdf_info.PdfReader") as mock_reader:
                mock_page = MagicMock()
                type(mock_page).mediabox = property(
                    lambda self: (_ for _ in ()).throw(Exception("Corrupted mediabox"))
                )

                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = False
                mock_pdf.metadata = {}
                mock_pdf.pages = [mock_page]
                mock_reader.return_value = mock_pdf

                result = extract_pdf_info(tmp_file.name)

                assert result.success
                assert result.page_count == 1
                assert len(result.page_dimensions) == 1
                assert result.page_dimensions[0]["width"] == 612.0
                assert result.page_dimensions[0]["height"] == 792.0

            Path(tmp_file.name).unlink()

    def test_extract_pdf_info_with_text_extraction_failure(self):
        """Test PDF info extraction when text extraction fails for some pages."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()

            with patch("mcp_latex_tools.tools.pdf_info.PdfReader") as mock_reader:
                mock_page1 = MagicMock()
                mock_page1.extract_text.return_value = "Page 1 content"

                mock_page2 = MagicMock()
                mock_page2.extract_text.side_effect = Exception(
                    "Text extraction failed"
                )

                mock_page3 = MagicMock()
                mock_page3.extract_text.return_value = "Page 3 content"

                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = False
                mock_pdf.metadata = {}
                mock_pdf.pages = [mock_page1, mock_page2, mock_page3]
                mock_reader.return_value = mock_pdf

                result = extract_pdf_info(tmp_file.name, include_text=True)

                assert result.success
                assert result.page_count == 3
                assert result.text_content is not None
                assert len(result.text_content) == 3
                assert result.text_content[0] == "Page 1 content"
                assert result.text_content[1] == ""
                assert result.text_content[2] == "Page 3 content"

            Path(tmp_file.name).unlink()


class TestPDFInfoGeneralErrors:
    """Test PDF info extraction general error handling."""

    def test_extract_pdf_info_with_pdf_read_error(self):
        """Test PDF info extraction when PdfReader raises PdfReadError."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"Not a valid PDF file")
            tmp_file.flush()

            with patch(
                "mcp_latex_tools.tools.pdf_info.PdfReader",
                side_effect=PdfReadError("Invalid PDF"),
            ):
                result = extract_pdf_info(tmp_file.name)

                assert not result.success
                assert "Not a valid PDF file" in result.error_message
                assert result.extraction_time_seconds is not None

            Path(tmp_file.name).unlink()

    def test_extract_pdf_info_with_unexpected_exception(self):
        """Test PDF info extraction when unexpected exception occurs."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()

            with patch(
                "mcp_latex_tools.tools.pdf_info.PdfReader",
                side_effect=RuntimeError("Unexpected error"),
            ):
                result = extract_pdf_info(tmp_file.name)

                assert not result.success
                assert "Failed to read PDF" in result.error_message
                assert "Unexpected error" in result.error_message
                assert result.extraction_time_seconds is not None

            Path(tmp_file.name).unlink()


class TestPDFDateFormatting:
    """Test PDF date formatting edge cases."""

    def test_format_pdf_date_with_none_input(self):
        result = _format_pdf_date(None)
        assert result is None

    def test_format_pdf_date_with_empty_string(self):
        result = _format_pdf_date("")
        assert result is None

    def test_format_pdf_date_with_whitespace_only(self):
        result = _format_pdf_date("   ")
        assert result is None

    def test_format_pdf_date_with_short_string(self):
        result = _format_pdf_date("D:2023")
        assert result is None

    def test_format_pdf_date_with_date_only_format(self):
        result = _format_pdf_date("D:20231201")
        assert result == "2023-12-01T00:00:00Z"

    def test_format_pdf_date_with_date_only_no_prefix(self):
        result = _format_pdf_date("20231201")
        assert result == "2023-12-01T00:00:00Z"

    def test_format_pdf_date_with_full_datetime_format(self):
        result = _format_pdf_date("D:20231201143000+05'30'")
        assert result == "2023-12-01T14:30:00+05:30"

    def test_format_pdf_date_with_invalid_month(self):
        """Test that invalid dates still produce output (no validation)."""
        result = _format_pdf_date("D:20231301")
        # The function doesn't validate dates, just formats them
        assert result == "2023-13-01T00:00:00Z"

    def test_format_pdf_date_with_utc_timezone(self):
        result = _format_pdf_date("D:20231201143000Z")
        assert result == "2023-12-01T14:30:00Z"


class TestPDFInfoIntegration:
    """Test PDF info extraction integration scenarios."""

    def test_extract_pdf_info_with_mixed_page_results(self):
        """Test PDF info extraction with mixed success/failure per page."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()

            with patch("mcp_latex_tools.tools.pdf_info.PdfReader") as mock_reader:
                mock_page1 = MagicMock()
                mock_page1.mediabox = MagicMock()
                mock_page1.mediabox.width = 612
                mock_page1.mediabox.height = 792
                mock_page1.extract_text.side_effect = Exception(
                    "Text extraction failed"
                )

                mock_page2 = MagicMock()
                mock_page2.mediabox = MagicMock()
                mock_page2.mediabox.width = 612
                mock_page2.mediabox.height = 792
                mock_page2.extract_text.return_value = "Page 2 content"

                mock_pdf = MagicMock()
                mock_pdf.is_encrypted = False
                mock_pdf.metadata = {
                    "/Title": "Test Document",
                    "/Author": "Test Author",
                    "/CreationDate": "D:20231201143000+05'30'",
                }
                mock_pdf.pages = [mock_page1, mock_page2]
                mock_pdf.pdf_version = None
                mock_pdf.pdf_header = None
                mock_reader.return_value = mock_pdf

                result = extract_pdf_info(tmp_file.name, include_text=True)

                assert result.success
                assert result.page_count == 2
                assert result.title == "Test Document"
                assert result.author == "Test Author"
                assert result.creation_date == "2023-12-01T14:30:00+05:30"

                assert len(result.page_dimensions) == 2
                assert result.text_content is not None
                assert len(result.text_content) == 2
                assert result.text_content[0] == ""
                assert result.text_content[1] == "Page 2 content"

            Path(tmp_file.name).unlink()

    def test_extract_pdf_info_timing_accuracy(self):
        """Test that extraction timing is accurate even with errors."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\n%Mock PDF content")
            tmp_file.flush()

            def delayed_exception(*args, **kwargs):
                time.sleep(0.1)
                raise Exception("Simulated error")

            with patch(
                "mcp_latex_tools.tools.pdf_info.PdfReader",
                side_effect=delayed_exception,
            ):
                result = extract_pdf_info(tmp_file.name)

                assert not result.success
                assert result.extraction_time_seconds is not None
                assert result.extraction_time_seconds >= 0.1

            Path(tmp_file.name).unlink()
