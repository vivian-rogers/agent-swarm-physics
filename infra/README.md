# infra

Shared processing code used by more than one hypothesis.

Belongs here: loaders for raw tables, time and regime handling (a
machine-readable regime table from `data/raw/ai-village/CHANGELOG.md`), common
transforms (e.g. building interaction networks), and processing schemes that
two or more hypotheses share.

Doesn't belong here: code specific to one hypothesis. Keep it in that
hypothesis's `scheme/` or `model/` until a second hypothesis needs it.
