"""H14 round 1b per-period pipeline (improved data). Non-holdout only. Design and predictions: card, "Round 1b".

Variants per agent:
  coarse      round-1 coarse turn chain (decimated over `other`), recomputed as a check
  coarse_b3   agent-only coarse chain (browse/type/shell/chat/idle; no infra-error turns), cut at scaffold records and
              scaffold-set call starts, first 3 transitions after every cut dropped (H56 Amendment 1)
  act_sh      fine classes with the shell split into vcs/net/run/read/write/wait/sh_other (all records, decimated)
  act_sh_b3   agent-only act_sh chain (shell sub-classes + click/scroll/look/type/chat/idle), cut + burn-in 3
  v3h         Jev v3.1 argmax (11 states + absent) on 5-min in-span windows
  v3s         soft v3 vectors (primary for v3; pooled period test), v3s_b1 with a 1-window burn-in after resets
Estimators: count-based cross-fitted Newton (primary), cfx (companion); nulls: DB surrogate (hard chains), block-flip
(all). Family tests per period on Newton excess.

Usage: uv run python hypotheses/H14-behavior-entropy-production/analysis/round1b.py --period G38 [--R 200]
       uv run python .../round1b.py --summarize
Writes data/processed/H14-behavior-entropy-production/r1b/<period>/{agents.parquet,results.json}, r1b/summary_r1b.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1b_lib as B  # noqa: E402  (sets thread env vars first)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = B.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H14-behavior-entropy-production"
OUT = DATA / "r1b"
# results folder: round 1b as run (legacy Newton) or the ep_gauss_crossfit recheck (H14_EP=heldout, 2026-10-04)
RES = OUT if B.EP == "xprod" else OUT / "recheck_epfix"
PERIODS = {"G27": [27], "G37": [37], "G38": [38], "G39": [39], "G40": [40], "G41": [41], "G42": [42], "G44": [44], "G51": [51]}
REGIME3 = ["G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
ACT = ["shell", "click", "scroll", "look", "type", "chat", "idle", "consolidate", "search", "session", "other"]
SHELL_SUB = ["vcs", "net", "run", "read", "write", "wait", "sh_other"]
ACT_SH = ACT[1:] + [f"sh_{s}" for s in SHELL_SUB]          # 10 non-shell classes + 7 shell sub-classes
JEV = ["plan_coordinate", "execute_task", "research_browse", "communicate_external", "debug_recover", "verify_report",
       "monitor_wait", "self_maintenance", "social", "meta", "idle"]
STATES12 = JEV + ["absent"]
MIN_TRANS, MIN_DAYS, TEST_TRANS, V3_TEST = 300, 2, 1000, 300
BURN = 3
TURN_BLOCK, WIN_BLOCK = 50, 12


# ============================================================================ chains
def act_sh_code(act, sh):
    """act_sh index: non-shell act k (1..10) -> k-1; shell with sub-class s -> 10 + s."""
    out = np.where(act == 0, 10 + np.maximum(sh, 6 * (sh < 0)), act - 1)
    return out.astype(np.int64)


def turn_chains(df, variant, code_map=None):
    """Transitions (a, b, day_index, seg_index) of one agent's records for a variant. df sorted by t."""
    act = df["act"].to_numpy().astype(np.int64)
    coarse = df["coarse"].to_numpy().astype(np.int64)
    sh = df["sh"].to_numpy().astype(np.int64)
    infra = df["infra"].to_numpy()
    sgap = df["sgap"].to_numpy()
    dayc = df["dayc"].to_numpy()
    if variant == "coarse":
        keep, x, cut = coarse >= 0, coarse, False
    elif variant == "coarse_b3":
        keep, x, cut = np.isin(coarse, [0, 1, 2, 3, 4]) & ~infra, coarse, True
    elif variant == "act_sh":
        keep, x, cut = np.ones(len(act), bool), code_map[act_sh_code(act, sh)], False
    elif variant == "act_sh_b3":
        keep, x, cut = np.isin(act, [0, 1, 2, 3, 4, 5, 6]) & ~infra, code_map[act_sh_code(act, sh)], True
    else:
        raise ValueError(variant)
    if not cut:
        idx = np.flatnonzero(keep)
        i0, i1 = idx[:-1], idx[1:]
        ok = dayc[i0] == dayc[i1]
    else:
        i0 = np.arange(len(act) - 1)
        i1 = i0 + 1
        ok = keep[i0] & keep[i1] & (dayc[i0] == dayc[i1]) & ~sgap[i1]
        ix = np.arange(len(ok))
        last_break = np.maximum.accumulate(np.where(~ok, ix, -1))
        ok = ok & ((ix - last_break - 1) >= BURN)
    i0, i1 = i0[ok], i1[ok]
    # segments: runs of consecutive valid transitions (a new segment where i0 != previous i1)
    newseg = np.ones(len(i0), bool)
    if len(i0) > 1:
        newseg[1:] = i0[1:] != i1[:-1]
    seg = np.cumsum(newseg) - 1
    return x[i0], x[i1], dayc[i1], seg


def hard_stats(a, b, d, seg, q, R, rng, do_db=True, do_flip=False, block_len=TURN_BLOCK):
    nday = int(d.max()) + 1 if len(d) else 0
    out = {"n_trans": int(len(a)), "n_days": int(len(np.unique(d)))}
    if len(a) < 10 or out["n_days"] < 2:
        return out
    C = B.day_counts(a, b, d, q, nday)
    out["newton"] = B.newton_counts(C)
    out["cfx"] = B.cfx_counts(C)
    if do_db:
        st = np.flatnonzero(np.r_[True, seg[1:] != seg[:-1]])
        lens = np.diff(np.r_[st, len(seg)])
        Cn = B.db_null_counts(a, b, d, a[st], lens, d[st], q, nday, R, rng)
        nn = np.array([B.newton_counts(c) for c in Cn])
        nc = np.array([B.cfx_counts(c) for c in Cn])
        out.update({"newton_null_mean": float(np.nanmean(nn)), "newton_p": B.pval(nn, out["newton"]),
                    "newton_exc": out["newton"] - float(np.nanmean(nn)),
                    "cfx_null_mean": float(np.nanmean(nc)), "cfx_p": B.pval(nc, out["cfx"]),
                    "cfx_exc": out["cfx"] - float(np.nanmean(nc))})
    if do_flip:
        blk = B.blocks_of(seg, block_len)
        Cb, bd = B.block_counts(a, b, d, blk, q)
        fl = B.flip_null_counts(Cb, bd, nday, R, rng)
        out.update({"flip_p": B.pval(fl, out["newton"]), "flip_null_mean": float(np.nanmean(fl))})
    return out


# ============================================================================ v3 windows
def load_v3(goals):
    v = pl.read_parquet(SH / "behavior_states_v3.parquet").filter(
        ~pl.col("holdout") & pl.col("in_span") & pl.col("goal_no").is_in(goals))
    assert not any(holdout_mask(v["pt_date"].to_list(), v["goal_no"].to_list()))
    v = v.sort("agent", "pt_date", "w")
    P = np.zeros((v.height, 12))
    lab = v["labeled"].to_numpy()
    for j, s in enumerate(JEV):
        P[:, j] = np.nan_to_num(v[f"p_{s}"].to_numpy().astype(np.float64)) * lab
    P[~lab, 11] = 1.0
    P = P / np.clip(P.sum(1, keepdims=True), 1e-12, None)
    mass = P.mean(0)
    keep = [j for j in range(12) if mass[j] >= 0.01]
    rest = [j for j in range(12) if mass[j] < 0.01]
    Pk = P[:, keep]
    names = [STATES12[j] for j in keep]
    if rest and P[:, rest].sum(1).mean() >= 0.01:
        Pk = np.column_stack([Pk, P[:, rest].sum(1)])
        names.append("rare")
    Pk = Pk / np.clip(Pk.sum(1, keepdims=True), 1e-12, None)
    return v, Pk, names


def v3_pairs(v, b1=False, mask=None, b1c=False):
    """Indices (i0, i1) of consecutive in-span windows of the same agent-day; b1 drops transitions into or out of a
    post-reset window (the first window after a context reset); mask (optional, per window) restricts both ends.

    b1 (pre-registered) keeps transitions INTO the window that contains the reset but drops those OUT of it, a
    time-asymmetric selection that manufactures irreversibility (found after running; see the card). b1c (amended)
    also drops every transition touching the reset window itself: a symmetric cut plus a 1-window burn-in after it."""
    ag = v["agent"].to_numpy()
    dy = v["pt_date"].to_numpy()
    w = v["w"].to_numpy()
    i0 = np.arange(v.height - 1)
    i1 = i0 + 1
    ok = (ag[i0] == ag[i1]) & (dy[i0] == dy[i1]) & (w[i1] - w[i0] == 1)
    if b1 or b1c:
        pr = v["post_reset"].fill_null(False).to_numpy()
        ok &= ~pr[i0] & ~pr[i1]
    if b1c:
        # reset_in[w] = the next consecutive window is flagged post_reset (the reset happened inside w)
        nxt = np.r_[(ag[1:] == ag[:-1]) & (dy[1:] == dy[:-1]) & (w[1:] - w[:-1] == 1), False]
        reset_in = nxt & np.r_[pr[1:], False]
        ok &= ~reset_in[i0] & ~reset_in[i1]
    if mask is not None:
        ok &= mask[i0] & mask[i1]
    return i0[ok], i1[ok]


def seg_of_pairs(i0, i1):
    newseg = np.ones(len(i0), bool)
    if len(i0) > 1:
        newseg[1:] = i0[1:] != i1[:-1]
    return np.cumsum(newseg) - 1


def soft_test(P, v, i0, i1, R, rng, day_codes):
    G = B.soft_G(P[i0], P[i1])
    d = day_codes[i1]
    obs = B.newton_G(G, d)
    out = {"n_trans": int(len(i0)), "newton": obs}
    if not np.isfinite(obs):
        return out
    seg = seg_of_pairs(i0, i1)
    blk = B.blocks_of(seg, WIN_BLOCK)
    fl = B.flip_null_G(G, d, blk, R, rng)
    out.update({"flip_p": B.pval(fl, obs), "flip_null_mean": float(np.nanmean(fl)),
                "flip_null_p95": float(np.nanpercentile(fl, 95)), "exc": obs - float(np.nanmean(fl))})
    return out


# ============================================================================ per period
def run(period, R=200, fast=False):
    t0 = time.time()
    goals = PERIODS[period]
    rng = np.random.default_rng(20261004 + goals[0])
    rec = pl.read_parquet(OUT / "records_r1b.parquet").filter(pl.col("goal_no").is_in(goals)).sort("agent", "t")
    assert not any(holdout_mask(rec["pt_date"].to_list(), rec["goal_no"].to_list()))
    days = sorted(rec["pt_date"].unique().to_list())
    dcode = {d: i for i, d in enumerate(days)}
    rec = rec.with_columns(pl.col("pt_date").replace_strict(dcode, return_dtype=pl.Int64).alias("dayc"))
    roster = pl.read_parquet(SH / "roster.parquet").select(pl.col("agent").cast(pl.Int8), "name", "lab", "claude_code")
    # act_sh rare merge (< 1% of the period's records -> other)
    xs = act_sh_code(rec["act"].to_numpy().astype(np.int64), rec["sh"].to_numpy().astype(np.int64))
    cnt = np.bincount(xs, minlength=len(ACT_SH))
    other = ACT_SH.index("other")
    m = np.array([other if (cnt[k] < 0.01 * len(xs)) else k for k in range(len(ACT_SH))])
    used = sorted(set(m.tolist()))
    remap = {u: i for i, u in enumerate(used)}
    code_map = np.array([remap[m[k]] for k in range(len(ACT_SH))])
    act_names = [ACT_SH[u] for u in used]
    Q = {"coarse": 6, "coarse_b3": 6, "act_sh": len(used), "act_sh_b3": len(used)}
    rows = []
    for agent in sorted(rec["agent"].unique().to_list()):
        info = roster.filter(pl.col("agent") == agent)
        if info.height == 0 or info["claude_code"][0]:
            continue
        g = rec.filter(pl.col("agent") == agent)
        row = {"agent": int(agent), "name": info["name"][0], "lab": info["lab"][0]}
        for var in ("coarse", "coarse_b3", "act_sh", "act_sh_b3"):
            a, b, d, seg = turn_chains(g, var, code_map)
            if len(a) < MIN_TRANS or len(np.unique(d)) < MIN_DAYS:
                row[f"{var}_n_trans"] = int(len(a))
                continue
            Rv = R if var in ("coarse", "act_sh") else max(R // 2, 50)
            hs = hard_stats(a, b, d, seg, Q[var], Rv, rng, do_db=True, do_flip=(var == "act_sh_b3"))
            row.update({f"{var}_{k}": v for k, v in hs.items()})
        rows.append(row)
        print(f"  {period} agent {agent:>2} " + " ".join(f"{v}={row.get(v + '_newton', np.nan):.4f}(p{row.get(v + '_newton_p', np.nan):.2f})"
                                                     for v in ("coarse", "coarse_b3", "act_sh", "act_sh_b3")), flush=True)
    # ---- v3 windows
    v, P, names = load_v3(goals)
    vdays = sorted(v["pt_date"].unique().to_list())
    vcode = {d_: i for i, d_ in enumerate(vdays)}
    day_codes = np.array([vcode[x] for x in v["pt_date"].to_list()])
    xh = P.argmax(1)
    q12 = P.shape[1]
    res_v3 = {"names": names, "n_windows": v.height}
    for tag, b1 in (("v3s", False), ("v3s_b1", True)):
        i0, i1 = v3_pairs(v, b1=b1)
        res_v3[f"pooled_{tag}"] = soft_test(P, v, i0, i1, R, rng, day_codes)
    i0, i1 = v3_pairs(v)
    seg = seg_of_pairs(i0, i1)
    res_v3["pooled_v3h"] = hard_stats(xh[i0], xh[i1], day_codes[i1], seg, q12, R, rng, do_db=True, do_flip=True, block_len=WIN_BLOCK)
    agv = v["agent"].to_numpy()
    out_rate = (v.group_by("agent").agg(((pl.col("n_commit_ok").sum() + pl.col("n_push_ok").sum()) / (pl.len() * 5 / 60)).alias("out_rate"),
                                        pl.col("p_blocked").mean().alias("p_blocked")))
    orate = {int(a): (o, pb) for a, o, pb in out_rate.iter_rows()}
    for row in rows:
        a = row["agent"]
        msk = agv[i0] == a
        if msk.sum() < V3_TEST or len(np.unique(day_codes[i1][msk])) < 2:
            row["v3_n_trans"] = int(msk.sum())
            continue
        ia, ib = i0[msk], i1[msk]
        st = soft_test(P, v, ia, ib, max(R // 2, 50) if not fast else 30, rng, day_codes)
        row.update({f"v3s_{k}": val for k, val in st.items()})
        sa = seg_of_pairs(ia, ib)
        hs = hard_stats(xh[ia], xh[ib], day_codes[ib], sa, q12, max(R // 2, 50), rng, do_db=True, do_flip=False)
        row.update({f"v3h_{k}": val for k, val in hs.items()})
        row["out_rate"], row["p_blocked"] = orate.get(a, (np.nan, np.nan))
    df = pl.DataFrame(rows, infer_schema_length=None)
    res = {"period": period, "days": days, "act_sh_classes": act_names, "v3": res_v3, "R": R}

    def col(c, sub=None):
        d_ = df if sub is None else sub
        return d_[c].drop_nulls().drop_nans().to_numpy() if c in d_.columns else np.array([])

    for var in ("coarse", "coarse_b3", "act_sh", "act_sh_b3", "v3h"):
        if f"{var}_newton_p" not in df.columns:
            continue
        thr = TEST_TRANS if var != "v3h" else V3_TEST
        te = df.filter(pl.col(f"{var}_n_trans") >= thr) if f"{var}_n_trans" in df.columns else df.clear()
        p = col(f"{var}_newton_p", te)
        res[f"{var}_frac_above_null"] = float(np.mean(p < 0.05)) if len(p) else None
        res[f"{var}_n_test"] = int(len(p))
        res[f"{var}_median_newton"] = float(np.median(col(f"{var}_newton"))) if len(col(f"{var}_newton")) else None
        res[f"{var}_median_exc"] = float(np.median(col(f"{var}_newton_exc"))) if len(col(f"{var}_newton_exc")) else None
        pc = col(f"{var}_cfx_p", te)
        res[f"{var}_frac_above_null_cfx"] = float(np.mean(pc < 0.05)) if len(pc) else None
    if "act_sh_b3_flip_p" in df.columns:
        te = df.filter(pl.col("act_sh_b3_n_trans") >= TEST_TRANS)
        p = col("act_sh_b3_flip_p", te)
        res["act_sh_b3_frac_above_flip"] = float(np.mean(p < 0.05)) if len(p) else None
    if "v3s_flip_p" in df.columns:
        p = col("v3s_flip_p")
        res["v3s_agent_frac_above_flip"] = float(np.mean(p < 0.05)) if len(p) else None
        res["v3s_agent_n"] = int(len(p))
        res["v3s_agent_median_newton"] = float(np.median(col("v3s_newton")))
    # P9-b3: share of the excess kept after scaffold removal with burn-in (median over agents with full excess > 0)
    for full, b3 in (("coarse", "coarse_b3"), ("act_sh", "act_sh_b3")):
        if f"{b3}_newton_exc" in df.columns and f"{full}_newton_exc" in df.columns:
            s = df.filter(pl.col(f"{full}_newton_exc").is_not_null() & pl.col(f"{b3}_newton_exc").is_not_null()
                          & (pl.col(f"{full}_newton_exc") > 0))
            if s.height:
                res[f"P9_{b3}_median_share_kept"] = float(np.median(s[f"{b3}_newton_exc"].to_numpy() / s[f"{full}_newton_exc"].to_numpy()))
                res[f"P9_{b3}_n"] = s.height
    pv = res_v3["pooled_v3s"].get("newton")
    pb = res_v3["pooled_v3s_b1"].get("newton")
    res["v3s_b1_share_kept"] = float(pb / pv) if (pv and pv > 0 and pb is not None) else None
    # family (lab) tests on Newton excess
    rng2 = np.random.default_rng(7 + goals[0])
    fam = {}
    for c in ("coarse_newton_exc", "coarse_b3_newton_exc", "act_sh_newton_exc", "act_sh_b3_newton_exc", "v3s_exc"):
        if c not in df.columns:
            continue
        d_ = df.filter(pl.col(c).is_not_null() & pl.col(c).is_not_nan() & ~pl.col("lab").str.starts_with("Fine"))
        if d_.height >= 4 and d_["lab"].n_unique() >= 2:
            vv, lb = d_[c].to_numpy(), np.array(d_["lab"].to_list())
            e = B.eta2(vv, lb)
            null = np.array([B.eta2(vv, rng2.permutation(lb)) for _ in range(5000)])
            fam[c] = {"eta2": e, "p": float((1 + (null >= e - 1e-12).sum()) / 5001), "n": d_.height,
                      "lab_means": {k: float(vv[lb == k].mean()) for k in np.unique(lb)}}
    res["family"] = fam
    # R1: useful irreversibility (descriptive)
    if "v3s_newton" in df.columns and "out_rate" in df.columns:
        d_ = df.filter(pl.col("v3s_newton").is_not_null() & pl.col("out_rate").is_not_null())
        if d_.height >= 5:
            r_, p_ = stats.spearmanr(d_["v3s_newton"].to_numpy(), d_["out_rate"].to_numpy())
            res["R1_rho_v3s_out"] = {"rho": float(r_), "p": float(p_), "n": d_.height}
    res["runtime_s"] = round(time.time() - t0, 1)
    od = RES / period
    od.mkdir(parents=True, exist_ok=True)
    df.write_parquet(od / "agents.parquet")
    (od / "results.json").write_text(json.dumps(jsonable(res), indent=1))
    print(json.dumps({k: res[k] for k in res if k.endswith("frac_above_null") or k.startswith("P9") or k == "runtime_s"}, default=str))
    print("pooled v3s", res_v3["pooled_v3s"], "\npooled v3h", {k: res_v3["pooled_v3h"].get(k) for k in ("newton", "newton_p", "flip_p")})
    return res


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


# ============================================================================ cross-period summary
def summarize():
    rng = np.random.default_rng(20261004)
    R = {p: json.loads((RES / p / "results.json").read_text()) for p in PERIODS if (RES / p / "results.json").exists()}
    A = {p: pl.read_parquet(RES / p / "agents.parquet") for p in R}
    r1 = {p: json.loads((DATA / p / "results.json").read_text()) for p in PERIODS if (DATA / p / "results.json").exists()}
    out = {"periods": {}}
    for p, r in R.items():
        o = {k: r.get(k) for k in r if k.endswith("frac_above_null") or k.endswith("_median_exc") or k.endswith("_median_newton")
             or k.startswith("P9") or k in ("v3s_b1_share_kept", "act_sh_b3_frac_above_flip", "v3s_agent_frac_above_flip",
                                            "v3s_agent_n", "R1_rho_v3s_out") or k.endswith("_n_test")}
        o["pooled_v3s"] = r["v3"]["pooled_v3s"]
        o["pooled_v3s_b1"] = r["v3"]["pooled_v3s_b1"]
        o["pooled_v3s_b1c"] = r["v3"].get("pooled_v3s_b1c")
        o["v3s_b1c_share_kept"] = r.get("v3s_b1c_share_kept")
        o["pooled_v3h"] = {k: r["v3"]["pooled_v3h"].get(k) for k in ("newton", "newton_p", "flip_p", "newton_exc", "n_trans")}
        o["round1"] = {k: r1[p].get(k) for k in ("P2_frac_above_null_newton", "act_frac_above_null", "median_newton_exc",
                                                  "median_act_newton_exc", "P9_median_share_lost")} if p in r1 else None
        out["periods"][p] = o
    # P2-fine and act_sh vs round-1 act excess
    out["P2_fine_periods_ge80"] = sum(1 for p in R if (R[p].get("act_sh_frac_above_null") or 0) >= 0.8)
    out["act_sh_exc_ge_round1_act"] = sum(1 for p in R if p in r1 and R[p].get("act_sh_median_exc") is not None
                                          and R[p]["act_sh_median_exc"] >= (r1[p].get("median_act_newton_exc") or np.inf))
    out["coarse_check_vs_round1"] = {p: [R[p].get("coarse_frac_above_null"), r1[p].get("P2_frac_above_null_newton"),
                                         R[p].get("coarse_median_exc"), r1[p].get("median_newton_exc")] for p in R if p in r1}
    out["P9_coarse_b3_lt50"] = sum(1 for p in REGIME3 if p in R and (R[p].get("P9_coarse_b3_median_share_kept") or 1) < 0.5)
    out["P9_act_sh_b3_ge50"] = sum(1 for p in R if (R[p].get("P9_act_sh_b3_median_share_kept") or 0) >= 0.5)
    out["act_sh_b3_ge50_above"] = sum(1 for p in R if (R[p].get("act_sh_b3_frac_above_null") or 0) >= 0.5)
    out["P2_v3_pooled_sig"] = {p: R[p]["v3"]["pooled_v3s"].get("flip_p") for p in R}
    pv = {p: R[p]["v3"]["pooled_v3s"].get("newton") for p in R}
    out["P6_v3_ratio_G27_over_r3"] = {p: (pv["G27"] / pv[p]) if (pv.get("G27") and pv.get(p) and pv[p] > 0) else None
                                      for p in REGIME3 if p in pv}
    pvh = {p: R[p]["v3"]["pooled_v3h"].get("newton") for p in R}
    out["P6_v3h_ratio_G27_over_r3"] = {p: (pvh["G27"] / pvh[p]) if (pvh.get("G27") and pvh.get(p) and pvh[p] > 0) else None
                                       for p in REGIME3 if p in pvh}
    # stratified family meta over regime III
    fam = {}
    cols = ("coarse_newton_exc", "coarse_b3_newton_exc", "act_sh_newton_exc", "act_sh_b3_newton_exc", "v3s_exc",
            "act_sh_cfx_exc", "act_sh_b3_cfx_exc", "rank:act_sh_newton_exc", "rank:act_sh_b3_newton_exc")
    for c in cols:
        rank = c.startswith("rank:")
        cc = c.split(":")[-1]
        groups, diffs = [], []
        for p in REGIME3:
            if p not in A or cc not in A[p].columns:
                continue
            d_ = A[p].filter(pl.col(cc).is_not_null() & pl.col(cc).is_not_nan() & ~pl.col("lab").str.starts_with("Fine"))
            vals = d_[cc].to_numpy()
            if rank and len(vals):
                vals = stats.rankdata(vals) / len(vals)
            groups.append((vals, np.array(d_["lab"].to_list())))
            lb_ = np.array(d_["lab"].to_list())
            an, op = vals[lb_ == "Anthropic"], vals[lb_ == "OpenAI"]
            if len(an) and len(op):
                diffs.append(an.mean() - op.mean())
        e, pval = B.stratified_eta2(groups, rng, 5000)
        # stratified one-sided permutation of the summed Anthropic - OpenAI mean difference (HH19 as stated)
        ao = []
        for vv, lb in groups:
            m_ = (lb == "Anthropic") | (lb == "OpenAI")
            if (lb[m_] == "Anthropic").any() and (lb[m_] == "OpenAI").any():
                ao.append((vv[m_], lb[m_]))
        def sdiff(gs):
            return sum(v_[l_ == "Anthropic"].mean() - v_[l_ == "OpenAI"].mean() for v_, l_ in gs)
        p_ao = None
        if ao:
            obs_ao = sdiff(ao)
            null_ao = np.array([sdiff([(v_, rng.permutation(l_)) for v_, l_ in ao]) for _ in range(5000)])
            p_ao = float((1 + np.sum(null_ao >= obs_ao - 1e-12)) / 5001)
        fam[c] = {"sum_eta2": e, "p": pval, "n_periods": len([g for g in groups if len(g[0]) >= 4]), "p_anth_gt_openai": p_ao,
                  "anth_minus_openai_sum": float(np.sum(diffs)) if diffs else None,
                  "anth_gt_openai_periods": int(np.sum(np.array(diffs) > 0)) if diffs else None, "n_diff": len(diffs)}
    out["family_meta"] = fam
    (RES / "summary_r1b.json").write_text(json.dumps(jsonable(out), indent=1))
    print(json.dumps(jsonable({k: v for k, v in out.items() if k != "periods"}), indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", nargs="*")
    ap.add_argument("--R", type=int, default=200)
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--v3-b1c", action="store_true", help="add the amended symmetric burn-in variant to existing results")
    a = ap.parse_args()
    if a.summarize:
        summarize()
        return
    if a.v3_b1c:
        for p in (a.period or list(PERIODS)):
            f = RES / p / "results.json"
            res = json.loads(f.read_text())
            goals = PERIODS[p]
            rng = np.random.default_rng(20261104 + goals[0])
            v, P, names = load_v3(goals)
            vdays = sorted(v["pt_date"].unique().to_list())
            vcode = {d_: i for i, d_ in enumerate(vdays)}
            day_codes = np.array([vcode[x] for x in v["pt_date"].to_list()])
            i0, i1 = v3_pairs(v, b1c=True)
            res["v3"]["pooled_v3s_b1c"] = jsonable(soft_test(P, v, i0, i1, a.R, rng, day_codes))
            pv = res["v3"]["pooled_v3s"].get("newton")
            pb = res["v3"]["pooled_v3s_b1c"].get("newton")
            res["v3s_b1c_share_kept"] = float(pb / pv) if (pv and pv > 0 and pb is not None) else None
            f.write_text(json.dumps(jsonable(res), indent=1))
            print(p, res["v3"]["pooled_v3s_b1c"], res["v3s_b1c_share_kept"], flush=True)
        return
    for p in (a.period or list(PERIODS)):
        run(p, R=a.R, fast=a.fast)


if __name__ == "__main__":
    main()
