"""H05 recheck of every Newton EP number after the `ep_gauss_crossfit` fix (2026-10-04; non-holdout only).

infra/README "Known issues" (found by H90): the cross-product Newton bound diverges when the observable count d nears
the row count T, and a shared scalar ridge across nested sets fakes a positive collective term. This script recomputes
every EP number the card quotes with the legacy estimator (`ep_newton.ep_gauss_crossfit`, a verbatim copy of
`ep.ep_gauss_crossfit`) and with the corrected held-out estimator (`ep_newton.ep_newton_heldout`: theta fitted on the
other day folds with a per-column ridge floored by the mean pair variance, evaluated on the held-out fold), on the same
data and the same surrogates.

  X5  whole-swarm EP per agent-hour per window (active spins; all pairs), cross-day surrogate null (R draws), excess.
  X2  class-restricted EP per pair-hour within vs cross room (regime II/III windows, both spins), room-label
      permutation p (NPERM), pooled regime-III Fisher combination.
  X3  event EP (class-restricted per pair-hour DiD per arm, whole-swarm pre/post per agent-hour).
The legacy values recomputed here must equal the stored round-1 values (checked and reported). Old nulls used 5
cross-day draws; both estimators get R fresh draws here, so legacy p-values differ from round 1 by Monte Carlo noise.

Usage: uv run python hypotheses/H05-rooms-cut/analysis/recheck_epfix.py [--R 40] [--nperm 300]
       (H05_DATA / H05_MASK switches as in explore_rooms.py; default = round-1 panel, the one the card quotes)
Writes data/processed/H05-rooms-cut[/r1b[/trim]]/recheck_epfix/recheck_bin1.json.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import ep_newton as E  # noqa: E402
import explore_rooms as X  # noqa: E402  (this hypothesis's own loaders; constants only at import)
from ep import g_matrix  # noqa: E402
from scipy.stats import chi2  # noqa: E402

BIN = X.BIN
EST = {"old": lambda G, dd, k=5: E.ep_gauss_crossfit(G, dd, k=k)["sigma"],
       "new": lambda G, dd, k=5: E.ep_newton_heldout(G, dd, k=k)["sigma"]}


def subset_sigmas(fst, masks: dict, legacy_G=None, dd=None):
    """{name: {"old", "new"}} for column masks. New: one shared set of fold stats (one block, per-column ridge)."""
    out = {nm: {} for nm in masks}
    new = E.newton_heldout_from_folds(fst, {nm: np.flatnonzero(m) for nm, m in masks.items()})
    for nm, m in masks.items():
        out[nm]["new"] = new[nm]["sigma"]
        out[nm]["old"] = E.ep_gauss_crossfit(legacy_G[:, m], dd)["sigma"] if legacy_G is not None else np.nan
    return out


# ============================================================================ X5
def x5(days, mats, goal, R, rng, spin="active"):
    out = {}
    windows = {f"#{g}": X.gdays(days, goal, g) for g in (35, 36, 37, 38, 39, 40, 41, 42, 44)}
    wk = {}
    for d in X.gdays(days, goal, 51):
        wk.setdefault(X.week_of(d), []).append(d)
    for k, v in wk.items():
        windows[f"#51 {k}"] = v
    for name, ds in windows.items():
        if len(ds) < 2:
            continue
        ag, Sp, Sn, dd, mm = X.stack_window(mats, ds, spin)
        if len(ag) < 4:
            continue
        N = len(ag)
        G = g_matrix(Sp, Sn, dtype=np.float64)
        k = min(5, len(ds))
        rec = {"days": len(ds), "N": int(N), "T": int(len(G)), "d": int(G.shape[1])}
        scale = 60 / BIN / N
        r_new = E.ep_newton_heldout(G, dd, k=k)
        rec["old_per_agent_hour"] = EST["old"](G, dd, k) * scale
        rec["new_per_agent_hour"] = r_new["sigma"] * scale
        rec["new_se_per_agent_hour"] = r_new["se"] * scale
        nd = len(np.unique(dd))
        Lmin = min(int((dd == q).sum()) for q in np.unique(dd))
        Xa = np.stack([np.vstack([Sp[dd == q][:Lmin], Sn[dd == q][Lmin - 1:Lmin]]) for q in np.unique(dd)])
        dlab = np.repeat(np.arange(nd), Lmin)
        Gt = g_matrix(Xa[:, :-1].reshape(-1, N), Xa[:, 1:].reshape(-1, N), dtype=np.float64)
        trunc = {e: EST[e](Gt, dlab, min(5, nd)) for e in EST}
        nulls = {e: [] for e in EST}
        for _ in range(R):
            Y = np.empty_like(Xa)
            for a in range(N):
                perm = rng.permutation(nd)
                for _t in range(50):
                    if not np.any(perm == np.arange(nd)):
                        break
                    perm = rng.permutation(nd)
                Y[:, :, a] = Xa[perm, :, a]
            Gx = g_matrix(Y[:, :-1].reshape(-1, N), Y[:, 1:].reshape(-1, N), dtype=np.float64)
            for e in EST:
                nulls[e].append(EST[e](Gx, dlab, min(5, nd)))
        for e in EST:
            v = np.array(nulls[e])
            rec[f"{e}_truncated_per_agent_hour"] = trunc[e] * scale
            rec[f"{e}_null_mean_per_agent_hour"] = float(v.mean() * scale)
            rec[f"{e}_null_sd_per_agent_hour"] = float(v.std(ddof=1) * scale)
            rec[f"{e}_excess_per_agent_hour"] = float((trunc[e] - v.mean()) * scale)
            rec[f"{e}_z"] = float((trunc[e] - v.mean()) / v.std(ddof=1)) if v.std() > 0 else np.nan
            rec[f"{e}_p_crossday"] = float((1 + np.sum(v >= trunc[e])) / (R + 1))
        out[name] = rec
        print("X5", name, {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in rec.items()}, flush=True)
    return out


# ============================================================================ X2
def x2(days, mats, goal, nperm, rng, spin):
    res = {}
    for gno in X.X2_WINDOWS:
        ds = [d for d in days if goal[d] == gno]
        if not ds:
            continue
        modes = X.agent_room_mode(mats, ds)
        pure = sorted(a for a, (r, p) in modes.items() if p >= 0.9)
        ag, Sp, Sn, dd, mm = X.stack_window(mats, ds, spin, agents=np.array(pure))
        if len(ag) < 4:
            continue
        lab = np.array([modes[a][0] for a in ag])
        ii, jj = np.triu_indices(len(ag), 1)
        G = g_matrix(Sp, Sn, ii, jj, dtype=np.float64)
        fst = E.fold_stats(G, dd, 5)
        sc = 60 / BIN

        def cls(lb, legacy=True):
            s = lb[ii] == lb[jj]
            if s.all() or (~s).all():
                return None
            r = subset_sigmas(fst, {"w": s, "c": ~s}, G if legacy else None, dd)
            return {e: {"within": r["w"][e] / s.sum() * sc, "cross": r["c"][e] / (~s).sum() * sc} for e in EST}
        obs = cls(lab)
        rec = {"N": int(len(ag)), "n_within": int((lab[ii] == lab[jj]).sum()), "n_cross": int((lab[ii] != lab[jj]).sum()),
               "agent_hour": {e: EST[e](G, dd) * 60 / BIN / len(ag) for e in EST}}
        nulls = {e: [] for e in EST}
        for _ in range(nperm):
            r = cls(rng.permutation(lab))
            if r is None:
                continue
            for e in EST:
                nulls[e].append(r[e]["within"] - r[e]["cross"])
        for e in EST:
            diff = obs[e]["within"] - obs[e]["cross"]
            v = np.array(nulls[e])
            rec[e] = {"within": obs[e]["within"], "cross": obs[e]["cross"], "diff": float(diff),
                      "p_perm": float((1 + np.sum(v >= diff)) / (1 + len(v)))}
        res[str(gno)] = rec
        print("X2", spin, gno, {e: {kk: round(vv, 4) for kk, vv in rec[e].items()} for e in EST}, flush=True)
    pooled = {}
    keys = ["37", "38", "39", "41", "42", "44"]
    for e in EST:
        diffs = [res[k][e]["diff"] for k in keys if k in res]
        ws = [res[k]["n_cross"] for k in keys if k in res]
        ps = [res[k][e]["p_perm"] for k in keys if k in res]
        pooled[e] = {"mean_diff": float(np.average(diffs, weights=ws)), "n_windows": len(diffs),
                     "n_positive": int(np.sum(np.array(diffs) > 0)),
                     "fisher_p": float(chi2.sf(-2 * np.sum(np.log(ps)), 2 * len(ps)))}
    return res, pooled


# ============================================================================ X3
def x3(days, mats, goal, pdf, spin):
    out = {}
    for ev in X.events(days, goal):
        pre, post = ev["pre"], ev["post"]
        t = pdf.filter((pl.col("spin") == spin) & pl.col("pt_date").is_in(pre + post))
        if t.height == 0 or not pre or not post:
            continue
        t = t.with_columns(pl.col("pt_date").is_in(post).alias("is_post"))
        mpre, mpost = X.agent_room_mode(mats, pre), X.agent_room_mode(mats, post)
        agents = np.array(sorted(set(mpre) & set(mpost)))
        t = t.filter(pl.col("i").is_in(agents.tolist()) & pl.col("j").is_in(agents.tolist()))
        pc = t.group_by("i", "j", "is_post").agg(pl.col("coloc").mean())
        cpre = {(i, j): c for i, j, p, c in pc.iter_rows() if not p}
        cpost = {(i, j): c for i, j, p, c in pc.iter_rows() if p}
        pairs = sorted(set(cpre) & set(cpost))
        if not pairs:
            continue
        cls = np.array([X.classify(cpre[p], cpost[p]) for p in pairs])
        if "pseudo" in ev:
            ps = set(ev["pseudo"])
            cls = np.array(["pseudo" if (c == "stay" and (p[0] in ps or p[1] in ps)) else c for c, p in zip(cls, pairs)])
        stacks = {}
        for lab in ("pre", "post"):
            ag, Sp, Sn, dd, mm = X.stack_window(mats, ev[lab], spin, min_flips=10, agents=agents)
            stacks[lab] = (ag, Sp, Sn, dd)
        common = np.array(sorted(set(stacks["pre"][0]) & set(stacks["post"][0])))
        if len(common) < 4:
            continue
        pidx = {p: k for k, p in enumerate(pairs)}
        ii, jj = np.triu_indices(len(common), 1)
        pcl = np.array([cls[pidx[(common[a], common[b])]] if (common[a], common[b]) in pidx else "other"
                        for a, b in zip(ii, jj)])
        rec = {}
        per = {}
        for lab in ("pre", "post"):
            ag, Sp, Sn, dd = stacks[lab]
            cols = np.searchsorted(ag, common)
            G = g_matrix(Sp[:, cols], Sn[:, cols], ii, jj, dtype=np.float64)
            for e in EST:
                rec[f"{e}_agent_hour_{lab}"] = EST[e](G, dd) * 60 / BIN / len(common)
            masks = {c: pcl == c for c in ("add", "cut", "cross", "pseudo", "stay") if (pcl == c).any()}
            r = subset_sigmas(E.fold_stats(G, dd, 5), masks, G, dd)
            per[lab] = {c: {e: r[c][e] / masks[c].sum() * 60 / BIN for e in EST} for c in masks}
        for arm in ("add", "cut", "cross", "pseudo"):
            if arm not in per["pre"] or "stay" not in per["pre"] or arm not in per["post"] or "stay" not in per["post"]:
                continue
            rec[arm] = {"n_arm": int((pcl == arm).sum()), "n_stay": int((pcl == "stay").sum())}
            for e in EST:
                rec[arm][f"{e}_did_per_pairhour"] = float((per["post"][arm][e] - per["pre"][arm][e])
                                                          - (per["post"]["stay"][e] - per["pre"]["stay"][e]))
        out[ev["id"]] = rec
        print("X3", spin, ev["id"], {k: (round(v, 4) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
    return out


def check_legacy(res, stored):
    """Max |difference| between legacy values recomputed here and the stored round-1 values."""
    dev = []
    for nm, r in res["X5"].items():
        s = stored["X5"]["active"].get(nm)
        if s:
            dev.append(abs(r["old_per_agent_hour"] - s["newton_cf_per_agent_hour"]))
            dev.append(abs(r["old_truncated_per_agent_hour"] - s["newton_cf_truncated_per_agent_hour"]))
    for spin in ("active", "talk"):
        for g, r in res["X2"][spin].items():
            s = stored["X2"][spin].get(g, {}).get("ep_newton_pairhour")
            if s:
                dev += [abs(r["old"]["within"] - s["within"]), abs(r["old"]["cross"] - s["cross"])]
        for eid, r in res["X3"][spin].items():
            s = (stored["X3"][spin].get(eid) or {}).get("ep")
            if s:
                dev.append(abs(r["old_agent_hour_pre"] - s["agent_hour_pre"]))
                for arm in ("add", "cut", "cross", "pseudo"):
                    if arm in r and arm in s:
                        dev.append(abs(r[arm]["old_did_per_pairhour"] - s[arm]["did_per_pairhour"]))
    return float(np.max(dev)) if dev else None, len(dev)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, default=40)
    ap.add_argument("--nperm", type=int, default=300)
    ap.add_argument("--bin", type=int, default=1)
    a, _ = ap.parse_known_args()
    t0 = time.time()
    rng = np.random.default_rng(20261004)
    days, mats, goal, regime = X.load_days()      # asserts no holdout day (guard_holdout)
    sys.path.insert(0, str(ROOT / "infra/shared"))
    from common import holdout_mask
    assert not any(holdout_mask(days, [goal[d] for d in days])), "holdout day in recheck"
    pdf = pl.read_parquet(X.DATA / f"pair_day_bin{BIN}.parquet")
    res = {"bin_minutes": BIN, "data_version": X.DATA_VERSION, "mask": X.MASK, "R_crossday": a.R, "nperm": a.nperm,
           "n_days": len(days), "X5": x5(days, mats, goal, a.R, rng), "X2": {}, "X2_pooled_III": {}, "X3": {}}
    for spin in X.SPINS:
        res["X2"][spin], res["X2_pooled_III"][spin] = x2(days, mats, goal, a.nperm, rng, spin)
        res["X3"][spin] = x3(days, mats, goal, pdf, spin)
    stored_p = X.DATA / f"explore_bin{BIN}.json"
    if stored_p.exists():
        res["legacy_max_abs_dev_vs_stored"], res["legacy_n_compared"] = check_legacy(res, json.loads(stored_p.read_text()))
        print("legacy reproduction: max |dev| =", res["legacy_max_abs_dev_vs_stored"], "over", res["legacy_n_compared"])
    res["runtime_s"] = time.time() - t0
    od = X.DATA / "recheck_epfix"
    od.mkdir(parents=True, exist_ok=True)
    (od / f"recheck_bin{BIN}.json").write_text(json.dumps(res, indent=1, default=float))
    prov = {"built_by": "hypotheses/H05-rooms-cut/analysis/recheck_epfix.py", "git_commit": E_git(),
            "inputs": [str((X.PANEL_DIR / "panel.parquet").relative_to(ROOT)), str(stored_p.relative_to(ROOT))],
            "params": {"R": a.R, "nperm": a.nperm, "bin": BIN, "seed": 20261004, "ridge_c": E.RIDGE_C,
                       "data_version": X.DATA_VERSION, "mask": X.MASK},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (od / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print("done", f"{time.time() - t0:.0f}s")


def E_git():
    from common import git_commit
    return git_commit()


if __name__ == "__main__":
    main()
