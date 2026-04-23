#!/usr/bin/env python3
"""
Session Scanner for GitHub Copilot CLI.

Scans ~/.copilot/session-state/ to discover sessions, extract metadata,
detect pending work, and generate a structured JSON report.

Usage:
    python3 scan-sessions.py [--json] [--cleanup SESSION_ID [SESSION_ID ...]]
"""

import argparse
import json
import os
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SESSION_STATE_DIR = Path(os.environ.get("COPILOT_HOME", Path.home() / ".copilot")) / "session-state"


def get_current_session_id():
    """Try to detect the currently active session from environment or cwd hints."""
    # The COPILOT_SESSION_ID env var is set inside a running session
    return os.environ.get("COPILOT_SESSION_ID", None)


def read_plan(session_dir: Path) -> dict:
    """Read plan.md and extract a summary and pending items."""
    plan_path = session_dir / "plan.md"
    if not plan_path.exists():
        return {"exists": False, "title": None, "summary": None, "raw_head": None}

    text = plan_path.read_text(errors="replace")
    lines = text.strip().splitlines()

    # Extract title from first heading
    title = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            break

    # First 60 lines as context for AI naming
    raw_head = "\n".join(lines[:60])

    # Extract pending checklist items
    pending = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- [ ]") or stripped.startswith("* [ ]"):
            pending.append(stripped[5:].strip())
        elif "pending" in stripped.lower() and "|" in stripped:
            pending.append(stripped)

    return {
        "exists": True,
        "title": title,
        "summary": "\n".join(pending[:10]) if pending else None,
        "raw_head": raw_head,
    }


def read_todos(session_dir: Path) -> list:
    """Read pending todos from session.db SQLite database."""
    db_path = session_dir / "session.db"
    if not db_path.exists():
        return []

    todos = []
    try:
        con = sqlite3.connect(str(db_path))
        con.row_factory = sqlite3.Row
        # Check if todos table exists
        tables = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='todos'"
        ).fetchall()
        if not tables:
            con.close()
            return []
        rows = con.execute(
            "SELECT id, title, description, status FROM todos WHERE status != 'done' ORDER BY status, id"
        ).fetchall()
        for r in rows:
            todos.append({
                "id": r["id"],
                "title": r["title"],
                "description": r["description"],
                "status": r["status"],
            })
        con.close()
    except Exception:
        pass
    return todos


def read_events_summary(session_dir: Path) -> dict:
    """Read events.jsonl for conversation topic hints."""
    events_path = session_dir / "events.jsonl"
    if not events_path.exists():
        return {"turn_count": 0, "first_prompt": None, "last_prompt": None, "topics": []}

    prompts = []
    turn_count = 0
    try:
        with open(events_path, "r", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Count conversation turns
                if evt.get("type") in ("user_message", "human", "user"):
                    turn_count += 1
                    msg = evt.get("message", evt.get("content", evt.get("text", "")))
                    if isinstance(msg, str) and msg.strip():
                        prompts.append(msg.strip()[:200])
                elif isinstance(evt, dict) and "role" in evt and evt["role"] == "user":
                    turn_count += 1
                    content = evt.get("content", "")
                    if isinstance(content, str) and content.strip():
                        prompts.append(content.strip()[:200])
    except Exception:
        pass

    return {
        "turn_count": turn_count,
        "first_prompt": prompts[0] if prompts else None,
        "last_prompt": prompts[-1] if prompts else None,
        "topics": prompts[:5],
    }


def read_workspace(session_dir: Path) -> dict:
    """Read workspace.yaml for working directory context."""
    ws_path = session_dir / "workspace.yaml"
    if not ws_path.exists():
        return {}
    try:
        text = ws_path.read_text(errors="replace")
        # Simple YAML key extraction (avoid dependency)
        result = {}
        for line in text.splitlines():
            if ":" in line and not line.strip().startswith("#"):
                key, _, val = line.partition(":")
                result[key.strip()] = val.strip().strip('"').strip("'")
        return result
    except Exception:
        return {}


def get_dir_size(path: Path) -> int:
    """Get total size of directory in bytes."""
    total = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                total += p.stat().st_size
    except Exception:
        pass
    return total


def scan_session(session_dir: Path) -> dict:
    """Scan a single session directory and return structured metadata."""
    session_id = session_dir.name
    stat = session_dir.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

    plan = read_plan(session_dir)
    todos = read_todos(session_dir)
    events = read_events_summary(session_dir)
    workspace = read_workspace(session_dir)
    size_bytes = get_dir_size(session_dir)

    # Check for lock files (indicates potentially active session)
    lock_files = list(session_dir.glob("*.lock"))
    is_locked = len(lock_files) > 0

    # Determine if session has pending work
    has_pending_work = bool(todos) or (plan["summary"] is not None)

    return {
        "session_id": session_id,
        "last_modified": mtime.isoformat(),
        "last_modified_human": mtime.strftime("%Y-%m-%d %H:%M"),
        "size_mb": round(size_bytes / (1024 * 1024), 2),
        "is_locked": is_locked,
        "has_pending_work": has_pending_work,
        "workspace": workspace,
        "plan": {
            "exists": plan["exists"],
            "title": plan["title"],
            "pending_summary": plan["summary"],
            "raw_head": plan["raw_head"],
        },
        "pending_todos": todos,
        "conversation": events,
    }


def scan_all_sessions() -> list:
    """Scan all sessions and return sorted by last modified (newest first)."""
    if not SESSION_STATE_DIR.exists():
        return []

    sessions = []
    for d in SESSION_STATE_DIR.iterdir():
        if d.is_dir() and not d.name.startswith("."):
            try:
                sessions.append(scan_session(d))
            except Exception as e:
                sessions.append({
                    "session_id": d.name,
                    "error": str(e),
                })

    sessions.sort(key=lambda s: s.get("last_modified", ""), reverse=True)
    return sessions


def delete_sessions(session_ids: list) -> dict:
    """Delete specified sessions. Returns results per session."""
    results = {}
    current = get_current_session_id()
    for sid in session_ids:
        session_dir = SESSION_STATE_DIR / sid
        if sid == current:
            results[sid] = {"deleted": False, "reason": "Cannot delete current active session"}
        elif not session_dir.exists():
            results[sid] = {"deleted": False, "reason": "Session not found"}
        else:
            try:
                # Check for lock files
                locks = list(session_dir.glob("*.lock"))
                if locks:
                    results[sid] = {"deleted": False, "reason": f"Session is locked ({len(locks)} lock files)"}
                else:
                    shutil.rmtree(session_dir)
                    results[sid] = {"deleted": True}
            except Exception as e:
                results[sid] = {"deleted": False, "reason": str(e)}
    return results


def main():
    parser = argparse.ArgumentParser(description="Copilot CLI Session Scanner")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--cleanup", nargs="+", metavar="SESSION_ID",
                        help="Delete specified session(s)")
    parser.add_argument("--pending-only", action="store_true",
                        help="Only show sessions with pending work")
    args = parser.parse_args()

    if args.cleanup:
        results = delete_sessions(args.cleanup)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for sid, res in results.items():
                status = "✅ Deleted" if res["deleted"] else f"❌ {res['reason']}"
                print(f"  {sid[:12]}… {status}")
        return

    sessions = scan_all_sessions()

    if args.pending_only:
        sessions = [s for s in sessions if s.get("has_pending_work")]

    if args.json:
        print(json.dumps(sessions, indent=2))
    else:
        # Human-readable table
        print(f"\n{'='*90}")
        print(f"  Copilot CLI Sessions  ({len(sessions)} total)")
        print(f"{'='*90}\n")
        for s in sessions:
            if "error" in s:
                print(f"  ❌ {s['session_id'][:12]}…  Error: {s['error']}")
                continue

            flags = []
            if s["is_locked"]:
                flags.append("🔒 LOCKED")
            if s["has_pending_work"]:
                flags.append("⏳ PENDING WORK")

            cwd = s.get("workspace", {}).get("cwd", "?")
            plan_title = s["plan"]["title"] or "(no plan)"
            turns = s["conversation"]["turn_count"]

            flag_str = f"  [{', '.join(flags)}]" if flags else ""
            print(f"  📁 {s['session_id'][:12]}…  |  {s['last_modified_human']}  |  {s['size_mb']} MB{flag_str}")
            print(f"     CWD: {cwd}")
            print(f"     Plan: {plan_title}")
            print(f"     Turns: {turns}")

            if s["pending_todos"]:
                print(f"     Pending todos:")
                for t in s["pending_todos"][:5]:
                    print(f"       [{t['status']}] {t['id']}: {t['title']}")

            first = s["conversation"].get("first_prompt")
            if first:
                print(f"     First prompt: {first[:100]}…" if len(first) > 100 else f"     First prompt: {first}")

            print()


if __name__ == "__main__":
    main()
