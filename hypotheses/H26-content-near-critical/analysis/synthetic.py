"""H26 synthetic validation (faithfulness axis F), run BEFORE any real-data H26 statistic.

World: rooms of soft-spin agents in the 32-d whitened content space plus a scalar activity channel, sampled like
the village (30-min windows, W per day, T days, Poisson statements per agent-window, 30 one-minute activity bins).

Latent kinetics per 30-min window t (agent i in room r, m_{r,-i} = mean of i's room-mates):
    z_i(t+1) = phi z_i(t) + (1 - phi) [ J m_{r,-i}(t) + F_i(t) ] + sqrt(1 - phi^2) L xi_i(t)
L L^T = anisotropic fluctuation shape (eigenvalues ~ exp(-k/k0), participation ratio ~ 8 of 32 dims, the H20
lesson). F = drives:
    G_d     global day drive (all rooms), drawn per day in the same anisotropic shape        (sigma_G)
    H_{r,d} room-day drive: random daily direction in the anisotropic shape, or a stable 3-d room subspace (sigma_R)
    K(t)    kickoff relaxation A_k exp(-t/tau_k) along a common 3-d kickoff subspace
    TOD(w)  time-of-day profile along 2 common directions
    E_{r,t} exogenous pulses (rate per room-window, 2-window duration); their *measured* direction has cos c_meas
Statements: u = unit(static_i + goal + z_i(t) + eps), eps ~ N(0, s_eps^2 I) (calibrated to the generic instrument
statistics in the card: within-agent-day resultant ~0.6). Activity: y_i(t) with the same kinetics and its own
global/TOD/pulse drives; minute states ~ Bernoulli(clip(0.5 + y, 0.02, 0.98)).

Truth: g_true at each resolution = the loop gain of the latent states themselves (no sampling noise, no drives),
from a twin run with the same coupling and noise but all drives off.

Estimators: H01's P9 (h01lib.mf_fit, imported read-only) and the H26 ladder L0-L4 (h26lib), content and activity,
day and w30. Nulls: N2 room permutation (size), bootstrap coverage.

Usage: uv run python hypotheses/H26-content-near-critical/analysis/synthetic.py [--fast] [--calibrate]
Writes data/processed/H26-content-near-critical/synthetic/*.json and figures/synthetic_validation.pdf.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h26lib as L  # noqa: E402  (sets thread caps to 2 before numpy)

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "hypotheses/H01-emergent-superagents-exist/analysis"))
from h01lib import Unit, mf_fit  # noqa: E402

import numpy as np  # noqa: E402

OUT = ROOT / "data/processed/H26-content-near-critical/synthetic"
FIG = HERE.parent / "figures"
SEED = 20261004
n = 32
FAST = "--fast" in sys.argv
NREP = 6 if FAST else 24

BASE = dict(N=14, sizes=(7, 7), T=5, W=8, phi=0.85, J=0.0, k0=4.0, vz=0.4, s_eps2=2.4 / 32, a_static=1.0,
            rate=4.5, sigma_G=0.0, sigma_R=0.0, room_stable=False, A_k=0.0, tau_k=2.0, A_tod=0.0,
            exo_rate=0.0, A_e=0.0, c_meas=0.8, ghat_cos=0.6,
            # activity channel
            Ja=None, vy=0.04, sigma_Ga=0.0, sigma_Ra=0.0, A_toda=0.0, A_ea=0.0, NS=3)


def rand_unit(rng, k):
    x = rng.standard_normal((k, n)); return x / np.linalg.norm(x, axis=1, keepdims=True)


def noisy_copy(v, c, rng):
    w = rng.standard_normal(n); w -= (w @ v) * v; w /= np.linalg.norm(w)
    return c * v + np.sqrt(1 - c ** 2) * w


def shape(rng, k0):
    lam = np.exp(-np.arange(n) / k0); lam /= lam.sum()
    Q, _ = np.linalg.qr(rng.standard_normal((n, n)))
    return Q * np.sqrt(lam)  # n x n; L @ xi has covariance Q diag(lam) Q^T (trace 1)


def simulate(p, rng, drives=True):
    """Return latent content z (T*W, N, n), latent activity y (T*W, N), and the drive bookkeeping."""
    N, T, W = p["N"], p["T"], p["W"]
    rooms = np.repeat(np.arange(len(p["sizes"])), p["sizes"])
    Lc = shape(rng, p["k0"]) * np.sqrt(p["vz"])
    nT = T * W
    phi, J = p["phi"], p["J"]
    Ja = J if p["Ja"] is None else p["Ja"]
    R = len(p["sizes"])
    # drives (drawn even when switched off so twin runs share the noise stream)
    G = (Lc @ rng.standard_normal((n, T))).T * p["sigma_G"]                 # (T, n)
    Ur = [np.linalg.qr(rng.standard_normal((n, 3)))[0].T for _ in range(R)]  # stable 3-d room subspaces
    Hrand = np.einsum("ij,rdj->rdi", Lc, rng.standard_normal((R, T, n))) * p["sigma_R"]
    Hstab = np.stack([np.stack([Ur[r].T @ rng.standard_normal(3) for _ in range(T)]) for r in range(R)]) \
        * p["sigma_R"] * np.sqrt(p["vz"] / 3)
    H = Hstab if p["room_stable"] else Hrand                                # (R, T, n)
    kdir = np.linalg.qr(rng.standard_normal((n, 3)))[0].T
    tdir = np.linalg.qr(rng.standard_normal((n, 2)))[0].T
    tod = np.stack([np.cos(2 * np.pi * np.arange(W) / W), np.sin(2 * np.pi * np.arange(W) / W)], 1)
    pulses = rng.random((nT, R)) < p["exo_rate"]
    pdirs = rand_unit(rng, nT * R).reshape(nT, R, n)
    pmeas = np.stack([np.stack([noisy_copy(pdirs[t, r], p["c_meas"], rng) for r in range(R)]) for t in range(nT)])
    Ga = rng.standard_normal(T) * p["sigma_Ga"]; Ra = rng.standard_normal((R, T)) * p["sigma_Ra"]
    xi = rng.standard_normal((nT, N, n)); xa = rng.standard_normal((nT, N))
    z = np.zeros((nT, N, n)); y = np.zeros((nT, N))
    zc = np.zeros((N, n)); yc = np.zeros(N)
    on = 1.0 if drives else 0.0
    for t in range(nT):
        d, w = divmod(t, W)
        F = np.zeros((N, n)); Fa = np.zeros(N)
        F += G[d]; F += H[rooms, d]
        F += p["A_k"] * np.exp(-(t / W) / p["tau_k"]) * kdir.sum(0) / np.sqrt(3)
        F += p["A_tod"] * (tod[w] @ tdir)
        Fa += Ga[d] + Ra[rooms, d] + p["A_toda"] * tod[w, 0]
        for tt in (t, t - 1):
            if tt >= 0:
                for r in range(R):
                    if pulses[tt, r]:
                        F[rooms == r] += p["A_e"] * pdirs[tt, r]; Fa[rooms == r] += p["A_ea"]
        msum = np.zeros((R, n)); cnt = np.bincount(rooms, minlength=R)
        np.add.at(msum, rooms, zc)
        m_oth = (msum[rooms] - zc) / np.maximum(cnt[rooms] - 1, 1)[:, None]
        asum = np.bincount(rooms, weights=yc, minlength=R)
        a_oth = (asum[rooms] - yc) / np.maximum(cnt[rooms] - 1, 1)
        zc = phi * zc + (1 - phi) * (J * m_oth + on * F) + np.sqrt(1 - phi ** 2) * (xi[t] @ Lc.T)
        yc = phi * yc + (1 - phi) * (Ja * a_oth + on * Fa) + np.sqrt(1 - phi ** 2) * np.sqrt(p["vy"]) * xa[t]
        z[t] = zc; y[t] = yc
    info = dict(rooms=rooms, kdir=kdir, pulses=pulses, pmeas=pmeas)
    return z, y, info


def observe(p, z, y, info, rng):
    """Statements and minute-level activity -> Panels (content/activity x day/w30) and an H01 Unit."""
    N, T, W, NS = p["N"], p["T"], p["W"], p["NS"]
    rooms = info["rooms"]
    goal = rand_unit(rng, 1)[0]
    stat = rand_unit(rng, N) * 0.8
    rate_i = np.exp(rng.normal(np.log(p["rate"]), 0.5, N))
    cnt = rng.poisson(rate_i[None, :] * np.exp(rng.normal(0, 0.3, (T * W, N))))
    U, own = [], []
    for t in range(T * W):
        for i in range(N):
            k = cnt[t, i]
            if k == 0:
                continue
            base = p["a_static"] * (stat[i] + goal * 0.6) + z[t, i]
            u = base[None, :] + rng.standard_normal((k, n)) * np.sqrt(p["s_eps2"])
            u /= np.linalg.norm(u, axis=1, keepdims=True)
            U.append(u); own += [(t, i)] * k
    U = np.vstack(U); own = np.array(own)
    # static field directions (measured): noisy goal, noisy kickoff subspace, first-hour PCs
    ghat = noisy_copy(goal, p["ghat_cos"], rng)
    kmeas = np.stack([noisy_copy(v, 0.6, rng) for v in info["kdir"]])
    first = U[own[:, 0] < 2]
    pcs = np.linalg.svd(first - first.mean(0), full_matrices=False)[2][:3] if len(first) > 5 else np.zeros((0, n))
    static = L.orthobasis(np.vstack([ghat, kmeas, pcs]))
    # minute activity
    pa = np.clip(0.5 + y, 0.02, 0.98)
    mins = rng.random((T * W, N, 30)) < pa[..., None]
    panels = {}
    for res in ("day", "w30", "wd"):
        rows = []
        for t in range(T * W):
            d, w = divmod(t, W)
            for i in range(N):
                rows.append((t, d, w, i))
        rows = np.array(rows)
        slot = rows[:, 1] if res == "day" else rows[:, 0]
        key = slot * N + rows[:, 3]
        uk, inv = np.unique(key, return_inverse=True)
        sl, ag = uk // N, uk % N
        nobs = len(uk)
        day = sl if res == "day" else sl // W
        wod = np.zeros_like(sl) if res == "day" else sl % W
        # content
        skey = (own[:, 0] // W if res == "day" else own[:, 0]) * N + own[:, 1]
        pos = np.searchsorted(uk, skey)
        X = np.full((nobs, n), np.nan); A = np.full((nobs, NS, n), np.nan); B = np.full((nobs, NS, n), np.nan)
        order = np.argsort(pos, kind="stable")
        ps = pos[order]
        starts = np.r_[0, np.flatnonzero(np.diff(ps)) + 1, len(ps)]
        rows_of = {}
        for k in range(len(starts) - 1):
            ix = order[starts[k]:starts[k + 1]]
            o = ps[starts[k]]
            rows_of[o] = ix
            X[o] = U[ix].mean(0)
            if len(ix) >= 2:
                for s in range(NS):
                    pp = rng.permutation(ix); h = len(pp) // 2
                    A[o, s] = U[pp[:h]].mean(0); B[o, s] = U[pp[h:]].mean(0)
        grp = day * N + ag if res == "wd" else ag
        exo = {}
        R = len(p["sizes"])
        for s_ in np.unique(sl):
            dirs = []
            ts = range(s_ * W, (s_ + 1) * W) if res == "day" else (s_, s_ - 1, s_ - 2, s_ - 3)
            for tt in ts:
                if 0 <= tt < T * W:
                    for r in range(R):
                        if info["pulses"][tt, r]:
                            dirs.append(info["pmeas"][tt, r])
            exo[int(s_)] = L.orthobasis(np.array(dirs)) if dirs else None
        Pc = L.Panel(agent=ag, t=sl, day=day, wod=wod, room=rooms[ag], X=X, A=A, B=B, grp=grp, static=static,
                     exo=exo, res=res)
        # activity
        Xa = np.zeros((nobs, 1)); Aa = np.zeros((nobs, NS, 1)); Ba = np.zeros((nobs, NS, 1))
        Zc = np.zeros((nobs, 1))
        for o in range(nobs):
            ts = np.arange(sl[o] * W, (sl[o] + 1) * W) if res == "day" else np.array([sl[o]])
            mm = mins[ts, ag[o]].ravel()
            Xa[o, 0] = mm.mean()
            for s in range(NS):
                pp = rng.permutation(len(mm)); h = len(mm) // 2
                Aa[o, s, 0] = mm[pp[:h]].mean(); Ba[o, s, 0] = mm[pp[h:]].mean()
            r = rooms[ag[o]]
            tz = list(ts) + ([] if res == "day" else [ts[0] - 1, ts[0] - 2, ts[0] - 3])
            Zc[o, 0] = sum(info["pulses"][tt, r] for tt in tz if 0 <= tt < T * W)
        Pa = L.Panel(agent=ag, t=sl, day=day, wod=wod, room=rooms[ag], X=Xa, A=Aa, B=Ba, grp=grp, Z=Zc, res=res)
        panels[("c", res)] = Pc; panels[("a", res)] = Pa
        if res == "day":
            # H01 Unit: unit-normalized agent-day vectors, statement rows
            okd = np.isfinite(X).all(1)
            V = X[okd] / np.linalg.norm(X[okd], axis=1, keepdims=True)
            unitobj = Unit(name="syn", agents=ag[okd], day=day[okd], room=rooms[ag[okd]], V=V,
                           nstmt=np.array([len(rows_of[o]) for o in np.flatnonzero(okd)]),
                           rows=[rows_of[o] for o in np.flatnonzero(okd)], U=U, lab={}, E={}, ghat=ghat, h={})
            panels["h01"] = unitobj
    return panels


def truth(p, z, y):
    """Latent loop gains (no sampling noise) at day and w30 resolution, from the drive-free twin."""
    N, T, W = p["N"], p["T"], p["W"]
    rooms = np.repeat(np.arange(len(p["sizes"])), p["sizes"])
    out = {}
    for ch, S in (("c", z), ("a", y[..., None])):
        for res in ("day", "w30", "wd"):
            if res == "day":
                M = S.reshape(T, W, N, -1).mean(1)          # (T, N, d)
                sl = np.repeat(np.arange(T), N); ag = np.tile(np.arange(N), T); grp = ag; day = sl
                wod = np.zeros_like(sl)
            else:
                M = S                                        # (T*W, N, d)
                sl = np.repeat(np.arange(T * W), N); ag = np.tile(np.arange(N), T * W)
                day = sl // W; grp = day * N + ag if res == "wd" else ag; wod = sl % W
            X = M.reshape(-1, M.shape[-1])
            P = L.Panel(agent=ag, t=sl, day=day, wod=wod, room=rooms[ag], X=X, A=X[:, None], B=X[:, None], grp=grp,
                        res=res)
            _, g, _ = L.run_level(P, 0)
            out[f"{ch}_{res}"] = {"g_room": g["g_room"], "g_ex": g["g_ex"], "g_all": g["g_all"], "rho_w": g["rho_w"]}
    return out


_TRUTH = {}


def truth_pop(p, T_long=120):
    """Population latent gains: drive-free run of T_long days with the same coupling, kinetics and sizes."""
    key = (p["J"], p["Ja"], p["N"], tuple(p["sizes"]), p["W"], p["phi"], p["k0"])
    if key not in _TRUTH:
        q = {**p, "T": T_long}
        z0, y0, _ = simulate(q, np.random.default_rng(12345), drives=False)
        _TRUTH[key] = truth(q, z0, y0)
    return _TRUTH[key]


def estimate(panels, rng, do_null=False, do_boot=False):
    res = {}
    for (ch, r), P in [(k, v) for k, v in panels.items() if k != "h01"]:
        levels = (0, 1, 2, 4) if ch == "c" else (0, 2, 4)
        for lv in levels:
            C, g, _ = L.run_level(P, lv)
            key = f"{ch}_{r}_L{lv}"
            res[key] = {k: g[k] for k in ("g_all", "g_room", "g_ex", "rho_w", "rho_c", "rho_ex", "Nr", "Nall")}
            if lv == 2 and do_boot:
                bs = L.bootstrap(C, B=200, rng=rng, keys=("g_ex", "g_room"))
                res[key]["ci_g_ex"] = L.ci(bs["g_ex"]); res[key]["ci_g_room"] = L.ci(bs["g_room"])
            if lv == 2 and do_null and len(np.unique(P.room)) > 1:
                dX, dA, dB, okX, okS = L.deviations(P, 2)
                nul = []
                for _ in range(40):
                    room2 = L.permute_rooms(P, rng)
                    nul.append(L.gains(L.contributions(P, dX, dA, dB, okX, okS, room=room2))["rho_ex"])
                res[key]["p_room_perm"] = float((1 + np.sum(np.array(nul) >= g["rho_ex"])) / (1 + len(nul)))
    mf = mf_fit(panels["h01"], rng)
    res["h01_bJ_over_n"] = None if mf is None else mf["bJ_over_n"]
    res["h01_R"] = None if mf is None else mf["R"]
    return res


SCEN = {
    "S0_null": {},
    "S1_global": dict(sigma_G=0.4),
    "S2_global+room": dict(sigma_G=0.4, sigma_R=0.6),
    "S3_global+room_stable": dict(sigma_G=0.4, sigma_R=0.6, room_stable=True),
    "S4_global+kick+tod+exo": dict(sigma_G=0.4, A_k=0.8, A_tod=0.4, exo_rate=0.25, A_e=0.8, sigma_Ga=0.05, A_toda=0.1,
                                   A_ea=0.05),
    "S5_J0.2": dict(J=0.2, sigma_G=0.4, A_k=0.8, A_tod=0.4, exo_rate=0.25, A_e=0.8, sigma_Ga=0.05, A_toda=0.1, A_ea=0.05),
    "S5_J0.4": dict(J=0.4, sigma_G=0.4, A_k=0.8, A_tod=0.4, exo_rate=0.25, A_e=0.8, sigma_Ga=0.05, A_toda=0.1, A_ea=0.05),
    "S5_J0.6": dict(J=0.6, sigma_G=0.4, A_k=0.8, A_tod=0.4, exo_rate=0.25, A_e=0.8, sigma_Ga=0.05, A_toda=0.1, A_ea=0.05),
    "S6_J0.4+room": dict(J=0.4, sigma_G=0.4, sigma_R=0.6, sigma_Ga=0.05, sigma_Ra=0.05),
    "S7_J0.4_content_only": dict(J=0.4, Ja=0.0, sigma_G=0.4, sigma_Ga=0.05),
}
SINGLE = dict(N=24, sizes=(24,), T=15, W=16)
SCEN_SINGLE = {"S1_global": dict(sigma_G=0.4), "S4_global+kick+tod+exo": SCEN["S4_global+kick+tod+exo"],
               "S5_J0.4": SCEN["S5_J0.4"]}


def run_scenario(name, over, base, nrep, rng, do_null=True):
    rows = []
    for rep in range(nrep):
        p = {**base, **over}
        seed = int(rng.integers(1 << 31))
        z, y, info = simulate(p, np.random.default_rng(seed), drives=True)
        z0, y0, _ = simulate(p, np.random.default_rng(seed), drives=False)
        tr = truth_pop(p)
        tr_real = truth(p, z0, y0)
        pan = observe(p, z, y, info, np.random.default_rng(seed + 1))
        est = estimate(pan, np.random.default_rng(seed + 2), do_null=do_null and rep < 8, do_boot=rep < 8)
        rows.append({"rep": rep, "truth": tr, "truth_realized": tr_real, "est": est})
    return rows


def calibrate():
    """Pick sigma_G, sigma_R so that day-level content rho_c ~ 0.06 and rho_ex ~ 0.15 (H01's medians) at J = 0."""
    rng = np.random.default_rng(SEED)
    for sg in (0.2, 0.3, 0.4):
        for sr in (0.0, 0.4, 0.6, 0.8):
            vals = []
            for _ in range(12):
                p = {**BASE, "sigma_G": sg, "sigma_R": sr}
                s = int(rng.integers(1 << 31))
                z, y, info = simulate(p, np.random.default_rng(s))
                pan = observe(p, z, y, info, np.random.default_rng(s + 1))
                _, g, _ = L.run_level(pan[("c", "day")], 2)
                vals.append((g["rho_c"], g["rho_ex"]))
            v = np.nanmedian(np.array(vals), 0)
            print(f"sigma_G {sg} sigma_R {sr}: rho_c {v[0]:.3f} rho_ex {v[1]:.3f}", flush=True)


def summarize(allrows):
    summ = {}
    for name, rows in allrows.items():
        keys = rows[0]["est"].keys()
        s = {}
        for k in keys:
            if k.startswith("h01"):
                v = np.array([r["est"][k] for r in rows if r["est"][k] is not None], float)
                s[k] = {"median": float(np.median(v)) if len(v) else None, "q25": float(np.percentile(v, 25)) if len(v) else None,
                        "q75": float(np.percentile(v, 75)) if len(v) else None}
                continue
            for m in ("g_all", "g_room", "g_ex", "rho_c", "rho_ex"):
                v = np.array([r["est"][k][m] for r in rows], float)
                v = v[np.isfinite(v)]
                s[f"{k}.{m}"] = {"median": float(np.median(v)) if len(v) else None,
                                 "q25": float(np.percentile(v, 25)) if len(v) else None,
                                 "q75": float(np.percentile(v, 75)) if len(v) else None}
            pr = [r["est"][k].get("p_room_perm") for r in rows if r["est"][k].get("p_room_perm") is not None]
            if pr:
                s[f"{k}.reject_room_perm_0.05"] = float(np.mean(np.array(pr) < 0.05))
            cis = [(r["est"][k].get("ci_g_ex"), r["truth"]) for r in rows if r["est"][k].get("ci_g_ex")]
            if cis:
                ch, res = k.split("_")[0], k.split("_")[1]
                cov = [lo <= t[f"{ch}_{res}"]["g_room"] <= hi for (lo, hi), t in cis if np.isfinite(lo)]
                s[f"{k}.ci_cover_true"] = float(np.mean(cov)) if cov else None
        for tk in rows[0]["truth"]:
            s[f"truth.{tk}.g_room"] = float(np.median([r["truth"][tk]["g_room"] for r in rows]))
        summ[name] = s
    return summ


def main():
    if "--calibrate" in sys.argv:
        calibrate(); return
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    allrows, allsingle = {}, {}
    for name, over in SCEN.items():
        allrows[name] = run_scenario(name, over, BASE, NREP, rng)
        print(f"{name} done {time.time() - t0:.0f}s", flush=True)
    for name, over in SCEN_SINGLE.items():
        allsingle[name] = run_scenario(name, over, {**BASE, **SINGLE}, max(4, NREP // 2), rng, do_null=False)
        print(f"single {name} done {time.time() - t0:.0f}s", flush=True)
    summ = {"two_room": summarize(allrows), "single_room": summarize(allsingle),
            "config": {"base": BASE, "single": SINGLE, "scenarios": SCEN, "nrep": NREP, "seed": SEED}}
    (OUT / "synthetic_summary.json").write_text(json.dumps(summ, indent=1, default=float))
    (OUT / "synthetic_rows.json").write_text(json.dumps({"two_room": allrows, "single_room": allsingle}, default=float))
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
