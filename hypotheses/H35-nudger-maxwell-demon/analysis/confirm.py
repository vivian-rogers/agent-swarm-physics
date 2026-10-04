"""H35 confirmatory test on the locked holdout. NOT RUN in round 1.

Refuses to touch held-out data unless called with BOTH flags:
    --confirm --i-understand-this-uses-the-locked-holdout
and only when the H35 card and this script are committed (holdout reuse policy, hypotheses/holdout.md: predictions and
script committed before the run). `--dry-run` runs the identical code on non-holdout stand-ins and writes to
data/processed/H35-nudger-maxwell-demon/confirm_dryrun/ (never evidence).

Targets and reuse (disclosed on the card):
  #45, #47, #50 (regime III; information side, gate mechanism and policy ranking). The default pause changed 12 h -> 5 min
      on 06-11: #45 is long-pause (like G38-G44), #47 and #50 short-pause (like G51). H04's confirmatory run computed the nudge A30 kernel
      on #45 (A1 segment) and #46-#50 (NE21 segments), so the *work* statistic there is not fresh. H35's statistics on
      these periods are the nudger's state information (bits per nudge and its decomposition), the gate-model kick
      slope, and the policy ranking (gate-once vs logged); nobody has computed these.
  #32 (regime I) and #34 (regime II): nudge work (first-nudge ATT) and information; no earlier run computed nudge
      responses there (H05 used #32's window for room couplings; H16's #32 script is unrun and uses other statistics).
Stand-ins for --dry-run: #45 -> G44 (long pause), #47 -> G51a (07-06..07-10), #50 -> G51b (07-13..07-17), #32 -> G31,
#34 -> G35 (the only short-pause non-holdout period is #51).
Predictions (C-*) and thresholds are in PREDICTIONS below and on the card ("Confirmatory predictions").
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import importlib.util  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h35lib as L  # noqa: E402


def _load(name: str, path: Path):
    """Load an H35 module by explicit path (h16lib puts H16's analysis folder, which also has run_period.py, on sys.path)."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RP = _load("h35_run_period", Path(__file__).resolve().parent / "run_period.py")

TARGETS = {
    "45": dict(goal=45, gate=True, stand_in="G44"),     # long-pause regime (default pause 12 h before 06-11)
    "47": dict(goal=47, gate=True, stand_in="G51a"),    # short-pause regime (5 min from 06-11), 4-h days
    "50": dict(goal=50, gate=True, stand_in="G51b"),    # short-pause regime, 8-h days
    "32": dict(goal=32, gate=False, stand_in="G31"),
    "34": dict(goal=34, gate=False, stand_in="G35"),
}

# Written 2026-10-03 after exploratory round 1 (card, "Confirmatory predictions"). Each returns (verdict, observed).
PREDICTIONS = {}


def register(pid, targets, primary, statement):
    def deco(f):
        PREDICTIONS[pid] = dict(targets=targets, primary=primary, statement=statement, fn=f)
        return f
    return deco


@register("C1", ["45", "47", "50"], True,
          "state information used: I(M; D,G,K) above its permutation null and b in [0.8, 3.0] bits per nudge "
          "(G51 1.42, G38 1.25, G44 1.19, G42 1.37)")
def c1(r):
    i = r["info"]["I_X"]
    b = i["bits_per_nudge"]
    return ("pass" if (i["above_null"] and 0.8 <= b <= 3.0) else "fail"), {"bits_per_nudge": b, "above_null": i["above_null"]}


@register("C2", ["47", "50"], True,
          "trap age carries the targeting: I(M;K) + I(M;K|D,G) > I(M;G|D) (G51: 1.42 vs 0.93 bits per nudge)")
def c2(r):
    i = r["info"]
    lhs = i["I_K"]["bits_per_nudge"] + i["I_K_given_DG"]["bits_per_nudge"]
    rhs = i["I_G_given_D"]["bits_per_nudge"]
    return ("pass" if lhs > rhs else "fail"), {"K_terms": lhs, "G_given_D": rhs}


@register("C3", ["47", "50"], True,
          "short-pause regime: nudging once at the first re-pause (k*=2) beats the logged nudger per nudge "
          "(card gate model, cross-fitted, escapes: ratio > 1; G51 2.01)")
def c3(r):
    g = r.get("gate", {}).get("eff_escapes_separate", {})
    x = g.get("ratio_gate_once2_vs_logged")
    if x is None:
        return "n/a", {}
    return ("pass" if x > 1 else "fail"), {"ratio": x}


@register("C4", ["47", "50"], True,
          "short-pause regime: the nudge's effect on acting at the gate falls with trap age (card gate model "
          "nudge x ln k < 0; G51 -0.32 +- 0.13)")
def c4(r):
    f = r.get("gate", {}).get("fit", {}).get("separate")
    if not f:
        return "n/a", {}
    b = f["beta"]["nudge_x_lnk"]
    return ("pass" if (b is not None and b < 0) else "fail"), {"nudge_x_lnk": b, "se": f["se"]["nudge_x_lnk"]}


@register("C7", ["45"], False,
          "long-pause regime: a nudge during a pause is a wake-up call: escape at nudged gates >= 0.8 and at "
          "un-nudged gates <= 0.6 (G38: 0.86-1.0 vs 0.20-0.51)")
def c7(r):
    rows = r.get("gate", {}).get("escape_by_K_nudge", [])
    n1 = sum(x["n"] for x in rows if x["M"] == 1); e1 = sum(x["n"] * x["escape"] for x in rows if x["M"] == 1)
    n0 = sum(x["n"] for x in rows if x["M"] == 0); e0 = sum(x["n"] * x["escape"] for x in rows if x["M"] == 0)
    if n1 < 5 or n0 < 20:
        return "n/a", {"n_nudged": n1}
    p1, p0 = e1 / n1, e0 / n0
    return ("pass" if (p1 >= 0.8 and p0 <= 0.6) else "fail"), {"escape_nudged": p1, "escape_unnudged": p0, "n_nudged": n1}


@register("C5", ["32", "34"], False,
          "first-nudge ATT on A30 (H04 isolation set; strict isolation leaves ~0 nudges in regimes I/II) has a positive "
          "point estimate")
def c5(r):
    w = r["work"]["first_pastonly_H04iso"]
    att = w["y30"]
    if not w.get("n"):
        return "n/a", {}
    return ("pass" if att[0] is not None and att[0] > 0 else "fail"), {"att": att, "placebo": w["ypre"], "n": w["n"]}


@register("C6", ["32", "34"], False, "the nudger's state information is above the permutation null")
def c6(r):
    i = r["info"]["I_X"]
    return ("pass" if i["above_null"] else "fail"), {"bits_per_nudge": i["bits_per_nudge"]}


def committed() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", "hypotheses/H35-nudger-maxwell-demon"],
                         capture_output=True, text=True).stdout
    return out.strip() == ""


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    real = "--confirm" in args and "--i-understand-this-uses-the-locked-holdout" in args
    if not dry and not real:
        sys.exit("refusing: pass --dry-run (stand-ins) or --confirm --i-understand-this-uses-the-locked-holdout")
    if real and not committed():
        sys.exit("refusing: commit the H35 card and confirm.py first (holdout reuse policy)")
    SB = _load("h35_build", Path(__file__).resolve().parents[1] / "scheme" / "build.py")
    base = L.OUT / ("confirm_dryrun" if dry else "confirm")
    results, verdicts = {}, {}
    for tid, t in TARGETS.items():
        name = t["stand_in"] if dry else f"C{tid}"
        if dry:
            p = SB.PERIODS[t["stand_in"]]
            days = SB.period_days(p)
            L.h16lib.assert_no_holdout(days)
        else:
            days = L.h16lib.period_days(t["goal"], allow_holdout=True)
        out = base / name
        SB.build_period(name, days, out, t["gate"], allow_holdout=not dry)
        # run_period reads from L.OUT/<period>; point it at the confirm folder
        rel = out.relative_to(L.OUT)
        results[tid] = RP.run(str(rel), B=200)
    for pid, pr in PREDICTIONS.items():
        verdicts[pid] = {}
        for tid in pr["targets"]:
            try:
                v, obs = pr["fn"](results[tid])
            except Exception as ex:
                v, obs = "n/a", {"error": repr(ex)}
            verdicts[pid][tid] = {"verdict": v, "observed": obs}
    prim = [v["verdict"] for pid, pr in PREDICTIONS.items() if pr["primary"] for v in verdicts[pid].values()]
    overall = "supported" if prim and all(x == "pass" for x in prim if x != "n/a") and any(x == "pass" for x in prim) else (
        "failed" if not any(x == "pass" for x in prim) else "mixed")
    summary = {"mode": "dry-run (stand-ins; not evidence)" if dry else "CONFIRMATORY (locked holdout)",
               "predictions": {pid: {k: v for k, v in pr.items() if k != "fn"} for pid, pr in PREDICTIONS.items()},
               "verdicts": verdicts, "overall": overall}
    L.jdump(summary, base / "confirm_summary.json")
    print(json.dumps(summary["verdicts"], indent=1, default=str))
    print("overall:", overall, "|", summary["mode"])


if __name__ == "__main__":
    main()
