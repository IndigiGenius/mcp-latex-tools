"""MCP server for LaTeX compilation and PDF tools."""

import asyncio
import logging

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

from mcp_latex_tools.tools.compile import compile_latex, CompilationError
from mcp_latex_tools.tools.validate import validate_latex, ValidationError
from mcp_latex_tools.tools.pdf_info import extract_pdf_info, PDFInfoError
from mcp_latex_tools.tools.cleanup import clean_latex, CleanupError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server: Server = Server("mcp-latex-tools")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available LaTeX tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="compile_latex",
                description="Compile LaTeX files to PDF with comprehensive error handling",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tex_path": {
                            "type": "string",
                            "description": "Path to the .tex file to compile",
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Directory for output (defaults to same as input)",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Maximum seconds to wait for compilation",
                            "default": 30,
                        },
                    },
                    "required": ["tex_path"],
                },
            ),
            Tool(
                name="validate_latex",
                description="Validate LaTeX syntax without full compilation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the .tex file to validate",
                        },
                        "quick": {
                            "type": "boolean",
                            "description": "Perform quick syntax check only (mutually exclusive with strict)",
                            "default": False,
                        },
                        "strict": {
                            "type": "boolean",
                            "description": "Perform thorough validation with style checks (mutually exclusive with quick)",
                            "default": False,
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            Tool(
                name="pdf_info",
                description="Extract PDF metadata and information without compilation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the PDF file to analyze",
                        },
                        "include_text": {
                            "type": "boolean",
                            "description": "Extract text content from PDF pages",
                            "default": False,
                        },
                        "password": {
                            "type": "string",
                            "description": "Password for encrypted PDFs (optional)",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            Tool(
                name="cleanup",
                description="Clean LaTeX auxiliary files (.aux, .log, .out, etc.) from directories or individual files",
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
                            "description": "List of file extensions to clean (defaults to common auxiliary files)",
                        },
                        "dry_run": {
                            "type": "boolean",
                            "description": "Show what would be cleaned without removing files",
                            "default": False,
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Clean subdirectories recursively",
                            "default": False,
                        },
                        "create_backup": {
                            "type": "boolean",
                            "description": "Create backup of files before deletion",
                            "default": False,
                        },
                    },
                    "required": ["path"],
                },
            ),
        ]
    )


@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    try:
        if request.params.name == "compile_latex":
            return await handle_compile_latex(request)
        elif request.params.name == "validate_latex":
            return await handle_validate_latex(request)
        elif request.params.name == "pdf_info":
            return await handle_pdf_info(request)
        elif request.params.name == "cleanup":
            return await handle_cleanup(request)
        else:
            raise ValueError(f"Unknown tool: {request.params.name}")
    except Exception as e:
        logger.error(f"Error in tool call {request.params.name}: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}",
                )
            ]
        )


async def handle_compile_latex(request: CallToolRequest) -> CallToolResult:
    """Handle LaTeX compilation requests."""
    args = request.params.arguments or {}
    
    # Extract arguments
    tex_path = args.get("tex_path")
    output_dir = args.get("output_dir")
    timeout = args.get("timeout", 30)
    
    if not tex_path:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Error: tex_path is required",
                )
            ]
        )
    
    try:
        # Run compilation in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            compile_latex,
            tex_path,
            output_dir,
            timeout,
        )
        
        # Format response
        if result.success:
            response_text = "✓ LaTeX compilation successful!\n"
            response_text += f"Output: {result.output_path}\n"
            if result.compilation_time_seconds:
                response_text += f"Compilation time: {result.compilation_time_seconds:.2f}s\n"
        else:
            response_text = "✗ LaTeX compilation failed\n"
            if result.error_message:
                response_text += f"Error: {result.error_message}\n"
            if result.compilation_time_seconds:
                response_text += f"Compilation time: {result.compilation_time_seconds:.2f}s\n"
        
        # Include log content if available
        if result.log_content:
            response_text += f"\nLog content:\n{result.log_content}"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=response_text,
                )
            ]
        )
        
    except CompilationError as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Compilation error: {str(e)}",
                )
            ]
        )
    except Exception as e:
        logger.error(f"Unexpected error in compile_latex: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}",
                )
            ]
        )


async def handle_validate_latex(request: CallToolRequest) -> CallToolResult:
    """Handle LaTeX validation requests."""
    args = request.params.arguments or {}
    
    # Extract arguments
    file_path = args.get("file_path")
    quick = args.get("quick", False)
    strict = args.get("strict", False)
    
    if not file_path:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Error: file_path is required",
                )
            ]
        )
    
    try:
        # Run validation in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            validate_latex,
            file_path,
            quick,
            strict,
        )
        
        # Format response
        if result.is_valid:
            response_text = "✓ Valid LaTeX syntax\n"
            response_text += "No errors found\n"
            if result.warnings:
                response_text += f"Warnings ({len(result.warnings)}):\n"
                for warning in result.warnings:
                    response_text += f"  • {warning}\n"
        else:
            response_text = "✗ Invalid LaTeX syntax\n"
            response_text += f"Errors found ({len(result.errors)}):\n"
            for error in result.errors:
                response_text += f"  • {error}\n"
            if result.warnings:
                response_text += f"Warnings ({len(result.warnings)}):\n"
                for warning in result.warnings:
                    response_text += f"  • {warning}\n"
        
        # Include validation time
        if result.validation_time_seconds:
            response_text += f"Validation time: {result.validation_time_seconds:.3f}s\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=response_text,
                )
            ]
        )
        
    except ValidationError as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Validation error: {str(e)}",
                )
            ]
        )
    except Exception as e:
        logger.error(f"Unexpected error in validate_latex: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}",
                )
            ]
        )


async def handle_pdf_info(request: CallToolRequest) -> CallToolResult:
    """Handle PDF info extraction requests."""
    args = request.params.arguments or {}
    
    # Extract arguments
    file_path = args.get("file_path")
    include_text = args.get("include_text", False)
    password = args.get("password")
    
    if not file_path:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Error: file_path is required",
                )
            ]
        )
    
    try:
        # Run PDF info extraction in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            extract_pdf_info,
            file_path,
            include_text,
            password,
        )
        
        # Format response
        if result.success:
            response_text = "✓ PDF info extracted successfully\n"
            response_text += f"File: {result.file_path}\n"
            response_text += f"Pages: {result.page_count}\n"
            response_text += f"File size: {result.file_size_bytes:,} bytes\n"
            
            if result.pdf_version:
                response_text += f"PDF version: {result.pdf_version}\n"
            
            if result.is_encrypted:
                response_text += "Encrypted: Yes\n"
            else:
                response_text += "Encrypted: No\n"
            
            # Add page dimensions
            if result.page_dimensions:
                response_text += "Dimensions:\n"
                for i, dims in enumerate(result.page_dimensions):
                    response_text += f"  Page {i+1}: {dims['width']:.1f} x {dims['height']:.1f} {dims['unit']}\n"
            
            # Add metadata if available
            if result.title:
                response_text += f"Title: {result.title}\n"
            if result.author:
                response_text += f"Author: {result.author}\n"
            if result.subject:
                response_text += f"Subject: {result.subject}\n"
            if result.producer:
                response_text += f"Producer: {result.producer}\n"
            if result.creator:
                response_text += f"Creator: {result.creator}\n"
            if result.creation_date:
                response_text += f"Created: {result.creation_date}\n"
            if result.modification_date:
                response_text += f"Modified: {result.modification_date}\n"
            
            # Add text content if requested
            if include_text and result.text_content:
                response_text += "\nText content:\n"
                for i, text in enumerate(result.text_content):
                    if text.strip():  # Only show non-empty text
                        response_text += f"  Page {i+1}: {text[:100]}...\n"
                    else:
                        response_text += f"  Page {i+1}: [No text content]\n"
            
            # Add extraction time
            if result.extraction_time_seconds:
                response_text += f"Extraction time: {result.extraction_time_seconds:.3f}s\n"
        else:
            response_text = "✗ PDF info extraction failed\n"
            if result.error_message:
                response_text += f"Error: {result.error_message}\n"
            if result.extraction_time_seconds:
                response_text += f"Extraction time: {result.extraction_time_seconds:.3f}s\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=response_text,
                )
            ]
        )
        
    except PDFInfoError as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"PDF info error: {str(e)}",
                )
            ]
        )
    except Exception as e:
        logger.error(f"Unexpected error in pdf_info: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}",
                )
            ]
        )


async def handle_cleanup(request: CallToolRequest) -> CallToolResult:
    """Handle LaTeX cleanup requests."""
    args = request.params.arguments or {}
    
    # Extract arguments
    path = args.get("path")
    extensions = args.get("extensions")
    dry_run = args.get("dry_run", False)
    recursive = args.get("recursive", False)
    create_backup = args.get("create_backup", False)
    
    if not path:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Error: path is required",
                )
            ]
        )
    
    try:
        # Run cleanup in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            clean_latex,
            path,
            extensions,
            dry_run,
            recursive,
            create_backup,
        )
        
        # Format response
        if result.success:
            if result.dry_run:
                response_text = "✓ Cleanup dry run completed\n"
                if result.would_clean_files:
                    response_text += f"Would clean {len(result.would_clean_files)} files:\n"
                    for file in result.would_clean_files[:10]:  # Show first 10
                        response_text += f"  • {file}\n"
                    if len(result.would_clean_files) > 10:
                        response_text += f"  ... and {len(result.would_clean_files) - 10} more\n"
                else:
                    response_text += "No files to clean\n"
            else:
                response_text = "✓ Cleanup completed successfully\n"
                if result.cleaned_files:
                    response_text += f"Files cleaned: {result.cleaned_files_count}\n"
                    for file in result.cleaned_files[:10]:  # Show first 10
                        response_text += f"  • {file}\n"
                    if len(result.cleaned_files) > 10:
                        response_text += f"  ... and {len(result.cleaned_files) - 10} more\n"
                else:
                    response_text += "No files needed cleaning\n"
            
            # Add details about the operation
            if result.tex_file_path:
                response_text += f"Cleaned around: {result.tex_file_path}\n"
            elif result.directory_path:
                response_text += f"Cleaned directory: {result.directory_path}\n"
            
            if result.backup_created:
                response_text += f"Backup created: {result.backup_directory}\n"
            
            if result.cleanup_time_seconds:
                response_text += f"Cleanup time: {result.cleanup_time_seconds:.3f}s\n"
        else:
            response_text = "✗ Cleanup failed\n"
            if result.error_message:
                response_text += f"Error: {result.error_message}\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=response_text,
                )
            ]
        )
        
    except CleanupError as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Cleanup error: {str(e)}",
                )
            ]
        )
    except Exception as e:
        logger.error(f"Unexpected error in cleanup: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}",
                )
            ]
        )


async def main():
    """Run the MCP server."""
    logger.info("Starting MCP LaTeX Tools server")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-latex-tools",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())