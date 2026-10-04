"""H65 cross-period summary of the replication layer (R1-R5) per embedding model.

    uv run python hypotheses/H65-leaders-are-routers/analysis/summarize.py
Writes data/processed/H65-leaders-are-routers/replication/summary.json.
"""
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

DATA = Path(__file__).resolve().parents[3] / "data/processed/H65-leaders-are-routers"


def summ(model):
    p = DATA / f"replication/{model}/periods.json"
    if not p.exists():
        return None
    u = json.loads(p.read_text())

    def col(k):
        return np.array([r.get(k, np.nan) if r.get(k) is not None else np.nan for r in u], float)
    out = {"n_units": len(u)}
    for k, lab in (("rho_RO_chi", "R1"), ("D", "R2"), ("rho_chi_kappa", "R3"), ("rho_kappa_H32out", "R4"),
                   ("rho_chi_H32in", "R4b"), ("lam_over_chi_median", "R5")):
        v = col(k)
        v = v[np.isfinite(v)]
        pos = int((v > 0).sum())
        out[lab] = {"stat": k, "n": int(len(v)), "median": float(np.median(v)) if len(v) else None,
                    "n_pos": pos, "sign_p_two": float(binomtest(pos, len(v)).pvalue) if len(v) else None}
    lo = [r["D_ci"][0] for r in u if r.get("D_ci") and r["D_ci"][0] is not None]
    hi = [r["D_ci"][1] for r in u if r.get("D_ci") and r["D_ci"][1] is not None]
    out["R2"]["n_ci_above0"] = int(sum(x > 0 for x in lo))
    out["R2"]["n_ci_below0"] = int(sum(x < 0 for x in hi))
    v = col("rho_RO_chi"); v = v[np.isfinite(v)]
    out["R1"]["pass"] = bool(out["R1"]["median"] > 0 and (v > 0).mean() >= 2 / 3)
    out["R2"]["pass"] = bool(out["R2"]["median"] > 0 and out["R2"]["sign_p_two"] < 0.10 and out["R2"]["n_pos"] / out["R2"]["n"] >= 2 / 3)
    out["R3"]["pass"] = bool(out["R3"]["median"] < 0.5)
    out["R4"]["pass"] = bool(out["R4"]["median"] is not None and out["R4"]["median"] > 0.3)
    out["chi_pos_units"] = int((col("chi_median") > 0).sum())
    out["chi_median_of_medians"] = float(np.nanmedian(col("chi_median")))
    out["kappa_median_of_medians"] = float(np.nanmedian(col("kappa_median")))
    return out


if __name__ == "__main__":
    res = {m: summ(m) for m in ("bge_small", "gte_modernbert", "style")}
    (DATA / "replication/summary.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
