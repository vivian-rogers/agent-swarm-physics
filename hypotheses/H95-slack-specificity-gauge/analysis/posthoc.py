"""H95 POST-HOC analysis (amendment A2, written after the replication run; labelled post hoc everywhere).

The pre-registered gauge x (day-1 share on H54-named repos) does not track kickoff specificity: H54's loose name-token
flags give the free 'novel research' kickoff x = 0.74 and 'build your own world' x = 0. This script tests the reading
the HH intended with a design code d taken from the goal titles (listed on the card before the run, but not
pre-registered as a predictor):
  d = 1  the goal assigns a concrete artifact to build or run (own world #39, connect the worlds #40, own YouTube
         channel #42, fine-tune the leader #44 #best, assigned private goals #51);
  d = 0  the goal names an objective or leaves the choice open (pick your own goal #37, raise money for a charity #38,
         novel research #41, #44 #rest own goals; #36 'interact with agents outside the village' as sensitivity).
Statistic: exact one-sided Mann-Whitney (S larger for d = 0) over the nine units; also T_e.
  uv run python hypotheses/H95-slack-specificity-gauge/analysis/posthoc.py
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h95lib as L  # noqa: E402

D = {"G37": 0, "G38": 0, "G39": 1, "G40": 1, "G41": 0, "G42": 1, "G44best": 1, "G44rest": 0, "G51": 1}


def mw_exact(a, b):
    """P(U >= observed) for 'b larger than a' under all relabelings (exact)."""
    v = np.r_[a, b]
    n = len(b)
    obs = sum((y > x) + 0.5 * (y == x) for x in a for y in b)
    cnt = tot = 0
    for idx in itertools.combinations(range(len(v)), n):
        bb = v[list(idx)]
        aa = np.delete(v, idx)
        u = sum((y > x) + 0.5 * (y == x) for x in aa for y in bb)
        cnt += u >= obs - 1e-12
        tot += 1
    return float(obs), float(cnt / tot)


def main():
    acr = json.load(open(L.OUTD / "results/across.json"))
    pu = acr["per_unit"]
    out = {"post_hoc": True, "code": D}
    for key in ("S_e", "T_e"):
        a = [pu[n][key] for n in D if D[n] == 1]
        b = [pu[n][key] for n in D if D[n] == 0]
        u, p = mw_exact(a, b)
        out[key] = {"assigned": a, "open": b, "U": u, "p_one_sided": p,
                    "max_assigned": float(max(a)), "min_open": float(min(b))}
        a2, b2 = a, b + [acr["G36"][key]]
        out[key + "_with_G36"] = {"U_p": mw_exact(a2, b2)}
    nat = json.load(open(L.OUTD / "results/natives.json"))
    out["G38_rooms_S"] = {k: v["S_e"] for k, v in nat["N2_G38"]["per_room"].items()}
    L.write_json(L.OUTD / "results/posthoc_design_code.json", out)
    print(out)


if __name__ == "__main__":
    main()
