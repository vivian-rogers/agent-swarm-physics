"""H24 exploratory round 1 on G21 (non-holdout). Observables O1-O4, O6 and nulls N1-N4 as written on the card
(2026-10-03, before this script was run on real data).

Outputs: data/processed/H24-forecast-coupling-switch/G21/explore.json (+ ramp/numeric tables for figures)
Usage: uv run python hypotheses/H24-forecast-coupling-switch/analysis/explore.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np
import polars as pl
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h24stats import (alignment_stats, betaJ_snapshot, degroot, degroot_null, project_out, random_rotations,  # noqa: E402
                      seg_alignment, segments, unit)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h24lib import ANCHORS, H24, TIER1  # noqa: E402
from common import OUT, holdout_mask, load_holdout, load_whitener  # noqa: E402

G = H24 / "G21"
K_ST, K_DOC, B, POST = 4, 5, 200, 60.0
SHIFTS = (60.0, 90.0, 120.0)
SEED = 20261003


def load():
    S = pl.read_parquet(G / "statements.parquet").with_row_index("i")
    X = np.load(G / "stmt_w64.npy").astype(np.float32)
    D = pl.read_parquet(G / "docs.parquet").with_row_index("i")
    Y = np.load(G / "docs_w64.npy").astype(np.float32)
    sw = pl.read_parquet(G / "switch_on.parquet")
    gv = np.load(G / "goal_vec.npz")
    cal = pl.read_parquet(OUT / "calendar.parquet").filter(pl.col("goal_no") == 21).sort("pt_date")
    assert not any(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    return S, X, D, Y, sw, gv, cal


def prep(Xfull, dim, ghat_vecs):
    Z = unit(Xfull[:, :dim].astype(np.float64))
    Zr = unit(project_out(Z, np.array([g[:dim] for g in ghat_vecs])))
    return Z, Zr


def day_minutes(df, cal):
    opens = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    return np.array([(t - opens[d]).total_seconds() / 60 if d in opens else np.nan
                     for t, d in zip(df["t"].to_list(), df["pt_date"].to_list())])


def o1(Z, df, mins, agent_list, tau, k, post_len, day, rng, post_to_eod=False):
    sel_day = (df["pt_date"] == day).to_numpy()
    agents = df["agent"].to_numpy()
    tt = np.where(sel_day, mins, np.nan)
    pl_len = 1e9 if post_to_eod else post_len
    pre, post = segments(tt, agents, agent_list, tau, pl_len)
    return seg_alignment(Z, pre, post, k, B, rng)


def run_instrument(name, Z, Zr, df, mins, agent_list, tau, k, rng, days, post_to_eod=False, row_mask=None):
    """O1 for one instrument: real, N1 placebos, rotation null for levels."""
    if row_mask is not None:
        keep = np.flatnonzero(row_mask)
        Z, Zr, df, mins = Z[keep], Zr[keep], df[keep], mins[keep]
    out = {"instrument": name, "k": k}
    for lab, ZZ in (("raw", Z), ("res", Zr)):
        r = o1(ZZ, df, mins, agent_list, tau, k, POST, days[0], rng, post_to_eod)
        if r is None:
            out[lab] = None
            continue
        plac = []
        for s in SHIFTS:
            p = o1(ZZ, df, mins, agent_list, {a: tau[a] + s for a in agent_list}, k, POST, days[0], rng, post_to_eod)
            if p:
                plac.append({"where": f"day1+{int(s)}", "dA": p["dA"]})
        for d in days[1:]:
            p = o1(ZZ, df, mins, agent_list, tau, k, POST, d, rng, post_to_eod)
            if p:
                plac.append({"where": d, "dA": p["dA"]})
        dAs = [p["dA"] for p in plac]
        r["N1"] = plac
        r["N1_q90"] = float(np.quantile(dAs, 0.9)) if dAs else None
        r["N1_rank"] = int(sum(x >= r["dA"] for x in dAs)) + 1 if dAs else None
        # N3 rotation null for the levels (one rotation per agent, both segments)
        lv = []
        ag = df["agent"].to_numpy()
        for rep in range(25):
            rots = random_rotations(ZZ.shape[1], len(agent_list), rng)  # a fresh rotation per agent (no collisions)
            ZR = ZZ.copy()
            for a, Q in zip(agent_list, rots):
                ZR[ag == a] = ZZ[ag == a] @ Q
            q = o1(ZR, df, mins, agent_list, tau, k, POST, days[0], np.random.default_rng(rep))
            if q:
                lv.append((q["A_pre"], q["A_post"], q["dA"]))
        lv = np.array(lv)
        r["N3_rot"] = {"A_pre_q95": float(np.quantile(lv[:, 0], 0.95)), "A_post_q95": float(np.quantile(lv[:, 1], 0.95)),
                       "dA_q05": float(np.quantile(lv[:, 2], 0.05)), "dA_q95": float(np.quantile(lv[:, 2], 0.95))}
        r["boot"] = o1_boot(ZZ, df, mins, agent_list, tau, k, days[0], rng, post_to_eod)
        out[lab] = r
    return out


def o1_boot(Z, df, mins, agent_list, tau, k, day, rng, post_to_eod, n_boot=200, b=20):
    """Bootstrap over statements within agent x segment: CI of dA and of the snapshot betaJ0/n."""
    sel_day = (df["pt_date"] == day).to_numpy()
    tt = np.where(sel_day, mins, np.nan)
    pre, post = segments(tt, df["agent"].to_numpy(), agent_list, tau, 1e9 if post_to_eod else POST)
    dA, dbJ, bJp, bJq = [], [], [], []
    for _ in range(n_boot):
        gp = [rng.choice(g, len(g), replace=True) if len(g) else g for g in pre]
        gq = [rng.choice(g, len(g), replace=True) if len(g) else g for g in post]
        r = seg_alignment(Z, gp, gq, k, b, rng)
        if r:
            dA.append(r["dA"]); bJp.append(r["bJ_pre"]); bJq.append(r["bJ_post"]); dbJ.append(r["bJ_post"] - r["bJ_pre"])
    q = lambda v: [float(np.quantile(v, 0.05)), float(np.quantile(v, 0.95))]  # noqa: E731
    return {"dA_ci90": q(dA), "bJ_pre_ci90": q(bJp), "bJ_post_ci90": q(bJq), "dbJ_ci90": q(dbJ)}


def placebo_N2(dim, k, rng, offset):
    """Kickoff-matched placebo weeks: tau = open + offset for every agent, first active day."""
    weeks = pl.read_parquet(H24 / "placebo/placebo_weeks.parquet")
    gh = np.load(H24 / "placebo/placebo_ghat.npy")
    held = set(load_holdout()["goal_periods_held_out"])
    st = pl.read_parquet(OUT / "embeddings/statements.parquet")
    roster = pl.read_parquet(OUT / "roster.parquet", columns=["agent", "claude_code"])
    st = st.join(roster, on="agent").filter(~pl.col("claude_code"))
    Ec = np.load(OUT / "embeddings/chat_bge_small.npy", mmap_mode="r")
    Ei = np.load(OUT / "embeddings/intentions_bge_small.npy", mmap_mode="r")
    W = load_whitener("I", 64)
    res = []
    for wk, g in zip(weeks.iter_rows(named=True), gh):
        assert wk["goal_no"] not in held
        sub = st.filter(pl.col("goal_no") == wk["goal_no"], pl.col("pt_date") == wk["pt_date"]).sort("t")
        assert not any(sub["holdout"].to_list())
        if sub.height == 0:
            continue
        kind = sub["kind"].to_numpy(); src = sub["src_row"].to_numpy()
        E = np.empty((sub.height, 384), dtype=np.float32)
        m = kind == "chat"
        E[m] = Ec[src[m]]; E[~m] = Ei[src[~m]]
        X = W(E)
        Z, Zr = prep(X, dim, [g])
        mins = np.array([(t - wk["win_start"]).total_seconds() / 60 for t in sub["t"].to_list()])
        agents = sub["agent"].to_numpy()
        al = sorted(set(agents.tolist()))
        tau = {a: offset for a in al}
        out = {"goal_no": wk["goal_no"], "has_kickoff": wk["has_kickoff"]}
        for lab, ZZ in (("raw", Z), ("res", Zr)):
            pre, post = segments(mins, agents, al, tau, POST)
            r = seg_alignment(ZZ, pre, post, k, B // 2, rng)
            out[lab] = None if r is None else {"N": r["N"], "dA": r["dA"], "A_pre": r["A_pre"], "A_post": r["A_post"]}
        if out["res"] is not None and out["res"]["N"] >= 4:
            res.append(out)
    return res


def ramp(Zr, Z, df, cal, rng, k=4):
    """O3: A_res per 2-h block over the week (agents with >= k statements in the block)."""
    opens = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    rows = []
    agents = df["agent"].to_numpy(); tt = df["t"].to_list(); dd = df["pt_date"].to_list()
    blk = np.array([int((t - opens[d]).total_seconds() // 7200) if d in opens else -1 for t, d in zip(tt, dd)])
    for bi, d in enumerate(cal["pt_date"].to_list()):
        for b in (0, 1):
            sel = (np.array(dd) == d) & (blk == b)
            groups = [np.flatnonzero(sel & (agents == a)) for a in sorted(set(agents[sel].tolist()))]
            groups = [g for g in groups if len(g) >= k]
            if len(groups) < 3:
                continue
            vals = {"raw": [], "res": []}
            for _ in range(B):
                for lab, ZZ in (("raw", Z), ("res", Zr)):
                    V = np.array([unit(ZZ[rng.choice(g, k, replace=False)].mean(0)) for g in groups])
                    vals[lab].append(alignment_stats(V))
            r = {"pt_date": d, "block": b, "idx": 2 * bi + b, "N": len(groups)}
            for lab in ("raw", "res"):
                a = np.array(vals[lab])
                r[f"A_{lab}"] = float(a[:, 0].mean()); r[f"m_{lab}"] = float(a[:, 1].mean())
            r["bJ_res"] = betaJ_snapshot(r["A_res"], r["N"])
            rows.append(r)
    return rows


def numeric(rng):
    out = {}
    for ex in ("prereg", "A1"):
        out[ex] = numeric_one(rng, pl.read_parquet(G / "numeric.parquet").filter(pl.col("extractor") == ex))
    hv = pl.read_parquet(G / "numeric_handverified.parquet")
    out["hand"] = {"all": units_test(rng, hv),
                   "day1_first": units_test(rng, hv.filter(pl.col("t_first").dt.day() == 1))}
    return out


def units_test(rng, both):
    """O4 on a first/last unit table (speaker, question, first, last)."""
    q = both["question"].to_list()
    k, dsd = degroot(both["first"].to_list(), both["last"].to_list(), q)
    kn, _ = degroot_null(both["first"].to_list(), both["last"].to_list(), q, rng, n_perm=10000)
    r = {"n_units": both.height, "kappa": k, "kappa_perm_p": float((np.sum(kn >= k) + 1) / (len(kn) + 1)) if k is not None else None,
         "kappa_null_q90": float(np.quantile(kn, 0.9)), "dSD": dsd, "dSD_perm_p": {},
         "sd_first": {}, "sd_last": {}, "mean_first": {}, "mean_last": {},
         "units": both.select("speaker", "question", "first", "last", "seg_first").to_dicts()}
    for qq in dsd:
        sb = both.filter(pl.col("question") == qq)
        x = sb["first"].to_numpy(); dl = (sb["last"] - sb["first"]).to_numpy()
        null = [np.std(x + rng.permutation(dl), ddof=1) - np.std(x, ddof=1) for _ in range(10000)]
        r["dSD_perm_p"][qq] = float(np.mean(np.array(null) <= dsd[qq]))
        r["sd_first"][qq] = float(np.std(x, ddof=1)); r["sd_last"][qq] = float(np.std(sb["last"].to_numpy(), ddof=1))
        r["mean_first"][qq] = float(x.mean()); r["mean_last"][qq] = float(sb["last"].mean())
    return r


def numeric_one(rng, N):
    out = {}
    for attr_set, lab in ((["self"], "self"), (["self", "ambiguous"], "self+ambiguous")):
        sub = N.filter(pl.col("attribution").is_in(attr_set), pl.col("question").is_in(ANCHORS)).sort("t")
        firsts = sub.group_by("speaker", "question").agg(pl.col("value").first().alias("first"), pl.col("value").last().alias("last"),
                                                       pl.col("t").first().alias("t_first"), pl.col("t").last().alias("t_last"),
                                                       pl.len().alias("n"), pl.col("seg").first().alias("seg_first"))
        both = firsts.filter(pl.col("t_last") > pl.col("t_first"))
        q = both["question"].to_list()
        k, dsd = degroot(both["first"].to_list(), both["last"].to_list(), q)
        kn, sdn = degroot_null(both["first"].to_list(), both["last"].to_list(), q, rng, n_perm=10000)
        delta = (both["last"] - both["first"]).to_numpy()
        # parametric independent updating: delta ~ N(0, sigma^2), sigma from observed deltas
        sig = float(np.sqrt(np.mean(delta ** 2))) if len(delta) else np.nan
        par_sd = []
        for _ in range(5000):
            dd = {}
            for qq in set(q):
                s = np.array(q) == qq
                x = both["first"].to_numpy()[s]
                y = x + rng.normal(0, sig, s.sum())
                dd[qq] = np.std(y, ddof=1) - np.std(x, ddof=1)
            par_sd.append(dd)
        out[lab] = {
            "units": both.select("speaker", "question", "first", "last", "n", "seg_first").to_dicts(),
            "n_units": both.height, "kappa": k, "kappa_perm_p": float((np.sum(kn >= k) + 1) / (len(kn) + 1)) if k is not None else None,
            "kappa_null_q90": float(np.quantile(kn, 0.9)), "dSD": dsd,
            "dSD_perm_p": {qq: None for qq in dsd},
            "dSD_param_p": {qq: float(np.mean([p[qq] <= v for p in par_sd if qq in p])) for qq, v in dsd.items()},
            "sd_first": {qq: float(both.filter(pl.col("question") == qq)["first"].std()) for qq in dsd},
            "sd_last": {qq: float(both.filter(pl.col("question") == qq)["last"].std()) for qq in dsd},
            "mean_first": {qq: float(both.filter(pl.col("question") == qq)["first"].mean()) for qq in dsd},
            "mean_last": {qq: float(both.filter(pl.col("question") == qq)["last"].mean()) for qq in dsd},
            "sigma_update": sig,
        }
        # permutation p for dSD per question
        for qq in dsd:
            s = both.filter(pl.col("question") == qq)
            x = s["first"].to_numpy(); dl = (s["last"] - s["first"]).to_numpy()
            null = [np.std(x + rng.permutation(dl), ddof=1) - np.std(x, ddof=1) for _ in range(10000)]
            out[lab]["dSD_perm_p"][qq] = float(np.mean(np.array(null) <= dsd[qq]))
    # time-resolved dispersion S_q(t) of each agent's latest self value; all tier-1 questions, descriptive
    sub = N.filter(pl.col("attribution") == "self", pl.col("question").is_in(TIER1)).sort("t")
    traj = []
    for qq in TIER1:
        s = sub.filter(pl.col("question") == qq)
        latest = {}
        for r in s.iter_rows(named=True):
            latest[r["speaker"]] = r["value"]
            if len(latest) >= 3:
                v = np.array(list(latest.values()))
                traj.append({"question": qq, "t": r["t"].isoformat(), "n_agents": len(latest), "sd": float(v.std(ddof=1)), "mean": float(v.mean())})
    out["trajectory"] = traj
    out["tier1_final"] = (sub.group_by("speaker", "question").agg(pl.col("value").last()).sort("question", "speaker").to_dicts())
    return out


def control_did(Zr, df, mins, switched, tau_star, rng, k=K_ST):
    """O6: DiD of residual alignment for switched pairs vs GPT-5 (agent 10) pairs around tau*."""
    day = "2025-12-01"
    sel = (df["pt_date"] == day).to_numpy()
    agents = df["agent"].to_numpy()
    al = switched + [10]
    tau = {a: tau_star for a in al}
    pre, post = segments(np.where(sel, mins, np.nan), agents, al, tau, POST)
    if min(len(pre[-1]), len(post[-1])) < k:
        return {"note": f"GPT-5 has {len(pre[-1])} pre / {len(post[-1])} post statements (< k)"}
    sw_pre, sw_post, c_pre, c_post = [], [], [], []
    for _ in range(B):
        vp = np.array([unit(Zr[rng.choice(g, k, replace=False)].mean(0)) for g in pre])
        vq = np.array([unit(Zr[rng.choice(g, k, replace=False)].mean(0)) for g in post])
        Cp, Cq = vp @ vp.T, vq @ vq.T
        n = len(switched)
        iu = np.triu_indices(n, 1)
        sw_pre.append(Cp[:n, :n][iu].mean()); sw_post.append(Cq[:n, :n][iu].mean())
        c_pre.append(Cp[n, :n].mean()); c_post.append(Cq[n, :n].mean())
    d_sw = float(np.mean(sw_post) - np.mean(sw_pre)); d_c = float(np.mean(c_post) - np.mean(c_pre))
    return {"dA_switched_pairs": d_sw, "dA_gpt5_pairs": d_c, "DiD": d_sw - d_c,
            "A_sw_pre": float(np.mean(sw_pre)), "A_sw_post": float(np.mean(sw_post)),
            "A_c_pre": float(np.mean(c_pre)), "A_c_post": float(np.mean(c_post)),
            "n_gpt5_pre": len(pre[-1]), "n_gpt5_post": len(post[-1])}


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    if "--numeric-only" in sys.argv:
        out = json.loads((G / "explore.json").read_text())
        out["numeric"] = numeric(rng)
        (G / "explore.json").write_text(json.dumps(out, indent=1, default=str))
        print("numeric updated"); return
    S, X, D, Y, sw, gv, cal = load()
    days = cal["pt_date"].to_list()
    switched = sw.filter(pl.col("role") == "switched")["agent"].to_list()
    tau = dict(zip(sw["agent"].to_list(), sw["tau_offset_min"].to_list()))
    tau_sw = {a: tau[a] for a in switched}
    tau_star = float(np.median([tau[a] for a in switched]))
    mins_S = day_minutes(S, cal); mins_D = day_minutes(D, cal)
    out = {"tau_star_min": tau_star, "switched": switched, "seed": SEED, "B": B}

    results = {}
    for dim, gname in ((32, "ghat"), (16, "ghat"), (64, "ghat"), (32, "goal"), (32, "kickoff")):
        gvec = [gv[gname]]
        Z, Zr = prep(X, dim, gvec)
        Zd, Zdr = prep(Y, dim, gvec)
        tag = f"n{dim}_{gname}"
        res = {}
        res["a_all"] = run_instrument("all statements", Z, Zr, S, mins_S, switched, tau_sw, K_ST, rng, days)
        if tag == "n32_ghat":
            res["b_forecast"] = run_instrument("forecast statements", Z, Zr, S, mins_S, switched, tau_sw, K_ST, rng, days,
                                               row_mask=S["forecast"].to_numpy())
            res["c_docs_all"] = run_instrument("doc chunks (all)", Zd, Zdr, D, mins_D, switched, tau_sw, K_DOC, rng, days, post_to_eod=True)
            res["c_docs_own"] = run_instrument("doc chunks (own)", Zd, Zdr, D, mins_D, switched, tau_sw, K_DOC, rng, days,
                                               post_to_eod=True, row_mask=~D["names_other"].to_numpy())
            for kk in (3, 5):
                res[f"a_all_k{kk}"] = run_instrument(f"all statements k={kk}", Z, Zr, S, mins_S, switched, tau_sw, kk, rng, days)
            out["ramp"] = ramp(Zr, Z, S, cal, rng)
            out["control_did"] = control_did(Zr, S, mins_S, switched, tau_star, rng)
        results[tag] = res
        print(tag, "done", f"{time.time() - t0:.0f}s", flush=True)
    out["O1"] = results
    out["N2"] = placebo_N2(32, K_ST, rng, tau_star)
    print("N2 done", f"{time.time() - t0:.0f}s", flush=True)
    out["numeric"] = numeric(rng)

    # O3 trend over G21b-c blocks (after day-1 block 0)
    rp = [r for r in out["ramp"] if not (r["pt_date"] == days[0] and r["block"] == 0)]
    rho, p = stats.spearmanr([r["idx"] for r in rp], [r["A_res"] for r in rp])
    b_ = [r["A_res"] for r in rp if r["pt_date"] < "2025-12-04"]; c_ = [r["A_res"] for r in rp if r["pt_date"] >= "2025-12-04"]
    out["O3"] = {"rho": float(rho), "p": float(p), "n_blocks": len(rp), "step_1204": float(np.mean(c_) - np.mean(b_))}
    (G / "explore.json").write_text(json.dumps(out, indent=1, default=str))
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
