"""H56 replication layer (non-holdout only): daily EP series, the within-agent event statistic at every eligible
day, the event study by class with weekday-matched placebo and random-date nulls, blind change-point detection,
family contrasts and per-period phase-diagram points.

Outputs in data/processed/H56-ep-platform-fingerprint/replication/:
  daily_agent.parquet, daily.parquet      O1 (n0 = 120 transitions per agent-day, folds = within-day quarters)
  tday.parquet                            O2 statistic at every eligible day (variant x estimator)
  tday_agent.parquet                      per-agent Delta_i (Newton) at every eligible day (for DiD / signatures)
  events.parquet                          catalog events with their statistics, placebo p-values, confounding
  results.json                            class tests, blind detection, families, period points
Run: OMP_NUM_THREADS=2 POLARS_MAX_THREADS=2 uv run python hypotheses/H56-ep-platform-fingerprint/analysis/event_study.py
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h56lib as L  # noqa: E402

OUT = L.OUTROOT / "replication"
K = 3
MIN_TRANS = 100
MIN_AGENTS = 4
SPAN_DAYS = 14
N0 = 120
R = 4
TESTED = ["scaffold_tool", "scaffold_prompt", "scaffold_family", "goal", "roster", "room", "operator",
          "operator_schedule", "goal_prompt"]
NOT_EVENTS = ["infra_invisible", "excluded"]
EST = ("newton", "cfx", "plugin")
FAMILY_EXCLUDE = {"Fine-tuned (Kimi)"}


def ddate(s):
    return dt.date.fromisoformat(s)


class Data:
    def __init__(self):
        self.days = pl.read_parquet(L.DATA / "days.parquet")
        nh = self.days.filter(~pl.col("holdout")).sort("nidx")
        self.nh_dates = nh["pt_date"].to_list()
        self.nh_regime = nh["regime"].to_list()
        self.nh_weekday = nh["weekday"].to_list()
        self.nh_goal = nh["goal_no"].to_list()
        self.nd = len(self.nh_dates)
        self.idx_of = {d: i for i, d in enumerate(self.nh_dates)}
        roster = pl.read_parquet(L.DATA.parent / "shared/roster.parquet")
        self.lab = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
        self.name = dict(zip(roster["agent"].to_list(), roster["name"].to_list()))
        c = pl.read_parquet(L.DATA / "counts.parquet")
        self.n_agents = 46
        self.C = []      # per variant: (agents, days, blocks, q, q) int32
        for vi, q in enumerate(L.QV):
            arr = np.zeros((self.n_agents, self.nd, 4, q, q), dtype=np.int32)
            cv = c.filter(pl.col("variant") == vi)
            di = np.array([self.idx_of[d] for d in cv["pt_date"].to_list()])
            np.add.at(arr, (cv["agent"].to_numpy(), di, cv["block"].to_numpy(), cv["a"].to_numpy(), cv["b"].to_numpy()),
                      cv["n"].to_numpy())
            self.C.append(arr)
        self.Cday = [a.sum(2) for a in self.C]   # (agents, days, q, q)
        self.ntr = [a.sum((2, 3)) for a in self.Cday]  # (agents, days)

    def windows(self, d, k=K, allow_cross=False):
        """Pre / post non-holdout day indices for day index d, or None if ineligible."""
        if d - k < 0 or d + k > self.nd:
            return None
        pre, post = list(range(d - k, d)), list(range(d, d + k))
        d0 = ddate(self.nh_dates[d])
        if (d0 - ddate(self.nh_dates[pre[0]])).days > SPAN_DAYS or (ddate(self.nh_dates[post[-1]]) - d0).days > SPAN_DAYS:
            return None
        regs = {self.nh_regime[i] for i in pre + post}
        if len(regs) > 1 and not allow_cross:
            return None
        return pre, post


def window_stat(D, vi, pre, post, rng, agents=None, est=EST, pairs=None, r=R):
    """Within-agent count-matched statistic. Returns (stats by estimator, per-agent rows)."""
    Cd, nt = D.Cday[vi], D.ntr[vi]
    cand = agents if agents is not None else range(D.n_agents)
    rows = []
    for a in cand:
        npre, npost = nt[a, pre].sum(), nt[a, post].sum()
        if npre < MIN_TRANS or npost < MIN_TRANS:
            continue
        cp = Cd[a, [i for i in pre if nt[a, i] > 0]]
        cq = Cd[a, [i for i in post if nt[a, i] > 0]]
        if len(cp) < 2 or len(cq) < 2:
            continue
        mp = L.matched_pair(cp, cq, rng, R=r, est=est, pairs=pairs)
        row = {"agent": a, "m": int(min(npre, npost))}
        for e in est:
            row[f"{e}_pre"], row[f"{e}_post"] = mp[e]
        rows.append(row)
    out = {}
    for e in est:
        dl = [x[f"{e}_post"] - x[f"{e}_pre"] for x in rows]
        lev = np.nanmean([0.5 * (x[f"{e}_post"] + x[f"{e}_pre"]) for x in rows]) if rows else np.nan
        out[e] = L.event_stats(dl, lev)
    return out, rows


def pooled_stat(D, vi, pre, post, rng):
    """Day-pooled swarm statistic (all agents summed per day, count-matched): post - pre (Newton)."""
    Cd = D.Cday[vi]
    a, b = Cd[:, pre].sum(0), Cd[:, post].sum(0)
    if a.sum() < 300 or b.sum() < 300:
        return np.nan
    mp = L.matched_pair(a, b, rng, R=2, est=("newton",))
    return mp["newton"][1] - mp["newton"][0]


# ----------------------------------------------------------------------------- O1 daily
def daily(D, rng):
    rows = []
    for vi, v in enumerate(L.VARIANTS):
        C = D.C[vi]
        for a in range(D.n_agents):
            for d in np.flatnonzero(D.ntr[vi][a] >= N0):
                blocks = C[a, d]
                vals_n, vals_c = [], []
                for _ in range(R):
                    sub = L.stratified_subsample(blocks, N0, rng)
                    vals_n.append(L.newton_counts(sub))
                    vals_c.append(L.cfx_counts(sub))
                rows.append({"variant": v, "agent": int(a), "pt_date": D.nh_dates[d], "n_trans": int(D.ntr[vi][a, d]),
                             "ep_newton": float(np.nanmean(vals_n)), "ep_cfx": float(np.nanmean(vals_c))})
    da = pl.DataFrame(rows)
    ad = pl.read_parquet(L.DATA / "agent_days.parquet").with_columns(
        pl.col("variant").replace_strict({i: v for i, v in enumerate(L.VARIANTS)}, return_dtype=pl.Utf8))
    da = da.join(ad.select("variant", "agent", "pt_date", "span_h", pl.col("n_trans").alias("nt_all")),
                 on=["variant", "agent", "pt_date"], how="left")
    da = da.with_columns((pl.col("ep_newton") * pl.col("nt_all") / pl.col("span_h").clip(0.25)).alias("ep_newton_per_h"))
    dd = (da.group_by("variant", "pt_date").agg(pl.len().alias("n_agents"), pl.col("ep_newton").mean().alias("ep"),
                                                 pl.col("ep_newton").std().alias("ep_sd"), pl.col("ep_cfx").mean().alias("ep_cfx"),
                                                 pl.col("ep_newton_per_h").median().alias("ep_per_h_median"))
          .sort("variant", "pt_date"))
    return da, dd


# ----------------------------------------------------------------------------- O2 at every day
def all_days(D, rng):
    trows, arows = [], []
    for d in range(D.nd):
        w = D.windows(d)
        if w is None:
            continue
        pre, post = w
        for vi, v in enumerate(L.VARIANTS):
            st, rows = window_stat(D, vi, pre, post, rng)
            if st["newton"]["n"] < MIN_AGENTS:
                continue
            rec = {"nidx": d, "pt_date": D.nh_dates[d], "regime": D.nh_regime[d], "weekday": D.nh_weekday[d],
                   "goal_no": D.nh_goal[d], "variant": v, "pooled": pooled_stat(D, vi, pre, post, rng),
                   "first_pre": D.nh_dates[pre[0]], "last_post": D.nh_dates[post[-1]]}
            for e in EST:
                for kk in ("n", "dbar", "t", "fpos", "rel"):
                    rec[f"{e}_{kk}"] = st[e][kk]
            trows.append(rec)
            for x in rows:
                arows.append({"nidx": d, "variant": v, "agent": x["agent"], "m": x["m"],
                              "pre": x["newton_pre"], "post": x["newton_post"]})
    return pl.DataFrame(trows), pl.DataFrame(arows)


# ----------------------------------------------------------------------------- event table and nulls
def event_table(D, tday, tagent):
    ev = pl.read_parquet(L.DATA / "event_catalog.parquet")
    allev = ev.filter(~pl.col("cls").is_in(NOT_EVENTS)).with_columns(
        pl.coalesce("day0", "date").alias("edate")).filter(pl.col("edate").is_not_null())
    edates = list(zip(allev["edate"].to_list(), allev["cls"].to_list(), allev["event_id"].to_list()))

    def contaminants(first_pre, last_post, own=None):
        return [(e, c, i) for e, c, i in edates if first_pre < e <= last_post and i != own]

    # placebo flags per day (variant independent: window dates)
    tday = tday.with_columns(pl.struct("first_pre", "last_post").map_elements(
        lambda s: len(contaminants(s["first_pre"], s["last_post"])) == 0, return_dtype=pl.Boolean).alias("placebo"))
    tested = ev.filter(pl.col("cls").is_in(TESTED) & ~pl.col("holdout0").fill_null(True))
    rows = []
    for r in tested.iter_rows(named=True):
        d = r["nidx"]
        w = D.windows(d, allow_cross=(r["ref"] == "NE14b"))
        base = {"event_id": r["event_id"], "ref": r["ref"], "refs": ",".join(r["refs"]), "cls": r["cls"],
                "family_target": r["family_target"], "day0": r["day0"], "weekday": r["weekday0"], "regime": r["regime0"],
                "goal_no": r["goal0"], "label": r["label"], "nidx": d}
        if w is None:
            rows.append({**base, "eligible": False})
            continue
        pre, post = w
        cont = contaminants(D.nh_dates[pre[0]], D.nh_dates[post[-1]], own=r["event_id"])
        other_cls = sorted({c for e, c, i in cont if c != r["cls"] or e != r["day0"]})
        base.update({"eligible": True, "confounded": len(other_cls) > 0, "confounders": ",".join(other_cls),
                     "first_pre": D.nh_dates[pre[0]], "last_post": D.nh_dates[post[-1]]})
        rows.append(base)
    et = pl.DataFrame(rows, infer_schema_length=None)
    return et, tday


def attach_stats(D, et, tday, tagent, rng):
    """Attach the statistic (all variants) to each eligible event; family events get the DiD statistic."""
    out = []
    for r in et.filter(pl.col("eligible")).iter_rows(named=True):
        for vi, v in enumerate(L.VARIANTS):
            rec = {**r, "variant": v}
            if r["ref"] == "NE14b":
                pre, post = D.windows(r["nidx"], allow_cross=True)
                st, rows = window_stat(D, vi, pre, post, rng)
                for kk in ("n", "dbar", "t", "fpos", "rel"):
                    rec[f"newton_{kk}"] = st["newton"][kk]
                    rec[f"cfx_{kk}"] = st["cfx"][kk]
                    rec[f"plugin_{kk}"] = st["plugin"][kk]
                rec["pooled"] = pooled_stat(D, vi, pre, post, rng)
            elif r["cls"] == "scaffold_family":
                tg = r["family_target"]
                ta = tagent.filter((pl.col("nidx") == r["nidx"]) & (pl.col("variant") == v))
                if ta.height == 0:
                    rec["newton_t"] = np.nan
                else:
                    isT = [is_target(D, a, tg) for a in ta["agent"].to_list()]
                    dl = (ta["post"] - ta["pre"]).to_numpy()
                    s = L.did_stats(dl[np.array(isT)], dl[~np.array(isT)])
                    rec.update({"newton_t": s["t"], "newton_dbar": s["did"], "newton_n": s["n_t"], "n_control": s["n_c"]})
            else:
                row = tday.filter((pl.col("nidx") == r["nidx"]) & (pl.col("variant") == v))
                if row.height == 0:
                    rec["newton_t"] = np.nan
                else:
                    rec.update({k: row[k][0] for k in row.columns if k.startswith(("newton_", "cfx_", "plugin_")) or k == "pooled"})
            out.append(rec)
    return pl.DataFrame(out, infer_schema_length=None)


def is_target(D, a, tg):
    if tg is None:
        return False
    if ":" in tg:
        return D.name.get(a) == tg.split(":", 1)[1]
    return D.lab.get(a) == tg


def placebo_pool(tday, v, regime, weekday, col="newton_t"):
    p = tday.filter(pl.col("placebo") & (pl.col("variant") == v) & pl.col(col).is_not_nan())
    s = p.filter((pl.col("regime") == regime) & (pl.col("weekday") == weekday))
    if s.height >= 8:
        return np.abs(s[col].to_numpy()), "weekday+regime"
    s = p.filter(pl.col("weekday") == weekday)
    if s.height >= 8:
        return np.abs(s[col].to_numpy()), "weekday"
    s = p.filter(pl.col("regime") == regime)
    return np.abs(s[col].to_numpy()), "regime"


def n2_pool(tday, v, regime, weekday, excl_nidx, col="newton_t", min_wd=20, sep=2):
    """Amendment 3 per-event null: eligible days of the regime farther than `sep` non-holdout days from every
    excluded day (the event's own class), weekday-matched when >= min_wd such days, else all weekdays."""
    p = tday.filter((pl.col("variant") == v) & (pl.col("regime") == regime) & pl.col(col).is_not_nan())
    ex = np.asarray(sorted(set(excl_nidx)))
    if len(ex):
        nid = p["nidx"].to_numpy()
        far = np.min(np.abs(nid[:, None] - ex[None, :]), 1) > sep
        p = p.filter(pl.Series(far))
    w = p.filter(pl.col("weekday") == weekday)
    if w.height >= min_wd:
        return np.abs(w[col].to_numpy()), "N2 weekday+regime"
    return np.abs(p[col].to_numpy()), "N2 regime"


def family_placebo(D, tday, tagent, v, tg, regime, weekday):
    """Placebo DiD |t| for one family split at weekday-matched placebo days."""
    pdays = tday.filter(pl.col("placebo") & (pl.col("variant") == v) & (pl.col("regime") == regime))
    wd = pdays.filter(pl.col("weekday") == weekday)
    if wd.height >= 8:
        pdays = wd
    vals = []
    for d in pdays["nidx"].to_list():
        ta = tagent.filter((pl.col("nidx") == d) & (pl.col("variant") == v))
        isT = np.array([is_target(D, a, tg) for a in ta["agent"].to_list()])
        if isT.sum() < 2 or (~isT).sum() < 2:
            continue
        dl = (ta["post"] - ta["pre"]).to_numpy()
        t = L.did_stats(dl[isT], dl[~isT])["t"]
        if np.isfinite(t):
            vals.append(abs(t))
    return np.array(vals)


def event_pvalues(D, es, tday, tagent):
    ps, null_kind, npl = [], [], []
    for r in es.iter_rows(named=True):
        t = r.get("newton_t")
        if t is None or not np.isfinite(t):
            ps.append(np.nan); null_kind.append(None); npl.append(0)
            continue
        if r["cls"] == "scaffold_family":
            pool = family_placebo(D, tday, tagent, r["variant"], r["family_target"], r["regime"], r["weekday"])
            kind = "family-split placebo"
        else:
            pool, kind = placebo_pool(tday, r["variant"], r["regime"], r["weekday"])
        ps.append(float((1 + (pool >= abs(t)).sum()) / (1 + len(pool))) if len(pool) else np.nan)
        null_kind.append(kind); npl.append(len(pool))
    return es.with_columns(pl.Series("p_placebo", ps, dtype=pl.Float64), pl.Series("null_kind", null_kind, dtype=pl.Utf8),
                           pl.Series("n_placebo", npl, dtype=pl.Int32))


def class_tests(es, tday, rng, n_draw=5000):
    res = {}
    for v in L.VARIANTS:
        res[v] = {}
        tv = tday.filter((pl.col("variant") == v) & pl.col("newton_t").is_not_nan())
        for cls in TESTED:
            for subset in ("all", "clean", "no_NE14b"):
                ee = es.filter((pl.col("variant") == v) & (pl.col("cls") == cls) & pl.col("newton_t").is_not_nan())
                if subset == "clean":
                    ee = ee.filter(~pl.col("confounded"))
                if subset == "no_NE14b":
                    if cls != "scaffold_tool":
                        continue
                    ee = ee.filter(pl.col("ref") != "NE14b")
                if ee.height == 0:
                    continue
                obs = float(np.mean(np.abs(ee["newton_t"].to_numpy())))
                hits = float(np.mean(ee["p_placebo"].to_numpy() < 0.05))
                rec = {"n": ee.height, "mean_abs_t": obs, "hit_rate": hits,
                       "refs_hit": ee.filter(pl.col("p_placebo") < 0.05)["refs"].to_list()}
                if cls != "scaffold_family":
                    # N2 random-date null (same regime, any weekday, not an event day of this class)
                    cls_days = set(es.filter(pl.col("cls") == cls)["nidx"].to_list())
                    pools = []
                    for r in ee.iter_rows(named=True):
                        pp = tv.filter((pl.col("regime") == r["regime"]) & ~pl.col("nidx").is_in(list(cls_days)))
                        pools.append(np.abs(pp["newton_t"].to_numpy()))
                    draws = np.array([np.mean([p[rng.integers(len(p))] for p in pools]) for _ in range(n_draw)])
                    rec["p_random_date"] = float((1 + (draws >= obs).sum()) / (1 + n_draw))
                    # weekday-matched placebo draws
                    pools2 = [placebo_pool(tday, v, r["regime"], r["weekday"])[0] for r in ee.iter_rows(named=True)]
                    if all(len(p) for p in pools2):
                        draws2 = np.array([np.mean([p[rng.integers(len(p))] for p in pools2]) for _ in range(n_draw)])
                        rec["p_placebo_class"] = float((1 + (draws2 >= obs).sum()) / (1 + n_draw))
                res[v][f"{cls}:{subset}"] = rec
        # P3: scaffold_tool vs goal class label permutation
        a = np.abs(es.filter((pl.col("variant") == v) & (pl.col("cls") == "scaffold_tool") & pl.col("newton_t").is_not_nan())["newton_t"].to_numpy())
        b = np.abs(es.filter((pl.col("variant") == v) & (pl.col("cls") == "goal") & pl.col("newton_t").is_not_nan())["newton_t"].to_numpy())
        if len(a) and len(b):
            obs = a.mean() - b.mean()
            allv = np.concatenate([a, b])
            perm = []
            for _ in range(n_draw):
                rng.shuffle(allv)
                perm.append(allv[:len(a)].mean() - allv[len(a):].mean())
            res[v]["P3_tool_minus_goal"] = {"diff": float(obs), "p_one_sided": float((1 + (np.array(perm) >= obs).sum()) / (1 + n_draw))}
    return res


# ----------------------------------------------------------------------------- O3 blind detection
def blind(D, tday, es, rng, n_shift=2000):
    ev = pl.read_parquet(L.DATA / "event_catalog.parquet").filter(~pl.col("cls").is_in(NOT_EVENTS))
    ev = ev.with_columns(pl.coalesce("day0", "date").alias("edate")).filter(pl.col("edate").is_not_null())
    # map each event to the first non-holdout day index >= its date
    nidx_after = []
    for e in ev["edate"].to_list():
        j = next((i for i, d in enumerate(D.nh_dates) if d >= e), None)
        nidx_after.append(j)
    ev = ev.with_columns(pl.Series("nidx_a", nidx_after, dtype=pl.Int32))
    out = {}
    for v in L.VARIANTS:
        tv = tday.filter((pl.col("variant") == v) & pl.col("newton_t").is_not_nan()).sort("nidx")
        cps_all, per_regime = [], {}
        elig_by_reg = {}
        for reg in ("I", "II", "III"):
            tr = tv.filter(pl.col("regime") == reg)
            if tr.height < 5:
                continue
            idx = tr["nidx"].to_numpy()
            at = np.abs(tr["newton_t"].to_numpy())
            tau = float(np.percentile(at, 90))
            m = dict(zip(idx.tolist(), at.tolist()))
            cps = [int(d) for d in idx if m[d] >= tau and all(m[d] >= m.get(e, -1) for e in range(d - 2, d + 3))]
            per_regime[reg] = {"tau": tau, "n_days": int(len(idx)), "n_cp": len(cps)}
            cps_all += cps
            elig_by_reg[reg] = idx
        cps_set = set(cps_all)

        def hits_for(cpset):
            res = {}
            for cls in TESTED + ["undocumented"]:
                ee = ev.filter((pl.col("cls") == cls) & pl.col("nidx_a").is_not_null() & ~pl.col("holdout0").fill_null(False))
                ee_idx = [i for i in ee["nidx_a"].to_list() if any(i in set(x.tolist()) for x in elig_by_reg.values())]
                if not ee_idx:
                    continue
                h = sum(any(abs(i - c) <= 1 for c in cpset) for i in ee_idx)
                res[cls] = (h, len(ee_idx))
            return res

        obs = hits_for(cps_set)
        # circular shifts of change-points within each regime's eligible-day list
        sh = {k: [] for k in obs}
        for _ in range(n_shift):
            new = []
            for reg, idx in elig_by_reg.items():
                pos = {d: j for j, d in enumerate(idx.tolist())}
                s = rng.integers(len(idx))
                new += [int(idx[(pos[c] + s) % len(idx)]) for c in cps_all if c in pos]
            hh = hits_for(set(new))
            for k in obs:
                sh[k].append(hh.get(k, (0, 1))[0])
        cls_res = {}
        for k, (h, n) in obs.items():
            arr = np.array(sh[k])
            cls_res[k] = {"hits": h, "n_events": n, "hit_rate": h / n, "chance_rate": float(arr.mean() / n),
                          "enrichment": float(h / arr.mean()) if arr.mean() > 0 else None,
                          "p": float((1 + (arr >= h).sum()) / (1 + n_shift))}
        # scaffold union
        ev_idx_all = [i for i in ev.filter(~pl.col("holdout0").fill_null(False))["nidx_a"].to_list() if i is not None]
        cp_rows = []
        for c in sorted(cps_set):
            near = ev.filter(pl.col("nidx_a").is_not_null() & ((pl.col("nidx_a") - c).abs() <= 1))
            row = tv.filter(pl.col("nidx") == c)
            cp_rows.append({"pt_date": D.nh_dates[c], "regime": D.nh_regime[c], "t": float(row["newton_t"][0]),
                            "fpos": float(row["newton_fpos"][0]), "rel": float(row["newton_rel"][0]),
                            "near": sorted(set(near["cls"].to_list())), "near_refs": near["ref"].to_list()[:6],
                            "unexplained": near.height == 0})
        out[v] = {"per_regime": per_regime, "classes": cls_res, "change_points": cp_rows,
                  "n_unexplained": int(sum(r["unexplained"] for r in cp_rows))}
    return out


# ----------------------------------------------------------------------------- O4 families and period points
def families(D, rng, n_perm=2000):
    h = L.h14()
    res = {}
    periods = sorted(set(D.nh_goal))
    per_rows = []
    for vi, v in enumerate(L.VARIANTS):
        recs = []
        for g in periods:
            didx = [i for i, gg in enumerate(D.nh_goal) if gg == g]
            if len(didx) < 2:
                continue
            nt = D.ntr[vi][:, didx]
            ag = [a for a in range(D.n_agents) if nt[a].sum() >= 300 and (nt[a] > 0).sum() >= 2]
            if len(ag) < 3:
                continue
            m = int(min(nt[a].sum() for a in ag))
            vals = {}
            for a in ag:
                Cl = D.Cday[vi][a, [i for i in didx if D.ntr[vi][a, i] > 0]]
                vv = [L.newton_counts(L.stratified_subsample(Cl, m, rng)) for _ in range(R)]
                vals[a] = float(np.nanmean(vv))
            # period point: full-sample per-agent EP (not count-matched) for the phase diagram
            full = {a: L.newton_counts(D.Cday[vi][a, [i for i in didx if D.ntr[vi][a, i] > 0]]) for a in ag}
            per_rows.append({"goal_no": g, "variant": v, "n_agents": len(ag), "regime": D.nh_regime[didx[0]],
                             "median_ep": float(np.nanmedian(list(full.values()))),
                             "median_ep_matched": float(np.nanmedian(list(vals.values()))), "m_matched": m,
                             "agents": {int(a): full[a] for a in ag}})
            labs = [D.lab[a] for a in ag]
            keep = [i for i, a in enumerate(ag) if labs.count(labs[i]) >= 2 and labs[i] not in FAMILY_EXCLUDE]
            if len({labs[i] for i in keep}) < 2:
                continue
            x = np.array([vals[ag[i]] for i in keep])
            lab = np.array([labs[i] for i in keep])
            e_obs, p_e, null_mean = h.perm_eta2(x, lab, n_perm, rng)
            recs.append({"goal_no": g, "n": len(keep), "labs": sorted(set(lab.tolist())), "eta2": float(e_obs),
                         "p": float(p_e), "null_mean": float(null_mean), "_x": x.tolist(), "_lab": lab.tolist(),
                         "lab_means": {lb: float(x[lab == lb].mean()) for lb in sorted(set(lab.tolist()))}})
        # stratified meta-test: sum of eta2, labels permuted within periods
        if recs:
            obs = sum(r["eta2"] for r in recs)
            tot = []
            for _ in range(n_perm):
                s = 0.0
                for r in recs:
                    lab = np.array(r["_lab"])
                    s += h.eta2(np.array(r["_x"]), rng.permutation(lab))
                tot.append(s)
            res[v] = {"periods": [{k: r[k] for k in r if not k.startswith("_")} for r in recs],
                      "sum_eta2": float(obs), "mean_eta2": float(obs / len(recs)),
                      "p_stratified": float((1 + (np.array(tot) >= obs).sum()) / (1 + n_perm))}
    return res, per_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-daily", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261004)
    D = Data()
    print("loaded", D.nd, "non-holdout days", flush=True)
    if not a.skip_daily:
        da, dd = daily(D, rng)
        da.write_parquet(OUT / "daily_agent.parquet", compression="zstd")
        dd.write_parquet(OUT / "daily.parquet", compression="zstd")
        print("daily done", flush=True)
    tday, tagent = all_days(D, rng)
    print("all days done", tday.height, flush=True)
    et, tday = event_table(D, tday, tagent)
    tday.write_parquet(OUT / "tday.parquet", compression="zstd")
    tagent.write_parquet(OUT / "tday_agent.parquet", compression="zstd")
    es = attach_stats(D, et, tday, tagent, rng)
    es = event_pvalues(D, es, tday, tagent)
    es.write_parquet(OUT / "events.parquet", compression="zstd")
    et.write_parquet(OUT / "event_eligibility.parquet", compression="zstd")
    ct = class_tests(es, tday, rng)
    print("class tests done", flush=True)
    bd = blind(D, tday, es, rng)
    print("blind done", flush=True)
    fam, per_rows = families(D, rng)
    print("families done", flush=True)
    n_pl = {v: int(tday.filter((pl.col("variant") == v) & pl.col("placebo")).height) for v in L.VARIANTS}
    res = {"n_eligible_days": {v: int(tday.filter(pl.col("variant") == v).height) for v in L.VARIANTS},
           "n_placebo_days": n_pl, "class_tests": ct, "blind": bd, "families": fam,
           "events_eligible": int(et.filter(pl.col("eligible")).height), "events_tested_total": int(et.height)}
    (OUT / "results.json").write_text(json.dumps(res, indent=1, default=lambda o: None if o is None else str(o)))
    (OUT / "period_points.json").write_text(json.dumps(per_rows, indent=1))
    prov_path = L.DATA / "_provenance.json"
    prov = json.loads(prov_path.read_text())
    if L.OUTROOT != L.DATA:   # recheck / verify runs: own provenance file, the round-1 one is left untouched
        import subprocess
        gc = subprocess.run(["git", "-C", str(L.ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        prov = {"scheme": prov["scheme"], "estimator": L.EP, "code_git_commit": gc + "+uncommitted (H56_EP switch)"}
        prov_path = L.OUTROOT / "_provenance.json"
    prov["replication"] = {"built_by": "hypotheses/H56-ep-platform-fingerprint/analysis/event_study.py",
                           "git_commit": prov["scheme"]["git_commit"], "inputs": "scheme outputs + shared/roster",
                           "params": {"k": K, "min_trans": MIN_TRANS, "min_agents": MIN_AGENTS, "span_days": SPAN_DAYS,
                                      "n0": N0, "R": R, "seed": 20261004},
                           "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print("done")


if __name__ == "__main__":
    main()
