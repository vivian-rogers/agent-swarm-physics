"""H61 confirmatory test on the locked holdout. WRITTEN 2026-10-04, FROZEN, NOT RUN on the holdout.

  uv run python hypotheses/H61-contagiousness-at-first-use/analysis/confirm.py --dry-run
      runs the frozen pipeline on non-holdout stand-ins (safe; exploration data only)
  uv run python hypotheses/H61-contagiousness-at-first-use/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      reads held-out chat text in memory (marker extraction only), builds the targets' idea tables and scores the
      frozen predictions. Refuses without BOTH flags. Calls holdout_ledger.check() first and writes
      results/confirm_sealed.json (SHA-256 of this docstring) BEFORE touching held-out data.

Targets (locked holdout; reuse policy in hypotheses/holdout.md):
  T1  #51 tail (2026-09-07 -> 09-21)   primary; models trained on all non-holdout #51 days, scored on the tail
  T2  #15 (regime I)    T3  #28 (regime I)   forward chaining by day inside the target (as in the replication layer)
Stand-ins for --dry-run: T1 = #51 days 08-24 -> 09-04 scored with a model trained on #51 days before 08-24;
T2 = #13, T3 = #25.
Reuse disclosure: the #51 tail, #15 and #28 are also targets of H34's unrun confirm script (same marker modality,
different statistic: tree sizes and HR10, not a first-use forecast) and of other unrun scripts listed in the holdout
ledger. If run, disclose in both cards and LOG.md.

Frozen predictions (from round-1 exploration, frozen 2026-10-04 before any holdout use):
  C1 (primary) T1: dLL(F - B4) > 0 with lower 95% seed-message cluster-bootstrap CI > 0.
     (Round 1: G51 +5.5 [+4.1, +7.1] millinats/idea; G38 +6.3 [+3.0, +9.7]; only 4/27 periods overall.)
  C2 T1: AUC_F - AUC_B1 >= 0.05 and top-decile lift for Y >= 1.5. (G51: +0.12, 2.54.)
  C3 T1: message-level dilution: the focus (log novel load) and seed-length coefficients are both < 0 with 95% CIs
     below 0 (standardised log-odds, in-sample on T1). (G51: -0.13 +- 0.02, -0.24 +- 0.02; pooled over 27 periods
     -0.08 +- 0.03 and -0.26 +- 0.04.)
  C4 T2, T3 (regime I, small): no reliable gain: dLL(F - B4) lower 95% CI <= 0 in both. Descriptive (synthetic power
     0.2-0.5 at these sizes), recorded so that the regime/size dependence is tested, not assumed.
  C5 T1 (convergence): G_read5 - G_unread5 lower 95% CI > +0.011 (the synthetic null mean), if >= 15 events each.
     Round 1 had no power for this (unread-5 adopters are 0.6% of adopters in G51); expected inconclusive.
  Overall: SUPPORTED (forecastable at first use in the largest regime-III swarm) if C1 and C2 pass; the
  message-level dilution law is CONFIRMED if C3 passes. Each C is reported separately.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

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
import h61lib as L  # noqa: E402
import idea_ledger as IL  # noqa: E402
import build as BLD  # noqa: E402

OUT = ROOT / "data/processed/H61-contagiousness-at-first-use"
RES = OUT / "results"
FIRST_SEEN = ROOT / "data/processed/H34-idea-cascades/markers/first_seen.parquet"
TARGETS = {"T1": dict(goal=51, label="#51 tail", train="nonholdout"), "T2": dict(goal=15, label="#15", train="chain"),
           "T3": dict(goal=28, label="#28", train="chain")}
STANDINS = {"T1": dict(goal=51, label="#51 08-24 -> 09-04 (stand-in)", split="2026-08-24"),
            "T2": dict(goal=13, label="#13 (stand-in)"), "T3": dict(goal=25, label="#25 (stand-in)")}
NULL_MEAN_P5 = 0.011


def heldout_ideas(base: IL.Base, g: int) -> pl.DataFrame:
    """Build the target's idea table from held-out days (confirm only). Markers are extracted in memory."""
    import idea_markers as M
    days = base.period_days(g, allow_holdout=True)
    days = [d for d, h in zip(days, IL.holdout_mask(days, [g] * len(days))) if h]
    P = IL.load_period(base, g, days=days, allow_holdout=True, with_markers=False)
    uses = M.uses_for_rows(P["rows"], allow_holdout=True)
    t_start = int(P["t"].min())
    fs = pl.read_parquet(FIRST_SEEN).select("marker", "first_t")
    old = fs.filter(pl.col("first_t").dt.epoch("us") < t_start)["marker"]
    uses = uses.filter(~pl.col("marker").is_in(old.implode()))
    pos_of = {int(r): i for i, r in enumerate(P["rows"])}
    P["use_pos"] = np.array([pos_of[int(m)] for m in uses["msg"].to_numpy()], dtype=np.int64)
    P["use_marker"] = uses["marker"].to_numpy().astype(np.int64)
    P["use_cls"] = uses["cls"].to_numpy().astype(np.int8)
    return BLD.build_period(base, BLD.Emb(), g, P=P)


def score_transfer(train: pl.DataFrame, test: pl.DataFrame, seed: int = 0) -> dict:
    both = pl.concat([train, test], how="diagonal_relaxed")
    tr = np.r_[np.ones(train.height, bool), np.zeros(test.height, bool)]
    y = both["y"].to_numpy().astype(float)
    P = {}
    for m in ("B1", "B4", "F"):
        X, names, pen = L._design(both, L.MODELS[m], tr)
        b = L.fit_logit(X[tr], y[tr], pen)
        P[m] = L.predict(b, X[~tr])
    pred = test.select("idea", "seed_msg", "day", "reach24", "y").with_columns(
        [pl.Series(f"p_{m}", v) for m, v in P.items()])
    return pred


def evaluate(tables: dict) -> dict:
    res = {}
    for k, (kind, a, b) in tables.items():
        if kind == "transfer":
            pred = score_transfer(a, b)
            df_t = b
        else:
            pred = L.forward_chain(a, "y", models=("B1", "B4", "F"))
            df_t = a
        y = pred["y"].to_numpy().astype(float)
        d = (L.ll(y, pred["p_F"].to_numpy()) - L.ll(y, pred["p_B4"].to_numpy())) * 1000
        bs = L.cluster_boot(lambda idx: d[idx].mean(), pred["seed_msg"].to_numpy(), 2000, np.random.default_rng(61))
        auc_gain = L.auc(y, pred["p_F"].to_numpy()) - L.auc(y, pred["p_B1"].to_numpy())
        lift = L.lift(y, pred["p_F"].to_numpy())
        coef = L.coefs(df_t, "y", "F")
        r = dict(n_test=int(len(y)), n_pos=int(y.sum()), dll=float(d.mean()), dll_lo=float(np.percentile(bs, 2.5)),
                 dll_hi=float(np.percentile(bs, 97.5)), auc_gain=float(auc_gain), lift=float(lift),
                 focus=coef["lg_novel"], length=coef["lg_len"])
        if k == "T1":
            r["conv"] = L.gains_conv(df_t, B=300, seed=61)
        res[k] = r
    t1 = res["T1"]
    c = {"C1": t1["dll_lo"] > 0,
         "C2": t1["auc_gain"] >= 0.05 and t1["lift"] >= 1.5,
         "C3": (t1["focus"][0] + 1.96 * t1["focus"][1] < 0) and (t1["length"][0] + 1.96 * t1["length"][1] < 0),
         "C4": res["T2"]["dll_lo"] <= 0 and res["T3"]["dll_lo"] <= 0,
         "C5": bool(t1["conv"].get("eligible") and t1["conv"]["diff_lo"] > NULL_MEAN_P5)}
    return dict(results=res, checks=c, supported=bool(c["C1"] and c["C2"]), dilution_confirmed=bool(c["C3"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    base = IL.Base()
    if a.dry_run:
        g51 = L.prep(pl.read_parquet(OUT / "G51/ideas.parquet"))
        split = int(dt.datetime.fromisoformat("2026-08-24T07:00:00+00:00").timestamp() * 1e6)
        tables = {"T1": ("transfer", g51.filter(pl.col("t0_us") < split), g51.filter(pl.col("t0_us") >= split)),
                  "T2": ("chain", L.prep(pl.read_parquet(OUT / "G13/ideas.parquet")), None),
                  "T3": ("chain", L.prep(pl.read_parquet(OUT / "G25/ideas.parquet")), None)}
        out = evaluate(tables)
        out["mode"] = "dry-run on stand-ins (non-holdout)"
        (RES / "confirm_dryrun.json").write_text(json.dumps(out, indent=1, default=float))
        print(json.dumps(out, indent=1, default=float))
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: needs --confirm --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
    import holdout_ledger as HL
    for tgt in ("#51-tail", "G15", "G28"):
        st = HL.check("H61", tgt, modality="chat content (markers)")
        if not st["allowed"]:
            sys.exit(f"refusing: {tgt} already used by the same estimator family: {st['prior_runs_same_family']}")
        if st["needs_disclosure"]:
            print(f"DISCLOSE reuse of {tgt}: {len(st['prior_runs'])} prior runs, {len(st['competing_planned'])} planned")
    seal = hashlib.sha256(__doc__.encode()).hexdigest()
    (RES / "confirm_sealed.json").write_text(json.dumps({"sha256": seal, "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat()}))
    g51 = L.prep(pl.read_parquet(OUT / "G51/ideas.parquet"))
    tables = {"T1": ("transfer", g51, L.prep(heldout_ideas(base, 51))),
              "T2": ("chain", L.prep(heldout_ideas(base, 15)), None),
              "T3": ("chain", L.prep(heldout_ideas(base, 28)), None)}
    out = evaluate(tables)
    out["mode"] = "CONFIRMATORY (locked holdout)"
    out["sha256"] = seal
    (RES / "confirm_results.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["checks"], indent=1))


if __name__ == "__main__":
    main()
