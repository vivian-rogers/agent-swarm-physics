"""The kappa table (H87, model 04): bits, value and value per bit for each memory channel.

    uv run python writeup/figures-js/export/h87_kappa.py

Reuses `table()` from writeup/visuals/H87-kappa-table/make.py, so every number is the one the old figure drew.
Input: data/processed/H87-kappa-channel-table/results/results.json (H87's non-reserved round-1 results; NE41 forced
erasures vs pseudo-erasures, and NE34 new-goal kickoffs for the K row). Intervals: agent-day paired bootstrap 95%.
Identified = lower bound of I_c above the 0.02-bit floor (H87's A1 rule); kappa is shown only for identified rows.
"""
from __future__ import annotations

import importlib.util
import json

from common import ROOT, write

R = ROOT / "data/processed/H87-kappa-channel-table/results/results.json"
ROWS = [("C", "context window"), ("A", "own artifact"), ("M", "memory note"), ("G", "chat reads"),
        ("H", "human messages"), ("Q", "history search"), ("K", "kickoff")]
FLOOR = 0.02


def old_make():
    spec = importlib.util.spec_from_file_location("h87_make", ROOT / "writeup/visuals/H87-kappa-table/make.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def main():
    res = json.loads(R.read_text())
    rows, ne = old_make().table(res)
    out = []
    for c, name in ROWS:
        r = rows[c]
        ident = r["I_ci"] is not None and r["I_ci"][0] > FLOOR
        assert ident == (r["k"] is not None), c          # kappa drawn exactly where identified
        out.append(dict(code=c, name=name, I=r["I"], I_ci=r["I_ci"], dV=r["dV"], dV_ci=r["dV_ci"], k=r["k"],
                        k_ci=r["k_ci"], identified=ident))
    C = rows["C"]
    # numbers printed in the figure must match the paper text (models-partial.tex, H87 item and fig:kappa)
    assert f"{C['I']:.3f}" == "0.078" and f"{C['dV']:.2f}" == "0.41"
    assert [f"{v:.1f}" for v in (C["k"], *C["k_ci"])] == ["5.2", "3.8", "7.9"]
    assert f"{rows['A']['k']:.1f}" == "-0.6"
    data = dict(rows=out, floor=FLOOR, n_scramble=ne["n_scramble"], n_placebo=ne["n_placebo"])
    print({r["code"]: (round(r["I"], 3), round(r["dV"], 2), r["k"] and round(r["k"], 1), r["identified"]) for r in out})
    write("h87_kappa", data, "writeup/figures-js/export/h87_kappa.py",
          ["data/processed/H87-kappa-channel-table/results/results.json"], dict(floor=FLOOR))


if __name__ == "__main__":
    main()
