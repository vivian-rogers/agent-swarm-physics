"""H62 confirmatory test on the locked holdout. WRITTEN 2026-10-04, FROZEN, NOT RUN on the holdout.

  uv run python hypotheses/H62-ideas-travel-reply-graph/analysis/confirm.py --dry-run
      runs the frozen pipeline on non-holdout stand-ins (safe; exploration data only)
  uv run python hypotheses/H62-ideas-travel-reply-graph/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      reads held-out chat text in memory (marker extraction only) and held-out DQ2 parents, builds the targets'
      channel tables and scores the frozen predictions. Refuses without BOTH flags. Calls holdout_ledger.check() and
      writes results/confirm_sealed.json (SHA-256 of this docstring) BEFORE touching held-out data.

Targets (locked holdout; reuse policy in hypotheses/holdout.md):
  T1  #51 tail (2026-09-07 -> 09-21), primary     T2  #15 (regime I)     T3  #28 (regime I)
Stand-ins for --dry-run: T1 = #51 days 2026-08-24 -> 09-04, T2 = #13, T3 = #25.
Reuse disclosure: the same targets are planned by H34 and H61 (unrun; same marker modality, different statistics:
H34 tree sizes and HR10, H61 first-use forecasts, H62 channel-resolved hazards). Disclose in both cards if run.

Frozen predictions (from round-1 exploration, frozen 2026-10-04 before any holdout use):
  C1 (primary) T1: reply premium Lambda = HR_rep / HR_room >= 3 with lower 95% idea-bootstrap CI > 1.
     (Round 1: G51 9.6 [8.6, 10.9]; regime-III median 2.2; 23/26 periods CI > 1.)
  C2 T1: T_rep / T_room >= 3 with lower CI > 1. (G51 10.0 [9.1, 11.0].)
  C3 T1: the tie-only guard (edges before the idea's first use; no direct replies) keeps Lambda lower CI > 1.
  C4 T2, T3: Lambda lower CI > 1 in at least one of the two (regime I: 12/15 periods CI > 1, median 1.8).
  C5 T1 (transmission, not thread field): C_rep = HR(seen reply use) / HR(unread-only reply use) at 300 s has lower
     95% Wald CI > 1 with >= 10 adoptions per cell. (Round 1: G51 1.70 [1.15, 2.53]; pooled 1.22 [0.93, 1.60].)
  Overall: the REPLY PREMIUM is confirmed if C1-C3 pass; TRANSMISSION along reply edges (HH254 proper) is confirmed
  only if C5 also passes. Each C is reported separately.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h62core as C  # noqa: E402
import h62lib as L  # noqa: E402
import idea_ledger as IL  # noqa: E402

OUT = ROOT / "data/processed/H62-ideas-travel-reply-graph"
RES = OUT / "results"
FIRST_SEEN = ROOT / "data/processed/H34-idea-cascades/markers/first_seen.parquet"


def heldout_period(base: IL.Base, g: int) -> dict:
    import idea_markers as M
    days = base.period_days(g, allow_holdout=True)
    days = [d for d, h in zip(days, IL.holdout_mask(days, [g] * len(days))) if h]
    P = IL.load_period(base, g, days=days, allow_holdout=True, with_markers=False)
    uses = M.uses_for_rows(P["rows"], allow_holdout=True)
    t_start = int(P["t"].min())
    old = pl.read_parquet(FIRST_SEEN).filter(pl.col("first_t").dt.epoch("us") < t_start)["marker"]
    uses = uses.filter(~pl.col("marker").is_in(old.implode()))
    pos_of = {int(r): i for i, r in enumerate(P["rows"])}
    P["use_pos"] = np.array([pos_of[int(m)] for m in uses["msg"].to_numpy()], dtype=np.int64)
    P["use_marker"] = uses["marker"].to_numpy().astype(np.int64)
    P["use_cls"] = uses["cls"].to_numpy().astype(np.int8)
    return P


def stats(P: dict, seed: int) -> dict:
    r = C.assemble(P)
    A = L.hr_fit(r["cells"], L.MODEL_A, B=200, seed=seed, contrasts={"Lam": ("rec_rep", "rec_room")})
    G = L.hr_fit(r["cells"], L.MODEL_G, B=200, seed=seed + 1, contrasts={"LamG": ("recg_rep", "recg_room")})
    Bm = L.hr_fit(r["cells"], L.MODEL_B, B=0, seed=seed + 2, contrasts={"C_rep": ("s_rep5", "u_rep5x")})
    T = L.transmissibility(r["events"], "chan", B=1000, seed=seed)
    return dict(Lam=A.get("Lam"), Lam_lo=A.get("Lam_lo"), Lam_hi=A.get("Lam_hi"), LamG=G.get("LamG"),
                LamG_lo=G.get("LamG_lo"), T_ratio=T.get("T_ratio"), T_lo=T.get("T_ratio_lo"), C_rep=Bm.get("C_rep"),
                C_rep_lo=Bm.get("C_rep_wlo"), C_rep_hi=Bm.get("C_rep_whi"), adopt_s=Bm.get("adopt_s_rep5", 0),
                adopt_u=Bm.get("adopt_u_rep5x", 0), n_adopt=A.get("n_adopt"))


def evaluate(Ps: dict) -> dict:
    res = {k: stats(P, seed=i) for i, (k, P) in enumerate(Ps.items())}
    t1 = res["T1"]
    c = {"C1": (t1["Lam"] or 0) >= 3 and (t1["Lam_lo"] or 0) > 1,
         "C2": (t1["T_ratio"] or 0) >= 3 and (t1["T_lo"] or 0) > 1,
         "C3": (t1["LamG_lo"] or 0) > 1,
         "C4": (res["T2"]["Lam_lo"] or 0) > 1 or (res["T3"]["Lam_lo"] or 0) > 1,
         "C5": t1["adopt_s"] >= 10 and t1["adopt_u"] >= 10 and (t1["C_rep_lo"] or 0) > 1}
    return dict(results=res, checks=c, premium_confirmed=bool(c["C1"] and c["C2"] and c["C3"]),
                transmission_confirmed=bool(c["C1"] and c["C2"] and c["C3"] and c["C5"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    if a.dry_run:
        base = IL.Base()
        d51 = [d for d in base.period_days(51) if d >= "2026-08-24"]
        Ps = {"T1": IL.load_period(base, 51, days=d51), "T2": IL.load_period(base, 13), "T3": IL.load_period(base, 25)}
        out = evaluate(Ps)
        out["mode"] = "dry-run on stand-ins (non-holdout)"
        (RES / "confirm_dryrun.json").write_text(json.dumps(out, indent=1, default=float))
        print(json.dumps(out, indent=1, default=float))
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: needs --confirm --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
    import holdout_ledger as HL
    for tgt in ("#51-tail", "G15", "G28"):
        st = HL.check("H62", tgt, modality="chat content (markers) + DQ2 reply parents")
        if not st["allowed"]:
            sys.exit(f"refusing: {tgt} already used by the same estimator family: {st['prior_runs_same_family']}")
        if st["needs_disclosure"]:
            print(f"DISCLOSE reuse of {tgt}: {len(st['prior_runs'])} prior runs, {len(st['competing_planned'])} planned")
    seal = hashlib.sha256(__doc__.encode()).hexdigest()
    (RES / "confirm_sealed.json").write_text(json.dumps({"sha256": seal, "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat()}))
    base = IL.Base(allow_holdout=True)
    Ps = {"T1": heldout_period(base, 51), "T2": heldout_period(base, 15), "T3": heldout_period(base, 28)}
    out = evaluate(Ps)
    out["mode"] = "CONFIRMATORY (locked holdout)"
    out["sha256"] = seal
    (RES / "confirm_results.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["checks"], indent=1))


if __name__ == "__main__":
    main()
