#!/bin/bash
set -e

echo "=== 26Q2-ENH-01 Verification ==="

# 1. SUPPORTED_ENGINES constant exists with all 4 engines
uv run python -c "
from mcp_latex_tools.tools.compile import SUPPORTED_ENGINES
assert 'pdflatex' in SUPPORTED_ENGINES
assert 'xelatex' in SUPPORTED_ENGINES
assert 'lualatex' in SUPPORTED_ENGINES
assert 'latexmk' in SUPPORTED_ENGINES
print('SUPPORTED_ENGINES OK')
"

# 2. New params accepted
uv run python -c "
from mcp_latex_tools.tools.compile import compile_latex
import inspect
sig = inspect.signature(compile_latex)
assert 'engine' in sig.parameters
assert 'passes' in sig.parameters
print('Params OK')
"

# 3. CompilationResult has new fields
uv run python -c "
from mcp_latex_tools.tools.compile import CompilationResult
r = CompilationResult(success=True, engine='xelatex', passes_run=2)
assert r.engine == 'xelatex'
assert r.passes_run == 2
print('CompilationResult OK')
"

# 4. Server schema has engine and passes
grep -q '"engine"' src/mcp_latex_tools/server.py
grep -q '"passes"' src/mcp_latex_tools/server.py
echo "Server schema OK"

# 5. Test classes exist
grep -q "class TestCompileEngine" tests/test_compile.py
grep -q "class TestCompilePasses" tests/test_compile.py
grep -q "class TestCompileBibliography" tests/test_compile.py
grep -q "class TestCompilationResultNewFields" tests/test_compile.py
echo "Test classes OK"

# 6. All compile tests pass
uv run pytest tests/test_compile.py -v --tb=short

# 7. Full suite passes (no regressions)
uv run pytest --tb=short -q

# 8. Code quality
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/

# 9. Docs updated
grep -q "engine" docs/LLM_REFERENCE.md
grep -q "passes" docs/LLM_REFERENCE.md
echo "Docs OK"

echo ""
echo "=== All 26Q2-ENH-01 verification checks passed ==="
