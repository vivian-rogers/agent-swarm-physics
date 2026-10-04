"""H129 analysis per unit-channel: A_3, A_cyc, m_2 with the per-agent reversal null and an agent bootstrap; Hodge
curl C_2 with the detailed-balance null; the age walker W1* calibrated to (m_2, return share) as the reference; dwell
hazards; hop rate vs H93's habit; verdicts, P1-P6, natives, estimates rows.

Writes data/processed/H129-project-cycle-currents/results/{units.json, score.json}.
Usage: uv run python hypotheses/H129-project-cycle-currents/analysis/run.py [--no-estimates] [--nref 400]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h129lib as L  # noqa: E402


def load(g, ch):
    o = L.D / f"G{g:02d}"
    return pl.read_parquet(o / f"hops_{ch}.parquet"), pl.read_parquet(o / f"visits_{ch}.parquet")


def rank_from(h):
    r = dict(zip(h["src"].to_list(), h["src_rank"].to_list()))
    r.update(dict(zip(h["dst"].to_list(), h["dst_rank"].to_list())))
    return r


def boot_ci(M, n=1000, rng=None):
    rng = rng or np.random.default_rng(0)
    k = M.shape[0]
    out = {"A3": [], "Acyc": [], "m2": []}
    for _ in range(n):
        idx = rng.integers(0, k, k)
        s = L.stats_from_counts(M[idx].sum(0))
        for key in out:
            out[key].append(s[key])
    return {key: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5)), float(np.nanstd(v))] for key, v in out.items()}


def analyse(g, ch, unit, h, v, nref, rng):
    seq = L.seqs(h)
    rank = rank_from(h)
    for x in v["repo"].to_list():
        rank.setdefault(x, 10**9)
    M = L.agent_counts(seq, rank)
    st = L.stats_from_counts(M.sum(0))
    r = {"goal_no": g, "channel": ch, "unit": unit, "n_agents": len(seq), "n_hops": int(h.height),
         "n_projects": len(set(h["src"].to_list()) | set(h["dst"].to_list())), **{k: st[k] for k in
         ("A3", "L2", "L3", "Acyc", "m2", "n_mono", "n_tri")}, "counts": st["counts"],
         "return_share": L.return_share(seq), "direct_share": float(h["direct"].mean()) if h.height else None}
    tot = st["counts"]
    r["testable_tri"] = bool(tot["omn"] + tot["nmo"] >= 10 and st["n_tri"] >= 20)
    fn = L.flip_null(M, 2000, rng)
    p = lambda null, x: float((np.sum(null >= x) + 1) / (len(null) + 1))  # noqa: E731
    r["p_flip"] = {k: p(fn[k], st[k]) for k in ("A3", "Acyc", "m2")}
    r["boot"] = boot_ci(M, 1000, rng)
    hd = L.hodge(h)
    r["C2"], r["kappa_c"], r["n_edges"], r["cycle_rank"] = hd["C2"], hd["kappa_c"], hd["n_edges"], hd["cycle_rank"]
    r["testable_curl"] = bool(h.height >= 30 and hd["n_nodes"] >= 4 and hd["cycle_rank"] >= 2)
    r["p_db_C2"] = p(L.db_null(hd, 2000, rng), hd["C2"]) if hd["n_edges"] else None
    r["dwell"] = L.dwell_hazard(v)
    # hop rate (work): hops per 100 own calls
    if (r["testable_tri"] or r["testable_curl"]) and nref > 0:
        sk = L.skeleton(h, v)
        rk = L.rank_of({}, sk["names"])   # placeholder; replaced by the real ranks below
        rk = {n: rank.get(n, 10**9) for n in sk["names"]}
        cal = L.calibrate(sk, rk, st["m2"], r["return_share"], rng, n_per=10)
        ref = L.reference(sk, rk, cal["lam"], cal["b"], rng, n=nref)
        r["W1star"] = {**cal, **{f"q95_{k}": float(np.nanpercentile(ref[k], 95)) for k in ref},
                       **{f"med_{k}": float(np.nanmedian(ref[k])) for k in ref}}
        r["p_ref"] = {"A3": p(ref["A3"], st["A3"]), "Acyc": p(ref["Acyc"], st["Acyc"]),
                      "C2": p(ref["C2"], hd["C2"]) if np.isfinite(hd["C2"]) else None}
    return r


def verdict(r, shared):
    if not shared:
        return "descriptive"
    if not r["testable_tri"]:
        return "descriptive"
    if r["p_flip"]["A3"] >= 0.05:
        return "failed"
    if r["p_flip"]["Acyc"] < 0.05 and r.get("p_ref", {}).get("Acyc", 1) < 0.05:
        return "supported"
    return "mixed"


def habit_b_own():
    out = {}
    for g in L.GOALS:
        f = L.ROOT / f"data/processed/H93-brock-durlauf-project-choice/results/G{g:02d}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        try:
            m = d["work"]["fits"]["M4"]
            if m.get("pool", {}).get("k"):
                us = list(m["units"].values())
                vals = [u["theta"][u["names"].index("prev")] for u in us if u.get("ok") and "prev" in u["names"]]
                if vals:
                    out[g] = float(np.mean(vals))
        except Exception:
            pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    ap.add_argument("--nref", type=int, default=400)
    a = ap.parse_args()
    t0 = time.time()
    res = {}
    for g in L.GOALS:
        for ch in ("work", "attention"):
            h, v = load(g, ch)
            units = sorted(set(h["unit"].to_list()) | set(v["unit"].to_list()))
            for u in units:
                rng = np.random.default_rng(zlib.crc32(f"{g}|{ch}|{u}".encode()))
                hu, vu = h.filter(pl.col("unit") == u), v.filter(pl.col("unit") == u)
                if hu.height < 3:
                    res[f"{u}|{ch}"] = {"goal_no": g, "channel": ch, "unit": u, "n_hops": hu.height, "testable_tri": False,
                                        "testable_curl": False, "verdict": "descriptive"}
                    continue
                r = analyse(g, ch, u, hu, vu, a.nref, rng)
                r["shared"] = g not in L.OWN
                r["verdict"] = verdict(r, r["shared"])
                res[f"{u}|{ch}"] = r
                print(f"{u}|{ch} hops {r['n_hops']} tri {r['n_tri']} {r['verdict']} {time.time() - t0:.0f}s", flush=True)
        # G44 rooms (native N3): split hops by DQ6 room assignment
        if g == 44:
            gt = pl.read_parquet(L.ROOT / "data/processed/shared/ground_truth_labels.parquet").filter(
                (pl.col("label_kind") == "room_assignment") & (pl.col("goal_no") == 44) & pl.col("preferred") & ~pl.col("holdout"))
            for room in ("best", "rest"):
                ag = gt.filter(pl.col("value") == room)["agent"].cast(pl.Int16).to_list()
                for ch in ("work", "attention"):
                    h, v = load(g, ch)
                    hu, vu = h.filter(pl.col("agent").is_in(ag)), v.filter(pl.col("agent").is_in(ag))
                    rng = np.random.default_rng(zlib.crc32(f"44{room}|{ch}".encode()))
                    if hu.height < 3:
                        continue
                    r = analyse(g, ch, f"G44{room}", hu, vu, a.nref, rng)
                    r["shared"] = True
                    r["verdict"] = verdict(r, True)
                    res[f"G44{room}|{ch}"] = r
    # hop rate per unit (work) and H93 habit
    hb = habit_b_own()
    rates = hop_rates()
    out = L.D / "results"
    out.mkdir(parents=True, exist_ok=True)
    score = score_all(res, hb, rates)
    dflt = lambda o: o.item() if isinstance(o, np.generic) else str(o)  # noqa: E731
    (out / "units.json").write_text(json.dumps(res, indent=1, default=dflt))
    (out / "score.json").write_text(json.dumps(score, indent=1, default=dflt))
    print(json.dumps({k: v for k, v in score.items() if k != "table"}, indent=1, default=str))
    if not a.no_estimates:
        write_rows(res, rates)


def hop_rates():
    """Work-channel hops per 100 own calls per unit (calls of agents with >= 1 host label in the unit)."""
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    out = {}
    for g in L.GOALS:
        h, v = load(g, "work")
        days = L.RH.period_days(g)
        calls = L.RH.load_calls(g, days)
        um = L.units_of(g)
        calls = calls.with_columns(pl.col("pt_date").replace_strict(um, default=None).alias("unit"))
        for u in sorted(set(v["unit"].to_list())):
            ag = set(v.filter(pl.col("unit") == u)["agent"].to_list())
            nc = calls.filter((pl.col("unit") == u) & pl.col("agent").cast(pl.Int16).is_in(list(ag))).height
            nh = h.filter(pl.col("unit") == u).height
            out[u] = {"hops": nh, "calls": nc, "rate_per_100": 100 * nh / nc if nc else None, "goal_no": g}
    return out


def score_all(res, hb, rates):
    wk = {k: r for k, r in res.items() if k.endswith("|work") and not k.startswith("G44b") and not k.startswith("G44r")}
    at = {k: r for k, r in res.items() if k.endswith("|attention") and not k.startswith("G44b") and not k.startswith("G44r")}
    both = {**wk, **at}
    sh_tri = [k for k, r in both.items() if r.get("shared") and r.get("testable_tri")]
    p1 = [k for k in sh_tri if both[k]["p_flip"]["A3"] < 0.05 and both[k]["A3"] > 0]
    p2 = [k for k in sh_tri if both[k]["p_flip"]["Acyc"] < 0.05 and both[k].get("p_ref", {}).get("Acyc", 1) < 0.05]
    sh_curl = [k for k, r in wk.items() if r.get("shared") and r.get("testable_curl")]
    p3 = [k for k in sh_curl if (wk[k]["p_db_C2"] or 1) < 0.05 and (wk[k].get("p_ref", {}).get("C2") or 1) < 0.05]
    t4 = [k for k, r in both.items() if r.get("testable_tri") or r.get("testable_curl")]
    p4 = [k for k in t4 if both[k]["m2"] > 0 and both[k]["p_flip"]["m2"] < 0.05]
    dw = [k for k, r in both.items() if isinstance(r.get("dwell"), dict) and r["dwell"].get("testable")]
    geo = [k for k in dw if both[k]["dwell"]["gamma_ci"][0] <= 0 <= both[k]["dwell"]["gamma_ci"][1]]
    aging = [k for k in dw if both[k]["dwell"]["gamma_ci"][1] < 0]
    per_g = {}
    for u, x in rates.items():
        if x["rate_per_100"] is not None:
            per_g.setdefault(x["goal_no"], []).append(x["rate_per_100"])
    gs = [g for g in hb if g in per_g]
    rho = spearmanr([np.mean(per_g[g]) for g in gs], [hb[g] for g in gs]) if len(gs) >= 4 else None
    own = [k for k, r in wk.items() if not r.get("shared") and r.get("testable_tri")]
    shw = [k for k, r in wk.items() if r.get("shared") and r.get("testable_tri")]
    sc = {"P1": {"testable": sh_tri, "pass_units": p1, "frac": len(p1) / len(sh_tri) if sh_tri else None,
                 "pass": bool(sh_tri) and len(p1) >= 2 / 3 * len(sh_tri)},
          "P2": {"pass_units": p2, "frac": len(p2) / len(sh_tri) if sh_tri else None,
                 "pass": bool(sh_tri) and len(p2) >= 0.5 * len(sh_tri)},
          "P3": {"testable": sh_curl, "pass_units": p3, "pass": bool(sh_curl) and len(p3) >= 0.5 * len(sh_curl)},
          "P4": {"testable": t4, "pass_units": p4, "frac": len(p4) / len(t4) if t4 else None,
                 "pass": bool(t4) and len(p4) >= 2 / 3 * len(t4)},
          "P5a": {"testable": dw, "geometric": geo, "aging": aging, "pass": bool(dw) and len(geo) >= 2 / 3 * len(dw)},
          "P5b": {"periods": gs, "rho": float(rho.statistic) if rho else None, "p": float(rho.pvalue) if rho else None,
                  "pass": bool(rho is not None and rho.statistic < 0)},
          "P6": {"own_testable": own, "shared_testable": shw,
                 "own_med_absAcyc": float(np.median([abs(wk[k]["Acyc"]) for k in own])) if own else None,
                 "shared_med_absAcyc": float(np.median([abs(wk[k]["Acyc"]) for k in shw])) if shw else None,
                 "own_med_rate": float(np.median([rates[u]["rate_per_100"] for u in rates if rates[u]["goal_no"] in L.OWN
                                                  and rates[u]["rate_per_100"] is not None])),
                 "shared_med_rate": float(np.median([rates[u]["rate_per_100"] for u in rates if rates[u]["goal_no"] not in L.OWN
                                                     and rates[u]["rate_per_100"] is not None]))},
          "hb": hb, "rates": rates}
    sc["P6"]["pass"] = bool(own and shw and sc["P6"]["own_med_absAcyc"] < sc["P6"]["shared_med_absAcyc"]
                            and sc["P6"]["own_med_rate"] < sc["P6"]["shared_med_rate"])
    sc["kill"] = {"met": (not sc["P1"]["pass"]) or (len(p2) == 0)}
    nat = {}
    for k in ("G35|work", "G35|attention"):
        r = res.get(k, {})
        if r.get("n_hops", 0) >= 3:
            nat.setdefault("N1", {})[k] = {"A3": r["A3"], "Acyc": r["Acyc"], "m2": r["m2"], "p_flip": r["p_flip"],
                                           "p_db_C2": r.get("p_db_C2"), "testable_tri": r["testable_tri"],
                                           "testable_curl": r["testable_curl"],
                                           "pass": bool(all(v >= 0.05 for v in r["p_flip"].values())
                                                        and (r.get("p_db_C2") is None or r["p_db_C2"] >= 0.05 or not r["testable_curl"]))}
    for k in ("G38|work", "G38|attention"):
        r = res.get(k, {})
        if r.get("p_flip"):
            nat.setdefault("N2", {})[k] = {"m2": r["m2"], "p_flip_m2": r["p_flip"]["m2"], "Acyc": r["Acyc"],
                                           "p_ref_Acyc": r.get("p_ref", {}).get("Acyc"),
                                           "pass": bool(r["m2"] > 0 and r["p_flip"]["m2"] < 0.05
                                                        and r.get("p_ref", {}).get("Acyc", 0) >= 0.05)}
    for ch in ("work", "attention"):
        b, rr = res.get(f"G44best|{ch}"), res.get(f"G44rest|{ch}")
        if b and rr:
            nat.setdefault("N3", {})[ch] = {"kappa_best": b["kappa_c"], "kappa_rest": rr["kappa_c"], "m2_best": b["m2"],
                                            "m2_rest": rr["m2"], "pass": bool((b["kappa_c"] or 0) < (rr["kappa_c"] or 0))}
    sc["natives"] = nat
    return sc


def write_rows(res, rates):
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import estimates as E
    rows = []
    for k, r in res.items():
        if "boot" not in r:
            continue
        g, ch, u = r["goal_no"], r["channel"], r["unit"]
        native = u.startswith("G44b") or u.startswith("G44r")
        role = "native" if native or (g in (35, 38) and False) else "replication"
        unit = u if (g == 51 and not u.startswith("G")) else (E.map_unit(g) or f"G{g:02d}")
        base = dict(period_unit=unit, goal_no=g, channel=f"{ch}_hops", role=role, unit_local=u if native else None,
                    n=r["n_hops"], n_kind="hops", source="data/processed/H129-project-cycle-currents/results/units.json",
                    post_hoc=False, notes=f"verdict={r.get('verdict')}; shared={r.get('shared')}")
        for stat, key, null in (("h129_age_triple_affinity_A3", "A3", "per-agent reversal null"),
                                ("h129_triple_cycle_affinity_Acyc", "Acyc", "reversal null; age walker W1* calibrated to m2 and return share"),
                                ("h129_net_age_flux_m2", "m2", "per-agent reversal null")):
            lo, hi, se = r["boot"][key]
            rows.append({**base, "statistic": stat, "estimate": r[key], "ci_lo": lo, "ci_hi": hi, "se": se,
                         "ci_kind": "percentile", "method": "agent bootstrap (1000) of consecutive distinct-project triples/hops; age = first non-holdout appearance",
                         "null": null})
        if r.get("kappa_c") is not None and np.isfinite(r["kappa_c"]):
            rows.append({**base, "statistic": "h129_hodge_cycle_share", "estimate": r["kappa_c"], "ci_lo": None, "ci_hi": None,
                         "ci_kind": "none", "method": "C2/||F||^2: net hop flow not explained by a potential (least squares Hodge split)",
                         "null": f"detailed-balance binomial null p={r.get('p_db_C2')}"})
        dwl = r.get("dwell") or {}
        if dwl.get("testable"):
            rows.append({**base, "statistic": "h129_dwell_hazard_slope", "estimate": dwl["gamma"], "ci_lo": dwl["gamma_ci"][0],
                         "ci_hi": dwl["gamma_ci"][1], "se": dwl["gamma_se"], "ci_kind": "se_z", "n": dwl["n"], "n_kind": "visits",
                         "method": "Poisson piecewise hazard, log rate = a + gamma ln(dwell); dwell in own calls (work) or windows (attention)",
                         "null": "gamma = 0 (geometric dwell)"})
    E.write_estimates([x for x in rows if x["estimate"] is not None and np.isfinite(x["estimate"])], hypothesis="H129")
    print(f"wrote {len(rows)} estimates rows")


if __name__ == "__main__":
    main()
