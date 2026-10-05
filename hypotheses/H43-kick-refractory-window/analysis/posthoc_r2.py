"""H43 round 2 post hoc checks (not pre-registered; written after the R2, R5 and R6 results).

  P1 (R2)  Why does the wake model give a large first-nudge effect when round 1 found none? Same wakes, round-1 outcome
           (a sustained run start, rule h43_gap, within 15 min of the wake), base and proxy models.
  P2 (R2)  Depth or re-fire? First nudges and same-trap re-fires by wake-index band (raw escape at nudged and un-nudged
           wakes in the same band).
  P3 (R6)  What carries the cadence drop? Declared pause length and wake index by segment (agent FE, OLS on logs).

Output: data/processed/H43-kick-refractory-window/r2/posthoc_r2.json
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402
from run_r2 import b_of, boot_fit, d_of, daycodes  # noqa: E402


def o1_15(w: pl.DataFrame) -> np.ndarray:
    ss = R.sustained_starts((51,))
    out = np.zeros(w.height, bool)
    for (a, d), sub in ss.group_by(["agent", "pt_date"]):
        ts = np.sort(sub["t_start"].to_numpy())
        m = ((w["agent"] == a) & (w["pt_date"] == d)).to_numpy()
        if not m.any():
            continue
        t = w["t_call"].to_numpy()[m]
        j = np.searchsorted(ts, t - 1e-6, "left")
        ok = j < len(ts)
        v = np.zeros(m.sum(), bool)
        v[ok] = ts[j[ok]] <= t[ok] + 900
        out[m] = v
    return out


def agent_fe_ols(y, X, agent, w=None):
    lev = np.unique(agent)
    Z = np.column_stack([np.ones(len(y)), X] + [(agent == a).astype(float) for a in lev[1:]])
    w = np.ones(len(y)) if w is None else w
    b = np.linalg.lstsq(Z * np.sqrt(w)[:, None], y * np.sqrt(w), rcond=None)[0]
    return b[1:1 + X.shape[1]]


def main():
    rng = np.random.default_rng(R.SEED + 99)
    t0 = time.time()
    out = {}
    # ---------------------------------------------------------------- P1
    w = R.add_nudge_history(R.load_wakes((51,), date_to=R.NE43))
    yo = o1_15(w).astype(float)
    ag, day = w["agent"].to_numpy(), daycodes(w)
    st, N = w["nprev_state"].to_numpy(), w["N_now"].to_numpy()
    p1 = {"rates_O1_15": {f"{s}|{int(n)}": float(yo[(st == s) & (N == n)].mean()) for s in (0, 1, 2) for n in (0, 1)}}
    for lab, kw in (("base", {}), ("proxy", {"proxies": True})):
        X, nm = R.r2_design(w, **kw)
        stats = {"dF": d_of("N_refire", "N_first", nm), "g_first": b_of("N_first", nm), "g_refire": b_of("N_refire", nm)}
        _, s = boot_fit(X, yo, ag, day, rng, 200, stats)
        p1[lab] = s
        print(f"P1 O1_15 {lab}: first {s['g_first']['est']:+.3f} {np.round(s['g_first']['ci'], 2)} refire {s['g_refire']['est']:+.3f} "
              f"dF {s['dF']['est']:+.3f} {np.round(s['dF']['ci'], 2)}", flush=True)
    # without ln k and trap age (round-1-like matching on idle age bins only is coarser): base model minus trap clocks
    X, nm = R.r2_design(w)
    drop = [nm.index(c) for c in ("ln_k", "ln_age_min", "no_sus")]
    Xd = np.delete(X, drop, axis=1)
    nmd = [c for i, c in enumerate(nm) if i not in drop]
    for lab, yy in (("y_sus", w["y_sus"].to_numpy().astype(float)), ("O1_15", yo)):
        f = R.fe_logit(Xd, yy, ag)
        p1[f"no_trap_clock_{lab}"] = {"g_first": float(f["beta"][nmd.index("N_first")]), "g_refire": float(f["beta"][nmd.index("N_refire")])}
        print(f"P1 no trap clocks, {lab}: first {p1[f'no_trap_clock_{lab}']['g_first']:+.3f} refire {p1[f'no_trap_clock_{lab}']['g_refire']:+.3f}",
              flush=True)
    out["P1"] = p1
    # ---------------------------------------------------------------- P2
    y = w["y_sus"].to_numpy()
    k = w["k"].to_numpy()
    bands = [(1, 2), (2, 5), (5, 10), (10, 30), (30, 1e9)]
    p2 = {}
    for lo, hi in bands:
        m = (k >= lo) & (k < hi)
        row = {}
        for lab, sel in (("first", N & (st == 0)), ("refire_same", N & (st == 1)), ("refire_new", N & (st == 2)),
                         ("none_state0", ~N & (st == 0)), ("none_state1", ~N & (st == 1)), ("none_state2", ~N & (st == 2))):
            mm = m & sel
            row[lab] = {"n": int(mm.sum()), "rate": float(y[mm].mean()) if mm.any() else None}
        p2[f"{lo}-{int(hi) if hi < 1e8 else 'inf'}"] = row
    out["P2"] = p2
    for kb, row in p2.items():
        print("P2 k", kb, {lab: (v["n"], None if v["rate"] is None else round(v["rate"], 3)) for lab, v in row.items()}, flush=True)
    # ---------------------------------------------------------------- P3
    w6 = R.load_wakes((51,), date_from=R.PRE_WIN[0], date_to=R.POST_WIN[1])
    seg = {"S1_0821": ("2026-08-21", "2026-08-22"), "S2_0824_0827": ("2026-08-24", "2026-08-28"),
           "S3_0828_0902": ("2026-08-28", "2026-09-03"), "S4_0903_0904": ("2026-09-03", "2026-09-05")}
    S = np.column_stack([((w6["pt_date"] >= a) & (w6["pt_date"] < b)).to_numpy().astype(float) for a, b in seg.values()])
    ag6 = w6["agent"].to_numpy()
    p3 = {}
    for lab, v in (("ln_declared_pause", np.log(w6["prev_pause_s"].fill_null(180.0).to_numpy().clip(10, None))),
                   ("ln_k", np.log(w6["k"].to_numpy())), ("ln_trap_age", np.log(w6["age_s"].to_numpy() / 60))):
        b = agent_fe_ols(v, S, ag6)
        p3[lab] = dict(zip(seg, b.tolist()))
    pre = (w6["pt_date"] < R.NE43).to_numpy()
    pp = w6["prev_pause_s"].fill_null(180.0).to_numpy()
    p3["median_declared_pause_s"] = {"pre": float(np.median(pp[pre])), **{k_: float(np.median(pp[S[:, i] > 0])) for i, k_ in enumerate(seg)}}
    p3["share_pause_ge_600s"] = {"pre": float((pp[pre] >= 600).mean()), **{k_: float((pp[S[:, i] > 0] >= 600).mean()) for i, k_ in enumerate(seg)}}
    out["P3"] = p3
    print("P3", {k_: {s_: round(x, 3) for s_, x in v.items()} for k_, v in p3.items()}, flush=True)
    out["secs"] = round(time.time() - t0, 1)
    out["built_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    R.jdump(out, R.OUT / "posthoc_r2.json")


if __name__ == "__main__":
    main()
