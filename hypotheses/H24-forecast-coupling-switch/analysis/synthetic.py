"""H24 synthetic validation (axis F), run before any real-data outcome.

Content world (O(n) soft spins, n = 32) with the village's actual #21 sampling: each switched agent's real
day-1 statement times and real tau_i (and real day-2/3 times for the N1 placebo). Latent states
  u_i(t) = h_g(t) g + h_a a_i + sigma_xi xi_i(t) + J(t) m_{-i}(t-1),   s_i = u_i / |u_i|
with a decaying kickoff field h_g(t) = h0 + h1 exp(-t / tau_f), persistent agent fields a_i, OU topic drift
xi_i (tau 30 min) and mean-field coupling J(t) = J1 for t >= tau_i (0 before; 0 always for the control).
Statements z = unit(s_i(t) + sigma_eps * noise), sigma_eps set so the within-agent same-window statement
cosine is ~0.5 (the measured #21 instrument value). g-hat used for residuals = noisy g (cos 0.8).

Numeric world (DeGroot soft spins): 3 anchor questions, 6 agents each, x_first ~ N(45, 8), updates
delta_i = kappa (xbar_{-i} - x_i) + N(0, 4); variant with measurement noise (regression to the mean).

Outputs: data/processed/H24-forecast-coupling-switch/G21/synthetic_validation.json, figures/synthetic_validation.pdf
Usage: uv run python hypotheses/H24-forecast-coupling-switch/analysis/synthetic.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h24stats import degroot, degroot_null, project_out, seg_alignment, segments, unit  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h24lib import H24, CARD, betaJ_snapshot  # noqa: E402

G = H24 / "G21"
n = 32
K, B, POST = 4, 40, 60.0
SHIFTS = (60.0, 90.0, 120.0)


def real_sampling():
    S = pl.read_parquet(G / "statements.parquet")
    sw = pl.read_parquet(G / "switch_on.parquet")
    switched = sw.filter(pl.col("role") == "switched")["agent"].to_list()
    tau = dict(zip(sw["agent"].to_list(), sw["tau_offset_min"].to_list()))
    cal = pl.read_parquet(H24.parents[1] / "processed/shared/calendar.parquet").filter(pl.col("goal_no") == 21).sort("pt_date")
    opens = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    days = {}
    for d in ["2025-12-01", "2025-12-02", "2025-12-03"]:
        sub = S.filter(pl.col("pt_date") == d).with_columns(((pl.col("t") - opens[d]).dt.total_seconds() / 60).alias("m"))
        days[d] = {a: np.sort(sub.filter(pl.col("agent") == a)["m"].to_numpy()) for a in switched + [10]}
    return switched, tau, days


def simulate_day(rng, agents_fields, J_of, h_of, T=241, sig_xi=0.27, h_a=1.0, xi0=None, s0=None):
    """Latent unit states (T x A x n) on a 1-min grid."""
    A = len(agents_fields)
    g = np.zeros(n); g[0] = 1.0
    xi = rng.standard_normal((A, n)) * sig_xi if xi0 is None else xi0.copy()
    S = np.zeros((T, A, n))
    s_prev = unit(h_of(0) * g + h_a * agents_fields + xi) if s0 is None else s0
    a_ou = np.exp(-1 / 30.0)
    for t in range(T):
        xi = a_ou * xi + np.sqrt(1 - a_ou ** 2) * sig_xi * rng.standard_normal((A, n))
        m_tot = s_prev.sum(0)
        m_others = (m_tot[None, :] - s_prev) / (A - 1)
        J = np.array([J_of(i, t) for i in range(A)])[:, None]
        u = h_of(t) * g + h_a * agents_fields + xi + J * m_others
        s_prev = unit(u)
        S[t] = s_prev
    return S, xi, s_prev


def statements_from(S, times_by_agent, rng, sig_eps):
    Z, ag, tm = [], [], []
    for i, ts in enumerate(times_by_agent):
        for t in ts:
            ti = int(min(max(t, 0), S.shape[0] - 1))
            Z.append(unit(S[ti, i] + sig_eps * rng.standard_normal(n))); ag.append(i); tm.append(t)
    return np.array(Z), np.array(ag), np.array(tm, float)


def one_world(rng, J1, h1, switched_times, ctrl_times, taus, days23, tau_med, sig_eps=0.15, ghat_cos=0.8,
              kickoff_null=False):
    A = len(switched_times) + 1  # last = control
    fields = unit(rng.standard_normal((A, n)))
    h0, tau_f = 0.5, 30.0
    taus_all = list(taus) + [1e9]
    if kickoff_null:
        J_of = lambda i, t: 0.0  # noqa: E731
    else:
        J_of = lambda i, t: J1 if t >= taus_all[i] else 0.0  # noqa: E731
    S1, xi, s_last = simulate_day(rng, fields, J_of, lambda t: h0 + h1 * np.exp(-t / tau_f))
    g = np.zeros(n); g[0] = 1
    gh = unit(ghat_cos * g + np.sqrt(1 - ghat_cos ** 2) * unit(project_out(rng.standard_normal((1, n)), g[None]))[0])
    Z, ag, tm = statements_from(S1, list(switched_times) + [ctrl_times], rng, sig_eps)
    Zr = unit(project_out(Z, gh[None]))
    sw = list(range(A - 1))
    tau_d = {i: taus[i] for i in sw}
    if kickoff_null:
        tau_d = {i: tau_med for i in sw}
    pre, post = segments(tm, ag, sw, tau_d, POST)
    out = {}
    res = seg_alignment(Zr, pre, post, K, B, rng)
    raw = seg_alignment(Z, pre, post, K, B, rng)
    out["dA_res"] = res["dA"]; out["dA_raw"] = raw["dA"]; out["bJ_pre"] = res["bJ_pre"]; out["bJ_post"] = res["bJ_post"]
    # true latent residual alignment in each window (noise-free states, true g removed)
    def true_A(i_lo, i_hi):
        V = []
        for i in sw:
            lo, hi = int(max(i_lo(i), 0)), int(min(i_hi(i), 240))
            if hi <= lo:
                return np.nan
            V.append(unit(unit(project_out(S1[lo:hi, i], g[None])).mean(0)))
        V = np.array(V); C = V @ V.T; N = len(V)
        return (C.sum() - N) / (N * (N - 1))
    out["trueA_pre"] = true_A(lambda i: 0, lambda i: taus[i])
    out["trueA_post"] = true_A(lambda i: taus[i], lambda i: taus[i] + POST)
    # N1 placebo: day-1 shifts (inside the coupled phase) + same offsets on days 2-3 (coupling on all day)
    plac = []
    for s in SHIFTS:
        p1, p2 = segments(tm, ag, sw, {i: tau_d[i] + s for i in sw}, POST)
        r = seg_alignment(Zr, p1, p2, K, B, rng)
        if r:
            plac.append(r["dA"])
    xi_d, s_d = xi, s_last
    for dtimes in days23:
        Jd = (lambda i, t: 0.0) if kickoff_null else (lambda i, t: J1 if i < A - 1 else 0.0)
        Sd, xi_d, s_d = simulate_day(rng, fields, Jd, lambda t: h0, xi0=xi_d, s0=s_d)
        Zd, agd, tmd = statements_from(Sd, list(dtimes) + [np.array([])], rng, sig_eps)
        Zdr = unit(project_out(Zd, gh[None]))
        p1, p2 = segments(tmd, agd, sw, tau_d, POST)
        r = seg_alignment(Zdr, p1, p2, K, B, rng)
        if r:
            plac.append(r["dA"])
    out["N1"] = plac
    return out


def numeric_power(rng, R=300):
    rows = []
    for rtm in (0.0, 4.0):
        for kappa in (0.0, 0.2, 0.4, 0.6):
            hits = 0; ks = []
            for _ in range(R):
                first, last, q = [], [], []
                for qq in range(3):
                    x = rng.normal(45, 8, 6)
                    y = x + kappa * ((x.sum() - x) / 5 - x) + rng.normal(0, 4, 6)
                    first += list(x + rng.normal(0, rtm, 6)); last += list(y + rng.normal(0, rtm, 6)); q += [qq] * 6
                k, dsd = degroot(first, last, q)
                kn, _ = degroot_null(first, last, q, rng, n_perm=400)
                p = (np.sum(kn >= k) + 1) / (len(kn) + 1)
                ks.append(k)
                if p < 0.10 and sum(v < 0 for v in dsd.values()) >= 2:
                    hits += 1
            rows.append({"rtm_noise_pp": rtm, "kappa": kappa, "rate": hits / R, "kappa_hat_mean": float(np.mean(ks))})
            print("numeric", rows[-1], flush=True)
    return rows


def main():
    t0 = time.time()
    rng = np.random.default_rng(20261003)
    switched, tau, days = real_sampling()
    st = [days["2025-12-01"][a] for a in switched]
    ctrl = days["2025-12-01"][10]
    taus = [tau[a] for a in switched]
    d23 = [[days[d][a] for a in switched] for d in ("2025-12-02", "2025-12-03")]
    tau_med = float(np.median(taus))
    R = int(os.environ.get("H24_SYN_R", 120))
    # kickoff-null worlds for the N2 threshold
    null_cache = {}
    for h1 in (0.0, 1.0):
        null_cache[h1] = [one_world(rng, 0.0, h1, st, ctrl, taus, d23, tau_med, kickoff_null=True)["dA_res"] for _ in range(R)]
        print(f"N2 null h1={h1}: q90 {np.quantile(null_cache[h1], 0.9):.3f}", flush=True)
    cells = []
    for h1 in (0.0, 1.0):
        for J1 in (0.0, 0.5, 1.0, 2.0, 4.0):
            det, dres, draw, tA_pre, tA_post, bjp, bjq, det_n1, det_n2 = [], [], [], [], [], [], [], [], []
            for r in range(R):
                w = one_world(rng, J1, h1, st, ctrl, taus, d23, tau_med)
                n2 = rng.choice(null_cache[h1], size=20, replace=False)
                q1 = np.quantile(w["N1"], 0.9) if len(w["N1"]) else np.inf
                q2 = np.quantile(n2, 0.9)
                det_n1.append(w["dA_res"] > q1); det_n2.append(w["dA_res"] > q2)
                det.append(w["dA_res"] > q1 and w["dA_res"] > q2)
                dres.append(w["dA_res"]); draw.append(w["dA_raw"]); tA_pre.append(w["trueA_pre"]); tA_post.append(w["trueA_post"])
                bjp.append(w["bJ_pre"]); bjq.append(w["bJ_post"])
            c = {"h1": h1, "J1": J1, "power_rule": float(np.mean(det)), "power_N1_only": float(np.mean(det_n1)),
                 "power_N2_only": float(np.mean(det_n2)), "dA_res_mean": float(np.mean(dres)), "dA_res_sd": float(np.std(dres)),
                 "dA_raw_mean": float(np.mean(draw)), "trueA_res_pre": float(np.nanmean(tA_pre)),
                 "trueA_res_post": float(np.nanmean(tA_post)),
                 "true_bJ_post": betaJ_snapshot(float(np.nanmean(tA_post)), len(switched)),
                 "true_bJ_pre": betaJ_snapshot(float(np.nanmean(tA_pre)), len(switched)),
                 "est_bJ_pre": float(np.mean(bjp)), "est_bJ_post": float(np.mean(bjq))}
            cells.append(c)
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in c.items()}, f"{time.time() - t0:.0f}s", flush=True)
    num = numeric_power(rng)
    out = {"R": R, "K": K, "B": B, "post_min": POST, "n": n, "sigma_eps": 0.15, "ghat_cos": 0.8,
           "field": {"h0": 0.5, "tau_f_min": 30, "h_a": 1.0, "sigma_xi": 0.27},
           "sampling": "real #21 day-1 statement times and tau_i of the 7 switched agents; days 2-3 times for N1",
           "N2_null_q90": {str(k): float(np.quantile(v, 0.9)) for k, v in null_cache.items()},
           "content": cells, "numeric": num}
    (G / "synthetic_validation.json").write_text(json.dumps(out, indent=1))
    figure(out)
    print(f"done {time.time() - t0:.0f}s", flush=True)


def figure(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.3))
    for h1, ls in ((0.0, "-"), (1.0, "--")):
        cs = [c for c in out["content"] if c["h1"] == h1]
        x = [c["true_bJ_post"] for c in cs]
        ax[0].plot(x, [c["power_rule"] for c in cs], "o" + ls, color="#2a6f97", label=f"rule (N1 & N2), kickoff h1={h1:g}")
        ax[0].plot(x, [c["power_N2_only"] for c in cs], "s" + ls, color="#b56576", ms=4, label=f"N2 only, h1={h1:g}")
        ax[1].plot(x, [c["est_bJ_post"] for c in cs], "o" + ls, color="#2a6f97", label=f"post, h1={h1:g}")
        ax[1].plot(x, [c["est_bJ_pre"] for c in cs], "s" + ls, color="#999999", ms=4, label=f"pre, h1={h1:g}")
        ax[2].plot([c["J1"] for c in cs], [c["dA_raw_mean"] for c in cs], "o" + ls, color="#e09f3e", label=f"raw ΔA, h1={h1:g}")
        ax[2].plot([c["J1"] for c in cs], [c["dA_res_mean"] for c in cs], "s" + ls, color="#2a6f97", label=f"residual ΔA, h1={h1:g}")
    ax[0].axhline(0.1, color="k", lw=0.5, ls=":"); ax[0].set_xlabel("true βJ₀/n after switch-on (latent, field removed)")
    ax[0].set_ylabel("detection rate"); ax[0].set_title("O1 power at #21 sampling"); ax[0].legend(fontsize=6)
    lim = [min(ax[1].get_xlim()[0], 0), 1]; ax[1].plot(lim, lim, "k:", lw=0.5)
    ax[1].set_xlabel("true βJ₀/n (latent)"); ax[1].set_ylabel("estimated βJ₀/n (rarefied k=4)"); ax[1].set_title("O2 recovery"); ax[1].legend(fontsize=6)
    ax[2].axhline(0, color="k", lw=0.5); ax[2].set_xlabel("coupling J1"); ax[2].set_ylabel("mean ΔA"); ax[2].set_title("raw vs residual"); ax[2].legend(fontsize=6)
    fig.tight_layout()
    (CARD / "figures").mkdir(exist_ok=True)
    fig.savefig(CARD / "figures/synthetic_validation.pdf")


if __name__ == "__main__":
    main()
