"""H43 round 2 summary figure -> figures/r2_summary.pdf (also used by the 2-page summary)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "data/processed/H43-kick-refractory-window/r2"
FIG = ROOT / "hypotheses/H43-kick-refractory-window/figures/r2_summary.pdf"
C1, C2, C3, GREY = "#1f4e79", "#c05a28", "#5a8f3a", "#8a8a8a"


def err(s):
    return [[s["est"] - s["ci"][0]], [s["ci"][1] - s["est"]]]


def main():
    r3 = json.loads((D / "results_r3.json").read_text())
    r5 = json.loads((D / "results_r5.json").read_text())
    r6 = json.loads((D / "results_r6.json").read_text())
    ph = json.loads((D / "posthoc_r2.json").read_text())
    fig, ax = plt.subplots(2, 2, figsize=(7.2, 5.6))

    # (a) R2: escape at the wake by wake index, nudged vs not
    a = ax[0, 0]
    bands = list(ph["P2"].keys())
    x = np.arange(len(bands))
    for lab, key, col, mk in (("first nudge", "first", C1, "o"), ("re-fire, new trap", "refire_new", C3, "s"),
                              ("re-fire, same trap", "refire_same", C2, "^"), ("no nudge (no nudge in 4 h)", "none_state0", GREY, ".")):
        vals = [ph["P2"][b][key]["rate"] if ph["P2"][b][key]["n"] >= 10 else np.nan for b in bands]
        a.plot(x, vals, marker=mk, color=col, label=lab, lw=1.2)
    vals = [ph["P2"][b]["none_state1"]["rate"] if ph["P2"][b]["none_state1"]["n"] >= 10 else np.nan for b in bands]
    a.plot(x, vals, ls=":", color=C2, lw=1, label="no nudge, after an ignored nudge")
    a.set_xticks(x, [b.replace("-inf", "+") for b in bands])
    a.set_xlabel("wake index k in the trap (re-pauses)")
    a.set_ylabel("P(sustained escape at the wake)")
    a.set_ylim(0, 1.35)
    a.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    a.set_title("(a) nudges at a timer wake (G51, before 08-21)", fontsize=9, loc="left")
    a.legend(fontsize=5.8, frameon=False, loc="upper center", ncol=2)

    # (b) R3: dose curve in one read (G51) for all calls and for Gemini logged starts
    b = ax[0, 1]
    g = r3["periods"]["G51"]["stats"]
    sens = r3["g51_sens"]
    for lab, s, col, off in (("all calls (S1)", g, C1, -0.08), ("Gemini, logged starts (S2)", sens["S2_gemini_logged"]["stats"], C2, 0.0),
                             ("timer wake, sustained escape", r3["timer_wake"]["G51"]["stats"], C3, 0.08)):
        f1 = s["f1"]["est"]
        pts = [0, f1, f1 + s["m2"]["est"], f1 + s["m2"]["est"] + s["m3"]["est"]] if "m3" in s else None
        if pts is None:
            continue
        b.plot(np.arange(4) + off, pts, "o-", color=col, label=lab, lw=1.2)
        b.errorbar([1 + off], [f1], yerr=err(s["f1"]), color=col, capsize=2, lw=0.8)
    b.set_xticks(range(4), ["0", "1", "2", "3+"])
    b.set_xlabel("directed items read in one call")
    b.set_ylabel("log OR vs no directed item")
    b.set_title("(b) the k-th kick inside one read (G51)", fontsize=9, loc="left")
    b.legend(fontsize=6.5, frameon=False, loc="lower right")

    # (c) R5: directed-read effect at fresh vs re-kicked wakes, per period
    c = ax[1, 0]
    per = r5["strict"]["periods"]
    ps = [p for p, v in per.items() if v.get("fit")]
    for i, p in enumerate(ps):
        key = "stats" if p == "G51" else "stats_pen"
        s = per[p][key]
        c.errorbar([i - 0.12], [s["b_fresh"]["est"]], yerr=err(s["b_fresh"]), fmt="o", color=C1, capsize=2, label="fresh wake" if i == 0 else None)
        c.errorbar([i + 0.12], [s["b_re"]["est"]], yerr=err(s["b_re"]), fmt="s", color=C2, capsize=2,
                   label="after an effective isolated primer" if i == 0 else None)
    c.axhline(0, color=GREY, lw=0.8)
    c.set_xticks(range(len(ps)), [f"{p}\n{per[p]['n_D_fresh']}/{per[p]['n_D_rekick']}" for p in ps], fontsize=7)
    c.set_ylabel("log OR of a directed read at the wake")
    c.set_title("(c) re-kicked vs fresh timer wakes (regime III)", fontsize=9, loc="left")
    c.legend(fontsize=6.5, frameon=False, loc="upper right")

    # (d) R6: the NE43 drop by segment: raw rate, per-read escape, cadence
    d = ax[1, 1]
    seg = r6["segments_raw"]
    ks = list(seg)
    x = np.arange(len(ks))
    d.bar(x - 0.25, [100 * seg[k]["rel_R"] for k in ks], 0.25, color=C1, label="escapes per idle minute")
    d.bar(x, [100 * seg[k]["rel_cadence"] for k in ks], 0.25, color=C2, label="idle reads per idle minute")
    d.bar(x + 0.25, [100 * seg[k]["rel_p"] for k in ks], 0.25, color=C3, label="escape per idle read")
    d.axhline(0, color=GREY, lw=0.8)
    d.set_xticks(x, ["08-21\nnudger off", "08-24–27\none room", "08-28–09-02\n+2 agents", "09-03–04\n+3 agents"], fontsize=7)
    d.set_ylabel("% change vs 08-06 – 08-20")
    d.set_title("(d) where the NE43 drop sits", fontsize=9, loc="left")
    d.set_ylim(-28, 30)
    d.legend(fontsize=6, frameon=False, loc="upper left")
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG)
    print("wrote", FIG)


if __name__ == "__main__":
    main()
