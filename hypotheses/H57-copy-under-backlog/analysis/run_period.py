"""H57 replication layer: the common estimator on every eligible goal period (non-holdout), then cross-period pooling.

  uv run python hypotheses/H57-copy-under-backlog/analysis/run_period.py [--periods 40,51] [--n_perm 500]

Reads data/processed/H57-copy-under-backlog/statements.parquet (scheme/build.py outcomes).
Writes data/processed/H57-copy-under-backlog/results/G<NN>.json, summary.parquet, pooled.json.
Primary outcomes (Amendment 1/1b): e_bge, e_gte (chance-corrected read-set echo), mkn_all (chance-corrected marker
near-copy), T on the addressed-source channel (K = 32). Within-period slopes on log2(1 + k) with agent x unit FE.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h57lib as L  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OUT = L.ROOT / "data/processed/H57-copy-under-backlog"
RES = OUT / "results"
PRIMARY = ["e_bge", "e_gte", "mkn_all"]
SECONDARY = ["e_both", "mkn_rare", "near_bge_addr", "near_gte_addr", "er_bge", "er_gte", "es_bge", "mkns_all",
             "cross_echo_bge_f", "cross_echo_gte_f", "cross_echo_both_f"]
POSTHOC = ["elc_bge", "elc_gte", "elc_both", "mklc_all", "mklc_rare", "el_bge", "el_gte", "mkl_all", "els_bge", "els_gte",
           "els_both", "mkls_all", "mkls_rare"]  # Amendment 2 (post hoc)
DESCRIPTIVE = ["em_bge", "em_gte", "mks_all", "near_bge_par", "near_gte_par"]
MIN_N, MIN_AGENTS = 200, 3


def eligible(d: pl.DataFrame) -> bool:
    return d.height >= MIN_N and d["agent"].n_unique() >= MIN_AGENTS


def jnum(x):
    if isinstance(x, dict):
        return {k: jnum(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jnum(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


def analyse_period(d: pl.DataFrame, g: int, n_perm: int = 500, seed: int = 0) -> dict:
    res = {"goal_no": g, "n": d.height, "n_agents": int(d["agent"].n_unique()), "regime": d["regime"].mode()[0],
           "k_med": float(d["k"].median()), "k_q90": float(d["k"].quantile(0.9)), "k_mean": float(d["k"].mean()),
           "n_units": int(d["unit_id"].n_unique()), "n_days": int(d["pt_date"].n_unique()),
           "corr_logk_early": float(np.corrcoef(d["logk"], d["early_f"])[0, 1]) if d["early_f"].std() > 0 else None,
           "corr_logk_daypos": float(np.corrcoef(d["logk"], d["daypos_f"])[0, 1]),
           "rates": {c: float(d[c].mean()) for c in ("echo_bge_R", "echo_gte_R", "echo_both_R", "chance_bge",
                                                       "chance_gte", "mk_near_all_R", "q_bge", "q_gte", "q_mk_all")
                     if c in d.columns and d[c].null_count() < d.height},
           "share_addressed": float(d["addressed_f"].mean()), "share_addr_unique": float((d["addr_n"] == 1).mean()),
           "slopes": {}}
    for y in PRIMARY + SECONDARY + DESCRIPTIVE + POSTHOC:
        if y not in d.columns:
            continue
        specs = ("agent", "day", "lab") if y in PRIMARY + POSTHOC[:4] else ("agent",)
        for spec in specs:
            res["slopes"][f"{y}|{spec}"] = L.slope(d, y, spec)
    # rival a: early x log k interaction; within early / late
    dd = d.with_columns((pl.col("early_f") * pl.col("logk")).alias("early_x_logk"))
    for y in PRIMARY + POSTHOC[:4]:
        if y not in d.columns:
            continue
        res["slopes"][f"{y}|agent+int"] = L.slope(dd, y, "agent", extra=["early_x_logk"])
        for nm, sub in (("early", d.filter(pl.col("early"))), ("late", d.filter(~pl.col("early")))):
            res["slopes"][f"{y}|{nm}"] = L.slope(sub, y, "agent")
    # rival b: drop templated (either model) and kickoff-echo statements (top decile cosine to the kickoff, either model)
    q = {m: d[f"kick_cos_{m}"].quantile(0.9) for m in L.MODELS if f"kick_cos_{m}" in d.columns}
    filt = d.filter(~pl.col("templated_bge").fill_null(False) & ~pl.col("templated_gte").fill_null(False))
    for m, qq in q.items():
        filt = filt.filter(pl.col(f"kick_cos_{m}") < qq)
    res["n_filt"] = filt.height
    for y in PRIMARY + ["mkn_rare"] + POSTHOC[:5]:
        if y in filt.columns:
            res["slopes"][f"{y}|filt"] = L.slope(filt, y, "agent")
    # sensitivity: DQ2 is_reply as the reply control (a collider in synthetic worlds; reported, not used)
    for y in PRIMARY:
        res["slopes"][f"{y}|isreply"] = L.slope(d, y, "agent", extra=["is_reply_f"])
    # context-load variant (computer-use calls): log2(1 + k_ctx), with log k held fixed
    dc = d.filter(pl.col("ctx_mode") == "cu").with_columns(
        (pl.col("k_ctx").cast(pl.Float64).fill_null(0) + 1).log(2).alias("logkctx"))
    if dc.height >= MIN_N and dc["logkctx"].std() > 0:
        for y in PRIMARY + [c for c in POSTHOC[:4] if c in d.columns]:
            res["slopes"][f"{y}|kctx"] = L.slope(dc, y, "agent", x="logkctx", extra=["logk"])
    # source channel: Kolchinsky decomposition (addressed source primary; DQ2 parent descriptive)
    res["decomp"] = {}
    for m in L.MODELS:
        for K in (16, 32, 64):
            res["decomp"][f"addr|{m}|K{K}"] = L.decomposition(d, m, K, n_perm=n_perm if K == 32 else 200,
                                                              n_null=100 if K == 32 else 0, seed=seed + K)
        res["decomp"][f"par|{m}|K32"] = L.decomposition(d, m, 32, n_perm=200, n_null=100, seed=seed + 1, src="par")
        res["decomp"][f"addrcluster|{m}|K32"] = L.decomposition(d, m, 32, n_perm=200, n_null=100, seed=seed + 2,
                                                               src="addr", coding="cluster")
        dp = L.add_pointwise(d, m, 32, "addr")
        for y in (f"pc_{m}", f"pt_{m}", f"pi_{m}"):
            res["slopes"][f"{y}|agent"] = L.slope(dp, y, "agent")
    # HH153 side: are echoes shorter? within-agent difference in log length for read-set echoes (both models)
    dh = d.with_columns(pl.col("echo_both_R").cast(pl.Float64).alias("echo_both_f"))
    res["slopes"]["log_len~echo_both"] = L.slope(dh.with_columns(pl.col("log_len").alias("y_len")), "y_len", "agent",
                                                 x="echo_both_f")
    cal = json.loads((OUT / "synthetic/calibration.json").read_text())
    res["calibrated_p"] = {}
    for key, r in res["slopes"].items():
        parts = key.split("|")
        spec = parts[1] if len(parts) > 1 else "agent"
        base = parts[0] + "|" + ("agent" if spec in ("agent", "isreply", "agent+int", "early", "late", "kctx", "lab")
                                 else spec)
        kap = cal.get(base, cal.get(key.split("|")[0] + "|agent", {})).get("kappa", 1.0)
        c = coef_name(key)
        b, se = L.bget(r, c), L.bget(r, c, key="se")
        if np.isfinite(b) and np.isfinite(se) and se > 0:
            from scipy import stats as _st
            res["calibrated_p"][key] = {"kappa": kap, "z_cal": float(b / se / kap),
                                        "p_cal": float(2 * _st.norm.sf(abs(b / se / kap)))}
    res["verdict"] = verdict(res)
    return res


def verdict(res: dict) -> str:
    """Card rule (per period): supported if e_bge, e_gte and mkn_all slopes are > 0 with at least one one-sided
    p < 0.05 and none significantly negative; failed if any primary slope is significantly negative or all <= 0;
    mixed otherwise."""
    bs, ps = [], []
    for y in PRIMARY:
        r = res["slopes"].get(f"{y}|agent", {})
        b = L.bget(r)
        p = res.get("calibrated_p", {}).get(f"{y}|agent", {}).get("p_cal", L.bget(r, key="p"))
        bs.append(b); ps.append(p)
    bs, ps = np.array(bs, float), np.array(ps, float)
    if np.any(np.isnan(bs)):
        return "n/a"
    sig_neg = np.any((bs < 0) & (ps < 0.05))
    if sig_neg or np.all(bs <= 0):
        return "failed"
    if np.all(bs > 0) and np.any(ps / 2 < 0.05):
        return "supported"
    return "mixed"


def coef_name(key: str) -> str:
    if key.endswith("|kctx"):
        return "logkctx"
    if key.startswith("log_len~"):
        return "echo_both_f"
    return "logk"


def pooled(rows: list[dict]) -> dict:
    out = {}
    keys = sorted({k for r in rows for k in r["slopes"]})
    for key in keys:
        c = coef_name(key)
        b = [L.bget(r["slopes"].get(key, {}), c) for r in rows]
        se = [L.bget(r["slopes"].get(key, {}), c, key="se") for r in rows]
        out[key] = L.random_effects(b, se)
        if key.endswith("|agent+int"):
            b = [L.bget(r["slopes"].get(key, {}), "early_x_logk") for r in rows]
            se = [L.bget(r["slopes"].get(key, {}), "early_x_logk", key="se") for r in rows]
            out[key + "#early_x_logk"] = L.random_effects(b, se)
    for key in sorted({k for r in rows for k in r["decomp"]}):
        Ts = [r["decomp"][key].get("T", np.nan) for r in rows]
        ps = [r["decomp"][key].get("p_one", np.nan) for r in rows]
        out[f"T|{key}"] = {"stouffer_p": L.stouffer(ps), "k": int(np.sum(np.isfinite(Ts))),
                           "n_pos": int(np.nansum(np.array(Ts) > 0)), "median_T": float(np.nanmedian(Ts)),
                           "n_p05": int(np.nansum(np.array(ps) < 0.05))}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default="")
    ap.add_argument("--n_perm", type=int, default=500)
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    allst = pl.read_parquet(OUT / "statements.parquet")
    allst = allst.with_columns(pl.col(c).cast(pl.Float64).alias(f"{c}_f") for c in
                               ("cross_echo_bge", "cross_echo_gte", "cross_echo_both"))
    gs = [int(x) for x in a.periods.split(",") if x] or sorted(allst["goal_no"].unique().to_list())
    rows = []
    for g in gs:
        t0 = time.time()
        d = L.prepare(allst.filter(pl.col("goal_no") == g))
        if not eligible(d):
            print(f"G{g:02d}: not eligible (n {d.height})")
            continue
        r = analyse_period(d, g, n_perm=a.n_perm, seed=g)
        (RES / f"G{g:02d}.json").write_text(json.dumps(jnum(r), indent=1))
        rows.append(r)
        e = r["slopes"]
        print(f"G{g:02d} n={r['n']} k_med={r['k_med']:.0f} | e_bge {L.bget(e['e_bge|agent']):+.4f} "
              f"(p {L.bget(e['e_bge|agent'], key='p'):.3f}) e_gte {L.bget(e['e_gte|agent']):+.4f} "
              f"mkn {L.bget(e['mkn_all|agent']):+.4f} T_bge {r['decomp']['addr|bge|K32'].get('T', np.nan):+.3f} "
              f"-> {r['verdict']} [{time.time() - t0:.0f}s]", flush=True)
    if len(gs) > 1 or not (RES / "pooled.json").exists():
        allrows = [json.loads((RES / f).read_text()) for f in sorted(p.name for p in RES.glob("G*.json"))]
        (RES / "pooled.json").write_text(json.dumps(jnum(pooled(allrows)), indent=1))
        summ = []
        for r in allrows:
            row = {"goal_no": r["goal_no"], "n": r["n"], "n_agents": r["n_agents"], "regime": r["regime"],
                   "k_med": r["k_med"], "k_q90": r["k_q90"], "verdict": r["verdict"]}
            for y in PRIMARY + ["e_both", "near_bge_addr", "near_gte_addr", "er_bge", "cross_echo_bge_f"]:
                s = r["slopes"].get(f"{y}|agent", {})
                row[f"{y}_b"], row[f"{y}_se"], row[f"{y}_p"] = (s.get("logk", {}) or {}).get("b"), \
                    (s.get("logk", {}) or {}).get("se"), (s.get("logk", {}) or {}).get("p")
            for m in L.MODELS:
                dd = r["decomp"].get(f"addr|{m}|K32", {})
                row[f"T_{m}"], row[f"Tp_{m}"] = dd.get("T"), dd.get("p_one")
                row[f"s_bottom_{m}"], row[f"s_top_{m}"] = dd.get("s_bottom"), dd.get("s_top")
            row.update({f"rate_{k}": v for k, v in r["rates"].items()})
            summ.append(row)
        pl.DataFrame(summ).write_parquet(RES / "summary.parquet")


if __name__ == "__main__":
    main()
