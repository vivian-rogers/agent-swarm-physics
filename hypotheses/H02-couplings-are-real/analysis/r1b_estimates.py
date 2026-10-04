"""H02 round 1b: per-period estimates into the shared table (infra/shared/estimates.py: write_estimates).
Rows: Curie-Weiss beta*J0 and the KI-1 significant-coupling fraction per 5-day chunk under the DQ8 corrected null
(replication), plus the period-native tests (#12 relation couplings, 44b leader). Supersedes the backfilled round-1
rows (buggy activity_bins); those are left for the coordinator to retire.
Usage: uv run python hypotheses/H02-couplings-are-real/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H02-couplings-are-real/r1b"
NOTE = "round 1b (2026-10-04): activity_bins_fixed; supersedes the backfilled round-1 row (buggy activity_bins)"


def main():
    sp = pl.read_parquet(D / "spins.parquet").group_by("chunk").agg(pl.col("pt_date").min().alias("d0"), pl.col("pt_date").max().alias("d1"))
    c = pl.read_parquet(D / "chunks_1b.parquet").join(sp, on="chunk")
    rows = []
    for r in c.iter_rows(named=True):
        unit = E.map_unit(r["goal_no"], r["d0"], r["d1"]) or f"local:{r['chunk']}"
        base = {"period_unit": unit, "goal_no": r["goal_no"], "channel": "activity", "n": r["N__r1b_trim_stall"], "n_kind": "agents",
                "role": "replication", "unit_local": r["chunk"], "first_day": r["d0"], "last_day": r["d1"], "status": "ok",
                "ci_kind": "none", "source": str((D / "trim_stall/mf_cw.parquet").relative_to(ROOT))}
        rows.append({**base, "statistic": "cw_beta_J0", "estimate": r["bJ0__r1b_trim_stall"],
                     "method": "Curie-Weiss inversion in (day, 30-min block), activity_bins_fixed, all-present window and explained joint silences removed (DQ8 trim_stall)",
                     "null": "N1 block shift drawn after the masks (100 surrogates)",
                     "notes": f"{NOTE}; z = {r['z__r1b_trim_stall']:.2f}; whole-grid beta*J0 {r['bJ0__r1b']:.3f} (z {r['z__r1b']:.2f}); kept share {r['kept_share']:.2f}"})
        rows.append({**base, "statistic": "ki1_frac_sig", "estimate": r["block_N1_frac_sig__r1b_trim_stall"],
                     "source": str((D / "trim_stall/real_chunks.parquet").relative_to(ROOT)),
                     "method": "fraction of directed KI-1 (block fields) couplings with |z| > 1.96, DQ8 trim_stall grid",
                     "null": "N1 block shift after the masks (100 surrogates); calibrated false-positive rate 5.8-7.6%", "notes": NOTE})
    g12 = json.loads((D / "native_g12.json").read_text())["talk"]
    rows.append({"period_unit": "12a", "goal_no": 12, "statistic": "relation_coupling_opp_minus_same", "channel": "talk",
                 "estimate": g12["d_opp_minus_same"], "n": g12["debate_minutes"], "n_kind": "debate-minutes", "role": "native",
                 "method": "relation-structured kinetic Ising on 1-min talk spins in the 10 debate windows (J_opp - J_same)",
                 "null": "team labels re-drafted within debates (500 permutations)", "ci_kind": "none", "status": "ok",
                 "source": str((D / "native_g12.json").relative_to(ROOT)),
                 "notes": f"{NOTE}; permutation z = {g12['z_d']:.2f}; judge coupling z = {g12['z_judge']:.2f}"})
    g44 = json.loads((D / "native_g44.json").read_text())["best|active|none"]
    rows.append({"period_unit": "44b", "goal_no": 44, "statistic": "leader_net_influence_z", "channel": "activity",
                 "estimate": g44["leader_z"], "n": g44["N"], "n_kind": "agents", "role": "native",
                 "method": "KI-1 + block fields within #best, net outgoing influence of the temporary fine-tuned leader (agent 28)",
                 "null": "N1 block shift (200 surrogates)", "ci_kind": "none", "status": "ok",
                 "source": str((D / "native_g44.json").relative_to(ROOT)),
                 "notes": f"{NOTE}; leader rank {g44['leader_rank']}/{g44['N']}; rule (rank 1, z >= 2) fails"})
    out = E.write_estimates(rows, hypothesis="H02")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
