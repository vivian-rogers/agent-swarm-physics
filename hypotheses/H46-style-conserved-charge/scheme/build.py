"""H46 scheme: per-message style table, boundary catalog and NE41 message-pair table (no text; holdout dropped).

Inputs (data/processed/shared/): text_features (H13's 20 style features), embeddings/statements + chat_index (row map
to the shared content vectors), statement_flags (DQ5 self_repeat, bge rule), period_units, calendar,
context_ledger_turns (DQ1 reset flags), roster.
Outputs (data/processed/H46-style-conserved-charge/):
  messages.parquet    one row per non-holdout agent chat message: keys, srow (row in embeddings/statements and the
                      DQ5 .npy files), unit / unit2 (unit2 splits 51g at NE43, 2026-08-21), self_repeat, main flag,
                      s_* (20 standardized style features), tc_* (17 type-controlled style features), has_code, has_url
  boundaries.parquet  day-level boundary catalog (class, NE id, pre / post units)
  ne41_pairs.parquet  consecutive eligible chat messages of one agent on one PT day in regime III, labelled
                      forced / voluntary / within by the resets between them
Usage: uv run python hypotheses/H46-style-conserved-charge/scheme/build.py
"""
from __future__ import annotations
import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
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
OUT = ROOT / "data/processed/H46-style-conserved-charge"
STYLE = ["log_chars", "lines", "bullet_share", "headers", "bold", "emoji", "excl", "ques", "urls", "backticks",
         "digit_share", "upper_share", "at", "emdash", "fps", "fpp", "sp", "colon", "word_len", "parens"]
TYPE_COVS = ["log_chars", "backticks", "urls"]           # message-type covariates (length, code, links)
TC = [f for f in STYLE if f not in TYPE_COVS]            # 17 type-controlled features
EXCLUDE_MAIN = {19, 28, 30}                              # Claude Code agent; the two fine-tuned leaders
NE43_DAY = "2026-08-21"


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    d = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H46-style-conserved-charge"],
                       capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if d.strip() else "")


def build_messages() -> pl.DataFrame:
    tf = pl.read_parquet(SH / "text_features.parquet",
                         columns=["message_id", "msg", "agent", "t", "pt_date", "goal_no", "room", "holdout"]
                         + [f"f_{f}" for f in STYLE])
    tf = tf.filter(~pl.col("holdout"))
    tf = tf.filter(pl.Series(holdout_mask(tf["pt_date"].to_list(), tf["goal_no"].to_list())).not_())
    # row map: message_id -> statements row (srow)
    st = pl.read_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    smap = (st.filter(pl.col("kind") == "chat").select("srow", "src_row", "regime")
            .join(ci, on="src_row").select("message_id", "srow", "regime"))
    fl = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", "self_repeat"])
    df = tf.join(smap, on="message_id", how="inner").join(fl, on="srow", how="left")
    print(f"messages: {tf.height:,} non-holdout; {df.height:,} with a statement row", flush=True)

    # units (period_units), assigned by time within goal; unit2 splits 51g at NE43
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout")).select(
        "unit_id", "goal_no", "start").sort("start")
    df = df.sort("t").join_asof(pu.rename({"goal_no": "pu_goal"}), left_on="t", right_on="start", strategy="backward")
    bad = df.filter(pl.col("pu_goal") != pl.col("goal_no")).height
    if bad:
        print(f"  warning: {bad} rows with unit goal != message goal (dropped)")
    df = df.filter(pl.col("pu_goal") == pl.col("goal_no")).drop("pu_goal", "start")
    df = df.with_columns(pl.when((pl.col("unit_id") == "51g") & (pl.col("pt_date") < NE43_DAY)).then(pl.lit("51g1"))
                         .when(pl.col("unit_id") == "51g").then(pl.lit("51g2"))
                         .otherwise(pl.col("unit_id")).alias("unit2"))
    df = df.with_columns((~pl.col("agent").is_in(list(EXCLUDE_MAIN))).alias("main"),
                         pl.col("self_repeat").fill_null(False))

    # style standardization: winsorize at non-holdout 0.1/99.9% quantiles, z-score (global ruler)
    F = df.select([f"f_{f}" for f in STYLE]).to_numpy().astype(np.float64)
    lo, hi = np.quantile(F, 0.001, axis=0), np.quantile(F, 0.999, axis=0)
    Fw = np.clip(F, lo, hi)
    mu, sd = Fw.mean(0), Fw.std(0)
    sd[sd == 0] = 1.0
    Z = (Fw - mu) / sd
    has_code = (F[:, STYLE.index("backticks")] > 0).astype(np.float64)
    has_url = (F[:, STYLE.index("urls")] > 0).astype(np.float64)
    # type control within regime: OLS of the 17 other z-features on a log_chars spline + has_code + has_url
    lc = F[:, STYLE.index("log_chars")]
    TCm = np.zeros((len(df), len(TC)))
    reg = df["regime"].to_numpy()
    fit_info = {}
    for r in np.unique(reg):
        ix = np.where(reg == r)[0]
        knots = np.quantile(lc[ix], [0.25, 0.5, 0.75])
        X = np.column_stack([np.ones(len(ix)), lc[ix]] + [np.maximum(lc[ix] - k, 0) for k in knots]
                            + [has_code[ix], has_url[ix]])
        Y = Z[ix][:, [STYLE.index(f) for f in TC]]
        B, *_ = np.linalg.lstsq(X, Y, rcond=None)
        R = Y - X @ B
        TCm[ix] = R
        fit_info[str(r)] = {"n": int(len(ix)), "knots": knots.tolist(), "coef": B.tolist(),
                            "r2_by_feature": dict(zip(TC, (1 - R.var(0) / np.maximum(Y.var(0), 1e-12)).round(3).tolist()))}
    cols = {f"s_{f}": Z[:, i].astype(np.float32) for i, f in enumerate(STYLE)}
    cols.update({f"tc_{f}": TCm[:, i].astype(np.float32) for i, f in enumerate(TC)})
    out = df.select("msg", "srow", "agent", "t", "pt_date", "goal_no", "unit_id", "unit2", "regime", "room",
                    "self_repeat", "main").with_columns(
        pl.Series("has_code", has_code.astype(bool)), pl.Series("has_url", has_url.astype(bool)),
        *[pl.Series(k, v) for k, v in cols.items()])
    meta = {"winsor_lo": dict(zip(STYLE, lo.tolist())), "winsor_hi": dict(zip(STYLE, hi.tolist())),
            "mu": dict(zip(STYLE, mu.tolist())), "sd": dict(zip(STYLE, sd.tolist())), "type_control": fit_info}
    return out, meta


def boundary_catalog(units: pl.DataFrame) -> pl.DataFrame:
    """Day-level boundaries: class, ne, label, pre units, post units, flag (all non-holdout)."""
    u = units.filter(~pl.col("holdout"))
    by_goal: dict[int, list[str]] = {}
    for r in u.sort("start").iter_rows(named=True):
        by_goal.setdefault(r["goal_no"], []).append(r["unit_id"])
    rows = []

    def add(cls, ne, label, pre, post, flag=""):
        rows.append({"cls": cls, "ne": ne, "label": label, "pre": pre, "post": post, "flag": flag})

    goals = sorted(by_goal)
    adjacent = [(g, g + 1) for g in goals if g + 1 in by_goal and g != 51]
    rooms_pairs = {(39, 40): "NE42 merge", (40, 41): "NE42 split"}
    for g, h in adjacent:
        if (g, h) in rooms_pairs:
            add("rooms", "NE42", f"{g}->{h} ({rooms_pairs[(g, h)]})", by_goal[g], by_goal[h], "goal-confounded")
        else:
            flag = "roster-confounded (NE28)" if (g, h) == (20, 21) else ""
            add("goal", "NE34", f"{g}->{h}", by_goal[g], by_goal[h], flag)
    for g, h in [(8, 10), (21, 23), (42, 44)]:       # skip one held-out goal, no NE window: sensitivity
        add("goal_skip", "NE34", f"{g}->{h}", by_goal[g], by_goal[h], "skips a held-out goal")
    # rooms inside #51 (#focus opened 08-05, closed 08-24)
    add("rooms", "NE42", "51f->51g (#focus opened)", ["51f"], ["51g1", "51g2"], "#51 room set change")
    add("rooms", "NE42", "51g->51h (#focus closed)", ["51g1", "51g2"], ["51h"], "#51 room set change")
    add("nudger", "NE43", "51g: 08-20 -> 08-21 (nudger off)", ["51g1"], ["51g2"], "")
    roster = [("4a", "4b", ""), ("4b", "4c", ""), ("18a", "18b", ""), ("18b", "18c", ""), ("19a", "19b", ""),
              ("20a", "20b", ""), ("31a", "31b", ""), ("31b", "31c", "NE29"), ("38b", "38c", ""), ("38d", "38e", ""),
              ("42a", "42b", ""), ("44a", "44b", "leader joins"), ("51a", "51b", "NE32"), ("51b", "51c", ""),
              ("51c", "51d", ""), ("51d", "51e", ""), ("51h", "51i", ""), ("51i", "51j", ""), ("51j", "51k", "NE33"),
              ("51k", "51l", "NE33")]
    for a, b, f in roster:
        add("roster", f if f.startswith("NE") else "NE32", f"{a}->{b}", [a], [b], f)
    scaffold = [("6a", "6b", "NE02", ""), ("10a", "10b", "NE03", ""), ("12a", "12b", "NE04", ""),
                ("20b", "20c", "NE06", ""), ("20c", "20d", "NE06", "with a roster join"),
                ("21a", "21b", "NE07", "with a roster join"), ("30a", "30b", "NE10", ""), ("31c", "31d", "NE11", ""),
                ("36a", "36b", "NE14", "regime II->III; content in raw bge space"), ("36b", "36c", "NE16", ""),
                ("38a", "38b", "NE17", ""), ("38c", "38d", "NE18", "")]
    for a, b, ne, f in scaffold:
        add("scaffold", ne, f"{a}->{b} ({ne})", [a], [b], f)
    return pl.DataFrame(rows)


def ne41_pairs(msgs: pl.DataFrame) -> pl.DataFrame:
    """Consecutive eligible chat messages (same agent, PT day, regime III), labelled by resets between them."""
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter((pl.col("regime") == "III") & ~pl.col("holdout"))
          .select("agent", "pt_date", "t_call", "t_log", "kind", "reset_consol", "reset_session", "prev_seg_len")
          .collect())
    cons = (ct.filter(pl.col("kind") == "consolidate")
            .select("agent", pl.col("t_log").alias("t_r"), pl.col("prev_seg_len").is_in([41, 42]).alias("forced")))
    sess = (ct.filter(pl.col("reset_session") & ~pl.col("reset_consol"))
            .select("agent", pl.col("t_call").alias("t_r")))
    m = (msgs.filter((pl.col("regime") == "III") & pl.col("main"))
         .select("msg", "srow", "agent", "t", "pt_date", "unit2", "self_repeat").sort("agent", "t"))
    res = []
    for dedup in (True, False):
        mm = m.filter(~pl.col("self_repeat")) if dedup else m
        p = (mm.with_columns(pl.col("msg").shift(-1).over("agent", "pt_date").alias("msg2"),
                             pl.col("srow").shift(-1).over("agent", "pt_date").alias("srow2"),
                             pl.col("t").shift(-1).over("agent", "pt_date").alias("t2"))
             .filter(pl.col("msg2").is_not_null()))
        p = p.with_row_index("pid")
        # count resets in (t, t2) per pair via sorted search per agent
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
        p = p.with_columns(pl.Series("label", lab), pl.Series("n_forced", n_f), pl.Series("n_vol", n_v),
                           pl.Series("n_sess", n_s), ((pl.col("t2") - pl.col("t")).dt.total_milliseconds() / 1000.0)
                           .cast(pl.Float32).alias("gap_s"), pl.lit(dedup).alias("dedup"))
        res.append(p.select("dedup", "agent", "pt_date", "unit2", "msg", "srow", "msg2", "srow2", "t", "gap_s",
                            "label", "n_forced", "n_vol", "n_sess"))
    return pl.concat(res)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    msgs, meta = build_messages()
    msgs.write_parquet(OUT / "messages.parquet", compression="zstd")
    (OUT / "style_standardization.json").write_text(json.dumps(meta, indent=1))
    print(f"messages.parquet: {msgs.height:,} rows; main {msgs['main'].sum():,}; self_repeat "
          f"{msgs['self_repeat'].mean():.3f}", flush=True)
    units = pl.read_parquet(SH / "period_units.parquet")
    bc = boundary_catalog(units)
    bc.write_parquet(OUT / "boundaries.parquet")
    print(bc.group_by("cls").len().sort("cls"))
    pr = ne41_pairs(msgs)
    pr.write_parquet(OUT / "ne41_pairs.parquet", compression="zstd")
    print(pr.group_by("dedup", "label").len().sort("dedup", "label"))
    prov = {"built_by": "hypotheses/H46-style-conserved-charge/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/text_features", "shared/embeddings/statements", "shared/embeddings/chat_index",
                                   "shared/statement_flags", "shared/period_units", "shared/context_ledger_turns"]}],
            "params": {"style": STYLE, "type_covariates": TYPE_COVS, "type_controlled": TC,
                       "winsor": [0.001, 0.999], "exclude_main": sorted(EXCLUDE_MAIN), "ne43_split": NE43_DAY,
                       "self_repeat": "DQ5 statement_flags.self_repeat (bge cos > 0.95, same agent, PT day, earlier)",
                       "forced": "consolidate row prev_seg_len in {41, 42} (DQ1 rule)",
                       "holdout": "calendar holdout flag and common.holdout_mask"},
            "built_at": dt.datetime.now(dt.UTC).isoformat()}
    old = json.loads((OUT / "_provenance.json").read_text()) if (OUT / "_provenance.json").exists() else {}
    if "analysis" in old:   # keep the analysis-output map written after round 1
        prov["analysis"] = old["analysis"]
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
