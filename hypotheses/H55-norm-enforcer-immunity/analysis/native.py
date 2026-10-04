"""H55 period-native tests: G51 roles, G12 judges, G16 operator rules, G38 loop-densest week.

  uv run python hypotheses/H55-norm-enforcer-immunity/analysis/native.py [--only G51,G12,G16,G38]
Outputs: data/processed/H55-norm-enforcer-immunity/G<NN>/native.json (codes and numbers only).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h55lib as L  # noqa: E402
from h55lib import H, NL  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

RNG = np.random.default_rng(H.SEED + 20)


def gt(goal):
    g = pl.read_parquet(H.SH / "ground_truth_labels.parquet")
    return g.filter((pl.col("goal_no") == goal) & pl.col("preferred") & ~pl.col("holdout"))


def perm_diff(vals, isE, R=5000, rng=RNG):
    vals, isE = np.asarray(vals, float), np.asarray(isE, bool)
    obs = vals[isE].mean() - vals[~isE].mean()
    null = np.empty(R)
    for k in range(R):
        e = rng.permutation(isE)
        null[k] = vals[e].mean() - vals[~e].mean()
    return {"diff": float(obs), "p_greater": float((1 + np.sum(null >= obs)) / (R + 1)), "nE": int(isE.sum()), "n": int(len(vals))}


# ============================================================================================================ G51
def g51():
    out = {}
    roles = gt(51).filter(pl.col("label_kind") == "role")
    role_of = {}
    for a, v in roles.select("agent", "value").iter_rows():
        role_of.setdefault(a, set()).add(v)
    E = {a for a, vs in role_of.items() if vs & set(H.ENFORCER_ROLES)}
    Ep = {a for a, vs in role_of.items() if vs & set(H.ENFORCER_ROLES_EXT)}
    out["E"], out["E_ext"] = sorted(E), sorted(Ep)
    msgs = pl.read_parquet(H.OUT / "messages.parquet")
    rates = L.sender_rates(msgs).filter(pl.col("goal_no") == 51)
    pp = L.pair_table().filter(pl.col("goal_no") == 51)
    fa = L.friction_agent(pp, rates, R=2000, rng=RNG)
    out["friction_agent"] = {k: fa[k] for k in ("rho", "p", "rho_partial", "p_partial", "n_agents")}
    ag = np.array(fa["agents"])
    holders = np.array([a in role_of for a in ag])
    c, nu = np.array(fa["c"]), np.array(fa["nu"])
    for nm, S in (("E", E), ("E_ext", Ep)):
        isE = np.array([a in S for a in ag])[holders]
        out[f"N51a_{nm}"] = perm_diff(c[holders], isE)
        out[f"N51b_{nm}"] = perm_diff(nu[holders], isE)
        # soft-sensor variant of c: q_soft per parented message
    q = msgs.filter((pl.col("goal_no") == 51) & (pl.col("speaker_kind") == "agent") & pl.col("parent_id").is_not_null()).with_columns(
        (pl.col("p_reply").fill_null(0) * pl.col("p_opposes").fill_null(0) * (pl.col("p_opp_correction").fill_null(0) + pl.col("p_opp_decline").fill_null(0))).alias("q"))
    qm = dict(q.group_by("agent").agg(pl.col("q").mean()).iter_rows())
    qv = np.array([qm.get(a, 0.0) for a in ag])
    out["N51a_E_soft"] = perm_diff(qv[holders], np.array([a in E for a in ag])[holders])
    out["agents"] = [{"agent": int(a), "E": a in E, "E_ext": a in Ep, "holder": bool(h), "c": float(ci), "nu": float(ni)}
                     for a, h, ci, ni in zip(ag, holders, c, nu)]
    # ---- N51c: significant negative pairs vs calibrated agent-field null
    agl, a_f, b_f, ok, spk, tgt = L.fit_fields(pp)
    y = pp["y"].to_numpy().astype(float)
    N = len(agl)
    isE_idx = np.array([a in E for a in agl])

    def sig_pairs(yy):
        J, C, r, key = NL._residual_matrix(spk, tgt, yy, N, 3)
        u = np.unique(key)
        pv, kk = [], []
        for k_ in u:
            rr = r[key == k_]
            if len(rr) < 3:
                continue
            sd = rr.std(ddof=1)
            if sd <= 0:
                continue
            pv.append(stats.t.cdf(rr.mean() / (sd / np.sqrt(len(rr))), len(rr) - 1))
            kk.append(k_)
        pv, kk = np.array(pv), np.array(kk)
        if not len(pv):
            return 0, 0
        o = np.argsort(pv)
        ok_ = pv[o] <= 0.1 * np.arange(1, len(pv) + 1) / len(pv)
        nsig = int(np.flatnonzero(ok_).max() + 1) if ok_.any() else 0
        sig = kk[o][:nsig]
        lo, hi = sig // N, sig % N
        return nsig, int(np.sum(isE_idx[lo] | isE_idx[hi]))
    nsig, nE = sig_pairs(y)
    null = [sig_pairs(ys) for ys in NL.agent_field_null(spk, tgt, y, N, 200, RNG)]
    ns = np.array([x[0] for x in null]); nE0 = np.array([x[1] for x in null])
    out["N51c"] = {"n_sig_neg_pairs": nsig, "n_involving_E": nE, "null_mean_sig": float(ns.mean()), "null_mean_E": float(nE0.mean()),
                   "p_sig": float((1 + np.sum(ns >= nsig)) / 201), "p_E": float((1 + np.sum(nE0 >= nE)) / 201),
                   "share_E_obs": nE / nsig if nsig else None,
                   "share_pairs_with_E": float(np.mean([(isE_idx[i] or isE_idx[j]) for i in range(N) for j in range(i + 1, N)]))}
    # ---- N51d: immune by role (directed reads from E agents vs other directed reads)
    for kind in ("loop", "blocked"):
        from explore import load_steps
        s, rd = load_steps(kind, "restate") if kind == "loop" else load_steps(kind)
        rd = rd.with_columns(pl.col("snd").is_in(list(E)).fill_null(False).alias("from_E"))
        if kind == "loop":
            st = pl.read_parquet(H.OUT / "loop_steps.parquet").filter((pl.col("version") == "restate") & pl.col("y").is_not_null() & (pl.col("goal_no") == 51))
            s2 = L.steps_with_reads(st, rd, pl.read_parquet(H.OUT / "reads_loop_volume.parquet"), "anchor_id", sensor="from_E")
        else:
            st = pl.read_parquet(H.OUT / "blocked_steps.parquet").filter(pl.col("y").is_not_null() & (pl.col("goal_no") == 51))
            st = st.with_columns((pl.col("t0").cast(pl.Int64).cast(pl.Utf8) + "_" + pl.col("agent").cast(pl.Utf8)).alias("win_id"))
            s2 = L.steps_with_reads(st, rd, pl.read_parquet(H.OUT / "reads_blocked_volume.parquet"), "win_id", sensor="from_E")
        s2 = s2.filter(~pl.col("agent").is_in(list(E)))   # recipients outside E
        ic = L.immune_contrast(s2, rng=RNG, B=2000)
        ic.pop("diffs", None); ic.pop("clusters", None)
        out[f"N51d_{kind}"] = ic
    return out


# ============================================================================================================ G12
def g12():
    out = {}
    g = gt(12)
    judges = {u: a for u, a in g.filter(pl.col("label_kind") == "judge").select("unit", "agent").iter_rows()}
    teams = g.filter(pl.col("label_kind") == "team").select("unit", "agent", "value")
    ph = g.filter(pl.col("label_kind") == "phase")
    msgs = pl.read_parquet(H.OUT / "messages.parquet").filter((pl.col("goal_no") == 12) & (pl.col("speaker_kind") == "agent"))
    pp = L.pair_table().filter(pl.col("goal_no") == 12)
    tB = msgs.select(pl.col("message_id").alias("B_message_id"), pl.col("t").alias("tB"))
    pp = pp.join(tB, on="B_message_id", how="left")
    for win in ("deb", "whole"):
        res_a, res_b = [], []
        for u, j in judges.items():
            if win == "deb":
                w = ph.filter((pl.col("unit") == u) & (pl.col("value") == "deb"))
            else:
                w = g.filter((pl.col("label_kind") == "judge") & (pl.col("unit") == u))
            t0, t1 = w["t_valid_from"].min(), w["t_valid_to"].max()
            mm = msgs.filter((pl.col("t") >= t0) & (pl.col("t") < t1) & pl.col("parent_id").is_not_null())
            tm = dict(teams.filter(pl.col("unit") == u).select("agent", "value").iter_rows())
            deb = [a for a, v in tm.items() if v in ("gov", "opp")]
            # N12a: judge vs debaters correction rate (Jev, and soft q)
            mm = mm.with_columns((pl.col("p_reply").fill_null(0) * pl.col("p_opposes").fill_null(0) * (pl.col("p_opp_correction").fill_null(0) + pl.col("p_opp_decline").fill_null(0))).alias("q"))
            byag = {a: (n, cj, qq) for a, n, cj, qq in mm.group_by("agent").agg(pl.len(), pl.col("corr_jev").sum(), pl.col("q").sum()).iter_rows()}
            if j in byag and any(a in byag for a in deb):
                nj, cj, qj = byag[j]
                nd = sum(byag[a][0] for a in deb if a in byag)
                cd = sum(byag[a][1] for a in deb if a in byag)
                qd = sum(byag[a][2] for a in deb if a in byag)
                res_a.append({"unit": u, "judge_rate": cj / nj, "deb_rate": cd / nd, "judge_q": qj / nj, "deb_q": qd / nd, "nj": nj, "nd": nd})
            # N12b: debaters' replies to judge vs to teammates (within speaker)
            pw = pp.filter((pl.col("tB") >= t0) & (pl.col("tB") < t1) & pl.col("b_agent").is_in(deb))
            for spk_ in deb:
                ps = pw.filter(pl.col("b_agent") == spk_)
                toj = ps.filter(pl.col("a_agent") == j)["s"]
                tot = ps.filter(pl.col("a_agent").is_in([a for a in deb if tm.get(a) == tm.get(spk_) and a != spk_]))["s"]
                too = ps.filter(pl.col("a_agent").is_in([a for a in deb if tm.get(a) != tm.get(spk_)]))["s"]
                if len(toj) and len(tot):
                    res_b.append({"unit": u, "speaker": int(spk_), "s_judge": float(toj.mean()), "s_team": float(tot.mean()),
                                  "s_opp": float(too.mean()) if len(too) else None, "n_j": len(toj), "n_t": len(tot)})
        da = pl.DataFrame(res_a) if res_a else None
        db = pl.DataFrame(res_b) if res_b else None
        r = {}
        if da is not None and da.height:
            d = (da["judge_rate"] - da["deb_rate"]).to_numpy()
            dq = (da["judge_q"] - da["deb_q"]).to_numpy()
            r["N12a"] = {"debates": da.height, "mean_diff_rate": float(d.mean()), "n_pos": int((d > 0).sum()), "n_zero": int((d == 0).sum()),
                         "sign_p": float(stats.binomtest(int((d > 0).sum()), int((d != 0).sum()), alternative="greater").pvalue) if (d != 0).sum() else None,
                         "mean_diff_soft": float(dq.mean()), "n_pos_soft": int((dq > 0).sum()),
                         "sign_p_soft": float(stats.binomtest(int((dq > 0).sum()), int((dq != 0).sum()), alternative="greater").pvalue) if (dq != 0).sum() else None,
                         "judge_rate_mean": float(da["judge_rate"].mean()), "deb_rate_mean": float(da["deb_rate"].mean())}
        if db is not None and db.height:
            per = db.group_by("unit").agg((pl.col("s_judge") - pl.col("s_team")).mean().alias("d"),
                                          (pl.col("s_judge") - pl.col("s_opp")).mean().alias("d_opp"))
            d = per["d"].to_numpy()
            bs = [RNG.choice(d, len(d)).mean() for _ in range(5000)]
            r["N12b"] = {"debates": per.height, "speaker_rows": db.height, "mean_s_judge_minus_team": float(d.mean()),
                         "ci": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
                         "n_neg": int((d < 0).sum()),
                         "sign_p_less": float(stats.binomtest(int((d < 0).sum()), len(d), alternative="greater").pvalue),
                         "mean_s_judge_minus_opp": float(np.nanmean(per["d_opp"].to_numpy().astype(float))),
                         "s_judge": float(db["s_judge"].mean()), "s_team": float(db["s_team"].mean())}
        out[win] = r
    return out


# ============================================================================================================ G16
RX_SHEET = re.compile(r"spreadsheet|google sheet|\bsheets?\b", re.I)
RX_BUG = re.compile(r"bug report|reporting (?:a |the |this )?bug|self[- ]caused|\bbugs?\b", re.I)


def g16():
    out = {}
    msgs = pl.read_parquet(H.OUT / "messages.parquet").filter(pl.col("goal_no").is_in([11, 13, 16, 17]))
    tx = pl.read_parquet(H.SH / "chat_text.parquet", columns=["message_id", "text"]).join(msgs.select("message_id"), on="message_id")
    T = dict(zip(tx["message_id"].to_list(), tx["text"].to_list()))
    sheet = [bool(RX_SHEET.search(T.get(m) or "")) for m in msgs["message_id"].to_list()]
    bug = [bool(RX_BUG.search(T.get(m) or "")) for m in msgs["message_id"].to_list()]
    del T, tx
    msgs = msgs.with_columns(pl.Series("sheet", sheet), pl.Series("bug", bug))
    ag = msgs.filter(pl.col("speaker_kind") == "agent")
    per = ag.group_by("goal_no").agg(pl.len().alias("n"), pl.col("sheet").mean().alias("sheet_share"), pl.col("bug").mean().alias("bug_share"),
                                     (pl.col("addressed")).sum().alias("n_addr")).sort("goal_no")
    out["shares"] = per.to_dicts()
    sh = {r["goal_no"]: r for r in out["shares"]}
    for b in (13, 11, 17):
        out[f"N16b_ratio_sheet_vs_{b}"] = sh[16]["sheet_share"] / sh[b]["sheet_share"] if sh[b]["sheet_share"] else None
        out[f"N16b_ratio_bug_vs_{b}"] = sh[16]["bug_share"] / sh[b]["bug_share"] if sh[b]["bug_share"] else None
    # daily shares in G16 (did the targeted topics fall over the week?)
    out["g16_daily"] = ag.filter(pl.col("goal_no") == 16).group_by("pt_date").agg(pl.len(), pl.col("sheet").mean(), pl.col("bug").mean()).sort("pt_date").to_dicts()
    # N16a: peer enforcement messages
    enf = ag.filter((pl.col("goal_no") == 16) & (pl.col("targets").list.len() > 0) & (pl.col("sheet") | pl.col("bug"))
                    & (pl.col("corr_jev") | pl.col("lex_norm")))
    n_addr16 = int(ag.filter((pl.col("goal_no") == 16) & pl.col("addressed")).height)
    out["N16a"] = {"n_enforce_candidates": enf.height, "n_addressed": n_addr16, "share": enf.height / max(n_addr16, 1),
                   "n_corr_jev_rule_topic": int(enf["corr_jev"].sum()), "n_lexnorm_rule_topic": int(enf["lex_norm"].sum()),
                   "baseline_same_rule_g13": int(ag.filter((pl.col("goal_no") == 13) & (pl.col("targets").list.len() > 0) & (pl.col("sheet") | pl.col("bug")) & (pl.col("corr_jev") | pl.col("lex_norm"))).height)}
    # human (operator) messages on the rule topics in G16
    hm = msgs.filter((pl.col("goal_no") == 16) & (pl.col("speaker_kind") == "human"))
    out["human_rule_topic_msgs_g16"] = int((hm["sheet"] | hm["bug"]).sum())
    out["human_msgs_g16"] = hm.height
    return out


# ============================================================================================================ G38
def g38():
    out = {}
    from explore import load_steps
    for version in ("restate", "copy"):
        s, rd = load_steps("loop", version)
        s = s.filter(pl.col("goal_no") == 38)
        out[f"N38a_{version}"] = L.address_contrast(s, rng=RNG, B=2000)
        for room, nm in ((2, "best"), (3, "rest")):
            out[f"N38a_{version}_{nm}"] = L.address_contrast(s.filter(pl.col("room") == room), rng=RNG, B=2000)
        # N38b novelty among directed-read steps: top vs bottom tercile of first directed message novelty
        d = s.filter((pl.col("n_dir") > 0) & pl.col("first_nov").is_not_null())
        if d.height >= 15:
            q1, q2 = d["first_nov"].quantile(1 / 3), d["first_nov"].quantile(2 / 3)
            top = d.filter(pl.col("first_nov") >= q2)
            bot = d.filter(pl.col("first_nov") <= q1)
            diff = float(top["y"].mean() - bot["y"].mean())
            cl = np.r_[(top["agent"].cast(pl.Utf8) + top["pt_date"]).to_numpy(), (bot["agent"].cast(pl.Utf8) + bot["pt_date"]).to_numpy()]
            yy = np.r_[top["y"].to_numpy(), bot["y"].to_numpy()].astype(float)
            grp = np.r_[np.ones(top.height), np.zeros(bot.height)]
            u, inv = np.unique(cl, return_inverse=True)
            bs = []
            for _ in range(2000):
                pick = RNG.integers(0, len(u), len(u))
                w = np.bincount(pick, minlength=len(u))[inv]
                if (w * grp).sum() and (w * (1 - grp)).sum():
                    bs.append((w * grp * yy).sum() / (w * grp).sum() - (w * (1 - grp) * yy).sum() / (w * (1 - grp)).sum())
            bs = np.array(bs)
            out[f"N38b_{version}"] = {"diff_top_minus_bottom": diff, "ci": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
                                      "p_two": float(2 * min((bs <= 0).mean(), (bs >= 0).mean())), "n_top": top.height, "n_bot": bot.height}
            # within-agent version: regress y on novelty rank with agent demeaning
            dd = d.with_columns(pl.col("first_nov").rank().over("agent").alias("rk"), pl.len().over("agent").alias("na")).filter(pl.col("na") >= 3)
            if dd.height >= 15:
                yr = (dd["y"] - dd.group_by("agent").agg(pl.col("y").mean().alias("m")).join(dd.select("agent"), on="agent", how="right")["m"]).to_numpy() if False else None
        out[f"counts_{version}"] = {"steps": s.height, "dir_steps": int((s["n_dir"] > 0).sum()), "trt_steps": int(s["treated"].sum()),
                                    "escape": float(s["y"].mean())}
    eps = pl.read_parquet(H.OUT / "loops.parquet").filter((pl.col("version") == "restate") & (pl.col("goal_no") == 38))
    summ = json.loads((H.OUT / "replication/summary.json").read_text())
    p8 = {r["goal_no"]: r for r in summ["P8"]["by_period"]}
    out["N38c"] = {"episodes": eps.height, "share_with_jev_correction": p8.get(38, {}).get("corr"), "share_with_directed": p8.get(38, {}).get("dir")}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="G51,G12,G16,G38")
    a = ap.parse_args()
    fns = {"G51": g51, "G12": g12, "G16": g16, "G38": g38}
    for k in a.only.split(","):
        res = fns[k]()
        d = H.OUT / k
        d.mkdir(exist_ok=True)
        (d / "native.json").write_text(json.dumps(res, indent=1, default=str))
        print(k, json.dumps({kk: v for kk, v in res.items() if kk not in ("agents", "g16_daily")}, indent=1, default=str)[:4000])
    H.write_prov("native", "hypotheses/H55-norm-enforcer-immunity/analysis/native.py",
                 ["H55 messages/loops/blocked/reads", "reply_pairs", "ground_truth_labels", "chat_text (in memory, G16 counts)"],
                 {"enforcer_roles": H.ENFORCER_ROLES, "enforcer_roles_ext": H.ENFORCER_ROLES_EXT})


if __name__ == "__main__":
    main()
