"""H43 cross-period synthesis: per-period replication rows, a random-effects pooled mention R, native results, and the
outcome-vs-prediction scoring inputs. Writes data/processed/H43-kick-refractory-window/summary.json.
Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/summarize.py
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h43lib as L  # noqa: E402


def se_from(d):
    if not d or d.get("lo") is None or d.get("hi") is None:
        return None
    return (d["hi"] - d["lo"]) / 3.92


def dl_pool(est, se):
    """DerSimonian-Laird random-effects mean, CI, tau^2, I^2."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) < 2:
        return None
    w = 1 / se ** 2
    m = np.sum(w * est) / w.sum()
    Q = np.sum(w * (est - m) ** 2)
    k = len(est)
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - np.sum(w ** 2) / w.sum()))
    wr = 1 / (se ** 2 + tau2)
    mr = np.sum(wr * est) / wr.sum()
    ser = np.sqrt(1 / wr.sum())
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0
    return {"k": k, "mean": float(mr), "lo": float(mr - 1.96 * ser), "hi": float(mr + 1.96 * ser), "tau2": float(tau2),
            "I2": float(I2), "fixed_mean": float(m)}


def main():
    rows = []
    for p in sorted(glob.glob(str(L.OUT / "G*" / "results.json"))):
        r = json.loads(Path(p).read_text())
        row = {"period": r["period"], "verdict": r["verdict_templated"], "n_days": r["n_days"], "regime": r["regime"],
               "tests": {cl: {k: v for k, v in t.items() if k in ("testable", "why", "pass", "rising", "delta_half",
                                                                    "window_tracks_episode", "n_primers", "n_second",
                                                                    "E1", "E1_lo", "E1_hi", "L_median")}
                         for cl, t in r["tests"].items()}}
        for cl in L.CLASSES:
            c = r["classes"][cl]
            for o in ("O1", "O1a", "O2", "O2c"):
                od = c.get("outcomes", {}).get(o, {})
                if "E1" not in od:
                    continue
                row[f"{cl}_{o}"] = {"E1": od["E1"], "E1_positive": od["E1_positive"],
                                   "R_pool": {k: {"R": v["R"], "n": v["n"]} for k, v in od.get("R_pool", {}).items()},
                                   "in": od.get("by_status", {}).get("in", {}).get("R"),
                                   "act": od.get("by_status", {}).get("act", {}).get("R"),
                                   "batched": (od.get("batched") or {}).get("R"),
                                   "delta_half": (od.get("fit") or {}).get("delta_half"),
                                   "L_median": c.get("L_median")}
        rows.append(row)
    meta = {}
    for key in ("A_O2", "A_O2c"):
        for rng in ("0-15", "15-60", "60-240"):
            est, se, per = [], [], []
            for row in rows:
                d = row.get(key)
                if not d or not d["E1_positive"] or d["E1"]["n"] < 20:
                    continue
                v = d["R_pool"].get(rng)
                if not v or v["n"] < 20:
                    continue
                s = se_from(v["R"])
                if s is None or not np.isfinite(v["R"]["est"]):
                    continue
                est.append(v["R"]["est"])
                se.append(s)
                per.append(row["period"])
            meta[f"{key}_{rng}"] = {"periods": per, "estimates": est, "se": se, "pooled": dl_pool(est, se),
                                    "median": float(np.median(est)) if est else None}
    testable = [(row["period"], cl) for row in rows for cl, t in row["tests"].items() if t.get("testable")]
    passed = [(row["period"], cl) for row in rows for cl, t in row["tests"].items() if t.get("pass")]
    verdicts = {}
    for row in rows:
        verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
    native = {t: json.loads((L.OUT / "native" / f"{t}.json").read_text()) for t in ("NE43", "G38", "G04")
              if (L.OUT / "native" / f"{t}.json").exists()}
    out = {"rows": rows, "meta": meta, "n_periods": len(rows), "replication_verdicts": verdicts,
           "testable_cells": testable, "passed_cells": passed,
           "native_keys": list(native), "rule": json.loads((L.OUT / "rule.json").read_text()) if (L.OUT / "rule.json").exists() else None}
    L.jdump(out, L.OUT / "summary.json")
    print("periods", len(rows), "verdicts", verdicts, "testable", len(testable), "passed", len(passed))
    for k, v in meta.items():
        print(k, "k", v["pooled"] and v["pooled"]["k"], "pooled", v["pooled"] and {kk: round(vv, 3) for kk, vv in v["pooled"].items()},
              "median", v["median"] and round(v["median"], 2), v["periods"])


if __name__ == "__main__":
    main()
