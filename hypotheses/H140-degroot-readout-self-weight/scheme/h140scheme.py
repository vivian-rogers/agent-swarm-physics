"""H140 scheme library: per-call Gram terms for the DeGroot read-out fit (no text).

For the statement y of reader i at talk call c (card, "Model" and "Data scheme"):
  p    mean of i's last two statements in the current context segment, posted before t_call(c)   (variant p1: last one)
  z    mean of i's third- and fourth-last statements in the segment (instrument for p)
  s    sum of the batch B_c: agent-kind items of i's pending set (pending_sets, H18's ledger k) with a statement vector
  sF   sum of the in-flight set F_c: other agents' statements in i's room posted in [t_call(c), t(y))
  h    i's leave-day-out well centre (mean of i's statements in the goal period on other days; >= 10 needed; H130 rule)
All vectors are deviations from the unit mean, then projected by P_c = complement of span{goal, kickoff, room kickoff}
(whitened per regime). Variant F also projects out the out-of-batch window field f_c (H113's +-30 min field).
Per row we store the Gram matrix of (y, p, p1, z, s, sF, h): 28 inner products. The fit needs nothing else.

Segments: per agent, ledger calls ordered by (t_call, turn_id); a new segment starts at reset_consol | reset_session
(infra Known issues: first_of_day is not a reset in regime III). Regime I/II (chat mode, O2 only): segment = PT day.
Self-share (H140, call-entry form) s_self = ctx_pos / (ctx_pos + k_ctx) at the producing call of y; chat form
n_own / (n_own + k_ctx) with n_own = own statements earlier in the segment. Call gap dn = own calls between the
producing calls of p's latest statement and of y.
Cross-reset rows (NE41 native): at the first talk call of a segment that started with a consolidation (no own statement
yet in the segment), p and z come from the previous segment (pre-reset content, no longer in context).

Inputs are shared tables only; reserved (locked) days are dropped through common.holdout_mask; pending_sets already
excludes them. The same index structure (Skeleton) serves real and synthetic vectors.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
import scipy.sparse as sp  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT as SHARED, holdout_mask  # noqa: E402

MODELS = ("bge_small", "gte_modernbert")
US = 1_000_000
FIELD_WIN_S = 30 * 60
FIELD_MIN = 3
MIN_WELL = 10
AGE_MAX_S = 120.0
N_SUR = 20
BASES = ("y", "p", "p1", "z", "s", "sF", "h", "f")
PAIRS = [(a, b) for i, a in enumerate(BASES) for b in BASES[i:]]
REG3 = (37, 38, 39, 40, 41, 42, 44, 51)
REG12 = {13: None, 16: None, 35: None, 36: ["36a"]}   # O2-only descriptive periods (H113 field-identified)


# ------------------------------------------------------------------------------------------------ shared tables
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


@lru_cache(maxsize=4)
def vectors(model: str, variant: str = "style_resid32") -> np.ndarray:
    return np.load(SHARED / f"embeddings/statements_{variant}_{model}.npy", mmap_mode="r")


@lru_cache(maxsize=1)
def flags() -> pl.DataFrame:
    return pl.read_parquet(SHARED / "statement_flags.parquet", columns=["srow", "templated", "self_repeat_both", "self_repeat"])


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


def orth_projector(B: np.ndarray) -> np.ndarray:
    """32x32 projector onto the orthogonal complement of span(B rows)."""
    P = np.eye(32)
    if B.shape[0] == 0:
        return P
    Q, R = np.linalg.qr(B.T)
    Q = Q[:, np.abs(np.diag(R)) > 1e-8]
    return P - Q @ Q.T


# ------------------------------------------------------------------------------------------------ skeleton
@dataclass
class Skeleton:
    goal_no: int
    regime: str
    st: pl.DataFrame             # period statements (index = position j): srow, msg, agent, t_us, pt_date, room, unit_id, ...
    rows: pl.DataFrame           # one row per (call, pmode): metadata
    Mp: sp.csr_matrix            # rows x statements, mean of last two (in segment or previous segment)
    Mp1: sp.csr_matrix
    Mz: sp.csr_matrix
    Ms: sp.csr_matrix            # batch indicator
    MF: sp.csr_matrix            # in-flight indicator
    Mf: sp.csr_matrix            # window field mean (rows with < FIELD_MIN members are empty)
    y_idx: np.ndarray            # statement index of y
    ad_idx: np.ndarray           # (agent, day) group of y for the well centre
    ad_of_st: np.ndarray         # group id per statement (agent-day)
    agent_of_ad: np.ndarray
    unit_of_row: np.ndarray      # unit index per row
    unit_of_st: np.ndarray
    units: list
    rooms: np.ndarray            # room per row (projection basis)
    items: pl.DataFrame          # O4 items: row, j (statement), read, age_s
    sur: np.ndarray              # rows x N_SUR surrogate row index (-1 none)
    extra: dict = field(default_factory=dict)


def period_days(goal_no: int, only_units: list | None = None) -> pl.DataFrame:
    pu = pl.read_parquet(SHARED / "period_units.parquet").filter((pl.col("goal_no") == goal_no) & ~pl.col("holdout"))
    if only_units:
        pu = pu.filter(pl.col("unit_id").is_in(only_units))
    d = pu.select("unit_id", "regime", "days").explode("days").rename({"days": "pt_date"})
    ho = holdout_mask(d["pt_date"].to_list(), [goal_no] * len(d))
    return d.filter(~pl.Series(ho))


def ledger(goal_no: int, agents: list[int], days: list[str]) -> pl.DataFrame:
    """Calls of the period's agents on the period's (non-reserved) days with call index n and segment id."""
    lt = pl.scan_parquet(SHARED / "context_ledger_turns.parquet").select(
        "turn_id", "agent", "pt_date", "holdout", "t_call", "ctx_mode", "kind", "reset_consol", "reset_forced",
        "reset_session", "ctx_pos", "k_ctx").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout")
                                                    & pl.col("agent").is_in(agents)).collect()
    lt = lt.with_columns(pl.col("t_call").dt.epoch("us").alias("tc_us")).sort("agent", "tc_us", "turn_id")
    lt = lt.with_columns(pl.int_range(pl.len()).over("agent").cast(pl.Int32).alias("n"),
                         (pl.col("reset_consol") | pl.col("reset_session")).cast(pl.Int32).cum_sum().over("agent").alias("seg"))
    return lt


def build_skeleton(goal_no: int, ps_kind: str = "talks", only_units: list | None = None, chat_mode: bool = False,
                   max_days: list | None = None) -> Skeleton:
    """ps_kind: 'talks' (scored talk calls) or 'wakes' (D2 timer-wake batches, #51)."""
    cr = chat_rows()
    pdays = period_days(goal_no, only_units)
    if max_days:
        pdays = pdays.filter(pl.col("pt_date").is_in(max_days))
    days = pdays["pt_date"].to_list()
    regime = pdays["regime"][0]
    u_of_day = dict(zip(pdays["pt_date"], pdays["unit_id"]))
    units = sorted(set(u_of_day.values()))
    uidx = {u: i for i, u in enumerate(units)}
    st = cr.filter(pl.col("pt_date").is_in(days) & pl.col("srow").is_not_null() & (pl.col("goal_no") == goal_no)
                   & (pl.col("speaker_kind").cast(pl.String) == "agent")).sort("t_us", "msg")
    ho = holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())
    st = st.filter(~pl.Series(ho))
    pc = pl.read_parquet(SHARED / "producing_calls.parquet", columns=["msg", "turn_id_prod"])
    st = st.join(pc, on="msg", how="left")
    agents = [int(a) for a in st["agent"].unique().to_list()]
    lt = ledger(goal_no, agents, days)
    st = st.join(lt.select(pl.col("turn_id").alias("turn_id_prod"), "n", "seg", "ctx_pos", "k_ctx", pl.col("tc_us").alias("tc_prod")),
                 on="turn_id_prod", how="left")
    fl = flags()
    st = st.join(fl.with_columns(pl.col("srow").cast(pl.UInt32)), on="srow", how="left")
    st = st.with_columns(pl.col("pt_date").replace_strict(u_of_day, default=None).alias("unit_id"))
    if chat_mode:
        # regime I/II: segment = PT day; call index from the ledger (all calls) when present
        st = st.with_columns(pl.col("pt_date").rank("dense").cast(pl.Int32).alias("seg"))
    st = st.sort("agent", "t_us", "msg").with_row_index("j")
    nst = len(st)
    A = st["agent"].to_numpy().astype(int); T = st["t_us"].to_numpy(); D = st["pt_date"].to_numpy()
    SEG = st["seg"].fill_null(-10**6).to_numpy(); TCP = st["tc_prod"].fill_null(st["t_us"]).to_numpy()
    NN = st["n"].fill_null(-1).to_numpy()
    U = np.array([uidx.get(u, -1) for u in st["unit_id"].to_list()])
    # earlier own in-segment statements (posted before the producing call's t_call)
    prev = [None] * nst
    prevseg = [None] * nst
    for a in np.unique(A):
        ia = np.flatnonzero(A == a)   # sorted by time
        segs = {}
        for j in ia:
            sg = SEG[j]
            lst = segs.get(sg, [])
            # statements in this segment posted strictly before this statement's producing call
            k = len(lst)
            while k > 0 and T[lst[k - 1]] >= TCP[j]:
                k -= 1
            prev[j] = lst[max(0, k - 4):k][::-1]          # newest first, up to 4
            pl_ = segs.get(sg - 1, [])
            prevseg[j] = pl_[-4:][::-1]
            nown = k
            st_n = nown
            prev[j] = (prev[j], st_n)
            lst = lst + [j]
            segs[sg] = lst
    n_own = np.array([p[1] for p in prev]); prev = [p[0] for p in prev]
    st = st.with_columns(pl.Series("n_own", n_own, dtype=pl.Int32), pl.Series("unit_ix", U, dtype=pl.Int16))
    # segment start kind per (agent, seg)
    sk = lt.filter(pl.col("reset_consol") | pl.col("reset_session")).select(
        "agent", "seg", pl.when(pl.col("reset_forced")).then(pl.lit("forced")).when(pl.col("reset_consol")).then(pl.lit("vol"))
        .otherwise(pl.lit("session")).alias("seg_kind")).unique(["agent", "seg"], keep="first")
    st = st.join(sk.with_columns(pl.col("agent").cast(st["agent"].dtype)), on=["agent", "seg"], how="left") \
        .with_columns(pl.col("seg_kind").fill_null("carry")).sort("j")
    # agent-day groups for well centres
    adk = (st["agent"].cast(pl.String) + "|" + st["pt_date"]).to_numpy()
    ad_u, ad_of_st = np.unique(adk, return_inverse=True)
    agent_of_ad = np.array([int(x.split("|")[0]) for x in ad_u])
    msg2j = dict(zip(st["msg"].to_list(), st["j"].to_list()))
    # ---- calls
    psd = SHARED / "pending_sets" / f"G{goal_no:02d}"
    if ps_kind == "talks":
        talks = pl.read_parquet(psd / "talks.parquet").filter(pl.col("pt_date").is_in(days))
        calls = talks.select(pl.col("talk_id").alias("cid"), "agent", "pt_date", "room", pl.col("s_us").alias("t_call_us"),
                             pl.col("t_us").alias("t_post_us"), pl.col("msg").cast(pl.UInt32).alias("resp_msg"),
                             pl.col("k").alias("k_pend"))
        pend = pl.read_parquet(psd / "pending.parquet").select(pl.col("talk_id").alias("cid"), "msg", "kind")
    else:
        wk = pl.read_parquet(psd / "wakes.parquet").filter(pl.col("talked") & pl.col("pt_date").is_in(days))
        wk = wk.with_columns((pl.col("t_wake_us") + (pl.col("delay_s").fill_null(0) * US).cast(pl.Int64)).alias("t_hint"))
        out = []
        by_a = {}
        for (a,), g in st.group_by(["agent"], maintain_order=True):
            by_a[int(a)] = (g["t_us"].to_numpy(), g["msg"].to_numpy(), g["room"].to_numpy())
        for r in wk.iter_rows(named=True):
            v = by_a.get(int(r["agent"]))
            if v is None:
                continue
            k = np.searchsorted(v[0], r["t_wake_us"], side="right")
            if k < len(v[0]) and v[0][k] <= r["t_hint"] + 5 * US:
                out.append((r["wake_id"], r["agent"], r["pt_date"], int(v[2][k]), r["t_wake_us"], int(v[0][k]), int(v[1][k]), r["k"]))
        calls = pl.DataFrame(out, schema={"cid": pl.Int32, "agent": pl.Int16, "pt_date": pl.String, "room": pl.Int16,
                                          "t_call_us": pl.Int64, "t_post_us": pl.Int64, "resp_msg": pl.UInt32, "k_pend": pl.Int32},
                             orient="row")
        pend = pl.read_parquet(psd / "wake_pending.parquet").select(pl.col("wake_id").cast(pl.Int32).alias("cid"), "msg", "kind")
    pend = pend.filter(pl.col("kind") == 0)
    bat = {int(c): [msg2j[int(m)] for m in g["msg"].to_list() if int(m) in msg2j]
           for (c,), g in pend.group_by(["cid"], maintain_order=True)}
    # room streams for in-flight and window field
    by_room = {}
    for (rm,), g in st.sort("t_us").group_by(["room"], maintain_order=True):
        by_room[int(rm)] = (g["t_us"].to_numpy(), g["j"].to_numpy(), g["agent"].to_numpy())
    st_seg = SEG; st_kind = st["seg_kind"].to_numpy()
    ctxp = st["ctx_pos"].to_numpy(); kctx = st["k_ctx"].to_numpy()
    tmpl = st["templated"].fill_null(False).to_numpy(); srep = st["self_repeat_both"].fill_null(False).to_numpy()
    srep1 = st["self_repeat"].fill_null(False).to_numpy()
    meta, Ip, Ip1, Iz, Is, IF, If, items = [], [], [], [], [], [], [], []
    y_idx, rooms, urow = [], [], []
    for r in calls.iter_rows(named=True):
        j = msg2j.get(int(r["resp_msg"]))
        if j is None or U[j] < 0:
            continue
        a = int(r["agent"]); tc = int(r["t_call_us"]); tp = int(r["t_post_us"])
        room = int(r["room"]) if r["room"] is not None else int(st["room"][j])
        b = bat.get(int(r["cid"]), [])
        # in-flight and field
        fl, fld = [], []
        vr = by_room.get(room)
        if vr is not None:
            lo = np.searchsorted(vr[0], tc, side="left"); hi = np.searchsorted(vr[0], tp, side="left")
            fl = [int(vr[1][q]) for q in range(lo, hi) if int(vr[2][q]) != a]
            lo2 = np.searchsorted(vr[0], tp - FIELD_WIN_S * US, side="left"); hi2 = np.searchsorted(vr[0], tp + FIELD_WIN_S * US, side="right")
            ex = set(b) | set(fl)
            fld = [int(vr[1][q]) for q in range(lo2, hi2) if int(vr[2][q]) != a and int(vr[1][q]) not in ex]
            if len(fld) < FIELD_MIN:
                fld = []
        modes = []
        pv = prev[j]
        if len(pv) >= 2:
            modes.append(("in", pv))
        if n_own[j] == 0 and st_kind[j] in ("forced", "vol") and len(prevseg[j]) >= 2:
            modes.append(("xreset", prevseg[j]))
        for pm, pv in modes:
            ri = len(meta)
            Ip.append(pv[:2]); Ip1.append(pv[:1]); Iz.append(pv[2:4] if len(pv) >= 4 else [])
            Is.append(b); IF.append(fl); If.append(fld)
            y_idx.append(j); rooms.append(room); urow.append(U[j])
            jl = pv[0]
            dn = int(NN[j] - NN[jl]) if NN[j] >= 0 and NN[jl] >= 0 else -1
            cp = ctxp[j]; kc = kctx[j]
            ss = float(cp) / (float(cp) + float(kc)) if cp is not None and kc is not None and np.isfinite(cp) and np.isfinite(kc) \
                and (cp + kc) > 0 else np.nan
            no = int(n_own[j])
            ssc = no / (no + float(kc)) if kc is not None and np.isfinite(kc) and (no + kc) > 0 else np.nan
            meta.append({"row": ri, "cid": int(r["cid"]), "pmode": pm, "agent": a, "pt_date": r["pt_date"], "unit_id": units[U[j]],
                         "room": room, "t_call_us": tc, "t_post_us": tp, "j": int(j), "srow": int(st["srow"][j]),
                         "k": len(b), "k_pend": r["k_pend"], "kF": len(fl), "has_field": len(fld) > 0, "has_z": len(pv) >= 4,
                         "n_prev": len(pv), "n_own": no, "ctx_pos": cp, "k_ctx": kc, "s_self": ss, "s_self_chat": ssc,
                         "dn": dn, "dt_s": float((tp - T[jl]) / US), "seg_kind": st_kind[j], "templated": bool(tmpl[j]), "self_repeat_both": bool(srep[j]),
                         "self_repeat": bool(srep1[j])})
            # O4 items: read items with age <= 120 s and all in-flight items (in-segment rows only)
            if pm == "in":
                for m in b:
                    age = (tp - T[m]) / US
                    if age <= AGE_MAX_S:
                        items.append((ri, int(m), True, float(age)))
                for m in fl:
                    items.append((ri, int(m), False, float((tp - T[m]) / US)))
    nr = len(meta)
    rows = pl.DataFrame(meta)

    def mat(lists, mean: bool):
        indptr = np.cumsum([0] + [len(x) for x in lists]); ind = np.fromiter((i for x in lists for i in x), dtype=np.int64,
                                                                             count=int(indptr[-1]))
        if mean:
            dat = np.concatenate([np.full(len(x), 1.0 / len(x)) for x in lists if len(x)]) if indptr[-1] else np.zeros(0)
        else:
            dat = np.ones(len(ind))
        return sp.csr_matrix((dat, ind, indptr), shape=(nr, nst))
    it = pl.DataFrame(items, schema={"row": pl.Int32, "j": pl.Int32, "read": pl.Boolean, "age_s": pl.Float32}, orient="row")
    sk_ = Skeleton(goal_no=goal_no, regime=regime, st=st, rows=rows, Mp=mat(Ip, True), Mp1=mat(Ip1, True), Mz=mat(Iz, True),
                   Ms=mat(Is, False), MF=mat(IF, False), Mf=mat(If, True), y_idx=np.array(y_idx, dtype=np.int64),
                   ad_idx=ad_of_st[np.array(y_idx, dtype=np.int64)] if nr else np.zeros(0, int), ad_of_st=ad_of_st,
                   agent_of_ad=agent_of_ad, unit_of_row=np.array(urow), unit_of_st=U, units=units, rooms=np.array(rooms),
                   items=it, sur=np.full((nr, N_SUR), -1))
    sk_.sur = surrogates(sk_)
    # extras for the synthetic generator: every statement's in-segment history, batch (if it is a scored y), self-share
    bos = {}
    for jy, bl, pm in zip(y_idx, Is, rows["pmode"].to_list() if nr else []):
        if pm == "in":
            bos[int(jy)] = bl
    cpa = np.asarray(ctxp, dtype=float); kca = np.asarray(kctx, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        ss_all = cpa / (cpa + kca)
    sk_.extra = {"prev": prev, "batch": bos, "s_self": ss_all, "n": NN, "t_us": T, "agent": A, "room": st["room"].to_numpy()}
    return sk_


def surrogates(sk: Skeleton, seed: int = 0) -> np.ndarray:
    """N1: for each row, N_SUR rows of the same unit, room and batch size k from other PT days (in-segment rows)."""
    rng = np.random.default_rng(seed)
    r = sk.rows
    out = np.full((len(r), N_SUR), -1, dtype=np.int64)
    if len(r) == 0:
        return out
    key = r.select("unit_id", "room", "k", "pt_date", "row", "pmode").filter(pl.col("pmode") == "in")
    for (u, rm, k), g in key.group_by(["unit_id", "room", "k"]):
        if k == 0:
            continue
        rr = g["row"].to_numpy(); dd = g["pt_date"].to_numpy()
        for i, d in zip(rr, dd):
            cand = rr[dd != d]
            if len(cand):
                out[i] = rng.choice(cand, N_SUR, replace=True)
    return out


# ------------------------------------------------------------------------------------------------ vectors -> Gram
def wells(sk: Skeleton, V: np.ndarray) -> np.ndarray:
    """Leave-day-out well centre per agent-day group (nan rows where < MIN_WELL statements on other days).
    V: statement vectors aligned to sk.st order (n_st x 32)."""
    nad = len(sk.agent_of_ad)
    S = np.zeros((nad, V.shape[1])); N = np.zeros(nad)
    np.add.at(S, sk.ad_of_st, V); np.add.at(N, sk.ad_of_st, 1)
    W = np.full_like(S, np.nan)
    for a in np.unique(sk.agent_of_ad):
        ia = np.flatnonzero(sk.agent_of_ad == a)
        tot = S[ia].sum(0); n = N[ia].sum()
        m = n - N[ia]
        ok = m >= MIN_WELL
        W[ia[ok]] = (tot[None, :] - S[ia[ok]]) / m[ok, None]
    return W


def gram_rows(sk: Skeleton, V: np.ndarray, model: str = "bge_small", field: bool = False, Gb: dict | None = None,
              with_items: bool = True, with_sur: bool = True):
    """V: statement vectors in sk.st order (n_st x 32). Returns (gram frame, items frame or None, ok mask)."""
    V = np.asarray(V, dtype=np.float64)
    nr = len(sk.rows)
    # unit means
    nu = len(sk.units)
    mu = np.zeros((nu, 32))
    for u in range(nu):
        m = sk.unit_of_st == u
        if m.any():
            mu[u] = V[m].mean(0)
    mr = mu[sk.unit_of_row]
    W = wells(sk, V)
    H = W[sk.ad_idx]
    hok = np.isfinite(H).all(1)
    H = np.nan_to_num(H)
    k = np.asarray(sk.Ms.sum(1)).ravel(); kF = np.asarray(sk.MF.sum(1)).ravel()
    vec = {"y": V[sk.y_idx] - mr, "p": sk.Mp @ V - mr, "p1": sk.Mp1 @ V - mr, "z": sk.Mz @ V - mr,
           "s": sk.Ms @ V - k[:, None] * mr, "sF": sk.MF @ V - kF[:, None] * mr, "h": H - mr, "f": sk.Mf @ V - mr}
    zok = np.asarray(sk.Mz.sum(1)).ravel() > 0.5
    vec["z"][~zok] = 0.0
    fok0 = np.asarray(sk.Mf.sum(1)).ravel() > 0.5
    vec["f"][~fok0] = 0.0
    # projection per room
    if Gb is None:
        Gb = {rm: orth_projector(goal_basis(sk.goal_no, rm if rm >= 0 else None, model, sk.regime)) for rm in np.unique(sk.rooms)}
    for rm in np.unique(sk.rooms):
        sel = sk.rooms == rm
        P = Gb[rm]
        for kk in vec:
            vec[kk][sel] = vec[kk][sel] @ P
    fok = np.asarray(sk.Mf.sum(1)).ravel() > 0.5
    if field:
        f = sk.Mf @ V - mr
        for rm in np.unique(sk.rooms):
            sel = sk.rooms == rm
            f[sel] = f[sel] @ Gb[rm]
        f /= np.linalg.norm(f, axis=1, keepdims=True) + 1e-12
        f[~fok] = 0.0
        for kk in vec:
            if kk != "f":
                vec[kk] = vec[kk] - (vec[kk] * f).sum(1, keepdims=True) * f
    cols = {f"g_{a}_{b}": np.einsum("ij,ij->i", vec[a], vec[b]).astype(np.float32) for a, b in PAIRS}
    out = pl.DataFrame(cols).with_columns(pl.Series("h_ok", hok), pl.Series("z_ok", zok), pl.Series("f_ok", fok))
    if with_sur:
        S = vec["s"]
        for d in range(N_SUR):
            idx = sk.sur[:, d]
            ok = idx >= 0
            Ssur = np.where(ok[:, None], S[np.maximum(idx, 0)], 0.0)
            for bname in ("y", "p", "p1", "z", "sF", "h"):
                out = out.with_columns(pl.Series(f"u{d}_{bname}", np.einsum("ij,ij->i", vec[bname], Ssur).astype(np.float32)))
            out = out.with_columns(pl.Series(f"u{d}_ss", np.einsum("ij,ij->i", Ssur, Ssur).astype(np.float32)))
    it = None
    if with_items and len(sk.items):
        r = sk.items["row"].to_numpy(); jj = sk.items["j"].to_numpy()
        X = V[jj] - mr[r]
        for rm in np.unique(sk.rooms):
            sel = sk.rooms[r] == rm
            X[sel] = X[sel] @ Gb[rm]
        if field:
            X = X - (X * f[r]).sum(1, keepdims=True) * f[r]
        # H113 O5 convention: y and x orthogonalized to the reader's own recent content p
        pu = vec["p"] / (np.linalg.norm(vec["p"], axis=1, keepdims=True) + 1e-12)
        yo = vec["y"] - (vec["y"] * pu).sum(1, keepdims=True) * pu
        Xo = X - (X * pu[r]).sum(1, keepdims=True) * pu[r]
        it = sk.items.with_columns(pl.Series("xy", np.einsum("ij,ij->i", Xo, yo[r]).astype(np.float32)),
                                   pl.Series("xx", np.einsum("ij,ij->i", Xo, Xo).astype(np.float32)))
    return out, it, Gb


def real_vectors(sk: Skeleton, model: str, variant: str = "style_resid32") -> np.ndarray:
    V = vectors(model, variant)
    return np.asarray(V[sk.st["srow"].to_numpy()], dtype=np.float64)
