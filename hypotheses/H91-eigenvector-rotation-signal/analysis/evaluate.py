"""H91 evaluation: trailing alarms, the goal-kickoff event study against H36's placebo days, the rival comparison with
R1 (H36 round 1b) and H74's fused detector, stationarity between events (P2), rooms (P3), robustness (P4-P6) and the
per-period replication table.

Inputs: rotation.parquet (run_rotation.py), rooms.parquet (scheme), H36 r1b design read as data
(r1b/fixed_bge_none/{events,scores}.parquet: catalog, day order, placebo flags, R1 bge; r1b/fixed_gte_restate/
scores.parquet: R1 gte), H74 scores.parquet (z_F fused, z_C).
Outputs: data/processed/H91-eigenvector-rotation-signal/{days_scored.parquet, periods.parquet, eval/results.json}
Usage: uv run python hypotheses/H91-eigenvector-rotation-signal/analysis/evaluate.py
"""
from __future__ import annotations

import json

import numpy as np
import polars as pl

import h91lib as L

DM = L.DM
H36 = L.ROOT / "data/processed/H36-reorganization-alarm/r1b"
H74 = L.ROOT / "data/processed/H74-change-detector/scores.parquet"
PRIMARY = "z2_boot"
CONTENT = ["content_bge", "content_gte"]
VARIANTS = {"style": ["content_bge_style_resid_period", "content_gte_style_resid_period"],
            "restate": ["content_bge_restate", "content_gte_restate"]}


def day_table() -> pl.DataFrame:
    s = pl.read_parquet(H36 / "fixed_bge_none/scores.parquet").select(
        "aday", "pt_date", "goal_no", "regime", "monday", "placebo", "dist_event", pl.col("R1").alias("R1_bge"),
        pl.col("Z_cont").alias("Zcont_bge"))
    g = pl.read_parquet(H36 / "fixed_gte_restate/scores.parquet").select("pt_date", pl.col("R1").alias("R1_gte"))
    d = s.join(g, on="pt_date", how="left").sort("aday")
    d = d.with_columns(pl.mean_horizontal("R1_bge", "R1_gte").alias("R1m"))
    if H74.exists():
        h = pl.read_parquet(H74).select("pt_date", pl.col("z_F").alias("H74_F"), pl.col("z_C").alias("H74_C"))
        d = d.join(h, on="pt_date", how="left")
    rot = pl.read_parquet(L.OUT / "rotation.parquet")
    for ch in rot["channel"].unique().to_list():
        x = rot.filter(pl.col("channel") == ch).select(
            "pt_date", pl.col(PRIMARY).alias(f"z_{ch}"), pl.col("p2_boot").alias(f"p_{ch}"), pl.col("d2").alias(f"d_{ch}"),
            pl.col("z2_split").alias(f"zs_{ch}"), pl.col("z1_boot").alias(f"z1_{ch}"), pl.col("z3_boot").alias(f"z3_{ch}"),
            pl.col("N").alias(f"N_{ch}"), pl.min_horizontal("La", "Lb").alias(f"L_{ch}"),
            (pl.col("n_b") - pl.col("n_a")).abs().alias(f"dn_{ch}"))
        d = d.join(x, on="pt_date", how="left")
    d = d.sort("aday")
    # trailing alarms over the non-holdout active days in time order (NaN where the pair is unscored)
    for ch in rot["channel"].unique().to_list():
        for pre in ("z", "d", "zs", "z1", "z3"):
            d = d.with_columns(pl.Series(f"A{pre}_{ch}", L.trailing_z(d[f"{pre}_{ch}"].to_numpy().astype(float))))
    for nm, chs in {"C": CONTENT, **{f"C_{k}": v for k, v in VARIANTS.items()}}.items():
        d = d.with_columns(pl.mean_horizontal(*[f"Az_{c}" for c in chs]).alias(f"A_{nm}"),
                           pl.mean_horizontal(*[f"z_{c}" for c in chs]).alias(f"z_{nm}"))
    d = d.with_columns(pl.mean_horizontal("Ad_content_bge", "Ad_content_gte").alias("A_C_raw"),
                       pl.mean_horizontal("Azs_content_bge", "Azs_content_gte").alias("A_C_split"),
                       pl.mean_horizontal("Az1_content_bge", "Az1_content_gte").alias("A_C_k1"),
                       pl.mean_horizontal("Az3_content_bge", "Az3_content_gte").alias("A_C_k3"),
                       pl.col("Az_talk").alias("A_T"),
                       pl.max_horizontal("N_content_bge", "N_content_gte").alias("N_C"),
                       pl.max_horizontal("L_content_bge", "L_content_gte").alias("W_C"))
    d = d.with_columns(((pl.col("A_C") + pl.col("R1m")) / np.sqrt(2)).alias("comb"))
    return d


def events() -> pl.DataFrame:
    return pl.read_parquet(H36 / "fixed_bge_none/events.parquet").filter(~pl.col("holdout0"))


def window_max(d: pl.DataFrame, col: str, pos: np.ndarray) -> np.ndarray:
    x = d[col].to_numpy().astype(float)
    out = []
    for p in pos:
        w = x[max(0, p - 1): p + 2]
        out.append(np.nanmax(w) if np.isfinite(w).any() else np.nan)
    return np.array(out)


def event_study(d, ev, score, rng, cls="goal"):
    pos_of = {t: i for i, t in enumerate(d["pt_date"].to_list())}
    e = ev.filter(pl.col("cls") == cls)
    pos = np.array([pos_of[t] for t in e["pt_date0"].to_list() if t in pos_of])
    x = d[score].to_numpy().astype(float)
    plc = d["placebo"].to_numpy()
    pe, pn = x[pos], x[plc]
    a, lo, hi = L.auc_ci(pe, pn, rng)
    hit_vals = window_max(d, score, pos)
    pidx = np.flatnonzero(plc)
    win_far = np.nanmean(window_max(d, score, pidx) >= L.THRESH) if len(pidx) else np.nan
    # random-date null for the mean event-day score (same regime, scored days)
    reg = d["regime"].to_numpy(); ok = np.isfinite(x)
    obs = np.nanmean(pe)
    draws = []
    for _ in range(2000):
        s = [rng.choice(np.flatnonzero(ok & (reg == reg[p]))) for p in pos if np.isfinite(x[p])]
        draws.append(np.mean(x[s]) if s else np.nan)
    draws = np.array(draws)
    return {"score": score, "n_events": int(np.isfinite(pe).sum()), "n_placebo": int(np.isfinite(pn).sum()),
            "auc": a, "auc_lo": lo, "auc_hi": hi,
            "hit": float(np.nanmean(hit_vals >= L.THRESH)) if np.isfinite(hit_vals).any() else np.nan,
            "far_day": float(np.nanmean(pn[np.isfinite(pn)] >= L.THRESH)) if np.isfinite(pn).any() else np.nan,
            "far_window": float(win_far), "mean_event": float(obs),
            "p_random_date": float((1 + np.sum(draws >= obs)) / (1 + np.isfinite(draws).sum()))}


def main():
    rng = np.random.default_rng(L.SEED)
    d = day_table()
    ev = events()
    (L.OUT / "eval").mkdir(exist_ok=True)
    d.write_parquet(L.OUT / "days_scored.parquet", compression="zstd")
    res = {"n_days": d.height, "n_placebo": int(d["placebo"].sum())}
    # ---------------------------------------------------------------- P1 goal kickoffs
    scores = ["A_C", "A_C_raw", "A_C_split", "A_C_k1", "A_C_k3", "A_C_style", "A_C_restate", "Az_content_bge",
              "Az_content_gte", "A_T", "z_C", "R1m", "R1_bge", "R1_gte", "comb"] + (["H74_F", "H74_C"] if "H74_F" in d.columns else [])
    res["goal"] = {s: event_study(d, ev, s, rng) for s in scores}
    pos_of = {t: i for i, t in enumerate(d["pt_date"].to_list())}
    goal_pos = np.array([pos_of[t] for t in ev.filter(pl.col("cls") == "goal")["pt_date0"].to_list() if t in pos_of])
    plc = d["placebo"].to_numpy()
    for other in ("R1m", "R1_bge", "H74_F") if "H74_F" in d.columns else ("R1m", "R1_bge"):
        a_e, b_e = d["A_C"].to_numpy()[goal_pos], d[other].to_numpy()[goal_pos]
        a_n, b_n = d["A_C"].to_numpy()[plc], d[other].to_numpy()[plc]
        res[f"dAUC_A_C_minus_{other}"] = L.paired_dauc(a_e.astype(float), b_e.astype(float), a_n.astype(float), b_n.astype(float), rng)
    c_e, r_e = d["comb"].to_numpy()[goal_pos], d["R1m"].to_numpy()[goal_pos]
    res["dAUC_comb_minus_R1m"] = L.paired_dauc(c_e.astype(float), r_e.astype(float), d["comb"].to_numpy()[plc].astype(float),
                                               d["R1m"].to_numpy()[plc].astype(float), rng)
    # R1 misses caught
    r1w = window_max(d, "R1m", goal_pos); acw = window_max(d, "A_C", goal_pos)
    miss = np.isfinite(r1w) & (r1w < L.THRESH)
    res["R1_misses"] = {"n_events_scored": int(np.isfinite(r1w).sum()), "n_missed_by_R1": int(miss.sum()),
                        "caught_by_A_C": int(np.sum(miss & (acw >= L.THRESH))),
                        "A_C_scored_among_missed": int(np.sum(miss & np.isfinite(acw)))}
    # powered subset of kickoffs (Amendment 1): W >= 16 or N >= 16 on the kickoff pair
    Wc, Nc = d["W_C"].to_numpy().astype(float), d["N_C"].to_numpy().astype(float)
    pw = goal_pos[(Wc[goal_pos] >= 16) | (Nc[goal_pos] >= 16)]
    x = d["A_C"].to_numpy().astype(float)
    res["goal_powered_subset"] = {"n": int(np.isfinite(x[pw]).sum()), "auc": L.auc(x[pw], x[plc]),
                                  "mean_A_C": float(np.nanmean(x[pw])) if len(pw) else None,
                                  "auc_R1m": L.auc(d["R1m"].to_numpy().astype(float)[pw], d["R1m"].to_numpy().astype(float)[plc])}
    # per-event table
    et = []
    for t in ev.filter(pl.col("cls").is_in(["goal", "room", "roster", "scaffold", "operator", "r1b"]))["pt_date0"].unique().to_list():
        if t not in pos_of:
            continue
        p = pos_of[t]
        refs = ev.filter(pl.col("pt_date0") == t)
        et.append({"pt_date": t, "refs": ",".join(refs["ref"].to_list()), "classes": ",".join(sorted(set(refs["cls"].to_list()))),
                   **{c: (float(d[c][p]) if d[c][p] is not None else None) for c in
                      ["z_content_bge", "z_content_gte", "z_talk", "A_C", "A_T", "R1m", "N_C", "W_C", "N_talk", "L_talk"]}})
    pl.DataFrame(et, infer_schema_length=None).sort("pt_date").write_parquet(L.OUT / "eval/event_table.parquet")
    # ---------------------------------------------------------------- P2 stationarity between events
    rot = pl.read_parquet(L.OUT / "rotation.parquet").join(d.select("pt_date", "placebo", "dist_event"), on="pt_date", how="left")
    p2 = {}
    for ch in rot["channel"].unique().to_list():
        x = rot.filter((pl.col("channel") == ch) & pl.col("placebo"))
        if ch == "talk":
            x = x.filter((pl.col("N") >= 16) & (pl.min_horizontal("La", "Lb") >= 240))
        k = int((x["p2_boot"] < 0.05).sum()); n = x.height
        ks = int((x["p2_split"] < 0.05).sum())
        p2[ch] = {"n": n, "s_sig_boot": k / n if n else None, "ci": L.wilson(k, n), "s_sig_split": ks / n if n else None,
                  "median_z": float(x[PRIMARY].median()) if n else None}
    p2["content_mean_s_sig"] = float(np.mean([p2[c]["s_sig_boot"] for c in CONTENT]))
    tall = rot.filter((pl.col("channel") == "talk") & pl.col("placebo"))
    p2["talk_all_sizes"] = {"n": tall.height, "s_sig_boot": float((tall["p2_boot"] < 0.05).mean()) if tall.height else None}
    res["P2"] = p2
    # ---------------------------------------------------------------- P3 rooms
    rooms = pl.read_parquet(L.OUT / "rooms.parquet")
    rc = []
    cal_pairs = rot.filter(pl.col("channel") == "content_bge").select("day_a", "pt_date")
    for da, db in cal_pairs.iter_rows():
        ra = rooms.filter(pl.col("pt_date") == da).select("agent", pl.col("room").alias("ra"))
        rb = rooms.filter(pl.col("pt_date") == db).select("agent", pl.col("room").alias("rb"))
        j = ra.join(rb, on="agent")
        rc.append({"pt_date": db, "n_room_moves": int((j["ra"] != j["rb"]).sum()), "n_rooms_b": int(rb["rb"].n_unique())})
    rcd = pl.DataFrame(rc)
    d2 = d.join(rcd, on="pt_date", how="left")
    room_ev = ev.filter(pl.col("cls") == "room")
    p3 = {"room_events": []}
    for r in room_ev.iter_rows(named=True):
        t = r["pt_date0"]
        if t in pos_of:
            p = pos_of[t]
            p3["room_events"].append({"ref": r["ref"], "pt_date": t,
                                      **{c: (float(d[c][p]) if d[c][p] is not None else None) for c in
                                         ["z_talk", "A_T", "z_content_bge", "z_content_gte", "A_C", "R1m", "N_talk", "L_talk"]}})
    goal_only = ev.filter(pl.col("cls") == "goal").filter(~pl.col("confounded"))["pt_date0"].to_list()
    go = d.filter(pl.col("pt_date").is_in(goal_only))
    p3["goal_only_median_A_T"] = float(go["A_T"].drop_nulls().drop_nans().median()) if go.height else None
    p3["goal_only_median_A_C"] = float(go["A_C"].drop_nulls().drop_nans().median()) if go.height else None
    mv = d2.filter(pl.col("n_room_moves") >= 2); st = d2.filter(pl.col("n_room_moves") < 2)
    for col in ("z_talk", "z_C"):
        p3[f"reassign_{col}"] = {"n_move_days": int(mv[col].drop_nulls().drop_nans().len()),
                                 "mean_move": float(mv[col].drop_nulls().drop_nans().mean()) if mv.height else None,
                                 "mean_other": float(st[col].drop_nulls().drop_nans().mean()),
                                 "p_perm": L.mannwhitney_p(mv[col].to_numpy(), st[col].to_numpy(), rng)}
    p3["reassign_days"] = mv.select("pt_date", "n_room_moves", "z_talk", "z_C").to_dicts()
    res["P3"] = p3
    # ---------------------------------------------------------------- P4-P6
    res["P4_spearman_A_C_R1m"] = L.spearman(d["A_C"].to_numpy(), d["R1m"].to_numpy())
    res["P4_spearman_zC_R1m_raw"] = L.spearman(d["z_C"].to_numpy(), d["R1m"].to_numpy())
    res["P5_spearman_bge_gte"] = L.spearman(d["z_content_bge"].to_numpy(), d["z_content_gte"].to_numpy())
    res["P5_auc_shift_style"] = res["goal"]["A_C_style"]["auc"] - res["goal"]["A_C"]["auc"]
    res["P5_auc_shift_restate"] = res["goal"]["A_C_restate"]["auc"] - res["goal"]["A_C"]["auc"]
    res["P6_spearman_z_dn"] = {c: L.spearman(d[f"z_{c}"].to_numpy(), d[f"dn_{c}"].to_numpy()) for c in CONTENT + ["talk"]}
    res["spearman_z_N"] = {c: L.spearman(d[f"z_{c}"].to_numpy(), d[f"N_{c}"].to_numpy()) for c in CONTENT + ["talk"]}
    res["talk_vs_content_spearman"] = L.spearman(d["z_talk"].to_numpy(), d["z_C"].to_numpy())
    # ---------------------------------------------------------------- per-period replication
    rows = []
    for g in sorted(d["goal_no"].unique().to_list()):
        rg = rot.filter(pl.col("channel").is_in(CONTENT) & (pl.col("goal_no") == g))
        within = rg.filter((pl.col("goal_a") == g) & (pl.col("dist_event") >= 2))
        kick = rg.filter(pl.col("goal_a") != g)
        shares = [float((within.filter(pl.col("channel") == c)["p2_boot"] < 0.05).mean()) for c in CONTENT
                  if within.filter(pl.col("channel") == c).height]
        npairs = within.filter(pl.col("channel") == "content_bge").height
        zz = within.group_by("pt_date").agg(pl.col(PRIMARY).mean())[PRIMARY].to_numpy()
        bs = [np.median(rng.choice(zz, len(zz))) for _ in range(1000)] if len(zz) >= 2 else []
        kday = kick["pt_date"].unique().to_list()
        kA = float(d.filter(pl.col("pt_date").is_in(kday))["A_C"].drop_nulls().drop_nans().max()) if kday and \
            d.filter(pl.col("pt_date").is_in(kday))["A_C"].drop_nulls().drop_nans().len() else None
        kz = float(kick[PRIMARY].mean()) if kick.height else None
        tw = rot.filter((pl.col("channel") == "talk") & (pl.col("goal_no") == g) & (pl.col("goal_a") == g) & (pl.col("dist_event") >= 2))
        s_sig = float(np.mean(shares)) if shares else None
        if npairs < 3:
            verdict = "descriptive"
        else:
            c1 = s_sig <= 0.15
            c2 = kA is not None and kA >= L.THRESH
            verdict = "supported" if (c1 and c2) else ("failed" if (not c1 and not c2) else "mixed")
        units = d.filter(pl.col("goal_no") == g)
        rows.append({"goal_no": g, "regime": units["regime"][0], "n_pairs": npairs, "s_sig": s_sig,
                     "s_sig_lo": L.wilson(int(round((s_sig or 0) * npairs)), npairs)[0] if npairs else None,
                     "s_sig_hi": L.wilson(int(round((s_sig or 0) * npairs)), npairs)[1] if npairs else None,
                     "z_med": float(np.median(zz)) if len(zz) else None,
                     "z_lo": float(np.quantile(bs, 0.025)) if bs else None, "z_hi": float(np.quantile(bs, 0.975)) if bs else None,
                     "kick_A_C": kA, "kick_z": kz, "kick_R1m": float(d.filter(pl.col("pt_date").is_in(kday))["R1m"].drop_nulls().drop_nans().max())
                     if kday and d.filter(pl.col("pt_date").is_in(kday))["R1m"].drop_nulls().drop_nans().len() else None,
                     "talk_pairs": tw.height, "talk_s_sig": float((tw["p2_boot"] < 0.05).mean()) if tw.height else None,
                     "N_med": float(within["N"].median()) if within.height else None,
                     "first_day": units["pt_date"].min(), "last_day": units["pt_date"].max(), "n_days": units.height,
                     "verdict": verdict})
    per = pl.DataFrame(rows, infer_schema_length=None)
    per.write_parquet(L.OUT / "periods.parquet", compression="zstd")
    res["periods"] = {"n": per.height, "verdicts": per["verdict"].value_counts().to_dicts(),
                      "s_sig_median": float(per.filter(pl.col("n_pairs") >= 3)["s_sig"].median()),
                      "share_s_sig_le_015": float((per.filter(pl.col("n_pairs") >= 3)["s_sig"] <= 0.15).mean())}
    (L.OUT / "eval/results.json").write_text(json.dumps(res, indent=1, default=lambda o: None if o is None else float(o)))
    # ---- print
    for s, r in res["goal"].items():
        print(f"{s:22s} n={r['n_events']:2d} AUC {r['auc']:.3f} [{r['auc_lo']:.2f},{r['auc_hi']:.2f}] hit {r['hit']:.2f} "
              f"farD {r['far_day']:.3f} farW {r['far_window']:.2f} p_rd {r['p_random_date']:.3f}")
    for k in [k for k in res if k.startswith("dAUC")]:
        print(k, res[k])
    for k in ("R1_misses", "goal_powered_subset", "P2", "P3", "P4_spearman_A_C_R1m", "P4_spearman_zC_R1m_raw", "P5_spearman_bge_gte",
              "P5_auc_shift_style", "P5_auc_shift_restate", "P6_spearman_z_dn", "spearman_z_N", "talk_vs_content_spearman", "periods"):
        print(k, json.dumps(res[k], default=lambda o: None if o is None else float(o))[:1500])


if __name__ == "__main__":
    main()
