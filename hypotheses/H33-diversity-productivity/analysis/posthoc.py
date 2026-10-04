"""H33 post hoc checks (run AFTER evaluate.py; decide no verdict). Non-holdout eligible units only.

1. PR15 robustness variant: tail size above its breakpoint, without #51, and with PR10 restricted to the same rows
   (is the steep right-side slope a property of PR15 or of the high-volume subsample?).
2. Leave-one-period-out stability of the primary two-lines slopes.
Writes posthoc.json.
Usage: uv run python hypotheses/H33-diversity-productivity/analysis/posthoc.py
"""
from __future__ import annotations

import json

import h33lib as H  # noqa: I001
import h33common as C
import numpy as np


def tl(x, y, Z, au, day):
    D = H.Design([au, day], au, Z)
    r, sp = H.two_lines(D, D.dm(y), x)
    return {k: r[k] for k in ("xc", "b1", "p1", "b2", "p2", "n_lo", "n_hi")} | {"x_max": sp["x_max"], "interior": sp["interior"]}


def main():
    out = {}
    ad, x, y, Z, au, day = H.load_pooled("pr15", "writes")
    out["pr15_all"] = tl(x, y, Z, au, day)
    m = ad["unit"].to_numpy() != "51"
    out["pr15_without_51"] = tl(x[m], y[m], Z[m], H.codes(au[m]), H.codes(day[m]))
    m = ad["unit"].to_numpy() == "51"
    out["pr15_only_51"] = tl(x[m], y[m], Z[m], H.codes(au[m]), H.codes(day[m]))
    x10 = ad["pr10"].to_numpy().astype(float)
    out["pr10_on_pr15_rows"] = tl(x10, y, Z, au, day)
    ad, x, y, Z, au, day = H.load_pooled("pr10", "writes")
    lopo = []
    for u in sorted(set(ad["unit"].to_list())):
        m = ad["unit"].to_numpy() != u
        r = tl(x[m], y[m], Z[m], H.codes(au[m]), H.codes(day[m]))
        lopo.append({"dropped": u} | r)
    out["lopo_pr10"] = lopo
    out["lopo_summary"] = {"min_p1": min(r["p1"] for r in lopo), "min_p2": min(r["p2"] for r in lopo),
                           "n_u_supported": sum(r["b1"] > 0 and r["b2"] < 0 and r["p1"] < 0.05 and r["p2"] < 0.05 for r in lopo)}
    (C.OUT / "posthoc.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "lopo_pr10"}, indent=1, default=float))
    for r in lopo:
        print(r["dropped"], f"b1 {r['b1']:+.3f} p {r['p1']:.3f}  b2 {r['b2']:+.3f} p {r['p2']:.3f} xc {r['xc']:.1f}")


if __name__ == "__main__":
    main()
