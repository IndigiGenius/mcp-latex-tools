"""Tests for LaTeX log parser utility."""

from mcp_latex_tools.utils.log_parser import (
    LaTeXError,
    LogSummary,
    parse_latex_log,
    format_log_summary,
    get_error_summary,
)


# Sample LaTeX log content for testing
SAMPLE_LOG_WITH_ERRORS = """This is pdfTeX, Version 3.14159265-2.6-1.40.20 (TeX Live 2019) (preloaded format=pdflatex)
 restricted \\write18 enabled.
entering extended mode
(./test.tex
LaTeX2e <2018-12-01>
! LaTeX Error: Missing \\begin{document}.

See the LaTeX manual or LaTeX Companion for explanation.
Type  H <return>  for immediate help.
 ...

l.5 Hello World

! Undefined control sequence.
l.10 \\invalidcommand

! LaTeX Error: \\begin{document} ended by \\end{itemize}.

See the LaTeX manual or LaTeX Companion for explanation.
Type  H <return>  for immediate help.
 ...

l.25 \\end{itemize}

LaTeX Warning: Reference `fig:example' on page 1 undefined on input line 30.

LaTeX Warning: Citation `einstein1905' on page 2 undefined on input line 45.

[1] [2] [3]
Output written on test.pdf (3 pages, 12345 bytes).
Transcript written on test.log.
"""


SAMPLE_LOG_SUCCESS = """This is pdfTeX, Version 3.14159265-2.6-1.40.20 (TeX Live 2019) (preloaded format=pdflatex)
 restricted \\write18 enabled.
entering extended mode
(./test.tex
LaTeX2e <2018-12-01>

LaTeX Warning: Reference `fig:example' on page 1 undefined on input line 30.

[1] [2]
Output written on test.pdf (2 pages, 12345 bytes).

LaTeX Warning: There were undefined references.

LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.

Transcript written on test.log.
"""


SAMPLE_LOG_MINIMAL = """This is pdfTeX, Version 3.14159265-2.6-1.40.20
[1]
Output written on test.pdf (1 page, 1234 bytes).
"""


def test_parse_latex_log_with_errors():
    """Test parsing log with multiple errors."""
    summary = parse_latex_log(SAMPLE_LOG_WITH_ERRORS)

    # Should extract errors
    assert len(summary.errors) >= 2
    assert summary.errors[0].error_type == "LaTeX Error"
    assert (
        "Missing" in summary.errors[0].message
        or "begin{document}" in summary.errors[0].message
    )

    # Should count warnings
    assert summary.warnings_count >= 2

    # Should extract page count
    assert summary.pages_count == 3

    # Should detect undefined references
    assert summary.has_undefined_references


def test_parse_latex_log_success_with_warnings():
    """Test parsing successful compilation with warnings."""
    summary = parse_latex_log(SAMPLE_LOG_SUCCESS)

    # Should have no errors
    assert len(summary.errors) == 0

    # Should count warnings
    assert summary.warnings_count >= 2

    # Should extract page count
    assert summary.pages_count == 2

    # Should detect undefined references
    assert summary.has_undefined_references

    # Should detect rerun suggestion
    assert summary.has_rerun_suggestion


def test_parse_latex_log_minimal():
    """Test parsing minimal successful log."""
    summary = parse_latex_log(SAMPLE_LOG_MINIMAL)

    # Should have no errors
    assert len(summary.errors) == 0

    # Should have no warnings
    assert summary.warnings_count == 0

    # Should extract page count
    assert summary.pages_count == 1


def test_parse_empty_log():
    """Test parsing empty log content."""
    summary = parse_latex_log("")

    assert len(summary.errors) == 0
    assert summary.warnings_count == 0
    assert summary.pages_count is None


def test_parse_latex_log_max_errors():
    """Test that max_errors parameter limits error extraction."""
    # Create log with many errors
    log_with_many_errors = "! Error 1\nl.1\n" * 20

    summary = parse_latex_log(log_with_many_errors, max_errors=5)

    # Should only extract up to max_errors
    assert len(summary.errors) <= 5


def test_latex_error_with_line_number():
    """Test parsing error with line number."""
    log = """! LaTeX Error: Undefined control sequence.

l.42 \\invalidcommand
"""

    summary = parse_latex_log(log)

    assert len(summary.errors) == 1
    assert summary.errors[0].line_number == 42
    assert summary.errors[0].error_type == "LaTeX Error"


def test_latex_error_without_line_number():
    """Test parsing error without line number."""
    log = """! LaTeX Error: Missing \\begin{document}.

See the LaTeX manual for explanation.
"""

    summary = parse_latex_log(log)

    assert len(summary.errors) == 1
    assert summary.errors[0].line_number is None


def test_format_log_summary_with_errors():
    """Test formatting log summary with errors."""
    summary = LogSummary(
        errors=[
            LaTeXError(
                line_number=42,
                error_type="LaTeX Error",
                message="Undefined control sequence",
                context="\\invalidcommand",
            ),
            LaTeXError(
                line_number=100,
                error_type="LaTeX Error",
                message="Missing \\begin{document}",
            ),
        ],
        warnings_count=3,
        pages_count=2,
        has_undefined_references=True,
        has_rerun_suggestion=False,
    )

    formatted = format_log_summary(summary)

    # Should include error count
    assert "Errors (2)" in formatted

    # Should include line numbers
    assert "Line 42" in formatted
    assert "Line 100" in formatted

    # Should include error types
    assert "LaTeX Error" in formatted

    # Should include warnings count
    assert "Warnings: 3" in formatted

    # Should include notes
    assert "undefined references" in formatted


def test_format_log_summary_no_errors():
    """Test formatting log summary with no errors."""
    summary = LogSummary(
        errors=[],
        warnings_count=0,
    )

    formatted = format_log_summary(summary)

    assert "No errors or warnings" in formatted


def test_format_log_summary_truncate_errors():
    """Test formatting log summary truncates to 5 errors by default."""
    errors = [
        LaTeXError(
            line_number=i,
            error_type="LaTeX Error",
            message=f"Error {i}",
        )
        for i in range(10)
    ]

    summary = LogSummary(
        errors=errors,
        warnings_count=0,
    )

    formatted = format_log_summary(summary, show_all=False)

    # Should show first 5 errors
    assert "Error 0" in formatted
    assert "Error 4" in formatted

    # Should indicate remaining errors
    assert "5 more error(s)" in formatted or "and 5 more" in formatted


def test_format_log_summary_show_all():
    """Test formatting log summary shows all errors when requested."""
    errors = [
        LaTeXError(
            line_number=i,
            error_type="LaTeX Error",
            message=f"Error {i}",
        )
        for i in range(10)
    ]

    summary = LogSummary(
        errors=errors,
        warnings_count=0,
    )

    formatted = format_log_summary(summary, show_all=True)

    # Should show all errors
    assert "Error 0" in formatted
    assert "Error 9" in formatted

    # Should not indicate remaining errors
    assert "more error(s)" not in formatted


def test_get_error_summary_empty_log():
    """Test get_error_summary with empty log."""
    result = get_error_summary("")

    assert "No log content available" in result


def test_get_error_summary_with_errors():
    """Test get_error_summary with log containing errors."""
    result = get_error_summary(SAMPLE_LOG_WITH_ERRORS)

    # Should contain error information
    assert "Error" in result or "error" in result

    # Should be concise (not thousands of lines)
    assert len(result.split("\n")) < 50


def test_get_error_summary_success():
    """Test get_error_summary with successful compilation."""
    result = get_error_summary(SAMPLE_LOG_SUCCESS)

    # Should mention warnings
    assert "Warning" in result or "warning" in result

    # Should be concise
    assert len(result.split("\n")) < 20


def test_unicode_error_parsing():
    """Test parsing Unicode-related errors."""
    log = """! LaTeX Error: Unicode character ─ (U+2500)
               not set up for use with LaTeX.

See the LaTeX manual or LaTeX Companion for explanation.
Type  H <return>  for immediate help.
 ...

l.749 \\end{verbatim}
"""

    summary = parse_latex_log(log)

    assert len(summary.errors) >= 1
    assert summary.errors[0].line_number == 749
    assert (
        "Unicode" in summary.errors[0].error_type
        or "Unicode" in summary.errors[0].message
    )


def test_overfull_hbox_not_treated_as_error():
    """Test that overfull hbox warnings are not treated as errors."""
    log = """
Overfull \\hbox (24.93141pt too wide) in paragraph at lines 759--769
 [][]
[]

[20]
Output written on test.pdf (20 pages, 123456 bytes).
"""

    summary = parse_latex_log(log)

    # Overfull hbox should not be in errors (it's not an error, just a warning)
    assert len(summary.errors) == 0

    # Should still count as warning
    assert summary.warnings_count >= 1


def test_font_info_not_included():
    """Test that font loading info doesn't bloat output."""
    log = """LaTeX Font Info:    External font `cmex10' loaded for size
(Font)              <10.95> on input line 759.
LaTeX Font Info:    External font `cmex10' loaded for size
(Font)              <8> on input line 759.
LaTeX Font Info:    External font `cmex10' loaded for size
(Font)              <6> on input line 759.

Output written on test.pdf (1 page, 1234 bytes).
"""

    result = get_error_summary(log)

    # Result should be concise and not include all font info
    assert "No errors" in result or "No log content" in result
    assert "cmex10" not in result
    assert len(result.split("\n")) < 10
