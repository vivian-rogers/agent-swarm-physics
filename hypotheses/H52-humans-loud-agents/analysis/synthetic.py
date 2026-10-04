"""H52 synthetic validation (axis F): agents on the real read-out schedule with a planted authority premium.

Skeleton: the real (message, recipient) rows of a period (receiving calls, read-out ages, naming, recipient state,
room size, length, k_new, pre15, statement availability). Only outcomes and vectors are synthetic.

World (d = 32):
- topic T(day, 2-h block); recipient centre c(j, day) = unit(T(day) + z_j + 0.5 z_jd);
- pre statements per receiving call: unit(c + 0.9 noise), as many as the real call had (<= 8);
- message vector u = unit(beta_cls T + (1 - beta_cls) r): agents beta 0.6, humans 0.35 (more novel), bots
  unit(0.7 template + 0.3 r);
- post statement per call: Q = unit(c + 0.9 eta + kappa sum_i g_i unit(P_perp u_i)), with salience-gated coupling
  g_i = (1 + 3 named)(exp(-age/600))(1 + 0.5 idle) sqrt(4 / (n_recv + 3)) (0.3 + nov_i) + pi_con [human];
- reply (eligible rows): Bernoulli(sigmoid(-2.5 + 1.6 named - 0.4 log1p(age/60) + (nov - 0.7) + 0.4 idle
  - 0.3 log n_recv + rho [human]));
- activity: y30 = clip(round(10 + 0.8 pre15 - 4 idle + day + recipient + 0.3 k_new + alpha [human]
  + alpha_bot [bot & named] + N(0, 3)), 0, 30);
- stance (replies): 0.45 + 0.1 named - 0.15 (nov - 0.7) + 0.05 idle + sigma_st [human] + N(0, 0.3).
Labels: `real` (the period's real human / bot rows) or `confounded` (agent messages relabelled "human" with
probability rising with naming, recipient idleness, length and read-out age; generated more novel).
Truth for content: common-random-number counterfactual (same noise, pi_con = 0) over the analysed human rows.

Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/synthetic.py [--reps 12] [--B 200]
Writes data/processed/H52-humans-loud-agents/synthetic/{replicates.parquet, summary.json}.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402
import estimate as E  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

D = 32
SKEL_COLS = ["item", "msg", "turn_id", "recv", "cls", "named", "age_s", "idle", "n_recv", "len", "k_new", "pre15",
             "day_idx", "n_pre", "n_chat_post", "y30_ok", "kickoff", "uncertain", "tc", "since_act"]
SCEN = {
    "S0": dict(pi_con=0.0, rho=0.0, alpha=0.0, alpha_bot=0.0, sigma_st=0.0),
    "S1": dict(pi_con=0.9, rho=0.6, alpha=1.0, alpha_bot=1.0, sigma_st=0.10),
}
KAPPA = 0.12


def load_skeleton(period: str, max_rows: int, rng) -> pl.DataFrame:
    R = pl.read_parquet(L.OUT / period / "rows.parquet")
    avail = R["chi"].is_not_null()          # statement availability only (not the value)
    R = R.with_columns(avail.alias("con_ok")).select(*SKEL_COLS, "con_ok").filter(~pl.col("kickoff"))
    if R.height > max_rows:
        calls_nonag = set(R.filter(pl.col("cls") != 0)["turn_id"].to_list())
        other = np.array(sorted(set(R["turn_id"].to_list()) - calls_nonag))
        sizes = R.group_by("turn_id").len()
        keep = list(calls_nonag)
        n_now = R.filter(pl.col("turn_id").is_in(keep)).height
        rng.shuffle(other)
        sz = dict(zip(sizes["turn_id"].to_list(), sizes["len"].to_list()))
        for t in other:
            if n_now >= max_rows:
                break
            keep.append(int(t)); n_now += sz[int(t)]
        R = R.filter(pl.col("turn_id").is_in(keep))
    return R.sort("item")


def relabel(R: pl.DataFrame, mode: str, rng, target_share: float) -> np.ndarray:
    cls = R["cls"].to_numpy().copy()
    if mode == "real":
        return cls
    cls[cls == 1] = 0          # confounded: real humans become agents; synthetic humans drawn from agent messages
    ag = R.filter(pl.col("cls") != 2)
    g = ag.group_by("msg").agg(pl.col("named").any().alias("nm"), pl.col("idle").mean().alias("idl"),
                               pl.col("len").first().alias("ln"), pl.col("age_s").log1p().mean().alias("ag"))
    z = lambda x: (x - x.mean()) / (x.std() + 1e-9)  # noqa: E731
    lin = 1.5 * g["nm"].cast(pl.Float64).to_numpy() + 1.2 * g["idl"].to_numpy() + 0.5 * z(np.log1p(g["ln"].to_numpy())) \
        + 0.4 * z(g["ag"].to_numpy())
    # calibrate intercept to the target share of messages
    lo, hi = -15.0, 5.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if (1 / (1 + np.exp(-(mid + lin)))).mean() > target_share:
            hi = mid
        else:
            lo = mid
    p = 1 / (1 + np.exp(-(mid + lin)))
    hm = set(g["msg"].to_numpy()[rng.random(len(p)) < p].tolist())
    is_h = np.isin(R["msg"].to_numpy(), list(hm)) & (R["cls"].to_numpy() != 2)
    cls[is_h] = 1
    return cls


def simulate(R: pl.DataFrame, cls: np.ndarray, sc: dict, rng, B: int, placebo_draws: int) -> dict:
    n = R.height
    day = R["day_idx"].to_numpy(); recv = R["recv"].to_numpy().astype(int)
    named = R["named"].to_numpy().astype(bool); age = R["age_s"].to_numpy().astype(float)
    idle = R["idle"].to_numpy().astype(bool); nrecv = R["n_recv"].to_numpy().astype(float)
    tc = R["tc"].to_numpy(); msg = R["msg"].to_numpy().astype(np.int64)
    blk = ((tc - tc.min()) // 7200).astype(int)
    # topics, centres
    keys_t = {}
    def topic(dd, bb):
        k = (int(dd), int(bb))
        if k not in keys_t:
            keys_t[k] = L.unit(rng.normal(size=D))
        return keys_t[k]
    agents = np.unique(recv)
    zj = {int(a): rng.normal(size=D) for a in agents}
    days = np.unique(day)
    zjd = {(int(a), int(dd)): rng.normal(size=D) * 0.5 for a in agents for dd in days}
    Tday = {int(dd): L.unit(rng.normal(size=D)) for dd in days}
    # message vectors
    template = L.unit(rng.normal(size=D))
    umsg = {}
    mcls = {}
    for m, c, dd, bb in zip(msg, cls, day, blk):
        if m in umsg:
            continue
        r = L.unit(rng.normal(size=D))
        T = L.unit(Tday[int(dd)] + 0.7 * topic(dd, bb))
        if c == 2:
            umsg[m] = L.unit(0.7 * template + 0.3 * r)
        else:
            beta = 0.35 if c == 1 else 0.6
            umsg[m] = L.unit(beta * T + (1 - beta) * r)
        mcls[m] = c
    # calls: pre statements and noise
    calls, call_idx = np.unique(R["turn_id"].to_numpy(), return_inverse=True)
    nc = len(calls)
    first = np.zeros(nc, int); first[call_idx[::-1]] = np.arange(n)[::-1]
    npre = R["n_pre"].to_numpy().astype(int)
    kpre = np.where(npre[first] > 0, np.clip(npre[first] + 2, 1, L.K_BASIS), 0)
    cen = np.stack([L.unit(Tday[int(day[i])] + zj[int(recv[i])] + zjd[(int(recv[i]), int(day[i]))]) for i in first])
    Vpre = np.zeros((nc, L.K_BASIS, D), np.float32)
    for k in range(L.K_BASIS):
        Vpre[:, k] = np.where((k < kpre)[:, None], L.unit(cen + 0.9 * rng.normal(size=(nc, D))), 0)
    eta = rng.normal(size=(nc, D))
    # replies quote the addressee: an agent (or bot-free) message naming a recipient carries 0.6 x that recipient's
    # most recent pre statement (regression-to-the-mean trap for pre/post designs; humans quote half as much)
    quoted = set()
    for i in np.flatnonzero(named & (cls != 2)):
        m = msg[i]
        if m in quoted or kpre[call_idx[i]] == 0:
            continue
        lastv = Vpre[call_idx[i], kpre[call_idx[i]] - 1]
        w = 0.6 if cls[i] == 0 else 0.3
        umsg[m] = L.unit(umsg[m] + w * lastv)
        quoted.add(m)
    U = np.stack([umsg[m] for m in msg]).astype(np.float32)
    # perp of messages w.r.t. call basis -> novelty
    Bas = L.orth_basis_batched(Vpre[call_idx])
    uh, nrm = L.perp(U.astype(np.float64), Bas)
    nov = np.where(kpre[call_idx] > 0, nrm, np.nan)
    sal = (1 + 3 * named) * np.exp(-age / 600) * (1 + 0.5 * idle) * np.sqrt(4 / (nrecv + 3)) * (0.3 + np.nan_to_num(nov, nan=1.0))

    def post_Q(pi):
        g = sal + pi * (cls == 1)
        push = np.zeros((nc, D))
        np.add.at(push, call_idx, (KAPPA * g)[:, None] * uh)
        return L.unit(cen + 0.9 * eta + push)

    # assemble V: pre statements then one post statement per call
    Vall = np.concatenate([Vpre.reshape(-1, D), np.zeros((nc, D), np.float32)])
    base_q = nc * L.K_BASIS
    bidx = np.where(np.arange(L.K_BASIS)[None, :] >= (L.K_BASIS - kpre[call_idx])[:, None],
                    call_idx[:, None] * L.K_BASIS + (np.arange(L.K_BASIS)[None, :] - (L.K_BASIS - kpre[call_idx])[:, None]), -1)
    # pre statements were stored at k < kpre; map basis slots (right-aligned) onto them
    pmask = (bidx >= 0) & (np.arange(L.K_BASIS)[None, :] >= L.K_BASIS - L.K_PRE)
    con_ok = R["con_ok"].to_numpy()
    qidx = np.full((n, L.K_POST), -1, np.int64)
    qidx[con_ok, 0] = base_q + call_idx[con_ok]
    # placebos: same class, other day
    pool = {}
    for c in (0, 1, 2):
        ms = np.array([m for m in umsg if mcls[m] == c], np.int64)
        if len(ms):
            dmap = dict(zip(msg, day))
            pool[c] = (ms, np.array([dmap[m] for m in ms]))
    plx = L.draw_placebos(cls, day, recv, pool, rng)
    Up = np.full(plx.shape + (D,), np.nan, np.float32)
    okp = plx >= 0
    Up[okp] = np.stack([umsg[m] for m in plx[okp]])
    out = {}
    chis = {}
    for tag, pi in (("obs", sc["pi_con"]), ("cf", 0.0)):
        Vall[base_q:] = post_Q(pi)
        r = L.content_rows(Vall, bidx, pmask, qidx, U, Up, call_id=call_idx)
        chis[tag] = r["chi"]; chis[tag + "_dd"] = r["chi_dd"]; chis[tag + "_jd"] = r["chi_jd"]
    chi = chis["obs"]
    # reply, activity, stance
    elig = R["n_chat_post"].to_numpy() >= 1
    nv = np.nan_to_num(nov, nan=0.7)
    lin = -2.5 + 1.6 * named - 0.4 * np.log1p(age / 60) + (nv - 0.7) + 0.4 * idle - 0.3 * np.log(nrecv)
    p1 = 1 / (1 + np.exp(-(lin + sc["rho"] * (cls == 1))))
    p0 = 1 / (1 + np.exp(-lin))
    rep = (rng.random(n) < p1)
    rep_f = np.where(elig, rep.astype(float), np.nan)
    deff = {int(dd): rng.normal(0, 2) for dd in days}
    reff = {int(a): rng.normal(0, 2) for a in agents}
    lam = 10 + 0.8 * R["pre15"].to_numpy() - 4 * idle + np.array([deff[int(x)] for x in day]) + \
        np.array([reff[int(x)] for x in recv]) + 0.3 * R["k_new"].to_numpy() + sc["alpha"] * (cls == 1) + \
        sc["alpha_bot"] * ((cls == 2) & named)
    y30 = np.clip(np.round(lam + rng.normal(0, 3, n)), 0, 30)
    st = np.clip(0.45 + 0.1 * named - 0.15 * (nv - 0.7) + 0.05 * idle + sc["sigma_st"] * (cls == 1) + rng.normal(0, 0.3, n), -1, 1)
    df = R.with_columns(pl.Series("cls", cls.astype(np.int8)), pl.Series("chi", chi).fill_nan(None),
                        pl.Series("chi_dd", chis["obs_dd"]).fill_nan(None), pl.Series("chi_jd", chis["obs_jd"]).fill_nan(None),
                        pl.Series("nov", nov).fill_nan(None), pl.Series("rep", rep), pl.Series("y30", y30),
                        pl.Series("st", st))
    d = E.prepare(df)
    res = E.analyze(d, B=B, placebo_draws=placebo_draws, regression=True)
    d2 = E.prepare(df, con_col="chi_dd")
    res["con_dd"] = E.analyze(d2, B=B, placebo_draws=placebo_draws, regression=True, outcomes=("con",))["con"]
    d3 = E.prepare(df, con_col="chi_jd")
    res["con_jd"] = E.analyze(d3, B=B, placebo_draws=placebo_draws, regression=True, outcomes=("con",))["con"]
    # truths over the analysed rows
    h = (cls == 1)
    mask_con = h & np.isfinite(chi) & np.isfinite(chis["cf"])
    cdd, cdd0 = chis["obs_dd"], chis["cf_dd"]
    mdd = h & np.isfinite(cdd) & np.isfinite(cdd0)
    out["truth"] = dict(con=float(np.mean(chi[mask_con] - chis["cf"][mask_con])) if mask_con.any() else np.nan,
                        con_dd=float(np.mean(cdd[mdd] - cdd0[mdd])) if mdd.any() else np.nan,
                        con_jd=float(np.nanmean(chis["obs_jd"][mdd] - chis["cf_jd"][mdd])) if mdd.any() else np.nan,
                        rep=float(np.mean((p1 - p0)[h & elig])) if (h & elig).any() else np.nan,
                        act=sc["alpha"], st=sc["sigma_st"], act_bot_named=sc["alpha_bot"])
    out["res"] = res
    return out


def flatten(rep_out: dict, meta: dict) -> list[dict]:
    rows = []
    res = rep_out["res"]
    for oc in E.OUTCOMES + ("con_dd", "con_jd"):
        r = res.get(oc, {})
        for c in ("human", "bot"):
            if c not in r:
                continue
            for sub in ("all", "named"):
                a = r[c].get(sub, {})
                reg = r[c].get("regression", {}).get(f"{c}_{'named' if sub == 'named' else 'unnamed'}", {}) if sub == "named" else {}
                truth = rep_out["truth"][oc] if c == "human" else (rep_out["truth"]["act_bot_named"] if (oc == "act" and sub == "named") else 0.0)
                if c == "bot" and oc != "act":
                    truth = 0.0
                if c == "bot" and oc == "act" and sub == "all":
                    truth = np.nan
                pc = r[c].get("placebo_class", {}) if sub == "all" else {}
                abc = r[c].get(sub + "_bc", {})
                acl = r[c].get("all_clean", {}) if sub == "all" else {}
                rows.append(dict(**meta, outcome=oc, cls=c, subset=sub, att=a.get("att"), lo=a.get("ci", [np.nan] * 2)[0],
                                 att_bc=abc.get("att"), lo_bc=abc.get("ci", [np.nan] * 2)[0], hi_bc=abc.get("ci", [np.nan] * 2)[1],
                                 att_clean=acl.get("att"),
                                 hi=a.get("ci", [np.nan] * 2)[1], se=a.get("se"), naive=a.get("naive"),
                                 naive_se=a.get("naive_se"), matched=a.get("matched_share"), n_t=a.get("n_t"),
                                 reg=reg.get("coef"), truth=truth,
                                 pc_lo=pc.get("null_band", [np.nan] * 2)[0], pc_hi=pc.get("null_band", [np.nan] * 2)[1]))
    return rows


def summarize(df: pl.DataFrame) -> dict:
    out = {}
    df = df.with_columns((pl.col("att") - pl.col("truth")).alias("err"), (pl.col("naive") - pl.col("truth")).alias("nerr"),
                         ((pl.col("lo") <= pl.col("truth")) & (pl.col("hi") >= pl.col("truth"))).alias("cover"),
                         ((pl.col("lo") > 0) | (pl.col("hi") < 0)).alias("reject0"),
                         ((pl.col("naive") - pl.col("truth")).abs() > 2 * pl.col("naive_se")).alias("naive_biased"),
                         ((pl.col("att") < pl.col("pc_lo")) | (pl.col("att") > pl.col("pc_hi"))).alias("pc_reject"))
    g = df.group_by("skeleton", "labels", "scenario", "outcome", "cls", "subset").agg(
        pl.len().alias("reps"), pl.col("truth").mean(), pl.col("att").mean().alias("att_mean"),
        pl.col("err").mean().alias("bias"), (pl.col("err") ** 2).mean().sqrt().alias("rmse_cem"),
        (pl.col("att_bc") - pl.col("truth")).mean().alias("bias_bc"),
        (pl.col("att_clean") - pl.col("truth")).mean().alias("bias_clean"),
        ((pl.col("att_clean") - pl.col("truth")) ** 2).mean().sqrt().alias("rmse_clean"),
        ((pl.col("att_bc") - pl.col("truth")) ** 2).mean().sqrt().alias("rmse_bc"),
        ((pl.col("lo_bc") <= pl.col("truth")) & (pl.col("hi_bc") >= pl.col("truth"))).mean().alias("coverage_bc"),
        ((pl.col("lo_bc") > 0) | (pl.col("hi_bc") < 0)).mean().alias("reject0_bc"),
        ((pl.col("reg") - pl.col("truth")) ** 2).mean().sqrt().alias("rmse_reg"),
        (pl.col("reg") - pl.col("truth")).mean().alias("bias_reg"),
        pl.col("nerr").mean().alias("naive_bias"), pl.col("cover").mean().alias("coverage"),
        pl.col("reject0").mean().alias("reject0"), pl.col("naive_biased").mean().alias("naive_biased_2se"),
        pl.col("pc_reject").mean().alias("placebo_class_reject"), pl.col("matched").mean().alias("matched_share"),
        pl.col("n_t").mean().alias("n_treated"))
    out["table"] = g.sort("skeleton", "labels", "scenario", "outcome", "cls", "subset").to_dicts()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=12)
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--skeletons", default="G51,G04")
    ap.add_argument("--max-rows", type=int, default=60000)
    ap.add_argument("--placebo-draws", type=int, default=100)
    a = ap.parse_args()
    outdir = L.OUT / "synthetic"
    outdir.mkdir(parents=True, exist_ok=True)
    allrows = []
    t0 = time.time()
    for sk in a.skeletons.split(","):
        rng0 = np.random.default_rng(L.SEED)
        R = load_skeleton(sk, a.max_rows, rng0)
        share = 0.03 if sk == "G51" else 0.25
        for labels in ("confounded", "real"):
            for scn, sc in SCEN.items():
                for rep in range(a.reps):
                    rng = np.random.default_rng([L.SEED, hash((sk, labels, scn)) % 10_000, rep])
                    cls = relabel(R, labels, rng, share)
                    o = simulate(R, cls, sc, rng, a.B, a.placebo_draws)
                    allrows += flatten(o, dict(skeleton=sk, labels=labels, scenario=scn, rep=rep))
                    print(f"{sk} {labels} {scn} rep {rep} done ({time.time() - t0:.0f} s)", flush=True)
                pl.DataFrame(allrows).write_parquet(outdir / "replicates.parquet")
    df = pl.DataFrame(allrows)
    df.write_parquet(outdir / "replicates.parquet")
    S = summarize(df)
    S["params"] = dict(reps=a.reps, B=a.B, max_rows=a.max_rows, kappa=KAPPA, scenarios=SCEN)
    L.jdump(S, outdir / "summary.json")
    L.write_provenance(outdir, "hypotheses/H52-humans-loud-agents/analysis/synthetic.py",
                       ["H52 rows.parquet skeleton columns (no outcomes)"], S["params"])
    print("done", time.time() - t0)


if __name__ == "__main__":
    main()
