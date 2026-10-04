"""H48 replication-layer period READMEs (role: replication).

  uv run python hypotheses/H48-settling-mixing-time/analysis/period_folders.py --predict   # before the settling run
  uv run python hypotheses/H48-settling-mixing-time/analysis/period_folders.py --results   # after compare.py

--predict writes the templated prediction (labelled as such) for every replication period without a README; it uses
read-out predictors only (no content). --results fills Verdict, Result and Scorecard from settling_period.parquet,
readout_period.parquet and compare_lopo.parquet, keeping the dated prediction text unchanged. Native folders
(G38, G51, NE42, NE32) are written by natives.py and are skipped here, except G38/G51 which get a replication row in
their own README (they are native)."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h48lib as L  # noqa: E402
from h48lib import hc  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

GP = hc.HDIR / "goalperiod-subhypotheses"
NATIVE_G = {38, 51}


def title(g: int) -> str:
    for h in ("H20-content-aging", "H54-kickoff-quench-target", "H31-consensus-time-spectral-gap"):
        p = hc.ROOT / "hypotheses" / h / "goalperiod-subhypotheses" / f"G{g:02d}" / "README.md"
        if p.exists():
            line = p.read_text().splitlines()[0]
            m = re.match(r"# H\d+ × G\d+: (.*)$", line)
            if m:
                return m.group(1)
    return f"goal period #{g}"


def f(x, d=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    if isinstance(x, float) and abs(x) >= 100:
        return f"{x:.0f}"
    return f"{x:.{d}f}"


def predict():
    X = pl.read_parquet(hc.OUT / "readout_period.parquet")
    for g in hc.REPLICATION:
        if g in NATIVE_G:
            continue
        d = GP / f"G{g:02d}"
        if (d / "README.md").exists():
            continue
        d.mkdir(parents=True, exist_ok=True)
        (d / "figures").mkdir(exist_ok=True)
        r = X.filter(pl.col("goal_no") == g).row(0, named=True)
        rooms = "one room (#general)" if r["n_rooms"] == 1 and r["regime"] == "I" else (
            f"{r['n_rooms']} room blocks ({r['rooms']})")
        txt = f"""# H48 × G{g:02d}: {title(g)}

**Verdict:** pending
**Role:** replication
**Period:** regime {r['regime']} · {r['N']} agents on the kickoff roster · {rooms} · {r['n_days']} active days ({f(r['T_h'], 1)} active h, {f(r['hours_per_day'], 1)} h/day). Kickoff time from {'H54' if r['t0_src'] == 'h54_kickoff' else 'the first window start (no H54 kickoff row)'}.

## Why this period
One phase-diagram point of the replication layer: the common estimators (S1 settling, read-out coverage, bulk mixing, λ₂ rivals) on a non-holdout period of ≥ 5 active days. Nothing period-specific is tested here.

## Prediction
*Templated replication prediction (card P1, P2), written 2026-10-04 ~07:25 UTC before the settling run on this period. Read-out predictors (no content) were already computed: direct coverage T90 = {f(r['k1_room_T90'], 3)} active h, depth-5 T90 = {f(r['k5_room_T90'], 2)} h, bulk mixing t_mix = {f(r['tmix_batch_bulk'], 3)} h, reading rate u = {f(r['u'], 1)} /h, λ₂^w,sym (min block) = {f(r['l2_sym_min'], 1)} /h.*
- S1 settling is detected (a decaying kickoff excess with ΔBIC ≥ 2).
- τ_S1 falls inside the 80% leave-one-period-out interval of the T90 model fitted on the other periods (the card's P1 rule applied to this point).
- Magnitude (card P2, expected to fail): τ_S1 / T90 ≤ 3.

## Result
(filled after the run)

## Scorecard (period-specific axes)
(filled after the run)

## Notes
- Data: `data/processed/H48-settling-mixing-time/G{g:02d}/` (`coverage_curves.parquet`, `s1_series_<model>.parquet`); cross-period rows in `readout_period.parquet` and `settling_period.parquet`.
"""
        (d / "README.md").write_text(txt)
        print("wrote", d / "README.md")


def results():
    X = pl.read_parquet(hc.OUT / "readout_period.parquet")
    S = pl.read_parquet(hc.OUT / "settling_period.parquet")
    lp = pl.read_parquet(hc.OUT / "compare_lopo.parquet")
    rows_out = {}

    def est(g, model, e):
        s = S.filter((pl.col("goal_no") == g) & (pl.col("model") == model) & (pl.col("estimator") == e))
        return s.row(0, named=True) if s.height else {}
    # LOPO 80% interval of the T90 model for each detected period (bge)
    T = S.filter((pl.col("model") == "bge_small") & (pl.col("estimator") == "S1") & pl.col("detected").fill_null(False))
    D = X.join(T.select("goal_no", "tau"), on="goal_no").filter(pl.col("goal_no").is_in(hc.REPLICATION))
    y = np.log(D["tau"].to_numpy())
    x = np.log(D["k1_room_T90"].to_numpy())
    _, pred = L.lopo_rmse(y, x)
    res = y - pred
    q10, q90 = np.quantile(res, [0.1, 0.9])
    lop = dict(zip(D["goal_no"].to_list(), zip(pred, res)))
    for g in hc.REPLICATION:
        d = GP / f"G{g:02d}"
        p = d / "README.md"
        if not p.exists() or g in NATIVE_G:     # native READMEs are written by hand from natives.json
            continue
        r = X.filter(pl.col("goal_no") == g).row(0, named=True)
        b, gt = est(g, "bge_small", "S1"), est(g, "gte_modernbert", "S1")
        s2, s3 = est(g, "bge_small", "S2_H20"), est(g, "bge_small", "S3_H54day")
        det = bool(b.get("detected"))
        inside = None
        if g in lop:
            pr, rs = lop[g]
            inside = bool(q10 <= rs <= q90)
        ratio = (b["tau"] / r["k1_room_T90"]) if det and r["k1_room_T90"] else None
        verdict = "descriptive"
        rows = [
            ("S1 settling detected (bge; gte)", f"{'yes' if det else 'no'} (ΔBIC {f(b.get('dbic'), 1)}); gte {'yes' if gt.get('detected') else 'no'} (ΔBIC {f(gt.get('dbic'), 1)})",
             "constant excess", "met" if det else "not met"),
            ("τ_S1 (active h), bge / gte", f"{f(b.get('tau'), 2)} / {f(gt.get('tau'), 2)}; excess {f(b.get('A_0'), 3)} → {f(b.get('A_inf'), 3)}", "–", "–"),
            ("inside the T90 model's 80% LOPO interval", "–" if inside is None else ("yes" if inside else "no") + f" (pred {f(float(np.exp(lop[g][0])), 2)} h)" if g in lop else "–",
             "constant model", "–" if inside is None else ("met" if inside else "not met")),
            ("magnitude τ_S1 / T90 ≤ 3", f"{f(ratio, 1)} (T90 {f(r['k1_room_T90'], 3)} h; depth-5 T90 {f(r['k5_room_T90'], 2)} h)", "–",
             "–" if ratio is None else ("met" if ratio <= 3 else "not met")),
            ("H20 τ_q (days → h), H54 day τ_K (h)", f"{f(s2.get('tau_days'), 2)} d → {f(s2.get('tau'), 1)} h ({'detected' if s2.get('detected') else 'not detected'}); {f(s3.get('tau'), 1)} h", "–", "descriptive"),
        ]
        if det and inside is not None:
            verdict = "supported" if inside and ratio is not None and ratio <= 3 else ("mixed" if inside else "failed")
        elif not det:
            verdict = "n/a"
        tbl = "| Prediction | Observed | Null | Verdict |\n| --- | --- | --- | --- |\n" + "\n".join(
            f"| {a} | {b_} | {c} | {v} |" for a, b_, c, v in rows)
        txt = p.read_text()
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict}", txt, count=1)
        figs = f"Figures: `../../figures/` (cross-period). Data: `data/processed/H48-settling-mixing-time/G{g:02d}/`."
        txt = re.sub(r"## Result\n.*?\n## Scorecard", f"## Result\n{tbl}\n\nVerdict rule (replication): supported = detected, inside the T90 model's LOPO 80% interval and τ/T90 ≤ 3; mixed = inside the interval only; failed = outside; n/a = no detected settling. {figs}\n\n## Scorecard", txt, flags=re.S)
        sc = ("- **C:** " + ("the T90 model's out-of-sample error for this point is "
                             f"{f(abs(lop[g][1]), 2)} in log τ" if g in lop else "not scored (no detected settling)") +
              ".\n- **D:** magnitude prediction " + ("met" if ratio is not None and ratio <= 3 else "not met" if ratio is not None else "not scored") + ".")
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", f"## Scorecard (period-specific axes)\n{sc}\n\n## Notes", txt, flags=re.S)
        p.write_text(txt)
        rows_out[g] = dict(verdict=verdict, tau=b.get("tau"), T90=r["k1_room_T90"], det=det)
    hc.save_json(hc.OUT / "replication_verdicts.json", rows_out)
    print(rows_out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--results", action="store_true")
    a = ap.parse_args()
    if a.predict:
        predict()
    if a.results:
        results()


if __name__ == "__main__":
    main()
