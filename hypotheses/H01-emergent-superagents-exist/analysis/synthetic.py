"""H01 synthetic validation (faithfulness axis F), run BEFORE the real-data tests.

World (village-like sampling): a pool of 30 agents with persistent style fields h_i; 11 periods per world (8 two-room
periods N = 14 in rooms of 5 + 9, T = 5 days; 2 one-room periods N = 20, T = 5; one long period N = 25 in rooms of
2 + 23, T = 14, like #focus). Agent-day latent direction (32-d):
    u_i(t) = normalize(a_g g_p + a_h h_i + a_tau tau_ip + a_rho rho_room + a_xi xi_i(t)
                       + J * sum_j (E_{i<-j}(t) / 20) xi_j(t))
g_p = period goal field, tau_ip = agent's own project in the period, rho_room = room-specific field (e.g. room
kickoffs), xi = daily fluctuation, E_{i<-j}(t) = j's chat messages that day if i and j share a room (else 0).
Statements ~ vMF(u_i(t), kappa_s) with A_32(kappa_s) = 0.62; statements per agent-day NegBin (median ~36, heavy tail),
60% of them chat -> exposure is correlated with statement counts (the verbosity confound is built in).
The observed goal vector g-hat has cos 0.6 with the true g_p (goal-text embeddings are imperfect); the observed room
field has cos 0.6 with rho_room. Calibration from generic instrument statistics of the real scheme (no outcome
statistics): agent-day statement counts, within-agent-day resultant ~0.63, agent-period resultant ~0.85.

Tests
  V1  P5/P6 decomposition: exposure slope (pair + day FE) vs planted J; size at J = 0 for the full-vector estimator
      (with log n controls) and the rarefied estimator (M = 8 statements per agent-day); RE summary over periods;
      rotation and day-shuffle nulls; within-room minus cross-room residual with and without the room field removed.
      P5 R^2 (estimated fields) vs oracle R^2 (true fields) vs rotation null.
  V2  P1 semantic-entropy room-vs-random test: size (no room structure) and power (room field, coupling).
  V3  P9 mean-field O(32) fit on Gibbs samples of the mean-field model (known bJ0, bh), N and T village-like,
      statement noise on top; plus a common day-varying field without coupling (expected upward bias).

Usage: uv run python hypotheses/H01-emergent-superagents-exist/analysis/synthetic.py [--fast]
Writes data/processed/H01-emergent-superagents-exist/synthetic_validation.json and figures/synthetic_validation.pdf.
"""
from __future__ import annotations

import json
import zlib
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h01lib import (Unit, A_n, fe_slope, fe_slope_fast, js_distance, kappa_for_A, mf_fit, pair_table,  # noqa: E402,F401
                    partition_test, r2_field, random_effects, rarefied_counts, rarefied_vectors, rotate_agents,
                    sample_vmf, shuffle_days, unit)
from h01common import OUT, FIG, SEED, kmeans  # noqa: E402

import numpy as np  # noqa: E402

FAST = "--fast" in sys.argv
NREP = 8 if FAST else 24
n = 32
KS = kappa_for_A(0.62, n)
PERIODS = [(14, (5, 9), 5)] * 8 + [(20, (20,), 5)] * 2 + [(25, (2, 23), 14)]
BASE = dict(a_g=0.5, a_h=0.6, a_tau=0.6, a_rho=0.3, a_xi=0.7, J=0.0, gcos=0.6)


def rand_unit(rng, k=None):
    x = rng.standard_normal((k or 1, n))
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    return x if k else x[0]


def noisy_copy(v, c, rng):
    """unit vector with cosine c to v."""
    w = rng.standard_normal(n); w -= (w @ v) * v; w /= np.linalg.norm(w)
    return c * v + np.sqrt(1 - c ** 2) * w


def make_world(par, rng, periods=PERIODS):
    pool = 30
    H = rand_unit(rng, pool)
    mu_agent = np.exp(rng.normal(np.log(36), 0.6, pool))
    units, truth, all_U = [], [], []
    for p, (N, sizes, T) in enumerate(periods):
        ags = np.sort(rng.choice(pool, N, replace=False))
        rooms = np.repeat(np.arange(len(sizes)), sizes); rng.shuffle(rooms)
        g = rand_unit(rng); tau = rand_unit(rng, N); rho = rand_unit(rng, len(sizes))
        nst = np.maximum(3, rng.negative_binomial(2, 2 / (2 + mu_agent[ags][:, None] * np.exp(rng.normal(0, 0.3, (N, T)))), (N, T)))
        chat = rng.binomial(nst, 0.6)
        xi = rand_unit(rng, N * T).reshape(N, T, n)
        E = {}
        for t in range(T):
            for a in range(N):
                for b in range(N):
                    if a != b and rooms[a] == rooms[b]:
                        E[(t, ags[a], ags[b])] = int(chat[b, t])
        lat = np.zeros((N, T, n))
        for a in range(N):
            for t in range(T):
                c = par["a_g"] * g + par["a_h"] * H[ags[a]] + par["a_tau"] * tau[a] + par["a_rho"] * rho[rooms[a]] + par["a_xi"] * xi[a, t]
                if par["J"]:
                    for b in range(N):
                        if b != a and rooms[a] == rooms[b]:
                            c = c + par["J"] * chat[b, t] / 20 * xi[b, t]
                lat[a, t] = c / np.linalg.norm(c)
        Ulist, rows, A_, D_, R_, V_, Nn = [], [], [], [], [], [], []
        off = sum(len(x) for x in all_U)
        for a in range(N):
            for t in range(T):
                s = sample_vmf(np.repeat(lat[a, t][None], nst[a, t], 0), KS, rng)
                rows.append(np.arange(off, off + len(s))); off += len(s); Ulist.append(s)
                A_.append(ags[a]); D_.append(t); R_.append(rooms[a]); V_.append(unit(s.mean(0))); Nn.append(len(s))
        all_U.extend(Ulist)
        units.append(Unit(name=f"S{p}", agents=np.array(A_), day=np.array(D_), room=np.array(R_), V=np.array(V_),
                          nstmt=np.array(Nn), rows=rows, U=None, lab={}, E=E, ghat=noisy_copy(g, par["gcos"], rng), h={},
                          ghat_room={r: noisy_copy(rho[r], 0.6, rng) for r in range(len(sizes))}))
        truth.append({"g": g, "H": H, "rho": rho, "rooms": rooms, "ags": ags})
    U = np.concatenate(all_U)
    for u in units:
        u.U = U
    # cross-fitted h: mean of the agent's agent-day vectors in OTHER periods
    for pi, u in enumerate(units):
        for a in np.unique(u.agents):
            vs = [w.V[w.agents == a] for qi, w in enumerate(units) if qi != pi and (w.agents == a).any()]
            if vs:
                u.h[a] = unit(np.concatenate(vs).mean(0))
    return units, truth, U


def add_clusters(units, U, rng, k=40):
    C, lab, _ = kmeans(U.astype(np.float32), k, seed=int(rng.integers(1e9)), n_init=1, max_iter=50)
    for u in units:
        u.lab[k] = lab


# ============================================================================ V1 decomposition
def v1_world(args):
    par, seed, do_nulls = args
    rng = np.random.default_rng(seed)
    units, truth, U = make_world(par, rng)
    res = {"full": [], "rare": [], "room_diff": [], "room_diff_rf": [], "r2": [], "r2_oracle": [], "r2_rot": [],
           "lag": [], "dir": [], "lag_joint": [], "same_joint": []}
    nulls = {"rot": [], "shuf": []}
    for u, tr in zip(units, truth):
        pt = pair_table(u)
        if pt is None:
            continue
        x = np.log1p(pt["Eij"] + pt["Eji"])
        pt["x"] = x; pt["lni"] = np.log(pt["ni"]); pt["lnj"] = np.log(pt["nj"])
        f = fe_slope(pt, ["x"], covars=("lni", "lnj"))
        Vr = rarefied_vectors(u, 8, 10, rng)
        ptr = pair_table(u, n_min=8, Vover=Vr)
        ptr["x"] = np.log1p(ptr["Eij"] + ptr["Eji"])
        fr = fe_slope(ptr, ["x"])
        if f is not None:
            res["full"].append((float(f["b"][0]), float(f["se"][0])))
        if fr is not None:
            res["rare"].append((float(fr["b"][0]), float(fr["se"][0])))
            ptr["x1"] = np.log1p(ptr["Eij"]); ptr["x2"] = np.log1p(ptr["Eji"])
            fd = fe_slope(ptr, ["x1", "x2"])
            if fd is not None:
                res["dir"].append([float(fd["b"][0]), float(fd["se"][0]), float(fd["b"][1]), float(fd["se"][1])])
            lagm = ptr["Eij_lag"] >= 0
            if lagm.sum() > 20:
                ptr["xl"] = np.log1p(np.clip(ptr["Eij_lag"], 0, None) + np.clip(ptr["Eji_lag"], 0, None))
                fl = fe_slope(ptr, ["xl"], mask=lagm)
                if fl is not None:
                    res["lag"].append((float(fl["b"][0]), float(fl["se"][0])))
                fj = fe_slope(ptr, ["x", "xl"], mask=lagm)
                if fj is not None:
                    res["lag_joint"].append((float(fj["b"][1]), float(fj["se"][1])))
                    res["same_joint"].append((float(fj["b"][0]), float(fj["se"][0])))
        if len(np.unique(u.room)) > 1:
            res["room_diff"].append(float(ptr["r"][ptr["same"]].mean() - ptr["r"][~ptr["same"]].mean()))
            ptf = pair_table(u, n_min=8, Vover=Vr, use_room=True)
            res["room_diff_rf"].append(float(ptf["r"][ptf["same"]].mean() - ptf["r"][~ptf["same"]].mean()))
        res["r2"].append(r2_field(pt))
        # oracle: true g and true h
        uo = Unit(**{**u.__dict__}); uo.ghat = tr["g"]; uo.h = {a: tr["H"][a] for a in np.unique(u.agents)}
        res["r2_oracle"].append(r2_field(pair_table(uo)))
        Vrot, hrot, _ = rotate_agents(u, rng)
        res["r2_rot"].append(r2_field(pair_table(u, Vover=Vrot, hover=hrot)))
        if do_nulls and fr is not None:
            rb, sb = [], []
            for _ in range(40):
                _, hrot, Vrr = rotate_agents(u, rng, extra=Vr)
                p0 = pair_table(u, n_min=8, Vover=Vrr, hover=hrot)
                rb.append(float(fe_slope_fast(fr, p0["r"])[0]) if len(p0["r"]) == len(ptr["r"]) else np.nan)
                _, Vss = shuffle_days(u, rng, extra=Vr, n_min=8)
                p1 = pair_table(u, n_min=8, Vover=Vss)
                sb.append(float(fe_slope_fast(fr, p1["r"])[0]) if len(p1["r"]) == len(ptr["r"]) else np.nan)
            b0 = float(fr["b"][0])
            nulls["rot"].append(float((1 + np.nansum(np.array(rb) >= b0)) / (1 + np.isfinite(rb).sum())))
            nulls["shuf"].append(float((1 + np.nansum(np.array(sb) >= b0)) / (1 + np.isfinite(sb).sum())))
    out = {}
    for k in ("full", "rare", "lag", "lag_joint", "same_joint"):
        arr = np.array(res[k])
        re = random_effects(arr[:, 0], arr[:, 1])
        out[k] = {"b_mean": float(arr[:, 0].mean()), "frac_pos": float((arr[:, 0] > 0).mean()),
                  "frac_p01": float(np.mean(arr[:, 0] / arr[:, 1] > 2.326)), "re_mu": re["mu"], "re_p_one": re["p_one"],
                  "P6_pass": bool((arr[:, 0] > 0).mean() >= 2 / 3 and re["p_one"] < 0.005)}
    d = np.array(res["dir"])
    r1 = random_effects(d[:, 0], d[:, 1]); r2 = random_effects(d[:, 2], d[:, 3])
    out["dir"] = {"re1": r1["mu"], "p1": r1["p_one"], "re2": r2["mu"], "p2": r2["p_one"],
                  "both_p01": bool(r1["p_one"] < 0.005 and r2["p_one"] < 0.005)}
    out["room_diff"] = float(np.mean(res["room_diff"])); out["room_diff_rf"] = float(np.mean(res["room_diff_rf"]))
    out["r2"] = float(np.mean(res["r2"])); out["r2_oracle"] = float(np.mean(res["r2_oracle"])); out["r2_rot"] = float(np.mean(res["r2_rot"]))
    if do_nulls:
        out["p_rot_frac01"] = float(np.mean(np.array(nulls["rot"]) < 0.05))
        out["p_shuf_frac05"] = float(np.mean(np.array(nulls["shuf"]) < 0.05))
    return out


# ============================================================================ V2 P1 size/power
def v2_world(args):
    par, seed = args
    rng = np.random.default_rng(seed)
    periods = [(14, (5, 9), 5)] * 6
    units, truth, U = make_world(par, rng, periods)
    add_clusters(units, U, rng)
    days = []
    for u in units:
        for t in range(int(u.day.max()) + 1):
            idx = np.where((u.day == t) & (u.nstmt >= 8))[0]
            labs = u.room[idx]
            if len(idx) < 4 or (np.bincount(labs) >= 2).sum() < 2:
                continue
            cnt = rarefied_counts(u, idx, 40, 8, 20, rng)
            days.append(partition_test(cnt, labs, 300, rng))
    dH = np.array([d["dH"] for d in days]); p = np.array([d["p"] for d in days])
    return {"n_days": len(days), "frac_dH_neg": float((dH < 0).mean()), "median_dH": float(np.median(dH)),
            "frac_p05": float((p < 0.05).mean()), "P1_pass": bool((dH < 0).mean() >= 0.6 and np.median(dH) <= -0.1),
            "P1_pass_weak": bool((dH < 0).mean() >= 0.6)}


# ============================================================================ V3 mean-field
def mf_gibbs(N, T, bJ, bh, rng, h_agent=1.0, day_field=0.0, nst_mean=36, sweeps=25, burn=150):
    g = np.zeros(n); g[0] = 1
    hi = rand_unit(rng, N) * h_agent
    S = rand_unit(rng, N)
    days = []
    for it in range(burn + T * sweeps):
        if it >= burn and (it - burn) % sweeps == 0:
            fd = rand_unit(rng) * day_field
        else:
            fd = fd if it >= burn else np.zeros(n)
        tot = S.sum(0)
        for i in range(N):
            th = bJ / N * (tot - S[i]) + bh * g + hi[i] + fd
            k = np.linalg.norm(th)
            new = sample_vmf(th[None] / max(k, 1e-12), k, rng)[0]
            tot += new - S[i]; S[i] = new
        if it >= burn and (it - burn) % sweeps == sweeps - 1:
            days.append(S.copy())
    Ul, rows, A_, D_, V_, Nn = [], [], [], [], [], []
    off = 0
    for t, St in enumerate(days):
        for i in range(N):
            m = max(4, rng.negative_binomial(2, 2 / (2 + nst_mean)))
            s = sample_vmf(np.repeat(St[i][None], m, 0), KS, rng)
            Ul.append(s); rows.append(np.arange(off, off + m)); off += m
            A_.append(i); D_.append(t); V_.append(unit(s.mean(0))); Nn.append(m)
    return Unit(name="mf", agents=np.array(A_), day=np.array(D_), room=np.zeros(len(A_), int), V=np.array(V_),
                nstmt=np.array(Nn), rows=rows, U=np.concatenate(Ul), lab={}, E={}, ghat=g, h={})


def v3_task(args):
    N, T, bJn, bh, day_field, seed = args
    rng = np.random.default_rng(seed)
    u = mf_gibbs(N, T, bJn * n, bh, rng, day_field=day_field)
    f = mf_fit(u, rng)
    # latent (noise-free) estimate for comparison: use statements' latent directly is not stored; use same unit
    return {"N": N, "T": T, "bJn": bJn, "bh": bh, "day_field": day_field,
            "bJn_hat": None if f is None else f["bJ_over_n"], "bh_hat": None if f is None else f["bh"],
            "m": None if f is None else f["m_g"], "R": None if f is None else f["R"]}


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    out = {"params": {"base": BASE, "periods": PERIODS, "kappa_s": KS, "nrep": NREP, "n": n}}
    # V1
    v1 = {}
    configs = {"J0": dict(BASE, J=0.0), "J0_noroom": dict(BASE, J=0.0, a_rho=0.0), "J0.05": dict(BASE, J=0.05),
               "J0.1": dict(BASE, J=0.1), "J0.2": dict(BASE, J=0.2), "J0.4": dict(BASE, J=0.4),
               "nofield_J0": dict(BASE, a_g=0.0, a_h=0.0, J=0.0), "nofield_J0.2": dict(BASE, a_g=0.0, a_h=0.0, J=0.2)}
    with Pool(4) as pool:
        for name, par in configs.items():
            reps = pool.map(v1_world, [(par, SEED + 1000 * i + zlib.crc32(name.encode()) % 997, i < (4 if FAST else 8)) for i in range(NREP)])
            agg = {}
            for key in ("full", "rare", "lag", "lag_joint", "same_joint"):
                agg[key] = {m: float(np.mean([r[key][m] for r in reps])) for m in reps[0][key]}
            agg["dir_both_p01"] = float(np.mean([r["dir"]["both_p01"] for r in reps]))
            for m in ("room_diff", "room_diff_rf", "r2", "r2_oracle", "r2_rot"):
                agg[m] = float(np.mean([r[m] for r in reps])); agg[m + "_sd"] = float(np.std([r[m] for r in reps]))
            nn = [r for r in reps if "p_rot_frac01" in r]
            agg["rot_null_reject05"] = float(np.mean([r["p_rot_frac01"] for r in nn]))
            agg["shuf_null_reject05"] = float(np.mean([r["p_shuf_frac05"] for r in nn]))
            v1[name] = agg
            print("V1", name, json.dumps({k: (v if not isinstance(v, dict) else {kk: round(vv, 4) for kk, vv in v.items()}) for k, v in agg.items()}), f"{time.time()-t0:.0f}s", flush=True)
        out["V1_decomposition"] = v1
        # V2
        v2 = {}
        for name, par in {"null": dict(BASE, a_rho=0.0, J=0.0), "room_field_0.15": dict(BASE, a_rho=0.15, J=0.0),
                          "room_field_0.3": dict(BASE, a_rho=0.3, J=0.0), "coupling_0.1": dict(BASE, a_rho=0.0, J=0.1),
                          "coupling_0.2": dict(BASE, a_rho=0.0, J=0.2)}.items():
            reps = pool.map(v2_world, [(par, SEED + 7000 + 31 * i + zlib.crc32(name.encode()) % 991) for i in range(NREP)])
            v2[name] = {m: float(np.mean([r[m] for r in reps])) for m in reps[0]}
            print("V2", name, {k: round(v, 3) for k, v in v2[name].items()}, f"{time.time()-t0:.0f}s", flush=True)
        out["V2_P1"] = v2
        # V3
        tasks = []
        for N, T in ((13, 5), (20, 15)):
            for bJn in (0.0, 0.25, 0.5, 0.75):
                for bh in (2.0, 8.0):
                    for i in range(NREP // 2):
                        tasks.append((N, T, bJn, bh, 0.0, SEED + 50000 + len(tasks)))
            for i in range(NREP // 2):
                tasks.append((N, T, 0.0, 2.0, 1.5, SEED + 50000 + len(tasks)))
        res = pool.map(v3_task, tasks)
    v3 = {}
    for r in res:
        key = f"N{r['N']}_T{r['T']}_bJn{r['bJn']}_bh{r['bh']}_df{r['day_field']}"
        v3.setdefault(key, []).append(r)
    out["V3_MF"] = {k: {"bJn_true": v[0]["bJn"], "bh_true": v[0]["bh"], "day_field": v[0]["day_field"],
                        "bJn_hat_median": float(np.nanmedian([x["bJn_hat"] for x in v if x["bJn_hat"] is not None])),
                        "bJn_hat_q10": float(np.nanquantile([x["bJn_hat"] for x in v if x["bJn_hat"] is not None], 0.1)),
                        "bJn_hat_q90": float(np.nanquantile([x["bJn_hat"] for x in v if x["bJn_hat"] is not None], 0.9)),
                        "bh_hat_median": float(np.nanmedian([x["bh_hat"] for x in v if x["bh_hat"] is not None])),
                        "frac_below_half": float(np.mean([x["bJn_hat"] < 0.5 for x in v if x["bJn_hat"] is not None])),
                        "m_median": float(np.nanmedian([x["m"] for x in v if x["m"] is not None]))} for k, v in v3.items()}
    for k, v in out["V3_MF"].items():
        print("V3", k, {kk: round(vv, 3) if isinstance(vv, float) else vv for kk, vv in v.items()})
    (OUT / "synthetic_validation.json").write_text(json.dumps(out, indent=1, default=float))
    print("done", f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
