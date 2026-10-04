# Lab dashboard

A local, live view of the project: hypotheses and how they're faring, the goal-period × hypothesis verdict grid, running agents, the holdout ledger, shared pipelines, storage, and the lab notebook.

```
uv run python dashboard/serve.py        # then open http://127.0.0.1:8765
```

It refreshes every 6 s. It binds to 127.0.0.1 only. Click a hypothesis row, a grid cell or a holdout chip to read its card or period README in the side panel. Click an agent to read its hand-back report, or its latest message and recent tool calls if it's still running.

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

The dashboard reads cards, metadata and transcripts only. It never opens the gated text tables, and the file viewer refuses `data/`, `.git`, `.venv` and `.env`.
