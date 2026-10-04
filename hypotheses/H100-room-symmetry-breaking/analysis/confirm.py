"""H100 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (thresholds fixed from round 1, before any holdout data is loaded):
  C1 NE19 mover: Claude Opus 4.7 (agent 24; #best -> #rest on 2026-06-01) has phi_pre <= 0 in #44 and, provided the
     #45 native contrast is significant (stayer-relabel p < 0.05), phi_post >= 0.5 and phi_post - phi_comp >= 0.5.
     If the #45 contrast is not significant, C1 is void (not failed).                                          [0.5]
  C2 spontaneous part: in the held-out two-room periods among #45-#48 with >= 3 agents per room (>= 2 days, one room),
     Q_spont > 1 with relabel p < 0.05 in at least half.                                                      [0.6]
  C3 no field direction: where the two room kickoffs differ (whitened cos < 0.95), f_field has direction-null
     p > 0.05.                                                                                                 [0.6]
  C4 no remanence: R (joint relabel) between consecutive held-out two-room periods has |z| < 2 in all pairs.  [0.65]
Primary instrument: bge_small style_resid agent-day vectors (gte reported alongside, not scored).

Reuse disclosure (hypotheses/holdout.md): #45 content is planned by H23, H26, H47, H65 and H81-H83 (NE19 is also H23's
and H65's target); #46-#48 content by H26, H47, H81-H83 and others. H100's statistics (room-separation decomposition,
one mover's phi) are new, but the modality (agent content) is shared. Disclose in the card and LOG.md before running.

Safeguards:
  * refuses to touch the holdout without --confirm --i-understand-this-uses-the-locked-holdout;
  * refuses unless this file, the card, h100lib.py, run.py and scheme/build.py are tracked and unmodified;
  * calls infra/shared/holdout_ledger.check() per target before loading anything;
  * --dry-run uses non-holdout stand-ins (mover: the 05-25 move into #44; periods #41, #42, #44; remanence #41-#42)
    and asserts that no held-out day is loaded.
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
import h100lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

FILES = [f"hypotheses/H100-room-symmetry-breaking/{f}" for f in
         ("analysis/confirm.py", "README.md", "analysis/h100lib.py", "analysis/run.py", "scheme/build.py")]
TARGETS = [45, 46, 47, 48]
NE19 = ("06-01", 44, 45, {24: (L.BEST, L.REST)})
STANDIN = {"mover": ("05-25", 42, 44, {22: (L.BEST, L.REST)}), "periods": [41, 42, 44], "pairs": [(41, 42)]}


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def load_build():
    spec = importlib.util.spec_from_file_location("h100build", ROOT / "hypotheses/H100-room-symmetry-breaking/scheme/build.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def two_room(tab, P):
    m = L.period_rows(tab, P)
    sub = tab.filter(pl.Series(m)).group_by("agent").agg(pl.col("room").n_unique().alias("nr"), pl.col("room").first(),
                                                            pl.len().alias("nd"))
    sub = sub.filter((pl.col("nr") == 1) & (pl.col("nd") >= 2))
    return (sub["room"] == L.BEST).sum() >= 3 and (sub["room"] == L.REST).sum() >= 3


def evaluate(tab, X, fields, F, mover, periods, pairs):
    Xc = L.day_center(tab, X)
    out = {"periods": {}, "pairs": {}}
    bnd, pre, post, mv = mover
    L.MOVES[bnd] = (pre, post, mv)
    m = L.mover_index(tab, Xc, bnd, n_boot=1000, seed=7)
    out["mover"] = m
    (k, _), = mv.items()
    r = m["movers"][k]
    if r.get("skip") or r["C_post_p"] >= 0.05:
        out["C1"] = None
    else:
        out["C1"] = bool(r.get("phi_pre", 1) <= 0 and r["phi_post"] >= 0.5 and r["phi_post"] - r.get("phi_comp", np.nan) >= 0.5)
    eligible = [P for P in periods if two_room(tab, P)]
    c2, c3 = [], []
    for P in eligible:
        d = L.decompose(tab, Xc, fields, F, P, n_null=2000, n_boot=500, seed=P)
        d.pop("_d", None)
        out["periods"][P] = d
        c2.append(d.get("p_spont", 1) < 0.05 and d.get("Q_spont", 0) > 1)
        if d.get("use_kickoff_room"):
            c3.append(d.get("f_field_p", 0) > 0.05)
    out["C2"] = (sum(c2) >= len(c2) / 2) if c2 else None
    out["C3"] = all(c3) if c3 else None
    zs = []
    for a, b in pairs:
        if a in eligible and b in eligible:
            rr = L.remanence(tab, Xc, fields, F, a, b, n_null=2000, seed=a)
            out["pairs"][f"{a}-{b}"] = rr
            zs.append(abs(rr["z"]) < 2)
    out["C4"] = all(zs) if zs else None
    out["eligible"] = eligible
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ok", action="store_true")
    a = ap.parse_args()
    B = load_build()
    if a.dry_run:
        tab, Xs, fields, Fs = B.main(goals=list(range(33, 52)), allow_holdout_goals=(), write=False)
        assert not any(holdout_mask(tab["pt_date"].to_list(), tab["goal_no"].to_list())), "held-out row in dry run"
        X = Xs[("style_resid", "bge_small")].astype(np.float64)
        out = evaluate(tab, X, fields, Fs["bge_small"], STANDIN["mover"], STANDIN["periods"], STANDIN["pairs"])
        ref = json.loads((L.DATA / "results/raw_all.json").read_text())["bge_small/style_resid"]
        for P in STANDIN["periods"]:
            assert abs(out["periods"][P]["Q_spont"] - ref["periods"][f"G{P}"]["Q_spont"]) < 0.02, P
        dest = L.DATA / "confirm"; dest.mkdir(exist_ok=True)
        (dest / "confirm_dryrun.json").write_text(json.dumps(
            {"C1": out["C1"], "C2": out["C2"], "C3": out["C3"], "C4": out["C4"], "eligible": out["eligible"],
             "mover_phi_post": out["mover"]["movers"][22]["phi_post"],
             "Q_spont": {P: out["periods"][P]["Q_spont"] for P in out["periods"]}}, indent=1, default=float))
        print("dry run ok:", {k: out[k] for k in ("C1", "C2", "C3", "C4", "eligible")})
        return
    if not (a.confirm and a.ok):
        sys.exit("refusing: pass --confirm --i-understand-this-uses-the-locked-holdout (needs Vivian's sign-off)")
    if not git_clean():
        sys.exit(1)
    import holdout_ledger as HL
    for t in ["G45", "NE19", "G46", "G47", "G48"]:
        c = HL.check("H100", t, "content", None)
        print(t, "allowed" if c["allowed"] else "BLOCKED", "disclosure needed" if c["needs_disclosure"] else "")
        if not c["allowed"]:
            sys.exit(f"refusing: {t} blocked by the holdout ledger")
    tab, Xs, fields, Fs = B.main(goals=list(range(33, 49)) + [51], allow_holdout_goals=set(TARGETS), write=False)
    X = Xs[("style_resid", "bge_small")].astype(np.float64)
    out = evaluate(tab, X, fields, Fs["bge_small"], NE19, TARGETS, [(45, 46), (46, 47), (47, 48)])
    dest = L.DATA / "confirm"; dest.mkdir(exist_ok=True)
    (dest / "confirm_result.json").write_text(json.dumps(out, indent=1, default=float))
    print({k: out[k] for k in ("C1", "C2", "C3", "C4", "eligible")})


if __name__ == "__main__":
    main()
