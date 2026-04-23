---
name: skill-builder
description: 'Create, validate, test, and publish Copilot CLI skills. Use when asked to make a new skill, turn a workflow into a skill, package a skill for sharing, or publish a skill to GitHub.'
argument-hint: 'What should the skill do?'
---

# Skill Builder

End-to-end workflow for creating, validating, and publishing Copilot CLI skills.

## When to Use

- User asks to create a new skill
- User wants to turn a conversation workflow into a reusable skill
- User wants to validate, test, or fix an existing skill
- User wants to publish or share a skill

## Phase 1: Discover Intent

Before writing anything, determine:

1. **What outcome** should the skill produce? (e.g., "debug CI failures", "scan sessions")
2. **Scope**: Personal (`~/.copilot/skills/`) or project (`.github/skills/`)?
3. **Complexity**: Simple checklist or multi-step workflow with scripts?
4. **Trigger**: When should Copilot auto-load it? What keywords/prompts activate it?

If the user has been following a multi-step workflow in this conversation, extract and
generalize it into a reusable skill. Look for:
- Step-by-step processes
- Decision points and branching logic
- Quality criteria or completion checks
- Scripts or commands that were run

## Phase 2: Scaffold

Create the skill directory and files. Follow the naming and structure conventions
in [structure-reference.md](./references/structure-reference.md).

### Directory Layout

```
<skills-root>/<skill-name>/
├── SKILL.md              # Required — instructions + frontmatter
├── scripts/              # Optional — executable scripts
│   └── *.py|*.sh|*.js
├── references/           # Optional — supplementary docs loaded on demand
│   └── *.md
└── assets/               # Optional — templates, boilerplate
    └── *
```

### Determine install location

| Scope | Path |
|-------|------|
| Personal (all projects) | `~/.copilot/skills/<name>/` |
| Project (one repo) | `.github/skills/<name>/` |
| Organization-wide | `.github-private` repo → `/agents/skills/<name>/` |

### Create SKILL.md

Use this template:

```markdown
---
name: <skill-name>
description: '<What it does>. <When to use it — include trigger keywords>.'
argument-hint: '<hint for slash command input>'
---

# <Skill Title>

## When to Use
- <trigger condition 1>
- <trigger condition 2>

## Procedure
1. <Step 1>
2. <Step 2>
3. <Step 3>

## Safety Rules
- <constraint 1>
- <constraint 2>
```

### Frontmatter Rules

| Field | Required | Notes |
|-------|----------|-------|
| `name` | ✅ | 1-64 chars, lowercase, hyphens only, must match folder name |
| `description` | ✅ | Max 1024 chars. Keyword-rich for discovery. Include "Use when…" |
| `argument-hint` | ❌ | Shown when user types `/skill-name` |
| `license` | ❌ | License text if publishing |
| `allowed-tools` | ❌ | Pre-approve tools (e.g., `shell`). **Omit unless trusted** |
| `user-invocable` | ❌ | Default `true`. Set `false` to hide from `/` slash menu |
| `disable-model-invocation` | ❌ | Default `false`. Set `true` to disable auto-loading |

## Phase 3: Write Quality Instructions

Follow the principles in [writing-guide.md](./references/writing-guide.md).

Key rules:
1. **Keyword-rich description** — include trigger words so Copilot discovers it
2. **Progressive loading** — keep SKILL.md under 500 lines; put deep docs in `references/`
3. **Relative paths** — always use `./` for referencing skill resources
4. **Self-contained** — include all procedural knowledge needed to complete the task
5. **Concrete steps** — not "analyze the code" but "run `pytest -x` and check exit code"
6. **Script references** — if the skill runs a script, show the exact command with args

### Anti-patterns to Avoid
- ❌ Vague description: "A helpful skill" — won't be discovered
- ❌ Monolithic SKILL.md with everything in one file
- ❌ Folder name doesn't match `name` field
- ❌ Missing procedures — descriptions without step-by-step guidance
- ❌ Hardcoded absolute paths — use `~/.copilot/skills/<name>/` or relative `./`

## Phase 4: Validate

### Manual check
1. Verify folder name matches `name` in frontmatter
2. Verify description is ≤ 1024 chars and includes trigger keywords
3. Verify all `./` file references resolve to real files
4. Verify scripts are executable (`chmod +x`)

### With GitHub CLI (if available)
```bash
gh skill publish --dry-run
```
This validates against the Agent Skills specification without publishing.

### Auto-fix metadata issues
```bash
gh skill publish --fix
```

### Reload in current session
```
/skills reload
```
Then verify with:
```
/skills info <skill-name>
```

## Phase 5: Test

1. Start a fresh Copilot CLI session or run `/skills reload`
2. Test **slash invocation**: type `/<skill-name>` and check it appears
3. Test **auto-discovery**: use a prompt with the trigger keywords from the description
4. Test **the procedure**: follow the skill's steps end-to-end and verify the output
5. If the skill has scripts, run them manually first to confirm they work

## Phase 6: Publish & Share

### Option A: Share directly (quickest)
```bash
tar czf <skill-name>.tar.gz -C ~/.copilot/skills <skill-name>
# Recipient:
tar xzf <skill-name>.tar.gz -C ~/.copilot/skills/
```

### Option B: GitHub repo (recommended for teams)

#### First publish (new repo)
```bash
# Structure the repo with skills at the root:
# repo-root/<skill-name>/SKILL.md
git init && git add . && git commit -m "feat: add <skill-name> skill"
git remote add origin git@github.com:<owner>/<repo>.git
git push -u origin main
```

#### Update existing repo
```bash
cd /tmp && rm -rf <repo> && git clone git@github.com:<owner>/<repo>.git
cp -r ~/.copilot/skills/<skill-name>/ /tmp/<repo>/<skill-name>/
cd /tmp/<repo>
git add <skill-name>/    # stage only the changed skill
git --no-pager diff --cached --stat   # verify staged files
git commit -m "feat: <concise description of change>"
git push origin main
rm -rf /tmp/<repo>       # clean up
```

> **Rules**: Stage specific files only — never `git add -A` or `git add .`.
> Verify the diff before committing. Clean up the temp clone after push.

Colleagues install with:
```bash
gh skill install <owner>/<repo> <skill-name>
```
Pin to a version:
```bash
gh skill install <owner>/<repo> <skill-name> --pin v1.0.0
```

### Option C: Publish to Awesome Copilot directory
```bash
gh skill publish    # validates + publishes for public discovery
```
Then anyone can find it via:
```bash
gh skill search <topic>
```

## Phase 7: Iterate

After saving the first version:
1. Identify the weakest or most ambiguous part of the skill
2. Ask the user about those specific areas
3. Refine and re-validate
4. If the skill is published to a GitHub repo, push the update using the **Option B: Update existing repo** flow from Phase 6
5. Suggest related skills or customizations to create next
