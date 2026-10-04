"""POST HOC (labelled; written after the round-1 results): G38's positive-control onset projection pi1 with the final
block at the horizon of a 5-day period (days 4-5) instead of the last third of 17 days (days 12-17); both models.
Usage: uv run python hypotheses/H107-room-split-onset/analysis/posthoc_g38.py"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h107lib as L  # noqa: E402
import rslib as R  # noqa: E402

st = L.load_inputs()
out = {}
for model in ("bge_small", "gte_modernbert"):
    V = R.load_vectors(model, "style_resid")
    ad, Xc = R.day_centered_agent_days(st, V, R.REG3 + [33, 35])
    consts = R.constants(ad, Xc, exclude={38, 37})
    p = R.build_panel(st, V, 38, "day", consts)
    PI = R.perms(p.lab, 2000, 38)
    res = {}
    for name, F in (("F_days4-5", [3, 4]), ("F_days12-17", list(range(11, 17)))):
        xF, mF = R.block(p, F)
        e = R.excess(xF, mF, xF, mF, p.lab, PI); c = R.excess(p.X[0], p.M[0], xF, mF, p.lab, PI)
        e1 = R.excess(p.X[0], p.M[0], p.X[0], p.M[0], p.lab, PI)
        res[name] = {"pi1": c["C"] / e["C"], "r1": e1["C"] / e["C"], "c1": c["C"] / np.sqrt(e1["C"] * e["C"])}
    out[model] = res
print(json.dumps(out, indent=1))
(L.DATA / "results" / "posthoc_g38.json").write_text(json.dumps(out, indent=1))
