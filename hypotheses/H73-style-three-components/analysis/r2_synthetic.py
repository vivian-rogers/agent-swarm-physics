"""H73 round 2 synthetic validation on the real message, pair and segment schedules (before any real-data statistic).

Noise = each agent's real style deviations permuted within agent x unit (time, day and context structure destroyed)
plus agent-day jitter (5% of per-message variance). Planted structure per world (see the card's pre-registration).
Output: data/processed/H73-style-three-components/r2/synthetic.json
Usage: uv run python hypotheses/H73-style-three-components/analysis/r2_synthetic.py [--only acc,rh,trans,cv] [--reps N]
"""
from __future__ import annotations
import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import r2lib as R  # noqa: E402
import r2_run as RUN  # noqa: E402

OUTP = R.R2 / ("synthetic_smoke.json" if os.environ.get("H73_SMOKE") else "synthetic.json")


class World:
    def __init__(self, m: pl.DataFrame, X: np.ndarray, seed: int):
        self.m = m
        self.rng = np.random.default_rng(seed)
        self.agent = m["agent"].to_numpy(); self.unit = m["unit_id"].to_numpy(); self.day = m["pt_date"].to_numpy()
        self.Dreal = R.deviations(X, self.agent, self.unit, clip=None)
        self.Vbar = float((self.Dreal ** 2).sum(1).mean() / X.shape[1])
        key = np.array([f"{a}|{u}" for a, u in zip(self.agent, self.unit)])
        _, self.au = np.unique(key, return_inverse=True)
        kd = np.array([f"{a}|{d}" for a, d in zip(self.agent, self.day)])
        _, self.ad = np.unique(kd, return_inverse=True)
        tc = m["t_call"].fill_null(m["t"]) if "t_call" in m.columns else m["t"]
        self.tcall = tc.dt.epoch("us").to_numpy() / 1e6
        self.t = m["t"].dt.epoch("us").to_numpy() / 1e6
        self.callage = np.clip(self.t - self.tcall, 0, None)
        rk = np.array([f"{r}|{d}" for r, d in zip(m["room"].to_numpy(), self.day)])
        _, self.rd = np.unique(rk, return_inverse=True)

    def noise(self) -> np.ndarray:
        dim = self.Dreal.shape[1]
        idx = np.arange(len(self.au))
        out = idx.copy()
        order = np.argsort(self.au, kind="stable")
        g = self.au[order]
        cuts = np.flatnonzero(g[1:] != g[:-1]) + 1
        for seg in np.split(order, cuts):
            out[seg] = self.rng.permutation(seg)
        E = self.Dreal[out]
        J = self.rng.normal(0, np.sqrt(0.05 * self.Vbar), (self.ad.max() + 1, dim))[self.ad]
        return E + J

    def ou(self, tau: float, share: float, times: np.ndarray, groups: np.ndarray) -> np.ndarray:
        dim = self.Dreal.shape[1]
        sig = np.sqrt(share * self.Vbar)
        out = np.zeros((len(times), dim))
        order = np.lexsort((times, groups))
        g, tt = groups[order], times[order]
        prev_g, prev_t, e = -1, 0.0, None
        Z = self.rng.normal(0, sig, (len(times), dim))
        for n, i in enumerate(order):
            if g[n] != prev_g:
                e = Z[n].copy()
            else:
                ph = np.exp(-max(tt[n] - prev_t, 0.0) / tau)
                e = ph * e + np.sqrt(1 - ph ** 2) * Z[n]
            out[i] = e
            prev_g, prev_t = g[n], tt[n]
        return out


# ============================================================================================ accommodation
def acc_world(W: World, kind: str, gamma: float, P_all: pl.DataFrame) -> np.ndarray:
    X = W.noise()
    if kind in ("W1", "W2", "W3", "W13", "W2b"):
        drv = W.ou(1200.0, 0.10, W.tcall, W.rd) + W.ou(120.0, 0.05, W.tcall, W.rd)
        if kind in ("W3", "W13", "W2b"):
            lam = np.exp(-W.callage / 60.0)
            drv = drv * (lam / np.sqrt((lam ** 2).mean()))[:, None]
        X = X + drv
    if kind in ("W2", "W2b") and gamma:
        rd = P_all.filter(pl.col("cls") == "read")
        b, a = rd["B_row"].to_numpy(), rd["A_row"].to_numpy()
        add = np.zeros_like(X)
        np.add.at(add, b, X[a] - X[a].mean(0))
        X = X + gamma * add
    return X


def run_acc(m, P, reps: int) -> dict:
    design = os.environ.get("H73_ACC_DESIGN", "lag")
    pops = RUN.acc_populations(m, P, design)
    pops = {k: v for k, v in pops.items() if k in ("III", "I")}
    X16 = RUN.style(m, R.TC16)
    W = World(m, X16, 7)
    worlds = [("W0", 0.0), ("W1", 0.0), ("W3", 0.0), ("W2", 0.02), ("W2", 0.05), ("W2b", 0.05)]
    out = {}
    for kind, g in worlds:
        key = f"{kind}_g{g}"
        rec = {"III": [], "I": []}
        t0 = time.time()
        for r in range(reps):
            X = acc_world(W, kind, g, P)
            D = R.deviations(X, W.agent, W.unit)
            for reg in ("III", "I"):
                fn = R.accommodation_rd if os.environ.get("H73_ACC_EST") == "rd" else R.accommodation
                p = fn(D, pops[reg], n_boot=200, seed=r)["pooled"]
                rec[reg].append((p["gamma"], p["lo"], p["hi"], p["level_inflight"]) if p else (np.nan,) * 4)
        summ = {}
        for reg, v in rec.items():
            a = np.array(v, dtype=float)
            summ[reg] = {"gamma_mean": float(np.nanmean(a[:, 0])), "gamma_sd": float(np.nanstd(a[:, 0])),
                         "ci_gt0": float(np.mean(a[:, 1] > 0)), "ci_lt0": float(np.mean(a[:, 2] < 0)),
                         "ci_excl0": float(np.mean((a[:, 1] > 0) | (a[:, 2] < 0))),
                         "ci_hi_mean": float(np.nanmean(a[:, 2])), "level_inflight": float(np.nanmean(a[:, 3]))}
        out[key] = summ
        print(key, json.dumps(summ), f"{time.time() - t0:.0f}s", flush=True)
    return out


# ============================================================================================ reset-and-hold
def rh_world(W: World, kind: str, m: pl.DataFrame, regs: list) -> np.ndarray:
    X = W.noise()
    dim = X.shape[1]
    cu = ((m["ctx_mode"] == "cu") & m["regime"].is_in(regs)).to_numpy()
    seg = m["seg"].fill_null(-1).to_numpy(); segk = m["seg_k"].fill_null(0).to_numpy()
    key = W.agent.astype(np.int64) * 10_000_000 + seg
    kap = 0.05 * W.Vbar
    if kind == "S_RH":
        uk, inv = np.unique(key[cu], return_inverse=True)
        O = W.rng.normal(0, np.sqrt(kap), (len(uk), dim))
        X[cu] += O[inv]
    elif kind == "S_carry":
        uk, inv = np.unique(key[cu], return_inverse=True)
        O = np.zeros((len(uk), dim))
        ag_of = uk // 10_000_000
        prev = {}
        Z = W.rng.normal(0, np.sqrt(kap), (len(uk), dim))
        for i in np.argsort(uk):
            a = ag_of[i]
            O[i] = 0.6 * prev[a] + np.sqrt(1 - 0.36) * Z[i] if a in prev else Z[i]
            prev[a] = O[i]
        X[cu] += O[inv]
    elif kind.startswith("S_OU"):
        phi = 0.7 if kind == "S_OU7" else 0.9
        sig = np.sqrt(kap * (1 - phi ** 2))
        ix = np.where(cu)[0]
        order = ix[np.lexsort((segk[ix], key[ix]))]
        e = np.zeros(dim); pk = None
        for i in order:
            if key[i] != pk:
                e = W.rng.normal(0, sig, dim)        # e_1 = sigma xi (e_0 = 0 at the reset)
            else:
                e = phi * e + W.rng.normal(0, sig, dim)
            X[i] += e; pk = key[i]
    return X


def run_rh(m, reps: int) -> dict:
    X17 = RUN.style(m, R.TC)
    W = World(m, X17, 9)
    out = {}
    for nm, regs in (("I_II", ["I", "II"]), ("III", ["III"])):
        Rp = R.rh_pairs(m, regs)
        for kind in ("S0", "S_RH", "S_OU7", "S_OU9", "S_carry"):
            rec = []
            t0 = time.time()
            for r in range(reps if nm == "I_II" else max(reps // 3, 4)):
                X = rh_world(W, kind, m, regs)
                D = R.deviations(X, W.agent, W.unit)
                s = R.rh_stats(D, Rp, n_boot=200, seed=r)
                rec.append(s)
            ks = ["dC1", "dC3", "dC_first", "dC_late", "r_first_late", "r_dC3_dC1", "kappa_seg", "carry", "growth",
                  "common_share", "T"]
            summ = {k: float(np.nanmean([s[k] for s in rec])) for k in ks}
            summ["dC1_ci_gt0"] = float(np.mean([s["dC1_ci"][0] > 0 for s in rec]))
            summ["first_ci_gt0"] = float(np.mean([s["dC_first_ci"][0] > 0 for s in rec]))
            summ["T_ci_gt_half"] = float(np.mean([s["T_ci"][0] > 0.5 for s in rec]))
            summ["r_ge_half"] = float(np.mean([(s["r_first_late"] >= 0.5) for s in rec]))
            summ["r_lt_033"] = float(np.mean([(s["r_first_late"] < 0.33) for s in rec]))
            summ["r_ci_lo_ge_033"] = float(np.mean([(s["r_first_late_ci"][0] >= 0.33) for s in rec]))
            summ["dC3dC1_ge_half"] = float(np.mean([(s["r_dC3_dC1"] >= 0.5) for s in rec]))
            summ["carry_ok"] = float(np.mean([(s["carry"] < 0.3) and (s["carry_ci"][1] < 0.5) for s in rec]))
            summ["carry_lo_gt_half"] = float(np.mean([s["carry_ci"][0] > 0.5 for s in rec]))
            summ["growth_ci_gt0"] = float(np.mean([s["growth_ci"][0] > 0 for s in rec]))
            summ["kappa_in_band"] = float(np.mean([0.02 <= s["kappa_seg"] <= 0.10 for s in rec]))
            summ["Vbar"] = float(np.mean([s["Vbar"] for s in rec]))

            def p2(s):
                g_ok = (s["growth_ci"][0] <= 0) or (s["growth"] < 0.5 * s["kappa_seg"] * s["Vbar"])
                return (s["r_first_late"] >= 0.5) and (s["r_dC3_dC1"] >= 0.5) and g_ok
            summ["P2_pass"] = float(np.mean([p2(s) for s in rec]))
            summ["P3_pass"] = float(np.mean([(s["carry"] < 0.3) and (s["carry_ci"][1] < 0.5) and (s["common_share"] < 0.25) for s in rec]))
            summ["P3_point"] = float(np.mean([(s["carry"] < 0.3) and (s["common_share"] < 0.25) for s in rec]))
            summ["reading_pass"] = float(np.mean([(s["T_ci"][0] > 0.5) and (s["dC_first_ci"][0] > 0) and p2(s)
                                                  and (s["carry"] < 0.3) and (s["carry_ci"][1] < 0.5) and (s["common_share"] < 0.25)
                                                  and (0.02 <= s["kappa_seg"] <= 0.10) for s in rec]))
            summ["kill"] = float(np.mean([(s["dC1_ci"][0] <= 0) or (s["r_first_late"] < 0.33) or (s["carry_ci"][0] > 0.5) for s in rec]))
            out[f"{nm}_{kind}"] = summ
            print(nm, kind, json.dumps(summ), f"{time.time() - t0:.0f}s", flush=True)
    return out


# ============================================================================================ transients
def run_trans(m, reps: int) -> dict:
    X17 = RUN.style(m, R.TC)
    inc = RUN.incumbents51(m)
    sel = (((m["regime"] == "III") & m["goal_no"].is_between(36, 44)) | (m["goal_no"] == 51)).to_numpy() \
        & m["agent"].is_in(inc).to_numpy()
    agent = m["agent"].to_numpy(); day = m["pt_date"].to_numpy()
    out = {}
    rng = np.random.default_rng(5)
    D = R.deviations(X17, agent, np.zeros(len(agent)), clip=None)   # per-agent deviations (no unit split)
    Vbar = float((D[sel] ** 2).sum(1).mean() / D.shape[1])
    for kind in ("null", "transient", "persistent"):
        rec = []
        t0 = time.time()
        for r in range(reps):
            X = np.zeros_like(X17)
            # permute within agent over the whole pre + #51 sample: no shift
            for g in np.unique(agent[sel]):
                ix = np.where(sel & (agent == g))[0]
                X[ix] = D[rng.permutation(ix)]
            post10 = sel & (agent == 10) & (m["goal_no"] == 51).to_numpy()
            if kind != "null":
                v = rng.normal(0, 1, X.shape[1]); v = v / np.sqrt((v ** 2).mean()) * np.sqrt(0.3 * Vbar)
                k = np.array([(dt.date.fromisoformat(d) - dt.date.fromisoformat(RUN.ONSET51)).days for d in day[post10]])
                amp = np.exp(-k / 3.0) if kind == "transient" else np.ones(len(k))
                X[post10] += amp[:, None] * v[None]
            res = RUN.onset51(m, X, n_boot=100, seed=r)
            a10 = res["agents"].get("10")
            rec.append(a10)
        ok = [a for a in rec if a]
        summ = {"tau_med": float(np.median([a["fit"]["tau"] for a in ok])),
                "A_ci_gt0": float(np.mean([a["A_ci"][0] > 0 for a in ok])),
                "tau_in_band": float(np.mean([0.5 <= a["fit"]["tau"] <= 14 and a["tau_ci"][1] < 30 for a in ok])),
                "late_le_q95": float(np.mean([a["late"] <= a["placebo_q95"] for a in ok])),
                "persistent_detected": float(np.mean([a["late_ci"][0] > a["placebo_mean"] for a in ok])),
                "late_w": float(np.mean([a["late_w"] for a in ok])), "placebo_mean": float(np.mean([a["placebo_mean"] for a in ok])),
                "P1_pass": float(np.mean([(a["A_ci"][0] > 0) and (0.5 <= a["fit"]["tau"] <= 14) and (a["tau_ci"][1] < 30)
                                          and (a["late"] <= a["placebo_q95"]) for a in ok])),
                "P1_pass_A3": float(np.mean([(a["A_ci"][0] > 0) and (0.5 <= a["fit"]["tau"] <= 14) and (a["tau_ci"][1] < 30)
                                             and not (a["late_ci"][0] > a["placebo_mean"]) for a in ok])),
                "early_gt_mid": float(np.mean([a["early"] > a["mid"] for a in ok])),
                "early_mean": float(np.mean([a["early"] for a in ok])), "placebo_med": float(np.mean([a["placebo_med"] for a in ok]))}
        out[kind] = summ
        print("trans", kind, json.dumps(summ), f"{time.time() - t0:.0f}s", flush=True)
    return out


# ============================================================================================ Cv decomposition
def run_cv(m, reps: int) -> dict:
    X17 = RUN.style(m, R.TC)
    W = World(m, X17, 13)
    out = {}
    for g in (41, 18):
        ix = (m["goal_no"] == g).to_numpy()
        mg = m.filter(pl.Series(ix))
        Cv = R.cv_block(mg)
        for kind in ("null", "planted"):
            rec = []
            for r in range(reps):
                X = W.noise()
                if kind == "planted":
                    Bv = W.rng.normal(0, 1, (Cv.shape[1], X.shape[1]))
                    eff = Cv @ Bv
                    eff *= np.sqrt(0.01 * W.Vbar / ((eff ** 2).sum(1).mean() / X.shape[1]))
                    X[ix] += eff
                res = RUN.run_cv(m, X, n_perm=49, goals=[g])[f"G{g:02d}"]
                rec.append(res)
            out[f"G{g}_{kind}"] = {"u_Cv": float(np.mean([x["u_Cv"] for x in rec])),
                                   "u_Cf": float(np.mean([x["u_Cf"] for x in rec])),
                                   "p_lt05": float(np.mean([x["p_Cv"] < 0.05 for x in rec]))}
            print("cv", g, kind, out[f"G{g}_{kind}"], flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="acc,rh,trans,cv")
    ap.add_argument("--reps", type=int, default=20)
    args = ap.parse_args()
    m, P = R.load()
    out = json.loads(OUTP.read_text()) if OUTP.exists() else {}
    for k in args.only.split(","):
        t0 = time.time()
        out[k] = {"acc": run_acc, "rh": run_rh, "trans": run_trans, "cv": run_cv}[k](m, P, args.reps) if k == "acc" \
            else {"rh": run_rh, "trans": run_trans, "cv": run_cv}[k](m, args.reps)
        out[k]["_run"] = {"at": dt.datetime.now(dt.UTC).isoformat(), "reps": args.reps, "secs": time.time() - t0}
        OUTP.write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
