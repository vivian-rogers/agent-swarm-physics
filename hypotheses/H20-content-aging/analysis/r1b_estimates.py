"""H20 round 1b: write per-period estimates (shared per_period_estimates table, infra/shared/estimates.py) from the
round-1b result files: both embedding models, the Amendment-2 (calibrated) null, shared goal fields; plus the native
tests. Non-holdout only (the writer refuses held-out rows).

Usage: uv run python hypotheses/H20-content-aging/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h20lib as L  # noqa: E402
from h20lib import hc  # noqa: E402
import estimates as E  # noqa: E402  (infra/shared is on sys.path via h20common)

METHOD = ("H20 r1b: agent-day statement means (n = 32, >= 8 statements), two-time C(t_w, t_w + tau), t_w >= 2; "
          "SE = SD under the fitted stationary swarm null with estimated latent shapes (Amendment 2); shared goal fields")


def unit_id(g):
    return E.map_unit(g)


def main():
    rows = []
    for model in ("bge_small", "gte_modernbert"):
        ch = f"content_{model}"
        for g in hc.ALL_PERIODS:
            f = hc.OUT / f"G{g:02d}/r1b/result_aniso_{model}.json"
            if not f.exists():
                continue
            r = json.loads(f.read_text())
            s = r["raw"]["stats"]
            base = dict(period_unit=unit_id(g), goal_no=g, channel=ch, n=r["n_agent_days_valid"], n_kind="agent-days",
                        role="replication", source=str(f.relative_to(hc.ROOT)), status="ok", unit_local=f"G{g:02d}",
                        notes=f"period role {hc.role(g)}; T = {r['T']} active days, N = {r['n_agents']} agents")
            for stat, key in (("aging_slope_A", "A"), ("aging_slope_A_c", "A_c"), ("aging_slope_A_late", "A_late"),
                              ("kickoff_transient_K", "K")):
                est, se = s[key]["obs"], s[key]["null_sd"]
                if est is None or se is None:
                    continue
                lo, hi = E.ci_from_se(est, se, 0.90)
                rows.append({**base, "statistic": stat, "estimate": est, "se": se, "ci_lo": lo, "ci_hi": hi, "ci_level": 0.90,
                             "ci_kind": "se_z", "method": METHOD,
                             "null": f"parametric stationary swarm (Amendment 2), one-sided p_upper = {s[key]['p_upper']:.3f}"})
            fi = r.get("fits", {})
            if fi.get("mu_hat") is not None:
                rows.append({**base, "statistic": "boxcox_aging_exponent_mu", "estimate": fi["mu_hat"],
                             "ci_lo": fi["mu_ci90"][0], "ci_hi": fi["mu_ci90"][1], "ci_level": 0.90, "ci_kind": "parametric",
                             "method": METHOD + "; M1 Box-Cox clock fit, parametric-bootstrap CI", "null": None})
            nm = r["raw"]["null_model"]
            rows.append({**base, "statistic": "plateau_q", "estimate": nm["q"], "ci_kind": "none",
                         "method": METHOD + "; stationary M0 fit (plateau of C)", "null": None})
    # natives
    for model in ("bge_small", "gte_modernbert"):
        f = L.R1B / f"natives_{model}.json"
        if not f.exists():
            continue
        nat = json.loads(f.read_text())
        ch = f"content_{model}"
        src = str(f.relative_to(hc.ROOT))
        if "G51_joiners" in nat:
            j = nat["G51_joiners"]
            rows.append(dict(period_unit="G51", goal_no=51, channel=ch, statistic="onboarding_transient_K_own_median",
                             estimate=j["K_own_median"], n=j["n_joiners"], n_kind="agents", ci_kind="none", role="native",
                             method="H20 r1b native: joiners' own-clock C_i(2,2+tau) - C_i(1,1+tau), tau = 1..3, median over joiners",
                             null=f"random-start placebo over incumbents, q90 = {j['placebo_K_q90']:.3f}", source=src, status="ok"))
        if "G27_block" in nat:
            b = nat["G27_block"]["raw"]
            rows.append(dict(period_unit=unit_id(27), goal_no=27, channel=ch, statistic="block_structure_B_max",
                             estimate=b["B_max"], ci_kind="none", role="native", source=src, status="ok",
                             method="H20 r1b native: max over split days of lag-matched non-straddling minus straddling C",
                             null=f"Amendment-2 stationary null, p_upper = {b['p_upper']:.3f}, q95 = {b['null_q95']:.3f}",
                             notes=f"s_hat = day {b['s_hat']}"))
        if "NE43" in nat:
            for step in ("bookends_end_0805", "nudges_end_0821"):
                x = nat["NE43"]["raw"][step]
                rows.append(dict(period_unit="G51", goal_no=51, channel=ch, statistic=f"step_break_R_{step}",
                                 estimate=x["R"], ci_kind="none", role="native", source=src, status="ok",
                                 method="H20 r1b native (NE43): lag-matched straddling minus non-straddling C at the step",
                                 null=f"Amendment-2 stationary null, p_lower = {x['p_lower']:.3f}; placebo q05 = {x['placebo_q05']:.3f}"))
    out = E.write_estimates(rows, hypothesis="H20")
    print(f"wrote {out.height} H20 rows")


if __name__ == "__main__":
    main()
