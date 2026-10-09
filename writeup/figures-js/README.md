# Paper figures (D3 → vector PDF)

Figures for the papers in `writeup/papers/` drawn with D3 in headless Chrome and printed to vector PDF, set in the paper's own
fonts (Latin Modern Roman 7/8, Latin Modern Math for Greek and symbols).

```
uv run python writeup/figures-js/export/<name>.py     # data  -> data/processed/paper-figs/<name>.json (gitignored)
cd writeup/figures-js && node lib/render.mjs <name>   # draw  -> writeup/papers/thermodynamics/figs/js/<name>.pdf + build/<name>.png
node lib/render.mjs --all
node lib/render.mjs --paper superagents <name>        # output to writeup/papers/superagents/figs/js
```

Setup once: `npm install` in this folder (d3, puppeteer-core; uses the installed Google Chrome).

## Contract

- `export/<name>.py` reads processed outputs only (`data/processed/...`, never `data/raw/`), masks reserved data
  (`infra/shared/common.py: holdout_mask`) or asserts the inputs are already non-reserved, and writes one small JSON
  with `export/common.py: write()` (which also records provenance in `data/processed/paper-figs/_provenance.json`).
  Reuse the card's or the old `make.py`'s functions where possible, so the numbers stay identical.
- `figs/<name>.js` sets `window.FIG = { width, height, draw(svg, data) }` (inches). The SVG viewBox is in points
  (1/72 in): a column figure is 3.40 in = 244.8 pt wide; a page figure is 7.05 in = 507.6 pt.
- `lib/style.js` (`window.S`) holds the shared look; do not fork it in a figure. Helpers: `S.axis`, `S.panel`,
  `S.text` (mini markup: `$x$` italic, `_{..}`, `^{..}`), `S.legend`, `S.pointCI`, `S.pointCIh`, `S.halo`, colors `S.C`,
  regime colors `S.REG`, regime shapes `S.REG_SHAPE`.

## Style rules

- **Type.** Labels 7.6 pt, ticks 6.6 pt, small notes 6.2 pt, panel tags bold letter + short title. Minus signs are
  U+2212. Math variables italic via `$..$`. No text smaller than 5.8 pt.
- **Color carries meaning, the same everywhere.** Field = orange `#E69F00`; coupling / read-out = blue `#0072B2`;
  spins: talk = red `#CC3311`, not-talk = blue; nulls, placebos and chance bands = gray. Regimes I/II/III =
  green / pink / blue with square / diamond / circle markers (identity never by color alone).
- **Marks.** Thin: 0.5 pt axis rules, 0.7 pt CIs, 1.1–1.4 pt lines, points 8–12 (d3 symbol area) with a white ring.
  Recessive grid (`#ececec`) or none. No top/right axis lines. No dual y-axes.
- **Labels over legends.** Direct-label series where there are ≤ 4; put the reference line labels on the line.
  A legend only where direct labels would collide.
- **One message per panel.** Every panel answers one question; its tag says it in plain words.
- **Numbers.** Every number drawn or printed must equal the number in the paper text or caption. If a figure would
  show a different value, stop and report it.
