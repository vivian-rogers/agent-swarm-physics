"""H130 confirmatory run on the LOCKED HOLDOUT (#51 tail, 2026-09-07 -> 09-21). Written and frozen 2026-10-04 after
round 1; NOT RUN.

Guard: held-out rows are built and read only with BOTH `--confirm` and H130_CONFIRM=1, only if the SHA-256 of this file,
h130lib.py and build.py match confirm.sha256, and only if `holdout_ledger.check` allows the target. `--dry-run` runs the
identical pipeline on a non-holdout stand-in (51g days, 2026-08-05 -> 08-21) and writes to a scratch folder whose name
contains "dry".

Frozen predictions (round-1 A1 estimators; primary variant style_resid_period x bge_small; wells leave-day-out over all
#51 days built; tail agent-days are the analysed set; agent-day bootstrap B = 200):
  C1  Read kick: J_K (read vs in-flight at matched posting age) > 0 with 95% CI above 0.           [round 1: 12/12 units]
  C2  Fast kick (the round-1 finding, the claim that stands): rho_gamma = gamma_kick / gamma_auto > 2 with the 90%
      bootstrap CI above 1 (the kick decays faster than the well).                                  [round 1: pooled ~15]
  C3  Well rate reproduces: gamma_auto in [0.0047, 0.0188] per call (round-1 pooled 0.0094 x/ 2).
  C4  HH371 as posed: rho_gamma in [0.5, 2]. Expected to FAIL (round 1 K1 fired).
Reading: C1 + C2 + C3 confirm "reads kick, but the kick is a fast transient that the well does not set". C4 passing
would revive the HH's one-rate claim.

Reuse policy (hypotheses/holdout.md): the #51 tail has planned content users (H98, H22, H12, H13, H20, H33, H72, H77,
H78, H93, H94, H102, H105 ...). H130's statistics (read jump, decay-rate ratio) are a different statistic from H98's
disorder ratio and H22's rival co-movement, but the same content modality: disclose in both cards and LOG.md.

Usage:
  uv run python hypotheses/H130-ou-private-wells-51/analysis/confirm.py --dry-run
  H130_CONFIRM=1 uv run python hypotheses/H130-ou-private-wells-51/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import build as B  # noqa: E402
import h130lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
OUT = ROOT / "data/processed/H130-ou-private-wells-51/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h130_confirm_dryrun"
TAIL = ("2026-09-07", "2026-09-21")
STANDIN = ("2026-08-05", "2026-08-21")
ALL51 = "2026-07-06"
FROZEN = {"g_auto_lo": 0.0047, "g_auto_hi": 0.0188, "rho_fast": 2.0, "rho_lo": 0.5, "rho_hi": 2.0, "B": 200, "seed": 41}
HASHED = [HERE / "confirm.py", HERE / "h130lib.py", HERE.parent / "scheme/build.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_hashes() -> None:
    ref = json.loads((HERE / "confirm.sha256").read_text())
    for p in HASHED:
        if ref.get(p.name) != sha(p):
            sys.exit(f"refused: {p.name} changed since the freeze (confirm.sha256)")


def score(r: dict) -> dict:
    s = {}
    s["C1"] = bool(r["ci_J"][0] > 0)
    s["C2"] = bool(np.isfinite(r["rho"]) and r["rho"] > FROZEN["rho_fast"] and r["ci_rho90"][0] > 1)
    s["C3"] = bool(FROZEN["g_auto_lo"] <= r["g_auto"] <= FROZEN["g_auto_hi"])
    s["C4_hh_as_posed"] = bool(FROZEN["rho_lo"] <= r["rho"] <= FROZEN["rho_hi"])
    s["round1_claim_confirmed"] = bool(s["C1"] and s["C2"] and s["C3"])
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.confirm == a.dry_run:
        sys.exit("choose exactly one of --confirm / --dry-run")
    if a.confirm:
        if os.environ.get("H130_CONFIRM") != "1":
            sys.exit("refused: set H130_CONFIRM=1 (Vivian's sign-off) to touch the locked holdout")
        check_hashes()
        import holdout_ledger as HL
        chk = HL.check("H130", "#51-tail", "message content", ["kick_response", "content_alignment"])
        if not chk["allowed"]:
            sys.exit(f"refused by the holdout ledger: {chk}")
        if chk["needs_disclosure"]:
            print("disclosure needed (holdout.md reuse policy):", sorted({u["hypothesis"] for u in chk["competing_planned"]}))
        root, allow, dates, target = OUT, True, (ALL51, TAIL[1]), TAIL
    else:
        root, allow, dates, target = SCRATCH, False, (ALL51, STANDIN[1]), STANDIN
    B.build(allow_holdout=allow, dates=dates, out_root=root)
    D = L.load("bge_small", "style_resid_period", root=root)
    g = L.agent_days(D)
    days = g["pt_date"].to_numpy()
    mask = (days >= target[0]) & (days < target[1])
    if a.confirm:
        assert mask.any(), "no tail agent-days built"
    r = L.analyze(D, B=FROZEN["B"], seed=FROZEN["seed"], mask_ad=mask, do_old=False, do_natives=False)
    keep = {k: v for k, v in r.items() if k in ("g_auto", "g_kick", "rho", "ci_rho90", "ci_auto", "ci_kick", "J", "ci_J",
                                                 "J_pair", "ci_J_pair", "n_ad", "beta", "beta_se")}
    res = {"mode": "confirm" if a.confirm else "dry-run", "target": target, "frozen": FROZEN,
           "script_sha": {p.name: sha(p)[:12] for p in HASHED}, "result": keep, "score": score(r)}
    root.mkdir(parents=True, exist_ok=True)
    (root / ("confirm_result.json" if a.confirm else "dryrun_result.json")).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
