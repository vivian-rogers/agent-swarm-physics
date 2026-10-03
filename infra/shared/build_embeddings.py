"""Phase 2: sentence embeddings of chat messages and self-written intentions, locally (Apple MPS).

Model: BAAI/bge-small-en-v1.5 (384-d), float16, L2-normalized. Raw embeddings (not whitened);
whiten/center downstream per analysis (embedding anisotropy, see physics-models/11).
Outputs: data/processed/shared/embeddings/{chat,intentions}_bge_small.npy + *_index.parquet

Usage: uv run --with sentence-transformers python infra/shared/build_embeddings.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, write_provenance

MODEL = "BAAI/bge-small-en-v1.5"


def main():
    import torch
    from sentence_transformers import SentenceTransformer
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    m = SentenceTransformer(MODEL, device=dev)
    m.max_seq_length = 256
    ed = OUT / "embeddings"; ed.mkdir(exist_ok=True)
    jobs = {
        "chat": pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"]).rename({"text": "s"}),
        "intentions": pl.read_parquet(OUT / "intentions_text.parquet", columns=["event_index", "goal_text"])
                        .rename({"goal_text": "s"}).drop_nulls("s"),
    }
    for name, df in jobs.items():
        t0 = time.time()
        texts = [s[:2000] for s in df["s"].to_list()]
        order = np.argsort([len(s) for s in texts])  # length-sorted batches are much faster
        emb = np.zeros((len(texts), m.get_embedding_dimension()), dtype=np.float16)
        bs = 256
        for i in range(0, len(order), bs):
            idx = order[i:i + bs]
            e = m.encode([texts[j] for j in idx], batch_size=bs, normalize_embeddings=True, convert_to_numpy=True)
            emb[idx] = e.astype(np.float16)
            if i % (bs * 100) == 0:
                print(name, i, len(order), f"{time.time()-t0:.0f}s", flush=True)
        np.save(ed / f"{name}_bge_small.npy", emb)
        df.drop("s").write_parquet(ed / f"{name}_index.parquet", compression="zstd")
        print(name, emb.shape, f"{time.time()-t0:.0f}s", flush=True)
    write_provenance("build_embeddings", ["chat_text", "intentions_text"], {"model": MODEL, "device": dev, "max_seq_length": 256,
                                                                          "dtype": "float16", "normalized": True})


if __name__ == "__main__":
    main()
