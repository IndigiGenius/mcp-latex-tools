"""
Comprehensive test suite for LaTeX utilities following TDD methodology.

These tests define the expected behavior for utility functions that will be
extracted from the LaTeX tools to eliminate code duplication and provide
consistent functionality across the MCP LaTeX Tools server.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

# Import the utilities we're going to implement (will fail initially)
from mcp_latex_tools.utils.latex_utils import (
    # File path validation and LaTeX file handling
    validate_file_path,
    is_latex_file,
    is_auxiliary_file,
    get_latex_file_extensions,
    get_auxiliary_file_extensions,
    get_protected_file_extensions,
    
    # Timing and performance utilities
    TimingContext,
    measure_execution_time,
    
    # Error message formatting
    format_validation_error,
    format_compilation_error,
    format_operation_error,
    
    # LaTeX content validation patterns
    LaTeXPatterns,
    has_document_class,
    has_begin_document,
    has_end_document,
    check_brace_balance,
    find_unmatched_environments,
    
    # Path resolution and handling
    resolve_output_path,
    ensure_directory_exists,
    get_stem_files,
    
    # Safe file operations
    read_latex_file,
    read_file_with_encoding,
    
    # Content extraction functions
    extract_packages,
    extract_citations,
    extract_labels,
    extract_references,
    has_document_structure,
    get_output_file_extensions,
    
    # LaTeX utility exceptions
    LaTeXUtilsError,
    FileValidationError,
    ContentValidationError,
)


class TestFilePathValidation:
    """Test file path validation utilities."""
    
    def test_validate_file_path_with_none_raises_error(self):
        """Test that None file path raises FileValidationError."""
        with pytest.raises(FileValidationError, match="File path cannot be None"):
            validate_file_path(None)
    
    def test_validate_file_path_with_empty_string_raises_error(self):
        """Test that empty file path raises FileValidationError."""
        with pytest.raises(FileValidationError, match="File path cannot be empty"):
            validate_file_path("")
    
    def test_validate_file_path_with_whitespace_only_raises_error(self):
        """Test that whitespace-only file path raises FileValidationError."""
        with pytest.raises(FileValidationError, match="File path cannot be empty"):
            validate_file_path("   \t\n  ")
    
    def test_validate_file_path_with_nonexistent_file_raises_error(self):
        """Test that non-existent file path raises FileValidationError."""
        with pytest.raises(FileValidationError, match="File not found: /nonexistent/file.tex"):
            validate_file_path("/nonexistent/file.tex")
    
    def test_validate_file_path_with_valid_file_returns_path(self):
        """Test that valid file path returns Path object."""
        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            tmp.write(b"\\documentclass{article}")
            tmp.flush()
            
            result = validate_file_path(tmp.name)
            assert isinstance(result, Path)
            assert result.exists()
            assert str(result) == tmp.name
    
    def test_validate_file_path_with_directory_when_file_required_raises_error(self):
        """Test that directory path raises error when file is required."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(FileValidationError, match="Path is a directory, not a file"):
                validate_file_path(tmp_dir, require_file=True)
    
    def test_validate_file_path_accepts_directory_when_allowed(self):
        """Test that directory path is accepted when files are not required."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = validate_file_path(tmp_dir, require_file=False)
            assert isinstance(result, Path)
            assert result.is_dir()


class TestLaTeXFileIdentification:
    """Test LaTeX file type identification utilities."""
    
    def test_is_latex_file_with_tex_extension_returns_true(self):
        """Test that .tex files are identified as LaTeX files."""
        assert is_latex_file("document.tex") is True
        assert is_latex_file("/path/to/document.tex") is True
    
    def test_is_latex_file_with_path_object_returns_true(self):
        """Test that Path objects with .tex extension are identified as LaTeX files."""
        assert is_latex_file(Path("document.tex")) is True
    
    def test_is_latex_file_with_non_tex_extension_returns_false(self):
        """Test that non-.tex files are not identified as LaTeX files."""
        assert is_latex_file("document.pdf") is False
        assert is_latex_file("document.txt") is False
        assert is_latex_file("document") is False
    
    def test_is_latex_file_case_insensitive(self):
        """Test that LaTeX file identification is case insensitive."""
        assert is_latex_file("document.TEX") is True
        assert is_latex_file("document.Tex") is True
    
    def test_is_auxiliary_file_with_aux_extensions_returns_true(self):
        """Test that auxiliary file extensions are correctly identified."""
        auxiliary_files = [
            "document.aux", "document.log", "document.out", "document.fls",
            "document.fdb_latexmk", "document.toc", "document.bbl"
        ]
        for file_path in auxiliary_files:
            assert is_auxiliary_file(file_path) is True
    
    def test_is_auxiliary_file_with_protected_extensions_returns_false(self):
        """Test that protected file extensions are not considered auxiliary."""
        protected_files = [
            "document.tex", "document.pdf", "document.bib", "image.png"
        ]
        for file_path in protected_files:
            assert is_auxiliary_file(file_path) is False
    
    def test_get_latex_file_extensions_returns_expected_set(self):
        """Test that LaTeX file extensions set contains expected values."""
        extensions = get_latex_file_extensions()
        assert isinstance(extensions, set)
        assert ".tex" in extensions
        assert len(extensions) >= 1
    
    def test_get_auxiliary_file_extensions_returns_comprehensive_set(self):
        """Test that auxiliary file extensions contains comprehensive list."""
        extensions = get_auxiliary_file_extensions()
        assert isinstance(extensions, set)
        expected_extensions = {".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".toc", ".bbl"}
        assert expected_extensions.issubset(extensions)
    
    def test_get_protected_file_extensions_returns_comprehensive_set(self):
        """Test that protected file extensions contains comprehensive list."""
        extensions = get_protected_file_extensions()
        assert isinstance(extensions, set)
        expected_extensions = {".tex", ".pdf", ".bib", ".png", ".jpg"}
        assert expected_extensions.issubset(extensions)


class TestTimingUtilities:
    """Test timing and performance measurement utilities."""
    
    def test_timing_context_measures_execution_time(self):
        """Test that TimingContext correctly measures execution time."""
        with TimingContext() as timer:
            time.sleep(0.01)  # Sleep for 10ms
        
        assert timer.elapsed_seconds is not None
        assert timer.elapsed_seconds >= 0.01
        assert timer.elapsed_seconds < 0.1  # Should be much less than 100ms
    
    def test_timing_context_can_be_accessed_during_execution(self):
        """Test that timing can be accessed while context is active."""
        with TimingContext() as timer:
            time.sleep(0.01)
            intermediate_time = timer.elapsed_seconds
            assert intermediate_time is not None
            assert intermediate_time >= 0.01
    
    def test_measure_execution_time_decorator_on_function(self):
        """Test that measure_execution_time decorator works on functions."""
        @measure_execution_time
        def slow_function():
            time.sleep(0.01)
            return "result"
        
        result, execution_time = slow_function()
        assert result == "result"
        assert execution_time >= 0.01
        assert execution_time < 0.1
    
    def test_measure_execution_time_decorator_with_exception(self):
        """Test that measure_execution_time handles exceptions properly."""
        @measure_execution_time
        def failing_function():
            time.sleep(0.01)
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            failing_function()


class TestErrorMessageFormatting:
    """Test error message formatting utilities."""
    
    def test_format_validation_error_with_context(self):
        """Test validation error formatting with context."""
        error_msg = format_validation_error(
            "Missing \\documentclass command",
            file_path="/path/to/document.tex",
            line_number=1
        )
        
        expected_parts = ["Missing \\documentclass command", "/path/to/document.tex", "line 1"]
        for part in expected_parts:
            assert part in error_msg
    
    def test_format_validation_error_without_optional_context(self):
        """Test validation error formatting without optional context."""
        error_msg = format_validation_error("Missing \\documentclass command")
        assert "Missing \\documentclass command" in error_msg
        assert "line" not in error_msg
    
    def test_format_compilation_error_with_details(self):
        """Test compilation error formatting with return code and stderr."""
        error_msg = format_compilation_error(
            return_code=1,
            stderr="LaTeX Error: File not found",
            context="pdflatex compilation"
        )
        
        expected_parts = ["compilation failed", "return code 1", "LaTeX Error: File not found"]
        for part in expected_parts:
            assert part in error_msg
    
    def test_format_operation_error_with_operation_context(self):
        """Test operation error formatting with operation context."""
        error_msg = format_operation_error(
            operation="PDF extraction",
            error="Permission denied",
            file_path="/path/to/document.pdf"
        )
        
        expected_parts = ["PDF extraction", "Permission denied", "/path/to/document.pdf"]
        for part in expected_parts:
            assert part in error_msg


class TestLaTeXContentValidation:
    """Test LaTeX content validation patterns and utilities."""
    
    def test_latex_patterns_class_provides_common_patterns(self):
        """Test that LaTeXPatterns class provides common regex patterns."""
        patterns = LaTeXPatterns()
        
        # Test that patterns exist and are compiled regex objects
        assert hasattr(patterns, 'document_class')
        assert hasattr(patterns, 'begin_document')
        assert hasattr(patterns, 'end_document')
        assert hasattr(patterns, 'environment_begin')
        assert hasattr(patterns, 'environment_end')
    
    def test_has_document_class_with_valid_content_returns_true(self):
        """Test documentclass detection with valid LaTeX content."""
        valid_content = "\\documentclass{article}\n\\begin{document}"
        assert has_document_class(valid_content) is True
        
        valid_with_options = "\\documentclass[12pt,a4paper]{report}"
        assert has_document_class(valid_with_options) is True
    
    def test_has_document_class_with_invalid_content_returns_false(self):
        """Test documentclass detection with invalid content."""
        invalid_content = "This is not LaTeX content"
        assert has_document_class(invalid_content) is False
        
        missing_documentclass = "\\begin{document}\nSome content\\end{document}"
        assert has_document_class(missing_documentclass) is False
    
    def test_has_begin_document_with_valid_content_returns_true(self):
        """Test begin document detection with valid content."""
        valid_content = "\\documentclass{article}\n\\begin{document}\nContent"
        assert has_begin_document(valid_content) is True
    
    def test_has_end_document_with_valid_content_returns_true(self):
        """Test end document detection with valid content."""
        valid_content = "Content\n\\end{document}"
        assert has_end_document(valid_content) is True
    
    def test_check_brace_balance_with_balanced_braces_returns_true(self):
        """Test brace balance checking with properly balanced braces."""
        balanced_content = "\\command{arg1}{arg2}"
        assert check_brace_balance(balanced_content) is True
        
        nested_balanced = "\\outer{\\inner{content}}"
        assert check_brace_balance(nested_balanced) is True
    
    def test_check_brace_balance_with_unbalanced_braces_returns_false(self):
        """Test brace balance checking with unbalanced braces."""
        unbalanced_opening = "\\command{arg1{arg2}"
        assert check_brace_balance(unbalanced_opening) is False
        
        unbalanced_closing = "\\command{arg1}arg2}"
        assert check_brace_balance(unbalanced_closing) is False
    
    def test_find_unmatched_environments_with_unmatched_returns_list(self):
        """Test finding unmatched environments returns appropriate list."""
        content_with_unmatched = """
        \\begin{document}
        \\begin{itemize}
        \\item First item
        \\begin{enumerate}
        \\item Nested item
        \\end{document}
        """
        
        unmatched = find_unmatched_environments(content_with_unmatched)
        assert isinstance(unmatched, list)
        assert "itemize" in unmatched
        assert "enumerate" in unmatched
    
    def test_find_unmatched_environments_with_matched_returns_empty(self):
        """Test finding unmatched environments with properly matched content."""
        matched_content = """
        \\begin{document}
        \\begin{itemize}
        \\item First item
        \\end{itemize}
        \\end{document}
        """
        
        unmatched = find_unmatched_environments(matched_content)
        assert unmatched == []


class TestPathHandling:
    """Test path resolution and handling utilities."""
    
    def test_resolve_output_path_with_none_returns_input_parent(self):
        """Test that None output_dir returns input file's parent directory."""
        input_path = Path("/path/to/document.tex")
        result = resolve_output_path(input_path, None)
        assert result == Path("/path/to")
    
    def test_resolve_output_path_with_directory_returns_path_object(self):
        """Test that provided output_dir returns Path object."""
        input_path = Path("/path/to/document.tex")
        output_dir = "/different/output/path"
        result = resolve_output_path(input_path, output_dir)
        assert result == Path("/different/output/path")
    
    def test_ensure_directory_exists_creates_missing_directory(self):
        """Test that ensure_directory_exists creates missing directories."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested_path = Path(tmp_dir) / "nested" / "directory"
            assert not nested_path.exists()
            
            ensure_directory_exists(nested_path)
            assert nested_path.exists()
            assert nested_path.is_dir()
    
    def test_ensure_directory_exists_with_existing_directory_succeeds(self):
        """Test that ensure_directory_exists works with existing directories."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            existing_path = Path(tmp_dir)
            ensure_directory_exists(existing_path)  # Should not raise
            assert existing_path.exists()
    
    def test_get_stem_files_returns_related_files(self):
        """Test that get_stem_files finds files with same stem."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            
            # Create test files
            (base_dir / "document.tex").touch()
            (base_dir / "document.aux").touch()
            (base_dir / "document.log").touch()
            (base_dir / "other.tex").touch()
            
            stem_files = get_stem_files(base_dir / "document.tex")
            stem_names = [f.name for f in stem_files]
            
            assert "document.tex" in stem_names
            assert "document.aux" in stem_names
            assert "document.log" in stem_names
            assert "other.tex" not in stem_names


class TestSafeFileOperations:
    """Test safe file reading and encoding handling utilities."""
    
    def test_read_latex_file_with_valid_utf8_file(self):
        """Test reading a valid UTF-8 LaTeX file."""
        content = "\\documentclass{article}\n% Comment with unicode: é\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', encoding='utf-8', delete=False) as tmp:
            tmp.write(content)
            tmp.flush()
            
            result = read_latex_file(tmp.name)
            assert result == content
    
    def test_read_latex_file_with_encoding_errors_handles_gracefully(self):
        """Test reading file with encoding errors handles gracefully."""
        # Create file with mixed encoding issues
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.tex', delete=False) as tmp:
            tmp.write(b"\\documentclass{article}\n")
            tmp.write(b"\xff\xfe")  # Invalid UTF-8 bytes
            tmp.write(b"\nSome content\n")
            tmp.flush()
            
            # Should not raise exception, should handle errors gracefully
            result = read_latex_file(tmp.name)
            assert "\\documentclass{article}" in result
            assert "Some content" in result
    
    def test_read_latex_file_with_nonexistent_file_raises_error(self):
        """Test reading nonexistent file raises appropriate error."""
        with pytest.raises(FileValidationError, match="File not found"):
            read_latex_file("/nonexistent/file.tex")
    
    def test_read_file_with_encoding_tries_multiple_encodings(self):
        """Test that read_file_with_encoding tries multiple encodings."""
        content = "LaTeX content with special chars: ñáéíóú"
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='latin-1', delete=False) as tmp:
            tmp.write(content)
            tmp.flush()
            
            # Should successfully read despite encoding difference
            result = read_file_with_encoding(tmp.name)
            assert "LaTeX content" in result
    
    def test_read_file_with_encoding_with_permission_error_raises_error(self):
        """Test that permission errors are properly handled."""
        with patch('pathlib.Path.read_text', side_effect=PermissionError("Access denied")):
            with pytest.raises(LaTeXUtilsError, match="Permission denied"):
                read_file_with_encoding("/some/file.tex")


class TestLaTeXUtilsExceptions:
    """Test LaTeX utilities exception hierarchy."""
    
    def test_latex_utils_error_is_base_exception(self):
        """Test that LaTeXUtilsError is the base exception class."""
        error = LaTeXUtilsError("Base error")
        assert isinstance(error, Exception)
        assert str(error) == "Base error"
    
    def test_file_validation_error_inherits_from_base(self):
        """Test that FileValidationError inherits from LaTeXUtilsError."""
        error = FileValidationError("File validation failed")
        assert isinstance(error, LaTeXUtilsError)
        assert isinstance(error, Exception)
    
    def test_content_validation_error_inherits_from_base(self):
        """Test that ContentValidationError inherits from LaTeXUtilsError."""
        error = ContentValidationError("Content validation failed")
        assert isinstance(error, LaTeXUtilsError)
        assert isinstance(error, Exception)


class TestFileValidationDetailed:
    """Test validate_file_path_detailed function comprehensively."""
    
    def test_validate_file_path_detailed_with_none_returns_error(self):
        """Test detailed validation with None path returns proper error."""
        from mcp_latex_tools.utils.latex_utils import validate_file_path_detailed
        
        result = validate_file_path_detailed(None)
        assert not result.is_valid
        assert result.error_message == "File path cannot be None"
        assert result.file_path is None
        assert not result.file_exists
        assert not result.is_readable
        assert result.file_size_bytes is None
    
    def test_validate_file_path_detailed_with_empty_string_returns_error(self):
        """Test detailed validation with empty string returns proper error."""
        from mcp_latex_tools.utils.latex_utils import validate_file_path_detailed
        
        result = validate_file_path_detailed("")
        assert not result.is_valid
        assert result.error_message == "File path cannot be empty"
        assert result.file_path == ""
        assert not result.file_exists
        assert not result.is_readable
        assert result.file_size_bytes is None
    
    def test_validate_file_path_detailed_with_whitespace_returns_error(self):
        """Test detailed validation with whitespace-only string returns proper error."""
        from mcp_latex_tools.utils.latex_utils import validate_file_path_detailed
        
        result = validate_file_path_detailed("   ")
        assert not result.is_valid
        assert result.error_message == "File path cannot be empty"
        assert result.file_path == "   "
        assert not result.file_exists
        assert not result.is_readable
        assert result.file_size_bytes is None
    
    def test_validate_file_path_detailed_with_nonexistent_file_returns_error(self):
        """Test detailed validation with nonexistent file returns proper error."""
        from mcp_latex_tools.utils.latex_utils import validate_file_path_detailed
        
        result = validate_file_path_detailed("/nonexistent/file.tex")
        assert not result.is_valid
        assert "File not found" in result.error_message
        assert result.file_path == "/nonexistent/file.tex"
        assert not result.file_exists
        assert not result.is_readable
        assert result.file_size_bytes is None
    
    def test_validate_file_path_detailed_with_valid_file_returns_success(self):
        """Test detailed validation with valid file returns success."""
        from mcp_latex_tools.utils.latex_utils import validate_file_path_detailed
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
            tmp.write("\\documentclass{article}")
            tmp.flush()
            
            result = validate_file_path_detailed(tmp.name)
            assert result.is_valid
            assert result.error_message is None
            assert result.file_path == tmp.name
            assert result.file_exists
            assert result.is_readable
            assert result.file_size_bytes > 0
    
    def test_validate_file_path_detailed_with_unreadable_file_returns_error(self):
        """Test detailed validation with unreadable file returns proper error."""
        from mcp_latex_tools.utils.latex_utils import validate_file_path_detailed
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
            tmp.write("content")
            tmp.flush()
            
            # Mock os.access to return False for read permission
            with patch('os.access', return_value=False):
                result = validate_file_path_detailed(tmp.name)
                assert not result.is_valid
                assert "File is not readable" in result.error_message
                assert result.file_path == tmp.name
                assert result.file_exists
                assert not result.is_readable
    
    def test_validate_file_path_detailed_with_wrong_extension_returns_error(self):
        """Test detailed validation with wrong extension returns proper error."""
        from mcp_latex_tools.utils.latex_utils import validate_file_path_detailed
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write("content")
            tmp.flush()
            
            result = validate_file_path_detailed(tmp.name, allowed_extensions={'.tex'})
            assert not result.is_valid
            assert "File extension '.txt' not allowed" in result.error_message
            assert result.file_path == tmp.name
            assert result.file_exists
            assert result.is_readable
            assert result.file_size_bytes > 0


class TestFileValidationPermissions:
    """Test file validation permission checks."""
    
    def test_validate_file_path_with_unreadable_file_raises_error(self):
        """Test validation with unreadable file raises proper error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
            tmp.write("content")
            tmp.flush()
            
            # Mock file permissions check to return False
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_mode = 0o000  # No permissions
                with pytest.raises(FileValidationError, match="File is not readable"):
                    validate_file_path(tmp.name, must_be_readable=True)
    
    def test_validate_file_path_with_unreadable_directory_raises_error(self):
        """Test validation with unreadable directory raises proper error."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Mock directory iteration to raise PermissionError
            with patch('pathlib.Path.iterdir', side_effect=PermissionError("Access denied")):
                with pytest.raises(FileValidationError, match="Directory is not readable"):
                    validate_file_path(tmp_dir, require_file=False, must_be_readable=True)
    
    def test_validate_file_path_with_access_exception_raises_error(self):
        """Test validation with access exception raises proper error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
            tmp.write("content")
            tmp.flush()
            
            # Mock os.access to raise an exception
            with patch('os.access', side_effect=OSError("Access error")):
                with pytest.raises(FileValidationError, match="Cannot access path"):
                    validate_file_path(tmp.name, must_be_readable=True)
    
    def test_validate_file_path_with_invalid_extension_raises_error(self):
        """Test validation with invalid extension raises proper error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write("content")
            tmp.flush()
            
            with pytest.raises(FileValidationError, match="File extension '.txt' not allowed"):
                validate_file_path(tmp.name, allowed_extensions={'.tex'})


class TestTimingContextEdgeCases:
    """Test TimingContext edge cases and error scenarios."""
    
    def test_timing_context_elapsed_seconds_before_start_returns_none(self):
        """Test elapsed_seconds property returns None before context is entered."""
        timer = TimingContext()
        assert timer.elapsed_seconds is None
    
    def test_timing_context_legacy_function_works(self):
        """Test legacy timing_context function works properly."""
        from mcp_latex_tools.utils.latex_utils import timing_context
        
        with timing_context() as timer:
            time.sleep(0.001)  # Small delay to ensure measurable time
        
        assert timer.elapsed_seconds is not None
        assert timer.elapsed_seconds > 0


class TestMeasureExecutionTimeDataclasses:
    """Test measure_execution_time decorator with different dataclass field names."""
    
    def test_measure_execution_time_with_compilation_time_field(self):
        """Test decorator with compilation_time_seconds field."""
        from dataclasses import dataclass
        
        @dataclass
        class CompilationResult:
            success: bool
            compilation_time_seconds: float = 0.0
        
        @measure_execution_time
        def compile_something():
            time.sleep(0.001)
            return CompilationResult(success=True)
        
        result = compile_something()
        assert result.success
        assert result.compilation_time_seconds > 0
    
    def test_measure_execution_time_with_validation_time_field(self):
        """Test decorator with validation_time_seconds field."""
        from dataclasses import dataclass
        
        @dataclass
        class ValidationResult:
            is_valid: bool
            validation_time_seconds: float = 0.0
        
        @measure_execution_time
        def validate_something():
            time.sleep(0.001)
            return ValidationResult(is_valid=True)
        
        result = validate_something()
        assert result.is_valid
        assert result.validation_time_seconds > 0
    
    def test_measure_execution_time_with_extraction_time_field(self):
        """Test decorator with extraction_time_seconds field."""
        from dataclasses import dataclass
        
        @dataclass
        class ExtractionResult:
            data: str
            extraction_time_seconds: float = 0.0
        
        @measure_execution_time
        def extract_something():
            time.sleep(0.001)
            return ExtractionResult(data="test")
        
        result = extract_something()
        assert result.data == "test"
        assert result.extraction_time_seconds > 0
    
    def test_measure_execution_time_with_cleanup_time_field(self):
        """Test decorator with cleanup_time_seconds field."""
        from dataclasses import dataclass
        
        @dataclass
        class CleanupResult:
            cleaned_files: list
            cleanup_time_seconds: float = 0.0
        
        @measure_execution_time
        def cleanup_something():
            time.sleep(0.001)
            return CleanupResult(cleaned_files=["file1.aux"])
        
        result = cleanup_something()
        assert result.cleaned_files == ["file1.aux"]
        assert result.cleanup_time_seconds > 0


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple utilities."""
    
    def test_complete_file_validation_workflow(self):
        """Test complete file validation workflow using multiple utilities."""
        latex_content = """\\documentclass{article}
\\begin{document}
Hello, world!
\\end{document}"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
            tmp.write(latex_content)
            tmp.flush()
            
            # Test complete workflow
            file_path = validate_file_path(tmp.name)
            assert is_latex_file(file_path)
            
            content = read_latex_file(str(file_path))
            assert has_document_class(content)
            assert has_begin_document(content)
            assert has_end_document(content)
            assert check_brace_balance(content)
    
    def test_error_handling_integration(self):
        """Test error handling integration across utilities."""
        # Test with invalid file path
        with pytest.raises(FileValidationError):
            validate_file_path(None)
        
        # Test with invalid content
        invalid_content = "Not LaTeX content"
        assert not has_document_class(invalid_content)
        assert not check_brace_balance("unbalanced{braces")
    
    def test_timing_integration_with_file_operations(self):
        """Test timing integration with file operations."""
        latex_content = "\\documentclass{article}\\begin{document}Content\\end{document}"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
            tmp.write(latex_content)
            tmp.flush()
            
            with TimingContext() as timer:
                file_path = validate_file_path(tmp.name)
                content = read_latex_file(str(file_path))
                is_valid = has_document_class(content) and has_begin_document(content)
            
            assert is_valid
            assert timer.elapsed_seconds is not None
            assert timer.elapsed_seconds > 0


class TestFileTypeChecking:
    """Test file type checking functions with string paths."""
    
    def test_is_output_file_with_string_path(self):
        """Test is_output_file with string path conversion."""
        from mcp_latex_tools.utils.latex_utils import is_output_file
        
        # Test with string path
        assert is_output_file("document.pdf")
        assert is_output_file("document.dvi")
        assert is_output_file("document.ps")
        assert not is_output_file("document.tex")
        assert not is_output_file("document.aux")
    
    def test_is_protected_file_with_string_path(self):
        """Test is_protected_file with string path conversion."""
        from mcp_latex_tools.utils.latex_utils import is_protected_file
        
        # Test with string path
        assert is_protected_file("document.tex")
        assert is_protected_file("document.pdf")
        assert is_protected_file("document.bib")
        assert is_protected_file("image.png")
        assert not is_protected_file("document.aux")
        assert not is_protected_file("document.log")


class TestErrorFormatting:
    """Test error formatting functions with various scenarios."""
    
    def test_format_validation_error_with_file_path_only(self):
        """Test validation error formatting with file path but no line number."""
        result = format_validation_error("Syntax error", file_path="test.tex")
        assert result == "Syntax error in test.tex"
    
    def test_format_operation_error_without_file_path(self):
        """Test operation error formatting without file path."""
        result = format_operation_error("Compilation", "Memory error")
        assert result == "Compilation failed: Memory error"


class TestEnvironmentMatching:
    """Test environment matching with complex scenarios."""
    
    def test_find_unmatched_environments_with_end_without_begin(self):
        """Test finding end environments without matching begin."""
        content = """
        Some content
        \\end{document}
        More content
        \\begin{equation}
        x = 1
        \\end{equation}
        \\end{figure}
        """
        
        unmatched = find_unmatched_environments(content)
        # Should find 'document' and 'figure' as unmatched (end without begin)
        assert 'document' in unmatched
        assert 'figure' in unmatched
        assert 'equation' not in unmatched  # This one is properly matched


class TestFileReadingEdgeCases:
    """Test file reading edge cases and error scenarios."""
    
    def test_read_latex_file_with_non_latex_extension_raises_error(self):
        """Test reading file with non-LaTeX extension raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write("\\documentclass{article}")
            tmp.flush()
            
            with pytest.raises(FileValidationError, match="Not a LaTeX file"):
                read_latex_file(tmp.name)
    
    def test_read_latex_file_with_latex_utils_error_handling(self):
        """Test LaTeX file reading with LaTeXUtilsError handling."""
        # Mock read_file_with_encoding to raise LaTeXUtilsError
        with patch('mcp_latex_tools.utils.latex_utils.read_file_with_encoding', 
                  side_effect=LaTeXUtilsError("Encoding error")):
            with pytest.raises(FileValidationError, match="Failed to read LaTeX file"):
                read_latex_file("test.tex")
    
    def test_read_file_with_encoding_with_file_not_found_raises_error(self):
        """Test read_file_with_encoding with FileNotFoundError."""
        with pytest.raises(LaTeXUtilsError, match="File not found"):
            read_file_with_encoding("/nonexistent/file.tex")
    
    def test_read_file_with_encoding_with_all_encodings_failing(self):
        """Test read_file_with_encoding when all encodings fail."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp:
            # Write binary data that cannot be decoded with common encodings
            tmp.write(b'\xff\xfe\x00\x00invalid')
            tmp.flush()
            
            with pytest.raises(LaTeXUtilsError, match="Could not read .* with any of the provided encodings"):
                read_file_with_encoding(tmp.name, encodings=['utf-8', 'latin-1'])


class TestContentExtraction:
    """Test content extraction functions."""
    
    def test_extract_packages_with_multiple_packages_per_command(self):
        """Test package extraction with multiple packages in one command."""
        content = """
        \\usepackage{amsmath,amssymb,amsfonts}
        \\usepackage[utf8]{inputenc}
        \\usepackage{geometry}
        """
        
        packages = extract_packages(content)
        assert 'amsmath' in packages
        assert 'amssymb' in packages
        assert 'amsfonts' in packages
        assert 'inputenc' in packages
        assert 'geometry' in packages
    
    def test_extract_citations_with_multiple_citations_per_command(self):
        """Test citation extraction with multiple citations in one command."""
        content = """
        See \\cite{ref1,ref2,ref3} for details.
        Also \\cite{ref4} and \\citep{ref5,ref6}.
        """
        
        citations = extract_citations(content)
        assert 'ref1' in citations
        assert 'ref2' in citations
        assert 'ref3' in citations
        assert 'ref4' in citations
        assert 'ref5' in citations
        assert 'ref6' in citations
    
    def test_extract_labels_basic_functionality(self):
        """Test basic label extraction functionality."""
        content = """
        \\section{Introduction}
        \\label{sec:intro}
        \\begin{equation}
        x = 1
        \\label{eq:simple}
        \\end{equation}
        \\begin{figure}
        \\label{fig:example}
        \\end{figure}
        """
        
        labels = extract_labels(content)
        assert 'sec:intro' in labels
        assert 'eq:simple' in labels
        assert 'fig:example' in labels
    
    def test_extract_references_basic_functionality(self):
        """Test basic reference extraction functionality."""
        content = """
        As shown in Section~\\ref{sec:intro}, we have
        Equation~\\eqref{eq:simple} and Figure~\\pageref{fig:example}.
        """
        
        references = extract_references(content)
        assert 'sec:intro' in references
        assert 'eq:simple' in references
        assert 'fig:example' in references


class TestDocumentStructure:
    """Test document structure validation."""
    
    def test_has_document_structure_with_complete_document(self):
        """Test document structure validation with complete document."""
        content = """
        \\documentclass{article}
        \\begin{document}
        Content here
        \\end{document}
        """
        
        has_structure, issues = has_document_structure(content)
        assert has_structure
        assert len(issues) == 0
    
    def test_has_document_structure_with_missing_documentclass(self):
        """Test document structure validation with missing documentclass."""
        content = """
        \\begin{document}
        Content here
        \\end{document}
        """
        
        has_structure, issues = has_document_structure(content)
        assert not has_structure
        assert 'Missing \\documentclass' in issues
    
    def test_has_document_structure_with_missing_begin_document(self):
        """Test document structure validation with missing begin document."""
        content = """
        \\documentclass{article}
        Content here
        \\end{document}
        """
        
        has_structure, issues = has_document_structure(content)
        assert not has_structure
        assert 'Missing \\begin{document}' in issues
    
    def test_has_document_structure_with_missing_end_document(self):
        """Test document structure validation with missing end document."""
        content = """
        \\documentclass{article}
        \\begin{document}
        Content here
        """
        
        has_structure, issues = has_document_structure(content)
        assert not has_structure
        assert 'Missing \\end{document}' in issues
    
    def test_has_document_structure_with_multiple_issues(self):
        """Test document structure validation with multiple issues."""
        content = """
        Just some content without proper structure
        """
        
        has_structure, issues = has_document_structure(content)
        assert not has_structure
        assert 'Missing \\documentclass' in issues
        assert 'Missing \\begin{document}' in issues
        assert 'Missing \\end{document}' in issues
        assert len(issues) == 3


class TestFileExtensionGetters:
    """Test file extension getter functions."""
    
    def test_get_output_file_extensions_returns_correct_extensions(self):
        """Test get_output_file_extensions returns correct extensions."""
        extensions = get_output_file_extensions()
        assert '.pdf' in extensions
        assert '.dvi' in extensions
        assert '.ps' in extensions
        assert isinstance(extensions, set)
        assert len(extensions) > 0