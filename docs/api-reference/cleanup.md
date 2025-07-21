# cleanup Tool

## Overview

The `cleanup` tool removes LaTeX auxiliary files and build artifacts, maintaining clean working directories and preventing compilation conflicts.

**Primary Use Cases:**
- Automated auxiliary file cleanup after compilation
- Repository maintenance and version control hygiene
- Troubleshooting compilation issues caused by stale files
- Disk space management for large projects

## Tool Specification

### MCP Tool Definition
```json
{
  "name": "cleanup",
  "description": "Clean LaTeX auxiliary files",
  "inputSchema": {
    "type": "object",
    "properties": {
      "tex_path": {
        "type": "string",
        "description": "Path to LaTeX file or directory to clean"
      },
      "dry_run": {
        "type": "boolean",
        "description": "If true, show what would be cleaned without deleting (default: false)"
      },
      "recursive": {
        "type": "boolean",
        "description": "If true, clean recursively in subdirectories (default: false)"
      },
      "backup": {
        "type": "boolean",
        "description": "If true, create backup before cleaning (default: false)"
      },
      "extensions": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Custom file extensions to clean (optional)"
      }
    },
    "required": ["tex_path"]
  }
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tex_path` | string | ✅ | - | Path to LaTeX file or directory to clean |
| `dry_run` | boolean | ❌ | false | Show what would be cleaned without deleting |
| `recursive` | boolean | ❌ | false | Clean recursively in subdirectories |
| `backup` | boolean | ❌ | false | Create backup before cleaning |
| `extensions` | array | ❌ | [default set] | Custom file extensions to clean |

### Response Schema

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "True if cleanup succeeded"
    },
    "error_message": {
      "type": "string",
      "description": "Error description if cleanup failed"
    },
    "tex_file_path": {
      "type": "string",
      "description": "Path to LaTeX file being cleaned"
    },
    "directory_path": {
      "type": "string", 
      "description": "Path to directory being cleaned"
    },
    "cleaned_files_count": {
      "type": "integer",
      "description": "Number of files cleaned"
    },
    "cleaned_files": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of files that were cleaned"
    },
    "would_clean_files": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of files that would be cleaned (dry run)"
    },
    "dry_run": {
      "type": "boolean",
      "description": "True if this was a dry run"
    },
    "recursive": {
      "type": "boolean",
      "description": "True if cleanup was recursive"
    },
    "backup_created": {
      "type": "boolean",
      "description": "True if backup was created"
    },
    "backup_directory": {
      "type": "string",
      "description": "Path to backup directory"
    },
    "cleanup_time_seconds": {
      "type": "number",
      "description": "Time taken for cleanup in seconds"
    }
  }
}
```

## Usage Examples

### Basic Cleanup

**Human Usage:**
```python
# Clean auxiliary files for specific document
result = cleanup("document.tex")
if result.success:
    print(f"🧹 Cleaned {result.cleaned_files_count} files")
    for file in result.cleaned_files:
        print(f"  - {file}")
else:
    print(f"❌ Cleanup failed: {result.error_message}")
```

**LLM Usage:**
```json
{
  "tool": "cleanup",
  "parameters": {
    "tex_path": "document.tex"
  }
}
```

### Dry Run Preview

**Human Usage:**
```python
# Preview what would be cleaned
result = cleanup("project/", dry_run=True, recursive=True)
if result.success:
    print(f"🔍 Would clean {len(result.would_clean_files)} files:")
    for file in result.would_clean_files:
        print(f"  - {file}")
    
    # Confirm and clean
    confirm = input("Proceed with cleanup? (y/N): ")
    if confirm.lower() == 'y':
        result = cleanup("project/", recursive=True)
        print(f"✅ Cleaned {result.cleaned_files_count} files")
```

**LLM Usage:**
```json
{
  "tool": "cleanup",
  "parameters": {
    "tex_path": "project/",
    "dry_run": true,
    "recursive": true
  }
}
```

### Safe Cleanup with Backup

**Human Usage:**
```python
# Clean with backup for safety
result = cleanup("thesis.tex", backup=True)
if result.success:
    print(f"🧹 Cleaned {result.cleaned_files_count} files")
    if result.backup_created:
        print(f"💾 Backup created: {result.backup_directory}")
```

**LLM Usage:**
```json
{
  "tool": "cleanup",
  "parameters": {
    "tex_path": "thesis.tex",
    "backup": true
  }
}
```

## Response Examples

### Successful Cleanup

```json
{
  "success": true,
  "error_message": null,
  "tex_file_path": "document.tex",
  "directory_path": "/path/to/directory",
  "cleaned_files_count": 4,
  "cleaned_files": [
    "document.aux",
    "document.log",
    "document.out",
    "document.fls"
  ],
  "would_clean_files": [],
  "dry_run": false,
  "recursive": false,
  "backup_created": false,
  "backup_directory": null,
  "cleanup_time_seconds": 0.02
}
```

### Dry Run Preview

```json
{
  "success": true,
  "error_message": null,
  "tex_file_path": null,
  "directory_path": "/path/to/project",
  "cleaned_files_count": 0,
  "cleaned_files": [],
  "would_clean_files": [
    "chapter1.aux",
    "chapter1.log",
    "chapter2.aux", 
    "chapter2.log",
    "main.aux",
    "main.log",
    "main.toc"
  ],
  "dry_run": true,
  "recursive": true,
  "backup_created": false,
  "backup_directory": null,
  "cleanup_time_seconds": 0.01
}
```

### Cleanup with Backup

```json
{
  "success": true,
  "error_message": null,
  "tex_file_path": "thesis.tex",
  "directory_path": "/path/to/thesis",
  "cleaned_files_count": 8,
  "cleaned_files": [
    "thesis.aux", "thesis.log", "thesis.out", "thesis.toc",
    "thesis.lot", "thesis.lof", "thesis.bbl", "thesis.blg"
  ],
  "would_clean_files": [],
  "dry_run": false,
  "recursive": false,
  "backup_created": true,
  "backup_directory": "/path/to/thesis/.cleanup_backup_20250718_122643",
  "cleanup_time_seconds": 0.15
}
```

## Default File Extensions

### Standard LaTeX Auxiliary Files
```python
DEFAULT_EXTENSIONS = {
    # Compilation artifacts
    ".aux",     # Auxiliary file
    ".log",     # Compilation log
    ".out",     # PDF bookmarks
    ".fls",     # File list
    ".fdb_latexmk",  # Latexmk database
    
    # Table of contents
    ".toc",     # Table of contents
    ".lot",     # List of tables
    ".lof",     # List of figures
    
    # Bibliography
    ".bbl",     # Bibliography
    ".blg",     # Bibliography log
    ".bcf",     # Biber control file
    ".run.xml", # Biber run file
    
    # Index
    ".idx",     # Index
    ".ind",     # Formatted index
    ".ilg",     # Index log
    
    # Nomenclature
    ".nlo",     # Nomenclature
    ".nls",     # Nomenclature sorted
    ".nlg",     # Nomenclature log
    
    # Navigation
    ".nav",     # Beamer navigation
    ".snm",     # Beamer slide notes
    ".vrb",     # Beamer verbatim
    
    # Other
    ".synctex.gz",  # SyncTeX
    ".figlist",     # Figure list
    ".makefile",    # Generated makefile
    ".figlist",     # PSTricks figure list
    ".fls",         # File list
}
```

### Custom Extensions

```python
# Clean specific file types
result = cleanup("document.tex", extensions=[".tmp", ".backup", ".old"])

# Clean only logs and auxiliary files
result = cleanup("project/", extensions=[".log", ".aux"], recursive=True)
```

## Advanced Usage Patterns

### Project-Wide Cleanup

```python
def clean_latex_project(project_dir: str, interactive: bool = True):
    """Clean entire LaTeX project with user confirmation"""
    
    # Preview cleanup
    preview = cleanup(project_dir, dry_run=True, recursive=True)
    
    if not preview.success:
        print(f"❌ Preview failed: {preview.error_message}")
        return False
    
    if not preview.would_clean_files:
        print("✨ Project is already clean")
        return True
    
    # Show what will be cleaned
    print(f"🔍 Found {len(preview.would_clean_files)} auxiliary files:")
    for file in preview.would_clean_files[:10]:  # Show first 10
        print(f"  - {file}")
    
    if len(preview.would_clean_files) > 10:
        print(f"  ... and {len(preview.would_clean_files) - 10} more")
    
    # Confirm if interactive
    if interactive:
        response = input("\nProceed with cleanup? (y/N): ")
        if response.lower() != 'y':
            print("Cleanup cancelled")
            return False
    
    # Perform cleanup with backup
    result = cleanup(project_dir, recursive=True, backup=True)
    
    if result.success:
        print(f"✅ Cleaned {result.cleaned_files_count} files")
        if result.backup_created:
            print(f"💾 Backup: {result.backup_directory}")
        return True
    else:
        print(f"❌ Cleanup failed: {result.error_message}")
        return False

# Usage
clean_latex_project("./thesis_project")
```

### Automated Post-Compilation Cleanup

```python
async def compile_and_clean(tex_file: str, keep_pdf: bool = True):
    """Compile document and clean auxiliary files"""
    
    # Compile document
    compilation = await compile_latex(tex_file)
    
    if not compilation.success:
        return {
            "status": "compilation_failed",
            "error": compilation.error_message
        }
    
    # Clean auxiliary files
    cleanup_result = cleanup(tex_file)
    
    # Preserve PDF if requested
    pdf_path = compilation.output_path
    if keep_pdf and pdf_path:
        print(f"📄 PDF preserved: {pdf_path}")
    
    return {
        "status": "success",
        "pdf_path": pdf_path,
        "cleaned_files": cleanup_result.cleaned_files_count,
        "compilation_time": compilation.compilation_time_seconds,
        "cleanup_time": cleanup_result.cleanup_time_seconds
    }

# Usage
result = await compile_and_clean("paper.tex")
print(f"Status: {result['status']}")
```

### Selective Cleanup

```python
def selective_cleanup(directory: str, file_types: list[str]):
    """Clean only specific types of auxiliary files"""
    
    type_map = {
        "logs": [".log", ".blg", ".ilg", ".nlg"],
        "aux": [".aux", ".out", ".fls", ".fdb_latexmk"],
        "toc": [".toc", ".lot", ".lof"],
        "bib": [".bbl", ".bcf", ".run.xml"],
        "index": [".idx", ".ind", ".ilg"],
        "beamer": [".nav", ".snm", ".vrb"],
        "sync": [".synctex.gz"]
    }
    
    extensions_to_clean = []
    for file_type in file_types:
        if file_type in type_map:
            extensions_to_clean.extend(type_map[file_type])
    
    if not extensions_to_clean:
        print("No valid file types specified")
        return None
    
    result = cleanup(
        directory, 
        extensions=extensions_to_clean, 
        recursive=True
    )
    
    print(f"🧹 Cleaned {file_types} files: {result.cleaned_files_count}")
    return result

# Usage examples
selective_cleanup("./", ["logs"])  # Clean only log files
selective_cleanup("./", ["aux", "toc"])  # Clean aux and TOC files
selective_cleanup("./", ["bib", "index"])  # Clean bibliography and index files
```

### Git Integration

```python
def cleanup_for_git(repository_path: str):
    """Clean auxiliary files before git commit"""
    
    import subprocess
    
    # Check if in git repository
    try:
        subprocess.run(["git", "status"], 
                      cwd=repository_path, 
                      capture_output=True, 
                      check=True)
    except subprocess.CalledProcessError:
        print("❌ Not a git repository")
        return False
    
    # Clean auxiliary files
    result = cleanup(repository_path, recursive=True, dry_run=True)
    
    if not result.would_clean_files:
        print("✨ No auxiliary files to clean")
        return True
    
    # Show files that would be cleaned
    print(f"🧹 Will clean {len(result.would_clean_files)} auxiliary files")
    
    # Perform cleanup
    cleanup_result = cleanup(repository_path, recursive=True)
    
    if cleanup_result.success:
        print(f"✅ Cleaned {cleanup_result.cleaned_files_count} files")
        
        # Add .gitignore rules if not present
        gitignore_path = f"{repository_path}/.gitignore"
        try:
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
        except FileNotFoundError:
            gitignore_content = ""
        
        latex_ignores = [
            "*.aux", "*.log", "*.out", "*.toc", "*.lot", "*.lof",
            "*.bbl", "*.blg", "*.idx", "*.ind", "*.ilg",
            "*.fls", "*.fdb_latexmk", "*.synctex.gz"
        ]
        
        missing_ignores = [ignore for ignore in latex_ignores 
                          if ignore not in gitignore_content]
        
        if missing_ignores:
            print(f"💡 Consider adding to .gitignore: {', '.join(missing_ignores)}")
        
        return True
    else:
        print(f"❌ Cleanup failed: {cleanup_result.error_message}")
        return False

# Usage
cleanup_for_git("./latex_project")
```

## Integration Patterns

### CI/CD Pipeline Cleanup

```yaml
# GitHub Actions example
- name: Clean auxiliary files
  run: |
    python -c "
    from mcp_latex_tools.tools.cleanup import clean_latex
    result = clean_latex('.', recursive=True)
    print(f'Cleaned {result.cleaned_files_count} auxiliary files')
    "
```

### Build System Integration

```python
# Makefile equivalent
def build_clean_cycle(tex_files: list[str]):
    """Build and clean cycle for multiple documents"""
    
    results = []
    
    for tex_file in tex_files:
        print(f"\n📄 Processing: {tex_file}")
        
        # Compile
        compilation = await compile_latex(tex_file)
        
        # Clean regardless of compilation success
        cleanup_result = cleanup(tex_file)
        
        results.append({
            "file": tex_file,
            "compilation_success": compilation.success,
            "cleaned_files": cleanup_result.cleaned_files_count
        })
    
    # Summary
    successful = sum(1 for r in results if r["compilation_success"])
    total_cleaned = sum(r["cleaned_files"] for r in results)
    
    print(f"\n📊 Build Summary:")
    print(f"  - Documents: {len(tex_files)}")
    print(f"  - Successful: {successful}")
    print(f"  - Files cleaned: {total_cleaned}")
    
    return results
```

## Best Practices

### When to Clean
1. **After successful compilation** - Remove build artifacts
2. **Before version control commits** - Keep repository clean
3. **When troubleshooting** - Clear stale files that might cause issues
4. **During project archival** - Reduce project size

### Safety Measures
1. **Use dry run first** - Preview what will be cleaned
2. **Create backups** for important projects
3. **Be selective** - Only clean known auxiliary file types
4. **Avoid recursive cleanup** in shared directories

### Performance Tips
1. **Batch operations** - Clean multiple projects efficiently
2. **Use appropriate extensions** - Don't clean more than necessary
3. **Monitor disk space** - Track space savings from cleanup
4. **Automate safely** - Build cleanup into workflows

---

**This tool provides comprehensive auxiliary file management for clean, efficient LaTeX development workflows.** 🧹