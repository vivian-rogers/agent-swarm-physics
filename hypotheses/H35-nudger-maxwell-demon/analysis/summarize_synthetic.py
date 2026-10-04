"""Summarize the H35 synthetic validation: recovery of information, work, policy values and efficiencies.

Reads data/processed/H35-nudger-maxwell-demon/synthetic/synthetic_results.json; writes synthetic_summary.json and
figures/synthetic_validation.pdf.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h35lib as L  # noqa: E402

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

KEYS = ("V_rand_per_nudge", "V_log_per_nudge", "dV_per_nudge", "eta_SU", "eta_KW", "bits_per_nudge",
        "ratio_gate_once1_vs_logged", "ratio_gate_once2_vs_logged")


def stat(v):
    v = np.array([x for x in v if x is not None and np.isfinite(x)], float)
    if len(v) == 0:
        return None
    return {"mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else None, "n": int(len(v))}


def main():
    d = json.loads((L.OUT / "synthetic" / "synthetic_results.json").read_text())
    summ = {}
    for key, block in d["results"].items():
        reps = [r for r in block["reps"] if "error" not in r]
        s = {"n_reps": len(block["reps"]), "n_ok": len(reps), "policy": block["policy"],
             "n_nudges": stat([r["n_nudges"] for r in reps])}
        if not reps:
            summ[key] = s
            continue
        s["bits_per_nudge_minute"] = stat([r["info"]["I_X"]["bits_per_nudge"] for r in reps if "I_X" in r["info"]])
        s["info_above_null"] = float(np.mean([r["info"]["I_X"]["above_null"] for r in reps if "I_X" in r["info"]]))
        s["share_DK"] = stat([r["info"].get("share_DK") for r in reps])
        s["share_A_given_X"] = stat([r["info"].get("share_A_given_X") for r in reps])
        s["att_first_pastonly"] = stat([r["att_first_pastonly"][0] for r in reps])
        s["att_first_pastonly_ci_excl0"] = float(np.mean([r["att_first_pastonly"][1] > 0 for r in reps if r["att_first_pastonly"][1] is not None]))
        s["att_first_H04"] = stat([r["att_first_H04"][0] for r in reps])
        s["att_repeat"] = stat([r["att_repeat"][0] for r in reps])
        s["placebo_covers0"] = float(np.mean([(r["placebo"][1] <= 0 <= r["placebo"][2]) for r in reps if r["placebo"][1] is not None]))
        s["att_true_mc"] = stat([r.get("att_true_single_nudge_mc") for r in reps])
        s["gate_kick_x_lnk"] = stat([r["gate_beta"].get("kick_x_lnk") for r in reps])
        s["gate_nudge_offset"] = stat([r["gate_beta"].get("nudge_offset") for r in reps])
        for lab in ("true", "est", "est_separate", "est_minutes"):
            es = [r["eff"].get(lab, {}) for r in reps]
            es = [e for e in es if "error" not in e and e]
            s[lab] = {k: stat([e.get(k) for e in es]) for k in KEYS}
            s[lab]["gate_once1"] = stat([e.get("gate_once", {}).get("1") for e in es])
            s[lab]["gate_once2"] = stat([e.get("gate_once", {}).get("2") for e in es])
            s[lab]["n"] = len(es)
        summ[key] = s
    summ["truth_big"] = d.get("truth_big")
    L.jdump(summ, L.OUT / "synthetic" / "synthetic_summary.json")

    # figure: est vs true per scenario (G51-like), escapes
    scen = [k for k in summ if k.endswith("|G51like")]
    fig, ax = plt.subplots(1, 3, figsize=(10, 3.2))
    cols = {"S1_inefficient": "#c0392b", "S2_efficient": "#2471a3", "S3_flat": "#7f8c8d"}
    for k in scen:
        sname = k.split("|")[0]
        s = summ[k]
        if "true" not in s:
            continue
        c = cols.get(sname, "k")
        for j, (key, lab) in enumerate((("V_rand_per_nudge", "rand"), ("V_log_per_nudge", "logged"),
                                        ("gate_once1", "once k=1"), ("gate_once2", "once k=2"))):
            t, e = s["true"].get(key), s["est"].get(key)
            if t and e:
                ax[0].errorbar(t["mean"], e["mean"], yerr=e["sd"] or 0, fmt="o", color=c, ms=4, alpha=0.8)
        for key, mk in (("eta_SU", "s"), ("eta_KW", "^")):
            t, e = s["true"].get(key), s["est"].get(key)
            if t and e:
                ax[1].errorbar(t["mean"], e["mean"], yerr=e["sd"] or 0, fmt=mk, color=c, ms=5)
        tb = (summ.get("truth_big") or {}).get(sname, {})
        b = s.get("bits_per_nudge_minute")
        if tb and b:
            ax[2].errorbar(tb["bits_per_nudge_minute_X"], b["mean"], yerr=b["sd"] or 0, fmt="o", color=c, ms=5, label=sname)
    for a in ax[:2]:
        lim = [min(a.get_xlim()[0], a.get_ylim()[0]), max(a.get_xlim()[1], a.get_ylim()[1])]
        a.plot(lim, lim, "k:", lw=0.8)
    lim = [0, max(ax[2].get_xlim()[1], ax[2].get_ylim()[1])]
    ax[2].plot(lim, lim, "k:", lw=0.8)
    ax[0].set(xlabel="true value per nudge (escapes)", ylabel="estimated", title="policy values")
    ax[1].set(xlabel="true efficiency", ylabel="estimated", title=r"$\eta_{SU}$ (sq), $\eta_{KW}$ (tri)")
    ax[2].set(xlabel="large-sample bits / nudge", ylabel="estimated (MM, null-corrected)", title="information")
    ax[2].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    (L.HDIR / "figures").mkdir(exist_ok=True)
    fig.savefig(L.HDIR / "figures" / "synthetic_validation.pdf")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk in ("n_ok", "bits_per_nudge_minute", "att_first_pastonly",
                                                                  "att_true_mc", "att_first_H04", "placebo_covers0")}
                      for k, v in summ.items() if k != "truth_big"}, indent=1, default=str))


if __name__ == "__main__" and "--compact" not in sys.argv:
    main()


def compact():
    """Two-panel synthetic figure for the summary page (column width)."""
    summ = json.loads((L.OUT / "synthetic" / "synthetic_summary.json").read_text())
    tb = summ.get("truth_big") or {}
    cols = {"S1_inefficient": "#c0392b", "S2_efficient": "#2471a3", "S3_flat": "#7f8c8d"}
    fig, ax = plt.subplots(1, 2, figsize=(3.4, 1.75))
    for k, s in summ.items():
        if k == "truth_big" or "|" not in k or not s.get("n_ok"):
            continue
        sname, size = k.split("|")
        if size == "small":
            continue
        c = cols[sname]; mk = "o" if size == "G51like" else "s"
        b = s.get("bits_per_nudge_minute")
        if b and sname in tb:
            ax[0].errorbar(tb[sname]["bits_per_nudge_minute_X"], b["mean"], yerr=b["sd"] or 0, fmt=mk, color=c, ms=3.5, lw=0.8)
        for key in ("ratio_gate_once1_vs_logged", "eta_SU"):
            t, e = s["true"].get(key), s["est"].get(key)
            if t and e and size == "G51like":
                ax[1].errorbar(t["mean"], e["mean"], yerr=e["sd"] or 0, fmt="o" if key.startswith("ratio") else "^", color=c, ms=3.5, lw=0.8)
    ax[0].plot([0, 4.5], [0, 4.5], "k:", lw=0.6)
    ax[1].plot([-1.2, 4.5], [-1.2, 4.5], "k:", lw=0.6)
    ax[0].set_xlabel("true bits / nudge", fontsize=6); ax[0].set_ylabel("estimated", fontsize=6)
    ax[1].set_xlabel("true ratio (o) or $\\eta_{SU}$ (tri)", fontsize=6)
    for a in ax:
        a.tick_params(labelsize=5)
    ax[0].set_title("(a) information", fontsize=6.5, loc="left")
    ax[1].set_title("(b) policy ratio, efficiency", fontsize=6.5, loc="left")
    fig.tight_layout(pad=0.3)
    fig.savefig(L.HDIR / "figures" / "synthetic_compact.pdf")


if __name__ == "__main__" and "--compact" in sys.argv:
    compact()
