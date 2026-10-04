"""H97 synthetic validation (axis F), run before the real analysis.

Vector-spin swarms in d = 32 at the real structure of every eligible transition (agents, statement counts per segment,
placebo boundaries; no content), calibrated per regime on ordinary placebo boundaries (calibration.json: statement
resultant, between-agent spread, placebo memory beta0; no kickoff direction used). Statements z = unit(s + e).
Agent state s_i = c (common) + a_i (persistent agent offset, share ALPHA of the deviation variance) + u_i (topic part).
Ordinary days: u' = rho0 u + sqrt(1 - rho0^2) fresh. Scenarios at the kickoff:
  H     restoring force: u(day1) = rho0 (1 - chi_ip) u(prev) + fresh; chi_ip = agent effect + kickoff noise (agent share 0.7)
  Hn    as H but chi_ip has no agent effect (agent share 0)
  R0    pure translation: u(day1) = rho0 u + fresh (chi = 0); the common part moves along k
  R1    common target: a_i and u reset (day-1 deviation fresh only, small)
  R2    longitudinal only: the k components of a_i and u reset; transverse keep rho0
  R4    constant speed along k (fixed step toward the target), transverse rho0 (1 - chi)
  R5    H plus a day-1 overshoot along k beyond the settled target
The real pipeline (h97lib.analyze_transition, dl_meta, constancy) is applied unchanged.
Writes data/processed/H97-quench-restoring-force/synthetic/results.json.
Usage: uv run python analysis/synthetic.py [--reps 60]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h97lib as L  # noqa: E402
from calibrate import placebo_boundaries  # noqa: E402

D = 32
ALPHA = 0.3
CHI_MEAN, CHI_AGENT_SD, CHI_KICK_SD = 0.5, 0.15, 0.10


def structure():
    """Real structure: per eligible transition, agents and counts (prev, day1, plateau) and placebo boundaries."""
    trs = pl.read_parquet(L.DATA / "transitions.parquet").filter((pl.col("kind") == "kickoff") & pl.col("same_regime"))
    out = []
    for tr in trs.iter_rows(named=True):
        stmt, _ = L.load_design(tr["design"])
        c = lambda m: dict(stmt.filter(m).group_by("agent").len().iter_rows())  # noqa: E731
        prev, day1, plat = c(pl.col("seg") == "prev"), c(pl.col("seg") == "day1"), c(pl.col("seg") == "plateau")
        ag = sorted(a for a in set(prev) & set(day1) if prev[a] >= L.MIN_STMT and day1[a] >= L.MIN_STMT)
        if len(ag) < L.MIN_N_AGENT:
            continue
        pls = []
        for g, d0, d1 in placebo_boundaries(stmt, tr):
            x = c((pl.col("goal_no") == g) & (pl.col("pt_date") == d0)); y = c((pl.col("goal_no") == g) & (pl.col("pt_date") == d1))
            pa = sorted(a for a in set(x) & set(y) if x[a] >= L.MIN_STMT and y[a] >= L.MIN_STMT)
            if len(pa) >= L.MIN_N_TRANSITION:
                pls.append({a: (x[a], y[a]) for a in pa})
        out.append(dict(design=tr["design"], regime=tr["regime"], date=tr["first_day"],
                        kick={a: (prev[a], day1[a], plat.get(a, 0)) for a in ag}, plac=pls))
    return out


def regime_params(cal):
    P = {}
    for reg, c in cal.items():
        R = min(c["resultant_median"], 0.9)
        s_norm = R / np.sqrt(1 - R ** 2)                     # |s| with |e| ~ 1
        dev2 = c["spread_median"] * (s_norm ** 2 + 1)         # deviation variance in s space
        dev2 = min(dev2, 0.8 * s_norm ** 2)
        common = np.sqrt(max(s_norm ** 2 - dev2, 0.05))
        rho0 = float(np.clip((c["beta0_full_median"] - ALPHA) / (1 - ALPHA), 0.05, 0.95))
        P[reg] = dict(common=common, dev_sd=np.sqrt(dev2 / D), rho0=rho0)
    return P


def stmts(rng, s, n):
    n = int(min(n, 150))
    Z = s[None, :] + rng.normal(0, 1 / np.sqrt(D), (n, D))
    return Z / np.linalg.norm(Z, axis=1, keepdims=True)


def unit(v):
    return v / np.linalg.norm(v)


def simulate_rep(struct, P, scen, rng):
    """One replicate over all transitions. Returns {variant: (per-transition results, chi rows)} for variants
    white (raw statement vectors) and center (agent leave-period-out mean subtracted, as in the real variant)."""
    agents_all = sorted({a for t in struct for a in t["kick"]})
    agent_eff = {a: rng.normal(0, CHI_AGENT_SD) for a in agents_all}
    chi_mean = CHI_MEAN * (0.5 if scen == "Hweak" else 1.0)
    out = {"white": ([], []), "center": ([], [])}
    for t in struct:
        p = P[t["regime"]]; sd = p["dev_sd"]; rho0 = p["rho0"]
        a_sd = sd * np.sqrt(ALPHA); u_sd = sd * np.sqrt(1 - ALPHA)
        k = unit(rng.normal(size=D))
        c_prev = unit(rng.normal(size=D)) * p["common"]
        target = unit(rng.normal(size=D)) * p["common"] * 0.6 + k * p["common"] * 0.8
        a_i = {a: rng.normal(0, a_sd, D) for a in t["kick"]}
        u_prev = {a: rng.normal(0, u_sd, D) for a in t["kick"]}
        fresh = lambda: rng.normal(0, u_sd, D)  # noqa: E731
        c_other = unit(rng.normal(size=D)) * p["common"] * 0.5   # regime mean seen in the agent's other periods
        chis = {}
        for a in t["kick"]:
            if scen == "Hn":
                chis[a] = float(np.clip(chi_mean + rng.normal(0, np.hypot(CHI_AGENT_SD, CHI_KICK_SD)), 0.02, 1))
            else:
                chis[a] = float(np.clip(chi_mean + agent_eff[a] + rng.normal(0, CHI_KICK_SD), 0.02, 1))
        rbar = rho0 * (1 - np.mean(list(chis.values())))
        c_day1 = target + rbar * (c_prev - target)          # the common mode relaxes with the mean memory (scalar law)
        if scen == "R6":
            c_day1 = target                                 # common mode jumps fully; individual offsets keep memory
        if scen == "R5":
            c_day1 = c_day1 + 0.5 * p["common"] * k          # overshoot along k beyond the settled target
        segs, platT_vals, rows = {}, {}, []
        for a, (n0, n1, n2) in t["kick"].items():
            chi = chis[a]; ai, ui = a_i[a], u_prev[a]
            x_state = c_prev + ai + ui
            if scen in ("H", "Hn", "Hweak", "R5", "R6"):
                rk = rho0 * (1 - chi)
                y_state = c_day1 + ai + rk * ui + np.sqrt(1 - rk ** 2) * fresh()
            elif scen == "R0":
                y_state = c_prev + 0.8 * p["common"] * k + ai + rho0 * ui + np.sqrt(1 - rho0 ** 2) * fresh()
                chi = 0.0
            elif scen == "R1":
                y_state = target + 0.3 * fresh()
                chi = 1.0
            elif scen == "R2":
                v = ai + rho0 * ui + np.sqrt(1 - rho0 ** 2) * fresh()
                v = v - (v @ k) * k + (fresh() @ k) * k * 0.3
                y_state = target + v
                chi = np.nan
            elif scen == "R4":
                rk = rho0 * (1 - chi)
                v = ai + rk * ui + fresh() * np.sqrt(1 - rk ** 2)
                uk = x_state @ k; Tk = (target + ai) @ k
                newk = uk + np.sign(Tk - uk) * min(abs(Tk - uk), 0.5 * p["common"])
                y_state = target + v
                y_state = y_state - (y_state @ k) * k + newk * k
            X, Yd = stmts(rng, x_state, n0), stmts(rng, y_state, n1)
            Pl = stmts(rng, target + ai + 0.5 * fresh(), n2) if n2 >= L.MIN_STMT else None
            # leave-period-out agent mean (as the real centering): other periods share a_i, not c or u
            cen = stmts(rng, c_other + ai + 0.3 * fresh(), 300).mean(0)
            segs[a] = (X, Yd, Pl, cen)
            rows.append(dict(design=t["design"], agent=a, first_day=t["date"], true_chi=float(chi)))
        pl_raw = []
        for pb in t["plac"]:
            bd = {}
            cp = unit(rng.normal(size=D)) * p["common"]
            for a, (n0, n1) in pb.items():
                ai = rng.normal(0, a_sd, D); ui = rng.normal(0, u_sd, D)
                cen = stmts(rng, c_other + ai + 0.3 * rng.normal(0, u_sd, D), 300).mean(0)
                bd[a] = (stmts(rng, cp + ai + ui, n0),
                         stmts(rng, cp + ai + rho0 * ui + np.sqrt(1 - rho0 ** 2) * rng.normal(0, u_sd, D), n1), cen)
            pl_raw.append(bd)
        for var in ("white", "center"):
            sub = (lambda M, c: M - c) if var == "center" else (lambda M, c: M)
            kick_bd = {a: (sub(X, c), sub(Yd, c)) for a, (X, Yd, Pl, c) in segs.items()}
            pv = {a: float((sub(Pl, c) @ k).mean()) for a, (X, Yd, Pl, c) in segs.items() if Pl is not None}
            tot = sum(pv.values()); m = len(pv)
            platT = {a: (tot - v) / (m - 1) for a, v in pv.items()} if m > 1 else {}
            platT["_all"] = tot / m if m else np.nan
            pl_bds = [{a: (sub(x, c), sub(y, c)) for a, (x, y, c) in bd.items()} for bd in pl_raw]
            r = L.analyze_transition(kick_bd, pl_bds, platT, k, n_splits=10, n_boot=0, seed=int(rng.integers(1e9)))
            r["design"] = t["design"]
            cm = dict(zip(r["agents"], r["chi_mem_i"]))
            rr = [dict(row, chi_mem=float(cm[row["agent"]])) for row in rows if row["agent"] in cm]
            out[var][0].append(r); out[var][1].extend(rr)
    return out


def verdicts(res_tr, chi_rows, n_perm=200):
    big = [r for r in res_tr if r["N"] >= L.MIN_N_TRANSITION and r["n_placebo"] > 0]
    dr = np.array([r["drho_full"] for r in big]); ser = np.array([r["se_drho_full"] for r in big])
    mr = L.dl_meta(dr, ser)
    p1r = (mr["mean"] - 1.645 * mr["se"] > 0) and (np.mean(dr > 0) >= 2 / 3)
    isor = L.dl_meta([r["iso_diff_rho"] for r in big], [r["se_iso_diff_rho"] for r in big])
    p2r_pass = (abs(isor["mean"]) < 0.2) and (isor["mean"] - 1.645 * isor["se"] < 0 < isor["mean"] + 1.645 * isor["se"])
    p2r_fail = (isor["mean"] + 1.645 * isor["se"] < 0) and (isor["mean"] <= -0.2)
    db = np.array([r["dbeta_full"] for r in big]); se = np.array([r["se_dbeta_full"] for r in big])
    m = L.dl_meta(db, se)
    p1 = (m["mean"] - 1.645 * m["se"] > 0) and (np.mean(db > 0) >= 2 / 3)
    p1_fail = (m["mean"] <= 0) or (np.mean(db > 0) <= 0.5)
    iso = L.dl_meta([r["iso_diff"] for r in big], [r["se_iso_diff"] for r in big])
    p2_pass = (abs(iso["mean"]) < 0.2) and (iso["mean"] - 1.645 * iso["se"] < 0 < iso["mean"] + 1.645 * iso["se"])
    p2_fail = (iso["mean"] + 1.645 * iso["se"] < 0) and (iso["mean"] <= -0.2)
    sa = L.dl_meta([r.get("shape_a", np.nan) for r in big], [r.get("se_shape_a", np.nan) for r in big])
    sb = L.dl_meta([r.get("shape_b", np.nan) for r in big], [r.get("se_shape_b", np.nan) for r in big])
    p3_slope = sb["mean"] - 1.645 * sb["se"] > 0
    p3_int0 = sa["mean"] - 1.645 * sa["se"] < 0 < sa["mean"] + 1.645 * sa["se"]
    p3_over = sa["mean"] - 1.645 * sa["se"] > 0
    cdf = pl.DataFrame([c for c in chi_rows if "chi_mem" in c])
    cons = L.constancy(cdf, "chi_mem", n_perm=n_perm)
    p4 = (cons["r"] >= 0.3) and (cons["p_r"] < 0.05) and (cons["u"] >= 0.3) and (cons["p_u"] < 0.05)
    # IV vs truth: mean true memory relative
    return dict(drho_mean=mr["mean"], p1_rho=bool(p1r), iso_rho=isor["mean"], p2r_pass=bool(p2r_pass),
                p2r_fail=bool(p2r_fail), dbeta_mean=m["mean"], dbeta_se=m["se"], p1=bool(p1), p1_fail=bool(p1_fail), iso_mean=iso["mean"],
                p2_pass=bool(p2_pass), p2_fail=bool(p2_fail), shape_a=sa["mean"], shape_b=sb["mean"],
                p3_slope=bool(p3_slope), p3_int0=bool(p3_int0), p3_over=bool(p3_over),
                r=cons["r"], u=cons["u"], p_r=cons["p_r"], p4=bool(p4), p4r=bool(cons["r"] >= 0.3 and cons["p_r"] < 0.05),
                beta_kick_med=float(np.median([r["beta_full"] for r in big])),
                beta0_med=float(np.median([r["beta0_full"] for r in big])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=60)
    ap.add_argument("--scen", default="H,Hn,Hweak,R0,R1,R2,R4,R5,R6")
    args = ap.parse_args()
    cal = json.loads((L.DATA / "synthetic/calibration.json").read_text())
    P = regime_params(cal)
    st = structure()
    print("transitions:", len(st), "params:", {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in P.items()})
    out = {"params": P, "alpha": ALPHA, "chi": [CHI_MEAN, CHI_AGENT_SD, CHI_KICK_SD], "reps": args.reps, "scenarios": {}}
    for scen in args.scen.split(","):
        rng = np.random.default_rng(abs(hash(scen)) % 2 ** 32)
        rows = {"white": [], "center": []}
        for rep in range(args.reps):
            o = simulate_rep(st, P, scen, rng)
            for var in rows:
                rows[var].append(verdicts(*o[var]))
        for var in rows:
            df = pl.DataFrame(rows[var])
            summ = {c: float(df[c].mean()) for c in df.columns}
            summ.update({f"{c}_q10": float(df[c].quantile(0.1)) for c in ("dbeta_mean", "iso_mean", "shape_a", "r", "u")})
            summ.update({f"{c}_q90": float(df[c].quantile(0.9)) for c in ("dbeta_mean", "iso_mean", "shape_a", "r", "u")})
            out["scenarios"][f"{scen}|{var}"] = summ
            print(scen, var, {k: round(v, 3) for k, v in summ.items() if not k.endswith(("_q10", "_q90"))}, flush=True)
    (L.DATA / "synthetic/results.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
