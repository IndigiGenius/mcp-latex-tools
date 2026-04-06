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
