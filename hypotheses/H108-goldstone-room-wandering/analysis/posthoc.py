"""POST HOC (labelled; written after the round-1 results). (1) Leave-one-out group contrasts: fielded = G44 only
(without G38), identical without G36 (no persistent direction). (2) Magnitude confound: Goldstone predicts
D ~ 1/(N_eff |m|^2), and the fielded periods have the largest splits. OLS of ln D on ln x (x = 1/(N_eff E_mean)) and a
fielded dummy over the regime-III periods with a defined D. Reads results/raw_all.json.
Usage: uv run python hypotheses/H108-goldstone-room-wandering/analysis/posthoc.py"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h108lib as L  # noqa: E402

raw = json.loads((L.DATA / "results" / "raw_all.json").read_text())
out = {}
for key in ("bge_small/style_resid", "gte_modernbert/style_resid"):
    per = raw[key]["periods"]
    def pooled(ps):
        return L.pooled_P([per[f"G{p}"] for p in ps])
    D = lambda p: L.D_of(p)  # noqa: E731
    res = {}
    for name, idp, fp in (("id_all__f_G44", [36, 37, 39, 41, 42], [44]),
                          ("id_noG36__f_all", [37, 39, 41, 42], [38, 44]),
                          ("id_noG36__f_G44", [37, 39, 41, 42], [44])):
        a, b = pooled(idp), pooled(fp)
        res[name] = {"P_id": a, "P_f": b, "R_D": D(a) / D(b) if D(b) > 0 else None}
    rows = []
    for p in (36, 37, 38, 39, 41, 42, 44):
        s = per[f"G{p}"]
        d = s["D"]
        if d is None or isinstance(d, str) or s["E_mean"] is None or s["E_mean"] <= 0:
            continue
        rows.append((p, np.log(max(d, 1e-3)), np.log(1 / (s["N_eff"] * s["E_mean"])), 1.0 if p in (38, 44) else 0.0))
    y = np.array([r[1] for r in rows]); X = np.column_stack([np.ones(len(rows)), [r[2] for r in rows], [r[3] for r in rows]])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(rows) - 3
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * (resid @ resid) / dof) if dof > 0 else [np.nan] * 3
    X2 = X[:, :2]; b2, *_ = np.linalg.lstsq(X2, y, rcond=None)
    res["magnitude_fit"] = {"periods": [r[0] for r in rows], "slope_lnx": float(beta[1]), "se_slope": float(se[1]),
                            "fielded_coef": float(beta[2]), "se_fielded": float(se[2]), "dof": dof,
                            "slope_without_dummy": float(b2[1]),
                            "rows": [{"P": r[0], "lnD": float(r[1]), "lnx": float(r[2])} for r in rows]}
    out[key] = res
print(json.dumps(out, indent=1))
(L.DATA / "results" / "posthoc.json").write_text(json.dumps(out, indent=1))
