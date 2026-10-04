"""H54 replication layer (all eligible kickoffs) + cross-kickoff tests (NE34): P1-P7 of the card.

Writes data/processed/H54-kickoff-quench-target/:
  NE34/periods.parquet       one row per eligible period (all per-period statistics)
  NE34/S_kick.npy / S_goal.npy / T_disp.npy   target-score matrices (rows: target periods, cols: kickoffs)
  NE34/results.json          cross-kickoff tests and verdicts
  NE34/human.parquet, NE34/remanence.parquet, NE34/chi.parquet, NE34/plans.parquet
  G<NN>/results.json         per-period numbers for the period READMEs
Usage: uv run python explore.py
"""
from __future__ import annotations

import time

import numpy as np
import polars as pl
from scipy import stats

import h54est as E
import h54lib as L

RNG = np.random.default_rng(54)


def basis_mats(periods, kind="kickoff"):
    """K[r] = (P x d) unit whitened vectors of `kind` for every period in regime r's basis."""
    return {r: np.vstack([L.gvec(q, kind, regime=r) for q in periods]) for r in ("I", "II", "III")}


def day_agents(st, Z, cond, n_min=L.N_MIN):
    s = st.with_row_index("i").filter(cond)
    g = s.group_by("goal_no", "agent").agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= n_min).sort("goal_no", "agent")
    V = np.vstack([E.unit(Z[np.asarray(ix)].mean(0)) for ix in g["i"].to_list()]) if g.height else np.zeros((0, L.D))
    return g, V


def main():
    t0 = time.time()
    out = L.OUT / "NE34"
    out.mkdir(parents=True, exist_ok=True)
    st, Z, ZS = L.load_stmt()
    elig = L.eligible()
    P = len(elig)
    idx = {p: k for k, p in enumerate(elig)}
    reg = {p: L.period_regime(p) for p in elig}
    Kb = basis_mats(elig, "kickoff")
    Gb = basis_mats(elig, "goal")
    ko = pl.read_parquet(L.OUT / "kickoffs.parquet").filter(pl.col("room").is_null())
    spec = {r["goal_no"]: r for r in ko.iter_rows(named=True)}
    roster = pl.read_parquet(L.SHARED / "roster.parquet")
    lab = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))

    cur = (pl.col("src_goal") == pl.col("goal_no"))
    g1, V1 = day_agents(st, Z, cur & (pl.col("day") == 1) & ~pl.col("pre_kick"))
    g1c, V1c = day_agents(st, Z, cur & (pl.col("day") == 1) & ~pl.col("pre_kick") & (pl.col("kind") == "chat"))
    g0, V0 = day_agents(st, Z, pl.col("day") == 0)

    def rows_of(g, p):
        return np.flatnonzero(g["goal_no"].to_numpy() == p)

    S = np.full((P, P), np.nan)
    Sc = np.full((P, P), np.nan)
    SG = np.full((P, P), np.nan)
    T = np.full((P, P), np.nan)
    Dex = np.full(P, np.nan)
    per = []
    st_i = st.with_row_index("i")
    for p in elig:
        k = idx[p]
        r = reg[p]
        rr = rows_of(g1, p)
        rec = {"goal_no": p, "regime": r, "n_agents": len(rr), "n_stmt": int(g1["n"].to_numpy()[rr].sum()) if len(rr) else 0}
        if len(rr) >= 3:
            V = V1[rr]
            m = V.mean(0)
            S[k] = E.unit(m) @ Kb[r].T
            SG[k] = E.unit(m) @ Gb[r].T
            A = V @ Kb[r].T  # agents x kickoffs
            Dex[k] = A[:, k].mean() - np.delete(A, k, 1).mean()
            rec.update({"m_norm": float(np.linalg.norm(m)), "q_day1": E.pairwise_q(V), "S_own_raw": float(S[k, k]),
                        "agent_align_own": float(A[:, k].mean()), "depth_ex": float(Dex[k])})
            groups = [Z[np.asarray(ix)] for ix in g1.filter(pl.col("goal_no") == p)["i"].to_list()]
            qr = E.rarefied_q(groups, L.N_RARE, 50, RNG)
            rec.update({"q_rare": qr, "spread": 1 - qr if np.isfinite(qr) else np.nan})
            rc = rows_of(g1c, p)
            if len(rc) >= 3:
                Sc[k] = E.unit(V1c[rc].mean(0)) @ Kb[r].T
            r0 = rows_of(g0, p)
            if len(r0) >= 3:
                m0 = V0[r0].mean(0)
                T[k] = E.unit(m - m0) @ Kb[r].T
                rec.update({"jump": float(E.unit(m) @ Kb[r][k] - E.unit(m0) @ Kb[r][k]), "n_prev_agents": len(r0)})
        sp = spec[p]
        rec.update({"S_text": sp["S_text"], "S_count": sp["S_count"], "words": sp["words"], "n_msgs": sp["n_msgs"],
                    "fallback": sp["fallback"], "S_emb": float(1 - np.mean(np.delete(Kb[r] @ Kb[r][k], k)))})
        per.append(rec)
    Sh, SGh, Tch, Sch = E.colcenter(S), E.colcenter(SG), E.colcenter(T), E.colcenter(Sc)
    regs = np.array([reg[p] for p in elig])
    mask_reg = regs[:, None] == regs[None, :]
    # adjacent decoys = nearest eligible periods before and after
    mask_adj = np.zeros((P, P), bool)
    for k in range(P):
        for j in (k - 1, k + 1):
            if 0 <= j < P:
                mask_adj[k, j] = True
    pi = E.own_percentiles(Sh)
    pi_raw = E.own_percentiles(S)
    t1 = E.top1(Sh)
    pi_reg = E.own_percentiles(Sh, mask_reg)
    t1_reg = E.top1(Sh, mask_reg)
    adj_win = np.array([np.all(Sh[k, mask_adj[k]] < Sh[k, k]) if np.isfinite(Sh[k, k]) else np.nan for k in range(P)], float)
    pi_goal = E.own_percentiles(SGh)
    pi_disp = E.own_percentiles(Tch)
    pi_chat = E.own_percentiles(Sch)
    np.save(out / "S_kick.npy", S)
    np.save(out / "S_goal.npy", SG)
    np.save(out / "T_disp.npy", T)
    for k, rec in enumerate(per):
        rec.update({"pi": pi[k], "pi_raw": pi_raw[k], "top1": t1[k], "pi_reg": pi_reg[k], "top1_reg": t1_reg[k],
                    "adj_win": adj_win[k], "pi_goal": pi_goal[k], "S_own_cc": Sh[k, k], "S_goal_cc": SGh[k, k],
                    "pi_disp": pi_disp[k], "pi_chat": pi_chat[k],
                    "rank": int(np.sum(np.delete(Sh[k], k) > Sh[k, k]) + 1) if np.isfinite(Sh[k, k]) else None})
    res = {"eligible": elig, "P1": E.p1_verdict(pi, t1)}
    res["P1"]["raw"] = {"median_pi": float(np.nanmedian(pi_raw)), "top1": float(np.nanmean(E.top1(S)))}
    res["P1"]["within_regime"] = {"median_pi": float(np.nanmedian(pi_reg)), "top1": float(np.nanmean(t1_reg))}
    res["P1"]["chat_only"] = {"median_pi": float(np.nanmedian(pi_chat)), "top1": float(np.nanmean(E.top1(Sch)))}
    res["P1"]["by_regime"] = {r: {"n": int(np.sum(regs == r)), "median_pi": float(np.nanmedian(pi[regs == r])),
                                  "top1": float(np.nanmean(t1[regs == r]))} for r in ("I", "II", "III")}
    res["P1b"] = {"adj_win_rate": float(np.nanmean(adj_win)), "n": int(np.isfinite(adj_win).sum())}
    jumps = np.array([r.get("jump", np.nan) for r in per])
    res["P1c"] = {"median_pi_disp": float(np.nanmedian(pi_disp)), "n": int(np.isfinite(pi_disp).sum()),
                  "top1_disp": float(np.nanmean(E.top1(Tch))), "jump_pos_rate": float(np.nanmean(jumps[np.isfinite(jumps)] > 0)),
                  "median_jump": float(np.nanmedian(jumps)), "p_wilcoxon_disp": E.wilcoxon_gt(pi_disp)}
    both = np.isfinite(Sh.diagonal()) & np.isfinite(SGh.diagonal())
    res["P1d"] = {"kick_beats_goal_cc": float(np.mean(Sh.diagonal()[both] > SGh.diagonal()[both])),
                  "kick_beats_goal_pi": float(np.mean(pi[both] > pi_goal[both])), "median_pi_goal": float(np.nanmedian(pi_goal)),
                  "top1_goal": float(np.nanmean(E.top1(SGh))), "n": int(both.sum())}
    print("P1", res["P1"], "\nP1b", res["P1b"], "\nP1c", res["P1c"], "\nP1d", res["P1d"])

    # ---------------------------------------------------------------- P3 specificity
    pdf = pl.DataFrame(per)
    x_text, x_cnt, x_emb = (pdf[c].to_numpy() for c in ("S_text", "S_count", "S_emb"))
    sig, dep = pdf["spread"].to_numpy(), pdf["depth_ex"].to_numpy()
    chunks = L.goals().filter(pl.col("kind") == "kickoff")
    chunk_of = dict(zip(chunks["goal_no"].to_list(), chunks["n_chunks"].to_list()))
    covars = np.column_stack([(pdf["regime"] == "III").to_numpy().astype(float), (pdf["regime"] == "I").to_numpy().astype(float),
                              np.log(pdf["n_agents"].to_numpy().astype(float)), np.log(pdf["words"].to_numpy().astype(float)),
                              np.log(np.array([chunk_of[p] for p in pdf["goal_no"].to_list()], float))])  # Amendment 1
    p3 = {}
    for nm, x in (("S_text", x_text), ("S_count", x_cnt), ("S_emb", x_emb)):
        r1, pv1, n1 = E.spearman(x, sig, "less")
        r2, pv2, _ = E.spearman(x, dep, "greater")
        pr1, ppv1 = E.partial_spearman(x, sig, covars)
        pr2, ppv2 = E.partial_spearman(x, dep, covars)
        p3[nm] = {"spread_rho": r1, "spread_p_one": pv1, "n": n1, "depth_rho": r2, "depth_p_one": pv2,
                  "spread_partial_rho": pr1, "spread_partial_p2": ppv1, "depth_partial_rho": pr2, "depth_partial_p2": ppv2}
    # within-regime ranks (regime I has the most periods)
    for r in ("I", "III"):
        m = (pdf["regime"] == r).to_numpy()
        a, b, n = E.spearman(x_text[m], sig[m], "less")
        p3[f"S_text_regime{r}"] = {"spread_rho": a, "spread_p_one": b, "n": n}
    res["P3"] = p3
    res["P3"]["verdict"] = ("supported" if p3["S_text"]["spread_rho"] <= -0.35 and p3["S_text"]["spread_p_one"] < 0.05
                            else "failed" if p3["S_text"]["spread_rho"] >= 0 else "mixed")
    print("P3", {k: v for k, v in p3.items()})

    # ---------------------------------------------------------------- P2 projects
    pr = pl.read_parquet(L.OUT / "projects.parquet")
    h31 = pr.filter(pl.col("src") == "H31")
    kf = (h31["cls"] == "kickoff_frozen").to_numpy()
    strata = h31["goal_no"].to_numpy()
    p2 = {}
    for nm in ("named", "named_strict", "named_loose_kick", "named_goal"):
        p2[nm] = E.naming_table(h31[nm].to_numpy(), kf, strata, 5000, RNG)
    p2["verdict"] = E.p2_verdict(p2["named"])
    p2["by_class"] = {c: {"n": int((h31["cls"] == c).sum()), "named_rate": float(h31.filter(pl.col("cls") == c)["named"].mean()),
                          "pre_existing_rate": float(h31.filter(pl.col("cls") == c)["pre_existing"].mean()),
                          "carry_over_rate": float(h31.filter((pl.col("cls") == c) & pl.col("carry_over").is_not_null())["carry_over"].mean())
                          if h31.filter((pl.col("cls") == c) & pl.col("carry_over").is_not_null()).height else None,
                          "carry_over_known": int(h31.filter((pl.col("cls") == c) & pl.col("carry_over").is_not_null()).height),
                          "plan_named_rate": float(h31.filter(pl.col("cls") == c)["plan_named"].mean()),
                          "human_day1_rate": float(h31.filter(pl.col("cls") == c)["human_day1"].mean())}
                      for c in ("kickoff_frozen", "instant", "gradual", "none")}
    fz = h31.filter(pl.col("cls") == "kickoff_frozen")
    p2["frozen_detail"] = [{"goal_no": r["goal_no"], "room": r["room"], "artifact": r["artifact"], "named": r["named"],
                            "strict": r["named_strict"], "loose_kick": r["named_loose_kick"], "goal": r["named_goal"],
                            "pre_existing": r["pre_existing"], "carry_over": r["carry_over"], "plan_named": r["plan_named"]}
                           for r in fz.iter_rows(named=True)]
    p2["P2b_carry"] = {"pre_existing_share": float(fz["pre_existing"].mean()),
                       "carry_over_share_known": float(fz.filter(pl.col("carry_over").is_not_null())["carry_over"].mean())
                       if fz.filter(pl.col("carry_over").is_not_null()).height else None,
                       "carry_known": int(fz.filter(pl.col("carry_over").is_not_null()).height),
                       "unnamed_and_pre_existing": int(fz.filter(~pl.col("named") & pl.col("pre_existing")).height)}
    # rival R1 as a predictor in the same table
    p2["R1_pre_existing_as_predictor"] = E.naming_table(h31["pre_existing"].to_numpy(), kf, strata, 5000, RNG)
    p2["named_or_plan"] = E.naming_table((h31["named"] | h31["plan_named"]).to_numpy(), kf, strata, 5000, RNG)
    own = pr.filter((pl.col("src") == "own") & pl.col("cls").is_in(["day1_dominant", "day1_scored"]))
    p2["P2c_own_rule"] = E.naming_table(own["named"].to_numpy(), (own["cls"] == "day1_dominant").to_numpy(), own["goal_no"].to_numpy(), 5000, RNG)
    p2["P2c_own_rule_pre_existing"] = E.naming_table(own["pre_existing"].to_numpy(), (own["cls"] == "day1_dominant").to_numpy(), own["goal_no"].to_numpy(), 5000, RNG)
    p2["P2c_verdict"] = E.p2_verdict(p2["P2c_own_rule"])
    # logistic: frozen ~ named + pre_existing
    X = np.column_stack([h31["named"].to_numpy().astype(float), h31["pre_existing"].to_numpy().astype(float)])
    w, se = E.logistic(kf.astype(float), X)
    p2["logit_named_pre"] = {"coef": w.tolist(), "se": se.tolist(), "names": ["const", "named", "pre_existing"]}
    res["P2"] = p2
    print("P2", {k: v for k, v in p2.items() if k not in ("frozen_detail",)})

    # P3c frozen fraction vs specificity
    ff = h31.group_by("goal_no").agg((pl.col("cls") == "kickoff_frozen").mean().alias("frac"), pl.len().alias("n"),
                                      pl.col("named").sum().alias("n_named"))
    ff = ff.join(pdf.select("goal_no", "S_text", "S_count"), on="goal_no")
    rf, pf, nf = E.spearman(ff["S_text"].to_numpy(), ff["frac"].to_numpy(), "greater")
    rfc, pfc, _ = E.spearman(ff["S_count"].to_numpy(), ff["frac"].to_numpy(), "greater")
    hh = h31.join(pdf.select("goal_no", "S_text"), on="goal_no").join(ff.select("goal_no", "n_named"), on="goal_no")
    Xl = np.column_stack([hh["named"].to_numpy().astype(float), hh["S_text"].to_numpy(), hh["n_named"].to_numpy().astype(float)])
    wl, sel = E.logistic((hh["cls"] == "kickoff_frozen").to_numpy().astype(float), Xl)
    res["P3c"] = {"period_frac_rho_S_text": rf, "p_one": pf, "n_periods": nf, "period_frac_rho_S_count": rfc, "p_one_count": pfc,
                  "logit": {"coef": wl.tolist(), "se": sel.tolist(), "names": ["const", "named", "S_text", "n_named_period"]}}
    print("P3c", res["P3c"])

    # ---------------------------------------------------------------- P4 human re-quenches (HH180) + pulse relaxation
    hm = pl.read_parquet(L.OUT / "human_msgs.parquet").filter(pl.col("goal_no").is_in(elig))
    hrows, traj = [], []
    offsets = [(0, 60), (60, 120), (120, 240), (240, 480)]
    for r_ in ("I", "II", "III"):
        sub = hm.filter(pl.col("goal_no").is_in([p for p in elig if reg[p] == r_]))
        if sub.height == 0:
            continue
        ids = sub["message_id"].to_list()
        EV = L.chat_vec(ids, r_)
        lens = sub["length"].to_numpy()
        for j, h in enumerate(sub.iter_rows(named=True)):
            p = h["goal_no"]
            s = st_i.filter((pl.col("goal_no") == p) & (pl.col("src_goal") == p) & (pl.col("day") >= 1))
            if reg[p] != "I":
                s = s.filter((pl.col("kind") == "chat") & (pl.col("room") == h["room"]))
            t = h["t"]

            def cen(a0, a1):
                w = s.filter((pl.col("t") > t + np.timedelta64(int(a0 * 60), "s")) & (pl.col("t") <= t + np.timedelta64(int(a1 * 60), "s"))) if a0 >= 0 else \
                    s.filter((pl.col("t") >= t + np.timedelta64(int(a0 * 60), "s")) & (pl.col("t") < t + np.timedelta64(int(a1 * 60), "s")))
                gg = w.group_by("agent").agg(pl.col("i"))
                if gg.height < 3:
                    return None
                return E.unit(np.vstack([E.unit(Z[np.asarray(ix)].mean(0)) for ix in gg["i"].to_list()]).mean(0))
            cb = cen(-60, 0)
            ca = cen(0, 60)
            if cb is None or ca is None or not np.all(np.isfinite(EV[j])):
                continue
            dec = [i for i in range(len(ids)) if i != j and sub["goal_no"][i] != p and 0.5 <= lens[i] / lens[j] <= 2 and np.all(np.isfinite(EV[i]))]
            if len(dec) < 5:
                dec = [i for i in range(len(ids)) if i != j and sub["goal_no"][i] != p and np.all(np.isfinite(EV[i]))]
            if len(dec) < 3:
                continue
            dec = RNG.choice(dec, min(50, len(dec)), replace=False)
            a_m = float(ca @ EV[j] - cb @ EV[j])
            a_d = (ca - cb) @ EV[dec].T
            delta = a_m - float(a_d.mean())
            pct = float(np.mean(a_d < a_m))
            hrows.append({"message_id": h["message_id"], "goal_no": p, "regime": r_, "a": a_m, "delta": delta, "pct": pct,
                          "S_text": h["S_text"], "S_count": h["S_count"], "receptive": h["receptive"], "n_read": h["n_read"],
                          "length": h["length"]})
            for (a0, a1) in offsets:
                cw = cen(a0, a1)
                if cw is not None:
                    traj.append({"message_id": h["message_id"], "mid_h": (a0 + a1) / 120, "ex": float((cw - cb) @ EV[j] - ((cw - cb) @ EV[dec].T).mean())})
    H = pl.DataFrame(hrows)
    H.write_parquet(out / "human.parquet")
    TR = pl.DataFrame(traj)
    TR.write_parquet(out / "human_traj.parquet")
    dl = H["delta"].to_numpy()
    sgn = stats.binomtest(int((dl > 0).sum()), len(dl), 0.5, alternative="greater").pvalue
    rs, ps, _ = E.spearman(H["S_text"].to_numpy(), dl, "greater")
    rr_, pr_, _ = E.spearman(H["receptive"].to_numpy(), dl, "greater")
    # pulse relaxation: median excess by offset; exponential decay fit
    med = TR.group_by("mid_h").agg(pl.col("ex").median(), pl.len()).sort("mid_h")
    fitH = E.exp_plateau_fit(med["mid_h"].to_numpy(), med["ex"].to_numpy())
    res["P4"] = {"n": len(dl), "median_delta": float(np.median(dl)), "pos_rate": float(np.mean(dl > 0)), "p_sign": float(sgn),
                 "median_pct": float(np.median(H["pct"].to_numpy())), "rho_spec": rs, "p_spec": ps, "rho_receptive": rr_, "p_receptive": pr_,
                 "receptive_share_eq1": float(np.mean(H["receptive"].to_numpy() >= 0.999)),
                 "by_regime": {r: {"n": int((H["regime"] == r).sum()), "median_delta": float(H.filter(pl.col("regime") == r)["delta"].median() or np.nan)}
                               for r in ("I", "II", "III")},
                 "by_period_n": dict(zip(*[H.group_by("goal_no").len().sort("goal_no")[c].to_list() for c in ("goal_no", "len")])),
                 "pulse_median_by_offset": dict(zip([str(x) for x in med["mid_h"].to_list()], med["ex"].to_list())), "pulse_fit": fitH}
    # without the two viewer-heavy periods (#4, #5)
    m45 = ~H["goal_no"].is_in([4, 5]).to_numpy()
    res["P4"]["excl_4_5"] = {"n": int(m45.sum()), "median_delta": float(np.median(dl[m45])), "pos_rate": float(np.mean(dl[m45] > 0))}
    print("P4", res["P4"])

    # ---------------------------------------------------------------- P5 remanence (HH182)
    rem, fits = [], {}
    cal = L.calendar()
    for p in elig:
        k, r = idx[p], reg[p]
        s = st_i.filter((pl.col("goal_no") == p) & (pl.col("src_goal") == p) & (pl.col("day") >= 1) & ~pl.col("pre_kick"))
        days = sorted(s["day"].unique().to_list())
        for d in days:
            gg = s.filter(pl.col("day") == d).group_by("agent").agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= 3)
            if gg.height < 3:
                continue
            V = np.vstack([E.unit(Z[np.asarray(ix)].mean(0)) for ix in gg["i"].to_list()])
            A = V @ Kb[r].T
            G_ = V @ Gb[r].T
            ex = float(A[:, k].mean() - np.delete(A, k, 1).mean())
            exg = float(G_[:, k].mean() - np.delete(G_, k, 1).mean())
            prevq = idx.get(p - 1)
            exprev = float(A[:, prevq].mean() - np.delete(A, [k, prevq], 1).mean()) if prevq is not None else np.nan
            rem.append({"goal_no": p, "day": d, "n_agents": gg.height, "ex_kick": ex, "ex_goal": exg, "ex_prev_kick": exprev})
        rp = [x for x in rem if x["goal_no"] == p]
        if len(rp) >= 5:
            f = E.exp_plateau_fit([x["day"] for x in rp], [x["ex_kick"] for x in rp])
            fg = E.exp_plateau_fit([x["day"] for x in rp], [x["ex_goal"] for x in rp])
            fits[p] = {"kick": f, "goal": fg, "last_ex": rp[-1]["ex_kick"], "first_ex": rp[0]["ex_kick"], "n_days": len(rp)}
    R = pl.DataFrame(rem)
    R.write_parquet(out / "remanence.parquet")
    lf = [v for v in fits.values()]
    hours = {"I": 4.0, "II": 4.0, "III": 6.0}
    tauK = np.array([v["kick"]["tau"] for v in lf])
    res["P5"] = {"n_periods": len(lf), "last_ex_pos_rate": float(np.mean([v["last_ex"] > 0 for v in lf])),
                 "exp_beats_const_rate": float(np.mean([v["kick"]["bic_exp"] < v["kick"]["bic_const"] - 2 for v in lf])),
                 "exp_beats_lin_rate": float(np.mean([v["kick"]["bic_exp"] < v["kick"]["bic_lin"] - 2 for v in lf])),
                 "median_tau_K_days": float(np.median(tauK)), "median_A_inf": float(np.median([v["kick"]["A_inf"] for v in lf])),
                 "median_A_1": float(np.median([v["kick"]["A_1"] for v in lf])),
                 "A_inf_pos_rate": float(np.mean([v["kick"]["A_inf"] > 0 for v in lf])),
                 "tau_H_hours": fitH["tau"] if fitH else None,
                 "fits": {str(k): v for k, v in fits.items()}}
    d1 = R.filter(pl.col("day") == 1)
    ep = d1["ex_prev_kick"].drop_nans().drop_nulls().to_numpy()
    res["P5"]["prev_kick_day1"] = {"n": len(ep), "median": float(np.median(ep)) if len(ep) else None,
                                   "pos_rate": float(np.mean(ep > 0)) if len(ep) else None,
                                   "p_wilcoxon": E.wilcoxon_gt(ep, 0.0)}
    # active-hours conversion of tau_K for comparison with the hour-scale pulse
    tauK_h = np.array([fits[p]["kick"]["tau"] * hours[reg[p]] for p in fits])
    res["P5"]["median_tau_K_active_hours"] = float(np.median(tauK_h))
    res["P5"]["tauK_over_tauH"] = float(np.median(tauK_h) / fitH["tau"]) if fitH and fitH["tau"] > 0 else None
    print("P5", {k: v for k, v in res["P5"].items() if k != "fits"})

    # ---------------------------------------------------------------- P6 first plans (HH181)
    fp = pl.read_parquet(L.OUT / "first_plans.parquet").filter(pl.col("scope") == "all")
    tf = pl.read_parquet(L.SHARED / "text_features.parquet", columns=["message_id", "agent", "t", "pt_date", "goal_no", "words"])
    plans = []
    for h in fp.iter_rows(named=True):
        p = h["goal_no"]
        if p not in idx:
            continue
        r = reg[p]
        d0 = st_i.filter((pl.col("goal_no") == p) & (pl.col("day") == 1))["pt_date"]
        if d0.len() == 0:
            continue
        day = d0[0]
        cand = tf.filter((pl.col("goal_no") == p) & (pl.col("pt_date") == day) & (pl.col("words") >= 40) & (pl.col("agent") != L.CLAUDE_CODE))
        ids = cand["message_id"].to_list()
        if h["message_id"] not in ids:
            ids.append(h["message_id"])
        EVp = L.chat_vec(ids, r)
        authors = dict(zip(cand["message_id"].to_list(), cand["agent"].to_list()))
        authors[h["message_id"]] = h["agent"]
        s1 = st_i.filter((pl.col("goal_no") == p) & (pl.col("src_goal") == p) & (pl.col("day") == 1) & ~pl.col("pre_kick"))
        gg = s1.group_by("agent").agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= 3)
        av = {a: E.unit(Z[np.asarray(ix)].mean(0)) for a, ix in zip(gg["agent"].to_list(), gg["i"].to_list())}
        if len(av) < 4:
            continue
        cent = {}

        def c_minus(a):
            if a not in cent:
                cent[a] = E.unit(np.vstack([v for b, v in av.items() if b != a]).mean(0))
            return cent[a]
        scores = np.array([c_minus(authors[m]) @ EVp[i] if np.all(np.isfinite(EVp[i])) else np.nan for i, m in enumerate(ids)])
        jp = ids.index(h["message_id"])
        dec = np.delete(scores, jp)
        dec = dec[np.isfinite(dec)]
        if len(dec) < 3 or not np.isfinite(scores[jp]):
            continue
        plans.append({"goal_no": p, "delta_P": float(scores[jp] - dec.mean()), "pct_P": float(np.mean(dec < scores[jp])), "n_decoys": len(dec),
                      "S_text": spec[p]["S_text"], "S_count": spec[p]["S_count"], "min_after_kick": h["min_after_kick"], "has_art": h["has_art"]})
    PL = pl.DataFrame(plans)
    PL.write_parquet(out / "plans.parquet")
    dP = PL["delta_P"].to_numpy()
    rps, pps, _ = E.spearman(PL["S_text"].to_numpy(), dP, "less")
    res["P6"] = {"n": len(dP), "pos_rate": float(np.mean(dP > 0)), "median_delta": float(np.median(dP)),
                 "median_pct": float(np.median(PL["pct_P"].to_numpy())), "p_wilcoxon_pct": E.wilcoxon_gt(PL["pct_P"].to_numpy()),
                 "rho_spec": rps, "p_spec": pps, "named_or_plan_table": p2["named_or_plan"]}
    print("P6", {k: v for k, v in res["P6"].items() if k != "named_or_plan_table"})

    # ---------------------------------------------------------------- P7 family susceptibility (HH184)
    chi_rows = []
    g0_map = {(a, b): i for i, (a, b) in enumerate(zip(g0["goal_no"].to_list(), g0["agent"].to_list()))}
    # style-residualized agent vectors (DQ5)
    st_s = st_i.with_columns(pl.Series("ok", np.all(np.isfinite(ZS), axis=1)))

    def vecs_s(cond):
        s = st_s.filter(cond & pl.col("ok"))
        g = s.group_by("goal_no", "agent").agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= 3)
        return {(a, b): E.unit(ZS[np.asarray(ix)].mean(0)) for a, b, ix in zip(g["goal_no"].to_list(), g["agent"].to_list(), g["i"].to_list())}
    s1v = vecs_s(cur & (pl.col("day") == 1) & ~pl.col("pre_kick"))
    s0v = vecs_s(pl.col("day") == 0)
    for i, (p, a) in enumerate(zip(g1["goal_no"].to_list(), g1["agent"].to_list())):
        j = g0_map.get((p, a))
        if j is None:
            continue
        k, r = idx[p], reg[p]
        kv = Kb[r][k]
        chi = float(V1[i] @ kv - V0[j] @ kv)
        chis = float(s1v[(p, a)] @ kv - s0v[(p, a)] @ kv) if (p, a) in s1v and (p, a) in s0v else np.nan
        chi_rows.append({"goal_no": p, "agent": a, "lab": lab.get(a), "chi": chi, "chi_style": chis, "regime": r})
    CH = pl.DataFrame(chi_rows)
    CH = CH.with_columns((pl.col("chi") - pl.col("chi").mean().over("goal_no")).alias("chi_d"),
                         (pl.col("chi_style") - pl.col("chi_style").mean().over("goal_no")).alias("chi_style_d"))
    CH.write_parquet(out / "chi.parquet")

    def lab_test(col):
        d = CH.filter(pl.col(col).is_not_nan() & pl.col(col).is_not_null())
        y = d[col].to_numpy()
        agents = d["agent"].to_numpy()
        labs = d["lab"].to_numpy()

        def F(lb):
            groups = [y[lb == u] for u in np.unique(lb)]
            groups = [g for g in groups if len(g) >= 3]
            return stats.f_oneway(*groups).statistic if len(groups) >= 2 else np.nan
        obs = F(labs)
        ua = np.unique(agents)
        amap = {a: labs[agents == a][0] for a in ua}
        cnt = 0
        nperm = 2000
        for _ in range(nperm):
            pa = dict(zip(ua, RNG.permutation([amap[a] for a in ua])))
            cnt += F(np.array([pa[a] for a in agents])) >= obs
        means = {u: float(y[labs == u].mean()) for u in np.unique(labs) if (labs == u).sum() >= 3}
        # split-half agent stability
        d2 = d.with_columns(pl.col("goal_no").rank("dense").over("agent").alias("kk"))
        h1 = d2.filter(pl.col("kk") % 2 == 1).group_by("agent").agg(pl.col(col).mean().alias("a"), pl.len().alias("na"))
        h2 = d2.filter(pl.col("kk") % 2 == 0).group_by("agent").agg(pl.col(col).mean().alias("b"), pl.len().alias("nb"))
        hh_ = h1.join(h2, on="agent").filter((pl.col("na") >= 2) & (pl.col("nb") >= 2))
        rsh = float(np.corrcoef(hh_["a"].to_numpy(), hh_["b"].to_numpy())[0, 1]) if hh_.height >= 5 else np.nan
        return {"n": len(y), "n_agents": len(ua), "F": float(obs), "p_perm_agent_lab": (cnt + 1) / (nperm + 1), "lab_means": means,
                "split_half_r": rsh, "split_half_n_agents": hh_.height}
    res["P7"] = {"chi": lab_test("chi_d"), "chi_style": lab_test("chi_style_d"),
                 "median_chi": float(CH["chi"].median()), "chi_pos_rate": float((CH["chi"] > 0).mean())}
    print("P7", res["P7"])

    # ---------------------------------------------------------------- write
    pdf = pl.DataFrame(per)
    pdf.write_parquet(out / "periods.parquet")
    for rec in per:
        p = rec["goal_no"]
        extra = {"remanence": fits.get(p), "plan": next((x for x in plans if x["goal_no"] == p), None),
                 "human": {"n": int((H["goal_no"] == p).sum()), "median_delta": float(H.filter(pl.col("goal_no") == p)["delta"].median())
                           if (H["goal_no"] == p).sum() else None},
                 "projects_h31": h31.filter(pl.col("goal_no") == p).select("room", "cls", "named", "pre_existing", "plan_named").to_dicts(),
                 "chi": CH.filter(pl.col("goal_no") == p).select("agent", "lab", "chi").to_dicts()}
        L.write_json(L.OUT / f"G{p:02d}" / "results.json", {**rec, **extra})
    res["runtime_s"] = time.time() - t0
    L.write_json(out / "results.json", res)
    L.provenance("analysis/explore.py", ["H54 scheme outputs (stmt, kickoffs, projects, human_msgs, first_plans)", "goal_fields",
                                         "text_features", "roster"], {"rng": 54, "n_rare": L.N_RARE, "n_min": L.N_MIN})
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
