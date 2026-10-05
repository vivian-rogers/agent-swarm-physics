"""H13 round 2 scheme: per-unit statement tables for the graded style ladder (R2-A).

For every round-1b unit (scheme/build.py UNITS) writes data/processed/H13-family-fields/r2/stmts/u<unit>.parquet with,
per agent chat statement that has a DQ5 vector and a text_features row (codes and numbers only, no text):
  srow (row of shared embeddings/statements.parquet), message_id, agent, lab, pt_date, room, role (#51)
  f_*        H13's 20 style features (shared text_features)
  w_*        sqrt relative frequency of the FW50 closed-class words (FW list copied from H46 round 2; the 50 most
             frequent in non-reserved H13-unit statements with >= 10 tokens), n_tok, short (n_tok < 10)
  genre      is_reply, par_human, par_auto, p_supports, p_opposes, p_asks, p_reply_max, has_ment, log_ment, lead_at,
             12 DQ3 probabilities (execute_task = reference) and dq3_missing
Reserved days raise (common.holdout_mask) unless allow_holdout (not used in round 2).

Usage: uv run python hypotheses/H13-family-fields/scheme/build_r2.py
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import build as B  # noqa: E402  (H13's own round-1 scheme: UNITS, STYLE, unit_days, roles_for)
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H13-family-fields/r2"

# H46 round-2 closed-class list (fixed 2026-10-04 by H46; copied verbatim, not imported)
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
DQ3 = ["p_plan_coordinate", "p_research_browse", "p_communicate_external", "p_debug_recover", "p_verify_report",
       "p_monitor_wait", "p_self_maintenance", "p_social", "p_meta", "p_idle", "p_addresses_participant", "p_blocked"]
N_FW, MIN_TOK = 50, 10


def unit_statements(u, spec):
    days = B.unit_days(spec)
    assert not any(holdout_mask(days, [spec[1]] * len(days)))
    st = (pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
          .filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(days) & ~pl.col("holdout")))
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("src_row")
    s = st.join(ci, on="src_row", how="left").sort("t")
    tf = pl.read_parquet(SH / "text_features.parquet", columns=["message_id"] + [f"f_{k}" for k in B.STYLE])
    s = s.join(tf, on="message_id", how="inner")
    return s, days


def word_counts(ids: pl.Series):
    tx = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).join(
        pl.DataFrame({"message_id": ids}), on="message_id", how="semi")
    idx = {w: k for k, w in enumerate(FW)}
    C = np.zeros((tx.height, len(FW)), np.uint16)
    nt = np.zeros(tx.height, np.int32)
    lead = np.zeros(tx.height, bool)
    for r, t in enumerate(tx["text"].to_list()):
        t = t or ""
        lead[r] = t.lstrip().startswith("@")
        toks = TOK.findall(CODE.sub(" ", URL.sub(" ", t)).lower())
        nt[r] = len(toks)
        for w in toks:
            k = idx.get(w)
            if k is not None:
                C[r, k] += 1
    return tx["message_id"], C, nt, lead


def genre(ids: pl.Series, s: pl.DataFrame):
    idf = pl.DataFrame({"message_id": ids})
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet").filter((pl.col("pair_set") == "cand") & ~pl.col("holdout"))
          .select("B_message_id", "parent", "p_reply", "a_kind", "p_supports", "p_opposes", "p_asks").collect()
          .rename({"B_message_id": "message_id"}).join(idf, on="message_id", how="semi"))
    pmax = rp.group_by("message_id").agg(pl.col("p_reply").max().alias("p_reply_max"))
    par = (rp.filter(pl.col("parent")).sort("p_reply", descending=True).unique("message_id", keep="first")
           .select("message_id", pl.lit(1.0).alias("is_reply"), (pl.col("a_kind") == 1).cast(pl.Float64).alias("par_human"),
                   (pl.col("a_kind") == 2).cast(pl.Float64).alias("par_auto"), "p_supports", "p_opposes", "p_asks"))
    men = (pl.read_parquet(SH / "chat_mentions_clean.parquet").join(idf, on="message_id", how="semi")
           .select("message_id", pl.col("mentions_roster").list.len().alias("n_ment")))
    g = idf.join(pmax, on="message_id", how="left").join(par, on="message_id", how="left").join(men, on="message_id", how="left")
    g = g.with_columns(*[pl.col(c).fill_null(0.0) for c in ("p_reply_max", "is_reply", "par_human", "par_auto",
                                                              "p_supports", "p_opposes", "p_asks")],
                       pl.col("n_ment").fill_null(0))
    g = g.with_columns((pl.col("n_ment") > 0).cast(pl.Float64).alias("has_ment"),
                       pl.col("n_ment").cast(pl.Float64).log1p().alias("log_ment")).drop("n_ment")
    b = (pl.scan_parquet(SH / "behavior_states_v3.parquet").filter(~pl.col("holdout") & pl.col("labeled"))
         .select("agent", "t0", "t1", *DQ3).collect().sort("t0"))
    x = s.select("message_id", "agent", "t").sort("t")
    j = x.join_asof(b, left_on="t", right_on="t0", by="agent", strategy="backward")
    ok = (j["t"] < j["t1"]).fill_null(False)
    j = j.with_columns(pl.Series("dq3_missing", (~ok).cast(pl.Float64).to_numpy()),
                       *[pl.when(pl.Series(ok)).then(pl.col(c)).otherwise(0.0).fill_null(0.0).alias(c) for c in DQ3])
    return g.join(j.select("message_id", "dq3_missing", *DQ3), on="message_id", how="left")


def main():
    OUT.joinpath("stmts").mkdir(parents=True, exist_ok=True)
    ro = pl.read_parquet(SH / "roster.parquet", columns=["agent", "lab"])
    per = {}
    allC, allN = [], []
    for u, spec in B.UNITS.items():
        s, days = unit_statements(u, spec)
        mid, C, nt, lead = word_counts(s["message_id"])
        wc = pl.DataFrame({"message_id": mid, "n_tok": nt, "lead_at": lead.astype(np.float64)})
        s = s.join(wc, on="message_id", how="left")
        order = {m: i for i, m in enumerate(mid.to_list())}
        ix = np.array([order[m] for m in s["message_id"].to_list()])
        per[u] = (s, days, C[ix], nt[ix])
        allC.append(C[ix][nt[ix] >= MIN_TOK])
        print(u, s.height, flush=True)
    tot = np.vstack(allC).sum(0)
    top = list(np.argsort(-tot)[:N_FW])
    words = [FW[k] for k in top]
    for u, (s, days, C, nt) in per.items():
        F = np.sqrt(C[:, top] / np.maximum(nt, 1)[:, None]).astype(np.float64)
        short = nt < MIN_TOK
        g = genre(s["message_id"], s)
        roles = B.roles_for(days) if spec_goal(u) >= 51 else {}
        t = (s.select("srow", "message_id", "agent", "t", "pt_date", "room", "n_tok", "lead_at",
                      *[f"f_{k}" for k in B.STYLE])
             .join(ro, on="agent", how="left")
             .with_columns(pl.col("agent").replace_strict(roles, default=None, return_dtype=pl.String).alias("role"),
                           pl.Series("short", short)))
        t = t.with_columns(*[pl.Series(f"w_{w}", np.where(short, np.nan, F[:, k]).astype(np.float32))
                             for k, w in enumerate(words)])
        t = t.join(g, on="message_id", how="left")
        assert t.height == s.height
        t.write_parquet(OUT / "stmts" / f"u{u}.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H13-family-fields/scheme/build_r2.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements", "shared/embeddings/chat_index", "shared/text_features",
                                   "shared/chat_text (counts only)", "shared/reply_pairs", "shared/chat_mentions_clean",
                                   "shared/behavior_states_v3", "shared/roster", "shared/calendar", "raw/agent_goals"]}],
            "params": {"fw50": words, "fw_source": "H46 round-2 list (128 words), top 50 by frequency in H13 units",
                       "min_tok": MIN_TOK, "dq3": DQ3, "units": list(B.UNITS)},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print("FW50:", words)


def spec_goal(u):
    return B.UNITS[u][1]


if __name__ == "__main__":
    main()
