"""H21 synthetic validation (faithfulness axis F): two-sublattice vector spins at G12's real design.

The design (who spoke when, in which debate, phase and team; statement counts; debate timings) is taken from
data/processed/H21-debate-antiferromagnet/G12/statements.parquet + debates_resolved.json. Only structure is
used (no embeddings, no outcomes). Statements are simulated in the D = 32 whitened space:

    x_k = f h_i  +  g u_d [pre, deb]  +  z_i(t_k) a_d  +  gen eps_i a_gen [deb]  +  xi_k,     xi ~ N(0, I)

  h_i   agent/family field (unit; agents of one lab share 70% of it), strength f
  u_d   debate topic direction (uniform field from the motion), strength g
  a_d   debate stance axis (random unit, orthogonal to u_d): the two-sublattice direction
  z_i   stance along a_d. Static model: z_i = mu eps_i in 'deb' (mu_pre = mu/2 in 'pre', 0 after the verdict).
        Dynamic model: Ornstein-Uhlenbeck with staggered field mu eps_i during the debate, couplings K_in
        (own team, ferro) and K_out (other team, antiferro), K_s = K_in + K_out, time constant tau, latent noise
        eta; after the verdict the staggered field is off and a winner field w eps_W switches on.
  a_gen a direction shared by all debates (generic 'proposing vs opposing' rhetoric), strength gen.

Experiments (results -> data/processed/H21-debate-antiferromagnet/synthetic/synthetic.json, figure ->
figures/synthetic_validation.pdf):
  E1 power / recovery vs mu (static)            E2 false positives under family fields and lab-sorted teams
  E3 generic vs motion-specific decomposition   E4 dynamics: rho (staggered susceptibility), remanence, winner field
  E5 per-agent rotation null calibration
  E6 semi-synthetic: inject mu eps_i a_d into REAL #12 masked statement vectors whose team structure has been
     destroyed (each agent's statements shuffled among its own pre/deb/post rows). Real anisotropy and heavy tails;
     no real outcome is computed.

Usage: uv run python hypotheses/H21-debate-antiferromagnet/analysis/synthetic.py [--quick]
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import afmlib as L  # noqa: E402
import h21core as C  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H21-debate-antiferromagnet"
FIG = HERE.parent / "figures"
D = 32
QUICK = "--quick" in sys.argv


def load_design():
    st = pl.read_parquet(DATA / "G12/statements.parquet")
    deb = json.loads((DATA / "G12/debates_resolved.json").read_text())
    roster = dict(zip(st["name"], st["agent"]))
    lab_of = dict(zip(st["agent"].to_list(), st["lab"].to_list()))
    t0 = st["t"].min()

    def sec(s):
        import datetime as dt
        return (dt.datetime.fromisoformat(s) - t0).total_seconds()

    debates = []
    for d in deb:
        debates.append({"debate": d["debate"], "gov": [roster[x] for x in d["gov"]], "opp": [roster[x] for x in d["opp"]],
                        "judge": roster.get(d["judge"]), "winner": {"Gov": 1, "Opp": -1}.get(d.get("winner"), 0),
                        "t_first_speech": sec(d["t_first_speech"]), "t_verdict": sec(d["t_verdict"]),
                        "t_teams": sec(d["t_teams"]), "t_post_end": sec(d["_t_post_end"])})
    return C.to_np(st), debates, lab_of


def simulate(st, debates, lab_of, rng, mu=0.2, f=1.0, g=1.0, gen=0.0, dynamic=False, K_s=0.0, tau=120.0,
             eta=0.5, w=0.0, mu_pre_frac=0.5, sigma=1.0):
    n = len(st["agent"])
    agents = np.unique(st["agent"])
    labs = sorted(set(lab_of[a] for a in agents))
    c_lab = {l: L.unit(rng.standard_normal(D)) for l in labs}
    h = {a: L.unit(0.7 * c_lab[lab_of[a]] + 0.3 * L.unit(rng.standard_normal(D))) for a in agents}
    a_gen = L.unit(rng.standard_normal(D))
    X = sigma * rng.standard_normal((n, D))
    for a in agents:
        X[st["agent"] == a] += f * h[a]
    for deb in debates:
        dmask = st["debate"] == deb["debate"]
        u = L.unit(rng.standard_normal(D))
        a = rng.standard_normal(D); a -= (a @ u) * u; a = L.unit(a)
        eps = {x: 1 for x in deb["gov"]} | {x: -1 for x in deb["opp"]}
        for ph in ("pre", "deb"):
            X[dmask & (st["phase"] == ph)] += g * u
        dm = dmask & (st["phase"] == "deb")
        for x, e in eps.items():
            X[dm & (st["agent"] == x)] += gen * e * a_gen
        if not dynamic:
            for x, e in eps.items():
                X[dm & (st["agent"] == x)] += mu * e * a
                X[dmask & (st["phase"] == "pre") & (st["agent"] == x)] += mu_pre_frac * mu * e * a
        else:
            ids = list(eps)
            e_vec = np.array([eps[x] for x in ids], dtype=float)
            k = len(ids)
            M = np.zeros((k, k))
            K_in = K_out = K_s / 2
            for i in range(k):
                own = [j for j in range(k) if j != i and e_vec[j] == e_vec[i]]
                oth = [j for j in range(k) if e_vec[j] != e_vec[i]]
                for j in own:
                    M[i, j] = K_in / len(own)
                for j in oth:
                    M[i, j] = -K_out / len(oth)
            t_start, t_end, dt_ = deb["t_teams"], deb["t_post_end"], 5.0
            grid = np.arange(t_start, t_end + dt_, dt_)
            z = np.zeros(k)
            Z = np.zeros((len(grid), k))
            for gi, t in enumerate(grid):
                if t < deb["t_first_speech"]:
                    hfield = mu_pre_frac * mu * e_vec
                elif t < deb["t_verdict"]:
                    hfield = mu * e_vec
                else:
                    hfield = w * deb["winner"] * np.ones(k)
                z = z + dt_ / tau * (-z + hfield + M @ z) + np.sqrt(2 * dt_ / tau) * eta * rng.standard_normal(k)
                Z[gi] = z
            sel = np.flatnonzero(dmask & np.isin(st["phase"], ["pre", "deb", "post"]))
            for r in sel:
                if st["agent"][r] not in eps:
                    continue
                gi = min(len(grid) - 1, max(0, int((st["ts"][r] - t_start) // dt_)))
                X[r] += Z[gi, ids.index(st["agent"][r])] * a
    return X


def real_noise_base(dim=D):
    """Real #12 masked statement vectors (whitened, agent-centred) as a noise bank."""
    sys.path.insert(0, str(ROOT / "infra/shared"))
    from common import load_whitener
    E = np.load(DATA / "G12/emb_masked.npy").astype(np.float32)
    st = pl.read_parquet(DATA / "G12/statements.parquet")
    return L.agent_center(load_whitener("I", dim)(E).astype(np.float64), st["agent"].to_numpy().astype(int))


def inject(Xr, st, debates, rng, mu):
    """Shuffle each agent's vectors among its own debate-window rows (destroys real team structure), then add the
    staggered field mu eps_i a_d to its 'deb' rows (and mu/2 to 'pre' rows) with a fresh random axis per debate."""
    X = Xr.copy()
    inwin = np.isin(st["phase"], ["pre", "deb", "post"])
    for a in np.unique(st["agent"]):
        r = np.flatnonzero(inwin & (st["agent"] == a))
        X[r] = Xr[rng.permutation(r)]
    for deb in debates:
        ax = L.unit(rng.standard_normal(X.shape[1]))
        for x, e in [(g, 1) for g in deb["gov"]] + [(o, -1) for o in deb["opp"]]:
            m = (st["debate"] == deb["debate"]) & (st["agent"] == x)
            X[m & (st["phase"] == "deb")] += mu * e * ax
            X[m & (st["phase"] == "pre")] += 0.5 * mu * e * ax
    return X


def run_all(X, st, debates, lab_of, n_perm=2000, extras=(), rng=0):
    """extras: subset of {'generic', 'verdict', 'fluct', 'pairfe'}."""
    if extras is True:
        extras = ("generic", "verdict", "fluct")
    Xc = L.agent_center(X, st["agent"])
    W = C.build_windows(X, st, debates, "deb", Xc=Xc)
    r = {"static": C.static_tests(W, n_perm, rng)}
    if "generic" in extras:
        r["generic"] = C.generic_tests(W, n_perm, rng, n_flip=300)
    if "verdict" in extras:
        r["verdict"] = {k: v for k, v in C.verdict_tests(X, st, debates, Xc=Xc).items() if k != "rows"}
    if "fluct" in extras:
        r["fluct"] = C.fluct_tests(C.fluct_series(X, st, debates, Xc=Xc), 1000, rng)
    if "pairfe" in extras:
        r["pairfe"] = C.pair_fe_regression(W, 300, rng)
    return r


def run_E4(st, debates, lab_of, rng, nsim):
    E4 = []
    for K_s in (0.0, 0.4, 0.8):
        for eta in (0.5, 1.5):
            for w in (0.0, 0.5):
                rs = [run_all(simulate(st, debates, lab_of, rng, mu=0.8, dynamic=True, K_s=K_s, eta=eta, w=w), st, debates,
                              lab_of, 500, ("verdict", "fluct"), int(rng.integers(1e9))) for _ in range(nsim // 4)]
                fl = [x["fluct"] for x in rs]; vd = [x["verdict"] for x in rs]
                E4.append({"K_s": K_s, "eta": eta, "w": w,
                           "mean_rho": float(np.nanmean([x["rho"] for x in fl])),
                           "power_rho": float(np.mean([x.get("p_rho_neg", 1) < 0.05 for x in fl])),
                           "mean_chi_ratio": float(np.nanmean([x["chi_ratio"] for x in fl])),
                           "mean_remanence": float(np.nanmean([x["remanence"] for x in vd])),
                           "mean_winner_asym": float(np.nanmean([x["winner_asym"] for x in vd])),
                           "power_asym": float(np.mean([x["winner_asym_ci"][0] > 0 for x in vd])),
                           "mean_delta": float(np.mean([x["static"]["delta"] for x in rs])),
                           "power_delta": float(np.mean([x["static"]["p_delta"] < 0.05 for x in rs]))})
                print("E4", E4[-1], flush=True)
    return E4


def main():
    t0 = time.time()
    st, debates, lab_of = load_design()
    if "--only-E4" in sys.argv:  # re-run E4 after the parity-demeaning fix to fluct_series; keep the other results
        out = json.loads((DATA / "synthetic/synthetic.json").read_text())
        rng = np.random.default_rng(20261004)
        out["E4_dynamics"] = run_E4(st, debates, lab_of, rng, 200)
        out["E4_note"] = "re-run 2026-10-03 after demeaning fluctuation series within bin parity (earlier rho biased +0.10)"
        (DATA / "synthetic/synthetic.json").write_text(json.dumps(out, indent=1))
        plot(out)
        print(f"done {time.time()-t0:.0f}s")
        return
    out = {"design": {"n_statements": int(len(st["agent"])), "n_debates": len(debates),
                      "deb_statements_debaters": int(sum(((st["debate"] == d["debate"]) & (st["phase"] == "deb") &
                                                          np.isin(st["agent"], d["gov"] + d["opp"])).sum() for d in debates))}}
    rng = np.random.default_rng(20261003)
    nsim = 40 if QUICK else 200

    # E1: power and recovery vs mu (static, family field f=1, topic g=1)
    mus = [0.0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2]
    E1 = []
    for mu in mus:
        rs = [run_all(simulate(st, debates, lab_of, rng, mu=mu), st, debates, lab_of, 1000, (), int(rng.integers(1e9)))["static"]
              for _ in range(nsim)]
        E1.append({"mu": mu, "power_delta": float(np.mean([x["p_delta"] < 0.05 for x in rs])),
                   "power_ms": float(np.mean([x["p_ms"] < 0.05 for x in rs])),
                   "power_recovery": float(np.mean([x["p_recovered"] < 0.05 for x in rs])),
                   "mean_delta": float(np.mean([x["delta"] for x in rs])), "sd_delta": float(np.std([x["delta"] for x in rs])),
                   "mean_ms": float(np.mean([x["ms"] for x in rs])), "mean_recovered": float(np.mean([x["recovered"] for x in rs])),
                   "n_debates": rs[0]["n_debates"]})
        print("E1", E1[-1], f"{time.time()-t0:.0f}s", flush=True)
    out["E1_power"] = E1

    # E2: false positives with strong family fields; real teams and lab-sorted teams; agent-centring on/off
    def lab_sorted(debates):
        new = []
        for d in debates:
            ag = d["gov"] + d["opp"]
            ag = sorted(ag, key=lambda a: (lab_of[a] != "Anthropic", lab_of[a], a))
            k = len(d["gov"])
            new.append(dict(d, gov=ag[:k], opp=ag[k:]))
        return new
    E2 = []
    for teams_name, dd in (("real", debates), ("lab_sorted", lab_sorted(debates))):
        for f in (1.0, 3.0):
            for centre in (True, False):
                ps = []
                for _ in range(nsim):
                    X = simulate(st, dd, lab_of, rng, mu=0.0, f=f)
                    W = C.build_windows(X, st, dd, "deb", agent_centre=centre)
                    ps.append(C.static_tests(W, 1000, int(rng.integers(1e9)))["p_delta"])
                E2.append({"teams": teams_name, "f": f, "agent_centre": centre, "fpr": float(np.mean(np.array(ps) < 0.05))})
                print("E2", E2[-1], flush=True)
    out["E2_fpr"] = E2
    E2b = []
    for teams_name, dd in (("real", debates), ("lab_sorted", lab_sorted(debates))):
        for mu in (0.0, 0.5):
            rr = [run_all(simulate(st, dd, lab_of, rng, mu=mu, f=3.0), st, dd, lab_of, 300, ("pairfe",), int(rng.integers(1e9)))["pairfe"]
                  for _ in range(nsim // 3)]
            E2b.append({"teams": teams_name, "mu": mu, "f": 3.0, "rej_pairFE": float(np.mean([x["p_team_pairFE"] < 0.05 for x in rr])),
                        "mean_b": float(np.nanmean([x["b_team_pairFE"] for x in rr])), "switching_pairs": rr[0]["n_switching_pairs"],
                        "pairs": rr[0]["n_pairs"]})
            print("E2b", E2b[-1], flush=True)
    out["E2b_pairFE"] = E2b

    # E3: generic vs motion-specific
    E3 = []
    for mu, gen in ((0.0, 0.0), (0.0, 0.3), (0.2, 0.0), (0.2, 0.3)):
        rs = [run_all(simulate(st, debates, lab_of, rng, mu=mu, gen=gen), st, debates, lab_of, 1000, ("generic",), int(rng.integers(1e9)))
              for _ in range(nsim // 4)]
        E3.append({"mu": mu, "gen": gen,
                   "power_generic": float(np.mean([x["generic"]["p_generic_flip"] < 0.05 for x in rs])),
                   "power_specific": float(np.mean([x["generic"]["specific"]["p_delta"] < 0.05 for x in rs])),
                   "power_total": float(np.mean([x["static"]["p_delta"] < 0.05 for x in rs])),
                   "mean_ms_generic": float(np.mean([x["generic"]["ms_generic"] for x in rs]))})
        print("E3", E3[-1], flush=True)
    out["E3_generic"] = E3

    # E4: dynamics (staggered susceptibility, remanence, winner field)
    out["E4_dynamics"] = run_E4(st, debates, lab_of, rng, nsim)

    # E5: rotation-null calibration at mu = 0 and power at mu = 0.2
    E5 = []
    for mu in (0.0, 0.2):
        ps = []
        for _ in range(20 if QUICK else 60):
            X = simulate(st, debates, lab_of, rng, mu=mu)
            W = C.build_windows(X, st, debates, "deb")
            obs = C.static_tests(W, 500, 0)["delta"]
            nd, _ = L.rotation_null([{"agents": w["agents"], "V": w["V"], "eps": w["eps"]} for w in W], 200, int(rng.integers(1e9)))
            ps.append(L.p_upper(obs, nd))
        E5.append({"mu": mu, "rej_rate": float(np.mean(np.array(ps) < 0.05))})
        print("E5", E5[-1], flush=True)
    out["E5_rotation"] = E5

    # E6: semi-synthetic injection into real (structure-destroyed) statement noise
    Xr = real_noise_base()
    out["real_noise_per_dim_var"] = float(Xr.var(0).mean())
    E6 = []
    for mu in [0.0, 0.1, 0.2, 0.3, 0.5, 0.8]:
        rs = []
        for _ in range(nsim):
            X = inject(Xr, st, debates, rng, mu)
            rs.append(run_all(X, st, debates, lab_of, 1000, (), int(rng.integers(1e9)))["static"])
        E6.append({"mu": mu, "power_delta": float(np.mean([x["p_delta"] < 0.05 for x in rs])),
                   "power_ms": float(np.mean([x["p_ms"] < 0.05 for x in rs])),
                   "power_recovery": float(np.mean([x["p_recovered"] < 0.05 for x in rs])),
                   "mean_delta": float(np.mean([x["delta"] for x in rs])), "sd_delta": float(np.std([x["delta"] for x in rs])),
                   "mean_ms": float(np.mean([x["ms"] for x in rs])), "mean_recovered": float(np.mean([x["recovered"] for x in rs]))})
        print("E6", E6[-1], flush=True)
    out["E6_semisynthetic"] = E6
    out["runtime_s"] = time.time() - t0
    (DATA / "synthetic").mkdir(parents=True, exist_ok=True)
    (DATA / "synthetic/synthetic.json").write_text(json.dumps(out, indent=1))
    plot(out)
    print(f"done {time.time()-t0:.0f}s")


def plot(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.6))
    E1 = out["E1_power"]
    mus = [e["mu"] for e in E1]
    ax[0].plot(mus, [e["power_delta"] for e in E1], "o-", color="#1f5f8b", label="Δ (within − cross cos)")
    ax[0].plot(mus, [e["power_ms"] for e in E1], "s--", color="#c0504d", label="LOAO staggered m_s")
    ax[0].plot(mus, [e["power_recovery"] for e in E1], "^:", color="#4f7f3f", label="exact team recovery")
    ax[0].axhline(0.05, color="gray", lw=0.8)
    ax[0].set_xlabel("staggered field μ (per-dim noise units)"); ax[0].set_ylabel("power (α = 0.05)")
    ax[0].set_title("E1 power at G12 design"); ax[0].legend(fontsize=7, frameon=False)
    ax[1].errorbar(mus, [e["mean_delta"] for e in E1], yerr=[e["sd_delta"] for e in E1], fmt="o-", color="#1f5f8b")
    ax[1].set_xlabel("μ"); ax[1].set_ylabel("pooled Δ (mean ± sd)"); ax[1].set_title("E1 calibration curve Δ(μ)")
    E4 = [e for e in out["E4_dynamics"] if e["w"] == 0.0]
    for eta, mk in ((0.5, "o-"), (1.5, "s--")):
        sub = [e for e in E4 if e["eta"] == eta]
        ax[2].plot([e["K_s"] for e in sub], [e["mean_rho"] for e in sub], mk, label=f"ρ(m_A,m_B), η={eta}")
        ax[2].plot([e["K_s"] for e in sub], [e["mean_remanence"] for e in sub], mk, alpha=0.5, label=f"remanence, η={eta}")
    ax[2].axhline(0, color="gray", lw=0.8)
    ax[2].set_xlabel("staggered loop gain K_s"); ax[2].set_title("E4 dynamics: fluctuation & remanence")
    ax[2].legend(fontsize=7, frameon=False)
    E6 = out.get("E6_semisynthetic", [])
    if E6:
        m6 = [e["mu"] for e in E6]
        ax[3].plot(m6, [e["power_delta"] for e in E6], "o-", color="#1f5f8b", label="Δ")
        ax[3].plot(m6, [e["power_ms"] for e in E6], "s--", color="#c0504d", label="LOAO m_s")
        ax[3].plot(m6, [e["power_recovery"] for e in E6], "^:", color="#4f7f3f", label="exact recovery")
        ax[3].axhline(0.05, color="gray", lw=0.8)
        ax[3].set_xlabel("injected μ (whitened units)"); ax[3].set_ylabel("power")
        ax[3].set_title("E6 injection into real #12 noise"); ax[3].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "synthetic_validation.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
