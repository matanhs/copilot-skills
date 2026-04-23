---
name: session-manager
description: 'Scan, name, and clean up Copilot CLI sessions. Use when asked about previous sessions, unfinished work, session history, session cleanup, or recovering past work.'
argument-hint: 'scan | cleanup | name | kill-and-resume'
---

# Session Manager

Discover, inspect, name, and clean up Copilot CLI sessions.

## When to Use

- User asks about previous/old sessions or unfinished work
- User wants to resume a session by description or index
- User wants to clean up stale or irrelevant sessions
- User says `/kill-and-resume` — destroy current session and switch to target

## Procedure

### Step 1: Scan Sessions

Run the scanner to get structured session data:

```bash
python3 ~/.copilot/skills/session-manager/scripts/scan-sessions.py --json
```

For only sessions with unfinished work:

```bash
python3 ~/.copilot/skills/session-manager/scripts/scan-sessions.py --json --pending-only
```

### Step 2: Name and Present

For each session, generate a name from `plan.title` or `workspace.summary`.
Present as a numbered list (1 = newest pending, -1 = oldest pending).

### Step 3: Resolve and Switch

The user may refer to a session by:
- **Index**: `1`, `2`, `-1` → map to the Nth pending session (newest-first)
- **Description**: "the backend one", "phase 5 work" → fuzzy match on plan title / workspace summary
- **Session ID prefix**: `dc840d25` → direct match

If the intent is ambiguous, use the `ask_user` tool with choices listing the matching sessions.

If the user also wants to **destroy the current session**, delete it before switching:
```bash
python3 ~/.copilot/skills/session-manager/scripts/scan-sessions.py --cleanup <current-session-id>
```

Then switch:
```
/resume <target-session-id>
```

### Step 4: Cleanup (if requested)

Delete sessions via:
```bash
python3 ~/.copilot/skills/session-manager/scripts/scan-sessions.py --cleanup SESSION_ID1 SESSION_ID2
```

**Always confirm before deleting. Never delete locked sessions.**

### Step 5: `/kill-and-resume {target}`

Shorthand to destroy the current session and resume another in one shot.

1. Resolve `{target}` (index, description, or ID prefix — same rules as Step 3).
2. If ambiguous, ask the user to pick.
3. Delete the **current** session:
   ```bash
   python3 ~/.copilot/skills/session-manager/scripts/scan-sessions.py --cleanup <current-session-id>
   ```
4. Immediately output:
   ```
   /resume <target-session-id>
   ```

No confirmation needed — the user's intent is explicit.

## Safety Rules

- Never delete the current session unless explicitly requested (e.g., `/kill-and-resume`)
- Never delete locked sessions
- Always confirm before deletion
- Treat session data as sensitive
