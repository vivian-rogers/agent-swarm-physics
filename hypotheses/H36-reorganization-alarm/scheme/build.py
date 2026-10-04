"""H36 scheme: builds data/processed/H36-reorganization-alarm/ from the shared tables (non-holdout days only; no text).

Outputs:
  events.parquet      transition catalog: event_id, cls (goal / room / scaffold / roster / operator), ref, label, t,
                      pt_date0 (day 0), aday0 (calendar active-day index), holdout0, confounded (same day 0 as another
                      primary-class event), all_refs_same_day
  allevents.parquet   every catalogued event used to exclude placebo days (incl. roster joins/leaves, room changes)
  day_stats.parquet   one row per non-holdout active day with >= 3 day-present agents: calendar facts, outage minutes,
                      every physics statistic (primary stall mask; variants _none, _lull, _b5), content statistics,
                      rival inputs (R1_shift, R2_level, R3_polar) and consolidations per present agent
  G<NN>/day_stats.parquet   per-goal-period copies
Holdout days are dropped with a hard assertion (calendar.holdout and infra holdout_mask must agree).

Usage: uv run python hypotheses/H36-reorganization-alarm/scheme/build.py [--catalog-only] [--workers 2]

Round 1b (improved data, 2026-10-04): switches that keep the round-1 path runnable (defaults = round 1):
  --data-version old | fixed     fixed = activity_bins_fixed (DQ8 event-drop fix) + shared outages_fixed/outages.parquet
                                 as the stall mask (same rule: village_off | cause in {scheduled, infra_error} | infra_burst)
  --model bge_small | gte_modernbert   content windows (agent_win30) and R1/R3 agent-day vectors from either model (DQ5)
  --dedupe none | restate | copies     recompute window and agent-day vectors without flagged chat statements
                                 (restate = the model's own self-repeat flag; copies = self_repeat_both)
  --catalog r1 | r1b             r1b adds the corrected and new NE dates as class `r1b` targets (NE39 2025-07-01,
                                 NE40 2026-04-20, NE43a 08-05, NE43b 08-21, NE44 06-11 (held out), NE45 07-29) and flags
                                 NE06 as confounded; they also enter the placebo-exclusion list
  every 1b build adds the activity variant `_trim` (DQ8: each day trimmed to the all-present window, the minutes in
  which every present agent is between its first and last record, before surrogates are drawn)
  --r1b TAG                      write to data/processed/H36-reorganization-alarm/r1b/<TAG>/ instead of the round-1 files
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import h36lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

H38 = L.ROOT / "data/processed/H38-platform-stalls"
EMB = L.SH / "embeddings"
# Round 1b switches (set by main(); defaults reproduce round 1, so confirm.py and old calls are unchanged)
CFG = {"data_version": "old", "model": "bge_small", "dedupe": "none", "trim": False}
R1B_CATALOG = False
SUFFIX = {"bge_small": "", "gte_modernbert": "_gte_modernbert"}
FLAGCOL = {("restate", "bge_small"): "self_repeat", ("restate", "gte_modernbert"): "self_repeat_gte",
           ("copies", "bge_small"): "self_repeat_both", ("copies", "gte_modernbert"): "self_repeat_both"}


def dedup_vectors(level: str, dl: list[str]):
    """Round 1b: agent_<level> raw mean vectors (normalized mean of raw statement embeddings, the shared
    build_agent_vectors rule) recomputed without flagged chat statements, for the given days. Returns (frame with gid,
    agent, pt_date[, win30], vectors (n, d))."""
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    from embed_models import statement_embeddings
    keys = ["agent", "pt_date"] + (["win30"] if level == "win30" else [])
    st = pl.read_parquet(EMB / "statements.parquet").with_row_index("srow").filter(pl.col("pt_date").is_in(dl))
    if level == "win30":
        st = st.filter(pl.col("win30").is_not_null())
    fl = pl.read_parquet(L.SH / "statement_flags.parquet", columns=["srow", FLAGCOL[(CFG["dedupe"], CFG["model"])]])
    st = st.join(fl, on="srow", how="left")
    st = st.filter(~(pl.col(FLAGCOL[(CFG["dedupe"], CFG["model"])]).fill_null(False) & (pl.col("kind") == "chat")))
    E = statement_embeddings(CFG["model"], st.select("kind", "src_row"))
    E = E / np.clip(np.linalg.norm(E, axis=1, keepdims=True), 1e-9, None)
    g = st.select(keys).with_row_index("r").group_by(keys, maintain_order=True).agg(pl.col("r")).sort(keys)
    V = np.zeros((g.height, E.shape[1]), np.float32)
    for n, ix in enumerate(g["r"].to_list()):
        v = E[np.asarray(ix)].mean(0)
        V[n] = v / max(np.linalg.norm(v), 1e-9)
    return g.drop("r").with_row_index("gid").with_columns(pl.col("gid").cast(pl.UInt32)), V


def window_vectors(dl: list[str]):
    if CFG["dedupe"] != "none":
        return dedup_vectors("win30", dl)
    aw = pl.read_parquet(EMB / "agent_win30.parquet").filter(pl.col("pt_date").is_in(dl))
    vec = np.load(EMB / f"agent_win30_vec{SUFFIX[CFG['model']]}.npy", mmap_mode="r")
    return aw, vec


def day_vectors(dl: list[str] | None):
    """(agent_day frame with gid and holdout, vectors) for R1/R3; dl None = all days (the shared table)."""
    ad = pl.read_parquet(EMB / "agent_day.parquet")
    if CFG["dedupe"] == "none":
        return ad, np.load(EMB / f"agent_day_vec{SUFFIX[CFG['model']]}.npy").astype(np.float32)
    days = ad.filter(~pl.col("holdout"))["pt_date"].unique().to_list() if dl is None else dl
    g, V = dedup_vectors("day", sorted(set(days)))
    hol = ad.select("pt_date", "holdout").unique()
    return g.join(hol, on="pt_date", how="left").with_columns(pl.col("holdout").fill_null(False)), V
PT = "America/Los_Angeles"

# Classes per the card (Transitions; Amendment 0). Scaffold = documented scaffold NEs; roster = batch roster NEs.
SCAFFOLD = ["NE01", "NE02", "NE03", "NE04", "NE05", "NE06", "NE07", "NE08", "NE09", "NE10", "NE11", "NE12", "NE13",
            "NE14", "NE16", "NE17", "NE18", "NE19", "NE20", "NE21", "NE22", "NE23", "NE24", "NE25", "NE26", "NE38"]
ROSTER = ["NE27", "NE28", "NE29", "NE30", "NE31", "NE32", "NE33"]
OPERATOR = ["NE35", "NE36", "NE37"]
ROOM_EVENTS = {  # room code -> (ref, label); moves of >= 2 established agents (Amendment 0b)
    1: ("NE-voted-out", "#voted-out room opens (inside #34)"),
    2: ("NE15", "#best/#rest split"),
    4: ("NE42a", "merge into #universe-coordination"),
    14: ("NE-side-room", "side-room (2 agents, 4 h)"),
    15: ("NE-focus", "#focus room opens"),
}


def calendar() -> pl.DataFrame:
    cal = pl.read_parquet(L.SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String)).sort("pt_date")
    hm = L.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    assert cal["holdout"].to_list() == hm, "calendar.holdout disagrees with holdout_mask"
    cal = cal.with_row_index("aday").with_columns(pl.col("aday").cast(pl.Int32))
    d = cal["pt_date"].str.to_date()
    gap = (d - d.shift(1)).dt.total_days()
    return cal.with_columns(gap.alias("gap_days"), (gap >= 3).fill_null(False).alias("monday"))


def day0_index(cal: pl.DataFrame, t) -> int | None:
    """First active day whose window is not over at time t (the day containing t if t is inside or before its window)."""
    import datetime as dt
    from zoneinfo import ZoneInfo
    pt = t.astimezone(ZoneInfo(PT)).date().isoformat()
    for r in cal.select("aday", "pt_date", "win_end").iter_rows():
        if r[1] > pt or (r[1] == pt and t <= r[2]):
            return int(r[0])
    return None


def catalog(cal: pl.DataFrame):
    k = pl.read_parquet(L.SH / "kicks.parquet")
    rooms = pl.read_parquet(L.SH / "rooms.parquet")
    rt = pl.read_parquet(L.SH / "rooms_timeline.parquet")
    import datetime as dt
    UTC = dt.timezone.utc
    rows = []
    for t, kind, ref in k.filter(pl.col("kind").is_in(["goal_kickoff", "natural_experiment"])).select("t", "kind", "ref").iter_rows():
        if kind == "goal_kickoff":
            g = int(ref[1:])
            if g == 1:
                continue
            rows.append(dict(cls="goal", ref=f"#{g}", label=f"goal #{g} kickoff", t=t))
        else:
            if ref == "NE10":
                t = dt.datetime(2026, 2, 13, 17, 0, tzinfo=UTC)  # Amendment 0c: first observed nudge (H04)
            if ref == "NE15":
                continue  # scored as a room event from the rooms table
            cls = "scaffold" if ref in SCAFFOLD else "roster" if ref in ROSTER else "operator" if ref in OPERATOR else "other"
            rows.append(dict(cls=cls, ref=ref, label=ref, t=t))
    # NE14 scored at the 03-24 regime boundary (the 03-11 start is held out)
    rows.append(dict(cls="scaffold", ref="NE14b", label="NE14 regime II->III boundary (perma-computer-use)",
                     t=dt.datetime(2026, 3, 24, 15, 0, tzinfo=UTC)))
    for code, (ref, label) in ROOM_EVENTS.items():
        first = rt.filter(pl.col("room") == code)["t_start"].min()
        rows.append(dict(cls="room", ref=ref, label=label, t=first))
    back = rt.filter(pl.col("room").is_in([2, 3]) & (pl.col("t_start").dt.date() == dt.date(2026, 5, 11)))["t_start"].min()
    rows.append(dict(cls="room", ref="NE42b", label="split back to #best/#rest", t=back))
    if R1B_CATALOG:
        # Round 1b (2026-10-04): corrected and new NE dates from the catalog (DQ9, H35, H56); class r1b so the
        # pre-registered class metrics keep their round-1 composition. Times are 17:00 UTC (= before or inside the
        # PT day's window) unless the record gives one.
        for ref, label, t in [
            ("NE39", "public chat closed (undocumented; dated by DQ9)", dt.datetime(2025, 7, 1, 17, 0, tzinfo=UTC)),
            ("NE40", "history-search answerer swap (undocumented; dated by H56, with NE18)", dt.datetime(2026, 4, 20, 17, 0, tzinfo=UTC)),
            ("NE43a", "daily pause/resume bookends stop (last 08-05 00:00 UTC)", dt.datetime(2026, 8, 5, 17, 0, tzinfo=UTC)),
            ("NE43b", "nudger off (last nudge 08-20 17:42 UTC)", dt.datetime(2026, 8, 21, 17, 0, tzinfo=UTC)),
            ("NE44", "pause default 12 h -> 5 min (with NE22)", dt.datetime(2026, 6, 11, 17, 0, tzinfo=UTC)),
            ("NE45", "history-search tool schema change (undocumented; H56)", dt.datetime(2026, 7, 29, 17, 0, tzinfo=UTC)),
        ]:
            rows.append(dict(cls="r1b", ref=ref, label=label, t=t))
    ev = pl.DataFrame(rows).with_columns(pl.col("t").dt.cast_time_unit("us"))
    ev = ev.with_columns(pl.Series("aday0", [day0_index(cal, t) for t in ev["t"].to_list()], dtype=pl.Int32))
    ev = ev.join(cal.select(pl.col("aday").alias("aday0"), pl.col("pt_date").alias("pt_date0"),
                            pl.col("holdout").alias("holdout0"), pl.col("goal_no").alias("goal0"),
                            pl.col("regime").alias("regime0")), on="aday0", how="left")
    prim = ev.filter(pl.col("cls").is_in(["goal", "room", "scaffold", "roster"]))
    same = prim.group_by("aday0").agg(pl.col("ref").alias("refs"))
    ev = ev.join(same, on="aday0", how="left").with_columns(
        pl.col("refs").list.len().gt(1).fill_null(False).alias("confounded"),
        pl.col("refs").list.join(",").alias("all_refs_same_day")).drop("refs")
    if R1B_CATALOG:   # DQ9: NE06 coincides with all-agent system-prompt changes (2025-11-20/21)
        ev = ev.with_columns(pl.when(pl.col("ref") == "NE06").then(True).otherwise(pl.col("confounded")).alias("confounded"))
        r1b_same = ev.filter(pl.col("cls").is_in(["goal", "room", "scaffold", "roster", "operator", "r1b"])).group_by("aday0").agg(pl.col("ref").alias("refs2"))
        ev = ev.join(r1b_same, on="aday0", how="left").with_columns(pl.col("refs2").list.join(",").alias("all_refs_same_day_r1b")).drop("refs2")
    ev = ev.sort("t").with_row_index("event_id")
    # every catalogued event (placebo exclusion): + roster joins/leaves, room creations/deletions
    ex = [(t,) for t in ev["t"].to_list()]
    ex += [(t,) for t in k.filter(pl.col("kind").is_in(["roster_join", "roster_leave"]))["t"].to_list()]
    for c, d in rooms.select("created_at", "deleted_at").iter_rows():
        for s in (c, d):
            if s:
                ex.append((dt.datetime.fromisoformat(s).replace(tzinfo=UTC),))
    allev = pl.DataFrame({"t": [e[0] for e in ex]}).with_columns(pl.col("t").dt.cast_time_unit("us"))
    allev = allev.with_columns(pl.Series("aday0", [day0_index(cal, t) for t in allev["t"].to_list()], dtype=pl.Int32)).unique().sort("t")
    return ev, allev


# ---------------------------------------------------------------------------------------------- per-day worker
_WH: dict = {}


def whitener(reg, model="bge_small"):
    if (reg, model) not in _WH:
        if model == "bge_small":
            _WH[(reg, model)] = L.load_whitener(reg, 32)
        else:
            from embed_models import load_whitener as lw
            _WH[(reg, model)] = lw(reg, 32, model)
    return _WH[(reg, model)]


def day_worker(p: dict) -> dict:
    rng = np.random.default_rng([L.SEED, int(p["aday"])])
    X, Bh, stall = p["X"], p["Bh"], p["stall"]  # n x T (+-1), n x T (0..3), T bool
    K = (X > 0).sum(0)
    lull = K <= 1
    out = {"aday": p["aday"], "T": X.shape[1], "n_present": X.shape[0], "stall_min": int(stall.sum()),
           "lull_min": int(lull.sum()), "offgap_min": int(L.off_runs(K).sum())}
    variants = {"": ~stall, "_none": np.ones_like(stall), "_lull": ~(stall | lull)}
    if p.get("allpres") is not None:   # round 1b: DQ8 trim to the all-present window (before surrogates)
        variants["_trim"] = ~stall & p["allpres"]
        out["trim_min"] = int(variants["_trim"].sum())
    rng_trim = np.random.default_rng([L.SEED, int(p["aday"]), 7])   # own stream: round-1 draws stay identical
    for tag, keep in variants.items():
        a = L.activity_stats(X[:, keep].astype(float), Bh[:, keep], rng_trim if tag == "_trim" else rng)
        for kk, v in a.items():
            if kk in L.ACT_STATS or kk.endswith(("_obs", "_sm", "_ss")) and tag == "":
                out[kk + tag] = v
        if tag == "":
            out["n_act"] = a.get("n_act"); out["T_act"] = a.get("T_act")
            out["R2_level"] = float((X[:, keep] > 0).mean()) if keep.any() else np.nan
    # 5-min bins (stall minutes dropped first, then binned): active if any active minute; behavior = max code
    keep = ~stall
    Xk, Bk = X[:, keep], Bh[:, keep]
    nb = Xk.shape[1] // 5
    if nb >= 30:
        X5 = np.where((Xk[:, :nb * 5].reshape(Xk.shape[0], nb, 5) > 0).any(2), 1, -1)
        B5 = Bk[:, :nb * 5].reshape(Bk.shape[0], nb, 5).max(2)
        a = L.activity_stats(X5.astype(float), B5, rng)
        for kk in L.ACT_STATS:
            if kk in a:
                out[kk + "_b5"] = a[kk]
    # content
    if p.get("V") is not None:
        W = whitener(p["regime"], p.get("model", "bge_small"))
        V = W(p["V"].reshape(-1, p["V"].shape[-1])).reshape(p["V"].shape[0], p["V"].shape[1], 32)
        V = V / np.clip(np.linalg.norm(V, axis=2, keepdims=True), 1e-9, None)
        c = L.content_stats(V, p["M"], rng)
        for kk, v in c.items():
            out[kk] = v
    return out


def make_payloads(days: pl.DataFrame):
    """Per-day payloads (spins, behavior, stall mask, content arrays) for the given calendar rows. The caller decides
    which days are allowed (build.py: non-holdout only; confirm.py: holdout only with the confirm flags)."""
    h38prov = None
    dl = days["pt_date"].to_list()
    fixed = CFG["data_version"] == "fixed"
    abt = "activity_bins_fixed.parquet" if fixed else "activity_bins.parquet"
    ab = (pl.scan_parquet(L.SH / abt).select("pt_date", "minute", "agent", "state",
                                              *(["talk", "idle", "consolidate", "other_event", "turns"] if CFG["trim"] else []))
          .filter(pl.col("pt_date").is_in(dl)).collect())
    # H38 outage mask (Amendment 0d) or the fallback; round 1b: the corrected shared outages_fixed table
    osrc = (L.SH / "outages_fixed/outages.parquet") if fixed else (H38 / "outages.parquet")
    use_h38 = osrc.exists()
    if use_h38:
        o = (pl.read_parquet(osrc).filter(pl.col("pt_date").is_in(dl))
             .filter(pl.col("village_off") | pl.col("cause").is_in(["scheduled", "infra_error"]) | pl.col("infra_burst")))
        omask = {}
        for d, s, e in o.select("pt_date", "m_start", "m_end").iter_rows():
            omask.setdefault(d, []).append((s, e))
        if fixed:
            h38prov = json.loads((L.SH / "_provenance.json").read_text()).get("outages_fixed", {}).get("built_at", "shared outages_fixed")
        else:
            h38prov = json.loads((H38 / "_provenance.json").read_text()).get("build_outages", {}).get("built_at")
    # content windows (round 1b: model and dedupe switches)
    aw, vec = window_vectors(dl)
    # consolidations per agent-day (NE41 nuisance check)
    cons = (pl.scan_parquet(L.SH / "events_core.parquet").filter(pl.col("action_type") == "CONSOLIDATE")
            .filter(pl.col("pt_date").is_in(dl)).group_by("pt_date").agg(pl.len().alias("n_consolidate")).collect())

    payloads = []
    abd = {d: g for (d,), g in ab.group_by(["pt_date"])}
    awd = {d: g for (d,), g in aw.group_by(["pt_date"])}
    for r in days.iter_rows(named=True):
        d = r["pt_date"]
        g = abd.get(d)
        if g is None:
            continue
        act = g.group_by("agent").agg((pl.col("state") >= 3).sum().alias("na"))
        pres = act.filter(pl.col("na") >= L.MIN_ACTIVE_MIN)["agent"].sort().to_list()
        if len(pres) < L.MIN_PRESENT:
            continue
        T = int(g["minute"].max()) + 1
        S = np.ones((len(pres), T), np.int8)  # state codes 1..4; missing rows = silent
        idx = {a_: i for i, a_ in enumerate(pres)}
        gg = g.filter(pl.col("agent").is_in(pres))
        S[[idx[x] for x in gg["agent"].to_list()], gg["minute"].to_numpy()] = gg["state"].to_numpy()
        X = np.where(S >= 3, 1, -1).astype(np.int8)
        Bh = (S - 1).astype(np.int8)
        K = (X > 0).sum(0)
        if use_h38:
            stall = np.zeros(T, bool)
            for s, e in omask.get(d, []):
                stall[max(0, s):min(T, e)] = True
        else:
            stall = L.off_runs(K)
        p = {"aday": r["aday"], "X": X, "Bh": Bh, "stall": stall, "regime": r["regime"], "model": CFG["model"]}
        if CFG["trim"]:   # DQ8: all-present window = minutes where every present agent is inside its record span
            rec = gg.filter((pl.col("talk") + pl.col("idle") + pl.col("consolidate") + pl.col("other_event") + pl.col("turns")) > 0)
            span = rec.group_by("agent").agg(pl.col("minute").min().alias("m0"), pl.col("minute").max().alias("m1"))
            sp = {a_: (m0, m1) for a_, m0, m1 in span.iter_rows()}
            allp = np.ones(T, bool)
            for a_ in pres:
                m0, m1 = sp.get(a_, (0, -1))
                inside = np.zeros(T, bool); inside[max(0, m0):min(T, m1 + 1)] = True
                allp &= inside
            p["allpres"] = allp
        w = awd.get(d)
        if w is not None and w.height:
            agents = sorted(set(w["agent"].to_list())); Wn = int(w["win30"].max()) + 1
            V = np.zeros((len(agents), Wn, vec.shape[1]), np.float32); M = np.zeros((len(agents), Wn), bool)
            ia = {a_: i for i, a_ in enumerate(agents)}
            for ag, wi, gid in w.select("agent", "win30", "gid").iter_rows():
                V[ia[ag], wi] = vec[gid]; M[ia[ag], wi] = True
            p["V"], p["M"] = V, M
        payloads.append(p)
    return payloads, use_h38, h38prov, cons


def add_rivals(st: pl.DataFrame, cal: pl.DataFrame, dl: list[str], allow_holdout_prev: bool) -> pl.DataFrame:
    """R1 (centroid shift vs the previous active day) and R3 (polarization) on raw 384-d agent-day vectors centered on the
    non-holdout mean (Amendment 0e). R1 is NaN when the previous active day is held out, unless allow_holdout_prev."""
    # rivals R1 / R3 on raw 384-d agent-day vectors centered on the non-holdout mean (Amendment 0e)
    ad, av = day_vectors(None if allow_holdout_prev or CFG["dedupe"] == "none" else dl)
    nh = ad.filter(~pl.col("holdout"))
    mu = av[nh["gid"].to_numpy()].mean(0)
    mbar = {}
    for (d,), g in ad.filter(pl.col("pt_date").is_in(dl + ([] if not allow_holdout_prev else cal["pt_date"].to_list()))).group_by(["pt_date"]):
        x = av[g["gid"].to_numpy()] - mu
        x /= np.clip(np.linalg.norm(x, axis=1, keepdims=True), 1e-9, None)
        mbar[d] = x.mean(0)
    allcal = cal.select("aday", "pt_date", "holdout")
    prev = {r[0]: r for r in allcal.iter_rows()}
    r1, r3 = [], []
    for aday, d in st.select("aday", "pt_date").iter_rows():
        m = mbar.get(d)
        r3.append(float(np.linalg.norm(m)) if m is not None else np.nan)
        pv = prev.get(aday - 1)
        if m is None or pv is None or (pv[2] and not allow_holdout_prev) or pv[1] not in mbar:
            r1.append(np.nan); continue
        m0 = mbar[pv[1]]
        r1.append(float(1 - m @ m0 / (np.linalg.norm(m) * np.linalg.norm(m0))))
    st = st.with_columns(pl.Series("R1_shift", r1), pl.Series("R3_polar", r3))
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog-only", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--data-version", default="old", choices=["old", "fixed"])
    ap.add_argument("--model", default="bge_small", choices=["bge_small", "gte_modernbert"])
    ap.add_argument("--dedupe", default="none", choices=["none", "restate", "copies"])
    ap.add_argument("--catalog", default="r1", choices=["r1", "r1b"])
    ap.add_argument("--r1b", default=None, help="round-1b tag: write to r1b/<tag>/ (adds the _trim variant)")
    a = ap.parse_args()
    global R1B_CATALOG
    CFG.update(data_version=a.data_version, model=a.model, dedupe=a.dedupe, trim=a.r1b is not None)
    R1B_CATALOG = a.catalog == "r1b"
    OUTD = (L.OUT / "r1b" / a.r1b) if a.r1b else L.OUT
    t0 = time.time()
    OUTD.mkdir(parents=True, exist_ok=True)
    cal = calendar()
    ev, allev = catalog(cal)
    ev.write_parquet(OUTD / "events.parquet", compression="zstd")
    allev.write_parquet(OUTD / "allevents.parquet", compression="zstd")
    print(f"catalog: {ev.height} events ({ev.filter(~pl.col('holdout0')).height} with non-holdout day 0), "
          f"{allev.height} exclusion dates")
    if a.catalog_only:
        return

    days = cal.filter(~pl.col("holdout") & (pl.col("goal_no") > 0))
    assert not any(L.holdout_mask(days["pt_date"].to_list(), days["goal_no"].to_list()))
    payloads, use_h38, h38prov, cons = make_payloads(days)
    print(f"{len(payloads)} days to process ({time.time() - t0:.0f}s)")
    res = []
    with ProcessPoolExecutor(max_workers=min(2, a.workers)) as ex:
        for out in ex.map(day_worker, payloads, chunksize=4):
            res.append(out)
    st = pl.DataFrame(res, infer_schema_length=None)
    base = days.select("aday", "pt_date", "goal_no", "regime", "weekday", "gap_days", "monday", "window_s", "documented_hours")
    st = base.join(st, on="aday", how="inner").join(cons, on="pt_date", how="left").sort("aday")
    st = st.with_columns((pl.col("n_consolidate").fill_null(0) / pl.col("n_present")).alias("consol_per_agent"))

    st = add_rivals(st, cal, days["pt_date"].to_list(), allow_holdout_prev=False)
    assert not st["pt_date"].is_in(cal.filter(pl.col("holdout"))["pt_date"]).any()
    st.write_parquet(OUTD / "day_stats.parquet", compression="zstd")
    if not a.r1b:
        for (g,), sub in st.group_by(["goal_no"]):
            dd = L.OUT / f"G{int(g):02d}"; dd.mkdir(exist_ok=True)
            sub.write_parquet(dd / "day_stats.parquet", compression="zstd")
    L.write_provenance("hypotheses/H36-reorganization-alarm/scheme/build.py",
                       ["activity_bins", "calendar", "kicks", "rooms", "rooms_timeline", "events_core",
                        "embeddings/agent_win30", "embeddings/agent_day", "whitening_<regime>"],
                       {"mask": "H38 outages (village_off | cause in {scheduled, infra_error} | infra_burst)" if use_h38
                        else "fallback K=0 runs >= 10 min", "h38_outages_built_at": h38prov if use_h38 else None,
                        "n_surr": L.N_SURR, "min_active_min": L.MIN_ACTIVE_MIN, "min_present": L.MIN_PRESENT,
                        "seed": L.SEED, "days": st.height})
    print(f"day_stats: {st.height} days, {time.time() - t0:.0f}s; mask = {'H38' if use_h38 else 'fallback'}")


if __name__ == "__main__":
    main()
