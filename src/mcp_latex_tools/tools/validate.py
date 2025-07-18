"""LaTeX validation tool for syntax checking without compilation."""

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class ValidationError(Exception):
    """Exception raised for validation errors."""

    pass


@dataclass
class ValidationResult:
    """Result of LaTeX validation."""

    is_valid: bool
    error_message: Optional[str]
    errors: list[str]
    warnings: list[str]
    validation_time_seconds: Optional[float] = None


def validate_latex(
    file_path: Optional[str], quick: bool = False, strict: bool = False
) -> ValidationResult:
    """
    Validate LaTeX file syntax without full compilation.

    Args:
        file_path: Path to the LaTeX file to validate
        quick: If True, perform quick syntax check only
        strict: If True, perform thorough validation with style checks

    Returns:
        ValidationResult containing validation status and any errors/warnings

    Raises:
        ValidationError: If file path is invalid or file cannot be read
    """
    start_time = time.time()

    # Validate input
    if file_path is None:
        raise ValidationError("File path cannot be None")
    if not file_path:
        raise ValidationError("File path cannot be empty")
    if quick and strict:
        raise ValidationError("Cannot use both quick and strict modes simultaneously")

    path = Path(file_path)
    if not path.exists():
        raise ValidationError(f"File not found: {file_path}")

    # Read file content
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        raise ValidationError(f"Failed to read file: {e}")

    errors = []
    warnings = []

    # Check for basic LaTeX structure
    if not re.search(r"\\documentclass\s*(\[.*?\])?\s*\{.*?\}", content):
        errors.append("Missing \\documentclass command")

    if not re.search(r"\\begin\s*\{document\}", content):
        errors.append("Missing \\begin{document}")

    if not re.search(r"\\end\s*\{document\}", content):
        errors.append("Missing \\end{document}")

    # Check for unmatched braces
    brace_count = 0
    for char in content:
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
        if brace_count < 0:
            errors.append("Unmatched closing brace }")
            break
    if brace_count > 0:
        errors.append(f"Unmatched opening braces: {brace_count} unclosed")
    elif brace_count < 0:
        errors.append(f"Unmatched closing braces: {abs(brace_count)} extra")

    # Check for unmatched environments
    environments = re.findall(r"\\begin\s*\{(\w+)\}", content)
    for env in environments:
        if not re.search(rf"\\end\s*\{{{env}\}}", content):
            errors.append(f"Unclosed environment: {env}")

    # Check for environments without begin
    end_envs = re.findall(r"\\end\s*\{(\w+)\}", content)
    for env in end_envs:
        if not re.search(rf"\\begin\s*\{{{env}\}}", content):
            errors.append(f"Environment ended without begin: {env}")

    if not quick:
        # Check for missing package declarations
        # Common commands that require packages
        package_commands = {
            "tikzpicture": "tikz",
            "includegraphics": "graphicx",
            "href": "hyperref",
            "url": "url or hyperref",
            "lstlisting": "listings",
            "algorithm": "algorithm",
            "align": "amsmath",
            "gather": "amsmath",
            "multirow": "multirow",
            "multicolumn": "array or tabularx",
        }

        for command, package in package_commands.items():
            if re.search(rf"\\(begin\s*\{{)?{command}", content) and not re.search(
                rf"\\usepackage.*\{{{package}", content
            ):
                warnings.append(
                    f"Command/environment '{command}' used but package '{package}' not included"
                )

    if strict:
        # Additional strict mode checks
        if (
            re.search(r"\\title\s*\{", content)
            and re.search(r"\\author\s*\{", content)
            and not re.search(r"\\maketitle", content)
        ):
            warnings.append("Title and author defined but \\maketitle not called")

        # Check for consecutive blank lines (more than 2)
        if re.search(r"\n\n\n+", content):
            warnings.append("Multiple consecutive blank lines detected")

        # Check for missing section structure
        if (
            "\\section" not in content
            and "\\chapter" not in content
            and "\\subsection" not in content
        ):
            warnings.append("No section structure found in document")

    # Determine overall validity
    is_valid = len(errors) == 0
    error_message = "; ".join(errors) if errors else None

    validation_time = time.time() - start_time

    return ValidationResult(
        is_valid=is_valid,
        error_message=error_message,
        errors=errors,
        warnings=warnings,
        validation_time_seconds=validation_time,
    )
