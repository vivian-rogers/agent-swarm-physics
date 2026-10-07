"""H133 round 1 on exploration data (non-reserved units that meet the structural precondition).

Per unit:
  O1-O3  conditional logit (h133lib.fit_logit): gamma_nam, gamma_un, gamma_if, held, share, phi; agent-cluster sandwich
         CIs; agent-block bootstrap (B_BOOT) when gamma_nam is estimable; O2 = gamma_nam - gamma_un, O3 = gamma_nam - gamma_if.
  N1     within-project-hour permutation of (N_nam, N_un), score statistic at the fit without them (N_PERM draws).
  O4     background cloglog eta_sw (card model) and the amended variant with ln(1 + n options) (Amendment A2).
  O5     lag profile of the most recent named read about the destination before a hop (0..5 calls).
  E/O    (post hoc) observed / expected chosen rows with a named / unnamed / in-flight read about the destination at the
         fit without read terms (the N1 score, read as a ratio), with the N1 permutation band.
Natives: N2 eta_sw on G51 timer-wake background calls; N3 G40 hub hops in the first 2 active hours; N4 = G31 eta_sw.
Random-effects (DerSimonian-Laird) means by regime group. Writes data/processed/H133-readout-glauber-potts/results/.

Usage: uv run python hypotheses/H133-readout-glauber-potts/analysis/run.py [--units a,b] [--no-boot]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h133lib as L  # noqa: E402

B_BOOT = 200
N_PERM = 1000
RES = L.D / "results"


def contrast(f, a, b):
    if not (f.ok and a in f.beta and b in f.beta):
        return None
    i, j = f.names.index(a), f.names.index(b)
    d = f.beta[a] - f.beta[b]
    s = math.sqrt(max(f.cov[i, i] + f.cov[j, j] - 2 * f.cov[i, j], 0))
    return {"est": d, "se": s, "ci": (d - f.info["tq"] * s, d + f.info["tq"] * s)}


def eo_ratios(sk, n_perm=N_PERM, seed=0):
    """Post hoc: observed / expected chosen rows with x > 0 for nam, un, if, at the fit without the three read terms;
    permutation band from shuffling each read column within project x active-hour cells."""
    rest = ["held", "share"]
    des = L.restricted_design(sk, sk.y, rest)
    if des["calls"].size == 0:
        return None
    B = L._build(sk, des)
    th, ok, _ = L.newton(B)
    Z, Gm, rcp, nC = B["Z"], B["Gm"], B["rcp"], B["nC"]
    u = Z @ th
    mx = np.full(nC, -np.inf)
    np.maximum.at(mx, rcp, u)
    e = np.exp(u - mx[rcp])
    p = (e / (Gm @ e)[rcp])[nC:]
    ch = B["chosen"][nC:]
    ridx = B["ridx"]
    cells = sk.row_cell[ridx]
    rng = np.random.default_rng(seed)
    xs = {f: (sk.X[f][ridx] > 0).astype(float) for f in ("nam", "un", "if")}
    T = {f: L.cell_perm_null(x, ch, cells, n_perm, rng) for f, x in xs.items()}
    out = {}
    for f, x in xs.items():
        O, E = float(ch @ x), float(p @ x)
        out[f] = {"O": O, "E": E, "OE": O / E if E > 0 else None, "perm_p_one_sided": float((1 + np.sum(T[f] >= O - 1e-12)) / (n_perm + 1)),
                  "perm_q95": float(np.quantile(T[f], 0.95)), "perm_q05": float(np.quantile(T[f], 0.05))}
    return out


def lag_profile(unit):
    import polars as pl
    c = pl.read_parquet(L.D / unit / "calls.parquet").sort("agent", "t_call", "turn_id")
    rd = pl.read_parquet(L.D / unit / "reads.parquet").filter(pl.col("n_nam") > 0).select("turn_id", "p")
    c = c.with_row_index("i")
    hops = c.filter(pl.col("hop"))
    prof = np.zeros(6)
    n = 0
    byag = {a: d for (a,), d in c.group_by(["agent"])}
    nam = set(zip(rd["turn_id"].to_list(), rd["p"].to_list()))
    for a, d in byag.items():
        tid = d["turn_id"].to_list()
        hp = d["hop"].to_list()
        ds = d["dst"].to_list()
        for k in range(len(tid)):
            if not hp[k]:
                continue
            for lag in range(6):
                if k - lag < 0:
                    break
                if (tid[k - lag], ds[k]) in nam:
                    prof[lag] += 1
                    n += 1
                    break
    return {"n_hops_with_recent_named_read": n, "share_by_lag": (prof / n).tolist() if n else None,
            "share_lag0_or_1": float(prof[:2].sum() / n) if n else None}


def run_unit(u, boot=True):
    t0 = time.time()
    sk = L.load_skeleton(u)
    r = {"unit": u, "calls": sk.n_calls, "option_rows": int(sk.row_call.size), "births": int((sk.y == -2).sum()),
         "hops_in_options": int((sk.y >= 0).sum())}
    f = L.fit_logit(sk)
    r["logit"] = {"ok": f.ok, "names": f.names, "beta": f.beta, "se": f.se, "ci": f.ci, "chosen_pos": f.chosen_pos,
                  "n_calls": f.n_calls, "n_rows": f.n_rows, "n_hops": f.n_hops, "n_cells": f.n_cells, "G": f.G}
    r["O2"] = contrast(f, "nam", "un")
    r["O3"] = contrast(f, "nam", "if")
    if boot and f.ok and "nam" in f.beta:
        bs = L.bootstrap_weighted(sk, [n for n in f.names if n != "phi"], B_BOOT, seed=7)
        dr = bs["draws"]
        ci = {}
        for n in f.names:
            v = np.array([d.get(n, np.nan) for d in dr], float)
            ci[n] = (float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5)), float(np.nanstd(v, ddof=1)))
        for a, b in (("nam", "un"), ("nam", "if")):
            if a in f.names and b in f.names:
                v = np.array([d.get(a, np.nan) - d.get(b, np.nan) for d in dr], float)
                ci[f"{a}-{b}"] = (float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5)), float(np.nanstd(v, ddof=1)))
        r["boot"] = {"draws": len(dr), "ci": ci, "method": bs["method"]}
    r["N1"] = L.score_perm(sk, L.FEATS, N_PERM, seed=3)
    r["EO_posthoc"] = eo_ratios(sk)
    nopt = L.n_options(sk)
    hop = sk.hop_any
    r["O4_card"] = L.fit_cloglog(sk, hop, sk.bg)
    r["O4_nopt"] = L.fit_cloglog(sk, hop, sk.bg, extra=nopt)
    if u.startswith("51"):
        r["N2_timer_card"] = L.fit_cloglog(sk, hop, sk.bg & sk.timer)
        r["N2_timer_nopt"] = L.fit_cloglog(sk, hop, sk.bg & sk.timer, extra=nopt)
    r["O5"] = lag_profile(u)
    r["secs"] = round(time.time() - t0, 1)
    return r


def native_g40():
    """N3: hops to the kickoff-named hub in the first 2 active hours of G40 (descriptive when not estimable)."""
    import polars as pl
    meta = json.loads((L.D / "40" / "meta.json").read_text())
    kn = set(meta.get("kickoff_named", []))
    sk = L.load_skeleton("40")
    tc = pl.read_parquet(L.D / "40" / "touches.parquet")
    hub = (tc.filter(pl.col("p").is_in(list(kn))).group_by("p").len().sort("len", descending=True))
    if hub.height == 0:
        return {"ok": False, "reason": "no kickoff-named project touched"}
    hp = hub["p"][0]
    hi = sk.projects.index(hp)
    first2 = sk.a < 2 * 3600
    rows = (sk.row_proj == hi) & first2[sk.row_call]
    ch = sk.y[(sk.y >= 0) & first2]
    hub_hops = int(np.sum(sk.row_proj[ch] == hi)) if ch.size else 0
    hub_hops_nam = int(np.sum((sk.row_proj[ch] == hi) & (sk.X["nam"][ch] > 0))) if ch.size else 0
    out = {"hub_hash": hp, "hub_hops_first2h": hub_hops, "hub_hops_with_named_read": hub_hops_nam,
           "hub_option_rows_first2h": int(rows.sum()), "hub_rows_with_named_read": int((rows & (sk.X["nam"] > 0)).sum()),
           "births_first2h": int(np.sum((sk.y == -2) & first2))}
    f = L.fit_logit(sk, call_mask=first2)
    out["logit_first2h"] = {"ok": f.ok, "names": f.names, "beta": f.beta, "ci": f.ci, "chosen_pos": f.chosen_pos,
                            "n_hops": f.n_hops}
    return out


def pool(results, key_fn, units):
    est, se = [], []
    for u in units:
        v = key_fn(results[u])
        if v is None:
            continue
        est.append(v[0])
        se.append(v[1])
    return L.dersimonian_laird(est, se)


def main():
    RES.mkdir(parents=True, exist_ok=True)
    st = json.loads((L.D / "structural_counts.json").read_text())
    reg = {r["unit"]: r["regime"] for r in st}
    units = [r["unit"] for r in st if r["testable"]]
    if "--units" in sys.argv:
        units = sys.argv[sys.argv.index("--units") + 1].split(",")
    boot = "--no-boot" not in sys.argv
    out = {}
    p = RES / "units.json"
    if p.exists():
        out = json.loads(p.read_text())
    for u in units:
        if u in out and "--redo" not in sys.argv:
            continue
        out[u] = run_unit(u, boot=boot)
        out[u]["regime"] = reg[u]
        p.write_text(json.dumps(out, indent=1, default=float))
        r = out[u]
        print(u, reg[u], r["secs"], "s", "chosen_pos", r["logit"]["chosen_pos"], "eta", r["O4_card"].get("eta"),
              r["O4_card"].get("ci"), "eta_nopt", r["O4_nopt"].get("eta"), flush=True)
    res = out
    all_units = sorted(res)
    g23 = [u for u in all_units if res[u]["regime"] != "I"]
    g1 = [u for u in all_units if res[u]["regime"] == "I"]
    g51 = [u for u in all_units if u.startswith("51")]

    def eta(k):
        return lambda r: (r[k]["eta"], r[k]["se"]) if r.get(k, {}).get("ok") else None

    def gam(n):
        def f(r):
            lg = r["logit"]
            if not lg["ok"] or n not in lg["beta"]:
                return None
            b = r.get("boot", {}).get("ci", {}).get(n)
            return (lg["beta"][n], b[2] if b else lg["se"][n])
        return f
    summ = {"eta_card": {"II_III": pool(res, eta("O4_card"), g23), "I": pool(res, eta("O4_card"), g1)},
            "eta_nopt": {"II_III": pool(res, eta("O4_nopt"), g23), "I": pool(res, eta("O4_nopt"), g1)},
            "N2_timer_card": pool(res, eta("N2_timer_card"), g51), "N2_timer_nopt": pool(res, eta("N2_timer_nopt"), g51),
            "N4_G31_card": pool(res, eta("O4_card"), [u for u in g1 if u.startswith("31")]),
            "N4_G31_nopt": pool(res, eta("O4_nopt"), [u for u in g1 if u.startswith("31")]),
            "gamma": {n: {"II_III": pool(res, gam(n), g23), "I": pool(res, gam(n), g1)} for n in ("nam", "un", "if")},
            "estimable": {n: [u for u in all_units if res[u]["logit"]["ok"] and n in res[u]["logit"]["beta"]] for n in ("nam", "un", "if")}}
    # pooled post hoc O/E across units by regime group (sums of O and E)
    for name, us in (("II_III", g23), ("I", g1)):
        for fct in ("nam", "un", "if"):
            O = sum(res[u]["EO_posthoc"][fct]["O"] for u in us if res[u].get("EO_posthoc"))
            E = sum(res[u]["EO_posthoc"][fct]["E"] for u in us if res[u].get("EO_posthoc"))
            summ.setdefault("EO_posthoc_sum", {}).setdefault(name, {})[fct] = {"O": O, "E": E, "OE": O / E if E else None}
    lagn = sum(res[u]["O5"]["n_hops_with_recent_named_read"] for u in g23)
    prof = np.zeros(6)
    for u in g23:
        s = res[u]["O5"]["share_by_lag"]
        if s:
            prof += np.array(s) * res[u]["O5"]["n_hops_with_recent_named_read"]
    summ["O5_II_III"] = {"n": lagn, "share_by_lag": (prof / lagn).tolist() if lagn else None,
                         "share_lag0_or_1": float(prof[:2].sum() / lagn) if lagn else None}
    try:
        summ["N3_G40"] = native_g40()
    except Exception as e:  # noqa: BLE001
        summ["N3_G40"] = {"error": repr(e)[:300]}
    (RES / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
