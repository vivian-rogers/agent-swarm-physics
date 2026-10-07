"""H135 round-1 analysis on exploration (non-reserved) data.

  POLARS_MAX_THREADS=1 ... uv run python hypotheses/H135-detailed-balance-potts-walker/analysis/run.py [--estimates]

Steps (card order):
  1. structural precondition per unit-channel under both co-alive rules (counts only);
  2. on unit-channels that pass (primary: none; 80% variant: #51 attention units), O1 (pair bootstrap 1,000), O2 m_pi
     and the (theta, beta_pi) binomial fit (pair bootstrap SEs), O3 m_2^co, pair-flip null N1 (2,000), the W0 band
     (N2, from synthetic/<unit>_<channel>.parquet) and the W1 age-drift band, O4 conditional logit with the LR test;
  3. DerSimonian-Laird means across testable unit-channels (raw and W0-centred);
  4. native N3 (G40 hub flux on days 1-2 against the W0 band);
  5. O5 descriptive ownership check on every unit-channel with owned hops;
  6. results/results.json; --estimates writes per_period_estimates rows (roles replication / native).
Every input is non-reserved (asserted by the scheme); nothing here reads reserved rows.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import zlib  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h135lib as L  # noqa: E402
import synthetic as S  # noqa: E402

GOALS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
OWN_ROLE = {39, 42, 51}
RULES = ("coalive", "coalive80")


def unit_data(g, ch):
    d = L.D / f"G{g:02d}"
    return (pl.read_parquet(d / f"hops_{ch}.parquet"), pl.read_parquet(d / f"avail_{ch}.parquet"),
            pl.read_parquet(d / f"occupancy_{ch}.parquet"))


def precondition(h, av, rule):
    co = set(av.filter(pl.col(rule))["project"].to_list())
    hu = h.filter(pl.col("src").is_in(co) & pl.col("dst").is_in(co))
    pc = hu.with_columns(pl.min_horizontal("src", "dst").alias("lo"), pl.max_horizontal("src", "dst").alias("hi")).group_by("lo", "hi").len()
    n4 = int((pc["len"] >= 4).sum()) if pc.height else 0
    return {"co_hops": hu.height, "pairs4": n4, "testable": bool(hu.height >= 60 and n4 >= 8)}


def band(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return [float(np.quantile(x, .025)), float(np.quantile(x, .975)), float(np.median(x))] if len(x) else [np.nan] * 3


def analyse(g, u, ch, rule, h, av, occ, rng):
    pre = "" if rule == "coalive" else "v80_"
    co = set(av.filter(pl.col(rule))["project"].to_list())
    pi = dict(occ.group_by("project").agg(pl.col("pi").first()).iter_rows())
    T = dict(occ.group_by("project").agg(pl.col("T").sum()).iter_rows())
    rank = dict(av.select("project", "age_rank").iter_rows())
    co = {p for p in co if p in pi}
    P = L.pair_table(h, T, pi, rank, co)
    r = {"unit": u, "goal_no": g, "channel": ch, "rule": rule, "n_hops": h.height,
         "n_co_hops": float((P["nab"] + P["nba"]).sum()), "n_pairs": len(P["keys"])}
    r["o1"] = L.o1(P, boot=1000, rng=rng)
    r["m_pi"], r["m2co"] = L.m_pi(P), L.m2_co(P)
    r["binom"] = L.binom_fit(P)
    # pair bootstrap for SEs of m_pi, m2co, theta, beta
    k = len(P["keys"])
    bs = {"m_pi": [], "m2co": [], "theta": [], "beta": []}
    for _ in range(1000):
        i = rng.integers(0, k, k)
        Pb = {key: (v[i] if isinstance(v, np.ndarray) else v) for key, v in P.items()}
        bs["m_pi"].append(L.m_pi(Pb)); bs["m2co"].append(L.m2_co(Pb))
        bf = L.binom_fit(Pb)
        bs["theta"].append(bf["theta"]); bs["beta"].append(bf["beta"])
    for key, v in bs.items():
        v = np.asarray(v, float)
        r[f"{key}_se"] = float(np.nanstd(v))
        r[f"{key}_ci"] = [float(np.nanquantile(v, .025)), float(np.nanquantile(v, .975))]
    fn = L.flip_null(P, 2000, rng)
    r["p_flip_mpi"], r["p_flip_m2"] = L.p_two(r["m_pi"], fn["m_pi"]), L.p_two(r["m2co"], fn["m2co"])
    # W0 band (decision null) and rival bands from the synthetic runs on this skeleton
    f = L.D / "synthetic" / f"{u}_{ch}.parquet"
    if f.exists():
        sy = pl.read_parquet(f)
        for w in ("W0", "W0M", "W1", "W2"):
            sw = sy.filter(pl.col("world") == w)
            r[f"band_{w}"] = {s: band(sw[pre + s].to_numpy()) for s in ("m_pi", "m2co", "slope", "beta", "theta")}
            if pre + "psi" in sw.columns:
                r[f"band_{w}"]["psi"] = band(sw[pre + "psi"].to_numpy())
        b0 = r["band_W0"]
        r["mpi_in_W0"] = bool(b0["m_pi"][0] <= r["m_pi"] <= b0["m_pi"][1])
        r["m2co_in_W0"] = bool(b0["m2co"][0] <= r["m2co"] <= b0["m2co"][1])
        r["mpi_centred"] = r["m_pi"] - b0["m_pi"][2]
        r["m2co_centred"] = r["m2co"] - b0["m2co"][2]
        w0 = sy.filter(pl.col("world") == "W0")
        r["p_W0_mpi"] = L.p_two(r["m_pi"], w0[pre + "m_pi"].to_numpy())
        r["p_W0_m2co"] = L.p_two(r["m2co"], w0[pre + "m2co"].to_numpy())
    # O4
    lnpi = {(int(a), p): float(np.log(max(x, math.exp(L.LNPI_FLOOR)))) for a, p, x in occ.select("agent", "project", "pi_i").iter_rows()}
    avd = {p: (a0, a1) for p, a0, a1 in av.filter(pl.col("project").is_in(list(pi))).select("project", "a0", "a1").iter_rows()}
    hh = h.filter(pl.col("src").is_in(list(pi)) & pl.col("dst").is_in(list(pi)))
    r4 = L.o4(hh, avd, lnpi, lr=True)
    if r4:
        r4["psi_ci"] = [r4["psi"] - 1.96 * r4["se_psi"], r4["psi"] + 1.96 * r4["se_psi"]]
        r4["rho_ci"] = [r4["rho"] - 1.96 * r4["se_rho"], r4["rho"] + 1.96 * r4["se_rho"]]
        # Amendment A1: calibrate the chi2 LR p against 100 W0 runs on the same skeleton
        fl = L.D / "synthetic" / f"lrnull_{u}_{ch}.parquet"
        if fl.exists() and np.isfinite(r4.get("lr_p", np.nan)):
            p0 = pl.read_parquet(fl)["lr_p"].drop_nulls().drop_nans().to_numpy()
            r4["lr_p_cal"] = float((1 + np.sum(p0 <= r4["lr_p"])) / (len(p0) + 1))
        else:
            r4["lr_p_cal"] = None
        r4["heatbath"] = bool(r4["psi_ci"][0] <= 1 <= r4["psi_ci"][1] and r4["rho_ci"][0] <= 0 <= r4["rho_ci"][1]
                              and (r4["lr_p_cal"] is None or r4["lr_p_cal"] >= 0.05))
    r["o4"] = r4
    return r


def o5(g, u, ch, h, occ):
    """Descriptive ownership check: per agent owning a project in the unit, observed ln(k_in / k_out) for hops into and
    out of the owned project vs the heat-bath stationary log-odds ln(pi_i(own) / (1 - pi_i(own)))."""
    own = occ.filter(pl.col("own"))
    out = []
    for a, p, pii in own.select("agent", "project", "pi_i").iter_rows():
        ha = h.filter(pl.col("agent") == a)
        nin, nout = ha.filter(pl.col("dst") == p).height, ha.filter(pl.col("src") == p).height
        To = float(occ.filter((pl.col("agent") == a) & (pl.col("project") == p))["T"].sum())
        Tother = float(occ.filter((pl.col("agent") == a) & (pl.col("project") != p))["T"].sum())
        if nin + nout == 0 or To <= 0 or Tother <= 0:
            continue
        obs = math.log((nin + .5) / Tother) - math.log((nout + .5) / To)
        pred = math.log(max(pii, 1e-6) / max(1 - pii, 1e-6))
        out.append((obs, pred, nin, nout))
    if not out:
        return None
    o = np.array(out)
    rho = float(stats.spearmanr(o[:, 0], o[:, 1]).statistic) if len(o) >= 4 else np.nan
    return {"unit": u, "channel": ch, "n_agents": len(o), "median_obs": float(np.median(o[:, 0])),
            "median_pred": float(np.median(o[:, 1])), "median_resid": float(np.median(o[:, 0] - o[:, 1])), "spearman": rho,
            "hops_in": int(o[:, 2].sum()), "hops_out": int(o[:, 3].sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimates", action="store_true")
    a = ap.parse_args()
    res = {"precondition": {}, "units": {}, "o5": [], "native": {}}
    for g in GOALS:
        for ch in ("work", "attention"):
            H, AV, OCC = unit_data(g, ch)
            for u in sorted(set(AV["unit"].to_list())):
                h, av, occ = H.filter(pl.col("unit") == u), AV.filter(pl.col("unit") == u), OCC.filter(pl.col("unit") == u)
                pc = {rule: precondition(h, av, rule) for rule in RULES}
                res["precondition"][f"{u}|{ch}"] = pc
                for rule in RULES:
                    if pc[rule]["testable"]:
                        rng = np.random.default_rng(zlib.crc32(f"{u}|{ch}|{rule}".encode()))
                        r = analyse(g, u, ch, rule, h, av, occ, rng)
                        r["own_role"] = g in OWN_ROLE
                        res["units"][f"{u}|{ch}|{rule}"] = r
                        print(f"{u}|{ch}|{rule} done", flush=True)
                x = o5(g, u, ch, h, occ)
                if x:
                    res["o5"].append(x)
    # random-effects means over testable unit-channels per rule
    res["pooled"] = {}
    for rule in RULES:
        rs = [r for r in res["units"].values() if r["rule"] == rule]
        if not rs:
            res["pooled"][rule] = {"k": 0}
            continue
        pool = {}
        for key, sek in (("m_pi", "m_pi_se"), ("m2co", "m2co_se"), ("mpi_centred", "m_pi_se"), ("m2co_centred", "m2co_se"),
                         ("beta", "beta_se"), ("theta", "theta_se")):
            est = [r["binom"][key] if key in ("beta", "theta") else r.get(key, np.nan) for r in rs]
            pool[key] = L.dersimonian_laird(est, [r[sek] for r in rs])
        o4s = [r["o4"] for r in rs if r["o4"]]
        pool["psi"] = L.dersimonian_laird([x["psi"] for x in o4s], [x["se_psi"] for x in o4s])
        pool["rho"] = L.dersimonian_laird([x["rho"] for x in o4s], [x["se_rho"] for x in o4s])
        res["pooled"][rule] = pool
    # native N3: G40 hub flux on days 1-2
    for ch in ("work", "attention"):
        H, AV, OCC = unit_data(40, ch)
        hub, t_split = S.g40_meta(ch)
        obs = S.hub_flux(H, hub, t_split)
        e = H.filter(pl.col("t") <= t_split)
        nin, nout = e.filter(pl.col("dst") == hub).height, e.filter(pl.col("src") == hub).height
        f = L.D / "synthetic" / f"40_{ch}.parquet"
        sy = pl.read_parquet(f).filter(pl.col("world") == "W0")["hub_flux_early"].to_numpy()
        b = band(sy)
        res["native"][f"N3|{ch}"] = {"m_hub": obs, "n_in": nin, "n_out": nout, "W0_band": b,
                                     "p_W0_upper": float((np.sum(sy[np.isfinite(sy)] >= obs) + 1) / (np.isfinite(sy).sum() + 1)),
                                     "beyond": bool(obs > b[1])}
    out = L.D / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(res, indent=1, default=lambda x: None if x is None or (isinstance(x, float) and not np.isfinite(x)) else float(x)))
    print(json.dumps(res["pooled"], indent=1, default=float)[:3000])
    if a.estimates:
        write_rows(res)


def write_rows(res):
    import estimates as E
    rows = []
    for key, r in res["units"].items():
        u, ch, rule = key.split("|")
        meth = f"H135 {rule} co-alive pairs (period_units unit); pair bootstrap 1000"
        nul = "W0 heat-bath band on the unit skeleton (200 runs)"
        base = {"period_unit": u, "goal_no": r["goal_no"], "channel": f"{ch}_hops", "role": "replication", "ci_kind": "percentile",
                "ci_level": 0.95, "n_kind": "co-alive hops", "post_hoc": False,
                "notes": "card variant rule (>= 80% of active seconds)" if rule == "coalive80" else "primary rule"}
        rows.append({**base, "statistic": "h135_net_maxent_flux", "estimate": r["m_pi"], "ci_lo": r["m_pi_ci"][0],
                     "ci_hi": r["m_pi_ci"][1], "n": r["n_co_hops"], "method": meth, "null": nul, "se": r["m_pi_se"]})
        rows.append({**base, "statistic": "h135_coalive_age_flux", "estimate": r["m2co"], "ci_lo": r["m2co_ci"][0],
                     "ci_hi": r["m2co_ci"][1], "n": r["n_co_hops"], "method": meth, "null": nul, "se": r["m2co_se"]})
        o1 = r["o1"]
        if np.isfinite(o1.get("slope", np.nan)):
            rows.append({**base, "statistic": "h135_rate_ratio_slope", "estimate": o1["slope"], "ci_lo": o1["slope_ci"][0],
                         "ci_hi": o1["slope_ci"][1], "n": o1["n_pairs"], "n_kind": "pairs (n >= 4)", "method": meth + "; Deming through origin",
                         "null": "slope 1 (detailed balance); O1 fails its synthetic pass rule (descriptive)"})
        if r["o4"]:
            rows.append({**base, "statistic": "h135_heatbath_psi", "estimate": r["o4"]["psi"], "ci_lo": r["o4"]["psi_ci"][0],
                         "ci_hi": r["o4"]["psi_ci"][1], "n": r["o4"]["n_choice"], "n_kind": "hops (choices)", "ci_kind": "se_z",
                         "se": r["o4"]["se_psi"], "method": "H135 conditional logit over available destinations (psi ln pi_i + rho held)",
                         "null": "psi = 1, rho = 0 (heat-bath)"})
    for key, r in res["native"].items():
        ch = key.split("|")[1]
        rows.append({"period_unit": "40", "goal_no": 40, "channel": f"{ch}_hops", "role": "native", "statistic": "h135_hub_flux_early",
                     "estimate": r["m_hub"], "ci_lo": r["W0_band"][0], "ci_hi": r["W0_band"][1], "ci_kind": "parametric", "ci_level": 0.95,
                     "n": r["n_in"] + r["n_out"], "n_kind": "hub hops (days 1-2)", "method": "H135 N3 net flux into the G40 hub on days 1-2",
                     "null": "W0 heat-bath band (CI columns hold the W0 2.5-97.5% band, not a CI of the estimate)", "post_hoc": False,
                     "notes": "in/out counts seen before the band (disclosed)"})
    E.write_estimates(rows, hypothesis="H135")
    print(f"wrote {len(rows)} estimates rows")


if __name__ == "__main__":
    main()
