# CLAUDE.md

MCP LaTeX Tools is an MCP server providing LaTeX compilation and PDF analysis tools. Uses TDD methodology with modern Python tooling.

**Status**: Production Ready | 4 tools

## Commands

```bash
# Tests
uv run pytest                                    # Run all tests
uv run pytest --cov=src --cov-report=html       # With coverage

# Code quality (run before committing)
uv run ruff check src/ tests/ && uv run ruff format src/ tests/ && uv run mypy src/

# Run server
uv run python src/mcp_latex_tools/server.py
```

## Project Structure

```
src/mcp_latex_tools/
├── server.py        # MCP server entry point
├── tools/           # compile, validate, pdf_info, cleanup
└── utils/           # log_parser
tests/               # Test files and fixtures
docs/                # Documentation
```

## MCP Tools

| Tool | Purpose |
|------|---------|
| `compile_latex` | Compile .tex to PDF with error handling |
| `validate_latex` | Quick syntax validation (no compilation) |
| `pdf_info` | Extract PDF metadata (pages, dimensions) |
| `cleanup` | Remove auxiliary files (.aux, .log, etc.) |

## Development Rules

- **TDD**: Write failing tests first, implement minimal code, refactor
- **Tests are immutable**: Code must pass existing tests (unless intentionally changing behavior)
- **Type hints**: Enforced by mypy throughout
- **No duplication**: Extract common patterns to utils/

## Documentation

| Document | Purpose |
|----------|---------|
| `docs/LLM_REFERENCE.md` | Quick reference for LLM agents |
| `docs/development/ARCHITECTURE.md` | System architecture |
| `docs/development/BACKLOG.md` | Feature backlog |

---
*Last Updated: 2026-03-15*
