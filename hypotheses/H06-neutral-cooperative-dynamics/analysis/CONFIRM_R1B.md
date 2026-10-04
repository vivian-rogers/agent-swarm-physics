# H06 confirm re-freeze on round-1b inputs (batch D, 2026-10-04)
Script: `confirm_r1b.py`, target #22. `confirm_holdout.py` is unchanged. Written before any #22 data was read. **Not run.**
## What changed vs `confirm_holdout.py`
- **Intention clusters.**
  - Old: round 1's own bge whitening.
  - New: DQ5 gte-modernbert `style_resid_period` vectors (`gte_sr`, the round-1b primary), plus bge-small `style_resid_period` (`bge_sr_km24`) as the second model.
  - The shared file holds only the regime-fallback style fit for #22, so the script refits the style regression on #22's own intent statements (`style_resid.fit_style` / `apply_style`).
- **Artifact labels.** Old: H11's nondeterministic files. New: shared deterministic `project_states` (w 30, sources all).
- **New label set:** DQ4 work ledger (agent work commits, automated streams excluded).
- **New copying-channel test:** ledger read vs posted-unread vs not mentioned (`context_ledger_items` × `call_windows`; round-1b R1b-4).
- **Predictions:**
  - **C1, C2 and C4: rules unchanged,** on `gte_sr` km24.
  - **C2-r1b:** C2 must hold in both models. Reason: round 1b found fragmentation and model inadequacy robust to the model and to style removal.
  - **C3-r1b (secondary):** β̂ must hold in both models, else "embedding-dependent". Reason: β̂ changed sign with the model in round 1b.
  - **New C5-r1b (secondary):** if work labels are testable, NCD is not adequate and singletons ≥ 0.6 (round-1b R1b-3).
  - **New C6-r1b (secondary):** OR(read vs posted-unread) > 1.5 with lower bound > 1. Inconclusive with < 5 switches per class. Round 1b pooled: 8.6.
- **Inputs that do not apply:** activity bins, outages, talk spins, the DQ8 trim and the leading-@ target (not H06 inputs).
- **New guards:** `holdout_ledger.check()` and a commit check (the original had neither).
## Holdout reuse collisions (ledger L028)
- **#22: allowed.** No prior run.
- **Disclosure needed for 10 planned users:** H10, H11, H12, H20, H25, H28, H32, H33, H34, H36.
  - H11 (project labels) and H28 share the artifact-label input.
  - H27 also targets #22 with onsets on the same `project_states`.
  - Whoever runs second must disclose. These use different statistics.
## Dry run (stand-ins #11, #16; `data/processed/H06-neutral-cooperative-dynamics/confirm_r1b_dryrun/`)
- **Executes** in about 7 min (2 processes).
- **Builder check:** the rebuilt labels are identical to the round-1b labels (6 clusterings, `bge_sr_km24`, art and work: 100%).
- **Style refit check:** equals the shared vectors (cos ≥ 0.9999998).
- **Reproduction:** G11 gives LLR_NH +0.98 / LLR_NC −1.10, exactly the round-1b numbers.
- **Both stand-ins:**
  - C1 not confirmed. C2-r1b confirmed in both models. C4 true.
  - C3-r1b: not confirmed (#11) and embedding-dependent (#16).
  - C5-r1b n/a: work labels are not testable in regime I.
  - C6-r1b inconclusive: 0 switches in the read and unread classes.
- **Original dry run:** C1 not confirmed, C2 confirmed.
- **Power expectation:** #22 is a regime-I free week, so C5-r1b and C6-r1b will likely be n/a or inconclusive.
## Recommendation
**Adopt.** C2-r1b is the substantive test. C5-r1b and C6-r1b are secondary and probably underpowered on #22. Vivian may drop them rather than spend the target on them.
