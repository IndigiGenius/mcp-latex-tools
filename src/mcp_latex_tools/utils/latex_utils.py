"""Common LaTeX utilities for file handling, validation, and processing."""

import os
import re
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Union


class LaTeXUtilsError(Exception):
    """Exception raised for LaTeX utilities errors."""
    pass


class FileValidationError(LaTeXUtilsError):
    """Exception raised for file validation errors."""
    pass


class ContentValidationError(LaTeXUtilsError):
    """Exception raised for content validation errors."""
    pass


@dataclass
class FileValidationResult:
    """Result of file validation operation."""
    is_valid: bool
    error_message: Optional[str]
    file_path: Optional[str]
    file_exists: bool
    is_readable: bool
    file_size_bytes: Optional[int]


@dataclass
class BraceCheckResult:
    """Result of brace balance checking."""
    is_balanced: bool
    error_message: Optional[str]
    unmatched_positions: List[int]
    missing_closing: int
    missing_opening: int


@dataclass
class EnvironmentCheckResult:
    """Result of environment matching checking."""
    all_matched: bool
    unmatched_environments: List[Dict[str, Any]]
    error_messages: List[str]


# LaTeX file extensions
LATEX_SOURCE_EXTENSIONS = {".tex", ".latex", ".ltx"}
LATEX_AUXILIARY_EXTENSIONS = {
    ".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".toc", ".lof", ".lot",
    ".bbl", ".blg", ".nav", ".snm", ".vrb", ".idx", ".ilg", ".ind", ".glo",
    ".gls", ".glg", ".synctex.gz", ".figlist", ".fpl", ".makefile", ".run.xml"
}
LATEX_OUTPUT_EXTENSIONS = {".pdf", ".dvi", ".ps"}
LATEX_PROTECTED_EXTENSIONS = {
    ".tex", ".pdf", ".bib", ".sty", ".cls", ".dtx", ".ins", ".png", ".jpg",
    ".jpeg", ".gif", ".svg", ".eps", ".ps", ".txt", ".md", ".py", ".sh", ".bat"
}


class LaTeXPatterns:
    """Common LaTeX regex patterns for validation."""
    
    def __init__(self):
        # Document structure patterns
        self.document_class = re.compile(r"\\documentclass(?:\[[^\]]*\])?\{[^}]+\}")
        self.begin_document = re.compile(r"\\begin\{document\}")
        self.end_document = re.compile(r"\\end\{document\}")
        
        # Environment patterns
        self.environment_begin = re.compile(r"\\begin\{([^}]+)\}")
        self.environment_end = re.compile(r"\\end\{([^}]+)\}")
        
        # Math environment patterns
        self.math_environments = re.compile(r"\\begin\{(equation|align|gather|multline|split|eqnarray)\*?\}")
        
        # Package and command patterns
        self.usepackage = re.compile(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}")
        self.newcommand = re.compile(r"\\newcommand\{\\([^}]+)\}")
        
        # Citation and reference patterns
        self.citation = re.compile(r"\\cite(?:[tp]?)?\{([^}]+)\}")
        self.label = re.compile(r"\\label\{([^}]+)\}")
        self.ref = re.compile(r"\\(?:ref|pageref|eqref)\{([^}]+)\}")
        
        # Brace patterns
        self.open_brace = re.compile(r"(?<!\\)\{")
        self.close_brace = re.compile(r"(?<!\\)\}")
        
        # Common issues patterns
        self.unescaped_special = re.compile(r"(?<!\\)[&%$#_{}~^]")
        self.double_backslash = re.compile(r"\\\\")
    
    # Keep class attributes for backwards compatibility
    DOCUMENTCLASS = re.compile(r"\\documentclass(?:\[[^\]]*\])?\{[^}]+\}")
    BEGIN_DOCUMENT = re.compile(r"\\begin\{document\}")
    END_DOCUMENT = re.compile(r"\\end\{document\}")
    BEGIN_ENV = re.compile(r"\\begin\{([^}]+)\}")
    END_ENV = re.compile(r"\\end\{([^}]+)\}")
    MATH_ENVIRONMENTS = re.compile(r"\\begin\{(equation|align|gather|multline|split|eqnarray)\*?\}")
    USEPACKAGE = re.compile(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}")
    NEWCOMMAND = re.compile(r"\\newcommand\{\\([^}]+)\}")
    CITATION = re.compile(r"\\cite(?:[tp]?)?\{([^}]+)\}")
    LABEL = re.compile(r"\\label\{([^}]+)\}")
    REF = re.compile(r"\\(?:ref|pageref|eqref)\{([^}]+)\}")
    OPEN_BRACE = re.compile(r"(?<!\\)\{")
    CLOSE_BRACE = re.compile(r"(?<!\\)\}")
    UNESCAPED_SPECIAL = re.compile(r"(?<!\\)[&%$#_{}~^]")
    DOUBLE_BACKSLASH = re.compile(r"\\\\")


def validate_file_path(
    file_path: Optional[str],
    must_exist: bool = True,
    must_be_readable: bool = True,
    allowed_extensions: Optional[Set[str]] = None,
    require_file: bool = True
) -> Path:
    """
    Validate a file path with comprehensive checks.
    
    Args:
        file_path: Path to validate
        must_exist: If True, path must exist
        must_be_readable: If True, path must be readable
        allowed_extensions: Set of allowed file extensions
        require_file: If True, path must be a file (not directory)
    
    Returns:
        The validated file path as Path object
        
    Raises:
        FileValidationError: If validation fails
    """
    if file_path is None:
        raise FileValidationError("File path cannot be None")
    
    if not file_path or not file_path.strip():
        raise FileValidationError("File path cannot be empty")
    
    path = Path(file_path)
    file_exists = path.exists()
    
    # Check existence requirement
    if must_exist and not file_exists:
        raise FileValidationError(f"File not found: {file_path}")
    
    # Check if it's a file when required
    if require_file and file_exists and not path.is_file():
        raise FileValidationError("Path is a directory, not a file")
    
    # Check readability requirement
    if must_be_readable and file_exists:
        try:
            if path.is_file():
                is_readable = path.stat().st_mode & 0o444
                if not is_readable:
                    raise FileValidationError(f"File is not readable: {file_path}")
            elif path.is_dir() and not require_file:
                # For directories, check if we can list contents
                try:
                    list(path.iterdir())
                except PermissionError:
                    raise FileValidationError(f"Directory is not readable: {file_path}")
        except Exception:
            raise FileValidationError(f"Cannot access path: {file_path}")
    
    # Check extension requirement
    if allowed_extensions and path.suffix.lower() not in allowed_extensions:
        raise FileValidationError(f"File extension '{path.suffix}' not allowed. Allowed: {sorted(allowed_extensions)}")
    
    return path


def validate_file_path_detailed(
    file_path: Optional[str],
    must_exist: bool = True,
    must_be_readable: bool = True,
    allowed_extensions: Optional[Set[str]] = None
) -> FileValidationResult:
    """
    Validate a file path with comprehensive checks, returning detailed result.
    
    Args:
        file_path: Path to validate
        must_exist: If True, file must exist
        must_be_readable: If True, file must be readable
        allowed_extensions: Set of allowed file extensions
    
    Returns:
        FileValidationResult with validation details
    """
    if file_path is None:
        return FileValidationResult(
            is_valid=False,
            error_message="File path cannot be None",
            file_path=None,
            file_exists=False,
            is_readable=False,
            file_size_bytes=None
        )
    
    if not file_path or not file_path.strip():
        return FileValidationResult(
            is_valid=False,
            error_message="File path cannot be empty",
            file_path=file_path,
            file_exists=False,
            is_readable=False,
            file_size_bytes=None
        )
    
    path = Path(file_path)
    file_exists = path.exists()
    is_readable = False
    file_size = None
    
    if file_exists:
        try:
            is_readable = path.is_file() and os.access(path, os.R_OK)
            file_size = path.stat().st_size
        except Exception:
            is_readable = False
    
    # Check existence requirement
    if must_exist and not file_exists:
        return FileValidationResult(
            is_valid=False,
            error_message=f"File not found: {file_path}",
            file_path=file_path,
            file_exists=file_exists,
            is_readable=is_readable,
            file_size_bytes=file_size
        )
    
    # Check readability requirement
    if must_be_readable and file_exists and not is_readable:
        return FileValidationResult(
            is_valid=False,
            error_message=f"File is not readable: {file_path}",
            file_path=file_path,
            file_exists=file_exists,
            is_readable=is_readable,
            file_size_bytes=file_size
        )
    
    # Check extension requirement
    if allowed_extensions and path.suffix.lower() not in allowed_extensions:
        return FileValidationResult(
            is_valid=False,
            error_message=f"File extension '{path.suffix}' not allowed. Allowed: {sorted(allowed_extensions)}",
            file_path=file_path,
            file_exists=file_exists,
            is_readable=is_readable,
            file_size_bytes=file_size
        )
    
    return FileValidationResult(
        is_valid=True,
        error_message=None,
        file_path=file_path,
        file_exists=file_exists,
        is_readable=is_readable,
        file_size_bytes=file_size
    )


def is_latex_file(file_path: Union[str, Path]) -> bool:
    """Check if a file is a LaTeX source file."""
    if isinstance(file_path, str):
        file_path = Path(file_path)
    return file_path.suffix.lower() in LATEX_SOURCE_EXTENSIONS


def is_auxiliary_file(file_path: Union[str, Path]) -> bool:
    """Check if a file is a LaTeX auxiliary file."""
    if isinstance(file_path, str):
        file_path = Path(file_path)
    return file_path.suffix.lower() in LATEX_AUXILIARY_EXTENSIONS


def is_output_file(file_path: Union[str, Path]) -> bool:
    """Check if a file is a LaTeX output file."""
    if isinstance(file_path, str):
        file_path = Path(file_path)
    return file_path.suffix.lower() in LATEX_OUTPUT_EXTENSIONS


def is_protected_file(file_path: Union[str, Path]) -> bool:
    """Check if a file should be protected from cleanup."""
    if isinstance(file_path, str):
        file_path = Path(file_path)
    return file_path.suffix.lower() in LATEX_PROTECTED_EXTENSIONS


class TimingContext:
    """Context manager for measuring execution time."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def elapsed_seconds(self) -> Optional[float]:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return None
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time


@contextmanager
def timing_context() -> Generator[TimingContext, None, None]:
    """Context manager for measuring execution time (legacy function version)."""
    timer = TimingContext()
    timer.start_time = time.time()
    try:
        yield timer
    finally:
        timer.end_time = time.time()


def measure_execution_time(func):
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Check if result is a dataclass with timing fields
            if hasattr(result, '__dict__'):
                if hasattr(result, 'execution_time_seconds'):
                    result.execution_time_seconds = execution_time
                    return result
                elif hasattr(result, 'compilation_time_seconds'):
                    result.compilation_time_seconds = execution_time
                    return result
                elif hasattr(result, 'validation_time_seconds'):
                    result.validation_time_seconds = execution_time
                    return result
                elif hasattr(result, 'extraction_time_seconds'):
                    result.extraction_time_seconds = execution_time
                    return result
                elif hasattr(result, 'cleanup_time_seconds'):
                    result.cleanup_time_seconds = execution_time
                    return result
            
            # For regular functions, return tuple of (result, execution_time)
            return result, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            # Re-raise the exception, timing info is lost but that's expected for errors
            raise e
    return wrapper


def format_validation_error(error_message: str, file_path: Optional[str] = None, line_number: Optional[int] = None) -> str:
    """Format a LaTeX validation error message."""
    if file_path and line_number is not None:
        return f"{error_message} in {file_path} at line {line_number}"
    elif file_path:
        return f"{error_message} in {file_path}"
    else:
        return error_message


def format_compilation_error(return_code: int, stderr: Optional[str] = None, context: Optional[str] = None) -> str:
    """Format a LaTeX compilation error message."""
    formatted = f"LaTeX compilation failed with return code {return_code}"
    if context:
        formatted = f"{context} {formatted}"
    if stderr:
        formatted += f"\nError output: {stderr}"
    return formatted


def format_operation_error(operation: str, error: str, file_path: Optional[str] = None) -> str:
    """Format a general operation error message."""
    if file_path:
        return f"{operation} failed for {file_path}: {error}"
    else:
        return f"{operation} failed: {error}"


def check_brace_balance(content: str) -> bool:
    """Check if braces are balanced in LaTeX content."""
    open_braces = []
    
    for match in LaTeXPatterns.OPEN_BRACE.finditer(content):
        open_braces.append(match.start())
    
    for match in LaTeXPatterns.CLOSE_BRACE.finditer(content):
        if open_braces:
            open_braces.pop()
        else:
            return False  # Unmatched closing brace
    
    return len(open_braces) == 0  # True if no unmatched opening braces


def find_unmatched_environments(content: str) -> List[str]:
    """Find unmatched LaTeX environments."""
    begin_stack = []
    unmatched = []
    
    # Find all begin environments
    for match in LaTeXPatterns.BEGIN_ENV.finditer(content):
        env_name = match.group(1)
        begin_stack.append(env_name)
    
    # Find all end environments
    for match in LaTeXPatterns.END_ENV.finditer(content):
        env_name = match.group(1)
        
        # Try to match with most recent begin
        if begin_stack:
            last_begin_name = begin_stack[-1]
            if last_begin_name == env_name:
                begin_stack.pop()  # Matched pair
            else:
                # Mismatched environment
                unmatched.append(env_name)
        else:
            # End without begin
            unmatched.append(env_name)
    
    # Remaining items in begin_stack are unmatched
    unmatched.extend(begin_stack)
    
    return unmatched


def resolve_output_path(input_path: Path, output_dir: Optional[Union[str, Path]]) -> Path:
    """Resolve output directory path for compilation."""
    if output_dir is None:
        return input_path.parent
    
    return Path(output_dir)


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_stem_files(file_path: Path) -> List[Path]:
    """Get all files with the same stem (different extensions)."""
    stem = file_path.stem
    parent = file_path.parent
    
    # Get all files in the directory with matching stem
    matching_files = []
    if parent.exists():
        for file in parent.glob(f"{stem}.*"):
            if file.is_file():
                matching_files.append(file)
    
    return sorted(matching_files)


def read_latex_file(file_path: Union[str, Path]) -> str:
    """Read a LaTeX file with proper encoding handling."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileValidationError(f"File not found: {file_path}")
    
    if not is_latex_file(path):
        raise FileValidationError(f"Not a LaTeX file: {file_path}")
    
    try:
        return read_file_with_encoding(path, ['utf-8', 'latin-1', 'cp1252'])
    except LaTeXUtilsError as e:
        raise FileValidationError(f"Failed to read LaTeX file {file_path}: {e}")


def read_file_with_encoding(file_path: Union[str, Path], encodings: Optional[List[str]] = None) -> str:
    """Read a file trying multiple encodings."""
    path = Path(file_path)
    
    if encodings is None:
        encodings = ['utf-8', 'latin-1', 'cp1252']
    
    # Try to read with different encodings
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            raise LaTeXUtilsError(f"File not found: {file_path}")
        except PermissionError as e:
            raise LaTeXUtilsError(f"Permission denied reading {file_path}: {e}")
    
    raise LaTeXUtilsError(f"Could not read {file_path} with any of the provided encodings: {encodings}")


def extract_packages(content: str) -> List[str]:
    """Extract package names from LaTeX content."""
    packages = []
    for match in LaTeXPatterns.USEPACKAGE.finditer(content):
        package_list = match.group(1)
        # Handle multiple packages in one usepackage command
        packages.extend([pkg.strip() for pkg in package_list.split(',')])
    return packages


def extract_citations(content: str) -> List[str]:
    """Extract citation keys from LaTeX content."""
    citations = []
    for match in LaTeXPatterns.CITATION.finditer(content):
        citation_list = match.group(1)
        # Handle multiple citations in one cite command
        citations.extend([cite.strip() for cite in citation_list.split(',')])
    return citations


def extract_labels(content: str) -> List[str]:
    """Extract label names from LaTeX content."""
    return [match.group(1) for match in LaTeXPatterns.LABEL.finditer(content)]


def extract_references(content: str) -> List[str]:
    """Extract reference names from LaTeX content."""
    return [match.group(1) for match in LaTeXPatterns.REF.finditer(content)]


def has_document_structure(content: str) -> Tuple[bool, List[str]]:
    """Check if LaTeX content has proper document structure."""
    issues = []
    
    # Check for documentclass
    if not LaTeXPatterns.DOCUMENTCLASS.search(content):
        issues.append("Missing \\documentclass command")
    
    # Check for begin{document}
    if not LaTeXPatterns.BEGIN_DOCUMENT.search(content):
        issues.append("Missing \\begin{document}")
    
    # Check for end{document}
    if not LaTeXPatterns.END_DOCUMENT.search(content):
        issues.append("Missing \\end{document}")
    
    return len(issues) == 0, issues


def has_document_class(content: str) -> bool:
    """Check if LaTeX content has documentclass command."""
    return LaTeXPatterns.DOCUMENTCLASS.search(content) is not None


def has_begin_document(content: str) -> bool:
    """Check if LaTeX content has begin{document}."""
    return LaTeXPatterns.BEGIN_DOCUMENT.search(content) is not None


def has_end_document(content: str) -> bool:
    """Check if LaTeX content has end{document}."""
    return LaTeXPatterns.END_DOCUMENT.search(content) is not None


def get_latex_file_extensions() -> Set[str]:
    """Get set of LaTeX source file extensions."""
    return LATEX_SOURCE_EXTENSIONS.copy()


def get_auxiliary_file_extensions() -> Set[str]:
    """Get set of LaTeX auxiliary file extensions."""
    return LATEX_AUXILIARY_EXTENSIONS.copy()


def get_output_file_extensions() -> Set[str]:
    """Get set of LaTeX output file extensions."""
    return LATEX_OUTPUT_EXTENSIONS.copy()


def get_protected_file_extensions() -> Set[str]:
    """Get set of protected file extensions."""
    return LATEX_PROTECTED_EXTENSIONS.copy()