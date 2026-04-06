"""Integration tests for MCP LaTeX Tools server."""

import tempfile
from pathlib import Path

import pytest

from mcp_latex_tools.server import list_tools, call_tool


class TestMCPServerIntegration:
    """Test MCP server integration."""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that the server can list available tools."""
        result = await list_tools()

        assert result is not None
        assert len(result) == 5

        names = {t.name for t in result}
        assert names == {
            "compile_latex",
            "validate_latex",
            "pdf_info",
            "cleanup",
            "detect_packages",
        }

        # Check tool schemas have required properties
        tool_map = {t.name: t for t in result}
        assert "tex_path" in tool_map["compile_latex"].inputSchema["properties"]
        assert "file_path" in tool_map["validate_latex"].inputSchema["properties"]
        assert "file_path" in tool_map["pdf_info"].inputSchema["properties"]
        assert "path" in tool_map["cleanup"].inputSchema["properties"]
        assert "file_path" in tool_map["detect_packages"].inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_compile_latex_tool_success(self):
        """Test successful LaTeX compilation through MCP tool."""
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            f.write(latex_content)
            tex_path = f.name

        try:
            result = await call_tool(
                "compile_latex", {"tex_path": tex_path, "timeout": 30}
            )

            assert result is not None
            assert len(result) > 0
            assert "Compilation successful" in result[0].text
            assert "Output:" in result[0].text
        finally:
            try:
                Path(tex_path).unlink()
                pdf_path = Path(tex_path).with_suffix(".pdf")
                if pdf_path.exists():
                    pdf_path.unlink()
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_compile_latex_tool_missing_file(self):
        """Test LaTeX compilation with missing file."""
        result = await call_tool("compile_latex", {"tex_path": "/nonexistent/file.tex"})

        assert len(result) > 0
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_compile_latex_tool_missing_tex_path(self):
        """Test LaTeX compilation without required tex_path."""
        result = await call_tool("compile_latex", {})

        assert len(result) > 0
        assert "tex_path is required" in result[0].text

    @pytest.mark.asyncio
    async def test_validate_latex_tool_success(self):
        """Test successful LaTeX validation through MCP tool."""
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            f.write(latex_content)
            tex_path = f.name

        try:
            result = await call_tool(
                "validate_latex",
                {"file_path": tex_path, "quick": False, "strict": False},
            )

            assert len(result) > 0
            assert "Valid LaTeX syntax" in result[0].text
            assert "No errors found" in result[0].text
        finally:
            Path(tex_path).unlink()

    @pytest.mark.asyncio
    async def test_validate_latex_tool_with_errors(self):
        """Test LaTeX validation with syntax errors."""
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            f.write(latex_content)
            tex_path = f.name

        try:
            result = await call_tool("validate_latex", {"file_path": tex_path})

            assert len(result) > 0
            assert "Invalid LaTeX syntax" in result[0].text
            assert "Errors found" in result[0].text
        finally:
            Path(tex_path).unlink()

    @pytest.mark.asyncio
    async def test_validate_latex_tool_missing_file(self):
        """Test LaTeX validation with missing file."""
        result = await call_tool(
            "validate_latex", {"file_path": "/nonexistent/file.tex"}
        )

        assert len(result) > 0
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_validate_latex_tool_missing_file_path(self):
        """Test LaTeX validation without required file_path."""
        result = await call_tool("validate_latex", {})

        assert len(result) > 0
        assert "file_path is required" in result[0].text

    @pytest.mark.asyncio
    async def test_validate_latex_tool_mutual_exclusivity(self):
        """Test that quick and strict modes are mutually exclusive."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            f.write(r"\documentclass{article}\begin{document}Test\end{document}")
            tex_path = f.name

        try:
            result = await call_tool(
                "validate_latex", {"file_path": tex_path, "quick": True, "strict": True}
            )

            assert len(result) > 0
            assert "Cannot use both quick and strict" in result[0].text
        finally:
            Path(tex_path).unlink()

    @pytest.mark.asyncio
    async def test_pdf_info_tool_success(self):
        """Test successful PDF info extraction through MCP tool."""
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"

        result = await call_tool(
            "pdf_info", {"file_path": str(pdf_path), "include_text": False}
        )

        assert len(result) > 0
        assert "PDF info extracted" in result[0].text
        assert "Pages:" in result[0].text
        assert "File size:" in result[0].text

    @pytest.mark.asyncio
    async def test_pdf_info_tool_with_text_extraction(self):
        """Test PDF info extraction with text content."""
        pdf_path = Path(__file__).parent / "fixtures" / "simple.pdf"

        result = await call_tool(
            "pdf_info", {"file_path": str(pdf_path), "include_text": True}
        )

        assert len(result) > 0
        assert "PDF info extracted" in result[0].text
        assert "Text content:" in result[0].text

    @pytest.mark.asyncio
    async def test_pdf_info_tool_missing_file(self):
        """Test PDF info extraction with missing file."""
        result = await call_tool("pdf_info", {"file_path": "/nonexistent/file.pdf"})

        assert len(result) > 0
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_pdf_info_tool_missing_file_path(self):
        """Test PDF info extraction without required file_path."""
        result = await call_tool("pdf_info", {})

        assert len(result) > 0
        assert "file_path is required" in result[0].text

    @pytest.mark.asyncio
    async def test_cleanup_tool_success(self):
        """Test successful cleanup through MCP tool."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_file = temp_path / "test.tex"
            tex_file.write_text(
                r"\documentclass{article}\begin{document}Test\end{document}"
            )

            for ext in [".aux", ".log", ".out"]:
                (temp_path / f"test{ext}").write_text("auxiliary content")

            result = await call_tool(
                "cleanup", {"path": str(tex_file), "dry_run": False}
            )

            assert len(result) > 0
            assert "Cleanup completed" in result[0].text
            assert "files cleaned" in result[0].text

    @pytest.mark.asyncio
    async def test_cleanup_tool_dry_run(self):
        """Test cleanup dry run through MCP tool."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_file = temp_path / "dryrun.tex"
            tex_file.write_text(
                r"\documentclass{article}\begin{document}Test\end{document}"
            )

            for ext in [".aux", ".log"]:
                (temp_path / f"dryrun{ext}").write_text("auxiliary content")

            result = await call_tool(
                "cleanup", {"path": str(tex_file), "dry_run": True}
            )

            assert len(result) > 0
            assert "dry run" in result[0].text.lower()
            assert "would clean" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_cleanup_tool_missing_path(self):
        """Test cleanup without required path."""
        result = await call_tool("cleanup", {})

        assert len(result) > 0
        assert "path is required" in result[0].text

    @pytest.mark.asyncio
    async def test_cleanup_tool_nonexistent_path(self):
        """Test cleanup with non-existent path."""
        result = await call_tool("cleanup", {"path": "/nonexistent/file.tex"})

        assert len(result) > 0
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_cleanup_tool_directory_cleanup(self):
        """Test cleanup of entire directory through MCP tool."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            for name in ["doc1", "doc2"]:
                (temp_path / f"{name}.tex").write_text(
                    r"\documentclass{article}\begin{document}Test\end{document}"
                )
                for ext in [".aux", ".log"]:
                    (temp_path / f"{name}{ext}").write_text("auxiliary content")

            result = await call_tool(
                "cleanup", {"path": str(temp_path), "recursive": True}
            )

            assert len(result) > 0
            assert "Cleanup completed" in result[0].text
