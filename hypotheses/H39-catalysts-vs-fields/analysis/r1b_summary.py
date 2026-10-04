"""H39 round 1b cross-period synthesis (2026-10-04): round 1 vs round 1b class verdicts on B4, the V4 (Jev v3.1)
second state space, lever_design ITT cross-check, receiving-call timing sensitivity, erasure, per-period verdicts
(round-1 rule unchanged), the NE44 native comparison, figure and per-period estimates.

Reads OUT/G<NN>/ (round 1) and OUT/r1b/G<NN>/ (round 1b), OUT/r1b/steps_native.json (natives).
Writes OUT/r1b/summary_r1b.json, figures/summary_obs_r1b.pdf.
Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/r1b_summary.py [--no-estimates]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h39lib as L  # noqa: E402
from summarize import content_pool, pooled_boot, unit_table  # noqa: E402
from write_results import score_period  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RNG = np.random.default_rng(L.SEED)
B4 = ["work", "chat", "idle", "consolidate"]
V4 = ["work", "coord", "wait", "maint"]
CLASSES = ("N_tgt", "H_any", "H_men", "H_und", "A_men")
TWELVE_H = ("G37", "G38", "G39", "G40", "G41", "G42", "G44")


def load(root):
    out = {}
    for d in sorted(root.glob("G*/results.json")):
        r = json.loads(d.read_text())
        bd = d.parent / "boot_draws.npz"
        if bd.exists():
            z = np.load(bd)
            for key in z.files:
                c, k = key.split("__")
                if c.startswith("erasure_"):
                    tgt = r.get("erasure", {}).get(c[len("erasure_"):])
                elif c.startswith("v4_"):
                    tgt = (r.get("v4") or {}).get(c[3:])
                else:
                    tgt = r.get("b4", {}).get(c)
                if isinstance(tgt, dict):
                    tgt.setdefault("_boot", {})[k] = z[key]
        out[r["period"]] = r
    return out


def class_block(P, getter):
    rows = unit_table(P, getter)
    units = [x["u"] for x in rows]
    v = L.class_verdict(units)
    v["probabilities"] = L.class_probabilities(units, RNG, R=2000)
    v["pooled_boot"] = pooled_boot(units)
    v["units"] = [{k: x[k] for k in x if k != "u"} for x in rows]
    return v


def short(v, names):
    m = v.get("K_meta", {})
    d = v.get("dpi_meta", [{}] * 4)
    e = v.get("esc_meta", [{}] * 4)
    return {"cls": v.get("cls"), "n_powered": v.get("n_powered"), "n_units": v.get("n_units"),
            "K": m.get("est"), "K_ci": m.get("ci"), "phi_exc_mean": v.get("phi_exc_mean"), "stouffer_pF": v.get("stouffer_pF"),
            "rho": v.get("rho"), "probabilities": v.get("probabilities"),
            "dpi": {names[s]: (d[s].get("est"), d[s].get("ci")) for s in range(min(len(d), len(names))) if d[s].get("k")},
            "esc": {names[s]: (e[s].get("est"), e[s].get("ci")) for s in range(min(len(e), len(names))) if e[s].get("k")}}


def pool_itt(P, c):
    xs = [r["lever_design"][c] for r in P.values() if isinstance(r.get("lever_design"), dict)
          and isinstance(r["lever_design"].get(c), dict) and r["lever_design"][c].get("status") == "ok"]
    xs = [x for x in xs if x["n_ep"] >= 20]
    if not xs:
        return {}
    se = [(x["diff_ci"][1] - x["diff_ci"][0]) / 3.92 for x in xs]
    m = L.dl_meta([x["diff"] for x in xs], se)
    return {"meta": m, "n_units": len(xs), "n_ep": int(sum(x["n_ep"] for x in xs))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    P1 = load(L.OUT)
    PB = load(L.OUT / "r1b")
    S = {"classes_r1": {}, "classes_r1b": {}, "classes_v4": {}, "erasure": {}, "itt": {}, "sens_rc": {}, "content_r1b": {},
         "periods": {}}
    for c in CLASSES:
        S["classes_r1"][c] = short(class_block(P1, lambda r: r.get("b4", {}).get(c)), B4)
        vb = class_block(PB, lambda r: r.get("b4", {}).get(c))
        S["classes_r1b"][c] = short(vb, B4)
        vv = class_block(PB, lambda r: (r.get("v4") or {}).get(c) if isinstance((r.get("v4") or {}).get(c), dict) else None)
        S["classes_v4"][c] = short(vv, V4)
        S["itt"][c] = pool_itt(PB, c)
        rc = [r["sens_rc"][c] for r in PB.values() if r.get("sens_rc", {}).get(c, {}).get("status") == "ok"]
        if rc:
            S["sens_rc"][c] = {"n_units": len(rc), "K_mean": float(np.mean([u["K"] for u in rc])),
                               "dpi_idle_mean": float(np.mean([u["dpi"][2] for u in rc])),
                               "esc_idle_mean": float(np.mean([u["esc"][2] for u in rc])),
                               "units": {p: {k: r["sens_rc"][c].get(k) for k in ("n_ep", "K", "K_ci", "dpi", "esc")}
                                         for p, r in PB.items() if r.get("sens_rc", {}).get(c, {}).get("status") == "ok"}}
        print(c, "r1", S["classes_r1"][c]["cls"], S["classes_r1"][c]["K"], "| r1b", S["classes_r1b"][c]["cls"],
              S["classes_r1b"][c]["K"], S["classes_r1b"][c]["K_ci"], "phi", S["classes_r1b"][c]["phi_exc_mean"],
              "| v4", S["classes_v4"][c]["cls"], S["classes_v4"][c]["K"], S["classes_v4"][c]["phi_exc_mean"], flush=True)
    for key in ("CF_b4", "CF_b4_nocons", "CV_b4_nocons", "CF_b6"):
        for lab, P in (("r1", P1), ("r1b", PB)):
            S["erasure"][f"{key}_{lab}"] = short(class_block(P, lambda r: r.get("erasure", {}).get(key)),
                                                 ["work", "chat", "idle"] if "nocons" in key else (B4 if "b4" in key else ["browse", "type", "shell", "chat", "idle", "consolidate"]))
    for kind in ("CF", "CV"):
        S["erasure"][f"v4_{kind}"] = short(class_block(PB, lambda r: (r.get("v4") or {}).get(f"erasure_{kind}")
                                                       if isinstance((r.get("v4") or {}).get(f"erasure_{kind}"), dict) else None), V4)
    for c in ("N_tgt", "H_any", "H_men", "A_men"):
        S["content_r1b"][c] = content_pool(PB, c)
    # per-period verdicts, round-1 rule
    for p, r in sorted(PB.items()):
        g = int(p[1:])
        v1, _ = score_period(g, P1[p]) if p in P1 else (None, None)
        vb, checks = score_period(g, r)
        S["periods"][p] = {"r1": v1, "r1b": vb, "checks": [(k, bool(o)) for k, o in checks],
                           "N_tgt": {k: r["b4"].get("N_tgt", {}).get(k) for k in ("n_ep", "K", "K_ci", "phi_exc", "p_F", "dpi", "esc", "status")},
                           "v4_N_tgt": {k: ((r.get("v4") or {}).get("N_tgt") or {}).get(k) for k in ("n_ep", "K", "K_ci", "phi_exc", "p_F", "dpi", "esc", "status")}}
    # NE44 native: idle escape log ratio and dpi_idle for N_tgt, 12-h side pooled vs G51
    def esc_se(u, s=2):
        return u["esc_boot_se"][s] if "esc_boot_se" in u else None
    side = [PB[p]["b4"]["N_tgt"] for p in TWELVE_H if p in PB and PB[p]["b4"].get("N_tgt", {}).get("n_ep", 0) >= 3
            and "esc" in PB[p]["b4"]["N_tgt"]]
    g51 = PB["G51"]["b4"]["N_tgt"]
    ne = {}
    for lab, key, s in (("esc_idle", "esc", 2), ("dpi_idle", "dpi", 2), ("K", "K", None)):
        if s is None:
            m = L.dl_meta([u["K"] for u in side], [u["K_boot_se"] for u in side])
            e51, s51 = g51["K"], g51["K_boot_se"]
        else:
            m = L.dl_meta([u[key][s] for u in side], [u[f"{key}_boot_se"][s] for u in side])
            e51, s51 = g51[key][s], g51[f"{key}_boot_se"][s]
        d = m["est"] - e51
        sd = np.sqrt(m["se"] ** 2 + s51 ** 2)
        ne[lab] = {"twelve_h": m, "G51": [e51, s51], "diff": [d, d - 1.96 * sd, d + 1.96 * sd]}
    ne["n_ep_12h"] = int(sum(u["n_ep"] for u in side))
    ne["periods"] = [p for p in TWELVE_H if p in PB and PB[p]["b4"].get("N_tgt", {}).get("n_ep", 0) >= 3]
    S["NE44"] = ne
    sp = L.OUT / "r1b" / "steps_native.json"
    if sp.exists():
        S["steps_native"] = json.loads(sp.read_text())
    L.jdump(S, L.OUT / "r1b" / "summary_r1b.json")
    print("NE44", json.dumps({k: v for k, v in ne.items()}, default=str)[:800])
    vc = {}
    for p, x in S["periods"].items():
        vc[(x["r1"], x["r1b"])] = vc.get((x["r1"], x["r1b"]), 0) + 1
    print("period verdict transitions", vc)
    figure(S)
    if not a.no_estimates:
        estimates(PB)


def figure(S):
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
    cols = {"N_tgt": "#2b6cb0", "H_any": "#c05621", "A_men": "#718096"}
    labs = {"N_tgt": "nudge", "H_any": "human", "A_men": "@-mention"}
    for c in ("N_tgt", "H_any", "A_men"):
        for fam, mk, key in (("r1", "o", "classes_r1"), ("r1b", "s", "classes_r1b"), ("v4", "^", "classes_v4")):
            v = S[key][c]
            if v.get("K") is None:
                continue
            ax[0].plot([v["K"]], [v["phi_exc_mean"] or 0], mk, color=cols[c], ms=6 if fam != "r1" else 4,
                       mfc="none" if fam == "r1" else cols[c], label=f"{labs[c]} {fam}")
            if v.get("K_ci"):
                ax[0].plot(v["K_ci"], [v["phi_exc_mean"] or 0] * 2, color=cols[c], lw=0.8, alpha=0.6)
    for key, mk, lab in (("CF_b4_nocons_r1b", "D", "erasure B4 (A2)"), ("v4_CF", "v", "erasure V4")):
        v = S["erasure"].get(key, {})
        if v.get("K") is not None:
            ax[0].plot([v["K"]], [v["phi_exc_mean"] or 0], mk, color="#2f855a", ms=5, label=lab)
    ax[0].axvline(0, color="0.6", lw=0.6); ax[0].axhline(0.10, color="0.6", lw=0.6, ls=":"); ax[0].axvline(0.10, color="0.6", lw=0.6, ls=":")
    ax[0].axvline(-0.10, color="0.6", lw=0.6, ls=":")
    ax[0].set_xlabel("catalytic K (escape at fixed occupancy)"); ax[0].set_ylabel("field φ_exc")
    ax[0].set_title("(a) lever plane: round 1 (open), 1b B4 (filled), V4 (triangles)", fontsize=8)
    ax[0].legend(fontsize=5.5, frameon=False, ncol=2)
    st = S.get("steps_native", {})
    items = []
    for k, lab in (("NE43_S1_bookends_off_5x5", "S1 bookends off"), ("NE43_S2_nudger_off_5x5", "S2 nudger off"), ("NE10", "NE10 nudger on")):
        r = st.get(k, {})
        for fam in ("b4", "v4"):
            j = r.get(f"judge_{fam}", {})
            if j:
                items.append((f"{lab} {fam.upper()}", j.get("esc_idle_pct"), j.get("dpi_idle_pct")))
    y = np.arange(len(items))[::-1]
    ax[1].scatter([i[1] for i in items], y, color="#2b6cb0", label="idle/wait escape pct", s=18)
    ax[1].scatter([i[2] for i in items], y, color="#c05621", marker="s", label="Δπ idle/wait pct", s=18)
    ax[1].set_yticks(y); ax[1].set_yticklabels([i[0] for i in items], fontsize=7)
    ax[1].axvspan(25, 75, color="0.9"); ax[1].set_xlim(-3, 103)
    ax[1].set_xlabel("percentile among same-shape day-boundary placebos")
    ax[1].set_title("(b) native steps: NE43 (two steps), NE10", fontsize=8); ax[1].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fig.savefig(L.HDIR / "figures" / "summary_obs_r1b.pdf"); plt.close(fig)


def estimates(PB):
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import estimates as E
    rows = []
    for p, r in sorted(PB.items()):
        g = int(p[1:])
        for fam, block, meth in (("B4", r.get("b4", {}), "B4 minute grid, leading-@ nudges, presence-cut windows (DQ8 lever_design), matched past-only controls; day bootstrap (r1b)"),
                                 ("V4", r.get("v4") or {}, "Jev v3.1 states lumped to V4, soft 5-min transitions, same design; day bootstrap (r1b)")):
            for c in CLASSES:
                u = block.get(c)
                if not isinstance(u, dict) or "K" not in u or u.get("n_ep", 0) < 5:
                    continue
                for stat, est, ci_, se in (("catalytic_K", u["K"], u.get("K_ci"), u.get("K_boot_se")),
                                           ("field_phi_exc", u["phi_exc"], None, None),
                                           ("idle_escape_lnratio", u["esc"][2], (u.get("esc_ci") or [[None] * 4, [None] * 4])[0][2:3] + (u.get("esc_ci") or [[None] * 4, [None] * 4])[1][2:3], None),
                                           ("dpi_idle", u["dpi"][2], (u.get("dpi_ci") or [[None] * 4, [None] * 4])[0][2:3] + (u.get("dpi_ci") or [[None] * 4, [None] * 4])[1][2:3], None)):
                    rows.append(dict(period_unit=p, goal_no=g, statistic=stat + ("" if fam == "B4" else "_v4"), channel=c,
                                     estimate=float(est), ci_lo=None if not ci_ or ci_[0] is None else float(ci_[0]),
                                     ci_hi=None if not ci_ or ci_[1] is None else float(ci_[1]),
                                     ci_level=0.95 if ci_ and ci_[0] is not None else None,
                                     ci_kind="percentile" if ci_ and ci_[0] is not None else "none", se=se,
                                     n=float(u["n_ep"]), n_kind="episodes", method=meth,
                                     null="placebo pseudo-episodes from matched pools (200 draws)", role="replication",
                                     first_day=r["days"][0], last_day=r["days"][-1],
                                     status="ok" if u.get("status") == "ok" else "underpowered",
                                     source=f"data/processed/H39-catalysts-vs-fields/r1b/{p}/results.json",
                                     notes="round 1b; idle = B4 idle or V4 wait"))
    E.write_estimates(rows, hypothesis="H39")
    print("estimates written:", len(rows))


if __name__ == "__main__":
    main()
