"""H106: write rows to the shared per_period_estimates table (non-holdout only).
Usage: uv run python hypotheses/H106-slow-mode-finite-size/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h106lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC = "hypotheses/H106-slow-mode-finite-size"
CH = {"bge_small": "content_bge", "gte_modernbert": "content_gte"}


def nn(x):
    return None if x is None or x != x else float(x)


def main():
    rows = []
    per = pl.read_parquet(L.OUT / "replication/periods.parquet")
    for r in per.iter_rows(named=True):
        if r["rho"] != r["rho"]:
            continue
        se = nn(r["rho_se"])
        rows.append({"period_unit": f"G{r['goal_no']:02d}", "goal_no": r["goal_no"], "statistic": "slow_mode_near_similarity_m4",
                     "channel": CH[r["model"]], "estimate": r["rho"],
                     "ci_lo": r["rho"] - 1.96 * se if se else None, "ci_hi": r["rho"] + 1.96 * se if se else None,
                     "se": se, "ci_level": 0.95, "ci_kind": "se_z" if se else "none", "n": r["n_pairs"],
                     "n_kind": "cross-goal block pairs",
                     "method": "goal-pair-weighted mean disattenuated similarity of 4-agent-subset culture vectors "
                               "(two-way FE personal vectors; split-half R) with other goals' blocks within 10 active days",
                     "null": "none (descriptive point; card-level alpha_k decides)", "role": "replication",
                     "source": f"{SRC}/analysis/replication.py",
                     "notes": f"regime {r['regime']}; active population N_G {r['N_G']:.2f}; implied k "
                              f"{r['k_implied'] if r['k_implied'] == r['k_implied'] else 'n/a'}"})
        rows.append({"period_unit": f"G{r['goal_no']:02d}", "goal_no": r["goal_no"], "statistic": "active_population_N_blocks",
                     "channel": CH[r["model"]], "estimate": r["N_G"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                     "n": r["n_pairs"], "n_kind": "cross-goal block pairs",
                     "method": "mean over the period's blocks of the daily active population (>= 1 record, Claude Code excluded)",
                     "null": "none", "role": "replication", "source": f"{SRC}/scheme/build.py"})
    rep = json.loads((L.OUT / "replication/replication.json").read_text())
    for reg, key in (("I", "primary"), ("III", "regime_III")):
        for m, p in rep[key].items():
            jk = p.get("jk", {})
            rows.append({"period_unit": f"local:{reg}-span", "goal_no": None, "regime": reg, "holdout": False,
                         "statistic": "slow_mode_finite_size_exponent_alpha_k", "channel": CH[m], "estimate": p["alpha"],
                         "ci_lo": nn(jk.get("lo")), "ci_hi": nn(jk.get("hi")), "se": nn(jk.get("se")), "ci_level": 0.95,
                         "ci_kind": "jackknife_z" if jk else "none", "n": jk.get("n_goals"), "n_kind": "goals",
                         "method": "V1: NLS s~ = A exp(-k6 int (N/6)^alpha da) + s_inf over cross-goal block pairs; "
                                   "4-agent subsets, split-half disattenuated, active-day clock (delete-one-goal jackknife, t)",
                         "null": "drift world alpha 0 (synthetic D on the real panel); magnet alpha -1",
                         "role": "replication", "source": f"{SRC}/analysis/replication.py",
                         "notes": f"k6 {p['k6']:.4f}/active day; A {p['A']:.3f}; s_inf {p['s_inf']:.3f}; "
                                  f"{'primary' if reg == 'I' else 'descriptive'}; exception (c)/(d)"})
    nat = json.loads((L.OUT / "natives/natives.json").read_text())
    for m, v in nat["NE27"]["by_model"].items():
        jk = v["jk"] or {}
        rows.append({"period_unit": "local:NE27", "goal_no": None, "regime": "I", "holdout": False, "statistic": "NE27_dlnk_rate_step",
                     "channel": CH[m], "estimate": v["dlnk"], "ci_lo": nn(jk.get("lo")), "ci_hi": nn(jk.get("hi")),
                     "se": nn(jk.get("se")), "ci_level": 0.95, "ci_kind": "jackknife_z" if jk else "none",
                     "n": jk.get("n_goals"), "n_kind": "goals",
                     "method": "two-rate NLS (alpha 0), rate step at 2025-08-18; #2-#8 vs #10-#18 blocks",
                     "null": f"drift world D q05 {v['D_q05']:.2f}; magnet prediction {v['magnet_pred']:.2f}",
                     "role": "native",
                     "source": f"{SRC}/analysis/natives.py", "notes": f"non-holdout blocks of #2-#8 and #10-#18 (2025-05-10 to 10-31; #9 masked); percentile in D {v['D_pct']:.2f}"})
    for m, g in nat["G51"]["by_model"].items():
        for e in ("NE32", "NE33"):
            x = g[e]
            rows.append({"period_unit": f"local:G51-{e}", "goal_no": 51, "statistic": "G51_common_mode_dphi_join",
                         "channel": CH[m], "estimate": x["dphi"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                         "n": x["placebo_n"], "n_kind": "placebo boundaries",
                         "method": "phi = L(1)/L(0+) cross-agent lag alignment of #51 day residuals; post minus pre",
                         "null": f"placebo percentile {x['placebo_pct']:.2f}", "role": "native",
                         "source": f"{SRC}/analysis/natives.py",
                         "notes": f"N {x['N_pre']:.1f} -> {x['N_post']:.1f}; unpowered (planted power < 0.8)"})
    df = E.write_estimates(rows, hypothesis="H106")
    print("rows written:", len(rows), "table rows:", df.height)


if __name__ == "__main__":
    main()
