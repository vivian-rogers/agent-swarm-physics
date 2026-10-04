"""H32 round 1b scheme (2026-10-04): second-model and style-residual vectors, row-aligned with messages.parquet.

  uv run python hypotheses/H32-information-current-leaders/scheme/build_r1b.py

Writes data/processed/H32-information-current-leaders/r1b/:
  vec_w64_gte.npy     gte-modernbert embeddings (DQ5) whitened in the period's regime basis (embed_models.load_whitener,
                      64-d, fp16), same construction as round 1's vec_w64.npy
  fields_gte.npz      goal-text and kickoff vectors from goal_vectors_gte_modernbert.npy (same goals.parquet rows)
  vec_style32_bge.npy agent chat and intentions: DQ5 statements_style_resid_period32_bge_small (style removed within goal
                      period); human / automated rows: round 1's whitened bge (first 32 columns)
No text. Holdout: messages.parquet holds non-holdout periods only (asserted at its build); asserted again here.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import embed_models as EM  # noqa: E402
from common import REVISION, git_commit, holdout_mask  # noqa: E402

DATA = ROOT / "data/processed/H32-information-current-leaders"
OUT = DATA / "r1b"
ED = ROOT / "data/processed/shared/embeddings"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m = pl.read_parquet(DATA / "messages.parquet").with_row_index("row")
    assert not any(holdout_mask(m["pt_date"].to_list(), m["goal_no"].to_list()))
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("crow")
    ii = pl.read_parquet(ED / "intentions_index.parquet").with_row_index("irow")
    m = m.join(ci, on="message_id", how="left").join(ii, on="event_index", how="left").sort("row")
    kind = m["kind"].to_numpy()
    crow, irow = m["crow"].to_numpy(), m["irow"].to_numpy()
    assert not np.isnan(crow[kind == 0].astype(float)).any() and not np.isnan(irow[kind == 1].astype(float)).any()
    periods = {p["goal_no"]: p for p in json.loads((DATA / "periods.json").read_text())}
    reg = np.array([periods[int(g)]["regime_basis"] for g in m["goal_no"].to_list()])
    # gte
    Ec = np.load(EM.emb_path("chat", "gte_modernbert"), mmap_mode="r")
    Ei = np.load(EM.emb_path("intentions", "gte_modernbert"), mmap_mode="r")
    V = np.zeros((m.height, 64), np.float32)
    for R in sorted(set(reg)):
        W = EM.load_whitener(R, 64, model="gte_modernbert")
        for k, E, idx in ((0, Ec, crow), (1, Ei, irow)):
            sel = np.flatnonzero((reg == R) & (kind == k))
            if len(sel):
                V[sel] = W(np.asarray(E[idx[sel].astype(np.int64)], np.float32))
    np.save(OUT / "vec_w64_gte.npy", V.astype(np.float16))
    # gte fields: same goals.parquet rows as round 1
    gm = pl.read_parquet(ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    graw = EM.goal_vectors("gte_modernbert").astype(np.float32)
    fz = {}
    for g in periods:
        rows_ = gm.filter((pl.col("goal_no") == g) & pl.col("kind").is_in(["goal_whole", "kickoff_room"]) & ~pl.col("holdout")).sort("gid")
        fz[f"g{g}_raw"] = graw[rows_["gid"].to_numpy()] if rows_.height else np.zeros((0, graw.shape[1]), np.float32)
        fz[f"g{g}_kind"] = np.array([0 if k == "goal_whole" else 1 for k in rows_["kind"].to_list()], np.int8)
        fz[f"g{g}_room"] = rows_["room"].fill_null(-1).to_numpy().astype(np.int16) if rows_.height else np.zeros(0, np.int16)
    np.savez(OUT / "fields_gte.npz", **fz)
    # style-residualized (within goal period), bge
    st = pl.read_parquet(ED / "statements.parquet", columns=["kind", "src_row"]).with_row_index("srow")
    S = np.load(ED / "statements_style_resid_period32_bge_small.npy", mmap_mode="r")
    key = pl.DataFrame({"row": m["row"], "kind": np.where(kind == 0, "chat", "intent"),
                        "src_row": np.where(kind == 0, crow, irow).astype(np.uint32)})
    j = key.join(st, on=["kind", "src_row"], how="left").sort("row")
    srow = j["srow"].to_numpy()
    Vb = np.load(DATA / "vec_w64.npy", mmap_mode="r")
    V2 = np.asarray(Vb[:, :32], np.float32).copy()
    have = ~np.isnan(srow.astype(float))
    V2[have] = np.asarray(S[srow[have].astype(np.int64)], np.float32)
    np.save(OUT / "vec_style32_bge.npy", V2.astype(np.float16))
    spk = m["spk"].to_numpy()
    info = {"rows": m.height, "style_rows_from_statements": int(have.sum()), "agent_rows": int((spk < 100).sum()),
            "agent_rows_without_statement": int(((spk < 100) & ~have).sum())}
    print(info)
    pp = OUT / "_provenance.json"
    old = json.loads(pp.read_text()) if pp.exists() else {}
    old["vectors"] = {"built_by": "hypotheses/H32-information-current-leaders/scheme/build_r1b.py", "git_commit": git_commit(),
                      "inputs": [{"source": "ai-village", "revision": REVISION,
                                  "tables": ["H32 messages.parquet + vec_w64.npy", "shared/embeddings chat/intentions_gte_modernbert",
                                             "whitening_gte_modernbert_<regime>", "goal_vectors_gte_modernbert", "statements.parquet",
                                             "statements_style_resid_period32_bge_small"]}],
                      "params": info, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    pp.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
