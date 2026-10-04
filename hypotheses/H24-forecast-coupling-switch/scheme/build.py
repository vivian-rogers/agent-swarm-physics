"""H24 scheme: build data/processed/H24-forecast-coupling-switch/G21/ from the shared tables and the #21
computer-use text sidecar (scheme/extract_cu_text.py must have run first).

Outputs (no agent text except in the gitignored cu_turns_text sidecar):
  switch_on.parquet     per agent: tau_intent, tau_record, tau (switch-on), role, first numeric chat exposure
  statements.parquet    #21 statements (chat + intentions) with flags; stmt_w64.npy whitened coordinates (fp16)
  docs.parquet          typed / heredoc document chunks (~1000 chars) with flags; docs_w64.npy (fp16)
  numeric.parquet       extracted anchor forecasts: t, speaker, source, question, value, attribution
  goal_vec.npz          g-hat (goal text + kickoff), goal-only and kickoff-only, whitened (64-d)
  _provenance.json

Usage: uv run python hypotheses/H24-forecast-coupling-switch/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h24lib import (COMPARISON_RE, CONFIRM_MIN, FORECAST_RE, H24, PCT_RE, ROOT, extract_numbers,  # noqa: E402
                    intention_reads, loose_other_pats, mention_regexes, record_reads, unit)
from common import OUT, REVISION, git_commit, load_goals, load_whitener, holdout_mask  # noqa: E402

GOAL = 21
DEST = H24 / f"G{GOAL}"
DIM = 64
UTC = dt.timezone.utc


def embed(texts):
    import torch
    torch.set_num_threads(2)
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
    m.max_seq_length = 256
    order = np.argsort([len(s) for s in texts])
    E = np.zeros((len(texts), 384), dtype=np.float32)
    bs = 32
    for k in range(0, len(texts), bs):
        idx = order[k:k + bs]
        E[idx] = m.encode([texts[j] for j in idx], batch_size=bs, normalize_embeddings=True, convert_to_numpy=True)
    return E


def chunk_text(s: str, size: int = 1000) -> list[str]:
    """Split on paragraph boundaries into ~size-char chunks."""
    paras = [p for p in re.split(r"\n{1,}", s) if p.strip()]
    out, cur = [], ""
    for p in paras:
        while len(p) > size:
            out.append(p[:size]); p = p[size:]
        if len(cur) + len(p) + 1 > size and cur:
            out.append(cur); cur = p
        else:
            cur = (cur + "\n" + p) if cur else p
    if cur:
        out.append(cur)
    return [c for c in out if len(c.strip()) >= 80]


HEREDOC_RE = re.compile(r"<<\s*['\"]?(\w+)['\"]?\s*\n(.*?)\n\1\b", re.S)
ECHO_RE = re.compile(r"(?:echo|printf)\s+(?:-e\s+)?([\"'])(.{150,}?)\1", re.S)


def doc_content(row) -> str | None:
    if row["typed"] and len(row["typed"]) >= 100:
        return row["typed"]
    c = row["command"]
    if c and len(c) >= 200:
        parts = [m.group(2) for m in HEREDOC_RE.finditer(c)] + [m.group(2) for m in ECHO_RE.finditer(c)]
        txt = "\n".join(parts)
        if len(txt) >= 150:
            return txt
        if "python" in c and ("%" in c or "forecast" in c.lower()):
            return c
    return None


def compute_switch_on(goal, cu, win0, win_end, present, names, pats, st):
    """The card's switch-on rule for every present agent (shared with analysis/confirm.py)."""
    it = (pl.read_parquet(OUT / "intentions.parquet").join(pl.read_parquet(OUT / "intentions_text.parquet"), on="event_index")
          .filter(pl.col("t") >= win0 - dt.timedelta(hours=1), pl.col("t") < win_end, pl.col("agent").is_in(present))
          .sort("t"))
    cu = cu.filter(pl.col("agent").is_in(present))
    rec_rows = []
    for x in cu.filter(pl.col("reasoning").is_not_null()).iter_rows(named=True):
        for sent in re.split(r"(?<=[.!?\n])\s+", x["reasoning"]):
            if not record_reads(sent):
                continue
            hits = [b for b in present if b != x["agent"] and pats[b].search(sent)]
            if hits:
                rec_rows.append({"agent": x["agent"], "t": x["t"], "whose": hits[0]})
                break
    rec = pl.DataFrame(rec_rows, schema={"agent": pl.Int8, "t": pl.Datetime("us", "UTC"), "whose": pl.Int8})

    chat = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "speaker_kind", "agent"]) \
             .with_row_index("msg").filter(pl.col("goal_no") == goal)
    ctext = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"])
    chat = chat.join(ctext, on="message_id", how="left")
    numchat = chat.filter(pl.col("speaker_kind") == "agent", pl.col("text").str.count_matches(PCT_RE.pattern) >= 1)
    expo = pl.read_parquet(OUT / "exposure.parquet").join(numchat.select("msg", "t", pl.col("agent").alias("src")), on="msg") \
             .filter(pl.col("agent") != pl.col("src")) \
             .with_columns((pl.col("t") + pl.duration(seconds=pl.col("lag_s"))).alias("t_seen"))
    sw = []
    for a in present:
        ia = it.filter(pl.col("agent") == a)
        cand = ia.filter(pl.Series([intention_reads(x) for x in ia["goal_text"].to_list()], dtype=pl.Boolean))
        ra = rec.filter(pl.col("agent") == a)
        tau_int = tau_rec = tau = None
        rule = "none"
        for c in cand.iter_rows(named=True):
            after = ra.filter(pl.col("t") >= c["t"], pl.col("t") <= c["t"] + dt.timedelta(minutes=CONFIRM_MIN))
            if after.height:
                tau_int, tau_rec, tau, rule = c["t"], after["t"][0], c["t"], "intent+record"
                break
        if tau is None and cand.height:
            tau_int = cand["t"][0]
            later = ra.filter(pl.col("t") >= tau_int)
            if later.height:
                tau_rec = tau = later["t"][0]; rule = "record-after-intent"
        first_seen = expo.filter(pl.col("agent") == a)["t_seen"].min() if expo.filter(pl.col("agent") == a).height else None
        first_stmt = st.filter(pl.col("agent") == a)["t"].min()
        joined_late = first_stmt > win0 + dt.timedelta(days=1)
        if joined_late:
            role = "late-joiner"
        elif tau is None:
            role = "uncoupled-docs"
        elif tau < win0 + dt.timedelta(hours=6):
            role = "switched"
        else:
            role = "switched-late"
        sw.append({"agent": a, "name": names[a], "tau_intent": tau_int, "tau_record": tau_rec, "tau": tau, "rule": rule,
                   "first_numeric_chat_seen": first_seen, "first_statement": first_stmt, "role": role,
                   "tau_offset_min": None if tau is None else (tau - win0).total_seconds() / 60})
    sw = pl.DataFrame(sw)
    return sw


def main():
    t0 = time.time()
    DEST.mkdir(parents=True, exist_ok=True)
    roster = pl.read_parquet(OUT / "roster.parquet")
    names = dict(zip(roster["agent"].to_list(), roster["name"].to_list()))
    pats = mention_regexes([{"id": a, "name": n} for a, n in zip(roster["agent"].to_list(), roster["name"].to_list())])
    cal = pl.read_parquet(OUT / "calendar.parquet").filter(pl.col("goal_no") == GOAL).sort("pt_date")
    assert not any(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())), "G21 must be non-holdout"
    win0 = cal["win_start"][0]
    days = cal["pt_date"].to_list()

    st = pl.read_parquet(OUT / "embeddings/statements.parquet").filter(pl.col("goal_no") == GOAL)
    st = st.join(roster.select("agent", "claude_code"), on="agent").filter(~pl.col("claude_code")).drop("claude_code")
    present = sorted(st["agent"].unique().to_list())
    print("present:", [names[a] for a in present], flush=True)

    # ---------------- switch-on ----------------
    cu = pl.read_parquet(DEST / "cu_turns_text.parquet").filter(pl.col("agent").is_in(present))
    sw = compute_switch_on(GOAL, cu, win0, cal["win_end"][-1], present, names, pats, st)
    chat = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "speaker_kind", "agent"]) \
             .filter(pl.col("goal_no") == GOAL)
    ctext = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"])
    sw.write_parquet(DEST / "switch_on.parquet")
    print(sw.select("name", "tau_intent", "tau_record", "rule", "role", "tau_offset_min", "first_numeric_chat_seen"), flush=True)

    # ---------------- statements ----------------
    itext = pl.read_parquet(OUT / "intentions_text.parquet", columns=["event_index", "goal_text"])
    iidx = pl.read_parquet(OUT / "embeddings/intentions_index.parquet").with_row_index("src_row")
    cidx = pl.read_parquet(OUT / "embeddings/chat_index.parquet").with_row_index("src_row")
    stc = st.filter(pl.col("kind") == "chat").join(cidx, on="src_row").join(ctext, on="message_id", how="left")
    sti = st.filter(pl.col("kind") == "intent").join(iidx, on="src_row").join(itext, on="event_index", how="left") \
            .rename({"goal_text": "text"})
    cols = ["kind", "src_row", "agent", "t", "pt_date", "win30", "text"]
    S = pl.concat([stc.select(cols), sti.select(cols)]).sort("t")
    txt = S["text"].fill_null("").to_list()
    ag = S["agent"].to_list()
    S = S.with_columns(
        pl.Series("n_pct", [len(PCT_RE.findall(s)) for s in txt], dtype=pl.Int16),
        pl.Series("forecast", [bool(FORECAST_RE.search(s)) for s in txt]),
        pl.Series("comparison", [bool(COMPARISON_RE.search(s)) for s in txt]),
        pl.Series("names_other", [any(pats[b].search(s) for b in present if b != a) for s, a in zip(txt, ag)]),
        pl.Series("n_chars", [len(s) for s in txt], dtype=pl.Int32),
    ).join(sw.select("agent", "tau"), on="agent", how="left")
    S = S.with_columns(pl.when(pl.col("tau").is_null()).then(pl.lit("none"))
                       .when(pl.col("t") < pl.col("tau")).then(pl.lit("pre")).otherwise(pl.lit("post")).alias("seg"),
                       ((pl.col("t") - win0).dt.total_seconds() / 60).alias("min_from_open"))
    Ec = np.load(OUT / "embeddings/chat_bge_small.npy", mmap_mode="r")
    Ei = np.load(OUT / "embeddings/intentions_bge_small.npy", mmap_mode="r")
    kind = S["kind"].to_numpy(); src = S["src_row"].to_numpy()
    E = np.empty((S.height, 384), dtype=np.float32)
    m = kind == "chat"
    E[m] = Ec[src[m]]; E[~m] = Ei[src[~m]]
    W = load_whitener("I", DIM)
    np.save(DEST / "stmt_w64.npy", W(E).astype(np.float16))
    S.drop("text").write_parquet(DEST / "statements.parquet", compression="zstd")
    print(f"statements: {S.height}", flush=True)

    # ---------------- document chunks ----------------
    docs, dtexts = [], []
    for x in cu.sort("t").iter_rows(named=True):
        c = doc_content(x)
        if not c:
            continue
        for k, ch in enumerate(chunk_text(c)):
            docs.append({"agent": x["agent"], "t": x["t"], "session_id": x["session_id"], "source": "type" if x["typed"] else "bash",
                         "part": k, "n_chars": len(ch), "n_pct": len(PCT_RE.findall(ch)),
                         "names_other": any(pats[b].search(ch) for b in present if b != x["agent"]),
                         "comparison": bool(COMPARISON_RE.search(ch)), "forecast": bool(FORECAST_RE.search(ch))})
            dtexts.append(ch)
    D = pl.DataFrame(docs).join(sw.select("agent", "tau"), on="agent", how="left")
    D = D.with_columns(pl.when(pl.col("tau").is_null()).then(pl.lit("none"))
                       .when(pl.col("t") < pl.col("tau")).then(pl.lit("pre")).otherwise(pl.lit("post")).alias("seg"),
                       ((pl.col("t") - win0).dt.total_seconds() / 60).alias("min_from_open"),
                       pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    print(f"doc chunks: {D.height}; embedding ...", flush=True)
    Ed = embed(dtexts)
    np.save(DEST / "docs_w64.npy", W(Ed).astype(np.float16))
    D.write_parquet(DEST / "docs.parquet", compression="zstd")

    # ---------------- numeric forecasts ----------------
    nums = []
    def add(rows, t, speaker, source, ref):
        for r in rows:
            nums.append({"t": t, "speaker": speaker, "source": source, "ref": ref, **r})
    S_txt = dict(zip(zip(S["kind"].to_list(), S["src_row"].to_list()), txt))
    pnames = [names[b] for b in present]
    for strict in (False, True):
        for x in S.filter(pl.col("n_pct") > 0).iter_rows(named=True):
            other = [pats[b] for b in present if b != x["agent"]]
            if strict:
                other = other + loose_other_pats(names[x["agent"]], pnames)
            rows = [dict(r, extractor="A1" if strict else "prereg") for r in extract_numbers(S_txt[(x["kind"], x["src_row"])], other, strict)]
            add(rows, x["t"], x["agent"], x["kind"], int(x["src_row"]))
        for i, x in enumerate(D.iter_rows(named=True)):
            if x["n_pct"] == 0:
                continue
            other = [pats[b] for b in present if b != x["agent"]]
            if strict:
                other = other + loose_other_pats(names[x["agent"]], pnames)
            rows = [dict(r, extractor="A1" if strict else "prereg") for r in extract_numbers(dtexts[i], other, strict)]
            add(rows, x["t"], x["agent"], "doc", i)
    N = pl.DataFrame(nums).join(sw.select(pl.col("agent").alias("speaker"), "tau"), on="speaker", how="left") \
          .with_columns(pl.when(pl.col("tau").is_null()).then(pl.lit("none"))
                        .when(pl.col("t") < pl.col("tau")).then(pl.lit("pre")).otherwise(pl.lit("post")).alias("seg"),
                        pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    N.write_parquet(DEST / "numeric.parquet", compression="zstd")
    print(f"numeric: {N.height} values; self-attributed {N.filter(pl.col('attribution') == 'self').group_by('extractor').len().to_dicts()}", flush=True)

    # ---------------- goal direction ----------------
    g = [x for x in load_goals() if x["goal_no"] == GOAL][0]
    hum = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "speaker_kind"]) \
            .filter(pl.col("speaker_kind") == "human", pl.col("t") >= win0 - dt.timedelta(minutes=10),
                    pl.col("t") <= win0 + dt.timedelta(minutes=45)).join(ctext, on="message_id")
    kick = [s for s in hum["text"].to_list() if len(s) >= 250]
    sents = [s for k in kick for s in re.split(r"(?<=[.!?])\s+", k)
             if not re.search(r"(?i)(substack|blogosphere|previous goal|last two weeks|analytics|git repo|archived)", s)]
    kick_txt = " ".join(sents)
    Eg = embed([g["goal"], kick_txt])
    Wg = W(Eg)
    ghat = unit(unit(Wg[0]) + unit(Wg[1]))
    np.savez(DEST / "goal_vec.npz", ghat=ghat.astype(np.float32), goal=unit(Wg[0]).astype(np.float32),
             kickoff=unit(Wg[1]).astype(np.float32), n_kick_chars=len(kick_txt))

    prov = {"built_by": "hypotheses/H24-forecast-coupling-switch/scheme/build.py (+ scheme/extract_cu_text.py)",
            "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["computer_use_turns", "computer_use_sessions", "chat_messages", "events", "village_goals"]},
                       {"source": "data/processed/shared", "tables": ["statements", "chat_core", "chat_text", "intentions",
                                                                       "intentions_text", "exposure", "calendar", "roster",
                                                                       "embeddings/*_bge_small.npy", "whitening_I.npz"]}],
            "params": {"goal_no": GOAL, "whitening": f"regime I, {DIM} dims (first 32 = primary)", "confirm_min": CONFIRM_MIN,
                       "doc_chunk_chars": 1000, "embedding": "BAAI/bge-small-en-v1.5 (docs and goal embedded here, CPU, 2 threads)"},
            "built_at": dt.datetime.now(UTC).isoformat()}
    (H24 / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
