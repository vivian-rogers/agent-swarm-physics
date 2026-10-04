"""H125 scheme: statement selections on the active-hour clock for the kickoff step-response tests (codes only, no text).

Builds data/processed/H125-kickoff-damped-oscillator/:
  kickoffs.parquet  one row per eligible kickoff (shared kickoff, non-holdout kickoff day, >= 5 non-holdout active days from
                    day 1 in one regime; #2 and #23 excluded) plus the native designs G51 (own roles) and NE38.
  stmt.parquet      statement rows (index into the shared statements arrays) per design: agent, t, pt_date, day_idx
                    (0 = previous active day, 1.. = active days of the period), h (active hours since t0, summed over
                    calendar windows; < 0 before t0), slot (quarter of the day's calendar window), seg (pre / post).
                    Every row passes common.holdout_mask (asserted).
  vectors.npz       unit kickoff directions of every non-holdout kickoff, whitened in each regime basis, both models
                    (decoys are chosen in the analysis); #51 agent_goal (role) directions in the regime-III basis.
  _provenance.json
Usage: uv run python hypotheses/H125-kickoff-damped-oscillator/scheme/build.py
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
from embed_models import goal_vectors, load_whitener  # noqa: E402

S = ROOT / "data/processed/shared"
ED = S / "embeddings"
OUT = ROOT / "data/processed/H125-kickoff-damped-oscillator"
H54 = ROOT / "data/processed/H54-kickoff-quench-target"
MODELS = ["bge_small", "gte_modernbert"]
EXCLUDE_AGENTS = {19, 28, 30}     # Claude Code agent; fine-tuned leaders (as H96/H103)
EXCLUDE_GOALS = {2, 23}           # no kickoff; H10 keeps #23 blind
MIN_DAYS = 5
NE38_T = dt.datetime(2026, 7, 29, 16, 51, tzinfo=dt.timezone.utc)
NE38_AGENT = 40
NE38_SPAN = ("2026-07-20", "2026-08-14")


def unitv(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("row")
    ho = holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())
    st = st.filter(~pl.Series(ho) & ~pl.col("agent").is_in(list(EXCLUDE_AGENTS)))

    cal = pl.read_parquet(S / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String)).sort("pt_date")
    cal = cal.with_columns(pl.Series("ho", holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))
    cal = cal.with_columns((pl.col("window_s") / 3600).alias("day_h"))
    # cumulative active hours at each calendar day start (all days, held-out days contribute 0 h: they are never inside
    # an analysed span because spans must be contiguous non-holdout days)
    cal = cal.with_columns((pl.col("day_h").cum_sum() - pl.col("day_h")).alias("H_before"))
    calr = {r["pt_date"]: r for r in cal.iter_rows(named=True)}
    days_all = cal["pt_date"].to_list()

    def hcum(t: dt.datetime, d: str) -> float:
        r = calr[d]
        x = (t - r["win_start"]).total_seconds() / 3600
        return r["H_before"] + min(max(x, 0.0), r["day_h"])

    def slot(t: dt.datetime, d: str) -> int:
        r = calr[d]
        f = (t - r["win_start"]).total_seconds() / max(r["window_s"], 1)
        return int(min(max(f, 0.0), 0.9999) * 4)

    goals = pl.read_parquet(ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    kick = goals.filter(pl.col("kind") == "kickoff")
    k54 = pl.read_parquet(H54 / "kickoffs.parquet").filter(pl.col("room").is_null()).select("goal_no", "t0")
    t0map = dict(zip(k54["goal_no"].to_list(), k54["t0"].to_list()))
    pa = pl.read_parquet(S / "period_affordances.parquet").select("goal_no", "mode").unique("goal_no")
    mode = dict(zip(pa["goal_no"].to_list(), pa["mode"].to_list()))
    pu = pl.read_parquet(S / "period_units.parquet")
    unit_of = {d: u for u, ds in zip(pu["unit_id"].to_list(), pu["days"].to_list()) for d in ds}

    GV = {m: goal_vectors(m).astype(np.float64) for m in MODELS}
    W = {(m, r): load_whitener(r, 32, m) for m in MODELS for r in ("I", "II", "III")}

    rows_out, kick_rows = [], []

    def add_design(design: str, goal: int, t0: dt.datetime, days: list[str], prev_day: str | None, agents: list[int],
                   extra: dict):
        sel_days = ([prev_day] if prev_day else []) + days
        sub = st.filter(pl.col("pt_date").is_in(sel_days) & pl.col("agent").is_in(agents))
        if goal is not None:
            sub = sub.filter((pl.col("goal_no") == goal) | (pl.col("pt_date") == (prev_day or "")))
        didx = {d: i + 1 for i, d in enumerate(days)}
        if prev_day:
            didx[prev_day] = 0
        h0 = hcum(t0, days[0])
        recs = sub.select("row", "agent", "t", "pt_date", "room", "kind").to_dicts()
        for r in recs:
            r["design"] = design
            r["day_idx"] = didx[r["pt_date"]]
            r["h"] = hcum(r["t"], r["pt_date"]) - h0
            r["slot"] = slot(r["t"], r["pt_date"])
            r["seg"] = "pre" if (r["day_idx"] == 0 or r["t"] < t0) else "post"
            r["unit_id"] = unit_of.get(r["pt_date"], "?")
        rows_out.extend(recs)
        kick_rows.append(dict(design=design, goal_no=goal, t0=t0, first_day=days[0], n_days=len(days),
                              days=days, prev_day=prev_day, incumbents=sorted(agents),
                              day_h=[calr[d]["day_h"] for d in days], **extra))

    # ------------------------------------------------------------------------------ replication: eligible kickoffs
    for r in kick.sort("goal_no").iter_rows(named=True):
        p = int(r["goal_no"])
        if p in EXCLUDE_GOALS or r["holdout"]:
            continue
        gd = cal.filter(pl.col("goal_no") == p).sort("pt_date")
        if gd.height == 0 or gd["ho"][0]:
            continue
        # contiguous non-holdout days from day 1
        days = []
        for rr in gd.iter_rows(named=True):
            if rr["ho"]:
                break
            days.append(rr["pt_date"])
        if len(days) < MIN_DAYS:
            continue
        regs = set(cal.filter(pl.col("pt_date").is_in(days[:MIN_DAYS]))["regime"].to_list())
        if len(regs) > 1:
            continue
        reg = regs.pop()
        t0 = t0map.get(p, r["win_start"])
        i0 = days_all.index(days[0])
        prev_day = days_all[i0 - 1] if i0 > 0 and not calr[days_all[i0 - 1]]["ho"] else None
        inc = st.filter((pl.col("goal_no") == p) & (pl.col("pt_date") == days[0]) & (pl.col("t") >= t0))["agent"]
        agents = sorted(set(inc.to_list()))
        if len(agents) < 3:
            continue
        add_design(f"T{p:02d}", p, t0, days, prev_day, agents,
                   dict(kind="kickoff", regime=reg, mode=mode.get(p), kick_gid=int(r["gid"]), native=None,
                        role_gids=None))

    # ------------------------------------------------------------------------------ native NE38: #51 around 07-29
    d51 = [d for d in days_all if NE38_SPAN[0] <= d <= NE38_SPAN[1] and calr[d]["goal_no"] == 51 and not calr[d]["ho"]]
    ag = goals.filter(pl.col("kind") == "agent_goal")
    valid = ag.filter((pl.col("valid_from") <= "2026-07-29") & pl.col("valid_to").is_null())
    roles = {int(a): int(g) for a, g in zip(valid["agent"].to_list(), valid["gid"].to_list())}
    roles[NE38_AGENT] = int(ag.filter(pl.col("agent") == NE38_AGENT)["gid"][0])
    agents = sorted(a for a in roles if a not in EXCLUDE_AGENTS)
    # day 1 = 07-29 (the reassignment day); days before it are 'pre' (day_idx <= 0 via negative indices below)
    i29 = d51.index("2026-07-29")
    pre_days, post_days = d51[:i29], d51[i29:]
    sub = st.filter(pl.col("pt_date").is_in(d51) & pl.col("agent").is_in(agents) & (pl.col("goal_no") == 51))
    h0 = hcum(NE38_T, "2026-07-29")
    for r in sub.select("row", "agent", "t", "pt_date", "room", "kind").to_dicts():
        r["design"] = "NE38"
        r["day_idx"] = (post_days.index(r["pt_date"]) + 1) if r["pt_date"] in post_days else (pre_days.index(r["pt_date"]) - len(pre_days))
        r["h"] = hcum(r["t"], r["pt_date"]) - h0
        r["slot"] = slot(r["t"], r["pt_date"])
        r["seg"] = "pre" if r["t"] < NE38_T else "post"
        r["unit_id"] = unit_of.get(r["pt_date"], "?")
        rows_out.append(r)
    kick_rows.append(dict(design="NE38", goal_no=51, t0=NE38_T, first_day="2026-07-29", n_days=len(post_days),
                          days=post_days, prev_day=pre_days[-1] if pre_days else None, incumbents=agents,
                          day_h=[calr[d]["day_h"] for d in post_days], kind="native", regime="III", mode=mode.get(51),
                          kick_gid=roles[NE38_AGENT], native="NE38", role_gids=json.dumps(roles)))

    # ------------------------------------------------------------------------------ native G51: own roles at the #51 kickoff
    g51 = [k for k in kick_rows if k["design"] == "T51"]
    if g51:
        k = g51[0]
        v51 = ag.filter(pl.col("valid_from") == "2026-07-06")
        r51 = {int(a): int(g) for a, g in zip(v51["agent"].to_list(), v51["gid"].to_list())}
        agents = [a for a in k["incumbents"] if a in r51]
        add_design("G51", 51, k["t0"], k["days"], k["prev_day"], agents,
                   dict(kind="native", regime="III", mode=mode.get(51), kick_gid=k["kick_gid"], native="G51",
                        role_gids=json.dumps(r51)))

    # ------------------------------------------------------------------------------ vectors
    flat = {}
    kgid = kick.filter(~pl.col("holdout") & ~pl.col("goal_no").is_in(list(EXCLUDE_GOALS))).sort("goal_no")
    flat["kick_goal_no"] = kgid["goal_no"].to_numpy().astype(np.int64)
    flat["kick_gid"] = kgid["gid"].to_numpy().astype(np.int64)
    for m in MODELS:
        for rg in ("I", "II", "III"):
            Kw = W[(m, rg)](GV[m][kgid["gid"].to_numpy()])
            flat[f"K|{m}|{rg}"] = Kw / np.linalg.norm(Kw, axis=1, keepdims=True)
        rg_all = ag.sort("gid")
        Rw = W[(m, "III")](GV[m][rg_all["gid"].to_numpy()])
        flat[f"R|{m}"] = Rw / np.linalg.norm(Rw, axis=1, keepdims=True)
    flat["role_gid"] = ag.sort("gid")["gid"].to_numpy().astype(np.int64)
    flat["role_agent"] = ag.sort("gid")["agent"].to_numpy().astype(np.int64)
    np.savez_compressed(OUT / "vectors.npz", **flat)

    so = pl.DataFrame(rows_out, infer_schema_length=None).with_columns(
        pl.col("day_idx").cast(pl.Int16), pl.col("slot").cast(pl.Int8), pl.col("h").cast(pl.Float32))
    assert not any(holdout_mask(so["pt_date"].to_list(), [None] * so.height)), "held-out day leaked"
    so.write_parquet(OUT / "stmt.parquet", compression="zstd")
    kr = pl.DataFrame(kick_rows, infer_schema_length=None)
    kr.write_parquet(OUT / "kickoffs.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H125-kickoff-damped-oscillator/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements", "shared/embeddings/goals", "goal_vectors{,_gte_modernbert}",
                                   "whitening_* (embed_models.load_whitener)", "shared/calendar", "shared/period_units",
                                   "shared/period_affordances", "H54/kickoffs (t0, read-only)"]}],
            "params": {"exclude_agents": sorted(EXCLUDE_AGENTS), "exclude_goals": sorted(EXCLUDE_GOALS), "min_days": MIN_DAYS,
                       "models": MODELS, "ne38_t": NE38_T.isoformat(), "ne38_span": NE38_SPAN},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(kr.select("design", "goal_no", "regime", "mode", "n_days", pl.col("incumbents").list.len().alias("n_inc"),
                    "first_day", "prev_day"))
    print("statements:", so.height)


if __name__ == "__main__":
    main()
