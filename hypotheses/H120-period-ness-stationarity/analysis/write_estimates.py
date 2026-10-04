"""Write H120 round-1 rows to the shared per_period_estimates table (infra/shared/estimates.py)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h120lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

GOAL = {"4c": 4, "6b": 6, "8": 8, "13": 13, "19a": 19, "27": 27, "38a": 38, "51g": 51, "G38": 38, "51main": 51}
SRC = "data/processed/H120-period-ness-stationarity/results/results.json"


def main():
    R = json.loads((L.DATA / "results" / "results.json").read_text())["windows"]
    rows = []
    for w, rec in R.items():
        for ch in ("act", "talk"):
            r = rec[ch]
            unit = {"G38": "G38", "51main": "local:51main"}.get(w, w)
            role = "native" if w in ("G38", "51main") else "replication"
            f, l = (r["days"][0], r["days"][-1]) if w == "51main" else (None, None)
            base = dict(period_unit=unit, goal_no=GOAL[w], channel=f"{'activity' if ch == 'act' else 'talk'}_1min_trim",
                        role=role, n=r["n_days"], n_kind="days", first_day=f, last_day=l, source=SRC, post_hoc=False)
            hol = rec["holm"]
            for t, stat, meth in (("T1", "drift_ratio_split_R", "score statistic W for first vs second half (h, J) / mean over 1000 random day splits"),
                                  ("T2", "drift_ratio_trend_R", "score statistic W for a linear day trend (h, J) / mean over 1000 day-order permutations")):
                rows.append(base | dict(statistic=stat, estimate=r[t]["R"], ci_lo=None, ci_hi=None, ci_kind="none", method=meth,
                                        null=f"permutation p = {r[t]['p']:.3f}; Holm (6 tests) = {hol[ch + '_' + t]:.3f}",
                                        notes=f"N core {r['n_core']}; minutes {r['minutes']}; kinetic Ising with weekday and session-length fields, ridge 1 on J"))
            rows.append(base | dict(statistic="ep_sigma_total", estimate=r["EP_all"], ci_lo=r["EP_all_ci"][0], ci_hi=r["EP_all_ci"][1],
                                    ci_kind="percentile", ci_level=0.95,
                                    method="corrected held-out Newton EP bound (pair + single blocks), nats per minute; day bootstrap",
                                    null="compare only with the same estimator"))
            rows.append(base | dict(statistic="ep_drift_dSigma", estimate=r["T3"]["dSigma"], ci_lo=None, ci_hi=None, ci_kind="none",
                                    method="EP(second half) - EP(first half), same estimator",
                                    null=f"random day splits: p = {r['T3']['p']:.2f}, null sd {r['T3']['null_sd']:.2e}; unpowered (Amendment 1)"))
    E.write_estimates(rows, hypothesis="H120")
    print("rows", len(rows))


if __name__ == "__main__":
    main()
