# Task Naming Convention

**Version**: 1.0
**Created**: 2026-04-06
**Status**: Active

## Task Identifier Format

### Primary Format: `[YEAR][QUARTER]-[EPIC]-[SEQUENCE]`

**Example:** `26Q2-TOOL-01` (Year 2026, Q2, New Tool, Task 1)

### Components

#### 1. Year-Quarter Identifier (`YYQ#`)
- `26Q2` - 2026 Quarter 2 (Apr-Jun) -- **Current Quarter**
- `26Q3` - 2026 Quarter 3 (Jul-Sep)
- `26Q4` - 2026 Quarter 4 (Oct-Dec)

#### 2. Epic/Category Codes

| Code | Description | Examples |
|------|-------------|----------|
| `TOOL` | New MCP tool implementation | compile engine support, bib_tools, create_document |
| `ENH` | Enhancement to existing tool | multi-pass, error recovery, new parameters |
| `FIX` | Bug fixes | URI comparison, parameter handling |
| `DOC` | Documentation | LLM_REFERENCE, ARCHITECTURE, README |
| `REFAC` | Code refactoring | Pydantic migration, test reorganization |
| `TEST` | Testing infrastructure | new test patterns, fixtures, CI |
| `INFRA` | Infrastructure & packaging | CI/CD, Docker, release automation |
| `DEBT` | Technical debt | type hints, dead code removal |

#### 3. Sequence Number (2-3 digits)
- Sequential within each epic per quarter (01, 02, 03...)
- Resets each quarter for each epic
- Leading zeros for consistent sorting
- Allows for insertion: `05a`, `05b` for related subtasks

## Usage

### Branch Naming
Task IDs map directly to branches:
- Task: `26Q2-ENH-01`
- Branch: `26Q2-ENH-01-multi-engine-compilation`

### Commit Messages
Reference task IDs using conventional commits:
```
feat(26Q2-ENH-01): add engine parameter to compile_latex
test(26Q2-ENH-01): add multi-engine compilation tests
docs(26Q2-ENH-01): update LLM_REFERENCE with engine param
```

### PR Titles
```
[26Q2-ENH-01] Multi-engine and multi-pass compilation
```

### Code Comments
```python
# TODO(26Q2-TOOL-01): Add template validation
# FIXME(26Q2-FIX-01): Handle edge case with empty .bib
```

## Special Cases

| Type | Format | Example |
|------|--------|---------|
| Hotfix | `YYQ#-HF-##` | `26Q2-HF-01` |
| Experimental | `YYQ#-RX-##` | `26Q2-RX-01` |

## Searching

```bash
# All Q2 2026 work
git log --grep="26Q2"

# All tool tasks
git log --grep="TOOL"

# Specific epic in quarter
git log --grep="26Q2-ENH"
```

---

*Last Updated: 2026-04-06*
