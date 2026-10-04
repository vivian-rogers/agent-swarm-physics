"""H21 x G12 POST-HOC checks (written 2026-10-03 AFTER seeing the primary null result; exploratory, not pre-registered).

Q1  Dilution: is staggered order hidden by procedural / waiting messages? Speeches only (debater messages in 'deb'
    with >= 400 characters; one-paragraph speeches are long), min 1 per agent.
Q2  Dimension: D = 128 whitened (all stored components).
Q3  Family vs team inside debates: same-lab minus different-lab mean pair cosine (agent- and debate-centred 'deb'
    spins), exact null over all 420 assignments of the lab labels to the 7 agents (group sizes 3/2/1/1 kept).
Q4  Uniform (topic) field on/off: topic alignment M_u . g_d in pre / deb / post (from results.json), sign tests.
Q5  A-priori text axis at the statement level: Gov-minus-Opp mean projection of 'deb' statements on the pro-minus-con
    template axis, per debate; team-permutation null at the agent level.
Q6  Remanence on the axis where order exists: the Q5 statistic in the 'pre' and 'post' phases (verdict = the switch).
Q7  Decompose the post-verdict move along the text axis (agent-level, fixed frame): s_i = eps_i (p_i,post - p_i,deb).
    Winner field w (everyone moves toward the winner): s = +w for winners, -w for losers. Crossing / balance field
    kappa (each agent moves toward the side it did NOT argue): s = -kappa for all. So kappa = -(s_W + s_L)/2 and
    w = (s_W - s_L)/2, per debate, then debate-bootstrap CIs. Also the judge's verdict message projection on the text
    axis, signed by the winner (manipulation check on an axis where order exists).
Writes data/processed/H21-debate-antiferromagnet/G12/results_posthoc.json.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import afmlib as L  # noqa: E402
import g12_analysis as G  # noqa: E402
import h21core as C  # noqa: E402

RNG = 20261003


def sign_test(x):
    x = np.asarray(x)
    k, n = int((x > 0).sum()), int((x != 0).sum())
    return k, n, float(sum(math.comb(n, j) for j in range(k, n + 1)) / 2 ** n)


def main():
    out = {}
    st_pl, st, X, debates, lab_of, W = G.load(32)
    Xc = L.agent_center(X, st["agent"])
    # Q1 speeches only
    long_ = st_pl["length"].to_numpy() >= 400
    st_sp = dict(st, phase=np.where(long_ & (st["phase"] == "deb"), "deb", "x").astype(object))
    Wsp = C.build_windows(X, st_sp, debates, "deb", min_n=1, Xc=Xc)
    out["Q1_speeches_only"] = {k: v for k, v in C.static_tests(Wsp, 50000, RNG).items() if k != "per_debate"}
    out["Q1_speeches_only"]["n_speech_statements"] = int((long_ & (st["phase"] == "deb")).sum())
    # Q2 D = 128
    _, st128, X128, _, _, _ = G.load(128)
    W128 = C.build_windows(X128, st128, debates, "deb")
    out["Q2_D128"] = {k: v for k, v in C.static_tests(W128, 50000, RNG).items() if k != "per_debate"}
    # Q3 same-lab vs different-lab pair cosine inside debate windows
    Wd = C.build_windows(X, st, debates, "deb", Xc=Xc)
    agents = sorted({int(a) for w in Wd for a in w["agents"]})
    labs = [lab_of[a] for a in agents]

    def lab_stat(labmap):
        same, diff = [], []
        for w in Wd:
            G_ = w["S"] @ w["S"].T
            for i, j in zip(*np.triu_indices(len(w["agents"]), 1)):
                (same if labmap[w["agents"][i]] == labmap[w["agents"][j]] else diff).append(G_[i, j])
        return float(np.mean(same) - np.mean(diff)) if same and diff else np.nan

    obs = lab_stat(dict(zip(agents, labs)))
    perms = {tuple(p) for p in itertools.permutations(labs)}
    nul = np.array([lab_stat(dict(zip(agents, p))) for p in perms])
    out["Q3_same_lab_pairs"] = {"same_minus_diff_cos": obs, "n_assignments": len(perms), "p_exact": L.p_upper(obs, nul),
                                "null_q95": float(np.nanquantile(nul, 0.95))}
    team_obs = float(np.mean([L.delta_stat(w["S"], w["eps"]) for w in Wd]))
    out["Q3_same_lab_pairs"]["for_comparison_team_delta"] = team_obs
    # Q4 topic field on/off
    R = json.loads((G.DATA / "results.json").read_text())
    mg = {(m["debate"], m["phase"]): m["Mu_topic"] for m in R["magnetization"]}
    deb = [d["debate"] for d in debates]
    dd = [(mg[(d, "deb")], mg.get((d, "post"))) for d in deb if (d, "deb") in mg and (d, "post") in mg]
    pd_ = [(mg.get((d, "pre")), mg[(d, "deb")]) for d in deb if (d, "deb") in mg and (d, "pre") in mg]
    out["Q4_topic_field"] = {"Mu_topic_mean": {ph: float(np.mean([v for (d, p), v in mg.items() if p == ph])) for ph in ("pre", "deb", "post")},
                             "deb_minus_post_sign": sign_test([a - b for a, b in dd]),
                             "deb_minus_pre_sign": sign_test([b - a for a, b in pd_]),
                             "deb_positive_sign": sign_test([mg[(d, "deb")] for d in deb if (d, "deb") in mg])}
    # Q5 statement-level text axis
    mot = np.load(G.DATA / "motions.npz")
    ax = {int(d): L.unit(W(e[1][None])[0] - W(e[2][None])[0]) for d, e in zip(mot["debates"], mot["emb"])}
    rng = np.random.default_rng(RNG)
    def text_stat(phase):
        diffs, per = [], []
        for deb_ in debates:
            m = (st["debate"] == deb_["debate"]) & (st["phase"] == phase) & np.isin(st["agent"], deb_["gov"] + deb_["opp"])
            idx = np.flatnonzero(m)
            if deb_["debate"] not in ax or len(idx) < 4:
                continue
            proj = Xc[idx] @ ax[deb_["debate"]]
            ag = st["agent"][idx]
            members = sorted(set(ag))
            eps = {a: C.team_of(deb_, a) for a in members}
            if len({eps[a] for a in members}) < 2:
                continue

            def stat(e):
                g = np.array([e[a] for a in ag])
                return proj[g == 1].mean() - proj[g == -1].mean()
            allv = []
            kA = sum(1 for a in members if eps[a] == 1)
            for part in L.partitions(len(members), kA):
                e = dict(zip(members, part))
                allv.append(stat(e))
                if 2 * kA == len(members):
                    allv.append(stat({a: -v for a, v in e.items()}))
            per.append({"debate": deb_["debate"], "obs": stat(eps), "all": np.array(allv)})
            diffs.append(stat(eps))
        o = float(np.mean(diffs))
        n5 = L.perm_null(per, "all", 50000, RNG)
        return {"gov_minus_opp_projection": o, "p": L.p_upper(o, n5), "n_debates": len(per),
                "positive_debates": int(sum(d > 0 for d in diffs)), "per_debate": {int(q["debate"]): float(q["obs"]) for q in per}}

    out["Q5_text_axis_statement_level"] = text_stat("deb")
    out["Q6_text_axis_by_phase"] = {ph: text_stat(ph) for ph in ("pre", "post")}
    common = [d for d in out["Q6_text_axis_by_phase"]["post"]["per_debate"] if d in out["Q5_text_axis_statement_level"]["per_debate"]]
    dpost = [out["Q5_text_axis_statement_level"]["per_debate"][d] for d in common]
    ppost = [out["Q6_text_axis_by_phase"]["post"]["per_debate"][d] for d in common]
    out["Q6_text_axis_by_phase"]["remanence_post_over_deb"] = float(np.mean(ppost) / np.mean(dpost)) if common else np.nan
    out["Q6_text_axis_by_phase"]["remanence_ci"] = L.ratio_boot_ci(np.array(ppost), np.array(dpost), 5000, RNG) if common else None
    out["Q6_text_axis_by_phase"]["n_common"] = len(common)
    # Q7
    kap, wf, jud = [], [], []
    for deb_ in debates:
        d = deb_["debate"]
        if d not in ax or not deb_.get("winner"):
            continue
        members = deb_["gov"] + deb_["opp"]
        sW, sL = [], []
        for a in members:
            md = (st["debate"] == d) & (st["phase"] == "deb") & (st["agent"] == a)
            mp = (st["debate"] == d) & (st["phase"] == "post") & (st["agent"] == a)
            if md.sum() < 1 or mp.sum() < 1:
                continue
            e = C.team_of(deb_, a)
            sv = e * ((Xc[mp] @ ax[d]).mean() - (Xc[md] @ ax[d]).mean())
            (sW if e == deb_["winner"] else sL).append(sv)
        if sW and sL:
            kap.append(-(np.mean(sW) + np.mean(sL)) / 2)
            wf.append((np.mean(sW) - np.mean(sL)) / 2)
        r = np.flatnonzero(st_pl["is_verdict"].to_numpy() & (st["debate"] == d))
        if len(r):
            jud.append(float(deb_["winner"] * (Xc[r[0]] @ ax[d])))
    out["Q7_post_verdict_decomposition"] = {
        "kappa_crossing": float(np.mean(kap)), "kappa_ci": L.boot_ci(kap, 5000, RNG), "kappa_pos": sign_test(kap),
        "w_winner_field": float(np.mean(wf)), "w_ci": L.boot_ci(wf, 5000, RNG), "w_pos": sign_test(wf), "n_debates": len(kap),
        "judge_verdict_toward_winner": {"mean": float(np.mean(jud)), "pos": sign_test(jud), "values": jud}}
    (G.DATA / "results_posthoc.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
