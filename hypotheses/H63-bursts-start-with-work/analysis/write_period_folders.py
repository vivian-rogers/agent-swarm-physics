"""Fill the H63 per-period READMEs from results/periods.parquet, summary.json and untrim_hazard.parquet."""
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / "hypotheses/H63-bursts-start-with-work/goalperiod-subhypotheses"
R = ROOT / "data/processed/H63-bursts-start-with-work/results"
d = pl.read_parquet(R / "periods.parquet").join(pl.read_parquet(R / "untrim_hazard.parquet"), on="goal_no", how="left")
s = json.loads((R / "summary.json").read_text())
f = lambda x: "n/a" if x is None or x != x else f"{x:.2f}"  # noqa: E731
for r in d.iter_rows(named=True):
    g = r["goal_no"]
    p = H / f"G{g:02d}" / "README.md"
    v = s["verdicts"][str(g)]
    tS, tL = json.loads(r["tab_S"]), json.loads(r["tab_L"])
    res = f"""*Run 2026-10-04 ~20:45 UTC (trimmed window: all-present, ≥ 30 min after each agent's first call).*

| Statistic | Value |
| --- | --- |
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | {r['n_bursts']} · {r['n_controls']} |
| bursts / controls with a state change (S) in the 60 min before the follower onset | {tS[0][0]}/{sum(tS[0])} · {tS[1][0]}/{sum(tS[1])} |
| OR_S [95%] (Haldane) · z vs S time-shift | {f(r['OR_S'])} [{f(r['OR_S_lo'])}, {f(r['OR_S_hi'])}] · {f(r.get('z_shift_OR_S'))} |
| bursts / controls with an agent chat link in the 60 min before | {tL[0][0]}/{sum(tL[0])} · {tL[1][0]}/{sum(tL[1])} (OR_L {f(r['OR_L'])}) |
| OR routine commit · OR birth | {f(r['OR_R'])} · {f(r['OR_B'])} |
| bursts with both S and a link · S first | {r['n_both']} · {r['n_S_first']} |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | {f(r.get('h_dS'))} [{f(r.get('h_dS_lo'))}, {f(r.get('h_dS_hi'))}] ({f(r.get('h_n_events'))}) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | {f(r.get('h_dL'))} [{f(r.get('h_dL_lo'))}, {f(r.get('h_dL_hi'))}] · {f(r.get('u_dL'))} |
| hazard h_S − h_R [95%] | {f(r.get('h_S_minus_R'))} [{f(r.get('h_S_minus_R_lo'))}, {f(r.get('h_S_minus_R_hi'))}] |

**Verdict: {v}.** {"Fewer than 3 herding bursts or 5 S signals: descriptive by the rule." if v == "descriptive" else "State changes precede few bursts; links precede most." }
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G{g:02d}.parquet`.
"""
    t = p.read_text()
    if "**Verdict:** pending" in t:
        t = t.replace("**Verdict:** pending", f"**Verdict:** {v}", 1)
    if "## Result\n*Pending.*" in t:
        t = t.replace("## Result\n*Pending.*", "## Result\n" + res, 1)
    elif "## Replication layer" not in t:
        t = t.rstrip() + "\n\n## Replication layer\n" + res
    p.write_text(t)
print("ok")
