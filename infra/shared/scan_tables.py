"""Phase 0, step 1: one streaming pass per big raw table, run in parallel processes.

Outputs (data/processed/shared/):
  roster.parquet            46 agents: code, id, name, model, lab, join/leave (CHANGELOG), flags
  events_core.parquet       381,610 events, no text
  intentions.parquet        self-written session goals (+ intentions_text sidecar)
  chat_core.parquet         183,485 messages, no text (+ chat_text sidecar)
  actions.parquet           2.51M computer-use turns, no raw messages; token accounting
  memory_stats.parquet      246,151 memory snapshots: size and diff vs previous (no text)

Usage: uv run python infra/shared/scan_tables.py [--only events,chat,turns,memories]
"""
from __future__ import annotations

import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import polars as pl

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from common import (OUT, RAW, GoalLookup, mention_regexes, parse_ts, pt_date, regime, rows, short_hash,
                    URL_RE, write_provenance)

# ----------------------------------------------------------------------------- roster

def provider(model: str) -> str:
    m = model.lower()
    for key, prov in [("claude", "Anthropic"), ("gpt", "OpenAI"), ("o1", "OpenAI"), ("o3", "OpenAI"),
                      ("o4", "OpenAI"), ("gemini", "Google"), ("grok", "xAI"), ("deepseek", "DeepSeek"),
                      ("tinker", "Fine-tuned (Kimi)"), ("kimi", "Moonshot"), ("glm", "Zhipu"), ("muse", "Meta")]:
        if key in m:
            return prov
    return "Other"


def build_roster() -> pl.DataFrame:
    agents = sorted(rows("agents"), key=lambda a: (a["created_at"], a["name"]))
    # join/leave from the CHANGELOG roster table (operator registry)
    cl = {}
    for line in (RAW / "CHANGELOG.md").read_text().splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*`?([^|`]+?)`?\s*\|\s*(\d{4}-\d{2}-\d{2})[^|]*\|\s*([^|]+?)\s*\|", line)
        if m:
            name, _, joined, left = m.groups()
            cl[name] = (joined, None if left.strip() == "active" else left.strip())
    recs = []
    for code, a in enumerate(agents):
        j, l = cl.get(a["name"], (a["created_at"][:10], None))
        recs.append({"agent": code, "agent_id": a["id"], "name": a["name"], "model_string": a["model_string"],
                     "lab": provider(a["model_string"]), "joined": j, "left": l,
                     "claude_code": a["model_string"].startswith("claude-code::"),
                     "fine_tuned": a["model_string"].startswith("tinker://")})
    df = pl.DataFrame(recs).with_columns(pl.col("agent").cast(pl.Int8))
    df.write_parquet(OUT / "roster.parquet", compression="zstd")
    return df


def agent_codes() -> dict:
    df = pl.read_parquet(OUT / "roster.parquet")
    return dict(zip(df["agent_id"].to_list(), df["agent"].to_list()))


def room_codes() -> dict:
    rooms = sorted(rows("chat_rooms"), key=lambda r: (r["created_at"], r["name"]))
    pl.DataFrame([{"room": i, "room_id": r["id"], "name": r["name"], "created_at": r["created_at"],
                   "deleted_at": r["deleted_at"]} for i, r in enumerate(rooms)]).with_columns(
        pl.col("room").cast(pl.Int8)).write_parquet(OUT / "rooms.parquet", compression="zstd")
    return {r["id"]: i for i, r in enumerate(rooms)}

# ----------------------------------------------------------------------------- events

def scan_events():
    t0 = time.time()
    A, R, G = agent_codes(), room_codes(), GoalLookup()
    ev, intents, itext = [], [], []
    for r in rows("events"):
        d = r["data"]
        t = parse_ts(r["created_at"])
        typ = d.get("actionType")
        if typ == "AGENT_TALK":
            kind, actor = "agent", A.get(d.get("speakerId"))
        elif typ == "USER_TALK":
            kind = "automated" if (d.get("speakerName") or "") == "automated" else "human"
            actor = None
        elif typ == "USER_NAME_CHANGE":
            kind, actor = "system", None
        else:
            kind, actor = "agent", A.get(d.get("agentId"))
        human = short_hash(d.get("speakerId")) if typ == "USER_TALK" and kind == "human" else None
        ev.append((r["event_index"], t, pt_date(t), G(t), regime(t), kind, actor, human, typ,
                   R.get(d.get("roomId")), int(d.get("inputTokens") or 0), int(d.get("outputTokens") or 0),
                   d.get("messageId"), d.get("computerUseSessionId"), float(d.get("seconds") or 0) or None))
        if typ in ("START_USING_COMPUTER", "CONSOLIDATE"):
            goal = d.get("sessionGoal") if typ == "START_USING_COMPUTER" else d.get("nextSessionGoal")
            short = d.get("shortDisplayedSessionGoal") if typ == "START_USING_COMPUTER" else d.get("nextShortDisplayedSessionGoal")
            intents.append((r["event_index"], t, actor, typ))
            itext.append((r["event_index"], goal, short))
    cols = ["event_index", "t", "pt_date", "goal_no", "regime", "actor_kind", "agent", "human", "action_type",
            "room", "tokens_in", "tokens_out", "message_id", "session_id", "pause_s"]
    df = pl.DataFrame(ev, schema=cols, orient="row").with_columns(
        pl.col("agent").cast(pl.Int8), pl.col("room").cast(pl.Int8), pl.col("goal_no").cast(pl.Int8),
        pl.col("tokens_in").cast(pl.Int32), pl.col("tokens_out").cast(pl.Int32),
        pl.col("action_type").cast(pl.Categorical), pl.col("actor_kind").cast(pl.Categorical),
        pl.col("regime").cast(pl.Categorical), pl.col("pause_s").cast(pl.Float32)).sort("event_index")
    df.write_parquet(OUT / "events_core.parquet", compression="zstd")
    pl.DataFrame(intents, schema=["event_index", "t", "agent", "source"], orient="row").with_columns(
        pl.col("agent").cast(pl.Int8)).write_parquet(OUT / "intentions.parquet", compression="zstd")
    pl.DataFrame(itext, schema=["event_index", "goal_text", "short_text"], orient="row").write_parquet(
        OUT / "intentions_text.parquet", compression="zstd")
    write_provenance("scan_tables:events", ["events", "agents", "chat_rooms", "village_goals"])
    return f"events {len(df):,} rows, intentions {len(intents):,} in {time.time()-t0:.0f}s"

# ----------------------------------------------------------------------------- chat

def scan_chat():
    t0 = time.time()
    A, R, G = agent_codes(), room_codes(), GoalLookup()
    pats = mention_regexes(list(rows("agents")))
    pats = {A[k]: v for k, v in pats.items() if k in A}
    core, text = [], []
    for r in rows("chat_messages"):
        t = parse_ts(r["created_at"])
        content = r["content"] or ""
        if r["speaker_type"] == "agent":
            kind, agent, human = "agent", A.get(r["agent_speaker_id"]), None
        else:
            kind, agent, human = "human", None, short_hash(r["user_speaker_id"])
        mentions = [c for c, p in pats.items() if c != agent and p.search(content)]
        urls = URL_RE.findall(content)
        core.append((r["id"], t, pt_date(t), G(t), regime(t), R.get(r["room_id"]), kind, agent, human,
                     len(content), mentions, len(urls)))
        text.append((r["id"], content, urls))
    cols = ["message_id", "t", "pt_date", "goal_no", "regime", "room", "speaker_kind", "agent", "human",
            "length", "mentions", "n_urls"]
    df = pl.DataFrame(core, schema=cols, orient="row").with_columns(
        pl.col("room").cast(pl.Int8), pl.col("agent").cast(pl.Int8), pl.col("goal_no").cast(pl.Int8),
        pl.col("length").cast(pl.Int32), pl.col("n_urls").cast(pl.Int16),
        pl.col("speaker_kind").cast(pl.Categorical), pl.col("regime").cast(pl.Categorical),
        pl.col("mentions").cast(pl.List(pl.Int8))).sort("t")
    df.write_parquet(OUT / "chat_core.parquet", compression="zstd")
    pl.DataFrame(text, schema=["message_id", "text", "urls"], orient="row").write_parquet(
        OUT / "chat_text.parquet", compression="zstd")
    write_provenance("scan_tables:chat", ["chat_messages", "agents", "chat_rooms", "village_goals"],
                     {"mentions": "regex on agent names/aliases (estimate)"})
    return f"chat {len(df):,} rows in {time.time()-t0:.0f}s"

# ----------------------------------------------------------------------------- computer-use turns

def _reasoning_chars(am) -> int:
    """Characters of model reasoning in a provider-shaped response (Anthropic thinking blocks,
    OpenAI reasoning summaries, Gemini thought parts). Best effort."""
    n = 0
    stack = [am]
    while stack:
        o = stack.pop()
        if isinstance(o, dict):
            typ = o.get("type")
            if typ == "thinking":
                n += len(o.get("thinking") or "")
            elif typ == "reasoning":
                for s in o.get("summary") or []:
                    n += len((s or {}).get("text") or "") if isinstance(s, dict) else 0
            elif o.get("thought") is True:
                n += len(o.get("text") or "")
            else:
                stack.extend(v for v in o.values() if isinstance(v, (dict, list)))
        elif isinstance(o, list):
            stack.extend(x for x in o if isinstance(x, (dict, list)))
    return n


def _usage(am):
    """(input, cache_read, cache_write, output) tokens from a provider response, best effort."""
    def find(o, keys):
        if isinstance(o, dict):
            for k in keys:
                if k in o and isinstance(o[k], dict):
                    return o[k]
            for v in o.values():
                r = find(v, keys)
                if r is not None:
                    return r
        elif isinstance(o, list):
            for x in o:
                r = find(x, keys)
                if r is not None:
                    return r
        return None
    u = find(am, ("usage", "usageMetadata"))
    if not u:
        return (None, None, None, None)
    if "promptTokenCount" in u or "candidatesTokenCount" in u:  # Gemini
        return (u.get("promptTokenCount"), u.get("cachedContentTokenCount"), None,
                (u.get("candidatesTokenCount") or 0) + (u.get("thoughtsTokenCount") or 0))
    if "input_tokens" in u:  # Anthropic / OpenAI Responses
        details = u.get("input_tokens_details") or {}
        return (u.get("input_tokens"), u.get("cache_read_input_tokens", details.get("cached_tokens")),
                u.get("cache_creation_input_tokens"), u.get("output_tokens"))
    if "prompt_tokens" in u:  # OpenAI chat completions
        details = u.get("prompt_tokens_details") or {}
        return (u.get("prompt_tokens"), details.get("cached_tokens"), None, u.get("completion_tokens"))
    return (None, None, None, None)


BASH_HEAD = re.compile(r"^\s*(?:sudo\s+|cd\s+\S+\s*&&\s*|timeout\s+\S+\s+)*([A-Za-z0-9_.\-/]+)")


def scan_turns():
    t0 = time.time()
    A = agent_codes()
    sess = {r["id"]: A.get(r["agent_id"]) for r in rows("computer_use_sessions")}
    recs = []
    for r in rows("computer_use_turns"):
        t = parse_ts(r["created_at"])
        a = r.get("agent_action") or {}
        if "command" in a and not a.get("action"):
            act, m = "bash", BASH_HEAD.match(a.get("command") or "")
            head = (m.group(1).split("/")[-1][:24] if m else None)
        else:
            act, head = (a.get("action") or ("none" if not a else "other")), None
        am = r.get("agent_messages")
        tin, cread, cwrite, tout = _usage(am)
        recs.append((t, sess.get(r["session_id"]), act, head, bool(r.get("error")), bool(r.get("screenshot_is_redacted")),
                     tin, cread, cwrite, tout, _reasoning_chars(am)))
    cols = ["t", "agent", "action", "bash_head", "error", "redacted", "tok_in", "tok_cache_read", "tok_cache_write",
            "tok_out", "reasoning_chars"]
    df = pl.DataFrame(recs, schema=cols, orient="row").with_columns(
        pl.col("agent").cast(pl.Int8), pl.col("action").cast(pl.Categorical), pl.col("bash_head").cast(pl.Categorical),
        *[pl.col(c).cast(pl.Int32) for c in ("tok_in", "tok_cache_read", "tok_cache_write", "tok_out", "reasoning_chars")]
    ).sort("t")
    df.write_parquet(OUT / "actions.parquet", compression="zstd")
    write_provenance("scan_tables:turns", ["computer_use_turns", "computer_use_sessions", "agents"],
                     {"text": "none kept; bash_head = first token of command; tokens from provider usage objects"})
    return f"actions {len(df):,} rows in {time.time()-t0:.0f}s"

# ----------------------------------------------------------------------------- memories

def scan_memories():
    """Size and line-level diff of each memory snapshot vs the same agent's previous one.
    Lines are hashed (64-bit) so no text is kept; ~250k snapshots."""
    t0 = time.time()
    A = agent_codes()
    snaps = []
    for r in rows("agent_memories"):
        c = r["content"] or ""
        lines = [ln.strip() for ln in c.splitlines() if ln.strip()]
        hs = frozenset(hash(ln) for ln in lines)
        heads = sum(1 for ln in lines if ln.startswith("#"))
        snaps.append((parse_ts(r["created_at"]), A.get(r["agent_id"]), len(c), len(lines), heads, hs))
    snaps.sort(key=lambda x: (x[1] if x[1] is not None else -1, x[0]))
    recs, prev = [], {}
    for t, a, n_chars, n_lines, heads, hs in snaps:
        p = prev.get(a)
        if p is None:
            kept = added = removed = None
            jac = None
        else:
            kept = len(hs & p); added = len(hs - p); removed = len(p - hs)
            union = len(hs | p); jac = kept / union if union else 1.0
        recs.append((t, a, n_chars, n_lines, heads, kept, added, removed, jac))
        prev[a] = hs
    cols = ["t", "agent", "n_chars", "n_lines", "n_headers", "lines_kept", "lines_added", "lines_removed", "jaccard_prev"]
    df = pl.DataFrame(recs, schema=cols, orient="row").with_columns(
        pl.col("agent").cast(pl.Int8), *[pl.col(c).cast(pl.Int32) for c in cols[2:8]],
        pl.col("jaccard_prev").cast(pl.Float32)).sort("t")
    df.write_parquet(OUT / "memory_stats.parquet", compression="zstd")
    write_provenance("scan_tables:memories", ["agent_memories", "agents"],
                     {"diff": "set of stripped non-empty lines, hashed; no text kept"})
    return f"memory_stats {len(df):,} rows in {time.time()-t0:.0f}s"


JOBS = {"events": scan_events, "chat": scan_chat, "turns": scan_turns, "memories": scan_memories}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].split(",")
    t0 = time.time()
    print(build_roster().select("agent", "name", "lab").head(3))
    jobs = [j for j in JOBS if not only or j in only]
    with ProcessPoolExecutor(max_workers=len(jobs)) as ex:
        futs = {ex.submit(JOBS[j]): j for j in jobs}
        for f in futs:
            print(futs[f], "->", f.result(), flush=True)
    print(f"total {time.time()-t0:.0f}s")
