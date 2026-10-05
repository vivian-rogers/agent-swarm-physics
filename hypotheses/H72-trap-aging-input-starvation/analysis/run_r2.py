"""H72 round 2 on real data (non-reserved days only): R1 chatter hold on every eligible period, the reconcile
(held-out log scores of starvation, chatter and self-share against the aging clocks) on regime-III periods, G51 extras
and the frozen-slope transfer from G51 to the other regime-III periods.

Pre-registration and amendments: card, "Round 2". Validation: analysis/synthetic_r2.py.
Output: data/processed/H72-trap-aging-input-starvation/r2/results_r2.json
Usage: uv run python hypotheses/H72-trap-aging-input-starvation/analysis/run_r2.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

B_BOOT = 200
REG3_TARGETS = (37, 38, 40, 41, 44)


def est(P, model, term, extra=None, y=None):
    f = R.fit(P, model, extra=extra, y=y)
    return R.b(f, term)


def boot_terms(P, specs, seed):
    """specs: list of (name, model, term, extra_fn or None). One day-block bootstrap shared by all specs."""
    def fn(idx):
        Q = R.subset_idx(P, idx)
        out = []
        for _, m, t, ex in specs:
            f = R.fit(Q, m, extra=None if ex is None else ex(Q))
            out.append(f["beta"].get(t, np.nan))
        return np.array(out)
    D = R.boot(P, fn, B_BOOT, seed)
    return {nm: R.pct(D[:, j]) for j, (nm, *_rest) in enumerate(specs)}


def full_model(P):
    return "B+S+C+F+A" if P["F"] else "B+S+C+A"


def r1(P, goal):
    full = full_model(P)
    n_esc = int(P["y"].sum())
    res = {"n": P["n"], "n_escape": n_esc, "escape_rate": n_esc / P["n"], "full_model": full,
           "powered": bool(n_esc >= R.MIN_EVENTS and P["n"] - n_esc >= R.MIN_EVENTS)}
    if not res["powered"]:
        return res
    specs = [("bC_BAC", "B+A+C", "ln_dose", None), ("bC_full", full, "ln_dose", None),
             ("ba_full", full, "ln_a", None), ("bk_full", full, "ln_k", None), ("bs_full", full, "ln_s", None)]
    if P["F"]:
        specs.append(("bf_full", full, "lnq", None))
    pts = {nm: est(P, m, t) for nm, m, t, _ in specs}
    cis = boot_terms(P, specs, seed=goal)
    for nm in pts:
        res[nm] = {"est": pts[nm][0], "se": pts[nm][1], "ci": cis[nm]}
    res["rel_change_full_vs_BAC"] = 1 - pts["bC_full"][0] / pts["bC_BAC"][0] if pts["bC_BAC"][0] != 0 else None
    return res


def g51_extras(P):
    full = full_model(P)
    o = {}
    day_ex = lambda Q: {f"day_{int(x)}": (Q["day"] == x).astype(float) for x in np.unique(Q["day"])[1:]}  # noqa: E731
    specs = [("bC_dayfe", full, "ln_dose", day_ex),
             ("b_int", full, "int", lambda Q: {"int": Q["C"]["ln_dose"] * Q["dir_wake"]}),
             ("bC_with_inflight", full, "ln_dose", lambda Q: {"inflight": Q["inflight"]}),
             ("b_inflight", full, "inflight", lambda Q: {"inflight": Q["inflight"]}),
             ("bC_with_ddose", full, "ln_dose", lambda Q: {"ln_ddose": Q["D"]["ln_ddose"]}),
             ("b_ddose", full, "ln_ddose", lambda Q: {"ln_ddose": Q["D"]["ln_ddose"]}),
             ("bC_with_win", full, "ln_dose", lambda Q: {"ln_win5": Q["W"]["ln_win5"]})]
    pts = {nm: est(P, m, t, extra=ex(P)) for nm, m, t, ex in specs}
    cis = boot_terms(P, specs, seed=5101)
    for nm in pts:
        o[nm] = {"est": pts[nm][0], "se": pts[nm][1], "ci": cis[nm]}
    # first wakes only (k = 1)
    k1 = P["k"] == 1
    Q = R.subset(P, k1)
    pt = est(Q, full, "ln_dose")
    ci = boot_terms(Q, [("bC_k1", full, "ln_dose", None)], seed=5102)["bC_k1"]
    o["bC_k1"] = {"est": pt[0], "se": pt[1], "ci": ci, "n": Q["n"], "n_escape": int(Q["y"].sum())}
    # competing-rates form: slope on ln chatter rate, wakes with U5 >= 1
    m = np.isfinite(P["ln_rate"])
    Q = R.subset(P, m)
    ex = lambda Z: {"ln_rate": Z["ln_rate"]}  # noqa: E731
    pt = est(Q, "B+A", "ln_rate", extra=ex(Q))
    ci = boot_terms(Q, [("b_rate", "B+A", "ln_rate", ex)], seed=5103)["b_rate"]
    pt2 = est(Q, full.replace("+C", ""), "ln_rate", extra=ex(Q))
    ci2 = boot_terms(Q, [("b_rate_full", full.replace("+C", ""), "ln_rate", ex)], seed=5104)["b_rate_full"]
    o["b_rate"] = {"est": pt[0], "se": pt[1], "ci": ci, "n": Q["n"]}
    o["b_rate_full"] = {"est": pt2[0], "se": pt2[1], "ci": ci2, "n": Q["n"]}
    # dose windows and peer-only dose (descriptive), Wald
    o["variants"] = {}
    for dose in ("U3", "U10", "Upeer5"):
        Pv = R.prep(R.load_wakes(51), dose=dose)
        o["variants"][dose] = list(est(Pv, full, "ln_dose"))
    # bridge to H16: all wakes (consolidation-start traps kept), ln a only, with / without F
    Pa = R.prep(R.load_wakes(51, sample="all"))
    la = {"ln_a_only": Pa["A"]["ln_a"]}
    b0 = est(Pa, "B", "ln_a_only", extra=la)[0]
    b1 = est(Pa, "B+F", "ln_a_only", extra=la)[0]
    o["bridge_h16_all_wakes"] = {"n": Pa["n"], "beta_a_only": b0, "beta_a_with_F": b1, "rho_F": 1 - b1 / b0,
                                 "beta_C_full": list(est(Pa, full, "ln_dose"))}
    bq = est(P, "B", "ln_a_only", extra={"ln_a_only": P["A"]["ln_a"]})[0]
    bq1 = est(P, "B+F", "ln_a_only", extra={"ln_a_only": P["A"]["ln_a"]})[0]
    o["bridge_h16_primary"] = {"beta_a_only": bq, "beta_a_with_F": bq1, "rho_F": 1 - bq1 / bq}
    return o


def reconcile(P, seed):
    per = R.cv_per_day(P)
    st = R.cv_stats(per, P["n"], B=1000, seed=seed)
    # in-sample clock slopes with and without each mechanism (descriptive absorption)
    ins = {}
    for M in ("", "+S", "+C", "+F", "+S+C+F"):
        if "F" in M and not P["F"]:
            continue
        f = R.fit(P, f"B{M}+A")
        ins[f"B{M}+A"] = {"ln_a": R.b(f, "ln_a"), "ln_k": R.b(f, "ln_k")}
    return {"cv": st, "in_sample": ins, "per_day_ll": {k: v.tolist() for k, v in per.items()}}


def transfer_only():
    """Re-run the frozen-slope transfer only (amendment R2-A6, post hoc bug fix in r2lib.fit_offset)."""
    out = json.loads((R.R2 / "results_r2.json").read_text())
    Ps = {g: R.prep(R.load_wakes(g)) for g in (51, *REG3_TARGETS)}
    out["transfer"] = {}
    for tgt in REG3_TARGETS:
        out["transfer"][f"G{tgt:02d}"] = {fam: R.transfer(Ps[51], Ps[tgt], fam) for fam in ("S", "C", "F", "A")}
    out["transfer"]["G51_from_G38"] = {fam: R.transfer(Ps[38], Ps[51], fam) for fam in ("S", "C", "F", "A")}
    out["transfer_note"] = "R2-A6: fit_offset with step halving (post hoc bug fix; first version diverged)"
    R.jdump(out, R.R2 / "results_r2.json")
    print(json.dumps(out["transfer"]))


def main():
    if "--transfer-only" in sys.argv:
        return transfer_only()
    t0 = time.time()
    g = pl.read_parquet(R.R2 / "wakes_r2.parquet")
    goals = sorted(g["goal_no"].unique().to_list())
    out = {"r1": {}, "reconcile": {}, "transfer": {}}
    Ps = {}
    for goal in goals:
        P = R.prep(R.load_wakes(goal))
        Ps[goal] = P
        out["r1"][f"G{goal:02d}"] = r1(P, goal)
        x = out["r1"][f"G{goal:02d}"]
        print(f"G{goal:02d} n={P['n']} bC_full={x.get('bC_full', {}).get('est')} ci={x.get('bC_full', {}).get('ci')} "
              f"[{time.time() - t0:.0f}s]", flush=True)
        if x["powered"]:
            out["reconcile"][f"G{goal:02d}"] = reconcile(P, seed=goal)
        R.jdump(out, R.R2 / "results_r2.json")
    out["g51_extras"] = g51_extras(Ps[51])
    print("g51 extras done", f"[{time.time() - t0:.0f}s]", flush=True)
    for tgt in REG3_TARGETS:
        out["transfer"][f"G{tgt:02d}"] = {fam: R.transfer(Ps[51], Ps[tgt], fam) for fam in ("S", "C", "F", "A")}
    out["transfer"]["G51_from_G38"] = {fam: R.transfer(Ps[38], Ps[51], fam) for fam in ("S", "C", "F", "A")}
    R.jdump(out, R.R2 / "results_r2.json")
    print("done", f"[{time.time() - t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
