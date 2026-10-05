"""H05 round 2 (2026-10-05): shared loaders and estimators for R1 (artifact channel), R2 (attention reallocation)
and R3 (leak conductance). The same estimator functions run on synthetic worlds (r2_synthetic.py) and on real
non-reserved data (r2_run.py). Predictions: card, "Round 2" -> "Round-2 predictions, nulls and kill rules".

Reserved data: every loader drops held-out days (calendar.holdout, hypotheses/holdout.json goal periods and NE
windows, via infra/shared/common.py: holdout_mask) and `assert_no_reserved` guards the day lists.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
R1B = ROOT / "data/processed/H05-rooms-cut/r1b"
OUT = ROOT / "data/processed/H05-rooms-cut/r2"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

BIN_MIN = 5          # commit-spin bin (minutes)
RESP_BINS = 6        # response window: next 6 bins = 30 min
TWO_ROOM_GOALS = (35, 36, 37, 38, 39, 41, 42, 44)
FOCUS = (6, 29)
FOCUS_PRE = ("2026-07-27", "2026-08-04")
FOCUS_DUR = ("2026-08-06", "2026-08-21")
BETA_H18 = 0.45


# ---------------------------------------------------------------------------------------------- reserved data
def reserved_days() -> set:
    cal = pl.read_parquet(SH / "calendar.parquet")
    m = np.array(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].fill_null(-1).to_list()))
    return set(cal.filter(pl.col("holdout") | pl.Series(m))["pt_date"].to_list())


def assert_no_reserved(days) -> None:
    bad = set(days) & reserved_days()
    assert not bad, "reserved day in a round-2 input"


# ---------------------------------------------------------------------------------------------- rooms per day
def agent_days() -> pl.DataFrame:
    """H05 r1b day-level rooms (modal room per agent-day, non-reserved panel days 03-16 -> 09-04) + room size."""
    ad = pl.read_parquet(R1B / "agent_day.parquet").select("pt_date", "agent", "goal_no", "regime", "room_mode", "purity",
                                                            "talk_frac", "active_frac")
    assert_no_reserved(ad["pt_date"].unique().to_list())
    n = ad.group_by("pt_date", "room_mode").agg(pl.len().alias("n_room"))
    return ad.join(n, on=["pt_date", "room_mode"])


def room_dict(ad: pl.DataFrame) -> dict:
    out = {}
    for d, a, r in ad.select("pt_date", "agent", "room_mode").iter_rows():
        out.setdefault(d, {})[int(a)] = int(r)
    return out


def iso_week(d: str) -> str:
    y, w, _ = dt.date.fromisoformat(d).isocalendar()
    return f"{y}-W{w:02d}"


# ---------------------------------------------------------------------------------------------- correlation helpers
def corr_cols(X, Y):
    X = X - np.nanmean(X, 0)
    Y = Y - np.nanmean(Y, 0)
    sx, sy = X.std(0), Y.std(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        C = (X.T @ Y) / len(X) / np.outer(sx, sy)
    C[~np.isfinite(C)] = np.nan
    return C


def resp_matrix(C: np.ndarray, L: int = RESP_BINS) -> np.ndarray:
    """r(t) = 1 if any event in bins t+1 .. t+L (rows), for each column; the last L rows are dropped by callers."""
    T = C.shape[0]
    cs = np.vstack([np.zeros((1, C.shape[1])), np.cumsum(C, 0)])
    idx = np.arange(T)
    hi = np.minimum(idx + L + 1, T)
    lo = np.minimum(idx + 1, T)
    return ((cs[hi] - cs[lo]) > 0).astype(float)


# ---------------------------------------------------------------------------------------------- R1: commit spins
def load_commits() -> pl.DataFrame:
    wc = (pl.scan_parquet(SH / "work_commits.parquet")
          .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                  & ~pl.col("holdout") & pl.col("in_window"))
          .select("t", "pt_date", "goal_no", pl.col("author_agent").alias("agent"), pl.col("repo").cast(pl.Utf8))
          .collect())
    m = np.array(holdout_mask(wc["pt_date"].to_list(), wc["goal_no"].fill_null(-1).to_list()))
    return wc.filter(~pl.Series(m))


def commit_mats(wc: pl.DataFrame, ad: pl.DataFrame) -> dict:
    """day -> {agents, C (T x N commit indicator per 5-min bin of the day's window), n (commits per agent),
    repos (agent -> set)}. Agents = the day's panel agents."""
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start", "win_end")
    win = {d: (a, b) for d, a, b in cal.iter_rows()}
    days = sorted(ad["pt_date"].unique().to_list())
    per = {d: np.sort(g["agent"].to_numpy()) for (d,), g in ad.group_by("pt_date")}
    wcd = {d: g for (d,), g in wc.filter(pl.col("pt_date").is_in(days)).group_by("pt_date")}
    mats = {}
    for d in days:
        a0, a1 = win[d]
        T = max(int((a1 - a0).total_seconds() // (60 * BIN_MIN)) + 1, 1)
        agents = per[d]
        C = np.zeros((T, len(agents)))
        n = np.zeros(len(agents), dtype=int)
        repos = {int(a): set() for a in agents}
        g = wcd.get(d)
        if g is not None:
            g = g.filter(pl.col("agent").is_in(agents.tolist()))
            b = ((g["t"] - a0).dt.total_seconds() // (60 * BIN_MIN)).to_numpy().astype(int)
            ok = (b >= 0) & (b < T)
            ai = np.searchsorted(agents, g["agent"].to_numpy())
            C[b[ok], ai[ok]] = 1
            n = np.bincount(ai[ok], minlength=len(agents))
            for a, r in zip(g["agent"].to_list(), g["repo"].to_list()):
                repos[int(a)].add(r)
        mats[d] = {"agents": agents, "C": C, "n": n, "repos": repos}
    return mats


def commit_pair_days(mats: dict, rooms: dict, min_commits: int = 2) -> pl.DataFrame:
    """Pair-day commit-response coupling E (symmetrized, 30-min response window) minus the cross-day surrogate
    (same pair, other days of the ISO week, aligned by bin of the window). Also co-edit and cross/within flags for
    every pair-day with both agents present (E only where both have >= min_commits)."""
    weeks = {}
    for d in mats:
        weeks.setdefault(iso_week(d), []).append(d)
    rows = []
    for wk, wd in weeks.items():
        wd = sorted(wd)
        agents = np.array(sorted(set().union(*[set(mats[d]["agents"].tolist()) for d in wd])))
        N = len(agents)
        Cw, Rw, nw = {}, {}, {}
        for d in wd:
            m = mats[d]
            cols = np.searchsorted(agents, m["agents"])
            C = np.full((m["C"].shape[0], N), np.nan)
            C[:, cols] = m["C"]
            nn = np.zeros(N, dtype=int)
            nn[cols] = (m["C"] > 0).sum(0)     # occupied 5-min bins
            ok = nn >= min_commits
            C2 = C.copy()
            C2[:, ~ok] = np.nan
            Cw[d], nw[d] = C2, nn
            Rw[d] = resp_matrix(np.nan_to_num(C2)) + np.where(np.isnan(C2), np.nan, 0)
        for d in wd:
            m = mats[d]
            pa = m["agents"]
            T = Cw[d].shape[0]
            if T <= RESP_BINS + 2:
                continue
            Cd, Rd = Cw[d][: T - RESP_BINS], Rw[d][: T - RESP_BINS]
            M = corr_cols(Rd, Cd)              # M[i, j] = corr(r_i, e_j)
            E = 0.5 * (M + M.T)
            sur = []
            for e in wd:
                if e == d:
                    continue
                L = min(T, Cw[e].shape[0]) - RESP_BINS
                if L < 3:
                    continue
                Mde = corr_cols(Rw[d][:L], Cw[e][:L])
                Med = corr_cols(Rw[e][:L], Cw[d][:L])
                sur.append((Mde + Mde.T + Med + Med.T) / 4)
            S = np.nanmean(np.array(sur), 0) if sur else np.full((N, N), np.nan)
            ia = np.searchsorted(agents, pa)
            for x in range(len(pa)):
                for y in range(x + 1, len(pa)):
                    i, j = int(pa[x]), int(pa[y])
                    gi, gj = ia[x], ia[y]
                    ri, rj = rooms[d].get(i), rooms[d].get(j)
                    rows.append((d, wk, i, j, ri == rj, bool(m["repos"][i] & m["repos"][j]), int(nw[d][gi]), int(nw[d][gj]),
                                 float(E[gi, gj]), float(S[gi, gj])))
    df = pl.DataFrame(rows, orient="row", schema={"pt_date": pl.Utf8, "week": pl.Utf8, "i": pl.Int16, "j": pl.Int16,
                                                  "same_room": pl.Boolean, "coedit": pl.Boolean, "n_i": pl.Int32,
                                                  "n_j": pl.Int32, "E": pl.Float64, "E_sur": pl.Float64})
    return df.with_columns((pl.col("E") - pl.col("E_sur")).alias("E_x")).fill_nan(None)


def strata_contrast(df: pl.DataFrame, y: str, flag: str, strata: list, n_perm: int, rng) -> dict:
    """Stratified mean difference y[flag] - y[~flag] (weights = harmonic count per stratum); permutation of the flag
    within strata."""
    t = df.filter(pl.col(y).is_not_null())
    if t.height == 0:
        return {"n": 0}
    sk = t.select(pl.concat_str([pl.col(s).cast(pl.Utf8) for s in strata], separator="|")).to_series().to_numpy()
    v = t[y].to_numpy().astype(float)
    f = t[flag].to_numpy().astype(bool)
    _, sid = np.unique(sk, return_inverse=True)

    def stat(ff):
        num = den = 0.0
        for s in np.unique(sid):
            m = sid == s
            a, b = ff & m, ~ff & m
            if a.sum() == 0 or b.sum() == 0:
                continue
            w = 1 / (1 / a.sum() + 1 / b.sum())
            num += w * (v[a].mean() - v[b].mean())
            den += w
        return num / den if den else np.nan

    obs = stat(f)
    groups = [np.where(sid == s)[0] for s in np.unique(sid)]
    null = []
    for _ in range(n_perm):
        ff = f.copy()
        for g in groups:
            ff[g] = rng.permutation(f[g])
        null.append(stat(ff))
    null = np.array(null)
    null = null[np.isfinite(null)]
    p = float((np.sum(null >= obs) + 1) / (len(null) + 1)) if np.isfinite(obs) else None
    return {"n": int(len(v)), "n_flag": int(f.sum()), "diff": float(obs), "p_perm_one_sided": p,
            "null_sd": float(null.std()) if len(null) else None,
            "mean_flag": float(v[f].mean()) if f.any() else None, "mean_other": float(v[~f].mean()) if (~f).any() else None}


def tertile(x: np.ndarray) -> np.ndarray:
    q = np.nanquantile(x, [1 / 3, 2 / 3]) if len(x) else [0, 0]
    return np.digitize(x, q)


# ---------------------------------------------------------------------------------------------- R2: two-way FE
def _demean(y, groups, iters=500, tol=1e-11):
    y = y.astype(np.float64).copy()
    for _ in range(iters):
        before = y.copy()
        for g in groups:
            s = np.bincount(g, weights=y)
            c = np.bincount(g)
            y -= (s / np.maximum(c, 1))[g]
        if np.max(np.abs(y - before)) < tol:
            break
    return y


def poisson_fe(y, n, x, g1, g2, iters=200):
    """Poisson pseudo-ML: E[y] = n exp(a_g1 + d_g2 + b x). Profiles out both FE sets by alternating closed-form
    updates; Newton step in b. Returns b and a pair-cluster (g1) sandwich SE."""
    y = y.astype(float); n = n.astype(float); x = x.astype(float)
    a = np.zeros(g1.max() + 1); d = np.zeros(g2.max() + 1); b = 0.0
    for it in range(iters):
        for _ in range(3):
            mu0 = n * np.exp(d[g2] + b * x)
            a = np.log(np.maximum(np.bincount(g1, y, len(a)), 1e-12) / np.maximum(np.bincount(g1, mu0, len(a)), 1e-300))
            mu0 = n * np.exp(a[g1] + b * x)
            d = np.log(np.maximum(np.bincount(g2, y, len(d)), 1e-12) / np.maximum(np.bincount(g2, mu0, len(d)), 1e-300))
        mu = n * np.exp(a[g1] + d[g2] + b * x)
        # score and (concentrated) information for b, partialling FE by weighted demeaning
        xt = x - (np.bincount(g1, mu * x, len(a)) / np.maximum(np.bincount(g1, mu, len(a)), 1e-300))[g1]
        xt = xt - (np.bincount(g2, mu * xt, len(d)) / np.maximum(np.bincount(g2, mu, len(d)), 1e-300))[g2]
        sc = np.sum(xt * (y - mu))
        info = np.sum(mu * xt * xt)
        step = sc / info if info > 0 else 0.0
        b += step
        if abs(step) < 1e-9:
            break
    mu = n * np.exp(a[g1] + d[g2] + b * x)
    xt = x - (np.bincount(g1, mu * x, len(a)) / np.maximum(np.bincount(g1, mu, len(a)), 1e-300))[g1]
    xt = xt - (np.bincount(g2, mu * xt, len(d)) / np.maximum(np.bincount(g2, mu, len(d)), 1e-300))[g2]
    info = np.sum(mu * xt * xt)
    sc_c = np.bincount(g1, xt * (y - mu))
    se1 = float(np.sqrt(np.sum(sc_c ** 2)) / info) if info > 0 else np.nan
    sc_d = np.bincount(g2, xt * (y - mu))
    se2 = float(np.sqrt(np.sum(sc_d ** 2)) / info) if info > 0 else np.nan
    return {"b": float(b), "se_pair": se1, "se_day": se2, "se": float(np.sqrt(se1 ** 2 + se2 ** 2)), "n": int(len(y))}


def codes(x):
    _, inv = np.unique(np.asarray(x), return_inverse=True)
    return inv


def r2_kappa_twfe(pdf: pl.DataFrame, twfe) -> dict:
    """R2-P1: talk kappa_x on log k_room among co-located pair-days, pair + day FE, activity controls."""
    t = pdf.filter(pl.col("kroom").is_not_null() & (pl.col("kroom") >= 1) & pl.col("kappa_x").is_not_null())
    pk = (t["i"].cast(pl.Int32) * 100 + t["j"].cast(pl.Int32)).to_numpy()
    dk = t["pt_date"].to_numpy()
    v = t["kappa_x"].to_numpy().astype(float)
    x = np.log(t["kroom"].to_numpy().astype(float))
    ctrl = np.column_stack([(t["act_i"] + t["act_j"]).to_numpy(), (t["act_i"] * t["act_j"]).to_numpy()]).astype(float)
    r = twfe(v, x, pk, dk, controls=ctrl)
    kbar = float(np.nanmean(v))
    b, se = r.get("beta"), r.get("se_twoway")
    out = {"b": b, "se": se, "z": b / se if se else None, "kappa_bar": kbar, "n": r.get("n"), "n_pairs": r.get("n_pairs"),
           "n_days": r.get("n_days")}
    if b is not None and np.isfinite(b) and kbar > 0:
        out["beta_hat"] = -b / kbar
        out["beta_ci95"] = [(-b - 1.96 * se) / kbar, (-b + 1.96 * se) / kbar]
    # identifying variation: within-day spread of log k across pairs
    sd_within = (t.with_columns(pl.Series("lk", x)).group_by("pt_date").agg(pl.col("lk").std()).drop_nulls()["lk"].mean())
    out["mean_within_day_sd_logk"] = float(sd_within) if sd_within is not None else None
    return out


def load_json(p: Path):
    return json.loads(Path(p).read_text())


# ---------------------------------------------------------------------------------------------- R2: ledger uptake
def uptake_pairdays(ad: pl.DataFrame, goals=(37, 38, 39, 40, 41, 42, 44, 51), date_range=None) -> pl.DataFrame:
    """Directed pair-days (recipient i, sender j, day): n = i's talk calls with j pending (agent items), y = those
    where the talk responds to j (mention: resp; reply parent: resp_reply). Co-located pair-days only, k_room =
    N_room - 1 from the day-level rooms."""
    rows = []
    for g in goals:
        p = SH / "pending_sets" / f"G{g:02d}"
        tk = pl.read_parquet(p / "talks.parquet", columns=["talk_id", "agent", "pt_date"])
        pe = pl.read_parquet(p / "pending.parquet", columns=["talk_id", "sender", "kind", "resp", "resp_reply"]).filter(pl.col("kind") == 0)
        x = (pe.group_by("talk_id", "sender").agg(pl.col("resp").any(), pl.col("resp_reply").any())
             .join(tk, on="talk_id").group_by("agent", "sender", "pt_date")
             .agg(pl.len().alias("n"), pl.col("resp").sum().alias("y"), pl.col("resp_reply").sum().alias("y_reply")))
        rows.append(x.with_columns(pl.lit(g).alias("goal_no")))
    u = pl.concat(rows).rename({"agent": "i", "sender": "j"}).with_columns(pl.col("i").cast(pl.Int16), pl.col("j").cast(pl.Int16))
    if date_range is not None:
        u = u.filter((pl.col("pt_date") >= date_range[0]) & (pl.col("pt_date") <= date_range[1]))
    assert_no_reserved(u["pt_date"].unique().to_list())
    r = ad.select("pt_date", pl.col("agent").cast(pl.Int16), "room_mode", "n_room")
    u = (u.join(r.rename({"agent": "i", "room_mode": "room_i", "n_room": "n_room_i"}), on=["pt_date", "i"])
         .join(r.rename({"agent": "j", "room_mode": "room_j", "n_room": "n_room_j"}), on=["pt_date", "j"]))
    return u.filter(pl.col("room_i") == pl.col("room_j")).with_columns((pl.col("n_room_i") - 1).alias("kroom"))


def uptake_fit(u: pl.DataFrame, ycol: str = "y", rng=None, n_boot: int = 0) -> dict:
    t = u.filter((pl.col("n") > 0) & (pl.col("kroom") >= 1))
    g1 = codes((t["i"].cast(pl.Int32) * 100 + t["j"].cast(pl.Int32)).to_numpy())
    g2 = codes(t["pt_date"].to_numpy())
    r = poisson_fe(t[ycol].to_numpy(), t["n"].to_numpy(), np.log(t["kroom"].to_numpy().astype(float)), g1, g2)
    out = {"beta_u": -r["b"], "se": r["se"], "se_pair": r["se_pair"], "se_day": r["se_day"], "n": r["n"],
           "beta_ci95": [-r["b"] - 1.96 * r["se"], -r["b"] + 1.96 * r["se"]], "n_pairs": int(g1.max() + 1),
           "n_days": int(g2.max() + 1), "y_total": int(t[ycol].sum()), "n_total": int(t["n"].sum())}
    return out
