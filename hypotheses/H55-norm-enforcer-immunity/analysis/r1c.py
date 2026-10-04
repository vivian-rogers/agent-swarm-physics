"""H55 round 1c: friction and immune tests re-run with stance v2.1 sensors (card "Round 1c", pre-registered
2026-10-04 22:14 UTC).

  uv run python hypotheses/H55-norm-enforcer-immunity/analysis/r1c.py synth   # synthetic validation first
  uv run python hypotheses/H55-norm-enforcer-immunity/analysis/r1c.py real

Sensors (a message's v2 class is its label toward its DQ2 parent; reply_stance_v2, non-holdout):
  C_v2   = stance2 in {correct, decline}      (correction sensor; precision ~0.5, recall ~0.7)
  decl   = stance2 == decline                 (secondary)
  D      = disagree_validated_agent of the reply (friction outcome; precision 0.61-0.67, recall ~0.6)
Round-1 estimators reused from analysis/h55lib.py (immune_contrast, address_contrast, random_effects, fisher_z_meta);
round-1 inputs untouched (corr_jev stays the round-1 sensor). Label-noise null: analysis/stance_noise.py.
Writes data/processed/H55-norm-enforcer-immunity/r1c/{synth,real}.json.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h55lib as L  # noqa: E402
from h55lib import H  # noqa: E402
import stance_noise as SN  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

OUT = H.OUT / "r1c"
SEED = H.SEED + 1055
PC, RC = 0.5, 0.7          # correction sensor precision / recall (pre-registered)
MIN_SENT = MIN_RECV = 20


def jd(o):
    def d(x):
        if isinstance(x, dict):
            return {str(k): d(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [d(v) for v in x]
        if isinstance(x, np.ndarray):
            return d(x.tolist())
        if isinstance(x, (np.floating, float)):
            return None if not np.isfinite(x) else float(x)
        if isinstance(x, np.integer):
            return int(x)
        if isinstance(x, np.bool_):
            return bool(x)
        return x
    return json.dumps(d(o), indent=1, default=str)


# ============================================================================================ inputs
_CACHE = {}


def msg_v2():
    """Per message: its v2 class toward its DQ2 parent (C_v2, decl)."""
    if "m" not in _CACHE:
        m = pl.read_parquet(H.OUT / "messages.parquet").select("message_id", "parent_id", "goal_no", "speaker_kind", "agent", "unit_id")
        v2 = SN.load_v2(["B_message_id", "A_message_id", "stance2", "stance2_conf"])
        m = m.join(v2.rename({"B_message_id": "message_id", "A_message_id": "parent_id"}), on=["message_id", "parent_id"], how="left")
        st = pl.col("stance2").cast(pl.String)
        m = m.with_columns(C_v2=st.is_in(["correct", "decline"]).fill_null(False), decl_v2=(st == "decline").fill_null(False),
                           v2_labelled=pl.col("stance2").is_not_null())
        _CACHE["m"] = m
    return _CACHE["m"]


def pairs():
    """Agent->agent reply pairs (p_reply >= 0.5, non-holdout) with the reply's v2 D / s2 / fp profile and the parent's
    v2 correction flags."""
    if "p" not in _CACHE:
        v2 = SN.load_v2().filter((pl.col("a_kind") == 0) & (pl.col("b_agent") != pl.col("a_agent")))
        g = SN.fp_profile(v2)
        v2 = v2.with_columns(D=pl.col("disagree_validated_agent").cast(pl.Float64), s2=pl.col("s2_soft").cast(pl.Float64),
                             g=pl.Series(g))
        m = msg_v2().select(pl.col("message_id").alias("A_message_id"), pl.col("C_v2").alias("A_C"), pl.col("decl_v2").alias("A_decl"),
                            pl.col("v2_labelled").alias("A_lab"))
        p = v2.join(m, on="A_message_id", how="left").with_columns(pl.col("A_C").fill_null(False), pl.col("A_decl").fill_null(False))
        cc = pl.read_parquet(H.SH / "chat_core.parquet", columns=["message_id", "t"]).rename({"message_id": "B_message_id"})
        p = p.join(cc, on="B_message_id", how="left")
        p = p.with_columns(block=(pl.col("room").cast(pl.Int64) * 10_000_000 + pl.col("t").dt.epoch("s") // 1800))
        _CACHE["p"] = p
    return _CACHE["p"]


def sender_rates_v2():
    m = msg_v2().filter((pl.col("speaker_kind") == "agent") & pl.col("parent_id").is_not_null() & pl.col("v2_labelled"))
    return m.group_by("goal_no", "agent").agg(pl.len().alias("n_par"), pl.col("C_v2").sum().alias("n_C"),
                                              pl.col("decl_v2").sum().alias("n_decl")).with_columns(
        (pl.col("n_C") / pl.col("n_par")).alias("c"), (pl.col("n_decl") / pl.col("n_par")).alias("c_decl"))


def codes(p):
    ag = np.unique(np.r_[p["b_agent"].to_numpy(), p["a_agent"].to_numpy()])
    idx = {a: k for k, a in enumerate(ag)}
    return ag, np.array([idx[a] for a in p["b_agent"].to_numpy()]), np.array([idx[a] for a in p["a_agent"].to_numpy()])


def twoway_fields(spk, tgt, y, N, it=60):
    y = np.asarray(y, float)
    a, b = np.zeros(N), np.zeros(N)
    mu = y.mean()
    ns, nt = np.maximum(np.bincount(spk, None, N), 1), np.maximum(np.bincount(tgt, None, N), 1)
    for _ in range(it):
        a = np.bincount(spk, y - mu - b[tgt], N) / ns
        b = np.bincount(tgt, y - mu - a[spk], N) / nt
    return a, b


# ============================================================================================ estimators
def friction_agent_v2(p, rates, rng, R=5000, ccol="c", D=None):
    if p.height < 50:
        return {"scorable": False, "why": "pairs < 50"}
    ag, spk, tgt = codes(p)
    y = p["D"].to_numpy() if D is None else D
    a, b = twoway_fields(spk, tgt, y, len(ag))
    nrecv, nsent = np.bincount(tgt, minlength=len(ag)), np.bincount(spk, minlength=len(ag))
    rr = dict(zip(rates["agent"].to_list(), zip(rates["n_par"].to_list(), rates[ccol].to_list())))
    keep = [k for k, gg in enumerate(ag) if nrecv[k] >= MIN_RECV and nsent[k] >= MIN_SENT and gg in rr and rr[gg][0] >= MIN_SENT]
    if len(keep) < 6:
        return {"scorable": False, "why": f"eligible agents {len(keep)} < 6", "n_agents": len(keep)}
    keep = np.array(keep)
    c = np.array([rr[ag[k]][1] for k in keep])
    nu, sp = b[keep], a[keep]
    if np.all(c == c[0]) or np.all(nu == nu[0]):
        return {"scorable": False, "why": "no variation", "n_agents": len(keep)}
    rho = stats.spearmanr(c, nu).statistic
    perm = np.array([stats.spearmanr(rng.permutation(c), nu).statistic for _ in range(R)])
    rc, rn = L._rank_resid(c, sp), L._rank_resid(nu, sp)
    rho_p = float(np.corrcoef(rc, rn)[0, 1])
    return {"scorable": True, "n_agents": int(len(keep)), "rho": float(rho),
            "p_greater": float((1 + np.sum(perm >= rho)) / (R + 1)), "p_less": float((1 + np.sum(perm <= rho)) / (R + 1)),
            "rho_partial": rho_p, "agents": [int(ag[k]) for k in keep], "c": c.tolist(), "nu": nu.tolist()}


def gamma_D(y, x, w, g1, g2):
    rx = L._demean2(x, g1, g2, g1.max() + 1, g2.max() + 1)
    ry = L._demean2(y, g1, g2, g1.max() + 1, g2.max() + 1)
    den = np.sum(w * rx * rx)
    return float(np.sum(w * rx * ry) / den) if den > 0 else np.nan, rx, ry


def friction_message_v2(p, xcol, rng, B=1000, min_treated=20, R_ng=500, ng=True):
    x = p[xcol].cast(pl.Float64).to_numpy()
    if x.sum() < min_treated:
        return {"scorable": False, "n_treated": int(x.sum())}
    y = p["D"].to_numpy()
    w = p["p_reply"].to_numpy().astype(float)
    _, g1 = np.unique(p["b_agent"].to_numpy(), return_inverse=True)
    _, g2 = np.unique(p["a_agent"].to_numpy(), return_inverse=True)
    gam, rx, ry = gamma_D(y, x, w, g1, g2)
    cl = (p["a_agent"].cast(pl.Utf8) + "_" + p["pt_date"]).to_numpy()
    u, inv = np.unique(cl, return_inverse=True)
    num, den = np.bincount(inv, w * rx * ry, len(u)), np.bincount(inv, w * rx * rx, len(u))
    idx = rng.integers(0, len(u), (B, len(u)))
    bs = num[idx].sum(1) / np.maximum(den[idx].sum(1), 1e-12)
    se = float(bs.std(ddof=1))
    out = {"scorable": True, "gamma": gam, "se": se, "lo": float(np.quantile(bs, 0.025)), "hi": float(np.quantile(bs, 0.975)),
           "p_boot_two": float(2 * stats.t.sf(abs(gam) / se, len(u) - 1)) if se > 0 else None, "n_treated": int(x.sum()),
           "n": int(len(x)), "rate_treated": float(y[x == 1].mean()), "rate_control": float(y[x == 0].mean())}
    s2 = p["s2"].to_numpy()
    out["gamma_s2"] = gamma_D(s2, x, w, g1, g2)[0]
    if ng:
        ag, spk, tgt = codes(p)
        N = SN.NoiseNull([spk, tgt], y, p["g"].to_numpy(), p["block"].to_numpy())
        nul = np.array([gamma_D(N.draw(rng), x, w, g1, g2)[0] for _ in range(R_ng)])
        fexp, fbar = N.f_expected()
        gf = gamma_D(fexp, x, w, g1, g2)[0]
        out.update({"p_NG_greater": SN.p_greater(gam, nul), "p_NG_less": SN.p_less(gam, nul), "null_sd": float(np.nanstd(nul)),
                    "null_mean": float(np.nanmean(nul)),
                    "gamma_f": gf, "gamma_corrected": (gam - gf) / (SN.R_POINT - fbar)})
    return out


# ============================================================================================ synthetic
def synth_p1_rep(args):
    g, beta, seed = args
    rng = np.random.default_rng(seed)
    p = pairs().filter(pl.col("goal_no") == g)
    rates = sender_rates_v2().filter(pl.col("goal_no") == g)
    ag, spk, tgt = codes(p)
    npar = dict(zip(rates["agent"].to_list(), rates["n_par"].to_list()))
    lc = rng.normal(np.log(0.1 / 0.9), 0.6, len(ag))
    ctrue = 1 / (1 + np.exp(-lc))
    base, tp = 0.10, RC * 0.10
    fpr = tp * (1 - PC) / PC / (1 - base)
    n = np.array([npar.get(a, 0) for a in ag])
    nt = rng.binomial(n, ctrue)
    nobs = rng.binomial(nt, RC) + rng.binomial(n - nt, fpr)
    cobs = np.where(n > 0, nobs / np.maximum(n, 1), 0)
    z = (lc - lc.mean()) / lc.std()
    a_f, b_f = rng.normal(0, 0.6, len(ag)), rng.normal(0, 0.6, len(ag))
    eta = a_f[spk] + b_f[tgt] + beta * z[tgt]
    pi, r = rng.uniform(*SN.PI_RANGE), rng.uniform(*SN.R_RANGE)
    dbar = float(p["D"].mean())
    delta = SN._shift(eta, pi * dbar / r)
    dstar = rng.random(len(eta)) < 1 / (1 + np.exp(-(eta + delta)))
    gg = p["g"].to_numpy()
    f = np.clip(SN.implied_fpr(dbar, pi, r) * gg / gg.mean(), 0, 0.5)
    y = np.where(dstar, rng.random(len(eta)) < r, rng.random(len(eta)) < f).astype(float)
    rs = pl.DataFrame({"agent": ag, "n_par": n, "c": cobs})
    fa = friction_agent_v2(p, rs, rng, R=500, D=y)
    return g, beta, fa.get("rho"), fa.get("p_greater"), fa.get("n_agents")


def synth_p2_rep(args):
    periods, delta, seed = args
    rng = np.random.default_rng(seed)
    est, se = [], []
    for g in periods:
        p = pairs().filter(pl.col("goal_no") == g)
        ua, ainv = np.unique(p["A_message_id"].to_numpy(), return_inverse=True)
        base = 0.10
        tc = rng.random(len(ua)) < base
        fpr = RC * base * (1 - PC) / PC / (1 - base)
        obs = np.where(tc, rng.random(len(ua)) < RC, rng.random(len(ua)) < fpr)[ainv].astype(float)
        ag, spk, tgt = codes(p)
        a_f, b_f = rng.normal(0, 0.6, len(ag)), rng.normal(0, 0.6, len(ag))
        eta = a_f[spk] + b_f[tgt] + delta * tc[ainv]
        pi, r = rng.uniform(*SN.PI_RANGE), rng.uniform(*SN.R_RANGE)
        dbar = float(p["D"].mean())
        sh = SN._shift(a_f[spk] + b_f[tgt], pi * dbar / r)
        dstar = rng.random(len(eta)) < 1 / (1 + np.exp(-(eta + sh)))
        gg = p["g"].to_numpy()
        f = np.clip(SN.implied_fpr(dbar, pi, r) * gg / gg.mean(), 0, 0.5)
        y = np.where(dstar, rng.random(len(eta)) < r, rng.random(len(eta)) < f).astype(float)
        q = p.with_columns(pl.Series("D", y), pl.Series("X", obs))
        fm = friction_message_v2(q, "X", rng, B=200, ng=False)
        if fm.get("scorable"):
            est.append(fm["gamma"]); se.append(fm["se"])
    re = L.random_effects(np.array(est), np.array(se))
    return delta, re.get("mu"), re.get("p_two"), re.get("k")


def synth_immune(kind, reps):
    import synthetic as S0
    s = S0.step_structure(kind)
    rd = pl.read_parquet(H.OUT / ("reads_loop.parquet" if kind == "loop" else "reads_blocked.parquet"))
    mv = msg_v2().select("message_id", "C_v2")
    rd = rd.join(mv, on="message_id", how="left").with_columns(pl.col("C_v2").fill_null(False))
    key = "anchor_id" if kind == "loop" else "win_id"
    st = s.filter(pl.col("y").is_not_null())
    keys = st["message_id" if kind == "loop" else "win_id"].to_list()
    rsub = rd.filter(pl.col(key).is_in(keys))
    r_obs = float(rsub["C_v2"].mean()) if rsub.height else 0.0
    base = PC * r_obs / RC
    S0.REC, S0.FPR = RC, (1 - PC) * r_obs / max(1 - base, 1e-6)
    out = []
    for bc in (0.0, 0.5, 1.0, 2.0):
        for k in range(reps):
            out.append(S0.s2_rep(s, bc, 0.4, False, 9000 + k + int(bc * 1000), base=base))
    df = pl.DataFrame(out)
    summ = df.group_by("beta_c").agg(pl.len().alias("reps"), ((pl.col("p") < 0.05) & (pl.col("delta") > 0)).mean().alias("power_pos"),
                                     (pl.col("p") < 0.05).mean().alias("rej_any"), pl.col("delta").mean().alias("delta_mean"),
                                     pl.col("n_treated").mean()).sort("beta_c")
    return {"obs_flag_rate_per_directed_read": r_obs, "implied_true_rate": base, "REC": S0.REC, "FPR": S0.FPR,
            "table": summ.to_dicts()}


def synth():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    jobs = [(g, b, SEED + 31 * k + int(10 * b) + g) for g in (51, 19, 38) for b in (0.0, 0.3, 0.6) for k in range(60)]
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(synth_p1_rep, jobs, chunksize=20))
    df = pl.DataFrame(res, schema=["goal", "beta", "rho", "p", "n_agents"], orient="row")
    out["P1"] = df.group_by("goal", "beta").agg(pl.len().alias("reps"), (pl.col("p") < 0.05).mean().alias("power"),
                                                pl.col("rho").mean(), pl.col("n_agents").mean()).sort("goal", "beta").to_dicts()
    print("P1", out["P1"], flush=True)
    # P2 over the periods where the real C_v2 sensor gives >= 20 treated replies (structural count, not an outcome)
    pp = pairs()
    cnt = pp.group_by("goal_no").agg(pl.col("A_C").sum().alias("n")).filter(pl.col("n") >= 20)
    periods = sorted(cnt["goal_no"].to_list())
    out["P2_periods"] = periods
    jobs = [(periods, d, SEED + 7 * k + int(10 * d)) for d in (0.0, 0.5, 1.0) for k in range(60)]
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(synth_p2_rep, jobs, chunksize=10))
    df2 = pl.DataFrame(res, schema=["delta", "mu", "p", "k"], orient="row")
    out["P2"] = df2.group_by("delta").agg(pl.len().alias("reps"), ((pl.col("p") < 0.05) & (pl.col("mu") > 0)).mean().alias("power_pos"),
                                          (pl.col("p") < 0.05).mean().alias("rej_any"), pl.col("mu").mean(), pl.col("k").mean()).sort("delta").to_dicts()
    print("P2", out["P2"], flush=True)
    out["P4_loop"] = synth_immune("loop", 150)
    print("P4", out["P4_loop"], flush=True)
    out["P5_blocked"] = synth_immune("blocked", 150)
    print("P5", out["P5_blocked"], flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    (OUT / "synth.json").write_text(jd(out))


# ============================================================================================ real
def real():
    t0 = time.time()
    rng = np.random.default_rng(SEED + 2)
    pp = pairs()
    rates = sender_rates_v2()
    periods = sorted(pp["goal_no"].unique().to_list())
    rows = []
    for g in periods:
        p = pp.filter(pl.col("goal_no") == g)
        rt = rates.filter(pl.col("goal_no") == g)
        r = {"goal_no": int(g), "n_pairs": p.height, "n_D": int(p["D"].sum()), "n_A_C": int(p["A_C"].sum())}
        fa = friction_agent_v2(p, rt, rng)
        fd = friction_agent_v2(p, rt, rng, ccol="c_decl")
        fm = friction_message_v2(p, "A_C", rng) if p.height >= 100 else {"scorable": False}
        fmd = friction_message_v2(p, "A_decl", rng) if p.height >= 100 else {"scorable": False}
        r["P1"] = {k: fa.get(k) for k in ("scorable", "n_agents", "rho", "p_greater", "p_less", "rho_partial", "why")}
        r["P1_decl"] = {k: fd.get(k) for k in ("scorable", "n_agents", "rho", "p_greater", "p_less")}
        r["P2"] = {k: v for k, v in fm.items()}
        r["P2_decl"] = {k: v for k, v in fmd.items()}
        rows.append(r)
        print(g, r["P1"].get("rho"), r["P2"].get("gamma"), r["P2"].get("p_NG_greater"), flush=True)
    summ = {}
    s1 = [r for r in rows if r["P1"].get("scorable")]
    summ["P1"] = {"k": len(s1), "n_pos": sum(r["P1"]["rho"] > 0 for r in s1),
                  "meta": L.fisher_z_meta([r["P1"]["rho"] for r in s1], [r["P1"]["n_agents"] for r in s1]),
                  "meta_partial": L.fisher_z_meta([r["P1"]["rho_partial"] for r in s1], [r["P1"]["n_agents"] for r in s1])}
    s1d = [r for r in rows if r["P1_decl"].get("scorable")]
    summ["P1_decl"] = {"k": len(s1d), "meta": L.fisher_z_meta([r["P1_decl"]["rho"] for r in s1d], [r["P1_decl"]["n_agents"] for r in s1d])}
    for key in ("P2", "P2_decl"):
        s2 = [r for r in rows if r[key].get("scorable")]
        if not s2:
            summ[key] = {"k": 0}
            continue
        re = L.random_effects(np.array([r[key]["gamma"] for r in s2]), np.array([r[key]["se"] for r in s2]))
        # NG-pooled: inverse-variance mean of (gamma - 0) against null sds, normal approx
        w = np.array([1 / r[key]["null_sd"] ** 2 for r in s2 if r[key].get("null_sd")])
        g_ = np.array([r[key]["gamma"] - r[key]["null_mean"] for r in s2 if r[key].get("null_sd")])
        zng = float(np.sum(w * g_) / np.sqrt(np.sum(w))) if len(w) else None
        summ[key] = {"k": len(s2), "n_pos": sum(r[key]["gamma"] > 0 for r in s2), "meta": re,
                     "z_NG_pooled": zng, "p_NG_pooled_greater": float(stats.norm.sf(zng)) if zng is not None else None,
                     "p_NG_pooled_less": float(stats.norm.cdf(zng)) if zng is not None else None,
                     "gamma_NG_pooled": float(np.sum(w * g_) / np.sum(w)) if len(w) else None,
                     "gamma_NG_pooled_se": float(1 / np.sqrt(np.sum(w))) if len(w) else None,
                     "gamma_corrected_median": float(np.median([r[key]["gamma_corrected"] for r in s2])),
                     "meta_s2": L.random_effects(np.array([r[key]["gamma_s2"] for r in s2]), np.array([r[key]["se"] for r in s2]))}
    # P3 descriptive: what v2 calls DQ2's confident received opposes (agent->agent)
    dq = pl.read_parquet(H.SH / "reply_stance_v2.parquet", columns=["B_message_id", "A_message_id", "dq2_stance", "dq2_stance_conf", "stance2", "a_kind"])
    dq = dq.filter((pl.col("a_kind") == 0) & (pl.col("dq2_stance").cast(pl.String) == "opposes") & (pl.col("dq2_stance_conf") >= 0.8))
    summ["P3_v2_composition_of_dq2_confident_opposes"] = dict(dq["stance2"].cast(pl.String).value_counts().iter_rows())
    # immune contrasts with the v2 sensor
    import explore as X
    for nm, kind, ver in (("P4_loop_restate", "loop", "restate"), ("P4_loop_copy", "loop", "copy"), ("P5_blocked", "blocked", None)):
        if kind == "loop":
            st = pl.read_parquet(H.OUT / "loop_steps.parquet").filter((pl.col("version") == ver) & pl.col("y").is_not_null())
            rd = pl.read_parquet(H.OUT / "reads_loop.parquet")
            vol = pl.read_parquet(H.OUT / "reads_loop_volume.parquet")
            keyc = "anchor_id"
        else:
            st = pl.read_parquet(H.OUT / "blocked_steps.parquet").filter(pl.col("y").is_not_null())
            st = st.with_columns((pl.col("t0").cast(pl.Int64).cast(pl.Utf8) + "_" + pl.col("agent").cast(pl.Utf8)).alias("win_id"))
            rd = pl.read_parquet(H.OUT / "reads_blocked.parquet").with_columns(pl.lit(None, pl.Float32).alias("novelty"))
            vol = pl.read_parquet(H.OUT / "reads_blocked_volume.parquet")
            keyc = "win_id"
        rd = rd.join(msg_v2().select("message_id", "C_v2", "decl_v2"), on="message_id", how="left").with_columns(
            pl.col("C_v2").fill_null(False), pl.col("decl_v2").fill_null(False))
        for sens in ("C_v2", "decl_v2"):
            s = L.steps_with_reads(st, rd, vol, keyc, sensor=sens)
            ic = L.immune_contrast(s, rng=rng, B=2000)
            ic.pop("diffs", None); ic.pop("clusters", None)
            summ[f"{nm}_{sens}"] = ic
            if sens == "C_v2":
                summ[f"{nm}_{sens}_hazard_fe"] = X.hazard_fe(s)
                if kind == "loop":
                    icn = L.immune_contrast(s, novelty=True, rng=rng, B=2000)
                    icn.pop("diffs", None); icn.pop("clusters", None)
                    summ[f"{nm}_{sens}_novelty"] = icn
                summ[f"{nm}_{sens}_counts"] = {"steps": s.height, "dir_steps": int((s["n_dir"] > 0).sum()), "trt_steps": int(s["treated"].sum())}
        if nm == "P4_loop_restate":
            # P8: share of restatement-loop episodes with >= 1 C_v2 directed read
            ep = st.select("episode", "message_id", "goal_no").join(
                rd.group_by("anchor_id").agg(pl.col("C_v2").sum().alias("nc"), pl.len().alias("nd")),
                left_on="message_id", right_on="anchor_id", how="left").group_by("episode").agg(
                pl.col("nc").fill_null(0).sum(), pl.col("nd").fill_null(0).sum())
            sh = float((ep["nc"] > 0).mean())
            summ["P8"] = {"episodes": ep.height, "share_with_C_v2": sh, "share_with_any_directed": float((ep["nd"] > 0).mean()),
                          "implied_true_share_point": min(1.0, sh * PC / RC), "implied_true_share_upper": min(1.0, sh * 0.7 / 0.5)}
    # G51 enforcers (descriptive)
    g51 = next((r for r in rows if r["goal_no"] == 51), None)
    if g51 and g51["P1"].get("scorable"):
        fa = friction_agent_v2(pp.filter(pl.col("goal_no") == 51), rates.filter(pl.col("goal_no") == 51), rng)
        gt = pl.read_parquet(H.SH / "ground_truth_labels.parquet").filter((pl.col("goal_no") == 51) & (pl.col("label_kind") == "role")
                                                                         & pl.col("preferred") & ~pl.col("holdout"))
        role_of = {}
        for a, v in gt.select("agent", "value").iter_rows():
            role_of.setdefault(a, set()).add(str(v).lower())
        ag = np.array(fa["agents"]); c = np.array(fa["c"]); nu = np.array(fa["nu"])
        hold = np.array([a in role_of for a in ag])
        isE = np.array([bool(role_of.get(a, set()) & set(H.ENFORCER_ROLES)) for a in ag])

        def pdiff(v, e, R=5000):
            v, e = v[hold], e[hold]
            obs = v[e].mean() - v[~e].mean()
            nul = np.array([(lambda q: v[q].mean() - v[~q].mean())(rng.permutation(e)) for _ in range(R)])
            return {"diff": float(obs), "p_greater": float((1 + np.sum(nul >= obs)) / (R + 1)), "n_E": int(e.sum()), "n_other": int((~e).sum())}
        summ["G51_enforcers"] = {"c_E_minus_other": pdiff(c, isE), "nuD_E_minus_other": pdiff(nu, isE)}
    summ["settings"] = {"sensor_C": "stance2 in {correct, decline}", "PC": PC, "RC": RC, "friction_outcome": "disagree_validated_agent",
                        "label": "round 1c, stance v2.1"}
    summ["seconds"] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "real_periods.json").write_text(jd(rows))
    (OUT / "real.json").write_text(jd(summ))
    print(jd({k: v for k, v in summ.items()}))


if __name__ == "__main__":
    {"synth": synth, "real": real}.get(sys.argv[1], lambda: None)()


# ============================================================================================ synthetic, part 2
# Added 2026-10-04 after the first synthetic pass and before any real-data statistic: the pre-registered RE-bootstrap
# inference for P2 had size 0.73 (rare binary outcome, degenerate cluster bootstraps), so P2's inference is re-sized
# here with the label-noise null (NG-pooled z), and P1's meta-analytic power is measured over all P1-scorable periods.
def _sim_D(p, rng, extra=None):
    ag, spk, tgt = codes(p)
    a_f, b_f = rng.normal(0, 0.6, len(ag)), rng.normal(0, 0.6, len(ag))
    base_eta = a_f[spk] + b_f[tgt]
    pi, r = rng.uniform(*SN.PI_RANGE), rng.uniform(*SN.R_RANGE)
    dbar = float(p["D"].mean())
    sh = SN._shift(base_eta, pi * dbar / r)
    eta = base_eta + (0 if extra is None else extra)
    dstar = rng.random(len(eta)) < 1 / (1 + np.exp(-(eta + sh)))
    gg = p["g"].to_numpy()
    f = np.clip(SN.implied_fpr(dbar, pi, r) * gg / gg.mean(), 0, 0.5)
    return np.where(dstar, rng.random(len(eta)) < r, rng.random(len(eta)) < f).astype(float)


def synth_p2ng_rep(args):
    periods, delta, seed, R = args
    rng = np.random.default_rng(seed)
    num = den = 0.0
    for g in periods:
        p = pairs().filter(pl.col("goal_no") == g)
        ua, ainv = np.unique(p["A_message_id"].to_numpy(), return_inverse=True)
        tc = rng.random(len(ua)) < 0.10
        fpr = RC * 0.10 * (1 - PC) / PC / 0.90
        x = np.where(tc, rng.random(len(ua)) < RC, rng.random(len(ua)) < fpr)[ainv].astype(float)
        if x.sum() < 20:
            continue
        y = _sim_D(p, rng, extra=delta * tc[ainv])
        w = p["p_reply"].to_numpy().astype(float)
        _, g1 = np.unique(p["b_agent"].to_numpy(), return_inverse=True)
        _, g2 = np.unique(p["a_agent"].to_numpy(), return_inverse=True)
        gam = gamma_D(y, x, w, g1, g2)[0]
        ag, spk, tgt = codes(p)
        N = SN.NoiseNull([spk, tgt], y, p["g"].to_numpy(), p["block"].to_numpy())
        nul = np.array([gamma_D(N.draw(rng), x, w, g1, g2)[0] for _ in range(R)])
        sd = np.nanstd(nul)
        if sd > 0 and np.isfinite(gam):
            num += (gam - np.nanmean(nul)) / sd ** 2
            den += 1 / sd ** 2
    z = num / np.sqrt(den) if den > 0 else np.nan
    return delta, z


def synth_p1meta_rep(args):
    periods, beta, seed = args
    rng = np.random.default_rng(seed)
    rhos, ns = [], []
    rates_all = sender_rates_v2()
    for g in periods:
        p = pairs().filter(pl.col("goal_no") == g)
        rates = rates_all.filter(pl.col("goal_no") == g)
        ag, spk, tgt = codes(p)
        npar = dict(zip(rates["agent"].to_list(), rates["n_par"].to_list()))
        lc = rng.normal(np.log(0.1 / 0.9), 0.6, len(ag))
        n = np.array([npar.get(a, 0) for a in ag])
        nt = rng.binomial(n, 1 / (1 + np.exp(-lc)))
        fpr = RC * 0.10 * (1 - PC) / PC / 0.90
        cobs = (rng.binomial(nt, RC) + rng.binomial(n - nt, fpr)) / np.maximum(n, 1)
        z = (lc - lc.mean()) / lc.std()
        y = _sim_D(p, rng, extra=beta * z[tgt])
        fa = friction_agent_v2(p, pl.DataFrame({"agent": ag, "n_par": n, "c": cobs}), rng, R=20, D=y)
        if fa.get("scorable"):
            rhos.append(fa["rho"]); ns.append(fa["n_agents"])
    re = L.fisher_z_meta(rhos, ns)
    return beta, re.get("rho"), re.get("p_two"), re.get("k")


def synth2():
    t0 = time.time()
    out = json.loads((OUT / "synth.json").read_text())
    pp = pairs()
    periods2 = out["P2_periods"]
    jobs = [(periods2, d, SEED + 101 * k + int(10 * d), 80) for d in (0.0, 1.0) for k in range(40)]
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(synth_p2ng_rep, jobs, chunksize=5))
    df = pl.DataFrame(res, schema=["delta", "z"], orient="row")
    out["P2_NGpooled"] = df.group_by("delta").agg(pl.len().alias("reps"), (pl.col("z") > 1.645).mean().alias("rej_greater_0.05"),
                                                  (pl.col("z").abs() > 1.96).mean().alias("rej_two_0.05"), pl.col("z").mean()).sort("delta").to_dicts()
    print("P2 NG", out["P2_NGpooled"], flush=True)
    rates = sender_rates_v2()
    p1per = []
    for g in sorted(pp["goal_no"].unique().to_list()):
        p = pp.filter(pl.col("goal_no") == g)
        if p.height < 50:
            continue
        ag, spk, tgt = codes(p)
        nrecv, nsent = np.bincount(tgt, minlength=len(ag)), np.bincount(spk, minlength=len(ag))
        rr = dict(zip(rates.filter(pl.col("goal_no") == g)["agent"].to_list(), rates.filter(pl.col("goal_no") == g)["n_par"].to_list()))
        k = sum(1 for i, a in enumerate(ag) if nrecv[i] >= MIN_RECV and nsent[i] >= MIN_SENT and rr.get(a, 0) >= MIN_SENT)
        if k >= 6:
            p1per.append(int(g))
    jobs = [(p1per, b, SEED + 211 * k + int(10 * b)) for b in (0.0, 0.3, 0.6) for k in range(40)]
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(synth_p1meta_rep, jobs, chunksize=5))
    df1 = pl.DataFrame(res, schema=["beta", "rho", "p", "k"], orient="row")
    out["P1_meta"] = df1.group_by("beta").agg(pl.len().alias("reps"), ((pl.col("p") < 0.10) & (pl.col("rho") > 0)).mean().alias("power_one_sided_0.05"),
                                              (pl.col("p") < 0.05).mean().alias("rej_two_0.05"), pl.col("rho").mean(), pl.col("k").mean()).sort("beta").to_dicts()
    out["P1_meta_periods"] = p1per
    print("P1 meta", out["P1_meta"], flush=True)
    out["seconds_part2"] = round(time.time() - t0, 1)
    (OUT / "synth.json").write_text(jd(out))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "synth2":
    synth2()
