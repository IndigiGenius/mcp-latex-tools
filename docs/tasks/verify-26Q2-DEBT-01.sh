#!/bin/bash
set -e

echo "=== 26Q2-DEBT-01: Test Organization Verification ==="

# 1. Subdirectories exist
echo "--- Checking subdirectories ---"
test -d tests/tools
test -d tests/utils
test -d tests/integration
echo "PASS: Subdirectories exist"

# 2. __init__.py files exist
echo "--- Checking __init__.py files ---"
test -f tests/tools/__init__.py
test -f tests/utils/__init__.py
test -f tests/integration/__init__.py
echo "PASS: __init__.py files exist"

# 3. Tool tests in correct location
echo "--- Checking tool tests ---"
test -f tests/tools/test_cleanup.py
test -f tests/tools/test_cleanup_edge_cases.py
test -f tests/tools/test_compile.py
test -f tests/tools/test_detect_packages.py
test -f tests/tools/test_pdf_info.py
test -f tests/tools/test_pdf_info_edge_cases.py
test -f tests/tools/test_validate.py
echo "PASS: Tool tests in place"

# 4. Utils tests in correct location
echo "--- Checking utils tests ---"
test -f tests/utils/test_log_parser.py
echo "PASS: Utils tests in place"

# 5. Integration tests in correct location
echo "--- Checking integration tests ---"
test -f tests/integration/test_mcp_resources_prompts.py
test -f tests/integration/test_server_error_handling.py
test -f tests/integration/test_server_integration.py
echo "PASS: Integration tests in place"

# 6. No test files left at top level (except __init__.py)
echo "--- Checking no stale test files at top level ---"
stale_count=$(find tests -maxdepth 1 -name "test_*.py" | wc -l)
if [ "$stale_count" -ne 0 ]; then
    echo "FAIL: Found $stale_count test files still at top level"
    find tests -maxdepth 1 -name "test_*.py"
    exit 1
fi
echo "PASS: No stale test files at top level"

# 7. Fixtures directory unchanged
echo "--- Checking fixtures ---"
test -d tests/fixtures
test -f tests/fixtures/simple.tex
test -f tests/fixtures/simple.pdf
echo "PASS: Fixtures intact"

# 8. All tests pass
echo "--- Running tests ---"
uv run pytest --tb=short -q

# 9. Code quality
echo "--- Running quality checks ---"
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/

echo ""
echo "=== All verification checks passed ==="
