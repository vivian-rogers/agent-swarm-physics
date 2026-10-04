"""Write H59 per-period estimates (shared table) and the summary figures."""
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
import h59lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

FIG = HERE.parent / "figures"
COL = {"delay": "#2a78d6", "lever": "#eb6834", "dir": "#1baf7a", "free": "#eda100"}
NAME = {"N": "nudge", "Hu": "human, broadcast", "Hm": "human, named", "A": "@-mention"}


def load_period(g):
    if g == 5:
        return json.loads((L.OUT / "native/G05.json").read_text()), "native"
    return json.loads((L.OUT / f"G{g:02d}/results.json").read_text()), "replication"


def rows():
    out = []
    for g in (51, 38, 4, 5):
        r, role = load_period(g)
        base = dict(period_unit=f"G{g:02d}", goal_no=g, role=role, source=f"data/processed/H59-one-lever-model/"
                    + (f"G{g:02d}/results.json" if role == "replication" else "native/G05.json"),
                    first_day=r["days"][0], last_day=r["days"][1])
        meth = "three-state call-level Markov GLM, one-lever constraint, receiving-call aligned (DQ1), baseline offset"
        th = r["triples"]["theta_deg"]
        out.append(dict(base, statistic="one_lever_field_direction_deg", channel="all", estimate=th["est"],
                        ci_lo=th["ci"][0] if th["ci"] else None, ci_hi=th["ci"][1] if th["ci"] else None, ci_level=0.95,
                        ci_kind="percentile" if th["ci"] else "none", n=r["n_exposed"], n_kind="exposed transitions",
                        method=meth + "; day-block bootstrap", null="none"))
        for c in r["classes"]:
            lo = r["loco"][c]
            for k in ("kappa", "h"):
                x = r["triples"][c][k]
                out.append(dict(base, statistic=f"one_lever_{'catalytic_kappa' if k == 'kappa' else 'field_h'}", channel=c,
                                estimate=x["est"], ci_lo=x["ci"][0], ci_hi=x["ci"][1], ci_level=0.95, ci_kind="percentile",
                                n=lo["n_rec"], n_kind="receiving calls", method=meth + "; day-block bootstrap",
                                null="0 (inert)"))
            if c in r["readout"]:
                ro = r["readout"][c]
                out.append(dict(base, statistic="readout_delay_median_s", channel=c, estimate=ro["median_s"], ci_lo=ro["q25_s"],
                                ci_hi=ro["q75_s"], ci_level=0.5, ci_kind="none", n=ro["n_items"], n_kind="kick items",
                                method="DQ1 ledger age at the receiving call (IQR in ci columns)", null="none"))
            if lo["T"] is not None:
                out.append(dict(base, statistic="loco_transfer_ratio_T", channel=c, estimate=lo["T"], ci_lo=lo["ci"]["T"][0],
                                ci_hi=lo["ci"]["T"][1], ci_level=0.95, ci_kind="percentile", n=lo["n_rec"],
                                n_kind="receiving calls", method="leave-one-class-out, 5-fold day CV, S_H59/S_free",
                                null="1 (one lever loses nothing)"))
            d = lo["ci"]["lever-delay"]
            out.append(dict(base, statistic="loco_skill_lever_minus_delay_nats", channel=c,
                            estimate=lo["S"]["lever"] - lo["S"]["delay"], ci_lo=d[0], ci_hi=d[1], ci_level=0.95,
                            ci_kind="percentile", n=lo["n_rec"], n_kind="receiving calls",
                            method="leave-one-class-out held-out log-likelihood, day-block bootstrap",
                            null="0 (read-out delay alone)"))
    ne = json.loads((L.OUT / "native/NE43.json").read_text())
    tr = ne["transfer"]
    out.append(dict(period_unit="G51", goal_no=51, role="native", statistic="ne43_pre_to_post_transfer_ratio", channel="all",
                    estimate=tr["ratio"], ci_lo=tr["ratio_ci"][0], ci_hi=tr["ratio_ci"][1], ci_level=0.95, ci_kind="percentile",
                    n=ne["n_days"][1], n_kind="post days", method="pre-fitted one-lever model on post-08-21 kicked rows vs 5-fold post CV refit",
                    null="1", source="data/processed/H59-one-lever-model/native/NE43.json", notes="NE43 nudger stop"))
    return out


def figure():
    cells = []
    for g in (51, 38, 4, 5):
        r, _ = load_period(g)
        sp = {}
        f = L.OUT / f"G{g:02d}/loco_split.json"
        if f.exists():
            sp = json.loads(f.read_text())
        for c in r["classes"]:
            lo = r["loco"][c]
            s = sp.get(c, {}).get("split") or lo.get("split_early_late")
            cells.append((f"G{g:02d} {c}", lo, s))
    cells = [x for x in cells if x[1]["ci"]["free"][0] > 0]          # informative cells only
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.5, 1]})
    y = np.arange(len(cells))[::-1]
    for k, m in enumerate(["delay", "lever", "dir"]):
        vals = [x[1]["S"][m] / x[1]["S"]["free"] for x in cells]
        ax[0].scatter(np.clip(vals, -0.6, 1.6), y + (k - 1) * 0.22, s=28, color=COL[m], zorder=3,
                      label={"delay": "read-out delay alone", "lever": "H59 one lever", "dir": "own direction"}[m])
    ax[0].axvline(1, color="#52514e", lw=1)
    ax[0].axvline(0.8, color="#52514e", lw=1, ls=":")
    ax[0].axvline(0, color="#c3c2b7", lw=1)
    ax[0].set_yticks(y)
    ax[0].set_yticklabels([x[0] for x in cells], fontsize=7)
    ax[0].set_xlabel("held-out skill / class-specific free fit", fontsize=8)
    ax[0].set_xlim(-0.65, 1.65)
    ax[0].tick_params(labelsize=7)
    ax[0].legend(fontsize=6, loc="lower right", frameon=False)
    ax[0].set_title("(a) leave one class out (clipped at −0.6)", fontsize=8)
    # (b) early vs late: H59 / free for informative cells with a split
    ys = [x for x in cells if x[2]]
    yy = np.arange(len(ys))[::-1]
    for j, (part, mk) in enumerate((("early", "o"), ("late", "s"))):
        vals = []
        for x in ys:
            fr = x[2]["free"][part]
            vals.append(x[2]["lever"][part] / fr if fr > 1 else np.nan)
        ax[1].scatter(np.clip(vals, -0.6, 1.6), yy + (j - 0.5) * 0.25, marker=mk, s=28,
                      color=COL["lever"] if part == "early" else "#52514e", zorder=3,
                      label="read 0–2 calls ago" if part == "early" else "read 3–30 calls ago")
    ax[1].axvline(1, color="#52514e", lw=1)
    ax[1].axvline(0.8, color="#52514e", lw=1, ls=":")
    ax[1].set_yticks(yy)
    ax[1].set_yticklabels([x[0] for x in ys], fontsize=7)
    ax[1].set_xlim(-0.65, 1.65)
    ax[1].tick_params(labelsize=7)
    ax[1].set_xlabel("H59 skill / free fit", fontsize=8)
    ax[1].legend(fontsize=6, loc="lower left", frameon=False)
    ax[1].set_title("(b) read-out vs tail (post hoc)", fontsize=8)
    for a in ax:
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=150)
    # synthetic figure: recovery
    s = json.loads((L.OUT / "synthetic/summary.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6))
    for g, mk in (("G51", "o"), ("G38", "s")):
        for r in s[g]["recovery"]:
            ax[0].scatter(r["h"][0], r["h"][1], marker=mk, color=COL["lever"], s=24)
            ax[0].scatter(r["kappa"][0], r["kappa"][1], marker=mk, color=COL["delay"], s=24)
    ax[0].plot([-0.2, 3], [-0.2, 3], color="#52514e", lw=1)
    ax[0].set_xlabel("planted", fontsize=8)
    ax[0].set_ylabel("recovered", fontsize=8)
    ax[0].set_title("(a) κ (blue), h (orange); ○ G51, □ G38", fontsize=8)
    worlds = ["lever", "dirviol", "delay", "null"]
    for g, off, mk in (("G51", -0.12, "o"), ("G38", 0.12, "s")):
        for k, (key, cells_) in enumerate(s[g]["cells"].items()):
            w = key.rsplit("_", 1)[0]
            for c, (st, T) in cells_.items():
                if T is None or st == "uninformative":
                    continue
                ax[1].scatter(np.clip(T, -0.5, 2.2), worlds.index(w) + off, marker=mk,
                              color={"pass": COL["dir"], "fail": "#d03b3b", "mixed": COL["free"]}[st], s=24)
    ax[1].axvline(0.8, color="#52514e", lw=1, ls=":")
    ax[1].set_yticks(range(4))
    ax[1].set_yticklabels(["one lever", "direction violated", "delay only", "null"], fontsize=7)
    ax[1].set_xlabel("transfer ratio T (informative cells)", fontsize=8)
    ax[1].set_title("(b) LOCO verdicts: pass green, fail red, mixed yellow", fontsize=8)
    for a in ax:
        a.tick_params(labelsize=7)
        for sp_ in ("top", "right"):
            a.spines[sp_].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_validation.pdf")
    fig.savefig(FIG / "synthetic_validation.png", dpi=150)


if __name__ == "__main__":
    figure()
    df = E.write_estimates(rows(), hypothesis="H59")
    print(df.height, "estimate rows written")
