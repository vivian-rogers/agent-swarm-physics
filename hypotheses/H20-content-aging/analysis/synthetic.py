"""H20 synthetic validation (faithfulness axis F), at village sampling.

Uses only the real *counts* (agent-day presence, statements per agent-day, weekend gaps) of each period plus an
assumed signal-to-noise grid; no real embedding statistic is read. Models: stationary vector OU (one and two
timescales), Box-Cox-clock aging (mu = 0.5, 1), Bouchaud trap model (x = 0.5 aging, x = 1.5 equilibrating),
kickoff quench + stationary (uncorrelated / correlated transient), drift toward ĝ, shared-only vs private-only aging.

Parts (run all by default):
  power     rejection rates of the A test against the stationary null at pseudo-true nuisance parameters
  pipeline  full pipeline (null refitted per dataset): false-positive rate and power
  cv        leave-one-day-out model selection (M0, M0b, MQ, M1, MT) and mu-hat recovery
  pitfalls  within-period centering; statement-count trends; drift toward ĝ (V-g); shared vs private aging
  table     design power of every analyzed period (mu = 0.5, 1; a^2 = 0.05, 0.15, 0.30)
Usage: uv run python hypotheses/H20-content-aging/analysis/synthetic.py [--parts power,pipeline,...] [--fast]
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h20lib as L  # noqa: E402
from h20lib import hc  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

SYN = hc.OUT / "synthetic"
BASE = L.SwarmModel(q=0.4, r=(0.35,), tau=(3.0,), gs=0.5, rs=0.4, es=0.2)
PERIODS_MAIN = [4, 8, 38, 51, 18, 21]


def scenarios(T):
    S0 = BASE
    return {
        "S0 stationary": S0,
        "S0b stationary 2 scales": dataclasses.replace(S0, q=0.3, r=(0.25, 0.2), tau=(1.0, 15.0)),
        "AG mu=0.5": L.alt_model(S0, 0.5, T),
        "AG mu=1": L.alt_model(S0, 1.0, T),
        "TRAP x=0.5": dataclasses.replace(S0, trap_x=0.5, rs=0.0),
        "TRAP x=1.5": dataclasses.replace(S0, trap_x=1.5, rs=0.0),
        "MQ uncorrelated": dataclasses.replace(S0, b2=1.0, tau_q=1.5, kap=0.0),
        "MQ correlated": dataclasses.replace(S0, b2=1.0, tau_q=1.5, kap=1.0),
        "DRIFT to g": dataclasses.replace(S0, drift=0.5, tau_g=5.0),
        "AG shared only": dataclasses.replace(L.alt_model(S0, 0.5, T), rs=1.0),
        "AG private only": dataclasses.replace(L.alt_model(S0, 0.5, T), rs=0.0),
    }


def make_design(cd, a2, n_override=None):
    n = cd["n"] if n_override is None else n_override
    valid = n >= hc.MIN_STMTS
    A = n.shape[0]
    v = np.where(valid, (1 - a2) / np.maximum(n, 1), 0.0)
    return dict(valid=valid, v_true=v, df=np.where(valid, (np.maximum(n, 2) - 1) * 32, 1), a=np.full(A, np.sqrt(a2)))


def sim_stats(model, design, cd, rng, B, stable=None, ghat=None, project=False, center=False):
    rows = []
    T = cd["T"]
    for _ in range(B):
        xb, vv, ok = L.simulate_states(model, design, rng, ghat=ghat)
        if project:
            xb, vv, ok = L.project_states(xb, vv, ok, ghat)
        if center:
            mu = np.array([xb[i][ok[i]].mean(0) if ok[i].any() else np.zeros(xb.shape[-1]) for i in range(len(xb))])
            xb = np.where(ok[..., None], xb - mu[:, None], 0.0)
        rows.append(L.stats_bundle(xb, vv, ok, cd["wk_gap"], T, stable=stable))
    return {k: np.array([r[k] for r in rows], float) for k in rows[0]}


def pseudo_true_null(model, design, cd, rng, nfit=40):
    """Stationary swarm model fitted to the scenario's mean C (what the pipeline would converge to)."""
    T = cd["T"]
    Cs, Cxs = [], []
    for _ in range(nfit):
        xb, vv, ok = L.simulate_states(model, design, rng)
        C, npair = L.two_time(xb, vv, ok)
        Cx, cnt = L.cross_agent_C(xb, vv, ok)
        Cs.append(C); Cxs.append(Cx)
    C = np.nanmean(Cs, 0); Cx = np.nanmean(Cxs, 0)
    return L.fit_null_model(C, npair, Cx, cnt, cd["wk_gap"], T)


def summarize(x):
    x = x[np.isfinite(x)]
    return dict(mean=float(x.mean()) if x.size else None, sd=float(x.std()) if x.size else None, n=int(x.size))


def part_power(cds, rng, B_alt, B_null, a2=0.15):
    out = {}
    for g, cd in cds.items():
        T = cd["T"]
        design = make_design(cd, a2)
        stable = L.stable_subset(design["valid"])
        out[g] = {}
        sc = scenarios(T)
        null_cache = {}
        for name, m in sc.items():
            t0 = time.time()
            if name.startswith("S0 "):
                nm = m
            else:
                nm = pseudo_true_null(m, design, cd, rng)
            key = name
            null_cache[key] = L.null_distribution(nm, design, cd["wk_gap"], T, B_null, rng, stable=stable)
            alt = sim_stats(m, design, cd, rng, B_alt, stable=stable)
            res = {}
            for stat in ("A", "A_c", "A_m", "A_late", "A_early", "K"):
                nd = null_cache[key][stat]
                nd = nd[np.isfinite(nd)]
                if nd.size < 20:
                    continue
                crit = np.quantile(nd, 0.95)
                x = alt[stat][np.isfinite(alt[stat])]
                res[stat] = dict(alt=summarize(alt[stat]), null=summarize(nd), reject=float((x > crit).mean()) if x.size else None)
            res["null_model"] = dataclasses.asdict(nm)
            out[g][name] = res
            print(f"[power] G{g:02d} {name:24s} A={res['A']['alt']['mean']:+.4f} rej={res['A']['reject']:.2f} "
                  f"({time.time() - t0:.1f}s)", flush=True)
    return out


def part_pipeline(cds, rng, n_data, B_null, a2=0.15):
    """Full pipeline per dataset: fit the stationary swarm model to the dataset, simulate the null, p-value."""
    out = {}
    for g, cd in cds.items():
        T = cd["T"]
        design = make_design(cd, a2)
        stable = L.stable_subset(design["valid"])
        out[g] = {}
        for name, m in (("S0 stationary", BASE), ("AG mu=0.5", L.alt_model(BASE, 0.5, T)), ("AG mu=1", L.alt_model(BASE, 1.0, T))):
            t0 = time.time()
            ps = []
            for _ in range(n_data):
                xb, vv, ok = L.simulate_states(m, design, rng)
                C, npair = L.two_time(xb, vv, ok)
                Cx, cnt = L.cross_agent_C(xb, vv, ok)
                nm = L.fit_null_model(C, npair, Cx, cnt, cd["wk_gap"], T)
                obs = L.stats_bundle(xb, vv, ok, cd["wk_gap"], T, stable=stable)
                dsg = L.design_from_states(xb, vv, ok, np.where(ok, cd["n"], 0), 32)
                nd = L.null_distribution(nm, dsg, cd["wk_gap"], T, B_null, rng, stable=stable, with_derived=False)
                ps.append(L.p_upper(obs["A"], nd["A"]))
            ps = np.array(ps)
            out[g][name] = dict(reject_005=float((ps < 0.05).mean()), p_median=float(np.median(ps)), n=int(ps.size))
            print(f"[pipeline] G{g:02d} {name:14s} reject@0.05={out[g][name]['reject_005']:.2f} ({time.time() - t0:.0f}s)",
                  flush=True)
    return out


def part_cv(cds, rng, n_data, a2=0.15):
    out = {}
    for g, cd in cds.items():
        T = cd["T"]
        design = make_design(cd, a2)
        out[g] = {}
        for name, m in scenarios(T).items():
            if name in ("DRIFT to g", "AG shared only", "AG private only"):
                continue
            t0 = time.time()
            wins, mus, cvs = [], [], []
            for _ in range(n_data):
                xb, vv, ok = L.simulate_states(m, design, rng)
                C, npair = L.two_time(xb, vv, ok)
                E = L.entries(C, npair, cd["wk_gap"], tw_min=2)
                fits = {k: L.fit_model(k, E)[0] for k in ("M0", "M0b", "MQ", "M1")}
                cv = L.lodo_cv(E, full_fits=fits)
                cvs.append(cv)
                wins.append(min(cv, key=cv.get))
                mus.append(fits["M1"][3])
            mus = np.array(mus)
            tab = {k: wins.count(k) / len(wins) for k in ("M0", "M0b", "MQ", "M1", "MT")}
            m1_beats_all = float(np.mean([cv["M1"] < min(cv[k] for k in ("M0", "M0b", "MQ", "MT")) for cv in cvs]))
            m1_beats_pre = float(np.mean([cv["M1"] < min(cv["M0"], cv["MQ"]) for cv in cvs]))
            out[g][name] = dict(win_share=tab, m1_beats_M0_MQ=m1_beats_pre, m1_beats_all=m1_beats_all,
                                mu_hat=dict(mean=float(mus.mean()), sd=float(mus.std()), median=float(np.median(mus))))
            print(f"[cv] G{g:02d} {name:24s} M1>M0,MQ {m1_beats_pre:.2f} M1>all {m1_beats_all:.2f} "
                  f"mu_hat {np.median(mus):+.2f}±{mus.std():.2f} wins {tab} ({time.time() - t0:.0f}s)", flush=True)
    return out


def part_pitfalls(cds, rng, B, a2=0.15):
    out = {}
    for g, cd in cds.items():
        T = cd["T"]
        design = make_design(cd, a2)
        stable = L.stable_subset(design["valid"])
        res = {}
        null = sim_stats(BASE, design, cd, rng, B, stable=stable)
        crit = np.nanquantile(null["A"], 0.95)
        # (1) within-period time-mean centering of each agent
        cen = sim_stats(BASE, design, cd, rng, B, stable=stable, center=True)
        res["centering"] = dict(A_uncentered=summarize(null["A"]), A_centered=summarize(cen["A"]),
                                reject_vs_uncentered_null=float(np.nanmean(cen["A"] > crit)))
        # (2) statement counts declining over the period (60 -> 8), stationary latent
        n_tr = np.where(cd["valid"], np.linspace(60, 8, T)[None, :].repeat(cd["A"], 0), 0)
        d_tr = make_design(cd, a2, n_override=n_tr)
        tr = sim_stats(BASE, d_tr, cd, rng, B, stable=stable)
        null_tr = sim_stats(BASE, d_tr, cd, rng, B, stable=stable)
        res["count_trend"] = dict(A=summarize(tr["A"]), reject_vs_constant_count_null=float(np.nanmean(tr["A"] > crit)),
                                  reject_vs_real_count_null=float(np.nanmean(tr["A"] > np.nanquantile(null_tr["A"], 0.95))))
        # (3) drift toward ĝ: raw vs V-g
        ghat = L._unit(rng.standard_normal(32))
        md = dataclasses.replace(BASE, drift=0.5, tau_g=5.0)
        raw = sim_stats(md, design, cd, rng, B, stable=stable, ghat=ghat)
        proj = sim_stats(md, design, cd, rng, B, stable=stable, ghat=ghat, project=True)
        nullp = sim_stats(BASE, design, cd, rng, B, stable=stable, ghat=ghat, project=True)
        res["drift_to_g"] = dict(A_raw=summarize(raw["A"]), reject_raw=float(np.nanmean(raw["A"] > crit)),
                                 A_g=summarize(proj["A"]), reject_g=float(np.nanmean(proj["A"] > np.nanquantile(nullp["A"], 0.95))))
        ag = L.alt_model(BASE, 0.5, T)
        agp = sim_stats(ag, design, cd, rng, B, stable=stable, ghat=ghat, project=True)
        res["aging_after_projection"] = dict(A_g=summarize(agp["A"]),
                                             reject_g=float(np.nanmean(agp["A"] > np.nanquantile(nullp["A"], 0.95))))
        # (4) shared-only vs private-only aging: A, A_c, A_m
        for nm, m in (("shared_only", dataclasses.replace(ag, rs=1.0)), ("private_only", dataclasses.replace(ag, rs=0.0))):
            s = sim_stats(m, design, cd, rng, B, stable=stable)
            res[f"aging_{nm}"] = {k: summarize(s[k]) for k in ("A", "A_c", "A_m")}
            res[f"aging_{nm}"]["reject"] = {k: float(np.nanmean(s[k] > np.nanquantile(null[k], 0.95))) for k in ("A", "A_c", "A_m")}
        out[g] = res
        print(f"[pitfalls] G{g:02d} centering A={res['centering']['A_centered']['mean']:+.4f} "
              f"rej={res['centering']['reject_vs_uncentered_null']:.2f}; count-trend rej(const null)="
              f"{res['count_trend']['reject_vs_constant_count_null']:.2f} rej(real null)={res['count_trend']['reject_vs_real_count_null']:.2f}; "
              f"drift rej raw={res['drift_to_g']['reject_raw']:.2f} V-g={res['drift_to_g']['reject_g']:.2f}", flush=True)
    return out


def part_table(cds_all, rng, B, a2s=(0.05, 0.15, 0.30)):
    out = {}
    for g, cd in cds_all.items():
        T = cd["T"]
        out[g] = {"T": T, "A": cd["A"]}
        for a2 in a2s:
            design = make_design(cd, a2)
            null = L.null_distribution(BASE, design, cd["wk_gap"], T, B, rng, with_derived=False)
            alts = {mu: L.null_distribution(L.alt_model(BASE, mu, T), design, cd["wk_gap"], T, B, rng, with_derived=False)
                    for mu in (0.5, 1.0)}
            for stat in ("A", "A_early", "A_late"):
                nd = null[stat][np.isfinite(null[stat])]
                if nd.size < 20:
                    continue
                crit = np.quantile(nd, 0.95)
                for mu in (0.5, 1.0):
                    out[g][f"{stat}|a2={a2}|mu={mu}"] = float(np.nanmean(alts[mu][stat] > crit))
                    out[g][f"{stat}_alt_mean|a2={a2}|mu={mu}"] = float(np.nanmean(alts[mu][stat]))
                out[g][f"{stat}_null_sd|a2={a2}"] = float(np.nanstd(nd))
        print(f"[table] G{g:02d} T={T} A={cd['A']} power(A, a2=.15, mu=.5)={out[g].get('A|a2=0.15|mu=0.5', float('nan')):.2f} "
              f"(mu=1: {out[g].get('A|a2=0.15|mu=1.0', float('nan')):.2f})", flush=True)
    return out


def lowrank_R(n, neff, rng):
    """Shape factor with an exponential spectrum of the given effective dimension, random basis."""
    best = None
    for kap in np.linspace(0.3, 40, 400):
        w = np.exp(-np.arange(n) / kap); w /= w.sum()
        ne = 1 / (w ** 2).sum()
        if best is None or abs(ne - neff) < abs(best[1] - neff):
            best = (w, ne)
    w = best[0]
    Q, _ = np.linalg.qr(rng.standard_normal((n, n)))
    return np.sqrt(n) * (Q * np.sqrt(w)) @ Q.T


def part_aniso(cds, rng, n_data, B_null, a2=0.15, neff_p=9.0, neff_s=5.0):
    """Amendment 2 check: low-rank stationary data; isotropic vs estimated-shape (anisotropic) null."""
    out = {}
    for g, cd in cds.items():
        T = cd["T"]
        design = make_design(cd, a2)
        out[g] = {}
        conds = (("lowrank stationary", 0.0, True), ("lowrank mu=0.5", 0.5, True), ("isotropic stationary", 0.0, False))
        for name, mu, lowrank in conds:
            t0 = time.time()
            p_iso, p_an, zs = [], [], []
            for _ in range(n_data):
                m = BASE if mu == 0 else L.alt_model(BASE, mu, T)
                if lowrank:
                    m = dataclasses.replace(m, Rs=lowrank_R(32, neff_s, rng), Rp=lowrank_R(32, neff_p, rng))
                xb, vv, ok = L.simulate_states(m, design, rng)
                C, npair = L.two_time(xb, vv, ok)
                Cx, cnt = L.cross_agent_C(xb, vv, ok)
                nm = L.fit_null_model(C, npair, Cx, cnt, cd["wk_gap"], T)
                obs = L.stats_bundle(xb, vv, ok, cd["wk_gap"], T, with_derived=False)
                dsg = L.design_from_states(xb, vv, ok, np.where(ok, cd["n"], 0), 32)
                nd = L.null_distribution(nm, dsg, cd["wk_gap"], T, B_null, rng, with_derived=False)
                p_iso.append(L.p_upper(obs["A"], nd["A"]))
                Rs, Rp, _, _ = L.estimate_shapes(xb, vv, ok)
                nma = dataclasses.replace(nm, Rs=Rs, Rp=Rp)
                nda = L.null_distribution(nma, dsg, cd["wk_gap"], T, B_null, rng, with_derived=False)
                p_an.append(L.p_upper(obs["A"], nda["A"]))
                zs.append((obs["A"] - np.nanmean(nd["A"])) / np.nanstd(nd["A"]))
            p_iso, p_an, zs = map(np.array, (p_iso, p_an, zs))
            out[g][name] = dict(reject_iso_null=float(np.mean(p_iso < 0.05)), reject_aniso_null=float(np.mean(p_an < 0.05)),
                                reject_iso_two_sided=float(np.mean((p_iso < 0.025) | (p_iso > 0.975))),
                                reject_aniso_two_sided=float(np.mean((p_an < 0.025) | (p_an > 0.975))),
                                z_sd_vs_iso_null=float(np.std(zs)), n=int(n_data))
            print(f"[aniso] G{g:02d} {name:22s} rej iso {out[g][name]['reject_iso_null']:.2f} aniso {out[g][name]['reject_aniso_null']:.2f} "
                  f"(two-sided iso {out[g][name]['reject_iso_two_sided']:.2f} aniso {out[g][name]['reject_aniso_two_sided']:.2f}); "
                  f"z-SD vs iso null {out[g][name]['z_sd_vs_iso_null']:.2f} ({time.time() - t0:.0f}s)", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", default="power,pipeline,cv,pitfalls,table")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--suffix", default="")
    ap.add_argument("--periods", default=",".join(map(str, PERIODS_MAIN)))
    args = ap.parse_args()
    SYN.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(hc.SEED)
    st = pl.read_parquet(hc.OUT / "statements.parquet", columns=["goal_no", "agent", "d"])
    days = pl.read_parquet(hc.OUT / "days.parquet")
    pers = [int(x) for x in args.periods.split(",")]
    cds = {g: L.count_design(g, st, days) for g in pers}
    f = 0.25 if args.fast else 1.0
    parts = args.parts.split(",")
    for part in parts:
        t0 = time.time()
        if part == "power":
            res = part_power(cds, rng, int(300 * f), int(500 * f))
        elif part == "pipeline":
            res = part_pipeline({g: cds[g] for g in pers if g in (4, 8, 38, 51)}, rng, int(60 * f), int(200 * f))
        elif part == "cv":
            res = part_cv({g: cds[g] for g in pers if g in (8, 38)}, rng, int(20 * f))
        elif part == "pitfalls":
            res = part_pitfalls(cds, rng, int(300 * f))
        elif part == "aniso":
            res = part_aniso({g: cds[g] for g in pers}, rng, int(40 * f), int(150 * f))
        elif part == "table":
            cds_all = {g: L.count_design(g, st, days) for g in hc.ALL_PERIODS}
            res = part_table(cds_all, rng, int(300 * f))
        else:
            raise ValueError(part)
        (SYN / f"{part}{args.suffix}.json").write_text(json.dumps({str(k): v for k, v in res.items()}, indent=1, default=float))
        print(f"== {part} done in {time.time() - t0:.0f}s", flush=True)
    hc.write_provenance({"seed": hc.SEED, "base_model": dataclasses.asdict(BASE), "parts": parts, "fast": args.fast,
                         "inputs_used": "counts only (agent-day presence, statements per agent-day, weekend gaps)"},
                        ["H20/statements.parquet (counts)", "H20/days.parquet"],
                        "hypotheses/H20-content-aging/analysis/synthetic.py")


if __name__ == "__main__":
    main()
