"""H37 scheme, step 2: zero-shot stance labels for reply pairs via Jev on OpenRouter (approved by Vivian).

API pattern, model and key loading are reused from infra/behavior_states/label_windows.py (imported, not copied):
API, MODEL, load_key(). The key is read from the environment or the gitignored project .env and is never printed,
logged or written.

Per pair (A -> B), Jev sees the two messages (A truncated to 800 chars; B to a 1,000-char window around its first
mention of A's author, else its head) and the two speakers' display names. No team, role, vote or period
information is sent. Questions:
  stance    choice: agree / support / neutral / oppose / undermine (B's stance toward A or A's author)
  responds  noul:   does B respond to or engage with A (or A's author)?
Stored (codes only, no text): pair key, stance choice, confidence, the 5 probabilities, responds, cost.

HARD SPEND CAP: the sum of usage.cost over every labels/*.jsonl file in this folder (all runs) must stay below
--cap (default $1.90, task cap $2.00). Requests in flight when the cap is hit are the only overshoot (<= workers x
~$0.0001).

Concurrency: one Python thread with asyncio (<= --workers requests in flight); CPU use is negligible.

Usage:
  uv run --with httpx python hypotheses/H37-stance-spins/scheme/label_stance.py --goal 40 --limit 5 --tag smoke
  uv run --with httpx python hypotheses/H37-stance-spins/scheme/label_stance.py --goal 12 --tag main
  uv run --with httpx python hypotheses/H37-stance-spins/scheme/label_stance.py --goal 51 --select g51_sample.parquet --tag main
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "infra/behavior_states"))
from common import OUT as SHARED, REVISION, git_commit, holdout_mask  # noqa: E402
from label_windows import API, MODEL, load_key  # noqa: E402

DATA = ROOT / "data/processed/H37-stance-spins"
LABELS = DATA / "labels"
TAXONOMY = "stance-v1"

STANCES = {
    "agree": "B agrees with, endorses, accepts or confirms what A says or proposes.",
    "support": "B helps, encourages, thanks, praises or backs A's author or their work, without disputing anything A says.",
    "neutral": "B takes no side on A: it asks a question, gives information or a status update, handles logistics, or just acknowledges A.",
    "oppose": "B disagrees with, rejects, corrects, rebuts or argues against what A says or proposes.",
    "undermine": "B attacks, discredits, mocks, accuses or works against A's author or their work.",
}
SIGN = {"agree": 1, "support": 1, "neutral": 0, "oppose": -1, "undermine": -1}


def questions() -> dict:
    return {
        "stance": {"type": "choice",
                   "instructions": "Message B was posted after message A in a group chat among AI agents. What is B's stance toward A (its content or its author)? Judge B's substantive stance and ignore courtesy openers such as thanks or greetings when B goes on to disagree.",
                   "criteria": STANCES},
        "responds": {"type": "noul",
                     "instructions": "Does message B respond to, refer to or engage with message A or A's author?",
                     "criteria": {"true": "Yes, B responds to, refers to or engages with A or its author.",
                                  "false": "No, B is about something else."}},
    }


def window_around(text: str, name: str | None, n: int) -> str:
    text = text or ""
    if len(text) <= n:
        return text
    pos = -1
    if name:
        for alias in {name, name.replace("Claude ", ""), name.replace(" Pro", "")}:
            if len(alias) >= 3:
                m = re.search(re.escape(alias), text, re.IGNORECASE)
                if m and (pos < 0 or m.start() < pos):
                    pos = m.start()
    if pos < 0:
        return text[:n] + " [...]"
    lo = max(0, min(pos - n // 3, len(text) - n))
    return ("[...] " if lo > 0 else "") + text[lo:lo + n] + (" [...]" if lo + n < len(text) else "")


def make_states(pairs: pl.DataFrame) -> list[dict]:
    names = dict(pl.read_parquet(SHARED / "roster.parquet", columns=["agent", "name"]).iter_rows())
    ids = set(pairs["msg_a"].to_list()) | set(pairs["msg_b"].to_list())
    txt = pl.read_parquet(SHARED / "chat_text.parquet", columns=["message_id", "text"]).filter(pl.col("message_id").is_in(list(ids)))
    T = dict(txt.iter_rows())
    out = []
    for r in pairs.iter_rows(named=True):
        na, nb = names.get(r["agent_a"], "an agent"), names.get(r["agent_b"], "an agent")
        state = {"message_A": {"speaker": na, "text": window_around(T.get(r["msg_a"], ""), None, 800)},
                 "message_B": {"speaker": nb, "text": window_around(T.get(r["msg_b"], ""), na, 1000)}}
        out.append({"goal_no": int(r["goal_no"]), "pair_id": int(r["pair_id"]), "msg_a": r["msg_a"], "msg_b": r["msg_b"], "state": state})
    return out


def total_spent() -> float:
    s = 0.0
    for f in LABELS.glob("*.jsonl"):
        for line in f.open():
            try:
                s += float(json.loads(line).get("cost") or 0)
            except Exception:
                pass
    return s


async def call(client, sem, item, key):
    body = {"model": MODEL, "state": item["state"], "questions": questions()}
    async with sem:
        for attempt in range(5):
            try:
                r = await client.post(API, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                                      json=body, timeout=60)
                if r.status_code == 200:
                    return r.json()
                if r.status_code in (429, 500, 502, 503, 504):
                    await asyncio.sleep(2 ** attempt); continue
                return {"error": r.status_code}
            except Exception:
                await asyncio.sleep(2 ** attempt)
    return {"error": "retries_exhausted"}


def parse(res: dict) -> dict:
    a = res.get("answers") or {}
    st = a.get("stance") or {}
    rp = a.get("responds") or {}
    probs = st.get("probabilities") or {}
    return {"stance": st.get("choice"), "stance_conf": st.get("confidence"),
            **{f"p_{k}": (float(probs[k]) if isinstance(probs, dict) and k in probs else None) for k in STANCES},
            "responds": rp.get("noul"), "responds_conf": rp.get("confidence")}


async def run(items, key, cap, workers, jsonl):
    import httpx
    spent0 = total_spent()
    if spent0 >= cap:
        print(f"cap already reached (${spent0:.4f} >= ${cap}); nothing sent", flush=True)
        return spent0
    sem = asyncio.Semaphore(workers)
    spent = spent0
    stop = False
    async with httpx.AsyncClient(http2=False) as client:
        with jsonl.open("a") as fout:
            for k in range(0, len(items), workers * 4):
                if stop:
                    break
                batch = items[k:k + workers * 4]
                res = await asyncio.gather(*[call(client, sem, it, key) for it in batch])
                for it, r in zip(batch, res):
                    cost = float(((r.get("usage") or {}).get("cost")) or 0)
                    spent += cost
                    rec = {"goal_no": it["goal_no"], "pair_id": it["pair_id"], "msg_a": it["msg_a"], "msg_b": it["msg_b"],
                           **parse(r), "error": r.get("error"), "cost": cost, "taxonomy": TAXONOMY}
                    fout.write(json.dumps(rec) + "\n")
                fout.flush()
                if (k // (workers * 4)) % 25 == 0:
                    print(f"  {k + len(batch)}/{len(items)} labelled; total spent ${spent:.4f}", flush=True)
                if spent >= cap:
                    print(f"HARD CAP reached: ${spent:.4f} >= ${cap}; stopping", flush=True)
                    stop = True
    return spent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", type=int, required=True)
    ap.add_argument("--pairs-file", help="pairs parquet under pairs/ (default G<NN>.parquet)")
    ap.add_argument("--select", help="parquet with pair_id column (subset to label), under data/processed/H37-stance-spins/")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--tag", default="main")
    ap.add_argument("--cap", type=float, default=1.90)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    held = set(json.loads((ROOT / "hypotheses/holdout.json").read_text())["goal_periods_held_out"])
    if args.goal in held and os.environ.get("H37_CONFIRM_HOLDOUT") != "yes-locked-holdout":
        sys.exit("refusing a held-out goal period (only analysis/confirm_g34.py may label it, with its flags)")
    pairs = pl.read_parquet(DATA / "pairs" / (args.pairs_file or f"G{args.goal:02d}.parquet"))
    if args.goal not in held:
        assert not any(holdout_mask(pairs["pt_date"].to_list(), pairs["goal_no"].to_list()))
    if args.select:
        sel = pl.read_parquet(DATA / args.select)
        pairs = pairs.join(sel.select("pair_id"), on="pair_id", how="semi")
    LABELS.mkdir(parents=True, exist_ok=True)
    jsonl = LABELS / f"G{args.goal:02d}_{args.tag}.jsonl"
    done = set()
    for f in LABELS.glob(f"G{args.goal:02d}_*.jsonl"):
        for line in f.open():
            j = json.loads(line)
            if j.get("stance") is not None:
                done.add(j["pair_id"])
    pairs = pairs.filter(~pl.col("pair_id").is_in(list(done)))
    if args.limit:
        pairs = pairs.head(args.limit)
    items = make_states(pairs)
    print(f"G{args.goal:02d}: {len(items)} pairs to label ({len(done)} done); spent so far ${total_spent():.4f}; cap ${args.cap}", flush=True)
    key = load_key()
    spent = asyncio.run(run(items, key, args.cap, args.workers, jsonl))
    print(f"total spent across all H37 runs: ${spent:.4f}", flush=True)
    prov_path = DATA / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov.setdefault("labels", {"built_by": "hypotheses/H37-stance-spins/scheme/label_stance.py", "runs": []})
    prov["labels"]["git_commit"] = git_commit()
    prov["labels"]["inputs"] = [{"source": "ai-village", "revision": REVISION, "tables": ["shared/chat_text", "shared/roster", "H37 pairs"]}]
    prov["labels"]["params"] = {"model": MODEL, "taxonomy": TAXONOMY, "stances": list(STANCES), "a_chars": 800, "b_chars": 1000}
    prov["labels"]["runs"].append({"goal": args.goal, "tag": args.tag, "n_sent": len(items), "total_spent_usd": round(spent, 5),
                                   "at": dt.datetime.now(dt.timezone.utc).isoformat()})
    prov["labels"]["built_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    prov_path.write_text(json.dumps(prov, indent=1, default=str))


if __name__ == "__main__":
    main()
