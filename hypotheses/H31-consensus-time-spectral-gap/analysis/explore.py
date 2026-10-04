"""H31 exploratory round 1 on non-holdout periods: consensus events (E-P, E-V, E-C), their times, event-window
predictors, and the cross-period tests T1-T7 of the card. Writes per-period results.json and cross-period outputs.

  uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/explore.py [--W 30]
Outputs in data/processed/H31-consensus-time-spectral-gap/: G<NN>/results.json, events_ep_w{W}.parquet,
events_ec.parquet, ev26.json, cross_period_w{W}.json, frozen_rule.json (W = 30 only).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h31lib as L  # noqa: E402
from predictors import block_predictors  # noqa: E402
from synthetic import SIGN, eligible_blocks  # noqa: E402

ROOMS = {0: "#general", 2: "#best", 3: "#rest", 4: "#universe-coordination"}
PRIMARY = "l2_sym"
SECONDARY = ["l2_dir", "l2_bin", "ul2_rw", "g_tr", "l2_ment"]
MODELS_FIXED = {"M_l2_sym": "l2_sym", "M_g_tr": "g_tr", "M_tau_V": "tau_V", "M_tau_wave": "tau_wave",
                # Amendment 2 (2026-10-03, after the synthetic run, before any real-data event detection)
                "M_ul2_rw": "ul2_rw", "M_l2_sym_core": "l2_sym_core"}


# ------------------------------------------------------------------------------------------------ per-period
def label_matrix(P, b, W):
    """(G, N) labels for block b on the W-min grid, act_h per window, N_b per window, agent list."""
    st = P[f"states{W}"]
    days = P["days"]
    rows = []
    for r in days.iter_rows(named=True):
        nk = int(-(-r["window_s"] // (W * 60))) if r["window_s"] else 1
        for k in range(max(nk, 1)):
            rows.append((r["day"], k, (r["act0"] + min(k * W * 60 + W * 30, r["window_s"])) / 3600))
    grid = pl.DataFrame(rows, schema=["day", "win", "act_h"], orient="row").with_columns(
        pl.col("day").cast(pl.Int16), pl.col("win").cast(pl.Int16))
    bw = P["block_windows"].filter(pl.col("room") == b).with_columns((pl.col("act_mid") / 3600).alias("a"))
    # N_b per W-window: nearest 30-min block window (same day)
    nb30 = bw.group_by("day", "win", "a").agg(pl.col("agent").n_unique().alias("nb")).sort("a")
    a30, n30 = nb30["a"].to_numpy(), nb30["nb"].to_numpy()
    idx = np.clip(np.searchsorted(a30, grid["act_h"].to_numpy()), 0, max(len(a30) - 1, 0))
    Nb = n30[idx].astype(float) if len(a30) else np.zeros(grid.height)
    s = st.filter(pl.col("room") == b)
    agents = sorted(set(bw["agent"].drop_nulls().to_list()) | set(s["agent"].to_list()))
    pos = {a: i for i, a in enumerate(agents)}
    gpos = {(d, w): i for i, (d, w) in enumerate(zip(grid["day"].to_list(), grid["win"].to_list()))}
    lab = np.full((grid.height, len(agents)), -1, np.int16)
    for d, w, a, l in s.select("day", "win", "agent", "label").iter_rows():
        k = gpos.get((d, w))
        if k is not None:
            lab[k, pos[a]] = l
    return lab, grid["act_h"].to_numpy(), Nb, agents


def kick_times(P, b):
    k = P["kicks"]
    hm = k.filter((pl.col("kind") == "human_message") & (pl.col("room") == b))["act"].to_numpy() / 3600
    return np.sort(np.r_[hm, 0.0])          # 0.0 = the goal kickoff (period's first window)


def kick_locked(t_c, kicks, w_h=L.W_H):
    """A kick in [t_c - 1 h, t_c + W/2]."""
    j = np.searchsorted(kicks, t_c + w_h / 2, side="right")
    return bool(j > 0 and kicks[j - 1] >= t_c - 1.0)


def ep_period(P, b, W, with_window_pred=True):
    lab, act_h, Nb, agents = label_matrix(P, b, W)
    evs = L.detect_project_events(lab, act_h, Nb, w_h=W / 60)
    kicks = kick_times(P, b)
    day_of = P["days"]
    out = []
    for e in evs:
        if not e["consensus"]:
            out.append(dict(room=b, label=e["label"], consensus=False, frozen=False, max_n=e["max_n"]))
            continue
        tc_h, t0_h = float(act_h[e["tc"]]), float(act_h[e["t0"]])
        d = dict(room=b, label=e["label"], consensus=True, frozen=e["frozen"], tau_h=e["tau_h"], t0_h=t0_h, tc_h=tc_h,
                 rise=e["rise"], max_n=e["max_n"], kick_locked=kick_locked(tc_h, kicks, W / 60))
        if with_window_pred and not e["frozen"]:
            a0 = t0_h * 3600
            pw = block_predictors(P, b, a0, a0 + L.EVENT_WINDOW_H * 3600, with_voter=False)
            if pw:
                for k in ("l2_sym", "l2_dir", "l2_bin", "ul2_rw", "g_tr", "u", "N_b", "tau_wave", "l2_ment", "msg_rate"):
                    d["ew_" + k] = pw[k]
        out.append(d)
    # placebo kick locking: random windows of the same block-days as the consensus windows
    return out, dict(act_h=act_h.tolist(), kicks=kicks.tolist())


def ec_period(P, b):
    if P["alignment"] is None:
        return None
    T_h = L.period_T(P) / 3600
    f = L.detect_content_event(P["alignment"], b, T_h)
    f["room"] = b
    if f.get("kind") == "convergence":
        pw = block_predictors(P, b, 0.0, L.EVENT_WINDOW_H * 3600, with_voter=False)
        if pw:
            for k in ("l2_sym", "g_tr", "ul2_rw", "u", "N_b"):
                f["ew_" + k] = pw[k]
    return f


def ev26():
    """E-V: #26 runoff, from H11's votes.parquet (first-person single-candidate declarations, carried forward).
    Round 1b (H31_EV26=dq6): per election round from DQ6 ballots instead (ev26_dq6.py); the runoff round fills the
    top-level keys used downstream, and all three rounds are under 'rounds'."""
    if os.environ.get("H31_EV26", "keyword") == "dq6":
        from ev26_dq6 import ev26_rounds
        return ev26_rounds(L.load_period(26))
    v = pl.read_parquet(L.ROOT / "data/processed/H11-potts-labor-vs-herding/G26/votes.parquet").sort("t")
    P = L.load_period(26)
    days = P["days"]
    import importlib.util
    spec = importlib.util.spec_from_file_location("h31b", L.HYP / "scheme/build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    clock = mod.ActiveClock(days.with_columns(pl.col("act0")))
    v = v.with_columns(pl.Series("act_h", clock(v["t"].dt.epoch("us").to_numpy()) / 3600))
    run = v.filter(pl.col("runoff_word"))
    if run.height == 0:
        return {"status": "no runoff messages"}
    onset = float(run["act_h"][0])
    dec = v.filter(pl.col("vote_word") & pl.col("first_person") & pl.col("candidate").is_not_null())
    # approval round: from the first declaration to the onset (counted only)
    pre = dec.filter(pl.col("act_h") < onset)
    post = dec.filter(pl.col("act_h") >= onset)
    last = {}
    for a, c in zip(post["agent"].to_list(), post["candidate"].to_list()):
        last[a] = c
    winner = max(set(last.values()), key=list(last.values()).count) if last else None
    cur = {}
    t_cons, share_at = None, []
    for a, c, t in zip(post["agent"].to_list(), post["candidate"].to_list(), post["act_h"].to_list()):
        cur[a] = c
        n = len(cur)
        sh = sum(1 for x in cur.values() if x == winner) / n
        share_at.append((t, sh, n))
        if t_cons is None and n >= 3 and sh >= 0.5:
            t_cons = t
    # approval round shares (descriptive)
    curp = {}
    for a, c in zip(pre["agent"].to_list(), pre["candidate"].to_list()):
        curp[a] = c
    counts = {}
    for c in curp.values():
        counts[c] = counts.get(c, 0) + 1
    rise = sb = None
    if t_cons is not None:
        tt = np.array([a[0] for a in share_at]); ss = np.array([a[1] for a in share_at]); nn = np.array([a[2] for a in share_at])
        k = int(np.flatnonzero((tt == t_cons))[0])
        pre = np.flatnonzero((nn[:k] >= 3) & (ss[:k] < 0.25))
        if len(pre):
            rise, sb = float(t_cons - tt[pre[-1]]), float(ss[pre[-1]])
    return {"rise_posthoc_h": rise, "share_before_posthoc": sb,
            "onset_h": onset, "winner": int(winner) if winner is not None else None,
            "t_cons_h": t_cons, "tau_V_h": (t_cons - onset) if t_cons is not None else None,
            "n_declared_post": len(cur), "final_share": share_at[-1][1] if share_at else None,
            "pre_runoff_max_share": (max(counts.values()) / max(len(curp), 1)) if counts else None,
            "pre_runoff_n": len(curp), "trajectory": share_at[:60]}


def period_job(args):
    g, W, elig = args
    P = L.load_period(g)
    blocks = L.blocks_of(P)
    res = {"goal_no": g, "blocks": blocks, "T_h": L.period_T(P) / 3600, "ep": [], "ec": [], "grids": {}}
    for b in blocks:
        if (g, b) in elig and P[f"states{W}"] is not None:
            evs, grid = ep_period(P, b, W, with_window_pred=(W == 30))
            res["ep"].extend(evs)
            res["grids"][str(b)] = grid
        if W == 30:
            f = ec_period(P, b)
            if f is not None:
                res["ec"].append(f)
    return res


# ------------------------------------------------------------------------------------------------ cross-period
def slope_table(d: pl.DataFrame, y: np.ndarray, preds, prefix=""):
    out = {}
    cl = d["goal_no"].to_numpy()
    for p in preds:
        col = prefix + p
        if col not in d.columns:
            continue
        v = d[col].to_numpy().astype(float)
        x = SIGN.get(p, -1) * np.log(np.maximum(v, 1e-6))
        ok = np.isfinite(x) & np.isfinite(y) & (v > 0)
        if ok.sum() < 4 or len(np.unique(cl[ok])) < 3:
            out[p] = dict(n=int(ok.sum()), b=None)
            continue
        b, ci = L.cluster_boot_slope(x[ok], y[ok], cl[ok], B=2000, seed=31)
        # permutation of the predictor across periods (N2)
        rng = np.random.default_rng(7)
        u = np.unique(cl[ok])
        xm = {c: x[ok][cl[ok] == c].mean() for c in u}
        perm = []
        for _ in range(2000):
            sh = dict(zip(u, rng.permutation([xm[c] for c in u])))
            xp = np.array([sh[c] for c in cl[ok]])
            perm.append(L.ols(xp, y[ok])[1])
        p_perm = float(np.mean(np.abs(perm) >= abs(b)))
        out[p] = dict(n=int(ok.sum()), n_periods=int(len(u)), b=b, lo=ci[0], hi=ci[1], p_perm=p_perm)
    # Holm over the secondary predictors (two-sided permutation p)
    sec = [(p, out[p]["p_perm"]) for p in preds[1:] if p in out and out[p].get("b") is not None]
    sec.sort(key=lambda z: z[1])
    m = len(sec)
    for k, (p, pv) in enumerate(sec):
        out[p]["p_holm"] = float(min(1.0, max(pv * (m - k), max([out[q]["p_holm"] for q, _ in sec[:k]] or [0]))))
    return out


def lopo_table(d: pl.DataFrame, y: np.ndarray, prefix=""):
    cl = d["goal_no"].to_numpy()
    pr = {"M0": L.lopo(y, cl)}
    for name, p in MODELS_FIXED.items():
        col = prefix + p
        if col in d.columns:
            v = d[col].to_numpy().astype(float)
            pr[name] = L.lopo(y, cl, offset=SIGN[p] * np.log(np.maximum(v, 1e-6)))
    if prefix + PRIMARY in d.columns:
        pr["M_l2_sym_free"] = L.lopo(y, cl, X=(-np.log(np.maximum(d[prefix + PRIMARY].to_numpy(), 1e-6)))[:, None])
    pr["M_N"] = L.lopo(y, cl, X=np.log(d[prefix + "N_b"].to_numpy().astype(float))[:, None])
    rm = {k: L.rmse(y, v) for k, v in pr.items()}
    return rm, pr


def two_room_contrast(ep: pl.DataFrame, pred: pl.DataFrame):
    out = []
    unc = ep.filter(pl.col("consensus") & ~pl.col("frozen"))
    for g in sorted(unc["goal_no"].unique().to_list()):
        sub = unc.filter(pl.col("goal_no") == g)
        rooms = sorted(sub["room"].unique().to_list())
        pg = pred.filter(pl.col("goal_no") == g)
        if len(rooms) < 2 or pg.height < 2:
            continue
        med = {r: float(np.exp(np.log(sub.filter(pl.col("room") == r)["tau_h"].to_numpy()).mean())) for r in rooms}
        pr = {r: pg.filter(pl.col("room") == r).row(0, named=True) for r in rooms}
        small = min(rooms, key=lambda r: pr[r]["N_b"])
        large = max(rooms, key=lambda r: pr[r]["N_b"])
        obs = np.log(med[small] / med[large])
        d_pred = np.log(pr[large]["l2_sym"] / pr[small]["l2_sym"])     # D: tau ~ 1/l2 -> log(tau_s/tau_l) = log(l2_l/l2_s)
        v_pred = np.log(pr[small]["N_b"] / pr[large]["N_b"])            # V: tau ~ N
        out.append(dict(goal_no=g, small=small, large=large, tau_small=med[small], tau_large=med[large],
                        log_ratio_obs=float(obs), D_pred=float(d_pred), V_pred=float(v_pred),
                        agrees_D=bool(np.sign(obs) == np.sign(d_pred)), agrees_V=bool(np.sign(obs) == np.sign(v_pred))))
    return out


def placebo_kicks(results, ep: pl.DataFrame, n_perm=2000, seed=11):
    """K = fraction of uncensored+frozen consensus windows kick-locked; placebo = random windows of the same block
    and day (matched by the event's day), permutation p."""
    rng = np.random.default_rng(seed)
    cons = ep.filter(pl.col("consensus"))
    if cons.height == 0:
        return {}
    k_obs = float(cons["kick_locked"].mean())
    perms = np.zeros(n_perm)
    base = []
    grids = {(r["goal_no"], int(b)): g for r in results for b, g in r["grids"].items()}
    for row in cons.iter_rows(named=True):
        gr = grids[(row["goal_no"], row["room"])]
        act = np.array(gr["act_h"])
        kicks = np.array(gr["kicks"])
        # windows of the same active day: same integer part of the day index via the gap structure
        tc = row["tc_h"]
        same = act[np.abs(act - tc) <= 8.0]        # within one long active day either side
        locked = np.array([kick_locked(t, kicks) for t in same])
        base.append(locked.mean())
        perms += rng.random(n_perm) < locked.mean()
    perms /= cons.height
    return {"K_obs": k_obs, "K_placebo": float(np.mean(base)), "ratio": k_obs / max(np.mean(base), 1e-9),
            "p_perm": float(np.mean(perms >= k_obs)), "n": cons.height}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--W", type=int, default=30)
    a = ap.parse_args()
    W = a.W
    elig = set(eligible_blocks())
    goals = sorted(int(p.name[1:]) for p in L.DATA.glob("G*") if p.is_dir())
    with ProcessPoolExecutor(max_workers=2) as ex:
        results = list(ex.map(period_job, [(g, W, elig) for g in goals]))
    pp = pl.read_parquet(L.DATA / "predictors_period.parquet")
    core = pp.filter(pl.col("variant") == "core").select("goal_no", "room", pl.col("l2_sym").alias("l2_sym_core"),
                                                         pl.col("g_tr").alias("g_tr_core"))
    pred = pp.filter(pl.col("variant") == "all").join(core, on=["goal_no", "room"], how="left")

    ep_rows = [dict(goal_no=r["goal_no"], **e) for r in results for e in r["ep"]]
    ep = pl.DataFrame(ep_rows, infer_schema_length=None) if ep_rows else pl.DataFrame()
    ep = ep.join(pred.drop("variant"), on=["goal_no", "room"], how="left")
    ep.write_parquet(L.DATA / f"events_ep_w{W}{L.SUFFIX}.parquet", compression="zstd")
    cross = {"W": W, "n_eligible_blocks": len(elig)}
    unc = ep.filter(pl.col("consensus") & ~pl.col("frozen"))
    y = np.log(unc["tau_h"].to_numpy())
    cross["ep_counts"] = dict(projects=ep.height, consensus=int(ep["consensus"].sum()),
                              frozen=int(ep.filter(pl.col("consensus"))["frozen"].sum()), uncensored=unc.height,
                              no_consensus=int((~ep["consensus"]).sum()),
                              periods_with_uncensored=int(unc["goal_no"].n_unique()),
                              blocks_with_uncensored=int(unc.select("goal_no", "room").unique().height))
    cross["ep_tau"] = dict(median=float(np.median(unc["tau_h"])), q10=float(np.quantile(unc["tau_h"], .1)),
                           q90=float(np.quantile(unc["tau_h"], .9)), sd_log=float(np.std(y)))
    preds_all = [PRIMARY] + SECONDARY + ["l2_sym_core", "u", "tau_wave", "tau_V", "N_b"]
    cross["T1_slopes_period"] = slope_table(unc, y, [PRIMARY] + SECONDARY)
    cross["T1_slopes_other"] = slope_table(unc, y, ["l2_sym_core", "g_tr_core", "u", "tau_wave", "tau_V", "N_b"])
    if W == 30:
        cross["T1_slopes_eventwindow"] = slope_table(unc, y, [PRIMARY] + SECONDARY + ["N_b"], prefix="ew_")
    rm, prd = lopo_table(unc, y)
    cross["T3_lopo_rmse"] = rm
    cross["T2_N"] = cross["T1_slopes_other"].get("N_b")
    rise = unc["rise"].drop_nulls().to_numpy()
    cross["T5_abrupt"] = dict(n=int(len(rise)), frac_rise_le1=float(np.mean(rise <= 1)) if len(rise) else None,
                              median_rise=float(np.median(rise)) if len(rise) else None)
    cross["T4_kick"] = placebo_kicks(results, ep)
    cross["T6_two_room"] = two_room_contrast(ep, pred)

    # P1 verdict
    t1 = cross["T1_slopes_period"][PRIMARY]
    imp = 1 - rm["M_l2_sym"] / rm["M0"]
    cross["P1"] = dict(b=t1.get("b"), lo=t1.get("lo"), hi=t1.get("hi"), lopo_gain=float(imp),
                       verdict=("supported" if (t1.get("b") is not None and t1["lo"] > 0 and t1["lo"] <= 1 <= t1["hi"] and imp >= 0.05)
                                else "failed" if (t1.get("b") is None or t1["b"] <= 0 or t1["hi"] < 1 or t1["lo"] > 1 or imp <= 0)
                                else "inconclusive"))

    # per-event LOPO errors for per-period verdicts
    unc = unc.with_columns(pl.Series("err_M0", np.abs(prd["M0"] - y)), pl.Series("err_Ml2", np.abs(prd["M_l2_sym"] - y)),
                           pl.Series("pred_Ml2_h", np.exp(prd["M_l2_sym"])), pl.Series("pred_M0_h", np.exp(prd["M0"])))

    # ---- E-C
    ec_rows = [dict(goal_no=r["goal_no"], **{k: v for k, v in e.items() if not isinstance(v, (list, dict))})
               for r in results for e in r["ec"]]
    ec = pl.DataFrame(ec_rows, infer_schema_length=None) if ec_rows else pl.DataFrame()
    if ec.height:
        ec = ec.join(pred.drop("variant"), on=["goal_no", "room"], how="left")
        if not L.SUFFIX:
            ec.write_parquet(L.DATA / "events_ec.parquet", compression="zstd")
        conv = ec.filter(pl.col("kind") == "convergence")
        cross["ec_counts"] = {k: int(v) for k, v in zip(*np.unique(ec["kind"].to_numpy(), return_counts=True))}
        if conv.height >= 4:
            yc = np.log(conv["tau"].to_numpy())
            cross["ec_tau"] = dict(median=float(np.median(conv["tau"])), sd_log=float(np.std(yc)), n=conv.height)
            cross["P5_slopes"] = slope_table(conv, yc, ["g_tr", "l2_sym", "l2_dir", "ul2_rw", "l2_bin", "l2_ment"])
            cross["P5_slopes_other"] = slope_table(conv, yc, ["N_b", "u", "tau_wave"])
            rmc, prc = lopo_table(conv, yc)
            cross["P5_lopo_rmse"] = rmc
            t5 = cross["P5_slopes"]["g_tr"]
            impc = 1 - rmc["M_g_tr"] / rmc["M0"]
            cross["P5"] = dict(b=t5.get("b"), lo=t5.get("lo"), hi=t5.get("hi"), lopo_gain=float(impc),
                               verdict=("supported" if (t5.get("b") is not None and t5["lo"] > 0 and t5["lo"] <= 1 <= t5["hi"] and impc >= 0.05)
                                        else "failed" if (t5.get("b") is None or t5["b"] <= 0 or t5["hi"] < 1 or t5["lo"] > 1 or impc <= 0)
                                        else "inconclusive"))
            conv = conv.with_columns(pl.Series("err_M0", np.abs(prc["M0"] - yc)), pl.Series("err_Mtr", np.abs(prc["M_g_tr"] - yc)))
        else:
            cross["P5"] = dict(verdict="inconclusive (too few convergence events)", n=conv.height)
    else:
        conv = pl.DataFrame()

    # ---- E-V and forecast rule (W = 30 only)
    if W == 30 and not L.SUFFIX:
        e26 = ev26()
        p26 = pred.filter(pl.col("goal_no") == 26).row(0, named=True)
        c_lambda = float(np.mean(y + np.log(unc["l2_sym"].to_numpy())))        # log tau = c - log l2
        resid = y - (c_lambda - np.log(unc["l2_sym"].to_numpy()))
        lo_q, hi_q = np.quantile(prd["M_l2_sym"] - y, [0.1, 0.9])              # LOPO residuals
        e26["M_l2_pred_h"] = float(np.exp(c_lambda) / p26["l2_sym"])
        e26["M_l2_80pct_h"] = [float(np.exp(c_lambda - hi_q) / p26["l2_sym"]), float(np.exp(c_lambda - lo_q) / p26["l2_sym"])]
        (L.DATA / "ev26.json").write_text(json.dumps(e26, indent=1, default=float))
        cross["E_V"] = {k: v for k, v in e26.items() if k != "trajectory"}
        # forecast rule
        cand = {k: v for k, v in rm.items() if k in ("M0", "M_l2_sym", "M_g_tr", "M_tau_V", "M_tau_wave", "M_N", "M_ul2_rw", "M_l2_sym_core")}
        best = min(cand, key=lambda k: cand[k])
        rule = {"chosen": best, "lopo_rmse": cand, "event_class": "E-P (W=30)", "n_events": int(len(y)),
                "n_periods": int(unc["goal_no"].n_unique())}
        if best == "M0":
            rule["log_c"] = float(y.mean())
        elif best == "M_N":
            coef = L.ols(np.log(unc["N_b"].to_numpy().astype(float)), y)
            rule["log_c"], rule["a_N"] = float(coef[0]), float(coef[1])
        else:
            p = MODELS_FIXED[best]
            rule["predictor"] = p
            rule["log_c"] = float(np.mean(y - SIGN[p] * np.log(np.maximum(unc[p].to_numpy(), 1e-6))))
        r_lopo = prd[best] - y
        rule["lopo_resid_q10_q90"] = [float(np.quantile(r_lopo, .1)), float(np.quantile(r_lopo, .9))]
        rule["constant_rule"] = {"log_c": float(y.mean()), "lopo_resid_q10_q90": [float(np.quantile(prd['M0'] - y, .1)),
                                                                                  float(np.quantile(prd['M0'] - y, .9))]}
        rule["median_tau_h"] = float(np.median(unc["tau_h"]))
        rule["interval_80_constant_h"] = [float(np.quantile(unc["tau_h"], .1)), float(np.quantile(unc["tau_h"], .9))]
        rule["lambda_rule"] = {"log_c": c_lambda, "lopo_resid_q10_q90": [float(lo_q), float(hi_q)]}
        # post hoc (after round 1): free-slope lambda rule, frozen for confirmation as secondary C1b
        xf = -np.log(unc["l2_sym"].to_numpy())
        cf = L.ols(xf, y)
        rf = prd["M_l2_sym_free"] - y
        rule["lambda_free_rule_posthoc"] = {"log_c": float(cf[0]), "b": float(cf[1]),
                                            "lopo_resid_q10_q90": [float(np.quantile(rf, .1)), float(np.quantile(rf, .9))],
                                            "lopo_rmse": rm["M_l2_sym_free"]}
        rule["frozen_at"] = "2026-10-03 (after exploratory round 1, before any holdout data)"
        cross["forecast_rule"] = rule
        (L.DATA / "frozen_rule.json").write_text(json.dumps(rule, indent=1))

        # per-period results.json
        for r in results:
            g = r["goal_no"]
            write_period_results(g, r, unc, ep, conv, ec, cross, pred, e26 if g == 26 else None)

    (L.DATA / f"cross_period_w{W}{L.SUFFIX}.json").write_text(json.dumps(cross, indent=1, default=float))
    print(json.dumps({k: v for k, v in cross.items() if k not in ("T6_two_room",)}, indent=1, default=float)[:6000])
    print("T6", cross["T6_two_room"])


def write_period_results(g, r, unc, ep, conv, ec, cross, pred, e26):
    rl, sc = [], []
    pe = ep.filter(pl.col("goal_no") == g) if ep.height else ep
    pu = unc.filter(pl.col("goal_no") == g)
    pc = ec.filter(pl.col("goal_no") == g) if ec.height else ec
    verdict_bits = []
    rl.append("| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |")
    rl.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for b in r["blocks"]:
        e = pe.filter(pl.col("room") == b) if pe.height else pe
        u = pu.filter(pl.col("room") == b)
        c = pc.filter(pl.col("room") == b) if pc.height else pc
        n_proj = e.height if e.height else 0
        n_cons = int(e["consensus"].sum()) if e.height else 0
        n_fro = int(e.filter(pl.col("consensus"))["frozen"].sum()) if e.height else 0
        n_inst = int(e.filter(pl.col("consensus") & pl.col("frozen") & (pl.col("t0_h") > 0.75 + 1e-6)).height) if e.height else 0
        taus = ", ".join(f"{x:.1f}" for x in u["tau_h"].to_list()) or "–"
        rises = ", ".join(str(x) for x in u["rise"].to_list()) or "–"
        kl = (f"{int(e.filter(pl.col('consensus'))['kick_locked'].sum())}/{n_cons}" if n_cons else "–")
        fl = ", ".join(f"{x:.1f}" for x in u["pred_Ml2_h"].to_list()) or "–"
        f0 = ", ".join(f"{x:.1f}" for x in u["pred_M0_h"].to_list()) or "–"
        kind = c["kind"][0] if c.height else "n/a"
        tauc = f"{c['tau'][0]:.1f}" if c.height and c["kind"][0] in ("convergence", "divergence") else "–"
        rl.append(f"| {ROOMS.get(b, b)} | {n_proj if n_proj else 'n/a'} | {n_cons} ({n_fro - n_inst} / {n_inst} / {n_cons - n_fro}) | {taus} | {rises} | {kl} | {fl} | {f0} | {kind} | {tauc} |")
    if pu.height:
        better = float(np.mean(pu["err_Ml2"].to_numpy() < pu["err_M0"].to_numpy()))
        verdict_bits.append(("supported" if better > 0.5 else "failed") if pu.height else None)
        rl.append("")
        rl.append(f"- **E-P vs the H31 line:** M_λ (fitted on the other periods) beats the constant forecast for "
                  f"{int(round(better * pu.height))}/{pu.height} uncensored events. Mean |log error| is "
                  f"{pu['err_Ml2'].mean():.2f} (M_λ) vs {pu['err_M0'].mean():.2f} (M0).")
    if conv.height and conv.filter(pl.col("goal_no") == g).height:
        cc = conv.filter(pl.col("goal_no") == g)
        bt = float(np.mean(cc["err_Mtr"].to_numpy() < cc["err_M0"].to_numpy()))
        verdict_bits.append("supported" if bt > 0.5 else "failed")
        rl.append(f"- **E-C vs the γ_tr line:** M_tr beats the constant for {int(round(bt * cc.height))}/{cc.height} convergence events.")
    t6 = [x for x in cross["T6_two_room"] if x["goal_no"] == g]
    if t6:
        x = t6[0]
        rl.append(f"- **T6 room contrast:** τ(small room {ROOMS.get(x['small'])}) / τ(large room {ROOMS.get(x['large'])}) = "
                  f"{np.exp(x['log_ratio_obs']):.2f}. D predicted {np.exp(x['D_pred']):.2f} (sign {'agrees' if x['agrees_D'] else 'disagrees'}); "
                  f"V predicted {np.exp(x['V_pred']):.2f} (sign {'agrees' if x['agrees_V'] else 'disagrees'}).")
    if e26:
        rl.append(f"- **E-V (runoff):** onset at {e26['onset_h']:.1f} active h. The winner's declared share reached ≥ 0.5 "
                  f"(≥ 3 declared) after τ_V = {e26['tau_V_h'] if e26['tau_V_h'] is not None else float('nan'):.2f} h. "
                  f"The M_λ forecast was {e26['M_l2_pred_h']:.2f} h (80%: {e26['M_l2_80pct_h'][0]:.2f}–{e26['M_l2_80pct_h'][1]:.2f}). "
                  f"Before the runoff, the top candidate's declared share was {e26['pre_runoff_max_share']:.2f} "
                  f"(n = {e26['pre_runoff_n']}).")
        if e26.get("rise_posthoc_h") is not None:
            rl.append(f"- **E-V post hoc:** the pre-registered onset (first runoff-word message) fired at the period start, as H11's "
                      f"onset rule did. The winner's share rose from {e26['share_before_posthoc']:.2f} to ≥ 0.5 within "
                      f"{e26['rise_posthoc_h']:.2f} h (last window below 0.25 → first ≥ 0.5): an abrupt decision step.")
        if e26["tau_V_h"] is not None:
            lo, hi = e26["M_l2_80pct_h"]
            verdict_bits.append("supported" if lo <= e26["tau_V_h"] <= hi else "failed")
    if pe.height and pu.height == 0 and pe["consensus"].sum() > 0:
        fz = pe.filter(pl.col("consensus") & pl.col("frozen"))
        ni = fz.filter(pl.col("t0_h") > 0.75 + 1e-6).height
        rl.append(f"- No uncensored E-P event: {fz.height - ni} frozen at the period start (kick-locked by construction) and "
                  f"{ni} *instant* (criterion met in the onset window mid-period: a one-window herding wave). "
                  "By the card's rule both are left-censored, so there is no τ to test.")
    if pc.height and pc["kind"][0] == "divergence":
        c0 = pc.row(0, named=True)
        rl.append(f"- **E-C divergence:** content alignment starts high after the kickoff (A₀ = {c0['A0']:.2f}) and relaxes to "
                  f"A∞ = {c0['Ainf']:.2f} with τ = {c0['tau']:.1f} h. The field imposes the alignment and the dynamics "
                  "dissolve it, the opposite of consensus formation.")
    vb = [v for v in verdict_bits if v]
    if not vb:
        verdict = "descriptive" if (pe.height or (pc.height and pc["kind"][0] != "n/a")) else "n/a"
    elif all(v == "supported" for v in vb):
        verdict = "supported"
    elif all(v == "failed" for v in vb):
        verdict = "failed"
    else:
        verdict = "mixed"
    rl.append("")
    rl.append("Data: `data/processed/H31-consensus-time-spectral-gap/G%02d/`, `events_ep_w30.parquet`, `events_ec.parquet`." % g)
    sc.append("- **C (period level):** the per-event leave-one-period-out comparison of M_λ (or M_tr) vs the constant is listed above.")
    sc.append("- **G:** " + ("the #26 runoff winner matches the dataset's summary (DeepSeek-V3.2)." if e26 else "no external ground truth for consensus timing in this period."))
    out = {"goal_no": g, "verdict": verdict, "result_lines": rl, "scorecard_lines": sc}
    (L.DATA / f"G{g:02d}" / "results.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
