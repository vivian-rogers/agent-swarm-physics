"""H89 Price-equation estimator (cross-fitted shares, open population, in-cone cultural parentage).

For a transition d -> d' of one goal period, with active populations A_d, A_d', stayers S, leavers E, entrants I:
  dz = Sel + Trans + Mig_out + Mig_in                         (exact, componentwise)
  Sel   = Cov_S(w, z(d))       w_i = sum_j alpha_ji (w-bar = 1), split self / named / unnamed
  Trans = E_S(w dz)            split self / social
  Mig   = Mig_out + Mig_in     split roster / presence
Parentage over stayers: alpha_jj = 1 - lambda_j; alpha_ji = lambda_j a_ji / sum_i a_ji, with a_ji the fractional
in-cone adoptions of j (first use on d') from source i in S, lambda_j = sum_i a_ji / F_j (F_j = j's first uses of
period ideas on d').
Shares are cross-fitted between message halves A and B (noise-free inner products in expectation).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"

import json  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import sys  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402
DATA = ROOT / "data/processed/H89-price-equation-culture"
SH = ROOT / "data/processed/shared"
TRAITS = ["content_bge", "content_gte", "style", "conv"]
CONTENT = {"content_bge": "bge_small", "content_gte": "gte_modernbert"}
TERMS = ["sel_self", "sel_named", "sel_unnamed", "trans_self", "trans_social", "mig_out_roster", "mig_out_presence",
         "mig_in_roster", "mig_in_presence"]
GROUPS = {"sel": ["sel_self", "sel_named", "sel_unnamed"], "trans": ["trans_self", "trans_social"],
          "mig": ["mig_out_roster", "mig_out_presence", "mig_in_roster", "mig_in_presence"],
          "mig_roster": ["mig_out_roster", "mig_in_roster"], "mig_presence": ["mig_out_presence", "mig_in_presence"],
          "sel_social": ["sel_named", "sel_unnamed"]}
MIN_STAY = 3
HOLD = json.loads((ROOT / "hypotheses/holdout.json").read_text())


def _roster():
    r = pl.read_parquet(SH / "roster.parquet", columns=["agent", "joined", "left"])
    return {int(a): (j, l) for a, j, l in r.iter_rows()}


ROSTER = _roster()


@dataclass
class Period:
    goal: int
    days: list
    keys: dict                   # (agent, day) -> row
    traits: dict                 # tag -> (n_keys x 3 x dim) [whole, A, B]
    active: dict                 # day -> sorted list of active agents
    F: dict                      # (agent, day) -> (F_all, F_notrait)
    adop: dict                   # kind -> list of (day, adopter, sources tuple, named tuple, in_trait)
    kick: dict = field(default_factory=dict)  # tag -> unit vector

    def drop(self, agents: set) -> "Period":
        act = {d: [a for a in v if a not in agents] for d, v in self.active.items()}
        return Period(self.goal, self.days, self.keys, self.traits, act, self.F, self.adop, self.kick)


def load_period(g: int, ad: pl.DataFrame | None = None, adop: pl.DataFrame | None = None, kick=None) -> Period:
    z = np.load(DATA / "traits" / f"G{g:02d}.npz", allow_pickle=False)
    days = [str(x) for x in z["days"]]
    ag, dy = z["agent"].astype(int), z["day"].astype(int)
    keys = {(int(a), int(d)): k for k, (a, d) in enumerate(zip(ag, dy))}
    traits = {t: z[t].astype(np.float64) for t in TRAITS}
    if ad is None:
        ad = pl.read_parquet(DATA / "agent_days.parquet")
    a = ad.filter(pl.col("goal") == g)
    assert not any(holdout_mask(a["pt_date"].to_list(), a["goal"].to_list())), "held-out day in H89 inputs"
    active = {}
    F = {}
    for r in a.iter_rows(named=True):
        F[(r["agent"], r["day"])] = (r["F_all"], r["F_notrait"])
        if r["active"]:
            active.setdefault(r["day"], []).append(r["agent"])
    active = {d: sorted(v) for d, v in active.items()}
    if adop is None:
        adop = pl.read_parquet(DATA / "adoptions.parquet")
    ap_ = adop.filter(pl.col("goal") == g)
    A = {"read": [], "plc": []}
    for r in ap_.iter_rows(named=True):
        A[r["kind"]].append((r["day"], r["adopter"], tuple(r["sources"]), tuple(r["named_sources"] or []), r["in_trait"]))
    if kick is None:
        kick = np.load(DATA / "kickoff.npz")
    kk = {}
    for tag, model in CONTENT.items():
        key = f"G{g:02d}_{model}"
        if key in kick.files:
            kk[tag] = kick[key].astype(np.float64)
    return Period(g, days, keys, traits, active, F, A, kk)


def transitions(P: Period) -> list[tuple[int, int]]:
    ds = sorted(P.active)
    return [(d, e) for d, e in zip(ds[:-1], ds[1:]) if len(set(P.active[d]) & set(P.active[e])) >= MIN_STAY]


def parentage(P: Period, d1: int, S: list[int], kind: str = "read", exclude_trait: bool = False):
    """alpha (|S| x |S|, rows = offspring j, cols = parent i) and its self / named / unnamed parts; diagnostics."""
    idx = {a: k for k, a in enumerate(S)}
    n = len(S)
    a_named = np.zeros((n, n)); a_un = np.zeros((n, n))
    n_ext = 0; n_in = 0
    for (day, j, srcs, nmd, in_tr) in P.adop[kind]:
        if day != d1 or j not in idx or (exclude_trait and in_tr):
            continue
        s_in = [s for s in srcs if s in idx and s != j]
        if not s_in:
            n_ext += 1
            continue
        n_in += 1
        wgt = 1.0 / len(s_in)
        for s in s_in:
            if s in nmd:
                a_named[idx[j], idx[s]] += wgt
            else:
                a_un[idx[j], idx[s]] += wgt
    Fj = np.array([P.F.get((a, d1), (0, 0))[1 if exclude_trait else 0] for a in S], dtype=float)
    tot = a_named.sum(1) + a_un.sum(1)
    lam = np.where(Fj > 0, np.minimum(tot / np.maximum(Fj, 1), 1.0), 0.0)
    scale = np.where(tot > 0, lam / np.maximum(tot, 1e-12), 0.0)
    al_named = a_named * scale[:, None]
    al_un = a_un * scale[:, None]
    al_self = np.diag(1 - lam)
    return al_self, al_named, al_un, dict(lam_mean=float(lam.mean()), n_in=n_in, n_ext=n_ext)


def _z(P: Period, tag: str, agents, day: int, h: int) -> np.ndarray:
    return np.stack([P.traits[tag][P.keys[(a, day)], h] for a in agents]) if len(agents) else \
        np.zeros((0, P.traits[tag].shape[2]))


def price_transition(P: Period, d0: int, d1: int, tags=TRAITS, kind: str = "read", exclude_trait=False,
                     perm_w: np.ndarray | None = None):
    """Per-term vectors for halves (whole, A, B): {tag: {term: (3 x dim)}}, plus dz and diagnostics."""
    A0, A1 = P.active[d0], P.active[d1]
    S = sorted(set(A0) & set(A1))
    E = [a for a in A0 if a not in S]
    I = [a for a in A1 if a not in S]
    day0, day1 = P.days[d0], P.days[d1]
    # roster flow: an entrant on its first active day of the period, having joined the roster after the period's
    # first day; a leaver on its last active day of the period, having left the roster by the period's last day + 1
    ds = sorted(P.active)
    first_act = {a: min(d for d in ds if a in P.active[d]) for a in I}
    last_act = {a: max(d for d in ds if a in P.active[d]) for a in E}
    p_first, p_last = P.days[0], P.days[-1]
    I_ro = [first_act[a] == d1 and ROSTER.get(a, (None, None))[0] is not None and ROSTER[a][0] > p_first
            for a in I]
    E_ro = [last_act[a] == d0 and ROSTER.get(a, (None, None))[1] is not None and ROSTER[a][1] <= _next_day(p_last)
            for a in E]
    al_s, al_n, al_u, diag = parentage(P, d1, S, kind, exclude_trait)
    al = al_s + al_n + al_u
    nS = len(S)
    w_c = {"self": al_s.sum(0), "named": al_n.sum(0), "unnamed": al_u.sum(0)}
    if perm_w is not None:
        w_c = {k: v[perm_w] for k, v in w_c.items()}
    out = {}
    for tag in tags:
        terms = {k: np.zeros((3, P.traits[tag].shape[2])) for k in TERMS}
        dz = np.zeros((3, P.traits[tag].shape[2]))
        for h in range(3):
            z0, z1 = _z(P, tag, S, d0, h), _z(P, tag, S, d1, h)
            zE, zI = _z(P, tag, E, d0, h), _z(P, tag, I, d1, h)
            m0, m1 = z0.mean(0), z1.mean(0)
            for c, w in w_c.items():
                terms[f"sel_{c}"][h] = ((w - w.mean())[:, None] * z0).sum(0) / nS
            # trans self: sum_i alpha_ii (z_i(d') - z_i(d)); social: sum_i sum_{j!=i} alpha_ji (z_j(d') - z_i(d))
            dg = np.diag(al_s)
            terms["trans_self"][h] = (dg[:, None] * (z1 - z0)).sum(0) / nS
            soc = al_n + al_u                       # rows j, cols i
            terms["trans_social"][h] = ((soc.sum(1)[:, None] * z1).sum(0) - (soc.sum(0)[:, None] * z0).sum(0)) / nS
            nA0, nA1 = len(A0), len(A1)
            for lst, flags, zz, mm, nn, sign, nm in ((E, E_ro, zE, m0, nA0, -1.0, "mig_out"),
                                                    (I, I_ro, zI, m1, nA1, 1.0, "mig_in")):
                for k in range(len(lst)):
                    terms[f"{nm}_{'roster' if flags[k] else 'presence'}"][h] += sign * (zz[k] - mm) / nn
            # check identity (unpermuted only)
            zA0 = _z(P, tag, A0, d0, h).mean(0); zA1 = _z(P, tag, A1, d1, h).mean(0)
            dz[h] = zA1 - zA0
            if perm_w is None:
                tot = sum(terms[k][h] for k in TERMS)
                assert np.allclose(tot, dz[h], atol=1e-8), f"Price identity failed G{P.goal} {d0}->{d1} {tag}"
        out[tag] = dict(terms=terms, dz=dz)
    diag.update(nS=nS, nE=len(E), nI=len(I), nE_roster=int(sum(E_ro)), nI_roster=int(sum(I_ro)),
                d0=day0, d1=day1, w_named=float(al_n.sum()), w_unnamed=float(al_u.sum()),
                w_sd=float((al_s + al_n + al_u).sum(0).std()))
    return out, diag


def _next_day(d: str) -> str:
    import datetime as dt
    return (dt.date.fromisoformat(d) + dt.timedelta(days=1)).isoformat()


def xf(a: np.ndarray, b: np.ndarray) -> float:
    """Cross-fitted inner product of two (3 x dim) half-arrays."""
    return 0.5 * (float(a[1] @ b[2]) + float(a[2] @ b[1]))


def group_vec(terms: dict, grp: str) -> np.ndarray:
    if grp in GROUPS:
        return sum(terms[k] for k in GROUPS[grp])
    return terms[grp]


def shares(res: list, tag: str, groups=("sel", "trans", "mig", "mig_roster", "mig_presence", "sel_self",
                                         "sel_named", "sel_unnamed", "sel_social", "trans_self", "trans_social"),
           kick: np.ndarray | None = None, cumulative: bool = False) -> dict:
    """Energy (sum over transitions) or cumulative cross-fitted shares for one trait."""
    if not res:
        return {}
    if cumulative:
        tot = {g: sum(group_vec(r[tag]["terms"], g) for r in res) for g in groups}
        dz = sum(r[tag]["dz"] for r in res)
        den = xf(dz, dz)
        out = {f"s_{g}": xf(tot[g], dz) / den if den > 0 else np.nan for g in groups}
        nm = (dz[1] @ dz[1]) * (dz[2] @ dz[2])
        out["rho"] = float(dz[1] @ dz[2]) / np.sqrt(nm) if nm > 0 else np.nan
        out["den"] = den
        if kick is not None:
            st = sum(group_vec(r[tag]["terms"], "sel") + group_vec(r[tag]["terms"], "trans") for r in res)
            sk = np.outer(np.ones(3), kick) * (st @ kick)[:, None]
            out["s_kick"] = xf(sk, dz) / den if den > 0 else np.nan
            out["R"] = out["s_sel"] + out["s_trans"] - out["s_kick"]
        return out
    den = sum(xf(r[tag]["dz"], r[tag]["dz"]) for r in res)
    out = {f"s_{g}": (sum(xf(group_vec(r[tag]["terms"], g), r[tag]["dz"]) for r in res) / den if den > 0 else np.nan)
           for g in groups}
    a = sum(float(r[tag]["dz"][1] @ r[tag]["dz"][2]) for r in res)
    nA = sum(float(r[tag]["dz"][1] @ r[tag]["dz"][1]) for r in res)
    nB = sum(float(r[tag]["dz"][2] @ r[tag]["dz"][2]) for r in res)
    out["rho"] = a / np.sqrt(nA * nB) if nA * nB > 0 else np.nan
    out["den"] = den
    if kick is not None:
        num = 0.0
        for r in res:
            st = group_vec(r[tag]["terms"], "sel") + group_vec(r[tag]["terms"], "trans")
            sk = (st @ kick)[:, None] * kick[None, :]
            num += xf(sk, r[tag]["dz"])
        out["s_kick"] = num / den if den > 0 else np.nan
        out["R"] = out["s_sel"] + out["s_trans"] - out["s_kick"]
    return out


def persistence(res: list, tag: str, kick: np.ndarray | None) -> float:
    """Cross-fitted cosine of the non-migration, non-kickoff change between consecutive transitions."""
    Y = []
    for r in res:
        st = group_vec(r[tag]["terms"], "sel") + group_vec(r[tag]["terms"], "trans")
        if kick is not None:
            st = st - (st @ kick)[:, None] * kick[None, :]
        Y.append(st)
    num = 0.0; den = 0.0
    for t in range(len(Y) - 1):
        num += xf(Y[t], Y[t + 1])
        den += np.sqrt(max(xf(Y[t], Y[t]), 1e-12) * max(xf(Y[t + 1], Y[t + 1]), 1e-12))
    return num / den if den > 0 else np.nan


def run_period(P: Period, kind="read", exclude_trait=False, tags=TRAITS):
    res, diags = [], []
    for d0, d1 in transitions(P):
        r, dg = price_transition(P, d0, d1, tags=tags, kind=kind, exclude_trait=exclude_trait)
        res.append(r); diags.append(dg)
    return res, diags


def summarize(P: Period, res: list, tags=TRAITS) -> dict:
    out = {}
    for tag in tags:
        k = P.kick.get(tag)
        e = shares(res, tag, kick=k)
        c = shares(res, tag, kick=k, cumulative=True)
        out[tag] = dict(energy=e, cum=c, C=persistence(res, tag, k) if len(res) >= 2 else np.nan)
    return out


def perm_sel(P: Period, tag: str, n_perm: int = 500, seed: int = 0, kind="read") -> tuple[float, float, np.ndarray]:
    """Observed energy s_sel and its w-permutation null (w shuffled among stayers within each transition)."""
    rng = np.random.default_rng(seed)
    trs = transitions(P)
    base = [price_transition(P, d0, d1, tags=[tag], kind=kind)[0] for d0, d1 in trs]
    den = sum(xf(r[tag]["dz"], r[tag]["dz"]) for r in base)
    obs = sum(xf(group_vec(r[tag]["terms"], "sel"), r[tag]["dz"]) for r in base) / den
    # fast permutation: Sel = Cov(w, z0) is linear in w; precompute w and z0 per transition
    pre = []
    for (d0, d1), r in zip(trs, base):
        S = sorted(set(P.active[d0]) & set(P.active[d1]))
        al_s, al_n, al_u, _ = parentage(P, d1, S, kind)
        w = (al_s + al_n + al_u).sum(0)
        z0 = np.stack([_z(P, tag, S, d0, h) for h in range(3)])   # 3 x nS x dim
        pre.append((w, z0, r[tag]["dz"]))
    null = np.empty(n_perm)
    for b in range(n_perm):
        num = 0.0
        for w, z0, dz in pre:
            wp = rng.permutation(w)
            sel = np.einsum("s,hsd->hd", wp - wp.mean(), z0) / len(w)
            num += xf(sel, dz)
        null[b] = num / den
    p = float((np.abs(null) >= abs(obs)).mean())
    return float(obs), p, null


def jackknife(P: Period, stat_fn, min_agents: int = 4) -> tuple[float, float, int]:
    """Leave-one-agent-out jackknife SE of stat_fn(Period) -> float. Returns (full, se, n_agents)."""
    agents = sorted({a for v in P.active.values() for a in v})
    full = stat_fn(P)
    vals = []
    for a in agents:
        Q = P.drop({a})
        if len(transitions(Q)) < 1:
            continue
        try:
            v = stat_fn(Q)
        except (ZeroDivisionError, ValueError):
            continue
        if np.isfinite(v):
            vals.append(v)
    n = len(vals)
    if n < min_agents or not np.isfinite(full):
        return full, np.nan, n
    vals = np.array(vals)
    se = np.sqrt((n - 1) / n * ((vals - vals.mean()) ** 2).sum())
    return full, float(se), n


def perm_sel_all(P: Period, tag: str, n_perm: int = 500, seed: int = 0, kind="read") -> dict:
    """Selection tests against the w-permutation null (w shuffled among stayers within each transition):
    energy share s_sel, cumulative share s_sel_cum, and the cross-fitted selection magnitude
    M = sum_t xf(Sel_t, Sel_t) / sum_t xf(dz_t, dz_t) (direction-free: any covariance of influence with trait)."""
    rng = np.random.default_rng(seed)
    trs = transitions(P)
    pre = []
    for d0, d1 in trs:
        r = price_transition(P, d0, d1, tags=[tag], kind=kind)[0]
        S = sorted(set(P.active[d0]) & set(P.active[d1]))
        al_s, al_n, al_u, _ = parentage(P, d1, S, kind)
        w = (al_s + al_n + al_u).sum(0)
        z0 = np.stack([_z(P, tag, S, d0, h) for h in range(3)])
        pre.append((w, z0, r[tag]["dz"]))
    den = sum(xf(dz, dz) for _, _, dz in pre)
    dzc = sum(dz for _, _, dz in pre)
    denc = xf(dzc, dzc)

    def stats(perm: bool):
        e = 0.0; m = 0.0; selc = 0.0
        for w, z0, dz in pre:
            ww = rng.permutation(w) if perm else w
            sel = np.einsum("s,hsd->hd", ww - ww.mean(), z0) / len(w)
            e += xf(sel, dz); m += xf(sel, sel); selc = selc + sel
        return e / den, xf(selc, dzc) / denc if denc > 0 else np.nan, m / den
    obs = stats(False)
    null = np.array([stats(True) for _ in range(n_perm)])
    out = {}
    for k, nm in enumerate(("energy", "cum", "mag")):
        o = obs[k]
        nl = null[:, k]
        if nm == "mag":
            p = float((nl >= o).mean())
        else:
            p = float((np.abs(nl) >= abs(o)).mean())
        out[nm] = dict(obs=float(o), p=p, null_mean=float(np.nanmean(nl)), null_q95=float(np.nanquantile(np.abs(nl), 0.95)))
    return out
