"""H96 replication on real (non-holdout) data: per-transition remanence, inertia time, order, pseudo-switches.

Usage: uv run python hypotheses/H96-goal-switch-hysteresis/analysis/run.py [--models bge_small,gte_modernbert]
Writes data/processed/H96-goal-switch-hysteresis/results/{transitions_<model>_<variant>.json, pseudo_<...>.json,
card.json}.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h96lib as L  # noqa: E402

RES = L.DATA / "results"


def nz(x):
    return None if (x is None or not np.isfinite(x)) else float(x)


def verdict(r, r1_pseudo_med):
    if not (r["M_pre"]["lo"] > 0):
        return "descriptive"
    m1_pos = r["M_1"]["lo"] > 0
    r1, r1hi = r["R1"]["est"], r["R1"]["hi"]
    if m1_pos and np.isfinite(r1) and r1 >= r1_pseudo_med:
        return "supported"
    if (not m1_pos) or (np.isfinite(r1hi) and r1hi < r1_pseudo_med):
        return "failed"
    return "mixed"


def run_model(model, variant, n_boot=300):
    S = L.Store(model, variant)
    X = S.X
    recs = L.transition_records()
    ps = L.pseudo_records()
    pseudo = []
    for j, r in enumerate(ps):
        s = L.summarize(L.projections(S, X, r), n_boot=0)
        pseudo.append({"goal_no": r["goal_no"], "regime": r["regime"], "pre_day": r["pre_day"],
                       "R1": nz(s["R1"]["est"]), "tau": nz(s["tau"]["est"]), "M_pre": nz(s["M_pre"]["est"]),
                       "q": nz(s["q"])})
    med = {}
    for reg in ("I", "III"):
        v = [p["R1"] for p in pseudo if p["regime"] == reg and p["R1"] is not None and p["M_pre"] and p["M_pre"] > 0]
        med[reg] = {"median": float(np.median(v)), "p10": float(np.percentile(v, 10)),
                    "p90": float(np.percentile(v, 90)), "n": len(v)}
        tv = [p["tau"] for p in pseudo if p["regime"] == reg and p["tau"] is not None]
        med[reg]["tau_median"] = float(np.median(tv)) if tv else None
    out = []
    for r in recs:
        st = L.summarize(L.projections(S, X, r, mode="state"), n_boot=n_boot, seed=r["P"])
        kk = L.summarize(L.projections(S, X, r, mode="kickoff"), n_boot=200, seed=r["P"])
        kick_sim = None
        k0, k1 = S.kickoff_vec(r["Pm1"], r["regime"]), S.kickoff_vec(r["P"], r["regime"])
        if k0 is not None and k1 is not None:
            kick_sim = float(k0 @ k1)
        ref = med[r["regime"]]["median"]
        dR1 = st["R1"]["est"] - ref if np.isfinite(st["R1"]["est"]) else np.nan
        se = (st["R1"]["hi"] - st["R1"]["lo"]) / 3.92 if np.isfinite(st["R1"]["hi"]) else np.nan
        out.append({"P": r["P"], "Pm1": r["Pm1"], "regime": r["regime"], "state": st, "kickoff": kk,
                    "kick_sim": kick_sim, "dR1": nz(dR1), "dR1_se": nz(se), "R1_pseudo_median": ref,
                    "verdict": verdict(st, ref)})
        print(model, variant, r["P"], out[-1]["verdict"], flush=True)
    return out, pseudo, med


def card_stats(out, synth_null=None):
    ok = [o for o in out if o["state"]["M_pre"]["lo"] > 0 and np.isfinite(o["state"]["tau"]["est"])]
    q = np.array([o["state"]["q"] for o in ok]); lt = np.log([o["state"]["tau"]["est"] for o in ok])
    r1 = np.array([o["state"]["R1"]["est"] for o in ok])
    rho, p = spearmanr(q, lt) if len(ok) >= 5 else (np.nan, np.nan)
    rho_r, p_r = spearmanr(q, r1) if len(ok) >= 5 else (np.nan, np.nan)
    # partial: residualize ranks on N agents, regime, kickoff similarity, new quench depth
    cov = np.column_stack([np.ones(len(ok)), [o["state"]["n_agents"] for o in ok],
                           [o["regime"] == "III" for o in ok],
                           [o["kick_sim"] if o["kick_sim"] is not None else 0 for o in ok],
                           [o["state"]["A_K1"]["est"] if np.isfinite(o["state"]["A_K1"]["est"]) else 0 for o in ok]])
    from scipy.stats import rankdata
    def res(v):
        b, *_ = np.linalg.lstsq(cov, rankdata(v), rcond=None)
        return rankdata(v) - cov @ b
    rho_p = float(np.corrcoef(res(q), res(lt))[0, 1]) if len(ok) >= 8 else np.nan
    dr = [o["dR1"] for o in out if o["dR1"] is not None and o["dR1_se"] and o["state"]["M_pre"]["lo"] > 0]
    se = [o["dR1_se"] for o in out if o["dR1"] is not None and o["dR1_se"] and o["state"]["M_pre"]["lo"] > 0]
    re_ = re_mean(dr, se)
    below = [o["state"]["R1"]["est"] < o["R1_pseudo_median"] for o in out if o["state"]["M_pre"]["lo"] > 0]
    taus = [o["state"]["tau"]["est"] for o in ok]
    kick_vs_state = [o["kickoff"]["R1"]["est"] <= o["state"]["R1"]["est"] for o in ok
                     if np.isfinite(o["kickoff"]["R1"]["est"])]
    p_one = (p / 2 if rho > 0 else 1 - p / 2) if np.isfinite(p) else np.nan
    # Amendment 1: P2 on the normalization-free switching time tau_sw, calibrated against the synthetic null
    oks = [o for o in out if o["state"]["M_pre"]["lo"] > 0 and np.isfinite(o["state"]["tau_sw"]["est"])
           and o["state"]["tau_sw"]["est"] < 500]
    rho_sw, p_sw = (spearmanr([o["state"]["q"] for o in oks], np.log([o["state"]["tau_sw"]["est"] for o in oks]))
                    if len(oks) >= 5 else (np.nan, np.nan))
    tsw = [o["state"]["tau_sw"]["est"] for o in oks]
    out_ = {"n_transitions": len(out), "n_identified": len(ok), "rho_q_logtau": nz(rho), "p_one_sided": nz(p_one),
            "rho_q_R1": nz(rho_r), "p_q_R1_two": nz(p_r), "rho_partial": nz(rho_p),
            "dR1_RE": re_, "share_R1_below_pseudo": float(np.mean(below)) if below else None,
            "n_with_old_state": len(below), "tau_median": float(np.median(taus)) if taus else None,
            "tau_iqr": [float(np.percentile(taus, 25)), float(np.percentile(taus, 75))] if taus else None,
            "share_kick_R1_le_state": float(np.mean(kick_vs_state)) if kick_vs_state else None,
            "n_sw_identified": len(oks), "rho_q_logtau_sw": nz(rho_sw), "p_sw_two_sided_nominal": nz(p_sw),
            "tau_sw_median": float(np.median(tsw)) if tsw else None,
            "tau_sw_iqr": [float(np.percentile(tsw, 25)), float(np.percentile(tsw, 75))] if tsw else None,
            "n_tau_sw_capped": sum(o["state"]["M_pre"]["lo"] > 0 and o["state"]["tau_sw"]["est"] >= 500 for o in out),
            "verdicts": {v: sum(o["verdict"] == v for o in out) for v in ("supported", "failed", "mixed", "descriptive")}}
    if synth_null is not None:
        null_sw, thr = synth_null
        out_["rho_sw_null_p95"] = thr
        out_["P2_pass"] = bool(np.isfinite(rho_sw) and rho_sw > thr)
        out_["p_sw_synthetic_null"] = float(np.mean(np.array(null_sw) >= rho_sw)) if np.isfinite(rho_sw) else None
    return out_


def re_mean(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"est": None, "lo": None, "hi": None, "k": 0}
    w = 1 / se ** 2; mu = (w * est).sum() / w.sum(); Q = (w * (est - mu) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2); m = (ws * est).sum() / ws.sum(); s = np.sqrt(1 / ws.sum())
    return {"est": float(m), "lo": float(m - 1.96 * s), "hi": float(m + 1.96 * s), "k": int(len(est)), "tau2": float(tau2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="bge_small,gte_modernbert")
    ap.add_argument("--variants", default="style_resid32")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    syn = json.loads((L.DATA / "synthetic/synthetic.json").read_text())
    null_sw = [rp["rho_q_logtau_sw"] for k in ("S1_lag", "S3_long") for rp in syn[k]["reps"]
               if np.isfinite(rp["rho_q_logtau_sw"])]
    null = (null_sw, float(np.percentile(null_sw, 95)))
    card = json.loads((RES / "card.json").read_text()) if (RES / "card.json").exists() else {}
    for model in a.models.split(","):
        for variant in a.variants.split(","):
            out, pseudo, med = run_model(model, variant)
            tag = f"{model}_{variant}"
            (RES / f"transitions_{tag}.json").write_text(json.dumps(out, indent=1, default=float))
            (RES / f"pseudo_{tag}.json").write_text(json.dumps({"pseudo": pseudo, "reference": med}, indent=1))
            card[tag] = {**card_stats(out, null), "pseudo_reference": med}
            print(tag, json.dumps({k: v for k, v in card[tag].items()}, default=float), flush=True)
            (RES / "card.json").write_text(json.dumps(card, indent=1, default=float))


if __name__ == "__main__":
    main()
