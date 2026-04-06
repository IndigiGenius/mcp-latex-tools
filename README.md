# MCP LaTeX Tools

Production-ready MCP server providing LaTeX compilation and PDF analysis tools for Claude Code.

## Tools

| Tool | Purpose |
|------|---------|
| `compile_latex` | Compile .tex to PDF via pdflatex |
| `validate_latex` | Check LaTeX syntax without compiling |
| `pdf_info` | Extract PDF metadata and dimensions |
| `cleanup` | Remove auxiliary files (.aux, .log, etc.) |

## Quick Start

### Prerequisites

- Python 3.8+
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)

### Installation

```bash
git clone https://github.com/IndigiGenius/mcp-latex-tools.git
cd mcp-latex-tools
uv sync
```

### Claude Code Configuration

Add to your Claude Code MCP config:

```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "uv",
      "args": ["run", "python", "src/mcp_latex_tools/server.py"],
      "cwd": "/absolute/path/to/mcp-latex-tools"
    }
  }
}
```

## Development

```bash
uv run pytest                          # Run tests
uv run pytest --cov=src                # With coverage
uv run ruff check src/ tests/          # Lint
uv run mypy src/                       # Type check
```

## Architecture

- **Async MCP server** using `mcp` SDK with stdio transport
- **4 tools** registered via `@server.call_tool()` dispatcher
- **3 resources** (cleanup extensions, protected extensions, workflow guide)
- **3 prompts** (compile-and-verify, diagnose-error, fresh-build)

See [docs/development/ARCHITECTURE.md](docs/development/ARCHITECTURE.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.
