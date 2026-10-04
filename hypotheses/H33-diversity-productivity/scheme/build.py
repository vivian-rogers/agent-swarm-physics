"""H33 scheme: agent-day and swarm-day diversity (self-deduplicated, rarefied PR) and artifact output.

Non-holdout days only (calendar flag + holdout_mask + guard). Writes, per goal period,
data/processed/H33-diversity-productivity/G<NN>/agent_day.parquet and swarm_day.parquet, plus _provenance.json.

agent_day columns: pt_date, agent, goal_no, unit, regime, lab, n_chat_raw, n_chat_dedup, selfrep, pr10, tv10, pr6, pr15,
  pr6_am, pr6_pm, n_dedup_am, n_dedup_pm, engaged_min, n_min, n_turns, writes, writes_clean, commits, deploys,
  artifacts_adv, writes_am, writes_pm.
swarm_day columns: pt_date, unit, goal_no, regime, n_active, prday_dd, tvday_dd, n_elig, writes_total, writes_per_agent.

Usage: uv run python hypotheses/H33-diversity-productivity/scheme/build.py
"""
from __future__ import annotations

import time

import h33common as C  # noqa: I001  (sets thread caps first)
import numpy as np
import polars as pl

import h12lib as L12  # H12 estimators (imported, not modified)
import posthoc as P12  # H12 self-repeat removal (dedup_rows)
from h15common import WRITE_VERBS  # H15 output definition

T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:6.1f}s] {msg}", flush=True)


def main():
    build(C.calendar_nonholdout(), C.OUT, guard=True)


def build(cal: pl.DataFrame, out_root, guard: bool = True):
    """Build agent_day / swarm_day for the calendar rows in `cal` (columns as calendar_nonholdout) into out_root.
    guard=True (exploration) aborts on any holdout day; guard=False is used only by analysis/confirm.py."""
    days = set(cal["pt_date"].to_list())
    if guard:
        C.refuse_holdout(days, "calendar")
    calj = cal.select("pt_date", "goal_no", "unit", "regime", "win_start", "win_end",
                      (pl.col("win_start") + (pl.col("win_end") - pl.col("win_start")) / 2).alias("t_mid"))
    roster = pl.read_parquet(C.SH / "roster.parquet").select("agent", "lab")
    log(f"non-holdout days {len(days)}")

    # ---------------------------------------------------------------- base agent-days (activity on the roster)
    ab = (pl.scan_parquet(C.SH / "activity_bins.parquet")
          .filter(pl.col("pt_date").is_in(list(days)) & (pl.col("agent") != C.CLAUDE_CODE_AGENT))
          .group_by("pt_date", "agent")
          .agg(pl.len().alias("n_min"), (pl.col("state") >= 3).sum().alias("engaged_min"))
          .collect())
    act = (pl.scan_parquet(C.SH / "actions.parquet").select("t", "agent", "action")
           .filter((pl.col("action") != "pause") & (pl.col("agent") != C.CLAUDE_CODE_AGENT))
           .with_columns(C.pt_date_expr("t").alias("pt_date"))
           .filter(pl.col("pt_date").is_in(list(days)))
           .group_by("pt_date", "agent").agg(pl.len().alias("n_turns")).collect())

    # ---------------------------------------------------------------- outputs (H15 write verbs, computer-use turns)
    art = pl.read_parquet(C.SH / "artifacts.parquet").select("artifact", "kind", "parent")
    am = (pl.scan_parquet(C.SH / "artifact_mentions.parquet")
          .filter((pl.col("source") == "action") & pl.col("verb").cast(pl.Utf8).is_in(WRITE_VERBS)
                  & (pl.col("agent") != C.CLAUDE_CODE_AGENT))
          .select("artifact", "t", "agent", pl.col("verb").cast(pl.Utf8), "ref_index")
          .with_columns(C.pt_date_expr("t").alias("pt_date"))
          .filter(pl.col("pt_date").is_in(list(days))).collect())
    err = (pl.scan_parquet(C.SH / "artifact_commands_text.parquet").select(pl.col("row").cast(pl.Int64), "error")
           .filter(pl.col("row").is_in(am["ref_index"].unique().to_list())).collect())
    am = am.join(err, left_on="ref_index", right_on="row", how="left")
    am = am.join(calj.select("pt_date", "t_mid"), on="pt_date", how="left")
    turns = am.unique(["agent", "t"])
    wr = turns.group_by("pt_date", "agent").agg(
        pl.len().alias("writes"),
        (~pl.col("error").fill_null(False)).sum().alias("writes_clean"),
        (pl.col("t") < pl.col("t_mid")).sum().alias("writes_am"),
        (pl.col("t") >= pl.col("t_mid")).sum().alias("writes_pm"))
    cm = am.filter(pl.col("verb") == "git commit").unique(["agent", "t"]).group_by("pt_date", "agent").agg(pl.len().alias("commits"))
    dp = am.filter(pl.col("verb") == "deploy").unique(["agent", "t"]).group_by("pt_date", "agent").agg(pl.len().alias("deploys"))
    aa = (am.join(art, on="artifact", how="left")
          .filter(pl.col("kind").cast(pl.Utf8) != "domain")
          .with_columns(pl.when((pl.col("kind").cast(pl.Utf8) == "file") & pl.col("parent").is_not_null())
                        .then(pl.col("parent")).otherwise(pl.col("artifact")).alias("adv"))
          .group_by("pt_date", "agent").agg(pl.col("adv").n_unique().alias("artifacts_adv")))
    log(f"write turns {turns.height}")

    # ---------------------------------------------------------------- chat statements, self-repeat removal, whitening
    st = (pl.read_parquet(C.EMB / "statements.parquet").with_row_index("row")
          .filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(list(days)) & (~pl.col("holdout") | (not guard))
                  & (pl.col("agent") != C.CLAUDE_CODE_AGENT)))
    if guard:
        C.refuse_holdout(st["pt_date"].unique().to_list(), "statements")
    raw_n = st.group_by("pt_date", "agent").agg(pl.len().alias("n_chat_raw"))
    idx = st.select("kind", "agent", "t", "pt_date", "row")
    kept = P12.dedup_rows(idx)  # H12 rule: drop cos > 0.95 to an earlier own statement that day (raw bge)
    st_d = st.filter(pl.col("row").is_in(kept["row"].to_list())).join(calj.select("pt_date", "unit", "t_mid"), on="pt_date")
    log(f"chat statements {st.height} -> dedup {st_d.height}")

    E = np.load(C.EMB / "chat_bge_small.npy", mmap_mode="r")
    Wd = {}
    for reg in st_d["regime"].unique().to_list():
        sub = st_d.filter(pl.col("regime") == reg)
        W = C.load_whitener(reg, C.D)
        src = sub["src_row"].to_numpy()
        order = np.argsort(src)
        Y = np.empty((len(src), C.D), dtype=np.float32)
        Y[order] = W(np.asarray(E[src[order]], dtype=np.float32))
        for r, y in zip(sub["row"].to_numpy(), Y):
            Wd[int(r)] = y
    log("whitened")

    # ---------------------------------------------------------------- agent-day PR
    rows = []
    zero = None
    for (d, a), g in st_d.sort("t").group_by(["pt_date", "agent"]):
        Y = np.stack([Wd[int(r)] for r in g["row"].to_numpy()]).astype(np.float64)
        rng = np.random.default_rng([C.SEED, C.stable_seed([d, int(a)])])
        zero = np.zeros(len(Y), dtype=np.int64)
        rec = {"pt_date": d, "agent": int(a), "n_chat_dedup": len(Y)}
        r10 = L12.pr_rarefied(Y, zero, C.N_PR, None, C.DRAWS, rng, erank=False)
        rec["pr10"], rec["tv10"] = r10["pr"], r10["tv"]
        for n in C.N_PR_ROB:
            rec[f"pr{n}"] = L12.pr_rarefied(Y, zero, n, None, C.DRAWS, rng, erank=False)["pr"]
        am_mask = (g["t"] < g["t_mid"]).to_numpy()
        for lab, m in (("am", am_mask), ("pm", ~am_mask)):
            rec[f"n_dedup_{lab}"] = int(m.sum())
            rec[f"pr6_{lab}"] = (L12.pr_rarefied(Y[m], np.zeros(int(m.sum()), dtype=np.int64), C.N_PR_HALF, None, C.DRAWS,
                                                 rng, erank=False)["pr"] if m.sum() >= C.N_PR_HALF else np.nan)
        rows.append(rec)
    prd = pl.DataFrame(rows).with_columns(pl.col("agent").cast(pl.Int8))
    log(f"agent-day PR rows {prd.height}")

    # ---------------------------------------------------------------- assemble agent_day
    ad = (ab.join(act, on=["pt_date", "agent"], how="left")
          .join(raw_n, on=["pt_date", "agent"], how="full", coalesce=True)
          .join(prd, on=["pt_date", "agent"], how="left")
          .join(wr, on=["pt_date", "agent"], how="left").join(cm, on=["pt_date", "agent"], how="left")
          .join(dp, on=["pt_date", "agent"], how="left").join(aa, on=["pt_date", "agent"], how="left")
          .join(calj.select("pt_date", "goal_no", "unit", "regime"), on="pt_date", how="inner")
          .join(roster, on="agent", how="left"))
    fill0 = ["n_min", "engaged_min", "n_turns", "n_chat_raw", "n_chat_dedup", "writes", "writes_clean", "writes_am",
             "writes_pm", "commits", "deploys", "artifacts_adv", "n_dedup_am", "n_dedup_pm"]
    ad = (ad.with_columns([pl.col(c).fill_null(0).cast(pl.Int32) for c in fill0])
          .with_columns(pl.when(pl.col("n_chat_raw") > 0).then(1 - pl.col("n_chat_dedup") / pl.col("n_chat_raw"))
                        .otherwise(None).cast(pl.Float32).alias("selfrep"))
          .with_columns([pl.col(c).cast(pl.Float32).fill_nan(None) for c in ["pr10", "tv10", "pr6", "pr15", "pr6_am", "pr6_pm"]])
          .filter((pl.col("engaged_min") > 0) | (pl.col("n_chat_raw") > 0) | (pl.col("n_turns") > 0))
          .select("pt_date", "agent", "goal_no", "unit", "regime", "lab", "n_chat_raw", "n_chat_dedup", "selfrep",
                  "pr10", "tv10", "pr6", "pr15", "pr6_am", "pr6_pm", "n_dedup_am", "n_dedup_pm", "engaged_min",
                  "n_min", "n_turns", "writes", "writes_clean", "commits", "deploys", "artifacts_adv", "writes_am",
                  "writes_pm")
          .sort("pt_date", "agent"))
    if guard:
        C.refuse_holdout(ad["pt_date"].unique().to_list(), "agent_day")

    # ---------------------------------------------------------------- swarm-day
    srows = []
    for d, g in st_d.group_by("pt_date"):
        d = d[0] if isinstance(d, tuple) else d
        Y = np.stack([Wd[int(r)] for r in g["row"].to_numpy()]).astype(np.float64)
        rng = np.random.default_rng([C.SEED, C.stable_seed([d, "swarm"])])
        r = L12.pr_balanced(Y, g["agent"].to_numpy(), C.SWARM_M, C.SWARM_K, C.SWARM_DRAWS, rng, erank=False)
        srows.append({"pt_date": d, "prday_dd": r["pr"], "tvday_dd": r["tv"], "n_elig": r["n_elig"]})
    sp = pl.DataFrame(srows).with_columns(pl.col("prday_dd").fill_nan(None), pl.col("tvday_dd").fill_nan(None))
    sw = (ad.group_by("pt_date").agg((pl.col("engaged_min") > 0).sum().alias("n_active"),
                                     pl.col("writes").sum().alias("writes_total"))
          .with_columns((pl.col("writes_total") / pl.col("n_active").clip(1, None)).alias("writes_per_agent"))
          .join(sp, on="pt_date", how="left").join(calj.select("pt_date", "goal_no", "unit", "regime"), on="pt_date")
          .sort("pt_date"))

    # ---------------------------------------------------------------- write per goal period
    out_root.mkdir(parents=True, exist_ok=True)
    for u in sorted(ad["unit"].unique().to_list()):
        od = out_root / C.unit_dir(u).name
        od.mkdir(parents=True, exist_ok=True)
        g = int(u.rstrip("abt"))
        ad.filter(pl.col("goal_no") == g).write_parquet(od / "agent_day.parquet", compression="zstd")
        sw.filter(pl.col("goal_no") == g).write_parquet(od / "swarm_day.parquet", compression="zstd")
    C.write_provenance("hypotheses/H33-diversity-productivity/scheme/build.py",
                       ["embeddings/statements", "embeddings/chat_bge_small", "whitening_I/II/III", "artifact_mentions",
                        "artifact_commands_text (error flag)", "artifacts", "activity_bins", "actions", "calendar", "roster"],
                       {"N_PR": C.N_PR, "N_PR_ROB": C.N_PR_ROB, "N_PR_HALF": C.N_PR_HALF, "draws": C.DRAWS, "d": C.D,
                        "swarm": [C.SWARM_M, C.SWARM_K, C.SWARM_DRAWS], "near_dup_cos": C.NEAR_DUP,
                        "write_verbs": WRITE_VERBS, "seed": C.SEED, "non_holdout_only": guard,
                        "units": "goal period; #36 split at 2026-03-24", "guard": guard},
                       path=out_root / "_provenance.json")
    log(f"agent_day {ad.height} rows, swarm_day {sw.height} rows; done")


if __name__ == "__main__":
    main()
