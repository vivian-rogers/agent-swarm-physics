"""H58 round-2 summaries: synthetic rates (R1, R2) and the real-data tables (R1, R2, R3) as compact JSON.
Run: uv run python hypotheses/H58-coordinated-superagents/analysis/r2_summarize.py [--synth] [--real]
Writes r2/synthetic_summary.json and r2/real_summary.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib58 as R  # noqa: E402


def rate(rows, key):
    v = [bool(r.get(key)) for r in rows]
    return float(np.mean(v)) if v else None


def synth():
    out = {}
    f1 = R.R2 / "synthetic_r1.json"
    if f1.exists():
        res = json.loads(f1.read_text())
        main = [r for r in res if r["rep"] < 500]
        g = [r for r in res if r["rep"] >= 500]
        worlds = sorted({(r["world"], r["par"]) for r in main})
        tab = {}
        for w, p in worlds:
            rows = [r for r in main if r["world"] == w and r["par"] == p]
            key = f"{w}_{p}"
            tab[key] = {"all": {"A": rate(rows, "a_qual"), "T": rate(rows, "t_qual"),
                                "village_herd": float(np.mean([(r["v_z_lam"] or 0) >= 2 and (r["v_z_T"] or 0) <= -2
                                                               for r in rows])),
                                "village_terr": float(np.mean([(r["v_z_T"] or 0) >= 2 for r in rows])),
                                "A_testable": rate(rows, "a_testable"),
                                "T_ref_ok": float(np.mean([(r["t_n_part"] or 0) >= 30 for r in rows]))},
                        "per_unit": {}}
            for u in R.REPL + R.NATIVE:
                ru = [r for r in rows if r["unit"] == u]
                if ru:
                    tab[key]["per_unit"][u] = {"A": rate(ru, "a_qual"), "T": rate(ru, "t_qual"),
                                               "herd": float(np.mean([(r["v_z_lam"] or 0) >= 2 for r in ru])),
                                               "T_ref_ok": float(np.mean([(r["t_n_part"] or 0) >= 30 for r in ru]))}
        out["r1"] = tab
        out["r1_g_rule_terr09"] = {"g_rule_rate": rate(g, "g_qualifies"), "A_rate": rate(g, "a_qual"),
                                   "g_pos_zshift2": float(np.mean([(r.get("g") or 0) > 0 and (r.get("g_z_shift") or 0) >= 2
                                                                    for r in g])),
                                   "n": len(g),
                                   "per_unit": {u: rate([r for r in g if r["unit"] == u], "g_qualifies")
                                                for u in R.REPL + R.NATIVE}}
    f2 = R.R2 / "synthetic_r2.json"
    if f2.exists():
        res = json.loads(f2.read_text())
        tab = {}
        for w in sorted({r["world"] for r in res}):
            rows = [r for r in res if r["world"] == w]
            reps = sorted({r["rep"] for r in rows})
            # pooled Stouffer per replicate (weights sqrt n_ctx)
            pooled = []
            for rp in reps:
                rr = [r for r in rows if r["rep"] == rp and r["z_lam"] is not None and r["n_ctx"]]
                if rr:
                    w_ = np.sqrt([r["n_ctx"] for r in rr])
                    pooled.append(float((w_ * np.array([r["z_lam"] for r in rr])).sum() / np.sqrt((w_ ** 2).sum())))
            tab[w] = {"per_repo_lam_z2": float(np.mean([(r["z_lam"] or 0) >= 2 and (r["lam_ratio"] or 0) > 1 for r in rows])),
                      "per_repo_T_z2": float(np.mean([(r["z_T"] or 0) >= 2 for r in rows])),
                      "per_repo_excl_z2": float(np.mean([(r["z_excl"] or 0) >= 2 for r in rows])),
                      "pooled_z2": float(np.mean(np.array(pooled) >= 2)) if pooled else None,
                      "n_repos": len({r["repo"] for r in rows}), "n_reps": len(reps)}
            tab[w]["per_repo"] = {}
            for k in sorted({r["repo"] for r in rows}):
                rr = [r for r in rows if r["repo"] == k]
                tab[w]["per_repo"][k] = {"lam": float(np.mean([(r["z_lam"] or 0) >= 2 and (r["lam_ratio"] or 0) > 1 for r in rr])),
                                         "T": float(np.mean([(r["z_T"] or 0) >= 2 for r in rr]))}
        out["r2"] = tab
    (R.R2 / "synthetic_summary.json").write_text(json.dumps(R.jsonable(out), indent=1))
    return out


if __name__ == "__main__":
    if "--synth" in sys.argv:
        o = synth()
        for k, v in o.get("r1", {}).items():
            print(k, v["all"], {u: (x["A"], x["T"]) for u, x in v["per_unit"].items()})
        print(o.get("r1_g_rule_terr09"))
        for k, v in o.get("r2", {}).items():
            print(k, {a: b for a, b in v.items() if a != "per_repo"})
