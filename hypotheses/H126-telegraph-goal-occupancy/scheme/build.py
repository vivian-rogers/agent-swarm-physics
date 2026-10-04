"""H126 scheme: per-statement on-goal labels on each agent's call clock. Codes only (no text).

For every eligible design it stores the statements (agent, time, call index c on the agent's ledger-call clock, gap in
calls and in wall minutes, 30-min window, PT date, segment) and the on-goal label b = 1[<z, g-hat> > theta] for three
instrument variants: bge_small white32 (primary), gte_modernbert white32, bge_small style_resid_period32.

Designs (card "Data scheme"):
  U<unit>   every non-holdout unit of an assigned goal period (period_affordances.mode != F), excluding #23 and #51;
  K<g>      kickoff transitions: F = last <= 5 active days of g-1, A = first unit of g (all days), both along g-hat_g;
  N12       #12a/#12b with the DQ6 debate windows (pre/deb = debate on) as a per-statement flag;
  N51       #51 head units 51a-51l, each agent along its own agent_goal direction (own threshold);
  NE38      agent 40 (Claude Opus 5) 2026-07-24 -> 08-04 along its 07-29 goal direction, split at 16:51 UTC.
g-hat = unit(unit(W goal) + unit(W kickoff)) in each model's regime basis (H105's construction, re-implemented here).
Decoy threshold = 95th percentile of <z, g-hat> over 10,000 non-holdout same-regime statements outside goals
{g-1, g, g+1} and #23 (seed 20261004). Dedupe flag = statement_flags.self_repeat_both.

Outputs in data/processed/H126-telegraph-goal-occupancy/: stmts.parquet, designs.parquet, thresholds.parquet,
_provenance.json.
Usage: uv run python hypotheses/H126-telegraph-goal-occupancy/scheme/build.py
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
from common import REVISION, git_commit, holdout_mask, load_holdout  # noqa: E402
from embed_models import goal_vectors, load_whitener  # noqa: E402

S = ROOT / "data/processed/shared"
ED = S / "embeddings"
OUT = ROOT / "data/processed/H126-telegraph-goal-occupancy"
CC_AGENT = 19
EXCLUDE_GOALS = {23}
N_DECOY = 10000
SEED = 20261004
VARS = {"bge": ("bge_small", "statements_white32"), "gte": ("gte_modernbert", "statements_white32"),
        "sty": ("bge_small", "statements_style_resid_period32")}
MIN_STMT_UNIT = 30
NE38_AGENT = 40
NE38_T = dt.datetime(2026, 7, 29, 16, 51, tzinfo=dt.timezone.utc)


def unitv(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def main(allow_holdout: bool = False, target_goals=None, out_dir: Path | None = None, natives: bool = True):
    """Default: non-holdout exploration build. allow_holdout=True is for the frozen confirm script only: it builds the
    U designs of `target_goals` (held-out rows of those goals admitted) into `out_dir` (must be a confirm folder, never
    the exploration folder). Decoys and thresholds always come from non-holdout statements (same instrument)."""
    out = OUT if out_dir is None else Path(out_dir)
    if allow_holdout:
        assert out_dir is not None and "confirm" in str(out_dir), "held-out builds go to a confirm folder only"
        assert target_goals, "held-out builds need explicit target goals"
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    st_all = pl.read_parquet(ED / "statements.parquet").with_row_index("row")
    ho = holdout_mask(st_all["pt_date"].to_list(), st_all["goal_no"].to_list())
    st_all = st_all.with_columns((pl.Series("ho", ho) | pl.col("holdout")).alias("ho"))
    st_all = st_all.filter((pl.col("agent") != CC_AGENT) & ~pl.col("goal_no").is_in(list(EXCLUDE_GOALS)))
    st = st_all.filter(~pl.col("ho")).drop("ho")
    # confirm path: the target goals plus each target's previous goal (the kickoff designs' F segment)
    st_t = (st_all.filter(pl.col("goal_no").is_in(sorted(set(target_goals) | {g - 1 for g in target_goals}))).drop("ho")
            if allow_holdout else None)
    fl = pl.read_parquet(S / "statement_flags.parquet").select(pl.col("srow").cast(pl.UInt32).alias("row"),
                                                               pl.col("self_repeat_both").alias("dup"))

    def prep(x):
        x = x.filter(pl.col("win30").is_not_null())
        return x.join(fl, on="row", how="left").with_columns(pl.col("dup").fill_null(False))
    st = prep(st)
    decoy_pool = st   # decoys: non-holdout only, always
    if allow_holdout:
        st = prep(st_t)
    # ---------------------------------------------------------------- call clock
    cw = (pl.scan_parquet(S / "call_windows.parquet").select("agent", "t_call").collect()
          .sort("agent", "t_call"))
    calls = {int(a): g["t_call"].dt.epoch("us").to_numpy() for (a,), g in cw.group_by(["agent"], maintain_order=True)}
    t_us = st["t"].dt.epoch("us").to_numpy()  # noqa
    ag = st["agent"].to_numpy()
    cidx = np.full(st.height, -1, np.int64)
    for a in np.unique(ag):
        sel = np.flatnonzero(ag == a)
        c = calls.get(int(a))
        if c is not None:
            cidx[sel] = np.searchsorted(c, t_us[sel], side="left")
    st = st.with_columns(pl.Series("c", cidx)).filter(pl.col("c") >= 0)

    pu = pl.read_parquet(S / "period_units.parquet").sort("goal_no", "seq")
    pa = pl.read_parquet(S / "period_affordances.parquet").select("unit_id", "mode")
    pu = pu.join(pa, on="unit_id", how="left")
    held = set(load_holdout()["goal_periods_held_out"])
    goals = pl.read_parquet(ED / "goals.parquet")
    GV = {m: goal_vectors(m).astype(np.float64) for m in ("bge_small", "gte_modernbert")}
    W = {(m, r): load_whitener(r, 32, m) for m in ("bge_small", "gte_modernbert") for r in ("I", "II", "III")}
    Z = {v: np.load(ED / f"{f}_{m}.npy", mmap_mode="r") for v, (m, f) in VARS.items()}
    reg_of = dict(st.group_by("goal_no").agg(pl.col("regime").first()).iter_rows())
    days_of = {g: sorted(d) for g, d in st.group_by("goal_no").agg(pl.col("pt_date").unique()).iter_rows()}

    def wvec(gid, regime, m):
        return unitv(W[(m, regime)](GV[m][gid][None, :])[0])

    def ghat(goal_no, regime):
        g = goals.filter(pl.col("goal_no") == goal_no)
        gg = g.filter(pl.col("kind") == "goal")["gid"]
        kk = g.filter(pl.col("kind") == "kickoff")["gid"]
        if len(kk) == 0:
            return None
        out = {}
        for m in ("bge_small", "gte_modernbert"):
            parts = [wvec(kk[0], regime, m)]
            if len(gg):
                parts.append(wvec(gg[0], regime, m))
            out[m] = unitv(np.sum(parts, axis=0))
        return out

    decoy_cache = {}

    def decoys(regime, g):
        key = (regime, g)
        if key not in decoy_cache:
            excl = {g - 1, g, g + 1, 23}
            rows = decoy_pool.filter((pl.col("regime") == regime) & ~pl.col("goal_no").is_in(list(excl)))["row"].to_numpy()
            if len(rows) > N_DECOY:
                rows = np.sort(rng.choice(rows, N_DECOY, replace=False))
            decoy_cache[key] = rows
        return decoy_cache[key]

    def label(rows, vec, regime, g):
        """vec: {model: unit vector}; returns {variant: (labels, theta)}."""
        drows = decoys(regime, g)
        out = {}
        for v, (m, _) in VARS.items():
            y = np.asarray(Z[v][rows], dtype=np.float64) @ vec[m]
            yd = np.asarray(Z[v][drows], dtype=np.float64) @ vec[m]
            th = float(np.percentile(yd, 95))
            out[v] = ((y > th).astype(np.int8), th)
        return out

    frames, designs, thr = [], [], []

    def add(design, kind, sub: pl.DataFrame, vec, regime, g, meta, seg_col="seg"):
        if sub.height == 0:
            return
        rows = sub["row"].to_numpy()
        lab = label(rows, vec, regime, g)
        sub = sub.with_columns([pl.Series(f"b_{v}", lab[v][0]) for v in VARS]).with_columns(pl.lit(design).alias("design"))
        frames.append(sub)
        designs.append(dict(design=design, kind=kind, regime=regime, goal_no=g, n_stmt=sub.height, **meta))
        for v in VARS:
            thr.append(dict(design=design, variant=v, theta=lab[v][1]))

    base_cols = ["row", "agent", "t", "pt_date", "goal_no", "regime", "kind", "win30", "c", "dup"]
    # ---------------------------------------------------------------- U: assigned units
    for r in pu.iter_rows(named=True):
        g = int(r["goal_no"])
        if allow_holdout:
            if g not in set(target_goals) or g == 51 or r["mode"] in (None, "F"):
                continue
        elif r["holdout"] or g in held or g in EXCLUDE_GOALS or g == 51 or r["mode"] in (None, "F"):
            continue
        regime = reg_of.get(g)
        vec = ghat(g, regime) if regime else None
        if vec is None:
            continue
        sub = st.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(r["days"])).select(base_cols)
        sub = sub.with_columns(pl.lit("A").alias("seg"), pl.lit(r["unit_id"]).alias("unit"))
        add(f"U{r['unit_id']}", "unit", sub, vec, regime, g, dict(unit=r["unit_id"], mode=r["mode"]))
    # ---------------------------------------------------------------- K: kickoff transitions
    k_goals = sorted(days_of) if natives else (sorted(set(target_goals)) if allow_holdout else [])
    for g in k_goals:
        F = g - 1
        if F not in days_of or g in EXCLUDE_GOALS or F in EXCLUDE_GOALS or g < 3 or g == 51:
            continue
        if not allow_holdout and (g in held or F in held):
            continue
        if reg_of[g] != reg_of[F]:
            continue
        vec = ghat(g, reg_of[g])
        if vec is None:
            continue
        hk = pl.lit(True) if allow_holdout else ~pl.col("holdout")
        uA = pu.filter((pl.col("goal_no") == g) & hk).sort("seq")
        uF = pu.filter((pl.col("goal_no") == F) & hk).sort("seq")
        if uA.height == 0 or uF.height == 0:
            continue
        A_days = [d for d in uA.row(0, named=True)["days"] if d in days_of[g]]
        F_days = [d for d in uF.row(-1, named=True)["days"] if d in days_of[F]][-5:]
        if len(A_days) < 2 or not F_days:
            continue
        sub = st.filter(((pl.col("goal_no") == F) & pl.col("pt_date").is_in(F_days))
                        | ((pl.col("goal_no") == g) & pl.col("pt_date").is_in(A_days))).select(base_cols)
        sub = sub.with_columns(pl.when(pl.col("goal_no") == F).then(pl.lit("F")).otherwise(pl.lit("A")).alias("seg"),
                               pl.lit(f"K{g:02d}").alias("unit"))
        add(f"K{g:02d}", "kickoff", sub, vec, reg_of[g], g,
            dict(unit=uA.row(0, named=True)["unit_id"], mode=uA.row(0, named=True)["mode"], F_goal=F))
    # ---------------------------------------------------------------- N12: debate windows flag
    gt = pl.read_parquet(S / "ground_truth_labels.parquet").filter(pl.col("preferred") & ~pl.col("holdout")
                                                                   & (pl.col("goal_no") == 12)
                                                                   & (pl.col("label_kind") == "phase"))
    on_w = gt.filter(pl.col("value").is_in(["pre", "deb"])).select("t_valid_from", "t_valid_to")
    vec12 = ghat(12, "I")
    for uid in (("12a", "12b") if natives else ()):
        r = pu.filter(pl.col("unit_id") == uid)
        if r.height == 0:
            continue
        sub = st.filter((pl.col("goal_no") == 12) & pl.col("pt_date").is_in(r["days"][0])).select(base_cols)
        tt = sub["t"].dt.epoch("us").to_numpy()
        flag = np.zeros(len(tt), bool)
        for a, b in zip(on_w["t_valid_from"].dt.epoch("us").to_numpy(), on_w["t_valid_to"].dt.epoch("us").to_numpy()):
            flag |= (tt >= a) & (tt < b)
        sub = sub.with_columns(pl.Series("seg", np.where(flag, "D", "O")), pl.lit(uid).alias("unit"))
        add(f"N12_{uid}", "native_g12", sub, vec12, "I", 12, dict(unit=uid, mode="M"))
    # ---------------------------------------------------------------- N51: own goals
    head = pu.filter((pl.col("goal_no") == 51) & ~pl.col("holdout")).sort("seq")
    ag_goals = goals.filter((pl.col("kind") == "agent_goal") & (pl.col("goal_no") == 51) & pl.col("valid_to").is_null())
    for r in (head.iter_rows(named=True) if natives else []):
        sub0 = st.filter((pl.col("goal_no") == 51) & pl.col("pt_date").is_in(r["days"])).select(base_cols)
        for gr in ag_goals.iter_rows(named=True):
            a = int(gr["agent"])
            sub = sub0.filter((pl.col("agent") == a) & (pl.col("pt_date") >= gr["valid_from"]))
            if sub.height < MIN_STMT_UNIT:
                continue
            vec = {m: wvec(gr["gid"], "III", m) for m in ("bge_small", "gte_modernbert")}
            sub = sub.with_columns(pl.lit("A").alias("seg"), pl.lit(r["unit_id"]).alias("unit"))
            add(f"N51_{r['unit_id']}_{a}", "native_g51", sub, vec, "III", 51, dict(unit=r["unit_id"], mode="I/K", agent=a))
    # ---------------------------------------------------------------- NE38
    gr = ag_goals.filter(pl.col("agent") == NE38_AGENT).row(0, named=True)
    vec = {m: wvec(gr["gid"], "III", m) for m in ("bge_small", "gte_modernbert")}
    sub = (st if natives else st.head(0)).filter((pl.col("agent") == NE38_AGENT) & pl.col("pt_date").is_between(pl.lit("2026-07-24"), pl.lit("2026-08-04"))
                    ).select(base_cols)
    sub = sub.with_columns(pl.when(pl.col("t") < NE38_T).then(pl.lit("F")).otherwise(pl.lit("A")).alias("seg"),
                           pl.lit("NE38").alias("unit"))
    add("NE38", "native_ne38", sub, vec, "III", 51, dict(unit="51e/51f", mode="I/K", agent=NE38_AGENT))

    df = pl.concat(frames, how="diagonal_relaxed").sort("design", "agent", "t")
    df = df.with_columns(
        (pl.col("c") - pl.col("c").shift(1).over("design", "agent")).alias("dc"),
        ((pl.col("t") - pl.col("t").shift(1).over("design", "agent")).dt.total_seconds() / 60.0).alias("dmin"))
    df.write_parquet(out / "stmts.parquet", compression="zstd")
    pl.DataFrame(designs).write_parquet(out / "designs.parquet")
    pl.DataFrame(thr).write_parquet(out / "thresholds.parquet")
    prov = {"built_by": "hypotheses/H126-telegraph-goal-occupancy/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements", "statements_white32_*", "statements_style_resid_period32_bge_small",
                                   "shared/embeddings/goals", "goal_vectors*", "whitening_*", "shared/statement_flags",
                                   "shared/call_windows", "shared/period_units", "shared/period_affordances",
                                   "shared/ground_truth_labels"]}],
            "params": {"exclude_goals": sorted(EXCLUDE_GOALS), "cc_agent": CC_AGENT, "n_decoy": N_DECOY, "seed": SEED,
                       "threshold_pct": 95, "variants": {k: list(v) for k, v in VARS.items()},
                       "ne38": [NE38_AGENT, NE38_T.isoformat()]},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov["params"]["allow_holdout"] = bool(allow_holdout)
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))
    if not allow_holdout:
        print(pl.DataFrame(designs).group_by("kind").agg(pl.len(), pl.col("n_stmt").sum()))


if __name__ == "__main__":
    main()
