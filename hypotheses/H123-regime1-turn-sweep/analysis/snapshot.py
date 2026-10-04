"""H123 O2: model-01 snapshot sufficiency rho_2 = I_2 / I_N on 1-min spins, size-matched N = 4 agent subsets,
regime-I vs regime-III non-holdout units (>= 2 days). Pairwise max-ent by iterative proportional fitting on 16 states.

Output: data/processed/H123-regime1-turn-sweep/results/snapshot.parquet
Usage: uv run python hypotheses/H123-regime1-turn-sweep/analysis/snapshot.py
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h123lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = L.ROOT / "data/processed/shared"
STATES = np.array(list(itertools.product([0, 1], repeat=4)))


def H(p):
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def pairwise_maxent(p, iters=300):
    q = np.full(16, 1 / 16)
    cons = []
    for i in range(4):
        cons.append(STATES[:, i] == 1)
    for i, j in itertools.combinations(range(4), 2):
        cons.append((STATES[:, i] == 1) & (STATES[:, j] == 1))
    for _ in range(iters):
        for m in cons:
            t, s = p[m].sum(), q[m].sum()
            if 0 < s < 1 and 0 < t < 1:
                q[m] *= t / s
                q[~m] *= (1 - t) / (1 - s)
    return q / q.sum()


def rho2(X):
    """X: n x 4 binary. Returns (I_N, I_2, rho2, n)."""
    idx = X @ np.array([8, 4, 2, 1])
    p = np.bincount(idx, minlength=16) / len(idx)
    hs = sum(H(np.array([1 - X[:, i].mean(), X[:, i].mean()])) for i in range(4))
    IN = hs - H(p)
    I2 = hs - H(pairwise_maxent(p))
    return IN, I2, (I2 / IN if IN > 0 else np.nan), len(idx)


def main():
    pu = pl.read_parquet(SH / "period_units.parquet").filter((~pl.col("holdout")) & (pl.col("n_days") >= 2)
                                                             & pl.col("regime").is_in(["I", "III"]))
    roster = pl.read_parquet(SH / "roster.parquet")
    cc = set(roster.filter(pl.col("claude_code"))["agent"].to_list())
    rng = np.random.default_rng(4)
    rows = []
    ab = pl.scan_parquet(SH / "activity_bins_fixed.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "goal_no")
    for u in pu.iter_rows(named=True):
        days = u["days"]
        gm = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
        days = [d for d, h in zip(days, holdout_mask(days, [gm.get(d, u["goal_no"]) for d in days])) if not h]
        A = ab.filter(pl.col("pt_date").is_in(days)).select("pt_date", "minute", "agent", "talk", "state").collect()
        A = A.filter(~pl.col("agent").is_in(list(cc)))
        agents = sorted(A.filter(pl.col("state") >= 2)["agent"].unique().to_list())
        if len(agents) < 4:
            continue
        per_day = []
        for d in days:
            x = A.filter(pl.col("pt_date") == d)
            if x.height == 0:
                continue
            T = int(x["minute"].max()) + 1
            st = np.zeros((T, len(agents)), np.int8)
            tk = np.zeros((T, len(agents)), np.int8)
            amap = {a: i for i, a in enumerate(agents)}
            xx = x.filter(pl.col("agent").is_in(agents))
            ai = np.array([amap[a] for a in xx["agent"].to_list()])
            st[xx["minute"].to_numpy(), ai] = xx["state"].to_numpy()
            tk[xx["minute"].to_numpy(), ai] = (xx["talk"].to_numpy() > 0)
            rec = st >= 2
            span = np.zeros_like(rec)
            for i in range(len(agents)):
                w = np.flatnonzero(rec[:, i])
                if len(w):
                    span[w[0]:w[-1] + 1, i] = True
            per_day.append((st, tk, span))
        combos = list(itertools.combinations(range(len(agents)), 4))
        pick = combos if len(combos) <= 20 else [combos[i] for i in rng.choice(len(combos), 20, replace=False)]
        for ch in ("activity", "talk"):
            vals = []
            for c in pick:
                c = list(c)
                Xs = []
                for st, tk, span in per_day:
                    m = span[:, c].all(1)
                    if m.sum() == 0:
                        continue
                    Xs.append(((st[m][:, c] >= 3) if ch == "activity" else (tk[m][:, c] > 0)).astype(int))
                if not Xs:
                    continue
                X = np.vstack(Xs)
                if len(X) < 200:
                    continue
                IN, I2, r, n = rho2(X)
                bias = 11 / (2 * n * np.log(2))
                if IN > 5 * bias:
                    vals.append(r)
            if vals:
                rows.append({"unit": u["unit_id"], "goal_no": u["goal_no"], "regime": u["regime"], "channel": ch,
                             "rho2_med": float(np.median(vals)), "rho2_q25": float(np.quantile(vals, 0.25)),
                             "rho2_q75": float(np.quantile(vals, 0.75)), "n_subsets": len(vals),
                             "n_agents": len(agents)})
                print(rows[-1], flush=True)
    df = pl.DataFrame(rows)
    df.write_parquet(L.OUT / "results/snapshot.parquet")
    print(df.group_by("regime", "channel").agg(pl.col("rho2_med").median().alias("median"), pl.len()))


if __name__ == "__main__":
    main()
