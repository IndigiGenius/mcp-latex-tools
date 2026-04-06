# CLAUDE.md

MCP LaTeX Tools is an MCP server providing LaTeX compilation and PDF analysis tools. Uses TDD methodology with modern Python tooling.

**Status**: Production Ready | 4 tools

## Commands

```bash
# Tests
uv run pytest                                    # Run all tests
uv run pytest --cov=src --cov-report=html       # With coverage

# Code quality (run before committing)
uv run ruff check src/ tests/ && uv run ruff format src/ tests/ && uv run mypy src/

# Run server
uv run python src/mcp_latex_tools/server.py
```

## Project Structure

```
src/mcp_latex_tools/
├── server.py        # MCP server entry point
├── tools/           # compile, validate, pdf_info, cleanup
└── utils/           # log_parser
tests/               # Test files and fixtures
docs/                # Documentation
docs/tasks/          # Task definitions (one per task ID)
```

## MCP Tools

| Tool | Purpose |
|------|---------|
| `compile_latex` | Compile .tex to PDF with error handling |
| `validate_latex` | Quick syntax validation (no compilation) |
| `pdf_info` | Extract PDF metadata (pages, dimensions) |
| `cleanup` | Remove auxiliary files (.aux, .log, etc.) |

## Development Workflow

All work follows the **10-step workflow** defined in `docs/development/DEVELOPMENT_WORKFLOW.md`:

1. **Task definition** - Write acceptance criteria + verification script in `docs/tasks/`
2. **Branch** - Create from main: `{TASK_ID}-description`
3. **TDD Red** - Write failing tests
4. **TDD Green** - Implement minimal code
5. **Quality gates** - `ruff format`, `ruff check`, `mypy`
6. **Documentation** - Update LLM_REFERENCE.md, ARCHITECTURE.md
7. **Issue + PR** - Push, create GitHub issue and PR
8. **Verification** - Run `bash docs/tasks/verify-{TASK_ID}.sh`
9. **Code review** - Agent or human review
10. **Merge** - Squash merge, update backlog

### Task Naming

Format: `[YEAR][QUARTER]-[EPIC]-[SEQUENCE]` (e.g., `26Q2-ENH-01`)

Epic codes: `TOOL`, `ENH`, `FIX`, `DOC`, `REFAC`, `TEST`, `INFRA`, `DEBT`

See `docs/development/TASK_NAMING.md` for full details.

### Development Rules

- **TDD**: Write failing tests first, implement minimal code, refactor
- **Tests are immutable**: Code must pass existing tests (unless intentionally changing behavior)
- **Type hints**: Enforced by mypy throughout
- **No duplication**: Extract common patterns to utils/
- **Small PRs**: Target <500 lines, max 1000
- **Atomic commits**: Each commit is a self-contained unit

## Documentation

| Document | Purpose |
|----------|---------|
| `docs/LLM_REFERENCE.md` | Quick reference for LLM agents |
| `docs/development/ARCHITECTURE.md` | System architecture |
| `docs/development/BACKLOG.md` | Feature backlog |
| `docs/development/DEVELOPMENT_WORKFLOW.md` | Full 10-step workflow |
| `docs/development/TASK_DEFINITION_STANDARD.md` | Task definition format |
| `docs/development/TASK_NAMING.md` | Task and branch naming |

---
*Last Updated: 2026-04-06*
