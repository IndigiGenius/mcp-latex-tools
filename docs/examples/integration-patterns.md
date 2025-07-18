# Integration Patterns

This guide demonstrates common integration patterns for MCP LaTeX Tools in various workflows and environments.

## Research Document Workflow

### Complete Academic Paper Pipeline

```python
import asyncio
from mcp_latex_tools.tools import compile_latex, validate_latex, pdf_info, cleanup

async def academic_paper_workflow(paper_path: str):
    """Complete academic paper preparation workflow"""
    
    print(f"📝 Processing: {paper_path}")
    
    # Step 1: Validate LaTeX syntax
    validation = validate_latex(paper_path, mode="strict")
    if not validation.is_valid:
        print("❌ Validation errors found:")
        for error in validation.errors:
            print(f"  - {error}")
        return False
    
    print("✅ LaTeX syntax validated")
    
    # Step 2: Compile to PDF
    compilation = await compile_latex(
        tex_path=paper_path,
        timeout=60,  # Longer timeout for complex papers
        engine="pdflatex"
    )
    
    if not compilation.success:
        print(f"❌ Compilation failed: {compilation.error_message}")
        print("📋 Compilation log:")
        print(compilation.log_content)
        return False
    
    print(f"✅ PDF generated: {compilation.output_path}")
    print(f"⏱️ Compilation time: {compilation.compilation_time_seconds:.2f}s")
    
    # Step 3: Analyze PDF output
    pdf_analysis = pdf_info(compilation.output_path)
    print(f"📄 Document analysis:")
    print(f"  - Pages: {pdf_analysis.page_count}")
    print(f"  - Size: {pdf_analysis.file_size_bytes / 1024:.1f} KB")
    print(f"  - PDF version: {pdf_analysis.pdf_version}")
    
    # Step 4: Clean auxiliary files
    cleanup_result = cleanup(paper_path, backup=True)
    print(f"🧹 Cleaned {cleanup_result.cleaned_files_count} auxiliary files")
    
    return True

# Usage
asyncio.run(academic_paper_workflow("research_paper.tex"))
```

### Multi-Chapter Thesis Processing

```python
async def thesis_workflow(chapters: list[str], main_file: str):
    """Process multi-chapter thesis documents"""
    
    results = {
        "chapters": {},
        "main": None,
        "total_pages": 0,
        "total_time": 0
    }
    
    # Process individual chapters
    for chapter in chapters:
        print(f"\n📖 Processing chapter: {chapter}")
        
        # Validate chapter
        validation = validate_latex(chapter)
        if not validation.is_valid:
            results["chapters"][chapter] = {"status": "validation_failed"}
            continue
        
        # Compile chapter
        compilation = await compile_latex(chapter)
        if compilation.success:
            info = pdf_info(compilation.output_path)
            results["chapters"][chapter] = {
                "status": "success",
                "pages": info.page_count,
                "time": compilation.compilation_time_seconds
            }
            results["total_pages"] += info.page_count
            results["total_time"] += compilation.compilation_time_seconds
    
    # Compile main thesis document
    print(f"\n📚 Compiling main thesis: {main_file}")
    main_result = await compile_latex(
        tex_path=main_file,
        timeout=120,  # Extended timeout for full thesis
        engine="xelatex"  # Better for complex formatting
    )
    
    if main_result.success:
        main_info = pdf_info(main_result.output_path)
        results["main"] = {
            "status": "success",
            "pages": main_info.page_count,
            "time": main_result.compilation_time_seconds,
            "size_mb": main_info.file_size_bytes / (1024 * 1024)
        }
    
    # Summary report
    print("\n📊 Thesis Compilation Summary:")
    print(f"  - Chapters processed: {len(chapters)}")
    print(f"  - Total pages: {results['total_pages']}")
    print(f"  - Total compilation time: {results['total_time']:.2f}s")
    if results["main"]:
        print(f"  - Full thesis: {results['main']['pages']} pages, {results['main']['size_mb']:.1f} MB")
    
    return results

# Usage
chapters = ["chapter1.tex", "chapter2.tex", "chapter3.tex"]
asyncio.run(thesis_workflow(chapters, "thesis_main.tex"))
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/latex-build.yml
name: LaTeX Document Build

on:
  push:
    paths:
      - '**.tex'
      - '**.bib'
  pull_request:
    paths:
      - '**.tex'
      - '**.bib'

jobs:
  build-documents:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install LaTeX
      run: |
        sudo apt-get update
        sudo apt-get install -y texlive-latex-base texlive-latex-extra texlive-fonts-recommended
    
    - name: Install MCP LaTeX Tools
      run: |
        pip install uv
        uv sync
    
    - name: Build Documents
      run: |
        python scripts/build_all_docs.py
    
    - name: Upload PDFs
      uses: actions/upload-artifact@v3
      with:
        name: compiled-documents
        path: '**/*.pdf'
```

### Build Script for CI/CD

```python
# scripts/build_all_docs.py
import asyncio
import glob
import json
import sys
from pathlib import Path
from mcp_latex_tools.tools import compile_latex, validate_latex, cleanup

async def build_all_documents():
    """Build all LaTeX documents in repository"""
    
    # Find all .tex files
    tex_files = glob.glob("**/*.tex", recursive=True)
    
    # Filter out auxiliary files
    main_docs = [f for f in tex_files if not any(
        exclude in f for exclude in ['_aux', 'include', 'preamble']
    )]
    
    results = {
        "success": [],
        "failed": [],
        "total_time": 0
    }
    
    for doc in main_docs:
        print(f"\n📄 Building: {doc}")
        
        # Validate first
        validation = validate_latex(doc)
        if not validation.is_valid:
            results["failed"].append({
                "file": doc,
                "error": "validation_failed",
                "details": validation.errors
            })
            continue
        
        # Compile
        try:
            compilation = await compile_latex(doc, timeout=60)
            if compilation.success:
                results["success"].append({
                    "file": doc,
                    "output": compilation.output_path,
                    "time": compilation.compilation_time_seconds
                })
                results["total_time"] += compilation.compilation_time_seconds
            else:
                results["failed"].append({
                    "file": doc,
                    "error": "compilation_failed",
                    "details": compilation.error_message
                })
        except Exception as e:
            results["failed"].append({
                "file": doc,
                "error": "exception",
                "details": str(e)
            })
    
    # Clean up auxiliary files
    for doc in results["success"]:
        cleanup(doc["file"], dry_run=False)
    
    # Summary
    print("\n" + "="*50)
    print("BUILD SUMMARY")
    print("="*50)
    print(f"✅ Successful: {len(results['success'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⏱️ Total time: {results['total_time']:.2f}s")
    
    # Write results to JSON
    with open("build_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Exit with error if any failures
    if results["failed"]:
        print("\nFailed documents:")
        for failure in results["failed"]:
            print(f"  - {failure['file']}: {failure['error']}")
        sys.exit(1)
    
    return results

if __name__ == "__main__":
    asyncio.run(build_all_documents())
```

## Jupyter Notebook Integration

### Research Notebook with LaTeX

```python
# In Jupyter notebook cell
%pip install mcp-latex-tools

import asyncio
from IPython.display import display, PDF, Markdown
from mcp_latex_tools.tools import compile_latex, validate_latex, pdf_info

async def compile_and_display(tex_content: str, filename: str = "notebook_output.tex"):
    """Compile LaTeX content and display in notebook"""
    
    # Write content to file
    with open(filename, 'w') as f:
        f.write(tex_content)
    
    # Validate
    validation = validate_latex(filename)
    if not validation.is_valid:
        display(Markdown(f"**Validation Errors:**\n" + "\n".join(
            f"- {error}" for error in validation.errors
        )))
        return
    
    # Compile
    result = await compile_latex(filename)
    
    if result.success:
        # Display PDF in notebook
        display(PDF(result.output_path))
        
        # Show metadata
        info = pdf_info(result.output_path)
        display(Markdown(f"""
**Compilation Successful!**
- Pages: {info.page_count}
- Size: {info.file_size_bytes / 1024:.1f} KB
- Time: {result.compilation_time_seconds:.2f}s
        """))
    else:
        display(Markdown(f"**Compilation Error:**\n{result.error_message}"))

# Example usage in notebook
tex_content = r"""
\documentclass{article}
\usepackage{amsmath}
\begin{document}

\title{Notebook Analysis Results}
\author{Data Science Team}
\date{\today}
\maketitle

\section{Results}

The analysis shows that:
\begin{equation}
    R^2 = 0.956
\end{equation}

This indicates a strong correlation.

\end{document}
"""

await compile_and_display(tex_content)
```

## Batch Processing Patterns

### Parallel Document Compilation

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

async def parallel_compilation(documents: list[str], max_workers: int = 4):
    """Compile multiple documents in parallel"""
    
    start_time = time.time()
    
    # Create task queue
    async def compile_with_status(doc):
        print(f"🔄 Starting: {doc}")
        result = await compile_latex(doc)
        status = "✅" if result.success else "❌"
        print(f"{status} Completed: {doc} ({result.compilation_time_seconds:.2f}s)")
        return (doc, result)
    
    # Run compilations in parallel
    tasks = [compile_with_status(doc) for doc in documents]
    results = await asyncio.gather(*tasks)
    
    # Summary statistics
    total_time = time.time() - start_time
    successful = sum(1 for _, r in results if r.success)
    total_compilation_time = sum(r.compilation_time_seconds for _, r in results)
    
    print(f"\n📊 Batch Compilation Summary:")
    print(f"  - Documents: {len(documents)}")
    print(f"  - Successful: {successful}/{len(documents)}")
    print(f"  - Total time: {total_time:.2f}s")
    print(f"  - Compilation time: {total_compilation_time:.2f}s")
    print(f"  - Speedup: {total_compilation_time/total_time:.2f}x")
    
    return dict(results)

# Usage
documents = [
    "paper1.tex",
    "paper2.tex", 
    "presentation.tex",
    "report.tex"
]

results = asyncio.run(parallel_compilation(documents))
```

### Incremental Build System

```python
import os
import hashlib
from datetime import datetime

class IncrementalBuilder:
    """Build only changed LaTeX documents"""
    
    def __init__(self, cache_file: str = ".latex_build_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load build cache"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Save build cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _file_hash(self, filepath: str) -> str:
        """Calculate file hash"""
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def needs_rebuild(self, tex_file: str) -> bool:
        """Check if file needs rebuilding"""
        current_hash = self._file_hash(tex_file)
        
        if tex_file not in self.cache:
            return True
        
        return self.cache[tex_file]["hash"] != current_hash
    
    async def build(self, tex_file: str):
        """Build if necessary"""
        if not self.needs_rebuild(tex_file):
            print(f"⏭️ Skipping {tex_file} (unchanged)")
            return self.cache[tex_file]["result"]
        
        print(f"🔨 Building {tex_file}")
        
        # Validate and compile
        validation = validate_latex(tex_file)
        if not validation.is_valid:
            return {"success": False, "error": "validation_failed"}
        
        result = await compile_latex(tex_file)
        
        # Update cache
        self.cache[tex_file] = {
            "hash": self._file_hash(tex_file),
            "timestamp": datetime.now().isoformat(),
            "result": {
                "success": result.success,
                "output": result.output_path,
                "time": result.compilation_time_seconds
            }
        }
        self._save_cache()
        
        return result

# Usage
builder = IncrementalBuilder()

documents = ["doc1.tex", "doc2.tex", "doc3.tex"]
for doc in documents:
    result = await builder.build(doc)
```

## Error Recovery Patterns

### Automatic Error Recovery

```python
async def compile_with_recovery(tex_file: str, max_attempts: int = 3):
    """Compile with automatic error recovery"""
    
    for attempt in range(max_attempts):
        print(f"🔄 Compilation attempt {attempt + 1}/{max_attempts}")
        
        # Validate first
        validation = validate_latex(tex_file)
        if not validation.is_valid:
            # Try to fix common issues
            fixed = await auto_fix_latex(tex_file, validation.errors)
            if not fixed:
                return {"success": False, "error": "validation_failed"}
        
        # Attempt compilation
        result = await compile_latex(tex_file, timeout=30 + (attempt * 15))
        
        if result.success:
            return result
        
        # Analyze error and attempt recovery
        recovery_action = analyze_compilation_error(result.error_message)
        
        if recovery_action == "install_package":
            missing_package = extract_missing_package(result.log_content)
            print(f"📦 Installing missing package: {missing_package}")
            install_latex_package(missing_package)
        
        elif recovery_action == "increase_memory":
            print("💾 Increasing memory limits")
            os.environ["TEXMFCNF"] = ".:$TEXMFHOME/texmf/web2c:"
        
        elif recovery_action == "clean_aux":
            print("🧹 Cleaning auxiliary files")
            cleanup(tex_file, dry_run=False)
        
        else:
            # No recovery possible
            break
    
    return result

async def auto_fix_latex(tex_file: str, errors: list[str]) -> bool:
    """Attempt to automatically fix common LaTeX errors"""
    
    fixes_applied = 0
    content = Path(tex_file).read_text()
    
    for error in errors:
        if "Missing $ inserted" in error:
            # Fix math mode errors
            content = fix_math_mode(content)
            fixes_applied += 1
        
        elif "Undefined control sequence" in error:
            # Add common missing packages
            if "\\cite" in error and "\\usepackage{cite}" not in content:
                content = add_package(content, "cite")
                fixes_applied += 1
    
    if fixes_applied > 0:
        # Create backup
        backup_file = f"{tex_file}.backup"
        Path(backup_file).write_text(Path(tex_file).read_text())
        
        # Write fixed content
        Path(tex_file).write_text(content)
        print(f"✅ Applied {fixes_applied} automatic fixes")
        return True
    
    return False
```

## Performance Monitoring

### LaTeX Compilation Dashboard

```python
import time
from collections import defaultdict
from datetime import datetime, timedelta

class CompilationMonitor:
    """Monitor LaTeX compilation performance"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = datetime.now()
    
    async def compile_with_monitoring(self, tex_file: str):
        """Compile with performance monitoring"""
        
        # Pre-compilation metrics
        start = time.time()
        file_size = os.path.getsize(tex_file) / 1024  # KB
        
        # Compile
        result = await compile_latex(tex_file)
        
        # Post-compilation metrics
        duration = time.time() - start
        
        # Store metrics
        self.metrics["compilations"].append({
            "file": tex_file,
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "success": result.success,
            "file_size_kb": file_size,
            "output_size_kb": os.path.getsize(result.output_path) / 1024 if result.success else 0
        })
        
        return result
    
    def get_statistics(self):
        """Get compilation statistics"""
        
        if not self.metrics["compilations"]:
            return {}
        
        compilations = self.metrics["compilations"]
        successful = [c for c in compilations if c["success"]]
        
        return {
            "total_compilations": len(compilations),
            "successful": len(successful),
            "failed": len(compilations) - len(successful),
            "success_rate": len(successful) / len(compilations),
            "average_duration": sum(c["duration"] for c in successful) / len(successful) if successful else 0,
            "total_duration": sum(c["duration"] for c in compilations),
            "uptime": str(datetime.now() - self.start_time),
            "throughput": len(compilations) / (datetime.now() - self.start_time).total_seconds() * 3600
        }
    
    def print_dashboard(self):
        """Print performance dashboard"""
        
        stats = self.get_statistics()
        
        print("\n" + "="*50)
        print("📊 LATEX COMPILATION DASHBOARD")
        print("="*50)
        print(f"Uptime: {stats['uptime']}")
        print(f"Total Compilations: {stats['total_compilations']}")
        print(f"Success Rate: {stats['success_rate']:.1%}")
        print(f"Average Duration: {stats['average_duration']:.2f}s")
        print(f"Throughput: {stats['throughput']:.1f} docs/hour")
        print("="*50)

# Usage
monitor = CompilationMonitor()

# Compile multiple documents
for doc in ["doc1.tex", "doc2.tex", "doc3.tex"]:
    await monitor.compile_with_monitoring(doc)

monitor.print_dashboard()
```

## Claude Code Integration Examples

### Interactive Document Development

```python
# This pattern is designed for Claude Code integration
async def interactive_latex_development(base_document: str):
    """Interactive LaTeX development with Claude Code"""
    
    print(f"🚀 Starting interactive development for: {base_document}")
    
    # Initial validation
    validation = validate_latex(base_document)
    if validation.is_valid:
        print("✅ Initial document is valid")
    else:
        print("⚠️ Initial validation errors:")
        for error in validation.errors:
            print(f"  - {error}")
    
    # Watch for changes (simulated - in practice Claude Code would trigger)
    async def on_document_change():
        """Called when document changes"""
        
        # Quick validation
        validation = validate_latex(base_document)
        
        if validation.is_valid:
            # Compile if valid
            result = await compile_latex(base_document)
            if result.success:
                info = pdf_info(result.output_path)
                print(f"✅ Compiled successfully: {info.page_count} pages")
            else:
                print(f"❌ Compilation error: {result.error_message}")
        else:
            print(f"❌ Validation errors: {len(validation.errors)}")
    
    # Simulate interactive session
    return on_document_change

# Usage with Claude Code
# Claude: "Let me help you develop this LaTeX document interactively"
handler = await interactive_latex_development("manuscript.tex")
# Claude makes changes to the document...
await handler()  # Validates and compiles automatically
```

---

**These integration patterns demonstrate the flexibility and power of MCP LaTeX Tools across various workflows, from simple document compilation to complex CI/CD pipelines and interactive development with Claude Code.**