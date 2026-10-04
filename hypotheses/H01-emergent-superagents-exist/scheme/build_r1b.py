"""H01 round 1b (improved data, 2026-10-04): parallel scheme folders for the round-1 (D3.1.a / D3.2) statistics on the
corrected shared inputs. The round-1 scheme (scheme/build.py -> data/processed/H01-emergent-superagents-exist/) is
left untouched and still runs; analysis/explore.py reads a 1b folder only when given --r1b TAG.

What changes relative to round 1 (each is a switch, so the steps can be separated):
  --model bge_small | gte_modernbert   statement embeddings from the shared tables (DQ5). bge_small = the same raw
                                       vectors as round 1; gte_modernbert = Alibaba-NLP/gte-modernbert-base (768-d).
                                       Whitening: H01's own per-regime PCA whitening (64 stored, first 32 primary),
                                       fit on ALL non-holdout H01 statements before any dedupe, so bge + --dedupe none
                                       reproduces round 1's vectors exactly.
  --dedupe none | restate | copies     drop chat statements flagged by DQ5's statement_flags: `restate` = the model's
                                       own self-repeat flag (bge: self_repeat, gte: self_repeat_gte; restatements and
                                       copies), `copies` = self_repeat_both (near-copies, both models agree).
                                       Intentions are kept (H26's round-1 rule). k-means rulers (k = 40, d = 32, per
                                       regime) are fit on all statements before the dedupe and only rows are dropped.
  --style                              use DQ5's style-residualized statement vectors (style_resid_period32, within
                                       goal period, both models) instead of the whitened vectors; these are 32-d only
                                       (P1/P2/P3 and P5-P7 only; goal fields are left in the whitened basis and are
                                       NOT meaningful in this space, so P4/P5/P9 are not read from a --style run).
  --exposure h01 | ledger              pair-day exposure: h01 = round 1 (shared `exposure`, lag_s not null);
                                       ledger = DQ1 context ledger (messages of j that entered a call of i, not
                                       omitted), the corrected visibility rule.
  goal fields                          always the shared goal table (goal_fields.py; embeddings/goals.parquet +
                                       goal_vectors[_gte_modernbert].npy): fixes the #38 room-2/3 kickoff swap and
                                       the 15-56 degree kickoff-span differences in #36, #37, #39, #40, #42 (H32).
                                       Kickoff rows = shared kickoff_room rows (one per room), as in round 1.

Output: data/processed/H01-emergent-superagents-exist/r1b/<tag>/ with the same file names as the round-1 scheme
(statements, vectors_w64 (or 32-d for --style), clusters, agent_day, units.json, goals + goals_raw, basis_<R>,
pair_day_exposure), loadable by analysis/h01data.Scheme(base=...). Non-holdout only (asserted).

Usage: uv run python hypotheses/H01-emergent-superagents-exist/scheme/build_r1b.py --model gte_modernbert \
           --dedupe restate [--style] [--exposure ledger] [--tag NAME]
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import argparse  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h01common import OUT, SH, SEED, guard_holdout, kmeans, unit, whiten_apply, write_provenance  # noqa: E402
from build import D_MAX, fit_basis  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

EMB = SH / "embeddings"
SUFFIX = {"bge_small": "bge_small", "gte_modernbert": "gte_modernbert"}
GOALVEC = {"bge_small": "goal_vectors.npy", "gte_modernbert": "goal_vectors_gte_modernbert.npy"}
FLAG = {"restate": {"bge_small": "self_repeat", "gte_modernbert": "self_repeat_gte"}, "copies": "self_repeat_both"}
R1B = OUT / "r1b"


def tag_of(a) -> str:
    if a.tag:
        return a.tag
    t = f"{'bge' if a.model == 'bge_small' else 'gte'}_{a.dedupe}"
    return t + ("_style" if a.style else "") + ("_ledger" if a.exposure == "ledger" else "")


def shared_rows(st: pl.DataFrame) -> np.ndarray:
    """Row of the shared embeddings/statements.parquet (= statement_flags.srow) for each H01 statement."""
    s = (pl.read_parquet(EMB / "statements.parquet").with_row_index("srow")
         .with_columns(pl.when(pl.col("kind") == "chat").then(0).otherwise(1).cast(pl.Int8).alias("k")))
    j = st.select("kind", "emb_row", "agent", "pt_date").with_row_index("r").join(
        s.select("srow", "k", "src_row", pl.col("agent").alias("a2"), pl.col("pt_date").alias("d2")),
        left_on=["kind", "emb_row"], right_on=["k", "src_row"], how="left").sort("r")
    assert j["srow"].null_count() == 0, "H01 statement without a shared statement row"
    assert (j["agent"] == j["a2"]).all() and (j["pt_date"] == j["d2"]).all(), "shared statement row mismatch"
    return j["srow"].to_numpy()


def raw_embeddings(st: pl.DataFrame, model: str) -> np.ndarray:
    ce = np.load(EMB / f"chat_{SUFFIX[model]}.npy", mmap_mode="r")
    ie = np.load(EMB / f"intentions_{SUFFIX[model]}.npy", mmap_mode="r")
    X = np.zeros((st.height, ce.shape[1]), dtype=np.float32)
    k = st["kind"].to_numpy(); r = st["emb_row"].to_numpy().astype(np.int64)
    for kind, E in ((0, ce), (1, ie)):
        m = k == kind
        o = np.argsort(r[m])
        tmp = np.asarray(E[r[m][o]], dtype=np.float32)
        out = np.empty_like(tmp); out[o] = tmp
        X[m] = out
    return X


def ledger_exposure(days: list[str]) -> pl.DataFrame:
    """Pair-day exposure from the DQ1 context ledger: n_seen = # messages of j (agent) that entered one of i's calls
    on that PT day (omitted items excluded). Same columns as the round-1 pair_day_exposure."""
    turns = (pl.scan_parquet(SH / "context_ledger_turns.parquet").select("turn_id", pl.col("agent").alias("i"), "pt_date")
             .filter(pl.col("pt_date").is_in(days)))
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet")
             .filter((pl.col("kind") == "agent") & ~pl.col("omitted") & pl.col("sender").is_not_null())
             .select("turn_id", pl.col("sender").alias("j")))
    e = (items.join(turns, on="turn_id", how="inner").filter(pl.col("i") != pl.col("j"))
         .group_by("pt_date", "i", "j").agg(pl.len().cast(pl.Int32).alias("n_seen")).collect())
    return e.sort("pt_date", "i", "j")


def shared_goals(model: str, regimes_of_goal: dict) -> tuple[pl.DataFrame, np.ndarray]:
    """Shared goal table -> H01's goals.parquet layout (goal / kickoff per room / agent_goal; one row per regime of
    the goal period's non-holdout days); gid indexes the returned raw goal-vector array (= shared gid)."""
    sg = pl.read_parquet(EMB / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    G = np.load(EMB / GOALVEC[model]).astype(np.float32)
    assert G.shape[0] == sg.height
    rows = []
    for r in sg.iter_rows(named=True):
        kind = {"goal": "goal", "kickoff_room": "kickoff", "agent_goal": "agent_goal"}.get(r["kind"])
        if kind is None or r["holdout"]:
            continue
        for R in regimes_of_goal.get(int(r["goal_no"]), []):
            rows.append({"goal_no": int(r["goal_no"]), "kind": kind,
                         "room": int(r["room"]) if (kind == "kickoff" and r["room"] is not None) else -1,
                         "agent": int(r["agent"]) if (kind == "agent_goal" and r["agent"] is not None) else -1,
                         "valid_from": r["valid_from"], "valid_to": r["valid_to"],
                         "n_chunks": int(r["n_chunks"] or 0), "n_chars": int(r["n_chars"] or 0),
                         "regime": R, "gid": int(r["gid"])})
    return pl.DataFrame(rows, infer_schema_length=None), G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="bge_small", choices=list(SUFFIX))
    ap.add_argument("--dedupe", default="restate", choices=["none", "restate", "copies"])
    ap.add_argument("--style", action="store_true")
    ap.add_argument("--exposure", default="h01", choices=["h01", "ledger"])
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()
    t0 = time.time()
    tag = tag_of(a)
    out = R1B / tag
    out.mkdir(parents=True, exist_ok=True)
    st = pl.read_parquet(OUT / "statements.parquet")
    days = sorted(st["pt_date"].unique().to_list())
    guard_holdout(days)
    srow = shared_rows(st)
    reg = st["regime"].to_numpy()
    # ---------------------------------------------------------------- vectors, bases, clusters (all statements)
    X = raw_embeddings(st, a.model)
    Z = np.zeros((st.height, D_MAX), np.float32)
    bases = {}
    for R in ("I", "II", "III"):
        m = reg == R
        b = fit_basis(X[m])
        Z[m] = whiten_apply(X[m], b, D_MAX)
        bases[R] = b      # kept for --style too: goal fields stay in the whitened (not residualized) basis
    del X
    dstore = D_MAX
    if a.style:
        Zs = np.load(EMB / f"statements_style_resid_period32_{SUFFIX[a.model]}.npy", mmap_mode="r")
        Z = np.asarray(Zs[srow], dtype=np.float32)
        Z[~np.isfinite(Z).all(1)] = 0.0
        dstore = 32
    lab = np.full(st.height, -1, np.int16)
    for R in ("I", "II", "III"):
        m = reg == R
        C, lb, _ = kmeans(unit(Z[m][:, :32]).astype(np.float32), 40, seed=SEED + 40)
        lab[m] = lb
        np.savez(out / f"basis_{R}.npz", **bases[R], centroids_k40_d32=C, n_fit=np.int64(m.sum()))
        print("regime", R, int(m.sum()), f"{time.time() - t0:.0f}s", flush=True)
    # ---------------------------------------------------------------- dedupe (rows only)
    keep = np.ones(st.height, bool)
    if a.dedupe != "none":
        col = FLAG[a.dedupe] if a.dedupe == "copies" else FLAG[a.dedupe][a.model]
        fl = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", col])
        assert (fl["srow"].to_numpy() == np.arange(fl.height)).all()
        flag = fl[col].to_numpy()[srow].astype(bool)
        keep = ~(flag & (st["kind"].to_numpy() == 0))
    st2 = st.filter(pl.Series(keep))
    Z2 = Z[keep]; lab2 = lab[keep]
    st2.write_parquet(out / "statements.parquet", compression="zstd")
    np.save(out / "vectors_w64.npy", Z2[:, :dstore].astype(np.float16))
    pl.DataFrame({"k20": lab2, "k40": lab2, "k80": lab2, "k40_d16": lab2, "k40_d64": lab2}).write_parquet(
        out / "clusters.parquet", compression="zstd")
    print(f"statements {st.height} -> {st2.height} (dropped {int((~keep).sum())} chat: {a.dedupe})", flush=True)
    # ---------------------------------------------------------------- agent days (room columns from round 1)
    U = unit(Z2[:, :32])
    key = st2.select("agent", "pt_date").with_row_index("r")
    ad = key.group_by("agent", "pt_date", maintain_order=True).agg(pl.col("r")).sort("pt_date", "agent")
    V = np.zeros((ad.height, 32), np.float32); res = np.zeros(ad.height, np.float32)
    for n, idx in enumerate(ad["r"].to_list()):
        mv = U[idx].mean(0); res[n] = np.linalg.norm(mv); V[n] = mv / max(res[n], 1e-9)
    cnt = st2.group_by("agent", "pt_date").agg(pl.len().alias("n_stmt"), (pl.col("kind") == 0).sum().alias("n_chat"),
                                               (pl.col("kind") == 1).sum().alias("n_int"), pl.col("unit").first(),
                                               pl.col("goal_no").first(), pl.col("regime").first())
    rooms = pl.read_parquet(OUT / "agent_day.parquet").select("agent", "pt_date", "room_mode", "room_purity", "room_mode_stmt")
    ad = (ad.drop("r").with_columns(pl.Series("resultant", res)).join(cnt, on=["agent", "pt_date"], how="left")
          .join(rooms, on=["agent", "pt_date"], how="left"))
    ad.write_parquet(out / "agent_day.parquet", compression="zstd")
    np.save(out / "agent_day_w32.npy", V.astype(np.float16))
    shutil.copy(OUT / "units.json", out / "units.json")
    # ---------------------------------------------------------------- exposure
    if a.exposure == "ledger":
        pe = ledger_exposure(days)
        guard_holdout(sorted(pe["pt_date"].unique().to_list()))
        pe.write_parquet(out / "pair_day_exposure.parquet", compression="zstd")
    else:
        shutil.copy(OUT / "pair_day_exposure.parquet", out / "pair_day_exposure.parquet")
    # ---------------------------------------------------------------- goal fields (shared)
    goal_regs = {int(g): sorted(r) for g, r in st.group_by("goal_no").agg(pl.col("regime").unique()).rows()}
    gt, G = shared_goals(a.model, goal_regs)
    gt.write_parquet(out / "goals.parquet", compression="zstd")
    np.save(out / "goals_raw.npy", G)
    write_provenance(f"r1b_{tag}", "hypotheses/H01-emergent-superagents-exist/scheme/build_r1b.py",
                     ["H01 statements (round-1 scheme)", f"shared/embeddings/{{chat,intentions}}_{SUFFIX[a.model]}",
                      "shared/statement_flags", "shared/embeddings/goals + " + GOALVEC[a.model],
                      "shared/embeddings/statements_style_resid_period32" if a.style else "",
                      "shared/context_ledger_{turns,items}" if a.exposure == "ledger" else "shared/exposure (via H01)"],
                     {"tag": tag, "model": a.model, "dedupe": a.dedupe, "style": a.style, "exposure": a.exposure,
                      "n_statements": st2.height, "n_dropped": int((~keep).sum()),
                      "whitening": "H01 per-regime PCA on all non-holdout statements (before dedupe)" if not a.style
                      else "DQ5 style_resid_period32 (whitened + residualized within goal period)",
                      "kmeans": "k40 d32 per regime, fit before dedupe (k20/k80 columns are copies)"})
    prov = json.loads((OUT / "_provenance.json").read_text())[f"r1b_{tag}"]
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print("done", tag, f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
