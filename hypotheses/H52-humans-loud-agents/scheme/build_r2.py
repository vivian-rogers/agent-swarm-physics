"""H52 round-2 scheme (card section "Round 2"). Reads the round-1 rows (data/processed/H52-humans-loud-agents/<P>/
rows.parquet) and shared tables; writes data/processed/H52-humans-loud-agents/r2/<P>/ (numbers and codes only).

Subcommands (run in this order; the synthetic check runs between `skeleton` and `content`/`pairvec`):
  skeleton  r2_skel.parquet  (G51, G04: per-row ages of the recipient's pre and post statements; structure only)
            r2_pairs.parquet (all 17 replication periods: read / in-flight pair skeleton; structure only)
  content   r2_content.parquet: per-row pieces of the quote-free DiD candidates (bge; gte; style-residualized)
  pairvec   r2_pairdelta.parquet: Delta and Delta_q per pair (bge, gte)
Usage: uv run python hypotheses/H52-humans-loud-agents/scheme/build_r2.py skeleton|content|pairvec [G04 ...]
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import h52lib as L  # noqa: E402
import r2lib as R  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

SH = L.SH
SKEL_PERIODS = ("G51", "G04")
N_AGENT_MSGS = 3000
SEED2 = 2026100552


def meta(p):
    return json.loads((L.OUT / p / "meta.json").read_text())


def rows(p, cols=None):
    return pl.read_parquet(L.OUT / p / "rows.parquet", columns=cols)


def outdir(p):
    d = R.R2OUT / p
    d.mkdir(parents=True, exist_ok=True)
    return d


# ============================================================================ skeleton
def skel_rows(p):
    m = meta(p)
    days = m["days"]
    L.assert_no_holdout(days, m["goal"])
    r = rows(p, ["item", "recv", "tc"])
    st, _ = L.statement_table(days, "bge_small", "white32")
    sa, stt = st["agent"].to_numpy(), st["ts"].to_numpy()
    bidx, pmask, qidx = L.window_indices(sa, stt, r["recv"].to_numpy().astype(int), r["tc"].to_numpy())
    tc = r["tc"].to_numpy()
    pre = np.where(bidx >= 0, tc[:, None] - stt[np.where(bidx >= 0, bidx, 0)], np.nan).astype(np.float32)
    post = np.where(qidx >= 0, stt[np.where(qidx >= 0, qidx, 0)] - tc[:, None], np.nan).astype(np.float32)
    cols = {"item": r["item"]}
    for k in range(L.K_BASIS):
        cols[f"pre{k}"] = pre[:, k]
    for k in range(L.K_POST):
        cols[f"post{k}"] = post[:, k]
    cols["pmask"] = pmask.sum(1).astype(np.int8)
    df = pl.DataFrame(cols)
    df.write_parquet(outdir(p) / "r2_skel.parquet", compression="zstd")
    print(p, "skel", df.height, flush=True)


def chat_with_prod(days):
    pc = pl.read_parquet(SH / "producing_calls.parquet",
                         columns=["msg", "agent", "t", "pt_date", "holdout", "t_call_prod"]).filter(
        pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
    return pc.with_columns((pl.col("t").dt.epoch("us") / 1e6).alias("ts"),
                           (pl.col("t_call_prod").dt.epoch("us") / 1e6).alias("tcp")).sort("agent", "ts")


def build_pairs(p):
    m = meta(p)
    days = m["days"]
    L.assert_no_holdout(days, m["goal"])
    r = rows(p, ["msg", "recv", "tc", "t_m", "cls", "named", "kickoff", "len", "pt_date", "sender"]).filter(
        ~pl.col("kickoff") & pl.col("cls").is_in([0, 1]))
    rng = np.random.default_rng([SEED2, m["goal"]])
    am = np.unique(r.filter(pl.col("cls") == 0)["msg"].to_numpy())
    if len(am) > N_AGENT_MSGS:
        am = np.sort(rng.choice(am, N_AGENT_MSGS, replace=False))
    r = r.filter((pl.col("cls") == 1) | pl.col("msg").is_in(am.tolist()))
    pc = chat_with_prod(days)
    out = []
    pa = pc["agent"].to_numpy(); pts = pc["ts"].to_numpy(); ptc = pc["tcp"].to_numpy()
    pmsg = pc["msg"].to_numpy().astype(np.int64); pdate = pc["pt_date"].to_numpy()
    for a in np.unique(r["recv"].to_numpy()):
        lo, hi = np.searchsorted(pa, a, "left"), np.searchsorted(pa, a, "right")
        if hi <= lo:
            continue
        T, TC, M, D = pts[lo:hi], ptc[lo:hi], pmsg[lo:hi], pdate[lo:hi]
        sub = r.filter(pl.col("recv") == a)
        tm = sub["t_m"].to_numpy(); tc = sub["tc"].to_numpy(); dd = sub["pt_date"].to_numpy()
        ib = np.searchsorted(T, tm, "left") - 1                      # last message strictly before t_m
        ia = np.searchsorted(T, tm, "right")                          # first message strictly after t_m
        for arm in ("read", "inflight"):
            if arm == "read":
                j = np.maximum(ia, np.searchsorted(np.maximum.accumulate(TC), tc, "left"))   # first after t_m with t_call_prod >= t_rc
            else:
                j = ia.copy()
            okj = j < len(T)
            jj = np.where(okj, j, 0)
            okb = ib >= 0
            bb = np.where(okb, ib, 0)
            ok = okj & okb
            ok &= (T[jj] - tm) <= 3600.0
            ok &= (tm - T[bb]) <= 6 * 3600.0
            ok &= D[bb] == dd
            if arm == "read":
                ok &= TC[jj] >= tc
            else:
                ok &= TC[jj] < tc
            if not ok.any():
                continue
            s = sub.filter(pl.Series(ok))
            out.append(s.select("msg", "recv", "cls", "named", "len", "sender", "t_m", "tc").with_columns(
                pl.lit(arm).alias("arm"), pl.Series("before_msg", M[bb[ok]]), pl.Series("after_msg", M[jj[ok]]),
                pl.Series("lag_s", (T[jj[ok]] - tm[ok]).astype(np.float32)),
                pl.Series("age_s", (tm[ok] - T[bb[ok]]).astype(np.float32))))
    P = pl.concat(out).with_columns(pl.lit(p).alias("period"), pl.lit(m["regime"]).alias("regime"))
    P.write_parquet(outdir(p) / "r2_pairs.parquet", compression="zstd")
    print(p, "pairs", P.group_by("cls", "arm").len().sort("cls", "arm").rows(), flush=True)


# ============================================================================ content candidates
def build_content(p):
    t0 = time.time()
    m = meta(p)
    days = m["days"]
    L.assert_no_holdout(days, m["goal"])
    r = rows(p, ["item", "msg", "recv", "tc", "cls", "day_idx", "kickoff", "turn_id"])
    rng = np.random.default_rng([SEED2, m["goal"], 1])
    st, V = L.statement_table(days, "bge_small", "white32")
    recv = r["recv"].to_numpy().astype(int); tc = r["tc"].to_numpy()
    bidx, pmask, qidx = L.window_indices(st["agent"].to_numpy(), st["ts"].to_numpy(), recv, tc)
    pool_df = r.select("msg", "cls", "day_idx", "kickoff").unique("msg", maintain_order=True)
    pool = {}
    for c in (0, 1, 2):
        q = pool_df.filter((pl.col("cls") == c) & ~pl.col("kickoff"))
        pool[c] = (q["msg"].to_numpy().astype(np.int64), q["day_idx"].to_numpy())
    plx = L.draw_placebos(r["cls"].to_numpy(), r["day_idx"].to_numpy(), recv, pool, rng)
    msg = r["msg"].to_numpy().astype(np.int64)
    uniq = np.unique(np.concatenate([msg, plx[plx >= 0]]))
    pos = np.searchsorted(uniq, msg)
    out = {"item": r["item"].to_numpy()}
    alphas = {}
    for model, variant, tag in (("bge_small", "white32", ""), ("gte_modernbert", "white32", "_gte"),
                                ("bge_small", "style_resid_period32", "_sr")):
        Mv = L.message_vectors(uniq, m["regime"], model)
        U = Mv[pos]
        Up = np.full(plx.shape + (32,), np.nan, np.float32)
        okp = plx >= 0
        Up[okp] = Mv[np.searchsorted(uniq, plx[okp])]
        Vs = V if tag == "" else L.statement_table(days, model, variant)[1]
        pc = R.content_rows_r2(Vs, bidx, pmask, qidx, U, Up, call_id=r["turn_id"].to_numpy().astype(np.int64))
        alphas[tag or "_bge"] = pc["alpha_sums"].tolist()
        for k, v in pc.items():
            if k != "alpha_sums":
                out[k + tag] = v
    out["k_pre"] = (bidx >= 0).sum(1).astype(np.int8)
    df = pl.DataFrame(out)
    df = df.with_columns([pl.col(c).fill_nan(None) for c in df.columns if df[c].dtype == pl.Float32])
    od = outdir(p)
    df.write_parquet(od / "r2_content.parquet", compression="zstd")
    (od / "r2_alpha_sums.json").write_text(json.dumps(alphas))
    L.write_provenance(od, "hypotheses/H52-humans-loud-agents/scheme/build_r2.py",
                       ["H52 rows.parquet", "embeddings/statements", "embeddings/statements_{white32,style_resid_period32}",
                        "embeddings/chat_{bge_small,gte_modernbert}", "embeddings/whitening*", "producing_calls"],
                       dict(period=p, seed=[SEED2, m["goal"]], n_agent_msgs=N_AGENT_MSGS, n_placebo=L.N_PL))
    print(p, "content", df.height, round(time.time() - t0, 1), "s", flush=True)


# ============================================================================ pair deltas
def decoy_pools(periods):
    """Per class, the messages of the round-2 pair sets with their goal, regime and length (decoy candidates)."""
    fr = []
    for p in periods:
        f = R.R2OUT / p / "r2_pairs.parquet"
        if f.exists():
            P = pl.read_parquet(f, columns=["msg", "cls", "len", "regime"]).unique("msg").with_columns(
                pl.lit(meta(p)["goal"]).alias("goal"))
            fr.append(P)
    return pl.concat(fr)


def build_pairvec(periods):
    pools = decoy_pools(L.REPLICATION)
    for p in periods:
        t0 = time.time()
        P = pl.read_parquet(R.R2OUT / p / "r2_pairs.parquet")
        reg, goal = meta(p)["regime"], meta(p)["goal"]
        rng = np.random.default_rng([SEED2, goal, 2])
        cand = pools.filter((pl.col("regime") == reg) & (pl.col("goal") != goal))
        res = {}
        for model in ("bge_small", "gte_modernbert"):
            ids = np.unique(np.concatenate([P["msg"].to_numpy(), P["before_msg"].to_numpy(), P["after_msg"].to_numpy(),
                                            cand["msg"].to_numpy()])).astype(np.int64)
            Mv = L.message_vectors(ids, reg, model)
            vec = lambda a: Mv[np.searchsorted(ids, np.asarray(a, np.int64))]  # noqa: E731
            E = vec(P["msg"].to_numpy()); Zb = vec(P["before_msg"].to_numpy()); Za = vec(P["after_msg"].to_numpy())
            d_raw = np.full(P.height, np.nan); d_q = np.full(P.height, np.nan); a_raw = np.full(P.height, np.nan)
            msgs = P["msg"].to_numpy(); cls = P["cls"].to_numpy(); ln = P["len"].to_numpy()
            cmsg = cand["msg"].to_numpy(); ccls = cand["cls"].to_numpy(); clen = cand["len"].to_numpy()
            Cv = vec(cmsg)
            cok = np.isfinite(Cv).all(1)
            for mm in np.unique(msgs):
                rr = np.flatnonzero(msgs == mm)
                c0, l0 = cls[rr[0]], ln[rr[0]]
                sel = np.flatnonzero((ccls == c0) & cok & (clen >= 0.5 * l0) & (clen <= 2 * l0))
                if len(sel) < 5:
                    sel = np.flatnonzero((ccls == c0) & cok)
                if len(sel) > 50:
                    sel = rng.choice(sel, 50, replace=False)
                if len(sel) < 5:
                    continue
                D = Cv[sel].astype(np.float64)
                e = E[rr[0]].astype(np.float64)
                if not np.isfinite(e).all():
                    continue
                zb, za = Zb[rr].astype(np.float64), Za[rr].astype(np.float64)
                ok = np.isfinite(zb).all(1) & np.isfinite(za).all(1)
                dz = za - zb
                a_raw[rr] = np.where(ok, dz @ e, np.nan)
                d_raw[rr] = np.where(ok, dz @ e - (dz @ D.T).mean(1), np.nan)
                eq = e[None, :] - (zb @ e)[:, None] * zb
                eq /= np.maximum(np.linalg.norm(eq, axis=1, keepdims=True), 1e-9)
                Dq = D[None, :, :] - np.einsum("nd,kd->nk", zb, D)[..., None] * zb[:, None, :]
                Dq /= np.maximum(np.linalg.norm(Dq, axis=2, keepdims=True), 1e-9)
                d_q[rr] = np.where(ok, np.einsum("nd,nd->n", za, eq) - np.einsum("nkd,nd->nk", Dq, za).mean(1), np.nan)
            tag = "" if model == "bge_small" else "_gte"
            res["a" + tag] = a_raw; res["delta" + tag] = d_raw; res["delta_q" + tag] = d_q
        out = P.with_columns(*[pl.Series(k, v.astype(np.float32)).fill_nan(None) for k, v in res.items()])
        out.write_parquet(R.R2OUT / p / "r2_pairdelta.parquet", compression="zstd")
        print(p, "pairvec", out.height, round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    ps = [a for a in sys.argv[2:] if not a.startswith("--")]
    if cmd == "skeleton":
        for p in (ps or SKEL_PERIODS):
            if p in SKEL_PERIODS:
                skel_rows(p)
        for p in (ps or L.REPLICATION):
            build_pairs(p)
    elif cmd == "content":
        for p in (ps or L.REPLICATION):
            build_content(p)
    elif cmd == "pairvec":
        build_pairvec(ps or L.REPLICATION)
