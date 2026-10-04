"""H84 POST HOC (written 2026-10-04 after the G37 run): single-agent check on the one agent the outage reached.

The first stage showed that only the top-dose agent (code 17) searched on outage days with collapsed answers (the
second searcher's answers halved; the third did not search). This is a single-agent ITS: fit y = agent + day fixed
effects on all non-outage, non-recovery days of the 12-agent panel, take agent 17's mean residual on the outage days,
and rank it against its mean residual on each of the 38 placebo pairs (two-sided rank p).
Output: data/processed/H84-search-outage-memory-scramble/results/posthoc_single_agent.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h84lib as L  # noqa: E402

AGENT = 17


def resid(f: pl.DataFrame) -> np.ndarray:
    y = f["y"].to_numpy()
    ag, dy = f["agent"].to_numpy(), f["pt_date"].to_numpy()
    fit = ~np.isin(dy, L.OUTAGE + L.RECOVERY)
    ua, ai = np.unique(ag, return_inverse=True)
    ud, di = np.unique(dy, return_inverse=True)
    Z = np.zeros((len(y), len(ua) + len(ud)))
    Z[np.arange(len(y)), ai] = 1
    Z[np.arange(len(y)), len(ua) + di] = 1
    b = np.linalg.lstsq(Z[fit], y[fit], rcond=None)[0]
    # outage/recovery day effects estimated from the other agents only
    for d in L.OUTAGE + L.RECOVERY:
        m = (dy == d) & (ag != AGENT)
        if m.any():
            b[len(ua) + np.flatnonzero(ud == d)[0]] = np.mean(y[m] - b[ai[m]])
    return y - Z @ b


def main():
    panel = L.load_panel()
    dose = L.dose_table(panel, L.DOSE_DAYS)
    pan = panel.filter(pl.col("agent").is_in(dose["agent"].implode()))
    pairs = L.placebo_pairs(pan, L.DOSE_DAYS + L.OUTAGE + L.RECOVERY)
    out = {}
    for k in ("V1_continuity", "V3_earlier_goal_refs", "V4_commits_per20", "S_search_per100", "S_rereads_per100"):
        f = L.frame(pan, k, dose)
        r = resid(f)
        a = f["agent"].to_numpy() == AGENT
        dy = f["pt_date"].to_numpy()
        real = float(np.mean(r[a & np.isin(dy, L.OUTAGE)])) if (a & np.isin(dy, L.OUTAGE)).any() else float("nan")
        rec = float(np.mean(r[a & np.isin(dy, L.RECOVERY)])) if (a & np.isin(dy, L.RECOVERY)).any() else float("nan")
        pb = np.array([np.mean(r[a & np.isin(dy, p)]) for p in pairs if (a & np.isin(dy, p)).any()])
        p2 = float((1 + np.sum(np.abs(pb - np.median(pb)) >= abs(real - np.median(pb)))) / (1 + len(pb)))
        out[k] = {"resid_outage": real, "resid_recovery": rec, "placebo_median": float(np.median(pb)),
                  "placebo_q10": float(np.percentile(pb, 10)), "placebo_q90": float(np.percentile(pb, 90)),
                  "n_placebo": len(pb), "p_two_sided": p2,
                  "n_outage_days_with_outcome": int((a & np.isin(dy, L.OUTAGE)).sum())}
        print(k, {kk: (round(v, 3) if isinstance(v, float) else v) for kk, v in out[k].items()})
    (L.DATA / "results/posthoc_single_agent.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
