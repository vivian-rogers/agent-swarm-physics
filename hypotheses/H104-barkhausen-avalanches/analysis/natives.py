"""H104 natives (predictions in goalperiod-subhypotheses/{NE38,NE43,G44}/README.md, written before running).

NE38  the 07-29 human session that reassigns agent 40 (first session after 16:40 UTC); W = 120 min. (a) does the target
      switch; (b) do other at-risk agents switch beyond the time-shuffle null (central 90%)?
NE43  switches per agent-hour at risk, 5 active days to 08-20 vs 5 from 08-21; placebo splits across #51.
G44   room locality: excess switching per at-risk agent in the posting room vs the other room.

    uv run python hypotheses/H104-barkhausen-avalanches/analysis/natives.py
Output: data/processed/H104-barkhausen-avalanches/results/natives.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h104lib as L  # noqa: E402

SH = L.ROOT / "data/processed/shared"
RES = L.DATA / "results"
EPOCH = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)


def ts(x: dt.datetime) -> float:
    return (x - EPOCH).total_seconds()


def pair_counts(pan: L.Panel, t_sw: np.ndarray) -> np.ndarray:
    x = t_sw[pan.e_sw]
    tw = pan.t0[pan.pair_win[pan.e_pair]]
    inw = (x > tw) & (x <= tw + pan.W)
    return np.bincount(pan.e_pair, weights=inw, minlength=len(pan.pair_ad)) > 0


def ne38() -> dict:
    P = L.load_period(51)
    st = P["steps"].filter(pl.col("pt_date") == "2026-07-29").sort("t")
    t_lo = ts(dt.datetime(2026, 7, 29, 16, 40, tzinfo=dt.timezone.utc))
    st = st.filter(pl.col("t") >= t_lo)
    if st.height == 0:
        return {"testable": False}
    step = st.row(0, named=True)
    W = 7200.0
    out = {"t_step_utc": (EPOCH + dt.timedelta(seconds=step["t"])).isoformat(), "m": step["m"], "W_min": 120}
    rc = P["step_receipts"].filter(pl.col("session") == step["session"])
    out["target_read"] = bool((rc["agent"] == 40).any())
    for ch in ("work", "attn"):
        ad = L.agent_days(P, "span")
        sw = L.switches_in(P, ch, ad)
        raw = P[f"switches_{ch}"]
        tgt = raw.filter((pl.col("agent") == 40) & (pl.col("t") > step["t"]) & (pl.col("t") <= step["t"] + W))
        pan = L.Panel(ad, sw, np.array([step["t"]]), W, np.array([step["pt_date"]]))
        others = pan.ad_agent[pan.pair_ad] != 40
        obs = pair_counts(pan, pan.sw_t)
        rng = np.random.default_rng(38)
        nul = np.array([(pair_counts(pan, pan.rotate(rng)) & others).sum() for _ in range(999)])
        k = int((obs & others).sum())
        out[ch] = {"target_switch": tgt.height > 0, "target_at_risk": bool((pan.ad_agent[pan.pair_ad] == 40).any()),
                   "others_switching": k, "others_at_risk": int(others.sum()),
                   "null_q05": float(np.percentile(nul, 5)), "null_q95": float(np.percentile(nul, 95)),
                   "null_mean": float(nul.mean()), "pct": float(np.mean(nul < k) + 0.5 * np.mean(nul == k))}
    out["a_pass"] = bool(out["work"]["target_switch"] or out["attn"]["target_switch"])
    out["b_pass"] = all(out[ch]["null_q05"] <= out[ch]["others_switching"] <= out[ch]["null_q95"] for ch in ("work", "attn"))
    return out


def rates_by_day(P, ch):
    ad = L.agent_days(P, "span")
    sw = L.switches_in(P, ch, ad)
    hrs = ad.with_columns(((pl.col("risk_hi") - pl.col("risk_lo")) / 3600).alias("h")).group_by("pt_date").agg(pl.col("h").sum())
    n = sw.group_by("pt_date").len()
    return hrs.join(n, on="pt_date", how="left").with_columns(pl.col("len").fill_null(0)).sort("pt_date")


def ratio(dfb, dfa, rng=None):
    if rng is not None:
        dfb = dfb[rng.integers(0, dfb.height, dfb.height)]
        dfa = dfa[rng.integers(0, dfa.height, dfa.height)]
    return (dfa["len"].sum() / dfa["h"].sum()) / (dfb["len"].sum() / dfb["h"].sum())


def ne43() -> dict:
    P = L.load_period(51)
    out = {}
    for ch in ("work", "attn"):
        R = rates_by_day(P, ch)
        days = R["pt_date"].to_list()
        k = sum(d <= "2026-08-20" for d in days)
        b, a = R[k - 5:k], R[k:k + 5]
        obs = ratio(b, a)
        rng = np.random.default_rng(43)
        bs = np.array([ratio(b, a, rng) for _ in range(2000)])
        plc = []
        for s in range(5, len(days) - 4):
            d0 = days[s]
            if abs((dt.date.fromisoformat(d0) - dt.date(2026, 7, 29)).days) <= 7 or abs((dt.date.fromisoformat(d0) - dt.date(2026, 8, 21)).days) <= 7:
                continue
            plc.append(ratio(R[s - 5:s], R[s:s + 5]))
        plc = np.asarray(plc)
        out[ch] = {"ratio": float(obs), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                   "before_days": b["pt_date"].to_list(), "after_days": a["pt_date"].to_list(),
                   "rate_before": float(b["len"].sum() / b["h"].sum()), "rate_after": float(a["len"].sum() / a["h"].sum()),
                   "placebo_n": len(plc), "placebo_q05": float(np.percentile(plc, 5)) if len(plc) else None,
                   "placebo_q95": float(np.percentile(plc, 95)) if len(plc) else None,
                   "placebo_pct": float(np.mean(plc < obs)) if len(plc) else None}
        out[ch]["a_pass"] = bool(0.85 <= obs <= 1.15 and out[ch]["ci"][0] <= 1 <= out[ch]["ci"][1])
        out[ch]["b_pass"] = bool(len(plc) and out[ch]["placebo_q05"] <= obs <= out[ch]["placebo_q95"])
    return out


def g44() -> dict:
    P = L.load_period(44)
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").with_columns(
        pl.col("t_end").fill_null(dt.datetime(2030, 1, 1, tzinfo=dt.timezone.utc)))
    out = {}
    W = 3600.0
    for ch in ("work", "attn"):
        ad = L.agent_days(P, "span")
        sw = L.switches_in(P, ch, ad)
        st = L.eligible_steps(P, ad, W)
        variant = "isolated"
        if st.height < 3:   # Amendment A1: too few isolated steps in #44 -> all-steps variant
            st = L.eligible_steps(P, ad, W, isolated=False)
            variant = "all steps"
        if st.height < 3 or sw.height < 30:
            out[ch] = {"testable": False, "n_steps": st.height, "variant": variant}
            continue
        pan = L.Panel(ad, sw, st["t"].to_numpy(), W, st["pt_date"].to_numpy())
        obs = pair_counts(pan, pan.sw_t).astype(float)
        rng = np.random.default_rng(44)
        nul = np.mean([pair_counts(pan, pan.rotate(rng)) for _ in range(999)], axis=0)
        # agent room at the step time
        rooms = st["room"].to_numpy()
        same = np.zeros(len(pan.pair_ad), bool)
        for p_, (w, a) in enumerate(zip(pan.pair_win, pan.pair_ad)):
            t = EPOCH + dt.timedelta(seconds=float(pan.t0[w]))
            r = rt.filter((pl.col("agent") == int(pan.ad_agent[a])) & (pl.col("t_start") <= t) & (pl.col("t_end") > t))
            same[p_] = r.height > 0 and int(r["room"][0]) == int(rooms[w])
        ex_in = float((obs[same] - nul[same]).mean()) if same.any() else np.nan
        ex_out = float((obs[~same] - nul[~same]).mean()) if (~same).any() else np.nan
        tot = float((obs - nul).sum())
        out[ch] = {"testable": True, "variant": variant, "n_steps": st.height, "excess_total": tot, "X": float(obs.sum() / nul.sum()),
                   "excess_in_room_per_agent": ex_in, "excess_other_room_per_agent": ex_out,
                   "n_in": int(same.sum()), "n_out": int((~same).sum())}
    return out


def main():
    RES.mkdir(parents=True, exist_ok=True)
    res = {"NE38": ne38(), "NE43": ne43(), "G44": g44()}
    (RES / "natives.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
