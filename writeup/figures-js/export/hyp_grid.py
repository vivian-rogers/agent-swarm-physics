"""Appendix grid: every hypothesis (rows, grouped by primary physics model) x every goal period and natural
experiment (columns), cell = the period's verdict, as in hypotheses/OVERVIEW.md.

    uv run python writeup/figures-js/export/hyp_grid.py

Verdict per period folder: the same rule as infra/overview/build_overview.py (a decided round-2 line, else the
round-1b verdict, else the round-1 verdict; one parser, dashboard/collect.py: verdict_key). Primary model per card:
writeup/figures/model_overrides.py (the paper's 17-model assignment). Regime and reserved flag per goal period:
data/processed/shared/calendar.parquet.
"""
from __future__ import annotations

import re
import sys

import polars as pl

from common import ROOT, write

sys.path.insert(0, str(ROOT / "infra/overview"))
sys.path.insert(0, str(ROOT / "writeup/figures"))
sys.path.insert(0, str(ROOT / "dashboard"))
import build_overview as BO  # noqa: E402
import model_overrides as MO  # noqa: E402
from collect import verdict_key  # noqa: E402

HYP = ROOT / "hypotheses"


def main():
    hs = MO.load_hypotheses(scored_only=False)
    rows = []
    for h in hs:
        prim = [m["model"] for m in h["models"] if m.get("role") == "primary"]
        rows.append(dict(id=h["id"], title=MO.clean_title(h.get("title") or ""), model=prim[0] if prim else "",
                         scored=(HYP / next(d.name for d in HYP.iterdir() if d.name.startswith(h["id"] + "-"))
                                 / "summary/meta.json").exists()))
    cells = []
    for d in sorted(x for x in HYP.iterdir() if x.is_dir() and re.match(r"^H\d{2,}-", x.name)):
        hid = d.name.split("-")[0]
        sub = d / "goalperiod-subhypotheses"
        cands = (list(sub.iterdir()) if sub.is_dir() else []) + [x for x in d.iterdir() if not (sub / x.name).exists()]
        for p in cands:
            if p.is_dir() and BO.PERIOD_RE.match(p.name) and (p / "README.md").exists():
                t = p.read_text() if p.is_file() else (p / "README.md").read_text()
                v = BO.round2_verdict(t) or BO.field(t, "Verdict (1b)") or BO.field(t, "Verdict")
                role = BO.field(t, "Role")
                cells.append(dict(h=hid, p=p.name, v=verdict_key(v), confirm=role.lower().startswith("confirm")))
    cal = (pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet").group_by("goal_no")
           .agg(pl.col("regime").first().cast(pl.String), pl.col("holdout").any()))
    cal = {int(r["goal_no"]): r for r in cal.iter_rows(named=True)}

    def key(p):
        m = BO.PERIOD_RE.match(p)
        return (0, int(m.group(2)), m.group(3)) if m.group(2) else (1, int(m.group(4)), "")
    pids = sorted({c["p"] for c in cells}, key=key)
    periods = []
    for p in pids:
        m = BO.PERIOD_RE.match(p)
        if m.group(2):
            c = cal.get(int(m.group(2)), {})
            periods.append(dict(id=p, kind="G", goal=int(m.group(2)), regime=c.get("regime"), reserved=bool(c.get("holdout"))))
        else:
            periods.append(dict(id=p, kind="NE", goal=None, regime=None, reserved=False))
    vc = {}
    for c in cells:
        vc[c["v"]] = vc.get(c["v"], 0) + 1
    print(len(rows), "hypotheses;", len(periods), "columns;", len(cells), "cells;", vc,
          "; no primary:", [r["id"] for r in rows if not r["model"]])
    write("hyp_grid", dict(rows=rows, periods=periods, cells=cells, names=MO.NAME),
          "writeup/figures-js/export/hyp_grid.py",
          ["hypotheses/H*/goalperiod-subhypotheses/*/README.md", "writeup/figures/model_overrides.py",
           "data/processed/shared/calendar.parquet"])


if __name__ == "__main__":
    main()
