"""H45 synthetic validation (axis F): four agent classes on the real call schedules and room streams.

Classes: controller (set point on the room share), passive accumulation, scaffold-capped (15-call sliding window),
context competition (engagement falls with total context). Inputs taken from real non-holdout calls: the order of each
agent's cu receiving calls per day, new items, characters and other room events per call (-> calibrated room tokens),
which calls carry a measured prompt (P mask), and each agent's base context and own-content growth scale (medians).
Resets, talk calls, engagement, own content and P are simulated. The same estimators as the real data are applied.

Usage: uv run python hypotheses/H45-context-homeostasis/analysis/synthetic.py [--reps 20] [--units 38a,...]
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import polars as pl

import h45lib as L

CLASSES = ("controller", "passive", "scaffold", "competition")
PAR = {"sigma_g": 0.6, "h_vol": 0.025, "kappa_W": 2.0, "kappa_c": 3.0, "ceil": 1.2, "window": 15,
       "talk_rate": 0.045, "talk_k": 0.4, "kappa_t": 0.8, "beta": 0.6, "kappa_e": 1.0, "E1_rate": 0.35}


def real_inputs(c: pl.DataFrame, units: list[str]) -> tuple[pl.DataFrame, dict]:
    x = c.filter((pl.col("ctx_mode") == "cu") & pl.col("unit_id").cast(pl.Utf8).is_in(units)).sort("agent", "t_first")
    # agent scales: base context at j = 1 and own-content growth per call (from action-row agents; lab / global fallback)
    seg1 = x.filter((pl.col("ctx_pos") == 1) & pl.col("P").is_not_null())
    B = dict(seg1.group_by("agent").agg((pl.col("P") - pl.col("r")).median().alias("B")).iter_rows())
    d = (x.filter(pl.col("p_src").cast(pl.Utf8) == "act")
         .with_columns((pl.col("P") - pl.col("P").shift(1).over("seg") - pl.col("r")).alias("g"))
         .filter(pl.col("g").is_not_null() & (pl.col("ctx_pos") > 1)))
    G = dict(d.group_by("agent").agg(pl.col("g").median().clip(200, None).alias("g")).iter_rows())
    Bg = float(np.median(list(B.values()))) if B else 20000.0
    Gg = float(np.median(list(G.values()))) if G else 800.0
    agents = x["agent"].unique().to_list()
    scale = {a: (max(B.get(a, Bg), 3000.0), G.get(a, Gg)) for a in agents}
    return x, scale


def simulate(x: pl.DataFrame, scale: dict, cls: str, rng: np.random.Generator, par=PAR) -> pl.DataFrame:
    """Lockstep simulation over agent-day streams."""
    x = x.with_columns(pl.int_range(pl.len()).over("agent", "pt_date").alias("t_idx"))
    streams = x.select("agent", "pt_date").unique(maintain_order=True)
    sid = {k: i for i, k in enumerate(streams.iter_rows())}
    x = x.with_columns(pl.Series("sid", [sid[(a, d)] for a, d in zip(x["agent"].to_list(), x["pt_date"].to_list())]))
    S, T = len(sid), int(x["t_idx"].max()) + 1
    rr = np.zeros((S, T)); kk = np.zeros((S, T)); mask = np.zeros((S, T), bool)
    si, ti = x["sid"].to_numpy(), x["t_idx"].to_numpy()
    rr[si, ti] = x["r"].to_numpy(); kk[si, ti] = x["k_new"].to_numpy(); mask[si, ti] = True
    ag = streams["agent"].to_numpy()
    Bv = np.array([scale[a][0] for a in ag]); gv = np.array([scale[a][1] for a in ag])
    # agent mean inflow per call -> controller target (passive share at j = 25)
    lam_a = x.group_by("agent").agg(pl.col("r").mean().alias("l"))
    lmap = dict(lam_a.iter_rows())
    lv = np.array([max(lmap[a], 1.0) for a in ag])
    s_star = lv * 25 / (Bv + (gv + lv) * 25)
    Pbar = Bv + (gv + lv) * 20
    j = np.zeros(S, int); R = np.zeros(S); W = np.zeros(S); s_prev = np.zeros(S)
    win_r = np.zeros((S, par["window"])); win_g = np.zeros((S, par["window"]))
    out = {k: np.full((S, T), np.nan) for k in ("j", "R", "W", "talk", "seg", "openf", "openv")}
    segc = np.zeros(S, int); nxt_forced = np.zeros(S, bool); nxt_vol = np.zeros(S, bool)
    base_logit = np.log(par["talk_rate"] / (1 - par["talk_rate"]))
    for t in range(T):
        m = mask[:, t]
        new = m & ((j == 0) | nxt_forced | nxt_vol)
        openf = new & nxt_forced; openv = new & nxt_vol
        j = np.where(new, 1, np.where(m, j + 1, j))
        segc = np.where(new, segc + 1, segc)
        W = np.where(new, Bv * rng.lognormal(0, 0.15, S), W)
        R = np.where(new, 0.0, R)
        win_r[new] = 0; win_g[new] = 0
        noise = rng.lognormal(-par["sigma_g"] ** 2 / 2, par["sigma_g"], S)
        if cls == "controller":
            g = gv * np.exp(np.clip(par["kappa_W"] * (s_prev - s_star) / s_star, -3, 3)) * noise
        else:
            g = gv * noise
        g = np.where(new, 0.0, g)
        if cls == "scaffold":
            win_r = np.roll(win_r, 1, axis=1); win_g = np.roll(win_g, 1, axis=1)
            win_r[:, 0] = np.where(m, rr[:, t], 0); win_g[:, 0] = np.where(m, g, 0)
            Rn = win_r.sum(1); Wn = np.where(new, W, (Bv + win_g.sum(1)))
            R = np.where(m, Rn, R); W = np.where(m, np.where(new, W, Wn), W)
        else:
            R = np.where(m, R + rr[:, t], R); W = np.where(m, W + g, W)
        P = R + W
        s = R / P
        # talk
        if cls == "controller":
            term = par["kappa_t"] * np.clip((s_star - s) / s_star, -2, 2)
        elif cls == "competition":
            term = -par["kappa_t"] * np.log(P / Pbar)
        else:
            term = 0.0
        pt = 1 / (1 + np.exp(-(base_logit + par["talk_k"] * np.log1p(kk[:, t]) + term)))
        talk = m & (rng.random(S) < pt)
        out["j"][m, t] = j[m]; out["R"][m, t] = R[m]; out["W"][m, t] = W[m]; out["talk"][m, t] = talk[m]
        out["seg"][m, t] = segc[m]; out["openf"][m, t] = openf[m]; out["openv"][m, t] = openv[m]
        # reset decision after this call
        if cls == "controller":
            h = np.minimum(par["h_vol"] * np.exp(np.clip(par["kappa_c"] * (s - par["ceil"] * s_star) / s_star, -5, 3)), 0.5)
        else:
            h = np.full(S, par["h_vol"])
        nxt_forced = m & (j >= 41)
        nxt_vol = m & ~nxt_forced & (rng.random(S) < h)
        nxt_forced = np.where(m, nxt_forced, False); nxt_vol = np.where(m, nxt_vol, False)
        s_prev = np.where(m, s, s_prev)
    v = {k: out[k][si, ti] for k in out}
    sim = x.select("agent", "lab", "goal_no", "unit_id", "pt_date", "t_first", "k_new", "chars_new", "n_oev", "r",
                   "P", "sid").with_columns(
        pl.Series("ctx_pos", v["j"].astype(np.int32)), pl.Series("R_true", v["R"]), pl.Series("W_true", v["W"]),
        pl.Series("talk", v["talk"].astype(bool)), pl.Series("seg_n", v["seg"].astype(np.int64)),
        pl.Series("open_forced", v["openf"].astype(bool)), pl.Series("open_consol", (v["openf"] + v["openv"]).astype(bool)))
    sim = sim.with_columns((pl.col("sid").cast(pl.Int64) * 10_000 + pl.col("seg_n")).alias("seg"))
    # P observed where the real call had a measured prompt, or at a simulated talk call (event tokens)
    sim = sim.with_columns(pl.when(pl.col("P").is_not_null() | pl.col("talk")).then(pl.col("R_true") + pl.col("W_true"))
                           .otherwise(None).alias("P"))
    # segment ends and lengths
    seg = sim.group_by("seg").agg(pl.len().alias("seg_len_calls"), pl.col("sid").first(), pl.col("t_first").min().alias("t0"),
                                  pl.col("open_forced").first().alias("of"), pl.col("open_consol").first().alias("oc")).sort("sid", "t0")
    seg = seg.with_columns(pl.col("of").shift(-1).over("sid").fill_null(False).alias("end_forced"),
                           pl.col("oc").shift(-1).over("sid").fill_null(False).alias("end_consol"))
    sim = sim.drop("open_forced", "open_consol").join(
        seg.select("seg", "seg_len_calls", "end_forced", "end_consol", pl.col("of").alias("open_forced"),
                   pl.col("oc").alias("open_consol")), on="seg", how="left")
    # k since the previous simulated talk (items of this call included), per agent-day
    sim = sim.sort("agent", "t_first").with_columns(pl.col("talk").cast(pl.Int32).cum_sum().over("sid").alias("_tc"))
    sim = sim.with_columns((pl.col("_tc") - pl.col("talk").cast(pl.Int32)).alias("_grp"))
    sim = sim.with_columns(pl.col("k_new").cum_sum().over("sid", "_grp").alias("k_since_talk")).drop("_tc", "_grp")
    sim = L.add_share(sim, r_col="r")
    # engagement at simulated talk calls
    k = np.maximum(sim["k_since_talk"].to_numpy().astype(float), 1.0)
    st = sim["s"].fill_null(np.nan).to_numpy()
    Pv = (sim["R_true"] + sim["W_true"]).to_numpy()
    sa = dict(zip(ag, s_star)); pa = dict(zip(ag, Pbar))
    ss = np.array([sa[a] for a in sim["agent"].to_list()]); pb = np.array([pa[a] for a in sim["agent"].to_list()])
    strue = sim["R_true"].to_numpy() / Pv
    if cls == "controller":
        xx = k * (ss / np.maximum(strue, 1e-4)) ** par["kappa_e"]
    elif cls == "competition":
        xx = k ** (1 - par["beta"]) * (pb / Pv)
    else:
        xx = k ** (1 - par["beta"])
    tk = sim["talk"].to_numpy()
    lo, hi = 1e-6, 10.0
    for _ in range(60):
        th = np.sqrt(lo * hi)
        mrate = np.mean(1 - np.exp(-th * xx[tk]))
        lo, hi = (th, hi) if mrate < par["E1_rate"] else (lo, th)
    e1 = rng.random(len(k)) < 1 - np.exp(-th * xx)
    sim = sim.with_columns(pl.when(pl.Series(tk)).then(pl.Series(e1)).otherwise(None).alias("eng_pending"))
    return sim


def estimate(sim: pl.DataFrame, B: int = 2) -> dict:
    bs = L.band_segments(sim)
    el = L.elasticities(bs, B=B)
    t = L.talk_rows(sim)
    return {"RI": el.get("RI"), "eta_W": el.get("eta_W"), "eps": el.get("eps"), "s_mean": el.get("s_mean"),
            "cv": L.cv_band(bs), "lever": L.segment_length_lever(sim, B=B).get("slope"),
            "pgrowth": L.p_growth(sim).get("ratio_median"),
            "beta": L.fit_beta_glm(t, B=0).get("beta") if t.height > 200 else None,
            **{k: v for k, v in L.share_dependence(t, B=B).items() if k in ("g_R", "g_W", "g_R_ci", "g_W_ci")},
            "overshoot": L.reset_profile(sim, B=B).get("overshoot"),
            "overshoot_any": L.reset_profile(sim, opener="open_consol", B=B).get("overshoot")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--units", default="38a,41,51c,51e,51f,51h")
    a = ap.parse_args()
    cal = L.load_calibration()
    c = L.load_calls()
    c = c.with_columns(L.room_tokens_expr(cal).alias("r"))
    c = L.add_share(c.filter(pl.col("ctx_mode") == "cu"), r_col="r")
    res = {"params": PAR, "units": a.units.split(","), "reps": a.reps, "runs": []}
    for unit in a.units.split(","):
        x, scale = real_inputs(c, [unit])
        print(unit, x.height, "calls", len(scale), "agents", flush=True)
        for cls in CLASSES:
            for rep in range(a.reps):
                t0 = time.time()
                sim = simulate(x, scale, cls, np.random.default_rng(1000 * rep + 17 * CLASSES.index(cls) + 7))
                e = estimate(sim)
                e.update({"unit": unit, "cls": cls, "rep": rep, "n_calls": x.height})
                res["runs"].append(e)
                if rep == 0:
                    f = lambda v: "None" if v is None else f"{v:.3f}"
                    print(f"  {cls:11s} rep0 " + " ".join(f"{k} {f(e.get(k))}" for k in
                          ("RI", "eta_W", "lever", "pgrowth", "beta", "g_R", "g_W", "overshoot", "overshoot_any", "cv"))
                          + f" ({time.time() - t0:.1f}s)", flush=True)
    out = L.DATA / "synthetic"
    out.mkdir(exist_ok=True)
    (out / "synthetic_runs.json").write_text(json.dumps(res, indent=1, default=float))
    summarize(res)


def summarize(res: dict):
    runs = pl.DataFrame([{k: (v if not isinstance(v, list) else None) for k, v in r.items()} for r in res["runs"]])
    agg = runs.group_by("cls").agg([pl.col(k).median().alias(k) for k in
                                    ("RI", "eta_W", "lever", "pgrowth", "beta", "g_R", "g_W", "overshoot", "overshoot_any", "cv")])
    print(agg.sort("cls"))
    (L.DATA / "synthetic" / "synthetic_summary.json").write_text(json.dumps(
        {"by_class": agg.to_dicts(),
         "by_unit_class": runs.group_by("unit", "cls").agg([pl.col(k).median().alias(k) for k in
                                                            ("RI", "eta_W", "lever", "pgrowth", "beta", "g_R", "g_W", "overshoot", "overshoot_any", "cv")]).to_dicts()},
        indent=1, default=float))


if __name__ == "__main__":
    main()


def cv_check(units=("41", "51f"), reps: int = 5) -> dict:
    """P3's real-data statistic (within-agent W-permutation CV ratio) on the synthetic classes."""
    from run_periods import w_permutation_cv
    cal = L.load_calibration()
    c = L.load_calls()
    c = c.with_columns(L.room_tokens_expr(cal).alias("r"))
    c = L.add_share(c.filter(pl.col("ctx_mode") == "cu"), r_col="r")
    out = []
    for unit in units:
        x, scale = real_inputs(c, [unit])
        for cls in CLASSES:
            for rep in range(reps):
                sim = simulate(x, scale, cls, np.random.default_rng(5000 + 1000 * rep + 17 * CLASSES.index(cls)))
                r = w_permutation_cv(L.band_segments(sim), n_perm=100)
                out.append({"unit": unit, "cls": cls, "rep": rep, **r})
                print(unit, cls, rep, round(r.get("ratio", float("nan")), 3), flush=True)
    (L.DATA / "synthetic" / "synthetic_cvcheck.json").write_text(json.dumps(out, indent=1, default=float))
    return out
