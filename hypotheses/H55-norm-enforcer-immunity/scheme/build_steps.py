"""H55 scheme steps: loop episodes, v3 blocked episodes, and directed reads (context ledger). Codes only.

Called from build.py (`loops`, `blocked`, `reads`).
"""
from __future__ import annotations

import numpy as np
import polars as pl

import h55common as H

BUILT_BY = "hypotheses/H55-norm-enforcer-immunity/scheme/build_steps.py"
AGE_MIN = 2           # loop / blocked episode: run of >= 2 flagged statements / windows
GAP_SKIP = 2          # v3: up to 2 unlabelled 5-min windows skipped inside a blocked run


# ------------------------------------------------------------------------------------------------------------ loops
def _runs(flags: np.ndarray, groups: np.ndarray):
    """Run age (consecutive True count) within groups; 0 where False."""
    age = np.zeros(len(flags), np.int32)
    for i in range(len(flags)):
        if flags[i]:
            age[i] = (age[i - 1] + 1) if (i > 0 and groups[i] == groups[i - 1]) else 1
    return age


def loop_steps(m: pl.DataFrame, version: str) -> pl.DataFrame:
    col = {"restate": "restate", "copy": "copy"}[version]
    s = (m.filter((pl.col("speaker_kind") == "agent") & pl.col("srow").is_not_null())
         .select("message_id", "t", "pt_date", "goal_no", "unit_id", "regime", "room", "agent", "length", pl.col(col).alias("f"))
         .sort("agent", "pt_date", "t"))
    g = (s["agent"].cast(pl.Int32) * 100000 + s["pt_date"].str.replace_all("-", "").cast(pl.Int32) % 100000).to_numpy()
    f = s["f"].to_numpy()
    age = _runs(f, g)
    same_next = np.r_[g[1:] == g[:-1], False]
    nxt_f = np.r_[f[1:], False]
    t = s["t"].to_numpy()
    t_next = np.r_[t[1:], np.datetime64("NaT")]
    same_prev = np.r_[False, g[1:] == g[:-1]]
    t_prev = np.r_[np.datetime64("NaT"), t[:-1]]
    # episode id: index of the run's first statement
    ep = np.full(len(f), -1, np.int64)
    for i in range(len(f)):
        if age[i] == 1:
            ep[i] = i
        elif age[i] > 1:
            ep[i] = ep[i - 1]
    s = s.with_columns(pl.Series("k", age), pl.Series("episode", ep), pl.Series("has_next", same_next),
                       pl.Series("next_flag", nxt_f & same_next),
                       pl.Series("t_next", np.where(same_next, t_next, np.datetime64("NaT"))).cast(pl.Datetime("us", "UTC")),
                       pl.Series("t_prev", np.where(same_prev, t_prev, np.datetime64("NaT"))).cast(pl.Datetime("us", "UTC")))
    s = s.with_columns(pl.lit(version).alias("version"),
                       pl.when(pl.col("has_next")).then((~pl.col("next_flag")).cast(pl.Int8)).otherwise(None).alias("y"))
    return s


def loops(od, allow_holdout=False):
    m = pl.read_parquet(od / "messages.parquet")
    out_steps, out_eps, anchors = [], [], None
    for v in ("restate", "copy"):
        s = loop_steps(m, v)
        if anchors is None:
            anchors = s.select("message_id", "agent", "pt_date", "t", "t_next")
        st = s.filter(pl.col("k") >= AGE_MIN)
        out_steps.append(st.drop("f", "next_flag"))
        eps = (s.filter(pl.col("k") >= 1).group_by("episode").agg(
            pl.col("version").first(), pl.col("agent").first(), pl.col("pt_date").first(), pl.col("goal_no").first(),
            pl.col("unit_id").first(), pl.col("regime").first(), pl.col("t").min().alias("t_start"),
            pl.col("k").max().alias("length"), pl.col("t_next").last().alias("t_exit"), pl.col("has_next").last().alias("escaped"))
            .filter(pl.col("length") >= AGE_MIN))
        out_eps.append(eps)
    pl.concat(out_steps).write_parquet(od / "loop_steps.parquet", compression="zstd")
    pl.concat(out_eps).write_parquet(od / "loops.parquet", compression="zstd")
    anchors.write_parquet(od / "stmt_anchors.parquet", compression="zstd")
    H.write_prov("loops", BUILT_BY, ["H55 messages (statement_flags)"],
                 {"age_min": AGE_MIN, "restate": "self_repeat_bge | self_repeat_gte", "copy": "self_repeat_both",
                  "outcome": "next statement same PT day unflagged"})
    for v, st in zip(("restate", "copy"), out_steps):
        print(v, st.height, "at-risk steps;", st.filter(pl.col("y").is_not_null()).height, "with outcome; escape rate",
              round(float(st["y"].mean()), 3))


# ---------------------------------------------------------------------------------------------------------- blocked
def blocked(od, allow_holdout=False):
    b = (pl.scan_parquet(H.SH / "behavior_states_v3.parquet")
         .select("pt_date", "agent", "w", "t0", "t1", "goal_no", "regime", "holdout", "labeled", "p_blocked", "behavior")
         .collect())
    if not allow_holdout:
        b = b.filter(~pl.col("holdout"))
        assert not any(H.holdout_flags(b["pt_date"], b["goal_no"]))
    b = b.filter(pl.col("labeled")).sort("agent", "pt_date", "w")
    g = (b["agent"].cast(pl.Int64) * 10**8 + b["pt_date"].str.replace_all("-", "").cast(pl.Int64)).to_numpy()
    w = b["w"].to_numpy()
    blk = (b["p_blocked"].fill_null(0).to_numpy() >= 0.5)
    n = len(w)
    age = np.zeros(n, np.int32)
    ep = np.full(n, -1, np.int64)
    for i in range(n):
        if blk[i]:
            cont = i > 0 and g[i] == g[i - 1] and blk[i - 1] and (w[i] - w[i - 1]) <= GAP_SKIP + 1
            age[i] = age[i - 1] + 1 if cont else 1
            ep[i] = ep[i - 1] if cont else i
    nxt_same = np.r_[(g[1:] == g[:-1]) & ((w[1:] - w[:-1]) <= GAP_SKIP + 1), False]
    nxt_blk = np.r_[blk[1:], False]
    t1 = b["t1"].to_numpy()
    t0n = np.r_[b["t0"].to_numpy()[1:], np.datetime64("NaT")]
    b = b.with_columns(pl.Series("k", age), pl.Series("episode", ep), pl.Series("has_next", nxt_same),
                       pl.Series("y", np.where(nxt_same, (~nxt_blk).astype(float), np.nan)),
                       pl.Series("t_next0", np.where(nxt_same, t0n, np.datetime64("NaT"))).cast(pl.Datetime("us", "UTC")))
    b = b.with_columns(pl.when(pl.col("y").is_nan()).then(None).otherwise(pl.col("y")).cast(pl.Int8).alias("y"))
    from build import assign_unit
    b = assign_unit(b.rename({"t0": "t"})).rename({"t": "t0"})
    steps = b.filter(pl.col("k") >= AGE_MIN)
    steps.write_parquet(od / "blocked_steps.parquet", compression="zstd")
    eps = (b.filter(pl.col("k") >= 1).group_by("episode").agg(
        pl.col("agent").first(), pl.col("pt_date").first(), pl.col("goal_no").first(), pl.col("unit_id").first(),
        pl.col("regime").first(), pl.col("t0").min().alias("t_start"), pl.col("k").max().alias("length"),
        pl.col("has_next").last().alias("escaped")).filter(pl.col("length") >= AGE_MIN))
    eps.write_parquet(od / "blocked_episodes.parquet", compression="zstd")
    H.write_prov("blocked", BUILT_BY, ["behavior_states_v3"], {"p_blocked_thr": 0.5, "age_min": AGE_MIN, "gap_skip_windows": GAP_SKIP})
    print("blocked steps", steps.height, "with outcome", steps.filter(pl.col("y").is_not_null()).height,
          "escape", round(float(steps["y"].mean()), 3), "episodes", eps.height)


# ------------------------------------------------------------------------------------------------------------ reads
def _calls(allow_holdout):
    tu = (pl.scan_parquet(H.SH / "context_ledger_turns.parquet")
          .select("turn_id", "agent", "pt_date", "goal_no", "holdout", "t_call", "k_new", "talk").collect())
    if not allow_holdout:
        tu = tu.filter(~pl.col("holdout"))
    return tu


def _items(turns: pl.DataFrame, msg: pl.DataFrame) -> pl.DataFrame:
    it = (pl.scan_parquet(H.SH / "context_ledger_items.parquet")
          .select("turn_id", "message_id", "sender", pl.col("kind").cast(pl.Utf8).alias("ikind"), "ment", "age_s")
          .join(turns.lazy().select("turn_id", "agent", "t_call"), on="turn_id").collect())
    mm = msg.select("message_id", pl.col("agent").alias("snd"), "speaker_kind", "length", "parent_agent", "parent_kind",
                    "corr_jev", "corr_lex", "lex_decl", "p_reply", "p_opposes", "p_opp_correction", "p_opp_decline",
                    "regime")
    it = it.join(mm, on="message_id", how="left")
    it = it.with_columns(
        ((pl.col("parent_agent") == pl.col("agent")) & (pl.col("parent_kind") == 0)).fill_null(False).alias("reply_to_me"),
    ).with_columns(
        ((pl.col("ment") | pl.col("reply_to_me")) & pl.col("ikind").is_in(["agent", "human"])).alias("directed"),
        (pl.col("p_reply").fill_null(0) * pl.col("p_opposes").fill_null(0)
         * (pl.col("p_opp_correction").fill_null(0) + pl.col("p_opp_decline").fill_null(0))).alias("q_soft"),
    )
    return it


def _novelty(dr: pl.DataFrame, anchor_col: str) -> pl.DataFrame:
    """cosine distance (white32 bge, per regime) between a directed message and the recipient's anchor statement."""
    import common as C
    ci = pl.read_parquet(H.SH / "embeddings/chat_index.parquet").with_row_index("row")
    E = np.load(H.SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    d = dr.join(ci.rename({"message_id": "mid", "row": "r_m"}), left_on="message_id", right_on="mid", how="left")
    d = d.join(ci.rename({"message_id": "aid", "row": "r_a"}), left_on=anchor_col, right_on="aid", how="left")
    nov = np.full(d.height, np.nan, np.float32)
    for reg in ("I", "II", "III"):
        ix = np.flatnonzero((d["regime"].cast(pl.Utf8).fill_null("") == reg).to_numpy() & d["r_m"].is_not_null().to_numpy() & d["r_a"].is_not_null().to_numpy())
        if not len(ix):
            continue
        W = C.load_whitener(reg, 32)
        A = W(E[d["r_m"].to_numpy()[ix].astype(int)])
        B = W(E[d["r_a"].to_numpy()[ix].astype(int)])
        A /= np.linalg.norm(A, axis=1, keepdims=True) + 1e-9
        B /= np.linalg.norm(B, axis=1, keepdims=True) + 1e-9
        nov[ix] = 1 - (A * B).sum(1)
    return d.with_columns(pl.Series("novelty", nov)).drop("r_m", "r_a")


def reads(od, allow_holdout=False):
    msg = pl.read_parquet(od / "messages.parquet")
    turns = _calls(allow_holdout)
    it = _items(turns, msg)
    print("ledger items (non-holdout recipients):", it.height, "directed:", int(it["directed"].sum()))
    # ---- loops: assign each call to the recipient's latest statement before t_call (any statement), same day
    anc = pl.read_parquet(od / "stmt_anchors.parquet").sort("t")
    calls = turns.select("turn_id", "agent", "t_call", "k_new").sort("t_call")
    ca = calls.join_asof(anc.select("agent", pl.col("t").alias("t_anchor"), pl.col("message_id").alias("anchor_id"), "t_next", "pt_date"),
                         left_on="t_call", right_on="t_anchor", by="agent", strategy="backward")
    ca = ca.filter(pl.col("anchor_id").is_not_null() & (pl.col("t_next").is_null() | (pl.col("t_call") < pl.col("t_next"))))
    # call volume per anchor window (all items read)
    vol = ca.group_by("anchor_id").agg(pl.col("k_new").sum().alias("items_read"), pl.len().alias("n_calls"))
    dr = it.filter(pl.col("directed")).join(ca.select("turn_id", "anchor_id"), on="turn_id")
    dr = _novelty(dr, "anchor_id")
    dr.select("anchor_id", "turn_id", "t_call", "message_id", "agent", "snd", "ikind", "ment", "reply_to_me", "length",
              "corr_jev", "corr_lex", "lex_decl", "q_soft", "age_s", "novelty").write_parquet(od / "reads_loop.parquet", compression="zstd")
    vol.write_parquet(od / "reads_loop_volume.parquet", compression="zstd")
    # ---- blocked windows: calls with t_call in [t0, t1) of the agent's labelled window
    bs = pl.read_parquet(od / "blocked_steps.parquet").select("agent", "t0", "t1", "episode", "k", "w", "pt_date")
    bw = bs.with_columns((pl.col("t0").cast(pl.Int64).cast(pl.Utf8) + "_" + pl.col("agent").cast(pl.Utf8)).alias("win_id")).sort("t0")
    cb = calls.join_asof(bw.select("agent", "t0", "t1", "win_id"), left_on="t_call", right_on="t0", by="agent", strategy="backward")
    cb = cb.filter(pl.col("win_id").is_not_null() & (pl.col("t_call") < pl.col("t1")))
    volb = cb.group_by("win_id").agg(pl.col("k_new").sum().alias("items_read"), pl.len().alias("n_calls"))
    drb = it.filter(pl.col("directed")).join(cb.select("turn_id", "win_id"), on="turn_id")
    drb.select("win_id", "turn_id", "t_call", "message_id", "agent", "snd", "ikind", "ment", "reply_to_me", "length",
               "corr_jev", "corr_lex", "lex_decl", "q_soft", "age_s").write_parquet(od / "reads_blocked.parquet", compression="zstd")
    volb.write_parquet(od / "reads_blocked_volume.parquet", compression="zstd")
    # ---- per-period directed-read totals (swarm level, all calls)
    H.write_prov("reads", BUILT_BY, ["context_ledger_turns", "context_ledger_items", "H55 messages", "embeddings/chat_bge_small",
                                     "whitening_<regime>"],
                 {"directed": "ledger item names recipient (ment) or its DQ2 parent is the recipient's message; agent/human senders",
                  "loop_window": "calls with t_call in (t(s_k), t(s_{k+1})) via as-of join to the recipient's latest statement",
                  "blocked_window": "calls with t_call in [t0, t1) of the labelled 5-min window",
                  "novelty": "1 - cos(white32 bge) between directed message and the recipient's anchor statement"})
    print("loop-window directed reads:", dr.height, "jev corrections:", int(dr["corr_jev"].sum()),
          "| blocked-window directed reads:", drb.height, "jev corrections:", int(drb["corr_jev"].sum()))
