"""Write H99 native rows (role native) to per_period_estimates from natives/*.json.
Usage: uv run python hypotheses/H99-glauber-fluctuation-relaxation/analysis/native_estimates.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

N = ROOT / "data/processed/H99-glauber-fluctuation-relaxation/natives"
ne = json.loads((N / "ne42.json").read_text())
g = json.loads((N / "g51.json").read_text())
src = "data/processed/H99-glauber-fluctuation-relaxation/natives/"
rows = []
for o in ("39", "41"):
    for k in ("g_chi", "drho1"):
        d = ne[f"{k}_40_minus_{o}"]
        rows.append({"period_unit": "40", "goal_no": 40, "statistic": f"{k}_talk_40_minus_{o}", "channel": "talk", "estimate": d["est"],
                     "ci_lo": d["ci"][0], "ci_hi": d["ci"][1], "ci_kind": "percentile", "n": None, "role": "native",
                     "method": "difference of independent 1-h block bootstraps", "null": "0", "source": src + "ne42.json",
                     "post_hoc": k == "drho1"})
G0 = g["nudge_target_readout_aligned"]["G_first12"][0]
lam = g["lam_pred_transverse"]
a30 = g["nudge_target_readout_aligned"]["A30"]
rows.append({"period_unit": "51g", "goal_no": 51, "statistic": "nudge_A30_over_onsager_prediction", "channel": "activity",
             "estimate": a30[0] / (G0 / (1 - lam)), "ci_lo": a30[1] / (G0 / (1 - lam)), "ci_hi": a30[2] / (G0 / (1 - lam)),
             "ci_kind": "parametric", "n": g["nudge_target_readout_aligned"]["n_cells"], "n_kind": "nudge-target cells (H04)",
             "role": "native", "method": "H04 r1b A30 / (G(0) / (1 - rho_perp(1))), H04 kernel read as data; CI from H04's A30 CI only",
             "null": "Onsager regression (1)", "source": src + "g51.json", "notes": "pooled over #51 head units; period_unit = largest unit"})
E.write_estimates(rows, hypothesis="H99")
print(len(rows))
