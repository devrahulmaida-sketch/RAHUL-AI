"""memory_manager.py — Persistent JSON memory for RAHUL"""
import json, os, time
from pathlib import Path

MEMORY_FILE = Path(__file__).resolve().parent / "memory.json"


def load_memory() -> dict:
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_memory(memory: dict):
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")


def update_memory(updates: dict):
    memory = load_memory()
    for category, data in updates.items():
        if category not in memory:
            memory[category] = {}
        if isinstance(data, dict):
            memory[category].update(data)
        else:
            memory[category] = data
    memory["_last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_memory(memory)


def format_memory_for_prompt(memory: dict) -> str:
    if not memory:
        return ""
    lines = ["[MEMORY — What you know about the user]"]
    skip  = {"_last_updated"}
    for category, data in memory.items():
        if category in skip:
            continue
        if isinstance(data, dict):
            for key, val in data.items():
                v = val.get("value", val) if isinstance(val, dict) else val
                lines.append(f"  • {category}/{key}: {v}")
        else:
            lines.append(f"  • {category}: {data}")
    if len(lines) == 1:
        return ""
    return "\n".join(lines) + "\n"
