# compile_latex Tool

## Overview

The `compile_latex` tool compiles LaTeX documents to PDF with comprehensive error handling and performance optimization.

**Primary Use Cases:**
- Research paper compilation
- Technical documentation generation
- Academic thesis preparation
- Report generation workflows

## Tool Specification

### MCP Tool Definition
```json
{
  "name": "compile_latex",
  "description": "Compile LaTeX documents to PDF with comprehensive error handling",
  "inputSchema": {
    "type": "object",
    "properties": {
      "tex_path": {
        "type": "string",
        "description": "Path to the LaTeX (.tex) file to compile"
      },
      "output_dir": {
        "type": "string",
        "description": "Directory for output PDF (optional, defaults to same directory as input)"
      },
      "timeout": {
        "type": "integer",
        "description": "Compilation timeout in seconds (optional, default: 30)"
      },
      "engine": {
        "type": "string",
        "description": "LaTeX engine to use (optional, default: pdflatex)",
        "enum": ["pdflatex", "xelatex", "lualatex"]
      }
    },
    "required": ["tex_path"]
  }
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tex_path` | string | ✅ | - | Path to LaTeX file to compile |
| `output_dir` | string | ❌ | Same as input | Output directory for PDF |
| `timeout` | integer | ❌ | 30 | Compilation timeout (seconds) |
| `engine` | string | ❌ | "pdflatex" | LaTeX engine (pdflatex/xelatex/lualatex) |

### Response Schema

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "True if compilation succeeded"
    },
    "output_path": {
      "type": "string",
      "description": "Path to generated PDF file"
    },
    "error_message": {
      "type": "string",
      "description": "Error description if compilation failed"
    },
    "log_content": {
      "type": "string", 
      "description": "Full LaTeX compilation log"
    },
    "compilation_time_seconds": {
      "type": "number",
      "description": "Time taken for compilation in seconds"
    }
  }
}
```

## Usage Examples

### Basic Compilation

**Human Usage:**
```python
# Compile a simple document
result = await compile_latex("document.tex")
if result.success:
    print(f"✅ PDF created: {result.output_path}")
    print(f"⏱️ Time: {result.compilation_time_seconds:.2f}s")
else:
    print(f"❌ Error: {result.error_message}")
```

**LLM Usage:**
```json
{
  "tool": "compile_latex",
  "parameters": {
    "tex_path": "document.tex"
  }
}
```

### Advanced Compilation with Options

**Human Usage:**
```python
# Compile with custom options
result = await compile_latex(
    tex_path="thesis.tex",
    output_dir="./output",
    timeout=60,
    engine="xelatex"
)
```

**LLM Usage:**
```json
{
  "tool": "compile_latex",
  "parameters": {
    "tex_path": "thesis.tex",
    "output_dir": "./output",
    "timeout": 60,
    "engine": "xelatex"
  }
}
```

### Batch Processing Pattern

**Human Usage:**
```python
# Compile multiple documents
documents = ["paper1.tex", "paper2.tex", "paper3.tex"]
results = []

for doc in documents:
    result = await compile_latex(doc)
    results.append(result)
    print(f"📄 {doc}: {'✅' if result.success else '❌'}")
```

**LLM Usage:**
```json
[
  {
    "tool": "compile_latex",
    "parameters": {"tex_path": "paper1.tex"}
  },
  {
    "tool": "compile_latex", 
    "parameters": {"tex_path": "paper2.tex"}
  },
  {
    "tool": "compile_latex",
    "parameters": {"tex_path": "paper3.tex"}
  }
]
```

## Response Examples

### Successful Compilation

```json
{
  "success": true,
  "output_path": "/path/to/document.pdf",
  "error_message": null,
  "log_content": "This is pdfTeX, Version 3.141592653...\nOutput written on document.pdf (1 page, 95405 bytes).",
  "compilation_time_seconds": 0.34
}
```

### Compilation Error

```json
{
  "success": false,
  "output_path": null,
  "error_message": "LaTeX compilation failed: Undefined control sequence \\invalidcommand on line 15",
  "log_content": "! Undefined control sequence.\nl.15 \\invalidcommand\n                     {text}",
  "compilation_time_seconds": 0.12
}
```

### Timeout Error

```json
{
  "success": false,
  "output_path": null,
  "error_message": "LaTeX compilation timed out after 30 seconds",
  "log_content": "Compilation interrupted due to timeout",
  "compilation_time_seconds": 30.0
}
```

## Error Handling

### Error Categories

| Error Type | Description | Common Causes | Recovery Strategy |
|------------|-------------|---------------|-------------------|
| **Syntax Error** | LaTeX syntax issues | Missing braces, undefined commands | Check LaTeX syntax, validate document |
| **Package Error** | Missing LaTeX packages | Package not installed | Install missing packages |
| **File Error** | File system issues | Permission denied, file not found | Check file permissions and paths |
| **Timeout Error** | Compilation timeout | Infinite loops, large documents | Increase timeout, optimize document |
| **Memory Error** | Out of memory | Very large documents | Optimize document, increase memory |

### Structured Error Response

```json
{
  "error_type": "syntax_error",
  "line_number": 42,
  "file_path": "/path/to/document.tex",
  "error_context": "\\section{Introduction",
  "suggestion": "Add closing brace: \\section{Introduction}"
}
```

## Performance Characteristics

### Benchmark Data

| Document Type | Typical Size | Compilation Time | Memory Usage |
|---------------|-------------|------------------|---------------|
| Simple Paper | 1-2 pages | 0.1-0.2s | 15-25MB |
| Research Paper | 6-10 pages | 0.2-0.5s | 25-40MB |
| Technical Report | 20-30 pages | 0.5-1.0s | 40-60MB |
| Thesis Chapter | 50+ pages | 1.0-2.0s | 60-100MB |

### Performance Optimization

**LaTeX Document Optimization:**
```latex
% Use efficient packages
\usepackage[final]{microtype}  % Better typography
\usepackage{graphicx}          % Efficient graphics
\usepackage{booktabs}          % Professional tables

% Optimize compilation
\nonstopmode                   % Continue on errors
\pdfcompresslevel=9           % Compress PDF
```

**Tool Usage Optimization:**
```python
# Pre-validate before compilation
validation = validate_latex("document.tex")
if validation.is_valid:
    result = await compile_latex("document.tex")
else:
    print("Fix validation errors first")
```

## Integration Patterns

### Research Workflow Pattern

```python
async def research_workflow(tex_file: str):
    """Complete research document workflow"""
    
    # 1. Validate syntax
    validation = validate_latex(tex_file)
    if not validation.is_valid:
        return {"status": "validation_failed", "errors": validation.errors}
    
    # 2. Compile document
    compilation = await compile_latex(tex_file)
    if not compilation.success:
        return {"status": "compilation_failed", "error": compilation.error_message}
    
    # 3. Analyze PDF
    pdf_analysis = extract_pdf_info(compilation.output_path)
    
    # 4. Clean auxiliary files
    cleanup_result = clean_latex(tex_file)
    
    return {
        "status": "success",
        "pdf_path": compilation.output_path,
        "pages": pdf_analysis.page_count,
        "size_kb": pdf_analysis.file_size_bytes / 1024,
        "compilation_time": compilation.compilation_time_seconds,
        "cleaned_files": cleanup_result.cleaned_files_count
    }
```

### CI/CD Integration Pattern

```yaml
# .github/workflows/latex-build.yml
name: LaTeX Build
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup LaTeX Tools
        run: |
          pip install mcp-latex-tools
          sudo apt-get install texlive-latex-base
      - name: Compile Documents
        run: |
          python -c "
          import asyncio
          from mcp_latex_tools.tools.compile import compile_latex
          
          async def build_all():
              docs = ['paper.tex', 'presentation.tex']
              for doc in docs:
                  result = await compile_latex(doc)
                  if not result.success:
                      raise Exception(f'Failed to compile {doc}')
              
          asyncio.run(build_all())
          "
```

## Best Practices

### Document Preparation
1. **Use consistent file structure** - Keep images and files organized
2. **Include error handling** - Always check compilation results
3. **Optimize for speed** - Use efficient LaTeX packages
4. **Test incrementally** - Compile frequently during development

### Tool Usage
1. **Validate before compiling** - Catch syntax errors early
2. **Use appropriate timeouts** - Match timeout to document complexity
3. **Handle errors gracefully** - Provide user-friendly error messages
4. **Monitor performance** - Track compilation times and optimize

### Production Deployment
1. **Resource monitoring** - Track memory and CPU usage
2. **Error logging** - Log compilation failures for debugging
3. **Caching strategy** - Cache compiled results when appropriate
4. **Backup strategy** - Preserve source files and compilation logs

---

**This tool provides production-ready LaTeX compilation with comprehensive error handling and performance optimization for both human and LLM users.** 🔧