"""H87 round 1 on real data (exploratory; holdout masked upstream).

  N1 NE41: the pooled call-scale table (rows A, M, G, Q, C; own-scramble variants H dose, G any, M size; V40), paired
     bootstrap 300 over agent-days, agent x period strata; return probabilities by open flag.
  N3 NE34: the kickoff row at day scale (new-goal nights vs within-goal nights).
  N2 G37: the search row's own scramble from H84's outage results (data reuse).
  Replication: the call-scale table per regime-III period (B = 200).
Ordering claims follow Amendment A1: only between identified rows (I CI lower bound > MIN_I).
Output: data/processed/H87-kappa-channel-table/results/results.json
Usage: uv run python hypotheses/H87-kappa-channel-table/analysis/run.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h87lib as L  # noqa: E402

ROWS = ("A", "M", "G", "Q")
MIN_F = 300


def identified(r: dict) -> bool:
    return r["I_ci"][0] is not None and r["I_ci"][0] > L.MIN_I


def return_probs(ev: pl.DataFrame) -> dict:
    e = ev.filter(pl.col("etype").is_in(["F", "P"]) & (pl.col("X_next") >= 0))
    out = {}
    for et in ("F", "P"):
        d = e.filter(pl.col("etype") == et)
        out[et] = {"all": float((d["X_next"] == d["A_prev"]).mean()), "n": d.height}
        for o in ("openA", "openM", "openG", "openQ"):
            for v in (True, False):
                dd = d.filter(pl.col(o) == v)
                out[et][f"{o}={v}"] = {"p": float((dd["X_next"] == dd["A_prev"]).mean()) if dd.height else None,
                                       "n": dd.height}
    return out


def strip(t: dict) -> dict:
    t = dict(t)
    t.pop("kappa_draws", None)
    return t


def period_verdict(t: dict) -> str:
    if t["n_scramble"] < MIN_F:
        return "descriptive"
    c = t["rows"]["C"]
    lo = c["kappa_ci"][0]
    if lo is None or not np.isfinite(c["kappa"]) or lo <= 0:
        return "failed"
    others = [t["rows"][k]["kappa"] for k in ROWS if identified(t["rows"][k]) and np.isfinite(t["rows"][k]["kappa"])]
    return "supported" if all(c["kappa"] > k for k in others) else "mixed"


def main():
    t0 = time.time()
    ev = L.load()
    f = L.call_frame(ev)
    res = {}
    tab = L.paired_table(f, B=300, n_perm=200, n_perm_boot=10, seed=41, rows=ROWS, variants=True)
    tab["identified"] = {c: identified(tab["rows"][c]) for c in list(ROWS) + ["C"]}
    ids = [c for c, v in tab["identified"].items() if v]
    tab["identified_pairs"] = {k: v for k, v in tab["paired"].items()
                               if k.split(">")[0] in ids and k.split(">")[1] in ids}
    res["NE41"] = tab
    res["NE41"]["return"] = return_probs(ev)
    print("NE41 done", f"{time.time() - t0:.0f}s", {c: (round(r["I"], 3), round(r["dV"], 3), round(r["kappa"], 2))
                                                     for c, r in tab["rows"].items()}, flush=True)
    res["NE34_K"] = L.kickoff_row(ev, B=300, seed=34)
    print("K", {k: res["NE34_K"][k] for k in ("I", "dV", "kappa", "kappa_ci")}, flush=True)
    h84 = json.loads((L.H84D / "results/results.json").read_text())
    ki = h84["kappa_inputs"]
    dV, se = ki["dV_Q_commits_per20_at_dbar"], ki["dV_Q_se_placebo"]
    I = ki["I_Q_pooled"]
    res["G37_Q"] = {"dV": dV, "dV_ci": [dV - 1.96 * se, dV + 1.96 * se], "I": I["est"], "I_ci": [I["lo"], I["hi"]],
                    "kappa": dV / I["est"] if I["est"] > L.MIN_I else float("nan"),
                    "identified": bool(I["lo"] > L.MIN_I),
                    "note": "dV from H84 G37 (beta_V4 x mean searcher dose, placebo-SD interval); I from H84's pooled "
                            "replication I_Q (DL over 7 periods)"}
    rep = {}
    for p in sorted(set(f["period"])):
        m = f["period"] == p
        sub = {k: (v[m] if isinstance(v, np.ndarray) and len(v) == len(m) else v) for k, v in f.items()}
        if sub["scramble"].sum() < MIN_F:
            continue
        t = L.paired_table(sub, B=200, n_perm=200, n_perm_boot=10, seed=int(p[1:]), rows=ROWS, variants=False)
        t["identified"] = {c: identified(t["rows"][c]) for c in list(ROWS) + ["C"]}
        t["verdict"] = period_verdict(t)
        t["agents"] = int(len(set(s.split("|")[0] for s in sub["stratum"])))
        t["days"] = sorted(set(s.split("|")[1] for s in sub["cluster"]))
        rep[p] = strip(t)
        print("rep", p, t["verdict"], {c: (round(r["I"], 3), round(r["dV"], 3), round(r["kappa"], 2))
                                        for c, r in t["rows"].items()}, f"{time.time() - t0:.0f}s", flush=True)
    res["replication"] = rep
    res["replication_summary"] = {
        "n_periods": len(rep),
        "kappa_C_positive": int(sum(1 for t in rep.values() if t["rows"]["C"]["kappa_ci"][0] is not None
                                    and t["rows"]["C"]["kappa_ci"][0] > 0)),
        "supported": int(sum(t["verdict"] == "supported" for t in rep.values()))}
    out = L.DATA / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(res, indent=1, default=float))
    print("written", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
