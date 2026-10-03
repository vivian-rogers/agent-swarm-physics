# Agent swarm physics

Studying the dynamics, statistical mechanics, information theory, sociophysics
(incl. contagion/epidemic models) and thermodynamics of LLM agent swarms, using
the AI Village dataset as the primary system.

## Layout

| Path | What lives there |
| --- | --- |
| `data/raw/` | Datasets exactly as downloaded. **Never edit, never write here.** One folder per source, each with `_source.md` (where it came from, which revision, terms). |
| `data/processed/` | Derived datasets. One folder per hypothesis (`H<NN>-<slug>/`) or per shared scheme. Every folder has a `_provenance.json` (see below). Rebuildable from `data/raw/` + code, so never hand-edited. |
| `infra/` | Shared processing code used by more than one hypothesis: raw-table loaders, time/regime handling, common transforms. |
| `physics-models/` | One folder per physics model (`NN-<slug>/`): the model, its interesting behavior, how it maps onto the swarm, how to fit it, nulls, pitfalls. Simulator/theory code for the model lives there too. `physics-models/README.md` is the index. |
| `physics-models/DEFINITIONS.md` | Operational definitions of physics concepts in terms of dataset fields. **Every model and hypothesis uses these.** |
| `hypotheses/H<NN>-<slug>/` | One research direction per folder. See "Hypotheses" below. Copy `hypotheses/_template/` to start one. |
| `hypotheses/HYPOHYPOTHESES.md` | Loose, speculative ideas. No rigor required. Ideas graduate to an `H<NN>` folder once they have a model, a scheme and a prediction. |
| `literature/` | Papers (PDF) + one notes file per paper (same basename, `.md`). `literature/README.md` is the index. Don't re-extract or reprocess the PDFs; use the notes. |
| `interpretation/` | Cross-hypothesis synthesis: what the results mean together. |
| `writeup/` | Drafts for papers, posts, talks. |
| `LOG.md` | Dated lab notebook. Newest entry at the top. |

## Hypotheses

Each hypothesis folder ties together one question, one physics model (from
`physics-models/`) and one data scheme:

```
hypotheses/H<NN>-<slug>/
├── README.md     # the card: question, model, data scheme, observables, null, prediction, status
├── scheme/       # the postprocessing scheme: builds data/processed/H<NN>-<slug>/ from data/raw/
├── analysis/     # fits the model to the processed data; tests the prediction
└── figures/
```

- Number hypotheses sequentially (`H01`, `H02`, …); never reuse a number. Parked or refuted ones stay, with their status updated.
- Write the prediction and the null/baseline in the card **before** running the analysis on real data.
- The card names its model by folder (e.g. `physics-models/03-contagion`). Hypothesis-specific variants of the model are described in the card; general improvements go back into the model folder.
- If a second hypothesis needs the same scheme, move that code into `infra/` and reference it from both cards rather than copying it.
- Any term used in a card that is in `physics-models/DEFINITIONS.md` must be used with that definition. If a hypothesis needs a different one, add a named variant there (e.g. "interaction (mention-based)") rather than redefining it locally.

## Provenance

Each `data/processed/<name>/` folder has a `_provenance.json`:

```json
{
  "built_by": "hypotheses/H01-slug/scheme/build.py",
  "git_commit": "<commit of the code that built it>",
  "inputs": [{"source": "ai-village", "revision": "<hf revision sha>", "tables": ["events", "chat_messages"]}],
  "params": {},
  "built_at": "<UTC timestamp>"
}
```

## Data rules

- The AI Village data is gated under research terms: no training/fine-tuning on it, no re-identification of people, cite AI Digest / AI Village, tell them about publications. `data/` is gitignored; never commit or upload it.
- Read `data/raw/ai-village/CHANGELOG.md` before any over-time analysis. Scaffolding changes (prompts, tools, roster) create regimes; see the "Regime" entry in `physics-models/DEFINITIONS.md`.
- The computer-use screenshots (~171 GB) are not downloaded. The plan is to OCR them later, but only when explicitly asked.
- Agent narration is a claim, not ground truth.

## Conventions

- Python, run via `uv`. Times are UTC unless a column says otherwise.
- Add a `LOG.md` entry when you start, finish, or abandon something, or make a decision worth remembering.
