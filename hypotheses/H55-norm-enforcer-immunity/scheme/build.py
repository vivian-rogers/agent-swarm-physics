"""H55 scheme: builds data/processed/H55-norm-enforcer-immunity/ from shared tables (codes only, no text).

  uv run python hypotheses/H55-norm-enforcer-immunity/scheme/build.py messages
  uv run python hypotheses/H55-norm-enforcer-immunity/scheme/build.py loops
  uv run python hypotheses/H55-norm-enforcer-immunity/scheme/build.py blocked
  uv run python hypotheses/H55-norm-enforcer-immunity/scheme/build.py reads

Non-holdout rows only (holdout_mask re-checked). `--allow-holdout` (confirmatory use only) writes to OUT/confirm_build/.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h55common as H  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import lexicon  # noqa: E402

BUILT_BY = "hypotheses/H55-norm-enforcer-immunity/scheme/build.py"


def outdir(allow_holdout: bool) -> Path:
    d = H.OUT / "confirm_build" if allow_holdout else H.OUT
    d.mkdir(parents=True, exist_ok=True)
    return d


def units_table() -> pl.DataFrame:
    pu = pl.read_parquet(H.SH / "period_units.parquet").select("unit_id", "goal_no", "start", "end", "days", "holdout")
    return pu


def assign_unit(df: pl.DataFrame, tcol: str = "t") -> pl.DataFrame:
    """unit_id by goal_no and time inside [start, end] (period_units); falls back to the unit containing pt_date."""
    pu = units_table().select("unit_id", "goal_no", "start", "end")
    d = df.with_row_index("_r")
    j = d.select("_r", "goal_no", tcol).join(pu, on="goal_no", how="left")
    j = j.filter((pl.col(tcol) >= pl.col("start")) & (pl.col(tcol) <= pl.col("end"))).group_by("_r").agg(pl.col("unit_id").first())
    d = d.join(j, on="_r", how="left")
    miss = d.filter(pl.col("unit_id").is_null())
    if miss.height:
        pu2 = units_table().explode("days").select("unit_id", "goal_no", pl.col("days").alias("pt_date"))
        pu2 = pu2.group_by("goal_no", "pt_date").agg(pl.col("unit_id").first().alias("u2"))
        d = d.join(pu2, on=["goal_no", "pt_date"], how="left").with_columns(pl.coalesce("unit_id", "u2").alias("unit_id")).drop("u2")
    return d.drop("_r")


# --------------------------------------------------------------------------------------------------------- messages
def build_messages(allow_holdout: bool = False) -> pl.DataFrame:
    cc = pl.read_parquet(H.SH / "chat_core.parquet").select(
        "message_id", "t", "pt_date", "goal_no", "regime", "room", "speaker_kind", "agent", "length")
    cc = cc.with_columns(pl.Series("holdout", H.holdout_flags(cc["pt_date"], cc["goal_no"])))
    if not allow_holdout:
        cc = cc.filter(~pl.col("holdout"))
    cc = cc.filter(pl.col("speaker_kind").cast(pl.Utf8).is_in(["agent", "human"]))
    mc = pl.read_parquet(H.SH / "chat_mentions_clean.parquet").select("message_id", "mentions_roster")
    cc = cc.join(mc, on="message_id", how="left")
    # text in memory only
    tx = pl.read_parquet(H.SH / "chat_text.parquet", columns=["message_id", "text"]).join(cc.select("message_id"), on="message_id")
    fam = {k: [] for k in ("corr", "norm", "decl")}
    for t in tx["text"].to_list():
        f = lexicon.families(t)
        for k in fam:
            fam[k].append(f[k])
    mk = pl.DataFrame({"message_id": tx["message_id"], "lex_corr": fam["corr"], "lex_norm": fam["norm"], "lex_decl": fam["decl"]})
    del tx
    cc = cc.join(mk, on="message_id", how="left")
    # DQ2 parent (best visible candidate with p_reply >= 0.5)
    rp = (pl.scan_parquet(H.SH / "reply_pairs.parquet")
          .filter((pl.col("pair_set") == "cand") & pl.col("parent"))
          .select(pl.col("B_message_id").alias("message_id"), pl.col("A_message_id").alias("parent_id"),
                  pl.col("a_kind").alias("parent_kind"), pl.col("a_agent").alias("parent_agent"), "p_reply",
                  "p_supports", "p_opposes", "p_asks", "p_neutral", pl.col("stance").cast(pl.Utf8),
                  "stance_conf", pl.col("opp_type").cast(pl.Utf8), "p_opp_correction", "p_opp_decline", "p_opp_position")
          .collect().unique("message_id", keep="first"))
    cc = cc.join(rp, on="message_id", how="left")
    me = pl.col("agent")
    cc = cc.with_columns(
        pl.col("mentions_roster").fill_null([]).list.set_difference(pl.concat_list(me.fill_null(-99))).alias("named"),
    ).with_columns(
        pl.when((pl.col("parent_kind") == 0) & (pl.col("parent_agent") != me.fill_null(-99)))
        .then(pl.concat_list("named", pl.col("parent_agent"))).otherwise(pl.col("named")).list.unique().alias("targets"),
    ).with_columns(
        ((pl.col("targets").list.len() > 0) | pl.col("parent_kind").is_in([1, 2]).fill_null(False)).alias("addressed"),
    ).with_columns(
        (pl.col("addressed") & (pl.col("lex_corr") | pl.col("lex_norm") | pl.col("lex_decl")).fill_null(False)).alias("corr_lex"),
        ((pl.col("stance") == "opposes") & (pl.col("stance_conf") >= 0.8)
         & pl.col("opp_type").is_in(["correction", "decline"])).fill_null(False).alias("corr_jev"),
    )
    # statement flags (agent chat only)
    ci = pl.read_parquet(H.SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    st = pl.read_parquet(H.SH / "embeddings/statements.parquet").with_row_index("srow").filter(pl.col("kind") == "chat").select("srow", "src_row")
    fl = pl.read_parquet(H.SH / "statement_flags.parquet").select(
        "srow", "self_repeat_bge", "self_repeat_gte", "self_repeat_both", "exact_self_repeat", "self_repeat_cos_bge")
    st = st.join(ci, on="src_row").join(fl, on="srow").select(
        "message_id", "srow", pl.col("self_repeat_bge").fill_null(False), pl.col("self_repeat_gte").fill_null(False),
        pl.col("self_repeat_both").fill_null(False), pl.col("exact_self_repeat").fill_null(False), "self_repeat_cos_bge")
    cc = cc.join(st, on="message_id", how="left").with_columns(
        (pl.col("self_repeat_bge") | pl.col("self_repeat_gte")).alias("restate"),
        pl.col("self_repeat_both").alias("copy"))
    cc = assign_unit(cc)
    cc = cc.sort("t").drop("mentions_roster")
    return cc


# ------------------------------------------------------------------------------------------------- validation sheet
def draw_validation(n_random: int = 90, n_lex: int = 40, n_jev: int = 20):
    """Blind sheet: text to the session scratchpad only; strata key kept separately (not shown while labelling)."""
    import json
    m = pl.read_parquet(H.OUT / "messages.parquet").filter((pl.col("speaker_kind") == "agent") & pl.col("addressed"))
    rng = np.random.default_rng(H.SEED + 55)
    # random, stratified by regime proportional to size
    parts = []
    tot = m.height
    for reg, g in m.group_by("regime"):
        k = int(round(n_random * g.height / tot))
        parts.append(g.sample(n=k, seed=int(rng.integers(1e9))))
    rnd = pl.concat(parts).with_columns(pl.lit("random").alias("stratum"))
    rest = m.join(rnd.select("message_id"), on="message_id", how="anti")
    lex = rest.filter(pl.col("corr_lex")).sample(n=n_lex, seed=int(rng.integers(1e9))).with_columns(pl.lit("lex").alias("stratum"))
    rest = rest.join(lex.select("message_id"), on="message_id", how="anti")
    jev = rest.filter(pl.col("corr_jev")).sample(n=n_jev, seed=int(rng.integers(1e9))).with_columns(pl.lit("jev").alias("stratum"))
    s = pl.concat([rnd, lex, jev], how="diagonal_relaxed")
    s = s.with_columns(pl.Series("order", rng.permutation(s.height))).sort("order").with_row_index("item")
    tx = pl.read_parquet(H.SH / "chat_text.parquet", columns=["message_id", "text"])
    names = dict(zip(*pl.read_parquet(H.SH / "roster.parquet").select("agent", "name").to_dict(as_series=False).values()))
    T = dict(zip(*tx.join(pl.concat([s.select("message_id"), s.select(pl.col("parent_id").alias("message_id"))]).drop_nulls(),
                          on="message_id").to_dict(as_series=False).values()))
    lines = []
    for r in s.iter_rows(named=True):
        par = T.get(r["parent_id"], "") if r["parent_id"] else ""
        pk = {0: names.get(r["parent_agent"], "agent"), 1: "a human", 2: "automated"}.get(r["parent_kind"], "")
        tg = ", ".join(names.get(a, str(a)) for a in (r["targets"] or []))
        lines.append(f"=== ITEM {r['item']} ===\nSPEAKER: {names.get(r['agent'], r['agent'])}  ADDRESSED TO: {tg}\n"
                     f"PARENT ({pk}): {par[:600]}\n--- MESSAGE ---\n{(T.get(r['message_id']) or '')[:1200]}\n")
    H.SCRATCH.mkdir(parents=True, exist_ok=True)
    (H.SCRATCH / "h55_validation_sheet.txt").write_text("\n".join(lines))
    key = s.select("item", "message_id", "stratum", "regime", "goal_no", "lex_corr", "lex_norm", "lex_decl", "corr_lex", "corr_jev")
    vd = H.OUT / "validation"
    vd.mkdir(exist_ok=True)
    key.write_parquet(vd / "sample_key.parquet")   # codes only; NOT read until labelling is done
    json.dump({"n": s.height, "drawn_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
               "lexicon": lexicon.VERSION, "seed": H.SEED + 55}, open(vd / "sample_meta.json", "w"), indent=1)
    print(f"sheet: {s.height} items -> scratchpad h55_validation_sheet.txt; key -> validation/sample_key.parquet")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["messages", "validation-sample", "loops", "blocked", "reads"])
    ap.add_argument("--allow-holdout", action="store_true")
    a = ap.parse_args()
    od = outdir(a.allow_holdout)
    if a.step == "messages":
        m = build_messages(a.allow_holdout)
        m.write_parquet(od / "messages.parquet", compression="zstd")
        H.write_prov("messages", BUILT_BY, ["chat_core", "chat_mentions_clean", "chat_text (in memory)", "reply_pairs",
                                            "statement_flags", "embeddings/statements", "period_units"],
                     {"lexicon": lexicon.VERSION, "parent": "reply_pairs.parent (p_reply>=0.5, cand)",
                      "jev_corr": "opposes & conf>=0.8 & opp_type in {correction, decline}", "allow_holdout": a.allow_holdout})
        print(m.height, m.filter(pl.col("speaker_kind") == "agent").select(
            pl.col("addressed").mean(), pl.col("corr_lex").mean(), pl.col("corr_jev").mean(), pl.col("restate").mean()))
    elif a.step == "validation-sample":
        draw_validation()
    else:
        import build_steps
        getattr(build_steps, a.step)(od, a.allow_holdout)


if __name__ == "__main__":
    main()
