"""Write H12 G<NN>/README.md files.

  predict   write each folder's header, "Why this period" and dated "Prediction" (before running on that period).
            Never overwrites an existing Prediction section.
  results   fill the "Result" / "Scorecard" sections between <!-- RESULT --> markers from analysis outputs,
            and set the Verdict line by the Amendment-1 rule. The Prediction section is left untouched.

Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/write_period_folders.py predict|results
"""
from __future__ import annotations

import json
import re
import sys

import h12lib as L
import polars as pl

PERIODS = [23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51, 19, 11, 16, 13, 18]
CONSENSUS = {19, 31, 40}
FREE = {"I": [11, 16, 31], "III": [37]}
SHARED = {"I": [13, 18, 19, 24, 25, 26, 30], "III": [38, 40, 44]}
TWO_ROOM = {"35", "36b", "37", "38a", "38b", "38c", "39", "41", "42", "44"}
MODE_NAME = {"C": "shared objective", "I": "individual objective", "K": "competition", "F": "free", "M": "mixed",
             "I/K": "private roles (individual/competitive)"}
HELD = set(L.load_holdout()["goal_periods_held_out"])
WHY = {
    19: "Named consensus event: many puzzle-game concepts were brainstormed, then the swarm converged on one and shipped it (N = 7; enters P7–P9 only).",
    31: "Free week in which about nine agents converged on the same task (competing PRs): a consensus event without a goal field, and a free week for P9.",
    40: "Named consensus event: 15 agents coordinated a shared 3D universe in a dedicated room after the 05-04 room merge; strongest H02 collective co-activation (βJ₀ = 0.50).",
    11: "Free week, regime I (N = 7): the re-expansion reference for P9.",
    16: "Free week with operator rules, regime I (N = 7): the re-expansion reference for P9.",
    37: "The only non-holdout free period in regime III (3 days): P9's regime-III reference; first goal in regime III; two rooms.",
    13: "Shared-objective week in regime I (N = 6), one of P9's comparison weeks.",
    18: "Shared-objective weeks in regime I (N = 6), one of P9's comparison weeks.",
    51: "The private-role era (21–31 present agents, 8-h days): largest N and longest units; split at NE32, #focus and NE33.",
    38: "Longest shared-objective period in regime III, split at NE17 (outreach approval) and NE18 (history search).",
    36: "Spans the regime boundary (03-24): 36a is one regime-II day (descriptive), 36b is regime III.",
    35: "#best/#rest split (NE15) on day 1: the first two-room period.",
}


def titles():
    t = {}
    for line in (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def transitions(units: pl.DataFrame):
    """Usable kickoff transitions g-1 -> g: both sides non-holdout and present in the data, same regime on the two days."""
    cal = pl.read_parquet(L.SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    out = {}
    for g in range(2, 52):
        if g in HELD or (g - 1) in HELD:
            continue
        a = cal.filter(pl.col("goal_no") == g - 1).sort("pt_date")
        b = cal.filter(pl.col("goal_no") == g).sort("pt_date")
        if a.height == 0 or b.height == 0:
            continue
        if a["holdout"][-1] or b["holdout"][0]:
            continue
        if a["regime"][-1] != b["regime"][0]:
            continue
        out[g] = (a["pt_date"][-1], b["pt_date"][0])
    return out


def predict():
    units = pl.read_parquet(L.OUT / "units.parquet")
    tt = titles(); tr = transitions(units)
    for g in PERIODS:
        d = L.HYP / "goalperiod-subhypotheses" / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        f = d / "README.md"
        if f.exists() and "## Prediction" in f.read_text():
            print("keep existing prediction", f); continue
        us = units.filter(pl.col("goal_no") == g).sort("unit")
        reg = us["regime"].to_list(); mode = us["mode"][0]
        days = sum(us["n_days"].to_list()); d0 = us["days"].to_list()[0][0]; d1 = us["days"].to_list()[-1][-1]
        Np = us["N_present"].to_list(); Ncat = us["N_catalog"][0]
        scored = [u for u, s in zip(us["unit"], us["scored"]) if s]
        split = "" if us.height == 1 else "Splits: " + ", ".join(f"{u} ({len(dd)} d, {r})" for u, dd, r in zip(us["unit"], us["days"], us["regime"])) + " (H01 step changes)."
        rooms = ", ".join(f"{u}: {n}" for u, n in zip(us["unit"], us["n_rooms3"]))
        lines = [f"# H12 × G{g:02d}: {tt.get(g, '')} ({d0} → {d1})", "",
                 "**Verdict:** pending", "**Role:** exploratory (round 1, non-holdout)",
                 f"**Period:** regime {'/'.join(sorted(set(reg)))} · mode {mode} ({MODE_NAME.get(mode, mode)}) · N = {Ncat} at start "
                 f"(present: {', '.join(map(str, Np))}) · rooms holding ≥ 3 present agents: {rooms} · {days} non-holdout days. {split}", "",
                 "## Why this period",
                 WHY.get(g, f"Non-holdout period with N ≥ 10 ({MODE_NAME.get(mode, mode)}); scored for P1–P4 and the per-period dimensionality checks."), "",
                 "## Prediction", "*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).", ""]
        if scored:
            lines += [f"- **P1 / P1′ (activity modes):** in {', '.join(scored)}: k_cd ∈ {{1, 2, 3}}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.",
                      "- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation)."
                      + (" Expect λ₁/edge above the regime-I median (regime III)." if "III" in reg else ""),
                      "- **P3 (talk):** k_cd(talk) ≤ k_cd(activity)." + (f" Two-room unit(s) {', '.join(u for u in scored if u in TWO_ROOM)}: a signal talk eigenvector separates the rooms (p < 0.05)." if any(u in TWO_ROOM for u in scored) else " Single-room: no room test."),
                      "- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1)." + (" Mode C: λ₁/edge above the mode-I/F median of the regime." if mode == "C" else ""),
                      "- **P5 (family mode):** descriptive only."]
        else:
            lines += ["- **P1–P5:** not scored (N < 10); random-matrix results are reported descriptively."]
        lines += ["- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+)" + ("" if days >= 3 else " (not applicable: < 3 days)") + "; within day 1, PR30 rises from the first to the last hour more than on other days."]
        if g in tr:
            lines += [f"- **P6 (kickoff collapse):** transition #{g - 1} → #{g} ({tr[g][0]} → {tr[g][1]}): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #{g - 1}) < 0."]
        else:
            lines += [f"- **P6:** no usable transition into #{g} (previous period held out, absent, or a regime change)."]
        if g in CONSENSUS:
            lines += ["- **P8 (consensus):** PR30 declines over days 2..D (slope < 0 with time-of-day fixed effects), and the slope is below the median slope of the regime's non-consensus units."]
        r0 = reg[-1]
        if g in FREE.get(r0, []):
            lines += [f"- **P9 (free week):** mean PRday above the median of the regime-{r0} shared-objective weeks ({', '.join('#' + str(x) for x in SHARED[r0])})."]
        elif g in SHARED.get(r0, []):
            lines += [f"- **P9 (shared week):** mean PRday below the regime-{r0} free weeks ({', '.join('#' + str(x) for x in FREE[r0])})."]
        lines += ["", "**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; "
                  "PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.",
                  "**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.", "",
                  "## Result", "<!-- RESULT -->", "(pending)", "<!-- /RESULT -->", "",
                  "## Scorecard (period-specific axes)", "<!-- SCORE -->", "(pending)", "<!-- /SCORE -->", "",
                  "## Notes", "- 2026-10-03: folder created and prediction written before running on this period."]
        f.write_text("\n".join(lines) + "\n")
        print("wrote", f)


def results():
    res = json.loads((L.OUT / "period_results.json").read_text())
    for g in PERIODS:
        f = L.HYP / "goalperiod-subhypotheses" / f"G{g:02d}" / "README.md"
        r = res.get(str(g))
        if r is None or not f.exists():
            continue
        txt = f.read_text()
        txt = re.sub(r"^\*\*Verdict:\*\*.*$", f"**Verdict:** {r['verdict']}", txt, count=1, flags=re.M)
        txt = re.sub(r"<!-- RESULT -->.*?<!-- /RESULT -->", "<!-- RESULT -->\n" + r["result_md"] + "\n<!-- /RESULT -->", txt, flags=re.S)
        txt = re.sub(r"<!-- SCORE -->.*?<!-- /SCORE -->", "<!-- SCORE -->\n" + r["score_md"] + "\n<!-- /SCORE -->", txt, flags=re.S)
        if "results filled" not in txt:
            txt = txt.rstrip() + "\n- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.\n"
        f.write_text(txt)
        print("results ->", f, r["verdict"])


if __name__ == "__main__":
    {"predict": predict, "results": results}[sys.argv[1]]()
