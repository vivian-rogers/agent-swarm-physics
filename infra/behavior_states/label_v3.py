"""Jev behavior states v3: label every active agent x 5-minute window zero-shot (design + validation: DESIGN.md).

  uv run --with httpx python infra/behavior_states/label_v3.py --keys data/processed/behavior_states/blind_draft.jsonl
  uv run --with httpx python infra/behavior_states/label_v3.py --all --max-usd 15
  uv run python infra/behavior_states/label_v3.py --all --compile-only
  (after the run the results JSONL is archived as jev_all_v3.jsonl.gz; resume, compile and the spend total read both)

State assembly: assemble_v3.py (vectorized). Taxonomy v3 = v2 with idle_monitor split into monitor_wait (waiting for a
specific expected event and checking for it) and idle (nothing purposeful), tightened execute/research/verify/debug
definitions, a broader `blocked` (stalled by failures, loops, or dependencies on others) and a narrower `others_work`.

Calls: OpenRouter Decisions API, model typesafe/jev-1.13, at most 16 concurrent requests (asyncio, one CPU thread), retries
with exponential backoff + jitter on 429/5xx/timeouts (Retry-After honoured). Resumable: results are appended to
data/processed/behavior_states/jev_<all|draft>_v3.jsonl; windows with answers are skipped on restart, errored ones retried.
Hard spend cap: --max-usd applies to the TOTAL usage.cost over every v3 JSONL (validation + full run), and the run stops
submitting once it is reached. The key (OPENROUTER_API_KEY, env or gitignored .env) is never printed or logged.
Gated text: window states go only to the Jev API; they are kept on disk only for the --keys audit sample (under data/).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "shared"))
import assemble_v3 as A  # noqa: E402
from common import OUT, REVISION, git_commit  # noqa: E402

API = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.13"
TAXONOMY = "v3"
BS = OUT.parent / "behavior_states"

BEHAVIORS = {
    "plan_coordinate": "Planning or coordinating with others: proposing or agreeing plans, dividing or assigning tasks, scheduling.",
    "execute_task": "Producing or changing an artifact, or doing the task's main activity: code, content, file edits, commits, deploys, forms, games, trades. If any artifact changed in this window, choose this even if it also checked or reported.",
    "research_browse": "Gathering new information: searching, reading pages, docs, code or data, exploring tools.",
    "communicate_external": "Sending something outside the village: emails, social posts, form submissions, DMs, external issue comments. Drafting without sending is execute_task.",
    "debug_recover": "Fixing problems as the main activity: diagnosing and repairing failures, broken pages or tools, retrying, working around errors, or looping on failing or no-op actions. Failures met while doing something else do not count.",
    "verify_report": "Checking or reporting results without changing anything: tests, QA, verifying a deploy or claim, posting status when nothing changed.",
    "monitor_wait": "Waiting for a specific expected event and checking for it: polling a page, inbox, PR, CI, market or leaderboard; awaiting a reply, go-ahead or set time. Nothing produced.",
    "self_maintenance": "Maintaining its own state: memory consolidation, notes to self, reflection, reviewing its own history or plans.",
    "social": "Off-task social chat: thanks, praise, greetings, welcomes, congratulations.",
    "meta": "Talking about the village, the agents' nature, or the experiment.",
    "idle": "Nothing purposeful and waiting for nothing specific: paused, or nothing but start-up or scaffold actions (a lone screenshot or mouse move). Purposeful clicks or typing are not idle; loops are not idle.",
}
PROGRESS = ["none", "little", "some", "substantial", "a lot"]


def questions(has_chat: bool) -> dict:
    q = {
        "behavior": {"type": "choice", "criteria": BEHAVIORS,
                     "instructions": "Which behavior best describes what the agent mainly did in this 5-minute window? Weigh actions, commands and artifact changes as much as chat; if it only chatted, label the chat. The intention is its plan, not evidence of what it did. Messages may recap earlier windows (see prev_window): label this window."},
        "blocked": {"type": "noul",
                    "instructions": "Was progress stalled for much of the window by failures, an action loop, or waiting on others (a human, a permission, another agent)? Isolated failures it worked past, or pausing by choice, do not count.",
                    "criteria": {"true": "Stalled by failures, a loop, or a dependency on others.", "false": "Made progress, worked past failures, or idle by choice."}},
        "others_work": {"type": "noul",
                        "instructions": "Was the agent mainly working on another agent's artifact (fixing, reviewing or extending it) or on a task another participant explicitly asked it to do? Co-building a shared team project does not count.",
                        "criteria": {"true": "Mainly another participant's artifact or explicit request.", "false": "Mainly its own or shared work, or nothing."}},
        "progress": {"type": "score", "instructions": "How much concrete progress did the agent make in this window?", "criteria": PROGRESS},
    }
    if has_chat:
        q["addresses_participant"] = {"type": "noul", "instructions": "Do the agent's messages reply to or address a specific named participant (another agent or a human)?",
                                      "criteria": {"true": "Addresses or replies to a specific named participant.", "false": "Broadcast to everyone."}}
    return q


def load_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    env = OUT.parents[2] / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit("OPENROUTER_API_KEY not found in the environment or the project .env")
    return key


def slim(ans: dict | None) -> dict | None:
    """Keep what the table needs (choices, confidences, probabilities, noul, scores); drop legends and types."""
    if not ans:
        return None
    out = {}
    for k, v in ans.items():
        if not isinstance(v, dict):
            continue
        out[k] = {x: v[x] for x in ("choice", "confidence", "probabilities", "noul", "score") if x in v}
    return out


def lines(path: Path):
    """Lines of a results JSONL and of its gzipped archive (path + '.gz'), if either exists."""
    if path.exists():
        yield from path.open()
    gz = Path(str(path) + ".gz")
    if gz.exists():
        yield from gzip.open(gz, "rt")


def prior_spend() -> float:
    s = 0.0
    for p in sorted(set(BS.glob(f"jev_*_{TAXONOMY}*.jsonl")) | {Path(str(q)[:-3]) for q in BS.glob(f"jev_*_{TAXONOMY}*.jsonl.gz")}):
        for line in lines(p):
            try:
                s += float(json.loads(line).get("cost") or 0)
            except json.JSONDecodeError:
                pass
    return s


def done_keys(jsonl: Path) -> set:
    done = set()
    if True:
        for line in lines(jsonl):
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue  # a torn last line after a kill
            if j.get("answers"):
                done.add((j["pt_date"], j["agent"], j["w"]))
    return done


QFUN = {"v3": questions}


def v2_questions(has_chat: bool) -> dict:
    from label_windows import questions as q2  # the v2 taxonomy, for state-vs-taxonomy decomposition runs
    return q2(has_chat)


QFUN["v2"] = v2_questions


async def call(client, key: str, item: dict, stats: dict) -> dict:
    body = {"model": MODEL, "state": item["state"], "questions": QFUN[item.get("qset", "v3")](item["has_chat"])}
    hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    last = None
    for attempt in range(8):
        try:
            r = await client.post(API, headers=hdr, json=body, timeout=90)
            if r.status_code == 200:
                return r.json()
            last = r.status_code
            if r.status_code in (408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524):
                stats["retries"] += 1
                ra = r.headers.get("retry-after")
                wait = float(ra) if ra and ra.replace(".", "", 1).isdigit() else min(60, 2 ** attempt)
                await asyncio.sleep(wait + random.random())
                continue
            return {"error": r.status_code, "body": r.text[:300]}
        except Exception as e:  # network hiccup / timeout
            last = type(e).__name__
            stats["retries"] += 1
            await asyncio.sleep(min(60, 2 ** attempt) + random.random())
    return {"error": f"retries_exhausted:{last}"}


async def run(items, jsonl: Path, key: str, cap: float, spent0: float, workers: int, keep_state: bool, total: int):
    import httpx
    q: asyncio.Queue = asyncio.Queue(maxsize=workers * 4)
    stats = {"spent": 0.0, "n": 0, "err": 0, "retries": 0, "stop": False, "t0": time.time()}
    fout = jsonl.open("a")

    async def worker(client):
        while True:
            it = await q.get()
            if it is None:
                q.task_done(); return
            if stats["stop"]:
                q.task_done(); continue
            res = await call(client, key, it, stats)
            cost = float(((res.get("usage") or {}).get("cost")) or 0)
            stats["spent"] += cost; stats["n"] += 1
            rec = {"pt_date": it["pt_date"], "agent": it["agent"], "w": it["w"], "answers": slim(res.get("answers")),
                   "error": res.get("error"), "cost": cost}
            if res.get("error"):
                stats["err"] += 1
            if keep_state:
                rec["state"] = it["state"]  # audit sample only (gated text, stays under data/)
            fout.write(json.dumps(rec, separators=(",", ":"), ensure_ascii=False) + "\n")
            if stats["n"] % 200 == 0:
                fout.flush()
            if stats["n"] % 2000 == 0:
                el = time.time() - stats["t0"]
                print(f"{stats['n']}/{total} labeled, {stats['err']} errors, {stats['retries']} retries, "
                      f"${spent0 + stats['spent']:.3f} total, {stats['n'] / el:.1f}/s, eta {(total - stats['n']) / max(stats['n'] / el, 1e-9) / 3600:.1f} h",
                      flush=True)
            if spent0 + stats["spent"] >= cap:
                if not stats["stop"]:
                    print(f"spend cap reached (${spent0 + stats['spent']:.3f} >= ${cap}); stopping", flush=True)
                stats["stop"] = True
            q.task_done()

    limits = httpx.Limits(max_connections=workers, max_keepalive_connections=workers)
    async with httpx.AsyncClient(limits=limits, http2=False) as client:
        tasks = [asyncio.create_task(worker(client)) for _ in range(workers)]
        for it in items:
            if stats["stop"]:
                break
            await q.put(it)
        for _ in tasks:
            await q.put(None)
        await asyncio.gather(*tasks)
    fout.close()
    return stats


def iter_items(f: pl.DataFrame, done: set, qset: str = "v3"):
    for r in f.iter_rows(named=True):
        if (r["pt_date"], r["agent"], r["w"]) in done:
            continue
        st = json.loads(r["state_json"]) if "state_json" in r else A.state_dict(r)
        yield {"pt_date": r["pt_date"], "agent": r["agent"], "w": r["w"], "has_chat": bool(r["has_chat"]), "state": st, "qset": qset}


# ----------------------------------------------------------------------------- compile
P_COLS = [f"p_{k}" for k in BEHAVIORS]


def flatten(j: dict) -> dict:
    a = j.get("answers") or {}
    b, pr = a.get("behavior") or {}, a.get("progress") or {}
    bp, pp = b.get("probabilities") or {}, pr.get("probabilities") or {}
    row = {"pt_date": j["pt_date"], "agent": j["agent"], "w": j["w"], "behavior": b.get("choice"), "behavior_conf": b.get("confidence")}
    row.update({f"p_{k}": (float(bp[k]) if k in bp else (0.0 if bp else None)) for k in BEHAVIORS})
    row.update({"p_blocked": (a.get("blocked") or {}).get("noul"), "p_others_work": (a.get("others_work") or {}).get("noul"),
                "p_addresses_participant": (a.get("addresses_participant") or {}).get("noul"),
                "progress_score": pr.get("score"), "progress_conf": pr.get("confidence")})
    row.update({f"p_progress_{i}": (float(pp[str(i)]) if str(i) in pp else (0.0 if pp else None)) for i in range(5)})
    row.update({"label_error": None if a else str(j.get("error")), "cost": j.get("cost") or 0.0})
    return row


def compile_all(jsonl: Path, spent_total: float):
    latest, costs = {}, {}
    for line in lines(jsonl):
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue  # torn line after a kill
        k = (j["pt_date"], j["agent"], j["w"])
        costs[k] = costs.get(k, 0.0) + float(j.get("cost") or 0)  # every attempt's cost counts
        if j.get("answers") or k not in latest:  # answers win over earlier errors
            latest[k] = j
    lab = pl.DataFrame([flatten(j) for j in latest.values()], infer_schema_length=None)
    lab = lab.with_columns(pl.Series("cost", [costs[(r[0], r[1], r[2])] for r in lab.select("pt_date", "agent", "w").iter_rows()]))
    win = A.windows()
    feats = A.features()
    feats = feats.with_columns(pl.Series("state_chars", [len(json.dumps(A.state_dict(r), ensure_ascii=False)) for r in feats.iter_rows(named=True)],
                                         dtype=pl.Int32))
    fl = (feats.select(A.KEY + [c for c in A.FLAG_COLS if c != "has_chat" and c not in win.columns] + ["state_chars"])
          .rename({"source": "intention_source"}))
    f32 = [c for c in lab.columns if c.startswith("p_") or c in ("behavior_conf", "progress_score", "progress_conf", "cost")]
    lab = lab.with_columns(pl.col("agent").cast(pl.Int8), pl.col("w").cast(pl.Int32), pl.col("label_error").cast(pl.Utf8),
                           *[pl.col(c).cast(pl.Float32) for c in f32])
    out = (win.join(fl, on=A.KEY, how="left").join(lab, on=A.KEY, how="left")
           .with_columns(pl.col("behavior").is_not_null().alias("labeled"), (pl.col("n_own").fill_null(0) > 0).alias("has_chat"),
                         pl.col("intention_source").replace({"CONSOLIDATE": "consolidate", "START_USING_COMPUTER": "session_start"}).cast(pl.Categorical),
                         pl.col("behavior").cast(pl.Categorical),
                         pl.col("regime").cast(pl.Utf8).cast(pl.Categorical), pl.col("w").cast(pl.Int16))
           .rename({"consolidate": "n_consolidate", "talk": "n_talk", "turns": "n_turns", "idle": "n_idle_events", "paused": "n_paused_min",
                    "other_event": "n_other_events", "session_start": "session_start_in_window", "pause_s": "declared_pause_s"}))
    lead = ["pt_date", "agent", "w", "t0", "t1", "goal_no", "regime", "holdout", "active", "in_span", "labeled", "behavior", "behavior_conf"]
    out = out.select(lead + P_COLS + [c for c in out.columns if c not in lead + P_COLS]).sort(A.KEY)
    path = OUT / f"behavior_states_{TAXONOMY}.parquet"
    out.write_parquet(path, compression="zstd", compression_level=10)
    act = out.filter("active")
    n_lab = int(act["labeled"].sum())
    params = {"model": MODEL, "taxonomy": TAXONOMY, "window_min": A.WIN_MIN, "states": list(BEHAVIORS),
              "rows": out.height, "active_windows": act.height, "labeled": n_lab, "unlabeled_active": act.height - n_lab,
              "holdout_rows_labeled": int(act.filter("holdout")["labeled"].sum()), "spent_usd_full_run": round(float(lab["cost"].sum()), 4),
              "spent_usd_total_v3": round(spent_total, 4), "stale_min": A.STALE_MIN, "self_repeat_cos": A.SELF_COS,
              "chat_budget_chars": A.CHAT_BUDGET, "intention_chars": A.INTENT_CHARS, "zero_shot": True}
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov[f"behavior_states_{TAXONOMY}"] = {
        "built_by": "infra/behavior_states/label_v3.py (assembly: infra/behavior_states/assemble_v3.py)", "git_commit": git_commit(),
        "inputs": {"source": "ai-village", "revision": REVISION,
                   "tables": ["activity_bins", "calendar", "actions", "artifact_commands_text (verbs)", "raw computer_use_turns (turn_outcomes)", "events_core", "chat_core", "chat_text",
                              "chat_mentions_clean", "exposure", "intentions", "intentions_text", "embeddings/chat_bge_small"]},
        "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    (BS / f"behavior_states_{TAXONOMY}_provenance.json").write_text(json.dumps(prov[f"behavior_states_{TAXONOMY}"], indent=1))
    print(json.dumps(params, indent=1))
    print(f"wrote {path} ({path.stat().st_size / 1e6:.1f} MB, {out.height} rows)")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--keys", help="JSONL with pt_date/agent/w: label exactly these windows (audit run; states kept)")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--tag", default="", help="suffix for the JSONL name (e.g. a second validation pass)")
    ap.add_argument("--max-usd", type=float, default=15.0, help="hard cap on total usage.cost over all v3 runs")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--compile-only", action="store_true")
    ap.add_argument("--estimate", action="store_true", help="assemble and report state sizes; no calls")
    ap.add_argument("--state-from", help="with --keys: take the states from this JSONL (e.g. the v1/v2 draft states) instead of assembling")
    ap.add_argument("--questions", default="v3", choices=["v2", "v3"], help="question set (v2 only for decomposition runs)")
    ap.add_argument("--retry-errors", action="store_true", help="with --all: label only windows whose last attempt errored (e.g. HTTP 402)")
    args = ap.parse_args()
    if args.workers > 16:
        sys.exit("at most 16 concurrent requests")
    jsonl = BS / (f"jev_draft_{TAXONOMY}{args.tag}.jsonl" if args.keys else f"jev_all_{TAXONOMY}{args.tag}.jsonl")
    if args.compile_only:
        return compile_all(jsonl, prior_spend()) if args.all else print("draft runs are compared with compare_labels.py")
    keys = None
    if args.keys:
        keys = pl.DataFrame([{k: json.loads(l)[k] for k in ("pt_date", "agent", "w")} for l in open(args.keys)])
    t = time.time()
    if args.state_from:  # decomposition runs: fixed states from an earlier assembly
        rows = [json.loads(l) for l in open(args.state_from)]
        f = pl.DataFrame([{"pt_date": r["pt_date"], "agent": r["agent"], "w": r["w"], "has_chat": r["state"].get("own_chat_messages") not in (None, "none"),
                           "state_json": json.dumps(r["state"], ensure_ascii=False)} for r in rows])
    else:
        f = A.features(keys)
    if args.all and args.retry_errors:
        errk, okk = set(), set()
        for line in lines(jsonl):
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            (okk if j.get("answers") else errk).add((j["pt_date"], j["agent"], j["w"]))
        errk -= okk
        f = f.filter(pl.struct(A.KEY).map_elements(lambda r: (r["pt_date"], r["agent"], r["w"]) in errk, return_dtype=pl.Boolean))
        print(f"retrying {f.height} errored windows", flush=True)
    if args.limit:
        f = f.head(args.limit)
    print(f"assembled {f.height} active windows in {time.time() - t:.0f}s", flush=True)
    if args.estimate:
        n = [len(json.dumps(A.state_dict(r), ensure_ascii=False)) for r in f.iter_rows(named=True)]
        print(f"state chars: mean {sum(n) / len(n):.0f}, total {sum(n)}")
        return
    done = done_keys(jsonl)
    spent0 = prior_spend()
    todo = f.height - len(done & set(zip(f["pt_date"], f["agent"], f["w"])))
    print(f"{todo} windows to label ({len(done)} done); v3 spend so far ${spent0:.4f}; cap ${args.max_usd}", flush=True)
    if spent0 >= args.max_usd:
        sys.exit("cap already reached")
    key = load_key()
    stats = asyncio.run(run(iter_items(f, done, args.questions), jsonl, key, args.max_usd, spent0, args.workers, bool(args.keys), todo))
    print(f"done: {stats['n']} calls, {stats['err']} errors, {stats['retries']} retries, this run ${stats['spent']:.4f}, "
          f"v3 total ${spent0 + stats['spent']:.4f}, {time.time() - stats['t0']:.0f}s", flush=True)
    if args.all and not args.limit:
        compile_all(jsonl, spent0 + stats["spent"])
    elif args.all:
        print("partial run (--limit): compile with --all --compile-only", flush=True)


if __name__ == "__main__":
    main()
