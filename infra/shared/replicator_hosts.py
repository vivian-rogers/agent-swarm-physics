"""Repos as replicators (shared by H77 and H78): host labels, recruitment/departure events and swarm call-clock bins.

Physics mapping (H77 card): repo j is a replicator, n_j(t) its number of hosts (agents whose current work label is j).
  recruitment  label change into j while n_j >= 1 (a copy step, catalysed by the hosts)
  birth        label change into j while n_j == 0 (formation)
  depart       label change out of j into another repo (the reverse step, "uncopying")
  expire       no commit to the labelled repo for E of the agent's own calls (dilution, X -> W)
  leave        the agent leaves the roster inside the period (dilution)

Host label ("host (work ledger, call-clock expiry)"): per agent and W-min window from the day's win_start, the repo with the
most DQ4 agent work commits (canonical & ~imported & author_kind == agent & ~automated; author time); ties -> the most
recent commit. Labels carry forward over windows without commits (H06) and expire after E (= 100 since A1) own calls without a commit to
the labelled repo (E = None: never).

Arrival tags (impostors): known (the recruit mentioned the repo, strict how, or hosted it earlier in the period), read (a
chat link to it from another sender entered one of the recruit's calls before the arrival; DQ1 ledger), blind (an unread
link was posted in the 30 min before the arrival: H28's blind window / in-flight convergence), none. named: the repo is
kickoff-named (H54 rule: strict link in a kickoff message, or a name token in the kickoff or goal text).

Clock: the swarm call clock (H40): the period's calls (call_windows, Claude Code agent excluded) sorted by t_call and cut
into bins of B calls within each period unit. Wall-clock variant: 30-min bins from each day's win_start.

Everything is codes only: repo names are kept in memory and hashed on output. No message text is stored.
Holdout rows are dropped with common.holdout_mask unless allow_holdout=True (confirm scripts only).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import sys  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import OUT as SHARED, ROOT, holdout_mask, load_goals  # noqa: E402

CLAUDE_CODE = 19
STRICT = ["url", "output", "bare"]
LINK_HOW = ["url", "bare"]
BLIND_S = 30 * 60
DEFAULTS = dict(W=30, E=100, B=200)  # E = 100 since amendment A1 (H77/H78 synthetic); was 300


def rhash(repo: str) -> str:
    return hashlib.sha1(repo.encode()).hexdigest()[:10]


# ============================================================================================ inputs
@lru_cache(maxsize=1)
def calendar() -> pl.DataFrame:
    c = pl.read_parquet(SHARED / "calendar.parquet", columns=["pt_date", "goal_no", "win_start", "win_end"])
    ho = holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())
    return c.with_columns(pl.Series("ho", ho))


@lru_cache(maxsize=1)
def roster() -> pl.DataFrame:
    return pl.read_parquet(SHARED / "roster.parquet", columns=["agent", "name", "lab", "left"])


def period_days(goal_no: int, allow_holdout: bool = False) -> list[str]:
    c = calendar().filter(pl.col("goal_no") == goal_no)
    if not allow_holdout:
        c = c.filter(~pl.col("ho"))
    return sorted(c["pt_date"].to_list())


def unit_of_day(goal_no: int) -> dict[str, str]:
    pu = pl.read_parquet(SHARED / "period_units.parquet").filter(pl.col("goal_no") == goal_no)
    out = {}
    for r in pu.iter_rows(named=True):
        for d in r["days"]:
            out[d] = r["unit_id"]
    return out


def load_calls(goal_no: int, days: list[str]) -> pl.DataFrame:
    return (pl.scan_parquet(SHARED / "call_windows.parquet")
            .filter((pl.col("goal_no") == goal_no) & pl.col("pt_date").is_in(days) & (pl.col("agent") != CLAUDE_CODE))
            .select("turn_id", "agent", "t_call", "pt_date").collect().sort("t_call", "agent"))


def load_commits(goal_no: int, days: list[str]) -> pl.DataFrame:
    return (pl.scan_parquet(SHARED / "work_commits.parquet")
            .filter((pl.col("goal_no") == goal_no) & pl.col("pt_date").is_in(days) & pl.col("canonical") & ~pl.col("imported")
                    & (pl.col("author_kind").cast(pl.String) == "agent") & ~pl.col("automated")
                    & pl.col("author_agent").is_not_null() & (pl.col("author_agent") != CLAUDE_CODE))
            .select(pl.col("author_agent").alias("agent"), pl.col("repo").cast(pl.String), "t", "pt_date").collect())


def project_map() -> pl.DataFrame:
    from project_states import project_map as pm
    return pm()


# ============================================================================================ host labels
def window_labels(commits: pl.DataFrame, W: int = 30) -> pl.DataFrame:
    """Modal repo per (agent, day, W-min window): agent, pt_date, win, repo, t_first (first commit to repo in window),
    t_last (last commit to it), n."""
    cal = calendar().select("pt_date", "win_start")
    c = commits.join(cal, on="pt_date", how="inner")
    c = c.with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // (W * 60)).clip(lower_bound=0)
                       .cast(pl.Int32).alias("win"))
    g = c.group_by("agent", "pt_date", "win", "repo").agg(pl.len().alias("n"), pl.col("t").min().alias("t_first"),
                                                          pl.col("t").max().alias("t_last"))
    g = g.sort(["agent", "pt_date", "win", "n", "t_last", "repo"], descending=[False, False, False, True, True, False])
    return g.group_by("agent", "pt_date", "win", maintain_order=True).first().sort("agent", "t_first")


def replay_events(labels: pl.DataFrame, calls: pl.DataFrame, E: int | None = 100,
                  leave_t: dict[int, dt.datetime] | None = None) -> pl.DataFrame:
    """Label-change events per agent (agent, t, kind, repo, to_repo), kinds arrive/depart/expire/leave; arrive is split
    into recruit/birth later (it needs the global host count)."""
    ct = {a: g["t_call"].to_numpy() for (a,), g in calls.group_by(["agent"])}
    rows = []
    leave_t = leave_t or {}
    for (a,), g in labels.group_by(["agent"], maintain_order=True):
        a = int(a)
        tc = ct.get(a, np.array([], dtype="datetime64[us]"))
        cur, last = None, None

        def expiry_before(t_next):
            if E is None or cur is None or len(tc) == 0:
                return None
            i0 = np.searchsorted(tc, np.datetime64(last.replace(tzinfo=None), "us"), side="right")
            k = i0 + E - 1  # the E-th own call after the last renewal
            if k < len(tc) and (t_next is None or tc[k] < np.datetime64(t_next.replace(tzinfo=None), "us")):
                return tc[k]
            return None

        for r in g.sort("t_first").iter_rows(named=True):
            te = expiry_before(r["t_first"])
            if te is not None:
                rows.append((a, _ts(te), "expire", cur, None))
                cur = None
            if cur == r["repo"]:
                last = max(last, r["t_last"])
                continue
            if cur is not None:
                rows.append((a, r["t_first"], "depart", cur, r["repo"]))
            rows.append((a, r["t_first"], "arrive", r["repo"], None))
            cur, last = r["repo"], r["t_last"]
        lt = leave_t.get(a)
        te = expiry_before(lt)
        if te is not None:
            rows.append((a, _ts(te), "expire", cur, None))
            cur = None
        if lt is not None and cur is not None:
            rows.append((a, lt, "leave", cur, None))
    ev = pl.DataFrame(rows, schema={"agent": pl.Int8, "t": pl.Datetime("us", "UTC"), "kind": pl.String,
                                    "repo": pl.String, "to_repo": pl.String}, orient="row")
    order = pl.col("kind").replace_strict({"expire": 0, "leave": 0, "depart": 1, "arrive": 2}, return_dtype=pl.Int8)
    return ev.with_columns(order.alias("_o")).sort("t", "_o", "agent").drop("_o")


def _ts(x) -> dt.datetime:
    return np.datetime64(x, "us").astype(dt.datetime).replace(tzinfo=dt.timezone.utc)


def classify_arrivals(ev: pl.DataFrame) -> pl.DataFrame:
    """Global replay: n_before for every event; arrivals -> recruit (n >= 1) or birth (n == 0)."""
    hosts: dict[str, int] = {}
    n_before, kinds = [], []
    for kind, repo in zip(ev["kind"].to_list(), ev["repo"].to_list()):
        n = hosts.get(repo, 0)
        n_before.append(n)
        if kind == "arrive":
            kinds.append("recruit" if n >= 1 else "birth")
            hosts[repo] = n + 1
        else:
            kinds.append(kind)
            hosts[repo] = n - 1
    return ev.with_columns(pl.Series("kind", kinds), pl.Series("n_before", n_before, dtype=pl.Int16))


# ============================================================================================ impostor tags
def kickoff_named(goal_no: int, repos: list[str]) -> dict[str, bool]:
    """H54's naming rule for each repo (text held in memory only). The token helpers are the shared verbatim copy
    (kickoff_naming.py; 2026-10-04: this used to load H54's scheme/build.py at run time)."""
    import kickoff_naming as m
    from goal_fields import kickoff_messages, strip_boilerplate
    cal_all = calendar()
    d0 = sorted(cal_all.filter(pl.col("goal_no") == goal_no)["pt_date"].to_list())[0]
    chat_h = (pl.read_parquet(SHARED / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "length"])
              .filter(pl.col("speaker_kind").cast(pl.String) == "human"))
    k, _, _ = kickoff_messages(cal_all.select("pt_date", "win_start"), chat_h, d0)
    ids = k["message_id"].to_list()
    text = pl.read_parquet(SHARED / "chat_text.parquet", columns=["message_id", "text"]).filter(pl.col("message_id").is_in(ids))
    body = " ".join(strip_boilerplate(x or "") for x in text["text"].to_list())
    gtext = {g["goal_no"]: g["goal"] for g in load_goals()}[goal_no]
    gt = m.text_tokens(gtext)
    kt = m.text_tokens(body) - gt
    am = pl.read_parquet(SHARED / "artifact_mentions.parquet").filter(pl.col("message_id").is_in(ids)
                                                                       & pl.col("how").cast(pl.String).is_in(STRICT))
    strict = set(am.join(project_map(), on="artifact")["project"].to_list())
    out = {}
    for r in repos:
        pt = m.name_tokens(r)
        out[r] = bool(r in strict or (pt and (m.tok_match(pt, kt) > 0 or m.tok_match(pt, gt) > 0)))
    del body, text, gtext
    return out


def tag_arrivals(ev: pl.DataFrame, goal_no: int, days: list[str], named: dict[str, bool]) -> pl.DataFrame:
    """Adds cls (known/read/blind/none) and named to arrival rows (recruit, birth)."""
    repos = sorted(set(ev.filter(pl.col("kind").is_in(["recruit", "birth"]))["repo"].to_list()))
    pm = project_map().filter(pl.col("project").is_in(repos))
    am = (pl.scan_parquet(SHARED / "artifact_mentions.parquet")
          .filter(pl.col("artifact").is_in(pm["artifact"].implode()))
          .collect().join(pm, on="artifact"))
    am = am.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    am = am.filter(pl.col("pt_date").is_in(days))
    links = am.filter((pl.col("source").cast(pl.String) == "chat") & pl.col("how").cast(pl.String).is_in(LINK_HOW)
                      & pl.col("message_id").is_not_null()).select("message_id", "t", "agent", "project").unique()
    selfm = am.filter(pl.col("how").cast(pl.String).is_in(STRICT) & (pl.col("speaker_kind").cast(pl.String) == "agent")
                      ).select("agent", "project", "t")
    # ledger reads of link messages: (message_id, reader agent, t_call)
    li = (pl.scan_parquet(SHARED / "context_ledger_items.parquet").filter(pl.col("message_id").is_in(links["message_id"].unique().implode()))
          .select("turn_id", "message_id").collect())
    cw = (pl.scan_parquet(SHARED / "call_windows.parquet").filter(pl.col("turn_id").is_in(li["turn_id"].implode()))
          .select("turn_id", "agent", "t_call").collect())
    reads = li.join(cw, on="turn_id").join(links.select("message_id", "project"), on="message_id")
    L = {p: g.sort("t") for (p,), g in links.group_by(["project"])}
    R = {(int(a), p): g["t_call"].min() for (a, p), g in reads.group_by(["agent", "project"])}
    Rt = {k: sorted(g["t_call"].to_list()) for k, g in ((tuple(k), g) for k, g in reads.group_by(["agent", "project"]))}
    S = {(int(a), p): g["t"].min() for (a, p), g in selfm.group_by(["agent", "project"])}
    hosted_before: dict[tuple[int, str], dt.datetime] = {}
    cls, nm, cls2 = [], [], []
    for a, t, kind, repo in ev.select("agent", "t", "kind", "repo").iter_rows():
        if kind not in ("recruit", "birth"):
            cls.append(None); nm.append(None); cls2.append(None)
            continue
        a = int(a)
        # A2 (post hoc): classify relative to the agent's first touch of the repo (first strict self-mention, else the
        # arrival itself): read (a link was read by then), blind (an unread link was posted in the 30 min before the
        # touch: H28's window), return (re-join of a repo hosted earlier), self (no link involved: stigmergic/independent)
        if (a, repo) in hosted_before:
            c2 = "return"
        else:
            tt = S.get((a, repo))
            tt = tt if (tt is not None and tt < t) else t
            if any(x <= tt for x in Rt.get((a, repo), [])):
                c2 = "read"
            else:
                lk = L.get(repo)
                rec = (lk.filter((pl.col("t") < tt) & (pl.col("t") >= tt - dt.timedelta(seconds=BLIND_S))
                                 & ((pl.col("agent") != a) | pl.col("agent").is_null())).height if lk is not None else 0)
                c2 = "blind" if rec else "self"
        cls2.append(c2)
        known = (S.get((a, repo)) is not None and S[(a, repo)] < t) or ((a, repo) in hosted_before)
        rr = Rt.get((a, repo), [])
        read = any(x <= t for x in rr)
        c = "known" if known else ("read" if read else None)
        if c is None:
            lk = L.get(repo)
            if lk is not None:
                recent = lk.filter((pl.col("t") < t) & (pl.col("t") >= t - dt.timedelta(seconds=BLIND_S))
                                   & ((pl.col("agent") != a) | pl.col("agent").is_null()))
                c = "blind" if recent.height else "none"
            else:
                c = "none"
        cls.append(c); nm.append(bool(named.get(repo, False)))
        hosted_before.setdefault((a, repo), t)
    return ev.with_columns(pl.Series("cls", cls, dtype=pl.String), pl.Series("named", nm, dtype=pl.Boolean),
                           pl.Series("cls_touch", cls2, dtype=pl.String))


# ============================================================================================ bins
def clock_bins(calls: pl.DataFrame, unit_map: dict[str, str], B: int = 200, wall_min: int | None = None) -> pl.DataFrame:
    """calls + bin id. Call clock: rank within unit // B. Wall clock (wall_min): minutes from the day's win_start."""
    c = calls.with_columns(pl.col("pt_date").replace_strict(unit_map, default=None).alias("unit"))
    if wall_min is None:
        c = c.with_columns((pl.int_range(pl.len()).over("unit") // B).alias("k"))
        c = c.with_columns(pl.struct("unit", "k").rank("dense").cast(pl.Int32).alias("bin"))
    else:
        cal = calendar().select("pt_date", "win_start")
        c = c.join(cal, on="pt_date", how="left").with_columns(
            ((pl.col("t_call") - pl.col("win_start")).dt.total_seconds() // (wall_min * 60)).clip(lower_bound=0).alias("k"))
        c = c.with_columns(pl.struct("pt_date", "k").rank("dense").cast(pl.Int32).alias("bin")).drop("win_start")
    return c.sort("t_call")


def bin_table(ev: pl.DataFrame, cb: pl.DataFrame, labs: dict[int, str]) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Per (repo, bin): n (hosts at bin start), n_cum (distinct arrivals before), calls (C), C_host, C_free, counts of
    recruits by class / named, births, departs, expires+leaves, new contributors; and the lab table per (repo, bin, lab):
    n_same, n_cross, C_free_lab, R (formation-free recruits by agents of that lab)."""
    binfo = cb.group_by("bin").agg(pl.col("t_call").min().alias("t0"), pl.col("unit").first(), pl.len().alias("C")).sort("t0")
    bins = binfo["bin"].to_list()
    t0 = binfo["t0"].to_list()
    units = binfo["unit"].to_list()
    Cb = binfo["C"].to_list()
    calls_ab = {}
    cab = cb.group_by("bin", "agent").agg(pl.len().alias("c"))
    for b, a, c in cab.iter_rows():
        calls_ab.setdefault(b, {})[int(a)] = c
    # assign events to bins (by time; events before the first bin go to bin 0, after the last to the last bin)
    t0_np = np.array([np.datetime64(x.replace(tzinfo=None), "us") for x in t0])
    evt = ev["t"].to_numpy()
    ev_bin_idx = np.clip(np.searchsorted(t0_np, evt, side="right") - 1, 0, len(bins) - 1)
    ev = ev.with_columns(pl.Series("bidx", ev_bin_idx))
    host: dict[int, str] = {}
    contributors: dict[str, set] = {}
    rows, lrows = [], []
    evl = ev.to_dicts()
    j = 0
    nE = len(evl)
    allab = sorted(set(labs.values()))
    for bi, b in enumerate(bins):
        # state at bin start: apply all events with bidx < bi
        while j < nE and evl[j]["bidx"] < bi:
            _apply(evl[j], host, contributors)
            j += 1
        k1 = j
        while k1 < nE and evl[k1]["bidx"] == bi:
            k1 += 1
        bev = evl[j:k1]  # applied at the start of the next bin
        ca = calls_ab.get(b, {})
        hosts_of: dict[str, list[int]] = {}
        for a, r in host.items():
            hosts_of.setdefault(r, []).append(a)
        touched = set(hosts_of) | {e["repo"] for e in bev}
        C = Cb[bi]
        for r in touched:
            hs = hosts_of.get(r, [])
            ch = sum(ca.get(a, 0) for a in hs)
            evr = [e for e in bev if e["repo"] == r]
            rec = [e for e in evr if e["kind"] == "recruit"]
            ff = [e for e in rec if e["cls"] != "blind" and not e["named"]]
            ff2 = [e for e in rec if e.get("cls_touch") != "blind" and not e["named"]]
            ncum = len(contributors.get(r, set()))
            newc = sum(1 for e in evr if e["kind"] in ("recruit", "birth") and e["agent"] not in contributors.get(r, set()))
            rows.append({"bin": b, "unit": units[bi], "repo": r, "n": len(hs), "n_cum": ncum, "C": C, "C_host": ch,
                         "C_free": C - ch, "R_all": len(rec), "R_ff": len(ff), "R_ff2": len(ff2),
                         "R_blind2": sum(e.get("cls_touch") == "blind" for e in rec),
                         "R_return": sum(e.get("cls_touch") == "return" for e in rec),
                         "R_known": sum(e["cls"] == "known" for e in rec), "R_read": sum(e["cls"] == "read" for e in rec),
                         "R_blind": sum(e["cls"] == "blind" for e in rec), "R_none": sum(e["cls"] == "none" for e in rec),
                         "R_named": sum(bool(e["named"]) for e in rec),
                         "births": sum(e["kind"] == "birth" for e in evr), "departs": sum(e["kind"] == "depart" for e in evr),
                         "expires": sum(e["kind"] in ("expire", "leave") for e in evr), "new_contrib": newc})
            if len(hs) >= 1:
                for lab in allab:
                    ns = sum(1 for a in hs if labs.get(a) == lab)
                    cfl = sum(c for a, c in ca.items() if labs.get(a) == lab and a not in hs)
                    rl = sum(1 for e in ff if labs.get(e["agent"]) == lab)
                    if cfl > 0 or rl > 0:
                        lrows.append({"bin": b, "unit": units[bi], "repo": r, "lab": lab, "n_same": ns,
                                      "n_cross": len(hs) - ns, "C_free_lab": cfl, "R": rl})
    bt = pl.DataFrame(rows)
    lt = pl.DataFrame(lrows) if lrows else pl.DataFrame(schema={"bin": pl.Int32, "unit": pl.String, "repo": pl.String,
                                                                 "lab": pl.String, "n_same": pl.Int64, "n_cross": pl.Int64,
                                                                 "C_free_lab": pl.Int64, "R": pl.Int64})
    tb = binfo.select("bin", "t0")
    return bt.join(tb, on="bin").sort("bin", "repo"), lt


def _apply(e, host, contributors):
    if e["kind"] in ("recruit", "birth"):
        host[e["agent"]] = e["repo"]
        contributors.setdefault(e["repo"], set()).add(e["agent"])
    elif e["kind"] in ("depart", "expire", "leave"):
        if host.get(e["agent"]) == e["repo"]:
            del host[e["agent"]]


def choice_sets(ev: pl.DataFrame) -> pl.DataFrame:
    """For each formation-free recruitment: the alternatives (repos with n >= 1 at that moment, excluding the recruit's
    current repo) with their n; chosen flag. Used by the conditional-logit variant (v4)."""
    host: dict[int, str] = {}
    cnt: dict[str, int] = {}
    rows = []
    eid = 0
    for e in ev.to_dicts():
        if e["kind"] == "recruit" and e["cls"] != "blind" and not e["named"]:
            cur = host.get(e["agent"])
            alts = [(r, n) for r, n in cnt.items() if n >= 1 and r != cur]
            if len(alts) >= 2 and any(r == e["repo"] for r, _ in alts):
                for r, n in alts:
                    rows.append({"eid": eid, "repo": r, "n": n, "chosen": r == e["repo"]})
                eid += 1
        if e["kind"] == "depart":
            # the paired arrival follows; remove from the old repo now
            cnt[e["repo"]] = cnt.get(e["repo"], 0) - 1
            host.pop(e["agent"], None)
        elif e["kind"] in ("expire", "leave"):
            cnt[e["repo"]] = cnt.get(e["repo"], 0) - 1
            host.pop(e["agent"], None)
        elif e["kind"] in ("recruit", "birth"):
            cnt[e["repo"]] = cnt.get(e["repo"], 0) + 1
            host[e["agent"]] = e["repo"]
    return pl.DataFrame(rows) if rows else pl.DataFrame(schema={"eid": pl.Int64, "repo": pl.String, "n": pl.Int64, "chosen": pl.Boolean})


# ============================================================================================ one call for a period
def leave_times(goal_no: int, calls: pl.DataFrame, days: list[str]) -> dict[int, dt.datetime]:
    """Agents whose roster `left` date falls inside the period (or within 1 day after its last day): their last call."""
    r = roster().filter(pl.col("left").is_not_null())
    out = {}
    last = days[-1]
    for a, left in r.select("agent", "left").iter_rows():
        if days[0] <= left <= (dt.date.fromisoformat(last) + dt.timedelta(days=1)).isoformat():
            ca = calls.filter(pl.col("agent") == a)
            if ca.height:
                out[int(a)] = ca["t_call"].max()
    return out


def build_from_frames(commits, calls, unit_map, labs, named, goal_no, days, W=30, E=100, B=200, wall_min=None,
                      tag=True, leave=None):
    lab = window_labels(commits, W)
    ev = classify_arrivals(replay_events(lab, calls, E=E, leave_t=leave))
    if tag:
        ev = tag_arrivals(ev, goal_no, days, named)
    else:  # synthetic worlds: no chat, every arrival untagged
        ev = ev.with_columns(pl.when(pl.col("kind").is_in(["recruit", "birth"])).then(pl.lit("none")).otherwise(None).alias("cls"),
                             pl.when(pl.col("kind").is_in(["recruit", "birth"])).then(pl.col("repo").replace_strict(named, default=False))
                             .otherwise(None).alias("named"),
                             pl.when(pl.col("kind").is_in(["recruit", "birth"])).then(pl.lit("self")).otherwise(None).alias("cls_touch"))
    cb = clock_bins(calls, unit_map, B=B, wall_min=wall_min)
    bt, lt = bin_table(ev, cb, labs)
    return ev, bt, lt


def build_period(goal_no: int, allow_holdout: bool = False, W=30, E=100, B=200, wall_min=None, named=None):
    days = period_days(goal_no, allow_holdout)
    calls = load_calls(goal_no, days)
    commits = load_commits(goal_no, days)
    umap = unit_of_day(goal_no)
    labs = dict(roster().select("agent", "lab").iter_rows())
    if named is None:
        named = kickoff_named(goal_no, sorted(set(commits["repo"].to_list())))
    leave = leave_times(goal_no, calls, days)
    ev, bt, lt = build_from_frames(commits, calls, umap, labs, named, goal_no, days, W=W, E=E, B=B, wall_min=wall_min,
                                   leave=leave)
    return {"events": ev, "bins": bt, "labs": lt, "named": named, "calls": calls, "commits": commits, "days": days,
            "unit_map": umap, "leave": leave}


def hashed(df: pl.DataFrame, cols=("repo", "to_repo")) -> pl.DataFrame:
    for c in cols:
        if c in df.columns:
            df = df.with_columns(pl.col(c).map_elements(rhash, return_dtype=pl.String).alias(c))
    return df


# ============================================================================================ verify
def verify(periods=(31, 33, 40)) -> bool:
    """Rebuild periods with the defaults and compare with H77's and H78's scheme outputs (data/processed/H7x/G<NN>/
    events, bins, labs, choice and the repo named flags; repo names hashed). Read-only."""
    import json
    res, ok = {}, True
    for g in periods:
        d = build_period(g)
        mine = {"events": hashed(d["events"]), "bins": hashed(d["bins"]), "labs": hashed(d["labs"]),
                "choice": hashed(choice_sets(d["events"]))}
        named = {rhash(k): v for k, v in d["named"].items()}
        for hyp in ("H77-repos-as-replicators", "H78-replicator-growth-order"):
            base = ROOT / "data/processed" / hyp / f"G{g:02d}"
            if not base.exists():
                continue
            r = {}
            for k, df in mine.items():
                old = pl.read_parquet(base / f"{k}.parquet")
                if k == "labs":   # bin_table's labs rows come out of an unordered group_by: compare as sets
                    old, df = old.sort(old.columns), df.sort(df.columns)
                r[k] = "identical" if old.equals(df) else {"rows": [old.height, df.height]}
            rp = pl.read_parquet(base / "repos.parquet")
            r["named"] = "identical" if all(named.get(h, False) == v for h, v in rp.select("repo", "named").iter_rows()) else "differ"
            ok &= all(v == "identical" for v in r.values())
            res[f"{hyp[:3]}/G{g:02d}"] = r
    res["ok"] = bool(ok)
    print(json.dumps(res, indent=1), flush=True)
    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    print(__doc__)
