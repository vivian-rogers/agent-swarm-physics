"""H37 round 1c (stance v2.1, 2026-10-04): round-1 predictions re-tested with DQ10's validated conflict flag.

Pre-registered in the card ("Round 1c", 22:10 UTC). Pairs: DQ2 candidate pairs in reply_stance_v2 (p_reply >= 0.5,
ledger visibility), agent parents, B != A, non-holdout. Flag: disagree_validated_agent. Ground truth: DQ6
ground_truth_labels (#12 teams and phases, #51 roles per day, #26 ballots). Topic: reply_pairs.cos. Label noise
(precision, recall) enters every null through analysis/labelnoise.py.
  P1c/P2c/P3c/P5c  #12: agent-adjusted flag contrast (two-way FE linear probability), team permutation, noise-aware
                   agent-field null, stress null, true-scale beta-hat; topic covariate and topic AUC; camp recovery;
                   post-verdict contrast
  P6c/P7c/P9c      #51: role-class coefficients (SR, OP, SY, NC vs U; same-lab covariate), role permutation; noise-aware
                   true-scale betas (day bootstrap); excess-disagreement pairs and their enrichment
  P10c             #26: Mantel of pair disagreement vs ballot dissimilarity
  P12c             #40: corrected disagreement rate vs #12 opposite-team; excess pairs vs the null
Usage: uv run python hypotheses/H37-stance-spins/analysis/r1c.py [--fast] [--only 12 51 26 40]
Writes data/processed/H37-stance-spins/r1c/r1c.json (numbers and agent/role codes only; no text).
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
from scipy.stats import fisher_exact, mannwhitneyu, poisson  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import labelnoise as N  # noqa: E402
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H37-stance-spins/r1c"
FAST = "--fast" in sys.argv
NPERM = 2000 if FAST else 10000
K_DRAWS = 20 if FAST else 40
M_SIM = 10 if FAST else 25
NBOOT = 60 if FAST else 200
SEED = 20261004

# H22's pair-class rule for #51 roles (hypotheses/H22-private-goals-spin-glass/scheme/role_relations.py, coded
# 2026-10-04 00:15 UTC), re-implemented here so new code does not import another hypothesis's folder.
CLASS_NAMES = {0: "U", 1: "SR", 2: "OP", 3: "SY", 4: "NC"}
SUPPORT = {"performance coach", "psychologist", "village helper", "village tooler"}
MEDIA = {"twitterati", "youtuber", "substacker", "reporter", "press baron"}
OPPOSED = {frozenset({"prankster", "ethicist"}), frozenset({"prankster", "psychologist"})}
NORM_ENFORCING = {"psychologist", "ethicist", "diplomat", "village helper", "performance coach"}   # round-1 post hoc lead


def pair_class(a, b):
    if a is None or b is None:
        return 0
    if a == b:
        return 1
    if frozenset({a, b}) in OPPOSED:
        return 2
    if a in SUPPORT or b in SUPPORT:
        return 3
    if a in MEDIA and b in MEDIA:
        return 4
    return 0


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


def pv(obs, null, side="greater"):
    return N.pval(obs, null, side)


# ============================================================================================ data
def load_v2(goal):
    r = pl.read_parquet(SH / "reply_stance_v2.parquet").rename({"phase": "lab_phase"})
    r = r.filter((pl.col("goal_no") == goal) & (pl.col("a_kind") == 0) & (pl.col("b_agent") != pl.col("a_agent")) & ~pl.col("holdout"))
    hm = np.array(holdout_mask(r["pt_date"].to_list(), r["goal_no"].to_list()), bool)
    assert not hm.any(), "holdout rows in reply_stance_v2"
    cos = pl.read_parquet(SH / "reply_pairs.parquet", columns=["B_message_id", "A_message_id", "pair_set", "cos"]).filter(
        pl.col("pair_set") == "cand").drop("pair_set").unique(["B_message_id", "A_message_id"])
    t = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t"]).rename({"message_id": "B_message_id", "t": "tB"})
    r = r.join(cos, on=["B_message_id", "A_message_id"], how="left").join(t, on="B_message_id", how="left")
    return r.with_columns(pl.col("disagree_validated_agent").cast(pl.Float64).alias("f"),
                          pl.col("stance2").cast(pl.String).is_in(["correct", "inform"]).alias("ci"),
                          (pl.col("stance2").cast(pl.String) == "disagree").alias("jev_dis"))


def gt(goal):
    return pl.read_parquet(SH / "ground_truth_labels.parquet").filter((pl.col("goal_no") == goal) & pl.col("preferred") & ~pl.col("holdout"))


def g12_debates():
    g = gt(12)
    out = {}
    for u in sorted(set(g.filter(pl.col("label_kind") == "team")["unit"].to_list())):
        d = int(u.split("_")[1])
        t = g.filter((pl.col("label_kind") == "team") & (pl.col("unit") == u))
        ph = g.filter((pl.col("label_kind") == "phase") & (pl.col("unit") == u))
        out[d] = {"team": {int(a): (1 if v == "gov" else -1) for a, v in zip(t["agent"], t["value"]) if v in ("gov", "opp")},
                  "phases": {v: (a, b) for v, a, b in zip(ph["value"], ph["t_valid_from"], ph["t_valid_to"])}}
    return out


def g12_frame():
    r = load_v2(12)
    debs = g12_debates()
    rows = []
    for x in r.iter_rows(named=True):
        deb, phase = -1, "other"
        for d, D in debs.items():
            for ph, (a, b) in D["phases"].items():
                if a <= x["tB"] < b:
                    deb, phase = d, ph
        rel = None
        if deb >= 0:
            tm = debs[deb]["team"]
            if x["b_agent"] in tm and x["a_agent"] in tm:
                rel = "same" if tm[x["b_agent"]] == tm[x["a_agent"]] else "opposite"
        rows.append({**{k: x[k] for k in ("B_message_id", "b_agent", "a_agent", "f", "ci", "jev_dis", "cos", "s2_soft", "p_disagree", "pt_date")},
                     "debate": deb, "phase": phase, "rel": rel})
    return pl.DataFrame(rows), debs


# ============================================================================================ FE linear probability
def design_fe(spk, tgt, N_, extra=None):
    cols = [np.ones(len(spk))] + [(spk == k).astype(float) for k in range(1, N_)] + [(tgt == k).astype(float) for k in range(1, N_)]
    if extra is not None:
        cols += [np.asarray(e, float) for e in extra]
    X = np.column_stack(cols)
    X = X[:, np.abs(X).sum(0) > 0]
    Q, Rr = np.linalg.qr(X)
    keep = np.abs(np.diag(Rr)) > 1e-8
    return Q[:, keep]


def resid(Q, v):
    return v - Q @ (Q.T @ v)


def codes(df):
    ags = sorted(set(df["b_agent"].to_list()) | set(df["a_agent"].to_list()))
    pos = {a: k for k, a in enumerate(ags)}
    return ags, np.array([pos[a] for a in df["b_agent"]]), np.array([pos[a] for a in df["a_agent"]])


def auc(score, lab):
    pos, neg = score[lab], score[~lab]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    return float(mannwhitneyu(pos, neg).statistic / (len(pos) * len(neg)))


class G12:
    """#12 debate-phase (or post) replies between two debaters; opposite-team indicator; team re-draw permutations."""

    def __init__(self, df, debs):
        self.df = df
        self.ags, self.spk, self.tgt = codes(df)
        self.NA = len(self.ags)
        self.deb = df["debate"].to_numpy()
        self.opp = (df["rel"] == "opposite").to_numpy()
        self.Q = design_fe(self.spk, self.tgt, self.NA)
        self.debs = sorted(set(self.deb.tolist()))
        self.team = {d: debs[d]["team"] for d in self.debs}
        self.b = df["b_agent"].to_numpy(); self.a = df["a_agent"].to_numpy()

    def gamma(self, y, x=None, Q=None):
        Q = self.Q if Q is None else Q
        xr = resid(Q, (self.opp if x is None else x).astype(float))
        return float(xr @ resid(Q, y) / (xr @ xr))

    def perm_x(self, n, rng):
        out = np.empty((n, len(self.deb)))
        for k in range(n):
            x = np.zeros(len(self.deb), bool)
            for d in self.debs:
                tm = self.team[d]
                mem = list(tm); lab = rng.permutation([tm[m] for m in mem]); mp = dict(zip(mem, lab))
                ix = self.deb == d
                x[ix] = np.array([mp[b] != mp[a] for b, a in zip(self.b[ix], self.a[ix])])
            out[k] = x
        return out


def g12_tests(rng):
    df, debs = g12_frame()
    out = {"n_rows_g12": df.height, "n_flags_g12": int(df["f"].sum())}
    deb = df.filter((pl.col("phase") == "deb") & pl.col("rel").is_not_null())
    S = G12(deb, debs)
    f = deb["f"].to_numpy()
    g_obs = S.gamma(f)
    PX = S.perm_x(NPERM, rng)
    PXr = PX - (PX @ S.Q) @ S.Q.T
    fr = resid(S.Q, f)
    g_perm = (PXr @ fr) / (PXr * PXr).sum(1)

    def gstat(y):
        return S.gamma(y)
    topic = deb["cos"].to_numpy().astype(float)
    okt = np.isfinite(topic)
    Qc = design_fe(S.spk, S.tgt, S.NA, extra=[np.where(okt, topic, np.nanmean(topic))])
    dr = N.draws(K_DRAWS, rng)
    null_af, null_st, null_g12, null_st_c = [], [], [], []
    grp = S.opp.astype(int)
    nd = ~deb["jev_dis"].to_numpy(); ci = deb["ci"].to_numpy()
    sh = np.array([ci[(grp == k) & nd].mean() for k in (0, 1)])
    for ppv, R, phi in dr:
        par = N.fit(f, S.spk, S.tgt, None, S.NA, R, phi)
        phs = N.stress_phi(phi, grp, sh)
        pars = N.fit(f, S.spk, S.tgt, None, S.NA, R, phs)
        for _ in range(M_SIM):
            null_af.append(gstat(N.simulate(S.spk, S.tgt, None, par, R, phi, rng)))
            ys = N.simulate(S.spk, S.tgt, None, pars, R, phs, rng)
            null_st.append(gstat(ys)); null_st_c.append(S.gamma(ys, Q=Qc))
    for ppv, R, phi in N.draws(K_DRAWS, rng, "g12"):
        par = N.fit(f, S.spk, S.tgt, None, S.NA, R, phi)
        for _ in range(M_SIM):
            null_g12.append(gstat(N.simulate(S.spk, S.tgt, None, par, R, phi, rng)))
    # true-scale beta-hat, debate bootstrap x noise draws
    X = S.opp.astype(float)[:, None]
    drb = N.draws(NBOOT, rng)
    bhat = float(np.mean([N.fit(f, S.spk, S.tgt, X, S.NA, R, phi)["beta"][0] for _, R, phi in dr]))
    bs = []
    for k in range(NBOOT):
        ix = np.concatenate([np.flatnonzero(S.deb == d) for d in rng.choice(S.debs, len(S.debs))])
        if X[ix, 0].min() == X[ix, 0].max():
            continue
        bs.append(N.fit(f[ix], S.spk[ix], S.tgt[ix], X[ix], S.NA, drb[k, 1], drb[k, 2])["beta"][0])
    by_rel = {r: {"n": int((deb["rel"] == r).sum()), "flags": int(deb.filter(pl.col("rel") == r)["f"].sum()),
                  "rate": float(deb.filter(pl.col("rel") == r)["f"].mean()),
                  "corrected": float(np.mean([N.rogan_gladen(deb.filter(pl.col("rel") == r)["f"].mean(), R, phi) for _, R, phi in dr])),
                  "s2_soft": float(deb.filter(pl.col("rel") == r)["s2_soft"].mean()), "topic_cos": float(deb.filter(pl.col("rel") == r)["cos"].mean())}
              for r in ("same", "opposite")}
    out["P1c"] = {"n": deb.height, "by_rel": by_rel, "gamma_f": g_obs, "p_team_perm": pv(g_obs, g_perm),
                  "af_null_q95": float(np.quantile(null_af, 0.95)), "p_af": pv(g_obs, null_af),
                  "stress_ci_share_same_opp": sh.tolist(), "stress_null_mean": float(np.mean(null_st)), "p_stress": pv(g_obs, null_st),
                  "stress_expected_over_obs": float(np.mean(null_st) / g_obs) if g_obs > 0 else None,
                  "p_af_g12noise": pv(g_obs, null_g12), "beta_opp_hat": bhat, "beta_opp_ci95": np.quantile(bs, [0.025, 0.975]).tolist()}
    # Amendment 1c-1 (synthetic, before the real run): team permutation has size 0.09-0.12 under differential false
    # positives, so the stress null takes its place in the decision; the beta-hat interval clause is dropped.
    out["P1c"]["pass"] = bool(g_obs > 0 and out["P1c"]["p_stress"] < 0.01 and g_obs > out["P1c"]["af_null_q95"])
    out["P1c"]["pass_preregistered_form"] = bool(g_obs > 0 and out["P1c"]["p_team_perm"] < 0.01 and g_obs > out["P1c"]["af_null_q95"]
                                                 and out["P1c"]["beta_opp_ci95"][0] > 0)
    # P2c: topic covariate and topic AUC (agent-adjusted)
    g_c = S.gamma(f, Q=Qc)
    PXc = PX - (PX @ Qc) @ Qc.T
    g_cp = (PXc @ resid(Qc, f)) / (PXc * PXc).sum(1)
    rt = resid(S.Q, np.where(okt, topic, np.nanmean(topic)))
    rpd = resid(S.Q, deb["p_disagree"].to_numpy().astype(float))
    rs2 = resid(S.Q, deb["s2_soft"].to_numpy().astype(float))
    out["P2c"] = {"gamma_f_topic_cov": g_c, "p_topic_cov": pv(g_c, g_cp), "p_topic_cov_stress": pv(g_c, null_st_c), "auc_topic_adj": auc(-rt, S.opp),
                  "auc_topic_adj_same_vs_opp": auc(rt, ~S.opp), "auc_p_disagree_adj": auc(rpd, S.opp), "auc_s2_soft_adj_same_vs_opp": auc(rs2, ~S.opp),
                  "topic_missing": int((~okt).sum())}
    out["P2c"]["pass"] = bool(out["P2c"]["p_topic_cov_stress"] < 0.01 and 0.40 <= out["P2c"]["auc_topic_adj_same_vs_opp"] <= 0.60)
    # P3c camp recovery (flag graph; s2_soft secondary)
    out["P3c_flag"] = camp_recovery(S, resid(S.Q, f), -1.0, rng)
    out["P3c_soft"] = camp_recovery(S, resid(S.Q, deb["s2_soft"].to_numpy().astype(float)), +1.0, rng)
    out["P3c_flag"]["pass"] = bool(out["P3c_flag"]["acc"] >= 0.80 and out["P3c_flag"]["p"] < 0.05)
    # P5c post-verdict
    post = df.filter((pl.col("phase") == "post") & pl.col("rel").is_not_null())
    if post.height >= 10 and post["rel"].n_unique() == 2:
        Sp = G12(post, debs)
        fp = post["f"].to_numpy()
        gp = Sp.gamma(fp)
        PXp = Sp.perm_x(NPERM, rng); PXpr = PXp - (PXp @ Sp.Q) @ Sp.Q.T
        gpp = (PXpr @ resid(Sp.Q, fp)) / (PXpr * PXpr).sum(1)
        out["P5c"] = {"n": post.height, "flags": int(fp.sum()), "flags_opp": int(fp[Sp.opp].sum()), "flags_same": int(fp[~Sp.opp].sum()),
                      "gamma_post": gp, "p_post_team_perm": pv(gp, gpp), "gamma_deb": g_obs, "pass": bool(gp < g_obs)}
    # old (round 1, H37 stance-v1) for the old -> new table
    s = json.loads((ROOT / "data/processed/H37-stance-spins/summary.json").read_text())["predictions"]
    out["old_round1"] = {k: s.get(k) for k in ("P1", "P2", "P3", "P5")}
    return out


def camp_recovery(S, r, sign, rng):
    accs, chance_sets, per = [], [], []
    for d in S.debs:
        tm = S.team[d]
        mem = sorted(tm); mp = {a: k for k, a in enumerate(mem)}; n = len(mem)
        ix = np.flatnonzero(S.deb == d)
        M = np.zeros((n, n)); C = np.zeros((n, n))
        for i in ix:
            p, q = mp[S.b[i]], mp[S.a[i]]
            M[p, q] += sign * r[i]; M[q, p] += sign * r[i]; C[p, q] += 1; C[q, p] += 1
        J = np.where(C > 0, M / np.where(C > 0, C, 1), 0.0)
        truth = np.array([tm[a] for a in mem])
        k = int((truth == 1).sum())
        parts = []
        for A in itertools.combinations(range(n), k):
            e = -np.ones(n); e[list(A)] = 1; parts.append(e)
        acc_all = np.array([max((e == truth).mean(), (-e == truth).mean()) if 2 * k == n else (e == truth).mean() for e in parts])
        en = np.array([0.5 * e @ J @ e for e in parts])
        best = np.flatnonzero(np.isclose(en, en.max()))
        a = float(acc_all[best].mean())
        accs.append(a); chance_sets.append(acc_all); per.append({"debate": int(d), "n_replies": int(len(ix)), "acc": a, "chance": float(acc_all.mean())})
    draws = np.mean([rng.choice(c, 20000) for c in chance_sets], 0)
    m = float(np.mean(accs))
    return {"acc": m, "chance": float(draws.mean()), "p": float((1 + np.sum(draws >= m - 1e-12)) / (1 + len(draws))),
            "exact": int(sum(p["acc"] == 1.0 for p in per)), "per_debate": per}


# ============================================================================================ #51
def role_spells():
    from zoneinfo import ZoneInfo
    PT = ZoneInfo("America/Los_Angeles")
    g = gt(51).filter((pl.col("label_kind") == "role") & pl.col("value").is_not_null()).sort("t_valid_from")
    ptd = lambda x: x.astimezone(PT).date().isoformat() if x is not None else None
    return [(int(a), str(v).strip().lower(), ptd(f), ptd(t)) for a, v, f, t in g.select("agent", "value", "t_valid_from", "t_valid_to").iter_rows()]


def role_on(spells, agent, day):
    best = None
    for a, role, s, e in spells:
        if a == agent and s is not None and s <= day and (e is None or day <= e):
            best = role
    return best


def g51_frame():
    r = load_v2(51)
    sp = role_spells()
    days = {}
    for b, a, d in zip(r["b_agent"], r["a_agent"], r["pt_date"]):
        days.setdefault(b, set()).add(d); days.setdefault(a, set()).add(d)
    maj = {}
    for ag, ds in days.items():
        rs = [role_on(sp, ag, d) for d in sorted(ds)]
        known = [x for x in rs if x is not None]
        if known and len(known) * 2 >= len(rs):
            v, c = np.unique(known, return_counts=True)
            maj[ag] = str(v[np.argmax(c)])
        else:
            maj[ag] = None
    day_cls = [pair_class(role_on(sp, b, d), role_on(sp, a, d)) for b, a, d in zip(r["b_agent"], r["a_agent"], r["pt_date"])]
    r = r.with_columns(pl.Series("cls_day", day_cls, pl.Int8))
    r = r.filter(pl.col("b_agent").replace_strict(maj, default=None).is_not_null() & pl.col("a_agent").replace_strict(maj, default=None).is_not_null())
    lab = dict(pl.read_parquet(SH / "roster.parquet", columns=["agent", "lab"]).iter_rows())
    r = r.with_columns((pl.col("b_agent").replace_strict(lab, default=None) == pl.col("a_agent").replace_strict(lab, default=None)).alias("same_lab"))
    return r, maj


class G51:
    def __init__(self, df, maj):
        self.df = df
        self.ags, self.spk, self.tgt = codes(df)
        self.NA = len(self.ags)
        self.roles = sorted({maj[a] for a in self.ags})
        self.role_idx = np.array([self.roles.index(maj[a]) for a in self.ags])
        R = len(self.roles)
        self.lookup = np.array([[pair_class(self.roles[x], self.roles[y]) for y in range(R)] for x in range(R)])
        self.lab = df["same_lab"].to_numpy().astype(float)
        self.Q = design_fe(self.spk, self.tgt, self.NA, extra=[self.lab])

    def classes(self, role_idx=None):
        ri = self.role_idx if role_idx is None else role_idx
        return self.lookup[ri[self.spk], ri[self.tgt]]

    def betas(self, y, cls=None, Q=None):
        Q = self.Q if Q is None else Q
        c = self.classes() if cls is None else cls
        X = np.column_stack([(c == k).astype(float) for k in (1, 2, 3, 4)])
        Xr = X - Q @ (Q.T @ X)
        yr = resid(Q, y)
        A = Xr.T @ Xr
        ok = np.diag(A) > 1e-9
        b = np.full(4, np.nan)
        if ok.any():
            b[ok] = np.linalg.solve(A[np.ix_(ok, ok)], Xr[:, ok].T @ yr)
        return b

    def perm(self, y, n, rng, Q=None):
        out = np.empty((n, 4))
        holders = np.arange(self.NA)
        for k in range(n):
            ri = self.role_idx.copy(); ri[holders] = rng.permutation(self.role_idx[holders])
            out[k] = self.betas(y, self.classes(ri), Q)
        return out


def excess_pairs(spk, tgt, days, f, P):
    """Unordered pairs with >= 2 flags on >= 2 distinct days and Poisson upper-tail p < 0.01 given expected flag
    probabilities P (noise-aware agent-field model)."""
    key = np.minimum(spk, tgt) * 1000 + np.maximum(spk, tgt)
    out = []
    for k in np.unique(key):
        m = key == k
        K = f[m].sum()
        if K < 2 or len(set(days[m][f[m] == 1])) < 2:
            continue
        p = poisson.sf(K - 1, P[m].sum())
        if p < 0.01:
            out.append(int(k))
    return out


def g51_tests(rng):
    df, maj = g51_frame()
    S = G51(df, maj)
    f = df["f"].to_numpy()
    cls = S.classes()
    out = {"n": df.height, "n_agents": S.NA, "n_flags": int(f.sum()), "roles": {int(a): maj[a] for a in S.ags},
           "class_counts": {CLASS_NAMES[k]: int((cls == k).sum()) for k in range(5)},
           "class_flags": {CLASS_NAMES[k]: int(f[cls == k].sum()) for k in range(5)},
           "class_rates": {CLASS_NAMES[k]: float(f[cls == k].mean()) if (cls == k).any() else None for k in range(5)},
           "n_unordered_pairs_by_class": {}}
    key = np.minimum(S.spk, S.tgt) * 1000 + np.maximum(S.spk, S.tgt)
    for k in range(5):
        out["n_unordered_pairs_by_class"][CLASS_NAMES[k]] = int(len(np.unique(key[cls == k])))
    b_obs = S.betas(f)
    bp = S.perm(f, NPERM, rng)
    out["beta_lp"] = {CLASS_NAMES[k + 1]: float(b_obs[k]) for k in range(4)}
    out["p_upper_role_perm"] = {CLASS_NAMES[k + 1]: pv(b_obs[k], bp[:, k]) for k in range(4)}
    out["p_lower_role_perm"] = {CLASS_NAMES[k + 1]: pv(b_obs[k], bp[:, k], "less") for k in range(4)}
    # per-day classes (robustness)
    b_day = S.betas(f, df["cls_day"].to_numpy())
    out["beta_lp_dayclass"] = {CLASS_NAMES[k + 1]: float(b_day[k]) for k in range(4)}
    # topic on the same pairs (round-1 P7 dissociation clause)
    topic = df["cos"].to_numpy().astype(float)
    tt = np.where(np.isfinite(topic), topic, np.nanmean(topic))
    bt = S.betas(tt); btp = S.perm(tt, min(NPERM, 2000), rng)
    out["topic_beta"] = {CLASS_NAMES[k + 1]: float(bt[k]) for k in range(4)}
    out["topic_p_upper"] = {CLASS_NAMES[k + 1]: pv(bt[k], btp[:, k]) for k in range(4)}
    # soft (unvalidated) p_disagree
    pd_ = df["p_disagree"].to_numpy().astype(float)
    bs_ = S.betas(pd_); bsp = S.perm(pd_, min(NPERM, 2000), rng)
    out["p_disagree_beta"] = {CLASS_NAMES[k + 1]: float(bs_[k]) for k in range(4)}
    out["p_disagree_p_upper"] = {CLASS_NAMES[k + 1]: pv(bs_[k], bsp[:, k]) for k in range(4)}
    # noise-aware true-scale betas (class indicators + same lab), day bootstrap x noise draws
    X = np.column_stack([(cls == k).astype(float) for k in (1, 2, 3, 4)] + [S.lab])
    dr = N.draws(max(NBOOT, K_DRAWS), rng)
    pts = np.array([N.fit(f, S.spk, S.tgt, X, S.NA, R, phi)["beta"][:4] for _, R, phi in dr[:min(K_DRAWS, 10)]])
    days = np.array(df["pt_date"].to_list())
    ud = np.unique(days); pos = {d: np.flatnonzero(days == d) for d in ud}
    bs = []
    for k in range(NBOOT // 2):
        ix = np.concatenate([pos[d] for d in rng.choice(ud, len(ud))])
        bs.append(N.fit(f[ix], S.spk[ix], S.tgt[ix], X[ix], S.NA, dr[k, 1], dr[k, 2])["beta"][:4])
    bs = np.array(bs)
    out["beta_true"] = {CLASS_NAMES[k + 1]: float(pts[:, k].mean()) for k in range(4)}
    out["beta_true_ci95"] = {CLASS_NAMES[k + 1]: np.quantile(bs[:, k], [0.025, 0.975]).tolist() for k in range(4)}
    # stress null for SR/OP: fp rate by class proportional to its Jev correct+inform share
    nd = ~df["jev_dis"].to_numpy(); ci = df["ci"].to_numpy()
    sh = np.array([ci[(cls == k) & nd].mean() if ((cls == k) & nd).any() else np.nan for k in range(5)])
    sh = np.where(np.isfinite(sh), sh, np.nanmean(sh))
    out["ci_share_by_class"] = {CLASS_NAMES[k]: float(sh[k]) for k in range(5)}
    nul_st, nul_af, n_exc_null = [], [], []
    dr2 = N.draws(10 if not FAST else 5, rng)
    for _, R, phi in dr2:
        par = N.fit(f, S.spk, S.tgt, X[:, 4:], S.NA, R, phi)          # agent fields + same lab, no class terms
        phs = N.stress_phi(phi, cls, sh)
        pars = N.fit(f, S.spk, S.tgt, X[:, 4:], S.NA, R, phs)
        for _ in range(10):
            ys = N.simulate(S.spk, S.tgt, X[:, 4:], pars, R, phs, rng)
            nul_st.append(S.betas(ys))
            ya = N.simulate(S.spk, S.tgt, X[:, 4:], par, R, phi, rng)
            nul_af.append(S.betas(ya))
            Pa = phi + (R - phi) * N.true_prob(S.spk, S.tgt, X[:, 4:], par)
            n_exc_null.append(len(excess_pairs(S.spk, S.tgt, days, ya, Pa)))
    nul_st, nul_af = np.array(nul_st), np.array(nul_af)
    out["stress_null_mean"] = {CLASS_NAMES[k + 1]: float(np.nanmean(nul_st[:, k])) for k in range(4)}
    out["p_upper_stress"] = {CLASS_NAMES[k + 1]: pv(b_obs[k], nul_st[:, k]) for k in range(4)}
    out["p_upper_af_noise"] = {CLASS_NAMES[k + 1]: pv(b_obs[k], nul_af[:, k]) for k in range(4)}
    for c in ("OP", "SR"):
        tag = "P6c" if c == "OP" else "P7c"
        out[tag] = {"beta_lp": out["beta_lp"][c], "p_upper": out["p_upper_role_perm"][c], "beta_true": out["beta_true"][c],
                    "beta_true_ci95": out["beta_true_ci95"][c], "n_rows": out["class_counts"][c], "n_flags": out["class_flags"][c],
                    "n_pairs": out["n_unordered_pairs_by_class"][c],
                    "pass": bool(out["beta_lp"][c] > 0 and out["p_upper_role_perm"][c] < 0.05)}
    # P9c excess-disagreement pairs, enrichment in SR u OP u NC
    _, R0, phi0 = N.R_MEAN, N.R_MEAN, N.phi_from(N.Q_POP, N.PPV_MEAN, N.R_MEAN)
    par0 = N.fit(f, S.spk, S.tgt, X[:, 4:], S.NA, R0, phi0)
    P0 = phi0 + (R0 - phi0) * N.true_prob(S.spk, S.tgt, X[:, 4:], par0)
    exc = excess_pairs(S.spk, S.tgt, days, f, P0)
    pair_cls = {}
    for k_, c_ in zip(key, cls):
        pair_cls.setdefault(int(k_), c_)
    cnt = {int(k_): int((key == k_).sum()) for k_ in np.unique(key)}
    tested = [k_ for k_ in pair_cls if cnt[k_] >= 3]
    conflict = {k_ for k_ in tested if pair_cls[k_] in (1, 2, 4)}
    es = set(exc) & set(tested)
    a_ = len(es & conflict); b_ = len(es - conflict); c_ = len(conflict - es); d_ = len(tested) - a_ - b_ - c_
    orr, pf = fisher_exact([[a_, b_], [c_, d_]], alternative="greater") if (a_ + b_) > 0 else (np.nan, 1.0)

    def roles_of(k_):
        i, j = k_ // 1000, k_ % 1000
        return sorted([maj[S.ags[i]], maj[S.ags[j]]])
    norm = sum(1 for k_ in exc if any(r_ in NORM_ENFORCING for r_ in roles_of(k_)))
    norm_tested = sum(1 for k_ in tested if any(r_ in NORM_ENFORCING for r_ in roles_of(k_)))
    out["P9c"] = {"n_excess": len(exc), "n_excess_null_mean": float(np.mean(n_exc_null)), "n_excess_null_q95": float(np.quantile(n_exc_null, 0.95)),
                  "p_excess_count": pv(len(exc), n_exc_null), "n_tested_pairs": len(tested), "n_conflict_tested": len(conflict),
                  "n_excess_conflict": a_, "odds_ratio": float(orr) if np.isfinite(orr) else None, "p_fisher": float(pf),
                  "excess_pairs": [{"agents": [int(S.ags[k_ // 1000]), int(S.ags[k_ % 1000])], "roles": roles_of(k_), "cls": CLASS_NAMES[int(pair_cls[k_])]}
                                   for k_ in exc],
                  "norm_enforcing_excess": norm, "norm_enforcing_share_tested": norm_tested / max(1, len(tested)),
                  "pass": bool((orr if np.isfinite(orr) else 0) >= 2 and pf < 0.05)}
    return out


# ============================================================================================ #26
def g26_struct():
    r = load_v2(26)
    g = gt(26)
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "agent"]).rename({"agent": "voter"})
    b = g.filter((pl.col("label_kind") == "ballot") & (pl.col("unit") == "approval")).with_columns(
        pl.col("source_ref").str.replace("chat_core:message_id=", "").alias("mid")).join(cc, left_on="mid", right_on="message_id", how="left")
    appr = {}
    for v, c in zip(b["voter"], b["agent_b"]):
        if v is not None:
            appr.setdefault(int(v), set()).add(int(c))
    voters = sorted(appr)
    n = len(voters)
    Dm = np.zeros((n, n))
    for i, j in itertools.combinations(range(n), 2):
        A, B = appr[voters[i]], appr[voters[j]]
        Dm[i, j] = Dm[j, i] = 1 - len(A & B) / len(A | B)
    rv = r.filter(pl.col("b_agent").is_in(voters) & pl.col("a_agent").is_in(voters))
    pos = {a: k for k, a in enumerate(voters)}
    spk = np.array([pos[x] for x in rv["b_agent"]]); tgt = np.array([pos[x] for x in rv["a_agent"]])
    return rv, voters, Dm, spk, tgt


def g26_pairmat(spk, tgt, ff, n):
    S = np.zeros((n, n)); C = np.zeros((n, n))
    for i, j, v in zip(spk, tgt, ff):
        S[i, j] += v; S[j, i] += v; C[i, j] += 1; C[j, i] += 1
    return np.where(C >= 2, S / np.where(C > 0, C, 1), np.nan)


def g26_mantel(M, Dm, n_perm, rng):
    n = len(Dm)
    iu = np.triu_indices(n, 1)
    a, bb = M[iu], Dm[iu]
    ok = np.isfinite(a)
    if ok.sum() < 5 or np.std(a[ok]) == 0:
        return np.nan, np.nan
    r_ = np.corrcoef(a[ok], bb[ok])[0, 1]
    nl = []
    for _ in range(n_perm):
        p = rng.permutation(n)
        bp = Dm[np.ix_(p, p)][iu]
        nl.append(np.corrcoef(a[ok], bp[ok])[0, 1])
    return float(r_), pv(r_, np.array(nl))


def g26_tests(rng):
    rv, voters, Dm, spk, tgt = g26_struct()
    n = len(voters)
    f = rv["f"].to_numpy()
    M = g26_pairmat(spk, tgt, f, n)
    r_, p_ = g26_mantel(M, Dm, 5000, rng)
    return {"n_voters": n, "n_replies": rv.height, "n_flags": int(f.sum()), "n_pairs_ge2": int(np.isfinite(M[np.triu_indices(n, 1)]).sum()),
            "mantel_r": r_, "p_greater": p_, "pass": bool(np.isfinite(r_) and r_ > 0 and p_ < 0.05)}




# ============================================================================================ #40
def corrected(f, clusters, rng, nboot=None):
    nboot = nboot or NBOOT
    dr = N.draws(nboot, rng)
    uc = np.unique(clusters); pos = {c: np.flatnonzero(clusters == c) for c in uc}
    pt = float(np.mean([N.rogan_gladen(f.mean(), R, phi) for _, R, phi in dr[:K_DRAWS]]))
    bs = np.array([N.rogan_gladen(f[np.concatenate([pos[c] for c in rng.choice(uc, len(uc))])].mean(), dr[k, 1], dr[k, 2]) for k in range(nboot)])
    return pt, bs


def g40_tests(rng, g12_opp):
    r = load_v2(40)
    f = r["f"].to_numpy()
    days = np.array(r["pt_date"].to_list())
    pt, bs = corrected(f, days, rng)
    f12, d12 = g12_opp
    pt12, bs12 = corrected(f12, d12, rng)
    ags, spk, tgt = codes(r)
    R0, phi0 = N.R_MEAN, N.phi_from(N.Q_POP, N.PPV_MEAN, N.R_MEAN)
    par0 = N.fit(f, spk, tgt, None, len(ags), R0, phi0)
    P0 = phi0 + (R0 - phi0) * N.true_prob(spk, tgt, None, par0)
    exc = excess_pairs(spk, tgt, days, f, P0)
    nl = []
    for _, R, phi in N.draws(10, rng):
        par = N.fit(f, spk, tgt, None, len(ags), R, phi)
        Pp = phi + (R - phi) * N.true_prob(spk, tgt, None, par)
        for _ in range(20):
            nl.append(len(excess_pairs(spk, tgt, days, N.simulate(spk, tgt, None, par, R, phi, rng), Pp)))
    ratio = bs / np.where(bs12 > 0, bs12, np.nan)
    out = {"n": r.height, "n_flags": int(f.sum()), "obs_rate": float(f.mean()), "corrected": pt, "ci95": np.quantile(bs, [0.025, 0.975]).tolist(),
           "g12_opp_corrected": pt12, "g12_opp_ci95": np.quantile(bs12, [0.025, 0.975]).tolist(),
           "ratio_to_g12_opp": pt / pt12 if pt12 > 0 else None, "ratio_ci95": np.nanquantile(ratio, [0.025, 0.975]).tolist(),
           "n_excess_pairs": len(exc), "excess_null_mean": float(np.mean(nl)), "excess_null_q95": float(np.quantile(nl, 0.95)),
           "dq2_opposes_share": float((r["dq2_stance"].cast(pl.String) == "opposes").mean())}
    out["pass"] = bool(pt <= 0.5 * pt12 and len(exc) <= max(0, int(np.ceil(out["excess_null_q95"]))))
    return out


# ============================================================================================ main
def holm(ps):
    names = [k for k in ps if ps[k] is not None and np.isfinite(ps[k])]
    p = np.array([ps[k] for k in names]); o = np.argsort(p); m = len(p)
    adj = np.empty(m); run = 0
    for r_, k in enumerate(o):
        run = max(run, min(1, (m - r_) * p[k])); adj[k] = run
    return {nm: float(a) for nm, a in zip(names, adj)}


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else ["12", "51", "26", "40"]
    fn = OUT / ("r1c_fast.json" if FAST else "r1c.json")
    res = json.loads(fn.read_text()) if fn.exists() else {}
    rng = np.random.default_rng(SEED)
    if "12" in only:
        res["G12"] = g12_tests(rng)
        print("G12", jdump({k: v for k, v in res["G12"].items() if not k.startswith("P3c")}).replace("\n", " ")[:3500], flush=True)
    if "51" in only:
        res["G51"] = g51_tests(rng)
        print("G51", jdump({k: v for k, v in res["G51"].items() if k not in ("roles",)}).replace("\n", " ")[:4000], flush=True)
    if "26" in only:
        res["G26"] = g26_tests(rng)
        print("G26", jdump({k: v for k, v in res["G26"].items()}).replace("\n", " "), flush=True)
    if "40" in only:
        df, debs = g12_frame()
        d12 = df.filter((pl.col("phase") == "deb") & (pl.col("rel") == "opposite"))
        res["G40"] = g40_tests(rng, (d12["f"].to_numpy(), d12["debate"].to_numpy()))
        print("G40", jdump(res["G40"]).replace("\n", " "), flush=True)
    ps = {"P1c": res.get("G12", {}).get("P1c", {}).get("p_stress"), "P2c": res.get("G12", {}).get("P2c", {}).get("p_topic_cov_stress"),
          "P3c": res.get("G12", {}).get("P3c_flag", {}).get("p"), "P6c": res.get("G51", {}).get("P6c", {}).get("p_upper"),
          "P7c": res.get("G51", {}).get("P7c", {}).get("p_upper"), "P10c": res.get("G26", {}).get("p_greater")}
    res["holm"] = holm(ps)
    res["settings"] = {"NPERM": NPERM, "K_DRAWS": K_DRAWS, "M_SIM": M_SIM, "NBOOT": NBOOT, "fast": FAST, "seed": SEED}
    res["seconds_last"] = round(time.time() - t0, 1)
    fn.write_text(jdump(res))
    prov_path = ROOT / "data/processed/H37-stance-spins/_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    import subprocess
    try:
        gc = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        gc = None
    prov["r1c"] = {"built_by": "hypotheses/H37-stance-spins/analysis/r1c.py", "git_commit": gc,
                   "inputs": [{"source": "ai-village", "tables": ["shared/reply_stance_v2", "shared/reply_pairs (cos)", "shared/ground_truth_labels",
                                                                 "shared/chat_core", "shared/roster"]}],
                   "params": res["settings"], "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1, default=str))
    print("holm", res["holm"], "done", res["seconds_last"])


if __name__ == "__main__":
    main()
