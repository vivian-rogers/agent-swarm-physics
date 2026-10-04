# Lab dashboard

A local, live view of the project: hypotheses and their scores, the physics-model × hypothesis matrix, the goal-period × hypothesis verdict grid, the phase diagram of fitted parameters, the measured swarm constants, running agents, the holdout ledger, shared pipelines, storage, and the lab notebook.

```
uv run python dashboard/serve.py        # then open http://127.0.0.1:8765
```

It refreshes every 6 s. It binds to 127.0.0.1 only. Click a hypothesis row, a grid cell or a holdout chip to read its card or period README in the side panel. Click an agent to read its hand-back report, or its latest message and recent tool calls while it runs. Click a model column head in the matrix to open the model card: the swarm variable, the signature, the hypotheses that use the model (by role, with outcome and credence) and the constants with that model tag.

**Phase diagram** (tab next to "models" and "goal periods"). One point per unit. X and Y are a period covariate (N agents, days, rooms, goal number) or any hypothesis × statistic × channel series (× method, when a series has more than one). The view joins X and Y on the unit label. When the labels differ (G51 and 51a), it joins on the goal number and says so above the plot. Held-out units are hidden by default. The page fetches `/api/estimates` once, when the tab opens, and again only when the parquet changes.

Links: `?view=phase&preset=2` opens a preset. `?view=phase&x=cov:goal&y=cov:n_agents&hold=1` sets the axes and the holdout toggle. `?model=09` opens a model card. `&noscroll=1` keeps the page at the top (for headless screenshots).

## Where each number comes from

| Panel | Source |
| --- | --- |
| Progress pips | Seven checks per hypothesis card: Question written; Prediction section has content; a synthetic or validation step exists (axis F scored, or an `analysis/*synth*`/`*valid*` script); share of `G<NN>/`/`NE<NN>/` folders with a verdict; share of scorecard axes scored; an `analysis/confirm*.py` exists; a confirmatory folder or `data/processed/<H>/confirm*` result exists. Percent = mean of the seven. |
| Scorecard | The card's faithfulness table (first digit 0–2 in the Score column). |
| Level | The promotion rules from `writeup/paper.tex` applied to the scorecard: descriptive needs C = 2 and D ≥ 1; supported and faithful need more, plus a holdout confirmation. |
| Goal periods / grid | `**Verdict:**` and `**Role:**` lines of each period README (same parser as `infra/overview/build_overview.py`). |
| Agents | Claude Code subagent transcripts in `~/.claude/projects/<this project>/*/subagents/`. **finished** = the transcript contains a hand-back; **running** = written in the last 15 min; **stalled** = neither. |
| Holdout ledger | `hypotheses/holdout.json`, plus every confirmatory period folder. |
| Shared pipelines | `data/processed/shared/_provenance.json` and file metadata. "Code changed" = the builder script is newer than the build. |
| Storage | `du` of the repo parts and the model caches, against the budget in `CLAUDE.md`. |
| Activity | Newest file mtime in the hypothesis folder or its `data/processed` folder. |
| Model matrix, model cards | `physics-models/README.md` (index) and the `models` field of each `summary/meta.json`. A faded cell is a guess from the card text. |
| Swarm constants | `interpretation/swarm-constants.json`. |
| Phase diagram | `data/processed/shared/per_period_estimates.parquet` and `period_units.parquet`. A whole-goal unit (G38) takes the peak N agents, the sum of days and the union of rooms over its split units. |

The dashboard reads cards, metadata, transcripts and two numeric shared tables (the phase-diagram inputs). It never opens the gated text tables, and the file viewer refuses `data/`, `.git`, `.venv` and `.env`.
