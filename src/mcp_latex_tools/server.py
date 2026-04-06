"""MCP server for LaTeX compilation and PDF tools."""

import asyncio
import json
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    Prompt,
    PromptArgument,
    PromptMessage,
    GetPromptResult,
    AnyUrl,
)

from mcp_latex_tools.tools.compile import compile_latex, CompilationError
from mcp_latex_tools.tools.validate import validate_latex, ValidationError
from mcp_latex_tools.tools.pdf_info import extract_pdf_info, PDFInfoError
from mcp_latex_tools.tools.cleanup import (
    clean_latex,
    CleanupError,
    DEFAULT_CLEANUP_EXTENSIONS,
    PROTECTED_EXTENSIONS,
)
from mcp_latex_tools.tools.detect_packages import (
    detect_packages,
    PackageDetectionError,
)
from mcp_latex_tools.config import load_config
from mcp_latex_tools.utils.log_parser import get_error_summary

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

server: Server = Server("mcp-latex-tools")
_config = load_config()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available LaTeX tools."""
    return [
        Tool(
            name="compile_latex",
            description="Compile .tex to PDF. Supports pdflatex/xelatex/lualatex/latexmk engines and multi-pass compilation with automatic bibliography (bibtex/biber) support.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tex_path": {
                        "type": "string",
                        "description": "Path to the .tex file to compile",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory for output files (default: same as input)",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Max compilation time in seconds",
                        "default": 30,
                        "minimum": 5,
                        "maximum": 300,
                    },
                    "engine": {
                        "type": "string",
                        "description": "LaTeX engine to use",
                        "enum": ["pdflatex", "xelatex", "lualatex", "latexmk"],
                        "default": "pdflatex",
                    },
                    "passes": {
                        "description": "Number of compilation passes (1-3) or 'auto' to detect from log. latexmk handles passes automatically.",
                        "oneOf": [
                            {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 3,
                            },
                            {
                                "type": "string",
                                "enum": ["auto"],
                            },
                        ],
                        "default": 1,
                    },
                },
                "required": ["tex_path"],
            },
        ),
        Tool(
            name="validate_latex",
            description="Check LaTeX syntax without compiling. Modes: quick, default, strict. Returns errors/warnings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the .tex file to validate",
                    },
                    "quick": {
                        "type": "boolean",
                        "description": "Quick mode: structure only",
                        "default": False,
                    },
                    "strict": {
                        "type": "boolean",
                        "description": "Strict mode: include style checks",
                        "default": False,
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="pdf_info",
            description="Extract PDF metadata: pages, dimensions, title, author, dates. Optional text extraction.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the PDF file to analyze",
                    },
                    "include_text": {
                        "type": "boolean",
                        "description": "Extract text content from pages",
                        "default": False,
                    },
                    "password": {
                        "type": "string",
                        "description": "Password for encrypted PDFs",
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="cleanup",
            description="Remove LaTeX auxiliary files (.aux, .log, etc.). Supports dry_run, recursive, backup. Never deletes .tex/.pdf/.bib.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to .tex file or directory to clean",
                    },
                    "extensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": 'Extensions with leading dot (e.g., [".aux", ".log"]). Default: .aux, .log, .out, etc.',
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Preview what would be deleted without deleting",
                        "default": False,
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Clean subdirectories recursively",
                        "default": False,
                    },
                    "create_backup": {
                        "type": "boolean",
                        "description": "Create backup before deleting",
                        "default": False,
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="detect_packages",
            description="Detect LaTeX packages required by a .tex file. Checks if each package is installed via kpsewhich and suggests tlmgr install commands for missing ones.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the .tex file to analyze",
                    },
                    "check_installed": {
                        "type": "boolean",
                        "description": "Check if packages are installed via kpsewhich (default: true). Set false for parse-only mode.",
                        "default": True,
                    },
                },
                "required": ["file_path"],
            },
        ),
    ]


# =============================================================================
# MCP Resources
# =============================================================================


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available LaTeX resources."""
    return [
        Resource(
            uri=AnyUrl("latex://config/cleanup-extensions"),
            name="Cleanup Extensions",
            description="File extensions removed by the cleanup tool",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("latex://config/protected-extensions"),
            name="Protected Extensions",
            description="File extensions protected from cleanup (never deleted)",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("latex://help/workflow"),
            name="Workflow Guide",
            description="Recommended workflow for LaTeX document compilation",
            mimeType="text/markdown",
        ),
    ]


@server.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read resource content."""
    uri_str = str(uri)
    if uri_str == "latex://config/cleanup-extensions":
        return json.dumps(
            {
                "extensions": sorted(DEFAULT_CLEANUP_EXTENSIONS),
                "description": "File extensions removed by the cleanup tool",
                "count": len(DEFAULT_CLEANUP_EXTENSIONS),
            },
            indent=2,
        )

    elif uri_str == "latex://config/protected-extensions":
        return json.dumps(
            {
                "extensions": sorted(PROTECTED_EXTENSIONS),
                "description": "File extensions protected from cleanup (never deleted)",
                "count": len(PROTECTED_EXTENSIONS),
            },
            indent=2,
        )

    elif uri_str == "latex://help/workflow":
        return """# LaTeX Compilation Workflow

1. **Validate**: `validate_latex` — catch syntax errors fast
2. **Compile**: `compile_latex` — generate PDF
3. **Verify**: `pdf_info` — check page count and metadata
4. **Cleanup**: `cleanup` with `dry_run=true` first, then without

## Error Recovery
If compilation fails, run `validate_latex` to identify syntax errors.
If validation passes but compilation fails, run `detect_packages` to check for missing packages, or increase timeout.
"""

    raise ValueError(f"Unknown resource: {uri_str}")


# =============================================================================
# MCP Prompts
# =============================================================================


@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available LaTeX workflow prompts."""
    return [
        Prompt(
            name="compile-and-verify",
            description="Complete workflow: validate, compile, verify PDF, and clean up",
            arguments=[
                PromptArgument(
                    name="tex_path",
                    description="Path to the .tex file to compile",
                    required=True,
                ),
                PromptArgument(
                    name="cleanup",
                    description="Whether to clean auxiliary files after (true/false)",
                    required=False,
                ),
            ],
        ),
        Prompt(
            name="diagnose-compilation-error",
            description="Diagnose why a LaTeX document fails to compile",
            arguments=[
                PromptArgument(
                    name="tex_path",
                    description="Path to the .tex file that failed to compile",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="prepare-fresh-build",
            description="Clean all auxiliary files and recompile from scratch",
            arguments=[
                PromptArgument(
                    name="tex_path",
                    description="Path to the .tex file to rebuild",
                    required=True,
                ),
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None) -> GetPromptResult:
    """Get prompt messages for a specific workflow."""
    args = arguments or {}

    if name == "compile-and-verify":
        tex_path = args.get("tex_path", "<tex_path>")
        do_cleanup = str(args.get("cleanup", "true")).lower() == "true"
        cleanup_step = (
            "\n4. **CLEANUP**: Run `cleanup` on the .tex file path to remove auxiliary files."
            if do_cleanup
            else "\n4. **SKIP CLEANUP**: User requested no cleanup."
        )
        return GetPromptResult(
            description=f"Complete compilation workflow for {tex_path}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Execute a complete LaTeX compilation workflow for: {tex_path}

Follow these steps in order:

1. **VALIDATE**: Run `validate_latex` on "{tex_path}" to check for syntax errors.
   - If errors found, report them and stop.
   - If only warnings, continue but note them.

2. **COMPILE**: Run `compile_latex` on "{tex_path}".
   - If compilation fails, report the error summary.
   - If successful, proceed to verification.

3. **VERIFY**: Run `pdf_info` on the generated PDF.
   - Report page count and file size.
   - Confirm the PDF was created successfully.
{cleanup_step}

Report results at each step. Summarize the final outcome.""",
                    ),
                ),
            ],
        )

    elif name == "diagnose-compilation-error":
        tex_path = args.get("tex_path", "<tex_path>")
        return GetPromptResult(
            description=f"Diagnose compilation errors for {tex_path}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Diagnose compilation issues for: {tex_path}

Follow this diagnostic procedure:

1. **VALIDATE (Quick)**: Run `validate_latex` with `quick=true`.
2. **VALIDATE (Full)**: If quick passes, run `validate_latex` with default settings.
3. **VALIDATE (Strict)**: If full passes, run `validate_latex` with `strict=true`.
4. **ATTEMPT COMPILATION**: If validation passes, try `compile_latex` with `timeout=60`.
5. **DIAGNOSIS**: Based on all results, provide root cause, line numbers, and suggested fixes.""",
                    ),
                ),
            ],
        )

    elif name == "prepare-fresh-build":
        tex_path = args.get("tex_path", "<tex_path>")
        return GetPromptResult(
            description=f"Fresh build workflow for {tex_path}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Perform a fresh build for: {tex_path}

Steps:

1. **PREVIEW CLEANUP**: Run `cleanup` with `dry_run=true` to see what would be removed.
2. **CLEAN**: Run `cleanup` with `create_backup=true` to safely remove auxiliary files.
3. **VALIDATE**: Run `validate_latex` to ensure the source file is ready.
4. **COMPILE**: Run `compile_latex` to rebuild from scratch.
5. **VERIFY**: Run `pdf_info` on the new PDF.""",
                    ),
                ),
            ],
        )

    raise ValueError(f"Unknown prompt: {name}")


# =============================================================================
# Tool Call Handler
# =============================================================================


def _text_result(text: str) -> list[TextContent]:
    """Return a single TextContent list."""
    return [TextContent(type="text", text=text)]


@server.call_tool()
async def call_tool(tool_name: str, arguments: dict) -> list[TextContent]:  # type: ignore[override]
    """Handle tool calls."""
    try:
        if tool_name == "compile_latex":
            return await _handle_compile(arguments)
        elif tool_name == "validate_latex":
            return await _handle_validate(arguments)
        elif tool_name == "pdf_info":
            return await _handle_pdf_info(arguments)
        elif tool_name == "cleanup":
            return await _handle_cleanup(arguments)
        elif tool_name == "detect_packages":
            return await _handle_detect_packages(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    except Exception as e:
        logger.error("Error in tool call %s: %s", tool_name, e)
        return _text_result(f"Error: {e}")


def _get_path_arg(args: dict, *keys: str) -> str | None:
    """Get path argument, accepting common aliases."""
    for key in keys:
        if val := args.get(key):
            return val
    return None


async def _handle_compile(args: dict) -> list[TextContent]:
    tex_path = _get_path_arg(args, "tex_path", "file_path", "path")
    if not tex_path:
        return _text_result(
            "Error: tex_path is required. Pass the path to the .tex file."
        )

    engine = args.get("engine", _config.compilation.engine)
    passes = args.get("passes", _config.compilation.passes)

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            lambda: compile_latex(
                tex_path,
                output_dir=args.get("output_dir"),
                timeout=args.get("timeout", _config.compilation.timeout),
                engine=engine,
                passes=passes,
            ),
        )

        if result.success:
            text = f"Compilation successful\nOutput: {result.output_path}"
            text += f"\nEngine: {result.engine}"
            if result.passes_run and result.passes_run > 1:
                text += f"\nPasses: {result.passes_run}"
            if result.compilation_time_seconds:
                text += f"\nCompilation time: {result.compilation_time_seconds:.2f}s"
        else:
            text = "Compilation failed"
            if result.error_message:
                text += f"\nError: {result.error_message}"
            if result.engine:
                text += f"\nEngine: {result.engine}"
            if result.compilation_time_seconds:
                text += f"\nCompilation time: {result.compilation_time_seconds:.2f}s"
            if result.log_content:
                text += f"\n{get_error_summary(result.log_content)}"
        return _text_result(text)

    except CompilationError as e:
        return _text_result(f"Compilation error: {e}")


async def _handle_validate(args: dict) -> list[TextContent]:
    file_path = _get_path_arg(args, "file_path", "tex_path", "path")
    if not file_path:
        return _text_result(
            "Error: file_path is required. Pass the path to the .tex file."
        )

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            validate_latex,
            file_path,
            args.get("quick", _config.validation.quick),
            args.get("strict", _config.validation.strict),
        )

        if result.is_valid:
            text = "Valid LaTeX syntax\nNo errors found"
            if result.warnings:
                text += f"\nWarnings ({len(result.warnings)}):"
                for w in result.warnings:
                    text += f"\n  - {w}"
        else:
            text = f"Invalid LaTeX syntax\nErrors found ({len(result.errors)}):"
            for e in result.errors:
                text += f"\n  - {e}"
            if result.warnings:
                text += f"\nWarnings ({len(result.warnings)}):"
                for w in result.warnings:
                    text += f"\n  - {w}"

        if result.validation_time_seconds:
            text += f"\nValidation time: {result.validation_time_seconds:.3f}s"
        return _text_result(text)

    except ValidationError as e:
        return _text_result(f"Validation error: {e}")


async def _handle_pdf_info(args: dict) -> list[TextContent]:
    file_path = _get_path_arg(args, "file_path", "path", "tex_path")
    if not file_path:
        return _text_result(
            "Error: file_path is required. Pass the path to the PDF file."
        )

    include_text = args.get("include_text", _config.pdf_info.include_text)
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, extract_pdf_info, file_path, include_text, args.get("password")
        )

        if result.success:
            text = f"PDF info extracted\nFile: {result.file_path}"
            text += f"\nPages: {result.page_count}"
            text += f"\nFile size: {result.file_size_bytes:,} bytes"
            if result.pdf_version:
                text += f"\nPDF version: {result.pdf_version}"
            text += f"\nEncrypted: {'Yes' if result.is_encrypted else 'No'}"
            if result.page_dimensions:
                text += "\nDimensions:"
                for i, dims in enumerate(result.page_dimensions):
                    text += f"\n  Page {i + 1}: {dims['width']:.1f} x {dims['height']:.1f} {dims['unit']}"
            for field, label in [
                ("title", "Title"),
                ("author", "Author"),
                ("subject", "Subject"),
                ("producer", "Producer"),
                ("creator", "Creator"),
                ("creation_date", "Created"),
                ("modification_date", "Modified"),
            ]:
                val = getattr(result, field, None)
                if val:
                    text += f"\n{label}: {val}"
            if include_text and result.text_content:
                text += "\nText content:"
                for i, page_text in enumerate(result.text_content):
                    if page_text.strip():
                        text += f"\n  Page {i + 1}: {page_text[:100]}..."
                    else:
                        text += f"\n  Page {i + 1}: [No text content]"
            if result.extraction_time_seconds:
                text += f"\nExtraction time: {result.extraction_time_seconds:.3f}s"
        else:
            text = "PDF info extraction failed"
            if result.error_message:
                text += f"\nError: {result.error_message}"

        return _text_result(text)

    except PDFInfoError as e:
        return _text_result(f"PDF info error: {e}")


async def _handle_cleanup(args: dict) -> list[TextContent]:
    path = _get_path_arg(args, "path", "file_path", "tex_path")
    if not path:
        return _text_result(
            "Error: path is required. Pass the path to a .tex file or directory."
        )

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            clean_latex,
            path,
            args.get("extensions", _config.cleanup.extensions),
            args.get("dry_run", _config.cleanup.dry_run),
            args.get("recursive", _config.cleanup.recursive),
            args.get("create_backup", _config.cleanup.create_backup),
        )

        if result.success:
            if result.dry_run:
                if result.would_clean_files:
                    text = f"Cleanup dry run: would clean {len(result.would_clean_files)} files:"
                    for f in result.would_clean_files[:10]:
                        text += f"\n  - {f}"
                    if len(result.would_clean_files) > 10:
                        text += f"\n  ... and {len(result.would_clean_files) - 10} more"
                else:
                    text = "Cleanup dry run: no files to clean"
            else:
                if result.cleaned_files:
                    text = f"Cleanup completed: {result.cleaned_files_count} files cleaned:"
                    for f in result.cleaned_files[:10]:
                        text += f"\n  - {f}"
                    if len(result.cleaned_files) > 10:
                        text += f"\n  ... and {len(result.cleaned_files) - 10} more"
                else:
                    text = "Cleanup completed: no files needed cleaning"

            if result.tex_file_path:
                text += f"\nCleaned around: {result.tex_file_path}"
            elif result.directory_path:
                text += f"\nCleaned directory: {result.directory_path}"
            if result.backup_created:
                text += f"\nBackup created: {result.backup_directory}"
            if result.cleanup_time_seconds:
                text += f"\nCleanup time: {result.cleanup_time_seconds:.3f}s"
        else:
            text = "Cleanup failed"
            if result.error_message:
                text += f"\nError: {result.error_message}"

        return _text_result(text)

    except CleanupError as e:
        return _text_result(f"Cleanup error: {e}")


async def _handle_detect_packages(args: dict) -> list[TextContent]:
    file_path = _get_path_arg(args, "file_path", "tex_path", "path")
    if not file_path:
        return _text_result(
            "Error: file_path is required. Pass the path to the .tex file."
        )

    check_installed = args.get(
        "check_installed", _config.detect_packages.check_installed
    )

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            lambda: detect_packages(file_path, check_installed=check_installed),
        )

        if result.success:
            text = f"Packages detected: {len(result.packages)}"
            if result.packages:
                text += f"\nPackages: {', '.join(result.packages)}"
            if result.installed:
                text += f"\nInstalled ({len(result.installed)}): {', '.join(result.installed)}"
            if result.missing:
                text += (
                    f"\nMissing ({len(result.missing)}): {', '.join(result.missing)}"
                )
                text += "\nInstall commands:"
                for cmd in result.install_commands:
                    text += f"\n  {cmd}"
            elif check_installed and result.packages:
                text += "\nAll packages are installed"
            if result.detection_time_seconds:
                text += f"\nDetection time: {result.detection_time_seconds:.3f}s"
        else:
            text = "Package detection failed"
            if result.error_message:
                text += f"\nError: {result.error_message}"

        return _text_result(text)

    except PackageDetectionError as e:
        return _text_result(f"Package detection error: {e}")


async def main():
    """Run the MCP server."""
    logger.info("Starting MCP LaTeX Tools server")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
