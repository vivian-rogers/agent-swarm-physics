"""R6 graph clause: event study on the relay read inside C's call clock (card "Round 2", R6).
--synth: synthetic talk outcomes on the real skeleton (#51b, #38a, #27, #51c): W0 no coupling, W1 gated per-read
coupling at round-1 sizes, W2 one-call dead time. --real: every eligible non-reserved unit.
Writes r2/synthetic_relay.json, r2/relay_units.parquet, r2/relay_summary.json.

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/r2_relay.py --synth [--seeds 5]
       uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/r2_relay.py --real
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import h50lib as L  # noqa: E402
import r2lib as R2  # noqa: E402
from build import load_unit  # noqa: E402
from common import holdout_mask  # noqa: E402

OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
SIZES = {"III": dict(J=0.06, J_named=1.5), "I": dict(J=0.2, J_named=0.3)}
WORLDS = {"W0_null": dict(J=0.0, J_named=0.0), "W1_gated": {}, "W2_dead1": dict(dead=1)}
COMMON = dict(phi=1.0, ou_sig=0.5, ou_tau=900.0, tau_h=1.0, K=5)


def load(u):
    U = load_unit(OUT / "units" / f"{u}.npz")
    U["N"] = int(U["N"])
    days = [str(d) for d in U["days"]]
    assert not any(holdout_mask(days, [int(U["goal_no"])] * len(days)))
    return U, R2.load_r2(OUT / "r2/units" / f"{u}.npz")


def analyse(U, P, y, R, nboot=200, seed=0):
    # Amendment R6-A1 (synthetic, before real data): 1-hour blocks in every unit (day blocks in 5-day units gave
    # anti-conservative CIs), and controls for the other items read at the outcome call and the call before.
    blk, nblk = R2.blocks_for(U, P["tA"], P["day"], min_days=None)
    S = R2.read_counts(U, R)
    res = {}
    treated = (P["rho"] >= 2) & (P["rho"] <= 5)
    for lab, sel in (("treated", treated), ("with_never", treated | (P["rho"] == 0)),
                     ("named", treated & P["named"]), ("unnamed", treated & ~P["named"])):
        if sel.sum() < 50:
            res[lab] = None
            continue
        pan = R2.relay_panel(U, P, y, sel)
        res[lab] = R2.event_study(pan, blk, nblk, nboot=nboot, seed=seed, Xc=R2.panel_controls(U, P, pan, S))
        if lab == "treated":
            res["raw"] = R2.event_study(pan, blk, nblk, nboot=nboot, seed=seed)
    return res


def synth(seeds):
    out = {}
    for u in ("51b", "38a", "27", "51c"):
        U, R = load(u)
        reg = str(U["regime"])
        P = R2.relay_pairs(U, R)
        treated = (P["rho"] >= 2) & (P["rho"] <= 5)
        print(u, "pairs", len(P["A"]), "treated", int(treated.sum()), "rho dist", np.bincount(P["rho"], minlength=7).tolist(), flush=True)
        for w, wp in WORLDS.items():
            prm = dict(COMMON, **SIZES[reg if reg in SIZES else "III"])
            prm.update(wp)
            key = f"{u}|{w}"
            out[key] = []
            for sd in range(seeds):
                t0 = time.time()
                y, truth = R2.syn_talk(U, R, prm, seed=200 + sd)
                r = analyse(U, P, y.astype(float), R, nboot=100, seed=sd)
                tv = np.array([truth.get((int(m), int(cc)), np.nan) for m, cc in zip(P["relay"][treated], P["C"][treated])])
                r["truth_G"] = float(np.nanmean(tv)) if np.isfinite(tv).any() else 0.0
                tn = treated & P["named"]
                tv = np.array([truth.get((int(m), int(cc)), np.nan) for m, cc in zip(P["relay"][tn], P["C"][tn])])
                r["truth_G_named"] = float(np.nanmean(tv)) if np.isfinite(tv).any() else 0.0
                out[key].append({k: (v if not isinstance(v, dict) else {str(kk): vv for kk, vv in v.items()}) for k, v in r.items()})
                t = r["treated"]
                print(f"{key} s{sd} {time.time() - t0:.0f}s G {t[0][0]:.4f} [{t[0][1]:.4f},{t[0][2]:.4f}] raw {r['raw'][0][0]:.4f} g-2 {t[-2][0]:.4f} "
                      f"g+1 {t[1][0]:.4f} truth {r['truth_G']:.4f} | named {r['named'][0][0] if r['named'] else float('nan'):.4f} "
                      f"(t {r['truth_G_named']:.4f})", flush=True)
            (OUT / "r2/synthetic_relay.json").write_text(json.dumps(out))


def real():
    units = pl.read_parquet(OUT / "units.parquet").filter(pl.col("eligible") & (pl.col("kind") == "period_unit"))
    rows = []
    for u, reg, g in zip(units["unit"], units["regime"], units["goal_no"]):
        U, R = load(u)
        P = R2.relay_pairs(U, R)
        y = U["calls"]["talk"].astype(float)
        treated = (P["rho"] >= 2) & (P["rho"] <= 5)
        base = dict(unit=u, regime=reg, goal_no=int(g), n_pairs=len(P["A"]), n_treated=int(treated.sum()),
                    **{f"rho{k}": int((P["rho"] == k).sum()) for k in range(0, 7)})
        if treated.sum() < 200:
            rows.append(dict(base, eligible=False))
            print(u, "not eligible", int(treated.sum()), flush=True)
            continue
        r = analyse(U, P, y, R, nboot=200, seed=3)
        row = dict(base, eligible=True)
        for lab in ("treated", "with_never", "named", "unnamed", "raw"):
            if r[lab] is None:
                continue
            for ev in (-3, -2, 0, 1, 2):
                e, lo, hi, se = r[lab][ev]
                row[f"{lab}_g{ev}"], row[f"{lab}_g{ev}_lo"], row[f"{lab}_g{ev}_hi"], row[f"{lab}_g{ev}_se"] = e, lo, hi, se
            row[f"{lab}_n"] = r[lab]["n_pairs"]
        # the standard gate of the relay messages at C (RD on the relay posting time), for comparison
        sel = treated
        te = R["m_t"][P["relay"][sel]]
        gk = L.gate_kernel(U, L.call_keys(U), te, P["day"][sel], P["C"][sel], y, K=1,
                           W=1.5 * L.median_call_interval(U), nboot=200)
        row["relay_gate_J1"], row["relay_gate_lo"], row["relay_gate_hi"] = float(gk["jumps"][0]), float(gk["j_lo"][0]), float(gk["j_hi"][0])
        row["relay_gate_se"] = float(gk["k_se"][0])
        rows.append(row)
        t = r["treated"]
        print(f"{u} ({reg}) treated {int(treated.sum())} G {t[0][0]:.4f} [{t[0][1]:.4f},{t[0][2]:.4f}] g-2 {t[-2][0]:.4f} "
              f"g+1 {t[1][0]:.4f} relay-gate {row['relay_gate_J1']:.4f}", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(OUT / "r2/relay_units.parquet")
    summ = {}
    el = df.filter(pl.col("eligible"))
    for reg in ("I", "II", "III"):
        s = el.filter(pl.col("regime") == reg)
        if not len(s):
            continue
        d = dict(n_units=len(s), rho_dist=[int(s[f"rho{k}"].sum()) for k in range(7)])
        for lab in ("treated", "with_never", "named", "unnamed", "raw"):
            for ev in (-3, -2, 0, 1, 2):
                col = f"{lab}_g{ev}"
                if col not in s.columns:
                    continue
                ss = s.filter(pl.col(col).is_not_null())
                m, se = R2.ivw(ss[col].to_numpy(), ss[col + "_se"].to_numpy())
                d[col] = (m, se, int((ss[col + "_lo"] > 0).sum()), int((ss[col + "_hi"] < 0).sum()), len(ss))
        m, se = R2.ivw(s["relay_gate_J1"].to_numpy(), s["relay_gate_se"].to_numpy())
        d["relay_gate_J1"] = (m, se)
        summ[reg] = d
        print(reg, json.dumps({k: v for k, v in d.items()}, default=float))
    (OUT / "r2/relay_summary.json").write_text(json.dumps(summ, indent=1, default=float))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synth", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--seeds", type=int, default=5)
    a = ap.parse_args()
    if a.synth:
        synth(a.seeds)
    if a.real:
        real()


if __name__ == "__main__":
    main()
