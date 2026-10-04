"""H111 synthetic validation (axis F) on real call grids, before any real-data statistic.

Talk is simulated at the real receiving calls of the present agents inside each day's all-present window:
  P(talk at call c of i) = clip(a_i f(t) + J R_ic + rho Y_{i,c-1}, 0, 1)
R_ic = simulated peer messages posted in i's room in [t_{c-1}, t_c) (H67's visibility rule); m messages per talk call
(1 + Poisson(mbar - 1)), posted at the call's first output. a_i from the agent's real talk-call share (skeleton
profile), scaled by (1 - g)(1 - rho). J = g / (mbar * rbar) with rbar the mean number of present room-mates.
f(t) = exp(sigma z - sigma^2/2), z a shared OU process (tau_f). The realized g_true = J * mbar_sim * readers per message.
Worlds: g0, g15, g30, rho (private persistence 0.3), f30 / f5 (shared field, no coupling), g15f30.
Outputs data/processed/H111-talk-fano-sum-rule/synthetic/{runs.parquet, summary.json}.
Usage: uv run python hypotheses/H111-talk-fano-sum-rule/analysis/synthetic.py [--reps 8]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import bisect  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h111lib as L  # noqa: E402

UNITS = ["27", "41", "44b", "51e"]
WORLDS = {
    "g0": dict(g=0.0), "g15": dict(g=0.15), "g30": dict(g=0.30), "rho": dict(g=0.0, rho=0.3),
    "f30": dict(g=0.0, sigma=0.5, tau=30.0), "f5": dict(g=0.0, sigma=0.5, tau=5.0),
    "g15f30": dict(g=0.15, sigma=0.5, tau=30.0),
}
MBAR = 1.0


def simulate(U: L.Unit, seed: int, g: float = 0.0, rho: float = 0.0, sigma: float = 0.0, tau: float = 30.0):
    rng = np.random.default_rng(seed)
    rows_t, rows_d, rows_a, rows_r = [], [], [], []
    n_msgs = 0
    readers_sum = 0.0
    talk_calls = 0
    # skeleton: per-agent talk-call share inside trimmed windows
    tc = []
    for d, lo, hi, kick, agents, rooms in L._day_frame(U, "trim"):
        c = U.calls.filter((pl.col("day") == d) & (pl.col("t_call") >= lo) & (pl.col("t_call") <= hi)
                           & pl.col("agent").is_in(agents.tolist()))
        tc.append(c)
    allc = pl.concat(tc) if tc else U.calls.head(0)
    share = {a: s for a, s in allc.group_by("agent").agg(pl.col("talk").mean()).iter_rows()}
    rbar_list = []
    for d, lo, hi, kick, agents, rooms in L._day_frame(U, "trim"):
        _, sz = np.unique(rooms, return_counts=True)
        rmap = dict(zip(agents.tolist(), rooms.tolist()))
        rbar_list.append(np.mean([(rooms == rmap[a]).sum() - 1 for a in agents.tolist()]))
    rbar = float(np.mean(rbar_list)) if rbar_list else 1.0
    J = g / (MBAR * max(rbar, 1e-9))
    for d, lo, hi, kick, agents, rooms in L._day_frame(U, "trim"):
        rmap = dict(zip(agents.tolist(), rooms.tolist()))
        c = (U.calls.filter((pl.col("day") == d) & (pl.col("t_call") >= lo) & (pl.col("t_call") <= hi)
                            & pl.col("agent").is_in(agents.tolist())).sort("t_call"))
        tcall = c["t_call"].to_numpy()
        tfirst = c["t_first"].fill_null(strategy="zero").to_numpy()
        tfirst = np.where((tfirst > tcall) & (tfirst < tcall + 600), tfirst, tcall + 5.0)
        ag = c["agent"].to_numpy()
        nmin = int((hi - lo) // 60) + 2
        if sigma > 0:
            z = np.empty(nmin)
            ph = np.exp(-1.0 / tau)
            z[0] = rng.normal()
            for k in range(1, nmin):
                z[k] = ph * z[k - 1] + np.sqrt(1 - ph ** 2) * rng.normal()
            f = np.exp(sigma * z - sigma ** 2 / 2)
        else:
            f = np.ones(nmin)
        room_msgs = {r: [] for r in set(rmap.values())}      # sorted (t) per room
        room_snd = {r: [] for r in set(rmap.values())}
        own = {a: [] for a in agents.tolist()}
        prev = {a: lo for a in agents.tolist()}
        ylast = {a: 0 for a in agents.tolist()}
        for k in range(len(tcall)):
            a = int(ag[k])
            r = rmap[a]
            t0, t1 = prev[a], tcall[k]
            lst = room_msgs[r]
            R = bisect.bisect_left(lst, t1) - bisect.bisect_left(lst, t0)
            ol = own[a]
            R -= bisect.bisect_left(ol, t1) - bisect.bisect_left(ol, t0)
            base = share.get(a, 0.0) * (1 - g) * (1 - rho)
            p = base * f[min(int((t1 - lo) // 60), nmin - 1)] + J * R + rho * ylast[a]
            y = rng.random() < min(max(p, 0.0), 1.0)
            ylast[a] = int(y)
            prev[a] = t1
            if y:
                talk_calls += 1
                m = 1 + rng.poisson(max(MBAR - 1, 0))
                for j in range(m):
                    tm = tfirst[k] + rng.uniform(0, 2.0)
                    bisect.insort(lst, tm)
                    bisect.insort(ol, tm)
                    rows_t.append(tm)
                    rows_d.append(d)
                    rows_a.append(a)
                    rows_r.append(r)
                    n_msgs += 1
                    readers_sum += (np.array(list(rmap.values())) == r).sum() - 1
    sim = pl.DataFrame({"t": np.array(rows_t, float), "day": np.array(rows_d, np.int16),
                        "agent": np.array(rows_a, np.int8), "room": np.array(rows_r, np.int8)}).sort("t")
    mb = n_msgs / max(talk_calls, 1)
    g_true = J * mb * (readers_sum / max(n_msgs, 1))
    return sim, g_true


def run_one(args):
    uid, world, rep, clock, exo = args
    L.CLOCK, L.EXO_RULE = clock, exo
    U = L.load_unit(uid)
    pars = WORLDS[world]
    sim, g_true = simulate(U, seed=10_000 * rep + list(WORLDS).index(world) * 101 + int(sum(map(ord, uid))), **pars)
    st = L.unit_stats(U, g=g_true, g_se=0.0, B=200, seed=rep, sim_msgs=sim, variants=False)
    st.update({"world": world, "rep": rep, "g_true": g_true, "n_sim_msgs": sim.height, "clock": clock, "exo": exo})
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--clock", default="percall")
    ap.add_argument("--exo", default="session10")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    jobs = [(u, w, r, a.clock, a.exo) for u in UNITS for w in WORLDS for r in range(a.reps)]
    with ProcessPoolExecutor(max_workers=min(a.workers, 2)) as ex:
        res = list(ex.map(run_one, jobs, chunksize=2))
    df = pl.DataFrame(res, infer_schema_length=None)
    out = L.OUT / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    tag = f"_{a.tag}" if a.tag else ""
    df.write_parquet(out / f"runs{tag}.parquet")
    summ = summarize(df)
    (out / f"summary{tag}.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


def summarize(df: pl.DataFrame) -> dict:
    S = {}
    T = L.T_STAR
    for w in WORLDS:
        x = df.filter(pl.col("world") == w)
        per = {}
        for u in UNITS:
            y = x.filter(pl.col("unit_id") == u)
            if y.height == 0:
                continue
            ph, lo, hi, pp = (y[f"phi_{T}"].to_numpy(), y[f"phi_{T}_lo"].to_numpy(), y[f"phi_{T}_hi"].to_numpy(),
                              y["phi_pred"].to_numpy())
            per[u] = {"g_true": float(np.median(y["g_true"])), "phi_med": float(np.median(ph)),
                      "pred_med": float(np.median(pp)), "rel_err_med": float(np.median(ph / pp - 1)),
                      "cover": float(np.mean((lo <= pp) & (pp <= hi))), "ci_incl_1": float(np.mean((lo <= 1) & (1 <= hi))),
                      "ci_width_med": float(np.median(hi - lo)),
                      "s_F_med": float(np.median(y["s_F"])), "s_F_pos_sig": float(np.mean(y["s_F_lo"].to_numpy() > 0)),
                      "phi_gt_1.2": float(np.mean(ph > 1.2)),
                      "rF_hi_below_2": float(np.mean(y["r_F_hi"].to_numpy() < 2)),
                      "phi_5": float(np.median(y["phi_5"])), "phi_30": float(np.median(y["phi_30"]))}
        S[w] = per
    return S


if __name__ == "__main__":
    main()
