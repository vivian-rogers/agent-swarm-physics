"""H76 synthetic validation (axis F): a 5-state mean-field master equation sampled like the village.

States 0 absent, 1 work, 2 explore, 3 coord, 4 wait. Per-minute generator with
  - symmetric base rates and energies, plus a driven cycle work -> explore -> coord -> work (force F): housekeeping;
  - mid-day pauses (absent), mostly from `wait`;
  - day edges: most agents start/stop within 30 s of the schedule, 20% with an exponential lag (mean 15 min);
    each day starts from a boot mix (explore-heavy) that relaxes within minutes (a scheduler start transient);
  - a kickoff field lowering the energy of coord (and explore) by h exp(-t/tau), tau = 5 active h.
Windows (5 min) take the modal minute state; soft labels c*onehot + (1-c)*Dirichlet(0.5) with c from v3's
confidence distribution; absent is observed exactly. Truth = the same estimator on N = 3000 agents, hard labels.

  uv run python hypotheses/H76-excess-housekeeping-split/analysis/synthetic.py [--quick]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h76lib as L  # noqa: E402
import h76run as RN  # noqa: E402

OUT = L.OUTD / "synthetic"
TAU_MIN = 300.0
U0 = np.array([0.0, -1.0, 0.0, 0.0, 0.3])
BOOT = np.array([0.0, 0.1, 0.5, 0.3, 0.1])


def generator(h_t: float, F: float = 1.0, k: float = 0.05) -> np.ndarray:
    U = U0.copy()
    U[3] -= h_t
    U[2] -= 0.5 * h_t
    W = np.zeros((5, 5))
    for x in range(1, 5):
        for y in range(1, 5):
            if x != y:
                W[x, y] = k * np.exp((U[x] - U[y]) / 2)
    for x, y in ((1, 2), (2, 3), (3, 1)):
        W[x, y] *= np.exp(F / 2)
        W[y, x] *= np.exp(-F / 2)
    # pauses: active -> absent (mostly from wait), absent -> wait / work
    W[4, 0], W[1, 0], W[2, 0], W[3, 0] = 0.03, 0.003, 0.003, 0.003
    W[0, 4], W[0, 1] = 0.06, 0.04
    np.fill_diagonal(W, -W.sum(1))
    return W


def step_mats(h: float, n_min: int, tau: float = TAU_MIN) -> np.ndarray:
    """One-minute transition matrices for active minutes 0..n_min-1 since the kickoff (field decays)."""
    cache = {}
    out = np.empty((n_min, 5, 5))
    for t in range(n_min):
        ht = round(h * np.exp(-t / tau), 3)
        if ht not in cache:
            cache[ht] = expm(generator(ht))
        out[t] = cache[ht]
    return out


def simulate(N: int, n_days: int, day_min: int, h: float, rng: np.random.Generator, conf: np.ndarray | None,
             late_frac: float = 0.2, tau: float = TAU_MIN) -> tuple[dict, dict]:
    """Returns (soft-label days, hard-label days) from the same trajectories."""
    n_tot = n_days * day_min
    Pm = step_mats(h, n_tot, tau)
    cum = np.cumsum(Pm, axis=2)
    days, hard = {}, {}
    tglob = 0
    for d in range(n_days):
        late = rng.random(N) < late_frac
        st = np.where(late, rng.exponential(15, N), rng.uniform(0, 0.5, N))
        late2 = rng.random(N) < late_frac
        en = day_min - np.where(late2, rng.exponential(15, N), rng.uniform(0, 0.5, N))
        en = np.maximum(en, st + 10)
        st_m, en_m = np.floor(st).astype(int), np.minimum(np.ceil(en).astype(int), day_min)
        S = np.zeros((N, day_min), np.int8)
        cur = rng.choice(5, N, p=BOOT)
        for m in range(day_min):
            on = (m >= st_m) & (m < en_m)
            starting = m == st_m
            cur = np.where(starting, rng.choice(5, N, p=BOOT), cur)
            u = rng.random(N)
            nxt = (u[:, None] > cum[tglob + m][cur]).sum(1)
            nxt = np.minimum(nxt, 4)
            S[:, m] = np.where(on, cur, 0)
            cur = np.where(on, nxt, cur)
        tglob += day_min
        # grid starts at the first agent start, 5-min windows
        g0 = int(st_m.min())
        nw = (day_min - g0) // 5
        Wst = S[:, g0:g0 + nw * 5].reshape(N, nw, 5)
        span = np.zeros((N, nw), bool)
        for i in range(N):
            span[i] = (np.arange(nw) * 5 + g0 + 5 > st_m[i]) & (np.arange(nw) * 5 + g0 < en_m[i])
        lab = np.zeros((N, nw), np.int8)
        for i in range(N):
            for w in range(nw):
                lab[i, w] = np.bincount(Wst[i, w], minlength=5).argmax()
        H = np.zeros((N, nw, 5))
        H[np.arange(N)[:, None], np.arange(nw)[None, :], lab] = 1.0
        X = np.zeros((N, nw, 5))
        if conf is not None:
            c = rng.choice(conf, (N, nw))
            noise = rng.dirichlet(np.full(4, 0.5), (N, nw))
            X[:, :, 1:] = (1 - c)[..., None] * noise
            idx = np.nonzero(lab > 0)
            X[idx[0], idx[1], lab[idx]] += c[idx]
            X[lab == 0] = 0.0
            X[lab == 0, 0] = 1.0
        else:
            X = H
        days[f"d{d:02d}"] = {"agents": list(range(N)), "X": X, "span": span}
        hard[f"d{d:02d}"] = {"agents": list(range(N)), "X": H, "span": span}
    return days, hard


def run_one(N, n_days, day_min, h, seed, conf, R=20, late_frac=0.2, tau=TAU_MIN):
    rng = np.random.default_rng(seed)
    soft, hard = simulate(N, n_days, day_min, h, rng, conf, late_frac, tau)
    out = []
    for days in (soft, hard):
        bl = RN.build_blocks(days, "d00", rng, R=R)
        s = RN.stats(bl, days, "d00")
        s["edge_time_share"] = RN.edge_time_share(days, "d00")
        out.append(s)
    return out


KEYS = ["kick_share", "kick_ratio", "kick_rank", "kick_ex", "dstart_ex_median", "decay_tau", "decay_A", "edge_share",
        "edge_share_day_median", "trim_rm_ex", "trim_rm_hk", "trim_rm_steps", "hk_share", "hk_per_step",
        "ex_per_step_trim", "ex_per_step_untrim", "edge_time_share"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    conf = pl.read_parquet(L.SH / "behavior_states_v3.parquet", columns=["behavior_conf", "labeled"]).filter(
        pl.col("labeled"))["behavior_conf"].to_numpy()
    OUT.mkdir(parents=True, exist_ok=True)
    designs = [("N15_5x4h", 15, 5, 240, 30), ("N25_10x8h", 25, 10, 480, 12)]
    amps = [("null", 0.0, TAU_MIN), ("slow", 2.0, TAU_MIN), ("fast", 2.0, 30.0)]
    if a.quick:
        designs = [("N15_5x4h", 15, 5, 240, 3)]
    rows = []
    t0 = time.time()
    for name, N, nd, dm, reps in designs:
        for scen, h, tau in amps:
            pop, _ = run_one(3000, nd, dm, h, 999, None, R=5, late_frac=0.0, tau=tau)
            rows.append({"design": name, "h": scen, "rep": -1, "kind": "population", **{k: pop.get(k, np.nan) for k in KEYS}})
            for r in range(reps):
                s_soft, s_hard = run_one(N, nd, dm, h, 7919 * len(scen) + r + 17 * N, conf, tau=tau)
                rows.append({"design": name, "h": scen, "rep": r, "kind": "soft", **{k: s_soft.get(k, np.nan) for k in KEYS}})
                rows.append({"design": name, "h": scen, "rep": r, "kind": "hard", **{k: s_hard.get(k, np.nan) for k in KEYS}})
            print(name, scen, f"{time.time() - t0:.0f}s", flush=True)
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / ("synthetic_quick.parquet" if a.quick else "synthetic.parquet"))
    summ = []
    for (name, h), g in df.group_by(["design", "h"], maintain_order=True):
        pop = g.filter(pl.col("kind") == "population")
        row = {"design": name, "h": h, "reps": g.filter(pl.col("kind") == "soft").height}
        for k in KEYS:
            row[f"{k}_pop"] = pop[k][0]
            for kind in ("hard", "soft"):
                v = g.filter(pl.col("kind") == kind)[k].fill_nan(None).drop_nulls()
                row[f"{k}_{kind}"] = float(v.mean()) if v.len() else np.nan
                row[f"{k}_{kind}_sd"] = float(v.std()) if v.len() > 1 else np.nan
        est = g.filter(pl.col("kind") == "soft")
        kr = est["kick_ratio"].fill_nan(None).drop_nulls()
        row["P_ratio_ge2"] = float((kr >= 2).mean()) if kr.len() else np.nan
        ks = est["kick_share"].fill_nan(None).drop_nulls()
        row["P_share_ge03"] = float((ks >= 0.3).mean()) if ks.len() else np.nan
        row["P_kick_top"] = float((est["kick_rank"].fill_nan(None).drop_nulls() >= 1.0).mean())
        row["P_kick_top_and_share"] = float(((est["kick_rank"] >= 1.0) & (est["kick_share"] >= 0.3)).mean())
        summ.append(row)
    sm = pl.DataFrame(summ)
    sm.write_parquet(OUT / ("summary_quick.parquet" if a.quick else "summary.parquet"))
    for r in sm.iter_rows(named=True):
        print(f"--- {r['design']} h={r['h']} reps={r['reps']}  P(ratio>=2)={r['P_ratio_ge2']:.2f} P(share>=0.3)={r['P_share_ge03']:.2f} P(top)={r['P_kick_top']:.2f} P(top&share)={r['P_kick_top_and_share']:.2f}")
        for k in KEYS:
            print(f"  {k:24s} pop {r[k+'_pop']:+.4f}  hard {r[k+'_hard']:+.4f} ({r[k+'_hard_sd']:.4f})  soft {r[k+'_soft']:+.4f} ({r[k+'_soft_sd']:.4f})")


if __name__ == "__main__":
    main()
