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
from mcp_latex_tools.utils.log_parser import get_error_summary

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

server: Server = Server("mcp-latex-tools")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available LaTeX tools."""
    return [
        Tool(
            name="compile_latex",
            description="Compile .tex to PDF via pdflatex. Creates .pdf/.aux/.log. Returns path, timing, errors.",
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
                        "description": "Custom extensions to clean (default: .aux, .log, .out, etc.)",
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
async def read_resource(uri: str) -> str:
    """Read resource content."""
    if uri == "latex://config/cleanup-extensions":
        return json.dumps(
            {
                "extensions": sorted(DEFAULT_CLEANUP_EXTENSIONS),
                "description": "File extensions removed by the cleanup tool",
                "count": len(DEFAULT_CLEANUP_EXTENSIONS),
            },
            indent=2,
        )

    elif uri == "latex://config/protected-extensions":
        return json.dumps(
            {
                "extensions": sorted(PROTECTED_EXTENSIONS),
                "description": "File extensions protected from cleanup (never deleted)",
                "count": len(PROTECTED_EXTENSIONS),
            },
            indent=2,
        )

    elif uri == "latex://help/workflow":
        return """# LaTeX Compilation Workflow

1. **Validate**: `validate_latex` — catch syntax errors fast
2. **Compile**: `compile_latex` — generate PDF
3. **Verify**: `pdf_info` — check page count and metadata
4. **Cleanup**: `cleanup` with `dry_run=true` first, then without

## Error Recovery
If compilation fails, run `validate_latex` to identify syntax errors.
If validation passes but compilation fails, check for missing packages or increase timeout.
"""

    raise ValueError(f"Unknown resource: {uri}")


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
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    except Exception as e:
        logger.error("Error in tool call %s: %s", tool_name, e)
        return _text_result(f"Error: {e}")


async def _handle_compile(args: dict) -> list[TextContent]:
    tex_path = args.get("tex_path")
    if not tex_path:
        return _text_result("Error: tex_path is required")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            compile_latex,
            tex_path,
            args.get("output_dir"),
            args.get("timeout", 30),
        )

        if result.success:
            text = f"Compilation successful\nOutput: {result.output_path}"
            if result.compilation_time_seconds:
                text += f"\nCompilation time: {result.compilation_time_seconds:.2f}s"
        else:
            text = "Compilation failed"
            if result.error_message:
                text += f"\nError: {result.error_message}"
            if result.compilation_time_seconds:
                text += f"\nCompilation time: {result.compilation_time_seconds:.2f}s"
            if result.log_content:
                text += f"\n{get_error_summary(result.log_content)}"
        return _text_result(text)

    except CompilationError as e:
        return _text_result(f"Compilation error: {e}")


async def _handle_validate(args: dict) -> list[TextContent]:
    file_path = args.get("file_path")
    if not file_path:
        return _text_result("Error: file_path is required")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            validate_latex,
            file_path,
            args.get("quick", False),
            args.get("strict", False),
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
    file_path = args.get("file_path")
    if not file_path:
        return _text_result("Error: file_path is required")

    include_text = args.get("include_text", False)
    try:
        loop = asyncio.get_event_loop()
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
    path = args.get("path")
    if not path:
        return _text_result("Error: path is required")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            clean_latex,
            path,
            args.get("extensions"),
            args.get("dry_run", False),
            args.get("recursive", False),
            args.get("create_backup", False),
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
