# MCP LaTeX Tools Documentation

> LaTeX compilation and PDF analysis tools via Model Context Protocol (MCP)

## Documents

| Document | Purpose |
|----------|---------|
| [LLM_REFERENCE.md](LLM_REFERENCE.md) | Quick reference for LLM agents |
| [development/ARCHITECTURE.md](development/ARCHITECTURE.md) | System design |
| [development/BACKLOG.md](development/BACKLOG.md) | Feature roadmap |

## Tools

| Tool | Purpose | Side Effects |
|------|---------|--------------|
| `compile_latex` | .tex to PDF | Creates .pdf, .aux, .log |
| `validate_latex` | Syntax check | None (read-only) |
| `pdf_info` | PDF metadata | None (read-only) |
| `cleanup` | Remove aux files | Deletes files |
