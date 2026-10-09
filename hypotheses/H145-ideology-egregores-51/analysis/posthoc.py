"""POST HOC (2026-10-09, after the round-1 outcomes): robustness of the P3a pass (K03) and descriptives.
  (1) K03 colonial A excess z on each half of the 45 days (days 0-21, 22-44), 2-h bins.
  (2) K03 at host thresholds m = 1 and m = 3.
  (3) K03, K05, K08 with the exogenous-message bins and the next bin removed from the transitions (field check).
Writes results/posthoc.json. Labelled post hoc in the card.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h145lib as L  # noqa: E402
import individuality as IND  # noqa: E402
import memeplex as MP  # noqa: E402
import build as B  # noqa: E402

BC = dict(h=10, n_max=200, min_draws=30)


def a_test(P, K, eb, es, rng, m=2, keep_bins=None):
    """Colonial A excess z vs pseudo-patterns, transitions restricted to b0 in keep_bins (bool [nB])."""
    def stat(KK):
        ps = MP.pattern_state(P, KK, m)
        b0 = IND.transitions(P.bins.day_of_bin)
        if keep_bins is not None:
            b0 = b0[keep_bins[b0]]
        (yn, yc), C = IND.compact_states(ps["sym"][b0 + 1], ps["sym"][b0])
        if C < 2 or len(np.unique(P.bins.day_of_bin[b0 + 1])) < 3:
            return np.nan
        cen = L.pattern_centroid(eb, ps["H"])
        Eb = L.pattern_env(eb, P, KK, ps["H"], cen)[b0]
        r = IND.krakauer_logit(yn, IND.onehot(yc, C), Eb, P.bins.day_of_bin[b0 + 1], C, 1.0)
        return r["A"] if r.get("ok") else np.nan
    obs = stat(K)
    pools = L.matched_pool(es, K)
    r = IND.besag_clifford(obs, lambda: stat(L.draw_pseudo(pools, rng)), **BC)
    return {"A": obs, "z": r["z"], "p": r["p"], "n": r["n"]}


def main():
    rng = np.random.default_rng(20261010)
    mem = {k["id"]: k for k in json.loads((L.OUT / "memeplexes.json").read_text())["memeplexes"]}
    P = B.load_panel(120)
    es = L.element_stats(P)
    eb = L.env_base_real(P)
    out = {}
    K = mem["K03"]["elements"]
    dob = P.bins.day_of_bin
    half = dob < 22
    out["K03_first_half"] = a_test(P, K, eb, es, rng, keep_bins=half)
    out["K03_second_half"] = a_test(P, K, eb, es, rng, keep_bins=~half)
    L.log("halves", out["K03_first_half"], out["K03_second_half"])
    for m in (1, 3):
        out[f"K03_m{m}"] = a_test(P, K, eb, es, rng, m=m)
        L.log("m", m, out[f"K03_m{m}"])
    exo = eb.exo_any > 0
    quiet = ~exo
    quiet[1:] &= ~exo[:-1]
    out["quiet_share"] = float(quiet.mean())
    for i in ("K03", "K05", "K08"):
        out[f"{i}_no_exo_bins"] = a_test(P, mem[i]["elements"], eb, es, rng, keep_bins=quiet)
        L.log(i, "no exo", out[f"{i}_no_exo_bins"])
    (L.OUT / "results/posthoc.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
