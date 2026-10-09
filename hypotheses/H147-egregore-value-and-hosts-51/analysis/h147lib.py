"""H147 estimators: wipe value and information of a pattern (O1), hub-loss beta (O2), operator-action prevalence
change (O3), host relation (O4). Pattern-agnostic: every function takes element `hits` (agent, t) for one pattern
K (or one frequency-matched pseudo-pattern), so the same code runs on H145's memeplexes, on the qualitative
candidate patterns, and on synthetic patterns.

Inputs (data/processed/H147-egregore-value-and-hosts-51/, scheme/build.py): events_fp, panel, stmt_align,
scramble_events.json, placebo_days. Reserved 51m is absent from all of them (asserted in Skeleton).

Definitions (card + Amendments A1-A3, Round 1, 2026-10-09):
  host of K in bin b   >= m distinct K elements expressed by the agent in b (m = 2), present agent-bins only (H145)
  current host         host of K in the bin before the event's bin (b_e - 1)
  windows              pre = calls -20..-1, post = calls 1..20 of the agent (H70 / H58 R3 windows; F = forced erasure,
                       P = call 21 of a segment of >= 40 calls)
  dV_K,F (A1)          exp(b_rate) - 1: the F effect on the wiped host's own K hits per element event in calls 1..20
                       (Poisson, stratum FE, offset log own element events; covariate: own K share in -20..-1)
  b_oth                the others' K share in the host's window per unit dose pi (the host's share of K hits in b_e - 1)
  variants (card)      b_dose (all K hits ~ F * pi), b_own (own K hits ~ F), count based
  I_K,F                I_P - I_F, I = MI_MM(own post level; own pre level) - within-stratum permutation floor, levels =
                       min(hits, 2), on all events of K's candidate hosts (agents that hosted K in >= 1 bin)
  host relation (A2)   within agent (agent x day-part FE, agent trend), activity held (log1p statements, log1p
                       non-pause calls); commits exp(b) - 1, alignment b / mean(non-hosting); class by the card's rule
                       with each component's CI excluding 0 in its direction
  dated events (A3)    beta and prevalence change against any-weekday placebo days (same weekday: variant)
  excess               every statistic minus the median over frequency-matched pseudo-patterns (card null)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h147common as C  # noqa: E402
import semantic_kappa as SK  # noqa: E402  (infra/shared)

M_HOST = 2


# ================================================================================================ skeleton
@dataclass
class Skeleton:
    ev: pl.DataFrame          # F / P events
    panel: pl.DataFrame       # agent x bin
    stm: pl.DataFrame         # statements (srow, agent, t, bin, alignment)
    bins: pl.DataFrame
    sev: dict                 # scramble events
    pdays: pl.DataFrame       # placebo days

    # numpy views
    def __post_init__(self):
        e = self.ev
        self.e_agent = e["agent"].to_numpy().astype(np.int16)
        self.e_t = e["t"].dt.epoch("us").to_numpy()
        self.e_post = e["t_post_end"].to_numpy()
        self.e_pre = e["t_pre_start"].to_numpy()
        self.e_F = (e["etype"] == "F").to_numpy()
        self.e_stratum = e["stratum"].to_numpy()
        self.e_cluster = e["cluster"].to_numpy()
        self.e_dur = np.maximum((self.e_post - self.e_t) / 6e7, 0.5)
        self.e_bin = e["bin"].fill_null(-1).to_numpy().astype(np.int32)
        self.e_stmt_post = e["stmt_post20"].to_numpy().astype(float)
        self.e_work_post = e["n_work_post20"].to_numpy().astype(float)
        self.n_bins = int(self.bins["bin"].max()) + 1
        self.agents = np.array(sorted(self.panel["agent"].unique().to_list()), dtype=np.int16)
        self.a_index = {int(a): i for i, a in enumerate(self.agents)}
        self.bin_t0 = self.bins["t0"].dt.epoch("us").to_numpy()
        pr = self.panel.select("agent", "bin", "present")
        self.present = np.zeros((len(self.agents), self.n_bins), bool)
        ai = np.array([self.a_index[int(a)] for a in pr["agent"].to_list()])
        self.present[ai, pr["bin"].to_numpy()] = pr["present"].to_numpy()


def set_base(sk: Skeleton, agent, t):
    """Base expression counts for the rate forms (Amendment A1): every element event of every agent (real data: all
    H145 element events; synthetic: all statements), counted in each F / P event's windows."""
    o = np.argsort(np.asarray(t, np.int64), kind="stable")
    hb = Hits(np.asarray(agent)[o], np.asarray(t, np.int64)[o], np.zeros(len(o), np.int32), np.full(len(o), -1, np.int32))
    sk.base_own_post = hb.count_own(sk.e_agent, sk.e_t, sk.e_post).astype(float)
    sk.base_own_pre = hb.count_own(sk.e_agent, sk.e_pre, sk.e_t).astype(float)
    sk.base_oth_post = hb.count_all(sk.e_t, sk.e_post).astype(float) - sk.base_own_post
    sk.base_oth_pre = hb.count_all(sk.e_pre, sk.e_t).astype(float) - sk.base_own_pre
    return sk


def load_skeleton() -> Skeleton:
    O = C.OUT
    ev = pl.read_parquet(O / "events_fp.parquet")
    panel = pl.read_parquet(O / "panel.parquet")
    stm = pl.read_parquet(O / "stmt_align.parquet")
    for df in (ev, panel, stm):
        assert df["pt_date"].max() <= C.LAST, "reserved data present"
    sev = json.loads((O / "scramble_events.json").read_text())
    pdays = pl.read_parquet(O / "placebo_days.parquet")
    return Skeleton(ev=ev, panel=panel, stm=stm, bins=C.bins(), sev=sev, pdays=pdays)


# ================================================================================================ hit counting
class Hits:
    """Element hits of one pattern: agent (int), t (epoch us), e (element id), bin. Sorted by time."""

    def __init__(self, agent, t, e, bin_):
        o = np.argsort(t, kind="stable")
        self.agent = np.asarray(agent, np.int16)[o]
        self.t = np.asarray(t, np.int64)[o]
        self.e = np.asarray(e, np.int32)[o]
        self.bin = np.asarray(bin_, np.int32)[o]
        self._by_agent = {}
        for a in np.unique(self.agent):
            self._by_agent[int(a)] = self.t[self.agent == a]

    def __len__(self):
        return len(self.t)

    def count_all(self, lo, hi):
        return np.searchsorted(self.t, hi, "left") - np.searchsorted(self.t, lo, "left")

    def count_own(self, agents, lo, hi):
        out = np.zeros(len(agents), np.int64)
        for a in np.unique(agents):
            ta = self._by_agent.get(int(a))
            if ta is None:
                continue
            m = agents == a
            out[m] = np.searchsorted(ta, hi[m], "left") - np.searchsorted(ta, lo[m], "left")
        return out

    def bin_tables(self, sk: Skeleton):
        """(hits per agent x bin, distinct elements per agent x bin) as dense arrays [n_agents, n_bins]."""
        na, nb = len(sk.agents), sk.n_bins
        ai = np.array([sk.a_index.get(int(a), -1) for a in self.agent])
        ok = ai >= 0
        H = np.zeros((na, nb), np.int32)
        np.add.at(H, (ai[ok], self.bin[ok]), 1)
        # distinct elements: unique (agent, bin, e) triples
        key = (ai[ok].astype(np.int64) * nb + self.bin[ok]) * 1_000_003 + self.e[ok]
        u = np.unique(key)
        ab = u // 1_000_003
        D = np.zeros(na * nb, np.int32)
        np.add.at(D, ab, 1)
        return H, D.reshape(na, nb)


# ================================================================================================ O1: wipes
def wipe_frame(sk: Skeleton, hits: Hits, m: int = M_HOST) -> dict:
    """Per-event quantities for one pattern (numpy dict over all F / P events)."""
    H, D = hits.bin_tables(sk)
    ai = np.array([sk.a_index.get(int(a), -1) for a in sk.e_agent])
    okb = (sk.e_bin > 0) & (ai >= 0)
    prev = np.where(okb, sk.e_bin - 1, 0)
    aic = np.where(ai >= 0, ai, 0)
    host_prev = okb & (D[aic, prev] >= m) & sk.present[aic, prev]
    tot_prev = H[:, prev].sum(0)
    pi = np.where(okb & (tot_prev > 0), H[aic, prev] / np.maximum(tot_prev, 1), 0.0)
    cand = (ai >= 0) & ((D >= m) & sk.present).any(1)[aic]
    V = hits.count_all(sk.e_t, sk.e_post)
    V_pre = hits.count_all(sk.e_pre, sk.e_t)
    own = hits.count_own(sk.e_agent, sk.e_t, sk.e_post)
    own_pre = hits.count_own(sk.e_agent, sk.e_pre, sk.e_t)
    return {"host": host_prev, "pi": pi, "cand": cand, "V": V.astype(float), "V_pre": V_pre.astype(float),
            "own": own.astype(float), "own_pre": own_pre.astype(float),
            "oth": (V - own).astype(float), "oth_pre": (V_pre - own_pre).astype(float)}


def _pfe(V, cols, strata):
    X = np.column_stack(cols)
    ok = np.isfinite(V) & np.all(np.isfinite(X), axis=1)
    if ok.sum() < 20 or V[ok].sum() == 0:
        return np.full(X.shape[1], np.nan)
    return SK.poisson_fe(V[ok], X[ok], np.asarray(strata)[ok])


def _pfe_off(V, cols, strata, off):
    ok = np.isfinite(off)
    if ok.sum() < 20:
        return np.full(len(cols), np.nan)
    X = np.column_stack([c[ok] for c in cols] + [off[ok]])
    Vv = V[ok]
    if Vv.sum() == 0:
        return np.full(len(cols), np.nan)
    # offset as a covariate with its coefficient fixed at 1: fit on V with the offset column, then refit by
    # semantic_kappa.poisson_fe on the offset-adjusted design (log E[V] = FE + X b + off)
    return _poisson_fe_offset(Vv, X[:, :-1], np.asarray(strata)[ok], X[:, -1])


def _poisson_fe_offset(y, X, strata, off, iters: int = 50, tol: float = 1e-8):
    """Poisson pseudo-ML with stratum fixed effects and an offset (IRLS with closed-form FE profiling)."""
    g = SK._codes(strata)
    keep = np.bincount(g, y)[g] > 0
    y, X, off, g = y[keep], X[keep], off[keep], SK._codes(g[keep])
    if len(y) < 5:
        return np.full(X.shape[1], np.nan)
    G = int(g.max()) + 1
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        eta0 = X @ b + off
        num = np.bincount(g, y, G)
        den = np.bincount(g, np.exp(eta0), G)
        fe = np.where(num > 0, np.log(np.maximum(num, 1e-300) / np.maximum(den, 1e-300)), -30.0)
        mu = np.exp(eta0 + fe[g])
        # score and Fisher information with the FE profiled out (within-stratum weighted centering)
        wsum = np.bincount(g, mu, G)
        Xc = X - (np.stack([np.bincount(g, mu * X[:, j], G) for j in range(X.shape[1])], 1)
                  / np.maximum(wsum, 1e-300)[:, None])[g]
        sc = Xc.T @ (y - mu)
        I = (Xc * mu[:, None]).T @ Xc
        try:
            step = np.linalg.solve(I + 1e-9 * np.eye(len(b)), sc)
        except np.linalg.LinAlgError:
            return np.full(X.shape[1], np.nan)
        if not np.all(np.isfinite(step)):
            return np.full(X.shape[1], np.nan)
        b = b + np.clip(step, -2, 2)
        if np.max(np.abs(step)) < tol:
            break
    return b


def value_fit(sk: Skeleton, wf: dict, idx: np.ndarray | None = None) -> dict:
    """On current-host events (optionally a resampled index), Poisson pseudo-ML with stratum (agent|unit) FE.
    Primary (Amendment A1): rate forms, K's share of the expression events in the window (offset = log of all element
    events in the same window), so the segment-position activity dip after a forced erasure cancels.
      b_rate  the wiped host's own K hits in calls 1..20, offset log(own element events in 1..20), covariate the own K
              share in calls -20..-1 (log((own_pre + 0.5) / (base_own_pre + 1))); exp(b_rate) - 1 = the pattern's
              relative loss when all its hosts are wiped (full dose) and the others do not respond;
      b_oth   others' K hits in the window, offset log(others' element events), covariates F * pi and the others'
              pre share: the others' response per unit dose (absorption > 0, spreading loss < 0).
    Variants (card's first form; count based, activity not held):
      b_dose  all K hits ~ F * pi + log1p(V_pre) + log(duration);  b_own  own K hits ~ F + log1p(own_pre) + log(dur)."""
    sel = np.flatnonzero(wf["host"]) if idx is None else idx
    F = sk.e_F[sel].astype(float)
    st = sk.e_stratum[sel]
    ldur = np.log(sk.e_dur[sel])
    b = _pfe(wf["V"][sel], [F * wf["pi"][sel], np.log1p(wf["V_pre"][sel]), ldur], st)
    bo = _pfe(wf["own"][sel], [F, np.log1p(wf["own_pre"][sel]), ldur], st)
    with np.errstate(divide="ignore"):
        off_own = np.log(sk.base_own_post[sel])
        off_oth = np.log(sk.base_oth_post[sel])
    sh_own = np.log((wf["own_pre"][sel] + 0.5) / (sk.base_own_pre[sel] + 1.0))
    sh_oth = np.log((wf["oth_pre"][sel] + 0.5) / (sk.base_oth_pre[sel] + 1.0))
    br = _pfe_off(wf["own"][sel], [F, sh_own], st, np.where(np.isfinite(off_own), off_own, np.nan))
    bt = _pfe_off(wf["oth"][sel], [F * wf["pi"][sel], sh_oth], st, np.where(np.isfinite(off_oth), off_oth, np.nan))
    return {"b_dose": float(b[0]), "b_own": float(bo[0]), "b_rate": float(br[0]), "b_oth": float(bt[0]),
            "n_host_events": int(len(sel)), "n_F": int(F.sum()), "n_P": int(len(sel) - F.sum()),
            "n_rate_events": int(np.isfinite(off_own).sum())}


def info_fit(sk: Skeleton, wf: dict, idx: np.ndarray | None = None, n_perm: int = 50, rng=None) -> dict:
    """I_K,F = I_P - I_F on candidate-host events (own post level vs own pre level)."""
    rng = rng or np.random.default_rng(0)
    sel = np.flatnonzero(wf["cand"]) if idx is None else idx
    X = np.minimum(wf["own"][sel], 2).astype(int)
    S = np.minimum(wf["own_pre"][sel], 2).astype(int)
    F = sk.e_F[sel]
    st = sk.e_stratum[sel]
    out = {}
    for arm, m in (("F", F), ("P", ~F)):
        if m.sum() < 20:
            out[arm] = float("nan")
            continue
        r = SK.mi_corrected(X[m], S[m], st[m], n_perm=n_perm, rng=rng)
        out[arm] = r["I"]
    return {"I_F": out["F"], "I_P": out["P"], "I_K": out["P"] - out["F"], "n_cand_events": int(len(sel))}


def cluster_index(clusters: np.ndarray, sel: np.ndarray):
    cl = clusters[sel]
    codes = np.unique(cl, return_inverse=True)[1]
    order = np.argsort(codes, kind="stable")
    members = np.split(sel[order], np.flatnonzero(np.diff(codes[order])) + 1)
    return members


VALUE_KEYS = ("b_rate", "b_oth", "b_dose", "b_own")


def boot_value_info(sk: Skeleton, wf: dict, B: int = 200, seed: int = 0, info: bool = True, n_perm_boot: int = 8):
    """Agent-day cluster bootstrap of the value coefficients (dict of arrays) and (optionally) I_K."""
    rng = np.random.default_rng(seed)
    hsel = np.flatnonzero(wf["host"])
    csel = np.flatnonzero(wf["cand"])
    hm = cluster_index(sk.e_cluster, hsel)
    cm = cluster_index(sk.e_cluster, csel) if info else None
    rv = {k: [] for k in VALUE_KEYS}
    ri = []
    for _ in range(B):
        if len(hm) > 2:
            idx = np.concatenate([hm[j] for j in rng.integers(0, len(hm), len(hm))])
            r = value_fit(sk, wf, idx)
            for k in VALUE_KEYS:
                rv[k].append(r[k])
        if info and len(cm) > 2:
            idx = np.concatenate([cm[j] for j in rng.integers(0, len(cm), len(cm))])
            ri.append(info_fit(sk, wf, idx, n_perm=n_perm_boot, rng=rng)["I_K"])
    return {k: np.array(v, float) for k, v in rv.items()}, np.array(ri, float)


def q(a, lo=2.5, hi=97.5):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if len(a) < 10:
        return [float("nan"), float("nan")]
    return [float(np.percentile(a, lo)), float(np.percentile(a, hi))]


def excess_ci(b, boot, pseudo):
    """Three CI forms for the excess b - median(pseudo), on the log scale -> relative change:
    boot   bootstrap percentiles of b, shifted by the pseudo median;
    comb   normal CI with se^2 = var(boot) + var(pseudo) (pattern-to-pattern spread of the null included);
    pq     [b - q97.5(pseudo), b - q2.5(pseudo)] (pseudo quantiles as the null band)."""
    pseudo = np.asarray(pseudo, float)
    pseudo = pseudo[np.isfinite(pseudo)]
    pm = float(np.median(pseudo)) if len(pseudo) else 0.0
    ex = b - pm
    out = {"excess": float(np.exp(ex) - 1)}
    ci = q(boot - pm)
    out["boot"] = [float(np.exp(x) - 1) for x in ci]
    bb = np.asarray(boot, float)
    bb = bb[np.isfinite(bb)]
    se = float(np.sqrt((bb.var() if len(bb) > 2 else np.nan) + (pseudo.var() if len(pseudo) > 2 else 0.0)))
    out["comb"] = [float(np.exp(ex - 1.96 * se) - 1), float(np.exp(ex + 1.96 * se) - 1)]
    if len(pseudo) >= 10:
        out["pq"] = [float(np.exp(b - np.percentile(pseudo, 97.5)) - 1), float(np.exp(b - np.percentile(pseudo, 2.5)) - 1)]
    else:
        out["pq"] = [float("nan"), float("nan")]
    return out


def output_selfdip(sk: Skeleton, B: int = 200, seed: int = 0) -> dict:
    """K1 positive control: the wiped agent's own output (work commits, statements) in calls 1..20 vs placebo."""
    e = sk.ev
    res = {}
    rng = np.random.default_rng(seed)
    allsel = np.arange(e.height)
    mem = cluster_index(sk.e_cluster, allsel)
    for name, v, vp in (("work_commits", "n_work_post20", "n_work_pre20"), ("statements", "stmt_post20", "stmt_pre20"),
                        ("own_repo_commits", "own_post20", "own_pre20")):
        V = e[v].to_numpy().astype(float)
        Vp = e[vp].to_numpy().astype(float)
        b0 = _pfe(V, [sk.e_F.astype(float), np.log1p(Vp)], sk.e_stratum)[0]
        bs = []
        for _ in range(B):
            idx = np.concatenate([mem[j] for j in rng.integers(0, len(mem), len(mem))])
            bs.append(_pfe(V[idx], [sk.e_F[idx].astype(float), np.log1p(Vp[idx])], sk.e_stratum[idx])[0])
        ci = q(bs)
        res[name] = {"dV_rel": float(np.exp(b0) - 1), "ci": [float(np.exp(ci[0]) - 1), float(np.exp(ci[1]) - 1)],
                     "mean_F": float(V[sk.e_F].mean()), "mean_P": float(V[~sk.e_F].mean())}
    return res


# ================================================================================================ O2 / O3: dated events
def active_of_hits(hits: Hits) -> np.ndarray:
    return C.active_time(hits.t)


def window_counts(a_hits: np.ndarray, agent: np.ndarray, lo: float, hi: float, who: int | None):
    m = (a_hits >= lo) & (a_hits < hi)
    tot = int(m.sum())
    own = int((m & (agent == who)).sum()) if who is not None else 0
    return tot, own


def event_loss(hits: Hits, a_hits: np.ndarray, e: dict, a_start: float, a_end: float, a_before: float,
               a_after: float | None = None):
    who = e["agent"]
    vb, ob = window_counts(a_hits, hits.agent, a_before, a_start, who)
    va, oa = window_counts(a_hits, hits.agent, a_start if a_after is None else a_after, a_end, who)
    L = 1 - va / vb if vb > 0 else float("nan")
    s = ob / vb if vb > 0 else float("nan")
    L_own = 1 - oa / ob if ob > 0 else float("nan")
    L_oth = 1 - (va - oa) / (vb - ob) if vb - ob > 0 else float("nan")
    return {"V_before": vb, "V_after": va, "own_before": ob, "own_after": oa, "L": L, "s": s, "L_own": L_own,
            "L_others": L_oth}


def hub_beta(sk: Skeleton, hits: Hits, eid: str, same_weekday: bool = True) -> dict:
    """beta = (L - mean L_placebo) / s, with L = 1 - V_after / V_before (K hits, 2 active days or the event window)."""
    e = next(x for x in sk.sev["events"] if x["id"] == eid)
    ah = active_of_hits(hits)
    r = event_loss(hits, ah, e, e["a_start"], e["a_end"], e["a_before"], e["a_after"])
    pd_ = sk.pdays.filter(pl.col("id") == eid)
    if same_weekday:
        pd_ = pd_.filter(pl.col("same_weekday"))
    Lp = []
    for p in pd_.iter_rows(named=True):
        rp = event_loss(hits, ah, e, p["a_start"], p["a_end"], p["a_before"], p["a_after"])
        Lp.append(rp["L"])
    Lp = np.array([x for x in Lp if np.isfinite(x)])
    mu = float(Lp.mean()) if len(Lp) else 0.0
    beta = (r["L"] - mu) / r["s"] if r["s"] and r["s"] > 0 and np.isfinite(r["L"]) else float("nan")
    dev = np.abs(Lp - mu)
    thr = float(np.percentile(dev, 95)) if len(dev) else float("nan")
    beta_band = [float((r["L"] - mu - thr) / r["s"]), float((r["L"] - mu + thr) / r["s"])] if r["s"] else [None, None]
    return {**r, "L_placebo_mean": mu, "L_placebo": Lp.tolist(), "n_placebo": int(len(Lp)), "beta": float(beta),
            "beta_band95": beta_band, "exceeds_placebo95": bool(np.isfinite(r["L"]) and abs(r["L"] - mu) > thr)}


def prevalence_change(sk: Skeleton, hits: Hits, eid: str, same_weekday: bool = True, m: int = M_HOST) -> dict:
    """Mean hosts per bin after vs before (bins whose start lies in the window), relative change, vs placebo days."""
    e = next(x for x in sk.sev["events"] if x["id"] == eid)
    n_host = host_matrix(sk, hits, m).sum(0).astype(float)
    a_bin = C.active_time(sk.bin_t0)

    def rel(a0, a1, ab, aa):
        bm = (a_bin >= ab) & (a_bin < a0)
        am = (a_bin >= aa) & (a_bin < a1)
        if bm.sum() == 0 or am.sum() == 0 or n_host[bm].mean() == 0:
            return float("nan"), float("nan"), float("nan")
        return n_host[am].mean() / n_host[bm].mean() - 1, float(n_host[bm].mean()), float(n_host[am].mean())
    r, nb, na = rel(e["a_start"], e["a_end"], e["a_before"], e["a_after"])
    pd_ = sk.pdays.filter(pl.col("id") == eid)
    if same_weekday:
        pd_ = pd_.filter(pl.col("same_weekday"))
    rp = np.array([rel(p["a_start"], p["a_end"], p["a_before"], p["a_after"])[0] for p in pd_.iter_rows(named=True)])
    rp = rp[np.isfinite(rp)]
    mu = float(rp.mean()) if len(rp) else 0.0
    thr = float(np.percentile(np.abs(rp - mu), 95)) if len(rp) else float("nan")
    return {"rel_change": float(r), "hosts_before": nb, "hosts_after": na, "placebo_mean": mu, "placebo": rp.tolist(),
            "n_placebo": int(len(rp)), "net": float(r - mu), "exceeds_placebo95": bool(np.isfinite(r) and abs(r - mu) > thr)}


# ================================================================================================ O4: host relation
def host_matrix(sk: Skeleton, hits: Hits, m: int = M_HOST) -> np.ndarray:
    """H145's host rule: >= m distinct K elements in the bin, present agent-bins only (DQ8 trim)."""
    _, D = hits.bin_tables(sk)
    return (D >= m) & sk.present


class HostPanel:
    """Present agent-bins (>= 1 non-pause call) with outcomes and FE design pieces, built once."""

    def __init__(self, sk: Skeleton, commits_col: str = "commits_own"):
        p = sk.panel.filter(pl.col("present") & (pl.col("n_work_calls") > 0)).sort("agent", "bin")
        self.agent = p["agent"].to_numpy().astype(np.int16)
        self.ai = np.array([sk.a_index[int(a)] for a in self.agent])
        self.bin = p["bin"].to_numpy()
        self.k = p["k"].to_numpy().astype(int)
        self.day = p["day_idx"].to_numpy().astype(float)
        self.commits = p[commits_col].to_numpy().astype(float)
        self.align = {c: p[c].to_numpy().astype(float) for c in ("align_bge", "align_gte", "align_sr_bge", "align_sr_gte")}
        self.talk = p["talk_share"].to_numpy().astype(float)
        self.n_stmt = p["n_stmt"].to_numpy().astype(float)
        self.n_work = p["n_work_calls"].to_numpy().astype(float)
        self.cluster = (p["agent"].cast(pl.String) + "|" + p["pt_date"]).to_numpy()
        self.group = (self.agent.astype(np.int64) * 16 + np.minimum(self.k, 15))
        self.n = len(self.agent)


def _trend_cols(agent_codes: np.ndarray, day: np.ndarray):
    u = np.unique(agent_codes)
    cols = []
    for a in u:
        m = agent_codes == a
        d = np.where(m, day - day[m].mean(), 0.0)
        if np.ptp(d[m]) > 0:
            cols.append(d / 10.0)
    return cols


def _ols_within(y, Xcols, g):
    ok = np.isfinite(y)
    for c in Xcols:
        ok &= np.isfinite(c)
    if ok.sum() < 20:
        return np.nan
    gg = SK._codes(g[ok])
    X = np.column_stack([SK._within(c[ok], gg) for c in Xcols])
    yy = SK._within(y[ok], gg)
    beta = np.linalg.lstsq(X, yy, rcond=None)[0]
    return float(beta[0])


def host_fit(hp: HostPanel, host_ab: np.ndarray, rows: np.ndarray | None = None, min_host_bins: int = 3,
             outcomes=("commits", "align_bge", "align_gte", "talk"), activity: bool = True) -> dict:
    """Within-agent (agent x day-part FE, agent-specific linear trend) effects of hosting K on own-role output.
    Amendment A2: with `activity`, log1p(statements) and log1p(non-pause calls) in the bin are covariates (hosting
    needs statements; statements co-vary with commits within agent), so the effect is at matched activity.
    Returns relative effects: commits exp(b) - 1; alignment and talk share b / mean(non-hosting)."""
    h = host_ab[hp.ai, hp.bin].astype(float)
    # eligible agents: >= min_host_bins hosting and >= min_host_bins non-hosting present bins
    elig = np.zeros(hp.n, bool)
    for a in np.unique(hp.agent):
        m = hp.agent == a
        nh = h[m].sum()
        if nh >= min_host_bins and (m.sum() - nh) >= min_host_bins:
            elig |= m
    sel = np.flatnonzero(elig) if rows is None else rows[elig[rows]]
    out = {"n_bins": int(len(sel)), "n_host_bins": int(h[sel].sum()), "n_agents": int(len(np.unique(hp.agent[sel])))}
    if len(sel) < 30 or h[sel].sum() < 3:
        return {**out, **{o: float("nan") for o in outcomes}}
    act = [np.log1p(hp.n_stmt), np.log1p(hp.n_work)] if activity else []
    for o in outcomes:
        if o == "commits":
            # agents with no own-repo commit in the rows carry no information (their FE groups drop out)
            ca = hp.agent[sel]
            tot = {a: hp.commits[sel][ca == a].sum() for a in np.unique(ca)}
            sc = sel[np.array([tot[a] > 0 for a in ca])]
            out["n_agents_commits"] = int(len(np.unique(hp.agent[sc])))
            if len(sc) < 30 or h[sc].sum() < 3:
                out[o] = float("nan")
                continue
            tr = _trend_cols(hp.agent[sc], hp.day[sc])
            b = _pfe(hp.commits[sc], [h[sc]] + [x[sc] for x in act] + tr, hp.group[sc])[0]
            out[o] = float(np.exp(b) - 1) if np.isfinite(b) and abs(b) < 20 else float("nan")
        else:
            tr = _trend_cols(hp.agent[sel], hp.day[sel])
            y = hp.talk[sel] if o == "talk" else hp.align[o][sel]
            b = _ols_within(y, [h[sel]] + [x[sel] for x in act] + tr, hp.group[sel])
            base = np.nanmean(y[h[sel] == 0])
            out[o] = float(b / base) if np.isfinite(b) and base and abs(base) > 1e-6 else float("nan")
            out[o + "_abs"] = float(b) if np.isfinite(b) else float("nan")
    return out


def host_boot(hp: HostPanel, host_ab: np.ndarray, B: int = 200, seed: int = 0, outcomes=("commits", "align_bge",
                                                                                          "align_gte", "talk"),
              activity: bool = True):
    rng = np.random.default_rng(seed)
    mem = cluster_index(hp.cluster, np.arange(hp.n))
    res = {o: [] for o in outcomes}
    for _ in range(B):
        idx = np.concatenate([mem[j] for j in rng.integers(0, len(mem), len(mem))])
        r = host_fit(hp, host_ab, rows=idx, outcomes=outcomes, activity=activity)
        for o in outcomes:
            res[o].append(r[o])
    return {o: np.array(v, float) for o, v in res.items()}


def classify(dc: float, da: float, dc_ci=None, da_ci=None, require_ci: bool = True) -> str:
    """Card rule: mutualist if (a) and (b) >= +5%; parasitic if (a) or (b) <= -10% with the other not >= +5%;
    neutral otherwise. Amendment A2: with require_ci, a component counts only if its CI excludes 0 in its direction."""
    def up(x, ci):
        return np.isfinite(x) and x >= 0.05 and (not require_ci or (ci is not None and ci[0] > 0))

    def down(x, ci):
        return np.isfinite(x) and x <= -0.10 and (not require_ci or (ci is not None and ci[1] < 0))
    if up(dc, dc_ci) and up(da, da_ci):
        return "mutualist"
    if (down(dc, dc_ci) and not up(da, da_ci)) or (down(da, da_ci) and not up(dc, dc_ci)):
        return "parasitic"
    return "neutral"


# ================================================================================================ pseudo-patterns
def draw_pseudo(elem_freq: dict, elem_hosts: dict, members: list, n: int, rng, pool: list | None = None,
                tol: float = 0.25, host_tol: int = 1) -> list[list]:
    """Frequency-matched pseudo-patterns: for each element of K, a random element with frequency within +-25% and host
    count within +-1 (widening the tolerances by steps when no candidate exists); elements of K excluded."""
    pool = [e for e in (pool or list(elem_freq)) if e not in set(members)]
    f = np.array([elem_freq[e] for e in pool], float)
    hcount = np.array([elem_hosts.get(e, 0) for e in pool], float)
    out = []
    for _ in range(n):
        s = []
        for e in members:
            fe, he = elem_freq[e], elem_hosts.get(e, 0)
            t, ht = tol, host_tol
            while True:
                cand = np.flatnonzero((np.abs(f - fe) <= t * fe) & (np.abs(hcount - he) <= ht))
                cand = [c for c in cand if pool[c] not in s]
                if cand or t > 4:
                    break
                t, ht = t * 1.5, ht + 1
            if cand:
                s.append(pool[int(rng.choice(cand))])
        out.append(s)
    return out
