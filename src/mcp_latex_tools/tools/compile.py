"""LaTeX compilation tool for MCP server."""

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from mcp_latex_tools.utils.log_parser import parse_latex_log

SUPPORTED_ENGINES = ("pdflatex", "xelatex", "lualatex", "latexmk")


class CompilationError(Exception):
    """Exception raised when LaTeX compilation fails."""

    pass


@dataclass
class CompilationResult:
    """Result of LaTeX compilation."""

    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    log_content: Optional[str] = None
    compilation_time_seconds: Optional[float] = None
    engine: Optional[str] = None
    passes_run: Optional[int] = None


def _detect_bib_tool(tex_content: str) -> Optional[str]:
    """Detect whether bibtex or biber is needed based on .tex content.

    Returns "biber" if \\addbibresource is found (biblatex),
    "bibtex" if \\bibliography is found (traditional),
    or None if no bibliography detected.
    """
    if re.search(r"\\addbibresource\s*\{", tex_content):
        return "biber"
    if re.search(r"\\bibliography\s*\{", tex_content):
        return "bibtex"
    return None


def _build_engine_cmd(engine: str, output_path: Path, tex_file: Path) -> list[str]:
    """Build the command list for the given engine."""
    if engine == "latexmk":
        return [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            f"-output-directory={output_path}",
            str(tex_file),
        ]
    # pdflatex, xelatex, lualatex all share the same CLI interface
    return [
        engine,
        "-interaction=nonstopmode",
        "-output-directory",
        str(output_path),
        str(tex_file),
    ]


def _run_bib_tool(
    bib_tool: str, stem: str, output_path: Path, timeout: Optional[int]
) -> None:
    """Run bibtex or biber on the given document stem."""
    if bib_tool == "biber":
        cmd = ["biber", str(output_path / stem)]
    else:
        cmd = ["bibtex", stem]
    subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(output_path),
    )


def _run_single_pass(
    cmd: list[str],
    output_path: Path,
    timeout: Optional[int],
) -> subprocess.CompletedProcess[str]:
    """Run a single compilation pass."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(output_path),
    )


def _read_log(output_path: Path, stem: str) -> str:
    """Read the .log file for the given document."""
    log_path = output_path / f"{stem}.log"
    if log_path.exists():
        try:
            return log_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return "Could not read log file"
    return ""


def compile_latex(
    tex_path: str,
    output_dir: Optional[str] = None,
    timeout: Optional[int] = None,
    engine: str = "pdflatex",
    passes: Union[int, str] = 1,
) -> CompilationResult:
    """
    Compile a LaTeX file to PDF.

    Args:
        tex_path: Path to the .tex file to compile
        output_dir: Directory for output (defaults to same as input)
        timeout: Maximum seconds to wait for compilation
        engine: LaTeX engine to use (pdflatex, xelatex, lualatex, latexmk)
        passes: Number of compilation passes (1, 2, 3) or "auto" to detect

    Returns:
        CompilationResult with success status and details

    Raises:
        CompilationError: If input validation fails
    """
    # Validate input
    if not tex_path:
        raise CompilationError("LaTeX file path cannot be empty")

    tex_file = Path(tex_path)
    if not tex_file.exists():
        raise CompilationError(f"LaTeX file not found: {tex_path}")

    # Validate engine
    if engine not in SUPPORTED_ENGINES:
        raise CompilationError(
            f"Unsupported engine: '{engine}'. "
            f"Supported engines: {', '.join(SUPPORTED_ENGINES)}"
        )

    # Validate passes
    if isinstance(passes, str):
        if passes != "auto":
            raise CompilationError(
                f"Invalid passes value: '{passes}'. Use 1, 2, 3, or 'auto'."
            )
    elif isinstance(passes, int):
        if passes < 1 or passes > 3:
            raise CompilationError(
                f"Invalid passes value: {passes}. Must be 1, 2, or 3."
            )
    else:
        raise CompilationError(
            f"Invalid passes type: {type(passes).__name__}. Use int or 'auto'."
        )

    # Set up paths
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = tex_file.parent

    output_path.mkdir(parents=True, exist_ok=True)

    pdf_path = output_path / (tex_file.stem + ".pdf")
    cmd = _build_engine_cmd(engine, output_path, tex_file)
    start_time = time.time()

    try:
        if engine == "latexmk":
            return _compile_latexmk(
                cmd, tex_file, output_path, pdf_path, timeout, start_time
            )

        return _compile_multi_pass(
            cmd,
            tex_file,
            output_path,
            pdf_path,
            timeout,
            engine,
            passes,
            start_time,
        )

    except subprocess.TimeoutExpired:
        compilation_time = time.time() - start_time
        return CompilationResult(
            success=False,
            error_message=f"LaTeX compilation timed out after {timeout} seconds",
            compilation_time_seconds=compilation_time,
            engine=engine,
        )

    except PermissionError as e:
        compilation_time = time.time() - start_time
        return CompilationResult(
            success=False,
            error_message=f"Permission denied during compilation: {e}",
            compilation_time_seconds=compilation_time,
            engine=engine,
        )

    except Exception as e:
        compilation_time = time.time() - start_time
        return CompilationResult(
            success=False,
            error_message=f"Unexpected error during compilation: {e}",
            compilation_time_seconds=compilation_time,
            engine=engine,
        )


def _compile_latexmk(
    cmd: list[str],
    tex_file: Path,
    output_path: Path,
    pdf_path: Path,
    timeout: Optional[int],
    start_time: float,
) -> CompilationResult:
    """Compile using latexmk, which handles passes automatically."""
    result = _run_single_pass(cmd, output_path, timeout)
    compilation_time = time.time() - start_time
    log_content = _read_log(output_path, tex_file.stem)

    # Count latexmk passes from log
    passes_run = max(1, len(re.findall(r"Rule.*pdflatex|Run number \d+", log_content)))

    if result.returncode == 0 and pdf_path.exists():
        return CompilationResult(
            success=True,
            output_path=str(pdf_path),
            log_content=log_content,
            compilation_time_seconds=compilation_time,
            engine="latexmk",
            passes_run=passes_run,
        )

    error_msg = f"LaTeX compilation failed with return code {result.returncode}"
    if result.stderr:
        error_msg += f": {result.stderr}"
    return CompilationResult(
        success=False,
        error_message=error_msg,
        log_content=log_content,
        compilation_time_seconds=compilation_time,
        engine="latexmk",
        passes_run=passes_run,
    )


def _compile_multi_pass(
    cmd: list[str],
    tex_file: Path,
    output_path: Path,
    pdf_path: Path,
    timeout: Optional[int],
    engine: str,
    passes: Union[int, str],
    start_time: float,
) -> CompilationResult:
    """Compile with explicit pass control (pdflatex, xelatex, lualatex)."""
    tex_content = tex_file.read_text(encoding="utf-8", errors="ignore")
    bib_tool = _detect_bib_tool(tex_content)

    if passes == "auto":
        max_passes = 3
    else:
        max_passes = int(passes)

    passes_run = 0
    log_content = ""
    last_result: Optional[subprocess.CompletedProcess[str]] = None

    for pass_num in range(1, max_passes + 1):
        # Run engine
        last_result = _run_single_pass(cmd, output_path, timeout)
        passes_run = pass_num
        log_content = _read_log(output_path, tex_file.stem)

        # If the engine hard-fails on first pass, stop immediately
        if last_result.returncode != 0 and pass_num == 1 and not pdf_path.exists():
            break

        # Run bibliography tool after first pass
        if pass_num == 1 and bib_tool:
            try:
                _run_bib_tool(bib_tool, tex_file.stem, output_path, timeout)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass  # Non-fatal — continue compilation

        # For "auto" mode: check if another pass is needed
        if passes == "auto" and pass_num < max_passes:
            summary = parse_latex_log(log_content)
            if (
                not summary.has_rerun_suggestion
                and not summary.has_undefined_references
            ):
                break

    compilation_time = time.time() - start_time

    if pdf_path.exists():
        return CompilationResult(
            success=True,
            output_path=str(pdf_path),
            log_content=log_content,
            compilation_time_seconds=compilation_time,
            engine=engine,
            passes_run=passes_run,
        )

    returncode = last_result.returncode if last_result else 1
    error_msg = f"LaTeX compilation failed with return code {returncode}"
    if last_result and last_result.stderr:
        error_msg += f": {last_result.stderr}"
    return CompilationResult(
        success=False,
        error_message=error_msg,
        log_content=log_content,
        compilation_time_seconds=compilation_time,
        engine=engine,
        passes_run=passes_run,
    )
