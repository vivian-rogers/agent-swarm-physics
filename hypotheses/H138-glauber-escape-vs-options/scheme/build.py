"""H138 scheme: per (agent, 30-min window, visit) leave panels with open-option counts and Z_alt, per goal period and
channel, from shared tables only.

Work channel: the shared host replay (infra/shared/replicator_hosts.py, W 30, E 100; non-reserved days). Attention
channel: project_states (w_min 30, sources all, strict mentions, raw project; non-reserved rows) carried forward with the
same call-clock expiry. A leave is a direct label change a -> b != a; expiry, roster exit and the unit end censor.
Exposure = own calls (call_windows, all kinds) in the window while the agent holds a.

Writes data/processed/H138-glauber-escape-vs-options/G<NN>/windows_<channel>.parquet (project names replaced by a
within-unit index; no text), G<NN>/counts.json and _provenance.json.

Usage: uv run python hypotheses/H138-glauber-escape-vs-options/scheme/build.py [--period G38] [--channel work]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import h138lib as L  # noqa: E402
from common import REVISION, git_commit, holdout_mask  # noqa: E402

RH = L.RH


def build(goal: int, channel: str) -> dict:
    if channel == "work":
        d = L.work_visits(goal)
        V, calls = d["visits"], d["calls"]
        com = d["commits"]
        marks_src = [(int(a), p, t.timestamp()) for a, p, t in com.select("agent", "repo", "t").iter_rows()]
    else:
        d = L.attention_visits(goal)
        V, calls = d["visits"], d["calls"]
        lab = d["labels"]
        marks_src = [(int(a), p, float(t) + 60.0) for a, p, t in lab.select("agent", "project", "tw0").iter_rows()]
    days_all = d["days"]
    assert not any(holdout_mask(days_all, [goal] * len(days_all))), "reserved day in input"
    projects = sorted(set(V["project"].to_list()))
    named = RH.kickoff_named(goal, projects) if projects else {}
    reads = L.read_projects(goal, days_all) if days_all else None
    out, counts = [], {}
    for unit, days in L.unit_days(goal).items():
        if not days:
            continue
        grid = L.Grid(days)
        tm = np.array([m[2] for m in marks_src])
        gg = grid.g_of(tm) if len(tm) else np.array([], int)
        own_mark = {(a, int(g), p) for (a, p, _), g in zip(marks_src, gg) if g >= 0}
        df, ctx = L.build_unit_panel(unit, days, V, calls, goal, channel, named, own_mark, reads)
        if df.height == 0:
            counts[unit] = {"rows": 0, "leaves": 0}
            continue
        df, zinfo = L.add_zalt(df, ctx)
        df = df.with_columns(pl.lit(goal).cast(pl.Int8).alias("goal_no"))
        out.append(df)
        nl = int(df["leave"].sum())
        counts[unit] = {"rows": df.height, "leaves": nl, "agents": int(df["agent"].n_unique()),
                        "projects": len(ctx["projects"]), "calls_at_risk": int(df["calls"].sum()), "days": len(days),
                        "windows": int(grid.G), "testable": bool(nl >= L.MIN_LEAVES), "z_join_model": zinfo,
                        "named_projects": int(sum(bool(named.get(p, False)) for p in ctx["projects"]))}
    return {"panel": pl.concat(out) if out else None, "counts": counts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default=None)
    ap.add_argument("--channel", default=None, choices=["work", "attention"])
    a = ap.parse_args()
    t0 = time.time()
    chans = [a.channel] if a.channel else ["work", "attention"]
    for ch in chans:
        goals = L.WORK_GOALS if ch == "work" else L.ATT_GOALS
        if a.period:
            goals = [int(a.period.lstrip("G"))]
        for g in goals:
            o = L.D / f"G{g:02d}"
            o.mkdir(parents=True, exist_ok=True)
            r = build(g, ch)
            if r["panel"] is not None:
                r["panel"].write_parquet(o / f"windows_{ch}.parquet", compression="zstd")
            cp = o / "counts.json"
            c = json.loads(cp.read_text()) if cp.exists() else {}
            c[ch] = r["counts"]
            cp.write_text(json.dumps(c, indent=1))
            print(f"G{g:02d} {ch}: " + ", ".join(f"{u} {v.get('leaves', 0)}/{v.get('rows', 0)}" for u, v in r["counts"].items())
                  + f"  ({time.time() - t0:.0f}s)", flush=True)
    prov = {"built_by": "hypotheses/H138-glauber-escape-vs-options/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["work_commits", "call_windows", "calendar", "period_units", "roster", "project_states",
                                   "rooms_timeline", "context_ledger_items", "context_ledger_turns",
                                   "project_mentions_chat", "chat_core (kickoff naming, in memory)", "artifact_mentions"]}],
            "params": {"W_min": L.W_MIN, "E": L.E_EXP, "lookback_windows": L.L_WIN, "attention": "project_states w30 sources=all",
                       "units": "#51 by period_units; #36 split at 2026-03-24; else whole period",
                       "zalt": "H11-r2 join features, clogit L2 0.5, cross-fitted by day folds"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (L.D / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
