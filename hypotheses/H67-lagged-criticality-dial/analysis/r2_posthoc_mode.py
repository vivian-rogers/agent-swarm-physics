"""H67 round 2, post hoc P2 (2026-10-05, after the real-data run; prompted by H50 round 2: in regime I a read raises
the chance that the next call is chat-mode). Two checks with the matched-lag in-flight design (h67lib main variant):
  (a) outcome = the call is chat-mode (is_chat), cells agent x day x wake (call mode not conditioned on);
  (b) outcome = talk, cells agent x day x wake: the reduced-form read-out gain including any mode-switch path.
Regime I and II units. Writes round2/posthoc_mode.parquet.

    uv run python hypotheses/H67-lagged-criticality-dial/analysis/r2_posthoc_mode.py
"""
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import polars as pl

import h67lib as L
import r2lib as R


def run(uid):
    c = pl.read_parquet(L.OUT / "units" / f"{uid}.parquet")
    m = pl.read_parquet(L.OUT / "msgs" / f"{uid}.parquet")
    d = L.all_counts(c, m).with_columns(pl.col("is_wake").cast(pl.Int8).alias("cls"))   # cells without call mode
    out = {"unit_id": uid}
    rt = L.fit(d, m, "main", True, B=200, seed=51)
    if rt.get("ok"):
        out.update({"g_nomode": rt["g"], "g_nomode_lo": rt.get("g_lo"), "g_nomode_hi": rt.get("g_hi"),
                    "g_nomode_se": rt.get("g_se"), "J_nomode": rt["J1"]})
    dm = d.with_columns(pl.col("is_chat").cast(pl.Boolean).alias("talk"))
    rm = L.fit(dm, m, "main", True, B=200, seed=52)
    if rm.get("ok"):
        out.update({"J_mode": rm["J1"], "J_mode_lo": rm.get("J1_lo"), "J_mode_hi": rm.get("J1_hi"),
                    "J_mode_se": rm.get("J1_se"), "chat_share": float(L._rows(d, True)["is_chat"].mean())})
    return out


def main():
    u1 = pl.read_parquet(L.OUT / "results" / "units.parquet").filter(pl.col("ok") & pl.col("regime").is_in(["I", "II"]))
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(run, u1["unit_id"].to_list()))
    df = pl.DataFrame(res, infer_schema_length=None).join(u1.select("unit_id", "regime", "goal_no", "g", "g_se"),
                                                          on="unit_id")
    df.write_parquet(R.R2 / "posthoc_mode.parquet")
    import r2_summarize as S
    for reg in ("I", "II"):
        s = df.filter(pl.col("regime") == reg)
        print(reg, s.height, "J_mode pool", S.re_pool(s["J_mode"], s["J_mode_se"]),
              "share J_mode>0 at 95%", float((s["J_mode_lo"] > 0).mean()),
              "\n  g_nomode pool", S.re_pool(s["g_nomode"], s["g_nomode_se"]), "median", float(s["g_nomode"].median()),
              "\n  g (r1) pool", S.re_pool(s["g"], s["g_se"]), "chat share", float(s["chat_share"].median()))


if __name__ == "__main__":
    main()
