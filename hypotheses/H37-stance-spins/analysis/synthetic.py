"""H37 synthetic validation (axis F): signed-graph swarms with known factions and Jev-like label noise.

Structure is taken from the real reply graphs (who replies to whom how often; teams, roles, days), never from labels.
Stance is simulated by the card's generative model: latent y = mu + a_speaker + b_target + Delta xi_i xi_j + P_ij + eps
(eps logistic), class - / 0 / + by cut points giving base shares (0.04, 0.70, 0.26) (Claude's blind validation
labels), agent fields sd 0.5. Observed label = class passed through a confusion matrix: identity ("perfect") or
Jev's measured matrix (validation/confusion.json, else a placeholder, flagged in the output).

Scenarios
  S1  #12 positive control: real debate-window reply counts and teams. gamma-hat power (within-debate team
      permutation, p < 0.01) and per-debate faction recovery (ground state with team sizes) vs Delta.
  S2  #51 treatment: real #51 selection reply counts and majority roles; OP and SR pairs get a pair term -delta;
      heterogeneity P_ij ~ N(0, 0.3). Power of h22lib.treatment_test (T_OP, T_SR; p_less < 0.05, family-adjusted).
  S3  balance: #51 structure; Mattis factions (Delta xi xi) vs random signs (P_ij ~ N(0, Delta)); tau3(dc) from
      three reply folds; rate of tau3(dc) >= 0.25.
  S4  #26 vote similarity: real #26 counts; pair term Delta (v_ij - mean v); Mantel power.
  S6  detector false alarms (agent fields only; random antagonisms) and camp recovery (Mattis) at each period's
      real reply structure (#12, #26, #40, #51), Jev noise.
  S5  saboteur design (#34 stand-in): #26 per-day counts; each agent-day a saboteur w.p. 1/6; replies TO saboteurs
      shifted by -delta_r (accused), FROM saboteurs by -delta_g; per-day received / given residual score; AUC.

Usage: uv run python hypotheses/H37-stance-spins/analysis/synthetic.py [--reps 200] [--quick]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h37lib as L  # noqa: E402
import h37data as D  # noqa: E402

OUT = D.DATA / "synthetic"
BASE = (0.04, 0.70, 0.26)
C1, C2 = np.log(BASE[0] / (1 - BASE[0])), np.log((BASE[0] + BASE[1]) / (1 - BASE[0] - BASE[1]))
PLACEHOLDER_CONF = np.array([[0.60, 0.35, 0.05], [0.03, 0.85, 0.12], [0.01, 0.30, 0.69]])  # rows true -,0,+; cols obs


def confusion():
    f = D.DATA / "validation/confusion.json"
    if f.exists():
        j = json.loads(f.read_text())
        return np.array(j["P_obs_given_true"]), j.get("source", "measured")
    return PLACEHOLDER_CONF, "placeholder"


def sample_stance(lat, conf, rng):
    u = rng.logistic(size=lat.shape)
    y = lat + u
    cls = np.where(y < C1, 0, np.where(y < C2, 1, 2))
    if conf is None:
        return cls.astype(float) - 1
    cum = np.cumsum(conf[cls], axis=1)
    r = rng.random(len(cls))[:, None]
    obs = (r > cum).sum(1)
    return obs.astype(float) - 1


# ----------------------------------------------------------------------------- S1: #12


def s1_structure():
    P = D.g12_relations(pl.read_parquet(D.DATA / "pairs/G12.parquet").vstack(pl.read_parquet(D.DATA / "pairs/G12_debater.parquet")))
    P = P.filter((pl.col("phase") == "deb") & pl.col("rel").is_in(["same", "opposite"]))
    return P.select("debate", "agent_a", "agent_b", "rel")


class FWProj:
    """Frisch-Waugh projector for speaker/target fixed effects (fixed design)."""

    def __init__(self, spk, tgt, N):
        X = L._design(spk, tgt, N)
        X = X[:, np.abs(X).sum(0) > 0]
        self.Q, _ = np.linalg.qr(X)

    def resid(self, v):
        return v - self.Q @ (self.Q.T @ v)


def s1_run(reps, deltas, conf, rng, nperm=500):
    S = s1_structure()
    teams = D.g12_teams()
    agents = sorted(set(S["agent_a"].to_list()) | set(S["agent_b"].to_list()))
    ix = {a: k for k, a in enumerate(agents)}
    N = len(agents)
    spk = np.array([ix[a] for a in S["agent_b"]]); tgt = np.array([ix[a] for a in S["agent_a"]])
    deb = S["debate"].to_numpy()
    debs = sorted(set(deb.tolist()))
    team_of = {d: {ix[a]: t for a, t in teams[d]["team"].items()} for d in debs}
    xi_i = np.array([team_of[d][i] for d, i in zip(deb, tgt)]); xi_j = np.array([team_of[d][j] for d, j in zip(deb, spk)])
    same = (xi_i == xi_j).astype(float)
    proj = FWProj(spk, tgt, N)
    # permutations: re-draw team labels within each debate (sizes fixed)
    perm_x = []
    prng = np.random.default_rng(7)
    for _ in range(nperm):
        tt = {}
        for d in debs:
            mem = list(team_of[d].keys()); lab = prng.permutation([team_of[d][m] for m in mem])
            tt[d] = dict(zip(mem, lab))
        xi_i_p = np.array([tt[d][i] for d, i in zip(deb, tgt)]); xi_j_p = np.array([tt[d][j] for d, j in zip(deb, spk)])
        perm_x.append(proj.resid((xi_i_p == xi_j_p).astype(float)))
    perm_x = np.array(perm_x)
    xr = proj.resid(same)
    # per-debate recovery setup
    dsets = {}
    for d in debs:
        mem = sorted(team_of[d]); truth = np.array([team_of[d][m] for m in mem])
        k = int((truth == 1).sum())
        dsets[d] = (mem, truth, (k, len(mem) - k), L.chance_accuracy(truth, (k, len(mem) - k)))
    res = {}
    for Delta in deltas:
        for cname, cm in conf.items():
            pw, accs, gam, pacc = [], [], [], []
            for _ in range(reps):
                a = rng.normal(0, 0.5, N); b = rng.normal(0, 0.5, N)
                lat = a[spk] + b[tgt] + Delta * xi_i * xi_j
                s = sample_stance(lat, cm, rng)
                sr = proj.resid(s)
                g = (xr @ sr) / (xr @ xr)
                gp = (perm_x @ sr) / (perm_x * perm_x).sum(1)
                p = (1 + np.sum(gp >= g)) / (1 + nperm)
                gam.append(g); pw.append(p < 0.01)
                r = L.two_way_resid(s, spk, tgt, N)
                acc_d, chance_means = [], []
                for d in debs:
                    m = deb == d
                    mem, truth, sizes, ch = dsets[d]
                    M, C = L.pair_matrix(spk[m], tgt[m], r[m], N)
                    sub = np.nan_to_num(M[np.ix_(mem, mem)])
                    x, _ = L.ground_state(sub, sizes=sizes)
                    acc_d.append(L.partition_accuracy(x, truth))
                acc = np.mean(acc_d)
                # p vs chance: mean of independent draws from each debate's chance distribution
                draws = np.mean([rng.choice(dsets[d][3], 2000) for d in debs], axis=0)
                pacc.append((1 + np.sum(draws >= acc)) / 2001)
                accs.append(acc)
            res[f"Delta={Delta}|{cname}"] = {"power_gamma_p01": float(np.mean(pw)), "gamma_mean": float(np.mean(gam)),
                                             "acc_mean": float(np.mean(accs)), "power_acc_p05": float(np.mean(np.array(pacc) < 0.05)),
                                             "chance_acc": float(np.mean([dsets[d][3].mean() for d in debs]))}
            print("S1", Delta, cname, res[f"Delta={Delta}|{cname}"], flush=True)
    return {"n_replies": int(len(s)), "N": N, "debates": len(debs), "cells": res}


# ----------------------------------------------------------------------------- S2/S3: #51


def s51_structure():
    P = pl.read_parquet(D.DATA / "pairs/G51.parquet").join(pl.read_parquet(D.DATA / "selection/g51_sample.parquet").select("pair_id"),
                                                             on="pair_id", how="semi")
    P = D.g51_roles(P)
    agents = sorted(set(P["agent_a"].to_list()) | set(P["agent_b"].to_list()))
    days = {a: sorted(set(P.filter((pl.col("agent_a") == a) | (pl.col("agent_b") == a))["pt_date"].to_list())) for a in agents}
    roles = D.g51_majority_roles(agents, days)
    return P, agents, roles


def s2_run(reps, deltas, conf, rng, nperm=1000):
    P, agents, roles = s51_structure()
    ix = {a: k for k, a in enumerate(agents)}
    N = len(agents)
    spk = np.array([ix[a] for a in P["agent_b"]]); tgt = np.array([ix[a] for a in P["agent_a"]])
    rlist = sorted({r for r in roles.values() if r})
    role_idx = np.array([rlist.index(roles[a]) if roles[a] else -1 for a in agents])
    lookup = D.RR.lookup_table(rlist)
    C = L.h22lib.class_matrix(role_idx, lookup)
    labs = D.labs(); lab_arr = np.array([labs[a] for a in agents])
    codes = {"SR": 1, "OP": 2, "SY": 3}
    target = (C == 1) | (C == 2)
    res = {}
    for delta in deltas:
        for cname, cm in conf.items():
            pOP, pSR, tOP, tSR = [], [], [], []
            for _ in range(reps):
                a = rng.normal(0, 0.5, N); b = rng.normal(0, 0.5, N)
                Pij = rng.normal(0, 0.3, (N, N)); Pij = (Pij + Pij.T) / 2
                Pij = Pij - delta * target
                lat = a[spk] + b[tgt] + Pij[spk, tgt]
                s = sample_stance(lat, cm, rng)
                J, Cn = L.pair_matrix(spk, tgt, s, N, nmin=3)
                tt = L.h22lib.treatment_test(J, role_idx, lookup, codes, labs=lab_arr, nperm=nperm, rng=rng)["family_adjusted"]
                pOP.append((tt["OP"]["p_less"] or 1) < 0.05); pSR.append((tt["SR"]["p_less"] or 1) < 0.05)
                tOP.append(tt["OP"]["T"]); tSR.append(tt["SR"]["T"])
            res[f"delta={delta}|{cname}"] = {"power_OP": float(np.mean(pOP)), "power_SR": float(np.mean(pSR)),
                                             "T_OP_mean": float(np.nanmean(np.array(tOP, float))), "T_SR_mean": float(np.nanmean(np.array(tSR, float)))}
            print("S2", delta, cname, res[f"delta={delta}|{cname}"], flush=True)
    J, Cn = L.pair_matrix(spk, tgt, np.zeros(len(spk)), N, nmin=3)
    n_pairs = {k: int(np.sum((np.triu(C == v, 1)) & np.isfinite(J))) for k, v in codes.items()}
    return {"N": N, "n_replies": int(len(spk)), "testable_pairs": n_pairs, "cells": res}


def s3_run(reps, deltas, conf, rng):
    P, agents, roles = s51_structure()
    ix = {a: k for k, a in enumerate(agents)}
    N = len(agents)
    spk = np.array([ix[a] for a in P["agent_b"]]); tgt = np.array([ix[a] for a in P["agent_a"]])
    # conversation-block folds: B's 10-min block, blocks assigned to folds at random
    blk = (P["t_b"].dt.epoch("s").to_numpy() // 600)
    res = {}
    for Delta in deltas:
        for model in ("mattis", "random"):
            for cname, cm in conf.items():
                t3, t3dc = [], []
                for _ in range(reps):
                    a = rng.normal(0, 0.5, N); b = rng.normal(0, 0.5, N)
                    if model == "mattis":
                        xi = rng.permutation(np.r_[np.ones(N // 2), -np.ones(N - N // 2)])
                        Pij = Delta * np.outer(xi, xi)
                    else:
                        Pij = rng.normal(0, Delta, (N, N)); Pij = (Pij + Pij.T) / 2 * np.sqrt(2)
                    lat = a[spk] + b[tgt] + Pij[spk, tgt]
                    s = sample_stance(lat, cm, rng)
                    ub, inv = np.unique(blk, return_inverse=True)
                    fold = rng.integers(3, size=len(ub))[inv]
                    t, tdc = L.tau3_folds(spk, tgt, s, N, fold, resid=True, nmin=1)
                    t3.append(t); t3dc.append(tdc)
                t3dc = np.array(t3dc, float)
                res[f"Delta={Delta}|{model}|{cname}"] = {"tau3dc_median": float(np.nanmedian(t3dc)),
                                                          "rate_tau3dc_ge_025": float(np.nanmean(t3dc >= 0.25)),
                                                          "tau3_median": float(np.nanmedian(np.array(t3, float)))}
                print("S3", Delta, model, cname, res[f"Delta={Delta}|{model}|{cname}"], flush=True)
    return {"N": N, "cells": res}


# ----------------------------------------------------------------------------- S4/S5: #26 structure


def s26_structure():
    P = pl.read_parquet(D.DATA / "pairs/G26.parquet")
    agents = sorted(set(P["agent_a"].to_list()) | set(P["agent_b"].to_list()))
    return P, agents


def vote_similarity(agents):
    v = D.g26_votes()
    sets = {a: set() for a in agents}
    for a, named in zip(v["agent"].to_list(), v["named"].to_list()):
        if a in sets:
            sets[a] |= set(named)
    N = len(agents)
    V = np.full((N, N), np.nan)
    for i, a in enumerate(agents):
        for j, b in enumerate(agents):
            if i != j and sets[a] and sets[b]:
                V[i, j] = len(sets[a] & sets[b]) / len(sets[a] | sets[b])
    return V, sets


def s4_run(reps, deltas, conf, rng):
    P, agents = s26_structure()
    ix = {a: k for k, a in enumerate(agents)}
    N = len(agents)
    spk = np.array([ix[a] for a in P["agent_b"]]); tgt = np.array([ix[a] for a in P["agent_a"]])
    V, _ = vote_similarity(agents)
    Vc = np.nan_to_num(V - np.nanmean(V))
    res = {}
    for Delta in deltas:
        for cname, cm in conf.items():
            pw, rs = [], []
            for _ in range(reps):
                a = rng.normal(0, 0.5, N); b = rng.normal(0, 0.5, N)
                lat = a[spk] + b[tgt] + Delta * Vc[spk, tgt]
                s = sample_stance(lat, cm, rng)
                J, _ = L.residual_matrix(spk, tgt, s, N, nmin=3)
                m = L.mantel(J, V, nperm=500, rng=rng)
                pw.append(m.get("p_greater", 1) < 0.05); rs.append(m["r"])
            res[f"Delta={Delta}|{cname}"] = {"power_mantel": float(np.mean(pw)), "r_mean": float(np.nanmean(rs))}
            print("S4", Delta, cname, res[f"Delta={Delta}|{cname}"], flush=True)
    return {"N": N, "n_voters_with_sets": int(np.isfinite(V).any(1).sum()), "cells": res}


def s5_run(reps, deltas, conf, rng):
    P, agents = s26_structure()
    ix = {a: k for k, a in enumerate(agents)}
    N = len(agents)
    spk = np.array([ix[a] for a in P["agent_b"]]); tgt = np.array([ix[a] for a in P["agent_a"]])
    days = P["pt_date"].to_list(); ud = sorted(set(days)); di = np.array([ud.index(d) for d in days])
    res = {}
    for (dr, dg) in deltas:
        for cname, cm in conf.items():
            aucs_r, aucs_g, aucs_c = [], [], []
            for _ in range(reps):
                a = rng.normal(0, 0.5, N); b = rng.normal(0, 0.5, N)
                sab = rng.random((len(ud), N)) < 1 / 6
                lat = a[spk] + b[tgt] - dr * sab[di, tgt] - dg * sab[di, spk]
                s = sample_stance(lat, cm, rng)
                pos_r, neg_r, pos_g, neg_g, pos_c, neg_c = [], [], [], [], [], []
                for d in range(len(ud)):
                    m = di == d
                    sc = L.agent_scores(spk[m], tgt[m], s[m], N)
                    for i in range(N):
                        zr, zg = -sc["z_received"][i], -sc["z_given"][i]
                        zc = np.nanmean([zr, zg]) if np.isfinite(zr) or np.isfinite(zg) else np.nan
                        (pos_r if sab[d, i] else neg_r).append(zr)
                        (pos_g if sab[d, i] else neg_g).append(zg)
                        (pos_c if sab[d, i] else neg_c).append(zc)
                aucs_r.append(L.auc(pos_r, neg_r)); aucs_g.append(L.auc(pos_g, neg_g)); aucs_c.append(L.auc(pos_c, neg_c))
            res[f"dr={dr},dg={dg}|{cname}"] = {"auc_received": float(np.nanmean(aucs_r)), "auc_given": float(np.nanmean(aucs_g)),
                                               "auc_combined": float(np.nanmean(aucs_c)),
                                               "auc_combined_q05": float(np.nanquantile(aucs_c, 0.05))}
            print("S5", dr, dg, cname, res[f"dr={dr},dg={dg}|{cname}"], flush=True)
    return {"N": N, "days": len(ud), "cells": res}


# ----------------------------------------------------------------------------- S6: detector false alarms and camp recovery


def s6_structure(name):
    if name == "51":
        P, agents, _ = s51_structure()
    else:
        P = pl.read_parquet(D.DATA / f"pairs/G{name}.parquet")
        if name == "12":
            P = P.vstack(pl.read_parquet(D.DATA / "pairs/G12_debater.parquet"))
        agents = sorted(set(P["agent_a"].to_list()) | set(P["agent_b"].to_list()))
    return P, agents


def s6_run(reps, conf, rng):
    """O6 detector on simulated stance at each period's real reply structure (Jev noise only).

    Cells: 'fields' (agent fields only), 'random' (plus random pair affinities sd 0.5: antagonisms without camps),
    'mattis0.5' / 'mattis1.0' (two random balanced camps, +-Delta). Reported: rate of faction p < 0.05 (residual J),
    rate of >= 1 significantly negative pair (FDR 0.1), camp-recovery accuracy for Mattis."""
    res = {}
    for name in ("12", "26", "40", "51"):
        P, agents = s6_structure(name)
        ix = {a: k for k, a in enumerate(agents)}
        N = len(agents)
        spk = np.array([ix[a] for a in P["agent_b"]]); tgt = np.array([ix[a] for a in P["agent_a"]])
        restarts = 40 if N > 22 else 300
        nnull = 40 if N > 22 else 100
        for cell in ("fields", "random", "mattis0.5", "mattis1.0"):
            fa, sg, acc = [], [], []
            for _ in range(reps):
                a = rng.normal(0, 0.5, N); b = rng.normal(0, 0.5, N)
                Pij = np.zeros((N, N)); xi = None
                if cell == "random":
                    Pij = rng.normal(0, 0.5, (N, N)); Pij = (Pij + Pij.T) / np.sqrt(2)
                elif cell.startswith("mattis"):
                    xi = rng.permutation(np.r_[np.ones(N // 2), -np.ones(N - N // 2)])
                    Pij = float(cell[6:]) * np.outer(xi, xi)
                s = sample_stance(a[spk] + b[tgt] + Pij[spk, tgt], conf["jev"], rng)
                Jr, C = L.residual_matrix(spk, tgt, s, N, nmin=3)
                fr = L.faction_score(Jr, nnull=nnull, rng=rng, restarts=restarts)
                fa.append(fr.get("p_factional", 1) < 0.05)
                sig, _ = L.significant_negative_pairs(spk, tgt, s, N, nmin=3, q=0.1)
                sg.append(len(sig) >= 1)
                if xi is not None:
                    x, _ = L.ground_state(Jr, rng=rng, restarts=restarts)
                    keep = (C >= 3).sum(1) > 0
                    acc.append(L.partition_accuracy(x[keep], xi[keep]))
            res[f"{name}|{cell}"] = {"N": N, "rate_faction_p05": float(np.mean(fa)), "rate_any_sig_neg_pair": float(np.mean(sg)),
                                     "camp_accuracy": float(np.mean(acc)) if acc else None}
            print("S6", name, cell, res[f"{name}|{cell}"], flush=True)
    return {"cells": res}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    rng = np.random.default_rng(20261004)
    cm, src = confusion()
    conf = {"perfect": None, "jev": cm}
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / "results.json"
    R = json.loads(f.read_text()) if f.exists() else {}
    R["confusion_source"] = src
    R["confusion"] = cm.tolist()
    t0 = time.time()
    jobs = {"S1": lambda: s1_run(a.reps, [0.0, 0.25, 0.5, 1.0], conf, rng),
            "S2": lambda: s2_run(max(50, a.reps // 2), [0.0, 0.5, 1.0, 2.0], conf, rng),
            "S3": lambda: s3_run(max(50, a.reps // 2), [0.5, 1.0, 2.0], conf, rng),
            "S4": lambda: s4_run(max(50, a.reps // 2), [0.0, 1.0, 2.0, 4.0], conf, rng),
            "S5": lambda: s5_run(max(50, a.reps // 2), [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (2.0, 2.0)], conf, rng),
            "S6": lambda: s6_run(max(40, a.reps // 5), conf, rng)}
    for k, fn in jobs.items():
        if a.only and k not in a.only:
            continue
        R[k] = fn()
        R[k]["elapsed_s"] = round(time.time() - t0, 1)
        f.write_text(json.dumps(R, indent=1))
    D.record("synthetic", "hypotheses/H37-stance-spins/analysis/synthetic.py", {"reps": a.reps, "only": a.only, "confusion": src},
             ["H37 pairs (structure only)", "validation/confusion.json"])
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
