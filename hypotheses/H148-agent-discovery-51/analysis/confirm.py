"""H148 CONFIRMATORY re-scoring on #51's reserved tail (51m, 2026-09-07 -> 09-18). FROZEN, NOT RUN.

Frozen test (written 2026-10-09, before any reserved data were read):
  For every individual discovered in round 1 (data/processed/H148-agent-discovery-51/individuals_<level>.json) with
  >= 2 atoms, build the same atom panel on the tail days (same atom definitions: atoms.parquet, own repos, top
  projects; same bins, trim, E and estimator: h148lib) and compute each member's coupling to the rest, z_tau(b | X - b),
  with 60 day-permutation draws over the tail days (round 1's blocks: 6 same-parity days).
  C1 (individuals persist): >= 2/3 of the discovered multi-atom individuals have mean member z >= 2 and min >= 1.
  C2 (agents stay individuals): >= 90% of the agents that were single-atom individuals keep colonial A above the
      within-(day, E) permutation null (p <= 0.025) on the tail.
  Verdict per prediction: holds / fails; no other statistic is read.

Guard: the confirm mode needs both flags and a reserved-data ledger entry, and it needs a commit cleaner that can read
reserved days (`memeplex.clean_commits` masks them; requested from the coordinator). Until then it refuses.

    uv run python confirm.py --dry-run
        runs the identical scoring on a non-reserved stand-in (the last 12 exploration days, 2026-08-19 -> 09-04) from
        the exploration panel; it reads no reserved row. The stand-in is a code check, not a test.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h148lib as L  # noqa: E402

TAIL = ("2026-09-07", "2026-09-18")
STANDIN_FIRST_DAY = "2026-08-19"


def subset_days(P: L.Panel, keep_days: np.ndarray) -> L.Panel:
    bins = np.flatnonzero(np.isin(P.day, keep_days))
    _, day = np.unique(P.day[bins], return_inverse=True)
    Q = L.Panel(P.S[:, bins], P.K, P.kind, P.names, P.agent_of, P.owner, day.astype(np.int64), P.valid[bins],
                P.phase[bins], P.exo[bins], P.width, dict(P.meta))
    return Q


def score(P: L.Panel, indiv: list, singles_atoms: list) -> dict:
    """Both 'halves' of the panel are scored together: the tail is one block; parity is not used."""
    P.day = P.day.copy()
    ev = L.Evaluator(P)
    # one half = all days: map every target day to half 0
    ev.tr = {0: np.arange(P.b0.size), 1: np.arange(P.b0.size)}
    _, dd = np.unique(P.tday, return_inverse=True)
    ev.dd = {0: dd, 1: dd}
    ev.cb_bins = {0: np.flatnonzero(P.valid), 1: np.flatnonzero(P.valid)}
    cp = L.Coupler(ev, 0)
    out = []
    for d in indiv:
        X = tuple(d["atoms"])
        if len(X) < 2:
            continue
        coh = []
        for b in X:
            rest = tuple(a for a in X if a != b)
            coh.append(float(cp.increments(rest, [b], 0, nnull=60)[0]["z"][0]))
        out.append({"atoms": list(X), "cohesion": coh, "holds": bool(np.mean(coh) >= 2 and min(coh) >= 1)})
    rng = np.random.default_rng(0)
    sing = [{"atom": a, **ev.single_test(a, 0, rng)} for a in singles_atoms]
    c1 = float(np.mean([o["holds"] for o in out])) if out else float("nan")
    c2 = float(np.mean([s["p"] <= L.P_SINGLE for s in sing])) if sing else float("nan")
    return {"individuals": out, "singles": sing, "C1_share": c1, "C1": None if out == [] else c1 >= 2 / 3,
            "C2_share": c2, "C2": None if not sing else c2 >= 0.9}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-reads-reserved-data", action="store_true")
    ap.add_argument("--level", default="agents")
    args = ap.parse_args()
    f = L.OUT / f"individuals_{args.level}.json"
    if not f.exists():
        raise SystemExit(f"no round-1 individuals at {f}")
    indiv = json.loads(f.read_text())["discovered"]
    res = json.loads((L.OUT / "results" / f"{args.level}_w30.json").read_text())
    singles_atoms = [r["atom"] for r in res["singles"] if r["individual"] and r["kind"] == "agent"]
    if args.confirm:
        if not args.i_understand_this_reads_reserved_data:
            raise SystemExit("refusing: --confirm needs --i-understand-this-reads-reserved-data")
        raise SystemExit("refusing: the tail panel needs a commit cleaner that can read reserved days "
                         "(memeplex.clean_commits masks them); see the card's Round 1 notes")
    if not args.dry_run:
        raise SystemExit("use --dry-run (stand-in) or --confirm with the acknowledgement flag")
    P = L.load_panel(30, with_elements=(args.level == "all"))
    import polars as pl
    bins = pl.read_parquet(L.OUT / "bins_30.parquet")
    days = np.unique(P.day[(bins["pt_date"] >= STANDIN_FIRST_DAY).to_numpy()])
    Q = subset_days(P, days)
    out = score(Q, indiv, singles_atoms)
    od = L.OUT / "confirm_dryrun"
    od.mkdir(exist_ok=True)
    (od / f"{args.level}.json").write_text(json.dumps(out, indent=1, default=float))
    print(f"dry run (stand-in {STANDIN_FIRST_DAY} -> 2026-09-04, {days.size} days): C1 share {out['C1_share']}, "
          f"C2 share {out['C2_share']} (code check only)")


if __name__ == "__main__":
    main()
