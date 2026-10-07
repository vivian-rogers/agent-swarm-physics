"""Write H142 per-period estimates rows (infra/shared/estimates.py) from results/periods.json and natives.json.

Roles: 'replication' for the per-period shape test (every analysed period; status ok when scored, else descriptive);
'native' for the #51 timer-wake batches (N1). NE42 differences are transition statistics and are not written.
Usage: uv run python hypotheses/H142-langevin-torque-saturation/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

RES = ROOT / "data/processed/H142-langevin-torque-saturation/results"
SRC = "data/processed/H142-langevin-torque-saturation/results/"
SHORT = {"bge_small": "bge", "gte_modernbert": "gte"}


def rows_for(unit: str, g: int, m: str, r: dict, role: str, src: str, design: str) -> list[dict]:
    ch = f"content step toward a period cluster direction ({SHORT[m]}, style_resid32, {design})"
    status = "ok" if r.get("scored", role == "native") else "descriptive"
    base = dict(period_unit=unit, goal_no=g, channel=ch, role=role, source=SRC + src, status=status, ci_level=0.95)
    out = []
    fd, fp = r["dummies"], r["profiles"]
    for nm, v in fd["f"].items():
        out.append(dict(base, statistic=f"h142_step_curve_{nm}", estimate=v["est"], ci_lo=v["lo"], ci_hi=v["hi"], n=v["n"],
                        n_kind="call-direction rows in the bin", ci_kind="percentile",
                        method="two-way FE (call; direction x room x hour) dummy coefficient, in-flight dummies, newest, named; agent-day cluster bootstrap 300",
                        null="0 (no read uptake)"))
    dc = fd["dcurv"]
    if dc.get("est") is not None:
        out.append(dict(base, statistic="h142_curvature_contrast", estimate=dc["est"], ci_lo=dc.get("lo"), ci_hi=dc.get("hi"),
                        n=fd["n_rows"], n_kind="call-direction rows", ci_kind="percentile" if dc.get("lo") is not None else "none",
                        method="ln[f(2)/f(1)] - ln[f(6+)/f(3)] from the dummies; agent-day cluster bootstrap (valid draws)",
                        null="0 (any power law or line)", notes=f"valid bootstrap share {dc.get('valid_share'):.2f}"))
    lg = fp["langevin"]
    for stat, est, lo, hi in (("h142_langevin_c", lg["theta"], lg.get("theta_lo"), lg.get("theta_hi")),
                              ("h142_nsat", lg["nsat"], lg.get("nsat_lo"), lg.get("nsat_hi"))):
        out.append(dict(base, statistic=stat, estimate=est, ci_lo=lo, ci_hi=hi, n=r["n_days"], n_kind="days",
                        ci_kind="percentile",
                        method="profile LS of f_inf,b L(c n) (amplitude per batch-size bin, A1) on a 61-point c grid; day bootstrap 300",
                        null=None, notes=f"grid-edge share {lg.get('edge_share', 0):.2f}"))
    for stat, key in (("h142_dll_langevin_linear", "dll_langevin_linear"), ("h142_dll_langevin_power", "dll_langevin_power")):
        d = r[key]
        out.append(dict(base, statistic=stat, estimate=d["dll"], ci_lo=d["lo"], ci_hi=d["hi"], n=d["n_days"], n_kind="day folds",
                        ci_kind="percentile",
                        method="leave-one-day-out Gaussian log-likelihood difference (nats, summed over rows); paired day-fold bootstrap 1000",
                        null="0 (shapes fit equally well out of fold)"))
    inf = fd.get("inflight")
    if inf and inf.get("ratio") is not None:
        out.append(dict(base, statistic="h142_inflight_ratio", estimate=inf["ratio"], ci_lo=inf["ratio_lo"], ci_hi=inf["ratio_hi"],
                        n=fd["n_rows"], n_kind="call-direction rows", ci_kind="percentile",
                        method="g(1)/f(1): in-flight vs read dummy at n = 1; agent-day cluster bootstrap 300",
                        null="1 (contemporaneous convergence)"))
    return out


def main():
    per = json.loads((RES / "periods.json").read_text())
    nat = json.loads((RES / "natives.json").read_text())
    rows = []
    for key, p in per.items():
        g = p["goal_no"]
        for m in ("bge_small", "gte_modernbert"):
            if m in p:
                rows += rows_for(p["period_unit"], g, m, p[m], "replication", "periods.json", "talk calls")
    for key, r in nat.items():
        if key.startswith("G51_wakes"):
            m = key.split("|")[1]
            rows += rows_for("G51", 51, m, r, "native", "natives.json", "timer-wake batches")
    E.write_estimates(rows, hypothesis="H142")
    print(f"wrote {len(rows)} rows")


if __name__ == "__main__":
    main()
