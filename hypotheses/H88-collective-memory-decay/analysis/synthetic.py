"""H88 synthetic validation at real offsets and observation masks (axis F). Runs before any real-data fit.

For every period that passes the design-only eligibility (item counts, observed days), the real veteran and newcomer
offsets O_{g,k} and the real masks are kept; counts are drawn as y ~ NegBin(mean O f(k), shape r) (r = inf: Poisson).
Truths: S0 single exponential; S1 biexponential (strong / weak slow part); S2 exponential + floor; S3 power law.
Reported: model-selection rates (best by QAIC; "biexp" = M2 best and beats M1 by >= 2), tau recovery, and the size and
power of the pooled newcomer slope b.

  uv run python hypotheses/H88-collective-memory-decay/analysis/synthetic.py [--reps 30]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h88lib as H  # noqa: E402

OUTD = H.DATA / "synthetic"
TRUTH = {
    "S0_single": ("M1", {"A": 0.3, "tau": 4.0}),
    "S1_biexp": ("M2", {"A1": 0.3, "tau1": 2.0, "A2": 0.02, "tau2": 40.0}),
    "S1w_biexp_weak": ("M2", {"A1": 0.3, "tau1": 2.0, "A2": 0.005, "tau2": 40.0}),
    "S2_floor": ("M1c", {"A": 0.3, "tau": 3.0, "c": 0.005}),
    "S3_power": ("MP", {"A": 0.3, "alpha": 1.0}),
}


def ftrue(model, p, k):
    if model == "M1":
        return p["A"] * np.exp(-k / p["tau"])
    if model == "M2":
        return p["A1"] * np.exp(-k / p["tau1"]) + p["A2"] * np.exp(-k / p["tau2"])
    if model == "M1c":
        return p["A"] * np.exp(-k / p["tau"]) + p["c"]
    return p["A"] * k ** (-p["alpha"])


def draw(rng, mu, r):
    if r is None:
        return rng.poisson(mu).astype(float)
    lam = rng.gamma(r, mu / r)
    return rng.poisson(lam).astype(float)


def eligible(daily, items, kind):
    """Design-only eligibility (no outcome): item count, observed days."""
    n_items = items.group_by("P", "kind").len()
    out = []
    for P in sorted(daily["P"].unique().to_list()):
        ni = n_items.filter((pl.col("P") == P) & (pl.col("kind") == kind))
        ni = int(ni["len"][0]) if ni.height else 0
        if ni < (10 if kind == "art" else 30):
            continue
        s = daily.filter((pl.col("P") == P) & (pl.col("kind") == kind) & (pl.col("group") == "vet") & pl.col("observed"))
        if s.filter(pl.col("k") <= 5).height >= 3 and s.height >= 30:
            out.append(P)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--only_b", action="store_true")
    args = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    daily = H.load_daily(); items = pl.read_parquet(H.DATA / "items.parquet")
    prev = json.loads((OUTD / "synthetic.json").read_text()) if (args.only_b and (OUTD / "synthetic.json").exists()) else {}
    out = {"reps": args.reps, "truth": {k: [m, p] for k, (m, p) in TRUTH.items()}, "selection": {}, "newcomer_b": {}}
    if prev:
        out["selection"] = prev.get("selection", {})
    rng = np.random.default_rng(88)
    for kind in ("art", "term"):
        Ps = eligible(daily, items, kind)
        out[f"eligible_{kind}"] = Ps
        for name, (model, p) in ([] if args.only_b else TRUTH.items()):
            for r in (None, 2.0):
                calls = {m: 0 for m in H.MODELS}; bi = 0; n = 0; t1s = []; t2s = []
                for rep in range(args.reps):
                    P = Ps[rep % len(Ps)]
                    k, _, O = H.series(daily, P, kind, "vet")
                    y = draw(rng, O * ftrue(model, p, k), r)
                    res = H.fit_all(k, y, O)
                    calls[res["best"]] += 1; bi += res["biexp"]; n += 1
                    t1s.append(res["M2_params"]["tau1"]); t2s.append(res["M2_params"]["tau2"])
                key = f"{kind}/{name}/{'pois' if r is None else 'nb2'}"
                out["selection"][key] = {"best_rate": {m: c / n for m, c in calls.items()}, "biexp_rate": bi / n,
                                         "tau1_median": float(np.median(t1s)), "tau2_median": float(np.median(t2s))}
                print(key, json.dumps(out["selection"][key]), f"{time.time() - t0:.0f}s", flush=True)
                (OUTD / "synthetic.json").write_text(json.dumps(out, indent=1))
        # newcomer slope b: size (same f for both groups) and power (newcomers carry only the slow part)
        p = TRUTH["S1_biexp"][1]
        for scen in ("same_f", "slow_only"):
            bs = []; rej = 0
            for rep in range(args.reps):
                rows = []
                for P in Ps:
                    for grp in ("vet", "new"):
                        k, _, O = H.series(daily, P, kind, grp)
                        if len(k) == 0:
                            continue
                        f = ftrue("M2", p, k) if (grp == "vet" or scen == "same_f") else p["A2"] * np.exp(-k / p["tau2"]) * 3
                        y = draw(rng, O * np.minimum(f, 1), 2.0)
                        rows += [(P, grp, kk, yy, oo) for kk, yy, oo in zip(k, y, O)]
                df = pl.DataFrame(rows, schema=["P", "group", "k", "y", "O"], orient="row")
                if df.filter(pl.col("group") == "new").height < 20:
                    continue
                bb = H.ratio_bands_boot(df, B=200, seed=rep)
                if bb["b"] is None or bb["b_ci"] is None:
                    continue
                bs.append(bb["b"]); rej += bb["b_ci"][0] > 0
            out["newcomer_b"][f"{kind}/{scen}"] = {"b_mean": float(np.mean(bs)) if bs else None,
                                                   "reject_rate": rej / max(len(bs), 1), "n": len(bs)}
            print(kind, scen, out["newcomer_b"][f"{kind}/{scen}"], flush=True)
            (OUTD / "synthetic.json").write_text(json.dumps(out, indent=1))
    print("done", time.time() - t0)


if __name__ == "__main__":
    main()
