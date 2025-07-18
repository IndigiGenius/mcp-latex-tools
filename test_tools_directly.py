#!/usr/bin/env python3
"""Test the MCP LaTeX Tools directly without the server layer."""

import tempfile
from pathlib import Path
import sys
import asyncio

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_latex_tools.tools.compile import compile_latex
from mcp_latex_tools.tools.validate import validate_latex
from mcp_latex_tools.tools.pdf_info import extract_pdf_info
from mcp_latex_tools.tools.cleanup import clean_latex

def test_latex_tools():
    """Test the LaTeX tools directly."""
    print("🚀 Testing MCP LaTeX Tools (Direct)")
    print("=" * 50)
    
    # Test 1: Create a simple LaTeX document
    print("\n📝 Test 1: Creating LaTeX Document")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
        latex_content = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\title{MCP LaTeX Tools Test}
\author{Test Suite}
\date{\today}

\begin{document}
\maketitle

\section{Introduction}
This is a test document to verify the MCP LaTeX Tools functionality.

\subsection{Features Tested}
\begin{itemize}
    \item Document compilation
    \item Syntax validation
    \item PDF information extraction
    \item File cleanup
\end{itemize}

\section{Conclusion}
If you can see this document, the tools are working correctly!

\end{document}
"""
        tmp.write(latex_content)
        tmp.flush()
        tex_path = Path(tmp.name)
        
        print(f"✅ Created LaTeX file: {tex_path}")
        
        # Test 2: Validate LaTeX syntax
        print("\n🔍 Test 2: LaTeX Validation")
        try:
            validation_result = validate_latex(str(tex_path))
            if validation_result.is_valid:
                print("✅ LaTeX syntax is valid")
                if validation_result.warnings:
                    print(f"   ⚠️ {len(validation_result.warnings)} warnings found")
            else:
                print(f"❌ LaTeX validation failed: {len(validation_result.errors)} errors")
                for error in validation_result.errors[:3]:  # Show first 3 errors
                    print(f"     • {error}")
        except Exception as e:
            print(f"❌ Validation error: {e}")
        
        # Test 3: Compile LaTeX to PDF
        print("\n🔨 Test 3: LaTeX Compilation")
        try:
            compilation_result = compile_latex(str(tex_path))
            if compilation_result.success:
                print("✅ LaTeX compilation successful")
                print(f"   📄 Output: {compilation_result.output_path}")
                print(f"   ⏱️ Time: {compilation_result.compilation_time_seconds:.2f}s")
                
                pdf_path = Path(compilation_result.output_path)
                
                # Test 4: Extract PDF information
                print("\n📊 Test 4: PDF Information Extraction")
                try:
                    pdf_info = extract_pdf_info(str(pdf_path))
                    if pdf_info.success:
                        print("✅ PDF info extracted successfully")
                        print(f"   📖 Pages: {pdf_info.page_count}")
                        print(f"   📏 File size: {pdf_info.file_size_bytes:,} bytes")
                        if pdf_info.title:
                            print(f"   📑 Title: {pdf_info.title}")
                        if pdf_info.page_dimensions:
                            dims = pdf_info.page_dimensions[0]
                            print(f"   📐 Page size: {dims['width']:.0f} x {dims['height']:.0f} {dims['unit']}")
                    else:
                        print(f"❌ PDF info extraction failed: {pdf_info.error_message}")
                except Exception as e:
                    print(f"❌ PDF info error: {e}")
                
            else:
                print(f"❌ LaTeX compilation failed: {compilation_result.error_message}")
                if compilation_result.log_content:
                    print("   📋 Log content preview:")
                    print("   " + compilation_result.log_content[:200] + "...")
        except Exception as e:
            print(f"❌ Compilation error: {e}")
        
        # Test 5: Cleanup auxiliary files
        print("\n🧹 Test 5: File Cleanup")
        try:
            cleanup_result = clean_latex(str(tex_path.parent), dry_run=True)
            if cleanup_result.success:
                print("✅ Cleanup scan successful")
                if cleanup_result.would_clean_files:
                    print(f"   🗑️ Would clean {len(cleanup_result.would_clean_files)} files:")
                    for file in cleanup_result.would_clean_files[:5]:  # Show first 5
                        print(f"     • {Path(file).name}")
                    if len(cleanup_result.would_clean_files) > 5:
                        print(f"     ... and {len(cleanup_result.would_clean_files) - 5} more")
                else:
                    print("   ✨ No auxiliary files to clean")
            else:
                print(f"❌ Cleanup failed: {cleanup_result.error_message}")
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
        
        print("\n🎉 Direct Tools Test Complete!")
        
        # Cleanup test files
        try:
            tex_path.unlink()
            # Try to remove PDF if it exists
            pdf_path = tex_path.with_suffix('.pdf')
            if pdf_path.exists():
                pdf_path.unlink()
            # Remove other auxiliary files
            for pattern in ['*.aux', '*.log', '*.out']:
                for file in tex_path.parent.glob(f"{tex_path.stem}.*"):
                    if file.suffix in ['.aux', '.log', '.out', '.fls', '.fdb_latexmk']:
                        file.unlink(missing_ok=True)
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

if __name__ == "__main__":
    test_latex_tools()