"""H134 synthetic validation (axis F), run before any H134 statistic on real data.

Skeletons (card): the real visit and touch paths of 51c, 51h (G51) and 38a (G38) from scheme/build.py: real calls,
real forced and voluntary resets, real touch patterns, so the real f_proj, d and visit-touch paths. Only the leave
outcome is simulated: per world, a per-call leave probability along each real path; the first hit ends the visit,
otherwise it is censored at the real end (real censoring). No real outcome is read.
Worlds (card, Synthetic validation plan; agent intercepts SD 0.5; covariates centred so the leave rate is similar):
  W0 geometric; W1 urn beta_F = 1; W2 intrinsic aging beta_d = -0.4; W3 per-visit frailty SD 1.5;
  W4 store: -0.6 ln(1 + touches earlier in the visit) (resets do not change it); W5 0.5 urn + (-0.2) aging.
Per run: O1 (beta_F in models a, b; Wald and agent-day cluster SEs), O2 eps(F) (day-blocked CV; first --cv-reps runs),
O3 calibration (fit B+F, forward copies, 95% bands), O4 reset step and pseudo-reset placebo (MH log OR, RBG SE).
Output: data/processed/H134-polya-urn-project-stickiness/synthetic/<unit>.json
Usage: uv run python .../analysis/synthetic.py --unit 51h --reps 200 --cv-reps 100
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h134lib as L  # noqa: E402

import numpy as np  # noqa: E402

WORLDS = ("W0", "W1", "W2", "W3", "W4", "W5")
ALPHA0 = -2.4   # per-row leave rate near the real completed-visit count ratio (about 0.08)


def gen(U: dict, w: str, rng) -> dict:
    ua = np.unique(U["agent"])
    al = dict(zip(ua, ALPHA0 + 0.5 * rng.standard_normal(len(ua))))
    a_i = np.array([al[a] for a in U["agent"]])
    s, e = U["s"], U["e"]
    u = (1.5 * rng.standard_normal(len(s)))[U["vidx"]]
    d, ntv = U["d"], U["ntv"]
    lq = L.lnq(U["f"])
    lq0 = np.median(lq)
    ld = np.log(d) - np.log(20)
    eta = {"W0": a_i, "W1": a_i + (lq - lq0), "W2": a_i - 0.4 * ld, "W3": a_i + u,
           "W4": a_i - 0.6 * (np.log1p(ntv) - np.log(6)), "W5": a_i + 0.5 * (lq - lq0) - 0.2 * ld}[w]
    p = 1 / (1 + np.exp(-eta))
    hit = rng.random(len(p)) < p
    fh = L.first_hits(hit, s, e)
    stop = np.where(fh >= 0, fh, e - 1)
    keep = np.arange(len(p)) <= stop[U["vidx"]]
    y = np.zeros(len(p)); y[fh[fh >= 0]] = 1
    return {"keep": keep, "y": y[keep], "n_completed": int((fh >= 0).sum())}


def analyse(U: dict, keep: np.ndarray, y: np.ndarray, rng, do_cv: bool, reps_sim: int) -> dict:
    agent = U["agent"][keep]; day = U["day"][keep]
    z = {k: v[keep] for k, v in U["z"].items()}
    d = U["d"][keep]; f = U["f"][keep]; fpre = U["f_pre"][keep]
    forced = U["forced"][keep]; pseudo = U["pseudo"][keep]
    F = L.lnq(f); A = np.log(d)
    cl = agent * 1000 + day
    out = {"n_rows": int(len(y)), "n_leave": int(y.sum())}
    fa = L.fit({"F": F}, z, agent, y, cluster=cl)
    fb = L.fit({"F": F, "A": A}, z, agent, y, cluster=cl)
    out["bF_a"] = [fa["beta"]["F"], fa["se"]["F"], fa["se_cl"]["F"]]
    out["bF_b"] = [fb["beta"]["F"], fb["se"]["F"], fb["se_cl"]["F"]]
    out["bd_b"] = [fb["beta"]["A"], fb["se"]["A"], fb["se_cl"]["A"]]
    if do_cv:
        cv = L.cv_eps(F, A, z, agent, y, day)
        out["G_A"], out["G_F"], out["eps_F"] = cv["G_A"], cv["G_F"], cv["eps_F"]
        out["cv_per"] = {k: v.tolist() for k, v in cv["per"].items()}
    # O3: forward copies from the fitted B+F along the (kept) real paths
    p = L.predict(fa, {"F": F}, z, agent)
    s, e = L.visit_bounds(U["visit"][keep])
    comp = y[e - 1] == 1
    obs = L.dwell_stats(d, y, np.ones(len(y), bool), d[e - 1][comp])
    sims = L.simulate_dwell(p, d, s, e, rng, reps=reps_sim)
    out["o3"] = L.calib(obs, sims)
    # O4: reset step (d >= 10) and pseudo-reset placebo
    (lor, se, nt), _ = L.reset_contrast(y, d, f, fpre, forced, agent, forced)
    sel = forced & (d >= L.D_RESET)
    pred = float(np.mean(fb["beta"]["F"] * L.lnq(fpre[sel]) * -1.0)) if sel.any() else float("nan")
    out["o4"] = [lor, se, nt, pred]
    (plor, pse, pnt), _ = L.reset_contrast(y, d, f, f, forced, agent, pseudo & ~forced)
    out["o4_placebo"] = [plor, pse, pnt]
    return out


def analyse_o3(U: dict, keep: np.ndarray, y: np.ndarray, rng, reps_sim: int) -> dict:
    """O3 variants for amendment A6: (fwd) card design; (fwd_draw) forward copies with coefficient draws;
    (pp) posterior-predictive outcomes on the observed risk rows with coefficient draws."""
    agent = U["agent"][keep]; day = U["day"][keep]
    z = {k: v[keep] for k, v in U["z"].items()}
    d = U["d"][keep]; F = L.lnq(U["f"][keep])
    fd = L.fit_draws({"F": F}, z, agent, y, agent * 1000 + day)
    s, e = L.visit_bounds(U["visit"][keep])
    comp = y[e - 1] == 1
    obs = L.dwell_stats(d, y, np.ones(len(y), bool), d[e - 1][comp])
    p = 1 / (1 + np.exp(-(fd["X"] @ fd["beta"])))
    out = {"fwd": L.calib(obs, L.simulate_dwell(p, d, s, e, rng, reps=reps_sim)),
           "fwd_draw": L.calib(obs, L.simulate_dwell_draws(fd, d, s, e, rng, reps=reps_sim)),
           "pp": L.calib(obs, L.predictive_dwell(fd, d, rng, reps=reps_sim))}
    return out


def o3_part(U, unit, reps, reps_sim):
    path = L.OUT / "synthetic" / f"o3_{unit}.json"
    res = {"unit": unit, "worlds": {}}
    for w in WORLDS:
        runs = []
        for r in range(reps):
            rng = np.random.default_rng([L.SEED, 77, WORLDS.index(w), r, sum(map(ord, unit))])
            G = gen(U, w, rng)
            runs.append(analyse_o3(U, G["keep"], G["y"], rng, reps_sim))
        res["worlds"][w] = runs
        L.jdump(res, path)
        print(unit, w, "o3 done", flush=True)


def o4_pool(units, reps, label):
    """O4 power at real counts: rows of all listed units, independent Bernoulli outcomes per risk row (no truncation),
    worlds W0, W1 (beta_F = 1), W4, W5; pooled MH contrast over unit-specific strata; predicted step from the fitted
    planted beta_F, averaged over treated rows."""
    Us = [L.load_unit(u) for u in units]
    res = {"units": units, "worlds": {}}
    for w in ("W0", "W1", "W4", "W5"):
        rows = []
        for r in range(reps):
            ys, ds, fs, fps, frs, ags, preds, nts = [], [], [], [], [], [], [], []
            for k, U in enumerate(Us):
                rng = np.random.default_rng([L.SEED, 99, WORLDS.index(w), r, k])
                ua = np.unique(U["agent"])
                al = dict(zip(ua, ALPHA0 + 0.5 * rng.standard_normal(len(ua))))
                a_i = np.array([al[a] for a in U["agent"]])
                lq = L.lnq(U["f"]); lq0 = np.median(lq); ld = np.log(U["d"]) - np.log(20)
                eta = {"W0": a_i, "W1": a_i + (lq - lq0), "W4": a_i - 0.6 * (np.log1p(U["ntv"]) - np.log(6)),
                       "W5": a_i + 0.5 * (lq - lq0) - 0.2 * ld}[w]
                # a reset call has f = 0 by construction (lq = 0), so W1 carries the urn's step
                y = (rng.random(U["n"]) < 1 / (1 + np.exp(-eta))).astype(float)
                bt = {"W0": 0.0, "W1": 1.0, "W4": 0.0, "W5": 0.5}[w]   # planted beta_F (no refit: speed)
                sel = U["forced"] & (U["d"] >= L.D_RESET)
                preds.append(float(np.sum(-bt * L.lnq(U["f_pre"][sel])))); nts.append(int(sel.sum()))
                ys.append(y); ds.append(U["d"]); fs.append(U["f"]); fps.append(U["f_pre"]); frs.append(U["forced"])
                ags.append(U["agent"] + 1000 * k)
            (lor, se, nt), _ = L.reset_contrast(np.concatenate(ys), np.concatenate(ds), np.concatenate(fs),
                                                np.concatenate(fps), np.concatenate(frs), np.concatenate(ags),
                                                np.concatenate(frs))
            rows.append([lor, se, nt, sum(preds) / max(sum(nts), 1)])
        res["worlds"][w] = rows
        L.jdump(res, L.OUT / "synthetic" / f"o4pool_{label}.json")
        print(label, w, "o4pool done", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", required=True)
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--cv-reps", type=int, default=100)
    ap.add_argument("--sim-reps", type=int, default=200)
    ap.add_argument("--worlds", default=",".join(WORLDS))
    ap.add_argument("--part", default="main", choices=("main", "o3", "o4pool"))
    a = ap.parse_args()
    if a.part == "o4pool":
        units = a.unit.split(",")
        o4_pool(units, a.reps, "G51" if units[0].startswith("51") else "G38")
        return
    if a.part == "o3":
        o3_part(L.load_unit(a.unit), a.unit, a.reps, a.sim_reps)
        return
    U = L.load_unit(a.unit)
    path = L.OUT / "synthetic" / f"{a.unit}.json"
    res = json.loads(path.read_text()) if path.exists() else \
        {"unit": a.unit, "n_rows": U["n"], "n_visits": int(len(U["s"])), "n_forced10": int((U["forced"] & (U["d"] >= 10)).sum()),
         "mean_f": float(U["f"].mean()), "worlds": {}}
    for w in a.worlds.split(","):
        runs = res["worlds"].get(w, [])
        t0 = time.time()
        for r in range(len(runs), a.reps):
            rng = np.random.default_rng([L.SEED, WORLDS.index(w), r, sum(map(ord, a.unit))])
            G = gen(U, w, rng)
            runs.append(analyse(U, G["keep"], G["y"], rng, do_cv=r < a.cv_reps, reps_sim=a.sim_reps))
            runs[-1]["n_completed"] = G["n_completed"]
            if (r + 1) % 20 == 0:
                res["worlds"][w] = runs
                L.jdump(res, path)
                print(f"{a.unit} {w} run {r + 1} {time.time() - t0:.0f}s", flush=True)
        res["worlds"][w] = runs
        L.jdump(res, path)
    print("done", path)


if __name__ == "__main__":
    main()
