"""H35 O6: the undocumented nudger stop on 2026-08-20 inside #51 (non-holdout), as a quasi-intervention.

Before = G51 (07-06 .. 08-19, nudger on); after = G51off (08-21 .. 09-02, no automated messages); 08-20 dropped.
(a) Work accounting: nudge-attributable active minutes (nudges/day x first-nudge ATT) as a share of present
    agent-minutes predicts the drop in the active fraction; compared with the observed change, a placebo split inside
    the before period, and day-to-day noise.
(b) Gate DiD: gates in the nudger's trigger region (chain-age bins with nudge rate >= half the maximum, from the before
    period only) vs gates below it, escape probability after minus before; predicted from the before-period nudge rate
    in the region x the cross-fitted dp of nudged gates.
(c) Chain tail: P(chain reaches k >= 10 | it reaches the trigger region's lowest k), before vs after.

Usage: uv run python hypotheses/H35-nudger-maxwell-demon/analysis/offstep.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h35lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

PRE, POST = "G51", "G51off"
B = 2000


def day_table(grid: pl.DataFrame) -> pl.DataFrame:
    return grid.group_by("pt_date").agg(pl.len().alias("epochs"), pl.col("a_now").sum().alias("active"),
                                         pl.col("M").sum().alias("nudges")).sort("pt_date")


def boot_diff(a: np.ndarray, b: np.ndarray, wa: np.ndarray, wb: np.ndarray, rng) -> tuple:
    """Difference of weighted means (b - a) with independent day bootstraps."""
    pt = np.sum(b * wb) / np.sum(wb) - np.sum(a * wa) / np.sum(wa)
    bs = []
    for _ in range(B):
        ia = rng.integers(0, len(a), len(a)); ib = rng.integers(0, len(b), len(b))
        bs.append(np.sum(b[ib] * wb[ib]) / np.sum(wb[ib]) - np.sum(a[ia] * wa[ia]) / np.sum(wa[ia]))
    return float(pt), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def gate_did(gpre: pl.DataFrame, gpost: pl.DataFrame, hi_bins: list[int], rng) -> dict:
    def agg(g):
        g = g.filter(pl.col("outcome_r") != "censored").with_columns(pl.col("Kb").is_in(hi_bins).alias("hi"))
        return g.group_by("pt_date", "hi").agg(pl.len().alias("n"), pl.col("escape").sum().alias("e"))
    a, b = agg(gpre), agg(gpost)

    def did(a_, b_):
        def rate(t, h):
            s = t.filter(pl.col("hi") == h)
            return s["e"].sum() / max(1, s["n"].sum())
        return (rate(b_, True) - rate(a_, True)) - (rate(b_, False) - rate(a_, False)), \
            {"pre_hi": rate(a_, True), "pre_lo": rate(a_, False), "post_hi": rate(b_, True), "post_lo": rate(b_, False)}
    pt, rates = did(a, b)
    da, db = a["pt_date"].unique().to_list(), b["pt_date"].unique().to_list()
    bs = []
    for _ in range(B // 4):
        pa = rng.choice(da, len(da)); pb = rng.choice(db, len(db))
        aa = pl.concat([a.filter(pl.col("pt_date") == d) for d in pa])
        bb = pl.concat([b.filter(pl.col("pt_date") == d) for d in pb])
        bs.append(did(aa, bb)[0])
    return {"did": float(pt), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "rates": rates,
            "n_pre_hi": int(a.filter(pl.col("hi"))["n"].sum()), "n_post_hi": int(b.filter(pl.col("hi"))["n"].sum())}


def chain_tail(g: pl.DataFrame, k_lo: int) -> dict:
    ch = g.group_by("agent", "pt_date", "chain_r").agg(pl.col("k_r").max().alias("kmax"))
    reach = ch.filter(pl.col("kmax") >= k_lo)
    return {"chains": ch.height, "reach_trigger": reach.height,
            "p_reach10_given_trigger": float((reach["kmax"] >= 10).mean()) if reach.height else None}


def main():
    rng = np.random.default_rng(L.SEED)
    gpre = pl.read_parquet(L.OUT / PRE / "grid.parquet")
    gpost = pl.read_parquet(L.OUT / POST / "grid.parquet")
    tpre = pl.read_parquet(L.OUT / PRE / "gates.parquet")
    tpost = pl.read_parquet(L.OUT / POST / "gates.parquet")
    res_pre = L.json.loads((L.OUT / PRE / "results.json").read_text())
    out = {"pre_days": gpre["pt_date"].n_unique(), "post_days": gpost["pt_date"].n_unique(),
           "post_nudges_in_grid": int(gpost["M"].sum())}
    # (a) accounting
    dpre, dpost = day_table(gpre), day_table(gpost)
    att = res_pre["work"]["first_pastonly"]["y30"]
    n_per_day = dpre["nudges"].mean()
    epochs_per_day = dpre["epochs"].mean()
    pred = -n_per_day * np.array(att) / epochs_per_day
    fa, fb = (dpre["active"] / dpre["epochs"]).to_numpy(), (dpost["active"] / dpost["epochs"]).to_numpy()
    obs = boot_diff(fa, fb, dpre["epochs"].to_numpy().astype(float), dpost["epochs"].to_numpy().astype(float), rng)
    # placebo: last 9 days of the before period vs the rest
    k = len(fa) - out["post_days"]
    plc = boot_diff(fa[:k], fa[k:], dpre["epochs"].to_numpy()[:k].astype(float), dpre["epochs"].to_numpy()[k:].astype(float), rng)
    out["accounting"] = {"nudges_per_day_pre": float(n_per_day), "att_first_A30": att,
                         "predicted_change_active_fraction": [float(pred[0]), float(min(pred[1:])), float(max(pred[1:]))],
                         "nudge_share_of_active_minutes": float(n_per_day * att[0] / dpre["active"].mean()),
                         "active_fraction_pre": float(np.average(fa, weights=dpre["epochs"])),
                         "active_fraction_post": float(np.average(fb, weights=dpost["epochs"])),
                         "observed_change": obs, "placebo_split_change": plc,
                         "day_sd_active_fraction_pre": float(np.std(fa, ddof=1))}
    # (b) gate DiD on the trigger region
    rate = (tpre.filter(pl.col("Kb") >= 1).group_by("Kb").agg(pl.col("M").mean().alias("r"), pl.len()).sort("Kb"))
    rmax = rate["r"].max()
    hi_bins = rate.filter(pl.col("r") >= 0.5 * rmax)["Kb"].to_list()
    out["trigger_region"] = {"rate_by_Kb": [dict(zip(["Kb", "rate", "n"], r)) for r in rate.iter_rows()], "hi_bins": hi_bins}
    did = gate_did(tpre, tpost, hi_bins, rng)
    # predicted DiD: -(pre nudge rate in hi region - in lo region) x mean dp of nudged gates (cross-fitted)
    eff = res_pre["gate"]["eff_escapes"]
    r_hi = float(tpre.filter(pl.col("Kb").is_in(hi_bins))["M"].mean())
    r_lo = float(tpre.filter(~pl.col("Kb").is_in(hi_bins) & (pl.col("Kb") >= 1))["M"].mean())
    did["predicted"] = -(r_hi - r_lo) * eff["logged_mean_direct"]
    did["pre_nudge_rate_hi_lo"] = [r_hi, r_lo]
    # placebo DiD: last 9 days of the before period vs the rest
    days = sorted(tpre["pt_date"].unique().to_list())
    cut = days[-out["post_days"]]
    did["placebo"] = gate_did(tpre.filter(pl.col("pt_date") < cut), tpre.filter(pl.col("pt_date") >= cut), hi_bins, rng)
    out["gate_did"] = did
    # (c) chain tail
    k_lo = {1: 1, 2: 2, 3: 4, 4: 10}[min(hi_bins)] if hi_bins else 4
    out["chain_tail"] = {"k_lo": k_lo, "pre": chain_tail(tpre, k_lo), "post": chain_tail(tpost, k_lo)}
    L.jdump(out, L.OUT / POST / "offstep_results.json")
    print(L.json.dumps(out, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
