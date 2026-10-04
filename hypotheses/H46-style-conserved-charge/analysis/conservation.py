"""H46 day-level conservation test and cross-boundary fingerprint for every NE class (O1, O2).

Outputs (data/processed/H46-style-conserved-charge/):
  conservation_rows.parquet  one row per (boundary, agent): D, percentile r, z per channel
  fingerprint.parquet        one row per boundary x variant: cross-boundary balanced accuracy, chance, ceiling
  conservation.json          class tests (T, CI, randomization and boundary-level p) per channel
Usage: uv run python hypotheses/H46-style-conserved-charge/analysis/conservation.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402

CHANNELS = {"style": "style_tc", "style_raw": "style_raw", "content": "content", "content_white": "content_white",
            "style_dm": "style_tc_dm", "content_dm": "content_dm"}
CROSS = {"content": "content_raw384", "content_white": "content_raw384", "content_dm": "content_raw384_dm"}
ALL_CLASSES = L.CLASSES + ["goal_skip"]


def main():
    m = L.load_messages()
    mats = {"style_tc": L.style_matrix(m, "tc"), "style_raw": L.style_matrix(m, "raw"),
            "content": L.content_matrix(m, "resid"), "content_white": L.content_matrix(m, "white")}
    dt_ = L.day_table(m, mats)
    L.add_demeaned(dt_, ["style_tc", "style_raw", "content", "content_white"])
    bounds = pl.read_parquet(L.DATA / "boundaries.parquet")
    fd = L.unit_first_days()
    main_b = bounds.filter(pl.col("ne") != "NE14")
    rows = L.eval_boundaries(main_b, dt_, CHANNELS, fd)
    # NE14 crosses regimes II -> III: content in raw bge space, on a subset day table (goals 33-38)
    ms = m.filter(pl.col("goal_no").is_in([33, 35, 36, 37, 38]))
    mats14 = {"style_tc": L.style_matrix(ms, "tc"), "style_raw": L.style_matrix(ms, "raw"),
              "content_raw384": L.content_matrix(ms, "raw384")}
    dt14 = L.day_table(ms, mats14)
    L.add_demeaned(dt14, ["style_tc", "style_raw", "content_raw384"])
    ch14 = {k: (v if k.startswith("style") else None) for k, v in CHANNELS.items()}
    rows14 = L.eval_boundaries(bounds.filter(pl.col("ne") == "NE14"), dt14, ch14, fd, cross_regime_map=CROSS)
    rows = pl.concat([rows, rows14], how="diagonal_relaxed")
    rows.write_parquet(L.DATA / "conservation_rows.parquet")
    print(rows.group_by("cls").agg(pl.len(), pl.col("r_style").mean(), pl.col("r_style_raw").mean(),
                                   pl.col("r_content").mean(), pl.col("r_content_white").mean(),
                                   pl.col("r_style_dm").mean(), pl.col("r_content_dm").mean()).sort("cls"))
    tests = {}
    for c in ALL_CLASSES + ["NE14_only"]:
        sub = rows.filter(pl.col("ne") == "NE14") if c == "NE14_only" else rows.filter(pl.col("cls") == c)
        tests[c] = {ch: L.class_test(sub, ch) for ch in CHANNELS}
    # fingerprint per boundary
    roster = pl.read_parquet(L.SH / "roster.parquet")
    anth = set(roster.filter(pl.col("lab") == "Anthropic")["agent"].to_list())
    fps = []
    for b in bounds.iter_rows(named=True):
        D = dt14 if b["ne"] == "NE14" else dt_
        variants = {"style": "style_tc_dm", "style_raw": "style_raw_dm",
                    "content": "content_raw384_dm" if b["ne"] == "NE14" else "content_dm"}
        if b["ne"] != "NE14":
            variants["content_white"] = "content_white_dm"
        for name, var in variants.items():
            for fam, ags in (("all", None), ("anthropic", anth)):
                r = L.fingerprint_boundary(D, var, set(b["pre"]), set(b["post"]), agents=ags)
                if "cross" in r:
                    fps.append({"cls": b["cls"], "ne": b["ne"], "label": b["label"], "variant": name, "family": fam, **r})
    fp = pl.DataFrame(fps)
    fp.write_parquet(L.DATA / "fingerprint.parquet")
    fsum = {}
    for c in ALL_CLASSES:
        f = fp.filter((pl.col("cls") == c))
        out = {}
        for (name, fam), g in f.group_by(["variant", "family"]):
            out[f"{name}|{fam}"] = {"n_boundaries": g.height, "cross": float(g["cross"].mean()),
                                    "chance": float(g["chance"].mean()),
                                    "ceiling": float(g["ceiling"].drop_nans().mean()) if g["ceiling"].drop_nans().len() else None,
                                    "share_ge_3x_chance": float((g["cross"] >= 3 * g["chance"]).mean()),
                                    "share_ge_2x_chance": float((g["cross"] >= 2 * g["chance"]).mean())}
        piv = (f.filter(pl.col("family") == "all").pivot(values="cross", index="label", on="variant"))
        if {"style", "content"} <= set(piv.columns):
            out["share_style_gt_content"] = float((piv["style"] > piv["content"]).mean())
        fsum[c] = out
    res = {"tests": tests, "fingerprint": fsum, "n_rows": rows.height,
           "n_agent_days": dt_.keys.height}
    (L.DATA / "conservation.json").write_text(json.dumps(res, indent=1, default=float))
    for c in ALL_CLASSES + ["NE14_only"]:
        t = tests[c]
        print(c, {ch: (round(t[ch].get("T", np.nan), 3), round(t[ch].get("lo", np.nan), 3), round(t[ch].get("hi", np.nan), 3),
                       round(t[ch].get("p_rand", np.nan), 4), round(t[ch].get("p_wilcoxon", np.nan) if t[ch].get("n") else np.nan, 4))
                  for ch in CHANNELS})
    print(json.dumps(fsum, indent=0, default=float)[:3000])


if __name__ == "__main__":
    main()
