"""H11 round 2 scheme (2026-10-05): joins, choice sets and exposures (R1, R2) and the output panel (R3).

Reads the round-1b label files (data/processed/H11-potts-labor-vs-herding/r1b/G<NN>/) and shared tables; writes
data/processed/H11-potts-labor-vs-herding/r2/:
  joins_<ch>.parquet    one row per join (agent i's labelled window whose project differs from its previous one):
                        unit, agent, g (window index in the unit), X, prev, kind (recruit | birth), n_choice, tau
                        (decision time), A_tau (active-clock seconds), plus R2d path flags for work recruits
  cands_<ch>.parquet    one row per (join, candidate Y in the choice set): chosen, a (others' labelled windows on Y in
                        the previous L windows), a_lead (next L windows), s (others' cumulative windows), s_tot (all,
                        incl. i), h (habit), m_read, m_unread, m_lead (chat mentions of Y by other agents read / posted
                        but unread / read after tau; 60 active min), c, c_lead (other agents' work commits to Y)
  skel_<ch>.parquet     the replay skeleton: unit, agent, g, project, ev (entry | stay | recruit | birth)
  panel_r3.parquet      agent x window (attention-action label, periods #30+): k_others, active minutes, commits
                        (all, landed, deployed, revert, merge)
  projwin_r3.parquet    project x window: n agents (attention-action), commits to the project by anyone
Channels: work (DQ4 agent work commits) and att (project_states sources = action). Codes only: project names are kept
as in the r1b label files (repo names, no text). Held-out days are never read (labels already exclude them; every
shared table is filtered with holdout_mask / its holdout flag).

Usage: uv run python hypotheses/H11-potts-labor-vs-herding/scheme/build_r2.py
"""
from __future__ import annotations

import bisect
import datetime as dt
import json
import sys
from collections import defaultdict

from h11common import C, OUT, SHARED  # noqa: F401  (sets thread env vars)
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(C.ROOT / "infra/shared"))
import project_states as PS  # noqa: E402

R1B = OUT / "r1b"
R2 = OUT / "r2"
W = 30
L_WIN = 4            # R1 lookback / lead in windows (2 active hours)
LOOK_S = 3600.0      # R2 lookback / lead in active seconds
TAU_MAX_S = 7200.0   # work joins: onset mention at most 2 active hours before the first commit
CLAUDE_CODE = 19
ATT_GOALS = [18, 19, 20, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
WORK_GOALS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
OWN_GROUP = {39, 42, 44, 51}
WORK_FILTER = (pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent")
               & ~pl.col("automated") & pl.col("author_agent").is_not_null() & ~pl.col("holdout"))


# ============================================================================================ units and clock
def units() -> list[dict]:
    """Analysis units: whole goal periods for #18-#44, the non-holdout #51 period units separately."""
    cal = PS.load_calendar(sorted(set(ATT_GOALS)), allow_holdout=False)
    pu = pl.read_parquet(SHARED / "period_units.parquet").filter((pl.col("goal_no") == 51) & ~pl.col("holdout"))
    out = []
    for g in sorted(set(ATT_GOALS)):
        c = cal.filter(pl.col("goal_no") == g).sort("pt_date")
        if g != 51:
            out.append({"unit": f"G{g:02d}", "goal": g, "cal": c})
        else:
            for r in pu.sort("seq").iter_rows(named=True):
                cu = c.filter(pl.col("pt_date").is_in(r["days"]))
                if cu.height:
                    out.append({"unit": r["unit_id"], "goal": 51, "cal": cu})
    return out


class Clock:
    """Active-time clock of a unit: the days' [win_start, win_end] concatenated (seconds)."""

    def __init__(self, cal: pl.DataFrame):
        self.days = cal["pt_date"].to_list()
        self.ws = {d: s for d, s in zip(self.days, cal["win_start"].to_list())}
        self.len = {d: float(x or 0) for d, x in zip(self.days, cal["window_s"].to_list())}
        off, o = {}, 0.0
        for d in self.days:
            off[d] = o
            o += self.len[d]
        self.off = off
        self.total = o
        # sorted day starts for vectorised mapping
        self.starts = np.array([self.ws[d].timestamp() for d in self.days])
        self.offs = np.array([off[d] for d in self.days])
        self.lens = np.array([self.len[d] for d in self.days])

    def A(self, ts: np.ndarray) -> np.ndarray:
        """Active seconds for unix times ts; times outside every active day window -> clipped into the nearest day
        window that starts at or before them (overnight -> end of the previous day); before the first day -> nan."""
        ts = np.asarray(ts, dtype=float)
        i = np.searchsorted(self.starts, ts, side="right") - 1
        out = np.full(ts.shape, np.nan)
        ok = i >= 0
        ii = i[ok]
        out[ok] = self.offs[ii] + np.clip(ts[ok] - self.starts[ii], 0, self.lens[ii])
        return out


def unix(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(float) / 1e6


# ============================================================================================ inputs
def load_labels(goal: int, ch: str, cal: pl.DataFrame) -> pl.DataFrame:
    f = "labels_work_w30" if ch == "work" else "labels_projectact_w30"
    p = R1B / f"G{goal:02d}" / f"{f}.parquet"
    if not p.exists():
        return pl.DataFrame()
    lab = pl.read_parquet(p).filter(pl.col("pt_date").is_in(cal["pt_date"].to_list()) & (pl.col("agent") != CLAUDE_CODE))
    wins = pl.read_parquet(R1B / f"G{goal:02d}" / "windows_w30.parquet").filter(
        pl.col("pt_date").is_in(cal["pt_date"].to_list())).sort("pt_date", "win")
    wins = wins.with_columns(pl.int_range(pl.len()).alias("g"))
    lab = lab.join(wins.select("pt_date", "win", "g", "t_mid"), on=["pt_date", "win"], how="inner")
    return lab.select("pt_date", "win", "g", "t_mid", pl.col("agent").cast(pl.Int16), "project", "room").sort("g", "agent")


_CACHE: dict = {}


def strict_action_mentions() -> pl.DataFrame:
    if "sam" not in _CACHE:
        pm = PS.project_map()
        am = pl.scan_parquet(SHARED / "artifact_mentions.parquet").filter(
            (pl.col("speaker_kind").cast(pl.String) == "agent") & (pl.col("source").cast(pl.String) == "action")
            & pl.col("how").cast(pl.String).is_in(["url", "output", "bare"]) & pl.col("agent").is_not_null()
        ).select("artifact", "t", "agent").collect()
        am = am.join(pm, on="artifact", how="inner").select("t", pl.col("agent").cast(pl.Int16), "project")
        am = am.filter(~pl.Series(C.holdout_mask(am["t"].dt.convert_time_zone("America/Los_Angeles").dt.date()
                                                   .cast(pl.String).to_list(), [None] * am.height)))
        _CACHE["sam"] = am.sort("t")
    return _CACHE["sam"]


def work_commits() -> pl.DataFrame:
    if "wc" not in _CACHE:
        wc = pl.scan_parquet(SHARED / "work_commits.parquet").filter(WORK_FILTER).select(
            pl.col("repo").cast(pl.String).alias("project"), "t", "hash", pl.col("author_agent").cast(pl.Int16).alias("agent"),
            "on_default", "is_merge", "pages_branch", "deploy_msg", "is_revert", "pt_date").collect()
        wc = wc.filter(pl.col("agent") != CLAUDE_CODE)
        _CACHE["wc"] = wc.sort("t")
    return _CACHE["wc"]


def chat_mentions() -> pl.DataFrame:
    if "pm" not in _CACHE:
        pm = pl.read_parquet(SHARED / "project_mentions_chat.parquet").filter(~pl.col("holdout")).select(
            "message_id", "t", "room", pl.col("agent").cast(pl.Int16).alias("sender"), "project")
        _CACHE["pm"] = pm.unique(["message_id", "project"]).sort("t")
    return _CACHE["pm"]


def deliveries(days: list[str]) -> pl.DataFrame:
    """(recipient, message_id, t_call) for the chat-mention messages delivered on these days (DQ1 ledger)."""
    if "dl" not in _CACHE:
        turns = pl.scan_parquet(SHARED / "context_ledger_turns.parquet").filter(~pl.col("holdout")).select(
            "turn_id", "agent", "t_call", "pt_date").collect()
        mids = chat_mentions()["message_id"].unique()
        items = pl.scan_parquet(SHARED / "context_ledger_items.parquet").filter(
            pl.col("message_id").is_in(mids.implode())).select("turn_id", "message_id").collect()
        d = items.join(turns, on="turn_id", how="inner")
        _CACHE["dl"] = d.select(pl.col("agent").cast(pl.Int16).alias("recipient"), "message_id", "t_call", "pt_date")
    return _CACHE["dl"].filter(pl.col("pt_date").is_in(days)).drop("pt_date")


def printed_hashes() -> pl.DataFrame:
    """(agent, t, hash7) for commit hashes printed in an agent's own command output."""
    if "ph" not in _CACHE:
        a = pl.scan_parquet(SHARED / "artifact_commands_text.parquet").select("t", "agent", "out_hashes").filter(
            pl.col("out_hashes").list.len() > 0).collect().explode("out_hashes")
        a = a.select("t", pl.col("agent").cast(pl.Int16), pl.col("out_hashes").str.slice(0, 7).alias("h7"))
        _CACHE["ph"] = a
    return _CACHE["ph"]


# ============================================================================================ events
def events(lab: pl.DataFrame) -> pl.DataFrame:
    """Per labelled agent-window: ev = entry | stay | recruit | birth; prev project."""
    lab = lab.sort("agent", "g").with_columns(pl.col("project").shift(1).over("agent").alias("prev"))
    first_g = lab.group_by("project").agg(pl.col("g").min().alias("g0"))
    lab = lab.join(first_g, on="project")
    ev = (pl.when(pl.col("prev").is_null()).then(pl.lit("entry"))
          .when(pl.col("prev") == pl.col("project")).then(pl.lit("stay"))
          .when(pl.col("g0") < pl.col("g")).then(pl.lit("recruit"))
          .otherwise(pl.lit("birth")))
    return lab.with_columns(ev.alias("ev")).drop("g0").sort("g", "agent")


def count_cubes(lab: pl.DataFrame, projects: list[str], agents: list[int], G: int):
    """cum_tot[g, p] = windows on p before g (all agents); cum_ag[a][g, p] per agent."""
    pi = {p: k for k, p in enumerate(projects)}
    ai = {a: k for k, a in enumerate(agents)}
    M = np.zeros((len(agents), G + 1, len(projects)), dtype=np.int32)
    for a, g, p in zip(lab["agent"].to_list(), lab["g"].to_list(), lab["project"].to_list()):
        M[ai[a], g + 1, pi[p]] += 1
    cum_ag = np.cumsum(M, axis=1)
    return cum_ag.sum(axis=0), cum_ag, pi, ai


# ============================================================================================ build one unit
def build_unit(u: dict, ch: str):
    cal = u["cal"]
    lab = load_labels(u["goal"], ch, cal)
    if lab.height == 0:
        return None
    clock = Clock(cal)
    ev = events(lab)
    projects = sorted(ev["project"].unique().to_list())
    agents = sorted(ev["agent"].unique().to_list())
    G = int(ev["g"].max()) + 1
    cum_tot, cum_ag, pi, ai = count_cubes(ev, projects, agents, G)

    def win_count(cum, g0, g1):  # windows in [g0, g1) clipped
        g0, g1 = max(g0, 0), min(max(g1, 0), G)
        return cum[g1] - cum[g0] if g1 > g0 else np.zeros(cum.shape[1], dtype=np.int32)

    first_g = {p: g for p, g in ev.group_by("project").agg(pl.col("g").min()).iter_rows()}
    joins = ev.filter(pl.col("ev").is_in(["recruit", "birth"]))

    # ---- decision times tau
    days = cal["pt_date"].to_list()
    wins_ws = {d: s for d, s in zip(days, cal["win_start"].to_list())}
    sam = strict_action_mentions().filter(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date()
                                          .cast(pl.String).is_in(days))
    sam_by = defaultdict(list)
    for a, p, t in zip(sam["agent"].to_list(), sam["project"].to_list(), unix(sam["t"]).tolist()):
        sam_by[(a, p)].append(t)
    wc_all = work_commits()
    wc = wc_all.filter(pl.col("pt_date").is_in(days))
    wc_by_ap = defaultdict(list)
    wc_by_a = defaultdict(list)
    wc_by_p = defaultdict(list)
    for a, p, t in zip(wc["agent"].to_list(), wc["project"].to_list(), unix(wc["t"]).tolist()):
        wc_by_ap[(a, p)].append(t)
        wc_by_a[a].append((t, p))
        wc_by_p[p].append((t, a))
    for d in (wc_by_ap, wc_by_a, wc_by_p):
        for k in d:
            d[k].sort()

    rows_j = []
    for r in joins.iter_rows(named=True):
        a, X, d, w = r["agent"], r["project"], r["pt_date"], r["win"]
        w0 = wins_ws[d].timestamp() + w * W * 60
        w1 = w0 + W * 60
        tau = None
        if ch == "att":
            ts = sam_by.get((a, X), [])
            k = bisect.bisect_left(ts, w0)
            tau = ts[k] if k < len(ts) and ts[k] < w1 + 1 else w0
        else:
            cs = wc_by_ap.get((a, X), [])
            k = bisect.bisect_left(cs, w0)
            t_c = cs[k] if k < len(cs) else w0
            # last commit by a to another repo before t_c
            prev_t = -np.inf
            for (t, p) in reversed(wc_by_a.get(a, [])):
                if t < t_c and p != X:
                    prev_t = t
                    break
            ts = sam_by.get((a, X), [])
            k2 = bisect.bisect_right(ts, prev_t)
            tau = t_c
            if k2 < len(ts) and ts[k2] <= t_c:
                A_on, A_c = clock.A(np.array([ts[k2], t_c]))
                if A_c - A_on <= TAU_MAX_S:
                    tau = ts[k2]
        rows_j.append({**r, "tau": tau, "t_win0": w0})
    if not rows_j:
        return {"ev": ev, "joins": None, "cands": None, "clock": clock}
    J = pl.DataFrame(rows_j).with_columns(pl.Series("A_tau", clock.A(np.array([x["tau"] for x in rows_j]))))

    # ---- chat mentions and deliveries for R2
    pm = chat_mentions().filter(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).is_in(days))
    pm = pm.with_columns(pl.Series("A", clock.A(unix(pm["t"]))))
    post_by_p = defaultdict(list)  # project -> list of (A, sender, message_id)
    for p, s, m, A in zip(pm["project"].to_list(), pm["sender"].to_list(), pm["message_id"].to_list(), pm["A"].to_list()):
        post_by_p[p].append((A, s, m))
    for p in post_by_p:
        post_by_p[p].sort()
    dl = deliveries(days).join(pm.select("message_id", "project", "sender"), on="message_id", how="inner")
    dl = dl.with_columns(pl.Series("A", clock.A(unix(dl["t_call"]))))
    deliv = defaultdict(list)          # (recipient, project) -> sorted A of deliveries of others' mentions
    deliv_msg = {}                     # (recipient, message_id) -> earliest delivery A
    for rcp, p, s, m, A in zip(dl["recipient"].to_list(), dl["project"].to_list(), dl["sender"].to_list(),
                               dl["message_id"].to_list(), dl["A"].to_list()):
        if s == rcp:
            continue
        deliv[(rcp, p)].append(A)
        key = (rcp, m)
        deliv_msg[key] = min(deliv_msg.get(key, np.inf), A)
    for k in deliv:
        deliv[k].sort()
    wcA_by_p = {p: (np.array(clock.A(np.array([t for t, _ in v]))), np.array([x for _, x in v])) for p, v in wc_by_p.items()}

    def n_in(arr, lo, hi, lo_open=False):
        i0 = bisect.bisect_right(arr, lo) if lo_open else bisect.bisect_left(arr, lo)
        return bisect.bisect_right(arr, hi) - i0

    # ---- candidates
    rows_c = []
    jrows = []
    for jid, r in enumerate(J.iter_rows(named=True)):
        a, g, X, prev, kind, Aτ = r["agent"], r["g"], r["project"], r["prev"], r["ev"], r["A_tau"]
        own_cum = cum_ag[ai[a]]
        tot_prev = win_count(cum_tot, g - L_WIN, g) - win_count(own_cum, g - L_WIN, g)
        tot_lead = win_count(cum_tot, g + 1, g + 1 + L_WIN) - win_count(own_cum, g + 1, g + 1 + L_WIN)
        s_oth = cum_tot[g] - own_cum[g]
        s_tot = cum_tot[g]
        h = own_cum[g] > 0
        choice = [p for p in projects if first_g[p] < g and p != prev]
        jrows.append({"jid": jid, "agent": a, "g": g, "X": X, "prev": prev, "kind": kind, "n_choice": len(choice),
                      "tau": r["tau"], "A_tau": Aτ, "pt_date": r["pt_date"]})
        if kind != "recruit" or len(choice) < 2:
            continue
        for p in choice:
            k = pi[p]
            posts = post_by_p.get(p, [])
            m_unread = 0
            if posts and np.isfinite(Aτ):
                i0 = bisect.bisect_left(posts, (Aτ - LOOK_S,))
                for (A_m, s, mid) in posts[i0:]:
                    if A_m >= Aτ:
                        break
                    if s == a:
                        continue
                    if deliv_msg.get((a, mid), np.inf) > Aτ:
                        m_unread += 1
            dv = deliv.get((a, p), [])
            m_read = n_in(dv, Aτ - LOOK_S, Aτ) if dv else 0
            m_lead = n_in(dv, Aτ, Aτ + LOOK_S, lo_open=True) if dv else 0
            c = c_lead = 0
            if p in wcA_by_p:
                At, au = wcA_by_p[p]
                oth = au != a
                c = int(((At >= Aτ - LOOK_S) & (At < Aτ) & oth).sum())
                c_lead = int(((At > Aτ) & (At <= Aτ + LOOK_S) & oth).sum())
            rows_c.append({"jid": jid, "Y": p, "chosen": p == X, "a": int(tot_prev[k]), "a_lead": int(tot_lead[k]),
                           "s": int(s_oth[k]), "s_tot": int(s_tot[k]), "h": bool(h[k]), "m_read": m_read,
                           "m_unread": m_unread, "m_lead": m_lead, "c": c, "c_lead": c_lead})
    jdf = pl.DataFrame(jrows)
    cdf = pl.DataFrame(rows_c) if rows_c else None

    # ---- R2d path flags (work recruits): read mention / seen commits in the 60 active min before the first commit
    if ch == "work" and jdf.height:
        ph = printed_hashes()
        ph = ph.filter(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).is_in(days))
        h2c = {h[:7]: (p, au) for h, p, au in zip(wc_all["hash"].to_list(), wc_all["project"].to_list(), wc_all["agent"].to_list())}
        seen = defaultdict(list)  # (agent, project) -> A of printing others' commits
        pA = clock.A(unix(ph["t"]))
        for a_, h7, A_ in zip(ph["agent"].to_list(), ph["h7"].to_list(), pA.tolist()):
            hit = h2c.get(h7)
            if hit and hit[1] != a_:
                seen[(a_, hit[0])].append(A_)
        for k in seen:
            seen[k].sort()
        f_read, f_seen, first = [], [], []
        for r in jdf.iter_rows(named=True):
            a, X = r["agent"], r["X"]
            cs = wc_by_ap.get((a, X), [])
            # first commit of the join window (tau <= first commit)
            t_c = cs[bisect.bisect_left(cs, r["tau"])] if cs and bisect.bisect_left(cs, r["tau"]) < len(cs) else r["tau"]
            Ac = float(clock.A(np.array([t_c]))[0])
            dv = deliv.get((a, X), [])
            rd = [x for x in dv if Ac - LOOK_S <= x <= Ac]
            sn = [x for x in seen.get((a, X), []) if Ac - LOOK_S <= x <= Ac]
            f_read.append(bool(rd))
            f_seen.append(bool(sn))
            first.append(None if not (rd and sn) else ("read" if min(rd) < min(sn) else "seen"))
        jdf = jdf.with_columns(pl.Series("p_read", f_read), pl.Series("p_seen", f_seen), pl.Series("p_first", first, dtype=pl.String))
    return {"ev": ev, "joins": jdf, "cands": cdf, "clock": clock}


# ============================================================================================ R3 panel
def build_r3(u: dict):
    cal = u["cal"]
    if u["goal"] < 30:
        return None, None
    lab = load_labels(u["goal"], "att", cal)
    if lab.height == 0:
        return None, None
    days = cal["pt_date"].to_list()
    k = lab.group_by("g", "project").agg(pl.len().alias("n_on"))
    lab = lab.join(k, on=["g", "project"]).with_columns((pl.col("n_on") - 1).alias("k_others"))
    # active minutes (state act / talk) per agent-window
    ab = pl.scan_parquet(SHARED / "activity_bins_fixed.parquet").filter(pl.col("pt_date").is_in(days)).select(
        "pt_date", "minute", pl.col("agent").cast(pl.Int16), "state").collect()
    ab = ab.with_columns((pl.col("minute") // W).cast(pl.Int16).alias("win")).group_by("pt_date", "win", "agent").agg(
        pl.col("state").is_in([3, 4]).sum().alias("act_min"))
    lab = lab.join(ab, on=["pt_date", "win", "agent"], how="left").with_columns(pl.col("act_min").fill_null(0))
    wc = work_commits().filter(pl.col("pt_date").is_in(days))
    cal2 = cal.select("pt_date", "win_start")
    wc = wc.join(cal2, on="pt_date").with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() // (W * 60)).clip(lower_bound=0).cast(pl.Int16).alias("win"))
    per_ag = wc.group_by("pt_date", "win", "agent").agg(
        pl.len().alias("n_commit"), (pl.col("on_default") & ~pl.col("is_merge")).sum().alias("n_land"),
        (pl.col("pages_branch") | pl.col("deploy_msg")).sum().alias("n_deploy"), pl.col("is_revert").sum().alias("n_revert"),
        pl.col("is_merge").sum().alias("n_merge"))
    panel = lab.join(per_ag, on=["pt_date", "win", "agent"], how="left").with_columns(
        [pl.col(c).fill_null(0).cast(pl.Int32) for c in ["n_commit", "n_land", "n_deploy", "n_revert", "n_merge"]])
    panel = panel.with_columns(pl.lit(u["unit"]).alias("unit"), pl.lit(u["goal"]).cast(pl.Int16).alias("goal"))
    per_p = wc.group_by("pt_date", "win", "project").agg(pl.len().alias("c_proj"))
    pw = lab.group_by("pt_date", "win", "g", "project").agg(pl.len().alias("n_ag"), pl.col("act_min").sum().alias("act_min"))
    pw = pw.join(per_p, on=["pt_date", "win", "project"], how="left").with_columns(pl.col("c_proj").fill_null(0).cast(pl.Int32))
    pw = pw.with_columns(pl.lit(u["unit"]).alias("unit"), pl.lit(u["goal"]).cast(pl.Int16).alias("goal"))
    return panel.drop("t_mid"), pw


# ============================================================================================ main
def main():
    R2.mkdir(parents=True, exist_ok=True)
    us = units()
    out = {ch: {"joins": [], "cands": [], "skel": []} for ch in ("work", "att")}
    panels, pws = [], []
    summary = {}
    for u in us:
        for ch in ("work", "att"):
            if ch == "work" and u["goal"] not in WORK_GOALS:
                continue
            res = build_unit(u, ch)
            if res is None:
                continue
            sk = res["ev"].select(pl.lit(u["unit"]).alias("unit"), pl.lit(u["goal"]).cast(pl.Int16).alias("goal"),
                                  "agent", "g", "pt_date", "project", "ev")
            out[ch]["skel"].append(sk)
            if res["joins"] is not None and res["joins"].height:
                jd = res["joins"].with_columns(pl.lit(u["unit"]).alias("unit"), pl.lit(u["goal"]).cast(pl.Int16).alias("goal"))
                out[ch]["joins"].append(jd)
                if res["cands"] is not None:
                    out[ch]["cands"].append(res["cands"].with_columns(pl.lit(u["unit"]).alias("unit")))
                nrec = jd.filter((pl.col("kind") == "recruit") & (pl.col("n_choice") >= 2)).height
                summary.setdefault(u["unit"], {})[ch] = {"joins": jd.height, "recruits_testable": nrec}
        p, pw = build_r3(u)
        if p is not None:
            panels.append(p)
            pws.append(pw)
        print(u["unit"], summary.get(u["unit"]), flush=True)
    for ch in out:
        for k, v in out[ch].items():
            if v:
                pl.concat(v, how="diagonal_relaxed").write_parquet(R2 / f"{k}_{ch}.parquet", compression="zstd")
    pl.concat(panels, how="diagonal_relaxed").write_parquet(R2 / "panel_r3.parquet", compression="zstd")
    pl.concat(pws, how="diagonal_relaxed").write_parquet(R2 / "projwin_r3.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H11-potts-labor-vs-herding/scheme/build_r2.py", "git_commit": C.git_commit(),
            "inputs": [{"source": "ai-village", "revision": C.REVISION,
                        "tables": ["r1b labels (project_states sources=action; DQ4 work labels)", "calendar", "period_units",
                                   "artifact_mentions", "artifacts", "work_commits", "project_mentions_chat",
                                   "context_ledger_items", "context_ledger_turns", "artifact_commands_text (out_hashes only)",
                                   "activity_bins_fixed"],
                        "via": "data/processed/shared and data/processed/H11-potts-labor-vs-herding/r1b"}],
            "params": {"W": W, "L_WIN": L_WIN, "LOOK_S": LOOK_S, "TAU_MAX_S": TAU_MAX_S, "att_goals": ATT_GOALS,
                       "work_goals": WORK_GOALS, "units": "whole periods #18-#44; non-holdout #51 period units",
                       "holdout": "labels exclude held-out days; shared tables filtered by holdout flag / holdout_mask"},
            "rows": summary, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (R2 / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
