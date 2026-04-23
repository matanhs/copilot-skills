# Copilot Skills

Personal [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) skills for session management and skill authoring.

## Skills

### 🗂️ session-manager

Scan, name, and clean up Copilot CLI sessions. Finds sessions with unfinished work, generates descriptive names, and allows cleanup of stale sessions.

**Install:**
```bash
gh skill install matanhs/copilot-skills session-manager
```

**Or manually:**
```bash
cp -r session-manager ~/.copilot/skills/
```

### 🛠️ skill-builder

End-to-end workflow for creating, validating, testing, and publishing Copilot CLI skills. Guides you through the full lifecycle from idea to published skill.

**Install:**
```bash
gh skill install matanhs/copilot-skills skill-builder
```

**Or manually:**
```bash
cp -r skill-builder ~/.copilot/skills/
```

## Usage

After installing, run `/skills reload` in your Copilot CLI session, then:

- `/session-manager` — scan and manage sessions
- `/skill-builder` — create a new skill

Or just describe what you need in natural language — Copilot auto-discovers skills by keyword.

## License

MIT
