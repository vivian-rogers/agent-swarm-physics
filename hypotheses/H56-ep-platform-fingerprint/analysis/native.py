"""H56 period-native tests (layer 2): NE14b, NE43, NE40, G51. Non-holdout only.

Run: OMP_NUM_THREADS=2 POLARS_MAX_THREADS=2 uv run python hypotheses/H56-ep-platform-fingerprint/analysis/native.py [--test NE14,NE43,NE40,G51]
Outputs: data/processed/H56-ep-platform-fingerprint/native/<test>.json (+ parquet tables)
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
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import event_study as ES  # noqa: E402
import h56lib as L  # noqa: E402

OUT = L.OUTROOT / "native"
REP = L.OUTROOT / "replication"
IDLE = {"act_all": 6, "act_agent": 6, "coarse_all": 4, "coarse_agent": 4, "act_agent_b3": 6, "coarse_agent_b3": 4}
CONS = {"act_all": 7, "coarse_all": 5}
SEARCH_ACT = 8


def side_labels(D, vi, a, days):
    """Per-agent counts on a side with (day, quarter) labels, empty labels removed: (L, q, q)."""
    C = D.C[vi][a, days].reshape((-1,) + D.C[vi].shape[-2:])
    return C[C.sum((1, 2)) > 0]


def native_window(D, vi, pre, post, rng, pairs=None, agents=None, min_trans=ES.MIN_TRANS, r=ES.R):
    """Within-agent count-matched Newton (labels = day x quarter, so 1-day sides work)."""
    rows = []
    for a in (agents if agents is not None else range(D.n_agents)):
        cp, cq = side_labels(D, vi, a, pre), side_labels(D, vi, a, post)
        if cp.sum() < min_trans or cq.sum() < min_trans or len(cp) < 2 or len(cq) < 2:
            continue
        mp = L.matched_pair(cp, cq, rng, R=r, est=("newton",), pairs=pairs)
        rows.append({"agent": int(a), "lab": D.lab[a], "pre": mp["newton"][0], "post": mp["newton"][1]})
    dl = [x["post"] - x["pre"] for x in rows]
    lev = np.nanmean([0.5 * (x["pre"] + x["post"]) for x in rows]) if rows else np.nan
    return L.event_stats(dl, lev), rows


def placebo_days(D, tday, weekday=None, regimes=None, goal=None):
    p = tday.filter(pl.col("placebo") & (pl.col("variant") == "act_all"))
    if weekday is not None:
        p = p.filter(pl.col("weekday") == weekday)
    if regimes is not None:
        p = p.filter(pl.col("regime").is_in(regimes))
    if goal is not None:
        p = p.filter(pl.col("goal_no") == goal)
    return sorted(p["nidx"].to_list())


def pval(obs, pool):
    pool = np.abs(np.asarray([x for x in pool if np.isfinite(x)]))
    return float((1 + (pool >= abs(obs)).sum()) / (1 + len(pool))) if len(pool) else np.nan, int(len(pool))


# ----------------------------------------------------------------------------- NE14b
def ne14(D, tday, rng):
    i24 = D.idx_of["2026-03-24"]
    pre, post = [i24 - 3, i24 - 2, i24 - 1], [i24, i24 + 1]
    assert D.nh_dates[pre[0]] == "2026-03-19" and D.nh_dates[post[-1]] == "2026-03-25"
    out = {"pre": [D.nh_dates[i] for i in pre], "post": [D.nh_dates[i] for i in post], "variants": {}}
    # Amendment 3: Tuesdays (any regime) with eligible windows, > 2 days from every scaffold_tool event
    ev = pl.read_parquet(L.DATA / "event_catalog.parquet")
    sc_days = ev.filter((pl.col("cls") == "scaffold_tool") & pl.col("nidx").is_not_null())["nidx"].to_list()
    elig = tday.filter((pl.col("variant") == "act_all") & (pl.col("weekday") == 2))["nidx"].to_list()
    pdays = [d for d in elig if min(abs(d - x) for x in sc_days) > 2]
    for vi, v in enumerate(L.VARIANTS):
        st, rows = native_window(D, vi, pre, post, rng)
        pool = []
        for d in pdays:
            if d - 3 < 0 or d + 2 > D.nd:
                continue
            s2, _ = native_window(D, vi, [d - 3, d - 2, d - 1], [d, d + 1], rng, r=2)
            pool.append(s2["t"])
        p, n = pval(st["t"], pool)
        rec = {**st, "p_tuesday_placebo": p, "n_placebo": n, "max_placebo_abs_t": float(np.nanmax(np.abs(pool))) if pool else None,
               "agents": rows}
        if v in CONS:
            q = L.QV[vi]
            s3, _ = native_window(D, vi, pre, post, rng, pairs=L.sector_pairs(q, CONS[v]))
            rec["consolidate_sector"] = s3
        out["variants"][v] = rec
    V = out["variants"]
    for ag, al in (("coarse_agent", "coarse_all"), ("act_agent", "act_all"), ("coarse_agent_b3", "coarse_all"), ("act_agent_b3", "act_all")):
        out[f"carriage_{ag}"] = abs(V[ag]["dbar"]) / abs(V[al]["dbar"]) if V[al]["dbar"] else None
    return out


# ----------------------------------------------------------------------------- NE43
def ne43(D, tday, rng):
    kc = pl.read_parquet(L.DATA.parent / "shared/kicks_classified.parquet")
    facts = {"last_nudge": kc.filter(pl.col("kind") == "nudge")["pt_date"].max(),
             "last_pause_resume": kc.filter(pl.col("kind") == "pause_resume")["pt_date"].max(),
             "nudges_51_before": int(kc.filter((pl.col("kind") == "nudge") & (pl.col("goal_no") == 51)).height)}
    i = D.idx_of["2026-08-21"]
    designs = {"k3": ([i - 3, i - 2, i - 1], [i, i + 1, i + 2]),
               "fri_only": ([i - 3, i - 2, i - 1], [i]),
               "k5": ([i - 5, i - 4, i - 3, i - 2, i - 1], [i, i + 1, i + 2, i + 3, i + 4])}
    fridays = [d for d in range(D.nd) if D.nh_weekday[d] == 5 and D.nh_goal[d] == 51 and d != i]
    out = {"facts": facts, "designs": {}}
    for nm, (pre, post) in designs.items():
        out["designs"][nm] = {"pre": [D.nh_dates[x] for x in pre], "post": [D.nh_dates[x] for x in post]}
        for vi, v in enumerate(L.VARIANTS):
            st, rows = native_window(D, vi, pre, post, rng)
            res = {**st}
            pool, pool_idle = [], []
            sec = L.sector_pairs(L.QV[vi], IDLE[v])
            si, _ = native_window(D, vi, pre, post, rng, pairs=sec)
            res["idle_sector"] = si
            for d in fridays:
                pp = [d + (x - i) for x in pre]
                qq = [d + (x - i) for x in post]
                if min(pp) < 0 or max(qq) >= D.nd or any(D.nh_goal[x] != 51 for x in pp + qq):
                    continue
                s2, _ = native_window(D, vi, pp, qq, rng, r=2)
                s3, _ = native_window(D, vi, pp, qq, rng, pairs=sec, r=2)
                pool.append(s2["t"])
                pool_idle.append(s3["t"])
            res["p_friday_placebo"], res["n_placebo"] = pval(st["t"], pool)
            res["idle_sector"]["p_friday_placebo"], _ = pval(si["t"], pool_idle)
            res["placebo_t"] = [float(x) for x in pool]
            out["designs"][nm][v] = res
    return out


# ----------------------------------------------------------------------------- NE40
def ne40(D, tday, rng):
    f = pl.read_parquet(L.DATA / "ne40_search_features.parquet")
    feats = ["ans_chars", "ans_lines", "ans_md_head", "ans_bold", "ans_bullets", "ans_numbered", "ans_nonascii",
             "ans_blank_lines"]
    daily = (f.group_by("pt_date").agg(pl.len().alias("n"), *[pl.col(c).median().alias(c) for c in feats],
                                       pl.col("schema_date").mean().alias("schema_date_share"))
             .filter(pl.col("n") >= 5).sort("pt_date"))
    X = daily.select(feats).to_numpy().astype(float)
    Z = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1)
    T = len(Z)

    def best_split(Zm):
        best, arg = -1, None
        for s in range(3, len(Zm) - 3):
            a, b = Zm[:s], Zm[s:]
            stat = (len(a) * len(b) / len(Zm)) * ((a.mean(0) - b.mean(0)) ** 2).sum()
            if stat > best:
                best, arg = stat, s
        return best, arg

    stat, s = best_split(Z)
    perm = []
    for _ in range(2000):
        perm.append(best_split(Z[rng.permutation(T)])[0])
    p = float((1 + (np.array(perm) >= stat).sum()) / 2001)
    per_feat = {}
    for j, c in enumerate(feats):
        st_j, s_j = best_split(Z[:, [j]])
        per_feat[c] = {"split_first_day": daily["pt_date"][s_j], "stat": float(st_j),
                       "before_median": float(np.median(X[:s_j, j])), "after_median": float(np.median(X[s_j:, j]))}
    # stability: bootstrap over searches within days
    boots = []
    for _ in range(200):
        fb = f.sample(fraction=1.0, with_replacement=True, seed=int(rng.integers(1e9)))
        db = (fb.group_by("pt_date").agg(pl.len().alias("n"), *[pl.col(c).median().alias(c) for c in feats])
              .filter(pl.col("n") >= 5).sort("pt_date"))
        Xb = db.select(feats).to_numpy().astype(float)
        Zb = (Xb - Xb.mean(0)) / np.where(Xb.std(0) > 0, Xb.std(0), 1)
        boots.append(db["pt_date"][best_split(Zb)[1]])
    bc = pl.Series(boots).value_counts().sort("count", descending=True)
    D40_len = daily["pt_date"][s]
    schema = f.group_by("schema_date").agg(pl.col("pt_date").min().alias("first"), pl.col("pt_date").max().alias("last"), pl.len())
    out = {"n_days": T, "prereg_joint_split_first_day": D40_len, "prereg_last_day_before": daily["pt_date"][s - 1],
           "prereg_stat": float(stat), "prereg_p_perm": p, "prereg_bootstrap_modal": bc.head(5).to_dicts(),
           "per_feature": per_feat, "schema": schema.to_dicts(), "daily": daily.to_dicts()}
    # Post hoc (Amendment 4): stylometric markers of the answerer (Gemini-style "*   " bullets vs "- " bullets)
    sty = (f.group_by("pt_date").agg(pl.len().alias("n"), (pl.col("m_star3_bullet") > 0).mean().alias("star3"),
                                     (pl.col("m_dash_bullet") > 0).mean().alias("dash"),
                                     (pl.col("m_emdash") > 0).mean().alias("emdash"))
           .filter(pl.col("n") >= 3).sort("pt_date"))
    Xs = sty.select("star3", "dash").to_numpy().astype(float)
    Zs = (Xs - Xs.mean(0)) / Xs.std(0)
    st_s, s_s = best_split(Zs)
    perm_s = [best_split(Zs[rng.permutation(len(Zs))])[0] for _ in range(2000)]
    D40 = sty["pt_date"][s_s]
    pre_s, post_s = sty[:s_s], sty[s_s:]
    out["stylometric"] = {"split_first_day": D40, "last_day_before": sty["pt_date"][s_s - 1], "stat": float(st_s),
                          "p_perm": float((1 + (np.array(perm_s) >= st_s).sum()) / 2001),
                          "star3_share_before": float(pre_s["star3"].mean()), "star3_share_after": float(post_s["star3"].mean()),
                          "days_before_with_star3": int((pre_s["star3"] > 0).sum()), "days_before": pre_s.height,
                          "days_after_with_star3": int((post_s["star3"] > 0).sum()), "days_after": post_s.height,
                          "dash_share_before": float(pre_s["dash"].mean()), "dash_share_after": float(post_s["dash"].mean()),
                          "emdash_share_before": float(pre_s["emdash"].mean()), "emdash_share_after": float(post_s["emdash"].mean()),
                          "daily": sty.to_dicts()}
    # EP tests at D40 (first non-holdout day >= D40)
    j = D.idx_of.get(D40)
    if j is not None:
        tv = tday.filter((pl.col("nidx") == j))
        out["replication_at_D40"] = {r["variant"]: {"t": r["newton_t"], "placebo": r["placebo"]} for r in tv.iter_rows(named=True)}
        es_pool = {}
        w = D.windows(j)
        if w is not None:
            pre, post = w
            st, _ = ES.window_stat(D, 0, pre, post, rng)
            reg, wd = D.nh_regime[j], D.nh_weekday[j]
            ev = pl.read_parquet(L.DATA / "event_catalog.parquet")
            sc_days = ev.filter((pl.col("cls") == "scaffold_tool") & pl.col("nidx").is_not_null())["nidx"].to_list()
            pool, kind = ES.n2_pool(tday, "act_all", reg, wd, sc_days)
            out["ep_at_D40_act_all"] = {**st["newton"], "p_placebo": pval(st["newton"]["t"], pool)[0], "null": kind}
            sec = L.sector_pairs(11, SEARCH_ACT)
            ss, _ = native_window(D, 0, pre, post, rng, pairs=sec, min_trans=100)
            pool_s = []
            far = tday.filter((pl.col("variant") == "act_all") & (pl.col("regime") == reg))["nidx"].to_list()
            far = [d for d in far if min(abs(d - x) for x in sc_days) > 2]
            for d in far:
                ww = D.windows(d)
                if ww is None:
                    continue
                s2, _ = native_window(D, 0, ww[0], ww[1], rng, pairs=sec, r=2)
                pool_s.append(s2["t"])
            out["search_sector_at_D40"] = {**ss, "p_placebo": pval(ss["t"], pool_s)[0], "n_placebo": len(pool_s)}
            es_pool["n"] = len(pool)
    return out


# ----------------------------------------------------------------------------- G51
def g51(D, tday, rng):
    res = json.loads((REP / "results.json").read_text())
    ev = pl.read_parquet(L.DATA / "event_catalog.parquet").filter(pl.col("goal0") == 51)
    g_idx = [i for i in range(D.nd) if D.nh_goal[i] == 51]
    out = {"days": [D.nh_dates[g_idx[0]], D.nh_dates[g_idx[-1]]], "n_days": len(g_idx), "variants": {}}
    da = pl.read_parquet(REP / "daily_agent.parquet")
    for v in L.VARIANTS:
        cps = [c for c in res["blind"][v]["change_points"] if c["pt_date"] in set(D.nh_dates[i] for i in g_idx)]
        tv = tday.filter((pl.col("variant") == v) & pl.col("nidx").is_in(g_idx) & pl.col("newton_t").is_not_nan()).sort("nidx")
        idx = tv["nidx"].to_list()
        cp_idx = [D.idx_of[c["pt_date"]] for c in cps]
        ev_r = ev.filter(pl.col("cls").is_in(["roster", "room", "operator"]) & pl.col("nidx").is_not_null())
        ev_idx = [x for x in ev_r["nidx"].to_list() if x in set(idx)]

        def nh(cpl):
            return sum(any(abs(e - c) <= 1 for c in cpl) for e in ev_idx)

        obs = nh(cp_idx)
        pos = {d: k for k, d in enumerate(idx)}
        sh = []
        for s in range(len(idx)):
            sh.append(nh([idx[(pos[c] + s) % len(idx)] for c in cp_idx if c in pos]))
        sh = np.array(sh)
        # trend: agent-demeaned daily EP
        dv = da.filter((pl.col("variant") == v) & pl.col("pt_date").is_in([D.nh_dates[i] for i in g_idx])
                       & pl.col("ep_newton").is_not_nan())
        dv = dv.with_columns((pl.col("ep_newton") - pl.col("ep_newton").mean().over("agent")).alias("res"))
        dm = dv.group_by("pt_date").agg(pl.col("res").mean()).sort("pt_date")
        rho, prho = spearmanr(np.arange(dm.height), dm["res"].to_numpy())
        # provider signature at each change-point
        ta = pl.read_parquet(REP / "tday_agent.parquet").filter(pl.col("variant") == v)
        sig = []
        for c in cps:
            t = ta.filter(pl.col("nidx") == D.idx_of[c["pt_date"]]).with_columns((pl.col("post") - pl.col("pre")).alias("d"))
            labs = {}
            for a, d in zip(t["agent"].to_list(), t["d"].to_list()):
                labs.setdefault(D.lab[a], []).append(d)
            prov = {k: float(np.mean(x)) for k, x in labs.items() if len(x) >= 2}
            same = len({np.sign(x) for x in prov.values()}) == 1 if prov else None
            sig.append({**c, "provider_means": prov, "all_providers_same_sign": same})
        out["variants"][v] = {"change_points": sig, "roster_room_operator_events": len(ev_idx), "hits": int(obs),
                              "chance_hits": float(sh.mean()), "enrichment": float(obs / sh.mean()) if sh.mean() > 0 else None,
                              "p_shift": float((1 + (sh >= obs).sum()) / (1 + len(sh))),
                              "trend_spearman": float(rho), "trend_p": float(prho), "n_trend_days": dm.height}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", default="NE14,NE43,NE40,G51")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261005)
    D = ES.Data()
    tday = pl.read_parquet(REP / "tday.parquet")
    fns = {"NE14": ne14, "NE43": ne43, "NE40": ne40, "G51": g51}
    for t in a.test.split(","):
        r = fns[t](D, tday, rng)
        (OUT / f"{t}.json").write_text(json.dumps(r, indent=1, default=lambda o: None if o is None else (float(o) if isinstance(o, (np.floating, np.integer)) else str(o))))
        print(t, "done", flush=True)


if __name__ == "__main__":
    main()
