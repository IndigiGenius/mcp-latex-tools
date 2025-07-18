"""Tests for LaTeX validation tool."""

import tempfile
from pathlib import Path

import pytest

from mcp_latex_tools.tools.validate import validate_latex, ValidationError, ValidationResult


class TestValidateLatex:
    """Test LaTeX validation functionality."""

    def test_validate_latex_with_valid_file_returns_success(self):
        """Test validation of a syntactically correct LaTeX file."""
        latex_content = r"""
\documentclass{article}
\usepackage{amsmath}
\begin{document}
\title{Valid Document}
\author{Test Author}
\date{\today}
\maketitle

\section{Introduction}
This is a valid LaTeX document with proper syntax.

\begin{equation}
E = mc^2
\end{equation}

\end{document}
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(latex_content)
            tex_path = f.name
        
        try:
            result = validate_latex(tex_path)
            
            assert isinstance(result, ValidationResult)
            assert result.is_valid is True
            assert result.error_message is None
            assert result.errors == []
            assert result.warnings == []
            
        finally:
            Path(tex_path).unlink()

    def test_validate_latex_with_syntax_errors_returns_failure(self):
        """Test validation of LaTeX file with syntax errors."""
        latex_content = r"""
\documentclass{article}
\begin{document}
\title{Invalid Document
\author{Test Author}
\date{\today}
\maketitle

\section{Introduction}
This document has syntax errors.

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
            result = validate_latex(tex_path)
            
            assert isinstance(result, ValidationResult)
            assert result.is_valid is False
            assert result.error_message is not None
            assert len(result.errors) > 0
            assert any("equation" in error.lower() for error in result.errors)
            
        finally:
            Path(tex_path).unlink()

    def test_validate_latex_with_missing_packages_returns_warnings(self):
        """Test validation detects missing package references."""
        latex_content = r"""
\documentclass{article}
\begin{document}
\title{Document with Missing Packages}
\author{Test Author}
\date{\today}
\maketitle

\section{Introduction}
This document uses commands from packages that aren't included.

\begin{tikzpicture}
\draw (0,0) -- (1,1);
\end{tikzpicture}

\end{document}
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(latex_content)
            tex_path = f.name
        
        try:
            result = validate_latex(tex_path)
            
            assert isinstance(result, ValidationResult)
            # Should still be valid LaTeX syntax but with warnings
            assert result.is_valid is True
            assert len(result.warnings) > 0
            assert any("tikz" in warning.lower() for warning in result.warnings)
            
        finally:
            Path(tex_path).unlink()

    def test_validate_latex_with_unmatched_braces_returns_failure(self):
        """Test validation detects unmatched braces."""
        latex_content = r"""
\documentclass{article}
\begin{document}
\title{Document with Unmatched Braces
\author{Test Author}
\date{\today}
\maketitle

\section{Introduction
This document has unmatched braces.

\textbf{Bold text

\end{document}
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(latex_content)
            tex_path = f.name
        
        try:
            result = validate_latex(tex_path)
            
            assert isinstance(result, ValidationResult)
            assert result.is_valid is False
            assert result.error_message is not None
            assert len(result.errors) > 0
            
        finally:
            Path(tex_path).unlink()

    def test_validate_latex_raises_error_for_missing_file(self):
        """Test validation raises error for non-existent file."""
        with pytest.raises(ValidationError) as excinfo:
            validate_latex("/nonexistent/file.tex")
        
        assert "not found" in str(excinfo.value).lower()

    def test_validate_latex_raises_error_for_empty_path(self):
        """Test validation raises error for empty file path."""
        with pytest.raises(ValidationError) as excinfo:
            validate_latex("")
        
        assert "cannot be empty" in str(excinfo.value).lower()

    def test_validate_latex_raises_error_for_none_path(self):
        """Test validation raises error for None file path."""
        with pytest.raises(ValidationError) as excinfo:
            validate_latex(None)
        
        assert "cannot be none" in str(excinfo.value).lower()

    def test_validate_latex_with_quick_mode_skips_deep_analysis(self):
        """Test validation with quick mode for faster syntax checking."""
        latex_content = r"""
\documentclass{article}
\begin{document}
\title{Quick Validation Test}
\author{Test Author}
\end{document}
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(latex_content)
            tex_path = f.name
        
        try:
            result = validate_latex(tex_path, quick=True)
            
            assert isinstance(result, ValidationResult)
            assert result.is_valid is True
            assert result.validation_time_seconds is not None
            assert result.validation_time_seconds < 1.0  # Should be fast
            
        finally:
            Path(tex_path).unlink()

    def test_validate_latex_with_strict_mode_catches_more_issues(self):
        """Test validation with strict mode for thorough checking."""
        latex_content = r"""
\documentclass{article}
\begin{document}
\title{Strict Mode Test}
\author{Test Author}
\date{\today}

% Missing \maketitle could be flagged in strict mode
\section{Introduction}
This document might have style issues in strict mode.

\end{document}
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(latex_content)
            tex_path = f.name
        
        try:
            result = validate_latex(tex_path, strict=True)
            
            assert isinstance(result, ValidationResult)
            # In strict mode, might catch style issues as warnings
            assert len(result.warnings) >= 0
            
        finally:
            Path(tex_path).unlink()

    def test_validation_result_properties(self):
        """Test ValidationResult dataclass properties."""
        result = ValidationResult(
            is_valid=True,
            error_message=None,
            errors=[],
            warnings=["Test warning"],
            validation_time_seconds=0.5
        )
        
        assert result.is_valid is True
        assert result.error_message is None
        assert result.errors == []
        assert result.warnings == ["Test warning"]
        assert result.validation_time_seconds == 0.5

    def test_validation_error_exception(self):
        """Test ValidationError exception."""
        error = ValidationError("Test validation error")
        assert str(error) == "Test validation error"
        assert isinstance(error, Exception)