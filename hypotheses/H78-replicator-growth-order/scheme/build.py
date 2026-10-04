"""H78 scheme: identical to H77's (shared builder infra/shared/replicator_hosts.py, same parameters).
Writes data/processed/H78-replicator-growth-order/G<NN>/. See hypotheses/H77-repos-as-replicators/scheme/build.py.
Usage: uv run python hypotheses/H78-replicator-growth-order/scheme/build.py [--periods ...] [--allow-holdout]
"""
import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--hyp", "H78"] + sys.argv[1:]
    runpy.run_path(str(Path(__file__).resolve().parents[2] / "H77-repos-as-replicators/scheme/build.py"), run_name="__main__")
