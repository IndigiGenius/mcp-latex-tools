"""Tests for LaTeX compilation tool."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
import tempfile

from mcp_latex_tools.tools.compile import (
    compile_latex,
    CompilationResult,
    CompilationError,
    SUPPORTED_ENGINES,
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


class TestCompileEngine:
    """Test cases for engine parameter."""

    def test_default_engine_is_pdflatex(self):
        """Test that default engine is pdflatex."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex))
            assert result.success is True
            assert result.engine == "pdflatex"

    def test_engine_pdflatex_explicit(self):
        """Test explicit pdflatex engine."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex), engine="pdflatex")
            assert result.success is True
            assert result.engine == "pdflatex"
            assert result.output_path is not None
            assert result.output_path.endswith(".pdf")

    def test_engine_xelatex(self):
        """Test xelatex engine compiles successfully."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex), engine="xelatex")
            assert result.success is True
            assert result.engine == "xelatex"
            assert result.output_path is not None
            assert Path(result.output_path).exists()

    def test_engine_lualatex(self):
        """Test lualatex engine compiles successfully."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex), engine="lualatex")
            assert result.success is True
            assert result.engine == "lualatex"
            assert result.output_path is not None
            assert Path(result.output_path).exists()

    def test_engine_latexmk(self):
        """Test latexmk engine compiles successfully."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex), engine="latexmk")
            assert result.success is True
            assert result.engine == "latexmk"
            assert result.output_path is not None
            assert Path(result.output_path).exists()

    def test_invalid_engine_raises_error(self):
        """Test that an invalid engine raises CompilationError."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with pytest.raises(CompilationError) as exc_info:
            compile_latex(str(fixture_path), engine="notanengine")
        assert "engine" in str(exc_info.value).lower()

    def test_supported_engines_constant(self):
        """Test that SUPPORTED_ENGINES lists all valid engines."""
        assert "pdflatex" in SUPPORTED_ENGINES
        assert "xelatex" in SUPPORTED_ENGINES
        assert "lualatex" in SUPPORTED_ENGINES
        assert "latexmk" in SUPPORTED_ENGINES

    def test_engine_builds_correct_command(self):
        """Test that each engine uses the right binary via subprocess."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"

        for engine in ["pdflatex", "xelatex", "lualatex"]:
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1, stderr="")
                try:
                    compile_latex(str(fixture_path), engine=engine)
                except Exception:
                    pass
                cmd = mock_run.call_args_list[0][0][0]
                assert cmd[0] == engine


class TestCompilePasses:
    """Test cases for passes parameter."""

    def test_default_passes_is_one(self):
        """Test that default passes is 1."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex))
            assert result.success is True
            assert result.passes_run == 1

    def test_explicit_single_pass(self):
        """Test passes=1 does a single compilation."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex), passes=1)
            assert result.success is True
            assert result.passes_run == 1

    def test_two_passes(self):
        """Test passes=2 runs the engine twice."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex), passes=2)
            assert result.success is True
            assert result.passes_run == 2

    def test_three_passes(self):
        """Test passes=3 runs the engine three times."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex), passes=3)
            assert result.success is True
            assert result.passes_run == 3

    def test_auto_passes_no_rerun_needed(self):
        """Test passes='auto' with a simple doc does a single pass."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex), passes="auto")
            assert result.success is True
            assert result.passes_run == 1

    def test_auto_passes_detects_rerun(self):
        """Test passes='auto' reruns when log suggests it."""
        tex_content = r"""\documentclass{article}
\begin{document}
See Section~\ref{sec:intro} on page~\pageref{sec:intro}.
\section{Introduction}\label{sec:intro}
Hello world.
\end{document}
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "crossref.tex"
            temp_tex.write_text(tex_content)
            result = compile_latex(str(temp_tex), passes="auto")
            assert result.success is True
            assert result.passes_run >= 2

    def test_auto_passes_max_three(self):
        """Test passes='auto' never exceeds 3 passes."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex), passes="auto")
            assert result.passes_run is not None
            assert result.passes_run <= 3

    def test_invalid_passes_raises_error(self):
        """Test that invalid passes value raises CompilationError."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with pytest.raises(CompilationError) as exc_info:
            compile_latex(str(fixture_path), passes=0)
        assert "passes" in str(exc_info.value).lower()

    def test_latexmk_ignores_passes(self):
        """Test that latexmk handles passes automatically regardless of param."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())
            result = compile_latex(str(temp_tex), engine="latexmk", passes=3)
            assert result.success is True
            assert result.engine == "latexmk"
            assert result.passes_run is not None


class TestCompileBibliography:
    """Test cases for bibliography detection and bibtex/biber support."""

    def test_bibtex_run_with_bibliography(self):
        """Test that bibtex is run when \\bibliography{} is detected."""
        tex_content = r"""\documentclass{article}
\begin{document}
Citation: \cite{knuth1984}.
\bibliographystyle{plain}
\bibliography{refs}
\end{document}
"""
        bib_content = r"""@book{knuth1984,
  author = {Donald E. Knuth},
  title = {The TeXbook},
  publisher = {Addison-Wesley},
  year = {1984},
}
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "bibtest.tex"
            temp_tex.write_text(tex_content)
            temp_bib = Path(temp_dir) / "refs.bib"
            temp_bib.write_text(bib_content)

            result = compile_latex(str(temp_tex), passes="auto")
            assert result.success is True
            assert result.passes_run is not None
            assert result.passes_run >= 2

    def test_biber_run_with_addbibresource(self):
        """Test that biber is run when \\addbibresource{} is detected."""
        tex_content = r"""\documentclass{article}
\usepackage[backend=biber]{biblatex}
\addbibresource{refs.bib}
\begin{document}
Citation: \cite{knuth1984}.
\printbibliography
\end{document}
"""
        bib_content = r"""@book{knuth1984,
  author = {Donald E. Knuth},
  title = {The TeXbook},
  publisher = {Addison-Wesley},
  year = {1984},
}
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "bibertest.tex"
            temp_tex.write_text(tex_content)
            temp_bib = Path(temp_dir) / "refs.bib"
            temp_bib.write_text(bib_content)

            result = compile_latex(str(temp_tex), passes="auto")
            assert result.success is True
            assert result.passes_run is not None
            assert result.passes_run >= 2

    def test_no_bibliography_no_bibtex(self):
        """Test that bibtex/biber is NOT run when no bibliography detected."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple.tex"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / "test.tex"
            temp_tex.write_text(fixture_path.read_text())

            with patch("subprocess.run", wraps=subprocess.run) as mock_run:
                result = compile_latex(str(temp_tex), passes="auto")
                for c in mock_run.call_args_list:
                    cmd = c[0][0]
                    assert cmd[0] not in ("bibtex", "biber"), (
                        f"bibtex/biber should not run without bibliography, got: {cmd}"
                    )
            assert result.success is True


class TestCompilationResultNewFields:
    """Test cases for new fields on CompilationResult."""

    def test_compilation_result_has_engine_field(self):
        """Test CompilationResult includes engine field."""
        result = CompilationResult(
            success=True,
            output_path="/path/to/output.pdf",
            engine="xelatex",
            passes_run=2,
        )
        assert result.engine == "xelatex"

    def test_compilation_result_has_passes_run_field(self):
        """Test CompilationResult includes passes_run field."""
        result = CompilationResult(
            success=True,
            output_path="/path/to/output.pdf",
            engine="pdflatex",
            passes_run=3,
        )
        assert result.passes_run == 3

    def test_compilation_result_defaults(self):
        """Test CompilationResult new fields default to None."""
        result = CompilationResult(success=False)
        assert result.engine is None
        assert result.passes_run is None
