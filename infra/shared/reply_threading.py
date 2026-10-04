"""DQ2: reply threading and stance labels (shared tables reply_pairs, reply_graph). Design: infra/data-quality/reply_threading.md.

For every agent chat message B, rank the messages A its author could have seen (same room, posted before the call that
produced B, same PT day, <= 60 min before it) and keep the top K = 3. Jev (typesafe/jev-1.13 on OpenRouter, zero-shot,
approved by Vivian) answers two questions per (A, B) pair in one call: is B a direct reply to A (noul), and B's stance
toward A (choice: supports / opposes / asks / neutral). Placebo pairs (A arrived during B's own model call, or A came
after B) and an exhaustive audit of whole candidate pools are labelled too.

  uv run python infra/shared/reply_threading.py candidates                 # codes only, ~2 min, 2 threads
  uv run --with httpx python infra/shared/reply_threading.py label --phase smoke --limit 20
  uv run --with httpx python infra/shared/reply_threading.py label --phase top1
  uv run --with httpx python infra/shared/reply_threading.py label --phase audit|placebo|extras
  uv run python infra/shared/reply_threading.py val-sample                 # blind validation sheet (gated text, data/processed only)
  uv run python infra/shared/reply_threading.py validate                   # kappa, confidence curves, placebo, ground truth
  uv run python infra/shared/reply_threading.py compile                    # reply_pairs.parquet, reply_graph.parquet

Visibility: H18's call-start rule (`--visibility h18`, default) until the DQ1 context ledger exists; then
`--visibility ledger` cuts each pool at the ledger's context-assembly time of B's own call (`call_windows.t_call`; see `ledger_call_starts`) and writes `*_ledger` files.

HARD SPEND CAP: the sum of usage.cost over every labels/*.jsonl file (all runs, all phases) stays below CAP_USD
($7.90; task cap $8.00). The only overshoot is requests already in flight when the cap is hit (<= WORKERS x ~$0.0001).
The key comes from label_windows.load_key() (environment or the gitignored project .env) and is never printed or
written. Message text goes only to the Jev API and, for the blind validation sheet, to data/processed (gitignored).
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "behavior_states"))
from common import OUT, REVISION, git_commit, holdout_mask  # noqa: E402

RT = OUT / "reply_threading"          # working folder: candidates, label JSONLs (codes only), validation (gated)
LABELS = RT / "labels"
VAL = RT / "validation"

# ---- pre-registered candidate rule (written 2026-10-04 before any Jev label; see the design doc) ----
K = 3                 # candidates kept per B in reply_pairs
GUARD_S = 1.0         # B's own action mirror is logged ~0.06 s before AGENT_TALK (H18)
LOOKBACK_S = 3600     # pool: visible messages <= 60 min before B's call start ...
MAX_POOL = 40         # ... and at most the 40 most recent of them
REV_WIN_S = 1800      # reversed placebo: messages <= 30 min after B
W_MB, W_MA, W_NEW, W_POS = 0.20, 0.10, 0.05, 0.03   # score = cos + W_MB*B_names_A + W_MA*A_names_B + W_NEW*new - W_POS*ln(pos)
SEED = 20261004
KEEP_RANKS = 10       # working file keeps ranks 1..10 (reply_pairs keeps 1..K) ...
AUDIT_FRAC = 0.02     # ... except for a pre-drawn 2% of messages, whose whole pools are kept for the recall audit
SETS = ("cand", "invisible", "reversed")

# ---- Jev ----
CAP_USD = 7.90
WORKERS = 12
A_CHARS, B_CHARS = 700, 900
TAXONOMY = "reply-stance-v1"
STANCES = {
    "supports": "B agrees with, endorses, accepts, confirms, thanks, praises or builds on what A says or proposes, or does what A asked.",
    "opposes": "B explicitly disagrees with, rejects, corrects, disputes or criticizes what A says or proposes, or refuses what A asked. Reporting other facts or a different status without disputing A does not count.",
    "asks": "B asks A's author a question about A, or asks for clarification, details or confirmation of A.",
    "neutral": "B takes no side on A: it gives information or a status update, acknowledges A, handles logistics, or is unrelated to A.",
}
KIND = {"agent": 0, "human": 1, "automated": 2}
# Second pass, only for pairs Jev called "opposes" (added 2026-10-04 at the coordinator's request after H37 measured an
# oppose precision of 0.30, mostly task corrections and polite declines). Written before any opposes pair was read.
OPP_TYPES = {
    "position": "B disagrees with A's position, argument, plan, proposal or decision, or criticizes A's author or their work.",
    "correction": "B corrects a fact, number, status, link or technical detail in A, or points out an error or bug in it, without disputing A's overall position or plan.",
    "decline": "B declines, refuses or defers a request, task or offer made in A.",
    "none": "B does not actually push back on A: it agrees, asks a question, or just gives information.",
}


def questions_opp() -> dict:
    return {"opp_type": {"type": "choice",
                         "instructions": "Message B was posted after message A in the same group chat room. If B pushes back on A, what kind of pushback is it? Judge B's substantive content and ignore courtesy openers.",
                         "criteria": OPP_TYPES}}


def questions() -> dict:
    return {
        "reply": {"type": "noul",
                  "instructions": "Message B was posted after message A in the same group chat room. Is B a direct reply or response to message A? Count it only if B takes up A specifically: answers its question, acts on its request, comments on or reacts to its content, or addresses its author about it. Being on the same general topic, or addressing A's author about something else, does not count.",
                  "criteria": {"true": "B directly replies or responds to message A.",
                               "false": "B does not respond to A: it is a broadcast, a status update, a reply to a different message, or only on the same general topic."}},
        "stance": {"type": "choice",
                   "instructions": "What is message B's stance toward message A? If B does not respond to A at all, choose neutral. Judge B's substantive stance and ignore courtesy openers such as thanks or praise when B goes on to disagree.",
                   "criteria": STANCES},
    }


# =====================================================================================================================
# candidates
# =====================================================================================================================

def _us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(np.int64)


def load_chat() -> pl.DataFrame:
    c = pl.read_parquet(OUT / "chat_core.parquet").with_row_index("msg")
    m = pl.read_parquet(OUT / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    assert c.height == m.height and (c["message_id"] == m["message_id"]).all()
    c = c.with_columns(m["mentions_roster"])
    ci = pl.read_parquet(OUT / "embeddings/chat_index.parquet").with_row_index("erow")
    c = c.join(ci, on="message_id", how="left").sort("msg")
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "win_start", "holdout"])
    c = c.join(cal, on="pt_date", how="left").sort("msg")
    hm = holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())
    return c.with_columns((pl.Series("hm", hm) | pl.col("holdout").fill_null(False)).alias("holdout"))


def turn_times() -> dict[int, np.ndarray]:
    """Per-agent sorted turn times (us): actions minus `pause` mirrors, plus events_core agent events (H18 rule)."""
    acts = (pl.scan_parquet(OUT / "actions.parquet").select("t", "agent", "action")
            .filter(pl.col("agent").is_not_null() & (pl.col("action").cast(pl.Utf8) != "pause")).select("t", "agent").collect())
    ev = (pl.scan_parquet(OUT / "events_core.parquet").select("t", "agent", "actor_kind")
          .filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null()).select("t", "agent").collect())
    allt = pl.concat([acts, ev]).sort("agent", "t")
    return {int(a): _us(sub["t"]) for (a,), sub in allt.group_by(["agent"], maintain_order=True)}


def window_around(text: str, name: str | None, n: int) -> str:
    """B text: whole if short, else an n-char window around the first mention of A's author, else the head."""
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


def ledger_call_starts(c: pl.DataFrame) -> pl.DataFrame:
    """Context-assembly time of the model call that produced each agent message B, from the DQ1 context ledger
    (`call_windows`: t_call with bounds t_call_lo / t_call_hi). B is matched through its AGENT_TALK event time (chat
    timestamps sit ~60 ms before the event) to the agent's call with t_first <= t_event <= t_log. Under the ledger's rule a
    message A is in that call's context iff it was posted in the agent's room before t_call (same pairs as `exposure`)."""
    cw = (pl.read_parquet(OUT / "call_windows.parquet", columns=["agent", "t_call", "t_call_lo", "t_call_hi", "t_first", "t_log", "start_conf"])
          .sort("t_first"))
    ev = (pl.read_parquet(OUT / "events_core.parquet", columns=["t", "message_id", "action_type"])
          .filter(pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev")))
    b = (c.filter(pl.col("speaker_kind") == "agent").select("msg", "message_id", "agent", "t").join(ev, on="message_id", how="left")
         .with_columns(pl.col("t_ev").fill_null(pl.col("t"))).sort("t_ev"))
    j = b.join_asof(cw, left_on="t_ev", right_on="t_first", by="agent", strategy="backward")
    j = j.with_columns(pl.when(pl.col("t_ev") <= pl.col("t_log")).then(pl.col("t_call")).otherwise(None).alias("t_call"))
    return j.select("msg", pl.col("t_call").dt.epoch("us").alias("lc"), pl.col("t_call_lo").dt.epoch("us").alias("lc_lo"),
                    pl.col("t_call_hi").dt.epoch("us").alias("lc_hi"), pl.col("start_conf").cast(pl.Utf8).alias("lc_conf")).sort("msg")


def build_candidates(visibility: str = "h18"):
    t0 = time.time()
    c = load_chat()
    E = np.asarray(np.load(OUT / "embeddings/chat_bge_small.npy"), dtype=np.float32)   # 183k x 384, ~280 MB
    n = c.height
    m_t = _us(c["t"])
    m_kind = c["speaker_kind"].cast(pl.Utf8).replace_strict(KIND, default=3).to_numpy().astype(np.int8)
    m_agent = c["agent"].fill_null(-1).to_numpy().astype(np.int16)
    m_room = c["room"].to_numpy()
    m_day = c["pt_date"].to_numpy()
    m_erow = c["erow"].fill_null(-1).to_numpy().astype(np.int64)
    m_ment = [frozenset(x or []) for x in c["mentions_roster"].to_list()]
    day_start = {d: int(v) for d, v in zip(c["pt_date"].to_list(), _us(c["win_start"].fill_null(c["t"])))}
    TT = turn_times()
    led = None
    if visibility == "ledger":
        L = ledger_call_starts(c)
        led = {k: np.full(n, -1, np.int64) for k in ("lc", "lc_lo", "lc_hi")}
        for k in led:
            led[k][L["msg"].to_numpy()] = L[k].fill_null(-1).to_numpy()
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    expo = pl.read_parquet(OUT / "exposure.parquet", columns=["msg", "agent"])
    by_agent = {}
    for (a,), sub in expo.group_by(["agent"], maintain_order=True):
        idx = sub["msg"].to_numpy().astype(np.int64)
        by_agent[int(a)] = idx[np.argsort(m_t[idx], kind="stable")]
    # room streams for the reversed placebo
    by_room = {}
    for r in np.unique(m_room):
        idx = np.where(m_room == r)[0]
        by_room[int(r)] = idx[np.argsort(m_t[idx], kind="stable")]

    def emb(ix):
        ok = m_erow[ix] >= 0
        out = np.zeros((len(ix), E.shape[1]), np.float32)
        if ok.any():
            out[ok] = E[m_erow[ix][ok]]
        return out, ok

    G = int(GUARD_S * 1e6)
    full_pool = np.random.default_rng(SEED).random(n) < AUDIT_FRAC   # pre-drawn audit subset: keep whole pools
    cols = {k: [] for k in ("b", "a", "set", "rank", "score", "cos", "mb", "ma", "new", "pos", "lag")}
    meta = []
    B_all = np.where(m_kind == 0)[0]
    B_all = B_all[np.argsort(m_t[B_all], kind="stable")]
    for a in np.unique(m_agent[B_all]):
        a = int(a)
        own = B_all[m_agent[B_all] == a]
        ex = by_agent.get(a, np.zeros(0, np.int64))
        ex_t = m_t[ex]
        tt = TT.get(a, np.zeros(0, np.int64))
        own_t = m_t[own]
        j = np.searchsorted(tt, own_t - G, side="left") - 1
        s = np.where(j >= 0, tt[np.clip(j, 0, None)], -1)
        ds = np.array([day_start.get(d, 0) for d in m_day[own]])
        fallback = s < ds - int(3600e6)               # no logged turn this day before B: use t_B - guard
        s = np.where(fallback, own_t - G, s)
        s_lo = s_hi = s
        if led is not None:                            # ledger t_call where B's call was found; else the H18 rule
            lc = led["lc"][own]
            okl = lc > 0
            s = np.where(okl, np.minimum(lc, own_t - 60_000), s)   # never after B itself (estimation error guard)
            s_lo = np.where(okl & (led["lc_lo"][own] > 0), np.minimum(led["lc_lo"][own], own_t), s)
            s_hi = np.where(okl & (led["lc_hi"][own] > 0), np.minimum(led["lc_hi"][own], own_t), s)
            fallback = ~okl
        prev_s = np.full(len(own), -1, np.int64)
        for q in range(1, len(own)):
            if m_day[own[q - 1]] == m_day[own[q]]:
                prev_s[q] = s[q - 1]
        eB, okB = emb(own)
        for q, b in enumerate(own):
            b = int(b)
            tb, sb, d = own_t[q], s[q], m_day[b]
            lo_t = max(sb - int(LOOKBACK_S * 1e6), ds[q] - int(3600e6))
            lo, hi = np.searchsorted(ex_t, lo_t, "left"), np.searchsorted(ex_t, sb, "left")
            P = ex[lo:hi]
            P = P[m_day[P] == d][-MAX_POOL:]
            hi2 = np.searchsorted(ex_t, tb, "left")
            Inv = ex[hi:hi2]
            Inv = Inv[m_day[Inv] == d]
            rs = by_room[int(m_room[b])]
            rlo, rhi = np.searchsorted(m_t[rs], tb, "right"), np.searchsorted(m_t[rs], tb + int(REV_WIN_S * 1e6), "right")
            Rv = rs[rlo:rhi]
            Rv = Rv[(m_agent[Rv] != a) & (m_day[Rv] == d)]
            meta.append((b, a, int(len(P)), int(len(Inv)), int(len(Rv)), int(sb), bool(fallback[q]), int(prev_s[q]),
                         int(s_lo[q]), int(s_hi[q])))
            bment = m_ment[b]
            for si, X in enumerate((P, Inv, Rv)):
                if not len(X):
                    continue
                eA, okA = emb(X)
                cos = np.where(okA & okB[q], eA @ eB[q], np.nan).astype(np.float32)
                mb = np.fromiter(((m_kind[x] == 0) and (int(m_agent[x]) in bment) for x in X), bool, len(X))
                ma = np.fromiter((a in m_ment[x] for x in X), bool, len(X))
                new = (m_t[X] >= prev_s[q]) if prev_s[q] > 0 else np.ones(len(X), bool)
                pos = np.arange(1, len(X) + 1) if si == 2 else np.arange(len(X), 0, -1)  # 1 = nearest to B / to the cutoff
                score = np.nan_to_num(cos, nan=0.0) + W_MB * mb + W_MA * ma + W_NEW * new - W_POS * np.log(pos)
                order = np.argsort(-score, kind="stable")
                keep = order[:(len(order) if full_pool[b] else KEEP_RANKS)] if si == 0 else order[:1]
                L = len(keep)
                cols["b"].append(np.full(L, b, np.uint32)); cols["a"].append(X[keep].astype(np.uint32))
                cols["set"].append(np.full(L, si, np.int8)); cols["rank"].append(np.arange(1, L + 1, dtype=np.int16))
                cols["score"].append(score[keep].astype(np.float32)); cols["cos"].append(cos[keep])
                cols["mb"].append(mb[keep]); cols["ma"].append(ma[keep]); cols["new"].append(new[keep])
                cols["pos"].append(pos[keep].astype(np.int16)); cols["lag"].append(((tb - m_t[X[keep]]) / 1e6).astype(np.float32))
    C = {k: np.concatenate(v) for k, v in cols.items()}
    cand = pl.DataFrame({"b": C["b"], "a": C["a"], "set": pl.Series(np.array(SETS)[C["set"]]).cast(pl.Categorical),
                         "rank": C["rank"], "score": C["score"], "cos": C["cos"], "b_names_a": C["mb"], "a_names_b": C["ma"],
                         "new": C["new"], "pos": C["pos"], "lag_s": C["lag"],
                         "a_kind": m_kind[C["a"].astype(np.int64)], "a_agent": m_agent[C["a"].astype(np.int64)].astype(np.int8),
                         "full_pool": full_pool[C["b"].astype(np.int64)]})
    mt = pl.DataFrame(meta, orient="row", schema={
        "b": pl.UInt32, "b_agent": pl.Int8, "n_pool": pl.Int16, "n_invisible": pl.Int16, "n_after": pl.Int16,
        "s_us": pl.Int64, "s_fallback": pl.Boolean, "prev_s_us": pl.Int64, "s_lo_us": pl.Int64, "s_hi_us": pl.Int64})
    mt = mt.join(c.select(pl.col("msg").alias("b"), "pt_date", "goal_no", "regime", "room", "holdout"), on="b", how="left")
    RT.mkdir(parents=True, exist_ok=True)
    sfx = "_ledger" if visibility == "ledger" else ""
    cand.write_parquet(RT / f"candidates{sfx}.parquet", compression="zstd")
    if not (RT / "msg_index.parquet").exists():
        c.select("msg", "message_id").write_parquet(RT / "msg_index.parquet", compression="zstd")  # pins row -> id
    mt.write_parquet(RT / f"b_meta{sfx}.parquet", compression="zstd")
    print(f"candidates: {cand.height} rows ({cand.group_by('set').len().rows()}), B={mt.height}, "
          f"B with pool={int((mt['n_pool'] > 0).sum())}, fallback={int(mt['s_fallback'].sum())}  {time.time() - t0:.0f}s", flush=True)
    write_prov(f"candidates{sfx}", {"visibility": visibility, "K": K, "guard_s": GUARD_S, "lookback_s": LOOKBACK_S,
                              "max_pool": MAX_POOL, "rev_win_s": REV_WIN_S,
                              "score": f"cos + {W_MB}*B_names_A + {W_MA}*A_names_B + {W_NEW}*new - {W_POS}*ln(pos)"})


# =====================================================================================================================
# Jev labelling
# =====================================================================================================================

def total_spent() -> float:
    s = 0.0
    for f in LABELS.glob("*.jsonl"):
        for line in f.open():
            try:
                s += float(json.loads(line).get("cost") or 0)
            except Exception:
                pass
    return s


def done_pairs(phase: str = "") -> set:
    out = set()
    field = "opp_type" if phase == "opptype" else "p_reply"
    for f in LABELS.glob("*.jsonl"):
        for line in f.open():
            j = json.loads(line)
            if j.get(field) is not None:
                out.add((j["b"], j["a"]))
    return out


def h37_pairs() -> pl.DataFrame:
    """(b, a) chat_core rows of pairs H37 already labelled (its own prompt; reused as separate columns, not as p_reply)."""
    d = OUT.parents[0] / "H37-stance-spins" / "labels"
    ids = set()
    for f in d.glob("*.jsonl"):
        for line in f.open():
            j = json.loads(line)
            if j.get("stance") is not None:
                ids.add((j["msg_b"], j["msg_a"]))
    idx = pl.read_parquet(RT / "msg_index.parquet")
    df = pl.DataFrame({"mb": [x[0] for x in ids], "ma": [x[1] for x in ids]}, schema={"mb": pl.Utf8, "ma": pl.Utf8})
    return (df.join(idx.select(pl.col("msg").alias("b"), pl.col("message_id").alias("mb")), on="mb")
            .join(idx.select(pl.col("msg").alias("a"), pl.col("message_id").alias("ma")), on="ma").select("b", "a"))


def load_labels() -> pl.DataFrame:
    recs = []
    for f in sorted(LABELS.glob("*.jsonl")):
        for line in f.open():
            recs.append(json.loads(line))
    if not recs:
        return pl.DataFrame()
    df = pl.DataFrame(recs, infer_schema_length=None)
    return df


def speaker_label(kind: int, agent: int, names: dict) -> str:
    if kind == 0:
        return f"{names.get(agent, 'an AI agent')} (AI agent)"
    if kind == 1:
        return "a human viewer"
    return "the village's automated system"


def make_states(pairs: pl.DataFrame) -> list[dict]:
    names = dict(pl.read_parquet(OUT / "roster.parquet", columns=["agent", "name"]).iter_rows())
    chat = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "speaker_kind", "agent"]).with_row_index("msg")
    ids = set(pairs["a"].to_list()) | set(pairs["b"].to_list())
    sub = chat.filter(pl.col("msg").is_in(list(ids)))
    txt = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"]).join(sub.select("message_id"), on="message_id", how="semi")
    T = dict(txt.iter_rows())
    info = {r[0]: (r[1], KIND.get(r[2], 3), -1 if r[3] is None else int(r[3])) for r in
            sub.select("msg", "message_id", pl.col("speaker_kind").cast(pl.Utf8), "agent").iter_rows()}
    out = []
    for r in pairs.select("b", "a", "set", "rank").iter_rows(named=True):
        ida, ka, aa = info[r["a"]]
        idb, kb, ab = info[r["b"]]
        na = names.get(aa) if ka == 0 else None
        ta = T.get(ida, "") or ""
        state = {"message_A": {"speaker": speaker_label(ka, aa, names),
                               "text": ta if len(ta) <= A_CHARS else ta[:A_CHARS] + " [...]"},
                 "message_B": {"speaker": speaker_label(kb, ab, names), "text": window_around(T.get(idb, ""), na, B_CHARS)}}
        out.append({"b": r["b"], "a": r["a"], "set": r["set"], "rank": r["rank"], "state": state})
    return out


def parse(res: dict, phase: str = "") -> dict:
    a = res.get("answers") or {}
    if phase == "opptype":
        o = a.get("opp_type") or {}
        pr = o.get("probabilities") or {}
        return {"opp_type": o.get("choice"), "opp_conf": o.get("confidence"),
                **{f"p_opp_{k}": (float(pr[k]) if isinstance(pr, dict) and k in pr else None) for k in OPP_TYPES}}
    rp, st = a.get("reply") or {}, a.get("stance") or {}
    probs = st.get("probabilities") or {}
    return {"p_reply": rp.get("noul"), "stance": st.get("choice"), "stance_conf": st.get("confidence"),
            **{f"p_{k}": (float(probs[k]) if isinstance(probs, dict) and k in probs else None) for k in STANCES}}


async def _call(client, sem, item, key, qs):
    from label_windows import API, MODEL
    body = {"model": MODEL, "state": item["state"], "questions": qs}
    async with sem:
        for attempt in range(6):
            try:
                r = await client.post(API, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                                      json=body, timeout=60)
                if r.status_code == 200:
                    return r.json()
                if r.status_code in (408, 429, 500, 502, 503, 504):
                    await asyncio.sleep(2 ** attempt); continue
                return {"error": r.status_code}
            except Exception:
                await asyncio.sleep(2 ** attempt)
    return {"error": "retries_exhausted"}


async def _run(items, key, cap, workers, jsonl, phase):
    import httpx
    spent = total_spent()
    if spent >= cap:
        print(f"cap already reached (${spent:.4f} >= ${cap}); nothing sent", flush=True)
        return spent
    sem = asyncio.Semaphore(workers)
    t0, nerr = time.time(), 0
    async with httpx.AsyncClient(http2=False) as client:
        with jsonl.open("a") as fout:
            step = workers * 8
            for k in range(0, len(items), step):
                batch = items[k:k + step]
                qs = questions_opp() if phase == "opptype" else questions()
                res = await asyncio.gather(*[_call(client, sem, it, key, qs) for it in batch])
                for it, r in zip(batch, res):
                    cost = float(((r.get("usage") or {}).get("cost")) or 0)
                    spent += cost
                    nerr += r.get("error") is not None
                    fout.write(json.dumps({"b": it["b"], "a": it["a"], "set": it["set"], "rank": it["rank"], "phase": phase,
                                           **parse(r, phase), "error": r.get("error"), "cost": cost,
                                           "taxonomy": "opp-type-v1" if phase == "opptype" else TAXONOMY}) + "\n")
                fout.flush()
                if (k // step) % 50 == 0:
                    rate = (k + len(batch)) / max(1e-9, time.time() - t0)
                    print(f"  {k + len(batch)}/{len(items)}  spent ${spent:.4f}  errors {nerr}  {rate:.1f}/s", flush=True)
                if spent >= cap:
                    print(f"HARD CAP reached: ${spent:.4f} >= ${cap}; stopping", flush=True)
                    break
    return spent


def select_items(phase: str, limit: int | None, budget: float | None) -> pl.DataFrame:
    cand = pl.read_parquet(RT / "candidates.parquet")
    meta = pl.read_parquet(RT / "b_meta.parquet")
    rng = np.random.default_rng(SEED)
    nh = meta.filter(~pl.col("holdout"))
    if phase == "smoke":
        bs = nh.filter(pl.col("n_pool") > 0)["b"].sample(limit or 20, seed=SEED)
        return cand.filter((pl.col("set") == "cand") & (pl.col("rank") == 1) & pl.col("b").is_in(bs.implode()))
    if phase == "top1":       # every message with a candidate; non-holdout first, then holdout
        x = cand.filter((pl.col("set") == "cand") & (pl.col("rank") == 1)).join(meta.select("b", "holdout"), on="b")
        return x.with_columns(pl.Series("_r", rng.random(x.height))).sort("holdout", "_r").drop("holdout", "_r")
    if phase == "audit":      # whole pools of 300 random non-holdout messages (pre-drawn subset) with >= 4 candidates
        fp = cand.filter(pl.col("full_pool")).select("b").unique()
        pool = nh.filter(pl.col("n_pool") >= 4).join(fp, on="b", how="semi")["b"].sort().to_numpy()
        bs = rng.choice(pool, size=min(300, len(pool)), replace=False)
        return cand.filter((pl.col("set") == "cand") & pl.col("b").is_in(bs.tolist()))
    if phase == "placebo":    # 2,000 invisible + 1,000 reversed, non-holdout, agent B
        inv = cand.filter(pl.col("set") == "invisible").join(nh.select("b"), on="b", how="semi")
        rev = cand.filter(pl.col("set") == "reversed").join(nh.select("b"), on="b", how="semi")
        inv = inv.sample(min(2000, inv.height), seed=SEED)
        rev = rev.sample(min(1000, rev.height), seed=SEED)
        return pl.concat([inv, rev])
    if phase == "extras":     # ranks 2..K where rank 1 is ambiguous; most ambiguous first; non-holdout first
        lab = load_labels().filter((pl.col("set") == "cand") & (pl.col("rank") == 1) & pl.col("p_reply").is_not_null())
        top = lab.select("b", pl.col("p_reply").cast(pl.Float64)).unique("b")
        amb = top.filter(pl.col("p_reply") < 0.8).join(meta.select("b", "holdout"), on="b")
        amb = amb.with_columns((pl.col("p_reply") - 0.5).abs().alias("amb"))
        x = cand.filter((pl.col("set") == "cand") & (pl.col("rank") >= 2) & (pl.col("rank") <= K)).join(amb, on="b")
        x = x.join(h37_pairs(), on=["b", "a"], how="anti")   # H37 already labelled these (coordinator, 2026-10-04)
        return x.sort("holdout", "rank", "amb").drop("p_reply", "holdout", "amb")
    if phase == "opptype":    # Amendment 2: non-holdout visible candidates Jev called "opposes" with p_reply >= 0.5
        lab = load_labels().filter(pl.col("p_reply").is_not_null() & (pl.col("stance") == "opposes") & (pl.col("set") == "cand")
                                   & (pl.col("p_reply") >= 0.5))
        x = (cand.join(lab.select(pl.col("b").cast(pl.UInt32), pl.col("a").cast(pl.UInt32)).unique(), on=["b", "a"], how="semi")
             .filter(pl.col("set") == "cand").join(nh.select("b"), on="b", how="semi"))
        return x.unique(["b", "a"], keep="first").sort("b", "rank")
    if phase == "top1_ledger":   # Amendment 2: ledger top-1 not yet labelled (nor by H37); non-holdout; II+III, then I at random
        cl = pl.read_parquet(RT / "candidates_ledger.parquet").filter((pl.col("set") == "cand") & (pl.col("rank") == 1))
        ml = pl.read_parquet(RT / "b_meta_ledger.parquet").filter(~pl.col("holdout")).select("b", "regime")
        x = cl.join(ml, on="b").join(h37_pairs(), on=["b", "a"], how="anti")
        x = x.with_columns((pl.col("regime").cast(pl.Utf8) == "I").alias("_r1"), pl.Series("_u", rng.random(x.height)))
        return x.sort("_r1", "_u").drop("regime", "_r1", "_u")
    raise SystemExit(f"unknown phase {phase}")


def label(phase: str, limit: int | None, cap: float, workers: int):
    from label_windows import load_key
    LABELS.mkdir(parents=True, exist_ok=True)
    pairs = select_items(phase, limit, None)
    done = done_pairs(phase)
    if done:
        pairs = pairs.join(pl.DataFrame({"b": [d[0] for d in done], "a": [d[1] for d in done]},
                                        schema={"b": pl.UInt32, "a": pl.UInt32}), on=["b", "a"], how="anti")
    if limit and phase != "smoke":
        pairs = pairs.head(limit)
    print(f"phase {phase}: {pairs.height} pairs to label ({len(done)} labelled already); spent so far ${total_spent():.4f}; cap ${cap}", flush=True)
    if pairs.is_empty():
        return
    key = load_key()
    spent = 0.0
    CH = 20000           # assemble text in chunks to keep memory flat
    for lo in range(0, pairs.height, CH):
        items = make_states(pairs.slice(lo, CH))
        spent = asyncio.run(_run(items, key, cap, workers, LABELS / f"{phase}.jsonl", phase))
        if spent >= cap:
            break
    print(f"phase {phase} done; total spent across all runs ${spent:.4f}", flush=True)
    write_prov(f"labels:{phase}", {"model": "typesafe/jev-1.13", "taxonomy": TAXONOMY, "a_chars": A_CHARS, "b_chars": B_CHARS,
                                   "cap_usd": cap, "total_spent_usd": round(total_spent(), 5)})


# =====================================================================================================================
# provenance helper
# =====================================================================================================================

def write_prov(step: str, params: dict):
    RT.mkdir(parents=True, exist_ok=True)
    p = RT / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov[step] = {"built_by": "infra/shared/reply_threading.py", "git_commit": git_commit(),
                  "inputs": [{"source": "ai-village", "revision": REVISION,
                              "tables": ["shared/chat_core", "shared/chat_mentions_clean", "shared/chat_text (Jev only)",
                                         "shared/exposure", "shared/actions", "shared/events_core", "shared/calendar",
                                         "shared/roster", "shared/embeddings/chat_bge_small", "shared/embeddings/chat_index"]}],
                  "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(prov, indent=1, default=str))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    c1 = sp.add_parser("candidates"); c1.add_argument("--visibility", default="h18", choices=["h18", "ledger"])
    c2 = sp.add_parser("label"); c2.add_argument("--phase", required=True); c2.add_argument("--limit", type=int)
    c2.add_argument("--cap", type=float, default=CAP_USD); c2.add_argument("--workers", type=int, default=WORKERS)
    c3 = sp.add_parser("val-sample"); c3.add_argument("--which", default="random100", choices=["random100", "mixed75"])
    sp.add_parser("validate"); sp.add_parser("compile")
    a = ap.parse_args()
    if a.cmd == "candidates":
        build_candidates(a.visibility)
    elif a.cmd == "label":
        if a.cap > 8.0:
            sys.exit("cap above the $8.00 task cap")
        label(a.phase, a.limit, a.cap, a.workers)
    elif a.cmd == "val-sample":
        from reply_threading_validate import val_sample
        val_sample(a.which)
    elif a.cmd == "validate":
        from reply_threading_validate import validate
        validate()
    elif a.cmd == "compile":
        from reply_threading_validate import compile_tables
        compile_tables()


if __name__ == "__main__":
    main()
