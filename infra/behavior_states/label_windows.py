"""Label agent x 5-minute windows with behavior states via Jev on OpenRouter (zero-shot).

Design: infra/behavior_states/DESIGN.md. Key: OPENROUTER_API_KEY from the environment, else from the
gitignored project .env (never print it, never commit it).

  uv run --with httpx python infra/behavior_states/label_windows.py --draft 200      # stratified non-holdout sample
  uv run --with httpx python infra/behavior_states/label_windows.py --all --max-usd 30

Only windows with activity are sent; windows with none are idle_wait by definition downstream.
Results are appended to a resumable JSONL, then compiled to data/processed/shared/behavior_states[_draft].parquet.
Window texts (gated) are kept only for the audit sample, under data/processed (gitignored).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from common import OUT, write_provenance  # noqa: E402

API = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.13"
WIN_MIN = 5

TAXONOMY = "v2"  # v1 (draft round 1) kept below as BEHAVIORS_V1 / MSG_ACTS_V1
BEHAVIORS = {
    "plan_coordinate": "Planning or coordinating work with others: proposing plans, dividing tasks, scheduling, assigning.",
    "execute_task": "Producing or changing an artifact, or carrying out the task's main activity: writing code or content, editing files, deploying, playing a game, making trades. If the window changed an artifact at all, choose this even if the agent also reported on it.",
    "research_browse": "Gathering information for a purpose: searching, reading web pages or docs, exploring tools or data.",
    "communicate_external": "Sending something to people or agents outside the village: emails, posts, forms, DMs, public boards. Producing the content alone is execute_task.",
    "debug_recover": "Fixing problems: errors, failed commands, broken pages, retries, workarounds, including loops of failing actions.",
    "verify_report": "Checking results without changing any artifact (testing, QA, verifying a deploy), or reporting status or results when nothing was changed in this window.",
    "self_maintenance": "Maintaining its own state: memory notes, reflection, reviewing its own history or plans.",
    "social": "Social chat with other agents not about the task: thanks, praise, greetings, encouragement.",
    "meta": "Talking about the village, the agents themselves, their nature, or the experiment.",
    "idle_monitor": "Waiting, pausing, polling or watching for a change without producing anything.",
}
MSG_ACTS = {
    "propose": "Proposes an idea, plan or option.", "agree": "Agrees with or endorses someone else.",
    "disagree": "Disagrees, objects or corrects someone.", "assign": "Assigns or requests a task from someone.",
    "report": "Reports status, results or information.", "ask": "Asks a question.",
    "thank_praise": "Mainly thanks or praises someone, with no other substantive act.", "other": "Anything else.",
}

BEHAVIORS_V1 = {
    "plan_coordinate": "Planning or coordinating work with others: proposing plans, dividing tasks, scheduling, assigning.",
    "build_execute": "Producing an artifact: writing code, documents, content or designs; deploying; editing files.",
    "research_browse": "Gathering information: searching, reading web pages or docs, exploring tools or data.",
    "communicate_external": "Reaching people or agents outside the village: emails, posts, forms, outreach, social media.",
    "debug_recover": "Fixing problems: errors, failed commands, broken pages, retries, workarounds, being stuck.",
    "verify_report": "Checking or reporting results: testing, verifying, summarizing progress or outcomes to others.",
    "self_maintenance": "Maintaining its own state: memory notes, reflection, reviewing its own history or plans.",
    "social": "Social chat with other agents not about the task: thanks, praise, greetings, encouragement.",
    "meta": "Talking about the village, the agents themselves, their nature, or the experiment.",
    "idle_wait": "Waiting, pausing, or doing essentially nothing.",
}
MSG_ACTS_V1 = {
    "propose": "Proposes an idea, plan or option.", "agree": "Agrees with or endorses someone else.",
    "disagree": "Disagrees, objects or corrects someone.", "assign": "Assigns or requests a task from someone.",
    "report": "Reports status, results or information.", "ask": "Asks a question.",
    "thank_praise": "Thanks or praises someone.", "other": "Anything else.",
}


def questions(has_chat: bool) -> dict:
    q = {
        "behavior": {"type": "choice", "instructions": "Which single behavior best describes what this agent mainly did in this 5-minute window? Weigh its computer actions and shell commands as much as its chat.",
                     "criteria": BEHAVIORS},
        "blocked": {"type": "noul", "instructions": "Did errors or failures stop this agent's progress for much of this window? Isolated errors it worked past do not count.",
                    "criteria": {"true": "Errors or failures stalled its progress for much of the window.", "false": "It made progress, worked past errors, or was simply idle."}},
        "others_work": {"type": "noul", "instructions": "Was the agent mainly working on an artifact another agent made, or on a task another participant explicitly asked it to do?",
                        "criteria": {"true": "Yes, mainly on another participant's artifact or explicit request.", "false": "No, mainly on its own work, or nothing."}},
        "progress": {"type": "score", "instructions": "How much concrete progress did the agent make in this window?",
                     "criteria": ["none", "little", "some", "substantial", "a lot"]},
    }
    if has_chat:
        q["message_act"] = {"type": "choice", "instructions": "What is the main act of the agent's own chat messages in this window? Choose the substantive act and ignore courtesy openers such as thanks.",
                            "criteria": MSG_ACTS}
        q["addresses_participant"] = {"type": "noul", "instructions": "Do the agent's messages reply to or address a specific named participant (another agent or a human)?",
                                      "criteria": {"true": "Yes, they address or reply to a specific named participant.", "false": "No, they are broadcast to everyone."}}
    return q


def build_windows(sample_n: int | None, seed: int = 20261003) -> pl.DataFrame:
    """One row per agent x 5-min window with any activity, plus the assembled state text."""
    bins = pl.read_parquet(OUT / "activity_bins.parquet").with_columns((pl.col("minute") // WIN_MIN).alias("w"))
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "win_start", "holdout", "regime", "goal_no"])
    win = (bins.group_by("pt_date", "agent", "w").agg(pl.col("talk").sum(), pl.col("turns").sum(), pl.col("idle").sum(),
                                                       pl.col("paused").sum(), pl.col("consolidate").sum(), pl.col("other_event").sum())
           .join(cal, on="pt_date"))
    win = win.with_columns((pl.col("win_start") + pl.duration(minutes=pl.col("w") * WIN_MIN)).alias("t0"),
                           (pl.col("win_start") + pl.duration(minutes=(pl.col("w") + 1) * WIN_MIN)).alias("t1"),
                           ((pl.col("talk") + pl.col("turns") + pl.col("other_event") + pl.col("consolidate")) > 0).alias("active"))
    if sample_n:
        roster = pl.read_parquet(OUT / "roster.parquet", columns=["agent", "lab"])
        pool = win.filter(pl.col("active") & ~pl.col("holdout")).join(roster, on="agent")
        pool = pool.with_columns(pl.concat_str(pl.col("regime").cast(pl.String), pl.lit("|"), "lab").alias("stratum"))
        k = max(1, sample_n // pool["stratum"].n_unique())  # equal allocation per regime x lab stratum
        strat = pool.group_by("stratum", maintain_order=True).map_groups(lambda g: g.sample(min(k, g.height), seed=seed))
        win = strat.sample(fraction=1.0, seed=seed, shuffle=True).drop("stratum", "lab")
    return win


def assemble_states(win: pl.DataFrame) -> list[dict]:
    """Assemble per-window state dicts from shared tables (actions, chat, intentions, exposure)."""
    acts = pl.read_parquet(OUT / "actions.parquet", columns=["t", "agent", "action", "bash_head", "error"])
    chat = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "agent", "speaker_kind"])
    ctext = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"])
    intents = pl.read_parquet(OUT / "intentions.parquet").join(pl.read_parquet(OUT / "intentions_text.parquet"), on="event_index")
    exp = pl.read_parquet(OUT / "exposure.parquet").join(chat.with_row_index("msg").select("msg", "t", "speaker_kind"), on="msg")
    out = []
    for r in win.iter_rows(named=True):
        a, t0, t1 = r["agent"], r["t0"], r["t1"]
        ac = acts.filter((pl.col("agent") == a) & (pl.col("t") >= t0) & (pl.col("t") < t1)).sort("t")
        prev = acts.filter((pl.col("agent") == a) & (pl.col("t") >= t0 - dt.timedelta(minutes=WIN_MIN)) & (pl.col("t") < t0))
        seq = [f"{x}|{y}" for x, y in zip(ac["action"].cast(pl.String).to_list(), ac["bash_head"].cast(pl.String).to_list())]
        run = best = 0
        for k, x in enumerate(seq):
            run = run + 1 if k and x == seq[k - 1] else 1
            best = max(best, run)
        own = (chat.filter((pl.col("agent") == a) & (pl.col("t") >= t0) & (pl.col("t") < t1)).join(ctext, on="message_id")
               .sort("t")["text"].to_list())
        it_row = intents.filter((pl.col("agent") == a) & (pl.col("t") < t1)).sort("t").tail(1)
        it = it_row["goal_text"].to_list()
        it_age = round((t1 - it_row["t"][0]).total_seconds() / 60) if it_row.height else None
        ex = exp.filter((pl.col("agent") == a) & (pl.col("t") >= t0) & (pl.col("t") < t1))
        state = {
            "computer_actions": ", ".join(f"{k}×{v}" for k, v in ac.group_by("action").len().sort("len", descending=True).iter_rows()) or "none",
            "shell_commands": ", ".join(f"{k}×{v}" for k, v in ac.drop_nulls("bash_head").group_by("bash_head").len()
                                        .sort("len", descending=True).head(12).iter_rows()) or "none",
            "errors": int(ac["error"].sum()) if ac.height else 0,
            "own_chat_messages": [m[:600] for m in own[:8]] or "none",
            "messages_seen": int(ex.height), "messages_seen_from_humans": int((ex["speaker_kind"] != "agent").sum()) if ex.height else 0,
            "current_intention": (it[0] or "")[:500] if it else "unknown",
            "intention_age_minutes": it_age,
            "previous_window_actions": ", ".join(f"{k}×{v}" for k, v in prev.group_by("action").len().sort("len", descending=True).iter_rows()) or "none",
            "longest_identical_action_run": best,
            "first_window_of_day": r["w"] == 0,
            "idle_or_pause_events": int(r["idle"] + r["paused"]), "memory_consolidations": int(r["consolidate"]),
        }
        out.append({"pt_date": r["pt_date"], "agent": a, "w": r["w"], "has_chat": bool(own), "state": state})
    return out


_lock = threading.Lock()


def call(client, item, key):
    body = {"model": MODEL, "state": item["state"], "questions": questions(item["has_chat"])}
    for attempt in range(5):
        try:
            r = client.post(API, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json=body, timeout=60)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 ** attempt); continue
            return {"error": r.status_code, "body": r.text[:300]}
        except Exception:  # network hiccup
            time.sleep(2 ** attempt)
    return {"error": "retries_exhausted"}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--draft", type=int); g.add_argument("--all", action="store_true")
    ap.add_argument("--max-usd", type=float, default=5.0); ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, help="label only the first N windows of the sample (smoke test)")
    ap.add_argument("--compile-only", action="store_true")
    ap.add_argument("--keys", help="JSONL with pt_date/agent/w: label exactly these windows (e.g. to compare taxonomies on one sample)")
    args = ap.parse_args()
    tag = "draft" if args.draft else "all"
    jsonl = OUT.parent / "behavior_states" / f"jev_{tag}_{TAXONOMY}.jsonl"
    if args.compile_only:
        return compile_jsonl(jsonl, bool(args.draft), None)
    key = load_key()
    import httpx
    jsonl.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if jsonl.exists():
        for line in jsonl.open():
            j = json.loads(line); done.add((j["pt_date"], j["agent"], j["w"]))
    if args.keys:  # grouped sampling in polars isn't reproducible across runs, so reuse an explicit key list
        keys = pl.DataFrame([{k: json.loads(l)[k] for k in ("pt_date", "agent", "w")} for l in open(args.keys)],
                            schema_overrides={"agent": pl.Int8, "w": pl.Int64})
        win = build_windows(None).join(keys, on=["pt_date", "agent", "w"], how="inner")
    else:
        win = build_windows(args.draft if args.draft else None)
    active = win.filter(pl.col("active"))
    if args.limit:
        active = active.head(args.limit)
    items = [it for it in assemble_states(active) if (it["pt_date"], it["agent"], it["w"]) not in done]
    print(f"{len(items)} windows to label ({len(done)} already done); cap ${args.max_usd}", flush=True)
    spent = 0.0
    with httpx.Client(http2=False) as client, ThreadPoolExecutor(args.workers) as ex, jsonl.open("a") as fout:
        futs = {ex.submit(call, client, it, key): it for it in items}
        for f in as_completed(futs):
            it, res = futs[f], f.result()
            cost = float(((res.get("usage") or {}).get("cost")) or 0)
            with _lock:
                spent += cost
                rec = {"pt_date": it["pt_date"], "agent": it["agent"], "w": it["w"], "answers": res.get("answers"),
                       "error": res.get("error"), "cost": cost}
                if args.draft:
                    rec["state"] = it["state"]  # audit sample only
                fout.write(json.dumps(rec) + "\n"); fout.flush()
            if spent > args.max_usd:
                print(f"cost cap reached (${spent:.2f}); stopping", flush=True)
                for ff in futs: ff.cancel()
                break
    print(f"spent ${spent:.4f}", flush=True)
    compile_jsonl(jsonl, bool(args.draft), spent)


def load_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    env = OUT.parents[2] / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key:
        sys.exit("OPENROUTER_API_KEY not found in the environment or the project .env")
    return key


def compile_jsonl(jsonl: Path, draft: bool, spent: float | None):
    rows = [json.loads(l) for l in jsonl.open()]
    flat = []
    for j in rows:
        a = j.get("answers") or {}
        b = a.get("behavior") or {}
        flat.append({"pt_date": j["pt_date"], "agent": j["agent"], "w": j["w"], "behavior": b.get("choice"),
                     "behavior_conf": b.get("confidence"), "behavior_probs": json.dumps(b.get("probabilities")),
                     "blocked": (a.get("blocked") or {}).get("noul"), "others_work": (a.get("others_work") or {}).get("noul"),
                     "progress": (a.get("progress") or {}).get("score"),
                     "message_act": (a.get("message_act") or {}).get("choice"),
                     "addresses_participant": (a.get("addresses_participant") or a.get("responds_to_agent") or {}).get("noul"), "error": str(j.get("error")), "cost": j["cost"]})
    pl.DataFrame(flat).write_parquet(OUT / f"behavior_states{'_draft' if draft else ''}_{TAXONOMY}.parquet", compression="zstd")
    write_provenance(f"behavior_states:{'draft' if draft else 'all'}", ["(shared tables)"],
                     {"model": MODEL, "taxonomy": TAXONOMY, "window_min": WIN_MIN, "n": len(flat), "spent_usd_total": round(sum(r["cost"] for r in flat), 4)})


if __name__ == "__main__":
    main()
