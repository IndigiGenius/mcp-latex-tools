#!/bin/bash
set -e

echo "=== 26Q2-ENH-02: Configuration System Verification ==="

# 1. Files exist
echo "1. Checking files exist..."
test -f src/mcp_latex_tools/config.py
test -f tests/test_config.py
echo "   OK"

# 2. Config models present
echo "2. Checking config models..."
grep -q "class ToolConfig" src/mcp_latex_tools/config.py
grep -q "class CompilationConfig" src/mcp_latex_tools/config.py
grep -q "class ValidationConfig" src/mcp_latex_tools/config.py
grep -q "class CleanupConfig" src/mcp_latex_tools/config.py
grep -q "class PdfInfoConfig" src/mcp_latex_tools/config.py
grep -q "class DetectPackagesConfig" src/mcp_latex_tools/config.py
echo "   OK"

# 3. Functions present
echo "3. Checking functions..."
grep -q "def find_config_file" src/mcp_latex_tools/config.py
grep -q "def load_config" src/mcp_latex_tools/config.py
echo "   OK"

# 4. Uses tomllib (stdlib)
echo "4. Checking tomllib usage..."
grep -q "tomllib" src/mcp_latex_tools/config.py
echo "   OK"

# 5. Server integration
echo "5. Checking server integration..."
grep -q "from mcp_latex_tools.config import" src/mcp_latex_tools/server.py
grep -q "_config" src/mcp_latex_tools/server.py
echo "   OK"

# 6. Import works
echo "6. Checking imports..."
uv run python -c "from mcp_latex_tools.config import ToolConfig, find_config_file, load_config; print('OK')"

# 7. Default values match current defaults
echo "7. Checking default values..."
uv run python -c "
from mcp_latex_tools.config import ToolConfig
cfg = ToolConfig()
assert cfg.compilation.engine == 'pdflatex'
assert cfg.compilation.passes == 1
assert cfg.compilation.timeout == 30
assert cfg.validation.quick is False
assert cfg.validation.strict is False
assert cfg.cleanup.dry_run is False
assert cfg.cleanup.recursive is False
assert cfg.cleanup.create_backup is False
assert cfg.cleanup.extensions is None
assert cfg.pdf_info.include_text is False
assert cfg.detect_packages.check_installed is True
print('OK')
"

# 8. Config tests pass
echo "8. Running config tests..."
uv run pytest tests/test_config.py -v --tb=short

# 9. Full suite (no regressions)
echo "9. Running full test suite..."
uv run pytest --tb=short -q

# 10. Code quality
echo "10. Running code quality checks..."
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/

echo ""
echo "=== All verification checks passed ==="
