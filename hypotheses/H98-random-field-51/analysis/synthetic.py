"""H98 synthetic validation at real counts (axis F), run before any real-data statistic.

Each world keeps a real unit's structure (agents, agent-days, half rows, 30-min windows, rooms, pairs, DQ6 rival pairs,
real whitened role vectors) and replaces the content vectors with a generative random-field model:
  static field  phi_i = m_u * u0 + Delta * (a_role * rhat_i + sqrt(1 - a_role^2) * e_i)      (rhat_i centered role dir)
  day field     g_d ~ N(0, s_g^2 / n);  drift z_id AR(1) over days (rho, s_z);  noise per state
  window        x_iw = (alpha * P_i + beta * I) eta_w + xi_iw  (+ pull J toward the room mean; + SR shared noise gamma)
  collective    c_d in {+1, -1} (Markov over days) * kappa * psi_i   (R2 world only)
Worlds: RF (H98: niche drive, no SR coupling); R3 (no niche filter, direct SR coupling); R2 (RF + collective switching);
UF (uniform field: small Delta, large m_u). Tests: R recovery, P(q) W_P size/power and BC false bimodality, niche beta_n
power and mediation-gap coverage/power, gain b recovery.

    uv run python hypotheses/H98-random-field-51/analysis/synthetic.py [--reps 20]
Output: data/processed/H98-random-field-51/synthetic/{results.parquet, summary.json}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import zlib  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h98lib as L  # noqa: E402

OUT = L.DATA / "synthetic"
n = 32
UNITS_PQ = ("51c", "51f", "51g")
UNITS_NICHE = ("51a", "51c", "51d", "51e", "51f", "51g", "51h")


def rnd_unit(rng, k=1):
    v = rng.standard_normal((k, n))
    return L.unit(v)


def roles_for(U, rv_all):
    ro = U.get("roles")
    out = {}
    if ro is None:
        return out
    for a, r in zip(ro["agent"].to_list(), ro["role"].to_list()):
        if (a, r) in rv_all:
            out[a] = rv_all[(a, r)]
    return out


def make_world(U: dict, rv_all: dict, world: str, rng, p: dict):
    """Return synthetic S (agent-day), H1, H2 (halves), X (windows) aligned with U's real rows."""
    ad, hv, wn = U["ad"], U["hv"], U["wn"]
    agents = sorted(set(ad["agent"].to_list()) | set(wn["agent"].to_list()))
    rv = roles_for(U, rv_all)
    rb = np.mean(list(rv.values()), 0) if rv else np.zeros(n)
    rhat = {a: L.unit(rv[a] - rb) if a in rv else rnd_unit(rng)[0] for a in agents}
    u0 = rnd_unit(rng)[0]
    phi = {}
    for a in agents:
        e = rnd_unit(rng)[0]
        phi[a] = p["m_u"] * u0 + p["Delta"] * (p["a_role"] * rhat[a] + np.sqrt(1 - p["a_role"] ** 2) * e)
    days = sorted(set(ad["day"].to_list()) | set(wn["day"].to_list()))
    D = max(days) + 1
    g = {d: rng.standard_normal(n) * p["s_g"] / np.sqrt(n) for d in range(D)}
    z = {}
    for a in agents:
        prev = rng.standard_normal(n) * p["s_z"] / np.sqrt(n)
        for d in range(D):
            prev = p["rho"] * prev + np.sqrt(1 - p["rho"] ** 2) * rng.standard_normal(n) * p["s_z"] / np.sqrt(n)
            z[(a, d)] = prev
    coll = np.zeros(D)
    psi = {a: rnd_unit(rng)[0] for a in agents}
    if world == "R2":
        c = 1.0
        for d in range(D):
            if rng.random() < 0.4:
                c = -c
            coll[d] = c

    def base(a, d):
        return phi[a] + g[d] + z[(a, d)] + coll[d] * p.get("kappa", 0.0) * psi[a]
    S = np.stack([base(a, d) + rng.standard_normal(n) * p["s_e"] / np.sqrt(n)
                  for a, d in zip(ad["agent"].to_list(), ad["day"].to_list())])
    H1 = np.stack([base(a, d) + rng.standard_normal(n) * p["s_h"] / np.sqrt(n)
                   for a, d in zip(hv["agent"].to_list(), hv["day"].to_list())])
    H2 = np.stack([base(a, d) + rng.standard_normal(n) * p["s_h"] / np.sqrt(n)
                   for a, d in zip(hv["agent"].to_list(), hv["day"].to_list())])
    # windows
    wa, wd, ww, wr = (wn[c].to_numpy() for c in ("agent", "day", "win30", "room"))
    X = np.zeros((len(wa), n))
    keys = {}
    for r, (d, w, ro) in enumerate(zip(wd, ww, wr)):
        keys.setdefault((d, w, ro), []).append(r)
    sr = []
    if world in ("R3", "RF+R3"):
        P = U["pairs"].filter(pl.col("cls") == "SR")
        sr = list(zip(P["i"].to_list(), P["j"].to_list()))
    for (d, w, ro), rows in keys.items():
        eta = rng.standard_normal(n) * p["s_eta"] / np.sqrt(n)
        xs = []
        for r in rows:
            a = wa[r]
            h = rhat[a]
            alpha = p["alpha"] if world in ("RF", "R2", "RF+R3") else 0.0
            xi = (alpha * h * (h @ eta) + p["beta"] * eta) + rng.standard_normal(n) * p["s_xi"] / np.sqrt(n)
            xs.append(xi)
        xs = np.asarray(xs)
        for (i, j) in sr:
            ii = [k for k, r in enumerate(rows) if wa[r] == i]
            jj = [k for k, r in enumerate(rows) if wa[r] == j]
            if ii and jj:
                zz = rng.standard_normal(n) * p["gamma"] / np.sqrt(n)
                xs[ii[0]] += zz
                xs[jj[0]] += zz
        if p.get("J", 0) > 0 and len(rows) > 1:
            x = xs.copy()
            for _ in range(30):
                tot = x.sum(0)
                x = xs + p["J"] * (tot[None, :] - x) / (len(rows) - 1)
            xs = x
        for k, r in enumerate(rows):
            X[r] = base(wa[r], d) + xs[k]
    return L.unit(S).astype(np.float32), L.unit(H1).astype(np.float32), L.unit(H2).astype(np.float32), L.unit(X).astype(np.float32)


BASE = dict(m_u=0.3, Delta=0.6, a_role=0.5, s_g=0.25, s_z=0.35, rho=0.6, s_e=0.3, s_h=0.8, s_eta=0.6,
            alpha=1.6, beta=0.25, s_xi=1.0, gamma=0.0, J=0.0, kappa=0.0)


def job(args):
    world, u, rep, p = args
    rng = np.random.default_rng(zlib.crc32(f"{world}|{u}|{rep}".encode()))
    U = L.load_unit(u)
    rv_all = L.role_table()
    S, H1, H2, X = make_world(U, rv_all, world, rng, p)
    ad, hv, wn = U["ad"], U["hv"], U["wn"]
    res = {"world": world, "unit": u, "rep": rep, **{k: p[k] for k in ("Delta", "m_u", "alpha", "gamma", "kappa", "J")}}
    # R
    dz = L.disorder(S, ad["agent"].to_numpy(), ad["day"].to_numpy(), c_ref=np.zeros(n))
    res["R_hat"] = dz["R"]
    res["R_true"] = p["Delta"] ** 2 / (p["Delta"] ** 2 + p["m_u"] ** 2)
    D = int(ad["day"].max()) + 1
    if u in UNITS_PQ and D >= 4:
        H1d, H2d = L.delta_halves(H1, H2, S, hv["agent"].to_numpy(), hv["day"].to_numpy(), ad["agent"].to_numpy(), ad["day"].to_numpy())
        t = L.pq_test(H1d, H2d, hv["agent"].to_numpy(), hv["day"].to_numpy(), D, n_shift=300, seed=rep)
        res.update({"W_P": t["W_P"], "p_WP": t["p_WP"], "W": t["W"], "p_W": t["p_W"], "bc": t["bc"],
                    "WP_hi": t["W_P_band"][1], "qbar": t["qbar"], "qbar_lo": t["qbar_band"][0], "qbar_hi": t["qbar_band"][1]})
    if u in UNITS_NICHE:
        wa, wd, ww = wn["agent"].to_numpy(), wn["day"].to_numpy(), wn["win30"].to_numpy()
        ms = 10 if D >= 4 else 5
        J = L.comovement(X, wa, wd, ww, min_shared=ms)
        P = U["pairs"].join(J, on=["i", "j"], how="inner")
        rv = roles_for(U, rv_all)
        P = L.niche_overlap(P, rv)
        f = L.jackknife(P, lambda Q: L.niche_fit(Q), ["beta_n", "G", "T_SR", "That_SR"])
        res.update({k: f.get(k, np.nan) for k in ("beta_n", "beta_n_se", "G", "G_se", "T_SR", "T_SR_se", "That_SR", "n_SR")})
        res["Jbar"] = float(P["J"].mean())
    if u in ("51c", "51g") and world in ("RF", "PULL"):
        gg = L.gain(X, wn["agent"].to_numpy(), wn["day"].to_numpy(), wn["win30"].to_numpy(), wn["room"].to_numpy(), B=0)
        res.update({"b": gg["b"], "b_ex": gg["b_ex"]})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--niche-only", action="store_true", help="Amendment A1 re-check: niche worlds only, alpha 2.7")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.niche_only:
        return niche_only(a)
    jobs = []
    worlds = {
        "RF": dict(BASE),
        "R3": dict(BASE, alpha=0.0, beta=0.45, gamma=0.3),
        "R2": dict(BASE, kappa=0.45),
        "UF": dict(BASE, Delta=0.25, m_u=0.6),
        "NULLN": dict(BASE, alpha=0.0, beta=0.45),           # no niche, no SR coupling: size of beta_n and G
        "PULL": dict(BASE, J=0.3, beta=0.0, alpha=0.0),       # mean-field pull only: b recovery
    }
    for w, p in worlds.items():
        units = sorted(set(UNITS_PQ) | set(UNITS_NICHE)) if w in ("RF", "R3", "R2", "NULLN") else ["51c", "51g", "40"]
        for u in units:
            for r in range(a.reps):
                jobs.append((w, u, r, p))
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(job, jobs, chunksize=4))
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(OUT / "results.parquet")
    summ = summarize(df)
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float))
    print(f"{len(jobs)} jobs in {time.time() - t0:.0f} s")


def niche_job(args):
    world, u, rep, p = args
    rng = np.random.default_rng(zlib.crc32(f"A1|{world}|{u}|{rep}".encode()))
    U = L.load_unit(u)
    rv_all = L.role_table()
    S, H1, H2, X = make_world(U, rv_all, world, rng, p)
    wn = U["wn"]
    D = int(U["ad"]["day"].max()) + 1
    J = L.comovement(X, wn["agent"].to_numpy(), wn["day"].to_numpy(), wn["win30"].to_numpy(), min_shared=10 if D >= 4 else 5)
    P = L.niche_overlap(U["pairs"].join(J, on=["i", "j"], how="inner"), roles_for(U, rv_all))
    res = {"world": world, "unit": u, "rep": rep}
    for reg in ("niche2", "niche"):
        f = L.jackknife(P, lambda Q, r=reg: L.niche_fit(Q, reg=r), ["beta_n", "G", "T_SR"])
        for k in ("beta_n", "beta_n_se", "G", "G_se", "T_SR", "T_SR_se"):
            res[f"{k}_{reg}"] = f.get(k, np.nan)
    if rep < 5 and world in ("RF", "NULLN"):
        res["perm_p_niche2"] = L.niche_perm(P, roles_for(U, rv_all), n_perm=200, seed=rep)
    return res


def niche_only(a):
    worlds = {"RF": dict(BASE, alpha=2.7), "R3": dict(BASE, alpha=0.0, beta=0.45, gamma=0.3),
              "NULLN": dict(BASE, alpha=0.0, beta=0.45), "RF+R3": dict(BASE, alpha=2.7, gamma=0.3)}
    jobs = [(w, u, r, p) for w, p in worlds.items() for u in UNITS_NICHE for r in range(a.reps)]
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(niche_job, jobs, chunksize=4))
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(OUT / "niche_A1.parquet")
    rows = []
    for (w, r), g in df.group_by(["world", "rep"]):
        row = {"world": w, "rep": r}
        for reg in ("niche2", "niche"):
            pb = L.re_pool(g[f"beta_n_{reg}"].to_numpy(), g[f"beta_n_se_{reg}"].to_numpy())
            pg = L.re_pool(g[f"G_{reg}"].to_numpy(), g[f"G_se_{reg}"].to_numpy())
            pt = L.re_pool(g[f"T_SR_{reg}"].to_numpy(), g[f"T_SR_se_{reg}"].to_numpy())
            row.update({f"beta_lo_{reg}": pb["lo"], f"beta_{reg}": pb["est"], f"G_lo_{reg}": pg["lo"], f"G_hi_{reg}": pg["hi"],
                        f"G_{reg}": pg["est"], f"T_{reg}": pt["est"], f"T_lo_{reg}": pt["lo"]})
        rows.append(row)
    pp = pl.DataFrame(rows)
    summ = {}
    for reg in ("niche2", "niche"):
        summ[reg] = pp.group_by("world").agg(
            (pl.col(f"beta_lo_{reg}") > 0).mean().alias("rate_beta_pos"),
            ((pl.col(f"G_lo_{reg}") <= 0) & (pl.col(f"G_hi_{reg}") >= 0)).mean().alias("rate_G_includes_0"),
            (pl.col(f"G_lo_{reg}") > 0).mean().alias("rate_G_pos"), (pl.col(f"T_lo_{reg}") > 0).mean().alias("rate_T_pos"),
            pl.col(f"beta_{reg}").median().alias("beta_med"), pl.col(f"G_{reg}").median().alias("G_med"),
            pl.col(f"T_{reg}").median().alias("T_med")).sort("world").to_dicts()
    if "perm_p_niche2" in df.columns:
        summ["perm_unit_rate_p05"] = df.filter(pl.col("perm_p_niche2").is_not_null()).group_by("world").agg(
            (pl.col("perm_p_niche2") < 0.05).mean().alias("rate"), pl.len()).to_dicts()
    (OUT / "niche_A1.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float))
    print(f"{len(jobs)} jobs in {time.time() - t0:.0f} s")


def summarize(df: pl.DataFrame) -> dict:
    s = {}
    # R recovery
    s["R"] = df.group_by("world", "unit").agg(pl.col("R_true").first(), pl.col("R_hat").mean().alias("R_hat_mean"),
                                              pl.col("R_hat").std().alias("R_hat_sd")).sort("world", "unit").to_dicts()
    # P(q)
    if "W_P" in df.columns:
        q = df.filter(pl.col("W_P").is_not_null())
        s["pq"] = q.group_by("world", "unit").agg(
            (pl.col("W_P") > pl.col("WP_hi")).mean().alias("rate_WP_above_band"),
            (pl.col("p_WP") < 0.05).mean().alias("rate_pWP_05"), (pl.col("p_W") < 0.05).mean().alias("rate_pW_05"),
            (pl.col("bc") > 0.555).mean().alias("rate_BC_bimodal"),
            ((pl.col("qbar") < pl.col("qbar_lo")) | (pl.col("qbar") > pl.col("qbar_hi"))).mean().alias("rate_qbar_out"),
            pl.col("W_P").median().alias("W_P_med")).sort("world", "unit").to_dicts()
    # niche pooled per replicate across units
    if "beta_n" in df.columns:
        nn = df.filter(pl.col("beta_n").is_not_null())
        pooled = []
        for (w, r), g in nn.group_by(["world", "rep"]):
            pb = L.re_pool(g["beta_n"].to_numpy(), g["beta_n_se"].to_numpy())
            pg = L.re_pool(g["G"].to_numpy(), g["G_se"].to_numpy())
            pt = L.re_pool(g["T_SR"].to_numpy(), g["T_SR_se"].to_numpy())
            pooled.append({"world": w, "rep": r, "beta": pb["est"], "beta_lo": pb["lo"], "G": pg["est"], "G_lo": pg["lo"],
                           "G_hi": pg["hi"], "T": pt["est"], "T_lo": pt["lo"]})
        pp = pl.DataFrame(pooled)
        s["niche"] = pp.group_by("world").agg(
            (pl.col("beta_lo") > 0).mean().alias("rate_beta_pos"),
            ((pl.col("G_lo") <= 0) & (pl.col("G_hi") >= 0)).mean().alias("rate_G_includes_0"),
            (pl.col("G_lo") > 0).mean().alias("rate_G_pos"), (pl.col("T_lo") > 0).mean().alias("rate_T_pos"),
            pl.col("beta").median(), pl.col("G").median(), pl.col("T").median()).sort("world").to_dicts()
        s["niche_unit"] = nn.group_by("world").agg(pl.col("Jbar").median(), pl.col("T_SR").median(),
                                                   pl.col("n_SR").median()).to_dicts()
    if "b_ex" in df.columns:
        s["gain"] = df.filter(pl.col("b_ex").is_not_null()).group_by("world", "unit").agg(
            pl.col("J").first(), pl.col("b").mean(), pl.col("b_ex").mean(), pl.col("b_ex").std().alias("b_ex_sd")).to_dicts()
    return s


if __name__ == "__main__":
    main()
