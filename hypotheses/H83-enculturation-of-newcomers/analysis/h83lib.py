"""H83 core estimators (shared by synthetic.py, replication.py, natives.py and confirm.py).

Everything works on agent-day aggregates of unit statement vectors:
  M[i,d]  mean of the agent's statement vectors that day; a = M . V_hat equals the mean statement cosine with V_hat
  Fm, Fsq mean style vector and mean squared style norm (for the per-message squared style distance)
Village vector V_d: agent-weighted mean of present veterans' M (leave-own-out for a veteran).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H83-enculturation-of-newcomers"
E_WIN = (2, 4)
L_WIN = (8, 14)
MIN_DAYS, MIN_STMTS = 2, 5          # newcomer, per window
VET_MIN_DAYS, VET_MIN_STMTS = 1, 3  # placebo veteran, per window
MIN_PLACEBO = 3
MM_GAP = 40                          # mismatched village: >= 40 village days away
EPS = 1e-12


# ----------------------------------------------------------------------------- loading
def load(model: str = "bge", variant: str = "vec"):
    st = pl.read_parquet(DATA / "statements.parquet")
    X = np.load(DATA / f"{variant}_{model}.npy").astype(np.float32)
    F = np.load(DATA / "style.npy").astype(np.float32)
    assert X.shape[0] == st.height == F.shape[0]
    assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    return st, X, F


def calendar_days() -> list[str]:
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date")
    return cal["pt_date"].sort().to_list()


def newcomers() -> pl.DataFrame:
    return pl.read_parquet(DATA / "newcomers.parquet")


# ----------------------------------------------------------------------------- aggregates
class AD:
    """Agent-day aggregates. Rows sorted by (pt_date, agent)."""

    def __init__(self, st: pl.DataFrame, X: np.ndarray, F: np.ndarray | None = None):
        key = st.select("agent", "pt_date").with_row_index("row")
        g = (key.group_by("agent", "pt_date").agg(pl.col("row")).sort("pt_date", "agent"))
        self.df = g.select("agent", "pt_date").join(
            st.group_by("agent", "pt_date").agg(pl.len().alias("n"), pl.col("regime").first(),
                                                pl.col("goal_no").first(), pl.col("day_room").first(),
                                                pl.col("tau").first(), pl.col("veteran").first(),
                                                pl.col("lab").first()),
            on=["agent", "pt_date"], how="left", maintain_order="left").with_row_index("ad")
        rows = g["row"].to_list()
        n = np.array([len(r) for r in rows])
        idx = np.concatenate(rows)
        seg = np.repeat(np.arange(len(rows)), n)
        self.n = n
        self.M = np.zeros((len(rows), X.shape[1]), dtype=np.float64)
        np.add.at(self.M, seg, X[idx].astype(np.float64))
        self.M /= n[:, None]
        if F is not None:
            self.Fm = np.zeros((len(rows), F.shape[1]))
            np.add.at(self.Fm, seg, F[idx].astype(np.float64))
            self.Fm /= n[:, None]
            self.Fsq = np.zeros(len(rows))
            np.add.at(self.Fsq, seg, (F[idx].astype(np.float64) ** 2).sum(1))
            self.Fsq /= n
        self.agent = self.df["agent"].to_numpy()
        self.day = np.array(self.df["pt_date"].to_list())
        self.vet = self.df["veteran"].to_numpy()
        self.room = self.df["day_room"].fill_null(-1).to_numpy()
        self.regime = np.array(self.df["regime"].to_list())
        self.tau = self.df["tau"].fill_null(-1).to_numpy()
        self.lab = np.array(self.df["lab"].to_list())
        self.loc = {(a, d): k for k, (a, d) in enumerate(zip(self.agent, self.day))}
        days = sorted(set(self.day))
        self.by_day = {d: np.flatnonzero(self.day == d) for d in days}


def village(ad: AD, field: str = "M", room: int | None = None, who: np.ndarray | None = None):
    """day -> (sum vector over veterans' agent-day means, count, member rows). who overrides the veteran mask."""
    A = getattr(ad, field)
    out = {}
    mask = ad.vet if who is None else who
    for d, rows in ad.by_day.items():
        r = rows[mask[rows]]
        if room is not None:
            r = r[ad.room[r] == room]
        if len(r):
            out[d] = (A[r].sum(0), len(r), set(r.tolist()))
    return out


def centroid(vill: dict, d: str, exclude: int | None, A: np.ndarray):
    """Leave-own-out mean of the village on day d (None if fewer than 1 member remains)."""
    if d not in vill:
        return None
    s, c, mem = vill[d]
    if exclude is not None and exclude in mem:
        if c <= 1:
            return None
        return (s - A[exclude]) / (c - 1)
    return s / c


def unit(v):
    return v / max(np.linalg.norm(v), EPS)


def align(ad: AD, k: int, vill: dict, d: str | None = None, field: str = "M") -> float | None:
    """a = M[k] . V_hat with a matched (c - 1)-member centroid on target day d (default: the row's own day).
    If the row's agent is a member of the target-day village, its own row is left out; otherwise the alignment is
    averaged over all single-member exclusions, so members and non-members see centroids of the same size."""
    A = getattr(ad, field)
    d = d or ad.day[k]
    if d not in vill:
        return None
    s, c, mem = vill[d]
    own = ad.loc.get((int(ad.agent[k]), d))
    if own is not None and own in mem:
        if c <= 1:
            return None
        return float(A[k] @ unit((s - A[own]) / (c - 1)))
    if c <= 1:
        return None
    m = np.fromiter(mem, int)
    U = s[None, :] - A[m]
    U /= np.maximum(np.linalg.norm(U, axis=1, keepdims=True), EPS)
    return float((U @ A[k]).mean())


def style_dist(ad: AD, k: int, vill_style: dict, d: str | None = None) -> float | None:
    """Mean per-message squared distance of the agent-day's style vectors to the veterans' style centroid, with the
    same matched (c - 1)-member rule as align()."""
    d = d or ad.day[k]
    if d not in vill_style:
        return None
    s, c, mem = vill_style[d]
    if c <= 1:
        return None
    own = ad.loc.get((int(ad.agent[k]), d))
    if own is not None and own in mem:
        Cs = ((s - ad.Fm[own]) / (c - 1))[None, :]
    else:
        m = np.fromiter(mem, int)
        Cs = (s[None, :] - ad.Fm[m]) / (c - 1)
    return float(np.mean(ad.Fsq[k] - 2 * Cs @ ad.Fm[k] + (Cs * Cs).sum(1)))


# ----------------------------------------------------------------------------- windows
def window_days(join_day: str, days: list[str], lo: int, hi: int) -> list[str]:
    after = [d for d in days if d >= join_day]
    return after[lo - 1:hi]


def mismatch_map(ad: AD, vill: dict, days: list[str], gap: int = MM_GAP, min_vet: int = 3) -> dict:
    """day -> the nearest same-regime day >= gap village days away with >= min_vet veterans."""
    pos = {d: i for i, d in enumerate(days)}
    reg = {d: ad.regime[rows[0]] for d, rows in ad.by_day.items()}
    cand = [d for d in vill if vill[d][1] >= min_vet]
    out = {}
    for d in vill:
        best = None
        for e in cand:
            if reg[e] != reg[d] or abs(pos[e] - pos[d]) < gap:
                continue
            if best is None or abs(pos[e] - pos[d]) < abs(pos[best] - pos[d]):
                best = e
        if best is not None:
            out[d] = best
    return out


def stat_rows(ad: AD, agent: int, days_: list[str]):
    return [ad.loc[(agent, d)] for d in days_ if (agent, d) in ad.loc]


def did_join(ad: AD, agent: int, Ed: list[str], Ld: list[str], fn, vet_mask=None, need_placebo=MIN_PLACEBO):
    """Generic difference in differences. fn(k) -> value for agent-day row k (or None).
    Returns dict with newcomer E/L means, placebo E/L means, delta, n placebo; or None if ineligible."""
    kE = [k for k in stat_rows(ad, agent, Ed)]
    kL = [k for k in stat_rows(ad, agent, Ld)]
    if len(kE) < MIN_DAYS or len(kL) < MIN_DAYS or ad.n[kE].sum() < MIN_STMTS or ad.n[kL].sum() < MIN_STMTS:
        return None
    vE = [fn(k) for k in kE]; vL = [fn(k) for k in kL]
    vE = [v for v in vE if v is not None]; vL = [v for v in vL if v is not None]
    if len(vE) < MIN_DAYS or len(vL) < MIN_DAYS:
        return None
    dE = [ad.day[k] for k in kE]; dL = [ad.day[k] for k in kL]
    vm = ad.vet if vet_mask is None else vet_mask
    vets = set()
    for d in dE + dL:
        vets |= {int(ad.agent[r]) for r in ad.by_day[d] if vm[r]}
    pl_d = []
    for j in sorted(vets):
        jE = [ad.loc[(j, d)] for d in dE if (j, d) in ad.loc and vm[ad.loc[(j, d)]]]
        jL = [ad.loc[(j, d)] for d in dL if (j, d) in ad.loc and vm[ad.loc[(j, d)]]]
        if len(jE) < VET_MIN_DAYS or len(jL) < VET_MIN_DAYS or ad.n[jE].sum() < VET_MIN_STMTS \
                or ad.n[jL].sum() < VET_MIN_STMTS:
            continue
        a = [fn(k) for k in jE]; b = [fn(k) for k in jL]
        a = [v for v in a if v is not None]; b = [v for v in b if v is not None]
        if a and b:
            pl_d.append((np.mean(a), np.mean(b)))
    if len(pl_d) < need_placebo:
        return None
    pE = np.mean([x for x, _ in pl_d]); pL = np.mean([y for _, y in pl_d])
    nE, nL = float(np.mean(vE)), float(np.mean(vL))
    return {"new_E": nE, "new_L": nL, "vet_E": float(pE), "vet_L": float(pL), "gap_E": nE - pE, "gap_L": nL - pL,
            "delta": (nL - nE) - (pL - pE), "n_placebo": len(pl_d), "n_days_E": len(vE), "n_days_L": len(vL),
            "n_stmts_E": int(ad.n[kE].sum()), "n_stmts_L": int(ad.n[kL].sum())}


# ----------------------------------------------------------------------------- family baselines
def family_baselines(ad: AD, newc: pl.DataFrame, days: list[str]):
    """Per regime: newcomer -> its tau=1 agent-day row (if observed). Returns {agent: (row, lab, regime)}."""
    out = {}
    for a, lab, jd in newc.select("agent", "lab", "join_day").iter_rows():
        if jd is None:
            continue
        d1 = window_days(jd, days, 1, 1)
        if d1 and (a, d1[0]) in ad.loc:
            k = ad.loc[(a, d1[0])]
            out[int(a)] = (k, lab, ad.regime[k])
    return out


EXCLUDE_SAME_DAY = False   # post hoc PH1: drop baseline newcomers who joined on the same day (shared tau-1 day field)


def fam_vectors(ad: AD, base: dict, agent: int, field: str = "M"):
    """F_f (other same-family newcomers, same regime) and F_notf (newcomers of other families, same regime)."""
    if agent not in base:
        return None
    A = getattr(ad, field)
    k0, lab, reg = base[agent]
    d0 = ad.day[k0]
    same = [k for b, (k, l2, r2) in base.items() if b != agent and l2 == lab and r2 == reg
            and not (EXCLUDE_SAME_DAY and ad.day[k] == d0)]
    other = [k for b, (k, l2, r2) in base.items() if l2 != lab and r2 == reg
             and not (EXCLUDE_SAME_DAY and ad.day[k] == d0)]
    if len(same) < 1 or len(other) < 2:
        return None
    return A[same].mean(0), A[other].mean(0), len(same), len(other)


# ----------------------------------------------------------------------------- one full pass
def run_all(st: pl.DataFrame, X: np.ndarray, F: np.ndarray | None, newc: pl.DataFrame, days: list[str],
            doses: pl.DataFrame | None = None, agents=None, with_family=True, with_mm=True) -> dict:
    ad = AD(st, X, F)
    vill = village(ad, "M")
    vill_s = village(ad, "Fm") if F is not None else None
    mm = mismatch_map(ad, vill, days) if with_mm else {}
    base = family_baselines(ad, newc, days) if with_family else {}
    res = {}
    for a, jd, jh in newc.select("agent", "join_day", "join_holdout").iter_rows():
        a = int(a)
        if agents is not None and a not in agents:
            continue
        if jd is None or jh:
            continue
        Ed = window_days(jd, days, *E_WIN); Ld = window_days(jd, days, *L_WIN)
        r = {"agent": a, "join_day": jd, "E_days": Ed, "L_days": Ld}
        g = did_join(ad, a, Ed, Ld, lambda k: align(ad, k, vill))
        if g is None:
            continue
        r["G"] = g
        d1 = window_days(jd, days, 1, 1)
        if d1 and (a, d1[0]) in ad.loc:
            k1 = ad.loc[(a, d1[0])]
            v1 = align(ad, k1, vill)
            vets1 = [align(ad, k, vill) for k in ad.by_day[d1[0]] if ad.vet[k]]
            vets1 = [v for v in vets1 if v is not None]
            if v1 is not None and vets1:
                r["G1"] = v1 - float(np.mean(vets1))
        if with_mm:
            def fmm(k):
                d = ad.day[k]
                return align(ad, k, vill, mm[d]) if d in mm else None
            r["G_mm"] = did_join(ad, a, Ed, Ld, fmm)
        if with_family:
            fv = fam_vectors(ad, base, a)
            if fv is not None:
                # unnormalized baselines (Amendment A1): a component shared by every newcomer's first day
                # (onboarding) cancels exactly in M.(F_f - F_notf); unit-normalizing would weight it by baseline size
                Ff, Fo = fv[0], fv[1]
                r["K"] = did_join(ad, a, Ed, Ld, lambda k: float(ad.M[k] @ (Ff - Fo)))
                r["K_nsame"], r["K_nother"] = fv[2], fv[3]
                if F is not None:
                    fs = fam_vectors(ad, base, a, "Fm")
                    Cf, Co = fs[0], fs[1]

                    def kst(k, Cf=Cf, Co=Co):
                        df_ = ad.Fsq[k] - 2 * ad.Fm[k] @ Cf + Cf @ Cf
                        do_ = ad.Fsq[k] - 2 * ad.Fm[k] @ Co + Co @ Co
                        return float(do_ - df_)          # > 0: closer to own family
                    r["K_style"] = did_join(ad, a, Ed, Ld, kst)
        if F is not None:
            r["S"] = did_join(ad, a, Ed, Ld, lambda k: style_dist(ad, k, vill_s))
        if doses is not None:
            d7 = window_days(jd, days, 1, 7)
            dd = doses.filter((pl.col("agent") == a) & pl.col("pt_date").is_in(d7))
            r["dose_vet_1_7"] = int(dd["items_vet"].sum()) if dd.height else 0
            r["dose_all_1_7"] = int(dd["items_agent"].sum()) if dd.height else 0
        res[a] = r
    return {"joins": res, "ad": ad, "vill": vill, "mm": mm, "base": base}


def boot_mean(x, B=10000, seed=0, clusters=None):
    """Mean with a percentile bootstrap; resamples clusters (e.g. join days: batch joins share windows) if given."""
    x = np.asarray(x, float)
    ok = np.isfinite(x)
    x = x[ok]
    if len(x) < 2:
        return (float(x.mean()) if len(x) else None, None, None, len(x))
    rng = np.random.default_rng(seed)
    if clusters is None:
        bs = x[rng.integers(0, len(x), (B, len(x)))].mean(1)
    else:
        cl = np.asarray(clusters)[ok]
        u = sorted(set(cl.tolist()))
        groups = [np.flatnonzero(cl == c) for c in u]
        sums = np.array([x[g].sum() for g in groups]); cnts = np.array([len(g) for g in groups])
        pick = rng.integers(0, len(u), (B, len(u)))
        bs = sums[pick].sum(1) / cnts[pick].sum(1)
    return float(x.mean()), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975)), len(x)


def summarize(joins: dict, key: str = "G", field: str = "delta", B=10000, seed=0):
    rows = [r for r in joins.values() if r.get(key)]
    vals = [r[key][field] for r in rows]
    m, lo, hi, n = boot_mean(vals, B, seed, clusters=[r["join_day"] for r in rows])
    pos = int(sum(v > 0 for v in vals))
    return {"mean": m, "lo": lo, "hi": hi, "n": n, "n_pos": pos, "n_clusters": len({r["join_day"] for r in rows})}


def entry_vector(ad: AD, agents, days: list[str], join_day: str, lo=1, hi=2):
    """Mean agent-day M of the given agents over tenure days lo..hi of a join (a fixed vector)."""
    dd = window_days(join_day, days, lo, hi)
    rows = [ad.loc[(a, d)] for a in agents for d in dd if (a, d) in ad.loc]
    return ad.M[rows].mean(0) if rows else None


def toward(ad: AD, agents, Ed, Ld, target: np.ndarray):
    """Mean over agents of the E->L change in alignment with a fixed target vector."""
    t = unit(target); out = []
    for a in agents:
        e = [ad.M[k] @ t for k in stat_rows(ad, a, Ed)]
        l_ = [ad.M[k] @ t for k in stat_rows(ad, a, Ld)]
        if e and l_:
            out.append(np.mean(l_) - np.mean(e))
    return float(np.mean(out)) if out else None


def spearman_perm(x, y, n_perm=10000, seed=0):
    from scipy.stats import spearmanr
    x = np.asarray(x, float); y = np.asarray(y, float)
    rho = spearmanr(x, y).statistic
    rng = np.random.default_rng(seed)
    null = np.array([spearmanr(x, rng.permutation(y)).statistic for _ in range(n_perm)])
    return float(rho), float((1 + (null >= rho).sum()) / (n_perm + 1))


# ----------------------------------------------------------------------------- natives
def day_gap(ad: AD, vill: dict, agents, d: str, pooled: bool = True):
    """Gap of the given agents on day d: (statement-weighted mean alignment) - (mean veteran alignment that day)."""
    rows = [ad.loc[(a, d)] for a in agents if (a, d) in ad.loc]
    if not rows or d not in ad.by_day:
        return None
    vals = [(align(ad, k, vill), ad.n[k]) for k in rows]
    vals = [(v, n) for v, n in vals if v is not None]
    vets = [align(ad, k, vill) for k in ad.by_day[d] if ad.vet[k]]
    vets = [v for v in vets if v is not None]
    if not vals or not vets:
        return None
    w = np.array([n for _, n in vals], float) if pooled else np.ones(len(vals))
    return float(np.dot([v for v, _ in vals], w) / w.sum() - np.mean(vets)), int(sum(n for _, n in vals))


def window_gap(ad, vill, agents, dd):
    g = [day_gap(ad, vill, agents, d) for d in dd]
    g = [x for x in g if x is not None]
    return (float(np.mean([x[0] for x in g])), int(sum(x[1] for x in g))) if g else None


def ne32_stats(ad, vill, days, triplet=(35, 36, 37), join="2026-07-09", others=None, post=(2, 6)):
    """N1 (Amendment A1): d1 = tau-1 gap of the isolated triplet minus the mean tau-1 gap of other newcomers;
    d2 = the triplet's tau1 -> tau post change minus the other newcomers' same change."""
    d1 = window_days(join, days, 1, 1)
    g1 = day_gap(ad, vill, triplet, d1[0]) if d1 else None
    gp = window_gap(ad, vill, triplet, window_days(join, days, *post))
    if g1 is None or gp is None:
        return None
    o1, oc = [], []
    for a, jd in (others or []):
        e = window_days(jd, days, 1, 1)
        x1 = day_gap(ad, vill, [a], e[0]) if e else None
        xp = window_gap(ad, vill, [a], window_days(jd, days, *post))
        if x1 is not None:
            o1.append(x1[0])
            if xp is not None:
                oc.append(xp[0] - x1[0])
    if not o1 or not oc:
        return None
    return {"G1_triplet": g1[0], "n1_triplet": g1[1], "Gpost_triplet": gp[0], "G1_others": float(np.mean(o1)),
            "chg_others": float(np.mean(oc)), "d1": g1[0] - float(np.mean(o1)),
            "d2": (gp[0] - g1[0]) - float(np.mean(oc)), "n_others": len(o1), "o1": o1, "oc": oc}


def room_villages(ad: AD):
    rooms = sorted({int(r) for r in ad.room if r >= 0})
    return {r: village(ad, "M", room=r) for r in rooms}


def room_R(ad, rv, k):
    """R = alignment with own-room veterans - alignment with the other room's veterans (the other structural room
    with the most veterans that day). None if the day has < 2 rooms with >= 2 veterans."""
    d = ad.day[k]; own = int(ad.room[k])
    if own < 0 or own not in rv or d not in rv[own] or rv[own][d][1] < 2:
        return None
    oth = [(rv[r][d][1], r) for r in rv if r != own and d in rv[r] and rv[r][d][1] >= 2]
    if not oth:
        return None
    r2 = max(oth)[1]
    a1 = align(ad, k, rv[own]); a2 = align(ad, k, rv[r2])
    if a1 is None or a2 is None:
        return None
    return a1 - a2


def rooms_native(ad, days, joins):
    """joins: list of (agent, join_day). Per join: mean R over tau 2-14 days with two rooms, and the DiD of R
    (E -> L) against veterans on the same days (min 1 day per window here: two-room days are few)."""
    rv = room_villages(ad)
    out = {}
    for a, jd in joins:
        Ed = window_days(jd, days, *E_WIN); Ld = window_days(jd, days, *L_WIN)
        allr = [room_R(ad, k, ) if False else room_R(ad, rv, k) for k in stat_rows(ad, a, window_days(jd, days, 2, 14))]
        allr = [x for x in allr if x is not None]
        kE = [k for k in stat_rows(ad, a, Ed) if room_R(ad, rv, k) is not None]
        kL = [k for k in stat_rows(ad, a, Ld) if room_R(ad, rv, k) is not None]
        res = {"R_mean": float(np.mean(allr)) if allr else None, "n_days": len(allr)}
        if kE and kL:
            rE = np.mean([room_R(ad, rv, k) for k in kE]); rL = np.mean([room_R(ad, rv, k) for k in kL])
            dE = [ad.day[k] for k in kE]; dL = [ad.day[k] for k in kL]
            vch = []
            vets = {int(ad.agent[r]) for d in dE + dL for r in ad.by_day[d] if ad.vet[r]}
            for j in vets:
                e = [room_R(ad, rv, ad.loc[(j, d)]) for d in dE if (j, d) in ad.loc]
                l_ = [room_R(ad, rv, ad.loc[(j, d)]) for d in dL if (j, d) in ad.loc]
                e = [x for x in e if x is not None]; l_ = [x for x in l_ if x is not None]
                if e and l_:
                    vch.append(np.mean(l_) - np.mean(e))
            if len(vch) >= MIN_PLACEBO:
                res.update({"R_E": float(rE), "R_L": float(rL), "dR": float((rL - rE) - np.mean(vch)),
                            "n_placebo": len(vch)})
        out[int(a)] = res
    return out
