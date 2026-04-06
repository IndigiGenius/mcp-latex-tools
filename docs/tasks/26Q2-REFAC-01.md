### 26Q2-REFAC-01: Pydantic Migration Part 1 — Utility and Validation Models

**User Story**: As a developer of mcp-latex-tools, I want to migrate dataclasses to Pydantic models so that I get automatic validation, richer serialization, and JSON schema generation for MCP tool results.

| Field | Value |
|-------|-------|
| **Story Points** | 3 |
| **Priority** | HIGH |
| **Status** | 🔲 PENDING |
| **Branch** | `26Q2-REFAC-01-pydantic-migration-p1` |
| **Dependencies** | None |
| **PR Size Target** | ~300-400 lines |

---

#### Context

**Current State**:
- 7 dataclass result classes across 6 source files, all using `from dataclasses import dataclass`
- This is Part 1 of 3: migrates `LaTeXError`, `LogSummary` (log_parser.py) and `ValidationResult` (validate.py) — the 3 smallest classes (4-6 fields each)
- Pydantic 2.11.7 is already available as a transitive dependency of `mcp>=1.11.0` — no new dependency needed
- 226 tests currently passing across the full suite
- All result classes are consumed via attribute access (dot notation) — Pydantic BaseModel preserves this interface
- No existing JSON schema automation; schemas in `docs/schemas/mcp-tools.json` are manually written

**Investigation**:
```bash
$ uv run python -c "import pydantic; print(pydantic.__version__)"
2.11.7

$ grep -n "from dataclasses import dataclass" src/mcp_latex_tools/utils/log_parser.py
4:from dataclasses import dataclass

$ grep -n "from dataclasses import dataclass" src/mcp_latex_tools/tools/validate.py
5:from dataclasses import dataclass

$ grep -c "LaTeXError\|LogSummary" tests/test_log_parser.py
13

$ grep -c "ValidationResult" tests/test_validate.py
8

$ uv run pytest --co -q | tail -1
226 tests collected in 0.49s
```

---

#### Acceptance Criteria

**log_parser.py — LaTeXError Migration**:
- [ ] `LaTeXError` is a `pydantic.BaseModel` (not a dataclass)
- [ ] Fields preserved: `line_number: Optional[int]`, `error_type: str`, `message: str`, `context: Optional[str] = None`
- [ ] `from dataclasses import dataclass` removed from log_parser.py
- [ ] `from pydantic import BaseModel` present in log_parser.py
- [ ] `LaTeXError` instances are still created with keyword arguments throughout codebase
- [ ] `LaTeXError` fields accessible via dot notation (unchanged API)

**log_parser.py — LogSummary Migration**:
- [ ] `LogSummary` is a `pydantic.BaseModel` (not a dataclass)
- [ ] Fields preserved: `errors: List[LaTeXError]`, `warnings_count: int`, `pages_count: Optional[int] = None`, `has_undefined_references: bool = False`, `has_rerun_suggestion: bool = False`
- [ ] `LogSummary` instances are still created with keyword arguments throughout codebase
- [ ] `LogSummary.errors` validates that elements are `LaTeXError` instances

**validate.py — ValidationResult Migration**:
- [ ] `ValidationResult` is a `pydantic.BaseModel` (not a dataclass)
- [ ] Fields preserved: `is_valid: bool`, `error_message: Optional[str]`, `errors: list[str]`, `warnings: list[str]`, `validation_time_seconds: Optional[float] = None`
- [ ] `from dataclasses import dataclass` removed from validate.py
- [ ] `from pydantic import BaseModel` present in validate.py
- [ ] `ValidationResult` instances are still created with keyword arguments throughout codebase
- [ ] `ValidationResult` fields accessible via dot notation (unchanged API)

**Backwards Compatibility**:
- [ ] All 226 existing tests pass without modification (tests are immutable)
- [ ] `server.py` handlers for `validate` and `compile` (which uses log parser) work unchanged
- [ ] No changes to function signatures of `parse_latex_log()`, `validate_latex()`, or any public API
- [ ] Other dataclass-based result classes (`CompilationResult`, `CleanupResult`, `PDFInfoResult`, `PackageDetectionResult`) remain as dataclasses (unchanged)

**Tests**:
- [ ] All existing tests in `tests/test_log_parser.py` pass (18 tests)
- [ ] All existing tests in `tests/test_validate.py` pass (11 tests)
- [ ] Full test suite passes: `uv run pytest`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Lint passes: `uv run ruff check src/ tests/`
- [ ] Format passes: `uv run ruff format --check src/ tests/`

**Documentation**:
- [ ] `docs/development/ARCHITECTURE.md` notes Pydantic migration status (which classes migrated, which remain)

---

#### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/mcp_latex_tools/utils/log_parser.py` | MODIFY | Migrate `LaTeXError` and `LogSummary` from dataclass to BaseModel |
| `src/mcp_latex_tools/tools/validate.py` | MODIFY | Migrate `ValidationResult` from dataclass to BaseModel |
| `docs/development/ARCHITECTURE.md` | MODIFY | Note Pydantic migration progress |

---

#### Implementation Notes

- **Drop-in replacement**: Pydantic `BaseModel` supports the same keyword-argument construction and dot-notation access as dataclasses — the migration should be transparent to all consumers
- **Import swap**: Replace `from dataclasses import dataclass` with `from pydantic import BaseModel`, and change `@dataclass` class decorator to `class Foo(BaseModel):`
- **No `@dataclass` decorator**: Pydantic models use class inheritance, not decorators
- **Frozen models**: Consider `model_config = ConfigDict(frozen=True)` to preserve the immutability that dataclasses had by default — but only if existing code doesn't mutate result fields (investigation shows no mutation)
- **Type compatibility**: Pydantic 2.x with `List[X]` and `Optional[X]` types works identically to dataclass field annotations
- **Do NOT add pydantic to pyproject.toml dependencies** — it's already available transitively via `mcp>=1.11.0`. Adding it explicitly is a decision for a later task if desired.
- **Existing tests must pass unchanged** — this is a refactoring, not a behavior change

---

#### Verification Script

```bash
#!/bin/bash
set -e

echo "=== 26Q2-REFAC-01 Verification ==="

# 1. LaTeXError is a Pydantic BaseModel
uv run python -c "
from mcp_latex_tools.utils.log_parser import LaTeXError
from pydantic import BaseModel
assert issubclass(LaTeXError, BaseModel), 'LaTeXError is not a BaseModel'
e = LaTeXError(line_number=42, error_type='LaTeX Error', message='test')
assert e.line_number == 42
assert e.context is None
print('LaTeXError OK')
"

# 2. LogSummary is a Pydantic BaseModel
uv run python -c "
from mcp_latex_tools.utils.log_parser import LogSummary, LaTeXError
from pydantic import BaseModel
assert issubclass(LogSummary, BaseModel), 'LogSummary is not a BaseModel'
s = LogSummary(errors=[], warnings_count=0)
assert s.pages_count is None
assert s.has_undefined_references is False
assert s.has_rerun_suggestion is False
print('LogSummary OK')
"

# 3. ValidationResult is a Pydantic BaseModel
uv run python -c "
from mcp_latex_tools.tools.validate import ValidationResult
from pydantic import BaseModel
assert issubclass(ValidationResult, BaseModel), 'ValidationResult is not a BaseModel'
r = ValidationResult(is_valid=True, error_message=None, errors=[], warnings=[])
assert r.validation_time_seconds is None
print('ValidationResult OK')
"

# 4. No dataclass imports in migrated files
! grep -q "from dataclasses import dataclass" src/mcp_latex_tools/utils/log_parser.py
echo "log_parser.py: no dataclass import OK"
! grep -q "from dataclasses import dataclass" src/mcp_latex_tools/tools/validate.py
echo "validate.py: no dataclass import OK"

# 5. Pydantic import present in migrated files
grep -q "from pydantic import BaseModel" src/mcp_latex_tools/utils/log_parser.py
grep -q "from pydantic import BaseModel" src/mcp_latex_tools/tools/validate.py
echo "Pydantic imports OK"

# 6. Other result classes still use dataclasses (not yet migrated)
grep -q "from dataclasses import dataclass" src/mcp_latex_tools/tools/compile.py
grep -q "from dataclasses import dataclass" src/mcp_latex_tools/tools/cleanup.py
grep -q "from dataclasses import dataclass" src/mcp_latex_tools/tools/pdf_info.py
grep -q "from dataclasses import dataclass" src/mcp_latex_tools/tools/detect_packages.py
echo "Non-migrated classes still dataclasses OK"

# 7. Log parser tests pass
uv run pytest tests/test_log_parser.py -v --tb=short

# 8. Validate tests pass
uv run pytest tests/test_validate.py -v --tb=short

# 9. Full suite passes (no regressions)
uv run pytest --tb=short -q

# 10. Code quality
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/

# 11. Docs updated
grep -q "Pydantic" docs/development/ARCHITECTURE.md
echo "Docs OK"

echo ""
echo "=== All 26Q2-REFAC-01 verification checks passed ==="
```

---

#### Definition of Done

- [ ] All acceptance criteria checked off
- [ ] Verification script exits with code 0
- [ ] Code quality checks pass (`ruff format`, `ruff check`, `mypy`)
- [ ] PR created with <500 lines changed
- [ ] All 226+ existing tests pass unchanged
- [ ] Documentation updated (ARCHITECTURE.md)
