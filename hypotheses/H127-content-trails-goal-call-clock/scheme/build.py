"""H127 scheme: per-agent clocks for the day-1 rise after each kickoff (codes and times only, no text).

Reads H125's processed statement selections (read-only) and the shared call tables. Builds
data/processed/H127-content-trails-goal-call-clock/:
  agents.parquet  one row per (design, agent): statement counts (pre, day-1 post-t0, days 2-5), day-1 calls after t0,
                  day-1 active hours after t0, call rate r, leave-period-out cadence r_lpo (same regime), read-out call
                  time t_ro (first call whose context ledger holds a kickoff message of the period), fallback flag, lab.
  day1.parquet    one row per day-1 post-t0 statement: row (shared statements index), design, agent, h (hours since t0),
                  c (own calls since t0, inclusive of the producing call), h_ro, c_ro (since the read-out call).
  _provenance.json
Usage: uv run python hypotheses/H127-content-trails-goal-call-clock/scheme/build.py
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

S = ROOT / "data/processed/shared"
H125 = ROOT / "data/processed/H125-kickoff-damped-oscillator"
OUT = ROOT / "data/processed/H127-content-trails-goal-call-clock"
NE38_AGENT = 40


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    kk = pl.read_parquet(H125 / "kickoffs.parquet").filter(pl.col("design") != "T51")   # G51 holds #51 (own roles)
    kk = pl.concat([kk, pl.read_parquet(H125 / "kickoffs.parquet").filter(pl.col("design") == "T51")])
    st = pl.read_parquet(H125 / "stmt.parquet")
    cal = pl.read_parquet(S / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    cal = cal.with_columns(pl.Series("ho", holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))
    calr = {r["pt_date"]: r for r in cal.iter_rows(named=True)}
    roster = pl.read_parquet(S / "roster.parquet")
    lab = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))

    cw = pl.read_parquet(S / "call_windows.parquet", columns=["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_call"])
    cw = cw.filter(~pl.col("holdout")).with_columns(pl.col("regime").cast(pl.String))
    cw = cw.filter(~pl.Series(holdout_mask(cw["pt_date"].to_list(), cw["goal_no"].to_list())))
    kc = pl.read_parquet(S / "kicks_classified.parquet")
    kmsg = kc.filter(((pl.col("kind") == "human_message") & (pl.col("subkind") == "kickoff")) | (pl.col("kind") == "goal_kickoff"))
    kmsg = kmsg.filter(pl.col("message_id").is_not_null())
    items = pl.read_parquet(S / "context_ledger_items.parquet", columns=["turn_id", "message_id", "omitted"])

    # leave-period-out cadence: calls per active hour over the agent's active days (>= 1 call) per regime and goal
    cday = cw.group_by("agent", "pt_date", "goal_no", "regime").len("n_calls")
    cday = cday.with_columns(pl.col("pt_date").map_elements(lambda d: calr[d]["window_s"] / 3600 if d in calr else None,
                                                            return_dtype=pl.Float64).alias("hours"))
    cg = cday.group_by("agent", "regime", "goal_no").agg(pl.col("n_calls").sum(), pl.col("hours").sum())

    def r_lpo(agent, regime, goal):
        x = cg.filter((pl.col("agent") == agent) & (pl.col("regime") == regime) & (pl.col("goal_no") != goal))
        return float(x["n_calls"].sum() / x["hours"].sum()) if x.height and x["hours"].sum() > 0 else None

    arows, drows = [], []
    for kr in kk.iter_rows(named=True):
        des, g, t0, d1 = kr["design"], kr["goal_no"], kr["t0"], kr["first_day"]
        sd = st.filter(pl.col("design") == des)
        win_end = calr[d1]["win_end"]
        hours1 = max((win_end - t0).total_seconds() / 3600, 1e-6)
        # read-out messages
        if des == "NE38":
            hm = kc.filter((pl.col("kind") == "human_message") & (pl.col("t") >= t0 - dt.timedelta(minutes=10))
                           & (pl.col("t") <= t0 + dt.timedelta(minutes=30)) & pl.col("message_id").is_not_null())
            hm = hm.filter(pl.col("targets").list.contains(NE38_AGENT))
            mids = hm["message_id"].to_list()
        else:
            mids = kmsg.filter(pl.col("goal_no") == g)["message_id"].to_list()
        ro_turns = items.filter(pl.col("message_id").is_in(mids) & ~pl.col("omitted").fill_null(False))["turn_id"].unique()
        cwd = cw.filter((pl.col("pt_date") == d1) & (pl.col("goal_no") == g)).sort("t_call")
        ro = cwd.filter(pl.col("turn_id").is_in(ro_turns.to_list()) & (pl.col("t_call") >= t0 - dt.timedelta(minutes=5)))
        ro_first = ro.group_by("agent").agg(pl.col("t_call").min().alias("t_ro"))
        ro_map = dict(zip(ro_first["agent"].to_list(), ro_first["t_ro"].to_list()))
        for a in kr["incumbents"]:
            sa = sd.filter(pl.col("agent") == a)
            pre = sa.filter(pl.col("seg") == "pre")
            post1 = sa.filter((pl.col("seg") == "post") & (pl.col("day_idx") == 1))
            sett = sa.filter((pl.col("seg") == "post") & pl.col("day_idx").is_between(2, 5))
            calls = cwd.filter((pl.col("agent") == a) & (pl.col("t_call") > t0))["t_call"].to_list()
            tc = np.array([c.timestamp() for c in calls])
            t_ro = ro_map.get(a)
            fb = t_ro is None
            if fb:
                t_ro = calls[0] if calls else None
            arows.append(dict(design=des, goal_no=g, regime=kr["regime"], agent=a, lab=lab.get(a), n_pre=pre.height,
                              n_day1=post1.height, n_settled=sett.height, calls_day1=len(calls), hours_day1=hours1,
                              r=len(calls) / hours1, r_lpo=r_lpo(a, kr["regime"], g), t_ro=t_ro, ro_fallback=fb,
                              ro_delay_h=((t_ro - t0).total_seconds() / 3600) if t_ro else None))
            if post1.height == 0:
                continue
            ts = np.array([t.timestamp() for t in post1["t"].to_list()])
            c = np.searchsorted(tc, ts, side="right") if len(tc) else np.zeros(len(ts), int)
            if t_ro is not None:
                tro = t_ro.timestamp()
                c_ro = c - np.searchsorted(tc, tro, side="left")
                h_ro = (ts - tro) / 3600
            else:
                c_ro = np.full(len(ts), np.nan); h_ro = np.full(len(ts), np.nan)
            for row, h, ci, hr, cr in zip(post1["row"].to_list(), post1["h"].to_list(), c, h_ro, c_ro):
                drows.append(dict(row=row, design=des, agent=a, h=float(h), c=int(ci), h_ro=float(hr), c_ro=float(cr)))
    ag = pl.DataFrame(arows, infer_schema_length=None)
    d1t = pl.DataFrame(drows).with_columns(pl.col("h").cast(pl.Float32), pl.col("c").cast(pl.Int32),
                                           pl.col("h_ro").cast(pl.Float32), pl.col("c_ro").cast(pl.Float32))
    ag.write_parquet(OUT / "agents.parquet", compression="zstd")
    d1t.write_parquet(OUT / "day1.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H127-content-trails-goal-call-clock/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["H125-kickoff-damped-oscillator/{kickoffs,stmt} (read-only)", "shared/call_windows",
                                   "shared/context_ledger_items", "shared/kicks_classified", "shared/calendar", "shared/roster"]}],
            "params": {"ne38_agent": NE38_AGENT}, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(ag.group_by("design").agg(pl.len(), pl.col("ro_fallback").mean().alias("fb"), (pl.col("n_pre") >= 4).mean().alias("pre4"),
                                    pl.col("calls_day1").median(), pl.col("r").median(), pl.col("ro_delay_h").median()).sort("design"))
    print(ag.height, d1t.height)


if __name__ == "__main__":
    main()
