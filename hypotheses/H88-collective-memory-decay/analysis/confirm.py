"""H88 confirmatory test on the locked holdout. WRITTEN 2026-10-04 after round 1, FROZEN, NOT RUN on the holdout.

  uv run python hypotheses/H88-collective-memory-decay/analysis/confirm.py --dry-run
      scores the round-1 (non-holdout) periods with the frozen rules. Safe: exploration data only.
  uv run python hypotheses/H88-collective-memory-decay/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      needs Vivian's sign-off. Checks the holdout ledger, writes confirm/confirm_sealed.json (SHA-256 of the frozen
      predictions) BEFORE reading any held-out row, rebuilds items, uses and daily shares in memory with held-out days
      (scheme/build.py build(include_holdout=True, write=False, last_day="2026-09-21"); H34 N markers for held-out chat
      rows from infra/shared/idea_markers.uses_for_rows(allow_holdout=True), never written), and fits the held-out-born
      periods' afterlives with the round-1 estimators (h88lib).

Round-1 picture under test: attention to a finished period's coined terms falls fast (exponential, tau ~ 5 village days)
to a persistent floor (~2% of the initial share), not as Candia's biexponential; the present veterans' share decays
(not departure-driven); newcomers are not slower than veterans.

Targets: the items of held-out goal periods #1, #9, #14, #15, #22, #28, #29, #43, #45, #46, #47, #48, #49, #50, followed
for 120 village days (to 2026-09-21).
Frozen predictions (terms primary; artifacts reported):
  C1 among eligible held-out periods (>= 30 term items, >= 3 observed days in k <= 5, >= 30 observed days, >= 50 veteran
     uses after the period), the biexp call (M2 best, dQAIC(M1-M2) >= 2) holds in < 40%, and M1c or MP is best in >= 1/2.
  C2 the present veterans' share at k 21-40 is below k 1-3 (day-bootstrap CI < 1) in >= 2/3 of periods with a ratio.
  C3 newcomers are not slower: the standardized newcomer ratio slope b (h88lib.ratio_bands_boot) has CI including 0 or b <= 0.
  C4 terms: median M1c tau in [2, 12] village days and median floor ratio c/A in [0.005, 0.08].
  Overall: the round-1 picture is CONFIRMED if C1, C2 and C4 pass.
Reuse disclosure: #45 (H02, H04 executed: activity), #46-#50 (H04 executed), #43 and the #51-tail windows have planned
content users; this test reads chat markers and artifact mentions. Disclose in both cards and LOG.md if run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h88lib as H  # noqa: E402

OUTD = H.DATA / "confirm"
PRED = {"C1": "biexp call < 40% and M1c|MP best >= 1/2 (terms)", "C2": "share ratio CI < 1 in >= 2/3",
        "C3": "newcomer b CI includes 0 or b <= 0", "C4": "median M1c tau in [2,12], floor ratio in [0.005,0.08]",
        "overall": "C1 & C2 & C4"}
HELD = [1, 9, 14, 15, 22, 28, 29, 43, 45, 46, 47, 48, 49, 50]
LEDGER_TARGETS = [f"G{g:02d}" for g in HELD]


def eligible(daily, items, kind, Ps):
    n_items = items.group_by("P", "kind").len()
    out = []
    for P in Ps:
        ni = n_items.filter((pl.col("P") == P) & (pl.col("kind") == kind))
        if not ni.height or int(ni["len"][0]) < (10 if kind == "art" else 30):
            continue
        s = daily.filter((pl.col("P") == P) & (pl.col("kind") == kind) & (pl.col("group") == "vet") & pl.col("observed"))
        if s.filter(pl.col("k") <= 5).height >= 3 and s.height >= 30 and (s["y"].sum() or 0) >= 50:
            out.append(P)
    return out


def score(daily, items, Ps):
    out = {}
    for kind in ("term", "art"):
        el = eligible(daily, items, kind, Ps)
        fits, ratios = {}, []
        for P in el:
            k, y, O = H.series(daily, P, kind, "vet")
            f = H.fit_all(k, y, O)
            fits[P] = {"best": f["best"], "dq": f["dq_M1_M2"], "biexp": f["biexp"], "M1c": f["M1c_params"]}
            r = H.share_ratio(k, y, O, seed=P)
            if r.get("ratio") is not None and np.isfinite(r["ratio"]):
                ratios.append(r)
        n = len(fits)
        nb = sum(v["biexp"] for v in fits.values())
        ncp = sum(v["best"] in ("M1c", "MP") for v in fits.values())
        rows = daily.filter((pl.col("kind") == kind) & pl.col("P").is_in(el) & pl.col("observed") & (pl.col("O") > 0)
                            & pl.col("group").is_in(["vet", "new"])).select("P", "group", "k", "y", "O")
        nb_ = H.ratio_bands_boot(rows, B=2000, seed=88) if n else {"b": None, "b_ci": None}
        tau = float(np.median([v["M1c"]["tau"] for v in fits.values()])) if n else None
        flo = float(np.median([v["M1c"]["c"] / v["M1c"]["A"] for v in fits.values()])) if n else None
        res = {"eligible": el, "fits": fits, "n_biexp": nb, "n_M1c_or_MP": ncp, "n_ratio": len(ratios),
               "n_ratio_decay": sum(1 for r in ratios if r.get("ci") and r["ci"][1] < 1), "newcomer": nb_,
               "M1c_tau_median": tau, "floor_ratio_median": flo}
        res["C1"] = bool(n and nb < 0.4 * n and ncp >= 0.5 * n)
        res["C2"] = bool(len(ratios) and res["n_ratio_decay"] >= (2 / 3) * len(ratios))
        res["C3"] = bool(nb_["b"] is None or nb_["b"] <= 0 or (nb_["b_ci"] and nb_["b_ci"][0] <= 0))
        res["C4"] = bool(tau is not None and 2 <= tau <= 12 and 0.005 <= flo <= 0.08)
        out[kind] = res
    t = out["term"]
    out["overall"] = bool(t["C1"] and t["C2"] and t["C4"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    if a.dry_run:
        daily = H.load_daily(); items = pl.read_parquet(H.DATA / "items.parquet")
        Ps = sorted(daily["P"].unique().to_list())
        out = {"mode": "dry-run (non-holdout stand-ins: round-1 periods)", "frozen": PRED, **score(daily, items, Ps),
               "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        (OUTD / "confirm_dryrun.json").write_text(json.dumps(out, indent=1, default=float))
        print({k: out["term"][k] for k in ("C1", "C2", "C3", "C4")}, "overall", out["overall"])
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: needs --confirm --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
    sys.path.insert(0, str(H.ROOT / "infra/shared"))
    import holdout_ledger as HL
    for tgt in LEDGER_TARGETS:
        chk = HL.check("H88", tgt, "chat markers + artifact mentions", None)
        print(tgt, "allowed" if chk["allowed"] else "NOT ALLOWED", "disclose" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            sys.exit(f"holdout ledger forbids {tgt}")
    seal = json.dumps(PRED, sort_keys=True)
    (OUTD / "confirm_sealed.json").write_text(json.dumps({"sha256": hashlib.sha256(seal.encode()).hexdigest(), "pred": PRED,
                                                          "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))
    import build as B
    T = B.build(include_holdout=True, write=False, last_day="2026-09-21")
    out = {"mode": "CONFIRMATORY", "frozen": PRED, **score(T["daily"], T["items"], HELD),
           "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUTD / "confirm_results.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float)[:3000])


if __name__ == "__main__":
    main()
