---
name: session-manager
description: 'Scan, name, and clean up Copilot CLI sessions. Use when asked about previous sessions, unfinished work, session history, session cleanup, or recovering past work.'
argument-hint: 'scan | cleanup | name'
---

# Session Manager

Discover, inspect, name, and clean up Copilot CLI sessions.

## When to Use

- User asks about previous/old sessions or unfinished work
- User wants to resume a session by description or index
- User wants to clean up stale or irrelevant sessions
- User asks "what was I working on?" or "resume my work"

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

### Step 3: Resolve Resume Target

The user may refer to a session by:
- **Index**: `1`, `2`, `-1` → map to the Nth pending session (newest-first)
- **Description**: "the backend one", "phase 5 work" → fuzzy match on plan title / workspace summary
- **Session ID prefix**: `dc840d25` → direct match

Once resolved, tell the user:
```
/resume <full-session-id>
```

### Step 4: Cleanup (if requested)

Delete sessions via:
```bash
python3 ~/.copilot/skills/session-manager/scripts/scan-sessions.py --cleanup SESSION_ID1 SESSION_ID2
```

**Always confirm before deleting. Never delete locked sessions.**

## Safety Rules

- Never delete the current session or locked sessions
- Always confirm before deletion
- Treat session data as sensitive
