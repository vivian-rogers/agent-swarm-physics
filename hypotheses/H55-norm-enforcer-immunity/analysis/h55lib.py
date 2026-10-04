"""H55 estimators, shared by synthetic.py, explore.py, native.py and confirm.py.

Friction (agent level, O3): ordered-logit speaker/target fields (H37 / infra nulls.fit_ordinal) on DQ2 reply pairs;
Spearman(c_j, nu_j) with agent permutation; partial version controlling the agent's own speaker field.
Friction (message level, O4): within-target contrast of reply stance to correction vs non-correction parents with
speaker and target fixed effects (FWL by alternating demeaning); target-day cluster bootstrap.
Immune contrast (O5/O6): matched treated (directed correction read) vs control (directed non-correction read) steps,
strata on pre-treatment / symmetric features, same-agent controls preferred; agent-day cluster bootstrap.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h55common as H  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

import nulls as NL  # noqa: E402  (infra/shared, on sys.path via h55common)

MIN_SENT, MIN_RECV = 20, 20


# ======================================================================================================== friction
def pair_table(od: Path = H.OUT, allow_holdout: bool = False) -> pl.DataFrame:
    """Agent->agent DQ2 candidate pairs with p_reply >= 0.5; y in {-1,0,+1} at conf >= 0.8; soft s; parent flags."""
    rp = (pl.scan_parquet(H.SH / "reply_pairs.parquet")
          .filter((pl.col("pair_set") == "cand") & pl.col("labelled") & (pl.col("a_kind") == 0)
                  & (pl.col("p_reply") >= 0.5) & (pl.col("a_agent") != pl.col("b_agent")))
          .select("B_message_id", "A_message_id", "b_agent", "a_agent", "pt_date", "goal_no", "holdout", "p_reply",
                  "p_supports", "p_opposes", pl.col("stance").cast(pl.Utf8), "stance_conf",
                  pl.col("opp_type").cast(pl.Utf8))
          .collect())
    if not allow_holdout:
        rp = rp.filter(~pl.col("holdout"))
    m = pl.read_parquet(od / "messages.parquet").select("message_id", "corr_jev", "corr_lex", "length", "unit_id", "t")
    rp = rp.join(m.rename({"message_id": "A_message_id", "corr_jev": "A_corr", "corr_lex": "A_lex", "length": "A_len",
                           "unit_id": "A_unit", "t": "tA"}), on="A_message_id", how="left")
    rp = rp.join(m.select("message_id", "corr_jev", "unit_id").rename({"message_id": "B_message_id", "corr_jev": "B_corr"}),
                 on="B_message_id", how="left")
    rp = rp.with_columns(
        pl.when((pl.col("stance") == "opposes") & (pl.col("stance_conf") >= 0.8)).then(-1)
        .when((pl.col("stance") == "supports") & (pl.col("stance_conf") >= 0.8)).then(1).otherwise(0).cast(pl.Int8).alias("y"),
        (pl.col("p_supports").fill_null(0) - pl.col("p_opposes").fill_null(0)).alias("s"),
        pl.col("A_corr").fill_null(False), pl.col("B_corr").fill_null(False))
    return rp


def sender_rates(msgs: pl.DataFrame) -> pl.DataFrame:
    """Per agent x goal period: messages with a DQ2 parent (the sensor's coverage) and Jev corrections among them."""
    a = msgs.filter((pl.col("speaker_kind") == "agent") & pl.col("parent_id").is_not_null())
    return a.group_by("goal_no", "agent").agg(pl.len().alias("n_par"), pl.col("corr_jev").sum().alias("n_corr"),
                                              pl.col("corr_lex").sum().alias("n_lex"),
                                              pl.len().alias("n_any")).with_columns(
        (pl.col("n_corr") / pl.col("n_par")).alias("c"))


def fit_fields(pp: pl.DataFrame):
    ag = np.unique(np.r_[pp["b_agent"].to_numpy(), pp["a_agent"].to_numpy()])
    idx = {a: k for k, a in enumerate(ag)}
    spk = np.array([idx[a] for a in pp["b_agent"].to_numpy()])
    tgt = np.array([idx[a] for a in pp["a_agent"].to_numpy()])
    y = pp["y"].to_numpy().astype(int) + 1
    c, a, b, ok = NL.fit_ordinal(spk, tgt, y, len(ag))
    return ag, a, b, ok, spk, tgt


def _rank_resid(x, z):
    rx, rz = stats.rankdata(x), stats.rankdata(z)
    beta = np.polyfit(rz, rx, 1)
    return rx - np.polyval(beta, rz)


def friction_agent(pp: pl.DataFrame, rates: pl.DataFrame, R: int = 5000, rng=None, ag_min=6):
    """pp: one period's pairs; rates: that period's sender rates. Returns dict with rho, p (one-sided greater), partial."""
    rng = rng or np.random.default_rng(H.SEED)
    if pp.height < 50:
        return {"scorable": False, "why": "pairs < 50"}
    ag, a, b, ok, spk, tgt = fit_fields(pp)
    nrecv = np.bincount(tgt, minlength=len(ag))
    nsent = np.bincount(spk, minlength=len(ag))
    rr = dict(zip(rates["agent"].to_list(), zip(rates["n_par"].to_list(), rates["c"].to_list())))
    keep = [k for k, g in enumerate(ag) if nrecv[k] >= MIN_RECV and nsent[k] >= MIN_SENT and g in rr and rr[g][0] >= MIN_SENT]
    if len(keep) < ag_min:
        return {"scorable": False, "why": f"eligible agents {len(keep)} < {ag_min}", "n_agents": len(keep)}
    keep = np.array(keep)
    c = np.array([rr[ag[k]][1] for k in keep])
    nu = -b[keep]
    sp = a[keep]
    if np.all(c == c[0]):
        return {"scorable": False, "why": "no variation in c", "n_agents": len(keep)}
    rho = stats.spearmanr(c, nu).statistic
    perm = np.array([stats.spearmanr(rng.permutation(c), nu).statistic for _ in range(R)])
    p = (1 + np.sum(perm >= rho)) / (R + 1)
    # partial: rank residuals of c and nu on the agent's own speaker field
    rc, rn = _rank_resid(c, sp), _rank_resid(nu, sp)
    rho_p = float(np.corrcoef(rc, rn)[0, 1])
    permp = np.array([np.corrcoef(_rank_resid(cc, sp), rn)[0, 1] for cc in (rng.permutation(c) for _ in range(min(R, 2000)))])
    pp_ = (1 + np.sum(permp >= rho_p)) / (len(permp) + 1)
    return {"scorable": True, "n_agents": int(len(keep)), "n_pairs": int(pp.height), "rho": float(rho), "p": float(p),
            "rho_partial": rho_p, "p_partial": float(pp_), "fit_ok": ok,
            "agents": [int(ag[k]) for k in keep], "c": c.tolist(), "nu": nu.tolist(), "a": sp.tolist(),
            "frac_y_neg": float((pp["y"] == -1).mean())}


def _demean2(v, g1, g2, n1, n2, it=30):
    r = v.astype(float).copy()
    for _ in range(it):
        r -= (np.bincount(g1, r, n1) / np.maximum(np.bincount(g1, None, n1), 1))[g1]
        r -= (np.bincount(g2, r, n2) / np.maximum(np.bincount(g2, None, n2), 1))[g2]
    return r


def friction_message(pp: pl.DataFrame, xcol: str = "A_corr", B: int = 1000, rng=None, min_treated=20):
    """Within-target, within-speaker contrast of soft stance s for replies to parents with xcol True vs False."""
    rng = rng or np.random.default_rng(H.SEED + 1)
    x = pp[xcol].cast(pl.Float64).to_numpy()
    if x.sum() < min_treated:
        return {"scorable": False, "why": f"treated replies {int(x.sum())} < {min_treated}", "n_treated": int(x.sum())}
    s = pp["s"].to_numpy().astype(float)
    w = pp["p_reply"].to_numpy().astype(float)
    _, g1 = np.unique(pp["b_agent"].to_numpy(), return_inverse=True)
    _, g2 = np.unique(pp["a_agent"].to_numpy(), return_inverse=True)
    rx = _demean2(x, g1, g2, g1.max() + 1, g2.max() + 1)
    rs = _demean2(s, g1, g2, g1.max() + 1, g2.max() + 1)
    gam = float(np.sum(w * rx * rs) / np.sum(w * rx * rx))
    cl = (pp["a_agent"].cast(pl.Utf8) + "_" + pp["pt_date"]).to_numpy()
    u, inv = np.unique(cl, return_inverse=True)
    num = np.bincount(inv, w * rx * rs, len(u))
    den = np.bincount(inv, w * rx * rx, len(u))
    idx = rng.integers(0, len(u), (B, len(u)))
    bs = num[idx].sum(1) / np.maximum(den[idx].sum(1), 1e-12)
    se = bs.std(ddof=1)
    p = float(2 * stats.t.sf(abs(gam) / se, len(u) - 1)) if se > 0 else float("nan")
    raw = float(s[x == 1].mean() - s[x == 0].mean())
    negsh = float((pp.filter(pl.col(xcol))["y"] == -1).mean()) - float((pp.filter(~pl.col(xcol))["y"] == -1).mean())
    return {"scorable": True, "gamma": gam, "se": float(se), "p": p, "lo": float(np.quantile(bs, 0.025)),
            "hi": float(np.quantile(bs, 0.975)), "n_treated": int(x.sum()), "n": int(len(x)), "raw_diff": raw,
            "neg_share_diff": negsh, "n_clusters": int(len(u))}


# ================================================================================================ immune contrast
def steps_with_reads(steps: pl.DataFrame, reads: pl.DataFrame, vol: pl.DataFrame, key: str, sensor: str = "corr_jev"):
    """One row per at-risk step with outcome: features of the first directed read, counts, treated flag."""
    rd = reads.sort("t_call")
    g = rd.group_by(key).agg(
        pl.len().alias("n_dir"), pl.col(sensor).sum().alias("n_trt"),
        pl.col("ikind").first().alias("first_kind"), pl.col("ment").first().alias("first_named"),
        pl.col("length").first().alias("first_len"),
        (pl.col("novelty").first() if "novelty" in rd.columns else pl.lit(None, pl.Float32)).alias("first_nov"),
        pl.col("q_soft").sum().alias("q_sum"),
        # first *treated* read features where treated (so treated rows describe their correction)
        pl.col("ikind").filter(pl.col(sensor)).first().alias("trt_kind"),
        pl.col("ment").filter(pl.col(sensor)).first().alias("trt_named"),
        pl.col("length").filter(pl.col(sensor)).first().alias("trt_len"),
        (pl.col("novelty").filter(pl.col(sensor)).first() if "novelty" in rd.columns else pl.lit(None, pl.Float32)).alias("trt_nov"))
    s = steps.join(g, left_on="message_id" if key == "anchor_id" else "win_id", right_on=key, how="left") \
        .join(vol, left_on="message_id" if key == "anchor_id" else "win_id", right_on=key, how="left")
    s = s.with_columns(pl.col("n_dir").fill_null(0), pl.col("n_trt").fill_null(0), pl.col("items_read").fill_null(0))
    s = s.with_columns(
        (pl.col("n_trt") > 0).alias("treated"),
        ((pl.col("n_dir") > 0) & (pl.col("n_trt") == 0)).alias("control"),
        pl.when(pl.col("n_trt") > 0).then(pl.col("trt_kind")).otherwise(pl.col("first_kind")).alias("kind_m"),
        pl.when(pl.col("n_trt") > 0).then(pl.col("trt_named")).otherwise(pl.col("first_named")).alias("named_m"),
        pl.when(pl.col("n_trt") > 0).then(pl.col("trt_len")).otherwise(pl.col("first_len")).alias("len_m"),
        pl.when(pl.col("n_trt") > 0).then(pl.col("trt_nov")).otherwise(pl.col("first_nov")).alias("nov_m"))
    return s


def _agebin(k):
    return np.where(k <= 2, 0, np.where(k <= 4, 1, 2))


def _demean_agent(s: pl.DataFrame) -> pl.DataFrame:
    """Agent fixed effect on the outcome: ya = y - mean_y(agent, goal period, all at-risk steps) + grand mean.
    Added 2026-10-04 after the synthetic null (S2/S3): pooled-stratum controls let agent frailty leak into Delta when
    corrections target escape-prone agents (blocked size 0.11 real sensor, 0.51 perfect sensor)."""
    d = s.filter(pl.col("y").is_not_null())
    gm = float(d["y"].mean()) if d.height else 0.0
    return s.with_columns((pl.col("y").cast(pl.Float64) - pl.col("y").cast(pl.Float64).mean().over(["agent", "goal_no"]) + gm).alias("ya"))


def immune_contrast(s: pl.DataFrame, by_unit: bool = True, R: int = 10, novelty: bool = False, rng=None, B: int = 1000,
                    min_treated: int = 1, demean_agent: bool = True):
    """Matched Delta = mean(y_t - mean y_c) over treated steps. s: steps_with_reads output (y not null)."""
    rng = rng or np.random.default_rng(H.SEED + 2)
    s = _demean_agent(s) if demean_agent else s.with_columns(pl.col("y").cast(pl.Float64).alias("ya"))
    d = s.filter(pl.col("y").is_not_null() & (pl.col("treated") | pl.col("control")))
    if d.filter(pl.col("treated")).height < min_treated:
        return {"scorable": False, "n_treated": int(d.filter(pl.col("treated")).height)}
    # length tercile within goal period (on directed reads in this set)
    d = d.with_columns(pl.col("len_m").fill_null(0).rank("ordinal").over("goal_no").alias("_r"),
                       pl.len().over("goal_no").alias("_n"))
    d = d.with_columns(((pl.col("_r") - 1) * 3 // pl.col("_n")).alias("lenT"))
    cols = ["agebin", "kind_m", "named_m", "lenT", "nbin"] + (["novT"] if novelty else [])
    d = d.with_columns(pl.Series("agebin", _agebin(d["k"].to_numpy())),
                       (pl.col("n_dir") >= 2).cast(pl.Int8).alias("nbin"),
                       pl.col("named_m").fill_null(False))
    if novelty:
        d = d.with_columns(pl.col("nov_m").fill_null(pl.col("nov_m").median()).rank("ordinal").over("goal_no").alias("_q"))
        d = d.with_columns(((pl.col("_q") - 1) * 3 // pl.col("_n")).alias("novT"))
    ucol = "unit_id" if by_unit else "goal_no"
    d = d.with_columns(pl.concat_str([pl.col(ucol).cast(pl.Utf8)] + [pl.col(c).cast(pl.Utf8) for c in cols], separator="|").alias("stratum"))
    T = d.filter(pl.col("treated"))
    Cn = d.filter(pl.col("control"))
    cg = {}
    for st, ys, ags in Cn.group_by("stratum").agg(pl.col("ya"), pl.col("agent")).iter_rows():
        cg[st] = (np.asarray(ys, float), np.asarray(ags))
    diffs, cl, used = [], [], 0
    for r in T.iter_rows(named=True):
        if r["stratum"] not in cg:
            continue
        ys, ags = cg[r["stratum"]]
        same = ys[ags == r["agent"]]
        pool = same if len(same) >= 3 else ys
        pick = pool[rng.integers(0, len(pool), min(R, max(len(pool), 1)))]
        diffs.append(r["ya"] - pick.mean())
        cl.append(f"{r['agent']}_{r['pt_date']}")
        used += 1
    if used < min_treated:
        return {"scorable": False, "n_treated": int(T.height), "n_matched": used}
    diffs = np.array(diffs)
    est, lo, hi, p = NL.cluster_boot_test(diffs, np.array(cl), B=B, rng=rng)
    return {"scorable": True, "delta": float(est), "lo": lo, "hi": hi, "p": p, "n_treated": int(T.height), "n_matched": used,
            "n_control": int(Cn.height), "y_treated": float(np.mean([T["y"].mean()])), "y_control": float(Cn["y"].mean()),
            "diffs": diffs.tolist(), "clusters": cl}


def address_contrast(s: pl.DataFrame, rng=None, R=10, B=1000):
    """R-address: steps with >= 1 directed read vs steps with none, matched on unit x age bin x items-read tercile."""
    rng = rng or np.random.default_rng(H.SEED + 3)
    d = _demean_agent(s).filter(pl.col("y").is_not_null())
    d = d.with_columns(pl.Series("agebin", _agebin(d["k"].to_numpy())),
                       (pl.col("n_dir") > 0).alias("dir"),
                       pl.col("items_read").rank("ordinal").over("goal_no").alias("_r"), pl.len().over("goal_no").alias("_n"))
    d = d.with_columns(((pl.col("_r") - 1) * 3 // pl.col("_n")).alias("volT"))
    d = d.with_columns(pl.concat_str([pl.col("unit_id"), pl.col("agebin").cast(pl.Utf8), pl.col("volT").cast(pl.Utf8)], separator="|").alias("st"))
    C = {st: (np.asarray(y, float), np.asarray(a)) for st, y, a in d.filter(~pl.col("dir")).group_by("st").agg(pl.col("ya"), pl.col("agent")).iter_rows()}
    diffs, cl = [], []
    for r in d.filter(pl.col("dir")).iter_rows(named=True):
        if r["st"] not in C:
            continue
        ys, ags = C[r["st"]]
        same = ys[ags == r["agent"]]
        pool = same if len(same) >= 3 else ys
        diffs.append(r["ya"] - pool[rng.integers(0, len(pool), R)].mean())
        cl.append(f"{r['agent']}_{r['pt_date']}")
    if len(diffs) < 5:
        return {"scorable": False, "n": len(diffs)}
    est, lo, hi, p = NL.cluster_boot_test(np.array(diffs), np.array(cl), B=B, rng=rng)
    return {"scorable": True, "delta": est, "lo": lo, "hi": hi, "p": p, "n": len(diffs)}


def random_effects(est, se):
    """DerSimonian-Laird random-effects mean of per-period estimates."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"k": 0}
    w = 1 / se ** 2
    mu_f = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - mu_f) ** 2)
    tau2 = max(0.0, (Q - (len(est) - 1)) / (np.sum(w) - np.sum(w ** 2) / np.sum(w))) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = np.sum(ws * est) / np.sum(ws)
    sem = np.sqrt(1 / np.sum(ws))
    return {"k": int(len(est)), "mu": float(mu), "se": float(sem), "z": float(mu / sem), "p_two": float(2 * stats.norm.sf(abs(mu / sem))),
            "tau2": float(tau2), "Q": float(Q), "n_pos": int((est > 0).sum())}


def fisher_z_meta(rhos, ns):
    """Random-effects mean of Spearman rho via Fisher z (se = 1.06/sqrt(n-3), Fieller)."""
    r = np.clip(np.asarray(rhos, float), -0.999, 0.999)
    n = np.asarray(ns, float)
    z = np.arctanh(r)
    se = 1.06 / np.sqrt(np.maximum(n - 3, 1))
    re = random_effects(z, se)
    if re.get("k", 0):
        re["rho"] = float(np.tanh(re["mu"]))
    return re
