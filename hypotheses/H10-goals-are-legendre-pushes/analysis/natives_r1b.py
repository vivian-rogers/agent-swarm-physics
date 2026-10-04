"""H10 round 1b period-native tests (predictions in goalperiod-subhypotheses/{G44,NE38,G26}/README.md, written before
this script ran on real data). Non-holdout only (h10data.guard); #23 untouched; nothing along g_32 is computed.

  G44   assigned (#best) vs self-chosen (#rest) room, #42 -> #44 days 2+, each room along its own kickoff direction
  NE38  Claude Opus 5's private goal reassigned 07-29: single-agent tilt check along its new goal, with controls
  G26   the elected leader's goal announcement as an agent-set field, #25 -> #26 (01-06 .. 01-08)

Outputs data/processed/H10-goals-are-legendre-pushes/r1b/<tag>/natives.json (tag = embedding / goals / dedupe config).
Usage: uv run python natives_r1b.py --emb bge_small [--dedupe restate]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h10data as HD  # noqa: E402
from h10lib import (agent_stats, aggregate, analyze_pair, perm_p_r, proj_stats, random_transverse)  # noqa: E402

SEED = 20261004
R1B = HD.R1B


def unit(x):
    x = np.asarray(x, np.float64)
    return x / np.linalg.norm(x)


def whiten_unit(raw, regime, n=32):
    return unit(HD._whitener(regime, n)(np.asarray(raw, np.float32)[None])[0])


def room_vec(goal_no, kind, room=None, agent=None):
    meta = pl.read_parquet(R1B / "goal_rooms.parquet")
    V = np.load(R1B / f"goal_rooms_{HD.CFG['emb']}.npy")
    q = meta.filter((pl.col("goal_no") == goal_no) & (pl.col("kind") == kind))
    if room is not None:
        q = q.filter(pl.col("room") == room)
    if agent is not None:
        q = q.filter(pl.col("agent") == agent)
    assert q.height == 1, (goal_no, kind, room, agent, q.height)
    return V[q["i"][0]].astype(np.float32)


def goal_kick(goal_no):
    gz = np.load(R1B / f"goal_vecs_{HD.CFG['emb']}.npz")
    i = int(np.flatnonzero(gz["goal_no"] == goal_no)[0])
    return gz["goal_raw"][i], gz["kick_raw"][i]


def seg_of(P, U, agents=None, meta=None):
    sel = np.ones(len(P["agent"]), bool) if agents is None else np.isin(P["agent"], list(agents))
    return aggregate(P["Z"][sel], P["agent"][sel], P["day"][sel], P["win"][sel], U, meta=meta)


def weights_from_days(seg, pick):
    cnt = {d: 0 for d in np.unique(seg.day)}
    for d in pick:
        cnt[d] = cnt.get(d, 0) + 1
    return np.array([cnt.get(d, 0) for d in seg.day], float)


def dbar_w(F, A, wF, wA):
    sF, sA = agent_stats(F, w=wF), agent_stats(A, w=wA)
    com = np.intersect1d(sF.agents, sA.agents)
    if len(com) < 2:
        return np.nan
    return float((sA.mu[np.searchsorted(sA.agents, com), 0] - sF.mu[np.searchsorted(sF.agents, com), 0]).mean())


def brief(r):
    keys = ("N", "Dbar", "Dbar_ci90", "lam", "eps", "P1_r", "P1_p", "P2_rho_gauss", "P2_rho_perp", "R2_slope_muF",
            "P1_mse_tilt", "P1_mse_trans", "gF", "gA", "agents", "P1_D", "P1_k2F")
    return {k: r.get(k) for k in keys}


# ------------------------------------------------------------------------------------------------------------- G44
def g44(rng, n_boot=1000):
    reg = "III"
    gt = pl.read_parquet(HD.SH / "ground_truth_labels.parquet")
    ra = gt.filter((pl.col("goal_no") == 44) & (pl.col("label_kind") == "room_assignment"))
    rooms = {"best": set(ra.filter(pl.col("value") == "best")["agent"].to_list()),
             "rest": set(ra.filter(pl.col("value") == "rest")["agent"].to_list())}
    gnum = {"best": 2, "rest": 3}
    goal_raw, _ = goal_kick(44)
    dirs = {r: whiten_unit(room_vec(44, "kickoff_room", room=gnum[r]), reg) for r in rooms}
    dirs_comb = {r: unit(dirs[r] + whiten_unit(goal_raw, reg)) for r in rooms}
    PF = HD.load_period(42)
    PA = HD.load_period(44, days=("2026-05-27", "2026-05-29"))
    out = {"rooms": {r: sorted(int(a) for a in v) for r, v in rooms.items()},
           "cos_best_rest_dirs": float(dirs["best"] @ dirs["rest"]), "F_days": PF["days"], "A_days": PA["days"]}
    segs = {}
    for variant, D in (("kickoff_room", dirs), ("goal+kickoff_room", dirs_comb)):
        res = {}
        for r in rooms:
            for along in rooms:
                U = random_transverse(D[along], 50, np.random.default_rng(0))
                F, A = seg_of(PF, U, rooms[r]), seg_of(PA, U, rooms[r])
                segs[(variant, r, along)] = (F, A)
                rr = analyze_pair(F, A, rng, n_boot=n_boot if r == along else 300, n_rot=0, with_p4=False)
                res[f"{r}_along_{along}"] = brief(rr)
        # N1b: room difference along g_best, with jointly resampled days
        Fb, Ab = segs[(variant, "best", "best")]; Fr, Ar = segs[(variant, "rest", "best")]
        dF, dA = np.unique(np.r_[Fb.day, Fr.day]), np.unique(np.r_[Ab.day, Ar.day])
        diffs = []
        for _ in range(n_boot):
            pf, pa = rng.choice(dF, len(dF)), rng.choice(dA, len(dA))
            diffs.append(dbar_w(Fb, Ab, weights_from_days(Fb, pf), weights_from_days(Ab, pa))
                         - dbar_w(Fr, Ar, weights_from_days(Fr, pf), weights_from_days(Ar, pa)))
        diffs = np.array(diffs, float)
        obs = res["best_along_best"]["Dbar"] - res["rest_along_best"]["Dbar"]
        res["N1b_diff"] = {"obs": obs, "ci90": [float(np.nanquantile(diffs, 0.05)), float(np.nanquantile(diffs, 0.95))]}
        out[variant] = res
    p = out["kickoff_room"]
    b, r_ = p["best_along_best"], p["rest_along_rest"]
    ln15 = float(np.log(1.5))
    out["N1a"] = bool(b["Dbar"] > 0 and b["Dbar_ci90"][0] > 0 and b["eps"] > 1)
    out["N1b"] = bool(p["N1b_diff"]["ci90"][0] > 0)
    out["N1c_rest"] = bool(abs(r_["P2_rho_gauss"] - r_["P2_rho_perp"]) < ln15)
    out["N1c_best"] = bool(b["P2_rho_gauss"] > ln15 and abs(b["P2_rho_perp"]) < ln15)
    out["verdict"] = ("supported" if out["N1a"] and out["N1b"] and out["N1c_rest"] else
                      "failed" if (not out["N1a"]) or p["N1b_diff"]["obs"] <= 0 else "mixed")
    return out


# ------------------------------------------------------------------------------------------------------------- NE38
def single_agent(P, agent, U):
    sel = P["agent"] == agent
    return aggregate(P["Z"][sel], P["agent"][sel], P["day"][sel], P["win"][sel], U)


def tilt_check(F, A):
    """Exponential reweighting of F's windows (along U[:,0]) matched to A's mean; noise-corrected variances."""
    xF, s2F, _ = proj_stats(F); xA, s2A, _ = proj_stats(A)
    nF, nA = s2F[:, 0] / F.c, s2A[:, 0] / A.c
    x, y = xF[:, 0], xA[:, 0]
    k2F = x.var(ddof=1) - nF.mean(); k2A = y.var(ddof=1) - nA.mean()
    target = y.mean()
    out = {"mean_F": float(x.mean()), "mean_A": float(target), "max_F": float(x.max()), "q90_F": float(np.quantile(x, 0.9)),
           "k2F": float(k2F), "k2A": float(k2A), "reachable": bool(target < x.max())}
    if not out["reachable"]:
        return out
    lo, hi = -1e4, 1e4
    for _ in range(200):
        lam = 0.5 * (lo + hi)
        w = np.exp(lam * (x - x.max())); w /= w.sum()
        if (w * x).sum() < target:
            lo = lam
        else:
            hi = lam
    w = np.exp(lam * (x - x.max())); w /= w.sum()
    m = (w * x).sum()
    vt = (w * (x - m) ** 2).sum() - (w * nF).sum()
    out.update(lam=float(lam), k2_tilt=float(vt), ess=float(1 / (w ** 2).sum()),
               rho_obs=float(np.log(k2A / k2F)) if k2A > 0 and k2F > 0 else None,
               rho_tilt=float(np.log(vt / k2F)) if vt > 0 and k2F > 0 else None)
    return out


def ne38(rng, n_boot=1000):
    reg = "III"
    a0 = 40
    g_new = whiten_unit(room_vec(51, "agent_goal", agent=a0), reg)
    U = random_transverse(g_new, 50, np.random.default_rng(0))
    PF = HD.load_period(51, days=("2026-07-24", "2026-07-28"))
    PA = HD.load_period(51, days=("2026-07-30", "2026-08-04"))
    F, A = single_agent(PF, a0, U), single_agent(PA, a0, U)
    sF, sA = agent_stats(F), agent_stats(A)
    out = {"F_days": PF["days"], "A_days": PA["days"], "n_win_F": int(len(F.c)), "n_win_A": int(len(A.c))}
    if len(sF.agents) == 0 or len(sA.agents) == 0:
        out["error"] = "too few windows"
        return out
    D = float(sA.mu[0, 0] - sF.mu[0, 0])
    eps = D / np.sqrt(max(sF.k2[0, 0], 1e-12))
    rho = float(np.log(sA.k2[0, 0] / sF.k2[0, 0])) if sA.k2[0, 0] > 0 and sF.k2[0, 0] > 0 else None
    rp = [np.log(sA.k2[0, k] / sF.k2[0, k]) for k in range(1, U.shape[1]) if sA.k2[0, k] > 0 and sF.k2[0, k] > 0]
    out.update(D=D, eps=float(eps), rho=rho, rho_perp=float(np.median(rp)), k2F=float(sF.k2[0, 0]), k2A=float(sA.k2[0, 0]),
               muF=float(sF.mu[0, 0]), muA=float(sA.mu[0, 0]))
    out["tilt"] = tilt_check(F, A)
    # day-block bootstrap for D, eps, rho
    bs = {"D": [], "eps": [], "rho": []}
    dF, dA = np.unique(F.day), np.unique(A.day)
    for _ in range(n_boot):
        wF = weights_from_days(F, rng.choice(dF, len(dF))); wA = weights_from_days(A, rng.choice(dA, len(dA)))
        bF, bA = agent_stats(F, w=wF, min_win=3), agent_stats(A, w=wA, min_win=3)
        if len(bF.agents) == 0 or len(bA.agents) == 0:
            continue
        d = bA.mu[0, 0] - bF.mu[0, 0]
        bs["D"].append(d); bs["eps"].append(d / np.sqrt(max(bF.k2[0, 0], 1e-12)))
        bs["rho"].append(np.log(bA.k2[0, 0] / bF.k2[0, 0]) if bA.k2[0, 0] > 0 and bF.k2[0, 0] > 0 else np.nan)
    for k, v in bs.items():
        v = np.array(v, float)
        out[f"{k}_ci90"] = [float(np.nanquantile(v, 0.05)), float(np.nanquantile(v, 0.95))]
    # controls (i): every other agent along g_new, same dates
    Fo = aggregate(PF["Z"][PF["agent"] != a0], PF["agent"][PF["agent"] != a0], PF["day"][PF["agent"] != a0],
                   PF["win"][PF["agent"] != a0], U)
    Ao = aggregate(PA["Z"][PA["agent"] != a0], PA["agent"][PA["agent"] != a0], PA["day"][PA["agent"] != a0],
                   PA["win"][PA["agent"] != a0], U)
    so, sa = agent_stats(Fo), agent_stats(Ao)
    com = np.intersect1d(so.agents, sa.agents)
    dj = sa.mu[np.searchsorted(sa.agents, com), 0] - so.mu[np.searchsorted(so.agents, com), 0]
    out["controls_other_agents"] = {"n": int(len(com)), "mean_D": float(dj.mean()), "ratio_to_opus5": float(dj.mean() / D),
                                    "max_abs_D": float(np.abs(dj).max())}
    # controls (ii): the two incumbent game developers, each along its own unchanged goal
    inc = {}
    for a in (24, 26):
        gi = whiten_unit(room_vec(51, "agent_goal", agent=a), reg)
        Ui = random_transverse(gi, 10, np.random.default_rng(0))
        Fi, Ai = single_agent(PF, a, Ui), single_agent(PA, a, Ui)
        si, ti = agent_stats(Fi), agent_stats(Ai)
        if len(si.agents) and len(ti.agents):
            d = float(ti.mu[0, 0] - si.mu[0, 0])
            inc[str(a)] = {"D": d, "eps": d / np.sqrt(max(si.k2[0, 0], 1e-12)), "cos_goal_with_opus5_new": float(gi @ g_new)}
    out["controls_incumbents"] = inc
    t = out["tilt"]
    ln15 = float(np.log(1.5))
    out["N2a"] = bool(eps > 2 and out["muA"] > t["q90_F"])
    out["N2b"] = bool((not t["reachable"]) or (t.get("rho_obs") is not None and t.get("rho_tilt") is not None
                                               and t["rho_obs"] - t["rho_tilt"] > ln15))
    out["N2c"] = bool(abs(out["controls_other_agents"]["ratio_to_opus5"]) < 0.25
                      and all(abs(v["eps"]) < 1 for v in inc.values()))
    tilt_ok = bool(t["reachable"] and t.get("rho_obs") is not None and t.get("rho_tilt") is not None
                   and abs(t["rho_obs"] - t["rho_tilt"]) < ln15)
    out["verdict"] = ("failed" if out["N2a"] and out["N2b"] and out["N2c"] else
                      "supported" if tilt_ok and out["N2c"] else "mixed")
    return out


# ------------------------------------------------------------------------------------------------------------- G26
def g26(rng, n_boot=1000):
    reg = "I"
    info = json.loads((HD.ROOT / "data/processed/H54-kickoff-quench-target/g26_leader.json").read_text())
    ci = pl.read_parquet(HD.SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    src = int(ci.filter(pl.col("message_id") == info["message_id"])["src_row"][0])
    sfx = HD.CFG["emb"]
    Ec = np.load(HD.SH / f"embeddings/chat_{sfx}.npy", mmap_mode="r")
    e_L = whiten_unit(Ec[src], reg)
    graw, kraw = goal_kick(26)
    g_kick = whiten_unit(kraw, reg)
    g_comb = unit(whiten_unit(graw, reg) + g_kick)
    PF = HD.load_period(25)
    PA = HD.load_period(26, days=("2026-01-06", "2026-01-08"))
    leader = int(info["agent"])
    agents = sorted(set(PF["agent"].tolist()) - {leader})
    out = {"leader": leader, "F_days": PF["days"], "A_days": PA["days"], "cos_eL_kickoff": float(e_L @ g_kick)}
    for name, d in (("leader_announcement", e_L), ("operator_kickoff", g_kick), ("operator_goal+kickoff", g_comb)):
        U = random_transverse(d, 50, np.random.default_rng(0))
        r = analyze_pair(seg_of(PF, U, agents), seg_of(PA, U, agents), rng, n_boot=n_boot, n_rot=0, with_p4=False)
        out[name] = brief(r)
    L = out["leader_announcement"]
    out["N3a"] = bool(L["eps"] < 1)
    out["N3b"] = bool(L["P1_r"] <= 0)
    out["verdict"] = ("failed" if out["N3b"] and L["eps"] > 0.34 else
                      "supported" if (L["P1_r"] > 0 and L["P1_p"] < 0.05) else "mixed")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emb", default="bge_small", choices=["bge_small", "gte_modernbert"])
    ap.add_argument("--dedupe", default="none", choices=["none", "copies", "restate"])
    ap.add_argument("--only", default="g44,ne38,g26")
    args = ap.parse_args()
    HD.configure(args.emb, "shared", args.dedupe, False)
    out_dir = HD.out_root()
    out_dir.mkdir(parents=True, exist_ok=True)
    f = out_dir / "natives.json"
    res = json.loads(f.read_text()) if f.exists() else {}
    res["config"] = HD.cfg_tag()
    rng = np.random.default_rng(SEED)
    for name, fn in (("G44", g44), ("NE38", ne38), ("G26", g26)):
        if name.lower() in args.only:
            res[name] = fn(rng)
            print(name, json.dumps({k: v for k, v in res[name].items() if k in ("verdict", "N1a", "N1b", "N1c_rest", "N1c_best",
                                                                               "N2a", "N2b", "N2c", "N3a", "N3b", "D", "eps",
                                                                               "rho", "rho_perp")}, default=float), flush=True)
    HD.save_json(res, f)


if __name__ == "__main__":
    main()
