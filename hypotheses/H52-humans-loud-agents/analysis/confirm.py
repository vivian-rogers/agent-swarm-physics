"""H52 confirmatory script for the LOCKED HOLDOUT. Written after exploratory round 1; NOT run in round 1.

Targets (hypotheses/holdout.md):
  T45    #45 (Fine-Tuned Leader, agent 30): N4's confirmation (leader premium) + human premium.
  T4650  #46-#50 (quench-lab month; regime III): human premium (content, reply), pooled.
  T51    #51 tail (2026-09-07 -> 09-21): human premium (content, reply, activity, stance); no bot (nudger silent
         after 08-20 in the non-holdout data; the tail was not inspected).

Reuse disclosures (holdout reuse policy, 2026-10-03): #45 was used for confirmation by H02 (activity-timing
couplings, beta J0); H23 plans leader message-content statistics there. #46-#50 lie in the NE21/NE23 window used by
H04 (nudge activity responses). The #51 tail is targeted by unrun confirmatory scripts of H12, H13, H22, H29, H30,
H35 and H39. H52's statistic (sender-class premium matched on salience) has been computed by none of them; this
script must be committed before it runs, and its use disclosed in both cards and LOG.md.

Guards: refuses without `--confirm --i-understand-this-uses-the-locked-holdout`, and refuses if the H52 folder has
uncommitted changes. `--dry-run` runs the identical pipeline on non-holdout stand-ins (G44 for T45 with agent 28 as
the leader; G38+G41+G42 for T4650; G51 08-24 -> 09-04 for T51) and writes confirm_dryrun/ (not evidence).

Usage:
  uv run python hypotheses/H52-humans-loud-agents/analysis/confirm.py --dry-run
  uv run python hypotheses/H52-humans-loud-agents/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h52lib as L  # noqa: E402
import estimate as E  # noqa: E402
import run_period as RP  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

# Frozen predictions (C-*), written 2026-10-04 ~11:30 UTC after exploratory round 1 (card, "Confirmatory predictions").
# kind: "pos" = CI lower bound > 0; "pos_point" = point > 0; "null" = CI includes 0.
PRED = {
    "C1": dict(target="T51", outcome="con", cls="human", kind="pos", primary=True,
               stmt="#51 tail: human content premium (DiD chi) > 0 with CI excluding 0 (round 1: G51 +0.014, 5/5 segments)"),
    "C2": dict(target="T51", outcome="rep", cls="human", kind="pos", primary=True,
               stmt="#51 tail: human reply premium > 0 with CI excluding 0 (round 1: G51 +0.029 before NE43 but -0.002 after; "
                    "this decides whether the NE43 drop was noise; credence 0.45)"),
    "C3": dict(target="T4650", outcome="rep", cls="human", kind="pos", primary=True,
               stmt="#46-#50 pooled: human reply premium > 0 with CI excluding 0"),
    "C4": dict(target="T4650", outcome="con", cls="human", kind="pos_point", primary=False,
               stmt="#46-#50 pooled: human content premium > 0 (point)"),
    "C5": dict(target="T51", outcome="act", cls="human", kind="null", primary=False,
               stmt="#51 tail: human activity premium CI includes 0"),
    "C6": dict(target="T45", outcome="rep", cls="leader", kind="null", primary=False,
               stmt="#45 Fine-Tuned Leader: reply premium CI includes 0 (as the G44 fine-tuned leader; elected/appointed "
                    "agent leaders in G26/G35 got +0.03)"),
    "C7": dict(target="T45", outcome="con", cls="leader", kind="null", primary=False,
               stmt="#45 Fine-Tuned Leader: content premium CI includes 0"),
    "C8": dict(target="T4650", outcome="st", cls="human", kind="pos_point", primary=False,
               stmt="#46-#50 pooled: stance premium toward humans > 0 (point; aggregate only)"),
}
DELTA = {"con": None, "rep": None, "act": 0.5, "st": 0.05}   # reported only (verdicts above use CI signs)

TARGETS = {
    "T45": dict(goals=[45], leader_agent=30),
    "T4650": dict(goals=[46, 47, 48, 49, 50]),
    "T51": dict(goals=[51], date_from="2026-09-07", date_to="2026-09-21"),
}
STANDINS = {
    "T45": dict(goals=[44], leader_agent=28),
    "T4650": dict(goals=[38, 41, 42]),
    "T51": dict(goals=[51], date_from="2026-08-24", date_to="2026-09-04"),
}


def dirty() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", str(L.HYP)],
                         capture_output=True, text=True).stdout
    return bool(out.strip())


def build_target(name: str, spec: dict, outroot: Path, allow_holdout: bool) -> list[pl.DataFrame]:
    from build import build_period
    frames = []
    for g in spec["goals"]:
        out = outroot / f"{name}_G{g:02d}"
        build_period(f"{name}_G{g:02d}", allow_holdout=allow_holdout, out=out, goal=g,
                     date_from=spec.get("date_from"), date_to=spec.get("date_to"))
        frames.append(pl.read_parquet(out / "rows.parquet"))
    return frames


def evaluate(name: str, frames: list[pl.DataFrame], spec: dict, outroot: Path, B: int) -> dict:
    res = {}
    for i, R in enumerate(frames):
        if spec.get("leader_agent") is not None:
            cls = R["cls"].to_numpy().copy()
            cls[(cls == 0) & (R["sender"].to_numpy() == spec["leader_agent"])] = 3
            R = R.with_columns(pl.Series("cls", cls.astype(np.int8)))
        d = E.prepare(R, con_col="chi_dd")
        a = E.analyze(d, B=B, placebo_draws=0, regression=False, classes=(1, 3))
        res[f"part{i}"] = {oc: {c: a[oc].get(c, {}).get("all_bc" if oc == "act" else "all") for c in ("human", "leader")}
                           for oc in E.OUTCOMES}
    # pool parts (random effects) when there are several goal periods
    pooled = {}
    for oc in E.OUTCOMES:
        for c in ("human", "leader"):
            est = [res[k][oc][c]["att"] for k in res if res[k][oc][c] and res[k][oc][c].get("att") is not None]
            se = [res[k][oc][c]["se"] for k in res if res[k][oc][c] and res[k][oc][c].get("att") is not None]
            if est:
                pooled[f"{oc}_{c}"] = L.re_pool(est, se) if len(est) > 1 else dict(pooled=est[0], ci=[
                    res["part0"][oc][c]["ci"][0], res["part0"][oc][c]["ci"][1]], k=1)
    res["pooled"] = pooled
    return res


def score(results: dict) -> dict:
    out = {}
    for cid, p in PRED.items():
        r = results.get(p["target"], {}).get("pooled", {}).get(f"{p['outcome']}_{p['cls']}")
        if not r or r.get("pooled") is None or not np.isfinite(r.get("pooled", np.nan)):
            out[cid] = dict(**p, verdict="n/a"); continue
        lo, hi = r["ci"]
        if p["kind"] == "pos":
            ok = lo > 0
        elif p["kind"] == "pos_point":
            ok = r["pooled"] > 0
        else:
            ok = lo <= 0 <= hi
        out[cid] = dict(**p, est=r["pooled"], ci=r["ci"], verdict="pass" if ok else "fail")
    prim = [v["verdict"] for v in out.values() if v["primary"] and v["verdict"] != "n/a"]
    out["overall"] = ("supported" if prim and all(v == "pass" for v in prim)
                      else ("failed" if prim and all(v == "fail" for v in prim) else "mixed"))
    out["rule"] = "supported if every testable primary passes; failed if none does; otherwise mixed"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--B", type=int, default=1000)
    a = ap.parse_args()
    import json
    S = json.loads((L.OUT / "summary.json").read_text())
    DELTA["con"] = S["margins"]["con"]; DELTA["rep"] = S["margins"]["rep"]
    if a.dry_run:
        outroot = L.OUT / "confirm_dryrun"
        specs, allow = STANDINS, False
    else:
        if not (a.confirm and a.ack):
            sys.exit("refusing: pass --confirm --i-understand-this-uses-the-locked-holdout (or --dry-run)")
        if dirty():
            sys.exit("refusing: commit the H52 folder (predictions and this script) before the confirmatory run")
        outroot = L.OUT / "confirm"
        specs, allow = TARGETS, True
    outroot.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, spec in specs.items():
        frames = build_target(name, spec, outroot, allow)
        results[name] = evaluate(name, frames, spec, outroot, a.B)
    sc = score(results)
    L.jdump(dict(results=results, score=sc, dry_run=a.dry_run, delta=DELTA), outroot / "confirm_results.json")
    for k, v in sc.items():
        print(k, v if isinstance(v, str) else (v.get("verdict"), v.get("est"), v.get("ci")))


if __name__ == "__main__":
    main()
