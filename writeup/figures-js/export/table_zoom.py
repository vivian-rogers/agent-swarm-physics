"""Table zoom (Sec. III): (a) part of the hypothesis x physics-model table (H01-H20, 17 models);
(b) one cell, H08 under model 02, resolved into verdicts per goal period.

    uv run python writeup/figures-js/export/table_zoom.py

Replaces writeup/paper/figs/table_zoom.pdf (writeup/figures/make_table_zoom.py). Same sources and logic:
  (a) meta.json `models` of each card with writeup/figures/model_overrides.py applied (models 16 and 17);
  (b) the latest per-period verdict written in each period README of the H08 card
      (Verdict (r2) > Verdict (2) > Verdict (1c) > Verdict (1b) > Verdict), via dashboard/collect.
Reserved goal periods come from hypotheses/holdout.json (infra/shared/common.py: load_holdout); they are marked,
not read. No data table is read.
"""
from __future__ import annotations

import sys

from common import ROOT, write

sys.path.insert(0, str(ROOT / "writeup/figures"))
import model_overrides as mo  # noqa: E402
from importlib import util as _u  # noqa: E402

collect = mo.collect
ZOOM_H, ZOOM_M = "H08", "02"
ROWS = [f"H{i:02d}" for i in range(1, 21)]
LATEST = ("Verdict (r2)", "Verdict (2)", "Verdict (1c)", "Verdict (1b)", "Verdict")


def shared_common():
    spec = _u.spec_from_file_location("shared_common", ROOT / "infra/shared/common.py")
    sc = _u.module_from_spec(spec); spec.loader.exec_module(sc)
    return sc


def latest_verdicts(h):
    out = {}
    for p in h["periods"]:
        t = (collect.ROOT / p["path"]).read_text(errors="replace")
        v = next((x for x in (collect.field(t, k) for k in LATEST) if x), "")
        out[p["period"]] = collect.verdict_key(v)
    return out


def main():
    hs = {h["id"]: h for h in mo.load_hypotheses()}
    cells = []
    for hid in ROWS:
        for m in hs.get(hid, {}).get("models") or []:
            if m["model"] in mo.COLS:
                cells.append(dict(h=hid, model=m["model"], role=m["role"], outcome=m.get("outcome") or "untested"))
    h = hs[ZOOM_H]
    verd = latest_verdicts(h)
    held = sorted(shared_common().load_holdout()["goal_periods_held_out"])
    periods = [dict(goal=g, verdict=verd.get(f"G{g:02d}"), reserved=g in held,
                    regime="I" if g <= 32 else ("II" if g <= 36 else "III")) for g in range(1, 52)]
    nes = [dict(id=k, verdict=v) for k, v in sorted(verd.items()) if k.startswith("NE")]
    tested = [p for p in periods if p["verdict"]]
    assert not any(p["reserved"] for p in tested), "a reserved period carries a verdict"
    assert len(tested) == 17, len(tested)       # paper: H08 runs on 17 periods outside the reserved data
    zoom_cell = next(c for c in cells if c["h"] == ZOOM_H and c["model"] == ZOOM_M)
    data = dict(rows=ROWS, cols=mo.COLS, short=mo.SHORT, name=mo.NAME, cells=cells,
                zoom=dict(h=ZOOM_H, model=ZOOM_M, title=mo.clean_title(h["title"]), cell=zoom_cell,
                          periods=periods, nes=nes))
    from collections import Counter
    print("cells", len(cells), Counter(c["role"] for c in cells), Counter(c["outcome"] for c in cells))
    print("zoom", zoom_cell, Counter(p["verdict"] for p in tested), nes, "reserved", held)
    write("table_zoom", data, "writeup/figures-js/export/table_zoom.py",
          ["hypotheses/H*/summary/meta.json (models)", "writeup/figures/model_overrides.py",
           "hypotheses/H08-*/goalperiod-subhypotheses/*/README.md", "hypotheses/holdout.json"],
          dict(rows="H01-H20", zoom=f"{ZOOM_H} x {ZOOM_M}"))


if __name__ == "__main__":
    main()
