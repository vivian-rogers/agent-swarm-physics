"""Post hoc (H25 outputs appeared after H34's predictions): idea branching vs H25's per-period and per-day dials.

  uv run python hypotheses/H34-idea-cascades/analysis/h25_link.py
Reads data/processed/H25-criticality-dial/{dial_period,dial_daily}.parquet (read-only) and H34's results; writes
results/h25_link.json. Channels: activity (variant none), talk (none), content (F2, H25's primary content variant).
Caveat: R-hat and the content dial are both computed from the same chat messages, so they share variance by
construction (term reuse and embedding alignment co-occur); this is a consistency check, not an independent instrument.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import h34core as C  # noqa: E402

H25 = C.ROOT / "data/processed/H25-criticality-dial"
CH = [("activity", "none"), ("talk", "none"), ("content", "F2")]


def partial_spearman(y, x, z):
    Y, X, Z = (stats.rankdata(v) for v in (y, x, z))
    A = np.c_[np.ones_like(Z), Z]
    ry = Y - A @ np.linalg.lstsq(A, Y, rcond=None)[0]
    rx = X - A @ np.linalg.lstsq(A, X, rcond=None)[0]
    r = stats.pearsonr(ry, rx)
    return float(r.statistic), float(r.pvalue)


def main():
    t = pl.read_parquet(C.OUT / "results/period_table.parquet").filter(pl.col("cls") == "ALL").select("goal", "R", "R_c", "p3", "N_room")
    per = pl.read_parquet(H25 / "dial_period.parquet")
    daily = pl.read_parquet(H25 / "dial_daily.parquet")
    out = {"period": {}, "daily": {}}
    for ch, var in CH:
        q = per.filter((pl.col("channel") == ch) & (pl.col("variant") == var)).select(pl.col("goal_no").alias("goal"), pl.col("fe").alias("g"))
        j = t.join(q, on="goal")
        for y in ("R", "R_c", "p3"):
            r = stats.spearmanr(j[y], j["g"])
            pr = partial_spearman(j[y].to_numpy(), j["g"].to_numpy(), j["N_room"].to_numpy())
            out["period"][f"{y}~{ch}"] = dict(rho=float(r.statistic), p=float(r.pvalue), n=j.height, partial_N_rho=pr[0], partial_N_p=pr[1])
        rows = []
        dd = daily.filter((pl.col("channel") == ch) & (pl.col("variant") == var) & pl.col("g").is_not_nan()).select("pt_date", "g")
        for g in t["goal"].to_list():
            days = json.loads((C.OUT / f"G{g:02d}/meta.json").read_text())["days"]
            tr = pl.read_parquet(C.OUT / f"G{g:02d}/trees.parquet")
            dr = (tr.group_by("day").agg(((pl.col("size") - 1).sum() / pl.col("size").sum()).alias("R"), pl.len().alias("n"))
                  .with_columns(pl.col("day").map_elements(lambda i: days[i], return_dtype=pl.Utf8).alias("pt_date")))
            for r in dr.join(dd, on="pt_date").filter(pl.col("n") >= 20).iter_rows(named=True):
                rows.append(dict(goal=g, R=r["R"], g=r["g"], day=r["day"]))
        D = pl.DataFrame(rows).with_columns((pl.col("R") - pl.col("R").mean().over("goal")).alias("dR"),
                                            (pl.col("g") - pl.col("g").mean().over("goal")).alias("dg"))
        r = stats.spearmanr(D["dR"], D["dg"])
        D2 = D.filter(pl.col("day") > 0)
        r2 = stats.spearmanr(D2["dR"], D2["dg"])
        out["daily"][ch] = dict(rho=float(r.statistic), p=float(r.pvalue), n_days=D.height, rho_no_kickoff=float(r2.statistic),
                                p_no_kickoff=float(r2.pvalue))
    (C.OUT / "results/h25_link.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
