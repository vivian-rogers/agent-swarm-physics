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


def whitener(reg):
    if reg not in _WH:
        _WH[reg] = L.load_whitener(reg, 32)
    return _WH[reg]


def day_worker(p: dict) -> dict:
    rng = np.random.default_rng([L.SEED, int(p["aday"])])
    X, Bh, stall = p["X"], p["Bh"], p["stall"]  # n x T (+-1), n x T (0..3), T bool
    K = (X > 0).sum(0)
    lull = K <= 1
    out = {"aday": p["aday"], "T": X.shape[1], "n_present": X.shape[0], "stall_min": int(stall.sum()),
           "lull_min": int(lull.sum()), "offgap_min": int(L.off_runs(K).sum())}
    variants = {"": ~stall, "_none": np.ones_like(stall), "_lull": ~(stall | lull)}
    for tag, keep in variants.items():
        a = L.activity_stats(X[:, keep].astype(float), Bh[:, keep], rng)
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
        W = whitener(p["regime"])
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
    ab = (pl.scan_parquet(L.SH / "activity_bins.parquet").select("pt_date", "minute", "agent", "state")
          .filter(pl.col("pt_date").is_in(dl)).collect())
    # H38 outage mask (Amendment 0d) or the fallback
    use_h38 = (H38 / "outages.parquet").exists()
    if use_h38:
        o = (pl.read_parquet(H38 / "outages.parquet").filter(pl.col("pt_date").is_in(dl))
             .filter(pl.col("village_off") | pl.col("cause").is_in(["scheduled", "infra_error"]) | pl.col("infra_burst")))
        omask = {}
        for d, s, e in o.select("pt_date", "m_start", "m_end").iter_rows():
            omask.setdefault(d, []).append((s, e))
        h38prov = json.loads((H38 / "_provenance.json").read_text()).get("build_outages", {}).get("built_at")
    # content windows
    aw = pl.read_parquet(EMB / "agent_win30.parquet").filter(pl.col("pt_date").is_in(dl))
    vec = np.load(EMB / "agent_win30_vec.npy", mmap_mode="r")
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
        p = {"aday": r["aday"], "X": X, "Bh": Bh, "stall": stall, "regime": r["regime"]}
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
    ad = pl.read_parquet(EMB / "agent_day.parquet")
    av = np.load(EMB / "agent_day_vec.npy").astype(np.float32)
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
    a = ap.parse_args()
    t0 = time.time()
    L.OUT.mkdir(parents=True, exist_ok=True)
    cal = calendar()
    ev, allev = catalog(cal)
    ev.write_parquet(L.OUT / "events.parquet", compression="zstd")
    allev.write_parquet(L.OUT / "allevents.parquet", compression="zstd")
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
    st.write_parquet(L.OUT / "day_stats.parquet", compression="zstd")
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
