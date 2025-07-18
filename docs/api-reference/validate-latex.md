# validate_latex Tool

## Overview

The `validate_latex` tool performs quick LaTeX syntax validation without full compilation, providing rapid feedback on document structure and syntax errors.

**Primary Use Cases:**
- Pre-compilation syntax checking
- Fast iteration during document development
- Automated validation in CI/CD pipelines
- Error detection in editing workflows

## Tool Specification

### MCP Tool Definition
```json
{
  "name": "validate_latex",
  "description": "Validate LaTeX syntax without full compilation",
  "inputSchema": {
    "type": "object",
    "properties": {
      "tex_path": {
        "type": "string",
        "description": "Path to the LaTeX (.tex) file to validate"
      },
      "mode": {
        "type": "string",
        "description": "Validation mode (optional, default: quick)",
        "enum": ["quick", "strict"]
      }
    },
    "required": ["tex_path"]
  }
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tex_path` | string | ✅ | - | Path to LaTeX file to validate |
| `mode` | string | ❌ | "quick" | Validation mode (quick/strict) |

### Response Schema

```json
{
  "type": "object",
  "properties": {
    "is_valid": {
      "type": "boolean",
      "description": "True if LaTeX syntax is valid"
    },
    "error_message": {
      "type": "string",
      "description": "Error description if validation failed"
    },
    "errors": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of validation errors"
    },
    "warnings": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of validation warnings"
    }
  }
}
```

## Usage Examples

### Basic Validation

**Human Usage:**
```python
# Quick validation check
result = validate_latex("document.tex")
if result.is_valid:
    print("✅ Document is valid")
else:
    print("❌ Validation errors:")
    for error in result.errors:
        print(f"  - {error}")
```

**LLM Usage:**
```json
{
  "tool": "validate_latex",
  "parameters": {
    "tex_path": "document.tex"
  }
}
```

### Strict Validation

**Human Usage:**
```python
# Strict validation with warnings
result = validate_latex("thesis.tex", mode="strict")
if result.is_valid:
    if result.warnings:
        print("⚠️ Document valid but has warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    else:
        print("✅ Document is perfectly valid")
else:
    print("❌ Validation failed")
```

**LLM Usage:**
```json
{
  "tool": "validate_latex",
  "parameters": {
    "tex_path": "thesis.tex",
    "mode": "strict"
  }
}
```

## Response Examples

### Valid Document

```json
{
  "is_valid": true,
  "error_message": null,
  "errors": [],
  "warnings": []
}
```

### Document with Errors

```json
{
  "is_valid": false,
  "error_message": "LaTeX syntax validation failed: 2 errors found",
  "errors": [
    "Missing closing brace on line 15: \\section{Introduction",
    "Undefined command \\invalidcommand on line 23"
  ],
  "warnings": []
}
```

### Document with Warnings (Strict Mode)

```json
{
  "is_valid": true,
  "error_message": null,
  "errors": [],
  "warnings": [
    "Deprecated package usage: \\usepackage{epsfig} on line 8",
    "Missing package recommendation: Consider \\usepackage{microtype} for better typography"
  ]
}
```

## Validation Modes

### Quick Mode (Default)
- **Speed**: < 0.1 seconds
- **Scope**: Basic syntax checking
- **Detects**: Missing braces, undefined commands, structural errors
- **Use Case**: Rapid iteration during development

### Strict Mode
- **Speed**: 0.1-0.3 seconds
- **Scope**: Comprehensive analysis
- **Detects**: All quick mode issues plus warnings
- **Additional**: Package recommendations, deprecated usage, style suggestions
- **Use Case**: Pre-publication quality checks

## Error Categories

### Syntax Errors
| Error Type | Description | Example |
|------------|-------------|---------|
| **Missing Braces** | Unmatched opening/closing braces | `\section{Introduction` |
| **Undefined Commands** | Commands not defined | `\invalidcommand{text}` |
| **Environment Mismatch** | Mismatched begin/end | `\begin{equation}...\end{align}` |
| **Invalid Arguments** | Wrong argument structure | `\frac{a}{b}{c}` |

### Warning Categories (Strict Mode)
| Warning Type | Description | Example |
|--------------|-------------|---------|
| **Deprecated Packages** | Outdated package usage | `\usepackage{epsfig}` |
| **Missing Packages** | Recommended packages | Missing `microtype` |
| **Style Issues** | Typography recommendations | Multiple spaces |
| **Best Practices** | LaTeX best practices | Using `$$` instead of `\[` |

## Performance Characteristics

### Benchmark Data

| Document Type | Quick Mode | Strict Mode | Memory Usage |
|---------------|------------|-------------|--------------|
| Simple Paper | 0.05s | 0.15s | 5-10MB |
| Research Paper | 0.08s | 0.25s | 10-20MB |
| Technical Report | 0.12s | 0.35s | 15-30MB |
| Thesis Chapter | 0.18s | 0.50s | 20-40MB |

### Validation Speed vs Compilation

```python
# Validation is ~10x faster than compilation
validation_time = 0.05  # seconds
compilation_time = 0.50  # seconds
speedup = compilation_time / validation_time  # 10x faster
```

## Integration Patterns

### Pre-compilation Validation

```python
async def safe_compilation(tex_file: str):
    """Validate before compiling"""
    
    # Quick validation check
    validation = validate_latex(tex_file)
    if not validation.is_valid:
        return {
            "success": False,
            "stage": "validation",
            "errors": validation.errors
        }
    
    # Proceed with compilation
    result = await compile_latex(tex_file)
    return {
        "success": result.success,
        "stage": "compilation",
        "output": result.output_path if result.success else None
    }
```

### Continuous Validation

```python
import time
from pathlib import Path

def watch_and_validate(tex_file: str, interval: float = 1.0):
    """Continuously validate file changes"""
    
    last_modified = 0
    last_validation = None
    
    while True:
        current_modified = Path(tex_file).stat().st_mtime
        
        if current_modified != last_modified:
            validation = validate_latex(tex_file)
            
            if validation.is_valid and not last_validation:
                print("✅ Document became valid")
            elif not validation.is_valid and last_validation:
                print("❌ Document became invalid")
                for error in validation.errors:
                    print(f"  - {error}")
            
            last_modified = current_modified
            last_validation = validation.is_valid
        
        time.sleep(interval)
```

### Batch Validation

```python
def validate_project(directory: str):
    """Validate all LaTeX files in project"""
    
    tex_files = Path(directory).glob("**/*.tex")
    results = {}
    
    for tex_file in tex_files:
        validation = validate_latex(str(tex_file))
        results[str(tex_file)] = {
            "valid": validation.is_valid,
            "errors": len(validation.errors),
            "warnings": len(validation.warnings)
        }
    
    # Summary
    total_files = len(results)
    valid_files = sum(1 for r in results.values() if r["valid"])
    total_errors = sum(r["errors"] for r in results.values())
    
    print(f"📊 Project Validation Summary:")
    print(f"  - Files: {total_files}")
    print(f"  - Valid: {valid_files}/{total_files}")
    print(f"  - Total errors: {total_errors}")
    
    return results
```

## Error Recovery Suggestions

### Common Fixes

```python
def suggest_fix(error: str) -> str:
    """Suggest fixes for common validation errors"""
    
    fixes = {
        "Missing closing brace": "Add closing brace '}' to match opening brace",
        "Undefined command": "Check command spelling or add required package",
        "Environment mismatch": "Ensure \\begin{env} matches \\end{env}",
        "Invalid arguments": "Check command syntax and argument count"
    }
    
    for pattern, fix in fixes.items():
        if pattern in error:
            return fix
    
    return "Check LaTeX syntax and documentation"

# Usage
validation = validate_latex("document.tex")
if not validation.is_valid:
    for error in validation.errors:
        suggestion = suggest_fix(error)
        print(f"Error: {error}")
        print(f"Fix: {suggestion}")
```

## Best Practices

### Development Workflow
1. **Validate frequently** - Run validation after each significant change
2. **Use quick mode** for rapid iteration
3. **Use strict mode** before final compilation
4. **Fix errors incrementally** - Address one error at a time

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Validate LaTeX
  run: |
    python -c "
    from mcp_latex_tools.tools.validate import validate_latex
    import sys
    
    result = validate_latex('document.tex', mode='strict')
    if not result.is_valid:
        print('Validation failed:')
        for error in result.errors:
            print(f'  - {error}')
        sys.exit(1)
    print('✅ Validation passed')
    "
```

### Editor Integration
```python
# VS Code extension integration
def on_document_change(document_path: str):
    """Called when document changes in editor"""
    
    validation = validate_latex(document_path)
    
    # Update editor diagnostics
    diagnostics = []
    for error in validation.errors:
        diagnostics.append({
            "severity": "error",
            "message": error,
            "source": "mcp-latex-tools"
        })
    
    # Send to editor
    update_editor_diagnostics(document_path, diagnostics)
```

---

**This tool provides instant LaTeX validation feedback, enabling rapid development cycles and early error detection for both human developers and automated workflows.** ✅