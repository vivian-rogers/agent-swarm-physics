"""H71 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (thresholds fixed from round 1, before any holdout data is loaded):
  C1 reversion: in every held-out target with >= 3 agents having >= 15 within-period cycle pairs, phi+ (half-panel
     jackknife, agent bootstrap B = 1000) lies in (0, 0.95) with the CI's upper bound < 1.                       [0.9]
  C2 the overshoot is a sampling artifact: in >= 2/3 of the regime-III targets, the mixed-phase phi (H09's statistic)
     is < 0 while phi+ > 0.                                                                                       [0.85]
  C3 no overshoot after forced erasures: pooled over regime-III targets (agent-period sufficient statistics),
     phi+(forced) has its CI above 0 and |phi+(forced) - phi+(voluntary)| < 0.15.                                [0.8]
  C4 two timescales: pooled over targets, rho_2 - rho_1^2 of x+ > 0 with the agent-bootstrap CI above 0.          [0.75]
  C5 #43 ("Improve your memory") moves the set point: for agents present in #42 or #44 (non-holdout) and #43, the
     paired mean change in ln set point is > 0 with the CI above 0.                                               [0.6]
Targets: G43, G45, G46, G47, G48, G49, G50 (all regime III), #51 tail (2026-09-07 -> 09-21).

Reuse disclosure (hypotheses/holdout.md): #45-#50 and the #51 tail are planned or used by many hypotheses (activity,
kicks, content, context). H71's statistic (memory-size dynamics from memory_stats) is a different modality; #43 is
planned by H15 (memory as semantic information, a different statistic). Disclose in the card and LOG.md before running.

Safeguards:
  * refuses to touch the holdout without --confirm --i-understand-this-uses-the-locked-holdout;
  * refuses unless this file, the card, h71lib.py, run.py, posthoc.py and scheme/build.py are tracked and unmodified;
  * calls infra/shared/holdout_ledger.check() per target before loading anything;
  * --dry-run uses non-holdout stand-ins (G41, G42, G44 and #51 08-24 -> 09-04) from the exploratory tables and
    asserts that no held-out day is present.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h71lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
DATA = ROOT / "data/processed/H71-memory-homeostat"
TARGETS = ["G43", "G45", "G46", "G47", "G48", "G49", "G50", "G51tail"]
STANDINS = {"G41": "G41", "G42": "G42", "G44": "G44", "G51late": "G51"}
FILES = [f"hypotheses/H71-memory-homeostat/{f}" for f in
         ("analysis/confirm.py", "README.md", "analysis/h71lib.py", "analysis/run.py", "analysis/posthoc.py",
          "scheme/build.py")]


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f],
                                 capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True,
                               text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def load_build():
    spec = importlib.util.spec_from_file_location("h71build", ROOT / "hypotheses/H71-memory-homeostat/scheme/build.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def evaluate(cyc: pl.DataFrame, snaps: pl.DataFrame, targets: list[str], prev: pl.DataFrame | None) -> dict:
    import posthoc as PH
    import run as R
    res, ok1, c2 = {}, [], []
    pairs_all = []
    S_acf = []
    for t in targets:
        cp = cyc.filter(pl.col("period") == t)
        p = L.pairs(cp)
        keep = p.group_by("agent").len().filter(pl.col("len") >= L.MIN_PAIRS_AGENT)["agent"]
        if keep.len() < 3:
            res[t] = {"scored": False, "n_agents": int(keep.len())}
            continue
        r = R.one_period(t, cyc, snaps)
        res[t] = {"scored": True, "phi": r["phi"], "mixed_phi": r["mixed_phi"], "regime": r["regime"]}
        ok1.append(0 < r["phi"]["est"] < 0.95 and r["phi"]["hi"] < 1)
        if r["regime"] == "III":
            c2.append(r["mixed_phi"] < 0 < r["phi"]["est"])
        pairs_all.append(p.filter(pl.col("agent").is_in(keep.implode())).with_columns(
            (pl.col("agent").cast(pl.Int32) * 1000 + len(pairs_all)).alias("agent")))
        S_acf.append(PH.acf_suff(cp.filter(pl.col("agent").is_in(keep.implode()))))
    out = {"targets": res}
    out["C1"] = bool(ok1) and all(ok1)
    out["C2"] = bool(c2) and sum(c2) >= 2 / 3 * len(c2)
    if pairs_all:
        P = pl.concat(pairs_all)
        ba = L.boot_all(P, B=1000)
        out["C3_detail"] = {"forced": ba["phi_forced"], "f_minus_v": ba["f_minus_v"]}
        out["C3"] = ba["phi_forced"]["lo"] > 0 and abs(ba["f_minus_v"]["est"]) < 0.15
        S = np.vstack([s for s in S_acf if len(s)])
        rho = PH.acf_from(S)
        bs = np.array([PH.acf_from(S[i]) for i in np.random.default_rng(43).integers(0, len(S), (1000, len(S)))])
        dev = bs[:, 1] - bs[:, 0] ** 2
        out["C4_detail"] = {"est": float(rho[1] - rho[0] ** 2), "ci": [float(np.percentile(dev, 2.5)),
                                                                      float(np.percentile(dev, 97.5))]}
        out["C4"] = out["C4_detail"]["ci"][0] > 0
    if prev is not None and "G43" in targets:
        a = cyc.filter(pl.col("period") == "G43").group_by("agent").agg(pl.col("xplus").mean().alias("m43"))
        b = prev.group_by("agent").agg(pl.col("xplus").mean().alias("m0"))
        w = a.join(b, on="agent")
        if w.height >= 3:
            d = (w["m43"] - w["m0"]).to_numpy()
            bs = np.random.default_rng(5).choice(d, (2000, len(d))).mean(1)
            out["C5_detail"] = {"dln": float(d.mean()), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                                "n": int(len(d))}
            out["C5"] = out["C5_detail"]["ci"][0] > 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        cyc = pl.read_parquet(DATA / "cycles.parquet")
        snaps = pl.read_parquet(DATA / "snapshots.parquet")
        from common import holdout_mask
        assert not any(holdout_mask(cyc["pt_date"].to_list(), cyc["goal_no"].to_list())), "holdout row in stand-ins"
        late = (pl.col("period") == "G51") & (pl.col("pt_date") >= "2026-08-24")
        cyc = cyc.with_columns(pl.when(late).then(pl.lit("G51late")).otherwise(pl.col("period")).alias("period"),
                               pl.when(late).then(pl.lit("G51late")).otherwise(pl.col("period_prev")).alias("period_prev"))
        snaps = snaps.with_columns(pl.when((pl.col("period") == "G51") & (pl.col("pt_date") >= "2026-08-24"))
                                   .then(pl.lit("G51late")).otherwise(pl.col("period")).alias("period"))
        prev = cyc.filter(pl.col("period") == "G41")
        cyc_c5 = cyc.with_columns(pl.when(pl.col("period") == "G42").then(pl.lit("G43")).otherwise(pl.col("period"))
                                  .alias("period"))
        out = evaluate(cyc, snaps, list(STANDINS), None)
        out["C5_standin"] = evaluate(cyc_c5, snaps, ["G43"], prev).get("C5_detail")
        (DATA / "confirm_dryrun.json").write_text(json.dumps(out, indent=1, default=float))
        print(json.dumps({k: v for k, v in out.items() if k != "targets"}, indent=1, default=float))
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: confirmatory runs need --confirm --i-understand-this-uses-the-locked-holdout")
    if not git_clean():
        sys.exit(2)
    import holdout_ledger as HL
    for t in ["G43", "G45", "G46", "G47", "G48", "G49", "G50", "#51-tail"]:
        chk = HL.check("H71", t, "memory_stats", ["behavior_states"])
        print(t, "allowed" if chk["allowed"] else "BLOCKED", "disclose" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            sys.exit(f"refusing: {t} already used by the same estimator family")
    hold = json.loads((ROOT / "hypotheses/holdout.json").read_text())
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet", columns=["pt_date", "goal_no"])
    tail = [w for w in hold["ne_windows"] if w["id"] == "#51-tail"][0]
    days = cal.filter(pl.col("goal_no").is_in([43, 45, 46, 47, 48, 49, 50])
                      | pl.col("pt_date").is_between(tail["start"], tail["end"], closed="left"))["pt_date"].to_list()
    B = load_build()
    B.build(held=True, days=days, out=DATA / "confirm")
    cyc = pl.read_parquet(DATA / "confirm/cycles_confirm.parquet")
    snaps = pl.read_parquet(DATA / "confirm/snapshots_confirm.parquet")
    tailx = (pl.col("goal_no") == 51)
    cyc = cyc.with_columns(pl.when(tailx).then(pl.lit("G51tail")).otherwise(pl.col("period")).alias("period"),
                           pl.when(tailx).then(pl.lit("G51tail")).otherwise(pl.col("period_prev")).alias("period_prev"))
    snaps = snaps.with_columns(pl.when(tailx).then(pl.lit("G51tail")).otherwise(pl.col("period")).alias("period"))
    prev = pl.read_parquet(DATA / "cycles.parquet").filter(pl.col("period").is_in(["G42", "G44"]))
    out = evaluate(cyc, snaps, TARGETS, prev)
    (DATA / "confirm/confirm_results.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "targets"}, indent=1, default=float))


if __name__ == "__main__":
    main()
