"""H28 exploratory round 1: per goal period, non-holdout days only.

  uv run python hypotheses/H28-links-spread-herding/analysis/explore.py --goals 31 41 [--shifts 99] [--sims 200]

For each period writes data/processed/H28-links-spread-herding/G<NN>/round1.json with: primary fit (kappa, J), link
time-shift null, kernel, dose-response and simple-vs-complex held-out likelihood, lead / momentum / room / naive rivals,
action-only and U+ robustness, project x day variant, lambda and R_link, the event-study pre-trend, NE09 latency, and
the counterfactual simulations (link thinning f = 1, 0.5, 0 and a 2-h cap) with observed pile-on sizes.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import numpy as np
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h28core as hc  # noqa: E402
from h28lib import ALL_PERIODS, MULTIROOM, OUT, assert_not_holdout, gname, write_provenance  # noqa: E402

MIN_ARRIVALS, MIN_LINKS = 30, 20


def _c(res, name):
    b, se = hc.coef(res, name)
    p = float(2 * norm.sf(abs(b / se))) if np.isfinite(se) and se > 0 else float("nan")
    return dict(b=b, se=se, p=p)


def _diff(res, a, b):
    if res is None or a not in res["names"] or b not in res["names"]:
        return dict(d=float("nan"), p=float("nan"), se=float("nan"))
    i, j = res["names"].index(a), res["names"].index(b)
    d = res["beta"][i] - res["beta"][j]
    v = res["V"][i, i] + res["V"][j, j] - 2 * res["V"][i, j]
    return dict(d=float(d), p=float(norm.sf(d / np.sqrt(v))) if v > 0 else float("nan"),
                se=float(np.sqrt(v)) if v > 0 else float("nan"))


def run_period(g, shifts=99, sims=200, lat_shifts=49, seed=28, folder=None, verbose=True):
    t0 = time.time()
    folder = folder or OUT / gname(g)
    P = hc.load_period(folder)
    R, B, G = hc.build_rows(P)
    P["_B"] = B
    F = hc.link_features(P, R)
    rng = np.random.default_rng(seed + g)
    out = dict(goal=g, days=len(P["days"]), agents=len(P["agents"]), K=P["K"], rows=int(len(R["y"])),
               arrivals=int(R["y"].sum()), arrivals_first=int(R["y"][R["own_ever"] == 0].sum()),
               links_universe=int((P["links"]["x"] >= 0).sum()), link_msgs=int(len(np.unique(P["links"]["msg"]))),
               rooms=sorted(set(int(r) for r in P["active"]["room"].tolist())), pre_ne09=P["pre_ne09"])
    out["tested"] = bool(out["arrivals"] >= MIN_ARRIVALS and out["links_universe"] >= MIN_LINKS)
    out["exposed_rows"] = int(F["E60"].sum())
    out["exposed_arrivals"] = int(R["y"][F["E60"] > 0].sum())
    res = hc.fit(R, F, "primary")
    out["primary"] = {n: _c(res, n) for n in res["names"]}
    out["kappa"], out["se"], out["p"] = out["primary"]["E60"]["b"], out["primary"]["E60"]["se"], out["primary"]["E60"]["p"]
    out["J"] = out["primary"]["log_occ"]["b"]
    # N1: link time-shift null
    null = []
    for _ in range(shifts):
        lt, tv = hc.shift_links(P, rng)
        Fs = hc.link_features(P, R, link_t=lt, t_vis=tv)
        null.append(hc.coef(hc.fit(R, Fs, "primary"), "E60")[0])
    null = np.array([v for v in null if np.isfinite(v)])
    out["null"] = dict(mean=float(null.mean()), sd=float(null.std(ddof=1)), n=int(len(null)),
                       q95=float(np.percentile(null, 95)))
    out["z_shift"] = float((out["kappa"] - null.mean()) / null.std(ddof=1))
    out["p_shift"] = float((1 + np.sum(null >= out["kappa"])) / (1 + len(null)))
    if verbose:
        print(f"  {gname(g)} primary + {shifts} shifts {time.time() - t0:.0f}s: kappa {out['kappa']:+.2f} "
              f"(se {out['se']:.2f}) z_shift {out['z_shift']:+.1f}", flush=True)
    # kernel, dose
    rk = hc.fit(R, F, "kernel")
    out["kernel"] = {n: _c(rk, n) for n in ("lE015", "lE1560", "lE60240")}
    rd = hc.fit(R, F, "dose")
    out["dose"] = {n: _c(rd, n) for n in ("d11", "d12", "d13", "dS2")}
    out["dose_n"] = {n: int(F[n].sum()) for n in ("d11", "d12", "d13", "dS2")}
    out["dose_events"] = {n: int(R["y"][F[n] > 0].sum()) for n in ("d11", "d12", "d13", "dS2")}
    rc = hc.fit(R, F, "complex")
    out["complex_S2"] = _c(rc, "dS2any")
    out["cv"] = hc.cv_quarters(R, F, specs=("fields", "occ_only", "primary", "simple", "complex", "threshold"))
    # rivals
    rl = hc.fit(R, F, "lead")
    out["lead"] = dict(kappa=_c(rl, "E60"), lead=_c(rl, "lead60"), diff=_diff(rl, "E60", "lead60"))
    rm = hc.fit(R, F, "momentum")
    out["momentum"] = dict(kappa=_c(rm, "E60"), mom=_c(rm, "mom30"))
    if len(out["rooms"]) > 1 or g in MULTIROOM:
        rr = hc.fit(R, F, "room")
        out["room"] = dict(same=_c(rr, "E60"), other=_c(rr, "other60"), diff=_diff(rr, "E60", "other60"),
                           other_rows=int(F["other60"].sum()), other_events=int(R["y"][F["other60"] > 0].sum()))
    naive = R["own_ever"] == 0
    rn = hc.fit(R, F, [n for n in hc.SPECS["primary"] if n not in ("own_ever", "log_own")], rows=naive)
    out["naive"] = _c(rn, "E60")
    ra = hc.fit(R, F, "addressed")
    out["addressed"] = dict(kappa=_c(ra, "E60"), addr=_c(ra, "addr60"), n=int(F["addr60"].sum()))
    rpd = hc.fit(R, F, "primary", fe="pd")
    out["pd"] = dict(kappa=_c(rpd, "E60"), J=_c(rpd, "log_occ"))
    roc = hc.fit(R, F, "occ_only")
    out["J_without_links"] = _c(roc, "log_occ")
    ryA = hc.fit(R, F, "primary", y="ya")
    out["action_only"] = _c(ryA, "E60")
    try:
        Pu = hc.load_period(folder, universe="U+")
        Ru, Bu, Gu = hc.build_rows(Pu)
        Fu = hc.link_features(Pu, Ru)
        out["Uplus"] = dict(K=Pu["K"], kappa=_c(hc.fit(Ru, Fu, "primary"), "E60"), arrivals=int(Ru["y"].sum()))
    except Exception as e:      # noqa: BLE001
        out["Uplus"] = dict(error=str(e))
    # infection rate and branching
    nexp = hc.count_exposures(P)
    out["attr"] = hc.attributable(res, R, F, nexp, link_names=("E60",), draws=400, rng=rng)
    out["attr_with_old"] = hc.attributable(res, R, F, nexp, link_names=("E60", "Eold"), draws=0)
    att_occ = hc.attributable(res, R, F, nexp, link_names=("E60", "log_occ"), draws=0)
    out["R_all"] = att_occ["R_link"]
    links_by_agents = int(((P["links"]["x"] >= 0) & (P["links"]["sender"] >= 0)).sum())
    out["pi_links_per_arrival"] = links_by_agents / max(out["arrivals"], 1)
    out["k_s_per_link"] = nexp / max(out["links_universe"], 1)
    # event study (naive agents, around first visible link)
    rf = hc.fit(R, F, "fields")
    out["event_study"] = hc.event_study(P, R, F, rf)
    # NE09 latency
    out["latency"] = hc.latency(P, shifts=lat_shifts)
    if verbose:
        print(f"  {gname(g)} rivals/latency {time.time() - t0:.0f}s", flush=True)
    # counterfactual
    obs = hc.observed_pileups(P, B, G)
    out["pileups_observed"] = obs
    if sims:
        sim = hc.Simulator(P, R, B, G, res, F)
        srng = np.random.default_rng(seed * 1000 + g)
        cf = {}
        for lab, kw in [("f1", dict(f=1.0)), ("f05", dict(f=0.5)), ("f0", dict(f=0.0)), ("cap2h", dict(f=1.0, cap_ms=7_200_000))]:
            runs = [sim.run(srng, **kw) for _ in range(sims)]
            cf[lab] = {k: [int(r[k]) for r in runs] for k in ("peak_occ", "burst60", "top_visitors", "arrivals")}
        out["counterfactual"] = cf
        f1 = cf["f1"]
        out["cf_summary"] = {}
        for lab in ("f05", "f0", "cap2h"):
            out["cf_summary"][lab] = {k: float(np.mean(cf[lab][k]) / max(np.mean(f1[k]), 1e-9)) for k in f1}
        out["cf_calibration"] = {k: dict(obs=obs[k], lo=float(np.percentile(f1[k], 5)), hi=float(np.percentile(f1[k], 95)),
                                         mean=float(np.mean(f1[k])), inside=bool(np.percentile(f1[k], 5) <= obs[k]
                                                                                   <= np.percentile(f1[k], 95)))
                                 for k in ("peak_occ", "burst60", "top_visitors")}
        out["cf_calibration"]["arrivals"] = dict(obs=out["arrivals"], mean=float(np.mean(f1["arrivals"])))
    out["secs"] = time.time() - t0
    (folder / "round1.json").write_text(json.dumps(out, indent=1, default=float))
    if verbose:
        print(f"{gname(g)} done in {out['secs']:.0f}s", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="*", default=None)
    ap.add_argument("--shifts", type=int, default=99)
    ap.add_argument("--sims", type=int, default=200)
    ap.add_argument("--lat-shifts", type=int, default=49)
    a = ap.parse_args()
    goals = a.goals or ALL_PERIODS
    assert_not_holdout(goals)
    for g in goals:
        run_period(g, shifts=a.shifts, sims=a.sims, lat_shifts=a.lat_shifts)
    write_provenance(OUT, "hypotheses/H28-links-spread-herding/analysis/explore.py", ["H28 scheme outputs (G<NN>/*.parquet)"],
                     {"shifts": a.shifts, "sims": a.sims, "lat_shifts": a.lat_shifts, "fe": "agent + project + day",
                      "goals": goals}, key=f"explore_{'_'.join(map(str, goals))}")


if __name__ == "__main__":
    main()
