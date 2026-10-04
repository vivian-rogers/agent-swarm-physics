"""H33 synthetic validation (axis F): planted inverted U vs monotone (incl. saturating) curves at the real sample.

Design = the real eligible agent-days (x = PR10 as observed, agent x unit and day FE, the two activity controls,
clusters, units). Synthetic outcome = g(x_true) + noise, where noise = the real outcome's residual after FE and
controls (NO x), permuted within unit (destroys any x-y relation, keeps per-unit noise scale and the zero-heavy shape).
Two conditions:
  exact : x_true = observed PR10 (no measurement error)
  eiv   : x_true = latent PR10 with within-FE reliability rel (from reliability.json): the analysis sees the real PR10,
          the signal sits on x_true = FE part + rel*w + sqrt(rel(1-rel))*sd(w)*xi  (w = within-FE PR10)
Shapes (x quantiles q10, q50, q75, q90 of observed PR10; e in residual-SD units):
  null; linear (rises e from q10 to q90); log (concave, rises e from q10 to q90); plateau (rises e from q10 to q50, flat
  above: the saturating rival); invU_mid (peak q50, drop e at q10 and q90); invU_q75 (peak q75, drop e at q10).
  x is clipped to its 2nd-98th percentile inside every shape.
Reports, per condition: rates of the quadratic test, the two-lines test, the interior-max check, the full P1 rule, the
R1 pattern, peak recovery, and (eiv) per-period P2 rates. Writes synthetic.json + figures/synthetic_validation.pdf.

Usage: uv run python hypotheses/H33-diversity-productivity/analysis/synthetic.py [--reps 200]
"""
from __future__ import annotations

import argparse
import json
import time

import h33lib as H  # noqa: I001
import h33common as C
import numpy as np


def shapes(q, lo, hi):
    """Bounded shapes: x is clipped to its 2nd-98th percentile [lo, hi] inside g, so tails cannot dominate."""
    q10, q50, q75, q90 = q
    s = q90 - q10
    c = lambda x: np.clip(x, lo, hi)  # noqa: E731

    def null(x):
        return np.zeros_like(x)

    def linear(x):
        return (c(x) - q10) / s

    def plateau(x):  # rises e from q10 to q50, flat above (the "saturating" rival)
        return (np.minimum(c(x), q50) - q10) / (q50 - q10)

    def log_(x):  # concave everywhere
        return (np.log(c(x)) - np.log(q10)) / (np.log(q90) - np.log(q10))

    def invU_mid(x):
        x = c(x)
        return np.where(x < q50, -((x - q50) / (q50 - q10)) ** 2, -((x - q50) / (q90 - q50)) ** 2)

    def invU_q75(x):
        return -((c(x) - q75) / (q75 - q10)) ** 2
    return {"null": (null, None), "linear": (linear, None), "plateau": (plateau, None), "log": (log_, None),
            "invU_mid": (invU_mid, q50), "invU_q75": (invU_q75, q75)}


def main(reps: int):
    t0 = time.time()
    ad, x, y, Z, au, day = H.load_pooled()
    rel = json.loads((C.OUT / "reliability.json").read_text())["pr"]["within_fe_reliability_SB"]
    groups = [au, day]
    D = H.Design(groups, au, Z)
    units = ad["unit"].to_numpy()
    # noise: residual of y on FE + controls, no x
    y_dm = D.dm(y)
    b, V, e_res, G = D.fit(y_dm, np.zeros((len(y), 0)))
    sig = float(e_res.std())
    q = np.quantile(x, [0.10, 0.50, 0.75, 0.90])
    w = D.dm(x)
    sw = float(w.std())
    # per-period designs (agent FE + day FE within unit; cluster agent)
    per = {}
    for u in np.unique(units):
        m = units == u
        per[u] = (m, H.Design([H.codes(ad["agent"].to_numpy()[m]), H.codes(ad["pt_date"].to_numpy()[m])],
                              ad["agent"].to_numpy()[m], Z[m]))
    S = shapes(q, *np.quantile(x, [0.02, 0.98]))
    effects = [0.2, 0.4, 0.8]
    conds = [("null", 0.0)] + [(s, e) for s in S if s != "null" for e in effects]
    out = {"n": int(len(x)), "units": int(len(per)), "noise_sd": sig, "rel_within": rel, "x_q10_50_75_90": q.tolist(),
           "reps": reps, "conditions": []}
    rng = np.random.default_rng(C.SEED)
    for cond in ("exact", "eiv"):
        for shape, e in conds:
            g, peak = S[shape]
            rec = {"cond": cond, "shape": shape, "effect_sd": e, "quad_U": 0, "two_lines_U": 0, "interior": 0, "P1": 0,
                   "R1": 0, "lin_sig_pos": 0, "xc": [], "xmax": [], "P2": 0, "per_pattern_frac": []}
            for r in range(reps):
                if cond == "exact":
                    xt = x
                else:
                    xt = x - w + rel * w + np.sqrt(rel * (1 - rel)) * sw * rng.standard_normal(len(x))
                noise = np.empty_like(e_res)
                for u, (m, _) in per.items():
                    idx = np.flatnonzero(m)
                    noise[idx] = e_res[rng.permutation(idx)]
                ys = e * sig * g(xt) + noise
                ys_dm = D.dm(ys)
                qt = H.quad_test(D, ys_dm, x)
                tl, sp = H.two_lines(D, ys_dm, x)
                lin = D.fit(ys_dm, D.dm(x, key="lin"))
                lb, lse = lin[0][0], np.sqrt(lin[1][0, 0])
                rec["quad_U"] += H.quad_supported(qt, x)
                rec["two_lines_U"] += tl["u_supported"]
                rec["interior"] += tl["interior"]
                rec["P1"] += tl["u_supported"] and tl["interior"]
                rec["R1"] += (tl["b1"] > 0 and tl["p1"] < 0.05) and not (tl["b2"] < 0 and tl["p2"] < 0.05)
                rec["lin_sig_pos"] += lb / lse > 1.96
                rec["xc"].append(tl["xc"])
                rec["xmax"].append(tl["x_max"])
                if cond == "eiv" and (e in (0.0, 0.4, 0.8)):
                    b1s, s1s, b2s, s2s, pat = [], [], [], [], []
                    for u, (m, Du) in per.items():
                        xu = x[m]
                        if (xu < tl["xc"]).sum() < 5 or (xu >= tl["xc"]).sum() < 5:
                            continue
                        rr = H.interrupted(Du, Du.dm(ys[m]), xu, tl["xc"])
                        b1s.append(rr["b1"]); s1s.append(rr["se1"]); b2s.append(rr["b2"]); s2s.append(rr["se2"])
                        pat.append(rr["b1"] > 0 and rr["b2"] < 0)
                    m1 = H.dersimonian_laird(b1s, s1s)
                    m2 = H.dersimonian_laird(b2s, s2s)
                    frac = float(np.mean(pat)) if pat else np.nan
                    rec["per_pattern_frac"].append(frac)
                    rec["P2"] += bool(m1["est"] > 0 and m2["est"] < 0 and frac >= 0.5)
            for k in ("quad_U", "two_lines_U", "interior", "P1", "R1", "lin_sig_pos", "P2"):
                rec[k] = rec[k] / reps
            rec["xc_med"], rec["xc_iqr"] = float(np.median(rec["xc"])), np.quantile(rec["xc"], [0.25, 0.75]).tolist()
            rec["xmax_med"], rec["xmax_iqr"] = float(np.median(rec["xmax"])), np.quantile(rec["xmax"], [0.25, 0.75]).tolist()
            rec["true_peak"] = None if peak is None else float(peak)
            rec["per_pattern_frac_med"] = float(np.nanmedian(rec["per_pattern_frac"])) if rec["per_pattern_frac"] else None
            del rec["xc"], rec["xmax"], rec["per_pattern_frac"]
            if not (cond == "eiv" and e in (0.0, 0.4, 0.8)):
                rec["P2"] = None
            out["conditions"].append(rec)
            print(f"[{time.time() - t0:5.0f}s] {cond:5s} {shape:10s} e={e:.1f} quadU={rec['quad_U']:.2f} "
                  f"2linesU={rec['two_lines_U']:.2f} P1={rec['P1']:.2f} R1={rec['R1']:.2f} xc={rec['xc_med']:.1f} "
                  f"xmax={rec['xmax_med']:.1f} P2={rec['P2']}", flush=True)
    (C.OUT / "synthetic.json").write_text(json.dumps(out, indent=1))
    C.write_provenance("hypotheses/H33-diversity-productivity/analysis/synthetic.py", ["H33 agent_day (x, design, residual noise)"],
                       {"reps": reps, "effects_sd": effects, "rel_within": rel, "seed": C.SEED})
    figure(out)


def figure(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cs = out["conditions"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    shapes_ = ["null", "linear", "log", "plateau", "invU_mid", "invU_q75"]
    for ax, cond in zip(axes, ["exact", "eiv"]):
        for i, (key, lab, col) in enumerate([("quad_U", "quadratic test", "#b07aa1"), ("P1", "two-lines + interior (P1)", "#4e79a7")]):
            xs, ys = [], []
            for j, s in enumerate(shapes_):
                for k, e in enumerate([0.0] if s == "null" else [0.2, 0.4, 0.8]):
                    r = next(c for c in cs if c["cond"] == cond and c["shape"] == s and c["effect_sd"] == e)
                    xs.append(j + (k - 1) * 0.22 + (0 if s != "null" else 0.22)); ys.append(r[key])
            ax.scatter(np.array(xs) + (i - 0.5) * 0.08, ys, s=14, color=col, label=lab, zorder=3)
        ax.axhline(0.05, color="0.5", lw=0.8, ls="--")
        ax.set_xticks(range(len(shapes_)))
        ax.set_xticklabels(["null", "linear", "log", "plateau", "inv-U\n(mid)", "inv-U\n(q75)"], fontsize=8)
        ax.set_title({"exact": "PR10 measured exactly", "eiv": f"PR10 reliability {out['rel_within']:.2f} (as measured)"}[cond], fontsize=9)
        ax.set_ylim(-0.02, 1.02)
        ax.grid(axis="y", color="0.9")
    axes[0].set_ylabel("rate of 'inverted U' verdict", fontsize=9)
    axes[0].legend(fontsize=7, frameon=False, loc="upper left")
    fig.text(0.5, -0.02, "effects 0.2 / 0.4 / 0.8 residual SD left to right within each shape; n = %d agent-days, %d units, %d reps"
             % (out["n"], out["units"], out["reps"]), ha="center", fontsize=7.5)
    fig.tight_layout()
    fig.savefig(C.FIG / "synthetic_validation.pdf", bbox_inches="tight")
    print("figure written")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    main(ap.parse_args().reps)
