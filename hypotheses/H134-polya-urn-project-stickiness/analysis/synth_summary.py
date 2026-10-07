"""Summarize H134 synthetic runs: size, power and bias per skeleton and world (cluster-SE 95% intervals).
Output: data/processed/H134-polya-urn-project-stickiness/synthetic/summary.json and a printed table.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h134lib as L  # noqa: E402

import numpy as np  # noqa: E402

TRUTH_F = {"W0": 0.0, "W1": 1.0, "W2": 0.0, "W3": 0.0, "W4": 0.0, "W5": 0.5}
TRUTH_D = {"W0": 0.0, "W1": 0.0, "W2": -0.4, "W3": 0.0, "W4": 0.0, "W5": -0.2}
Z = 1.96


def frac(x):
    x = np.asarray(x, float)
    return float(np.mean(x)) if len(x) else float("nan")


def summarize(res: dict) -> dict:
    out = {"unit": res["unit"], "n_rows": res["n_rows"], "n_visits": res["n_visits"], "n_forced10": res["n_forced10"],
           "mean_f": res["mean_f"], "worlds": {}}
    eps_proxy = []
    for w, runs in res["worlds"].items():
        s = {"runs": len(runs)}
        for m in ("a", "b"):
            b = np.array([r[f"bF_{m}"] for r in runs], float)
            for k, j in (("wald", 1), ("cl", 2)):
                lo, hi = b[:, 0] - Z * b[:, j], b[:, 0] + Z * b[:, j]
                s[f"bF_{m}_rej0_{k}"] = frac(lo > 0)
                s[f"bF_{m}_cov1_{k}"] = frac((lo <= 1) & (hi >= 1))
                s[f"bF_{m}_covtrue_{k}"] = frac((lo <= TRUTH_F[w]) & (hi >= TRUTH_F[w]))
            s[f"bF_{m}_mean"] = float(b[:, 0].mean()); s[f"bF_{m}_bias"] = float(b[:, 0].mean() - TRUTH_F[w])
            s[f"bF_{m}_sd"] = float(b[:, 0].std()); s[f"bF_{m}_se_cl"] = float(np.median(b[:, 2]))
        bd = np.array([r["bd_b"] for r in runs], float)
        s["bd_mean"] = float(bd[:, 0].mean()); s["bd_rejneg_cl"] = frac(bd[:, 0] + Z * bd[:, 2] < 0)
        s["bd_covtrue_cl"] = frac((bd[:, 0] - Z * bd[:, 2] <= TRUTH_D[w]) & (bd[:, 0] + Z * bd[:, 2] >= TRUTH_D[w]))
        ev = [r for r in runs if "eps_F" in r]
        if ev:
            e = np.array([r["eps_F"] for r in ev], float); ga = np.array([r["G_A"] for r in ev], float)
            s["eps_F_q"] = [float(np.nanpercentile(e, q)) for q in (2.5, 50, 97.5)]
            s["G_A_med"] = float(np.median(ga)); s["G_A_pos"] = frac(ga > 0); s["eps_runs"] = len(ev)
            s["eps_F_vals"] = e.tolist()
            if w in ("W2", "W3", "W4"):
                eps_proxy += [x for x, g in zip(e, ga) if np.isfinite(x)]
        o3 = [r["o3"] for r in runs]
        for k in ("gamma", "km10", "km30", "km100", "km300", "p90"):
            ins = [x[k]["inside"] for x in o3 if x[k]["inside"] is not None]
            s[f"o3_out_{k}"] = frac([not v for v in ins]) if ins else None
            s[f"o3_obs_{k}"] = float(np.nanmedian([x[k]["obs"] if x[k]["obs"] is not None else np.nan for x in o3]))
            s[f"o3_sim_{k}"] = float(np.nanmedian([x[k]["sim_med"] if x[k]["sim_med"] is not None else np.nan for x in o3]))
        killA = [((x["gamma"]["inside"] is False) or (x["km100"]["inside"] is False)) for x in o3]
        s["o3_killA_rate"] = frac(killA)
        o4 = np.array([r["o4"] for r in runs], float)
        s["o4_rej0"] = frac(o4[:, 0] - Z * o4[:, 1] > 0); s["o4_mean"] = float(np.nanmean(o4[:, 0]))
        s["o4_pred_mean"] = float(np.nanmean(o4[:, 3])); s["o4_se_med"] = float(np.nanmedian(o4[:, 1]))
        s["o4_n_treated"] = float(np.nanmedian(o4[:, 2]))
        s["o4_ratio_in_0.5_2"] = frac((o4[:, 0] / o4[:, 3] >= 0.5) & (o4[:, 0] / o4[:, 3] <= 2))
        pl_ = np.array([r["o4_placebo"] for r in runs], float)
        s["o4p_rej_two"] = frac(np.abs(pl_[:, 0]) > Z * pl_[:, 1]); s["o4p_mean"] = float(np.nanmean(pl_[:, 0]))
        s["n_leave_med"] = float(np.median([r["n_leave"] for r in runs]))
        s["n_completed_med"] = float(np.median([r["n_completed"] for r in runs]))
        out["worlds"][w] = s
    if eps_proxy:
        band = float(np.percentile(eps_proxy, 97.5))
        out["eps_band_97_5"] = band
        if "W1" in out["worlds"]:
            out["eps_power_W1"] = frac(np.array(out["worlds"]["W1"]["eps_F_vals"]) > band)
        if "W5" in out["worlds"]:
            out["eps_power_W5"] = frac(np.array(out["worlds"]["W5"]["eps_F_vals"]) > band)
    return out


def main():
    allres = {}
    for p in sorted((L.OUT / "synthetic").glob("[0-9]*.json")):
        allres[p.stem] = summarize(json.loads(p.read_text()))
    L.jdump(allres, L.OUT / "synthetic" / "summary.json")
    for u, r in allres.items():
        print(f"== {u}: rows {r['n_rows']} visits {r['n_visits']} resets(d>=10) {r['n_forced10']} mean f {r['mean_f']:.3f}"
              f" eps band {r.get('eps_band_97_5')} powW1 {r.get('eps_power_W1')} powW5 {r.get('eps_power_W5')}")
        for w, s in r["worlds"].items():
            print(f" {w} n={s['runs']} leave {s['n_leave_med']:.0f} | bF_a {s['bF_a_mean']:+.2f} (sd {s['bF_a_sd']:.2f}, se_cl {s['bF_a_se_cl']:.2f})"
                  f" rej0 cl {s['bF_a_rej0_cl']:.2f} | bF_b {s['bF_b_mean']:+.2f} (sd {s['bF_b_sd']:.2f}) rej0 cl {s['bF_b_rej0_cl']:.2f} wald {s['bF_b_rej0_wald']:.2f}"
                  f" cov1 {s['bF_b_cov1_cl']:.2f} covtrue {s['bF_b_covtrue_cl']:.2f} | bd {s['bd_mean']:+.2f} rej- {s['bd_rejneg_cl']:.2f}"
                  f" | eps {s.get('eps_F_q')} GA+ {s.get('G_A_pos')}")
            print(f"    O3 out: g {s['o3_out_gamma']} km10 {s['o3_out_km10']} km30 {s['o3_out_km30']} km100 {s['o3_out_km100']}"
                  f" km300 {s['o3_out_km300']} p90 {s['o3_out_p90']} killA {s['o3_killA_rate']:.2f}"
                  f" | gamma obs {s['o3_obs_gamma']:+.2f} sim {s['o3_sim_gamma']:+.2f}"
                  f" | O4 rej0 {s['o4_rej0']:.2f} mean {s['o4_mean']:+.2f} pred {s['o4_pred_mean']:+.2f} se {s['o4_se_med']:.2f}"
                  f" nT {s['o4_n_treated']:.0f} ratio-ok {s['o4_ratio_in_0.5_2']:.2f} | plac rej {s['o4p_rej_two']:.2f} mean {s['o4p_mean']:+.2f}")


if __name__ == "__main__":
    main()
