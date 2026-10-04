"""H119 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (rules fixed from round 1, before any holdout data is loaded). Pair classes come from the
minute-level room timeline at run time (metadata): within = co-located >= 90% of kept minutes in every block of the
design; cross = co-located <= 20% in the two-room blocks and >= 90% in the merged block.
  C1 #47 -> #48/#49 -> #50 (two rooms 06-15..06-19 | one room #general 06-22..06-26 | two rooms 06-30..07-03; 06-29 is
     skipped: NE21's hours switch and NE24 fall on it):
     (a) merge contrast M = J_x(merged) - mean(J_x(before), J_x(after)) > 0 with the 95% Wald CI excluding 0;
     (b) no remanence: Rm = J_x(after) - J_x(before) has a CI including 0, or Rm < M/2;
     (c) read-gated: E2 C_RU,x = J^R_x - J^U_x in the merged block > 0 with the CI excluding 0.
     Supported if (a), (b), (c); failed (HH kill) if M's CI includes 0 or M <= 0, or Rm > 0 with CI excluding 0 and
     Rm >= M/2; mixed otherwise.                                                                           [0.5]
  C2 NE15 (one room #34, 03-11..03-13 -> #best/#rest #35, 03-16..03-20): cut arm DiD
     D = (J_x(#35) - J_x(#34)) - (J_w(#35) - J_w(#34)) < 0 with the CI excluding 0; failed if D >= 0.       [0.45]
Primary instrument: E1 KI-5 class model (ki_talk.fit_e1_class); E2 as in run.e2_week.

Reuse disclosure (holdout_ledger.check): #47-#50 were used by H04 (curie_weiss_gain, hawkes, kick response) and are
planned by many; #34 / NE30 by H05 (talk). Different estimator family (kinetic_ising_couplings), same talk modality:
disclose in the card and LOG.md before running.

Safeguards: refuses without --confirm --i-understand-this-uses-the-locked-holdout; refuses unless this file, the card,
scheme/ki_talk.py, analysis/h119lib.py and analysis/run.py are tracked and unmodified; holdout_ledger.check() per
target; --dry-run uses non-holdout stand-ins (NE42 #39/#40/#41 for C1; #40 -> #41 for C2) with ALLOW_HOLDOUT False.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(HERE))
import ki_talk as K  # noqa: E402
import h119lib as L  # noqa: E402
import run as RUN  # noqa: E402

ROOT = K.ROOT
FILES = [f"hypotheses/H119-room-merge-adjacency/{f}" for f in
         ("analysis/confirm.py", "README.md", "scheme/ki_talk.py", "analysis/h119lib.py", "analysis/run.py")]
Z = 1.959964

C1 = {"A": ["2026-06-15", "2026-06-16", "2026-06-17", "2026-06-18", "2026-06-19"],
      "B": ["2026-06-22", "2026-06-23", "2026-06-24", "2026-06-25", "2026-06-26"],
      "C": ["2026-06-30", "2026-07-01", "2026-07-02", "2026-07-03"]}
C2 = {"A": ["2026-03-11", "2026-03-12", "2026-03-13"],
      "B": ["2026-03-16", "2026-03-17", "2026-03-18", "2026-03-19", "2026-03-20"]}
STANDIN_C1 = {k: v for k, v in zip("ABC", L.NE42_WEEKS.values())}
STANDIN_C2 = {"A": L.NE42_WEEKS["40"], "B": L.NE42_WEEKS["41"]}


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def setup(blocks: dict):
    alld = [d for v in blocks.values() for d in v]
    sp = K.day_spins(alld)
    ag = K.eligible(sp, list(blocks.values()))
    st = {k: K.stack(sp, v, ag) for k, v in blocks.items()}
    sh = {k: K.coloc_share(K.colocation(s, ag)) for k, s in st.items()}
    return ag, st, sh


def classes_aba(sh, merged="B"):
    N = next(iter(sh.values())).shape[0]
    off = ~np.eye(N, dtype=bool)
    within = off.copy(); cross = off.copy()
    for k, s in sh.items():
        within &= s >= L.FIX_HI
        cross &= (s >= L.FIX_HI) if k == merged else (s <= L.SW_LO)
    cls = -np.ones((N, N), int)
    cls[within] = 0; cls[cross] = 1
    return cls


def run_c1(blocks):
    ag, st, sh = setup(blocks)
    cls = classes_aba(sh, "B")
    fits = {"39": K.fit_e1_class(st["A"], cls, L.CLASS_IDS), "40": K.fit_e1_class(st["B"], cls, L.CLASS_IDS),
            "41": K.fit_e1_class(st["C"], cls, L.CLASS_IDS)}
    c = L.ne42_contrasts(fits)
    e2 = RUN.e2_week(blocks["B"], ag, cls)
    a_ok = c["M_lo"] > 0
    kill = (not a_ok) or (c["M"] <= 0) or (c["Rm_lo"] > 0 and c["Rm"] >= c["M"] / 2)
    b_ok = (c["Rm_lo"] <= 0 <= c["Rm_hi"]) or (c["Rm"] < c["M"] / 2)
    c_ok = bool(np.isfinite(e2["CRU_cross_lo"]) and e2["CRU_cross_lo"] > 0)
    verdict = "failed" if kill else ("supported" if (a_ok and b_ok and c_ok) else "mixed")
    return {"n_agents": len(ag), "n_within": int((cls == 0).sum()), "n_cross": int((cls == 1).sum()),
            "M": c["M"], "M_ci": [c["M_lo"], c["M_hi"]], "Rm": c["Rm"], "Rm_ci": [c["Rm_lo"], c["Rm_hi"]],
            "CRU_x": e2["CRU_cross"], "CRU_x_ci": [e2["CRU_cross_lo"], e2["CRU_cross_hi"]], "verdict": verdict}


def run_c2(blocks):
    ag, st, sh = setup(blocks)
    N = len(ag)
    off = ~np.eye(N, dtype=bool)
    cls = -np.ones((N, N), int)
    cls[off & (sh["A"] >= L.FIX_HI) & (sh["B"] >= L.FIX_HI)] = 0
    cls[off & (sh["A"] >= L.FIX_HI) & (sh["B"] <= L.SW_LO)] = 1
    fa, fb = K.fit_e1_class(st["A"], cls, L.CLASS_IDS), K.fit_e1_class(st["B"], cls, L.CLASS_IDS)
    D = (fb["J"][1] - fa["J"][1]) - (fb["J"][0] - fa["J"][0])
    var = (fb["V"][1, 1] + fb["V"][0, 0] - 2 * fb["V"][0, 1]) + (fa["V"][1, 1] + fa["V"][0, 0] - 2 * fa["V"][0, 1])
    se = float(np.sqrt(var))
    verdict = "supported" if D + Z * se < 0 else ("failed" if D >= 0 else "mixed")
    return {"n_agents": N, "n_within": int((cls == 0).sum()), "n_cut": int((cls == 1).sum()), "D": float(D),
            "D_ci": [float(D - Z * se), float(D + Z * se)], "verdict": verdict}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        assert not K.ALLOW_HOLDOUT
        out = {"C1_standin_NE42": run_c1(STANDIN_C1), "C2_standin_40to41": run_c2(STANDIN_C2)}
        print(json.dumps(out, indent=1, default=float))
        print("dry run OK (non-holdout stand-ins; no held-out row loaded)")
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: needs --confirm --i-understand-this-uses-the-locked-holdout (Vivian's sign-off)")
    if not git_clean():
        sys.exit(1)
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import holdout_ledger as HL
    for t in ("G47", "G48", "G49", "G50", "G34", "G35"):
        chk = HL.check("H119", t, "talk", "kinetic_ising_couplings")
        if not chk["allowed"]:
            sys.exit(f"refusing: ledger blocks {t}")
        if chk["needs_disclosure"]:
            print(f"disclosure required for {t}: {[u['hypothesis'] for u in chk['prior_runs']]}")
    K.ALLOW_HOLDOUT = True
    res = {"C1": run_c1(C1), "C2": run_c2(C2)}
    od = ROOT / "data/processed/H119-room-merge-adjacency/confirm"
    od.mkdir(parents=True, exist_ok=True)
    (od / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
