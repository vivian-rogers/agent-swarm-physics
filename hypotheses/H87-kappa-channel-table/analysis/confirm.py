"""H87 confirmatory test on the locked holdout. WRITTEN 2026-10-04 after round 1, NOT RUN on the holdout.

  uv run python hypotheses/H87-kappa-channel-table/analysis/confirm.py --dry-run
      runs the frozen pipeline on the non-holdout stand-in (the round-1 NE41 frame, B = 100). Safe.
  uv run python hypotheses/H87-kappa-channel-table/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      checks the holdout ledger, writes confirm/confirm_sealed.json (SHA-256 of the frozen predictions) BEFORE reading
      any held-out row, builds the held-out event frame, then scores. Refuses to run without BOTH flags.

Inputs for the held-out run (data, not code; STANDARDS §8 asks that the builders move to infra/shared first):
  data/processed/H70-artifact-store-semantic-info/events_confirm.parquet  (H70's builder with held=True)
  data/processed/H84-search-outage-memory-scramble/search_events_confirm.parquet  (H84 search_events.py --held)
The script stops if either is missing; it never builds them itself.

Round-1 picture under test: of all channels, only the context window buys commits per allocation bit; artifact,
memory, chat and search pointers carry bits without value; memory size does nothing; chat after an erasure helps.
Targets: held-out regime-III periods #43, #45-#50 and the #51 tail (forced erasures F vs pseudo-erasures P).
Frozen predictions:
  C1 pooled erasure cost dV_rel(C) in [0.30, 0.50] with CI excluding 0.
  C2 if A and C are both identified (I CI lower > 0.02 bits): P(kappa_C > kappa_A) >= 0.9; else C identified, kappa_C > 0.
  C3 the open-channel dV_rel of A, M and G each has a CI that includes 0 or lies below 0.
  C4 memory-size (top vs bottom tercile) x erasure dV_rel within [-0.10, +0.10].
  C5 any agent chat item x erasure dV_rel > 0 with CI excluding 0.
  Overall: CONFIRMED if C1, C2 and C3 pass.
Reuse disclosure: the held-out regime-III periods are targeted by H70's confirm.py (artifact row, same events), H44,
H15 and H58 (forced-erasure designs) and many others (infra/data-quality/holdout_ledger.json). H87 shares H70's
event frame and estimator; if H70's confirmatory run happens first, H87's C1/C2 are not independent of it. Disclose.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h87lib as L  # noqa: E402

OUTD = L.DATA / "confirm"
H70 = L.ROOT / "data/processed/H70-artifact-store-semantic-info"
PRED = {"C1": "pooled erasure cost dV_rel(C) in [0.30, 0.50], CI excluding 0",
        "C2": "if A and C identified: P(kappa_C > kappa_A) >= 0.9; else C identified and kappa_C > 0",
        "C3": "open-channel dV_rel of A, M, G: CI includes 0 or lies below 0",
        "C4": "memory size x erasure dV_rel within [-0.10, +0.10]",
        "C5": "any agent chat item x erasure dV_rel > 0, CI excluding 0",
        "overall": "CONFIRMED if C1, C2 and C3 pass"}
TARGETS = ["G43", "G45", "G46", "G47", "G48", "G49", "G50", "#51-tail"]


def ident(r):
    return r["I_ci"][0] is not None and r["I_ci"][0] > L.MIN_I


def score(ev: pl.DataFrame, B: int) -> dict:
    f = L.call_frame(ev)
    t = L.paired_table(f, B=B, n_perm=200, n_perm_boot=10, seed=87, rows=("A", "M", "G", "Q"), variants=True)
    R, own = t["rows"], t["own_scramble"]
    c = R["C"]
    c1 = 0.30 <= c["dV_rel"] <= 0.50 and c["dV_rel_ci"][0] > 0
    if ident(R["A"]) and ident(c):
        c2 = (t["paired"]["C>A"]["p"] or 0) >= 0.9
    else:
        c2 = ident(c) and c["kappa_ci"][0] is not None and c["kappa_ci"][0] > 0
    c3 = all(R[k]["dV_rel_ci"][0] is None or R[k]["dV_rel_ci"][0] <= 0 for k in ("A", "M", "G"))
    m = own["Msize"]["dV_rel"]
    c4 = -0.10 <= m <= 0.10
    c5 = own["Gany"]["dV_rel_ci"][0] is not None and own["Gany"]["dV_rel_ci"][0] > 0
    out = {"C1": bool(c1), "C2": bool(c2), "C3": bool(c3), "C4": bool(c4), "C5": bool(c5),
           "rows": {k: {kk: v for kk, v in r.items()} for k, r in R.items()}, "own_scramble": own,
           "n_scramble": t["n_scramble"], "n_placebo": t["n_placebo"]}
    out["overall"] = "CONFIRMED" if c1 and c2 and c3 else "NOT confirmed"
    return out


def dry_run():
    res = {"mode": "dry-run (non-holdout NE41 stand-in, B = 100)", "predictions": PRED, **score(L.load(), B=100)}
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=float))
    print({k: res[k] for k in ("C1", "C2", "C3", "C4", "C5", "overall")})


def confirm():
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import holdout_ledger as HL  # noqa: E402
    for tg in TARGETS:
        chk = HL.check("H87", tg, "work commits after forced erasures", ["work_output", "artifact_lineage"])
        print(tg, "allowed" if chk["allowed"] else "BLOCKED", "disclosure needed" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            sys.exit(f"holdout ledger blocks {tg}; stop and ask Vivian")
    ev_path = H70 / "events_confirm.parquet"
    se_path = L.H84D / "search_events_confirm.parquet"
    for p in (ev_path, se_path):
        if not p.exists():
            sys.exit(f"missing held-out input {p}; build it with its owner's script first (see docstring)")
    OUTD.mkdir(parents=True, exist_ok=True)
    sealed = {"predictions": PRED, "sha256": hashlib.sha256(json.dumps(PRED, sort_keys=True).encode()).hexdigest(),
              "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUTD / "confirm_sealed.json").write_text(json.dumps(sealed, indent=1))
    import build as B  # noqa: E402  (H87 scheme)
    cal = pl.read_parquet(L.ROOT / "data/processed/shared/calendar.parquet").filter(
        pl.col("holdout") & (pl.col("regime").cast(pl.Utf8) == "III"))
    B.build(events_path=ev_path, search_path=se_path, held_days=sorted(cal["pt_date"].to_list()),
            out_name="events_plus_confirm.parquet")
    ev = L.load(L.DATA / "events_plus_confirm.parquet")
    res = {"mode": "CONFIRMATORY", "predictions": PRED, "sealed": sealed["sha256"], **score(ev, B=300)}
    (OUTD / "confirm_result.json").write_text(json.dumps(res, indent=1, default=float))
    print(res["overall"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", action="store_true", dest="ack")
    a = ap.parse_args()
    if a.confirm:
        if not a.ack:
            sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
        confirm()
    elif a.dry_run:
        dry_run()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
