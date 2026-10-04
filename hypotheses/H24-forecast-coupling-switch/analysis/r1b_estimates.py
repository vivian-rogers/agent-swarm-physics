"""H24 round 1b: per-period estimates for the shared table (infra/shared/estimates.py), both embedding models, shared
goal fields, field removed along g-hat (replication) and the native tests (G21 pair-level reading DiD, G41 room cut).
Usage: uv run python hypotheses/H24-forecast-coupling-switch/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h24lib import H24, ROOT  # noqa: E402
import estimates as E  # noqa: E402

M1 = ("H24 r1b: whitened n = 32 statement vectors, field removed along g-hat (shared goal fields), rarefied agent vectors "
      "(k = 4, 200 draws)")


def main():
    rows = []
    for model in ("bge_small", "gte_modernbert"):
        f = H24 / "G21" / "r1b" / f"explore_{model}_shared_1d.json"
        d = json.loads(f.read_text())
        a = d["O1"]["n32_ghat"]["a_all"]["res"]
        n2 = sorted(x["res"]["dA"] for x in d["N2"])
        q90 = n2[int(0.9 * (len(n2) - 1) + 0.5)] if n2 else None
        base = dict(period_unit=E.map_unit(21), goal_no=21, channel=f"content_{model}", source=str(f.relative_to(ROOT)),
                    status="ok")
        rows.append({**base, "statistic": "alignment_step_at_switch_on", "estimate": a["dA"], "ci_lo": a["boot"]["dA_ci90"][0],
                     "ci_hi": a["boot"]["dA_ci90"][1], "ci_level": 0.90, "ci_kind": "percentile", "role": "native",
                     "n": len(d["switched"]), "n_kind": "agents", "first_day": "2025-12-01", "last_day": "2025-12-01",
                     "method": M1 + "; pre = [open, tau_i), post = [tau_i, tau_i + 60 min) on day 1",
                     "null": f"N1 within-week placebo q90 = {a['N1_q90']:.3f}; N2 kickoff-matched q90 ~ {q90:.3f}"})
        rows.append({**base, "statistic": "residual_alignment_pre_switch", "estimate": a["A_pre"], "ci_kind": "none",
                     "role": "native", "n": len(d["switched"]), "n_kind": "agents", "method": M1 + "; level before tau_i",
                     "null": f"per-agent Haar rotation q95 = {a['N3_rot']['A_pre_q95']:.3f}"})
        docs = d["O1"]["n32_ghat"]["c_docs_all"]["res"]
        rows.append({**base, "statistic": "doc_alignment_step_at_switch_on", "estimate": docs["dA"],
                     "ci_lo": docs["boot"]["dA_ci90"][0], "ci_hi": docs["boot"]["dA_ci90"][1], "ci_level": 0.90,
                     "ci_kind": "percentile", "role": "native", "method": M1.replace("k = 4", "k = 5") + "; document chunks, post = rest of day 1",
                     "null": None})
        rows.append({**base, "statistic": "alignment_ramp_spearman", "estimate": d["O3"]["rho"], "ci_kind": "none",
                     "role": "replication", "n": d["O3"]["n_blocks"], "n_kind": "2-h blocks",
                     "method": M1 + "; Spearman of residual alignment on block index, G21b-c", "null": f"p = {d['O3']['p']:.3f}"})
        # natives
        g = json.loads((H24 / "G21" / "r1b" / f"native_{model}.json").read_text())
        for kind in ("stmt", "doc"):
            x = g[kind]
            rows.append({**base, "statistic": f"pair_reading_DiD_{kind}", "estimate": x["mean_did"], "ci_kind": "none",
                         "role": "native", "n": x["n"], "n_kind": "reading events",
                         "method": "H24 r1b native: (a_post - a_pre)(i, owner) minus unread controls, 60-min windows, field "
                                   "removed along all goal and kickoff chunk directions",
                         "null": f"owner-label permutation p = {x['perm_p']:.3f}",
                         "source": str((H24 / "G21" / "r1b" / f"native_{model}.json").relative_to(ROOT))})
        w = json.loads((H24 / "G41" / "r1b" / f"native_{model}.json").read_text())
        src = str((H24 / "G41" / "r1b" / f"native_{model}.json").relative_to(ROOT))
        for b in w["days"]:
            rows.append(dict(period_unit=f"local:41_{b['block']}", unit_local=b["block"], goal_no=41, channel=f"content_{model}", source=src, status="ok",
                             statistic="room_gap_dW_daily", estimate=b["dW"], ci_kind="none", role="native",
                             first_day=b["block"], last_day=b["block"],
                             method="H24 r1b native: within-room minus cross-room mean pairwise cosine of rarefied agent vectors "
                                    "(k = 3), field removed along goal and kickoff chunks",
                             null=f"room-label permutation p = {b['perm_p']:.4f}, q95 = {b['null_q95']:.3f}"))
    out = E.write_estimates(rows, hypothesis="H24")
    print(f"wrote {out.height} H24 rows")


if __name__ == "__main__":
    main()
