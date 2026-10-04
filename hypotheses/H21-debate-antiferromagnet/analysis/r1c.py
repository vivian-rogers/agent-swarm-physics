"""H21 round 1c (stance v2.1, 2026-10-04): re-test of the round-1b stance clauses with DQ10's validated conflict flag.

Pre-registered in the card (section "Round 1c", 22:10 UTC). Input: data/processed/shared/reply_stance_v2.parquet
(disagree_validated_agent), agent parents, non-holdout. Label noise (precision, recall) is built into the nulls through
analysis/labelnoise.py. Tests:
  S1c      flag rate opposite minus same team (debate phase, equal weight per debate): team re-partition null;
           noise-aware agent-field null; label-confusion stress null; noise-aware true-scale Delta-hat; corrected rates
  S2c      team recovery from each debate's flag graph (and s2_soft, secondary)
  S3c      post-verdict window contrast + power at the debate-phase Delta-hat; S3c-carry outside debate phases
  native   within-pair contrast (re-drafting)
  controls #33 and #26 corrected disagreement rates vs #12 opposite-team; #33 camps vs the noise-aware null
  old->new DQ2 opposes shares on the same rows; #12-specific noise sensitivity
Usage: uv run python hypotheses/H21-debate-antiferromagnet/analysis/r1c.py [--fast]
Writes data/processed/H21-debate-antiferromagnet/r1c/r1c.json (numbers only; no text).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import afmlib as L  # noqa: E402
import h21core as C  # noqa: E402
import labelnoise as N  # noqa: E402
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H21-debate-antiferromagnet/r1c"
FAST = "--fast" in sys.argv
NPERM = 5000 if FAST else 20000
K_DRAWS = 20 if FAST else 40
M_SIM = 10 if FAST else 25
NBOOT = 100 if FAST else 300
RNG = 20261004


def jdump(o):
    def d(x):
        if isinstance(x, dict):
            return {str(k): d(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [d(v) for v in x]
        if isinstance(x, np.ndarray):
            return d(x.tolist())
        if isinstance(x, (np.floating, float)):
            return None if not np.isfinite(x) else float(x)
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, np.bool_):
            return bool(x)
        return x
    return json.dumps(d(o), indent=1)


# ============================================================================================ data
def load_v2(goal):
    r = pl.read_parquet(SH / "reply_stance_v2.parquet").rename({"phase": "lab_phase"})
    r = r.filter((pl.col("goal_no") == goal) & (pl.col("a_kind") == 0) & (pl.col("b_agent") != pl.col("a_agent"))
                 & ~pl.col("holdout"))
    hm = np.array(holdout_mask(r["pt_date"].to_list(), r["goal_no"].to_list()), bool)
    assert not hm.any(), "holdout rows in reply_stance_v2"
    return r.with_columns(pl.col("disagree_validated_agent").cast(pl.Float64).alias("f"),
                          pl.col("stance2").cast(pl.String).is_in(["correct", "inform"]).alias("ci"),
                          (pl.col("stance2").cast(pl.String) == "disagree").alias("jev_dis"),
                          (pl.col("dq2_stance").cast(pl.String) == "opposes").alias("dq2_opp"))


def load_debates():
    import g12_analysis as G
    st_pl, st, X, debates, lab_of, W = G.load(32)
    t0 = st_pl["t"].min()
    return st_pl, debates, t0


def g12_frame(st_pl, debates, t0):
    """v2 replies in #12 with B's debate and phase (H21 labels); team relation for debater-to-debater pairs."""
    r = load_v2(12)
    ph = st_pl.select(pl.col("message_id").alias("B_message_id"), "debate", "phase", pl.col("t").alias("tB"))
    r = r.join(ph, on="B_message_id", how="inner")
    dd = {d["debate"]: d for d in debates}
    rows = []
    for x in r.iter_rows(named=True):
        d = dd.get(x["debate"])
        eb = ea = 0
        if d is not None and x["phase"] in ("pre", "deb", "post"):
            eb, ea = C.team_of(d, x["b_agent"]), C.team_of(d, x["a_agent"])
        rows.append({"B_message_id": x["B_message_id"], "b_agent": x["b_agent"], "a_agent": x["a_agent"], "debate": x["debate"],
                     "phase": x["phase"], "tB_s": (x["tB"] - t0).total_seconds(), "f": x["f"], "ci": x["ci"], "jev_dis": x["jev_dis"],
                     "dq2_opp": x["dq2_opp"], "s2_soft": x["s2_soft"], "p_disagree": x["p_disagree"], "eb": eb, "ea": ea})
    df = pl.DataFrame(rows)
    return df.with_columns((pl.col("eb") == pl.col("ea")).alias("same"), ((pl.col("eb") != 0) & (pl.col("ea") != 0)).alias("debaters"))


# ============================================================================================ design
class Design:
    """Rows inside debates with a two-team relation. deb[i] debate id; members per debate; exact re-partitions."""

    def __init__(self, df, debates, team_override=None):
        self.df = df
        self.n = df.height
        self.b = df["b_agent"].to_numpy().astype(int)
        self.a = df["a_agent"].to_numpy().astype(int)
        self.deb = df["debate"].to_numpy().astype(int)
        dd = {d["debate"]: d for d in debates}
        ags = sorted(set(self.b.tolist()) | set(self.a.tolist()))
        self.agents = ags
        pos = {x: k for k, x in enumerate(ags)}
        self.spk = np.array([pos[x] for x in self.b]); self.tgt = np.array([pos[x] for x in self.a])
        self.NA = len(ags)
        self.debs = sorted(set(self.deb.tolist()))
        self.idx, self.parts_same, self.same_true = {}, {}, np.zeros(self.n, bool)
        for d in self.debs:
            deb = dd[d] if team_override is None else team_override[d]
            ix = np.flatnonzero(self.deb == d)
            members = sorted(set(deb["gov"]) | set(deb["opp"]))
            mp = {x: k for k, x in enumerate(members)}
            bi = np.array([mp[x] for x in self.b[ix]]); ai = np.array([mp[x] for x in self.a[ix]])
            parts = L.partitions(len(members), len(deb["gov"]))
            S = np.array([e[bi] == e[ai] for e in parts])
            truth = np.array([C.team_of(deb, x) for x in members])
            self.same_true[ix] = truth[bi] == truth[ai]
            self.idx[d] = ix
            self.parts_same[d] = S

    def per_debate(self, f, same=None):
        same = self.same_true if same is None else same
        out = {}
        for d in self.debs:
            ix = self.idx[d]
            s = same[ix]
            if s.sum() == 0 or (~s).sum() == 0:
                continue
            out[d] = float(f[ix][~s].mean() - f[ix][s].mean())   # opposite minus same: AF order > 0
        return out

    def stat(self, f, same=None):
        p = self.per_debate(f, same)
        return float(np.mean(list(p.values()))) if p else np.nan

    def perm_null(self, f, n, rng):
        vals = {}
        for d in self.debs:
            ix = self.idx[d]
            S = self.parts_same[d]
            v = []
            for s in S:
                if s.sum() and (~s).sum():
                    v.append(f[ix][~s].mean() - f[ix][s].mean())
            if v:
                vals[d] = np.array(v)
        obs_debs = [d for d in self.per_debate(f)]
        tot = np.zeros(n)
        for d in obs_debs:
            tot += vals[d][rng.integers(0, len(vals[d]), n)]
        return tot / max(1, len(obs_debs))


def ci_shares(df, group):
    """Share of Jev correct+inform among rows whose Jev class is not 'disagree', per group code."""
    g = np.asarray(group)
    ci = df["ci"].to_numpy(); nd = ~df["jev_dis"].to_numpy()
    out = np.zeros(g.max() + 1)
    for k in range(g.max() + 1):
        m = (g == k) & nd
        out[k] = ci[m].mean() if m.any() else np.nan
    return out


def noise_null(D, f, stat_fn, rng, ctx="pop", stress=None, K=None, M=None):
    """Noise-aware agent-field null: per noise draw, fit the Delta = 0 model to the observed flags through the noise
    map (optionally with a per-row stress phi), simulate M flag sets, return the statistic's null values."""
    K = K or K_DRAWS; M = M or M_SIM
    dr = N.draws(K, rng, ctx)
    vals = []
    for ppv, R, phi in dr:
        phv = phi if stress is None else N.stress_phi(phi, *stress)
        par = N.fit(f, D.spk, D.tgt, None, D.NA, R, phv)
        for _ in range(M):
            vals.append(stat_fn(N.simulate(D.spk, D.tgt, None, par, R, phv, rng)))
    return np.array(vals)


def delta_hat(D, f, rng, ctx="pop", nboot=None):
    """True-scale log-odds of disagreement, opponents vs teammates (noise-aware agent-field logistic), with corrected
    rates. Interval: debate bootstrap x noise draws (percentile)."""
    nboot = nboot or NBOOT
    X = (~D.same_true).astype(float)[:, None]
    dr = N.draws(max(nboot, K_DRAWS), rng, ctx)
    pt = []
    for ppv, R, phi in dr[:K_DRAWS]:
        pt.append(N.fit(f, D.spk, D.tgt, X, D.NA, R, phi)["beta"][0])

    def rates(ff, same, R, phi):
        ro, rs = ff[~same].mean(), ff[same].mean()
        return N.rogan_gladen(ro, R, phi), N.rogan_gladen(rs, R, phi), ro, rs
    rr = np.array([rates(f, D.same_true, R, phi)[:2] for ppv, R, phi in dr[:K_DRAWS]])
    bs, bsr = [], []
    for k in range(nboot):
        dsel = rng.choice(D.debs, len(D.debs))
        ix = np.concatenate([D.idx[d] for d in dsel])
        ppv, R, phi = dr[k]
        Xb = X[ix]
        if Xb[:, 0].min() == Xb[:, 0].max():
            continue
        bs.append(N.fit(f[ix], D.spk[ix], D.tgt[ix], Xb, D.NA, R, phi)["beta"][0])
        bsr.append(rates(f[ix], D.same_true[ix], R, phi)[:2])
    bs, bsr = np.array(bs), np.array(bsr)
    return {"delta_hat": float(np.mean(pt)), "delta_hat_ci95": np.quantile(bs, [0.025, 0.975]).tolist(),
            "delta_hat_noise_range": [float(np.min(pt)), float(np.max(pt))],
            "true_rate_opp": float(rr[:, 0].mean()), "true_rate_same": float(rr[:, 1].mean()),
            "true_rate_opp_ci95": np.quantile(bsr[:, 0], [0.025, 0.975]).tolist(),
            "true_rate_same_ci95": np.quantile(bsr[:, 1], [0.025, 0.975]).tolist(),
            "true_rate_diff_ci95": np.quantile(bsr[:, 0] - bsr[:, 1], [0.025, 0.975]).tolist(),
            "obs_rate_opp": float(f[~D.same_true].mean()), "obs_rate_same": float(f[D.same_true].mean()), "n_boot": len(bs)}


# ============================================================================================ S2c recovery
def recovery(D, w, debates, rng, sign=-1.0):
    """Per debate: J_ij = mean of sign*w over replies between i and j (both directions); the best two-block split
    (true sizes) maximizing within minus across mean J. Ties share credit. Chance by Monte Carlo of random splits."""
    dd = {d["debate"]: d for d in debates}
    credit, chance, per = [], [], {}
    for d in D.debs:
        deb = dd[d]
        members = sorted(set(deb["gov"]) | set(deb["opp"]))
        mp = {x: k for k, x in enumerate(members)}
        n = len(members)
        S = np.zeros((n, n)); Wt = np.zeros((n, n))
        for i in D.idx[d]:
            p, q = mp[D.b[i]], mp[D.a[i]]
            S[p, q] += sign * w[i]; S[q, p] += sign * w[i]; Wt[p, q] += 1; Wt[q, p] += 1
        J = np.where(Wt > 0, S / np.where(Wt > 0, Wt, 1), np.nan)
        parts = L.partitions(n, len(deb["gov"]))
        truth = L.canon(np.array([C.team_of(deb, x) for x in members]))
        iu = np.triu_indices(n, 1)
        v = J[iu]; ok = np.isfinite(v)
        sc = []
        for e in parts:
            same = e[iu[0]] == e[iu[1]]
            sc.append(v[same & ok].mean() - v[~same & ok].mean() if (same & ok).any() and (~same & ok).any() else np.nan)
        sc = np.array(sc)
        if np.all(~np.isfinite(sc)):
            c = 1 / len(parts)
        else:
            best = np.flatnonzero(np.isclose(sc, np.nanmax(sc)))
            c = float(np.mean([L.canon(parts[k]) == truth for k in best]))
        credit.append(c); chance.append(1 / len(parts))
        per[int(d)] = {"credit": c, "n_part": len(parts), "n_replies": int(len(D.idx[d])), "n_pairs_observed": int(ok.sum())}
    obs = float(np.sum(credit))
    null = np.sum(rng.random((20000, len(chance))) < np.array(chance), 1)
    return {"recovered": obs, "n_debates": len(credit), "expected": float(np.sum(chance)),
            "p": float((1 + np.sum(null >= obs - 1e-9)) / (1 + len(null))), "per_debate": per}


# ============================================================================================ S1c / S3c
def s1c(D, rng, label):
    f = D.df["f"].to_numpy()
    obs = D.stat(f)
    per = D.per_debate(f)
    null_perm = D.perm_null(f, NPERM, rng)
    null_af = noise_null(D, f, D.stat, rng)
    grp = (~D.same_true).astype(int)
    sh = ci_shares(D.df, grp)
    null_stress = noise_null(D, f, D.stat, rng, stress=(grp, sh))
    null_g12 = noise_null(D, f, D.stat, rng, ctx="g12")
    out = {"label": label, "n": D.n, "n_same": int(D.same_true.sum()), "n_opp": int((~D.same_true).sum()),
           "n_flags": int(f.sum()), "flags_same": int(f[D.same_true].sum()), "flags_opp": int(f[~D.same_true].sum()),
           "delta_f": obs, "per_debate": per, "positive_debates": int(sum(v > 0 for v in per.values())),
           "zero_debates": int(sum(v == 0 for v in per.values())), "n_debates": len(per),
           "p_team_perm": L.p_upper(obs, null_perm), "perm_q95": float(np.quantile(null_perm, 0.95)),
           "af_null_mean": float(np.mean(null_af)), "af_null_q95": float(np.quantile(null_af, 0.95)), "p_af": N.pval(obs, null_af),
           "stress_ci_share_same_opp": sh.tolist(), "stress_phi_ratio_opp_over_same": float(sh[1] / sh[0]) if sh[0] > 0 else None,
           "stress_null_mean": float(np.mean(null_stress)), "stress_null_q95": float(np.quantile(null_stress, 0.95)),
           "p_stress": N.pval(obs, null_stress),
           "g12noise_null_q95": float(np.quantile(null_g12, 0.95)), "p_af_g12noise": N.pval(obs, null_g12)}
    out["stress_expected_over_obs"] = float(out["stress_null_mean"] / obs) if obs > 0 else None
    # Amendment 1c-1 (synthetic, before the real run): the stress null replaces team permutation in the decision;
    # the Delta-hat interval clause is dropped (under-coverage).
    out["pass_S1c"] = bool(obs > 0 and out["p_stress"] < 0.01 and obs > out["af_null_q95"])
    out["pass_S1c_stress_half"] = bool(obs > 0 and out["stress_null_mean"] < 0.5 * obs)
    out["dhat_pop"] = delta_hat(D, f, rng, "pop")
    out["dhat_g12"] = delta_hat(D, f, rng, "g12", nboot=max(50, NBOOT // 3))
    # old -> new on the same rows
    dq = D.df["dq2_opp"].to_numpy().astype(float)
    out["dq2_opposes_share_same"] = float(dq[D.same_true].mean()); out["dq2_opposes_share_opp"] = float(dq[~D.same_true].mean())
    out["dq2_delta_opposes"] = D.stat(dq)
    out["flag_given_dq2_opposes_opp"] = float(f[(~D.same_true) & (dq == 1)].mean()) if ((~D.same_true) & (dq == 1)).any() else None
    out["flag_given_dq2_opposes_same"] = float(f[D.same_true & (dq == 1)].mean()) if (D.same_true & (dq == 1)).any() else None
    pd_ = D.df["p_disagree"].to_numpy(); s2 = D.df["s2_soft"].to_numpy()
    out["soft_p_disagree_delta"] = D.stat(pd_); out["soft_p_disagree_p_perm"] = L.p_upper(D.stat(pd_), D.perm_null(pd_, NPERM, rng))
    out["s2_soft_same"] = float(s2[D.same_true].mean()); out["s2_soft_opp"] = float(s2[~D.same_true].mean())
    out["s2_soft_delta_same_minus_opp"] = -D.stat(s2)
    out["s2_soft_p_perm"] = L.p_lower(D.stat(s2), D.perm_null(s2, NPERM, rng))
    out["jev_correct_inform_share_same_opp"] = sh.tolist()
    return out


def post_power(Ddeb, Dpost, rng, reps=500):
    """Power of the post-window team-permutation test (alpha 0.05) if the debate-phase contrast persisted. Two
    persistence models, simulated on the post-window reply structure:
      'model': the debate-phase noise-aware fit (fields and Delta-hat of the debate phase; one noise draw per replicate)
      'rates': the debate-phase observed flag rates per relation (same / opposite), applied row by row."""
    fd = Ddeb.df["f"].to_numpy()
    Xd = (~Ddeb.same_true).astype(float)[:, None]
    pos = {a: k for k, a in enumerate(Ddeb.agents)}
    sp = np.array([pos[x] for x in Dpost.b]); tp = np.array([pos[x] for x in Dpost.a])
    Xp = (~Dpost.same_true).astype(float)[:, None]
    dr = N.draws(reps, rng)
    fits = [N.fit(fd, Ddeb.spk, Ddeb.tgt, Xd, Ddeb.NA, R, phi) for _, R, phi in dr[:20]]
    r_opp, r_same = fd[~Ddeb.same_true].mean(), fd[Ddeb.same_true].mean()
    hits_m, hits_r, nflags_m = [], [], []
    for k in range(reps):
        ppv, R, phi = dr[k]
        y = N.simulate(sp, tp, Xp, fits[k % 20], R, phi, rng)
        nflags_m.append(y.sum())
        hits_m.append(bool(y.sum() > 0 and L.p_upper(Dpost.stat(y), Dpost.perm_null(y, 400, rng)) < 0.05))
        yr = (rng.random(Dpost.n) < np.where(Dpost.same_true, r_same, r_opp)).astype(float)
        hits_r.append(bool(yr.sum() > 0 and L.p_upper(Dpost.stat(yr), Dpost.perm_null(yr, 400, rng)) < 0.05))
    p0 = float(np.prod(np.where(Dpost.same_true, 1 - r_same, 1 - r_opp)))
    return {"power_model": float(np.mean(hits_m)), "power_rates": float(np.mean(hits_r)), "expected_flags_model": float(np.mean(nflags_m)),
            "expected_flags_rates": float(np.sum(np.where(Dpost.same_true, r_same, r_opp))), "p_zero_flags_if_rates_persist": p0}


# ============================================================================================ carry-over
def carry(df, debates, rng):
    """Replies outside debate phases between two debaters of the most recent completed debate (B after its verdict)."""
    deb_sorted = sorted(debates, key=lambda d: d["t_verdict"])
    out_rows = []
    X = df.filter(~pl.col("phase").is_in(["pre", "deb", "post"]))
    for x in X.iter_rows(named=True):
        prev = [d for d in deb_sorted if d["t_verdict"] <= x["tB_s"]]
        if not prev:
            continue
        d = prev[-1]
        eb, ea = C.team_of(d, x["b_agent"]), C.team_of(d, x["a_agent"])
        if eb == 0 or ea == 0:
            continue
        out_rows.append({**x, "debate": d["debate"]})
    if not out_rows:
        return {"n": 0}
    Dc = Design(pl.DataFrame(out_rows), debates)
    f = Dc.df["f"].to_numpy()
    o = Dc.stat(f)
    nl = Dc.perm_null(f, NPERM, rng)
    return {"n": Dc.n, "n_flags": int(f.sum()), "n_same": int(Dc.same_true.sum()), "n_opp": int((~Dc.same_true).sum()),
            "delta_f": o, "p_team_perm": L.p_upper(o, nl), "n_debates": len(Dc.per_debate(f))}


# ============================================================================================ native within-pair
def within_pair(D, rng):
    f = D.df["f"].to_numpy()

    def contrast(ff):
        acc = {}
        for b, a, v, s in zip(D.b, D.a, ff, D.same_true):
            acc.setdefault((min(b, a), max(b, a)), {True: [], False: []})[bool(s)].append(v)
        c = np.array([np.mean(v[False]) - np.mean(v[True]) for v in acc.values() if v[True] and v[False]])
        return c
    c = contrast(f)
    flips = np.array([np.mean(c * rng.choice([-1, 1], len(c))) for _ in range(NPERM)]) if len(c) else np.array([])
    nl = noise_null(D, f, lambda y: float(np.mean(contrast(y))) if len(c) else np.nan, rng)
    return {"n_pairs": int(len(c)), "mean_c": float(c.mean()) if len(c) else None, "positive": int((c > 0).sum()),
            "negative": int((c < 0).sum()), "zero": int((c == 0).sum()),
            "p_signflip_upper": L.p_upper(c.mean(), flips) if len(c) else None,
            "p_af_upper": N.pval(float(c.mean()), nl) if len(c) else None}


# ============================================================================================ negative controls
def codes(r):
    ags = sorted(set(r["b_agent"].to_list()) | set(r["a_agent"].to_list()))
    pos = {x: k for k, x in enumerate(ags)}
    return ags, np.array([pos[x] for x in r["b_agent"]]), np.array([pos[x] for x in r["a_agent"]])


def corrected_rate(f, clusters, rng, nboot=None, ctx="pop"):
    nboot = nboot or NBOOT
    dr = N.draws(nboot, rng, ctx)
    uc = np.unique(clusters)
    pos = {c: np.flatnonzero(clusters == c) for c in uc}
    pt = np.mean([N.rogan_gladen(f.mean(), R, phi) for _, R, phi in dr[:K_DRAWS]])
    bs = []
    for k in range(nboot):
        ix = np.concatenate([pos[c] for c in rng.choice(uc, len(uc))])
        bs.append(N.rogan_gladen(f[ix].mean(), dr[k, 1], dr[k, 2]))
    return float(pt), np.array(bs)


def camps_33(rng):
    r = load_v2(33)
    ags, spk, tgt = codes(r)
    n = len(ags)
    f = r["f"].to_numpy()

    def camp(ff):
        S = np.zeros((n, n)); Nn = np.zeros((n, n))
        for i, j, v in zip(spk, tgt, ff):
            S[i, j] -= v; S[j, i] -= v; Nn[i, j] += 1; Nn[j, i] += 1
        J = np.where(Nn >= 3, S / np.where(Nn > 0, Nn, 1), np.nan)
        np.fill_diagonal(J, np.nan)
        M = J.copy()
        for _ in range(20):
            rm = np.nanmean(M, 1, keepdims=True); rm[~np.isfinite(rm)] = 0; M = M - rm
            cm = np.nanmean(M, 0, keepdims=True); cm[~np.isfinite(cm)] = 0; M = M - cm
        M = (M + M.T) / 2
        iu = np.triu_indices(n, 1); v = M[iu]; ok = np.isfinite(v)
        tot = np.abs(v[ok]).sum()
        if tot == 0:
            return np.nan
        best = -np.inf
        for bits in range(2 ** (n - 1)):
            xi = np.array([1] + [1 if (bits >> k) & 1 else -1 for k in range(n - 1)])
            best = max(best, (v[ok] * xi[iu[0]][ok] * xi[iu[1]][ok]).sum())
        return float((best + tot) / (2 * tot))
    obs = camp(f)

    class _D:
        pass
    Dd = _D(); Dd.spk, Dd.tgt, Dd.NA = spk, tgt, n
    nl = noise_null(Dd, f, camp, rng, K=10, M=20)
    return {"n_agents": n, "n_replies": r.height, "n_flags": int(f.sum()), "camp_score": obs,
            "null_mean": float(np.nanmean(nl)), "null_q95": float(np.nanquantile(nl, 0.95)), "p": N.pval(obs, nl)}


def controls(D12, rng):
    f12 = D12.df["f"].to_numpy()
    opp = ~D12.same_true
    pt12, bs12 = corrected_rate(f12[opp], D12.deb[opp], rng)
    out = {"g12_opp_corrected": pt12, "g12_opp_ci95": np.quantile(bs12, [0.025, 0.975]).tolist()}
    pts, bss = corrected_rate(f12[~opp], D12.deb[~opp], rng)
    out["g12_same_corrected"] = pts; out["g12_same_ci95"] = np.quantile(bss, [0.025, 0.975]).tolist()
    for g in (33, 26):
        r = load_v2(g)
        f = r["f"].to_numpy()
        pt, bs = corrected_rate(f, np.array(r["pt_date"].to_list()), rng)
        m = min(len(bs), len(bs12))
        out[f"g{g}"] = {"n": r.height, "n_flags": int(f.sum()), "obs_rate": float(f.mean()), "corrected": pt,
                        "ci95": np.quantile(bs, [0.025, 0.975]).tolist(),
                        "diff_vs_g12_opp_ci95": np.quantile(bs12[:m] - bs[:m], [0.025, 0.975]).tolist(),
                        "dq2_opposes_share": float(r["dq2_opp"].cast(pl.Float64).mean())}
    out["g33_camps"] = camps_33(rng)
    return out


# ============================================================================================ main
def gt_check():
    import r1b
    return r1b.gt_check()


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(RNG)
    res = {"gt_check": gt_check()}
    st_pl, debates, tz = load_debates()
    df = g12_frame(st_pl, debates, tz)
    res["n_v2_rows_g12"] = df.height
    res["n_flags_g12_all"] = int(df["f"].sum())
    deb = df.filter(pl.col("debaters") & (pl.col("phase") == "deb"))
    Dd = Design(deb, debates)
    res["S1c"] = s1c(Dd, rng, "deb")
    print("S1c", jdump({k: v for k, v in res["S1c"].items() if k != "per_debate"}).replace("\n", " ")[:3000], flush=True)
    res["S2c_flag"] = recovery(Dd, Dd.df["f"].to_numpy(), debates, rng, sign=-1.0)
    res["S2c_soft"] = recovery(Dd, Dd.df["s2_soft"].to_numpy(), debates, rng, sign=+1.0)
    print("S2c", res["S2c_flag"]["recovered"], res["S2c_flag"]["expected"], res["S2c_flag"]["p"], "| soft",
          res["S2c_soft"]["recovered"], res["S2c_soft"]["p"], flush=True)
    post = df.filter(pl.col("debaters") & (pl.col("phase") == "post"))
    Dp = Design(post, debates)
    fp = Dp.df["f"].to_numpy()
    o = Dp.stat(fp)
    per_post = Dp.per_debate(fp)
    common = [d for d in per_post if d in res["S1c"]["per_debate"]]
    res["S3c"] = {"n": Dp.n, "n_flags": int(fp.sum()), "flags_same": int(fp[Dp.same_true].sum()), "flags_opp": int(fp[~Dp.same_true].sum()),
                  "delta_f_post": o, "p_team_perm": L.p_upper(o, Dp.perm_null(fp, NPERM, rng)), "n_debates": len(per_post),
                  "delta_f_deb_same_debates": float(np.mean([res["S1c"]["per_debate"][d] for d in common])) if common else None,
                  "power_if_persisting": post_power(Dd, Dp, rng, reps=200 if FAST else 500),
                  "dhat_post": delta_hat(Dp, fp, rng, "pop", nboot=max(50, NBOOT // 3)) if fp.sum() > 0 else None}
    print("S3c", jdump({k: v for k, v in res["S3c"].items() if k != "dhat_post"}).replace("\n", " "), flush=True)
    pre = df.filter(pl.col("debaters") & (pl.col("phase") == "pre"))
    Dpre = Design(pre, debates)
    fpre = Dpre.df["f"].to_numpy()
    res["pre"] = {"n": Dpre.n, "n_flags": int(fpre.sum()), "delta_f_pre": Dpre.stat(fpre)}
    res["S3c_carry"] = carry(df, debates, rng)
    print("carry", res["S3c_carry"], flush=True)
    res["native_within_pair"] = within_pair(Dd, rng)
    print("within", res["native_within_pair"], flush=True)
    res["controls"] = controls(Dd, rng)
    print("controls", jdump(res["controls"]).replace("\n", " ")[:2000], flush=True)
    r1b = json.loads((ROOT / "data/processed/H21-debate-antiferromagnet/r1b/r1b.json").read_text())
    s = r1b["stance"]
    res["old_r1b"] = {"delta_soft": s["S1_delta_soft"]["delta"], "opposes_share_same": s["opposes_share_same"],
                      "opposes_share_opp": s["opposes_share_opp"], "recovered": s["S2_recovery"]["recovered"],
                      "post_delta": s["S3_post"]["delta_post"], "within_pair": r1b["native_G12"]["stance_soft"]["mean_c"],
                      "within_pair_neg": r1b["native_G12"]["stance_soft"]["negative"], "within_pair_n": r1b["native_G12"]["stance_soft"]["n_pairs"],
                      "n_replies_deb": s["n_replies_deb"]}
    res["settings"] = {"NPERM": NPERM, "K_DRAWS": K_DRAWS, "M_SIM": M_SIM, "NBOOT": NBOOT, "fast": FAST, "q_pop": N.Q_POP,
                       "ppv": [N.PPV_MEAN, N.PPV_SD], "recall": [N.R_MEAN, N.R_SD]}
    res["seconds"] = round(time.time() - t0, 1)
    (OUT / ("r1c_fast.json" if FAST else "r1c.json")).write_text(jdump(res))
    prov = {"built_by": "hypotheses/H21-debate-antiferromagnet/analysis/r1c.py", "git_commit": _git(),
            "inputs": [{"source": "ai-village", "tables": ["shared/reply_stance_v2 (disagree_validated_agent)", "H21 G12 statements + labels",
                                                          "shared/ground_truth_labels (check)"]}],
            "params": res["settings"], "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print("done", res["seconds"])


def _git():
    import subprocess
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


if __name__ == "__main__":
    main()
