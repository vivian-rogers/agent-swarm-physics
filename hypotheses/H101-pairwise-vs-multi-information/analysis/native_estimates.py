"""Write H101 native rows (role native) to per_period_estimates from natives/*.json.
Usage: uv run python hypotheses/H101-pairwise-vs-multi-information/analysis/native_estimates.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

N = ROOT / "data/processed/H101-pairwise-vs-multi-information/natives"
g12 = json.loads((N / "g12.json").read_text())
ne = json.loads((N / "ne42.json").read_text())
g51 = json.loads((N / "g51.json").read_text())
src = "data/processed/H101-pairwise-vs-multi-information/natives/"
rows = [{"period_unit": "12a", "goal_no": 12, "statistic": "team_J_same_minus_opposite", "channel": "co-usage (conventions, per debate)",
         "estimate": g12["team_J"]["diff"], "n": g12["team_J"]["n_same"] + g12["team_J"]["n_diff"], "n_kind": "agent pairs x debates",
         "method": "K-pairwise J per debate; permutation within debate", "null": f"label permutation p = {g12['team_J']['p_greater']:.4f}",
         "role": "native", "ci_kind": "none", "source": src + "g12.json", "notes": "10 debates of #12 (12a, 12b days)"}]
for u in ("39", "41"):
    t = ne["room_J"][u]
    rows.append({"period_unit": u, "goal_no": int(u), "statistic": "room_J_within_minus_across", "channel": "co-usage (conventions)",
                 "estimate": t["diff"], "n": t["n_same"] + t["n_diff"], "n_kind": "agent pairs x days", "role": "native",
                 "method": "subset-averaged K-pairwise J; permutation of room labels within day", "null": f"p = {t['p_greater']:.4f}",
                 "ci_kind": "none", "source": src + "ne42.json"})
for r in g51["sweep"]:
    rows.append({"period_unit": r["unit"], "goal_no": 51, "statistic": f"rho_F_subset_n{r['n']}", "channel": "co-usage (conventions)",
                 "estimate": r["rho_F"], "n": r["n_subset_days"], "n_kind": "subset-days", "role": "native", "ci_kind": "none",
                 "method": "size sweep of the max-ent hierarchy", "null": f"remainder z = {r['ho_excess_z']:.1f}", "source": src + "g51.json"})
E.write_estimates(rows, hypothesis="H101")
print(len(rows))
