"""H55 synthetic validation (axis F) on REAL structures with MEASURED sensor noise. No real outcomes are used:
stance labels, correction status and loop/blocked outcomes are all simulated; only the reply graph, message counts,
loop at-risk steps and directed-read counts come from the data.

S1 friction: real DQ2 reply graphs (#51, #19, #38); ordered-logit stance with speaker/target fields; enforcer
   propensity e_j; corrections observed through the Jev sensor (recall 0.107, false-positive rate 0.0012, precision ~0.93
   at base rate 0.13); observed stance through a confusion matrix matching DQ2 (opposes precision ~0.08).
   Scenarios: null0, null_style (enforcers argumentative + reciprocity), agent-level friction (gamma), message-level
   friction (delta).
S2 immune (loops) / S3 immune (blocked): real at-risk steps and directed-read counts; per-read true correction status
   (rate 0.13; targeted at escape-prone agents under the null), the same sensor; escape logit with agent frailty, age,
   directed-read effect beta_D, correction effect beta_C. Also a perfect-sensor variant.
S4 swarm: why a cross-period correlation cannot identify immunity when corrections are induced by loops.
  uv run python hypotheses/H55-norm-enforcer-immunity/analysis/synthetic.py [--reps 60]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h55lib as L  # noqa: E402
from h55lib import H  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

BASE, REC, FPR = 0.13, 0.107, 0.0012
# P(observed class | true class), rows true (-,0,+), cols observed (-,0,+); gives opposes precision ~0.08 at 0.5% true -
CONF = np.array([[0.60, 0.30, 0.10], [0.05, 0.60, 0.35], [0.01, 0.20, 0.79]])
SD = H.OUT / "synthetic"
SD.mkdir(exist_ok=True)


def sensor(true: np.ndarray, rng, perfect=False) -> np.ndarray:
    if perfect:
        return true.copy()
    u = rng.random(len(true))
    return np.where(true, u < REC, u < FPR)


# ------------------------------------------------------------------------------------------------------------- S1
def s1_structures():
    pp = L.pair_table()
    msgs = pl.read_parquet(H.OUT / "messages.parquet")
    rates = L.sender_rates(msgs)
    out = {}
    for g in (51, 19, 38):
        p = pp.filter(pl.col("goal_no") == g).select("A_message_id", "b_agent", "a_agent", "pt_date", "p_reply")
        r = rates.filter(pl.col("goal_no") == g).select("agent", "n_par")
        out[g] = (p, r)
    return out


def s1_rep(args):
    g, p, r, scen, val, seed = args
    rng = np.random.default_rng(seed)
    ag = np.unique(np.r_[p["b_agent"].to_numpy(), p["a_agent"].to_numpy(), r["agent"].to_numpy()])
    N = len(ag)
    idx = {a: k for k, a in enumerate(ag)}
    a_f = rng.normal(0, 0.5, N)
    b_f = rng.normal(0, 0.5, N)
    loge = rng.normal(0, 0.6, N)
    if scen == "null_style":
        loge = -0.6 * (a_f / 0.5) * 0.6 + np.sqrt(1 - 0.36) * loge     # enforcers less agreeable as repliers
        b_f = b_f + 0.5 * a_f                                         # reciprocity: treated as they treat others
    e = np.exp(loge)
    pc = np.clip(BASE * e / e.mean(), 0, 0.9)
    ez = (loge - loge.mean()) / loge.std()
    gamma = val if scen == "agent" else 0.0
    delta = val if scen == "msg" else 0.0
    # sender rates (c_j observed)
    rr = r.with_columns(pl.Series("k", [idx[a] for a in r["agent"].to_list()]))
    ntrue = rng.binomial(rr["n_par"].to_numpy(), pc[rr["k"].to_numpy()])
    nobs = rng.binomial(ntrue, REC) + rng.binomial(rr["n_par"].to_numpy() - ntrue, FPR)
    rates = pl.DataFrame({"agent": rr["agent"], "n_par": rr["n_par"], "n_corr": nobs}).with_columns((pl.col("n_corr") / pl.col("n_par")).alias("c"))
    # A messages' true correction status (one draw per A message)
    uA, invA = np.unique(p["A_message_id"].to_numpy(), return_inverse=True)
    tgtA = np.zeros(len(uA), int)
    tgtA[invA] = [idx[a] for a in p["a_agent"].to_numpy()]
    Atrue = rng.random(len(uA)) < pc[tgtA]
    Aobs = sensor(Atrue, rng)
    spk = np.array([idx[a] for a in p["b_agent"].to_numpy()])
    tgt = np.array([idx[a] for a in p["a_agent"].to_numpy()])
    eta = 1.0 + a_f[spk] + b_f[tgt] - gamma * ez[tgt] - delta * Atrue[invA] + rng.logistic(size=len(spk))
    true_cls = np.where(eta < -3.0, 0, np.where(eta < 1.2, 1, 2))
    u = rng.random(len(spk))
    cum = np.cumsum(CONF[true_cls], 1)
    obs = (u[:, None] > cum).sum(1)
    y = obs - 1
    s = y * rng.uniform(0.6, 1.0, len(y))
    sim = p.with_columns(pl.Series("y", y.astype(np.int8)), pl.Series("s", s), pl.Series("A_corr", Aobs[invA]))
    fa = L.friction_agent(sim, rates, R=999, rng=rng)
    fm = L.friction_message(sim, B=300, rng=rng, min_treated=5)
    return {"g": g, "scen": scen, "val": val, "rho": fa.get("rho"), "p": fa.get("p"), "rho_partial": fa.get("rho_partial"),
            "p_partial": fa.get("p_partial"), "gamma": fm.get("gamma"), "p_msg": fm.get("p"), "n_trt": fm.get("n_treated"),
            "n_agents": fa.get("n_agents"), "true_neg": float((true_cls == 0).mean()), "obs_neg": float((y == -1).mean())}


def run_s1(reps):
    st = s1_structures()
    jobs, seed = [], 1000
    scen = [("null0", 0.0), ("null_style", 0.0), ("agent", 0.3), ("agent", 0.6), ("msg", 0.5), ("msg", 1.0)]
    for g, (p, r) in st.items():
        for sc, v in scen:
            for k in range(reps):
                seed += 1
                jobs.append((g, p, r, sc, v, seed))
    t0 = time.time()
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(s1_rep, jobs, chunksize=4))
    df = pl.DataFrame(res)
    df.write_parquet(SD / "s1_reps.parquet")
    summ = df.group_by("g", "scen", "val").agg(
        pl.len().alias("reps"), (pl.col("p") < 0.05).mean().alias("rej_P1"), pl.col("rho").mean().alias("rho_mean"),
        (pl.col("p_partial") < 0.05).mean().alias("rej_P1b"), pl.col("rho_partial").mean().alias("rhop_mean"),
        ((pl.col("p_msg") < 0.05) & (pl.col("gamma") < 0)).mean().alias("rej_P2_neg"),
        (pl.col("p_msg") < 0.05).mean().alias("rej_P2_any"), pl.col("gamma").mean().alias("gamma_mean"),
        pl.col("n_trt").mean().alias("n_trt"), pl.col("obs_neg").mean(), pl.col("true_neg").mean()).sort("g", "scen", "val")
    print(f"S1 done in {time.time() - t0:.0f}s")
    print(summ)
    return summ


# ---------------------------------------------------------------------------------------------------------- S2/S3
def step_structure(kind: str):
    if kind == "loop":
        st = pl.read_parquet(H.OUT / "loop_steps.parquet").filter((pl.col("version") == "restate") & pl.col("y").is_not_null())
        rd = pl.read_parquet(H.OUT / "reads_loop.parquet")
        vol = pl.read_parquet(H.OUT / "reads_loop_volume.parquet")
        s = L.steps_with_reads(st, rd, vol, "anchor_id")
    else:
        st = pl.read_parquet(H.OUT / "blocked_steps.parquet").filter(pl.col("y").is_not_null())
        st = st.with_columns((pl.col("t0").cast(pl.Int64).cast(pl.Utf8) + "_" + pl.col("agent").cast(pl.Utf8)).alias("win_id"))
        rd = pl.read_parquet(H.OUT / "reads_blocked.parquet")
        vol = pl.read_parquet(H.OUT / "reads_blocked_volume.parquet")
        s = L.steps_with_reads(st, rd.with_columns(pl.lit(None, pl.Float32).alias("novelty")), vol, "win_id")
    return s


def s2_rep(s: pl.DataFrame, beta_c: float, beta_d: float, perfect: bool, seed: int, conf_target: bool = True, base: float = BASE):
    rng = np.random.default_rng(seed)
    ags, ainv = np.unique(s["agent"].to_numpy(), return_inverse=True)
    alpha = rng.normal(np.log(0.27 / 0.73), 0.6, len(ags))
    az = (alpha - alpha.mean()) / alpha.std()
    ndir = s["n_dir"].to_numpy()
    pc = np.clip(base * (np.exp(0.5 * az[ainv]) if conf_target else 1.0), 0, 0.9)
    # per step: number of true corrections among directed reads; observed flags
    ntrue = rng.binomial(ndir, pc)
    nobs = (rng.binomial(ntrue, 1.0 if perfect else REC) + (0 if perfect else rng.binomial(ndir - ntrue, FPR)))
    k = s["k"].to_numpy()
    eta = alpha[ainv] - 0.3 * np.log(k) + beta_d * (ndir > 0) + beta_c * (ntrue > 0)
    y = (rng.random(len(k)) < 1 / (1 + np.exp(-eta))).astype(np.int8)
    sim = s.with_columns(pl.Series("y", y), pl.Series("n_trt", nobs),
                         pl.Series("treated", nobs > 0), pl.Series("control", (ndir > 0) & (nobs == 0)),
                         pl.col("first_kind").alias("kind_m"), pl.col("first_named").alias("named_m"), pl.col("first_len").alias("len_m"))
    r = L.immune_contrast(sim, rng=rng, B=300)
    a = L.address_contrast(sim, rng=rng, B=200) if beta_c == 0 and not perfect else {}
    return {"beta_c": beta_c, "beta_d": beta_d, "perfect": perfect, "delta": r.get("delta"), "p": r.get("p"),
            "n_treated": r.get("n_treated"), "n_matched": r.get("n_matched"), "addr_delta": a.get("delta"), "addr_p": a.get("p")}


def run_s2(kind: str, reps: int):
    s = step_structure(kind)
    r_obs = float(s.filter(pl.col("y").is_not_null())["n_trt"].sum() / max(s.filter(pl.col("y").is_not_null())["n_dir"].sum(), 1))
    base = max((r_obs - FPR) / (REC - FPR), 0.002)     # true correction rate among directed reads implied by the sensor
    print(f"{kind}: observed flag rate per directed read {r_obs:.4f} -> implied true correction rate {base:.3f}")
    out = []
    t0 = time.time()
    for perfect in (False, True):
        for bc in (0.0, 0.5, 1.0, 2.0):
            for bd in ((0.0, 0.4) if (bc == 0 and not perfect) else (0.4,)):
                for k in range(reps):
                    out.append(s2_rep(s, bc, bd, perfect, 5000 + k + int(bc * 1000) + int(bd * 100) + 7 * perfect, base=base))
    df = pl.DataFrame(out)
    df.write_parquet(SD / f"s2_{kind}_reps.parquet")
    summ = df.group_by("perfect", "beta_c", "beta_d").agg(
        pl.len().alias("reps"), (pl.col("delta").is_not_null()).mean().alias("scorable"),
        ((pl.col("p") < 0.05) & (pl.col("delta") > 0)).mean().alias("power_pos"), (pl.col("p") < 0.05).mean().alias("rej_any"),
        pl.col("delta").mean().alias("delta_mean"), pl.col("n_treated").mean(), pl.col("n_matched").mean(),
        (pl.col("addr_p") < 0.05).mean().alias("addr_rej"), pl.col("addr_delta").mean()).sort("perfect", "beta_c", "beta_d")
    print(f"S2 {kind} done in {time.time() - t0:.0f}s")
    summ = summ.with_columns(pl.lit(r_obs).alias("obs_flag_rate"), pl.lit(base).alias("implied_true_rate"))
    print(summ)
    return summ


# ------------------------------------------------------------------------------------------------------------- S4
def run_s4(reps=500):
    rng = np.random.default_rng(H.SEED + 4)
    res = {}
    for label, beta, induce in (("immune_no_induction", 1.0, 0.0), ("no_immune_induction", 0.0, 1.0), ("immune_and_induction", 1.0, 1.0)):
        rs = []
        for _ in range(reps):
            P = 25
            sticky = rng.normal(0, 1, P)                      # period loop stickiness (scaffold, task)
            enf = rng.normal(0, 1, P)                         # spontaneous enforcer strength
            S = enf + induce * sticky + rng.normal(0, 0.5, P)  # observed correction rate: spontaneous + induced by loops
            pi = 0.7 + 0.08 * sticky - 0.08 * beta * enf + rng.normal(0, 0.03, P)
            from scipy.stats import spearmanr
            rs.append(spearmanr(S, pi).statistic)
        rs = np.array(rs)
        res[label] = {"rho_mean": float(rs.mean()), "frac_rho_neg_sig": float(np.mean(rs < -0.34)), "frac_rho_pos": float(np.mean(rs > 0))}
    print("S4", res)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=60)
    ap.add_argument("--reps2", type=int, default=200)
    ap.add_argument("--only", default="s1,s2,s3,s4")
    a = ap.parse_args()
    out = {}
    if "s1" in a.only:
        out["S1"] = run_s1(a.reps).to_dicts()
    if "s2" in a.only:
        out["S2_loop"] = run_s2("loop", a.reps2).to_dicts()
    if "s3" in a.only:
        out["S3_blocked"] = run_s2("blocked", a.reps2).to_dicts()
    if "s4" in a.only:
        out["S4"] = run_s4()
    prev = json.loads((SD / "results.json").read_text()) if (SD / "results.json").exists() else {}
    prev.update(out)
    (SD / "results.json").write_text(json.dumps(prev, indent=1, default=str))
    H.write_prov("synthetic", "hypotheses/H55-norm-enforcer-immunity/analysis/synthetic.py",
                 ["reply_pairs (structure only)", "H55 loop_steps/blocked_steps/reads (structure only)"],
                 {"base": BASE, "recall": REC, "fpr": FPR, "confusion": CONF.tolist(), "reps": a.reps, "reps2": a.reps2})


if __name__ == "__main__":
    main()
