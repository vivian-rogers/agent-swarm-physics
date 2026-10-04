"""H110 scheme: goal transitions, statement windows and own-repo pinning.

Output: data/processed/H110-exchange-bias-own-artifact/
  transitions.parquet  P, P-1, regime, t0 (kickoff), L (last active day of P-1), old_days (L-3..L-1), last2 (last 2 active
                       days before t0), post_days (first 5 active days of P), placebo periods Q and their late days
  windows.parquet      per statement x transition: srow, agent, t, transition P, window (old / pre / d1..d5 / plc_<Q>)
  pinning.parquet      per agent x transition: n_own_last2, n_any_last2, pinned_own, pinned_any, pinned_repos (list),
                       commits to the pinned repos on post days d1..d5 (after t0 on d1), last_day (index of the last post
                       day with a commit to a pinned repo, 0 if none), continuing (commits on >= 2 of d1..d3), stopped (pinned, none on d1..d3)
  owners.parquet       repo -> owner (author of the earliest NON-HOLDOUT agent work commit; H94 rule restricted to the
                       exploration window)
No text is read. Held-out rows are dropped with holdout_mask and the table flags (asserted).

Usage: uv run python hypotheses/H110-exchange-bias-own-artifact/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H110-exchange-bias-own-artifact"
EXCLUDE = {19, 28, 30}
TRANSITIONS = [31, 37, 38, 39, 40, 41, 42]
NPOST = 5


def active_days(include_holdout: bool = False) -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("n_agent_events") > 0)
    if not include_holdout:
        cal = cal.filter(~pl.col("holdout"))
    return cal.select("pt_date", "goal_no", "regime", "win_start").sort("pt_date")


def kickoff_time(goal: int, cal: pl.DataFrame):
    g = pl.read_parquet(ED / "goals.parquet").filter((pl.col("goal_no") == goal) & (pl.col("kind") == "kickoff"))
    if g.height and g["win_start"][0] is not None:
        return g["win_start"].min()
    return cal.filter(pl.col("goal_no") == goal)["win_start"].min()


def transitions(cal: pl.DataFrame, targets=TRANSITIONS, include_holdout: bool = False) -> pl.DataFrame:
    rows = []
    for P in targets:
        dp = cal.filter(pl.col("goal_no") == P - 1)
        dn = cal.filter(pl.col("goal_no") == P)
        if dp.height == 0 or dn.height == 0:
            continue
        pdays = dp["pt_date"].to_list()
        ndays = dn["pt_date"].to_list()
        reg = dn["regime"][0]
        regs = set(dp["regime"].to_list()[-4:]) | set(dn["regime"].to_list()[:NPOST])
        L = pdays[-1]
        old = pdays[-4:-1] if len(pdays) >= 2 else []
        last2 = pdays[-2:]
        # placebo periods: same regime, not adjacent, not #23
        qs = []
        for Q in sorted(set(cal.filter(pl.col("regime") == reg)["goal_no"].to_list())):
            if Q in range(P - 2, P + 2) or Q == 23:
                continue
            qd = cal.filter((pl.col("goal_no") == Q) & (pl.col("regime") == reg))["pt_date"].to_list()
            if len(qd) >= 1:
                qs.append({"Q": int(Q), "days": qd[-3:]})
        rows.append({"P": P, "P_prev": P - 1, "regime": reg, "one_regime": len(regs) == 1,
                     "t0": kickoff_time(P, cal), "L": L, "old_days": old, "last2": last2,
                     "post_days": ndays[:NPOST], "placebos": json.dumps(qs)})
    return pl.DataFrame(rows)


def statements(include_holdout: bool = False) -> pl.DataFrame:
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
    st = st.filter(~pl.col("agent").is_in(list(EXCLUDE)))
    hm = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    st = st.with_columns(pl.Series("hm", hm))
    if not include_holdout:
        st = st.filter(~pl.col("hm") & ~pl.col("holdout"))
        assert not st["hm"].any() and not st["holdout"].any()
    return st.select("srow", "kind", "agent", "t", "pt_date", "goal_no", "regime")


def windows(st: pl.DataFrame, tr: pl.DataFrame) -> pl.DataFrame:
    out = []
    for row in tr.iter_rows(named=True):
        P, t0 = row["P"], row["t0"]
        d1 = row["post_days"][0]
        s_old = st.filter(pl.col("pt_date").is_in(row["old_days"])).with_columns(pl.lit("old").alias("window"))
        s_pre = st.filter((pl.col("pt_date") == row["L"]) | ((pl.col("pt_date") == d1) & (pl.col("t") < t0))) \
            .with_columns(pl.lit("pre").alias("window"))
        parts = [s_old, s_pre]
        for k, d in enumerate(row["post_days"], start=1):
            s = st.filter(pl.col("pt_date") == d)
            if k == 1:
                s = s.filter(pl.col("t") >= t0)
            parts.append(s.with_columns(pl.lit(f"d{k}").alias("window")))
        for q in json.loads(row["placebos"]):
            parts.append(st.filter(pl.col("pt_date").is_in(q["days"])).with_columns(pl.lit(f"plc_{q['Q']}").alias("window")))
        out.append(pl.concat(parts).with_columns(pl.lit(P).cast(pl.Int16).alias("P")))
    return pl.concat(out)


def work(include_holdout: bool = False) -> pl.DataFrame:
    wc = pl.read_parquet(SH / "work_commits.parquet", columns=["repo", "t", "pt_date", "goal_no", "holdout", "author_agent",
                                                                "author_kind", "automated", "canonical", "imported"])
    wc = wc.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated"))
    hm = np.array(holdout_mask(wc["pt_date"].to_list(), wc["goal_no"].to_list()))
    wc = wc.with_columns(pl.Series("hm", hm))
    if not include_holdout:
        wc = wc.filter(~pl.col("hm") & ~pl.col("holdout"))
        assert not wc["hm"].any()
    return wc.with_columns(pl.col("repo").cast(pl.Utf8))


def owners(wc: pl.DataFrame) -> pl.DataFrame:
    return wc.sort("t").group_by("repo").agg(pl.col("author_agent").first().alias("owner"))


def pinning(wc: pl.DataFrame, own: pl.DataFrame, tr: pl.DataFrame, st: pl.DataFrame) -> pl.DataFrame:
    wc = wc.join(own, on="repo", how="left")
    rows = []
    for row in tr.iter_rows(named=True):
        P, t0 = row["P"], row["t0"]
        agents = sorted(set(st.filter(pl.col("pt_date").is_in([row["L"]] + row["post_days"]))["agent"].to_list()))
        w2 = wc.filter(pl.col("pt_date").is_in(row["last2"]) & (pl.col("t") < t0))
        for a in agents:
            wa = w2.filter(pl.col("author_agent") == a)
            own_repos = sorted(set(wa.filter(pl.col("owner") == a)["repo"].to_list()))
            any_repos = sorted(set(wa["repo"].to_list()))
            post = []
            for k, d in enumerate(row["post_days"], start=1):
                wd = wc.filter((pl.col("author_agent") == a) & (pl.col("pt_date") == d) & (pl.col("t") >= t0))
                post.append(int(wd.filter(pl.col("repo").is_in(own_repos)).height) if own_repos else 0)
            post_any = []
            for k, d in enumerate(row["post_days"], start=1):
                wd = wc.filter((pl.col("author_agent") == a) & (pl.col("pt_date") == d) & (pl.col("t") >= t0))
                post_any.append(int(wd.filter(pl.col("repo").is_in(any_repos)).height) if any_repos else 0)
            last = max([k for k, c in enumerate(post, start=1) if c > 0], default=0)
            last_any = max([k for k, c in enumerate(post_any, start=1) if c > 0], default=0)
            rows.append({"P": P, "agent": a, "n_own_last2": int(wa.filter(pl.col("owner") == a).height),
                         "n_any_last2": int(wa.height), "pinned_own": bool(own_repos), "pinned_any": bool(any_repos),
                         "pinned_repos": own_repos, "any_repos": any_repos, "post_commits": post,
                         "post_commits_any": post_any, "last_day": last, "last_day_any": last_any,
                         "n_post_days": len(row["post_days"]),
                         "continuing": sum(c > 0 for c in post[:3]) >= 2,
                         "stopped": bool(own_repos) and sum(post[:3]) == 0})
    return pl.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cal = active_days()
    tr = transitions(cal)
    st = statements()
    win = windows(st, tr)
    wc = work()
    own = owners(wc)
    pin = pinning(wc, own, tr, st)
    tr.write_parquet(OUT / "transitions.parquet")
    win.write_parquet(OUT / "windows.parquet", compression="zstd")
    pin.write_parquet(OUT / "pinning.parquet")
    own.write_parquet(OUT / "owners.parquet")
    prov = {"built_by": "hypotheses/H110-exchange-bias-own-artifact/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["embeddings/statements", "calendar", "goals", "work_commits"]}],
            "params": {"transitions": TRANSITIONS, "npost": NPOST, "exclude": sorted(EXCLUDE)},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(tr.select("P", "regime", "one_regime", "t0", "L", "old_days", "last2", "post_days"))
    print(pin.group_by("P").agg(pl.len(), pl.col("pinned_own").sum(), pl.col("pinned_any").sum(),
                                pl.col("continuing").sum(), pl.col("stopped").sum()).sort("P"))


if __name__ == "__main__":
    main()
