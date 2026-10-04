"""H48 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploration; NOT RUN.

  uv run python hypotheses/H48-settling-mixing-time/analysis/confirm.py --freeze          # freeze rules from exploration
  uv run python hypotheses/H48-settling-mixing-time/analysis/confirm.py --dry-run         # stand-ins, no holdout access
  uv run python hypotheses/H48-settling-mixing-time/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout

Targets (held-out goal periods with a kickoff and >= 5 active days, chosen to avoid the most contended content
targets: #45 has 11 planned content users, #22 is H10's confirmatory pair, #14 is H18's): #1, #15, #28, #29, #47, #50.
Modality: content (kickoff alignment, S1) + read-out schedule (context ledger). Estimator family: content_alignment.
None of the three executed holdout runs (H02, H04, H05: activity timing) used this family, so the reuse policy allows
it with disclosure; `holdout_ledger.check()` is called for every target before any data is read.

Frozen rules (from exploration, `frozen_rule.json`):
  C1 (H48 primary, expected to fail given exploration): the bulk-mixing model log tau = a + b log t_mix^bulk, fitted
     on the exploration periods with detected S1 (bge), has lower RMSE on the targets' detected tau_S1 than the
     frozen constant (exploration median).
  C2 (post-hoc lead): the depth-5 coverage model log tau = a + b log T90_k5 beats the frozen constant on the targets.
  C3 (magnitude lead): the median of tau_S1 / T90_k5 over the targets lies in [1/3, 3].
  C4 (replication of the null): the frozen constant's 80% interval covers >= 70% of the targets' tau_S1.
  Both embedding models are computed; bge is primary, gte must agree in sign of the C1/C2 RMSE difference.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h48lib as L  # noqa: E402
from h48lib import hc  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

TARGETS = [1, 15, 28, 29, 47, 50]
STAND_INS = [10, 20, 24, 41]
FROZEN = Path(__file__).resolve().parent / "frozen_rule.json"
CONF = hc.OUT / "confirm"


def freeze():
    S = pl.read_parquet(hc.OUT / "settling_period.parquet")
    X = pl.read_parquet(hc.OUT / "readout_period.parquet")
    out = {"written": "2026-10-04", "source": "exploration (non-holdout replication periods)", "rules": {}}
    for model in ("bge_small", "gte_modernbert"):
        T = S.filter((pl.col("model") == model) & (pl.col("estimator") == "S1") & pl.col("detected").fill_null(False))
        D = X.join(T.select("goal_no", "tau"), on="goal_no").filter(pl.col("goal_no").is_in(hc.REPLICATION))
        y = np.log(D["tau"].to_numpy())
        r0, pred0 = L.lopo_rmse(y, None)
        res = y - pred0
        rules = {"constant": {"log_tau": float(y.mean()), "tau_h": float(np.exp(y.mean())),
                              "q10_resid": float(np.quantile(res, 0.1)), "q90_resid": float(np.quantile(res, 0.9))},
                 "n_exploration": int(len(y)), "periods": D["goal_no"].to_list()}
        for name, col in (("tmix_bulk", "tmix_batch_bulk"), ("T90_k5", "k5_room_T90")):
            x = np.log(D[col].to_numpy())
            b, a = np.polyfit(x, y, 1)
            rules[name] = {"column": col, "intercept": float(a), "slope": float(b)}
        out["rules"][model] = rules
    hc.save_json(FROZEN, out)
    print("frozen:", out)


def compute_unit(g: int, allow_holdout: bool, base: Path, suffix: str) -> dict:
    import readout as RO
    import settling as SE
    P = L.load_period(g, base=base, suffix=suffix)
    ro = P["roster"].filter(pl.col("on_day1"))
    agents = sorted(int(a) for a in ro["agent"].to_list())
    blocks = L.blocks_of(P["roster"])
    de = L.day_ends(g, allow_holdout)
    a2 = float(de[min(1, len(de) - 1)])
    a_max = float(de[min(hc.MAX_FIT_DAYS, len(de)) - 1])
    row, _ = RO.unit_predictors(P, agents, blocks, a2, a_max, seed=g, with_dg=False)
    reg = P["meta"]["regime"]
    st = P["stmts"].filter(~pl.col("pre_kick") & (pl.col("a") >= 0) & (pl.col("a") <= a_max))
    for model in SE.MODELS:
        k = SE.gvec(g, reg, model)
        if k is None:
            row[f"tau_{model}"], row[f"det_{model}"] = np.nan, False
            continue
        Dq = SE.decoys(g, reg, model)
        Z = np.asarray(SE.stmt_vectors(model)[st["srow"].to_numpy()], dtype=np.float64)
        f, _ = L.s1_fit(st["a"].to_numpy().astype(float), st["agent"].to_numpy(), Z, k, Dq, a_max)
        row[f"tau_{model}"] = f["tau"] if f else np.nan
        row[f"det_{model}"] = bool(f and f["detected"])
    row["goal_no"] = g
    return row


def evaluate(rows: list[dict], frozen: dict) -> dict:
    out = {}
    for model, R in frozen["rules"].items():
        d = [r for r in rows if r.get(f"det_{model}")]
        res = {"n_detected": len(d), "n_targets": len(rows)}
        if len(d) >= 3:
            y = np.log([r[f"tau_{model}"] for r in d])
            c = R["constant"]
            e0 = y - c["log_tau"]
            res["rmse_constant"] = float(np.sqrt(np.mean(e0 ** 2)))
            for name in ("tmix_bulk", "T90_k5"):
                x = np.log([r[R[name]["column"]] for r in d])
                e = y - (R[name]["intercept"] + R[name]["slope"] * x)
                res[f"rmse_{name}"] = float(np.sqrt(np.mean(e ** 2)))
            res["C1_pass"] = bool(res["rmse_tmix_bulk"] < res["rmse_constant"])
            res["C2_pass"] = bool(res["rmse_T90_k5"] < res["rmse_constant"])
            ratio = np.array([r[f"tau_{model}"] / r["k5_room_T90"] for r in d])
            res["C3_median_ratio"] = float(np.median(ratio))
            res["C3_pass"] = bool(1 / 3 <= np.median(ratio) <= 3)
            res["C4_coverage"] = float(np.mean((e0 >= c["q10_resid"]) & (e0 <= c["q90_resid"])))
            res["C4_pass"] = bool(res["C4_coverage"] >= 0.7)
        out[model] = res
    if all(k in out.get(m, {}) for m in out for k in ("C1_pass",)):
        out["gte_agrees_C1"] = out["bge_small"]["C1_pass"] == out["gte_modernbert"]["C1_pass"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.freeze:
        freeze()
    if a.dry_run:
        frozen = hc.load_json(FROZEN)
        rows = [compute_unit(g, False, hc.OUT, "") for g in STAND_INS]
        ev = evaluate(rows, frozen)
        hc.save_json(hc.OUT / "confirm_dryrun.json", {"stand_ins": STAND_INS, "rows": rows, "evaluation": ev,
                                                      "note": "stand-ins are exploration periods; no holdout data read"})
        print("dry run on stand-ins", STAND_INS, ev)
    if a.confirm:
        if not a.ack:
            sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
        import holdout_ledger as HL
        for g in TARGETS:
            chk = HL.check("H48", f"G{g:02d}", "content", "content_alignment")
            print(f"G{g:02d}: allowed={chk['allowed']} disclosure={chk['needs_disclosure']} "
                  f"prior_runs={[u['hypothesis'] for u in chk['prior_runs']]}")
            if not chk["allowed"]:
                sys.exit(f"G{g:02d} blocked by the reuse policy")
        frozen = hc.load_json(FROZEN)
        import build  # scheme/build.py
        CONF.mkdir(parents=True, exist_ok=True)
        build.build(TARGETS, allow_holdout=True, out=CONF)
        rows = [compute_unit(g, True, CONF, "_confirm") for g in TARGETS]
        ev = evaluate(rows, frozen)
        hc.save_json(CONF / "results.json", {"targets": TARGETS, "rows": rows, "evaluation": ev})
        print(ev)
        print("Record the run in the holdout ledger (holdout_ledger.record_run with H48's entry id), the card and LOG.md.")


if __name__ == "__main__":
    main()
