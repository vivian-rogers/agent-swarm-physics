"""H52 replication layer: the common estimator on one period.

Reads data/processed/H52-humans-loud-agents/<period>/rows.parquet and boundary.parquet; writes results.json there.
Primary estimators (Amendment A1, chosen on synthetic data before any real-data run): content = DiD statistic
`chi_dd` (CEM), reply = CEM, activity = bias-corrected CEM, stance = CEM (coarse strata). Robustness: H30's
orthogonalized `chi`, gte-modernbert, style-residualized recipient statements, excluding uncertain ledger rows,
including goal kickoffs, clean controls, regression adjustment. Boundary design: H29's rd_kappa (imported read-only).

Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/run_period.py G04 [G51 ...] [--B 1000]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402
import estimate as E  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(L.ROOT / "hypotheses/H29-driver-nodes/analysis"))
from h29lib import rd_kappa  # noqa: E402  (read-only import)

PRIMARY = {"con": "all", "rep": "all", "act": "all_bc", "st": "all"}


def boundary(period: str, B: int) -> dict:
    p = L.OUT / period / "boundary.parquet"
    if not p.exists():
        return {}
    R = pl.read_parquet(p)
    if R.height == 0:
        return {}
    out = {}
    for k, nm in ((0, "agent"), (1, "human"), (2, "bot")):
        for lab, flt in (("named", pl.col("named")), ("unnamed", ~pl.col("named"))):
            sub = R.filter(flt)
            nvis = sub.filter((pl.col("kind") == k) & pl.col("vis")).height
            ninv = sub.filter((pl.col("kind") == k) & ~pl.col("vis") & (pl.col("c") <= 30)).height
            if nvis >= 10 and ninv >= 10:
                r = rd_kappa(sub, kinds=(k,), B=B)
                out[f"{nm}_{lab}"] = dict(jump=r["jump"], ci=r["ci"], n_vis=nvis, n_inv=ninv)
            else:
                out[f"{nm}_{lab}"] = dict(jump=None, n_vis=nvis, n_inv=ninv)
    # joint-bootstrap difference human - agent (unnamed, all bins), H29's estimator replicated per draw
    out["human_minus_agent_unnamed"] = rd_diff(R.filter(~pl.col("named")), 1, 0, B)
    return out


def rd_diff(R: pl.DataFrame, k1: int, k0: int, B: int, bins=(0.0, 10.0, 20.0, 30.0), c_max=30.0) -> dict:
    """Difference of H29 visibility jumps between two sender kinds with a joint day-block bootstrap. The per-kind
    point estimates equal h29lib.rd_kappa's (same sums, same bin weights)."""
    R = R.filter(pl.col("yu_x").is_not_nan())
    days = sorted(set(R["day_idx"].to_list()))
    if len(days) < 3:
        return {}
    dpos = {d: i for i, d in enumerate(days)}
    nb = len(bins) - 1

    def sums(k):
        S = np.zeros((len(days), 2, nb, 5))
        Rk = R.filter(pl.col("kind") == k)
        for v, flt in ((0, pl.col("vis")), (1, ~pl.col("vis") & (pl.col("c") <= c_max))):
            sub = Rk.filter(flt & (pl.col("dt_talk") >= bins[0]) & (pl.col("dt_talk") < bins[-1]))
            if not sub.height:
                continue
            b = np.clip(np.searchsorted(np.array(bins), sub["dt_talk"].to_numpy(), side="right") - 1, 0, nb - 1)
            di = np.array([dpos[d] for d in sub["day_idx"].to_list()])
            for c, col in enumerate(("yu", "uu", "yu_x", "uu_x")):
                np.add.at(S[:, v, :, c], (di, b), sub[col].to_numpy())
            np.add.at(S[:, v, :, 4], (di, b), 1)
        return S

    def est(T):
        with np.errstate(invalid="ignore", divide="ignore"):
            pull = T[:, :, 0] / T[:, :, 1] - T[:, :, 2] / T[:, :, 3]
        n = T[:, :, 4]
        w = np.where((n[0] >= 5) & (n[1] >= 5), 2 * n[0] * n[1] / np.maximum(n[0] + n[1], 1), 0)
        ok = w > 0
        return float((w[ok] * (pull[0] - pull[1])[ok]).sum() / w[ok].sum()) if ok.any() else np.nan

    S1, S0 = sums(k1), sums(k0)
    d0 = est(S1.sum(0)) - est(S0.sum(0))
    rng = np.random.default_rng(L.SEED)
    bs = []
    for _ in range(B):
        w = np.bincount(rng.integers(len(days), size=len(days)), minlength=len(days)).astype(float)
        bs.append(est((S1 * w[:, None, None, None]).sum(0)) - est((S0 * w[:, None, None, None]).sum(0)))
    return dict(diff=d0, ci=L.ci(bs))


def headline(res: dict) -> dict:
    """Primary premium per outcome and class."""
    h = {}
    for oc, sub in PRIMARY.items():
        for c in ("human", "bot"):
            r = res.get(oc, {}).get(c, {}).get(sub)
            if r:
                h[f"{oc}_{c}"] = dict(att=r.get("att"), ci=r.get("ci"), se=r.get("se"), n_t=r.get("n_t"),
                                      n_t_msgs=r.get("n_t_msgs"), matched=r.get("matched_share"),
                                      ctrl_mean=r.get("ctrl_matched_mean"),
                                      naive=res[oc][c].get("all", {}).get("naive"),
                                      naive_ci=res[oc][c].get("all", {}).get("naive_ci"),
                                      cluster=res[oc][c].get("cluster"))
        an = res.get(oc, {}).get("agent_naming", {})
        h[f"{oc}_agent_naming"] = dict(att=an.get("att"), ci=an.get("ci"), se=an.get("se"))
    return h


def run(period: str, B: int = 1000, placebo_draws: int = 200, rows: pl.DataFrame | None = None,
        out: Path | None = None) -> dict:
    R = rows if rows is not None else pl.read_parquet(L.OUT / period / "rows.parquet")
    out = out or (L.OUT / period)
    res = {"period": period}
    d = E.prepare(R, con_col="chi_dd")
    res["primary"] = E.analyze(d, B=B, placebo_draws=placebo_draws)
    res["headline"] = headline(res["primary"])
    # robustness (content and reply only unless noted; smaller B)
    Br = max(200, B // 5)
    rob = {}
    for tag, kw in (("con_h30orth", dict(con_col="chi")), ("con_gte", dict(con_col="chi_dd_gte")),
                    ("con_sr", dict(con_col="chi_dd_sr")), ("con_jd", dict(con_col="chi_jd"))):
        if kw["con_col"] in R.columns:
            dd = E.prepare(R, **kw)
            rob[tag] = E.analyze(dd, B=Br, placebo_draws=0, regression=False, outcomes=("con",))["con"]
    for tag, kw in (("drop_uncertain", dict(drop_uncertain=True)), ("with_kickoffs", dict(include_kickoffs=True))):
        dd = E.prepare(R, con_col="chi_dd", **kw)
        rob[tag] = E.analyze(dd, B=Br, placebo_draws=0, regression=False)
    res["robustness"] = rob
    res["boundary"] = boundary(period, B=min(B, 500))
    # reply bias diagnostic: rows where a non-agent message would be the top candidate without the naming bonus
    for c, nm in ((1, "human"), (2, "bot")):
        sub = d.filter((pl.col("cls") == c) & (pl.col("n_chat_post") >= 1))
        if sub.height:
            res[f"reply_bias_{nm}"] = dict(rows=sub.height, rep_rate=float(sub["rep"].mean()),
                                           nf_risk_rate=float((sub["rep_nf_risk"] > 0).mean()))
    res["descr"] = descriptives(d)
    L.jdump(res, out / "results.json")
    return res


def descriptives(d: pl.DataFrame) -> dict:
    g = d.group_by("cls").agg(pl.len().alias("rows"), pl.col("msg").n_unique().alias("msgs"),
                              pl.col("day_idx").n_unique().alias("days"), pl.col("named").mean().alias("named_share"),
                              pl.col("age_s").median().alias("age_med"), pl.col("nov").mean().alias("nov_mean"),
                              pl.col("len").median().alias("len_med"), pl.col("idle").mean().alias("idle_share"),
                              pl.col("y_con").is_not_null().sum().alias("n_con"), pl.col("y_rep").is_not_null().sum().alias("n_rep"),
                              pl.col("y_act").is_not_null().sum().alias("n_act"), pl.col("y_st").is_not_null().sum().alias("n_st"))
    return {L.CLS_NAME[r["cls"]]: r for r in g.to_dicts()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("periods", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--B", type=int, default=1000)
    ap.add_argument("--placebo-draws", type=int, default=200)
    a = ap.parse_args()
    todo = (L.REPLICATION + L.EXTRA) if a.all else a.periods
    for p in todo:
        if not (L.OUT / p / "rows.parquet").exists():
            print(p, "no rows; skipped"); continue
        r = run(p, B=a.B, placebo_draws=a.placebo_draws)
        hh = r["headline"]
        print(p, {k: (round(v["att"], 4) if v.get("att") is not None and np.isfinite(v["att"]) else None)
                  for k, v in hh.items()}, flush=True)


if __name__ == "__main__":
    main()
