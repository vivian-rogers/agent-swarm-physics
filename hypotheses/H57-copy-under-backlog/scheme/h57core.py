"""H57 core: read-set skeletons (statements, read sets R, time-mirrored placebo sets F) and content outcomes.

The skeleton is structure only (who read what, when); the outcome functions take any content (real embeddings and
H34 markers, or synthetic ones), so the synthetic validation runs the exact real-data code path.

Skeleton (one goal period, non-holdout days only):
  S  statements: sid, msg (chat_core row), agent, lab, unit_id, pt_date, room, t, t_call, turn_id, ctx_mode, regime,
     n_chars, k (|R|), k_since_talk, k_ctx, ctx_pos, f_n, f_full, is_reply, early, day_idx, phase, daypos,
     NE41 helpers (pos_after, last_forced, pos_before, next_forced, next_same_day)
  P  pairs: sid, msg (item chat_core row), set, rank
       set 0 = read set R (rank 1 = newest); 1 = time-mirrored placebo F (rank 1 = first after t_call; descriptive
       only: contaminated by others copying B, see the card's Amendment 1); 2 = mutually invisible in-flight set I
       (other agents' statements posted after B's call started whose own call started before B was posted);
       3 = DQ2 reply parent of B (agent parents only; one row when it exists)
       4 = addressed source: the latest read item whose author B names (one row when it exists)

Read set R(B) ("Backlog (in-context read set)"): agent-authored context-ledger items received by the author's calls
after its previous talk call up to and including B's call, same PT day; in computer-use calls only items after the
last context reset in that span.
Placebo F(B) ("Placebo read set (time-mirrored)"): the first k agent messages in B's room, same day, posted at or after
B's call start by other agents, excluding messages whose DQ2 reply parent is B.
No text is read anywhere in this module.
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
H34 = ROOT / "data/processed/H34-idea-cascades/markers"
OUT = ROOT / "data/processed/H57-copy-under-backlog"
MODELS = ("bge", "gte")
MODEL_FILE = {"bge": "bge_small", "gte": "gte_modernbert"}
THR = {"bge": 0.95, "gte": 0.938}          # DQ5 near-copy thresholds (raw cosine; gte rate-matched)
TALK_TOL_S = 3.0                            # chat row -> talk call (chat rows precede t_first by ~40 ms)
COMMON_FRAC = 0.02                          # marker used in >= 2% of the period's chat messages -> common
COMMON_DAY1_AGENTS = 3                      # or by >= 3 agents on the period's first active day -> common
INFLIGHT_CAP_S = 900                        # in-flight search stops 15 min after B (calls longer than that are rare)
LAG_EDGES = [15.0, 30.0, 60.0]              # lag bins (s) for the lag-matched chance model (Amendment 2, post hoc)


# ------------------------------------------------------------------------------------------------ base tables
@lru_cache(maxsize=1)
def chat() -> pl.DataFrame:
    cc = pl.read_parquet(SH / "chat_core.parquet",
                         columns=["message_id", "t", "pt_date", "goal_no", "regime", "room", "speaker_kind", "agent",
                                  "length"]).with_row_index("msg")
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "holdout"]).rename({"holdout": "cal_ho"})
    cc = cc.join(cal, on="pt_date", how="left", maintain_order="left")
    hm = np.array(holdout_mask(cc["pt_date"].to_list(), cc["goal_no"].to_list()))
    ho = hm | cc["cal_ho"].fill_null(False).to_numpy()
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("crow")
    cc = cc.with_columns(pl.Series("holdout", ho)).drop("cal_ho").join(ci, on="message_id", how="left",
                                                                         maintain_order="left")
    return cc.with_columns(pl.col("regime").cast(pl.Utf8))


@lru_cache(maxsize=1)
def roster() -> pl.DataFrame:
    return pl.read_parquet(SH / "roster.parquet", columns=["agent", "name", "lab", "claude_code"])


@lru_cache(maxsize=1)
def ledger_turns() -> pl.DataFrame:
    lt = pl.read_parquet(SH / "context_ledger_turns.parquet",
                         columns=["turn_id", "agent", "pt_date", "goal_no", "holdout", "t_call", "t_first", "talk",
                                  "ctx_mode", "k_since_talk", "k_ctx", "ctx_pos", "reset_consol", "reset_forced",
                                  "reset_session", "first_of_day", "n_agent", "k_new"])
    lt = lt.sort("turn_id").with_columns(
        pl.col("talk").cast(pl.Int32).cum_sum().shift(1, fill_value=0).over("agent").alias("tg"),
        (pl.col("reset_consol") | pl.col("reset_session") | pl.col("first_of_day")).alias("reset_any"))
    return lt


@lru_cache(maxsize=1)
def ledger_items() -> pl.DataFrame:
    return pl.read_parquet(SH / "context_ledger_items.parquet", columns=["turn_id", "message_id", "kind"]).filter(
        pl.col("kind") == "agent")


@lru_cache(maxsize=1)
def parents() -> pl.DataFrame:
    rp = pl.scan_parquet(SH / "reply_pairs.parquet").filter(pl.col("parent")).select(
        "B_message_id", "A_message_id").collect()
    return rp.unique("B_message_id")


@lru_cache(maxsize=1)
def units() -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet", columns=["unit_id", "goal_no", "days", "holdout", "first_day"])
    return pu.explode("days").rename({"days": "pt_date"}).select("unit_id", "goal_no", "pt_date", "holdout")


@lru_cache(maxsize=1)
def calendar() -> pl.DataFrame:
    return pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "win_start", "win_end", "goal_no"])


def ne41_helpers(lt: pl.DataFrame) -> pl.DataFrame:
    """Per receiving call: position after the last reset and before the next one, and whether each is forced."""
    r = lt.filter(pl.col("ctx_mode") != "summary").select("turn_id", "agent", "pt_date", "reset_consol",
                                                         "reset_forced").sort("turn_id")
    r = r.with_columns(pl.col("reset_consol").cast(pl.Int32).cum_sum().over("agent").alias("seg"))
    seg = (r.group_by("agent", "seg").agg(pl.col("turn_id").min().alias("seg_t0"), pl.len().alias("seg_len"),
                                          pl.col("reset_forced").first().alias("seg_forced"),
                                          pl.col("reset_consol").first().alias("seg_is_reset"),
                                          pl.col("pt_date").first().alias("seg_day"))
           .sort("agent", "seg")
           .with_columns(pl.col("seg_forced").shift(-1).over("agent").alias("next_forced"),
                         (pl.col("seg_is_reset") & ~pl.col("seg_forced")).shift(-1).over("agent").alias("next_vol"),
                         pl.col("seg_day").shift(-1).over("agent").alias("next_day")))
    r = r.join(seg, on=["agent", "seg"], how="left").with_columns(
        (pl.col("turn_id").rank("ordinal").over("agent", "seg")).cast(pl.Int32).alias("pos_after"))
    r = r.with_columns((pl.col("seg_len") - pl.col("pos_after") + 1).cast(pl.Int32).alias("pos_before"),
                       (pl.col("seg_forced") & pl.col("seg_is_reset")).alias("last_forced"),
                       (~pl.col("seg_forced") & pl.col("seg_is_reset")).alias("last_vol"),
                       (pl.col("next_day") == pl.col("pt_date")).fill_null(False).alias("next_same_day"))
    return r.select("turn_id", "pos_after", "last_forced", "last_vol", "pos_before",
                    pl.col("next_forced").fill_null(False), pl.col("next_vol").fill_null(False), "next_same_day")


# ------------------------------------------------------------------------------------------------ skeleton
def build_skeleton(goal_no: int, allow_holdout: bool = False) -> tuple[pl.DataFrame, pl.DataFrame]:
    """allow_holdout=True only from analysis/confirm.py under its guard flags (locked-holdout confirmation)."""
    cc = chat()
    HO = pl.lit(False) if allow_holdout else pl.col("holdout")
    cc_p = cc.filter((pl.col("goal_no") == goal_no) & ~HO)
    ros = roster()
    cc_agents = cc_p.filter(pl.col("speaker_kind") == "agent").join(
        ros.select("agent", "lab", "claude_code"), on="agent", how="left").filter(~pl.col("claude_code").fill_null(False))
    if cc_agents.height == 0:
        return pl.DataFrame(), pl.DataFrame()
    days = cc_agents["pt_date"].unique().to_list()
    lt = ledger_turns().filter(pl.col("pt_date").is_in(days) & (~pl.col("holdout") | pl.lit(allow_holdout)))
    talk = lt.filter(pl.col("talk")).select("turn_id", "agent", "t_first", "t_call", "tg", "ctx_mode", "k_since_talk",
                                            "k_ctx", "ctx_pos").sort("t_first")
    # 1. statement -> talk call (nearest t_first within tolerance)
    st = cc_agents.select("msg", "message_id", "agent", "lab", "pt_date", "room", "t", "length", "regime").sort("t")
    st = st.join_asof(talk, left_on="t", right_on="t_first", by="agent", strategy="nearest",
                      tolerance=f"{int(TALK_TOL_S * 1000)}ms", check_sortedness=False)
    st = st.filter(pl.col("turn_id").is_not_null())
    # 2. read sets
    items = ledger_items()
    lt_small = lt.select("turn_id", "agent", "tg", "reset_any", "ctx_mode")
    items = items.join(lt_small, on="turn_id", how="inner")
    msgid = cc.select("message_id", pl.col("msg").alias("imsg"), pl.col("pt_date").alias("ipt"),
                      pl.col("t").alias("it"), pl.col("holdout").alias("iho"))
    items = items.join(msgid, on="message_id", how="left").filter(~pl.col("iho") | pl.lit(allow_holdout))
    # last reset call in each talk group, up to the talk call (cu mode only)
    resets = lt_small.filter(pl.col("reset_any") & (pl.col("ctx_mode") == "cu")).select(
        "agent", "tg", pl.col("turn_id").alias("r_turn"))
    stg = st.select("msg", "agent", "tg", pl.col("turn_id").alias("b_turn"), pl.col("ctx_mode").alias("b_mode"),
                    pl.col("pt_date").alias("b_pt"), pl.col("t_call").alias("b_tcall"))
    last_r = (stg.join(resets, on=["agent", "tg"], how="inner").filter(pl.col("r_turn") <= pl.col("b_turn"))
              .group_by("msg").agg(pl.col("r_turn").max().alias("r_turn")))
    stg = stg.join(last_r, on="msg", how="left")
    pr = (stg.join(items.select("agent", "tg", "turn_id", "imsg", "ipt", "it"), on=["agent", "tg"], how="inner")
          .filter((pl.col("turn_id") <= pl.col("b_turn")) & (pl.col("ipt") == pl.col("b_pt")))
          .filter(pl.col("r_turn").is_null() | (pl.col("b_mode") != "cu") | (pl.col("turn_id") >= pl.col("r_turn"))))
    pr = pr.unique(["msg", "imsg"]).with_columns(
        pl.col("it").rank("ordinal", descending=True).over("msg").cast(pl.Int32).alias("rank"))
    kR = pr.group_by("msg").agg(pl.len().cast(pl.Int32).alias("k"))
    st = st.join(kR, on="msg", how="left").with_columns(pl.col("k").fill_null(0))
    # 3. placebo sets (time-mirrored, same room-day, other agents, not replies to B)
    par = parents()
    reply_to = par.join(cc.select("message_id", pl.col("msg").alias("cmsg")), left_on="B_message_id",
                        right_on="message_id", how="inner").join(
        cc.select("message_id", pl.col("msg").alias("pmsg")), left_on="A_message_id", right_on="message_id",
        how="inner").select("cmsg", "pmsg")
    child_of = {}
    for c_, p_ in zip(reply_to["cmsg"].to_list(), reply_to["pmsg"].to_list()):
        child_of[c_] = p_
    pool = cc_agents.select("msg", "agent", "pt_date", "room", "t").sort("t")
    F_sid, F_msg, F_rank, f_n = [], [], [], []
    st = st.sort("msg")
    grp = {key: (g["t"].to_numpy(), g["msg"].to_numpy(), g["agent"].to_numpy())
           for key, g in pool.group_by(["pt_date", "room"])}
    for msg_b, ag_b, pt_b, room_b, tcall_b, k_b in zip(st["msg"].to_list(), st["agent"].to_list(),
                                                        st["pt_date"].to_list(), st["room"].to_list(),
                                                        st["t_call"].to_numpy(), st["k"].to_list()):
        n = 0
        if k_b > 0:
            tt, mm, aa = grp[(pt_b, room_b)]
            j = int(np.searchsorted(tt, tcall_b, side="left"))
            while j < len(tt) and n < k_b:
                m_ = int(mm[j])
                if aa[j] != ag_b and child_of.get(m_) != msg_b and m_ != msg_b:
                    n += 1
                    F_sid.append(msg_b); F_msg.append(m_); F_rank.append(n)
                j += 1
        f_n.append(n)
    st = st.with_columns(pl.Series("f_n", f_n, dtype=pl.Int32)).with_columns((pl.col("f_n") == pl.col("k")).alias("f_full"))
    # 3b. mutually invisible (in-flight) set I(B): statements C in B's room-day by other agents with
    #     t_C >= t_call(B) (B could not see C) and t_call(C) < t_B (C's context was assembled before B existed)
    I_sid, I_msg, I_rank, i_n = [], [], [], []
    pool_s = st.select("msg", "agent", "pt_date", "room", "t", "t_call").sort("t")
    gs = {key: (g["t"].to_numpy(), g["t_call"].to_numpy(), g["msg"].to_numpy(), g["agent"].to_numpy())
          for key, g in pool_s.group_by(["pt_date", "room"])}
    cap = np.timedelta64(int(INFLIGHT_CAP_S * 1e6), "us")
    for msg_b, ag_b, pt_b, room_b, tcall_b, t_b in zip(st["msg"].to_list(), st["agent"].to_list(),
                                                       st["pt_date"].to_list(), st["room"].to_list(),
                                                       st["t_call"].to_numpy(), st["t"].to_numpy()):
        tt, tc, mm, aa = gs[(pt_b, room_b)]
        j = int(np.searchsorted(tt, tcall_b, side="left"))
        n = 0
        while j < len(tt) and tt[j] <= t_b + cap:
            if aa[j] != ag_b and tc[j] < t_b and int(mm[j]) != msg_b:
                n += 1
                I_sid.append(msg_b); I_msg.append(int(mm[j])); I_rank.append(n)
            j += 1
        i_n.append(n)
    st = st.with_columns(pl.Series("i_n", i_n, dtype=pl.Int32))
    # 3c. DQ2 reply parent of B and its candidate-pool size
    rp_all = pl.scan_parquet(SH / "reply_pairs.parquet").filter(pl.col("parent")).select(
        pl.col("b_msg"), "B_message_id", "A_message_id", "n_pool").collect().unique("B_message_id")
    par_b = (rp_all.join(cc.select("message_id", pl.col("msg").alias("msg")), left_on="B_message_id",
                         right_on="message_id", how="inner")
             .join(cc.select("message_id", pl.col("msg").alias("par_msg"), pl.col("holdout").alias("par_ho"),
                             pl.col("speaker_kind").cast(pl.Utf8).alias("par_kind")),
                   left_on="A_message_id", right_on="message_id", how="inner")
             .filter((~pl.col("par_ho") | pl.lit(allow_holdout)) & (pl.col("par_kind") == "agent"))   # agents only
             .select("msg", "par_msg", pl.col("n_pool").cast(pl.Int16)))
    st = st.join(par_b, on="msg", how="left")
    npool = (pl.scan_parquet(SH / "reply_pairs.parquet").filter(pl.col("pair_set") == "cand")
             .select("B_message_id", "n_pool").collect().unique("B_message_id")
             .join(cc.select("message_id", "msg"), left_on="B_message_id", right_on="message_id", how="inner")
             .select("msg", pl.col("n_pool").cast(pl.Int16).alias("n_pool_all")))
    st = st.join(npool, on="msg", how="left")
    # 3d. addressed source: the latest read item whose author B names (chat_mentions_clean.mentions_roster)
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    men = men.join(cc.select("message_id", "msg"), on="message_id", how="inner").select("msg", "mentions_roster")
    named = st.select("msg").join(men, on="msg", how="inner").explode("mentions_roster").drop_nulls().rename(
        {"mentions_roster": "named"})
    snd = cc.select(pl.col("msg").alias("imsg"), pl.col("agent").alias("isender"))
    addr = (pr.select("msg", "imsg", "it").join(snd, on="imsg", how="left")
            .join(named, left_on=["msg", "isender"], right_on=["msg", "named"], how="inner")
            .sort("it").group_by("msg").agg(pl.col("imsg").last().alias("addr_msg"), pl.len().alias("addr_n")))
    st = st.join(addr, on="msg", how="left").with_columns(
        pl.col("addr_msg").is_not_null().alias("addressed"), pl.col("addr_n").fill_null(0).cast(pl.Int16))
    inR = pr.select("msg", pl.col("imsg").alias("par_msg")).with_columns(pl.lit(True).alias("par_in_R"))
    st = st.join(inR, on=["msg", "par_msg"], how="left").with_columns(pl.col("par_in_R").fill_null(False))
    # 4. controls
    is_rep = set(reply_to["cmsg"].to_list())
    st = st.with_columns(pl.col("msg").is_in(list(is_rep)).alias("is_reply"))
    un = units().filter(pl.col("goal_no") == goal_no)
    st = st.join(un.select("unit_id", "pt_date"), on="pt_date", how="left")
    days_sorted = sorted(set(days))
    first_day = days_sorted[0]
    dix = {d: i for i, d in enumerate(days_sorted)}
    cal = calendar().select("pt_date", "win_start", "win_end")
    st = st.join(cal, on="pt_date", how="left").with_columns(
        (pl.col("pt_date") == first_day).alias("early"),
        pl.col("pt_date").replace_strict(dix, return_dtype=pl.Int16).alias("day_idx"),
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() /
         (pl.col("win_end") - pl.col("win_start")).dt.total_seconds()).clip(0, 1).alias("daypos"))
    st = st.with_columns((pl.col("day_idx") / max(1, len(days_sorted) - 1)).alias("phase"))
    st = st.join(ne41_helpers(lt), on="turn_id", how="left")
    st = st.sort("t").with_row_index("sid").with_columns(pl.col("sid").cast(pl.Int32))
    sid_of = dict(zip(st["msg"].to_list(), st["sid"].to_list()))
    PR = pr.select(pl.col("msg").replace_strict(sid_of, return_dtype=pl.Int32).alias("sid"), pl.col("imsg").alias("msg"),
                   pl.lit(0, dtype=pl.Int8).alias("set"), "rank")
    PF = pl.DataFrame({"sid": [sid_of[x] for x in F_sid], "msg": F_msg, "set": [1] * len(F_msg), "rank": F_rank},
                      schema={"sid": pl.Int32, "msg": pl.UInt32, "set": pl.Int8, "rank": pl.Int32})
    PI = pl.DataFrame({"sid": [sid_of[x] for x in I_sid], "msg": I_msg, "set": [2] * len(I_msg), "rank": I_rank},
                      schema={"sid": pl.Int32, "msg": pl.UInt32, "set": pl.Int8, "rank": pl.Int32})
    par = st.filter(pl.col("par_msg").is_not_null())
    PPAR = pl.DataFrame({"sid": [sid_of[x] for x in par["msg"].to_list()], "msg": par["par_msg"].to_list(),
                         "set": [3] * par.height, "rank": [1] * par.height},
                        schema={"sid": pl.Int32, "msg": pl.UInt32, "set": pl.Int8, "rank": pl.Int32})
    ad = st.filter(pl.col("addr_msg").is_not_null())
    PADDR = pl.DataFrame({"sid": [sid_of[x] for x in ad["msg"].to_list()], "msg": ad["addr_msg"].to_list(),
                          "set": [4] * ad.height, "rank": [1] * ad.height},
                         schema={"sid": pl.Int32, "msg": pl.UInt32, "set": pl.Int8, "rank": pl.Int32})
    P = pl.concat([PR.with_columns(pl.col("msg").cast(pl.UInt32)), PF, PI, PPAR, PADDR]).sort("sid", "set", "rank")
    S = st.select("sid", "msg", "agent", "lab", "unit_id", "pt_date", "room", "t", "t_call", "turn_id", "ctx_mode",
                  "regime", pl.col("length").alias("n_chars"), "k", "k_since_talk", "k_ctx", "ctx_pos", "f_n", "f_full",
                  "is_reply", "early", "day_idx", "phase", "daypos", "pos_after", "last_forced", "last_vol",
                  "pos_before", "next_forced", "next_vol", "next_same_day", "i_n", "par_msg", "n_pool", "n_pool_all", "par_in_R", "addr_msg",
                  "addressed", "addr_n").with_columns(pl.lit(goal_no, dtype=pl.Int8).alias("goal_no"))
    return S, P


# ------------------------------------------------------------------------------------------------ content (real)
def holdout_markers(msgs: np.ndarray) -> pl.DataFrame:
    """H34 marker rule applied in memory to messages without stored markers (held-out text; confirm.py only).
    Read-only import of hypotheses/H34-idea-cascades/scheme/markers.py; no text is written."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("h34markers", ROOT / "hypotheses/H34-idea-cascades/scheme/markers.py")
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    M.dictionary()
    ros = frozenset(M.roster_full_names(pl.read_parquet(SH / "roster.parquet")["name"].to_list()))
    ids = chat()[msgs.astype(np.int64)].select("msg", "message_id")
    txt = pl.scan_parquet(SH / "chat_text.parquet").select("message_id", "text").join(
        ids.lazy(), on="message_id", how="inner").collect()
    rows = [(int(m), int(M.marker_id(c, x))) for m, t in zip(txt["msg"].to_list(), txt["text"].to_list())
            for c, x in M.extract(t or "", ros)]
    return pl.DataFrame(rows, schema={"msg": pl.UInt32, "marker": pl.Int64}, orient="row").unique()


def load_real_content(msgs: np.ndarray, allow_holdout: bool = False) -> dict:
    """Content for a set of chat_core rows: raw unit embeddings (per model), regime-whitened 32-d unit vectors, and
    H34 marker frames (non-holdout only). Returned arrays are indexed by position in `msgs`."""
    import embed_models as EM
    cc = chat()
    sub = cc[msgs.astype(np.int64)]
    crow = sub["crow"].to_numpy()
    reg = sub["regime"].to_numpy()
    out = {"msgs": msgs, "raw": {}, "white": {}}
    for m in MODELS:
        E = np.load(EM.emb_path("chat", MODEL_FILE[m]), mmap_mode="r")
        X = np.asarray(E[crow], dtype=np.float32)
        X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
        out["raw"][m] = X
        Wt = np.zeros((len(msgs), 32), dtype=np.float32)
        for r in np.unique(reg):
            W = EM.load_whitener(r, 32, MODEL_FILE[m])
            idx = np.flatnonzero(reg == r)
            Z = W(X[idx])
            Wt[idx] = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-12)
        out["white"][m] = Wt
    uses = pl.scan_parquet(H34 / "uses.parquet").filter(pl.col("msg").is_in(msgs.tolist())).select("msg",
                                                                                                    "marker").collect()
    uses = uses.unique()
    if allow_holdout:
        ho = chat()[msgs.astype(np.int64)].filter(pl.col("holdout"))["msg"].to_numpy()
        if len(ho):
            uses = pl.concat([uses.with_columns(pl.col("msg").cast(pl.UInt32)), holdout_markers(ho)])
    out["markers"] = uses
    return out


def kickoff_vectors(goal_no: int) -> dict:
    import embed_models as EM
    g = pl.read_parquet(ED / "goals.parquet", columns=["gid", "goal_no", "kind"]).filter(
        (pl.col("goal_no") == goal_no) & pl.col("kind").cast(pl.Utf8).is_in(["kickoff", "kickoff_room"]))
    out = {}
    for m in MODELS:
        G = EM.goal_vectors(MODEL_FILE[m]).astype(np.float32)[g["gid"].to_numpy()]
        out[m] = G / (np.linalg.norm(G, axis=1, keepdims=True) + 1e-12)
    return out


# ------------------------------------------------------------------------------------------------ helpers
def spherical_kmeans(X: np.ndarray, K: int, seed: int = 0, iters: int = 40) -> tuple[np.ndarray, np.ndarray]:
    """Cosine k-means (k-means++ init) on unit vectors. Returns (centroids, labels)."""
    rng = np.random.default_rng(seed)
    n = len(X)
    K = min(K, n)
    C = np.empty((K, X.shape[1]), dtype=np.float64)
    C[0] = X[rng.integers(n)]
    d = 1 - X @ C[0]
    for j in range(1, K):
        p = np.clip(d, 0, None) ** 2
        p = p / p.sum() if p.sum() > 0 else np.full(n, 1 / n)
        C[j] = X[rng.choice(n, p=p)]
        d = np.minimum(d, 1 - X @ C[j])
    lab = np.zeros(n, dtype=np.int32)
    for _ in range(iters):
        S = X @ C.T
        new = S.argmax(1).astype(np.int32)
        if _ > 0 and np.array_equal(new, lab):
            break
        lab = new
        for j in range(K):
            mj = lab == j
            if mj.any():
                v = X[mj].sum(0)
                C[j] = v / (np.linalg.norm(v) + 1e-12)
            else:
                C[j] = X[rng.integers(n)]
    return C.astype(np.float32), lab


def group_max(vals: np.ndarray, gid: np.ndarray, n_groups: int, fill=np.nan):
    """Max and argmax (position into vals) per group id (gid sorted not required)."""
    order = np.lexsort((vals, gid))
    g = gid[order]
    last = np.r_[np.flatnonzero(np.diff(g)), len(g) - 1] if len(g) else np.array([], int)
    mx = np.full(n_groups, fill, dtype=np.float64)
    am = np.full(n_groups, -1, dtype=np.int64)
    if len(g):
        mx[g[last]] = vals[order[last]]
        am[g[last]] = order[last]
    return mx, am


# ------------------------------------------------------------------------------------------------ outcomes
def outcomes(S: pl.DataFrame, P: pl.DataFrame, content: dict, K_list=(16, 32, 64), common: set | None = None,
             kick: dict | None = None, seed: int = 0, thr: dict | None = None) -> pl.DataFrame:
    """Per-statement outcomes for the four pair sets (suffix R = read set, F = mirrored placebo, I = in-flight set,
    par = DQ2 reply parent).

    content: {"msgs": global ids aligned with arrays, "raw": {m: unit vectors}, "white": {m: unit 32-d},
              "markers": DataFrame(msg, marker)}.
    common:  marker ids treated as common (shared sources); "rare" versions use M minus common.
    kick:    {m: unit kickoff vectors} -> kick_cos_{m} (max over the period's kickoff vectors).
    Columns (per model m): maxcos_{m}_{R,F}, echo_{m}_{R,F} (max >= thr), nI, nnear_{m}_I (in-flight pairs above
    thr), cos_{m}_par, near_{m}_par, wmax_{m}_{R,F}; codes y_{m}_K, x_{m}_K_{R,F,I} (newest read item / first
    placebo / first in-flight item), xmax_{m}_K_{R,F} (most similar item), xpar_{m}_K (parent); markers
    mk_n_{f}, mk_share_{f}_{R,F}, mk_near_{f}_{R,F} (max Jaccard >= 0.5), nmknear_{f}_I, mkj_{f}_par.
    """
    thr = thr or THR
    n = S.height
    assert np.array_equal(S["sid"].to_numpy(), np.arange(n)), "S must be sorted by sid = 0..n-1"
    NS = 5
    SUF = {0: "R", 1: "F", 2: "I", 3: "par", 4: "addr"}
    pos = {int(g): i for i, g in enumerate(content["msgs"])}
    b_loc = np.array([pos[int(x)] for x in S["msg"].to_list()], dtype=np.int64)
    p_sid = P["sid"].to_numpy().astype(np.int64)
    p_set = P["set"].to_numpy().astype(np.int64)
    p_rank = P["rank"].to_numpy()
    p_loc = np.array([pos[int(x)] for x in P["msg"].to_list()], dtype=np.int64)
    gid = p_sid * NS + p_set
    out = {"sid": S["sid"].to_numpy()}
    first = {}
    for s in range(NS):
        a = np.full(n, -1, dtype=np.int64)
        m1 = (p_set == s) & (p_rank == 1)
        a[p_sid[m1]] = p_loc[m1]
        first[s] = a
    nI = np.bincount(p_sid[p_set == 2], minlength=n)
    out["nI"] = nI
    # lag bins for the lag-matched chance model (post hoc, Amendment 2): |t_B - t_item| in [0,15), [15,30), [30,60), 60+ s
    tmsg = content.get("t_msg")
    if tmsg is None:
        tmsg = chat()["t"].to_numpy()[np.asarray(content["msgs"], dtype=np.int64)]
    tb = S["t"].to_numpy()
    lag = np.abs((tb[p_sid] - tmsg[p_loc]).astype("timedelta64[ms]").astype(np.float64)) / 1000.0
    lbin = np.digitize(lag, LAG_EDGES)
    for j in range(len(LAG_EDGES) + 1):
        out[f"nR_b{j}"] = np.bincount(p_sid[(p_set == 0) & (lbin == j)], minlength=n)
        out[f"nI_b{j}"] = np.bincount(p_sid[(p_set == 2) & (lbin == j)], minlength=n)

    def pair_dots(X):
        d = np.empty(len(p_loc), dtype=np.float32)
        for a in range(0, len(p_loc), 50000):
            sl = slice(a, a + 50000)
            d[sl] = np.einsum("ij,ij->i", X[b_loc[p_sid[sl]]], X[p_loc[sl]])
        return d.astype(np.float64)

    loc2sid = {int(l): i for i, l in enumerate(b_loc)}
    c_sid = np.array([loc2sid.get(int(l), -1) for l in p_loc], dtype=np.int64)   # sid of the item if it is a statement

    def near_sets(mask_near):
        """sid -> set of read items (set 0) that are near-copies of the statement."""
        ns = {}
        idx = np.flatnonzero(mask_near & (p_set == 0))
        for i_ in idx:
            ns.setdefault(int(p_sid[i_]), set()).add(int(p_loc[i_]))
        return ns

    def nonsibling_mask(mask_pair_near, ns):
        """In-flight near pairs not explained by a shared near-copied read item (siblings excluded)."""
        idx = np.flatnonzero(mask_pair_near & (p_set == 2))
        keep = np.zeros(len(p_loc), bool)
        for i_ in idx:
            b_, c_ = int(p_sid[i_]), int(c_sid[i_])
            if c_ < 0 or not (ns.get(b_, set()) & ns.get(c_, set())):
                keep[i_] = True
        return keep

    def nonsibling_count(mask_pair_near, ns):
        return np.bincount(p_sid[nonsibling_mask(mask_pair_near, ns)], minlength=n)

    near_sets_m = {}
    for m in MODELS:
        dots = pair_dots(content["raw"][m])
        mx, _ = group_max(dots, gid, NS * n)
        near_sets_m[m] = (dots >= thr[m], near_sets(dots >= thr[m]))
        wd = pair_dots(content["white"][m])
        wmx, wam = group_max(wd, gid, NS * n)
        for s, suf in ((0, "R"), (1, "F")):
            v = mx[s::NS]
            out[f"maxcos_{m}_{suf}"] = v
            out[f"echo_{m}_{suf}"] = np.where(np.isnan(v), np.nan, (v >= thr[m]).astype(float))
            out[f"wmax_{m}_{suf}"] = wmx[s::NS]
        near = (dots >= thr[m]) & (p_set == 2)
        out[f"nnear_{m}_I"] = np.bincount(p_sid[near], minlength=n)
        out[f"nnear_{m}_Ins"] = nonsibling_count(dots >= thr[m], near_sets_m[m][1])
        nsb = nonsibling_mask(dots >= thr[m], near_sets_m[m][1])
        for j in range(len(LAG_EDGES) + 1):
            out[f"nnear_{m}_I_b{j}"] = np.bincount(p_sid[nsb & (lbin == j)], minlength=n)
            out[f"nnear_{m}_R_b{j}"] = np.bincount(p_sid[(dots >= thr[m]) & (p_set == 0) & (lbin == j)], minlength=n)
        for s, suf in ((3, "par"), (4, "addr")):
            out[f"cos_{m}_{suf}"] = mx[s::NS]
            out[f"near_{m}_{suf}"] = np.where(np.isnan(mx[s::NS]), np.nan, (mx[s::NS] >= thr[m]).astype(float))
        if kick is not None and len(kick.get(m, [])):
            out[f"kick_cos_{m}"] = (content["raw"][m][b_loc] @ kick[m].T).max(1)
        W = content["white"][m]
        srcmax = {s: np.where(wam[s::NS] >= 0, p_loc[np.clip(wam[s::NS], 0, None)], -1) for s in (0, 1)}
        for K in K_list:
            _, lab = spherical_kmeans(W.astype(np.float64), K, seed=seed + K)
            out[f"y_{m}_K{K}"] = lab[b_loc]
            for s in (0, 1, 2):
                out[f"x_{m}_K{K}_{SUF[s]}"] = np.where(first[s] >= 0, lab[np.clip(first[s], 0, None)], -1)
            for s in (0, 1):
                out[f"xmax_{m}_K{K}_{SUF[s]}"] = np.where(srcmax[s] >= 0, lab[np.clip(srcmax[s], 0, None)], -1)
            out[f"xpar_{m}_K{K}"] = np.where(first[3] >= 0, lab[np.clip(first[3], 0, None)], -1)
            out[f"xaddr_{m}_K{K}"] = np.where(first[4] >= 0, lab[np.clip(first[4], 0, None)], -1)
    for suf in ("R", "F"):
        out[f"echo_both_{suf}"] = np.where(np.isnan(out[f"echo_bge_{suf}"]), np.nan,
                                           out[f"echo_bge_{suf}"] * out[f"echo_gte_{suf}"])
    # in-flight near-copies under both models need pairwise agreement
    nb_all = near_sets_m["bge"][0] & near_sets_m["gte"][0]
    out["nnear_both_I"] = np.bincount(p_sid[nb_all & (p_set == 2)], minlength=n)
    ns_b = {k_: v_ | near_sets_m["gte"][1].get(k_, set()) for k_, v_ in near_sets_m["bge"][1].items()}
    for k_, v_ in near_sets_m["gte"][1].items():
        ns_b.setdefault(k_, v_)
    nsb_both = nonsibling_mask(nb_all, ns_b)
    for j in range(len(LAG_EDGES) + 1):
        out[f"nnear_both_I_b{j}"] = np.bincount(p_sid[nsb_both & (lbin == j)], minlength=n)
        out[f"nnear_both_R_b{j}"] = np.bincount(p_sid[nb_all & (p_set == 0) & (lbin == j)], minlength=n)
    ns_both = {k_: v_ | near_sets_m["gte"][1].get(k_, set()) for k_, v_ in near_sets_m["bge"][1].items()}
    for k_, v_ in near_sets_m["gte"][1].items():
        ns_both.setdefault(k_, v_)
    out["nnear_both_Ins"] = nonsibling_count(nb_all, ns_both)
    for suf in ("par", "addr"):
        out[f"near_both_{suf}"] = np.where(np.isnan(out[f"near_bge_{suf}"]), np.nan,
                                           out[f"near_bge_{suf}"] * out[f"near_gte_{suf}"])
    # --- markers
    mk = content["markers"]
    gmsg = pl.DataFrame({"loc": np.arange(len(content["msgs"]), dtype=np.int64),
                         "msg": np.asarray(content["msgs"], dtype=np.int64)})
    mkl = mk.with_columns(pl.col("msg").cast(pl.Int64)).join(gmsg, on="msg", how="inner").select("loc", "marker")
    base = pl.DataFrame({"sid": S["sid"].to_numpy().astype(np.int64)})
    pp = pl.DataFrame({"sid": p_sid, "set": p_set, "loc": p_loc})
    for filt in ("all", "rare"):
        mk_use = mkl if filt == "all" or not common else mkl.filter(~pl.col("marker").is_in(list(common)))
        nm = mk_use.group_by("loc").agg(pl.len().alias("nm"))
        bm = (pl.DataFrame({"sid": S["sid"].to_numpy().astype(np.int64), "loc": b_loc})
              .join(mk_use, on="loc", how="inner").select("sid", "marker"))
        nbm = base.join(bm.group_by("sid").agg(pl.len().alias("nb")), on="sid", how="left").with_columns(
            pl.col("nb").fill_null(0))
        nb_arr = nbm["nb"].to_numpy()
        pm = pp.join(mk_use, on="loc", how="inner")
        hit = (pm.select("sid", "set", "marker").unique().join(bm, on=["sid", "marker"], how="inner")
               .group_by("sid", "set").agg(pl.len().alias("hit")))
        ipair = (pm.join(bm, on=["sid", "marker"], how="inner").group_by("sid", "set", "loc").agg(pl.len().alias("ip"))
                 .join(nm, on="loc", how="left").join(nbm, on="sid", how="left")
                 .with_columns((pl.col("ip") / (pl.col("nm") + pl.col("nb") - pl.col("ip"))).alias("j")))
        jmax = ipair.group_by("sid", "set").agg(pl.col("j").max().alias("jmax"))
        jI = ipair.filter((pl.col("set") == 2) & (pl.col("j") >= 0.5)).group_by("sid").agg(pl.len().alias("nj"))
        # siblings for marker near-copies: in-flight pairs explained by a shared near-copied read item
        nearR = ipair.filter((pl.col("set") == 0) & (pl.col("j") >= 0.5)).select("sid", "loc")
        nsm = {}
        for a_, l_ in zip(nearR["sid"].to_list(), nearR["loc"].to_list()):
            nsm.setdefault(int(a_), set()).add(int(l_))
        pin = ipair.filter((pl.col("set") == 2) & (pl.col("j") >= 0.5)).select("sid", "loc")
        cnt_ns = np.zeros(n, dtype=np.int64)
        for a_, l_ in zip(pin["sid"].to_list(), pin["loc"].to_list()):
            c_ = loc2sid.get(int(l_), -1)
            if c_ < 0 or not (nsm.get(int(a_), set()) & nsm.get(c_, set())):
                cnt_ns[int(a_)] += 1
        out[f"mk_n_{filt}"] = nb_arr

        def per_sid(frame, col, s=None):
            f = frame if s is None else frame.filter(pl.col("set") == s)
            return base.join(f.select("sid", col), on="sid", how="left")[col]
        for s, suf in ((0, "R"), (1, "F")):
            h = per_sid(hit, "hit", s).fill_null(0).to_numpy().astype(float)
            jm = per_sid(jmax, "jmax", s).fill_null(0.0).to_numpy()
            out[f"mk_share_{filt}_{suf}"] = np.where(nb_arr >= 2, h / np.maximum(nb_arr, 1), np.nan)
            out[f"mk_near_{filt}_{suf}"] = np.where(nb_arr >= 3, (jm >= 0.5).astype(float), np.nan)
        out[f"nmknear_{filt}_I"] = np.where(nb_arr >= 3, per_sid(jI, "nj").fill_null(0).to_numpy(), 0)
        out[f"nmknear_{filt}_Ins"] = np.where(nb_arr >= 3, cnt_ns, 0)
        lag_of = {}
        for i_ in np.flatnonzero(p_set == 2):
            lag_of[(int(p_sid[i_]), int(p_loc[i_]))] = int(lbin[i_])
        cnt_b = np.zeros((len(LAG_EDGES) + 1, n), dtype=np.int64)
        for a_, l_ in zip(pin["sid"].to_list(), pin["loc"].to_list()):
            c_ = loc2sid.get(int(l_), -1)
            if c_ < 0 or not (nsm.get(int(a_), set()) & nsm.get(c_, set())):
                cnt_b[lag_of[(int(a_), int(l_))], int(a_)] += 1
        for j in range(len(LAG_EDGES) + 1):
            out[f"nmknear_{filt}_I_b{j}"] = np.where(nb_arr >= 3, cnt_b[j], 0)
        lagR = {}
        for i_ in np.flatnonzero(p_set == 0):
            lagR[(int(p_sid[i_]), int(p_loc[i_]))] = int(lbin[i_])
        rin = ipair.filter((pl.col("set") == 0) & (pl.col("j") >= 0.5)).select("sid", "loc")
        cnt_r = np.zeros((len(LAG_EDGES) + 1, n), dtype=np.int64)
        for a_, l_ in zip(rin["sid"].to_list(), rin["loc"].to_list()):
            cnt_r[lagR[(int(a_), int(l_))], int(a_)] += 1
        for j in range(len(LAG_EDGES) + 1):
            out[f"nmknear_{filt}_R_b{j}"] = np.where(nb_arr >= 3, cnt_r[j], 0)
        for s, suf in ((3, "par"), (4, "addr")):
            jp = per_sid(jmax, "jmax", s).fill_null(0.0).to_numpy()
            out[f"mkj_{filt}_{suf}"] = np.where((first[s] >= 0) & (nb_arr >= 3), jp, np.nan)
    return pl.DataFrame(out)


def common_markers(goal_no: int, S: pl.DataFrame, content: dict, allow_holdout: bool = False) -> set:
    """Markers used in >= COMMON_FRAC of the period's agent chat messages, or by >= 3 agents on the first day.
    With allow_holdout the frequencies come from the content's own marker frame (the confirmation unit)."""
    if allow_holdout:
        cc = chat()[np.asarray(content["msgs"], dtype=np.int64)]
        uses = content["markers"].with_columns(pl.col("msg").cast(pl.UInt32))
    else:
        cc = chat().filter((pl.col("goal_no") == goal_no) & ~pl.col("holdout"))
        uses = pl.scan_parquet(H34 / "uses.parquet").filter(pl.col("msg").is_in(cc["msg"].to_list())).select(
            "msg", "marker").collect().unique()
    nmsg = cc.height
    j = uses.join(cc.select("msg", "agent", "pt_date"), on="msg", how="left")
    freq = j.group_by("marker").agg(pl.len().alias("n"))
    common = set(freq.filter(pl.col("n") >= COMMON_FRAC * nmsg)["marker"].to_list())
    d1 = cc["pt_date"].min()
    a1 = j.filter(pl.col("pt_date") == d1).group_by("marker").agg(pl.col("agent").n_unique().alias("na"))
    common |= set(a1.filter(pl.col("na") >= COMMON_DAY1_AGENTS)["marker"].to_list())
    return common
