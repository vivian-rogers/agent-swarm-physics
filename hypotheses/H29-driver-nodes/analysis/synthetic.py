"""H29 synthetic validation (axis F): can the pipeline find the driver nodes at village sampling?

Content dynamics are simulated on the REAL event skeleton of a unit (who posted when, in which room, which messages
were in each recipient's visible set, who was named). Only the vectors are synthetic. Per agent i, latent content
  z_i(t) = h_i + c_room(t) + delta_i(t),
  delta relaxes at rate Gamma toward 0 with OU noise; c_room is a room-level OU drift (common drive);
  at each talk turn: delta_i += sum_{m in V} w_m a_{s(m) i} (x_m - z_i)     [linear]
     nonlinear: w_m = (k/3)^-0.6 (dilution) * sigmoid((cos(x_m, z_i) - theta)/0.1) (bounded confidence);
  emitted statement x = z_i + eta (readout noise). Humans: x = c_room + g (own direction); they pull with
  a_named / a_bystander. Automated: a fixed nudge direction + noise, no pull.
Nuisance variances are calibrated to analysis/calibrate.py (agent share ~0.2, day share ~0.05, residual ~0.65).

Ground truth "where to inject": for every agent k and day, add eps*v to delta_k at t0 = day start + 30 min and
measure D_true_k = int_{t0}^{t0+4h} (sum_j p_j(t))^2 dt with p_j = (z_j^inj - z_j^base).v / eps, using common random
numbers (exact paired runs). Averaged over days. Linear and nonlinear alike.

  uv run python hypotheses/H29-driver-nodes/analysis/synthetic.py            # full design (2 processes)
  uv run python hypotheses/H29-driver-nodes/analysis/synthetic.py --quick
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402

D = 32
CAL = dict(s2_h=0.20, s2_c=0.06, tau_c_h=1.5, s2_d=0.12, gamma=0.7, s2_eta=0.62, s2_g=0.8)
EPS = 0.5
T0_OFF_H = 0.5


class Skeleton:
    """Per-day event arrays from a real unit (no content)."""

    def __init__(self, U: dict):
        msgs = U["msgs"].sort("t_us")
        self.U = U
        self.msg = msgs["msg"].to_numpy().astype(np.int64)
        self.t = msgs["t_us"].to_numpy()
        self.day = msgs["pt_date"].to_numpy()
        self.kind = msgs["kind"].to_numpy()
        self.sender = msgs["sender"].to_numpy()
        rooms = msgs["room"].to_numpy()
        ur = sorted(set(rooms.tolist()))
        self.room = np.array([ur.index(r) for r in rooms])
        self.n_rooms = len(ur)
        snd = sorted(set(self.sender[self.kind == 0].tolist()) | set(U["turns"]["agent"].to_list()))
        self.agents = snd
        self.apos = {a: i for i, a in enumerate(snd)}
        pos = {int(m): q for q, m in enumerate(self.msg)}
        T = U["turns"]
        turn_of = dict(zip(T["msg"].to_list(), T["talk_id"].to_list()))
        Rv = U["rows"].filter(pl.col("vis"))
        V = {}
        for (tid,), sub in Rv.group_by(["talk_id"], maintain_order=True):
            V[int(tid)] = (np.array([pos[int(m)] for m in sub["msg"].to_list()], dtype=np.int64),
                           sub["kind"].to_numpy().astype(np.int8), sub["sender"].to_numpy(), sub["ment_j"].to_numpy())
        self.V = {}
        for q, m in enumerate(self.msg):
            tid = turn_of.get(int(m))
            if tid is not None and tid in V:
                self.V[q] = V[tid]
        self.days = sorted(set(self.day.tolist()))
        self.day_ev = {d: np.where(self.day == d)[0] for d in self.days}


def draw_params(sk: Skeleton, rng, a_mean: float, sigma_s: float, sigma_r: float = 0.3) -> dict:
    Na = len(sk.agents)
    s = rng.lognormal(-sigma_s ** 2 / 2, sigma_s, Na)
    r = rng.lognormal(-sigma_r ** 2 / 2, sigma_r, Na)
    a = a_mean * np.outer(s, r)
    np.fill_diagonal(a, 0)
    h = rng.normal(0, np.sqrt(CAL["s2_h"] / D), (Na, D))
    nudge = rng.normal(0, np.sqrt(0.8 / D), D)
    return dict(a=a, s=s, r=r, h=h, nudge=nudge, a_hn=3 * a_mean, a_hb=a_mean)


def day_noise(sk: Skeleton, d: str, rng) -> dict:
    ev = sk.day_ev[d]
    n = len(ev)
    t_h = (sk.t[ev] - sk.t[ev[0]]) / 3.6e9
    C = np.zeros((sk.n_rooms, n, D))
    for r in range(sk.n_rooms):
        c = rng.normal(0, np.sqrt(CAL["s2_c"] / D), D)
        prev = 0.0
        z = rng.normal(0, 1, (n, D))
        for q in range(n):
            f = np.exp(-(t_h[q] - prev) / CAL["tau_c_h"])
            c = f * c + np.sqrt(CAL["s2_c"] / D * (1 - f * f)) * z[q]
            C[r, q] = c
            prev = t_h[q]
    return dict(ev=ev, t_h=t_h, C=C, eta=rng.normal(0, np.sqrt(CAL["s2_eta"] / D), (n, D)),
                xi=rng.normal(0, 1, (n, D)), g=rng.normal(0, np.sqrt(CAL["s2_g"] / D), (n, D)),
                d0=rng.normal(0, np.sqrt(CAL["s2_d"] / D), (len(sk.agents), D)),
                v=(lambda x: x / np.linalg.norm(x))(rng.normal(0, 1, D)))


def simulate_day(sk: Skeleton, P: dict, nz: dict, nonlinear: bool, inject: tuple[int, float] | None = None,
                 start_state=None, start_q: int = 0, stop_h: float | None = None, record_v: bool = False):
    """Simulate one day. inject = (agent index k, t0 in hours since day start). Returns X (n x D) and optionally
    per-event projections of delta on v for the acting agent (for the paired response)."""
    ev, t_h, C, eta, xi, g = nz["ev"], nz["t_h"], nz["C"], nz["eta"], nz["xi"], nz["g"]
    n = len(ev)
    Na = len(sk.agents)
    gam = CAL["gamma"]
    s2d = CAL["s2_d"] / D
    if start_state is None:
        delta = nz["d0"].copy()
        tlast = np.zeros(Na)
        X = np.zeros((n, D))
    else:
        delta, tlast, X = (x.copy() for x in start_state)
    injected = inject is None
    proj = []  # (q, agent, delta.v)
    a = P["a"]
    for q in range(start_q, n):
        th = t_h[q]
        if stop_h is not None and th > stop_h:
            break
        e = ev[q]
        k = sk.kind[e]
        rm = sk.room[e]
        if not injected and th >= inject[1]:
            kk = inject[0]
            # apply eps*v at t0 to agent kk (relax it to t0 first; noise for that interval is drawn at kk's next event,
            # identically in both runs because relaxation is linear)
            delta[kk] = delta[kk] + EPS * nz["v"] * np.exp(-gam * 0.0)
            # shift kk's clock bookkeeping: the injected part should decay from t0, not from tlast. Handle by
            # pre-scaling: the next relaxation multiplies by exp(-gam (t - tlast)); compensate.
            delta[kk] = delta[kk] + EPS * nz["v"] * (np.exp(gam * (inject[1] - tlast[kk])) - 1.0)
            injected = True
        if k == 0:
            i = sk.apos[int(sk.sender[e])]
            f = np.exp(-gam * (th - tlast[i]))
            delta[i] = f * delta[i] + np.sqrt(s2d * (1 - f * f)) * xi[q]
            tlast[i] = th
            z = P["h"][i] + C[rm, q] + delta[i]
            Vq = sk.V.get(e)
            if Vq is not None:
                idx, kinds, snd, named = Vq
                qi = np.searchsorted(ev, idx)  # positions within the day
                okq = (qi < n) & (ev[np.clip(qi, 0, n - 1)] == idx) & (qi < q)
                if okq.any():
                    qi, kinds, snd, named = qi[okq], kinds[okq], snd[okq], named[okq]
                    w = np.zeros(len(qi))
                    ag = kinds == 0
                    if ag.any():
                        w[ag] = a[[sk.apos[int(x)] for x in snd[ag]], i]
                        if P.get("named_mult", 1.0) != 1.0:
                            w[ag] = w[ag] * np.where(named[ag], P["named_mult"], 1.0)
                    hu = kinds == 1
                    w[hu] = np.where(named[hu], P["a_hn"], P["a_hb"])
                    Xm = X[qi]
                    if nonlinear:
                        w = w * (len(qi) / 3.0) ** -0.6
                        zc = z / (np.linalg.norm(z) + 1e-9)
                        cs = (Xm @ zc) / (np.linalg.norm(Xm, axis=1) + 1e-9)
                        w = w / (1 + np.exp(-(cs - 0.0) / 0.1))
                    delta[i] = delta[i] + (w[:, None] * (Xm - z)).sum(0)
                    z = P["h"][i] + C[rm, q] + delta[i]
            X[q] = z + eta[q]
            if record_v:
                proj.append((q, i, float(delta[i] @ nz["v"])))
        elif k == 1:
            X[q] = C[rm, q] + g[q]
        else:
            X[q] = P["nudge"] + 0.3 * eta[q]
    return X, proj, (delta, tlast, X)


def state_at(sk, P, nz, nonlinear, t0_h):
    """Base run up to (not including) the first event at or after t0; returns the state and that event index."""
    n = len(nz["ev"])
    q0 = int(np.searchsorted(nz["t_h"], t0_h, "left"))
    if q0 >= n:
        return None, q0
    if q0 == 0:
        return (nz["d0"].copy(), np.zeros(len(sk.agents)), np.zeros((n, D))), 0
    _, _, st = simulate_day(sk, P, nz, nonlinear, stop_h=None if q0 == 0 else nz["t_h"][q0 - 1] + 1e-12)
    return st, q0


def response_D(sk, P, nz, nonlinear, T_h: float = L.T_HORIZON_H, grid_h: float = L.DT_H) -> np.ndarray:
    """D_true_k for this day for every agent index k (paired injected vs base runs from t0)."""
    Na = len(sk.agents)
    t_h = nz["t_h"]
    t0 = t_h[0] + T0_OFF_H
    t_end = min(t0 + T_h, t_h[-1])
    if t_end <= t0 + 0.5:
        return np.full(Na, np.nan)
    st, q0 = state_at(sk, P, nz, nonlinear, t0)
    if st is None:
        return np.full(Na, np.nan)
    _, base, _ = simulate_day(sk, P, nz, nonlinear, start_state=st, start_q=q0, stop_h=t_end, record_v=True)
    grid = np.arange(t0, t_end + 1e-9, grid_h)
    gam = CAL["gamma"]
    v0 = st[0] @ nz["v"]  # base delta.v at t0 (before relaxation to t0)
    tl0 = st[1].copy()

    def traj(rec):
        # per agent: piecewise-exponential delta.v between its events
        P_ = np.zeros((Na, len(grid)))
        last_t = tl0.copy()
        last_v = v0.copy()
        bya = {}
        for q, i, val in rec:
            bya.setdefault(i, []).append((t_h[q], val))
        for i in range(Na):
            evs = bya.get(i, [])
            ts = np.array([x[0] for x in evs])
            vs = np.array([x[1] for x in evs])
            idx = np.searchsorted(ts, grid, "right") - 1
            lt = np.where(idx >= 0, ts[np.clip(idx, 0, None)] if len(ts) else 0, last_t[i])
            lv = np.where(idx >= 0, vs[np.clip(idx, 0, None)] if len(vs) else 0, last_v[i])
            P_[i] = lv * np.exp(-gam * (grid - lt))
        return P_

    Pb = traj(base)
    out = np.zeros(Na)
    for k in range(Na):
        _, inj, _ = simulate_day(sk, P, nz, nonlinear, inject=(k, t0), start_state=st, start_q=q0, stop_h=t_end,
                                 record_v=True)
        Pi = traj(inj)
        # agent k's own injected part before its first event after t0: add eps*exp(-gam(t - t0))
        diff = (Pi - Pb) / EPS
        firstk = [t_h[q] for q, i, _ in inj if i == k]
        tk = firstk[0] if firstk else np.inf
        pre = grid < tk
        diff[k, pre] = np.exp(-gam * (grid[pre] - t0))
        S = diff.sum(0)
        out[k] = np.trapezoid(S ** 2, grid)
    return out


def simulate_unit(sk: Skeleton, P: dict, nonlinear: bool, seed: int, truth: bool = True):
    rng = np.random.default_rng(seed)
    U = sk.U
    Xall = np.zeros((len(sk.msg), D))
    Dt = []
    for d in sk.days:
        nz = day_noise(sk, d, rng)
        X, _, _ = simulate_day(sk, P, nz, nonlinear)
        Xall[nz["ev"]] = X
        if truth:
            Dt.append(response_D(sk, P, nz, nonlinear))
    Xn = Xall / np.linalg.norm(Xall, axis=1, keepdims=True)
    o = np.argsort(sk.msg)
    Usyn = dict(U)
    Usyn["msg_sorted"] = sk.msg[o]
    Usyn["X"] = Xn[o].astype(np.float32)
    Dtrue = np.nanmean(np.array(Dt), axis=0) if truth else None
    return Usyn, Dtrue


def evaluate(sk: Skeleton, Usyn: dict, Dtrue, P: dict, estimators=("marginal", "joint"), seed: int = 0) -> dict:
    R = L.row_stats(Usyn, seed=seed)
    agents = L.network_agents(Usyn)
    ai = [sk.apos[a] for a in agents]
    res = dict(n_agents=len(agents))
    ku = L.kappa_unit(R, B=300, seed=seed)
    res["kappa"] = ku["kappa"]
    res["kappa_ci"] = ku.get("kappa_ci")
    res["kappa_x"] = ku["kappa_x"]
    res["kappa_x_ci"] = ku.get("kappa_x_ci")
    res["contamination"] = ku["contamination"]
    res["gamma_hat"] = L.gamma_unit(Usyn)["gamma"]
    true_out = P["s"][ai]
    if Dtrue is not None:
        dtr = Dtrue[ai]
        res["true_top"] = int(np.nanargmax(dtr))
        res["rho_truth_vs_s"] = L.spearman(dtr, true_out)
    nd = len(Usyn["meta"]["days"])
    even = {d for d in range(nd) if d % 2 == 0}
    odd = set(range(nd)) - even
    for est in estimators:
        F = L.fit_network(Usyn, R, agents, estimator=est, gamma=None, B_unit=50, B_pair=100, seed=seed)
        r = {}
        if Dtrue is not None:
            r["rho_D"] = L.spearman(F["D"], dtr)
            r["rho_out"] = L.spearman(F["out"], dtr)
            r["rho_net"] = L.spearman(F["net"], dtr)
            r["rho_vol"] = L.spearman(F["vol"], dtr)
            top3 = np.argsort(-F["D"])[:3]
            r["top_in_top3"] = bool(res["true_top"] in top3)
            r["top1"] = bool(int(np.argmax(F["D"])) == res["true_top"])
        r["rho_D_vs_s"] = L.spearman(F["D"], true_out)
        r["rho_D_vs_net"] = L.spearman(F["D"], F["net"])
        # split-half reliability
        if len(even) >= 1 and len(odd) >= 1:
            Fe = L.fit_network(Usyn, R, agents, day_set=even, estimator=est, B_unit=20, B_pair=60, seed=seed)
            Fo = L.fit_network(Usyn, R, agents, day_set=odd, estimator=est, B_unit=20, B_pair=60, seed=seed)
            r["split_half"] = L.spearman(Fe["D"], Fo["D"])
            if est == "marginal":
                res["_halves"] = (Fe, Fo)
        res[est] = r
    # cross-fitted V2 (hourly 2-h swarm spread on the test half) for the marginal estimator
    if "_halves" in res:
        Fe, Fo = res.pop("_halves")
        am = Usyn["msgs"].filter(pl.col("kind") == 0).with_columns(
            pl.col("pt_date").replace_strict({d: i for i, d in enumerate(Usyn["meta"]["days"])}, return_dtype=pl.Int16)
            .alias("day_idx"))
        hs = L.horizon_spread(Usyn, am)
        rows = []
        for train, test, Ftr in ((even, odd, Fe), (odd, even, Fo)):
            hrs = L.active_hours(Usyn, [Usyn["meta"]["days"][d] for d in test])
            H = L.hourly_spread(hs, agents, hrs, day_set=test)
            rows.append(dict(D=L.spearman(Ftr["D"], H), vol=L.spearman(Ftr["vol"], H), out=L.spearman(Ftr["out"], H),
                             net=L.spearman(Ftr["net"], H),
                             truth=L.spearman(Dtrue[ai], H) if Dtrue is not None else np.nan))
        res["V2"] = {k: float(np.nanmean([r[k] for r in rows])) for k in rows[0]}
    return res


def run_one(job):
    unit, cond, rep = job
    t = time.time()
    U = L.load_unit(unit)  # event skeleton only; no real vectors are loaded
    sk = Skeleton(U)
    rng = np.random.default_rng(L.SEED + 1000 * rep + zlib.crc32(cond.encode()) % 997)
    P = draw_params(sk, rng, a_mean=cond_params(cond)["a"], sigma_s=cond_params(cond)["sigma_s"])
    Usyn, Dtrue = simulate_unit(sk, P, cond_params(cond)["nonlinear"], seed=L.SEED + rep,
                                truth=cond_params(cond)["a"] > 0)
    res = evaluate(sk, Usyn, Dtrue, P, seed=rep)
    res.update(unit=unit, cond=cond, rep=rep, secs=time.time() - t)
    return res


def cond_params(cond: str) -> dict:
    return {
        "null": dict(a=0.0, sigma_s=0.7, nonlinear=False),
        "lin03": dict(a=0.03, sigma_s=0.7, nonlinear=False),
        "lin01": dict(a=0.01, sigma_s=0.7, nonlinear=False),
        "lin03_s1": dict(a=0.03, sigma_s=1.0, nonlinear=False),
        "nl03": dict(a=0.03, sigma_s=0.7, nonlinear=True),
    }[cond]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--extra", action="store_true", help="append the a = 0.01 conditions for G41 and G51b")
    ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    if a.summarize:
        summarize()
        return
    prev = []
    if a.extra:
        prev = json.loads((L.OUT / "synthetic" / "synthetic_results.json").read_text())
        jobs = [("G41", "lin01", r) for r in range(8)] + [("G51b", "lin01", r) for r in range(3)]
    elif a.quick:
        jobs = [("G41", "lin03", 0), ("G41", "null", 0)]
    else:
        jobs = ([("G38", c, r) for c in ("null", "lin03", "lin01", "nl03", "lin03_s1") for r in range(8)]
                + [("G41", c, r) for c in ("null", "lin03", "nl03") for r in range(8)]
                + [("G51b", c, r) for c in ("null", "lin03", "nl03") for r in range(3)])
    out = L.OUT / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    t = time.time()
    results = list(prev)
    with ProcessPoolExecutor(max_workers=min(2, a.workers)) as ex:
        for r in ex.map(run_one, jobs):
            results.append(r)
            m = r.get("marginal", {})
            print(f"{r['unit']} {r['cond']} rep{r['rep']}: kappa {r['kappa']:.4f} ci {r['kappa_ci']} | rhoD "
                  f"{m.get('rho_D', float('nan')):.2f} top3 {m.get('top_in_top3')} split {m.get('split_half', float('nan')):.2f}"
                  f" | joint rhoD {r.get('joint', {}).get('rho_D', float('nan')):.2f} | V2 {r.get('V2')} "
                  f"({r['secs']:.0f}s)", flush=True)
            L.jdump(results, out / ("synthetic_quick.json" if a.quick else "synthetic_results.json"))
    L.write_provenance("synthetic", "hypotheses/H29-driver-nodes/analysis/synthetic.py",
                       {"calibration": CAL, "eps": EPS, "jobs": len(jobs), "quick": a.quick})
    print(f"done {time.time() - t:.0f}s")
    if not a.quick:
        summarize()



def summarize(path: Path | None = None) -> dict:
    """Per (unit, condition): recovery, reliability, false positives and V2, from synthetic_results.json."""
    path = path or (L.OUT / "synthetic" / "synthetic_results.json")
    res = json.loads(path.read_text())
    groups = {}
    for r in res:
        groups.setdefault((r["unit"], r["cond"]), []).append(r)
    out = {}
    for (u, c), rs in sorted(groups.items()):
        def med(f):
            v = [f(r) for r in rs]
            v = [x for x in v if x is not None and np.isfinite(x)]
            return float(np.median(v)) if v else None

        def frac(f):
            v = [f(r) for r in rs]
            v = [x for x in v if x is not None]
            return float(np.mean(v)) if v else None
        ci_pos = lambda key: (lambda r: (r.get(key) or [0, 0])[0] > 0)
        ci_neg = lambda key: (lambda r: (r.get(key) or [0, 0])[1] < 0)
        g = dict(n=len(rs), kappa_med=med(lambda r: r["kappa"]), kappa_ci_pos=frac(ci_pos("kappa_ci")),
                 kappa_ci_neg=frac(ci_neg("kappa_ci")), raw_ci_pos=frac(ci_pos("kappa_x_ci")),
                 contamination_med=med(lambda r: r["contamination"]), gamma_hat_med=med(lambda r: r["gamma_hat"]))
        for est in ("marginal", "joint"):
            g[est] = dict(rho_D=med(lambda r: r.get(est, {}).get("rho_D")),
                          rho_out=med(lambda r: r.get(est, {}).get("rho_out")),
                          rho_net=med(lambda r: r.get(est, {}).get("rho_net")),
                          rho_vol=med(lambda r: r.get(est, {}).get("rho_vol")),
                          top_in_top3=frac(lambda r: r.get(est, {}).get("top_in_top3")),
                          top1=frac(lambda r: r.get(est, {}).get("top1")),
                          split_half=med(lambda r: r.get(est, {}).get("split_half")),
                          rho_D_vs_net=med(lambda r: r.get(est, {}).get("rho_D_vs_net")))
        g["truth_vs_s"] = med(lambda r: r.get("rho_truth_vs_s"))
        g["V2"] = {k: med(lambda r, k=k: (r.get("V2") or {}).get(k)) for k in ("D", "vol", "out", "net", "truth")}
        out[f"{u}/{c}"] = g
    L.jdump(out, path.parent / "synthetic_summary.json")
    for k, g in out.items():
        m = g["marginal"]
        print(f"{k:16s} n={g['n']} kappa {g['kappa_med']:.4f} CI>0 {g['kappa_ci_pos']:.2f} CI<0 {g['kappa_ci_neg']:.2f} "
              f"raw>0 {g['raw_ci_pos']:.2f} | rhoD {m['rho_D']} top3 {m['top_in_top3']} split {m['split_half']:.2f} "
              f"| joint rhoD {g['joint']['rho_D']} | out {m['rho_out']} vol {m['rho_vol']} | V2 {g['V2']}")
    return out


if __name__ == "__main__":
    main()
