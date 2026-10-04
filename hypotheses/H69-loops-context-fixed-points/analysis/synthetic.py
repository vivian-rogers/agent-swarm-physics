"""H69 synthetic validation on real skeletons (axis F), run before any H69 statistic on real data.

  uv run python hypotheses/H69-loops-context-fixed-points/analysis/synthetic.py [--reps 20] [--procs 4]

Skeleton: each period's real statements (agent-day order, times, producing calls, segments, O, K, resets, read counts
and novelty counts of read / in-flight items) and the real pair structure. Statement vectors (32-d) are simulated:
a restatement copies an earlier-call statement u of the same day (cos ~ 0.97); otherwise a fresh statement is drawn
around a drifting agent-day topic (cos ~ 0.6). The flag is computed as on real data: max cosine to earlier-call
statements > 0.95. The overall flag rate is matched to the period's real restatement rate (a nuisance level).
Worlds:
  Z0  recency/topic null: logit q = a + rho * r_prev - 0.3 log(lag / 600); source weights decay with calls between
      and lag, blind to segments; no input effect;
  Z1  H69: logit q = a + J (s - 0.3)+ - c_nu * r_prev * log(1 + novel reads); the source is drawn blind to segments
      and copied if still in context, or with probability 0.25 if erased (J = 4, c_nu = 0.7);
  Z2  input starvation: logit q = a - 0.7 log(1 + reads since previous); sources blind to segments.
Statistics: onset (b_s, b_K, hinge dAIC), exit (forced, novel read, in-flight, next-call), enrichment (in context vs
erased; pseudo half), episodes. Outputs: data/processed/H69-loops-context-fixed-points/synthetic/.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

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
import h69lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H69-loops-context-fixed-points"
OUT = D / "synthetic"
PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
DIM = 32
THR = 0.95


def load(p, frac=1.0, seed=0):
    st = pl.read_parquet(D / p / "statements.parquet")
    it = pl.read_parquet(D / p / "items.parquet")
    pr = pl.read_parquet(D / p / "pairs.parquet")
    if frac < 1:
        ads = st.select("agent", "pt_date").unique().sort("agent", "pt_date")
        rng = np.random.default_rng(seed)
        keep = ads.filter(pl.Series(rng.random(ads.height) < frac))
        st = st.join(keep, on=["agent", "pt_date"], how="semi")
        it = it.filter(pl.col("sid").is_in(st["sid"].implode()))
        pr = pr.filter(pl.col("sid").is_in(st["sid"].implode()))
    st0, thr = L.prepare(st, it)  # real novelty counts (covariates); r_prev from real flags is replaced below
    return st, it, pr, st0


def simulate(st0: pl.DataFrame, world: str, offset: float, rng) -> np.ndarray:
    """Synthetic vectors per statement (rows in st0 order sorted by agent, t)."""
    df = st0.sort("agent", "t")
    n = df.height
    V = np.zeros((n, DIM), np.float32)
    r = np.zeros(n, bool)
    ad = df["aday"].to_list()
    ci = df["call_idx"].to_numpy()
    seg = df["seg"].to_numpy()
    tt = df["t"].dt.epoch("us").to_numpy() / 1e6
    s_self = df["s_self"].to_numpy()
    nread = df["n_read"].fill_null(0).to_numpy()
    novr = df["nov_read"].to_numpy()
    agent = df["agent"].to_numpy()
    a_ag = {a: rng.normal(0, 0.5) for a in np.unique(agent)}
    start = 0
    while start < n:
        end = start
        while end < n and ad[end] == ad[start]:
            end += 1
        T = rng.normal(size=DIM)
        T /= np.linalg.norm(T)
        for i in range(start, end):
            T = T + 0.15 * rng.normal(size=DIM) / np.sqrt(DIM)
            T /= np.linalg.norm(T)
            js = np.arange(start, i)
            js = js[(ci[js] < ci[i]) & (tt[i] - tt[js] <= 3 * 3600)]
            copied = False
            if len(js):
                rp = float(r[i - 1]) if i > start else 0.0
                lag = max(tt[i] - tt[i - 1], 1.0) if i > start else 600.0
                base = offset + a_ag[agent[i]]
                if world == "Z0":
                    eta = base + 1.0 * rp - 0.3 * np.log(lag / 600)
                elif world == "Z1":
                    eta = base + 4.0 * max(s_self[i] - 0.3, 0) - 0.7 * rp * np.log1p(novr[i])
                else:
                    eta = base - 0.7 * np.log1p(nread[i])
                q = 1 / (1 + np.exp(-eta))
                if rng.random() < q:
                    w = np.exp(-(ci[i] - ci[js]) / 20.0) * np.exp(-(tt[i] - tt[js]) / 3600.0)
                    w = w / w.sum()
                    u = js[rng.choice(len(js), p=w)]
                    # Z1: a source still in context is copied; an erased one only with probability 0.25
                    if world != "Z1" or seg[u] == seg[i] or rng.random() < 0.25:
                        v = V[u] + 0.25 * rng.normal(size=DIM) / np.sqrt(DIM)
                        copied = True
            if not copied:
                v = T + 0.75 * rng.normal(size=DIM) / np.sqrt(DIM)
            V[i] = v / np.linalg.norm(v)
            if len(js):
                r[i] = bool(np.max(V[js] @ V[i]) > THR)
        start = end
    return V, r, df["sid"].to_numpy()


def stats_for(st, it, pr, V, r, sids):
    sim = pl.DataFrame({"sid": sids.astype(np.uint32), "r_sim": r})
    st2 = st.join(sim, on="sid", how="inner")
    s3, _ = L.prepare(st2, it, resp="r_sim")
    row = L.episodes(s3, "r_sim")
    on = L.onset(s3, "r_sim")
    ex = L.exit_model(s3, "r_sim")
    pos = {int(s): k for k, s in enumerate(sids)}
    iu = np.array([pos.get(int(x), -1) for x in pr["sid_u"].to_numpy()])
    itt = np.array([pos.get(int(x), -1) for x in pr["sid"].to_numpy()])
    ok = (iu >= 0) & (itt >= 0)
    y = np.zeros(pr.height, bool)
    y[ok] = np.einsum("ij,ij->i", V[itt[ok]], V[iu[ok]]) > THR
    p2 = pr.with_columns(pl.Series("y", y)).filter(pl.Series(ok))
    en = L.enrichment(p2, s3, B=60)
    ps = L.enrichment(p2, s3, B=60, exposure="same_half", restrict=pl.col("in_seg"))
    out = dict(rate=row["rate"], n_episodes=row["n_episodes"])
    if on:
        out.update(b_s=on["b_s"], z_s=on["b_s"] / on["se_s"], b_K=on["b_K"], z_K=on["b_K"] / on["se_K"],
                   dAIC=on["dAIC_hinge"], s_star=on["s_star"])
    if ex:
        for k in ("forced_between", "nov_read", "nov_infl", "nov_read_next"):
            out[f"b_{k}"] = ex[f"b_{k}"]
            out[f"z_{k}"] = ex[f"b_{k}"] / ex[f"se_{k}"] if ex[f"se_{k}"] and np.isfinite(ex[f"se_{k}"]) else np.nan
    if en:
        out.update(lor=en["log_or"], lor_lo=en["lo"], lor_hi=en["hi"])
    if ps:
        out.update(pseudo_lor=ps["log_or"], pseudo_lo=ps["lo"], pseudo_hi=ps["hi"])
    return out


def run_period(args):
    p, reps, seed = args
    t0 = time.time()
    frac = 0.25 if p == "G51" else 1.0
    st, it, pr, st0 = load(p, frac, seed)
    target = float(st["r_either"].cast(pl.Float64).mean())
    rng = np.random.default_rng(seed)
    rows = []
    for world in ("Z0", "Z1", "Z2"):
        # calibrate the offset to the real restatement rate (nuisance level)
        lo, hi = -8.0, 4.0
        for _ in range(7):
            mid = 0.5 * (lo + hi)
            _, rr, _ = simulate(st0, world, mid, np.random.default_rng(seed + 99))
            lo, hi = (mid, hi) if rr.mean() < target else (lo, mid)
        off = 0.5 * (lo + hi)
        for rep in range(reps):
            V, r, sids = simulate(st0, world, off, rng)
            o = stats_for(st, it, pr, V, r, sids)
            o.update(period=p, world=world, rep=rep, offset=off, target_rate=target)
            rows.append(o)
    print(f"{p} done {time.time() - t0:.0f}s", flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    ps = [a.only] if a.only else PERIODS
    rows = []
    with ProcessPoolExecutor(a.procs) as ex:
        for r in ex.map(run_period, [(p, a.reps if p != "G51" else max(6, a.reps // 2), 500 + i)
                                     for i, p in enumerate(ps)]):
            rows.extend(r)
    df = pl.DataFrame(rows, infer_schema_length=None)
    for c in ("z_s", "z_K", "dAIC", "z_forced_between", "z_nov_read", "z_nov_infl", "z_nov_read_next", "lor", "lor_lo",
              "lor_hi", "pseudo_lo", "pseudo_hi"):
        if c not in df.columns:
            df = df.with_columns(pl.lit(None, dtype=pl.Float64).alias(c))
    name = "worlds.parquet" if not a.only else f"worlds_{a.only}.parquet"
    df.write_parquet(OUT / name)

    def rej(c, side):
        return ((pl.col(c) > 1.96) if side > 0 else (pl.col(c) < -1.96)).cast(pl.Float64).mean()
    summ = df.group_by("period", "world").agg(
        pl.col("rate").mean(), pl.col("n_episodes").mean(),
        rej("z_s", 1).alias("P1_bs_pos"), rej("z_K", -1).alias("P1_bK_neg"), (pl.col("dAIC") >= 4).cast(pl.Float64).mean().alias("P2_hinge"),
        rej("z_forced_between", 1).alias("P3_forced"), rej("z_nov_read", 1).alias("P5_read"),
        rej("z_nov_infl", 1).alias("P5_infl"), rej("z_nov_read_next", 1).alias("P5_next"),
        (pl.col("lor_lo") > 0).cast(pl.Float64).mean().alias("P4_lor_pos"), pl.col("lor").median(),
        ((pl.col("pseudo_lo") > 0) | (pl.col("pseudo_hi") < 0)).cast(pl.Float64).mean().alias("pseudo_rej"),
    ).sort("period", "world")
    (OUT / ("summary.json" if not a.only else f"summary_{a.only}.json")).write_text(json.dumps(summ.to_dicts(), indent=1))
    with pl.Config(tbl_rows=40, tbl_cols=20, tbl_width_chars=250):
        print(summ)


if __name__ == "__main__":
    main()
