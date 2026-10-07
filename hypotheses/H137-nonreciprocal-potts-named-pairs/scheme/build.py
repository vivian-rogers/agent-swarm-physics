"""H137 scheme entry point. The scheme is built from shared tables only (infra/shared/project_calls.py labels, DQ1
ledger, chat_core, chat_mentions_clean, period_units, roster) by analysis/h137lib.py:
  1. analysis/structure.py  -> results/structure.parquet (structural counts, no follow direction)
  2. analysis/run.py        -> follows.parquet, pairs.parquet, results/round1.json, results/units.parquet, _provenance.json
This wrapper runs step 1. Usage: uv run python hypotheses/H137-nonreciprocal-potts-named-pairs/scheme/build.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import structure  # noqa: E402

if __name__ == "__main__":
    structure.main()
