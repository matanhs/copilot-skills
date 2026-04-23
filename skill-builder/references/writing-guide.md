# Writing Effective Skill Instructions

## The Golden Rule

A skill must contain **all procedural knowledge** needed to complete the task.
Copilot has no memory of previous skill executions — every invocation starts fresh.

## Description (Frontmatter)

The description is the most important line. It controls **when** Copilot loads the skill.

### Formula
```
<What it does in one sentence>. <When to use — with trigger keywords>.
```

### Good Examples
- `'Debug failing GitHub Actions workflows. Use when asked to debug CI, fix builds, or investigate workflow failures.'`
- `'Scan and manage Copilot CLI sessions. Use when asked about previous sessions, unfinished work, or session cleanup.'`

### Bad Examples
- `'A helpful skill'` — zero trigger keywords
- `'Does stuff with GitHub'` — too vague for discovery

## Body Structure

### Recommended Sections

```markdown
# Skill Title

## When to Use
Bullet list of trigger conditions. Helps both Copilot AND humans understand scope.

## Procedure
Numbered steps. This is the core — make it concrete and actionable.

## Safety Rules
Constraints and things to never do.
```

### Optional Sections
- `## Output Schema` — if the skill produces structured data
- `## Examples` — sample inputs/outputs
- `## Troubleshooting` — common failure modes

## Writing Procedures

### Do ✅
- Use numbered steps with concrete commands: `Run \`pytest -x tests/\``
- Include decision branches: "If X, do A. Otherwise, do B."
- Reference scripts with relative paths: `[scan script](./scripts/scan.py)`
- Specify expected outputs: "This produces a JSON array of..."

### Don't ❌
- "Analyze the situation" — too vague
- "Use appropriate tools" — which ones?
- "Check if things are working" — what does "working" mean?
- Absolute paths that only work on your machine

## Scripts

When a skill includes scripts:

1. **Reference them explicitly** in the procedure: "Run `./scripts/scan.py --json`"
2. **Make them executable**: `chmod +x`
3. **Use portable interpreters**: `#!/usr/bin/env python3` not `#!/usr/local/bin/python3`
4. **Support `--help`**: Users and Copilot should be able to discover flags
5. **Output JSON when possible**: Structured output is easier for Copilot to process
6. **Handle errors gracefully**: Non-zero exit code + stderr message on failure

## Keeping Skills Focused

Each skill should do **one thing well**. If you find yourself writing 800+ lines,
split into multiple skills or move content to `references/` files.

| Skill size | Action |
|------------|--------|
| < 100 lines | Consider if this should be a custom instruction instead |
| 100–500 lines | Ideal skill size |
| 500+ lines | Move details to `references/` files |
| 1000+ lines | Split into multiple skills |
