"""H73 scheme: per-message style table with context state, time of day, register and genre flags (no text; holdout dropped).

Inputs (data/processed/shared/): text_features (H13's 20 style features), embeddings/statements + chat_index (row map to
statement_flags), statement_flags (DQ5 dedupe flags), context_ledger_turns (DQ1 talk calls: ctx_mode, ctx_pos, k_ctx),
calendar (win_start), period_units, ground_truth_labels (DQ6 #12 judges/teams, #51 roles), reply_pairs (DQ2 parent),
chat_mentions_clean, roster.
Output (data/processed/H73-style-three-components/):
  messages.parquet             one row per non-holdout agent chat message matched to its talk call
  style_standardization.json   winsorization, z-scoring and type-control coefficients (frozen for confirm.py)
  _provenance.json
Style construction re-implements H46's (17 type-controlled features); nothing is imported from another hypothesis.
Usage: uv run python hypotheses/H73-style-three-components/scheme/build.py
"""
from __future__ import annotations
import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")
import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra" / "shared"))
from common import holdout_mask, REVISION  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H73-style-three-components"
STYLE = ["log_chars", "lines", "bullet_share", "headers", "bold", "emoji", "excl", "ques", "urls", "backticks",
         "digit_share", "upper_share", "at", "emdash", "fps", "fpp", "sp", "colon", "word_len", "parens"]
TYPE_COVS = ["log_chars", "backticks", "urls"]
TC = [f for f in STYLE if f not in TYPE_COVS]
EXCLUDE_MAIN = {19, 28, 30}
JOIN_TOL = "3s"


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    d = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H73-style-three-components"],
                       capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if d.strip() else "")


def standardize(F: np.ndarray, regime: np.ndarray, meta: dict | None = None):
    """Winsorize + z-score (global) + type control within regime. meta given -> apply frozen coefficients."""
    fit = meta is None
    if fit:
        lo, hi = np.quantile(F, 0.001, axis=0), np.quantile(F, 0.999, axis=0)
    else:
        lo = np.array([meta["winsor_lo"][f] for f in STYLE]); hi = np.array([meta["winsor_hi"][f] for f in STYLE])
    Fw = np.clip(F, lo, hi)
    if fit:
        mu, sd = Fw.mean(0), Fw.std(0)
        sd[sd == 0] = 1.0
    else:
        mu = np.array([meta["mu"][f] for f in STYLE]); sd = np.array([meta["sd"][f] for f in STYLE])
    Z = (Fw - mu) / sd
    lc = F[:, STYLE.index("log_chars")]
    has_code = (F[:, STYLE.index("backticks")] > 0).astype(float)
    has_url = (F[:, STYLE.index("urls")] > 0).astype(float)
    TCm = np.zeros((len(F), len(TC)))
    info = {} if fit else meta["type_control"]
    for r in np.unique(regime):
        ix = np.where(regime == r)[0]
        if fit:
            knots = np.quantile(lc[ix], [0.25, 0.5, 0.75])
        else:
            knots = np.array(info[str(r)]["knots"])
        X = np.column_stack([np.ones(len(ix)), lc[ix]] + [np.maximum(lc[ix] - k, 0) for k in knots]
                            + [has_code[ix], has_url[ix]])
        Y = Z[ix][:, [STYLE.index(f) for f in TC]]
        if fit:
            B, *_ = np.linalg.lstsq(X, Y, rcond=None)
            info[str(r)] = {"n": int(len(ix)), "knots": knots.tolist(), "coef": B.tolist()}
        else:
            B = np.array(info[str(r)]["coef"])
        TCm[ix] = Y - X @ B
    meta_out = meta or {"winsor_lo": dict(zip(STYLE, lo.tolist())), "winsor_hi": dict(zip(STYLE, hi.tolist())),
                        "mu": dict(zip(STYLE, mu.tolist())), "sd": dict(zip(STYLE, sd.tolist())), "type_control": info}
    return Z, TCm, has_code.astype(bool), has_url.astype(bool), meta_out


def base_messages(include_holdout: bool = False) -> pl.DataFrame:
    """Agent chat messages with call context, unit, hours, genre and dedupe flags (no style transform)."""
    tf = pl.read_parquet(SH / "text_features.parquet",
                         columns=["message_id", "msg", "agent", "t", "pt_date", "goal_no", "room", "holdout"]
                         + [f"f_{f}" for f in STYLE])
    hm = pl.Series(holdout_mask(tf["pt_date"].to_list(), tf["goal_no"].to_list()))
    tf = tf.with_columns((pl.col("holdout") | hm).alias("holdout"))
    if not include_holdout:
        tf = tf.filter(~pl.col("holdout"))
    st = pl.read_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    smap = (st.filter(pl.col("kind") == "chat").select("srow", "src_row", "regime")
            .join(ci, on="src_row").select("message_id", "srow", "regime"))
    fl = pl.read_parquet(SH / "statement_flags.parquet",
                         columns=["srow", "self_repeat_both", "self_repeat_bge", "self_repeat_gte"])
    df = tf.join(smap, on="message_id", how="inner").join(fl, on="srow", how="left")
    df = df.with_columns(pl.col("self_repeat_both").fill_null(False).alias("copy"),
                         (pl.col("self_repeat_bge").fill_null(False) | pl.col("self_repeat_gte").fill_null(False))
                         .alias("restate")).drop("self_repeat_both", "self_repeat_bge", "self_repeat_gte")
    # producing talk call
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("talk"))
          .select("turn_id", "agent", "t_first", "ctx_mode", "ctx_pos", "k_ctx", "holdout").collect())
    if not include_holdout:
        ct = ct.filter(~pl.col("holdout"))
    ct = ct.drop("holdout").sort("t_first")
    df = df.sort("t").join_asof(ct, left_on="t", right_on="t_first", by="agent", strategy="nearest",
                                tolerance=JOIN_TOL, check_sortedness=False)
    n0 = df.height
    df = df.filter(pl.col("turn_id").is_not_null() & (pl.col("ctx_mode") != "summary"))
    print(f"messages: {n0:,}; matched to a talk call: {df.height:,} ({df.height / n0:.3f})", flush=True)
    # units
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "goal_no", "start").sort("start")
    df = df.sort("t").join_asof(pu.rename({"goal_no": "pu_goal"}), left_on="t", right_on="start", strategy="backward")
    df = df.filter(pl.col("pu_goal") == pl.col("goal_no")).drop("pu_goal", "start")
    # hours since the day's first agent event
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "win_start"])
    df = df.join(cal, on="pt_date", how="left").with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() / 3600.0).clip(0, 24).cast(pl.Float32).alias("hours")
    ).drop("win_start")
    # genre flags
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet").filter((pl.col("pair_set") == "cand") & pl.col("parent"))
          .select(pl.col("B_message_id").alias("message_id")).unique().collect().with_columns(pl.lit(True).alias("is_reply")))
    mc = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"]).with_columns(
        (pl.col("mentions_roster").list.len() > 0).alias("has_mention")).drop("mentions_roster")
    df = (df.join(rp, on="message_id", how="left").join(mc, on="message_id", how="left")
          .with_columns(pl.col("is_reply").fill_null(False), pl.col("has_mention").fill_null(False)))
    # registers (DQ6, preferred & ~holdout)
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(pl.col("preferred") & ~pl.col("holdout"))
    reg12 = np.array(["none"] * df.height, dtype=object)
    deb = np.array([""] * df.height, dtype=object)
    ag = df["agent"].to_numpy()
    tt = df["t"].dt.epoch("us").to_numpy()
    g12 = gt.filter((pl.col("goal_no") == 12) & pl.col("label_kind").is_in(["judge", "team"]))
    for r in g12.iter_rows(named=True):
        a0, a1 = r["t_valid_from"].timestamp() * 1e6, r["t_valid_to"].timestamp() * 1e6
        msk = (ag == r["agent"]) & (tt >= a0) & (tt < a1)
        if r["label_kind"] == "judge":
            reg12[msk] = "judge"
        elif r["value"] in ("gov", "opp"):
            reg12[msk & (reg12 != "judge")] = "debater"
        deb[msk] = r["unit"]
    roles = gt.filter((pl.col("goal_no") == 51) & pl.col("label_kind").is_in(["role", "role_class"]))
    role = np.array([""] * df.height, dtype=object)
    rclass = np.array([""] * df.height, dtype=object)
    for r in roles.iter_rows(named=True):
        a0 = r["t_valid_from"].timestamp() * 1e6
        a1 = r["t_valid_to"].timestamp() * 1e6 if r["t_valid_to"] is not None else np.inf
        msk = (ag == r["agent"]) & (tt >= a0) & (tt < a1)
        (role if r["label_kind"] == "role" else rclass)[msk] = r["value"]
    df = df.with_columns(pl.Series("register", reg12.astype(str)), pl.Series("debate", deb.astype(str)),
                         pl.Series("role", role.astype(str)), pl.Series("role_class", rclass.astype(str)),
                         (~pl.col("agent").is_in(list(EXCLUDE_MAIN))).alias("main"))
    return df


def build(include_holdout: bool = False, meta: dict | None = None):
    df = base_messages(include_holdout)
    F = df.select([f"f_{f}" for f in STYLE]).to_numpy().astype(np.float64)
    fitmask = ~df["holdout"].to_numpy()
    if meta is None:   # fit on non-holdout rows only
        assert fitmask.all(), "standardization must be fit on non-holdout rows only"
    Z, TCm, has_code, has_url, meta = standardize(F, df["regime"].to_numpy(), meta)
    out = df.select("message_id", "msg", "srow", "agent", "t", "pt_date", "goal_no", "unit_id", "regime", "room",
                    "holdout", "main", "copy", "restate", "turn_id", "ctx_mode", "ctx_pos", "k_ctx", "hours",
                    "is_reply", "has_mention", "register", "debate", "role", "role_class").with_columns(
        pl.col("ctx_mode").cast(pl.String), pl.col("regime").cast(pl.String),
        pl.Series("has_code", has_code), pl.Series("has_url", has_url),
        *[pl.Series(f"s_{f}", Z[:, i].astype(np.float32)) for i, f in enumerate(STYLE)],
        *[pl.Series(f"tc_{f}", TCm[:, i].astype(np.float32)) for i, f in enumerate(TC)])
    return out, meta


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    msgs, meta = build(include_holdout=False)
    assert not msgs["holdout"].any()
    assert not any(holdout_mask(msgs["pt_date"].to_list(), msgs["goal_no"].to_list()))
    msgs.write_parquet(OUT / "messages.parquet", compression="zstd")
    (OUT / "style_standardization.json").write_text(json.dumps(meta, indent=1))
    print(f"messages.parquet: {msgs.height:,} rows; main {msgs['main'].sum():,}; copy {msgs['copy'].mean():.3f}; "
          f"restate {msgs['restate'].mean():.3f}; cu {(msgs['ctx_mode'] == 'cu').mean():.3f}", flush=True)
    print(msgs.group_by("register").len(), msgs.filter(pl.col("role") != "").group_by("role_class").len())
    prov = {"built_by": "hypotheses/H73-style-three-components/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/text_features", "shared/embeddings/statements", "shared/embeddings/chat_index",
                                   "shared/statement_flags", "shared/context_ledger_turns", "shared/calendar",
                                   "shared/period_units", "shared/ground_truth_labels", "shared/reply_pairs",
                                   "shared/chat_mentions_clean"]}],
            "params": {"style": STYLE, "type_covariates": TYPE_COVS, "type_controlled": TC, "winsor": [0.001, 0.999],
                       "exclude_main": sorted(EXCLUDE_MAIN), "call_join": f"nearest t_first, same agent, {JOIN_TOL}",
                       "copy": "statement_flags.self_repeat_both", "restate": "self_repeat_bge | self_repeat_gte",
                       "is_reply": "reply_pairs pair_set=cand & parent", "has_mention": "mentions_roster non-empty",
                       "registers": "DQ6 #12 judge/team windows; #51 role and role_class (preferred & ~holdout)",
                       "holdout": "calendar holdout flag OR common.holdout_mask; asserted"},
            "built_at": dt.datetime.now(dt.UTC).isoformat()}
    old = json.loads((OUT / "_provenance.json").read_text()) if (OUT / "_provenance.json").exists() else {}
    if "analysis" in old:
        prov["analysis"] = old["analysis"]
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
