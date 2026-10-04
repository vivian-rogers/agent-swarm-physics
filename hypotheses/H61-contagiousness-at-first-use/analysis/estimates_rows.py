"""Write H61 per-period rows to data/processed/shared/per_period_estimates.parquet (write_estimates).

  uv run python hypotheses/H61-contagiousness-at-first-use/analysis/estimates_rows.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

DATA = ROOT / "data/processed/H61-contagiousness-at-first-use"
SRC = "data/processed/H61-contagiousness-at-first-use/results/periods.json"


def unit_of(g: int) -> str:
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").filter(pl.col("goal_no") == g)
    return str(g) if pu.height == 1 else f"G{g:02d}"


def main():
    rows = json.loads((DATA / "results/periods.json").read_text())
    out = []
    for r in rows:
        if not r.get("eligible"):
            continue
        g = r["goal"]
        base = dict(period_unit=unit_of(g), goal_no=g, channel="content", role="replication", ci_level=0.95,
                    source=SRC, first_day=None, last_day=None, confirmatory=False)
        ntest = float(r["n_test"])
        out.append(dict(base, statistic="dLL_F_minus_B4", estimate=r["dll_F_B4"], ci_lo=r["dll_F_B4_lo"],
                        ci_hi=r["dll_F_B4_hi"], se=r["dll_F_B4_se"], n=ntest, n_kind="held-out test ideas",
                        method="H61.forward_chain_logit (millinats/idea; seed-message cluster bootstrap)",
                        null="B4 = class + poster + kickoff day + room size", ci_kind="percentile", post_hoc=False,
                        notes="amendment A1 baseline; underpowered if n < 2500 (synthetic power < 0.8)"))
        out.append(dict(base, statistic="dLL_F_minus_B3", estimate=r["dll_F_B3"], ci_lo=r["dll_F_B3_lo"],
                        ci_hi=r["dll_F_B3_hi"], se=r["dll_F_B3_se"], n=ntest, n_kind="held-out test ideas",
                        method="H61.forward_chain_logit (millinats/idea; seed-message cluster bootstrap)",
                        null="B3 = class + poster (pre-registered; synthetic size 0.39 under drift)",
                        ci_kind="percentile", post_hoc=False))
        out.append(dict(base, statistic="AUC_F_reach2_24h", estimate=r["auc_F"], ci_lo=None, ci_hi=None, n=ntest,
                        n_kind="held-out test ideas", method="H61.forward_chain_logit", null="AUC 0.5",
                        ci_kind="none", post_hoc=False, notes=f"B1 class-only AUC {r['auc_B1']:.3f}; B4 {r['auc_B4']:.3f}"))
        out.append(dict(base, statistic="top_decile_lift_reach2", estimate=r["lift_y"], ci_lo=None, ci_hi=None,
                        n=ntest, n_kind="held-out test ideas", method="H61.forward_chain_logit", null="lift 1",
                        ci_kind="none", post_hoc=False))
        cv = r.get("conv", {})
        if cv.get("eligible"):
            out.append(dict(base, statistic="G_read5_minus_G_unread5", estimate=cv["diff"], ci_lo=cv["diff_lo"],
                            ci_hi=cv["diff_hi"], se=cv["diff_se"], n=ntest, n_kind="held-out test ideas",
                            method="H61.in-flight placebo (AUC gain of F over B1, read-5 vs unread-5 adoption)",
                            null="synthetic same-fitness mean +0.011", ci_kind="percentile", post_hoc=False))
    nat = json.loads((DATA / "results/natives.json").read_text())
    for key, g, stat, val in (("G26", 26, "leader_OR_adjusted", nat["G26"]["adj"]), ("G35", 35, "lead_day_OR_adjusted", nat["G35"]["adj"])):
        out.append(dict(period_unit=unit_of(g), goal_no=g, channel="content", role="native", statistic=stat,
                        estimate=val["OR"], ci_lo=val["lo"], ci_hi=val["hi"], n=float(val["n"]), n_kind="seeded ideas",
                        method="H61.native logistic OR (seed-message cluster bootstrap)", null="OR 1", ci_kind="percentile",
                        ci_level=0.95, source="data/processed/H61-contagiousness-at-first-use/results/natives.json",
                        confirmatory=False, post_hoc=False))
    for wk, g in (("t39_40", 40), ("t40_41", 41)):
        t = nat["NE42"][wk]
        out.append(dict(period_unit=unit_of(g), goal_no=g, channel="content", role="native",
                        statistic="transfer_dLL_Fplus_minus_B3", estimate=t["dll"], ci_lo=t["lo"], ci_hi=t["hi"],
                        n=float(t["n"]), n_kind="test ideas (next NE42 week)",
                        method="H61.NE42 transfer (model fitted on the previous week)", null="B3 fitted on the previous week",
                        ci_kind="percentile", ci_level=0.95,
                        source="data/processed/H61-contagiousness-at-first-use/results/natives.json",
                        confirmatory=False, post_hoc=False, unit_local=f"NE42:{wk}"))
    df = E.write_estimates(out, hypothesis="H61")
    print(f"wrote {df.height} H61 rows")


if __name__ == "__main__":
    main()
