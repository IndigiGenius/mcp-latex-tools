# MCP LaTeX Tools

[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com/IndigiGenius/mcp-latex-tools)
[![Claude Code Compatible](https://img.shields.io/badge/Claude%20Code-Compatible-blue)](https://claude.ai/code)
[![Test Coverage](https://img.shields.io/badge/Test%20Coverage-85%25-green)](https://github.com/IndigiGenius/mcp-latex-tools)

> **Production-ready Model Context Protocol server providing LaTeX compilation and PDF analysis tools for Claude Code**

## Overview

MCP LaTeX Tools is a comprehensive Model Context Protocol server that enables Claude Code to compile LaTeX documents, validate syntax, extract PDF metadata, and manage auxiliary files with professional-grade performance and error handling.

### =€ Key Features

- **¡ Fast Compilation**: Sub-second compilation for typical documents
- ** Syntax Validation**: Instant LaTeX syntax checking without compilation
- **=Ä PDF Analysis**: Comprehensive PDF metadata extraction and analysis
- **>ù Smart Cleanup**: Automated auxiliary file management with backup options
- **> Claude Code Integration**: Seamless integration with Claude Code CLI
- **= Production Ready**: 85% test coverage with robust error handling

### =à Tools Provided

| Tool | Purpose | Performance |
|------|---------|-------------|
| **compile_latex** | LaTeX to PDF compilation | 0.1-0.5s typical |
| **validate_latex** | Syntax validation | < 0.1s |
| **pdf_info** | PDF metadata extraction | < 0.1s |
| **cleanup** | Auxiliary file management | < 0.1s |

## Quick Start

### Prerequisites

- Python 3.8+
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Claude Code CLI

### Installation

```bash
# Clone repository
git clone https://github.com/IndigiGenius/mcp-latex-tools.git
cd mcp-latex-tools

# Install dependencies
uv sync

# Test installation
uv run python src/mcp_latex_tools/server.py
```

### Claude Code Configuration

Add to your Claude Code configuration file (`~/.config/claude-code/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "uv",
      "args": ["run", "python", "src/mcp_latex_tools/server.py"],
      "cwd": "/absolute/path/to/mcp-latex-tools",
      "env": {}
    }
  }
}
```

### First Use

In Claude Code, ask:
```
Can you create a simple LaTeX document and compile it?
```

Claude Code will demonstrate all four tools in action! <‰

## Documentation

### =Ö Getting Started
- **[Installation Guide](docs/getting-started/installation.md)** - Complete setup instructions
- **[Claude Code Setup](docs/getting-started/claude-code-setup.md)** - MCP server configuration
- **[First Compilation](docs/getting-started/first-compilation.md)** - Your first LaTeX document

### =' API Reference
- **[compile_latex](docs/api-reference/compile-latex.md)** - LaTeX compilation with error handling
- **[validate_latex](docs/api-reference/validate-latex.md)** - Syntax validation and checking
- **[pdf_info](docs/api-reference/pdf-info.md)** - PDF metadata and analysis
- **[cleanup](docs/api-reference/cleanup.md)** - Auxiliary file management

### =¡ Examples & Patterns
- **[Integration Patterns](docs/examples/integration-patterns.md)** - Advanced workflows and use cases
- **[Research Workflow](RESEARCH_WORKFLOW.md)** - Academic document preparation

### =' Troubleshooting
- **[Common Errors](docs/troubleshooting/common-errors.md)** - Solutions to frequent issues

### =Ê Technical Details
- **[JSON Schemas](docs/schemas/mcp-tools.json)** - Complete tool specifications
- **[Documentation Strategy](DOCUMENTATION_STRATEGY.md)** - Dual-audience documentation approach

## Performance Benchmarks

| Document Type | Validation | Compilation | PDF Analysis | Total Workflow |
|---------------|------------|-------------|--------------|----------------|
| Simple Paper (1-2 pages) | < 0.1s | 0.1-0.2s | < 0.1s | < 0.4s |
| Research Paper (6-10 pages) | < 0.1s | 0.2-0.5s | < 0.1s | < 0.7s |
| Technical Report (20+ pages) | < 0.2s | 0.5-1.0s | < 0.1s | < 1.3s |
| Thesis Chapter (50+ pages) | < 0.3s | 1.0-2.0s | < 0.1s | < 2.4s |

## Example Usage

### Complete Research Workflow

```python
# Through Claude Code, this workflow happens automatically:

# 1. Validate LaTeX syntax
validation = validate_latex("research_paper.tex")
#  Validation: Success - No errors found

# 2. Compile to PDF  
compilation = await compile_latex("research_paper.tex")
#  Compilation: Success in 0.25s

# 3. Analyze PDF output
pdf_analysis = pdf_info("research_paper.pdf") 
#  PDF Info: 6 pages, 164.5 KB

# 4. Clean auxiliary files
cleanup_result = cleanup("research_paper.tex")
#  Cleanup: 2 auxiliary files removed
```

### Real-World Performance

**Research Document Example** (6 pages with math, tables, figures):
- **Validation**:  0.05s
- **Compilation**:  0.25s  
- **PDF Analysis**:  0.02s
- **Cleanup**:  0.01s
- **Total**:  0.33s

## Integration Examples

### Academic Research
```
Claude Code: "Help me create a research paper with abstract, introduction, 
methodology, results with tables and graphs, and conclusion. Include proper 
citations and compile it."
```

### Technical Documentation
```
Claude Code: "Create technical documentation with code listings, diagrams, 
and a professional layout. Make sure it compiles cleanly."
```

### Presentations
```
Claude Code: "Create a Beamer presentation about machine learning with 
mathematical equations and compile it to PDF."
```

## Architecture

### Modern Python Tooling
- **UV**: Fast Python package manager and virtual environment management
- **Ruff**: Lightning-fast linting and formatting
- **MyPy**: Static type checking for reliability
- **Pytest**: Comprehensive testing with 85% coverage

### MCP Integration
- **Async Operations**: Non-blocking LaTeX compilation
- **Structured Responses**: JSON schemas for reliable tool interactions  
- **Error Handling**: Comprehensive error taxonomy and recovery
- **Performance Monitoring**: Built-in timing and resource tracking

### Test-Driven Development
- **Immutable Tests**: Tests define behavior, code adapts to pass tests
- **Edge Case Coverage**: Comprehensive error condition testing
- **Integration Testing**: End-to-end MCP protocol verification
- **Performance Testing**: Benchmark validation for all operations

## Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/IndigiGenius/mcp-latex-tools.git
cd mcp-latex-tools

# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Code quality checks
uv run ruff check src/ tests/
uv run mypy src/
```

### Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests first** (TDD approach)
4. **Implement feature** to make tests pass
5. **Ensure quality**: `uv run ruff check && uv run mypy src/ && uv run pytest`
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**

## Production Status

###  Production Ready Features
- **Core Tools**: All 4 MCP tools fully functional
- **Claude Code Integration**: 100% compatible
- **Error Handling**: Robust with comprehensive error taxonomy
- **Performance**: Sub-second compilation for typical documents
- **Test Coverage**: 85% with focus on critical paths
- **Documentation**: Complete dual-audience documentation

### =' Optional Enhancements
- **Documentation**: API docs and advanced examples (in progress)
- **Testing**: Increase coverage from 85% to 95%
- **Architecture**: Migrate to Pydantic models for enhanced validation
- **Features**: Batch processing, package management, caching

## Support

### Getting Help
- **=Ú Documentation**: Complete guides and API reference in `/docs`
- **= Issues**: [GitHub Issues](https://github.com/IndigiGenius/mcp-latex-tools/issues)
- **=¬ Discussions**: [GitHub Discussions](https://github.com/IndigiGenius/mcp-latex-tools/discussions)

### Reporting Issues
Include:
- System information (OS, Python version, LaTeX distribution)
- MCP server configuration
- Minimal example that reproduces the issue
- Full error messages and logs

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Anthropic** for Claude Code and the Model Context Protocol
- **LaTeX Community** for the excellent typesetting system
- **Python Community** for outstanding development tools

---

**=€ Ready to create beautiful LaTeX documents with the power of Claude Code and MCP LaTeX Tools!**

*For detailed documentation, examples, and troubleshooting, visit the [docs](docs/) directory.*