"""H84 analysis helpers: outcomes, two-way fixed-effect dose DiD, placebo dates, dose permutation."""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H84-search-outage-memory-scramble"
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))

DOSE_DAYS = ["2026-03-24", "2026-03-25", "2026-03-26", "2026-03-27", "2026-03-30"]
OUTAGE = ["2026-03-31", "2026-04-01"]
RECOVERY = ["2026-04-02", "2026-04-03"]
SEARCHER_MIN = 0.25  # searches per 100 calls: "searchers" (Amendment A1)

OUTCOMES = {
    # name: (expression, eligibility)
    "V1_continuity": (pl.col("commits_pre") / pl.col("commits"), pl.col("commits") >= 1),
    "V2_duplicates": (pl.col("dup_repos").cast(pl.Float64), pl.lit(True)),
    "V3_earlier_goal_refs": (pl.col("ment_old") / pl.col("ment"), pl.col("ment") >= 5),
    "V4_commits_per20": (20 * pl.col("commits") / pl.col("calls"), pl.col("calls") >= 20),
    "S_search_per100": (100 * pl.col("search_calls") / pl.col("calls"), pl.col("calls") >= 20),
    "S_rereads_per100": (100 * pl.col("rereads") / pl.col("calls"), pl.col("calls") >= 20),
}


def load_panel(tag: str = "") -> pl.DataFrame:
    return pl.read_parquet(DATA / f"panel{tag}.parquet")


def dose_table(panel: pl.DataFrame, days: list[str], min_days: int = 3) -> pl.DataFrame:
    d = (panel.filter(pl.col("pt_date").is_in(days)).group_by("agent")
         .agg(pl.col("calls").sum(), pl.col("search_calls").sum(), pl.len().alias("n_days")))
    d = d.filter(pl.col("n_days") >= min_days)
    return d.with_columns((100 * pl.col("search_calls") / pl.col("calls")).alias("dose")).sort("agent")


def twfe(y: np.ndarray, agent: np.ndarray, day: np.ndarray, X: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    """OLS of y on X with agent and day dummies (optionally weighted). Returns the X coefficients."""
    ua, ai = np.unique(agent, return_inverse=True)
    ud, di = np.unique(day, return_inverse=True)
    A = np.zeros((len(y), len(ua)))
    A[np.arange(len(y)), ai] = 1
    D = np.zeros((len(y), max(len(ud) - 1, 0)))
    m = di > 0
    D[np.flatnonzero(m), di[m] - 1] = 1
    Z = np.column_stack([X, A, D])
    if w is not None:
        sw = np.sqrt(w)
        Z, y = Z * sw[:, None], y * sw
    b = np.linalg.lstsq(Z, y, rcond=None)[0]
    return b[: X.shape[1]]


def frame(panel: pl.DataFrame, outcome: str, dose: pl.DataFrame) -> pl.DataFrame:
    expr, elig = OUTCOMES[outcome]
    f = panel.join(dose.select("agent", "dose"), on="agent", how="inner").filter(elig)
    return f.with_columns(expr.alias("y")).filter(pl.col("y").is_finite())


def beta(f: pl.DataFrame, treat_days: list[str], ctrl_sets: list[list[str]], dose_col: str = "dose") -> float:
    """beta of dose x 1[day in treat_days], with dose x 1[day in each control set] as extra regressors."""
    d = f[dose_col].to_numpy()
    days = f["pt_date"].to_numpy()
    cols = [d * np.isin(days, treat_days)] + [d * np.isin(days, cs) for cs in ctrl_sets if cs]
    X = np.column_stack(cols)
    if not X[:, 0].any():
        return float("nan")
    return float(twfe(f["y"].to_numpy(), f["agent"].to_numpy(), days, X)[0])


def placebo_pairs(panel: pl.DataFrame, exclude: list[str], kickoff_matched: bool = False) -> list[list[str]]:
    """Consecutive active-day pairs (both outside `exclude`); kickoff-matched = days 2-3 of one goal period."""
    days = panel.select("pt_date", "goal_no", "day_in_goal").unique().sort("pt_date")
    rows = days.rows(named=True)
    out = []
    for a, b in zip(rows[:-1], rows[1:]):
        if a["pt_date"] in exclude or b["pt_date"] in exclude:
            continue
        if kickoff_matched and not (a["goal_no"] == b["goal_no"] and a["day_in_goal"] == 2 and b["day_in_goal"] == 3):
            continue
        out.append([a["pt_date"], b["pt_date"]])
    return out


def did_test(f: pl.DataFrame, treat: list[str], ctrl: list[list[str]], pairs: list[list[str]], pairs_k: list[list[str]],
             n_perm: int = 2000, seed: int = 0, sign: int = -1) -> dict:
    """Real beta; placebo betas (all pairs, kickoff-matched); one-sided rank p in direction `sign`; dose permutation."""
    b = beta(f, treat, ctrl)
    real_ctrl = [treat] + ctrl
    pb = np.array([beta(f, p, real_ctrl) for p in pairs])
    pk = np.array([beta(f, p, real_ctrl) for p in pairs_k])
    pb, pk = pb[np.isfinite(pb)], pk[np.isfinite(pk)]

    def rank_p(x, ref):
        if len(ref) == 0 or not np.isfinite(x):
            return float("nan")
        return float((1 + np.sum(sign * ref >= sign * x)) / (1 + len(ref)))
    rng = np.random.default_rng(seed)
    ag = f["agent"].to_numpy()
    ua, ai = np.unique(ag, return_inverse=True)
    dose_by = np.array([f.filter(pl.col("agent") == a)["dose"][0] for a in ua])
    perm = []
    for _ in range(n_perm):
        dp = rng.permutation(dose_by)[ai]
        perm.append(beta(f.with_columns(pl.Series("dose", dp)), treat, ctrl))
    perm = np.array(perm)
    perm = perm[np.isfinite(perm)]
    loo = {}
    for a in ua:
        g = f.filter(pl.col("agent") != a)
        loo[int(a)] = beta(g, treat, ctrl)
    return {"beta": b, "n": f.height, "n_agents": len(ua),
            "placebo": {"n": len(pb), "p_rank": rank_p(b, pb), "q10": _q(pb, 10), "q50": _q(pb, 50), "q90": _q(pb, 90),
                        "sd": float(np.std(pb)) if len(pb) else float("nan")},
            "placebo_kickoff": {"n": len(pk), "p_rank": rank_p(b, pk), "values": [float(x) for x in pk]},
            "perm_p": float((1 + np.sum(sign * perm >= sign * b)) / (1 + len(perm))) if len(perm) else float("nan"),
            "loo": loo, "loo_range": [float(np.nanmin(list(loo.values()))), float(np.nanmax(list(loo.values())))]}


def _q(a, q):
    return float(np.percentile(a, q)) if len(a) else float("nan")


def central80(x: float, placebo: dict) -> bool:
    return placebo["q10"] <= x <= placebo["q90"]
