"""Whole-period predictors per block (the forecast inputs): spectral gaps of the seen-weighted exposure graph,
time-respecting DeGroot gap, reading rate, herding-wave time, voter time on the real schedule, N.

  uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/predictors.py
Writes data/processed/H31-consensus-time-spectral-gap/predictors_period.parquet. Uses no outcome (no states,
no alignment)."""
from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h31lib as L  # noqa: E402


def voter_time(S, R=40, n_starts=8, seed=0, alpha=1.0):
    """Voter conditional time (h) from one seed to 50% on the real schedule (copy at every reading turn)."""
    rng = np.random.default_rng(seed)
    starts = rng.uniform(S.a0, S.a0 + 0.5 * (S.a1 - S.a0), n_starts)
    out = []
    for st in starts:
        grid = np.array([st + 3600 * 200])            # no grid needed; just t50
        _, t50 = L.simulate_states(S, "V", {"alpha": alpha}, st, R, rng, grid, max_cycles=6)
        out.extend(t50[np.isfinite(t50)].tolist())
    return float(np.median(out)) if out else np.nan, len(out)


def block_predictors(P, b, a0=None, a1=None, keep=None, with_voter=True, seed=0):
    S = L.make_schedule(P, b, a0, a1, keep=keep)
    if S is None:
        return None
    W = S.W
    u = L.reading_rate(S)
    bw = P["block_windows"].filter(pl.col("room") == b)
    if a0 is not None:
        bw = bw.filter((pl.col("act_mid") >= a0) & (pl.col("act_mid") < a1))
    nb = bw.group_by("day", "win").agg(pl.col("agent").n_unique().alias("n"))["n"]
    d = dict(N_sched=S.N, N_b=float(nb.median()) if len(nb) else np.nan, T_h=S.T_h, n_msgs=len(S.msg_t),
             n_upd=len(S.upd_t), msg_rate=len(S.msg_t) / max(S.T_h, 1e-9), u=u,
             l2_sym=L.lam2_sym(W), l2_dir=L.lam2_dir(W), l2_bin=L.lam2_bin(W), ul2_rw=u * L.lam2_rw(W),
             g_tr=L.gamma_tr(S, seed=seed), tau_wave=L.tau_wave(S, seed=seed),
             l2_ment=L.lam2_sym(L.mention_W(P, S)))
    if with_voter:
        d["tau_V"], d["n_V"] = voter_time(S, seed=seed)
    return d


def period_job(g):
    P = L.load_period(g)
    rows = []
    for b in L.blocks_of(P):
        for variant, keep in (("all", None), ("core", L.core_agents(P, b))):
            d = block_predictors(P, b, keep=keep, with_voter=(variant == "all"))
            if d is None:
                continue
            rows.append(dict(goal_no=g, room=b, variant=variant, regime=str(P["days"]["regime"][0]), **d))
    return rows


def main():
    goals = sorted(int(p.name[1:]) for p in L.DATA.glob("G*") if p.is_dir())
    rows = []
    with ProcessPoolExecutor(max_workers=2) as ex:
        for r in ex.map(period_job, goals):
            rows.extend(r)
    df = pl.DataFrame(rows)
    df.write_parquet(L.DATA / "predictors_period.parquet", compression="zstd")
    with pl.Config(tbl_rows=100, tbl_cols=30, tbl_width_chars=250):
        print(df.filter(pl.col("variant") == "all").select(
            "goal_no", "room", "N_b", "N_sched", "T_h", "msg_rate", "u", "l2_sym", "l2_dir", "l2_bin", "ul2_rw", "g_tr",
            "tau_wave", "l2_ment", "tau_V").with_columns(pl.col(pl.Float64).round(3)))


if __name__ == "__main__":
    main()
