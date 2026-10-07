"""Scoring scatter (Sec. III): credence p against value if true V for every scored claim.

    uv run python writeup/figures-js/export/scoring_scatter.py

Replaces writeup/paper/figs/scoring_scatter.pdf (writeup/figures/make_scoring_scatter.py). Same source:
the `v2` block of every hypotheses/H*/summary/meta.json. Cards whose v2 credence is null (H133-H142, run on
2026-10-07 and not yet scored) are left out, as in the paper's counts. No data table is read, so nothing to mask.
Checks against the paper text (method.tex, "Scoring"): 132 scored claims, median credence 0.64, 82 claims at
p >= 0.6, M2 claims exactly H16 and H38.
"""
from __future__ import annotations

import glob
import json

import numpy as np

from common import ROOT, write

import sys
sys.path.insert(0, str(ROOT / "writeup/figures"))
import model_overrides as MO  # noqa: E402  (the paper's primary-model assignment)

# model families for the marker colour (primary model of each card)
FAMILY = {"01": "spins", "02": "spins", "10": "spins", "11": "fields", "03": "echoes", "09": "echoes",
          "16": "relax", "17": "relax", "04": "info", "15": "info"}

N_LABEL = 20


def main():
    rows = []
    for f in sorted(glob.glob(str(ROOT / "hypotheses/H*/summary/meta.json"))):
        v = json.load(open(f)).get("v2")
        if not v or v.get("credence") is None:
            continue
        hid = f.split("/hypotheses/")[1].split("/")[0].split("-")[0]
        rows.append(dict(id=hid, p=float(v["credence"]), V=float(v["value_if_true"]), eu=float(v["expected_usefulness"]),
                         m=v.get("mechanism_level", "M0"), fragile=bool(v.get("fragile", False))))
    prim = {h["id"]: next((m["model"] for m in h["models"] if m.get("role") == "primary"), "")
            for h in MO.load_hypotheses(scored_only=False)}
    for r in rows:
        r["model"] = prim.get(r["id"], "")
        r["family"] = FAMILY.get(r["model"], "other")
    ps = [r["p"] for r in rows]
    checks = dict(n=len(rows), median_p=float(np.median(ps)), n_p06=sum(p >= 0.6 for p in ps),
                  m2=sorted(r["id"] for r in rows if r["m"] == "M2"))
    assert checks["n"] == 132 and abs(checks["median_p"] - 0.64) < 1e-9 and checks["n_p06"] == 82, checks
    assert checks["m2"] == ["H16", "H38"], checks
    top = sorted(rows, key=lambda r: -r["eu"])[:N_LABEL]
    assert top[-1]["eu"] > sorted(rows, key=lambda r: -r["eu"])[N_LABEL]["eu"], "tie at the label cut"
    for r in rows:
        r["label"] = r in top
    import collections
    print(checks, "labelled:", [r["id"] for r in top], "families:", collections.Counter(r["family"] for r in rows))
    write("scoring_scatter", dict(rows=rows, checks=checks, n_label=N_LABEL), "writeup/figures-js/export/scoring_scatter.py",
          ["hypotheses/H*/summary/meta.json (v2)"], dict(n_label=N_LABEL))


if __name__ == "__main__":
    main()
