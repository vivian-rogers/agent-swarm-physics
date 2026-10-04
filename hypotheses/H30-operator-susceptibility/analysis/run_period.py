"""H30 per-period analysis: chi_act / chi_con, daily gauge, stability, nulls, aging, context fill, family, H04 cross-check.

Reads data/processed/H30-operator-susceptibility/G<NN>/{kicks,content}.parquet (scheme/build.py) and the activity panels.
Writes G<NN>/{results.json, daily.parquet, kick_resp.parquet} and goalperiod-subhypotheses/G<NN>/figures/daily_gauge.pdf.
Run: uv run python hypotheses/H30-operator-susceptibility/analysis/run_period.py --period G51   (or --all)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h30lib import *  # noqa: E402,F403

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PERIODS = ["G04", "G05", "G06", "G13", "G30", "G31", "G33", "G35", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
DENSE = {"G04", "G05", "G06"}
KIND = {"G04": "human_dense", "G05": "human_dense", "G06": "human_dense", "G13": "human_dense", "G38": "G38",
        "G41": "G41", "G44": "G44", "G51": "G51"}
B = 1000
N_SWAP = 20


def fnum(x, k=2):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{k}f}"


def fci(c, k=2):
    if c is None or c[0] is None or not np.isfinite(c[0]):
        return "–"
    if c[1] is None or not np.isfinite(c[1]):
        return f"{c[0]:.{k}f}"
    if max(abs(c[1]), abs(c[2])) > 50 * max(1.0, abs(c[0])) or c[2] - c[1] < 1e-9:
        return f"{c[0]:.{k}f} [CI unstable: too few days]"
    return f"{c[0]:.{k}f} [{c[1]:.{k}f}, {c[2]:.{k}f}]"


def boot_rows(fit: ActFit, W: np.ndarray, c: str) -> np.ndarray:
    j = fit.classes.index(c)
    A = np.nan_to_num(fit.day_A[:, j]); Bv = fit.day_B[:, j]
    with np.errstate(invalid="ignore", divide="ignore"):
        return (W @ A) / (W @ Bv)


def h04_crosscheck(days: list[str], msgs: pl.DataFrame) -> dict:
    """H04's matched Green's function (imported unmodified) on the same days, with clean-mention messages."""
    import h04lib as H4
    D = H4.load_days(days)
    m = msgs.rename({"named": "valid_mentions"}).select("msg", "t", "pt_date", "room", "kind", "valid_mentions", "recipients", "length")
    resp = H4.responder_rows(D, m)
    if resp.height == 0:
        return {}
    H4.attach_hits(D, resp)
    c = H4.build_cells(D, np.arange(64))
    ctl = H4.control_means(c, 64)
    sets = H4.build_sets(D, resp, c)
    W = H4.boot_weights(len(D), 400)
    out = {}
    for k in ("nudge_target_iso", "nudge_bystander_iso", "human_all_iso", "human_mentioned_iso"):
        if k in sets and len(sets[k]["ids"]) >= 5:
            r = H4.matched_response(c, ctl, sets[k]["ids"], len(D), k, sets[k]["n_kicks"], sets[k]["nb_adjust"])
            s = H4.summarize(r, W)
            out[k] = {"A30": s.get("A30"), "n_cells": s.get("n_cells"), "pre_m15_m1": s.get("pre_m15_m1"),
                      "placebo_m30_m16": s.get("placebo_m30_m16")}
    return out


def run_period(p: str, kicks: pl.DataFrame | None = None, content: pl.DataFrame | None = None, days: list[str] | None = None,
               allow_holdout: bool = False, out_dir: Path | None = None, fig_dir: Path | None = None, do_h04: bool = True,
               n_swap: int = N_SWAP) -> dict:
    t0 = time.time()
    out_dir = out_dir or (OUT / p)
    fig_dir = fig_dir or (HYP / "goalperiod-subhypotheses" / p / "figures")
    info = json.loads((out_dir / "build.json").read_text())
    days = days or info["days"]
    if not allow_holdout:
        assert_no_holdout(days)
    panels, meta = load_panels(days, allow_holdout=allow_holdout)
    kicks = kicks if kicks is not None else pl.read_parquet(out_dir / "kicks.parquet")
    content = content if content is not None else pl.read_parquet(out_dir / "content.parquet")
    nd = len(panels)
    R = {"period": p, "regime": info["regime"], "n_days": nd, "n_kicks": info["n_kicks"], "n_messages": info["n_messages"],
         "n_pairs": info["n_pairs_both_sides"], "notes": []}
    W = boot_weights(nd, B)
    pres = {pp.day: {int(a): i for i, a in enumerate(pp.agents)} for pp in panels}

    # ------------------------------------------------------------------ activity channel
    base = build_base(panels, kicks=kicks)
    X = kick_columns(base, kicks)
    fit = fit_activity(base, X)
    pc = period_ci(fit, W)
    R["act"] = {c: pc.get(c) for c in CLASSES}
    R["act_n"] = {c: pc.get(c + "_n") for c in CLASSES}
    R["act_se_cluster"] = {c: pc.get(c + "_se_cluster") for c in CLASSES}
    pre = fit_activity(base, X, outcome="Ypre")
    pre0 = fit_activity(base, X, outcome="Ypre", fe2=None)
    R["pre_placebo_nofe"] = {c: (float(pre0.beta[j]) if np.isfinite(pre0.beta[j]) else None,
                                 float(pre0.se[j]) if np.isfinite(pre0.se[j]) else None) for j, c in enumerate(CLASSES)}
    R["pre_placebo"] = {c: (float(pre.beta[j]) if np.isfinite(pre.beta[j]) else None,
                            float(pre.se[j]) if np.isfinite(pre.se[j]) else None) for j, c in enumerate(CLASSES)}
    # pre-registered variant (strata only, no day fixed effects) and agent-day fixed effects (A2 sensitivity)
    f_nofe = fit_activity(base, X, fe2=None)
    R["act_nofe"] = {c: v for c, v in period_ci(f_nofe, W).items() if c in CLASSES}
    f_ad = fit_activity(base, X, fe2="agentday")
    R["act_agentday"] = {c: v for c, v in period_ci(f_ad, W).items() if c in CLASSES}
    fo = fit_activity(base, X, mask=base.out_ok)
    R["act_outage_masked"] = {c: (float(fo.beta[j]) if np.isfinite(fo.beta[j]) else None) for j, c in enumerate(CLASSES)}
    R["act_outage_masked_ci"] = {c: v for c, v in period_ci(fo, W).items() if c in CLASSES}
    R["outage_share_cells"] = float(1 - base.out_ok.mean())
    pre_cols = len(CLASSES) + len(POST_CLASSES)
    Kpast = X[:, pre_cols + CLASSES.index("N_tgt")] + X[:, pre_cols + CLASSES.index("H_men")]
    first, rep = {}, {}
    for lab_, msk in (("first", Kpast == 0), ("repeat", Kpast > 0)):
        ff = fit_activity(base, X, mask=msk)
        R[f"act_{lab_}"] = {c: v for c, v in period_ci(ff, W).items() if c in ("N_tgt", "N_by", "H_men", "H_und")}
        R[f"act_{lab_}_n"] = ff.n_kicks
    bh = build_base(panels, kicks=kicks, strata="h04")
    fh = fit_activity(bh, kick_columns(bh, kicks))
    R["act_h04strata"] = {c: (float(fh.beta[j]) if np.isfinite(fh.beta[j]) else None) for j, c in enumerate(CLASSES)}
    # baseline: mean Y (expected active minutes in 30 min) among targeted cells' strata -> relative response
    R["baseline_Y_mean"] = float(base.Y.mean())
    # day-swap null
    rng = np.random.default_rng(SEED + int(p[1:]))
    sw = {c: [] for c in CLASSES}
    for _ in range(n_swap):
        ks = day_swap(kicks, pres, rng)
        if ks.height == 0:
            break
        b2 = build_base(panels, kicks=ks)
        f2 = fit_activity(b2, kick_columns(b2, ks))
        for j, c in enumerate(CLASSES):
            if np.isfinite(f2.beta[j]):
                sw[c].append(float(f2.beta[j]))
    R["swap_null"] = {c: ([float(np.mean(v)), float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) >= 5 else None)
                      for c, v in sw.items()}
    # collective mode per message (nudges and humans), for the pre-registered fit (level) and the day-FE fit
    msgs_by_kind = {k: kicks.filter(pl.col("kind") == k)["msg"].n_unique() for k in ("nudge", "human")}
    for key, fv, actd in (("collective", f_nofe, R["act_nofe"]), ("collective_dayfe", fit, R["act"])):
        coll = {}
        for kind, (ca, cb) in {"nudge": ("N_tgt", "N_by"), "human": ("H_men", "H_und")}.items():
            nm_ = msgs_by_kind.get(kind, 0)
            if nm_ == 0:
                continue
            na_, nb_ = R["act_n"].get(ca) or 0, R["act_n"].get(cb) or 0
            rows = np.zeros(len(W))
            for c, n_ in ((ca, na_), (cb, nb_)):
                if n_ and actd.get(c):
                    rows = rows + n_ * np.nan_to_num(boot_rows(fv, W, c))
            coll[kind] = {"chi_coll_per_msg": ci(rows / nm_), "targets_per_msg": na_ / nm_, "bystanders_per_msg": nb_ / nm_}
        R[key] = coll
    # post hoc (A2): swarm-wide lull at the kick (fraction of present agents active in the previous 5 min, bottom quartile)
    frac = np.zeros(len(base.Y), np.float32)
    for pp in panels:
        start, mm_ = base.offsets[pp.day]
        if len(mm_) == 0:
            continue
        cs_ = np.concatenate([[0.0], np.cumsum(pp.act.mean(0))])
        a0 = np.clip(mm_ - 5, 0, None)
        frac[start:start + pp.act.shape[0] * len(mm_)] = np.tile((cs_[mm_] - cs_[a0]) / np.maximum(mm_ - a0, 1), pp.act.shape[0])
    q25 = float(np.quantile(frac, 0.25))
    lull = frac <= q25
    R["lull_split"] = {"q25_active_fraction": q25}
    for lab_, msk in (("lull", lull), ("no_lull", ~lull)):
        try:
            fl_ = fit_activity(base, X, mask=msk)
            R["lull_split"][lab_] = {c: v for c, v in period_ci(fl_, W).items() if c in ("N_tgt", "N_by", "N_tgt_n", "N_by_n")}
        except Exception as ex:  # noqa: BLE001
            R["lull_split"][lab_] = {"error": str(ex)[:100]}

    # per-kick contributions with covariates
    kr = fit.kick_r.join(kicks.unique(["day", "row", "minute", "cls"]).select("day", "row", "minute", "cls", "fill", "ptok",
                                                                               "lab", "goal_day", "since_reset_s"),
                         on=["day", "row", "minute", "cls"], how="left")
    kr.write_parquet(out_dir / "kick_resp.parquet", compression="zstd")

    # ------------------------------------------------------------------ content channel
    con = {}
    for c in CLASSES:
        sub = content.filter((pl.col("cls") == c) & pl.col("chi_orth").is_not_nan())
        if sub.height < 10:
            continue
        con[c] = {"n": sub.height, "orth": boot_mean_by_day(sub, "chi_orth", np.arange(nd), W),
                  "matched": boot_mean_by_day(sub.filter(pl.col("chi").is_not_nan()), "chi", np.arange(nd), W),
                  "unmatched": float(sub["chi_unm"].drop_nans().mean()),
                  "raw_d_true": float(sub["d_true"].drop_nans().mean()),
                  "pseudo_null_orth": boot_mean_by_day(sub.filter(pl.col("chi_orth_null").is_not_nan()), "chi_orth_null", np.arange(nd), W),
                  "u_perp_norm": float(sub["u_perp_norm"].drop_nans().mean()),
                  "a_pre_mean": float(sub["a_pre"].drop_nans().mean())}
    R["con"] = con

    # ------------------------------------------------------------------ daily gauge + stability
    dly_act = daily_activity(fit).with_columns(pl.lit("act").alias("channel"))
    dly_con = (daily_mean(content.filter(pl.col("chi_orth").is_not_nan()), "chi_orth")
               .with_columns(pl.lit("con").alias("channel")).select("day", "cls", "n", "chi", "se", "channel"))
    daily = pl.concat([dly_act.select("day", "cls", "n", "chi", "se", "channel"),
                       dly_con.with_columns(pl.col("n").cast(pl.Int64))], how="vertical_relaxed")
    lab = {pp.day: pp.label for pp in panels}
    gd = {pp.day: pp.goal_day for pp in panels}
    daily = daily.with_columns(pl.col("day").replace_strict(lab, default=None).alias("pt_date"),
                               pl.col("day").replace_strict(gd, default=None).alias("goal_day"))
    daily.write_parquet(out_dir / "daily.parquet", compression="zstd")
    stab = {}
    for ch, c in (("act", "N_tgt"), ("act", "H_und"), ("act", "H_men"), ("con", "N_tgt"), ("con", "H_und"), ("con", "H_men")):
        dsub = daily.filter((pl.col("channel") == ch) & (pl.col("cls") == c)).select("day", "n", "chi", "se")
        if ch == "act":
            if p in DENSE:
                continue  # A1: no activity heterogeneity test in dense chat
            kv = fit.kick_r.filter(pl.col("cls") == c).join(
                kicks.unique(["day", "row", "minute", "cls"]).select("day", "row", "minute", "cls", pl.col("msg").alias("cluster")),
                on=["day", "row", "minute", "cls"], how="left")
            st = stability(dsub, kick_values=kv)
            # outage-masked daily series (A2)
            dso = daily_activity(fo).filter(pl.col("cls") == c).select("day", "n", "chi", "se")
            kvo = fo.kick_r.filter(pl.col("cls") == c).join(
                kicks.unique(["day", "row", "minute", "cls"]).select("day", "row", "minute", "cls", pl.col("msg").alias("cluster")),
                on=["day", "row", "minute", "cls"], how="left")
            so = stability(dso, kick_values=kvo)
            keys_ = ("n_days_eligible", "p_perm", "p_perm_msg", "p_perm_agent", "R1_perm", "R1_perm_msg", "R1_perm_agent",
                     "lag1", "p_lag1")
            st["outage_masked"] = {k: so.get(k) for k in keys_}
            for lab_, fv in (("nofe", f_nofe), ("agentday", f_ad)):
                dsv = daily_activity(fv).filter(pl.col("cls") == c).select("day", "n", "chi", "se")
                kvv = fv.kick_r.filter(pl.col("cls") == c).join(
                    kicks.unique(["day", "row", "minute", "cls"]).select("day", "row", "minute", "cls", pl.col("msg").alias("cluster")),
                    on=["day", "row", "minute", "cls"], how="left")
                sv = stability(dsv, kick_values=kvv)
                st[lab_] = {k: sv.get(k) for k in keys_}
        else:
            kv = content.filter((pl.col("cls") == c) & pl.col("chi_orth").is_not_nan()).select(
                "day", "agent", pl.col("msg").alias("cluster"), pl.col("chi_orth").alias("r"))
            st = stability(dsub, kick_values=kv, weight_col=None)
        if st.get("n_days_eligible", 0) >= 4:
            st["windows"] = [window_reliability(dsub, w) for w in (2, 3, 5, 10)]
        stab[f"{ch}_{c}"] = st
    R["stability"] = stab

    # ------------------------------------------------------------------ aging, context fill, tokens, family
    cov = {}
    for c in ("N_tgt", "H_und", "H_men"):
        k = kr.filter(pl.col("cls") == c)
        if k.height < 15:
            continue
        y, w, ag, dd = k["r"].to_numpy(), k["w"].to_numpy(), k["agent"].to_numpy(), k["day"].to_numpy()
        e = {"age": wls_slope(y, k["goal_day"].to_numpy().astype(float), w, groups=ag, clusters=dd)}
        fl = k["fill"].to_numpy().astype(float)
        e["fill"] = wls_slope(y, fl, w, groups=ag, clusters=dd)
        pt = k["ptok"].to_numpy().astype(float)
        e["log_ptok"] = wls_slope(y, np.log(np.where(pt > 0, pt, np.nan)), w, groups=ag, clusters=dd)
        thirds = {}
        for lab_, lo, hi in (("early", 0, 13), ("mid", 14, 27), ("late", 28, 10 ** 6)):
            m_ = (fl >= lo) & (fl <= hi) & np.isfinite(fl)
            if m_.sum() >= 5:
                # day bootstrap of the weighted mean
                S_ = np.bincount(dd[m_], weights=(y * w)[m_], minlength=nd); N_ = np.bincount(dd[m_], weights=w[m_], minlength=nd)
                with np.errstate(invalid="ignore", divide="ignore"):
                    thirds[lab_] = ci((W @ S_) / (W @ N_)) + [int(m_.sum())]
        e["thirds"] = thirds
        if "early" in thirds and "late" in thirds:
            m_e = (fl <= 13); m_l = (fl >= 28)
            Se = np.bincount(dd[m_e], weights=(y * w)[m_e], minlength=nd); Ne = np.bincount(dd[m_e], weights=w[m_e], minlength=nd)
            Sl = np.bincount(dd[m_l], weights=(y * w)[m_l], minlength=nd); Nl = np.bincount(dd[m_l], weights=w[m_l], minlength=nd)
            with np.errstate(invalid="ignore", divide="ignore"):
                e["early_minus_late"] = ci((W @ Se) / (W @ Ne) - (W @ Sl) / (W @ Nl))
                e["early_over_late"] = ci(((W @ Se) / (W @ Ne)) / ((W @ Sl) / (W @ Nl)))
        cov[f"act_{c}"] = e
    for c in ("N_tgt", "H_und", "H_men"):
        sub = content.filter((pl.col("cls") == c) & pl.col("chi_orth").is_not_nan()).join(
            kicks.with_row_index("pair").with_columns(pl.col("pair").cast(pl.Int64)).select("pair", "fill", "goal_day"), on="pair", how="left")
        if sub.height < 15:
            continue
        y = sub["chi_orth"].to_numpy(); ag = sub["agent"].to_numpy(); dd = sub["day"].to_numpy()
        cov[f"con_{c}"] = {"age": wls_slope(y, sub["goal_day"].to_numpy().astype(float), np.ones(len(y)), groups=ag, clusters=dd),
                           "fill": wls_slope(y, sub["fill"].to_numpy().astype(float), np.ones(len(y)), groups=ag, clusters=dd)}
    R["covariates"] = cov
    fam = {}
    k = kr.filter(pl.col("cls") == "N_tgt")
    if k.height >= 30:
        pooled = R["act"]["N_tgt"][0] if R["act"].get("N_tgt") else np.nan
        rows = []
        for (lb,), g in k.group_by(["lab"]):
            if g.height < 15 or lb is None:
                continue
            dd = g["day"].to_numpy(); y = g["r"].to_numpy(); w = g["w"].to_numpy()
            S_ = np.bincount(dd, weights=y * w, minlength=nd); N_ = np.bincount(dd, weights=w, minlength=nd)
            with np.errstate(invalid="ignore", divide="ignore"):
                bt = (W @ S_) / (W @ N_)
            c_ = ci(bt)
            sd = float(np.nanstd(bt[1:]))
            z = (c_[0] - pooled) / sd if sd > 0 else np.nan
            rows.append({"lab": lb, "n": g.height, "chi": c_, "z_vs_pooled": z,
                         "p": float(2 * stats.norm.sf(abs(z))) if np.isfinite(z) else np.nan})
        rows.sort(key=lambda r: r["p"] if np.isfinite(r["p"]) else 9)
        mH = len(rows)
        for i, r in enumerate(rows):
            r["p_holm"] = min(1.0, r["p"] * (mH - i)) if np.isfinite(r["p"]) else np.nan
        fam = {"pooled": pooled, "labs": rows}
    R["family"] = fam

    # ------------------------------------------------------------------ context fill with phase-matched controls (A2)
    try:
        ph = cell_fill_phase(base, panels, info["regime"])
        idx = []
        for d_, r_, m_ in kicks.select("day", "row", "minute").iter_rows():
            start, mm_ = base.offsets.get(d_, (0, np.zeros(0, int)))
            na_ = base.shapes[d_][0]
            if len(mm_) == 0 or m_ < mm_[0] or m_ > mm_[-1] or r_ >= na_:
                idx.append(-1)
            else:
                idx.append(start + r_ * len(mm_) + (m_ - mm_[0]))
        idx = np.array(idx)
        kph = np.where(idx >= 0, ph[np.clip(idx, 0, None)], 3)
        ks = kicks.with_columns(pl.Series("phase", kph)).with_columns(
            pl.when(pl.col("cls") == "N_tgt").then(pl.lit("N_tgt_f") + pl.col("phase").cast(pl.Utf8)).otherwise(pl.col("cls")).alias("cls"))
        FC = ("N_tgt_f0", "N_tgt_f1", "N_tgt_f2", "N_tgt_f3", "N_by", "H_men", "H_und")
        Xf = kick_columns(base, ks, classes=FC)
        ff = fit_activity(base, Xf, classes=FC, strata_extra=ph)
        pcf = period_ci(ff, W)
        rows_ = {c: boot_rows(ff, W, c) for c in FC[:3] if c in pcf}
        fp = {"phase_share_cells": [float((ph == q).mean()) for q in range(4)],
              "chi": {c: pcf.get(c) for c in FC[:4]}, "n": {c: pcf.get(c + "_n") for c in FC[:4]}}
        if "N_tgt_f0" in rows_ and "N_tgt_f2" in rows_:
            fp["early_minus_late"] = ci(rows_["N_tgt_f0"] - rows_["N_tgt_f2"])
        R["fill_phase"] = fp
    except Exception as ex:  # noqa: BLE001
        R["fill_phase"] = {"error": str(ex)[:200]}

    # ------------------------------------------------------------------ H04 cross-check
    if do_h04:
        try:
            msgs = load_operator_messages(days)
            R["h04_crosscheck"] = h04_crosscheck(days, msgs)
        except Exception as ex:  # noqa: BLE001
            R["h04_crosscheck"] = {"error": str(ex)[:200]}

    R["verdict"] = verdicts(p, R)
    R["scorecard"] = period_scorecard(p, R)
    R["secs"] = round(time.time() - t0, 1)
    jdump(R, out_dir / "results.json")
    plot_daily(p, daily, R, fig_dir)
    return R


# ============================================================================ verdicts

def verdicts(p: str, R: dict) -> dict:
    kind = KIND.get(p, "nudge_low")
    rows = []
    act, con, st, cov = R["act"], R["con"], R["stability"], R["covariates"]
    sw = R["swap_null"]

    def add(id_, obs, null, verdict):
        rows.append({"id": id_, "observed": obs, "null": null, "verdict": verdict})

    act_fe = act
    act = R.get("act_nofe", act)   # levels: pre-registered model (no day FE); day-FE values shown as sensitivity
    a = act.get("N_tgt")
    if a and R["act_n"].get("N_tgt", 0) >= 5:
        nulls = f"day-swap {fci(sw.get('N_tgt'))}" if sw.get("N_tgt") else ""
        if kind in ("G38", "G51"):
            if a[1] > 0 and 0.8 <= a[0] <= 2.5:
                v = "supported"
            elif a[1] > 0:
                v = "sign supported, size outside 0.8–2.5"
            elif a[2] < 0:
                v = "failed (negative)"
            else:
                v = "not supported (CI includes 0)"
        else:
            v = "supported (point > 0)" if a[0] > 0 else "failed (point ≤ 0)"
            if a[1] > 0:
                v += "; CI excludes 0"
        fr = R.get("act_first", {}).get("N_tgt"); rp = R.get("act_repeat", {}).get("N_tgt")
        om = R.get("act_outage_masked_ci", {}).get("N_tgt")
        dfe = act_fe.get("N_tgt")
        ls_ = R.get("lull_split", {})
        add("P1 χ_act(N_tgt), min per nudge (pre-registered model)",
            f"{fci(a)} (n = {R['act_n']['N_tgt']}); with day FE (A2) {fci(dfe)}: first nudge in 30 min {fci(fr)}, repeat {fci(rp)}, "
            f"outage-masked {fci(om)}, swarm lull {fci(ls_.get('lull', {}).get('N_tgt'))} vs not {fci(ls_.get('no_lull', {}).get('N_tgt'))}",
            nulls, v)
    b = act.get("N_by")
    if b and R["act_n"].get("N_by", 0) >= 20:
        v = "supported" if abs(b[0]) <= 0.15 else "failed"
        coll = R["collective"].get("nudge", {})
        bfe = act_fe.get("N_by"); cfe = R.get("collective_dayfe", {}).get("nudge", {})
        ls_ = R.get("lull_split", {})
        add("P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model)",
            f"{fci(b)}; χ_coll {fci(coll.get('chi_coll_per_msg'))} ({fnum(coll.get('bystanders_per_msg'), 1)} bystanders/nudge); "
            f"with day FE {fci(bfe)}, χ_coll {fci(cfe.get('chi_coll_per_msg'))}; day FE within swarm lulls "
            f"{fci(ls_.get('lull', {}).get('N_by'))} / outside {fci(ls_.get('no_lull', {}).get('N_by'))}",
            f"day-swap {fci(sw.get('N_by'))}", v)
    if kind in ("human_dense", "G44"):
        hm, hu = act.get("H_men"), act.get("H_und")
        if hm and hu:
            ratio = hm[0] / hu[0] if hu[0] not in (0, None) else np.nan
            ok_ratio = np.isfinite(ratio) and hu[0] > 0 and ratio >= 2
            v = ("supported" if ok_ratio and hu[1] > 0 else
                 "partly (H_men > H_und, H_und CI includes 0)" if hm[0] > hu[0] and not hu[1] > 0 else
                 "partly (H_und > 0, ratio < 2)" if hu[1] > 0 else "failed")
            add("P3 χ_act(H_men) vs χ_act(H_und), min per message-recipient", f"H_men {fci(hm)}; H_und {fci(hu)}; ratio {fnum(ratio)}",
                f"day-swap H_und {fci(sw.get('H_und'))}", v)
        for c in ("H_und", "H_men"):
            cc = con.get(c)
            if cc:
                o = cc["orth"]
                v = ("supported" if o[1] is not None and o[1] > 0 and 0.02 <= o[0] <= 0.10 else
                     "sign supported, size outside 0.02–0.10" if o[1] is not None and o[1] > 0 else
                     "failed (negative)" if o[2] is not None and o[2] < 0 else "not supported (CI includes 0)")
                add(f"P4 χ_con({c}), cosine", f"{fci(o, 3)} (n = {cc['n']}; matched {fci(cc['matched'], 3)})",
                    f"pseudo-true null {fci(cc['pseudo_null_orth'], 3)}", v)
    if kind in ("G38", "G41", "G51"):
        cc = con.get("N_tgt")
        if cc:
            o = cc["orth"]
            if kind == "G51":
                v = "supported" if abs(o[0]) < 0.02 and o[1] <= 0 <= o[2] else "failed"
            else:
                v = "positive (CI excludes 0)" if o[1] > 0 else ("negative (CI excludes 0)" if o[2] < 0 else "CI includes 0")
            add("P5 χ_con(N_tgt), cosine", f"{fci(o, 3)} (n = {cc['n']}; matched {fci(cc['matched'], 3)})",
                f"pseudo-true null {fci(cc['pseudo_null_orth'], 3)}", v)
    s = st.get("act_N_tgt")
    if kind in ("G38", "G51") and s and s.get("n_days_eligible", 0) >= 4:
        pm = s.get("p_perm_msg", s.get("p_perm", 1)); r1 = s.get("R1_perm_msg", s.get("R1_perm", 0))
        ok = (pm >= 0.05) and (r1 < 0.3)
        lag = s.get("lag1"); plag = s.get("p_lag1")
        v = "supported" if ok and (plag is None or plag >= 0.05) else "failed"
        so = s.get("outage_masked", {})
        add("P6 daily χ_act(N_tgt) stability",
            f"perm p (msg) {fnum(pm, 3)}, within-agent {fnum(s.get('p_perm_agent'), 3)}; R₁(perm, msg) {fnum(r1)}, within-agent "
            f"{fnum(s.get('R1_perm_agent'))}; lag-1 {fnum(lag)} (p {fnum(plag, 3)}); {s['n_days_eligible']} days, median "
            f"{fnum(s.get('median_n'), 0)} kicks/day; Q p {fnum(s.get('p_Q'), 3)}; outage-masked: p {fnum(so.get('p_perm_msg'), 3)}, "
            f"R₁ {fnum(so.get('R1_perm_msg'))}; no day FE (pre-registered): p {fnum(s.get('nofe', {}).get('p_perm_msg'), 3)}, "
            f"R₁ {fnum(s.get('nofe', {}).get('R1_perm_msg'))}; agent-day FE: p {fnum(s.get('agentday', {}).get('p_perm_msg'), 3)}, "
            f"R₁ {fnum(s.get('agentday', {}).get('R1_perm_msg'))}", "constant χ", v)
    for c in ("H_und", "H_men", "N_tgt"):
        s = st.get(f"con_{c}")
        if s and s.get("n_days_eligible", 0) >= 4 and (kind in ("human_dense", "G51", "G38") or c != "N_tgt"):
            r1 = s.get("R1_perm_msg", s.get("R1_perm")) or 0
            v = "supported (R₁ < 0.5)" if r1 < 0.5 else "failed (R₁ ≥ 0.5)"
            add(f"P6 daily χ_con({c}) stability",
                f"perm p (msg) {fnum(s.get('p_perm_msg'), 3)} (kick-level {fnum(s.get('p_perm'), 3)}); R₁(perm, msg) {fnum(r1)}; "
                f"lag-1 {fnum(s.get('lag1'))}; {s['n_days_eligible']} days, median {fnum(s.get('median_n'), 0)} pairs/day",
                "constant χ", v)
    if kind in ("G38", "G51"):
        e = cov.get("act_N_tgt", {}).get("age")
        if e and "slope" in e:
            v = "supported (no aging)" if e["lo"] <= 0 <= e["hi"] else ("failed: aging (negative slope)" if e["hi"] < 0 else "failed: rising")
            add("P7 aging: d r / d goal-day (activity, N_tgt)", f"{fnum(e['slope'], 3)} [{fnum(e['lo'], 3)}, {fnum(e['hi'], 3)}] min/day",
                "0", v)
        e = cov.get("act_N_tgt", {})
        if e.get("fill") and "slope" in e["fill"]:
            f_ = e["fill"]; ratio = e.get("early_over_late"); diff = e.get("early_minus_late")
            th = e.get("thirds", {})
            late_pos = th.get("late") and th["late"][0] is not None and th["late"][0] > 0
            neg = f_["hi"] < 0
            rat_ok = late_pos and ratio is not None and ratio[0] is not None and np.isfinite(ratio[0]) and ratio[0] >= 1.3
            v = ("supported" if neg and rat_ok else "direction only (slope < 0, CI includes 0)" if f_["slope"] < 0 and not neg
                 else "failed")
            thtxt = ", ".join(f"{k} {fci(th[k])}" for k in ("early", "mid", "late") if k in th)
            fpz = R.get("fill_phase", {})
            fch = fpz.get("chi", {})
            e0, e2 = fch.get("N_tgt_f0"), fch.get("N_tgt_f2")
            if e0 and e2 and e0[0] is not None and e2[0] is not None:
                lp = e2[0] > 0
                rat = e0[0] / e2[0] if lp else np.nan
                d02 = fpz.get("early_minus_late")
                v = ("supported" if lp and rat >= 1.3 and d02 and d02[1] > 0 else
                     "direction only (early > late, CI includes 0)" if e0[0] > e2[0] else "failed (late ≥ early)")
                add("P8 context fill (activity, N_tgt; controls matched on their own fill phase, A2)",
                    f"early (turns 0–13) {fci(e0)} n {fpz['n'].get('N_tgt_f0')}; mid {fci(fch.get('N_tgt_f1'))}; late (28+) {fci(e2)} "
                    f"n {fpz['n'].get('N_tgt_f2')}; early − late {fci(d02)}; pre-registered per-kick slope {fnum(f_['slope'], 3)} "
                    f"[{fnum(f_['lo'], 3)}, {fnum(f_['hi'], 3)}] min/turn", "0; ratio 1", v)
            else:
                add("P8 context fill (activity, N_tgt)", f"slope {fnum(f_['slope'], 3)} [{fnum(f_['lo'], 3)}, {fnum(f_['hi'], 3)}] min/turn; "
                    f"by thirds: {thtxt}; early − late {fci(diff)}" + ("" if late_pos else " (late mean ≤ 0)"), "0; ratio 1", v)
    if kind == "G38":
        pass
    if kind == "G51" and R.get("family", {}).get("labs"):
        labs = R["family"]["labs"]
        sig = [r for r in labs if np.isfinite(r.get("p_holm", np.nan)) and r["p_holm"] < 0.05]
        v = "supported" if not sig else f"failed ({', '.join(r['lab'] for r in sig)})"
        add("P10 family (lab) differences in χ_act(N_tgt)", "; ".join(f"{r['lab']} {fci(r['chi'])} (n {r['n']})" for r in labs), "pooled", v)
    if kind in ("G38", "G51"):
        pp_ = R["pre_placebo_nofe"].get("N_tgt", (None, None))[0] if "pre_placebo_nofe" in R else R["pre_placebo"].get("N_tgt", (None, None))[0]
        pp_fe = R["pre_placebo"].get("N_tgt", (None, None))[0]
        swn = sw.get("N_tgt")
        ok = pp_ is not None and abs(pp_) <= 0.5 and swn is not None and swn[1] <= 0 <= swn[2]
        cn = con.get("N_tgt", {}).get("pseudo_null_orth")
        add("P11 nulls", f"pre-window placebo {fnum(pp_)} (day FE {fnum(pp_fe)}); day-swap {fci(swn)}; pseudo-true content null "
            f"{fci(cn, 3)}", "0", "supported" if ok else "failed")
    # overall per-period verdict
    vs = [r["verdict"] for r in rows]
    if not vs:
        overall = "descriptive (too few kicks)"
    elif all(v.startswith("supported") for v in vs):
        overall = "supported"
    elif not any(v.startswith("supported") or v.startswith("sign supported") or v.startswith("partly") or v.startswith("direction") for v in vs):
        overall = "failed"
    else:
        overall = "mixed"
    if kind == "nudge_low" and overall == "supported":
        overall = "supported (low power)"
    return {"overall": overall, "rows": rows}


def period_scorecard(p: str, R: dict) -> list[str]:
    out = []
    a = R["act"].get("N_tgt") or R["act"].get("H_und")
    if a:
        out.append(f"C: χ_act {'beats' if a[1] is not None and a[1] > 0 else 'does not beat'} the day-swap / zero null at the period level.")
    out.append("D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).")
    out.append("F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).")
    return out


# ============================================================================ figure

def plot_daily(p: str, daily: pl.DataFrame, R: dict, fig_dir: Path):
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
    main_act = "N_tgt" if (R["act_n"].get("N_tgt") or 0) >= 20 else "H_und"
    for a_, ch, cls_list, ylab in ((ax[0], "act", [main_act], "extra active min / kick (30 min)"),
                                   (ax[1], "con", ["N_tgt", "H_und", "H_men"], "content χ (cosine)")):
        for k, c in enumerate(cls_list):
            d = daily.filter((pl.col("channel") == ch) & (pl.col("cls") == c) & (pl.col("n") >= 3)).sort("day")
            if d.height == 0:
                continue
            x = d["goal_day"].to_numpy() + 0.15 * k
            a_.errorbar(x, d["chi"].to_numpy(), yerr=1.96 * d["se"].to_numpy(), fmt="o", ms=3, lw=0.8, capsize=0,
                        label=f"{c} (n/day med {int(np.median(d['n'].to_numpy()))})")
            per = R["act"].get(c) if ch == "act" else (R["con"].get(c) or {}).get("orth")
            if per and per[0] is not None and np.isfinite(per[0]):
                a_.axhline(per[0], color=a_.lines[-1].get_color() if a_.lines else "k", lw=0.8, ls="--")
        a_.axhline(0, color="0.6", lw=0.6)
        a_.set_xlabel("day in goal period"); a_.set_ylabel(ylab)
        a_.legend(fontsize=7, frameon=False)
    ax[0].set_title(f"H30 {p}: daily activity gauge", fontsize=9)
    ax[1].set_title("daily content gauge (orthogonalized)", fontsize=9)
    fig.tight_layout()
    fig.savefig(fig_dir / "daily_gauge.pdf")
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--no-h04", action="store_true")
    a = ap.parse_args()
    todo = PERIODS if a.all else [a.period]
    for p in todo:
        R = run_period(p, do_h04=not a.no_h04)
        print(p, R["secs"], "s;", R["verdict"]["overall"], flush=True)
        for r in R["verdict"]["rows"]:
            print("   ", r["id"], "|", r["observed"], "|", r["verdict"], flush=True)
