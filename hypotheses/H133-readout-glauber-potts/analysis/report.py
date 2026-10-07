"""H133 round 1: estimates rows (infra/shared/estimates.py) and per-unit tables for the period READMEs.

Usage: uv run python hypotheses/H133-readout-glauber-potts/analysis/report.py [--write-estimates]
Prints a markdown table per goal period to data/processed/H133-readout-glauber-potts/results/period_tables.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
D = ROOT / "data/processed/H133-readout-glauber-potts"
SRC = "data/processed/H133-readout-glauber-potts/results/units.json"


def goal_of(u):
    return int("".join(ch for ch in u if ch.isdigit()))


def fmt(v, ci=None, d=2):
    if v is None:
        return "n.e."
    s = f"{v:+.{d}f}"
    if ci:
        s += f" [{ci[0]:+.{d}f}, {ci[1]:+.{d}f}]"
    return s


def rows_for(res, summ):
    out = []
    for u, r in res.items():
        g = goal_of(u)
        e = r["O4_nopt"]
        if e.get("ok"):
            out.append({"period_unit": u, "goal_no": g, "statistic": "h133_eta_switch", "channel": "background calls (A2 model)",
                        "estimate": e["eta"], "ci_lo": e["ci"][0], "ci_hi": e["ci"][1], "se": e["se"], "n": e["n"],
                        "n_kind": "calls", "ci_level": 0.95, "ci_kind": "se_t",
                        "method": "cloglog P(hop) on background calls: agent + ln(span) + ln(1+n options) + 4-h bins + previous kind; agent-cluster sandwich t(G-1)",
                        "null": "per call: eta = 0; wall clock: eta = 1", "role": "replication", "source": SRC})
        lg = r["logit"]
        for n, stat in (("nam", "h133_gamma_named"), ("un", "h133_gamma_unnamed"), ("if", "h133_gamma_inflight")):
            if not (lg["ok"] and n in lg["beta"]):
                continue
            b = r.get("boot", {}).get("ci", {}).get(n)
            lo, hi = (b[0], b[1]) if b else lg["ci"][n]
            out.append({"period_unit": u, "goal_no": g, "statistic": stat, "channel": "per-call conditional logit",
                        "estimate": lg["beta"][n], "ci_lo": lo, "ci_hi": hi, "se": (b[2] if b else lg["se"][n]),
                        "n": lg["n_hops"], "n_kind": "hops", "ci_level": 0.95, "ci_kind": "percentile" if b else "se_t",
                        "method": "Glauber conditional logit with project x active-hour FE, agent stay FE, habit, held-before, share; "
                                  + ("agent-block bootstrap 200" if b else "agent-cluster sandwich t(G-1)"),
                        "null": "gamma = 0 (N1 within-project-hour permutation)", "role": "replication", "source": SRC,
                        "status": "descriptive (Amendment A1: unpowered at the planted effect)"})
        if u.startswith("51") and r.get("N2_timer_nopt", {}).get("ok"):
            e = r["N2_timer_nopt"]
            out.append({"period_unit": u, "goal_no": 51, "statistic": "h133_eta_switch_timer", "channel": "timer-wake background calls (A2 model)",
                        "estimate": e["eta"], "ci_lo": e["ci"][0], "ci_hi": e["ci"][1], "se": e["se"], "n": e["n"],
                        "n_kind": "calls", "ci_level": 0.95, "ci_kind": "se_t",
                        "method": "cloglog on timer-wake background calls; agent-cluster sandwich t(G-1)",
                        "null": "per call: eta = 0; wall clock: eta = 1", "role": "native", "source": SRC})
    for key, unit, g, stat in (("N2_timer_nopt", "G51", 51, "h133_eta_switch_timer_RE"), ("N4_G31_nopt", "G31", 31, "h133_eta_switch_RE")):
        p = summ[key]
        if p["k"]:
            out.append({"period_unit": unit, "goal_no": g, "statistic": stat, "channel": "random-effects mean over units",
                        "estimate": p["mean"], "ci_lo": p["ci"][0], "ci_hi": p["ci"][1], "se": p["se"], "n": p["k"],
                        "n_kind": "units", "ci_level": 0.95, "ci_kind": "se_z",
                        "method": "DerSimonian-Laird over per-unit eta_sw (A2 model)", "null": "per call: eta = 0; wall clock: eta = 1",
                        "role": "native", "source": "data/processed/H133-readout-glauber-potts/results/summary.json"})
    return out


def tables(res):
    by = {}
    for u in sorted(res, key=lambda x: (goal_of(x), x)):
        r = res[u]
        lg = r["logit"]
        b = r.get("boot", {}).get("ci", {})
        cp = lg["chosen_pos"]
        eo = r["EO_posthoc"]
        nam = fmt(lg["beta"].get("nam"), (b["nam"][:2] if "nam" in b else lg["ci"].get("nam"))) if "nam" in lg["beta"] else f"n.e. ({cp['nam']} rows)"
        un = fmt(lg["beta"].get("un"), lg["ci"].get("un")) if "un" in lg["beta"] else f"n.e. ({cp['un']})"
        iff = fmt(lg["beta"].get("if"), lg["ci"].get("if")) if "if" in lg["beta"] else f"n.e. ({cp['if']})"
        e = r["O4_nopt"]
        ec = r["O4_card"]
        line = (f"| {u} | {lg['n_hops']} / {r['births']} | {nam} | {un} | {iff} | {r['N1']['p_one_sided']:.3f} | "
                f"{eo['nam']['O']:.0f}/{eo['nam']['E']:.1f}; {eo['un']['O']:.0f}/{eo['un']['E']:.1f}; {eo['if']['O']:.0f}/{eo['if']['E']:.1f} | "
                f"{fmt(e.get('eta'), e.get('ci'))} (card {fmt(ec.get('eta'))}) |")
        if u.startswith("51") and r.get("N2_timer_nopt", {}).get("ok"):
            t = r["N2_timer_nopt"]
            line += f" {fmt(t['eta'], t['ci'])} ({t['n']} calls) |"
        elif u.startswith("51"):
            line += " n.e. |"
        by.setdefault(goal_of(u), []).append(line)
    return by


def main():
    res = json.loads((D / "results/units.json").read_text())
    summ = json.loads((D / "results/summary.json").read_text())
    by = tables(res)
    (D / "results/period_tables.json").write_text(json.dumps(by, indent=1))
    for g, ls in by.items():
        print(g)
        print("\n".join(ls))
    if "--write-estimates" in sys.argv:
        import estimates as E
        rows = rows_for(res, summ)
        E.write_estimates(rows, hypothesis="H133")
        print(f"wrote {len(rows)} estimates rows")


if __name__ == "__main__":
    main()
