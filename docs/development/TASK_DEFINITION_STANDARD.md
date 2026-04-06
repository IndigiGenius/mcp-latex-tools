# Task Definition Standard

**Version**: 1.0
**Created**: 2026-04-06
**Status**: Active

## Overview

This document defines the standard format for task definitions in mcp-latex-tools. Well-defined tasks ensure:

1. **Clarity** - Both humans and AI agents can understand requirements
2. **Verifiability** - Every criterion can be tested with a command
3. **Scoping** - Clear boundaries prevent scope creep
4. **Traceability** - Tasks link to branches, PRs, and verification

## Task Template

```markdown
### {TASK_ID}: {Task Title}

**User Story**: As a [role], I want [feature] so that [benefit].

| Field | Value |
|-------|-------|
| **Story Points** | N |
| **Priority** | CRITICAL / HIGH / MEDIUM / LOW |
| **Status** | 🔲 PENDING / 🔄 IN PROGRESS / ✅ COMPLETE |
| **Branch** | `{TASK_ID}-short-description` |
| **Dependencies** | None / List of task IDs |
| **PR Size Target** | <500 lines (max 1000) |

---

#### Context

> Summarize current state. Include investigation results.

**Current State**:
- `path/to/existing.py` contains `ExistingClass` (N lines)
- No existing tests for this functionality

**Investigation**:
```bash
# What exists now
grep -r "relevant_pattern" --include="*.py" src/ tests/
# Output summary: Found X files, Y usages
```

---

#### Acceptance Criteria

> Each criterion must be verifiable with a single command returning exit code 0.

- [ ] `path/to/file.py` has `function_name(arg: Type) -> ReturnType`
- [ ] `tests/test_file.py` covers: happy path, edge case, error case
- [ ] All tests pass: `uv run pytest tests/test_file.py -v`
- [ ] Type checking passes: `uv run mypy path/to/file.py`
- [ ] No lint errors: `uv run ruff check path/to/file.py`

---

#### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/mcp_latex_tools/tools/new.py` | CREATE | Main implementation |
| `src/mcp_latex_tools/server.py` | MODIFY | Register tool, add handler |
| `tests/test_new.py` | CREATE | Unit tests |

---

#### Implementation Notes

> Optional: Key decisions, algorithms, or patterns to follow.

- Follow existing tool pattern from `compile.py`
- Use `_text_result()` helper for MCP responses

---

#### Verification Script

```bash
#!/bin/bash
set -e

# 1. Files exist
test -f path/to/file.py

# 2. Required content present
grep -q "function_name" path/to/file.py

# 3. Import works
uv run python -c "from mcp_latex_tools.tools.module import Class; print('OK')"

# 4. Tests pass
uv run pytest tests/test_file.py -v --tb=short

# 5. Full suite (no regressions)
uv run pytest --tb=short -q

# 6. Code quality
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/

echo "All verification checks passed"
```

---

#### Definition of Done

- [ ] All acceptance criteria checked off
- [ ] Verification script exits with code 0
- [ ] Code quality checks pass (`ruff format`, `ruff check`, `mypy`)
- [ ] PR created with <500 lines changed
- [ ] Tests included with implementation
- [ ] Documentation updated (LLM_REFERENCE.md, ARCHITECTURE.md if applicable)
```

---

## Guidelines

### 1. Investigation Before Writing

Before finalizing acceptance criteria, verify what exists:

```bash
# Find existing code
grep -r "function_name\|ClassName" --include="*.py" src/ tests/

# Check current tool count
grep -c "Tool(" src/mcp_latex_tools/server.py

# Check test count
uv run pytest --co -q | tail -1
```

**Rule**: If grep returns nothing, don't create acceptance criteria for it.

### 2. Acceptance Criteria Patterns

| Type | BAD | GOOD |
|------|-----|------|
| New tool | "Add compile support" | "`compile_latex` accepts `engine: str` param with values `pdflatex`, `xelatex`, `lualatex`, `latexmk`" |
| Testing | "Add tests" | "`test_compile.py` has `TestCompileEngine` with tests: default, each engine, invalid engine" |
| Server | "Update server" | "`server.py` tool schema has `engine` field with `enum` constraint" |
| Docs | "Update docs" | "`LLM_REFERENCE.md` has `engine` in compile_latex params table" |

### 3. Test-to-Criteria Mapping

Each acceptance criterion should have a corresponding test:

| Acceptance Criterion | Test Function |
|---------------------|---------------|
| `engine` param defaults to `"pdflatex"` | `test_default_engine_is_pdflatex()` |
| Invalid engine raises error | `test_invalid_engine_raises_error()` |
| `xelatex` compiles successfully | `test_engine_xelatex()` |
| `passes="auto"` detects rerun | `test_auto_passes_detects_rerun()` |

### 4. Verification Command Reference

```bash
# File operations
test -f file.py                    # File exists
test ! -f file.py                  # File doesn't exist

# Content checks
grep -q "exact string" file.py     # Contains string (quiet)
grep -c "pattern" file.py          # Count matches

# Python checks
uv run python -c "from mcp_latex_tools.tools.compile import compile_latex"
uv run python -c "from mcp_latex_tools.tools.compile import SUPPORTED_ENGINES; assert 'xelatex' in SUPPORTED_ENGINES"

# Quality checks
uv run pytest tests/ -v --tb=short
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
```

### 5. Task Size Guidelines

| Lines Changed | Guidance |
|---------------|----------|
| <100 | Single commit, single PR |
| 100-500 | Ideal PR size, 2-5 atomic commits |
| 500-1000 | Acceptable, consider splitting |
| >1000 | **Must split** into Part 1, Part 2, etc. |

### 6. Status Indicators

| Status | Meaning |
|--------|---------|
| 🔲 PENDING | Not started |
| 🔄 IN PROGRESS | Work underway |
| ✅ COMPLETE | Done, verified, merged |
| 🚫 BLOCKED | Waiting on dependency |
| ⏸️ DEFERRED | Moved to backlog |

---

## Compact Format (for Simple Tasks)

For straightforward tasks (<100 lines, single file):

```markdown
### {TASK_ID}: {Task Title}

**User Story**: As a [role], I want [feature] so that [benefit].
**Points**: N | **Priority**: HIGH | **Status**: 🔲 | **Branch**: `{TASK_ID}-description`

**Acceptance Criteria**:
- [ ] `file.py` has `function(arg: Type) -> ReturnType`
- [ ] `test_file.py` covers: happy path, edge case, error case
- [ ] `uv run pytest test_file.py && uv run mypy src/` passes

**Verification**: `test -f file.py && grep -q "function" file.py && uv run pytest tests/test_file.py`
```

---

## Anti-Patterns to Avoid

### Vague Criteria
```markdown
# BAD
- [ ] Add multi-engine support
- [ ] Write tests
- [ ] Update documentation

# GOOD
- [ ] `compile_latex()` accepts `engine` param: "pdflatex", "xelatex", "lualatex", "latexmk"
- [ ] `TestCompileEngine` has 8 tests: default, explicit pdflatex, xelatex, lualatex, latexmk, invalid, constant, command
- [ ] `LLM_REFERENCE.md` compile_latex table includes `engine` and `passes` params
```

### Criteria for Non-Existent Items
```markdown
# BAD (if nothing deprecated exists)
- [ ] Remove deprecated engine handling

# GOOD (after investigation)
# Investigation: grep -r "deprecated" returned 0 results
# Criterion removed - nothing to deprecate
```

### Unverifiable Criteria
```markdown
# BAD
- [ ] Code is well-structured
- [ ] Implementation is efficient

# GOOD
- [ ] All public functions have type annotations (mypy passes)
- [ ] Compilation completes in <30s for simple.tex (tested via timeout param)
```

---

## See Also

- [TASK_NAMING.md](./TASK_NAMING.md) - Task and branch naming conventions
- [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md) - Full development workflow
- [BACKLOG.md](./BACKLOG.md) - Feature backlog
- [../../CLAUDE.md](../../CLAUDE.md) - Project development guidelines

---

*Last Updated: 2026-04-06*
