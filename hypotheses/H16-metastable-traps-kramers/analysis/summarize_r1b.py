"""H16 round 1b summary: round-1 vs round-1b numbers per period and the round-1b prediction tallies.

Reads data/processed/H16-metastable-traps-kramers/<period>/results.json (round 1) and r1b/<period>/results.json.
Writes r1b/summary_r1b.json.
Usage: uv run python hypotheses/H16-metastable-traps-kramers/analysis/summarize_r1b.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h16lib as L  # noqa: E402

import numpy as np  # noqa: E402

PERIODS = ["G27", "G30", "G31", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
REG = {p: ("I" if p in ("G27", "G30", "G31") else "III") for p in PERIODS}
nan = float("nan")


def g(d, *ks, default=nan):
    for k in ks:
        if not isinstance(d, dict) or k not in d or d[k] is None:
            return default
        d = d[k]
    return d


def row(r):
    a, c = r["a"], r["c"]
    return {
        "ts1r_deep_beta": g(a, "TS1r", "deep", "beta_agentFE"), "ts1r_deep_ci": g(a, "TS1r", "deep", "ci", default=[nan, nan]),
        "ts2r_beta": g(a, "TS2r", "beta_lnk_agentFE"), "ts2r_ci": g(a, "TS2r", "ci", default=[nan, nan]),
        "ts2r_wald": g(a, "TS2r", "ci_wald", default=[nan, nan]),
        "ts3_beta": g(a, "TS3", "deep", "beta_agentFE"), "ts3_ci": g(a, "TS3", "deep", "ci", default=[nan, nan]),
        "ts3_wald": g(a, "TS3", "deep", "ci_wald", default=[nan, nan]), "ts3_events": g(a, "TS3", "deep", "events"),
        "ts3_rows": r["counts"]["ts3_rows"], "ts3_verdict": g(a, "TS3", "deep", "verdict", default="n/a"),
        "ts5_beta": g(a, "TS5", "deep", "beta_agentFE"), "ts5_ci": g(a, "TS5", "deep", "ci", default=[nan, nan]),
        "ts5_wald": g(a, "TS5", "deep", "ci_wald", default=[nan, nan]), "ts5_events": g(a, "TS5", "deep", "events"),
        "ts5_spells": g(a, "TS5", "n_spells"), "ts5_verdict": g(a, "TS5", "deep", "verdict", default="n/a"),
        "ts5_dir_lnHR": g(a, "TS5", "kicks", "directed_lnHR"), "ts5_dir_se": g(a, "TS5", "kicks", "directed_se"),
        "ts6_beta": g(a, "TS6", "deep", "beta_agentFE"), "ts6_ci": g(a, "TS6", "deep", "ci", default=[nan, nan]),
        "ts6_wald": g(a, "TS6", "deep", "ci_wald", default=[nan, nan]), "ts6_events": g(a, "TS6", "deep", "events"),
        "ts6_spells": g(a, "TS6", "n_spells"), "ts6_verdict": g(a, "TS6", "deep", "verdict", default="n/a"),
        "kick_und": g(c, "TS1", "any_undirected_lnHR"), "kick_und_null95": g(c, "TS1", "null_undirected_lnHR_p95"),
        "kick_dir": g(c, "TS1", "any_directed_lnHR"), "kick_dir_se": g(c, "TS1", "any_directed_se"),
        "kick_dir_null95": g(c, "TS1", "null_directed_lnHR_p95"),
        "gate_dir1": g(c, "TS2r", "dose_directed", "lnOR", default=[nan])[0],
        "gate_dir1_se": g(c, "TS2r", "dose_directed", "se", default=[nan])[0],
        "gate_dir_events": g(c, "TS2r", "dose_directed", "events", default=[nan, nan])[1] if isinstance(g(c, "TS2r", "dose_directed", "events", default=None), list) else nan,
        "nudge15": g(c, "TS1", "nudge_slow15_lnHR"), "nudge15_se": g(c, "TS1", "nudge_slow15_se"),
        "ts3_kick_dir": g(c, "TS3", "directed_lnHR"), "ts3_kick_dir_se": g(c, "TS3", "directed_se"),
        "ts3_kick_dir_rows": g(c, "TS3", "directed_rows"),
        "kicks": r["counts"].get("kicks", {})}


def main():
    out = {"periods": {}}
    for p in PERIODS:
        f0, f1 = L.OUT / p / "results.json", L.OUT / "r1b" / p / "results.json"
        if not f1.exists():
            continue
        r0 = json.loads(f0.read_text()) if f0.exists() else None
        r1 = json.loads(f1.read_text())
        out["periods"][p] = {"regime": REG[p], "round1": row(r0) if r0 else None, "r1b": row(r1)}
    P = out["periods"]
    III = [p for p in P if REG[p] == "III"]
    t = {}
    # P-a5r: TS3r aging in the majority of periods with >= 15 deep escapes; G51 boot CI below -0.3
    pw = [p for p in P if (P[p]["r1b"]["ts3_events"] or 0) >= 15]
    ag = [p for p in pw if P[p]["r1b"]["ts3_beta"] < -0.3]
    t["P-a5r"] = {"powered": pw, "aging_point": ag, "aging_ci": [p for p in pw if P[p]["r1b"]["ts3_ci"][1] < -0.3],
                  "aging_wald": [p for p in pw if P[p]["r1b"]["ts3_wald"][1] < -0.3],
                  "G51": [P["G51"]["r1b"]["ts3_beta"], P["G51"]["r1b"]["ts3_ci"]] if "G51" in P else None}
    t["TS3_rows_change_regime3"] = {p: [P[p]["round1"]["ts3_rows"], P[p]["r1b"]["ts3_rows"]] for p in III}
    tot0 = sum(P[p]["round1"]["ts3_rows"] for p in III)
    tot1 = sum(P[p]["r1b"]["ts3_rows"] for p in III)
    t["TS3_rows_drop_regime3"] = 1 - tot1 / tot0
    # P-c6r
    pk = [p for p in P if (P[p]["r1b"]["ts3_kick_dir_rows"] or 0) >= 30]
    t["P-c6r"] = {"powered": pk, "no_break": [p for p in pk if (P[p]["r1b"]["ts3_kick_dir"] <= 0)
                                              or (P[p]["r1b"]["ts3_kick_dir"] - 1.96 * P[p]["r1b"]["ts3_kick_dir_se"] < 0)]}
    # P-a7, P-a8
    for nm, key in (("P-a7_TS5", "ts5"), ("P-a8_TS6", "ts6")):
        pw = [p for p in P if (P[p]["r1b"][f"{key}_events"] or 0) >= 15]
        t[nm] = {"powered": pw, "aging_point": [p for p in pw if P[p]["r1b"][f"{key}_beta"] < -0.3],
                 "aging_ci": [p for p in pw if P[p]["r1b"][f"{key}_ci"][1] < -0.3],
                 "memoryless_ci": [p for p in pw if P[p]["r1b"][f"{key}_ci"][0] >= -0.3 and P[p]["r1b"][f"{key}_ci"][1] <= 0.3],
                 "betas": {p: round(P[p]["r1b"][f"{key}_beta"], 3) for p in pw}}
    # P-c3r: gate OR >= 1.5 with CI excluding 1 (Wald)
    gp = [p for p in III if np.isfinite(P[p]["r1b"]["gate_dir1"])]
    t["P-c3r"] = {"tested": gp, "pass": [p for p in gp if np.exp(P[p]["r1b"]["gate_dir1"]) >= 1.5
                                         and P[p]["r1b"]["gate_dir1"] - 1.96 * P[p]["r1b"]["gate_dir1_se"] > 0],
                  "OR": {p: round(float(np.exp(P[p]["r1b"]["gate_dir1"])), 2) for p in gp},
                  "OR_round1": {p: round(float(np.exp(P[p]["round1"]["gate_dir1"])), 2) for p in gp if P[p]["round1"]}}
    t["P-c2r"] = {"above_null95": [p for p in III if P[p]["r1b"]["kick_und"] > P[p]["r1b"]["kick_und_null95"]]}
    t["P-c5r"] = {p: [P[p]["r1b"]["nudge15"], P[p]["r1b"]["nudge15_se"]] for p in III if np.isfinite(P[p]["r1b"]["nudge15"])}
    t["directed_TS1"] = {p: [round(P[p]["r1b"]["kick_dir"], 3), round(P[p]["r1b"]["kick_dir_null95"], 3),
                             round(P[p]["round1"]["kick_dir"], 3)] for p in III}
    out["tallies"] = t
    (L.OUT / "r1b" / "summary_r1b.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(t, indent=1, default=float))


if __name__ == "__main__":
    main()
