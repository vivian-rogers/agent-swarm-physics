"""Append (or refresh) a dated Round 2 block in each regime-III period README and NE41, from r2/results.json.

    uv run python hypotheses/H15-semantic-information-scrambles/analysis/r2_period_folders.py
Idempotent: the block between the round-2 markers is replaced. A `**Verdict (r2):**` line is added after the 1b line.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as L  # noqa: E402

GP = L.ROOT / "hypotheses/H15-semantic-information-scrambles/goalperiod-subhypotheses"
B0, B1 = "<!-- r2 begin -->", "<!-- r2 end -->"


def f(d, k="RR", lo="lo_sw", hi="hi_sw", nd=2):
    if not isinstance(d, dict) or d.get(k) is None or d[k] != d[k]:
        return "n.e."
    return f"{d[k]:.{nd}f} [{d[lo]:.{nd}f}, {d[hi]:.{nd}f}]"


def put(path: Path, block: str, verdict: str):
    s = path.read_text()
    s = re.sub(re.escape(B0) + r".*?" + re.escape(B1) + r"\n?", "", s, flags=re.S)
    s = re.sub(r"\*\*Verdict \(r2\):\*\*.*\n", "", s)
    lines = s.split("\n")
    idx = next((i for i, x in enumerate(lines) if x.startswith("**Verdict (1b):**")), None)
    if idx is None:
        idx = next(i for i, x in enumerate(lines) if x.startswith("**Role:**"))
    lines.insert(idx + 1, f"**Verdict (r2):** {verdict}")
    s = "\n".join(lines).rstrip("\n") + "\n\n" + B0 + "\n" + block.rstrip("\n") + "\n" + B1 + "\n"
    path.write_text(s)


def main():
    r = json.loads((L.DATA / "results.json").read_text())
    for p in L.PERIODS:
        folder = GP / L.FOLDER.get(p, p)
        a = r["R1a"]["per"][p]
        t1 = r["R1b"]["per"].get(p, {})
        r2 = r["R2"]["per"].get(p, {})
        r3 = r["R3"]["per"].get(p)
        lines = [f"## Round 2 (2026-10-05; replication; predictions in the card's \"Round 2\" section, written before the run)",
                 f"Forced erasures {a['n_F']}, pseudo-erasures {a['n_P']} (≥ 10 window calls). Decisions are pooled "
                 "(DerSimonian–Laird over periods and the NE41 pooled fit); these are this period's contributions.",
                 "",
                 "| Statistic | This period | Pooled |",
                 "| --- | --- | --- |",
                 f"| R1a read-or-search share, calls 1–5, F − P | {a['diff']:+.3f} [{a['lo']:+.3f}, {a['hi']:+.3f}] | "
                 f"{r['R1a']['pooled_diff']['est']:+.3f} [{r['R1a']['pooled_diff']['lo']:+.3f}, {r['R1a']['pooled_diff']['hi']:+.3f}] |",
                 f"| R1a F events touching a pre-window file or A⁻ in calls 1–5 | {a['touch_any5_F']:.2f} | "
                 f"{r['R1a']['touch_any5_F']:.2f} (P {r['R1a']['touch_any5_P']:.2f}) |",
                 f"| R1b trail T2 × F (RR, V20) | {f(t1.get('T2xF'))} | {f(r['R1b']['NE41']['T2xF'], lo='lo_boot', hi='hi_boot')} |",
                 f"| R2 re-open last files L × F (RR, V3) | {f(r2.get('LxF'))} | {f(r['R2']['NE41']['LxF'], lo='lo_boot', hi='hi_boot')} |",
                 f"| R2 new messages M × F | {f(r2.get('MxF'))} | {f(r['R2']['NE41']['MxF'], lo='lo_boot', hi='hi_boot')} |",
                 f"| R2 note names repo Gn × F | {f(r2.get('GnxF'))} | {f(r['R2']['NE41']['GnxF'], lo='lo_boot', hi='hi_boot')} |"]
        if r3:
            lines += [f"| R3 excess recall, window swap (E_s) | {f(r3['E_s'], 'est', 'lo', 'hi', 3)} | "
                      f"{r['R3']['pooled']['E_s']['est']:.3f} [{r['R3']['pooled']['E_s']['lo']:.3f}, {r['R3']['pooled']['E_s']['hi']:.3f}] |",
                      f"| R3 novel-term excess (novel E_s) | {f(r3['Enov_s'], 'est', 'lo', 'hi', 3)} | "
                      f"{r['R3']['pooled']['Enov_s']['est']:.3f} [{r['R3']['pooled']['Enov_s']['lo']:.3f}, {r['R3']['pooled']['Enov_s']['hi']:.3f}] |",
                      f"| R3 recall pre − post (retrospective) | {f(r3['pre_minus_post'], 'est', 'lo', 'hi', 3)} | "
                      f"{r['R3']['pooled']['pre_minus_post']['est']:+.3f} |"]
        dropped = r2.get("dropped") or []
        lines += ["", "Per-period intervals are cluster-robust sandwich (R1b, R2) or agent-day cluster bootstrap (R1a, R3). "
                  + (f"Not estimable here: {', '.join(dropped)} (< 10 events with the class in an arm). " if dropped else "")
                  + "No verbatim text is stored; terms and file objects are hashes."]
        if r3 and r3["E_s"]["n"] == 0:
            lines.append("R3 window swap not estimable here (no same-agent notes ≥ 3 days apart).")
        put(folder / "README.md", "\n".join(lines), "descriptive (round-2 decisions are pooled; numbers below)")
    # NE41 native
    R2, C, T = r["R2"]["NE41"], r["R2"]["concentration"], r["R1b"]["NE41"]
    blk = ["## Round 2 (2026-10-05; native, pooled over the non-reserved regime-III periods)",
           f"Pooled fit with agent × period × arm fixed effects, agent-day cluster bootstrap (B = 300); {R2['n']} events "
           f"({R2['n_F']} forced). Predictions: card \"Round 2\".",
           "",
           "| Statistic | Estimate | Prediction | Verdict |",
           "| --- | --- | --- | --- |",
           f"| R2 L × F (re-open last files) | {f(R2['LxF'], lo='lo_boot', hi='hi_boot')} | ≥ 1.15, CI > 1 | direction yes, size no |",
           f"| R2 M × F (new messages) | {f(R2['MxF'], lo='lo_boot', hi='hi_boot')} | ≥ 1.10, CI > 1 | supported here; across periods heterogeneous |",
           f"| R2 Gp × F (notes / search) | {f(R2['GpxF'], lo='lo_boot', hi='hi_boot')} | CI includes 1 | inconclusive (unpowered, A3) |",
           f"| R2 Gn × F (note names repo) | {f(R2['GnxF'], lo='lo_boot', hi='hi_boot')} | CI includes 1 | supported |",
           f"| R2 none of L, M, Gp (scramble by proxy) | {f(r['R2']['proxy_none'], lo='lo_boot', hi='hi_boot')} | — | descriptive |",
           f"| R2 concentration RR(U12)/RR(U35) | {C['ratio']:.2f} [{C['ratio_ci'][0]:.2f}, {C['ratio_ci'][1]:.2f}] | > 1, CI > 1 | inconclusive (A5) |",
           f"| R2 share of the dip carried by the first reads | {C['dip_share_U12']['share']:.2f} [{C['dip_share_U12']['share_ci'][0]:.2f}, {C['dip_share_U12']['share_ci'][1]:.2f}] | ≥ 0.25 | failed |",
           f"| R1b trail T1 × F | {f(T['T1xF'], lo='lo_boot', hi='hi_boot')} | between 1 and T2 | not ordered |",
           f"| R1b trail T2 × F | {f(T['T2xF'], lo='lo_boot', hi='hi_boot')} | ≥ 1.10, CI > 1 | not supported (CI reaches 0.99) |"]
    put(GP / "NE41" / "README.md", "\n".join(blk), "mixed (round 2: first reads add 10–14% but carry ~4% of the dip; trail dose not shown)")
    print("period READMEs updated")


if __name__ == "__main__":
    main()
