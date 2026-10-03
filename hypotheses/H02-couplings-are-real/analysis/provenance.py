"""Record provenance for every H02 output in data/processed/H02-couplings-are-real/_provenance.json."""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit  # noqa: E402

DATA = ROOT / "data/processed/H02-couplings-are-real"
A = "hypotheses/H02-couplings-are-real/analysis/"
SP = "data/processed/H02-couplings-are-real/spins.parquet"
SH = "data/processed/shared/"
ENTRIES = {
    "calibration.json": (A + "calibrate.py", [SP], {"model": "M1 (block fields + self)", "regimes": ["I", "III"]}),
    "harness_A.parquet": (A + "harness.py A", ["calibration.json"], {"N": 18, "Td": 241, "D": [1, 2, 3, 5, 10, 20], "JL": [0.1, 0.2, 0.3, 0.5], "KL": 5, "rho": 0.15, "reps": 40}),
    "harness_A_true.parquet": (A + "harness.py Atrue", ["calibration.json"], {"note": "true net-influence rank of the planted leader, same seeds as A"}),
    "harness_B.parquet": (A + "harness.py B", ["calibration.json"], {"truth": "5-min boxcar delay", "D": [5, 20], "JL": [0.3, 0.5], "reps": 40}),
    "harness_B2.parquet": (A + "harness.py B2", ["calibration.json"], {"truth": "lag-1", "fit": ["KI-1", "KI-5"], "reps": 40}),
    "harness_C.parquet": (A + "harness.py C", ["calibration.json"], {"D": 5, "surrogates": 100, "reps": 30}),
    "real_chunks.parquet": (A + "nulls_real.py 100", [SP, SH + "roster.parquet"], {"spin": "active", "surrogates": 100}),
    "real_couplings.parquet": (A + "nulls_real.py 100", [SP, SH + "roster.parquet"], {"spin": "active"}),
    "real_influence.parquet": (A + "nulls_real.py 100", [SP], {"spin": "active"}),
    "real_chunks_talk.parquet": (A + "nulls_real.py 100 talk", [SP, SH + "roster.parquet"], {"spin": "talk (post hoc)", "min_talk_bins": 30}),
    "real_couplings_talk.parquet": (A + "nulls_real.py 100 talk", [SP], {"spin": "talk (post hoc)"}),
    "real_influence_talk.parquet": (A + "nulls_real.py 100 talk", [SP], {"spin": "talk (post hoc)"}),
    "heldout_null.parquet": (A + "heldout_null.py 20 active", [SP, SH + "roster.parquet"], {"block_min": 30, "surrogates": 20}),
    "heldout_null_talk.parquet": (A + "heldout_null.py 20 talk", [SP, SH + "roster.parquet"], {"block_min": 30, "surrogates": 20}),
    "heldout_null_b10_rIII.parquet": (A + "heldout_null.py 20 active 10 III", [SP, SH + "roster.parquet"], {"block_min": 10, "regime": "III"}),
    "validate_heldout.parquet": (A + "validate_heldout.py", ["calibration.json"], {"N": 15, "D": 5, "reps": 10}),
    "scheduler_audit.parquet": (A + "scheduler_audit.py", [SP, SH + "events_core.parquet", SH + "actions.parquet", SH + "calendar.parquet"], {"shifts": 20}),
    "binwidth.parquet": (A + "binwidth.py", [SP, "real_couplings.parquet"], {"bin": "2 min", "surrogates": 50}),
    "mf_cw.parquet": (A + "mf.py 100 50", [SP], {"model": "Curie-Weiss inversion within 30-min blocks (HH80)", "cw_surrogates": 100}),
    "mf_pk.parquet": (A + "mf.py 100 50", [SP], {"model": "forward P(K): Poisson-binomial and CW tilt per block"}),
    "mf_lf.parquet": (A + "mf.py 100 50", [SP], {"model": "leader-follower mean field (HH83), M1 offsets", "lf_surrogates": 50}),
    "mf_cw_nolull.parquet": (A + "mf.py nolull", [SP, "mf_cw.parquet"], {"cw_surrogates": 50, "filter": "K > 1"}),
    "results_summary.json": (A + "summarize.py", ["all of the above"], {}),
    "dryrun_g26.json": (A + "confirm_45.py --dry-run-goal 26 --leader 17", [SH + "activity_bins.parquet", SH + "calendar.parquet", SH + "roster.parquet"], {"surrogates": 200}),
}


def main():
    path = DATA / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    for f, (by, inputs, params) in ENTRIES.items():
        if not (DATA / f).exists():
            continue
        prov[f] = {"built_by": by, "git_commit": git_commit(),
                   "inputs": [{"source": "ai-village", "revision": REVISION, "tables": inputs}],
                   "params": params | {"holdout": "excluded (non-holdout chunks only)"}, "built_at": now}
    missing = sorted(p.name for p in DATA.iterdir() if p.name not in prov and p.name != "_provenance.json" and p.stem != "spins")
    path.write_text(json.dumps(prov, indent=1))
    print("entries", len(prov), "unrecorded files:", missing)


if __name__ == "__main__":
    main()
