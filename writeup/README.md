# Writeup

Start here.

| File | What it is |
| --- | --- |
| **`papers/`** | **The papers**, one folder each; `papers/README.md` is the index. |
| **`papers/thermodynamics/paper.pdf`** | **Paper 1** (318 pp. with the compendium): *Towards a thermodynamics of agent swarms: (Ising model claudeslop as a scheme for swarm interpretability)*. Pages 1–8: introduction and the picture of the swarm with the monitoring table; then data and method, evidence by model, results that span models, limits; appendices A–F; Appendix G: the hypothesis compendium (every card's two-page summary). Source: `papers/thermodynamics/paper.tex` + `sections/`. |
| `papers/superagents/` | **Paper 2** (in preparation): effective superagents that run on a substrate of other agents (essay Direction 3). Scope and candidate goal periods in its `README.md`. |
| `intuition/intuition.pdf` | Summary and intuition notes for the 15 hypotheses with the highest estimated usefulness, with figures (2 pp. each). |
| `slides/theses-slides.pdf` | Beamer deck (16:9): the 15 theses with the highest estimated usefulness, one slide each (models with role and outcome, key equation, figure, result, what to do). |
| `slides/talk-slides.pdf`, `slides/talk-png/` | Talk deck (19 slides) and its 1920×1080 PNG export: system, what the system essentially is (effective model), global variables for swarm interpretability, the two lenses, method, which physics fits, 10 theses, next steps. Frames shared with the direction deck (`slides/frames/`). |
| `slides/direction-slides.pdf` | Beamer deck (16:9, 71 slides): research direction (11 slides: timeline, Q1–Q7, the two lenses with their math, method, scoring, results, which physics fits, next steps); appendix A: goal periods, hypothesis × model table, EU ranking (`slides/make_tables.py`, `figures/make_matrix_slides.py`); appendix B: 37 promising/intuitive thesis slides by theme (`slides/theses/H*.tex`, `slides/make_theme_appendix.py`). Shared style: `slides/swarmslides.sty`. |
| `hypotheses-compendium.pdf` | Superseded (2026-10-04 build): the compendium is now Appendix G of paper 1 (`papers/thermodynamics/make_compendium_tex.py`). |
| `visuals/` | 32 writeup figures (`H<NN>-*/fig.pdf`, rebuilt by each folder's `make.py`). `visuals/index.html` shows them with the animations; `visuals/compendium.pdf` collects the figures. |
| `animations/` | The 13 animations (`H<NN>-<slug>.mp4`, 27 MB, gitignored) and their poster frames (`*_poster.png`). Written by `vs.save_anim` from `visuals/H<NN>-*/make.py`. |
| `project-architecture.pdf`, `scoring-1col.pdf` | The one-column architecture and scoring figures (sources in `figures/`). |
| `credence-faithfulness.pdf` | The full credence and faithfulness scoring diagram. |
| `operator-guide/` | Operator guide (4 pp.). |
| `hypothesis-pages/` | Rubric and style rules for the summary pages (`RUBRIC.md`). |
| `round1-reflection/`, `round1b-synthesis/`, `synthesis-2026-10-04b/`, `scoring/` | Earlier syntheses and the scoring-v2 note. |
| `archive/` | Superseded drafts (the 2026-10-03 design paper). |

Build the paper: `cd writeup/papers/thermodynamics && pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper`.
Data: AI Village (AI Digest), used under its research terms; no data are in this repository.
