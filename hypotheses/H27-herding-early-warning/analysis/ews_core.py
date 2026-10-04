"""H27 core: herding-onset rule, early-warning indicators, placebo segments, operator alarm evaluation.

Everything here works on one share series per project, x_a(w) = k_a(w) / n(w) (NaN where n(w) < N_OBS),
indexed by a global active-time window w. Used identically by analysis/synthetic.py (kinetic Potts at village
sampling), analysis/explore.py (non-holdout periods) and analysis/confirm_holdout.py (frozen rule).

Parameters are the pre-registered values from the card (README.md, "Observables"), written 2026-10-04 before
any synthetic or real-data run. Do not change them here; robustness variants pass overrides explicitly.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv


@dataclass(frozen=True)
class Params:
    # O1 onset rule
    th_hi: float = 0.5        # onset share
    k_min: int = 3            # agents on the project at onset
    n_onset: int = 4          # labeled agents at onset
    base_w: int = 4           # baseline windows before onset
    base_skip: int = 0        # gap between baseline and onset (O1-slow amendment: 4)
    th_base: float = 0.25     # baseline mean share
    pers_w: int = 4           # persistence windows from onset
    th_pers: float = 0.4      # persistence mean share
    n_obs: int = 3            # min labeled agents for a window to be observed
    # O2 indicators
    S: int = 24               # segment length (windows)
    L: int = 12               # rolling window inside the segment
    sigma: float = 4.0        # Gaussian detrending bandwidth (windows)
    flick: float = 0.3        # flicker threshold (up-crossings)
    min_obs_seg: float = 0.75
    min_obs_roll: float = 0.75
    min_pairs: int = 6
    min_tau: int = 8
    # matching ("low at t_e")
    match_w: int = 4
    th_match: float = 0.3
    # O3 placebo and O5 operator
    placebo_gap: int = 8
    placebo_step: int = 2
    horizon: int = 12
    x_floor: float = 0.05     # binomial standardization floor


P0 = Params()
P_W30 = replace(P0, S=16, L=8, horizon=6)
# Amendment 1 (2026-10-04, after the synthetic pilot, before any real data): onset-rule variant whose baseline is
# taken 1 h earlier ([w0-8, w0-5]) so rises spread over up to ~2 h (a deterministic fold's bottleneck) still count.
P_SLOW = replace(P0, base_skip=4)

INDICATORS = ("tau_ar1", "tau_sd", "tau_skew", "tau_flick", "flick_level", "composite", "tau_sd_binom",
              "mean_last4", "level_ar1", "level_sd")


# ------------------------------------------------------------------------------------------------ series

def shares(k: np.ndarray, n: np.ndarray, p: Params = P0) -> np.ndarray:
    """k: (T, q) agents per project, n: (T,) labeled agents. Returns x (T, q), NaN where n < n_obs."""
    k = np.asarray(k, float)
    n = np.asarray(n, float)
    with np.errstate(invalid="ignore", divide="ignore"):
        x = k / n[:, None]
    x[n < p.n_obs] = np.nan
    return x


def _nanmean_slice(v):
    v = v[~np.isnan(v)]
    return (v.mean(), len(v)) if len(v) else (np.nan, 0)


# ------------------------------------------------------------------------------------------------ O1 onsets

def find_onsets(k: np.ndarray, n: np.ndarray, win_in_day: np.ndarray | None = None, day: np.ndarray | None = None,
                p: Params = P0) -> list[dict]:
    """Pre-registered herding-onset rule (card O1). Returns dicts: project (0-based column), w0, flags."""
    x = shares(k, n, p)
    T, q = x.shape
    out = []
    last_day = None if day is None else int(np.max(day))
    for a in range(q):
        armed, last = True, -10**9
        for w in range(T):
            hi = w - p.base_skip
            lo = hi - p.base_w
            if lo < 0:
                continue
            bm, bn = _nanmean_slice(x[lo:hi, a])
            base_ok = bn >= 2 and bm <= p.th_base
            if not armed and lo > last and base_ok:
                armed = True
            if not armed or not base_ok:
                continue
            xa = x[w, a]
            if not (np.isfinite(xa) and xa >= p.th_hi and k[w, a] >= p.k_min and n[w] >= p.n_onset):
                continue
            pm, pn = _nanmean_slice(x[w:w + p.pers_w, a])
            if pn < 2 or pm < p.th_pers:
                continue
            out.append(dict(project=a, w0=w, x0=float(xa), k0=int(k[w, a]), n0=int(n[w]), base_mean=float(bm),
                            pers_mean=float(pm),
                            day_start=bool(win_in_day is not None and win_in_day[w] <= 1),
                            last_day=bool(day is not None and day[w] == last_day)))
            armed, last = False, w
    return out


# ------------------------------------------------------------------------------------------------ O2 indicators

def _gauss_matrix(S, sigma):
    i = np.arange(S)
    return np.exp(-0.5 * ((i[:, None] - i[None, :]) / sigma) ** 2)


def _kendall_tau_time(Y: np.ndarray, min_def: int) -> np.ndarray:
    """Kendall tau_b of each row of Y (M, R) against time (no ties in time); NaN entries skipped.
    Rows with fewer than min_def defined values get 0 ('no trend', card rule)."""
    M, R = Y.shape
    iu, ju = np.triu_indices(R, 1)
    yi, yj = Y[:, iu], Y[:, ju]
    both = ~(np.isnan(yi) | np.isnan(yj))
    d = np.where(both, np.sign(yj - yi), 0.0)
    n0 = both.sum(1)
    ties = (both & (yi == yj)).sum(1)
    num = d.sum(1)
    den = np.sqrt(n0 * np.maximum(n0 - ties, 0))
    with np.errstate(invalid="ignore", divide="ignore"):
        tau = np.where(den > 0, num / den, 0.0)
    ndef = (~np.isnan(Y)).sum(1)
    tau[ndef < min_def] = 0.0
    return tau


def segment_indicators(x: np.ndarray, n: np.ndarray, ends: np.ndarray, p: Params = P0) -> dict[str, np.ndarray]:
    """Indicators for segments of series x (T,) ending at each index in `ends` (M,), length p.S.

    Returns arrays (M,) for every name in INDICATORS plus 'valid' (enough observed windows) and 'matched'
    (low at t_e). Segments with end < S - 1 are invalid."""
    x = np.asarray(x, float)
    n = np.asarray(n, float)
    ends = np.asarray(ends, int)
    M, S, L = len(ends), p.S, p.L
    res = {k: np.full(M, np.nan) for k in INDICATORS}
    res["valid"] = np.zeros(M, bool)
    res["matched"] = np.zeros(M, bool)
    if M == 0:
        return res
    ok_end = ends >= S - 1
    e = np.where(ok_end, ends, S - 1)
    idx = e[:, None] - (S - 1) + np.arange(S)[None, :]
    X = x[idx]
    Nn = n[idx]
    mask = ~np.isnan(X)
    valid = ok_end & (mask.mean(1) >= p.min_obs_seg)
    # matching: low at t_e
    last = X[:, -p.match_w:]
    with np.errstate(invalid="ignore"):
        ml = np.nanmean(np.where(np.isnan(last), np.nan, last), axis=1) if last.size else np.full(M, np.nan)
    matched = np.isfinite(ml) & (ml <= p.th_match)
    res["mean_last4"] = ml
    # detrend
    G = _gauss_matrix(S, p.sigma)
    X0 = np.where(mask, X, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        trend = (X0 @ G.T) / (mask.astype(float) @ G.T)
    R = np.where(mask, X - trend, np.nan)
    tf = np.clip(np.where(np.isfinite(trend), trend, p.x_floor), p.x_floor, 1 - p.x_floor)
    with np.errstate(invalid="ignore", divide="ignore"):
        Rb = R / np.sqrt(tf * (1 - tf) / np.maximum(Nn, 1))
    # rolling windows (M, Rn, L)
    Rw = swv(R, L, axis=1)
    Rbw = swv(Rb, L, axis=1)
    Mw = swv(mask, L, axis=1)
    cnt = Mw.sum(-1)
    okw = cnt >= np.ceil(p.min_obs_roll * L)

    def roll_sd(A):
        m = np.nansum(A, -1) / np.maximum(cnt, 1)
        dev = A - m[..., None]
        v = np.nansum(dev ** 2, -1) / np.maximum(cnt - 1, 1)
        return np.sqrt(v), dev, v

    sd, dev, var = roll_sd(Rw)
    sdb, _, _ = roll_sd(Rbw)
    # lag-1 autocorrelation on observed consecutive pairs (Pearson on lagged pairs)
    d0, d1 = dev[..., :-1], dev[..., 1:]
    pr = ~(np.isnan(d0) | np.isnan(d1))
    npair = pr.sum(-1)
    a0 = np.where(pr, d0, 0.0)
    a1 = np.where(pr, d1, 0.0)
    num = (a0 * a1).sum(-1)
    den = np.sqrt((a0 ** 2).sum(-1) * (a1 ** 2).sum(-1))
    with np.errstate(invalid="ignore", divide="ignore"):
        ar1 = np.where((den > 1e-12) & (npair >= p.min_pairs), num / den, np.nan)
    # skewness
    with np.errstate(invalid="ignore", divide="ignore"):
        m2 = np.nansum(dev ** 2, -1) / np.maximum(cnt, 1)
        m3 = np.nansum(dev ** 3, -1) / np.maximum(cnt, 1)
        sk = np.where(m2 > 1e-12, m3 / m2 ** 1.5, np.nan)
    # flicker: up-crossings of p.flick on the raw share
    up = (X[:, :-1] < p.flick) & (X[:, 1:] >= p.flick)  # NaN compares False
    upw = swv(up, L - 1, axis=1).sum(-1).astype(float)  # pairs inside each rolling window
    sd = np.where(okw & (sd > 1e-12), sd, np.nan)
    sdb = np.where(okw & np.isfinite(sdb) & (sdb > 1e-12), sdb, np.nan)
    ar1 = np.where(okw, ar1, np.nan)
    sk = np.where(okw, sk, np.nan)
    upw = np.where(okw, upw, np.nan)
    res["tau_ar1"] = _kendall_tau_time(ar1, p.min_tau)
    res["tau_sd"] = _kendall_tau_time(sd, p.min_tau)
    res["tau_skew"] = _kendall_tau_time(sk, p.min_tau)
    res["tau_flick"] = _kendall_tau_time(upw, p.min_tau)
    res["tau_sd_binom"] = _kendall_tau_time(sdb, p.min_tau)
    res["composite"] = res["tau_ar1"] + res["tau_sd"]
    res["flick_level"] = up.sum(1).astype(float)
    with np.errstate(invalid="ignore"):
        res["level_ar1"] = np.nanmean(ar1[:, -1:], 1) if ar1.shape[1] else np.nan
        res["level_sd"] = np.nanmean(sd[:, -1:], 1) if sd.shape[1] else np.nan
    res["valid"] = valid
    res["matched"] = matched
    return res


# ------------------------------------------------------------------------------------------------ O3/O4 segments

def onset_and_placebo_segments(k, n, onsets, lead: int, p: Params = P0, extra_series=None):
    """Rows (dicts) of onset segments (t_e = w0 - lead) and placebo segments for every project.

    Placebo: t_e on a grid of p.placebo_step, no onset of that project with w0 in [t_e - S + 1, t_e + lead + gap].
    Only valid & matched segments are returned (others are counted in the 'dropped' tallies)."""
    x = shares(k, n, p)
    T, q = x.shape
    rows, dropped = [], dict(onset_short=0, onset_invalid=0, onset_unmatched=0)
    by_proj = {a: [o["w0"] for o in onsets if o["project"] == a] for a in range(q)}
    for a in range(q):
        on = by_proj[a]
        ends_on = np.array([w0 - lead for w0 in on], int)
        grid = np.arange(p.S - 1, T, p.placebo_step)
        keep = []
        for te in grid:
            if any(te - p.S + 1 <= w0 <= te + lead + p.placebo_gap for w0 in on):
                continue
            keep.append(te)
        ends_pl = np.array(keep, int)
        for kind, ends in (("onset", ends_on), ("placebo", ends_pl)):
            if len(ends) == 0:
                continue
            ind = segment_indicators(x[:, a], n, ends, p)
            for j, te in enumerate(ends):
                if kind == "onset":
                    if te < p.S - 1:
                        dropped["onset_short"] += 1
                        continue
                    if not ind["valid"][j]:
                        dropped["onset_invalid"] += 1
                        continue
                    if not ind["matched"][j]:
                        dropped["onset_unmatched"] += 1
                        continue
                elif not (ind["valid"][j] and ind["matched"][j]):
                    continue
                r = dict(kind=kind, project=a, t_e=int(te), lead=lead)
                r.update({kk: float(ind[kk][j]) for kk in INDICATORS})
                rows.append(r)
    return rows, dropped


def concentration_segments(k, n, onsets, lead: int, p: Params = P0):
    """O7: indicators on the Simpson concentration C(w) = sum_a x_a^2; onset segments before swarm onsets,
    placebos with no onset of any project in (t_e, t_e + lead + gap] and inside the segment, all projects low."""
    x = shares(k, n, p)
    T, q = x.shape
    C = np.nansum(x ** 2, 1)
    C[np.isnan(x).all(1)] = np.nan
    w0s = sorted({o["w0"] for o in onsets})
    ends_on = np.array([w - lead for w in w0s], int)
    grid = np.arange(p.S - 1, T, p.placebo_step)
    ends_pl = np.array([te for te in grid if not any(te - p.S + 1 <= w <= te + lead + p.placebo_gap for w in w0s)], int)
    pc = replace(p, th_match=np.inf)  # matching done on project shares below

    def allow(te):
        lo = max(0, te - p.match_w + 1)
        with np.errstate(invalid="ignore"):
            m = np.nanmean(x[lo:te + 1], 0)
        return bool(np.all(~np.isfinite(m) | (m <= p.th_match)))

    rows = []
    for kind, ends in (("onset", ends_on), ("placebo", ends_pl)):
        ends = np.array([e for e in ends if e >= p.S - 1], int)
        if len(ends) == 0:
            continue
        ind = segment_indicators(C, n, ends, pc)
        for j, te in enumerate(ends):
            if not ind["valid"][j] or not allow(te):
                continue
            r = dict(kind=kind, t_e=int(te), lead=lead)
            r.update({kk: float(ind[kk][j]) for kk in INDICATORS})
            rows.append(r)
    return rows


# ------------------------------------------------------------------------------------------------ O5/O6 operator

def all_window_indicators(k, n, p: Params = P0):
    """Indicators at every window end t for every project: dict name -> (T, q) arrays, plus valid/matched."""
    x = shares(k, n, p)
    T, q = x.shape
    ends = np.arange(T)
    out = {}
    for a in range(q):
        ind = segment_indicators(x[:, a], n, ends, p)
        for kk, v in ind.items():
            out.setdefault(kk, np.zeros((T, q), dtype=v.dtype))[:, a] = v
    out["x"] = x
    return out


def alarms(ind, k, rule: str, tau_star: float | None = None, p: Params = P0):
    """Boolean (T, q) alarm array for a rule, evaluated only where valid & matched (the 'watchable' set)."""
    x = ind["x"]
    T, q = x.shape
    watch = ind["valid"] & ind["matched"]
    if rule == "ews":
        al = (ind["tau_ar1"] > tau_star) & (ind["tau_sd"] > tau_star)
    elif rule == "ews_sd":
        al = ind["tau_sd"] > tau_star
    elif rule == "level":
        al = np.nan_to_num(x, nan=0.0) >= p.flick
    elif rule == "momentum":
        kk = np.asarray(k, float)
        d = np.zeros_like(kk)
        d[2:] = kk[2:] - kk[:-2]
        al = d >= 2
    else:
        raise ValueError(rule)
    return al & watch, watch


def score_alarms(al, watch, onsets, p: Params = P0):
    """Hit rate, false alarms and lead times for one period. Hit horizon [w0 - H, w0 - 1]."""
    T, q = al.shape
    H = p.horizon
    on_by = {a: sorted(o["w0"] for o in onsets if o["project"] == a) for a in range(q)}
    hits, warnable, leads = 0, 0, []
    per_onset = []
    for o in onsets:
        a, w0 = o["project"], o["w0"]
        lo, hi = max(0, w0 - H), w0  # [lo, hi)
        win_watch = watch[lo:hi, a]
        wa = bool(win_watch.any())
        warnable += wa
        aw = np.where(al[lo:hi, a])[0]
        hit = len(aw) > 0
        lead = (w0 - (lo + aw[0])) if hit else None
        hits += hit
        if hit:
            leads.append(lead)
        per_onset.append(dict(project=a, w0=w0, warnable=wa, hit=hit, lead_windows=lead))
    # false alarms: alarm at t with no onset of a in (t, t + H]
    fa, neg, n_alarm, tp_alarm = 0, 0, 0, 0
    for a in range(q):
        on = np.array(on_by[a], int)
        for t in np.where(watch[:, a])[0]:
            fut = bool(((on > t) & (on <= t + H)).any()) if len(on) else False
            if al[t, a]:
                n_alarm += 1
                tp_alarm += fut
                fa += not fut
            if not fut:
                neg += 1
    return dict(n_onsets=len(onsets), warnable=warnable, hits=hits, leads=leads, false_alarms=fa, negatives=neg,
                n_alarms=n_alarm, true_alarms=tp_alarm, per_onset=per_onset)


def swarm_score(al, watch, onsets, p: Params = P0):
    """Project-agnostic: alarm if any project alarms; hit if alarm in [w0 - H, w0 - 1] for an onset of any project."""
    T, q = al.shape
    H = p.horizon
    A = al.any(1)
    Wt = watch.any(1)
    w0s = np.array(sorted({o["w0"] for o in onsets}), int)
    hits, leads = 0, []
    for w0 in w0s:
        lo = max(0, w0 - H)
        aw = np.where(A[lo:w0])[0]
        if len(aw):
            hits += 1
            leads.append(w0 - (lo + aw[0]))
    fa = neg = 0
    for t in np.where(Wt)[0]:
        fut = bool(((w0s > t) & (w0s <= t + H)).any()) if len(w0s) else False
        if A[t] and not fut:
            fa += 1
        if not fut:
            neg += 1
    return dict(n_onsets=len(w0s), hits=hits, leads=leads, false_alarms=fa, negatives=neg, alarm_windows=int(A.sum()))


def shifted_hits(al, watch, onsets, rng, n_shift=500, p: Params = P0):
    """N2: rate-matched random alarm. Circularly shift each project's alarm series (over its watchable windows)."""
    T, q = al.shape
    out = np.zeros(n_shift, int)
    for s in range(n_shift):
        al2 = np.zeros_like(al)
        for a in range(q):
            idx = np.where(watch[:, a])[0]
            if len(idx) == 0:
                continue
            vals = al[idx, a]
            al2[idx, a] = np.roll(vals, rng.integers(len(idx)))
        out[s] = score_alarms(al2, watch, onsets, p)["hits"]
    return out


# ------------------------------------------------------------------------------------------------ stats

def auc(pos, neg):
    """Mann-Whitney AUC = P(pos > neg) + 0.5 P(pos = neg). NaN if either side empty. Vectorized."""
    pos = np.asarray(pos, float)
    neg = np.asarray(neg, float)
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    ns = np.sort(neg)
    lt = np.searchsorted(ns, pos, side="left")
    le = np.searchsorted(ns, pos, side="right")
    return float((lt + 0.5 * (le - lt)).sum() / (len(pos) * len(neg)))


def cluster_bootstrap_auc(groups: dict, key: str, rng, n_boot=2000):
    """groups: cluster id -> (pos array, neg array). Resample clusters with replacement."""
    ids = list(groups)
    if not ids:
        return np.nan, (np.nan, np.nan)
    est = auc(np.concatenate([groups[g][0] for g in ids]), np.concatenate([groups[g][1] for g in ids]))
    bs = []
    for _ in range(n_boot):
        pick = rng.choice(len(ids), len(ids), replace=True)
        pos = np.concatenate([groups[ids[i]][0] for i in pick])
        neg = np.concatenate([groups[ids[i]][1] for i in pick])
        v = auc(pos, neg)
        if np.isfinite(v):
            bs.append(v)
    if not bs:
        return est, (np.nan, np.nan)
    return est, (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))


def display_project(name, label=None) -> str:
    """Short display name for an artifact project. Google Docs / Sheets / Drive / Forms ids are hidden."""
    if not isinstance(name, str):
        return "?"
    tag = f" #{label}" if label is not None else ""
    for key, nm in (("docs.google.com/document", "Google doc"), ("docs.google.com/spreadsheets", "Google sheet"),
                    ("docs.google.com/presentation", "Google slides"), ("drive.google.com", "Drive file"),
                    ("forms.gle", "Google form"), ("docs.google.com/forms", "Google form")):
        if key in name:
            return nm + tag
    return name.rstrip("/").split("/")[-1]
