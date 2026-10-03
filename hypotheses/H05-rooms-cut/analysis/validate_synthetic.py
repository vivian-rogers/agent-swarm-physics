"""H05 estimator validation on synthetic kinetic Ising data (no project data touched).

Checks (prediction P1 on the card):
  V1  asymmetric J, stationary days: held-out Sigma_g vs exact Sigma; theta vs J - J^T; time reversal; shuffles.
  V2  symmetric J (detailed balance, Sigma = 0) under village-like nonstationarity: cold daily restarts and a
      shared daily-schedule field. Does the forward-only estimator report spurious EP? Does trimming help?
  V3  synthetic room cut: two rooms, cross-room couplings set to 0 after a date. Does the pair DiD (kappa,
      pair EP) and the whole-system / cross-pair EP recover it? False-positive rate with no cut.

Usage: uv run python hypotheses/H05-rooms-cut/analysis/validate_synthetic.py [--quick]
Writes data/processed/H05-rooms-cut/synthetic_validation.json and figures/synthetic_validation.pdf.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ep import (circular_shift_agents, ep_gauss_crossfit, ep_heldout, g_matrix, pair_index, reverse_time,
                shuffle_configurations, simulate_kinetic_ising, transitions, true_ep_stationary)
from pairs import did_2x2, pair_day_table, twfe

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H05-rooms-cut"
FIG = Path(__file__).resolve().parents[1] / "figures"
QUICK = "--quick" in sys.argv
DAY_LEN = 240


def make_J(N, rooms, rng, mu_in=0.06, sd=0.08, mu_out=0.06, self_c=0.9, cut=False):
    """Asymmetric couplings: independent draws for J_ij and J_ji; rooms: (N,) labels."""
    J = rng.normal(mu_in, sd, (N, N))
    same = rooms[:, None] == rooms[None, :]
    Jo = rng.normal(mu_out, sd, (N, N))
    J = np.where(same, J, 0.0 if cut else Jo)
    np.fill_diagonal(J, self_c)
    return J


def est(S, days, k=5):
    Sp, Sn, dd = transitions(S, days)
    G = g_matrix(Sp, Sn)
    r = ep_heldout(G, dd, k=k)
    r["newton_cf"] = ep_gauss_crossfit(G, dd, k=k)
    return r, Sp, Sn, dd


def v1(rng):
    N = 16
    rooms = np.repeat([0, 1], N // 2)
    J = make_J(N, rooms, rng, mu_in=0.0, sd=0.15, mu_out=0.0)
    res = {}
    for h0, label in ((0.0, "act~0.5"), (-0.6, "act~0.25")):
        h = np.full(N, h0) + rng.normal(0, 0.1, N)
        Sl, dl = simulate_kinetic_ising(J, h, 200 if not QUICK else 60, DAY_LEN, rng=rng)
        Spl, Snl, _ = transitions(Sl, dl)
        sig_true = true_ep_stationary(J, Spl, Snl)
        i, j = pair_index(N)
        asym = J[i, j] - J[j, i]
        for nd in ((20, 40) if not QUICK else (20,)):
            S, days = simulate_kinetic_ising(J, h, nd, DAY_LEN, rng=rng)
            r, Sp, Sn, dd = est(S, days)
            th = r["theta"]
            # time reversal
            Sr, dr = reverse_time(S, days)
            rr, *_ = est(Sr, dr)
            # shuffles
            Sc = shuffle_configurations(S, days, rng)
            rc, *_ = est(Sc, days)
            Sh = circular_shift_agents(S, days, rng)
            rh, *_ = est(Sh, days)
            res[f"{label}|days={nd}"] = {
                "activity": float((S > 0).mean()), "T": r["T"], "sigma_true": sig_true,
                "sigma_heldout": r["sigma"], "se": r["se"], "sigma_insample": r["insample"],
                "ratio_heldout_true": r["sigma"] / sig_true,
                "corr_theta_asymJ": float(np.corrcoef(th, asym)[0, 1]),
                "slope_theta_asymJ": float(np.polyfit(asym, th, 1)[0]),
                "reversed_sigma_heldout": rr["sigma"], "reversed_se": rr["se"],
                "corr_theta_rev_theta": float(np.corrcoef(rr["theta"], th)[0, 1]),
                "shuffle_config_sigma": rc["sigma"], "shuffle_config_se": rc["se"],
                "circshift_sigma": rh["sigma"], "circshift_se": rh["se"],
                "newton_cf_sigma": r["newton_cf"]["sigma"], "newton_cf_se": r["newton_cf"]["se"],
                "newton_plugin": r["newton_cf"]["plugin"],
                "newton_cf_shuffle_config": rc["newton_cf"]["sigma"], "newton_cf_circshift": rh["newton_cf"]["sigma"],
                "newton_cf_circshift_se": rh["newton_cf"]["se"],
            }
            print("V1", label, nd, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in res[f"{label}|days={nd}"].items()}, flush=True)
    return res, (J, h)


def v2(rng):
    N = 16
    A = rng.normal(0.0, 0.15, (N, N))
    J = (A + A.T) / 2
    np.fill_diagonal(J, 0.9)
    h = np.full(N, -0.4)
    nd = 30 if not QUICK else 15
    out = {}
    # daily-schedule field: everyone ramps up over the first 20 minutes, quiet dip in the last 15
    ht = np.zeros(DAY_LEN)
    ht[:20] = np.linspace(-1.5, 0, 20)
    ht[-15:] = -0.8
    for label, kw in (("stationary", {}), ("cold_restart", {"restart": "off"}),
                      ("schedule_field", {"h_t": ht}), ("cold+field", {"restart": "off", "h_t": ht})):
        S, days = simulate_kinetic_ising(J, h, nd, DAY_LEN, rng=rng, **kw)
        r, *_ = est(S, days)
        rec = {"sigma_heldout": r["sigma"], "se": r["se"], "activity": float((S > 0).mean()),
               "newton_cf": r["newton_cf"]["sigma"], "newton_cf_se": r["newton_cf"]["se"]}
        for trim in (10, 30):
            keep = np.tile(np.arange(DAY_LEN) >= trim, nd)
            rt, *_ = est(S[keep], days[keep])
            rec[f"trim{trim}_sigma"] = rt["sigma"]; rec[f"trim{trim}_se"] = rt["se"]
            rec[f"trim{trim}_newton_cf"] = rt["newton_cf"]["sigma"]
        out[label] = rec
        print("V2", label, {k: round(v, 5) for k, v in rec.items()}, flush=True)
    return out


def v3(rng, n_rep, nd=5, mu=0.06, sd=0.08, h0=-0.3):
    """Synthetic cut: rooms A/B (8+8), nd days before and after (village events are one week each).

    variants: cut (cross J -> 0), cut_matched (cross J -> 0 and each agent's field raised by its lost mean
    cross-room input, so activity stays put), no_cut (placebo)."""
    N = 16
    rooms = np.repeat([0, 1], N // 2)
    i_all, j_all = pair_index(N)
    cx = rooms[i_all] != rooms[j_all]
    recs = []
    for rep in range(n_rep):
        Jb = make_J(N, rooms, rng, mu_in=mu, sd=sd, mu_out=mu)
        h = np.full(N, h0) + rng.normal(0, 0.15, N)
        Sb, db = simulate_kinetic_ising(Jb, h, nd, DAY_LEN, rng=rng)
        mb = Sb.mean(0).astype(float)
        for variant in ("cut", "cut_matched", "no_cut"):
            Ja = Jb.copy(); ha = h.copy()
            if variant != "no_cut":
                cross = rooms[:, None] != rooms[None, :]
                if variant == "cut_matched":
                    ha = h + (np.where(cross, Jb, 0.0) @ mb)
                Ja[cross] = 0.0
            Sa, da = simulate_kinetic_ising(Ja, ha, nd, DAY_LEN, rng=rng)
            S = np.vstack([Sb, Sa]); days = np.r_[db, da + nd]
            room = np.tile(rooms, (len(S), 1))
            room[: len(Sb)] = 0  # before: everyone co-located
            tab = pair_day_table(S, days, np.arange(N), room)
            period = (tab["day"] >= nd).astype(int)
            treated = rooms[tab["i"]] != rooms[tab["j"]]
            pk = tab["i"] * 100 + tab["j"]
            rec = {"rep": rep, "variant": variant, "act_before": float((Sb > 0).mean()), "act_after": float((Sa > 0).mean())}
            for y in ("kappa", "sig"):
                dd = did_2x2(tab[y], pk, period, treated, 0, 1)
                tw = twfe(tab[y], tab["coloc"], pk, tab["day"])
                rec[f"did_{y}"] = dd["effect"]; rec[f"twfe_{y}"] = tw["beta"]; rec[f"twfe_{y}_se"] = tw.get("se_twoway", np.nan)
            for lab, Sx, dx, Jx in (("before", Sb, db, Jb), ("after", Sa, da, Ja)):
                Sp, Sn, dd_ = transitions(Sx, dx)
                G = g_matrix(Sp, Sn)
                rec[f"ep_heldout_agent_hour_{lab}"] = ep_heldout(G, dd_, k=5, return_theta=False)["sigma"] * 60 / N
                rec[f"ep_newton_agent_hour_{lab}"] = ep_gauss_crossfit(G, dd_, k=5)["sigma"] * 60 / N
                rec[f"ep_newton_cross_per_pairhour_{lab}"] = ep_gauss_crossfit(G[:, cx], dd_, k=5)["sigma"] * 60 / cx.sum()
                rec[f"ep_newton_within_per_pairhour_{lab}"] = ep_gauss_crossfit(G[:, ~cx], dd_, k=5)["sigma"] * 60 / (~cx).sum()
                rec[f"true_ep_agent_hour_{lab}"] = true_ep_stationary(Jx, Sp, Sn) * 60 / N
                ii, jj = i_all, j_all
                contrib = (Jx[ii, jj] - Jx[jj, ii]) * G.mean(0)
                rec[f"true_ep_cross_per_pairhour_{lab}"] = float(contrib[cx].sum() * 60 / cx.sum())
                rec[f"true_ep_within_per_pairhour_{lab}"] = float(contrib[~cx].sum() * 60 / (~cx).sum())
            recs.append(rec)
            print("V3", {k: (round(float(v), 4) if isinstance(v, (float, np.floating)) else v) for k, v in rec.items()}, flush=True)
    return recs


def summarize_v3(recs):
    out = {}
    for variant in ("cut", "cut_matched", "no_cut"):
        rr = [r for r in recs if r["variant"] == variant]
        if not rr:
            continue
        s = {"n_rep": len(rr)}
        for k in ("did_kappa", "did_sig", "twfe_kappa", "twfe_sig"):
            v = np.array([r[k] for r in rr])
            s[k] = {"mean": float(np.nanmean(v)), "sd": float(np.nanstd(v)), "frac_negative": float(np.mean(v < 0))}
        for k in ("twfe_kappa", "twfe_sig"):
            z = np.array([r[k] / r[k + "_se"] for r in rr])
            s[k + "_frac_z>1.96"] = float(np.mean(z > 1.96))
        for k in ("act", "ep_heldout_agent_hour", "ep_newton_agent_hour", "ep_newton_cross_per_pairhour",
                  "ep_newton_within_per_pairhour", "true_ep_agent_hour", "true_ep_cross_per_pairhour", "true_ep_within_per_pairhour"):
            b = np.array([r[f"{k}_before"] for r in rr]); a = np.array([r[f"{k}_after"] for r in rr])
            s[k] = {"before": float(b.mean()), "after": float(a.mean()), "frac_after<before": float(np.mean(a < b))}
        out[variant] = s
    return out


def figure(v1res, v3recs, Jh):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.4))
    keys = list(v1res)
    x = np.arange(len(keys))
    ax[0].bar(x - 0.2, [v1res[k]["sigma_true"] for k in keys], 0.2, label="exact Σ", color="#444")
    ax[0].bar(x, [v1res[k]["sigma_heldout"] for k in keys], 0.2, yerr=[v1res[k]["se"] for k in keys], label="held-out Σ_g", color="#2a7")
    ax[0].bar(x + 0.2, [v1res[k]["circshift_sigma"] for k in keys], 0.2, label="circ-shift null", color="#bbb")
    ax[0].set_xticks(x); ax[0].set_xticklabels([k.replace("|", "\n") for k in keys], fontsize=6)
    ax[0].set_ylabel("nats / bin"); ax[0].legend(fontsize=6); ax[0].set_title("V1: EP recovery", fontsize=9)
    ax[1].text(0.05, 0.9, "\n".join(f"{k}: r(θ, J−Jᵀ)={v1res[k]['corr_theta_asymJ']:.2f}; rev r={v1res[k]['corr_theta_rev_theta']:.2f}"
                                      for k in keys), fontsize=6, va="top", transform=ax[1].transAxes)
    ax[1].axis("off"); ax[1].set_title("V1: coupling asymmetry", fontsize=9)
    for var, col in (("cut", "#c33"), ("cut_matched", "#e90"), ("no_cut", "#36c")):
        v = [r["twfe_kappa"] for r in v3recs if r["variant"] == var]
        ax[2].hist(v, bins=12, alpha=0.6, color=col, label=var)
    ax[2].axvline(0, color="k", lw=0.8); ax[2].set_xlabel("TWFE β(co-location) on κ"); ax[2].legend(fontsize=7)
    ax[2].set_title("V3: synthetic room cut", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "synthetic_validation.pdf"); plt.close(fig)


if __name__ == "__main__":
    t0 = time.time()
    rng = np.random.default_rng(20261003)
    OUT.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
    r1, Jh = v1(rng)
    r2 = v2(rng)
    r3 = v3(rng, 4 if QUICK else 20)
    res = {"V1_asymmetric_stationary": r1, "V2_symmetric_nonstationary": r2,
           "V3_room_cut_replicates": r3, "V3_summary": summarize_v3(r3),
           "params": {"day_len": DAY_LEN, "quick": QUICK, "seed": 20261003}, "runtime_s": time.time() - t0}
    (OUT / "synthetic_validation.json").write_text(json.dumps(res, indent=1, default=float))
    figure(r1, r3, Jh)
    print("done", f"{time.time()-t0:.0f}s")
