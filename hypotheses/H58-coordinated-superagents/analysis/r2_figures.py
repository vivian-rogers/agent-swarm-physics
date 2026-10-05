"""H58 round-2 figures: synthetic power (R1 A-rule, T-rule), village herding vs exclusion per unit (R1), file-level
statistics per shared repo (R2), and the pair's stored information and read/unread contrast (R3).
Output: hypotheses/H58-coordinated-superagents/figures/r2_summary.pdf
Run: uv run python hypotheses/H58-coordinated-superagents/analysis/r2_figures.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib58 as R  # noqa: E402

FIG = HERE.parent / "figures"
RED, GRAY, GREEN, BLUE = "#b2182b", "#7f7f7f", "#1a9850", "#2166ac"


def main():
    syn = json.loads((R.R2 / "synthetic_summary.json").read_text())
    r1 = json.loads((R.R2 / "r1_results.json").read_text())
    r2 = json.loads((R.R2 / "r2_results.json").read_text())
    r3 = json.loads((R.R2 / "r3_results.json").read_text())
    fig, ax = plt.subplots(2, 2, figsize=(10, 7.5))
    # (a) synthetic power per unit
    a = ax[0, 0]
    units = R.REPL + R.NATIVE
    x = np.arange(len(units))
    for j, (key, lab, col, mk) in enumerate([("store_0.5", "A-rule, store ρ 0.5", BLUE, "o"),
                                             ("store_0.7", "A-rule, store ρ 0.7", BLUE, "s"),
                                             ("terr_0.9", "T-rule, exclusion θ 0.9", GREEN, "^"),
                                             ("own_0.0", "A-rule, W_own (size)", GRAY, "x"),
                                             ("env_0.5", "A-rule, W_env (size)", RED, "x")]):
        rule = "T" if key.startswith("terr") else "A"
        v = [syn["r1"][key]["per_unit"].get(u, {}).get(rule) for u in units]
        a.plot(x, [np.nan if t is None else t for t in v], mk, color=col, label=lab, ms=6)
    a.axhline(0.8, color="k", lw=0.6, ls="--")
    a.set_xticks(x, units, rotation=60, fontsize=8)
    a.set_ylabel("detection rate (20 replicates)")
    a.set_title("(a) synthetic: detection on real schedules", fontsize=10)
    a.legend(fontsize=7, loc="upper left")
    # (b) village herding vs exclusion (real)
    b = ax[0, 1]
    for u in units:
        v = r1[u]["village"]
        col = BLUE if u in R.REPL else GREEN
        b.scatter(v["lam_V_ratio"], v["T_V"], color=col, s=25)
        b.annotate(u, (v["lam_V_ratio"], v["T_V"]), fontsize=7, xytext=(3, 2), textcoords="offset points")
    b.axvline(1, color="k", lw=0.6)
    b.axhline(0, color="k", lw=0.6)
    b.set_xlabel("Λ_V / rotation mean (attraction)")
    b.set_ylabel("T_V (exclusion; < 0 = co-working)")
    b.set_title("(b) village level per unit (blue: replication)", fontsize=10)
    # (c) file level per shared repo
    c = ax[1, 0]
    keys = sorted(r2)
    zl = [r2[k]["village"]["z_lam"] for k in keys]
    zt = [r2[k]["village"]["z_T"] for k in keys]
    ze = [r2[k]["static"].get("z_excl") for k in keys]
    xx = np.arange(len(keys))
    c.plot(xx, [np.nan if z is None else z for z in zl], "o", color=BLUE, ms=4, label="Λ_file z (rotation)")
    c.plot(xx, [np.nan if z is None else z for z in zt], "^", color=GREEN, ms=4, label="T_file z (rotation)")
    c.plot(xx, [np.nan if z is None else min(z, 15) for z in ze], "s", color=GRAY, ms=3,
           label="exclusivity z (random partition, cap 15)")
    c.axhline(2, color="k", lw=0.6, ls="--")
    c.axhline(-2, color="k", lw=0.6, ls="--")
    c.set_xlabel("eligible (unit, shared repo)")
    c.set_ylabel("z")
    c.set_title("(c) file level inside shared repos", fontsize=10)
    c.legend(fontsize=7)
    # (d) R3
    d = ax[1, 1]
    st = r3["store"]
    ru = r3["read_unread"]
    labels = ["I_store F", "I_store P"]
    vals = [st["I_store_F"], st["I_store_P"]]
    err = [st["I_store_F_ci"], st["I_store_P_ci"]]
    d.bar([0, 1], vals, color=[RED, GRAY], width=0.6)
    d.errorbar([0, 1], vals, yerr=np.abs(np.array(err).T - np.array(vals)), fmt="none", color="k", capsize=3)
    d.set_xticks([0, 1], labels)
    d.set_ylabel("bits (KL vs time-shifted artifact)")
    d2 = d.twinx()
    d2.errorbar([2.5], [ru["inter"]], yerr=[[ru["inter"] - ru["inter_ci"][0]], [ru["inter_ci"][1] - ru["inter"]]],
                fmt="o", color=BLUE, capsize=3)
    d2.axhline(0, color=BLUE, lw=0.5, ls=":")
    d2.set_ylabel("read × erasure log-OR (return to r1)", color=BLUE)
    d.set_xlim(-0.6, 3.1)
    d.set_xticks([0, 1, 2.5], labels + ["read × F"])
    d.set_title("(d) the pair after forced erasures (NE41)", fontsize=10)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "r2_summary.pdf")
    print("wrote", FIG / "r2_summary.pdf")


if __name__ == "__main__":
    main()
