"""H84 synthetic validation at real counts (axis F), run before any real outcome statistic.

Keeps the real panel skeleton: agents, days, commits and strict-mention counts per agent-day, and the real doses (G37:
03-24 -> 03-30; NE18: 04-06 -> 04-17). Replaces the outcome with a synthetic draw:
    commits_pre ~ Binomial(commits, p_ad),  logit p_ad = a_a + g_t + e_ad
    a_a ~ N(logit 0.84, 0.7), g_t ~ N(0, 0.5), e_ad ~ N(0, s_e), s_e in {0.3, 0.6, 1.0}
and plants an absolute shift delta * d_a / d_bar_s on the treated days (d_bar_s = mean dose of searchers, d >= 0.25).
The test is the card's: one-sided placebo-rank p <= 0.10 among all consecutive-day placebo pairs (G37) or placebo
boundaries (NE18). Reports size (delta = 0) and power per delta. V3 uses the strict-mention counts the same way.
Output: data/processed/H84-search-outage-memory-scramble/synthetic/synthetic.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h84lib as L  # noqa: E402
from run import ne18_frames  # noqa: E402

REPS = 200


def synth_panel(panel: pl.DataFrame, dose: pl.DataFrame, treat: list[str], delta: float, s_e: float, rng,
                count_col: str, hit_col: str) -> pl.DataFrame:
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
    tr = np.isin(p["pt_date"].to_numpy(), treat)
    pr = np.clip(pr + np.where(tr, delta * d / dbar, 0.0), 0, 1)
    n = p[count_col].to_numpy()
    return p.drop("dose").with_columns(pl.Series(hit_col, rng.binomial(n, pr)).cast(pl.Int32))


def run_g37(panel, rng, outcome, count_col, hit_col):
    dose = L.dose_table(panel, L.DOSE_DAYS)
    panel = panel.filter(pl.col("agent").is_in(dose["agent"].implode()))
    excl = L.DOSE_DAYS + L.OUTAGE + L.RECOVERY
    pairs = L.placebo_pairs(panel, excl)
    out = {}
    for s_e in (0.3, 0.6, 1.0):
        for delta in (0.0, -0.10, -0.20, -0.30, -0.50):
            hits = []
            for _ in range(REPS):
                sp = synth_panel(panel, dose, L.OUTAGE, delta, s_e, rng, count_col, hit_col)
                f = L.frame(sp, outcome, dose)
                b = L.beta(f, L.OUTAGE, [L.RECOVERY])
                pb = np.array([L.beta(f, pp, [L.OUTAGE, L.RECOVERY]) for pp in pairs])
                hits.append((1 + np.sum(pb <= b)) / (1 + len(pb)) <= 0.10)
            out[f"s_e={s_e}|delta={delta}"] = float(np.mean(hits))
            print("G37", outcome, s_e, delta, out[f"s_e={s_e}|delta={delta}"], flush=True)
    return {"n_pairs": len(pairs), "power": out}


def run_ne18(panel, rng, outcome, count_col, hit_col):
    real, placebos, dose = ne18_frames(panel)
    out = {}
    for s_e in (0.3, 0.6, 1.0):
        for delta in (0.0, 0.10, 0.20, 0.30):
            hits = []
            for _ in range(REPS):
                sp = synth_panel(panel.filter(pl.col("agent").is_in(dose["agent"].implode())), dose,
                                 real["post"], delta, s_e, rng, count_col, hit_col)
                bs = []
                for spec in [real] + placebos:
                    f = L.frame(sp.filter(pl.col("pt_date").is_in(spec["days"])), outcome, dose)
                    bs.append(L.beta(f, spec["post"], []))
                b, pb = bs[0], np.array(bs[1:])
                hits.append((1 + np.sum(pb >= b)) / (1 + len(pb)) <= 0.10)
            out[f"s_e={s_e}|delta={delta}"] = float(np.mean(hits))
            print("NE18", outcome, s_e, delta, out[f"s_e={s_e}|delta={delta}"], flush=True)
    return {"n_placebos": len(placebos), "power": out}


def main():
    rng = np.random.default_rng(84)
    panel = L.load_panel()
    res = {"reps": REPS,
           "G37_V1": run_g37(panel, rng, "V1_continuity", "commits", "commits_pre"),
           "G37_V3": run_g37(panel, rng, "V3_earlier_goal_refs", "ment", "ment_old"),
           "NE18_V1": run_ne18(panel, rng, "V1_continuity", "commits", "commits_pre")}
    out = L.DATA / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    (out / "synthetic.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
