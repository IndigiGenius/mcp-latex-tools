"""Tests for LaTeX compilation tool."""

import pytest
from pathlib import Path
from unittest.mock import patch
import tempfile

from mcp_latex_tools.tools.compile import (
    compile_latex,
    CompilationResult,
    CompilationError,
)


class TestCompileLatex:
    """Test cases for compile_latex function."""

    def test_compile_latex_with_valid_file_returns_success(self):
        """Test that compiling a valid LaTeX file returns success."""
        # Arrange
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"

        # Act
        result = compile_latex(str(fixture_path))

        # Assert
        assert isinstance(result, CompilationResult)
        assert result.success is True
        assert result.output_path is not None
        assert result.output_path.endswith(".pdf")
        assert result.error_message is None
        assert result.log_content is not None
        assert "Output written on" in result.log_content

    def test_compile_latex_with_invalid_file_returns_error(self):
        """Test that compiling an invalid LaTeX file returns error."""
        # Arrange
        fixture_path = Path(__file__).parent / "fixtures" / "invalid.tex"

        # Act
        result = compile_latex(str(fixture_path))

        # Assert
        assert isinstance(result, CompilationResult)
        assert result.success is False
        assert result.output_path is None
        assert result.error_message is not None
        assert "failed" in result.error_message.lower()
        assert result.log_content is not None

    def test_compile_latex_with_nonexistent_file_raises_error(self):
        """Test that compiling a nonexistent file raises CompilationError."""
        # Arrange
        nonexistent_path = "/path/to/nonexistent/file.tex"

        # Act & Assert
        with pytest.raises(CompilationError) as exc_info:
            compile_latex(nonexistent_path)

        assert "not found" in str(exc_info.value).lower()

    def test_compile_latex_with_empty_string_raises_error(self):
        """Test that compiling with empty string raises CompilationError."""
        # Act & Assert
        with pytest.raises(CompilationError) as exc_info:
            compile_latex("")

        assert "path" in str(exc_info.value).lower()

    def test_compile_latex_with_none_raises_error(self):
        """Test that compiling with None raises CompilationError."""
        # Act & Assert
        with pytest.raises(CompilationError) as exc_info:
            compile_latex(None)

        assert "path" in str(exc_info.value).lower()

    def test_compile_latex_creates_output_in_same_directory(self):
        """Test that PDF output is created in the same directory as source."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy simple.tex to temp directory
            source_path = Path(__file__).parent / "fixtures" / "simple.tex"
            temp_tex_path = Path(temp_dir) / "test.tex"
            temp_tex_path.write_text(source_path.read_text())

            # Act
            result = compile_latex(str(temp_tex_path))

            # Assert
            assert result.success is True
            expected_pdf_path = Path(temp_dir) / "test.pdf"
            assert Path(result.output_path) == expected_pdf_path
            assert expected_pdf_path.exists()

    def test_compile_latex_with_custom_output_directory(self):
        """Test compilation with custom output directory."""
        # Arrange
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()

            # Act
            result = compile_latex(str(fixture_path), output_dir=str(output_dir))

            # Assert
            assert result.success is True
            assert result.output_path.startswith(str(output_dir))

    def test_compile_latex_with_timeout_parameter(self):
        """Test compilation with timeout parameter."""
        # Arrange
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"

        # Act
        result = compile_latex(str(fixture_path), timeout=30)

        # Assert
        assert result.success is True
        assert result.compilation_time_seconds is not None
        assert result.compilation_time_seconds > 0

    def test_compile_latex_handles_permission_errors(self):
        """Test that compilation handles permission errors gracefully."""
        # Arrange
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"

        # Mock subprocess to raise PermissionError
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = PermissionError("Permission denied")

            # Act
            result = compile_latex(str(fixture_path))

            # Assert
            assert result.success is False
            assert "permission" in result.error_message.lower()

    def test_compile_latex_handles_process_timeout(self):
        """Test that compilation handles process timeout gracefully."""
        # Arrange
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"

        # Mock subprocess to raise TimeoutExpired
        with patch("subprocess.run") as mock_run:
            from subprocess import TimeoutExpired

            mock_run.side_effect = TimeoutExpired("pdflatex", 30)

            # Act
            result = compile_latex(str(fixture_path), timeout=30)

            # Assert
            assert result.success is False
            assert "timed out" in result.error_message.lower()


class TestCompilationResult:
    """Test cases for CompilationResult dataclass."""

    def test_compilation_result_success_creation(self):
        """Test creating a successful CompilationResult."""
        # Act
        result = CompilationResult(
            success=True,
            output_path="/path/to/output.pdf",
            log_content="LaTeX compilation log",
            compilation_time_seconds=1.5,
        )

        # Assert
        assert result.success is True
        assert result.output_path == "/path/to/output.pdf"
        assert result.error_message is None
        assert result.log_content == "LaTeX compilation log"
        assert result.compilation_time_seconds == 1.5

    def test_compilation_result_error_creation(self):
        """Test creating an error CompilationResult."""
        # Act
        result = CompilationResult(
            success=False,
            error_message="Compilation failed",
            log_content="Error log content",
        )

        # Assert
        assert result.success is False
        assert result.output_path is None
        assert result.error_message == "Compilation failed"
        assert result.log_content == "Error log content"
        assert result.compilation_time_seconds is None


class TestCompilationError:
    """Test cases for CompilationError exception."""

    def test_compilation_error_creation(self):
        """Test creating CompilationError with message."""
        # Act
        error = CompilationError("Test error message")

        # Assert
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_compilation_error_with_cause(self):
        """Test creating CompilationError with cause."""
        # Arrange
        original_error = FileNotFoundError("Original error")

        # Act
        try:
            raise CompilationError("Compilation failed") from original_error
        except CompilationError as error:
            # Assert
            assert str(error) == "Compilation failed"
            assert error.__cause__ == original_error
