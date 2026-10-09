# Papers

One folder per paper. Each paper has its own `paper.tex`, `sections/`, `refs.bib` and `figs/`; shared tools stay in
`writeup/` (D3 figures: `writeup/figures-js/`, render with `--paper <folder>`; matplotlib card figures:
`writeup/visuals/`; tables: `writeup/figures/`). Hypothesis cards are shared by all papers (`hypotheses/`,
numbered append-only); a paper cites the cards it uses.

The four research directions are from the project essay
([literature/jazzloaf-2026-agent-ecologies-essay.md](../../literature/jazzloaf-2026-agent-ecologies-essay.md)).

| Folder | Paper | Essay direction | Status |
| --- | --- | --- | --- |
| [`thermodynamics/`](thermodynamics/) | *Towards a thermodynamics of agent swarms: (Ising model claudeslop as a scheme for swarm interpretability)* | 2: statistical mechanics of swarms for safety and interpretability | complete draft, 318 pp. with the compendium; public on `dev` |
| [`superagents/`](superagents/) | Effective superagents on a substrate of agents (working title) | 3: superagents in agent swarms and swarm swarms | scoping |

Build a paper: `cd writeup/papers/<folder> && pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper`.
