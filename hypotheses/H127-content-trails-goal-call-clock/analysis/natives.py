"""H127 natives (each with its own dated prediction in its folder README):
  N1 G51   own-role half-alignment time vs call rate across ~21 agents (decoys = other agents' roles): Theil-Sen s < 0,
           90% CI below 0, both models.
  N2 NE38  Opus 5's measured T_half^H (own new role) vs the call-clock prediction (regime-III replication median T_half^C /
           Opus 5's day-1 call rate) and the hour-clock prediction (regime-III median T_half^H).
Writes data/processed/H127-content-trails-goal-call-clock/natives/{G51,NE38}.json. Needs NE34/agents_all_configs.parquet.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h127lib as L  # noqa: E402

OUT = L.DATA / "natives"
NE38_AGENT = 40


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    adf = pl.read_parquet(L.DATA / "NE34/agents_all_configs.parquet")
    g51, ne = {}, {}
    for cfg in ("bge_white", "gte_white"):
        us = L.build_units("G51", cfg)
        r = L.analyze_kickoff(us, n_boot=1000, seed=51)
        pa = r.pop("_per_agent", [])
        g51[cfg] = {k: v for k, v in r.items() if not isinstance(v, list)} | dict(
            per_agent=[{k: v for k, v in x.items()} for x in pa],
            N1=bool(np.isfinite(r.get("s_hi", np.nan)) and r["s_hi"] < 0))
        us = L.build_units("NE38", cfg)
        u = [x for x in us if x["agent"] == NE38_AGENT][0]
        ht = L.unit_half_times(u) if len(u["a"]) else {}
        a3 = adf.filter((pl.col("cfg") == cfg) & (pl.col("regime") == "III"))
        TC_med, TH_med = float(a3["TC"].median()), float(a3["TH"].median())
        pred_C = TC_med / u["r"] * np.log(2) / np.log(2) if u["r"] else np.nan   # T_half^C [calls] / r [calls/h] = hours
        pred_H = TH_med
        meas = ht.get("TH", np.nan)
        ne[cfg] = dict(opus5_r=u["r"], opus5_Delta=u["Delta"], opus5_se_Delta=u["se_Delta"], opus5_rising=u["rising"],
                       opus5_n_day1=len(u["a"]), opus5_TH=meas, opus5_TC=ht.get("TC", np.nan), opus5_TH_floor=ht.get("TH_floor"),
                       regIII_median_TC=TC_med, regIII_median_TH=TH_med, regIII_median_r=float(a3["r"].median()),
                       pred_call_clock_h=pred_C, pred_hour_clock_h=pred_H,
                       logratio_call=float(abs(np.log(meas / pred_C))) if meas and pred_C else np.nan,
                       logratio_hour=float(abs(np.log(meas / pred_H))) if meas and pred_H else np.nan)
        ne[cfg]["N2"] = bool(ne[cfg]["logratio_call"] < ne[cfg]["logratio_hour"])
    (OUT / "G51.json").write_text(json.dumps(g51, indent=1, default=float))
    (OUT / "NE38.json").write_text(json.dumps(ne, indent=1, default=float))
    for cfg in g51:
        v = g51[cfg]
        print(f"G51 {cfg}: rise {v['n_rise']}/{v['n_elig']} s {v['s']:+.2f} [{v.get('s_lo', np.nan):+.2f},{v.get('s_hi', np.nan):+.2f}] CR {v['CR']:.2f} "
              f"medTH {v.get('med_T_H', np.nan):.3f} imm_ro {v.get('imm_ro', np.nan):.2f} N1 {v['N1']}")
        w = ne[cfg]
        print(f"NE38 {cfg}: r {w['opus5_r']:.1f}/h rising {w['opus5_rising']} TH {w['opus5_TH']:.3f}h  pred call {w['pred_call_clock_h']:.3f}h  "
              f"pred hour {w['pred_hour_clock_h']:.3f}h  |log| call {w['logratio_call']:.2f} hour {w['logratio_hour']:.2f} N2 {w['N2']}")


if __name__ == "__main__":
    main()
