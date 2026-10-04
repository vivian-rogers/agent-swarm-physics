"""Summarize the H59 synthetic runs against P7 (a)-(e). Writes data/processed/H59-one-lever-model/synthetic/summary.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h59lib as L  # noqa: E402
import synthetic as S  # noqa: E402


def cell_status(x):
    T, ci = x["T"], x["ci"]
    if ci["free"][0] <= 0:
        return "uninformative"
    if T is not None and T >= 0.8 and ci["lever"][0] > 0:
        return "pass"
    if (T is None or T < 0.5) and ci["free-lever"][0] > 0:
        return "fail"
    return "mixed"


def main():
    out = {}
    for g in (51, 38):
        fn = L.OUT / "synthetic" / f"synthetic_G{g}.json"
        if not fn.exists():
            continue
        R = json.loads(fn.read_text())
        s = {"recovery": [], "lever_T": [], "dir_any_fail": [], "delay_ci_incl0": [], "null_lever_ci_incl0": [],
             "cells": {}}
        for k, r in R.items():
            w = r["world"]
            st = {c: cell_status(x) for c, x in r["loco"].items()}
            s["cells"][k] = {c: (st[c], None if x["T"] is None else round(x["T"], 2)) for c, x in r["loco"].items()}
            if w == "lever":
                for c in r["classes"]:
                    if r["loco"][c]["n_rec"] >= 300:
                        kt, ht = S.TRIPLES[c]
                        ke, he = r["triples"][c]["kappa"]["est"], r["triples"][c]["h"]["est"]
                        s["recovery"].append({"class": c, "kappa": [kt, ke], "h": [ht, he],
                                              "theta": [S.TH, r["triples"]["theta_deg"]["est"]]})
                        T = r["loco"][c]["T"]
                        s["lever_T"].append(T if T is not None else np.nan)
            if w == "dirviol":
                s["dir_any_fail"].append(any(v == "fail" for v in st.values()))
            if w == "delay":
                for c, x in r["loco"].items():
                    if x["n_rec"] >= 300:
                        lo, hi = x["ci"]["lever-delay"]
                        s["delay_ci_incl0"].append(lo <= 0 <= hi)
            if w == "null":
                for c, x in r["loco"].items():
                    lo, hi = x["ci"]["lever"]
                    s["null_lever_ci_incl0"].append(lo <= 0 <= hi)
        rel_h = [abs(r["h"][1] - r["h"][0]) / abs(r["h"][0]) for r in s["recovery"]]
        th_err = [abs(r["theta"][1] - r["theta"][0]) for r in s["recovery"]]
        s["P7"] = {"a_median_rel_err_h": float(np.median(rel_h)) if rel_h else None,
                   "a_median_abs_err_kappa": float(np.median([abs(r["kappa"][1] - r["kappa"][0]) for r in s["recovery"]])) if rel_h else None,
                   "a_median_theta_err_deg": float(np.median(th_err)) if th_err else None,
                   "b_share_T_ge_0.8": float(np.nanmean(np.array(s["lever_T"]) >= 0.8)) if s["lever_T"] else None,
                   "c_share_dirviol_detected": float(np.mean(s["dir_any_fail"])) if s["dir_any_fail"] else None,
                   "d_share_delay_ci_incl0": float(np.mean(s["delay_ci_incl0"])) if s["delay_ci_incl0"] else None,
                   "e_share_null_ci_incl0": float(np.mean(s["null_lever_ci_incl0"])) if s["null_lever_ci_incl0"] else None}
        out[f"G{g}"] = s
        print(g, json.dumps(s["P7"]), json.dumps(s["cells"]))
    (L.OUT / "synthetic" / "summary.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
