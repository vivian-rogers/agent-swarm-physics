"""H41 replication layer: the common estimator on every eligible period.

  uv run python hypotheses/H41-readout-light-cone/analysis/explore.py

Reads data/processed/H41-readout-light-cone/G<NN>/ and writes results/period_table.parquet, results/summary.json.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h41stats as S  # noqa: E402

OUT = HERE.parents[2] / "data/processed/H41-readout-light-cone"
RES = OUT / "results"
CHANNELS = ["timing", "templated", "human_logged", "human_crosspost", "common_stimulus", "artifact", "web", "private",
            "search", "room_move"]


def channel_label(v: pl.DataFrame) -> pl.DataFrame:
    """First matching channel in the card's order; 'unexplained' otherwise."""
    expr = pl.lit("unexplained")
    for c in reversed(CHANNELS):
        expr = pl.when(pl.col(c).fill_null(False)).then(pl.lit(c)).otherwise(expr)
    return v.with_columns(expr.alias("channel"))


def fix_cross(adf: pl.DataFrame) -> pl.DataFrame:
    """Cross-room = adopter's known room at t0 differs from the source room (room -1 = unknown, not cross)."""
    return adf.with_columns(((pl.col("room_t0") != pl.col("room0")) & (pl.col("room_t0") >= 0)).alias("cross"))


def channel_summary(v: pl.DataFrame, adf: pl.DataFrame) -> dict:
    if v.height == 0:
        return {}
    v = v.join(adf.select("marker", "agent", "cross", "in_cone_len", "cls"), on=["marker", "agent"], how="left")
    v = channel_label(v)
    out = {}
    if "control" in v.columns:
        ctl = v.filter(pl.col("control"))
        v = v.filter(~pl.col("control"))
        out["control_n"] = ctl.height
        if ctl.height:
            out["control_identified"] = float((ctl["channel"] != "unexplained").mean())
            out["control_identified_nontiming"] = float((ctl.filter(pl.col("channel") != "timing")["channel"] != "unexplained").mean())
            out["control_any"] = {c: float(ctl[c].fill_null(False).mean()) for c in CHANNELS}
            for cr in [True, False]:
                s2 = ctl.filter(pl.col("cross") == cr)
                key = "cross" if cr else "within"
                out[f"control_{key}_n"] = s2.height
                if s2.height:
                    out[f"control_{key}_artweb"] = float((s2["artifact"].fill_null(False) | s2["web"].fill_null(False)).mean())
    rob = v.filter(~pl.col("in_cone") & ~pl.col("in_cone_len"))
    if "control_any" in out and rob.height:
        out["lift"] = {c: (float(rob[c].fill_null(False).mean()) / out["control_any"][c]) if out["control_any"][c] > 0 else None
                       for c in CHANNELS}
        out["rob_counts"] = {c: int(rob[c].fill_null(False).sum()) for c in CHANNELS}
        out["ctl_counts"] = {c: int(round(out["control_any"][c] * out["control_n"])) for c in CHANNELS}
    for name, sub in [("acaus", v.filter(~pl.col("in_cone"))), ("acaus_rob", v.filter(~pl.col("in_cone") & ~pl.col("in_cone_len"))),
                      ("unexposed_incone", v.filter(pl.col("in_cone") & ~pl.col("exposed")))]:
        n = sub.height
        out[f"{name}_n"] = n
        if n:
            cnt = sub.group_by("channel").len()
            out[f"{name}_mix"] = {r["channel"]: r["len"] / n for r in cnt.iter_rows(named=True)}
            out[f"{name}_any"] = {c: float(sub[c].fill_null(False).mean()) for c in CHANNELS}
            out[f"{name}_identified"] = float((sub["channel"] != "unexplained").mean())
            out[f"{name}_identified_nontiming"] = float(sub.filter(pl.col("channel") != "timing")
                                                        .select((pl.col("channel") != "unexplained").mean()).item()) \
                if sub.filter(pl.col("channel") != "timing").height else np.nan
            for cr in [True, False]:
                s2 = sub.filter(pl.col("cross") == cr)
                key = "cross" if cr else "within"
                out[f"{name}_{key}_n"] = s2.height
                if s2.height:
                    out[f"{name}_{key}_artweb"] = float((s2["artifact"].fill_null(False) | s2["web"].fill_null(False)).mean())
                    out[f"{name}_{key}_identified"] = float((s2["channel"] != "unexplained").mean())
    return out


def main():
    RES.mkdir(parents=True, exist_ok=True)
    rows, summ = [], {}
    for d in sorted(OUT.glob("G[0-9][0-9]")):
        g = int(d.name[1:])
        meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
        if not (d / "adoptions.parquet").exists():
            continue
        adf = fix_cross(pl.read_parquet(d / "adoptions.parquet"))
        hz = pl.read_parquet(d / "hazard.parquet") if (d / "hazard.parquet").exists() else pl.DataFrame()
        v = pl.read_parquet(d / "violations.parquet") if (d / "violations.parquet").exists() else pl.DataFrame()
        vs = S.violation_shares(adf, B=300, seed=g)
        hj = S.hazard_jump(hz, B=500, seed=g)
        ve = S.velocity(adf)
        cr = S.cadence_regression(adf, B=300, seed=g)
        ch = channel_summary(v, adf)
        hm = S.hazard_jump_mh(hz, B=300, seed=g) if hz.height else {}
        hml = S.hazard_jump_mh(hz, B=200, seed=g, prefix="L_") if hz.height else {}
        hmc = {c: S.hazard_jump_mh(hz, B=200, seed=g, cls=c) for c in range(4)} if hz.height else {}
        row = dict(goal=g, regime=meta.get("regime"), n_agents=meta.get("n_agents"), days=meta.get("days"),
                   n_items=meta.get("n_items"), n_adopt=adf.height)
        row.update({k: v_ for k, v_ in vs.items() if not isinstance(v_, tuple)})
        for k, v_ in vs.items():
            if isinstance(v_, tuple):
                row[k + "_lo"], row[k + "_hi"] = v_
        for k, v_ in hj.items():
            if isinstance(v_, tuple):
                row[k + "_lo"], row[k + "_hi"] = v_
            else:
                row[k] = v_
        for k, v_ in ve.items():
            if isinstance(v_, tuple):
                row[k + "_lo"], row[k + "_hi"] = v_
            else:
                row[k] = v_
        for k, v_ in cr.items():
            if isinstance(v_, tuple):
                row[k + "_lo"], row[k + "_hi"] = v_
            else:
                row[k] = v_
        row["J_mh"], (row["J_mh_lo"], row["J_mh_hi"]) = hm.get("J_mh"), hm.get("J_mh_ci", (None, None))
        row["J_mh_len"], (row["J_mh_len_lo"], row["J_mh_len_hi"]) = hml.get("J_mh"), hml.get("J_mh_ci", (None, None))
        for c, nm in enumerate("UDNW"):
            x = hmc.get(c, {})
            row[f"J_mh_{nm}"], (row[f"J_mh_{nm}_lo"], row[f"J_mh_{nm}_hi"]) = x.get("J_mh"), x.get("J_mh_ci", (None, None))
            row[f"risk_pre_in_{nm}"], row[f"adopt_pre_in_{nm}"] = x.get("risk_pre_in"), x.get("adopt_pre_in")
            row[f"adopt_o1_in_{nm}"] = x.get("adopt_o1_in")
        for k in ["acaus_n", "acaus_rob_n", "acaus_rob_identified", "acaus_rob_identified_nontiming", "unexposed_incone_n",
                  "acaus_rob_cross_n", "acaus_rob_within_n", "acaus_rob_cross_artweb", "acaus_rob_within_artweb",
                  "acaus_rob_cross_identified", "acaus_rob_within_identified", "acaus_identified", "control_n",
                  "control_identified", "control_identified_nontiming", "control_within_artweb", "control_cross_artweb"]:
            row[k] = ch.get(k)
        rows.append(row)
        summ[f"G{g:02d}"] = dict(meta=meta, violations=vs, hazard=hj, hazard_mh=hm, hazard_mh_len=hml,
                                 hazard_mh_cls={k_: v_ for k_, v_ in hmc.items()}, velocity=ve, cadence=cr, channels=ch)
        print(f"G{g:02d} n={adf.height} A={vs.get('acaus'):.3f} Arob={vs.get('acaus_rob'):.3f} "
              f"J_in={hj.get('J_in', np.nan):.2f} [{hj.get('J_in_ci', (np.nan, np.nan))[0]:.2f},{hj.get('J_in_ci', (np.nan, np.nan))[1]:.2f}] "
              f"Jmh={hm.get('J_mh', np.nan):.2f} [{hm.get('J_mh_ci', (np.nan, np.nan))[0]:.2f},{hm.get('J_mh_ci', (np.nan, np.nan))[1]:.2f}] "
              f"cyc={ve.get('cyc_med')} talk={ve.get('talk_med')} b={cr.get('b', np.nan):.2f} c={cr.get('c', np.nan):.2f}", flush=True)
    tab = pl.DataFrame(rows, infer_schema_length=None)
    tab.write_parquet(RES / "period_table.parquet")
    # across-period cadence vs volume (period-level parameters; no pooling of data)
    t2 = tab.filter(pl.col("med_dt").is_not_null())
    if t2.height >= 5:
        r_tau = stats.spearmanr(t2["med_dt"], t2["med_tau"])
        r_vol = stats.spearmanr(t2["med_dt"], 1.0 / t2["med_vol"])
        summ["across"] = dict(rho_dt_tau=float(r_tau.statistic), p_tau=float(r_tau.pvalue),
                              rho_dt_invvol=float(r_vol.statistic), p_vol=float(r_vol.pvalue), n=t2.height)
    (RES / "summary.json").write_text(json.dumps(summ, indent=1, default=lambda o: None if o is None else float(o)
                                                 if isinstance(o, (np.floating, np.integer)) else str(o)))
    print(summ.get("across"))


if __name__ == "__main__":
    main()
