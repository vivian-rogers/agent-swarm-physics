"""H06 exploratory round 1 on real (non-holdout) goal periods.

For each scope (goal period, or a block of #51) and each label set (intention clusterings km8..wd64; artifact labels
with and without carry-forward), compute the observed statistics, fit each model (NCD, Hubbell, conformist) by
profile synthetic likelihood over its (mu, k) grid, simulate 400 fresh replicates at each model's best cell, and
compute LLRs, posterior-predictive p-values, the day-shift independent-agents null, split-half stationarity,
P_n histograms and residence/max-abundance scatters. Verdicts follow the card's pre-registered rules
(Prediction, as amended before the real-data run).

Outputs: data/processed/H06-neutral-cooperative-dynamics/<scope>/round1.json and results_round1.parquet.
Usage: uv run python hypotheses/H06-neutral-cooperative-dynamics/analysis/explore.py [--scopes G31 ...] [--workers 2]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import get_context
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("POLARS_MAX_THREADS", "1")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncd_core as M  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H06-neutral-cooperative-dynamics"
sys.path.insert(0, str(ROOT))
from infra.shared import common as C  # noqa: E402

CLUSTERINGS = ["km8", "km24", "km64", "wd8", "wd24", "wd64"]
PRIMARY = "km24"
R_FRESH = 400
N_SHIFT = 200
MIN_PER_WIN = 3.0
MIN_CHANGES = 20

# scope -> (data folder, pt_date filter or None, role)
SCOPES = {
    "G11": ("G11", None, "free"), "G16": ("G16", None, "free"), "G31": ("G31", None, "free"),
    "G37": ("G37", None, "free"), "G44": ("G44", None, "free"),
    "G19": ("G19", None, "contrast"), "G25": ("G25", None, "contrast"), "G30": ("G30", None, "contrast"),
    "G38": ("G38", None, "contrast"),
    "G51a": ("G51", ("2026-07-06", "2026-07-10"), "check"), "G51b": ("G51", ("2026-07-27", "2026-07-31"), "check"),
    "G51c": ("G51", ("2026-08-24", "2026-08-28"), "check"),
    "G08": ("G08", None, "NE27 pre"), "G10": ("G10", None, "NE27 post"),
    "NE33pre": ("G51", ("2026-08-31", "2026-09-02"), "NE33 pre"), "NE33post": ("G51", ("2026-09-03", "2026-09-04"), "NE33 post"),
}
FREE = ["G11", "G16", "G31", "G37", "G44"]
OUT_SUFFIX = ""  # confirm_holdout.py sets "_confirm" / "_confirm_dryrun" so round-1 files are never overwritten


def guard(folder: str, dates):
    held = set(C.load_holdout()["goal_periods_held_out"])
    g = int(folder[1:3])
    if g in held:
        raise SystemExit(f"refusing: #{g} is held out")
    if dates:
        if any(C.holdout_mask([d], [g])[0] for d in dates):
            raise SystemExit(f"refusing: dates {dates} touch the holdout")


def load_scope(scope: str):
    folder, rng_, role = SCOPES[scope]
    d = DATA / folder
    wins = pl.read_parquet(d / "windows.parquet").sort("gwin")
    if rng_:
        wins = wins.filter((pl.col("pt_date") >= rng_[0]) & (pl.col("pt_date") <= rng_[1]))
    guard(folder, sorted(set(wins["pt_date"].to_list())))
    keep = wins["gwin"].to_list()
    remap = {g: i for i, g in enumerate(keep)}
    days = wins["day"].to_numpy()
    _, day = np.unique(days, return_inverse=True)
    art = pl.read_parquet(d / "labels_art.parquet").filter(pl.col("gwin").is_in(keep))
    lint = pl.read_parquet(d / "labels_int.parquet").filter(pl.col("gwin").is_in(keep))
    return wins, day, remap, art, lint, role


def matrix(df: pl.DataFrame, col: str, remap: dict, T: int, agents=None):
    df = df.filter(pl.col(col).is_not_null() & (pl.col(col) >= 0))
    agents = sorted(set(df["agent"].to_list())) if agents is None else agents
    ai = {a: i for i, a in enumerate(agents)}
    lab = np.full((T, len(agents)), -1, dtype=np.int64)
    g = np.array([remap[x] for x in df["gwin"].to_list()], dtype=np.int64)
    a = np.array([ai[x] for x in df["agent"].to_list()], dtype=np.int64)
    lab[g, a] = df[col].to_numpy().astype(np.int64)
    return lab, agents


def day_shift_null(lab, day, n=N_SHIFT, seed=0):
    """Independent-agents null: each agent's sequence moved by a random whole number of days (cyclic)."""
    rng = np.random.default_rng(seed)
    D = int(day.max()) + 1
    T, N = lab.shape
    starts = [np.flatnonzero(day == d) for d in range(D)]
    out = []
    for _ in range(n):
        sh = np.full_like(lab, -1)
        for a in range(N):
            k = int(rng.integers(0, D))
            for d in range(D):
                src, dst = starts[(d + k) % D], starts[d]
                m = min(len(src), len(dst))
                sh[dst[:m], a] = lab[src[:m], a]
        st = M.label_stats(sh, day)
        out.append((st["lam"], st["copyfrac"], st["beta"]))
    return np.array(out)


def analyse_labelset(name, lab, day, bank, extra=True, seed=0):
    t = M.label_stats(lab, day, bank.m_core)
    c, f, n_tr, n_ch, n_nov = M.moments(lab, day)
    tvec = np.array([c, f] + [t[k] for k in M.STAT_NAMES[:7]])
    nobs = (lab >= 0).sum(1)
    res = {"labelset": name, "N": lab.shape[1], "T": lab.shape[0], "mean_per_win": float(nobs.mean()),
           "n_transitions": n_tr, "n_changes": n_ch, "n_novel": n_nov, "obs": dict(zip(M.FIT_NAMES, map(float, tvec))),
           "copyfrac": t["copyfrac"], "beta_se": t["beta_se"], "n_events": t["n_events"], "n_species": t["n_species"],
           "m_core": bank.m_core, "hist": t["hist"].tolist(), "res_max": t["res_max"]}
    res["testable"] = bool(nobs.mean() >= MIN_PER_WIN and n_ch >= MIN_CHANGES)
    N = lab.shape[1]
    res["mu_B"], res["mu_L"] = M.mu_B(N), M.mu_L(N)
    if not res["testable"]:
        return res
    fits = {}
    for m in M.MODELS:
        mu_h, k_h, L, ij = bank.profile(m, tvec)
        F, H, cf, _ = bank.fresh(m, mu_h, k_h, R=R_FRESH, tag=M._seed(name, m))
        ll, cols = M.synth_loglik(tvec, F)
        ppc = {k: M.ppc_p(tvec[i], F[:, i]) for i, k in enumerate(M.FIT_NAMES)}
        ppc["copyfrac"] = M.ppc_p(t["copyfrac"], cf)
        pred = {k: [float(np.nanmean(F[:, i])), float(np.nanpercentile(F[:, i], 2.5)), float(np.nanpercentile(F[:, i], 97.5)),
                    float(np.nanmedian(F[:, i]))] for i, k in enumerate(M.FIT_NAMES)}
        pred["copyfrac"] = [float(np.nanmean(cf)), float(np.nanpercentile(cf, 2.5)), float(np.nanpercentile(cf, 97.5)), float(np.nanmedian(cf))]
        pj = M.joint_ppc(tvec, F)
        single_ok = bool(min(v for k, v in ppc.items() if k in M.FIT_NAMES and np.isfinite(v)) >= 0.05 / len(M.FIT_NAMES))
        adequate = bool(single_ok and np.isfinite(pj) and pj >= 0.01)  # amendment 3: joint PPC
        fits[m] = {"mu": mu_h, "k": k_h, "ll": ll, "ll_grid_max": float(np.nanmax(L)), "ppc": ppc, "pred": pred, "ppc_joint": pj,
                   "adequate": adequate, "hist_mean": H.mean(0).tolist(), "cols": [M.FIT_NAMES[i] for i in cols],
                   "grid_ij": list(ij)}
        if extra:
            # moment-only fit (secondary, 'unfitted' lambda; known to be weakly identified, synthetic notes)
            mu_m, k_m, dist = bank.fit(m, c, f)
            Mm, _, _, _, _ = bank.predictive(m, mu_m, k_m, R=200, tag=M._seed(name, m, "mom"))
            lam_i = M.STAT_NAMES.index("lam")
            fits[m]["moment_fit"] = {"mu": mu_m, "k": k_m, "dist": dist, "lam_pred": [float(np.nanmean(Mm[:, lam_i])),
                                     float(np.nanpercentile(Mm[:, lam_i], 2.5)), float(np.nanpercentile(Mm[:, lam_i], 97.5))],
                                     "ppc_lam": M.ppc_p(t["lam"], Mm[:, lam_i])}
    res["fits"] = fits
    res["LLR_NH"] = fits["ncd"]["ll"] - fits["hubbell"]["ll"]
    res["LLR_NC"] = fits["ncd"]["ll"] - fits["conformist"]["ll"]
    res["best_model"] = max(M.MODELS, key=lambda m: fits[m]["ll"] if np.isfinite(fits[m]["ll"]) else -np.inf)
    mu_n = fits["ncd"]["mu"]
    res["lambda_star_asym"] = M.lambda_star(mu_n, N)
    res["mu_regime"] = "below mu_B" if mu_n < res["mu_B"] else ("above mu_L" if mu_n >= res["mu_L"] else "between")
    # interior mode of the pooled P_n (n >= 2 has more species-occurrences than n - 1)
    h = np.array(t["hist"])
    res["interior_mode"] = bool(any(h[n] > h[n - 1] and h[n] > 0 for n in range(2, len(h))))
    for m in M.MODELS:
        hm = np.array(fits[m]["hist_mean"])
        fits[m]["interior_mode_pred"] = bool(any(hm[n] > hm[n - 1] for n in range(2, len(hm))))
    if extra:
        nul = day_shift_null(lab, day, seed=M._seed(name, "shift"))
        res["null_ind"] = {
            "lam_mean": float(np.nanmean(nul[:, 0])), "lam_p_greater": float((np.sum(nul[:, 0] >= t["lam"]) + 1) / (len(nul) + 1)),
            "copy_mean": float(np.nanmean(nul[:, 1])), "copy_p_greater": float((np.sum(nul[:, 1] >= t["copyfrac"]) + 1) / (len(nul) + 1)),
            "beta_mean": float(np.nanmean(nul[:, 2])), "beta_p_less": float((np.sum(nul[:, 2] <= t["beta"]) + 1) / (len(nul) + 1))}
        # split-half stationarity of lambda
        D = int(day.max()) + 1
        if D >= 2:
            h1 = day < (D / 2.0)
            l1 = M.label_stats(lab[h1], day[h1])["lam"]
            l2 = M.label_stats(lab[~h1], day[~h1])["lam"]
            res["lam_halves"] = [l1, l2]
    return res


def verdict_p1(r_by_set: dict, primary=PRIMARY) -> dict:
    """Card rule P1 (amended): supported / failed / mixed for the intention-cluster family."""
    p = r_by_set.get(primary)
    if not p or not p.get("testable"):
        return {"verdict": "n/a (insufficient labels)"}
    others = [r_by_set[k] for k in CLUSTERINGS if k in r_by_set and r_by_set[k].get("testable")]
    sup_sets = [r for r in others if r["LLR_NH"] >= 2 and r["LLR_NC"] >= 2]
    fail_sets = [r for r in others if r["LLR_NH"] <= -2 or r["LLR_NC"] <= -2]
    need = int(np.ceil(2 * len(others) / 3))  # 4 of 6 clusterings (2 of 3 where Ward is skipped, #51)
    supported = (p["LLR_NH"] >= 2 and p["LLR_NC"] >= 2 and len(sup_sets) >= need and p["fits"]["ncd"]["adequate"])
    failed = ((p["LLR_NH"] <= -2 or p["LLR_NC"] <= -2) and len(fail_sets) >= need)
    downgraded = False
    if supported and p["fits"]["ncd"]["mu"] >= p["mu_L"] / 2:
        supported, downgraded = False, True  # amendment 2: models converge near mu_L
    v = "supported" if supported else ("failed" if failed else "mixed")
    return {"verdict": v, "n_sets": len(others), "n_sup_sets": len(sup_sets), "n_fail_sets": len(fail_sets),
            "downgraded_high_mu": downgraded, "LLR_NH": p["LLR_NH"], "LLR_NC": p["LLR_NC"], "best": p["best_model"],
            "best_counts": {m: sum(r["best_model"] == m for r in others) for m in M.MODELS}}


def verdict_simple(r: dict) -> str:
    if not r or not r.get("testable"):
        return "n/a (insufficient labels)"
    if r["LLR_NH"] >= 2 and r["LLR_NC"] >= 2 and r["fits"]["ncd"]["adequate"]:
        if r["fits"]["ncd"]["mu"] >= r["mu_L"] / 2:
            return "mixed (NCD best but mu near mu_L)"
        return "supported"
    if r["LLR_NH"] <= -2 or r["LLR_NC"] <= -2:
        return "failed"
    return "mixed"


def p2(r):  # negative frequency dependence
    if not r or not r.get("testable"):
        return "n/a"
    b = r["obs"]["beta"]
    hub, ncd = r["fits"]["hubbell"]["pred"]["beta"], r["fits"]["ncd"]["pred"]["beta"]
    if not np.isfinite(b):
        return "n/a (no recruitment events)"
    if b > hub[2]:
        return "failed (herding: beta above Hubbell 97.5%)"
    if b < hub[3] and ncd[1] <= b <= ncd[2]:
        return "supported"
    if b >= hub[3]:
        return "failed (no negative frequency dependence)"
    return "mixed"


def p3(r):
    if not r or not r.get("testable"):
        return "n/a"
    lam = r["obs"]["lam"]
    ncd, hub = r["fits"]["ncd"]["pred"]["lam"], r["fits"]["hubbell"]["pred"]["lam"]
    inside = ncd[1] <= lam <= ncd[2]
    below_hub = lam < hub[1]
    if inside and (below_hub or r["fits"]["ncd"]["mu"] >= r["mu_L"]):
        return "supported"
    if not inside:
        return "failed (lambda outside NCD 95%)"
    return "mixed (inside NCD and Hubbell intervals)"


def p4(r):
    if not r or not r.get("testable"):
        return "n/a"
    reg = r["mu_regime"]
    if reg == "above mu_L":
        return "n/a (high mu)"
    if reg == "between":
        return "n/a (between mu_B and mu_L: no bimodality required)"
    ok = r["interior_mode"] and np.isfinite(r["obs"]["dbic2"]) and r["obs"]["dbic2"] > 0 and \
        r["fits"]["ncd"]["pred"]["infil"][1] <= r["obs"]["infil"] <= r["fits"]["ncd"]["pred"]["infil"][2]
    return "supported" if ok else "failed"


def run_scope(scope: str) -> dict:
    t0 = time.time()
    wins, day, remap, art, lint, role = load_scope(scope)
    T = wins.height
    out = {"scope": scope, "role": role, "T": T, "days": int(day.max()) + 1, "pt_dates": sorted(set(wins["pt_date"].to_list())),
           "sets": {}}
    # intention clusterings share one mask (agent slot labelled), so one bank
    li = {}
    agents_int = sorted(set(lint["agent"].to_list()))
    for k in CLUSTERINGS:
        if k in lint.columns and (lint[k] >= 0).any():
            li[k], _ = matrix(lint, k, remap, T, agents_int)
    if li:
        mask = (li[PRIMARY] >= 0)
        bank = M.Bank(mask, day, seed=M._seed(scope, "int"))
        for k, lab in li.items():
            # all clusterings share the mask by construction
            assert ((lab >= 0) == mask).all()
            out["sets"][k] = analyse_labelset(f"{scope}/{k}", lab, day, bank, extra=(k == PRIMARY or scope in FREE))
    # artifact labels: carry-forward (primary art) and no carry-forward (sensitivity)
    for nm, df in (("art", art), ("art_nocarry", art.filter(pl.col("carried_age") == 0))):
        if df.height == 0:
            continue
        lab, _ = matrix(df, "project_id", remap, T)
        if (lab >= 0).sum(1).mean() < MIN_PER_WIN:
            out["sets"][nm] = {"labelset": f"{scope}/{nm}", "testable": False, "mean_per_win": float((lab >= 0).sum(1).mean()),
                               "N": lab.shape[1]}
            continue
        if nm == "art_nocarry" and scope not in FREE:
            continue
        bank = M.Bank(lab >= 0, day, seed=M._seed(scope, nm))
        out["sets"][nm] = analyse_labelset(f"{scope}/{nm}", lab, day, bank, extra=True)
    out["P1"] = verdict_p1(out["sets"])
    out["P1_art"] = verdict_simple(out["sets"].get("art"))
    out["P2"] = p2(out["sets"].get(PRIMARY))
    out["P3"] = p3(out["sets"].get(PRIMARY))
    out["P4"] = p4(out["sets"].get(PRIMARY))
    out["P2_art"] = p2(out["sets"].get("art"))
    out["P3_art"] = p3(out["sets"].get("art"))
    out["secs"] = time.time() - t0
    f = DATA / SCOPES[scope][0]
    with open(f / f"round1_{scope}{OUT_SUFFIX}.json", "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print(f"{scope}: {out['secs']:.0f}s P1 {out['P1'].get('verdict')} | art {out['P1_art']}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scopes", nargs="*", default=None)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    scopes = a.scopes or list(SCOPES)
    with get_context("spawn").Pool(min(2, a.workers)) as pool:
        res = pool.map(run_scope, scopes, chunksize=1)
    rows = []
    for r in res:
        for k, s in r["sets"].items():
            if not s.get("testable"):
                rows.append({"scope": r["scope"], "labelset": k, "testable": False})
                continue
            row = {"scope": r["scope"], "labelset": k, "testable": True, "N": s["N"], "mean_per_win": s["mean_per_win"],
                   "LLR_NH": s["LLR_NH"], "LLR_NC": s["LLR_NC"], "best": s["best_model"], "mu_ncd": s["fits"]["ncd"]["mu"],
                   "mu_hub": s["fits"]["hubbell"]["mu"], "mu_B": s["mu_B"], "mu_L": s["mu_L"], "ncd_adequate": s["fits"]["ncd"]["adequate"],
                   "copyfrac": s["copyfrac"], "lam_star_asym": s["lambda_star_asym"]}
            row.update({f"obs_{k2}": v for k2, v in s["obs"].items()})
            for m in M.MODELS:
                row[f"lam_pred_{m}"] = s["fits"][m]["pred"]["lam"][0]
                row[f"beta_pred_{m}"] = s["fits"][m]["pred"]["beta"][0]
                row[f"adequate_{m}"] = s["fits"][m]["adequate"]
                row[f"ppcj_{m}"] = s["fits"][m]["ppc_joint"]
            rows.append(row)
    df = pl.DataFrame(rows, infer_schema_length=None)
    tag = "_".join(scopes) if a.scopes else "all"
    df.write_parquet(DATA / f"results_round1_{tag}.parquet", compression="zstd")
    print(df.select("scope", "labelset", "testable", "LLR_NH", "LLR_NC", "best", "mu_ncd", "mu_L", "obs_lam", "ncd_adequate"))


if __name__ == "__main__":
    main()
