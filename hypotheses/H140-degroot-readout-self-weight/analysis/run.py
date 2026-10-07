"""H140 round-1 analysis on exploration data (non-reserved days only; reserved days never enter the scheme).

Per unit (period_units): O1 (A1 primary spec and the registered spec), O2 (b, a), O3 closure, O4 (gammaF/gamma1,
matched-age contrast, redundancy r), N1 cross-day surrogate batches, N2 within-agent-day s_self permutation, variants.
Natives: NE41 (first post-reset talk call, p from the erased segment), G51 timer wakes. Regime I/II: O2 only.
Usage: uv run python .../analysis/run.py [--part units|ne41|wakes|reg12|all] [--period 38 ...]
Output: data/processed/H140-degroot-readout-self-weight/results/*.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
import h140lib as L  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H140-degroot-readout-self-weight"
RES = DATA / "results"
REG3 = (37, 38, 39, 40, 41, 42, 44, 51)
REG12 = (13, 16, 35, 36)
MIN_ROWS = 300
B = 300


def load(g: int, tag: str = "bge", prefix: str = "") -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame | None]:
    d = DATA / f"G{g:02d}"
    meta = pl.read_parquet(d / f"{prefix}rows.parquet")
    gram = pl.read_parquet(d / f"{prefix}gram_{tag}.parquet")
    ip = d / f"{prefix}items_{tag}.parquet"
    it = pl.read_parquet(ip) if ip.exists() else None
    return meta, gram, it


def clean(x):
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items() if not k.startswith("_")}
    if isinstance(x, list):
        return [clean(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    return x


def add_deciles(d: pl.DataFrame) -> pl.DataFrame:
    q = np.quantile(d["s_self"].to_numpy(), np.linspace(0, 1, 11)[1:-1])
    return d.with_columns(pl.Series("sig_dec", np.searchsorted(q, d["s_self"].to_numpy(), side="right")))


def unit_block(d: pl.DataFrame, G: np.ndarray, it, full: bool = True, seed: int = 0) -> dict:
    out = {"n_scored": len(d), "n_agent_days": int(L.cluster_ids(d).max() + 1) if len(d) else 0,
           "s_self_mean": float(d["s_self"].mean()) if len(d) else None, "s_self_sd": float(d["s_self"].std()) if len(d) > 1 else None,
           "k_mean": float(d["k"].mean()) if len(d) else None}
    if len(d) < 30:
        return out
    fa = L.fit(d, G, "A1", B=B, seed=seed, keep_draws=True)
    out["A1"] = fa
    out["closure"] = L.closure(d, fa, "A1")
    out["main"] = L.fit(d, G, "main", B=B, seed=seed)
    out["noDn"] = L.fit(d, G, "noDn", B=B, seed=seed)
    out["A1noDn"] = L.fit(d, G, "A1noDn", B=B, seed=seed)
    out["contrast"] = L.placebo_contrast(d, it, B=B, seed=seed) if it is not None else {}
    out["r"] = L.redundancy(d, G)
    c = out["contrast"]
    out["identified"] = bool(c.get("lo") is not None and c["lo"] > 0 and np.isfinite(out["r"]) and out["r"] < 0.7)
    if not full:
        return out
    for v in ("A1chat", "A1ols", "A1p1"):
        out[v] = L.fit(d, G, v, B=200, seed=seed)
    dd = add_deciles(d)
    out["A1deciles"] = L.fit(dd, G, "A1deciles", B=200, seed=seed)
    out["A1deciles"]["sig_dec_means"] = [float(x) for x in dd.group_by("sig_dec").agg(pl.col("s_self").mean()).sort("sig_dec")["s_self"]]
    nr = d.filter(~pl.col("self_repeat_both"))
    out["A1_norepeat"] = L.fit(nr, L.gram_tensor(nr), "A1", B=200, seed=seed) if len(nr) >= 30 else {}
    # N1 cross-day surrogate batches (point fits)
    if "u0_ss" in d.columns:
        sur = []
        for q in range(20):
            f = L.fit(d, L.surrogate_gram(G, d, q), "A1", B=0)
            sur.append((f.get("a"), f.get("gamma1"), f.get("w1")))
        sur = np.array(sur, dtype=float)
        out["N1_sur"] = {"a_med": float(np.nanmedian(sur[:, 0])), "a_lo": float(np.nanpercentile(sur[:, 0], 2.5)),
                         "a_hi": float(np.nanpercentile(sur[:, 0], 97.5)), "gamma1_med": float(np.nanmedian(sur[:, 1])),
                         "gamma1_lo": float(np.nanpercentile(sur[:, 1], 2.5)), "gamma1_hi": float(np.nanpercentile(sur[:, 1], 97.5)),
                         "share_gamma1_ge_real": float(np.mean(sur[:, 1] >= fa["gamma1"]))}
    # N2 within-agent-day permutation of s_self (b fixed at the real b-hat)
    nul = []
    for q in range(200):
        f = L.fit(L.permute_sig(d, 1000 + q), G, "A1", B=0, grid=[fa["b"]])
        nul.append(f.get("w1"))
    nul = np.array(nul, dtype=float)
    out["N2_perm"] = {"w1_null_mean": float(np.nanmean(nul)), "w1_null_sd": float(np.nanstd(nul)),
                      "w1_null_lo": float(np.nanpercentile(nul, 2.5)), "w1_null_hi": float(np.nanpercentile(nul, 97.5)),
                      "p_two_sided": float(np.mean(np.abs(nul - np.nanmean(nul)) >= abs(fa["w1"] - np.nanmean(nul))))}
    return out


def run_units(periods) -> dict:
    res = {}
    for g in periods:
        t0 = time.time()
        meta, gram, it = load(g, "bge")
        d0, _, _ = L.prep(meta, gram)
        for u in sorted(d0["unit_id"].unique().to_list()):
            d = d0.filter(pl.col("unit_id") == u)
            G = L.gram_tensor(d)
            r = {"goal_no": g, "unit": u, "bge": unit_block(d, G, it, full=True, seed=g)}
            for tag in ("gte", "bgeF", "bgeW"):
                m2, g2, it2 = load(g, tag)
                e, _, _ = L.prep(m2, g2)
                e = e.filter(pl.col("unit_id") == u)
                r[tag] = unit_block(e, L.gram_tensor(e), it2, full=False, seed=g)
            res[u] = r
            print(f"{u}: n {r['bge']['n_scored']} w1 {r['bge'].get('A1', {}).get('w1')} a {r['bge'].get('A1', {}).get('a')} "
                  f"({time.time() - t0:.0f}s)", flush=True)
        (RES / f"units_G{g:02d}.json").write_text(json.dumps(clean({k: v for k, v in res.items() if v["goal_no"] == g}), indent=1))
    return res


def ne41_rows(meta: pl.DataFrame, gram: pl.DataFrame, kind: str) -> pl.DataFrame:
    d = pl.concat([meta, gram], how="horizontal")
    base = pl.col("h_ok") & pl.col("z_ok") & ~pl.col("templated") & (pl.col("dn") >= 0) & pl.col("s_self").is_not_nan()
    first = d.filter(base & (pl.col("pmode") == "xreset") & (pl.col("seg_kind") == kind)).with_columns(pl.lit(1).alias("first"))
    ctrl = d.filter(base & (pl.col("pmode") == "in") & (pl.col("ctx_pos") >= 5)).with_columns(pl.lit(0).alias("first"))
    return pl.concat([first, ctrl])


def run_ne41(periods) -> dict:
    res = {}
    for g in periods:
        for tag in ("bge", "gte"):
            meta, gram, _ = load(g, tag)
            for kind in ("forced", "vol"):
                d0 = ne41_rows(meta, gram, kind)
                for u in sorted(d0["unit_id"].unique().to_list()):
                    d = d0.filter(pl.col("unit_id") == u)
                    nf = int(d["first"].sum())
                    r = {"goal_no": g, "unit": u, "model": tag, "kind": kind, "n_first": nf, "n_ctrl": len(d) - nf}
                    if nf >= 30:
                        sf = d.filter(pl.col("first") == 1)["s_self"]; sc = d.filter(pl.col("first") == 0)["s_self"]
                        r["s_first"] = float(sf.mean()); r["s_ctrl"] = float(sc.mean()); r["ds"] = r["s_first"] - r["s_ctrl"]
                        r["fit"] = L.fit(d, L.gram_tensor(d), "firstA1", B=B, seed=g)
                        r["fit_noDn"] = L.fit(d, L.gram_tensor(d), "firstA1noDn", B=200, seed=g)
                    res[f"{u}|{tag}|{kind}"] = r
                    print(f"NE41 {u} {tag} {kind}: first {nf} dw {r.get('fit', {}).get('dw_first')}", flush=True)
    (RES / "ne41.json").write_text(json.dumps(clean(res), indent=1))
    return res


def run_wakes() -> dict:
    res = {}
    for tag in ("bge", "gte"):
        meta, gram, it = load(51, tag, "wake_")
        d0, _, _ = L.prep(meta, gram)
        for u in sorted(d0["unit_id"].unique().to_list()):
            d = d0.filter(pl.col("unit_id") == u)
            res[f"{u}|{tag}"] = {"unit": u, "model": tag, **unit_block(d, L.gram_tensor(d), it, full=False, seed=51)}
            print(f"wakes {u} {tag}: n {len(d)} w1 {res[f'{u}|{tag}'].get('A1', {}).get('w1')}", flush=True)
    (RES / "wakes.json").write_text(json.dumps(clean(res), indent=1))
    return res


def run_reg12() -> dict:
    res = {}
    for g in REG12:
        for tag in ("bge", "gte"):
            meta, gram, it = load(g, tag)
            d, G, _ = L.prep(meta, gram, need_sig=False)
            r = {"goal_no": g, "model": tag, "n_scored": len(d)}
            if len(d) >= 30:
                r["o2A1"] = L.fit(d, G, "o2A1", B=B, seed=g)
                r["contrast"] = L.placebo_contrast(d, it, B=B, seed=g)
                r["r"] = L.redundancy(d, G)
            res[f"G{g}|{tag}"] = r
            print(f"reg12 G{g} {tag}: n {len(d)} a {r.get('o2A1', {}).get('a')}", flush=True)
    (RES / "reg12.json").write_text(json.dumps(clean(res), indent=1))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="all")
    ap.add_argument("--period", type=int, action="append")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    periods = a.period or list(REG3)
    if a.part in ("units", "all"):
        run_units(periods)
    if a.part in ("ne41", "all"):
        run_ne41(periods)
    if a.part in ("wakes", "all"):
        run_wakes()
    if a.part in ("reg12", "all"):
        run_reg12()


if __name__ == "__main__":
    main()
