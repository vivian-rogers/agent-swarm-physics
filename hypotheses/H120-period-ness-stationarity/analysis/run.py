"""H120 round 1 (exploratory, non-holdout): drift of kinetic Ising J and of EP inside long windows.

Usage: uv run python hypotheses/H120-period-ness-stationarity/analysis/run.py [--perm 1000] [--perm-ep 300]
Writes data/processed/H120-period-ness-stationarity/results/results.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h120lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import git_commit  # noqa: E402

WINDOWS = ("4c", "6b", "8", "13", "19a", "27", "38a", "51g", "G38", "51main")
BOUNDARIES = {"G38": {"NE17 (04-14)": "2026-04-14", "join Opus 4.7 (04-17)": "2026-04-17", "NE18 (04-20)": "2026-04-20",
                      "join Kimi K2.6 (04-22)": "2026-04-22"},
              "51main": {"08-05 (#focus, bookends stop)": "2026-08-05", "08-24 (merge; nudges stopped 08-21)": "2026-08-24",
                         "07-17 (join Kimi K3)": "2026-07-17", "07-24 (join Opus 5)": "2026-07-24",
                         "07-29 (NE38)": "2026-07-29", "09-03 (NE33)": "2026-09-03"}}
PRIMARY_BOUNDARY = {"G38": ["NE17 (04-14)"], "51main": ["08-05 (#focus, bookends stop)", "08-24 (merge; nudges stopped 08-21)"]}
RES = L.DATA / "results"


def stratified_splits(weekday, first_idx, max_n=2000, rng=None):
    """Weekday-stratified splits with the same per-weekday counts in the first half as the contiguous split."""
    n = len(weekday)
    groups = {}
    for i, w in enumerate(weekday):
        groups.setdefault(w, []).append(i)
    k = {w: sum(1 for i in first_idx if weekday[i] == w) for w in groups}
    combos = [list(itertools.combinations(groups[w], k[w])) for w in groups]
    total = int(np.prod([len(c) for c in combos]))
    out = []
    if total <= max_n:
        for pick in itertools.product(*combos):
            out.append(L.split_tau(n, [i for g in pick for i in g]))
    else:
        for _ in range(max_n):
            out.append(L.split_tau(n, [i for c in combos for i in c[rng.integers(len(c))]]))
    return out, total


def weekly(F, days, rng, B=200):
    import datetime as _dt
    wk = np.array([_dt.date.fromisoformat(d).isocalendar()[1] for d in days])
    weeks = sorted(set(wk.tolist()))
    N = F["N"]
    prof = []
    for w in weeks:
        idx = np.flatnonzero(wk == w)
        if len(idx) < 2:
            continue
        th = L.onestep_window(F, idx)
        bs = []
        for _ in range(B):
            bs.append(L.onestep_window(F, rng.choice(idx, size=len(idx), replace=True))[:, 1:1 + N])
        bs = np.array(bs)
        prof.append({"week": int(w), "n_days": int(len(idx)), "J": th[:, 1:1 + N],
                     "lo": np.percentile(bs, 2.5, axis=0), "hi": np.percentile(bs, 97.5, axis=0)})
    if len(prof) < 2:
        return {"n_weeks": len(prof)}
    lo = np.max([p["lo"] for p in prof], axis=0)
    hi = np.min([p["hi"] for p in prof], axis=0)
    overlap = float(np.mean(lo <= hi))
    return {"n_weeks": len(prof), "weeks": [p["week"] for p in prof], "days": [p["n_days"] for p in prof],
            "share_J_all_weeks_overlap": overlap,
            "mean_abs_J_offdiag": [float(np.abs(p["J"][~np.eye(N, dtype=bool)]).mean()) for p in prof],
            "mean_J_diag": [float(np.diag(p["J"]).mean()) for p in prof]}


def analyse(wname, ch, n_perm, n_perm_ep, rng, drop_first=False):
    win = L.load_window(wname, ch)
    des = L.design(win, drop_first_day=drop_first)
    F = L.fit(des)
    days = [win["days"][d] for d in des["days"]]
    n = len(days)
    nulls = L.random_splits(n, n_perm, rng)
    t1 = L.perm_test(F, L.contiguous_tau(n), nulls)
    perms = [L.trend_tau(n)[rng.permutation(n)] for _ in range(n_perm)]
    t2 = L.perm_test(F, L.trend_tau(n), perms)
    stats, block = L.ep_day_stats(win, drop_first_day=drop_first)
    t3 = L.ep_split_test(stats, block, list(range(n // 2)), nulls[:n_perm_ep], n)
    ep_all = L.ep_of_days(stats, block, list(range(n)))
    # EP CI: day bootstrap (copies of a day kept in one fold by construction of ep_of_days on unique days -> resample
    # weights by repeating days in the fold sums)
    ep_bs = []
    for _ in range(100):
        pick = rng.choice(n, size=n, replace=True)
        st2 = [stats[i] for i in pick]
        ep_bs.append(L.ep_of_days(st2, block, list(range(n)), fold_of=[int(i) for i in pick]))
    out = {"window": wname, "channel": ch, "n_days": n, "n_core": F["N"], "days": days,
           "minutes": int(sum(len(x) for x in des["X"])),
           "T1": t1, "T2": t2, "T3": t3,
           "EP_all": float(ep_all), "EP_all_ci": [float(np.percentile(ep_bs, 2.5)), float(np.percentile(ep_bs, 97.5))],
           "EP_halves": [float(L.ep_of_days(stats, block, list(range(n // 2)))),
                         float(L.ep_of_days(stats, block, list(range(n // 2, n))))],
           "z_per_day": float(t1["z"] / n),
           "J_offdiag_sd": float(np.std(F["theta"][:, 1:1 + F["N"]][~np.eye(F["N"], dtype=bool)])),
           "J_diag_mean": float(np.mean(np.diag(F["theta"][:, 1:1 + F["N"]])))}
    if not drop_first:
        strat, total = stratified_splits(win["weekday"][des["days"]], list(range(n // 2)), rng=rng)
        out["T1_strat"] = L.perm_test(F, L.contiguous_tau(n), strat) if total >= 20 else {"n_distinct": total}
        out["T1_strat_n_distinct"] = total
        out["weekly"] = weekly(F, days, rng)
        if wname in BOUNDARIES:
            out["boundaries"] = {}
            for lab, d in BOUNDARIES[wname].items():
                if d in days:
                    br = L.boundary_rank(F, n, days.index(d))
                    out["boundaries"][lab] = {"rank_frac": br["rank_frac"], "W": br["W"], "n": br["n_boundaries"]}
            if "boundaries" in out and out["boundaries"]:
                br = L.boundary_rank(F, n, days.index(next(iter(BOUNDARIES[wname].values()))))
                out["boundary_W_all"] = {days[b]: float(v) for b, v in br["all"].items()}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=1000)
    ap.add_argument("--perm-ep", type=int, default=300)
    ap.add_argument("--windows", nargs="*", default=list(WINDOWS))
    a = ap.parse_args()
    rng = np.random.default_rng(20261004)
    RES.mkdir(parents=True, exist_ok=True)
    path = RES / "results.json"
    out = json.loads(path.read_text()) if path.exists() else {"windows": {}}
    out["built_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    out["git_commit"] = git_commit()
    for w in a.windows:
        rec = {}
        for ch in ("act", "talk"):
            big = w in ("51main", "51g")
            rec[ch] = analyse(w, ch, a.perm, a.perm_ep if not big else max(100, a.perm_ep // 3), rng)
            rec[ch + "_dropfirst"] = analyse(w, ch, 300, 100, rng, drop_first=True)
            print(w, ch, "T1 p", round(rec[ch]["T1"]["p"], 3), "R", round(rec[ch]["T1"]["R"], 2),
                  "T2 p", round(rec[ch]["T2"]["p"], 3), "T3 p", round(rec[ch]["T3"]["p"], 3), flush=True)
        ps = [rec[ch][t]["p"] for ch in ("act", "talk") for t in ("T1", "T2", "T3")]
        rec["holm"] = dict(zip([f"{ch}_{t}" for ch in ("act", "talk") for t in ("T1", "T2", "T3")],
                               L.holm(ps).tolist()))
        out["windows"][w] = rec
        path.write_text(json.dumps(out, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o)))
    print("written", path)


if __name__ == "__main__":
    main()
