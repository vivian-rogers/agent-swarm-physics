"""H51 scheme: phase-diagram axes and unfitted observables per goal period (and per sub-unit for the natives).

Builds data/processed/H51-one-dial-collapse/:
  axes_units.parquet          per non-holdout period unit: g_lag (H67), c_x / phi trimmed and raw (H86, activity),
                              N_active and pending k (H85), median call interval (H67), regime, n_days
  axes_periods.parquet        per non-holdout goal period: g_lag pool + SE and g_eq (H67 periods), c_x / phi (day-weighted
                              over units), log N, S_text (H54), f_sched (H38), call interval
  observables_periods.parquet per goal period: tau_settle (H48 bge/gte), cowork excess (H11 project/work), R_hat (H34 rule
                              on its ledger first-use tables; H34 table value as variant), loop rate (DQ5 statement_flags),
                              consensus time (H31)
  natives_units.parquet       per sub-unit of #36 and #51 (and #39-#41): R_hat, loop rate, H11 cowork rows where present
Every input row is non-holdout: the shared estimates writer refuses held-out rows, and this script also applies
infra/shared/common.holdout_mask to statement/idea rows and asserts that no held-out goal survives.

Usage: uv run python hypotheses/H51-one-dial-collapse/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra" / "shared"))
from common import REVISION, git_commit, holdout_mask, load_holdout  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H51-one-dial-collapse"
H67 = ROOT / "data/processed/H67-lagged-criticality-dial/results"
H86 = ROOT / "data/processed/H86-taylor-law-field-gauge/replication/gauge.parquet"
H54 = ROOT / "data/processed/H54-kickoff-quench-target/kickoffs.parquet"
H34 = ROOT / "data/processed/H34-idea-cascades/r1b"
HELD = set(load_holdout()["goal_periods_held_out"])


def pu_table() -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet")
    return pu.filter(~pl.col("holdout")).select("unit_id", "goal_no", "start", "end", "first_day", "last_day", "n_days",
                                               "n_agents", "regime", "days")


def est(h: str, stat: str, channel: str | None = None, method_has: str | None = None, method_not: str | None = None):
    e = pl.read_parquet(SH / "per_period_estimates.parquet").filter(
        (pl.col("hypothesis") == h) & (pl.col("statistic") == stat) & ~pl.col("holdout"))
    if channel is not None:
        e = e.filter(pl.col("channel") == channel)
    if method_has:
        e = e.filter(pl.col("method").str.contains(method_has, literal=True))
    if method_not:
        e = e.filter(~pl.col("method").str.contains(method_not, literal=True))
    return e.select("period_unit", "goal_no", "estimate", "ci_lo", "ci_hi", "n", "method")


def to_period(e: pl.DataFrame, pu: pl.DataFrame, name: str) -> pl.DataFrame:
    """Whole-period value per goal: a 'G<NN>' row or an unsplit unit row; else the day-weighted mean of sub-unit rows."""
    nunits = pu.group_by("goal_no").agg(pl.len().alias("k"))
    rows = []
    for g, sub in e.group_by("goal_no"):
        g = int(g[0])
        if g in HELD:
            continue
        keys = sub["period_unit"].to_list()
        whole = [k for k in keys if k == f"G{g:02d}" or k == f"G{g}"]
        k_g = nunits.filter(pl.col("goal_no") == g)["k"]
        if not whole and str(g) in keys and (k_g.len() and k_g[0] == 1):
            whole = [str(g)]
        if whole:
            r = sub.filter(pl.col("period_unit") == whole[0]).row(0, named=True)
            rows.append({"goal_no": g, name: r["estimate"], f"{name}_lo": r["ci_lo"], f"{name}_hi": r["ci_hi"],
                         f"{name}_src": "period"})
            continue
        su = sub.filter(~pl.col("period_unit").str.starts_with("local:")).join(
            pu.select("unit_id", "n_days"), left_on="period_unit", right_on="unit_id")
        if su.height:
            w = su["n_days"].to_numpy().astype(float)
            rows.append({"goal_no": g, name: float(np.sum(w * su["estimate"].to_numpy()) / w.sum()),
                         f"{name}_lo": None, f"{name}_hi": None, f"{name}_src": f"units({su.height})"})
    return pl.DataFrame(rows, schema={"goal_no": pl.Int64, name: pl.Float64, f"{name}_lo": pl.Float64,
                                      f"{name}_hi": pl.Float64, f"{name}_src": pl.String})


# ------------------------------------------------------------------------------------------------ axes
def axes_units(pu: pl.DataFrame) -> pl.DataFrame:
    u67 = pl.read_parquet(H67 / "units.parquet").select(
        "unit_id", pl.col("g").alias("g_lag"), pl.col("g_se").alias("g_lag_se"), pl.col("g_eq"),
        pl.col("J1").alias("J1"), "rbar", "med_call_s", pl.col("N").alias("N_calling"), "ok")
    g = pl.read_parquet(H86).filter(pl.col("channel") == "activity")
    gt = g.filter(pl.col("grid") == "trim").select("unit_id", pl.col("c_x").alias("c_x_trim"),
                                                  pl.col("c_x_lo").alias("c_x_trim_lo"), pl.col("c_x_hi").alias("c_x_trim_hi"),
                                                  pl.col("phi").alias("phi_trim"))
    gr = g.filter(pl.col("grid") == "raw").select("unit_id", pl.col("c_x").alias("c_x_raw"), pl.col("phi").alias("phi_raw"))
    n85 = est("H85", "active_population_N").select(pl.col("period_unit").alias("unit_id"), pl.col("estimate").alias("N_active"))
    k85 = est("H85", "pending_set_k_talk").select(pl.col("period_unit").alias("unit_id"), pl.col("estimate").alias("k_talk"))
    a = (pu.join(u67, on="unit_id", how="left").join(gt, on="unit_id", how="left").join(gr, on="unit_id", how="left")
         .join(n85, on="unit_id", how="left").join(k85, on="unit_id", how="left"))
    num = [c for c, t in a.schema.items() if t in (pl.Float64, pl.Float32)]
    return a.with_columns([pl.col(c).fill_nan(None) for c in num]).drop("days")  # NaN (e.g. H86 4b) -> null


def wmean(df: pl.DataFrame, col: str) -> pl.Expr:
    return (pl.col(col) * pl.col("n_days")).sum() / pl.when(pl.col(col).is_not_null()).then(pl.col("n_days")).otherwise(0).sum()


def axes_periods(au: pl.DataFrame, pu: pl.DataFrame) -> pl.DataFrame:
    p67 = pl.read_parquet(H67 / "periods.parquet").select(
        "goal_no", "regime", pl.col("g").alias("g_lag"), pl.col("g_lo").alias("g_lag_lo"), pl.col("g_hi").alias("g_lag_hi"),
        pl.col("g_se").alias("g_lag_se"), "g_eq", "g_h25_trim", "rbar", "g_named")
    agg = au.group_by("goal_no").agg(
        *[wmean(au, c).alias(c) for c in ("c_x_trim", "phi_trim", "c_x_raw", "phi_raw", "N_active", "k_talk", "med_call_s")],
        pl.col("n_days").sum().alias("n_days"), pl.col("unit_id").sort().alias("units"),
        pl.col("regime").mode().first().alias("regime_pu"))
    kick = pl.read_parquet(H54).filter(pl.col("room").is_null()).select(pl.col("goal_no").cast(pl.Int64), "S_text", "S_count")
    fs = to_period(est("H38", "f_scaffold", "activity", method_not="significant"), pu, "f_sched").select("goal_no", "f_sched")
    ap = (agg.with_columns(pl.col("goal_no").cast(pl.Int64)).join(p67, on="goal_no", how="left")
          .join(kick, on="goal_no", how="left").join(fs, on="goal_no", how="left"))
    ap = ap.with_columns(pl.coalesce("regime", "regime_pu").alias("regime"), pl.col("N_active").log().alias("logN")).drop("regime_pu")
    return ap.sort("goal_no")


# ------------------------------------------------------------------------------------------------ observables
def stmt_flags() -> pl.DataFrame:
    s = pl.read_parquet(SH / "embeddings/statements.parquet", columns=["kind", "agent", "t", "pt_date", "goal_no", "holdout"])
    f = pl.read_parquet(SH / "statement_flags.parquet", columns=["self_repeat", "self_repeat_both", "self_repeat_bge",
                                                                 "self_repeat_gte"])
    d = pl.concat([s, f], how="horizontal_extend").filter((pl.col("kind") == "chat") & ~pl.col("holdout") & pl.col("goal_no").is_not_null())
    m = np.array(holdout_mask(d["pt_date"].to_list(), d["goal_no"].to_list()))
    d = d.filter(pl.Series(~m))
    assert not set(d["goal_no"].unique().to_list()) & HELD
    return d


def loop_rates(d: pl.DataFrame, by: list[str]) -> pl.DataFrame:
    return d.group_by(by).agg(pl.len().alias("n_stmt"), pl.col("self_repeat").mean().alias("loop_rate"),
                              pl.col("self_repeat_both").mean().alias("loop_rate_both"),
                              pl.col("self_repeat_bge").mean().alias("loop_rate_bge"),
                              pl.col("self_repeat_gte").mean().alias("loop_rate_gte"))


def first_uses(goal: int) -> pl.DataFrame | None:
    f = H34 / f"G{goal:02d}" / "first_uses.parquet"
    if not f.exists():
        return None
    return pl.read_parquet(f, columns=["status", "parent", "t_us"])


def r_hat(fu: pl.DataFrame) -> tuple[float, int]:
    """H34 rule: first uses with status 1 and an agent parent / all first uses."""
    n = fu.height
    return (float(((fu["status"] == 1) & (fu["parent"] >= 0)).sum() / n) if n else np.nan), n


def project_frame(goal: int, days: list[str] | None = None, sources: str = "all", w_min: int = 30) -> pl.DataFrame:
    p = pl.read_parquet(SH / "project_states.parquet").filter(
        (pl.col("goal_no") == goal) & (pl.col("w_min") == w_min) & (pl.col("sources") == sources) & ~pl.col("holdout")
        & pl.col("project").is_not_null())
    if days is not None:
        p = p.filter(pl.col("pt_date").is_in(days))
    if p.height:
        m = np.array(holdout_mask(p["pt_date"].to_list(), p["goal_no"].to_list()))
        p = p.filter(pl.Series(~m))
    return p.select("pt_date", "win", "agent", "room", pl.col("project").cast(pl.String))


def _cowork_rate(day, pos, room, proj) -> float:
    """Share of agents (in blocks of >= 2 labelled agents) whose raw project is held by >= 1 block-mate."""
    key = (day.astype(np.int64) * 10000 + pos) * 100 + room
    df = pl.DataFrame({"b": key, "p": proj})
    bs = df.group_by("b").agg(pl.len().alias("nb"))
    bp = df.group_by("b", "p").agg(pl.len().alias("c"))
    bp = bp.join(bs, on="b").filter(pl.col("nb") >= 2)
    den = bs.filter(pl.col("nb") >= 2)["nb"].sum()
    return float(bp.filter(pl.col("c") >= 2)["c"].sum() / den) if den else np.nan


def herd_share(p: pl.DataFrame, nnull: int = 20, seed: int = 51) -> tuple[float, float, int]:
    """H11-style cowork excess (re-implemented): observed cowork rate minus the mean under a circular shift of each
    agent's within-day window sequence (room kept per agent-day). Blocks = (day, 30-min window, room)."""
    if p.height < 20:
        return np.nan, np.nan, p.height
    days = {d: i for i, d in enumerate(sorted(p["pt_date"].unique().to_list()))}
    day = np.array([days[d] for d in p["pt_date"].to_list()])
    win = p["win"].to_numpy().astype(np.int64)
    agent = p["agent"].to_numpy().astype(np.int64)
    room = p["room"].fill_null(0).to_numpy().astype(np.int64)
    proj = p["project"].to_numpy()
    lo = {d: win[day == d].min() for d in np.unique(day)}
    hi = {d: win[day == d].max() for d in np.unique(day)}
    obs = _cowork_rate(day, win, room, proj)
    rng = np.random.default_rng(seed)
    ad = agent * 1000 + day
    uad = np.unique(ad)
    idx = {k: np.flatnonzero(ad == k) for k in uad}
    nulls = []
    for _ in range(nnull):
        pos = win.copy()
        for k, m in idx.items():
            d = day[m[0]]
            L = hi[d] - lo[d] + 1
            pos[m] = lo[d] + (win[m] - lo[d] + rng.integers(0, L)) % L
        nulls.append(_cowork_rate(day, pos, room, proj))
    return obs - float(np.mean(nulls)), obs, p.height


def observables_periods(pu: pl.DataFrame, flags: pl.DataFrame) -> pl.DataFrame:
    goals = sorted(set(pu["goal_no"].to_list()))
    obs = pl.DataFrame({"goal_no": [int(g) for g in goals]}, schema={"goal_no": pl.Int64})
    parts = [
        to_period(est("H48", "tau_settle_S1_active_h", "content_bge_small"), pu, "tau_settle"),
        to_period(est("H48", "tau_settle_S1_active_h", "content_gte_modernbert"), pu, "tau_settle_gte"),
        to_period(est("H11", "cowork_excess", "project"), pu, "herd"),
        to_period(est("H11", "cowork_excess", "work"), pu, "herd_work"),
        to_period(est("H34", "branching_ratio_R", "ideas"), pu, "R_h34tab"),
        to_period(est("H31", "consensus_time_gradual_median_h", "project"), pu, "t_cons"),
    ]
    for p in parts:
        obs = obs.join(p, on="goal_no", how="left")
    rr = []
    for g in goals:
        fu = first_uses(int(g))
        if fu is not None:
            r, n = r_hat(fu)
            rr.append({"goal_no": int(g), "R_hat": r, "R_n": n})
    obs = obs.join(pl.DataFrame(rr), on="goal_no", how="left")
    hh = []
    for g in goals:
        ex, rate, n = herd_share(project_frame(int(g)))
        hh.append({"goal_no": int(g), "herd_own": ex, "herd_own_rate": rate, "herd_own_n": n})
    obs = obs.join(pl.DataFrame(hh), on="goal_no", how="left")
    lr =loop_rates(flags, ["goal_no"]).with_columns(pl.col("goal_no").cast(pl.Int64))
    obs = obs.join(lr, on="goal_no", how="left")
    assert not set(obs["goal_no"].to_list()) & HELD
    return obs.sort("goal_no")


def natives_units(pu: pl.DataFrame, flags: pl.DataFrame, au: pl.DataFrame) -> pl.DataFrame:
    rows = []
    sel = pu.filter(pl.col("goal_no").is_in([36, 39, 40, 41, 51]))
    fu_cache = {}
    for r in sel.iter_rows(named=True):
        g = int(r["goal_no"])
        if g not in fu_cache:
            fu_cache[g] = first_uses(g)
        fu = fu_cache[g]
        t0, t1 = r["start"], r["end"]
        out = {"unit_id": r["unit_id"], "goal_no": g, "start": t0, "end": t1}
        if fu is not None:
            us0 = int(t0.timestamp() * 1e6)
            us1 = int(t1.timestamp() * 1e6)
            sub = fu.filter((pl.col("t_us") >= us0) & (pl.col("t_us") < us1))
            out["R_hat"], out["R_n"] = r_hat(sub) if sub.height else (np.nan, 0)
        fl = flags.filter((pl.col("t") >= t0) & (pl.col("t") < t1))
        out["n_stmt"] = fl.height
        out["herd_own"], out["herd_own_rate"], out["herd_own_n"] = herd_share(project_frame(g, days=list(r["days"])))
        for c in ("self_repeat", "self_repeat_both", "self_repeat_bge", "self_repeat_gte"):
            out[c.replace("self_repeat", "loop_rate")] = float(fl[c].mean()) if fl.height else np.nan
        rows.append(out)
    nu = pl.DataFrame(rows)
    h11 = est("H11", "cowork_excess", "project").select(pl.col("period_unit").alias("unit_id"), pl.col("estimate").alias("herd"))
    nu = nu.join(h11, on="unit_id", how="left").join(
        au.select("unit_id", "g_lag", "g_lag_se", "c_x_trim", "phi_trim", "N_active", "k_talk", "n_days", "regime"),
        on="unit_id", how="left")
    return nu.sort("start")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pu = pu_table()
    assert not set(pu["goal_no"].to_list()) & HELD
    au = axes_units(pu)
    au.write_parquet(OUT / "axes_units.parquet")
    ap = axes_periods(au, pu)
    ap.write_parquet(OUT / "axes_periods.parquet")
    flags = stmt_flags()
    op = observables_periods(pu, flags)
    op.write_parquet(OUT / "observables_periods.parquet")
    nu = natives_units(pu, flags, au)
    nu.write_parquet(OUT / "natives_units.parquet")
    prov = {"built_by": "hypotheses/H51-one-dial-collapse/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["period_units", "per_period_estimates (H67, H86, H85, H38, H48, H11, H34, H31)",
                                   "statement_flags", "embeddings/statements"]},
                       {"source": "derived (read only)", "files": [
                           "data/processed/H67-lagged-criticality-dial/results/{units,periods}.parquet",
                           "data/processed/H86-taylor-law-field-gauge/replication/gauge.parquet",
                           "data/processed/H54-kickoff-quench-target/kickoffs.parquet",
                           "data/processed/H34-idea-cascades/r1b/G*/first_uses.parquet"]}],
            "params": {"holdout": "masked (estimates writer + holdout_mask + assert)", "loop_rate": "chat self_repeat (either model)",
                       "R_hat": "H34 rule on ledger first uses"},
            "built_at": dt.datetime.now(dt.UTC).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print("axes_units", au.height, "axes_periods", ap.height, "observables", op.height, "natives", nu.height)
    print("coverage:", {c: int(op[c].is_not_null().sum()) for c in ("tau_settle", "herd", "herd_own", "R_hat", "loop_rate", "t_cons")})
    print("axes coverage:", {c: int(ap[c].is_not_null().sum()) for c in ("g_lag", "c_x_trim", "phi_trim", "N_active", "S_text", "f_sched")})


if __name__ == "__main__":
    main()
