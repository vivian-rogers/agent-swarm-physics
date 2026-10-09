"""H147 frozen confirmation script (written 2026-10-09, round 1; NOT RUN). Runs only with Vivian's sign-off.

Target (reserved): the #51 tail 51m (2026-09-07 -> 09-18), with H145's memeplex definitions frozen
(data/processed/H145-ideology-egregores-51/memeplexes.json, the version hashed in FROZEN below at sign-off).
Reuse disclosure: the #51 tail is also planned by H22, H98, H104, H105, H111, H114 and H145/H146/H148 (check the
holdout ledger first). #45-#50 are exposed for vocabulary claims (hypotheses/holdout.md, item 50) and are not targets.

Frozen tests (card, Round 1, after Amendments A1-A3):
  C1 (P1, A1): for each distributed memeplex (h_K < 0.5), dV_K,F = exp(b_rate) - 1 (own K share after a forced
     erasure, Poisson stratum FE, offset log own element events) minus the median of 100 frequency-matched
     pseudo-patterns. A pattern is a falsifier if dV <= -0.10 and both its agent-day bootstrap CI (B = 200) and its
     pseudo-quantile band lie below 0. P1 fails if >= 1/2 of distributed patterns are falsifiers.
  C2 (P4, A2): host relation at matched activity (own-repo commits and role alignment, bge), class by the card's
     rule with CIs; the DeepSeek-V3.2-centred pattern(s) parasitic, verification and onboarding patterns not parasitic.
No dated events fall in 51m; O2/O3 are not confirmatory.

Usage:
  uv run python hypotheses/H147-egregore-value-and-hosts-51/analysis/confirm.py --dry-run
        runs the frozen pipeline on a NON-reserved stand-in (H143 window E, 08-24 -> 09-04) into a scratch folder;
        reads no reserved row.
  H147_CONFIRM=1 uv run python .../confirm.py --run --i-understand-this-uses-the-reserved-periods
        the confirmatory run. It needs a reserved build of the scheme (not written: build it at sign-off, then
        re-freeze this file) and a holdout-ledger check.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h147lib as L  # noqa: E402
import run as R  # noqa: E402

C = L.C
STAND_IN = ("2026-08-24", "2026-09-04")
N_PSEUDO, B = 100, 200
FROZEN = {"memeplexes_sha256": None}   # filled at sign-off


def subset_skeleton(sk: L.Skeleton, lo: str, hi: str) -> L.Skeleton:
    keep = lambda df: df.filter((pl.col("pt_date") >= lo) & (pl.col("pt_date") <= hi))  # noqa: E731
    return L.Skeleton(ev=keep(sk.ev), panel=keep(sk.panel), stm=keep(sk.stm), bins=sk.bins, sev=sk.sev,
                      pdays=sk.pdays)


def frozen_tests(sk: L.Skeleton, ev: pl.DataFrame, pats: list[dict], out: Path) -> dict:
    L.set_base(sk, ev["agent"].to_numpy(), ev["t"].dt.epoch("us").to_numpy())
    store = R.Store(ev, sk)
    hp = L.HostPanel(sk)
    pool = [int(e) for e in store.e_ids]
    res = {}
    for j, p in enumerate(pats):
        K = [e for e in p["eids"] if e in store.idx]
        rng = np.random.default_rng(147_900 + j)
        pseudo = L.draw_pseudo(store.freq, store.hosts, K, N_PSEUDO, rng, pool=pool)
        w = R.wipe_block(sk, store, K, pseudo, B, seed=j)
        h = R.host_block(sk, hp, store, K, pseudo, B, seed=j)
        br = w["b_rate"]
        res[p["id"]] = {"label": p["label"], "h_K": p["h_K"], "dV": br["excess"], "boot": br["boot"], "pq": br["pq"],
                        "falsifier": bool(br["excess"] <= -0.10 and br["boot"][1] < 0 and br["pq"][1] < 0),
                        "host_class": h["A2"]["class_raw"], "host_commits": h["A2"]["est"]["commits"],
                        "host_ci": h["A2"]["ci"]["commits"]}
    dist = [r for r in res.values() if r["h_K"] is not None and r["h_K"] < R.DIST_MAX]
    nf = sum(r["falsifier"] for r in dist)
    summ = {"patterns": res, "C1": {"n_distributed": len(dist), "n_falsifiers": nf,
                                    "verdict": None if not dist else ("P1 fails" if nf >= len(dist) / 2 else "P1 holds")}}
    (out / "confirm_summary.json").write_text(json.dumps(summ, indent=1, default=float))
    return summ


def dry_run():
    out = Path(tempfile.mkdtemp(prefix="h147_confirm_dry_"))
    sk = subset_skeleton(L.load_skeleton(), *STAND_IN)
    ev, _ = R.element_events()
    ev = ev.filter((pl.col("t").dt.date().cast(pl.String) >= STAND_IN[0])
                   & (pl.col("t").dt.date().cast(pl.String) <= STAND_IN[1]))
    pats = [p for p in R.load_patterns() if p["source"] == "H145"]
    s = frozen_tests(sk, ev, pats, out)
    print(json.dumps(s["C1"], indent=1), "->", out)


def main():
    if "--dry-run" in sys.argv:
        dry_run()
        return
    if ("--run" in sys.argv and "--i-understand-this-uses-the-reserved-periods" in sys.argv
            and os.environ.get("H147_CONFIRM") == "1"):
        raise SystemExit("H147 confirm: the reserved build of the scheme is not written. Build it at sign-off, "
                         "fill FROZEN, re-freeze this file, check the holdout ledger, then run.")
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
