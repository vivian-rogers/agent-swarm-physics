"""H73 confirmatory test on the locked holdout. WRITTEN 2026-10-04 after round 1, NOT RUN on the holdout.

  uv run python hypotheses/H73-style-three-components/analysis/confirm.py --dry-run
      runs the full pipeline on non-holdout stand-ins (G38, G41, G13 as periods; regime-III #51 07-06..08-31 as the
      NE41 stand-in). Safe: exploration data only.
  uv run python hypotheses/H73-style-three-components/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      rebuilds the message table with held-out rows in memory, applying the FROZEN round-1 standardization and
      type-control coefficients (data/processed/H73-style-three-components/style_standardization.json), writes
      confirm/confirm_sealed.json (SHA-256 of the frozen predictions) BEFORE reading any held-out row, then scores.
      Refuses to run without BOTH flags, and checks the holdout ledger first (infra/shared/holdout_ledger.check).

Round 1 picture under test: style = agent constant + a small context component + agent-day jitter. The agent constant
dominates (F3 >= 0.57 of the non-day systematic variance), the context component exists but removing it does not help
attribution, the forced-erasure jump is mostly a directionless excursion (small beta, T_s > 1/2), and in regime III
the context component follows received chat (conversation state) more than own fill.

Targets (locked holdout):
  T1 held-out goal periods with eligible data: #1, #9, #14, #15, #22, #28, #29 (regime I), #32, #34 (regime II),
     #43, #45, #46, #47, #48, #49, #50 (regime III); the #51 tail (09-07 -> 09-21) as one more period.
  T2 NE41 on held-out regime-III days (#43, #45-#50, #51 tail).
  T3 NE30 (03-05 -> 03-16): Gemini 3.1 Pro (agent 22) vs Gemini 3 Pro (agent 15).
Frozen predictions:
  C1 (T1) F3 >= 0.57 in >= 2/3 of eligible held-out periods and median F3 >= 0.57.
  C2 (T1) the agent constant has the largest unique share in >= 80% of them; u_C > 0 (permutation p < 0.05) in
     >= 2/3 of those with >= 500 computer-use messages.
  C3 (T1) no material attribution gain from the agent-specific context model: period-mean Delta_c < +0.02 and fewer
     than 2/3 of periods positive.
  C4 (T2) forced erasures: beta < 0.6 with predicted ||dx_hat||^2 < 5% of observed ||dx||^2, and T_s raw >= 0.53 with
     agent-cluster CI lower bound > 0.5.
  C5 (T1, regime III) received fill beats own fill: median u_recv - u_own > 0.
  C6 (T3, descriptive) agent 22's style centroid on its first <= 5 eligible days has agent 15 among its 2 nearest
     centroids (agents present in the window).
  Overall: the round-1 picture is CONFIRMED if C1, C2, C3 and C4 pass.
Reuse disclosure (hypotheses/holdout.md policy): the #51 tail is targeted by unrun scripts of H14, H18, H20, H22,
H34 and H46 (H46 uses the same style features with a different statistic: boundary displacement percentiles and NE41
gap-matched percentiles; H73's C4 T_s overlaps H46's C3 estimator family and must be disclosed if both run). #45 by H02
(run, activity timing) and H23 (unrun, content copying). Disclose in both cards and LOG.md if run.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h73lib as L  # noqa: E402

OUTD = L.DATA / "confirm"
PRED = {"C1": "F3 >= 0.57 in >= 2/3 of held-out periods; median >= 0.57",
        "C2": "u_A largest in >= 80%; u_C p < 0.05 in >= 2/3 of n_cu >= 500 periods",
        "C3": "mean Delta_c < +0.02 and < 2/3 positive",
        "C4": "NE41 forced beta < 0.6, pred/obs norm < 0.05, T_s raw >= 0.53 with lo > 0.5",
        "C5": "regime III median u_recv - u_own > 0",
        "C6": "agent 15 among agent 22's 2 nearest style centroids (descriptive)",
        "overall": "C1 & C2 & C3 & C4"}
HELD_GOALS = [1, 9, 14, 15, 22, 28, 29, 32, 34, 43, 45, 46, 47, 48, 49, 50]
TAIL = ("2026-09-07", "2026-09-22")
NE30 = ("2026-03-05", "2026-03-16")


def frozen_table(include_holdout: bool) -> pl.DataFrame:
    import build as B  # scheme/build.py
    meta = json.loads((L.DATA / "style_standardization.json").read_text())
    df, _ = B.build(include_holdout=include_holdout, meta=meta)
    return df


def prep(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(pl.col("main") & ~pl.col("copy")).sort("agent", "t")


def period_stats(m: pl.DataFrame) -> dict:
    import replication as R
    a = L.arrays(m)
    dec = L.decompose(a, n_perm=200, seed=1)
    att = L.attribution(a, ks=(5,)).get(5)
    riv = R.rivals(a)
    return {"F3": dec["F3"], "u_A": dec["u_A"], "u_C": dec["u_C"], "u_R": dec["u_R"], "p_C": dec.get("p_C", 1.0),
            "n_cu": dec["n_cu"], "dc": att["gain_agent"] if att else np.nan, "rivals": riv,
            "regime": m["regime"][0]}


def eligible(m: pl.DataFrame) -> bool:
    c = m.group_by("agent").len()
    return (c["len"] >= 30).sum() >= 3 and (m["ctx_mode"] == "cu").sum() >= 100


def score(periods: dict, ne41: dict, ne30: dict) -> dict:
    P = list(periods.values())
    F3 = np.array([p["F3"] for p in P])
    uA = np.array([p["u_A"] for p in P]); uC = np.array([p["u_C"] for p in P])
    uR = np.array([p["u_R"] if p["u_R"] == p["u_R"] else -1 for p in P])
    big = np.array([p["n_cu"] >= 500 for p in P]); pC = np.array([p["p_C"] for p in P])
    dc = np.array([p["dc"] for p in P])
    r3 = [p["rivals"]["u_recv_fill"] - p["rivals"]["u_own_fill"] for p in P if "u_own_fill" in p["rivals"]]
    F = ne41.get("forced", {})
    out = {"C1": bool((F3 >= 0.57).mean() >= 2 / 3 and np.median(F3) >= 0.57),
           "C2": bool((uA >= np.maximum(uC, uR)).mean() >= 0.8 and (pC[big] < 0.05).mean() >= 2 / 3),
           "C3": bool(np.nanmean(dc) < 0.02 and (dc > 0).mean() < 2 / 3),
           "C4": bool(F and F["beta"] < 0.6 and F["pred_norm2"] < 0.05 * F["obs_norm2"]
                      and F.get("T_raw", {}).get("T", 0) >= 0.53 and F.get("T_raw", {}).get("lo", 0) > 0.5),
           "C5": bool(len(r3) and np.median(r3) > 0), "C6": ne30.get("met")}
    out["overall"] = bool(out["C1"] and out["C2"] and out["C3"] and out["C4"])
    out["numbers"] = {"F3": F3.tolist(), "dc": dc.tolist(), "ne41": ne41, "r3": r3, "ne30": ne30}
    return out


def ne30_check(m: pl.DataFrame) -> dict:
    w = m.filter(pl.col("pt_date").is_between(pl.lit(NE30[0]), pl.lit(NE30[1]), closed="left"))
    if w.filter(pl.col("agent") == 22).height < 10:
        return {"met": None, "why": "too few agent-22 messages"}
    a = L.arrays(w)
    X0 = a["X"].copy()
    for d in np.unique(a["day"]):
        ix = a["day"] == d
        X0[ix] -= X0[ix].mean(0)
    d22 = sorted(set(a["day"][a["agent"] == 22]))[:5]
    t22 = (a["agent"] == 22) & np.isin(a["day"], d22)
    cands = [g for g in np.unique(a["agent"]) if g != 22 and (a["agent"] == g).sum() >= 20]
    mu = np.stack([X0[a["agent"] == g].mean(0) for g in cands])
    d = ((X0[t22].mean(0)[None] - mu) ** 2).sum(1)
    near = [int(cands[i]) for i in np.argsort(d)[:2]]
    return {"met": 15 in near, "nearest": near}


def run(m_all: pl.DataFrame, period_frames: dict, ne41_frame: pl.DataFrame, include_holdout: bool = False) -> dict:
    periods = {k: period_stats(v) for k, v in period_frames.items() if eligible(v)}
    pairs = L.ne41_pairs(ne41_frame, include_holdout=include_holdout)
    ne41 = L.ne41_fit(L.arrays(ne41_frame), pairs)
    ne30 = ne30_check(m_all)
    return {"periods": periods, "score": score(periods, ne41, ne30)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ok", action="store_true")
    args = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        m = prep(L.load_messages(dedupe="none", main_only=False))
        frames = {f"G{g:02d}": m.filter(pl.col("goal_no") == g) for g in (13, 38, 41)}
        ne = m.filter((pl.col("goal_no") == 51) & (pl.col("pt_date") <= "2026-08-31"))
        res = run(m, frames, ne)
        res["mode"] = "dry-run on non-holdout stand-ins (G13, G38, G41; #51 07-06..08-31 for NE41; NE30 check skipped)"
        (OUTD / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps({k: v for k, v in res["score"].items() if k != "numbers"}, indent=1, default=str))
        return
    if not (args.confirm and args.ok):
        sys.exit("refusing: needs --confirm --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
    sys.path.insert(0, str(L.ROOT / "infra" / "shared"))
    import holdout_ledger as HL
    for tgt in ("#51-tail", "G43", "G45", "NE30"):
        chk = HL.check("H73", tgt, "chat style features", None)
        print(tgt, chk["allowed"], "disclosure needed" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            sys.exit(f"holdout ledger refuses {tgt}")
    sealed = {"predictions": PRED, "frozen_at": "2026-10-04 (round 1)", "sha256": hashlib.sha256(
        json.dumps(PRED, sort_keys=True).encode()).hexdigest(), "sealed_at": dt.datetime.now(dt.UTC).isoformat()}
    (OUTD / "confirm_sealed.json").write_text(json.dumps(sealed, indent=1))
    df = prep(frozen_table(include_holdout=True))
    held = df.filter(pl.col("holdout"))
    frames = {f"G{g:02d}": held.filter(pl.col("goal_no") == g) for g in HELD_GOALS}
    frames["51tail"] = held.filter((pl.col("goal_no") == 51) & pl.col("pt_date").is_between(pl.lit(TAIL[0]), pl.lit(TAIL[1]), closed="left"))
    ne = held.filter(pl.col("regime") == "III")
    res = run(held, frames, ne, include_holdout=True)
    res["mode"] = "CONFIRMATORY"
    (OUTD / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: v for k, v in res["score"].items() if k != "numbers"}, indent=1, default=str))


if __name__ == "__main__":
    main()
