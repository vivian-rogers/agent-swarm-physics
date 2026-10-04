"""H68 synthetic validation on real unit skeletons (axis F), run before any per-agent statistic on real data.

  uv run python hypotheses/H68-dilution-mixture/analysis/synthetic.py [--reps 30] [--procs 4]

Skeleton: each period's real units (agent, day, k, n, mention). Responses are simulated from the uptake model with
agent rates matched to the agent's real response rate (a nuisance level), day effects N(0, 0.4^2), mention factor 2.2.
Worlds (population layer):
  W0  one exponent, beta_i = 0.65 (tau = 0)
  W1  unimodal spread, beta_i ~ N(0.65, 0.15^2)
  W2  H68 literal: beta_i = 1 w.p. 0.65 else 0 (tau_w = 0.05)
  W3  soft two-strategy: beta_i in {0.95, 0.35} w.p. 1/2
Per rep: eligible agents, per-agent fits, mixture test (B = 100), tau profile CI, P1 rule.
Pooled family/trait worlds (all periods at once): L0 agent traits without lab (agent sd 0.15, agent x period sd 0.1);
L1 lab sets the strategy (each lab thin = 1 or thread = 0, agent x period sd 0.05).
Outputs: data/processed/H68-dilution-mixture/synthetic/{period_worlds.parquet, summary.json, lab_worlds.json}.
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
import h68lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H68-dilution-mixture"
OUT = D / "synthetic"
PERIODS = ["G10", "G24", "G25", "G26", "G27", "G30", "G31", "G35", "G36", "G37", "G38", "G39", "G40", "G41", "G42",
           "G44", "G51"]
GAMMA = np.log(2.2)
BETA0 = 0.65


def draw_betas(world, n, rng):
    if world == "W0":
        return np.full(n, BETA0)
    if world == "W1":
        return rng.normal(BETA0, 0.15, n)
    if world == "W2":
        return np.where(rng.random(n) < 0.65, 1.0, 0.0) + rng.normal(0, 0.05, n)
    if world == "W3":
        return np.where(rng.random(n) < 0.5, 0.95, 0.35)
    raise ValueError(world)


def simulate(units: pl.DataFrame, beta_of: dict, rng, rate_of: dict) -> np.ndarray:
    """Simulated responses for every unit given per-agent beta; agent level matched to rate_of[agent]."""
    y = np.zeros(units.height, dtype=bool)
    ag = units["agent"].to_numpy()
    dd = units["day"].to_numpy().astype(int)
    lk = units["logk"].to_numpy()
    ln = np.log(units["n"].to_numpy().astype(float))
    mm = units["ment"].to_numpy().astype(float)
    dayeff = rng.normal(0, 0.4, dd.max() + 1)
    for a in np.unique(ag):
        idx = np.where(ag == a)[0]
        base = ln[idx] - beta_of[a] * lk[idx] + GAMMA * mm[idx] + dayeff[dd[idx]]
        target = rate_of[a]
        lo, hi = -15.0, 8.0
        for _ in range(50):
            mid = 0.5 * (lo + hi)
            pm = np.mean(1 - np.exp(-np.exp(np.clip(mid + base, -30, 6))))
            lo, hi = (mid, hi) if pm < target else (lo, mid)
        p = 1 - np.exp(-np.exp(np.clip(0.5 * (lo + hi) + base, -30, 6)))
        y[idx] = rng.random(len(idx)) < p
    return y


def per_agent(units: pl.DataFrame, resp: str):
    rows = []
    for (a,), g in units.group_by(["agent"], maintain_order=True):
        if not L.eligible(g, resp):
            continue
        r = L.agent_fit(g, resp)
        r["agent"] = int(a)
        rows.append(r)
    return rows


def run_period(args):
    p, reps, B, seed = args
    t0 = time.time()
    units = pl.read_parquet(D / p / "units.parquet").select("agent", "day", "logk", "n", "ment", "resp", "lab", "sender")
    rate_of = {int(a): max(float(r), 0.01) for a, r in
               units.group_by("agent").agg(pl.col("resp").mean()).iter_rows()}
    agents = sorted(rate_of)
    rng = np.random.default_rng(seed)
    rows = []
    for world in ("W0", "W1", "W2", "W3"):
        for rep in range(reps):
            bt = draw_betas(world, len(agents), rng)
            beta_of = dict(zip(agents, bt))
            y = simulate(units, beta_of, rng, rate_of)
            u = units.with_columns(pl.Series("ysim", y))
            fits = per_agent(u, "ysim")
            n_el = len(fits)
            row = dict(period=p, world=world, rep=rep, n_eligible=n_el)
            if n_el >= 4:
                b = np.array([f["beta"] for f in fits])
                s = np.array([f["se"] for f in fits])
                tr = np.array([beta_of[f["agent"]] for f in fits])
                mt = L.mixture_test(b, s, B=B, seed=int(rng.integers(1 << 30)))
                lo, hi = L.tau_profile_ci(b, s)
                row.update(p=mt["p"], lr=mt["lr"], p1=L.p1_pass(mt), tau=mt["U"]["tau"], tau_lo=lo, tau_hi=hi,
                           mu=mt["U"]["mu"], m_lo=mt["M2"]["m_lo"], m_hi=mt["M2"]["m_hi"], dll_h68=mt["dll_H68_U"],
                           bias=float(np.mean(b - tr)), z_sd=float(np.std((b - tr) / s)),
                           cover=float(np.mean(np.abs((b - tr) / s) < 1.96)), med_se=float(np.median(s)),
                           mid_share=float(np.mean((b >= 0.3) & (b <= 0.7))))
            rows.append(row)
    print(f"{p} done {time.time() - t0:.0f}s", flush=True)
    return rows


def lab_worlds(reps, seed, B=0):
    """Pooled family and trait worlds over all periods (per-agent fits only; no bootstrap)."""
    rng = np.random.default_rng(seed)
    allu = {p: pl.read_parquet(D / p / "units.parquet").select("agent", "day", "logk", "n", "ment", "resp", "lab")
            for p in PERIODS}
    labs = {}
    for u in allu.values():
        labs.update(dict(u.select("agent", "lab").unique().iter_rows()))
    agents = sorted(labs)
    out = {}
    for world in ("L0", "L1"):
        res = []
        for rep in range(reps):
            if world == "L0":
                trait = dict(zip(agents, rng.normal(0, 0.15, len(agents))))
                beta_ap = lambda a: BETA0 + trait[a] + rng.normal(0, 0.10)  # noqa: E731
            else:
                ul = sorted(set(labs.values()))
                while True:
                    lab_b = dict(zip(ul, (rng.random(len(ul)) < 0.6).astype(float)))
                    if 0 < sum(lab_b.values()) < len(ul):
                        break
                beta_ap = lambda a: lab_b[labs[a]] + rng.normal(0, 0.05)  # noqa: E731
            recs = []
            for p, u in allu.items():
                rate_of = {int(a): max(float(r), 0.01) for a, r in u.group_by("agent").agg(pl.col("resp").mean()).iter_rows()}
                beta_of = {a: beta_ap(a) for a in rate_of}
                y = simulate(u, beta_of, rng, rate_of)
                for f in per_agent(u.with_columns(pl.Series("ysim", y)), "ysim"):
                    recs.append(dict(agent=f["agent"], period=p, lab=labs[f["agent"]], beta=f["beta"], se=f["se"]))
            df = pl.DataFrame(recs)
            ls = L.lab_share(df, n_perm=500, seed=rep)
            ti = L.trait_icc(df, n_boot=200, seed=rep)
            res.append(dict(eta2=ls["eta2"], p=ls["p"], icc=ti["icc"], icc_lo=ti["ci"][0], icc_hi=ti["ci"][1]))
            print(world, rep, res[-1], flush=True)
        out[world] = res
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--B", type=int, default=100)
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--lab-reps", type=int, default=20)
    ap.add_argument("--only", default=None)
    ap.add_argument("--labs-only", action="store_true")
    a = ap.parse_args()
    if a.labs_only:
        OUT.mkdir(parents=True, exist_ok=True)
        lw = lab_worlds(a.lab_reps, 7)
        (OUT / "lab_worlds.json").write_text(json.dumps(lw, indent=1))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    ps = [a.only] if a.only else PERIODS
    jobs = [(p, a.reps, a.B, 1000 + i) for i, p in enumerate(ps)]
    rows = []
    with ProcessPoolExecutor(a.procs) as ex:
        for r in ex.map(run_period, jobs):
            rows.extend(r)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(OUT / "period_worlds.parquet")
    summ = (df.group_by("period", "world").agg(
        pl.col("n_eligible").median(), pl.col("p1").cast(pl.Float64).mean().alias("p1_rate"),
        (pl.col("p") < 0.05).cast(pl.Float64).mean().alias("lr_reject"), pl.col("tau").median(),
        (pl.col("tau_hi") < 0.35).cast(pl.Float64).mean().alias("tauhi_lt035"), pl.col("bias").mean(),
        pl.col("z_sd").median(), pl.col("cover").mean(), pl.col("med_se").median(), pl.col("mid_share").mean())
        .sort("period", "world"))
    (OUT / "summary.json").write_text(json.dumps(summ.to_dicts(), indent=1))
    print(summ)
    if a.lab_reps and not a.only:
        lw = lab_worlds(a.lab_reps, 7)
        (OUT / "lab_worlds.json").write_text(json.dumps(lw, indent=1))


if __name__ == "__main__":
    main()
