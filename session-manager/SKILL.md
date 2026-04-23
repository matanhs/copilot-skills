---
name: session-manager
description: 'Scan, name, and clean up Copilot CLI sessions. Use when asked about previous sessions, unfinished work, session history, session cleanup, or recovering past work.'
argument-hint: 'scan | cleanup | name'
---

# Session Manager

Discover, inspect, name, and clean up Copilot CLI sessions.

## When to Use

- User asks about previous/old sessions or unfinished work
- User wants to find sessions with pending tasks or plans
- User wants to name or label sessions for recall
- User wants to clean up stale or irrelevant sessions
- User asks "what was I working on?" or "resume my work"

## Procedure

### Step 1: Scan Sessions

Run the scanner script to discover all sessions and their state:

```bash
python3 ~/.copilot/skills/session-manager/scripts/scan-sessions.py --json
```

For only sessions with unfinished work:

```bash
python3 ~/.copilot/skills/session-manager/scripts/scan-sessions.py --json --pending-only
```

### Step 2: Generate Session Names

For each session, generate a short memorable name based on:
1. **plan.md title** — the most authoritative signal (e.g., "Phase 4 Critical Review")
2. **Pending todos** — what's left unfinished (e.g., "Backend Integration — 2 tasks left")
3. **First/last user prompts** — conversation topic
4. **Workspace CWD** — which project/directory was active

Name format: **`<topic> — <status>`** where:
- `<topic>` is 2–5 words describing the work
- `<status>` is one of: `✅ Complete`, `⏳ Pending (N tasks)`, `🔒 Active`, `💤 Idle`

### Step 3: Present Report

Display sessions as a clear table with columns:
| Name | Session ID (short) | Last Active | Size | Status | Pending Work |

Group into:
1. **🔒 Active** — currently locked/in-use sessions
2. **⏳ Unfinished** — sessions with pending todos or incomplete plans
3. **💤 Idle** — sessions with no pending work

### Step 4: Cleanup (if requested)

When the user wants to clean up sessions:

1. Present the idle/completed sessions as candidates for deletion
2. **Always ask for explicit confirmation before deleting** — list the session IDs and names
3. **Never delete locked or active sessions**
4. Run cleanup:

```bash
python3 ~/.copilot/skills/session-manager/scripts/scan-sessions.py --cleanup SESSION_ID1 SESSION_ID2
```

5. Report results

### Step 5: Resume (if requested)

When the user wants to resume a session, tell them to use:
```
/resume <session-id>
```

Or for the most recent session:
```
copilot --continue
```

## Output Schema

The scanner produces JSON with this structure per session:

```json
{
  "session_id": "uuid",
  "last_modified": "ISO8601",
  "size_mb": 1.5,
  "is_locked": false,
  "has_pending_work": true,
  "workspace": { "cwd": "/path/to/project" },
  "plan": {
    "exists": true,
    "title": "Phase 4 Critical Review",
    "pending_summary": "...",
    "raw_head": "first 60 lines..."
  },
  "pending_todos": [
    { "id": "task-id", "title": "...", "status": "in_progress" }
  ],
  "conversation": {
    "turn_count": 15,
    "first_prompt": "...",
    "last_prompt": "...",
    "topics": ["..."]
  }
}
```

## Safety Rules

- **Never delete the current session**
- **Never delete locked sessions** (they may be active in another terminal)
- **Always confirm before deletion** — show what will be removed
- Treat session data as sensitive — don't leak content to external services
