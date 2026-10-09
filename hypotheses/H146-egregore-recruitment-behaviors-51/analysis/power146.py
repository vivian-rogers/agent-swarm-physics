"""H146 per-pattern power on the pattern's own real skeleton (Amendment A1, untestability rule).

Each check keeps the real skeleton of one pattern K (its real item coding, real exposures, real at-risk rows, real
event counts, real wipe/placebo events, real challenge rows) and plants the outcome. It runs BEFORE the pattern's
estimate is computed (run_real.py stage 1), and its result decides whether a kill rule can be applied to K.

  p1_power   read-gated adoption / expression response: contagion through K items from hosts read at the producing
             call (mirror + rest of the call) at log-odds beta, earlier 2-h reads at beta/5; base rate set so the
             expected events equal the real count; power = share with z(delta) > 1.96 among replicates (estimable
             or not; a non-estimable replicate counts as no rejection). size = the same with beta = 0.
  p4_power   wipe survival: real host F/P events and follow-up call counts; planted per-call hazard h0 = the
             arm-blind pooled real re-expression rate; r = 0.5 (K2 world) and r = 1 (survival world), g = 2
             (read-gated re-supply, R+ = the real read status).
  p5_power   repair rate ratio on the real event rows (agents, strata, clusters): negative-binomial counts (k = 1)
             with the arm-blind pooled mean; power = share passing the P5 rule (RR > 1.2 and CI above 1) at RR 1.5.
Each returns a dict with the replicate count, the share and the inputs used.
"""
from __future__ import annotations

import numpy as np

import h146lib as L


def _base(eta, n_target):
    lo, hi = -20.0, 5.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if (1 / (1 + np.exp(-(mid + eta)))).sum() > n_target:
            hi = mid
        else:
            lo = mid
    return lo


def p1_power(ev, Xd, rows, n_events, ctrl, beta=0.3, reps=60, seed=0, split_named=False):
    """rows: bool mask of the design's risk set; n_events: real event count in it."""
    rng = np.random.default_rng(seed)
    r = np.where(rows)[0]
    if n_events < 5 or len(r) < 50:
        return {"reps": 0, "power": 0.0, "size": None, "n_events": int(n_events), "note": "too few events"}
    Rcall = Xd["Rm"] + Xd["Rc_rest"]
    out = {}
    for lab, b in (("power", beta), ("size", 0.0)):
        eta = b * Rcall[r] + (b / 5) * Xd["R2h"][r]
        c = _base(eta, n_events)
        p = 1 / (1 + np.exp(-(c + eta)))
        rej = []
        for _ in range(reps if lab == "power" else 100):
            y = np.zeros(len(rows), bool)
            y[r] = rng.random(len(r)) < p
            o = L.p1_fit(ev, Xd, rows, y, ctrl=ctrl)
            e, se = o["delta"]
            rej.append(bool(o["estimable"] and se > 0 and e / se > 1.96))
        out[lab] = float(np.mean(rej))
    out.update({"reps": reps, "reps_size": 100, "beta": beta, "n_events": int(n_events), "n_rows": int(len(r)),
                "rows_read_exposed": int((Xd["Rm"][r] > 0).sum()), "rows_inflight_exposed": int((Xd["P"][r] > 0).sum())})
    return out


def p4_power(E, reps=60, seed=0, B=150):
    """E: real host events from L.p4_events (F, agent, unit, day, t, T, d, n10 via lm fields, nread, touched)."""
    if E is None or E["F"].sum() < 5 or (~E["F"]).sum() < 5:
        return None
    rng = np.random.default_rng(seed)
    F = E["F"]
    # follow-up lengths in calls (1-20) and the landmark (call 10), from the real skeleton: n20 = T when not
    # re-expressed, else unknown -> use the real follow-up length recorded in E["n20"], E["n10"]
    n20, n10 = E["n20"], np.minimum(E["n10"], E["n20"])
    h0 = float(E["d"].sum() / max(E["T"].sum(), 1.0))       # arm-blind pooled per-call rate
    Rp = (E["nread"] > 0) | E["touched"]
    res = {"h0": h0, "n_F": int(F.sum()), "n_P": int((~F).sum()), "share_Rplus": float(Rp.mean())}
    for lab, r, g in (("K2_world_r0.5", 0.5, 1.0), ("survive_r1", 1.0, 1.0), ("readgate_g2", 1.0, 2.0)):
        lt05, ge08, rg = [], [], []
        for _ in range(reps):
            ha = {a_: h0 * np.exp(rng.normal(0, 0.7)) for a_ in np.unique(E["agent"])}
            h = np.array([ha[a_] for a_ in E["agent"]]) * np.where(F, r, 1.0)
            t1 = rng.geometric(np.clip(h, 1e-6, 1))
            e10 = t1 <= n10
            t2 = n10 + rng.geometric(np.clip(h * np.where(Rp, g, 1.0), 1e-6, 1))
            te = np.where(e10, t1, t2)
            d = (te <= n20).astype(float)
            Ep = dict(E)
            Ep["d"] = d
            Ep["T"] = np.where(d > 0, te, n20).astype(float)
            Ep["expr10"] = e10.astype(int)
            lm = (d > 0) & ~e10
            Ep["lm_d"] = lm.astype(float)
            Ep["lm_T"] = np.where(lm, te - n10, np.maximum(n20 - n10, 0)).astype(float)
            o = L.p4_stats(Ep, B=B, seed=int(rng.integers(1e9)))
            if o is None:
                continue
            lt05.append(o["HR_F_vs_P"] < 0.5)
            ge08.append(o["HR_F_vs_P"] >= 0.8)
            x = o.get("HR_read_F")
            rg.append(bool(x and np.isfinite(x["ci"][0]) and x["ci"][0] > 1))
        res[lab] = {"reps": len(lt05), "share_HR_lt_0.5": float(np.mean(lt05)) if lt05 else None,
                    "share_HR_ge_0.8": float(np.mean(ge08)) if ge08 else None,
                    "share_readgate_ci_above1": float(np.mean(rg)) if rg else None}
    return res


def p5_power(ev_mask, agent, strata, cluster, counts, ratio=1.5, reps=60, seed=0, B=150):
    """ev_mask: bool, True = event arm; counts: the real counts (used only for the arm-blind pooled mean)."""
    if ev_mask.sum() < 3 or (~ev_mask).sum() < 3:
        return {"reps": 0, "power": 0.0, "note": "too few rows"}
    rng = np.random.default_rng(seed)
    mu0 = float(np.mean(counts))
    if mu0 <= 0:
        return {"reps": 0, "power": 0.0, "mu0": 0.0, "note": "no repair messages in either arm"}
    out = {}
    for lab, rr_ in (("power", ratio), ("size", 1.0)):
        rej = []
        for _ in range(reps):
            mu_a = {a_: rng.gamma(4.0, mu0 / 4.0) for a_ in np.unique(agent)}
            mu = np.array([mu_a[a_] for a_ in agent]) * np.where(ev_mask, rr_, 1.0)
            c = rng.poisson(rng.gamma(1.0, mu)).astype(float)
            est, lo, hi, _ = L.cluster_boot_rr(np.where(ev_mask, c, 0), ev_mask.astype(float),
                                               np.where(~ev_mask, c, 0), (~ev_mask).astype(float), strata, cluster,
                                               B=B, seed=int(rng.integers(1e9)))
            rej.append(bool(np.isfinite(est) and np.isfinite(lo) and lo > 1 and est > 1.2))
        out[lab] = float(np.mean(rej))
    out.update({"reps": reps, "ratio": ratio, "mu0": mu0, "n_event": int(ev_mask.sum()),
                "n_placebo": int((~ev_mask).sum())})
    return out
