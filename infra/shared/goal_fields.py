"""Shared goal fields: bge-small embeddings of every village goal text, its kickoff message(s), and the per-agent
assigned goals (#51 era). Moved here from H01 (scheme/build.py: goal_texts, embed_goal_texts) and H10
(scheme/build.py: goal_texts, embed), which duplicated the same rule.

Rule (H01 = H10):
  first_day   the goal period's first active PT day (calendar). No goal period has a held-out first day followed by
              non-holdout days, so this equals H01/H10's "first non-holdout day" wherever that exists.
  kickoff     human messages (speaker_kind == human; the `automated` bot excluded) of >= 250 chars posted within
              [win_start - 10 min, win_start + 45 min] of first_day's empirical window; fallback: that day's longest
              human message >= 250 chars (flag `fallback`). Sentences about the previous goal are stripped
              (BOILER regex); the body is cut into <= 700-char sentence chunks; the vector is the mean of the unit
              chunk embeddings (not re-normalized).
Kinds (one row each; `gid` = row of goal_vectors.npy):
  goal          village_goals text, chunked as above (H10's goal_raw)
  goal_whole    village_goals text embedded as one string, truncated at 256 tokens (H01's "goal" rows)
  kickoff       all rooms combined (H10's kick_raw)
  kickoff_room  one row per room that has kickoff messages (H01's "kickoff" rows)
  agent_goal    raw agent_goals: name + ". " + description; agent, valid_from / valid_to (H01's "agent_goal" rows);
                `ref` = the raw agent_goals id (join raw for the text; no text is stored here)
All goal periods are included; `holdout` flags rows whose anchor day is in the locked holdout (measurement only:
exploration must filter holdout == False). No text is written anywhere.

Outputs (data/processed/shared/embeddings/):
  goals.parquet      gid, goal_no, kind, room, agent, first_day, win_start, valid_from, valid_to, regime, holdout,
                     n_msgs, n_rooms, n_chunks, n_chars, fallback, ref
  goal_vectors.npy   (n, 384) float16 raw bge-small (BAAI/bge-small-en-v1.5, max_seq_length 256), mean of unit chunk
                     embeddings; whiten downstream with common.load_whitener(regime) and unit-normalize.

Usage:  UV_OFFLINE=1 HF_HUB_OFFLINE=1 uv run --with sentence-transformers python infra/shared/goal_fields.py
        uv run python infra/shared/goal_fields.py --verify     (compare with H01's and H10's vectors; read-only)
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import datetime as dt  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, GoalLookup, holdout_mask, load_goals, parse_ts, rows, write_provenance  # noqa: E402

ED = OUT / "embeddings"
MODEL = "BAAI/bge-small-en-v1.5"
MAX_SEQ = 256
KICK_MIN_CHARS = 250
KICK_BEFORE_MIN = 10
KICK_AFTER_MIN = 45
CHUNK_CHARS = 700

BOILER = re.compile(r"wrap(s|ped)?\s+up|to a close|your memory|previous goal|last week|last two weeks|that goal is", re.I)


def strip_boilerplate(text: str) -> str:
    sents = re.split(r"(?<=[.!?])\s+|\n+", text)
    return " ".join(s for s in sents if s.strip() and not BOILER.search(s)).strip()


def chunks(text: str, n: int = CHUNK_CHARS) -> list[str]:
    sents = re.split(r"(?<=[.!?])\s+", text)
    out, cur = [], ""
    for s in sents:
        if len(cur) + len(s) > n and cur:
            out.append(cur)
            cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        out.append(cur)
    return [c[:2000] for c in out if len(c) > 20]


def kickoff_messages(cal: pl.DataFrame, chat: pl.DataFrame, d0: str):
    """Human kickoff messages on day d0 (message_id, t, room, length) and whether the fallback was used."""
    ws = cal.filter(pl.col("pt_date") == d0)["win_start"][0]
    k = chat.filter((pl.col("pt_date") == d0) & (pl.col("length") >= KICK_MIN_CHARS)
                    & (pl.col("t") >= ws - dt.timedelta(minutes=KICK_BEFORE_MIN))
                    & (pl.col("t") <= ws + dt.timedelta(minutes=KICK_AFTER_MIN)))
    fallback = False
    if k.height == 0:
        k = chat.filter((pl.col("pt_date") == d0) & (pl.col("length") >= KICK_MIN_CHARS)).sort("length", descending=True).head(1)
        fallback = k.height > 0
    return k, fallback, ws


def goal_texts() -> tuple[list[dict], list[list[str]]]:
    """(meta rows, text chunks per row). Text stays in memory only."""
    goals = {g["goal_no"]: g for g in load_goals()}
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "win_start", "goal_no", "regime", "holdout"]) \
            .with_columns(pl.col("regime").cast(pl.String))
    first = cal.filter(pl.col("goal_no") > 0).sort("pt_date").group_by("goal_no", maintain_order=True).first().sort("goal_no")
    chat = (pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "length"])
            .filter(pl.col("speaker_kind").cast(pl.String) == "human"))
    text = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"])
    meta, texts = [], []
    base = {"room": None, "agent": None, "valid_from": None, "valid_to": None, "n_msgs": 0, "n_rooms": 0, "fallback": False,
            "ref": None}
    for d0, ws, g, reg, ho in first.select("pt_date", "win_start", "goal_no", "regime", "holdout").iter_rows():
        g = int(g)
        common = {**base, "goal_no": g, "first_day": d0, "win_start": ws, "regime": reg, "holdout": bool(ho)}
        gt = goals[g]["goal"]
        meta.append({**common, "kind": "goal"}); texts.append(chunks(gt) or [gt])
        meta.append({**common, "kind": "goal_whole"}); texts.append([gt])
        k, fallback, _ = kickoff_messages(cal, chat, d0)
        k = k.join(text, on="message_id").sort("t")
        if k.height == 0:
            continue
        body = " ".join(strip_boilerplate(x) for x in k["text"].to_list())
        ch = chunks(body)
        if ch:
            meta.append({**common, "kind": "kickoff", "n_msgs": k.height, "n_rooms": k["room"].n_unique(), "fallback": fallback})
            texts.append(ch)
        for (room,), grp in k.group_by(["room"], maintain_order=True):
            body = " ".join(strip_boilerplate(x) for x in grp.sort("t")["text"].to_list())
            ch = chunks(body)
            if ch:
                meta.append({**common, "kind": "kickoff_room", "room": int(room), "n_msgs": grp.height, "n_rooms": 1,
                             "fallback": fallback})
                texts.append(ch)
    # per-agent assigned goals (#51 era)
    roster = {r["agent_id"]: r["agent"] for r in pl.read_parquet(OUT / "roster.parquet").iter_rows(named=True)}
    G = GoalLookup()
    h_first = {r[0]: r for r in first.select("goal_no", "pt_date", "win_start", "regime").iter_rows()}
    for a in sorted(rows("agent_goals"), key=lambda r: (r.get("start_time") or "", r["id"])):
        if a["agent_id"] not in roster:
            continue
        txt = a["name"] + ("" if a.get("description") in (None, "None") else ". " + a["description"])
        st = a.get("start_time") if a.get("start_time") not in (None, "None") else None
        en = a.get("end_time") if a.get("end_time") not in (None, "None") else None
        g = G(parse_ts(st)) if st else 51
        vf = st[:10] if st else None
        meta.append({**base, "goal_no": int(g), "kind": "agent_goal", "agent": int(roster[a["agent_id"]]),
                     "valid_from": vf, "valid_to": en[:10] if en else None, "first_day": h_first[g][1],
                     "win_start": h_first[g][2], "regime": h_first[g][3],
                     "holdout": bool(holdout_mask([vf or h_first[g][1]], [g])[0]), "ref": a["id"]})
        texts.append([txt])
    return meta, texts


def embed(texts: list[list[str]]) -> tuple[np.ndarray, str]:
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(2)
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    m = SentenceTransformer(MODEL, device=dev)
    m.max_seq_length = MAX_SEQ
    out = np.zeros((len(texts), 384), dtype=np.float32)
    for i, ch in enumerate(texts):
        out[i] = m.encode(ch, batch_size=32, normalize_embeddings=True, convert_to_numpy=True).mean(0)
    return out, dev


def main():
    t0 = time.time()
    meta, texts = goal_texts()
    V, dev = embed(texts)
    df = pl.DataFrame(meta, schema={"goal_no": pl.Int8, "kind": pl.String, "room": pl.Int8, "agent": pl.Int8,
                                    "first_day": pl.String, "win_start": pl.Datetime("us", "UTC"), "valid_from": pl.String,
                                    "valid_to": pl.String, "regime": pl.String, "holdout": pl.Boolean, "n_msgs": pl.Int16,
                                    "n_rooms": pl.Int8, "fallback": pl.Boolean, "ref": pl.String})
    df = df.with_columns(pl.Series("n_chunks", [len(t) for t in texts], dtype=pl.Int16),
                         pl.Series("n_chars", [sum(len(c) for c in t) for t in texts], dtype=pl.Int32))
    df = df.with_row_index("gid").with_columns(pl.col("gid").cast(pl.Int32), pl.col("kind").cast(pl.Categorical))
    del texts
    df = df.select("gid", "goal_no", "kind", "room", "agent", "first_day", "win_start", "valid_from", "valid_to", "regime",
                   "holdout", "n_msgs", "n_rooms", "n_chunks", "n_chars", "fallback", "ref")
    ED.mkdir(exist_ok=True)
    df.write_parquet(ED / "goals.parquet", compression="zstd")
    np.save(ED / "goal_vectors.npy", V.astype(np.float16))
    print(df.group_by("kind").agg(pl.len(), pl.col("holdout").sum().alias("holdout")).sort("kind"))
    print(f"goal_fields: {df.height} rows; no kickoff for goals "
          f"{sorted(set(df['goal_no'].to_list()) - set(df.filter(pl.col('kind') == 'kickoff')['goal_no'].to_list()))}; "
          f"device {dev}; {time.time() - t0:.0f}s")
    write_provenance("goal_fields", ["village_goals", "agent_goals", "chat_core", "chat_text (kickoff texts, in memory only)",
                                     "calendar", "roster"],
                     {"model": MODEL, "max_seq_length": MAX_SEQ, "device": dev, "dtype": "float16", "normalized": "chunks unit, mean not renormalized",
                      "kickoff_rule": f"human msgs >= {KICK_MIN_CHARS} chars within [win_start-{KICK_BEFORE_MIN}m, win_start+{KICK_AFTER_MIN}m] "
                                      "of the goal's first active day; fallback longest >= 250 that day; previous-goal boilerplate stripped; "
                                      f"chunks <= {CHUNK_CHARS} chars, mean of unit chunk embeddings",
                      "sources": "H01 scheme/build.py goal_texts (goal_whole, kickoff_room, agent_goal); H10 scheme/build.py (goal, kickoff)",
                      "holdout": "all goals included; holdout flag = anchor day in locked holdout"})


# ----------------------------------------------------------------------------- verification (read-only)
def verify():
    df = pl.read_parquet(ED / "goals.parquet")
    V = np.load(ED / "goal_vectors.npy").astype(np.float32)

    def cmp(a, b):
        cos = float((a @ b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        return float(np.abs(a - b).max()), cos

    res = {}
    h01 = ROOT / "data/processed/H01-emergent-superagents-exist"
    gm = pl.read_parquet(h01 / "goals.parquet").unique(["gid"]).sort("gid")
    G1 = np.load(h01 / "goals_raw.npy")
    out = []
    for r in gm.iter_rows(named=True):
        kind = {"goal": "goal_whole", "kickoff": "kickoff_room", "agent_goal": "agent_goal"}[r["kind"]]
        q = df.filter((pl.col("goal_no") == r["goal_no"]) & (pl.col("kind").cast(pl.String) == kind))
        if kind == "kickoff_room":
            q = q.filter(pl.col("room") == r["room"])
        if kind == "agent_goal":
            q = q.filter((pl.col("agent") == r["agent"]) & (pl.col("valid_from") == r["valid_from"]))
            if q.height > 1:  # same agent, same start: match on vector
                q = q.with_columns(pl.Series("d", [float(np.abs(V[i] - G1[r["gid"]]).max()) for i in q["gid"].to_list()])).sort("d").head(1)
        if q.height != 1:
            out.append((r["kind"], r["goal_no"], None, None)); continue
        out.append((r["kind"], r["goal_no"], *cmp(V[q["gid"][0]], G1[r["gid"]])))
    miss = [o for o in out if o[2] is None]
    ok = [o for o in out if o[2] is not None and o[3] > 0.9999]
    bad = [o for o in out if o[2] is not None and o[3] <= 0.9999]
    # a mismatching H01 row: does its vector equal some OTHER shared row of the same goal (a permuted row)?
    perm = []
    for kind, g, _, _ in bad:
        r = gm.filter((pl.col("goal_no") == g) & (pl.col("kind") == kind))
        for row in r.iter_rows(named=True):
            sims = [(int(i), float(V[i] @ G1[row["gid"]] / np.linalg.norm(V[i]) / np.linalg.norm(G1[row["gid"]])))
                    for i in df.filter(pl.col("goal_no") == g)["gid"].to_list()]
            best = max(sims, key=lambda s: s[1])
            perm.append({"h01_row": (kind, g, row["room"]), "best_shared_gid": best[0],
                         "best_shared": df.filter(pl.col("gid") == best[0]).select("kind", "room").row(0), "cos": round(best[1], 6)})
    res["H01"] = {"rows": len(out), "unmatched": len(miss), "matched_fp16": len(ok),
                  "max_abs_diff_matched": max(o[2] for o in ok), "min_cos_matched": min(o[3] for o in ok),
                  "mismatched": [(o[0], o[1], round(o[3], 4)) for o in bad], "mismatch_best_match": perm}
    h10 = np.load(ROOT / "data/processed/H10-goals-are-legendre-pushes/goal_vecs.npz")
    out = []
    for g, gr, kr in zip(h10["goal_no"], h10["goal_raw"], h10["kick_raw"]):
        for kind, ref in (("goal", gr), ("kickoff", kr)):
            q = df.filter((pl.col("goal_no") == int(g)) & (pl.col("kind").cast(pl.String) == kind))
            if np.isnan(ref).all():
                out.append((kind, int(g), "nan_ref", q.height)); continue
            out.append((kind, int(g), *cmp(V[q["gid"][0]], ref)) if q.height == 1 else (kind, int(g), None, None))
    ok = [o for o in out if isinstance(o[2], float)]
    res["H10"] = {"rows": len(out), "nan_ref_rows": [(o[0], o[1], "shared rows:", o[3]) for o in out if o[2] == "nan_ref"],
                  "unmatched": [o[:2] for o in out if o[2] is None], "max_abs_diff": max(o[2] for o in ok),
                  "min_cos": min(o[3] for o in ok)}
    print(res)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
