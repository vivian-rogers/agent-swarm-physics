"""Write H46 goal-period / NE READMEs.

--phase predict : creates every README with Verdict pending and the dated prediction (run before the real-data run).
--phase results : rewrites the Verdict / Result / Scorecard sections from the result JSONs, keeping the prediction
                  section verbatim.
Replication READMEs are templated on purpose (layer 1) and say so; native and NE-class READMEs are written by hand
in NATIVE / NE_TEXT below.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402

HDIR = L.ROOT / "hypotheses/H46-style-conserved-charge"
PDIR = HDIR / "goalperiod-subhypotheses"
NATIVE_G = {12, 44, 51}
ENTRY = {3: (2, "adjacent"), 4: (3, "adjacent"), 5: (4, "adjacent"), 6: (5, "adjacent"), 7: (6, "adjacent"),
         8: (7, "adjacent"), 10: (8, "skips held-out #9"), 11: (10, "adjacent"), 12: (11, "adjacent"),
         13: (12, "adjacent"), 17: (16, "adjacent"), 18: (17, "adjacent"), 19: (18, "adjacent"), 20: (19, "adjacent"),
         21: (20, "adjacent; NE28 double retirement the same day"), 23: (21, "skips held-out #22"),
         24: (23, "adjacent"), 25: (24, "adjacent"), 26: (25, "adjacent"), 27: (26, "adjacent"), 31: (30, "adjacent"),
         36: (35, "adjacent"), 37: (36, "adjacent"), 38: (37, "adjacent"), 39: (38, "adjacent"),
         40: (39, "adjacent; NE42 merge"), 41: (40, "adjacent; NE42 split"), 42: (41, "adjacent"),
         44: (42, "skips held-out #43")}
NO_ENTRY_WHY = {2: "predecessor #1 is held out", 16: "predecessors #14 and #15 are held out",
                30: "predecessors #28 and #29 are held out",
                33: "the step from #31 spans the held-out NE12 window (#32)",
                35: "the step from #33 is NE15 (held out: its pre-side #34 is a held-out period)",
                51: "the step from #44 spans the held-out NE21+NE23 window; handled by the native persona test"}


def titles() -> dict:
    t = {}
    for line in (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def period_info() -> dict:
    m = L.load_messages()
    dt_ = L.day_table(m, {"x": np.zeros((m.height, 1))})
    k = dt_.keys
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter(~pl.col("holdout"))
    info = {}
    for g in sorted(k["goal_no"].unique().to_list()):
        kk = k.filter(pl.col("goal_no") == g)
        per_agent = kk.group_by("agent").len()
        units = pu.filter(pl.col("goal_no") == g)
        info[g] = {"n_agents": int(kk["agent"].n_unique()), "n_agents_2d": int((per_agent["len"] >= 2).sum()),
                   "n_agent_days": kk.height, "first": units["first_day"].min(), "last": units["last_day"].max(),
                   "n_days": int(kk["pt_date"].n_unique()), "regime": units["regime"][0],
                   "rooms": sorted({r for rr in units["rooms"].to_list() for r in rr}),
                   "units": units["unit_id"].to_list()}
    return info


def eligible(info) -> list[int]:
    return [g for g, v in info.items() if v["n_agents_2d"] >= 3]


REPL_PRED = """*Written {stamp}, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **Entry boundary** ({entry}): type-controlled style percentile T_s ≤ 0.60 while content T_c ≥ T_s + 0.10 (content moves, style stays in the agent's day-to-day band).
- **Cross-boundary fingerprint** (train on the predecessor's last ≤ 3 days, test on this period's first ≤ 3, day-demeaned): style balanced accuracy > content's and ≥ 2× chance.
- **Within period:** style identifies agents at least as well as content in a split-half test (first half of days → second half).
- **Kolchinsky–Wolpert** (periods #30 onward): within-agent style fluctuations carry no information about next-day output (scramble-null p ≥ 0.05).
- **Verdict rule:** supported if the entry-boundary and fingerprint conditions hold; failed if T_s > 0.60 and T_s ≥ T_c − 0.10, or style accuracy ≤ 1.5× chance; otherwise mixed. No entry boundary → descriptive.
- *Counts against:* style moving at the entry boundary as much as content does."""

NATIVE = {
    "G12": {"role": "native (exploratory)", "why": """#12 is the only period where the operator **assigned adversarial positions**: ten debates in four days, teams re-drafted for every debate (DQ6 `team` labels: gov/opp), a rotating judge (DQ6 `judge`), and a new motion every debate. That gives (i) ten rapid content quenches inside one period, (ii) an assigned register change inside one agent (Claude Opus 4.1 judged six debates and argued in four), and (iii) assigned sides. If style is a state that follows the assigned role or side, it moves here.""",
            "pred": """*Written {stamp}, before running on this period (from card P11).*
- **(a) Fingerprint across debates:** train on each agent's debates 1–5, test on 6–10. Style balanced accuracy ≥ 3× chance (7 agents: chance 0.14) and above content's.
- **(b) Debate switch:** displacement between an agent's consecutive debates vs its own within-debate split halves (placebo): content T_c > T_s, with T_s ≤ 0.60.
- **(c) Assigned role (judge vs debater), agent 9:** leave-one-debate-out classification of role from content ≥ 0.8; from style ≤ 0.7. The four one-time judges: style distance of the judge window to their debater centroid inside their own leave-one-out debater band (percentile < 0.9).
- **(d) Assigned side:** within-agent side permutation on style displacement, p ≥ 0.05.
- *Counts against H46:* (c) style separates judging from debating as well as content does, or (d) side moves style."""},
    "G44": {"role": "native (exploratory)", "why": """#44 holds the **H23 distilled leader**: base Kimi K2.6 fine-tuned (LoRA r8, 30 steps) on outputs of a prompted Kimi K2.6, deployed as agent 28 on 05-28/29 (27 chat rows over all checkpoints, 16 from the final weights). The weights are the substrate. If style is substrate, the leader writes like base Kimi K2.6 (agent 25) even though its role and context (leader of #best) differ.""",
            "pred": """*Written {stamp}, before running on this period (card P12; descriptive, n = 27 messages).*
- Leader style (type-controlled, message mean) nearest centroid among agents with regime-III non-holdout data (#38–#44, leader window excluded): **Kimi K2.6 at rank 1** (rank 2 acceptable). Label-permutation null over agents.
- Leader content nearest centroid: not specifically Kimi K2.6 (H23: its plans look like the room's).
- The replication estimator (entry boundary 42 → 44, skipping held-out #43) is reported here as well.
- *Counts against:* Kimi K2.6 ranked in the bottom half by style."""},
    "G51": {"role": "native (exploratory)", "why": """#51 is the **private-role era**: each agent got an assigned role (DQ6 `role`), from task roles (forecaster, game dev) to performative ones: the **Prankster** (GPT-5, agent 10), whose role is to act on others for effect, and the **media** roles (`role_class == media`: twitterati, substacker, YouTuber). An assigned persona is the sharpest test of a conserved style: if the role reaches the register, style moves. #51 also holds **NE38** (07-29): Claude Opus 5 was reassigned from game dev to mathematician, a single-agent role switch with a long baseline on both sides.""",
            "pred": """*Written {stamp}, before running on this period (card P9, P10).*
- **Personas (P9):** incumbents with regime-III non-holdout data before #45. Block displacement of type-controlled style from their last ≤ 3 eligible days before #45 to their first ≤ 3 eligible days of #51 (07-06 → 07-08), against their own placebo block pairs with a calendar gap ≥ 21 days (#36–#44, #51 non-holdout). H46 predicts the Prankster's percentile < 0.9, the media roles within band, and no media-vs-other difference (Mann–Whitney p ≥ 0.05). Content moves for everyone (median percentile ≥ 0.7). *Falsifier:* Prankster ≥ 0.95, or media > other at p < 0.05. Prior: about 50% that the Prankster breaks it.
- **NE38 (P10):** agent 40, day-level transition 07-28 → 07-29 and 3-day blocks, against its own #51 placebo transitions: content percentile ≥ 0.9, style percentile < 0.9.
- The replication estimator inside #51 (within-period split-half fingerprint, KW information) is reported here as well; #51's internal boundaries (roster, rooms, NE43) feed the NE classes."""},
}

NE_TEXT = {
    "NE34": ("replication (exploratory)", "Goal switches (NE34): the common estimator over the 24 adjacent non-holdout goal transitions (39→40 and 40→41 go to NE42), plus 3 transitions that skip one held-out goal (sensitivity).",
             "content moves strongly (T_c ≥ 0.70); type-controlled style conserved (T_s ≤ 0.60; verdict rule in the card). Raw style may leak (T_s,raw up to 0.65), and the type control removes most of it (R2). Fingerprint: style balanced accuracy ≥ 3× chance at ≥ 80% of boundaries, retention ≥ 0.8; content retention ≤ 0.6; style > content at ≥ 2/3; Anthropic-only style accuracy above chance at ≥ 2/3. *Falsifier:* type-controlled style broken."),
    "NE42": ("replication (exploratory)", "Room events (NE42): the 05-04 merge of #best and #rest (39→40) and the 05-11 split (40→41), both goal-confounded, plus the #51 `#focus` room opening (08-05) and closing (08-24).",
             "content moves (T_c ≥ 0.65); type-controlled style conserved. A merge changes who an agent reads, so this is where accommodation (R1) would show."),
    "NE43": ("replication (exploratory)", "Nudger off (NE43, 2026-08-21, inside #51): the automated speaker falls silent (no nudges, no daily bookends). Day-level transition 08-20 → 08-21 against #51 placebo transitions.",
             "content barely moves (T_c ≤ 0.6; likely uninformative); style conserved (T_s within band)."),
    "NE32": ("replication (exploratory)", "Roster changes (class folder named after NE32): 20 within-period joins and leaves with no other step change (incl. NE29, NE32, NE33); incumbents only.",
             "incumbents' content moves little (T_c ≈ 0.55, possibly uninformative); style conserved."),
    "NE14": ("replication (exploratory)", "Scaffold steps (class folder named after NE14): NE02, NE03, NE04, NE06 (×2), NE07, NE10, NE11, NE14 (regime II→III, content in raw bge space), NE16, NE17, NE18.",
             "style conserved at the small steps. NE14 (chat now written from inside continuous computer use) is where H46 is most at risk; the hypothesis predicts conservation there too (prior: about 40% that it breaks)."),
}

NE41_PRED = """*Written {stamp}, before running on these events (card P2).*
- **Design:** consecutive eligible chat messages of one agent on one PT day (regime III, non-holdout). *Forced* pairs straddle exactly one forced consolidation (DQ1 rule: the closed segment has 41–42 records), *voluntary* pairs one voluntary consolidation, *within* pairs no reset. Each crossing pair is ranked among within pairs of the same agent, unit and time-gap bin (0.25 decades), which removes the recency confound.
- **Prediction:** content moves beyond within-context pairs (T_c in 0.53–0.65); style conserved (|T_s − ½| ≤ 0.03; turn-level margin 0.05). Voluntary consolidations shift content more than forced ones.
- *Falsifier:* T_s ≥ 0.55 with p < 0.05 (in-context self-imitation: style is partly held by the context window, R1)."""


def write(path: Path, text: str):
    path.mkdir(parents=True, exist_ok=True)
    (path / "figures").mkdir(exist_ok=True)
    (path / "README.md").write_text(text)


def phase_predict(stamp: str):
    info = period_info()
    tt = titles()
    el = eligible(info)
    for g in el:
        v = info[g]
        name = f"G{g:02d}"
        head = f"# H46 × {name}: {tt.get(g, '')} ({v['first']} → {v['last']})\n\n"
        per = (f"**Period:** regime {v['regime']} · {v['n_agents']} agents with eligible days · rooms {v['rooms']} · "
               f"{v['n_days']} days with eligible agent-days · units {', '.join(v['units'])}.\n")
        if f"G{g}" in NATIVE:
            n = NATIVE[f"G{g}"]
            txt = (head + "**Verdict:** pending\n" + f"**Role:** {n['role']}\n" + per + "\n## Why this period\n" + n["why"]
                   + "\n\n## Prediction\n" + n["pred"].format(stamp=stamp) + "\n\n## Result\n(pending)\n")
        else:
            if g in ENTRY:
                entry = f"#{ENTRY[g][0]} → #{g}, {ENTRY[g][1]}"
            else:
                entry = f"none: {NO_ENTRY_WHY.get(g, 'no eligible predecessor')}; within-period numbers only"
            txt = (head + "**Verdict:** pending\n**Role:** replication (exploratory)\n" + per
                   + "\n## Why this period\nA replication point for the common estimator (layer 1): every eligible goal "
                     "period gets the same statistics, so periods are comparable points, not independent tests.\n"
                   + "\n## Prediction\n" + REPL_PRED.format(stamp=stamp, entry=entry) + "\n\n## Result\n(pending)\n")
        write(PDIR / name, txt)
    for ne, (role, what, pred) in NE_TEXT.items():
        txt = (f"# H46 × {ne}: {what.split(':')[0]}\n\n**Verdict:** pending\n**Role:** {role}\n**Boundaries:** {what}\n"
               "\n## Why this class\nA natural-experiment class for the conservation test (exception (c): the transition "
               "is the object). Each boundary is scored against the agent's own day-to-day transitions near it.\n"
               f"\n## Prediction\n*Written {stamp}, before running on this class.*\n- {pred}\n\n## Result\n(pending)\n")
        write(PDIR / ne, txt)
    write(PDIR / "NE41", "# H46 × NE41: forced context erasures (turn level)\n\n**Verdict:** pending\n"
          "**Role:** native (exploratory)\n**Events:** regime III non-holdout consolidations (DQ1 `context_ledger_turns`).\n"
          "\n## Why this NE\nThousands of exogenously timed erasures of the context window, memory kept. If an agent's style "
          "is held in its context (self-imitation), an erasure resets it; if it is in the weights, nothing happens. "
          "Content, which lives in the context, should move.\n\n## Prediction\n" + NE41_PRED.format(stamp=stamp)
          + "\n\n## Result\n(pending)\n")
    print("eligible replication/native periods:", el)
    (L.DATA / "period_list.json").write_text(json.dumps({"eligible": el, "info": info}, indent=1, default=str))


def replace_section(text: str, name: str, body: str) -> str:
    pat = re.compile(rf"(^## {re.escape(name)}\n)(.*?)(?=^## |\Z)", re.S | re.M)
    if pat.search(text):
        return pat.sub(lambda m: m.group(1) + body.rstrip() + "\n\n", text, count=1)
    return text.rstrip() + f"\n\n## {name}\n{body.rstrip()}\n"


def set_verdict(text: str, v: str) -> str:
    return re.sub(r"^\*\*Verdict:\*\* .*$", f"**Verdict:** {v}", text, count=1, flags=re.M)


def phase_results():
    res = json.loads((L.DATA / "period_results.json").read_text())
    for folder, r in res.items():
        p = PDIR / folder / "README.md"
        if not p.exists():
            continue
        t = p.read_text()
        t = set_verdict(t, r["verdict"])
        t = replace_section(t, "Result", r["result_md"])
        if r.get("scorecard_md"):
            t = replace_section(t, "Scorecard (period-specific axes)", r["scorecard_md"])
        if r.get("notes_md"):
            t = replace_section(t, "Notes", r["notes_md"])
        p.write_text(t)
    print("updated", len(res), "READMEs")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["predict", "results"], required=True)
    a = ap.parse_args()
    if a.phase == "predict":
        phase_predict(dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC"))
    else:
        phase_results()
