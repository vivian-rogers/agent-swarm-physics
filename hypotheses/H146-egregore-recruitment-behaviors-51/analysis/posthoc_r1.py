"""H146 round 1 POST HOC (2026-10-09, after the estimates): is the read-gated re-expression after a wipe (P4,
HR R+ vs R- after call 10) specific to the patterns, or does any frequency-matched element set show it?
Draws 30 new pseudo-patterns per pattern (same matching rule as run_real.py, seed 777) and computes only the P4
read-gating HR. Writes results/posthoc_readgate_<set>.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h146lib as L  # noqa: E402
import run_real as RR  # noqa: E402


def main(set_):
    import coding_h145 as CH
    ev = L.load()
    pool = CH.build(ev)
    if set_ == "h145":
        cod = pool
        Ks, _, _ = RR.load_memeplexes(cod)
    else:
        cod, Ks = L.coding_candidates(ev)
    rng = np.random.default_rng(777)
    prof_pool = RR.profiles(pool)
    out = {}
    for k, K in Ks.items():
        pn = L.panel(ev, cod, K)
        E4 = L.p4_events(ev, cod, pn, K, RR.practice_slugs(cod, K))
        o = L.p4_stats(E4, B=0)
        real = ((o or {}).get("HR_read_F") or {}).get("est")
        excl = set(K.tolist()) if set_ == "h145" else set()
        sets, _ = RR.pseudo_sets(RR.k_profile_in(cod, K), prof_pool, excl, 30, rng)
        ps = []
        for S in sets:
            pS = L.panel(ev, pool, S)
            oS = L.p4_stats(L.p4_events(ev, pool, pS, S, RR.practice_slugs(pool, S)), B=0)
            ps.append(((oS or {}).get("HR_read_F") or {}).get("est"))
        v = np.array([x for x in ps if x is not None and np.isfinite(x)])
        out[k] = {"readgate_HR": real, "pseudo": ps, "pseudo_median": float(np.median(v)) if len(v) else None,
                  "p_pseudo": float((1 + (v >= real).sum()) / (len(v) + 1)) if real is not None and len(v) else None}
        print(k, json.dumps(out[k])[:200], flush=True)
    (RR.OUTR / f"posthoc_readgate_{set_}.json").write_text(json.dumps(RR.jsonable(out), indent=1))


if __name__ == "__main__":
    for s in sys.argv[1:]:
        main(s)
