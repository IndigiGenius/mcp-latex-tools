"""LaTeX package detection tool for identifying required packages."""

import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class PackageDetectionError(Exception):
    """Exception raised for package detection errors."""

    pass


@dataclass
class PackageDetectionResult:
    """Result of LaTeX package detection."""

    success: bool
    packages: list[str]
    installed: list[str]
    missing: list[str]
    install_commands: list[str]
    error_message: Optional[str] = None
    file_path: Optional[str] = None
    detection_time_seconds: Optional[float] = None


# Regex: match \usepackage or \RequirePackage, with optional [...] options, capture {packages}
# Only match lines where % does not precede the command
_PACKAGE_RE = re.compile(
    r"^[^%\n]*\\(?:usepackage|RequirePackage)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}",
    re.MULTILINE,
)


def _parse_packages(content: str) -> list[str]:
    """Parse package names from LaTeX file content.

    Returns a deduplicated, sorted list of package names.
    """
    packages: set[str] = set()
    for match in _PACKAGE_RE.finditer(content):
        raw = match.group(1)
        for pkg in raw.split(","):
            name = pkg.strip()
            if name:
                packages.add(name)
    return sorted(packages)


def _check_installed(packages: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Check which packages are installed via kpsewhich.

    Returns (installed, missing, install_commands).
    """
    if not shutil.which("kpsewhich"):
        raise PackageDetectionError(
            "kpsewhich not found. Is TeX Live installed and on PATH?"
        )

    installed: list[str] = []
    missing: list[str] = []
    install_commands: list[str] = []

    for pkg in packages:
        result = subprocess.run(
            ["kpsewhich", f"{pkg}.sty"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            installed.append(pkg)
        else:
            missing.append(pkg)
            install_commands.append(f"tlmgr install {pkg}")

    return installed, missing, install_commands


def detect_packages(
    file_path: Optional[str], check_installed: bool = True
) -> PackageDetectionResult:
    """Detect LaTeX packages required by a .tex file.

    Args:
        file_path: Path to the LaTeX file to analyze.
        check_installed: If True, check each package against TeX Live
            via kpsewhich. If False, only parse package declarations.

    Returns:
        PackageDetectionResult with detected packages and installation status.

    Raises:
        PackageDetectionError: If file path is invalid or file cannot be read.
    """
    start_time = time.time()

    # Validate input
    if file_path is None:
        raise PackageDetectionError("File path cannot be None")
    if not file_path:
        raise PackageDetectionError("File path cannot be empty")

    path = Path(file_path)

    if not path.exists():
        raise PackageDetectionError(f"File not found: {file_path}")
    if path.suffix.lower() != ".tex":
        raise PackageDetectionError(
            f"Expected .tex file, got '{path.suffix}': {file_path}"
        )

    content = path.read_text(encoding="utf-8", errors="replace")
    packages = _parse_packages(content)

    installed_list: list[str] = []
    missing_list: list[str] = []
    commands: list[str] = []

    if check_installed and packages:
        installed_list, missing_list, commands = _check_installed(packages)

    elapsed = time.time() - start_time

    return PackageDetectionResult(
        success=True,
        packages=packages,
        installed=installed_list,
        missing=missing_list,
        install_commands=commands,
        file_path=file_path,
        detection_time_seconds=elapsed,
    )
