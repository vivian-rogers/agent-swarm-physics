"""H108 round 1 (exploratory, non-holdout): daily room-difference persistence P(l), rotation, angular decorrelation
rate, the identical vs fielded contrast R_D with agent-bootstrap CIs, the Goldstone scaling inputs, the G38 lag profile
and the G35 work-field native; both embedding models, style_resid and white32, and a no-constants variant.

Writes data/processed/H108-goldstone-room-wandering/results/raw_all.json.
Usage: uv run python hypotheses/H108-goldstone-room-wandering/analysis/run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h108lib as L  # noqa: E402
import rslib as R  # noqa: E402

RES = L.DATA / "results"
VARIANTS = [("bge_small", "style_resid", True), ("gte_modernbert", "style_resid", True),
            ("bge_small", "white32", True), ("gte_modernbert", "white32", True),
            ("bge_small", "style_resid", False), ("gte_modernbert", "style_resid", False)]


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        o = o.item()
    if isinstance(o, float) and not np.isfinite(o):
        return None if np.isnan(o) else ("inf" if o > 0 else "-inf")
    return o


def group_stats(per: dict, boots: dict | None):
    out = {}
    for g, Ps in (("identical", R.IDENTICAL), ("fielded", R.FIELDED)):
        P1 = L.pooled_P([per[P] for P in Ps])
        out[g] = {"P1": P1, "D": L.D_of(P1), "omega": 1 - P1 if np.isfinite(P1) else np.nan,
                  "P1_sh": L.pooled_P([per[P] for P in Ps], key="sh")}
    Did, Df = out["identical"]["D"], out["fielded"]["D"]
    out["R_D"] = Did / Df if (np.isfinite(Df) and Df > 0 and np.isfinite(Did)) else (np.inf if Df == 0 and Did > 0 else np.nan)
    out["omega_diff"] = out["identical"]["omega"] - out["fielded"]["omega"]
    if boots:
        nb = min(len(b) for b in boots.values())
        rr, od, pid, pf = [], [], [], []
        for j in range(nb):
            a = L.pooled_P([boots[P][j] for P in R.IDENTICAL]); b = L.pooled_P([boots[P][j] for P in R.FIELDED])
            pid.append(a); pf.append(b); od.append((1 - a) - (1 - b))
            da, db = L.D_of(a), L.D_of(b)
            rr.append(np.inf if (db == 0 and da > 0) else (da / db if db and np.isfinite(db) and db > 0 else np.nan))
        rr = np.array(rr, float)
        q = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]  # noqa: E731
        out["R_D_ci"] = q(np.where(np.isinf(rr), 1e6, rr)); out["omega_diff_ci"] = q(np.array(od))
        out["P1_identical_ci"] = q(np.array(pid)); out["P1_fielded_ci"] = q(np.array(pf))
    return out


def one(st, model, variant, use_consts, boot):
    V = R.load_vectors(model, variant)
    ad, Xc = R.day_centered_agent_days(st, V, R.REG3)
    per, boots = {}, {}
    for P in R.PERIODS:
        consts = R.constants(ad, Xc, exclude={P}) if (use_consts and P != 35) else None
        pan = R.build_panel(st, V, P, "day", consts, halves=True)
        s = L.sums(pan, n_perm=2000, seed=P, max_lag=6)
        s["P1"] = L.P_from(s); s["D"] = L.D_of(s["P1"]); s["P1_sh"] = L.P_from(s, key="sh")
        s["P_lag"] = {l: L.P_from(s, l) for l in s["lags"]}
        s["n_best"], s["n_rest"], s["days"] = pan.info["n_best"], pan.info["n_rest"], pan.days
        if boot:
            boots[P] = L.boot_sums(pan, n_boot=200, n_perm=200, seed=P)
            bp = np.array([L.P_from(b) for b in boots[P]])
            s["P1_ci"] = [float(np.nanpercentile(bp, 2.5)), float(np.nanpercentile(bp, 97.5))]
        per[P] = s
        print(model, variant, use_consts, P, "P1", round(s["P1"], 3) if np.isfinite(s["P1"]) else s["P1"],
              "P_sh", round(s["P1_sh"], 3) if np.isfinite(s["P1_sh"]) else None, "persist_p", s.get("persist_p"),
              flush=True)
    out = {"model": model, "variant": variant, "constants": use_consts,
           "periods": {f"G{P}": s for P, s in per.items()}, "groups": group_stats(per, boots if boot else None)}
    # O4 scaling over identical periods
    Dv, xv = [], []
    for P in R.IDENTICAL:
        s = per[P]
        if s["E_mean"] > 0 and np.isfinite(s["D"]):
            Dv.append(min(s["D"], 50)); xv.append(1 / (s["N_eff"] * s["E_mean"]))
    if len(Dv) >= 4:
        rk = lambda v: np.argsort(np.argsort(v))  # noqa: E731
        out["scaling"] = {"spearman": float(np.corrcoef(rk(np.array(Dv)), rk(np.array(xv)))[0, 1]), "n": len(Dv),
                          "loglog_slope": (float(np.polyfit(np.log(xv), np.log(np.maximum(Dv, 1e-3)), 1)[0])
                                           if all(d > 0 for d in Dv) else None), "D": Dv, "x": xv}
    return clean(out)


def main():
    RES.mkdir(parents=True, exist_ok=True)
    st = L.load_inputs()
    allr = {}
    for model, variant, use_consts in VARIANTS:
        boot = variant == "style_resid"
        key = f"{model}/{variant}" + ("" if use_consts else "/noconst")
        allr[key] = one(st, model, variant, use_consts, boot)
        g = allr[key]["groups"]
        print("GROUP", key, json.dumps({k: g[k] for k in ("R_D", "omega_diff")}), g["identical"], g["fielded"],
              g.get("R_D_ci"), flush=True)
        (RES / "raw_all.json").write_text(json.dumps(allr, indent=1))


if __name__ == "__main__":
    main()
