"""H54 round 2 (card section "Round 2"): R5 embedding swap build, synthetic validation (S6-S8), R3 read-out re-quench,
R2 first-plan read, R1 two concrete targets (#12 debates; #19 / #21 options).

Subcommands
  r5build   gte copies of stmt_z / stmt_zs in data/processed/H54-kickoff-quench-target/r2_gte/ (+ model-free tables);
            then run explore.py and native.py with H54_MODEL=gte_modernbert. --check compares a bge rebuild with round 1.
  synth     S6 (read-out vs convergence on the real message/read skeleton), S7 (#12 team domains), S8 (#19/#21 domains)
  r3        human-message read-out re-quench (both models)
  r2        first-plan read (both models)
  r1        #12 team domains + motion target; #19/#21 two-option tests (both models)
  estimates write per_period_estimates rows (after the runs)
Outputs: data/processed/H54-kickoff-quench-target/r2/*.json|parquet. No text is read except through the stored
target vectors (scheme/embed_targets.py). Pools: none (single process, 2 BLAS threads).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys

import numpy as np
import polars as pl
from scipy import stats

import h54est as E
import h54lib as L

EM = L._EM
R2 = L.OUT_BASE / "r2"
MODELS = ("bge_small", "gte_modernbert")
UTC = dt.timezone.utc
LAG_BINS = [0, 30, 60, 120, 300, 900]
AGE_BINS = [0, 120, 600, 1e9]      # Amendment R2-1: the before message's age (t_m - t_before) is matched too
CC = L.CLAUDE_CODE


# ============================================================================== vectors (model-explicit)
_W = {}


def whitener(regime, model):
    if (regime, model) not in _W:
        _W[(regime, model)] = L.load_whitener(regime, L.D) if model == "bge_small" else EM.load_whitener(regime, L.D, model)
    return _W[(regime, model)]


def wunit(raw, regime, model):
    return E.unit(whitener(regime, model)(np.asarray(raw, dtype=np.float32)))


_CHAT = {}


def chat_raw(model):
    if model not in _CHAT:
        _CHAT[model] = np.load(EM.emb_path("chat", model), mmap_mode="r")
    return _CHAT[model]


_CIDX = None


def chat_row_map() -> pl.DataFrame:
    global _CIDX
    if _CIDX is None:
        _CIDX = pl.read_parquet(L.ED / "chat_index.parquet").with_row_index("crow")
    return _CIDX


def chat_vecs(message_ids, regime_of_row, model) -> np.ndarray:
    """Unit whitened chat vectors for message ids; regime_of_row: list of regimes (one per id). NaN rows if missing."""
    ids = list(message_ids)
    df = pl.DataFrame({"message_id": ids, "k": np.arange(len(ids)), "reg": list(regime_of_row)}).join(
        chat_row_map(), on="message_id", how="left")
    out = np.full((len(ids), L.D), np.nan)
    raw = chat_raw(model)
    for reg in df["reg"].unique().to_list():
        d = df.filter((pl.col("reg") == reg) & pl.col("crow").is_not_null())
        if d.height == 0:
            continue
        cr = d["crow"].to_numpy()
        o = np.argsort(cr)
        X = np.asarray(raw[cr[o]], dtype=np.float32)
        out[d["k"].to_numpy()[o]] = wunit(X, reg, model)
    return out


def goal_vec(p, kind, regime, model, room=None):
    g = L.goals().filter((pl.col("goal_no") == p) & (pl.col("kind") == kind))
    if room is not None:
        g = g.filter(pl.col("room") == room)
    if g.height == 0:
        return None
    gv = np.load(L.ED / "goal_vectors.npy") if model == "bge_small" else EM.goal_vectors(model)
    return wunit(np.asarray(gv[int(g["gid"][0])], dtype=np.float32)[None], regime, model)[0]


def stmt_Z(model):
    """H54 stmt table + whitened vectors (target-period basis) for a model."""
    base = L.OUT_BASE if model == "bge_small" else L.OUT_BASE / "r2_gte"
    st = pl.read_parquet(L.OUT_BASE / "stmt.parquet")
    Z = np.load(base / "stmt_z.npy").astype(np.float64)
    return st, Z


def jdump(path, obj):
    L.write_json(path, obj)


# ============================================================================== R5 build
def r5build(check=False):
    st = pl.read_parquet(L.OUT_BASE / "stmt.parquet")
    allst = L.statements().select("srow", "kind", "src_row")
    s2 = st.select("srow", "goal_no", "regime_src").with_row_index("k").join(allst, on="srow", how="left").sort("k")
    reg_p = {p: L.period_regime(p) for p in st["goal_no"].unique().to_list()}
    models = ["bge_small"] if check else ["gte_modernbert"]
    for model in models:
        raw = EM.statement_embeddings(model, s2.select("kind", "src_row"))
        Z = np.zeros((s2.height, L.D), dtype=np.float32)
        tgt = s2["goal_no"].to_numpy()
        for p, r in reg_p.items():
            m = tgt == p
            Z[m] = wunit(raw[m], r, model)
        if check:
            Z0 = np.load(L.OUT_BASE / "stmt_z.npy").astype(np.float32)
            d = np.abs(Z.astype(np.float16).astype(np.float32) - Z0).max()
            print(f"bge rebuild vs round-1 stmt_z: max abs diff {d:.2e} (fp16 rounding)")
            return
        ZSa = np.load(L.ED / f"statements_style_resid_period32_{model}.npy", mmap_mode="r")
        ZS = np.full((s2.height, L.D), np.nan, dtype=np.float32)
        same = np.array([reg_p[p] == r for p, r in zip(s2["goal_no"].to_list(), s2["regime_src"].to_list())])
        sr = s2["srow"].to_numpy()
        o = np.argsort(sr[same])
        ZS[np.flatnonzero(same)[o]] = np.asarray(ZSa[sr[same][o]], dtype=np.float32)
        out = L.OUT_BASE / "r2_gte"
        out.mkdir(parents=True, exist_ok=True)
        np.save(out / "stmt_z.npy", Z.astype(np.float16))
        np.save(out / "stmt_zs.npy", ZS.astype(np.float16))
        for f in ("stmt.parquet", "kickoffs.parquet", "kick_msgs.parquet", "projects.parquet", "human_msgs.parquet",
                  "first_plans.parquet", "g26_leader.json"):
            shutil.copy2(L.OUT_BASE / f, out / f)
        print(f"wrote {out} ({s2.height} statements, {model})")


# ============================================================================== shared read-out estimator (R3, R2)
def ledger_reads(message_ids) -> pl.DataFrame:
    """(message_id, agent, t_rc, ment) for every non-reserved receiving call of the messages."""
    it = pl.read_parquet(L.SHARED / "context_ledger_items.parquet", columns=["turn_id", "message_id", "ment"]).filter(
        pl.col("message_id").is_in(list(message_ids)))
    tu = pl.read_parquet(L.SHARED / "context_ledger_turns.parquet", columns=["turn_id", "agent", "t_call", "holdout"])
    r = it.join(tu, on="turn_id", how="inner").filter(~pl.col("holdout") & (pl.col("agent") != CC))
    return r.group_by("message_id", "agent").agg(pl.col("t_call").min().alias("t_rc"), pl.col("ment").any().alias("ment"))


_PC = None


def agent_chat() -> pl.DataFrame:
    """Agent chat messages with producing-call times (non-reserved)."""
    global _PC
    if _PC is None:
        pc = pl.read_parquet(L.SHARED / "producing_calls.parquet",
                             columns=["message_id", "agent", "t", "pt_date", "goal_no", "holdout", "t_call_prod"])
        _PC = pc.filter(~pl.col("holdout") & (pl.col("agent") != CC)).drop("holdout").sort("agent", "t")
    return _PC


def build_pairs(targets: pl.DataFrame) -> pl.DataFrame:
    """targets: target_id, message_id, t, goal_no, regime, author (or -1). Returns one row per (target, recipient, arm)
    with before/after message ids and lag; no vectors."""
    reads = ledger_reads(targets["message_id"].to_list())
    ac = agent_chat()
    rows = []
    for tg in targets.iter_rows(named=True):
        rd = reads.filter(pl.col("message_id") == tg["message_id"])
        t_m = tg["t"]
        win = ac.filter((pl.col("t") >= t_m - dt.timedelta(hours=6)) & (pl.col("t") <= t_m + dt.timedelta(minutes=60))
                        & (pl.col("goal_no") == tg["goal_no"]) & (pl.col("message_id") != tg["message_id"]))
        for r in rd.iter_rows(named=True):
            a = r["agent"]
            if a == tg["author"]:
                continue
            w = win.filter(pl.col("agent") == a)
            bef = w.filter(pl.col("t") < t_m)
            if bef.height == 0:
                continue
            b = bef.row(bef.height - 1, named=True)
            if b["pt_date"] != str(t_m.astimezone(dt.timezone(dt.timedelta(hours=-8))).date()) and \
                    (t_m - b["t"]).total_seconds() > 6 * 3600:
                continue
            aft = w.filter(pl.col("t") > t_m)
            if aft.height == 0:
                continue
            isread = (aft["t_call_prod"] >= r["t_rc"]).to_numpy()
            for arm, mask in (("read", isread), ("inflight", ~isread)):
                if mask.any():
                    x = aft.row(int(np.flatnonzero(mask)[0]), named=True)
                    rows.append({"target_id": tg["target_id"], "goal_no": tg["goal_no"], "regime": tg["regime"], "agent": a,
                                 "ment": r["ment"], "arm": arm, "before_id": b["message_id"], "after_id": x["message_id"],
                                 "lag_s": (x["t"] - t_m).total_seconds(), "read_lag_s": (r["t_rc"] - t_m).total_seconds(),
                                 "t_before": b["t"], "t_after": x["t"]})
    return pl.DataFrame(rows)


def pair_deltas(pairs, targets, decoys_of, model, Zover=None):
    """Δ per pair. decoys_of(target_id) -> (k x d) decoy matrix. Zover: optional dict message_id -> vector (synthetic)."""
    if Zover is None:
        ids = list(set(pairs["before_id"].to_list()) | set(pairs["after_id"].to_list()))
        reg = dict(zip(pairs["before_id"].to_list() + pairs["after_id"].to_list(), pairs["regime"].to_list() * 2))
        V = chat_vecs(ids, [reg[i] for i in ids], model)
        Zover = dict(zip(ids, V))
    tv = {r["target_id"]: np.asarray(r["vec"], float) for r in targets.iter_rows(named=True)}
    out = np.full(pairs.height, np.nan)
    araw = np.full(pairs.height, np.nan)
    for k, r in enumerate(pairs.iter_rows(named=True)):
        zb, za = Zover.get(r["before_id"]), Zover.get(r["after_id"])
        if zb is None or za is None or not (np.all(np.isfinite(zb)) and np.all(np.isfinite(za))):
            continue
        e = tv[r["target_id"]]
        D = decoys_of(r["target_id"])
        dz = za - zb
        araw[k] = dz @ e
        out[k] = araw[k] - float((D @ dz).mean())
    return pairs.with_columns(pl.Series("a", araw), pl.Series("delta", out))


def lag_bin(l):
    return int(np.searchsorted(LAG_BINS, l, side="right") - 1)


def summarize(P: pl.DataFrame, n_boot=2000, rng=None) -> dict:
    """R*-A (read arm across targets) and R*-B (matched-lag read minus in-flight), message-cluster bootstrap
    (multinomial target weights)."""
    rng = rng if rng is not None else np.random.default_rng(542)
    P = P.filter(pl.col("delta").is_not_nan() & pl.col("delta").is_not_null())
    P = P.with_columns(pl.col("lag_s").map_elements(lag_bin, return_dtype=pl.Int64).alias("bin"))
    age = ((P["t_after"] - P["t_before"]).dt.total_microseconds() / 1e6 - P["lag_s"]).to_numpy()
    abin = np.searchsorted(AGE_BINS, age, side="right") - 1
    nA = len(AGE_BINS) - 1
    tids = sorted(P["target_id"].unique().to_list())
    tix = {t: k for k, t in enumerate(tids)}
    ti = np.array([tix[t] for t in P["target_id"].to_list()], int)
    rd = (P["arm"] == "read").to_numpy()
    b = P["bin"].to_numpy()
    d = P["delta"].to_numpy()
    nT, nB0 = len(tids), len(LAG_BINS) - 1
    nB = nB0 * nA
    inb0 = (b >= 0) & (b < nB0)
    b = np.where(inb0, b * nA + abin, -1)                 # cell = (after-lag bin, before-age bin)
    # per target sums for the read arm, and per (target, bin, arm) sums
    rs = np.bincount(ti[rd], d[rd], nT); rc = np.bincount(ti[rd], None, nT)
    S = np.zeros((2, nT, nB)); N = np.zeros((2, nT, nB))
    inb = (b >= 0) & (b < nB)          # matched-lag contrast uses lags < 900 s; the read arm (A) uses all pairs <= 60 min
    for arm, m in ((0, rd & inb), (1, ~rd & inb)):
        np.add.at(S[arm], (ti[m], b[m]), d[m]); np.add.at(N[arm], (ti[m], b[m]), 1)
    has = rc > 0
    mt = np.where(has, rs / np.maximum(rc, 1), np.nan)

    def stat(w):
        ww = w[has]
        A = float(np.sum(ww * mt[has]) / ww.sum()) if ww.sum() else np.nan
        med = float(np.median(np.repeat(mt[has], ww.astype(int)))) if ww.sum() else np.nan
        Sr, Nr = (w[:, None] * S[0]).sum(0), (w[:, None] * N[0]).sum(0)
        Si, Ni = (w[:, None] * S[1]).sum(0), (w[:, None] * N[1]).sum(0)
        ok = (Nr > 0) & (Ni > 0)
        if not ok.any():
            return A, np.nan, np.nan, np.nan, med
        xr, xi, wt = Sr[ok] / Nr[ok], Si[ok] / Ni[ok], Ni[ok]
        return A, float(np.average(xr - xi, weights=wt)), float(np.average(xr, weights=wt)), float(np.average(xi, weights=wt)), med
    obs = stat(np.ones(nT))
    boots = np.array([stat(rng.multinomial(nT, np.full(nT, 1 / nT)).astype(float)) for _ in range(n_boot)])
    per_t = mt[has]
    npos = int((per_t > 0).sum())
    sign_p = float(stats.binomtest(npos, len(per_t), 0.5, alternative="greater").pvalue) if len(per_t) else np.nan
    ci = lambda j: [float(np.nanpercentile(boots[:, j], 5)), float(np.nanpercentile(boots[:, j], 95))]  # noqa: E731
    R = P.filter(pl.col("arm") == "read")
    named = R.filter(pl.col("ment"))["delta"].to_numpy()
    unnamed = R.filter(~pl.col("ment"))["delta"].to_numpy()
    return {"n_targets_read": int(len(per_t)), "n_pairs_read": int(rd.sum()), "n_pairs_inflight": int((~rd).sum()),
            "n_targets_with_inflight": int(len(set(ti[~rd].tolist()))),
            "A_median": obs[4], "A_mean": obs[0], "A_mean_ci90": ci(0), "A_pos_rate": float(npos / max(1, len(per_t))),
            "A_sign_p": sign_p,
            "B_C": obs[1], "B_C_ci90": ci(1), "B_read_matched": obs[2], "B_inflight_matched": obs[3],
            "B_convergence_share": (obs[3] / obs[2]) if np.isfinite(obs[2]) and obs[2] != 0 else None,
            "named_mean": float(named.mean()) if len(named) else None, "unnamed_mean": float(unnamed.mean()) if len(unnamed) else None,
            "n_named": int(len(named)), "n_unnamed": int(len(unnamed)),
            "cells": {f"lag{LAG_BINS[k // nA]}_age{int(AGE_BINS[k % nA])}": {
                "read_n": int(N[0][:, k].sum()), "inflight_n": int(N[1][:, k].sum()),
                "read_mean": float(S[0][:, k].sum() / N[0][:, k].sum()) if N[0][:, k].sum() else None,
                "inflight_mean": float(S[1][:, k].sum() / N[1][:, k].sum()) if N[1][:, k].sum() else None}
                for k in range(nB) if N[1][:, k].sum()},
            "paired": paired_within(P, rng, n_boot)}


def paired_within(P, rng, n_boot):
    """Secondary (Amendment R2-1): agents with both arms for one target share the before message, so
    Δ_read - Δ_inflight = decoy-corrected alignment of the read message minus that of the in-flight message."""
    X = P.pivot(on="arm", index=["target_id", "agent"], values="delta", aggregate_function="first")
    if "read" not in X.columns or "inflight" not in X.columns:
        return {"n": 0}
    X = X.drop_nulls(["read", "inflight"])
    if X.height == 0:
        return {"n": 0}
    d = (X["read"] - X["inflight"]).to_numpy()
    tl = X["target_id"].to_list()
    ut = sorted(set(tl))
    ix = np.array([ut.index(t) for t in tl])
    sums, cnt = np.bincount(ix, d, len(ut)), np.bincount(ix, None, len(ut))
    bs = []
    for _ in range(n_boot):
        w = rng.multinomial(len(ut), np.full(len(ut), 1 / len(ut)))
        bs.append((w * sums).sum() / max(1e-9, (w * cnt).sum()))
    return {"n": int(len(d)), "n_targets": len(ut), "mean": float(d.mean()), "ci90": [float(np.percentile(bs, 5)), float(np.percentile(bs, 95))],
            "pos_rate": float(np.mean(d > 0))}


def named_diff_ci(P, n_boot=2000, rng=None):
    rng = rng if rng is not None else np.random.default_rng(543)
    rd = P.filter((pl.col("arm") == "read") & pl.col("delta").is_not_nan())
    tids = np.array(sorted(rd["target_id"].unique().to_list()))
    by_t = {t: rd.filter(pl.col("target_id") == t) for t in tids}

    def d(sample):
        R = pl.concat([by_t[t] for t in sample])
        a, b = R.filter(pl.col("ment"))["delta"], R.filter(~pl.col("ment"))["delta"]
        return (a.mean() - b.mean()) if a.len() and b.len() else np.nan
    obs = d(tids)
    bs = np.array([d(rng.choice(tids, len(tids), replace=True)) for _ in range(n_boot)], dtype=float)
    return {"diff": obs, "ci90": [float(np.nanpercentile(bs, 5)), float(np.nanpercentile(bs, 95))]}


# ============================================================================== target sets
def human_targets():
    hm = pl.read_parquet(L.OUT_BASE / "human_msgs.parquet").filter(pl.col("goal_no").is_in(L.eligible()))
    reg = {p: L.period_regime(p) for p in L.eligible()}
    return hm.select(pl.col("message_id").alias("target_id"), "message_id", "t", "goal_no", "length").with_columns(
        pl.col("goal_no").replace_strict(reg, return_dtype=pl.String).alias("regime"), pl.lit(-1).alias("author"))


def plan_targets():
    fp = pl.read_parquet(L.OUT_BASE / "first_plans.parquet").filter(pl.col("goal_no").is_in(L.eligible()))
    fp = fp.unique(subset=["message_id"], keep="first", maintain_order=True)
    reg = {p: L.period_regime(p) for p in L.eligible()}
    return fp.select(pl.col("message_id").alias("target_id"), "message_id", "t", "goal_no", "scope", "room",
                     pl.col("agent").alias("author")).with_columns(
        pl.col("goal_no").replace_strict(reg, return_dtype=pl.String).alias("regime"))


def human_decoys(T, model):
    """Decoys per human message: other human messages, same regime, other goal period, length ratio 0.5-2 (<= 50)."""
    V = chat_vecs(T["message_id"].to_list(), T["regime"].to_list(), model)
    T = T.with_columns(pl.Series("vec", list(V)))
    rng = np.random.default_rng(54)
    reg, gno, ln = T["regime"].to_numpy(), T["goal_no"].to_numpy(), T["length"].to_numpy()
    ok = np.all(np.isfinite(V), axis=1)
    dec = {}
    for j, tid in enumerate(T["target_id"].to_list()):
        c = [i for i in range(len(T)) if i != j and ok[i] and reg[i] == reg[j] and gno[i] != gno[j] and 0.5 <= ln[i] / ln[j] <= 2]
        if len(c) < 5:
            c = [i for i in range(len(T)) if i != j and ok[i] and reg[i] == reg[j] and gno[i] != gno[j]]
        c = rng.choice(c, min(50, len(c)), replace=False) if len(c) else []
        dec[tid] = V[np.asarray(c, int)] if len(c) else np.zeros((0, L.D))
    T = T.filter(pl.Series(ok))
    return T, dec


def plan_decoys(T, model):
    """Decoys per plan: other agents' >= 40-word chat messages on the same day 1 (minus the plan); the recipient's own
    messages are not removed per recipient (pooled decoys; they enter only as a mean direction)."""
    tf = pl.read_parquet(L.SHARED / "text_features.parquet", columns=["message_id", "agent", "t", "pt_date", "goal_no", "words"])
    V = chat_vecs(T["message_id"].to_list(), T["regime"].to_list(), model)
    T = T.with_columns(pl.Series("vec", list(V)))
    dec = {}
    for r in T.iter_rows(named=True):
        day = r["t"].astimezone(dt.timezone(dt.timedelta(hours=-8))).date()
        c = tf.filter((pl.col("goal_no") == r["goal_no"]) & (pl.col("words") >= 40) & (pl.col("agent") != CC)
                      & (pl.col("message_id") != r["message_id"]) & (pl.col("agent") != r["author"]))
        c = c.filter(pl.col("pt_date") == str(day))
        D = chat_vecs(c["message_id"].to_list(), [r["regime"]] * c.height, model) if c.height else np.zeros((0, L.D))
        D = D[np.all(np.isfinite(D), axis=1)] if len(D) else D
        dec[r["target_id"]] = D
    ok = [len(dec[t]) >= 3 and np.all(np.isfinite(v)) for t, v in zip(T["target_id"].to_list(), V)]
    return T.filter(pl.Series(ok)), dec


# ============================================================================== R3 / R2 runs
def run_readout(kind: str):
    T0 = human_targets() if kind == "r3" else plan_targets()
    pairs_path = R2 / f"{kind}_pairs.parquet"
    if pairs_path.exists():
        pairs = pl.read_parquet(pairs_path)
    else:
        pairs = build_pairs(T0)
        R2.mkdir(parents=True, exist_ok=True)
        pairs.write_parquet(pairs_path)
    res = {"n_targets": T0.height, "n_pairs": pairs.height}
    for model in MODELS:
        T, dec = (human_decoys if kind == "r3" else plan_decoys)(T0, model)
        P = pairs.filter(pl.col("target_id").is_in(T["target_id"].to_list()))
        P = pair_deltas(P, T, lambda t: dec[t], model)
        P.select("target_id", "goal_no", "regime", "agent", "ment", "arm", "lag_s", "read_lag_s", "a", "delta").write_parquet(
            R2 / f"{kind}_deltas_{model}.parquet")
        s = summarize(P)
        s["named_diff"] = named_diff_ci(P)
        s["by_regime"] = {}
        for rg in ("I", "II", "III"):
            Pr = P.filter(pl.col("regime") == rg)
            if Pr.filter(pl.col("arm") == "read").height >= 10:
                q = summarize(Pr, n_boot=500)
                s["by_regime"][rg] = {k: q[k] for k in ("n_targets_read", "A_median", "A_mean", "A_mean_ci90", "B_C", "B_C_ci90",
                                                        "n_pairs_inflight")}
        if kind == "r2":
            s["R2C_two_room"] = never_read_control(T, dec, model)
        res[model] = s
        print(kind, model, {k: v for k, v in s.items() if k not in ("lag_bins", "by_regime")})
    jdump(R2 / f"{kind}.json", res)
    return res


def never_read_control(T, dec, model):
    """R2-C: room-scope plans; other-room agents (never read) over the same clock window vs same-room readers."""
    ac = agent_chat()
    rt = pl.read_parquet(L.SHARED / "rooms_timeline.parquet")
    out = []
    for r in T.filter(pl.col("scope").str.starts_with("room")).iter_rows(named=True):
        t_m = r["t"]
        pairs = pl.read_parquet(R2 / "r2_pairs.parquet").filter((pl.col("target_id") == r["target_id"]) & (pl.col("arm") == "read"))
        if pairs.height == 0:
            continue
        lag = float(np.median(pairs["read_lag_s"].to_numpy()))
        inroom = rt.filter((pl.col("t_start") <= t_m) & (pl.col("t_end") >= t_m))
        other = set(inroom.filter(pl.col("room") != r["room"])["agent"].to_list()) - {CC}
        rows = []
        for a in other:
            w = ac.filter((pl.col("agent") == a) & (pl.col("goal_no") == r["goal_no"]))
            b = w.filter((pl.col("t") < t_m) & (pl.col("t") >= t_m - dt.timedelta(hours=6)))
            x = w.filter((pl.col("t") > t_m + dt.timedelta(seconds=lag)) & (pl.col("t") <= t_m + dt.timedelta(minutes=60)))
            if b.height and x.height:
                rows.append({"target_id": r["target_id"], "goal_no": r["goal_no"], "regime": r["regime"], "agent": a, "ment": False,
                             "arm": "never", "before_id": b["message_id"][-1], "after_id": x["message_id"][0], "lag_s": 0.0})
        if not rows:
            continue
        Pn = pair_deltas(pl.DataFrame(rows), T, lambda t: dec[t], model)
        Pr = pair_deltas(pairs, T, lambda t: dec[t], model)
        out.append({"goal_no": r["goal_no"], "scope": r["scope"], "n_read": Pr.height, "n_never": Pn.height,
                    "read_mean": float(np.nanmean(Pr["delta"].to_numpy())), "never_mean": float(np.nanmean(Pn["delta"].to_numpy()))})
    d = [o["read_mean"] - o["never_mean"] for o in out if np.isfinite(o["read_mean"]) and np.isfinite(o["never_mean"])]
    return {"plans": out, "n": len(d), "median_diff": float(np.median(d)) if d else None,
            "pos_rate": float(np.mean(np.array(d) > 0)) if d else None}


# ============================================================================== R1: #12 debates
def debates():
    gt = pl.read_parquet(L.SHARED / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 12) & pl.col("preferred") & ~pl.col("holdout"))
    out = []
    for unit in sorted(gt["unit"].unique().to_list()):
        g = gt.filter(pl.col("unit") == unit)
        teams = g.filter((pl.col("label_kind") == "team") & pl.col("value").is_in(["gov", "opp"]))
        deb = g.filter((pl.col("label_kind") == "phase") & (pl.col("value") == "deb"))
        if deb.height == 0 or teams.height == 0:
            continue
        out.append({"unit": unit, "t_draft": teams["t_valid_from"].min(), "t_deb0": deb["t_valid_from"].min(),
                    "t_deb1": deb["t_valid_to"].max(), "team": dict(zip(teams["agent"].to_list(), teams["value"].to_list()))})
    return out


def team_Q(V, lab):
    lab = np.asarray(lab)
    G = V @ V.T
    n = len(V)
    iu = np.triu_indices(n, 1)
    same = lab[iu[0]] == lab[iu[1]]
    if same.sum() == 0 or (~same).sum() == 0:
        return np.nan
    return float(G[iu][same].mean() - G[iu][~same].mean())


def r1_debate_units(st, Z, min_n=2):
    """Per debate: agents with >= min_n statements in both deb and pre-draft windows; their unit mean vectors."""
    s = st.with_row_index("i").filter((pl.col("goal_no") == 12) & (pl.col("src_goal") == 12))
    units = []
    for d in debates():
        deb = s.filter((pl.col("t") >= d["t_deb0"]) & (pl.col("t") < d["t_deb1"]))
        pre = s.filter((pl.col("t") >= d["t_draft"] - dt.timedelta(minutes=30)) & (pl.col("t") < d["t_draft"]))
        ag, Vd, Vp, lab, nd, npre = [], [], [], [], [], []
        for a, tm in d["team"].items():
            x = deb.filter(pl.col("agent") == a)["i"].to_numpy()
            y = pre.filter(pl.col("agent") == a)["i"].to_numpy()
            if len(x) >= min_n and len(y) >= min_n:
                ag.append(a); lab.append(tm); nd.append(len(x)); npre.append(len(y))
                Vd.append(E.unit(Z[x].mean(0))); Vp.append(E.unit(Z[y].mean(0)))
        if len(ag) >= 4 and len(set(lab)) == 2:
            units.append({"unit": d["unit"], "agents": ag, "lab": np.array(lab), "Vd": np.vstack(Vd), "Vp": np.vstack(Vp),
                          "n_deb": nd, "n_pre": npre, "deb_idx": [deb.filter(pl.col("agent") == a)["i"].to_numpy() for a in ag],
                          "pre_idx": [pre.filter(pl.col("agent") == a)["i"].to_numpy() for a in ag]})
    return units


def r1a_stats(units, n_perm=2000, rng=None):
    rng = rng if rng is not None else np.random.default_rng(1212)
    q = np.array([team_Q(u["Vd"], u["lab"]) for u in units])
    qp = np.array([team_Q(u["Vp"], u["lab"]) for u in units])
    did = q - qp
    obs_q, obs_d = float(np.nanmean(q)), float(np.nanmean(did))
    cq = cd = 0
    for _ in range(n_perm):
        pq, pd_ = [], []
        for u in units:
            lab = rng.permutation(u["lab"])
            a, b = team_Q(u["Vd"], lab), team_Q(u["Vp"], lab)
            pq.append(a); pd_.append(a - b)
        cq += np.nanmean(pq) >= obs_q
        cd += np.nanmean(pd_) >= obs_d
    return {"n_debates": len(units), "mean_Q": obs_q, "p_Q": (cq + 1) / (n_perm + 1), "mean_Q_pre": float(np.nanmean(qp)),
            "mean_DiD": obs_d, "p_DiD": (cd + 1) / (n_perm + 1), "Q": q.tolist(), "Q_pre": qp.tolist(),
            "units": [u["unit"] for u in units], "n_agents": [len(u["agents"]) for u in units]}


def r1b_motion(st, Z, model):
    tg = pl.read_parquet(R2 / "targets.parquet")
    TV = np.load(R2 / f"targets_{model}.npy").astype(np.float32)
    tg = tg.filter((pl.col("goal_no") == 12) & pl.col("found"))
    M = wunit(TV[tg["tid"].to_numpy()], "I", model)
    s = st.with_row_index("i").filter((pl.col("goal_no") == 12) & (pl.col("src_goal") == 12))
    dmap = {d["unit"]: d for d in debates()}
    cents = []
    for u in tg["unit"].to_list():
        d = dmap.get(u)
        if d is None:
            cents.append(np.full(L.D, np.nan)); continue
        deb = s.filter((pl.col("t") >= d["t_deb0"]) & (pl.col("t") < d["t_deb1"]) & pl.col("agent").is_in(list(d["team"])))
        g = deb.group_by("agent").agg(pl.col("i")).filter(pl.col("i").list.len() >= 1)
        V = np.vstack([E.unit(Z[np.asarray(ix)].mean(0)) for ix in g["i"].to_list()]) if g.height else np.full((1, L.D), np.nan)
        cents.append(E.unit(V.mean(0)))
    C = np.vstack(cents)
    S = C @ M.T
    Sh = E.colcenter(S)
    pi = E.own_percentiles(Sh)
    t1 = E.top1(Sh)
    return {"n": int(np.isfinite(pi).sum()), "median_pi": float(np.nanmedian(pi)), "top1": float(np.nanmean(t1)),
            "pi": pi.tolist(), "units": tg["unit"].to_list(), "p_wilcoxon": E.wilcoxon_gt(pi)}


# ============================================================================== R1: #19 / #21 options
def option_targets(p, model):
    tg = pl.read_parquet(R2 / "targets.parquet").filter((pl.col("goal_no") == p) & pl.col("found"))
    TV = np.load(R2 / f"targets_{model}.npy").astype(np.float32)
    tA = wunit(TV[tg.filter(pl.col("unit") == "A")["tid"].to_numpy()], "I", model)[0]
    tB = wunit(TV[tg.filter(pl.col("unit") == "B")["tid"].to_numpy()], "I", model)[0]
    return tA, tB


def null_axes(p, model):
    el = [q for q in L.eligible() if q != p]
    K = np.vstack([goal_vec(q, "kickoff", "I", model) for q in el])
    ax = [E.unit(K[i] - K[j]) for i in range(len(K)) for j in range(i + 1, len(K))]
    return np.vstack(ax), K


def reliable_var(groups, axes, R=50, rng=None):
    """Mean over R random split-halves of the across-agent covariance of half-mean projections, per axis.
    groups: list of (n_i x d) statement matrices (plain means, no normalization)."""
    rng = rng if rng is not None else np.random.default_rng(1919)
    gs = [g for g in groups if len(g) >= 4]
    if len(gs) < 4:
        return None
    acc = np.zeros(len(axes))
    for _ in range(R):
        A, B = [], []
        for g in gs:
            o = rng.permutation(len(g))
            h = len(g) // 2
            A.append(g[o[:h]].mean(0)); B.append(g[o[h:2 * h]].mean(0))
        PA, PB = np.vstack(A) @ axes.T, np.vstack(B) @ axes.T
        PA -= PA.mean(0); PB -= PB.mean(0)
        acc += (PA * PB).sum(0) / (len(gs) - 1)
    return acc / R


def r1_options(st, Z, p, model, days=(1, 2, 3)):
    tA, tB = option_targets(p, model)
    u = E.unit(tA - tB)
    NA, K = null_axes(p, model)
    axes = np.vstack([u, NA])
    s = st.with_row_index("i").filter((pl.col("goal_no") == p) & (pl.col("src_goal") == p) & (pl.col("day") >= 1) & ~pl.col("pre_kick"))
    rv, exA, exB = [], [], []
    for d in days:
        sd = s.filter(pl.col("day") == d)
        g = sd.group_by("agent").agg(pl.col("i"))
        groups = [Z[np.asarray(ix)] for ix in g["i"].to_list()]
        v = reliable_var(groups, axes)
        if v is not None:
            rv.append(v)
        gg = g.filter(pl.col("i").list.len() >= 3)
        if gg.height >= 3:
            V = np.vstack([E.unit(Z[np.asarray(ix)].mean(0)) for ix in gg["i"].to_list()])
            dec = (V @ K.T).mean()
            exA.append(float((V @ tA).mean() - dec)); exB.append(float((V @ tB).mean() - dec))
    rv = np.mean(rv, axis=0) if rv else None
    pct = float(np.mean(rv[1:] < rv[0])) if rv is not None else np.nan
    # sequence over all active days
    seq = []
    for d in sorted(s["day"].unique().to_list()):
        g = s.filter(pl.col("day") == d).group_by("agent").agg(pl.col("i")).filter(pl.col("i").list.len() >= 3)
        if g.height >= 3:
            V = np.vstack([E.unit(Z[np.asarray(ix)].mean(0)) for ix in g["i"].to_list()])
            seq.append((d, float(V.mean(0) @ u)))
    rho, pr = (stats.spearmanr([a for a, _ in seq], [b for _, b in seq]) if len(seq) >= 4 else (np.nan, np.nan))
    return {"cos_tA_tB": float(tA @ tB), "excess_A": float(np.mean(exA)) if exA else None, "excess_B": float(np.mean(exB)) if exB else None,
            "excess_A_by_day": exA, "excess_B_by_day": exB, "domain_pct": pct, "relvar_u": float(rv[0]) if rv is not None else None,
            "relvar_null_median": float(np.median(rv[1:])) if rv is not None else None, "n_null_axes": int(len(NA)),
            "seq": seq, "seq_rho": float(rho) if np.isfinite(rho) else None, "seq_p_two": float(pr) if np.isfinite(pr) else None}


def run_r1():
    res = {}
    for model in MODELS:
        st, Z = stmt_Z(model)
        units = r1_debate_units(st, Z)
        r = {"R1A": r1a_stats(units), "R1B": r1b_motion(st, Z, model)}
        for p in (19, 21):
            r[f"G{p}"] = r1_options(st, Z, p, model)
        res[model] = r
        print("R1", model, {k: (v if k != "R1A" else {kk: vv for kk, vv in v.items() if kk in ("n_debates", "mean_Q", "p_Q", "mean_DiD", "p_DiD")})
                             for k, v in r.items()})
    jdump(R2 / "r1.json", res)
    return res


# ============================================================================== synthetic validation (S6-S8)
def synth_vectors(ids, agent_of, rng, rho_agent=0.35, extra=None):
    """Unit 32-d vectors: z = unit(sqrt(rho) o_agent + sqrt(1-rho) eps + extra). Returns dict id -> z."""
    agents = sorted(set(agent_of.values()))
    O = {a: E.unit(rng.standard_normal(L.D)) for a in agents}
    out = {}
    for i in ids:
        z = np.sqrt(rho_agent) * O[agent_of[i]] + np.sqrt(1 - rho_agent) * E.unit(rng.standard_normal(L.D))
        if extra is not None and i in extra:
            z = z + extra[i]
        out[i] = E.unit(z)
    return out


def s6(kind="r3", reps=40, amps=(0.05, 0.15, 0.3), seed=6):
    """Read-out (WH) vs convergence (WC) vs none (W0) on the real pair skeleton with the real target and decoy vectors."""
    T0 = human_targets() if kind == "r3" else plan_targets()
    pairs = pl.read_parquet(R2 / f"{kind}_pairs.parquet") if (R2 / f"{kind}_pairs.parquet").exists() else build_pairs(T0)
    if not (R2 / f"{kind}_pairs.parquet").exists():
        R2.mkdir(parents=True, exist_ok=True)
        pairs.write_parquet(R2 / f"{kind}_pairs.parquet")
    T, dec = (human_decoys if kind == "r3" else plan_decoys)(T0, "bge_small")
    P = pairs.filter(pl.col("target_id").is_in(T["target_id"].to_list()))
    tvec = {k: np.asarray(v, float) for k, v in zip(T["target_id"].to_list(), T["vec"].to_list())}
    ids = list(set(P["before_id"].to_list()) | set(P["after_id"].to_list()))
    agent_of = dict(zip(P["before_id"].to_list() + P["after_id"].to_list(), P["agent"].to_list() * 2))
    # message times relative to each target: a message gets a pulse toward target m if (WH) it is an after-message of a
    # read pair of m, or (WC) it is posted after t_m - 10 min (before messages within 10 min of m included)
    rng = np.random.default_rng(seed)
    out = {}
    for world in ("W0", "WH", "WC"):
        for A in ([x for x in amps if x > 0] if world != "W0" else (0.0,)):
            fa, fb, fp_, means, cm = 0, 0, 0, [], []
            nrep = reps * 5 if world == "W0" else reps
            for _ in range(nrep):
                pulsed = {}
                if A > 0:
                    for r in P.iter_rows(named=True):
                        t = r["target_id"]
                        if world == "WH" and r["arm"] == "read":
                            pulsed.setdefault(r["after_id"], set()).add(t)
                        if world == "WC":
                            pulsed.setdefault(r["after_id"], set()).add(t)
                            if (r["t_after"] - r["t_before"]).total_seconds() < 600 + r["lag_s"]:
                                pulsed.setdefault(r["before_id"], set()).add(t)
                extra = {m: A * sum(tvec[t] for t in ts) for m, ts in pulsed.items()}
                Zs = synth_vectors(ids, agent_of, rng, extra=extra)
                Q = pair_deltas(P, T, lambda t: dec[t], "bge_small", Zover=Zs)
                s = summarize(Q, n_boot=200, rng=rng)
                fa += s["A_sign_p"] < 0.05
                fb += s["B_C_ci90"][0] > 0
                fp_ += (s["paired"].get("n", 0) > 0) and s["paired"]["ci90"][0] > 0
                means.append(s["A_mean"]); cm.append(s["B_C"])
            out[f"{world}_A{A}"] = {"reps": nrep, "rate_A": fa / nrep, "rate_B": fb / nrep, "rate_paired": fp_ / nrep, "mean_delta": float(np.nanmean(means)),
                                    "mean_C": float(np.nanmean(cm))}
            print(kind, world, A, out[f"{world}_A{A}"])
    return out


def s7(reps=200, ws=(0.0, 0.05, 0.1, 0.2, 0.3), seed=7):
    st, Z = stmt_Z("bge_small")
    units = r1_debate_units(st, Z)
    rng = np.random.default_rng(seed)
    out = {}
    for w in ws:
        fq = fd = 0
        qs = []
        for _ in range(reps):
            su = []
            for u in units:
                n = len(u["agents"])
                O = [E.unit(rng.standard_normal(L.D)) for _ in range(n)]
                tdir = E.unit(rng.standard_normal(L.D))
                Vd, Vp = [], []
                for k in range(n):
                    sg = 1.0 if u["lab"][k] == u["lab"][0] else -1.0

                    def draw(m, team):
                        X = np.sqrt(0.35) * O[k] + np.sqrt(0.65) * E.unit(rng.standard_normal((m, L.D)))
                        if team:
                            X = X + w * sg * tdir
                        return E.unit(E.unit(X).mean(0))
                    Vd.append(draw(u["n_deb"][k], True)); Vp.append(draw(u["n_pre"][k], False))
                su.append({**u, "Vd": np.vstack(Vd), "Vp": np.vstack(Vp)})
            r = r1a_stats(su, n_perm=200, rng=rng)
            qs.append(r["mean_Q"])
            fq += r["p_Q"] < 0.05
            fd += r["p_DiD"] < 0.1
        out[f"w{w}"] = {"reps": reps, "rate_Q": fq / reps, "rate_DiD": fd / reps, "mean_Q": float(np.mean(qs))}
        print("S7", w, out[f"w{w}"])
    return out


def s8(reps=200, fs=(0.0, 0.03, 0.05, 0.1, 0.3), seed=8):
    st, _ = stmt_Z("bge_small")
    rng = np.random.default_rng(seed)
    out = {}
    for p in (19, 21):
        tA, tB = option_targets(p, "bge_small")
        u = E.unit(tA - tB)
        NA, _ = null_axes(p, "bge_small")
        axes = np.vstack([u, NA])
        mix = E.unit(tA + tB)
        s = st.filter((pl.col("goal_no") == p) & (pl.col("src_goal") == p) & pl.col("day").is_in([1, 2, 3]) & ~pl.col("pre_kick"))
        cnt = s.group_by("day", "agent").len()
        for world in ("mixed", "domains"):
            for f in fs:
                if world == "mixed" and f != fs[-1]:
                    continue
                hits = 0
                gap = []
                for _ in range(reps):
                    agents = sorted(cnt["agent"].unique().to_list())
                    O = {a: E.unit(rng.standard_normal(L.D)) for a in agents}
                    side = {a: (tA if k % 2 == 0 else tB) for k, a in enumerate(rng.permutation(agents))}
                    rvs = []
                    for d in (1, 2, 3):
                        groups = []
                        for a, n in cnt.filter(pl.col("day") == d).select("agent", "len").iter_rows():
                            tgt = mix if world == "mixed" else side[a]
                            X = np.sqrt(0.35) * O[a] + np.sqrt(0.65) * E.unit(rng.standard_normal((n, L.D))) + f * 3 * tgt
                            groups.append(E.unit(X))
                            if world == "domains" and d == 1:
                                v_ = E.unit(groups[-1].mean(0))
                                oth = tB if side[a] is tA else tA
                                gap.append(float(v_ @ side[a] - v_ @ oth))
                        v = reliable_var(groups, axes, R=10, rng=rng)
                        if v is not None:
                            rvs.append(v)
                    rv = np.mean(rvs, axis=0)
                    hits += np.mean(rv[1:] < rv[0]) >= 0.9
                out[f"G{p}_{world}_f{f}"] = {"reps": reps, "rate_pct_ge_0.9": hits / reps,
                                             "agent_side_gap_day1": float(np.mean(gap)) if gap else None}
                print("S8", p, world, f, out[f"G{p}_{world}_f{f}"])
    return out


def run_synth(which):
    res = json.loads((R2 / "synthetic.json").read_text()) if (R2 / "synthetic.json").exists() else {}
    if "s6" in which:
        res["S6_r3"] = s6("r3")
        res["S6_r2"] = s6("r2")
    if "s7" in which:
        res["S7"] = s7()
    if "s8" in which:
        res["S8"] = s8()
    jdump(R2 / "synthetic.json", res)



# ============================================================================== per_period_estimates
def write_r2_estimates():
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import estimates as ES
    pu = pl.read_parquet(L.SHARED / "period_units.parquet").sort("goal_no", "seq")
    first_unit = {g: u for g, u in zip(pu["goal_no"].to_list(), pu["unit_id"].to_list())} if False else \
        {g: pu.filter(pl.col("goal_no") == g)["unit_id"][0] for g in pu["goal_no"].unique().to_list()}
    ch = {"bge_small": "content_bge", "gte_modernbert": "content_gte"}
    rows = []
    # R5 / P1 per period, both models (day-1 unit)
    for model, base in (("bge_small", L.OUT_BASE), ("gte_modernbert", L.OUT_BASE / "r2_gte")):
        per = pl.read_parquet(base / "NE34" / "periods.parquet")
        for r in per.iter_rows(named=True):
            if r["pi"] is None or not np.isfinite(r["pi"]):
                continue
            rows.append({"period_unit": first_unit[r["goal_no"]], "goal_no": r["goal_no"], "statistic": "own_kickoff_percentile",
                         "channel": ch[model], "estimate": r["pi"], "ci_lo": None, "ci_hi": None, "n": r["n_agents"], "n_kind": "agents",
                         "method": "day-1 agent-mean centroid vs 33 kickoffs, genericness-corrected own percentile (H54 P1)",
                         "null": "32 decoy kickoffs (uniform under R0)", "role": "replication", "ci_kind": "none",
                         "unit_local": "day 1 after the kickoff", "source": f"{base.name}/NE34/periods.parquet", "post_hoc": False})
        g51 = json.loads((base / "G51" / "native.json").read_text())
        rows.append({"period_unit": "G51", "goal_no": 51, "statistic": "private_goal_role_swap_accuracy", "channel": ch[model],
                     "estimate": g51["swap_accuracy"], "ci_lo": None, "ci_hi": None, "n": g51["n_pairs"], "n_kind": "agent pairs",
                     "method": "role-swap pair accuracy, first day per agent on its current goal (H54 N1)",
                     "null": f"role permutation p = {g51['p_perm']:.4f}", "role": "native", "ci_kind": "none",
                     "source": f"{base.name}/G51/native.json", "post_hoc": False})
        ne = g51["NE38"]["new"]
        rows.append({"period_unit": "local:NE38", "goal_no": 51, "statistic": "ne38_did_new_goal_alignment", "channel": ch[model],
                     "estimate": ne["did"], "ci_lo": ne["ci95"][0], "ci_hi": ne["ci95"][1], "ci_level": 0.95, "ci_kind": "percentile",
                     "n": ne["n_pre_days"] + ne["n_post_days"], "n_kind": "Opus 5 day segments",
                     "method": "DiD of alignment with the new goal, Opus 5 vs other agents, day bootstrap (H54 N1b)",
                     "null": "0", "role": "native", "unit_local": "2026-07-24..2026-08-07", "source": f"{base.name}/G51/native.json",
                     "post_hoc": False})
    # R3 per period (human-message read-out re-quench, read arm), both models
    for model in MODELS:
        D = pl.read_parquet(R2 / f"r3_deltas_{model}.parquet").filter((pl.col("arm") == "read") & pl.col("delta").is_not_nan())
        for g in sorted(D["goal_no"].unique().to_list()):
            x = D.filter(pl.col("goal_no") == g)
            pt = x.group_by("target_id").agg(pl.col("delta").mean())["delta"].to_numpy()
            if len(pt) < 5:
                continue
            rng = np.random.default_rng(g)
            bs = [rng.choice(pt, len(pt)).mean() for _ in range(2000)]
            rows.append({"period_unit": ES.map_unit(g) or f"G{g:02d}", "goal_no": g, "statistic": "readout_requench_delta",
                         "channel": ch[model], "estimate": float(pt.mean()), "ci_lo": float(np.percentile(bs, 5)),
                         "ci_hi": float(np.percentile(bs, 95)), "ci_level": 0.90, "ci_kind": "percentile", "n": len(pt),
                         "n_kind": "human messages", "method": "first chat message after the ledger read-out call minus last before, "
                         "decoy-corrected alignment with the message (H54 R3-A), message bootstrap", "null": "0 (decoy messages)",
                         "role": "replication", "source": "r2/r3_deltas", "post_hoc": False})
    # R1 natives
    r1 = json.loads((R2 / "r1.json").read_text())
    for model in MODELS:
        a = r1[model]["R1A"]
        b = r1[model]["R1B"]
        rows += [{"period_unit": "12a", "goal_no": 12, "statistic": "debate_team_domain_Q", "channel": ch[model], "estimate": a["mean_Q"],
                  "ci_lo": None, "ci_hi": None, "n": a["n_debates"], "n_kind": "debates", "ci_kind": "none",
                  "method": "within- minus between-team pair cosine of debaters in the deb phase, mean over debates (H54 R1-A)",
                  "null": f"team re-split permutation p = {a['p_Q']:.3f}; DiD vs pre-draft {a['mean_DiD']:+.3f} (p = {a['p_DiD']:.3f})",
                  "role": "native", "source": "r2/r1.json", "post_hoc": False},
                 {"period_unit": "12a", "goal_no": 12, "statistic": "debate_own_motion_percentile", "channel": ch[model],
                  "estimate": b["median_pi"], "ci_lo": None, "ci_hi": None, "n": b["n"], "n_kind": "debates", "ci_kind": "none",
                  "method": "median genericness-corrected own-motion percentile of the deb-phase centroid (H54 R1-B)",
                  "null": f"other debates' motions; Wilcoxon p = {b['p_wilcoxon']:.4f}", "role": "native", "source": "r2/r1.json",
                  "post_hoc": False}]
        for g in (19, 21):
            o = r1[model][f"G{g}"]
            rows.append({"period_unit": first_unit[g], "goal_no": g, "statistic": "two_option_domain_percentile", "channel": ch[model],
                         "estimate": o["domain_pct"], "ci_lo": None, "ci_hi": None, "n": o["n_null_axes"], "n_kind": "null axes",
                         "ci_kind": "none", "method": "reliable between-agent variance along t_A - t_B vs kickoff-difference axes, days 1-3 (H54 R1-D)",
                         "null": "percentile >= 0.9 = domains (12% under one mixed target)", "role": "native", "unit_local": "days 1-3",
                         "source": "r2/r1.json", "post_hoc": False})
    out = ES.write_estimates(rows, hypothesis="H54")
    print(f"wrote {out.height} H54 rows to per_period_estimates")

# ============================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["r5build", "synth", "r3", "r2", "r1", "estimates"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", default="s6,s7,s8")
    a = ap.parse_args()
    if L.MODEL != "bge_small":
        sys.exit("round2.py runs with the default H54_MODEL (it handles both models itself)")
    R2.mkdir(parents=True, exist_ok=True)
    if a.cmd == "r5build":
        r5build(check=a.check)
    elif a.cmd == "synth":
        run_synth(a.only.split(","))
    elif a.cmd in ("r3", "r2"):
        run_readout(a.cmd)
    elif a.cmd == "r1":
        run_r1()
    elif a.cmd == "estimates":
        write_r2_estimates()
    L.provenance(f"analysis/round2.py:{a.cmd}", ["H54 stmt + target tables", "DQ5 bge-small + gte-modernbert (chat, statements, "
                 "goal vectors, whiteners, style_resid_period32)", "context_ledger_items", "context_ledger_turns", "producing_calls",
                 "ground_truth_labels (#12)", "text_features", "rooms_timeline"], {"lag_bins_s": LAG_BINS})


if __name__ == "__main__":
    main()
