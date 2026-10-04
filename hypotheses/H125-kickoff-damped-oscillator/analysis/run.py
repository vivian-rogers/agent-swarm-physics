"""H125 replication run: every eligible kickoff x 6 input configurations (+ R5 settled = day 4 only), card-level tests.

Writes data/processed/H125-kickoff-damped-oscillator/NE34/:
  kickoffs_all_configs.parquet  one row per (design, cfg) with U, E1, placebo, decoy percentile, fits, zeta
  placebo_all_configs.parquet   one row per (design, cfg, origin) placebo-day U
  card.json                     card-level P1-P3, S1-S4 per configuration
  series.json                   day-level and window series per kickoff (bge_white, gte_white) for figures
Usage: uv run python hypotheses/H125-kickoff-damped-oscillator/analysis/run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import mannwhitneyu

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h125lib as L  # noqa: E402

Z90 = 1.645
OUT = L.DATA / "NE34"


def human_diff(kr: dict) -> int:
    kc = pl.read_parquet(L.S / "kicks_classified.parquet").filter((pl.col("kind") == "human_message") & (pl.col("subkind") != "kickoff"))
    days = kr["days"]
    cnt = {i + 1: kc.filter(pl.col("pt_date") == d).height for i, d in enumerate(days[:5])}
    return int(cnt.get(4, 0) + cnt.get(5, 0) - cnt.get(2, 0) - cnt.get(3, 0)), int(cnt.get(4, 0) + cnt.get(5, 0))


def day_profile(st, a, n=10):
    ad = L.agent_day(st, a)
    prof = {}
    for d in range(1, n + 1):
        v = []
        for i, dd in ad.items():
            s45 = L._pair(dd, (4, 5))
            if d in dd and dd[d][1] >= L.MIN_DAY_STMT and np.isfinite(s45):
                v.append(dd[d][0] - s45)
        prof[d] = (float(np.mean(v)), float(np.std(v, ddof=1) / np.sqrt(len(v))) if len(v) > 1 else np.nan, len(v)) if v else (np.nan, np.nan, 0)
    return prof


def card(df: pl.DataFrame, plc: pl.DataFrame) -> dict:
    out = {}
    for cfg in df["cfg"].unique().sort().to_list():
        d = df.filter(pl.col("cfg") == cfg)
        U = d["U"].to_numpy(); se = d["se_U"].to_numpy()
        m = L.dl_meta(U, se)
        pu = plc.filter(pl.col("cfg") == cfg)["U"].to_numpy()
        ok = np.isfinite(U)
        p_mw = float(mannwhitneyu(U[ok], pu[np.isfinite(pu)], alternative="greater").pvalue) if len(pu) >= 3 else np.nan
        E = L.dl_meta(d["E1"].to_numpy(), d["se_E1"].to_numpy())
        ds = d["dsse"].to_numpy()
        pi = d["pi_U"].to_numpy()
        reg = d["regime"].to_numpy()
        uI, uIII = U[(reg == "I") & ok], U[(reg == "III") & ok]
        out[cfg] = dict(
            k=int(ok.sum()), U=m["mean"], U_se=m["se"], U_lo=m["mean"] - Z90 * m["se"], U_hi=m["mean"] + Z90 * m["se"], tau2=m["tau2"],
            U_pos=int((U[ok] > 0).sum()), U_sign_p=L.sign_p(U), p_mw_vs_placebo=p_mw, n_placebo=int(np.isfinite(pu).sum()),
            placebo_median=float(np.nanmedian(pu)) if len(pu) else np.nan, placebo_q95=float(np.nanpercentile(pu, 95)) if len(pu) else np.nan,
            P1=bool(m["mean"] - Z90 * m["se"] > 0 and p_mw < 0.05),
            E1=E["mean"], E1_se=E["se"], E1_pos=int((d["E1"].to_numpy() > 0).sum()), S1=bool(E["mean"] - Z90 * E["se"] > 0 and np.mean(d["E1"].to_numpy() > 0) >= 2 / 3),
            osc_win=int((ds > 0).sum()), osc_win_share=float(np.nanmean(ds > 0)), dsse_sign_p=L.sign_p(ds),
            P2=bool(np.nanmean(ds > 0) >= 2 / 3 and L.sign_p(ds) < 0.05),
            zeta_pk_meta=L.zeta_pk(E["mean"], m["mean"]), zeta_fit_median_oscwin=float(np.nanmedian(d["zeta_fit"].to_numpy()[ds > 0])) if (ds > 0).any() else np.nan,
            S2_U_I=float(np.mean(uI)) if len(uI) else np.nan, S2_U_III=float(np.mean(uIII)) if len(uIII) else np.nan,
            S2_p=float(mannwhitneyu(uIII, uI, alternative="greater").pvalue) if len(uI) >= 3 and len(uIII) >= 3 else np.nan,
            S4_pi_median=float(np.nanmedian(pi)) if np.isfinite(pi).any() else np.nan, S4_sign_p=L.sign_p(pi - 0.5) if np.isfinite(pi).any() else np.nan,
        )
        dn = d.filter(pl.col("human45") == 0)
        if dn.height >= 3:
            mn = L.dl_meta(dn["U"].to_numpy(), dn["se_U"].to_numpy())
            out[cfg]["R4_noHuman45_U"] = mn["mean"]; out[cfg]["R4_noHuman45_lo"] = mn["mean"] - Z90 * mn["se"]; out[cfg]["R4_k"] = dn.height
        if "human_diff" in d.columns:
            hd = d["human_diff"].to_numpy().astype(float)
            if np.std(hd) > 0:
                out[cfg]["R4_corr_U_humandiff"] = float(np.corrcoef(U[ok], hd[ok])[0, 1])
        h97 = d.filter(pl.col("goal_no").is_in([11, 12, 13, 17, 18, 19, 20, 21, 25, 26, 27, 31, 38, 39, 40, 41, 42]))
        mh = L.dl_meta(h97["U"].to_numpy(), h97["se_U"].to_numpy())
        out[cfg]["H97set_U"] = mh["mean"]; out[cfg]["H97set_lo"] = mh["mean"] - Z90 * mh["se"]; out[cfg]["H97set_k"] = mh["k"]
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    k = L.kickoffs().filter(pl.col("kind") == "kickoff").sort("goal_no")
    rows, prow, series = [], [], {}
    cache: dict = {}
    for kr in k.iter_rows(named=True):
        st = L.stmt(kr["design"])
        hd, h45 = human_diff(kr)
        for cfg in L.CFGS:
            a, Pq = L.excess_alignment(st, kr, cfg, with_decoys=True)
            nb = 50 if cfg in ("bge_white", "gte_white") else 0
            r = L.analyze_kickoff(st, kr, a, Pq, fitter_cache=cache, n_boot=nb, seed=kr["goal_no"])
            ser = r.pop("_series", None)
            for o, u in zip(L.placebo_origins(kr["n_days"]), r["placebo_u"]):
                prow.append(dict(design=kr["design"], cfg=cfg, origin=o, U=u))
            row = {kk: v for kk, v in r.items() if not isinstance(v, list)}
            row.update(design=kr["design"], goal_no=kr["goal_no"], regime=kr["regime"], mode=kr["mode"], cfg=cfg,
                       n_inc=len(kr["incumbents"]), human_diff=hd, human45=h45,
                       zeta_lo=(r.get("zeta_ci") or [np.nan, np.nan])[0], zeta_hi=(r.get("zeta_ci") or [np.nan, np.nan])[1],
                       placebo_q95_own=float(np.nanpercentile(r["placebo_u"], 95)) if r["placebo_u"] else np.nan)
            rows.append(row)
            if cfg in ("bge_white", "gte_white"):
                series.setdefault(kr["design"], {})[cfg] = dict(window=ser, day=day_profile(st, a))
            if cfg in ("bge_white", "gte_white"):     # R5 variant: settled level from day 4 only
                r5 = L.analyze_kickoff(st, kr, a, None, fitter_cache=cache, settled=(4,))
                rows.append(dict(design=kr["design"], goal_no=kr["goal_no"], regime=kr["regime"], mode=kr["mode"], cfg=cfg + "_day4",
                                 n_inc=len(kr["incumbents"]), human_diff=hd, human45=h45,
                                 **{kk: v for kk, v in r5.items() if not isinstance(v, (list, tuple)) and kk != "_series"}))
                for o, u in zip(L.placebo_origins(kr["n_days"]), r5["placebo_u"]):
                    prow.append(dict(design=kr["design"], cfg=cfg + "_day4", origin=o, U=u))
        print(kr["design"], "done", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    plc = pl.DataFrame(prow)
    # pooled placebo 95th percentile per cfg for the per-kickoff rule
    q95 = {c: float(np.nanpercentile(plc.filter(pl.col("cfg") == c)["U"].to_numpy(), 95)) for c in plc["cfg"].unique().to_list()}
    df = df.with_columns(pl.col("cfg").replace_strict(q95, default=None).alias("placebo_q95"))
    df.write_parquet(OUT / "kickoffs_all_configs.parquet")
    plc.write_parquet(OUT / "placebo_all_configs.parquet")
    c = card(df, plc)
    (OUT / "card.json").write_text(json.dumps(c, indent=1, default=float))
    (OUT / "series.json").write_text(json.dumps(series, default=float))
    for cfg, v in c.items():
        print(f"{cfg:16s} U {v['U']:+.4f} [{v['U_lo']:+.4f},{v['U_hi']:+.4f}] pos {v['U_pos']}/{v['k']} p_mw {v['p_mw_vs_placebo']:.3f} "
              f"P1 {v['P1']} | E1 {v['E1']:+.3f} S1 {v['S1']} | osc {v['osc_win']}/{v['k']} P2 {v['P2']} | zpk {v['zeta_pk_meta']} | "
              f"S2 I {v['S2_U_I']:+.3f} III {v['S2_U_III']:+.3f} p {v['S2_p']} | pi {v['S4_pi_median']}")


if __name__ == "__main__":
    main()
