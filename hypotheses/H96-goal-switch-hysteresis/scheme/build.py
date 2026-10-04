"""H96 scheme: transitions, old-state windows, placebo old states and pseudo-switches (no text; shared tables only).

Writes data/processed/H96-goal-switch-hysteresis/:
  transitions.parquet  one row per eligible transition P-1 -> P (both non-holdout, one regime, #23 excluded):
                       t0 (kickoff time of P), pre day L, old-state days, post days, placebo periods, field gids
  pseudo.parquet       one row per ordinary day boundary inside a non-holdout period (rival R2)
  late_days.parquet    the last 3 active days of every non-holdout period (placebo old states)
  _provenance.json
Statement vectors are not copied: the analysis reads the shared DQ5 arrays by row index.

Usage: uv run python hypotheses/H96-goal-switch-hysteresis/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT, REVISION, git_commit, holdout_mask, load_holdout  # noqa: E402

DATA = ROOT / "data/processed/H96-goal-switch-hysteresis"
EXCLUDE_GOALS = {23}          # H10 keeps #23 blind for its confirmatory #22 -> #23 pair (H54 did the same)
EXCLUDE_AGENTS = {19, 28, 30}  # Claude Code agent; fine-tuned leaders
OLD_DAYS = 3                   # days before the pre day used for the old-state direction
POST_DAYS = 3


def calendar() -> pl.DataFrame:
    cal = pl.read_parquet(OUT / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String)).sort("pt_date")
    ho = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    return cal.with_columns(pl.Series("ho", ho))


def eligible_goals(cal: pl.DataFrame) -> list[int]:
    held = set(load_holdout()["goal_periods_held_out"])
    out = []
    for g in sorted(cal["goal_no"].unique().to_list()):
        if g in held or g in EXCLUDE_GOALS or g < 1:
            continue
        out.append(g)
    return out


def days_of(cal: pl.DataFrame, g: int, nonho: bool = True) -> pl.DataFrame:
    d = cal.filter(pl.col("goal_no") == g)
    return d.filter(~pl.col("ho")) if nonho else d


def kickoff_time(goals: pl.DataFrame, cal: pl.DataFrame, g: int) -> dt.datetime:
    k = goals.filter((pl.col("goal_no") == g) & (pl.col("kind") == "kickoff"))
    if k.height:
        return k["win_start"][0]
    return cal.filter(pl.col("goal_no") == g)["win_start"].min()


def field_gids(goals: pl.DataFrame, g: int) -> list[int]:
    f = goals.filter((pl.col("goal_no") == g) & pl.col("kind").cast(pl.String).is_in(["kickoff", "goal", "kickoff_room"]))
    return sorted(f["gid"].to_list())


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    cal = calendar()
    goals = pl.read_parquet(OUT / "embeddings/goals.parquet")
    elig = eligible_goals(cal)

    # last 3 active non-holdout days of each eligible period, by regime (placebo old states)
    late = []
    for g in elig:
        d = days_of(cal, g)
        for reg in d["regime"].unique().to_list():
            dd = d.filter(pl.col("regime") == reg)["pt_date"].to_list()[-OLD_DAYS:]
            late += [{"goal_no": g, "regime": reg, "pt_date": x} for x in dd]
    late = pl.DataFrame(late)

    def placebos(P: int, reg: str) -> list[int]:
        cand = sorted(late.filter(pl.col("regime") == reg)["goal_no"].unique().to_list())
        return [q for q in cand if q not in range(P - 2, P + 2)]

    trans = []
    for P in elig:
        if P - 1 not in elig:
            continue
        old = days_of(cal, P - 1)
        new = days_of(cal, P)
        if old.height < 2 or new.height < 1:
            continue
        L = old["pt_date"][-1]
        reg = old["regime"][-1]
        odays = [x for x in old["pt_date"].to_list()[:-1][-OLD_DAYS:]]
        odays = [x for x in odays if old.filter(pl.col("pt_date") == x)["regime"][0] == reg]
        pdays = [x for x in new["pt_date"].to_list()[:POST_DAYS]
                 if new.filter(pl.col("pt_date") == x)["regime"][0] == reg]
        if not odays or not pdays:
            continue
        plac = placebos(P, reg)
        trans.append({"P": P, "Pm1": P - 1, "regime": reg, "t0": kickoff_time(goals, cal, P), "pre_day": L,
                      "old_days": odays, "post_days": pdays, "placebos": plac, "n_placebos": len(plac),
                      "field_gids": field_gids(goals, P), "eligible": len(plac) >= 3})
    trans = pl.DataFrame(trans)

    # pseudo-switches: ordinary day boundaries inside eligible periods (>= 3 days before, >= 1 after)
    pseudo = []
    for g in elig:
        d = days_of(cal, g)
        for reg in d["regime"].unique().to_list():
            dd = d.filter(pl.col("regime") == reg)
            ds = dd["pt_date"].to_list()
            for j in range(OLD_DAYS, len(ds) - 1):
                post = ds[j + 1: j + 1 + POST_DAYS]
                pseudo.append({"goal_no": g, "regime": reg, "pre_day": ds[j], "old_days": ds[j - OLD_DAYS:j],
                               "post_days": post, "t0": dd.filter(pl.col("pt_date") == ds[j + 1])["win_start"][0],
                               "placebos": placebos(g, reg), "field_gids": field_gids(goals, g)})
    pseudo = pl.DataFrame(pseudo).with_columns(pl.col("placebos").list.len().alias("n_placebos"))

    # every day used must be non-holdout
    used = set(late["pt_date"].to_list())
    for col in ("old_days", "post_days"):
        for r in trans[col].to_list() + pseudo[col].to_list():
            used |= set(r)
    used |= set(trans["pre_day"].to_list()) | set(pseudo["pre_day"].to_list())
    chk = cal.filter(pl.col("pt_date").is_in(list(used)))
    assert not chk["ho"].any(), "held-out day in H96 windows"

    trans.write_parquet(DATA / "transitions.parquet")
    pseudo.write_parquet(DATA / "pseudo.parquet")
    late.write_parquet(DATA / "late_days.parquet")
    prov = {"built_by": "hypotheses/H96-goal-switch-hysteresis/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["calendar", "embeddings/goals", "embeddings/statements",
                                   "statements_{style_resid32,white32,style_resid_period32}_{bge_small,gte_modernbert}",
                                   "goal_vectors", "whitening", "roster", "ground_truth_labels"]}],
            "params": {"exclude_goals": sorted(EXCLUDE_GOALS), "exclude_agents": sorted(EXCLUDE_AGENTS),
                       "old_days": OLD_DAYS, "post_days": POST_DAYS},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (DATA / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))
    print(f"transitions {trans.height} (eligible {trans['eligible'].sum()}), pseudo-switches {pseudo.height}")
    print(trans.select("P", "regime", "pre_day", "n_placebos", "eligible", pl.col("old_days").list.len().alias("n_old"),
                       pl.col("post_days").list.len().alias("n_post")))


if __name__ == "__main__":
    main()
