# Skill Directory Structure Reference

## File Layout

```
<skills-root>/<skill-name>/
├── SKILL.md              # Required — name must be SKILL.md exactly
├── scripts/              # Executable code Copilot can run
│   └── *.py|*.sh|*.js
├── references/           # Supplementary docs loaded on demand
│   └── *.md
└── assets/               # Templates, boilerplate, examples
    └── *
```

## Install Locations

| Path | Scope | Shared with |
|------|-------|-------------|
| `~/.copilot/skills/<name>/` | Personal | All your projects |
| `~/.claude/skills/<name>/` | Personal | Claude Code |
| `~/.agents/skills/<name>/` | Personal | Any agent |
| `.github/skills/<name>/` | Project | Repo collaborators |
| `.claude/skills/<name>/` | Project | Claude Code in repo |
| `.agents/skills/<name>/` | Project | Any agent in repo |
| `.github-private` → `/agents/skills/<name>/` | Org/Enterprise | Entire org |

## Naming Rules

- Folder name **must match** the `name` field in SKILL.md frontmatter
- Lowercase only, hyphens for spaces: `my-cool-skill` ✅, `MyCoolSkill` ❌
- 1–64 characters, alphanumeric + hyphens only
- No underscores, dots, or special characters

## Progressive Loading

Copilot loads skills in three stages to save context tokens:

1. **Discovery** (~100 tokens): Reads `name` + `description` from frontmatter
2. **Instructions** (<5000 tokens): Loads SKILL.md body when the skill is relevant
3. **Resources**: Additional files in `references/` and `scripts/` load only when referenced

**Implication**: Keep SKILL.md under 500 lines. Move deep documentation to `references/`.
Keep file references one level deep from SKILL.md.

## Slash Command Behavior

| `user-invocable` | `disable-model-invocation` | Slash command? | Auto-loaded? |
|---|---|---|---|
| *(default)* | *(default)* | ✅ Yes | ✅ Yes |
| `false` | *(default)* | ❌ No | ✅ Yes |
| *(default)* | `true` | ✅ Yes | ❌ No |
| `false` | `true` | ❌ No | ❌ No |
