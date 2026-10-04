"""H104 synthetic validation at real counts (axis F), run before any real-data statistic.

Structure kept from each eligible period and channel: at-risk agent-day spans, eligible step times and at-risk counts,
quiet windows, and each agent-day's number of switches (counts only; no switch timing is read). Worlds:
  W0  null: each agent-day's switches placed uniformly in its span (Poisson given the count)
  W1  Barkhausen: W0 background (thinned to keep the total) + at each step, with prob 1 - pi0 an avalanche of
      A ~ truncated power law (tau = 1.5) distinct at-risk agents switching at t_k + Exp(15 min) (within W)
  W2  thin response: as W1 but A ~ Poisson(mu) with mu matched to W1's mean avalanche
  W3  endogenous bursts: background regrouped into clusters (1 + Geometric(mean 3) agents within 20 min) at random
      times; no step response
Every world is run through the real-data estimators (n_draw = 199). Reported: rejection rates per period x world.

    uv run python hypotheses/H104-barkhausen-avalanches/analysis/synthetic.py [--reps 20]
Output: data/processed/H104-barkhausen-avalanches/synthetic/{results.parquet, summary.json}
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
import h104lib as L  # noqa: E402

OUT = L.DATA / "synthetic"
W = L.W_DEFAULT
TAU, PI0, DELAY = 1.5, 0.3, 900.0


def structure(g: int, channel: str):
    P = L.load_period(g)
    if not P:
        return None
    ad = L.agent_days(P, "span")
    sw = L.switches_in(P, channel, ad)
    st = L.eligible_steps(P, ad, W)
    if st.height < 3 or sw.height < 30:
        return None
    q0, qd = L.quiet_windows(P, ad, W)
    counts = sw.group_by("ad").len()
    n_ad = np.zeros(ad.height, int)
    n_ad[counts["ad"].to_numpy()] = counts["len"].to_numpy()
    return {"g": g, "channel": channel, "ad": ad, "n_ad": n_ad, "steps": st, "q0": q0, "qd": qd}


def pl_sample(rng, nmax, tau=TAU):
    s = np.arange(1, nmax + 1)
    p = s ** (-tau)
    return int(rng.choice(s, p=p / p.sum()))


def mean_pl(nmax, tau=TAU):
    s = np.arange(1, nmax + 1)
    p = s ** (-tau)
    return float((s * p).sum() / p.sum())


def simulate(Sx: dict, world: str, rng) -> pl.DataFrame:
    ad = Sx["ad"]
    lo, hi = ad["risk_lo"].to_numpy(), ad["risk_hi"].to_numpy()
    dd, ag = ad["pt_date"].to_numpy(), ad["agent"].to_numpy()
    n_ad = Sx["n_ad"].copy()
    st = Sx["steps"]
    tk, dk = st["t"].to_numpy(), st["pt_date"].to_numpy()
    av_rows = []
    if world in ("W1", "W2"):
        for t, d in zip(tk, dk):
            risk = np.flatnonzero((dd == d) & (lo <= t) & (hi >= t + W))
            if len(risk) == 0 or rng.random() < PI0:
                continue
            if world == "W1":
                A = pl_sample(rng, len(risk))
            else:
                A = min(len(risk), max(1, rng.poisson(mean_pl(len(risk)))))
            for a in rng.choice(risk, A, replace=False):
                dt_ = min(rng.exponential(DELAY), W - 1)
                av_rows.append((a, t + dt_))
        # thin background to keep each agent-day's total (as far as possible)
        for a, _ in av_rows:
            if n_ad[a] > 0:
                n_ad[a] -= 1
    rows = []
    if world == "W3":
        # regroup background into clusters per day
        for d in np.unique(dd):
            idx = np.flatnonzero(dd == d)
            pool = np.repeat(idx, n_ad[idx])
            rng.shuffle(pool)
            k = 0
            while k < len(pool):
                size = 1 + rng.geometric(1 / 3.0)
                members = pool[k:k + size]
                k += size
                lo_d, hi_d = lo[idx].min(), hi[idx].max()
                c = lo_d + rng.random() * (hi_d - lo_d)
                for a in members:
                    t = c + rng.random() * 1200.0
                    if t < lo[a] or t > hi[a]:
                        t = lo[a] + rng.random() * (hi[a] - lo[a])
                    rows.append((a, t))
    else:
        for a in np.flatnonzero(n_ad > 0):
            for t in lo[a] + rng.random(n_ad[a]) * (hi[a] - lo[a]):
                rows.append((a, t))
    rows += av_rows
    df = pl.DataFrame(rows, schema={"ad": pl.UInt32, "t": pl.Float64}, orient="row")
    return df.join(ad.select("ad", "agent", "pt_date"), on="ad").select("ad", "agent", "pt_date", "t").sort("ad", "t")


def evaluate(Sx: dict, sw: pl.DataFrame, n_draw: int, seed: int) -> dict:
    ad, st = Sx["ad"], Sx["steps"]
    pan = L.Panel(ad, sw, st["t"].to_numpy(), W, st["pt_date"].to_numpy())
    S, _ = pan.counts(pan.sw_t)
    Sn, _ = pan.null(n_draw, seed)
    r = L.step_response(S, Sn, B=500, seed=seed)
    out = {"X": r["X"], "p_X": r["p_X"], "V": r["V"], "p_V": r["p_V"], "F_A": r["F_A"],
           "F_A_lo": r["F_A_ci"][0], "F_A_hi": r["F_A_ci"][1], "n_steps": len(S)}
    t = L.tau_mle(S, Sn, pan.n_at_risk)
    out.update({"tau": t["tau"], "tau_lo": t["tau_lo"], "tau_hi": t["tau_hi"], "pi": t["pi"], "llr": t["llr_vs_null"]})
    if len(Sx["q0"]) >= 5:
        pq = L.Panel(ad, sw, Sx["q0"], W, Sx["qd"])
        Sq, _ = pq.counts(pq.sw_t)
        Sqn, _ = pq.null(n_draw, seed + 1)
        dsp = L.dispersion(Sq, Sqn)
        br = L.burst_ratio(S, Sn, Sq, Sqn, B=500, seed=seed)
        out.update({"D": dsp["D"], "D_lo": dsp["D_band"][0], "D_hi": dsp["D_band"][1], "p_D": dsp["p_D"],
                    "BR": br["BR"], "BR_lo": br["BR_ci"][0], "n_quiet": len(Sq)})
    return out


def job(args):
    g, channel, world, rep = args
    Sx = structure(g, channel)
    rng = np.random.default_rng(zlib.crc32(f"{g}|{channel}|{world}|{rep}".encode()))
    sw = simulate(Sx, world, rng)
    return {"g": g, "channel": channel, "world": world, "rep": rep, **evaluate(Sx, sw, 199, rep)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    per = pl.read_parquet(L.DATA / "periods.parquet")
    elig = []
    for g in per["goal_no"].to_list():
        for ch in ("work", "attn"):
            Sx = structure(g, ch)
            if Sx is not None:
                elig.append((g, ch, Sx["steps"].height, int(Sx["n_ad"].sum()), len(Sx["q0"])))
    print("eligible (g, channel, steps, switches, quiet):", elig, flush=True)
    jobs = [(g, ch, w, r) for (g, ch, *_ ) in elig for w in ("W0", "W1", "W2", "W3") for r in range(a.reps)]
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(job, jobs, chunksize=2))
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(OUT / "results.parquet")
    s = summarize(df, elig)
    (OUT / "summary.json").write_text(json.dumps(s, indent=1, default=float))
    print(json.dumps(s, indent=1, default=float))
    print(f"{len(jobs)} jobs in {time.time() - t0:.0f} s")


def summarize(df: pl.DataFrame, elig) -> dict:
    agg = df.group_by("g", "channel", "world").agg(
        pl.col("n_steps").first(),
        (pl.col("p_X") < 0.05).mean().alias("rate_X"),
        ((pl.col("V") > 1) & (pl.col("F_A_lo") > 1)).mean().alias("rate_tail"),
        (pl.col("p_V") < 0.05).mean().alias("rate_pV"),
        ((pl.col("tau") >= 1.2) & (pl.col("tau") <= 1.8) & (pl.col("tau_hi") < 3)).mean().alias("rate_tau_band"),
        pl.col("tau").median().alias("tau_med"), pl.col("F_A").median().alias("F_A_med"),
        ((pl.col("D") >= 0.8) & (pl.col("D") <= 1.25)).mean().alias("rate_D_band"),
        (pl.col("BR_lo") > 1).mean().alias("rate_BR"),
    ).sort("g", "channel", "world")
    return {"eligible": elig, "table": agg.to_dicts()}


if __name__ == "__main__":
    main()
