"""H146 CONFIRMATORY test on the reserved #51 tail (51m, 2026-09-07 -> 09-18). Frozen 2026-10-09 after round 1.
NOT RUN. Dry-run only until Vivian signs off.

Refuses to read any reserved day unless BOTH flags are given:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` applies the identical rules to the round-1 exploration results (results/real_h145.json,
results/posthoc_readgate_h145.json) as stand-ins; it reads no reserved day.

Frozen criteria (H145's 15 memeplexes K01-K15 as frozen in memeplexes.json md5 9b899c34; same codings, same
estimators, 30 pseudo-patterns per memeplex, same matching rule; K14 excluded as too small):
  C1  Survival of amnesia (P4): the median over memeplexes of HR(re-expression, forced wipe vs placebo, calls 1-20)
      is >= 0.8 and no memeplex with >= 300 host wipes has HR < 0.5.          (round 1: median 0.90, range 0.78-1.11)
  C2  Generic, not pattern-specific (P1b, P4 read-gating, P6 specialization): for each of the three statistics, the
      number of memeplexes with p_pseudo <= 0.05 is <= 2 of 14, and no memeplex has p_pseudo <= 0.05 on two of the
      three. (round 1: P1b 0, read-gating 0 (post hoc), specialization 2 (K05, K15); none on two.)
  C3  No repair after wipes (P5): no memeplex has wipe RR > 1.2 with CI above 1. (round 1: RR 0.95-1.07)
  Confirmed ("patterns survive amnesia as generic vocabulary, not as egregores with functional behaviors") if C1, C2
  and C3 all hold. Refuted if C2 fails (>= 3 memeplexes beyond pseudo on one statistic, or one on two).
Before a real run: the event tables must be rebuilt for 51m with a separate, reviewed switch in scheme/build.py
(not written), and this script re-frozen if any input changed. Disclose in the card and LOG.md first.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
D = HERE.parents[2] / "data" / "processed" / "H146-egregore-recruitment-behaviors-51" / "results"
sys.path.insert(0, str(HERE))


def p_pseudo(val, ps, lower=False):
    v = np.array([x for x in ps if x is not None and np.isfinite(x)], float)
    if val is None or not len(v):
        return None
    return float((1 + ((v <= val) if lower else (v >= val)).sum()) / (len(v) + 1))


def rules(real, rg):
    Ks = [k for k in real["patterns"] if k != "K14"]
    hr, wipe, hits = [], [], {"P1b": [], "readgate": [], "spec": []}
    for k in Ks:
        st, ps = real["patterns"][k]["stats"], real["patterns"][k]["pseudo"]["values"]
        p4 = st.get("P4") or {}
        if p4.get("HR_F_vs_P") is not None:
            hr.append((k, p4["HR_F_vs_P"], p4.get("n_F", 0)))
        w = (st.get("P5") or {}).get("wipe") or {}
        wipe.append((k, w.get("rr"), (w.get("ci") or [None])[0]))
        d = (st.get("P1b") or {}).get("delta")
        if d and p_pseudo(d[0], ps["P1b"]) is not None and p_pseudo(d[0], ps["P1b"]) <= 0.05:
            hits["P1b"].append(k)
        if rg and k in rg and rg[k].get("p_pseudo") is not None and rg[k]["p_pseudo"] <= 0.05:
            hits["readgate"].append(k)
        z = (st.get("P6_spec") or {}).get("z")
        if z is not None and p_pseudo(z, ps["P6_spec_z"]) <= 0.05:
            hits["spec"].append(k)
    med = float(np.median([h for _, h, _ in hr]))
    c1 = med >= 0.8 and not any(h < 0.5 and n >= 300 for _, h, n in hr)
    from collections import Counter
    cnt = Counter(k for v in hits.values() for k in v)
    c2 = all(len(v) <= 2 for v in hits.values()) and not any(c >= 2 for c in cnt.values())
    c3 = not any(r is not None and lo is not None and r > 1.2 and lo > 1 for _, r, lo in wipe)
    return {"C1": {"median_HR": med, "holds": c1}, "C2": {"hits": hits, "holds": c2},
            "C3": {"holds": c3, "max_rr": max(r for _, r, _ in wipe if r is not None)},
            "confirmed": c1 and c2 and c3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    A = ap.parse_args()
    if A.confirm:
        if not A.ack:
            sys.exit("refused: --confirm needs --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
        raise NotImplementedError("the 51m event tables are not built; add a reviewed reserved switch to "
                                  "scheme/build.py, re-freeze this script, disclose, then run")
    if not A.dry_run:
        sys.exit("use --dry-run (exploration stand-ins) or the two confirm flags")
    real = json.loads((D / "real_h145.json").read_text())
    rgp = D / "posthoc_readgate_h145.json"
    rg = json.loads(rgp.read_text()) if rgp.exists() else None
    print(json.dumps(rules(real, rg), indent=1))


if __name__ == "__main__":
    main()
