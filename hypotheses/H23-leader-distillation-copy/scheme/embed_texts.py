"""H23 scheme step 3: bge-small-en-v1.5 embeddings of the recovered corpus (targets and scenario snippets) and of the
sibling checkpoints' offline outputs, with the settings of infra/shared/build_embeddings.py (normalized, max_seq 256,
text[:2000]). CPU, 2 threads, offline.

Usage: HF_HUB_OFFLINE=1 uv run --offline --with sentence-transformers python \
           hypotheses/H23-leader-distillation-copy/scheme/embed_texts.py
Output: data/processed/H23-leader-distillation-copy/G44/corpus_emb.npz  (target, snippet, offline arrays + row keys)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
G44 = ROOT / "data/processed/H23-leader-distillation-copy/G44"


def main():
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(2)
    m = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
    m.max_seq_length = 256
    C = pl.read_parquet(G44 / "corpus_text.parquet")
    V = pl.read_parquet(G44 / "corpus_rows_text.parquet")
    # offline outputs of sibling Kimi checkpoints (eval files with leader_response / holdout responses)
    off = (V.filter(pl.col("response").is_not_null() & pl.col("id").str.contains("holdout|resample")
                    & ~pl.col("response").str.contains("TODO"))
           .unique(["id", "response"], keep="first"))
    enc = lambda xs: m.encode([s[:2000] for s in xs], batch_size=64, normalize_embeddings=True,
                              convert_to_numpy=True).astype(np.float32)
    np.savez_compressed(G44 / "corpus_emb.npz",
                        target=enc(C["response"].to_list()), snippet=enc(C["chat_snippet"].to_list()),
                        offline=enc(off["response"].to_list()),
                        offline_snippet=enc(off["chat_snippet"].fill_null("").to_list()),
                        offline_file=np.array(off["file"].fill_null("?").to_list()),
                        offline_id=np.array(off["id"].to_list()))
    off.write_parquet(G44 / "offline_text.parquet", compression="zstd")
    print("embedded", C.height, "corpus rows;", off.height, "offline outputs")


if __name__ == "__main__":
    main()
