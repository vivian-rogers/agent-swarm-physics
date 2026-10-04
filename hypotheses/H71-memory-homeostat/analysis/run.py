"""H71 round 1: replication on every eligible period, cross-period tests, natives (exploratory, non-holdout only).

Writes data/processed/H71-memory-homeostat/results/{periods.json, cross.json, natives.json}.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h71lib as L  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H71-memory-homeostat"
RES = DATA / "results"
RNG = np.random.default_rng(71)


def ci_boot(p, fn, B=200):
    est, lo, hi = L.boot_agents(p, fn, B=B, rng=RNG)
    return {"est": est, "lo": lo, "hi": hi}


def fitted_noise(p: pl.DataFrame) -> dict:
    """Growth mean and residual SDs of the two phases (for the period's mixed-series synthetic, P3)."""
    q = p.with_columns((pl.col("y1") - pl.col("x0")).alias("grow"))
    dec = L.decomposition(p)
    m = q.group_by("agent").agg(pl.col("grow").mean().alias("mg"), pl.col("x0").mean().alias("m0"),
                                pl.col("x1").mean().alias("m1"), pl.col("y1").mean().alias("my"))
    q = q.join(m, on="agent")
    rg = (q["grow"] - q["mg"]).to_numpy() - dec["c"] * (q["x0"] - q["m0"]).to_numpy()
    rc = (q["x1"] - q["m1"]).to_numpy() - dec["b"] * (q["y1"] - q["my"]).to_numpy()
    return {"d": float(q["grow"].mean()), "s_grow": float(np.std(rg)), "s_comp": float(np.std(rc)),
            "b": dec["b"], "c": dec["c"]}


def synth_mixed(cyc_p: pl.DataFrame, phi: float, nz: dict, reps: int = 10) -> dict:
    skel = cyc_p.select("agent", "period", "regime", "t", "n_app", "ctype", "dt_s")
    vals = []
    for k in range(reps):
        c = nz["c"] if np.isfinite(nz["c"]) and abs(nz["c"]) < 0.95 else 0.0
        cs, ss = L.simulate_cycles(skel, phi, c, s_grow=max(nz["s_grow"], 0.01), s_comp=max(nz["s_comp"], 0.01),
                                   rng=np.random.default_rng(500 + k))
        vals.append(L.mixed_phi(ss))
    return {"mean": float(np.mean(vals)), "sd": float(np.std(vals))}


def one_period(per: str, cyc: pl.DataFrame, snaps: pl.DataFrame) -> dict:
    cp = cyc.filter(pl.col("period") == per)
    p = L.pairs(cp)
    keep = p.group_by("agent").len().filter(pl.col("len") >= L.MIN_PAIRS_AGENT)["agent"]
    pk = p.filter(pl.col("agent").is_in(keep.implode()))
    ba = L.boot_all(pk, B=1000, rng=RNG)
    est, lo, hi = ba["phi_hpj"]["est"], ba["phi_hpj"]["lo"], ba["phi_hpj"]["hi"]
    out = {"period": per, "regime": cp["regime"][0], "n_agents": int(keep.len()), "n_pairs": pk.height,
           "phi": {"est": est, "lo": lo, "hi": hi, "raw": L.phi_pooled(pk)}}
    o = L.oos(cp.filter(pl.col("agent").is_in(keep.implode())))
    out["oos"] = {"n_agents": o.height,
                  "ar1_beats_rw": float((o["mse_ar1"] < o["mse_rw"]).mean()) if o.height else None,
                  "ar1_beats_db": float((o["mse_ar1"] < o["mse_db"]).mean()) if o.height else None,
                  "ar2_beats_ar1": float((o["mse_ar2"] < o["mse_ar1"]).mean()) if o.height else None,
                  "mse_ratio_ar1_rw_median": float((o["mse_ar1"] / o["mse_rw"]).median()) if o.height else None}
    out["ar2"] = ba["ar2"]
    out["mixed_phi"] = L.mixed_phi(snaps.filter(pl.col("agent").is_in(keep.implode())), per)
    out["dec"] = L.decomposition(pk)
    out["dec_b_ci"] = ba["b"]
    out["dec_c_ci"] = ba["c"]
    out["clock"] = L.clock_slope(pk)
    out["clock_ci"] = ba["clock_slope"]
    if out["regime"] == "III":
        out["by_type"] = L.phi_by_type(pk)
        out["forced"] = ba["phi_forced"]
        out["voluntary"] = ba["phi_vol"]
        out["f_minus_v"] = ba["f_minus_v"]
    nz = fitted_noise(pk)
    out["noise"] = nz
    out["synth_mixed"] = synth_mixed(cp.filter(pl.col("agent").is_in(keep.implode())), est, nz,
                                     reps=4 if cp.height > 5000 else 10)
    pa = L.per_agent(pk)
    out["agents"] = pa.to_dicts()
    if pa.height >= 3:
        m, s, tau = L.dl_tau(pa["phi"].to_numpy(), pa["se"].to_numpy())
        out["agent_re"] = {"mean": m, "se": s, "tau": tau}
    out["mu_median_chars"] = float(np.exp(pa["mu"].median())) if pa.height else None
    # verdict (card rule)
    ok_phi = (lo > 0) and (hi < 1) and (0 < est < 0.9)
    share = out["oos"]["ar1_beats_rw"]
    if out["n_agents"] < 3:
        v = "descriptive"
    elif (hi >= 1) or (hi < 0) or (share is not None and share < 0.4):
        v = "failed"
    elif ok_phi and share is not None and share >= 0.6:
        v = "supported"
    else:
        v = "mixed"
    out["verdict"] = v
    return out


def paired_change(cyc: pl.DataFrame, before: list[str], after: list[str], min_pairs: int = 10) -> dict:
    """Per agent: phi+ and mu on each side (pairs within periods, pooled over the side's periods); paired means."""
    rows = []
    for side, pers in (("before", before), ("after", after)):
        p = L.pairs(cyc.filter(pl.col("period").is_in(pers)))
        # demean within agent x period, then pool over the side
        for a, g in p.group_by("agent"):
            if g.height < min_pairs:
                continue
            q = g.with_columns(pl.concat_list("x0", "x1").list.mean().alias("_"))
            mu = (pl.concat([g.select("period", pl.col("x0").alias("x")), g.select("period", pl.col("x1").alias("x"))])
                  .group_by("period").agg(pl.col("x").mean().alias("mu")))
            q = g.join(mu, on="period")
            d0 = (q["x0"] - q["mu"]).to_numpy()
            d1 = (q["x1"] - q["mu"]).to_numpy()
            rows.append({"agent": int(a[0]), "side": side, "phi": float(np.sum(d0 * d1) / np.sum(d0 * d0)),
                         "mu": float(q["mu"].mean()), "T": g.height,
                         "frac_removed": float((g["x0"] - g["x1"]).mean())})
    df = pl.DataFrame(rows)
    if df.height == 0:
        return {"n_agents": 0}
    w = df.pivot(on="side", index="agent", values=["phi", "mu", "T"]).drop_nulls()
    if w.height < 2:
        return {"n_agents": int(w.height)}
    dphi = (w["phi_after"] - w["phi_before"]).to_numpy()
    dmu = (w["mu_after"] - w["mu_before"]).to_numpy()
    bs = RNG.integers(0, len(dphi), size=(2000, len(dphi)))
    cp = np.percentile(dphi[bs].mean(1), [2.5, 97.5])
    cm = np.percentile(dmu[bs].mean(1), [2.5, 97.5])
    return {"n_agents": int(w.height), "dphi": float(dphi.mean()), "dphi_ci": [float(cp[0]), float(cp[1])],
            "dln_mu": float(dmu.mean()), "dln_mu_ci": [float(cm[0]), float(cm[1])],
            "phi_before_mean": float(w["phi_before"].mean()), "phi_after_mean": float(w["phi_after"].mean()),
            "agents": w.to_dicts()}


def removal_share(cyc: pl.DataFrame, pers: list[str]) -> dict:
    c = cyc.filter(pl.col("period").is_in(pers))
    fr = (c["lines_removed"] / (c["lines_removed"] + c["lines_kept"]).clip(lower_bound=1)).to_numpy()
    return {"mean": float(np.mean(fr)), "n": int(len(fr))}


def newcomers(cyc: pl.DataFrame, snaps: pl.DataFrame) -> dict:
    """Onsager regression: agents whose first-ever memory snapshot is in the non-holdout data, >= 40 cycles."""
    ros = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet", columns=["agent", "name", "joined"])
    first = snaps.group_by("agent").agg(pl.col("t").min().alias("t0"), pl.col("pt_date").min().alias("d0"))
    first = first.join(ros, on="agent")
    # a join is observed when the agent's first snapshot falls within 3 days of its roster join date
    first = first.filter(pl.col("joined").is_not_null())
    out = []
    for r in first.to_dicts():
        if r["joined"] is None or r["d0"] is None:
            continue
        dj = (np.datetime64(r["d0"]) - np.datetime64(r["joined"][:10])).astype(int)
        if not (0 <= dj <= 3):
            continue
        c = cyc.filter(pl.col("agent") == r["agent"]).sort("t")
        if c.height < 40:
            continue
        x = c["xplus"].to_numpy()
        late = x[20:]
        mu = late.mean()
        dl = late - mu
        phi_i = float(np.sum(dl[1:] * dl[:-1]) / np.sum(dl[:-1] ** 2))
        d = x[:20] - mu
        # least-squares relaxation factor on d_n = d_0 * phi^n (n = 0..19)
        grid = np.linspace(-0.5, 0.999, 300)
        sse = [np.sum((d - d[0] * g ** np.arange(len(d))) ** 2) for g in grid]
        phi_r = float(grid[int(np.argmin(sse))])
        half = next((n for n in range(1, len(d)) if abs(d[n]) < 0.5 * abs(d[0])), None)
        out.append({"agent": int(r["agent"]), "joined": r["joined"][:10], "period": c["period"][0],
                    "n_cycles": c.height, "d0": float(d[0]), "phi_i": phi_i, "phi_relax": phi_r,
                    "within_02": bool(abs(phi_r - phi_i) <= 0.2), "half_cycles": half,
                    "first_xplus_chars": float(np.exp(x[0])), "mu_chars": float(np.exp(mu))})
    n = len(out)
    return {"n": n, "share_within_02": float(np.mean([o["within_02"] for o in out])) if n else None,
            "share_half_le3": float(np.mean([(o["half_cycles"] is not None and o["half_cycles"] <= 3) for o in out]))
            if n else None, "rows": out}


def cross(per_res: dict, cyc: pl.DataFrame) -> dict:
    """Agent invariance of phi_i across periods; lab share of set point; DL pools by regime."""
    rows = []
    for per, r in per_res.items():
        for a in r.get("agents", []):
            rows.append({"period": per, "regime": r["regime"], **a})
    df = pl.DataFrame(rows)
    ros = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet", columns=["agent", "lab"])
    df = df.join(ros, on="agent", how="left")
    # invariance: for agents in >= 2 periods, correlate phi_i in a period with the agent's mean over other periods
    xs, ys = [], []
    for a, g in df.group_by("agent"):
        if g.height < 2:
            continue
        ph = g["phi"].to_numpy()
        for i in range(len(ph)):
            xs.append(ph[i])
            ys.append(np.delete(ph, i).mean())
    inv = float(np.corrcoef(xs, ys)[0, 1]) if len(xs) > 5 else None
    # permutation null for the invariance correlation (shuffle agent labels within period)
    null = []
    for _ in range(500):
        sh = df.with_columns(pl.col("agent").shuffle(seed=int(RNG.integers(1e9))).over("period"))
        xx, yy = [], []
        for a, g in sh.group_by("agent"):
            if g.height < 2:
                continue
            ph = g["phi"].to_numpy()
            for i in range(len(ph)):
                xx.append(ph[i])
                yy.append(np.delete(ph, i).mean())
        null.append(np.corrcoef(xx, yy)[0, 1])
    # set point: agent vs lab vs period shares of var(mu) (eta^2)
    tot = float(df["mu"].var())
    def eta(col):
        m = df.group_by(col).agg(pl.col("mu").mean().alias("m"), pl.len().alias("n"))
        g = df["mu"].mean()
        return float((m["n"] * (m["m"] - g) ** 2).sum() / ((df.height - 1) * tot))
    pools = {}
    for reg in ("I", "II", "III", "all"):
        sel = [r for r in per_res.values() if (reg == "all" or r["regime"] == reg) and np.isfinite(r["phi"]["lo"])]
        if not sel:
            continue
        est = np.array([r["phi"]["est"] for r in sel])
        se = np.array([(r["phi"]["hi"] - r["phi"]["lo"]) / 3.92 for r in sel])
        m, s, tau = L.dl_tau(est, se)
        pools[reg] = {"phi": m, "lo": m - 1.96 * s, "hi": m + 1.96 * s, "tau": tau, "k": len(sel)}
    return {"invariance_r": inv, "invariance_null_p95": float(np.nanpercentile(null, 95)),
            "invariance_null_mean": float(np.nanmean(null)), "n_agent_periods": df.height,
            "eta2_agent": eta("agent"), "eta2_lab": eta("lab"), "eta2_period": eta("period"), "pools": pools,
            "n_agents_multi": int(df.group_by("agent").len().filter(pl.col("len") >= 2).height)}


def main():
    cyc = pl.read_parquet(DATA / "cycles.parquet")
    snaps = pl.read_parquet(DATA / "snapshots.parquet")
    RES.mkdir(parents=True, exist_ok=True)
    pers = sorted(p for p in (ROOT / "hypotheses/H71-memory-homeostat/goalperiod-subhypotheses").iterdir()
                  if p.name.startswith("G"))
    per_res = {}
    for d in pers:
        r = one_period(d.name, cyc, snaps)
        per_res[d.name] = r
        print(d.name, r["verdict"], f"phi {r['phi']['est']:+.3f} [{r['phi']['lo']:+.3f}, {r['phi']['hi']:+.3f}] "
              f"oos {r['oos']['ar1_beats_rw']} mixed {r['mixed_phi']:+.3f} synth {r['synth_mixed']['mean']:+.3f} "
              f"ar2 {r['ar2']['est']:+.3f} clock {r['clock']['slope']:+.3f} b {r['dec']['b']:.2f} c {r['dec']['c']:+.2f}"
              + (f" F {r['by_type'].get('forced', np.nan):+.3f} V {r['by_type'].get('voluntary', np.nan):+.3f}"
                 if r['regime'] == 'III' else ''), flush=True)
    (RES / "periods.json").write_text(json.dumps(per_res, indent=1, default=float))
    cr = cross(per_res, cyc)
    (RES / "cross.json").write_text(json.dumps(cr, indent=1, default=float))
    print("cross", {k: v for k, v in cr.items() if k != "pools"}, cr["pools"])
    nat = {
        "NE14": {"wide": paired_change(cyc, ["G33", "G35", "G36a"], ["G36b", "G36c", "G37", "G38", "G39"]),
                 "within36": paired_change(cyc, ["G36a"], ["G36b", "G36c"], min_pairs=8)},
        "NE04": {"paired": paired_change(cyc, ["G11", "G12a"], ["G12b", "G13"]),
                 "removal_before": removal_share(cyc, ["G11", "G12a"]),
                 "removal_after": removal_share(cyc, ["G12b", "G13"])},
        "NE16": {"paired": paired_change(cyc, ["G36b"], ["G36c"], min_pairs=8),
                 "append_share_before": float((cyc.filter(pl.col("period") == "G36b")["n_app"] > 0).mean()),
                 "append_share_after": float((cyc.filter(pl.col("period") == "G36c")["n_app"] > 0).mean())},
        "NE32": newcomers(cyc, snaps),
    }
    # bootstrap CI for the NE04 removal-share change (agents resampled)
    (RES / "natives.json").write_text(json.dumps(nat, indent=1, default=float))
    for k, v in nat.items():
        print(k, {kk: (vv if not isinstance(vv, dict) else {a: b for a, b in vv.items() if a != "agents"})
                  for kk, vv in v.items() if kk != "rows"})


if __name__ == "__main__":
    main()
