"""H35 synthetic validation (axis F): can the pipeline recover the nudger's information, work and efficiencies?

Generative model (regime-III-like; event times in seconds, h16lib row format):
  - cold start, then alternating active bursts (Exp(mu_i) long, active rows Poisson 1/min) and pause chains;
  - a pause has a declared duration (5 min w.p. 0.8, 15 min 0.15, 30 min 0.05); at its expiry (gate k) the agent escapes
    w.p. sigmoid(a_i + theta ln k + eff), else re-pauses (with a 'glance' w.p. 0.5: one active row, re-pause < 120 s);
  - kicks received during a pause are read at the gate; one kick counts (saturation): eff = max over unread kicks of
    gamma_type(k), gamma_N(k) = g0 + lam (ln k - ln 3) for nudges, gamma_A(k) = s * gamma_N(k) for agent mentions;
  - kicks to an active agent do nothing;
  - agent mentions arrive as an exogenous Poisson process (independent of state).
Policies (the controller sees the event stream): logged-like 'repeated-idling' (at PAUSE k >= k0, cooldown, fire w.p. q),
random-minute (Poisson nudges regardless of state), gate-once(k*) and frontier pi_beta (decide at each PAUSE).
Truth: per-gate dp of adding a nudge (exact from the model), minutes per escape and the single-nudge A30 effect by Monte
Carlo replay, and large-sample information. Estimators: exactly the h35lib functions used on real data.

Usage: uv run python hypotheses/H35-nudger-maxwell-demon/analysis/synthetic.py [--quick]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h35lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import special  # noqa: E402

SYN = L.OUT / "synthetic"
DECL = np.array([300.0, 900.0, 1800.0])
DECL_P = np.array([0.8, 0.15, 0.05])
RESET_S = 150.0   # a burst shorter than this does not reset the trap age (matches TS2r's 120-s glance rule)


class World:
    def __init__(self, n_agents, n_days, T_min, theta, g0, lam, s_men, rng, men_rate=0.004):
        self.n_agents, self.n_days, self.T = n_agents, n_days, T_min * 60.0
        self.theta, self.g0, self.lam, self.s_men, self.men_rate = theta, g0, lam, s_men, men_rate
        self.a = rng.normal(-0.4, 0.7, n_agents)
        self.mu = 720.0 * np.exp(rng.normal(0, 0.4, n_agents))   # mean burst length (s)

    def gamma_n(self, k):
        return self.g0 + self.lam * (np.log(k) - np.log(3.0))

    def gamma_a(self, k):
        return self.s_men * self.gamma_n(k)


def burst_rows(t, L_, rng):
    n = rng.poisson(L_ / 60.0)
    return np.sort(np.r_[t, t + rng.uniform(0, L_, n), t + L_])


def sim_agent_day(w: World, i: int, policy: dict, rng, t0: float, exo_nudge_rate: float = 0.0):
    """One agent-day. Returns rows dict, nudge times, mention times, gate truth records."""
    T = t0 + w.T
    men = t0 + np.sort(rng.uniform(0, w.T, rng.poisson(w.men_rate * w.T / 60.0)))
    exo = t0 + np.sort(rng.uniform(0, w.T, rng.poisson(exo_nudge_rate * w.T / 60.0))) if exo_nudge_rate > 0 else np.zeros(0)
    acts, pts, pss, nud, truth = [], [], [], list(exo), []
    last_n = -np.inf
    t = t0 + rng.exponential(180.0)
    k_prev = 0
    while t < T:
        L_ = rng.exponential(w.mu[i])
        acts.append(burst_rows(t, L_, rng))
        te = t + L_
        if te >= T:
            break
        # trap age resets only after sustained work (a burst >= RESET_S); shorter bursts continue the chain (TS2r-like)
        k, tp = (1 if (L_ >= RESET_S or k_prev == 0) else k_prev + 1), te + 1.0
        escaped = False
        while tp < T:
            d = float(rng.choice(DECL, p=DECL_P))
            pts.append(tp); pss.append(d)
            texp = tp + d
            # controller decision at the PAUSE event
            fire = False
            kind = policy["kind"]
            if kind == "logged":
                fire = (k >= policy["k0"]) and (tp - last_n >= policy["cool"]) and (rng.random() < policy["q"])
            elif kind == "gate_once":
                fire = (k == policy["kstar"]) and (rng.random() < policy["f"])
            elif kind == "cells":   # pi(x) over (Kb, declb)
                kb = int(L.k_bin(np.array([k]))[0]); db = int(L.decl_bin(np.array([d]))[0])
                fire = rng.random() < policy["pi"][kb - 1, db]
            if fire:
                tn = tp + rng.uniform(5.0, 90.0)
                if tn < min(texp, T):
                    nud.append(tn); last_n = tn
            if texp >= T:
                break
            nn = np.array(nud)
            has_n = bool(np.any((nn >= tp) & (nn < texp))) if len(nn) else False
            has_m = bool(np.any((men >= tp) & (men < texp)))
            base = w.a[i] + w.theta * np.log(k)
            gN, gA = w.gamma_n(k), w.gamma_a(k)
            eff_m = gA if has_m else 0.0
            eff = max(gN if has_n else 0.0, eff_m)
            p = special.expit(base + eff)
            dp = special.expit(base + max(gN, eff_m)) - special.expit(base + eff_m)
            truth.append((tp, k, d, int(has_n), int(has_m), float(dp)))
            if rng.random() < p:
                t = texp + rng.uniform(2.0, 20.0)
                escaped = True
                k_prev = k
                break
            if rng.random() < 0.5:
                acts.append(np.array([texp + 5.0]))
                tp = texp + rng.uniform(20.0, 60.0)
            else:
                tp = texp + 2.0
            k += 1
        if not escaped:
            break
    act = np.sort(np.concatenate(acts)) if acts else np.zeros(0)
    act = act[act <= T]
    rows = {"act": act, "pause_t": np.array(pts), "pause_s": np.array(pss), "wait_t": np.zeros(0),
            "turn_t": np.zeros(0), "turn_err": np.zeros(0, bool), "turn_bash": np.zeros(0, bool), "turn_h": np.zeros(0, np.uint64)}
    return rows, np.sort(np.array(nud)), men, truth


def sim_world(w: World, policy: dict, rng, exo_nudge_rate=0.0):
    rows, W, K, truth = {}, {}, {}, []
    for dd in range(w.n_days):
        d = f"S{dd:03d}"
        t0 = 1.0e9 + dd * 86400.0
        W[d] = {"t0": t0, "t1": t0 + w.T, "regime": "III", "goal_no": 0, "hours": w.T / 3600, "weekday": 2}
        for i in range(w.n_agents):
            r, nt, men, tr = sim_agent_day(w, i, policy, rng, t0, exo_nudge_rate)
            if len(r["act"]) == 0:
                continue
            rows[(i, d)] = r
            ka = K.setdefault(i, {"N_tgt": [], "A_men": []})
            ka["N_tgt"].append(nt); ka["A_men"].append(men)
            for x in tr:
                truth.append((i, d) + x)
    for i, ka in K.items():
        for c in list(ka):
            ka[c] = np.sort(np.concatenate(ka[c])) if ka[c] else np.zeros(0)
    tr = pl.DataFrame(truth, schema=["agent", "pt_date", "t_pause", "k", "decl", "has_n", "has_m", "dp_true"], orient="row")
    return rows, W, K, tr


def forward_a30(w: World, i, k, tp, d, unread_n, unread_m, t_nudge, T_end, rng, reps=30):
    """Single-nudge A30 (minutes m+1..m+30 after the nudge minute, no further kicks): mean over replays."""
    m0 = np.floor(t_nudge / 60.0)
    out = []
    for _ in range(reps):
        acts = []
        kk, tpp, dd = k, tp, d
        un, um = unread_n, unread_m
        horizon = (m0 + 31) * 60.0
        t = None
        while tpp < min(horizon, T_end):
            texp = tpp + dd
            if texp >= min(horizon, T_end):
                break
            base = w.a[i] + w.theta * np.log(kk)
            eff = max(w.gamma_n(kk) if un else 0.0, w.gamma_a(kk) if um else 0.0)
            un = um = False
            if rng.random() < special.expit(base + eff):
                t = texp + rng.uniform(2.0, 20.0)
                while t < horizon:
                    L_ = rng.exponential(w.mu[i]); acts.append(burst_rows(t, L_, rng)); te = t + L_
                    # after the burst: a chain without kicks (fresh only after sustained work)
                    kk2, tp2 = (1 if L_ >= RESET_S else kk + 1), te + 1.0
                    esc = False
                    while tp2 < horizon:
                        d2 = float(rng.choice(DECL, p=DECL_P)); tx = tp2 + d2
                        if tx >= horizon:
                            break
                        if rng.random() < special.expit(w.a[i] + w.theta * np.log(kk2)):
                            t = tx + rng.uniform(2.0, 20.0); esc = True; kk = kk2; break
                        tp2 = tx + 2.0; kk2 += 1
                    if not esc:
                        break
                break
            if rng.random() < 0.5:
                acts.append(np.array([texp + 5.0])); tpp = texp + rng.uniform(20.0, 60.0)
            else:
                tpp = texp + 2.0
            kk += 1
            dd = float(rng.choice(DECL, p=DECL_P))
        a = np.concatenate(acts) if acts else np.zeros(0)
        mins = np.unique(np.floor(a / 60.0))
        out.append(int(np.sum((mins >= m0 + 1) & (mins <= m0 + 30))))
    return float(np.mean(out))


def gate_cells(gt: pl.DataFrame, gcol: str):
    """p(x), pi_log(x), g(x) over x = (Kb 1..4) x (declb 0..2) from a gate table with per-gate values in gcol."""
    p = np.zeros((4, 3)); m = np.zeros((4, 3)); gs = np.zeros((4, 3))
    for kb, db, mm, gv in gt.select("Kb", "declb", "M", gcol).iter_rows():
        if kb < 1 or gv is None or not np.isfinite(gv):
            continue
        p[kb - 1, db] += 1; m[kb - 1, db] += mm; gs[kb - 1, db] += gv
    ok = p > 0
    pi = np.where(ok, m / np.maximum(p, 1), 0.0)
    g = np.where(ok, gs / np.maximum(p, 1), 0.0)
    return p[ok], pi[ok], g[ok], ok


def run_pipeline(rows, W, K, truth, rng, n_null=20, B=200, mc_reps=0, w=None):
    gates = L.gate_table(rows, W, K)
    grid = L.build_grid(rows, W, gates, K)
    info = L.info_block(grid, rng, n_null=n_null)
    work = L.work_minute(grid, rng, B=B)
    gates = gates.join(truth.select("agent", "pt_date", "t_pause", "dp_true", "has_n"), on=["agent", "pt_date", "t_pause"], how="left")
    gates = gates.with_columns(pl.Series("dp_hat", L.crossfit_dp(gates)))
    fit = L.gate_fit(gates)
    Bk = L.gate_minutes_per_escape(gates)
    gate_I = L.mi(L.codes(gates["Kb"].to_numpy(), gates["declb"].to_numpy()), gates["M"].to_numpy()) / L.LN2
    res = {"n_nudges": int(sum(len(v.get("N_tgt", [])) for v in K.values())), "n_gates": gates.height,
           "n_nudged_gates": int(gates["M"].sum()), "info": info,
           "att_first_pastonly": work["first_pastonly"]["y30"], "att_first_H04": work["first_futureisolated_H04"]["y30"],
           "att_repeat": work["repeat_pastonly"]["y30"], "placebo": work["first_pastonly"]["ypre"],
           "gate_beta": dict(zip(fit["names"], fit["beta"].tolist())), "gate_se": dict(zip(fit["names"], fit["se"].tolist())),
           "B_per_escape": Bk, "gate_I_bits_MM": gate_I}
    gates = gates.with_columns(pl.Series("dp_hat_sep", L.crossfit_dp(gates, "separate")))
    Bmap = {k: (v if np.isfinite(v) else np.nan) for k, v in Bk.items()}
    gates = gates.with_columns(pl.col("Kb").replace_strict(Bmap, default=None, return_dtype=pl.Float64).alias("B_k"))
    gates = gates.with_columns((pl.col("dp_hat") * pl.col("B_k")).alias("g_min_hat"))
    gk = gates.filter((pl.col("Kb") >= 1) & pl.col("dp_hat").is_not_null() & pl.col("dp_hat").is_not_nan()
                      & pl.col("dp_true").is_not_null())
    eff = {}
    for lab, col in (("true", "dp_true"), ("est", "dp_hat"), ("est_separate", "dp_hat_sep"), ("est_minutes", "g_min_hat")):
        s0 = gk.filter(pl.col(col).is_not_null() & pl.col(col).is_not_nan())
        if s0.height == 0:
            continue
        p, pi, g, ok = gate_cells(s0, col)
        e = L.efficiencies(p, pi, g)
        if "error" in e:
            eff[lab] = e
            continue
        e["gate_once"] = {}
        for ks in (1, 2, 3):
            s = s0.filter(pl.col("k_r") == ks)
            e["gate_once"][ks] = float(s[col].mean()) if s.height else float("nan")
        e["ratio_gate_once1_vs_logged"] = e["gate_once"][1] / e["V_log_per_nudge"] if e["V_log_per_nudge"] else float("nan")
        e["ratio_gate_once2_vs_logged"] = e["gate_once"][2] / e["V_log_per_nudge"] if e["V_log_per_nudge"] else float("nan")
        e["logged_mean_direct"] = float(s0.filter(pl.col("M") == 1)[col].mean())
        eff[lab] = e
    res["eff"] = eff
    res["n_mention_gates"] = int(gates["dir_other"].sum())
    if mc_reps and w is not None:
        # single-nudge A30 truth for a sample of first nudges (past-only treated set)
        idx = work["first_pastonly"]["_idx"]
        sel = rng.choice(idx, size=min(300, len(idx)), replace=False) if len(idx) else idx
        sub = grid[sel]
        tr_by = {}
        for (a, d), s in truth.group_by(["agent", "pt_date"]):
            tr_by[(int(a), d)] = s.sort("t_pause")
        diffs = []
        for a, d, mnt in sub.select("agent", "pt_date", "minute").iter_rows():
            t0 = W[d]["t0"]
            tn = t0 + 60.0 * mnt + 30.0
            s = tr_by.get((int(a), d))
            if s is None:
                continue
            j = int(np.searchsorted(s["t_pause"].to_numpy(), tn, "right") - 1)
            if j < 0:
                continue
            k, tp, dd, hm = int(s["k"][j]), float(s["t_pause"][j]), float(s["decl"][j]), bool(s["has_m"][j])
            if tn >= tp + dd:
                continue
            f1 = forward_a30(w, int(a), k, tp, dd, True, hm, t0 + 60.0 * mnt, W[d]["t1"], rng, mc_reps)
            f0 = forward_a30(w, int(a), k, tp, dd, False, hm, t0 + 60.0 * mnt, W[d]["t1"], rng, mc_reps)
            diffs.append(f1 - f0)
        res["att_true_single_nudge_mc"] = float(np.mean(diffs)) if diffs else float("nan")
        res["att_true_n"] = len(diffs)
    return res


SCEN = {
    # name: world params, logged policy
    "S1_inefficient": dict(theta=-0.5, g0=np.log(2.0), lam=-0.3, s_men=0.8, policy=dict(kind="logged", k0=4, cool=1800.0, q=0.5)),
    "S2_efficient": dict(theta=-0.5, g0=np.log(2.0), lam=-0.3, s_men=0.8, policy=dict(kind="gate_once", kstar=1, f=0.12)),
    "S3_flat": dict(theta=0.0, g0=np.log(2.0), lam=0.0, s_men=0.8, policy=dict(kind="logged", k0=4, cool=1800.0, q=0.5)),
}
SIZES = {"G51like": dict(n_agents=30, n_days=33, T_min=480), "small": dict(n_agents=12, n_days=5, T_min=240),
         "G38like": dict(n_agents=12, n_days=17, T_min=240)}


def calibrate_q(sc, size, rng, target):
    """Pick the logged policy's firing probability so the nudge count is near the target (one quick world)."""
    pol = dict(sc["policy"])
    key = "q" if pol["kind"] == "logged" else "f"
    for _ in range(6):
        w = World(**size, theta=sc["theta"], g0=sc["g0"], lam=sc["lam"], s_men=sc["s_men"], rng=rng)
        rows, W, K, tr = sim_world(w, pol, rng)
        n = sum(len(v["N_tgt"]) for v in K.values())
        if n == 0:
            pol[key] = min(1.0, pol[key] * 3)
            continue
        pol[key] = float(np.clip(pol[key] * target / n, 1e-3, 1.0))
        if abs(n - target) / target < 0.15:
            break
    return pol


def main():
    quick = "--quick" in sys.argv
    only = None
    if "--sizes" in sys.argv:
        only = sys.argv[sys.argv.index("--sizes") + 1].split(",")
    t_start = time.time()
    rng = np.random.default_rng(L.SEED + (0 if only is None else 7))
    fpath = SYN / "synthetic_results.json"
    if only is not None and fpath.exists():
        out = L.json.loads(fpath.read_text())
    else:
        out = {"design": {"scenarios": {k: {kk: (vv if not isinstance(vv, float) else round(vv, 4)) for kk, vv in v.items()} for k, v in SCEN.items()},
                          "sizes": SIZES}, "results": {}}
    out["design"]["sizes"] = SIZES
    reps = {"G51like": 3 if quick else 6, "small": 6 if quick else 20, "G38like": 4 if quick else 10}
    targets = {"G51like": 700, "small": 25, "G38like": 110}
    for sname, sc in SCEN.items():
        for zname, size in SIZES.items():
            if only is not None and zname not in only:
                continue
            if only is None and zname == "G38like":
                continue
            pol = calibrate_q(sc, size, rng, targets[zname])
            rr = []
            for rep in range(reps[zname]):
                w = World(**size, theta=sc["theta"], g0=sc["g0"], lam=sc["lam"], s_men=sc["s_men"], rng=rng)
                rows, W, K, tr = sim_world(w, pol, rng)
                mc = 40 if (zname == "G51like" and rep < 3) else 0
                try:
                    res = run_pipeline(rows, W, K, tr, rng, n_null=10 if quick else 20, B=200, mc_reps=mc, w=w)
                except Exception as ex:  # report and continue (small worlds can have no nudged gates in a fold)
                    res = {"error": repr(ex)}
                rr.append(res)
                print(sname, zname, rep, {k: res.get(k) for k in ("n_nudges", "n_nudged_gates")},
                      round(time.time() - t_start), "s", flush=True)
            out["results"][f"{sname}|{zname}"] = {"policy": pol, "reps": rr}
            L.jdump(out, fpath)
    if only is not None:
        print("done", round(time.time() - t_start, 1), "s")
        return
    # large-sample information truth for the logged policies (one big world each)
    big = {}
    for sname, sc in SCEN.items():
        pol = out["results"][f"{sname}|G51like"]["policy"]
        w = World(n_agents=60, n_days=60, T_min=480, theta=sc["theta"], g0=sc["g0"], lam=sc["lam"], s_men=sc["s_men"], rng=rng)
        rows, W, K, tr = sim_world(w, pol, rng)
        gates = L.gate_table(rows, W, K)
        grid = L.build_grid(rows, W, gates, K)
        m = grid["M"].to_numpy()
        X = L.codes(grid["Db"].to_numpy(), grid["Gb"].to_numpy(), grid["Kb"].to_numpy())
        r = m.mean()
        big[sname] = {"bits_per_nudge_minute_X": L.mi(X, m, mm=False) / L.LN2 / r,
                      "gate_I_bits": L.mi(L.codes(gates["Kb"].to_numpy(), gates["declb"].to_numpy()), gates["M"].to_numpy(), mm=False) / L.LN2,
                      "n_epochs": int(len(m)), "n_nudges": int(m.sum())}
        print("truth-big", sname, big[sname], flush=True)
    out["truth_big"] = big
    out["seconds"] = round(time.time() - t_start, 1)
    L.jdump(out, SYN / "synthetic_results.json")
    L.write_provenance(SYN, "hypotheses/H35-nudger-maxwell-demon/analysis/synthetic.py", [], {"seed": L.SEED, "quick": quick, "reps": reps})
    print("done", out["seconds"], "s")


if __name__ == "__main__":
    main()
