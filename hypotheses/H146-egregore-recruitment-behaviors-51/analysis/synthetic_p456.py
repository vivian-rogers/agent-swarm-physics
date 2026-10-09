"""H146 synthetic validation (axis F) for P4 (amnesia), P5 (repair) and P6 (specialization, O-information).

Skeletons are real: the #51 forced-erasure / placebo-call table (agents, units, days, follow-up call counts from the
call ledger) for P4 and P5, and the real agent x 2-h-bin presence (calls) of the 8 most active agents for P6.
Outcomes are planted. Output: data/processed/H146-.../synthetic/p456_synthetic.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h146lib as L  # noqa: E402
import tests146 as T  # noqa: E402

OUT = L.ROOT / "data" / "processed" / "H146-egregore-recruitment-behaviors-51" / "synthetic"


def er_skeleton(ev):
    """Real F/P events with follow-up lengths in calls (1-20 and 1-10)."""
    a = ev.a
    er = ev.er
    ct = L.call_times(ev)
    dix = {d: i for i, d in enumerate(a["days"])}
    ag = er["agent"].to_numpy(); t = er["t_call"].to_numpy(); t10 = er["t10"].to_numpy(); t20 = er["t20"].to_numpy()
    n10 = np.zeros(len(ag), int); n20 = np.zeros(len(ag), int)
    for g in np.unique(ag):
        s = ag == g
        c = ct.get(int(g), np.array([0]))
        i0 = np.searchsorted(c, t[s], "left")
        n10[s] = np.searchsorted(c, t10[s], "right") - i0
        n20[s] = np.maximum(np.searchsorted(c, t20[s], "right") - i0, 1)
    return {"F": (er["etype"] == "F").to_numpy(), "agent": ag, "unit": er["unit_id"].to_numpy(),
            "day": np.array([dix[d] for d in er["pt_date"].to_list()]), "t": t, "n10": np.maximum(n10, 1),
            "n20": n20}


def p4_world(S, rng, n_host, r, g, h0=0.03, sd=0.7, pR_F=0.6, pR_P=0.4):
    idx = rng.choice(len(S["F"]), n_host, replace=False)
    F = S["F"][idx]; ag = S["agent"][idx]; n20 = S["n20"][idx]; n10 = np.minimum(S["n10"][idx], n20)
    ha = {a_: h0 * np.exp(rng.normal(0, sd)) for a_ in np.unique(ag)}
    h = np.array([ha[a_] for a_ in ag]) * np.where(F, r, 1.0)
    Rp = rng.random(n_host) < np.where(F, pR_F, pR_P)
    # calls 1-10 at hazard h; calls 11-20 at hazard h * g if R+ (read-gated re-supply)
    t1 = rng.geometric(np.clip(h, 1e-6, 1))
    e10 = t1 <= n10
    h2 = np.clip(h * np.where(Rp, g, 1.0), 1e-6, 1)
    t2 = n10 + rng.geometric(h2)
    te = np.where(e10, t1, t2)
    d = (te <= n20).astype(float)
    Tt = np.where(d > 0, te, n20).astype(float)
    lm_d = (d > 0) & ~e10
    lm_T = np.where(lm_d, te - n10, np.maximum(n20 - n10, 0)).astype(float)
    return {"F": F, "agent": ag, "unit": S["unit"][idx], "day": S["day"][idx], "t": S["t"][idx], "d": d, "T": Tt,
            "expr10": e10.astype(int), "nread": Rp.astype(int), "touched": np.zeros(n_host, bool),
            "lm_d": lm_d.astype(float), "lm_T": lm_T}


def run_p4(ev, rng, reps=100):
    S = er_skeleton(ev)
    res = {}
    for n_host in (300, 1500):
        for r in (1.0, 0.8, 0.5):
            for g in (1.0, 2.0):
                if r != 1.0 and g != 1.0:
                    continue
                hr, cov, lt05, ge08, rd, rd_rej = [], [], [], [], [], []
                for _ in range(reps):
                    E = p4_world(S, rng, n_host, r, g)
                    o = T.L.p4_stats(E, B=200, seed=int(rng.integers(1e9)))
                    if o is None:
                        continue
                    hr.append(o["HR_F_vs_P"]); lo, hi = o["ci"]
                    cov.append(lo <= r <= hi if np.isfinite(lo) else False)
                    lt05.append(o["HR_F_vs_P"] < 0.5); ge08.append(o["HR_F_vs_P"] >= 0.8)
                    x = o.get("HR_read_F")
                    if x:
                        rd.append(x["est"]); rd_rej.append(np.isfinite(x["ci"][0]) and x["ci"][0] > 1)
                key = f"p4_n{n_host}_r{r}_g{g}"
                res[key] = {"reps": len(hr), "mean_HR": float(np.mean(hr)), "sd_logHR": float(np.std(np.log(hr))),
                            "coverage": float(np.mean(cov)), "share_HR_lt_0.5": float(np.mean(lt05)),
                            "share_HR_ge_0.8": float(np.mean(ge08)),
                            "read_gating": {"mean": float(np.mean(rd)) if rd else None,
                                            "share_ci_above1": float(np.mean(rd_rej)) if rd_rej else None}}
                print(key, json.dumps(res[key]), flush=True)
    return res


def run_p5(ev, rng, reps=100):
    S = er_skeleton(ev)
    res = {}
    for n_ev, n_pl in ((300, 300), (1500, 1500), (20, 200)):
        for ratio in (1.0, 1.5, 2.0):
            rr, rej = [], []
            for _ in range(reps):
                idx = rng.choice(len(S["F"]), n_ev + n_pl, replace=False)
                ag = S["agent"][idx]
                E = np.zeros(n_ev + n_pl, bool); E[:n_ev] = True
                mu_a = {a_: rng.gamma(1.0, 0.25) for a_ in np.unique(ag)}
                mu = np.array([mu_a[a_] for a_ in ag]) * np.where(E, ratio, 1.0)
                lam = rng.gamma(1.0, mu)   # negative binomial (k = 1)
                c = rng.poisson(lam).astype(float)
                s = L.strata_codes(ag, S["unit"][idx])
                est, lo, hi, _ = L.cluster_boot_rr(np.where(E, c, 0), E.astype(float), np.where(~E, c, 0),
                                                   (~E).astype(float), s, ag * 1000 + S["day"][idx], B=200,
                                                   seed=int(rng.integers(1e9)))
                if not np.isfinite(est):
                    continue
                rr.append(est); rej.append(np.isfinite(lo) and lo > 1 and est > 1.2)
            key = f"p5_nev{n_ev}_npl{n_pl}_ratio{ratio}"
            res[key] = {"reps": len(rr), "mean_rr": float(np.mean(rr)), "share_pass_rule": float(np.mean(rej))}
            print(key, json.dumps(res[key]), flush=True)
    return res


def spec_world(pres_bins, rng, n_el=6, lam=0.0, field=False, p_host=0.3):
    agents = list(pres_bins)
    common = rng.dirichlet(np.ones(n_el))
    own = {g: rng.dirichlet(0.3 * np.ones(n_el)) for g in agents}
    allb = sorted(set().union(*[set(v) for v in pres_bins.values()]))
    hh, ee, bb = [], [], []
    for b in allb:
        cm = rng.dirichlet(2 * np.ones(n_el)) if field else common
        for g in agents:
            if b not in pres_bins[g] or rng.random() > p_host:
                continue
            w = (1 - lam) * cm + lam * own[g]
            k = min(2 + rng.poisson(1.0), n_el)
            els = rng.choice(n_el, k, replace=False, p=w)
            for e in els:
                hh.append(g); ee.append(e); bb.append(b)
    h, e, b = np.array(hh), np.array(ee), np.array(bb)
    # bins with >= 2 hosts
    u = np.unique(np.column_stack([b, h]), axis=0)
    ub, nh = np.unique(u[:, 0], return_counts=True)
    k = np.isin(b, ub[nh >= 2])
    return h[k], e[k], b[k]


def p6_spec_stat(h, e, b, rng, n_perm=200):
    S = L.mi_host_element(h, e)
    null, exc = [], 0
    for _ in range(n_perm):
        v = L.mi_host_element(L.perm_within_bin(e, b, rng, h), e)
        null.append(v); exc += v >= S
        if exc >= 10:
            break
    null = np.array(null)
    return (S - null.mean()) / null.std() if null.std() > 0 else 0.0, (exc + 1) / (len(null) + 1)


def omega_world(Pm, rng, kind, p=0.3):
    """Pm: bins x hosts presence (all present by construction). Returns binary host matrix."""
    nb, n = Pm.shape
    if kind == "null":
        return (rng.random((nb, n)) < p).astype(float)
    if kind == "field":
        f = rng.normal(0, 1.2, nb)
        return (rng.random((nb, n)) < 1 / (1 + np.exp(-(np.log(p / (1 - p)) + f[:, None])))).astype(float)
    if kind == "dol":   # fixed budget: exactly 2 hosts per bin
        X = np.zeros((nb, n))
        for i in range(nb):
            X[i, rng.choice(n, 2, replace=False)] = 1
        return X
    if kind == "xor":   # host 3 expresses iff exactly one of hosts 1, 2 does (prob 0.85); others independent
        X = (rng.random((nb, n)) < 0.5).astype(float)
        par = (X[:, 0] + X[:, 1]) % 2
        flip = rng.random(nb) < 0.15
        X[:, 2] = np.where(flip, 1 - par, par)
        return X
    raise ValueError(kind)


def run_p6(ev, rng, reps_spec=100, reps_om=60):
    pres = T.presence(ev)
    ag_all = pres // 10**9
    ga, cnt = np.unique(ag_all, return_counts=True)
    top = ga[np.argsort(-cnt)][:8]
    pres_bins = {int(g): set((pres[ag_all == g] % 10**9).tolist()) for g in top}
    res = {}
    for name, lam, field in (("null", 0.0, False), ("field", 0.0, True), ("spec0.2", 0.2, False),
                             ("spec0.5", 0.5, False)):
        z, pv = [], []
        reps = reps_spec if lam == 0 else max(reps_spec // 2, 30)
        for _ in range(reps):
            h, e, b = spec_world(pres_bins, rng, lam=lam, field=field, p_host=0.15)
            zz, pp = p6_spec_stat(h, e, b, rng)
            z.append(zz); pv.append(pp)
        res[f"spec_{name}"] = {"reps": reps, "share_z_ge2": float(np.mean(np.array(z) >= 2)),
                               "share_p_lt_0.05": float(np.mean(np.array(pv) < 0.05)), "mean_z": float(np.mean(z)),
                               "n_triples_last": int(len(h))}
        print(f"spec_{name}", json.dumps(res[f"spec_{name}"]), flush=True)
    # O-information on the bins where the 6 most active agents are all present
    hosts6 = top[:6]
    common = set.intersection(*[pres_bins[int(g)] for g in hosts6])
    nb = len(common)
    a = ev.a
    T.presence(ev)
    bins = np.array(sorted(common))
    tod = bins % 12
    Z = np.column_stack([(tod == k).astype(float) for k in np.unique(tod)[1:]] +
                        [np.array([a["bin_exo"].get(b, 0) for b in bins], float),
                         np.log1p(np.array([a["bin_msgs"].get(b, 0) for b in bins], float))])
    for kind in ("null", "field", "dol", "xor"):
        rule, raw_neg, res_neg, oms = [], [], [], []
        for _ in range(reps_om):
            X = omega_world(np.ones((nb, 6)), rng, kind)
            if (X.std(0) == 0).any():
                continue
            om = L.o_information_discrete(X) / 4
            raw = L.o_information(L.field_removed(X, Z)) / 4
            sur = []
            for _s in range(60):
                Xs = L.curveball(X.T.astype(np.int8), rng, n_iter=120).T.astype(float)
                if (Xs.std(0) == 0).any():
                    continue
                sur.append(L.o_information_discrete(Xs) / 4)
            p05 = np.percentile(sur, 5)
            rule.append(om < 0 and om < p05); raw_neg.append(raw < 0); res_neg.append(om < 0); oms.append(om)
        res[f"omega_{kind}"] = {"reps": len(rule), "n_bins": int(nb), "share_rule": float(np.mean(rule)),
                                "share_gauss_fieldremoved_neg": float(np.mean(raw_neg)),
                                "share_discrete_neg": float(np.mean(res_neg)), "mean_omega_discrete": float(np.mean(oms))}
        print(f"omega_{kind}", json.dumps(res[f"omega_{kind}"]), flush=True)
    return res


def main(quick=False):
    ev = L.load()
    rng = np.random.default_rng(20261010)
    t0 = time.time()
    r = 10 if quick else 100
    out = {"p4": run_p4(ev, rng, reps=r), "p5": run_p5(ev, rng, reps=r),
           "p6": run_p6(ev, rng, reps_spec=r, reps_om=(6 if quick else 60))}
    out["seconds"] = time.time() - t0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ("p456_synthetic_quick.json" if quick else "p456_synthetic.json")).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(quick="--quick" in sys.argv)
