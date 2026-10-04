"""H102: verdicts by the card's rules, per-unit result tables (results/results.json), estimates rows and figures.

Usage: uv run python hypotheses/H102-room-domain-walls/analysis/summarize.py [--estimates] [--figures]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
H = HERE.parent
ROOT = H.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h102lib as L  # noqa: E402

RES = L.DATA / "results"
FIG = H / "figures"
NAMES = {31: "Claude Fable 5", 27: "Gemini 3.5 Flash", 34: "GLM-5.2", 17: "DeepSeek-V3.2", 26: "GPT-5.5",
         13: "Claude Haiku 4.5", 6: "Gemini 2.5 Pro", 29: "Claude Opus 4.8"}
ROLE = {"G35": "replication", "G37": "replication", "G39": "replication", "G41": "replication", "G42": "replication",
        "G38": "native", "G44": "native", "51g": "native", "G36": "native"}
P = "bge_small_style_resid"; G = "gte_modernbert_style_resid"


def f2(x, n=2):
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{n}f}"


def verdict(u, R):
    x = R[P]["units"][u]; b = x["bimodality"]
    if ROLE[u] == "replication":
        if b["D"] >= 2 and b["p"] < 0.05:
            return "supported"
        if b["D"] < 1 or b["p"] > 0.2:
            return "failed"
        return "mixed"
    if u in ("G38", "G44"):
        ok = b["D"] >= 2 and b["p"] < 0.05 and x["field_alignment"]["p"] < 0.05
        return "supported" if ok else ("failed" if b["D"] < 1 else "mixed")
    if u == "51g":
        hp = x["hoppers"]
        many = [k for k, v in hp["hoppers"].items() if sum(1 for d in v["days"].values() if d["n_all"] > d["n_home"]) >= 5]
        inter = [k for k in many if hp["home_stayers_p95"] < hp["hoppers"][k]["s_all"] < 1]
        if not inter:
            return "failed"
        d = x["dose"]
        return "supported" if (d.get("kappa_R", 0) > 0 and d["kappa_R_ci_day"][0] > 0) else "mixed"
    if u == "G36":
        h = x["hoppers"]["hoppers"]["17"]
        sh = h["s_other"] - h["s_home"]
        return "supported" if sh >= 0.3 else ("failed" if sh < 0 else "mixed")


def unit_md(u, R):
    rows = []
    for tag, lab in ((P, "bge style_resid"), (G, "gte style_resid"), ("bge_small_white32", "bge white32"),
                     ("bge_small_style_resid_dedupe", "bge dedupe")):
        x = R[tag]["units"][u]; b = x["bimodality"]
        rows.append(f"| {lab} | {f2(b['D'])} | {f2(b['D_null_p95'])} | {b['p']:.3f} | {f2(b['I_stayers'])} | {f2(b['acc'])} |")
    x = R[P]["units"][u]
    t = ("| Instrument | D | relabel D p95 | p | I (stayers) | stayers on their side |\n| --- | --- | --- | --- | --- | --- |\n"
         + "\n".join(rows)
         + f"\n\nStayers: home A (room {x['A']}) {x['bimodality']['n_A']}, home B (room {x['B']}) {x['bimodality']['n_B']}. "
         f"Cross-domain read share: P_hop {x['P_hop']:.4f} (items read while in the other room), P_dom {x['P_dom']:.4f} "
         "(items from other-domain senders). Relabel null: 1,000 draws, axis refitted.")
    if "field_alignment" in x:
        fa, fg = x["field_alignment"], R[G]["units"][u]["field_alignment"]
        t += (f"\n\n**Domain axis vs room-kickoff direction:** |cos| {f2(fa['cos'])} (direction-null p95 {f2(fa['null_p95'])}, "
              f"p {fa['p']:.3f}); gte {f2(fg['cos'])} (p {fg['p']:.3f}).")
    if "hoppers" in x:
        hp, hg = x["hoppers"], R[G]["units"][u]["hoppers"]
        t += (f"\n\n**Hoppers** (wall coordinate s: 0 = home domain centroid, 1 = other domain). Home stayers: median "
              f"{f2(hp['home_stayers_median'])}, 95th percentile {f2(hp['home_stayers_p95'])}.\n\n"
              "| Hopper | statements home / other room | hop-days | s(all) | s(home) | s(statements in other room) | gte s(all) |\n"
              "| --- | --- | --- | --- | --- | --- | --- |\n")
        for k, v in hp["hoppers"].items():
            hd = sum(1 for d in v["days"].values() if d["n_all"] > d["n_home"])
            t += (f"| {NAMES.get(int(k), k)} | {v['n_home']} / {v['n_other']} | {hd} | {f2(v['s_all'])} | {f2(v['s_home'])} | "
                  f"{f2(v['s_other'])} | {f2(hg['hoppers'][k]['s_all'])} |\n")
    if u == "51g":
        for tag, lab in ((P, "bge"), (G, "gte")):
            d, dl, da = R[tag]["units"][u]["dose"], R[tag]["units"][u]["dose_lag"], R[tag]["units"][u]["dose_all_agents"]
            t += (f"\n**Dose–response ({lab}; {d['n']} hopper-days, {d['n_hoppers']} hoppers, hopper fixed effects):** "
                  f"κ_R {f2(d['kappa_R'], 3)} [{f2(d['kappa_R_ci_day'][0], 3)}, {f2(d['kappa_R_ci_day'][1], 3)}] (day bootstrap), "
                  f"κ_U {f2(d['kappa_U'], 3)} [{f2(d['kappa_U_ci_day'][0], 3)}, {f2(d['kappa_U_ci_day'][1], 3)}]; lagged κ_R "
                  f"{f2(dl['kappa_R'], 3)} [{f2(dl['kappa_R_ci_day'][0], 3)}, {f2(dl['kappa_R_ci_day'][1], 3)}]. All #general "
                  f"agents ({da['n']} agent-days): κ on reads from #focus-home senders {f2(da['kappa_Rdom'], 4)} "
                  f"[{f2(da['kappa_Rdom_ci_day'][0], 4)}, {f2(da['kappa_Rdom_ci_day'][1], 4)}].\n")
        rv = R[P]["units"][u]["reverse_hoppers"]
        t += ("\n**Reverse hoppers** (#focus core members' statements in #general; s from their own home, the other core "
              "member's centroid = 0, #general = 1): " + "; ".join(
                  f"{NAMES[int(k)]} s(#focus statements) {f2(v['s_home'])}, s(#general statements) {f2(v['s_other'])}"
                  for k, v in rv.items()) + ".\n")
    return t


SC = {"G38": "- **C:** relabel null on D; **G:** room-specific kickoffs are known structure; the axis is not the kickoff direction.",
      "G44": "- **C:** relabel null on D; **G:** room kickoffs; the axis is not the kickoff direction.",
      "51g": "- **C:** stayer distribution and posted-unread placebo; **D:** hopper wall coordinate; **F:** synthetic power on this skeleton (Amendment 1).",
      "G36": "- **D:** one hopper's wall coordinate before, during and after; **E:** the 03-26 → 03-30 stint."}


def build():
    R = json.loads((RES / "raw_all.json").read_text())
    out = {"units": {}}
    for u in L.UNITS:
        out["units"][u] = {"verdict": verdict(u, R), "result_md": "*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; "
                           "non-holdout).*\n\n" + unit_md(u, R),
                           "scorecard_md": SC.get(u, "- **C:** relabel null on D (axis refitted); **F:** D size and power "
                                                     "on fixed-room skeletons (Amendment 1).")}
    (RES / "results.json").write_text(json.dumps(out, indent=1))
    return out


def estimates():
    import estimates as E
    R = json.loads((RES / "raw_all.json").read_text())
    rows = []
    for tag, ch in ((P, "content_bge_style_resid"), (G, "content_gte_style_resid")):
        for u in L.UNITS:
            x = R[tag]["units"][u]; b = x["bimodality"]
            goal = 51 if u == "51g" else int(u[1:])
            base = {"period_unit": u, "goal_no": goal, "role": ROLE[u], "channel": ch, "post_hoc": False,
                    "source": f"data/processed/H102-room-domain-walls/results/raw_all.json[{tag}]"}
            rows.append({**base, "statistic": "domain_bimodality_D", "estimate": b["D"], "ci_lo": None, "ci_hi": None,
                         "ci_kind": "none", "n": b["n_A"] + b["n_B"], "n_kind": "stayers",
                         "method": "Ashman D of cross-fitted axis projections (alternating-day halves, LOO centroids)",
                         "null": f"room relabel, axis refitted (1000); p={b['p']:.4f}; null p95={b['D_null_p95']:.2f}"})
            rows.append({**base, "statistic": "cross_domain_read_share_P_hop", "estimate": x["P_hop"], "ci_lo": None,
                         "ci_hi": None, "ci_kind": "none", "n": None, "n_kind": None,
                         "method": "ledger items received while outside the home room / all agent items", "null": "none"})
        d = R[tag]["units"]["51g"]["dose"]
        rows.append({"period_unit": "51g", "goal_no": 51, "role": "native", "channel": ch, "post_hoc": False,
                     "source": f"data/processed/H102-room-domain-walls/results/raw_all.json[{tag}]",
                     "statistic": "hopper_dose_kappa_R", "estimate": d["kappa_R"], "ci_lo": d["kappa_R_ci_day"][0],
                     "ci_hi": d["kappa_R_ci_day"][1], "ci_kind": "percentile", "n": d["n"], "n_kind": "hopper-days",
                     "method": "WLS of hopper-day s(home) on log1p(hopping read-outs) + log1p(posted-unread), hopper FE",
                     "null": f"posted-unread placebo kappa_U={d['kappa_U']:.3f}"})
    E.write_estimates(rows, hypothesis="H102")
    print("estimates rows", len(rows))


def figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    C1, C2, C3, GR, INK, MUT = "#2a78d6", "#eb6834", "#1baf7a", "#a9a8a1", "#0b0b0b", "#52514e"
    plt.rcParams.update({"font.size": 7.5, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUT,
                         "xtick.color": MUT, "ytick.color": MUT})
    R = json.loads((RES / "raw_all.json").read_text())
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1.05, 1]})
    units = ["G38", "G44", "G41", "G35", "G37", "G39", "G42", "51g"]
    col = {"G38": C2, "G44": C2, "G41": C3, "G35": C3, "G37": GR, "G39": GR, "G42": GR, "51g": C1}
    x = np.arange(len(units))
    for i, u in enumerate(units):
        bb, bg = R[P]["units"][u]["bimodality"], R[G]["units"][u]["bimodality"]
        a.bar(i - 0.18, bb["D"], 0.34, color=col[u], edgecolor="white")
        a.bar(i + 0.18, bg["D"], 0.34, color=col[u], alpha=0.55, edgecolor="white")
        a.plot([i - 0.38, i + 0.38], [bb["D_null_p95"]] * 2, color=INK, lw=1)
    a.axhline(2, color=MUT, ls=":", lw=1)
    a.set_xticks(x, ["#38", "#44", "#41", "#35", "#37", "#39", "#42", "51g"])
    a.set_ylabel("bimodality D (bge | gte)")
    a.set_title("(a) two domains per unit; line = relabel p95", fontsize=7.5, loc="left")
    for c, lab in ((C2, "room instructions"), (C3, "work split"), (GR, "identical"), (C1, "#focus")):
        a.bar([0], [0], color=c, label=lab)
    a.legend(frameon=False, fontsize=5.8, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.02), handlelength=1)
    a.set_ylim(0, 7.2)
    # (b) 51g wall coordinate
    hp = R[P]["units"]["51g"]["hoppers"]; rv = R[P]["units"]["51g"]["reverse_hoppers"]
    st = list(hp["stayers"].values())
    st_gen = [hp["stayers"][k] for k in hp["stayers"] if R[P]["units"]["51g"]["s_by_agent"].get(k, {}).get("home", 0) == 0]
    b.scatter(st_gen, np.full(len(st_gen), 3) + np.random.default_rng(0).uniform(-0.15, 0.15, len(st_gen)), s=12,
              color=GR, label="#general stayers")
    names = []
    for j, (k, v) in enumerate(hp["hoppers"].items()):
        y = 2 - 0.3 * j
        b.plot([v["s_home"]], [y], "o", color=C1, ms=5)
        if v["s_other"] is not None:
            b.plot([v["s_other"]], [y], "o", mfc="white", mec=C1, ms=5)
            b.plot([v["s_home"], v["s_other"]], [y, y], color=C1, lw=1)
        b.text(-0.62, y, NAMES[int(k)], fontsize=5.8, va="center", color=INK)
    for j, (k, v) in enumerate(rv.items()):
        y = 0.2 - 0.3 * j
        b.plot([1 - v["s_home"]], [y], "s", color=C2, ms=5)
        b.plot([1 - v["s_other"]], [y], "s", mfc="white", mec=C2, ms=5)
        b.plot([1 - v["s_home"], 1 - v["s_other"]], [y, y], color=C2, lw=1)
        b.text(-0.62, y, NAMES[int(k)] + " (core)", fontsize=5.8, va="center", color=INK)
    b.axvline(hp["home_stayers_p95"], color=MUT, ls=":", lw=1)
    b.set_xlim(-0.65, 1.1); b.set_yticks([]); b.set_xlabel("wall coordinate s (0 = #general, 1 = #focus core)")
    b.set_title("(b) 51g: filled = home-room talk, open = talk in the other room", fontsize=7, loc="left")
    b.spines["left"].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)
    # synthetic
    S = json.loads((L.DATA / "synthetic/synthetic_summary.json").read_text())["hoppers"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.0))
    ws = [("none_k0.0", "none"), ("coupling_k0.1", "coupling 0.1"), ("coupling_k0.3", "coupling 0.3"),
          ("selection_k0.3", "selection"), ("field_k0.0", "own field"), ("mixture_k0.0", "mixture")]
    xx = np.arange(len(ws))
    a.bar(xx - 0.2, [S[w]["kR"] for w, _ in ws], 0.38, color=C1, label="κ_R (same day)")
    a.bar(xx + 0.2, [S[w]["kR_lag"] for w, _ in ws], 0.38, color=C3, label="κ_R (lagged)")
    a.axhline(0, color=MUT, lw=0.8)
    a.set_xticks(xx, [w[1] for w in ws], fontsize=6, rotation=20); a.set_ylabel("recovered κ (median)")
    a.legend(frameon=False, fontsize=6); a.set_title("(a) dose–response on the 51g skeleton", fontsize=7.5, loc="left")
    b.bar(xx - 0.2, [S[w]["s_all"] for w, _ in ws], 0.38, color=C2, label="hopper s(all)")
    b.bar(xx + 0.2, [S[w]["stay_p95"] for w, _ in ws], 0.38, color=GR, label="stayers p95")
    b.set_xticks(xx, [w[1] for w in ws], fontsize=6, rotation=20); b.legend(frameon=False, fontsize=6)
    b.set_title("(b) is the hopper intermediate?", fontsize=7.5, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "summary_synthetic.pdf"); plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    out = build()
    for k, v in out["units"].items():
        print(k, v["verdict"])
    if "--estimates" in sys.argv:
        estimates()
    if "--figures" in sys.argv:
        figures()
