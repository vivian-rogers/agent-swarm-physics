"""H73 replication layer: O1 decomposition, O2 attribution, O3 dispersion and O4 rival controls per eligible goal period.

Output: data/processed/H73-style-three-components/replication/replication.json (+ card-level P1-P5 summary).
Usage: uv run python hypotheses/H73-style-three-components/analysis/replication.py [--procs 4] [--only 38,41]
"""
from __future__ import annotations
import os
os.environ["OMP_NUM_THREADS"] = os.environ["OPENBLAS_NUM_THREADS"] = os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["POLARS_MAX_THREADS"] = "1"
import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import binomtest  # noqa: E402

import h73lib as L  # noqa: E402
from write_period_cards import eligible_goals  # noqa: E402


def sub(a: dict, idx: np.ndarray, day=None) -> dict:
    b = {k: (v[idx] if isinstance(v, np.ndarray) and len(v) == len(a["agent"]) else v) for k, v in a.items()}
    if day is not None:
        b["day"] = day
    return b


def jack_F3(a: dict):
    """Delete-one-day jackknife of F3 (replaces the day bootstrap, whose duplicated days skewed the interval)."""
    days = np.unique(a["day"])
    th = []
    for d in days:
        idx = np.where(a["day"] != d)[0]
        th.append(L.decompose(sub(a, idx), n_perm=0)["F3"])
    th = np.array(th)
    n = len(th)
    se = float(np.sqrt((n - 1) / n * ((th - th.mean()) ** 2).sum())) if n > 1 else np.nan
    return se


def sensitivities(a: dict, m: pl.DataFrame, g: int) -> dict:
    """Preprocessing and post-hoc variants (labelled in the card)."""
    s = {}
    Y = a["X"] - a["X"].mean(0)
    G, A, C, R = L.block_G(a), L.block_A(a), L.block_C(a), L.block_R(a)
    base = L.decompose(a, n_perm=0)
    # post hoc PH1: ceiling at agent-day resolution (context and register as parametric terms)
    ad = np.array([f"{x}|{d}" for x, d in zip(a["agent"], a["day"])])
    kAD = L.fit_r2(Y, [G, L.dummies(ad), C, R])[1]
    den = kAD - base["r2a"]["G"]
    s["kappa_AD"] = kAD
    s["F3_AD"] = (base["r2a"]["GACR"] - base["r2a"]["G"]) / den if den > 0 else np.nan
    s["eta_share_AD"] = (kAD - base["r2a"]["GACR"]) / den if den > 0 else np.nan
    # post hoc PH2: context share without the chat/computer-use mode level (mode moved into the nuisance block)
    if (~a["cu"]).any() and a["cu"].any():
        s["u_C_fill_only"] = L.decompose(a, n_perm=0, extra_G=[(~a["cu"]).astype(float)[:, None]])["u_C"]
    # planned preprocessing variants: raw 20-d style; restatements removed
    raw = dict(a); raw["X"] = m.select([f"s_{f}" for f in L.STYLE]).to_numpy().astype(float)
    dr = L.decompose(raw, n_perm=0)
    s["F3_raw20"], s["u_C_raw20"], s["u_A_raw20"] = dr["F3"], dr["u_C"], dr["u_A"]
    mr = L.load_messages(dedupe="restate").filter(pl.col("goal_no") == g)
    ar = L.arrays(mr)
    drs = L.decompose(ar, n_perm=0)
    at = L.attribution(ar, ks=(5,)).get(5)
    s["F3_restate"], s["u_C_restate"] = drs["F3"], drs["u_C"]
    s["dc_restate"] = at["gain_agent"] if at else np.nan
    return s


def rivals(a: dict) -> dict:
    """O4: genre controls, dropping p <= 1, own vs received fill (regime III)."""
    r = {}
    base = L.decompose(a, n_perm=0)
    r["u_C"] = base["u_C"]
    g = L.decompose(a, n_perm=0, extra_G=[np.column_stack([a["is_reply"], a["has_mention"]]).astype(float)])
    r["u_C_genre"] = g["u_C"]
    mask = ~(a["cu"] & (a["pos"] <= 1))
    if mask.sum() > 100:
        r["u_C_drop_p01"] = L.decompose(a, n_perm=0, mask=mask)["u_C"]
    if a["cu"].all():   # regime III: own fill z vs received fill zk
        Y = a["X"] - a["X"].mean(0)
        zk = np.log2(1.0 + a["kctx"]); zk = zk - zk.mean()
        G, A, R = L.block_G(a), L.block_A(a), L.block_R(a)
        bins = L.block_C(a, agent_slopes=False)
        Da = L.dummies(a["agent"], drop=None)
        Cz, Ck = Da * a["z"][:, None], Da * zk[:, None]
        full = L.fit_r2(Y, [G, A, bins, Cz, Ck, R])[1]
        no_z = L.fit_r2(Y, [G, A, bins, Ck, R])[1]
        no_k = L.fit_r2(Y, [G, A, bins, Cz, R])[1]
        den = base["kappa"] - base["r2a"]["G"]
        r["u_own_fill"] = (full - no_z) / den
        r["u_recv_fill"] = (full - no_k) / den
        r["corr_z_zk"] = float(np.corrcoef(a["z"], zk)[0, 1])
    return r


def verdict(dec, att5) -> str:
    gain = att5["gain_agent"] if att5 else np.nan
    largest = dec["u_A"] >= np.nanmax([dec["u_C"], dec["u_R"] if dec["u_R"] == dec["u_R"] else -1])
    pc_ok = dec.get("p_C", 0) < 0.05 if dec["n_cu"] >= 500 else True
    if dec["F3"] >= 0.57 and largest and gain > 0 and pc_ok:
        return "supported"
    if dec["F3"] < 0.5 and not gain > 0:
        return "failed"
    return "mixed"


def run_goal(g: int) -> tuple[str, dict]:
    m = L.load_messages().filter(pl.col("goal_no") == g)
    a = L.arrays(m)
    nperm = 100 if g == 51 else 200
    dec = L.decompose(a, n_perm=nperm, seed=g)
    att = L.attribution(a, ks=(1, 5))
    dis = L.dispersion_slope(a)
    se = jack_F3(a)
    ci = [dec["F3"] - 1.96 * se, dec["F3"] + 1.96 * se]
    riv = rivals(a)
    sens = sensitivities(a, m, g)
    att = {str(k): v for k, v in att.items()}
    res = {"goal_no": g, "regime": m["regime"][0], "dec": dec, "F3_ci": ci, "F3_se": se, "att": att, "disp": dis,
           "rivals": riv, "sens": sens,
           "units": sorted(m["unit_id"].unique().to_list())}
    res["verdict"] = verdict(dec, att.get("5"))
    print(f"G{g:02d}: F3 {dec['F3']:.2f} {ci} uA {dec['u_A']:.2f} uC {dec['u_C']:.3f} p {dec.get('p_C')} "
          f"dc5 {att['5']['gain_agent'] if att.get('5') else None} -> {res['verdict']}", flush=True)
    return f"G{g:02d}", res


def card_level(rep: dict) -> dict:
    rows = [r for k, r in rep.items() if not k.startswith("_")]
    F3 = np.array([r["dec"]["F3"] for r in rows])
    uA = np.array([r["dec"]["u_A"] for r in rows]); uC = np.array([r["dec"]["u_C"] for r in rows])
    uR = np.array([r["dec"]["u_R"] if r["dec"]["u_R"] == r["dec"]["u_R"] else -1 for r in rows])
    big = np.array([r["dec"]["n_cu"] >= 500 for r in rows])
    pC = np.array([r["dec"].get("p_C", 1.0) for r in rows])
    dc = np.array([r["att"]["5"]["gain_agent"] if r["att"].get("5") else np.nan for r in rows])
    db = np.array([r["att"]["5"]["gain_det"] if r["att"].get("5") else np.nan for r in rows])
    dc1 = np.array([r["att"]["1"]["gain_agent"] if r["att"].get("1") else np.nan for r in rows])
    ok = ~np.isnan(dc)
    rng = np.random.default_rng(11)
    bs = [np.nanmean(rng.choice(dc[ok], ok.sum(), replace=True)) for _ in range(5000)]
    npos = int((dc[ok] > 0).sum())
    a3 = [r for r in rows if r["dec"]["n_cu"] >= 2000]
    disp_pos = [r["disp"]["lo"] > 0 for r in a3]
    reg3 = [r for r in rows if r["regime"] == "III"]
    out = {
        "n_periods": len(rows),
        "P1": {"n_F3_ge_057": int((F3 >= 0.57).sum()), "median_F3": float(np.median(F3)),
               "pass": bool((F3 >= 0.57).mean() >= 2 / 3 and np.median(F3) >= 0.57),
               "F3_q25_q75": [float(np.quantile(F3, 0.25)), float(np.quantile(F3, 0.75))]},
        "P2": {"n_uA_largest": int((uA >= np.maximum(uC, uR)).sum()), "n_big": int(big.sum()),
               "n_pC_lt05_big": int((pC[big] < 0.05).sum()),
               "median_uC": float(np.median(uC)), "median_uA": float(np.median(uA)),
               "pass": bool((uA >= np.maximum(uC, uR)).mean() >= 0.8 and (pC[big] < 0.05).mean() >= 2 / 3)},
        "P3": {"n_pos": npos, "n": int(ok.sum()), "sign_p": float(binomtest(npos, int(ok.sum()), 0.5, alternative="greater").pvalue),
               "mean_dc": float(np.nanmean(dc)), "ci": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
               "mean_db": float(np.nanmean(db)), "mean_dc_k1": float(np.nanmean(dc1)),
               "pass": bool(npos / ok.sum() >= 2 / 3 and binomtest(npos, int(ok.sum()), 0.5, alternative="greater").pvalue < 0.05
                            and np.nanmean(dc) >= 0.01 and np.quantile(bs, 0.025) > 0)},
        "P4": {"periods": [f"G{r['goal_no']:02d}" for r in a3], "n_pos": int(sum(disp_pos)), "n": len(a3),
               "slopes_rel": [r["disp"]["slope_rel"] for r in a3],
               "pass": bool(len(a3) and sum(disp_pos) / len(a3) >= 2 / 3)},
        "P5": {"median_retention_genre": float(np.nanmedian([r["rivals"]["u_C_genre"] / r["rivals"]["u_C"] for r in rows if r["rivals"]["u_C"] > 0.005])),
               "median_retention_drop_p01": float(np.nanmedian([r["rivals"].get("u_C_drop_p01", np.nan) / r["rivals"]["u_C"] for r in rows if r["rivals"]["u_C"] > 0.005])),
               "regIII_own_vs_recv": [[f"G{r['goal_no']:02d}", r["rivals"]["u_own_fill"], r["rivals"]["u_recv_fill"], r["rivals"]["corr_z_zk"]] for r in reg3]},
        "verdict_counts": {v: sum(r["verdict"] == v for r in rows) for v in ("supported", "mixed", "failed")},
        "sens": {"median_F3_AD": float(np.nanmedian([r["sens"]["F3_AD"] for r in rows])),
                 "n_F3_AD_ge_057": int(sum(r["sens"]["F3_AD"] >= 0.57 for r in rows)),
                 "median_eta_share_AD": float(np.nanmedian([r["sens"]["eta_share_AD"] for r in rows])),
                 "median_uC_fill_only_regI_II": float(np.nanmedian([r["sens"].get("u_C_fill_only", np.nan) for r in rows if r["regime"] != "III"])),
                 "median_uC_regI_II": float(np.nanmedian([r["dec"]["u_C"] for r in rows if r["regime"] != "III"])),
                 "median_uC_regIII": float(np.nanmedian([r["dec"]["u_C"] for r in rows if r["regime"] == "III"])),
                 "median_F3_raw20": float(np.nanmedian([r["sens"]["F3_raw20"] for r in rows])),
                 "median_F3_restate": float(np.nanmedian([r["sens"]["F3_restate"] for r in rows])),
                 "mean_dc_restate": float(np.nanmean([r["sens"]["dc_restate"] for r in rows])),
                 "n_dc_restate_pos": int(sum(r["sens"]["dc_restate"] > 0 for r in rows))},
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    goals = [int(x) for x in args.only.split(",")] if args.only else eligible_goals()
    goals = sorted(goals, key=lambda g: -1 if g == 51 else g)
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        res = dict(ex.map(run_goal, goals))
    path = L.DATA / "replication" / "replication.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if args.only and path.exists():
        old = json.loads(path.read_text()); old.update(res); res = old
    rep = {k: res[k] for k in sorted(k for k in res if not k.startswith("_"))}
    rep["_meta"] = {"run_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC"), "dedupe": "copy (self_repeat_both)",
                    "style": "17-d type-controlled"}
    rep["_card"] = card_level(rep)
    path.write_text(json.dumps(rep, indent=1, default=float))
    print(json.dumps(rep["_card"], indent=1, default=float))


if __name__ == "__main__":
    main()
