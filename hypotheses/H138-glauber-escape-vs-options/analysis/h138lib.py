"""H138 library: per (agent, 30-min window) leave panels for the work and attention channels, the open-option counts
(q_live, q_cum, q_room, q_read, q_named / q_free, q_lead), the cross-fitted Glauber alternative sum Z_alt, the Poisson
hazard per own call with agent fixed effects and an agent-cluster sandwich, the natural spline in active time, a small
conditional logit, the DerSimonian-Laird pool, and the synthetic worlds W0-W4 on the real skeleton.

Codes only: repo/project names stay in memory; the scheme hashes them on output. Reserved days are never read
(replicator_hosts.period_days and the project_states / ledger holdout flags; asserted again in build()).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import datetime as dt  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import replicator_hosts as RH  # noqa: E402
from common import OUT as SHARED, holdout_mask  # noqa: E402

D = ROOT / "data/processed/H138-glauber-escape-vs-options"
W_MIN = 30
L_WIN = 4          # lookback / lead in windows (2 active hours)
E_EXP = 100        # call-clock expiry (own calls)
CLAUDE_CODE = 19
WORK_GOALS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
ATT_GOALS = [18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
OWN_ROLE = {39, 42, 44, 51}
MIN_LEAVES = 25


# ============================================================================================ units and windows
@lru_cache(maxsize=1)
def calendar() -> pl.DataFrame:
    c = pl.read_parquet(SHARED / "calendar.parquet", columns=["pt_date", "goal_no", "win_start", "win_end", "window_s",
                                                               "n_agent_events"])
    c = c.filter(pl.col("n_agent_events") > 0)
    ho = holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())
    return c.with_columns(pl.Series("ho", ho)).filter(~pl.col("ho")).sort("pt_date")


def unit_days(goal: int) -> dict[str, list[str]]:
    """Analysis units of a goal period (non-reserved days): #51 by period_units (51a-51l); #36 split at the 2026-03-24
    regime boundary (36a | 36bc); every other period whole."""
    days = sorted(calendar().filter(pl.col("goal_no") == goal)["pt_date"].to_list())
    if goal == 51:
        um = RH.unit_of_day(51)
        out = defaultdict(list)
        for d in days:
            if d in um:
                out[um[d]].append(d)
        return dict(sorted(out.items()))
    if goal == 36:
        return {"36a": [d for d in days if d < "2026-03-24"], "36bc": [d for d in days if d >= "2026-03-24"]}
    return {f"{goal:02d}": days}


class Grid:
    """The unit's 30-min windows: g = 0..G-1 over its days, in order (active time)."""

    def __init__(self, days: list[str]):
        cal = calendar().filter(pl.col("pt_date").is_in(days)).sort("pt_date")
        self.days = cal["pt_date"].to_list()
        t0s, dayi, wins = [], [], []
        for k, (ws, we) in enumerate(zip(cal["win_start"].to_list(), cal["win_end"].to_list())):
            n = max(1, int(math.ceil((we - ws).total_seconds() / (W_MIN * 60))))
            for w in range(n):
                t0s.append(ws.timestamp() + w * W_MIN * 60)
                dayi.append(k)
                wins.append(w)
        self.t0 = np.array(t0s)
        self.t1 = self.t0 + W_MIN * 60
        # the last window of each day ends at win_end (clip)
        ends = {k: we.timestamp() for k, we in enumerate(cal["win_end"].to_list())}
        for i, k in enumerate(dayi):
            if i == len(dayi) - 1 or dayi[i + 1] != k:
                self.t1[i] = max(ends[k], self.t0[i] + 60)
        self.day = np.array(dayi, dtype=np.int16)
        self.win = np.array(wins, dtype=np.int16)
        self.G = len(t0s)
        self.ws = {d: ws.timestamp() for d, ws in zip(self.days, cal["win_start"].to_list())}

    def g_of(self, ts: np.ndarray) -> np.ndarray:
        """Window index of unix times (−1 if outside every window of the unit)."""
        ts = np.asarray(ts, float)
        i = np.searchsorted(self.t0, ts, side="right") - 1
        ok = (i >= 0) & (ts < self.t1[np.clip(i, 0, self.G - 1)])
        return np.where(ok, i, -1)


def unix(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(float) / 1e6


# ============================================================================================ visits
def work_visits(goal: int) -> dict:
    """Host replay of the whole period (shared code, non-reserved days): visits (agent, project, t_arr, t_end, end) with
    end in {depart, censor}; plus calls and commits."""
    days = RH.period_days(goal)
    calls = RH.load_calls(goal, days)
    commits = RH.load_commits(goal, days)
    leave = RH.leave_times(goal, calls, days)
    lab = RH.window_labels(commits, W_MIN)
    ev = RH.replay_events(lab, calls, E=E_EXP, leave_t=leave)
    rows = []
    for (a,), g in ev.sort("t").group_by(["agent"], maintain_order=True):
        cur = None
        for kind, repo, t in g.select("kind", "repo", "t").iter_rows():
            ts = t.timestamp()
            if kind == "arrive":
                cur = [int(a), repo, ts]
            elif kind in ("depart", "expire", "leave"):
                if cur is not None and cur[1] == repo:
                    rows.append((*cur, ts, "depart" if kind == "depart" else "censor"))
                    cur = None
        if cur is not None:
            rows.append((*cur, np.inf, "censor"))
    V = pl.DataFrame(rows, schema={"agent": pl.Int16, "project": pl.String, "t_arr": pl.Float64, "t_end": pl.Float64,
                                   "end": pl.String}, orient="row")
    return {"visits": V, "calls": calls, "commits": commits, "days": days}


@lru_cache(maxsize=1)
def attention_rows_all() -> pl.DataFrame:
    ps = (pl.scan_parquet(SHARED / "project_states.parquet")
          .filter((pl.col("w_min") == W_MIN) & (pl.col("sources").cast(pl.String) == "all") & ~pl.col("holdout"))
          .select("goal_no", "pt_date", "win", "agent", "room", pl.col("project").cast(pl.String)).collect())
    return ps.filter(pl.col("agent") != CLAUDE_CODE)


def attention_visits(goal: int) -> dict:
    """Attention labels (project_states W 30, sources all, strict mentions) carried forward with the same call-clock
    expiry (E own calls without a labelled window on the project). A leave is a labelled window on b != a with no
    expiry in between; the leave sits in that window (t_end = its end - 1 s) and the new visit starts at its end."""
    days = sorted(calendar().filter(pl.col("goal_no") == goal)["pt_date"].to_list())
    ps = attention_rows_all().filter((pl.col("goal_no") == goal) & pl.col("pt_date").is_in(days))
    calls = (pl.scan_parquet(SHARED / "call_windows.parquet")
             .filter((pl.col("goal_no") == goal) & pl.col("pt_date").is_in(days) & (pl.col("agent") != CLAUDE_CODE)
                     & ~pl.col("holdout"))
             .select("turn_id", "agent", "t_call", "pt_date").collect().sort("t_call", "agent"))
    leave = RH.leave_times(goal, calls, days) if days else {}
    ws = {d: s.timestamp() for d, s in zip(calendar()["pt_date"].to_list(), calendar()["win_start"].to_list())}
    ps = ps.with_columns(pl.struct("pt_date", "win").map_elements(lambda r: ws[r["pt_date"]] + r["win"] * W_MIN * 60,
                                                                   return_dtype=pl.Float64).alias("tw0"))
    ct = {int(a): np.sort(unix(g["t_call"])) for (a,), g in calls.group_by(["agent"])}
    rows = []
    for (a,), g in ps.sort("tw0").group_by(["agent"], maintain_order=True):
        a = int(a)
        tc = ct.get(a, np.array([]))
        cur, last = None, None   # cur = [agent, project, t_arr]; last = end of the last renewal window

        def expiry(t_next):
            if cur is None or len(tc) == 0:
                return None
            i0 = np.searchsorted(tc, last, side="right")
            k = i0 + E_EXP - 1
            if k < len(tc) and tc[k] < t_next:
                return tc[k]
            return None

        for p, tw0 in g.select("project", "tw0").iter_rows():
            tw1 = tw0 + W_MIN * 60
            te = expiry(tw0)
            if te is not None:
                rows.append((*cur, float(te), "censor"))
                cur = None
            if cur is not None and cur[1] == p:
                last = tw1
                continue
            if cur is not None:
                rows.append((*cur, tw1 - 1.0, "depart"))
            cur, last = [a, p, tw1], tw1
        lt = leave.get(a)
        lt = lt.timestamp() if lt is not None else np.inf
        te = expiry(lt)
        if te is not None:
            rows.append((*cur, float(te), "censor"))
            cur = None
        if cur is not None:
            rows.append((*cur, lt, "censor"))
    V = pl.DataFrame(rows, schema={"agent": pl.Int16, "project": pl.String, "t_arr": pl.Float64, "t_end": pl.Float64,
                                   "end": pl.String}, orient="row")
    return {"visits": V, "calls": calls, "labels": ps, "days": days}


# ============================================================================================ ownership, rooms, reads
@lru_cache(maxsize=1)
def owners() -> dict:
    """H94 owner rule: the agent with the earliest agent work commit to the repo (DQ4 default filter; non-reserved rows
    only, so a repo first committed on a reserved day gets its first non-reserved author)."""
    c = (pl.scan_parquet(SHARED / "work_commits.parquet")
         .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent")
                 & ~pl.col("automated") & pl.col("author_agent").is_not_null() & (pl.col("author_agent") != CLAUDE_CODE))
         .select(pl.col("repo").cast(pl.String), "t", "pt_date", "goal_no", "author_agent").collect())
    c = c.filter(~pl.Series(holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())))
    f = c.sort("t").group_by("repo", maintain_order=True).first()
    return {r: int(a) for r, a in f.select("repo", "author_agent").iter_rows()}


@lru_cache(maxsize=1)
def rooms_tl() -> pl.DataFrame:
    rt = pl.read_parquet(SHARED / "rooms_timeline.parquet")
    return rt.with_columns(pl.col("t_end").fill_null(dt.datetime(2100, 1, 1, tzinfo=dt.timezone.utc)))


def room_matrix(agents: list[int], grid: Grid) -> np.ndarray:
    """Room of each agent at each window midpoint (-1 = none)."""
    rt = rooms_tl().filter(pl.col("agent").is_in(agents))
    tm = (grid.t0 + grid.t1) / 2
    R = np.full((len(agents), grid.G), -1, dtype=np.int16)
    ai = {a: k for k, a in enumerate(agents)}
    for a, room, ts, te in rt.select("agent", "room", "t_start", "t_end").sort("t_start").iter_rows():
        k = ai[int(a)]
        m = (tm >= ts.timestamp()) & (tm < te.timestamp())
        R[k, m] = room
    return R


@lru_cache(maxsize=1)
def chat_project_mentions() -> pl.DataFrame:
    pm = pl.read_parquet(SHARED / "project_mentions_chat.parquet").filter(~pl.col("holdout") & pl.col("agent").is_not_null())
    return pm.select("message_id", pl.col("agent").cast(pl.Int16).alias("sender"), "project").unique()


def read_projects(goal: int, days: list[str]) -> pl.DataFrame:
    """(agent, t_call, project): strict project mentions in other agents' chat items that entered the agent's call."""
    pm = chat_project_mentions()
    turns = (pl.scan_parquet(SHARED / "context_ledger_turns.parquet")
             .filter((pl.col("goal_no") == goal) & pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
             .select("turn_id", pl.col("agent").cast(pl.Int16), "t_call").collect())
    items = (pl.scan_parquet(SHARED / "context_ledger_items.parquet")
             .filter(pl.col("message_id").is_in(pm["message_id"].unique().implode()) & pl.col("turn_id").is_in(turns["turn_id"].implode()))
             .select("turn_id", "message_id").collect())
    d = items.join(turns, on="turn_id").join(pm, on="message_id")
    return d.filter(pl.col("sender") != pl.col("agent")).select("agent", "t_call", "project")


# ============================================================================================ panel
def build_unit_panel(unit: str, days: list[str], V: pl.DataFrame, calls: pl.DataFrame, goal: int, channel: str,
                     named: dict, own_mark: dict | None, reads: pl.DataFrame | None) -> tuple[pl.DataFrame, dict]:
    """Rows: one per (agent, window, visit) at risk. Columns as in the card's scheme (names kept in memory)."""
    grid = Grid(days)
    G = grid.G
    lo, hi = grid.t0[0], grid.t1[-1]
    v = V.filter((pl.col("t_arr") < hi) & (pl.col("t_end") > lo))
    agents = sorted(set(v["agent"].to_list()) | set(int(a) for a in calls.filter(pl.col("pt_date").is_in(days))["agent"].unique().to_list()))
    ai = {a: k for k, a in enumerate(agents)}
    projects = sorted(set(v["project"].to_list()))
    pi = {p: k for k, p in enumerate(projects)}
    P = len(projects)
    ct = {}
    for (a,), g in calls.group_by(["agent"]):
        ct[int(a)] = np.sort(unix(g["t_call"]))
    # held-during-window cube H[a, g, p]
    H = np.zeros((len(agents), G, max(P, 1)), dtype=bool)
    vis = v.select("agent", "project", "t_arr", "t_end", "end").rows()
    for a, p, ta, te, _ in vis:
        g0 = np.searchsorted(grid.t1, ta, side="right")          # first window whose end is after ta
        g1 = np.searchsorted(grid.t0, te, side="left") - 1         # last window starting before te
        if g1 >= g0:
            H[ai[a], g0:g1 + 1, pi[p]] = True
    Hc = H.astype(np.int32)
    tot = Hc.sum(0)                                                # G x P (agents holding p in g)
    cum_tot = np.vstack([np.zeros((1, P), np.int32), np.cumsum(tot, 0)])          # (G+1) x P, windows before g
    cum_ag = np.concatenate([np.zeros((len(agents), 1, P), np.int32), np.cumsum(Hc, 1)], axis=1)
    first_g = np.full(P, G, dtype=np.int64)
    anyh = tot > 0
    for k in range(P):
        nz = np.flatnonzero(anyh[:, k])
        if len(nz):
            first_g[k] = nz[0]
    births = np.bincount(first_g[(first_g < G) & (first_g > 0)], minlength=G)   # g = 0 holds carried-over labels
    named_v = np.array([bool(named.get(p, False)) for p in projects]) if P else np.zeros(0, bool)
    rooms = room_matrix(agents, grid)
    n_active = np.zeros(G, dtype=np.int16)
    calls_ag = np.zeros((len(agents), G), dtype=np.int32)
    for a, tc in ct.items():
        if a not in ai:
            continue
        gg = grid.g_of(tc)
        gg = gg[gg >= 0]
        calls_ag[ai[a]] = np.bincount(gg, minlength=G)
    n_active = (calls_ag > 0).sum(0).astype(np.int16)
    # reads: per agent, per window, the set of projects read
    read_sets = defaultdict(set)
    if reads is not None and reads.height:
        rr = reads.filter(pl.col("agent").is_in(agents))
        gg = grid.g_of(unix(rr["t_call"]))
        for a, g, p in zip(rr["agent"].to_list(), gg.tolist(), rr["project"].to_list()):
            if g >= 0:
                read_sets[(int(a), g)].add(p)
    # target of each direct leave: the agent's next visit (starts at the leave time)
    nxt = {}
    by_a = defaultdict(list)
    for vid, (a, p, ta, te, end) in enumerate(vis):
        by_a[a].append((ta, vid, p))
    for a in by_a:
        by_a[a].sort()
    for vid, (a, p, ta, te, end) in enumerate(vis):
        if end != "depart":
            continue
        for tb, vb, pb in by_a[a]:
            if tb >= te - 1e-6 and vb != vid and pb != p:
                nxt[vid] = pb
                break
    # own mark in previous window (work: own commit on a; attention: own labelled window on a)
    rows = []
    for vid, (a, p, ta, te, end) in enumerate(vis):
        k_a, k_p = ai[a], pi[p]
        tc = ct.get(a, np.array([]))
        g0 = max(0, int(np.searchsorted(grid.t1, ta, side="right")))
        g1 = min(G - 1, int(np.searchsorted(grid.t0, te, side="left") - 1))
        for g in range(g0, g1 + 1):
            s = max(ta, grid.t0[g])
            e = min(te, grid.t1[g])
            n_calls = int(np.searchsorted(tc, e, side="right") - np.searchsorted(tc, s, side="right"))
            leave = int(end == "depart" and grid.t0[g] <= te < grid.t1[g])
            dwell = int(np.searchsorted(tc, s, side="right") - np.searchsorted(tc, ta, side="right"))
            lb0 = max(0, g - L_WIN)
            # others' held windows in the lookback, per project
            look = (cum_tot[g] - cum_tot[lb0]) - (cum_ag[k_a, g] - cum_ag[k_a, lb0])
            live = look > 0
            live[k_p] = False
            q_live = int(live.sum())
            a_a = int(look[k_p])
            # lead: projects first held in (g, g+L]
            lead = (first_g > g) & (first_g <= g + L_WIN)
            lead[k_p] = False
            q_lead = int(lead.sum())
            cum_set = first_g < g
            cum_set[k_p] = False
            q_cum = int(cum_set.sum())
            # room menu: others in i's room (at window g) holding b in the lookback
            r_i = rooms[k_a, g]
            if r_i >= 0 and g > lb0:
                same = (rooms[:, lb0:g] == r_i)                     # agents x L
                same[k_a] = False
                hr = (H[:, lb0:g, :] & same[:, :, None]).any(axis=(0, 1))
                hr[k_p] = False
                q_room = int(hr.sum())
            else:
                q_room = 0
            rs = set()
            for gg in range(lb0, g):
                rs |= read_sets.get((a, gg), set())
            rs.discard(p)
            q_read = len(rs)
            q_named = int((live & named_v).sum())
            own_prev = int(own_mark is not None and g > 0 and (a, g - 1, p) in own_mark)
            owner = int(owners().get(p) == a)
            B = int(births[max(0, g - 2):g + 3].sum())
            to_new = -1
            if leave and vid in nxt:
                fb = first_g[pi[nxt[vid]]]
                to_new = int(0 < fb and g - L_WIN <= fb <= g)
            rows.append((unit, a, vid, k_p, g, int(grid.day[g]), int(n_calls), leave, q_live, q_cum, q_room, q_read,
                         q_named, q_live - q_named, q_lead, a_a, dwell, own_prev, owner, int(r_i), int(n_active[g]), B,
                         to_new))
    cols = {"unit": pl.String, "agent": pl.Int16, "visit": pl.Int32, "proj": pl.Int32, "g": pl.Int32, "day": pl.Int16,
            "calls": pl.Int32, "leave": pl.Int8, "q_live": pl.Int32, "q_cum": pl.Int32, "q_room": pl.Int32,
            "q_read": pl.Int32, "q_named": pl.Int32, "q_free": pl.Int32, "q_lead": pl.Int32, "a_a": pl.Int32,
            "dwell": pl.Int32, "own_prev": pl.Int8, "owner": pl.Int8, "room": pl.Int16, "n_active": pl.Int16,
            "births_pm2": pl.Int32, "to_new": pl.Int8}
    df = pl.DataFrame(rows, schema=cols, orient="row")
    ctx = {"grid": grid, "projects": projects, "agents": agents, "H": H, "cum_tot": cum_tot, "cum_ag": cum_ag,
           "first_g": first_g, "births": births, "vis": vis, "ai": ai, "pi": pi, "calls_ag": calls_ag}
    return df, ctx


# ============================================================================================ joins and Z_alt
def joins_table(ctx: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Recruit joins (a visit starting on a project held earlier in the unit, after a previous visit of the agent):
    returns X (rows: candidates), gid, y, day of the join."""
    grid, vis, ai, pi = ctx["grid"], ctx["vis"], ctx["ai"], ctx["pi"]
    cum_tot, cum_ag, first_g = ctx["cum_tot"], ctx["cum_ag"], ctx["first_g"]
    G = grid.G
    by_agent = defaultdict(list)
    for a, p, ta, te, end in vis:
        by_agent[a].append((ta, p))
    Xs, gids, ys, jday = [], [], [], []
    jid = 0
    for a, lst in by_agent.items():
        lst.sort()
        for (t_prev, p_prev), (ta, p) in zip(lst[:-1], lst[1:]):
            g = int(grid.g_of(np.array([ta]))[0])
            if g < 0:
                g = int(np.searchsorted(grid.t0, ta, side="right") - 1)
                if g < 0 or g >= G:
                    continue
            kp = pi[p]
            if first_g[kp] >= g:
                continue   # birth, not a recruit
            cand = np.flatnonzero(first_g < g)
            cand = cand[cand != pi[p_prev]]
            if len(cand) < 2 or kp not in set(cand.tolist()):
                continue
            X = feats(ctx, ai[a], g, cand)
            Xs.append(X)
            gids.append(np.full(len(cand), jid))
            ys.append((cand == kp).astype(float))
            jday.append(int(grid.day[g]))
            jid += 1
    if not Xs:
        return np.zeros((0, 4)), np.zeros(0, int), np.zeros(0), np.zeros(0, int)
    return np.vstack(Xs), np.concatenate(gids), np.concatenate(ys), np.array(jday)


def feats(ctx, k_a, g, cand) -> np.ndarray:
    """H11 round-2 join features: [log a_b * (a_b > 0), (a_b == 0), log(1 + s_b), h_b] for candidates at window g."""
    cum_tot, cum_ag = ctx["cum_tot"], ctx["cum_ag"]
    lb0 = max(0, g - L_WIN)
    a_b = ((cum_tot[g] - cum_tot[lb0]) - (cum_ag[k_a, g] - cum_ag[k_a, lb0]))[cand].astype(float)
    s_b = (cum_tot[g] - cum_ag[k_a, g])[cand].astype(float)
    h_b = (cum_ag[k_a, g][cand] > 0).astype(float)
    return np.c_[np.where(a_b > 0, np.log(np.maximum(a_b, 1)), 0.0), (a_b == 0).astype(float), np.log1p(s_b), h_b]


def clogit(X, gid, y, ridge=0.5, max_iter=100):
    """Conditional logit with an L2 penalty (Known issue: quasi-separation; H11 r2 used L2 0.5), damped Newton with
    step halving on the penalized log-likelihood. gid sorted."""
    n, k = X.shape
    b = np.zeros(k)
    if n == 0:
        return b
    st = np.flatnonzero(np.r_[True, gid[1:] != gid[:-1]])
    cnt = np.diff(np.r_[st, n])

    def pll(bb):
        eta = X @ bb
        m = np.maximum.reduceat(eta, st)
        lse = m + np.log(np.add.reduceat(np.exp(eta - np.repeat(m, cnt)), st))
        return float((y * eta).sum() - lse.sum()) - 0.5 * ridge * float(bb @ bb)

    cur = pll(b)
    for _ in range(max_iter):
        eta = X @ b
        m = np.repeat(np.maximum.reduceat(eta, st), cnt)
        e = np.exp(eta - m)
        s = np.repeat(np.add.reduceat(e, st), cnt)
        p = e / s
        xbar = np.add.reduceat(p[:, None] * X, st, axis=0)
        grad = (y[:, None] * X).sum(0) - xbar.sum(0) - ridge * b
        Xc = X - np.repeat(xbar, cnt, axis=0)
        Hm = (Xc * p[:, None]).T @ Xc + ridge * np.eye(k)
        step = np.linalg.solve(Hm, grad)
        t = 1.0
        while t > 1e-6:
            bn = b + t * step
            new = pll(bn)
            if new >= cur - 1e-12:
                break
            t /= 2
        if t <= 1e-6:
            break
        b, done = bn, abs(new - cur) < 1e-10
        cur = new
        if done:
            break
    return b


def add_zalt(df: pl.DataFrame, ctx: dict) -> tuple[pl.DataFrame, dict]:
    """Z_alt per row with utilities from the join model cross-fitted by day folds (joins of day d never enter the
    utilities used on day d)."""
    X, gid, y, jday = joins_table(ctx)
    jd_rows = np.repeat(jday, np.diff(np.r_[np.flatnonzero(np.r_[True, gid[1:] != gid[:-1]]), len(gid)])) if len(gid) else np.zeros(0, int)
    betas = {}
    full = clogit(X, gid, y) if len(gid) else np.zeros(4)
    days = sorted(set(df["day"].to_list()))
    for d in days:
        m = jd_rows != d
        if m.sum() and len(np.unique(gid[m])) >= 5:
            g2 = gid[m]
            betas[d] = clogit(X[m], g2, y[m])
        else:
            betas[d] = np.zeros(4)
    first_g = ctx["first_g"]
    ai = ctx["ai"]
    z = np.zeros(df.height)
    has = np.zeros(df.height, bool)
    for r, (a, kp, g, d) in enumerate(df.select("agent", "proj", "g", "day").iter_rows()):
        cand = np.flatnonzero(first_g < g)
        cand = cand[cand != kp]
        if len(cand) == 0:
            continue
        u = feats(ctx, ai[a], g, cand) @ betas[d]
        mx = u.max()
        z[r] = float(mx + np.log(np.exp(u - mx).sum()))
        has[r] = True
    info = {"n_joins": int(len(np.unique(gid))) if len(gid) else 0, "beta_full": full.tolist(),
            "names": ["alpha_loga", "beta0_zero", "gamma_logsize", "eta_habit"]}
    info["beta_folds"] = {int(k): v.tolist() for k, v in betas.items()}
    return df.with_columns(pl.Series("lnZ_alt", z), pl.Series("Z_any", has)), info


# ============================================================================================ hazard model
def ns_basis(x: np.ndarray, df: int = 3, knots: np.ndarray | None = None, bounds=None):
    """Natural cubic spline basis (df columns, no intercept): boundary knots at min/max, df-1 interior knots at
    quantiles (Hastie-Tibshirani truncated-power form)."""
    x = np.asarray(x, float)
    if bounds is None:
        bounds = (x.min(), x.max())
    if knots is None:
        knots = np.quantile(x, np.linspace(0, 1, df + 1)[1:-1]) if df > 1 else np.array([])
    kk = np.r_[bounds[0], knots, bounds[1]]
    K = len(kk)
    if bounds[1] <= bounds[0] or K < 3:
        return (x - x.mean())[:, None] / (x.std() + 1e-9), knots, bounds
    xs = (x - bounds[0]) / (bounds[1] - bounds[0])
    ks = (kk - bounds[0]) / (bounds[1] - bounds[0])

    def d(k):
        return (np.maximum(xs - ks[k], 0) ** 3 - np.maximum(xs - ks[K - 1], 0) ** 3) / (ks[K - 1] - ks[k])
    cols = [xs]
    for k in range(K - 2):
        cols.append(d(k) - d(K - 2))
    B = np.column_stack(cols)
    return B, knots, bounds


def poisson_fe(y, X, off, agent, maxit=80, tol=1e-9, ridge=1e-6):
    """Poisson GLM log mu = X b + alpha_agent + off by Newton with agent dummies; agents with no event are dropped by
    the caller. Returns b (X part), the agent-cluster sandwich cov (G/(G-1) factor), model cov, ll, alphas."""
    lev, inv = np.unique(agent, return_inverse=True)
    Gc = len(lev)
    n, k = X.shape
    Dm = np.zeros((n, Gc))
    Dm[np.arange(n), inv] = 1.0
    Z = np.hstack([X, Dm])
    p = Z.shape[1]
    rate = max(y.sum(), 0.5) / np.exp(off).sum()
    beta = np.zeros(p)
    beta[k:] = np.log(rate)
    R = np.r_[np.full(k, ridge), np.zeros(Gc)]
    ll_old = -np.inf
    for _ in range(maxit):
        eta = Z @ beta + off
        mu = np.exp(np.clip(eta, -50, 30))
        ll = float((y * eta - mu).sum())
        grad = Z.T @ (y - mu) - R * beta
        Hm = (Z * mu[:, None]).T @ Z + np.diag(R)
        try:
            step = np.linalg.solve(Hm, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(Hm, grad, rcond=None)[0]
        t = 1.0
        while t > 1e-4:
            bn = beta + t * step
            en = Z @ bn + off
            lln = float((y * en - np.exp(np.clip(en, -50, 30))).sum()) - 0.5 * float((R * bn * bn).sum())
            if lln >= ll - 0.5 * float((R * beta * beta).sum()) - 1e-9:
                break
            t /= 2
        beta = bn
        if np.max(np.abs(t * step)) < tol or abs(lln - ll_old) < tol:
            break
        ll_old = lln
    eta = Z @ beta + off
    mu = np.exp(np.clip(eta, -50, 30))
    Hm = (Z * mu[:, None]).T @ Z + np.diag(R)
    Hinv = np.linalg.pinv(Hm)
    sc = Z * (y - mu)[:, None]
    S = np.zeros((Gc, p))
    np.add.at(S, inv, sc)
    meat = S.T @ S * (Gc / max(Gc - 1, 1))
    cov = Hinv @ meat @ Hinv
    return {"b": beta[:k], "cov": cov[:k, :k], "cov_model": Hinv[:k, :k], "ll": float((y * eta - mu).sum()),
            "alpha": dict(zip(lev.tolist(), beta[k:].tolist())), "G": Gc, "beta_full": beta, "levels": lev}


def cloglog_fe(y, X, off, agent, maxit=100, tol=1e-9, ridge=1e-6):
    """Binary complementary log-log hazard per window, P(leave) = 1 - exp(-exp(X b + alpha_agent + off)), off =
    ln(own calls): the per-call hazard model that the card names as equivalent to the Poisson form; it does not
    saturate when a window holds many calls. Fisher scoring with step halving; agent-cluster sandwich (G/(G-1))."""
    lev, inv = np.unique(agent, return_inverse=True)
    Gc = len(lev)
    n, k = X.shape
    Dm = np.zeros((n, Gc))
    Dm[np.arange(n), inv] = 1.0
    Z = np.hstack([X, Dm])
    p = Z.shape[1]
    beta = np.zeros(p)
    beta[k:] = np.log(max(y.mean(), 1e-4) / np.exp(off).mean())
    R = np.r_[np.full(k, ridge), np.zeros(Gc)]

    def parts(bb):
        eta = np.clip(Z @ bb + off, -30, 5)
        e = np.exp(eta)
        S = np.exp(-e)                       # survival of the window
        mu = np.clip(1 - S, 1e-12, 1 - 1e-12)
        ll = float((y * np.log(mu) + (1 - y) * (-e)).sum()) - 0.5 * float((R * bb * bb).sum())
        dmu = e * S
        u = y * dmu / mu - (1 - y) * e       # d ll / d eta
        w = dmu ** 2 / (mu * (1 - mu))       # Fisher weight
        return ll, u, w

    ll, u, w = parts(beta)
    for _ in range(maxit):
        grad = Z.T @ u - R * beta
        Hm = (Z * w[:, None]).T @ Z + np.diag(R)
        try:
            step = np.linalg.solve(Hm, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(Hm, grad, rcond=None)[0]
        t = 1.0
        while t > 1e-5:
            bn = beta + t * step
            lln, un, wn = parts(bn)
            if lln >= ll - 1e-10:
                break
            t /= 2
        done = abs(lln - ll) < tol
        beta, ll, u, w = bn, lln, un, wn
        if done:
            break
    Hm = (Z * w[:, None]).T @ Z + np.diag(R)
    Hinv = np.linalg.pinv(Hm)
    S = np.zeros((Gc, p))
    np.add.at(S, inv, Z * u[:, None])
    meat = S.T @ S * (Gc / max(Gc - 1, 1))
    cov = Hinv @ meat @ Hinv
    eta = Z @ beta + off
    return {"b": beta[:k], "cov": cov[:k, :k], "cov_model": Hinv[:k, :k], "ll": ll,
            "alpha": dict(zip(lev.tolist(), beta[k:].tolist())), "G": Gc, "beta_full": beta, "levels": lev}


def ll_rows(r: dict, X, off, agent, y, link="cloglog") -> np.ndarray:
    """Per-row log-likelihood of a fitted model on new rows (agents unseen in the fit -> nan)."""
    al = np.array([r["alpha"].get(int(a), np.nan) for a in agent])
    eta = X @ r["b"] + al + off
    if link == "cloglog":
        e = np.exp(np.clip(eta, -30, 5))
        mu = np.clip(1 - np.exp(-e), 1e-12, 1 - 1e-12)
        return y * np.log(mu) + (1 - y) * (-e)
    mu = np.exp(eta)
    return y * eta - mu


TERMS = {
    "O1": ["lnq", "q0"],
    "O2": ["lnZ", "Z0"],
    "O3": ["lnq", "q0", "lnlead"],
}
STAY = ["lndwell", "lnaa", "own_prev", "owner"]


def design(df: pl.DataFrame, model: str = "O1", qcol: str = "q_live", spline_df: int = 3, knots=None, bounds=None,
           extra: list[str] | None = None):
    q = df[qcol].to_numpy().astype(float)
    cols, names = [], []
    if model in ("O1", "O3"):
        cols += [np.where(q > 0, np.log(np.maximum(q, 1)), 0.0), (q == 0).astype(float)]
        names += ["lnq", "q0"]
    elif model == "O2":
        has = df["Z_any"].to_numpy()
        cols += [np.where(has, df["lnZ_alt"].to_numpy().astype(float), 0.0), (~has).astype(float)]
        names += ["lnZ", "Z0"]
    if model == "O3":
        cols.append(np.log1p(df["q_lead"].to_numpy().astype(float)))
        names.append("lnlead")
    cols += [np.log1p(df["dwell"].to_numpy().astype(float)), np.log1p(df["a_a"].to_numpy().astype(float)),
             df["own_prev"].to_numpy().astype(float), df["owner"].to_numpy().astype(float)]
    names += STAY
    for e in extra or []:
        cols.append(df[e].to_numpy().astype(float))
        names.append(e)
    B, knots, bounds = ns_basis(df["g"].to_numpy().astype(float), spline_df, knots, bounds)
    for j in range(B.shape[1]):
        cols.append(B[:, j])
        names.append(f"s{j}")
    X = np.column_stack(cols)
    # drop constant columns (e.g. q0 never 1, owner never varies) to keep the fit identified
    keep = [j for j in range(X.shape[1]) if np.ptp(X[:, j]) > 0]
    return X[:, keep], [names[j] for j in keep], knots, bounds


def prep(df: pl.DataFrame) -> pl.DataFrame:
    """Rows with exposure; a leave row with zero counted calls gets one call; agents with no leave dropped."""
    d = df.with_columns(pl.when((pl.col("calls") == 0) & (pl.col("leave") == 1)).then(1).otherwise(pl.col("calls")).alias("calls"))
    d = d.filter(pl.col("calls") > 0)
    ag = d.group_by("agent").agg(pl.col("leave").sum().alias("nl")).filter(pl.col("nl") > 0)["agent"]
    return d.filter(pl.col("agent").is_in(ag.implode()))


LINK = "cloglog"   # Amendment A1 (pre-data): the card's cloglog form; the Poisson form saturates (synthetic bias)


def fit(df: pl.DataFrame, model="O1", qcol="q_live", y=None, extra=None, link=None) -> dict:
    d = df
    link = link or LINK
    yv = d["leave"].to_numpy().astype(float) if y is None else y
    X, names, knots, bounds = design(d, model, qcol, extra=extra)
    off = np.log(d["calls"].to_numpy().astype(float))
    r = (cloglog_fe if link == "cloglog" else poisson_fe)(yv, X, off, d["agent"].to_numpy())
    r["link"] = link
    r["names"] = names
    r["knots"], r["bounds"] = knots, bounds
    r["n"] = int(len(yv))
    r["events"] = int(yv.sum())
    return r


def coef(r: dict, name: str, df_t: int | None = None) -> dict:
    if name not in r["names"]:
        return {"est": None, "se": None, "lo": None, "hi": None, "p": None}
    j = r["names"].index(name)
    est = float(r["b"][j])
    se = float(np.sqrt(max(r["cov"][j, j], 0)))
    dfv = df_t if df_t is not None else max(r["G"] - 1, 1)
    q = float(stats.t.ppf(0.975, dfv))
    p = float(2 * stats.t.sf(abs(est) / se, dfv)) if se > 0 else None
    return {"est": est, "se": se, "lo": est - q * se, "hi": est + q * se, "p": p, "df": dfv}


def contrast(r: dict, a: str, b: str) -> dict:
    if a not in r["names"] or b not in r["names"]:
        return {"est": None, "se": None, "lo": None, "hi": None}
    i, j = r["names"].index(a), r["names"].index(b)
    est = float(r["b"][i] - r["b"][j])
    var = r["cov"][i, i] + r["cov"][j, j] - 2 * r["cov"][i, j]
    se = float(np.sqrt(max(var, 0)))
    q = float(stats.t.ppf(0.975, max(r["G"] - 1, 1)))
    return {"est": est, "se": se, "lo": est - q * se, "hi": est + q * se}


def dl_pool(est, se) -> dict:
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    k = len(est)
    if k == 0:
        return {"est": None, "se": None, "lo": None, "hi": None, "tau2": None, "k": 0}
    w = 1 / se ** 2
    mu_f = (w * est).sum() / w.sum()
    Q = float((w * (est - mu_f) ** 2).sum())
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if k > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = float((ws * est).sum() / ws.sum())
    s = math.sqrt(1 / ws.sum())
    return {"est": mu, "se": s, "lo": mu - 1.96 * s, "hi": mu + 1.96 * s, "tau2": float(tau2), "k": k, "Q": Q}


# ============================================================================================ synthetic worlds
def syn_dwell_resets(df: pl.DataFrame) -> np.ndarray:
    """Per row: True where the synthetic dwell restarts from the real skeleton (a visit that starts after a censoring,
    i.e. not right after a real direct leave of the same agent)."""
    d = df.select("agent", "visit", "g").with_row_index("r")
    first = d.group_by("visit").agg(pl.col("r").min().alias("r0"), pl.col("agent").first())
    vend = df.group_by("visit").agg(pl.col("leave").max().alias("lv"), pl.col("agent").first(), pl.col("g").min().alias("g0"))
    vend = vend.sort("agent", "g0").with_columns(pl.col("lv").shift(1).over("agent").fill_null(0).alias("prev_lv"))
    restart = set(vend.filter(pl.col("prev_lv") == 0)["visit"].to_list())
    out = np.zeros(df.height, bool)
    for v, r0 in first.select("visit", "r0").iter_rows():
        if v in restart:
            out[r0] = True
    return out


class World:
    """Semi-synthetic leaves on the real skeleton of one unit-channel (rows, calls, q series, births, actives kept).
    eta = ln h0 + theta_i + gamma ln(1 + dwell_syn) + eps ln q_live + drive terms; dwell_syn restarts at synthetic
    leaves and at real visits that follow a censoring."""

    def __init__(self, df: pl.DataFrame, n_leaves_target: int, rng):
        self.df = df.sort("agent", "g", "visit")
        self.calls = self.df["calls"].to_numpy().astype(float)
        self.q = self.df["q_live"].to_numpy().astype(float)
        self.agent = self.df["agent"].to_numpy()
        self.reset = syn_dwell_resets(self.df)
        self.B = self.df["births_pm2"].to_numpy().astype(float)
        self.N = self.df["n_active"].to_numpy().astype(float)
        self.target = max(n_leaves_target, 1)
        ags = np.unique(self.agent)
        self.theta = dict(zip(ags.tolist(), rng.normal(0, 0.5, len(ags)).tolist()))
        # agent row blocks
        self.blocks = []
        st = np.flatnonzero(np.r_[True, self.agent[1:] != self.agent[:-1]])
        en = np.r_[st[1:], len(self.agent)]
        self.blocks = list(zip(st, en))
        self.th = np.array([self.theta[a] for a in self.agent])

    def lin(self, world: str, eps: float) -> np.ndarray:
        q = self.q
        base = self.th + eps * np.where(q > 0, np.log(np.maximum(q, 1)), 0.0)
        if world == "W2":
            base = base + 1.0 * np.log1p(self.B)
        if world == "W3":
            base = base + 1.5 * np.log(np.maximum(self.N, 1))
        return base

    def simulate(self, world: str, eps: float, h0: float, rng, gamma=-0.3, flicker=0.0) -> np.ndarray:
        lin = self.lin(world, eps)
        y = np.zeros(len(lin), np.int8)
        dws = np.zeros(len(lin))
        for s, e in self.blocks:
            dw = 0.0
            for r in range(s, e):
                if self.reset[r]:
                    dw = 0.0
                dws[r] = dw
                c = self.calls[r]
                h = h0 * math.exp(lin[r] + gamma * math.log1p(dw))
                p = 1.0 - math.exp(-c * h)
                if flicker > 0 and self.q[r] > 0:
                    p = 1.0 - (1.0 - p) * math.exp(-c * flicker * self.q[r])
                if rng.random() < p:
                    y[r] = 1
                    dw = 0.0
                    if flicker > 0 and r + 1 < e and rng.random() < 0.5:
                        y[r + 1] = 1   # the flicker's return switch (half the time inside the unit's next row)
                else:
                    dw += c
        self.last_dwell = dws
        return y

    def calibrate(self, world: str, eps: float, rng, flicker_share=0.0) -> tuple[float, float]:
        lin = self.lin(world, eps)
        h0 = self.target / float((self.calls * np.exp(lin) * 0.3).sum())
        fl = 0.0
        if flicker_share > 0:
            fl = flicker_share * self.target / float((self.calls * self.q).sum())
        for _ in range(6):
            n = np.mean([self.simulate(world, eps, h0, rng, flicker=fl).sum() for _ in range(3)])
            if n <= 0:
                h0 *= 3
                continue
            ratio = self.target / n
            h0 *= ratio ** 0.9
            if abs(ratio - 1) < 0.05:
                break
        return h0, fl
