"""H94 synthetic checks (axis F) on real unit skeletons: the real runs (consecutive same-repo quanta of an agent-day) keep
their agent, day, window and length; each run's repo is redrawn from a known world.
  S0  max-ent with margins only (P_1 row conditional)          -> D_1 at the persistence floor
  S1  max-ent with ownership, lambda_own = 3                   -> lambda_own-hat ~ 3, D_2 at the persistence floor
  S2  neutral Polya copying over the unit's K repos (BE)       -> kappa ~ 1
  S3  herding beyond neutral (weight (c+1)^1.5)                -> kappa > 1
  S4  planned teams (agents fixed to team repos)               -> kappa < 0.5
  uv run python hypotheses/H94-maxent-work-allocation/analysis/synthetic.py --unit 31a --unit 39 --unit 41 --unit 51d
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import h94lib as L  # noqa: E402

DATA = ROOT / "data/processed/H94-maxent-work-allocation"


def load_unit(unit: str) -> pl.DataFrame:
    g = int("".join(ch for ch in unit if ch.isdigit()))
    q = pl.read_parquet(DATA / f"G{g:02d}" / "quanta.parquet")
    return q.filter(pl.col("unit") == unit)


def runs_frame(q: pl.DataFrame) -> pl.DataFrame:
    q = q.sort("agent", "pt_date", "win", "repo").with_columns(
        (pl.col("repo") != pl.col("repo").shift(1).over("agent", "pt_date")).fill_null(True).cum_sum().over("agent", "pt_date").alias("run"))
    return q


def world_tables(q: pl.DataFrame, world: str, rng, labs=None) -> pl.DataFrame:
    t = L.unit_table(q, labs=labs)
    repos = t["repos"]
    ai = {a: k for k, a in enumerate(t["agents"])}
    qr = runs_frame(q)
    runs = qr.group_by("agent", "pt_date", "run", maintain_order=True).agg(pl.len().alias("L"), pl.col("win").min().alias("w0"))
    runs = runs.sort("pt_date", "w0", "agent")
    K = len(repos)
    if world in ("S0", "S1"):
        if world == "S0":
            mu, _ = L.fit_maxent(t["n"], [])
        else:  # lambda fixed at 3: refit margins only, with the own feature as an offset
            n = t["n"]
            off = 3.0 * t["own"]
            a = np.zeros(n.shape[0]); b = np.zeros(n.shape[1])
            for _ in range(2000):
                mu = np.exp(a[:, None] + b[None, :] + off)
                a += np.log(n.sum(1) / mu.sum(1))
                mu = np.exp(a[:, None] + b[None, :] + off)
                b += np.log(n.sum(0) / mu.sum(0))
            mu = np.exp(a[:, None] + b[None, :] + off)
        P = mu / mu.sum(1, keepdims=True)
        pick = [repos[rng.choice(K, p=P[ai[a]])] for a in runs["agent"].to_list()]
    elif world in ("S2", "S3"):
        ex = 1.0 if world == "S2" else 1.5
        c = np.zeros(K)
        pick = []
        for _L in runs["L"].to_list():
            w = (c + 1) ** ex
            j = rng.choice(K, p=w / w.sum())
            pick.append(repos[j])
            c[j] += 1  # Polya on work episodes (runs)
    else:  # S4 planned teams
        A = len(t["agents"])
        nt = max(2, min(K, A // 3))
        order = np.argsort(-t["n"].sum(0))[:nt]
        team = {a: repos[order[k % nt]] for k, a in enumerate(rng.permutation(t["agents"]))}
        pick = [team[a] for a in runs["agent"].to_list()]
    runs = runs.with_columns(pl.Series("new_repo", pick))
    q2 = qr.join(runs.select("agent", "pt_date", "run", "new_repo"), on=["agent", "pt_date", "run"])
    q2 = q2.with_columns(pl.col("new_repo").alias("repo")).drop("new_repo", "run")
    # recompute own / same_room / named for the new repo assignment (repo properties are unchanged)
    props = q.select("repo", "owner", "owner_period", "owner_room", "named").unique(subset="repo")
    q2 = q2.drop("owner", "owner_period", "owner_room", "named").join(props, on="repo", how="left")
    q2 = q2.with_columns((pl.col("owner") == pl.col("agent")).fill_null(False).alias("own"),
                         (pl.col("room_mode") == pl.col("owner_room")).fill_null(False).alias("same_room"))
    # keep the unit's repo set fixed: S2-S4 may leave some repos empty (dropped from the table)
    return q2


def run_unit(unit: str, reps: int, draws: int = 50) -> list[dict]:
    q = load_unit(unit)
    two = q["room_mode"].drop_nulls().n_unique() > 1
    labs = None
    out = []
    for world in ("S0", "S1", "S2", "S3", "S4"):
        for r in range(reps):
            rng = np.random.default_rng(1000 * r + ord(world[1]))
            q2 = world_tables(q, world, rng, labs)
            res = L.unit_analysis(q2, two, draws=draws, seed=r)
            out.append({"unit": unit, "world": world, "rep": r, "D1": res["D1"], "D2": res["D2"], "D3": res["D3"],
                        "floor1": res["floor1"], "pfloor1": res["pfloor1"], "pfloor1_95": res["pfloor1_95"],
                        "floor2": res["floor2"], "pfloor2": res["pfloor2"], "pfloor2_95": res["pfloor2_95"],
                        "lam_own": res["lam_own"], "lam_lo": res["lam_own_lo"], "lam_hi": res["lam_own_hi"],
                        "kappa": res["kappa"]["kappa"], "be_lo": (res["kappa"].get("be_band") or [None, None])[0],
                        "be_hi": (res["kappa"].get("be_band") or [None, None])[1],
                        "breadth_M2": res["sig_M2"]["breadth_ratio"], "reach_M2": res["sig_M2"]["reach_ratio_top3"],
                        "kappa_q": res["kappa_quanta"]["kappa"]})
        print(unit, world, flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", action="append")
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    (DATA / "synthetic").mkdir(parents=True, exist_ok=True)
    if not a.summary:
        rows = []
        for u in a.unit:
            rows += run_unit(u, a.reps)
        pl.DataFrame(rows).write_parquet(DATA / "synthetic" / "worlds.parquet")
    d = pl.read_parquet(DATA / "synthetic" / "worlds.parquet")
    s = d.group_by("unit", "world").agg(
        pl.len().alias("n"), pl.col("D1").median(), pl.col("pfloor1").median(), pl.col("floor1").median(),
        (pl.col("D1") <= pl.col("pfloor1_95")).mean().alias("D1_in_pfloor"),
        pl.col("D2").median(), pl.col("pfloor2").median(), (pl.col("D2") <= pl.col("pfloor2_95")).mean().alias("D2_in_pfloor"),
        pl.col("lam_own").median(), ((pl.col("lam_lo") <= 3) & (pl.col("lam_hi") >= 3)).mean().alias("lam_cover3"),
        pl.col("kappa").median(), pl.col("kappa").quantile(0.1).alias("kappa_p10"), pl.col("kappa").quantile(0.9).alias("kappa_p90"),
        pl.col("kappa_q").median(),
        pl.col("breadth_M2").median(), pl.col("reach_M2").median()).sort("unit", "world")
    s.write_parquet(DATA / "synthetic" / "summary.parquet")
    with pl.Config(tbl_rows=100, tbl_cols=20, tbl_width_chars=250, float_precision=3):
        print(s)
