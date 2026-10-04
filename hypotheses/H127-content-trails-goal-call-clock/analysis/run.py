"""H127 replication run: every eligible kickoff x 4 input configurations; card-level tests (after Amendment 1).

Writes data/processed/H127-content-trails-goal-call-clock/NE34/:
  kickoffs_all_configs.parquet  one row per (design, cfg): rise share, per-kickoff slope s (bootstrap CI), CR, dSSE (t0 and
                                read-out origin), read-out statistics, group stretch
  agents_all_configs.parquet    one row per rising agent fit (design, cfg): half times, rates, levels
  card.json                     card-level statistics per configuration
Usage: uv run python hypotheses/H127-content-trails-goal-call-clock/analysis/run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import mannwhitneyu

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h127lib as L  # noqa: E402

Z90 = 1.645
OUT = L.DATA / "NE34"
CFG = ["bge_white", "gte_white", "bge_style", "gte_style"]


def designs():
    k = L.tables()["k"]
    return [d for d in k.filter(pl.col("kind") == "kickoff").sort("goal_no")["design"].to_list()]


def card(kdf: pl.DataFrame, adf: pl.DataFrame) -> dict:
    out = {}
    for cfg in CFG:
        d = kdf.filter(pl.col("cfg") == cfg)
        a = adf.filter(pl.col("cfg") == cfg)
        pa = a.to_dicts()
        po = L.pooled_slope(pa, n_boot=1000, seed=1)
        po_lpo = L.pooled_slope(pa, rate="r_lpo", n_boot=1000, seed=2)
        # controls: on-task trait (leave-kickoff-out mean settled level) and lab dummies
        labs = sorted(set(x["lab"] for x in pa if x["lab"]))
        for x in pa:
            for lb in labs[1:]:
                x[f"lab_{lb}"] = 1.0 if x["lab"] == lb else 0.0
        ctrl = ["a_on"] + [f"lab_{lb}" for lb in labs[1:]]
        po_c = L.pooled_slope([x for x in pa if x.get("a_on") is not None], controls=ctrl, n_boot=1000, seed=3)
        reg = {"I": [x for x in pa if x["regime"] == "I"], "II-III": [x for x in pa if x["regime"] in ("II", "III")]}
        po_r = {kk: L.pooled_slope(v, n_boot=1000, seed=4) for kk, v in reg.items()}
        s = d["s"].to_numpy(); se = d["se_s"].to_numpy()
        m = L.dl_meta(s, se)
        CR = d["CR"].to_numpy(); crs = CR[np.isfinite(CR)]
        dro = d["dsse_ro"].to_numpy(); dt0 = d["dsse"].to_numpy()
        sro = d["s_ro"].to_numpy()
        sI = d.filter(pl.col("regime") == "I")["s"].drop_nans().to_numpy(); sIII = d.filter(pl.col("regime") != "I")["s"].drop_nans().to_numpy()
        stretch = L.stretch_card(d.select("dlr", "dlt_H", "dlt_C").to_dicts(), n_boot=1000)
        out[cfg] = dict(
            n_kick=int(d.height), n_rising=int(a.height), rise_share=float(d["n_rise"].sum() / max(d["n_elig"].sum(), 1)),
            median_Delta=float(a["Delta"].median()), median_T_H=float(a["TH"].median()), median_T_C=float(a["TC"].median()),
            median_ro_delay_h=float(a["ro_delay_h"].median()), share_floor_t0=float(a["TH_floor"].mean()),
            s_pool=po["s_pool"], s_pool_lo=po["s_pool_lo"], s_pool_hi=po["s_pool_hi"], n_pool=po["n_agents"],
            P1_pool=bool(po["s_pool_hi"] < 0 and po["s_pool_lo"] <= -0.5 and po["s_pool_hi"] >= -1.5),
            kill_pool=bool(abs(po["s_pool"]) < 0.25 and po["s_pool_lo"] <= 0 <= po["s_pool_hi"]),
            s_meta=m["mean"], s_meta_lo=m["mean"] - Z90 * m["se"], s_meta_hi=m["mean"] + Z90 * m["se"], s_meta_k=m["k"],
            CR_median=float(np.median(crs)) if len(crs) else np.nan, CR_share_below1=float(np.mean(crs < 1)) if len(crs) else np.nan,
            dsse_ro_mean=float(np.nanmean(dro)), dsse_ro_lo=float(np.nanmean(dro) - Z90 * L.jack_meta_se(dro)),
            dsse_ro_hi=float(np.nanmean(dro) + Z90 * L.jack_meta_se(dro)),
            dsse_t0_mean=float(np.nanmean(dt0)), dsse_t0_lo=float(np.nanmean(dt0) - Z90 * L.jack_meta_se(dt0)),
            imm_ro_share=float(a["THro_floor"].mean()), s_ro_mean=float(np.nanmean(sro)),
            s_ro_lo=float(np.nanmean(sro) - Z90 * L.jack_meta_se(sro)), s_ro_hi=float(np.nanmean(sro) + Z90 * L.jack_meta_se(sro)),
            s_pool_lpo=po_lpo["s_pool"], s_pool_lpo_lo=po_lpo["s_pool_lo"], s_pool_lpo_hi=po_lpo["s_pool_hi"],
            s_pool_ctrl=po_c["s_pool"], s_pool_ctrl_lo=po_c["s_pool_lo"], s_pool_ctrl_hi=po_c["s_pool_hi"], n_ctrl=po_c["n_agents"],
            s_pool_I=po_r["I"]["s_pool"], s_pool_I_lo=po_r["I"]["s_pool_lo"], s_pool_I_hi=po_r["I"]["s_pool_hi"],
            s_pool_II_III=po_r["II-III"]["s_pool"], s_pool_II_III_lo=po_r["II-III"]["s_pool_lo"], s_pool_II_III_hi=po_r["II-III"]["s_pool_hi"],
            S1_p_meta=float(mannwhitneyu(sI, sIII, alternative="greater").pvalue) if len(sI) >= 3 and len(sIII) >= 3 else np.nan,
            stretch=stretch,
        )
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    krows, arows = [], []
    for cfg in CFG:
        units_all = {}
        for des in designs():
            units_all[des] = L.build_units(des, cfg)
        # on-task trait: leave-kickoff-out mean settled level S over the agent's other eligible kickoffs (>= 2)
        S_by = {}
        for des, us in units_all.items():
            for u in us:
                if u["eligible"] and np.isfinite(u["S"]):
                    S_by.setdefault(u["agent"], []).append((des, u["S"]))
        for des, us in units_all.items():
            r = L.analyze_kickoff(us, n_boot=500, seed=int(des[1:]))
            g0 = L.group_stretch(us); gro = L.group_stretch(us, origin="ro")
            pa = r.pop("_per_agent", [])
            reg = us[0]["regime"] if us else None
            for x in pa:
                oth = [s for d_, s in S_by.get(x["agent"], []) if d_ != des]
                x.update(cfg=cfg, regime=reg, a_on=float(np.mean(oth)) if len(oth) >= 2 else None)
                arows.append(x)
            krows.append(dict(design=des, goal_no=int(des[1:]), regime=reg, cfg=cfg, **{k: v for k, v in r.items() if not isinstance(v, list)},
                              dlr=g0["dlr"], dlt_H=g0["dlt_H"], dlt_C=g0["dlt_C"], dlt_H_ro=gro["dlt_H"], dlt_C_ro=gro["dlt_C"]))
        print(cfg, "done", flush=True)
    kdf = pl.DataFrame(krows, infer_schema_length=None)
    adf = pl.DataFrame(arows, infer_schema_length=None)
    kdf.write_parquet(OUT / "kickoffs_all_configs.parquet")
    adf.write_parquet(OUT / "agents_all_configs.parquet")
    c = card(kdf, adf)
    (OUT / "card.json").write_text(json.dumps(c, indent=1, default=float))
    for cfg, v in c.items():
        print(f"{cfg}: rise {v['rise_share']:.2f} n {v['n_rising']} medDelta {v['median_Delta']:.3f} medTH {v['median_T_H']:.3f}h medTC {v['median_T_C']:.1f} "
              f"| POOL s {v['s_pool']:+.2f} [{v['s_pool_lo']:+.2f},{v['s_pool_hi']:+.2f}] P1 {v['P1_pool']} kill {v['kill_pool']} "
              f"| meta s {v['s_meta']:+.2f} [{v['s_meta_lo']:+.2f},{v['s_meta_hi']:+.2f}] | CR {v['CR_median']:.2f} ({v['CR_share_below1']:.2f}) "
              f"| dSSE_ro {v['dsse_ro_mean']:+.4f} [{v['dsse_ro_lo']:+.4f},{v['dsse_ro_hi']:+.4f}] | imm_ro {v['imm_ro_share']:.2f} s_ro {v['s_ro_mean']:+.2f} "
              f"| ctrl {v['s_pool_ctrl']:+.2f} [{v['s_pool_ctrl_lo']:+.2f},{v['s_pool_ctrl_hi']:+.2f}] lpo {v['s_pool_lpo']:+.2f} "
              f"| I {v['s_pool_I']:+.2f} II-III {v['s_pool_II_III']:+.2f} | stretch s_g {v['stretch']['s_g']:+.2f}")


if __name__ == "__main__":
    main()
