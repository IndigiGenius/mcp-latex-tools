"""LaTeX compilation tool for MCP server."""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


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


def compile_latex(
    tex_path: str, output_dir: Optional[str] = None, timeout: Optional[int] = None
) -> CompilationResult:
    """
    Compile a LaTeX file to PDF.

    Args:
        tex_path: Path to the .tex file to compile
        output_dir: Directory for output (defaults to same as input)
        timeout: Maximum seconds to wait for compilation

    Returns:
        CompilationResult with success status and details

    Raises:
        CompilationError: If input validation fails
    """
    # Validate input
    if not tex_path:
        raise CompilationError("LaTeX file path cannot be empty")

    if tex_path is None:
        raise CompilationError("LaTeX file path cannot be None")

    tex_file = Path(tex_path)
    if not tex_file.exists():
        raise CompilationError(f"LaTeX file not found: {tex_path}")

    # Set up paths
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = tex_file.parent

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Expected output PDF path
    pdf_path = output_path / (tex_file.stem + ".pdf")

    # Prepare pdflatex command
    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory",
        str(output_path),
        str(tex_file),
    ]

    start_time = time.time()

    try:
        # Run pdflatex
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=str(output_path)
        )

        compilation_time = time.time() - start_time

        # Read log file if it exists
        log_path = output_path / (tex_file.stem + ".log")
        log_content = ""
        if log_path.exists():
            try:
                log_content = log_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                log_content = "Could not read log file"

        # Check if compilation was successful
        if result.returncode == 0 and pdf_path.exists():
            return CompilationResult(
                success=True,
                output_path=str(pdf_path),
                log_content=log_content,
                compilation_time_seconds=compilation_time,
            )
        else:
            # Compilation failed
            error_msg = f"LaTeX compilation failed with return code {result.returncode}"
            if result.stderr:
                error_msg += f": {result.stderr}"

            return CompilationResult(
                success=False,
                error_message=error_msg,
                log_content=log_content,
                compilation_time_seconds=compilation_time,
            )

    except subprocess.TimeoutExpired:
        compilation_time = time.time() - start_time
        return CompilationResult(
            success=False,
            error_message=f"LaTeX compilation timed out after {timeout} seconds",
            compilation_time_seconds=compilation_time,
        )

    except PermissionError as e:
        compilation_time = time.time() - start_time
        return CompilationResult(
            success=False,
            error_message=f"Permission denied during compilation: {e}",
            compilation_time_seconds=compilation_time,
        )

    except Exception as e:
        compilation_time = time.time() - start_time
        return CompilationResult(
            success=False,
            error_message=f"Unexpected error during compilation: {e}",
            compilation_time_seconds=compilation_time,
        )
