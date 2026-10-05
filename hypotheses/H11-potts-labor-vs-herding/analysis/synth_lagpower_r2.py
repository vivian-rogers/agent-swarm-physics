"""H11 round 2, amendment A2 (post hoc): power of the lag - lead test in planted past-driven attachment worlds.
Usage: cd hypotheses/H11-potts-labor-vs-herding/analysis && uv run python synth_lagpower_r2.py"""
import sys, json, numpy as np, polars as pl
sys.path.insert(0, '.')
import round2 as R
rng = np.random.default_rng(7)
out = {}
for ch, us in {"work": ["G31", "G38", "51f", "51g"], "att": ["G19", "G38", "51d"]}.items():
    c, j, sk = R.load(ch)
    for u in us:
        cu = c.filter(pl.col("unit") == u)
        a = cu["a"].to_numpy().astype(float); h = cu["h"].to_numpy().astype(float)
        loga = np.where(a > 0, np.log(np.maximum(a, 1)), 0); z0 = (a == 0).astype(float)
        res = {}
        for wn, uu in {"alpha1": 1.0 * loga - 1.0 * z0 + 1.5 * h, "alpha05": 0.5 * loga - 1.0 * z0 + 1.5 * h}.items():
            d, sig = [], []
            for _ in range(40):
                y = R.draw_choice(cu, uu, rng)
                w = R.fit_r1(cu, "lead", y)["lag_minus_lead"]
                d.append(w["est"]); sig.append((w["lo"] or -1) > 0)
            res[wn] = {"lag_minus_lead_mean": float(np.mean(d)), "power_lag_gt_lead": float(np.mean(sig))}
        out[f"{ch}:{u}"] = res
        print(ch, u, res, flush=True)
json.dump(out, open(R.RES / "synthetic_r2_A2_lagpower.json", "w"), indent=1)
