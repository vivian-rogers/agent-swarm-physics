"""H54 robustness and post hoc checks (all labelled post hoc in the card).

R1  P1 without near-echo statements (whitened cosine to the own kickoff > 0.5 / 0.7 dropped): is target identification
    just agents quoting the kickoff?
R2  P1 on DQ5 style-residualized statement vectors (per-period fit).
R3  G51 role swap on chat only, without intentions (CONSOLIDATE nextSessionGoal restates the role), and on style-residualized vectors.
R4  Is the S_emb (kickoff distinctiveness) -> depth / spread relation mechanical? Synthetic swarms with a constant day-1
    target share and the real kickoff geometry: rho(S_emb, depth_ex) and rho(S_emb, spread) under no specificity effect.
R5  P2 leave-one-period-out on the goal-text naming result (is it carried by one period?).
Output: data/processed/H54-kickoff-quench-target/NE34/robustness.json
"""
from __future__ import annotations

import datetime as dt
import json

import numpy as np
import polars as pl

import h54est as E
import h54lib as L

RNG = np.random.default_rng(545454)


def p1_variant(st, Z, drop_thr=None, chat_only=False, use_zs=None):
    elig = L.eligible()
    idx = {p: k for k, p in enumerate(elig)}
    Kb = {r: np.vstack([L.gvec(q, "kickoff", regime=r) for q in elig]) for r in ("I", "II", "III")}
    P = len(elig)
    S = np.full((P, P), np.nan)
    Zu = Z if use_zs is None else use_zs
    s = st.with_row_index("i").filter((pl.col("src_goal") == pl.col("goal_no")) & (pl.col("day") == 1) & ~pl.col("pre_kick"))
    if chat_only:
        s = s.filter(pl.col("kind") == "chat")
    nd = 0
    ntot = 0
    for p in elig:
        r = L.period_regime(p)
        sp = s.filter(pl.col("goal_no") == p)
        ii = sp["i"].to_numpy()
        ok = np.all(np.isfinite(Zu[ii]), axis=1)
        if drop_thr is not None:
            ok &= (Z[ii] @ Kb[r][idx[p]]) <= drop_thr
        ntot += len(ii)
        nd += int((~ok).sum())
        sp = sp.filter(pl.Series(ok))
        g = sp.group_by("agent").agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= 3)
        if g.height < 3:
            continue
        V = np.vstack([E.unit(Zu[np.asarray(ix)].mean(0)) for ix in g["i"].to_list()])
        S[idx[p]] = E.unit(V.mean(0)) @ Kb[r].T
    Sh = E.colcenter(S)
    pi, t1 = E.own_percentiles(Sh), E.top1(Sh)
    v = E.p1_verdict(pi, t1)
    v["dropped_share"] = nd / max(ntot, 1)
    return v


def g51_variant(st, Z, chat_only=False, use_zs=None):
    import native as N
    Zu = Z if use_zs is None else use_zs
    s = st.with_row_index("i")
    if chat_only:
        s = s.filter(pl.col("kind") == "chat")
    if use_zs is not None:
        s = s.filter(pl.Series(np.all(np.isfinite(Zu[s["i"].to_numpy()]), axis=1)))
    # reuse the native routine on the filtered table (it expects column i)
    res = N.g51(s, Zu)
    return {k: res[k] for k in ("n_agents", "swap_accuracy", "p_perm", "own_goal_pct_median", "centered_alignment_mean",
                                "own_goal_beats_kickoff_rate")} | {"weekly_min": min(w["swap_accuracy"] for w in res["weekly"])}


def s_emb_mechanics(reps=200):
    """Constant day-1 target share; real kickoff geometry (whitened real kickoff vectors as targets' text proxies)."""
    import synthetic as SY
    cal = json.loads((L.OUT / "synthetic" / "calibration.json").read_text())
    struct = SY.real_structure()
    out = []
    for _ in range(reps):
        o = SY.simulate(struct, cal, 0.15, 0.5, 0.5, 0.3, "H54", RNG)
        # distinctiveness of the synthetic kickoffs is implicit in S matrix columns: recompute K via S? use Sh diag vs mean
        S = o["S"]
        q = np.array([E.rarefied_q(g, 5, 10, RNG) for g in o["groups"]])
        # S_emb proxy: 1 - mean cos between kickoff q and the other kickoffs is not stored; use the depth relation on the
        # synthetic depth and the column mean of S (genericness) as the distinctiveness proxy
        gen = np.array([np.mean(np.delete(S[:, k], k)) for k in range(S.shape[0])])
        r1, _, _ = E.spearman(-gen, o["Dex"])
        r2, _, _ = E.spearman(-gen, 1 - q)
        out.append([r1, r2])
    a = np.array(out)
    return {"rho_distinct_depth_median": float(np.median(a[:, 0])), "rho_distinct_depth_q95": float(np.percentile(a[:, 0], 95)),
            "rho_distinct_spread_median": float(np.median(a[:, 1])), "rho_distinct_spread_q05": float(np.percentile(a[:, 1], 5)),
            "note": "distinctiveness proxy = minus the kickoff's mean score with other centroids; constant target share f = 0.15"}


def s_emb_real_check():
    """Real data: does distinctiveness predict spread within regime I only, and with the genericness proxy?"""
    per = pl.read_parquet(L.OUT / "NE34" / "periods.parquet")
    S = np.load(L.OUT / "NE34" / "S_kick.npy")
    gen = np.array([np.nanmean(np.delete(S[:, k], k)) for k in range(S.shape[0])])
    sp = per["spread"].to_numpy()
    se = per["S_emb"].to_numpy()
    out = {"rho_Semb_genericness": E.spearman(se, -gen)[0], "rho_distinct_proxy_spread": E.spearman(-gen, sp)}
    for r in ("I", "III"):
        m = (per["regime"] == r).to_numpy()
        out[f"regime{r}_rho_Semb_spread"] = E.spearman(se[m], sp[m], "less")
    return out


def p2_lopo():
    pr = pl.read_parquet(L.OUT / "projects.parquet").filter(pl.col("src") == "H31")
    rows = []
    for p in sorted(pr["goal_no"].unique().to_list()):
        d = pr.filter(pl.col("goal_no") != p)
        t = E.naming_table(d["named_goal"].to_numpy(), (d["cls"] == "kickoff_frozen").to_numpy(), None)
        rows.append({"drop": p, "precision": t["precision"], "enrichment": t["enrichment"], "p_fisher": t["p_fisher"]})
    return {"min_enrichment": min(r["enrichment"] for r in rows if r["enrichment"] == r["enrichment"]),
            "max_p_fisher": max(r["p_fisher"] for r in rows if r["p_fisher"] == r["p_fisher"]), "rows": rows}


def main():
    st, Z, ZS = L.load_stmt()
    res = {}
    res["R1_no_echo_0.7"] = p1_variant(st, Z, drop_thr=0.7)
    res["R1_no_echo_0.5"] = p1_variant(st, Z, drop_thr=0.5)
    res["R1_no_echo_0.3"] = p1_variant(st, Z, drop_thr=0.3)
    res["R1_chat_no_echo_0.5"] = p1_variant(st, Z, drop_thr=0.5, chat_only=True)
    res["R2_style_resid"] = p1_variant(st, Z, use_zs=ZS)
    for k, v in res.items():
        print(k, v)
    res["R3_g51_chat"] = g51_variant(st, Z, chat_only=True)
    res["R3_g51_style"] = g51_variant(st, Z, use_zs=ZS)
    res["R3_g51_chat_style"] = g51_variant(st, Z, chat_only=True, use_zs=ZS)
    print("R3", res["R3_g51_chat"], res["R3_g51_style"], res["R3_g51_chat_style"])
    res["R4_synthetic"] = s_emb_mechanics(150)
    res["R4_real"] = s_emb_real_check()
    print("R4", res["R4_synthetic"], res["R4_real"])
    res["R5_p2_lopo"] = p2_lopo()
    print("R5", {k: v for k, v in res["R5_p2_lopo"].items() if k != "rows"})
    L.write_json(L.OUT / "NE34" / "robustness.json", res)
    L.provenance("analysis/robustness.py", ["H54 stmt tables (+ DQ5 style-residualized)", "NE34 outputs", "projects.parquet", "synthetic module"], {"seed": 545454})


if __name__ == "__main__":
    main()
