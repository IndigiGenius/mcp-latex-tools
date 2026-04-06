"""Tests for LaTeX package detection tool."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from mcp_latex_tools.tools.detect_packages import (
    detect_packages,
    PackageDetectionError,
    PackageDetectionResult,
)


class TestPackageDetectionResult:
    """Test PackageDetectionResult dataclass."""

    def test_result_fields(self):
        """Test all fields are present and correct."""
        result = PackageDetectionResult(
            success=True,
            packages=["amsmath", "geometry"],
            installed=["amsmath"],
            missing=["geometry"],
            install_commands=["tlmgr install geometry"],
        )
        assert result.success is True
        assert result.packages == ["amsmath", "geometry"]
        assert result.installed == ["amsmath"]
        assert result.missing == ["geometry"]
        assert result.install_commands == ["tlmgr install geometry"]

    def test_result_defaults(self):
        """Test optional fields default to None."""
        result = PackageDetectionResult(
            success=True,
            packages=[],
            installed=[],
            missing=[],
            install_commands=[],
        )
        assert result.error_message is None
        assert result.file_path is None
        assert result.detection_time_seconds is None

    def test_result_with_error(self):
        """Test result with error message."""
        result = PackageDetectionResult(
            success=False,
            error_message="File not found",
            packages=[],
            installed=[],
            missing=[],
            install_commands=[],
        )
        assert result.success is False
        assert result.error_message == "File not found"

    def test_error_exception(self):
        """Test PackageDetectionError exception."""
        error = PackageDetectionError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)


class TestDetectPackagesParsing:
    """Test package parsing from .tex files (no installation checks)."""

    def _detect_parse_only(self, content: str) -> PackageDetectionResult:
        """Helper: write content to temp .tex file and detect with check_installed=False."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            f.write(content)
            tex_path = f.name

        try:
            return detect_packages(tex_path, check_installed=False)
        finally:
            Path(tex_path).unlink()

    def test_single_usepackage(self):
        """Test detection of a single \\usepackage."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage{amsmath}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["amsmath"]

    def test_multiple_usepackages(self):
        """Test detection of multiple \\usepackage declarations."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{geometry}
\usepackage{hyperref}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["amsmath", "geometry", "hyperref"]

    def test_comma_separated_packages(self):
        """Test detection of comma-separated packages in single \\usepackage."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage{amsmath,amssymb,amsthm}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["amsmath", "amssymb", "amsthm"]

    def test_usepackage_with_options(self):
        """Test \\usepackage with options are parsed correctly."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=1in]{geometry}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["fontenc", "geometry", "inputenc"]

    def test_requirepackage(self):
        """Test detection of \\RequirePackage."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\RequirePackage{etoolbox}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["etoolbox"]

    def test_requirepackage_with_options(self):
        """Test detection of \\RequirePackage with options."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\RequirePackage[dvipsnames]{xcolor}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["xcolor"]

    def test_commented_out_packages_skipped(self):
        """Test that commented-out package declarations are skipped."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage{amsmath}
% \usepackage{tikz}
  % \usepackage{pgfplots}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["amsmath"]
        assert "tikz" not in result.packages
        assert "pgfplots" not in result.packages

    def test_deduplicated_packages(self):
        """Test that duplicate packages are deduplicated."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{amsmath}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["amsmath"]

    def test_sorted_packages(self):
        """Test that packages are returned sorted."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage{zref}
\usepackage{amsmath}
\usepackage{hyperref}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["amsmath", "hyperref", "zref"]

    def test_no_packages(self):
        """Test file with no packages."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == []

    def test_mixed_usepackage_and_requirepackage(self):
        """Test file with both \\usepackage and \\RequirePackage."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\RequirePackage{etoolbox}
\usepackage{amsmath}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["amsmath", "etoolbox"]

    def test_usepackage_star_variant(self):
        """Test detection of \\usepackage* (starred variant)."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage*{amsmath}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["amsmath"]

    def test_invalid_package_names_filtered(self):
        """Test that invalid package names are filtered out."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{../../etc/passwd}
\usepackage{evil;rm -rf /}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.success is True
        assert result.packages == ["amsmath"]

    def test_empty_file(self):
        """Test empty .tex file returns no packages."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            f.write("")
            tex_path = f.name

        try:
            result = detect_packages(tex_path, check_installed=False)
            assert result.success is True
            assert result.packages == []
        finally:
            Path(tex_path).unlink()

    def test_check_installed_false_skips_checks(self):
        """Test that check_installed=False leaves installed/missing empty."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage{amsmath}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.installed == []
        assert result.missing == []
        assert result.install_commands == []

    def test_result_includes_file_path(self):
        """Test that result includes the file path."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            f.write(r"\documentclass{article}\begin{document}Hi\end{document}")
            tex_path = f.name

        try:
            result = detect_packages(tex_path, check_installed=False)
            assert result.file_path == tex_path
        finally:
            Path(tex_path).unlink()

    def test_result_includes_timing(self):
        """Test that result includes detection time."""
        result = self._detect_parse_only(
            r"""
\documentclass{article}
\usepackage{amsmath}
\begin{document}
Hello
\end{document}
"""
        )
        assert result.detection_time_seconds is not None
        assert result.detection_time_seconds >= 0


class TestDetectPackagesInstalled:
    """Test package installation checking via kpsewhich."""

    def _write_tex(self, content: str) -> str:
        """Helper: write content to temp .tex file, return path."""
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_installed_package_detected(self):
        """Test that an installed package is reported as installed."""
        tex_path = self._write_tex(
            r"""
\documentclass{article}
\usepackage{amsmath}
\begin{document}
Hello
\end{document}
"""
        )
        try:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = (
                "/usr/share/texlive/texmf-dist/tex/latex/amsmath/amsmath.sty\n"
            )

            with patch(
                "mcp_latex_tools.tools.detect_packages.subprocess.run",
                return_value=mock_result,
            ):
                with patch(
                    "mcp_latex_tools.tools.detect_packages.shutil.which",
                    return_value="/usr/bin/kpsewhich",
                ):
                    result = detect_packages(tex_path, check_installed=True)

            assert result.success is True
            assert "amsmath" in result.installed
            assert "amsmath" not in result.missing
            assert result.install_commands == []
        finally:
            Path(tex_path).unlink()

    def test_missing_package_detected(self):
        """Test that a missing package is reported as missing."""
        tex_path = self._write_tex(
            r"""
\documentclass{article}
\usepackage{nonexistentpackagexyz}
\begin{document}
Hello
\end{document}
"""
        )
        try:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""

            with patch(
                "mcp_latex_tools.tools.detect_packages.subprocess.run",
                return_value=mock_result,
            ):
                with patch(
                    "mcp_latex_tools.tools.detect_packages.shutil.which",
                    return_value="/usr/bin/kpsewhich",
                ):
                    result = detect_packages(tex_path, check_installed=True)

            assert result.success is True
            assert "nonexistentpackagexyz" in result.missing
            assert "nonexistentpackagexyz" not in result.installed
        finally:
            Path(tex_path).unlink()

    def test_install_commands_generated(self):
        """Test that tlmgr install commands are generated for missing packages."""
        tex_path = self._write_tex(
            r"""
\documentclass{article}
\usepackage{missingpkg}
\begin{document}
Hello
\end{document}
"""
        )
        try:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""

            with patch(
                "mcp_latex_tools.tools.detect_packages.subprocess.run",
                return_value=mock_result,
            ):
                with patch(
                    "mcp_latex_tools.tools.detect_packages.shutil.which",
                    return_value="/usr/bin/kpsewhich",
                ):
                    result = detect_packages(tex_path, check_installed=True)

            assert "tlmgr install missingpkg" in result.install_commands
        finally:
            Path(tex_path).unlink()

    def test_mixed_installed_and_missing(self):
        """Test file with both installed and missing packages."""
        tex_path = self._write_tex(
            r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{nonexistentxyz}
\begin{document}
Hello
\end{document}
"""
        )
        try:

            def mock_run(cmd, *args, **kwargs):
                result = MagicMock()
                if any("amsmath.sty" in arg for arg in cmd):
                    result.returncode = 0
                    result.stdout = "/path/to/amsmath.sty\n"
                else:
                    result.returncode = 1
                    result.stdout = ""
                return result

            with patch(
                "mcp_latex_tools.tools.detect_packages.subprocess.run",
                side_effect=mock_run,
            ):
                with patch(
                    "mcp_latex_tools.tools.detect_packages.shutil.which",
                    return_value="/usr/bin/kpsewhich",
                ):
                    result = detect_packages(tex_path, check_installed=True)

            assert "amsmath" in result.installed
            assert "nonexistentxyz" in result.missing
            assert "tlmgr install nonexistentxyz" in result.install_commands
        finally:
            Path(tex_path).unlink()

    def test_kpsewhich_timeout_treated_as_missing(self):
        """Test that kpsewhich timeout is handled gracefully."""
        tex_path = self._write_tex(
            r"""
\documentclass{article}
\usepackage{slowpkg}
\begin{document}
Hello
\end{document}
"""
        )
        try:
            with patch(
                "mcp_latex_tools.tools.detect_packages.subprocess.run",
                side_effect=subprocess.TimeoutExpired(cmd="kpsewhich", timeout=5),
            ):
                with patch(
                    "mcp_latex_tools.tools.detect_packages.shutil.which",
                    return_value="/usr/bin/kpsewhich",
                ):
                    result = detect_packages(tex_path, check_installed=True)

            assert result.success is True
            assert "slowpkg" in result.missing
            assert "tlmgr install slowpkg" in result.install_commands
        finally:
            Path(tex_path).unlink()

    def test_kpsewhich_not_available_raises_error(self):
        """Test that missing kpsewhich raises PackageDetectionError."""
        tex_path = self._write_tex(
            r"""
\documentclass{article}
\usepackage{amsmath}
\begin{document}
Hello
\end{document}
"""
        )
        try:
            with patch(
                "mcp_latex_tools.tools.detect_packages.shutil.which", return_value=None
            ):
                with pytest.raises(PackageDetectionError) as exc_info:
                    detect_packages(tex_path, check_installed=True)

            assert "kpsewhich" in str(exc_info.value).lower()
        finally:
            Path(tex_path).unlink()


class TestDetectPackagesErrors:
    """Test error handling in detect_packages."""

    def test_none_path_raises_error(self):
        """Test that None file path raises PackageDetectionError."""
        with pytest.raises(PackageDetectionError):
            detect_packages(None, check_installed=False)

    def test_empty_path_raises_error(self):
        """Test that empty file path raises PackageDetectionError."""
        with pytest.raises(PackageDetectionError):
            detect_packages("", check_installed=False)

    def test_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises PackageDetectionError."""
        with pytest.raises(PackageDetectionError) as exc_info:
            detect_packages("/nonexistent/file.tex", check_installed=False)

        assert "not found" in str(exc_info.value).lower()

    def test_non_tex_file_raises_error(self):
        """Test that non-.tex file raises PackageDetectionError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("not a tex file")
            txt_path = f.name

        try:
            with pytest.raises(PackageDetectionError) as exc_info:
                detect_packages(txt_path, check_installed=False)

            assert ".tex" in str(exc_info.value).lower()
        finally:
            Path(txt_path).unlink()
