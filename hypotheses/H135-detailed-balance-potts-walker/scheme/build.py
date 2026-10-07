"""H135 scheme: project hops, occupancies (own calls), max-ent occupancies pi (H94 rules), availability windows,
age ranks and co-alive flags per period unit and channel.

  POLARS_MAX_THREADS=1 ... uv run python hypotheses/H135-detailed-balance-potts-walker/scheme/build.py [--period 38 ...]

Rules (card "Data scheme"; re-implemented, nothing imported from H94's or H129's folders):
- Units: `period_units` unit_id (#51: 51a-51l; split periods such as 38a-38e separately). Non-reserved days only
  (replicator_hosts.period_days, which applies common.holdout_mask; asserted again here).
- Work hops (H129): host replay (replicator_hosts: window_labels W 30, replay_events E 100, leave_times,
  classify_arrivals); per (unit, agent) a hop is a change between consecutive distinct host labels (direct departure
  or expiry then a later arrival). Hop time = arrival time. Visits: [arrival, depart/expire/leave] or open at the end.
- Attention hops (H129): project_states (w_min 30, sources all, raw project, non-reserved rows); consecutive labelled
  windows with different projects.
- Occupancy T^i_a: agent i's own calls (`call_windows`) carrying label a. Work: calls in (t_arr, t_end] of each visit
  (open visits: to the agent's last call in the unit). Attention: calls inside the agent's 30-min windows labelled a.
- pi (H94 rules): per unit, the M2 max-ent fit (row/column margins + own) on work quanta (agent x 30-min window x repo
  with >= 1 agent work commit), M3 (+ room) in two-room units (agents' modal rooms take > 1 value). Owner: the agent
  with the earliest non-reserved agent work commit to the repo (H94 used all DQ4 rows; mismatches are counted).
  Attention variant: the same fit on attention quanta (one per labelled agent-window); owner = H94 owner where the
  project is a DQ4 repo, else the agent with the earliest strict (url/output/bare) non-reserved mention.
  pi_i(j) = mu_ij / mu_i. ; pi(j) = mu_.j / N.
- Availability window per project in a unit-channel: [first arrival, last visit end] (open visits -> unit end).
- Co-alive (primary): first arrival <= unit start + 1 h and last end >= unit end - 1 h, where unit start/end are the
  calendar win_start of the unit's first active day and win_end of its last. Variant: alive >= 80% of the unit's
  active (calendar window) seconds.
- Age rank (H129): first non-reserved appearance of the project in the channel over all periods (older = smaller);
  ties by hashed name.

Writes data/processed/H135-detailed-balance-potts-walker/G<NN>/{hops,occupancy,avail}_<channel>.parquet, counts.json,
check.json (cross-check against H129 hops and H94 quanta) and _provenance.json. Names hashed on output.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import bisect  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE.parent / "analysis"))
import replicator_hosts as RH  # noqa: E402
from common import OUT as SHARED, REVISION, git_commit, holdout_mask  # noqa: E402
import h135lib as L  # noqa: E402

OUT = L.D
GOALS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
H129 = ROOT / "data/processed/H129-project-cycle-currents"
H94 = ROOT / "data/processed/H94-maxent-work-allocation"
W = 30
HOUR = 3600.0


# ============================================================================================ shared inputs
def _wc_all() -> pl.DataFrame:
    c = (pl.scan_parquet(SHARED / "work_commits.parquet")
         .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent")
                 & ~pl.col("automated") & pl.col("author_agent").is_not_null() & (pl.col("author_agent") != RH.CLAUDE_CODE))
         .select(pl.col("repo").cast(pl.String), pl.col("author_agent").alias("agent"), "t", "pt_date", "goal_no").collect())
    return c.filter(~pl.Series(holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())))


@lru_cache(maxsize=1)
def work_owner_age():
    c = _wc_all()
    own = c.sort("t", "agent").group_by("repo", maintain_order=True).first()
    return dict(own.select("repo", "agent").iter_rows()), {r: t.timestamp() for r, t in own.select("repo", "t").iter_rows()}


@lru_cache(maxsize=1)
def attention_rows() -> pl.DataFrame:
    ps = (pl.scan_parquet(SHARED / "project_states.parquet")
          .filter((pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all") & ~pl.col("holdout"))
          .select("goal_no", "pt_date", "win", "agent", "room", pl.col("project").cast(pl.String)).collect())
    assert not any(holdout_mask(ps["pt_date"].to_list(), ps["goal_no"].to_list())), "reserved rows in attention input"
    cal = RH.calendar().select("pt_date", "win_start")
    ps = ps.join(cal, on="pt_date", how="inner").with_columns(
        (pl.col("win_start") + pl.duration(minutes=30) * pl.col("win")).alias("t"))
    return ps.filter(pl.col("agent") != RH.CLAUDE_CODE)


@lru_cache(maxsize=1)
def attention_age() -> dict:
    a = attention_rows().group_by("project").agg(pl.col("t").min())
    return {p: t.timestamp() for p, t in a.iter_rows()}


@lru_cache(maxsize=1)
def strict_mention_owner() -> dict:
    """project -> agent with the earliest strict non-reserved mention (artifact_mentions, project_states' map)."""
    import project_states as PS
    pm = PS.project_map()
    am = (pl.scan_parquet(SHARED / "artifact_mentions.parquet")
          .filter((pl.col("speaker_kind").cast(pl.String) == "agent") & pl.col("how").cast(pl.String).is_in(["url", "output", "bare"])
                  & pl.col("agent").is_not_null() & (pl.col("agent") != RH.CLAUDE_CODE))
          .select("artifact", "t", "agent").collect())
    am = am.join(pm, on="artifact", how="inner")
    am = am.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    cal = pl.read_parquet(SHARED / "calendar.parquet", columns=["pt_date", "goal_no"])
    am = am.join(cal, on="pt_date", how="left").with_columns(pl.col("goal_no").fill_null(0))
    am = am.filter(~pl.Series(holdout_mask(am["pt_date"].to_list(), am["goal_no"].to_list())))
    f = am.sort("t", "agent").group_by("project", maintain_order=True).first()
    return dict(f.select("project", "agent").iter_rows())


def rank_of(age: dict, names) -> dict:
    keys = sorted(set(names), key=lambda r: (age.get(r, np.inf), RH.rhash(r)))
    return {r: i for i, r in enumerate(keys)}


@lru_cache(maxsize=1)
def rooms_by_agent():
    rt = pl.read_parquet(SHARED / "rooms_timeline.parquet")
    by = {}
    for (a,), g in rt.sort("t_start").group_by(["agent"], maintain_order=True):
        by[int(a)] = ([x.timestamp() for x in g["t_start"].to_list()], g["room"].to_list())
    return by


def room_of(a, ts: float):
    """H94's rule: the room of the agent's latest stay starting at or before t."""
    v = rooms_by_agent().get(int(a))
    if not v:
        return None
    k = bisect.bisect_right(v[0], ts) - 1
    return v[1][k] if k >= 0 else None


def unit_bounds(g: int, days: list[str]) -> dict:
    """unit -> (start, end, active seconds, [(win_start, win_end)])."""
    um = RH.unit_of_day(g)
    cal = pl.read_parquet(SHARED / "calendar.parquet", columns=["pt_date", "win_start", "win_end"]).filter(pl.col("pt_date").is_in(days))
    out = {}
    for d, ws, we in cal.sort("pt_date").iter_rows():
        u = um.get(d)
        if u is None or ws is None or we is None:
            continue
        o = out.setdefault(u, [ws.timestamp(), we.timestamp(), 0.0, []])
        o[0] = min(o[0], ws.timestamp())
        o[1] = max(o[1], we.timestamp())
        o[2] += we.timestamp() - ws.timestamp()
        o[3].append((ws.timestamp(), we.timestamp()))
    return out


def active_overlap(wins, t0, t1) -> float:
    return sum(max(0.0, min(we, t1) - max(ws, t0)) for ws, we in wins)


# ============================================================================================ hops
def work_hops(g: int, days, calls, um) -> tuple[pl.DataFrame, pl.DataFrame]:
    commits = RH.load_commits(g, days)
    leave = RH.leave_times(g, calls, days)
    lab = RH.window_labels(commits, W)
    ev = RH.classify_arrivals(RH.replay_events(lab, calls, E=100, leave_t=leave))
    ev = ev.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    ev = ev.with_columns(pl.col("pt_date").replace_strict(um, default=None).alias("unit")).filter(pl.col("unit").is_not_null())
    hops, visits = [], []
    for (u, a), gg in ev.sort("t").group_by(["unit", "agent"], maintain_order=True):
        a = int(a)
        last_repo, vis, prev_depart = None, None, None
        for kind, repo, t in gg.select("kind", "repo", "t").iter_rows():
            ts = t.timestamp()
            if kind in ("birth", "recruit"):
                if last_repo is not None and repo != last_repo:
                    hops.append((u, a, ts, last_repo, repo, prev_depart == (ts, last_repo)))
                vis = [u, a, repo, ts, None, None]
                last_repo = repo
            elif kind in ("depart", "expire", "leave"):
                if vis is not None and vis[2] == repo and vis[4] is None:
                    vis[4], vis[5] = ts, kind
                    visits.append(tuple(vis))
                    vis = None
                if kind == "depart":
                    prev_depart = (ts, repo)
        if vis is not None:
            visits.append(tuple(vis[:4]) + (None, "end"))
    H = pl.DataFrame(hops, schema={"unit": pl.String, "agent": pl.Int16, "t": pl.Float64, "src": pl.String,
                                   "dst": pl.String, "direct": pl.Boolean}, orient="row")
    V = pl.DataFrame(visits, schema={"unit": pl.String, "agent": pl.Int16, "repo": pl.String, "t_arr": pl.Float64,
                                     "t_end": pl.Float64, "end": pl.String}, orient="row")
    return H, V


def attention_hops(g: int, um) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    ps = attention_rows().filter(pl.col("goal_no") == g)
    ps = ps.with_columns(pl.col("pt_date").replace_strict(um, default=None).alias("unit")).filter(pl.col("unit").is_not_null())
    hops, visits = [], []
    for (u, a), gg in ps.sort("t").group_by(["unit", "agent"], maintain_order=True):
        a = int(a)
        last, start = None, None
        for p, t in gg.select("project", "t").iter_rows():
            ts = t.timestamp()
            if p != last:
                if last is not None:
                    hops.append((u, a, ts, last, p, True))
                    visits.append((u, a, last, start, ts, "depart"))
                last, start = p, ts
        if last is not None:
            visits.append((u, a, last, start, None, "end"))
    H = pl.DataFrame(hops, schema={"unit": pl.String, "agent": pl.Int16, "t": pl.Float64, "src": pl.String,
                                   "dst": pl.String, "direct": pl.Boolean}, orient="row")
    V = pl.DataFrame(visits, schema={"unit": pl.String, "agent": pl.Int16, "repo": pl.String, "t_arr": pl.Float64,
                                     "t_end": pl.Float64, "end": pl.String}, orient="row")
    return H, V, ps


# ============================================================================================ occupancy
def call_times(calls: pl.DataFrame, um) -> dict:
    c = calls.with_columns(pl.col("pt_date").replace_strict(um, default=None).alias("unit")).filter(pl.col("unit").is_not_null())
    return {(u, int(a)): np.sort(gg["t_call"].dt.epoch("us").to_numpy() / 1e6) for (u, a), gg in c.group_by(["unit", "agent"])}


def work_T(V: pl.DataFrame, ct: dict) -> dict:
    T = {}
    for u, a, r, t0, t1 in V.select("unit", "agent", "repo", "t_arr", "t_end").iter_rows():
        tc = ct.get((u, int(a)), np.array([]))
        hi = (tc[-1] if len(tc) else t0) if t1 is None else t1
        n = int(np.searchsorted(tc, hi, side="right") - np.searchsorted(tc, t0, side="right"))
        T[(u, int(a), r)] = T.get((u, int(a), r), 0) + max(n, 0)
    return T


def attention_T(ps: pl.DataFrame, ct: dict) -> dict:
    T = {}
    for u, a, p, t in ps.select("unit", "agent", "project", "t").iter_rows():
        tc = ct.get((u, int(a)), np.array([]))
        ts = t.timestamp()
        n = int(np.searchsorted(tc, ts + W * 60, side="left") - np.searchsorted(tc, ts, side="left"))
        T[(u, int(a), p)] = T.get((u, int(a), p), 0) + n
    return T


# ============================================================================================ pi
def work_quanta(g: int, days, um) -> pl.DataFrame:
    commits = RH.load_commits(g, days)
    cal = RH.calendar().filter(pl.col("pt_date").is_in(days)).select("pt_date", "win_start")
    c = commits.join(cal, on="pt_date", how="inner").with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() // (W * 60)).clip(lower_bound=0).cast(pl.Int32).alias("win"))
    q = c.group_by("agent", "pt_date", "win", "repo").agg(pl.col("t").min().alias("t_first"), pl.col("win_start").first())
    q = q.with_columns(pl.col("pt_date").replace_strict(um, default=None).alias("unit")).filter(pl.col("unit").is_not_null())
    q = q.with_columns((pl.col("win_start") + pl.duration(minutes=W) * pl.col("win") + pl.duration(minutes=W // 2)).alias("t_mid"))
    return q.select("unit", "agent", "pt_date", "win", pl.col("repo").alias("project"), "t_mid")


def attention_quanta(ps: pl.DataFrame) -> pl.DataFrame:
    return ps.with_columns((pl.col("t") + pl.duration(minutes=W // 2)).alias("t_mid")).select(
        "unit", "agent", "pt_date", "win", "project", "t_mid")


def fit_unit(q: pl.DataFrame, owner: dict) -> dict:
    """H94 M2/M3 on one unit's quanta (agent x project counts)."""
    q = q.with_columns(pl.Series("room", [room_of(a, t.timestamp()) for a, t in q.select("agent", "t_mid").iter_rows()],
                                 dtype=pl.Int16))
    agents = sorted(q["agent"].unique().to_list())
    projs = sorted(q["project"].unique().to_list())
    ai = {a: k for k, a in enumerate(agents)}
    pj = {p: k for k, p in enumerate(projs)}
    n = np.zeros((len(agents), len(projs)))
    for a, p in q.select("agent", "project").iter_rows():
        n[ai[a], pj[p]] += 1
    mr = (q.drop_nulls("room").group_by("agent", "room").len().sort("agent", "len", "room", descending=[False, True, False])
          .group_by("agent", maintain_order=True).first())
    room_mode = dict(mr.select("agent", "room").iter_rows())
    t0 = q["t_mid"].min().timestamp()
    own = np.zeros_like(n)
    room = np.zeros_like(n)
    for p, j in pj.items():
        o = owner.get(p)
        if o in ai:
            own[ai[o], j] = 1.0
        orm = room_mode.get(o) if o is not None else None
        if orm is None and o is not None:
            orm = room_of(o, t0)
        for a, i in ai.items():
            if orm is not None and room_mode.get(a) is not None and room_mode[a] == orm:
                room[i, j] = 1.0
    two = len(set(room_mode.values())) > 1
    mu, lam, model = L.maxent_pi(n, own, room, two)
    pi_i = mu / mu.sum(1, keepdims=True)
    pi = mu.sum(0) / mu.sum()
    rows = [(a, p, float(n[i, j]), float(pi_i[i, j]), float(pi[j]), bool(own[i, j]))
            for a, i in ai.items() for p, j in pj.items()]
    return {"rows": rows, "model": model, "two_rooms": two, **lam, "N": float(n.sum()), "A": len(agents), "J": len(projs)}


# ============================================================================================ one period
def build_period(g: int) -> dict:
    days = RH.period_days(g)
    assert not any(holdout_mask(days, [g] * len(days))), "reserved days in exploratory input"
    um = {d: u for d, u in RH.unit_of_day(g).items() if d in set(days)}
    calls = RH.load_calls(g, days)
    ct = call_times(calls, um)
    ub = unit_bounds(g, days)
    wown, wage = work_owner_age()
    smo = strict_mention_owner()
    od = OUT / f"G{g:02d}"
    od.mkdir(parents=True, exist_ok=True)
    counts, fits = {}, {}
    Hw, Vw = work_hops(g, days, calls, um)
    Ha, Va, ps = attention_hops(g, um)
    chans = {"work": (Hw, Vw, work_T(Vw, ct), work_quanta(g, days, um), wown, wage),
             "attention": (Ha, Va, attention_T(ps, ct), attention_quanta(ps),
                           {**smo, **{p: o for p, o in wown.items()}}, attention_age())}
    for ch, (H, V, T, Q, owner, age) in chans.items():
        names = set(H["src"].to_list()) | set(H["dst"].to_list()) | set(V["repo"].to_list()) | set(Q["project"].to_list())
        rank = rank_of(age, names)
        occ_rows, av_rows = [], []
        for u in sorted(set(Q["unit"].to_list()) | set(V["unit"].to_list())):
            if u not in ub:
                continue
            s0, s1, act, wins = ub[u]
            qu = Q.filter(pl.col("unit") == u)
            vu = V.filter(pl.col("unit") == u)
            f = fit_unit(qu, owner) if qu.height and qu["agent"].n_unique() >= 1 else None
            if f is not None:
                fits[f"{u}|{ch}"] = {k: v for k, v in f.items() if k != "rows"}
                for a, p, nq, pii, pp, ow in f["rows"]:
                    occ_rows.append((u, a, p, nq, pii, pp, ow, float(T.get((u, a, p), 0))))
            # availability: [first arrival, last end] (open -> unit end)
            if vu.height:
                avv = vu.with_columns(pl.col("t_end").fill_null(s1)).group_by("repo").agg(
                    pl.col("t_arr").min().alias("a0"), pl.col("t_end").max().alias("a1"))
                for p, a0, a1 in avv.iter_rows():
                    a1 = max(a1, a0)
                    co = (a0 <= s0 + HOUR) and (a1 >= s1 - HOUR)
                    co80 = active_overlap(wins, a0, a1) >= 0.8 * act
                    av_rows.append((u, p, a0, a1, co, co80, rank[p]))
        occ = pl.DataFrame(occ_rows, schema={"unit": pl.String, "agent": pl.Int16, "project": pl.String, "n_quanta": pl.Float32,
                                             "pi_i": pl.Float64, "pi": pl.Float64, "own": pl.Boolean, "T": pl.Float32}, orient="row")
        av = pl.DataFrame(av_rows, schema={"unit": pl.String, "project": pl.String, "a0": pl.Float64, "a1": pl.Float64,
                                           "coalive": pl.Boolean, "coalive80": pl.Boolean, "age_rank": pl.Int32}, orient="row")
        co = {(u, p): c for u, p, c in av.select("unit", "project", "coalive").iter_rows()}
        H2 = H.with_columns(
            pl.Series("src_rank", [rank[x] for x in H["src"].to_list()], dtype=pl.Int32),
            pl.Series("dst_rank", [rank[x] for x in H["dst"].to_list()], dtype=pl.Int32),
            pl.Series("coalive_pair", [bool(co.get((u, s), False) and co.get((u, d), False))
                                       for u, s, d in H.select("unit", "src", "dst").iter_rows()], dtype=pl.Boolean))
        RH.hashed(H2, cols=("src", "dst")).write_parquet(od / f"hops_{ch}.parquet", compression="zstd")
        RH.hashed(occ, cols=("project",)).write_parquet(od / f"occupancy_{ch}.parquet", compression="zstd")
        RH.hashed(av, cols=("project",)).write_parquet(od / f"avail_{ch}.parquet", compression="zstd")
        ag_first = (V.sort("t_arr").group_by("unit", "agent", maintain_order=True).first()
                    .select("unit", "agent", pl.col("repo").alias("first_project"), pl.col("t_arr").alias("t_first")))
        RH.hashed(ag_first, cols=("first_project",)).write_parquet(od / f"first_{ch}.parquet", compression="zstd")
        for u in sorted(set(H2["unit"].to_list()) | set(av["unit"].to_list())):
            hu = H2.filter(pl.col("unit") == u)
            cu = hu.filter(pl.col("coalive_pair"))
            pc = cu.with_columns(pl.min_horizontal("src_rank", "dst_rank").alias("lo"), pl.max_horizontal("src_rank", "dst_rank").alias("hi")
                                 ).group_by("lo", "hi").len()
            counts[f"{u}|{ch}"] = {"hops": hu.height, "coalive_projects": int(av.filter((pl.col("unit") == u) & pl.col("coalive")).height),
                                   "projects": int(av.filter(pl.col("unit") == u).height), "coalive_hops": cu.height,
                                   "pairs_ge4": int((pc["len"] >= 4).sum()) if pc.height else 0,
                                   "testable": bool(cu.height >= 60 and (pc.height and int((pc["len"] >= 4).sum()) >= 8))}
    # calls per unit (own-call clock) for the walker
    rows = [(u, a, t) for (u, a), tc in ct.items() for t in tc]
    pl.DataFrame(rows, schema={"unit": pl.String, "agent": pl.Int16, "t": pl.Float64}, orient="row").write_parquet(
        od / "calls.parquet", compression="zstd")
    (od / "counts.json").write_text(json.dumps({"counts": counts, "fits": fits}, indent=1, default=float))
    # whole-period hops (H129's unit rule outside #51) for the read-only cross-check
    if g != 51:
        uw = {d: f"G{g:02d}" for d in days}
        Hw_c, _ = work_hops(g, days, calls, uw)
        Ha_c, _, _ = attention_hops(g, uw)
    else:
        Hw_c, Ha_c = Hw, Ha
    return {"counts": counts, "fits": fits, "Hw": Hw_c, "Ha": Ha_c, "Q": chans["work"][3], "wown": wown}


def cross_check(g: int, res: dict) -> dict:
    """Read-only comparison with H129's hops (whole period outside #51: compare multisets of (agent, src, dst)) and
    H94's quanta (agent, pt_date, win, repo; owner)."""
    out = {}
    for ch, H in (("work", res["Hw"]), ("attention", res["Ha"])):
        f = H129 / f"G{g:02d}" / f"hops_{ch}.parquet"
        if not f.exists():
            continue
        old = pl.read_parquet(f)
        new = RH.hashed(H, cols=("src", "dst"))
        k_old = sorted((int(a), s, d) for a, s, d in old.select("agent", "src", "dst").iter_rows())
        k_new = sorted((int(a), s, d) for a, s, d in new.select("agent", "src", "dst").iter_rows())
        so, sn = {}, {}
        for k in k_old:
            so[k] = so.get(k, 0) + 1
        for k in k_new:
            sn[k] = sn.get(k, 0) + 1
        common = sum(min(v, sn.get(k, 0)) for k, v in so.items())
        out[ch] = {"h129_hops": len(k_old), "h135_hops": len(k_new), "common": common}
    f = H94 / f"G{g:02d}" / "quanta.parquet"
    if f.exists():
        old = pl.read_parquet(f)
        q = RH.hashed(res["Q"].rename({"project": "repo"}), cols=("repo",))
        ko = set(old.select("agent", "pt_date", "win", "repo").iter_rows())
        kn = set((int(a), d, int(w), r) for a, d, w, r in q.select("agent", "pt_date", "win", "repo").iter_rows())
        ko = set((int(a), d, int(w), r) for a, d, w, r in ko)
        own_old = dict(old.select("repo", "owner").unique(subset="repo").iter_rows())
        own_new = {RH.rhash(r): o for r, o in res["wown"].items()}
        mism = sum(1 for r, o in own_old.items() if o is not None and own_new.get(r) is not None and int(own_new[r]) != int(o))
        out["quanta"] = {"h94": len(ko), "h135": len(kn), "common": len(ko & kn), "owner_mismatch_repos": mism,
                         "repos": len(own_old)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    a = ap.parse_args()
    periods = a.period or GOALS
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    checks = json.loads((OUT / "check.json").read_text()) if (OUT / "check.json").exists() else {}
    for g in periods:
        res = build_period(g)
        checks[f"G{g:02d}"] = cross_check(g, res)
        print(f"G{g:02d} {time.time() - t0:.0f}s check {json.dumps(checks[f'G{g:02d}'])}", flush=True)
        (OUT / "check.json").write_text(json.dumps(checks, indent=1))
    prov = {"built_by": "hypotheses/H135-detailed-balance-potts-walker/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["work_commits", "call_windows", "calendar", "period_units", "roster", "project_states",
                                   "artifact_mentions", "artifacts", "rooms_timeline"]}],
            "params": {"host_labels": "replicator_hosts W=30 E=100", "attention": "project_states w_min=30 sources=all, non-reserved",
                       "pi": "H94 M2 (M3 in two-room units) by IPF per period unit", "owner": "earliest non-reserved agent work commit; "
                       "attention: else earliest strict mention", "coalive": "first arrival <= unit start + 1 h, last end >= unit end - 1 h; "
                       "variant >= 80% of active seconds", "units": "period_units unit_id"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "periods_built": sorted(int(k[1:]) for k in checks)}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"built in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
