"""Write the per-period cards goalperiod-subhypotheses/G<NN>/README.md.

  uv run python hypotheses/H34-idea-cascades/analysis/write_period_cards.py predict   # before the real-data run
  uv run python hypotheses/H34-idea-cascades/analysis/write_period_cards.py results   # after explore.py

`predict` writes header + "Why this period" + the dated "Prediction" (never overwritten once written).
`results` keeps everything above "## Result" and rewrites Verdict, Result, Scorecard and Notes from results/periods.json.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
GP = ROOT / "hypotheses/hypohypotheses/goal-periods.md"
DATA = ROOT / "data/processed/H34-idea-cascades"
PRIMARY = {20, 42, 51}
MODE_NAME = {"C": "shared objective", "I": "each agent its own objective", "F": "free / pick your own",
             "K": "competitive", "M": "mixed (teams)", "P": "private assigned roles", "I/K": "individual / competing pairs"}


def goal_meta() -> dict[int, dict]:
    txt = GP.read_text()
    out = {}
    for m in re.finditer(r"^\| (\d+) \| (\S+) → (\S+) \| (\S+) \| (\d+) \| (\S+) \| (\S+) \| (\S+) \| (\S+) \| ([^|]+) \|$", txt, re.M):
        g = int(m.group(1))
        out[g] = dict(start=m.group(2), end=m.group(3), d=m.group(4), N=int(m.group(5)), regime=m.group(7),
                      mode=m.group(9), top=m.group(10).strip())
    for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M):
        g = int(m.group(1))
        if g in out:
            out[g]["title"] = m.group(2).strip()
    for g in out:
        sec = re.search(rf"^### {g} · .+?\n(.*?)(?=^### |\Z)", txt, re.M | re.S)
        out[g]["setup"] = ""
        if sec:
            s = re.search(r"\*\*Setup and context:\*\* (.+)", sec.group(1))
            out[g]["setup"] = s.group(1).strip() if s else ""
    return out


def h03_n() -> dict[int, float]:
    p = ROOT / "data/processed/H03-self-excited-criticality/period_table.parquet"
    t = pl.read_parquet(p).filter(pl.col("set") == "TALK")
    return {int(r["goal_no"]): float(r["n"]) for r in t.iter_rows(named=True)}


def why(g: int, m: dict) -> str:
    if g == 20:
        return ("Card candidate (HH122; goal-periods.md ranks 03 Contagion first here). Every agent runs its own Substack in a "
                "single room (regime I), so post titles, blog names and coined phrases are natural ideas, and cross-promotion "
                "is a direct transmission channel. One room means exposure is nearly saturated: the field and contagion can "
                "only be told apart by timing (HR₁₀), not by who could see what.")
    if g == 42:
        return ("Card candidate (03 Contagion ranked first: the \"1–10 means 10\" reading spread between agents). Two rooms "
                "(#best / #rest) give a never-exposed control group for the cross-room field contrast (P5c), the cleanest "
                "contagion-vs-field design available outside the holdout.")
    if g == 51:
        return ("Card candidate and the largest sample (≈ 45 non-holdout days, 21–29 agents, 8 h/day, private roles). It has "
                "the most ideas and trees, so the tail shape (FN-GW band, τ_app) and the day-ahead forecast rule are best "
                "powered here. Side rooms (GPT-5.6 isolation 07-09/10, #focus 08-05 → 08-24) add some never-exposed agents.")
    return (f"Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). "
            f"Mode {m['mode']} ({MODE_NAME.get(m['mode'], m['mode'])}), regime {m['regime']}.")


def prediction(g: int, m: dict, n03: float | None, stamp: str) -> str:
    n03s = f"{n03:.2f}" if n03 is not None else "n/a"
    base = [
        f"*Written {stamp}, before running on this period* (after the synthetic validation and amendments A1–A5 of the "
        f"main card; no real cascade statistic had been computed for any period).",
        "",
        "| # | Prediction here | Counts against |",
        "| --- | --- | --- |",
        "| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |",
        f"| P2 | R̂ < H03 n̂_talk = {n03s}; R_c < R̂ | R̂ > n̂_talk beyond its CI |",
        "| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |",
        "| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |",
        "| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |",
    ]
    if g == 20:
        base += ["| G20-a | URL (U) and name (N) ideas spread more than numbers (D): R̂_U, R̂_N > R̂_D | R̂_D highest |",
                 "| G20-b | one room: ≥ 90% of non-seed first uses are 'exposed' (saturation), so R̂ is mostly field floor + contagion mix; R_c ≤ 0.6 R̂ | R_c ≈ R̂ |"]
    if g == 42:
        base += ["| G42-a | cross-room contrast: P(adopt \\| exposed) / P(adopt \\| never exposed) > 3 (P5c) | ratio ≤ 2 (the field) |",
                 "| G42-b | low branching (mode I, separate channels): R̂ ≤ 0.3 | R̂ > 0.5 |"]
    if g == 51:
        base += ["| G51-a | the largest tree-count period: pure s^−3/2 rejected (LR p < 0.05); τ_app ≥ 2 (⇔ R ≲ 0.5 by S1) | s^−3/2 not rejected |",
                 "| G51-b | day-ahead FN-GW forecasts cover the observed P(s ≥ 2) and P(s ≥ 3) on ≥ 80% of days with ≥ 20 trees (P7) | coverage < 70% |"]
    base += ["",
             "**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; "
             "mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then "
             "counts as not tested and the verdict rests on P5: supported → mixed at best)."]
    return "\n".join(base)


def header(g: int, m: dict, meta: dict | None) -> str:
    days = meta["n_days"] if meta else m["d"]
    N = meta["N_room"] if meta else m["N"]
    return (f"# H34 × G{g:02d}: {m.get('title', '')} ({m['start']} → {m['end']})\n\n"
            f"**Verdict:** pending\n"
            f"**Role:** exploratory\n"
            f"**Period:** regime {m['regime']} · mode {m['mode']} · {m['N']} agents at start (median room size {N}) · "
            f"{days} non-holdout days. {('Setup: ' + m['setup']) if m.get('setup') else ''}\n")


def write_predict():
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    gm = goal_meta()
    n03 = h03_n()
    sys.path.insert(0, str(HYP / "scheme"))
    periods = [5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39,
               40, 41, 42, 44, 51]
    for g in periods:
        d = HYP / "goalperiod-subhypotheses" / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "figures" / ".gitkeep").touch()
        f = d / "README.md"
        if f.exists():
            continue
        m = gm[g]
        txt = (header(g, m, None) + "\n## Why this period\n" + why(g, m) + "\n\n## Prediction\n" +
               prediction(g, m, n03.get(g), stamp) + "\n\n## Result\n_pending_\n\n## Scorecard (period-specific axes)\n"
               "_pending_\n\n## Notes\n")
        f.write_text(txt)
    print(f"wrote prediction cards for {len(periods)} periods at {stamp}")


def fmt(x, nd=2):
    if x is None:
        return "–"
    try:
        if x != x:
            return "–"
        if x == float("inf"):
            return "∞"
    except TypeError:
        return str(x)
    return f"{x:.{nd}f}"


def write_results():
    res = json.loads((DATA / "results/periods.json").read_text())
    for gs, r in res.items():
        g = int(gs)
        f = HYP / "goalperiod-subhypotheses" / f"G{g:02d}" / "README.md"
        txt = f.read_text()
        top = txt.split("\n## Result")[0]
        top = re.sub(r"\*\*Verdict:\*\* \S+", f"**Verdict:** {r['verdict']}", top)
        top = re.sub(r"\(median room size \d+\)", f"(median room size {r['N_room']})", top)
        top = re.sub(r"· \d+ non-holdout days", f"· {r['n_days']} non-holdout days", top)
        lines = ["## Result", r.get("summary_line", ""), "",
                 "| Prediction | Observed | Null / reference | Verdict |", "| --- | --- | --- | --- |"]
        for row in r["rows"]:
            lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |")
        lines += ["", "**By idea class** (U artifact, D number, N name/coinage, W rare word):", "",
                  "| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for c in r["classes"]:
            lines.append(f"| {c['cls']} | {c['ideas']} | {c['nodes']} | {fmt(c['R'])} [{fmt(c['R_lo'])}, {fmt(c['R_hi'])}] | "
                         f"{fmt(c.get('R_c'))} | {fmt(c['p2'], 3)} | {fmt(c['p3'], 3)} | {c['smax']} |")
        lines += ["", f"Data: `data/processed/H34-idea-cascades/G{g:02d}/`. Figures: `../../figures/` (cross-period); "
                  f"numbers from `analysis/explore.py` → `results/periods.json`.", "",
                  "## Scorecard (period-specific axes)", r.get("scorecard", ""), "", "## Notes"]
        lines += [f"- {n}" for n in r.get("notes", [])]
        f.write_text(top + "\n" + "\n".join(lines) + "\n")
    print(f"wrote results into {len(res)} period cards")


if __name__ == "__main__":
    {"predict": write_predict, "results": write_results}[sys.argv[1]]()
