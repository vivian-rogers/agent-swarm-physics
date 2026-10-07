"""H134 round 1, POST HOC (written after the O4 result): is the forced-reset leave step a flicker artifact?

A flicker leave: the agent leaves A for B and returns to A at B's next hop within 5 own calls (A -> B -> A; the shared
label README reports 25.7% of hops are such flickers). Sustained leave = a leave that is not a flicker.
Same MH contrast as O4 (strata agent x dwell decile x f decile, d >= 10), per unit, pooled over G51 and G38 by
inverse variance; the pseudo-reset placebo is repeated. Also: the O4 contrast without the f decile in the strata.
Output: results/posthoc.json
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h134lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

Z = 1.959964


def main():
    v = pl.read_parquet(L.OUT / "visits.parquet").sort("visit")
    v = v.with_columns(nxt_proj=pl.col("project").shift(-1).over("agent"), nxt2_proj=pl.col("project").shift(-2).over("agent"),
                       nxt_len=pl.col("d_last").shift(-1).over("agent"),
                       nxt_vis=pl.col("visit").shift(-1).over("agent"), nxt2_vis=pl.col("visit").shift(-2).over("agent"))
    v = v.with_columns(flicker=(pl.col("completed") == 1) & (pl.col("nxt2_proj") == pl.col("project"))
                       & (pl.col("nxt_len") <= 6) & (pl.col("nxt_vis") == pl.col("visit") + 1)
                       & (pl.col("nxt2_vis") == pl.col("visit") + 2))
    flick = set(v.filter(pl.col("flicker"))["visit"].to_list())
    share = len(flick) / max(v["completed"].sum(), 1)
    counts = {r["unit_id"]: r for r in __import__("json").loads((L.OUT / "counts.json").read_text())}
    out = {"flicker_share_of_completed": share, "units": {}}
    for u, c in counts.items():
        if not c["testable"]:
            continue
        U = L.load_unit(u)
        fl = np.isin(U["visit"], np.array(sorted(flick))) & (U["y"] == 1)
        ysus = np.where(fl, 0.0, U["y"])
        r = {}
        for nm, y in (("all", U["y"]), ("sustained", ysus)):
            (lor, se, nt), _ = L.reset_contrast(y, U["d"], U["f"], U["f_pre"], U["forced"], U["agent"], U["forced"])
            (plor, pse, pnt), _ = L.reset_contrast(y, U["d"], U["f"], U["f"], U["forced"], U["agent"], U["pseudo"] & ~U["forced"])
            r[nm] = {"lor": lor, "se": se, "n": nt, "placebo": plor, "placebo_se": pse,
                     "rate_reset": float(y[U["forced"] & (U["d"] >= 10)].mean()),
                     "rate_ctrl": float(y[~U["forced"] & (U["d"] >= 10)].mean())}
        out["units"][u] = r
    for per, pre in (("G51", "51"), ("G38", "38")):
        for nm in ("all", "sustained"):
            for key, sk in (("lor", "se"), ("placebo", "placebo_se")):
                a = np.array([[out["units"][u][nm][key], out["units"][u][nm][sk]] for u in out["units"] if u.startswith(pre)], float)
                a = a[np.isfinite(a).all(1) & (a[:, 1] > 0)]
                w = 1 / a[:, 1] ** 2
                m = float(np.sum(w * a[:, 0]) / w.sum()); s = float(np.sqrt(1 / w.sum()))
                out[f"{per}_{nm}_{key}"] = [m, m - Z * s, m + Z * s]
    L.jdump(out, L.OUT / "results" / "posthoc.json")
    print({k: v for k, v in out.items() if k != "units"})


if __name__ == "__main__":
    main()
