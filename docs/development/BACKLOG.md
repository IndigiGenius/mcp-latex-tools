# MCP LaTeX Tools Development Backlog

This document tracks features and improvements planned for future development.

**Last Updated**: 2026-04-06

---

## Near-Term Candidates

### ~~Pydantic Migration~~ ✅ COMPLETE (Apr 2026)

Migrated all 7 result classes from dataclasses to Pydantic BaseModel in 3 PRs (26Q2-REFAC-01/02/03). Remaining scope for future work: schema documentation generation.

---

### ~~Configuration System~~ ✅ COMPLETE (Apr 2026)

TOML-based config file (`.mcp-latex-tools.toml`) with Pydantic v2 models (26Q2-ENH-02). Walk-up file discovery, fail-open design, no new dependencies. Remaining scope for future work: environment variable overrides, global config, config reload.

---

### Enhanced Error Recovery
**Priority**: MEDIUM | **Effort**: 2 weeks

Smart error suggestions and automatic retry logic.

**Features**:
- Missing package → suggest installation command
- Syntax error → suggest common fixes
- Unicode error → suggest encoding fixes
- Retry with fallback options

---

## Future Candidates

### Multi-file Project Support
**Priority**: LOW | **Effort**: 5-8 days

Better handling of LaTeX projects with multiple files.

**Features**:
- `\include{}` and `\input{}` resolution
- Dependency tracking
- Incremental compilation
- Project structure detection

---

---

### Template Support
**Priority**: LOW | **Effort**: 3-5 days

LaTeX template management for common document types.

**Use Cases**:
- Academic papers (IEEE, ACM, Springer)
- Presentations (Beamer)
- Letters, resumes

---

## Research & Experimentation

### Alternative PDF Libraries
**Current**: pypdf
**Candidates**:
- PyMuPDF (faster, more features)
- pdfminer.six (better text extraction)
- camelot (table extraction)

**Evaluation Criteria**: Performance, features, maintenance, license

---

### WebAssembly LaTeX Compilation
**Idea**: Client-side LaTeX compilation via WASM

**Challenges**:
- Large WASM binary size
- Package availability
- Performance considerations

**Priority**: Research only (long-term)

---

## Technical Debt

### ~~Test Organization~~ ✅ COMPLETE (Apr 2026)

Reorganized all 11 test files into `tests/tools/`, `tests/utils/`, `tests/integration/` subdirectories mirroring source structure (26Q2-DEBT-01).

---

### Type Hint Coverage
**Goal**: 100% type hint coverage with strict mypy.

**Action Items**:
- Enable mypy strict mode in CI
- Add missing type hints
- Document type annotation standards

---

### CI/CD Enhancements
**Current**: Basic test running

**Proposed Additions**:
- Automated performance benchmarking
- Coverage reporting with trends
- Automatic documentation generation
- Release automation
- Docker image publishing

---

## Completed Items

### Q4 2025

- [x] **Token Optimization** (Oct 2025): 97.4% token reduction via log parser
- [x] **LaTeX Utilities Module** (Oct 2025): 65 tests, 150+ lines eliminated
- [x] **Core Tools** (Sep-Oct 2025): 4 production-ready tools

### Q1 2026

- [x] **Dead Code Removal** (Mar 2026): Removed `latex_utils.py`, consolidated constants
- [x] **Server Refactor** (Mar 2026): Simplified server.py, inline handlers
- [x] **Documentation Trim** (Apr 2026): Reduced docs from ~6,600 to ~800 lines

### Q2 2026

- [x] **Multi-Engine & Multi-Pass Compilation** (Apr 2026): 26Q2-ENH-01 — pdflatex/xelatex/lualatex/latexmk, auto passes, bibtex/biber support
- [x] **LaTeX Package Detection** (Apr 2026): 26Q2-TOOL-01 — parse \usepackage/\RequirePackage, kpsewhich checks, tlmgr install suggestions
- [x] **Pydantic Migration Part 1** (Apr 2026): 26Q2-REFAC-01 — LaTeXError, LogSummary, ValidationResult migrated from dataclasses to Pydantic BaseModel
- [x] **Pydantic Migration Part 2** (Apr 2026): 26Q2-REFAC-02 — CompilationResult, PackageDetectionResult migrated; pydantic>=2.0 added as explicit dependency
- [x] **Pydantic Migration Part 3** (Apr 2026): 26Q2-REFAC-03 — CleanupResult, PDFInfoResult migrated; all 7 result classes now Pydantic BaseModel
- [x] **Test Organization** (Apr 2026): 26Q2-DEBT-01 — Tests reorganized into tools/, utils/, integration/ subdirectories
- [x] **Configuration System** (Apr 2026): 26Q2-ENH-02 — TOML-based config file with Pydantic v2 models, walk-up discovery, fail-open design

---

## Prioritization Criteria

| Factor | Weight | Description |
|--------|--------|-------------|
| User Value | 40% | Direct benefit to users |
| Technical Debt | 20% | Long-term maintainability |
| Dependencies | 20% | Unlocks other work |
| Effort | 20% | Implementation complexity |

---

## Questions to Resolve

1. **Pydantic vs Attrs**: Which validation library for migration?
2. **Config Format**: YAML, TOML, or Python-based?
3. **Multi-file Projects**: How to detect project root?
4. **CI Platform**: GitHub Actions vs alternatives?

---

*Next Review: End of Q2 2026*
