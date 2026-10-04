"""H105 scheme: two-state goal spins. Codes and projections only (no text).

For each design (free -> assigned pairs, kickoff transitions, natives) stores the statements of its F and A segments
with agent, window (win30), day, segment, and the projection y = <z, g-hat> on the goal direction (both models; white
and style_resid_period variants), the projections on 50 fixed random unit directions orthogonal to g-hat (white, both
models), and decoy thresholds (90/95/98th percentiles of decoy-statement projections; decoys = non-holdout statements
of the same regime outside goal periods {A-1, A, A+1} and #23, 10,000-statement subsample, fixed seed).
Natives: G51 (own agent_goal directions), NE38 (Opus 5's new goal), G12 (uses the #11 -> #12a pair; phases in analysis).

Outputs in data/processed/H105-two-state-goal-order/: designs.parquet, stmt_<design>.parquet, proj_<design>.npz,
_provenance.json.
Usage: uv run python hypotheses/H105-two-state-goal-order/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask, REVISION  # noqa: E402
from embed_models import goal_vectors, load_whitener  # noqa: E402

S = ROOT / "data/processed/shared"
ED = S / "embeddings"
OUT = ROOT / "data/processed/H105-two-state-goal-order"
MODELS = ["bge_small", "gte_modernbert"]
VARIANTS = {"white": "statements_white32", "style": "statements_style_resid_period32"}
CC_AGENT = 19
EXCLUDE = {23}
N_PERP = 50
N_DECOY = 10000
PCTS = (90, 95, 98)
PAIRS = [(11, 12), (16, 17), (37, 38), (3, 4), (5, 6)]
NE38_T = dt.datetime(2026, 7, 29, 16, 51, tzinfo=dt.timezone.utc)


def unitv(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("row")
    ho = holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())
    st = st.with_columns(pl.Series("ho", ho)).filter(~pl.col("ho") & (pl.col("agent") != CC_AGENT)
                                                     & ~pl.col("goal_no").is_in(list(EXCLUDE))).drop("ho")
    st = st.filter(pl.col("win30").is_not_null())
    pu = pl.read_parquet(S / "period_units.parquet").sort("goal_no", "seq")
    goals = pl.read_parquet(ED / "goals.parquet")
    GV = {m: goal_vectors(m).astype(np.float64) for m in MODELS}
    W = {(m, r): load_whitener(r, 32, m) for m in MODELS for r in ("I", "II", "III")}
    Z = {(m, v): np.load(ED / f"{f}_{m}.npy", mmap_mode="r") for m in MODELS for v, f in VARIANTS.items()}
    rng = np.random.default_rng(20261004)
    days_of = st.group_by("goal_no").agg(pl.col("pt_date").unique().sort().alias("d"))
    dd = {r["goal_no"]: r["d"] for r in days_of.iter_rows(named=True)}
    reg_of = dict(st.group_by("goal_no").agg(pl.col("regime").first()).iter_rows())

    def gvec(gid, regime):
        return {m: unitv(W[(m, regime)](GV[m][gid][None, :])[0]) for m in MODELS}

    def ghat(goal_no, regime):
        g = goals.filter((pl.col("goal_no") == goal_no))
        gg = g.filter(pl.col("kind") == "goal")["gid"]; kk = g.filter(pl.col("kind") == "kickoff")["gid"]
        out = {}
        for m in MODELS:
            parts = []
            if len(gg):
                parts.append(unitv(W[(m, regime)](GV[m][gg[0]][None, :])[0]))
            if len(kk):
                parts.append(unitv(W[(m, regime)](GV[m][kk[0]][None, :])[0]))
            out[m] = unitv(np.sum(parts, axis=0))
        return out

    def perp_dirs(g):
        R = rng.normal(size=(N_PERP, 32))
        R = R - (R @ g)[:, None] * g[None, :]
        return R / np.linalg.norm(R, axis=1, keepdims=True)

    def decoys(regime, excl):
        dsub = st.filter((pl.col("regime") == regime) & ~pl.col("goal_no").is_in(list(excl)))
        rows = dsub["row"].to_numpy()
        if len(rows) > N_DECOY:
            rows = np.sort(rng.choice(rows, N_DECOY, replace=False))
        return rows

    designs, prov_designs = [], []

    def save(design, kind, sub: pl.DataFrame, dirs: dict, regime, A_goal, meta):
        """dirs: {name: {model: unit vector}}; the first is the goal direction 'goal'."""
        rows = sub["row"].to_numpy()
        drows = decoys(regime, {A_goal - 1, A_goal, A_goal + 1, 23})
        arr = {}
        thr = []
        for m in MODELS:
            for v in VARIANTS:
                Zs = np.asarray(Z[(m, v)][rows], dtype=np.float64)
                Zd = np.asarray(Z[(m, v)][drows], dtype=np.float64)
                for name, vec in dirs.items():
                    y = Zs @ vec[m]; yd = Zd @ vec[m]
                    arr[f"{name}|{m}|{v}"] = y.astype(np.float32)
                    thr.append(dict(design=design, dir=name, model=m, variant=v,
                                    **{f"q{p}": float(np.percentile(yd, p)) for p in PCTS}))
            if "goal" in dirs:
                P = perp_dirs(dirs["goal"][m])
                Zs = np.asarray(Z[(m, "white")][rows], dtype=np.float64)
                Zd = np.asarray(Z[(m, "white")][drows], dtype=np.float64)
                arr[f"perp|{m}|white"] = (Zs @ P.T).astype(np.float32)
                q = np.percentile(Zd @ P.T, 95, axis=0)
                arr[f"perp_q95|{m}|white"] = q.astype(np.float32)
        np.savez_compressed(OUT / f"proj_{design}.npz", **arr)
        sub.select("row", "agent", "win30", "pt_date", "goal_no", "seg", "t", "room", "kind").write_parquet(
            OUT / f"stmt_{design}.parquet", compression="zstd")
        designs.append(dict(design=design, kind=kind, regime=regime, A_goal=A_goal, n_stmt=sub.height, **meta))
        return thr

    thr_all = []
    # ------------------------------------------------------------ free -> assigned pairs
    for F, A in PAIRS:
        uA = pu.filter((pl.col("goal_no") == A)).row(0, named=True)
        A_days = [d for d in uA["days"] if d in dd.get(A, [])][1:]
        regime = reg_of[A]
        sub = st.filter(((pl.col("goal_no") == F) & pl.col("pt_date").is_in(dd[F]))
                        | ((pl.col("goal_no") == A) & pl.col("pt_date").is_in(A_days)))
        sub = sub.with_columns(pl.when(pl.col("goal_no") == F).then(pl.lit("F")).otherwise(pl.lit("A")).alias("seg"))
        thr_all += save(f"P{F:02d}_{A:02d}", "pair", sub, {"goal": ghat(A, regime)}, regime, A,
                        dict(F_goal=F, F_days=",".join(dd[F]), A_days=",".join(A_days), A_unit=uA["unit_id"]))
    # ------------------------------------------------------------ kickoff transitions
    for A in sorted(dd):
        F = A - 1
        if F not in dd or A in EXCLUDE or F in EXCLUDE or A < 3:
            continue
        if reg_of[A] != reg_of[F]:
            continue
        if goals.filter((pl.col("goal_no") == A) & (pl.col("kind") == "kickoff")).height == 0:
            continue
        uA = pu.filter(pl.col("goal_no") == A).row(0, named=True)
        A_days = [d for d in uA["days"] if d in dd[A]][1:]
        if len(A_days) < 2:
            continue
        uF = pu.filter(pl.col("goal_no") == F).sort("seq").row(-1, named=True)
        F_days = [d for d in uF["days"] if d in dd[F]][-5:]
        if not F_days:
            continue
        regime = reg_of[A]
        sub = st.filter(((pl.col("goal_no") == F) & pl.col("pt_date").is_in(F_days))
                        | ((pl.col("goal_no") == A) & pl.col("pt_date").is_in(A_days)))
        sub = sub.with_columns(pl.when(pl.col("goal_no") == F).then(pl.lit("F")).otherwise(pl.lit("A")).alias("seg"))
        thr_all += save(f"K{A:02d}", "kickoff", sub, {"goal": ghat(A, regime)}, regime, A,
                        dict(F_goal=F, F_days=",".join(F_days), A_days=",".join(A_days), A_unit=uA["unit_id"]))
    # ------------------------------------------------------------ native G51: own goals, head units 51a-51l
    head = pu.filter((pl.col("goal_no") == 51) & ~pl.col("holdout"))
    hdays = sorted({d for ds in head["days"].to_list() for d in ds})
    sub = st.filter((pl.col("goal_no") == 51) & pl.col("pt_date").is_in(hdays))
    unit_map = {d: r["unit_id"] for r in head.iter_rows(named=True) for d in r["days"]}
    sub = sub.with_columns(pl.col("pt_date").replace_strict(unit_map, default="?").alias("seg"))
    ag = goals.filter((pl.col("kind") == "agent_goal") & pl.col("valid_to").is_null())
    dirs = {f"agent_{r['agent']}": gvec(r["gid"], "III") for r in ag.iter_rows(named=True)}
    dirs["shared"] = ghat(51, "III")
    thr_all += save("G51", "native", sub, dirs, "III", 51, dict(F_goal=None, F_days="", A_days=",".join(hdays), A_unit="51a-51l"))
    # ------------------------------------------------------------ native NE38: 07-24 .. 08-04
    sub = st.filter((pl.col("goal_no") == 51) & pl.col("pt_date").is_between(pl.lit("2026-07-24"), pl.lit("2026-08-04")))
    sub = sub.with_columns(pl.when(pl.col("t") < NE38_T).then(pl.lit("pre")).otherwise(pl.lit("post")).alias("seg"))
    thr_all += save("NE38", "native", sub, dirs, "III", 51, dict(F_goal=None, F_days="", A_days="2026-07-24..2026-08-04",
                                                                  A_unit="51e/51f"))

    pl.DataFrame(designs).write_parquet(OUT / "designs.parquet")
    pl.DataFrame(thr_all).write_parquet(OUT / "thresholds.parquet")
    prov = {"built_by": "hypotheses/H105-two-state-goal-order/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements", "statements_white32_*", "statements_style_resid_period32_*",
                                   "shared/embeddings/goals", "goal_vectors*", "whitening*", "shared/period_units"]}],
            "params": {"exclude_goals": sorted(EXCLUDE), "cc_agent": CC_AGENT, "n_perp": N_PERP, "n_decoy": N_DECOY,
                       "percentiles": PCTS, "pairs": PAIRS, "ne38_t": NE38_T.isoformat(), "seed": 20261004},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(pl.DataFrame(designs).select("design", "kind", "regime", "n_stmt", "A_unit"))


if __name__ == "__main__":
    main()
