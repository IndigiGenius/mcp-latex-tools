### 26Q2-REFAC-03: Pydantic Migration Part 3 — Cleanup and PDF Info Models

**User Story**: As a developer of mcp-latex-tools, I want to complete the Pydantic migration so that all result classes use BaseModel for consistent validation and serialization.

| Field | Value |
|-------|-------|
| **Story Points** | 3 |
| **Priority** | HIGH |
| **Status** | 🔲 PENDING |
| **Branch** | `26Q2-REFAC-03-pydantic-migration-p3` |
| **Dependencies** | 26Q2-REFAC-01 (complete), 26Q2-REFAC-02 (complete) |
| **PR Size Target** | ~300-400 lines |

---

#### Context

**Current State**:
- Parts 1-2 migrated 5 of 7 classes: `LaTeXError`, `LogSummary`, `ValidationResult`, `CompilationResult`, `PackageDetectionResult`
- This is Part 3 of 3: migrates the final 2 classes — `CleanupResult` (12 fields) and `PDFInfoResult` (20 fields)
- `pydantic>=2.0` is already an explicit dependency (added in Part 2)
- 226 tests currently passing
- **Key pattern**: Both classes are constructed early with initial values, then **mutated** throughout their functions. Pydantic BaseModel is mutable by default, so this is safe.
- `CleanupResult` has NO default values — all 12 fields are required at construction
- `PDFInfoResult` has NO default values — all 20 fields are required at construction
- After this PR, all `from dataclasses import dataclass` imports will be removed from the project

**Investigation**:
```bash
$ grep -n "from dataclasses import dataclass" src/mcp_latex_tools/tools/cleanup.py
6:from dataclasses import dataclass

$ grep -n "from dataclasses import dataclass" src/mcp_latex_tools/tools/pdf_info.py
4:from dataclasses import dataclass

$ grep -c "result\." src/mcp_latex_tools/tools/cleanup.py
18  # CleanupResult is mutated after construction

$ grep -c "result\." src/mcp_latex_tools/tools/pdf_info.py
32  # PDFInfoResult is mutated after construction

$ grep -rn "from dataclasses import dataclass" src/
src/mcp_latex_tools/tools/cleanup.py:6
src/mcp_latex_tools/tools/pdf_info.py:4
# Only 2 remaining — this PR eliminates all dataclass usage

$ uv run pytest --co -q | tail -1
226 tests collected in 0.59s
```

---

#### Acceptance Criteria

**cleanup.py — CleanupResult Migration**:
- [ ] `CleanupResult` is a `pydantic.BaseModel` (not a dataclass)
- [ ] All 12 fields preserved: `success: bool`, `error_message: Optional[str]`, `tex_file_path: Optional[str]`, `directory_path: Optional[str]`, `cleaned_files_count: int`, `cleaned_files: List[str]`, `would_clean_files: List[str]`, `dry_run: bool`, `recursive: bool`, `backup_created: bool`, `backup_directory: Optional[str]`, `cleanup_time_seconds: Optional[float]`
- [ ] `from dataclasses import dataclass` removed from cleanup.py
- [ ] `from pydantic import BaseModel` present in cleanup.py
- [ ] Field mutation after construction still works (mutable by default)

**pdf_info.py — PDFInfoResult Migration**:
- [ ] `PDFInfoResult` is a `pydantic.BaseModel` (not a dataclass)
- [ ] All 20 fields preserved: `success: bool`, `error_message: Optional[str]`, `file_path: str`, `file_size_bytes: int`, `page_count: int`, `page_dimensions: List[Dict[str, Any]]`, `pdf_version: Optional[str]`, `is_encrypted: bool`, `is_linearized: Optional[bool]`, `creation_date: Optional[str]`, `modification_date: Optional[str]`, `title: Optional[str]`, `author: Optional[str]`, `subject: Optional[str]`, `keywords: Optional[str]`, `producer: Optional[str]`, `creator: Optional[str]`, `text_content: Optional[List[str]]`, `extraction_time_seconds: Optional[float]`
- [ ] `from dataclasses import dataclass` removed from pdf_info.py
- [ ] `from pydantic import BaseModel` present in pdf_info.py
- [ ] Field mutation after construction still works (mutable by default)

**Complete Migration**:
- [ ] Zero `from dataclasses import dataclass` imports remain in `src/`
- [ ] All 7 result classes are now Pydantic BaseModel subclasses

**Backwards Compatibility**:
- [ ] All 226 existing tests pass without modification
- [ ] `server.py` handlers for `cleanup` and `pdf_info` work unchanged
- [ ] No changes to function signatures of `clean_latex()`, `extract_pdf_info()`, or any public API

**Tests**:
- [ ] All existing tests in `tests/test_cleanup.py` pass
- [ ] All existing tests in `tests/test_cleanup_edge_cases.py` pass
- [ ] All existing tests in `tests/test_pdf_info.py` pass
- [ ] All existing tests in `tests/test_pdf_info_edge_cases.py` pass
- [ ] Full test suite passes: `uv run pytest`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Lint passes: `uv run ruff check src/ tests/`
- [ ] Format passes: `uv run ruff format --check src/ tests/`

**Documentation**:
- [ ] `docs/development/ARCHITECTURE.md` migration status table shows all 7 classes as Pydantic BaseModel
- [ ] ARCHITECTURE.md code example updated to reflect completed migration

---

#### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/mcp_latex_tools/tools/cleanup.py` | MODIFY | Migrate `CleanupResult` from dataclass to BaseModel |
| `src/mcp_latex_tools/tools/pdf_info.py` | MODIFY | Migrate `PDFInfoResult` from dataclass to BaseModel |
| `docs/development/ARCHITECTURE.md` | MODIFY | Finalize migration status table |

---

#### Implementation Notes

- **Same pattern as Parts 1-2**: Replace `from dataclasses import dataclass` with `from pydantic import BaseModel`, change `@dataclass class Foo:` to `class Foo(BaseModel):`
- **Mutation is safe**: Both classes are mutated after construction (`result.success = True`, `result.page_count = ...`, etc.). Pydantic v2 BaseModel is mutable by default — no `ConfigDict(frozen=True)` is set, so field assignment works identically to dataclasses.
- **No default values**: Unlike previous migrations, ALL fields in these classes are required. This means construction sites must pass every field — they already do.
- **`List[str]` vs `list[str]`**: `cleanup.py` uses `List[str]` (from typing), `pdf_info.py` uses `List[Dict[str, Any]]`. Both work with Pydantic.
- **Final migration**: After this PR, `from dataclasses import dataclass` will no longer appear anywhere in `src/`.
- **Existing tests must pass unchanged** — this is a refactoring, not a behavior change

---

#### Verification Script

```bash
#!/bin/bash
set -e

echo "=== 26Q2-REFAC-03 Verification ==="

# 1. CleanupResult is a Pydantic BaseModel
uv run python -c "
from mcp_latex_tools.tools.cleanup import CleanupResult
from pydantic import BaseModel
assert issubclass(CleanupResult, BaseModel), 'CleanupResult is not a BaseModel'
r = CleanupResult(
    success=True, error_message=None, tex_file_path=None,
    directory_path='/tmp', cleaned_files_count=0, cleaned_files=[],
    would_clean_files=[], dry_run=False, recursive=False,
    backup_created=False, backup_directory=None, cleanup_time_seconds=0.1,
)
# Verify mutation works
r.success = False
assert r.success is False
print('CleanupResult OK')
"

# 2. PDFInfoResult is a Pydantic BaseModel
uv run python -c "
from mcp_latex_tools.tools.pdf_info import PDFInfoResult
from pydantic import BaseModel
assert issubclass(PDFInfoResult, BaseModel), 'PDFInfoResult is not a BaseModel'
r = PDFInfoResult(
    success=True, error_message=None, file_path='/tmp/test.pdf',
    file_size_bytes=1024, page_count=1, page_dimensions=[],
    pdf_version='1.7', is_encrypted=False, is_linearized=False,
    creation_date=None, modification_date=None, title=None,
    author=None, subject=None, keywords=None, producer=None,
    creator=None, text_content=None, extraction_time_seconds=0.1,
)
# Verify mutation works
r.page_count = 5
assert r.page_count == 5
print('PDFInfoResult OK')
"

# 3. No dataclass imports remain anywhere in src/
! grep -rq "from dataclasses import dataclass" src/
echo "No dataclass imports remain in src/ OK"

# 4. Pydantic import present in migrated files
grep -q "from pydantic import BaseModel" src/mcp_latex_tools/tools/cleanup.py
grep -q "from pydantic import BaseModel" src/mcp_latex_tools/tools/pdf_info.py
echo "Pydantic imports OK"

# 5. Cleanup tests pass
uv run pytest tests/test_cleanup.py tests/test_cleanup_edge_cases.py -v --tb=short

# 6. PDF info tests pass
uv run pytest tests/test_pdf_info.py tests/test_pdf_info_edge_cases.py -v --tb=short

# 7. Full suite passes (no regressions)
uv run pytest --tb=short -q

# 8. Code quality
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/

# 9. All 7 classes migrated in docs
grep -q "CleanupResult.*Pydantic" docs/development/ARCHITECTURE.md
grep -q "PDFInfoResult.*Pydantic" docs/development/ARCHITECTURE.md
echo "Docs OK"

echo ""
echo "=== All 26Q2-REFAC-03 verification checks passed ==="
```

---

#### Definition of Done

- [ ] All acceptance criteria checked off
- [ ] Verification script exits with code 0
- [ ] Code quality checks pass (`ruff format`, `ruff check`, `mypy`)
- [ ] PR created with <500 lines changed
- [ ] All 226+ existing tests pass unchanged
- [ ] Documentation updated (ARCHITECTURE.md)
- [ ] Zero `from dataclasses import dataclass` remaining in `src/`
