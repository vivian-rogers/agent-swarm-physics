"""H84 synthetic power with one reached agent (correction 2026-10-04, after round 1; the round-1 synthetic is unchanged).

The round-1 synthetic (`synthetic.py`) planted a dose-proportional dip delta * d_a / d_bar_s in every dose-window
agent. The real outage fully reached only the top-dose searcher (first stage, P4). This variant plants the same
per-agent dip, delta * d_top / d_bar_s, in the top-dose agent only; every other agent gets no dip. The test is the
card's, unchanged: dose x outage beta from `h84lib.beta`, one-sided placebo-rank p <= 0.10 among the 38 placebo pairs.
G37 V1 (continuity) only. One extra cell plants a 0.20 dip in the reached agent itself (delta = -0.20 d_bar_s / d_top). Output: data/processed/H84-search-outage-memory-scramble/synthetic/synthetic_one_reached.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h84lib as L  # noqa: E402

REPS = 200


def synth_panel_one(panel, dose, top, treat, delta, s_e, rng, count_col, hit_col):
    p = panel.join(dose.select("agent", "dose"), on="agent", how="inner")
    agents = p["agent"].unique().to_list()
    days = p["pt_date"].unique().to_list()
    a = dict(zip(agents, rng.normal(np.log(0.84 / 0.16), 0.7, len(agents))))
    g = dict(zip(days, rng.normal(0, 0.5, len(days))))
    lo = np.array([a[x] for x in p["agent"].to_list()]) + np.array([g[x] for x in p["pt_date"].to_list()]) \
        + rng.normal(0, s_e, p.height)
    pr = 1 / (1 + np.exp(-lo))
    d = p["dose"].to_numpy()
    dbar = dose.filter(pl.col("dose") >= L.SEARCHER_MIN)["dose"].mean()
    hit = np.isin(p["pt_date"].to_numpy(), treat) & (p["agent"].to_numpy() == top)
    pr = np.clip(pr + np.where(hit, delta * d / dbar, 0.0), 0, 1)
    n = p[count_col].to_numpy()
    return p.drop("dose").with_columns(pl.Series(hit_col, rng.binomial(n, pr)).cast(pl.Int32))


def main():
    rng = np.random.default_rng(8401)
    panel = L.load_panel()
    dose = L.dose_table(panel, L.DOSE_DAYS)
    panel = panel.filter(pl.col("agent").is_in(dose["agent"].implode()))
    top = dose.sort("dose", descending=True)["agent"][0]
    d_top = float(dose["dose"].max())
    dbar = float(dose.filter(pl.col("dose") >= L.SEARCHER_MIN)["dose"].mean())
    pairs = L.placebo_pairs(panel, L.DOSE_DAYS + L.OUTAGE + L.RECOVERY)
    out = {}
    for s_e in (0.3, 0.6, 1.0):
        # -0.20 * d_bar_s / d_top: a 0.20 dip in the reached agent itself (not at the mean searcher dose)
        for delta in (0.0, round(-0.20 * dbar / d_top, 3), -0.20, -0.30, -0.50):
            hits = []
            for _ in range(REPS):
                sp = synth_panel_one(panel, dose, top, L.OUTAGE, delta, s_e, rng, "commits", "commits_pre")
                f = L.frame(sp, "V1_continuity", dose)
                b = L.beta(f, L.OUTAGE, [L.RECOVERY])
                pb = np.array([L.beta(f, pp, [L.OUTAGE, L.RECOVERY]) for pp in pairs])
                hits.append((1 + np.sum(pb <= b)) / (1 + len(pb)) <= 0.10)
            out[f"s_e={s_e}|delta={delta}"] = float(np.mean(hits))
            print(s_e, delta, out[f"s_e={s_e}|delta={delta}"], flush=True)
    res = {"reps": REPS, "reached_agent_dose": d_top, "d_bar_s": dbar, "n_pairs": len(pairs),
           "plant": "delta * d_top / d_bar_s in the top-dose agent only, outage days", "G37_V1_one_reached": out}
    o = L.DATA / "synthetic"
    o.mkdir(parents=True, exist_ok=True)
    (o / "synthetic_one_reached.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
