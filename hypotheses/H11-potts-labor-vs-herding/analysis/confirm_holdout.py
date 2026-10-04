"""H11 confirmatory test on the LOCKED HOLDOUT. Written in round 1 (2026-10-03); NOT RUN.

Targets (chosen 2026-10-03 from hypotheses/holdout.json, before round 1 results):
  #22  free week (F)                      -> predicted class FM-free
  #28  quiz build + promotion (C)         -> predicted class AF
  #45  Follow your leader, modules (C)    -> predicted class AF   (regime III, room blocks)

The decision rules C1-C3 (FROZEN dict and verdict()) were frozen on 2026-10-03 after exploratory round 1 (see the
card, "Confirmatory prediction (frozen)") and must not be edited once any holdout data has been read.

Usage
  --dry-run   run the identical pipeline on non-holdout stand-ins (#31 for #22, #25 for #28, #38 for #45),
              using the already-built exploratory labels; never touches holdout data.
  --confirm --i-understand-this-uses-the-locked-holdout
              build labels for the holdout targets into data/processed/H11-potts-labor-vs-herding/confirm/
              (scheme/build.py --allow-holdout) and apply the frozen rule. Needs Vivian's sign-off.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h11common as HC  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potts_core as P  # noqa: E402
from h11data import load_period, blocks_ge  # noqa: E402

TARGETS = {22: "FM-free", 28: "AF", 45: "AF"}
STANDINS = {22: 31, 28: 25, 45: 38}

FROZEN = {
    "frozen_on": "2026-10-03 (after exploratory round 1; before any holdout data was read)",
    "W": 30, "q_max": 8, "min_share": 0.02, "strict_how": ["url", "output", "bare"], "min_blocks3": 15,
    "n_null": 199, "seed": 20261003, "own_threshold": 0.5,
    "C1_original_H11": "every target: sign(βJ_CW) = class sign (FM-free > 0; AF < 0) with |t| > t_crit(D-1)",
    "C2_round1_pattern": ("ownership < 0.5 (shared artifacts): βJ_CW > 0 with |t| > t_crit AND z_N2 >= 2 AND z_local1 >= 2; "
                          "ownership >= 0.5 (own artifacts): z_N2 < 2. Holds iff true for every tested target; "
                          "refuted if any shared-artifact target has z_N2 < 0"),
    "C3_specificity": "action-class βJ_CW not significantly negative (t > -t_crit) in every target",
}


def ownership(df):
    """Share of labeled agent-windows on projects one agent dominates (>= 80% of the project's agent-windows)."""
    import polars as pl
    c = df.group_by("project", "agent").agg(pl.len().alias("n"))
    t = c.group_by("project").agg(pl.col("n").sum().alias("tot"), pl.col("n").max().alias("top"))
    t = t.with_columns((pl.col("top") / pl.col("tot")).alias("own"))
    return float(t.filter(pl.col("own") >= 0.8)["tot"].sum() / t["tot"].sum())


def run_target(g, base, n_null, rng):
    s, df = load_period(g, base=base)
    out = dict(goal=g, n_obs=int(len(s.label)), blocks3=blocks_ge(s, 3), q=int(s.S - 1), n_days=int(s.n_days))
    if out["blocks3"] < FROZEN["min_blocks3"]:
        out["tested"] = False
        return out
    out["tested"] = True
    full, se, jk = P.jackknife_cw(s, "period")
    from scipy import stats
    dfree = max(len(jk) - 1, 1)
    t = full["bj"] / se if se and se > 0 else np.nan
    out.update(bj_cw=full["bj"], se_cw=se, t_cw=t, tcrit=float(stats.t.ppf(0.975, dfree)))
    n1 = np.array([P.fit_cw(s.with_labels(P.null_labels(s, "perm", rng)), "period")["bj"] for _ in range(n_null)])
    out["z_cw_N1"] = float((full["bj"] - n1.mean()) / n1.std(ddof=1))
    bj_pl = P.fit_pl(s, "agent")["bj"]
    n2 = np.array([P.fit_pl(P.shift_snap(s, rng), "agent")["bj"] for _ in range(n_null)])
    out.update(bj_pl=bj_pl, z_pl_N2=float((bj_pl - n2.mean()) / n2.std(ddof=1)))
    n_loc = np.array([P.fit_pl(P.shift_snap(s, rng, max_shift=1), "agent")["bj"] for _ in range(n_null)])
    out["z_pl_local1"] = float((bj_pl - n_loc.mean()) / n_loc.std(ddof=1))
    out["ownership"] = ownership(df)
    sa, _ = load_period(g, state="action", base=base)
    fa, sea, _ = P.jackknife_cw(sa, "period")
    out.update(act_bj_cw=fa["bj"], act_t_cw=fa["bj"] / sea if sea else np.nan)
    return out


def verdict(o, cls):
    """Frozen per-target rules C1-C3 (see FROZEN)."""
    sig = abs(o["t_cw"]) > o["tcrit"] if np.isfinite(o["t_cw"]) else False
    want = 1 if cls.startswith("FM") else -1
    c1 = bool(np.sign(o["bj_cw"]) == want and sig)
    if o["ownership"] < FROZEN["own_threshold"]:
        c2 = bool(o["bj_cw"] > 0 and sig and o["z_pl_N2"] >= 2 and o["z_pl_local1"] >= 2)
        c2_refute = bool(o["z_pl_N2"] < 0)
    else:
        c2 = bool(o["z_pl_N2"] < 2)
        c2_refute = False
    c3 = bool(o["act_t_cw"] > -o["tcrit"]) if np.isfinite(o["act_t_cw"]) else True
    return dict(C1=c1, C2=c2, C2_refute=c2_refute, C3=c3)


def overall(results):
    tested = [r for r in results if r.get("tested")]
    if not tested:
        return "no target testable"
    v = [r["verdict"] for r in tested]
    c1 = "C1 (original H11 sign-by-mode) CONFIRMED" if all(x["C1"] for x in v) else "C1 (original H11 sign-by-mode) NOT confirmed"
    if any(x["C2_refute"] for x in v):
        c2 = "C2 (round-1 pattern: herding on shared artifacts) REFUTED"
    elif all(x["C2"] for x in v):
        c2 = "C2 (round-1 pattern) CONFIRMED"
    else:
        c2 = "C2 (round-1 pattern) inconclusive"
    c3 = "C3 specificity holds" if all(x["C3"] for x in v) else "C3 specificity fails"
    return f"{c1}; {c2}; {c3}; tested {len(tested)}/{len(results)} targets"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.confirm and not a.ack:
        raise SystemExit("refusing: --confirm also needs --i-understand-this-uses-the-locked-holdout")
    if not a.dry_run and not (a.confirm and a.ack):
        raise SystemExit("refusing: pass --dry-run (non-holdout stand-ins) or "
                         "--confirm --i-understand-this-uses-the-locked-holdout (locked holdout; needs sign-off)")
    rng = np.random.default_rng(FROZEN["seed"])
    held = HC.held_goals()
    results = []
    if a.dry_run:
        for g, cls in TARGETS.items():
            sg = STANDINS[g]
            assert sg not in held, "stand-in must be non-holdout"
            o = run_target(sg, HC.OUT, 49, rng)
            o.update(target=g, standin=sg, cls=cls, verdict=verdict(o, cls) if o.get("tested") else "n/a")
            results.append(o)
        outf = HC.OUT / "confirm_dryrun.json"
    else:
        assert set(TARGETS) <= held, "confirm targets must be holdout periods"
        cdir = HC.OUT / "confirm"
        subprocess.run([sys.executable, str(HC.HYP / "scheme/build.py"), "--allow-holdout", "--out", str(cdir),
                        "--goals", *map(str, TARGETS)], check=True)
        for g, cls in TARGETS.items():
            o = run_target(g, cdir, FROZEN["n_null"], rng)
            o.update(target=g, cls=cls, verdict=verdict(o, cls) if o.get("tested") else "n/a")
            results.append(o)
        outf = cdir / "confirm_results.json"
    ov = overall(results)
    rep = dict(mode="dry-run" if a.dry_run else "CONFIRM (locked holdout)", run_at=dt.datetime.now(dt.timezone.utc).isoformat(),
               frozen=FROZEN, results=results, overall=ov)
    outf.parent.mkdir(parents=True, exist_ok=True)
    outf.write_text(json.dumps(rep, indent=1, default=lambda x: float(x) if hasattr(x, "item") else str(x)))
    for o in results:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in o.items()})
    print("overall:", ov, "->", outf)


if __name__ == "__main__":
    main()
