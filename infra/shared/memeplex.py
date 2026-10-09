"""Memeplex instrument (H145 owns this module, 2026-10-09): elements, expression panels, discovery.

A memeplex K is a set of content elements that co-occur within agents. Its hosts in bin b are the agents that express
>= m of its elements in b (physics-models/DEFINITIONS.md, "Egregore (an ideology running on a substrate of agents)").
Used by H145 (discovery, Krakauer tests), H146 (recruitment), H147 (value, hosts), H148 (agent discovery).

Bins (`make_bins`): clock bins anchored at 16:00 UTC (09:00 PT, the day's start) inside each non-reserved active day
of the goal period; width 30, 120 or 1440 min; 8 h per day. DQ8 presence trim per agent: agent i is present in bin b
when its first-to-last non-pause call span that day covers >= half of the bin (1-day bins: >= 1 non-pause call).
Absent agent-bins are not counted as non-expression.

Elements (`build_elements`; every rule fixed before any H145 test):
  cluster  k-means (k = 80; variants 40, 160) on `statements_style_resid_period32_<model>.npy` rows of the period's
           non-reserved statements (chat + intention); an element = a cluster with statements from >= 3 agents.
  marker   H34 idea markers of class N (names, coinages) and W (rare words) from `idea_markers.uses_for_rows` on the
           period's agent chat rows, used by >= 3 agents on >= 2 days (hashes only).
  repo     shared repos after cleaning (`clean_commits`): >= 3 agent writers with >= 3 commits each.
  project  touched projects from `project_calls.proj` (modal touched project of a non-pause call; never `label`, which
           carries over resets), mapped to repo slugs, touched by >= 3 agents with >= 3 calls each.
Expression x_{i,e}(b) = 1 if agent i has >= 1 event of element e in bin b (statement in the cluster, chat message with
the marker, cleaned commit to the repo, call touching the project).

Commit cleaning (`clean_commits`; story-51 data traps): agent work commits (canonical, not imported, author_kind agent,
not automated); drop single-agent single-file streams > 200 a day (the surprise-lab-mirror-proofs screenshot loop);
drop commits by agents with no touching call on that repo that day (removes the other village's "-chat" identities in
glm-5-3-flash-notes, which the ledger maps to roster agents); dedupe by hash; drop commits dated before the author's
roster join date.

Panels (`Panel`): counts per (agent, bin, element) as a CSR matrix with rows = agent * nB + bin, plus presence.
Discovery (`discover`):
  graph    co-occurrence O_ef = # present agent-bins expressing both e and f; agent-constant expectation
           E_ef = sum_i c_ie c_if / n_i (each agent's own element frequencies); weight = max(0, ln O_ef / E_ef) where
           O_ef >= min_co (positive PMI beyond each agent's habitual vocabulary).
  partition Louvain with resolution gamma (local moving + aggregation) and Leiden's connectivity fix (a community that
           is not connected is split into its components); best of `n_seeds` seeds by modularity.
  gamma    from a grid: the gamma that maximizes Q_real(gamma) - mean Q_null(gamma) over null panels
           (`rotate_elements` surrogates); `choose_resolution`.
  qualify  >= 4 elements, >= 3 hosts (agents with >= 2 host bins) from >= 2 labs, lifetime >= 10 active days with >= 1
           host (span also reported); h_K = the largest share of K's expressions by one host (>= 0.8: "one agent's
           vocabulary").
Pattern state (`pattern_state`): n_K(b) = hosts among present agents; c_K(b) = which third of K's elements (ordered by
median expression bin) has the most expressions by hosts in b; levels: 0 = no host, then <= 4 quantile levels of
positive n_K; symbol 0 = no host, else 1 + 3 (level - 1) + c.
Surrogates: `rotate_elements` (each element's series circularly shifted within each agent-day's present bins; keeps
per-agent-day element counts, breaks within-bin co-expression) and `rotate_agent_bins` (each agent's whole bin rows
shifted within day; keeps within-agent co-expression, breaks cross-agent timing).

Run `uv run python infra/shared/memeplex.py --verify`.
"""
from __future__ import annotations

import datetime as dt
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
SH = ROOT / "data/processed/shared"
EMB = SH / "embeddings"
DAY_START_UTC = 16          # 09:00 PT
DAY_HOURS = 8
BOOKENDS_LAST_DAY = "2026-08-04"   # daily pause/resume bookends stop after this PT day (NE43 step 1)
NUDGES_LAST_DAY = "2026-08-20"     # nudges stop after this PT day (NE43 step 2)


# ============================================================================ bins and presence
@dataclass
class Bins:
    goal_no: int
    width_min: int
    days: list                      # PT dates (non-reserved active days)
    t0: np.ndarray                  # bin start (datetime64[us], UTC)
    day_of_bin: np.ndarray          # index into days
    bin_in_day: np.ndarray
    agents: list                    # agent codes (rows)
    present: np.ndarray             # [nA, nB] bool (DQ8 per-agent presence trim)
    labs: dict = field(default_factory=dict)

    @property
    def nB(self):
        return len(self.t0)

    @property
    def nA(self):
        return len(self.agents)

    def locate(self, agent, t) -> tuple[np.ndarray, np.ndarray]:
        """(row agent index, bin index) for event arrays; -1 where outside the bins or not a panel agent."""
        t = np.asarray(t).astype("datetime64[us]")
        w = np.timedelta64(self.width_min, "m")
        pos = np.searchsorted(self.t0, t, side="right") - 1
        ok = (pos >= 0) & (t < self.t0[np.clip(pos, 0, None)] + w)
        lut = np.full(256, -1, np.int64)
        lut[np.asarray(self.agents, np.int64)] = np.arange(len(self.agents))
        ai = lut[np.asarray(agent, np.int64) & 255]
        b = np.where(ok, pos, -1)
        return np.where(b >= 0, ai, -1), b


def period_days(goal_no: int) -> list:
    import polars as pl
    from common import holdout_mask
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no", "holdout"]).filter(
        pl.col("goal_no") == goal_no)
    held = np.array(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())) | cal["holdout"].fill_null(False).to_numpy()
    return sorted(cal.filter(pl.Series(~held))["pt_date"].to_list())


def make_bins(goal_no: int = 51, width_min: int = 120, days: list | None = None) -> Bins:
    import polars as pl
    days = period_days(goal_no) if days is None else days
    nper = 1 if width_min >= 1440 else DAY_HOURS * 60 // width_min
    w = 1440 if width_min >= 1440 else width_min
    t0, dob, bid = [], [], []
    for k, d in enumerate(days):
        base = np.datetime64(f"{d}T{DAY_START_UTC:02d}:00:00", "us")
        for j in range(nper):
            t0.append(base + np.timedelta64(j * (DAY_HOURS * 60 if w == 1440 else w), "m"))
            dob.append(k)
            bid.append(j)
    t0 = np.array(t0, dtype="datetime64[us]")
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.col("goal_no") == goal_no) & ~pl.col("holdout") & (pl.col("kind") != "pause")
                  & pl.col("pt_date").is_in(days))
          .group_by("agent", "pt_date").agg(pl.col("t_call").min().alias("a"), pl.col("t_end").max().alias("b"),
                                            pl.len().alias("n")).collect())
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "lab", "claude_code"])
    cw = cw.join(ros.filter(~pl.col("claude_code")), on="agent", how="semi")
    agents = sorted(cw["agent"].unique().to_list())
    pos = {a: i for i, a in enumerate(agents)}
    dpos = {d: i for i, d in enumerate(days)}
    P = np.zeros((len(agents), len(t0)), bool)
    wdur = np.timedelta64(DAY_HOURS * 60 if w == 1440 else w, "m")
    dob = np.array(dob)
    for a, d, lo, hi in zip(cw["agent"].to_list(), cw["pt_date"].to_list(), cw["a"].to_numpy(), cw["b"].to_numpy()):
        idx = np.flatnonzero(dob == dpos[d])
        if w == 1440:
            P[pos[a], idx] = True
            continue
        lo = np.datetime64(lo, "us")
        hi = np.datetime64(hi, "us")
        s = t0[idx]
        e = s + wdur
        ov = (np.minimum(e, hi) - np.maximum(s, lo)) / np.timedelta64(1, "s")
        P[pos[a], idx] = ov >= 0.5 * wdur / np.timedelta64(1, "s")
    labs = dict(zip(ros["agent"].to_list(), ros["lab"].to_list()))
    return Bins(goal_no, width_min, list(days), t0, dob, np.array(bid), agents, P, {a: labs[a] for a in agents})


# ============================================================================ k-means
def kmeans(X: np.ndarray, k: int, seed: int = 0, iters: int = 100, tol: float = 1e-6, n_init: int = 3):
    """Lloyd's k-means with k-means++ seeding (float32, squared Euclidean); best of n_init seeds by inertia.
    Returns (labels, centers)."""
    best = None
    for s in range(n_init):
        lab, C, obj = _kmeans1(X, k, seed * 100 + s, iters, tol)
        if best is None or obj < best[2]:
            best = (lab, C, obj)
    return best[0], best[1]


def _kmeans1(X, k, seed, iters, tol):
    rng = np.random.default_rng(seed)
    X = np.asarray(X, np.float32)
    n = len(X)
    xx = (X * X).sum(1)
    C = np.empty((k, X.shape[1]), np.float32)
    C[0] = X[rng.integers(n)]
    d2 = ((X - C[0]) ** 2).sum(1)
    for j in range(1, k):
        p = d2 / d2.sum()
        C[j] = X[rng.choice(n, p=p)]
        d2 = np.minimum(d2, ((X - C[j]) ** 2).sum(1))
    lab = np.zeros(n, np.int64)
    prev = np.inf
    for _ in range(iters):
        D = xx[:, None] - 2 * X @ C.T + (C * C).sum(1)[None, :]
        lab = D.argmin(1)
        obj = float(D[np.arange(n), lab].sum())
        cnt = np.bincount(lab, minlength=k)
        S = np.zeros_like(C)
        np.add.at(S, lab, X)
        empty = cnt == 0
        C = np.where(empty[:, None], X[rng.integers(n, size=k)], S / np.maximum(cnt, 1)[:, None])
        if prev - obj <= tol * abs(prev):
            break
        prev = obj
    return lab, C, obj


# ============================================================================ elements
def load_statements(goal_no: int = 51, kinds=("chat", "intent")):
    """Non-reserved statements of the period: srow (row in the statement .npy files), agent, t, pt_date, kind."""
    import polars as pl
    from common import holdout_mask
    st = pl.read_parquet(EMB / "statements.parquet").with_row_index("srow")
    st = st.filter((pl.col("goal_no") == goal_no) & ~pl.col("holdout") & pl.col("kind").is_in(list(kinds)))
    held = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    return st.filter(pl.Series(~held))


def slug(project: str | None) -> str | None:
    """Repo slug of a project string: git hosts -> last path part; *.gitlab.io/<grp>/<x> -> x; *.workers.dev and
    other hosts -> first host label (or the full host)."""
    if project is None:
        return None
    p = str(project).strip().rstrip("/")
    parts = p.split("/")
    host = parts[0]
    if host in ("gitlab.com", "github.com"):
        return parts[-1] if len(parts) >= 3 else "/".join(parts)
    if host.endswith(".gitlab.io") or host.endswith(".github.io"):
        return parts[-1] if len(parts) >= 3 else p
    if host.endswith(".workers.dev"):
        return host.split(".")[0]
    return p


def clean_commits(goal_no: int = 51, report: dict | None = None):
    """Cleaned agent work commits of the period (see the module docstring). report (dict) receives the counts."""
    import polars as pl
    from common import holdout_mask
    w = (pl.scan_parquet(SH / "work_commits.parquet")
         .filter((pl.col("goal_no") == goal_no) & ~pl.col("holdout") & pl.col("canonical") & ~pl.col("imported")
                 & (pl.col("author_kind") == "agent") & ~pl.col("automated"))
         .select("repo", "hash", "t", "pt_date", "goal_no", "author_agent", "n_files").collect()
         .with_columns(pl.col("repo").cast(pl.Utf8)))
    held = np.array(holdout_mask(w["pt_date"].to_list(), w["goal_no"].to_list()))
    w = w.filter(pl.Series(~held))
    rep = {"work_commits": w.height}
    # single-agent single-file streams > 200 a day
    s1 = (w.filter(pl.col("n_files") <= 1).group_by("author_agent", "repo", "pt_date").len()
          .filter(pl.col("len") > 200))
    drop1 = w.join(s1.select("author_agent", "repo", "pt_date"), on=["author_agent", "repo", "pt_date"], how="semi") \
        .filter(pl.col("n_files") <= 1)
    w = w.join(drop1.select("hash", "repo"), on=["hash", "repo"], how="anti")
    rep["drop_single_file_streams"] = drop1.height
    # no touching call on the repo that day
    pc = (pl.scan_parquet(SH / "project_calls.parquet").filter((pl.col("goal_no") == goal_no) & ~pl.col("holdout"))
          .select("turn_id", "pt_date").collect())
    tt = (pl.scan_parquet(SH / "project_call_touches.parquet").filter(~pl.col("holdout"))
          .select("turn_id", "agent", "project").collect().join(pc, on="turn_id", how="inner"))
    tt = tt.with_columns(pl.col("project").map_elements(slug, return_dtype=pl.Utf8).alias("slug")) \
        .select("agent", "pt_date", "slug").unique()
    w = w.with_columns(pl.col("repo").map_elements(slug, return_dtype=pl.Utf8).alias("slug"))
    n0 = w.height
    w = w.join(tt.rename({"agent": "author_agent"}), on=["author_agent", "pt_date", "slug"], how="semi")
    rep["drop_no_call_on_repo_that_day"] = n0 - w.height
    # dedupe by hash (mirrored commits)
    n0 = w.height
    w = w.sort("t", "repo").unique("hash", keep="first", maintain_order=True)
    rep["drop_duplicate_hash"] = n0 - w.height
    # before the author's join date
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "joined"]).rename({"agent": "author_agent"})
    n0 = w.height
    w = w.join(ros, on="author_agent", how="left").filter(pl.col("pt_date") >= pl.col("joined")).drop("joined")
    rep["drop_before_join"] = n0 - w.height
    rep["kept"] = w.height
    if report is not None:
        report.update(rep)
    return w


@dataclass
class Elements:
    table: object            # polars: eid, kind, key, label_key, n_events, n_agents, n_days
    events: object           # polars: agent, t, eid  (one row per expression event)
    stmt_cluster: np.ndarray | None = None   # cluster label per statement row of `statements`
    statements: object = None
    centers: np.ndarray | None = None
    info: dict = field(default_factory=dict)


def build_elements(goal_no: int = 51, k: int = 80, model: str = "bge", seed: int = 0, min_agents: int = 3,
                   min_days_marker: int = 2, min_count: int = 3, marker_classes=("N", "W"), verbose=True) -> Elements:
    import polars as pl
    import idea_markers as IM
    info = {}
    # --- clusters
    st = load_statements(goal_no)
    mname = {"bge": "bge_small", "gte": "gte_modernbert"}[model]
    V = np.load(EMB / f"statements_style_resid_period32_{mname}.npy", mmap_mode="r")
    X = np.asarray(V[st["srow"].to_numpy()], np.float32)
    lab, C = kmeans(X, k, seed=seed)
    st = st.with_columns(pl.Series("cluster", lab))
    cl = st.group_by("cluster").agg(pl.col("agent").n_unique().alias("n_agents"), pl.len().alias("n_events"),
                                    pl.col("pt_date").n_unique().alias("n_days"))
    keep_c = cl.filter(pl.col("n_agents") >= min_agents)
    ev_c = st.join(keep_c.select("cluster"), on="cluster", how="semi").select(
        pl.col("agent").cast(pl.Int16), "t", pl.format("c:{}", pl.col("cluster")).alias("key"))
    tab_c = keep_c.select(pl.lit("cluster").alias("kind"), pl.format("c:{}", pl.col("cluster")).alias("key"),
                          "n_events", "n_agents", "n_days")
    info["clusters"] = {"k": k, "model": model, "statements": st.height, "elements": keep_c.height}
    if verbose:
        print(f"clusters: {st.height} statements, {keep_c.height}/{k} clusters with >= {min_agents} agents", flush=True)
    # --- markers
    from common import holdout_mask
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["goal_no", "pt_date", "agent", "speaker_kind", "t"])
            .with_row_index("msg").filter((pl.col("goal_no") == goal_no) & (pl.col("speaker_kind") == "agent")))
    held = np.array(holdout_mask(chat["pt_date"].to_list(), chat["goal_no"].to_list()))
    chat = chat.filter(pl.Series(~held))
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "holdout"])
    chat = chat.join(cal, on="pt_date", how="left").filter(~pl.col("holdout").fill_null(False)).drop("holdout")
    uses = IM.uses_for_rows(chat["msg"].to_numpy())
    cls_ids = [IM.CLS[c] for c in marker_classes]
    u = uses.filter(pl.col("cls").is_in(cls_ids)).join(chat.select(pl.col("msg").cast(pl.UInt32), "agent", "t", "pt_date"),
                                                        on="msg", how="inner")
    mk = u.group_by("marker", "cls").agg(pl.col("agent").n_unique().alias("n_agents"), pl.len().alias("n_events"),
                                         pl.col("pt_date").n_unique().alias("n_days"))
    keep_m = mk.filter((pl.col("n_agents") >= min_agents) & (pl.col("n_days") >= min_days_marker))
    ev_m = u.join(keep_m.select("marker"), on="marker", how="semi").select(
        pl.col("agent").cast(pl.Int16), "t", pl.format("m:{}", pl.col("marker")).alias("key"))
    tab_m = keep_m.select(pl.lit("marker").alias("kind"), pl.format("m:{}", pl.col("marker")).alias("key"),
                          "n_events", "n_agents", "n_days")
    info["markers"] = {"messages": chat.height, "uses_NW": u.height, "elements": keep_m.height,
                       "by_class": {IM.CLS_NAME[int(c)]: int(n) for c, n in keep_m.group_by("cls").len().iter_rows()}}
    if verbose:
        print(f"markers: {chat.height} messages, {keep_m.height} N/W markers", flush=True)
    # --- repos
    rep = {}
    w = clean_commits(goal_no, rep)
    wr = w.group_by("slug", "author_agent").len().filter(pl.col("len") >= min_count)
    rr = wr.group_by("slug").agg(pl.col("author_agent").n_unique().alias("nw")).filter(pl.col("nw") >= min_agents)
    ev_r = w.join(rr.select("slug"), on="slug", how="semi").select(
        pl.col("author_agent").cast(pl.Int16).alias("agent"), "t", pl.format("r:{}", pl.col("slug")).alias("key"))
    tab_r = (ev_r.with_columns(pl.col("t").dt.date().alias("d")).group_by("key")
             .agg(pl.len().alias("n_events"), pl.col("agent").n_unique().alias("n_agents"), pl.col("d").n_unique().alias("n_days"))
             .select(pl.lit("repo").alias("kind"), "key", "n_events", "n_agents", "n_days"))
    info["repos"] = {"cleaning": rep, "elements": rr.height}
    if verbose:
        print(f"repos: {rep}; {rr.height} shared repos", flush=True)
    # --- projects
    pc = (pl.scan_parquet(SH / "project_calls.parquet")
          .filter((pl.col("goal_no") == goal_no) & ~pl.col("holdout") & (pl.col("kind") != "pause") & pl.col("proj").is_not_null())
          .select("agent", "t_call", "pt_date", "proj").collect())
    held = np.array(holdout_mask(pc["pt_date"].to_list(), [goal_no] * pc.height))
    pc = pc.filter(pl.Series(~held)).with_columns(pl.col("proj").map_elements(slug, return_dtype=pl.Utf8).alias("slug"))
    pa = pc.group_by("slug", "agent").len().filter(pl.col("len") >= min_count)
    pp = pa.group_by("slug").agg(pl.col("agent").n_unique().alias("na")).filter(pl.col("na") >= min_agents)
    ev_p = pc.join(pp.select("slug"), on="slug", how="semi").select(
        pl.col("agent").cast(pl.Int16), pl.col("t_call").alias("t"), pl.format("p:{}", pl.col("slug")).alias("key"))
    tab_p = (ev_p.with_columns(pl.col("t").dt.date().alias("d")).group_by("key")
             .agg(pl.len().alias("n_events"), pl.col("agent").n_unique().alias("n_agents"), pl.col("d").n_unique().alias("n_days"))
             .select(pl.lit("project").alias("kind"), "key", "n_events", "n_agents", "n_days"))
    info["projects"] = {"calls": pc.height, "elements": pp.height}
    if verbose:
        print(f"projects: {pc.height} labelled calls, {pp.height} projects", flush=True)
    tab = pl.concat([tab_c.with_columns(pl.col(c).cast(pl.Int64) for c in ("n_events", "n_agents", "n_days")),
                     tab_m.with_columns(pl.col(c).cast(pl.Int64) for c in ("n_events", "n_agents", "n_days")),
                     tab_r.with_columns(pl.col(c).cast(pl.Int64) for c in ("n_events", "n_agents", "n_days")),
                     tab_p.with_columns(pl.col(c).cast(pl.Int64) for c in ("n_events", "n_agents", "n_days"))])
    tab = tab.sort("kind", "key").with_row_index("eid").with_columns(pl.col("eid").cast(pl.Int32))
    ev = pl.concat([ev_c, ev_m, ev_r, ev_p]).join(tab.select("eid", "key"), on="key").select(
        "agent", "t", "eid").sort("t")
    return Elements(tab, ev, lab, st, C, info)


# ============================================================================ panels
@dataclass
class Panel:
    bins: Bins
    X: object                # scipy.sparse.csr_matrix [nA * nB, nE] counts
    nE: int

    def rows(self, a, b):
        return np.asarray(a) * self.bins.nB + np.asarray(b)

    def present_rows(self) -> np.ndarray:
        return np.flatnonzero(self.bins.present.ravel())

    def binary(self):
        Y = self.X.copy()
        Y.data = np.ones_like(Y.data)
        return Y

    def dense_cols(self, cols) -> np.ndarray:
        """[nA, nB, len(cols)] counts for a few elements (0 where absent)."""
        sub = self.X[:, np.asarray(cols)].toarray()
        return sub.reshape(self.bins.nA, self.bins.nB, len(cols))


def make_panel(elements_events, bins: Bins, nE: int) -> Panel:
    import scipy.sparse as sp
    ev = elements_events
    ai, b = bins.locate(ev["agent"].to_numpy(), ev["t"].to_numpy())
    e = ev["eid"].to_numpy().astype(np.int64)
    ok = (ai >= 0) & (b >= 0)
    ai, b, e = ai[ok], b[ok], e[ok]
    pres = bins.present[ai, b]
    ai, b, e = ai[pres], b[pres], e[pres]
    X = sp.csr_matrix((np.ones(len(e), np.float32), (ai * bins.nB + b, e)), shape=(bins.nA * bins.nB, nE))
    X.sum_duplicates()
    return Panel(bins, X, nE)


def panel_with(panel: Panel, X) -> Panel:
    return Panel(panel.bins, X, panel.nE)


# ============================================================================ surrogates
def _agent_day_blocks(bins: Bins):
    """For each row (agent * nB + b) of present agent-bins: block id (agent, day), block start row, block length."""
    nA, nB = bins.nA, bins.nB
    P = bins.present
    start = np.full(nA * nB, -1, np.int64)
    length = np.zeros(nA * nB, np.int64)
    for a in range(nA):
        for d in np.unique(bins.day_of_bin):
            idx = np.flatnonzero((bins.day_of_bin == d) & P[a])
            if len(idx) == 0:
                continue
            r = a * nB + idx
            start[r] = r[0]
            length[r] = len(idx)
    return start, length


def rotate_elements(panel: Panel, rng: np.random.Generator, _cache: dict = {}) -> Panel:
    """Each element's series circularly shifted within each agent-day's present bins (an independent offset per
    (agent-day, element)). Present bins of an agent-day are contiguous (span trim), so the shift is index arithmetic."""
    import scipy.sparse as sp
    key = id(panel.bins)
    if key not in _cache:
        _cache.clear()
        _cache[key] = _agent_day_blocks(panel.bins)
    start, length = _cache[key]
    C = panel.X.tocoo()
    r, c, v = C.row.astype(np.int64), C.col.astype(np.int64), C.data
    s, L = start[r], length[r]
    # offset per (block start row, element) from a random hash
    salt = rng.integers(1, 2 ** 31 - 1)
    hsh = (s * 1_000_003 + c * 7_919 + salt) % 2_147_483_647
    hsh = (hsh * 48_271) % 2_147_483_647
    off = hsh % np.maximum(L, 1)
    r2 = s + (r - s + off) % np.maximum(L, 1)
    X = sp.csr_matrix((v, (r2, c)), shape=panel.X.shape)
    X.sum_duplicates()
    return panel_with(panel, X)


def rotate_agent_bins(panel: Panel, rng: np.random.Generator) -> Panel:
    """Each agent's whole bin rows circularly shifted within each day's present bins (keeps within-agent co-expression
    and per-agent-day composition; breaks cross-agent timing)."""
    import scipy.sparse as sp
    start, length = _agent_day_blocks(panel.bins)
    C = panel.X.tocoo()
    r, c, v = C.row.astype(np.int64), C.col.astype(np.int64), C.data
    s, L = start[r], length[r]
    offs = rng.integers(0, 1 << 30, size=panel.X.shape[0])
    off = offs[s] % np.maximum(L, 1)
    r2 = s + (r - s + off) % np.maximum(L, 1)
    X = sp.csr_matrix((v, (r2, c)), shape=panel.X.shape)
    X.sum_duplicates()
    return panel_with(panel, X)


# ============================================================================ discovery
def ppmi_graph(panel: Panel, min_co: int = 3, p_edge: float | None = 0.01) -> np.ndarray:
    """W_ef = max(0, ln O_ef / E_ef) for O_ef >= min_co; O = co-expression counts over present agent-bins, E = the
    agent-constant expectation sum_i c_ie c_if / n_i. With p_edge, an edge is kept only if O_ef exceeds E_ef at a
    one-sided Poisson p < p_edge (removes chance co-occurrences; p_edge=None gives the plain PPMI graph)."""
    import scipy.sparse as sp
    pr = panel.present_rows()
    Y = panel.binary()[pr]
    O = (Y.T @ Y).toarray().astype(np.float64)
    np.fill_diagonal(O, 0)
    agent_of = pr // panel.bins.nB
    nA = panel.bins.nA
    A = sp.csr_matrix((np.ones(len(pr)), (agent_of, np.arange(len(pr)))), shape=(nA, len(pr)))
    Cc = (A @ Y).toarray()                               # [nA, nE] agent element counts
    n_i = np.bincount(agent_of, minlength=nA).astype(float)
    Cw = Cc / np.sqrt(np.maximum(n_i, 1))[:, None]
    E = Cw.T @ Cw
    np.fill_diagonal(E, 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        W = np.where((O >= min_co) & (E > 0), np.log(O / E), 0.0)
    W = np.maximum(W, 0.0)
    if p_edge is not None:
        from scipy.stats import poisson
        iu = np.triu_indices_from(W, 1)
        sel = W[iu] > 0
        pv = np.ones(sel.shape)
        pv[sel] = poisson.sf(O[iu][sel] - 1, E[iu][sel])
        keep = np.zeros_like(W, bool)
        keep[iu[0][sel], iu[1][sel]] = pv[sel] < p_edge
        keep = keep | keep.T
        W = np.where(keep, W, 0.0)
    return W


def modularity(W: np.ndarray, labels: np.ndarray, gamma: float = 1.0) -> float:
    k = W.sum(1)
    m2 = k.sum()
    if m2 <= 0:
        return 0.0
    q = 0.0
    for c in np.unique(labels):
        idx = labels == c
        q += W[np.ix_(idx, idx)].sum() / m2 - gamma * (k[idx].sum() / m2) ** 2
    return float(q)


def _louvain_level(W: np.ndarray, gamma: float, rng) -> np.ndarray:
    n = len(W)
    k = W.sum(1)
    m2 = k.sum()
    lab = np.arange(n)
    tot = k.copy()
    nbrs = [np.flatnonzero(W[i] > 0) for i in range(n)]
    improved = True
    it = 0
    while improved and it < 50:
        improved = False
        it += 1
        for i in rng.permutation(n):
            if k[i] == 0:
                continue
            ci = lab[i]
            nb = nbrs[i]
            nb = nb[nb != i]
            if len(nb) == 0:
                continue
            w_to = np.bincount(lab[nb], weights=W[i, nb], minlength=n)
            tot[ci] -= k[i]
            cands = np.unique(np.r_[lab[nb], ci])
            gain = w_to[cands] - gamma * tot[cands] * k[i] / m2
            best = cands[np.argmax(gain)]
            if gain.max() <= w_to[ci] - gamma * tot[ci] * k[i] / m2 + 1e-12:
                best = ci
            lab[i] = best
            tot[best] += k[i]
            if best != ci:
                improved = True
    _, lab = np.unique(lab, return_inverse=True)
    return lab


def _split_disconnected(W: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Leiden's guarantee: split every community into its connected components."""
    out = labels.copy()
    nxt = labels.max() + 1
    for c in np.unique(labels):
        idx = np.flatnonzero(labels == c)
        if len(idx) <= 1:
            continue
        sub = W[np.ix_(idx, idx)] > 0
        comp = -np.ones(len(idx), np.int64)
        cc = 0
        for s in range(len(idx)):
            if comp[s] >= 0:
                continue
            stack = [s]
            comp[s] = cc
            while stack:
                u = stack.pop()
                for v in np.flatnonzero(sub[u]):
                    if comp[v] < 0:
                        comp[v] = cc
                        stack.append(v)
            cc += 1
        for j in range(1, cc):
            out[idx[comp == j]] = nxt
            nxt += 1
    _, out = np.unique(out, return_inverse=True)
    return out


def louvain(W: np.ndarray, gamma: float = 1.0, seed: int = 0, n_seeds: int = 5) -> tuple[np.ndarray, float]:
    """Louvain (local moving + aggregation) with Leiden's connectivity fix; best of n_seeds by modularity."""
    best = (None, -np.inf)
    for s in range(n_seeds):
        rng = np.random.default_rng(seed * 1000 + s)
        lab = np.arange(len(W))
        Wc = W.copy()
        while True:
            l1 = _louvain_level(Wc, gamma, rng)
            if l1.max() + 1 == len(Wc):
                break
            lab = l1[lab]
            nC = l1.max() + 1
            M = np.zeros((nC, len(Wc)))
            M[l1, np.arange(len(Wc))] = 1
            Wc = M @ Wc @ M.T
        lab = _split_disconnected(W, lab)
        q = modularity(W, lab, gamma)
        if q > best[1]:
            best = (lab, q)
    return best


def choose_resolution(W_real: np.ndarray, W_nulls: list, grid=(0.5, 0.75, 1.0, 1.5, 2.0, 3.0), seed: int = 0) -> dict:
    """gamma maximizing Q_real(gamma) - mean_null Q_null(gamma)."""
    rows = []
    for g in grid:
        _, qr = louvain(W_real, g, seed)
        qn = [louvain(Wn, g, seed)[1] for Wn in W_nulls]
        rows.append({"gamma": g, "Q_real": qr, "Q_null": float(np.mean(qn)) if qn else 0.0})
    for r in rows:
        r["gap"] = r["Q_real"] - r["Q_null"]
    best = max(rows, key=lambda r: r["gap"])
    return {"gamma": best["gamma"], "grid": rows}


def host_matrix(panel: Panel, K, m: int = 2) -> tuple[np.ndarray, np.ndarray]:
    """H [nA, nB] bool (agent expresses >= m elements of K in bin b, present only) and the per-agent-bin count of
    distinct K elements expressed."""
    Y = panel.binary()[:, np.asarray(K)]
    cnt = np.asarray(Y.sum(1)).ravel().reshape(panel.bins.nA, panel.bins.nB)
    H = (cnt >= m) & panel.bins.present
    return H, cnt


def pattern_stats(panel: Panel, K, m: int = 2) -> dict:
    """Hosts, labs, lifetime (days with >= 1 host; span), h_K and the host series for a memeplex K."""
    H, cnt = host_matrix(panel, K, m)
    bins = panel.bins
    hb = H.sum(1)
    hosts = [bins.agents[i] for i in np.flatnonzero(hb >= 2)]
    labs = sorted({bins.labs[a] for a in hosts})
    days_with = np.unique(bins.day_of_bin[H.any(0)])
    span = int(days_with.max() - days_with.min() + 1) if len(days_with) else 0
    Y = panel.binary()[:, np.asarray(K)]
    expr = np.asarray(Y.sum(1)).ravel().reshape(bins.nA, bins.nB)
    expr_h = np.where(H, expr, 0).sum(1)
    tot = expr_h.sum()
    hK = float(expr_h.max() / tot) if tot > 0 else np.nan
    top = bins.agents[int(np.argmax(expr_h))] if tot > 0 else None
    return {"n_elements": len(K), "hosts": hosts, "n_hosts": len(hosts), "labs": labs, "n_labs": len(labs),
            "lifetime_days": int(len(days_with)), "span_days": span, "h_K": hK, "top_host": top,
            "host_bins": int(H.sum()), "first_day": bins.days[int(days_with.min())] if len(days_with) else None,
            "last_day": bins.days[int(days_with.max())] if len(days_with) else None}


def qualifies(s: dict, min_el=4, min_hosts=3, min_labs=2, min_life=10) -> bool:
    return bool(s["n_elements"] >= min_el and s["n_hosts"] >= min_hosts and s["n_labs"] >= min_labs
                and s["lifetime_days"] >= min_life)


def discover(panel: Panel, gamma: float, m: int = 2, min_co: int = 3, seed: int = 0, W: np.ndarray | None = None,
             rules: dict | None = None) -> dict:
    """Communities of the PPMI graph at resolution gamma, with pattern stats and the qualification flag."""
    rules = rules or {}
    W = ppmi_graph(panel, min_co) if W is None else W
    lab, q = louvain(W, gamma, seed)
    out = []
    for c in np.unique(lab):
        K = np.flatnonzero(lab == c)
        if len(K) < 2:
            continue
        s = pattern_stats(panel, K, m)
        s["elements"] = K.tolist()
        s["qualifies"] = qualifies(s, **rules)
        s["qualifies_hub_free"] = bool(s["qualifies"] and np.isfinite(s["h_K"]) and s["h_K"] < 0.8)
        out.append(s)
    return {"Q": q, "labels": lab, "communities": out, "n_qualify": sum(c["qualifies"] for c in out),
            "n_qualify_hub_free": sum(c["qualifies_hub_free"] for c in out)}


def pattern_state(panel: Panel, K, m: int = 2, thirds: list | None = None, cuts: np.ndarray | None = None) -> dict:
    """S_K(b) symbols (0 = no host; else 1 + 3 (level - 1) + c), n_K, c_K, the thirds and the level cuts."""
    K = np.asarray(K)
    bins = panel.bins
    D = panel.dense_cols(K)                                  # [nA, nB, |K|]
    Db = D > 0
    H = (Db.sum(2) >= m) & bins.present
    nK = H.sum(0)
    if thirds is None:
        # order elements by the median bin of their expressions
        med = []
        for j in range(len(K)):
            bb = np.flatnonzero(Db[:, :, j].any(0))
            med.append(np.median(bb) if len(bb) else np.inf)
        order = np.argsort(med, kind="stable")
        thirds = [order[int(len(K) * t / 3):int(len(K) * (t + 1) / 3)].tolist() for t in range(3)]
    hexp = (Db & H[:, :, None]).sum(0)                       # [nB, |K|] host expressions
    comp = np.stack([hexp[:, th].sum(1) if len(th) else np.zeros(bins.nB) for th in thirds], 1)
    cK = comp.argmax(1)
    if cuts is None:
        pos = nK[nK > 0]
        cuts = np.unique(np.quantile(pos, [0.25, 0.5, 0.75])) if len(pos) else np.array([])
    lvl = np.where(nK > 0, 1 + np.searchsorted(cuts, nK, side="left").clip(0, 3), 0)
    lvl = np.minimum(lvl, 4)
    sym = np.where(nK > 0, 1 + 3 * (lvl - 1) + cK, 0)
    return {"sym": sym.astype(np.int64), "n": nK, "c": cK, "level": lvl, "thirds": thirds, "cuts": cuts,
            "K_sym": 13, "H": H}


def element_prevalence(panel: Panel, K) -> np.ndarray:
    """[nB, |K|] number of present agents expressing each element in each bin."""
    D = panel.dense_cols(np.asarray(K)) > 0
    return (D & panel.bins.present[:, :, None]).sum(0)


def jaccard_renewal(H: np.ndarray, day_of_bin: np.ndarray, k: int) -> float:
    """J_K(k): mean over days d of Jaccard(hosts over days d-k+1..d, hosts over d+1..d+k) (days with hosts on both
    sides only)."""
    nd = int(day_of_bin.max()) + 1
    Hd = np.zeros((H.shape[0], nd), bool)
    for d in range(nd):
        Hd[:, d] = H[:, day_of_bin == d].any(1)
    vals = []
    for d in range(k - 1, nd - k):
        a = Hd[:, d - k + 1:d + 1].any(1)
        b = Hd[:, d + 1:d + k + 1].any(1)
        u = (a | b).sum()
        if a.any() and b.any():
            vals.append((a & b).sum() / u)
    return float(np.mean(vals)) if vals else np.nan


def daily_prevalence(H: np.ndarray, present: np.ndarray, day_of_bin: np.ndarray) -> np.ndarray:
    nd = int(day_of_bin.max()) + 1
    out = np.zeros(nd)
    for d in range(nd):
        sel = day_of_bin == d
        pres = present[:, sel].any(1)
        out[d] = H[:, sel].any(1).sum() / max(pres.sum(), 1)
    return out


def autocorr(x: np.ndarray, k: int) -> float:
    x = np.asarray(x, float)
    if len(x) <= k + 2 or np.std(x[:-k]) == 0 or np.std(x[k:]) == 0:
        return np.nan
    return float(np.corrcoef(x[:-k], x[k:])[0, 1])


# ============================================================================ verify
def verify() -> bool:
    import scipy.sparse as sp
    rng = np.random.default_rng(20261009)
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
        ok &= bool(cond)

    # 1. k-means recovers planted blobs
    cen = rng.normal(scale=6, size=(6, 8))
    lab0 = rng.integers(0, 6, 3000)
    X = cen[lab0] + rng.normal(size=(3000, 8))
    lab, _ = kmeans(X, 6, seed=1)
    pur = sum(np.bincount(lab0[lab == c]).max() for c in np.unique(lab)) / len(lab)
    check("kmeans purity on planted blobs", pur > 0.97, f"purity={pur:.3f}")

    # 2. Louvain on a planted SBM (4 blocks of 25)
    n = 100
    blk = np.repeat(np.arange(4), 25)
    Pm = np.where(blk[:, None] == blk[None, :], 0.4, 0.03)
    A = (rng.random((n, n)) < Pm).astype(float)
    A = np.triu(A, 1)
    A = A + A.T
    lab, q = louvain(A, 1.0, seed=0)
    pur = sum(np.bincount(blk[lab == c]).max() for c in np.unique(lab)) / n
    check("louvain recovers a planted SBM", pur > 0.95 and len(np.unique(lab)) <= 6, f"purity={pur:.3f}, Q={q:.3f}, k={len(np.unique(lab))}")
    lab2 = _split_disconnected(np.array([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], float), np.zeros(4, int))
    check("connectivity fix splits a disconnected community", len(np.unique(lab2)) == 2)

    # 3. synthetic panel: 12 agents, 5 days x 16 bins; 60 background elements with agent-specific rates; a planted
    #    memeplex of 6 elements co-expressed when an agent is a host.
    nA, nD, nb, nE = 12, 5, 16, 66
    days = [f"2026-01-{d + 5:02d}" for d in range(nD)]
    t0 = np.array([np.datetime64(f"{d}T16:00", "us") + np.timedelta64(30 * j, "m") for d in days for j in range(nb)])
    dob = np.repeat(np.arange(nD), nb)
    bins = Bins(51, 30, days, t0, dob, np.tile(np.arange(nb), nD), list(range(nA)), np.ones((nA, nD * nb), bool),
                {a: ("L1" if a < 6 else "L2") for a in range(nA)})
    rate = rng.gamma(0.5, 0.15, size=(nA, 60)).clip(0, 0.9)
    Xb = (rng.random((nA, nD * nb, 60)) < rate[:, None, :])
    host = rng.random((nA, nD * nb)) < 0.25
    planted = (rng.random((nA, nD * nb, 6)) < 0.8) & host[:, :, None]
    full = np.concatenate([Xb, planted], 2).astype(np.float32).reshape(nA * nD * nb, nE)
    panel = Panel(bins, sp.csr_matrix(full), nE)
    W = ppmi_graph(panel, 3)
    # agent-constant expectation: background-only edges are weak, planted edges strong
    wp = W[60:, 60:][np.triu_indices(6, 1)].mean()
    wb = W[:60, :60][np.triu_indices(60, 1)].mean()
    check("PPMI: planted edges >> background edges", wp > 0.5 and wb < 0.15, f"planted={wp:.2f}, background={wb:.3f}")
    # brute-force O and E
    Y = (full > 0).astype(float)
    O = Y.T @ Y
    np.fill_diagonal(O, 0)
    ag = np.repeat(np.arange(nA), nD * nb)
    Ecalc = sum(np.outer(Y[ag == a].sum(0), Y[ag == a].sum(0)) / (ag == a).sum() for a in range(nA))
    np.fill_diagonal(Ecalc, 0)
    with np.errstate(divide='ignore', invalid='ignore'):
        Wb = np.maximum(np.where((O >= 3) & (Ecalc > 0), np.log(O / Ecalc), 0), 0)
    check("ppmi_graph == brute force", np.allclose(ppmi_graph(panel, 3, p_edge=None), Wb, atol=1e-8))
    nulls = [ppmi_graph(rotate_elements(panel, np.random.default_rng(100 + i)), 3) for i in range(3)]
    cr = choose_resolution(W, nulls)
    res = discover(panel, cr["gamma"], m=2, W=W, rules={"min_life": 3})
    best = max(res["communities"], key=lambda c: len(set(c["elements"]) & set(range(60, 66))) / len(set(c["elements"]) | set(range(60, 66))))
    jac = len(set(best["elements"]) & set(range(60, 66))) / len(set(best["elements"]) | set(range(60, 66)))
    check("discover recovers the planted memeplex", jac >= 0.8 and best["qualifies"], f"Jaccard={jac:.2f}, hosts={best['n_hosts']}, gamma={cr['gamma']}")
    # 4. surrogates
    rot = rotate_elements(panel, rng)
    cnt_a = np.asarray(panel.X.sum(0)).ravel()
    cnt_b = np.asarray(rot.X.sum(0)).ravel()
    per_ad = lambda P: np.add.reduceat(P.X.toarray().reshape(nA, nD * nb, nE), np.arange(0, nD * nb, nb), axis=1)
    check("rotate_elements keeps per-agent-day element counts", np.array_equal(per_ad(panel), per_ad(rot)) and np.array_equal(cnt_a, cnt_b))
    Wr = ppmi_graph(rot, 3)
    check("rotate_elements breaks within-bin co-expression", Wr[60:, 60:][np.triu_indices(6, 1)].mean() < 0.5 * wp,
          f"planted after rotation={Wr[60:, 60:][np.triu_indices(6, 1)].mean():.2f}")
    rab = rotate_agent_bins(panel, rng)
    Wa = ppmi_graph(rab, 3)
    check("rotate_agent_bins keeps the within-agent graph exactly", np.allclose(Wa, W))
    # 5. pattern state and renewal helpers
    ps = pattern_state(panel, list(range(60, 66)), m=2)
    check("pattern_state symbols in 0..12", ps["sym"].min() >= 0 and ps["sym"].max() <= 12)
    Hc = np.zeros((4, 20), bool)
    Hc[0] = True
    check("jaccard_renewal = 1 for a constant host", abs(jaccard_renewal(Hc, np.repeat(np.arange(10), 2), 2) - 1) < 1e-12)
    # 6. slug map and commit-cleaning rules on real tables (counts only)
    check("slug map", slug("gitlab.com/ai-village-agents/village/echoes-of-the-real") == "echoes-of-the-real"
          and slug("keystone-dau.aivillage.workers.dev") == "keystone-dau"
          and slug("ai-village-agents.gitlab.io/village/hub") == "hub")
    try:
        rep = {}
        w = clean_commits(51, rep)
        g = w.filter(w["slug"] == "glm-5-3-flash-notes")
        others = int((g["author_agent"] != 41).sum())
        sl = int((w["slug"] == "surprise-lab-mirror-proofs").sum())
        check("cleaning removes the other village's identities in glm-5-3-flash-notes", others <= 5,
              f"non-GLM-5.3-Flash commits left={others}; cleaning={rep}; mirror-proofs kept={sl}")
    except FileNotFoundError as ex:
        check("commit tables present", False, repr(ex))
    # 7. marker uses for #51 chat rows: idea_markers.uses_for_rows reproduces H34's stored uses on a sample
    try:
        import polars as pl
        import idea_markers as IM
        h34 = pl.read_parquet(ROOT / "data/processed/H34-idea-cascades/markers/uses.parquet")
        chat = pl.read_parquet(SH / "chat_core.parquet", columns=["goal_no", "speaker_kind"]).with_row_index("msg")
        rows = (h34.join(chat.filter((pl.col("goal_no") == 51) & (pl.col("speaker_kind") == "agent")), on="msg", how="semi")
                ["msg"].unique().sort().head(400))
        mine = IM.uses_for_rows(rows.to_numpy()).sort("msg", "marker")
        ref = h34.filter(pl.col("msg").is_in(rows.implode())).sort("msg", "marker")
        check("marker uses on 400 #51 messages == H34 uses.parquet", mine.equals(ref), f"{ref.height} uses")
    except FileNotFoundError as ex:
        check("H34 marker table present", False, repr(ex))
    print("verify:", "OK" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    print(__doc__)
