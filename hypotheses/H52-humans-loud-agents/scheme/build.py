"""H52 scheme: per-period (message, recipient) rows on the context ledger with salience covariates and four outcomes.

Outputs, per period, in data/processed/H52-humans-loud-agents/<period>/ (zstd parquet; numbers and codes only):
  rows.parquet      one row per (message m, recipient j) ledger item (agent / human / nudge; omitted items dropped);
                    agent rows subsampled to <= AGENT_CAP (seeded), human and bot rows always kept
  boundary.parquet  H29's boundary design on the ledger (talk call x message posted < 30 s before the talk)
  meta.json, _provenance.json
Text is read in memory only to find a nudge's leading @ (H35's rule); no text and no vectors are written.

Usage: uv run python hypotheses/H52-humans-loud-agents/scheme/build.py G04 G51 ... | --all
Confirmatory use: analysis/confirm.py calls build_period(..., allow_holdout=True, out=<confirm folder>).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import h52lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

SH = L.SH


def leading_targets(msg_ids: list[str], days: list[str]) -> dict:
    """message_id -> leading-@ roster agent code (H35's rule: text starts with '@', longest alias match at
    position 1 among agents on the roster that day). Text read in memory only."""
    import common
    if not msg_ids:
        return {}
    txt = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).filter(
        pl.col("message_id").is_in(msg_ids))
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date"]).filter(
        pl.col("message_id").is_in(msg_ids))
    txt = txt.join(cc, on="message_id", how="left")
    ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code"))
    agents = [{"id": int(a), "name": n} for a, n in ros.select("agent", "name").iter_rows()]
    pats = common.mention_regexes(agents)
    span = {int(a): (j, lv) for a, j, lv in ros.select("agent", "joined", "left").iter_rows()}
    out = {}
    for mid, text, d in txt.select("message_id", "text", "pt_date").iter_rows():
        best, blen = None, 0
        if text and text.startswith("@"):
            for a, pat in pats.items():
                j, lv = span[a]
                if not (j <= d and (lv is None or d < lv)):
                    continue
                m = pat.match(text, 1)
                if m and (m.end() - m.start()) > blen:
                    best, blen = a, m.end() - m.start()
        out[mid] = best
    return out


def activity_arrays(days: list[str]):
    """(pt_date, agent) -> int8 array of active minutes (states 3-4) indexed by minute since the day's win_start."""
    ab = pl.read_parquet(SH / "activity_bins_fixed.parquet", columns=["pt_date", "minute", "agent", "state"]).filter(
        pl.col("pt_date").is_in(days))
    out = {}
    for (d, a), g in ab.group_by(["pt_date", "agent"]):
        mm = g["minute"].to_numpy()
        arr = np.zeros(int(mm.max()) + 1, np.int8)
        arr[mm] = (g["state"].to_numpy() >= 3).astype(np.int8)
        out[(d, int(a))] = arr
    return out


def build_period(period: str, allow_holdout: bool = False, out: Path | None = None, date_from: str | None = None,
                 date_to: str | None = None, agent_cap: int = L.AGENT_CAP, seed: int = L.SEED, goal: int | None = None,
                 verbose: bool = True) -> dict:
    t0 = time.time()
    goal = goal if goal is not None else L.PERIODS[period]["goal"]
    days = L.period_days(goal, allow_holdout=allow_holdout, date_from=date_from, date_to=date_to)
    if not allow_holdout:
        L.assert_no_holdout(days, goal)
    out = out or (L.OUT / period)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    day_idx = {d: i for i, d in enumerate(days)}

    # --- receiving calls and ledger items
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days))
          .select("turn_id", "agent", "pt_date", "regime", "t_call", "t_log", "gap_kind", "talk").collect())
    regime = cw["regime"].cast(pl.Utf8).mode()[0]
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("pt_date").is_in(days))
          .select("turn_id", "k_new").collect())
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .filter(pl.col("turn_id").is_in(cw["turn_id"].implode()) & ~pl.col("omitted")
                  & pl.col("kind").cast(pl.Utf8).is_in(["agent", "human", "nudge"]))
          .collect())
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "room", "length", "agent"]).with_row_index("msg")
    rows = (it.join(cw, on="turn_id", how="inner").join(lt, on="turn_id", how="left")
            .join(cc.rename({"agent": "s_agent", "t": "t_m_dt"}), on="message_id", how="left")
            .rename({"agent": "recv"}))
    rows = rows.with_columns(pl.col("kind").cast(pl.Utf8).replace_strict(L.CLS).cast(pl.Int8).alias("cls"))
    # kickoffs
    kc = pl.read_parquet(SH / "kicks_classified.parquet", columns=["message_id", "kind", "subkind"]).filter(
        pl.col("kind").cast(pl.Utf8) == "human_message")
    kick_ids = kc.filter(pl.col("subkind").cast(pl.Utf8) == "kickoff")["message_id"]
    rows = rows.with_columns(pl.col("message_id").is_in(kick_ids.implode()).alias("kickoff"))
    # bot leading target
    nud_ids = rows.filter(pl.col("cls") == 2)["message_id"].unique().to_list()
    lead = leading_targets(nud_ids, days)
    rows = rows.with_columns(pl.col("message_id").replace_strict(lead, default=None, return_dtype=pl.Int16).alias("lead"))
    rows = rows.with_columns(
        pl.when(pl.col("cls") == 2).then(pl.col("lead").fill_null(-99) == pl.col("recv").cast(pl.Int16))
        .otherwise(pl.col("ment")).alias("named"))
    # room size = distinct ledger recipients of the message
    nrecv = rows.group_by("message_id").agg(pl.col("recv").n_unique().alias("n_recv"))
    rows = rows.join(nrecv, on="message_id", how="left")
    rows = rows.with_columns(
        (pl.col("t_m_dt").dt.epoch("us") / 1e6).alias("t_m"),
        (pl.col("t_call").dt.epoch("us") / 1e6).alias("tc"),
        pl.col("gap_kind").cast(pl.Utf8).is_in(list(L.IDLE_GAPS)).alias("idle"),
        pl.col("pt_date").replace_strict(day_idx, return_dtype=pl.Int16).alias("day_idx"),
        pl.col("s_agent").fill_null(-1).cast(pl.Int16).alias("sender0"),
        pl.col("length").alias("len"))
    rows = rows.with_columns(pl.when(pl.col("cls") == 0).then(pl.col("sender0"))
                             .when(pl.col("cls") == 1).then(pl.lit(-1, pl.Int16)).otherwise(pl.lit(-2, pl.Int16)).alias("sender"))
    n_all = rows.group_by("cls").len().sort("cls").to_dicts()
    # subsample agent rows (seeded)
    ag = rows.filter(pl.col("cls") == 0)
    if ag.height > agent_cap:
        keep = np.zeros(ag.height, bool)
        keep[rng.choice(ag.height, agent_cap, replace=False)] = True
        ag = ag.filter(pl.Series(keep))
    rows = pl.concat([ag, rows.filter(pl.col("cls") != 0)]).sort("tc", "recv")
    rows = rows.with_row_index("item")
    n = rows.height

    # --- activity covariates and outcome
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days)).select("pt_date", "win_start")
    ws = {d: w.timestamp() for d, w in cal.iter_rows()}
    act = activity_arrays(days)
    y30 = np.full(n, np.nan, np.float32); y30_ok = np.zeros(n, bool)
    pre15 = np.full(n, 0, np.int16); since = np.full(n, -1, np.int16)
    for i, (d, a, tc) in enumerate(rows.select("pt_date", "recv", "tc").iter_rows()):
        arr = act.get((d, int(a)))
        if arr is None:
            continue
        mc = int((tc - ws[d]) // 60)
        if mc < 0 or mc >= len(arr):
            continue
        lo = max(0, mc - 15)
        pre15[i] = int(arr[lo:mc].sum())
        prev = np.flatnonzero(arr[:mc])
        since[i] = min(120, mc - 1 - prev[-1]) if len(prev) else -1
        if mc + 30 < len(arr):
            y30[i] = float(arr[mc + 1: mc + 31].sum()); y30_ok[i] = True

    # --- content: statements, message vectors, placebos
    st, V = L.statement_table(days, "bge_small", "white32")
    st_agent = st["agent"].to_numpy(); st_ts = st["ts"].to_numpy()
    recv = rows["recv"].to_numpy().astype(int); tcall = rows["tc"].to_numpy()
    bidx, pmask, qidx = L.window_indices(st_agent, st_ts, recv, tcall)
    # pools: messages of the period's days by class (other-day placebos), from chat_core + ledger kinds
    pool_df = (rows.select("msg", "cls", "day_idx", "kickoff", "lead").unique("msg"))
    pool = {}
    for c in (0, 1, 2):
        p = pool_df.filter((pl.col("cls") == c) & ~pl.col("kickoff"))
        pool[c] = (p["msg"].to_numpy().astype(np.int64), p["day_idx"].to_numpy())
    btp = {}
    pb = pool_df.filter(pl.col("cls") == 2)
    for a in pb["lead"].drop_nulls().unique().to_list():
        q = pb.filter(pl.col("lead") == a)
        btp[int(a)] = (q["msg"].to_numpy().astype(np.int64), q["day_idx"].to_numpy())
    pl_idx = L.draw_placebos(rows["cls"].to_numpy(), rows["day_idx"].to_numpy(), recv, pool, rng, bot_target_pool=btp)
    # reply eligibility: the recipient's own chat messages in [t_call, t_call + 60 min)
    chat_mask = (st["kind"] == "chat").to_numpy()
    n_chat_post = np.zeros(n, np.int16)
    ca, ct = st_agent[chat_mask], st_ts[chat_mask]
    o = np.lexsort((ct, ca)); ca, ct = ca[o], ct[o]
    for a in np.unique(recv):
        lo, hi = np.searchsorted(ca, a, "left"), np.searchsorted(ca, a, "right")
        rr = np.flatnonzero(recv == a)
        T = ct[lo:hi]
        n_chat_post[rr] = (np.searchsorted(T, tcall[rr] + L.POST_WIN, "left") - np.searchsorted(T, tcall[rr], "left")).astype(np.int16)
    msg_rows = rows["msg"].to_numpy().astype(np.int64)
    uniq = np.unique(np.concatenate([msg_rows, pl_idx[pl_idx >= 0]]))
    res = {}
    for model, variant, tag in (("bge_small", "white32", ""), ("gte_modernbert", "white32", "_gte"),
                                ("bge_small", "style_resid_period32", "_sr")):
        Mv = L.message_vectors(uniq, regime, model)
        pos = {int(m): k for k, m in enumerate(uniq)}
        U = Mv[np.array([pos[int(m)] for m in msg_rows])]
        Up = np.full(pl_idx.shape + (32,), np.nan, np.float32)
        okp = pl_idx >= 0
        Up[okp] = Mv[np.array([pos[int(m)] for m in pl_idx[okp]])]
        if tag == "":
            Vs = V
        else:
            _, Vs = L.statement_table(days, model, variant)
        r = L.content_rows(Vs, bidx, pmask, qidx, U, Up,
                           call_id=rows["turn_id"].to_numpy().astype(np.int64) if tag == "" else None)
        for k_, v in r.items():
            if tag and k_ in ("n_pre", "n_post"):
                continue
            res[k_ + tag] = v
        if tag == "":
            U_bge = U

    # --- replies and stance (DQ2, pair_set = cand, labelled)
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet")
          .filter(pl.col("pt_date").is_in(days) & (pl.col("pair_set").cast(pl.Utf8) == "cand") & pl.col("labelled"))
          .select("A_message_id", "b_agent", "p_reply", "parent", "p_supports", "p_opposes", "p_asks").collect())
    rsoft = rp.group_by("A_message_id", "b_agent").agg(pl.col("p_reply").max().alias("rep_soft"),
                                                      pl.col("parent").any().alias("rep"))
    par = (rp.filter(pl.col("parent")).sort("p_reply", descending=True)
           .group_by("A_message_id", "b_agent").first()
           .select("A_message_id", "b_agent", (pl.col("p_supports") - pl.col("p_opposes")).alias("st"),
                   pl.col("p_opposes").alias("st_opp"), pl.col("p_asks").alias("st_ask")))
    rows = (rows.join(rsoft.rename({"A_message_id": "message_id", "b_agent": "recv"}), on=["message_id", "recv"], how="left")
            .join(par.rename({"A_message_id": "message_id", "b_agent": "recv"}), on=["message_id", "recv"], how="left"))
    rows = rows.with_columns(pl.col("rep_soft").is_not_null().alias("rep_lab"),
                             pl.col("rep_soft").fill_null(0.0), pl.col("rep").fill_null(False))
    # reply bias diagnostic: m (non-agent) is the top candidate without the +0.20 b_names_a term but not with it
    cand = (pl.scan_parquet(SH / "reply_threading/candidates_ledger.parquet")
            .filter(pl.col("set").cast(pl.Utf8) == "cand").select("b", "a", "score", "b_names_a", "a_kind").collect())
    bmeta = pl.read_parquet(SH / "reply_threading/b_meta_ledger.parquet", columns=["b", "b_agent", "pt_date"]).filter(
        pl.col("pt_date").is_in(days))
    cand = cand.join(bmeta.select("b", "b_agent"), on="b", how="inner")
    cand = cand.with_columns((pl.col("score") - 0.20 * pl.col("b_names_a").cast(pl.Float32)).alias("score_nf"))
    top = cand.sort("score", descending=True).group_by("b").first().select("b", pl.col("a").alias("a_top"))
    topnf = cand.sort("score_nf", descending=True).group_by("b").first().select("b", "b_agent", pl.col("a").alias("a_nf"),
                                                                                pl.col("a_kind").alias("k_nf"))
    risk = (topnf.join(top, on="b").filter((pl.col("a_nf") != pl.col("a_top")) & (pl.col("k_nf") != 0))
            .group_by("a_nf", "b_agent").len().rename({"a_nf": "msg", "b_agent": "recv", "len": "rep_nf_risk"}))
    rows = rows.join(risk.with_columns(pl.col("msg").cast(pl.UInt32)), on=["msg", "recv"], how="left").with_columns(
        pl.col("rep_nf_risk").fill_null(0).cast(pl.Int16))
    rows = rows.sort("item")

    # --- assemble
    out_df = rows.select(
        "item", "message_id", pl.col("msg").cast(pl.UInt32), "turn_id", pl.col("recv").cast(pl.Int8), "sender", "cls",
        "kickoff", "day_idx", "pt_date", "t_m", "tc", pl.col("age_s").cast(pl.Float32), "uncertain", "during_prev",
        "named", pl.col("len").cast(pl.Int32), "idle", pl.col("n_recv").cast(pl.Int16),
        pl.col("k_new").fill_null(1).cast(pl.Int16), "room",
        "rep", pl.col("rep_soft").cast(pl.Float32), "rep_lab", "rep_nf_risk",
        pl.col("st").cast(pl.Float32), pl.col("st_opp").cast(pl.Float32), pl.col("st_ask").cast(pl.Float32))
    out_df = out_df.with_columns(pl.Series("y30", y30).fill_nan(None), pl.Series("y30_ok", y30_ok),
                                 pl.Series("pre15", pre15), pl.Series("since_act", since), pl.Series("n_chat_post", n_chat_post),
                                 *[(pl.Series(k_, v.astype(np.float32)).fill_nan(None) if v.dtype.kind == "f"
                                    else pl.Series(k_, v)) for k_, v in res.items()])
    out_df.write_parquet(out / "rows.parquet", compression="zstd")

    # --- boundary design (H29) on the ledger
    bnd = boundary_rows(days, cw, it, cc, st, V, regime, lead, rng, day_idx)
    bnd.write_parquet(out / "boundary.parquet", compression="zstd")

    meta = dict(period=period, goal=goal, days=days, regime=regime, n_rows=out_df.height, n_all_by_cls=n_all,
                agent_cap=agent_cap, n_boundary=bnd.height, seconds=round(time.time() - t0, 1))
    L.jdump(meta, out / "meta.json")
    L.write_provenance(out, "hypotheses/H52-humans-loud-agents/scheme/build.py",
                       ["call_windows", "context_ledger_items", "context_ledger_turns", "chat_core", "chat_text (leading @ only, in memory)",
                        "kicks_classified", "activity_bins_fixed", "calendar", "embeddings/statements",
                        "embeddings/statements_{white32,style_resid_period32}_{bge_small,gte_modernbert}",
                        "embeddings/chat_{bge_small,gte_modernbert}", "embeddings/whitening*", "reply_pairs",
                        "reply_threading/candidates_ledger", "reply_threading/b_meta_ledger", "roster"],
                       dict(period=period, goal=goal, date_from=date_from, date_to=date_to, allow_holdout=allow_holdout,
                            agent_cap=agent_cap, seed=seed, n_placebo=L.N_PL, windows_s=[L.PRE_WIN, L.POST_WIN, L.BASIS_WIN]))
    if verbose:
        print(f"[{period}] rows {out_df.height} (all by cls {n_all}), boundary {bnd.height}, {meta['seconds']} s", flush=True)
    return meta


def boundary_rows(days, cw, it, cc, st, V, regime, lead, rng, day_idx) -> pl.DataFrame:
    """H29's boundary rows on the ledger. For each agent chat message B (talk statement) of recipient j produced by
    call c: visible rows = items new at c posted < 30 s before B; invisible rows = items of j's next receiving call
    that were posted in [t_call(c), t_B) (during c). x_prev = j's previous chat statement that day. Cross-day placebo
    partner: same sender for agents, same class (other day) for humans and bots. Returns per-row pull sums."""
    chat_st = st.filter(pl.col("kind") == "chat")
    ci = pl.read_parquet(L.ED / "chat_index.parquet").with_row_index("src_row").with_columns(pl.col("src_row").cast(pl.UInt32))
    chat_st = chat_st.join(ci, on="src_row", how="left")
    srow_pos = {int(s): k for k, s in enumerate(st["srow"].to_list())}
    chat_st = chat_st.with_columns(pl.col("srow").replace_strict(srow_pos, return_dtype=pl.Int64).alias("vpos")).sort("agent", "ts")
    # producing call of each talk statement: the agent's last call with t_call <= t_B
    calls = cw.select("turn_id", "agent", pl.col("t_call").dt.epoch("us").alias("tcu"), pl.col("t_log").dt.epoch("us").alias("tlu")).sort("agent", "tcu")
    B = chat_st.select("agent", "ts", "vpos", "message_id", "pt_date").with_columns((pl.col("ts") * 1e6).cast(pl.Int64).alias("tbu")).sort("agent", "tbu")
    B = B.sort("tbu").join_asof(calls.sort("tcu"), left_on="tbu", right_on="tcu", by="agent", strategy="backward")
    B = B.sort("agent", "tbu")
    B = B.with_columns(pl.col("vpos").shift(1).over("agent", "pt_date").alias("vprev")).filter(
        pl.col("vprev").is_not_null() & pl.col("turn_id").is_not_null())
    # next receiving call of the same agent (holds messages that arrived during c)
    nxt = calls.with_columns(pl.col("turn_id").shift(-1).over("agent").alias("next_turn")).select("turn_id", "next_turn")
    B = B.join(nxt, on="turn_id", how="left")
    itm = it.select("turn_id", "message_id", "kind", "ment", "sender").join(
        cc.select("message_id", "msg", (pl.col("t").dt.epoch("us")).alias("tmu")), on="message_id", how="left")
    vis = B.join(itm, on="turn_id", how="inner").with_columns(pl.lit(True).alias("vis"))
    inv = B.join(itm.rename({"turn_id": "next_turn"}), on="next_turn", how="inner").filter(
        (pl.col("tmu") >= pl.col("tcu")) & (pl.col("tmu") < pl.col("tbu"))).with_columns(pl.lit(False).alias("vis"))
    R = pl.concat([vis, inv.select(vis.columns)])
    R = R.with_columns(((pl.col("tbu") - pl.col("tmu")) / 1e6).alias("dt_talk"),
                       ((pl.col("tbu") - pl.col("tcu")) / 1e6).alias("c")).filter(
        (pl.col("dt_talk") >= 0) & (pl.col("dt_talk") < 30))
    if R.height == 0:
        return pl.DataFrame()
    R = R.with_columns(pl.col("kind").cast(pl.Utf8).replace_strict(L.CLS).cast(pl.Int8).alias("kcls"),
                       pl.col("pt_date").replace_strict(day_idx, return_dtype=pl.Int16).alias("day_idx"))
    R = R.with_columns(pl.when(pl.col("kcls") == 2)
                       .then(pl.col("message_id").replace_strict(lead, default=None, return_dtype=pl.Int16) == pl.col("agent").cast(pl.Int16))
                       .otherwise(pl.col("ment")).fill_null(False).alias("named"))
    # vectors
    msgs = R["msg"].to_numpy().astype(np.int64)
    # cross-day placebo partner
    allm = itm.select("msg", "kind", "sender").unique("msg").join(
        cc.select("msg", (pl.col("t").dt.epoch("us")).alias("tmu")), on="msg", how="left")
    cal_day = {}
    dser = pl.read_parquet(L.SH / "chat_core.parquet", columns=["pt_date"]).with_row_index("msg")
    allm = allm.join(dser, on="msg", how="left").filter(pl.col("pt_date").is_in(days))
    allm = allm.with_columns(pl.col("pt_date").replace_strict(day_idx, return_dtype=pl.Int16).alias("d"),
                             pl.col("kind").cast(pl.Utf8).replace_strict(L.CLS).cast(pl.Int8).alias("kcls"))
    grp = {}
    for (kc, sd), g in allm.group_by(["kcls", "sender"]):
        key = (int(kc), int(sd) if (kc == 0 and sd is not None) else -1)
        grp[key] = (g["msg"].to_numpy().astype(np.int64), g["d"].to_numpy())
    part = np.full(len(msgs), -1, np.int64)
    kcls = R["kcls"].to_numpy(); snd = R["sender"].to_numpy(); dd = R["day_idx"].to_numpy()
    for i in range(len(msgs)):
        key = (int(kcls[i]), int(snd[i]) if (kcls[i] == 0 and snd[i] is not None and not np.isnan(snd[i])) else -1)
        g = grp.get(key)
        if g is None:
            continue
        cand = g[0][g[1] != dd[i]]
        if len(cand):
            part[i] = cand[rng.integers(len(cand))]
    uniq = np.unique(np.concatenate([msgs, part[part >= 0]]))
    Mv = L.message_vectors(uniq, regime, "bge_small")
    pos = {int(m): k for k, m in enumerate(uniq)}
    xm = Mv[[pos[int(m)] for m in msgs]]
    xp = np.full_like(xm, np.nan)
    okp = part >= 0
    xp[okp] = Mv[[pos[int(m)] for m in part[okp]]]
    xn = V[R["vpos"].to_numpy().astype(int)]
    xo = V[R["vprev"].to_numpy().astype(int)]
    y = xn - xo; u = xm - xo; up = xp - xo
    out = R.select(pl.col("agent").alias("recv"), "day_idx", "msg", pl.col("kcls").alias("kind"), "named", "vis",
                   "dt_talk", "c", "turn_id").with_columns(
        pl.Series("yu", (y * u).sum(1)), pl.Series("uu", (u * u).sum(1)),
        pl.Series("yu_x", (y * up).sum(1)), pl.Series("uu_x", (up * up).sum(1)))
    return out.filter(pl.col("yu").is_not_nan() & pl.col("uu").is_not_nan())


if __name__ == "__main__":
    args = sys.argv[1:]
    todo = (L.REPLICATION + L.EXTRA) if "--all" in args else [a for a in args if not a.startswith("--")]
    for p in todo:
        build_period(p)
