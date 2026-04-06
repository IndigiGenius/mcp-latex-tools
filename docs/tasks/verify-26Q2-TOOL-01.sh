#!/bin/bash
set -e

echo "=== 26Q2-TOOL-01 Verification ==="

# 1. Module exists and imports
uv run python -c "
from mcp_latex_tools.tools.detect_packages import (
    detect_packages,
    PackageDetectionResult,
    PackageDetectionError,
)
print('Imports OK')
"

# 2. Function signature
uv run python -c "
from mcp_latex_tools.tools.detect_packages import detect_packages
import inspect
sig = inspect.signature(detect_packages)
assert 'file_path' in sig.parameters
assert 'check_installed' in sig.parameters
print('Signature OK')
"

# 3. Result dataclass fields
uv run python -c "
from mcp_latex_tools.tools.detect_packages import PackageDetectionResult
r = PackageDetectionResult(
    success=True,
    packages=['amsmath', 'geometry'],
    installed=['amsmath', 'geometry'],
    missing=[],
    install_commands=[],
)
assert r.success is True
assert r.error_message is None
assert r.file_path is None
assert r.detection_time_seconds is None
assert len(r.packages) == 2
print('PackageDetectionResult OK')
"

# 4. Server schema has detect_packages
grep -q '"detect_packages"' src/mcp_latex_tools/server.py
grep -q 'check_installed' src/mcp_latex_tools/server.py
echo "Server schema OK"

# 5. Test classes exist
grep -q "class TestPackageDetectionResult" tests/test_detect_packages.py
grep -q "class TestDetectPackagesParsing" tests/test_detect_packages.py
grep -q "class TestDetectPackagesInstalled" tests/test_detect_packages.py
grep -q "class TestDetectPackagesErrors" tests/test_detect_packages.py
echo "Test classes OK"

# 6. All detect_packages tests pass
uv run pytest tests/test_detect_packages.py -v --tb=short

# 7. Full suite passes (no regressions)
uv run pytest --tb=short -q

# 8. Code quality
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/

# 9. Docs updated
grep -q "detect_packages" docs/LLM_REFERENCE.md
grep -q "detect_packages" docs/development/ARCHITECTURE.md
echo "Docs OK"

echo ""
echo "=== All 26Q2-TOOL-01 verification checks passed ==="
