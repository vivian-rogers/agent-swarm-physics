"""H74 detector: channel scores, fused alarm and evaluation against a catalog of dated changes.

Inputs are the scheme's tables (or synthetic tables with the same columns):
  days   (idx, pt_date, regime, weekday, gap_return)
  agd    agent x day features (channel M)          columns: agent, pt_date, M_FEATURES
  dfeat  day features (channels D and C)            columns: pt_date, D_FEATURES, r1_bge, r1_gte
  sdaily search answers per day (channel O)         columns: pt_date, n_search, O_FEATURES
  sigs   signature counts per day (channel S)       columns: pt_date, rtype, sig, n, n_agents, agents
Card rule: robust trailing z against the previous B = 10 baseline values (>= 5 required); scale = trimmed SD (max and
min dropped) / c_k (Gaussian consistency factor, c_10 ~ 0.70); per-feature absolute floors. Fused Z = max of the five
channel scores; alarm at Z >= TAU = 4. Hit = alarm on day -1, 0 or +1 (calendar active-day offsets).
"""
from __future__ import annotations

import numpy as np
import polars as pl

B = 10
BMIN = 5
TAU = 4.0
M_FEATURES = ["sh_cu_action", "sh_talk", "sh_pause", "sh_wait", "sh_consolidate", "sh_search", "sh_session_start",
              "sh_session_stop", "sh_room_move", "rec_per_call", "log_turnaround", "log_prompt", "log_out", "log_reason",
              "cache_share", "tok_null_share", "infra_err_share", "bash_share"]
D_FEATURES = ["start_tod_min", "window_min", "documented_hours", "n_bookends", "n_nudges", "n_human", "js_share",
              "start_iqr_min", "n_present"]
O_FEATURES = ["f_chars", "f_lines", "f_blank", "f_h1", "f_h2", "f_h3", "f_bold", "f_b_star3", "f_b_star", "f_b_dash",
              "f_b_dot", "f_b_num", "f_emdash", "f_endash", "f_nonascii", "f_mean_line", "f_open"]
FLOOR = {**{f: 0.01 for f in M_FEATURES if f.startswith("sh_") or f.endswith("_share")},
         **{f: 0.05 for f in ("log_turnaround", "log_prompt", "log_out", "log_reason")}, "rec_per_call": 0.05,
         "start_tod_min": 5.0, "window_min": 10.0, "documented_hours": 0.5, "n_bookends": 0.25, "n_nudges": 2.0,
         "n_human": 2.0, "js_share": 0.01, "start_iqr_min": 2.0, "n_present": 1.0,
         **{f: 1.0 for f in O_FEATURES}, "f_chars": 50.0, "f_lines": 2.0, "f_nonascii": 0.002, "f_mean_line": 5.0,
         "r1_bge": 0.005, "r1_gte": 0.005}
CHANNELS = ["S", "M", "O", "D", "C"]


def _consistency(k: int, reps: int = 20000, seed: int = 7) -> float:
    rng = np.random.default_rng(seed)
    x = np.sort(rng.normal(size=(reps, k)), axis=1)[:, 1:-1]
    return float(x.std(axis=1, ddof=1).mean())


C_K = {k: _consistency(k) for k in range(BMIN, B + 1)}


def trailing_z(x: np.ndarray, floor: float, rel: float = 0.0) -> np.ndarray:
    """Robust trailing z of a series (NaN = missing); baseline = previous B non-missing values."""
    z = np.full(x.size, np.nan)
    hist: list[float] = []
    for t in range(x.size):
        if not np.isnan(x[t]) and len(hist) >= BMIN:
            b = np.array(hist[-B:])
            med = np.median(b)
            sd = np.sort(b)[1:-1].std(ddof=1) / C_K[len(b)] if len(b) >= 4 else b.std()
            scale = max(sd, floor, rel * abs(med))
            z[t] = (x[t] - med) / scale
        if not np.isnan(x[t]):
            hist.append(float(x[t]))
    return z


# ------------------------------------------------------------------------------------------------ channels
def score_M(agd: pl.DataFrame, days: list[str], features=M_FEATURES) -> tuple[np.ndarray, dict]:
    """Synchronous within-agent shift: per feature, median across agents of the agent's own trailing z."""
    pos = {d: i for i, d in enumerate(days)}
    T = len(days)
    per = {f: [[] for _ in range(T)] for f in features}
    for (a,), g in agd.sort("pt_date").group_by("agent", maintain_order=True):
        idx = np.array([pos[d] for d in g["pt_date"].to_list()])
        for f in features:
            if f not in g.columns:
                continue
            x = g[f].cast(pl.Float64).fill_null(np.nan).to_numpy()
            z = trailing_z(x, FLOOR.get(f, 0.05))
            for t, v in zip(idx, z):
                if np.isfinite(v):
                    per[f][t].append(v)
    med = {f: np.array([np.median(v) if len(v) >= 3 else np.nan for v in per[f]]) for f in features}
    M = np.vstack([np.abs(med[f]) for f in features])
    with np.errstate(all="ignore"):
        zM = np.where(np.all(np.isnan(M), 0), np.nan, np.nanmax(M, 0))
        arg = np.where(np.all(np.isnan(M), 0), -1, np.nanargmax(np.where(np.isnan(M), -np.inf, M), 0))
    return zM, {"feature": [features[k] if k >= 0 else None for k in arg], "median_z": med}


def score_series(df: pl.DataFrame, days: list[str], features, two_sided=True, min_count_col=None, min_count=0):
    pos = {d: i for i, d in enumerate(days)}
    T = len(days)
    zs = {}
    d = df.filter(pl.col("pt_date").is_in(days))
    if min_count_col:
        d = d.filter(pl.col(min_count_col) >= min_count)
    idx = np.array([pos[x] for x in d["pt_date"].to_list()], int)
    for f in features:
        if f not in d.columns:
            continue
        x = np.full(T, np.nan)
        x[idx] = d[f].cast(pl.Float64).fill_null(np.nan).to_numpy()
        z = trailing_z(x, FLOOR.get(f, 0.05))
        zs[f] = np.abs(z) if two_sided else z
    Z = np.vstack(list(zs.values()))
    with np.errstate(all="ignore"):
        best = np.where(np.all(np.isnan(Z), 0), np.nan, np.nanmax(Z, 0))
        arg = np.where(np.all(np.isnan(Z), 0), -1, np.nanargmax(np.where(np.isnan(Z), -np.inf, Z), 0))
    names = list(zs)
    return best, {"feature": [names[k] if k >= 0 else None for k in arg], "z": zs}


def score_C(dfeat: pl.DataFrame, days: list[str]):
    _, info = score_series(dfeat, days, ["r1_bge", "r1_gte"], two_sided=False)
    zz = np.vstack([info["z"][k] for k in ("r1_bge", "r1_gte") if k in info["z"]])
    with np.errstate(all="ignore"):
        return np.nanmean(zz, 0), info


def score_S(sigs: pl.DataFrame, days: list[str], newcomer: dict[tuple[int, str], bool] | None = None):
    """Platform-wide signature changes per day: new (never seen on an earlier day; >= 5 records; >= 2 agents not all
    newcomers, or agentless) and retired (>= 2% of its family and >= 2 agents in the previous B days, expected >= 10
    today, zero today, at least 2 of its baseline agents active today)."""
    T = len(days)
    pos = {d: i for i, d in enumerate(days)}
    s = sigs.filter(pl.col("pt_date").is_in(days)).with_columns(
        pl.col("rtype").str.split(":").list.first().alias("fam"),
        pl.col("pt_date").replace_strict(pos, return_dtype=pl.Int32).alias("t"))
    fam_tot = s.group_by("t", "fam").agg(pl.col("n").sum().alias("tot"))
    tot = {(t, f): n for t, f, n in fam_tot.iter_rows()}
    by_sig = {}
    for (sig,), g in s.group_by("sig"):
        by_sig[sig] = {t: (n, ag, fam) for t, n, ag, fam in zip(g["t"].to_list(), g["n"].to_list(), g["agents"].to_list(),
                                                                g["fam"].to_list())}
    active = {}
    for (t, ag) in s.select("t", "agents").explode("agents").drop_nulls().unique().iter_rows():
        active.setdefault(t, set()).add(ag)
    new = np.zeros(T, int)
    gone = np.zeros(T, int)
    detail = [[] for _ in range(T)]
    for sig, rec in by_sig.items():
        ts = sorted(rec)
        first = ts[0]
        n0, ag0, fam = rec[first]
        agents = [a for a in ag0 if a >= 0]
        nonnew = [a for a in agents if not (newcomer or {}).get((a, days[first]), False)]
        if first > 0 and n0 >= 5 and (len(agents) == 0 or (len(agents) >= 2 and len(nonnew) >= 2)):
            new[first] += 1
            detail[first].append(("new", sig))
        # retirement
        for t in range(1, T):
            if t in rec:
                continue
            base = [u for u in range(max(0, t - B), t)]
            nb = sum(rec[u][0] for u in base if u in rec)
            if nb == 0:
                continue
            ftot = sum(tot.get((u, fam), 0) for u in base)
            share = nb / max(ftot, 1)
            bag = set(a for u in base if u in rec for a in rec[u][1] if a >= 0)
            exp_today = share * tot.get((t, fam), 0)
            if share >= 0.02 and (len(bag) >= 2 or not bag) and exp_today >= 10 and \
                    (not bag or len(bag & active.get(t, set())) >= 2):
                # only the first day of a retirement counts
                if (t - 1) in rec:
                    gone[t] += 1
                    detail[t].append(("gone", sig))
    return 4.0 * (new + gone), {"new": new, "gone": gone, "detail": detail}


def fused(scores: dict[str, np.ndarray]) -> tuple[np.ndarray, list]:
    Z = np.vstack([scores[c] for c in CHANNELS])
    with np.errstate(all="ignore"):
        F = np.where(np.all(np.isnan(Z), 0), np.nan, np.nanmax(Z, 0))
        arg = [CHANNELS[k] if np.isfinite(F[t]) else None
               for t, k in enumerate(np.nanargmax(np.where(np.isnan(Z), -np.inf, Z), 0))]
    return F, arg


# ------------------------------------------------------------------------------------------------ evaluation
def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if not len(pos) or not len(neg):
        return np.nan
    r = (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()
    return float(r)


def window_array(score: np.ndarray, cal_days: list[str], day_pos: dict) -> np.ndarray:
    """wm[c] = max score over calendar active days c-1, c, c+1 that are scored (non-holdout); NaN if none."""
    v = np.array([score[day_pos[d]] if d in day_pos else np.nan for d in cal_days], float)
    pad = np.r_[np.nan, v, np.nan]
    W = np.vstack([pad[:-2], pad[1:-1], pad[2:]])
    with np.errstate(all="ignore"):
        return np.where(np.all(np.isnan(W), 0), np.nan, np.nanmax(W, 0))


def evaluate(scores: dict[str, np.ndarray], days: pl.DataFrame, events: pl.DataFrame, cal_days: list[str],
             classes: list[str], rng: np.random.Generator, n_rand: int = 2000, n_boot: int = 1000, tau: float = TAU,
             exclude_from_placebo: pl.DataFrame | None = None):
    """Per class and channel: hit rate, AUC vs placebo windows (bootstrap CI), random-date p; placebo FARs."""
    dl = days["pt_date"].to_list()
    day_pos = {d: i for i, d in enumerate(dl)}
    cal_pos = {d: i for i, d in enumerate(cal_days)}
    ev = events.filter(~pl.col("held0") & pl.col("day0").is_in(dl))
    excl = events if exclude_from_placebo is None else pl.concat([events.select("day0"), exclude_from_placebo.select("day0")])
    all_centers = np.array(sorted({cal_pos[d] for d in excl["day0"].drop_nulls().to_list() if d in cal_pos}))
    eligible = days.filter(pl.col("has_baseline"))["pt_date"].to_list()
    gapret = set(days.filter(pl.col("gap_return"))["pt_date"].to_list())
    placebo = [d for d in eligible if d not in gapret and (all_centers.size == 0 or np.min(np.abs(all_centers - cal_pos[d])) >= 3)]
    pc = np.array([cal_pos[d] for d in placebo], int)
    wd = dict(zip(dl, days["weekday"].to_list()))
    mon = np.array([wd[d] == 1 for d in placebo])
    regime_of = dict(zip(dl, days["regime"].to_list()))
    res = {"n_placebo": len(placebo), "classes": {}, "far": {}, "placebo_days": placebo}
    pools = {r: np.array([cal_pos[d] for d in eligible if regime_of[d] == r and d not in gapret], int) for r in set(regime_of.values())}
    for ch, sc in scores.items():
        wm = window_array(sc, cal_days, day_pos)
        pday = np.array([sc[day_pos[d]] for d in placebo])
        pw = wm[pc]
        res["far"][ch] = {"per_day": float(np.nanmean(pday >= tau)), "window": float(np.nanmean(pw >= tau)),
                          "monday_per_day": float(np.nanmean(pday[mon] >= tau)) if mon.any() else None,
                          "other_per_day": float(np.nanmean(pday[~mon] >= tau)) if (~mon).any() else None,
                          "n_monday": int(mon.sum())}
        for cls in classes:
            e = ev.filter(pl.col("cls") == cls)
            if e.height == 0:
                continue
            cent = np.array([cal_pos[d] for d in e["day0"].to_list()], int)
            ew = wm[cent]
            ok = np.isfinite(ew)
            if ok.sum() == 0:
                continue
            x = ew[ok]
            hit = float(np.mean(x >= tau))
            a = auc(x, pw)
            pwf = pw[np.isfinite(pw)]
            boots = [auc(x[rng.integers(0, x.size, x.size)], pwf[rng.integers(0, pwf.size, pwf.size)]) for _ in range(n_boot)]
            regs = [regime_of[d] for d, o in zip(e["day0"].to_list(), ok) if o]
            draws = np.column_stack([pools[r][rng.integers(0, len(pools[r]), n_rand)] for r in regs])
            W = wm[draws]
            with np.errstate(all="ignore"):
                rh = np.nanmean(W >= tau, 1); rm = np.nanmean(W, 1)
            res["classes"].setdefault(cls, {})[ch] = {
                "n": int(ok.sum()), "hit": hit, "auc": a,
                "auc_ci": [float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5))],
                "p_rand_hit": float((1 + np.sum(rh >= hit)) / (1 + n_rand)),
                "p_rand_mean": float((1 + np.sum(rm >= np.mean(x))) / (1 + n_rand)),
                "events": [{"event": i, "day0": d, "label": lab, "score": float(v) if np.isfinite(v) else None}
                           for i, d, lab, v in zip(e["event"].to_list(), e["day0"].to_list(), e["label"].to_list(), ew)]}
    return res
