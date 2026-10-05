"""H69 round 2 synthetic validation on real skeletons (axis F), run before any round-2 statistic on real data.

  uv run python hypotheses/H69-loops-context-fixed-points/analysis/synthetic_r2.py [--reps 60] [--procs 2]

Skeleton: each period's real statements (agent-day order, O, U, K, ctx_pos, P, resets, erasure dose), real pairs and
real memory containment (c_t, c_u, prior copies). Restatement flags and pair outcomes are simulated; the real flags
are never read (except the period's overall restatement rate and persistence, round-1 nuisance levels).
Sequence worlds (R1, R2a): onset logit = offset + agent + 0.32 log(1+O) + 0.40 log(1+ctx_pos) + b_U log(1+U/1000);
  exit logit = c + ln 2.4 * erasure + b_dose * erasure * dose_c.  W0: b_U 0, b_dose 0. WU: b_U 0.32. WD: b_dose 0.7.
Pair worlds (R3): logit P(copy) = offset + agent - 0.5 log(lag/600) - 0.3 log(1+calls) + ln 3.4 * in_seg + ...
  M0: no memory effect. M1: + ln 3 * in_mem (real c_t >= 0.5). M2 (salience): latent z_u ~ N(0,1) adds +1.0 z_u to
  copying and drives simulated memory flags (pre-memory, new memory) and prior copies (noisy proxies).
Outputs: data/processed/H69-loops-context-fixed-points/synthetic/r2_worlds.parquet, r2_summary.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h69lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H69-loops-context-fixed-points"
OUT = D / "synthetic"
PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
LN24 = math.log(2.4)


def load(p, frac=1.0, seed=0):
    st = pl.read_parquet(D / p / "statements.parquet")
    it = pl.read_parquet(D / p / "items.parquet")
    pr = pl.read_parquet(D / p / "pairs.parquet")
    tok = pl.read_parquet(D / p / "r2_tokens.parquet")
    mem = pl.read_parquet(D / p / "r2_memory.parquet")
    if frac < 1:
        ads = st.select("agent", "pt_date").unique().sort("agent", "pt_date")
        keep = ads.filter(pl.Series(np.random.default_rng(seed).random(ads.height) < frac))
        st = st.join(keep, on=["agent", "pt_date"], how="semi")
        ids = st["sid"].implode()
        it, pr, mem = it.filter(pl.col("sid").is_in(ids)), pr.filter(pl.col("sid").is_in(ids)), mem.filter(
            pl.col("sid").is_in(ids))
    s, _ = L.prepare(st, it)
    s = L.attach_r2(s, tok)
    return st, it, pr, tok, mem, s


def simulate_seq(s: pl.DataFrame, off, b_U, b_dose, c_exit, rng, a_ag):
    df = s.sort("agent", "t")
    n = df.height
    ad = df["aday"].to_list()
    ag = df["agent"].to_numpy()
    O = np.log1p(df["o_ctx"].to_numpy().astype(float))
    F = np.log1p(df["ctx_pos"].fill_null(0).to_numpy().astype(float))
    U = df["U_k"].to_numpy().astype(float)
    U = np.log1p(np.where(np.isfinite(U), U, np.nanmedian(U)))
    er = df["reset_between"].fill_null(False).to_numpy()
    dose = df["dose_prev"].to_numpy().astype(float)
    mu = np.nanmean(dose[er & np.isfinite(dose)]) if (er & np.isfinite(dose)).any() else 0.0
    dc = np.where(er & np.isfinite(dose), dose - mu, 0.0)
    eta_on = off + np.array([a_ag[a] for a in ag]) + 0.32 * O + 0.40 * F + b_U * U
    eta_ex = c_exit + LN24 * er + b_dose * dc
    p_on = 1 / (1 + np.exp(-eta_on))
    p_ex = 1 / (1 + np.exp(-eta_ex))
    u = rng.random(n)
    r = np.zeros(n, bool)
    for i in range(n):
        if i > 0 and ad[i] == ad[i - 1] and r[i - 1]:
            r[i] = u[i] >= p_ex[i]
        else:
            r[i] = u[i] < p_on[i]
    return df["sid"].to_numpy(), r


def seq_stats(s, sids, r):
    sim = pl.DataFrame({"sid": sids.astype(np.uint32), "r_sim": r})
    x = s.drop("r_prev").join(sim, on="sid").sort("agent", "t").with_columns(
        pl.col("r_sim").cast(pl.Int8).shift(1).over("agent", "pt_date").alias("r_prev"))
    out = dict(rate=float(r.mean()))
    dense = x.filter(pl.col("dense").fill_null(False) & (pl.col("base_pos") == 0))
    allx = x.filter(pl.col("base_pos") <= 2)
    for name, d in (("dense", dense), ("all", allx)):
        o = L.r1_onset(d, "r_sim")
        if o:
            for k in ("U_k", "o_ctx"):
                b, se = o["terms"][k]
                out[f"z_{name}_{k}"] = b / se if se and np.isfinite(se) and se > 0 else np.nan
                out[f"b_{name}_{k}"] = b
    ex = L.r2_exit_dose(x, "r_sim")
    if ex:
        b, se = ex["terms"]["dose_c"]
        out["z_exit_dose"] = b / se if se and np.isfinite(se) and se > 0 else np.nan
        out["b_exit_dose"] = b
        out["n_exit_erasure"] = ex["n_erasure"]
    on = L.r2_onset_dose(x, "r_sim")
    if on:
        b, se = on["terms"]["dose_c"]
        out["z_onset_dose"] = b / se if se and np.isfinite(se) and se > 0 else np.nan
    return out


def simulate_pairs(p: pl.DataFrame, world, off, rng, a_ag):
    ag = p["agent"].to_numpy()
    lag = p["lag_s"].to_numpy().astype(float)
    cb = p["calls_between"].to_numpy().astype(float)
    ins = p["in_seg"].to_numpy()
    ct = np.nan_to_num(p["c_t"].to_numpy(), nan=0.0)
    eta = off + np.array([a_ag[a] for a in ag]) - 0.5 * np.log(np.maximum(lag, 1) / 600) - 0.3 * np.log1p(cb) \
        + math.log(3.4) * ins
    cols = {}
    if world == "M1":
        eta = eta + math.log(3) * (~ins & (ct >= 0.5))
    if world == "M2":
        su = p["sid_u"].to_numpy()
        uu, inv = np.unique(su, return_inverse=True)
        z = rng.normal(size=len(uu))[inv]
        er = ~ins
        share_pre = float((np.nan_to_num(p["c_u"].to_numpy(), nan=0) >= 0.5)[er].mean())
        share_in = float((ct >= 0.5)[er].mean())
        a_pre = math.log(max(share_pre, 1e-3) / (1 - max(share_pre, 1e-3))) - 0.7
        a_new = math.log(max(share_in - share_pre, 1e-3) / (1 - max(share_in - share_pre, 1e-3))) - 0.7
        pre = rng.random(len(z)) < 1 / (1 + np.exp(-(a_pre + 1.2 * z)))
        new = rng.random(len(z)) < 1 / (1 + np.exp(-(a_new + 1.2 * z)))
        lam = max(float(p["prior_copies"].mean()), 0.05)
        cols = dict(c_u=np.where(pre, 0.9, 0.1).astype(np.float32),
                    c_t=np.where(er, np.where(pre | new, 0.9, 0.1), np.nan).astype(np.float32),
                    prior_copies=rng.poisson(lam * np.exp(0.8 * z - 0.32)))
        eta = eta + 1.0 * z
    y = rng.random(len(eta)) < 1 / (1 + np.exp(-eta))
    q = p.with_columns(pl.Series("y_sim", y), *[pl.Series(k, v) for k, v in cols.items()])
    return q


def pair_stats(q, B):
    out = {}
    e = q.filter(~pl.col("in_seg"))
    r3 = L.r3_stats(e, "y_sim", B=B)
    if r3:
        for k in ("P1", "P2_new", "P2_strat", "within_u"):
            out[f"{k}_lor"] = r3[k]["log_or"]
            out[f"{k}_lo"] = r3[k]["lo"]
            out[f"{k}_hi"] = r3[k]["hi"]
    lb = L.r3_lowerbound(q, "y_sim", B=B)
    out.update(P3_diff=lb["diff"], P3_lo=lb["lo"], P3_hi=lb["hi"])
    return out


def run_period(args):
    p, reps, seed = args
    t0 = time.time()
    frac = 0.25 if p == "G51" else 1.0
    st, it, pr, tok, mem, s = load(p, frac, seed)
    rng = np.random.default_rng(seed)
    rows = []
    # nuisance levels from round 1: restatement rate and persistence
    target = float(s["r_either"].cast(pl.Float64).mean())
    rp = s.filter(pl.col("r_prev") == 1)
    p_stay = float(rp["r_either"].mean()) if rp.height else 0.5
    c_exit = math.log((1 - p_stay) / max(p_stay, 1e-3))
    a_ag = {int(a): rng.normal(0, 0.5) for a in s["agent"].unique().to_list()}
    worlds = {"W0": (0.0, 0.0), "WU": (0.32, 0.0), "WD": (0.0, 0.7)}
    for w, (bu, bd) in worlds.items():
        lo, hi = -10.0, 2.0
        for _ in range(8):
            mid = 0.5 * (lo + hi)
            _, rr = simulate_seq(s, mid, bu, bd, c_exit, np.random.default_rng(seed + 7), a_ag)
            lo, hi = (mid, hi) if rr.mean() < target else (lo, mid)
        off = 0.5 * (lo + hi)
        for rep in range(reps):
            sids, r = simulate_seq(s, off, bu, bd, c_exit, rng, a_ag)
            o = seq_stats(s, sids, r)
            o.update(period=p, world=w, rep=rep)
            rows.append(o)
    # pair worlds
    tb, tg = (json.loads((ROOT / "data/processed/shared/statement_flags_meta.json").read_text())[k]
              for k in ("thr_bge", "thr_gte_rate_matched"))
    pr = pr.with_columns(((pl.col("cos_bge") > tb) | (pl.col("cos_gte") > tg)).alias("y"))
    q0 = L.r3_frame(pr, mem, s)
    target_p = float(q0["y"].mean())
    for w in ("M0", "M1", "M2"):
        lo, hi = -12.0, 2.0
        for _ in range(8):
            mid = 0.5 * (lo + hi)
            yy = simulate_pairs(q0, w, mid, np.random.default_rng(seed + 9), a_ag)["y_sim"].mean()
            lo, hi = (mid, hi) if yy < target_p else (lo, mid)
        off = 0.5 * (lo + hi)
        for rep in range(max(reps // 3, 8)):
            q = simulate_pairs(q0, w, off, rng, a_ag)
            o = pair_stats(q, B=60)
            o.update(period=p, world=w, rep=rep)
            rows.append(o)
    print(f"{p} done {time.time() - t0:.0f}s", flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=60)
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    ps = [a.only] if a.only else PERIODS
    rows = []
    with ProcessPoolExecutor(min(a.procs, 2)) as ex:
        for r in ex.map(run_period, [(p, a.reps if p != "G51" else max(20, a.reps // 2), 700 + i)
                                     for i, p in enumerate(ps)]):
            rows.extend(r)
    df = pl.DataFrame(rows, infer_schema_length=None)
    name = "r2_worlds.parquet" if not a.only else f"r2_worlds_{a.only}.parquet"
    df.write_parquet(OUT / name)

    def rej(c, side):
        if c not in df.columns:
            return pl.lit(None, dtype=pl.Float64).alias(c)
        return ((pl.col(c) > 1.96) if side > 0 else (pl.col(c).abs() > 1.96)).cast(pl.Float64).mean()

    def ci_pos(c):
        if f"{c}_lo" not in df.columns:
            return pl.lit(None, dtype=pl.Float64).alias(c)
        return (pl.col(f"{c}_lo") > 0).cast(pl.Float64).mean()
    summ = df.group_by("period", "world").agg(
        pl.len().alias("reps"), pl.col("rate").mean() if "rate" in df.columns else pl.lit(None),
        rej("z_dense_U_k", 1).alias("R1_bU_dense"), rej("z_all_U_k", 1).alias("R1_bU_all"),
        rej("z_dense_o_ctx", 1).alias("R1_bO_dense"), rej("z_all_o_ctx", 1).alias("R1_bO_all"),
        rej("z_exit_dose", 1).alias("R2_exit_dose"), rej("z_onset_dose", 0).alias("R2_onset_dose_2s"),
        pl.col("n_exit_erasure").mean() if "n_exit_erasure" in df.columns else pl.lit(None),
        ci_pos("P1").alias("R3_P1"), ci_pos("P2_new").alias("R3_P2_new"), ci_pos("P2_strat").alias("R3_P2_strat"),
        ci_pos("within_u").alias("R3_within_u"), ci_pos("P3").alias("R3_P3"),
        pl.col("P1_lor").median() if "P1_lor" in df.columns else pl.lit(None),
        pl.col("P2_strat_lor").median() if "P2_strat_lor" in df.columns else pl.lit(None),
        pl.col("within_u_lor").median() if "within_u_lor" in df.columns else pl.lit(None),
    ).sort("period", "world")
    (OUT / ("r2_summary.json" if not a.only else f"r2_summary_{a.only}.json")).write_text(
        json.dumps(summ.to_dicts(), indent=1, default=float))
    with pl.Config(tbl_rows=60, tbl_cols=25, tbl_width_chars=300):
        print(summ)


def summarize():
    """Per-period rejection rates with NaN-safe comparisons (polars ranks NaN above every number: infra Known
    issues, H63) and pooled power over the scorable periods. Writes r2_summary.json and r2_pooled_power.json."""
    df = pl.read_parquet(OUT / "r2_worlds.parquet")

    def fin(c):
        return pl.col(c).is_not_null() & pl.col(c).is_finite()

    def rej(c):
        return (fin(c) & (pl.col(c) > 1.96)).cast(pl.Float64).mean()

    def cip(c):
        return (fin(f"{c}_lo") & fin(f"{c}_lor") & (pl.col(f"{c}_lo") > 0)).cast(pl.Float64).mean()
    seq = df.filter(pl.col("world").str.starts_with("W")).group_by("period", "world").agg(
        pl.len().alias("reps"), pl.col("rate").mean(),
        rej("z_dense_U_k").alias("R1_bU_dense"), rej("z_all_U_k").alias("R1_bU_all"),
        rej("z_dense_o_ctx").alias("R1_bO_dense"), rej("z_all_o_ctx").alias("R1_bO_all"),
        rej("z_exit_dose").alias("R2_exit_dose"), pl.col("n_exit_erasure").mean())
    prs = df.filter(pl.col("world").str.starts_with("M")).group_by("period", "world").agg(
        pl.len().alias("reps"), cip("P1").alias("R3_P1"), cip("P2_new").alias("R3_P2_new"),
        cip("P2_strat").alias("R3_P2_strat"), cip("within_u").alias("R3_within_u"),
        fin("within_u_lor").cast(pl.Float64).mean().alias("R3_within_u_estimable"),
        (fin("P3_lo") & (pl.col("P3_lo") > 0)).cast(pl.Float64).mean().alias("R3_P3"),
        pl.col("P1_lor").median().alias("P1_lor_median"))
    summ = pl.concat([seq, prs], how="diagonal").sort("period", "world")
    (OUT / "r2_summary.json").write_text(json.dumps(summ.to_dicts(), indent=1, default=float))

    def pooled(world, periods, getter):
        d = df.filter(pl.col("world") == world)
        nrep = min(d.filter(pl.col("period") == p).height for p in periods)
        hits = []
        for i in range(nrep):
            e, s = [], []
            for p in periods:
                r = d.filter((pl.col("period") == p) & (pl.col("rep") == i))
                if r.height:
                    v = getter(r)
                    if v:
                        e.append(v[0])
                        s.append(v[1])
            po = L.dl_pool(e, s)
            hits.append(bool(po["k"] > 0 and po["lo"] > 0))
        return dict(power=float(np.mean(hits)), reps=nrep, periods=periods)

    def g_seq(b, z):
        def f(r):
            bb, zz = r[b][0], r[z][0]
            if bb is None or zz is None or not np.isfinite(bb) or not np.isfinite(zz) or zz == 0:
                return None
            return bb, abs(bb / zz)
        return f

    def g_or(c):
        def f(r):
            b, lo, hi = r[f"{c}_lor"][0], r[f"{c}_lo"][0], r[f"{c}_hi"][0]
            if None in (b, lo, hi) or not np.all(np.isfinite([b, lo, hi])) or hi <= lo:
                return None
            return b, (hi - lo) / 3.92
        return f
    S1 = ["G38", "G40", "G41", "G51"]
    S3 = ["G38", "G39", "G40", "G41", "G51"]
    res = {}
    for w in ("W0", "WU", "WD"):
        for name, b, z in (("bU_dense", "b_dense_U_k", "z_dense_U_k"), ("bU_all", "b_all_U_k", "z_all_U_k"),
                           ("bO_dense", "b_dense_o_ctx", "z_dense_o_ctx"), ("bO_all", "b_all_o_ctx", "z_all_o_ctx"),
                           ("exit_dose", "b_exit_dose", "z_exit_dose")):
            res[f"{w}_{name}"] = pooled(w, S1, g_seq(b, z))
    for w in ("M0", "M1", "M2"):
        for c in ("P1", "P2_new", "P2_strat"):
            res[f"{w}_{c}"] = pooled(w, S3, g_or(c))
    (OUT / "r2_pooled_power.json").write_text(json.dumps(res, indent=1))
    with pl.Config(tbl_rows=80, tbl_cols=25, tbl_width_chars=300):
        print(summ)
    for k, v in res.items():
        print(k, v["power"])


if __name__ == "__main__":
    if "--summarize" in sys.argv:
        summarize()
    else:
        main()
