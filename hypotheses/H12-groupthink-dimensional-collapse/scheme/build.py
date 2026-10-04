"""H12 scheme: builds data/processed/H12-groupthink-dimensional-collapse/ from the shared tables (non-holdout only).

Outputs:
  units.parquet          one row per analysis unit (goal period split at H01's step changes): goal_no, unit, regime,
                         mode, N_catalog, days, n_days, scored (N_catalog >= 10, >= 2 days), role
  agents_units.parquet   unit x agent: lab, modal room (time-weighted over the unit's active windows) and its share,
                         activity presence (H02 rule: a row on every day and >= 30 active bins)
  spins.parquet          unit, pt_date, day, minute, agent, state (1 silent, 2 idle, 3 act, 4 talk), present only
  stmt_index.parquet     non-holdout statements: row, kind, agent, t, pt_date, win30, room, goal_no, regime, unit
  stmt_white_d64.npy     whitened statement vectors (regime whitener, top 64 components, fp16); the first 32 columns
                         are the d = 32 representation. No text anywhere.
Holdout days are dropped with a hard assertion (calendar.holdout and infra holdout_mask must agree).

Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/scheme/build.py
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import h12lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import load_whitener  # noqa: E402

GOAL_TABLE = L.ROOT / "hypotheses/hypohypotheses/goal-periods.md"
MIN_ACTIVE_BINS = 30


def goal_catalog() -> pl.DataFrame:
    rows = []
    for line in GOAL_TABLE.read_text().splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(\S+) → (\S+)\s*\|\s*([^|]*)\|\s*(\d+)\s*\|\s*([^|]*)\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|", line)
        if m:
            rows.append({"goal_no": int(m.group(1)), "N_catalog": int(m.group(5)), "reg_catalog": m.group(7),
                         "by": m.group(8), "mode": m.group(9)})
    cat = pl.DataFrame(rows).unique("goal_no", keep="first").sort("goal_no")
    assert cat.height == 51, cat.height
    return cat


def main():
    t0 = time.time()
    L.OUT.mkdir(parents=True, exist_ok=True)
    cal = pl.read_parquet(L.SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    hm = L.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    assert cal["holdout"].to_list() == hm, "calendar.holdout disagrees with holdout_mask"
    cal = cal.filter(~pl.col("holdout") & (pl.col("goal_no") > 0))
    assert not any(L.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    cal = cal.with_columns(pl.struct("goal_no", "pt_date").map_elements(lambda r: L.unit_of(r["goal_no"], r["pt_date"]),
                                                                       return_dtype=pl.String).alias("unit")).sort("pt_date")
    cat = goal_catalog()

    # ---- units
    u = (cal.group_by("unit", "goal_no").agg(pl.col("pt_date").sort().alias("days"), pl.len().alias("n_days"),
                                            pl.col("regime").unique().alias("regs"))
         .join(cat, on="goal_no", how="left").sort("goal_no", "unit"))
    assert all(len(r) == 1 for r in u["regs"]), "a unit spans regimes"
    u = u.with_columns(pl.col("regs").list.first().alias("regime")).drop("regs")
    u = u.with_columns(((pl.col("N_catalog") >= 10) & (pl.col("n_days") >= 2)).alias("scored"),
                       pl.lit("exploratory").alias("role"))

    # ---- activity spins (present population per unit)
    ab = (pl.scan_parquet(L.SH / "activity_bins.parquet").select("pt_date", "minute", "agent", "state")
          .filter(pl.col("pt_date").is_in(cal["pt_date"].to_list())).collect())
    ab = ab.join(cal.select("pt_date", "unit"), on="pt_date")
    nd = cal.group_by("unit").agg(pl.len().alias("nd_unit"))
    pres = (ab.group_by("unit", "agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("nact"))
            .join(nd, on="unit").with_columns(((pl.col("nd") == pl.col("nd_unit")) & (pl.col("nact") >= MIN_ACTIVE_BINS)).alias("present")))
    dayidx = cal.select("pt_date", "unit").with_columns(pl.col("pt_date").rank("ordinal").over("unit").cast(pl.Int16).sub(1).alias("day"))
    spins = (ab.join(pres.filter("present").select("unit", "agent"), on=["unit", "agent"], how="semi")
             .join(dayidx, on=["pt_date", "unit"])
             .select("unit", "pt_date", "day", pl.col("minute").cast(pl.Int16), "agent", "state").sort("unit", "day", "minute", "agent"))
    spins.write_parquet(L.OUT / "spins.parquet", compression="zstd")

    # ---- statements, whitened per regime
    st = (pl.read_parquet(L.SH / "embeddings/statements.parquet")
          .filter(~pl.col("holdout") & pl.col("pt_date").is_in(cal["pt_date"].to_list()))
          .join(cal.select("pt_date", "unit"), on="pt_date"))
    assert not any(L.holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    Ec = np.load(L.SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    Ei = np.load(L.SH / "embeddings/intentions_bge_small.npy", mmap_mode="r")
    kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy(); reg = st["regime"].to_numpy()
    Wout = np.zeros((st.height, 64), dtype=np.float16)
    for r in np.unique(reg):
        Wr = load_whitener(r, 64)
        for k, E in (("chat", Ec), ("intent", Ei)):
            m = (reg == r) & (kind == k)
            if m.any():
                Wout[m] = Wr(np.asarray(E[src[m]], dtype=np.float32)).astype(np.float16)
    st = st.with_row_index("row").select("row", "kind", "agent", "t", "pt_date", "win30", "room", "goal_no", "regime", "unit")
    st.write_parquet(L.OUT / "stmt_index.parquet", compression="zstd")
    np.save(L.OUT / "stmt_white_d64.npy", Wout)

    # ---- agents x units: lab, modal room, presence
    roster = pl.read_parquet(L.SH / "roster.parquet").select("agent", "name", "lab")
    rt = pl.read_parquet(L.SH / "rooms_timeline.parquet")
    win = cal.select("pt_date", "unit", "win_start", "win_end")
    ov = (rt.join(win, how="cross")
          .with_columns(pl.min_horizontal("t_end", "win_end").alias("e"), pl.max_horizontal("t_start", "win_start").alias("s"))
          .with_columns((pl.col("e") - pl.col("s")).dt.total_seconds().alias("ov")).filter(pl.col("ov") > 0)
          .group_by("unit", "agent", "room").agg(pl.col("ov").sum()))
    modal = (ov.with_columns((pl.col("ov") / pl.col("ov").sum().over("unit", "agent")).alias("share"))
             .sort("share", descending=True).group_by("unit", "agent").first().rename({"room": "room_modal", "share": "room_share"})
             .drop("ov"))
    nst = st.group_by("unit", "agent").agg(pl.len().alias("n_stmt"), (pl.col("kind") == "chat").sum().alias("n_chat"))
    au = (pres.select("unit", "agent", "present", "nd", "nact").join(nst, on=["unit", "agent"], how="full", coalesce=True)
          .join(modal, on=["unit", "agent"], how="left").join(roster, on="agent", how="left").sort("unit", "agent"))
    au.write_parquet(L.OUT / "agents_units.parquet", compression="zstd")

    # room count per unit (rooms holding >= 3 present agents as their modal room)
    rooms = (au.filter(pl.col("present").fill_null(False)).group_by("unit", "room_modal").len()
             .filter(pl.col("len") >= 3).group_by("unit").len().rename({"len": "n_rooms3"}))
    u = u.join(rooms, on="unit", how="left").with_columns(pl.col("n_rooms3").fill_null(0))
    npres = au.filter(pl.col("present").fill_null(False)).group_by("unit").len().rename({"len": "N_present"})
    u = u.join(npres, on="unit", how="left")
    u.write_parquet(L.OUT / "units.parquet", compression="zstd")

    L.write_provenance("hypotheses/H12-groupthink-dimensional-collapse/scheme/build.py",
                       ["activity_bins", "calendar", "roster", "rooms_timeline", "embeddings/statements",
                        "embeddings/chat_bge_small.npy", "embeddings/intentions_bge_small.npy", "embeddings/whitening_*"],
                       {"units": "goal periods split at H01 step changes", "min_active_bins": MIN_ACTIVE_BINS,
                        "whitening_dim_stored": 64, "holdout": "excluded (calendar.holdout == holdout_mask, asserted)"})
    with pl.Config(tbl_rows=60, tbl_width_chars=200):
        print(u.select("unit", "goal_no", "regime", "mode", "N_catalog", "N_present", "n_days", "n_rooms3", "scored"))
    print(f"spins {spins.height}, statements {st.height}; {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
