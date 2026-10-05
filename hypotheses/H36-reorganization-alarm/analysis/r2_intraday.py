"""H36 round 2, R2 (2026-10-05): intraday topic-shift alarm on 30-min windows (pre-registered in the card, Round 2).

Statistic. Per 30-min window w of the day's activity window (`agent_win30`, restatements removed with the model's own
self_repeat flag), m_w = mean over speaking agents (>= 3) of the centered unit raw vectors (centered on the
non-holdout mean of window vectors). D(w) = 1 - cos(m_w, mean of m over the previous 4 scored windows), across day
edges; held-out days are absent. r1w(w) = robust z of D(w) against the previous 16 scored windows (median; SD of the
middle 14 divided by its Gaussian consistency factor; >= 10 windows needed). Alarm: r1w >= 3.

Readouts (non-holdout only): kickoff hits in the first 2 windows of day 0 vs the same windows of placebo days; lead =
alarms in the last 4 windows of day -1 vs placebo days; first alarm window on day 0 and its lag after the kickoff
message; mid-day room events (#focus 08-05 first move 17:39 UTC; side-room 07-24) and the day-start room events
(05-04 merge, 05-11 split).

Synthetic (axis F; --synthetic): the real non-holdout skeleton (days, windows, speaking agents) with synthetic vectors
(synthetic.py's content model in d = 32 plus a day-level drift), goal switches at the real kickoff day starts and at a
random mid-day window on 12 random other days per run.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r2_intraday.py [--synthetic] [--model bge_small]
Outputs: data/processed/H36-reorganization-alarm/r2/intraday_<model>.{parquet,json}, r2/intraday_synthetic.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h36lib as L  # noqa: E402
import build as B  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R2 = L.OUT / "r2"
REF_W, BASE_W, MIN_W, THR, MIN_AG = 4, 16, 10, 3.0, 3
UTC = dt.timezone.utc


def trim_factor(k: int, n: int = 40000, seed: int = 1) -> float:
    """E[SD (ddof 1) of the middle k-2 of k Gaussian draws] / sigma."""
    x = np.sort(np.random.default_rng(seed).normal(size=(n, k)), 1)[:, 1:-1]
    return float(x.std(1, ddof=1).mean())


TF = {k: trim_factor(k) for k in range(MIN_W, BASE_W + 1)}


def robust_z(x: np.ndarray) -> np.ndarray:
    z = np.full(x.size, np.nan); hist: list[float] = []
    for i in range(x.size):
        if np.isfinite(x[i]) and len(hist) >= MIN_W:
            h = np.array(hist[-BASE_W:]); hs = np.sort(h)[1:-1]
            sd = hs.std(ddof=1) / TF[h.size]
            if sd > 0:
                z[i] = (x[i] - np.median(h)) / sd
        if np.isfinite(x[i]):
            hist.append(float(x[i]))
    return z


def window_shift(M: np.ndarray) -> np.ndarray:
    """M: (n_windows, d) swarm window means in time order (NaN rows = unscored). Returns D(w)."""
    D = np.full(M.shape[0], np.nan); prev: list[np.ndarray] = []
    for i in range(M.shape[0]):
        if not np.isfinite(M[i, 0]):
            continue
        if len(prev) >= REF_W:
            r = np.mean(prev[-REF_W:], 0)
            D[i] = 1 - M[i] @ r / (np.linalg.norm(M[i]) * np.linalg.norm(r) + 1e-12)
        prev.append(M[i])
    return D


def skeleton(model: str):
    """Window table (pt_date, aday, win30, t0, regime, goal_no, n_agents) and swarm means of the real vectors."""
    B.CFG.update(data_version="fixed", model=model, dedupe="restate", trim=False)
    cal = B.calendar()
    days = cal.filter(~pl.col("holdout") & (pl.col("goal_no") > 0))
    assert not any(L.holdout_mask(days["pt_date"].to_list(), days["goal_no"].to_list()))
    g, V = B.window_vectors(days["pt_date"].to_list())
    assert not g["pt_date"].is_in(cal.filter(pl.col("holdout"))["pt_date"].implode()).any()
    mu = V.mean(0)
    X = V - mu; X /= np.clip(np.linalg.norm(X, axis=1, keepdims=True), 1e-9, None)
    g = g.with_row_index("row").join(days.select("pt_date", "aday", "win_start", "regime", "goal_no"), on="pt_date")
    w = (g.group_by("pt_date", "aday", "win30", "win_start", "regime", "goal_no")
         .agg(pl.col("row"), pl.col("agent"), pl.len().alias("n_agents")).sort("aday", "win30"))
    w = w.with_columns((pl.col("win_start") + pl.duration(minutes=30) * pl.col("win30").cast(pl.Int64)).alias("t0"))
    M = np.full((w.height, X.shape[1]), np.nan)
    for i, (rows, n) in enumerate(zip(w["row"].to_list(), w["n_agents"].to_list())):
        if n >= MIN_AG:
            M[i] = X[np.asarray(rows)].mean(0)
    return w, M, cal


# ---------------------------------------------------------------------------------------------- real-data readouts
def readouts(w: pl.DataFrame, z: np.ndarray, model: str) -> dict:
    sc = pl.read_parquet(L.OUT / "r1b" / ("fixed_bge_restate" if model == "bge_small" else "fixed_gte_restate") / "scores.parquet")
    ev = pl.read_parquet(L.OUT / "r1b" / "fixed_bge_restate" / "events.parquet").filter(~pl.col("holdout0"))
    kicks = pl.read_parquet(L.SH / "kicks.parquet").filter(pl.col("kind") == "goal_kickoff")
    kt = {r: t for t, r in kicks.select("t", "ref").iter_rows()}
    w = w.with_columns(pl.Series("z", z), pl.Series("alarm", np.nan_to_num(z, nan=-9) >= THR))
    byday = {d: g for (d,), g in w.group_by(["aday"])}
    adays = sorted(byday)
    placebo = set(sc.filter(pl.col("placebo"))["aday"].to_list())
    monday = set(sc.filter(pl.col("monday"))["aday"].to_list())

    def first2(a):
        g = byday.get(a)
        if g is None:
            return None
        g = byday[a].filter((pl.col("win30") <= 1) & pl.col("z").is_finite())
        return None if g.height == 0 else bool(g["alarm"].any())

    def last4(a):
        g = byday.get(a)
        if g is None:
            return None
        g = g.filter(pl.col("z").is_finite()).sort("win30").tail(4)
        return None if g.height == 0 else bool(g["alarm"].any())

    def prev_day(a):
        i = adays.index(a) if a in adays else None
        if i is None or i == 0:
            return None
        return adays[i - 1] if adays[i - 1] == a - 1 else None   # the previous calendar active day must be scored

    out = {"model": model, "n_windows_scored": int(np.isfinite(z).sum()), "per_window_far": None, "kickoffs": []}
    pw = w.filter(pl.col("aday").is_in(list(placebo)) & pl.col("z").is_finite())
    out["per_window_far"] = float(pw["alarm"].mean())
    out["per_window_far_after_first2"] = float(pw.filter(pl.col("win30") >= 2)["alarm"].mean())
    pf2 = [first2(a) for a in placebo]; pf2 = [x for x in pf2 if x is not None]
    pl4 = [last4(a) for a in placebo]; pl4 = [x for x in pl4 if x is not None]
    pf2m = [first2(a) for a in placebo & monday]; pf2m = [x for x in pf2m if x is not None]
    pf2o = [first2(a) for a in placebo - monday]; pf2o = [x for x in pf2o if x is not None]
    out["placebo_first2_rate"] = [float(np.mean(pf2)), len(pf2)]
    out["placebo_first2_rate_monday"] = [float(np.mean(pf2m)) if pf2m else None, len(pf2m)]
    out["placebo_first2_rate_other"] = [float(np.mean(pf2o)) if pf2o else None, len(pf2o)]
    out["placebo_last4_rate"] = [float(np.mean(pl4)), len(pl4)]
    # mean z by window index, placebo days
    out["placebo_z_by_win"] = {int(k): float(v) for k, v in pw.group_by("win30").agg(pl.col("z").mean()).sort("win30").iter_rows() if k <= 15}
    hits, leads, firsts, lags = [], [], [], []
    for r in ev.filter(pl.col("cls") == "goal").iter_rows(named=True):
        a = r["aday0"]
        f2 = first2(a)
        pd_ = prev_day(a)
        l4 = last4(pd_) if pd_ is not None else None
        g = byday.get(a)
        fa, lag = None, None
        if g is not None:
            al = g.filter(pl.col("alarm")).sort("win30")
            if al.height:
                fa = int(al["win30"][0])
                t_end = al["t0"][0] + dt.timedelta(minutes=30)
                if r["ref"] in kt:
                    lag = (t_end - kt[r["ref"]]).total_seconds() / 60
        rec = {"ref": r["ref"], "pt_date0": r["pt_date0"], "monday": a in monday, "first2": f2, "dm1_last4": l4,
               "first_alarm_win": fa, "lag_min_after_kickoff": lag,
               "z_by_win": {int(k): float(v) for k, v in g.select("win30", "z").iter_rows() if np.isfinite(v) and k <= 15} if g is not None else {}}
        out["kickoffs"].append(rec)
        if f2 is not None:
            hits.append(f2)
        if l4 is not None:
            leads.append(l4)
        if fa is not None:
            firsts.append(fa)
            if lag is not None:
                lags.append(lag)
    out["kickoff_first2_rate"] = [float(np.mean(hits)), len(hits)]
    out["kickoff_dm1_last4_rate"] = [float(np.mean(leads)) if leads else None, len(leads)]
    out["first_alarm_win_counts"] = {int(k): int(v) for k, v in zip(*np.unique(firsts, return_counts=True))} if firsts else {}
    out["share_first_alarm_win01"] = float(np.mean(np.array(firsts) <= 1)) if firsts else None
    out["lag_min_median_iqr"] = [float(np.median(lags)), float(np.percentile(lags, 25)), float(np.percentile(lags, 75)), len(lags)] if lags else None
    # AUC of max z in the first 2 windows, kickoff vs placebo days
    def f2max(a):
        g = byday.get(a)
        if g is None:
            return np.nan
        v = g.filter((pl.col("win30") <= 1) & pl.col("z").is_finite())["z"].to_numpy()
        return float(v.max()) if v.size else np.nan
    kp = np.array([f2max(r["aday0"]) for r in ev.filter(pl.col("cls") == "goal").iter_rows(named=True)])
    pp = np.array([f2max(a) for a in placebo])
    out["auc_first2_kickoff_vs_placebo"] = L.auc(kp, pp)
    out["auc_first2_ci"] = L.auc_ci(kp, pp, np.random.default_rng(L.SEED + 5), 1000)
    # room events
    rt = pl.read_parquet(L.SH / "rooms_timeline.parquet")
    rooms = {"focus_0805": (rt.filter(pl.col("room") == 15)["t_start"].min(), "mid-day"),
             "side_room_0724": (rt.filter(pl.col("room") == 14)["t_start"].min(), "mid-day"),
             "merge_0504": (rt.filter(pl.col("room") == 4)["t_start"].min(), "day start"),
             "split_0511": (rt.filter(pl.col("room").is_in([2, 3]) & (pl.col("t_start").dt.date() == dt.date(2026, 5, 11)))["t_start"].min(), "day start")}
    out["rooms"] = {}
    for k, (t, kind) in rooms.items():
        from zoneinfo import ZoneInfo
        pt = t.astimezone(ZoneInfo(B.PT)).date().isoformat()
        g = w.filter(pl.col("pt_date") == pt).sort("win30")
        if g.height == 0:
            out["rooms"][k] = {"note": "day not scored"}; continue
        wi = int((t - g["win_start"][0]).total_seconds() // 1800)
        near = g.filter((pl.col("win30") - wi).abs() <= 1)
        out["rooms"][k] = {"t": t.isoformat(), "kind": kind, "win_of_event": wi,
                           "z_near": {int(a): (float(b) if np.isfinite(b) else None) for a, b in near.select("win30", "z").iter_rows()},
                           "alarm_within_1": bool(near["alarm"].any()),
                           "alarm_first2": bool(g.filter(pl.col("win30") <= 1)["alarm"].any()),
                           "z_day": {int(a): (float(b) if np.isfinite(b) else None) for a, b in g.select("win30", "z").iter_rows()}}
    return out


# ---------------------------------------------------------------------------------------------- synthetic
def synthetic(w: pl.DataFrame, runs: int = 10) -> dict:
    lam = np.exp(-np.arange(32) / 4.0); lam /= lam.sum()
    ev = pl.read_parquet(L.OUT / "r1b" / "fixed_bge_restate" / "events.parquet").filter(~pl.col("holdout0") & (pl.col("cls") == "goal"))
    kick_days = set(ev["aday0"].to_list())
    adays = np.array(sorted(set(w["aday"].to_list())))
    rows_day = w["aday"].to_numpy(); win = w["win30"].to_numpy(); nag = w["n_agents"].to_numpy()
    agents = w["agent"].to_list()
    res = {"day_start": [], "mid": [], "far_clean": [], "far_first2_nonswitch_days": []}
    for run in range(runs):
        rng = np.random.default_rng([L.SEED, 77, run])
        others = [a for a in adays if a not in kick_days]
        mid_days = set(rng.choice(others, 12, replace=False).tolist())
        mid_win = {}
        for a in mid_days:
            nw = win[rows_day == a].max() + 1
            mid_win[a] = int(rng.integers(2, max(3, nw - 1)))
        style = {ag: rng.normal(size=32) * np.sqrt(lam) * 1.0 for ag in range(64)}
        g = rng.normal(size=32) * np.sqrt(lam); g /= np.linalg.norm(g)
        cur_day, dayfield = None, None
        switch_rows = []
        M = np.full((w.height, 32), np.nan)
        for i in range(w.height):
            a = int(rows_day[i])
            if a != cur_day:
                cur_day = a
                dayfield = rng.normal(size=32) * np.sqrt(lam) * 0.4
                if a in kick_days:
                    g = rng.normal(size=32) * np.sqrt(lam); g /= np.linalg.norm(g); switch_rows.append(("day_start", i))
            if a in mid_win and win[i] == mid_win[a] and not any(s[1] == i for s in switch_rows):
                g = rng.normal(size=32) * np.sqrt(lam); g /= np.linalg.norm(g); switch_rows.append(("mid", i))
            if nag[i] < MIN_AG:
                continue
            u = rng.normal(size=32) * np.sqrt(lam) * 0.6
            vs = []
            for ag in agents[i]:
                v = g + style[int(ag) % 64] + dayfield + u + rng.normal(size=32) * np.sqrt(lam) * 1.2
                vs.append(v / np.linalg.norm(v))
            M[i] = np.mean(vs, 0)
        z = robust_z(window_shift(M))
        al = np.nan_to_num(z, nan=-9) >= THR
        near = np.zeros(w.height, bool)
        sw_days = set()
        for kind, i in switch_rows:
            ok = [j for j in range(i - 1, min(w.height, i + 2)) if rows_day[j] == rows_day[i] or j == i - 1]
            res[kind].append(bool(al[ok].any()) if np.isfinite(z[ok]).any() else None)
            near[max(0, i - 1):min(w.height, i + 5)] = True
            sw_days.add(int(rows_day[i]))
        clean = ~near & np.isfinite(z)
        res["far_clean"].append(float(al[clean].mean()))
        f2 = [(rows_day == a) & (win <= 1) & np.isfinite(z) for a in adays if a not in sw_days]
        f2r = [bool(al[m].any()) for m in f2 if m.any()]
        res["far_first2_nonswitch_days"].append(float(np.mean(f2r)))
    return {"runs": runs, "hit_day_start": float(np.mean([x for x in res["day_start"] if x is not None])),
            "hit_mid": float(np.mean([x for x in res["mid"] if x is not None])),
            "n_mid": len(res["mid"]), "per_window_far_clean": float(np.mean(res["far_clean"])),
            "first2_far_nonswitch_days": float(np.mean(res["far_first2_nonswitch_days"]))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="bge_small", choices=["bge_small", "gte_modernbert"])
    ap.add_argument("--synthetic", action="store_true")
    a = ap.parse_args()
    R2.mkdir(parents=True, exist_ok=True)
    w, M, cal = skeleton(a.model)
    if a.synthetic:
        s = synthetic(w)
        (R2 / "intraday_synthetic.json").write_text(json.dumps(s, indent=1))
        print(json.dumps(s, indent=1))
        return
    z = robust_z(window_shift(M))
    out = readouts(w, z, a.model)
    tag = a.model.split("_")[0]
    w.select("pt_date", "aday", "win30", "t0", "regime", "goal_no", "n_agents").with_columns(pl.Series("z", z)) \
        .write_parquet(R2 / f"intraday_{tag}.parquet", compression="zstd")
    (R2 / f"intraday_{tag}.json").write_text(json.dumps(out, indent=1, default=str))
    L.write_provenance("hypotheses/H36-reorganization-alarm/analysis/r2_intraday.py",
                       ["embeddings/agent_win30 (restate dedupe)", "statement_flags", "calendar", "kicks", "rooms_timeline"],
                       {"model": a.model, "ref_windows": REF_W, "base_windows": BASE_W, "thr": THR, "min_agents": MIN_AG},
                       path=R2 / "_provenance.json")
    print(json.dumps({k: v for k, v in out.items() if k not in ("kickoffs", "rooms", "placebo_z_by_win")}, indent=1, default=str))
    for k, v in out["rooms"].items():
        print(k, {kk: vv for kk, vv in v.items() if kk != "z_day"})


if __name__ == "__main__":
    main()
