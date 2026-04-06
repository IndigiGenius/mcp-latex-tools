"""LaTeX log parsing utilities for extracting concise error information."""

import re
from typing import List, Optional

from pydantic import BaseModel


class LaTeXError(BaseModel):
    """Represents a LaTeX error extracted from logs."""

    line_number: Optional[int]
    error_type: str
    message: str
    context: Optional[str] = None


class LogSummary(BaseModel):
    """Concise summary of LaTeX compilation log."""

    errors: List[LaTeXError]
    warnings_count: int
    pages_count: Optional[int] = None
    has_undefined_references: bool = False
    has_rerun_suggestion: bool = False


def parse_latex_log(log_content: str, max_errors: int = 10) -> LogSummary:
    """
    Parse LaTeX log and extract only essential error information.

    Args:
        log_content: Full LaTeX log content
        max_errors: Maximum number of errors to extract (default: 10)

    Returns:
        LogSummary with concise error information
    """
    if not log_content:
        return LogSummary(errors=[], warnings_count=0)

    errors: List[LaTeXError] = []
    warnings_count = 0
    pages_count = None
    has_undefined_references = False
    has_rerun_suggestion = False

    lines = log_content.split("\n")
    i = 0

    while i < len(lines) and len(errors) < max_errors:
        line = lines[i]

        # Detect LaTeX errors (! prefix)
        if line.startswith("!"):
            error = _parse_error_block(lines, i)
            if error:
                errors.append(error)

        # Count warnings (case-insensitive)
        if "warning" in line.lower():
            warnings_count += 1

        # Count overfull/underfull hbox as warnings (elif to avoid double-counting)
        elif "overfull" in line.lower() or "underfull" in line.lower():
            warnings_count += 1

        # Check for undefined references
        if "undefined references" in line.lower() or (
            "reference" in line.lower() and "undefined" in line.lower()
        ):
            has_undefined_references = True

        # Check for rerun suggestion
        if "rerun" in line.lower() and (
            "latex" in line.lower() or "get" in line.lower()
        ):
            has_rerun_suggestion = True

        # Extract page count from final output
        if "Output written on" in line:
            page_match = re.search(r"\((\d+) page", line)
            if page_match:
                pages_count = int(page_match.group(1))

        i += 1

    return LogSummary(
        errors=errors,
        warnings_count=warnings_count,
        pages_count=pages_count,
        has_undefined_references=has_undefined_references,
        has_rerun_suggestion=has_rerun_suggestion,
    )


def _parse_error_block(lines: List[str], start_index: int) -> Optional[LaTeXError]:
    r"""
    Parse a LaTeX error block starting with '!'.

    LaTeX errors typically look like:
    ! LaTeX Error: ...

    See the LaTeX manual or LaTeX Companion for explanation.
    Type  H <return>  for immediate help.
     ...

    l.123 \somecommand
    """
    if start_index >= len(lines):
        return None

    error_line = lines[start_index]

    # Extract error type and message
    error_match = re.match(r"!\s+(.+?):\s*(.+)", error_line)
    if error_match:
        error_type = error_match.group(1)
        message = error_match.group(2).strip()
    else:
        # Generic error without type
        error_type = "LaTeX Error"
        message = error_line[1:].strip()  # Remove '!' prefix

    # Look for line number in the following lines
    line_number = None
    context = None

    # Check next few lines for line number (l.XXX format)
    # Need to look further for multi-line error messages
    for offset in range(1, min(15, len(lines) - start_index)):
        next_line = lines[start_index + offset]

        # Look for line number pattern (may have leading whitespace)
        line_match = re.match(r"\s*l\.(\d+)\s*(.*)", next_line)
        if line_match:
            line_number = int(line_match.group(1))
            context_text = line_match.group(2).strip()
            if context_text:
                context = context_text
            break

        # Stop at next error
        if next_line.startswith("!"):
            break

    return LaTeXError(
        line_number=line_number,
        error_type=error_type,
        message=message,
        context=context,
    )


def format_log_summary(summary: LogSummary, show_all: bool = False) -> str:
    """
    Format log summary as concise human-readable text.

    Args:
        summary: LogSummary object
        show_all: If True, show all errors; if False, show first 5

    Returns:
        Formatted string for display
    """
    if not summary.errors and summary.warnings_count == 0:
        return "No errors or warnings"

    lines = []

    # Show errors
    if summary.errors:
        max_display = len(summary.errors) if show_all else min(5, len(summary.errors))
        lines.append(f"Errors ({len(summary.errors)}):")

        for i, error in enumerate(summary.errors[:max_display]):
            error_prefix = f"  [{i + 1}]"
            if error.line_number:
                error_prefix += f" Line {error.line_number}:"
            else:
                error_prefix += ":"

            lines.append(f"{error_prefix} {error.error_type}")
            lines.append(f"      {error.message}")

            if error.context:
                lines.append(f"      Context: {error.context}")

        if len(summary.errors) > max_display:
            remaining = len(summary.errors) - max_display
            lines.append(f"  ... and {remaining} more error(s)")

    # Show warnings count (not full warnings text)
    if summary.warnings_count > 0:
        lines.append(f"Warnings: {summary.warnings_count} (use full log for details)")

    # Show suggestions
    if summary.has_undefined_references:
        lines.append("Note: Document has undefined references")

    if summary.has_rerun_suggestion:
        lines.append("Suggestion: Rerun LaTeX to resolve cross-references")

    return "\n".join(lines)


def get_error_summary(log_content: str) -> str:
    """
    Quick helper to get a concise error summary from log content.

    Args:
        log_content: Full LaTeX log content

    Returns:
        Concise formatted error summary
    """
    if not log_content:
        return "No log content available"

    summary = parse_latex_log(log_content, max_errors=10)
    return format_log_summary(summary, show_all=False)
