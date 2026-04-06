# MCP LaTeX Tools Architecture Documentation

**Last Updated**: 2026-04-05
**Version**: 2.0

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [MCP Integration](#mcp-integration)
4. [Tool Design Patterns](#tool-design-patterns)
5. [Token Optimization Strategy](#token-optimization-strategy)
6. [Roadmap](#roadmap)

---

## Executive Summary

MCP LaTeX Tools is a production-ready Model Context Protocol server providing LaTeX compilation and PDF analysis tools with three key architectural pillars:

1. **Concise Output**: 97.4% token reduction through intelligent log parsing
2. **Comprehensive Tooling**: Five core tools (compile, validate, pdf_info, cleanup, detect_packages)
3. **Extensible Design**: Modular architecture supporting future enhancements

**Current Status**: Production-ready core tools with 100% test pass rate (172 tests), achieving sub-second performance and massive token reduction.

---

## System Architecture Overview

### Directory Structure

```
mcp-latex-tools/
├── src/mcp_latex_tools/
│   ├── server.py              # MCP server entry point
│   ├── tools/
│   │   ├── compile.py         # LaTeX compilation (pdflatex/xelatex/lualatex/latexmk, multi-pass)
│   │   ├── validate.py        # Syntax validation
│   │   ├── pdf_info.py        # PDF metadata extraction
│   │   ├── cleanup.py         # Auxiliary file cleanup
│   │   └── detect_packages.py # Package detection and installation check
│   └── utils/
│       └── log_parser.py      # Token-optimized log parsing
├── tests/                     # Test suite (mirrors src structure)
│   ├── fixtures/              # Test fixture files
│   ├── test_compile.py
│   ├── test_validate.py
│   ├── test_pdf_info.py
│   ├── test_pdf_info_edge_cases.py
│   ├── test_cleanup.py
│   ├── test_cleanup_edge_cases.py
│   ├── test_log_parser.py
│   ├── test_mcp_resources_prompts.py
│   ├── test_detect_packages.py
│   ├── test_server_integration.py
│   └── test_server_error_handling.py
├── docs/                      # Documentation
│   ├── LLM_REFERENCE.md
│   ├── README.md
│   └── development/
│       ├── ARCHITECTURE.md
│       └── BACKLOG.md
└── pyproject.toml             # UV project configuration
```

### Architectural Layers

#### Layer 1: MCP Protocol Handler (server.py)
- Handles MCP JSON-RPC communication
- Routes tool calls to appropriate handlers
- Formats responses for Claude Code consumption
- Implements token-optimized output

#### Layer 2: Tool Implementation (tools/)
- **compile.py**: LaTeX → PDF compilation with multi-engine (pdflatex/xelatex/lualatex/latexmk), multi-pass, and automatic bibliography (bibtex/biber) support
- **validate.py**: Syntax checking without compilation
- **pdf_info.py**: PDF metadata extraction
- **cleanup.py**: Auxiliary file management
- **detect_packages.py**: Package detection via `\usepackage`/`\RequirePackage` parsing and `kpsewhich` installation checks

#### Layer 3: Utilities (utils/)
- **log_parser.py**: Intelligent log parsing for token reduction

---

## MCP Integration

### Protocol Implementation

The MCP server implements the Model Context Protocol for seamless integration with Claude Code and other MCP clients.

```python
# MCP Server Registration
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available LaTeX tools."""
    return [
        Tool(name="compile_latex", ...),
        Tool(name="validate_latex", ...),
        Tool(name="pdf_info", ...),
        Tool(name="cleanup", ...),
        Tool(name="detect_packages", ...),
    ]

@server.call_tool()
async def call_tool(tool_name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    # Route to appropriate handler
    # Return concise, token-optimized results
```

### Tool Schema Pattern

Each tool follows a consistent schema pattern:

```json
{
  "name": "tool_name",
  "description": "Clear description of what the tool does",
  "inputSchema": {
    "type": "object",
    "properties": {
      "required_param": {
        "type": "string",
        "description": "What this parameter does"
      },
      "optional_param": {
        "type": "string",
        "description": "Optional parameter with default",
        "default": "default_value"
      }
    },
    "required": ["required_param"]
  }
}
```

---

## Tool Design Patterns

### Pattern 1: Result Dataclasses

Each tool returns a structured result:

```python
@dataclass
class CompilationResult:
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    log_content: Optional[str] = None  # Full log for internal use
    compilation_time_seconds: Optional[float] = None
```

**Benefits**:
- Type-safe return values
- Clear success/failure states
- Comprehensive error information
- Performance metrics included

### Pattern 2: Graceful Error Handling

```python
try:
    result = subprocess.run(cmd, capture_output=True, ...)
    if result.returncode == 0 and output_exists:
        return SuccessResult(...)
    else:
        return FailureResult(error_message=...)
except subprocess.TimeoutExpired:
    return FailureResult(error_message="Timeout...")
except PermissionError as e:
    return FailureResult(error_message=f"Permission denied: {e}")
except Exception as e:
    return FailureResult(error_message=f"Unexpected error: {e}")
```

### Pattern 3: Token-Optimized Output

```python
# Before (full log dump - 11,147 characters):
if result.log_content:
    response_text += f"\nLog content:\n{result.log_content}"

# After (concise summary - 291 characters):
if result.log_content:
    error_summary = get_error_summary(result.log_content)
    response_text += f"\n{error_summary}\n"
```

**Result**: 97.4% token reduction

### Pattern 4: Path Parameter Aliases

Tool handlers accept common parameter name aliases (`tex_path`, `file_path`, `path`) to improve LLM invocation success rate:

```python
def _get_path_arg(args: dict, *keys: str) -> str | None:
    for key in keys:
        if val := args.get(key):
            return val
    return None
```

---

## Token Optimization Strategy

### Problem Analysis

LaTeX logs can contain thousands of lines with:
- Font loading details for every font used
- Overfull/underfull hbox warnings
- Package loading messages
- Page-by-page compilation details

### Solution: Intelligent Log Parsing

```python
class LogSummary:
    errors: List[LaTeXError]           # Only actual errors
    warnings_count: int                 # Count, not full text
    pages_count: Optional[int]          # PDF output info
    has_undefined_references: bool      # Helpful flags
    has_rerun_suggestion: bool
```

### Results

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Characters | 11,147 | 291 | 97.4% |
| Lines | 279 | 9 | 96.8% |
| Tokens (approx) | ~2,786 | ~72 | 97.4% |

---

## Roadmap

See [BACKLOG.md](BACKLOG.md) for the full feature backlog and prioritization.

---

## References

### Key Technologies
- **MCP**: Model Context Protocol for Claude Code integration
- **pypdf**: PDF metadata extraction
- **pytest**: Testing framework with async support
- **ruff**: Modern Python linter and formatter
- **mypy**: Static type checking
- **uv**: Fast Python package manager

### Related Documentation
- LLM Reference: `docs/LLM_REFERENCE.md`
- Backlog: `docs/development/BACKLOG.md`
- Project Instructions: `CLAUDE.md`

---

**Document Version History**:
- 2026-04-05: Major rewrite — updated for post-cleanup architecture
- 2025-10-22: Initial architecture document
