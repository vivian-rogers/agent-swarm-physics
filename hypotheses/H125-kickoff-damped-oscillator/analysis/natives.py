"""H125 natives (each with its own dated prediction in its folder README):
  N1 G51   own-role excess alignment after the #51 kickoff (decoys = other agents' roles): U_own > 0, CI above 0.
  N2 NE38  Opus 5's own-new-role U after 2026-07-29 16:51 UTC vs the 90th percentile of the other agents' own-role U.
  N3 G38   M_osc vs M_fade on days 1-10 of #38 (room for a second swing): dSSE > 0 and zeta_fit < 1.
Writes data/processed/H125-kickoff-damped-oscillator/natives/{G51,NE38,G38}.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h125lib as L  # noqa: E402

Z90 = 1.645
OUT = L.DATA / "natives"
NE38_AGENT = 40


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    k = L.kickoffs()
    res = {}
    # N1 G51
    kr = k.filter(pl.col("design") == "G51").row(0, named=True)
    st = L.stmt("G51")
    g51 = {}
    for cfg in ("bge_white", "gte_white", "bge_style", "gte_style"):
        a = L.excess_alignment(st, kr, cfg)
        r = L.analyze_kickoff(st, kr, a, None)
        ser = r.pop("_series", None)
        ad = L.agent_day(st, a)
        prof = {d: float(np.nanmean([dd[d][0] - L._pair(dd, (4, 5)) for dd in ad.values() if d in dd and dd[d][1] >= 3])) for d in range(1, 11)}
        g51[cfg] = {kk: v for kk, v in r.items() if kk != "placebo_u"} | dict(
            placebo_n=len(r["placebo_u"]), placebo_q95=float(np.nanpercentile(r["placebo_u"], 95)) if r["placebo_u"] else np.nan,
            placebo_median=float(np.nanmedian(r["placebo_u"])) if r["placebo_u"] else np.nan, day_profile=prof,
            N1=bool(r["U"] - Z90 * r["se_U"] > 0))
    res["G51"] = g51
    # N2 NE38
    kr = k.filter(pl.col("design") == "NE38").row(0, named=True)
    st = L.stmt("NE38")
    ne = {}
    for cfg in ("bge_white", "gte_white"):
        a = L.excess_alignment(st, kr, cfg)
        ad = L.agent_day(st, a)
        U = {}; E = {}
        for i, dd in ad.items():
            lo, hi = L._pair(dd, (2, 3)), L._pair(dd, (4, 5))
            U[i] = hi - lo
            E[i] = (dd[1][0] - hi) if 1 in dd and dd[1][1] >= 3 else np.nan
        others = np.array([u for i, u in U.items() if i != NE38_AGENT and np.isfinite(u)])
        uo = U.get(NE38_AGENT, np.nan)
        pre = st.filter((pl.col("agent") == NE38_AGENT) & (pl.col("seg") == "pre"))
        a_pre = a[(st["agent"] == NE38_AGENT).to_numpy() & (st["seg"] == "pre").to_numpy()]
        prof = {d: (ad[NE38_AGENT][d][0] if NE38_AGENT in ad and d in ad[NE38_AGENT] else None) for d in range(1, 11)}
        ne[cfg] = dict(U_opus5=uo, E1_opus5=E.get(NE38_AGENT, np.nan), others_q90=float(np.percentile(others, 90)),
                       others_median=float(np.median(others)), n_others=len(others),
                       pct_opus5=float(np.mean(others < uo)) if np.isfinite(uo) else np.nan,
                       opus5_pre_level=float(np.nanmean(a_pre)) if len(a_pre) else np.nan, n_pre=pre.height,
                       opus5_day_levels=prof, N2=bool(np.isfinite(uo) and uo > np.percentile(others, 90)
                                                       and np.isfinite(E.get(NE38_AGENT, np.nan)) and E[NE38_AGENT] > 0))
    res["NE38"] = ne
    # N3 G38 ten-day ring-down
    kr = k.filter(pl.col("design") == "T38").row(0, named=True)
    st = L.stmt("T38")
    g38 = {}
    for cfg in ("bge_white", "gte_white"):
        a = L.excess_alignment(st, kr, cfg)
        r = L.analyze_kickoff(st, kr, a, None, fit_days=10, n_boot=100, seed=38)
        ser = r.pop("_series", None)
        g38[cfg] = {kk: v for kk, v in r.items() if kk not in ("placebo_u",)} | dict(series=ser,
                                                                                    N3=bool((r.get("dsse") or -1) > 0 and r.get("zeta_fit", 2) < 1))
    res["G38"] = g38
    for name, v in res.items():
        (OUT / f"{name}.json").write_text(json.dumps(v, indent=1, default=float))
    for cfg in g51:
        v = g51[cfg]
        print(f"G51 {cfg}: U_own {v['U']:+.4f} ± {v['se_U']:.4f} (n {v['n_u']}), E1 {v['E1']:+.3f}, placebo q95 {v['placebo_q95']:+.4f}, N1 {v['N1']}")
    for cfg, v in ne.items():
        print(f"NE38 {cfg}: U_opus5 {v['U_opus5']:+.4f} E1 {v['E1_opus5']:+.3f} others q90 {v['others_q90']:+.4f} pct {v['pct_opus5']:.2f} N2 {v['N2']}")
    for cfg, v in g38.items():
        print(f"G38 {cfg}: dsse {v['dsse']:+.4f} zeta_fit {v['zeta_fit']:.2f} ci {v.get('zeta_ci')} N3 {v['N3']}")


if __name__ == "__main__":
    main()
