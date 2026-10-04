"""H47 core library: room correlation function (room contrast C_B, conversational tier ratio G, partition ratios),
room-relabel / tier / partition permutation nulls, the room-localized centroid-shift detector (R1_loc) and the room
lead index (L) for leadership at goal changes.

Read-only imports (no shared version exists; listed in the card):
  hypotheses/H26-content-near-critical/analysis/h26lib.py   Panel, deviations, contributions, permute_rooms, orthobasis
  hypotheses/H36-reorganization-alarm/analysis/h36lib.py    trailing_z, auc, auc_ci (imported lazily by callers)

Thread caps: 2 (set before numpy import).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
           "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import zlib  # noqa: E402
from dataclasses import replace  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H47-room-coherence-length"
OUT = ROOT / "data/processed/H47-room-coherence-length"
SH = ROOT / "data/processed/shared"
FIG = HYP / "figures"
SEED = 20261004
sys.path.insert(0, str(ROOT / "hypotheses/H26-content-near-critical/analysis"))
import h26lib as H26  # noqa: E402  (read-only import)
from h26lib import Panel, contributions, deviations, orthobasis, permute_rooms  # noqa: E402,F401


def stable_seed(*parts) -> int:
    return zlib.crc32("|".join(map(str, parts)).encode()) & 0x7FFFFFFF


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(HYP)],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return [conv(x) for x in o.tolist()]
        if isinstance(o, float):
            return None if not np.isfinite(o) else o
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(x) for x in o]
        return o
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(conv(obj), indent=1))


# ------------------------------------------------------------------------------------------- pair-class correlations
def signal_var(C, w=None):
    """Per-agent split-half signal variance (day-weighted), as in h26lib.gains."""
    D = C["Cw"].shape[0]
    w = np.ones(D) if w is None else np.asarray(w, float)
    cnt = np.tensordot(w, C["s_cnt"], 1)
    S = np.tensordot(w, C["s_sum"], 1) / np.maximum(cnt, 1e-12)
    return np.where(cnt > 0, np.maximum(S, 1e-9), np.nan)


def class_rho(C, mask, typ="all", w=None):
    """Per-pair correlation for pairs in `mask` (N x N bool, any triangle; upper triangle used), from the same-room
    ('w'), cross-room ('c') or all ('all') slot sums. rho = sum C / sum n sqrt(S_i S_j)."""
    D = C["Cw"].shape[0]
    w = np.ones(D) if w is None else np.asarray(w, float)
    if typ == "all":
        num = np.tensordot(w, C["Cw"] + C["Cc"], 1); cnt = np.tensordot(w, C["Nw"] + C["Nc"], 1)
    else:
        num = np.tensordot(w, C["C" + typ], 1); cnt = np.tensordot(w, C["N" + typ], 1)
    S = signal_var(C, w)
    sq = np.sqrt(np.outer(S, S))
    m = np.triu(mask | mask.T, 1) & np.isfinite(sq) & (cnt > 0)
    den = (cnt * np.where(m, sq, 0)).sum()
    return (float(num[m].sum() / den) if den > 0 else np.nan), int(m.sum())


def coherence_from_C(C, tiers=None, w=None):
    """rho_w, rho_c, C_B, D_B (and G from mention tiers: N x N int, 1 = high, 0 = low, -1 = n/a)."""
    N = C["Cw"].shape[1]
    allm = np.ones((N, N), bool)
    rw, nw = class_rho(C, allm, "w", w)
    rc, nc = class_rho(C, allm, "c", w)
    out = dict(rho_w=rw, rho_c=rc, npair_w=nw, npair_c=nc,
               C_B=(rc / rw) if (np.isfinite(rc) and np.isfinite(rw) and rw > 0) else np.nan,
               D_B=(rw - rc) if np.isfinite(rc) else np.nan)
    if tiers is not None:
        rh, nh = class_rho(C, tiers == 1, "w", w)
        rl, nl = class_rho(C, tiers == 0, "w", w)
        out.update(rho_hi=rh, rho_lo=rl, n_hi=nh, n_lo=nl,
                   G=(rl / rh) if (np.isfinite(rl) and np.isfinite(rh) and rh > 0) else np.nan)
    return out


def mention_tiers(C, mw: dict):
    """Tier matrix over C['agents']: same-room pairs (Nw > 0 on any day) split at the median mention weight.
    high = m > median (m over same-room pairs); low = otherwise. mw: {(a, b): weight} with a < b agent codes."""
    ags = list(C["agents"]); N = len(ags)
    same = (C["Nw"].sum(0) > 0)
    same = same | same.T
    M = np.zeros((N, N))
    for i in range(N):
        for j in range(i + 1, N):
            a, b = sorted((int(ags[i]), int(ags[j])))
            M[i, j] = M[j, i] = mw.get((a, b), 0.0)
    iu = np.triu_indices(N, 1)
    vals = M[iu][same[iu]]
    T = np.full((N, N), -1, int)
    if vals.size < 4:
        return T, np.nan
    med = np.median(vals)
    T[same & (M > med)] = 1
    T[same & (M <= med)] = 0
    np.fill_diagonal(T, -1)
    if (T == 1).sum() == 0 or (T == 0).sum() == 0:
        return np.full((N, N), -1, int), med
    return T, med


def permute_tiers(T, rng):
    """N2: permute tier labels among same-room pairs (sizes kept)."""
    N = T.shape[0]
    iu = np.triu_indices(N, 1)
    v = T[iu].copy()
    ok = v >= 0
    v[ok] = rng.permutation(v[ok])
    out = np.full((N, N), -1, int)
    out[iu] = v
    out.T[iu] = v
    return out


def panel_coherence(P: Panel, level=1, mw=None, n_perm=300, rng=None, need_cross=True):
    """Observed coherence statistics + N1 room-relabel permutation (p for D_B, one-sided) + N2 tier permutation."""
    rng = np.random.default_rng(0) if rng is None else rng
    dX, dA, dB, okX, okS = deviations(P, level)
    C = contributions(P, dX, dA, dB, okX, okS)
    T, med = mention_tiers(C, mw) if mw is not None else (None, np.nan)
    obs = coherence_from_C(C, T if (T is not None and (T >= 0).any()) else None)
    obs["tier_median"] = med
    res = dict(obs=obs, C=C, tiers=T)
    if n_perm and need_cross and np.isfinite(obs["D_B"]):
        nul = []
        for _ in range(n_perm):
            r = permute_rooms(P, rng)
            Cp = contributions(P, dX, dA, dB, okX, okS, room=r)
            o = coherence_from_C(Cp)
            nul.append((o["D_B"], o["C_B"]))
        nul = np.array(nul, float)
        ok = np.isfinite(nul[:, 0])
        res["perm_DB"] = nul[ok, 0]
        res["p_DB"] = float((1 + (nul[ok, 0] >= obs["D_B"]).sum()) / (1 + ok.sum())) if ok.any() else np.nan
        res["null_CB_med"] = float(np.nanmedian(nul[:, 1]))
    if n_perm and T is not None and np.isfinite(obs.get("G", np.nan)):
        gn = []
        for _ in range(n_perm):
            o = coherence_from_C(C, permute_tiers(T, rng))
            gn.append(o["G"])
        gn = np.array(gn, float)
        gn = gn[np.isfinite(gn)]
        res["p_G_low"] = float((1 + (gn <= obs["G"]).sum()) / (1 + gn.size)) if gn.size else np.nan
    return res


def day_bootstrap(C, fn, B=300, rng=None):
    rng = np.random.default_rng(0) if rng is None else rng
    D = C["Cw"].shape[0]
    out = []
    for _ in range(B):
        w = np.bincount(rng.integers(0, D, D), minlength=D)
        out.append(fn(C, w))
    return np.array(out, float)


def partition_ratio(C, part: dict, w=None):
    """r_X = rho(cross-partition pairs) / rho(within-partition pairs), all slots (same- and cross-room sums).
    part: agent code -> partition label (agents missing are dropped)."""
    ags = list(C["agents"]); N = len(ags)
    lab = np.array([part.get(int(a), -1) for a in ags])
    ok = lab >= 0
    X = ok[:, None] & ok[None, :] & (lab[:, None] != lab[None, :])
    Wm = ok[:, None] & ok[None, :] & (lab[:, None] == lab[None, :])
    rx, nx = class_rho(C, X, "all", w)
    rw, nwp = class_rho(C, Wm, "all", w)
    return dict(rho_XP=rx, rho_WP=rw, n_XP=nx, n_WP=nwp,
                r_X=(rx / rw) if (np.isfinite(rx) and np.isfinite(rw) and rw > 0) else np.nan)


def permute_partition(part: dict, rng):
    ks = list(part.keys())
    vs = rng.permutation([part[k] for k in ks])
    return dict(zip(ks, vs))


# ------------------------------------------------------------------------------------------- detector (day level)
def r1_shift(m1, m0):
    n1, n0 = np.linalg.norm(m1), np.linalg.norm(m0)
    if n1 < 1e-12 or n0 < 1e-12:
        return np.nan
    return float(1 - m1 @ m0 / (n1 * n0))


def r1_loc(Vd: np.ndarray, Vp: np.ndarray, room_d: np.ndarray, room_p: np.ndarray, rng, n_rand=300, min_size=2):
    """Room-localized centroid shift. Rows = agents present on both days (Vd day-d vectors, Vp day-(d-1) vectors,
    centered and unit-normalized). Cohorts = groups by room on d and by room on d-1 (size >= min_size and < n).
    Returns (max z, list of per-cohort dicts)."""
    n = len(Vd)
    if n < 3:
        return np.nan, []
    cohorts = {}
    for tag, rr in (("d", room_d), ("p", room_p)):
        for r in np.unique(rr):
            if r < 0:
                continue
            idx = np.flatnonzero(rr == r)
            if min_size <= len(idx) < n:
                key = tuple(idx.tolist())
                cohorts.setdefault(key, []).append(f"{tag}{int(r)}")
    out = []
    null_cache = {}
    for idx, tags in cohorts.items():
        idx = np.array(idx)
        k = len(idx)
        D = r1_shift(Vd[idx].mean(0), Vp[idx].mean(0))
        if k not in null_cache:
            nd = np.empty(n_rand)
            for b in range(n_rand):
                s = rng.choice(n, k, replace=False)
                nd[b] = r1_shift(Vd[s].mean(0), Vp[s].mean(0))
            null_cache[k] = (np.nanmean(nd), np.nanstd(nd, ddof=1))
        mu, sd = null_cache[k]
        z = (D - mu) / sd if sd > 0 else np.nan
        out.append(dict(tags=tags, size=k, D=D, z=z))
    if not out:
        return np.nan, []
    zs = np.array([o["z"] for o in out], float)
    return (float(np.nanmax(zs)) if np.isfinite(zs).any() else np.nan), out


# ------------------------------------------------------------------------------------------- leadership (intraday)
def response_curves(tau, X, coh, pre, post, bin_min=15.0, nbins=8):
    """Per cohort c in {0,1}: y per statement = (x - pre_c).u_c/|post_c - pre_c|; binned means of y over the first
    nbins bins of width bin_min (minutes, tau >= 0). Returns (ybar (2, nbins), n (2, nbins))."""
    yb = np.full((2, nbins), np.nan); nb = np.zeros((2, nbins), int)
    b = np.floor(tau / bin_min).astype(int)
    for c in (0, 1):
        dlt = post[c] - pre[c]
        nrm = np.linalg.norm(dlt)
        if nrm < 1e-12:
            continue
        m = (coh == c) & (b >= 0) & (b < nbins)
        if not m.any():
            continue
        y = (X[m] - pre[c]) @ dlt / nrm**2
        for k in range(nbins):
            mk = b[m] == k
            nb[c, k] = int(mk.sum())
            if mk.any():
                yb[c, k] = float(y[mk].mean())
    return yb, nb


def lead_stats(yb, nb, min_n=3):
    """L = mean over common bins (>= min_n statements in both cohorts) of y_0 - y_1; T50 difference (bins) from a
    2-bin rolling mean (censored at nbins); positive = cohort 0 ahead."""
    common = (nb[0] >= min_n) & (nb[1] >= min_n)
    L = float(np.mean(yb[0, common] - yb[1, common])) if common.any() else np.nan

    def t50(y):
        yy = np.where(np.isfinite(y), y, np.nan)
        r = np.array([np.nanmean(yy[max(0, k - 1):k + 1]) if np.isfinite(yy[max(0, k - 1):k + 1]).any() else np.nan
                      for k in range(len(yy))])
        hit = np.flatnonzero(r >= 0.5)
        return float(hit[0]) if hit.size else float(len(yy))
    dT = t50(yb[1]) - t50(yb[0])   # positive = cohort 0 reaches 0.5 earlier
    return dict(L=L, dT50=dT, n_common=int(common.sum()))


def cohort_means(agent_of, X, coh_of_agent):
    """Statement-weighted mean of X per cohort (0/1) given a per-statement agent code array and agent->cohort."""
    c = np.array([coh_of_agent.get(int(a), -1) for a in agent_of])
    out = []
    for k in (0, 1):
        m = c == k
        out.append(X[m].mean(0) if m.any() else np.full(X.shape[1], np.nan))
    return np.array(out)


def lead_test(ev: dict, rng, n_perm=500, bin_min=15.0, nbins=8, min_n=3, n_boot=300):
    """ev: dict with arrays for kickoff-day statements (tau [min], X, agent), pre-day (Xpre, apre), post-days (Xpost,
    apost) and coh: agent -> 0/1. Observed L, dT50; cohort-relabel permutation p (two-sided on |stat|); agent
    bootstrap CI for L."""
    coh = ev["coh"]

    def stat(cmap):
        pre = cohort_means(ev["apre"], ev["Xpre"], cmap)
        post = cohort_means(ev["apost"], ev["Xpost"], cmap)
        c = np.array([cmap.get(int(a), -1) for a in ev["agent"]])
        yb, nb = response_curves(ev["tau"], ev["X"], c, pre, post, bin_min, nbins)
        return lead_stats(yb, nb, min_n), yb, nb
    obs, yb, nb = stat(coh)
    ags = sorted(coh.keys())
    labs = np.array([coh[a] for a in ags])
    pl_, pt_ = [], []
    for _ in range(n_perm):
        cm = dict(zip(ags, rng.permutation(labs)))
        s, _, _ = stat(cm)
        pl_.append(s["L"]); pt_.append(s["dT50"])
    pl_ = np.array(pl_, float); pt_ = np.array(pt_, float)
    okl = np.isfinite(pl_)
    pL = float((1 + (np.abs(pl_[okl]) >= abs(obs["L"])).sum()) / (1 + okl.sum())) if (okl.any() and np.isfinite(obs["L"])) else np.nan
    pT = float((1 + (np.abs(pt_) >= abs(obs["dT50"])).sum()) / (1 + len(pt_)))
    # agent bootstrap within cohort
    bs = []
    by = {0: [a for a in ags if coh[a] == 0], 1: [a for a in ags if coh[a] == 1]}
    for _ in range(n_boot):
        pick = {k: rng.choice(v, len(v), replace=True) for k, v in by.items() if len(v)}
        if len(pick) < 2:
            break
        # rebuild arrays with duplicated agents
        idx_k, idx_pre, idx_post, cm = [], [], [], {}
        newcode = 100000
        agent_new = []
        for k, arr in pick.items():
            for a in arr:
                newcode += 1
                cm[newcode] = k
                ik = np.flatnonzero(ev["agent"] == a); ipr = np.flatnonzero(ev["apre"] == a); ipo = np.flatnonzero(ev["apost"] == a)
                idx_k.append((ik, newcode)); idx_pre.append((ipr, newcode)); idx_post.append((ipo, newcode))
        def cat(pairs, Xa):
            ii = np.concatenate([p[0] for p in pairs]) if pairs else np.array([], int)
            aa = np.concatenate([np.full(len(p[0]), p[1]) for p in pairs]) if pairs else np.array([], int)
            return ii, aa
        ik, ak = cat(idx_k, None); ipr, apr = cat(idx_pre, None); ipo, apo = cat(idx_post, None)
        if len(ik) == 0:
            continue
        pre = cohort_means(apr, ev["Xpre"][ipr], cm); post = cohort_means(apo, ev["Xpost"][ipo], cm)
        c = np.array([cm[int(a)] for a in ak])
        ybb, nbb = response_curves(ev["tau"][ik], ev["X"][ik], c, pre, post, bin_min, nbins)
        bs.append(lead_stats(ybb, nbb, min_n)["L"])
    bs = np.array(bs, float); bs = bs[np.isfinite(bs)]
    ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs.size >= 20 else [np.nan, np.nan]
    return dict(obs=obs, p_L=pL, p_T50=pT, L_ci=ci, yb=yb, nb=nb, null_L_sd=float(np.nanstd(pl_)))
