"""H131 scheme: replies between debaters (#12) and among #26 agents, with relation, phase, read-gated prize state and
post-read call index on the DQ1 context ledger. Codes only (no text).

Per reply (reply_stance_v2, labelled, A by an agent, A's author != B's author, non-holdout):
  goal, unit (debate id / 'runoff'), speaker j (b_agent), target i (a_agent), t_B, t_call_prod (producing call),
  y = disagree_validated_agent, p_disagree, s2_soft, R (rival), phase (pre/deb/post or open/settled),
  t_verdict, t_read (j's receiving call of the verdict message), clock (t_B >= t_verdict), read (t_call_prod >= t_read),
  inflight (clock & ~read), k (post-read call index: 1 + j's talk calls with t_read <= t_call < t_call_prod; null if
  not read), k_on (the same after j's read of the team-assignment 'pre' message; #12 only).
reads.parquet: unit x agent read delays of the verdict (and of the 'pre' message in #12).
Usage: uv run python hypotheses/H131-antagonism-off-one-readout/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
import visibility as V  # noqa: E402

S = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H131-antagonism-off-one-readout"
G26_RIVALS = (0, 6, 17)
G26_OPEN_DAY = "2026-01-05"
G26_SETTLED_END = dt.datetime(2026, 1, 9, 18, 45, tzinfo=dt.timezone.utc)
UTC = dt.timezone.utc


def mid(ref):
    return ref.replace("chat_core:message_id=", "")


def talk_calls():
    cw = (pl.scan_parquet(S / "call_windows.parquet").filter(pl.col("talk") & pl.col("goal_no").is_in([12, 26]))
          .select("agent", "t_call").collect().sort("agent", "t_call"))
    return {int(a): g["t_call"].dt.epoch("us").to_numpy() for (a,), g in cw.group_by(["agent"], maintain_order=True)}


def k_index(agent, t_read_us, t_prod_us, tc):
    """1 + number of the agent's talk calls with t_read <= t_call < t_prod."""
    out = np.full(len(agent), -1, np.int64)
    for n, (a, tr, tp) in enumerate(zip(agent, t_read_us, t_prod_us)):
        if tr < 0 or tp < tr:
            continue
        c = tc.get(int(a))
        if c is None:
            out[n] = 1
            continue
        out[n] = 1 + int(np.searchsorted(c, tp, "left") - np.searchsorted(c, tr, "left"))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rs = pl.read_parquet(S / "reply_stance_v2.parquet").filter(
        pl.col("labelled") & (pl.col("a_kind") == 0) & pl.col("goal_no").is_in([12, 26]) & ~pl.col("holdout")
        & (pl.col("a_agent") != pl.col("b_agent")))
    ho = holdout_mask(rs["pt_date"].to_list(), rs["goal_no"].to_list())
    rs = rs.filter(~pl.Series(ho))
    pc = pl.read_parquet(S / "producing_calls.parquet").select(pl.col("message_id").alias("B_message_id"),
                                                               pl.col("t").alias("tB"), "t_call_prod", "prod_fallback")
    rs = rs.join(pc, on="B_message_id", how="left").select(
        "B_message_id", "goal_no", "pt_date", pl.col("b_agent").alias("j"), pl.col("a_agent").alias("i"), "tB",
        "t_call_prod", "prod_fallback", pl.col("disagree_validated_agent").cast(pl.Int8).alias("y"), "p_disagree",
        "s2_soft")
    gt = pl.read_parquet(S / "ground_truth_labels.parquet").filter(pl.col("preferred") & ~pl.col("holdout"))
    tc = talk_calls()
    rows, reads = [], []
    # ------------------------------------------------------------------------------------------------ #12
    g12 = gt.filter(pl.col("goal_no") == 12)
    for d in sorted(g12.filter(pl.col("label_kind") == "debate_result")["unit"].to_list()):
        gd = g12.filter(pl.col("unit") == d)
        team = gd.filter(pl.col("label_kind") == "team")
        side = {int(a): v for a, v in zip(team["agent"], team["value"]) if v in ("gov", "opp")}
        t0, t1 = team["t_valid_from"].min(), team["t_valid_to"].max()
        ph = gd.filter(pl.col("label_kind") == "phase").sort("t_valid_from")
        res = gd.filter(pl.col("label_kind") == "debate_result").row(0, named=True)
        v_mid, t_v = mid(res["source_ref"]), res["t_valid_from"]
        pre = ph.filter(pl.col("value") == "pre").row(0, named=True)
        on_mid, t_on = mid(pre["source_ref"]), pre["t_valid_from"]
        rc = V.receipts([v_mid, on_mid])
        rv = {int(a): t for m, a, t in zip(rc["message_id"], rc["recipient"], rc["t_call"]) if m == v_mid}
        ro = {int(a): t for m, a, t in zip(rc["message_id"], rc["recipient"], rc["t_call"]) if m == on_mid}
        for a in side:
            reads.append(dict(goal_no=12, unit=d, agent=a, team=side[a],
                              read_delay_s=(rv[a] - t_v).total_seconds() if a in rv else None,
                              read_on_delay_s=(ro[a] - t_on).total_seconds() if a in ro else None))
        sub = rs.filter((pl.col("goal_no") == 12) & (pl.col("tB") >= t0) & (pl.col("tB") < t1)
                        & pl.col("j").is_in(list(side)) & pl.col("i").is_in(list(side)))
        if sub.height == 0:
            continue
        phase = []
        for tb in sub["tB"].to_list():
            lab = None
            for r in ph.iter_rows(named=True):
                if r["t_valid_from"] <= tb < r["t_valid_to"]:
                    lab = r["value"]
            phase.append(lab)
        sub = sub.with_columns(
            pl.lit("12").alias("period"), pl.lit(d).alias("unit"), pl.Series("phase", phase, dtype=pl.String),
            pl.Series("R", [int(side[int(a)] != side[int(b)]) for a, b in zip(sub["j"], sub["i"])], dtype=pl.Int8),
            pl.lit(t_v).alias("t_verdict"), pl.lit(t_on).alias("t_on"),
            pl.col("j").replace_strict(rv, default=None, return_dtype=pl.Datetime("us", "UTC")).alias("t_read"),
            pl.col("j").replace_strict(ro, default=None, return_dtype=pl.Datetime("us", "UTC")).alias("t_read_on"))
        rows.append(sub)
    # ------------------------------------------------------------------------------------------------ #26
    g26 = gt.filter((pl.col("goal_no") == 26) & (pl.col("label_kind") == "phase") & (pl.col("unit") == "round1")
                    & (pl.col("value") == "result")).row(0, named=True)
    v_mid, t_v = mid(g26["source_ref"]), g26["t_valid_from"]
    cc = pl.read_parquet(S / "chat_core.parquet").filter((pl.col("goal_no") == 26) & (pl.col("pt_date") == G26_OPEN_DAY)
                                                        & (pl.col("speaker_kind") == "agent"))
    t_open = cc["t"].min()
    rc = V.receipts([v_mid])
    rv = {int(a): t for a, t in zip(rc["recipient"], rc["t_call"])}
    for a, t in rv.items():
        reads.append(dict(goal_no=26, unit="runoff", agent=a, team="rival" if a in G26_RIVALS else "other",
                          read_delay_s=(t - t_v).total_seconds(), read_on_delay_s=None))
    sub = rs.filter((pl.col("goal_no") == 26) & (pl.col("tB") >= t_open) & (pl.col("tB") < G26_SETTLED_END))
    sub = sub.with_columns(
        pl.lit("26").alias("period"), pl.lit("runoff").alias("unit"),
        pl.when(pl.col("tB") < t_v).then(pl.lit("open")).otherwise(pl.lit("settled")).alias("phase"),
        (pl.col("j").is_in(list(G26_RIVALS)) & pl.col("i").is_in(list(G26_RIVALS))).cast(pl.Int8).alias("R"),
        pl.lit(t_v).alias("t_verdict"), pl.lit(None, dtype=pl.Datetime("us", "UTC")).alias("t_on"),
        pl.col("j").replace_strict(rv, default=None, return_dtype=pl.Datetime("us", "UTC")).alias("t_read"),
        pl.lit(None, dtype=pl.Datetime("us", "UTC")).alias("t_read_on"))
    rows.append(sub)
    df = pl.concat(rows, how="diagonal_relaxed")
    us = lambda c: pl.col(c).dt.epoch("us")  # noqa: E731
    df = df.with_columns((pl.col("tB") >= pl.col("t_verdict")).alias("clock"),
                         (pl.col("t_read").is_not_null() & (pl.col("t_call_prod") >= pl.col("t_read"))).alias("read"))
    df = df.with_columns((pl.col("clock") & ~pl.col("read")).alias("inflight"))
    k = k_index(df["j"].to_numpy(), df.select(us("t_read").fill_null(-1))["t_read"].to_numpy(),
                df.select(us("t_call_prod").fill_null(-1))["t_call_prod"].to_numpy(), tc)
    kon = k_index(df["j"].to_numpy(), df.select(us("t_read_on").fill_null(-1))["t_read_on"].to_numpy(),
                  df.select(us("t_call_prod").fill_null(-1))["t_call_prod"].to_numpy(), tc)
    df = df.with_columns(pl.Series("k", k, dtype=pl.Int32), pl.Series("k_on", kon, dtype=pl.Int32))
    df = df.with_columns(pl.when(pl.col("k") > 0).then(pl.col("k")).alias("k"),
                         pl.when(pl.col("k_on") > 0).then(pl.col("k_on")).alias("k_on"))
    df.write_parquet(OUT / "replies.parquet", compression="zstd")
    pl.DataFrame(reads).write_parquet(OUT / "reads.parquet")
    prov = {"built_by": "hypotheses/H131-antagonism-off-one-readout/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/reply_stance_v2", "shared/producing_calls", "shared/ground_truth_labels",
                                   "shared/context_ledger_items", "shared/call_windows", "shared/chat_core"]}],
            "params": {"g26_rivals": list(G26_RIVALS), "g26_settled_end": G26_SETTLED_END.isoformat(),
                       "outcome": "disagree_validated_agent", "read_rule": "visibility.receipts; t_call_prod >= t_read"},
            "built_at": dt.datetime.now(UTC).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    # structural counts only (no outcome)
    print(df.group_by("period", "R", "clock", "read").len().sort("period", "R", "clock", "read"))
    print(df.group_by("period", "phase").len().sort("period", "phase"))


if __name__ == "__main__":
    main()
