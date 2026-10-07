"""H134 round 1, real data (exploration units only): O1-O5 per unit, written to results/<unit>.json.

Per unit (card, Observables; amendments in the card's Round 1 section):
  O1  agent-FE logit of leaving: (a) B + F + K, (b) B + F + A + K. B = nuisance z; F = ln(1 - f_proj); A = ln d;
      K = ln(1 + N^nam_other). CIs: agent-day block bootstrap (A2), 200 draws; Wald and agent-day cluster SEs reported.
  O2  day-blocked CV (k = min(5, days)) per-day held-out LL of B, B+A, B+F, B+F+A (K in B).
  O3  fit B + F (+K, no ln d); 200 forward copies on the real paths, censored at the real end; bands for gamma, KM at
      d = 10, 30, 100, 300, P90 of completed dwell.
  O4  rows for the pooled reset contrast (written; combined across units in summarize.py).
  O5  stay probability by f_proj decile (descriptive).
  Variants (O1 b only): f_lab, f_rec, f_entry; drop kickoff window; drop calls that read a human message.
Usage: uv run python .../analysis/run.py --unit 51c [--boot 200]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h134lib as L  # noqa: E402

import numpy as np  # noqa: E402

EXTRA = ("kick_nam", "kick4", "human", "f_lab", "f_rec", "f_entry", "goal_no", "turn_id")


def boot_beta(U, cols, z, y, terms, B, seed, idx_all=None):
    """Agent-day block bootstrap of the named coefficients."""
    rng = np.random.default_rng(seed)
    blk = U["agent"] * 1000 + U["day"]
    if idx_all is not None:
        blk = blk[idx_all]
    _, code = np.unique(blk, return_inverse=True)
    order = np.argsort(code, kind="stable")
    cuts = np.flatnonzero(np.diff(code[order])) + 1
    groups = np.split(order, cuts)
    out = []
    agent = U["agent"] if idx_all is None else U["agent"][idx_all]
    for _ in range(B):
        pick = rng.integers(0, len(groups), len(groups))
        ii = np.concatenate([groups[k] for k in pick])
        try:
            fr = L.fit({k: v[ii] for k, v in cols.items()}, {k: v[ii] for k, v in z.items()}, agent[ii], y[ii])
            out.append([fr["beta"][t] for t in terms])
        except Exception:  # noqa: BLE001
            continue
    a = np.array(out, float)
    return {t: L.pct(a[:, j]) for j, t in enumerate(terms)}


def o1(U, fvar="f", mask=None, B=200, seed=0, boot=True):
    m = np.ones(U["n"], bool) if mask is None else mask
    z = {k: v[m] for k, v in U["z"].items()}
    y = U["y"][m]
    F = L.lnq(U[fvar][m]); A = np.log(U["d"][m]); K = np.log1p(U["kick_nam"][m].astype(float))
    agent = U["agent"][m]; cl = agent * 1000 + U["day"][m]
    res = {"n_rows": int(m.sum()), "n_leave": int(y.sum())}
    for nm, cols in (("a", {"F": F, "K": K}), ("b", {"F": F, "A": A, "K": K})):
        fr = L.fit(cols, z, agent, y, cluster=cl)
        r = {t: {"est": fr["beta"][t], "se": fr["se"][t], "se_cl": fr["se_cl"][t]} for t in cols}
        if boot:
            bb = boot_beta(U, cols, z, y, list(cols), B, seed + (nm == "b"), idx_all=np.flatnonzero(m))
            for t in cols:
                r[t]["ci"] = bb[t]
        r["conv"] = fr["conv"]
        res[nm] = r
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", required=True)
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--sim-reps", type=int, default=200)
    a = ap.parse_args()
    t0 = time.time()
    U = L.load_unit(a.unit, extra=EXTRA)
    U["kick_nam"] = U["kick_nam"].astype(float)
    res = {"unit": a.unit, "n_rows": U["n"], "n_visits": int(len(U["s"])), "n_days": len(U["days"]),
           "mean_f": float(U["f"].mean()), "sd_lnq": float(L.lnq(U["f"]).std())}
    # O1 primary
    res["O1"] = o1(U, B=a.boot, seed=L.SEED)
    print(a.unit, "O1", f"{time.time() - t0:.0f}s", flush=True)
    # O1 variants (b only, cluster SE, no bootstrap)
    var = {}
    for fv in ("f_lab", "f_rec", "f_entry"):
        var[fv] = o1(U, fvar=fv, boot=False)["b"]["F"]
    var["drop_kickoff4"] = o1(U, mask=~U["kick4"], boot=False)["b"]["F"] if (~U["kick4"]).sum() < U["n"] and (~U["kick4"]).sum() > 1000 else None
    var["drop_human_read"] = o1(U, mask=~U["human"], boot=False)["b"]["F"] if U["human"].any() else None
    res["O1_variants"] = var
    # O2 eps(F)
    z = dict(U["z"]); z["K"] = np.log1p(U["kick_nam"])
    F = L.lnq(U["f"]); A = np.log(U["d"])
    nd = len(U["days"])
    if nd >= 2:
        cv = L.cv_eps(F, A, z, U["agent"], U["y"], U["day"], k=min(5, nd), boot=1000, seed=L.SEED)
        res["O2"] = {k: v for k, v in cv.items() if k != "per"}
        res["O2"]["per"] = {k: v.tolist() for k, v in cv["per"].items()}
    # O3 calibration
    fa = L.fit({"F": F}, z, U["agent"], U["y"])
    p = L.predict(fa, {"F": F}, z, U["agent"])
    s, e = U["s"], U["e"]
    comp = U["y"][e - 1] == 1
    obs = L.dwell_stats(U["d"], U["y"], np.ones(U["n"], bool), U["d"][e - 1][comp])
    rng = np.random.default_rng(L.SEED + 3)
    sims = L.simulate_dwell(p, U["d"], s, e, rng, reps=a.sim_reps)
    res["O3"] = L.calib(obs, sims)
    res["O3"]["n_completed"] = int(comp.sum())
    # amendment A6 variants: coefficient draws (forward), and posterior-predictive on the observed risk rows
    fd = L.fit_draws({"F": F}, z, U["agent"], U["y"], U["agent"] * 1000 + U["day"])
    res["O3draw"] = L.calib(obs, L.simulate_dwell_draws(fd, U["d"], s, e, rng, reps=a.sim_reps))
    res["O3pp"] = L.calib(obs, L.predictive_dwell(fd, U["d"], rng, reps=a.sim_reps))
    # O4 per unit (reset contrast) and placebo
    fb = res["O1"]["b"]["F"]["est"]
    (lor, se, nt), _ = L.reset_contrast(U["y"], U["d"], U["f"], U["f_pre"], U["forced"], U["agent"], U["forced"])
    sel = U["forced"] & (U["d"] >= L.D_RESET)
    pred = float(np.mean(-fb * L.lnq(U["f_pre"][sel]))) if sel.any() else None
    (plor, pse, pnt), _ = L.reset_contrast(U["y"], U["d"], U["f"], U["f"], U["forced"], U["agent"], U["pseudo"] & ~U["forced"])
    res["O4"] = {"lor": lor, "se": se, "n_treated": nt, "pred": pred, "mean_f_pre": float(U["f_pre"][sel].mean()) if sel.any() else None,
                 "placebo": {"lor": plor, "se": pse, "n_treated": pnt}}
    # O5 calibration curve
    q = L.deciles(U["f"])
    res["O5"] = [{"decile": int(k), "f_mean": float(U["f"][q == k].mean()), "stay": float(1 - U["y"][q == k].mean()),
                  "n": int((q == k).sum())} for k in np.unique(q)]
    L.jdump(res, L.OUT / "results" / f"{a.unit}.json")
    print(a.unit, "done", f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
