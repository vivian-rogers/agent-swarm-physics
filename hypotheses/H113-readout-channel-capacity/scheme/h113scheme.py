"""H113 scheme library: read-out batches, orthogonalized content projections and per-call uptake terms (no text).

For a response statement y of reader i at receiving/talk call c (card, "Model"):
  B_c   the agent-kind items of i's pending set at c (pending_sets, H18's ledger k) with a statement vector;
  F_c   the in-flight set: other agents' statements in i's room posted in [t_call(c), t(y)) (unreadable by c);
  p_c   i's previous statement on the same PT day (before t_call);
  G     goal, kickoff and room-kickoff directions of the period, whitened (embed_models.load_whitener);
  f_c   out-of-batch window field: the unit mean of other agents' statements in i's room within +-30 min of t(y),
        excluding i, B_c and F_c (needs >= 3 statements, else omitted);
  P_c   projector onto the orthogonal complement of span{p_c, G, f_c}; y_perp = P_c y, x_perp = P_c x.
Per call we store the inner products that the estimators need (s = sum of x_perp over B_c, sF over F_c, the newest
item, the one-call subset) and the projected vectors (float16) for the discrete check.

Inputs are shared tables only; pending_sets already drops held-out days and every other table is masked with
common.holdout_mask (allow_holdout=True only in confirm.py).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT as SHARED, holdout_mask  # noqa: E402

MODELS = ("bge_small", "gte_modernbert")
US = 1_000_000
FIELD_WIN_S = 30 * 60
FIELD_MIN = 3


@lru_cache(maxsize=1)
def chat_rows() -> pl.DataFrame:
    """chat_core rows (msg = row index) with the statement row (srow) of agent messages."""
    cc = pl.read_parquet(SHARED / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room", "speaker_kind",
                                                                "agent"]).with_row_index("msg")
    ci = pl.read_parquet(SHARED / "embeddings/chat_index.parquet").with_row_index("src_row")
    st = pl.read_parquet(SHARED / "embeddings/statements.parquet").with_row_index("srow").filter(pl.col("kind") == "chat")
    st = st.select("srow", pl.col("src_row").cast(pl.UInt32)).join(ci.with_columns(pl.col("src_row").cast(pl.UInt32)),
                                                                   on="src_row").select("message_id", "srow")
    cc = cc.join(st, on="message_id", how="left")
    return cc.with_columns(pl.col("t").dt.epoch("us").alias("t_us"))


@lru_cache(maxsize=2)
def vectors(model: str, variant: str = "style_resid32") -> np.ndarray:
    return np.load(SHARED / f"embeddings/statements_{variant}_{model}.npy", mmap_mode="r")


def goal_basis(goal_no: int, room: int | None, model: str, regime: str) -> np.ndarray:
    from embed_models import goal_vectors, load_whitener
    g = pl.read_parquet(SHARED / "embeddings/goals.parquet").with_row_index("row")
    g = g.filter((pl.col("goal_no") == goal_no) & pl.col("kind").cast(pl.String).is_in(["goal", "kickoff", "kickoff_room"]))
    if room is not None:
        g = g.filter((pl.col("kind").cast(pl.String) != "kickoff_room") | (pl.col("room") == room))
    else:
        g = g.filter(pl.col("kind").cast(pl.String) != "kickoff_room")
    if len(g) == 0:
        return np.zeros((0, 32))
    raw = goal_vectors(model)[g["row"].to_numpy()].astype(np.float32)
    W = load_whitener(regime, 32, model)
    G = np.asarray(W(raw), dtype=np.float64)
    G /= np.linalg.norm(G, axis=1, keepdims=True) + 1e-12
    return G


def project_out(B: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Remove span(B rows) from X rows (B may be rank deficient)."""
    if B.shape[0] == 0:
        return X
    Q, R = np.linalg.qr(B.T)
    keep = np.abs(np.diag(R)) > 1e-8
    Q = Q[:, keep]
    return X - (X @ Q) @ Q.T


def build_frames_talks(goal_no: int, ps_dir: Path) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Calls (one per scored talk) and items (agent-kind pending items) from a pending_sets folder."""
    talks = pl.read_parquet(ps_dir / "talks.parquet")
    pend = pl.read_parquet(ps_dir / "pending.parquet")
    calls = talks.select(pl.col("talk_id").alias("cid"), "agent", "pt_date", "room", pl.col("s_us").alias("t_call_us"),
                         pl.col("t_us").alias("t_post_us"), pl.col("msg").cast(pl.UInt32).alias("resp_msg"),
                         pl.col("k").alias("k_pend"), "k_since_talk", "after_pause")
    items = pend.select(pl.col("talk_id").alias("cid"), pl.col("msg").cast(pl.UInt32), "kind", "sender", "rank", "ment_i")
    return calls, items


def build_frames_wakes(goal_no: int, ps_dir: Path, cr: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """D2 timer-wake batches: response = the agent's first chat statement after the wake call within delay + 5 s."""
    wk = pl.read_parquet(ps_dir / "wakes.parquet").filter(pl.col("talked"))
    wp = pl.read_parquet(ps_dir / "wake_pending.parquet")
    msgs = cr.filter(pl.col("speaker_kind").cast(pl.String) == "agent").select("msg", "agent", "t_us", "room") \
        .with_columns(pl.col("agent").cast(pl.Int16)).sort("t_us")
    wk = wk.with_columns((pl.col("t_wake_us") + (pl.col("delay_s").fill_null(0) * US).cast(pl.Int64)).alias("t_resp_hint"))
    # explicit matching: the first agent statement after the wake call, within the logged delay + 5 s
    out = []
    by_agent = {int(a): (g["t_us"].to_numpy(), g["msg"].to_numpy(), g["room"].to_numpy())
                for (a,), g in msgs.group_by(["agent"], maintain_order=True)}
    for r in wk.iter_rows(named=True):
        v = by_agent.get(int(r["agent"]))
        if v is None:
            continue
        k = np.searchsorted(v[0], r["t_wake_us"], side="right")
        if k < len(v[0]) and v[0][k] <= r["t_resp_hint"] + 5 * US:
            out.append((r["wake_id"], r["agent"], r["pt_date"], int(v[2][k]), r["t_wake_us"], int(v[0][k]), int(v[1][k]), r["k"]))
    calls = pl.DataFrame(out, schema={"cid": pl.Int32, "agent": pl.Int16, "pt_date": pl.String, "room": pl.Int16,
                                      "t_call_us": pl.Int64, "t_post_us": pl.Int64, "resp_msg": pl.UInt32, "k_pend": pl.Int32},
                         orient="row").with_columns(pl.lit(None, pl.Int32).alias("k_since_talk"), pl.lit(True).alias("after_pause"))
    items = wp.select(pl.col("wake_id").cast(pl.Int32).alias("cid"), pl.col("msg").cast(pl.UInt32), "kind", "sender", "rank",
                      "ment_i")
    return calls, items


def at_call_items(calls: pl.DataFrame, items: pl.DataFrame, cr: pl.DataFrame) -> pl.DataFrame:
    """Flag items that are new at the response's producing call (HH345's one-call batch)."""
    pc = pl.read_parquet(SHARED / "producing_calls.parquet", columns=["msg", "turn_id_prod"])
    c = calls.select("cid", "resp_msg").join(pc.rename({"msg": "resp_msg"}), on="resp_msg", how="left")
    li = pl.scan_parquet(SHARED / "context_ledger_items.parquet").select("turn_id", "message_id") \
        .filter(pl.col("turn_id").is_in(c["turn_id_prod"].drop_nulls().unique().implode())).collect()
    li = li.join(cr.select("message_id", "msg"), on="message_id", how="inner").select(pl.col("turn_id").alias("turn_id_prod"), "msg")
    flag = c.join(li, on="turn_id_prod", how="inner").select("cid", "msg").with_columns(pl.lit(True).alias("at_call"))
    return items.join(flag, on=["cid", "msg"], how="left").with_columns(pl.col("at_call").fill_null(False))


def compute(goal_no: int, calls: pl.DataFrame, items: pl.DataFrame, model: str, variant: str = "style_resid32",
            allow_holdout: bool = False, field: bool = True, V: np.ndarray | None = None
            ) -> tuple[pl.DataFrame, pl.DataFrame, np.ndarray, np.ndarray]:
    """V: optional statement-vector array (synthetic worlds replace the real vectors; same row index)."""
    cr = chat_rows()
    V = vectors(model, variant) if V is None else V
    reg = pl.read_parquet(SHARED / "period_units.parquet").filter(pl.col("goal_no") == goal_no)["regime"][0]
    # agent statements of the period (for previous statements, in-flight sets and the field)
    days = calls["pt_date"].unique().to_list()
    pst = cr.filter(pl.col("pt_date").is_in(days) & pl.col("srow").is_not_null()
                    & (pl.col("speaker_kind").cast(pl.String) == "agent"))
    if not allow_holdout:
        ho = holdout_mask(pst["pt_date"].to_list(), pst["goal_no"].to_list())
        pst = pst.filter(~pl.Series(ho))
    pst = pst.sort("t_us")
    msg2srow = {int(m): (int(s) if s is not None else -1) for m, s in pst.select("msg", "srow").iter_rows()}
    msg2t = {int(m): int(t) for m, t in pst.select("msg", "t_us").iter_rows()}
    by_agent = {int(a): (g["t_us"].to_numpy(), g["srow"].to_numpy(), g["pt_date"].to_numpy())
                for (a,), g in pst.group_by(["agent"], maintain_order=True)}
    by_room = {int(r): (g["t_us"].to_numpy(), g["srow"].to_numpy(), g["agent"].to_numpy(), g["msg"].to_numpy())
               for (r,), g in pst.group_by(["room"], maintain_order=True)}
    Gb = {}
    items = items.filter(pl.col("kind") == 0)
    it_by_cid = {}
    for (cid,), g in items.group_by(["cid"], maintain_order=True):
        it_by_cid[int(cid)] = g
    crow, irow, Y, X = [], [], [], []
    for r in calls.iter_rows(named=True):
        ys = msg2srow.get(int(r["resp_msg"]), -1)
        if ys < 0:
            continue
        a = int(r["agent"]); tc = int(r["t_call_us"]); tp = int(r["t_post_us"]); room = int(r["room"]) if r["room"] is not None else -1
        va = by_agent.get(a)
        if va is None:
            continue
        kprev = np.searchsorted(va[0], tc, side="left") - 1
        if kprev < 0 or va[2][kprev] != r["pt_date"]:
            continue
        ps = int(va[1][kprev])
        g = it_by_cid.get(int(r["cid"]))
        bmsg = [] if g is None else [int(m) for m in g["msg"].to_list()]
        bsrow = [msg2srow.get(m, -1) for m in bmsg]
        # in-flight set
        vr = by_room.get(room)
        fl_srow, fl_msg = [], []
        fld = None
        if vr is not None:
            lo = np.searchsorted(vr[0], tc, side="left"); hi = np.searchsorted(vr[0], tp, side="left")
            for q in range(lo, hi):
                if int(vr[2][q]) != a:
                    fl_srow.append(int(vr[1][q])); fl_msg.append(int(vr[3][q]))
            if field:
                lo2 = np.searchsorted(vr[0], tp - FIELD_WIN_S * US, side="left")
                hi2 = np.searchsorted(vr[0], tp + FIELD_WIN_S * US, side="right")
                excl = set(bmsg) | set(fl_msg)
                sel = [int(vr[1][q]) for q in range(lo2, hi2) if int(vr[2][q]) != a and int(vr[3][q]) not in excl]
                if len(sel) >= FIELD_MIN:
                    fv = np.asarray(V[sel], dtype=np.float64).mean(0)
                    fld = fv / (np.linalg.norm(fv) + 1e-12)
        key = room
        if key not in Gb:
            Gb[key] = goal_basis(goal_no, room if room >= 0 else None, model, reg)
        basis = [np.asarray(V[ps], dtype=np.float64)[None, :], Gb[key]]
        if fld is not None:
            basis.append(fld[None, :])
        Bm = np.vstack(basis)
        y = project_out(Bm, np.asarray(V[ys], dtype=np.float64)[None, :])[0]
        ok = [i for i, s in enumerate(bsrow) if s >= 0]
        xb = project_out(Bm, np.asarray(V[[bsrow[i] for i in ok]], dtype=np.float64)) if ok else np.zeros((0, 32))
        xf = project_out(Bm, np.asarray(V[fl_srow], dtype=np.float64)) if fl_srow else np.zeros((0, 32))
        s = xb.sum(0) if len(xb) else np.zeros(32)
        sF = xf.sum(0) if len(xf) else np.zeros(32)
        gi = g[ok] if g is not None and ok else None
        rank = gi["rank"].to_numpy() if gi is not None else np.zeros(0)
        atc = gi["at_call"].to_numpy() if gi is not None and "at_call" in gi.columns else np.zeros(len(ok), bool)
        newest = int(np.argmin(rank)) if len(rank) else -1
        s1 = xb[atc].sum(0) if len(xb) and atc.any() else np.zeros(32)
        cidx = len(crow)
        crow.append({"cid": int(r["cid"]), "agent": a, "pt_date": r["pt_date"], "room": room, "t_call_us": tc, "t_post_us": tp,
                     "k": len(ok), "k_pend": r["k_pend"], "k1": int(atc.sum()), "kF": len(xf), "has_field": fld is not None,
                     "yy": float(y @ y), "ys": float(y @ s), "ss": float(s @ s), "ysF": float(y @ sF), "sFsF": float(sF @ sF),
                     "ssF": float(s @ sF), "ys1": float(y @ s1), "s1s1": float(s1 @ s1),
                     "yn": float(y @ xb[newest]) if newest >= 0 else 0.0, "nn": float(xb[newest] @ xb[newest]) if newest >= 0 else 0.0,
                     "after_pause": r.get("after_pause")})
        Y.append(y.astype(np.float16))
        for jj, i in enumerate(ok):
            m = bmsg[i]
            irow.append({"call_row": cidx, "msg": m, "read": True, "age_s": (tp - msg2t.get(m, tp)) / US,
                         "rank": int(rank[jj]), "ment_i": bool(gi["ment_i"][jj]), "at_call": bool(atc[jj]),
                         "xy": float(xb[jj] @ y), "xx": float(xb[jj] @ xb[jj])})
            X.append(xb[jj].astype(np.float16))
        for jj, m in enumerate(fl_msg):
            irow.append({"call_row": cidx, "msg": m, "read": False, "age_s": (tp - msg2t.get(m, tp)) / US, "rank": -1,
                         "ment_i": False, "at_call": False, "xy": float(xf[jj] @ y), "xx": float(xf[jj] @ xf[jj])})
            X.append(xf[jj].astype(np.float16))
    cdf = pl.DataFrame(crow)
    idf = pl.DataFrame(irow) if irow else pl.DataFrame(schema={"call_row": pl.Int64})
    return cdf, idf, np.asarray(Y, np.float16).reshape(-1, 32), np.asarray(X, np.float16).reshape(-1, 32)
