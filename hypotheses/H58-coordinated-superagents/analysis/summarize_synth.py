"""Summarize the H58 synthetic validation (card S0): power and size of the decision rule, H01's binary-state statistics
on the same worlds, the Krakauer criteria, the night gain, and search recovery. Reads results/synthetic.json and writes
results/synthetic_summary.json. Run after analysis/synthetic.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h58data as HD  # noqa: E402

OUT = HD.D / "results"


def rate(vals):
    v = [x for x in vals if x is not None and not (isinstance(x, float) and np.isnan(x))]
    return (float(np.mean(v)), len(v)) if v else (None, 0)


def main():
    tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else ""
    R = json.loads((OUT / f"synthetic{tag}.json").read_text())
    meta = {x["unit"]: x for x in HD.units_meta()}
    rows = [r for r in R if r["rep"] < 1000]
    srch = [r for r in R if r["rep"] >= 1000]
    out = {"per_setting": {}, "per_unit": {}, "search": {}}
    settings = sorted({(r["world"], r["rho"]) for r in rows})
    big = lambda r: r["nB"] >= 40  # noqa: E731
    for (w, rho) in settings:
        sub = [r for r in rows if r["world"] == w and r["rho"] == rho]
        sb = [r for r in sub if big(r)]
        z2 = lambda key, rr: [bool(x[key] is not None and np.isfinite(x[key]) and x[key] >= 2) if x.get(key) is not None else None for x in rr]  # noqa: E731
        out["per_setting"][f"{w}_{rho}"] = {
            "qualifies_all": rate([r["qualifies"] for r in sub]),
            "qualifies_ge40bins": rate([r["qualifies"] for r in sb]),
            "z_bin_ge2": rate(z2("z_bin", sub)),
            "z_alloc_bin_ge2": rate(z2("z_alloc_bin", sub)),
            "iota_shift_z_ge2": rate(z2("z_iota_shift", sub)),
            "iota_unit_ge_members": rate([bool(r["iota_unit"] >= r["iota_members"]) if (r.get("iota_unit") is not None and r.get("iota_members") is not None and np.isfinite(r["iota_unit"]) and np.isfinite(r["iota_members"])) else None for r in sub]),
            "night_comp_z_ge2": rate(z2("z_night_comp", sub)),
            "median_g": float(np.nanmedian([r["g"] if r["g"] is not None else np.nan for r in sub])),
            "median_spec": float(np.nanmedian([r.get("specificity") if r.get("specificity") is not None else np.nan for r in sub])),
        }
    for u in sorted({r["unit"] for r in rows}, key=lambda x: (len(x), x)):
        out["per_unit"][u] = {"nB": next(r["nB"] for r in rows if r["unit"] == u),
                              "nA": next(r["nA"] for r in rows if r["unit"] == u),
                              "n_days": meta[u]["n_days"]}
        for (w, rho) in settings:
            sub = [r for r in rows if r["unit"] == u and r["world"] == w and r["rho"] == rho]
            out["per_unit"][u][f"{w}_{rho}"] = rate([r["qualifies"] for r in sub])[0]
            out["per_unit"][u][f"{w}_{rho}_zbin"] = rate([bool(r.get("z_bin") is not None and r["z_bin"] >= 2) for r in sub])[0]
    for (w, rho) in sorted({(r["world"], r["rho"]) for r in srch}):
        sub = [r for r in srch if r["world"] == w and r["rho"] == rho]
        out["search"][f"{w}_{rho}"] = {
            "n": len(sub),
            "jaccard_ge05": rate([bool(r.get("search_jaccard") is not None and r["search_jaccard"] >= 0.5) if w == "store" else None for r in sub]),
            "median_jaccard": float(np.nanmedian([r.get("search_jaccard") if r.get("search_jaccard") is not None else np.nan for r in sub])) if w == "store" else None,
            "beats_surrogates": rate([r.get("search_beats_surr") for r in sub]),
            "final_qualifies": rate([r.get("search_final_qualifies") for r in sub]),
            "search_qualifies": rate([r.get("search_qualifies") for r in sub]),
            "median_size": float(np.median([len(r["search_members"]) for r in sub if r.get("search_members")])),
            "median_secs": float(np.median([r.get("search_s", np.nan) for r in sub])),
        }
    (OUT / f"synthetic_summary{tag}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["per_setting"], indent=1))
    print(json.dumps(out["search"], indent=1))
    for u, v in out["per_unit"].items():
        print(u, v["nB"], v["nA"], " ".join(f"{k}={v[k]:.2f}" for k in v if k.startswith("store_0.5") or k.startswith("own") or k.startswith("env") if v[k] is not None and not k.endswith("zbin")))


if __name__ == "__main__":
    main()
