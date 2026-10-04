"""H38 goal-period folders: `predict` writes each G<NN>/README.md with its dated prediction (never overwrites a
README that already exists); `results` fills Verdict / Result / Scorecard from data/processed/H38-platform-stalls/
period_results.json and rewrites the card's "Results by goal period" table.

Usage:
  uv run python hypotheses/H38-platform-stalls/analysis/write_period_folders.py predict
  uv run python hypotheses/H38-platform-stalls/analysis/write_period_folders.py results
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

import polars as pl

sys.dont_write_bytecode = True
HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import load_goals  # noqa: E402

GP = HYP / "goalperiod-subhypotheses"
DATA = ROOT / "data/processed/H38-platform-stalls"
CATALOG = ROOT / "hypotheses/hypohypotheses/goal-periods.md"


def catalog() -> dict:
    out = {}
    for line in CATALOG.read_text().splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(\S+) → (\S+)\s*\|\s*([^|]*)\|\s*(\d+)\s*\|\s*([^|]*)\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|", line)
        if m and int(m.group(1)) not in out:
            out[int(m.group(1))] = {"N": int(m.group(5)), "regime": m.group(7), "by": m.group(8), "mode": m.group(9)}
    return out


def nonholdout_periods() -> pl.DataFrame:
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet").filter(~pl.col("holdout") & (pl.col("goal_no") > 0))
    return (cal.group_by("goal_no").agg(pl.len().alias("days"), pl.col("pt_date").min().alias("first"),
                                        pl.col("pt_date").max().alias("last"), pl.col("regime").cast(pl.String).first(),
                                        (pl.col("window_s") / 3600).median().alias("hours"))
            .sort("goal_no"))


def regime_text(reg: str, g: int) -> str:
    if g == 36:
        return ("Split at the 2026-03-24 regime boundary (36a regime II, 36b regime III); predictions apply to each side "
                "with its regime, and the pair also enters the NE14 boundary test.")
    if reg == "III":
        return ("Regime III: always-on computer use, self-scheduled PAUSE timers and CONSOLIDATE every ~40 actions, so "
                "scaffold states can synchronize (common starts, common timers).")
    return ("Regime %s: discrete sessions; WAIT is logged at the end of the gap it closes and is message-triggered "
            "(H09), so synchronized waiting is the coupled-lull rival here." % reg)


def prediction(g: int, reg: str, mode: str, days: int, hours: float) -> str:
    big = "regime III" if reg == "III" else f"regime {reg}"
    cause = "`timer_pause`" if reg == "III" else "`edge` or `wait`"
    js = "0.10–0.40" if reg == "III" else "0.05–0.30"
    lines = [
        f"- **P1.** JS share in {js} ({big}), above the per-block independent expectation.",
        f"- **P2.** Explained share of JS minutes ≥ 0.5 and above its N1-surrogate level; largest primary cause {cause}; "
        "`infra_error` < 10% of JS minutes; village-off minutes, if any, ≥ 80% `scheduled`.",
        "- **P3.** If there are ≥ 20 infra-burst minutes: odds ratio of JS given a burst > 1.",
        "- **P4.** If raw g_eq active is significant (z > 2 vs N1): f_infra ≥ 0.5 (dropping explained JS minutes removes at "
        "least half of the excess) and f_lull ≥ f_infra.",
        "- **P7.** If the raw excess is ≥ 0.05: the O6 two-state formula predicts g_raw − g_stall within a factor of 2.",
        "- **Per-period verdict rule** (fixed now): **supported** if (i) explained share ≥ 0.5 and above its surrogate "
        "level and (ii) f_infra ≥ 0.5 where raw g is significant; **failed** if the explained share is at or below its "
        "surrogate level, or raw g is significant with f_infra < 0.25; **mixed** otherwise. If raw g is not significant, "
        "(ii) is not scored and the verdict rests on (i).",
        "- Against it: joint silences no more scaffold-marked than chance, or a significant raw gain that survives stall "
        "removal nearly intact.",
    ]
    if g == 51:
        lines.insert(0, "- 8-hour days and the largest roster (private roles): more agents make K ≤ 1 rarer, so JS share "
                        "near the bottom of the range; H16 saw village-off gaps on 6 days here, predicted `scheduled`.")
    if days <= 2:
        lines.insert(0, f"- Only {days} non-holdout day(s): N1 surrogates and z are weak; read as descriptive.")
    return "\n".join(lines)


def predict():
    cat = catalog()
    goals = {g["goal_no"]: g for g in load_goals()}
    per = nonholdout_periods()
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    made = 0
    for r in per.iter_rows(named=True):
        g = r["goal_no"]
        d = GP / f"G{g:02d}"
        f = d / "README.md"
        if f.exists():
            continue
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "figures" / ".gitkeep").touch()
        c = cat.get(g, {})
        title = goals[g]["goal"].splitlines()[0][:110] if g in goals else f"goal {g}"
        title = title.replace("|", "/")
        reg = r["regime"]
        f.write_text(
            f"# H38 × G{g:02d}: {title} ({r['first']} → {r['last']})\n\n"
            "**Verdict:** pending\n"
            "**Role:** exploratory (round 1, non-holdout)\n"
            f"**Period:** regime {reg} · mode {c.get('mode', '?')} · {c.get('N', '?')} agents (catalog) · "
            f"{r['days']} non-holdout days · {r['hours']:.1f} h/day (empirical median window)."
            + (" Splits inside the period: 2026-03-24 (regime II → III)." if g == 36 else "") + "\n\n"
            "## Why this period\n"
            f"One point in H38's period-by-period decomposition of joint silences and of the equal-time gain. "
            f"{regime_text(reg, g)}\n\n"
            "## Prediction\n"
            f"*Written {now}, before running H38 on this period.*\n"
            f"{prediction(g, reg, c.get('mode', '?'), r['days'], r['hours'])}\n\n"
            "## Result\n(pending)\n\n"
            "## Scorecard (period-specific axes)\n(pending)\n\n"
            "## Notes\n"
            f"- {now[:10]}: folder created with the prediction, before the run.\n")
        made += 1
    print(f"created {made} period folders")


# ------------------------------------------------------------------------------------------------ results
def fmt(x, nd=2):
    if x is None:
        return "–"
    if isinstance(x, float):
        if x != x:
            return "–"
        return f"{x:.{nd}f}"
    return str(x)


def results():
    R = json.loads((DATA / "period_results.json").read_text())
    rows = []
    for key in sorted(R):
        r = R[key]
        g = int(key[1:3])
        f = GP / key / "README.md"
        if not f.exists():
            continue
        txt = f.read_text()
        verdict = r["verdict"]
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict}", txt, count=1)
        res = r["result_md"]
        sc = r["scorecard_md"]
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + res + "\n\n## Scorecard", txt, flags=re.S)
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" + sc
                     + "\n\n## Notes", txt, flags=re.S)
        for note in r.get("notes", []):
            if note not in txt:
                txt = txt.rstrip("\n") + "\n" + note + "\n"
        f.write_text(txt)
        rows.append(f"| [{key}](goalperiod-subhypotheses/{key}/README.md) | exploratory | {verdict} | {r['key_numbers']} |")
    ne = GP / "NE14" / "README.md"
    nj = DATA / "NE14" / "result.json"
    if ne.exists() and nj.exists():
        v = re.search(r"\*\*Verdict:\*\* (\S+)", ne.read_text()).group(1)
        n = json.loads(nj.read_text())["delta"]
        rows.append(f"| [NE14](goalperiod-subhypotheses/NE14/README.md) | exploratory (boundary) | {v} | "
                    f"Δ excess gain II → III: raw {n['raw']['dE']:+.3f} [{n['raw']['lo']:+.3f}, {n['raw']['hi']:+.3f}]; "
                    f"stall {n['stall']['dE']:+.3f}; edge-conditioned {n['mask_edge']['dE']:+.3f}; scaffold-conditioned {n['mask_scaffold']['dE']:+.3f} |")
    card = HYP / "README.md"
    t = card.read_text()
    table = "| Period | Role | Verdict | Key numbers |\n| --- | --- | --- | --- |\n" + "\n".join(rows)
    t = re.sub(r"## Results by goal period\n.*?\n## Results\n", "## Results by goal period\n" + table + "\n\n## Results\n", t,
               flags=re.S)
    card.write_text(t)
    print(f"filled {len(rows)} period folders")


if __name__ == "__main__":
    {"predict": predict, "results": results}[sys.argv[1]]()
