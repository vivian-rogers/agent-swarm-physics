"""Count computer-use action types per agent and per month (no text kept).

Output: data/processed/ai-village/turns_stats.json
        data/processed/ai-village/event_type_counts.json   (with --event-types)
Usage:  uv run --with orjson python infra/ai_village_overview/scan_turns.py   (~2.5M rows, a few minutes)
        uv run --with orjson python infra/ai_village_overview/scan_turns.py --event-types
"""
import gzip, json, collections
from pathlib import Path
import orjson

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/ai-village"
OUT = ROOT / "data/processed/ai-village"


def rows(name):
    with gzip.open(RAW / f"{name}.jsonl.gz", "rb") as f:
        for line in f:
            yield orjson.loads(line)


def main():
    sess_agent = {r["id"]: r["agent_id"] for r in rows("computer_use_sessions")}
    actions = collections.Counter()
    actions_by_agent = collections.defaultdict(collections.Counter)
    per_month = collections.Counter()
    os_hits = collections.Counter()
    probes = ["Ubuntu", "Debian", "Firefox", "Chromium", "Google Chrome", "xdotool", "gitlab", "github.com"]
    n = n_err = n_redacted = 0
    for r in rows("computer_use_turns"):
        n += 1
        a = r.get("agent_action") or {}
        name = a.get("action") or ("bash" if "command" in a else ("none" if not a else "other"))
        actions[name] += 1
        actions_by_agent[sess_agent.get(r["session_id"], "?")][name] += 1
        per_month[r["created_at"][:7]] += 1
        n_err += bool(r.get("error"))
        n_redacted += bool(r.get("screenshot_is_redacted"))
        out = r.get("output")
        if out and n % 20 == 0:  # 5% sample of tool outputs, for platform strings
            for p in probes:
                if p in out:
                    os_hits[p] += 1
    stats = {"n_turns": n, "n_error": n_err, "n_redacted": n_redacted, "actions": actions.most_common(),
             "actions_by_agent": {k: v.most_common() for k, v in actions_by_agent.items()},
             "per_month": dict(sorted(per_month.items())), "platform_string_hits_5pct_sample": os_hits}
    (OUT / "turns_stats.json").write_text(json.dumps(stats, indent=1))


def scan_event_types():
    counts = collections.Counter(r["data"].get("actionType") for r in rows("events"))
    (OUT / "event_type_counts.json").write_text(json.dumps(
        {"note": "Counts of events.data.actionType over all events.", "counts": dict(counts.most_common())}, indent=1))


if __name__ == "__main__":
    import sys
    scan_event_types() if "--event-types" in sys.argv else main()
