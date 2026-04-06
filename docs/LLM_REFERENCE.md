# LLM Quick Reference for MCP LaTeX Tools

Quick reference for LLM agents using MCP LaTeX Tools.

## Tool Cheat Sheet

| Tool | Purpose | Key Params | Side Effects |
|------|---------|------------|--------------|
| `compile_latex` | .tex to PDF | `tex_path` (required), `engine`, `passes`, `timeout`, `output_dir` | Creates .pdf, .aux, .log |
| `validate_latex` | Syntax check | `file_path` (required), `quick`, `strict` | None (read-only) |
| `pdf_info` | PDF metadata | `file_path` (required), `include_text` | None (read-only) |
| `cleanup` | Remove aux files | `path` (required), `dry_run`, `recursive` | Deletes files |
| `detect_packages` | Find required packages | `file_path` (required), `check_installed` | None (read-only) |

## Recommended Workflow

```
1. validate_latex(file_path="doc.tex")
   -> Check is_valid field
   -> If errors, fix and retry

2. compile_latex(tex_path="doc.tex")
   -> Check success field
   -> Get output_path for PDF location

3. pdf_info(file_path="doc.pdf")
   -> Verify page_count
   -> Check file_size_bytes

4. cleanup(path="doc.tex", dry_run=true)
   -> Preview what will be deleted
   -> Then: cleanup(path="doc.tex")
```

## Decision Tree

```
Need PDF from .tex?
  -> compile_latex

Unicode fonts or OpenType?
  -> compile_latex with engine="xelatex" or engine="lualatex"

Has bibliography or cross-references?
  -> compile_latex with passes="auto" (auto-detects bibtex/biber)

Complex document (bibliography + cross-refs + TOC)?
  -> compile_latex with engine="latexmk" (handles everything automatically)

Syntax errors?
  -> validate_latex first (faster than compilation)

Check PDF properties?
  -> pdf_info

Remove .aux/.log files?
  -> cleanup (use dry_run=true first)

Missing packages?
  -> detect_packages (shows what's missing + tlmgr install commands)
```

## Error Recovery Patterns

| Symptom | Action |
|---------|--------|
| Compilation fails | Run `validate_latex` first to identify syntax errors |
| Validate passes, compile fails | Run `detect_packages` to check for missing packages |
| "File not found" | Verify file path is absolute or relative to CWD |
| "Permission denied" | Check file/directory permissions |
| Timeout | Increase `timeout` parameter (default: 30s) |

## Configuration File

Place a `.mcp-latex-tools.toml` in your project root to override defaults. All fields are optional:

```toml
[compilation]
engine = "xelatex"    # default: "pdflatex"
timeout = 60          # default: 30
passes = "auto"       # default: 1

[validation]
strict = true         # default: false
max_errors = 5        # default: 10

[cleanup]
dry_run = true        # default: false
extensions = [".aux", ".log", ".out"]  # default: all 26 extensions

[pdf_info]
include_text = true   # default: false

[detect_packages]
check_installed = false  # default: true
```

MCP tool call arguments always override config file values.

## Parameter Defaults

### compile_latex
- `engine`: `"pdflatex"` (default). Options: `"pdflatex"`, `"xelatex"`, `"lualatex"`, `"latexmk"`
  - Use `xelatex` or `lualatex` for Unicode/OpenType font support
  - Use `latexmk` for automatic multi-pass handling (recommended for complex documents)
- `passes`: `1` (default). Options: `1`, `2`, `3`, or `"auto"`
  - `"auto"` detects rerun needs from the log (max 3 passes)
  - Automatically runs `bibtex` when `\bibliography{}` is detected
  - Automatically runs `biber` when `\addbibresource{}` is detected
  - `latexmk` engine handles passes automatically regardless of this setting
- `timeout`: 30 seconds (increase for large documents or multi-pass)
- `output_dir`: Same directory as input file

### validate_latex
- `quick`: false (set true for fastest basic check)
- `strict`: false (set true for style checking)
- Note: `quick` and `strict` are mutually exclusive

### cleanup
- `dry_run`: false (set true to preview without deleting)
- `recursive`: false (set true to clean subdirectories)
- `create_backup`: false (set true to backup before deletion)

### detect_packages
- `check_installed`: true (set false for parse-only mode without kpsewhich)
- Returns: `packages` (all detected), `installed`, `missing`, `install_commands`

## Response Parsing

### Success Indicators
- `compile_latex`: Check `success` field or look for checkmark in text
- `validate_latex`: Check `is_valid` field
- `pdf_info`: Check `success` field
- `cleanup`: Check `success` field
- `detect_packages`: Check `success` field; inspect `missing` list

### Error Information
- All tools include `error_message` on failure
- `compile_latex` includes concise log summary (not full log)
- `validate_latex` includes list of specific errors with line numbers

## File Extensions

### Cleaned by cleanup tool (common)
`.aux`, `.log`, `.out`, `.fls`, `.fdb_latexmk`, `.toc`, `.lof`, `.lot`, `.bbl`, `.blg`, `.nav`, `.snm`, `.vrb`, `.idx`, `.ilg`, `.ind`, `.synctex.gz`

For the full list (26 extensions), query the `latex://config/cleanup-extensions` resource.

### Protected (never deleted, common)
`.tex`, `.pdf`, `.bib`, `.sty`, `.cls`, `.png`, `.jpg`, `.eps`

For the full list (20 extensions), query the `latex://config/protected-extensions` resource.

## Common Workflows

### Quick Validation
```python
validate_latex(file_path="doc.tex", quick=true)
```
Checks only: documentclass, begin/end document, brace balance.

### Full Build Cycle
```python
validate_latex(file_path="doc.tex")           # Check syntax
compile_latex(tex_path="doc.tex", timeout=60) # Build PDF
pdf_info(file_path="doc.pdf")                 # Verify output
cleanup(path="doc.tex")                       # Clean up
```

### Fresh Build (Clean First)
```python
cleanup(path="doc.tex", dry_run=true)  # Preview
cleanup(path="doc.tex")                # Clean
compile_latex(tex_path="doc.tex")      # Fresh build
```

### Debug Compilation Failure
```python
validate_latex(file_path="doc.tex", quick=true)   # Fast check
validate_latex(file_path="doc.tex")               # Full check
validate_latex(file_path="doc.tex", strict=true)  # Style check
compile_latex(tex_path="doc.tex", timeout=120)    # Try with longer timeout
```
