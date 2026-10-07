"""Section II figure: one real G38 message and the calls of its room-mates (read-out call, H08).

    uv run python writeup/figures-js/export/s2_readout_example.py

Reuses pick_example() from writeup/visuals/H08-context-is-the-coupling/make.py unchanged, so the example message, the
receiving (read-out) call and the in-flight call are the ones of the H08 table (make.py asserts this). The example day
is checked against the reserved data inside pick_example (holdout_mask).
Inputs: data/processed/H08-context-is-the-coupling/r1b/G38/{readout,turns}.parquet; shared chat_core, roster.
"""
from __future__ import annotations

import importlib.util

import numpy as np

from common import ROOT, write

X0, PAD = -35.0, 35.0


def load_h08():
    import sys
    # make.py does `from common import holdout_mask` (infra/shared/common.py); our export/common.py has the same name,
    # so load the shared one under that name while make.py imports, then restore ours.
    sspec = importlib.util.spec_from_file_location("common", ROOT / "infra/shared/common.py")
    shared = importlib.util.module_from_spec(sspec)
    sspec.loader.exec_module(shared)
    ours = sys.modules.get("common")
    sys.modules["common"] = shared
    try:
        f = ROOT / "writeup/visuals/H08-context-is-the-coupling/make.py"
        spec = importlib.util.spec_from_file_location("h08_make", f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    finally:
        sys.modules["common"] = ours
    return m


def main():
    h08 = load_h08()
    ex = h08.pick_example()
    lanes = ex["lanes"]
    x1 = max(l["W"] for l in lanes[1:]) + PAD
    out = []
    for i, l in enumerate(lanes):
        calls = []
        for j, (s, t) in enumerate(zip(l["s"], l["t"])):
            if t < X0 or s > x1:
                continue
            kind = "call"
            if i > 0 and j == l.get("infl"):
                kind = "infl"
            if i > 0 and j == l.get("recv"):
                kind = "recv"
            calls.append(dict(s=float(s), t=float(t), kind=kind, reply=bool(i > 0 and j == l.get("recv") and l["replied"])))
        d = dict(name=l["name"], sender=i == 0, calls=calls)
        if i > 0:
            k = l["recv"]
            d.update(W=float(l["W"]), recv_s=float(l["s"][k]), recv_t=float(l["t"][k]), replied=bool(l["replied"]),
                     infl=l["infl"] is not None)
        out.append(d)
    rec = out[1:]
    infl = [r for r in rec if r["infl"]]
    pause = [r for r in rec if not r["infl"]]
    summary = dict(n_infl=len(infl), n_pause=len(pause),
                   W_infl=[min(r["W"] for r in infl), max(r["W"] for r in infl)],
                   W_pause=[min(r["W"] for r in pause), max(r["W"] for r in pause)],
                   replied_pause=sum(r["replied"] for r in pause), replied_infl=sum(r["replied"] for r in infl))
    print("msg", ex["msg"], ex["day"], "room", ex["room"], summary)
    for r in rec:
        print(f"  {r['name']:20s} W={r['W']:6.1f} infl={r['infl']} replied={r['replied']}")
    write("s2_readout_example", dict(period=h08.EX_PERIOD, day=ex["day"], msg=ex["msg"], x0=X0, x1=float(x1),
                                     lanes=out, summary=summary),
          "writeup/figures-js/export/s2_readout_example.py",
          ["data/processed/H08-context-is-the-coupling/r1b/G38/readout.parquet", "G38/turns.parquet",
           "data/processed/shared/chat_core.parquet", "roster.parquet"],
          dict(period=h08.EX_PERIOD, x0=X0, pad=PAD))


if __name__ == "__main__":
    main()
