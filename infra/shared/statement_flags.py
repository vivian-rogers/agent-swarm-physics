"""DQ5: per-statement quality flags, computed with both embedding models (bge_small, gte_modernbert).

Rows: embeddings/statements.parquet (agent chat + intentions), same order; join on `srow` (= statements row index) or
on (kind, src_row). Comparisons are always within the same kind (chat with chat, intention with intention).
Columns (numbers and booleans only; no text, no text hashes):
  srow, kind, src_row, n_chars, n_words           full-text length (characters; \\b\\w+\\b words)
  n_tok_bge, n_tok_gte                            tokens under each model's tokenizer (no special tokens); both
                                                  models embed only the first 256 tokens (and 2,000 characters)
  exact_self_repeat                               identical normalized text (lower case, collapsed whitespace) to an
                                                  earlier statement of the same agent, same PT day
  exact_cross_echo                                identical normalized text to another agent's statement in [t-2h, t)
  per model m in {bge, gte}:
    self_repeat_cos_m   max cosine to the same agent's earlier statements that PT day (null for the first)
    self_repeat_m       self_repeat_cos_m > thr_m
    cross_echo_cos_m    max cosine to another agent's statements in [t - 2 h, t) (any room; null if none)
    cross_echo_src_m    srow of that best match (null if none)
    cross_echo_m        cross_echo_cos_m > thr_m
    n_dup_agents_m      distinct OTHER agents with a statement at cosine > thr_m anywhere in the same goal period
    templated_m         n_dup_agents_m >= 2 (the near-identical form is used by >= 3 agents in the period)
  self_repeat_src_m   srow of the best earlier same-agent match (null for the first statement of the agent-day)
  self_repeat, cross_echo, templated              the primary flags: the bge versions (H12's rule, continuity)
  self_repeat_both, cross_echo_both, templated_both   both models flag (high precision: surface near-copies)
surface_overlap in the meta JSON: a model-free check (character 5-gram Jaccard with the matched statement, computed in
memory) by agreement category.
Thresholds: thr_bge = 0.95 (H12). gte cosines run lower (different similarity scale), so thr_gte is rate-matched: the
value at which gte's self_repeat rate on NON-HOLDOUT statements equals bge's at 0.95 (written to
statement_flags_meta.json, with agreement at gte 0.95 as well).

Outputs: data/processed/shared/statement_flags.parquet, statement_flags_meta.json (thresholds, agreement),
         statement_flags_by_period.parquet (rates per goal period x kind, non-holdout statements only).
Usage: uv run --with sentence-transformers python infra/shared/statement_flags.py   (tokenizers come from that env)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, write_provenance  # noqa: E402
from embed_models import ED, MODELS, statement_embeddings  # noqa: E402

THR_BGE = 0.95
WINDOW_US = 2 * 3600 * 1_000_000
TEMPLATE_MIN_OTHER_AGENTS = 2
SHORT = {"bge_small": "bge", "gte_modernbert": "gte"}


def load_texts(st: pl.DataFrame) -> list[str]:
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("src_row")
    ct = ci.join(pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"]), on="message_id",
                 how="left", maintain_order="left").drop("message_id")
    ii = pl.read_parquet(ED / "intentions_index.parquet").with_row_index("src_row")
    it = ii.join(pl.read_parquet(OUT / "intentions_text.parquet", columns=["event_index", "goal_text"])
                 .rename({"goal_text": "text"}), on="event_index", how="left", maintain_order="left").drop("event_index")
    key = st.select(pl.int_range(pl.len()).alias("srow"), "kind", "src_row")
    a = key.filter(pl.col("kind") == "chat").join(ct, on="src_row", how="left", maintain_order="left")
    b = key.filter(pl.col("kind") == "intent").join(it, on="src_row", how="left", maintain_order="left")
    T = pl.concat([a, b]).sort("srow")
    assert T.height == st.height and T["text"].null_count() == 0
    return T["text"].to_list()


def token_counts(texts: list[str]) -> dict[str, np.ndarray]:
    from huggingface_hub import hf_hub_download
    from tokenizers import Tokenizer
    out = {}
    for model, short in SHORT.items():
        spec = MODELS[model]
        tk = Tokenizer.from_file(hf_hub_download(spec["hf"], "tokenizer.json", revision=spec.get("revision"),
                                                 local_files_only=True))
        tk.no_truncation(); tk.no_padding()
        n = np.empty(len(texts), dtype=np.int32)
        for i in range(0, len(texts), 20000):
            enc = tk.encode_batch(texts[i:i + 20000], add_special_tokens=False)
            n[i:i + 20000] = [len(e.ids) for e in enc]
        out[f"n_tok_{short}"] = np.minimum(n, 32767).astype(np.int16)
    return out


def self_and_echo(E: np.ndarray, st: pl.DataFrame, keys: np.ndarray | None):
    """Max cosine to the same agent's earlier same-kind statements that day, and to other agents' same-kind
    statements in [t - 2h, t). keys (normalized-text ids) also give the exact-duplicate versions."""
    n = st.height
    sr = np.full(n, np.nan, dtype=np.float32)
    ssrc = np.full(n, -1, dtype=np.int64)
    ce = np.full(n, np.nan, dtype=np.float32)
    src = np.full(n, -1, dtype=np.int64)
    ex_s = np.zeros(n, dtype=bool); ex_c = np.zeros(n, dtype=bool)
    groups = (st.with_row_index("srow").group_by("agent", "pt_date", "kind").agg(pl.col("srow")))["srow"].to_list()
    for g in groups:
        idx = np.sort(np.asarray(g))
        if len(idx) < 2:
            continue
        S = E[idx] @ E[idx].T
        S[np.triu_indices(len(idx))] = -np.inf
        sr[idx[1:]] = S[1:].max(1)
        ssrc[idx[1:]] = idx[S[1:].argmax(1)]
        if keys is not None:
            K = keys[idx][:, None] == keys[idx][None, :]
            ex_s[idx] = np.tril(K, -1).any(1)
    t = st["t"].dt.epoch("us").to_numpy(); ag = st["agent"].to_numpy(); kind = st["kind"].to_numpy()
    day = st["pt_date"].to_numpy()
    for k in np.unique(kind):
        rows = np.flatnonzero(kind == k)  # t-sorted (statements are sorted by t)
        tk = t[rows]
        for d in np.unique(day[rows]):
            tgt = rows[day[rows] == d]
            lo = np.searchsorted(tk, t[tgt].min() - WINDOW_US, "left")
            hi = np.searchsorted(tk, t[tgt].max(), "left")
            cand = rows[lo:hi]
            if len(cand) == 0:
                continue
            M = (t[cand][None, :] < t[tgt][:, None]) & (t[cand][None, :] >= t[tgt][:, None] - WINDOW_US) \
                & (ag[cand][None, :] != ag[tgt][:, None])
            S = E[tgt] @ E[cand].T
            S[~M] = -np.inf
            j = S.argmax(1)
            best = S[np.arange(len(tgt)), j]
            ok = np.isfinite(best)
            ce[tgt[ok]] = best[ok]; src[tgt[ok]] = cand[j[ok]]
            if keys is not None:
                ex_c[tgt] = ((keys[tgt][:, None] == keys[cand][None, :]) & M).any(1)
    return sr, ssrc, ce, src, ex_s, ex_c


def dup_agents(E: np.ndarray, st: pl.DataFrame, thr: float, block: int = 1024) -> np.ndarray:
    """Distinct other agents with a same-kind statement at cosine > thr in the same goal period."""
    out = np.zeros(st.height, dtype=np.int16)
    goal = st["goal_no"].to_numpy(); kind = st["kind"].to_numpy(); ag = st["agent"].to_numpy().astype(np.int64)
    for k in np.unique(kind):
        for g in np.unique(goal[kind == k]):
            idx = np.flatnonzero((kind == k) & (goal == g))
            V = E[idx]
            codes, a = np.unique(ag[idx], return_inverse=True)
            A = np.zeros((len(idx), len(codes)), dtype=np.float32)
            A[np.arange(len(idx)), a] = 1
            for b0 in range(0, len(idx), block):
                b = slice(b0, b0 + block)
                C = ((V[b] @ V.T) > thr).astype(np.float32) @ A
                C[np.arange(C.shape[0]), a[b]] = 0  # own agent (incl. the statement itself)
                out[idx[b]] = (C > 0).sum(1)
    return out


def _shingles(s: str, k: int = 5) -> set:
    s = " ".join(s.lower().split())
    return {s[i:i + k] for i in range(max(1, len(s) - k + 1))}


def surface_overlap(df: pl.DataFrame, hold: np.ndarray, texts: list[str], n_sample: int = 3000) -> dict:
    """Model-free check of the flags: median character 5-gram Jaccard between a statement and its best-matching
    statement (bge match; gte match for gte-only flags), by agreement category, on a sample of non-holdout rows."""
    out = {}
    x = df.filter(pl.Series(~hold))
    for f in ("self_repeat", "cross_echo"):
        cat = (pl.when(pl.col(f"{f}_bge") & pl.col(f"{f}_gte")).then(pl.lit("both"))
               .when(pl.col(f"{f}_bge")).then(pl.lit("bge_only"))
               .when(pl.col(f"{f}_gte")).then(pl.lit("gte_only")).otherwise(pl.lit("neither")))
        y = x.with_columns(cat.alias("cat"), pl.when(pl.col(f"{f}_gte") & ~pl.col(f"{f}_bge"))
                           .then(pl.col(f"{f}_src_gte")).otherwise(pl.col(f"{f}_src_bge")).alias("match")) \
             .drop_nulls("match")
        for (c, kd), sub in sorted(y.group_by("cat", "kind"), key=lambda z: z[0]):
            smp = sub.sample(min(n_sample, sub.height), seed=1)
            j = np.array([len(_shingles(texts[a]) & _shingles(texts[b])) / max(1, len(_shingles(texts[a]) | _shingles(texts[b])))
                          for a, b in zip(smp["srow"].to_list(), smp["match"].to_list())])
            out[f"{f}/{kd}/{c}"] = {"n": sub.height, "jaccard5_median": float(np.median(j)),
                                    "share_jaccard5_gt_0.5": float((j > 0.5).mean())}
    return out


def kappa(a: np.ndarray, b: np.ndarray) -> dict:
    a = a.astype(bool); b = b.astype(bool)
    po = (a == b).mean(); pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    union = (a | b).sum()
    return {"rate_bge": float(pa), "rate_gte": float(pb), "kappa": float((po - pe) / (1 - pe)) if pe < 1 else np.nan,
            "jaccard": float((a & b).sum() / union) if union else np.nan}


def main():
    t0 = time.time()
    st = pl.read_parquet(ED / "statements.parquet")
    assert st["t"].is_sorted()
    texts = load_texts(st)
    norm = pl.Series(texts).str.to_lowercase().str.replace_all(r"\s+", " ").str.strip_chars()
    keys = norm.hash(seed=0).to_numpy()  # in memory only
    del norm
    cols = {"srow": np.arange(st.height, dtype=np.uint32), "kind": st["kind"], "src_row": st["src_row"],
            "n_chars": pl.Series(texts).str.len_chars().cast(pl.Int32),
            "n_words": pl.Series(texts).str.count_matches(r"\b\w+\b").cast(pl.Int32)}
    cols.update(token_counts(texts))
    print(f"texts and token counts {time.time() - t0:.0f}s", flush=True)
    res, emb = {}, {}
    for model, short in SHORT.items():
        E = statement_embeddings(model, st, mmap=False)
        E /= np.linalg.norm(E, axis=1, keepdims=True)
        sr, ssrc, ce, src, ex_s, ex_c = self_and_echo(E, st, keys if model == "bge_small" else None)
        res[short] = (sr, ssrc, ce, src)
        if model == "bge_small":
            cols["exact_self_repeat"] = ex_s; cols["exact_cross_echo"] = ex_c
        emb[short] = E
        print(f"{model}: self/echo {time.time() - t0:.0f}s", flush=True)
    hold = st["holdout"].to_numpy()
    # rate-matched gte threshold (non-holdout statements)
    rate = np.nanmean(np.where(np.isnan(res["bge"][0][~hold]), 0, res["bge"][0][~hold] > THR_BGE))
    v = np.nan_to_num(res["gte"][0][~hold], nan=-1.0)
    thr_gte = float(np.quantile(v, 1 - rate))
    thr = {"bge": THR_BGE, "gte": thr_gte}
    print(f"self-repeat rate (bge @ {THR_BGE}) {rate:.4f}; rate-matched gte threshold {thr_gte:.4f}", flush=True)
    for short in ("bge", "gte"):
        sr, ssrc, ce, src = res[short]
        cols[f"self_repeat_cos_{short}"] = pl.Series(sr).fill_nan(None)
        cols[f"self_repeat_src_{short}"] = pl.Series(ssrc.astype(np.int32)).replace(-1, None)
        cols[f"self_repeat_{short}"] = np.nan_to_num(sr, nan=-1) > thr[short]
        cols[f"cross_echo_cos_{short}"] = pl.Series(ce).fill_nan(None)
        cols[f"cross_echo_src_{short}"] = pl.Series(src.astype(np.int32)).replace(-1, None)
        cols[f"cross_echo_{short}"] = np.nan_to_num(ce, nan=-1) > thr[short]
        nd = dup_agents(emb[short], st, thr[short])
        cols[f"n_dup_agents_{short}"] = np.minimum(nd, 127).astype(np.int8)
        cols[f"templated_{short}"] = nd >= TEMPLATE_MIN_OTHER_AGENTS
        print(f"{short}: templated {time.time() - t0:.0f}s", flush=True)
    del emb
    df = pl.DataFrame(cols).with_columns(
        pl.col("self_repeat_bge").alias("self_repeat"), pl.col("cross_echo_bge").alias("cross_echo"),
        pl.col("templated_bge").alias("templated"),
        *[(pl.col(f"{f}_bge") & pl.col(f"{f}_gte")).alias(f"{f}_both") for f in ("self_repeat", "cross_echo", "templated")])
    for c in ("self_repeat_cos_bge", "self_repeat_cos_gte", "cross_echo_cos_bge", "cross_echo_cos_gte"):
        df = df.with_columns(pl.col(c).cast(pl.Float32))
    df.write_parquet(OUT / "statement_flags.parquet", compression="zstd")

    # agreement and per-period rates (non-holdout only)
    nh = df.filter(pl.Series(~hold))
    meta = {"thr_bge": THR_BGE, "thr_gte_rate_matched": thr_gte, "window_h": 2,
            "template_min_other_agents": TEMPLATE_MIN_OTHER_AGENTS, "n_nonholdout": nh.height, "agreement": {}}
    for kind in ("chat", "intent", "all"):
        x = nh if kind == "all" else nh.filter(pl.col("kind") == kind)
        ag = {}
        for f in ("self_repeat", "cross_echo", "templated"):
            ag[f] = kappa(x[f"{f}_bge"].to_numpy(), x[f"{f}_gte"].to_numpy())
        for f in ("self_repeat", "cross_echo"):
            b = x[f"{f}_cos_bge"].fill_null(-1).to_numpy() > THR_BGE
            g95 = x[f"{f}_cos_gte"].fill_null(-1).to_numpy() > 0.95
            ag[f + "@gte0.95"] = kappa(b, g95)
            from scipy.stats import spearmanr
            both = x.select(f"{f}_cos_bge", f"{f}_cos_gte").drop_nulls()
            ag[f + "_cos_spearman"] = float(spearmanr(both[:, 0], both[:, 1]).statistic)
        ex = {"self_repeat": "exact_self_repeat", "cross_echo": "exact_cross_echo"}
        for f, e in ex.items():
            em = x[e].to_numpy()
            ag[f + "_exact"] = {"exact_rate": float(em.mean()),
                                "recall_bge": float(x[f"{f}_bge"].to_numpy()[em].mean()) if em.any() else None,
                                "recall_gte": float(x[f"{f}_gte"].to_numpy()[em].mean()) if em.any() else None,
                                "exact_share_of_bge_flags": float(em[x[f"{f}_bge"].to_numpy()].mean()),
                                "exact_share_of_gte_flags": float(em[x[f"{f}_gte"].to_numpy()].mean())}
        meta["agreement"][kind] = ag
    meta["surface_overlap"] = surface_overlap(df, hold, texts)
    del texts
    gp = (st.select("goal_no", "regime", "holdout").hstack(df).filter(~pl.col("holdout"))
          .group_by("goal_no", "kind")
          .agg(pl.len().alias("n"), pl.col("n_chars").median().alias("median_chars"),
               *[pl.col(f"{f}_{m}").mean().alias(f"{f}_{m}") for f in ("self_repeat", "cross_echo", "templated")
                 for m in ("bge", "gte")],
               pl.col("exact_self_repeat").mean(), pl.col("exact_cross_echo").mean(),
               (pl.col("n_tok_bge") > 256).mean().alias("trunc_bge"), (pl.col("n_tok_gte") > 256).mean().alias("trunc_gte"))
          .sort("goal_no", "kind"))
    gp.write_parquet(OUT / "statement_flags_by_period.parquet", compression="zstd")
    (OUT / "statement_flags_meta.json").write_text(json.dumps(meta, indent=1, default=float))
    write_provenance("statement_flags", ["embeddings/statements", "embeddings/{chat,intentions}_<model>.npy",
                                         "chat_text, intentions_text (lengths, token counts, exact-match keys in memory)"],
                     {"thr_bge": THR_BGE, "thr_gte": thr_gte, "thr_gte_rule": "rate-matched to bge self_repeat on non-holdout",
                      "self_repeat": "same agent, same PT day, same kind, earlier", "cross_echo": "other agent, same kind, [t-2h, t), any room",
                      "templated": f"distinct other agents with cos > thr in the same goal period >= {TEMPLATE_MIN_OTHER_AGENTS}",
                      "primary": "bge versions", "models": {s: MODELS[m]["hf"] for m, s in SHORT.items()}})
    print(json.dumps(meta, indent=1, default=float))
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
