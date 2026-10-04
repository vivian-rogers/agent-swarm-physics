"""H115 G12 unblinding: score the frozen rankings against DQ6 judges and teams; P1, P1b, P1c, P2, P3, N2.

  uv run python hypotheses/H115-debate-judge-role-recovery/analysis/run_g12_unblind.py [--perm 200] [--skel 200]

Refuses to run unless G12/frozen_ranking.json matches the SHA-256 recorded in G12/frozen_ranking.sha256 (and the card).
Writes data/processed/H115-debate-judge-role-recovery/G12/results.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h115lib as L  # noqa: E402

CS = L.CS
D12 = L.DATA / "G12"
A1 = json.loads((L.DATA / "synthetic" / "amendment_A1.json").read_text())
LAM = float(A1["lambda"])
JSELF = 0.3


def check_hash():
    blob = (D12 / "frozen_ranking.json").read_bytes()
    h = hashlib.sha256(blob).hexdigest()
    if h != (D12 / "frozen_ranking.sha256").read_text().strip():
        raise SystemExit("frozen ranking hash mismatch; refusing")
    return json.loads(blob), h


def labels():
    g = (pl.scan_parquet(CS.SH / "ground_truth_labels.parquet")
         .filter((pl.col("goal_no") == 12) & pl.col("preferred") & ~pl.col("holdout")
                 & pl.col("label_kind").is_in(["judge", "team", "debate_result"])).collect())
    lab = {}
    for row in g.iter_rows(named=True):
        d = lab.setdefault(row["unit"], {"judge": None, "gov": [], "opp": [], "bench": [], "result": None})
        if row["label_kind"] == "judge":
            d["judge"] = int(row["agent"])
        elif row["label_kind"] == "team":
            v = str(row["value"]).lower()
            key = "gov" if v.startswith("gov") else ("opp" if v.startswith("opp") else "bench")
            d[key].append(int(row["agent"]))
        elif row["label_kind"] == "debate_result":
            d["result"] = row["value"]
    return lab, sorted(g["value"].unique().to_list())


def uniform_null(ns, R=200000, seed=1):
    rng = np.random.default_rng(seed)
    r = np.column_stack([rng.integers(1, n + 1, R) for n in ns])
    u = (r - 1) / (np.array(ns) - 1)
    return np.median(r, 1), (r == 1).sum(1), u.mean(1)


# ---------------------------------------------------------------- field-only skeleton null (N2)
_S = {}


def _skel_init():
    calls, XR, XP, agents = L.load("G12")
    s = calls["s"].to_numpy()
    a = calls["agent"].to_numpy()
    md = calls["mode"].to_numpy()
    win = np.array([w if w is not None else "none" for w in calls["win"].to_list()])
    ph = np.array([p if p is not None else "none" for p in calls["phase"].to_list()])
    h = np.zeros(calls.height)
    # real talk rate per agent x window x phase x mode (outside windows: agent x mode), add-one smoothed
    keys = np.char.add(np.char.add(np.char.add(a.astype(str), "|"), np.char.add(win, "|")),
                       np.char.add(ph, np.char.add("|", md.astype(str))))
    for k in np.unique(keys):
        sel = keys == k
        p = ((s[sel] > 0).sum() + 0.5) / (sel.sum() + 1.0)
        h[sel] = 0.5 * np.log(p / (1 - p))
    _S.update(calls=calls, agents=agents, h=h, win=win, ph=ph)


def skel_world(seed):
    if not _S:
        _skel_init()
    calls, agents, h = _S["calls"], _S["agents"], _S["h"]
    A = len(agents)
    Z = np.zeros((A, A))
    s, XRs, XPs = CS.simulate(calls, agents, h, lambda k: Z, np.zeros(A), seed=seed)
    out = {}
    trim = calls["trim"].to_numpy()
    for w in sorted(set(_S["win"]) - {"none"}):
        m = (_S["win"] == w) & trim
        cw = calls.filter(pl.Series(m))
        pres = L.present_agents(cw)
        f = L.fit_additive(cw, XRs[m], XPs[m], agents, pres, LAM, phase=_S["ph"][m], s_override=s[m])
        out[w] = {"pres": pres, "S": f["S"].tolist(), "SP": f["SP"].tolist()}
    return out


def judge_stats(rank_by_deb, lab, wins, key="rank"):
    rs, ns, us = [], [], []
    for w in wins:
        r = rank_by_deb[w]
        if r is None or lab[w]["judge"] not in r["pres"]:
            continue
        q = r["pres"].index(lab[w]["judge"])
        n = len(r["pres"])
        rs.append(int(r[key][q]))
        ns.append(n)
        us.append((r[key][q] - 1) / (n - 1))
    return rs, ns, us


def pairtype_windows(calls, XR, XP, agents, lab, wins, perm_rng=None):
    W = []
    trim = calls["trim"].to_numpy()
    for k, w in enumerate(wins):
        m = (calls["win"] == w).fill_null(False).to_numpy() & trim
        cw = calls.filter(pl.Series(m))
        pres = L.present_agents(cw)
        gov, opp = list(lab[w]["gov"]), list(lab[w]["opp"])
        if perm_rng is not None:
            deb = [q for q in gov + opp if q in pres]
            perm = list(perm_rng.permutation(deb))
            ng = sum(q in pres for q in gov)
            gov, opp = perm[:ng], perm[ng:]
        ph = np.array([p if p is not None else "none" for p in cw["phase"].to_list()])
        W.append({"calls": cw, "XR": XR[m], "XP": XP[m], "pres": pres, "judge": lab[w]["judge"], "gov": gov,
                  "opp": opp, "phase": ph, "wid": k})
    return W


_P = {}


def perm_job(seed):
    if not _P:
        calls, XR, XP, agents = L.load("G12")
        lab, _ = labels()
        _P.update(calls=calls, XR=XR, XP=XP, agents=agents, lab=lab,
                  wins=sorted(w for w in calls["win"].unique().to_list() if w is not None))
    rng = np.random.default_rng(seed)
    W = pairtype_windows(_P["calls"], _P["XR"], _P["XP"], _P["agents"], _P["lab"], _P["wins"], perm_rng=rng)
    f = L.fit_pairtype(W, _P["agents"], LAM, se=False)
    return f["coef"]["R_ST_all"] - f["coef"]["R_OT_all"]


def verdict_step(calls, lab, wins, rng=None, n_draw=0):
    """Debaters' talk step at the verdict (post vs deb) with agent x debate x mode intercepts; placebo splits in deb."""
    trim = calls["trim"].to_numpy()

    def fit(rows_list):
        Xs, ys = [], []
        keys = sorted({k for (_, _, kk) in rows_list for k in kk})
        kid = {k: q for q, k in enumerate(keys)}
        for (after, y, kk) in rows_list:
            I = np.zeros((len(y), len(keys)))
            I[np.arange(len(y)), [kid[k] for k in kk]] = 1
            Xs.append(np.column_stack([I, after]))
            ys.append(y)
        X = np.vstack(Xs)
        y = np.concatenate(ys)
        lam = np.r_[np.full(len(keys), L.LAM_INT), 0.1]
        b, _ = CS.fit_logit(X, y, lam)
        return b[-1] / 2

    def rows(placebo_rng=None):
        out = []
        for w in wins:
            m = (calls["win"] == w).fill_null(False).to_numpy() & trim
            cw = calls.filter(pl.Series(m))
            deb = set(lab[w]["gov"]) | set(lab[w]["opp"])
            a = cw["agent"].to_numpy()
            ph = np.array([p if p is not None else "none" for p in cw["phase"].to_list()])
            sel = np.isin(a, list(deb))
            if placebo_rng is None:
                sel &= np.isin(ph, ["deb", "post"])
                after = (ph == "post").astype(float)
            else:
                sel &= ph == "deb"
                t = cw["t_call"].dt.epoch("s").to_numpy()
                if sel.sum() < 4:
                    continue
                lo, hi = t[sel].min(), t[sel].max()
                cut = lo + placebo_rng.uniform(0.25, 0.75) * (hi - lo)
                after = (t >= cut).astype(float)
            y = (cw["s"].to_numpy() > 0).astype(float)
            kk = [f"{w}|{aa}|{mm}" for aa, mm in zip(a, cw["mode"].to_numpy())]
            idx = np.where(sel)[0]
            out.append((after[idx], y[idx], [kk[i] for i in idx]))
        return out

    obs = fit(rows())
    pl_ = [fit(rows(rng)) for _ in range(n_draw)] if rng is not None else []
    return obs, pl_


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--skel", type=int, default=200)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    fr, h = check_hash()
    lab, team_values = labels()
    calls, XR, XP, agents = L.load("G12")
    wins = sorted(fr["debates"])
    res = {"hash": h, "lambda": LAM, "team_label_values": team_values, "labels": lab}
    # ---------------- P1 (primary) and variants
    prim = {w: fr["debates"][w]["primary"] for w in wins}
    rs, ns, us = judge_stats(prim, lab, wins)
    rsP, _, usP = judge_stats(prim, lab, wins, key="rankP")
    med0, n10, u0 = uniform_null(ns)
    obs_med, obs_n1, obs_u = float(np.median(rs)), int(sum(r == 1 for r in rs)), float(np.mean(us))
    res["P1"] = {"judge_ranks": rs, "n_present": ns, "median_rank": obs_med, "n_rank1": obs_n1, "mean_u": obs_u,
                 "p_uniform_mean_u": float((u0 <= obs_u).mean()),
                 "p_uniform_support_rule": float(((med0 <= 2) & (n10 >= 4)).mean()),
                 "p_uniform_n1": float((n10 >= obs_n1).mean()),
                 "support": bool(obs_med <= 2 and obs_n1 >= 4), "kill": bool(obs_med >= 4),
                 "p_uniform_mean_u_bottom": float((u0 >= obs_u).mean())}
    res["P1c"] = {"judge_ranks_inflight": rsP, "mean_u_inflight": float(np.mean(usP)), "mean_u_read": obs_u,
                  "mean_rank_read": float(np.mean(rs)), "mean_rank_inflight": float(np.mean(rsP))}
    var = {}
    for v in ("fullJ", "chatclock", "untrimmed"):
        rr = {w: fr["debates"][w][v] for w in wins}
        r_, n_, u_ = judge_stats(rr, lab, wins)
        var[v] = {"judge_ranks": r_, "median_rank": float(np.median(r_)), "n_rank1": int(sum(x == 1 for x in r_)),
                  "mean_u": float(np.mean(u_))}
    res["P1_variants"] = var
    # ---------------- P1b within-agent judge contrast + permutation
    def contrast(judges):
        vals = []
        for w in wins:
            k = judges[w]
            r = prim[w]
            if k not in r["pres"]:
                continue
            sj = r["S"][r["pres"].index(k)]
            other = [prim[w2]["S"][prim[w2]["pres"].index(k)] for w2 in wins
                     if w2 != w and judges[w2] != k and k in prim[w2]["pres"]]
            if other:
                vals.append(sj - np.mean(other))
        return float(np.mean(vals)) if vals else np.nan
    J0 = {w: lab[w]["judge"] for w in wins}
    obs_c = contrast(J0)
    rng = np.random.default_rng(20261004)
    permc = [contrast({w: int(rng.choice(prim[w]["pres"])) for w in wins}) for _ in range(5000)]
    res["P1b"] = {"contrast": obs_c, "p_perm": float((np.array(permc) >= obs_c).mean()),
                  "perm_sd": float(np.std(permc))}
    # ---------------- N2 field-only skeleton null
    with ProcessPoolExecutor(max_workers=a.workers, initializer=_skel_init) as ex:
        sk = list(ex.map(skel_world, range(5000, 5000 + a.skel), chunksize=4))
    sk_u, sk_n1, sk_uP = [], [], []
    for wd in sk:
        rr = {w: {"pres": wd[w]["pres"], "rank": L.ranks_desc(np.array(wd[w]["S"])).tolist(),
                  "rankP": L.ranks_desc(np.array(wd[w]["SP"])).tolist()} for w in wins}
        r_, n_, u_ = judge_stats(rr, lab, wins)
        _, _, uP_ = judge_stats(rr, lab, wins, key="rankP")
        sk_u.append(np.mean(u_))
        sk_n1.append(sum(x == 1 for x in r_))
        sk_uP.append(np.mean(uP_))
    sk_u = np.array(sk_u)
    res["N2_field_null"] = {"reps": len(sk), "mean_u_null_mean": float(sk_u.mean()), "mean_u_null_sd": float(sk_u.std()),
                            "p_field_top": float((sk_u <= obs_u).mean()), "p_field_bottom": float((sk_u >= obs_u).mean()),
                            "n_rank1_null_mean": float(np.mean(sk_n1)),
                            "mean_uP_null_mean": float(np.mean(sk_uP))}
    # ---------------- P2 team blocks (pair-type model) + permutation; P3a from the same fit
    W = pairtype_windows(calls, XR, XP, agents, lab, wins)
    ft = L.fit_pairtype(W, agents, LAM)
    est, se = L.contrast(ft, "R_ST_all", "R_OT_all")
    estP, seP = L.contrast(ft, "P_ST_all", "P_OT_all")
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        perm = np.array(list(ex.map(perm_job, range(9000, 9000 + a.perm), chunksize=4)))
    ftp = L.fit_pairtype(W, agents, LAM, with_phase_split=True)
    by_phase = {p: L.contrast(ftp, f"R_ST_{p}", f"R_OT_{p}") for p in ("pre", "deb", "post")}
    res["P2"] = {"ST_minus_OT": est, "se": se, "inflight_ST_minus_OT": estP, "se_inflight": seP,
                 "p_perm_greater": float((perm >= est).mean()), "p_perm_less": float((perm <= est).mean()),
                 "perm_sd": float(perm.std()), "coef": ft["coef"], "se_coef": ft["se"],
                 "by_phase": {p: {"est": v[0], "se": v[1]} for p, v in by_phase.items()}}
    dj, dj_se = L.contrast(ft, "R_DJ_all", "P_DJ_all")
    jd, jd_se = L.contrast(ft, "R_JD_all", "P_JD_all")
    # ---------------- P3b verdict step
    obs_v, pl_v = verdict_step(calls, lab, wins, rng=np.random.default_rng(7), n_draw=200)
    pl_v = np.array(pl_v)
    res["P3"] = {"DJ_read_minus_inflight": dj, "se_DJ": dj_se, "JD_read_minus_inflight": jd, "se_JD": jd_se,
                 "verdict_step": obs_v, "placebo_q95_abs": float(np.percentile(np.abs(pl_v), 95)),
                 "p_abs": float((np.abs(pl_v) >= abs(obs_v)).mean()), "placebo_sd": float(pl_v.std())}
    (D12 / "results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: v for k, v in res.items() if k not in ("labels",)}, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
