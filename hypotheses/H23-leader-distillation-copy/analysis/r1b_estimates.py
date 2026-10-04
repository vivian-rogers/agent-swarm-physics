"""H23 round 1b: O3a embedding contrasts in both models into the shared estimates table.
Usage: uv run python hypotheses/H23-leader-distillation-copy/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

P = ROOT / "data/processed/H23-leader-distillation-copy/G44/r1b/r1b.json"


def main():
    R = json.loads(P.read_text())["C_embedding_two_models"]
    rows = []
    for model, r in R.items():
        for o in ("CTRL", "K_same"):
            t = r["tests"][f"d:leader>{o}"]
            rows.append({"period_unit": E.map_unit(44) or "G44", "goal_no": 44, "statistic": f"o3a_d_leader_minus_{o}",
                         "channel": f"content ({model})", "estimate": t["diff"], "ci_kind": "none", "n": t["n_a"] + t["n_b"],
                         "n_kind": "messages", "method": f"d = cos(z, corpus) - cos(z, Kimi field), regime-III whitened 32-d, {model}",
                         "null": f"one-sided speaker-label permutation p={t['p']:.3g}", "role": "native",
                         "source": str(P.relative_to(ROOT)), "status": "exploratory round 1b (both embedding models)"})
    E.write_estimates(rows, hypothesis="H23")
    print("wrote", len(rows))


if __name__ == "__main__":
    main()
