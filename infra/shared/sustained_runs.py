"""Shared sustained-run starts: the first call of a run of >= 3 consecutive active DQ1 ledger calls of one agent-day.

Two hypotheses build this sidecar with different rules, so both rules are kept, one per `rule` value:
  h35_kind  H35 (hypotheses/H35-nudger-maxwell-demon/analysis/r1b_outcomes.py: load_sources). All ledger calls
            (context_ledger_turns, summary calls included) in (t_first, turn_id) order per agent-day; a call is active
            iff kind in {cu_action, talk, search, room_move, request}; a run is a maximal block of consecutive active
            calls; its start time is the first call's t_first.
  h43_gap   H43 (hypotheses/H43-kick-refractory-window/analysis/h43lib.py: Prep, "sustained run starts"). Non-summary
            calls (call_windows) in (t_call, turn_id) order per agent-day; a call is idle iff kind in {pause, wait} and
            it does not talk, else active; a new run also starts after a gap >= 180 s between the previous call's
            t_end and this call's t_call; the start time is the first call's t_call.
The H43 rule is stricter (gap breaks), so its run starts are a different set, not a subset. Escape outcomes are
definition-sensitive (Known issue, H43): report both.

Output (data/processed/shared/sustained_run_starts.parquet, zstd, codes only, ALL days; `holdout` flags locked-holdout
days; exploratory users filter `~holdout`): rule, agent, pt_date, goal_no, holdout, turn_id (first call of the run),
t_start, n_calls (active calls in the run, >= 3). Only sustained runs are stored.

Usage: uv run python infra/shared/sustained_runs.py            (build)
       uv run python infra/shared/sustained_runs.py --verify   (H35 load_sources and H43 Prep in memory; read-only)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "RAYON_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, write_provenance  # noqa: E402
from visibility import load_ro  # noqa: E402

SH = OUT
RUN_MIN = 3
ACTIVE_KINDS_H35 = ["cu_action", "talk", "search", "room_move", "request"]
IDLE_KINDS_H43 = ["pause", "wait"]
GAP_IDLE_S = 180.0


def runs_h35(min_len: int = RUN_MIN) -> pl.DataFrame:
    led = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
           .select("turn_id", "agent", "pt_date", "goal_no", "holdout", "t_first", "kind").collect()
           .with_columns(pl.col("kind").cast(pl.Utf8).is_in(ACTIVE_KINDS_H35).alias("act"))
           .sort("agent", "pt_date", "t_first", "turn_id"))
    led = led.with_columns((pl.col("act") != pl.col("act").shift(1).over("agent", "pt_date")).fill_null(True).alias("brk"))
    led = led.with_columns(pl.col("brk").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("run"))
    return (led.filter(pl.col("act")).group_by("agent", "pt_date", "run", maintain_order=True)
            .agg(pl.len().cast(pl.Int32).alias("n_calls"), pl.col("turn_id").first(), pl.col("t_first").first().alias("t_start"),
                 pl.col("goal_no").first(), pl.col("holdout").first())
            .filter(pl.col("n_calls") >= min_len).drop("run").with_columns(pl.lit("h35_kind").alias("rule")))


def runs_h43(min_len: int = RUN_MIN) -> pl.DataFrame:
    c = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("ctx_mode").cast(pl.Utf8) != "summary")
         .select("turn_id", "agent", "pt_date", "goal_no", "holdout", "kind", "talk", "t_call", "t_end").collect()
         .sort("agent", "pt_date", "t_call", "turn_id"))
    idle = c["kind"].cast(pl.Utf8).is_in(IDLE_KINDS_H43).to_numpy() & ~c["talk"].to_numpy()
    active = ~idle
    key = (c["agent"].cast(pl.Utf8) + "|" + c["pt_date"]).to_numpy()
    newg = np.r_[True, key[1:] != key[:-1]]
    t = c["t_call"].dt.epoch("us").to_numpy() / 1e6
    tend = c["t_end"].dt.epoch("us").to_numpy() / 1e6
    gap = t - np.r_[np.nan, tend[:-1]]
    prev_idle = np.r_[False, idle[:-1]]
    boundary = newg | prev_idle | (gap >= GAP_IDLE_S)
    run_id = np.cumsum(boundary | ~active)
    c = c.with_columns(pl.Series("run", run_id), pl.Series("act", active), pl.Series("start", active & boundary))
    r = (c.filter(pl.col("act")).group_by("run", maintain_order=True)
         .agg(pl.len().cast(pl.Int32).alias("n_calls"), pl.col("start").first(), pl.col("agent").first(),
              pl.col("pt_date").first(), pl.col("turn_id").first(), pl.col("t_call").first().alias("t_start"),
              pl.col("goal_no").first(), pl.col("holdout").first()))
    assert r["start"].all(), "an active run must open at a boundary"
    return r.filter(pl.col("n_calls") >= min_len).drop("run", "start").with_columns(pl.lit("h43_gap").alias("rule"))


def build() -> pl.DataFrame:
    cols = ["rule", "agent", "pt_date", "goal_no", "holdout", "turn_id", "t_start", "n_calls"]
    out = pl.concat([runs_h35().select(cols), runs_h43().select(cols)])
    return out.with_columns(pl.col("rule").cast(pl.Categorical)).sort("rule", "agent", "t_start")


def main():
    t0 = time.time()
    df = build()
    p = SH / "sustained_run_starts.parquet"
    df.write_parquet(p, compression="zstd", compression_level=9)
    nh = df.filter(~pl.col("holdout"))
    summ = {r: int(n) for r, n in nh.group_by("rule").len().iter_rows()}
    write_provenance("sustained_runs", ["context_ledger_turns", "call_windows"],
                     {"run_min": RUN_MIN, "h35_kind": f"all ledger calls by t_first; active = kind in {ACTIVE_KINDS_H35}",
                      "h43_gap": f"non-summary calls by t_call; idle = kind in {IDLE_KINDS_H43} & ~talk; new run after "
                                 f"an idle call or a gap >= {GAP_IDLE_S} s (t_call - previous t_end)",
                      "order_ties": "turn_id", "holdout": "all days, flagged",
                      "sources": "H35 r1b_outcomes.load_sources; H43 h43lib.Prep (rules unchanged)",
                      "summary_nonholdout_starts": summ})
    print(f"sustained_run_starts.parquet: {df.height} rows, {p.stat().st_size / 1e6:.2f} MB, {time.time() - t0:.0f}s; "
          f"non-holdout {summ}", flush=True)


def _cmp(mine: dict, ref: dict, tol: float = 1e-3) -> dict:
    keys = set(mine) | set(ref)
    n_m = sum(len(v) for v in mine.values())
    n_r = sum(len(v) for v in ref.values())
    agree = 0
    bad_keys = 0
    for k in keys:
        a = np.sort(mine.get(k, np.zeros(0)))
        b = np.sort(ref.get(k, np.zeros(0)))
        if len(a) == len(b) and (len(a) == 0 or np.max(np.abs(a - b)) < tol):
            agree += len(a)
        else:
            bad_keys += 1
            # matched starts within tolerance
            j = np.searchsorted(b, a)
            ok = np.zeros(len(a), bool)
            for s in (j - 1, j):
                ss = np.clip(s, 0, max(len(b) - 1, 0))
                if len(b):
                    ok |= np.abs(b[ss] - a) < tol
            agree += int(ok.sum())
    return {"shared": n_m, "reference": n_r, "matched": agree, "agent_days_differing": bad_keys,
            "identical": n_m == n_r == agree}


def verify() -> dict:
    df = pl.read_parquet(SH / "sustained_run_starts.parquet").filter(~pl.col("holdout"))
    res = {}
    # H35
    r1b = load_ro("h35_r1b_outcomes_ro", ROOT / "hypotheses/H35-nudger-maxwell-demon/analysis/r1b_outcomes.py")
    sust, _, _ = r1b.load_sources()
    m = df.filter(pl.col("rule") == "h35_kind").with_columns((pl.col("t_start").dt.epoch("us") / 1e6).alias("ts"))
    mine = {(int(a), d): g["ts"].to_numpy() for (a, d), g in m.group_by(["agent", "pt_date"])}
    res["H35"] = _cmp(mine, sust)
    # H43 (its calls.parquet: non-holdout, unit-mapped; Prep over all calls, groups = agent-day)
    h43 = load_ro("h43lib_ro", ROOT / "hypotheses/H43-kick-refractory-window/analysis/h43lib.py")
    calls = pl.read_parquet(ROOT / "data/processed/H43-kick-refractory-window/calls.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "win_start", "win_end"]).with_columns(
        (pl.col("win_start").dt.epoch("us") / 1e6), (pl.col("win_end").dt.epoch("us") / 1e6))
    states = pl.DataFrame(schema={"pt_date": pl.Utf8, "minute": pl.Int64, "agent": pl.Int64, "lump4_min": pl.Int8,
                                  "in_span": pl.Boolean, "present": pl.Boolean})
    writes = pl.DataFrame(schema={"agent": pl.Int8, "t": pl.Float64})
    P = h43.Prep(calls, states, writes, cal)
    key_day = np.floor(P.rs3_key / 1e7).astype(np.int64)
    first_idx = np.full(int(P.grp.max()) + 1, -1, np.int64)
    first_idx[P.grp[::-1]] = np.arange(P.n)[::-1]          # first call index of each agent-day group
    ref = {}
    for gi, ts in zip(key_day, P.rs3_t):
        i0 = first_idx[gi]
        ref.setdefault((int(P.agent[i0]), P.pt_date[i0]), []).append(ts)
    ref = {k: np.array(v) for k, v in ref.items()}
    m = df.filter(pl.col("rule") == "h43_gap").with_columns((pl.col("t_start").dt.epoch("us") / 1e6).alias("ts"))
    days = set(calls.select("agent", "pt_date").unique().iter_rows())
    mine = {(int(a), d): g["ts"].to_numpy() for (a, d), g in m.group_by(["agent", "pt_date"]) if (int(a), d) in days}
    res["H43"] = _cmp(mine, ref)
    res["H43"]["note"] = "H43 calls.parquet keeps unit-mapped non-holdout days; shared restricted to its agent-days"
    print(json.dumps(res, indent=1), flush=True)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
