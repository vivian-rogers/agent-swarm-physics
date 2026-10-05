"""H46 round 2 scheme: genre covariates, context position and function-word counts for every eligible message.

Population: the shared `style_messages` table (H46's fit population, values within one float32 ulp of round 1), rows with
holdout == False and holdout_mask == False, `main` agents only. Reserved rows are dropped before anything is read.

Per message (codes and numbers only; no text is written):
  genre     DQ2 reply parent (pair_set = cand, parent), parent speaker kind, parent-pair stance soft probabilities,
            max candidate p_reply; roster mentions (chat_mentions_clean); leading '@' (from the text, flag only);
            DQ3 behavior-state probabilities of the agent's 5-min window holding the message.
  context   ctx_mode, ctx_pos, k_ctx (from style_messages, H73's call match); regime-III segment id and the message's
            position in its segment (segments cut at reset_consol | reset_session, DQ1; first_of_day is not a reset);
            the kind of reset that opened the segment (forced / voluntary / session).
  words     n_tok (word tokens after removing URLs and backtick code) and counts of the closed-class words in FW.

Output: data/processed/H46-style-conserved-charge/r2/messages_r2.parquet (+ _provenance.json entry `r2`).
Usage: uv run python hypotheses/H46-style-conserved-charge/scheme/build_r2.py
"""
from __future__ import annotations
import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
import datetime as dt  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H46-style-conserved-charge/r2"

# Closed-class English words (articles, pronouns, prepositions, conjunctions, auxiliaries, modals, negation,
# quantifiers, wh-words, common function adverbs). Fixed 2026-10-04 before any round-2 statistic.
FW = """a an the this that these those
i me my mine myself we us our ours ourselves you your yours yourself he him his she her it its itself they them their
of in on at by for with about from to into onto over under after before between through during without within upon
against among around across along toward towards per via
and or but nor so yet if because while although though as than then whether unless until since
is are was were be been being am have has had having do does did doing will would can could should may might must shall
not no
all some any each every both more most much many few other such own same
what which who whom whose when where why how
also just only very now here there still even too again already quite rather perhaps""".split()
FW = list(dict.fromkeys(FW))
TOK = re.compile(r"[a-z]+(?:'[a-z]+)?")
URL = re.compile(r"https?://\S+|www\.\S+")
CODE = re.compile(r"```.*?```|`[^`]*`", re.S)
DQ3_P = ["p_plan_coordinate", "p_execute_task", "p_research_browse", "p_communicate_external", "p_debug_recover",
         "p_verify_report", "p_monitor_wait", "p_self_maintenance", "p_social", "p_meta", "p_idle",
         "p_addresses_participant", "p_blocked"]


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    d = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if d.strip() else "")


def base_messages() -> pl.DataFrame:
    m = pl.read_parquet(SH / "style_messages.parquet").filter(~pl.col("holdout") & pl.col("main"))
    hm = np.array(holdout_mask(m["pt_date"].to_list(), m["goal_no"].to_list()), bool)
    m = m.filter(pl.Series(~hm))
    assert not m["holdout"].any()
    return m.sort("agent", "t", "msg")


def genre(m: pl.DataFrame) -> pl.DataFrame:
    ids = m.select("message_id")
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet")
          .filter((pl.col("pair_set") == "cand") & ~pl.col("holdout"))
          .select("B_message_id", "parent", "p_reply", "a_kind", "p_supports", "p_opposes", "p_asks", "p_neutral")
          .collect())
    rp = rp.join(ids.rename({"message_id": "B_message_id"}), on="B_message_id", how="semi")
    pmax = rp.group_by("B_message_id").agg(pl.col("p_reply").max().alias("p_reply_max"))
    par = (rp.filter(pl.col("parent")).sort("p_reply", descending=True).unique("B_message_id", keep="first")
           .select("B_message_id", pl.lit(True).alias("is_reply"), pl.col("a_kind").alias("parent_kind"),
                   "p_supports", "p_opposes", "p_asks", "p_neutral"))
    g = (ids.join(pmax.rename({"B_message_id": "message_id"}), on="message_id", how="left")
         .join(par.rename({"B_message_id": "message_id"}), on="message_id", how="left"))
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet").join(ids, on="message_id", how="semi")
    men = men.select("message_id", pl.col("mentions_roster").list.len().alias("n_mention"))
    g = g.join(men, on="message_id", how="left")
    return g.with_columns(pl.col("is_reply").fill_null(False), pl.col("parent_kind").fill_null(-1).cast(pl.Int8),
                          pl.col("p_reply_max").fill_null(0.0),
                          *[pl.col(c).fill_null(0.0) for c in ("p_supports", "p_opposes", "p_asks", "p_neutral")],
                          pl.col("n_mention").fill_null(0).cast(pl.Int16))


def dq3(m: pl.DataFrame) -> pl.DataFrame:
    b = (pl.scan_parquet(SH / "behavior_states_v3.parquet").filter(~pl.col("holdout") & pl.col("labeled"))
         .select("agent", "t0", "t1", *DQ3_P).collect().sort("t0"))
    x = m.select("message_id", "agent", "t").sort("t")
    j = x.join_asof(b, left_on="t", right_on="t0", by="agent", strategy="backward")
    j = j.with_columns(pl.when(pl.col("t") < pl.col("t1")).then(pl.lit(True)).otherwise(pl.lit(False)).alias("dq3_ok"))
    return j.select("message_id", "dq3_ok", *[pl.when(pl.col("dq3_ok")).then(pl.col(c)).otherwise(None).alias(c)
                                              for c in DQ3_P])


def segments(m: pl.DataFrame) -> pl.DataFrame:
    """Regime III: segment index per agent (cut at consolidation t_log and session reset t_call) and position."""
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter((pl.col("regime") == "III") & ~pl.col("holdout"))
          .select("agent", "t_call", "t_log", "kind", "reset_consol", "reset_session", "prev_seg_len").collect())
    cons = ct.filter(pl.col("kind") == "consolidate").select(
        "agent", pl.col("t_log").alias("t_r"),
        pl.when(pl.col("prev_seg_len").is_in([41, 42])).then(pl.lit("forced")).otherwise(pl.lit("voluntary")).alias("rk"))
    sess = ct.filter(pl.col("reset_session") & ~pl.col("reset_consol")).select(
        "agent", pl.col("t_call").alias("t_r"), pl.lit("session").alias("rk"))
    resets = pl.concat([cons, sess]).sort("agent", "t_r")
    m3 = m.filter(pl.col("regime") == "III").select("message_id", "agent", "t", "self_repeat")
    ag = m3["agent"].to_numpy()
    tt = m3["t"].dt.epoch("us").to_numpy()
    seg = np.full(len(m3), -1, np.int32)
    rk = np.array(["none"] * len(m3), dtype=object)
    t_reset = np.full(len(m3), np.nan)
    for a in np.unique(ag):
        ix = np.where(ag == a)[0]
        r = resets.filter(pl.col("agent") == a)
        tr = r["t_r"].dt.epoch("us").to_numpy()
        kinds = r["rk"].to_numpy()
        k = np.searchsorted(tr, tt[ix], side="right")
        seg[ix] = k
        rk[ix] = np.where(k > 0, kinds[np.maximum(k - 1, 0)], "none")
        t_reset[ix] = np.where(k > 0, (tt[ix] - tr[np.maximum(k - 1, 0)]) / 1e6, np.nan)
    s = m3.with_columns(pl.Series("seg", seg), pl.Series("seg_open", rk.astype(str)),
                        pl.Series("s_since_reset", t_reset.astype(np.float32)))
    s = s.sort("agent", "t").with_columns(
        pl.int_range(1, pl.len() + 1).over("agent", "seg").cast(pl.Int16).alias("pos_all"),
        (~pl.col("self_repeat")).cast(pl.Int32).cum_sum().over("agent", "seg").cast(pl.Int16).alias("pos_elig"),
        pl.len().over("agent", "seg").cast(pl.Int16).alias("seg_n_all"),
        (~pl.col("self_repeat")).sum().over("agent", "seg").cast(pl.Int16).alias("seg_n_elig"))
    return s.select("message_id", "seg", "seg_open", "s_since_reset", "pos_all", "pos_elig", "seg_n_all", "seg_n_elig")


def words(m: pl.DataFrame) -> pl.DataFrame:
    tx = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).join(
        m.select("message_id"), on="message_id", how="semi")
    idx = {w: k for k, w in enumerate(FW)}
    C = np.zeros((tx.height, len(FW)), np.uint16)
    ntok = np.zeros(tx.height, np.int32)
    lead_at = np.zeros(tx.height, bool)
    for r, t in enumerate(tx["text"].to_list()):
        t = t or ""
        lead_at[r] = t.lstrip().startswith("@")
        s = CODE.sub(" ", URL.sub(" ", t)).lower()
        toks = TOK.findall(s)
        ntok[r] = len(toks)
        for w in toks:
            k = idx.get(w)
            if k is not None:
                C[r, k] += 1
    out = pl.DataFrame({"message_id": tx["message_id"], "n_tok": ntok, "lead_at": lead_at})
    return out.with_columns(*[pl.Series(f"w_{w}", C[:, k]) for k, w in enumerate(FW)])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m = base_messages()
    keep = ["message_id", "msg", "srow", "agent", "t", "pt_date", "goal_no", "unit_id", "unit2", "regime", "room",
            "self_repeat", "copy", "restate", "turn_id", "ctx_mode", "ctx_pos", "k_ctx", "has_code", "has_url"]
    keep += [c for c in m.columns if c.startswith("s_") or c.startswith("tc_")]
    out = m.select(keep)
    for f in (genre, dq3, segments, words):
        out = out.join(f(m), on="message_id", how="left")
        print(f.__name__, out.height, flush=True)
    out = out.with_columns(pl.col("ctx_mode").cast(pl.String))
    out.write_parquet(OUT / "messages_r2.parquet", compression="zstd")
    prov_p = ROOT / "data/processed/H46-style-conserved-charge/_provenance.json"
    prov = json.loads(prov_p.read_text())
    prov["r2"] = {"built_by": "hypotheses/H46-style-conserved-charge/scheme/build_r2.py", "git_commit": git_commit(),
                  "inputs": [{"source": "ai-village", "revision": prov.get("inputs", [{}])[0].get("revision"),
                              "tables": ["shared/style_messages", "shared/reply_pairs", "shared/chat_mentions_clean",
                                         "shared/behavior_states_v3", "shared/context_ledger_turns", "shared/chat_text"]}],
                  "params": {"function_words": FW, "dq3": DQ3_P, "segments": "reset_consol | reset_session (regime III)",
                             "population": "style_messages main & ~holdout & ~holdout_mask"},
                  "built_at": dt.datetime.now(dt.UTC).isoformat()}
    prov_p.write_text(json.dumps(prov, indent=1))
    print("rows", out.height, "cols", out.width)


if __name__ == "__main__":
    main()
