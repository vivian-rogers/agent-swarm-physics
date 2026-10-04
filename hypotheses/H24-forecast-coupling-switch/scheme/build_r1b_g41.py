"""H24 round 1b, native G41 inputs: the #41 goal field at chunk level (both models, regime-III whitening), so the
field can be removed along every goal-text and kickoff chunk direction. No text is stored.

Output: data/processed/H24-forecast-coupling-switch/G41/r1b/field_<model>.npz (ghat, goal, kickoff, chunks; 64-d)
Usage: UV_OFFLINE=1 HF_HUB_OFFLINE=1 uv run --offline --with sentence-transformers python \
           hypotheses/H24-forecast-coupling-switch/scheme/build_r1b_g41.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h24lib import H24, unit  # noqa: E402
from build_r1b import MODELS, encode, st_model  # noqa: E402
from common import load_holdout  # noqa: E402
import embed_models as EM  # noqa: E402
import goal_fields as GF  # noqa: E402

GOAL, REG = 41, "III"
DEST = H24 / "G41" / "r1b"


def main():
    assert GOAL not in set(load_holdout()["goal_periods_held_out"])
    DEST.mkdir(parents=True, exist_ok=True)
    meta, texts = GF.goal_texts()
    rec = {m["kind"]: tx for m, tx in zip(meta, texts) if m["goal_no"] == GOAL and m["kind"] in ("goal", "kickoff")
           and not m["holdout"]}
    del texts
    gm = pl.read_parquet(EM.ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    info = {}
    for model in MODELS:
        mdl = st_model(model)
        W = EM.load_whitener(REG, 64, model)
        V = EM.goal_vectors(model).astype(np.float32)
        ch = [unit(W(encode(mdl, rec[k]))) for k in ("goal", "kickoff") if rec.get(k)]
        gv = unit(W(V[gm.filter((pl.col("goal_no") == GOAL) & (pl.col("kind") == "goal"))["gid"][0]][None])[0])
        kv = unit(W(V[gm.filter((pl.col("goal_no") == GOAL) & (pl.col("kind") == "kickoff"))["gid"][0]][None])[0])
        np.savez(DEST / f"field_{model}.npz", ghat=unit(gv + kv).astype(np.float32), goal=gv.astype(np.float32),
                 kickoff=kv.astype(np.float32), chunks=np.vstack(ch).astype(np.float32))
        info[model] = int(sum(len(c) for c in ch))
        del mdl
    (DEST / "check.json").write_text(json.dumps({"n_chunks": info}, indent=1))
    print(info)


if __name__ == "__main__":
    main()
