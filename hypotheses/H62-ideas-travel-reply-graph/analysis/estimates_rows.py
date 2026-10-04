"""Write H62 per-period rows to data/processed/shared/per_period_estimates.parquet (write_estimates).

  uv run python hypotheses/H62-ideas-travel-reply-graph/analysis/estimates_rows.py
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

DATA = ROOT / "data/processed/H62-ideas-travel-reply-graph"
SRC = "data/processed/H62-ideas-travel-reply-graph/results/periods.json"
NSRC = "data/processed/H62-ideas-travel-reply-graph/results/natives.json"


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
                    source=SRC, confirmatory=False, post_hoc=False, first_day=r["first_day"], last_day=r["last_day"])
        n = float(r["A_n_adopt"])
        out.append(dict(base, statistic="reply_premium_Lambda", estimate=r["Lam"], ci_lo=r.get("Lam_lo"),
                        ci_hi=r.get("Lam_hi"), se=r.get("Lam_bse"), n=n, n_kind="adoptions (idea-stratified)",
                        method="H62.cond_poisson recency window: HR_rep / HR_room (idea bootstrap)",
                        null="Lambda = 1 (room contagion; synthetic median 0.93)", ci_kind="percentile",
                        notes="se on log scale"))
        if r.get("T_ratio") is not None:
            out.append(dict(base, statistic="T_rep_over_T_room", estimate=r["T_ratio"], ci_lo=r.get("T_ratio_lo"),
                            ci_hi=r.get("T_ratio_hi"), se=r.get("T_ratio_logse"), n=float(r["n_rep"] + r["n_room"]),
                            n_kind="first-exposure events", method="H62.per-edge transmissibility, adoption in 3 talk calls",
                            null="ratio 1", ci_kind="percentile", notes="se on log scale"))
        if r.get("C_rep") is not None:
            out.append(dict(base, statistic="C_rep_seen_over_unread_only", estimate=r["C_rep"], ci_lo=r.get("C_rep_wlo"),
                            ci_hi=r.get("C_rep_whi"), se=r.get("C_rep_se"), n=n, n_kind="adoptions (idea-stratified)",
                            method="H62.cond_poisson matched lag 300 s, unread-only coding (A1)",
                            null="C = 1 (thread field; synthetic 0.98)", ci_kind="se_z",
                            notes=("powered" if r.get("B_rep_power") else "underpowered (<10 adoptions in a cell)")
                            + "; se on log scale"))
        out.append(dict(base, statistic="reply_premium_Lambda_guard", estimate=r["LamG"], ci_lo=r.get("LamG_lo"),
                        ci_hi=r.get("LamG_hi"), se=r.get("LamG_bse"), n=n, n_kind="adoptions (idea-stratified)",
                        method="H62.cond_poisson tie-only guard (edges before first use; no direct replies)",
                        null="Lambda = 1", ci_kind="percentile", notes="se on log scale"))
    nat = json.loads((DATA / "results/natives.json").read_text())
    for wk in ("39", "40", "41"):
        T = nat["NE42"]["T"][wk]
        out.append(dict(period_unit=unit_of(int(wk)), goal_no=int(wk), channel="content", role="native",
                        statistic="T_room_NE42", estimate=T[0], ci_lo=None, ci_hi=None, n=None, n_kind=None,
                        method="H62.NE42 per-edge room-only transmissibility by week", null="no change across the merge",
                        ci_kind="none", ci_level=None, source=NSRC, confirmatory=False, post_hoc=False,
                        unit_local=f"NE42:{wk}"))
    c = nat["NE42"]["cross"]
    out.append(dict(period_unit=unit_of(40), goal_no=40, channel="content", role="native",
                    statistic="T_rep_over_T_room_crossgroup", estimate=c["T_ratio"], ci_lo=c.get("T_ratio_lo"),
                    ci_hi=c.get("T_ratio_hi"), n=float(c["n_rep"] + c["n_room"]), n_kind="first-exposure events",
                    method="H62.NE42 cross-group pairs (#39 partition) in the merged week", null="ratio 1",
                    ci_kind="percentile", ci_level=0.95, source=NSRC, confirmatory=False, post_hoc=False,
                    unit_local="NE42:40cross"))
    h = nat["G12"]["hr"]
    out.append(dict(period_unit=unit_of(12), goal_no=12, channel="content", role="native",
                    statistic="HR_reply_crossteam_over_HR_room_sameteam", estimate=h.get("repX_vs_roomS"),
                    ci_lo=h.get("repX_vs_roomS_lo"), ci_hi=h.get("repX_vs_roomS_hi"), n=float(h["n_adopt"]),
                    n_kind="adoptions (idea-stratified)", method="H62.G12 DQ6 teams", null="ratio 1",
                    ci_kind="percentile", ci_level=0.95, source=NSRC, confirmatory=False, post_hoc=False,
                    notes="descriptive: 6 adoptions in the same-team room-only cell"))
    df = E.write_estimates(out, hypothesis="H62")
    print(f"wrote {df.height} H62 rows")


if __name__ == "__main__":
    main()
