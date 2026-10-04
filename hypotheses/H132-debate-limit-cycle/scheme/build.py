"""H132 scheme: #12 debate turns on the motion's issue axis. Codes and vectors only, no text.

Reads H21's G12 products as data (statements with debate/phase/team; masked embeddings; motion template embeddings),
re-checks teams and phases against DQ6 ground_truth_labels, and whitens with the regime-I whitener of each model.

    uv run python hypotheses/H132-debate-limit-cycle/scheme/build.py
Output (data/processed/H132-debate-limit-cycle/G12/): messages.parquet (debater messages in pre/deb/post phases with
the projection columns per model and source), axes_<model>.npz (issue axis a, topic axis g per debate),
msg_white_<model>_<src>.npy (32-d whitened message vectors), _provenance.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
from embed_models import load_whitener  # noqa: E402

SH = ROOT / "data/processed/shared"
H21 = ROOT / "data/processed/H21-debate-antiferromagnet/G12"
OUT = ROOT / "data/processed/H132-debate-limit-cycle/G12"
MODELS = {"bge_small": ("emb_masked.npy", "motions.npz"), "gte_modernbert": ("emb_masked_gte_modernbert.npy",
                                                                               "motions_gte_modernbert.npz")}


def gt_check(st: pl.DataFrame) -> dict:
    """Teams per debate in H21's statements agree with DQ6 team rows (preferred, non-holdout)."""
    g = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 12) & pl.col("preferred") & ~pl.col("holdout") & (pl.col("label_kind") == "team"))
    res = {"dq6_team_rows": g.height}
    deb = st.filter(pl.col("team").is_in([1, -1]) & pl.col("debate").is_not_null())
    obs = deb.group_by("debate", "agent").agg(pl.col("team").first()).sort("debate", "agent")
    res["h21_agent_debate_teams"] = obs.height
    res["dq6_columns"] = g.columns
    res["dq6_values"] = sorted(set(g["value"].to_list()))
    # unit holds the debate number in DQ6 (string); value = gov/opp
    agree = tot = 0
    for r in g.iter_rows(named=True):
        try:
            d = int(str(r["unit"]).split("_")[-1]) if r["unit"] is not None else None
        except ValueError:
            d = None
        if d is None or r["agent"] is None:
            continue
        o = obs.filter((pl.col("debate") == d) & (pl.col("agent") == r["agent"]))
        if o.height == 0:
            continue
        tot += 1
        v = str(r["value"]).lower()
        want = 1 if v.startswith("gov") else (-1 if v.startswith("opp") else None)
        agree += int(want == o["team"][0])
    res["agree"], res["checked"] = agree, tot
    return res


def main():
    st = pl.read_parquet(H21 / "statements.parquet")
    hm = holdout_mask(st["t"].dt.convert_time_zone("America/Los_Angeles").dt.strftime("%Y-%m-%d").to_list(),
                      [12] * st.height)
    assert not any(hm), "#12 rows in the holdout"
    msgs = (st.filter(pl.col("phase").is_in(["pre", "deb", "post"]) & pl.col("team").is_in([1, -1]))
            .sort("debate", "t"))
    # producing call of each message (ledger visibility of the previous turn, N2)
    pc = pl.read_parquet(SH / "producing_calls.parquet").select("message_id", "t_call_prod", "prod_fallback")
    msgs = msgs.join(pc, on="message_id", how="left")
    # unmasked shared statement rows (variant)
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    stx = (pl.scan_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
           .filter(pl.col("kind") == "chat").select("srow", "src_row").collect().join(ci, on="src_row"))
    msgs = msgs.join(stx.select("message_id", "srow"), on="message_id", how="left")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = msgs["emb_row"].to_numpy()
    for model, (ef, mf) in MODELS.items():
        W = load_whitener("I", 32, model)
        E = np.load(H21 / ef).astype(np.float32)
        Xm = W(E[rows]).astype(np.float32)
        np.save(OUT / f"msg_white_{model}_masked.npy", Xm)
        V = np.load(SH / f"embeddings/statements_white32_{model}.npy", mmap_mode="r")
        sr = msgs["srow"].fill_null(-1).to_numpy()
        Xu = np.full((len(sr), 32), np.nan, np.float32)
        Xu[sr >= 0] = np.asarray(V[sr[sr >= 0]], dtype=np.float32)
        np.save(OUT / f"msg_white_{model}_unmasked.npy", Xu)
        M = np.load(H21 / mf)
        debs, me = M["debates"], M["emb"]
        Wt = W(me.reshape(-1, me.shape[-1])).reshape(me.shape[0], 3, 32)
        a = Wt[:, 1] - Wt[:, 2]
        a /= np.linalg.norm(a, axis=1, keepdims=True)
        g = Wt[:, 0] / np.linalg.norm(Wt[:, 0], axis=1, keepdims=True)
        np.savez(OUT / f"axes_{model}.npz", debates=debs, a=a, g=g)
    msgs.write_parquet(OUT / "messages.parquet", compression="zstd")
    chk = gt_check(st)
    prov = {"built_by": "hypotheses/H132-debate-limit-cycle/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["H21-debate-antiferromagnet/G12 (statements, masked embeddings, motions)",
                                   "ground_truth_labels", "producing_calls", "embeddings/statements",
                                   "embeddings/chat_index", "whitening_I"]}],
            "params": {"phases": ["pre", "deb", "post"], "n_messages": msgs.height, "gt_check": chk},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT.parent / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))
    print(json.dumps({"n": msgs.height, "gt": chk,
                      "unmasked_missing": int(msgs["srow"].null_count()),
                      "no_prod_call": int(msgs["t_call_prod"].null_count())}, indent=1, default=str))


if __name__ == "__main__":
    main()
