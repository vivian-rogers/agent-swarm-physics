"""H44 scheme: regime-III non-holdout calls with categories, outputs and segments; events; v3 windows; reply pools;
content-pull pairs. Builds data/processed/H44-erasure-reacquisition-thrash/.

  calls.parquet       one row per non-summary model call (regime III, non-holdout): category, write evidence, real
                      failures, agent work commits, new items, ctx_pos, segment (reset that opened it), loop flag,
                      integer command hash (no text)
  events.parquet      anchors: forced / voluntary resets and pseudo-erasures (ctx_pos 31: window -20..+10; ctx_pos 21:
                      window -10..+20), with window bounds, memory dose and time of day
  v3_windows.parquet  Jev v3 windows with time since the last reset and its kind
  reply_pools.parquet one row per agent talk message B: segment position, visible-pool counts by read class x age bin
                      and its DQ2 parent's class x age bin
  pull_pairs.parquet  consecutive chat statements of one agent-day straddling 0 or 1 consolidation reset: content-pull
                      numerators / denominators by read class x age bin (bge white32; gte white32 as robustness)

Usage: uv run python hypotheses/H44-erasure-reacquisition-thrash/scheme/build.py [--only calls,events,v3,replies,pull]
Command text from turn_outcomes is classified and hashed in memory and never written.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h44common as C  # noqa: E402

AGE_EDGES = np.array([0, 60, 180, 600, 1800, 3600.0001])  # s: <=1, 1-3, 3-10, 10-30, 30-60 min
N_AGE = len(AGE_EDGES) - 1
RCLS = ["post", "pre_ctx", "pre_erased"]


def load_calls_raw(days: pl.DataFrame | None = None, umap: pl.DataFrame | None = None) -> pl.DataFrame:
    """Regime-III calls on `days` (default: non-holdout days). Confirmatory callers pass held-out days explicitly."""
    held = days is not None
    days = C.nonholdout_days() if days is None else days
    t = (pl.read_parquet(C.SH / "context_ledger_turns.parquet",
                         columns=["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_call", "t_first",
                                  "t_log", "kind", "talk", "ctx_mode", "room", "n_agent", "n_human", "n_nudge", "n_ment",
                                  "k_new", "chars_new", "ctx_pos", "reset_consol", "reset_forced", "reset_session",
                                  "first_of_day", "prev_seg_len"])
         .filter((pl.col("regime") == "III") & (pl.lit(held) | ~pl.col("holdout")) & (pl.col("ctx_mode") == "cu")
                 & pl.col("pt_date").is_in(days["pt_date"].implode())))
    return t.join(C.unit_map() if umap is None else umap, on="pt_date", how="inner")


def action_rows() -> pl.DataFrame:
    """Regime-III action rows with category, write evidence, failure, hash (no text kept)."""
    t0 = pl.datetime(2026, 3, 24, 7, time_zone="UTC")
    a = (pl.read_parquet(C.SH / "actions.parquet", columns=["t", "agent", "action"]).with_row_index("row")
         .filter(pl.col("t") >= t0))
    bh = pl.read_parquet(C.SH / "actions_bash_head_fixed.parquet", columns=["row", "bash_head_fixed"])
    a = a.join(bh, on="row", how="left")
    to = (pl.read_parquet(C.BS / "turn_outcomes.parquet",
                          columns=["t", "agent", "act", "failed", "commit_ok", "push_ok", "file_write", "api_write",
                                   "deploy", "cmd"])
          .filter(pl.col("t") >= t0).unique(["agent", "t"], keep="first"))
    a = a.join(to, on=["agent", "t"], how="left")
    act = a["action"].cast(pl.Utf8).to_list()
    cmd = a["cmd"].to_list()
    head = a["bash_head_fixed"].cast(pl.Utf8).to_list()
    wr = (a["commit_ok"].fill_null(False) | a["push_ok"].fill_null(False) | a["file_write"].fill_null(False)
          | a["api_write"].fill_null(False) | a["deploy"].fill_null(False)).to_list()
    cats, hashes, tlong, hn = [], [], [], []
    for ac, cm, hd, w in zip(act, cmd, head, wr):
        nc = C.norm_cmd(cm) if ac == "bash" else None
        hn.append(int.from_bytes(hashlib.blake2b(nc.encode(), digest_size=8).digest(), "little") >> 1 if nc else None)
        if ac == "bash":
            cats.append("write" if w else C.classify_bash(cm if cm else hd))
            hashes.append(int.from_bytes(hashlib.blake2b(cm.encode(), digest_size=8).digest(), "little") >> 1
                          if cm else None)
            tlong.append(False)
        elif ac == "type":
            cats.append("gui_type")
            hashes.append(None)
            s = cm or ""
            tlong.append(len(s) >= 40 and not s.lower().startswith(("http", "www.")))
        elif ac in C.GUI_LOOK:
            cats.append("look"); hashes.append(None); tlong.append(False)
        elif ac in C.GUI_NAV:
            cats.append("gui"); hashes.append(None); tlong.append(False)
        else:
            cats.append(C.EVENT_CAT.get(ac, "other")); hashes.append(None); tlong.append(False)
    a = a.with_columns(pl.Series("cat", [C.CAT[c] for c in cats], dtype=pl.Int8),
                       pl.Series("h", hashes, dtype=pl.Int64), pl.Series("h_norm", hn, dtype=pl.Int64),
                       pl.Series("type_long", tlong),
                       pl.Series("any_write", wr))
    return a.select("t", "agent", "cat", "h", "h_norm", "type_long", "any_write", pl.col("commit_ok").fill_null(False),
                    pl.col("push_ok").fill_null(False), pl.col("failed").fill_null(False))


def build_calls(days: pl.DataFrame | None = None, umap: pl.DataFrame | None = None, out: Path | None = None,
                guard: bool = True) -> pl.DataFrame:
    t0 = time.time()
    out = out or C.OUT
    calls = load_calls_raw(days, umap)
    C.log("ledger calls", calls.height)
    a = action_rows()
    C.log("action rows", a.height, f"{time.time() - t0:.0f}s")
    keys = calls.select("turn_id", "agent", "t_first", "t_log").sort("t_first")
    m = (a.sort("t").join_asof(keys, left_on="t", right_on="t_first", by="agent", strategy="backward")
         .filter(pl.col("turn_id").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=1))))
    C.log("rows mapped to calls", m.height, "of", a.height)
    agg = (m.sort("t").group_by("turn_id").agg(
        pl.col("cat").min().alias("cat"), pl.col("any_write").any().alias("any_write"),
        pl.col("commit_ok").any().alias("commit_ok"), pl.col("push_ok").any().alias("push_ok"),
        pl.col("failed").sum().cast(pl.Int16).alias("n_fail"), pl.col("type_long").any().alias("type_long"),
        pl.col("h").drop_nulls().first().alias("h"), pl.col("h_norm").drop_nulls().first().alias("h_norm"),
        pl.len().cast(pl.Int16).alias("n_rows")))
    calls = calls.join(agg, on="turn_id", how="left")
    kind_cat = (pl.when(pl.col("kind") == "talk").then(C.CAT["talk"])
                .when(pl.col("kind").is_in(["pause", "wait"])).then(C.CAT["idle"])
                .when(pl.col("kind") == "search").then(C.CAT["room_read"]).otherwise(C.CAT["other"]))
    calls = calls.with_columns(pl.coalesce("cat", kind_cat).cast(pl.Int8).alias("cat"),
                               *[pl.col(c).fill_null(False) for c in ("any_write", "commit_ok", "push_ok", "type_long")],
                               pl.col("n_fail").fill_null(0), pl.col("n_rows").fill_null(0))
    # agent work commits (DQ4) -> the first call of the author with t_log >= commit time (<= 10 min)
    wc = (pl.read_parquet(C.SH / "work_commits.parquet",
                          columns=["t", "author_agent", "author_kind", "canonical", "imported", "automated", "holdout",
                                   "pt_date"])
          .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                  & (~pl.col("holdout") if guard else pl.lit(True)) & (pl.col("pt_date") >= C.REGIME3_START))
          .select("t", pl.col("author_agent").alias("agent")).drop_nulls().sort("t"))
    wm = wc.join_asof(calls.select("turn_id", "agent", "t_log").sort("t_log"), left_on="t", right_on="t_log",
                      by="agent", strategy="forward", tolerance="10m")
    C.log("work commits", wc.height, "mapped", wm["turn_id"].is_not_null().sum())
    wcnt = wm.drop_nulls("turn_id").group_by("turn_id").agg(pl.len().cast(pl.Int16).alias("n_work"))
    calls = calls.join(wcnt, on="turn_id", how="left").with_columns(pl.col("n_work").fill_null(0))
    # sequence, segments
    calls = calls.sort("agent", "t_first").with_columns(
        pl.int_range(pl.len()).over("agent", "pt_date").cast(pl.Int32).alias("seq"))
    rst = (pl.col("reset_consol") | pl.col("reset_session") | pl.col("first_of_day") | (pl.col("seq") == 0))
    calls = calls.with_columns(rst.alias("is_reset"))
    calls = calls.with_columns(pl.col("is_reset").cast(pl.Int32).cum_sum().over("agent", "pt_date").cast(pl.Int16)
                               .alias("seg"))
    sk = (pl.when(pl.col("reset_forced")).then(pl.lit("forced"))
          .when(pl.col("reset_consol")).then(pl.lit("voluntary"))
          .when(pl.col("reset_session")).then(pl.lit("session")).otherwise(pl.lit("day_start")))
    seginfo = (calls.filter(pl.col("is_reset")).select("agent", "pt_date", "seg", sk.alias("seg_kind"),
                                                       pl.col("seq").alias("seg_start"), "prev_seg_len"))
    seglen = calls.group_by("agent", "pt_date", "seg").agg(pl.len().cast(pl.Int16).alias("seg_len"))
    seginfo = seginfo.join(seglen, on=["agent", "pt_date", "seg"], how="left").sort("agent", "pt_date", "seg")
    seginfo = seginfo.with_columns(pl.col("seg_kind").shift(-1).over("agent", "pt_date").fill_null("day_end")
                                   .alias("seg_end_kind"))
    calls = calls.join(seginfo.drop("prev_seg_len"), on=["agent", "pt_date", "seg"], how="left")
    calls = calls.with_columns((pl.col("seq") - pl.col("seg_start") + 1).cast(pl.Int16).alias("pos"))
    # loop flag: exact command hash seen >= 2 times in the previous 10 calls, or 3rd real failure in 10 calls
    same = sum((pl.col("h") == pl.col("h").shift(o).over("agent", "pt_date")).fill_null(False).cast(pl.Int8)
               for o in range(1, 11))
    nf = sum((pl.col("n_fail").shift(o).over("agent", "pt_date").fill_null(0) > 0).cast(pl.Int8) for o in range(1, 10))
    calls = calls.with_columns(((same >= 2) | ((pl.col("n_fail") > 0) & (nf >= 2))).alias("in_loop"))
    same_n = sum((pl.col("h_norm") == pl.col("h_norm").shift(o).over("agent", "pt_date")).fill_null(False).cast(pl.Int8)
                 for o in range(1, 11))
    calls = calls.with_columns(((same_n >= 2) | ((pl.col("n_fail") > 0) & (nf >= 2))).alias("in_loop_norm"))
    if guard:
        C.refuse_holdout(calls["pt_date"].unique().to_list(), "calls")
    cols = ["turn_id", "agent", "pt_date", "goal_no", "unit_id", "period", "seq", "t_call", "t_first", "t_log", "kind",
            "talk", "room", "cat", "any_write", "commit_ok", "push_ok", "type_long", "n_fail", "n_work", "n_rows",
            "n_agent", "n_human", "n_nudge", "n_ment", "k_new", "chars_new", "ctx_pos", "reset_consol", "reset_forced",
            "reset_session", "first_of_day", "prev_seg_len", "is_reset", "seg", "seg_kind", "seg_start", "seg_len",
            "seg_end_kind", "pos", "h", "in_loop", "h_norm", "in_loop_norm"]
    calls = calls.select(cols)
    calls.write_parquet(out / "calls.parquet", compression="zstd")
    C.log("calls written", calls.height, f"{time.time() - t0:.0f}s")
    return calls


def build_events(calls: pl.DataFrame, out: Path | None = None) -> pl.DataFrame:
    """Anchors. Real: the first call of a segment opened by a consolidation (forced / voluntary). Pseudo: pos == 31
    (window -20..+10 inside the segment) and pos == 21 (window -10..+20) in segments that run >= pos + 10 / + 20."""
    seg = calls.filter(pl.col("is_reset")).select("agent", "pt_date", "seg", "seq", "seg_kind", "seg_len", "prev_seg_len",
                                                  "t_call", "unit_id", "period", "goal_no")
    prev = (calls.group_by("agent", "pt_date", "seg").agg(pl.len().alias("plen"), pl.col("seg_kind").first().alias("pkind"))
            .with_columns((pl.col("seg") + 1).cast(pl.Int16).alias("seg")))
    real = (seg.filter(pl.col("seg_kind").is_in(["forced", "voluntary"]))
            .join(prev, on=["agent", "pt_date", "seg"], how="left")
            .with_columns(pl.col("seg_kind").alias("ev_kind"), pl.col("plen").fill_null(0).alias("n_pre_avail"),
                          pl.col("seg_len").alias("n_post_avail"), pl.col("pkind").alias("prev_kind")))
    # memory dose: memory_stats snapshot within 180 s before the first post-reset call
    ms = pl.read_parquet(C.SH / "memory_stats.parquet", columns=["t", "agent", "n_lines", "lines_added", "lines_removed"])
    real = real.sort("t_call").join_asof(ms.sort("t"), left_on="t_call", right_on="t", by="agent", strategy="backward",
                                         tolerance="180s")
    real = real.select("agent", "pt_date", "seg", "seq", "ev_kind", "prev_seg_len", "n_pre_avail", "n_post_avail",
                       "prev_kind", "t_call", "unit_id", "period", "goal_no", "n_lines", "lines_added", "lines_removed")
    ps = []
    for p0, kind in ((31, "pseudo31"), (21, "pseudo21")):
        need = 9 if p0 == 31 else 19   # +1 = pos p0; the last window offset sits at pos 40 (forced segments hold 40 calls)
        e = (calls.filter((pl.col("pos") == p0) & (pl.col("seg_len") >= p0 + need))
             .select("agent", "pt_date", "seg", "seq", pl.lit(kind).alias("ev_kind"), pl.lit(None, pl.Int16).alias("prev_seg_len"),
                     pl.lit(p0 - 1, pl.UInt32).alias("n_pre_avail"), (pl.col("seg_len") - p0 + 1).cast(pl.Int16).alias("n_post_avail"),
                     pl.col("seg_kind").alias("prev_kind"), "t_call", "unit_id", "period", "goal_no",
                     pl.lit(None, pl.Int32).alias("n_lines"), pl.lit(None, pl.Int32).alias("lines_added"),
                     pl.lit(None, pl.Int32).alias("lines_removed")))
        ps.append(e)
    ev = pl.concat([real.with_columns(pl.col("n_pre_avail").cast(pl.UInt32), pl.col("n_post_avail").cast(pl.Int16))] + ps,
                   how="vertical_relaxed")
    ev = ev.with_columns(pl.col("t_call").dt.convert_time_zone("America/Los_Angeles").dt.hour().alias("hour_pt"))
    ev = ev.sort("agent", "t_call").with_row_index("ev_id")
    ev.write_parquet((out or C.OUT) / "events.parquet", compression="zstd")
    C.log("events", ev.group_by("ev_kind").len().sort("ev_kind").rows())
    return ev


def build_v3(calls: pl.DataFrame):
    v = pl.read_parquet(C.SH / "behavior_states_v3.parquet")
    days = C.nonholdout_days()["pt_date"]
    v = v.filter((pl.col("regime") == "III") & ~pl.col("holdout") & pl.col("labeled") & pl.col("pt_date").is_in(days.implode()))
    P = [c for c in v.columns if c.startswith("p_") and c not in ("p_blocked", "p_others_work", "p_addresses_participant")
         and not c.startswith("p_progress")]
    pm = v.select(P).to_numpy().astype(float)
    pm = pm / np.clip(pm.sum(1, keepdims=True), 1e-9, None)
    ent = -(np.where(pm > 0, pm * np.log(np.clip(pm, 1e-12, None)), 0)).sum(1)
    v = v.with_columns(pl.Series("H_v3", ent.astype(np.float32)))
    rs = (calls.filter(pl.col("is_reset")).select("agent", "pt_date", pl.col("t_call").alias("t_reset"),
                                                   pl.col("seg_kind").alias("reset_kind")).sort("t_reset"))
    v = v.sort("t0").join_asof(rs, left_on="t0", right_on="t_reset", by=["agent", "pt_date"], strategy="backward")
    nxt = rs.rename({"t_reset": "t_next", "reset_kind": "next_kind"})
    v = v.sort("t0").join_asof(nxt, left_on="t0", right_on="t_next", by=["agent", "pt_date"], strategy="forward")
    v = v.with_columns(((pl.col("t0") - pl.col("t_reset")).dt.total_seconds() / 60).cast(pl.Float32).alias("min_since"),
                       ((pl.col("t_next") - pl.col("t1")).dt.total_seconds() / 60).cast(pl.Float32).alias("min_until"),
                       ((pl.col("t_next") < pl.col("t1")) & pl.col("t_next").is_not_null()).alias("reset_inside"))
    v = v.join(C.unit_map(), on="pt_date", how="inner")
    keep = ["agent", "pt_date", "goal_no", "unit_id", "period", "w", "t0", "t1", "active", "n_turns", "n_actions",
            "n_errors", "n_consolidate", "n_commit_ok", "n_push_ok", "n_file_write", "progress_score", "p_blocked",
            "post_reset", "H_v3", "reset_kind", "min_since", "reset_inside", "next_kind", "min_until"] + P
    v = v.select(keep)
    C.refuse_holdout(v["pt_date"].unique().to_list(), "v3")
    v.write_parquet(C.OUT / "v3_windows.parquet", compression="zstd")
    C.log("v3 windows", v.height)


def _age_bin(age: np.ndarray) -> np.ndarray:
    return np.clip(np.searchsorted(AGE_EDGES, age, side="right") - 1, 0, N_AGE - 1)


def build_replies(calls: pl.DataFrame, out: Path | None = None, guard: bool = True):
    """Per agent talk message B: visible pool (ledger items read by the agent's calls up to B's call, age <= 60 min,
    same day) counted by read class x age bin; B's DQ2 parent class and age bin."""
    t0 = time.time()
    cc = pl.read_parquet(C.SH / "chat_core.parquet", columns=["message_id", "t", "speaker_kind", "agent", "pt_date"])
    tmsg = cc.select("message_id", pl.col("t").alias("t_msg"))
    B = (cc.filter((pl.col("speaker_kind") == "agent") & pl.col("pt_date").is_in(calls["pt_date"].unique().implode()))
         .select(pl.col("message_id").alias("B"), "agent", "t", "pt_date").sort("t"))
    ck = calls.select("turn_id", "agent", "t_first", "t_log", "t_call", "seq", "seg", "pos", "seg_kind", "seg_len",
                      "unit_id", "period").sort("t_first")
    B = B.join_asof(ck, left_on="t", right_on="t_first", by="agent", strategy="backward")
    B = B.filter(pl.col("turn_id").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=2)))
    C.log("talk messages mapped", B.height)
    it = (pl.read_parquet(C.SH / "context_ledger_items.parquet", columns=["turn_id", "message_id", "sender", "kind"])
          .join(calls.select("turn_id", "agent", "pt_date", "seq", "seg", "pos"), on="turn_id", how="inner")
          .join(tmsg, on="message_id", how="left"))
    par = (pl.read_parquet(C.SH / "reply_pairs.parquet", columns=["B_message_id", "A_message_id", "pair_set", "parent"])
           .filter((pl.col("pair_set") == "cand") & pl.col("parent"))
           .select(pl.col("B_message_id").alias("B"), pl.col("A_message_id").alias("A")).unique("B"))
    B = B.join(par, on="B", how="left")
    out = []
    itg = {k: g for k, g in it.sort("t_msg").group_by(["agent", "pt_date"])}
    for (a, d), g in B.group_by(["agent", "pt_date"]):
        ig = itg.get((a, d))
        if ig is None:
            continue
        tm = ig["t_msg"].dt.epoch("us").to_numpy() / 1e6
        iseq, iseg, ipos = ig["seq"].to_numpy(), ig["seg"].to_numpy(), ig["pos"].to_numpy()
        mid = ig["message_id"].to_list()
        midx = {m: i for i, m in enumerate(mid)}
        for r in g.iter_rows(named=True):
            tb = r["t"].timestamp()
            sel = np.nonzero((iseq <= r["seq"]) & (tm >= tb - 3600) & (tm < tb))[0]
            age = tb - tm[sel]
            ab = _age_bin(age)
            # read class relative to B's segment boundary (erasure anchor) and to the pseudo boundary at pos 21
            post = iseg[sel] == r["seg"]
            cls_e = np.where(post, 0, 2)                             # post / pre_erased
            cls_p = np.where(post & (ipos[sel] >= 21), 0, np.where(post, 1, 2))  # post / pre_ctx / pre_erased (pos 21)
            ne = np.zeros((3, N_AGE), np.int16)
            npz = np.zeros((3, N_AGE), np.int16)
            np.add.at(ne, (cls_e, ab), 1)
            np.add.at(npz, (cls_p, ab), 1)
            pc_e = pc_p = pb = -1
            if r["A"] is not None and r["A"] in midx:
                j = midx[r["A"]]
                k = np.nonzero(sel == j)[0]
                if len(k):
                    pc_e, pc_p, pb = int(cls_e[k[0]]), int(cls_p[k[0]]), int(ab[k[0]])
            out.append((r["B"], a, d, r["unit_id"], r["period"], r["seq"], r["seg"], r["pos"], r["seg_kind"], r["seg_len"],
                        r["A"] is not None, pc_e, pc_p, pb, ne.ravel().tolist(), npz.ravel().tolist()))
    df = pl.DataFrame(out, schema=["B", "agent", "pt_date", "unit_id", "period", "seq", "seg", "pos", "seg_kind", "seg_len",
                                   "has_parent", "par_cls_e", "par_cls_p", "par_age", "n_e", "n_p"], orient="row")
    df = df.with_columns(pl.col("n_e").list.to_array(3 * N_AGE), pl.col("n_p").list.to_array(3 * N_AGE),
                         pl.col("agent").cast(pl.Int8), pl.col("pos").cast(pl.Int16), pl.col("par_cls_e").cast(pl.Int8),
                         pl.col("par_cls_p").cast(pl.Int8), pl.col("par_age").cast(pl.Int8))
    if guard:
        C.refuse_holdout(df["pt_date"].unique().to_list(), "reply pools")
    df.write_parquet((out or C.OUT) / "reply_pools.parquet", compression="zstd")
    C.log("reply pools", df.height, f"{time.time() - t0:.0f}s")


def _unit_rows(X: np.ndarray) -> np.ndarray:
    X = X.astype(np.float32)
    return X / np.clip(np.linalg.norm(X, axis=1, keepdims=True), 1e-6, None)


def build_pull(calls: pl.DataFrame):
    """Consecutive chat statements (prev, next) of one agent-day; messages read by the agent's calls in (prev, next]
    split at the boundary (the consolidation reset; within pairs: the middle call); pull sums by class x age bin."""
    t0 = time.time()
    st = pl.read_parquet(C.EMB / "statements.parquet").with_row_index("srow")
    ci = pl.read_parquet(C.EMB / "chat_index.parquet").with_row_index("src_row")
    st = st.filter(pl.col("kind") == "chat").join(ci.with_columns(pl.col("src_row").cast(pl.UInt32)), on="src_row",
                                                  how="left")
    vec = {"bge": _unit_rows(np.load(C.EMB / "statements_white32_bge_small.npy")),
           "gte": _unit_rows(np.load(C.EMB / "statements_white32_gte_modernbert.npy"))}
    cc = pl.read_parquet(C.SH / "chat_core.parquet", columns=["message_id", "t", "speaker_kind", "agent"])
    srow = st.select("message_id", "srow")
    A = (cc.filter(pl.col("speaker_kind") == "agent").join(srow, on="message_id", how="inner")
         .select("message_id", "agent", "t", "srow").sort("t"))
    ck = calls.select("turn_id", "agent", "pt_date", "t_first", "t_log", "seq", "seg", "seg_kind", "unit_id",
                      "period").sort("t_first")
    A = A.join_asof(ck, left_on="t", right_on="t_first", by="agent", strategy="backward")
    A = A.filter(pl.col("turn_id").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=2)))
    A = A.sort("agent", "t").with_columns(
        *[pl.col(c).shift(1).over("agent", "pt_date").alias(f"{c}_prev") for c in ("srow", "t", "seq", "seg")])
    P = A.filter(pl.col("srow_prev").is_not_null())
    P = P.with_columns((pl.col("seg") - pl.col("seg_prev")).alias("n_reset"))
    seg_kind_next = P["seg_kind"].to_list()
    lab = []
    for nr, sk in zip(P["n_reset"].to_list(), seg_kind_next):
        lab.append("within" if nr == 0 else (sk if (nr == 1 and sk in ("forced", "voluntary")) else "other"))
    P = P.with_columns(pl.Series("label", lab)).filter(pl.col("label") != "other")
    P = P.with_columns(((pl.col("t") - pl.col("t_prev")).dt.total_seconds()).alias("gap_s"))
    C.log("pairs", P.group_by("label").len().rows())
    it = (pl.read_parquet(C.SH / "context_ledger_items.parquet", columns=["turn_id", "message_id"])
          .join(calls.select("turn_id", "agent", "pt_date", "seq", "seg"), on="turn_id", how="inner")
          .join(srow, on="message_id", how="inner")
          .join(cc.select("message_id", pl.col("t").alias("t_msg")), on="message_id", how="left"))
    itg = {k: g for k, g in it.sort("seq").group_by(["agent", "pt_date"])}
    rows = []
    for (a, d), g in P.group_by(["agent", "pt_date"]):
        ig = itg.get((a, d))
        if ig is None:
            continue
        iseq, iseg = ig["seq"].to_numpy(), ig["seg"].to_numpy()
        isr = ig["srow"].to_numpy()
        tm = ig["t_msg"].dt.epoch("us").to_numpy() / 1e6
        for r in g.iter_rows(named=True):
            sel = np.nonzero((iseq > r["seq_prev"]) & (iseq <= r["seq"]))[0]
            if len(sel) == 0:
                continue
            if r["label"] == "within":
                mid = (r["seq_prev"] + r["seq"]) // 2 + 1
                post = iseq[sel] >= mid
            else:
                post = iseg[sel] == r["seg"]
            age = r["t"].timestamp() - tm[sel]
            ab = _age_bin(np.clip(age, 0, None))
            cls = np.where(post, 0, 1)
            rec = [r["message_id"], a, d, r["unit_id"], r["period"], r["label"], float(r["gap_s"]), int(len(sel)),
                   int(post.sum()), r["seq"] - r["seq_prev"]]
            for mname, X in vec.items():
                y = X[r["srow"]] - X[r["srow_prev"]]
                U = X[isr[sel]] - X[r["srow_prev"]]
                num = U @ y
                den = (U * U).sum(1)
                N = np.zeros((2, N_AGE)); D = np.zeros((2, N_AGE))
                np.add.at(N, (cls, ab), num); np.add.at(D, (cls, ab), den)
                rec += [N.ravel().astype(np.float32).tolist(), D.ravel().astype(np.float32).tolist()]
            rec.append(float(X[r["srow"]] @ X[r["srow_prev"]]))
            rows.append(rec)
    schema = ["B", "agent", "pt_date", "unit_id", "period", "label", "gap_s", "n_read", "n_post", "n_calls",
              "num_bge", "den_bge", "num_gte", "den_gte", "cos_prev_next_gte"]
    df = pl.DataFrame(rows, schema=schema, orient="row")
    df = df.with_columns(*[pl.col(c).list.to_array(2 * N_AGE) for c in ("num_bge", "den_bge", "num_gte", "den_gte")],
                         pl.col("agent").cast(pl.Int8))
    C.refuse_holdout(df["pt_date"].unique().to_list(), "pull pairs")
    df.write_parquet(C.OUT / "pull_pairs.parquet", compression="zstd")
    C.log("pull pairs", df.height, df.group_by("label").len().rows(), f"{time.time() - t0:.0f}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="calls,events,v3,replies,pull")
    args = ap.parse_args()
    only = set(args.only.split(","))
    C.OUT.mkdir(parents=True, exist_ok=True)
    calls = build_calls() if "calls" in only else pl.read_parquet(C.OUT / "calls.parquet")
    if "events" in only:
        build_events(calls)
    if "v3" in only:
        build_v3(calls)
    if "replies" in only:
        build_replies(calls)
    if "pull" in only:
        build_pull(calls)
    C.write_provenance({"regime": "III", "holdout": "excluded (calendar flag and holdout_mask)",
                        "forced": "reset_forced (41-42 record segment)", "voluntary": "reset_consol & ~reset_forced",
                        "pseudo": "pos 31 (window -20..+10), pos 21 (window -10..+20)",
                        "categories": C.CATS, "reacquisition": C.REACQ, "age_edges_s": AGE_EDGES.tolist(),
                        "work": "canonical & ~imported & author_kind=='agent' & ~automated, mapped forward <= 10 min",
                        "loop": "same exact command hash >= 2x in previous 10 calls, or 3rd real failure in 10 calls",
                        "text": "command text classified and hashed in memory only; never stored"})


if __name__ == "__main__":
    main()
