"""Registry and loaders for the shared statement embeddings of more than one model (embedding robustness pack, DQ5).

Models (both fp16, L2-normalized, same inputs: text cut at 2,000 characters, max 256 tokens):
  bge_small       BAAI/bge-small-en-v1.5 (384-d), built by build_embeddings.py / build_agent_vectors.py (the original)
  gte_modernbert  Alibaba-NLP/gte-modernbert-base (768-d, CLS pooling, no prefix), built by build_embeddings_v2.py

Files in data/processed/shared/embeddings/ (all aligned to the existing index tables):
  chat_<model>.npy, intentions_<model>.npy      rows of chat_index.parquet / intentions_index.parquet
  agent_day_vec[_<model>].npy                   rows of agent_day.parquet   (normalized mean raw embedding)
  agent_win30_vec[_<model>].npy                 rows of agent_win30.parquet
  whitening[_<model>]_<regime>.npz              mean, top-128 PCA components, eigenvalues; non-holdout fit per regime
  statements_white32_<model>.npy                rows of statements.parquet: regime-whitened (32-d), unit-normalized
  statements_style_resid32_<model>.npy          same after OLS residualization on 20 style features (style_resid.py)
  statements_style_resid_period32_<model>.npy   same, residualized within goal period (style_resid.py)
  agent_{day,win30}_{white32,style_resid,style_resid_period}_<model>.npy   plain means of the statement-level vectors
                                                per agent_day / agent_win30 row
  goal_vectors[_<model>].npy                    rows of goals.parquet (goal_fields.py texts)
For bge_small the original files keep their names (no model suffix); the helpers below hide the difference.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT  # noqa: E402

ED = OUT / "embeddings"
MODELS = {
    "bge_small": {"hf": "BAAI/bge-small-en-v1.5", "dim": 384, "suffix": "bge_small", "vec_suffix": ""},
    "gte_modernbert": {"hf": "Alibaba-NLP/gte-modernbert-base", "revision": "e7f32e3c00f91d699e8c43b53106206bcc72bb22",
                       "dim": 768, "suffix": "gte_modernbert", "vec_suffix": "_gte_modernbert"},
}
STYLE_DIM = 32


def emb_path(kind: str, model: str) -> Path:
    """kind in {chat, intentions}."""
    return ED / f"{kind}_{MODELS[model]['suffix']}.npy"


def statement_embeddings(model: str, st=None, mmap: bool = True) -> np.ndarray:
    """Raw embeddings (float32) aligned to statements.parquet rows (or to the given statements frame)."""
    import polars as pl
    if st is None:
        st = pl.read_parquet(ED / "statements.parquet", columns=["kind", "src_row"])
    mode = "r" if mmap else None
    Ec = np.load(emb_path("chat", model), mmap_mode=mode)
    Ei = np.load(emb_path("intentions", model), mmap_mode=mode)
    kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy()
    E = np.empty((len(kind), Ec.shape[1]), dtype=np.float32)
    m = kind == "chat"
    E[m] = Ec[src[m]]
    E[~m] = Ei[src[~m]]
    return E


def whitening_path(regime: str, model: str) -> Path:
    return ED / f"whitening{MODELS[model]['vec_suffix']}_{regime}.npz"


def load_whitener(regime: str, dim: int = 32, model: str = "bge_small"):
    """W(x): raw embeddings (n x d_model) -> whitened, centered n x dim coordinates (non-holdout fit per regime).
    For bge_small this is identical to common.load_whitener."""
    z = np.load(whitening_path(regime, model))
    mu, U, w = z["mean"], z["components"][:, :dim], z["eigenvalues"][:dim]

    def W(x):
        return ((np.asarray(x, dtype=np.float32) - mu) @ U) / np.sqrt(w)
    return W


def agent_vectors(level: str, model: str = "bge_small", variant: str = "raw") -> np.ndarray:
    """level in {day, win30}; variant in {raw, white32, style_resid}. Rows follow agent_<level>.parquet.
    raw: normalized mean raw embedding (whiten downstream); white32 / style_resid: plain means of unit-normalized
    32-d regime-whitened statement vectors (already whitened; do not whiten again)."""
    if variant == "raw":
        return np.load(ED / f"agent_{level}_vec{MODELS[model]['vec_suffix']}.npy")
    return np.load(ED / f"agent_{level}_{variant}_{MODELS[model]['suffix']}.npy")


def group_ids(st, level: str) -> tuple[np.ndarray, np.ndarray, int]:
    """Statement -> row of the EXISTING agent_<level>.parquet (level in {day, win30}), recomputed with
    build_agent_vectors' grouping and asserted identical. Returns (statement rows used, group id per used row, n_groups)."""
    import polars as pl
    keys = ["agent", "pt_date"] + (["win30"] if level == "win30" else [])
    idx = np.flatnonzero(st["win30"].is_not_null().to_numpy()) if level == "win30" else np.arange(st.height)
    sub = st[idx] if level == "win30" else st
    grp = (sub.group_by(keys, maintain_order=True)
           .agg((pl.col("kind") == "chat").sum().alias("n_chat"), (pl.col("kind") == "intent").sum().alias("n_intent"))
           .sort(keys).with_row_index("gid"))
    ref = pl.read_parquet(ED / f"agent_{level}.parquet")
    assert grp.select(*keys, "n_chat", "n_intent").equals(ref.select(*keys, "n_chat", "n_intent")), \
        f"agent_{level}: regrouping differs from the existing table"
    gid = sub.join(grp.select(*keys, "gid"), on=keys, how="left", maintain_order="left")["gid"].to_numpy()
    return idx, gid, grp.height


def group_plain_means(X: np.ndarray, gid: np.ndarray, n_groups: int) -> np.ndarray:
    """Plain (unnormalized) group means, float16."""
    order = np.argsort(gid, kind="stable")
    g = gid[order]
    starts = np.r_[0, np.flatnonzero(np.diff(g)) + 1]
    sums = np.add.reduceat(X[order].astype(np.float64), starts, axis=0)
    cnt = np.diff(np.r_[starts, len(g)])
    out = np.zeros((n_groups, X.shape[1]), dtype=np.float64)
    out[g[starts]] = sums / cnt[:, None]
    return out.astype(np.float16)


def goal_vectors(model: str = "bge_small") -> np.ndarray:
    """Rows of goals.parquet (goal_fields.py); raw, mean of unit chunk embeddings. Whiten with load_whitener(..., model)."""
    return np.load(ED / ("goal_vectors.npy" if model == "bge_small" else f"goal_vectors_{MODELS[model]['suffix']}.npy"))


def statement_vectors(model: str = "bge_small", variant: str = "style_resid32") -> np.ndarray:
    """Statement-level 32-d vectors aligned to statements.parquet; variant in {white32, style_resid32}."""
    return np.load(ED / f"statements_{variant}_{MODELS[model]['suffix']}.npy")
