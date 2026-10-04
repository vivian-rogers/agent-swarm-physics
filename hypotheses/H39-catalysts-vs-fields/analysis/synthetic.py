"""H39 synthetic validation (axis F): can the estimators tell planted fields from planted catalysts at village sampling?

Agents: 4-state Markov-jump chains (work, chat, idle, consolidate) on a 1-min grid, one jump at most per minute
(p_jump = 1 - exp(-sum_j k_ij), destination proportional to k_ij), with agent heterogeneity, optional aging of
the idle state (H16) and optional kinetic-Potts herding (rates into j scaled by exp(J (m_j - mbar_j))).

Point levers ("nudges"): an agent idle for >= 10 min receives a kick with probability p_n per minute; the effect
starts after a 0-4 min delay and lasts 20 min. Background kicks of another class (no effect) at 0.003/agent-min
create the busy/quiet structure of the real data. Planted effect types:
  field_half   k_ij *= exp((h_j - h_i)/2), h = (+a, 0, -a, 0)        (Arrhenius field, theta = 1/2)
  field_dest   k_ij *= exp(h_j), rows rescaled to keep each state's exit rate   (destination-only field)
  cat_uniform  k_ij *= c                                             (uniform catalyst = time rescaling)
  cat_edge     k_idle,work and k_work,idle *= c                      (barrier lowered on one edge)
  escape       k_idle,j *= c                                         (escape-only kick: expected "both")
  null
Steps: field / catalyst / null applied to all agents from day 10 of 20, with day-level noise; judged against
within-series day-boundary placebos. Content: a q = 6 chain at 30-min windows with kicks.

Writes data/processed/H39-catalysts-vs-fields/synthetic/synthetic_results.json and figures/synthetic_validation.pdf.
Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/synthetic.py [--quick]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import sys
import time
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h39lib as L  # noqa: E402

BASE = np.array([
    #  work   chat   idle   cons
    [0.000, 0.050, 0.040, 0.020],   # work
    [0.450, 0.000, 0.150, 0.020],   # chat
    [0.060, 0.030, 0.000, 0.006],   # idle
    [0.300, 0.020, 0.050, 0.000],   # cons
])
WORK, CHAT, IDLE, CONS = 0, 1, 2, 3
A_FIELD = 0.8
C_CAT = 2.0
C_EDGE = 2.5
C_ESC = 2.5


def modify(K: np.ndarray, kind: str) -> np.ndarray:
    K = K.copy()
    if kind == "null":
        return K
    if kind == "field_half":
        h = np.array([A_FIELD, 0, -A_FIELD, 0])
        return K * np.exp((h[None, :] - h[:, None]) / 2)
    if kind == "field_dest":
        h = np.array([A_FIELD, 0, -A_FIELD, 0])
        K2 = K * np.exp(h[None, :])
        return K2 * (K.sum(1, keepdims=True) / K2.sum(1, keepdims=True))
    if kind == "cat_uniform":
        return K * C_CAT
    if kind == "cat_edge":
        K[IDLE, WORK] *= C_EDGE
        K[WORK, IDLE] *= C_EDGE
        return K
    if kind == "escape":
        K[IDLE, :] *= C_ESC
        return K
    raise ValueError(kind)


def stationary_rates(K):
    Q = K - np.diag(K.sum(1))
    A = Q.T.copy()
    A[-1] = 1
    b = np.zeros(len(K))
    b[-1] = 1
    return np.linalg.solve(A, b)


def simulate(n_agents, n_days, L_day, kind, rng, p_n=0.03, aging=False, J=0.0, bg_rate=0.003,
             effect_len=20, step_day=None, step_kind=None, day_sd=0.0):
    """Returns per agent-day sequences, kick minutes (nudge, bg), and the busy masks."""
    spd = np.exp(rng.normal(0, 0.3, n_agents))
    idl = np.exp(rng.normal(0, 0.4, n_agents))
    Ka = np.stack([BASE * spd[a] for a in range(n_agents)])
    Ka[:, IDLE, :] *= idl[:, None]
    Kk = np.stack([modify(Ka[a], kind) for a in range(n_agents)])
    mbar = stationary_rates(BASE)
    seqs, agents, days, nud, bg = [], [], [], [], []
    for d in range(n_days):
        Kd = Ka.copy()
        Kkd = Kk.copy()
        if day_sd > 0:
            sp = np.exp(rng.normal(0, day_sd))
            hd = rng.normal(0, day_sd, 4)
            fac = sp * np.exp((hd[None, :] - hd[:, None]) / 2)
            Kd = Kd * fac[None]
            Kkd = Kkd * fac[None]
        if step_day is not None and d >= step_day:
            Kd = np.stack([modify(Kd[a], step_kind) for a in range(n_agents)])
            Kkd = Kd
        x = np.zeros((n_agents, L_day), np.int8)
        s = np.zeros(n_agents, np.int64)  # cold start in work
        age = np.ones(n_agents)
        eff_until = np.full(n_agents, -1)
        eff_from = np.full(n_agents, 10 ** 9)
        kn = [[] for _ in range(n_agents)]
        kb = [[] for _ in range(n_agents)]
        for m in range(L_day):
            x[:, m] = s
            # kicks at minute m (seen before the transition m -> m+1)
            isn = (s == IDLE) & (age >= 10) & (m > eff_until) & (rng.random(n_agents) < p_n)
            for a in np.flatnonzero(isn):
                kn[a].append(m)
                dl = rng.integers(0, 5)
                eff_from[a] = m + 1 + dl
                eff_until[a] = m + dl + effect_len
            for a in np.flatnonzero(rng.random(n_agents) < bg_rate):
                kb[a].append(m)
            active = (m + 1 >= eff_from) & (m + 1 <= eff_until)
            Kcur = np.where(active[:, None, None], Kkd, Kd)
            rows = Kcur[np.arange(n_agents), s].copy()
            if aging:
                fac = np.where(s == IDLE, (1 + age / 5.0) ** -0.7, 1.0)
                rows *= fac[:, None]
            if J != 0:
                cnt = np.bincount(s, minlength=4).astype(float)
                mo = (cnt[None, :] - np.eye(4)[s]) / max(n_agents - 1, 1)
                rows *= np.exp(J * (mo - mbar[None, :]))
                rows[np.arange(n_agents), s] = 0
            tot = rows.sum(1)
            jump = rng.random(n_agents) < 1 - np.exp(-tot)
            new = s.copy()
            for a in np.flatnonzero(jump):
                new[a] = rng.choice(4, p=rows[a] / tot[a])
            age = np.where(new == s, age + 1, 1)
            s = new
        for a in range(n_agents):
            seqs.append(x[a])
            agents.append(a)
            days.append(d)
            nud.append(np.array(kn[a], np.int64))
            bg.append(np.array(kb[a], np.int64))
    busy = []
    for k in range(len(seqs)):
        b = np.zeros(len(seqs[k]), bool)
        b[nud[k]] = True
        b[bg[k]] = True
        busy.append(b)
    return seqs, agents, days, nud, bg, busy


def unit_from_sim(sim, q=4):
    seqs, agents, days, nud, bg, busy = sim
    return L.build_unit(seqs, agents, days, None, q, events={"N_tgt": nud, "A_men": bg}, busy=busy,
                        active_states=(WORK, CHAT))


def verdict_single(r):
    """Single-unit classification: field if p_F < 0.05; catalyst if K CI excludes 0 and |K| >= THR."""
    return L.unit_class(r)


def one_point(args):
    kind, size, variant, rep = args
    rng = np.random.default_rng(1000 * rep + zlib.crc32(f"{kind}{size}{variant}".encode()) % 997)
    if size == "small":
        na, nd, Ld, pn = 12, 5, 240, 0.03
    elif size == "few":
        na, nd, Ld, pn = 12, 5, 240, 0.008
    else:
        na, nd, Ld, pn = 25, 20, 480, 0.02
    aging = variant in ("aging", "aging_potts")
    J = 1.0 if variant in ("potts", "aging_potts") else 0.0
    sim = simulate(na, nd, Ld, kind, rng, p_n=pn, aging=aging, J=J)
    U = unit_from_sim(sim)
    r = L.run_point(U, "N_tgt", W=30, B=200, P=100, seed=rep)
    out = dict(kind=kind, size=size, variant=variant, rep=rep, n_ep=r.get("n_ep", 0), verdict=verdict_single(r))
    for k in ("K", "phi", "phi_exc", "p_F", "p_K", "rho", "ksym"):
        out[k] = r.get(k)
    if "dpi" in r:
        out["dpi_idle"] = r["dpi"][IDLE]
        out["docc_idle"] = r["docc"][IDLE]
        out["p_docc_idle"] = r["p_docc"][IDLE]
        out["esc_idle"] = r["esc"][IDLE]
        out["esc_work"] = r["esc"][WORK]
        out["K_ci"] = r["K_ci"]
    return out


def one_step(args):
    kind, rep = args
    rng = np.random.default_rng(50000 + 100 * rep + zlib.crc32(kind.encode()) % 97)
    na, nd, Ld, sd = 10, 40, 240, 20
    sim = simulate(na, nd, Ld, "null", rng, p_n=0.0, step_day=sd, step_kind=kind, day_sd=0.25, bg_rate=0.0)
    seqs, agents, days = sim[0], sim[1], sim[2]
    days = np.array(days)

    def U_for(dd):
        ix = [k for k in range(len(seqs)) if days[k] in dd]
        return L.build_unit([seqs[k] for k in ix], [agents[k] for k in ix], [int(days[k]) for k in ix], None, 4)
    res = L.run_step(U_for({sd - 2, sd - 1}), U_for({sd, sd + 1}), B=200, seed=rep)
    plac = []
    for b in range(2, nd - 1):
        if b in (sd - 1, sd, sd + 1):
            continue
        plac.append(L.run_step(U_for({b - 2, b - 1}), U_for({b, b + 1}), B=2, seed=b))
    j = L.judge_step(res, plac)
    return dict(kind=kind, rep=rep, K=res["K"], phi=res["phi"], verdict=j.get("cls"), phi_pct=j.get("phi_pct"),
                K_pct=j.get("K_pct"))


def one_content(args):
    """q = 6 chain at 30-min windows; kicks act on the next 2 windows."""
    kind, rep = args
    rng = np.random.default_rng(90000 + 100 * rep + zlib.crc32(kind.encode()) % 89)
    q, na, nd, Lw = 6, 12, 10, 12
    base = np.full((q, q), 0.35 / (q - 1))
    np.fill_diagonal(base, 0)
    seqs, agents, days, kicks, busy = [], [], [], [], []
    for d in range(nd):
        for a in range(na):
            x = np.zeros(Lw, np.int8)
            s = rng.integers(0, q)
            ku, eff = [], -1
            for w in range(Lw):
                x[w] = s
                if w > eff + 1 and rng.random() < 0.12:
                    ku.append(w)
                    eff = w + 2
                K = base.copy()
                if w + 1 <= eff and kind != "null":
                    if kind == "field":
                        h = np.zeros(q)
                        h[0] = 1.2
                        K = K * np.exp((h[None, :] - h[:, None]) / 2)
                    elif kind == "catalyst":
                        K = K * 2.0
                p = 1 - np.exp(-K[s].sum())
                if rng.random() < p:
                    s = rng.choice(q, p=K[s] / K[s].sum())
            seqs.append(x)
            agents.append(a)
            days.append(d)
            kicks.append(np.array(ku, np.int64))
            b = np.zeros(Lw, bool)
            b[ku] = True
            busy.append(b)
    U = L.build_unit(seqs, agents, days, None, q, events={"N_tgt": kicks}, busy=busy)
    r = L.run_point(U, "N_tgt", W=3, B=200, P=100, seed=rep, quiet=1)
    return dict(kind=kind, rep=rep, n_ep=r.get("n_ep"), verdict=verdict_single(r), K=r.get("K"), phi=r.get("phi"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    reps = 2 if a.quick else 8
    kinds = ["null", "field_half", "field_dest", "cat_uniform", "cat_edge", "escape"]
    t0 = time.time()
    jobs = [(k, s, v, r) for k in kinds for s in ("small", "large") for v in ("markov", "aging_potts")
            for r in range(2 * reps if k == "null" else reps)]
    jobs += [(k, "few", "aging_potts", r) for k in kinds for r in range(reps)]
    with ProcessPoolExecutor(a.workers) as ex:
        point = list(ex.map(one_point, jobs, chunksize=1))
        print(f"point done {time.time() - t0:.0f}s", flush=True)
        steps = list(ex.map(one_step, [(k, r) for k in ("null", "field_half", "cat_uniform", "escape")
                                       for r in range(2 * reps if k == "null" else reps)]))
        print(f"steps done {time.time() - t0:.0f}s", flush=True)
        content = list(ex.map(one_content, [(k, r) for k in ("null", "field", "catalyst") for r in range(reps)]))
    # theoretical stationary shifts of the planted effects on the base chain
    theory = {}
    p0 = stationary_rates(BASE)
    for k in kinds:
        K2 = modify(BASE, k)
        p1 = stationary_rates(K2)
        e0 = BASE.sum(1)
        e1 = K2.sum(1)
        theory[k] = dict(dpi=(p1 - p0).tolist(), K_fixed_occ=float(np.log((p0 * e1).sum() / (p0 * e0).sum())))
    # confusion
    expected = {"null": "neither", "field_half": "field", "field_dest": "field", "cat_uniform": "catalyst",
                "cat_edge": "catalyst", "escape": "both"}
    summ = {}
    for s in ("small", "large", "few"):
        for v in ("markov", "aging_potts"):
            for k in kinds:
                rr = [p for p in point if p["kind"] == k and p["size"] == s and p["variant"] == v]
                if not rr:
                    continue
                vc = {}
                for p in rr:
                    vc[p["verdict"]] = vc.get(p["verdict"], 0) + 1
                summ[f"{s}|{v}|{k}"] = dict(n=len(rr), verdicts=vc, expected=expected[k],
                                            hit=float(np.mean([p["verdict"] == expected[k] for p in rr])),
                                            n_ep=float(np.mean([p["n_ep"] for p in rr])),
                                            K=float(np.mean([p["K"] for p in rr if p["K"] is not None])),
                                            phi_exc=float(np.mean([p["phi_exc"] for p in rr if p["phi_exc"] is not None])),
                                            dpi_idle=float(np.mean([p.get("dpi_idle", np.nan) for p in rr])),
                                            docc_idle=float(np.mean([p.get("docc_idle", np.nan) for p in rr])),
                                            docc_idle_sig=float(np.mean([p.get("p_docc_idle", 1) < 0.05 for p in rr])))
    step_summ = {}
    for k in ("null", "field_half", "cat_uniform", "escape"):
        rr = [p for p in steps if p["kind"] == k]
        vc = {}
        for p in rr:
            vc[p["verdict"]] = vc.get(p["verdict"], 0) + 1
        step_summ[k] = dict(verdicts=vc, K=float(np.mean([p["K"] for p in rr])), phi=float(np.mean([p["phi"] for p in rr])))
    cont_summ = {}
    for k in ("null", "field", "catalyst"):
        rr = [p for p in content if p["kind"] == k]
        vc = {}
        for p in rr:
            vc[p["verdict"]] = vc.get(p["verdict"], 0) + 1
        cont_summ[k] = dict(verdicts=vc, n_ep=float(np.mean([p["n_ep"] for p in rr])))
    out = dict(point=point, steps=steps, content=content, theory=theory, summary=summ, step_summary=step_summ,
               content_summary=cont_summ, params=dict(A_FIELD=A_FIELD, C_CAT=C_CAT, C_EDGE=C_EDGE, C_ESC=C_ESC,
                                                      BASE=BASE.tolist(), reps=reps))
    L.jdump(out, L.OUT / "synthetic" / "synthetic_results.json")
    for k, v in summ.items():
        print(k, v["hit"], v["verdicts"], f"n_ep {v['n_ep']:.0f} K {v['K']:.3f} phi_exc {v['phi_exc']:.3f} dpi_idle {v['dpi_idle']:.3f} docc_idle {v['docc_idle']:.3f} docc_sig {v['docc_idle_sig']:.2f}")
    print("steps", step_summ)
    print("content", cont_summ)
    print("theory", theory)
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
