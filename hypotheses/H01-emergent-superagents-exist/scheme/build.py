"""H01 scheme S1 (observational order parameter): statements -> whitened vectors, meaning clusters, goal fields,
agent-day vectors, room membership and pair-day exposure. NON-HOLDOUT DAYS ONLY.

Statements = each agent's own chat messages (chat_core.speaker_kind == "agent") + its self-written intentions
(session goals before regime III, CONSOLIDATE nextSessionGoal after). Embeddings: BAAI/bge-small-en-v1.5 (shared,
data/processed/shared/embeddings/). Per regime (I < 02-25 <= II < 03-24 <= III, by PT date), fitted on non-holdout
statements only:
  - center on the regime mean, PCA, whiten (z = (x - mu) V_d / sqrt(lambda_d)); d = 64 stored, first 32 = the
    primary n = 32 vectors (PCA whitening is nested, so d = 16 is the first 16 columns);
  - k-means (cosine geometry: on unit-normalized whitened vectors) for k = 20, 40, 80 at d = 32, and k = 40 at
    d = 16 and d = 64 (robustness).
Goal field g-hat: bge embedding of the village goal text and of the kickoff message(s) posted at the start of the
period's first day (boilerplate sentences about the *previous* goal stripped), per room; per-agent assigned goals
(agent_goals, #51) as agent-specific goal fields. Whitened in the regime basis, unit-normalized.

Outputs (data/processed/H01-emergent-superagents-exist/):
  statements.parquet        kind (0 chat, 1 intention), message_id, event_index, emb_row, agent, t, pt_date,
                            goal_no, unit, regime, room, n_chars
  vectors_w32.npy           (n_stmt, 32) fp16 whitened (NOT unit-normalized), row-aligned with statements
  vectors_w64.npy           (n_stmt, 64) fp16 whitened (robustness; first 16 columns = d16)
  clusters.parquet          k20, k40, k80 (d32), k40_d16, k40_d64 labels, row-aligned
  basis_<regime>.npz        mean, components (64 x 384), eigvals (64), centroids_*  (lets the confirm script
                            project holdout statements at confirmation time without refitting)
  agent_day.parquet         agent, pt_date, unit, goal_no, regime, n_stmt, n_chat, n_int, resultant (|mean unit
                            vector|), room_mode, room_purity, room_mode_stmt   (+ agent_day_w32.npy, unit vectors)
  pair_day_exposure.parquet pt_date, i (recipient), j (speaker), n_seen  (# of j's messages i was exposed to)
  goals.parquet + goals_raw.npy (384-d) + goals_w32.npy / goals_w64.npy (whitened, unit, in `regime` basis)
  units.json                analysis units (goal period split at step changes) with their days
  _provenance.json

Usage:  UV_OFFLINE=1 HF_HUB_OFFLINE=1 uv run --with sentence-transformers python \
            hypotheses/H01-emergent-superagents-exist/scheme/build.py [--reuse-goal-emb]
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h01common import (OUT, EMB, SH, SEED, ROOT, guard_holdout, holdout_mask, kmeans, nonholdout_days,  # noqa: E402
                       unit, unit_of, whiten_apply, write_provenance)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(ROOT / "infra/shared"))
from common import load_goals, rows  # noqa: E402

D_MAX = 64
KS = (20, 40, 80)
MODEL = "BAAI/bge-small-en-v1.5"
PT = "America/Los_Angeles"


def regime_of_date(col):
    return (pl.when(col < "2026-02-25").then(pl.lit("I")).when(col < "2026-03-24").then(pl.lit("II"))
            .otherwise(pl.lit("III")))


def load_statements(days: list[str], allow_holdout: bool = False) -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", pl.col("goal_no").alias("cal_goal"))
    roster = pl.read_parquet(SH / "roster.parquet").select("agent")
    # chat
    cc = (pl.read_parquet(SH / "chat_core.parquet").filter(pl.col("speaker_kind") == "agent")
          .select("message_id", "t", "pt_date", "goal_no", "room", "agent", pl.col("length").alias("n_chars")))
    ci = pl.read_parquet(EMB / "chat_index.parquet").with_row_index("emb_row")
    cc = cc.join(ci, on="message_id", how="inner").with_columns(pl.lit(0, pl.Int8).alias("kind"),
                                                                 pl.lit(None, pl.Int64).alias("event_index"))
    # intentions
    it = pl.read_parquet(SH / "intentions.parquet")
    ii = pl.read_parquet(EMB / "intentions_index.parquet").with_row_index("emb_row")
    it = it.join(ii, on="event_index", how="inner")
    itx = pl.read_parquet(SH / "intentions_text.parquet", columns=["event_index", "goal_text"]).with_columns(
        pl.col("goal_text").str.len_chars().cast(pl.Int32).alias("n_chars")).drop("goal_text")
    it = it.join(itx, on="event_index", how="left")
    it = it.with_columns(pl.col("t").dt.convert_time_zone(PT).dt.date().cast(pl.Utf8).alias("pt_date"))
    goals = load_goals()
    gs = pl.DataFrame({"t_goal": [g["start"] for g in goals], "goal_no": [g["goal_no"] for g in goals]}).with_columns(
        pl.col("t_goal").dt.cast_time_unit("us"), pl.col("goal_no").cast(pl.Int8))
    it = it.sort("t").join_asof(gs, left_on="t", right_on="t_goal", strategy="backward").drop("t_goal")
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").select("agent", "room", pl.col("t_start").alias("t")).sort("agent", "t")
    it = it.sort("agent", "t").join_asof(rt, on="t", by="agent", strategy="backward")
    it = it.with_columns(pl.lit(1, pl.Int8).alias("kind"), pl.lit(None, pl.Utf8).alias("message_id"))
    cols = ["kind", "message_id", "event_index", "emb_row", "agent", "t", "pt_date", "goal_no", "room", "n_chars"]
    st = pl.concat([cc.select(cols).with_columns(pl.col("emb_row").cast(pl.UInt32), pl.col("room").cast(pl.Int8),
                                                  pl.col("goal_no").cast(pl.Int8), pl.col("n_chars").cast(pl.Int32)),
                    it.select(cols).with_columns(pl.col("emb_row").cast(pl.UInt32), pl.col("room").cast(pl.Int8),
                                                  pl.col("goal_no").cast(pl.Int8), pl.col("n_chars").cast(pl.Int32))])
    st = st.join(roster, on="agent", how="semi")
    # holdout: by day (calendar) AND by the row's own (pt_date, goal_no)
    st = st.join(cal, on="pt_date", how="left")
    hm_row = holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())
    if allow_holdout:  # confirmation only (analysis/confirm_d32.py --confirm); the scheme build never sets this
        hm_row = [False] * st.height
    st = st.with_columns(pl.Series("hm_row", hm_row)).filter(~pl.col("hm_row") & pl.col("pt_date").is_in(days)).drop("hm_row")
    st = st.with_columns(pl.col("cal_goal").cast(pl.Int8).alias("goal_no")).drop("cal_goal")
    st = st.filter(pl.col("goal_no") > 0)
    st = st.with_columns(regime_of_date(pl.col("pt_date")).alias("regime"),
                         pl.struct("goal_no", "pt_date").map_elements(lambda s: unit_of(s["goal_no"], s["pt_date"]),
                                                                      return_dtype=pl.Utf8).alias("unit"))
    return st.sort("t", "kind").select("kind", "message_id", "event_index", "emb_row", "agent", "t", "pt_date",
                                       "goal_no", "unit", "regime", "room", "n_chars")


def raw_embeddings(st: pl.DataFrame) -> np.ndarray:
    ce = np.load(EMB / "chat_bge_small.npy", mmap_mode="r")
    ie = np.load(EMB / "intentions_bge_small.npy", mmap_mode="r")
    X = np.zeros((st.height, ce.shape[1]), dtype=np.float32)
    k = st["kind"].to_numpy(); r = st["emb_row"].to_numpy().astype(np.int64)
    X[k == 0] = ce[np.sort(r[k == 0])][np.argsort(np.argsort(r[k == 0]))]
    X[k == 1] = ie[np.sort(r[k == 1])][np.argsort(np.argsort(r[k == 1]))]
    return X


def fit_basis(X: np.ndarray) -> dict:
    mu = X.mean(0)
    Xc = X - mu
    C = (Xc.T @ Xc) / (len(X) - 1)
    w, V = np.linalg.eigh(C.astype(np.float64))
    o = np.argsort(w)[::-1][:D_MAX]
    return {"mean": mu.astype(np.float32), "components": V[:, o].T.astype(np.float32), "eigvals": w[o].astype(np.float32),
            "var_explained": np.float32(w[o].sum() / w.sum())}


def room_membership(st: pl.DataFrame, days: list[str]) -> pl.DataFrame:
    """Time-weighted room per agent-day over the day's empirical active window (1-min grid, as-of rooms_timeline)."""
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days)).select("pt_date", "win_start", "win_end")
    ad = st.select("agent", "pt_date").unique()
    grid = cal.with_columns(pl.datetime_ranges("win_start", "win_end", interval="1m").alias("t")).explode("t").select("pt_date", "t")
    g = ad.join(grid, on="pt_date").with_columns(pl.col("t").dt.cast_time_unit("us"))
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").select("agent", "room", pl.col("t_start").alias("t"), "t_end").sort("agent", "t")
    g = g.sort("agent", "t").join_asof(rt, on="t", by="agent", strategy="backward")
    g = g.with_columns(pl.when(pl.col("t_end").is_not_null() & (pl.col("t") >= pl.col("t_end"))).then(None)
                       .otherwise(pl.col("room")).alias("room"))
    rm = (g.drop_nulls("room").group_by("agent", "pt_date", "room").agg(pl.len().alias("n")).sort("n", descending=True)
          .group_by("agent", "pt_date").agg(pl.col("room").first().alias("room_mode"),
                                             (pl.col("n").first() / pl.col("n").sum()).cast(pl.Float32).alias("room_purity")))
    sm = (st.filter(pl.col("room").is_not_null()).group_by("agent", "pt_date", "room").agg(pl.len().alias("n"))
          .sort("n", descending=True).group_by("agent", "pt_date").agg(pl.col("room").first().alias("room_mode_stmt")))
    return ad.join(rm, on=["agent", "pt_date"], how="left").join(sm, on=["agent", "pt_date"], how="left")


def pair_exposure(days: list[str]) -> pl.DataFrame:
    cc = pl.read_parquet(SH / "chat_core.parquet").with_row_index("msg").select(
        pl.col("msg").cast(pl.UInt32), "pt_date", "speaker_kind", pl.col("agent").alias("j"))
    ex = pl.read_parquet(SH / "exposure.parquet").filter(pl.col("lag_s").is_not_null()).select("msg", pl.col("agent").alias("i"))
    e = (ex.join(cc, on="msg").filter((pl.col("speaker_kind") == "agent") & pl.col("pt_date").is_in(days) & (pl.col("i") != pl.col("j")))
         .group_by("pt_date", "i", "j").agg(pl.len().cast(pl.Int32).alias("n_seen")))
    return e.sort("pt_date", "i", "j")


# ============================================================================ goal fields
BOILER = re.compile(r"wrap(s|ped)?\s+up|to a close|your memory|previous goal|last week|last two weeks|that goal is", re.I)


def strip_boilerplate(text: str) -> str:
    sents = re.split(r"(?<=[.!?])\s+|\n+", text)
    keep = [s for s in sents if s.strip() and not BOILER.search(s)]
    return " ".join(keep).strip()


def chunks(text: str, n: int = 700) -> list[str]:
    sents = re.split(r"(?<=[.!?])\s+", text)
    out, cur = [], ""
    for s in sents:
        if len(cur) + len(s) > n and cur:
            out.append(cur); cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        out.append(cur)
    return [c[:2000] for c in out if len(c) > 20]


def goal_texts(st: pl.DataFrame, days: list[str]) -> tuple[list[dict], list[list[str]]]:
    """Return (meta rows, list of text chunks per row). Kickoff = human messages >= 250 chars posted within 45 min
    of the window start on the goal period's first non-holdout active day, per room. Text stays in memory only."""
    goals = {g["goal_no"]: g for g in load_goals()}
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days))
    first = cal.group_by("goal_no").agg(pl.col("pt_date").min()).sort("goal_no")
    cc = pl.read_parquet(SH / "chat_core.parquet").filter(pl.col("speaker_kind") == "human").select("message_id", "t", "pt_date", "room", "length")
    ct = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"])
    meta, texts = [], []
    for g, d0 in first.iter_rows():
        if g == 0:
            continue
        ws = cal.filter(pl.col("pt_date") == d0)["win_start"][0]
        meta.append({"goal_no": g, "kind": "goal", "room": -1, "agent": -1, "valid_from": d0, "valid_to": None})
        texts.append([goals[g]["goal"]])
        k = cc.filter((pl.col("pt_date") == d0) & (pl.col("length") >= 250) & (pl.col("t") >= ws - pl.duration(minutes=10))
                      & (pl.col("t") <= ws + pl.duration(minutes=45)))
        if k.height == 0:
            k = cc.filter((pl.col("pt_date") == d0) & (pl.col("length") >= 250)).sort("length", descending=True).head(1)
        k = k.join(ct, on="message_id")
        for room, grp in k.group_by("room"):
            body = " ".join(strip_boilerplate(x) for x in grp.sort("t")["text"].to_list())
            ch = chunks(body)
            if ch:
                meta.append({"goal_no": g, "kind": "kickoff", "room": int(room[0]), "agent": -1, "valid_from": d0, "valid_to": None})
                texts.append(ch)
    # per-agent assigned goals (#51 era)
    roster = {r["agent_id"]: r["agent"] for r in pl.read_parquet(SH / "roster.parquet").iter_rows(named=True)}
    for a in rows("agent_goals"):
        if a["agent_id"] not in roster:
            continue
        txt = a["name"] + ("" if a.get("description") in (None, "None") else ". " + a["description"])
        vf = a["start_time"][:10] if a.get("start_time") else None
        vt = a["end_time"][:10] if a.get("end_time") else None
        meta.append({"goal_no": 51, "kind": "agent_goal", "room": -1, "agent": int(roster[a["agent_id"]]), "valid_from": vf, "valid_to": vt})
        texts.append([txt])
    return meta, texts


def embed_goal_texts(texts: list[list[str]]) -> np.ndarray:
    import torch
    from sentence_transformers import SentenceTransformer
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    torch.set_num_threads(4)
    m = SentenceTransformer(MODEL, device=dev)
    m.max_seq_length = 256
    out = np.zeros((len(texts), 384), dtype=np.float32)
    for i, ch in enumerate(texts):
        e = m.encode(ch, batch_size=32, normalize_embeddings=True, convert_to_numpy=True)
        out[i] = e.mean(0)  # mean of unit chunk embeddings (re-normalized after whitening downstream)
    return out


# ============================================================================ main
def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    days = nonholdout_days()
    guard_holdout(days)
    st = load_statements(days)
    guard_holdout(sorted(st["pt_date"].unique().to_list()))
    print("statements", st.height, st.group_by("kind").len().sort("kind").rows(), f"{time.time()-t0:.0f}s", flush=True)
    X = raw_embeddings(st)
    Z64 = np.zeros((st.height, D_MAX), dtype=np.float32)
    labels = {f"k{k}": np.full(st.height, -1, np.int16) for k in KS}
    labels.update({"k40_d16": np.full(st.height, -1, np.int16), "k40_d64": np.full(st.height, -1, np.int16)})
    reg = st["regime"].to_numpy()
    bases = {}
    for R in ("I", "II", "III"):
        m = reg == R
        b = fit_basis(X[m])
        Z = whiten_apply(X[m], b, D_MAX)
        Z64[m] = Z
        cents = {}
        for k in KS:
            C, lab, _ = kmeans(unit(Z[:, :32]).astype(np.float32), k, seed=SEED + k)
            labels[f"k{k}"][m] = lab; cents[f"centroids_k{k}_d32"] = C
        for d in (16, 64):
            C, lab, _ = kmeans(unit(Z[:, :d]).astype(np.float32), 40, seed=SEED + 40 + d)
            labels[f"k40_d{d}"][m] = lab; cents[f"centroids_k40_d{d}"] = C
        np.savez(OUT / f"basis_{R}.npz", **b, **cents, n_fit=np.int64(m.sum()))
        bases[R] = b
        print("regime", R, int(m.sum()), "stmts; var explained by 64 PCs", float(b["var_explained"]), f"{time.time()-t0:.0f}s", flush=True)
    st.write_parquet(OUT / "statements.parquet", compression="zstd")
    np.save(OUT / "vectors_w64.npy", Z64.astype(np.float16))
    np.save(OUT / "vectors_w32.npy", Z64[:, :32].astype(np.float16))
    pl.DataFrame(labels).write_parquet(OUT / "clusters.parquet", compression="zstd")

    # agent-day vectors (w32): normalized mean of unit statement vectors
    U = unit(Z64[:, :32])
    key = st.select("agent", "pt_date").with_row_index("r")
    ad = (key.group_by("agent", "pt_date", maintain_order=True).agg(pl.col("r")).sort("pt_date", "agent"))
    V = np.zeros((ad.height, 32), np.float32); res = np.zeros(ad.height, np.float32)
    for n, idx in enumerate(ad["r"].to_list()):
        mvec = U[idx].mean(0); res[n] = np.linalg.norm(mvec); V[n] = mvec / max(res[n], 1e-9)
    cnt = st.group_by("agent", "pt_date").agg(pl.len().alias("n_stmt"), (pl.col("kind") == 0).sum().alias("n_chat"),
                                              (pl.col("kind") == 1).sum().alias("n_int"), pl.col("unit").first(),
                                              pl.col("goal_no").first(), pl.col("regime").first())
    rm = room_membership(st, days)
    ad = (ad.drop("r").with_columns(pl.Series("resultant", res)).join(cnt, on=["agent", "pt_date"], how="left")
          .join(rm, on=["agent", "pt_date"], how="left"))
    ad.write_parquet(OUT / "agent_day.parquet", compression="zstd")
    np.save(OUT / "agent_day_w32.npy", V.astype(np.float16))
    print("agent-days", ad.height, f"{time.time()-t0:.0f}s", flush=True)

    pe = pair_exposure(days)
    guard_holdout(sorted(pe["pt_date"].unique().to_list()))
    pe.write_parquet(OUT / "pair_day_exposure.parquet", compression="zstd")
    print("pair-day exposure rows", pe.height, flush=True)

    # goal fields
    meta, texts = goal_texts(st, days)
    graw_path = OUT / "goals_raw.npy"
    if "--reuse-goal-emb" in sys.argv and graw_path.exists():
        G = np.load(graw_path)
        assert len(G) == len(meta), "goal rows changed; re-embed"
    else:
        G = embed_goal_texts(texts)
        np.save(graw_path, G)
    gm = pl.DataFrame(meta, infer_schema_length=None).with_columns(pl.Series("n_chunks", [len(t) for t in texts]),
                                         pl.Series("n_chars", [sum(len(c) for c in t) for t in texts]))
    # regime basis for each goal row = regime(s) of the goal period's non-holdout days
    goal_regs = st.group_by("goal_no").agg(pl.col("regime").unique()).rows()
    goal_regs = {int(g): sorted(r) for g, r in goal_regs}
    rows_out, W32, W64 = [], [], []
    for i, r in enumerate(gm.iter_rows(named=True)):
        for R in goal_regs.get(r["goal_no"], []):
            z = whiten_apply(G[i:i + 1], bases[R], D_MAX)[0]
            rows_out.append({**r, "regime": R, "gid": i})
            W32.append(unit(z[:32])); W64.append(unit(z))
    pl.DataFrame(rows_out, infer_schema_length=None).write_parquet(OUT / "goals.parquet", compression="zstd")
    np.save(OUT / "goals_w32.npy", np.array(W32, np.float32))
    np.save(OUT / "goals_w64.npy", np.array(W64, np.float32))
    print("goal rows", len(rows_out), gm.group_by("kind").len().rows(), flush=True)

    units = (st.group_by("unit").agg(pl.col("goal_no").first(), pl.col("regime").unique().sort(),
                                     pl.col("pt_date").unique().sort().alias("days"), pl.col("agent").n_unique().alias("n_agents"))
             .sort(pl.col("days").list.first()))
    uj = [{"unit": u, "goal_no": int(g), "regimes": list(r), "days": list(d), "n_agents": int(n)} for u, g, r, d, n in units.iter_rows()]
    (OUT / "units.json").write_text(json.dumps(uj, indent=1))

    write_provenance("scheme", "hypotheses/H01-emergent-superagents-exist/scheme/build.py",
                     ["shared/chat_core", "shared/chat_text (kickoff texts only, not stored)", "shared/intentions",
                      "shared/intentions_text (lengths only)", "shared/embeddings (bge-small)", "shared/rooms_timeline",
                      "shared/exposure", "shared/calendar", "shared/roster", "raw/village_goals", "raw/agent_goals"],
                     {"embedding_model": MODEL, "whitening": "per regime, PCA, fit on non-holdout statements", "d_stored": D_MAX,
                      "d_primary": 32, "kmeans_k": list(KS), "kmeans_extra": ["k40_d16", "k40_d64"], "kmeans_geometry": "unit-normalized whitened",
                      "seed": SEED, "regimes": "I < 2026-02-25 <= II < 2026-03-24 <= III (PT date)",
                      "holdout": "excluded: calendar.holdout OR holdout_mask (day and row goal_no); asserted",
                      "kickoff_rule": "human msgs >= 250 chars within [win_start-10m, win_start+45m] of the goal's first non-holdout day, per room; previous-goal boilerplate sentences stripped",
                      "n_statements": st.height, "n_days": len(days), "units": [u["unit"] for u in uj]})
    print("done", f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
