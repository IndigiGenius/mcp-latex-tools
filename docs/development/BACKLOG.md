# MCP LaTeX Tools Development Backlog

This document tracks features and improvements planned beyond the current quarter. For Q1 2026 work, see [sprints/UPCOMING.md](../sprints/UPCOMING.md).

**Last Updated**: 2026-01-24

---

## Q2 2026 Candidates

### Pydantic Migration
**Priority**: HIGH | **Effort**: 2-3 weeks

Migrate all result classes from dataclasses to Pydantic models.

**Benefits**:
- Automatic input validation
- JSON schema generation for MCP
- Enhanced error messages
- Type coercion

**Scope**:
- `CompilationResult`, `ValidationResult`, `PdfInfoResult`, `CleanupResult`
- `LintResult`, `FormatResult` (new tools)
- Schema documentation generation

---

### Configuration System
**Priority**: MEDIUM | **Effort**: 1-2 weeks

Central configuration management for project and user preferences.

**Proposed Config** (`.mcp-latex-tools.yml`):
```yaml
compilation:
  engine: pdflatex  # or xelatex, lualatex
  timeout: 60
  passes: auto

validation:
  strict: false
  max_errors: 10

cleanup:
  dry_run_by_default: true
  extensions: [.aux, .log, .out]
```

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

## Q3 2026 Candidates

### Multi-file Project Support
**Priority**: LOW | **Effort**: 5-8 days

Better handling of LaTeX projects with multiple files.

**Features**:
- `\include{}` and `\input{}` resolution
- Dependency tracking
- Incremental compilation
- Project structure detection

---

### LaTeX Package Detection
**Priority**: LOW | **Effort**: 3-5 days

Detect and report missing LaTeX packages.

**Features**:
- Parse `\usepackage{}` commands
- Check if packages are installed
- Suggest tlmgr installation commands
- Integration with TeX Live

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

### Test Organization
**Problem**: Inconsistent test organization across directories.

**Proposed Structure**:
```
tests/
├── tools/
│   ├── test_compile.py
│   ├── test_validate.py
│   └── ...
├── utils/
│   └── test_*.py
├── integration/
│   └── test_end_to_end.py
└── fixtures/
```

**Effort**: Low (1-2 hours)

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

See [sprints/archive/](../sprints/archive/) for completed sprint details.

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

*Next Review: End of Q1 2026*
