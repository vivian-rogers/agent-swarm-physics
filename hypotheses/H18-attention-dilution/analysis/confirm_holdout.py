"""H18 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-03 after exploratory round 1. NOT RUN.

  uv run python hypotheses/H18-attention-dilution/analysis/confirm_holdout.py --dry-run
  uv run python hypotheses/H18-attention-dilution/analysis/confirm_holdout.py --confirm --i-understand-this-uses-the-locked-holdout

Without both confirm flags the script refuses to touch held-out days. --dry-run runs the identical pipeline on
non-holdout stand-ins (asserting that every stand-in day is outside the holdout) and writes to confirm_dryrun/.

Targets and pre-registered predictions: see PREDICTIONS below and the card, section "Confirmatory predictions".
Holdout reuse (hypotheses/holdout.md, 2026-10-03 policy): #45 was used by H02 (activity-timing couplings), #46-#50 by
H04 (hours / Hawkes), the NE15 pre-split days by H05 (activity couplings). H18's observable (mention responses vs the
pending count) is a different statistic that nobody has computed on those days; the reuse must be disclosed in both
cards and LOG.md, and this script plus the card must be committed before the run.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

OUT = ROOT / "data/processed/H18-attention-dilution"

# ----------------------------------------------------------------------------------------------- targets
# name: (goal, (start, end) PT end-exclusive, role); holdout ranges
TARGETS = {
    "T51tail": (51, ("2026-09-07", "2026-09-21"), "C1, C3: largest N (up to 32), 8 h days"),
    "T45": (45, ("2026-06-01", "2026-06-08"), "C2: regime III, 18 agents, two rooms"),
    "T46": (46, ("2026-06-08", "2026-06-15"), "C2"),
    "T47": (47, ("2026-06-15", "2026-06-22"), "C2"),
    "T49": (49, ("2026-06-23", "2026-06-29"), "C2"),
    "T50": (50, ("2026-06-29", "2026-07-06"), "C2"),
    "T28": (28, ("2026-01-26", "2026-02-02"), "C4: regime I"),
    "T29": (29, ("2026-02-02", "2026-02-09"), "C4: regime I"),
    "T34pre": (34, ("2026-03-09", "2026-03-14"), "C5: NE15 pre-split side (everyone outside #voted-out in #general)"),
}
# non-holdout stand-ins for --dry-run (same code path; nothing held out is read)
STANDINS = {
    "T51tail": (51, ("2026-08-24", "2026-09-05")),
    "T45": (41, ("2026-05-11", "2026-05-18")),
    "T46": (42, ("2026-05-18", "2026-05-25")),
    "T47": (44, ("2026-05-26", "2026-06-01")),
    "T49": (39, ("2026-04-27", "2026-05-04")),
    "T50": (40, ("2026-05-04", "2026-05-11")),
    "T28": (30, ("2026-02-09", "2026-02-16")),
    "T29": (31, ("2026-02-16", "2026-02-23")),
    "T34pre": (39, ("2026-04-27", "2026-05-04")),
}

# ----------------------------------------------------------------------------------------------- predictions
# Filled 2026-10-03 from exploratory round 1 (see the card). Each is evaluated mechanically below.
PREDICTIONS = {
    "C1": "T51tail: D1 beta-hat CI excludes 0 and beta-hat lies in [0.35, 0.85]; the within-day-block CV winner is "
          "M_sat or M_rec (not M_const, not M_inv): saturating/recency, not a literal 1/k",
    "C2": "Regime-III holdout periods T45-T50 (each >= 300 units): beta-hat CI excludes 0 in >= 4 of 5; pooled "
          "(random-effects) beta-hat in [0.45, 0.95]; M_const is never the effective CV winner",
    "C3": "T51tail and T45-T50: the per-pair addressing rate falls with mean room size across these periods plus the "
          "exploratory periods' fitted p-bar (Spearman rho < 0 over the 6 new points vs N_room), and the senders-addressed-"
          "per-turn B-hat varies less than p-bar (CV(B-hat) < CV(p-bar))",
    "C4": "Regime-I holdout T28, T29: beta-hat in [0.3, 0.8] with CI excluding 0 in both",
    "C5": "NE15 before/after (T34pre vs exploratory G35, the agents present on both sides): for agents whose room "
          "shrank (now in #best), the per-pair addressing rate rises (post/pre > 1) and S per talk turn changes by "
          "< 50%; for #rest agents p-bar changes by less than for #best agents",
    "C6": "Timer-wake D2 in T51tail: beta-hat_D2 > 0 with CI excluding 0 (exploratory #51 had the only well-powered D2)",
}


def build(name, g, dates, holdout: bool):
    from build import Shared, build_period, write_period
    sh = build.__globals__.get("_SH")
    if sh is None:
        sh = Shared()
        build.__globals__["_SH"] = sh
    res = build_period(sh, g, allow_holdout=holdout, with_content=False, dates=dates, only_holdout=holdout)
    if res is None:
        return None
    if not holdout:
        hm = holdout_mask(res["days"], [g] * len(res["days"]))
        assert not any(hm), f"stand-in {name} touches held-out days"
    sub = ("confirm/" if holdout else "confirm_dryrun/") + name
    write_period(g, res, sub=sub)
    return OUT / sub


def evaluate(F, base):
    from summarize_lib import d1_checks
    from fit_periods import dl_pool
    from scipy.stats import spearmanr
    R = {}

    def beta(n):
        f = F.get(n)
        if not f or f["D1"]["n_units"] < 300:
            return None
        c = d1_checks(f)
        return c

    c1 = beta("T51tail")
    if c1:
        R["C1"] = dict(beta=c1["beta"], lo=c1["lo"], hi=c1["hi"], eff=c1["eff"],
                       pass_=bool(c1["lo"] and c1["lo"] > 0 and 0.35 <= c1["beta"] <= 0.85 and
                                  c1["eff"] in ("sat", "sat~inv", "rec")))
    r3 = [n for n in ("T45", "T46", "T47", "T49", "T50") if beta(n)]
    if r3:
        excl = sum(1 for n in r3 if beta(n)["lo"] and beta(n)["lo"] > 0)
        est = [F[n]["D1"]["beta"] for n in r3]
        se = [F[n]["D1"]["boot"]["beta"]["sd"] for n in r3]
        po = dl_pool(est, se)
        R["C2"] = dict(n=len(r3), n_excl0=excl, pooled=po, effs={n: beta(n)["eff"] for n in r3},
                       pass_=bool(excl >= min(4, len(r3)) and po and 0.45 <= po["mean"] <= 0.95 and
                                  all(beta(n)["eff"] not in ("const", "sat~const", "rec~const") for n in r3)))
    pts = [n for n in ("T51tail", "T45", "T46", "T47", "T49", "T50") if n in F]
    if len(pts) >= 4:
        N = [F[n]["n_room_mean"] for n in pts]
        p = [F[n]["p_bar"] for n in pts]
        B = [F[n]["B_hat"] for n in pts]
        rho = spearmanr(N, p).statistic
        R["C3"] = dict(rho_p_N=float(rho), cv_p=float(np.std(p) / np.mean(p)), cv_B=float(np.std(B) / np.mean(B)),
                       pass_=bool(rho < 0 and np.std(B) / np.mean(B) < np.std(p) / np.mean(p)))
    r1 = [n for n in ("T28", "T29") if beta(n)]
    if r1:
        R["C4"] = dict(betas={n: beta(n)["beta"] for n in r1},
                       pass_=bool(len(r1) == 2 and all(0.3 <= beta(n)["beta"] <= 0.8 and beta(n)["lo"] > 0 for n in r1)))
    if "T34pre" in F and (OUT / "G35/talks.parquet").exists():
        R["C5"] = ne15_before_after(base / "T34pre", OUT / "G35")
    f51 = F.get("T51tail")
    if f51 and (f51.get("D2") or {}).get("boot"):
        b = f51["D2"]["boot"]["beta"]
        R["C6"] = dict(beta=f51["D2"]["beta"], lo=b["lo"], hi=b["hi"], pass_=bool(b["lo"] > 0))
    return R


def ne15_before_after(pre_dir, post_dir):
    from h18lib import Units
    best_room = 2
    out = {}
    pre_t = pl.read_parquet(pre_dir / "talks.parquet")
    post_t = pl.read_parquet(post_dir / "talks.parquet")
    Upre = Units(pre_t, pl.read_parquet(pre_dir / "pending.parquet"), "talk_id")
    Upost = Units(post_t, pl.read_parquet(post_dir / "pending.parquet"), "talk_id")
    post_room = post_t.group_by("agent").agg(pl.col("room").mode().first())
    both = set(pre_t["agent"].unique().to_list()) & set(post_t["agent"].unique().to_list())
    rows = []
    for a in sorted(both):
        rm = post_room.filter(pl.col("agent") == a)["room"]
        grp = "best" if len(rm) and rm[0] == best_room else "rest"
        u0 = Upre.df.filter(pl.col("agent") == a)
        u1 = Upost.df.filter(pl.col("agent") == a)
        if u0.height < 20 or u1.height < 20:
            continue
        S0 = u0.group_by("talk_id").agg(pl.col("r").sum())["r"].mean()
        S1 = u1.group_by("talk_id").agg(pl.col("r").sum())["r"].mean()
        rows.append(dict(agent=a, group=grp, p_ratio=u1["r"].cast(pl.Float64).mean() / max(1e-9, u0["r"].cast(pl.Float64).mean()),
                         S_ratio=S1 / max(1e-9, S0)))
    bst = [r for r in rows if r["group"] == "best"]
    rst = [r for r in rows if r["group"] == "rest"]
    out["rows"] = rows
    if bst and rst:
        out["pass_"] = bool(np.median([r["p_ratio"] for r in bst]) > 1 and
                            all(0.5 <= r["S_ratio"] <= 1.5 for r in bst) and
                            abs(np.log(np.median([r["p_ratio"] for r in rst]))) < abs(np.log(np.median([r["p_ratio"] for r in bst]))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--only", default=None, help="comma-separated target names")
    a = ap.parse_args()
    if a.dry_run and (a.confirm or a.ack):
        sys.exit("choose either --dry-run or --confirm, not both")
    if not a.dry_run and not (a.confirm and a.ack):
        sys.exit("REFUSED: this script reads the locked holdout. Pass --confirm --i-understand-this-uses-the-locked-holdout "
                 "(only after the card's confirmatory predictions and this script are committed), or --dry-run.")
    holdout = not a.dry_run
    from fit_periods import run
    base = OUT / ("confirm" if holdout else "confirm_dryrun")
    names = a.only.split(",") if a.only else list(TARGETS)
    F = {}
    for name in names:
        g, dates = (TARGETS[name][0], TARGETS[name][1]) if holdout else STANDINS[name]
        d = build(name, g, dates, holdout)
        if d is None:
            print(name, "no data")
            continue
        two_room = g in (35, 36, 37, 38, 39, 41, 42, 44, 45, 46, 47, 49, 50)
        B = a.boot if name != "T51tail" else min(a.boot, 60)
        F[name] = run(name, B if holdout else min(B, 20), base=base, two_room=two_room)
    R = evaluate(F, base)
    R["_meta"] = dict(mode="CONFIRMATORY (holdout)" if holdout else "dry-run (non-holdout stand-ins)",
                      run_at=dt.datetime.now(dt.timezone.utc).isoformat(), predictions=PREDICTIONS)
    (base / "results.json").write_text(json.dumps(R, indent=1, default=float))
    for k, v in R.items():
        if k != "_meta":
            print(k, "PASS" if v.get("pass_") else "FAIL", {kk: vv for kk, vv in v.items() if kk not in ("rows", "pooled")})


if __name__ == "__main__":
    main()
