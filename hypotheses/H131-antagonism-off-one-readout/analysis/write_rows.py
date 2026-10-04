"""H131: rows into per_period_estimates (G12 = unit 12a, where all ten debates fall; G26 = unit 26).
Usage: uv run python hypotheses/H131-antagonism-off-one-readout/analysis/write_rows.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

RES = ROOT / "data/processed/H131-antagonism-off-one-readout/results"
SRC = "data/processed/H131-antagonism-off-one-readout/results/results.json"
UNIT = {"12": ("12a", 12), "26": ("26", 26)}


def main():
    res = json.loads((RES / "results.json").read_text())
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet")
    rows = []
    for per, r in res.items():
        uid, g = UNIT[per]
        p = pu.filter(pl.col("unit_id") == uid).row(0, named=True)
        b = dict(hypothesis="H131", period_unit=uid, goal_no=g, first_day=p["first_day"], last_day=p["last_day"],
                 unit_local=f"G{g}", status="ok", source=SRC)
        for key, ch in (("did_flag", "stance_conflict_flag"), ("did_soft", "stance_p_disagree")):
            d = r[key]
            n = d["n_riv_open"] + d["n_mate_open"] + d["n_riv_set"] + d["n_mate_set"]
            for st, est, ci in (("readgated_settlement_did", d["delta"], d["delta_ci"]),
                                ("rival_contrast_after_read", d["g_set"], d["g_set_ci"]),
                                ("rival_contrast_open", d["g_open"], d["g_open_ci"])):
                rows.append(dict(**b, statistic=st, channel=ch, estimate=est, ci_lo=ci[0], ci_hi=ci[1], ci_level=0.95,
                                 ci_kind="percentile", n=float(n), n_kind="events", role="replication",
                                 method="LPM with speaker, target, debate x phase FE; read-gated prize state; cluster bootstrap over debates (#26: replies within phase)",
                                 null=f"relation permutation within debates, p {d['p_perm']:.4f}"))
        rows.append(dict(**b, statistic="inflight_rival_replies", channel="stance_conflict_flag",
                         estimate=float(r["inflight_rival"]), ci_lo=None, ci_hi=None, ci_kind="none", n=float(r["n"]),
                         n_kind="events", role="native", method="count of rival replies posted after the verdict but produced before the speaker's ledger read",
                         null=None))
        if per == "12":
            k = r["kernel_flag"]
            rows.append(dict(**b, statistic="first_postread_minus_later_rival_rate", channel="stance_conflict_flag",
                             estimate=k["d_k1_k2"], ci_lo=k["d_k1_k2_lo"], ci_hi=k["d_k1_k2_hi"], ci_level=0.90,
                             ci_kind="percentile", n=float(k["n_k1"] + k["n_k2"]), n_kind="events", role="native",
                             method="rival flag rate: each speaker's first post-read rival reply minus its later post-read rival replies; debate cluster bootstrap",
                             null="0"))
            s = r["switch_on_flag"]
            rows.append(dict(**b, statistic="first_postassign_minus_later_rival_rate", channel="stance_conflict_flag",
                             estimate=s["d_on"], ci_lo=s["d_on_lo"], ci_hi=s["d_on_hi"], ci_level=0.90,
                             ci_kind="percentile", n=float(s["n_on1"] + s["n_deb_later"]), n_kind="events", role="native",
                             method="rival flag rate: first rival reply after reading the team assignment minus later deb-phase rival replies; debate cluster bootstrap",
                             null="0"))
    rows = [x for x in rows if x["estimate"] is not None and math.isfinite(x["estimate"])]
    E.write_estimates(rows, hypothesis="H131")
    print("wrote", len(rows))


if __name__ == "__main__":
    main()
