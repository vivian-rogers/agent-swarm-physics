"""H109 scheme: statements, erasure boundaries and post-erasure reads for the scoped regime-III multi-room periods.

Output: data/processed/H109-erasure-demagnetizing-pulse/
  statements.parquet   regime-III main chat statements, non-holdout (all periods: needed for day means and the
                       leave-period-out agent constants), with srow (DQ5 row), msg, agent, t, pt_date, goal_no, unit_id,
                       room, scoped (in a scoped unit and one of its two rooms), restate, copy, producing call
                       (turn_id_prod, t_call_prod), cumulative reset counters at the producing call (cf, cv, cs) and the
                       first call of the producing call's segment (t_seg0)
  boundaries.parquet   per dedupe variant (none / restate / copy): consecutive scoped statements k, k+1 of one agent on
                       one PT day with different producing calls; label F / V / W / O; gap_s; pre and post window rows
                       (up to 3 statements each, same segment, same day) as lists of statement-table row ids
  reads.parquet        per F or V event (variant, boundary id) and post statement k = 1..10 of the post segment:
                       R_k (agent ledger items received from the segment's first call through the producing call) and
                       U_k (agent messages by others posted in the statement's room in (t_call_prod, t_call_prod + L],
                       L = t_call_prod - t_seg0: posted-unread of equal duration)
No text is read or written. Held-out rows are dropped with holdout_mask and the table flags (asserted).

Usage: uv run python hypotheses/H109-erasure-demagnetizing-pulse/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
import datetime as dt  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H109-erasure-demagnetizing-pulse"
EXCLUDE = {19, 28, 30}
# scoped units and their two rooms (A first: +1; B second: -1)
UNIT_ROOMS = {u: (2, 3) for u in ["36b", "36c", "37", "38a", "38b", "38c", "38d", "38e", "39", "41", "42a", "42b",
                                  "44a", "44b"]}
UNIT_ROOMS["51g"] = (0, 15)
GOAL_OF_UNIT = {u: int("".join(c for c in u if c.isdigit())) for u in UNIT_ROOMS}
WIN = 3
KMAX = 10
VARIANTS = ("none", "restate", "copy")


def load_statements(include_holdout: bool = False) -> pl.DataFrame:
    """include_holdout: only for the guarded analysis/confirm.py (in memory, never written)."""
    sm = pl.read_parquet(SH / "style_messages.parquet",
                         columns=["message_id", "msg", "srow", "agent", "t", "pt_date", "goal_no", "unit_id", "regime",
                                  "room", "holdout", "main", "copy", "restate"])
    sm = sm.filter(pl.col("main") & (pl.col("regime") == "III") & ~pl.col("agent").is_in(list(EXCLUDE)))
    hm = np.array(holdout_mask(sm["pt_date"].to_list(), sm["goal_no"].to_list()))
    sm = sm.with_columns(pl.Series("hm", hm))
    if not include_holdout:
        sm = sm.filter(~pl.col("hm") & ~pl.col("holdout"))
        assert not sm["hm"].any() and not sm["holdout"].any()
    pc = pl.read_parquet(SH / "producing_calls.parquet", columns=["message_id", "turn_id_prod", "t_call_prod"])
    sm = sm.join(pc, on="message_id", how="left").filter(pl.col("turn_id_prod").is_not_null())
    return sm


def ledger_counters(include_holdout: bool = False) -> pl.DataFrame:
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter((pl.col("regime") == "III") & (pl.lit(include_holdout) | ~pl.col("holdout")))
          .select("turn_id", "agent", "pt_date", "t_call", "n_agent", "reset_forced", "reset_consol", "reset_session")
          .collect().sort("agent", "t_call", "turn_id"))
    ct = ct.with_columns(
        pl.col("reset_forced").cast(pl.Int32).cum_sum().over("agent").alias("cf"),
        (pl.col("reset_consol") & ~pl.col("reset_forced")).cast(pl.Int32).cum_sum().over("agent").alias("cv"),
        (pl.col("reset_session") & ~pl.col("reset_consol")).cast(pl.Int32).cum_sum().over("agent").alias("cs"))
    ct = ct.with_columns((pl.col("cf") + pl.col("cv") + pl.col("cs")).alias("seg"))
    seg0 = ct.group_by("agent", "seg").agg(pl.col("t_call").min().alias("t_seg0"))
    ct = ct.join(seg0, on=["agent", "seg"], how="left")
    ct = ct.with_columns(pl.col("n_agent").cast(pl.Int64).cum_sum().over("agent").alias("cum_items"))
    return ct


def build_statements(include_holdout: bool = False):
    sm = load_statements(include_holdout)
    ct = ledger_counters(include_holdout)
    sm = sm.join(ct.select(pl.col("turn_id").alias("turn_id_prod"), "cf", "cv", "cs", "seg", "t_seg0", "cum_items"),
                 on="turn_id_prod", how="left").filter(pl.col("cf").is_not_null())
    ur = pl.DataFrame({"unit_id": list(UNIT_ROOMS), "roomA": [v[0] for v in UNIT_ROOMS.values()],
                       "roomB": [v[1] for v in UNIT_ROOMS.values()]})
    sm = sm.join(ur, on="unit_id", how="left")
    sm = sm.with_columns(((pl.col("room") == pl.col("roomA")) | (pl.col("room") == pl.col("roomB"))).fill_null(False)
                         .alias("scoped"),
                         pl.when(pl.col("room") == pl.col("roomA")).then(1).when(pl.col("room") == pl.col("roomB"))
                         .then(-1).otherwise(0).cast(pl.Int8).alias("sigma"))
    sm = sm.sort("agent", "t", "msg").with_row_index("sid")
    return sm, ct


def boundaries(sm: pl.DataFrame, variant: str) -> pl.DataFrame:
    s = sm.filter(pl.col("scoped"))
    if variant != "none":
        s = s.filter(~pl.col(variant))
    s = s.sort("agent", "t", "msg")
    rows = []
    for (agent, day), g in s.group_by(["agent", "pt_date"], maintain_order=True):
        sid = g["sid"].to_numpy()
        cf, cv, cs, seg = (g[c].to_numpy() for c in ("cf", "cv", "cs", "seg"))
        tp = g["turn_id_prod"].to_numpy()
        tt = g["t"].dt.epoch("us").to_numpy()
        n = len(sid)
        for k in range(n - 1):
            if tp[k] == tp[k + 1]:
                continue
            df_, dv, ds = cf[k + 1] - cf[k], cv[k + 1] - cv[k], cs[k + 1] - cs[k]
            lab = ("W" if (df_, dv, ds) == (0, 0, 0) else "F" if (df_, dv, ds) == (1, 0, 0)
                   else "V" if (df_, dv, ds) == (0, 1, 0) else "O")
            pre = [j for j in range(max(0, k - WIN + 1), k + 1) if seg[j] == seg[k]]
            post = [j for j in range(k + 1, min(n, k + 1 + WIN)) if seg[j] == seg[k + 1]]
            postk = [j for j in range(k + 1, min(n, k + 1 + KMAX)) if seg[j] == seg[k + 1]]
            rows.append({"agent": agent, "pt_date": day, "k_sid": int(sid[k]), "k1_sid": int(sid[k + 1]), "label": lab,
                         "gap_s": (tt[k + 1] - tt[k]) / 1e6, "pre": [int(sid[j]) for j in pre],
                         "post": [int(sid[j]) for j in post], "postk": [int(sid[j]) for j in postk]})
    b = pl.DataFrame(rows, schema={"agent": pl.Int8, "pt_date": pl.Utf8, "k_sid": pl.UInt32, "k1_sid": pl.UInt32,
                                   "label": pl.Utf8, "gap_s": pl.Float64, "pre": pl.List(pl.UInt32),
                                   "post": pl.List(pl.UInt32), "postk": pl.List(pl.UInt32)})
    return b.with_columns(pl.lit(variant).alias("variant")).with_row_index("bid")


def reads(sm: pl.DataFrame, b: pl.DataFrame, ct: pl.DataFrame, chat: pl.DataFrame) -> pl.DataFrame:
    """R_k and U_k for the post statements (k = 1..10) of F and V events."""
    ev = b.filter(pl.col("label").is_in(["F", "V"])).select("variant", "bid", "agent", "postk").explode("postk") \
        .rename({"postk": "sid"}).with_columns(pl.int_range(1, pl.len() + 1).over("variant", "bid").alias("k"))
    st = sm.select("sid", "agent", "room", "t", "t_call_prod", "t_seg0", "cum_items", "seg")
    ev = ev.join(st.drop("agent"), on="sid", how="left")
    # items received from the segment's first call through the producing call = cum_items(prod) - cum_items(before seg0)
    first = ct.sort("agent", "t_call", "turn_id").group_by("agent", "seg").agg(
        (pl.col("cum_items").first() - pl.col("n_agent").first().cast(pl.Int64)).alias("cum_before"))
    ev = ev.join(first, on=["agent", "seg"], how="left")
    ev = ev.with_columns((pl.col("cum_items") - pl.col("cum_before")).alias("R"))
    # posted-unread of equal duration
    L = (ev["t_call_prod"] - ev["t_seg0"]).dt.total_microseconds().to_numpy()
    t0 = ev["t_call_prod"].dt.epoch("us").to_numpy()
    U = np.zeros(ev.height, np.int32)
    ag, rm = ev["agent"].to_numpy(), ev["room"].to_numpy()
    for r in np.unique(rm):
        c = chat.filter(pl.col("room") == r)
        tc = c["t"].dt.epoch("us").to_numpy()
        ac = c["agent"].to_numpy()
        o = np.argsort(tc)
        tc, ac = tc[o], ac[o]
        ix = np.where(rm == r)[0]
        for i in ix:
            lo, hi = np.searchsorted(tc, t0[i], "right"), np.searchsorted(tc, t0[i] + max(L[i], 0), "right")
            U[i] = int(np.sum(ac[lo:hi] != ag[i]))
    return ev.with_columns(pl.Series("U", U)).select("variant", "bid", "k", "sid", "R", "U")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sm, ct = build_statements()
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["t", "pt_date", "goal_no", "room", "speaker_kind", "agent"])
            .filter((pl.col("speaker_kind") == "agent") & (pl.col("goal_no") >= 36)))
    chat = chat.filter(~pl.Series(holdout_mask(chat["pt_date"].to_list(), chat["goal_no"].to_list())))
    bs, rs = [], []
    for v in VARIANTS:
        b = boundaries(sm, v)
        bs.append(b)
        rs.append(reads(sm, b, ct, chat))
    B = pl.concat(bs)
    R = pl.concat(rs)
    sm.drop("hm", "message_id").write_parquet(OUT / "statements.parquet", compression="zstd")
    B.write_parquet(OUT / "boundaries.parquet", compression="zstd")
    R.write_parquet(OUT / "reads.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H109-erasure-demagnetizing-pulse/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["style_messages", "producing_calls", "context_ledger_turns", "chat_core"]}],
            "params": {"units": UNIT_ROOMS, "win": WIN, "kmax": KMAX, "variants": VARIANTS, "exclude": sorted(EXCLUDE)},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print("statements", sm.height, "scoped", int(sm["scoped"].sum()))
    print(B.group_by("variant", "label").len().sort("variant", "label"))


if __name__ == "__main__":
    main()
