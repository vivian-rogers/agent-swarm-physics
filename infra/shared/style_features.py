"""Style standardization and type control for agent chat messages, plus the NE41 erasure-pair builder.

Moved from H46 (hypotheses/H46-style-conserved-charge/scheme/build.py: build_messages, ne41_pairs) and H73
(hypotheses/H73-style-three-components/scheme/build.py: standardize, base_messages; analysis/h73lib.py: ne41_pairs),
which each carried a copy (STANDARDS §8, 2026-10-04). Rules unchanged; the hypothesis copies stay in place.

Style ruler (H46 card, re-implemented by H73):
  features   H13's 20 style features from shared `text_features` (STYLE);
  s_*        winsorized at the fit population's 0.1 / 99.9% quantiles, then z-scored (one global ruler);
  tc_*       17 type-controlled features: within each regime, the OLS residual of the z-features on a log_chars
             linear spline (knots at the regime's quartiles) + has_code (backticks > 0) + has_url (urls > 0);
  fit        on non-holdout rows only; `standardize(F, regime, meta)` applies frozen coefficients (confirm scripts).
The coefficients depend on the fit population: H46 fits on every non-holdout agent chat message with a statement row;
H73 fits on the subset matched to a ledger talk call. `standardize` reproduces either; the shared table uses H46's.

NE41 pairs (consecutive eligible messages of one agent on one PT day, regime III, labelled by the resets between them):
  rule "time" (H46)  counts consolidations by their log time between the two message times (forced = the consolidation
                     row's prev_seg_len in {41, 42}, DQ1) and session resets (reset_session & ~reset_consol, at t_call);
  rule "call" (H73)  matches each message to its talk call and differences the per-agent cumulative counts of the
                     ledger flags reset_forced, reset_consol & ~reset_forced, reset_session & ~reset_consol between the
                     two calls; pairs inside one call are dropped.
  label: within (no reset), forced (one forced, nothing else), voluntary (one voluntary, nothing else), other.
The two rules do not label every pair alike (see --verify); state which one a result uses.

Holdout. `style_messages` covers ALL agent chat messages with a statement row and a `holdout` flag, like its parent
`text_features`; the ruler is fit on non-holdout rows only and applied frozen to held-out rows. Exploratory users filter
`~holdout`. `style_ne41_pairs` is non-holdout only (both originals); `ne41_pairs_*(..., include_holdout=True)` is for
confirm scripts only.

Outputs (data/processed/shared/):
  style_messages.parquet    message_id, msg (chat_core row), srow (embeddings/statements row), agent, t, pt_date,
                            goal_no, unit_id, unit2 (51g split at NE43, 2026-08-21), regime, room, holdout, main
                            (not the Claude Code agent or the two fine-tuned leaders), self_repeat (DQ5 bge flag),
                            copy (self_repeat_both), restate (bge | gte), turn_id, ctx_mode, ctx_pos, k_ctx (ledger talk
                            call, nearest t_first within 3 s; null when unmatched), has_code, has_url, s_* (20), tc_* (17)
  style_standardization.json the frozen ruler (winsor bounds, mu, sd, per-regime knots and coefficients, R2)
  style_ne41_pairs.parquet  rule, dedup (time: none / self_repeat; call: copy / restate), agent, pt_date, unit_id,
                            unit2, msg, msg2, srow, srow2, t, gap_s, label, n_forced, n_vol, n_sess

Usage: uv run python infra/shared/style_features.py            (build)
       uv run python infra/shared/style_features.py --verify   (H46 messages + ne41_pairs; H73 messages + its call-rule
                                                                pairs through a read-only import; rule agreement)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT as SH, ROOT, holdout_mask, write_provenance  # noqa: E402

H46 = ROOT / "data/processed/H46-style-conserved-charge"
H73 = ROOT / "data/processed/H73-style-three-components"
STYLE = ["log_chars", "lines", "bullet_share", "headers", "bold", "emoji", "excl", "ques", "urls", "backticks",
         "digit_share", "upper_share", "at", "emdash", "fps", "fpp", "sp", "colon", "word_len", "parens"]
TYPE_COVS = ["log_chars", "backticks", "urls"]           # message-type covariates (length, code, links)
TC = [f for f in STYLE if f not in TYPE_COVS]            # 17 type-controlled features
EXCLUDE_MAIN = {19, 28, 30}                              # Claude Code agent; the two fine-tuned leaders
NE43_DAY = "2026-08-21"
JOIN_TOL = "3s"


# ----------------------------------------------------------------------------- the ruler
def standardize(F: np.ndarray, regime: np.ndarray, meta: dict | None = None):
    """Winsorize + z-score (global) + type control within regime. meta None -> fit (caller passes non-holdout rows
    only); meta given -> apply frozen coefficients. Returns Z (n x 20), TC (n x 17), has_code, has_url, meta."""
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
        knots = np.quantile(lc[ix], [0.25, 0.5, 0.75]) if fit else np.array(info[str(r)]["knots"])
        X = np.column_stack([np.ones(len(ix)), lc[ix]] + [np.maximum(lc[ix] - k, 0) for k in knots]
                            + [has_code[ix], has_url[ix]])
        Y = Z[ix][:, [STYLE.index(f) for f in TC]]
        if fit:
            B, *_ = np.linalg.lstsq(X, Y, rcond=None)
            R = Y - X @ B
            info[str(r)] = {"n": int(len(ix)), "knots": knots.tolist(), "coef": B.tolist(),
                            "r2_by_feature": dict(zip(TC, (1 - R.var(0) / np.maximum(Y.var(0), 1e-12)).round(3).tolist()))}
        else:
            B = np.array(info[str(r)]["coef"])
        TCm[ix] = Y - X @ B
    meta_out = meta or {"winsor_lo": dict(zip(STYLE, lo.tolist())), "winsor_hi": dict(zip(STYLE, hi.tolist())),
                        "mu": dict(zip(STYLE, mu.tolist())), "sd": dict(zip(STYLE, sd.tolist())), "type_control": info}
    return Z, TCm, has_code.astype(bool), has_url.astype(bool), meta_out


# ----------------------------------------------------------------------------- message table
def base_messages() -> pl.DataFrame:
    """Agent chat messages (text_features) with a statement row: srow, regime, DQ5 flags, unit, holdout (all days)."""
    tf = pl.read_parquet(SH / "text_features.parquet",
                         columns=["message_id", "msg", "agent", "t", "pt_date", "goal_no", "room", "holdout"]
                         + [f"f_{f}" for f in STYLE])
    hm = pl.Series(holdout_mask(tf["pt_date"].to_list(), tf["goal_no"].to_list()))
    tf = tf.with_columns((pl.col("holdout") | hm).alias("holdout"))
    st = pl.read_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    smap = (st.filter(pl.col("kind") == "chat").select("srow", "src_row", "regime")
            .join(ci, on="src_row").select("message_id", "srow", "regime"))
    fl = pl.read_parquet(SH / "statement_flags.parquet",
                         columns=["srow", "self_repeat", "self_repeat_both", "self_repeat_bge", "self_repeat_gte"])
    df = tf.join(smap, on="message_id", how="inner").join(fl, on="srow", how="left")
    df = df.with_columns(pl.col("self_repeat").fill_null(False),
                         pl.col("self_repeat_both").fill_null(False).alias("copy"),
                         (pl.col("self_repeat_bge").fill_null(False) | pl.col("self_repeat_gte").fill_null(False)).alias("restate")
                         ).drop("self_repeat_both", "self_repeat_bge", "self_repeat_gte")
    # units by time within goal (H46 / H73 rule); unit2 splits 51g at NE43
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "goal_no", "start").sort("start")
    df = df.sort("t").join_asof(pu.rename({"goal_no": "pu_goal"}), left_on="t", right_on="start", strategy="backward")
    df = df.filter(pl.col("pu_goal") == pl.col("goal_no")).drop("pu_goal", "start")
    df = df.with_columns(pl.when((pl.col("unit_id") == "51g") & (pl.col("pt_date") < NE43_DAY)).then(pl.lit("51g1"))
                         .when(pl.col("unit_id") == "51g").then(pl.lit("51g2"))
                         .otherwise(pl.col("unit_id")).alias("unit2"),
                         (~pl.col("agent").is_in(list(EXCLUDE_MAIN))).alias("main"))
    return df


def attach_calls(df: pl.DataFrame, include_holdout: bool = False) -> pl.DataFrame:
    """H73: the producing ledger talk call (nearest t_first, same agent, within 3 s; summary-mode calls dropped)."""
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("talk"))
          .select("turn_id", "agent", "t_first", "ctx_mode", "ctx_pos", "k_ctx", "holdout").collect())
    if not include_holdout:
        ct = ct.filter(~pl.col("holdout"))
    ct = ct.drop("holdout").sort("t_first")
    out = df.sort("t").join_asof(ct, left_on="t", right_on="t_first", by="agent", strategy="nearest",
                                 tolerance=JOIN_TOL, check_sortedness=False).drop("t_first")
    bad = pl.col("turn_id").is_not_null() & (pl.col("ctx_mode") == "summary")
    return out.with_columns(*[pl.when(bad).then(None).otherwise(pl.col(c)).alias(c)
                              for c in ("turn_id", "ctx_mode", "ctx_pos", "k_ctx")])


def build_messages() -> tuple[pl.DataFrame, dict]:
    df = base_messages()
    # held-out talk calls are attached only to held-out messages (a non-holdout message never joins a held-out call:
    # calls are matched within 3 s of the message, and holdout is a day property)
    df = attach_calls(df, include_holdout=True)
    nh = ~df["holdout"].to_numpy()
    F = df.select([f"f_{f}" for f in STYLE]).to_numpy().astype(np.float64)
    reg = df["regime"].cast(pl.String).to_numpy()
    _, _, _, _, meta = standardize(F[nh], reg[nh])                 # fit on non-holdout rows (H46's population)
    Z, TCm, has_code, has_url, _ = standardize(F, reg, meta)        # apply the frozen ruler to every row
    out = df.select("message_id", "msg", "srow", "agent", "t", "pt_date", "goal_no", "unit_id", "unit2",
                    pl.col("regime").cast(pl.String), "room", "holdout", "main", "self_repeat", "copy", "restate",
                    "turn_id", pl.col("ctx_mode").cast(pl.String), "ctx_pos", "k_ctx").with_columns(
        pl.Series("has_code", has_code), pl.Series("has_url", has_url),
        *[pl.Series(f"s_{f}", Z[:, i].astype(np.float32)) for i, f in enumerate(STYLE)],
        *[pl.Series(f"tc_{f}", TCm[:, i].astype(np.float32)) for i, f in enumerate(TC)])
    return out.sort("t", "msg"), meta


# ----------------------------------------------------------------------------- NE41 pairs
def ne41_pairs_time(msgs: pl.DataFrame, dedup_col: str | None = "self_repeat", include_holdout: bool = False) -> pl.DataFrame:
    """H46 rule. msgs: regime-III main messages (msg, srow, agent, t, pt_date, unit2, dedup_col). Resets are counted by
    time in (t, t2): consolidations by t_log (forced = prev_seg_len in {41, 42}), session resets by t_call."""
    keep_h = pl.lit(True) if include_holdout else ~pl.col("holdout")
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter((pl.col("regime") == "III") & keep_h)
          .select("agent", "pt_date", "t_call", "t_log", "kind", "reset_consol", "reset_session", "prev_seg_len")
          .collect())
    cons = (ct.filter(pl.col("kind") == "consolidate")
            .select("agent", pl.col("t_log").alias("t_r"), pl.col("prev_seg_len").is_in([41, 42]).alias("forced")))
    sess = ct.filter(pl.col("reset_session") & ~pl.col("reset_consol")).select("agent", pl.col("t_call").alias("t_r"))
    mm = msgs.filter(~pl.col(dedup_col)) if dedup_col else msgs
    p = (mm.sort("agent", "t")
         .with_columns(pl.col("msg").shift(-1).over("agent", "pt_date").alias("msg2"),
                       pl.col("srow").shift(-1).over("agent", "pt_date").alias("srow2"),
                       pl.col("t").shift(-1).over("agent", "pt_date").alias("t2"))
         .filter(pl.col("msg2").is_not_null()))
    n_f = np.zeros(p.height, np.int16)
    n_v = np.zeros(p.height, np.int16)
    n_s = np.zeros(p.height, np.int16)
    pa = p["agent"].to_numpy()
    t1 = p["t"].dt.epoch("us").to_numpy()
    t2 = p["t2"].dt.epoch("us").to_numpy()
    for a in np.unique(pa):
        ix = np.where(pa == a)[0]
        c = cons.filter(pl.col("agent") == a)
        tc = c["t_r"].dt.epoch("us").to_numpy()
        fc = c["forced"].to_numpy()
        o = np.argsort(tc)
        tc, fc = tc[o], fc[o]
        cf = np.concatenate([[0], np.cumsum(fc)])
        cv = np.concatenate([[0], np.cumsum(~fc)])
        lo = np.searchsorted(tc, t1[ix], side="right")
        hi = np.searchsorted(tc, t2[ix], side="left")
        n_f[ix] = cf[hi] - cf[lo]
        n_v[ix] = cv[hi] - cv[lo]
        ts = np.sort(sess.filter(pl.col("agent") == a)["t_r"].dt.epoch("us").to_numpy())
        n_s[ix] = np.searchsorted(ts, t2[ix], side="right") - np.searchsorted(ts, t1[ix], side="right")
    lab = np.where((n_f == 0) & (n_v == 0) & (n_s == 0), "within",
                   np.where((n_f == 1) & (n_v == 0) & (n_s == 0), "forced",
                            np.where((n_f == 0) & (n_v == 1) & (n_s == 0), "voluntary", "other")))
    return p.with_columns(pl.Series("label", lab), pl.Series("n_forced", n_f), pl.Series("n_vol", n_v),
                          pl.Series("n_sess", n_s),
                          ((pl.col("t2") - pl.col("t")).dt.total_milliseconds() / 1000.0).cast(pl.Float32).alias("gap_s"))


def ne41_pairs_call(msgs: pl.DataFrame, include_holdout: bool = False) -> pl.DataFrame:
    """H73 rule. msgs: regime-III messages with turn_id (already filtered for main / dedupe as wanted). Returns rows with
    i, i2 = row positions in `msgs`, plus msg/msg2 when present, nf/nv/ns, gap_s, label; pairs inside one call dropped."""
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter((pl.col("regime") == "III") & (pl.lit(include_holdout) | ~pl.col("holdout")))
          .select("turn_id", "agent", "reset_forced", "reset_consol", "reset_session").collect().sort("turn_id"))
    ct = ct.with_columns(
        pl.col("reset_forced").cast(pl.Int32).cum_sum().over("agent").alias("cf"),
        (pl.col("reset_consol") & ~pl.col("reset_forced")).cast(pl.Int32).cum_sum().over("agent").alias("cv"),
        (pl.col("reset_session") & ~pl.col("reset_consol")).cast(pl.Int32).cum_sum().over("agent").alias("cs"))
    mm = msgs.filter(pl.col("regime") == "III").with_row_index("i").sort("agent", "t")
    mm = mm.join(ct.select("turn_id", "cf", "cv", "cs"), on="turn_id", how="left")
    cols = ["i", "t", "cf", "cv", "cs", "turn_id"] + [c for c in ("msg", "srow") if c in mm.columns]
    p = mm.with_columns(*[pl.col(c).shift(-1).over("agent", "pt_date").alias(c + "2") for c in cols]
                        ).filter(pl.col("i2").is_not_null())
    p = p.filter(pl.col("turn_id2") != pl.col("turn_id"))
    p = p.with_columns((pl.col("cf2") - pl.col("cf")).alias("nf"), (pl.col("cv2") - pl.col("cv")).alias("nv"),
                       (pl.col("cs2") - pl.col("cs")).alias("ns"),
                       ((pl.col("t2") - pl.col("t")).dt.total_milliseconds() / 1000.0).alias("gap_s"))
    return p.with_columns(pl.when((pl.col("nf") == 0) & (pl.col("nv") == 0) & (pl.col("ns") == 0)).then(pl.lit("within"))
                          .when((pl.col("nf") == 1) & (pl.col("nv") == 0) & (pl.col("ns") == 0)).then(pl.lit("forced"))
                          .when((pl.col("nf") == 0) & (pl.col("nv") == 1) & (pl.col("ns") == 0)).then(pl.lit("voluntary"))
                          .otherwise(pl.lit("other")).alias("label"))


PAIR_COLS = ["rule", "dedup", "agent", "pt_date", "unit_id", "unit2", "msg", "msg2", "srow", "srow2", "t", "gap_s",
             "label", "n_forced", "n_vol", "n_sess"]


def build_pairs(msgs: pl.DataFrame) -> pl.DataFrame:
    m3 = msgs.filter(~pl.col("holdout") & (pl.col("regime") == "III") & pl.col("main")).sort("agent", "t")
    out = []
    for dedup in ("none", "self_repeat"):
        p = ne41_pairs_time(m3, None if dedup == "none" else "self_repeat")
        out.append(p.with_columns(pl.lit("time").alias("rule"), pl.lit(dedup).alias("dedup"),
                                  pl.col("t").alias("t")).select(PAIR_COLS))
    mc = m3.filter(pl.col("turn_id").is_not_null())
    for dedup in ("copy", "restate"):
        p = ne41_pairs_call(mc.filter(~pl.col(dedup)))
        out.append(p.with_columns(pl.lit("call").alias("rule"), pl.lit(dedup).alias("dedup"),
                                  pl.col("nf").cast(pl.Int16).alias("n_forced"), pl.col("nv").cast(pl.Int16).alias("n_vol"),
                                  pl.col("ns").cast(pl.Int16).alias("n_sess"), pl.col("gap_s").cast(pl.Float32))
                   .select(PAIR_COLS))
    return pl.concat(out, how="vertical_relaxed")


def main():
    msgs, meta = build_messages()
    msgs.write_parquet(SH / "style_messages.parquet", compression="zstd")
    (SH / "style_standardization.json").write_text(json.dumps(meta, indent=1))
    pairs = build_pairs(msgs)
    pairs.write_parquet(SH / "style_ne41_pairs.parquet", compression="zstd")
    nh = msgs.filter(~pl.col("holdout"))
    summ = {"messages": msgs.height, "messages_nonholdout": nh.height, "with_call_nonholdout": int(nh["turn_id"].is_not_null().sum()),
            "pairs": {f"{r}/{d}/{lab}": n for r, d, lab, n in pairs.group_by("rule", "dedup", "label").len()
                      .sort("rule", "dedup", "label").iter_rows()}}
    write_provenance("style_features", ["text_features", "embeddings/statements", "embeddings/chat_index", "statement_flags",
                                        "period_units", "context_ledger_turns"],
                     {"style": STYLE, "type_covariates": TYPE_COVS, "type_controlled": TC, "winsor": [0.001, 0.999],
                      "fit": "non-holdout rows of style_messages (H46's population); applied frozen to held-out rows",
                      "exclude_main": sorted(EXCLUDE_MAIN), "ne43_split": NE43_DAY, "call_join": f"nearest t_first, {JOIN_TOL}",
                      "pairs": "non-holdout only; rule time (H46) and call (H73)",
                      "holdout": "style_messages: all rows flagged; pairs: excluded",
                      "source": "H46 scheme/build.py; H73 scheme/build.py and analysis/h73lib.py:ne41_pairs (rules unchanged)",
                      "summary": summ})
    print(json.dumps(summ, indent=1), flush=True)


# ----------------------------------------------------------------------------- verify
def _maxdiff(a: pl.DataFrame, b: pl.DataFrame, cols: list[str]) -> float:
    return float(max(np.nanmax(np.abs(a[c].to_numpy().astype(np.float64) - b[c].to_numpy().astype(np.float64))) for c in cols))


def verify() -> dict:
    res = {}
    msgs = pl.read_parquet(SH / "style_messages.parquet")
    nh = msgs.filter(~pl.col("holdout"))
    feat = [f"s_{f}" for f in STYLE] + [f"tc_{f}" for f in TC]
    # (1) H46 messages: same rows, keys and flags; style columns equal (shared table is fit on H46's population)
    h46 = pl.read_parquet(H46 / "messages.parquet").sort("t", "msg")
    mine = nh.sort("t", "msg")
    keys = ["msg", "srow", "agent", "t", "pt_date", "goal_no", "unit_id", "unit2", "room", "self_repeat", "main",
            "has_code", "has_url"]
    r = {"rows": [h46.height, mine.height]}
    if h46.height == mine.height:
        r["keys_identical"] = all(h46[c].equals(mine[c]) for c in keys)
        r["style_identical"] = all(h46[c].equals(mine[c]) for c in feat)
        r["style_max_abs_diff"] = _maxdiff(h46, mine, feat)
    res["H46 messages"] = r
    # (2) H73 messages: refit on H73's population (talk-matched, non-summary) must reproduce it; and the shared table's
    #     H46-population ruler differs from H73's by a small amount (reported)
    h73 = pl.read_parquet(H73 / "messages.parquet").sort("t", "msg")
    sub = nh.filter(pl.col("turn_id").is_not_null()).sort("t", "msg")
    r = {"rows": [h73.height, sub.height]}
    if h73.height == sub.height:
        k73 = ["message_id", "msg", "srow", "agent", "unit_id", "main", "copy", "restate", "turn_id", "ctx_mode", "ctx_pos",
               "k_ctx", "has_code", "has_url"]
        r["keys_identical"] = all(h73[c].equals(sub[c]) for c in k73)
        tf = pl.read_parquet(SH / "text_features.parquet", columns=["msg"] + [f"f_{f}" for f in STYLE])
        F = sub.select("msg").join(tf, on="msg", how="left").select([f"f_{f}" for f in STYLE]).to_numpy().astype(np.float64)
        Z, TCm, _, _, _ = standardize(F, sub["regime"].to_numpy())
        refit = pl.DataFrame({**{f"s_{f}": Z[:, i].astype(np.float32) for i, f in enumerate(STYLE)},
                              **{f"tc_{f}": TCm[:, i].astype(np.float32) for i, f in enumerate(TC)}})
        r["refit_identical"] = all(h73[c].equals(refit[c]) for c in feat)
        r["refit_max_abs_diff"] = _maxdiff(h73, refit, feat)
        r["shared_ruler_vs_h73_max_abs_diff"] = _maxdiff(h73, sub, feat)
        r["shared_ruler_vs_h73_median_abs_diff_tc"] = float(np.median(np.abs(
            h73.select([f"tc_{f}" for f in TC]).to_numpy() - sub.select([f"tc_{f}" for f in TC]).to_numpy())))
    res["H73 messages"] = r
    # (3) H46 ne41_pairs (time rule)
    pairs = pl.read_parquet(SH / "style_ne41_pairs.parquet")
    old = pl.read_parquet(H46 / "ne41_pairs.parquet")
    r = {}
    for dedup, d_old in (("self_repeat", True), ("none", False)):
        a = old.filter(pl.col("dedup") == d_old).drop("dedup").sort("agent", "t")
        b = pairs.filter((pl.col("rule") == "time") & (pl.col("dedup") == dedup)).select(a.columns).sort("agent", "t")
        r[dedup] = "identical" if a.equals(b) else {"rows": [a.height, b.height],
                                                     "cols_differ": [c for c in a.columns if a.height == b.height and not a[c].equals(b[c])]}
    res["H46 ne41_pairs"] = r
    # (4) H73 call-rule pairs: read-only import of h73lib.ne41_pairs on H73's own messages, vs this module's function
    import importlib.util
    sys.dont_write_bytecode = True          # read-only import: never write into hypotheses/
    spec = importlib.util.spec_from_file_location("_h73lib_ro", ROOT / "hypotheses/H73-style-three-components/analysis/h73lib.py")
    h73lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h73lib)
    m3 = h73lib.load_messages().filter(pl.col("regime") == "III")
    a = h73lib.ne41_pairs(m3)
    b = ne41_pairs_call(m3).select(a.columns)
    res["H73 ne41_pairs (read-only import)"] = "identical" if a.sort("i").equals(b.sort("i")) else {"rows": [a.height, b.height]}
    sh_call = pairs.filter((pl.col("rule") == "call") & (pl.col("dedup") == "copy"))
    a2 = a.join(m3.with_row_index("i").select("i", "msg"), on="i").join(
        m3.with_row_index("i2").select("i2", pl.col("msg").alias("msg2")), on="i2")
    j = a2.select("msg", "msg2", "label").join(sh_call.select("msg", "msg2", pl.col("label").alias("label_sh")),
                                               on=["msg", "msg2"], how="full", coalesce=True)
    res["H73 pairs vs shared table (call/copy)"] = {
        "h73": a2.height, "shared": sh_call.height, "matched": int(j.filter(pl.col("label").is_not_null() & pl.col("label_sh").is_not_null()).height),
        "label_agree": int((j["label"] == j["label_sh"]).sum())}
    # (5) rule agreement on the same message pairs (copy dedupe vs self_repeat dedupe differ, so join on msg pairs)
    t_ = pairs.filter((pl.col("rule") == "time") & (pl.col("dedup") == "none")).select("msg", "msg2", pl.col("label").alias("lt"))
    c_ = pairs.filter((pl.col("rule") == "call") & (pl.col("dedup") == "copy")).select("msg", "msg2", pl.col("label").alias("lc"))
    jj = t_.join(c_, on=["msg", "msg2"], how="inner")
    res["rule agreement (same msg pairs)"] = {"pairs": jj.height, "agree": int((jj["lt"] == jj["lc"]).sum()),
                                              "crosstab": {f"{x}|{y}": n for x, y, n in jj.group_by("lt", "lc").len().sort("lt", "lc").iter_rows()}}
    # H46's fit summed rows in a different order: float32 outputs may differ by an ulp (tolerance 1e-5)
    res["ok"] = (res["H46 messages"].get("keys_identical") and res["H46 messages"].get("style_max_abs_diff", 1.0) < 1e-5
                 and res["H73 messages"].get("keys_identical") and res["H73 messages"].get("refit_identical")
                 and all(v == "identical" for v in res["H46 ne41_pairs"].values())
                 and res["H73 ne41_pairs (read-only import)"] == "identical")
    print(json.dumps(res, indent=1, default=str), flush=True)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify()["ok"] else 1)
    main()
