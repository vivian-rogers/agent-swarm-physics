"""H16 round 2 POST HOC checks (written after the first real-data gate results; labelled post hoc on the card).

  P1  forced-reset step with a shifted outcome: the three calls after the gate call are all active (skips the gate
      call, which a scaffold mouse move can fill after a consolidation; infra Known issue "scaffold artifacts").
  P2  absorption with ln(gate index k) added: does the own-call share (U-call) still absorb aging when the gate count
      is in the model?
  P4  calibration of the agent x kind x last_kind x day mixture null (a stress variant that was not pre-registered):
      on the real G51 deep skeleton, worlds with true within-cell aging (-0.5) and with none; does the day-cell null
      reproduce the aging of a true aging world (i.e. is it fitted to the outcome)?
  P3  urn-implied reset step and kick effects at the observed escape level (U-call urn on the real G51 skeleton,
      sequential within traps; the A1 models). Compared with the observed step and kick.
Output: data/processed/H16-metastable-traps-kramers/r2/posthoc_r2.json
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402


def shifted_outcome(g: pl.DataFrame) -> np.ndarray:
    cc = pl.read_parquet(R.R2 / "calls_comp.parquet", columns=["turn_id", "agent", "pt_date", "t_call", "idle"]).sort("agent", "t_call", "turn_id")
    cc = cc.with_columns([pl.col("idle").shift(-i).over("agent", "pt_date").alias(f"i{i}") for i in (1, 2, 3)])
    cc = cc.with_columns(y_shift=pl.when(pl.col("i3").is_not_null()).then(~pl.col("i1") & ~pl.col("i2") & ~pl.col("i3")).otherwise(None))
    j = g.select("turn_id").join(cc.select("turn_id", "y_shift"), on="turn_id", how="left")
    return j["y_shift"].to_numpy()


def main():
    rng = np.random.default_rng(R.SEED + 20)
    out = {}
    g = R.prep_gates(pl.read_parquet(R.R2 / "gates_r2.parquet").filter(pl.col("goal_no") == 51))
    days = np.unique(np.array(g["pt_date"].to_list()), return_inverse=True)[1]
    y = g["y_sus"].to_numpy().astype(np.int8)
    ag = g["agent"].to_numpy()
    X0 = R.nuisance(g)
    lnk = np.log(g["k_sus"].to_numpy().astype(float))
    fo = g["forced"].to_numpy().astype(float); vo = g["vol"].to_numpy().astype(float)
    # gate-call kind after forced resets
    out["forced_gate_kind"] = g.filter(pl.col("forced")).group_by("kind").len().sort("len", descending=True).to_dicts()
    out["forced_escape_rate"] = float(y[fo > 0].mean()); out["other_escape_rate"] = float(y[(fo == 0) & (vo == 0)].mean())
    # P1
    ys = shifted_outcome(g)
    ok = np.array([v is not None for v in ys])
    ysv = np.array([bool(v) if v is not None else False for v in ys]).astype(np.int8)
    X = np.column_stack([X0, lnk, fo, vo])[ok]

    def fit_step(idx):
        f = R.fe_logit(ysv[ok][idx], X[idx], ag[ok][idx])
        return f["beta"][X.shape[1] - 2]
    f = R.fe_logit(ysv[ok], X, ag[ok])
    bs = R.day_boot(lambda idx: fit_step(idx), days[ok], 200, rng)
    out["P1_shifted"] = {"forced": float(f["beta"][X.shape[1] - 2]), "se": float(f["se"][X.shape[1] - 2]), "ci": R.pct_ci(bs),
                         "vol": float(f["beta"][X.shape[1] - 1]), "n": int(ok.sum()), "forced_rate_shift": float(ysv[ok][fo[ok] > 0].mean())}
    # P2
    f_call = g["f_call"].to_numpy().astype(float)
    okf = np.isfinite(f_call)
    Xa = np.column_stack([X0, lnk])[okf]
    Xb = np.column_stack([X0, lnk, R.lnq(f_call)])[okf]

    def p2(idx):
        a = R.fe_logit(y[okf][idx], Xa[idx], ag[okf][idx])["beta"]
        b = R.fe_logit(y[okf][idx], Xb[idx], ag[okf][idx])["beta"]
        return [a[0], b[0], b[-1], a[-1], b[-2]]
    pt = p2(np.arange(okf.sum()))
    bs = R.day_boot(p2, days[okf], 200, rng)
    out["P2_with_lnk"] = {"beta_a_noF": pt[0], "beta_a_withF": pt[1], "beta_f": pt[2], "beta_lnk_noF": pt[3], "beta_lnk_withF": pt[4],
                          "ci_beta_a_withF": R.pct_ci(bs[:, 1]), "ci_beta_f": R.pct_ci(bs[:, 2]), "ci_beta_lnk_withF": R.pct_ci(bs[:, 4])}
    # P3: urn-implied step and kick at the observed level
    st, en = R.trap_index(g)
    fz = np.nan_to_num(f_call, nan=0.0)
    p = R.urn_prob(fz, ag, float(y.mean()))
    rows = []
    for _ in range(40):
        keep, ys_ = R.simulate_traps(rng, p, st, en)
        o = R.flat(R.gate_models(g.filter(pl.Series(keep)), ys_[keep], urn_cols=("f_call",), parts=("reset", "kick")))
        rows.append(o)
    for k in ("reset.forced", "kick.dir", "kick.undir", "kick.diff", "beta_a0"):
        v = np.array([r[k][0] for r in rows])
        out.setdefault("P3_urn_implied", {})[k] = {"mean": float(v.mean()), "q": R.pct_ci(v)}
    # P4
    H = R.ts1r_deep("G51")
    dc = R.cell_codes(H, cols=("kind_start", "last_kind", "day"))
    cc = R.cell_codes(H)
    for w, b in (("aging_-0.5", -0.5), ("no_aging", 0.0)):
        rec = []
        for _ in range(4):
            al = np.log(0.02) + rng.standard_normal(dc.max() + 1)
            eta = al[dc] + b * (H["lnel"] - np.log(10.0))
            h = -np.expm1(-np.exp(np.clip(eta, -30, 3)))
            ys_ = (rng.random(len(h)) < h).astype(np.int8)
            obs = R.slope_cloglog(ys_, H["lnel"], H["agent"])[0]
            nd = R.mixture_null(rng, H, ys_, dc, sims=20)
            nc = R.mixture_null(rng, H, ys_, cc, sims=20)
            rec.append({"obs": obs, "null_day_mean": float(nd.mean()), "null_cell_mean": float(nc.mean())})
        out.setdefault("P4_day_null_calibration", {})[w] = rec
    R.jdump(out, R.R2 / "posthoc_r2.json")
    print(out)


if __name__ == "__main__" and "--p5" not in sys.argv:
    main()


def p5():
    """P5 (post hoc): does escape after a forced reset still fall with gate index k (frailty: yes; context-held: flat)?
    Logit with agent FE on ln k + nuisance, within forced-reset gates vs within no-reset gates; and the forced x ln k
    interaction in the pooled A1 model."""
    rng = np.random.default_rng(R.SEED + 21)
    g = R.prep_gates(pl.read_parquet(R.R2 / "gates_r2.parquet").filter(pl.col("goal_no") == 51))
    days = np.unique(np.array(g["pt_date"].to_list()), return_inverse=True)[1]
    y = g["y_sus"].to_numpy().astype(np.int8); ag = g["agent"].to_numpy()
    X0 = R.nuisance(g); lnk = np.log(g["k_sus"].to_numpy().astype(float))
    fo = g["forced"].to_numpy().astype(float); vo = g["vol"].to_numpy().astype(float)
    X = np.column_stack([X0, lnk, fo, vo, fo * (lnk - lnk[fo > 0].mean())])

    def inter(idx):
        return R.fe_logit(y[idx], X[idx], ag[idx])["beta"][[5, 6, 8]]
    pt = inter(np.arange(len(y)))
    bs = R.day_boot(inter, days, 200, rng)
    out = {"lnk_noreset": float(pt[0]), "forced_at_mean_lnk": float(pt[1]), "forced_x_lnk": float(pt[2]),
           "ci_lnk": R.pct_ci(bs[:, 0]), "ci_forced": R.pct_ci(bs[:, 1]), "ci_forced_x_lnk": R.pct_ci(bs[:, 2])}
    k = g["k_sus"].to_numpy()
    out["rates"] = {f"{lab}": {"forced": float(y[(fo > 0) & m].mean()) if ((fo > 0) & m).sum() else None, "n_forced": int(((fo > 0) & m).sum()),
                               "noreset": float(y[(fo == 0) & (vo == 0) & m].mean())}
                    for lab, m in (("k1", k == 1), ("k2_4", (k >= 2) & (k <= 4)), ("k5p", k >= 5))}
    import json
    p = R.R2 / "posthoc_r2.json"
    d = json.loads(p.read_text()); d["P5_reset_by_k"] = out
    R.jdump(d, p)
    print(out)


if __name__ == "__main__" and "--p5" in sys.argv:
    p5()
