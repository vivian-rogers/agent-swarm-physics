"""H75 scheme: DQ4 work commits -> per-period repo-allocation ensembles in active hours since the kickoff.

  uv run python hypotheses/H75-reallocation-speed-limit/scheme/build.py      (writes data/processed/H75-.../<unit>/)

Library use (analysis/run.py): `clock(goal)`, `commits()`, `ensemble(goal, variant, H)`, `call_rates(...)`.
Holdout: every commit, call and calendar day passes `holdout_mask`; a pre-kickoff window inside the holdout is refused.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import h75lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import git_commit, holdout_mask, REVISION  # noqa: E402

SLACK = dt.timedelta(minutes=15)
REPLICATION = {39: "pre", 40: "pre", 41: "pre", 51: "null"}


def calendar() -> pl.DataFrame:
    c = pl.read_parquet(L.SH / "calendar.parquet").sort("pt_date")
    hm = holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())
    return c.with_columns(pl.Series("ho", hm))


def kickoff(goal: int) -> dt.datetime:
    g = pl.read_parquet(L.SH / "embeddings/goals.parquet").filter((pl.col("goal_no") == goal) & (pl.col("kind") == "kickoff"))
    return g["win_start"][0]


def clock(goal: int, pre_days: int = 2, days: list[str] | None = None, allow_holdout: bool = False) -> pl.DataFrame:
    """Day table with active-hour offsets: t_active = off + clamp(t - start, 0, len) / 3600. Kickoff day starts at 0
    (at the kickoff time); pre days (the last `pre_days` calendar days before the kickoff day) get negative offsets.
    Columns: pt_date, start, end, len_h, off_h, pre, ho."""
    c = calendar()
    k = kickoff(goal)
    kd = c.filter(pl.col("goal_no") == goal).sort("pt_date")
    if days is not None:
        kd = kd.filter(pl.col("pt_date").is_in(days))
    if not allow_holdout:
        kd = kd.filter(~pl.col("ho"))
    first = kd["pt_date"][0]
    pre = c.filter(pl.col("pt_date") < first).tail(pre_days)
    rows = []
    off = 0.0
    for r in kd.iter_rows(named=True):
        st = max(r["win_start"], k) if r["pt_date"] == first else r["win_start"]
        ln = max((r["win_end"] - st).total_seconds() / 3600, 0)
        rows.append(dict(pt_date=r["pt_date"], start=st, end=r["win_end"], len_h=ln, off_h=off, pre=False, ho=r["ho"]))
        off += ln
    off = 0.0
    for r in reversed(list(pre.iter_rows(named=True))):
        ln = (r["win_end"] - r["win_start"]).total_seconds() / 3600
        off -= ln
        rows.append(dict(pt_date=r["pt_date"], start=r["win_start"], end=r["win_end"], len_h=ln, off_h=off, pre=True, ho=r["ho"]))
    return pl.DataFrame(rows).sort("off_h")


def to_active(df: pl.DataFrame, tcol: str, clk: pl.DataFrame) -> pl.DataFrame:
    """Map UTC times to active hours via the row's PT date; drops rows outside [start - 15 min, end + 15 min]."""
    j = df.join(clk.select("pt_date", "start", "end", "len_h", "off_h", "pre", "ho"), on="pt_date", how="inner")
    j = j.filter((pl.col(tcol) >= pl.col("start") - SLACK) & (pl.col(tcol) <= pl.col("end") + SLACK))
    sec = (pl.col(tcol) - pl.col("start")).dt.total_microseconds() / 3.6e9
    return j.with_columns((pl.col("off_h") + pl.min_horizontal(pl.max_horizontal(sec, pl.lit(0.0)), pl.col("len_h"))).alias("ta"))


_COMMITS = None
_COMMITS_ALL = None


def commits(allow_holdout: bool = False) -> pl.DataFrame:
    """DQ4 agent work commits; holdout rows removed unless allow_holdout (confirm.py only)."""
    global _COMMITS, _COMMITS_ALL
    if allow_holdout:
        if _COMMITS_ALL is None:
            w = pl.read_parquet(L.SH / "work_commits.parquet", columns=["repo", "t", "pt_date", "author_agent", "author_kind",
                                                                        "canonical", "imported", "automated"])
            _COMMITS_ALL = w.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent")
                                    & ~pl.col("automated") & pl.col("author_agent").is_not_null()).select(
                "repo", "t", "pt_date", pl.col("author_agent").alias("agent"))
        return _COMMITS_ALL
    if _COMMITS is None:
        w = pl.read_parquet(L.SH / "work_commits.parquet", columns=["repo", "t", "pt_date", "goal_no", "holdout", "author_agent",
                                                                    "author_kind", "canonical", "imported", "automated"])
        w = w.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                     & pl.col("author_agent").is_not_null())
        hm = holdout_mask(w["pt_date"].to_list(), w["goal_no"].to_list())
        _COMMITS = w.filter(~pl.Series(hm) & ~pl.col("holdout")).select("repo", "t", "pt_date", pl.col("author_agent").alias("agent"))
    return _COMMITS


def commits_active(clk: pl.DataFrame, allow_holdout: bool = False) -> tuple[pl.DataFrame, dict]:
    c = commits(allow_holdout).filter(pl.col("pt_date").is_in(clk["pt_date"].to_list()))
    n0 = c.height
    a = to_active(c, "t", clk).sort(["agent", "ta", "t"])
    return a, {"n_commits_days": n0, "n_mapped": a.height, "n_dropped_outside_window": n0 - a.height}


def ensemble(goal: int, variant: str, H: float, clk: pl.DataFrame | None = None, agents: list | None = None,
             settle_win: float = 4.0, allow_holdout: bool = False) -> L.Ensemble:
    clk = clock(goal, allow_holdout=allow_holdout) if clk is None else clk
    if variant == "pre" and clk.filter(pl.col("pre"))["ho"].any() and not allow_holdout:
        raise RuntimeError(f"#{goal}: pre-kickoff days are in the holdout")
    if variant == "pre" and clk.filter(pl.col("pre")).height == 0:
        raise RuntimeError(f"#{goal}: no pre-kickoff days")
    a, info = commits_active(clk, allow_holdout)
    post = a.filter((pl.col("ta") >= 0) & (pl.col("ta") <= H))
    ags = sorted(post["agent"].unique().to_list()) if agents is None else sorted(set(agents) & set(post["agent"].unique().to_list()))
    repos = sorted(a["repo"].unique().to_list())
    code = {r: i for i, r in enumerate(repos)}
    times, codes, init = [], [], []
    for ag in ags:
        p = post.filter(pl.col("agent") == ag)
        times.append(p["ta"].to_numpy())
        codes.append(np.array([code[r] for r in p["repo"].to_list()], np.int64))
        if variant == "pre":
            q = a.filter((pl.col("agent") == ag) & (pl.col("ta") < 0))
            init.append(code[q["repo"][-1]] if q.height else L.NULL)
        else:
            init.append(L.NULL)
    E = L.Ensemble(ags, times, codes, np.array(init, np.int64), H, settle_win)
    E.extra = {"goal": goal, "variant": variant, **info, "n_repos_seen": len(repos)}
    return E


def call_rates(clk: pl.DataFrame, agents: list, t0: float, t1: float, allow_holdout: bool = False) -> dict:
    """Ledger calls per active hour in [t0, t1] (summary calls excluded)."""
    cw = pl.read_parquet(L.SH / "call_windows.parquet", columns=["agent", "pt_date", "goal_no", "holdout", "kind", "t_call"])
    cw = cw.filter(pl.col("pt_date").is_in(clk["pt_date"].to_list()) & pl.col("agent").is_in(agents)
                   & ~pl.col("kind").cast(pl.String).is_in(list(L.SUMMARY_CALLS)))
    if not allow_holdout:
        hm = holdout_mask(cw["pt_date"].to_list(), cw["goal_no"].to_list())
        cw = cw.filter(~pl.Series(hm) & ~pl.col("holdout"))
    cw = to_active(cw, "t_call", clk).filter((pl.col("ta") >= t0) & (pl.col("ta") <= t1))
    n = cw.group_by("agent").len()
    return {r["agent"]: r["len"] / (t1 - t0) for r in n.iter_rows(named=True)}


def write_unit(E: L.Ensemble, name: str):
    d = L.OUTD / name
    d.mkdir(parents=True, exist_ok=True)
    rows = []
    for a, t, c in zip(E.agents, E.times, E.codes):
        rows += [{"agent": a, "t_active": float(x), "repo_code": int(y)} for x, y in zip(t, c)]
    pl.DataFrame(rows, schema={"agent": pl.Int16, "t_active": pl.Float32, "repo_code": pl.Int32}).write_parquet(
        d / f"states_{E.extra['variant']}.parquet", compression="zstd")
    pl.DataFrame({"agent": E.agents, "init_code": E.init.tolist()}).write_parquet(d / f"init_{E.extra['variant']}.parquet")


def provenance(params: dict):
    L.OUTD.mkdir(parents=True, exist_ok=True)
    (L.OUTD / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H75-reallocation-speed-limit/scheme/build.py (+ analysis/run.py, analysis/synthetic.py)",
        "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["work_commits (DQ4)", "calendar", "goals.parquet", "call_windows", "ground_truth_labels", "roster"]}],
        "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))


def main():
    for g, var in REPLICATION.items():
        for v in (["pre", "null"] if var == "pre" else ["null"]):
            E = ensemble(g, v, 20.0)
            write_unit(E, f"G{g:02d}")
            print(g, v, len(E.agents), E.extra)
    provenance({"horizon_h": 20.0, "pre_days": 2, "grid_h": L.GRID_H, "settle_win_h": 4.0, "work_filter": "DQ4 default"})


if __name__ == "__main__":
    main()
