"""H52 estimation core: one function, `analyze`, applied identically to synthetic and real per-period frames.

For each outcome (content chi, reply, activity, stance) and each non-agent class present (human = 1, bot = 2):
CEM ATT vs agent rows (all, named, unnamed), the naive contrast, regression adjustment, and (content, reply) the
placebo-class null. Also the agents' own naming effect (named vs unnamed agent rows, strata without naming).
Cluster rule (card): day blocks when the treated class appears on >= 6 days, message clusters otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OUTCOMES = ("con", "rep", "act", "st")
MIN_DAYS_DAYBLOCK = 6


def prepare(df: pl.DataFrame, include_kickoffs: bool = False, drop_uncertain: bool = False,
            con_col: str = "chi") -> pl.DataFrame:
    """Adds outcome columns y_con, y_rep, y_act (day + recipient FE residualized), y_st and strata."""
    d = df
    if not include_kickoffs and "kickoff" in d.columns:
        d = d.filter(~pl.col("kickoff"))
    if drop_uncertain:
        d = d.filter(~pl.col("uncertain"))
    y30 = d["y30"].to_numpy().astype(float) if "y30" in d.columns else np.full(d.height, np.nan)
    if "y30_ok" in d.columns:
        y30 = np.where(d["y30_ok"].to_numpy(), y30, np.nan)
    yact = L.fe_residualize(y30, d["day_idx"].to_numpy(), d["recv"].to_numpy())
    rep = d["rep"].cast(pl.Float64).to_numpy()
    rep = np.where(d["n_chat_post"].to_numpy() >= 1, rep, np.nan)
    st = d["st"].cast(pl.Float64).to_numpy()
    st = np.where(d["rep"].to_numpy(), st, np.nan)
    d = d.with_columns(pl.Series("y_con", d[con_col].cast(pl.Float64).to_numpy()).fill_nan(None),
                       pl.Series("y_rep", rep).fill_nan(None), pl.Series("y_act", yact).fill_nan(None),
                       pl.Series("y_st", st).fill_nan(None))
    # clean controls: agent rows at receiving calls without any human or bot item (a co-arriving human message
    # shifts the shared post-call statement and activity, contaminating same-call agent rows)
    nonag_calls = d.filter(pl.col("cls") != 0)["turn_id"].unique()
    clean = ~d["turn_id"].is_in(nonag_calls.implode()).to_numpy()
    d = d.with_columns(pl.Series("clean", clean))
    fitm = d["cls"].to_numpy() == 0
    bc = {}
    for oc in ("con", "rep", "act", "st"):
        yv = d[f"y_{oc}"].cast(pl.Float64).fill_null(np.nan).to_numpy()
        bc[oc] = L.bc_residualize(d, yv, fitm, activity=(oc == "act"))
    d = d.with_columns(*[pl.Series(f"y_{oc}_bc", v).fill_nan(None) for oc, v in bc.items()])
    s_con = L.add_strata(d)["stratum"].to_numpy()
    s_act = L.add_strata(d, activity=True)["stratum"].to_numpy()
    s_con_nn = L.add_strata(d, with_named=False)["stratum"].to_numpy()
    s_st = L.add_strata_coarse(d)["stratum"].to_numpy()
    return d.with_columns(pl.Series("s_con", s_con), pl.Series("s_act", s_act), pl.Series("s_nn", s_con_nn),
                          pl.Series("s_st", s_st))


def cluster_ids(d: pl.DataFrame, cls: int) -> tuple[np.ndarray, str]:
    days_t = d.filter(pl.col("cls") == cls)["day_idx"].n_unique()
    if days_t >= MIN_DAYS_DAYBLOCK:
        return d["day_idx"].to_numpy().astype(np.int64), "day"
    return d["msg"].to_numpy().astype(np.int64), "message"


def analyze(d: pl.DataFrame, B: int = 1000, seed: int = L.SEED, classes=(1, 2), placebo_draws: int = 200,
            regression: bool = True, outcomes=OUTCOMES) -> dict:
    cls = d["cls"].to_numpy(); named = d["named"].to_numpy().astype(bool)
    msg = d["msg"].to_numpy()
    clean = d["clean"].to_numpy()
    res = {"n_rows": {L.CLS_NAME[c]: int((cls == c).sum()) for c in (0, 1, 2)}}
    for oc in outcomes:
        y = d[f"y_{oc}"].cast(pl.Float64).fill_null(np.nan).to_numpy()
        ybc = d[f"y_{oc}_bc"].cast(pl.Float64).fill_null(np.nan).to_numpy()
        strat = d["s_act"].to_numpy() if oc == "act" else (d["s_st"].to_numpy() if oc == "st" else d["s_con"].to_numpy())
        r = {}
        # agents' own naming effect (salience reference)
        cl_day = d["day_idx"].to_numpy().astype(np.int64)
        s_nn = _strip_named_act(d) if oc == "act" else d["s_nn"].to_numpy()
        r["agent_naming"] = L.att(y, (cls == 0) & named, (cls == 0) & ~named, s_nn, cl_day, B=B, seed=seed)
        for c in classes:
            if (cls == c).sum() < 5:
                continue
            clu, rule = cluster_ids(d, c)
            rc = {"cluster": rule}
            for lab, m in (("all", np.ones(len(y), bool)), ("named", named), ("unnamed", ~named)):
                rc[lab] = L.att(y, (cls == c) & m, (cls == 0) & m, strat, clu, B=B, seed=seed, msg=msg)
                rc[lab + "_bc"] = L.att(ybc, (cls == c) & m, (cls == 0) & m, strat, clu, B=B, seed=seed,
                                        msg=msg, naive=False)
            rc["all_clean"] = L.att(y, cls == c, (cls == 0) & clean, strat, clu, B=B, seed=seed, msg=msg, naive=False)
            if regression and oc != "st":
                try:
                    rc["regression"] = L.regression_premium(d.with_columns(pl.Series("_y", y).fill_nan(None)), "_y",
                                                            B=min(B, 300), seed=seed,
                                                            cluster="day_idx" if rule == "day" else "msg",
                                                            activity=(oc == "act"))
                except Exception as e:  # noqa: BLE001
                    rc["regression"] = {"error": str(e)[:200]}
            if placebo_draws and oc in ("con", "rep") and c == 1:
                tmp = d.with_columns(pl.Series("_y", y).fill_nan(None), pl.Series("stratum", strat))
                rc["placebo_class"] = L.placebo_class_null(tmp, "_y", c, draws=placebo_draws, seed=seed)
            r[L.CLS_NAME[c]] = rc
        res[oc] = r
    return res


def _strip_named_act(d: pl.DataFrame) -> np.ndarray:
    return L.add_strata(d, activity=True, with_named=False)["stratum"].to_numpy()
