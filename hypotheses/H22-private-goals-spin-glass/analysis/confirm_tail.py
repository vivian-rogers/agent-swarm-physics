"""H22 confirmatory test on the locked #51 tail (2026-09-07 -> 09-18, unit 51T). WRITTEN, NOT RUN.

The confirmatory predictions C1-C5 are fixed below (and in the card, "Confirmatory predictions"), written after
exploratory round 1 and before any look at the tail. The code path is identical to the exploratory one
(scheme/build.build_unit + explore.run_unit).

Refuses to touch the holdout unless BOTH flags are given:
    uv run python .../confirm_tail.py --confirm --i-understand-this-uses-the-locked-holdout
Dry run (non-holdout stand-in: 08-25 -> 09-04, i.e. 51d + 51e, 9 days, same pipeline, writes to G51/51D_standin/):
    uv run python .../confirm_tail.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))

CONFIRM = {"51T": ("G51", "2026-09-07", "2026-09-18")}
STANDIN = {"51D_standin": ("G51", "2026-08-25", "2026-09-04")}

# ---------------------------------------------------------------------------------------------------------------
# Confirmatory predictions (locked; see the card). Each is a function of the run_unit() result dict -> (pass, detail).
# ---------------------------------------------------------------------------------------------------------------
PREDICTIONS_WRITTEN = "2026-10-04 00:51 UTC (card: 'Confirmatory predictions for the #51 tail'), after exploratory round 1, before any look at the tail"


def _g(d, *ks, default=None):
    for k in ks:
        if not isinstance(d, dict) or k not in d or d[k] is None:
            return default
        d = d[k]
    return d


def evaluate(r):
    """Locked confirmatory rules (C1-C5). Returns dict of verdicts."""
    c = _g(r, "content", "moments", default={})
    fr = _g(r, "content", "frustration", "shuffle", default={})
    tr = _g(r, "content", "treatment", "family_adjusted", default={})
    ov = _g(r, "overlap", default={})
    sra = _g(r, "static_role_alignment", default={})
    out = {}
    # C1 heterogeneous content couplings are real (spread above the pseudo-null)
    out["C1_heterogeneity"] = {"pass": (c.get("p_rho") is not None and c["p_rho"] < 0.05),
                               "rho_split": c.get("rho_split"), "p_rho": c.get("p_rho")}
    # C2 (H22 glass signature) drive-robust balance index below 0.25, CI90 upper bound below 0.5
    t, ci = c.get("tau3_dc"), c.get("tau3_dc_ci90")
    out["C2_unbalanced_tau3dc"] = {"pass": (t is not None and t < 0.25 and ci is not None and ci[1] < 0.5),
                                   "tau3_dc": t, "ci90": ci}
    # C3 (H22) same-role rivals couple negatively relative to unrelated pairs (family-adjusted, one-sided)
    sr = tr.get("SR", {}) if isinstance(tr, dict) else {}
    out["C3_SR_negative"] = {"pass": (sr.get("T") is not None and sr["T"] < 0 and sr.get("p_less") is not None and sr["p_less"] < 0.05),
                             "T": sr.get("T"), "p_less": sr.get("p_less"), "p_greater": sr.get("p_greater"), "n": sr.get("n")}
    out["C3_rival_SR_positive"] = {"pass": (sr.get("T") is not None and sr["T"] > 0 and sr.get("p_greater") is not None and sr["p_greater"] < 0.05)}
    # C4 (H22) collective metastable states: synchrony W > 1 at p < 0.05
    out["C4_synchrony"] = {"pass": (ov.get("p_W") is not None and ov["p_W"] < 0.05 and ov.get("W", 0) > 1),
                           "W": ov.get("W"), "p_W": ov.get("p_W"), "M": ov.get("M")}
    # C5 triangle frustration not below the sign-shuffle null (no structural balance)
    out["C5_not_balanced_F"] = {"pass": (fr.get("p_F_low") is not None and fr["p_F_low"] >= 0.05),
                                "F": fr.get("F"), "F_null": fr.get("F_null_mean"), "p_F_low": fr.get("p_F_low")}
    # R1 (exploration-derived rival): ferromagnetic side, raw tau3 >= 0.25 and kappa > 1
    out["R1_ferro_side"] = {"pass": (c.get("tau3") is not None and c["tau3"] >= 0.25 and c.get("kappa") is not None and c["kappa"] > 1),
                            "tau3": c.get("tau3"), "kappa": c.get("kappa")}
    # R2 (rival): random-field memory without collective switching: W not significant, M > 0.2
    out["R2_rf_drift"] = {"pass": (ov.get("p_W") is not None and ov["p_W"] >= 0.05 and ov.get("M") is not None and ov["M"] > 0.2),
                          "W": ov.get("W"), "p_W": ov.get("p_W"), "M": ov.get("M")}
    # manipulation check (not a prediction of H22): role fields visible in content
    s = sra.get("SR", {}) if isinstance(sra, dict) else {}
    out["manipulation_role_field"] = {"pass": (s.get("p_greater") is not None and s["p_greater"] < 0.05),
                                      "T": s.get("T"), "p_greater": s.get("p_greater"), "n": s.get("n")}
    out["n_SR_pairs_in_test"] = sr.get("n")
    if sr.get("n") is None or sr["n"] < 3:  # locked rule: fewer than 3 testable rival pairs -> C3 / rival C3 not testable
        out["C3_SR_negative"]["pass"] = False; out["C3_SR_negative"]["status"] = "not testable (< 3 SR pairs)"
        out["C3_rival_SR_positive"]["pass"] = False; out["C3_rival_SR_positive"]["status"] = "not testable (< 3 SR pairs)"
    out["H22_confirmed"] = bool(all(out[k]["pass"] for k in ("C1_heterogeneity", "C2_unbalanced_tau3dc", "C3_SR_negative", "C4_synchrony")))
    out["rival_confirmed"] = bool(out["C1_heterogeneity"]["pass"] and out["C3_rival_SR_positive"]["pass"]
                                  and out["R1_ferro_side"]["pass"] and out["R2_rf_drift"]["pass"])
    out["predictions_written"] = PREDICTIONS_WRITTEN
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    import build as B
    import explore as X
    if a.dry_run:
        units = STANDIN
        name = "51D_standin"
        allow = False
    else:
        if not (a.confirm and a.ack):
            sys.exit("Refusing: this script reads the locked #51 tail. It needs BOTH --confirm and "
                     "--i-understand-this-uses-the-locked-holdout (and Vivian's sign-off). Use --dry-run to test.")
        units = CONFIRM
        name = "51T"
        allow = True
    t0 = time.time()
    B.build_unit(name, allow_holdout=allow, units=units)
    r = X.run_unit(name, units=units)
    v = evaluate(r)
    v["unit"] = name; v["dry_run"] = bool(a.dry_run); v["runtime_s"] = round(time.time() - t0, 1)
    out = X.DATA / units[name][0] / name / "confirm.json"
    out.write_text(json.dumps(v, indent=1, default=X._js))
    print(json.dumps(v, indent=1, default=X._js))


if __name__ == "__main__":
    main()
