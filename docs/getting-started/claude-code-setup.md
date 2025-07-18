# Claude Code Setup Guide

## Overview

This guide walks you through configuring Claude Code to use the MCP LaTeX Tools server for seamless LaTeX document compilation and management.

## Prerequisites

- ✅ MCP LaTeX Tools installed ([Installation Guide](installation.md))
- ✅ Claude Code CLI installed and running
- ✅ LaTeX distribution available on your system

## Configuration Steps

### Step 1: Locate Configuration File

Claude Code configuration is stored in a JSON file at:

**macOS:**
```bash
~/.config/claude-code/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/claude-code/claude_desktop_config.json
```

### Step 2: Create Configuration Directory

If the configuration directory doesn't exist, create it:

```bash
# macOS/Linux
mkdir -p ~/.config/claude-code/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Claude"
```

### Step 3: Configure MCP Server

Create or edit the configuration file with the following content:

```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-latex-tools/src/mcp_latex_tools/server.py"],
      "env": {}
    }
  }
}
```

**Important**: Replace `/absolute/path/to/mcp-latex-tools/` with the actual absolute path to your installation.

### Step 4: Find Your Installation Path

To find the correct path to use:

```bash
# Navigate to your mcp-latex-tools directory
cd /path/to/mcp-latex-tools

# Get absolute path
pwd

# Expected output: /home/username/code/mcp-latex-tools
```

Use this path in your configuration:
```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "python",
      "args": ["/home/username/code/mcp-latex-tools/src/mcp_latex_tools/server.py"],
      "env": {}
    }
  }
}
```

### Step 5: Restart Claude Code

1. **Close Claude Code completely**
2. **Restart Claude Code**
3. **Wait for initialization** (may take 10-15 seconds)

## Verification

### Test 1: List Available Tools

In Claude Code, ask:
```
Can you list the available MCP tools?
```

**Expected Response:**
```
I can see the following MCP tools available:

1. compile_latex - Compile LaTeX documents to PDF with comprehensive error handling
2. validate_latex - Validate LaTeX syntax without full compilation  
3. pdf_info - Extract PDF metadata and document information
4. cleanup - Clean LaTeX auxiliary files

All tools are working properly!
```

### Test 2: Simple Compilation Test

Create a test document:
```
Can you create a simple LaTeX document and compile it?
```

**Expected Response:**
Claude Code should:
1. Create a `.tex` file
2. Use the `compile_latex` tool
3. Show compilation results
4. Confirm PDF creation

### Test 3: Complete Workflow Test

```
Can you demonstrate all four LaTeX tools with a test document?
```

**Expected Response:**
Claude Code should demonstrate:
1. ✅ `validate_latex` - Syntax validation
2. ✅ `compile_latex` - PDF compilation  
3. ✅ `pdf_info` - Metadata extraction
4. ✅ `cleanup` - Auxiliary file cleanup

## Advanced Configuration

### Multiple Python Environments

If using virtual environments or conda:

```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "/path/to/venv/bin/python",
      "args": ["/absolute/path/to/mcp-latex-tools/src/mcp_latex_tools/server.py"],
      "env": {
        "VIRTUAL_ENV": "/path/to/venv"
      }
    }
  }
}
```

### UV Environment Setup

If using UV (recommended):

```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "uv",
      "args": ["run", "python", "src/mcp_latex_tools/server.py"],
      "env": {},
      "cwd": "/absolute/path/to/mcp-latex-tools"
    }
  }
}
```

### Environment Variables

For custom LaTeX installations:

```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-latex-tools/src/mcp_latex_tools/server.py"],
      "env": {
        "PATH": "/usr/local/texlive/2023/bin/x86_64-linux:$PATH",
        "TEXMFHOME": "/home/username/texmf"
      }
    }
  }
}
```

## Troubleshooting

### Issue 1: MCP Server Not Found

**Symptoms:**
```
No MCP tools available
```

**Solutions:**
1. **Check file path** - Ensure absolute path is correct
2. **Verify installation** - Test server manually
3. **Check permissions** - Ensure files are executable

```bash
# Test server manually
python /absolute/path/to/mcp-latex-tools/src/mcp_latex_tools/server.py

# Check permissions
ls -la /absolute/path/to/mcp-latex-tools/src/mcp_latex_tools/server.py
```

### Issue 2: Python Not Found

**Symptoms:**
```
Command 'python' not found
```

**Solutions:**
1. **Use full Python path**:
```json
{
  "command": "/usr/bin/python3",
  "args": ["..."]
}
```

2. **Check Python installation**:
```bash
which python
which python3
```

### Issue 3: Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Solutions:**
1. **Verify dependencies installed**:
```bash
cd /path/to/mcp-latex-tools
uv run python -c "import mcp; print('MCP installed')"
```

2. **Use UV runner**:
```json
{
  "command": "uv",
  "args": ["run", "python", "src/mcp_latex_tools/server.py"],
  "cwd": "/absolute/path/to/mcp-latex-tools"
}
```

### Issue 4: LaTeX Not Found

**Symptoms:**
```
LaTeX compilation failed: pdflatex not found
```

**Solutions:**
1. **Add LaTeX to PATH**:
```json
{
  "env": {
    "PATH": "/usr/local/texlive/2023/bin/x86_64-linux:$PATH"
  }
}
```

2. **Test LaTeX installation**:
```bash
pdflatex --version
```

### Issue 5: Permission Denied

**Symptoms:**
```
Permission denied: '/path/to/server.py'
```

**Solutions:**
1. **Make script executable**:
```bash
chmod +x /path/to/mcp-latex-tools/src/mcp_latex_tools/server.py
```

2. **Use explicit python call**:
```json
{
  "command": "python",
  "args": ["/path/to/server.py"]
}
```

## Configuration Examples

### Basic Setup
```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "python",
      "args": ["/home/user/mcp-latex-tools/src/mcp_latex_tools/server.py"],
      "env": {}
    }
  }
}
```

### Production Setup with UV
```json
{
  "mcpServers": {
    "latex-tools": {
      "command": "uv",
      "args": ["run", "python", "src/mcp_latex_tools/server.py"],
      "env": {
        "PYTHONPATH": "/home/user/mcp-latex-tools/src"
      },
      "cwd": "/home/user/mcp-latex-tools"
    }
  }
}
```

### Development Setup
```json
{
  "mcpServers": {
    "latex-tools-dev": {
      "command": "python",
      "args": ["/home/user/dev/mcp-latex-tools/src/mcp_latex_tools/server.py"],
      "env": {
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Validation Checklist

Before proceeding, ensure:

- [ ] Configuration file exists and is valid JSON
- [ ] Absolute paths are used (not relative paths)
- [ ] Python executable is accessible
- [ ] MCP LaTeX Tools dependencies are installed
- [ ] LaTeX distribution is available
- [ ] File permissions are correct
- [ ] Claude Code has been restarted

## Next Steps

Once Claude Code is configured:

1. **[First Compilation](first-compilation.md)** - Create your first LaTeX document
2. **[API Reference](../api-reference/)** - Explore all available tools
3. **[Integration Patterns](../examples/integration-patterns.md)** - Advanced usage examples

---

**Claude Code is now ready to compile LaTeX documents with MCP LaTeX Tools!** 🚀