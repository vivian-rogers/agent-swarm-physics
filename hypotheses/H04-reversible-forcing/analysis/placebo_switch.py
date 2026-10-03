"""Placebo switches: week-to-week variation of the Hawkes n, its fast part a1, and the mean-field K between ADJACENT
non-holdout weeks with the SAME documented hours. This is the noise floor the NE21 reversal (C1, MF-C) must beat.

Unit = ISO week with >= 3 active non-holdout days and a single documented-hours value. Regimes I and III.
"""
from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hawkes import *  # noqa: E402,F403


def weeks():
    cal = calendar().filter(~pl.col("holdout") & (pl.col("window_s") > 0) & pl.col("regime").cast(pl.Utf8).is_in(["I", "III"]))
    cal = cal.with_columns(pl.col("pt_date").str.to_date().dt.strftime("%G-W%V").alias("wk"))
    out = []
    for (wk,), g in cal.group_by(["wk"], maintain_order=True):
        hrs = g["documented_hours"].drop_nulls().unique().to_list()
        reg = g["regime"].cast(pl.Utf8).unique().to_list()
        if g.height >= 3 and len(hrs) == 1 and len(reg) == 1:
            out.append((wk, reg[0], int(hrs[0]), sorted(g["pt_date"].to_list())))
    return sorted(out)


def fit_week(w):
    wk, reg, hrs, days = w
    ser = build_series(days)
    res = {"week": wk, "regime": reg, "hours": hrs, "days": days, "n_events": ser.n_events}
    if ser.n_events >= 300:
        s = fit_suite(ser).summary()
        res.update({"n": s["n"], "a1": s["a1"], "a2": s["a2"]})
    D = load_days(days)
    mf = mean_field(D, np.ones((1, len(D))))
    res["K"] = mf["K"][0]
    return res


if __name__ == "__main__":
    W = weeks()
    with ProcessPoolExecutor(max_workers=3) as ex:
        R = list(ex.map(fit_week, W))
    R.sort(key=lambda r: r["week"])
    diffs = {"I": {"n": [], "a1": [], "K": []}, "III": {"n": [], "a1": [], "K": []}}
    for a, b in zip(R[:-1], R[1:]):
        # adjacent = consecutive ISO weeks (or separated only by held-out / inactive weeks within 14 days), same regime and hours
        gap = (dt.date.fromisoformat(b["days"][0]) - dt.date.fromisoformat(a["days"][-1])).days
        if a["regime"] == b["regime"] and a["hours"] == b["hours"] and gap <= 14:
            for k in ("n", "a1", "K"):
                if a.get(k) is not None and b.get(k) is not None:
                    diffs[a["regime"]][k].append(b[k] - a[k])
    summ = {}
    for reg, dd in diffs.items():
        summ[reg] = {k: {"n_pairs": len(v), "abs_median": float(np.median(np.abs(v))) if v else None,
                         "abs_p90": float(np.percentile(np.abs(v), 90)) if v else None,
                         "abs_p95": float(np.percentile(np.abs(v), 95)) if v else None, "diffs": v} for k, v in dd.items()}
    out = {"weeks": R, "adjacent_same_hours": summ}
    jdump(out, OUT / "explore_placebo_switch.json")
    write_provenance("explore_placebo_switch.json", "hypotheses/H04-reversible-forcing/analysis/placebo_switch.py",
                     ["calendar", "chat_core", "exposure", "roster", "activity_bins"],
                     {"unit": "ISO week, >=3 non-holdout days, one documented-hours value", "max_gap_days": 14})
    for reg, s in summ.items():
        print(reg, {k: (v["n_pairs"], v["abs_median"], v["abs_p90"]) for k, v in s.items()})
