"""Correction 2026-10-04: recompute round 1's room-field robustness variant for #38 with the corrected kickoffs.

H01's goals_raw.npy had the #38 room-2 / room-3 kickoff vectors swapped. The only round-1 statistic that used per-room
kickoffs is `within_minus_cross_roomfield_removed` (P6's room criterion with each room's own g-hat_r added to the
field subspace before the residual is taken). This script recomputes, for 38a/38b/38c and with the same rarefied
draws for both versions: the within-minus-cross residual (no room field), the room-field-removed value with the
swapped (old) vectors and with the corrected (shared-table) vectors. Five rarefaction draws, d = 32, first-day h_i
(the round-1 primary). Writes data/processed/H01-emergent-superagents-exist/round2/fix_r1_room_kickoff.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.argv = [sys.argv[0]]  # explore.py parses argv at import
sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib  # noqa: E402,F401  (thread caps)
from h01data import Scheme  # noqa: E402
from h01lib import pair_table, rarefied_vectors  # noqa: E402
from h01common import OUT, SEED  # noqa: E402

import numpy as np  # noqa: E402


def wc(p):
    pk = p["i"] * 1000 + p["j"]
    pairs = np.unique(pk)
    pm = np.array([p["r"][pk == q].mean() for q in pairs])
    ps = np.array([p["same"][pk == q].mean() > 0.5 for q in pairs])
    return float(pm[ps].mean() - pm[~ps].mean())


def main():
    S_new = Scheme(d=32)
    S_old = Scheme(d=32, shared_room_kickoffs=False)
    old_json = json.loads((OUT / "explore.json").read_text())["p56"]["P6"]["two_room"]
    out = {"note": __doc__.split("\n")[0], "source_new": S_new.room_kickoff_source, "units": {}}
    for name in ("38a", "38b", "38c"):
        un, uo = S_new.unit(name), S_old.unit(name)
        gr_n, gr_o = un.ghat_room, uo.ghat_room
        rec = {"cos_room2_old_vs_new": float(gr_o[2] @ gr_n[2]), "cos_room3_old_vs_new": float(gr_o[3] @ gr_n[3]),
               "cos_room2_old_vs_room3_new": float(gr_o[2] @ gr_n[3]), "draws": []}
        rng = np.random.default_rng(SEED + 404)
        for _ in range(5):
            Vr = rarefied_vectors(un, 8, 10, rng)
            base = wc(pair_table(un, n_min=8, Vover=Vr))
            new = wc(pair_table(un, n_min=8, Vover=Vr, use_room=True))
            old = wc(pair_table(uo, n_min=8, Vover=Vr, use_room=True))
            rec["draws"].append({"within_minus_cross": base, "roomfield_removed_swapped": old, "roomfield_removed_corrected": new})
        for k in ("within_minus_cross", "roomfield_removed_swapped", "roomfield_removed_corrected"):
            rec[k + "_mean"] = float(np.mean([d[k] for d in rec["draws"]]))
        rec["round1_reported"] = {"within_minus_cross": old_json[name]["within_minus_cross"],
                                  "roomfield_removed": old_json[name]["roomfield_removed"]}
        out["units"][name] = rec
        print(name, {k: round(v, 4) for k, v in rec.items() if isinstance(v, float)}, rec["round1_reported"], flush=True)
    dst = OUT / "round2"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "fix_r1_room_kickoff.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
