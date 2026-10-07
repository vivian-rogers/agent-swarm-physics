"""H141 scheme: agent chat statements on the per-call clock, the reads of each call, and the text planes E built from
goal, kickoff and room-kickoff texts only (never from agent content). Codes, row ids and vectors of texts; no text.

    uv run python hypotheses/H141-easy-plane-anisotropy/scheme/build.py [--period G38 | --all]

Output (data/processed/H141-easy-plane-anisotropy/G<NN>/):
  statements.parquet  srow, message_id, agent, t, pt_date, room, unit_id, turn_id (producing call), t_call, n (agent-day
                      call index), nf / nc (forced / voluntary resets before the call, that day), half (split-half parity
                      within the agent-day, by time), plane (text-plane key of the statement: "P" in shared-goal periods;
                      "a<agent>" or "a40old" in #51)
  reads.parquet       reader, turn_id, t_call, n, nf, nc, sender, srow_m, t_post, room_m, pt_date, unit_id
  calls.parquet       agent, pt_date, turn_id, t_call, n, reset_forced, reset_consol, nf, nc, room, unit_id
  planes.npz          per model m in {bge_small, gte_modernbert}: whitened (regime III, 32-d) unit text vectors
                      "<m>|<key>" (keys: goal, kickoff, room2, room3, a<agent>) and the text-plane bases
                      "<m>|E|<plane>" (Gram-Schmidt, 32 x d_E)
  _provenance.json
Reserved days and periods are removed with calendar.holdout and common.holdout_mask (asserted twice).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
from embed_models import goal_vectors, load_whitener  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H141-easy-plane-anisotropy"
PERIODS = [37, 38, 39, 40, 41, 42, 44, 51]
ROOM_KICKOFF_PERIODS = {38, 44}          # card: room-kickoff axes enter E only where the rooms got different kickoffs
MODELS = ("bge_small", "gte_modernbert")
NE38_AGENT = 40
NE38_T = dt.datetime(2026, 7, 29, 16, 51, tzinfo=dt.timezone.utc)
NE38_OLD_GOAL_AGENT = 24                 # the game-dev role text Opus 5 held before 07-29 (H54 native.py)


def unitv(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def gram_schmidt(vs: list[np.ndarray], tol: float = 0.05) -> np.ndarray:
    """Orthonormal basis; a text vector whose residual norm is below tol (numerically a linear combination of the
    earlier ones, e.g. #44: the kickoff is the chunk mean of the two room kickoffs) adds no axis."""
    out = []
    for v in vs:
        w = v.copy()
        for q in out:
            w -= (w @ q) * q
        n = np.linalg.norm(w)
        if n > tol:
            out.append(w / n)
    return np.column_stack(out)


def days_for(goal: int) -> list[str]:
    cal = pl.read_parquet(SH / "calendar.parquet").filter((pl.col("goal_no") == goal) & (pl.col("n_agent_events") > 0)
                                                          & ~pl.col("holdout"))
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.filter(~pl.Series(hm))
    assert not any(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    return sorted(cal["pt_date"].to_list())


def unit_of(goal: int, days: list[str]) -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet").filter((pl.col("goal_no") == goal) & ~pl.col("holdout"))
    rows = [(d, r["unit_id"], r["start"]) for r in pu.iter_rows(named=True) for d in r["days"]]
    df = pl.DataFrame(rows, schema={"pt_date": pl.String, "unit_id": pl.String, "ustart": pl.Datetime("us", "UTC")},
                      orient="row")
    df = df.sort("ustart").group_by("pt_date").agg(pl.col("unit_id").last())
    return df.filter(pl.col("pt_date").is_in(days))


def text_vectors(goal: int) -> dict:
    """Whitened (regime III) unit text vectors and plane bases, per model. Texts only."""
    g = pl.read_parquet(SH / "embeddings/goals.parquet").filter(pl.col("goal_no") == goal)
    assert not g["holdout"].any()
    out = {}
    for m in MODELS:
        GV = goal_vectors(m).astype(np.float64)
        W = load_whitener("III", 32, m)
        vec = lambda gid: unitv(W(GV[gid][None, :])[0].astype(np.float64))  # noqa: E731
        gid_goal = g.filter(pl.col("kind") == "goal")["gid"][0]
        gid_kick = g.filter(pl.col("kind") == "kickoff")["gid"][0]
        out[f"{m}|goal"] = vec(gid_goal)
        out[f"{m}|kickoff"] = vec(gid_kick)
        if goal in ROOM_KICKOFF_PERIODS:
            for rm in (2, 3):
                out[f"{m}|room{rm}"] = vec(g.filter((pl.col("kind") == "kickoff_room") & (pl.col("room") == rm))["gid"][0])
            out[f"{m}|E|P"] = gram_schmidt([out[f"{m}|goal"], out[f"{m}|kickoff"], out[f"{m}|room2"], out[f"{m}|room3"]])
            out[f"{m}|roomdiff"] = unitv(out[f"{m}|room2"] - out[f"{m}|room3"])
        elif goal != 51:
            out[f"{m}|E|P"] = gram_schmidt([out[f"{m}|goal"], out[f"{m}|kickoff"]])
        if goal == 51:
            ag = g.filter((pl.col("kind") == "agent_goal") & pl.col("valid_to").is_null())   # current role text per agent
            for a, gid in zip(ag["agent"].to_list(), ag["gid"].to_list()):
                out[f"{m}|a{a}"] = vec(gid)
                out[f"{m}|E|a{a}"] = gram_schmidt([out[f"{m}|a{a}"], out[f"{m}|goal"]])
            old = ag.filter(pl.col("agent") == NE38_OLD_GOAL_AGENT)["gid"][0]
            out[f"{m}|a40old"] = vec(old)
            out[f"{m}|E|a40old"] = gram_schmidt([out[f"{m}|a40old"], out[f"{m}|goal"]])
    return out


def build(goal: int) -> dict:
    days = days_for(goal)
    units = unit_of(goal, days)
    od = OUT / f"G{goal:02d}"
    od.mkdir(parents=True, exist_ok=True)

    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.col("goal_no") == goal) & pl.col("pt_date").is_in(days))
          .select("turn_id", "agent", "pt_date", "t_call", "holdout").collect())
    assert not cw["holdout"].any()
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("goal_no") == goal)
          .select("turn_id", "reset_forced", "reset_consol", "room").collect())
    calls = (cw.join(ct, on="turn_id", how="left")
             .with_columns(pl.col("reset_forced").fill_null(False), pl.col("reset_consol").fill_null(False))
             .sort("agent", "pt_date", "t_call", "turn_id")
             .with_columns(pl.int_range(pl.len()).over("agent", "pt_date").cast(pl.Int32).alias("n"))
             .with_columns(pl.col("reset_forced").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("nf"),
                           (pl.col("reset_consol") & ~pl.col("reset_forced")).cast(pl.Int32).cum_sum()
                           .over("agent", "pt_date").alias("nc"))
             .drop("holdout"))
    calls = calls.join(units, on="pt_date", how="inner")

    st = (pl.scan_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
          .filter((pl.col("kind") == "chat") & (pl.col("goal_no") == goal) & pl.col("pt_date").is_in(days))
          .select("srow", "src_row", "agent", "t", "pt_date", "room", "holdout").collect())
    assert not st["holdout"].any()
    assert not any(holdout_mask(st["pt_date"].to_list(), [goal] * st.height))
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    cc = pl.scan_parquet(SH / "chat_core.parquet").select("message_id", "speaker_kind", pl.col("agent").alias("a_cc")).collect()
    st = (st.join(ci, on="src_row", how="left").join(cc, on="message_id", how="left")
          .filter((pl.col("speaker_kind") == "agent") & (pl.col("a_cc") == pl.col("agent"))).drop("a_cc"))
    fl = pl.scan_parquet(SH / "statement_flags.parquet").select("srow", "exact_self_repeat").collect()
    st = st.join(fl, on="srow", how="left").with_columns(pl.col("exact_self_repeat").fill_null(False))
    pc = (pl.scan_parquet(SH / "producing_calls.parquet").filter(pl.col("goal_no") == goal)
          .select("message_id", "turn_id_prod", "t_call_prod", "prod_fallback").collect())
    st = st.join(pc, on="message_id", how="left")
    allst = st
    tgt = (st.filter(pl.col("turn_id_prod").is_not_null() & ~pl.col("prod_fallback").fill_null(True)
                     & ~pl.col("exact_self_repeat"))
           .join(calls.select(pl.col("turn_id").alias("turn_id_prod"), "n", "nf", "nc", "unit_id"),
                 on="turn_id_prod", how="inner")
           .rename({"turn_id_prod": "turn_id", "t_call_prod": "t_call"})
           .select("srow", "message_id", "agent", "t", "pt_date", "room", "unit_id", "turn_id", "t_call", "n", "nf", "nc")
           .sort("agent", "t"))
    tgt = tgt.with_columns((pl.int_range(pl.len()).over("agent", "pt_date") % 2).cast(pl.Int8).alias("half"))
    if goal == 51:
        tgt = tgt.with_columns(
            pl.when((pl.col("agent") == NE38_AGENT) & (pl.col("t") < NE38_T)).then(pl.lit("a40old"))
            .otherwise(pl.lit("a") + pl.col("agent").cast(pl.String)).alias("plane"))
    else:
        tgt = tgt.with_columns(pl.lit("P").alias("plane"))

    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind") == "agent")
             .select("turn_id", "message_id", "sender").collect())
    items = items.join(calls.select("turn_id", pl.col("agent").alias("reader"), "pt_date", "t_call", "n", "nf", "nc",
                                    "unit_id"), on="turn_id", how="inner")
    msg = allst.select("message_id", pl.col("srow").alias("srow_m"), pl.col("t").alias("t_post"),
                       pl.col("room").alias("room_m"), pl.col("agent").alias("sender_st"))
    reads = (items.join(msg, on="message_id", how="inner")
             .filter(pl.col("sender_st") != pl.col("reader"))
             .select("reader", "turn_id", "t_call", "n", "nf", "nc", pl.col("sender_st").alias("sender"), "srow_m",
                     "t_post", "room_m", "pt_date", "unit_id")
             .sort("reader", "t_call", "t_post"))

    tv = text_vectors(goal)
    missing = sorted(set(tgt["plane"].unique().to_list()) - {k.split("|")[2] for k in tv if k.count("|") == 2})
    tgt.write_parquet(od / "statements.parquet", compression="zstd")
    reads.write_parquet(od / "reads.parquet", compression="zstd")
    calls.write_parquet(od / "calls.parquet", compression="zstd")
    np.savez_compressed(od / "planes.npz", **tv)
    summ = {"goal": goal, "days": len(days), "statements": tgt.height, "reads": reads.height, "calls": calls.height,
            "units": sorted(units["unit_id"].unique().to_list()), "planes_missing": missing,
            "dropped_no_call_or_repeat": int(st.height - tgt.height)}
    prov = {"built_by": "hypotheses/H141-easy-plane-anisotropy/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["embeddings/statements", "embeddings/chat_index", "embeddings/goals",
                                   "embeddings/goal_vectors{,_gte_modernbert}", "embeddings/whitening*_III",
                                   "chat_core", "statement_flags", "producing_calls", "call_windows",
                                   "context_ledger_items", "context_ledger_turns", "calendar", "period_units"]}],
            "params": {"goal": goal, "room_kickoff_periods": sorted(ROOM_KICKOFF_PERIODS), "ne38_old_goal_agent":
                       NE38_OLD_GOAL_AGENT, "summary": summ},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (od / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    goals = PERIODS if a.all or not a.period else [int(a.period.lstrip("G"))]
    for g in goals:
        assert g in PERIODS
        print(json.dumps(build(g)), flush=True)
    top = {"built_by": "hypotheses/H141-easy-plane-anisotropy/scheme/build.py", "git_commit": git_commit(),
           "inputs": [{"source": "ai-village", "revision": REVISION, "tables": ["see G<NN>/_provenance.json"]}],
           "params": {"periods": PERIODS}, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(top, indent=1))


if __name__ == "__main__":
    main()
