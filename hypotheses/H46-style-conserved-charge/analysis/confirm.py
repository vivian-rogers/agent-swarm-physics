"""H46 confirmatory test on the locked holdout. WRITTEN 2026-10-04 after round 1, NOT RUN on the holdout.

  uv run python hypotheses/H46-style-conserved-charge/analysis/confirm.py --dry-run
      runs the full pipeline on non-holdout stand-ins (safe; exploration data only)
  uv run python hypotheses/H46-style-conserved-charge/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      builds the held-out message table in memory (text_features rows with holdout == True, frozen round-1
      standardization and type-control coefficients from style_standardization.json), scores the frozen predictions.
      Refuses to run without BOTH flags. Writes confirm/confirm_sealed.json (SHA-256 of the frozen predictions) BEFORE
      touching any held-out row, then confirm/confirm_results.json.

Round 1 refuted strict conservation; the frozen predictions test the round-1 picture instead ("quasi-conserved
charge"): style = agent charge (substrate) + a context-held excitation that grows with context length and is erased
at resets + a register response; goal quenches shift style by a fraction of content's shift; identity survives.

Targets (locked holdout):
  T1 #51 tail (09-07 -> 09-18)            fingerprint transfer and in-context drift
  T2 held-out goal switches               8->9, 9->10, 13->14, 14->15, 15->16, 21->22, 22->23, 27->28, 28->29, 29->30,
                                          42->43, 43->44, 44->45, 45->46, 46->47, 47->48, 48->49, 49->50, 50->51
  T3 NE41 in held-out regime-III days     #43, #45-#50, #51 tail
  T4 rooms: NE15 (33/34 -> 35 split, 03-16) and NE12 (02-25 rooms, inside #32; 32a -> 32b)
  T5 NE30 same-family succession (Gemini 3 Pro -> 3.1 Pro, 03-09)
  T6 NE23 nudger off (46c -> 46d, 06-13; the other NE21/NE23 switches coincide with goal changes and are left out)
Frozen predictions:
  C1 (T1) style balanced accuracy (train: each agent's last <= 3 eligible days before 09-07; test: first <= 3 tail
     days; day-demeaned) >= 5x chance.
  C2 (T2) pooled class: style T_s in [0.55, 0.85] with randomization p < 0.05 (style moves), content T_c >= T_s + 0.10;
     style cross-boundary accuracy > content's at >= 2/3 of boundaries with >= 3 agents.
  C3 (T3) forced erasures: style T_s >= 0.53 with agent-cluster CI lower bound > 0.5; T_s - T_c >= 0.02.
  C4 (T1 + T3 days) in-context drift: within segments of >= 7 messages, style excess distance at positions 7+ minus
     position 1 > 0 (bootstrap over agents, 95% CI excludes 0).
  C5 (T4) content T_c > 0.60 and T_s < T_c (both boundaries pooled).
  C6 (T5, descriptive) Gemini 3.1 Pro's first <= 3 eligible days: Gemini 3 Pro within the 3 nearest style centroids.
  C7 (T6) style T_s <= 0.62 at the nudger switch-off (no register change).
  Overall: the quasi-conserved picture is CONFIRMED if C1, C2, C3 and C4 pass.
Reuse disclosure (policy in hypotheses/holdout.md): the #51 tail is also targeted by unrun scripts of H14, H18, H20,
H22 and H34; #45 by H02 (activity timing, run) and H23 (leader content copying, unrun); #34 by six scripts. H46's
observables (per-agent style-feature displacement against own placebo transitions; gap-matched erasure pairs) are
different statistics. Disclose in both cards and LOG.md if run.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h46lib as L  # noqa: E402

OUTD = L.DATA / "confirm"
PRED = {"C1": "style acc >= 5x chance (T1)", "C2": "T_s in [0.55,0.85], p<0.05; T_c >= T_s+0.10; style>content fp at >= 2/3 (T2)",
        "C3": "forced erasure T_s >= 0.53, lo > 0.5; T_s - T_c >= 0.02 (T3)", "C4": "drift pos7+ - pos1 > 0, CI excludes 0",
        "C5": "rooms T_c > 0.60 and T_s < T_c (T4)", "C6": "Gemini 3 Pro in 3 nearest style centroids of 3.1 Pro (descr.)",
        "C7": "nudger-off switch T_s <= 0.62 (T6)", "overall": "C1 & C2 & C3 & C4"}
GOAL_SWITCHES = [(8, 9), (9, 10), (13, 14), (14, 15), (15, 16), (21, 22), (22, 23), (27, 28), (28, 29), (29, 30),
                 (42, 43), (43, 44), (44, 45), (45, 46), (46, 47), (47, 48), (48, 49), (49, 50), (50, 51)]


def frozen_messages(include_holdout: bool) -> pl.DataFrame:
    """All-day message table with the round-1 frozen standardization (only called under --confirm)."""
    meta = json.loads((L.DATA / "style_standardization.json").read_text())
    tf = pl.read_parquet(L.SH / "text_features.parquet")
    if not include_holdout:
        tf = tf.filter(~pl.col("holdout"))
    st = pl.read_parquet(L.SH / "embeddings/statements.parquet").with_row_index("srow")
    ci = pl.read_parquet(L.SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    smap = st.filter(pl.col("kind") == "chat").select("srow", "src_row", "regime").join(ci, on="src_row")
    fl = pl.read_parquet(L.SH / "statement_flags.parquet", columns=["srow", "self_repeat"])
    df = tf.join(smap.select("message_id", "srow", "regime"), on="message_id").join(fl, on="srow", how="left")
    pu = pl.read_parquet(L.SH / "period_units.parquet").select("unit_id", "goal_no", "start").sort("start")
    df = df.sort("t").join_asof(pu.rename({"goal_no": "pu_goal"}), left_on="t", right_on="start", strategy="backward")
    df = df.filter(pl.col("pu_goal") == pl.col("goal_no")).with_columns(pl.col("unit_id").alias("unit2"))
    F = df.select([f"f_{f}" for f in L.STYLE]).to_numpy().astype(float)
    lo = np.array([meta["winsor_lo"][f] for f in L.STYLE])
    hi = np.array([meta["winsor_hi"][f] for f in L.STYLE])
    mu = np.array([meta["mu"][f] for f in L.STYLE])
    sd = np.array([meta["sd"][f] for f in L.STYLE])
    Z = (np.clip(F, lo, hi) - mu) / sd
    lc = F[:, L.STYLE.index("log_chars")]
    hc = (F[:, L.STYLE.index("backticks")] > 0).astype(float)
    hu = (F[:, L.STYLE.index("urls")] > 0).astype(float)
    TCm = np.zeros((len(df), len(L.TC)))
    reg = df["regime"].to_numpy()
    for r in np.unique(reg):
        ix = np.where(reg == r)[0]
        tcm = meta["type_control"][str(r)]
        X = np.column_stack([np.ones(len(ix)), lc[ix]] + [np.maximum(lc[ix] - k, 0) for k in tcm["knots"]] + [hc[ix], hu[ix]])
        TCm[ix] = Z[ix][:, [L.STYLE.index(f) for f in L.TC]] - X @ np.array(tcm["coef"])
    out = df.select("msg", "srow", "agent", "t", "pt_date", "goal_no", "unit_id", "unit2", "regime", "room",
                    pl.col("self_repeat").fill_null(False), "holdout").with_columns(
        (~pl.col("agent").is_in([19, 28, 30])).alias("main"),
        *[pl.Series(f"s_{f}", Z[:, i].astype(np.float32)) for i, f in enumerate(L.STYLE)],
        *[pl.Series(f"tc_{f}", TCm[:, i].astype(np.float32)) for i, f in enumerate(L.TC)])
    return out.filter(pl.col("main") & ~pl.col("self_repeat")).sort("agent", "pt_date", "t")


def goal_bounds(pairs, units: pl.DataFrame) -> pl.DataFrame:
    by = {}
    for r in units.sort("start").iter_rows(named=True):
        by.setdefault(r["goal_no"], []).append(r["unit_id"])
    return pl.DataFrame([{"cls": "goal", "ne": "NE34", "label": f"{g}->{h}", "pre": by[g], "post": by[h], "flag": ""}
                         for g, h in pairs if g in by and h in by])


def fp_class(dt_, bounds):
    res = []
    for b in bounds.iter_rows(named=True):
        fs = L.fingerprint_boundary(dt_, "style_dm", set(b["pre"]), set(b["post"]))
        fc = L.fingerprint_boundary(dt_, "content_dm", set(b["pre"]), set(b["post"]))
        if "cross" in fs:
            res.append((fs["cross"], fc["cross"], fs["chance"]))
    return res


def score(m: pl.DataFrame, cfg: dict) -> dict:
    mats = {"style": L.style_matrix(m, "tc"), "content": L.content_matrix(m, "resid")}
    dt_ = L.day_table(m, mats)
    L.add_demeaned(dt_, ["style", "content"])
    fd = L.unit_first_days()
    units = pl.read_parquet(L.SH / "period_units.parquet")
    out = {}
    # C1 fingerprint transfer
    k = dt_.keys
    pre, post = set(cfg["T1_pre_units"]), set(cfg["T1_post_units"])
    r1 = L.fingerprint_boundary(dt_, "style_dm", pre, post)
    r1c = L.fingerprint_boundary(dt_, "content_dm", pre, post)
    out["C1"] = {"style": r1, "content": r1c, "pass": bool(r1.get("cross", 0) >= 5 * r1.get("chance", 1))}
    # C2 goal switches
    gb = goal_bounds(cfg["T2_pairs"], units)
    rows = L.eval_boundaries(gb, dt_, {"style": "style", "content": "content"}, fd)
    ts, tc = L.class_test(rows, "style"), L.class_test(rows, "content")
    fps = fp_class(dt_, gb)
    share = float(np.mean([s > c for s, c, _ in fps])) if fps else np.nan
    out["C2"] = {"style": {k_: v for k_, v in ts.items() if k_ != "per_boundary"},
                 "content": {k_: v for k_, v in tc.items() if k_ != "per_boundary"}, "share_style_gt_content": share,
                 "pass": bool(0.55 <= ts.get("T", 0) <= 0.85 and ts.get("p_rand", 1) < 0.05
                              and tc.get("T", 0) >= ts.get("T", 1) + 0.10 and share >= 2 / 3)}
    # C5 rooms, C7 hours / nudger
    for key, pairs in (("C5", cfg["T4_units"]), ("C7", cfg["T6_units"])):
        b = pl.DataFrame([{"cls": key, "ne": key, "label": f"{a}->{c}", "pre": [a], "post": [c], "flag": ""} for a, c in pairs])
        rr = L.eval_boundaries(b, dt_, {"style": "style", "content": "content"}, fd)
        ts_, tc_ = L.class_test(rr, "style"), L.class_test(rr, "content")
        out[key] = {"style_T": ts_.get("T"), "content_T": tc_.get("T"), "n": ts_.get("n")}
        out[key]["pass"] = bool((tc_.get("T", 0) > 0.60 and ts_.get("T", 1) < tc_.get("T", 0)) if key == "C5"
                                else (ts_.get("T", 1) <= 0.62))
    return out


def ne41_score(m: pl.DataFrame, days: set) -> dict:
    """C3 and C4 on the given PT days (regime III)."""
    mm = m.filter(pl.col("pt_date").is_in(list(days)) & (pl.col("regime") == "III")).with_columns(pl.lit(True).alias("main"))
    ct = (pl.scan_parquet(L.SH / "context_ledger_turns.parquet").filter(pl.col("pt_date").is_in(list(days)))
          .select("agent", "pt_date", "t_call", "t_log", "kind", "reset_consol", "reset_session", "prev_seg_len").collect())
    cons = ct.filter(pl.col("kind") == "consolidate").select("agent", pl.col("t_log").alias("t_r"),
                                                            pl.col("prev_seg_len").is_in([41, 42]).alias("forced"))
    sess = ct.filter(pl.col("reset_session") & ~pl.col("reset_consol")).select("agent", pl.col("t_call").alias("t_r"))
    p = (mm.sort("agent", "t").with_columns(pl.col("msg").shift(-1).over("agent", "pt_date").alias("msg2"),
                                            pl.col("t").shift(-1).over("agent", "pt_date").alias("t2"))
         .filter(pl.col("msg2").is_not_null()))
    pa, t1, t2 = p["agent"].to_numpy(), p["t"].dt.epoch("us").to_numpy(), p["t2"].dt.epoch("us").to_numpy()
    nf, nv, ns = (np.zeros(p.height, int) for _ in range(3))
    for a in np.unique(pa):
        ix = np.where(pa == a)[0]
        c = cons.filter(pl.col("agent") == a).sort("t_r")
        tc_, fc = c["t_r"].dt.epoch("us").to_numpy(), c["forced"].to_numpy()
        cf, cv = np.concatenate([[0], np.cumsum(fc)]), np.concatenate([[0], np.cumsum(~fc)])
        lo, hi = np.searchsorted(tc_, t1[ix], "right"), np.searchsorted(tc_, t2[ix], "left")
        nf[ix], nv[ix] = cf[hi] - cf[lo], cv[hi] - cv[lo]
        ts_ = np.sort(sess.filter(pl.col("agent") == a)["t_r"].dt.epoch("us").to_numpy())
        ns[ix] = np.searchsorted(ts_, t2[ix], "right") - np.searchsorted(ts_, t1[ix], "right")
    lab = np.where((nf == 0) & (nv == 0) & (ns == 0), "within", np.where((nf == 1) & (nv == 0) & (ns == 0), "forced", "other"))
    idx = {k_: i for i, k_ in enumerate(mm["msg"].to_list())}
    i1 = np.array([idx[k_] for k_ in p["msg"].to_list()])
    i2 = np.array([idx[k_] for k_ in p["msg2"].to_list()])
    Xs, Xc = L.style_matrix(mm, "tc"), L.content_matrix(mm, "resid")
    gap = np.maximum((t2 - t1) / 1e6, 1.0)
    gb = np.floor(np.log10(gap) / L.GAP_BIN).astype(int)
    un = p["unit2"].to_numpy()
    S1 = np.array([f"{a}|{u}|{g}" for a, u, g in zip(pa, un, gb)])
    S2 = np.array([f"{u}|{g}" for u, g in zip(un, gb)])
    ds = ((Xs[i1] - Xs[i2]) ** 2).sum(1)
    dc = 1 - (Xc[i1] * Xc[i2]).sum(1)
    ps_, nps = L.pair_percentiles(lab, ds, S1, S2)
    pc_, npc = L.pair_percentiles(lab, dc, S1, S2)
    f = lab == "forced"
    ts, tc = L.mean_pct_test(ps_[f], nps[f], pa[f]), L.mean_pct_test(pc_[f], npc[f], pa[f])
    c3 = bool(ts.get("T", 0) >= 0.53 and ts.get("lo", 0) > 0.5 and ts.get("T", 0) - tc.get("T", 1) >= 0.02)
    # C4 drift: positions since last reset within segments >= 7 messages
    tt = mm["t"].dt.epoch("us").to_numpy()
    ag = mm["agent"].to_numpy()
    seg = np.zeros(len(mm), np.int64)
    allr = pl.concat([cons.select("agent", "t_r"), sess])
    for a in np.unique(ag):
        ix = np.where(ag == a)[0]
        seg[ix] = np.searchsorted(np.sort(allr.filter(pl.col("agent") == a)["t_r"].dt.epoch("us").to_numpy()), tt[ix], "right")
    q = mm.with_columns(pl.Series("seg", seg)).with_row_index("i")
    q = q.with_columns(pl.col("i").rank("ordinal").over("agent", "pt_date", "seg").alias("pos"),
                       pl.len().over("agent", "pt_date", "seg").alias("seglen"))
    key = (q["agent"].cast(pl.Utf8) + "|" + q["unit2"]).to_numpy()
    _, inv = np.unique(key, return_inverse=True)
    S = np.zeros((inv.max() + 1, Xs.shape[1]))
    np.add.at(S, inv, Xs)
    d = ((Xs - (S / np.bincount(inv)[:, None])[inv]) ** 2).sum(1)
    sk = (q["agent"].cast(pl.Utf8) + "|" + q["pt_date"] + "|" + q["seg"].cast(pl.Utf8)).to_numpy()
    _, sinv = np.unique(sk, return_inverse=True)
    dsg = d - (np.bincount(sinv, weights=d) / np.bincount(sinv))[sinv]
    pos, sl = q["pos"].to_numpy(), q["seglen"].to_numpy()
    rng = np.random.default_rng(0)
    diffs = []
    agents = np.unique(ag[sl >= 7])
    for _ in range(1000):
        aa = rng.choice(agents, len(agents))
        sel = np.concatenate([np.where((ag == a) & (sl >= 7))[0] for a in aa])
        diffs.append(dsg[sel][pos[sel] >= 7].mean() - dsg[sel][pos[sel] == 1].mean())
    lo4, hi4 = np.quantile(diffs, [0.025, 0.975])
    return {"C3": {"style": ts, "content": tc, "n_forced": int(f.sum()), "pass": c3},
            "C4": {"diff_mean": float(np.mean(diffs)), "lo": float(lo4), "hi": float(hi4), "pass": bool(lo4 > 0)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    if a.confirm and not a.ack:
        sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
    if a.confirm:
        sealed = {"predictions": PRED, "sha256": hashlib.sha256(json.dumps(PRED, sort_keys=True).encode()).hexdigest(),
                  "sealed_at": dt.datetime.now(dt.UTC).isoformat()}
        (OUTD / "confirm_sealed.json").write_text(json.dumps(sealed, indent=1))
        m = frozen_messages(include_holdout=True)
        cfg = {"T1_pre_units": ["51h", "51i", "51j", "51k", "51l"], "T1_post_units": ["51m"], "T2_pairs": GOAL_SWITCHES,
               "T4_units": [("34d", "35"), ("32a", "32b")], "T6_units": [("46c", "46d")]}
        days = set(m.filter(pl.col("holdout") & (pl.col("regime") == "III"))["pt_date"].unique().to_list())
        res = score(m, cfg)
        res.update(ne41_score(m, days))
        res["C6"] = {"note": "computed by hand from the frozen centroids if run; descriptive"}
        res["overall"] = bool(all(res[c]["pass"] for c in ("C1", "C2", "C3", "C4")))
        (OUTD / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps({k: v.get("pass") if isinstance(v, dict) else v for k, v in res.items()}, indent=1))
        return
    if not a.dry_run:
        sys.exit("use --dry-run, or --confirm --i-understand-this-uses-the-locked-holdout")
    # dry run on non-holdout stand-ins: T1 <- #51 before/after 08-24; T2 <- four round-1 goal switches; T3/T4 <- 51h-51l
    m = L.load_messages()
    cfg = {"T1_pre_units": ["51g1", "51g2"], "T1_post_units": ["51h"], "T2_pairs": [(36, 37), (37, 38), (38, 39), (41, 42)],
           "T4_units": [("51f", "51g1")], "T6_units": [("30a", "30b"), ("51g1", "51g2")]}
    res = score(m, cfg)
    days = set(m.filter(pl.col("unit2").is_in(["51h", "51i", "51j", "51k", "51l"]))["pt_date"].unique().to_list())
    res.update(ne41_score(m, days))
    res["stand_ins"] = cfg
    (OUTD / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: (v.get("pass") if isinstance(v, dict) and "pass" in v else "-") for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    main()
