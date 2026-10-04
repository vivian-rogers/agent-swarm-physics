"""H81 round 2 scheme: inputs for R1 (record carrier), R2 (exogenous-drift probe) and R4 (H82 link). No text is written;
held-out rows are dropped (common.holdout_mask) and asserted. Base panel: the shared culture_vectors tables
(infra/shared/culture_vectors.py), identical to round 1's.

Outputs (data/processed/H81-culture-beyond-composition/round2/):
  r1_sets.parquet        one row per (regime, agent, block): artifact-id lists R (ledger read), U_ledger (posted but never
                         read in the block), U_act (used by block-mates in actions/intentions, never posted to a chat
                         item the agent read, never touched by it); long-lived = first non-holdout appearance >= 14 d
                         before the block's first day; repo/site/file only
  r1_record_rows.parquet one row per (artifact, agentdays row): eligible agent-days on which the artifact was mentioned
                         (chat, intention or action; how in url/output/bare)
  outside_flags.parquet  statements row -> outside-marker flag (agent chat + intentions, non-holdout); counts only
  human_pcs_<model>.npz  per (goal, regime): top-3 principal directions of the goal's human messages (whitened 32-d)
  clocks.parquet         per non-holdout calendar date: cumulative documented hours (schedule metadata)
  boundaries.parquet     H82's boundary rule rebuilt from the shared panel (P-1 -> P, same regime, first 5 days of P)
  _provenance.json
Usage: uv run python hypotheses/H81-culture-beyond-composition/scheme/build_r2.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra" / "shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
from embed_models import load_whitener, MODELS  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
CV = SH / "culture_vectors"
OUT = ROOT / "data/processed/H81-culture-beyond-composition/round2"
AGE_LONG = 14          # days: long-lived artifact
STRICT = ["url", "output", "bare"]
KINDS = ["repo", "site", "file"]
PT = "America/Los_Angeles"

# R2b outside-topic markers (pre-registered list; model names excluded: agents carry them as names)
_MONTH = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
OUTSIDE = re.compile("|".join([
    rf"\b{_MONTH}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?\b",            # explicit calendar dates
    r"\b\d{1,2}(?:st|nd|rd|th)?\s+of\s+" + _MONTH + r"\b",
    r"\b202[4-7]-\d{2}-\d{2}\b", r"\b202[4-7]\b",                  # ISO dates, years
    r"\b(?:halloween|thanksgiving|christmas|hanukkah|new year'?s?|valentine'?s?|black friday|cyber monday|"
    r"memorial day|independence day|fourth of july|labor day|easter|diwali|ramadan)\b",
    r"\b(?:news|headlines?|announced|announcement|press release|released|launch(?:ed|es)?|election|"
    r"stock market|breaking)\b",
    r"\b(?:openai|anthropic|deepmind|xai|meta ai|mistral|deepseek|nvidia|microsoft)\b",
]), re.IGNORECASE)


def pt_date(col: str) -> pl.Expr:
    return pl.col(col).dt.convert_time_zone(PT).dt.strftime("%Y-%m-%d")


def load_panel():
    ad = pl.read_parquet(CV / "agentdays.parquet").with_row_index("row")
    blocks = pl.read_parquet(CV / "blocks.parquet")
    hm = np.array(holdout_mask(ad["pt_date"].to_list(), ad["goal_no"].to_list()))
    assert not hm.any() and not ad["holdout"].any()
    return ad, blocks


def block_days(ad: pl.DataFrame) -> pl.DataFrame:
    """(block, goal_no, pt_date): every PT date of the block's goal and week (from the calendar, non-holdout)."""
    b = ad.select("block", "goal_no", "regime", "week").unique()
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no", "holdout"]).filter(~pl.col("holdout"))
    d = cal["pt_date"].str.to_date()
    cal = cal.with_columns((d.dt.iso_year().cast(pl.Int32) * 100 + d.dt.week().cast(pl.Int32)).alias("week"))
    hm = np.array(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    cal = cal.filter(~pl.Series(hm))
    return b.join(cal.select("pt_date", "goal_no", "week"), on=["goal_no", "week"], how="inner")


def mentions() -> pl.DataFrame:
    """Non-holdout strict mentions of repo/site/file artifacts with PT date; first non-holdout appearance per artifact."""
    am = pl.read_parquet(SH / "artifact_mentions.parquet")
    a = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind"])
    am = am.join(a, on="artifact").filter(pl.col("kind").cast(pl.Utf8).is_in(KINDS)
                                          & pl.col("how").cast(pl.Utf8).is_in(STRICT))
    am = am.with_columns(pt_date("t").alias("pt_date"))
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    am = am.join(cal, on="pt_date", how="left")
    hm = np.array(holdout_mask(am["pt_date"].to_list(), am["goal_no"].fill_null(-1).to_list()))
    am = am.filter(~pl.Series(hm))
    first = am.group_by("artifact").agg(pl.col("pt_date").min().alias("first_nh"))
    return am.join(first, on="artifact").with_columns(pl.col("source").cast(pl.Utf8))


def build_r1(ad: pl.DataFrame, blocks: pl.DataFrame):
    am = mentions()
    bd = block_days(ad)
    bfirst = blocks.select("block", pl.col("first_day").str.to_date().alias("b_first"))
    # ledger reads of chat messages that name an artifact
    chat_m = am.filter(pl.col("source") == "chat").select("artifact", "message_id", "first_nh").drop_nulls("message_id").unique()
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id", "sender") \
        .filter(pl.col("message_id").is_in(chat_m["message_id"].unique().implode())).collect()
    cw = pl.scan_parquet(SH / "call_windows.parquet").select("turn_id", "agent", "pt_date", "goal_no", "holdout").collect()
    it = it.join(cw, on="turn_id").filter(~pl.col("holdout"))
    hm = np.array(holdout_mask(it["pt_date"].to_list(), it["goal_no"].to_list()))
    it = it.filter(~pl.Series(hm))
    # reads in block: receiving call on one of the block's dates (and of the block's goal)
    rd = it.join(bd, on=["pt_date", "goal_no"]).join(chat_m, on="message_id")
    rd = rd.filter(pl.col("sender").is_null() | (pl.col("sender") != pl.col("agent")))
    members = ad.select("agent", "block", "regime").unique()
    rd = rd.join(members.select("agent", "block"), on=["agent", "block"])
    read_all = rd.group_by("agent", "block").agg(pl.col("artifact").unique().alias("read_all"),
                                                 pl.col("message_id").unique().alias("read_msgs"))
    # chat messages posted on the block's dates (any room), naming artifacts
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date", "goal_no", "agent"]) \
        .rename({"agent": "spk"})
    posted = chat_m.join(cc, on="message_id").join(bd, on=["pt_date", "goal_no"])
    # agent's own touches in the block (any source)
    own = am.filter(pl.col("agent").is_not_null()).join(bd, on=["pt_date", "goal_no"]) \
        .group_by("agent", "block").agg(pl.col("artifact").unique().alias("own"))
    # block-mates' action/intention touches
    act = am.filter(pl.col("source").is_in(["action", "intention"]) & pl.col("agent").is_not_null()) \
        .join(bd, on=["pt_date", "goal_no"]).select("block", pl.col("agent").alias("j"), "artifact").unique()
    first = am.select("artifact", "first_nh").unique()
    rows = []
    mem = members.join(bfirst, on="block").join(read_all, on=["agent", "block"], how="left") \
        .join(own, on=["agent", "block"], how="left")
    posted_by_block = {k[0]: v for k, v in posted.partition_by("block", as_dict=True).items()}
    act_by_block = {k[0]: v for k, v in act.partition_by("block", as_dict=True).items()}
    fmap = dict(zip(first["artifact"].to_list(), [dt.date.fromisoformat(x) for x in first["first_nh"].to_list()]))
    for r in mem.iter_rows(named=True):
        i, b, bf = r["agent"], r["block"], r["b_first"]
        long_ok = lambda x: fmap.get(x) is not None and (bf - fmap[x]).days >= AGE_LONG  # noqa: E731
        read_all_i = set(r["read_all"] or []); own_i = set(r["own"] or []); rmsg = set(r["read_msgs"] or [])
        R = {x for x in read_all_i if long_ok(x)}
        pb = posted_by_block.get(b)
        U = set()
        if pb is not None:
            pbu = pb.filter(~pl.col("message_id").is_in(list(rmsg)) & (pl.col("spk").is_null() | (pl.col("spk") != i)))
            U = {x for x in pbu["artifact"].unique().to_list() if long_ok(x)} - R - own_i
        ab = act_by_block.get(b)
        Ua = set()
        if ab is not None:
            Ua = {x for x in ab.filter(pl.col("j") != i)["artifact"].unique().to_list() if long_ok(x)} - read_all_i - own_i - R
        rows.append({"regime": r["regime"], "agent": i, "block": b, "R": sorted(R), "U_ledger": sorted(U),
                     "U_act": sorted(Ua)})
    sets = pl.DataFrame(rows, schema={"regime": pl.Utf8, "agent": pl.Int8, "block": pl.Utf8, "R": pl.List(pl.Int32),
                                      "U_ledger": pl.List(pl.Int32), "U_act": pl.List(pl.Int32)})
    # record rows: eligible agent-days on which the artifact was mentioned (any source)
    rec = am.filter(pl.col("agent").is_not_null()).select("artifact", "agent", "pt_date").unique() \
        .join(ad.select("row", "agent", "pt_date", "regime"), on=["agent", "pt_date"])
    rec = rec.group_by("artifact", "row", "agent", "pt_date", "regime").len().rename({"len": "n_mentions"})
    return sets, rec


def build_outside_flags(ad: pl.DataFrame) -> pl.DataFrame:
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
    st = st.filter(~pl.col("holdout"))
    hm = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    st = st.filter(~pl.Series(hm))
    st = st.join(ad.select("agent", "pt_date"), on=["agent", "pt_date"], how="semi")
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("src_row")
    ct = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"])
    chat = st.filter(pl.col("kind") == "chat").join(ci, on="src_row").join(ct, on="message_id", how="left")
    ii = pl.read_parquet(ED / "intentions_index.parquet").with_row_index("src_row")
    itx = pl.read_parquet(SH / "intentions_text.parquet", columns=["event_index", "goal_text"]).rename({"goal_text": "text"})
    inte = st.filter(pl.col("kind") == "intent").join(ii, on="src_row").join(itx, on="event_index", how="left")
    out = []
    for d in (chat, inte):
        txt = d["text"].fill_null("").to_list()
        flag = [bool(OUTSIDE.search(t)) for t in txt]
        out.append(d.select("srow", "kind", "agent", "pt_date", "goal_no", "regime").with_columns(pl.Series("outside", flag)))
    return pl.concat(out).sort("srow")


def build_human_pcs(model: str):
    k = pl.read_parquet(SH / "kicks_classified.parquet").filter(pl.col("kind") == "human_message") \
        .select("message_id", "goal_no", "pt_date")
    hm = np.array(holdout_mask(k["pt_date"].to_list(), k["goal_no"].to_list()))
    k = k.filter(~pl.Series(hm))
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("row")
    k = k.join(ci, on="message_id", how="inner")
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "regime"]).with_columns(pl.col("regime").cast(pl.Utf8))
    k = k.join(cal, on="pt_date", how="left")
    C = np.load(ED / f"chat_{MODELS[model]['suffix']}.npy", mmap_mode="r")
    W = {r: load_whitener(r, 32, model) for r in ("I", "II", "III")}
    keys, pcs, nmsg = [], [], []
    for (g, reg), sub in k.group_by(["goal_no", "regime"]):
        rows = np.sort(sub["row"].to_numpy())
        if len(rows) < 4:
            continue
        Xw = np.asarray(W[reg](np.asarray(C[rows], dtype=np.float32)), dtype=np.float64)
        Xw /= np.maximum(np.linalg.norm(Xw, axis=1, keepdims=True), 1e-12)
        Xc = Xw - Xw.mean(0)
        _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
        keys.append(f"{int(g)}|{reg}"); pcs.append(Vt[:3]); nmsg.append(len(rows))
    np.savez_compressed(OUT / f"human_pcs_{model}.npz", keys=np.array(keys), pcs=np.array(pcs), n=np.array(nmsg))


def build_clocks() -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "documented_hours", "regime"]).sort("pt_date")
    cal = cal.with_columns(pl.col("documented_hours").fill_null(2.0).alias("h"))
    cal = cal.with_columns(pl.col("h").cum_sum().alias("cum_hours"))
    return cal.select("pt_date", pl.col("regime").cast(pl.Utf8), "cum_hours")


def build_boundaries(ad: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for reg in ("I", "III"):      # H82: regime II's single boundary (35 -> 36, one day) is excluded
        sub = ad.filter(pl.col("regime") == reg)
        goals = sorted(set(sub["goal_no"].to_list()))
        days = {g: sorted(set(sub.filter(pl.col("goal_no") == g)["pt_date"].to_list())) for g in goals}
        for P in goals:
            if P - 1 in days:
                nxt = P + 1 if P + 1 in days else None
                rows.append({"P": P, "prev": P - 1, "next": nxt, "regime": reg, "first_day": days[P][0],
                             "days_P": days[P][:5], "prev_days": days[P - 1], "prev_last_day": days[P - 1][-1]})
    return pl.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ad, blocks = load_panel()
    sets, rec = build_r1(ad, blocks)
    sets.write_parquet(OUT / "r1_sets.parquet"); rec.write_parquet(OUT / "r1_record_rows.parquet")
    print("r1 sets", sets.height, "record rows", rec.height, flush=True)
    of = build_outside_flags(ad)
    of.write_parquet(OUT / "outside_flags.parquet")
    print("outside flags", of.height, "share outside", round(float(of["outside"].mean()), 4), flush=True)
    for m in ("bge_small", "gte_modernbert"):
        build_human_pcs(m)
    build_clocks().write_parquet(OUT / "clocks.parquet")
    bd = build_boundaries(ad)
    bd.write_parquet(OUT / "boundaries.parquet")
    h82 = ROOT / "data/processed/H82-remanence-endogenous-field/boundaries.parquet"
    same = None
    if h82.exists():   # data comparison only (no code import)
        o = pl.read_parquet(h82).select("P", "prev", "next", "regime", "days_P").sort("regime", "P")
        n = bd.select("P", "prev", "next", "regime", "days_P").sort("regime", "P")
        same = bool(o.equals(n))
    print("boundaries", bd.height, "identical to H82's:", same, flush=True)
    prov = {"built_by": "hypotheses/H81-culture-beyond-composition/scheme/build_r2.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["culture_vectors/*", "artifact_mentions", "artifacts", "context_ledger_items",
                                   "call_windows", "chat_core", "chat_text (flags only)", "intentions_text (flags only)",
                                   "embeddings/statements", "chat_index", "intentions_index", "kicks_classified",
                                   "chat_<model>", "whitening_<model>_<regime>", "calendar"]}],
            "params": {"age_long_days": AGE_LONG, "how": STRICT, "kinds": KINDS, "outside_pattern": OUTSIDE.pattern,
                       "boundaries_identical_to_H82": same, "holdout": "dropped (holdout_mask)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
