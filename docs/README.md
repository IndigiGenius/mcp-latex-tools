# MCP LaTeX Tools Documentation

[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com/IndigiGenius/mcp-latex-tools)
[![Claude Code Compatible](https://img.shields.io/badge/Claude%20Code-Compatible-blue)](https://claude.ai/code)
[![Test Coverage](https://img.shields.io/badge/Test%20Coverage-85%25-green)](https://github.com/IndigiGenius/mcp-latex-tools)

> **Complete LaTeX compilation and PDF analysis tools for Claude Code via Model Context Protocol (MCP)**

## Overview

MCP LaTeX Tools is a production-ready Model Context Protocol server that provides four essential LaTeX workflow capabilities:

- **🔧 compile_latex**: Fast LaTeX-to-PDF compilation with comprehensive error handling
- **✅ validate_latex**: Quick syntax validation without full compilation  
- **📄 pdf_info**: PDF metadata extraction and analysis
- **🧹 cleanup**: Automated auxiliary file management

## Quick Start

### Prerequisites
- Python 3.8+
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Claude Code CLI

### Installation
```bash
# Clone the repository
git clone https://github.com/IndigiGenius/mcp-latex-tools.git
cd mcp-latex-tools

# Install dependencies
uv sync

# Test the server
uv run python src/mcp_latex_tools/server.py
```

### Claude Code Integration
```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "python",
      "args": ["/path/to/mcp-latex-tools/src/mcp_latex_tools/server.py"],
      "env": {}
    }
  }
}
```

## Performance Benchmarks

| Document Type | Pages | Compilation Time | Test Status |
|---------------|-------|------------------|-------------|
| Simple Paper | 1-2 | 0.1-0.2s | ✅ |
| Research Paper | 3-10 | 0.2-0.5s | ✅ |
| Technical Report | 10-30 | 0.5-1.0s | ✅ |
| Complex Document | 30+ | 1.0-2.0s | ✅ |

## Documentation Structure

### 📖 For Human Users
- **[Getting Started](getting-started/)** - Installation and first-use guide
- **[Examples](examples/)** - Real-world usage patterns and workflows
- **[Troubleshooting](troubleshooting/)** - Common issues and solutions

### 🤖 For LLM Users  
- **[API Reference](api-reference/)** - Structured tool specifications
- **[Schemas](schemas/)** - JSON schemas and OpenAPI definitions
- **[Performance](performance/)** - Benchmarks and optimization data

### 📋 Universal Reference
- **[Tool Specifications](api-reference/)** - Complete parameter documentation
- **[Error Handling](troubleshooting/errors.md)** - Structured error taxonomies
- **[Integration Patterns](examples/integration-patterns.md)** - Common usage scenarios

## Tool Overview

### compile_latex
**Purpose**: Compile LaTeX documents to PDF with comprehensive error handling

**Key Features**:
- Sub-second compilation for typical documents
- Comprehensive error parsing and reporting
- Automatic path resolution and validation
- Timeout protection and resource management

### validate_latex
**Purpose**: Quick syntax validation without full compilation

**Key Features**:
- Instant syntax checking
- Multiple validation modes (quick/strict)
- Error location reporting
- No PDF generation overhead

### pdf_info
**Purpose**: Extract PDF metadata and document analysis

**Key Features**:
- Page count and dimensions
- File size and creation metadata
- PDF version and encryption status
- Document properties extraction

### cleanup
**Purpose**: Automated auxiliary file management

**Key Features**:
- Selective file type cleaning
- Backup creation options
- Dry-run preview mode
- Recursive directory support

## Integration Examples

### Basic LaTeX Compilation
```python
# Human-readable workflow
result = await compile_latex("document.tex")
if result.success:
    print(f"✅ PDF created: {result.output_path}")
    print(f"⏱️ Compilation time: {result.compilation_time_seconds:.2f}s")
```

### Complete Research Workflow
```python
# Comprehensive document workflow
# 1. Validate syntax
validation = validate_latex("research_paper.tex")
if not validation.is_valid:
    print("❌ Syntax errors found")
    
# 2. Compile to PDF
compilation = await compile_latex("research_paper.tex")
if compilation.success:
    # 3. Analyze PDF
    pdf_analysis = extract_pdf_info("research_paper.pdf")
    print(f"📄 {pdf_analysis.page_count} pages, {pdf_analysis.file_size_bytes/1024:.1f}KB")
    
    # 4. Clean auxiliary files
    cleanup_result = clean_latex("research_paper.tex")
    print(f"🧹 Cleaned {cleanup_result.cleaned_files_count} auxiliary files")
```

## Error Handling

### Structured Error Response
```json
{
  "success": false,
  "error_message": "LaTeX compilation failed",
  "error_type": "compilation_error",
  "line_number": 42,
  "file_path": "/path/to/document.tex",
  "suggestion": "Missing package 'amsmath'. Add \\usepackage{amsmath} to preamble."
}
```

### Common Error Categories
- **Syntax Errors**: Missing braces, undefined commands
- **Package Errors**: Missing LaTeX packages
- **File Errors**: Permission issues, missing files
- **Compilation Errors**: Memory limits, infinite loops

## Performance Optimization

### Best Practices
1. **Use validation before compilation** - Catch errors early
2. **Clean auxiliary files regularly** - Prevent conflicts
3. **Optimize LaTeX code** - Reduce compilation time
4. **Monitor resource usage** - Prevent memory issues

### Benchmarking Data
```json
{
  "performance_metrics": {
    "average_compilation_time": "0.35s",
    "memory_usage": "45MB",
    "success_rate": "99.2%",
    "error_recovery_rate": "87%"
  }
}
```

## Support and Contributing

### Getting Help
- **Documentation**: This comprehensive guide
- **Issues**: [GitHub Issues](https://github.com/IndigiGenius/mcp-latex-tools/issues)
- **Discussions**: [GitHub Discussions](https://github.com/IndigiGenius/mcp-latex-tools/discussions)

### Contributing
- **Code**: Submit pull requests with tests
- **Documentation**: Improve clarity and completeness
- **Examples**: Add real-world usage patterns
- **Testing**: Expand test coverage and edge cases

## License

MIT License - See [LICENSE](../LICENSE) file for details.

---

**📖 This documentation serves both human users and LLM assistants with structured, comprehensive information optimized for clarity and machine readability.**