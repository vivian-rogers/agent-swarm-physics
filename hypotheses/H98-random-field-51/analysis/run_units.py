"""H98 replication run on the non-holdout units (shared period_units): O1 disorder ratio R (leave-own-period-out
reference, Amendment A0), O1 role share, O2 mean-field gain b, O3 P(q) with the per-agent circular day-shift null,
O4 niche regression and mediation gap, O5 stance niche slope. Primary variant: style_resid_period x bge_small; variants:
white32, gte_modernbert.

    uv run python hypotheses/H98-random-field-51/analysis/run_units.py [--fast]
Output: data/processed/H98-random-field-51/results/{units.parquet, niche_pairs.parquet, pooled.json, pq_<unit>.npy}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h98lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
RES = L.DATA / "results"
PRIMARY = ("style_resid_period", "bge_small")
REPL = ("51c", "51d", "51f", "51g", "51h", "38a", "39", "40", "41")
COUNTED51 = ("51c", "51d", "51f", "51g", "51h")
NICHE = ("51a", "51c", "51d", "51e", "51f", "51g", "51h")
REF_GOALS = (36, 37, 38, 39, 40, 41, 42, 44, 51)


def period_refs(var: str, model: str) -> dict:
    """Equal-weight leave-own-period-out reference: mean over the other regime-III periods' agent-day means."""
    ad = pl.read_parquet(SH / "embeddings/agent_day.parquet").with_row_index("row")
    A = np.load(SH / f"embeddings/agent_day_{var}_{model}.npy", mmap_mode="r")
    ad = ad.filter(pl.col("goal_no").is_in(list(REF_GOALS)) & ~pl.col("holdout") & (pl.col("regime") == "III")
                   & ((pl.col("n_chat") + pl.col("n_intent")) >= 3))
    assert not any(holdout_mask(ad["pt_date"].to_list(), ad["goal_no"].to_list()))
    means = {}
    for g in REF_GOALS:
        rows = ad.filter(pl.col("goal_no") == g)["row"].to_numpy()
        if len(rows):
            means[g] = L.unit(np.asarray(A[rows], np.float32)).mean(0)
    return {g: np.mean([means[h] for h in means if h != g], 0) for g in means}


def run_unit(args):
    u, var, model, primary, fast = args
    U = L.load_unit(u, var, model)
    ad, hv, wn = U["ad"], U["hv"], U["wn"]
    goal = 51 if u.startswith("51") else int(u.rstrip("abcdefgh"))
    refs = period_refs(var, model)
    res = {"unit": u, "goal_no": goal, "var": var, "model": model, "n_days": int(ad["day"].n_unique()),
           "n_agents": int(ad["agent"].n_unique())}
    a, d = ad["agent"].to_numpy(), ad["day"].to_numpy()
    dz = L.disorder(U["S"], a, d, c_ref=refs.get(goal))
    dz0 = L.disorder(U["S"], a, d, c_ref=None)
    res.update({"R": dz["R"], "D2": dz["D2"], "M2": dz["M2"], "R_raw": dz0["R"], "M2_raw": dz0["M2"], "N_R": dz["N"]})
    if primary and not fast:
        res["R_lo"], res["R_hi"] = L.disorder_boot(U["S"], a, d, c_ref=refs.get(goal), B=500, seed=1)
    # role share
    rv_all = L.role_table(model)
    rv = {}
    if "roles" in U:
        for ag, ro in zip(U["roles"]["agent"].to_list(), U["roles"]["role"].to_list()):
            if (ag, ro) in rv_all:
                rv[ag] = rv_all[(ag, ro)]
    if rv and dz.get("phi") is not None:
        keep = [k for k, ag in enumerate(dz["agents"]) if ag in rv]
        if len(keep) >= 6:
            rs = L.role_share(dz["phi"][keep], np.stack([rv[dz["agents"][k]] for k in keep]),
                              n_perm=2000 if primary else 500, seed=2)
            res.update({"R2_role": rs["R2_role"], "R2_role_p": rs["p"], "R2_role_null": rs["null_mean"], "role_gain": rs["a"]})
    # gain
    if res["n_days"] >= 2:
        gg = L.gain(U["X"], wn["agent"].to_numpy(), wn["day"].to_numpy(), wn["win30"].to_numpy(), wn["room"].to_numpy(),
                    B=(200 if primary and not fast else 0), seed=3)
        res.update({"b": gg["b"], "b_surr": gg["b_surr"], "b_ex": gg["b_ex"], "b_lo": gg["ci"][0], "b_hi": gg["ci"][1],
                    "n_windows": gg.get("n_windows")})
    # P(q)
    D = int(ad["day"].max()) + 1
    if res["n_days"] >= 4:
        H1d, H2d = L.delta_halves(U["H1"], U["H2"], U["S"], hv["agent"].to_numpy(), hv["day"].to_numpy(), a, d)
        t = L.pq_test(H1d, H2d, hv["agent"].to_numpy(), hv["day"].to_numpy(), D,
                      n_shift=(2000 if primary else 500) if not fast else 200, seed=4)
        res.update({k: t[k] for k in ("qbar", "sd", "bc", "skew", "W_P", "p_WP", "W", "p_W", "qself", "qinf", "M", "n_pairs")})
        res["WP_lo"], res["WP_hi"] = t["W_P_band"]
        res["qbar_lo"], res["qbar_hi"] = t["qbar_band"]
        if primary:
            RES.mkdir(parents=True, exist_ok=True)
            np.save(RES / f"pq_{u}.npy", t["q"])
    # niche
    pairs_out = None
    if u in NICHE and rv:
        ms = 10 if res["n_days"] >= 4 else 5
        J = L.comovement(U["X"], wn["agent"].to_numpy(), wn["day"].to_numpy(), wn["win30"].to_numpy(), min_shared=ms)
        P = U["pairs"].join(J, on=["i", "j"], how="inner")
        P = L.niche_overlap(P, rv)
        res["Jbar"] = float(P["J"].mean())
        res["n_pairs_J"] = P.height
        for tag, covs in (("", ("same_lab", "log_reads")), ("_A", ("same_lab",)), ("_B", ("same_lab", "log_reads", "log_replies"))):
            f = L.jackknife(P, lambda Q, c=covs: L.niche_fit(Q, c), ["beta_n", "G", "T_SR", "That_SR"])
            for k in ("beta_n", "beta_n_se", "G", "G_se", "T_SR", "T_SR_se", "That_SR", "That_SR_se", "n_SR", "n_U",
                      "beta_log_reads", "beta_log_replies", "beta_same_lab"):
                if k in f:
                    res[f"{k}{tag}"] = f[k]
        fl = L.jackknife(P, lambda Q: L.niche_fit(Q, ("same_lab", "log_reads"), "niche"), ["beta_n", "G"])
        res.update({"beta_n_lin": fl.get("beta_n"), "beta_n_lin_se": fl.get("beta_n_se"), "G_lin": fl.get("G"),
                    "G_lin_se": fl.get("G_se")})
        if primary or not fast:
            res["beta_n_p"] = L.niche_perm(P, rv, n_perm=(1000 if primary else 200), seed=5)
        res["T_SR_raw"] = L.sr_adjusted(P, ("same_lab",))
        res["T_SR_adj"] = L.sr_adjusted(P, ("same_lab", "log_reads", "log_replies"))
        # stance
        Ps = P.filter(pl.col("stance").is_not_null())
        res["n_stance_pairs"] = Ps.height
        if Ps.height >= 20:
            res["Js_mean"] = float(Ps["stance"].mean())
            Us = Ps.filter(pl.col("cls").is_null() & pl.col("niche").is_not_null())

            def sfit(Q):
                if Q.height < 10:
                    return {}
                X = np.column_stack([np.ones(Q.height), Q["niche"].to_numpy(), Q["same_lab"].cast(pl.Float64).to_numpy()])
                return {"beta_s": float(L.ols(Q["stance"].to_numpy(), X)[1])}
            fs = L.jackknife(Us, sfit, ["beta_s"])
            res["beta_s"], res["beta_s_se"] = fs.get("beta_s", np.nan), fs.get("beta_s_se", np.nan)
        if primary:
            pairs_out = P.with_columns(pl.lit(u).alias("unit"))
    return res, pairs_out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    units = pl.read_parquet(L.DATA / "unit_counts.parquet")["unit"].to_list()
    jobs = []
    for u in units:
        for var in L.VARS:
            for model in L.MODELS:
                prim = (var, model) == PRIMARY
                jobs.append((u, var, model, prim, a.fast))
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        out = list(ex.map(run_unit, jobs))
    rows = [r for r, _ in out]
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(RES / "units.parquet")
    pp = [p for _, p in out if p is not None]
    if pp:
        pl.concat(pp, how="diagonal_relaxed").write_parquet(RES / "niche_pairs.parquet")
    pooled = pool(df)
    (RES / "pooled.json").write_text(json.dumps(pooled, indent=1, default=float))
    print(json.dumps(pooled, indent=1, default=float))
    print(f"done in {time.time() - t0:.0f} s")


def pool(df: pl.DataFrame) -> dict:
    out = {}
    for (var, model), g in df.group_by(["var", "model"]):
        key = f"{var}|{model}"
        n = g.filter(pl.col("unit").is_in(list(NICHE)) & pl.col("beta_n").is_not_null()) if "beta_n" in g.columns else g.head(0)
        o = {}
        if n.height:
            for k in ("beta_n", "G", "T_SR", "That_SR", "beta_n_A", "beta_n_B", "G_B", "beta_s", "beta_n_lin", "G_lin"):
                se = k.replace("beta_n_A", "beta_n_A").replace("beta_n_B", "beta_n_B")
                if k in n.columns and f"{k}_se" in n.columns:
                    o[k] = L.re_pool(n[k].to_numpy(), n[f"{k}_se"].to_numpy())
        c = g.filter(pl.col("unit").is_in(list(COUNTED51)))
        o["R_51_mean"] = float(c["R"].mean()) if c.height else np.nan
        o["R_contrast_max"] = float(g.filter(pl.col("unit").is_in(["38a", "39", "40", "41"]))["R"].max())
        o["R_51_min"] = float(c["R"].min()) if c.height else np.nan
        out[key] = o
    return out


if __name__ == "__main__":
    main()
