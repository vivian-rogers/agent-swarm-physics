"""H106 natives (non-holdout).

N1 NE27: the two-rate contrast from replication.py (real) against the drift-world (synthetic D) distribution on the
   same window (Amendment A1); magnet prediction -ln(N_post/N_pre); two placebo breaks (descriptive).
N2 G51 + NE32 + NE33: #51 day residuals (H81 native form: own #51 mean removed; #51 directions and own agent goal
   projected). Cross-agent lagged alignment L(k) over i != j (expectation free of N). Window statistic
   phi_W = L_W(1) / L_W(0+); Delta phi = phi_post - phi_pre (Amendment A2: phi rather than ln k, because k = -ln phi
   is undefined when phi is outside (0, 1) in short windows). Placebo: every other #51 boundary with the same window
   lengths. Power: planted day-level OU common mode with tau proportional to N on the real #51 panel.
   Within-#51 weekly phi_w vs ln N_w (descriptive).
Output: data/processed/H106-slow-mode-finite-size/natives/natives.json
Usage: uv run python hypotheses/H106-slow-mode-finite-size/analysis/natives.py [--reps 300]
"""
from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h106lib as L  # noqa: E402

MODELS = ["bge_small", "gte_modernbert"]
EVENTS = {"NE32": {"pre": ("2026-07-06", "2026-07-08"), "post": ("2026-07-10", "2026-07-17"), "gap": 1},
          "NE33": {"pre": ("2026-08-27", "2026-09-02"), "post": ("2026-09-03", "2026-09-04"), "gap": 0}}


# ------------------------------------------------------------------------------------------------- #51 day panel
def g51_panel(model):
    ad, X, blocks = L.load(model, "style_resid", "III")
    P = L.projectors(model, "III", ad)
    m = (ad["goal_no"] == 51).to_numpy()
    ad51 = ad.filter(pl.col("goal_no") == 51)
    X = X[m]
    agent = ad51["agent"].to_numpy().astype(int)
    Pi = np.stack([P.get((51, a), P[(51, -1)]) for a in agent])
    Xp = np.einsum("nij,nj->ni", Pi, X)
    R = np.full_like(Xp, np.nan)
    for a in np.unique(agent):
        mm = agent == a
        if mm.sum() >= 3:
            R[mm] = np.einsum("nij,nj->ni", Pi[mm], Xp[mm] - Xp[mm].mean(0))
    days = sorted(set(ad51["pt_date"].to_list()))
    di = {d: k for k, d in enumerate(days)}
    dayidx = np.array([di[d] for d in ad51["pt_date"].to_list()])
    nday = pl.read_parquet(L.OUT / "nday.parquet")
    Nd = dict(zip(nday["pt_date"].to_list(), nday["N_d"].to_list()))
    return {"agent": agent, "R": R, "day": dayidx, "days": days, "N": np.array([Nd[d] for d in days], float)}


def day_sums(agent, R, day, nd):
    """Per day: sum vector S_d, sum of squares Q_d, count n_d, dict agent -> vector."""
    ok = ~np.isnan(R[:, 0])
    S = np.zeros((nd, R.shape[1])); n = np.zeros(nd); Q = np.zeros(nd)
    np.add.at(S, day[ok], R[ok]); np.add.at(n, day[ok], 1); np.add.at(Q, day[ok], (R[ok] ** 2).sum(1))
    per = [dict() for _ in range(nd)]
    for k in np.flatnonzero(ok):
        per[day[k]][agent[k]] = R[k]
    return S, Q, n, per


def window_phi(S, Q, n, per, days_idx):
    """phi = L(1)/L(0+) over consecutive day pairs inside the window (i != j)."""
    days_idx = sorted(days_idx)
    num0 = den0 = 0.0
    for d in days_idx:
        if n[d] >= 2:
            num0 += S[d] @ S[d] - Q[d]; den0 += n[d] * (n[d] - 1)
    num1 = den1 = 0.0
    for d0, d1 in zip(days_idx[:-1], days_idx[1:]):
        if d1 != d0 + 1 or n[d0] == 0 or n[d1] == 0:
            continue
        cross = S[d0] @ S[d1]
        same = sum(per[d0][a] @ per[d1][a] for a in set(per[d0]) & set(per[d1]))
        num1 += cross - same
        den1 += n[d0] * n[d1] - len(set(per[d0]) & set(per[d1]))
    if den0 == 0 or den1 == 0:
        return np.nan
    L0 = num0 / den0; L1 = num1 / den1
    return float(L1 / L0) if L0 > 0 else np.nan


def contrast(S, Q, n, per, j_post, n_pre, n_post, gap, nd):
    pre = list(range(j_post - gap - n_pre, j_post - gap))
    post = list(range(j_post, j_post + n_post))
    if min(pre) < 0 or max(post) >= nd:
        return np.nan
    return window_phi(S, Q, n, per, post) - window_phi(S, Q, n, per, pre)


def event_positions(days):
    out = {}
    for name, e in EVENTS.items():
        pre = [k for k, d in enumerate(days) if e["pre"][0] <= d <= e["pre"][1]]
        post = [k for k, d in enumerate(days) if e["post"][0] <= d <= e["post"][1]]
        out[name] = {"j_post": post[0], "n_pre": len(pre), "n_post": len(post), "gap": post[0] - pre[-1] - 1}
    return out


def g51_stats(pnl):
    nd = len(pnl["days"])
    S, Q, n, per = day_sums(pnl["agent"], pnl["R"], pnl["day"], nd)
    ev = event_positions(pnl["days"])
    res = {}
    for name, e in ev.items():
        real = contrast(S, Q, n, per, e["j_post"], e["n_pre"], e["n_post"], e["gap"], nd)
        plac = [contrast(S, Q, n, per, j, e["n_pre"], e["n_post"], e["gap"], nd) for j in range(nd) if j != e["j_post"]]
        plac = np.array([x for x in plac if x == x])
        Npre = float(pnl["N"][e["j_post"] - e["gap"] - e["n_pre"]:e["j_post"] - e["gap"]].mean())
        Npost = float(pnl["N"][e["j_post"]:e["j_post"] + e["n_post"]].mean())
        res[name] = {"dphi": real, "placebo_n": int(len(plac)),
                     "placebo_pct": float((plac < real).mean()) if len(plac) and real == real else np.nan,
                     "N_pre": Npre, "N_post": Npost, **e}
    # weekly phi vs ln N
    wk = {}
    for k, d in enumerate(pnl["days"]):
        import datetime as dt
        w = dt.date.fromisoformat(d).isocalendar()[1]
        wk.setdefault(w, []).append(k)
    W = [(w, window_phi(S, Q, n, per, ks), float(pnl["N"][ks].mean())) for w, ks in sorted(wk.items())]
    Wv = np.array([(p, np.log(N)) for _, p, N in W if p == p])
    slope = float(np.polyfit(Wv[:, 1], Wv[:, 0], 1)[0]) if len(Wv) >= 3 else np.nan
    res["weekly"] = {"rows": [{"week": int(w), "phi": p, "N": N} for w, p, N in W], "slope_phi_on_lnN": slope}
    res["phi_all"] = window_phi(S, Q, n, per, list(range(nd)))
    return res


def plant_power(pnl, rng, reps, share, tau0=3.0, magnet=True):
    """Planted day-level OU common mode (share of residual variance), tau proportional to N_d (magnet) or constant;
    noise = real #51 residual rows permuted. Returns placebo percentiles of the planted contrasts."""
    R0 = pnl["R"].copy(); ok = ~np.isnan(R0[:, 0])
    nd = len(pnl["days"]); d = R0.shape[1]
    var = float(np.nanmean((R0[ok] ** 2).sum(1)))
    Nm = pnl["N"].mean()
    out = {name: [] for name in EVENTS}
    ev = event_positions(pnl["days"])
    for _ in range(reps):
        E = R0.copy(); E[ok] = R0[ok][rng.permutation(ok.sum())]
        u = np.zeros((nd, d)); z = rng.standard_normal((nd, d)) * np.sqrt(var * share / d)
        for k in range(nd):
            tau = tau0 * (pnl["N"][k] / Nm if magnet else 1.0)
            rho = np.exp(-1.0 / tau)
            u[k] = z[k] if k == 0 else rho * u[k - 1] + np.sqrt(1 - rho ** 2) * z[k]
        Rs = E * np.sqrt(1 - share)
        Rs[ok] += u[pnl["day"][ok]]
        S, Q, n, per = day_sums(pnl["agent"], Rs, pnl["day"], nd)
        for name, e in ev.items():
            real = contrast(S, Q, n, per, e["j_post"], e["n_pre"], e["n_post"], e["gap"], nd)
            plac = np.array([contrast(S, Q, n, per, j, e["n_pre"], e["n_post"], e["gap"], nd) for j in range(nd)
                             if j != e["j_post"]])
            plac = plac[~np.isnan(plac)]
            out[name].append(float((plac < real).mean()) if real == real and len(plac) else np.nan)
    return {name: {"median_pct": float(np.nanmedian(v)), "power_pct_ge_0.9": float(np.nanmean(np.array(v) >= 0.9))}
            for name, v in out.items()}


def ne27_eval(rep):
    syn = pl.read_parquet(L.OUT / "synthetic/replicates.parquet")
    out = {}
    for model in MODELS:
        r = rep["ne27"][model]["NE27"]
        D = syn.filter((pl.col("model") == model) & (pl.col("regime") == "I") & (pl.col("world") == "D"))["ne27_dlnk"].to_numpy()
        M = syn.filter((pl.col("model") == model) & (pl.col("regime") == "I") & (pl.col("world") == "M"))["ne27_dlnk"].to_numpy()
        q05 = float(np.nanquantile(D, 0.05))
        out[model] = {"dlnk": r.get("dlnk"), "jk": r.get("jk"), "N_pre": r.get("N_pre"), "N_post": r.get("N_post"),
                      "magnet_pred": r.get("magnet_pred"), "D_q05": q05, "D_median": float(np.nanmedian(D)),
                      "D_pct": float(np.nanmean(D < r["dlnk"])) if r.get("ok") else None,
                      "power_M_below_Dq05": float(np.nanmean(M < q05)),
                      "pass": bool(r.get("ok") and r["dlnk"] < q05 and abs(r["dlnk"] - r["magnet_pred"]) <= 0.5),
                      "placebo": {k: v.get("dlnk") for k, v in rep["ne27"][model]["placebo"].items()}}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--reps", type=int, default=300)
    a = ap.parse_args()
    out = L.OUT / "natives"; out.mkdir(parents=True, exist_ok=True)
    rep = json.loads((L.OUT / "replication/replication.json").read_text())
    res = {"NE27": {"by_model": ne27_eval(rep)}, "G51": {"by_model": {}}}
    for model in MODELS:
        pnl = g51_panel(model)
        st = g51_stats(pnl)
        rng = np.random.default_rng(zlib.crc32(f"H106|G51|{model}".encode()))
        st["power"] = {f"share{s}_tau3_magnet": plant_power(pnl, rng, a.reps // (2 if s == 0.05 else 3), s)
                       for s in (0.05, 0.2)}
        res["G51"]["by_model"][model] = st
        print(model, json.dumps({k: v for k, v in st.items() if k != "weekly"}, default=float), flush=True)
    # verdicts (card rules + Amendment A3: unpowered tests are inconclusive whatever the sign)
    ne = res["NE27"]["by_model"]
    pw = max(v["power_M_below_Dq05"] for v in ne.values())
    if pw < 0.8:
        v27 = "inconclusive (unpowered)"
    elif all(v["pass"] for v in ne.values()):
        v27 = "supported"
    elif all(v["dlnk"] >= 0 for v in ne.values()):
        v27 = "failed"
    else:
        v27 = "mixed"
    res["NE27"]["verdict"] = "descriptive" if v27.startswith("inconclusive") else v27
    res["NE27"]["verdict_reading"] = v27
    res["NE27"]["power_max"] = pw
    lines = ["| Model | Δln k (jackknife 95% CI) | magnet prediction | drift world D: median, q05 | percentile in D | power (M below D q05) | placebo breaks |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for m, v in ne.items():
        jk = v["jk"] or {}
        lines.append(f"| {m} | {v['dlnk']:+.2f} [{jk.get('lo', float('nan')):+.2f}, {jk.get('hi', float('nan')):+.2f}] | "
                     f"{v['magnet_pred']:+.2f} (N {v['N_pre']:.1f} → {v['N_post']:.1f}) | {v['D_median']:+.2f}, {v['D_q05']:+.2f} | "
                     f"{v['D_pct']:.2f} | {v['power_M_below_Dq05']:.2f} | "
                     + ", ".join(f"{k}: {x:+.2f}" for k, x in v["placebo"].items() if x is not None) + " |")
    res["NE27"]["result_md"] = "\n".join(lines) + f"\n\nReading: **{v27}** (card rule; power of the D-world 5% test under M: {pw:.2f})."
    g = res["G51"]["by_model"]
    pw51 = max(g[m]["power"]["share0.2_tau3_magnet"][e]["power_pct_ge_0.9"] for m in g for e in EVENTS)
    res["G51"]["power_max"] = pw51
    res["G51"]["verdict"] = "n/a" if pw51 < 0.8 else "pending"
    lines = ["| Model | event | Δφ (post − pre) | placebo percentile | N pre → post | planted power (share 0.05 / 0.2) |",
             "| --- | --- | --- | --- | --- | --- |"]
    for m in g:
        for e in EVENTS:
            x = g[m][e]
            p05 = g[m]["power"]["share0.05_tau3_magnet"][e]["power_pct_ge_0.9"]
            p2 = g[m]["power"]["share0.2_tau3_magnet"][e]["power_pct_ge_0.9"]
            lines.append(f"| {m} | {e} | {x['dphi']:+.3f} | {x['placebo_pct']:.2f} (n {x['placebo_n']}) | "
                         f"{x['N_pre']:.1f} → {x['N_post']:.1f} | {p05:.2f} / {p2:.2f} |")
    for m in g:
        lines.append(f"\nWeekly φ_w vs ln N_w slope ({m}): {g[m]['weekly']['slope_phi_on_lnN']:+.3f}; whole-period φ = {g[m]['phi_all']:.3f}.")
    res["G51"]["result_md"] = "\n".join(lines) + (f"\n\nReading: **inconclusive** (unpowered: the best planted power is "
                                                  f"{pw51:.2f} < 0.8); verdict n/a by the card's power rule.")
    (out / "natives.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
