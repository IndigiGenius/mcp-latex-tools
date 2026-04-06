# Development Workflow

**Version**: 1.0
**Created**: 2026-04-06
**Status**: Active

## Overview

This document defines the complete development workflow for mcp-latex-tools. Every feature, enhancement, or fix follows these 10 steps to ensure quality, traceability, and maintainability.

---

## The 10-Step Workflow

```
 1. Task Definition     Write acceptance criteria + verification script
 2. Branch Creation     Create branch from main using naming convention
 3. TDD Red Phase       Write failing tests from acceptance criteria
 4. TDD Green Phase     Implement minimal code to pass tests
 5. Code Quality        ruff format, ruff check, mypy
 6. Documentation       Update LLM_REFERENCE.md, ARCHITECTURE.md
 7. Issue + PR          Create GitHub issue, push branch, open PR
 8. Verification        Run acceptance/verification script
 9. Code Review         Agent or human review, fix issues
10. Merge + Backlog     Merge PR, update BACKLOG.md
```

---

## Step 1: Task Definition

Write the task definition **before writing any code**. The task definition is the contract — it defines "done".

Follow the format in [TASK_DEFINITION_STANDARD.md](./TASK_DEFINITION_STANDARD.md).

**Key requirements:**
- Every acceptance criterion must be verifiable with a single command
- Include a verification script that exits 0 when all criteria are met
- Investigate current state before writing criteria (grep, test -f, etc.)
- Map each criterion to a test function

**Output:** Task definition file at `docs/tasks/{TASK_ID}.md`

---

## Step 2: Branch Creation

```bash
# Sync with main
git checkout main && git pull

# Create branch using naming convention
git checkout -b {TASK_ID}-short-description
# Example: git checkout -b 26Q2-ENH-01-multi-engine-compilation
```

See [TASK_NAMING.md](./TASK_NAMING.md) for naming conventions.

---

## Step 3: TDD Red Phase

Write tests **first**, before any implementation. Tests should trace directly to acceptance criteria.

```bash
# Write test file
# tests/test_feature.py

# Verify tests FAIL (feature doesn't exist yet)
uv run pytest tests/test_feature.py -v
# Expected: ImportError or assertion failures

# Commit failing tests
git add tests/
git commit -m "test({TASK_ID}): add tests for {feature description}"
```

**Test template:**
```python
class TestFeatureHappyPath:
    def test_default_behavior(self):
        """Test normal operation with defaults."""
        ...

    def test_explicit_params(self):
        """Test with explicit parameter values."""
        ...

class TestFeatureEdgeCases:
    def test_boundary_value(self):
        """Test at boundary conditions."""
        ...

class TestFeatureErrors:
    def test_invalid_input_raises(self):
        """Test error on invalid input."""
        with pytest.raises(ExpectedError):
            ...
```

---

## Step 4: TDD Green Phase

Implement **only enough code** to make all tests pass. No extras.

```bash
# Implement in src/mcp_latex_tools/
# Run tests until passing
uv run pytest tests/test_feature.py -v

# Run full suite to catch regressions
uv run pytest --tb=short -q

# Commit implementation
git add src/
git commit -m "feat({TASK_ID}): implement {feature description}"
```

**Principles:**
- Write minimal code to pass tests
- Don't add features not covered by tests
- If you discover new requirements, add tests first, then code
- Keep commits small and atomic

---

## Step 5: Code Quality Gates

All three must pass before proceeding:

```bash
# Format
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

Fix any issues, then commit:
```bash
git add -u
git commit -m "style({TASK_ID}): fix formatting and type issues"
```

---

## Step 6: Documentation

Update documentation that reflects the changes:

| Document | When to update |
|----------|----------------|
| `docs/LLM_REFERENCE.md` | New/changed tool params, workflows, or error patterns |
| `docs/development/ARCHITECTURE.md` | New files, structural changes, new patterns |
| `CLAUDE.md` | New commands, changed project structure |

```bash
git add docs/
git commit -m "docs({TASK_ID}): update {doc} with {change description}"
```

---

## Step 7: Issue + PR

### Create GitHub Issue
```bash
gh issue create \
  --title "[{TASK_ID}] {Task Title}" \
  --body "$(cat docs/tasks/{TASK_ID}.md)"
```

### Push and Create PR
```bash
git push -u origin {TASK_ID}-short-description

gh pr create --title "[{TASK_ID}] {Task Title}" --body "$(cat <<'EOF'
## Summary
Implements {TASK_ID}: {description}

## Changes
- {bullet points of what changed}

## Verification
```bash
$ bash docs/tasks/verify-{TASK_ID}.sh
All verification checks passed
```

## Checklist
- [ ] All acceptance criteria met
- [ ] Verification script passes
- [ ] Tests pass (uv run pytest)
- [ ] Code quality passes (ruff, mypy)
- [ ] Documentation updated

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Step 8: Verification

Run the verification script from the task definition:

```bash
bash docs/tasks/verify-{TASK_ID}.sh
```

The script must exit with code 0. If it fails:
1. Fix the issue
2. Re-run the script
3. Commit the fix
4. Push to update PR

---

## Step 9: Code Review

Request a code review (agent or human):

```bash
# Agent review via Claude Code
# The reviewer checks:
# - Code correctness and test coverage
# - Adherence to project patterns
# - No regressions in existing tests
# - Documentation accuracy
# - PR size (<500 lines target)
```

If changes are requested:
1. Make the changes
2. Re-run quality gates (Step 5)
3. Re-run verification script (Step 8)
4. Push updates

---

## Step 10: Merge + Backlog

After review approval:

```bash
# Merge PR
gh pr merge --squash

# Update backlog
# Mark the relevant item in docs/development/BACKLOG.md as complete
```

---

## Quick Reference

```bash
# Full workflow commands (copy-paste ready)

# 1. Task definition → write docs/tasks/{TASK_ID}.md

# 2. Branch
git checkout main && git pull
git checkout -b {TASK_ID}-description

# 3. TDD Red
# Write tests → verify they fail
uv run pytest tests/test_new.py -v

# 4. TDD Green
# Implement → verify tests pass
uv run pytest tests/test_new.py -v
uv run pytest --tb=short -q  # full suite

# 5. Quality
uv run ruff format src/ tests/
uv run ruff check src/ tests/
uv run mypy src/

# 6. Docs
# Update LLM_REFERENCE.md, ARCHITECTURE.md as needed

# 7. Issue + PR
git push -u origin {TASK_ID}-description
gh issue create --title "[{TASK_ID}] Title"
gh pr create --title "[{TASK_ID}] Title"

# 8. Verify
bash docs/tasks/verify-{TASK_ID}.sh

# 9. Review → fix → push

# 10. Merge
gh pr merge --squash
```

---

## Key Principles

1. **Task definition first** - Define "done" before writing code
2. **Tests before implementation** - Red → Green → Refactor
3. **Small atomic commits** - Each commit is a self-contained unit
4. **Quality gates are mandatory** - Never skip ruff/mypy
5. **Documentation travels with code** - Update docs in the same PR
6. **Verification is automated** - Every task has a runnable script
7. **Reviews catch what automation misses** - Human or agent review before merge

---

## See Also

- [TASK_DEFINITION_STANDARD.md](./TASK_DEFINITION_STANDARD.md) - How to write task definitions
- [TASK_NAMING.md](./TASK_NAMING.md) - Naming conventions
- [BACKLOG.md](./BACKLOG.md) - Feature backlog

---

*Last Updated: 2026-04-06*
