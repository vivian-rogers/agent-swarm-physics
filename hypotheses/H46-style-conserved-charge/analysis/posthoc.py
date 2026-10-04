"""H46 post-hoc diagnostics (labelled post hoc in the card; written after the pre-registered results were seen).

PH1 goal switches: kickoff-day transient (boundary = last pre day vs SECOND post day, placebo = lag-2 pairs inside
    units) and calendar-gap matching (placebo pairs with gap >= 2 calendar days only).
PH2 which style features carry the excess displacement (goal switches, NE41 forced, G51 movers, #12 judges).
PH3 NE41 context position: style / content distance to the agent's unit mean by messages since the last reset.
PH4 KW #51: does style add information beyond content (incremental R2, within-agent scramble of the style block)?
PH5 G51: family pattern of the style shift into #51 (Anthropic vs other labs).
Output: data/processed/H46-style-conserved-charge/posthoc.json
"""
from __future__ import annotations
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402


def lag_pairs(dt_: L.DayTab, lag: int):
    k = dt_.keys.select("row", "agent", "pt_date", "unit2", "regime")
    nx = k.with_columns(pl.col("row").shift(-lag).over("agent").alias("row2"),
                        pl.col("pt_date").shift(-lag).over("agent").alias("d2"),
                        pl.col("unit2").shift(-lag).over("agent").alias("u2"))
    return nx.filter(pl.col("row2").is_not_null() & (pl.col("unit2") == pl.col("u2")))


def ph1(m, dt_, bounds, fd):
    out = {}
    keys = dt_.keys
    ag, un, dd = keys["agent"].to_numpy(), keys["unit2"].to_numpy(), keys["pt_date"].to_numpy()
    toord = lambda s: dt.date.fromisoformat(s).toordinal()  # noqa: E731
    p1, p2 = L.placebo_pairs(dt_), lag_pairs(dt_, 2)
    for variant in ("kickoff_skip", "wrapup_skip", "gap_matched"):
        rows = []
        for b in bounds.filter(pl.col("cls") == "goal").iter_rows(named=True):
            pre, post = set(b["pre"]), set(b["post"])
            tb = toord(min(fd[u] for u in post))
            for a in np.unique(ag[np.isin(un, list(pre))]):
                ipre = np.where(np.isin(un, list(pre)) & (ag == a))[0]
                ipost = np.where(np.isin(un, list(post)) & (ag == a))[0]
                ipre, ipost = ipre[np.argsort(dd[ipre])], ipost[np.argsort(dd[ipost])]
                if variant == "kickoff_skip":
                    if len(ipost) < 2 or len(ipre) < 1:
                        continue
                    i, j, P = ipre[-1], ipost[1], p2
                elif variant == "wrapup_skip":
                    if len(ipre) < 2 or len(ipost) < 1:
                        continue
                    i, j, P = ipre[-2], ipost[0], p2
                else:
                    if len(ipre) < 1 or len(ipost) < 1:
                        continue
                    i, j, P = ipre[-1], ipost[0], p1
                s = P.filter(pl.col("agent") == a)
                d1 = np.array([toord(x) for x in s["pt_date"].to_list()]) if "pt_date" in s.columns else \
                    np.array([toord(x) for x in s["d1"].to_list()])
                d2 = np.array([toord(x) for x in s["d2"].to_list()])
                sel = (np.abs(d1 - tb) <= 42) & (np.abs(d2 - tb) <= 42)
                if variant == "gap_matched":
                    sel &= (d2 - d1) >= 2
                pi = (s["row"] if "row" in s.columns else s["i"]).to_numpy()[sel]
                pj = (s["row2"] if "row2" in s.columns else s["j"]).to_numpy()[sel]
                if len(pi) < 4:
                    continue
                row = {"label": b["label"], "agent": int(a), "n_p": int(len(pi))}
                for ch in ("style", "content"):
                    Db = L.D_unb(dt_, ch, np.array([i]), np.array([j]))[0]
                    Dp = L.D_unb(dt_, ch, pi, pj)
                    row[f"r_{ch}"] = float(((Dp < Db).sum() + 0.5 * (Dp == Db).sum()) / len(Dp))
                rows.append(row)
        r = pl.DataFrame(rows)
        out[variant] = {ch: {k: v for k, v in L.class_test(r, ch, n_rand=5000, n_boot=1000).items() if k != "per_boundary"}
                        for ch in ("style", "content")}
    return out


def feature_excess(Db2: np.ndarray, Dp2: np.ndarray, names):
    """Db2, Dp2: (n, F) squared per-feature differences (sampling-corrected or raw); excess share per feature."""
    ex = Db2.mean(0) - Dp2.mean(0)
    tot = ex.sum()
    order = np.argsort(-ex)
    return {"total_excess": float(tot), "top": [(names[q], float(ex[q] / tot) if tot != 0 else np.nan) for q in order[:6]],
            "ratio_by_feature": {names[q]: float(Db2.mean(0)[q] / Dp2.mean(0)[q]) for q in order[:6]}}


def ph2(m, dt_, rows_cons, bounds):
    out = {}
    names = L.TC
    M, V = dt_.M["style"], None
    keys = dt_.keys.with_row_index("_r")
    look = {(r["agent"], r["pt_date"]): r["row"] for r in keys.iter_rows(named=True)}
    g = rows_cons.filter(pl.col("cls") == "goal")
    bi = np.array([look[(a, d)] for a, d in zip(g["agent"].to_list(), g["d_pre"].to_list())])
    bj = np.array([look[(a, d)] for a, d in zip(g["agent"].to_list(), g["d_post"].to_list())])
    pp = L.placebo_pairs(dt_)
    out["goal_switch"] = feature_excess((M[bi] - M[bj]) ** 2, (M[pp["i"].to_numpy()] - M[pp["j"].to_numpy()]) ** 2, names)
    # NE41 forced vs within pairs, reweighted to the forced pairs' gap-bin distribution
    pr = pl.read_parquet(L.DATA / "ne41_pairs.parquet").filter(pl.col("dedup") & pl.col("label").is_in(["forced", "within"]))
    msgs = pl.read_parquet(L.DATA / "messages.parquet").filter(pl.col("main") & (pl.col("regime") == "III"))
    idx = {k: i for i, k in enumerate(msgs["msg"].to_list())}
    X = L.style_matrix(msgs, "tc")
    i1 = np.array([idx[k] for k in pr["msg"].to_list()])
    i2 = np.array([idx[k] for k in pr["msg2"].to_list()])
    d2 = (X[i1] - X[i2]) ** 2
    gb = np.floor(np.log10(np.maximum(pr["gap_s"].to_numpy(), 1)) / 0.05).astype(int)
    lab = pr["label"].to_numpy()
    f, w = lab == "forced", lab == "within"
    wts = np.zeros(len(lab))
    for b_ in np.unique(gb[f]):
        nw = (w & (gb == b_)).sum()
        if nw:
            wts[w & (gb == b_)] = (f & (gb == b_)).sum() / nw
    Dw = (d2 * wts[:, None])[w].sum(0) / wts[w].sum()
    out["ne41_forced"] = feature_excess(d2[f], np.tile(Dw, (2, 1)), names)
    return out


def ph3():
    """Style distance to the agent's unit mean by position since the last reset (regime III)."""
    ct = (pl.scan_parquet(L.SH / "context_ledger_turns.parquet").filter((pl.col("regime") == "III") & ~pl.col("holdout"))
          .select("agent", "t_call", "t_log", "kind", "reset_consol", "reset_session").collect())
    resets = pl.concat([ct.filter(pl.col("kind") == "consolidate").select("agent", pl.col("t_log").alias("t_r")),
                        ct.filter(pl.col("reset_session") & ~pl.col("reset_consol")).select("agent", pl.col("t_call").alias("t_r"))])
    m = L.load_messages().filter(pl.col("regime") == "III")
    Xs = L.style_matrix(m, "tc")
    Xc = L.content_matrix(m, "resid")
    ag = m["agent"].to_numpy()
    tt = m["t"].dt.epoch("us").to_numpy()
    seg = np.zeros(len(m), np.int64)
    for a in np.unique(ag):
        ix = np.where(ag == a)[0]
        tr = np.sort(resets.filter(pl.col("agent") == a)["t_r"].dt.epoch("us").to_numpy())
        seg[ix] = np.searchsorted(tr, tt[ix], side="right")
    m = m.with_columns(pl.Series("seg", seg)).with_row_index("i")
    m = m.with_columns(pl.col("i").rank("ordinal").over("agent", "pt_date", "seg").alias("pos"))
    pos = m["pos"].to_numpy()
    key = (m["agent"].cast(pl.Utf8) + "|" + m["unit2"]).to_numpy()
    _, inv = np.unique(key, return_inverse=True)
    out = {}
    for name, X, cosine in (("style", Xs, False), ("content", Xc, True)):
        S = np.zeros((inv.max() + 1, X.shape[1]))
        np.add.at(S, inv, X)
        mu = S / np.bincount(inv)[:, None]
        if cosine:
            mun = mu / np.linalg.norm(mu, axis=1, keepdims=True)
            d = 1 - (X * mun[inv]).sum(1)
        else:
            d = ((X - mu[inv]) ** 2).sum(1)
        # remove agent-unit mean distance so agents with different spreads are comparable
        Sd = np.bincount(inv, weights=d) / np.bincount(inv)
        dd = d - Sd[inv]
        bins = {"1": pos == 1, "2": pos == 2, "3": pos == 3, "4-6": (pos >= 4) & (pos <= 6), "7+": pos >= 7}
        res = {}
        for b_, msk in bins.items():
            res[b_] = {"n": int(msk.sum()), "mean_excess": float(dd[msk].mean()), "se": float(dd[msk].std(ddof=1) / np.sqrt(msk.sum()))}
        # within long segments only (>= 7 messages): removes the selection of chat-dense segments
        segkey = (m["agent"].cast(pl.Utf8) + "|" + m["pt_date"] + "|" + m["seg"].cast(pl.Utf8)).to_numpy()
        _, sinv = np.unique(segkey, return_inverse=True)
        seglen = np.bincount(sinv)[sinv]
        long_ = seglen >= 7
        # demean within segment so only the position profile inside a segment remains
        Sd2 = np.bincount(sinv, weights=d) / np.bincount(sinv)
        ds = d - Sd2[sinv]
        res["within_long_segments"] = {b_: {"n": int((msk & long_).sum()), "mean_excess": float(ds[msk & long_].mean()),
                                            "se": float(ds[msk & long_].std(ddof=1) / np.sqrt(max((msk & long_).sum(), 2)))}
                                       for b_, msk in bins.items()}
        # within-segment consecutive similarity vs across-segment (already NE41); here: slope over positions 2..7
        out[name] = res
    return out


def ph4():
    m = L.load_messages().filter(pl.col("goal_no") == 51)
    mats = {"style": L.style_matrix(m, "tc"), "content": L.content_matrix(m, "resid")}
    dt_ = L.day_table(m, mats)
    k = dt_.keys
    w = (pl.read_parquet(L.SH / "work_daily.parquet").filter((pl.col("level") == "agent") & ~pl.col("holdout"))
         .select("agent", "pt_date", (pl.col("commits").fill_null(0) + pl.col("api_content_writes").fill_null(0)
                                      + pl.col("api_mr_pr_writes").fill_null(0)).alias("out")))
    k = k.join(w, on=["agent", "pt_date"], how="left").with_columns(pl.col("out").fill_null(0).log1p().alias("V")).sort("row")
    k = k.with_columns(pl.col("V").shift(-1).over("agent", "unit2", order_by="pt_date").alias("V_next"))
    kk = k.filter(pl.col("V_next").is_not_null())
    rows = kk["row"].to_numpy()
    a, d, y = kk["agent"].to_numpy(), kk["pt_date"].to_numpy(), kk["V_next"].to_numpy()
    Vt = kk["V"].to_numpy()
    Xs, Xc = dt_.M["style"][rows], dt_.M["content"][rows]
    yd = L.twoway_demean(y[:, None], a, d)[:, 0]

    def r2(X):
        Xd = L.twoway_demean(X, a, d)
        al = L.ridge_gcv(Xd, yd)
        return L.cv_r2(Xd, yd, d, al)
    base = r2(Xc)
    both = r2(np.hstack([Xc, Xs]))
    rng = np.random.default_rng(0)
    null = []
    for _ in range(200):
        perm = np.arange(len(y))
        for g in np.unique(a):
            ix = np.where(a == g)[0]
            perm[ix] = rng.permutation(ix)
        null.append(r2(np.hstack([Xc, Xs[perm]])))
    null = np.array(null)
    # same-day output as a control: is the style signal just persistence of today's output?
    only_v = r2(Vt[:, None])
    sty_v = r2(np.column_stack([Vt, Xs]))
    base_v = r2(np.column_stack([Xc, Vt]))
    both_v = r2(np.column_stack([Xc, Vt, Xs]))
    return {"n": int(len(y)), "r2_content": base, "r2_content_style": both, "incr": both - base,
            "p_style_block_scramble": float((1 + (null >= both).sum()) / 201), "null_median": float(np.median(null)),
            "r2_Vtoday": only_v, "r2_Vtoday_style": sty_v, "r2_content_Vtoday": base_v, "r2_content_Vtoday_style": both_v, "incr_given_Vtoday": both_v - base_v}


def ph5():
    g = json.loads((L.DATA / "G51/native.json").read_text())["agents"]
    roster = pl.read_parquet(L.SH / "roster.parquet")
    lab = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    an = [v["pct_style"] for a, v in g.items() if lab[int(a)] == "Anthropic"]
    ot = [v["pct_style"] for a, v in g.items() if lab[int(a)] != "Anthropic"]
    return {"anthropic": an, "other": ot, "labs_other": [lab[int(a)] for a in g if lab[int(a)] != "Anthropic"],
            "MW_p_other_gt_anthropic": float(stats.mannwhitneyu(ot, an, alternative="greater").pvalue)}


def main():
    m = L.load_messages()
    mats = {"style": L.style_matrix(m, "tc"), "content": L.content_matrix(m, "resid")}
    dt_ = L.day_table(m, mats)
    bounds = pl.read_parquet(L.DATA / "boundaries.parquet")
    fd = L.unit_first_days()
    rows = pl.read_parquet(L.DATA / "conservation_rows.parquet")
    only = sys.argv[1:] if len(sys.argv) > 1 else ["PH1", "PH2", "PH3", "PH4", "PH5"]
    prev = json.loads((L.DATA / "posthoc.json").read_text()) if (L.DATA / "posthoc.json").exists() else {}
    res = dict(prev)
    if "PH1" in only:
        res["PH1"] = ph1(m, dt_, bounds, fd)
    print("PH1", json.dumps(res.get("PH1"), default=float)[:300], flush=True)
    if "PH2" in only:
        res["PH2"] = ph2(m, dt_, rows, bounds)
    print("PH2", json.dumps(res["PH2"], default=float)[:2000], flush=True)
    if "PH3" in only:
        res["PH3"] = ph3()
    print("PH3", json.dumps(res["PH3"], default=float), flush=True)
    if "PH4" in only:
        res["PH4"] = ph4()
    print("PH4", res["PH4"], flush=True)
    if "PH5" in only:
        res["PH5"] = ph5()
    print("PH5", res["PH5"], flush=True)
    (L.DATA / "posthoc.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
