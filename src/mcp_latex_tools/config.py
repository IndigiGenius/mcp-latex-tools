"""Configuration system for mcp-latex-tools.

Loads project-level defaults from a `.mcp-latex-tools.toml` file.
Override precedence: MCP call args > config file > hardcoded defaults.
"""

import logging
import tomllib
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic import BaseModel

logger = logging.getLogger(__name__)

CONFIG_FILENAME = ".mcp-latex-tools.toml"


class CompilationConfig(BaseModel):
    """Defaults for the compile_latex tool."""

    engine: str = "pdflatex"
    passes: Union[int, Literal["auto"]] = 1
    timeout: int = 30


class ValidationConfig(BaseModel):
    """Defaults for the validate_latex tool."""

    quick: bool = False
    strict: bool = False


class CleanupConfig(BaseModel):
    """Defaults for the cleanup tool."""

    dry_run: bool = False
    recursive: bool = False
    create_backup: bool = False
    extensions: Optional[list[str]] = None


class PdfInfoConfig(BaseModel):
    """Defaults for the pdf_info tool."""

    include_text: bool = False


class DetectPackagesConfig(BaseModel):
    """Defaults for the detect_packages tool."""

    check_installed: bool = True


class ToolConfig(BaseModel):
    """Root configuration for mcp-latex-tools."""

    compilation: CompilationConfig = CompilationConfig()
    validation: ValidationConfig = ValidationConfig()
    cleanup: CleanupConfig = CleanupConfig()
    pdf_info: PdfInfoConfig = PdfInfoConfig()
    detect_packages: DetectPackagesConfig = DetectPackagesConfig()


def find_config_file(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Search for .mcp-latex-tools.toml, walking up from start_dir to root.

    Args:
        start_dir: Directory to start searching from. Defaults to cwd.

    Returns:
        Path to the config file if found, None otherwise.
    """
    current = (start_dir or Path.cwd()).resolve()
    while True:
        candidate = current / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_config(config_path: Optional[Path] = None) -> ToolConfig:
    """Load configuration from a TOML file.

    Args:
        config_path: Explicit path to config file. If None, searches
            for .mcp-latex-tools.toml walking up from cwd.

    Returns:
        ToolConfig instance. Returns default config if no file found
        or if file cannot be parsed.
    """
    if config_path is None:
        config_path = find_config_file()

    if config_path is None or not config_path.is_file():
        return ToolConfig()

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        return ToolConfig.model_validate(data)
    except Exception as e:
        logger.warning("Failed to load config from %s: %s", config_path, e)
        return ToolConfig()
