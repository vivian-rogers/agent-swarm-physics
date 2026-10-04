"""H128 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after exploratory round 1. NOT RUN.

Targets: the held-out kickoffs #45-#50, whole periods, first 20 active hours, host labels (W 30, E 100), primary
observable dw = (N_p - 1)/(N_h - 1) (Amendment A1). Kickoff code fixed from the goal TITLES only (no held-out content):
  free (open or objective only): #46 Organise an event, #47 Reduce global suffering, #49 Beat the hardest game you can
  named (assigned artifact):     #48 Help Gemini 2.5 Pro (one target agent)
  reported, not scored (ambiguous from the title): #45 Follow your leader, #50 Compete to be the best AI Assistant
Disclosure: H95's agent read catalog setup lines for #45-#50 (#47 #best had a Help Kit live within 11 min); I have
read only the goal titles (goal-periods.md headings).

Frozen predictions (round 1 found HH369's kill met: free and named curves have the same shape; free weeks do not
coarsen by merging):
  C1 (HH369's free-week coarsening absent): at most 1 of the 3 free targets is "supported" by the period rule
     (dw slow, power law selected, alpha CI overlapping [0.3, 0.5]).                                        [0.80]
  C2 (no systematic coarsening drift after free kickoffs): at most 1 of the 3 free targets has a negative dw
     drift with Kendall tau < 0 at p < 0.05 after the peak (round 1: 2 of 7 free units).                    [0.60]
  C3 (deaths by finishing, not merging): merge share c_m < 0.5 in at least 2 of the 3 free targets
     (round 1: c_m 0.00-0.38 in 7/7 free units).                                                            [0.80]
Reading: C1-C3 confirm "free kickoffs do not coarsen by merging". C1 failing (>= 2 supported) revives HH369.

Reuse policy (hypotheses/holdout.md): #45-#47 and #50 work-ledger project allocation is planned by H75, H77, H78,
H93, H94, H95 (families project_potts, artifact_lineage). H128's statistic (the post-kickoff domain-wall curve) is
new; disclose in the card and LOG.md before running.

Guards: needs BOTH --confirm and H128_CONFIRM=1; refuses unless the sha256 of h128lib.py and this file match
analysis/confirm.sha256; calls holdout_ledger.check() per target. --dry-run runs the identical pipeline on non-holdout
stand-ins (free #36, #38, #41; named #40), asserts no held-out day is loaded, and writes to
data/processed/H128-coarsening-vs-freeze/confirm_dryrun/.

Usage:
  uv run python hypotheses/H128-coarsening-vs-freeze/analysis/confirm.py --dry-run
  H128_CONFIRM=1 uv run python hypotheses/H128-coarsening-vs-freeze/analysis/confirm.py --confirm
  uv run python hypotheses/H128-coarsening-vs-freeze/analysis/confirm.py --freeze
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import kendalltau

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h128lib as L  # noqa: E402

FROZEN_FILES = [HERE / "h128lib.py", Path(__file__).resolve()]
SHA_FILE = HERE / "confirm.sha256"
TARGETS = {46: "free", 47: "free", 49: "free", 48: "named", 45: "report", 50: "report"}
STANDINS = {36: "free", 38: "free", 41: "free", 40: "named"}


def digest() -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in FROZEN_FILES}


def unit(g: int, allow: bool) -> dict:
    d = L.real_events(g, tag=False, allow_holdout=allow)
    if not allow:
        ho = L.RH.calendar().filter(pl.col("pt_date").is_in(d["days"]))["ho"]
        assert not ho.any(), "held-out day loaded in a dry run"
    clock = L.ActiveClock(d["days"])
    cur, de = L.curve_from_events(d["events"], clock)
    s = L.curve_stats(cur, de, col="dw", boot=500, rng=np.random.default_rng(g))
    n = L.curve_stats(cur, de, col="N_p")
    c = cur.filter(pl.col("dw").is_not_nan())
    if s.get("class") is not None:
        c = c.filter(pl.col("t") >= s["t_pk"])
    tau = kendalltau(c["t"].to_numpy(), c["dw"].to_numpy()) if c.height >= 8 else None
    lo, hi = (s.get("alpha_ci") or [None, None])
    a_ok = None if lo is None or not np.isfinite(lo) or not s.get("alpha_fit_ok") else bool(lo <= 0.5 and hi >= 0.3)
    return {"dw": s, "N_p": n, "verdict_free": L.verdict_free(s, a_ok) if s.get("class") else "descriptive",
            "tau": float(tau.statistic) if tau else None, "tau_p": float(tau.pvalue) if tau else None,
            "c_m": n.get("c_m"), "days": len(d["days"])}


def score(res: dict, codes: dict) -> dict:
    free = [g for g, c in codes.items() if c == "free" and res[g]["dw"].get("testable")]
    sup = [g for g in free if res[g]["verdict_free"] == "supported"]
    neg = [g for g in free if res[g]["tau"] is not None and res[g]["tau"] < 0 and res[g]["tau_p"] < 0.05]
    lowm = [g for g in free if res[g]["c_m"] is not None and np.isfinite(res[g]["c_m"]) and res[g]["c_m"] < 0.5]
    return {"free_testable": free, "C1": len(sup) <= 1, "C1_supported": sup, "C2": len(neg) <= 1, "C2_negative": neg,
            "C3": len(lowm) >= 2, "C3_low_merge": lowm,
            "note": "C3 needs >= 2 free targets with deaths; fewer testable targets -> 'not testable'" if len(free) < 2 else ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--freeze", action="store_true")
    a = ap.parse_args()
    if a.freeze:
        SHA_FILE.write_text(json.dumps(digest(), indent=1))
        print("frozen:", digest())
        return
    if a.confirm == a.dry_run:
        sys.exit("choose exactly one of --confirm / --dry-run")
    if not SHA_FILE.exists() or json.loads(SHA_FILE.read_text()) != digest():
        sys.exit("refused: frozen files changed since the freeze (confirm.sha256)")
    if a.confirm:
        if os.environ.get("H128_CONFIRM") != "1":
            sys.exit("refused: set H128_CONFIRM=1 (Vivian's sign-off) to touch the locked holdout")
        sys.path.insert(0, str(L.ROOT / "infra/shared"))
        import holdout_ledger as HL
        for g in TARGETS:
            chk = HL.check("H128", f"G{g}", "work", ["project_potts"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger for G{g}: {chk}")
            if chk["needs_disclosure"]:
                print(f"disclosure needed for G{g}:", sorted({u["hypothesis"] for u in chk["competing_planned"] + chk["prior_runs"]}))
        codes, allow, out = TARGETS, True, L.D / "confirm"
    else:
        codes, allow, out = STANDINS, False, L.D / "confirm_dryrun"
    out.mkdir(parents=True, exist_ok=True)
    res = {g: unit(g, allow) for g in codes}
    sc = score(res, codes)
    tag = "confirm" if a.confirm else "dryrun"
    dflt = lambda o: o.item() if isinstance(o, np.generic) else str(o)  # noqa: E731
    (out / f"{tag}.json").write_text(json.dumps({"units": {str(k): v for k, v in res.items()}, "score": sc}, indent=1, default=dflt))
    print(json.dumps(sc, indent=1, default=dflt))


if __name__ == "__main__":
    main()
