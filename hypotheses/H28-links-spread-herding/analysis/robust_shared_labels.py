"""Robustness (coordinator request, 2026-10-04; post hoc): the headline link-exposure hazard on the deterministic shared
project labels (data/processed/shared/project_states.parquet, infra/shared/project_states.py; W = 30 min, sources
"all"), i.e. H11-style window states instead of H28's touch-based arrivals.

Window-level kinetic Potts switch: risk set = (agent i labeled in window w, real project label X in 1..q) with i's
previous labeled window on the same day not in state X; y = 1[sigma_i(w) = X]. Exposure E60 = any link to X (by
others) visible to i in the 60 min before the window start (H28 exposures, call-start visibility). Controls: log(1 +
others in X in the previous window), i was ever in X before (period), quarter; FE agent + project + day (Amendment 1).
Null: the same link time-shift as N1 (99 draws). Non-holdout rows only.

  uv run python hypotheses/H28-links-spread-herding/analysis/robust_shared_labels.py [--goals ...] [--shifts 99]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h28core as hc  # noqa: E402
from h28lib import ALL_PERIODS, OUT, SHARED, gname  # noqa: E402

W_MS = 30 * 60_000


def period_rows(g, P):
    ps = pl.read_parquet(SHARED / "project_states.parquet").filter(
        (pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all") & (pl.col("goal_no") == g) & ~pl.col("holdout"))
    meta = P["meta"]
    ws = {d["pt_date"]: d["ws_ms"] for d in meta["days"]}
    ps = ps.filter(pl.col("pt_date").is_in(list(ws)))
    ps = ps.with_columns(pl.col("project").cast(pl.String))
    q = int(ps["label"].max() or 0)
    names = {int(r["label"]): r["project"] for r in ps.filter(pl.col("label") > 0).select("label", "project").unique().iter_rows(named=True)}
    ps = ps.sort("agent", "pt_date", "win")
    rows = []
    for (a, d), sub in ps.group_by(["agent", "pt_date"], maintain_order=True):
        lab = sub["label"].to_list()
        win = sub["win"].to_list()
        for k in range(1, len(lab)):
            prev = lab[k - 1]
            for X in range(1, q + 1):
                if prev == X:
                    continue
                rows.append((int(a), d, int(win[k]), X, int(lab[k] == X)))
    df = pl.DataFrame(rows, schema=["agent", "pt_date", "win", "X", "y"], orient="row")
    df = df.with_columns(pl.col("pt_date").replace_strict(ws).alias("ws")).with_columns(
        (pl.col("ws") + pl.col("win").cast(pl.Int64) * W_MS).alias("T"))
    # controls: occupancy of X in the previous window (others), ever-in-X before
    occ = ps.filter(pl.col("label") > 0).group_by("pt_date", "win", "label").agg(pl.col("agent").alias("occ_agents"))
    df = df.join(occ.with_columns((pl.col("win") + 1).alias("win")).rename({"label": "X"}), on=["pt_date", "win", "X"], how="left")
    df = df.with_columns(pl.struct("agent", "occ_agents").map_elements(
        lambda s: sum(1 for x in (s["occ_agents"] or []) if x != s["agent"]), return_dtype=pl.Int64).alias("occ"))
    first = ps.filter(pl.col("label") > 0).with_columns(
        (pl.col("pt_date").replace_strict(ws) + pl.col("win").cast(pl.Int64) * W_MS).alias("T0")).group_by(
        "agent", "label").agg(pl.col("T0").min()).rename({"label": "X"})
    df = df.join(first, on=["agent", "X"], how="left").with_columns(
        (pl.col("T0").is_not_null() & (pl.col("T0") < pl.col("T"))).cast(pl.Float64).alias("own_ever"))
    days = sorted(ws)
    span = {d["pt_date"]: max(1, d["we_ms"] - d["ws_ms"]) for d in meta["days"]}
    df = df.with_columns(pl.col("pt_date").replace_strict({d: i for i, d in enumerate(days)}).alias("day"),
                         ((4 * (pl.col("T") - pl.col("ws"))) // pl.col("pt_date").replace_strict(span)).clip(0, 3).alias("q"))
    return df, names


def exposure_feature(P, df, names, link_t=None, t_vis=None):
    """E60 for rows (agent code, X, T) from H28 link exposures, matched by project name."""
    L, E = P["links"], P["expo"]
    pname = P["projects"]
    lab_of = {v: k for k, v in names.items()}
    agents = np.array(P["agents"])
    tv = E["t_vis"] if t_vis is None else t_vis
    xs = np.array([lab_of.get(pname[x], -1) if x >= 0 else -1 for x in L["x"]], np.int64)
    ex_lab = xs[E["lid"]]
    m = (ex_lab > 0) & (tv >= 0)
    rcode = agents[E["ri"][m]]
    comp = np.sort((rcode.astype(np.int64) * 100 + ex_lab[m]) * hc.BIG + tv[m])
    base = (df["agent"].to_numpy().astype(np.int64) * 100 + df["X"].to_numpy()) * hc.BIG + df["T"].to_numpy()
    return (hc._count(comp, base - hc.W60, base) > 0).astype(float)


def fit_rows(df, E):
    X = np.column_stack([E, np.log1p(df["occ"].to_numpy()), df["own_ever"].to_numpy(),
                         *[(df["q"].to_numpy() == k).astype(float) for k in (1, 2, 3)]])
    nD = int(df["day"].max()) + 1
    fes = [df["agent"].to_numpy().astype(np.int64), df["X"].to_numpy().astype(np.int64), df["day"].to_numpy().astype(np.int64)]
    cl = df["agent"].to_numpy().astype(np.int64) * nD + df["day"].to_numpy()
    res = hc.pois_fe(df["y"].to_numpy().astype(float), X, fes, cl, names=["E60", "log_occ", "own_ever", "q1", "q2", "q3"])
    return res


def run(g, shifts=99, seed=2028):
    P = hc.load_period(OUT / gname(g), universe="U+")
    df, names = period_rows(g, P)
    if df.is_empty() or df["y"].sum() < 10:
        return dict(goal=g, n=int(df.height), switches=int(df["y"].sum()) if df.height else 0, note="too few switches")
    E = exposure_feature(P, df, names)
    res = fit_rows(df, E)
    k, se = hc.coef(res, "E60")
    rng = np.random.default_rng(seed + g)
    null = []
    for _ in range(shifts):
        lt, tv = hc.shift_links(P, rng)
        null.append(hc.coef(fit_rows(df, exposure_feature(P, df, names, lt, tv)), "E60")[0])
    null = np.array([v for v in null if np.isfinite(v)])
    return dict(goal=g, n=int(df.height), switches=int(df["y"].sum()), exposed_switches=int(df["y"].to_numpy()[E > 0].sum()),
                q=len(names), kappa=k, se=se, p=float(2 * norm.sf(abs(k / se))), null_mean=float(null.mean()),
                null_sd=float(null.std(ddof=1)), z_shift=float((k - null.mean()) / null.std(ddof=1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="*", default=[g for g in ALL_PERIODS if g != 51])
    ap.add_argument("--shifts", type=int, default=99)
    a = ap.parse_args()
    out = {}
    for g in a.goals:
        out[g] = run(g, a.shifts)
        print(json.dumps(out[g], default=float), flush=True)
    (OUT / "robust_shared_labels.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
