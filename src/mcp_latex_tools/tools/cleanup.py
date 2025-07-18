"""LaTeX auxiliary file cleanup tool for removing build artifacts."""

import shutil
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set


class CleanupError(Exception):
    """Exception raised for cleanup errors."""

    pass


@dataclass
class CleanupResult:
    """Result of LaTeX cleanup operation."""

    success: bool
    error_message: Optional[str]
    tex_file_path: Optional[str]
    directory_path: Optional[str]
    cleaned_files_count: int
    cleaned_files: List[str]
    would_clean_files: List[str]
    dry_run: bool
    recursive: bool
    backup_created: bool
    backup_directory: Optional[str]
    cleanup_time_seconds: Optional[float]


# Default auxiliary file extensions to clean
DEFAULT_CLEANUP_EXTENSIONS = {
    ".aux",      # LaTeX auxiliary files
    ".log",      # LaTeX log files
    ".out",      # Hyperref output files
    ".fls",      # LaTeX file list
    ".fdb_latexmk",  # Latexmk database
    ".toc",      # Table of contents
    ".lof",      # List of figures
    ".lot",      # List of tables
    ".bbl",      # Bibliography
    ".blg",      # Bibliography log
    ".nav",      # Beamer navigation
    ".snm",      # Beamer slide notes
    ".vrb",      # Beamer verbatim
    ".idx",      # Index files
    ".ilg",      # Index log
    ".ind",      # Index
    ".glo",      # Glossary
    ".gls",      # Glossary sorted
    ".glg",      # Glossary log
    ".synctex.gz",  # SyncTeX files
    ".figlist",  # Figure list
    ".fpl",      # Figure page list
    ".makefile", # Auto-generated makefiles
    ".run.xml",  # Biber run files
}

# File extensions that should be protected from cleanup
PROTECTED_EXTENSIONS = {
    ".tex",      # LaTeX source files
    ".pdf",      # Output files
    ".bib",      # Bibliography files
    ".sty",      # Style files
    ".cls",      # Class files
    ".dtx",      # Documented LaTeX source
    ".ins",      # Installation files
    ".png",      # Images
    ".jpg",      # Images
    ".jpeg",     # Images
    ".gif",      # Images
    ".svg",      # Images
    ".eps",      # Images
    ".ps",       # PostScript
    ".txt",      # Text files
    ".md",       # Markdown files
    ".py",       # Python files
    ".sh",       # Shell scripts
    ".bat",      # Batch files
}


def clean_latex(
    path: Optional[str],
    extensions: Optional[List[str]] = None,
    dry_run: bool = False,
    recursive: bool = False,
    create_backup: bool = False,
) -> CleanupResult:
    """
    Clean LaTeX auxiliary files from a file or directory.

    Args:
        path: Path to .tex file or directory to clean
        extensions: List of file extensions to clean (defaults to common auxiliary files)
        dry_run: If True, show what would be cleaned without removing files
        recursive: If True, clean subdirectories recursively
        create_backup: If True, create backup of files before deletion

    Returns:
        CleanupResult containing cleanup status and information

    Raises:
        CleanupError: If path is invalid or cleanup fails
    """
    start_time = time.time()

    # Validate input
    if path is None:
        raise CleanupError("Path cannot be None")
    if not path:
        raise CleanupError("Path cannot be empty")

    path_obj = Path(path)
    if not path_obj.exists():
        raise CleanupError(f"Path not found: {path}")

    # Use default extensions if not provided
    if extensions is None:
        cleanup_extensions = DEFAULT_CLEANUP_EXTENSIONS
    else:
        cleanup_extensions = set(extensions)

    # Initialize result
    result = CleanupResult(
        success=False,
        error_message=None,
        tex_file_path=None,
        directory_path=None,
        cleaned_files_count=0,
        cleaned_files=[],
        would_clean_files=[],
        dry_run=dry_run,
        recursive=recursive,
        backup_created=False,
        backup_directory=None,
        cleanup_time_seconds=None,
    )

    # Create backup directory if requested
    backup_dir = None
    if create_backup and not dry_run:
        try:
            backup_dir = _create_backup_directory(path_obj)
            result.backup_directory = str(backup_dir)
        except Exception as e:
            # If backup creation fails, continue without backup
            result.error_message = f"Warning: Backup creation failed: {e}. Continuing without backup."
            backup_dir = None

    try:
        if path_obj.is_file():
            # Clean auxiliary files for a specific .tex file
            result.tex_file_path = str(path_obj)
            result.directory_path = str(path_obj.parent)
            
            if path_obj.suffix == ".tex":
                # Clean auxiliary files with the same stem
                _clean_tex_file_auxiliaries(
                    path_obj, cleanup_extensions, result, backup_dir
                )
            else:
                # Single file cleanup (if it matches cleanup extensions)
                _clean_single_file(
                    path_obj, cleanup_extensions, result, backup_dir
                )
        else:
            # Clean auxiliary files in directory
            result.directory_path = str(path_obj)
            _clean_directory_auxiliaries(
                path_obj, cleanup_extensions, result, backup_dir, recursive
            )

        # Mark backup as created if files were backed up
        if backup_dir and result.cleaned_files:
            result.backup_created = True

        result.success = True

    except Exception as e:
        result.error_message = f"Cleanup failed: {e}"

    result.cleanup_time_seconds = time.time() - start_time
    return result


def _create_backup_directory(path: Path) -> Path:
    """Create a backup directory for the cleanup operation."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if path.is_file():
        backup_name = f"backup_{path.stem}_{timestamp}"
        backup_dir = path.parent / backup_name
    else:
        backup_name = f"backup_{path.name}_{timestamp}"
        backup_dir = path.parent / backup_name
    
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def _clean_tex_file_auxiliaries(
    tex_file: Path,
    cleanup_extensions: Set[str],
    result: CleanupResult,
    backup_dir: Optional[Path],
) -> None:
    """Clean auxiliary files for a specific .tex file."""
    tex_stem = tex_file.stem
    tex_dir = tex_file.parent
    
    # Find all files with the same stem and auxiliary extensions
    for ext in cleanup_extensions:
        aux_file = tex_dir / f"{tex_stem}{ext}"
        if aux_file.exists() and aux_file.is_file():
            _process_file_for_cleanup(aux_file, result, backup_dir)


def _clean_single_file(
    file_path: Path,
    cleanup_extensions: Set[str],
    result: CleanupResult,
    backup_dir: Optional[Path],
) -> None:
    """Clean a single file if it matches cleanup extensions."""
    if file_path.suffix in cleanup_extensions:
        _process_file_for_cleanup(file_path, result, backup_dir)


def _clean_directory_auxiliaries(
    directory: Path,
    cleanup_extensions: Set[str],
    result: CleanupResult,
    backup_dir: Optional[Path],
    recursive: bool,
) -> None:
    """Clean auxiliary files in a directory."""
    # Use find_auxiliary_files to get list of files to clean
    auxiliary_files = find_auxiliary_files(
        str(directory), 
        extensions=list(cleanup_extensions), 
        recursive=recursive
    )
    
    # Process each auxiliary file
    for file_path in auxiliary_files:
        # file_path is already a Path object from find_auxiliary_files
        _process_file_for_cleanup(file_path, result, backup_dir)


def _process_file_for_cleanup(
    file_path: Path,
    result: CleanupResult,
    backup_dir: Optional[Path],
) -> None:
    """Process a single file for cleanup (backup and/or remove)."""
    file_str = str(file_path)
    
    if result.dry_run:
        # Dry run - just record what would be cleaned
        result.would_clean_files.append(file_str)
    else:
        try:
            # Create backup if requested
            if backup_dir:
                backup_file = backup_dir / file_path.name
                shutil.copy2(file_path, backup_file)
            
            # Remove the file
            file_path.unlink()
            
            # Record successful cleanup
            result.cleaned_files.append(file_str)
            result.cleaned_files_count += 1
            
        except Exception:
            # If we can't remove a file, record it but don't fail the whole operation
            # This allows partial cleanup to succeed
            pass


def get_default_cleanup_extensions() -> Set[str]:
    """Get the default set of file extensions that will be cleaned."""
    return DEFAULT_CLEANUP_EXTENSIONS.copy()


def get_protected_extensions() -> Set[str]:
    """Get the set of file extensions that are protected from cleanup."""
    return PROTECTED_EXTENSIONS.copy()


def is_auxiliary_file(file_path: Path) -> bool:
    """Check if a file is considered an auxiliary file that can be cleaned."""
    return (
        file_path.suffix in DEFAULT_CLEANUP_EXTENSIONS
        and file_path.suffix not in PROTECTED_EXTENSIONS
    )


def find_auxiliary_files(
    directory: Path,
    recursive: bool = False,
    extensions: Optional[Set[str]] = None,
) -> List[Path]:
    """
    Find all auxiliary files in a directory.

    Args:
        directory: Directory to search
        recursive: If True, search subdirectories
        extensions: Set of extensions to look for (defaults to standard auxiliary files)

    Returns:
        List of Path objects for auxiliary files found
    """
    if extensions is None:
        extensions = DEFAULT_CLEANUP_EXTENSIONS
    
    auxiliary_files = []
    
    # Convert string path to Path object if needed
    if isinstance(directory, str):
        directory = Path(directory)
    
    # Get pattern based on recursive flag
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    # Find all files matching cleanup extensions
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            if (
                file_path.suffix in extensions
                and file_path.suffix not in PROTECTED_EXTENSIONS
            ):
                auxiliary_files.append(file_path)
    
    return auxiliary_files