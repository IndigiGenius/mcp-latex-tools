#!/usr/bin/env python3
"""Test LaTeX tools directly without MCP protocol."""

import asyncio
import tempfile
from pathlib import Path

from mcp_latex_tools.tools.compile import compile_latex
from mcp_latex_tools.tools.validate import validate_latex
from mcp_latex_tools.tools.pdf_info import extract_pdf_info
from mcp_latex_tools.tools.cleanup import clean_latex

def test_latex_tools():
    """Test LaTeX tools directly."""
    print("🚀 Testing LaTeX Tools Directly")
    print("=" * 50)
    
    # Create a test LaTeX file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
        tmp.write(r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\title{Test Document}
\author{MCP LaTeX Tools}
\date{\today}

\begin{document}
\maketitle

\section{Introduction}
This is a test document compiled by the MCP LaTeX Tools.

\subsection{Features}
\begin{itemize}
    \item Direct compilation test
    \item PDF generation
    \item Metadata extraction
\end{itemize}

\section{Math Example}
Here's a simple equation:
\[
    E = mc^2
\]

\end{document}
""")
        tmp.flush()
        tex_path = Path(tmp.name)
    
    print(f"\n📄 Created test file: {tex_path}")
    
    # Test 1: Validate LaTeX
    print("\n📋 Test 1: Validate LaTeX")
    try:
        validation_result = validate_latex(str(tex_path))
        if validation_result.is_valid:
            print("✅ LaTeX validation passed")
        else:
            print(f"❌ LaTeX validation failed: {validation_result.errors}")
    except Exception as e:
        print(f"❌ Validation error: {e}")
    
    # Test 2: Compile LaTeX
    print("\n📝 Test 2: Compile LaTeX")
    try:
        compile_result = compile_latex(str(tex_path), timeout=30)
        if compile_result.success:
            print(f"✅ LaTeX compilation successful!")
            print(f"   Output: {compile_result.output_path}")
            print(f"   Compile time: {compile_result.compilation_time_seconds:.2f}s")
            pdf_path = compile_result.output_path
        else:
            print(f"❌ LaTeX compilation failed: {compile_result.error_message}")
            pdf_path = None
    except Exception as e:
        print(f"❌ Compilation error: {e}")
        pdf_path = None
    
    # Test 3: Extract PDF info
    if pdf_path and Path(pdf_path).exists():
        print("\n📊 Test 3: Extract PDF Info")
        try:
            pdf_info = extract_pdf_info(pdf_path)
            print(f"✅ PDF info extracted:")
            print(f"   Pages: {pdf_info.page_count}")
            print(f"   Size: {pdf_info.file_size_bytes:,} bytes")
            print(f"   Created: {pdf_info.creation_date}")
        except Exception as e:
            print(f"❌ PDF info error: {e}")
    
    # Test 4: Cleanup
    print("\n🧹 Test 4: Cleanup auxiliary files")
    try:
        cleanup_result = clean_latex(str(tex_path), dry_run=True)
        print(f"✅ Would clean {cleanup_result.cleaned_files_count} files:")
        for file in cleanup_result.would_clean_files[:5]:  # Show first 5
            print(f"   • {file}")
        if len(cleanup_result.would_clean_files) > 5:
            print(f"   • ... and {len(cleanup_result.would_clean_files) - 5} more")
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    
    # Clean up test files
    tex_path.unlink(missing_ok=True)
    if pdf_path:
        Path(pdf_path).unlink(missing_ok=True)
    
    print("\n🎉 Direct Testing Complete!")

if __name__ == "__main__":
    test_latex_tools()