"""Test server error handling paths and edge cases for MCP LaTeX Tools."""

import tempfile
from pathlib import Path
from unittest.mock import patch
from dataclasses import dataclass
from typing import Optional

import pytest

from mcp_latex_tools.server import call_tool


class TestServerErrorHandling:
    """Test server error handling paths and edge cases."""

    @pytest.mark.asyncio
    async def test_call_tool_with_unknown_tool_name(self):
        """Test call_tool with unknown tool name returns error."""
        result = await call_tool("unknown_tool", {})
        assert len(result) == 1
        assert "Unknown tool: unknown_tool" in result[0].text

    @pytest.mark.asyncio
    async def test_compile_latex_with_unexpected_exception(self):
        """Test compile_latex handler with unexpected exception."""
        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            tmp.write(b"\\documentclass{article}\\begin{document}test\\end{document}")
            tmp.flush()

            with patch(
                "mcp_latex_tools.server.compile_latex",
                side_effect=RuntimeError("Unexpected compile error"),
            ):
                result = await call_tool("compile_latex", {"tex_path": tmp.name})
                assert len(result) == 1
                assert "Unexpected compile error" in result[0].text

            Path(tmp.name).unlink()

    @pytest.mark.asyncio
    async def test_validate_latex_with_unexpected_exception(self):
        """Test validate_latex handler with unexpected exception."""
        with patch(
            "mcp_latex_tools.server.validate_latex",
            side_effect=RuntimeError("Unexpected validate error"),
        ):
            result = await call_tool("validate_latex", {"file_path": "test.tex"})
            assert len(result) == 1
            assert "Unexpected validate error" in result[0].text

    @pytest.mark.asyncio
    async def test_pdf_info_with_unexpected_exception(self):
        """Test pdf_info handler with unexpected exception."""
        with patch(
            "mcp_latex_tools.server.extract_pdf_info",
            side_effect=RuntimeError("Unexpected PDF error"),
        ):
            result = await call_tool("pdf_info", {"file_path": "test.pdf"})
            assert len(result) == 1
            assert "Unexpected PDF error" in result[0].text

    @pytest.mark.asyncio
    async def test_cleanup_with_unexpected_exception(self):
        """Test cleanup handler with unexpected exception."""
        with patch(
            "mcp_latex_tools.server.clean_latex",
            side_effect=RuntimeError("Unexpected cleanup error"),
        ):
            result = await call_tool("cleanup", {"path": "test.tex"})
            assert len(result) == 1
            assert "Unexpected cleanup error" in result[0].text


class TestCompilationResponseFormatting:
    """Test compilation response formatting edge cases."""

    @pytest.mark.asyncio
    async def test_compilation_failure_with_timing(self):
        """Test compilation failure response with timing info."""

        @dataclass
        class MockResult:
            success: bool = False
            error_message: Optional[str] = "Compilation failed due to missing package"
            output_path: Optional[str] = None
            log_content: Optional[str] = None
            compilation_time_seconds: Optional[float] = 1.5

        with patch("mcp_latex_tools.server.compile_latex", return_value=MockResult()):
            result = await call_tool("compile_latex", {"tex_path": "test.tex"})
            text = result[0].text
            assert "failed" in text.lower()
            assert "missing package" in text
            assert "1.5" in text


class TestValidationResponseFormatting:
    """Test validation response formatting edge cases."""

    @pytest.mark.asyncio
    async def test_validation_success_with_warnings(self):
        """Test validation success response with warnings."""

        @dataclass
        class MockResult:
            is_valid: bool = True
            error_message: Optional[str] = None
            errors: list = None  # type: ignore[assignment]
            warnings: list = None  # type: ignore[assignment]
            validation_time_seconds: Optional[float] = 0.5

            def __post_init__(self):
                if self.errors is None:
                    self.errors = []
                if self.warnings is None:
                    self.warnings = [
                        "Warning: Package geometry not found",
                        "Warning: Missing bibliography",
                    ]

        with patch("mcp_latex_tools.server.validate_latex", return_value=MockResult()):
            result = await call_tool("validate_latex", {"file_path": "test.tex"})
            text = result[0].text
            assert "Valid LaTeX syntax" in text
            assert "Warnings" in text
            assert "Package geometry not found" in text

    @pytest.mark.asyncio
    async def test_validation_failure_with_errors(self):
        """Test validation failure response."""

        @dataclass
        class MockResult:
            is_valid: bool = False
            error_message: Optional[str] = "Syntax error"
            errors: list = None  # type: ignore[assignment]
            warnings: list = None  # type: ignore[assignment]
            validation_time_seconds: Optional[float] = 0.5

            def __post_init__(self):
                if self.errors is None:
                    self.errors = ["Missing closing brace"]
                if self.warnings is None:
                    self.warnings = ["Deprecated command used"]

        with patch("mcp_latex_tools.server.validate_latex", return_value=MockResult()):
            result = await call_tool("validate_latex", {"file_path": "test.tex"})
            text = result[0].text
            assert "Invalid LaTeX syntax" in text
            assert "Missing closing brace" in text
            assert "Deprecated command used" in text


class TestPDFInfoResponseFormatting:
    """Test PDF info response formatting edge cases."""

    @pytest.mark.asyncio
    async def test_pdf_info_with_metadata(self):
        """Test PDF info response with metadata fields."""

        @dataclass
        class MockResult:
            success: bool = True
            error_message: Optional[str] = None
            file_path: str = "document.pdf"
            file_size_bytes: int = 10000
            page_count: int = 25
            page_dimensions: list = None  # type: ignore[assignment]
            pdf_version: Optional[str] = "1.7"
            is_encrypted: bool = False
            is_linearized: Optional[bool] = False
            creation_date: Optional[str] = None
            modification_date: Optional[str] = None
            title: str = "LaTeX Document Title"
            author: str = "John Doe"
            subject: str = "Mathematics Research"
            keywords: Optional[str] = None
            producer: Optional[str] = None
            creator: Optional[str] = None
            text_content: Optional[list] = None
            extraction_time_seconds: Optional[float] = 0.3

            def __post_init__(self):
                if self.page_dimensions is None:
                    self.page_dimensions = [
                        {"width": 612.0, "height": 792.0, "unit": "pt"}
                    ]

        with patch(
            "mcp_latex_tools.server.extract_pdf_info", return_value=MockResult()
        ):
            result = await call_tool("pdf_info", {"file_path": "document.pdf"})
            text = result[0].text
            assert "PDF info extracted" in text
            assert "Title: LaTeX Document Title" in text
            assert "Author: John Doe" in text
            assert "Pages: 25" in text

    @pytest.mark.asyncio
    async def test_pdf_info_encrypted(self):
        """Test PDF info response with encrypted PDF."""

        @dataclass
        class MockResult:
            success: bool = True
            error_message: Optional[str] = None
            file_path: str = "encrypted.pdf"
            file_size_bytes: int = 5000
            page_count: int = 10
            page_dimensions: list = None  # type: ignore[assignment]
            pdf_version: Optional[str] = None
            is_encrypted: bool = True
            is_linearized: Optional[bool] = None
            creation_date: Optional[str] = None
            modification_date: Optional[str] = None
            title: Optional[str] = None
            author: Optional[str] = None
            subject: Optional[str] = None
            keywords: Optional[str] = None
            producer: Optional[str] = None
            creator: Optional[str] = None
            text_content: Optional[list] = None
            extraction_time_seconds: Optional[float] = 0.3

            def __post_init__(self):
                if self.page_dimensions is None:
                    self.page_dimensions = []

        with patch(
            "mcp_latex_tools.server.extract_pdf_info", return_value=MockResult()
        ):
            result = await call_tool("pdf_info", {"file_path": "encrypted.pdf"})
            text = result[0].text
            assert "Encrypted: Yes" in text
            assert "Pages: 10" in text


class TestCleanupResponseFormatting:
    """Test cleanup response formatting edge cases."""

    @pytest.mark.asyncio
    async def test_cleanup_failure_with_error(self):
        """Test cleanup failure response."""

        @dataclass
        class MockResult:
            success: bool = False
            error_message: str = "Permission denied"
            tex_file_path: Optional[str] = None
            directory_path: Optional[str] = None
            cleaned_files_count: int = 0
            cleaned_files: list = None  # type: ignore[assignment]
            would_clean_files: list = None  # type: ignore[assignment]
            dry_run: bool = False
            recursive: bool = False
            backup_created: bool = False
            backup_directory: Optional[str] = None
            cleanup_time_seconds: Optional[float] = 0.1

            def __post_init__(self):
                if self.cleaned_files is None:
                    self.cleaned_files = []
                if self.would_clean_files is None:
                    self.would_clean_files = []

        with patch("mcp_latex_tools.server.clean_latex", return_value=MockResult()):
            result = await call_tool("cleanup", {"path": "test.tex"})
            text = result[0].text
            assert "failed" in text.lower()
            assert "Permission denied" in text
