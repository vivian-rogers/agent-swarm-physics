"""H05 CONFIRMATORY test on the locked holdout: rooms v1 (NE12, 2026-02-25), #voted-out (inside #34) and the
#best/#rest split (NE15, 2026-03-16). WRITTEN 2026-10-03, NOT RUN.

!!! Running this consumes the holdout for H05. Do not run it until the predictions below (and the card's
!!! "Prediction" / "H05-MF" sections) are final and the run is signed off. It refuses to run without --confirm.
!!! `--dry-run` executes every code path on NON-holdout stand-in windows (and asserts no holdout day is touched).

Design (difference-in-differences across agent pairs; pairs that stay co-located are the control, which removes
same-day shocks common to all pairs such as the operator reset NE35 on 02-25 and the NE14 tool/scaffold bundle):

  A  NE12 placebo/scoping (02-25). Structural fact: no pair was separated on 02-25 (every agent stayed in
     #general until #voted-out appeared on 03-05/06). Asserted below from rooms_timeline. So 02-25 changed
     visibility rules but cut no channel. Pre = #31 + 02-23/24; post = 02-25..02-27 + #33.
  B  #voted-out (03-05 -> 03-13): pairs (voted-out agent x others) separated on the days the agent sat in room 1.
     Few pairs; analysed in the pooled TWFE (D) with continuous per-day co-location.
  C  NE15 split (03-16): cut arm = #best x #rest pairs; control = pairs within #best and within #rest.
     Pre = #33 + #34 pair-days with both agents in #general; post = #35.
  D  Pooled two-way FE over 02-09 -> 03-20: y_ij,d = a_ij + g_d + b * coloc_ij,d.
  E  H05-MF: block mean field, sublattices = the 03-16 partition; (J_in, J_out) per window.

Outcomes: excess lagged correlation kappa_x and excess equal-time correlation c0_x (over the cross-day surrogate),
pair EP (block cross-fitted Gaussian bound, minus surrogate), class-restricted Newton EP per pair-hour, whole-system
EP per agent-hour (cross-fitted Newton bound and held-out ML bound), for talk spins (primary: chat is the channel
rooms cut) and active spins (secondary). Inference: day bootstrap, assignment permutation, two-way clustered SEs.

Usage:
  uv run python hypotheses/H05-rooms-cut/analysis/confirm_ne12.py --dry-run     # safe: non-holdout stand-ins
  uv run python hypotheses/H05-rooms-cut/analysis/confirm_ne12.py --confirm     # CONSUMES THE HOLDOUT
Writes data/processed/H05-rooms-cut/confirm/ (confirm_ne12.json) or .../confirm_dryrun/.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
CARD = HERE.parent / "README.md"
warnings.simplefilter("ignore", RuntimeWarning)

DRY = "--dry-run" in sys.argv
CONFIRM = "--confirm" in sys.argv
OUT = ROOT / "data/processed/H05-rooms-cut" / ("confirm_dryrun" if DRY else "confirm")

# ============================================================================ pre-registered predictions
# Written 2026-10-03 after the non-holdout exploration (round 1), before any holdout outcome was computed.
PREDICTIONS = {
    "C1_talk_pair_did_split": "NE15 cut arm (best x rest) vs stay: DiD of talk c0_x AND talk kappa_x < 0; day-bootstrap "
                              "95% CI excludes 0 for at least one of them and assignment-permutation p < 0.05 for it.",
    "C2_active_pair_did_split": "Same for active spins: DiD < 0 predicted, NOT decisive (exploration found active-spin "
                                "coupling barely room-dependent; failure here does not count against H05).",
    "C3_twfe_talk": "Pooled TWFE 02-09 -> 03-20, talk kappa_x (and c0_x): beta(coloc) > 0 with two-way clustered z > 1.96. "
                    "Exploration (regime III) found beta ~ +0.008 (z ~ 2.6); expect similar size.",
    "C4_ep": "Class-restricted Newton EP per pair-hour: cut-arm DiD < 0 (direction only; exploration showed EP measures "
             "underpowered at this sampling, so a null here is uninformative). Whole-system EP per agent-hour does NOT "
             "fall at 02-25 (95% CI of post - pre from delete-one-day jackknife SEs includes 0, or the change is positive), because no "
             "channel was cut that day.",
    "C5_MF": "H05-MF, talk spins, sublattices = 03-16 partition: J_out in #35 within 2 bootstrap SE of 0 and below its "
             "pre-split value (#33 + #34-in-#general); J_in post - pre 95% day-bootstrap CI includes 0 (amended 2026-10-03 from a "
             "post/pre ratio, which the non-holdout dry run showed is unstable when J_in(pre) ~ 0). Placebo: J_out does not drop at 02-25.",
    "C6_placebo_0225": "No pair separated on 02-25 (asserted). Pair-level co-location is constant across 02-25, so any "
                       "change at 02-25 is attributed to NE35 / visibility scoping, not to a channel cut.",
    "overall": "H05 confirmed if C1 and C3 pass and C5's J_out criterion passes. Refuted if C1 and C3 both have the "
               "wrong sign or CIs centred on 0 with |effect| < half the exploratory effect. Otherwise inconclusive.",
}

# confirmation windows (PT dates) and non-holdout stand-ins for --dry-run
WINDOWS = {
    "A_pre": ("2026-02-16", "2026-02-24"), "A_post": ("2026-02-25", "2026-03-04"),
    "C_pre": ("2026-03-02", "2026-03-13"), "C_post": ("2026-03-16", "2026-03-20"),
    "D_all": ("2026-02-09", "2026-03-20"),
}
DRY_WINDOWS = {  # same structure, regime III, all non-holdout: merge (#39 -> #40) then split (#40 -> #41)
    "A_pre": ("2026-04-27", "2026-05-01"), "A_post": ("2026-05-04", "2026-05-08"),
    "C_pre": ("2026-05-04", "2026-05-08"), "C_post": ("2026-05-11", "2026-05-15"),
    "D_all": ("2026-04-20", "2026-05-22"),
}
SPLIT_LABEL_WINDOW = ("2026-03-16", "2026-03-20")
DRY_SPLIT_LABEL_WINDOW = ("2026-05-11", "2026-05-15")


def card_hash():
    """Fingerprint of the card's prediction sections, stored with the results (detects post-hoc edits)."""
    txt = CARD.read_text()
    a = txt.index("## Prediction"); b = txt.index("## Results")
    return hashlib.sha256(txt[a:b].encode()).hexdigest()[:16]


# ============================================================================ data (same transform as scheme/build_panel.py)
def calendar_days(lo, hi):
    cal = pl.read_parquet(SH / "calendar.parquet")
    return sorted(cal.filter((pl.col("pt_date") >= lo) & (pl.col("pt_date") <= hi))["pt_date"].to_list())


def build_mats(days, bin_k=1):
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days))
    if DRY:
        assert not cal["holdout"].any(), "dry run must not touch holdout days"
    ab = (pl.scan_parquet(SH / "activity_bins.parquet").filter(pl.col("pt_date").is_in(days))
          .select("pt_date", "minute", "agent", "state").collect())
    ab = ab.join(cal.select("pt_date", "win_start", "goal_no", pl.col("regime").cast(pl.Utf8)), on="pt_date")
    ab = ab.with_columns((pl.col("win_start") + pl.duration(seconds=pl.col("minute") * 60 + 30)).alias("t"))
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").select("agent", "room", pl.col("t_start").alias("t")).sort("agent", "t")
    ab = ab.sort("agent", "t").join_asof(rt, on="t", by="agent", strategy="backward")
    p = ab.select("pt_date", "minute", "agent", (pl.col("state") >= 3).cast(pl.Int8).alias("active"),
                  (pl.col("state") == 4).cast(pl.Int8).alias("talk"), pl.col("room").fill_null(-1).cast(pl.Int8),
                  "goal_no", "regime").sort("pt_date", "minute", "agent")
    goal = dict(p.group_by("pt_date").agg(pl.col("goal_no").first()).iter_rows())
    regime = dict(p.group_by("pt_date").agg(pl.col("regime").first()).iter_rows())
    mats = {}
    for (d,), g in p.group_by("pt_date", maintain_order=True):
        agents = np.sort(g["agent"].unique().to_numpy())
        L = int(g["minute"].max()) + 1
        ai = np.searchsorted(agents, g["agent"].to_numpy()); mi = g["minute"].to_numpy().astype(int)
        m = {"agents": agents}
        for s in ("active", "talk"):
            A = -np.ones((L, len(agents)), dtype=np.int8); A[mi, ai] = np.where(g[s].to_numpy() > 0, 1, -1); m[s] = A
        R = -np.ones((L, len(agents)), dtype=np.int8); R[mi, ai] = g["room"].to_numpy(); m["room"] = R
        mats[d] = m
    ad = (p.group_by("pt_date", "agent").agg(pl.col("active").mean().alias("active_frac"), pl.col("goal_no").first())
          .join(p.filter(pl.col("room") >= 0).group_by("pt_date", "agent", "room").agg(pl.len().alias("n"))
                .sort("n", descending=True).group_by("pt_date", "agent")
                .agg(pl.col("room").first().alias("room_mode"), (pl.col("n").first() / pl.col("n").sum()).alias("purity")),
                on=["pt_date", "agent"], how="left"))
    return mats, goal, regime, ad


# ============================================================================ analysis
def main():
    if not (DRY or CONFIRM):
        sys.exit("Refusing to run: pass --dry-run (non-holdout stand-ins) or --confirm (consumes the holdout).")
    if CONFIRM and DRY:
        sys.exit("Choose one of --dry-run / --confirm.")
    import explore_rooms as X
    from mf_blocks import labels_from_agent_day, window_mf, strip
    from pairs import twfe

    W = DRY_WINDOWS if DRY else WINDOWS
    lab_win = DRY_SPLIT_LABEL_WINDOW if DRY else SPLIT_LABEL_WINDOW
    rng = np.random.default_rng(20261003)
    OUT.mkdir(parents=True, exist_ok=True)
    days = calendar_days(*W["D_all"])
    mats, goal, regime, ad = build_mats(days)
    days = sorted(mats)
    pdf = pl.concat([X.pair_days(days, mats, goal, regime, s) for s in ("talk", "active")])
    pdf.write_parquet(OUT / "pair_day.parquet", compression="zstd")
    rng_days = lambda k: [d for d in days if W[k][0] <= d <= W[k][1]]
    res = {"mode": "dry-run (non-holdout stand-ins)" if DRY else "CONFIRMATORY", "predictions": PREDICTIONS,
           "card_prediction_hash": card_hash(), "windows": W, "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}

    # ---- A: 02-25 structural check + placebo
    pre_a, post_a = rng_days("A_pre"), rng_days("A_post")
    sub = pdf.filter(pl.col("pt_date").is_in(pre_a + post_a) & (pl.col("spin") == "talk"))
    sep = sub.filter(pl.col("coloc") < 0.75)
    n_sep_pre = sep.filter(pl.col("pt_date").is_in(pre_a)).height
    n_sep_post = sep.filter(pl.col("pt_date").is_in(post_a)).height
    res["A_structure"] = {"separated_pair_days_pre": n_sep_pre, "separated_pair_days_post": n_sep_post}
    if not DRY:
        assert n_sep_pre == 0 and n_sep_post == 0, "NE12 premise violated: some pair was separated around 02-25"
    res["A_placebo"] = {}
    for spin in ("talk", "active"):
        r = {}
        for y in ("kappa_x", "c0_x"):
            t = pdf.filter((pl.col("spin") == spin) & pl.col("pt_date").is_in(pre_a + post_a))
            dm = t.group_by("pt_date").agg(pl.col(y).mean()).sort("pt_date")
            a = dm.filter(pl.col("pt_date").is_in(pre_a))[y].to_numpy(); b = dm.filter(pl.col("pt_date").is_in(post_a))[y].to_numpy()
            bs = [rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean() for _ in range(2000)]
            r[y] = {"post_minus_pre": float(b.mean() - a.mean()), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
        eps = {}
        for lab, ds in (("pre", pre_a), ("post", post_a)):
            ag, Sp, Sn, dd, mm = X.stack_window(mats, ds, spin)
            G = X.g_matrix(Sp, Sn, dtype=np.float64)
            eps[lab] = {"newton": X.ep_gauss_crossfit(G, dd)["sigma"] * 60 / len(ag),
                        "heldout_ml": X.ep_heldout(G, dd, k=min(5, len(ds)), return_theta=False)["sigma"] * 60 / len(ag), "N": int(len(ag))}
            # delete-one-day jackknife of the cross-fitted Newton bound (a day bootstrap would put duplicated days in
            # different folds and bias the cross terms upward)
            uq = np.unique(dd)
            jk = np.array([X.ep_gauss_crossfit(G[dd != q], dd[dd != q])["sigma"] * 60 / len(ag) for q in uq])
            eps[lab]["jk_var"] = float((len(uq) - 1) / len(uq) * np.sum((jk - jk.mean()) ** 2))
        diff = eps["post"]["newton"] - eps["pre"]["newton"]
        se = np.sqrt(eps["pre"]["jk_var"] + eps["post"]["jk_var"])
        r["ep_newton_agent_hour"] = {"pre": eps["pre"]["newton"], "post": eps["post"]["newton"],
                                     "post_minus_pre_ci95": [float(diff - 1.96 * se), float(diff + 1.96 * se)],
                                     "heldout_ml_pre": eps["pre"]["heldout_ml"], "heldout_ml_post": eps["post"]["heldout_ml"]}
        res["A_placebo"][spin] = r

    # ---- C: NE15 split, pair DiD (+ class-restricted EP) via the exploratory machinery
    pre_c, post_c = rng_days("C_pre"), rng_days("C_post")
    ev = {"id": "split", "kind": "cut (NE15 #best/#rest split)" if not DRY else "dry-run stand-in: 05-11 split",
          "pre": pre_c, "post": post_c}
    # pre-split pair-days count only when both agents shared a room that day (drops #voted-out separations)
    pdf_c = pdf.filter(~(pl.col("pt_date").is_in(pre_c) & (pl.col("coloc") < 0.75)))
    res["C_split"] = {s: X.event_did(ev, pdf_c, mats, s) for s in ("talk", "active")}

    # ---- D: pooled TWFE over the whole confirmation window
    res["D_twfe"] = {}
    for spin in ("talk", "active"):
        tt = pdf.filter((pl.col("spin") == spin) & pl.col("coloc").is_not_null() & (pl.col("known") > 0.5))
        pk = (tt["i"].cast(pl.Int32) * 100 + tt["j"].cast(pl.Int32)).to_numpy(); dk = tt["pt_date"].to_numpy()
        x = tt["coloc"].to_numpy().astype(float)
        ctrl = np.column_stack([(tt["act_i"] + tt["act_j"]).to_numpy(), (tt["act_i"] * tt["act_j"]).to_numpy()]).astype(float)
        res["D_twfe"][spin] = {y: {"plain": twfe(tt[y].to_numpy().astype(float), x, pk, dk),
                                   "act_controls": twfe(tt[y].to_numpy().astype(float), x, pk, dk, controls=ctrl)}
                               for y in ("kappa_x", "c0_x", "sig_x")}

    # ---- E: H05-MF block couplings, sublattices = the split partition
    lab_days = [d for d in days if lab_win[0] <= d <= lab_win[1]]
    labels = labels_from_agent_day(ad, lab_days)
    res["E_MF"] = {"labels": {int(k): int(v) for k, v in labels.items()}}
    for spin in ("talk", "active"):
        per = {}
        for nm, ds in (("A_pre", pre_a), ("A_post", post_a), ("C_pre", pre_c), ("C_post", post_c)):
            per[nm] = window_mf(pdf, ds, labels, spin, rng, nperm=500)
        e = {k: strip(v) for k, v in per.items()}
        jo_pre, jo_post = per["C_pre"]["J_out"], per["C_post"]["J_out"]
        se_post = per["C_post"]["J_out_se"]
        din_bs = per["C_post"]["_boot"][:, 0] - per["C_pre"]["_boot"][:, 0]
        e["C5_checks"] = {"J_out_post_within_2se_of_0": bool(abs(jo_post) <= 2 * se_post),
                          "J_out_post_below_pre": bool(jo_post < jo_pre),
                          "J_out_drop_ci95": [float(np.nanpercentile(per["C_post"]["_boot"][:, 1] - per["C_pre"]["_boot"][:, 1], q)) for q in (2.5, 97.5)],
                          "J_in_change_post_minus_pre": float(per["C_post"]["J_in"] - per["C_pre"]["J_in"]),
                          "J_in_change_ci95": [float(np.nanpercentile(din_bs, 2.5)), float(np.nanpercentile(din_bs, 97.5))],
                          "placebo_J_out_change_0225_ci95": [float(np.nanpercentile(per["A_post"]["_boot"][:, 1] - per["A_pre"]["_boot"][:, 1], q)) for q in (2.5, 97.5)]}
        res["E_MF"][spin] = e

    # ---- verdicts (mechanical application of PREDICTIONS)
    def did(spin, y, arm="cut"):
        q = (res["C_split"][spin] or {}).get(y, {}).get(arm)
        return q
    v = {}
    c1 = [did("talk", y) for y in ("c0_x", "kappa_x")]
    v["C1"] = bool(c1[0] and c1[1] and c1[0]["did"] < 0 and c1[1]["did"] < 0 and any(
        q["ci95_dayboot"][1] < 0 and (q["p_assign_perm_2sided"] or 1) < 0.05 for q in c1))
    tw = res["D_twfe"]["talk"]["kappa_x"]["plain"]
    v["C3"] = bool(tw.get("beta", np.nan) > 0 and tw["beta"] / tw["se_twoway"] > 1.96)
    ck = res["E_MF"]["talk"]["C5_checks"]
    v["C5_J_out"] = bool(ck["J_out_post_within_2se_of_0"] and ck["J_out_post_below_pre"])
    v["C5_J_in_unchanged"] = bool(ck["J_in_change_ci95"][0] <= 0 <= ck["J_in_change_ci95"][1])
    ep_ci = res["A_placebo"]["active"]["ep_newton_agent_hour"]["post_minus_pre_ci95"]
    v["C4_no_EP_drop_at_0225"] = bool(ep_ci[0] <= 0 <= ep_ci[1] or ep_ci[0] > 0)
    v["overall"] = "confirmed" if (v["C1"] and v["C3"] and v["C5_J_out"]) else "see components"
    res["verdicts"] = v
    (OUT / "confirm_ne12.json").write_text(json.dumps(res, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
