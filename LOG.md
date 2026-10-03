# Lab notebook

Newest entry at the top. Add an entry when you start, finish, or abandon
something, or make a decision worth remembering.

---

## 2026-10-03

- Set up the project structure: `data/raw`, `data/processed`, `infra`, `physics-models`, `hypotheses`, `literature`, `interpretation`, `writeup`. See `CLAUDE.md`.
- **Decision:** physics models get their own folder, `physics-models/`, one subfolder per model. Each hypothesis picks one model from there and owns its processing scheme (`scheme/`). Code shared by more than one hypothesis moves to `infra/`. (Briefly had models inside hypothesis folders; reversed the same day.)
- Wrote up 8 models: inverse Ising, nonequilibrium Ising (asymmetric J and non-random update order), contagion with thermo dictionary, semantic information of emergent structures, replicator dissipation, neutral cooperative dynamics, replicators in fluctuating environments, copying vs. transformation. Models 04–07 come from the papers in `literature/`; references marked † were written from memory and need verifying.
- Pulled the full AI Village export (all tables + `village-transcript.json`) into `data/raw/ai-village/`, pinned to one HF revision. See `data/raw/ai-village/_source.md`.
- **Decision:** skipped the computer-use screenshots (171 GB, 370 daily tars). Plan: OCR them later rather than store raw images. Not now.
- Started `physics-models/DEFINITIONS.md` with draft operational definitions. Biggest open questions: what counts as exposure in an interaction, and how to separate contagion from shared pretraining.
- Added 7 papers to `literature/` with notes and an index; PDFs renamed to `author-year-title`. Kolchinsky is an author on all 7. None is a contagion paper, so model 03 rests on references not yet in the folder.
- Started `hypotheses/HYPOHYPOTHESES.md` for loose ideas.
