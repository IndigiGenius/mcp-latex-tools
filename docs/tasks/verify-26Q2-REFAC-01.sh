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
