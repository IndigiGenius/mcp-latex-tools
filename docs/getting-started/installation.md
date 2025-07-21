# Installation Guide

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **LaTeX Distribution**: TeX Live, MiKTeX, or MacTeX
- **Claude Code**: Latest version with MCP support

### Platform-Specific LaTeX Installation

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install texlive-latex-base texlive-latex-extra texlive-fonts-recommended
```

#### macOS
```bash
# Using Homebrew
brew install --cask mactex

# Or download from https://www.tug.org/mactex/
```

#### Windows
```bash
# Download and install MiKTeX from https://miktex.org/download
# Or install TeX Live from https://www.tug.org/texlive/
```

## Installation Methods

### Method 1: From Source (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/IndigiGenius/mcp-latex-tools.git
cd mcp-latex-tools

# 2. Install UV (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv sync

# 4. Verify installation
uv run python src/mcp_latex_tools/server.py --help
```

### Method 2: Development Installation

```bash
# For contributors and developers
git clone https://github.com/IndigiGenius/mcp-latex-tools.git
cd mcp-latex-tools

# Install in development mode
uv sync --dev

# Run tests to verify
uv run pytest
```

## Claude Code Integration

### Step 1: Configure MCP Server

Create or edit your Claude Code configuration file:

**Location**: `~/.config/claude-code/claude_desktop_config.json`

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

### Step 2: Restart Claude Code

```bash
# Close Claude Code completely
# Restart Claude Code
```

### Step 3: Verify Integration

In Claude Code, ask:
```
Can you list the available MCP tools?
```

Expected response should show:
- compile_latex
- validate_latex  
- pdf_info
- cleanup

## Verification Tests

### Test 1: Basic Server Functionality

```bash
# Test the server directly
cd mcp-latex-tools
uv run python src/mcp_latex_tools/server.py
```

### Test 2: MCP Client Test

```bash
# Run the comprehensive MCP client test
uv run python test_mcp_client.py
```

Expected output:
```
🔍 Testing MCP Server with Official Client
==================================================
✅ Server initialized: MCP LaTeX Tools
✅ Found 4 tools: compile_latex, validate_latex, pdf_info, cleanup
✅ Tool call result: Compilation successful...
```

### Test 3: LaTeX Compilation Test

Create a test file `test.tex`:
```latex
\documentclass{article}
\begin{document}
Hello, LaTeX!
\end{document}
```

Test compilation:
```bash
uv run python -c "
import asyncio
from src.mcp_latex_tools.tools.compile import compile_latex
result = compile_latex('test.tex')
print('✅ Success!' if result.success else '❌ Failed')
"
```

## Troubleshooting Installation

### Common Issues

#### Issue 1: Python Version Compatibility
```bash
# Check Python version
python --version

# Must be 3.8 or higher
# Install newer Python if needed
```

#### Issue 2: LaTeX Not Found
```bash
# Check LaTeX installation
pdflatex --version

# If not found, install LaTeX distribution
```

#### Issue 3: Permission Errors
```bash
# Fix permissions
chmod +x src/mcp_latex_tools/server.py

# Or run with explicit python
python src/mcp_latex_tools/server.py
```

#### Issue 4: Claude Code Configuration
```bash
# Check config file location
ls ~/.config/claude-code/claude_desktop_config.json

# Create directory if needed
mkdir -p ~/.config/claude-code/
```

#### Issue 5: MCP Server Not Starting
```bash
# Check server logs
uv run python src/mcp_latex_tools/server.py --verbose

# Check for port conflicts
lsof -i :8080  # If using specific port
```

### Diagnostic Commands

```bash
# System information
uv run python -c "
import sys
print(f'Python: {sys.version}')
import subprocess
try:
    result = subprocess.run(['pdflatex', '--version'], capture_output=True, text=True)
    print('LaTeX: Available')
except:
    print('LaTeX: Not found')
"

# Package versions
uv run python -c "
import pkg_resources
packages = ['mcp', 'pypdf', 'pytest']
for pkg in packages:
    try:
        version = pkg_resources.get_distribution(pkg).version
        print(f'{pkg}: {version}')
    except:
        print(f'{pkg}: Not installed')
"
```

## Next Steps

After successful installation:

1. **[Claude Code Setup](claude-code-setup.md)** - Configure Claude Code integration
2. **[First Compilation](first-compilation.md)** - Your first LaTeX document
3. **[API Reference](../api-reference/)** - Complete tool documentation

## Support

If you encounter issues:

1. **Check Prerequisites**: Ensure Python 3.8+ and LaTeX are installed
2. **Verify Paths**: Use absolute paths in Claude Code configuration
3. **Test Components**: Run individual verification tests
4. **Check Issues**: [GitHub Issues](https://github.com/IndigiGenius/mcp-latex-tools/issues)

---

**Installation complete! Ready to compile LaTeX documents with Claude Code.** 🚀