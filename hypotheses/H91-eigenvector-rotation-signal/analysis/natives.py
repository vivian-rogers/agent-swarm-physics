"""H91 native tests (predictions in goalperiod-subhypotheses/NE42 and G51, written before running).
NE42: talk and content rotation at the 05-04 merge and the 05-11 split; NE42 vs goal-only kickoffs.
G51: stationarity between events in the densest baseline; #focus open (08-05) and empty (08-24); roster-join pairs.
Output: data/processed/H91-eigenvector-rotation-signal/native/results.json
"""
from __future__ import annotations

import json

import numpy as np
import polars as pl

import h91lib as L

H36 = L.ROOT / "data/processed/H36-reorganization-alarm/r1b/fixed_bge_none/events.parquet"


def val(d, t, c):
    x = d.filter(pl.col("pt_date") == t)
    return None if not x.height or x[c][0] is None or not np.isfinite(x[c][0]) else float(x[c][0])


def main():
    rng = np.random.default_rng(L.SEED + 1)
    d = pl.read_parquet(L.OUT / "days_scored.parquet")
    rot = pl.read_parquet(L.OUT / "rotation.parquet").join(d.select("pt_date", "dist_event"), on="pt_date", how="left")
    ev = pl.read_parquet(H36).filter(~pl.col("holdout0"))
    out = {}
    # ------------------------------------------------------------------ NE42
    ne = {}
    for t, lab in (("2026-05-04", "merge"), ("2026-05-11", "split")):
        ne[lab] = {c: val(d, t, c) for c in ("z_talk", "p_talk", "A_T", "z_content_bge", "z_content_gte", "p_content_bge",
                                             "p_content_gte", "A_C", "R1m", "N_talk", "L_talk", "N_C", "W_C")}
        ne[lab]["zs_talk"] = val(d, t, "zs_talk")
    goal_only = ev.filter((pl.col("cls") == "goal") & ~pl.col("confounded"))["pt_date0"].to_list()
    go = d.filter(pl.col("pt_date").is_in(goal_only))
    at = go["A_T"].to_numpy().astype(float); at = at[np.isfinite(at)]
    zt = go["z_talk"].to_numpy().astype(float); zt = zt[np.isfinite(zt)]
    m_ne = np.nanmean([ne["merge"]["A_T"], ne["split"]["A_T"]])
    ne["goal_only"] = {"n_A_T": int(len(at)), "median_A_T": float(np.median(at)), "n_z_talk": int(len(zt)),
                       "median_z_talk": float(np.median(zt)), "rank_of_NE42_mean_A_T": float(np.mean(at < m_ne))}
    ne["N1a"] = {lab: (ne[lab]["z_talk"] is not None and ne[lab]["z_talk"] >= 2) for lab in ("merge", "split")}
    ne["N1b"] = any((ne[lab]["A_C"] or -9) >= 2 for lab in ("merge", "split"))
    ne["N1c"] = bool(m_ne > ne["goal_only"]["median_A_T"])
    ne["verdict"] = ("supported" if all(ne["N1a"].values()) else
                     "failed" if (not any(ne["N1a"].values()) and not ne["N1b"]) else "mixed")
    out["NE42"] = ne
    # ------------------------------------------------------------------ G51
    g = {}
    r51 = rot.filter((pl.col("goal_no") == 51) & (pl.col("goal_a") == 51))
    quiet = r51.filter(pl.col("dist_event") >= 2)
    for ch in ("content_bge", "content_gte", "talk"):
        x = quiet.filter(pl.col("channel") == ch)
        if ch == "talk":
            x = x.filter((pl.col("N") >= 16) & (pl.min_horizontal("La", "Lb") >= 240))
        k, n = int((x["p2_boot"] < 0.05).sum()), x.height
        allp = r51.filter(pl.col("channel") == ch)
        g[ch] = {"n_quiet": n, "s_sig_quiet": k / n if n else None, "ci": L.wilson(k, n),
                 "median_z_quiet": float(x["z2_boot"].median()) if n else None,
                 "n_all": allp.height, "s_sig_all": float((allp["p2_boot"] < 0.05).mean()) if allp.height else None,
                 "median_z_all": float(allp["z2_boot"].median()) if allp.height else None}
    g["N2a_content"] = float(np.mean([g[c]["s_sig_quiet"] for c in ("content_bge", "content_gte")]))
    g["N2a_content_pass"] = g["N2a_content"] <= 0.15
    g["N2a_talk_pass"] = g["talk"]["s_sig_quiet"] is not None and g["talk"]["s_sig_quiet"] <= 0.15
    g["focus_open"] = {c: val(d, "2026-08-05", c) for c in ("z_talk", "p_talk", "A_T", "z_C", "A_C", "N_talk", "L_talk")}
    g["focus_empty"] = {c: val(d, "2026-08-24", c) for c in ("z_talk", "p_talk", "A_T", "z_C", "A_C", "N_talk", "L_talk")}
    fo = g["focus_open"]
    g["N2b_open_pass"] = bool((fo["z_talk"] or -9) >= 2 or (fo["A_T"] or -9) >= 2)
    g["N2b_empty_pass"] = bool((g["focus_empty"]["z_talk"] or -9) >= 2)
    joins = ["2026-07-09", "2026-07-10", "2026-07-17", "2026-07-24", "2026-08-28", "2026-09-01", "2026-09-03", "2026-09-04"]
    jz = d.filter(pl.col("pt_date").is_in(joins))["z_C"].to_numpy().astype(float)
    qz = d.filter((pl.col("goal_no") == 51) & (pl.col("dist_event") >= 2))["z_C"].to_numpy().astype(float)
    jz, qz = jz[np.isfinite(jz)], qz[np.isfinite(qz)]
    g["joins"] = {"n": int(len(jz)), "mean_z": float(jz.mean()), "quiet_mean_z": float(qz.mean()), "quiet_sd": float(qz.std(ddof=1)),
                  "within_1sd": bool(abs(jz.mean() - qz.mean()) <= qz.std(ddof=1)),
                  "p_perm_greater": L.mannwhitney_p(jz, qz, rng)}
    g["verdict"] = ("supported" if (g["N2a_content_pass"] and g["N2b_open_pass"]) else
                    "failed" if (not g["N2a_content_pass"] and not g["N2b_open_pass"]) else "mixed")
    out["G51"] = g
    (L.OUT / "native").mkdir(exist_ok=True)
    (L.OUT / "native/results.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
