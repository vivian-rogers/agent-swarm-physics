# Visuals and animations: shared rules

For Vivian's writeup (RevTeX) and talks. One folder per hypothesis: `writeup/visuals/H<NN>-<slug>/`.

## Every folder contains
- `make.py`: builds everything from `data/processed/` (never `data/raw` text; never held-out rows). Runs with `uv run python writeup/visuals/H<NN>-<slug>/make.py`.
- `fig.pdf` + `fig.png`: **the writeup figure**, static, RevTeX single column (3.4 in) or double (7.0 in). Required even when an animation exists.
- `anim.mp4` + `anim_poster.png` (only when motion explains something a still cannot: a quench, a cascade, a split, a light cone). 8–25 s, ≤ 10 MB, 24 fps, 1280×720 or square 1080. Loops cleanly. Captions burned in as a short title plus a time counter.
- `caption.tex`: a 2–4 sentence figure caption in the house style (physicist voice, ASD-STE100 leaning, numbers with CIs, says which panel is the null). `\label{fig:H<NN>}`.
- `README.md`: one paragraph: what it shows, which data, which numbers come from which card section.

## Look
- `import vstyle as vs; vs.use()`. Okabe-Ito order only (`vs.CAT`); never generate extra hues.
- Fixed meanings across the set: **field = orange, coupling = blue, null/shuffle = gray band**, rooms by `vs.ROOM`.
- Direct labels on lines (≤ 4 series) plus a legend for ≥ 2 series; identity never by color alone (CVD).
- One y-axis per panel. Thin marks, 1.5 pt lines, recessive grid. Sequential = one hue; diverging = `RdBu_r` with neutral midpoint.
- Show the null or synthetic band whenever the claim is "beyond the null". Show the uncertainty (CI band or bars).
- Prefer intuitive schematics + real data side by side: panel (a) the physics picture (cartoon or simulation), panel (b) the measured village quantity against the model and the null.
- Text inside figures: plain, short. No agent text, no verbatim messages (data terms). Agent names are fine.

## Data rules
- Only non-holdout data (`infra/shared/common.py: holdout_mask`); never open `data/processed/holdout_labels/`.
- Visuals show aggregates, projections and fitted quantities; never message text.
- Embedding projections: use the shared instruments (both models exist; pick bge and say so).
- Simulations are fine and encouraged for the schematic panel; label them "simulation".
