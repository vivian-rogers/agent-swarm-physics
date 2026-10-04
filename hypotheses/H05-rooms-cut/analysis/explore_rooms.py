"""H05 exploratory analysis (non-holdout only): rooms as coupled blocks, room events, entropy production.

X2  within- vs. cross-room coupling in two-room windows (regime III #37-#39, #41, #42, #44; regime II #35, #36 as
    a labeled side check): pair-window excess lagged correlation, pair EP, kinetic-Ising J; room-label permutations.
X3  room events: pair DiD with assignment permutations and day bootstraps (merge 05-04, split 05-11, transfers
    04-02 / 04-27 / 05-25, #focus on/off, placebos), class-restricted EP DiD, onboarding isolations.
X4  pooled two-way fixed effects over all regime III pair-days: y = a_pair + g_day + b * co-location.
X5  entropy production per agent-hour per window (held-out ML bound and cross-fitted Newton bound).

Usage: uv run python hypotheses/H05-rooms-cut/analysis/explore_rooms.py [--bin 1] [--fast]
Reads data/processed/H05-rooms-cut/panel.parquet; writes explore_bin{k}.json, pair_day_bin{k}.parquet, figures.

Round 1b (2026-10-04), switches (env vars; defaults reproduce round 1):
  H05_DATA=r1b   panel from activity_bins_fixed (scheme/build_panel.py with H05_DATA=r1b) -> data/processed/H05-rooms-cut/r1b/
  H05_MASK=trim  DQ8 rule "trim before surrogates": each day is cut to its all-present window (every agent active that
                 day is between its first and last active minute) BEFORE pair statistics and the cross-day surrogate
                 are computed; outputs in r1b/trim/. The surrogate then aligns days by minute of the trimmed window.
  Figures of r1b runs are written as figures/r1b[_trim]_*.pdf so the round-1 figures stay.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ep import (circular_shift_agents, ep_gauss_crossfit, ep_heldout, fit_kinetic_ising, g_matrix, pair_ep_blocks,
                tod_basis)
from pairs import twfe

import os  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA_VERSION = os.environ.get("H05_DATA", "r1")
MASK = os.environ.get("H05_MASK", "none")
assert DATA_VERSION in ("r1", "r1b") and MASK in ("none", "trim"), (DATA_VERSION, MASK)
assert not (DATA_VERSION == "r1" and MASK != "none"), "masks need the r1b panel (present column)"
PANEL_DIR = ROOT / "data/processed/H05-rooms-cut" / ("" if DATA_VERSION == "r1" else "r1b")
DATA = PANEL_DIR / ("" if MASK == "none" else MASK)
DATA.mkdir(parents=True, exist_ok=True)
SH = ROOT / "data/processed/shared"
FIG = Path(__file__).resolve().parents[1] / "figures"
FIG_PREFIX = "" if DATA_VERSION == "r1" else ("r1b_" if MASK == "none" else f"r1b_{MASK}_")
BIN = int(sys.argv[sys.argv.index("--bin") + 1]) if "--bin" in sys.argv else 1
FAST = "--fast" in sys.argv
NPERM = 300 if FAST else 2000
NBOOT = 200 if FAST else 1000
RNG = np.random.default_rng(20261003)
warnings.simplefilter("ignore", RuntimeWarning)
SPINS = ("active", "talk")


# ============================================================================ data
def guard_holdout(days):
    cal = pl.read_parquet(SH / "calendar.parquet")
    held = set(cal.filter(pl.col("holdout"))["pt_date"].to_list())
    h = json.loads((ROOT / "hypotheses/holdout.json").read_text())
    for d in days:
        assert d not in held, f"holdout day {d} in exploration"
        assert not any(w["start"] <= d < w["end"] for w in h["ne_windows"]), f"NE window day {d}"


def trim_window(g):
    """DQ8 all-present window of one day (contiguous): [max first-active minute, min last-active minute] over the
    agents active that day. Returns (lo, hi) inclusive, or None if empty."""
    sp = (g.filter(pl.col("present") > 0).group_by("agent").agg(pl.col("minute").min().alias("m0"), pl.col("minute").max().alias("m1")))
    if sp.height == 0:
        return None
    lo, hi = int(sp["m0"].max()), int(sp["m1"].min())
    return (lo, hi) if hi > lo else None


TRIM_INFO = {}


def load_days():
    p = pl.read_parquet(PANEL_DIR / "panel.parquet")
    days = sorted(p["pt_date"].unique().to_list())
    guard_holdout(days)
    goal = dict(p.group_by("pt_date").agg(pl.col("goal_no").first()).iter_rows())
    regime = dict(p.group_by("pt_date").agg(pl.col("regime").first()).iter_rows())
    mats = {}
    for (d,), g in p.group_by("pt_date", maintain_order=True):
        agents = np.sort(g["agent"].unique().to_numpy())
        L = int(g["minute"].max()) + 1
        ai = np.searchsorted(agents, g["agent"].to_numpy())
        mi = g["minute"].to_numpy().astype(int)
        m = {"agents": agents}
        for s in SPINS:
            A = -np.ones((L, len(agents)), dtype=np.int8)
            A[mi, ai] = np.where(g[s].to_numpy() > 0, 1, -1)
            m[s] = A
        R = -np.ones((L, len(agents)), dtype=np.int8)
        R[mi, ai] = g["room"].to_numpy()
        m["room"] = R
        if MASK == "trim":
            w = trim_window(g)
            TRIM_INFO[d] = {"window": w, "L": L}
            if w is None or w[1] - w[0] + 1 < 31:
                continue  # too short to give >= 30 transitions
            for s in SPINS:
                m[s] = m[s][w[0]: w[1] + 1]
            m["room"] = m["room"][w[0]: w[1] + 1]
        if BIN > 1:
            Lb = L // BIN
            for s in SPINS:
                m[s] = m[s][: Lb * BIN].reshape(Lb, BIN, -1).max(1)
            m["room"] = m["room"][: Lb * BIN: BIN]
        mats[d] = m
    days = [d for d in days if d in mats]
    return days, mats, goal, regime


def week_of(d):
    y, w, _ = dt.date.fromisoformat(d).isocalendar()
    return f"{y}-W{w:02d}"


# ============================================================================ pair-day table with surrogate
def corr_cols(X, Y):
    X = X - np.nanmean(X, 0)
    Y = Y - np.nanmean(Y, 0)
    sx, sy = X.std(0), Y.std(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        C = (X.T @ Y) / len(X) / np.outer(sx, sy)
    C[~np.isfinite(C)] = np.nan
    return C


def pair_days(days, mats, goal, regime, spin):
    weeks = {}
    for d in days:
        weeks.setdefault(week_of(d), []).append(d)
    out = []
    for wk, wdays in weeks.items():
        agents = np.array(sorted(set().union(*[set(mats[d]["agents"].tolist()) for d in wdays])))
        N = len(agents)
        pi, pj = np.triu_indices(N, 1)
        X, Rm, valid, act = {}, {}, {}, {}
        for d in wdays:
            m = mats[d]
            L = m[spin].shape[0]
            A = np.full((L, N), np.nan)
            R = -np.ones((L, N), dtype=int)
            cols = np.searchsorted(agents, m["agents"])
            A[:, cols] = m[spin]
            R[:, cols] = m["room"]
            flips = np.nansum(A[1:] != A[:-1], 0)
            v = np.isfinite(A).all(0) & (flips >= 4)
            A[:, ~v] = np.nan
            X[d], Rm[d], valid[d] = A, R, v
            act[d] = (np.nanmean(A, 0) + 1) / 2
        for d in wdays:
            S = X[d]
            sel = valid[d][pi] & valid[d][pj]
            if not sel.any():
                continue
            a, b = pi[sel], pj[sel]
            Sp, Sn = S[:-1], S[1:]
            C1 = corr_cols(Sn, Sp)
            C0 = corr_cols(S, S)
            G = Sn[:, a] * Sp[:, b] - Sp[:, a] * Sn[:, b]
            sig = pair_ep_blocks(G)
            ks, cs, ss = [], [], []
            for e in wdays:
                if e == d:
                    continue
                Se = X[e]
                L = min(len(S), len(Se))
                Ade = corr_cols(S[1:L], Se[: L - 1]); Aed = corr_cols(Se[1:L], S[: L - 1])
                Bde = corr_cols(S[:L], Se[:L])
                ks.append(((Ade + Aed.T + Aed + Ade.T) / 4)[a, b])
                cs.append(((Bde + Bde.T) / 2)[a, b])
                G1 = S[1:L][:, a] * Se[: L - 1][:, b] - S[: L - 1][:, a] * Se[1:L][:, b]
                G2 = Se[1:L][:, a] * S[: L - 1][:, b] - Se[: L - 1][:, a] * S[1:L][:, b]
                with np.errstate(invalid="ignore"):
                    ss.append(0.5 * (pair_ep_blocks(np.nan_to_num(G1)) + pair_ep_blocks(np.nan_to_num(G2)))
                              + np.where(np.isnan(G1).any(0) | np.isnan(G2).any(0), np.nan, 0))
            if True:
                k_sur = np.nanmean(np.array(ks), 0) if ks else np.full(len(a), np.nan)
                c_sur = np.nanmean(np.array(cs), 0) if cs else np.full(len(a), np.nan)
                s_sur = np.nanmean(np.array(ss), 0) if ss else np.full(len(a), np.nan)
            R = Rm[d][:-1]
            known = (R[:, a] >= 0) & (R[:, b] >= 0)
            same = (R[:, a] == R[:, b]) & known
            col = np.where(known.sum(0) > 0, same.sum(0) / np.maximum(known.sum(0), 1), np.nan)
            n = len(a)
            out.append(pl.DataFrame({
                "pt_date": [d] * n, "week": [wk] * n, "goal_no": [goal[d]] * n, "regime": [regime[d]] * n,
                "i": agents[a].astype(np.int8), "j": agents[b].astype(np.int8),
                "kappa": 0.5 * (C1[a, b] + C1[b, a]), "c0": C0[a, b], "sig": sig, "gbar": G.mean(0),
                "kappa_sur": k_sur, "c0_sur": c_sur, "sig_sur": s_sur,
                "act_i": act[d][a], "act_j": act[d][b], "coloc": col, "known": known.mean(0), "n": [len(Sp)] * n}))
    df = pl.concat(out).with_columns((pl.col("kappa") - pl.col("kappa_sur")).alias("kappa_x"),
                                     (pl.col("c0") - pl.col("c0_sur")).alias("c0_x"),
                                     (pl.col("sig") - pl.col("sig_sur")).alias("sig_x"),
                                     pl.lit(spin).alias("spin"))
    return df.fill_nan(None)


# ============================================================================ helpers
def agent_room_mode(mats, ds):
    """Agent -> modal room over the given days, and purity (share of bins in that room)."""
    cnt = {}
    for d in ds:
        m = mats[d]
        for k, a in enumerate(m["agents"]):
            r = m["room"][:, k]
            r = r[r >= 0]
            for room, c in zip(*np.unique(r, return_counts=True)):
                cnt.setdefault(int(a), {}).setdefault(int(room), 0)
                cnt[int(a)][int(room)] += int(c)
    out = {}
    for a, c in cnt.items():
        tot = sum(c.values())
        room = max(c, key=c.get)
        out[a] = (room, c[room] / tot)
    return out


def stack_window(mats, ds, spin, min_flips=20, agents=None):
    """Concatenate the window's days on a common agent set (present every day, enough flips)."""
    common = set(mats[ds[0]]["agents"].tolist())
    for d in ds[1:]:
        common &= set(mats[d]["agents"].tolist())
    if agents is not None:
        common &= set(np.asarray(agents).tolist())
    agents = np.array(sorted(common))
    Sp, Sn, dd, mm = [], [], [], []
    for k, d in enumerate(ds):
        m = mats[d]
        cols = np.searchsorted(m["agents"], agents)
        S = m[spin][:, cols].astype(np.float64)
        Sp.append(S[:-1]); Sn.append(S[1:]); dd.append(np.full(len(S) - 1, k)); mm.append(np.arange(len(S) - 1) * BIN)
    Sp, Sn, dd, mm = np.vstack(Sp), np.vstack(Sn), np.concatenate(dd), np.concatenate(mm)
    flips = (Sp != Sn).sum(0)
    keep = flips >= min_flips
    return agents[keep], Sp[:, keep], Sn[:, keep], dd, mm


def perm_diff(vals, ai, aj, labels, n_perm, rng):
    """Within-minus-cross difference of pair values; null by permuting agent labels (room sizes kept)."""
    def diff(lab):
        same = lab[ai] == lab[aj]
        if same.all() or (~same).all():
            return np.nan
        return np.nanmean(vals[same]) - np.nanmean(vals[~same])
    obs = diff(labels)
    null = np.array([diff(rng.permutation(labels)) for _ in range(n_perm)])
    null = null[np.isfinite(null)]
    p = (1 + np.sum(null >= obs)) / (1 + len(null))
    return float(obs), float(p), null


# ============================================================================ X2
X2_WINDOWS = [35, 36, 37, 38, 39, 41, 42, 44]


def x2(days, mats, goal, pdf, spin):
    res = {}
    pd_ = pdf.filter(pl.col("spin") == spin)
    for gno in X2_WINDOWS:
        ds = [d for d in days if goal[d] == gno]
        if not ds:
            continue
        modes = agent_room_mode(mats, ds)
        pure = {a for a, (r, p) in modes.items() if p >= 0.9}
        w = (pd_.filter(pl.col("pt_date").is_in(ds) & pl.col("i").is_in(list(pure)) & pl.col("j").is_in(list(pure)))
             .group_by("i", "j").agg(pl.col("kappa_x").mean(), pl.col("c0_x").mean(), pl.col("sig").mean(),
                                    pl.col("sig_x").mean(), pl.col("kappa").mean(), pl.len().alias("ndays")))
        if w.height == 0:
            continue
        agents = np.array(sorted(pure))
        labels = np.array([modes[a][0] for a in agents])
        ai = np.searchsorted(agents, w["i"].to_numpy()); aj = np.searchsorted(agents, w["j"].to_numpy())
        same = labels[ai] == labels[aj]
        rec = {"days": len(ds), "n_agents": len(agents), "n_within": int(same.sum()), "n_cross": int((~same).sum()),
               "rooms": {int(r): int((labels == r).sum()) for r in np.unique(labels)}}
        for col in ("kappa_x", "c0_x", "sig", "sig_x", "kappa"):
            v = w[col].to_numpy().astype(float)
            obs, p, null = perm_diff(v, ai, aj, labels, NPERM, RNG)
            rec[col] = {"within": float(np.nanmean(v[same])), "cross": float(np.nanmean(v[~same])), "diff": obs,
                        "p_perm": p, "null_sd": float(np.std(null)) if len(null) else None}
        # kinetic Ising on the window (agents present every day)
        ag, Sp, Sn, dd, mm = stack_window(mats, ds, spin, agents=agents)
        if len(ag) >= 4:
            J, _ = fit_kinetic_ising(Sp, Sn, tod_basis(mm), lam=1e-3)
            lab_k = np.array([modes[a][0] for a in ag])
            ii, jj = np.triu_indices(len(ag), 1)
            Js = 0.5 * (J[ii, jj] + J[jj, ii])
            Ja = np.abs(J[ii, jj] - J[jj, ii])
            for nm, v in (("J_sym", Js), ("J_asym_abs", Ja)):
                obs, p, null = perm_diff(v, ii, jj, lab_k, NPERM, RNG)
                s = lab_k[ii] == lab_k[jj]
                rec[nm] = {"within": float(np.nanmean(v[s])), "cross": float(np.nanmean(v[~s])), "diff": obs, "p_perm": p}
            # EP: whole window, and class-restricted Newton bounds
            G = g_matrix(Sp, Sn, ii, jj, dtype=np.float64)
            N = len(ag)
            rec["ep_newton_agent_hour"] = ep_gauss_crossfit(G, dd)["sigma"] * 60 / BIN / N
            s = lab_k[ii] == lab_k[jj]

            def cls_ep(lab):
                sm = lab[ii] == lab[jj]
                if sm.all() or (~sm).all():
                    return np.nan
                w_ = ep_gauss_crossfit(G[:, sm], dd)["sigma"] / sm.sum()
                c_ = ep_gauss_crossfit(G[:, ~sm], dd)["sigma"] / (~sm).sum()
                return (w_ - c_) * 60 / BIN
            obs = cls_ep(lab_k)
            null = np.array([cls_ep(RNG.permutation(lab_k)) for _ in range(min(NPERM, 300))])
            rec["ep_newton_pairhour"] = {
                "within": ep_gauss_crossfit(G[:, s], dd)["sigma"] / s.sum() * 60 / BIN,
                "cross": ep_gauss_crossfit(G[:, ~s], dd)["sigma"] / (~s).sum() * 60 / BIN,
                "diff": float(obs), "p_perm": float((1 + np.sum(null >= obs)) / (1 + len(null)))}
        res[str(gno)] = rec
        print("X2", spin, gno, {k: (v if not isinstance(v, dict) else {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()}) for k, v in rec.items() if k in ("n_within", "n_cross", "kappa_x", "sig", "J_sym")}, flush=True)
    # pooled regime III: weighted mean of diffs, permutation null = sum of per-window nulls (approximate via z)
    return res


def x2_pooled(res, keys):
    out = {}
    for col in ("kappa_x", "c0_x", "sig", "sig_x", "J_sym", "ep_newton_pairhour"):
        diffs, ws, ps = [], [], []
        for k in keys:
            if k in res and col in res[k] and np.isfinite(res[k][col]["diff"]):
                diffs.append(res[k][col]["diff"]); ws.append(res[k]["n_cross"]); ps.append(res[k][col]["p_perm"])
        if diffs:
            # Fisher's combination of one-sided permutation p-values
            from scipy.stats import chi2
            stat = -2 * np.sum(np.log(ps))
            out[col] = {"mean_diff": float(np.average(diffs, weights=ws)), "n_windows": len(diffs),
                        "n_positive": int(np.sum(np.array(diffs) > 0)), "fisher_p": float(chi2.sf(stat, 2 * len(ps)))}
    return out


# ============================================================================ X3 events
def gdays(days, goal, g):
    return [d for d in days if goal[d] == g]


def drange(days, a, b, excl=()):
    return [d for d in days if a <= d <= b and d not in excl]


def events(days, goal):
    return [
        {"id": "merge_0504", "kind": "add (merge into #universe-coordination)", "pre": gdays(days, goal, 39), "post": gdays(days, goal, 40)},
        {"id": "split_0511", "kind": "cut (split back to #best/#rest)", "pre": gdays(days, goal, 40), "post": gdays(days, goal, 41)},
        {"id": "aba_39_41", "kind": "A-B-A check (same partition before and after the merge week)", "pre": gdays(days, goal, 39), "post": gdays(days, goal, 41)},
        {"id": "transfer_0427", "kind": "3 agents #best->#rest", "pre": drange(days, "2026-04-20", "2026-04-24"), "post": gdays(days, goal, 39)},
        {"id": "transfer_0402", "kind": "Sonnet 4.6 #rest->#best", "pre": gdays(days, goal, 37), "post": drange(days, "2026-04-02", "2026-04-08")},
        {"id": "transfer_0525", "kind": "Gemini 3.1 Pro #best->#rest (#43 held out)", "pre": gdays(days, goal, 42), "post": gdays(days, goal, 44)},
        {"id": "focus_on", "kind": "cut (2 agents leave #general for #focus)", "pre": drange(days, "2026-07-27", "2026-08-04"), "post": drange(days, "2026-08-06", "2026-08-21")},
        {"id": "focus_off", "kind": "add (#focus agents return)", "pre": drange(days, "2026-08-06", "2026-08-21"), "post": drange(days, "2026-08-25", "2026-09-04", excl=("2026-08-27",))},
        {"id": "placebo_41_42", "kind": "placebo: no room change", "pre": gdays(days, goal, 41), "post": gdays(days, goal, 42)},
        {"id": "placebo_51_july", "kind": "placebo: no room change; pseudo-treated = pairs with agents 6, 29", "pre": drange(days, "2026-07-13", "2026-07-17"), "post": drange(days, "2026-07-20", "2026-07-24"), "pseudo": [6, 29]},
    ]


def classify(pre_c, post_c):
    hi, lo = 0.75, 0.25
    if pre_c >= hi and post_c >= hi:
        return "stay"
    if pre_c >= hi and post_c <= lo:
        return "cut"
    if pre_c <= lo and post_c >= hi:
        return "add"
    if pre_c <= lo and post_c <= lo:
        return "cross"
    return "other"


def event_did(ev, pdf, mats, spin, outcomes=("kappa_x", "c0_x", "sig", "sig_x")):
    pre, post = ev["pre"], ev["post"]
    t = pdf.filter((pl.col("spin") == spin) & pl.col("pt_date").is_in(pre + post))
    if t.height == 0 or not pre or not post:
        return None
    t = t.with_columns(pl.col("pt_date").is_in(post).alias("is_post"))
    # agent trajectories (modal room pre, post) for assignment permutation
    mpre, mpost = agent_room_mode(mats, pre), agent_room_mode(mats, post)
    agents = np.array(sorted(set(mpre) & set(mpost)))
    traj = np.array([[mpre[a][0], mpost[a][0]] for a in agents])
    t = t.filter(pl.col("i").is_in(agents.tolist()) & pl.col("j").is_in(agents.tolist()))
    pc = t.group_by("i", "j", "is_post").agg(pl.col("coloc").mean())
    cpre = {(i, j): c for i, j, p, c in pc.iter_rows() if not p}
    cpost = {(i, j): c for i, j, p, c in pc.iter_rows() if p}
    pairs = sorted(set(cpre) & set(cpost))
    if not pairs:
        return None
    pa = np.array(pairs)
    cls = np.array([classify(cpre[p], cpost[p]) for p in pairs])
    if "pseudo" in ev:
        ps = set(ev["pseudo"])
        cls = np.array(["pseudo" if (c == "stay" and (p[0] in ps or p[1] in ps)) else c for c, p in zip(cls, pairs)])
    ai = np.searchsorted(agents, pa[:, 0]); aj = np.searchsorted(agents, pa[:, 1])
    pre_idx = {d: k for k, d in enumerate(pre)}; post_idx = {d: k for k, d in enumerate(post)}
    pkey = {p: k for k, p in enumerate(pairs)}
    rec = {"kind": ev["kind"], "pre": [pre[0], pre[-1], len(pre)], "post": [post[0], post[-1], len(post)],
           "n_pairs": {c: int((cls == c).sum()) for c in np.unique(cls)}}
    arms = [c for c in ("add", "cut", "cross", "pseudo") if (cls == c).sum() > 0]

    def traj_cls(tr):
        same_pre = tr[ai, 0] == tr[aj, 0]
        same_post = tr[ai, 1] == tr[aj, 1]
        c = np.where(same_pre & same_post, "stay", np.where(same_pre & ~same_post, "cut",
                     np.where(~same_pre & same_post, "add", "cross")))
        return c

    for y in outcomes:
        Mpre = np.full((len(pairs), len(pre)), np.nan); Mpost = np.full((len(pairs), len(post)), np.nan)
        for i, j, d, ip, v in t.select("i", "j", "pt_date", "is_post", y).iter_rows():
            k = pkey.get((i, j))
            if k is None or v is None:
                continue
            if ip:
                Mpost[k, post_idx[d]] = v
            else:
                Mpre[k, pre_idx[d]] = v
        if True:
            diff = np.nanmean(Mpost, 1) - np.nanmean(Mpre, 1)
            lev_pre = {c: float(np.nanmean(np.nanmean(Mpre, 1)[cls == c])) for c in np.unique(cls)}
            lev_post = {c: float(np.nanmean(np.nanmean(Mpost, 1)[cls == c])) for c in np.unique(cls)}
        ry = {"level_pre": lev_pre, "level_post": lev_post}
        for arm in arms:
            m_arm, m_st = cls == arm, cls == "stay"
            if m_st.sum() == 0:
                continue
            eff = float(np.nanmean(diff[m_arm]) - np.nanmean(diff[m_st]))
            # day bootstrap
            bs = []
            for _ in range(NBOOT):
                a_ = RNG.integers(len(pre), size=len(pre)); b_ = RNG.integers(len(post), size=len(post))
                if True:
                    dd_ = np.nanmean(Mpost[:, b_], 1) - np.nanmean(Mpre[:, a_], 1)
                    bs.append(np.nanmean(dd_[m_arm]) - np.nanmean(dd_[m_st]))
            bs = np.array(bs)
            # assignment permutation (shuffle which agent had which room trajectory)
            null = []
            if arm != "pseudo":
                for _ in range(NPERM):
                    c2 = traj_cls(traj[RNG.permutation(len(agents))])
                    a2, s2 = c2 == arm, c2 == "stay"
                    if a2.sum() and s2.sum():
                        null.append(np.nanmean(diff[a2]) - np.nanmean(diff[s2]))
            else:
                ps = list(ev["pseudo"])
                for _ in range(NPERM):
                    fake = set(RNG.choice(agents, size=len(ps), replace=False).tolist())
                    a2 = np.array([(p[0] in fake or p[1] in fake) for p in pairs]) & (cls != "other")
                    s2 = ~a2 & (cls != "other")
                    null.append(np.nanmean(diff[a2]) - np.nanmean(diff[s2]))
            null = np.array(null)
            null = null[np.isfinite(null)]
            p2 = (float((1 + np.sum(np.abs(null - np.mean(null)) >= abs(eff - np.mean(null)))) / (1 + len(null)))
                  if len(null) and np.isfinite(eff) else None)
            ry[arm] = {"did": eff, "ci95_dayboot": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
                       "p_assign_perm_2sided": p2, "n_arm": int(m_arm.sum()), "n_stay": int(m_st.sum())}
        rec[y] = ry
    # class-restricted EP (Newton, cross-fitted) per pair-hour, pre vs post
    rec["ep"] = event_ep(ev, mats, spin, agents, traj, pairs, cls)
    return rec


def event_ep(ev, mats, spin, agents, traj, pairs, cls):
    out = {}
    stacks = {}
    for lab in ("pre", "post"):
        ag, Sp, Sn, dd, mm = stack_window(mats, ev[lab], spin, min_flips=10, agents=agents)
        stacks[lab] = (ag, Sp, Sn, dd)
    common = np.array(sorted(set(stacks["pre"][0]) & set(stacks["post"][0])))
    if len(common) < 4:
        return None
    pidx = {p: k for k, p in enumerate(pairs)}
    ii, jj = np.triu_indices(len(common), 1)
    pc = np.array([cls[pidx[(common[a], common[b])]] if (common[a], common[b]) in pidx else "other" for a, b in zip(ii, jj)])
    Gs = {}
    for lab in ("pre", "post"):
        ag, Sp, Sn, dd = stacks[lab]
        cols = np.searchsorted(ag, common)
        Gs[lab] = (g_matrix(Sp[:, cols], Sn[:, cols], ii, jj, dtype=np.float64), dd)
        out[f"agent_hour_{lab}"] = ep_gauss_crossfit(*Gs[lab])["sigma"] * 60 / BIN / len(common)
        if len(np.unique(dd)) >= 2:
            out[f"agent_hour_heldout_ml_{lab}"] = ep_heldout(Gs[lab][0], dd, k=min(5, len(np.unique(dd))), return_theta=False)["sigma"] * 60 / BIN / len(common)

    def per_pair(mask, lab):
        if mask.sum() == 0:
            return np.nan
        G, dd = Gs[lab]
        return ep_gauss_crossfit(G[:, mask], dd)["sigma"] / mask.sum() * 60 / BIN

    for arm in ("add", "cut", "cross", "pseudo"):
        m = pc == arm
        if m.sum() == 0 or (pc == "stay").sum() == 0:
            continue
        s = pc == "stay"
        e = (per_pair(m, "post") - per_pair(m, "pre")) - (per_pair(s, "post") - per_pair(s, "pre"))
        out[arm] = {"pre": per_pair(m, "pre"), "post": per_pair(m, "post"), "stay_pre": per_pair(s, "pre"),
                    "stay_post": per_pair(s, "post"), "did_per_pairhour": float(e), "n_arm": int(m.sum()), "n_stay": int(s.sum())}
    return out


# ============================================================================ onboarding isolations (within-day)
def onboarding(mats, spin):
    """Newcomer in an isolated room, then merged into #general, same day. DiD on raw kappa across the two intervals:
    newcomer x incumbent pairs vs incumbent x incumbent pairs."""
    cases = [("2026-07-09", [35, 36, 37], [10, 11, 12]), ("2026-07-10", [38], [13]), ("2026-07-24", [40], [14])]
    out = {}
    for d, newc, iso_rooms in cases:
        if d not in mats:
            continue
        m = mats[d]
        ag = m["agents"]
        S = m[spin].astype(float); R = m["room"]
        nk = [int(np.searchsorted(ag, a)) for a in newc if a in ag]
        iso = np.isin(R[:, nk], iso_rooms).any(1)
        if iso.sum() < 10:
            out[d] = {"note": "isolation interval < 10 bins"}
            continue
        t_iso = np.flatnonzero(iso)
        A = np.arange(t_iso[0], t_iso[-1] + 1)
        B = np.arange(t_iso[-1] + 1, len(S))
        inc = [k for k in range(len(ag)) if k not in nk]

        def kap(T):
            Sp, Sn = S[T[:-1]], S[T[1:]]
            C = corr_cols(Sn, Sp)
            return 0.5 * (C + C.T)
        KA, KB = kap(A), kap(B)
        nv = np.array([KB[i, j] - KA[i, j] for i in nk for j in inc])
        iv = np.array([KB[i, j] - KA[i, j] for x, i in enumerate(inc) for j in inc[x + 1:]])
        nv, iv = nv[np.isfinite(nv)], iv[np.isfinite(iv)]
        bs = []
        for _ in range(NBOOT):
            bs.append(RNG.choice(nv, len(nv)).mean() - RNG.choice(iv, len(iv)).mean())
        out[d] = {"newcomers": newc, "bins_isolated": int(len(A)), "bins_after": int(len(B)),
                  "did_kappa_after_minus_isolated": float(nv.mean() - iv.mean()) if len(nv) and len(iv) else None,
                  "ci95_pairboot": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None,
                  "n_newcomer_pairs": int(len(nv)), "n_incumbent_pairs": int(len(iv)),
                  "newcomer_kappa_isolated": float(np.nanmean([KA[i, j] for i in nk for j in inc])),
                  "newcomer_kappa_after": float(np.nanmean([KB[i, j] for i in nk for j in inc]))}
    return out


# ============================================================================ X4 pooled TWFE
def x4(pdf, spin):
    t = pdf.filter((pl.col("spin") == spin) & (pl.col("regime") == "III"))
    out = {}
    for era, cond in (("all_III", None), ("two_room_era_37_44", pl.col("goal_no") <= 44), ("era_51", pl.col("goal_no") == 51)):
        tt = t if cond is None else t.filter(cond)
        tt = tt.filter(pl.col("coloc").is_not_null() & (pl.col("known") > 0.5))
        pk = (tt["i"].cast(pl.Int32) * 100 + tt["j"].cast(pl.Int32)).to_numpy()
        dk = tt["pt_date"].to_numpy()
        x = tt["coloc"].to_numpy().astype(float)
        ctrl = np.column_stack([(tt["act_i"] + tt["act_j"]).to_numpy(), (tt["act_i"] * tt["act_j"]).to_numpy()]).astype(float)
        r = {}
        for y in ("kappa_x", "c0_x", "sig", "sig_x", "kappa"):
            v = tt[y].to_numpy().astype(float)
            r[y] = twfe(v, x, pk, dk)
            r[y + "|act_controls"] = twfe(v, x, pk, dk, controls=ctrl)
        out[era] = r
    return out


# ============================================================================ X5 EP per window
def x5(days, mats, goal, spin):
    out = {}
    windows = {f"#{g}": gdays(days, goal, g) for g in (35, 36, 37, 38, 39, 40, 41, 42, 44)}
    d51 = gdays(days, goal, 51)
    wk = {}
    for d in d51:
        wk.setdefault(week_of(d), []).append(d)
    for k, v in wk.items():
        windows[f"#51 {k}"] = v
    for name, ds in windows.items():
        if len(ds) < 2:
            continue
        ag, Sp, Sn, dd, mm = stack_window(mats, ds, spin)
        if len(ag) < 4:
            continue
        G = g_matrix(Sp, Sn, dtype=np.float64)
        N = len(ag)
        r_ml = ep_heldout(G, dd, k=min(5, len(ds)), return_theta=False)
        r_nt = ep_gauss_crossfit(G, dd, k=min(5, len(ds)))
        # null: independent circular shifts within days
        # null 1: cross-day surrogate (each agent's days permuted independently; keeps daily profiles aligned)
        nd = len(np.unique(dd))
        Lmin = min(int((dd == q).sum()) for q in np.unique(dd))
        X = np.stack([np.vstack([Sp[dd == q][:Lmin], Sn[dd == q][Lmin - 1:Lmin]]) for q in np.unique(dd)])  # (days, Lmin+1, N)
        xnull = []
        for rep in range(5):
            Y = np.empty_like(X)
            for a in range(N):
                perm = RNG.permutation(nd)
                while nd > 1 and np.any(perm == np.arange(nd)) and rep < 50:
                    perm = RNG.permutation(nd)
                Y[:, :, a] = X[perm, :, a]
            Gx = g_matrix(Y[:, :-1].reshape(-1, N), Y[:, 1:].reshape(-1, N), dtype=np.float64)
            xnull.append(ep_gauss_crossfit(Gx, np.repeat(np.arange(nd), Lmin), k=min(5, nd))["sigma"])
        Gt = g_matrix(X[:, :-1].reshape(-1, N), X[:, 1:].reshape(-1, N), dtype=np.float64)
        trunc = ep_gauss_crossfit(Gt, np.repeat(np.arange(nd), Lmin), k=min(5, nd))["sigma"]
        # null 2: independent circular shifts within days (misaligns daily profiles; reported for contrast)
        nulls = []
        for rep in range(3):
            Sps, Sns = [], []
            for q in np.unique(dd):
                idx = np.flatnonzero(dd == q)
                Sday = np.vstack([Sp[idx], Sn[idx[-1:]]])
                Ssh = circular_shift_agents(Sday, np.zeros(len(Sday), int), RNG)
                Sps.append(Ssh[:-1]); Sns.append(Ssh[1:])
            Gs = g_matrix(np.vstack(Sps), np.vstack(Sns), dtype=np.float64)
            nulls.append(ep_gauss_crossfit(Gs, dd, k=min(5, len(ds)))["sigma"])
        out[name] = {"days": len(ds), "N": int(N), "T": int(len(G)), "activity": float((Sp > 0).mean()),
                     "flip_rate": float((Sp != Sn).mean()),
                     "heldout_ml_per_agent_hour": r_ml["sigma"] * 60 / BIN / N, "heldout_ml_se": r_ml["se"] * 60 / BIN / N,
                     "newton_cf_per_agent_hour": r_nt["sigma"] * 60 / BIN / N, "newton_cf_se": r_nt["se"] * 60 / BIN / N,
                     "newton_cf_per_pair_hour": r_nt["sigma"] * 60 / BIN / (N * (N - 1) / 2),
                     "circshift_null_newton_per_agent_hour": float(np.mean(nulls) * 60 / BIN / N),
                     "newton_cf_truncated_per_agent_hour": float(trunc * 60 / BIN / N),
                     "crossday_null_newton_per_agent_hour_mean": float(np.mean(xnull) * 60 / BIN / N),
                     "crossday_null_newton_per_agent_hour_sd": float(np.std(xnull) * 60 / BIN / N),
                     "excess_over_crossday_per_agent_hour": float((trunc - np.mean(xnull)) * 60 / BIN / N)}
        print("X5", spin, name, {k: round(v, 4) if isinstance(v, float) else v for k, v in out[name].items()}, flush=True)
    return out


# ============================================================================ figures
def figures(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(exist_ok=True)
    sfx = "" if BIN == 1 else f"_bin{BIN}"
    # X2
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2))
    for ax, col, lab in zip(axes, ("kappa_x", "sig", "J_sym"), ("excess lagged corr κ", "pair EP (nats/bin)", "kinetic-Ising J_sym")):
        ks = [k for k in res["X2"]["active"] if col in res["X2"]["active"][k]]
        x = np.arange(len(ks))
        w = [res["X2"]["active"][k][col]["within"] for k in ks]
        c = [res["X2"]["active"][k][col]["cross"] for k in ks]
        ax.bar(x - 0.2, w, 0.4, label="within room", color="#2a7")
        ax.bar(x + 0.2, c, 0.4, label="cross room", color="#999")
        for xi, k in zip(x, ks):
            p = res["X2"]["active"][k][col]["p_perm"]
            ax.text(xi, max(w[list(ks).index(k)], c[list(ks).index(k)]), f"p={p:.2f}", fontsize=5, ha="center", va="bottom")
        ax.set_xticks(x); ax.set_xticklabels([f"#{k}" for k in ks], fontsize=7); ax.set_title(lab, fontsize=8)
        ax.axhline(0, color="k", lw=0.5)
    axes[0].legend(fontsize=6)
    fig.suptitle("X2: within vs cross-room coupling, active spins (non-holdout; #35-#36 regime II)", fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / f"{FIG_PREFIX}x2_within_cross{sfx}.pdf"); plt.close(fig)
    # X3 forest
    rows = []
    for eid, r in res["X3"]["active"].items():
        if r is None:
            continue
        for arm in ("add", "cut", "cross", "pseudo"):
            if arm in r.get("kappa_x", {}):
                q = r["kappa_x"][arm]
                rows.append((f"{eid}:{arm}", q["did"], q["ci95_dayboot"], q["p_assign_perm_2sided"]))
    fig, ax = plt.subplots(figsize=(6, 0.28 * len(rows) + 1))
    for k, (lab, e, ci, p) in enumerate(rows):
        ax.errorbar(e, k, xerr=[[e - ci[0]], [ci[1] - e]], fmt="o", color="#c33" if ":cut" in lab else "#2a7" if ":add" in lab else "#666", ms=4)
        ax.text(ci[1], k, f"  p={p:.2f}" if p is not None else "", fontsize=6, va="center")
    ax.axvline(0, color="k", lw=0.6)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=7)
    ax.set_xlabel("pair DiD of excess lagged correlation κ (arm − pairs co-located throughout)", fontsize=7)
    ax.set_title("X3: room events (active spins, day-bootstrap 95% CI, assignment-permutation p)", fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / f"{FIG_PREFIX}x3_events{sfx}.pdf"); plt.close(fig)


# ============================================================================ main
if __name__ == "__main__":
    t0 = time.time()
    days, mats, goal, regime = load_days()
    print("days", len(days), "bin", BIN, flush=True)
    pdf = pl.concat([pair_days(days, mats, goal, regime, s) for s in SPINS])
    pdf.write_parquet(DATA / f"pair_day_bin{BIN}.parquet", compression="zstd")
    print("pair-days", pdf.height, f"{time.time()-t0:.0f}s", flush=True)
    res = {"bin_minutes": BIN, "n_days": len(days), "goals": sorted(set(goal.values())), "X2": {}, "X2_pooled_III": {},
           "X3": {}, "X3_onboarding": {}, "X4": {}, "X5": {}}
    for s in SPINS:
        res["X2"][s] = x2(days, mats, goal, pdf, s)
        res["X2_pooled_III"][s] = x2_pooled(res["X2"][s], ["37", "38", "39", "41", "42", "44"])
        res["X3"][s] = {ev["id"]: event_did(ev, pdf, mats, s) for ev in events(days, goal)}
        res["X3_onboarding"][s] = onboarding(mats, s)
        res["X4"][s] = x4(pdf, s)
        print("X2/X3/X4 done", s, f"{time.time()-t0:.0f}s", flush=True)
    res["X5"]["active"] = x5(days, mats, goal, "active")
    res["runtime_s"] = time.time() - t0
    res["data_version"] = DATA_VERSION
    res["mask"] = MASK
    if MASK == "trim":
        kept = [d for d in days]
        res["trim"] = {"days_kept": len(kept), "days_dropped": [d for d, v in TRIM_INFO.items() if d not in mats],
                       "median_window_frac": float(np.median([(v["window"][1] - v["window"][0] + 1) / v["L"]
                                                              for v in TRIM_INFO.values() if v["window"]]))}
    (DATA / f"explore_bin{BIN}.json").write_text(json.dumps(res, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)))
    figures(res)
    prov_path = PANEL_DIR / "_provenance.json"
    prov = json.loads(prov_path.read_text())
    prov[f"explore_bin{BIN}" + ("" if MASK == "none" else f"_{MASK}")] = {
        "built_by": "hypotheses/H05-rooms-cut/analysis/explore_rooms.py", "inputs": [str((PANEL_DIR / "panel.parquet").relative_to(ROOT))],
                                 "params": {"bin": BIN, "nperm": NPERM, "nboot": NBOOT, "seed": 20261003,
                                            "data_version": DATA_VERSION, "mask": MASK},
                                 "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print("done", f"{time.time()-t0:.0f}s")
