"""Post-hoc robustness (added 2026-10-03 after placebo_diag.py; NOT pre-registered).

Does the k-dilution survive controlling for dyadic engagement (i mentioned j at its previous talk turn)? Engaged
senders are mentioned 30-65% of the time whatever their status, and engagement may co-vary with k (active exchanges
mean frequent talk turns, hence small k). Fits per period, D1 and D2:
  M_pow vs M_pow_eng (S = w k^-beta e^{delta * engaged}); day-bootstrap CI of beta under M_pow_eng;
  within-day-block CV of pow, pow_eng, const_eng (is k still needed once engagement is in?);
  beta on the non-engaged units alone.
Writes data/processed/H18-attention-dilution/posthoc_engagement.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_periods import d2_units, summ  # noqa: E402
from h18lib import Units, cv, fit, paired_day_boot  # noqa: E402
from periods import PERIODS, gname  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H18-attention-dilution"
SH = ROOT / "data/processed/shared"


def mentions_by_msg():
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["mentions_roster"])
    m = pl.concat([chat, men], how="horizontal")
    return {int(i): set(x or []) for i, x in zip(m["msg"].to_list(), m["mentions_roster"].to_list())}


def prev_mentions(talks: pl.DataFrame, MB):
    """talk_id -> set of agents i mentioned at its previous talk turn (same day)."""
    t = talks.sort("agent", "t_us")
    out, last = {}, {}
    for r in t.iter_rows(named=True):
        key = (r["agent"], r["pt_date"])
        out[r["talk_id"]] = last.get(key, set())
        last[key] = MB.get(r["msg"], set())
    return out


def eng_flags(U: Units, id_col: str, pm: dict):
    ids = U.df[id_col].to_list()
    snd = U.df["sender"].to_list()
    return np.array([1.0 if s in pm.get(i, ()) else 0.0 for i, s in zip(ids, snd)])


def analyze(U: Units, rng, B):
    out = {"n": U.n, "share_engaged": float(U.eng.mean()),
           "rate_engaged": float(U.r[U.eng > 0].mean()) if (U.eng > 0).any() else None,
           "rate_not_engaged": float(U.r[U.eng == 0].mean())}
    fp = fit("pow", U)
    fe = fit("pow_eng", U)
    out["beta_pow"] = fp["params"]["beta"]
    out["beta_eng"] = fe["params"]["beta"]
    out["delta"] = fe["params"]["delta"]
    out["k_mean_engaged"] = float(U.k[U.eng > 0].mean()) if (U.eng > 0).any() else None
    out["k_mean_not_engaged"] = float(U.k[U.eng == 0].mean())
    bs = []
    for _ in range(B):
        Ub = U.resample_days(rng)
        if Ub.r.sum() >= 5:
            bs.append(fit("pow_eng", Ub, start=[fe["params"][k] for k in ("g", "beta", "delta")])["params"]["beta"])
    out["beta_eng_boot"] = summ(bs) if len(bs) > 5 else None
    ne = U.subset(U.eng == 0)
    if ne.r.sum() >= 10:
        fn = fit("pow", ne)
        bs2 = []
        for _ in range(B):
            Ub = ne.resample_days(rng)
            if Ub.r.sum() >= 5:
                bs2.append(fit("pow", Ub, start=[fn["params"]["g"], fn["params"]["beta"]])["params"]["beta"])
        out["beta_not_engaged"] = fn["params"]["beta"]
        out["beta_not_engaged_boot"] = summ(bs2) if len(bs2) > 5 else None
    if U.r.sum() >= 30:
        ll = cv(["pow", "pow_eng", "const_eng"], U, "block")
        out["cv"] = {m: float(np.nanmean(v)) for m, v in ll.items()}
        out["cv_poweng_vs_consteng"] = paired_day_boot(ll["pow_eng"], ll["const_eng"], U.day)
    return out


def main():
    MB = mentions_by_msg()
    rng = np.random.default_rng(18)
    res = {}
    for g in PERIODS:
        gp = gname(g)
        d = DATA / gp
        if not (d / "talks.parquet").exists():
            continue
        talks = pl.read_parquet(d / "talks.parquet")
        pend = pl.read_parquet(d / "pending.parquet")
        pm = prev_mentions(talks, MB)
        U = Units(talks, pend, "talk_id")
        U.eng = eng_flags(U, "talk_id", pm)
        B = 100 if U.n < 100000 else 25
        r = {"D1": analyze(U, rng, B)}
        # D2: engagement = i mentioned j at its last talk before the pause
        wk = d / "wakes.parquet"
        if wk.exists() and g in (36, 37, 38, 39, 40, 41, 42, 44, 51):
            wakes = pl.read_parquet(wk)
            wp = pl.read_parquet(d / "wake_pending.parquet")
            U2 = d2_units(wakes, wp, 300.0)
            if U2.n >= 200 and U2.r.sum() >= 10:
                t = talks.select("agent", "pt_date", "t_us", "msg").sort("agent", "t_us")
                last_m = {}
                tw = wakes.select("wake_id", "agent", "pt_date", "t_pause_us").sort("agent", "t_pause_us")
                # last talk before the pause, same day
                tt = {}
                for (a, dd), sub in t.group_by(["agent", "pt_date"], maintain_order=True):
                    tt[(a, dd)] = (sub["t_us"].to_numpy(), sub["msg"].to_list())
                for row in tw.iter_rows(named=True):
                    arr = tt.get((row["agent"], row["pt_date"]))
                    if arr is None:
                        last_m[row["wake_id"]] = set()
                        continue
                    j = np.searchsorted(arr[0], row["t_pause_us"]) - 1
                    last_m[row["wake_id"]] = MB.get(arr[1][j], set()) if j >= 0 else set()
                U2.eng = eng_flags(U2, "wake_id", last_m)
                r["D2"] = analyze(U2, rng, B)
        res[gp] = r
        d1 = r["D1"]
        print(gp, f"beta {d1['beta_pow']:.2f} -> eng-controlled {d1['beta_eng']:.2f} (delta {d1['delta']:.2f}); "
                  f"non-engaged only {d1.get('beta_not_engaged', float('nan')):.2f}; share eng {d1['share_engaged']:.2f}; "
                  f"k eng/non {d1['k_mean_engaged']:.1f}/{d1['k_mean_not_engaged']:.1f}"
              + (f" | D2 {r['D2']['beta_pow']:.2f} -> {r['D2']['beta_eng']:.2f}" if "D2" in r else ""), flush=True)
        (DATA / "posthoc_engagement.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
