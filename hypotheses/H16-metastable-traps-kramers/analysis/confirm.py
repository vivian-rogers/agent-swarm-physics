"""H16 CONFIRMATORY test on the locked holdout: goal periods #32 (regime I) and #45 (regime III).

WRITTEN, NOT RUN. Running it touches held-out data. It refuses to run without BOTH flags:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` runs the identical pipeline and scoring on non-holdout stand-ins (G31 for #32, G44 for #45) to check that
the code works; it never reads holdout rows.

Pre-registered predictions: the card, section "Confirmatory predictions (C-*)", mirrored in PREDICTIONS below. The
card and this script must be committed before a real run (holdout reuse policy, hypotheses/holdout.md):
  - #45 was used by H02 (activity-timing couplings, Curie-Weiss betaJ0); #32 lies inside H05's NE12 window (room
    couplings). H16 scores only different statistics there: dwell hazards, pause gates, loop hazards, kick effects.
    The swarm block (d) is reported descriptively and NOT scored (betaJ0 and the activity distribution overlap with
    what H02/H05 computed).

Usage:
  uv run python hypotheses/H16-metastable-traps-kramers/analysis/confirm.py --dry-run
  uv run python hypotheses/H16-metastable-traps-kramers/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Outputs: data/processed/H16-metastable-traps-kramers/confirm/<target>/ (tables, results.json) and confirm_results.json
(or confirm_dryrun/ for --dry-run).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h16lib as L  # noqa: E402

import numpy as np  # noqa: E402

FLAG1, FLAG2 = "--confirm", "--i-understand-this-uses-the-locked-holdout"

# target -> (goal_no, regime, date window, stand-in for dry run)
TARGETS = {
    "G32": dict(goal=32, regime="I", date_from=None, date_to=None, standin=dict(goal=31, date_to="2026-02-20"),
                split="2026-02-25"),   # NE12 rooms + NE35 operator reset on 02-25: sensitivity split only
    "G45": dict(goal=45, regime="III", date_from=None, date_to=None, standin=dict(goal=44, date_to=None),
                split="2026-06-03"),   # NE20 (one tool call per turn, Anthropic) on 06-03: sensitivity split only
}

# Pre-registered decision rules (mirror of the card's "Confirmatory predictions"). Filled 2026-10-03 after exploratory
# round 1 and before any holdout data was read. Each rule is a function of the results dict -> (observed, pass bool|None).
def _wald(d, key="beta_agentFE"):
    lo, hi = d.get("ci_wald", [np.nan, np.nan])
    return d.get(key, np.nan), lo, hi


def rule_ts1r_aging_wald(R):
    d = _deep(R, "TS1r")
    if d is None:
        return "too few deep escapes", None
    b, lo, hi = _wald(d)
    return f"beta {b:.2f}, Wald [{lo:.2f}, {hi:.2f}], {d['events']} deep escapes", bool(b < -0.3 and hi < 0)


def rule_loop_aging_wald(R, key):
    d = _deep(R, key)
    if d is None:
        return "too few", None
    b, lo, hi = _wald(d)
    return f"beta {b:.2f}, Wald [{lo:.2f}, {hi:.2f}], {d['events']} escapes", bool(b < -0.3 and hi < 0)


def rule_gate_aging_wald(R):
    t = R["a"].get("TS2r", {})
    if not t.get("ok"):
        return "no TS2r chains", None
    b, lo, hi = _wald(t, "beta_lnk_agentFE")
    return f"TS2r beta_lnk {b:.2f}, Wald [{lo:.2f}, {hi:.2f}], {t['n_gates']} gates", bool(hi < 0)


def rule_gate_directed_r(R):
    c = R["c"].get("TS2r", {})
    if not (c.get("ok") and c.get("dose_directed")):
        return "n/a", None
    lo, se = c["dose_directed"]["lnOR"][0], c["dose_directed"]["se"][0]
    if lo is None or not np.isfinite(lo):
        return "n/a", None
    return f"TS2r lnOR(dose 1) {lo:.2f} +- {1.96 * se:.2f}", bool(lo >= np.log(1.5) and lo - 1.96 * se > 0)


def rule_undirected_above_null(R):
    c = R["c"]["TS1"]
    if not c.get("ok"):
        return "n/a", None
    u = c["any_undirected_lnHR"]
    return f"lnHR {u:.2f} (+- {1.96 * c['any_undirected_se']:.2f}); null p95 {c['null_undirected_lnHR_p95']:.2f}", bool(u > c["null_undirected_lnHR_p95"])


def rule_undirected_not_above_null(R):
    obs, ok = rule_undirected_above_null(R)
    return obs, (None if ok is None else (not ok))


def rule_dose_not_kramers(R):
    cells = []
    for key in ("TS1",):
        for grp in ("directed", "undirected"):
            dl = R["c"][key].get(f"dose_{grp}", {}) if R["c"][key].get("ok") else {}
            if dl.get("powered") and dl.get("best"):
                cells.append(dl["best"])
    c2 = R["c"].get("TS2r", {})
    if c2.get("ok") and c2.get("dose_directed", {}).get("powered"):
        cells.append(c2["dose_directed"].get("best"))
    cells = [x for x in cells if x]
    if not cells:
        return "no powered dose cell", None
    nk = sum(x != "kramers" for x in cells)
    return f"best laws {cells}", bool(nk > len(cells) / 2)


# Written 2026-10-03 after exploratory round 1 (11 non-holdout periods) and before any holdout data was read.
PREDICTIONS: dict = {
    "G45": {
        "C45-1": {"rule": rule_ts1r_aging_wald, "primary": True,
                  "statement": "TS1r deep-window escape hazard ages within agent: beta < -0.3 and Wald CI below 0"},
        "C45-2": {"rule": rule_gate_aging_wald, "primary": True,
                  "statement": "TS2r per-gate escape falls with re-pause count (agent FE, ln declared controlled): Wald CI below 0"},
        "C45-3": {"rule": rule_gate_directed_r, "primary": True,
                  "statement": "a directed kick during a pause raises gate escape odds: TS2r OR(dose 1) >= 1.5, CI excluding 1"},
        "C45-4": {"rule": rule_loop_aging_wald, "args": ("TS3",), "primary": False,
                  "statement": "TS3 error loops age: beta < -0.3 and Wald CI below 0"},
        "C45-5": {"rule": rule_dose_not_kramers, "primary": False,
                  "statement": "where powered, the dose law is additive or saturating (not exponential) in the majority of cells"},
        "C45-6": {"rule": rule_undirected_above_null, "primary": False,
                  "statement": "undirected room messages raise TS1 escape above the day-swap null p95 (reversal of P-c2, from exploration)"},
    },
    "G32": {
        "C32-1": {"rule": rule_loop_aging_wald, "args": ("TS3",), "primary": True,
                  "statement": "TS3 error loops age: beta < -0.3 and Wald CI below 0"},
        "C32-2": {"rule": rule_undirected_not_above_null, "primary": True,
                  "statement": "regime I: undirected kicks do NOT raise escape from >= 3-min silences above the day-swap null p95"},
        "C32-3": {"rule": rule_loop_aging_wald, "args": ("TS4",), "primary": False,
                  "statement": "TS4 identical-command loops age: beta < -0.3 and Wald CI below 0"},
        "C32-4": {"rule": rule_dose_not_kramers, "primary": False,
                  "statement": "where powered, the dose law is additive or saturating (not exponential)"},
    },
}


def _deep(R, key):
    d = R["a"][key].get("deep", {}) if R["a"][key].get("ok") else {}
    return d if d.get("ok") else None


def rule_ts3_aging(R):
    d = _deep(R, "TS3")
    if d is None:
        return "too few", None
    return f"beta {d['beta_agentFE']:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]", bool(d["ci"][1] < -0.3) if np.isfinite(d["ci"][1]) else None


def rule_ts4_aging(R):
    d = _deep(R, "TS4")
    if d is None:
        return "too few", None
    return f"beta {d['beta_agentFE']:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]", bool(d["beta_agentFE"] < -0.3)


def rule_ts1r_not_timer(R):
    d = _deep(R, "TS1r")
    if d is None:
        return "too few", None
    return f"beta {d['beta_agentFE']:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]", bool(d["beta_agentFE"] <= 0.3)


def rule_undirected(R, regime):
    c = R["c"]["TS1"]
    if not c.get("ok"):
        return "n/a", None
    u, s = c["any_undirected_lnHR"], c["any_undirected_se"]
    if regime == "I":
        return f"lnHR {u:.2f} +- {1.96 * s:.2f}; null p95 {c['null_undirected_lnHR_p95']:.2f}", bool(u >= np.log(1.5) and u > c["null_undirected_lnHR_p95"])
    return f"lnHR {u:.2f} +- {1.96 * s:.2f}", bool(abs(u) <= np.log(1.25) or abs(u) < 1.96 * s)


def rule_directed(R, regime):
    c = R["c"]["TS1"]
    if not c.get("ok"):
        return "n/a", None
    d, s = c["any_directed_lnHR"], c["any_directed_se"]
    thr = np.log(1.5) if regime == "I" else np.log(1.3)
    return f"lnHR {d:.2f} +- {1.96 * s:.2f}; null p95 {c['null_directed_lnHR_p95']:.2f}", bool(d >= thr and d > c["null_directed_lnHR_p95"])


def rule_gate_directed(R):
    for key in ("TS2r", "TS2"):
        c = R["c"].get(key, {})
        if c.get("ok") and c.get("dose_directed"):
            lo = c["dose_directed"]["lnOR"][0]; se = c["dose_directed"]["se"][0]
            if lo is not None and np.isfinite(lo):
                return f"{key}: lnOR(dose 1) {lo:.2f} +- {1.96 * se:.2f}", bool(lo >= np.log(1.5) and lo - 1.96 * se > 0)
    return "n/a", None


def rule_gate_aging(R):
    for key in ("TS2r", "TS2"):
        t = R["a"].get(key, {})
        if t.get("ok"):
            return f"{key}: beta_lnk {t['beta_lnk_agentFE']:.2f} [{t['ci'][0]:.2f}, {t['ci'][1]:.2f}]", bool(t["ci"][1] < 0)
    return "n/a", None


def score(R, target):
    reg = TARGETS[target]["regime"]
    out = []
    for pid, spec in PREDICTIONS.get(target, {}).items():
        obs, ok = spec["rule"](R) if spec.get("args") is None else spec["rule"](R, *spec["args"])
        if ok is not None:
            ok = bool(ok)
        out.append({"id": pid, "statement": spec["statement"], "observed": obs,
                    "verdict": "pass" if ok else ("fail" if ok is False else "n/a")})
    primary = [o for o in out if PREDICTIONS[target][o["id"]].get("primary")]
    npass = sum(o["verdict"] == "pass" for o in primary)
    nfail = sum(o["verdict"] == "fail" for o in primary)
    overall = "supported" if (nfail == 0 and npass >= 1) else ("failed" if npass == 0 and nfail >= 1 else "mixed")
    return {"rows": out, "overall": overall, "rule": "primary predictions: all scored pass -> supported; none pass -> failed; else mixed"}


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    real = FLAG1 in args and FLAG2 in args
    if not dry and not real:
        sys.exit(f"Refusing to run: this script reads the locked holdout. Use --dry-run (stand-ins) or pass both "
                 f"{FLAG1} {FLAG2} (only after the card and this script are committed).")
    if dry and real:
        sys.exit("Choose either --dry-run or the confirm flags, not both.")
    if not PREDICTIONS:
        sys.exit("PREDICTIONS is empty: write the confirmatory predictions on the card and here first.")
    from build import build_period  # noqa: E402
    from run_period import analyze  # noqa: E402
    outroot = L.OUT / ("confirm_dryrun" if dry else "confirm")
    allres = {"mode": "dry-run (non-holdout stand-ins)" if dry else "CONFIRMATORY (locked holdout)"}
    for target, spec in TARGETS.items():
        if dry:
            st = spec["standin"]
            days = L.period_days(st["goal"], allow_holdout=False, date_to=st.get("date_to"))
            L.assert_no_holdout(days)
            allow = False
        else:
            days = L.period_days(spec["goal"], allow_holdout=True, date_from=spec["date_from"], date_to=spec["date_to"])
            allow = True
        folder = outroot / target
        build_period(target + ("-standin" if dry else ""), days, folder, allow_holdout=allow)
        rng = np.random.default_rng(L.SEED + 1000 + spec["goal"])
        R = analyze(folder, spec["regime"], rng, B=200, n_null=100, fig_dir=folder / "figures", label=target + (" (dry-run stand-in)" if dry else ""))
        R["score"] = score(R, target)
        L.jdump(R, folder / "results.json")
        allres[target] = {"days": days, "score": R["score"]}
        print(target, R["score"]["overall"])
        for row in R["score"]["rows"]:
            print("  ", row["id"], row["verdict"], "|", row["observed"])
    L.jdump(allres, outroot / "confirm_results.json")


if __name__ == "__main__":
    main()
