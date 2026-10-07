"""H08 read-out jump (Fig. fig:readoutjump): (a) G38 offset profile, own room vs other-room placebo; (b) the jump
D = G(1) - G(0) per period for replies and mentions, with the other-room null.

    uv run python writeup/figures-js/export/h08_readout_jump.py

Reuses load_c9 / regime_of / PERIODS from writeup/visuals/H08-context-is-the-coupling/make.py (the old matplotlib
figure fig_bc.pdf), so the numbers are identical. Reads data/processed/H08-context-is-the-coupling/r1b/<G>/c9.json and
summary_r1b.json only. All 17 periods are outside the reserved data (asserted with the locked list).
Units: percentage points (pp). Mentions = 'addr' (the call names the sender); replies = 'auth' (answers the sender).
"""
from __future__ import annotations

import importlib.util
import sys

from common import ROOT, write


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# the old make.py does `from common import holdout_mask` (infra/shared/common.py); give it that module while it loads
sc = load_module("shared_common", ROOT / "infra/shared/common.py")
_ours = sys.modules["common"]; sys.modules["common"] = sc
mk = load_module("h08make", ROOT / "writeup/visuals/H08-context-is-the-coupling/make.py")
sys.modules["common"] = _ours


def ci(v):
    return [100 * float(x) for x in v]


def main():
    held = set(sc.load_holdout()["goal_periods_held_out"])
    assert not {int(g[1:]) for g in mk.PERIODS} & held, "a reserved period is in the figure"
    c9 = mk.load_c9()
    ex = c9[mk.EX_PERIOD]
    offs = [-2, -1, 0, 1, 2, 3]
    profile = {k: [dict(o=o, G=ci(ex[k]["addr"]["G"][str(o)])) for o in offs] for k in ("primary", "other_room")}
    rows = []
    for g in mk.PERIODS:
        d = c9[g]
        orr = d.get("other_room")
        rows.append(dict(period=g, regime=mk.regime_of(g), reply=ci(d["primary"]["auth"]["D"]),
                         mention=ci(d["primary"]["addr"]["D"]),
                         null=ci(orr["addr"]["D"]) if orr and d["n_pairs_other"] > 0 else None))
    n_m = sum(r["mention"][1] > 0 for r in rows); n_r = sum(r["reply"][1] > 0 for r in rows)
    nn = [r for r in rows if r["null"]]; n_flat = sum(r["null"][1] <= 0 <= r["null"][2] for r in nn)
    counts = dict(mentions_pos=n_m, replies_pos=n_r, null_flat=n_flat, null_n=len(nn), n=len(rows))
    assert (n_m, n_r, n_flat, len(nn), len(rows)) == (14, 17, 8, 8, 17), counts   # paper: 14/17, 17/17, 8/8
    print(counts)
    write("h08_readout_jump", dict(example=mk.EX_PERIOD, n_days=ex["n_days"], profile=profile, periods=rows, counts=counts),
          "writeup/figures-js/export/h08_readout_jump.py",
          ["data/processed/H08-context-is-the-coupling/r1b/<period>/c9.json", "r1b/summary_r1b.json"],
          dict(periods=mk.PERIODS, example=mk.EX_PERIOD, response_a="addr (names sender)", units="pp"))


if __name__ == "__main__":
    main()
