"""H69 scheme: restatement sequences, context self-share, inputs and source-location pairs (regime III, non-holdout).

  uv run python hypotheses/H69-loops-context-fixed-points/scheme/build.py               # all periods
  uv run python hypotheses/H69-loops-context-fixed-points/scheme/build.py --period G38

Definitions (card, "Data scheme"):
- statement: an agent chat statement (DQ5 `statements`, kind = chat), mapped to its producing ledger call through its
  AGENT_TALK event (t_first <= t_event <= t_log of the agent's call; DQ2's rule);
- segment: the agent's calls between two resets (reset_consol | reset_session); forced = reset_forced (NE41);
  segments can cross midnight (regime III has no reset at day start);
- cross-call restatement: DQ5 self_repeat by a model whose matched source statement comes from an EARLIER call;
  r_either (primary, H55 restatement), r_bge, r_gte, r_both (copy);
- O (own statements in context): earlier statements of the agent from earlier calls of the same segment and PT day
  (o_day; the flag's comparison set) and of the same segment on any day (o_all); K = k_ctx at the producing call;
- read items since the previous statement: ledger items of the agent's calls in (call of t-1, call of t];
- in-flight items: messages by others in the agent's room (room at t_call) posted in [t_call, t_statement);
- novelty of an item: 1 - max cosine (raw unit vectors) to the agent's last 5 statements before t (same day);
- pairs (t, u): u an earlier same-day statement of the agent from an earlier call, lag <= 3 h, at most the 40 most
  recent; cosines under both models, lag, calls between, same segment, a forced reset between, pseudo-half.
Holdout days are dropped (calendar.holdout, holdout_mask, ledger holdout) before anything is computed. No text.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H69-loops-context-fixed-points"
PERIODS = [36, 37, 38, 39, 40, 41, 42, 44, 51]
MAX_LAG_S = 3 * 3600
MAX_PAIRS = 40
N_RECENT = 5
ALLOW_HOLDOUT = False  # only confirm.py sets this (guarded); round 1 never reads held-out rows


def days_of(g: int) -> list[str]:
    cal = pl.read_parquet(SH / "calendar.parquet").filter(
        (pl.col("goal_no") == g) & (pl.col("regime").cast(pl.Utf8) == "III") & (pl.col("window_s") > 0))
    d = cal["pt_date"].to_list()
    hm = holdout_mask(d, [g] * len(d))
    return sorted(x for x, m, h in zip(d, hm, cal["holdout"].to_list()) if not m and not h)


class Emb:
    def __init__(self):
        self.bge = np.load(ED / "chat_bge_small.npy", mmap_mode="r")
        self.gte = np.load(ED / "chat_gte_modernbert.npy", mmap_mode="r")
        ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("crow")
        self.row_of = dict(zip(ci["message_id"].to_list(), ci["crow"].to_list()))

    def get(self, rows: np.ndarray, which: str) -> np.ndarray:
        a = self.bge if which == "bge" else self.gte
        rows = np.asarray(rows, dtype=np.int64)
        order = np.argsort(rows)
        v = np.empty((len(rows), a.shape[1]), dtype=np.float32)
        v[order] = np.asarray(a[rows[order]], dtype=np.float32)
        v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
        return v


def build(g: int, emb: Emb, flags: pl.DataFrame, stm: pl.DataFrame, ev: pl.DataFrame, chat: pl.DataFrame,
          kicks: pl.DataFrame, thr: dict) -> dict:
    t0 = time.time()
    days = days_of(g)
    if not days:
        return {}
    # ---- calls (all agent calls on these days), ordered per agent; segments over the agent's timeline
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter(pl.col("pt_date").is_in(days) & (~pl.col("holdout") | pl.lit(ALLOW_HOLDOUT)))
          .select("turn_id", "agent", "pt_date", "t_call", "t_first", "t_log", "ctx_mode", "k_ctx", "ctx_pos",
                  "chars_new", "k_new", "reset_consol", "reset_forced", "reset_session", "room")
          .collect().sort("agent", "t_call"))
    lt = lt.with_columns(
        (pl.col("reset_consol") | pl.col("reset_session")).fill_null(False).alias("reset_any"),
        pl.col("reset_forced").fill_null(False))
    lt = lt.with_columns(
        pl.int_range(pl.len()).over("agent").alias("call_idx"),
        pl.col("reset_any").cast(pl.Int32).cum_sum().over("agent").alias("seg"),
        pl.col("reset_forced").cast(pl.Int32).cum_sum().over("agent").alias("n_forced_cum"),
        pl.col("reset_any").cast(pl.Int32).cum_sum().over("agent").alias("n_reset_cum"),
    ).with_columns(
        pl.col("chars_new").fill_null(0).cum_sum().over("agent", "seg").alias("chars_ctx"),
        pl.int_range(pl.len()).over("agent", "seg").alias("seg_pos"),
        pl.len().over("agent", "seg").alias("seg_len"))
    # ---- statements -> calls
    s = (stm.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days) & (~pl.col("holdout") | pl.lit(ALLOW_HOLDOUT))))
    s = s.join(chat.select("crow", "message_id", pl.col("length").alias("chars")), left_on="src_row", right_on="crow",
               how="left")
    s = s.join(ev, on="message_id", how="left").with_columns(pl.col("t_ev").fill_null(pl.col("t"))).sort("t_ev")
    cw = lt.select("turn_id", "agent", "t_first", "t_log").sort("t_first")
    s = s.join_asof(cw, left_on="t_ev", right_on="t_first", by="agent", strategy="backward")
    n_all = s.height
    s = s.filter(pl.col("turn_id").is_not_null() & (pl.col("t_ev") <= pl.col("t_log")))
    s = s.join(lt.select("turn_id", "call_idx", "seg", "ctx_pos", "k_ctx", "chars_ctx", "n_forced_cum", "n_reset_cum",
                         "t_call", "room", "seg_pos", "seg_len", "ctx_mode"), on="turn_id", how="left")
    s = s.filter(pl.col("ctx_mode") == "cu")
    s = s.join(flags, on="srow", how="left").sort("agent", "t")
    # cross-call restatement: source statement's call must be earlier
    src_call = s.select(pl.col("srow").alias("src"), pl.col("call_idx").alias("src_call"))
    for m in ("bge", "gte"):
        s = s.join(src_call.rename({"src": f"self_repeat_src_{m}", "src_call": f"src_call_{m}"}),
                   on=f"self_repeat_src_{m}", how="left")
        s = s.with_columns((pl.col(f"self_repeat_{m}").fill_null(False)
                            & (pl.col(f"src_call_{m}").fill_null(10 ** 9) < pl.col("call_idx"))).alias(f"r_{m}"))
    s = s.with_columns((pl.col("r_bge") | pl.col("r_gte")).alias("r_either"),
                       (pl.col("r_bge") & pl.col("r_gte")).alias("r_both"),
                       (pl.col("self_repeat_bge").fill_null(False) | pl.col("self_repeat_gte").fill_null(False)).alias(
                           "flag_any"))
    s = s.sort("agent", "t").with_row_index("sid")
    # ---- per agent-day sequential quantities
    rows_extra = []
    items_rows = []
    pair_rows = []
    items_all = (pl.scan_parquet(SH / "context_ledger_items.parquet")
                 .filter(pl.col("turn_id").is_in(lt["turn_id"].implode()))
                 .select("turn_id", "message_id", "sender", "kind").collect()
                 .join(lt.select("turn_id", "agent", "call_idx"), on="turn_id", how="left"))
    items_all = items_all.with_columns(
        pl.col("message_id").replace_strict(emb.row_of, default=-1, return_dtype=pl.Int64).alias("crow"))
    item_by_agent = {int(a): g_ for (a,), g_ in items_all.group_by(["agent"])}
    ch_g = chat.filter(pl.col("pt_date").is_in(days)).select("crow", "message_id", "t", "room", "speaker_kind", "agent")
    ch_g = ch_g.join(kicks.select("message_id", pl.col("kind").cast(pl.Utf8).alias("kick_kind")), on="message_id",
                     how="left")
    ch_t = ch_g["t"].dt.epoch("us").to_numpy()
    ch_room = ch_g["room"].to_numpy()
    ch_ag = ch_g["agent"].fill_null(-1).to_numpy()
    ch_crow = ch_g["crow"].to_numpy()
    ch_kind = ch_g["speaker_kind"].cast(pl.Utf8).to_list()
    ch_kick = ch_g["kick_kind"].to_list()
    order_t = np.argsort(ch_t)
    ch_t_sorted = ch_t[order_t]
    lt_by_agent = {int(a): g_ for (a,), g_ in lt.group_by(["agent"])}
    for (a, d), ss in s.group_by(["agent", "pt_date"], maintain_order=True):
        a = int(a)
        ss = ss.sort("t")
        n = ss.height
        crow = ss["src_row"].to_numpy().astype(np.int64)
        vb = emb.get(crow, "bge")
        vg = emb.get(crow, "gte")
        tt = ss["t"].dt.epoch("us").to_numpy()
        tcall = ss["t_call"].dt.epoch("us").to_numpy()
        ci = ss["call_idx"].to_numpy()
        seg = ss["seg"].to_numpy()
        nf = ss["n_forced_cum"].to_numpy()
        nr = ss["n_reset_cum"].to_numpy()
        segpos = ss["seg_pos"].to_numpy()
        seglen = ss["seg_len"].to_numpy()
        chars = ss["chars"].fill_null(0).to_numpy()
        room = ss["room"].fill_null(-1).to_numpy()
        sid = ss["sid"].to_numpy()
        ia = item_by_agent.get(a)
        ia_ci = ia["call_idx"].to_numpy() if ia is not None else np.zeros(0, int)
        ia_crow = ia["crow"].to_numpy() if ia is not None else np.zeros(0, int)
        ia_kind = ia["kind"].cast(pl.Utf8).to_list() if ia is not None else []
        for i in range(n):
            earlier_call = ci[:i] < ci[i]
            same_seg = earlier_call & (seg[:i] == seg[i])
            o_day = int(same_seg.sum())
            own_chars = int(chars[:i][same_seg].sum())
            prev = i - 1 if i > 0 else None
            rec = dict(sid=int(sid[i]), o_day=o_day, own_chars_day=own_chars, n_prev_day=i,
                       n_prev_xcall=int(earlier_call.sum()))
            if prev is not None:
                rec.update(lag_prev_s=(tt[i] - tt[prev]) / 1e6, calls_prev=int(ci[i] - ci[prev]),
                           forced_between=bool(nf[i] > nf[prev]), reset_between=bool(nr[i] > nr[prev]))
            # recent own vectors (last N_RECENT statements before t, same day)
            lo = max(0, i - N_RECENT)
            rb, rg = vb[lo:i], vg[lo:i]
            # read items since previous statement
            if prev is not None and ia is not None:
                m_ = (ia_ci > ci[prev]) & (ia_ci <= ci[i])
                idx = np.where(m_)[0]
                rec["n_read"] = int(len(idx))
                if len(idx):
                    cr = ia_crow[idx]
                    ok = cr >= 0
                    nb = np.ones(len(idx), np.float32)
                    ng = np.ones(len(idx), np.float32)
                    if ok.any() and i > 0:
                        eb = emb.get(cr[ok], "bge")
                        eg = emb.get(cr[ok], "gte")
                        nb[ok] = 1 - (eb @ rb.T).max(axis=1)
                        ng[ok] = 1 - (eg @ rg.T).max(axis=1)
                    for j, jj in enumerate(idx):
                        items_rows.append((int(sid[i]), 0, ia_kind[jj], float(nb[j]), float(ng[j])))
            # in-flight items: others' messages in the agent's room posted in [t_call, t)
            lo_i = np.searchsorted(ch_t_sorted, tcall[i], side="left")
            hi_i = np.searchsorted(ch_t_sorted, tt[i], side="left")
            cand = order_t[lo_i:hi_i]
            cand = cand[(ch_room[cand] == room[i]) & (ch_ag[cand] != a)]
            rec["n_inflight"] = int(len(cand))
            if len(cand) and i > 0:
                eb = emb.get(ch_crow[cand], "bge")
                eg = emb.get(ch_crow[cand], "gte")
                nb = 1 - (eb @ rb.T).max(axis=1)
                ng = 1 - (eg @ rg.T).max(axis=1)
                for j, c in enumerate(cand):
                    k_ = ch_kind[c]
                    if k_ == "automated":
                        k_ = ch_kick[c] or "automated_other"
                    elif k_ == "human":
                        k_ = "human"
                    items_rows.append((int(sid[i]), 1, k_, float(nb[j]), float(ng[j])))
            rows_extra.append(rec)
            # pairs (t, u)
            js = np.where(earlier_call & ((tt[i] - tt[:i]) <= MAX_LAG_S * 1e6))[0][-MAX_PAIRS:]
            if len(js):
                cb = vb[js] @ vb[i]
                cg = vg[js] @ vg[i]
                insg = seg[js] == seg[i]
                half_u = segpos[js] >= seglen[js] / 2
                half_t = segpos[i] >= seglen[i] / 2
                for j, u in enumerate(js):
                    pair_rows.append((int(sid[i]), int(sid[u]), float(cb[j]), float(cg[j]), (tt[i] - tt[u]) / 1e6,
                                      int(ci[i] - ci[u]), bool(insg[j]), bool(nf[i] > nf[u]), bool(nr[i] > nr[u]),
                                      bool(insg[j] and (half_u[j] == half_t))))
    ex = pl.DataFrame(rows_extra, infer_schema_length=None)
    s = s.join(ex, on="sid", how="left")
    keep = ["sid", "srow", "agent", "pt_date", "goal_no", "t", "turn_id", "call_idx", "seg", "ctx_pos", "k_ctx",
            "chars_ctx", "chars", "room", "seg_pos", "seg_len", "r_either", "r_bge", "r_gte", "r_both", "flag_any",
            "templated", "cross_echo", "self_repeat_cos_bge", "self_repeat_cos_gte", "o_day", "own_chars_day",
            "n_prev_day", "n_prev_xcall", "lag_prev_s", "calls_prev", "forced_between", "reset_between", "n_read",
            "n_inflight"]
    s = s.select([c for c in keep if c in s.columns])
    o = OUT / f"G{g:02d}"
    o.mkdir(parents=True, exist_ok=True)
    s.write_parquet(o / "statements.parquet", compression="zstd")
    it = pl.DataFrame(items_rows, schema=[("sid", pl.UInt32), ("inflight", pl.Int8), ("kind", pl.Utf8),
                                          ("nov_bge", pl.Float32), ("nov_gte", pl.Float32)], orient="row")
    it.write_parquet(o / "items.parquet", compression="zstd")
    pr = pl.DataFrame(pair_rows, schema=[("sid", pl.UInt32), ("sid_u", pl.UInt32), ("cos_bge", pl.Float32),
                                         ("cos_gte", pl.Float32), ("lag_s", pl.Float32), ("calls_between", pl.Int32),
                                         ("in_seg", pl.Boolean), ("forced_between", pl.Boolean),
                                         ("reset_between", pl.Boolean), ("same_half", pl.Boolean)], orient="row")
    pr.write_parquet(o / "pairs.parquet", compression="zstd")
    info = dict(period=f"G{g:02d}", days=len(days), statements_mapped=s.height, statements_all=n_all,
                items=it.height, pairs=pr.height, secs=round(time.time() - t0, 1))
    (o / "build.json").write_text(json.dumps(info, indent=1))
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, default=None)
    a = ap.parse_args()
    ps = [a.period] if a.period else PERIODS
    emb = Emb()
    meta = json.loads((SH / "statement_flags_meta.json").read_text())
    thr = dict(bge=meta["thr_bge"], gte=meta["thr_gte_rate_matched"])
    stm = pl.read_parquet(ED / "statements.parquet").with_row_index("srow").filter(
        (pl.col("kind") == "chat") & (pl.col("regime") == "III") & ~pl.col("holdout"))
    flags = pl.read_parquet(SH / "statement_flags.parquet", columns=[
        "srow", "self_repeat_bge", "self_repeat_gte", "self_repeat_src_bge", "self_repeat_src_gte", "templated",
        "cross_echo", "self_repeat_cos_bge", "self_repeat_cos_gte"])
    ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "message_id", "action_type"])
          .filter(pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev"))
          .unique("message_id"))
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("crow")
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind",
                                                               "agent", "length"]).join(ci, on="message_id", how="left")
    kicks = pl.read_parquet(SH / "kicks_classified.parquet", columns=["message_id", "kind"]).filter(
        pl.col("message_id").is_not_null()).unique("message_id")
    infos = []
    for g in ps:
        info = build(g, emb, flags, stm, ev, chat, kicks, thr)
        print(info, flush=True)
        infos.append(info)
    prov = {"built_by": "hypotheses/H69-loops-context-fixed-points/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements", "shared/statement_flags",
                                   "shared/embeddings/chat_{bge_small,gte_modernbert}", "shared/context_ledger_turns",
                                   "shared/context_ledger_items", "shared/events_core", "shared/chat_core",
                                   "shared/kicks_classified", "shared/calendar"]}],
            "params": {"periods": ps, "max_lag_s": MAX_LAG_S, "max_pairs": MAX_PAIRS, "n_recent": N_RECENT,
                       "thresholds": thr, "holdout": "excluded (calendar.holdout | holdout_mask | ledger holdout)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
