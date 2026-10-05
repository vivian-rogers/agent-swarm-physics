# Writeup

Start here.

| File | What it is |
| --- | --- |
| **`paper/paper.pdf`** | **The paper** (26 pp.): *Towards a thermodynamics of agent swarms: (Slopvestigating sociophysics as a scheme for swarm interpretability)*. Pages 1–5: summary, motivation and diagrams; then the ten highest-EU theses, method, results, discussion; appendices: goal periods, the full hypothesis × physics-model table, all 132 hypotheses by estimated usefulness. Source: `paper/paper.tex` + `paper/sections/`. |
| `intuition/intuition.pdf` | Summary and intuition notes for the 15 hypotheses with the highest estimated usefulness, with figures (2 pp. each). |
| `slides/theses-slides.pdf` | Beamer deck (16:9): the 15 theses with the highest estimated usefulness, one slide each (models with role and outcome, key equation, figure, result, what to do). |
| `slides/talk-slides.pdf`, `slides/talk-png/` | Talk deck (19 slides) and its 1920×1080 PNG export: system, what the system essentially is (effective model), global variables for swarm interpretability, the two lenses, method, which physics fits, 10 theses, next steps. Frames shared with the direction deck (`slides/frames/`). |
| `slides/direction-slides.pdf` | Beamer deck (16:9, 71 slides): research direction (11 slides: timeline, Q1–Q7, the two lenses with their math, method, scoring, results, which physics fits, next steps); appendix A: goal periods, hypothesis × model table, EU ranking (`slides/make_tables.py`, `figures/make_matrix_slides.py`); appendix B: 37 promising/intuitive thesis slides by theme (`slides/theses/H*.tex`, `slides/make_theme_appendix.py`). Shared style: `slides/swarmslides.sty`. |
| `hypotheses-compendium.pdf` | Two-page summary of every hypothesis, with a linked contents table (credence, EU) and the figures appendix. Rebuild: `uv run python infra/summaries/build_summaries.py --compendium-only`. |
| `visuals/` | 32 writeup figures and 13 animations (`H<NN>-*/fig.pdf`, `anim.mp4`). `visuals/index.html` plays them locally; `visuals/compendium.pdf` collects the figures. |
| `project-architecture.pdf`, `scoring-1col.pdf` | The one-column architecture and scoring figures (sources in `figures/`). |
| `credence-faithfulness.pdf` | The full credence and faithfulness scoring diagram. |
| `operator-guide/` | Operator guide (4 pp.). |
| `hypothesis-pages/` | Rubric and style rules for the summary pages (`RUBRIC.md`). |
| `round1-reflection/`, `round1b-synthesis/`, `synthesis-2026-10-04b/`, `scoring/` | Earlier syntheses and the scoring-v2 note. |
| `archive/` | Superseded drafts (the 2026-10-03 design paper). |

Build the paper: `cd writeup/paper && pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper`.
Data: AI Village (AI Digest), used under its research terms; no data are in this repository.
