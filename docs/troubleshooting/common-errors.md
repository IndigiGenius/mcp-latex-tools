# Common Errors and Solutions

## Overview

This guide covers the most common issues encountered when using MCP LaTeX Tools and provides step-by-step solutions.

## Quick Diagnosis

### Identify Your Issue Type

| Symptom | Issue Type | Quick Fix |
|---------|------------|-----------|
| "No MCP tools available" | Configuration | Check [Claude Code Setup](../getting-started/claude-code-setup.md) |
| "Command not found: pdflatex" | LaTeX Installation | Install LaTeX distribution |
| "Permission denied" | File Permissions | Check file/directory permissions |
| "Module not found: mcp" | Dependencies | Run `uv sync` in project directory |
| "Compilation failed" | LaTeX Syntax | Use `validate_latex` to find errors |

## Configuration Issues

### Issue: MCP Server Not Found

**Symptoms:**
```
Claude Code says: "No MCP tools are currently available"
```

**Diagnosis:**
1. Check if server starts manually:
```bash
cd /path/to/mcp-latex-tools
uv run python src/mcp_latex_tools/server.py
```

2. Verify configuration file exists:
```bash
# macOS/Linux
cat ~/.config/claude-code/claude_desktop_config.json

# Windows
type %APPDATA%\Claude\claude_desktop_config.json
```

**Solutions:**

**Solution 1: Fix Configuration Path**
```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "python",
      "args": ["/ABSOLUTE/path/to/mcp-latex-tools/src/mcp_latex_tools/server.py"],
      "env": {}
    }
  }
}
```
*Note: Must use absolute path, not relative path*

**Solution 2: Use UV Runner**
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

**Solution 3: Check Permissions**
```bash
chmod +x /path/to/mcp-latex-tools/src/mcp_latex_tools/server.py
```

### Issue: Python Module Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'mcp'
ImportError: cannot import name 'TextContent'
```

**Diagnosis:**
```bash
cd /path/to/mcp-latex-tools
uv run python -c "import mcp; print('MCP available')"
```

**Solutions:**

**Solution 1: Reinstall Dependencies**
```bash
cd /path/to/mcp-latex-tools
uv sync --reinstall
```

**Solution 2: Check Virtual Environment**
```bash
# Find correct Python path
uv run which python

# Use full path in configuration
{
  "command": "/path/to/.venv/bin/python",
  "args": ["src/mcp_latex_tools/server.py"]
}
```

**Solution 3: Force UV Usage**
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

## LaTeX Installation Issues

### Issue: LaTeX Not Found

**Symptoms:**
```
❌ Compilation failed: pdflatex not found
❌ Command 'pdflatex' not found
```

**Diagnosis:**
```bash
pdflatex --version
which pdflatex
echo $PATH
```

**Solutions:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install texlive-latex-base texlive-latex-extra texlive-fonts-recommended
```

**macOS:**
```bash
# Option 1: Homebrew
brew install --cask mactex

# Option 2: Manual download
# Download from https://tug.org/mactex/
```

**Windows:**
```powershell
# Download and install MiKTeX from https://miktex.org/download
# Or install TeX Live from https://tug.org/texlive/
```

**Add LaTeX to PATH:**
```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "python",
      "args": ["src/mcp_latex_tools/server.py"],
      "env": {
        "PATH": "/usr/local/texlive/2023/bin/x86_64-linux:$PATH"
      }
    }
  }
}
```

### Issue: Missing LaTeX Packages

**Symptoms:**
```
❌ Package 'amsmath' not found
❌ File 'inputenc.sty' not found
```

**Solutions:**

**Ubuntu/Debian:**
```bash
# Install common packages
sudo apt install texlive-latex-extra texlive-science texlive-pictures

# For specific packages
sudo apt install texlive-fonts-extra texlive-lang-european
```

**macOS (MacTeX):**
```bash
# Usually includes all packages, but can install additional:
sudo tlmgr update --self
sudo tlmgr install <package-name>
```

**Windows (MiKTeX):**
```powershell
# Packages install automatically, but can force:
mpm --install=<package-name>
```

## Compilation Issues

### Issue: LaTeX Syntax Errors

**Symptoms:**
```
❌ Validation failed: Missing closing brace on line 15
❌ Compilation failed: Undefined control sequence
```

**Diagnosis:**
Use the validation tool first:
```
Ask Claude Code: "Can you validate this LaTeX file and show me any errors?"
```

**Common Syntax Fixes:**

**Missing Braces:**
```latex
% ❌ Wrong
\section{Introduction

% ✅ Correct  
\section{Introduction}
```

**Undefined Commands:**
```latex
% ❌ Wrong
\invalidcommand{text}

% ✅ Correct - check spelling
\textbf{text}
```

**Environment Mismatch:**
```latex
% ❌ Wrong
\begin{equation}
E = mc^2
\end{align}

% ✅ Correct
\begin{equation}
E = mc^2
\end{equation}
```

**Missing Packages:**
```latex
% ❌ Wrong - using \cite without cite package
\cite{author2023}

% ✅ Correct
\usepackage{cite}
\cite{author2023}
```

### Issue: Compilation Timeouts

**Symptoms:**
```
❌ Compilation timed out after 30 seconds
❌ LaTeX appears to be in infinite loop
```

**Solutions:**

**Solution 1: Increase Timeout**
```
Ask Claude Code: "Can you compile this with a longer timeout of 60 seconds?"
```

**Solution 2: Check for Infinite Loops**
```latex
% Common causes:
% - Recursive macro definitions
% - Missing \end{document}
% - Circular package dependencies
```

**Solution 3: Simplify Document**
```
Ask Claude Code: "Can you create a minimal version of this document to test compilation?"
```

### Issue: Font or Encoding Problems

**Symptoms:**
```
❌ Font 'cmr10' not found
❌ Unicode character not displayable
```

**Solutions:**

**Font Issues:**
```bash
# Rebuild font cache
sudo fc-cache -fv
sudo texhash
```

**Encoding Issues:**
```latex
% ✅ Use proper encoding
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
```

## File and Permission Issues

### Issue: Permission Denied

**Symptoms:**
```
❌ Permission denied: cannot write to directory
❌ Permission denied: '/path/to/document.tex'
```

**Solutions:**

**Fix File Permissions:**
```bash
chmod 644 document.tex
chmod 755 /path/to/directory
```

**Fix Directory Permissions:**
```bash
# Make directory writable
chmod 755 /path/to/working/directory

# Change ownership if needed
sudo chown $USER:$USER /path/to/directory
```

**Use Home Directory:**
```
Ask Claude Code: "Can you create the document in my home directory instead?"
```

### Issue: File Not Found

**Symptoms:**
```
❌ File 'document.tex' not found
❌ Cannot open file for reading
```

**Solutions:**

**Check File Exists:**
```bash
ls -la document.tex
pwd  # Check current directory
```

**Use Absolute Paths:**
```
Ask Claude Code: "Can you use the absolute path: /full/path/to/document.tex?"
```

**Check Working Directory:**
```
Ask Claude Code: "What is the current working directory? Can you list the files here?"
```

## Performance Issues

### Issue: Slow Compilation

**Symptoms:**
```
Compilation takes > 5 seconds for simple documents
Memory usage very high during compilation
```

**Solutions:**

**Optimize LaTeX Code:**
```latex
% Use efficient packages
\usepackage[final]{microtype}
\usepackage{graphicx}

% Avoid heavy packages if not needed
% \usepackage{tikz}  % Only if actually using TikZ
```

**Check System Resources:**
```bash
# Monitor during compilation
top -p $(pgrep pdflatex)
df -h  # Check disk space
```

**Use Faster Compilation:**
```
Ask Claude Code: "Can you compile this in draft mode for faster processing?"
```

### Issue: Large PDF Files

**Symptoms:**
```
PDF files much larger than expected
PDF > 10MB for simple documents
```

**Solutions:**

**Optimize Images:**
```latex
% Compress images
\usepackage{graphicx}
\includegraphics[width=0.5\textwidth,keepaspectratio]{image.pdf}
```

**Use PDF Compression:**
```latex
% Add to preamble
\pdfcompresslevel=9
\pdfobjcompresslevel=3
```

**Check PDF Info:**
```
Ask Claude Code: "Can you analyze this PDF and tell me why it's so large?"
```

## Tool-Specific Issues

### Issue: validate_latex Not Working

**Symptoms:**
```
❌ Validation returns no results
❌ Validation tool reports errors incorrectly
```

**Solutions:**

**Test Direct Tool Usage:**
```bash
cd /path/to/mcp-latex-tools
uv run python -c "
from src.mcp_latex_tools.tools.validate import validate_latex
result = validate_latex('test.tex')
print(result)
"
```

**Check File Encoding:**
```bash
file -bi document.tex
# Should show: text/x-tex; charset=utf-8
```

### Issue: cleanup Tool Not Working

**Symptoms:**
```
❌ Auxiliary files not removed
❌ Cleanup reports success but files remain
```

**Solutions:**

**Check File Permissions:**
```bash
ls -la *.aux *.log *.out
# Ensure files are writable
```

**Test Manual Cleanup:**
```bash
cd /path/to/document/directory
rm -f *.aux *.log *.out *.fls *.fdb_latexmk
```

**Use Dry Run First:**
```
Ask Claude Code: "Can you show me what cleanup would remove with a dry run?"
```

## Advanced Diagnostics

### Debug Mode

Enable debug logging in configuration:
```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "python",
      "args": ["src/mcp_latex_tools/server.py"],
      "env": {
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Manual Testing

Test each component independently:

**1. Test MCP Server:**
```bash
cd /path/to/mcp-latex-tools
uv run python src/mcp_latex_tools/server.py
```

**2. Test LaTeX Tools:**
```bash
uv run python test_mcp_client.py
```

**3. Test LaTeX Installation:**
```bash
echo '\documentclass{article}\begin{document}Hello\end{document}' > test.tex
pdflatex test.tex
```

### Log Analysis

Check Claude Code logs for detailed error information:
- Look for MCP server startup messages
- Check for tool registration success
- Monitor tool call/response patterns

## Getting Help

### Collect Diagnostic Information

When reporting issues, include:

1. **System Information:**
```bash
uname -a
python --version
pdflatex --version
```

2. **Configuration:**
```bash
cat ~/.config/claude-code/claude_desktop_config.json
```

3. **Error Messages:**
- Full error output from Claude Code
- MCP server logs if available
- LaTeX compilation logs

4. **Minimal Example:**
- Simplest LaTeX document that reproduces the issue
- Exact steps taken

### Support Resources

- **GitHub Issues**: [Report bugs and get help](https://github.com/IndigiGenius/mcp-latex-tools/issues)
- **Documentation**: [Complete documentation](../README.md)
- **Examples**: [Working examples](../examples/)

---

**Most issues can be resolved by checking configuration, dependencies, and file permissions. The tools are designed to provide clear error messages to guide troubleshooting.** 🔧