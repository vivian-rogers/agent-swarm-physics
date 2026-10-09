"""Model 17 (collective modes vs a calibrated random-matrix edge) paper figure, single column, from H12 round 1b.

    uv run python writeup/figures-js/export/m17_modes.py

Reuses writeup/papers/thermodynamics/figs/make_model17.py: panel_a() and panel_b() run on a throwaway matplotlib axis so the counts,
medians and the #12 statistics are the ones of the old figure (panel_a warns if a count differs from the card). The
per-unit ratios are read with the same filter and columns as panel_a.
(a) per scored unit (24 non-reserved units), top eigenvalue / calibrated 95% surrogate edge, three channels;
(b) #12 debates: participation ratio of content (bge) after the verdict vs while the motion is on, paired.
Inputs: data/processed/H12-groupthink-dimensional-collapse/r1b/{unit_table.parquet, native/g12_debates.parquet,
native/native.json}.
"""
from __future__ import annotations

import importlib.util

import numpy as np
import polars as pl

from common import ROOT, write

D = ROOT / "data/processed/H12-groupthink-dimensional-collapse/r1b"
CHANS = (("activity", "l1_edge_trim"), ("talk", "talk_l1_edge_trim"), ("content", "content_l1_edge"))


def load_m17():
    spec = importlib.util.spec_from_file_location("make_model17", ROOT / "writeup/papers/thermodynamics/figs/make_model17.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_shared_common():
    spec = importlib.util.spec_from_file_location("shared_common", ROOT / "infra/shared/common.py")
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
    return sc


def main():
    import matplotlib.pyplot as plt
    m17 = load_m17()
    fig, ax = plt.subplots(1, 2)
    ca = m17.panel_a(ax[0])
    cb = m17.panel_b(ax[1])
    plt.close(fig)
    for k, v in ca.items():
        assert v[0] == m17.CARD_COUNTS[k], (k, v[0], m17.CARD_COUNTS[k])
    u = pl.read_parquet(D / "unit_table.parquet").filter(pl.col("scored")).sort("unit")
    print("unit_table columns:", u.columns[:12])
    chans = []
    for name, col in CHANS:
        y = u[col].to_numpy().astype(float)
        assert np.isfinite(y).all() and len(y) == 24
        chans.append(dict(name=name, y=y, above=int((y > 1).sum()), n=len(y), median=float(np.median(y))))
    # reserved-data check on the unit goal periods (units are built from non-reserved periods by the H12 scheme)
    sc = load_shared_common()
    held = set(sc.load_holdout()["goal_periods_held_out"])
    if "goal_no" in u.columns:
        assert not held & set(u["goal_no"].to_list()), "reserved period among the units"
    pairs = [dict(off=float(a), on=float(b)) for a, b in zip(cb["off"], cb["on"])]
    data = dict(channels=chans, debates=dict(pairs=pairs, n_low=cb["n_low"], n=cb["n"], median_rel=cb["rel"], p=cb["p"],
                                             n_debates=cb["n_debates"]))
    print({c["name"]: (f"{c['above']}/{c['n']}", round(c["median"], 3)) for c in chans})
    print("G12", cb["n_low"], "/", cb["n"], "rel", round(cb["rel"], 4), "p", round(cb["p"], 4), "of", cb["n_debates"])
    write("m17_modes", data, "writeup/figures-js/export/m17_modes.py",
          ["data/processed/H12-groupthink-dimensional-collapse/r1b/unit_table.parquet", "r1b/native/g12_debates.parquet",
           "r1b/native/native.json"], dict(channels=[c for _, c in CHANS]))


if __name__ == "__main__":
    main()
