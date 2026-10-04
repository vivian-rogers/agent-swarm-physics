"""Write H80 round-1 per-period rows to the shared estimates table. Non-holdout only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H80-assembly-vs-compression/results"
SRC = "data/processed/H80-assembly-vs-compression/results/{}"


def main():
    cls = json.loads((D / "classifier.json").read_text())
    rows = []
    for r in cls:
        u = r["unit"]
        g = 51 if u.startswith("G51") else int(u[1:])
        b = {"period_unit": f"G{g:02d}", "goal_no": g, "role": "replication", "post_hoc": False,
             "source": SRC.format("classifier.json"), "channel": f"commit windows L=16 ({u}; {r['block']}-blocked)",
             "n": float(r["n_windows"]), "n_kind": f"windows ({r['n_pos']} automated from {r['pos_streams']} streams)",
             "notes": "G51+post adds automated windows from 2026-09-21..10-03 (amendment A1)" if u == "G51+post" else None}
        for s in ("T", "C", "C+A"):
            lo, hi = r["auc_ci"][s]
            rows.append({**b, "statistic": f"auc_{s.replace('+', '_plus_')}", "estimate": r["auc"][s], "ci_lo": lo,
                         "ci_hi": hi, "ci_kind": "percentile", "ci_level": 0.95,
                         "method": "L2 logistic, out-of-fold; cluster bootstrap", "null": "AUC 0.5 (label permutation)"})
        d = r["dAUC_A_over_C"]
        rows.append({**b, "statistic": "dauc_assembly_over_compression", "estimate": d["est"], "ci_lo": d["ci"][0],
                     "ci_hi": d["ci"][1], "ci_kind": "percentile", "ci_level": 0.95,
                     "method": "AUC(C+A) - AUC(C), Re-Pair assembly proxy", "null": "0; kill at >= 0.05"})
        rows.append({**b, "statistic": "spearman_arp_lz78", "estimate": r["rho_arp_lz78"], "ci_kind": "none",
                     "method": "Spearman over windows", "null": "prediction >= 0.9"})
    m = json.loads((D / "motifs.json").read_text())
    rows.append({"period_unit": "G51", "goal_no": 51, "role": "replication", "post_hoc": False,
                 "statistic": "hh_motif_prior_share", "channel": "command motifs n=4..8 (a>=6, copies>=20)",
                 "estimate": m["P5_share_first_day_and_2labs"], "ci_kind": "none", "n": float(m["n_hh_motifs"]),
                 "n_kind": "motifs", "method": "present on a joiner's first day and used by >= 2 labs",
                 "null": f"copy-matched low-index motifs any-first-day {m['low_copy_matched_share_any_first']:.3f}",
                 "source": SRC.format("motifs.json")})
    nc = json.loads((D / "ncd.json").read_text())
    rows.append({"period_unit": "G51", "goal_no": 51, "role": "replication", "post_hoc": False,
                 "statistic": "ncd_change_late_minus_early", "channel": "command strings vs first-day reference",
                 "estimate": nc["median_change_late_minus_early"], "ci_kind": "none", "n": float(nc["n_joiners"]),
                 "n_kind": "joiners", "method": "median over joiners of NCD(days>=5) - NCD(days 1-2), gzip",
                 "null": "0 (no village-specific accumulation)", "source": SRC.format("ncd.json")})
    nat = json.loads((D / "natives.json").read_text())
    n32 = nat["NE32"]
    rows.append({"period_unit": "local:NE32", "unit_local": "NE32", "goal_no": 51, "first_day": "2026-07-09",
                 "last_day": "2026-07-09", "role": "native", "post_hoc": False,
                 "statistic": "ne32_day1_hh_session_share_ratio", "channel": "command motifs, isolated newcomers",
                 "estimate": n32["N1a_ratio_ne32_vs_incumbents"], "ci_kind": "none", "n": 3.0, "n_kind": "newcomers",
                 "method": "newcomers' day-1 share of sessions with an HH-HC motif / incumbents' share on 07-09",
                 "null": "prior reading predicts >= 0.8", "source": SRC.format("natives.json")})
    g38 = nat["G38"]
    for s in ("T", "C", "C+A"):
        lo, hi = g38[s]["fpr_ci_wilson"]
        rows.append({"period_unit": "G38", "goal_no": 38, "role": "native", "post_hoc": False,
                     "statistic": f"fpr_no_automation_{s.replace('+', '_plus_')}", "channel": "commit windows, transfer from G51+post",
                     "estimate": g38[s]["fpr"], "ci_lo": max(lo, 0.0), "ci_hi": hi, "ci_kind": "parametric",
                     "ci_level": 0.95, "n": float(g38["n_test"]), "n_kind": "agent windows",
                     "method": "threshold at 90% training sensitivity; Wilson interval",
                     "null": "prediction <= 0.05", "source": SRC.format("natives.json")})
    out = E.write_estimates(rows, hypothesis="H80")
    print(out.height, "rows")


if __name__ == "__main__":
    main()
