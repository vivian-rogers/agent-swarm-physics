"""H134 scheme: project visits (call), dwell d, the project self-share f_proj and its variants, reset flags and nuisance
terms, from the shared per-call project labels (infra/shared/project_calls.py) and the DQ1 context ledger.

Regime III, non-reserved rows only (project_calls `holdout` flag and common.holdout_mask, both asserted).
Visit (card, Data scheme): a run of an agent's calls with one carried label (E = 100). It starts at a hop or an arrival.
  It ends at the next hop (completed; that hop call is the visit's last risk row, y = 1), at label expiry, at the end of
  the carry block (goal period) or the agent's last call (right-censored).
Risk rows: the visit's calls with d >= 2 (d = own calls from the visit's first call, inclusive), plus the leaving hop call.
Segment: cut at reset_consol | reset_session (H69 rule) and at a goal-period change.
f_proj (amended ruler A1): f = n_a / (n_own + 1/2); n_a = own earlier calls in the segment that touched the visit's
  project (any strict touch, `project_call_touches`), n_own = own earlier calls in the segment.
Variants: f_lab (denominator: own earlier calls in the segment that touched any project), f_rec (last 10 own calls in
  the segment), f_entry ((n_a + k_a) / (n_own + k + 1/2); k = `k_ctx` room items in context, k_a = items read in the
  segment so far that link the project via `project_mentions_chat`).
Kick: N^nam_other(c) = agent messages read at c (ledger items, not omitted) that name the reader (`ment`) and link a
  project other than the visit's.
Outputs (data/processed/H134-polya-urn-project-stickiness/): calls.parquet (risk rows), visits.parquet, counts.json,
  _provenance.json. Project names hashed. No text.
Usage: uv run python hypotheses/H134-polya-urn-project-stickiness/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H134-polya-urn-project-stickiness"
REC = 10
D_RESET = 10


def h8(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()[:10]


def load() -> pl.DataFrame:
    c = (pl.scan_parquet(SH / "project_calls.parquet")
         .filter(pl.col("regime") == "III", ~pl.col("holdout"))
         .select("turn_id", "agent", "pt_date", "goal_no", "unit_id", "holdout", "t_call", "t_first", "kind",
                 "proj", "label", "prev_label", "hop", "arrive").collect())
    hm = np.array(holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list()))
    assert not hm.any() and not c["holdout"].any(), "reserved rows"
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("regime") == "III", ~pl.col("holdout"))
          .select("turn_id", "reset_consol", "reset_forced", "reset_session", "first_of_day", "k_ctx", "n_human").collect())
    c = c.join(lt, on="turn_id", how="left")
    assert c["reset_consol"].null_count() == 0
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start")
    c = c.join(cal, on="pt_date", how="left").sort("agent", "t_first", "turn_id")
    k = pl.col("kind").cast(pl.Utf8)
    c = c.with_columns(
        hbin=((pl.col("t_call") - pl.col("win_start")).dt.total_seconds() / 3600).floor().clip(0, 6).cast(pl.Int8),
        kcode=pl.when(k == "cu_action").then(0).when(k == "talk").then(1).when(k.is_in(["pause", "wait"])).then(2)
        .when(k.is_in(["consolidate", "session_start", "session_stop"])).then(3).otherwise(4).cast(pl.Int8),
        forced=pl.col("reset_forced"), vol=pl.col("reset_consol") & ~pl.col("reset_forced"), sess=pl.col("reset_session"),
        fod=pl.col("first_of_day").fill_null(False))
    newblk = (pl.col("agent") != pl.col("agent").shift(1)) | (pl.col("goal_no") != pl.col("goal_no").shift(1))
    c = c.with_columns(prev_k=pl.col("kcode").shift(1).over("agent").fill_null(4),
                       blk=newblk.fill_null(True).cast(pl.Int32).cum_sum())
    c = c.with_columns(seg=(pl.col("reset_consol") | pl.col("reset_session") | (pl.col("blk") != pl.col("blk").shift(1)))
                       .fill_null(True).cast(pl.Int32).cum_sum())
    # kickoff window: first 4 active hours of the goal period's first day
    g0 = c.group_by("goal_no").agg(pl.col("win_start").min().alias("g_start"))
    c = c.join(g0, on="goal_no", how="left").with_columns(
        kick4=(pl.col("t_call") - pl.col("g_start")).dt.total_seconds() < 4 * 3600)
    return c.drop("win_start", "g_start")


def reads(c: pl.DataFrame) -> pl.DataFrame:
    """Per (turn_id, project): agent messages read at the call that link the project; n_nam = those naming the reader."""
    pm = pl.read_parquet(SH / "project_mentions_chat.parquet").select("message_id", "project").unique()
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .filter(pl.col("kind") == "agent", ~pl.col("omitted"))
          .select("turn_id", "message_id", "ment").collect())
    it = it.join(c.select("turn_id"), on="turn_id", how="semi").join(pm, on="message_id", how="inner")
    return it.group_by("turn_id", "project").agg(n_all=pl.len(), n_nam=pl.col("ment").sum())


def main():
    c = load()
    tch = pl.read_parquet(SH / "project_call_touches.parquet").filter(~pl.col("holdout")).select("turn_id", "project")
    projs = sorted(set(tch["project"].to_list()) | set(c["label"].drop_nulls().to_list()))
    pcode = {p: i for i, p in enumerate(projs)}
    tch = tch.join(c.select("turn_id"), on="turn_id", how="semi").with_columns(
        pc=pl.col("project").replace_strict(pcode, return_dtype=pl.Int32))
    tl = tch.group_by("turn_id").agg(pl.col("pc"))
    c = c.join(tl, on="turn_id", how="left").sort("agent", "t_first", "turn_id")
    rd = reads(c).with_columns(pc=pl.col("project").replace_strict(pcode, default=-1, return_dtype=pl.Int32))
    rdl = rd.group_by("turn_id").agg(pl.col("pc").alias("rpc"), pl.col("n_all"), pl.col("n_nam"))
    c = c.join(rdl, on="turn_id", how="left").sort("agent", "t_first", "turn_id")
    # pseudo-reset placebo (O4): the call 20 own calls before a forced reset, same carry block
    c = c.with_columns(pseudo=pl.col("forced").shift(-20).over("blk").fill_null(False) & ~pl.col("forced"))

    n = c.height
    lab = c["label"].to_list()
    hop = c["hop"].fill_null(False).to_numpy()
    arr = c["arrive"].fill_null(False).to_numpy()
    blk = c["blk"].to_numpy(); seg = c["seg"].to_numpy()
    touches = [x if x is not None else [] for x in c["pc"].to_list()]
    rpc = c["rpc"].to_list(); rall = c["n_all"].to_list(); rnam = c["n_nam"].to_list()
    kctx = c["k_ctx"].fill_null(0).to_numpy()
    labc = np.array([pcode[x] if x is not None else -1 for x in lab])

    # visits and risk rows: one pass
    vis_rows = []          # (call index, visit, d, y)
    visits = []            # [visit, agent idx row of arrival, project code, completed]
    v = -1; d = 0; cur = -1
    for i in range(n):
        newb = i == 0 or blk[i] != blk[i - 1]
        if newb and cur >= 0:
            cur = -1
        if hop[i] and cur >= 0:
            d += 1
            vis_rows.append((i, v, d, 1)); visits[v][3] = 1
            cur = -1
        if labc[i] < 0:
            cur = -1
            continue
        if hop[i] or arr[i] or cur < 0 or labc[i] != cur:
            assert hop[i] or arr[i] or newb or cur < 0, i
            v += 1; d = 1; cur = labc[i]
            visits.append([v, i, cur, 0])
            vis_rows.append((i, v, d, 0))
            continue
        d += 1
        vis_rows.append((i, v, d, 0))
    vr = np.array(vis_rows)
    risk = vr[vr[:, 2] >= 2]
    # one risk row per call at most
    assert len(np.unique(risk[:, 0])) == len(risk)
    vproj = np.array([x[2] for x in visits])
    cur_at = np.full(n, -1); vis_at = np.full(n, -1)
    cur_at[risk[:, 0]] = vproj[risk[:, 1]]; vis_at[risk[:, 0]] = risk[:, 1]
    # visit touches before c (ntv): touches of the visit's project at the visit's rows, cumulative, exclusive
    allr = vr[np.lexsort((vr[:, 2], vr[:, 1]))]
    tch_a = np.array([1 if vproj[vv] in touches[ii] else 0 for ii, vv, _, _ in allr])
    vstart = np.r_[True, allr[1:, 1] != allr[:-1, 1]]
    cs = np.cumsum(tch_a)
    base = np.maximum.accumulate(np.where(vstart, np.arange(len(allr)), 0))
    ntv_all = cs - tch_a - (cs[base] - tch_a[base])
    ntv_map = {(ii, vv): nt for (ii, vv, _, _), nt in zip(allr.tolist(), ntv_all.tolist())}

    # segment composition (one pass)
    keys = ("n_a", "n_own", "n_lab", "n_a_pre", "n_own_pre", "rec_a", "rec_n", "k_a", "kick_nam", "kick_all", "nam_cur")
    o = {k: np.zeros(n) for k in keys}
    seg_cnt: dict = {}; read_cnt: dict = {}
    seg_own = seg_lab = 0
    prev_cnt: dict = {}; prev_own = 0
    hist: list = []
    for i in range(n):
        if i == 0 or seg[i] != seg[i - 1]:
            newb = i == 0 or blk[i] != blk[i - 1]
            prev_cnt, prev_own = ({}, 0) if newb else (seg_cnt, seg_own)
            seg_cnt, read_cnt, seg_own, seg_lab, hist = {}, {}, 0, 0, []
            isreset = not newb
        else:
            isreset = False
        a = cur_at[i]
        rp = rpc[i] or []
        if a >= 0:
            o["n_a"][i] = seg_cnt.get(a, 0); o["n_own"][i] = seg_own; o["n_lab"][i] = seg_lab
            o["n_a_pre"][i] = prev_cnt.get(a, 0) if isreset else o["n_a"][i]
            o["n_own_pre"][i] = prev_own if isreset else seg_own
            h = hist[-REC:]
            o["rec_n"][i] = len(h); o["rec_a"][i] = sum(1 for s in h if a in s)
            o["k_a"][i] = read_cnt.get(a, 0)
            for p, na, nn in zip(rp, rall[i] or [], rnam[i] or []):
                if p != a:
                    o["kick_nam"][i] += nn; o["kick_all"][i] += na
                else:
                    o["nam_cur"][i] += nn
        for p in touches[i]:
            seg_cnt[p] = seg_cnt.get(p, 0) + 1
        for p, na in zip(rp, rall[i] or []):
            read_cnt[p] = read_cnt.get(p, 0) + na
        seg_own += 1
        seg_lab += 1 if touches[i] else 0
        hist.append(set(touches[i]))

    idx = risk[:, 0]
    f = o["n_a"][idx] / (o["n_own"][idx] + 0.5)
    cols = c[idx].select("turn_id", "agent", "pt_date", "goal_no", "unit_id", "hbin", "prev_k", "forced", "vol", "sess",
                         "fod", "kick4", "n_human", "seg", "pseudo")
    out = cols.with_columns(
        visit=pl.Series(risk[:, 1].astype(np.int32)), d=pl.Series(risk[:, 2].astype(np.int32)),
        y=pl.Series(risk[:, 3].astype(np.int8)), risk=pl.lit(True),
        f=pl.Series(f.astype(np.float32)),
        f_pre=pl.Series((o["n_a_pre"][idx] / (o["n_own_pre"][idx] + 0.5)).astype(np.float32)),
        f_lab=pl.Series((o["n_a"][idx] / (o["n_lab"][idx] + 0.5)).astype(np.float32)),
        f_rec=pl.Series((o["rec_a"][idx] / (o["rec_n"][idx] + 0.5)).astype(np.float32)),
        f_entry=pl.Series(((o["n_a"][idx] + o["k_a"][idx]) / (o["n_own"][idx] + kctx[idx] + 0.5)).astype(np.float32)),
        n_a=pl.Series(o["n_a"][idx].astype(np.int16)), n_own=pl.Series(o["n_own"][idx].astype(np.int16)),
        ntv=pl.Series(np.array([ntv_map[(ii, vv)] for ii, vv in zip(idx.tolist(), risk[:, 1].tolist())], np.int32)),
        kick_nam=pl.Series(o["kick_nam"][idx].astype(np.int16)), kick_all=pl.Series(o["kick_all"][idx].astype(np.int16)),
        nam_cur=pl.Series(o["nam_cur"][idx].astype(np.int16)),
        human=pl.col("n_human").fill_null(0) > 0,
    ).drop("n_human")
    vt = pl.DataFrame({"visit": np.array([x[0] for x in visits], np.int32),
                       "arr_turn": c["turn_id"].to_numpy()[[x[1] for x in visits]],
                       "agent": c["agent"].to_numpy()[[x[1] for x in visits]],
                       "unit_arr": c["unit_id"].gather([x[1] for x in visits]),
                       "project": [h8(projs[x[2]]) for x in visits],
                       "completed": np.array([x[3] for x in visits], np.int8)})
    dmax = out.group_by("visit").agg(pl.col("d").max().alias("d_last"))
    vt = vt.join(dmax, on="visit", how="left")
    OUT.mkdir(parents=True, exist_ok=True)
    out.write_parquet(OUT / "calls.parquet", compression="zstd")
    vt.write_parquet(OUT / "visits.parquet", compression="zstd")
    # structural counts per unit (no outcome statistic): visits with a risk row in the unit, completed in the unit,
    # forced resets inside visits with d >= 10
    cnt = (out.group_by("unit_id").agg(
        n_rows=pl.len(), n_visits=pl.col("visit").n_unique(), n_completed=pl.col("y").sum(),
        n_reset10=(pl.col("forced") & (pl.col("d") >= D_RESET)).sum()).sort("unit_id"))
    cnt = cnt.with_columns(testable=(pl.col("n_visits") >= 100) & (pl.col("n_completed") >= 50),
                           reset_testable=pl.col("n_reset10") >= 50)
    (OUT / "counts.json").write_text(json.dumps(cnt.to_dicts(), indent=1))
    prov = {"built_by": "hypotheses/H134-polya-urn-project-stickiness/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["project_calls", "project_call_touches", "context_ledger_turns", "context_ledger_items",
                                   "project_mentions_chat", "calendar"]}],
            "params": {"E": 100, "rec": REC, "ruler": "A1 f = n_a/(n_own+1/2)", "regime": "III", "reserved": "dropped"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(cnt)
    print("rows", out.height, "visits", vt.height)


if __name__ == "__main__":
    main()
