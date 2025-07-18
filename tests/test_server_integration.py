"""Integration tests for MCP LaTeX Tools server."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

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


class TestMCPServerIntegration:
    """Test MCP server integration."""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that the server can list available tools."""
        # Call the list_tools handler directly
        result = await list_tools()
        
        assert result is not None
        assert hasattr(result, 'tools')
        assert len(result.tools) == 4
        
        # Check compile_latex tool
        compile_tool = next(t for t in result.tools if t.name == "compile_latex")
        assert compile_tool.name == "compile_latex"
        assert "LaTeX" in compile_tool.description
        assert compile_tool.inputSchema is not None
        assert "tex_path" in compile_tool.inputSchema["properties"]
        
        # Check validate_latex tool
        validate_tool = next(t for t in result.tools if t.name == "validate_latex")
        assert validate_tool.name == "validate_latex"
        assert "validate" in validate_tool.description.lower()
        assert validate_tool.inputSchema is not None
        assert "file_path" in validate_tool.inputSchema["properties"]
        
        # Check pdf_info tool
        pdf_info_tool = next(t for t in result.tools if t.name == "pdf_info")
        assert pdf_info_tool.name == "pdf_info"
        assert "pdf" in pdf_info_tool.description.lower()
        assert pdf_info_tool.inputSchema is not None
        assert "file_path" in pdf_info_tool.inputSchema["properties"]
        
        # Check cleanup tool
        cleanup_tool = next(t for t in result.tools if t.name == "cleanup")
        assert cleanup_tool.name == "cleanup"
        assert "clean" in cleanup_tool.description.lower()
        assert cleanup_tool.inputSchema is not None
        assert "path" in cleanup_tool.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_compile_latex_tool_success(self):
        """Test successful LaTeX compilation through MCP tool."""
        # Create a simple LaTeX document
        latex_content = r"""
\documentclass{article}
\begin{document}
\title{Test Document}
\author{MCP Test}
\date{\today}
\maketitle

This is a test document.

\end{document}
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(latex_content)
            tex_path = f.name
        
        try:
            # Create mock request arguments
            mock_request = create_mock_request({
                "tex_path": tex_path,
                "timeout": 30
            })
            
            # Call the tool handler directly
            result = await handle_compile_latex(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            assert len(result.content) > 0
            
            # Check response content
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ LaTeX compilation successful!" in content.text
            assert "Output:" in content.text
            
        finally:
            # Cleanup
            try:
                Path(tex_path).unlink()
                # Find and remove PDF
                pdf_path = Path(tex_path).with_suffix('.pdf')
                if pdf_path.exists():
                    pdf_path.unlink()
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_compile_latex_tool_missing_file(self):
        """Test LaTeX compilation with missing file."""
        mock_request = create_mock_request({
            "tex_path": "/nonexistent/file.tex"
        })
        
        result = await handle_compile_latex(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "error" in content.text.lower()

    @pytest.mark.asyncio
    async def test_compile_latex_tool_missing_tex_path(self):
        """Test LaTeX compilation without required tex_path."""
        mock_request = create_mock_request({})
        
        result = await handle_compile_latex(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "tex_path is required" in content.text

    @pytest.mark.asyncio
    async def test_tex_path_validation(self):
        """Test tex_path validation in tool handler."""
        # Test with None arguments
        mock_request = create_mock_request(None)
        
        result = await handle_compile_latex(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "tex_path is required" in content.text

    @pytest.mark.asyncio
    async def test_validate_latex_tool_success(self):
        """Test successful LaTeX validation through MCP tool."""
        # Create a simple valid LaTeX document
        latex_content = r"""
\documentclass{article}
\begin{document}
\title{Valid Test Document}
\author{MCP Test}
\date{\today}
\maketitle

This is a valid test document.

\end{document}
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(latex_content)
            tex_path = f.name
        
        try:
            # Create mock request arguments
            mock_request = create_mock_request({
                "file_path": tex_path,
                "quick": False,
                "strict": False
            })
            
            # Call the tool handler directly
            result = await handle_validate_latex(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            assert len(result.content) > 0
            
            # Check response content
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ Valid LaTeX syntax" in content.text
            assert "No errors found" in content.text
            
        finally:
            # Cleanup
            Path(tex_path).unlink()

    @pytest.mark.asyncio
    async def test_validate_latex_tool_with_errors(self):
        """Test LaTeX validation with syntax errors."""
        # Create LaTeX with syntax errors
        latex_content = r"""
\documentclass{article}
\begin{document}
\title{Invalid Document
\author{Test Author}

\begin{equation
E = mc^2
\end{equation}

\end{document}
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(latex_content)
            tex_path = f.name
        
        try:
            mock_request = create_mock_request({
                "file_path": tex_path
            })
            
            result = await handle_validate_latex(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            assert len(result.content) > 0
            
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✗ Invalid LaTeX syntax" in content.text
            assert "Errors found" in content.text
            
        finally:
            Path(tex_path).unlink()

    @pytest.mark.asyncio 
    async def test_validate_latex_tool_missing_file(self):
        """Test LaTeX validation with missing file."""
        mock_request = create_mock_request({
            "file_path": "/nonexistent/file.tex"
        })
        
        result = await handle_validate_latex(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "error" in content.text.lower()
        assert "not found" in content.text.lower()

    @pytest.mark.asyncio
    async def test_validate_latex_tool_missing_file_path(self):
        """Test LaTeX validation without required file_path."""
        mock_request = create_mock_request({})
        
        result = await handle_validate_latex(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "file_path is required" in content.text

    @pytest.mark.asyncio
    async def test_validate_latex_tool_mutual_exclusivity(self):
        """Test that quick and strict modes are mutually exclusive."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(r"""
\documentclass{article}
\begin{document}
Test
\end{document}
""")
            tex_path = f.name
        
        try:
            mock_request = create_mock_request({
                "file_path": tex_path,
                "quick": True,
                "strict": True
            })
            
            result = await handle_validate_latex(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            assert len(result.content) > 0
            
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "Cannot use both quick and strict modes simultaneously" in content.text
            
        finally:
            Path(tex_path).unlink()

    @pytest.mark.asyncio
    async def test_pdf_info_tool_success(self):
        """Test successful PDF info extraction through MCP tool."""
        # Use the simple.pdf fixture
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        mock_request = create_mock_request({
            "file_path": str(pdf_path),
            "include_text": False
        })
        
        result = await handle_pdf_info(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "✓ PDF info extracted successfully" in content.text
        assert "Pages:" in content.text
        assert "File size:" in content.text
        assert "Dimensions:" in content.text

    @pytest.mark.asyncio
    async def test_pdf_info_tool_with_text_extraction(self):
        """Test PDF info extraction with text content."""
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"
        
        mock_request = create_mock_request({
            "file_path": str(pdf_path),
            "include_text": True
        })
        
        result = await handle_pdf_info(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "✓ PDF info extracted successfully" in content.text
        assert "Text content:" in content.text

    @pytest.mark.asyncio
    async def test_pdf_info_tool_missing_file(self):
        """Test PDF info extraction with missing file."""
        mock_request = create_mock_request({
            "file_path": "/nonexistent/file.pdf"
        })
        
        result = await handle_pdf_info(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "error" in content.text.lower()
        assert "not found" in content.text.lower()

    @pytest.mark.asyncio
    async def test_pdf_info_tool_missing_file_path(self):
        """Test PDF info extraction without required file_path."""
        mock_request = create_mock_request({})
        
        result = await handle_pdf_info(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "file_path is required" in content.text

    @pytest.mark.asyncio
    async def test_pdf_info_tool_invalid_pdf_file(self):
        """Test PDF info extraction with invalid PDF file."""
        # Use a non-PDF file
        tex_path = Path(__file__).parent / "fixtures" / "simple.tex"
        
        mock_request = create_mock_request({
            "file_path": str(tex_path)
        })
        
        result = await handle_pdf_info(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "✗ PDF info extraction failed" in content.text or "invalid" in content.text.lower()

    @pytest.mark.asyncio
    async def test_cleanup_tool_success(self):
        """Test successful cleanup through MCP tool."""
        # Create temporary directory with auxiliary files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create .tex file
            tex_file = temp_path / "test.tex"
            tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create auxiliary files
            aux_files = [
                temp_path / "test.aux",
                temp_path / "test.log",
                temp_path / "test.out",
            ]
            
            for aux_file in aux_files:
                aux_file.write_text("auxiliary content")
            
            mock_request = create_mock_request({
                "path": str(tex_file),
                "dry_run": False
            })
            
            result = await handle_cleanup(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            assert len(result.content) > 0
            
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ Cleanup completed successfully" in content.text
            assert "Files cleaned:" in content.text

    @pytest.mark.asyncio
    async def test_cleanup_tool_dry_run(self):
        """Test cleanup dry run through MCP tool."""
        # Create temporary directory with auxiliary files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create .tex file
            tex_file = temp_path / "dryrun.tex"
            tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create auxiliary files
            aux_files = [
                temp_path / "dryrun.aux",
                temp_path / "dryrun.log",
            ]
            
            for aux_file in aux_files:
                aux_file.write_text("auxiliary content")
            
            mock_request = create_mock_request({
                "path": str(tex_file),
                "dry_run": True
            })
            
            result = await handle_cleanup(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            assert len(result.content) > 0
            
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ Cleanup dry run completed" in content.text
            assert "Would clean" in content.text

    @pytest.mark.asyncio
    async def test_cleanup_tool_missing_path(self):
        """Test cleanup without required path."""
        mock_request = create_mock_request({})
        
        result = await handle_cleanup(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "path is required" in content.text

    @pytest.mark.asyncio
    async def test_cleanup_tool_nonexistent_path(self):
        """Test cleanup with non-existent path."""
        mock_request = create_mock_request({
            "path": "/nonexistent/file.tex"
        })
        
        result = await handle_cleanup(mock_request)
        
        assert result is not None
        assert hasattr(result, 'content')
        assert len(result.content) > 0
        
        content = result.content[0]
        assert hasattr(content, 'text')
        assert "error" in content.text.lower()
        assert "not found" in content.text.lower()

    @pytest.mark.asyncio
    async def test_cleanup_tool_directory_cleanup(self):
        """Test cleanup of entire directory through MCP tool."""
        # Create temporary directory with multiple files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create multiple .tex files
            tex_files = [
                temp_path / "doc1.tex",
                temp_path / "doc2.tex",
            ]
            
            for tex_file in tex_files:
                tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            
            # Create auxiliary files
            aux_files = [
                temp_path / "doc1.aux",
                temp_path / "doc1.log",
                temp_path / "doc2.aux",
                temp_path / "doc2.log",
            ]
            
            for aux_file in aux_files:
                aux_file.write_text("auxiliary content")
            
            mock_request = create_mock_request({
                "path": str(temp_path),
                "recursive": True
            })
            
            result = await handle_cleanup(mock_request)
            
            assert result is not None
            assert hasattr(result, 'content')
            assert len(result.content) > 0
            
            content = result.content[0]
            assert hasattr(content, 'text')
            assert "✓ Cleanup completed successfully" in content.text
            assert "Files cleaned:" in content.text
