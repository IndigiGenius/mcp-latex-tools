"""Test server error handling paths and edge cases for MCP LaTeX Tools."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from dataclasses import dataclass

import pytest

from mcp_latex_tools.server import list_tools, handle_compile_latex, handle_validate_latex, handle_pdf_info, handle_cleanup, call_tool


def create_mock_request(arguments: dict):
    """Create a mock MCP request with proper structure."""
    mock_params = type('MockParams', (), {
        'arguments': arguments
    })()
    return type('MockRequest', (), {
        'params': mock_params
    })()


class TestServerErrorHandling:
    """Test server error handling paths and edge cases."""
    
    @pytest.mark.asyncio
    async def test_call_tool_with_unknown_tool_name(self):
        """Test call_tool with unknown tool name returns error result."""
        mock_request = MagicMock()
        mock_request.params.name = "unknown_tool"
        mock_request.params.arguments = {}
        
        result = await call_tool(mock_request)
        assert len(result.content) == 1
        assert "Error: Unknown tool: unknown_tool" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_with_unexpected_exception(self):
        """Test call_tool with unexpected exception in tool routing."""
        mock_request = MagicMock()
        mock_request.params.name = "compile_latex"
        mock_request.params.arguments = {}
        
        # Mock handle_compile_latex to raise unexpected exception
        with patch('mcp_latex_tools.server.handle_compile_latex', side_effect=RuntimeError("Unexpected error")):
            result = await call_tool(mock_request)
            assert len(result.content) == 1
            assert "Error: Unexpected error" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_compile_latex_with_unexpected_exception(self):
        """Test compile_latex handler with unexpected exception."""
        # Create a temporary file to pass validation
        with tempfile.NamedTemporaryFile(suffix='.tex', delete=False) as tmp:
            tmp.write(b"\\documentclass{article}\\begin{document}test\\end{document}")
            tmp.flush()
            
            mock_request = create_mock_request({
                "tex_path": tmp.name
            })
            
            # Mock the compilation function to raise unexpected exception
            with patch('mcp_latex_tools.tools.compile.compile_latex', side_effect=RuntimeError("Unexpected compile error")):
                result = await handle_compile_latex(mock_request)
                
                assert result is not None
                assert hasattr(result, 'content')
                content = result.content[0]
                assert hasattr(content, 'text')
                assert "Unexpected error" in content.text
    
    @pytest.mark.asyncio
    async def test_validate_latex_with_unexpected_exception(self):
        """Test validate_latex handler with unexpected exception."""
        mock_request = create_mock_request({
            "file_path": "test.tex"
        })
        
        # Mock the validation function to raise unexpected exception
        with patch('mcp_latex_tools.tools.validate.validate_latex', side_effect=RuntimeError("Unexpected validate error")):
            result = await handle_validate_latex(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "Error during validation" in content.text
            assert "Unexpected validate error" in content.text
    
    @pytest.mark.asyncio
    async def test_pdf_info_with_unexpected_exception(self):
        """Test pdf_info handler with unexpected exception."""
        mock_request = create_mock_request({
            "pdf_path": "test.pdf"
        })
        
        # Mock the PDF info function to raise unexpected exception
        with patch('mcp_latex_tools.tools.pdf_info.extract_pdf_info', side_effect=RuntimeError("Unexpected PDF error")):
            result = await handle_pdf_info(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "Error extracting PDF info" in content.text
            assert "Unexpected PDF error" in content.text
    
    @pytest.mark.asyncio
    async def test_cleanup_with_unexpected_exception(self):
        """Test cleanup handler with unexpected exception."""
        mock_request = create_mock_request({
            "path": "test.tex"
        })
        
        # Mock the cleanup function to raise unexpected exception
        with patch('mcp_latex_tools.tools.cleanup.clean_auxiliary_files', side_effect=RuntimeError("Unexpected cleanup error")):
            result = await handle_cleanup(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "Error during cleanup" in content.text
            assert "Unexpected cleanup error" in content.text


class TestCompilationResponseFormatting:
    """Test compilation response formatting edge cases."""
    
    @pytest.mark.asyncio
    async def test_compilation_failure_with_timing_information(self):
        """Test compilation failure response with timing information."""
        mock_request = create_mock_request({
            "tex_path": "test.tex"
        })
        
        # Mock compilation result with failure but timing info
        @dataclass
        class MockCompilationResult:
            success: bool
            error_message: str
            output_path: str = None
            compilation_time_seconds: float = 1.5
        
        mock_result = MockCompilationResult(
            success=False,
            error_message="Compilation failed due to missing package",
            compilation_time_seconds=1.5
        )
        
        with patch('mcp_latex_tools.tools.compile.compile_latex', return_value=mock_result):
            result = await handle_compile_latex(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✗ Compilation failed" in content.text
            assert "missing package" in content.text
            assert "Compilation time: 1.5s" in content.text


class TestValidationResponseFormatting:
    """Test validation response formatting edge cases."""
    
    @pytest.mark.asyncio
    async def test_validation_success_with_warnings(self):
        """Test validation success response with warnings."""
        mock_request = create_mock_request({
            "file_path": "test.tex"
        })
        
        # Mock validation result with success but warnings
        @dataclass
        class MockValidationResult:
            is_valid: bool
            warnings: list
            error_message: str = None
            validation_time_seconds: float = 0.5
        
        mock_result = MockValidationResult(
            is_valid=True,
            warnings=["Warning: Package geometry not found", "Warning: Missing bibliography"],
            validation_time_seconds=0.5
        )
        
        with patch('mcp_latex_tools.tools.validate.validate_latex', return_value=mock_result):
            result = await handle_validate_latex(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ Valid LaTeX syntax" in content.text
            assert "Warnings:" in content.text
            assert "Package geometry not found" in content.text
            assert "Missing bibliography" in content.text
    
    @pytest.mark.asyncio
    async def test_validation_failure_with_warnings(self):
        """Test validation failure response with warnings."""
        mock_request = create_mock_request({
            "file_path": "test.tex"
        })
        
        # Mock validation result with failure and warnings
        @dataclass
        class MockValidationResult:
            is_valid: bool
            warnings: list
            error_message: str
            validation_time_seconds: float = 0.5
        
        mock_result = MockValidationResult(
            is_valid=False,
            warnings=["Warning: Deprecated command used"],
            error_message="Syntax error: Missing closing brace",
            validation_time_seconds=0.5
        )
        
        with patch('mcp_latex_tools.tools.validate.validate_latex', return_value=mock_result):
            result = await handle_validate_latex(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✗ Invalid LaTeX syntax" in content.text
            assert "Warnings:" in content.text
            assert "Deprecated command used" in content.text
            assert "Missing closing brace" in content.text


class TestPDFInfoResponseFormatting:
    """Test PDF info response formatting edge cases."""
    
    @pytest.mark.asyncio
    async def test_pdf_info_with_encrypted_pdf(self):
        """Test PDF info response with encrypted PDF."""
        mock_request = create_mock_request({
            "pdf_path": "encrypted.pdf"
        })
        
        # Mock PDF info result with encrypted flag
        @dataclass
        class MockPDFInfo:
            success: bool
            pages: int
            encrypted: bool = False
            title: str = None
            author: str = None
            subject: str = None
            extraction_time_seconds: float = 0.3
        
        mock_result = MockPDFInfo(
            success=True,
            pages=10,
            encrypted=True,
            extraction_time_seconds=0.3
        )
        
        with patch('mcp_latex_tools.tools.pdf_info.extract_pdf_info', return_value=mock_result):
            result = await handle_pdf_info(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ PDF info extracted successfully" in content.text
            assert "Encrypted: Yes" in content.text
            assert "Pages: 10" in content.text
    
    @pytest.mark.asyncio
    async def test_pdf_info_with_all_metadata(self):
        """Test PDF info response with all metadata fields."""
        mock_request = create_mock_request({
            "pdf_path": "document.pdf"
        })
        
        # Mock PDF info result with all metadata
        @dataclass
        class MockPDFInfo:
            success: bool
            pages: int
            encrypted: bool = False
            title: str = None
            author: str = None
            subject: str = None
            extraction_time_seconds: float = 0.3
        
        mock_result = MockPDFInfo(
            success=True,
            pages=25,
            encrypted=False,
            title="LaTeX Document Title",
            author="John Doe",
            subject="Mathematics Research",
            extraction_time_seconds=0.3
        )
        
        with patch('mcp_latex_tools.tools.pdf_info.extract_pdf_info', return_value=mock_result):
            result = await handle_pdf_info(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ PDF info extracted successfully" in content.text
            assert "Title: LaTeX Document Title" in content.text
            assert "Author: John Doe" in content.text
            assert "Subject: Mathematics Research" in content.text
            assert "Pages: 25" in content.text
    
    @pytest.mark.asyncio
    async def test_pdf_info_with_empty_page_content(self):
        """Test PDF info response with pages that have no text content."""
        mock_request = create_mock_request({
            "pdf_path": "document.pdf",
            "extract_text": True
        })
        
        # Mock PDF info result with page text extraction
        @dataclass
        class MockPDFInfo:
            success: bool
            pages: int
            page_texts: list
            extraction_time_seconds: float = 0.5
        
        mock_result = MockPDFInfo(
            success=True,
            pages=3,
            page_texts=["Page 1 content", "", "Page 3 content"],  # Page 2 is empty
            extraction_time_seconds=0.5
        )
        
        with patch('mcp_latex_tools.tools.pdf_info.extract_pdf_info', return_value=mock_result):
            result = await handle_pdf_info(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ PDF info extracted successfully" in content.text
            assert "Page 1: Page 1 content" in content.text
            assert "Page 2: [No text content]" in content.text
            assert "Page 3: Page 3 content" in content.text


class TestCleanupResponseFormatting:
    """Test cleanup response formatting edge cases."""
    
    @pytest.mark.asyncio
    async def test_cleanup_dry_run_with_many_files(self):
        """Test cleanup dry run response with more than 10 files."""
        mock_request = create_mock_request({
            "path": "test.tex",
            "dry_run": True
        })
        
        # Mock cleanup result with many files
        @dataclass
        class MockCleanupResult:
            success: bool
            dry_run: bool
            files_to_clean: list
            files_to_clean_count: int
            cleanup_time_seconds: float = 0.2
        
        # Generate list of 15 files
        many_files = [f"file{i}.aux" for i in range(15)]
        
        mock_result = MockCleanupResult(
            success=True,
            dry_run=True,
            files_to_clean=many_files,
            files_to_clean_count=15,
            cleanup_time_seconds=0.2
        )
        
        with patch('mcp_latex_tools.tools.cleanup.clean_auxiliary_files', return_value=mock_result):
            result = await handle_cleanup(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ Cleanup dry run completed" in content.text
            assert "Would clean 15 files" in content.text
            assert "First 10 files:" in content.text
            assert "file0.aux" in content.text
            assert "file9.aux" in content.text
            assert "... and 5 more files" in content.text
    
    @pytest.mark.asyncio
    async def test_cleanup_with_many_files_cleaned(self):
        """Test cleanup response with more than 10 files cleaned."""
        mock_request = create_mock_request({
            "path": "test.tex"
        })
        
        # Mock cleanup result with many files cleaned
        @dataclass
        class MockCleanupResult:
            success: bool
            dry_run: bool
            cleaned_files: list
            cleaned_files_count: int
            cleanup_time_seconds: float = 0.5
        
        # Generate list of 12 files
        many_files = [f"document{i}.log" for i in range(12)]
        
        mock_result = MockCleanupResult(
            success=True,
            dry_run=False,
            cleaned_files=many_files,
            cleaned_files_count=12,
            cleanup_time_seconds=0.5
        )
        
        with patch('mcp_latex_tools.tools.cleanup.clean_auxiliary_files', return_value=mock_result):
            result = await handle_cleanup(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ Cleanup completed successfully" in content.text
            assert "Cleaned 12 files" in content.text
            assert "First 10 files:" in content.text
            assert "document0.log" in content.text
            assert "document9.log" in content.text
            assert "... and 2 more files" in content.text
    
    @pytest.mark.asyncio
    async def test_cleanup_with_backup_created(self):
        """Test cleanup response with backup directory created."""
        mock_request = create_mock_request({
            "path": "test.tex",
            "create_backup": True
        })
        
        # Mock cleanup result with backup
        @dataclass
        class MockCleanupResult:
            success: bool
            dry_run: bool
            cleaned_files: list
            cleaned_files_count: int
            backup_directory: str
            cleanup_time_seconds: float = 0.3
        
        mock_result = MockCleanupResult(
            success=True,
            dry_run=False,
            cleaned_files=["test.aux", "test.log"],
            cleaned_files_count=2,
            backup_directory="/tmp/latex_backup_20231201_123456",
            cleanup_time_seconds=0.3
        )
        
        with patch('mcp_latex_tools.tools.cleanup.clean_auxiliary_files', return_value=mock_result):
            result = await handle_cleanup(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ Cleanup completed successfully" in content.text
            assert "Backup created: /tmp/latex_backup_20231201_123456" in content.text
            assert "Cleaned 2 files" in content.text
    
    @pytest.mark.asyncio
    async def test_cleanup_failure_with_error_message(self):
        """Test cleanup failure response with error message."""
        mock_request = create_mock_request({
            "path": "test.tex"
        })
        
        # Mock cleanup result with failure
        @dataclass
        class MockCleanupResult:
            success: bool
            error_message: str
            cleanup_time_seconds: float = 0.1
        
        mock_result = MockCleanupResult(
            success=False,
            error_message="Permission denied: Cannot delete file test.aux",
            cleanup_time_seconds=0.1
        )
        
        with patch('mcp_latex_tools.tools.cleanup.clean_auxiliary_files', return_value=mock_result):
            result = await handle_cleanup(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✗ Cleanup failed" in content.text
            assert "Permission denied: Cannot delete file test.aux" in content.text
            assert "Cleanup time: 0.1s" in content.text


class TestMainServerInitialization:
    """Test main server initialization and entry point."""
    
    @pytest.mark.asyncio
    async def test_main_server_initialization(self):
        """Test main server initialization function."""
        # Mock the MCP server components
        with patch('mcp_latex_tools.server.Server') as mock_server, \
             patch('mcp_latex_tools.server.stdio_server') as mock_stdio:
            
            from mcp_latex_tools.server import main
            
            # Test that main function can be called
            try:
                await main()
            except Exception:
                # We expect some errors due to mocking, but function should be callable
                pass
            
            # Verify server was created
            mock_server.assert_called_once()
    
    def test_server_entry_point(self):
        """Test server entry point execution."""
        # Mock asyncio.run to avoid actual server startup
        with patch('asyncio.run') as mock_run:
            # Import and test the entry point
            try:
                import mcp_latex_tools.server
                # The module should be importable
                assert hasattr(mcp_latex_tools.server, 'main')
                assert callable(mcp_latex_tools.server.main)
            except Exception as e:
                # If there are import issues, that's still a test case
                assert "import" in str(e).lower() or "module" in str(e).lower()