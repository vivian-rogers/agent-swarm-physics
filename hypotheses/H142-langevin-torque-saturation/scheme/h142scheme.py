"""H142 scheme library: per (call, content direction) rows for the Langevin-torque test. No text is read.

Unit rows (card, "Data scheme"; same unit as H113's scored talk calls, rebuilt here, H113 code not imported):
  call c        a scored talk call of reader i (shared pending_sets), with a statement y (DQ5 vector) and a previous
                same-PT-day statement p_c of i before t_call;
  batch B_c     agent-kind (kind 0) pending items with a statement vector (ledger k); human and nudge items excluded;
  in-flight F_c others' statements in i's room posted in [t_call, t(y)) (unreadable at c);
  P_c           projector that removes span{p_c, goal, kickoff, room kickoff (whitened per regime),
                f_c = the out-of-batch window field (others' statements in i's room within +-30 min of t(y),
                excluding i, B_c and F_c; >= 3 statements)} (H113's card definition);
  directions u  K spherical k-means centroids of the unit projected reader statements, fitted with day folds: the
                centroids used on day d are fitted on the other days' calls (a shared ruler, exception (a));
  labels        each projected batch / in-flight item goes to its nearest centroid if cos >= 0.3, else none (-1);
  rows          one per (c, u): y_cu = (P_c y) . u_hat; n_cu (aligned batch items), nF_cu (aligned in-flight items),
                newest_cu (the newest batch item is aligned with u), nname_cu (aligned items that name the reader,
                pending_sets.ment_i, from chat_mentions_clean), k, room, hour, agent, day.
Held-out days are absent from pending_sets; every other table passes common.holdout_mask.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

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
COS_MIN = 0.3
HOUR_US = 3600 * US


@lru_cache(maxsize=1)
def chat_rows() -> pl.DataFrame:
    cc = pl.read_parquet(SHARED / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room", "speaker_kind",
                                                                "agent"]).with_row_index("msg")
    ci = pl.read_parquet(SHARED / "embeddings/chat_index.parquet").with_row_index("src_row")
    st = pl.read_parquet(SHARED / "embeddings/statements.parquet").with_row_index("srow").filter(pl.col("kind") == "chat")
    st = st.select("srow", pl.col("src_row").cast(pl.UInt32)).join(ci.with_columns(pl.col("src_row").cast(pl.UInt32)),
                                                                   on="src_row").select("message_id", "srow")
    cc = cc.join(st, on="message_id", how="left")
    return cc.with_columns(pl.col("t").dt.epoch("us").alias("t_us"))


@lru_cache(maxsize=1)
def flags() -> pl.DataFrame:
    return pl.read_parquet(SHARED / "statement_flags.parquet", columns=["srow", "self_repeat_both", "cross_echo_both",
                                                                         "templated_both"])


@lru_cache(maxsize=4)
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
    if B.shape[0] == 0:
        return X
    Q, R = np.linalg.qr(B.T)
    keep = np.abs(np.diag(R)) > 1e-8
    Q = Q[:, keep]
    return X - (X @ Q) @ Q.T


def frames_talks(ps_dir: Path) -> tuple[pl.DataFrame, pl.DataFrame]:
    talks = pl.read_parquet(ps_dir / "talks.parquet")
    pend = pl.read_parquet(ps_dir / "pending.parquet")
    calls = talks.select(pl.col("talk_id").alias("cid"), "agent", "pt_date", "room", pl.col("s_us").alias("t_call_us"),
                         pl.col("t_us").alias("t_post_us"), pl.col("msg").cast(pl.UInt32).alias("resp_msg"))
    items = pend.select(pl.col("talk_id").alias("cid"), pl.col("msg").cast(pl.UInt32), "kind", "sender", "rank", "ment_i")
    return calls, items


def frames_wakes(ps_dir: Path, cr: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """D2 timer-wake batches: response = the agent's first chat statement after the wake call within delay + 5 s."""
    wk = pl.read_parquet(ps_dir / "wakes.parquet").filter(pl.col("talked"))
    wp = pl.read_parquet(ps_dir / "wake_pending.parquet")
    msgs = cr.filter(pl.col("speaker_kind").cast(pl.String) == "agent").select("msg", "agent", "t_us", "room") \
        .with_columns(pl.col("agent").cast(pl.Int16)).sort("t_us")
    wk = wk.with_columns((pl.col("t_wake_us") + (pl.col("delay_s").fill_nan(0).fill_null(0) * US).cast(pl.Int64)).alias("t_hint"))
    by_agent = {int(a): (g["t_us"].to_numpy(), g["msg"].to_numpy(), g["room"].to_numpy())
                for (a,), g in msgs.group_by(["agent"], maintain_order=True)}
    out = []
    for r in wk.iter_rows(named=True):
        v = by_agent.get(int(r["agent"]))
        if v is None:
            continue
        k = np.searchsorted(v[0], r["t_wake_us"], side="right")
        if k < len(v[0]) and v[0][k] <= r["t_hint"] + 5 * US:
            out.append((r["wake_id"], r["agent"], r["pt_date"], int(v[2][k]), r["t_wake_us"], int(v[0][k]), int(v[1][k])))
    calls = pl.DataFrame(out, schema={"cid": pl.Int32, "agent": pl.Int16, "pt_date": pl.String, "room": pl.Int16,
                                      "t_call_us": pl.Int64, "t_post_us": pl.Int64, "resp_msg": pl.UInt32}, orient="row")
    items = wp.select(pl.col("wake_id").cast(pl.Int32).alias("cid"), pl.col("msg").cast(pl.UInt32), "kind", "sender", "rank",
                      "ment_i")
    return calls, items


def project_calls(goal_no: int, calls: pl.DataFrame, items: pl.DataFrame, model: str, variant: str = "style_resid32",
                  field: bool = True) -> dict:
    """Projected reader statements Y (n_calls x 32), batch items (call index, rank, ment_i, X) and in-flight items."""
    cr = chat_rows()
    V = vectors(model, variant)
    reg = pl.read_parquet(SHARED / "period_units.parquet").filter(pl.col("goal_no") == goal_no)["regime"][0]
    days = calls["pt_date"].unique().to_list()
    pst = cr.filter(pl.col("pt_date").is_in(days) & pl.col("srow").is_not_null()
                    & (pl.col("speaker_kind").cast(pl.String) == "agent"))
    ho = holdout_mask(pst["pt_date"].to_list(), pst["goal_no"].to_list())
    pst = pst.filter(~pl.Series(ho)).sort("t_us")
    msg2srow = {int(m): int(s) for m, s in pst.select("msg", "srow").iter_rows()}
    by_agent = {int(a): (g["t_us"].to_numpy(), g["srow"].to_numpy(), g["pt_date"].to_numpy())
                for (a,), g in pst.group_by(["agent"], maintain_order=True)}
    by_room = {int(r): (g["t_us"].to_numpy(), g["srow"].to_numpy(), g["agent"].to_numpy(), g["msg"].to_numpy())
               for (r,), g in pst.group_by(["room"], maintain_order=True)}
    Gb: dict = {}
    it_by_cid = {int(c): g for (c,), g in items.filter(pl.col("kind") == 0).group_by(["cid"], maintain_order=True)}
    crow, Y = [], []
    ib_call, ib_rank, ib_name, ib_msg, XB = [], [], [], [], []
    if_call, if_msg, XF = [], [], []
    for r in calls.sort("t_call_us").iter_rows(named=True):
        ys = msg2srow.get(int(r["resp_msg"]), -1)
        if ys < 0:
            continue
        a = int(r["agent"]); tc = int(r["t_call_us"]); tp = int(r["t_post_us"])
        room = int(r["room"]) if r["room"] is not None else -1
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
        vr = by_room.get(room)
        fl_srow, fl_msg, fld = [], [], None
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
        if room not in Gb:
            Gb[room] = goal_basis(goal_no, room if room >= 0 else None, model, reg)
        basis = [np.asarray(V[ps], dtype=np.float64)[None, :], Gb[room]]
        if fld is not None:
            basis.append(fld[None, :])
        Bm = np.vstack(basis)
        y = project_out(Bm, np.asarray(V[ys], dtype=np.float64)[None, :])[0]
        ok = [i for i, s in enumerate(bsrow) if s >= 0]
        ci = len(crow)
        if ok:
            xb = project_out(Bm, np.asarray(V[[bsrow[i] for i in ok]], dtype=np.float64))
            rk = g["rank"].to_numpy()[ok]; mi = g["ment_i"].to_numpy()[ok]
            for j, i in enumerate(ok):
                ib_call.append(ci); ib_rank.append(int(rk[j])); ib_name.append(bool(mi[j])); ib_msg.append(bmsg[i])
            XB.append(xb)
        if fl_srow:
            xf = project_out(Bm, np.asarray(V[fl_srow], dtype=np.float64))
            for m in fl_msg:
                if_call.append(ci); if_msg.append(m)
            XF.append(xf)
        crow.append({"cid": int(r["cid"]), "agent": a, "pt_date": r["pt_date"], "room": room, "t_call_us": tc,
                     "t_post_us": tp, "resp_srow": ys, "k": len(ok), "kF": len(fl_srow), "has_field": fld is not None})
        Y.append(y)
    calls_df = pl.DataFrame(crow)
    return {"calls": calls_df, "Y": np.asarray(Y, np.float64).reshape(-1, 32),
            "items": pl.DataFrame({"call": np.asarray(ib_call, np.int32), "rank": np.asarray(ib_rank, np.int16),
                                   "ment_i": np.asarray(ib_name, bool), "msg": np.asarray(ib_msg, np.uint32)}),
            "XB": np.vstack(XB) if XB else np.zeros((0, 32)),
            "inflight": pl.DataFrame({"call": np.asarray(if_call, np.int32), "msg": np.asarray(if_msg, np.uint32)}),
            "XF": np.vstack(XF) if XF else np.zeros((0, 32))}


def _unit(X: np.ndarray) -> np.ndarray:
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def skmeans(U: np.ndarray, K: int, seed: int, n_init: int = 3, iters: int = 40) -> np.ndarray:
    """Spherical k-means (k-means++ init on cosine distance) on unit rows; returns K unit centroids."""
    rng = np.random.default_rng(seed)
    best, best_obj = None, -np.inf
    for _ in range(n_init):
        c = [U[rng.integers(len(U))]]
        for _k in range(1, K):
            d = 1 - np.max(U @ np.asarray(c).T, axis=1)
            d = np.clip(d, 0, None)
            p = d / d.sum() if d.sum() > 0 else None
            c.append(U[rng.choice(len(U), p=p)])
        C = np.asarray(c)
        for _i in range(iters):
            lab = np.argmax(U @ C.T, axis=1)
            Cn = np.vstack([U[lab == j].sum(0) if (lab == j).any() else C[j] for j in range(K)])
            Cn = _unit(Cn)
            if np.allclose(Cn, C):
                break
            C = Cn
        obj = float(np.max(U @ C.T, axis=1).sum())
        if obj > best_obj:
            best, best_obj = C, obj
    return best


def fold_centroids(calls: pl.DataFrame, Y: np.ndarray, K: int, seed: int) -> dict[str, np.ndarray]:
    """Day folds: centroids for day d fitted on the unit projected reader statements of the other days."""
    days = sorted(calls["pt_date"].unique().to_list())
    dd = calls["pt_date"].to_numpy()
    U = _unit(Y)
    out = {}
    for j, d in enumerate(days):
        m = dd != d
        out[d] = skmeans(U[m], K, seed + j) if m.sum() >= 4 * K else skmeans(U, K, seed + j)
    return out


def assign(X: np.ndarray, call_idx: np.ndarray, call_day: np.ndarray, cents: dict) -> tuple[np.ndarray, np.ndarray]:
    """Nearest fold centroid label (cos >= COS_MIN, else -1) and that cosine, for rows of X attached to calls."""
    lab = np.full(len(X), -1, np.int8); cs = np.zeros(len(X), np.float32)
    if len(X) == 0:
        return lab, cs
    Xu = _unit(X)
    days = call_day[call_idx]
    for d, C in cents.items():
        m = days == d
        if not m.any():
            continue
        S = Xu[m] @ C.T
        j = np.argmax(S, axis=1); s = S[np.arange(len(j)), j]
        lab[m] = np.where(s >= COS_MIN, j, -1).astype(np.int8); cs[m] = s
    return lab, cs


def rows_frame(P: dict, cents: dict, K: int, goal_no: int) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    """One row per (call, direction) plus labelled batch / in-flight item tables."""
    c = P["calls"]
    n = len(c)
    day = c["pt_date"].to_numpy()
    blab, bcos = assign(P["XB"], P["items"]["call"].to_numpy(), day, cents)
    flab, fcos = assign(P["XF"], P["inflight"]["call"].to_numpy(), day, cents)
    items = P["items"].with_columns(pl.Series("lab", blab), pl.Series("cos", bcos))
    infl = P["inflight"].with_columns(pl.Series("lab", flab), pl.Series("cos", fcos))
    nB = np.zeros((n, K), np.int16); nF = np.zeros((n, K), np.int16); nN = np.zeros((n, K), np.int16)
    newest = np.zeros((n, K), bool)
    ic = items["call"].to_numpy(); ir = items["rank"].to_numpy(); im = items["ment_i"].to_numpy()
    ok = blab >= 0
    np.add.at(nB, (ic[ok], blab[ok]), 1)
    np.add.at(nN, (ic[ok & im], blab[ok & im]), 1)
    if len(ic):
        order = np.lexsort((ir, ic))
        first = order[np.r_[True, np.diff(ic[order]) != 0]]
        f_ok = first[blab[first] >= 0]
        newest[ic[f_ok], blab[f_ok]] = True
    fc = infl["call"].to_numpy(); okf = flab >= 0
    np.add.at(nF, (fc[okf], flab[okf]), 1)
    Yc = np.zeros((n, K))
    for d, C in cents.items():
        m = day == d
        Yc[m] = P["Y"][m] @ C.T
    rr = np.repeat(np.arange(n), K); uu = np.tile(np.arange(K), n)
    fl = flags()
    resp = c.select("resp_srow").with_columns(pl.col("resp_srow").cast(pl.UInt32).alias("srow")).join(
        fl, on="srow", how="left")
    rows = pl.DataFrame({
        "call": rr.astype(np.int32), "u": uu.astype(np.int8), "y": Yc.ravel().astype(np.float32),
        "n": nB.ravel(), "nF": nF.ravel(), "newest": newest.ravel(), "nname": nN.ravel(),
    })
    cc = c.with_row_index("call").with_columns(
        pl.col("call").cast(pl.Int32), (pl.col("t_call_us") // HOUR_US).cast(pl.Int32).alias("hour"),
        pl.Series("yy", (P["Y"] ** 2).sum(1).astype(np.float32)),
        resp["self_repeat_both"].fill_null(False).alias("f_self"), resp["cross_echo_both"].fill_null(False).alias("f_echo"),
        resp["templated_both"].fill_null(False).alias("f_templ"))
    rows = rows.join(cc.select("call", "cid", "agent", "pt_date", "room", "hour", "k", "kF", "f_self", "f_echo", "f_templ"),
                     on="call", how="left")
    return rows, items, infl, cc


def message_labels(goal_no: int, days: list[str], cents: dict, model: str, variant: str = "style_resid32") -> pl.DataFrame:
    """Own label of every agent statement in the period (goal-basis projection only; fold centroids of its day).
    Used only by the synthetic hot-topic world (structural; no reader outcome)."""
    cr = chat_rows()
    V = vectors(model, variant)
    reg = pl.read_parquet(SHARED / "period_units.parquet").filter(pl.col("goal_no") == goal_no)["regime"][0]
    pst = cr.filter(pl.col("pt_date").is_in(days) & pl.col("srow").is_not_null()
                    & (pl.col("speaker_kind").cast(pl.String) == "agent"))
    ho = holdout_mask(pst["pt_date"].to_list(), pst["goal_no"].to_list())
    pst = pst.filter(~pl.Series(ho)).sort("t_us")
    labs = np.full(len(pst), -1, np.int8)
    rooms = pst["room"].to_numpy(); dd = pst["pt_date"].to_numpy(); sr = pst["srow"].to_numpy().astype(np.int64)
    for room in np.unique(rooms):
        G = goal_basis(goal_no, int(room), model, reg)
        m = rooms == room
        X = project_out(G, np.asarray(V[sr[m]], dtype=np.float64))
        idx = np.flatnonzero(m)
        Xu = _unit(X)
        for d, C in cents.items():
            mm = dd[idx] == d
            if not mm.any():
                continue
            S = Xu[mm] @ C.T
            j = np.argmax(S, 1); s = S[np.arange(len(j)), j]
            labs[idx[mm]] = np.where(s >= COS_MIN, j, -1)
    return pst.select("msg", "t_us", "room", "pt_date", "agent").with_columns(pl.Series("lab", labs))
