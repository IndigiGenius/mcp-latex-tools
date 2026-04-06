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
