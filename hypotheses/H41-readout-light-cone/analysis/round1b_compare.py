"""H41 round 1b (room-index fix, 2026-10-04): old -> new comparison of every room-dependent statistic.

  uv run python hypotheses/H41-readout-light-cone/analysis/round1b_compare.py

Old = data/processed/H41-readout-light-cone/round1/results/ (round 1, stale room index; reproducible with H41_ROOMS=old).
New = data/processed/H41-readout-light-cone/results/ (fixed index). Writes results/round1b_compare.json.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from write_period_cards import verdict_posthoc, verdict_rep  # noqa: E402

D = HERE.parents[2] / "data/processed/H41-readout-light-cone"
OLD, NEW = D / "round1/results", D / "results"
COLS = ["n_adopt", "share_cross", "acaus", "acaus_rob", "acaus_rob_within", "acaus_rob_cross", "J_in", "J_in_ci_lo",
        "J_in_ci_hi", "risk_pre_in", "adopt_o1_in", "powered_in", "J_mh", "J_mh_lo", "J_mh_hi", "J_mh_len", "J_mh_N",
        "J_mh_N_lo", "J_mh_D", "J_mh_U", "J_mh_W", "J", "v4", "v4_hinf", "out_room", "cyc_med", "talk_med", "b",
        "b_ci_lo", "b_ci_hi", "c", "c_ci_lo", "c_ci_hi", "n_reg", "acaus_rob_n", "acaus_rob_cross_n",
        "acaus_rob_identified", "control_identified"]
CH = ["timing", "templated", "human_logged", "human_crosspost", "common_stimulus", "artifact", "web", "private", "search",
      "room_move"]


def clean(x):
    if isinstance(x, float) and (math.isnan(x)):
        return None
    if isinstance(x, float) and math.isinf(x):
        return "inf"
    return x


def pooled_lift(summ: dict) -> dict:
    rob = {c: 0 for c in CH}
    ctl = {c: 0 for c in CH}
    n_rob = n_ctl = 0
    for k, v in summ.items():
        ch = v.get("channels", {}) if isinstance(v, dict) else {}
        if "rob_counts" not in ch:
            continue
        n_rob += ch.get("acaus_rob_n") or 0
        n_ctl += ch.get("control_n") or 0
        for c in CH:
            rob[c] += ch["rob_counts"].get(c, 0)
            ctl[c] += ch["ctl_counts"].get(c, 0)
    return dict(n_rob=n_rob, n_ctl=n_ctl, lift={c: (rob[c] / n_rob) / (ctl[c] / n_ctl) if ctl[c] and n_rob else None
                                                for c in CH},
                rate_rob={c: rob[c] / n_rob if n_rob else None for c in CH})


def main():
    to, tn = pl.read_parquet(OLD / "period_table.parquet"), pl.read_parquet(NEW / "period_table.parquet")
    out = {"periods": {}}
    for g in sorted(set(tn["goal"].to_list())):
        ro = to.filter(pl.col("goal") == g).to_dicts()[0]
        rn = tn.filter(pl.col("goal") == g).to_dicts()[0]
        diff = {c: (clean(ro.get(c)), clean(rn.get(c))) for c in COLS if clean(ro.get(c)) != clean(rn.get(c))}
        vo = (verdict_rep(ro)[0], verdict_posthoc(ro))
        vn = (verdict_rep(rn)[0], verdict_posthoc(rn))
        if diff or vo != vn:
            out["periods"][f"G{g:02d}"] = dict(changed=diff, verdict_old=vo, verdict_new=vn)
    # tallies (card headline counts)
    for name, t in (("old", to), ("new", tn)):
        rows = t.to_dicts()
        out[f"tally_{name}"] = dict(
            J_in_sig=sum(1 for r in rows if (r.get("J_in_ci_lo") or 0) > 1),
            J_mh_sig=sum(1 for r in rows if (r.get("J_mh_lo") or 0) > 1 or (r.get("J_mh") is not None
                         and math.isinf(r["J_mh"]) and (r.get("J_in_ci_lo") or 0) > 1)),
            verdicts=sorted((r["goal"], verdict_rep(r)[0], verdict_posthoc(r)) for r in rows),
            within_rob_max=max((r.get("acaus_rob_within") or 0) for r in rows),
            within_rob_median=float(pl.Series([r.get("acaus_rob_within") or 0 for r in rows]).median()),
            cross_rob=sorted((r["goal"], round(r["acaus_rob_cross"], 3), round(r["share_cross"], 3))
                             for r in rows if (r.get("share_cross") or 0) > 0.01 and r.get("acaus_rob_cross") is not None),
        )
    so, sn = json.loads((OLD / "summary.json").read_text()), json.loads((NEW / "summary.json").read_text())
    out["lift_old"], out["lift_new"] = pooled_lift(so), pooled_lift(sn)
    out["across_old"], out["across_new"] = so.get("across"), sn.get("across")
    no, nn = json.loads((OLD / "native.json").read_text()), json.loads((NEW / "native.json").read_text())
    keys = {"G38": ["n_cross", "share_cross", "a_cross_out_of_cone", "a_cross_out_of_cone_rob", "b_ratio", "b_ratio_ci",
                    "c_cross_n", "c_cross_artweb", "c_within_n", "c_within_artweb", "d_ratio", "verdict"],
            "G51": ["n_isolated", "n_focus_cross", "b_focus_cross_incone", "b_focus_cross_incone_rob", "b_focus_Htr",
                    "cad_b", "cad_b_lo", "cad_b_hi", "cad_c", "cad_c_lo", "cad_c_hi", "checks", "verdict"],
            "G31": ["J_in", "J_in_ci", "J_in_regIII_median", "checks", "verdict"],
            "NE42": ["a_ratio_40_39", "a_ratio_40_41", "a_ratio_40_39_ci", "a_ratio_40_41_ci", "checks", "verdict"]}
    out["native"] = {k: {kk: (no[k].get(kk), nn[k].get(kk)) for kk in v} for k, v in keys.items()}
    for g in ("G39", "G40", "G41"):
        out["native"][f"NE42_{g}"] = {kk: (no["NE42"][g].get(kk), nn["NE42"][g].get(kk))
                                      for kk in ("acaus_cross", "acaus_within", "ratio_cross_within", "h_cross")}
    (NEW / "round1b_compare.json").write_text(json.dumps(out, indent=1, default=clean))
    for k, v in out["periods"].items():
        print(k, v["verdict_old"], "->", v["verdict_new"])
        for c, (a, b) in v["changed"].items():
            print(f"   {c}: {a} -> {b}")
    for k in ("tally_old", "tally_new"):
        print(k, {kk: vv for kk, vv in out[k].items() if kk != "verdicts"})
    print("lift old", {k: round(v, 2) if v else v for k, v in out["lift_old"]["lift"].items()}, out["lift_old"]["n_rob"],
          out["lift_old"]["n_ctl"])
    print("lift new", {k: round(v, 2) if v else v for k, v in out["lift_new"]["lift"].items()}, out["lift_new"]["n_rob"],
          out["lift_new"]["n_ctl"])
    print("across", out["across_old"], out["across_new"])
    for k, v in out["native"].items():
        print(k, json.dumps(v, default=clean))


if __name__ == "__main__":
    main()
