"""H14 per-period pipeline (one goal period at a time; non-holdout unless called by the confirmatory script).

For each agent (>= 2 days, >= 300 transitions): single-agent EP of its coarse turn sequence (cfx primary after the
synthetic amendment, Newton, plug-in, chi2, TUR, order-2), detailed-balance (DB) surrogate tests, the fine `act`
scheme, the no-consolidate chain, the minute grid, held-out Markov-order likelihoods and lump4 cycle affinities.
Per period: family tests (lab), and the collective term on the minute grid vs. cross-day surrogates.

Usage:
  uv run python hypotheses/H14-behavior-entropy-production/analysis/run_period.py --period G38 [--fast]
  uv run python .../run_period.py --period G38 --states my_states.parquet --state-col state [--time-col t |
      --day-col pt_date --bin-col w]      (any categorical state table: single-agent and family parts only)
Writes data/processed/H14-behavior-entropy-production/<period>/{agents.parquet,results.json} and
hypotheses/H14-behavior-entropy-production/goalperiod-subhypotheses/<period>/figures/period_summary.pdf.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h14lib as L  # noqa: E402  (sets thread env vars first)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H14-behavior-entropy-production"
HYP = HERE.parent

COARSE = ["browse", "type", "shell", "chat", "idle", "consolidate"]
ACT = ["shell", "click", "scroll", "look", "type", "chat", "idle", "consolidate", "search", "session", "other"]
LUMP4 = ["work", "chat", "idle", "consolidate"]
LUMP = np.array([0, 0, 0, 1, 2, 3])          # coarse -> lump4
WORK, CHAT, CONS = [0, 1, 2], 3, 5
# oriented lump4 cycles (work=0, chat=1, idle=2, consolidate=3); P5 names
CYCLES = {"work>chat>idle": (0, 1, 2), "work>chat>cons": (0, 1, 3), "work>idle>cons": (0, 2, 3), "chat>idle>cons": (1, 2, 3)}
PERIODS = {
    "G27": dict(goals=[27]), "G37": dict(goals=[37]), "G38": dict(goals=[38], split="2026-04-14"),
    "G39": dict(goals=[39]), "G40": dict(goals=[40]), "G41": dict(goals=[41]), "G42": dict(goals=[42]),
    "G44": dict(goals=[44]), "G51": dict(goals=[51], block=("2026-07-24", "2026-08-28"), weekly=True),
}
MIN_TRANS, MIN_DAYS, TEST_TRANS = 300, 2, 1000
TRIM = 5


# ============================================================================ helpers
def period_days(spec, allow_holdout=False):
    cal = pl.read_parquet(SH / "calendar.parquet")
    c = cal.filter(pl.col("goal_no").is_in(spec["goals"]))
    hm = np.array(holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list()))
    if not allow_holdout:
        c = c.filter(pl.Series(~hm))
        assert not any(holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())), "holdout day in exploration"
    else:
        c = c.filter(pl.Series(hm))
    return c.sort("pt_date")


def pval(null, obs):
    null = np.asarray(null)
    null = null[np.isfinite(null)]
    if not np.isfinite(obs) or len(null) == 0:
        return np.nan
    return float((1 + (null >= obs).sum()) / (len(null) + 1))


def rare_merge_map(act_counts: dict, n_total: int, other=ACT.index("other")):
    """Fine classes with < 1% of the period's records are merged into `other`."""
    m = np.arange(len(ACT))
    for k, v in act_counts.items():
        if v < 0.01 * n_total:
            m[k] = other
    # recode to consecutive codes
    used = sorted(set(m.tolist()))
    rec = {u: i for i, u in enumerate(used)}
    return np.array([rec[x] for x in m]), [ACT[u] for u in used]


def day_codes(pt_dates):
    u, inv = np.unique(np.asarray(pt_dates), return_inverse=True)
    return inv, u


# ============================================================================ single agent
def single_agent(seqs, R, rng, q_act, fast=False):
    """seqs: dict with 'coarse' (seq, day), 'act' (seq, day), 'min' (seq, day) or None. Returns flat dict."""
    out = {}
    x, d = seqs["coarse"]
    p, n_, dd = L.transitions(x, d)
    out["n_trans"] = int(len(p))
    out["n_days"] = int(len(np.unique(dd)))
    out["plugin"] = L.ep_plugin(p, n_, 6)
    out["chi2"] = L.ep_chi2(p, n_, 6)
    out["newton"] = L.ep_newton(p, n_, dd, 6)
    out["cfx"] = L.ep_cfx(p, n_, dd, 6)
    out["tur"] = L.ep_tur(out["newton"])
    out["cfx3"] = L.ep_cfx3(x, d, 6)
    ll = L.heldout_loglik(x, d, 6)
    out.update({f"ll{o}": v for o, v in ll.items()})
    C = L.counts(p, n_, 6)
    dec = L.ep_decomposition(C)
    tot = dec[np.triu_indices(6, 1)].sum()
    out["plugin_share_consolidate"] = float(dec[CONS].sum() / tot) if tot > 0 else np.nan
    for k, c in enumerate(COARSE):
        out[f"occ_{c}"] = float(np.mean(x == k))
    # DB null (coarse) with lumped counts for the affinity nulls
    nl = L.db_null(x, d, 6, R, rng, stats=("newton", "cfx", "plugin"), lump=LUMP)
    for k in ("newton", "cfx", "plugin"):
        out[f"{k}_null_mean"] = float(np.nanmean(nl[k]))
        out[f"{k}_null_p95"] = float(np.nanpercentile(nl[k], 95))
        out[f"{k}_p"] = pval(nl[k], out[k])
        out[f"{k}_exc"] = out[k] - out[f"{k}_null_mean"]
    # lump4 currents
    C4 = L.counts(LUMP[p], LUMP[n_], 4)
    F = L.flux(C4)
    for a in range(4):
        for b in range(4):
            if a != b:
                out[f"flux_{LUMP4[a]}>{LUMP4[b]}"] = float(F[a, b])
    for nm, (a, b, c) in CYCLES.items():
        A = L.cycle_affinity(C4, a, b, c)
        An = np.array([L.cycle_affinity(Cn, a, b, c) for Cn in nl["counts_lumped"]])
        out[f"aff_{nm}"] = A
        out[f"aff_{nm}_null_sd"] = float(np.std(An))
        out[f"aff_{nm}_p_pos"] = pval(An, A)            # orientation as named
        out[f"aff_{nm}_p_neg"] = pval(-An, -A)          # reverse orientation
        out[f"cur_{nm}"] = L.cycle_current(C4, a, b, c)
    # act scheme
    xa, da = seqs["act"]
    pa, na, dda = L.transitions(xa, da)
    out["act_cfx"] = L.ep_cfx(pa, na, dda, q_act)
    out["act_newton"] = L.ep_newton(pa, na, dda, q_act)
    nla = L.db_null(xa, da, q_act, max(R // 2, 20), rng, stats=("cfx", "newton"))
    for k in ("cfx", "newton"):
        out[f"act_{k}_null_mean"] = float(np.nanmean(nla[k]))
        out[f"act_{k}_p"] = pval(nla[k], out[f"act_{k}"])
        out[f"act_{k}_exc"] = out[f"act_{k}"] - out[f"act_{k}_null_mean"]
    # no-consolidate (decimated) chain
    keep = x != CONS
    xn, dn = x[keep], d[keep]
    pn, nn, ddn = L.transitions(xn, dn)
    remap = np.array([0, 1, 2, 3, 4, -1])
    if len(pn) > 50 and len(np.unique(ddn)) >= 2:
        out["nocons_cfx"] = L.ep_cfx(remap[pn], remap[nn], ddn, 5)
        out["nocons_newton"] = L.ep_newton(remap[pn], remap[nn], ddn, 5)
        nln = L.db_null(remap[xn], dn, 5, max(R // 2, 20), rng, stats=("cfx", "newton"))
        for k in ("cfx", "newton"):
            out[f"nocons_{k}_null_mean"] = float(np.nanmean(nln[k]))
            out[f"nocons_{k}_p"] = pval(nln[k], out[f"nocons_{k}"])
            out[f"nocons_{k}_exc"] = out[f"nocons_{k}"] - out[f"nocons_{k}_null_mean"]
        out["nocons_n_trans"] = int(len(pn))
    # minute grid
    if seqs.get("min") is not None:
        xm, dm = seqs["min"]
        pm, nm_, ddm = L.transitions(xm, dm)
        if len(pm) > 100 and len(np.unique(ddm)) >= 2:
            out["min_n_trans"] = int(len(pm))
            out["min_cfx"] = L.ep_cfx(pm, nm_, ddm, 6)
            out["min_newton"] = L.ep_newton(pm, nm_, ddm, 6)
            nlm = L.db_null(xm, dm, 6, max(R // 2, 20), rng, stats=("cfx", "newton"))
            for k in ("cfx", "newton"):
                out[f"min_{k}_null_mean"] = float(np.nanmean(nlm[k]))
                out[f"min_{k}_p"] = pval(nlm[k], out[f"min_{k}"])
                out[f"min_{k}_exc"] = out[f"min_{k}"] - out[f"min_{k}_null_mean"]
    return out


def build_agent_seqs(st, sm, agent, days, act_map):
    """Turn (coarse, act) and minute sequences for one agent in the given days."""
    a = st.filter(pl.col("agent") == agent).sort("t")
    dcode = {dd: i for i, dd in enumerate(days)}
    dl = np.array([dcode[x] for x in a["pt_date"].to_list()])
    co = a["coarse"].to_numpy()
    ac = act_map[a["act"].to_numpy()]
    keep = co >= 0
    seqs = {"coarse": (co[keep].astype(np.int8), dl[keep]), "act": (ac.astype(np.int8), dl)}
    if sm is not None:
        m = (sm.filter((pl.col("agent") == agent) & pl.col("present"))
             .sort("pt_date", "minute"))
        if m.height:
            mx = m.group_by("pt_date").agg(pl.col("minute").max().alias("mx"))
            m = m.join(mx, on="pt_date").filter((pl.col("minute") >= TRIM) & (pl.col("minute") <= pl.col("mx") - TRIM))
            seqs["min"] = (m["coarse_min"].to_numpy().astype(np.int8), np.array([dcode[x] for x in m["pt_date"].to_list()]))
    return seqs


# ============================================================================ family
def family_tests(df, col, rng, nperm=10000):
    d = df.filter(pl.col(col).is_not_nan() & pl.col("eligible") & ~pl.col("lab").str.starts_with("Fine"))
    v, lab = d[col].to_numpy(), np.array(d["lab"].to_list())
    out = {"n_agents": int(len(v)), "labs": {k: int((lab == k).sum()) for k in np.unique(lab)}}
    if len(v) < 4 or len(np.unique(lab)) < 2:
        return out
    e, p, nm = L.perm_eta2(v, lab, nperm, rng)
    out.update({"eta2": e, "eta2_p": p, "eta2_null_mean": nm})
    diff, p2, p1 = L.perm_diff(v, lab, "Anthropic", "OpenAI", nperm, rng)
    out.update({"anth_minus_openai": diff, "p_two": p2, "p_anth_gt_openai": p1})
    out["lab_means"] = {k: float(v[lab == k].mean()) for k in np.unique(lab)}
    # adjusted for shell share and log n (rival R2)
    X = np.column_stack([np.ones(len(v)), d["occ_shell"].to_numpy(), np.log(d["n_trans"].to_numpy())])
    beta, *_ = np.linalg.lstsq(X, v, rcond=None)
    res = v - X @ beta
    e2, p2a, _ = L.perm_eta2(res, lab, nperm, rng)
    out.update({"eta2_adj": e2, "eta2_adj_p": p2a})
    return out


# ============================================================================ collective
def aligned_grid(sm, days, agents_req=None, min_frac=0.8):
    """(n_days, L+1, N) minute arrays for agents present on >= min_frac of days, restricted to days where all of them
    are present; minutes TRIM .. Lmin - TRIM aligned by minute of window."""
    s = sm.filter(pl.col("pt_date").is_in(days))
    pres = s.filter(pl.col("present")).group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"))
    agents = sorted(pres.filter(pl.col("nd") >= min_frac * len(days))["agent"].to_list())
    if agents_req is not None:
        agents = [a for a in agents if a in agents_req]
    ok_days = []
    for dd in days:
        pa = set(s.filter((pl.col("pt_date") == dd) & pl.col("present"))["agent"].to_list())
        if all(a in pa for a in agents):
            ok_days.append(dd)
    s = s.filter(pl.col("pt_date").is_in(ok_days) & pl.col("agent").is_in(agents))
    Lmin = int(s.group_by("pt_date").agg(pl.col("minute").max())["minute"].min())
    lo, hi = TRIM, Lmin - TRIM
    X = np.zeros((len(ok_days), hi - lo + 1, len(agents)), dtype=np.int8)
    ai = {a: i for i, a in enumerate(agents)}
    for k, dd in enumerate(ok_days):
        g = s.filter((pl.col("pt_date") == dd) & (pl.col("minute") >= lo) & (pl.col("minute") <= hi))
        X[k, g["minute"].to_numpy() - lo, [ai[a] for a in g["agent"].to_list()]] = g["coarse_min"].to_numpy()
    return X, agents, ok_days


def collective(X, R, rng, circ=5):
    Xp, Xn, d = L.stack_aligned(X)
    obs = L.collective_ep(Xp, Xn, d, 6, WORK, CHAT)
    obs["sigma1_cfx_sum"] = float(np.nansum([L.ep_cfx(Xp[:, i], Xn[:, i], d, 6) for i in range(X.shape[2])]))
    null = {k: [] for k in ("sigma1", "delta_mf", "delta_pw", "sigma_mf_alone", "sigma_pw_alone")}
    for _ in range(R):
        ns = L.collective_ep(*L.stack_aligned(L.crossday_surrogate(X, rng)), 6, WORK, CHAT)
        for k in null:
            null[k].append(ns[k])
    out = {"n_days": int(X.shape[0]), "L": int(X.shape[1]), "N": int(X.shape[2]), "T": int(len(Xp)), **obs}
    for k, v in null.items():
        v = np.array(v)
        out[f"{k}_null_mean"] = float(v.mean())
        out[f"{k}_null_sd"] = float(v.std())
        out[f"{k}_null_p95"] = float(np.percentile(v, 95))
        out[f"{k}_p"] = pval(v, obs[k])
        out[f"{k}_exc"] = float(obs[k] - v.mean())
        out[f"{k}_null"] = v.tolist()
    if circ:
        cs = [L.collective_ep(*L.stack_aligned(L.circshift_surrogate(X, rng)), 6, WORK, CHAT) for _ in range(circ)]
        out["circshift_delta_mf_mean"] = float(np.mean([c["delta_mf"] for c in cs]))
        out["circshift_sigma1_mean"] = float(np.mean([c["sigma1"] for c in cs]))
    out["ratio_delta_mf_exc_to_sigma1_cfx"] = out["delta_mf_exc"] / out["sigma1_cfx_sum"] if out["sigma1_cfx_sum"] > 0 else np.nan
    out["ratio_delta_pw_exc_to_sigma1_cfx"] = out["delta_pw_exc"] / out["sigma1_cfx_sum"] if out["sigma1_cfx_sum"] > 0 else np.nan
    return out


# ============================================================================ main per period
def run(period, st, sm, cal_days, fast=False, out_dir=None, fig_dir=None, label="exploratory", R_override=None):
    spec = PERIODS.get(period, {})
    rng = np.random.default_rng(20261003 + int("".join(ch for ch in period if ch.isdigit()) or 0))
    t0 = time.time()
    days = cal_days["pt_date"].to_list()
    win_h = dict(zip(cal_days["pt_date"].to_list(), (cal_days["window_s"] / 3600).to_list()))
    st = st.filter(pl.col("pt_date").is_in(days))
    sm = sm.filter(pl.col("pt_date").is_in(days)) if sm is not None else None
    roster = pl.read_parquet(SH / "roster.parquet").select(pl.col("agent").cast(pl.Int8), "name", "lab", "claude_code")
    ac = dict(st.group_by("act").len().iter_rows())
    act_map, act_names = rare_merge_map(ac, st.height)
    R = R_override or (60 if fast else 200)
    rows = []
    for agent in sorted(st["agent"].unique().to_list()):
        info = roster.filter(pl.col("agent") == agent)
        if info.height == 0 or info["claude_code"][0]:
            continue
        seqs = build_agent_seqs(st, sm, agent, days, act_map)
        x, d = seqs["coarse"]
        ndays = len(np.unique(d))
        ntr = len(L.transitions(x, d)[0])
        row = {"agent": int(agent), "name": info["name"][0], "lab": info["lab"][0], "n_days": ndays, "n_trans": ntr}
        if ndays < MIN_DAYS or ntr < MIN_TRANS:
            row["eligible"] = False
            rows.append(row)
            continue
        row["eligible"] = True
        row["test_eligible"] = ntr >= TEST_TRANS
        agent_days = sorted(set(np.array(days)[np.unique(d)]))
        hours = float(sum(win_h[dd] for dd in agent_days))
        row["hours"] = hours
        row.update(single_agent(seqs, R, rng, len(act_names), fast))
        row["trans_per_hour"] = row["n_trans"] / hours
        for k in ("cfx", "cfx_exc", "newton", "newton_exc", "plugin"):
            row[f"{k}_per_hour"] = row[k] * row["trans_per_hour"]
        if "min_cfx" in row:
            row["min_cfx_exc_per_hour"] = row["min_cfx_exc"] * 60
            row["min_newton_exc_per_hour"] = row["min_newton_exc"] * 60
        if spec.get("split"):
            sp = spec["split"]
            for half, sel in (("a", lambda z: z < sp), ("b", lambda z: z >= sp)):
                hd = [i for i, dd in enumerate(days) if sel(dd)]
                m = np.isin(d, hd)
                if len(np.unique(d[m])) >= 2 and m.sum() > 300:
                    ph, nh, dh = L.transitions(x[m], d[m])
                    nlh = L.db_null(x[m], d[m], 6, 50, rng, stats=("cfx", "newton"))
                    row[f"newton_exc_{half}"] = L.ep_newton(ph, nh, dh, 6) - float(np.nanmean(nlh["newton"]))
                    row[f"cfx_exc_{half}"] = L.ep_cfx(ph, nh, dh, 6) - float(np.nanmean(nlh["cfx"]))
        rows.append(row)
        print(f"  {period} agent {agent:>2} {row['name'][:22]:<22} n={ntr:>6} newton={row['newton']:.4f} (p={row['newton_p']:.3f}) "
              f"cfx_exc={row['cfx_exc']:.4f} (p={row['cfx_p']:.3f})", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    res = {"period": period, "role": label, "days": days, "n_days": len(days), "act_classes": act_names, "R_db": R}
    el = df.filter(pl.col("eligible"))
    te = el.filter(pl.col("test_eligible"))
    res["n_agents_eligible"] = el.height
    res["n_agents_test"] = te.height

    def frac(col, thr=0.05, sub=te):
        v = sub[col].drop_nans().drop_nulls().to_numpy() if col in sub.columns else np.array([])
        return (float(np.mean(v < thr)) if len(v) else np.nan, int(len(v)))

    # primary estimator: Newton (H05), per the pre-registered decision rule (its trigger was not met in P1)
    res["P2_frac_above_null_newton"], res["P2_n"] = frac("newton_p")
    res["P2_frac_above_null_cfx"], _ = frac("cfx_p")
    res["P2_frac_above_null_min"], res["P2_n_min"] = frac("min_newton_p")
    res["P2_frac_above_null_min_cfx"], _ = frac("min_cfx_p")
    res["act_frac_above_null"], _ = frac("act_newton_p")
    res["act_frac_above_null_cfx"], _ = frac("act_cfx_p")
    for col in ("newton", "newton_exc", "newton_exc_per_hour", "cfx", "cfx_exc", "plugin", "cfx_per_hour", "cfx_exc_per_hour",
                "min_newton", "min_newton_exc", "min_newton_exc_per_hour", "min_cfx", "min_cfx_exc", "min_cfx_exc_per_hour",
                "act_newton_exc", "act_cfx_exc", "nocons_newton_exc", "nocons_cfx_exc", "cfx3", "trans_per_hour"):
        if col in el.columns:
            v = el[col].drop_nans().drop_nulls().to_numpy()
            res[f"median_{col}"] = float(np.median(v)) if len(v) else np.nan
    for est in ("newton", "cfx"):
        if f"min_{est}_exc_per_hour" in el.columns:
            b = el.filter(pl.col(f"min_{est}_exc_per_hour").is_not_nan() & pl.col(f"{est}_exc_per_hour").is_not_nan())
            res[f"P2_frac_min_per_hour_below_turn_{est}"] = float(np.mean(b[f"min_{est}_exc_per_hour"].to_numpy() < b[f"{est}_exc_per_hour"].to_numpy())) if b.height else np.nan
    res["P2_frac_min_per_hour_below_turn"] = res.get("P2_frac_min_per_hour_below_turn_newton", np.nan)
    # Markov order (P8)
    o = el.filter(pl.col("ll2").is_not_nan())
    res["P8_frac_order2_beats_order1"] = float(np.mean(o["ll2"].to_numpy() > o["ll1"].to_numpy())) if o.height else np.nan
    res["P8_frac_order1_beats_order0"] = float(np.mean(o["ll1"].to_numpy() > o["ll0"].to_numpy())) if o.height else np.nan
    o3 = el.filter(pl.col("cfx3").is_not_nan())
    res["P8_frac_cfx3_gt_cfx"] = float(np.mean(o3["cfx3"].to_numpy() > o3["cfx"].to_numpy())) if o3.height else np.nan
    # P9: consolidate removal
    for est, suf in (("newton", ""), ("cfx", "_cfx")):
        col = f"nocons_{est}_exc"
        nc = el.filter(pl.col(col).is_not_nan() & (pl.col(f"{est}_exc") > 0)) if col in el.columns else el.clear()
        if nc.height:
            loss = 1 - nc[col].to_numpy() / nc[f"{est}_exc"].to_numpy()
            res[f"P9_median_share_lost{suf}"] = float(np.median(loss))
            res[f"P9_frac_nocons_above_null{suf}"] = float(np.mean(nc[f"nocons_{est}_p"].to_numpy() < 0.05))
    res["median_plugin_share_consolidate"] = float(np.nanmedian(el["plugin_share_consolidate"].to_numpy())) if el.height else np.nan
    # P5 currents
    cyc = {}
    for nm in CYCLES:
        a = el[f"aff_{nm}"].to_numpy()
        cyc[nm] = {"frac_pos": float(np.mean(a > 0)), "median_aff": float(np.median(a)),
                   "frac_sig_pos": float(np.mean(el[f"aff_{nm}_p_pos"].to_numpy() < 0.05)),
                   "frac_sig_neg": float(np.mean(el[f"aff_{nm}_p_neg"].to_numpy() < 0.05)),
                   "median_current": float(np.median(el[f"cur_{nm}"].to_numpy())),
                   "median_aff_x_cur": float(np.median(np.abs(a * el[f"cur_{nm}"].to_numpy())))}
        k = int((a > 0).sum())
        from scipy.stats import binomtest
        cyc[nm]["sign_test_p"] = float(binomtest(k, len(a), 0.5).pvalue) if len(a) else np.nan
    res["P5_cycles"] = cyc
    res["P5_dominant_cycle"] = max(cyc, key=lambda k: cyc[k]["median_aff_x_cur"]) if cyc else None
    agg = {f: float(el[f].sum()) for f in el.columns if f.startswith("flux_")}
    res["flux_sum_over_agents"] = agg
    # family
    for col in ("newton_exc", "cfx_exc", "newton_exc_per_hour", "cfx_exc_per_hour", "min_newton_exc", "min_cfx_exc",
                "nocons_newton_exc", "nocons_cfx_exc"):
        if col in df.columns:
            res[f"family_{col}"] = family_tests(df, col, rng)
    if spec.get("split") and "newton_exc_a" in df.columns:
        b = el.filter(pl.col("newton_exc_a").is_not_null() & pl.col("newton_exc_b").is_not_null())
        if b.height >= 3:
            from scipy.stats import wilcoxon
            dlt = b["newton_exc_b"].to_numpy() - b["newton_exc_a"].to_numpy()
            res["split"] = {"date": spec["split"], "n": b.height, "median_b_minus_a": float(np.median(dlt)),
                            "wilcoxon_p": float(wilcoxon(dlt).pvalue)}
    # collective
    if sm is not None:
        cdays = days
        if spec.get("block"):
            lo, hi = spec["block"]
            cdays = [x for x in days if lo <= x < hi]
        X, agents, ok_days = aligned_grid(sm, cdays)
        roster_cc = set(roster.filter(pl.col("claude_code"))["agent"].to_list())
        if any(a in roster_cc for a in agents):
            keep = [i for i, a in enumerate(agents) if a not in roster_cc]
            X, agents = X[:, :, keep], [agents[i] for i in keep]
        if X.shape[0] >= 3 and X.shape[2] >= 4:
            Rc = R_override or (30 if fast else (40 if X.shape[2] > 20 else 100))
            res["collective"] = collective(X, Rc, rng)
            res["collective"]["agents"] = [int(a) for a in agents]
            res["collective"]["days"] = ok_days
            print(f"  {period} collective N={X.shape[2]} days={X.shape[0]} dMF={res['collective']['delta_mf']:.4f} "
                  f"(null {res['collective']['delta_mf_null_mean']:.4f}, p={res['collective']['delta_mf_p']:.3f}) "
                  f"dPW={res['collective']['delta_pw']:.4f} (null {res['collective']['delta_pw_null_mean']:.4f}, "
                  f"p={res['collective']['delta_pw_p']:.3f})", flush=True)
        else:
            res["collective"] = {"skipped": f"{X.shape[0]} days x {X.shape[2]} agents after completeness filter"}
        if spec.get("weekly") and spec.get("block"):
            wk = {}
            for x_ in ok_days:
                y, w, _ = dt.date.fromisoformat(x_).isocalendar()
                wk.setdefault(f"{y}-W{w:02d}", []).append(x_)
            res["collective_weekly"] = {}
            for k, v in wk.items():
                if len(v) >= 3:
                    Xw, ag_w, okw = aligned_grid(sm, v, agents_req=set(agents))
                    if Xw.shape[0] >= 3:
                        cw = collective(Xw, 20 if not fast else 10, rng, circ=0)
                        res["collective_weekly"][k] = {kk: cw[kk] for kk in cw if not kk.endswith("_null")}
    res["runtime_s"] = time.time() - t0
    out_dir = out_dir or (DATA / period)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out_dir / "agents.parquet", compression="zstd")
    (out_dir / "results.json").write_text(json.dumps(res, indent=1, default=float))
    fig_dir = fig_dir or (HYP / "goalperiod-subhypotheses" / period / "figures")
    try:
        period_figure(period, df, res, fig_dir)
    except Exception as e:  # figures must not kill a run
        print("figure failed:", e)
    return df, res


# ============================================================================ figure
LAB_COL = {"Anthropic": "#c2662d", "OpenAI": "#3f6fb5", "Google": "#2a8a4a", "DeepSeek": "#8a5ab5", "Moonshot": "#b5a02a",
           "xAI": "#555555", "Zhipu": "#b52a6e", "Meta": "#2ab5b0"}


def period_figure(period, df, res, fig_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42})
    fig_dir.mkdir(parents=True, exist_ok=True)
    el = df.filter(pl.col("eligible")).sort("newton_exc")
    fig, axs = plt.subplots(2, 2, figsize=(7.0, 5.0))
    ax = axs[0, 0]
    y = np.arange(el.height)
    cols = [LAB_COL.get(l, "#999999") for l in el["lab"].to_list()]
    ax.barh(y, el["newton_exc"].to_numpy(), color=cols)
    ax.scatter(el["cfx_exc"].to_numpy(), y, s=5, color="k", marker="|", zorder=3, label="cfx − null")
    ax.errorbar(np.zeros(el.height), y, xerr=(el["newton_null_p95"] - el["newton_null_mean"]).to_numpy(), fmt="none", ecolor="k", lw=0.6)
    ax.set_yticks(y); ax.set_yticklabels([n[:18] for n in el["name"].to_list()], fontsize=5)
    ax.set_xlabel("Σ_i excess over DB surrogate (Newton bars; cfx ticks; nats/transition)")
    ax.set_title(f"{period}: single-agent arrow (whisker = null 95th pct)", fontsize=7)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for l, c in LAB_COL.items() if l in el["lab"].to_list()]
    ax.legend(handles, [l for l in LAB_COL if l in el["lab"].to_list()], frameon=False, fontsize=5, loc="lower right")
    # lump4 flux diagram
    ax = axs[0, 1]
    pos = {"work": (0, 1), "chat": (1, 1), "idle": (1, 0), "consolidate": (0, 0)}
    fl = res["flux_sum_over_agents"]
    n_ag = max(el.height, 1)
    mx = max([abs(v) for v in fl.values()] + [1e-9])
    for nm, (x0, y0) in pos.items():
        ax.scatter([x0], [y0], s=300, color="#dddddd", zorder=2)
        ax.text(x0, y0, nm, ha="center", va="center", fontsize=6, zorder=3)
    for k, v in fl.items():
        a, b = k[5:].split(">")
        if v <= 0:
            continue
        (x0, y0), (x1, y1) = pos[a], pos[b]
        off = 0.06
        dx, dy = x1 - x0, y1 - y0
        nx, ny = -dy * off, dx * off
        ax.annotate("", xy=(x1 * 0.8 + x0 * 0.2 + nx, y1 * 0.8 + y0 * 0.2 + ny), xytext=(x0 * 0.8 + x1 * 0.2 + nx, y0 * 0.8 + y1 * 0.2 + ny),
                    arrowprops=dict(arrowstyle="-|>", lw=0.5 + 4 * v / mx, color="#3f6fb5"))
        ax.text((x0 + x1) / 2 + 2.5 * nx, (y0 + y1) / 2 + 2.5 * ny, f"{v / n_ag:.3f}", fontsize=5, ha="center")
    ax.set_xlim(-0.4, 1.4); ax.set_ylim(-0.4, 1.4); ax.axis("off")
    ax.set_title("net flux per transition (lump4, mean over agents)", fontsize=7)
    # cycle affinities
    ax = axs[1, 0]
    for k, nm in enumerate(CYCLES):
        a = el[f"aff_{nm}"].to_numpy()
        ax.scatter(np.full(len(a), k) + np.random.default_rng(k).uniform(-0.15, 0.15, len(a)), a, s=6,
                   c=[LAB_COL.get(l, "#999") for l in el["lab"].to_list()])
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xticks(range(len(CYCLES))); ax.set_xticklabels(list(CYCLES), fontsize=6)
    ax.set_ylabel("cycle affinity (nats)"); ax.set_title("lump4 cycle affinities per agent (orientation as named)", fontsize=7)
    # collective
    ax = axs[1, 1]
    c = res.get("collective", {})
    if "delta_mf" in c:
        for k, colr in (("delta_mf", "#2a8a4a"), ("delta_pw", "#3f6fb5")):
            v = np.array(c[f"{k}_null"])
            ax.hist(v, bins=15, alpha=0.5, color=colr, label=f"{k} cross-day null")
            ax.axvline(c[k], color=colr, lw=1.2, label=f"{k} observed (p={c[f'{k}_p']:.2f})")
        ax.set_xlabel("ΔΣ (Newton, nats per minute, whole swarm)")
        ax.set_title(f"collective term: N={c['N']}, {c['n_days']} days", fontsize=7)
        ax.legend(frameon=False, fontsize=5)
    else:
        ax.text(0.5, 0.5, c.get("skipped", "no collective analysis"), ha="center", fontsize=6); ax.axis("off")
    fig.tight_layout()
    fig.savefig(fig_dir / "period_summary.pdf")
    plt.close(fig)


# ============================================================================ CLI
def main():
    period = sys.argv[sys.argv.index("--period") + 1]
    fast = "--fast" in sys.argv
    spec = PERIODS[period]
    cal_days = period_days(spec)
    if "--states" in sys.argv:
        path = sys.argv[sys.argv.index("--states") + 1]
        get = lambda k, dflt=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else dflt  # noqa: E731
        tab, names = L.load_state_table(path, state_col=get("--state-col", "state"), time_col=get("--time-col", "t"),
                                        day_col=get("--day-col"), bin_col=get("--bin-col"))
        run_generic(period, tab, names, cal_days)
        return
    st = pl.read_parquet(DATA / "states_turn.parquet")
    sm = pl.read_parquet(DATA / "states_min.parquet")
    df, res = run(period, st, sm, cal_days, fast=fast)
    print(json.dumps({k: v for k, v in res.items() if not isinstance(v, (dict, list))}, indent=1, default=float))


def run_generic(period, tab, names, cal_days, R=100):
    """Single-agent EP + DB null + family test for an arbitrary categorical state table (e.g. Jev labels)."""
    rng = np.random.default_rng(20261003)
    days = set(cal_days["pt_date"].to_list())
    tab = tab.filter(pl.col("pt_date").is_in(days))
    roster = pl.read_parquet(SH / "roster.parquet").select(pl.col("agent").cast(pl.Int16), "name", "lab")
    q = len(names)
    rows = []
    for agent in sorted(tab["agent"].unique().to_list()):
        a = tab.filter(pl.col("agent") == agent)
        dl, _ = day_codes(a["pt_date"].to_list())
        x, o = a["state"].to_numpy(), a["order"].to_numpy()
        if bool(a["grid"][0]):
            # contiguous runs of bins are the segments (gaps break transitions); segments are the folds
            brk = np.r_[True, (dl[1:] != dl[:-1]) | ((o[1:] - o[:-1]) != 1)]
            seg = np.cumsum(brk) - 1
        else:
            seg = dl
        p, n_, d = L.transitions(x, seg)
        row = {"agent": agent, "n_trans": int(len(p)), "n_days": int(len(np.unique(dl)))}
        if len(p) >= 100 and len(np.unique(d)) >= 2:
            row["cfx"] = L.ep_cfx(p, n_, d, q)
            row["newton"] = L.ep_newton(p, n_, d, q)
            nl = L.db_null(x, seg, q, R, rng, stats=("cfx",))
            row["cfx_p"] = pval(nl["cfx"], row["cfx"])
            row["cfx_exc"] = row["cfx"] - float(np.nanmean(nl["cfx"]))
        rows.append(row)
    df = pl.DataFrame(rows, infer_schema_length=None).join(roster, on="agent", how="left")
    print(df)
    print(f"{period}: {df.height} agents, states {names}; agents with >= 100 transitions: "
          f"{df.filter(pl.col('n_trans') >= 100).height}")


if __name__ == "__main__":
    main()
