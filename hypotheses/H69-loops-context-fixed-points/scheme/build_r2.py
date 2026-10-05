"""H69 round 2 scheme: own content in tokens (R1), erasure dose and cap hits (R2), memory containment of erased
sources (R3). Regime III, non-reserved days only. Reads the round-1 period frames; writes new files next to them, so
round 1 reproduces unchanged.

  uv run python hypotheses/H69-loops-context-fixed-points/scheme/build_r2.py tokens          # R1/R2 covariates
  uv run python hypotheses/H69-loops-context-fixed-points/scheme/build_r2.py memory          # R3 (one raw pass)

Definitions (card, "Round 2"):
- P = H45 prompt tokens of a call (`data/processed/H45-context-homeostasis/calls.parquet`); R = room tokens on H45's
  ruler (`calibration.json`: a_L per item, b_L per char, e_L per other-room event), summed over the H69 segment;
  W = P - R (own content). W_0 = W at the first call of the segment that has P. Own chat tokens C = a_L O + b_L chars
  over own statements in earlier calls of the segment. Own tool tokens U = max(W - W_0 - C, 0).
- dense = Anthropic or Google agent (P on every call). base_pos = segment position of the W_0 call.
- seg_dose = log(1 + max(W_last - W_0, 0)/1000), W_last = W at the segment's last call with P: the own tokens an
  erasure at the segment's end removes. cap_cum = cumulative 200-event cap hits of the agent (NE22) up to the call.
- Memory (R3): for pairs (t, u) with u erased (in_seg false), M_t = the agent's latest `agent_memories` snapshot
  created before t's t_call, M_u = the latest before u's time. c = share of u's word 3-grams found in M. The raw
  memory text and the chat text are read in memory only; only numbers are written.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import orjson  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import build as B  # noqa: E402  (H69's own round-1 scheme)
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H69-loops-context-fixed-points"
H45 = ROOT / "data/processed/H45-context-homeostasis"
RAW = ROOT / "data/raw/ai-village"
PERIODS = [36, 37, 38, 39, 40, 41, 42, 44, 51]
DENSE = {"Anthropic", "Google"}
MIN_GRAMS = 5
WORD = re.compile(r"\w+")


def ruler():
    c = json.loads((H45 / "calibration.json").read_text())
    return {k: (v["a_per_item"], v["b_per_char"], v["e_per_other_event"]) for k, v in c.items()}


# ============================================================================ R1 / R2: tokens
def tokens_period(g: int, h45: pl.DataFrame, lab_of: dict, cal: dict) -> dict:
    t0 = time.time()
    days = B.days_of(g)
    load_days, blk = B.context_days(days)
    lt = B.ledger_calls(load_days, blk, extra=("n_ev", "cap_hit", "n_omitted"))
    lt = lt.join(h45, on="turn_id", how="left")
    lt = lt.with_columns(pl.col("agent").replace_strict(lab_of, default="other", return_dtype=pl.Utf8).alias("lab"))
    labs = lt["lab"].to_numpy()
    co = np.array([cal.get(x, cal["other_labs"]) for x in labs], float)
    lt = lt.with_columns(pl.Series("a_L", co[:, 0]), pl.Series("b_L", co[:, 1]), pl.Series("e_L", co[:, 2]))
    oev = (pl.col("n_ev").fill_null(0) - pl.col("k_new").fill_null(0)).clip(lower_bound=0)
    lt = lt.with_columns(
        (pl.col("a_L") * pl.col("k_new").fill_null(0) + pl.col("b_L") * pl.col("chars_new").fill_null(0)
         + pl.col("e_L") * oev).cum_sum().over("agent", "seg").alias("R"),
        pl.col("cap_hit").fill_null(False).cast(pl.Int32).cum_sum().over("agent").alias("cap_cum"))
    lt = lt.with_columns((pl.col("P") - pl.col("R")).alias("W"))
    base = (lt.filter(pl.col("P").is_not_null()).sort("agent", "seg", "seg_pos")
            .group_by("agent", "seg").agg(pl.col("W").first().alias("W0"), pl.col("seg_pos").first().alias("base_pos"),
                                          pl.col("W").last().alias("W_last"), pl.col("seg_pos").last().alias("last_pos")))
    base = base.with_columns(
        ((pl.col("W_last") - pl.col("W0")).clip(lower_bound=0) / 1000).log1p().alias("seg_dose"))
    st = pl.read_parquet(OUT / f"G{g:02d}" / "statements.parquet")
    assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    chk = st.select("turn_id", "call_idx", "seg").join(lt.select("turn_id", pl.col("call_idx").alias("ci2"),
                                                                   pl.col("seg").alias("seg2")), on="turn_id")
    assert chk.height == st.height and (chk["call_idx"] == chk["ci2"]).all() and (chk["seg"] == chk["seg2"]).all(), \
        "ledger_calls does not reproduce round-1 calls"
    x = st.select("sid", "agent", "turn_id", "seg", "o_seg", "own_chars_seg").join(
        lt.select("turn_id", "lab", "a_L", "b_L", "P", "R", "W", "cap_cum"), on="turn_id", how="left").join(
        base, on=["agent", "seg"], how="left")
    x = x.with_columns((pl.col("a_L") * pl.col("o_seg") + pl.col("b_L") * pl.col("own_chars_seg")).alias("C"))
    x = x.with_columns((pl.col("W") - pl.col("W0") - pl.col("C")).clip(lower_bound=0).alias("U"),
                       pl.col("lab").is_in(list(DENSE)).alias("dense"))
    x = x.select("sid", "lab", "dense", "P", "R", "W", "W0", "base_pos", "C", "U", "seg_dose", "last_pos", "cap_cum")
    x.write_parquet(OUT / f"G{g:02d}" / "r2_tokens.parquet", compression="zstd")
    info = dict(period=f"G{g:02d}", n=x.height, P_cov=float(x["P"].is_not_null().mean()),
                U_dense=int((x["dense"] & x["U"].is_not_null() & (x["base_pos"] == 0)).sum()),
                U_all=int((x["U"].is_not_null() & (x["base_pos"] <= 2)).sum()),
                cap_calls=int(lt["cap_hit"].fill_null(False).sum()), secs=round(time.time() - t0, 1))
    return info


def run_tokens():
    h45 = pl.read_parquet(H45 / "calls.parquet", columns=["turn_id", "P", "holdout"]).filter(~pl.col("holdout")).drop(
        "holdout")
    ro = pl.read_parquet(SH / "roster.parquet", columns=["agent", "lab"])
    lab_of = dict(zip(ro["agent"].to_list(), ro["lab"].cast(pl.Utf8).to_list()))
    cal = ruler()
    infos = [tokens_period(g, h45, lab_of, cal) for g in PERIODS]
    for i in infos:
        print(i, flush=True)
    (OUT / "r2_tokens_build.json").write_text(json.dumps(infos, indent=1))


# ============================================================================ R3: memory containment
def grams(text: str) -> set:
    w = WORD.findall((text or "").lower())
    return {hash((w[i], w[i + 1], w[i + 2])) for i in range(len(w) - 2)}


def run_memory():
    t0 = time.time()
    m = json.loads((SH / "statement_flags_meta.json").read_text())
    tb, tg = m["thr_bge"], m["thr_gte_rate_matched"]
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("crow").select("crow", "message_id")
    stm = pl.read_parquet(ED / "statements.parquet", columns=["src_row"]).with_row_index("srow")
    ms = pl.read_parquet(SH / "memory_stats.parquet", columns=["t", "agent", "lines_added", "lines_removed"])
    ms = ms.sort("agent", "t").with_row_index("snap")
    reqs = []  # per period: pair frame with snapshot keys
    for g in PERIODS:
        p = OUT / f"G{g:02d}"
        st = pl.read_parquet(p / "statements.parquet", columns=["sid", "srow", "agent", "t", "turn_id", "pt_date",
                                                                "goal_no"])
        assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
        cw = pl.scan_parquet(SH / "call_windows.parquet").filter(
            pl.col("turn_id").is_in(st["turn_id"].implode())).select("turn_id", "t_call").collect()
        st = st.join(cw, on="turn_id", how="left")
        pr = pl.read_parquet(p / "pairs.parquet").with_columns(
            ((pl.col("cos_bge") > tb) | (pl.col("cos_gte") > tg)).alias("y"))
        prior = (pr.filter(pl.col("in_seg") & pl.col("y")).group_by("sid_u").agg(pl.len().alias("prior_copies")))
        e = pr.filter(~pl.col("in_seg")).select("sid", "sid_u")
        e = e.join(st.select("sid", "agent", "t_call"), on="sid").join(
            st.select(pl.col("sid").alias("sid_u"), pl.col("srow").alias("srow_u"), pl.col("t").alias("t_u")),
            on="sid_u")
        e = e.join(prior, on="sid_u", how="left").with_columns(pl.col("prior_copies").fill_null(0))
        # latest snapshot before t_call (M_t) and before t_u (M_u), same agent
        e = e.sort("t_call").join_asof(ms.sort("t").select("agent", pl.col("t").alias("t_call"), pl.col("snap").alias("snap_t")),
                                       on="t_call", by="agent", strategy="backward", allow_exact_matches=False)
        e = e.sort("t_u").join_asof(ms.sort("t").select("agent", pl.col("t").alias("t_u"), pl.col("snap").alias("snap_u")),
                                    on="t_u", by="agent", strategy="backward", allow_exact_matches=False)
        # memory writes between u and t (append rows: lines_removed == 0 or null; Known issue)
        e = e.with_columns(pl.lit(g).alias("g"))
        reqs.append(e)
    E = pl.concat(reqs)
    # lines added by consolidations strictly between u and t (cumulative over append rows)
    ms2 = ms.with_columns(pl.when(pl.col("lines_removed").fill_null(0) == 0).then(pl.col("lines_added").fill_null(0))
                          .otherwise(0).cum_sum().over("agent").alias("cum_add"))
    cum = dict(zip(ms2["snap"].to_list(), ms2["cum_add"].to_list()))
    E = E.with_columns(
        (pl.col("snap_t").replace_strict(cum, default=None, return_dtype=pl.Int64)
         - pl.col("snap_u").replace_strict(cum, default=None, return_dtype=pl.Int64)).alias("lines_added_between"),
        (pl.col("snap_t") != pl.col("snap_u")).alias("mem_changed"))
    # texts of the sources (chat text, in memory only)
    srcs = E.select("srow_u").unique().join(stm, left_on="srow_u", right_on="srow").join(
        ci, left_on="src_row", right_on="crow")
    txt = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).join(
        srcs.select("srow_u", "message_id"), on="message_id")
    G = {int(r): grams(t) for r, t in zip(txt["srow_u"].to_list(), txt["text"].to_list())}
    del txt
    n3 = {k: len(v) for k, v in G.items()}
    # needed snapshots: snap -> list of (row index, which)
    rows_t = E["snap_t"].to_list()
    rows_u = E["snap_u"].to_list()
    src = E["srow_u"].to_list()
    need: dict[int, list] = {}
    for i, (a, b) in enumerate(zip(rows_t, rows_u)):
        if a is not None:
            need.setdefault(int(a), []).append((i, 0))
        if b is not None:
            need.setdefault(int(b), []).append((i, 1))
    key = {(int(a), t.replace(tzinfo=None)): int(s) for a, t, s in zip(ms["agent"].to_list(), ms["t"].to_list(),
                                                                      ms["snap"].to_list())}
    ro = pl.read_parquet(SH / "roster.parquet", columns=["agent", "agent_id"])
    code = dict(zip(ro["agent_id"].to_list(), ro["agent"].to_list()))
    need_agents = set(int(a) for a in E["agent"].unique().to_list())
    c_t = np.full(E.height, np.nan, np.float32)
    c_u = np.full(E.height, np.nan, np.float32)
    seen = 0
    pat_a = re.compile(rb'"agent_id":\s*"([^"]+)"')
    pat_c = re.compile(rb'"created_at":\s*"([^"]+)"')
    with gzip.open(RAW / "agent_memories.jsonl.gz", "rb") as f:
        for line in f:
            ma, mc = pat_a.search(line), pat_c.search(line)
            if not ma or not mc:
                continue
            a = code.get(ma.group(1).decode())
            if a is None or a not in need_agents:
                continue
            tt = dt.datetime.fromisoformat(mc.group(1).decode().replace("Z", ""))
            s = key.get((int(a), tt))
            if s is None or s not in need:
                continue
            seen += 1
            M = grams(orjson.loads(line).get("content") or "")
            for i, which in need[s]:
                gu = G.get(int(src[i]))
                if not gu or len(gu) < MIN_GRAMS:
                    continue
                v = len(gu & M) / len(gu)
                if which == 0:
                    c_t[i] = v
                else:
                    c_u[i] = v
    E = E.with_columns(pl.Series("c_t", c_t), pl.Series("c_u", c_u),
                       pl.col("srow_u").replace_strict(n3, default=0, return_dtype=pl.Int32).alias("n3_u"))
    info = dict(snapshots_needed=len(need), snapshots_found=seen, secs=round(time.time() - t0, 1))
    for g in PERIODS:
        o = E.filter(pl.col("g") == g).select("sid", "sid_u", "prior_copies", "snap_t", "snap_u", "mem_changed",
                                              "lines_added_between", "n3_u", "c_t", "c_u")
        o.write_parquet(OUT / f"G{g:02d}" / "r2_memory.parquet", compression="zstd")
        info[f"G{g:02d}"] = dict(pairs=o.height, c_t_defined=int(o["c_t"].is_not_nan().sum()))
    print(info, flush=True)
    (OUT / "r2_memory_build.json").write_text(json.dumps(info, indent=1))


def provenance(which: str):
    pth = OUT / "_provenance_r2.json"
    prov = json.loads(pth.read_text()) if pth.exists() else {}
    prov[which] = {"built_by": "hypotheses/H69-loops-context-fixed-points/scheme/build_r2.py", "git_commit": git_commit(),
                   "inputs": [{"source": "ai-village", "revision": REVISION,
                               "tables": (["H45 calls.parquet (P)", "H45 calibration.json", "shared/context_ledger_turns",
                                           "shared/roster"] if which == "tokens" else
                                          ["raw agent_memories (text read in memory only)", "shared/memory_stats",
                                           "shared/chat_text (in memory only)", "shared/call_windows",
                                           "H69 round-1 pairs"])}],
                   "params": {"periods": PERIODS, "dense": sorted(DENSE), "min_grams": MIN_GRAMS,
                              "holdout": "excluded (round-1 frames; ledger holdout)"},
                   "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    pth.write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "tokens"
    if which == "tokens":
        run_tokens()
    else:
        run_memory()
    provenance(which)
