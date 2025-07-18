# First LaTeX Compilation

## Overview

This guide walks you through creating and compiling your first LaTeX document using MCP LaTeX Tools with Claude Code.

## Quick Start

### Step 1: Create Your First Document

Ask Claude Code:
```
Can you create a simple LaTeX document about "Getting Started with LaTeX" and compile it?
```

Claude Code will:
1. Create a `.tex` file with proper LaTeX structure
2. Use `validate_latex` to check syntax
3. Use `compile_latex` to generate PDF
4. Show compilation results and PDF metadata

### Step 2: Verify Success

You should see output similar to:
```
✅ Document validated successfully
✅ Compilation completed in 0.25 seconds
📄 PDF created: getting_started.pdf (2 pages, 156.3 KB)
```

## Detailed Walkthrough

### Creating a LaTeX Document

Let's create a sample document step by step:

**Ask Claude Code:**
```
Please create a LaTeX document with the following content:
- Title: "My First LaTeX Document"
- Author: "Your Name"
- Abstract about LaTeX benefits
- Introduction section
- Mathematical equation example
- Conclusion section

Then validate and compile it.
```

**Expected LaTeX Content:**
```latex
\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}

\title{My First LaTeX Document}
\author{Your Name}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
LaTeX is a high-quality typesetting system that produces professional documents with excellent typography, particularly suited for academic and technical writing.
\end{abstract}

\section{Introduction}

Welcome to LaTeX! This document demonstrates basic LaTeX features including sections, mathematics, and professional formatting.

\section{Mathematical Example}

LaTeX excels at typesetting mathematics. Here's the famous Euler's formula:

\begin{equation}
e^{i\pi} + 1 = 0
\end{equation}

This equation beautifully connects five fundamental mathematical constants.

\section{Conclusion}

LaTeX provides powerful tools for creating professional documents with consistent formatting and beautiful typography.

\end{document}
```

### Validation Process

Claude Code will use the `validate_latex` tool:

**Tool Call:**
```json
{
  "tool": "validate_latex",
  "parameters": {
    "tex_path": "my_first_document.tex"
  }
}
```

**Expected Result:**
```
✅ Validation successful: No syntax errors found
```

### Compilation Process

Claude Code will use the `compile_latex` tool:

**Tool Call:**
```json
{
  "tool": "compile_latex", 
  "parameters": {
    "tex_path": "my_first_document.tex"
  }
}
```

**Expected Result:**
```
✅ Compilation successful
📄 Output: my_first_document.pdf
⏱️ Time: 0.34 seconds
📊 Size: 187.2 KB
```

### PDF Analysis

Claude Code will use the `pdf_info` tool:

**Tool Call:**
```json
{
  "tool": "pdf_info",
  "parameters": {
    "pdf_path": "my_first_document.pdf"
  }
}
```

**Expected Result:**
```
📄 PDF Analysis:
- Pages: 2
- Size: 187.2 KB  
- Format: Letter (612×792 pt)
- PDF Version: 1.4
- Created: 2025-07-18T15:30:45-07:00
```

### Cleanup

Claude Code will use the `cleanup` tool:

**Tool Call:**
```json
{
  "tool": "cleanup",
  "parameters": {
    "tex_path": "my_first_document.tex"
  }
}
```

**Expected Result:**
```
🧹 Cleaned 3 auxiliary files:
- my_first_document.aux
- my_first_document.log  
- my_first_document.out
```

## Common First-Time Issues

### Issue 1: Syntax Errors

**Problem:**
```
❌ Validation failed: Missing closing brace on line 12
```

**Solution:**
Claude Code will identify and fix syntax errors automatically, or provide clear guidance:
```
The issue is on line 12 where \section{Introduction is missing a closing brace.
Fixed version: \section{Introduction}
```

### Issue 2: Missing Packages

**Problem:**
```
❌ Compilation failed: Package 'amsmath' not found
```

**Solution:**
Claude Code will suggest installing the package or using alternative approaches:
```
The amsmath package is required for advanced mathematics. 
Options:
1. Install texlive-latex-extra package
2. Use basic math mode without amsmath
```

### Issue 3: File Permissions

**Problem:**
```
❌ Permission denied writing to directory
```

**Solution:**
```
Let me create the document in your current directory with proper permissions.
```

Claude Code will handle file creation in an accessible location.

## Interactive Features

### Real-time Editing

Ask Claude Code to make changes:
```
Can you add a new section about "LaTeX Benefits" with a bulleted list?
```

Claude Code will:
1. Modify the LaTeX source
2. Re-validate the document
3. Re-compile if requested
4. Show the changes made

### Multiple Formats

Try different document types:
```
Can you create a presentation version using Beamer?
```

```
Can you create a formal letter format?
```

```
Can you create a scientific paper template?
```

### Advanced Mathematics

Explore mathematical typesetting:
```
Can you add more complex equations like matrices and integrals?
```

Claude Code will add sophisticated mathematical content and ensure proper compilation.

## Building Your Skills

### Exercise 1: Personal Document

Create a document about yourself:
```
Create a LaTeX document that includes:
- Your name and contact information
- Education section with a table
- Skills section with itemized lists  
- A simple chart or figure
- Professional formatting
```

### Exercise 2: Technical Report

```
Create a technical report template with:
- Executive summary
- Multiple sections and subsections
- Figure placeholders
- Bibliography section
- Appendix
```

### Exercise 3: Academic Paper

```
Create an academic paper format with:
- Abstract and keywords
- Literature review section
- Methodology section
- Results with tables and figures
- Conclusion and references
```

## Understanding the Workflow

### Complete LaTeX Workflow

The MCP LaTeX Tools provide a complete workflow:

1. **📝 Create** - Write LaTeX content
2. **✅ Validate** - Check syntax (`validate_latex`)
3. **🔧 Compile** - Generate PDF (`compile_latex`)
4. **📊 Analyze** - Check metadata (`pdf_info`)
5. **🧹 Clean** - Remove auxiliary files (`cleanup`)

### Performance Expectations

| Document Type | Validation | Compilation | Total Time |
|---------------|------------|-------------|------------|
| Simple (1-2 pages) | < 0.1s | 0.1-0.3s | < 0.4s |
| Standard (3-10 pages) | < 0.1s | 0.2-0.6s | < 0.7s |
| Complex (10+ pages) | < 0.2s | 0.5-1.5s | < 1.7s |

### Quality Assurance

Each compilation includes:
- ✅ Syntax validation
- ✅ Error detection and reporting
- ✅ Performance monitoring
- ✅ Output verification
- ✅ Automatic cleanup

## Next Steps

### Explore Advanced Features

1. **[API Reference](../api-reference/)** - Detailed tool documentation
2. **[Integration Patterns](../examples/integration-patterns.md)** - Advanced workflows
3. **[Troubleshooting](../troubleshooting/)** - Common issues and solutions

### Try Different Document Types

- **Research Papers** - Academic formatting with citations
- **Presentations** - Beamer slides with animations  
- **Books** - Multi-chapter documents with cross-references
- **Letters** - Professional correspondence
- **Resumes** - Professional CV formatting

### Advanced LaTeX Features

Ask Claude Code to demonstrate:
- **Bibliography management** with BibTeX
- **Cross-references** for figures and tables
- **Custom commands** and environments
- **Package integration** for specialized formatting
- **Multi-language** document support

## Troubleshooting Tips

### If Compilation Fails

1. **Check syntax** with validation first
2. **Review error messages** for specific issues
3. **Try simpler content** to isolate problems
4. **Ask Claude Code** for specific help with errors

### If PDF Looks Wrong

1. **Check document class** and formatting options
2. **Verify page dimensions** with `pdf_info`
3. **Review package usage** for conflicts
4. **Ask for layout adjustments**

### If Tools Don't Work

1. **Verify MCP server** is running correctly
2. **Check file paths** are accessible
3. **Restart Claude Code** if needed
4. **Review configuration** in setup guide

---

**Congratulations! You've successfully compiled your first LaTeX document with MCP LaTeX Tools and Claude Code.** 🎉

The combination provides a powerful, intelligent LaTeX development environment that handles the technical details while you focus on content creation.

Ready to create professional documents with LaTeX and Claude Code! 📚