"""H57 confirmatory test on the locked holdout. WRITTEN, NOT RUN (round 1, 2026-10-04).

  uv run python hypotheses/H57-copy-under-backlog/analysis/confirm.py                 # dry run on non-holdout stand-ins
  uv run python hypotheses/H57-copy-under-backlog/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout

Predictions (frozen 2026-10-04, after exploratory round 1, before any held-out row was read). Exploration refuted H57
as stated and found that what looks like echo is mostly contemporaneous convergence; the confirmation therefore tests
the refutation and the bounds, on statistics nobody has computed on these targets.
Targets: primary the #51 tail (unit 51m, 2026-09-07 -> 09-18); secondary #43 and #45 (regime III, pooled).
  C1 (no load-driven copying): within-agent slope of the raw read-set echo (any read item above the DQ5 near-copy
     threshold) on log2(1 + k), agent x unit FE and the card's controls: the upper end of the one-sided 95% interval
     is < 0.006 per doubling in both models (exploration: #51 +0.0007 +- 0.0002; pooled +0.0016; the synthetic
     H57 world plants +0.03). Falsifier: lower end > 0.006 in both models.
  C2 (addressed replies transform): the near-copy rate of the unambiguous addressed source (named author has one read
     item) is < 0.02 in every within-target k tercile, both models (exploration 0.001-0.022).
  C3 (convergence, not copying, makes semantic near-copies): at lags < 15 s the both-model near-copy rate of mutually
     invisible in-flight pairs is >= 0.4 x that of read pairs (exploration median 0.75; #51 0.52). Pooled over targets.
  C4 (post hoc estimator): the lag-matched count excess (elc, Amendment 2) has slope <= 0.002 per doubling in both
     models (exploration #51 -0.0055 / +0.0003).
Reuse policy: holdout_ledger.check() is called for every target; the run stops if a prior run used the same estimator
family; required disclosures are printed (the #51 tail is planned by H34 and H37; #45 was used by H02/H04 for activity
timing, a different modality).
Outputs: data/processed/H57-copy-under-backlog/confirm_dryrun/ (dry run) or confirm/ (real run). Codes and numbers only;
held-out text is read in memory only for H34 markers (scheme/h57core.holdout_markers).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
import h57core as C  # noqa: E402
import h57lib as L  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from run_period import jnum  # noqa: E402
from scipy import stats  # noqa: E402

sys.path.insert(0, str(C.ROOT / "infra/shared"))
import holdout_ledger as HL  # noqa: E402

REAL = {"#51-tail": (51, ["51m"]), "G43": (43, None), "G45": (45, None)}
STANDIN = {"#51-tail": (51, ["51h", "51i", "51j", "51k", "51l"]), "G43": (44, None), "G45": (42, None)}
FAMILY = ["content_alignment", "artifact_lineage"]
MODALITY = "message content"


def unit_frame(goal: int, units, confirm: bool):
    if confirm:
        S, P = C.build_skeleton(goal, allow_holdout=True)
    else:
        S = pl.read_parquet(C.OUT / "skeleton" / f"G{goal:02d}_S.parquet")
        P = pl.read_parquet(C.OUT / "skeleton" / f"G{goal:02d}_P.parquet")
    if units:
        keep = S.filter(pl.col("unit_id").is_in(units))
        P = P.filter(pl.col("sid").is_in(keep["sid"].to_list()))
        remap = {o: i for i, o in enumerate(keep["sid"].to_list())}
        S = keep.with_columns(pl.col("sid").replace_strict(remap, return_dtype=pl.Int32))
        P = P.with_columns(pl.col("sid").replace_strict(remap, return_dtype=pl.Int32))
    msgs = np.unique(np.r_[S["msg"].to_numpy(), P["msg"].to_numpy()]).astype(np.int64)
    content = C.load_real_content(msgs, allow_holdout=confirm)
    common = C.common_markers(goal, S, content, allow_holdout=confirm)
    o = C.outcomes(S, P, content, K_list=(32,), common=common, kick=C.kickoff_vectors(goal), seed=goal)
    d = L.prepare(S.join(o, on="sid", how="left"))
    return d, S, P, content


def lag0_counts(S, P, content):
    """Both-model near-copy hits and pairs at lag < 15 s for read (set 0) and in-flight (set 2) pairs."""
    pos = {int(m): i for i, m in enumerate(content["msgs"])}
    PP = P.filter(pl.col("set").is_in([0, 2]))
    b = np.array([pos[int(x)] for x in S["msg"].to_list()])
    ps = PP["sid"].to_numpy(); pl_ = np.array([pos[int(x)] for x in PP["msg"].to_list()])
    near = np.ones(len(ps), bool)
    for m in C.MODELS:
        R = content["raw"][m]
        near &= np.einsum("ij,ij->i", R[b[ps]], R[pl_]) >= C.THR[m]
    tb = S["t"].to_numpy()[ps]
    ta = C.chat()["t"].to_numpy()[PP["msg"].to_numpy().astype(np.int64)]
    lag = np.abs((tb - ta).astype("timedelta64[ms]").astype(float)) / 1000
    st = PP["set"].to_numpy()
    out = {}
    for s, nm in ((0, "read"), (2, "inflight")):
        m = (st == s) & (lag < 15)
        out[nm] = {"pairs": int(m.sum()), "hits": int(near[m].sum())}
    return out


def evaluate(d, S, P, content) -> dict:
    r = {"n": d.height}
    for m in C.MODELS:
        for y in (f"er_{m}", f"elc_{m}"):
            s = L.slope(d, y, "agent").get("logk", {})
            b, se = s.get("b", np.nan), s.get("se", np.nan)
            r[y] = {"b": b, "se": se, "lo95_one": b - 1.645 * se, "hi95_one": b + 1.645 * se}
        dd = d.filter(pl.col(f"near_{m}_addr").is_not_null())
        if dd.height >= 30:
            bins = L.k_bins(dd["k"].to_numpy().astype(float))
            r[f"near_addr_{m}_by_tercile"] = [float(dd.filter(pl.Series(bins == j))[f"near_{m}_addr"].mean())
                                              for j in (0, 1, 2)]
    r["lag0"] = lag0_counts(S, P, content)
    return r


def verdicts(per: dict) -> dict:
    tail = per.get("#51-tail", {})
    v = {}
    if tail:
        his = [tail[f"er_{m}"]["hi95_one"] for m in C.MODELS]
        los = [tail[f"er_{m}"]["lo95_one"] for m in C.MODELS]
        v["C1"] = "pass" if max(his) < 0.006 else ("fail" if min(los) > 0.006 else "inconclusive")
        nt = [x for m in C.MODELS for x in tail.get(f"near_addr_{m}_by_tercile", [np.nan])]
        v["C2"] = "pass" if np.all(np.array(nt) < 0.02) else "fail"
        v["C4"] = "pass" if max(tail[f"elc_{m}"]["b"] for m in C.MODELS) <= 0.002 else "fail"
    hr = sum(p["lag0"]["read"]["hits"] for p in per.values()); nr = sum(p["lag0"]["read"]["pairs"] for p in per.values())
    hi = sum(p["lag0"]["inflight"]["hits"] for p in per.values()); ni = sum(p["lag0"]["inflight"]["pairs"] for p in per.values())
    ratio = (hi / max(ni, 1)) / (hr / max(nr, 1)) if hr > 0 else np.nan
    v["C3"] = {"ratio": ratio, "read": [hr, nr], "inflight": [hi, ni],
               "verdict": "pass" if np.isfinite(ratio) and ratio >= 0.4 else ("fail" if np.isfinite(ratio) else "n/a")}
    # secondary targets: the pooled er slopes (inverse-variance) must also satisfy C1's bound
    sec = [p for k, p in per.items() if k != "#51-tail"]
    for m in C.MODELS:
        re = L.random_effects([p[f"er_{m}"]["b"] for p in sec], [p[f"er_{m}"]["se"] for p in sec])
        v[f"C1_secondary_{m}"] = re
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    confirm = a.confirm and a.ack
    if a.confirm and not a.ack:
        sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
    targets = REAL if confirm else STANDIN
    checks = {t: HL.check("H57", t, MODALITY, FAMILY) for t in REAL}
    for t, c in checks.items():
        print(f"ledger {t}: allowed={c['allowed']} needs_disclosure={c['needs_disclosure']} "
              f"prior_runs={[u['hypothesis'] for u in c['prior_runs']]} "
              f"competing={[u['hypothesis'] for u in c['competing_planned']]}")
        if confirm and not c["allowed"]:
            sys.exit(f"refusing: {t} already used by the same estimator family")
    per = {}
    for t, (g, units) in targets.items():
        d, S, P, content = unit_frame(g, units, confirm)
        per[t] = evaluate(d, S, P, content)
        print(t, "(stand-in G%02d %s)" % (g, units) if not confirm else "", json.dumps(jnum(per[t]))[:400])
    v = verdicts(per)
    out = C.OUT / ("confirm" if confirm else "confirm_dryrun")
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(jnum({"mode": "confirm" if confirm else "dry-run (stand-ins)",
                                                      "targets": {k: list(map(str, v_)) for k, v_ in targets.items()},
                                                      "ledger": {k: {"allowed": c["allowed"],
                                                                     "needs_disclosure": c["needs_disclosure"]}
                                                                 for k, c in checks.items()},
                                                      "per_target": per, "verdicts": v,
                                                      "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}),
                                                indent=1, default=str))
    print("verdicts:", json.dumps(jnum(v), default=str))
    if confirm:
        print("Record the run: holdout_ledger.record_run(<entry id>, evidence) and disclose reuse in the card and LOG.md")


if __name__ == "__main__":
    main()
