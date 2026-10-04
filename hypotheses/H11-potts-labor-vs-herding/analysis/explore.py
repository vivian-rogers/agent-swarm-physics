"""H11 exploratory round 1 on non-holdout goal periods (predictions in the card and G<NN>/README.md, 2026-10-03).

Per period: O1 βJ_CW (+ jackknife, N1), O2 βJ_PL (+ N2 shift, N1d, N1), O3 agreement ratio, O4 jump test,
O5 mean-field check, O6 action class, O7 held-out PL, O8 plmDCA, O9 robustness; G26 adds the HH22 vote tests.
Writes data/processed/H11-potts-labor-vs-herding/G<NN>/results.json and results_round1.parquet.

Usage: uv run python analysis/explore.py [--goals 13 18 ...] [--nnull 99] [--workers 2]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h11common as HC  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potts_core as P  # noqa: E402
from h11data import load_period, blocks_ge  # noqa: E402

MIN_BLOCKS3 = 15


def zscore(obs, nul):
    nul = np.asarray(nul, float)
    nul = nul[np.isfinite(nul)]
    if len(nul) < 5 or not np.isfinite(obs):
        return np.nan, np.nan, np.nan, np.nan
    sd = nul.std(ddof=1)
    z = (obs - nul.mean()) / sd if sd > 0 else np.nan
    p = (1 + np.sum(np.abs(nul - nul.mean()) >= abs(obs - nul.mean()))) / (len(nul) + 1)
    return float(z), float(p), float(nul.mean()), float(sd)


def cw_block(s):
    full, se, jk = P.jackknife_cw(s, "period")
    D = s.n_days
    t = full["bj"] / se if se and se > 0 else np.nan
    df = max(len(jk) - 1, 1)
    p = 2 * stats.t.sf(abs(t), df) if np.isfinite(t) else np.nan
    return dict(bj=full["bj"], se=se, t=t, df=df, p=p, lr=full.get("lr"), n_blocks=full.get("n_blocks"),
                mean_N=full.get("mean_N"), tcrit=float(stats.t.ppf(0.975, df)), D=D)


def agreement_ratio(s):
    """Observed same-real-project pair fraction per block / sum_a p_a^2 (pooled shares over coupled states)."""
    m = s.N >= 2
    cnt, N = s.counts[m], s.N[m]
    same = (cnt[:, s.coupled] * (cnt[:, s.coupled] - 1) / 2).sum(1)
    pairs = N * (N - 1) / 2
    obs = same.sum() / pairs.sum()
    p = s.counts.sum(0) / s.counts.sum()
    exp = (p[s.coupled] ** 2).sum()
    return float(obs / exp) if exp > 0 else np.nan, float(obs), float(exp)


def heldout_pl(s):
    """Leave-one-day-out: mean held-out pseudo-loglik, coupled agent-field PL vs fields-only."""
    out = []
    for d in range(s.n_days):
        tr, te = s.day != d, s.day == d
        if te.sum() < 5 or tr.sum() < 20:
            continue
        str_ = s.subset_obs(tr)
        ste = s.subset_obs(te)
        # keep agent indexing global
        str_.n_agents = ste.n_agents = s.n_agents
        a, n = P.pl_loglik_heldout(str_, ste, True)
        b, _ = P.pl_loglik_heldout(str_, ste, False)
        out.append((d, a - b, n))
    if not out:
        return dict(folds=0)
    dl = np.array([o[1] for o in out])
    return dict(folds=len(out), dll_mean=float(dl.mean()), dll_pos=int((dl > 0).sum()), dll=[float(x) for x in dl])


def jump_and_mf(s, cw_bj):
    """O4 + O5 on the share of the final-day dominant real state."""
    lab, gw, day = s.label, s.gwin, s.day
    last = day == day.max()
    real = lab > 0
    if not (last & real).any():
        return dict(verdict="n/a")
    c_last = np.bincount(lab[last & real], minlength=s.S)
    dom = int(np.argmax(c_last))
    uw, inv = np.unique(gw, return_inverse=True)
    n = np.bincount(inv)
    k = np.bincount(inv, weights=(lab == dom).astype(float))
    j = P.fit_jump(uw, k, n)
    # q_eff from the first third (real states)
    T = gw.max() + 1
    first = gw < T / 3
    c1 = np.bincount(lab[first & real], minlength=s.S)[1:]
    p1 = c1 / max(c1.sum(), 1)
    qeff = float(np.exp(-(p1[p1 > 0] * np.log(p1[p1 > 0])).sum())) if c1.sum() else np.nan
    qr = max(2, int(round(qeff))) if np.isfinite(qeff) else 2
    bjs = P.bj_spinodal(qr)
    x_last = float(c_last[dom] / max((last).sum(), 1))
    return dict(**j, dominant_state=dom, qeff=qeff, q_round=qr, bj_s=bjs, bj_c=P.bj_c(qr),
                first_order_region=bool(np.isfinite(cw_bj) and cw_bj >= bjs),
                mf_pred_share=float(P.mf_ordered_share(cw_bj, qr)) if np.isfinite(cw_bj) else np.nan,
                x_last=x_last, bj_x1=P.bj_from_share(x_last, qr), series=dict(t=uw.tolist(), k=k.tolist(), n=n.tolist()))


def analyze(args):
    g, nnull = args
    rng = np.random.default_rng(20261003 + g)
    R = dict(goal=g, cls={**HC.CANDIDATES, **HC.TRANSFER}.get(g, "?"))
    s, df = load_period(g)
    R["n_obs"] = int(len(s.label))
    R["n_agents"] = int(s.n_agents)
    R["n_days"] = int(s.n_days)
    R["blocks3"] = blocks_ge(s, 3)
    R["q"] = int(s.S - 1)
    R["other_frac"] = float((s.label == 0).mean()) if len(s.label) else np.nan
    R["obs_rate"] = float(len(s.label) / max(1, len(np.unique(s.gwin)) * s.n_agents))
    R["rooms"] = int(len(np.unique(df["room"].to_numpy())))
    if R["blocks3"] < MIN_BLOCKS3:
        R["tested"] = False
        return R
    R["tested"] = True
    # persistence: P(same label in the next window | agent observed in both)
    o = np.lexsort((s.win, s.day, s.agent))
    a_, d_, w_, l_ = s.agent[o], s.day[o], s.win[o], s.label[o]
    nxt = (a_[1:] == a_[:-1]) & (d_[1:] == d_[:-1]) & (w_[1:] == w_[:-1] + 1)
    R["persist"] = float((l_[1:][nxt] == l_[:-1][nxt]).mean()) if nxt.any() else np.nan
    # O1
    R["O1"] = cw_block(s)
    nul = [P.fit_cw(s.with_labels(P.null_labels(s, "perm", rng)), "period")["bj"] for _ in range(nnull)]
    R["O1"]["z_N1"], R["O1"]["p_N1"], R["O1"]["N1_mean"], R["O1"]["N1_sd"] = zscore(R["O1"]["bj"], nul)
    # O2
    bj_pl = P.fit_pl(s, "agent")["bj"]
    n2 = [P.fit_pl(P.shift_snap(s, rng), "agent")["bj"] for _ in range(nnull)]
    n1d = [P.fit_pl(s.with_labels(P.null_labels(s, "perm_day", rng)), "agent")["bj"] for _ in range(nnull)]
    n1 = [P.fit_pl(s.with_labels(P.null_labels(s, "perm", rng)), "agent")["bj"] for _ in range(nnull)]
    R["O2"] = dict(bj=bj_pl)
    for nm, nl in (("N2", n2), ("N1d", n1d), ("N1", n1)):
        z, p, m, sd = zscore(bj_pl, nl)
        R["O2"].update({f"z_{nm}": z, f"p_{nm}": p, f"{nm}_mean": m, f"{nm}_sd": sd})
    R["O2"]["bj_uniform"] = P.fit_pl(s, "uniform")["bj"]
    # O3
    R["O3"] = dict(zip(("R", "obs", "exp"), agreement_ratio(s)))
    # O4/O5
    R["O45"] = jump_and_mf(s, R["O1"]["bj"])
    # O6 action class
    sa, _ = load_period(g, state="action")
    ca = cw_block(sa)
    bja = P.fit_pl(sa, "agent")["bj"]
    na2 = [P.fit_pl(P.shift_snap(sa, rng), "agent")["bj"] for _ in range(max(nnull // 2, 19))]
    z, p, m, sd = zscore(bja, na2)
    R["O6"] = dict(bj_cw=ca["bj"], t_cw=ca["t"], se_cw=ca["se"], bj_pl=bja, z_N2=z, p_N2=p)
    # O7
    R["O7"] = heldout_pl(s)
    # O8 plmDCA (secondary, few nulls)
    d_obs, _ = P.plm_diag(s)
    dn = [P.plm_diag(s.with_labels(P.null_labels(s, "perm", rng)))[0] for _ in range(9)]
    z, p, m, sd = zscore(d_obs, dn)
    R["O8"] = dict(diag=d_obs, z_N1=z, null_mean=m, null_sd=sd, n_null=9)
    # O9 robustness
    rob = {}
    for nm, kw in (("raw", dict(variant="raw")), ("q4", dict(qmax=4)), ("W15", dict(W=15)), ("W60", dict(W=60)), ("action_only", dict(state="projectact")),
                   ("pooled_rooms", dict(pool_rooms=True))):
        if nm == "pooled_rooms" and R["rooms"] < 2:
            continue
        try:
            sr, _ = load_period(g, **kw)
            if blocks_ge(sr, 3) < 8:
                rob[nm] = dict(bj_cw=np.nan, note="too few blocks")
                continue
            c = cw_block(sr) if nm != "raw" else dict(bj=P.fit_cw(sr, "period")["bj"], t=np.nan)
            pl_ = P.fit_pl(sr, "agent")["bj"] if nm != "raw" else P.fit_pl(sr, "uniform")["bj"]
            rob[nm] = dict(bj_cw=c["bj"], t_cw=c.get("t"), bj_pl=pl_)
        except Exception as e:  # noqa: BLE001
            rob[nm] = dict(error=str(e)[:200])
    rob["cw_day"] = dict(bj_cw=P.fit_cw(s, "day")["bj"])
    R["O9"] = rob
    return R


# ------------------------------------------------------------------------------------------------ HH22 / G26 votes


def votes_g26(first_person=True):
    v = pl.read_parquet(HC.OUT / "G26" / "votes.parquet")
    wins = pl.read_parquet(HC.OUT / "G26" / "windows_w30.parquet").sort("day", "win").with_row_index("gwin")
    cal = pl.read_parquet(HC.SHARED / "calendar.parquet").select("pt_date", "win_start", "win_end")
    wins = wins.join(cal, on="pt_date").with_columns(
        (pl.col("win_start") + pl.duration(minutes=30 * (pl.col("win").cast(pl.Int64) + 1))).alias("t_end"))
    decl = v.filter(pl.col("vote_word") & (pl.col("n_named") > 0))
    if first_person:
        decl = decl.filter(pl.col("first_person"))
    decl = decl.sort("t")
    cands = sorted({c for lst in decl["named"].to_list() for c in lst})
    # runoff onset: first window with >= 2 runoff-word agent messages
    ro = v.filter(pl.col("runoff_word")).sort("t")
    t_end = wins["t_end"].to_list()
    onset = None
    for i, te in enumerate(t_end):
        ts = wins["win_start"][i] + __import__("datetime").timedelta(minutes=30 * int(wins["win"][i]))
        nro = ro.filter((pl.col("t") >= ts) & (pl.col("t") < te)).height
        if nro >= 2:
            onset = i
            break
    # carried-forward declared states per window
    rows = decl.to_dicts()
    W = []
    for i, te in enumerate(t_end):
        latest = {}
        for r in rows:
            if r["t"] < te:
                latest[r["agent"]] = r["named"]
        W.append(latest)
    final_single = {}
    for r in rows:
        if r["n_named"] == 1 and (onset is None or r["t"] >= wins["win_start"][onset]):
            final_single[r["agent"]] = r["named"][0]
    cnt = {}
    for c in final_single.values():
        cnt[c] = cnt.get(c, 0) + 1
    winner = max(cnt, key=cnt.get) if cnt else (cands[0] if cands else None)
    t, k, n = [], [], []
    for i, latest in enumerate(W):
        if not latest:
            continue
        t.append(i)
        n.append(len(latest))
        k.append(sum(1.0 / len(s_) for s_ in latest.values() if winner in s_))
    j = P.fit_jump(np.array(t), np.array(k), np.array(n))
    out = dict(first_person=first_person, n_decl=len(rows), n_voters=int(decl["agent"].n_unique()), candidates=cands,
               q_vote=len(cands), onset_window=onset, n_windows=len(t_end), winner=winner, runoff_counts=cnt, jump=j,
               series=dict(t=t, k=k, n=n))
    # P-G26a: symmetric point at onset (approval counts and 1/k weights over candidates)
    if onset is not None:
        latest = W[onset - 1] if onset > 0 else {}
        appr = {c: 0 for c in cands}
        wts = {c: 0.0 for c in cands}
        for s_ in latest.values():
            for c in s_:
                appr[c] += 1
                wts[c] += 1.0 / len(s_)
        top = sorted(appr, key=appr.get, reverse=True)[:3]
        obs = np.array([appr[c] for c in top], float)
        chi = stats.chisquare(obs) if obs.sum() > 0 else None
        w = np.array(list(wts.values()))
        pw = w / w.sum() if w.sum() > 0 else w
        qeff = float(np.exp(-(pw[pw > 0] * np.log(pw[pw > 0])).sum())) if w.sum() > 0 else np.nan
        out["sym"] = dict(n_voters_at_onset=len(latest), approvals=appr, top3=top, top3_counts=obs.tolist(),
                          chi2_p=float(chi.pvalue) if chi is not None else np.nan, qeff=qeff)
    # P-G26c: runoff snapshot, symmetric fields
    if cnt:
        q = max(len(out.get("sym", {}).get("top3", [])), len(cnt), 2)
        nvec = np.array(sorted(cnt.values(), reverse=True) + [0] * (q - len(cnt)))
        Nn = int(nvec.sum())
        grid = np.linspace(-10, 15, 501)
        S = q
        coupled = np.ones(S, bool)
        ll = []
        for bj in grid:
            # one snapshot, all fields 0, all states coupled
            snap = P.Snap(np.arange(Nn), np.repeat(np.arange(S), nvec), np.zeros(Nn, int), np.zeros(Nn, int), S, coupled)
            gC = P.CWGroups(snap, "period")
            # force symmetric fields: evaluate negll with all free fields at 0 but all states present
            gC.present[:] = True
            gC.free[:] = True
            gC.free[0, gC.ref[0]] = False
            gC.n_par = 1 + int(gC.free.sum())
            th = np.zeros(gC.n_par)
            th[0] = bj
            ll.append(-gC.negll(th, ridge=0.0)[0])
        ll = np.array(ll)
        i = int(np.argmax(ll))
        ci = grid[ll >= ll[i] - 1.92]
        # P(max count >= observed | βJ = 0, symmetric)
        rng = np.random.default_rng(26)
        sims = rng.multinomial(Nn, np.ones(S) / S, size=200000).max(1)
        out["snapshot"] = dict(q_runoff=q, counts=nvec.tolist(), N=Nn, bj_mle=float(grid[i]),
                               bj_ci=[float(ci.min()), float(ci.max())], bj_s=P.bj_spinodal(q) if q >= 3 else 2.0,
                               p_max_indep=float((sims >= nvec.max()).mean()),
                               mle_at_bound=bool(i == len(grid) - 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="*", default=None)
    ap.add_argument("--nnull", type=int, default=99)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    goals = a.goals or sorted({**HC.CANDIDATES, **HC.TRANSFER})
    HC.assert_not_holdout(goals)
    with Pool(min(a.workers, 2)) as pool:
        res = pool.map(analyze, [(g, a.nnull) for g in goals], chunksize=1)
    for R in res:
        if R["goal"] == 26:
            R["votes"] = votes_g26(True)
            R["votes_any"] = votes_g26(False)
        f = HC.OUT / f"G{R['goal']:02d}" / "round1.json"
        f.write_text(json.dumps(R, indent=1, default=lambda x: None if (isinstance(x, float) and not math.isfinite(x)) else (x.item() if hasattr(x, "item") else str(x))))
        print(R["goal"], R["cls"], "tested" if R.get("tested") else "n/a",
              {k: round(R["O1"][k], 3) for k in ("bj", "t")} if R.get("tested") else "")
    flat = []
    for R in res:
        row = dict(goal=R["goal"], cls=R["cls"], tested=R.get("tested", False), n_obs=R["n_obs"], blocks3=R["blocks3"],
                   q=R["q"], n_agents=R["n_agents"], n_days=R["n_days"])
        if R.get("tested"):
            row.update(bj_cw=R["O1"]["bj"], se_cw=R["O1"]["se"], t_cw=R["O1"]["t"], tcrit=R["O1"]["tcrit"],
                       z_cw_N1=R["O1"]["z_N1"], bj_pl=R["O2"]["bj"], z_N2=R["O2"]["z_N2"], z_N1d=R["O2"]["z_N1d"],
                       z_N1=R["O2"]["z_N1"], R=R["O3"]["R"], jump=R["O45"].get("verdict"), qeff=R["O45"].get("qeff"),
                       act_bj_cw=R["O6"]["bj_cw"], act_t_cw=R["O6"]["t_cw"], act_z_N2=R["O6"]["z_N2"],
                       dll=R["O7"].get("dll_mean"), plm_z=R["O8"]["z_N1"])
        flat.append(row)
    pl.DataFrame(flat).write_parquet(HC.OUT / "results_round1.parquet")
    import datetime as dt
    pf = HC.OUT / "_provenance.json"
    prov = json.loads(pf.read_text()) if pf.exists() else {}
    prov["analysis_outputs"] = {"built_by": "hypotheses/H11-potts-labor-vs-herding/analysis/explore.py",
                                "files": ["G<NN>/round1.json", "results_round1.parquet"], "git_commit": HC.C.git_commit(),
                                "params": {"goals": goals, "nnull": a.nnull, "W_primary": 30}, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    pf.write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
