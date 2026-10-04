"""H14 recheck of the round-1 collective term (O4 / P4, HH67) after the `ep_gauss_crossfit` fix (2026-10-04).

The collective term is a difference of Newton bounds on nested observable sets, Delta_w = Sigma(single u w) -
Sigma(single), with d (225-1,200 observables) a sizeable fraction of T (1,000-5,500 minute transitions): exactly the
case where the legacy cross-product form with a subset-dependent scalar ridge is biased (infra/README "Known issues",
H90). This script recomputes the collective block of `run_period.py` with both estimators on the same grid and the
same cross-day surrogates:
  old  h14lib._newton_subsets_xprod (= round 1's newton_subsets; must reproduce the stored point estimates exactly)
  new  ep_newton.newton_subsets_heldout with blocks single / mf / pw (per-column ridge floored by the block mean)
Non-holdout only (run_period.period_days asserts it). Single-agent and round-1b numbers are rechecked by running
round1b.py / native_r1b.py with H14_EP=heldout (outputs in r1b/recheck_epfix/).

Usage: uv run python hypotheses/H14-behavior-entropy-production/analysis/recheck_epfix.py [--period G38 ...] [--R 100]
Writes data/processed/H14-behavior-entropy-production/recheck_epfix/collective.json (+ _provenance.json).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_period as RP  # noqa: E402  (imports h14lib, which sets the thread caps)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

L = RP.L
ROOT = RP.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
import ep_newton as E  # noqa: E402
from common import git_commit, holdout_mask  # noqa: E402

OUTD = RP.DATA / "recheck_epfix"
REGIME3 = ["G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
KEYS = ("sigma1", "delta_mf", "delta_pw", "sigma_mf_alone", "sigma_pw_alone")


def both(X):
    """Collective statistics with the legacy and the corrected estimator on one aligned grid (n_days, L+1, N)."""
    Xp, Xn, d = L.stack_aligned(X)
    B = L.collective_blocks(Xp, Xn, 6, RP.WORK, RP.CHAT, which=("single", "mf", "pw"))
    blocks = [("single", B["single"]), ("mf", B["mf"]), ("pw", B["pw"])]
    G = np.hstack([b for _, b in blocks])
    idx, o = {}, 0
    for nm, b in blocks:
        idx[nm] = np.arange(o, o + b.shape[1])
        o += b.shape[1]
    blk = np.concatenate([np.full(len(idx[nm]), k) for k, (nm, _) in enumerate(blocks)])
    subsets = {"sigma1": idx["single"], "sigma1_mf": np.r_[idx["single"], idx["mf"]],
               "sigma1_pw": np.r_[idx["single"], idx["pw"]], "sigma_mf_alone": idx["mf"], "sigma_pw_alone": idx["pw"]}
    old = L._newton_subsets_xprod(G, d, subsets)
    new, folds = E.newton_subsets_heldout(G, d, subsets, block=blk, return_folds=True)
    out = {"d_single": len(idx["single"]), "d_mf": len(idx["mf"]), "d_pw": len(idx["pw"]), "T": int(len(G))}
    for tag, r in (("old", old), ("new", new)):
        out[tag] = {"sigma1": r["sigma1"], "delta_mf": r["sigma1_mf"] - r["sigma1"], "delta_pw": r["sigma1_pw"] - r["sigma1"],
                    "sigma_mf_alone": r["sigma_mf_alone"], "sigma_pw_alone": r["sigma_pw_alone"]}
    for w in ("mf", "pw"):
        dv = np.array(folds[f"sigma1_{w}"]) - np.array(folds["sigma1"])
        out["new"][f"delta_{w}_fold_se"] = float(dv.std(ddof=1) / np.sqrt(len(dv))) if len(dv) > 1 else np.nan
    return out


def holm(ps):
    ps = np.asarray(ps, float)
    o = np.argsort(ps)
    m = len(ps)
    adj = np.empty(m)
    run = 0.0
    for r, i in enumerate(o):
        run = max(run, min(1.0, (m - r) * ps[i]))
        adj[i] = run
    return adj


def period(p, sm_all, roster_cc, R_arg):
    spec = RP.PERIODS[p]
    cal_days = RP.period_days(spec)                       # asserts no holdout day
    days = cal_days["pt_date"].to_list()
    assert not any(holdout_mask(days, cal_days["goal_no"].to_list()))
    sm = sm_all.filter(pl.col("pt_date").is_in(days))
    cdays = days
    if spec.get("block"):
        lo, hi = spec["block"]
        cdays = [x for x in days if lo <= x < hi]
    X, agents, ok_days = RP.aligned_grid(sm, cdays)
    if any(a in roster_cc for a in agents):
        keep = [i for i, a in enumerate(agents) if a not in roster_cc]
        X, agents = X[:, :, keep], [agents[i] for i in keep]
    if not (X.shape[0] >= 3 and X.shape[2] >= 4):
        return {"skipped": f"{X.shape[0]} days x {X.shape[2]} agents"}
    R = R_arg or (40 if X.shape[2] > 20 else 100)
    rng = np.random.default_rng(20261004 + int(p[1:]))
    t0 = time.time()
    obs = both(X)
    Xp, Xn, d = L.stack_aligned(X)
    s1cfx = float(np.nansum([L.ep_cfx(Xp[:, i], Xn[:, i], d, 6) for i in range(X.shape[2])]))
    nulls = [both(L.crossday_surrogate(X, rng)) for _ in range(R)]
    res = {"N": int(X.shape[2]), "n_days": int(X.shape[0]), "T": obs["T"], "d_single": obs["d_single"], "d_mf": obs["d_mf"],
           "d_pw": obs["d_pw"], "R": R, "sigma1_cfx_sum": s1cfx}
    for tag in ("old", "new"):
        r = {}
        for k in KEYS:
            v = np.array([x[tag][k] for x in nulls])
            r[k] = obs[tag][k]
            r[f"{k}_null_mean"] = float(v.mean())
            r[f"{k}_null_sd"] = float(v.std(ddof=1))
            r[f"{k}_p"] = float((1 + np.sum(v >= obs[tag][k])) / (R + 1))
            r[f"{k}_exc"] = float(obs[tag][k] - v.mean())
        for w in ("mf", "pw"):
            r[f"ratio_delta_{w}_exc_to_sigma1_cfx"] = r[f"delta_{w}_exc"] / s1cfx if s1cfx > 0 else np.nan
            r[f"ratio_delta_{w}_exc_to_sigma1"] = r[f"delta_{w}_exc"] / r["sigma1"] if r["sigma1"] > 0 else np.nan
            if tag == "new":
                r[f"delta_{w}_fold_se"] = obs["new"][f"delta_{w}_fold_se"]
        res[tag] = r
    stored = RP.DATA / p / "results.json"
    if stored.exists():
        c = json.loads(stored.read_text()).get("collective", {})
        res["stored_round1"] = {k: c.get(k) for k in ("sigma1", "delta_mf", "delta_pw", "delta_mf_p", "delta_pw_p",
                                                       "delta_mf_exc", "delta_pw_exc", "delta_mf_null_mean",
                                                       "delta_pw_null_mean", "ratio_delta_mf_exc_to_sigma1_cfx",
                                                       "ratio_delta_pw_exc_to_sigma1_cfx", "N", "n_days")}
        res["legacy_reproduces_stored"] = bool(all(np.isclose(res["old"][k], c[k], rtol=1e-9, atol=1e-12)
                                                   for k in ("sigma1", "delta_mf", "delta_pw") if k in c))
    res["runtime_s"] = time.time() - t0
    print(p, f"N={res['N']} days={res['n_days']} T={res['T']} d={obs['d_single']}+{obs['d_mf']}+{obs['d_pw']}",
          {t: {k: round(res[t][k], 4) for k in ("sigma1", "delta_mf", "delta_mf_p", "delta_pw", "delta_pw_p",
                                                "delta_pw_exc", "delta_pw_null_mean")} for t in ("old", "new")},
          "repro", res.get("legacy_reproduces_stored"), f"{res['runtime_s']:.0f}s", flush=True)
    return res


def write_estimates():
    """Per-period rows (held-out Newton collective excess, MF and PW) -> shared per_period_estimates. The round-1
    backfill rows (legacy Newton, source G<NN>/results.json) stay; these carry their own method and source."""
    import estimates as ES
    out = json.loads((OUTD / "collective.json").read_text())
    rows = []
    for p, r in out.items():
        if "new" not in r:
            continue
        g = int(p[1:])
        days = json.loads((RP.DATA / p / "results.json").read_text())["collective"]["days"]
        u = ES.map_unit(g, days[0], days[-1]) or f"G{g:02d}"
        for w, nm in (("mf", "mean-field"), ("pw", "pairwise")):
            n = r["new"]
            rows.append(dict(period_unit=u, goal_no=g, statistic=f"collective_ep_excess_{w}", channel="activity",
                             estimate=n[f"delta_{w}_exc"], se=n[f"delta_{w}_null_sd"], ci_kind="none", n=r["n_days"],
                             n_kind="days", unit_local="nats per minute step (whole swarm)", role="replication",
                             first_day=days[0], last_day=days[-1], post_hoc=True,
                             method=f"{nm} collective EP (held-out Newton, per-column block-floored ridge) minus cross-day "
                                    "surrogate mean [ep_gauss_crossfit recheck]",
                             null=f"cross-day surrogate ({r['R']})",
                             source="data/processed/H14-behavior-entropy-production/recheck_epfix/collective.json",
                             notes=f"p {n[f'delta_{w}_p']:.3f}, Holm {n.get(f'delta_{w}_p_holm')}; legacy excess "
                                   f"{r['old'][f'delta_{w}_exc']:.4f} (p {r['old'][f'delta_{w}_p']:.3f}); se = null SD"))
    res = ES.write_estimates(rows, hypothesis="H14")
    print(res.height, "rows written")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", nargs="*")
    ap.add_argument("--R", type=int, default=None)
    ap.add_argument("--write-estimates", action="store_true")
    a = ap.parse_args()
    if a.write_estimates:
        write_estimates()
        return
    sm_all = pl.read_parquet(RP.DATA / "states_min.parquet")
    roster = pl.read_parquet(RP.SH / "roster.parquet")
    roster_cc = set(roster.filter(pl.col("claude_code"))["agent"].to_list())
    OUTD.mkdir(parents=True, exist_ok=True)
    f = OUTD / "collective.json"
    out = json.loads(f.read_text()) if f.exists() else {}
    for p in (a.period or list(RP.PERIODS)):
        out[p] = period(p, sm_all, roster_cc, a.R)
        f.write_text(json.dumps(out, indent=1, default=float))
    done = [p for p in REGIME3 if p in out and "new" in out[p]]
    for tag in ("old", "new"):
        for w in ("mf", "pw"):
            adj = holm([out[p][tag][f"delta_{w}_p"] for p in done])
            for p, v in zip(done, adj):
                out[p][tag][f"delta_{w}_p_holm"] = float(v)
    f.write_text(json.dumps(out, indent=1, default=float))
    (OUTD / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H14-behavior-entropy-production/analysis/recheck_epfix.py", "git_commit": git_commit(),
        "inputs": ["data/processed/H14-behavior-entropy-production/states_min.parquet", "shared/calendar.parquet",
                   "shared/roster.parquet"],
        "params": {"R": a.R, "ridge_c": E.RIDGE_C, "seed": "20261004 + goal"},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))


if __name__ == "__main__":
    main()
