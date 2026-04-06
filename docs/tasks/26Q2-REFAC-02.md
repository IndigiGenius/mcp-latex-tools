### 26Q2-REFAC-02: Pydantic Migration Part 2 — Compilation and Package Detection Models

**User Story**: As a developer of mcp-latex-tools, I want to continue migrating dataclasses to Pydantic models so that all tool result classes benefit from automatic validation and JSON schema generation.

| Field | Value |
|-------|-------|
| **Story Points** | 3 |
| **Priority** | HIGH |
| **Status** | 🔲 PENDING |
| **Branch** | `26Q2-REFAC-02-pydantic-migration-p2` |
| **Dependencies** | 26Q2-REFAC-01 (complete) |
| **PR Size Target** | ~300-400 lines |

---

#### Context

**Current State**:
- Part 1 (26Q2-REFAC-01) migrated `LaTeXError`, `LogSummary`, `ValidationResult` — merged to main
- 4 dataclass result classes remain: `CompilationResult`, `PackageDetectionResult`, `CleanupResult`, `PDFInfoResult`
- This is Part 2 of 3: migrates `CompilationResult` (7 fields) and `PackageDetectionResult` (8 fields)
- Pydantic 2.11.7 available transitively via `mcp>=1.11.0`
- Part 1 review recommended: add `pydantic>=2.0` as explicit dependency before Part 2 merges
- 226 tests currently passing

**Investigation**:
```bash
$ grep -n "from dataclasses import dataclass" src/mcp_latex_tools/tools/compile.py
7:from dataclasses import dataclass

$ grep -n "from dataclasses import dataclass" src/mcp_latex_tools/tools/detect_packages.py
7:from dataclasses import dataclass

$ grep -c "CompilationResult" tests/test_compile.py
12

$ grep -c "PackageDetectionResult" tests/test_detect_packages.py
10

$ uv run pytest --co -q | tail -1
226 tests collected in 0.36s
```

---

#### Acceptance Criteria

**pyproject.toml — Explicit Pydantic Dependency**:
- [ ] `pydantic>=2.0` added to `dependencies` list in `pyproject.toml`
- [ ] `uv lock` succeeds with the updated dependency

**compile.py — CompilationResult Migration**:
- [ ] `CompilationResult` is a `pydantic.BaseModel` (not a dataclass)
- [ ] Fields preserved: `success: bool`, `output_path: Optional[str] = None`, `error_message: Optional[str] = None`, `log_content: Optional[str] = None`, `compilation_time_seconds: Optional[float] = None`, `engine: Optional[str] = None`, `passes_run: Optional[int] = None`
- [ ] `from dataclasses import dataclass` removed from compile.py
- [ ] `from pydantic import BaseModel` present in compile.py
- [ ] `CompilationResult` fields accessible via dot notation (unchanged API)

**detect_packages.py — PackageDetectionResult Migration**:
- [ ] `PackageDetectionResult` is a `pydantic.BaseModel` (not a dataclass)
- [ ] Fields preserved: `success: bool`, `packages: list[str]`, `installed: list[str]`, `missing: list[str]`, `install_commands: list[str]`, `error_message: Optional[str] = None`, `file_path: Optional[str] = None`, `detection_time_seconds: Optional[float] = None`
- [ ] `from dataclasses import dataclass` removed from detect_packages.py
- [ ] `from pydantic import BaseModel` present in detect_packages.py
- [ ] `PackageDetectionResult` fields accessible via dot notation (unchanged API)

**Backwards Compatibility**:
- [ ] All 226 existing tests pass without modification
- [ ] `server.py` handlers for `compile_latex` and `detect_packages` work unchanged
- [ ] No changes to function signatures of `compile_latex()`, `detect_packages()`, or any public API
- [ ] Remaining dataclass result classes (`CleanupResult`, `PDFInfoResult`) remain as dataclasses

**Tests**:
- [ ] All existing tests in `tests/test_compile.py` pass
- [ ] All existing tests in `tests/test_detect_packages.py` pass
- [ ] Full test suite passes: `uv run pytest`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Lint passes: `uv run ruff check src/ tests/`
- [ ] Format passes: `uv run ruff format --check src/ tests/`

**Documentation**:
- [ ] `docs/development/ARCHITECTURE.md` migration status table updated for `CompilationResult` and `PackageDetectionResult`

---

#### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `pyproject.toml` | MODIFY | Add `pydantic>=2.0` as explicit dependency |
| `src/mcp_latex_tools/tools/compile.py` | MODIFY | Migrate `CompilationResult` from dataclass to BaseModel |
| `src/mcp_latex_tools/tools/detect_packages.py` | MODIFY | Migrate `PackageDetectionResult` from dataclass to BaseModel |
| `docs/development/ARCHITECTURE.md` | MODIFY | Update migration status table |

---

#### Implementation Notes

- **Same pattern as Part 1**: Replace `from dataclasses import dataclass` with `from pydantic import BaseModel`, change `@dataclass class Foo:` to `class Foo(BaseModel):`
- **Explicit pydantic dependency**: Add `pydantic>=2.0` to `pyproject.toml` dependencies per Part 1 review recommendation. This makes the dependency graph honest instead of relying on transitive availability via `mcp`.
- **CompilationResult has Union type in callers**: `compile_latex()` accepts `passes: Union[int, str]` — this is a parameter type, not a result field, so it is unaffected by the migration
- **PackageDetectionResult uses list[str] (lowercase)**: This is valid in Python 3.11+ and works with both dataclasses and Pydantic
- **Existing tests must pass unchanged** — this is a refactoring, not a behavior change

---

#### Verification Script

```bash
#!/bin/bash
set -e

echo "=== 26Q2-REFAC-02 Verification ==="

# 1. Pydantic is an explicit dependency
grep -q 'pydantic>=2.0' pyproject.toml
echo "Explicit pydantic dependency OK"

# 2. CompilationResult is a Pydantic BaseModel
uv run python -c "
from mcp_latex_tools.tools.compile import CompilationResult
from pydantic import BaseModel
assert issubclass(CompilationResult, BaseModel), 'CompilationResult is not a BaseModel'
r = CompilationResult(success=True)
assert r.output_path is None
assert r.error_message is None
assert r.log_content is None
assert r.compilation_time_seconds is None
assert r.engine is None
assert r.passes_run is None
print('CompilationResult OK')
"

# 3. PackageDetectionResult is a Pydantic BaseModel
uv run python -c "
from mcp_latex_tools.tools.detect_packages import PackageDetectionResult
from pydantic import BaseModel
assert issubclass(PackageDetectionResult, BaseModel), 'PackageDetectionResult is not a BaseModel'
r = PackageDetectionResult(
    success=True,
    packages=['amsmath'],
    installed=['amsmath'],
    missing=[],
    install_commands=[],
)
assert r.error_message is None
assert r.file_path is None
assert r.detection_time_seconds is None
print('PackageDetectionResult OK')
"

# 4. No dataclass imports in migrated files
! grep -q "from dataclasses import dataclass" src/mcp_latex_tools/tools/compile.py
echo "compile.py: no dataclass import OK"
! grep -q "from dataclasses import dataclass" src/mcp_latex_tools/tools/detect_packages.py
echo "detect_packages.py: no dataclass import OK"

# 5. Pydantic import present in migrated files
grep -q "from pydantic import BaseModel" src/mcp_latex_tools/tools/compile.py
grep -q "from pydantic import BaseModel" src/mcp_latex_tools/tools/detect_packages.py
echo "Pydantic imports OK"

# 6. Remaining classes still use dataclasses (not yet migrated)
grep -q "from dataclasses import dataclass" src/mcp_latex_tools/tools/cleanup.py
grep -q "from dataclasses import dataclass" src/mcp_latex_tools/tools/pdf_info.py
echo "Non-migrated classes still dataclasses OK"

# 7. Compile tests pass
uv run pytest tests/test_compile.py -v --tb=short

# 8. Detect packages tests pass
uv run pytest tests/test_detect_packages.py -v --tb=short

# 9. Full suite passes (no regressions)
uv run pytest --tb=short -q

# 10. Code quality
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/

# 11. Docs updated
grep -q "CompilationResult.*Pydantic" docs/development/ARCHITECTURE.md
grep -q "PackageDetectionResult.*Pydantic" docs/development/ARCHITECTURE.md
echo "Docs OK"

echo ""
echo "=== All 26Q2-REFAC-02 verification checks passed ==="
```

---

#### Definition of Done

- [ ] All acceptance criteria checked off
- [ ] Verification script exits with code 0
- [ ] Code quality checks pass (`ruff format`, `ruff check`, `mypy`)
- [ ] PR created with <500 lines changed
- [ ] All 226+ existing tests pass unchanged
- [ ] Documentation updated (ARCHITECTURE.md)
