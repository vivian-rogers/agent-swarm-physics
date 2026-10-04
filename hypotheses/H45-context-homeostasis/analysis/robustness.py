"""H45 robustness of the regulation index (P1) to preprocessing choices, per eligible period.

Variants: baseline; action-row labs only (Anthropic, Google: dense prompt tokens); event-token labs' calibration x0.5
and x2; a generic ruler (0.25 tokens per character, no per-item or per-event overhead); band j 8-20 instead of 15-35;
low-confidence call starts dropped. Writes robustness.json.
"""
from __future__ import annotations

import json

import numpy as np
import polars as pl

import h45lib as L
from run_periods import ELIGIBLE


def ri(cu: pl.DataFrame, g: int, band=L.BAND, B: int = 100) -> dict:
    x = cu.filter(pl.col("goal_no") == g)
    r = L.elasticities(L.band_segments(x, band=band), group_cols=("agent", "unit_id"), B=B)
    return {k: r.get(k) for k in ("RI", "RI_ci", "eta_W", "eps", "eps_passive", "n_seg", "s_mean")}


def main():
    cal = L.load_calibration()
    c = L.load_calls()
    base = c.filter((pl.col("ctx_mode") == "cu") & pl.col("seg").is_not_null())
    variants = {
        "baseline": L.add_share(base, cal),
        "act_labs_only": L.add_share(base.filter(pl.col("lab").cast(pl.Utf8).is_in(list(L.LABS_ACT))), cal),
        "other_x0.5": L.add_share(base, cal, scale_other=0.5),
        "other_x2": L.add_share(base, cal, scale_other=2.0),
        "generic_ruler": L.add_share(base.with_columns((0.25 * pl.col("chars_new")).alias("r_gen")), r_col="r_gen"),
        "no_low_conf_starts": L.add_share(base, cal).filter(pl.col("start_conf").cast(pl.Utf8) != "low"),
    }
    out = {}
    for g in ELIGIBLE:
        row = {name: ri(v, g) for name, v in variants.items()}
        row["band_8_20"] = ri(variants["baseline"], g, band=(8, 20))
        out[f"G{g:02d}"] = row
        print(f"G{g:02d}", " ".join(f"{k}={v['RI']:.2f}" if v.get("RI") is not None else f"{k}=NA" for k, v in row.items()), flush=True)
    (L.DATA / "robustness.json").write_text(json.dumps(out, indent=1, default=float))
    # summary: range of RI across variants per period, and the count with RI CI upper < 0.5
    summ = {}
    for name in list(variants) + ["band_8_20"]:
        vals = [out[p][name] for p in out if out[p][name].get("RI") is not None]
        summ[name] = {"n_periods": len(vals), "RI_median": float(np.median([v["RI"] for v in vals])),
                      "n_upper_below_0.5": int(sum(v["RI_ci"][1] < 0.5 for v in vals)),
                      "n_RI_ge_0.5": int(sum(v["RI"] >= 0.5 for v in vals))}
    (L.DATA / "robustness_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
