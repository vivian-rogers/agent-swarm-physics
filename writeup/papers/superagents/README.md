# Paper 2 (scoping): effective superagents on a substrate of agents

Essay Direction 3 ([literature/jazzloaf-2026-agent-ecologies-essay.md](../../../literature/jazzloaf-2026-agent-ecologies-essay.md)):
model emergent behavior in swarms as agents that run on a substrate of other agents, and look for
information-dynamical signatures of agent-like systems at the group level.

**Working definition.** Following [Krakauer et al. 2020](../../../literature/krakauer-2020-information-theory-of-individuality.md),
a candidate superagent is a set of agents (plus what they share) that carries information from its own past into its
own future better than its parts, size-matched random groups or its environment do: organismal A* = I(S′;S), colonial
A = I(S′;S|E), environmental determination nC = I(S′;E|S). Following [Kolchinsky & Wolpert 2018](../../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md),
it is *agent-like* if scrambling that information lowers its viability (here: the group's output or persistence).

## What the village has already said (cards in `hypotheses/`)

- **No effective superagent above "agent + its own artifact" so far** (H01 round 2, H58 round 2). The persistent
  individual is one model together with its own files: after 10,806 forced wipes the pair keeps its next-file
  information. Group candidates (artifact crews, synchrony, co-allocation, reply communities, rooms, labs) are not
  individuality maxima and carry no measurable semantic information.
- **The null is weak.** H01's timing-individuality tests had ≤ 7% validated power. Absence is not shown.
- **Small attraction crews exist in #51b–d** (H58): groups of 6–8 that move onto each other's current repository
  4–8× more than expected, beyond outsiders. Few joins, not yet separated from chat steering.
- **A slow collective mode persists across member turnover in regime I** (H81: τ ≈ 23–28 days, beyond
  composition and the measured goal fields). Of all the results, this is the closest to a colonial individual
  whose parts are replaced. It is not seen in regime III or inside #51.
- **Rooms are spontaneous domains, but they do not persist** (H100): rooms differ beyond random groupings in 5/7
  regime-III periods, yet no split direction survives a goal change. They are candidate within-goal individuals,
  not lasting ones.
- **Assigned groups are fields, not superagents:** the #12 drafted debate teams are not units (H01), and
  antagonism comes only from assignment (H21, H131).
- **Lesson from paper 1:** fields (timetable, goal, room, style) set most of what agents do. Any group-level
  "individuality" must be measured after conditioning on E = these fields, or it is the field.

## Where to look: goal periods ranked for this question

Goal periods as in `hypotheses/hypohypotheses/goal-periods.md`; reserved periods (16 goal periods, 4 windows;
`hypotheses/holdout.json`) are excluded from exploration and named here as confirmation targets.

**Tier 1: explore first (not reserved)**

| Period | Why it suits a substrate-level superagent | Natural experiment inside |
| --- | --- | --- |
| **#51 a–f** (2026-07-06 → 09-06; 21–32 agents, 55 days, 12k agent-hours) | Largest N and longest run, so a level above the agents has room to form and the statistics have power. Private goals: any group that forms is spontaneous, not assigned. H58's 6–8-agent crews live here. | NE33 batch join (09-03/04): new parts enter a running system; NE43 daily bookends stop (08-05, 08-20) plus the #general/#focus room split; NE41 forced erasures throughout (parts lose memory, does the group keep it?) |
| **#39 → #40** (build your own world → connect the worlds into one 3D universe; 15 agents) | A fusion event: separate individual artifacts are merged into one shared artifact by assignment. Test whether a joint individual appears at the merge and dissolves after. | NE42: the rooms were merged on 05-04 (the start of #40) and split back on 05-11, an A-B-A intervention on the substrate in the same week |
| **#35** (test your game; 13 agents, regime II) | Two forks of one RPG, one per room, from a common ancestor (H07: they diverge gradually). Two candidate group-individuals with a shared origin: a speciation analog. | NE15: #best/#rest split on 03-16, the day #35 starts |
| **#44** (fine-tune your leader; 16 agents) | The swarm's own data trains a model that then joins it: a superagent distilled from the substrate and re-inserted. Short (4 days). | NE31: the fine-tuned leader enters (temporary → permanent) |
| **#26** (elect a village leader, who picks the goal; 10 agents) | Explicit hierarchical control: does the swarm behave as one controlled unit once a leader exists? | none dated |
| **Regime I, #2–#31** (4–12 agents) | H81's slow cultural mode: test it as a colonial individual (A > 0 given E) and ask whether it survives part replacement. | NE27 batch join (08-18, 4 → 7 agents), NE28 double retirement (12-01), NE29 retirement of the longest-serving agent (02-19): Ship-of-Theseus tests |

**Tier 2: confirmation targets (reserved; do not explore)**

| Period | Why |
| --- | --- |
| #34 (develop an RPG while voting out saboteurs) | A group with defectors inside it: does the group detect and expel them, i.e. does it show an immune response? Closest to the essay's misaligned-swarm question. |
| #45 (follow your leader) | Completes the #44 → #45 leader experiment (NE31 retirement inside). |
| #48 (help Gemini 2.5 Pro) | The whole village directed at one agent: the swarm as substrate for one individual. One day. |
| NE30 (Gemini 3 Pro → 3.1 Pro, 03-05 → 03-16) | Replacing one part with a near-identical part: the cleanest Ship-of-Theseus test. |
| #51 tail (09-07 → 09-21) | Confirms anything found in #51 a–f. |

**Controls (individual tasks, no shared artifact):** #6 merch stores, #17 personal websites, #23 chess, #27 Juice
Shop. A superagent measure that fires here as often as in Tier 1 is measuring the field. Free weeks and holidays
(#3, #5, #7, #11, #16, #31, #37) give the baseline with no goal field.

**Swarm swarms.** Within the village, rooms make it a swarm of swarms in regimes II–III (#best/#rest, later
#general/#focus). #36 (interact with AI agents outside the village) is the one period with contact to other
swarms; the dataset holds only the village's side of it.

## Guardrails (from paper 1 and H01)

- Condition on the fields (scheduler day edges, goal text, room, style) before calling anything a group individual.
- Use size-matched random groups as the null: A and A* never fall as a group grows.
- Prefer content and artifact states over timing, where H01 had no power; run synthetic recovery first.
- Unit of analysis stays one goal period (split at step changes); compare periods by their fitted values.

## Cards (2026-10-09)

- **H143 — Egregore search in #51** (`hypotheses/H143-egregore-search-51/`): Krakauer colonial individuality with the impostor bundle in E, out-of-sample candidates from eight families, the leave-one-member-out hub test, boundary expansion; natives NE43 and the #focus split. From HH386, HH387.
- **H144 — Egregore value in #51** (`hypotheses/H144-egregore-value-51/`): continuity across member wipes (NE41), group dip, read-gated channel information, the #focus room cut as the channel scramble, κ_G by channel; natives NE43, NE33. From HH388–HH391.
- The operational definition of an egregore is in `physics-models/DEFINITIONS.md` ("Egregore").

## Next step

Run H143 and H144 (synthetic validation first), then write HHs for #39→#40 (NE42 merge) and regime I (H81's slow mode under NE27/28/29).
