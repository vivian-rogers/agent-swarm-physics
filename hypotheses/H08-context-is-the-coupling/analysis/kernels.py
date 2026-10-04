"""C8 (HH92) on real data: per-period message -> activity kernels (H04's design, imported) against the
zero-parameter read-out prediction, rival models by day-split CV, and the pause-stratified onset test.

  uv run python hypotheses/H08-context-is-the-coupling/analysis/kernels.py [--period 51 ...] [--pooled]

Writes data/processed/H08-context-is-the-coupling/G<NN>/c8.json (and c8_pooled.json with --pooled).
Non-holdout days only (h08lib.period_days asserts it).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c8lib import *  # noqa: E402,F403

B = 500
N_SPLIT = 100
KICK_SETS = {"nudge_target_iso": ("nudge", "target"), "human_mentioned_iso": ("human", "mentioned"),
             "human_all_iso": ("human", None)}
C8_PERIODS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]   # nudges exist from 2026-02-13
MIN_CELLS = 10


def kick_rows(resp: pl.DataFrame, kind: str, role: str | None) -> pl.DataFrame:
    r = resp.filter(pl.col("kind") == kind)
    if role:
        r = r.filter(pl.col("role") == role)
    return r.with_columns(pl.col("day").cast(pl.Int64))


def analyse_set(P: Prep, c, ctl, ids, kr, nd, W, h, rng, label, with_cv=True):
    r = matched(c, ctl, ids, nd, label)
    Gb = h04lib.curves(r, W)
    ro = treated_readout(P, c, ids, kr)
    hk = hkey_cells(P, c, ids)
    M_obs = F_hr_cells(ro["tau_obs"], hk // 16, h, hk)
    M_sched = F_hr_cells(ro["tau_sched"], hk // 16, h, hk)
    tau_ren = np.stack([renewal_tau(P.T, rng, n=len(ids)) for _ in range(10)])
    M_ren = np.mean([F_hr_cells(tau_ren[j], hk // 16, h, hk) for j in range(10)], 0)
    CM = control_matrix(c, ctl, ids)
    Fb = {"hr": F_hr_boot(M_obs, ro["day"], W, nd), "step": F_boot(ro["tau_obs"], ro["day"], W, nd),
          "hr_sched": F_hr_boot(M_sched, ro["day"], W, nd), "hr_ren": F_hr_boot(M_ren, ro["day"], W, nd)}
    E0 = np.nanmean(CM, 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        Fb["imm_hr"] = np.repeat((1 - E0)[None, :], len(W), 0)
    out = {"n_cells": int(len(ids)), "n_days_with": int(len(np.unique(ro["day"]))), "fallback": r.fallback,
           "shape": shape_tests(Gb, Fb, W),
           "pre15": ci(np.nansum(Gb[:, L0 - 15:L0], 1)), "placebo_m30_m16": ci(np.nansum(Gb[:, L0 - 30:L0 - 15], 1)),
           "G": Gb[0].tolist(), "G_lo": np.nanpercentile(Gb[1:], 2.5, 0).tolist(),
           "G_hi": np.nanpercentile(Gb[1:], 97.5, 0).tolist(),
           "F_hr": Fb["hr"][0].tolist(), "F_step": Fb["step"][0].tolist(), "F_hr_sched": Fb["hr_sched"][0].tolist(),
           "F_hr_ren": Fb["hr_ren"][0].tolist(), "E0": E0.tolist(),
           "readout": {"paused_share": float(np.mean(ro["paused"])),
                       "W_obs_s_q": [float(x) for x in np.nanpercentile(ro["W_obs"], [10, 25, 50, 75, 90])] if np.isfinite(ro["W_obs"]).any() else None,
                       "tau_obs_q": [float(x) for x in np.nanpercentile(ro["tau_obs"], [10, 25, 50, 75, 90])] if np.isfinite(ro["tau_obs"]).any() else None,
                       "never_share": float(np.mean(~np.isfinite(ro["tau_obs"]))),
                       "rem_s_paused_q": [float(x) for x in np.percentile(ro["rem_s"][ro["paused"]], [25, 50, 75])] if ro["paused"].any() else None}}
    if with_cv and len(ids) >= MIN_CELLS:
        out["cv"] = cross_validate(r, Gb, ro["tau_obs"], ro["day"], nd, M_obs, CM, n_split=N_SPLIT, seed=7)
        out["fit"] = full_fit(Gb, ro["tau_obs"], M_obs, CM)
    return out, {"r": r, "tau": ro["tau_obs"], "day": ro["day"], "M": M_obs, "CM": CM, "ro": ro, "hk": hk}


def run_period(g: int, chat=None, days: list[str] | None = None, folder: Path | None = None) -> dict | None:
    days = days if days is not None else period_days(g)
    folder = folder or (OUT / gname(g))
    if not days:
        return None
    t0 = time.time()
    P = Prep(days, chat)
    P.attach()
    nd = len(P.D)
    W = h04lib.boot_weights(nd, B, seed=20261004 + g)
    rng = np.random.default_rng(g)
    out = {"period": gname(g), "n_days": nd, "days": [days[0], days[-1]],
           "n_messages": {k: int(v) for k, v in P.msgs.group_by("kind").len().iter_rows()}}
    c, ctl = build_kernel_inputs(P)                              # H04's design
    sets = h04lib.build_sets(P.D, P.resp, c)
    h = headroom_profiles(P, c, seed=g)
    out["headroom_class"] = {str(k): v.tolist() for k, v in enumerate(h["class"])}
    out["sets"] = {}
    keep = {}
    for name, (kind, role) in KICK_SETS.items():
        ids = sets.get(name, {"ids": np.array([], int)})["ids"]
        if len(ids) < MIN_CELLS:
            out["sets"][name] = {"n_cells": int(len(ids)), "underpowered": True}
            continue
        res, raw = analyse_set(P, c, ctl, ids, kick_rows(P.resp, kind, role), nd, W, h, rng, name)
        out["sets"][name] = res
        keep[name] = raw
    # P5: pause-matched kernels, kicks to agents with >= 5 min of declared pause left vs not paused
    if "nudge_target_iso" in keep:
        c2, ctl2 = build_kernel_inputs(P, pause_matched=True)
        ids2 = sets["nudge_target_iso"]["ids"]   # same cells (cell ids are identical: same build_cells order)
        ro = keep["nudge_target_iso"]["ro"]
        strata = {"paused_ge5min": ro["paused"] & (ro["rem_s"] >= 300), "not_paused": ~ro["paused"],
                  "all": np.ones(len(ids2), bool)}
        out["pause_matched"] = {}
        for sname, msk in strata.items():
            sub = ids2[msk]
            if len(sub) < MIN_CELLS:
                out["pause_matched"][sname] = {"n_cells": int(len(sub)), "underpowered": True}
                continue
            r2 = matched(c2, ctl2, sub, nd, sname)
            Gb2 = h04lib.curves(r2, W)
            Fb2 = {"hr": F_hr_boot(keep["nudge_target_iso"]["M"][msk], ro["day"][msk], W, nd)}
            st = shape_tests(Gb2, Fb2, W)
            out["pause_matched"][sname] = {"n_cells": int(len(sub)), "A30": st["A30"], "A60": st["A60"],
                                           "phi_1_5": st["phi_1_5"], "phi_1_5_pred_hr": st["phi_1_5_pred_hr"],
                                           "phi_1_5_diff_hr": st["phi_1_5_diff_hr"], "plateau": st["plateau_mean"],
                                           "early_1_5_mean": ci(np.nanmean(Gb2[:, L0 + 1:L0 + 6], 1)),
                                           "G": Gb2[0].tolist(), "_Gb_rows": Gb2}
        a, b = out["pause_matched"].get("paused_ge5min", {}), out["pause_matched"].get("not_paused", {})
        if "_Gb_rows" in a and "_Gb_rows" in b:
            ea = np.nanmean(a["_Gb_rows"][:, L0 + 1:L0 + 6], 1); eb = np.nanmean(b["_Gb_rows"][:, L0 + 1:L0 + 6], 1)
            out["pause_matched"]["early_diff_notpaused_minus_paused"] = ci(eb - ea)
        for v in out["pause_matched"].values():
            if isinstance(v, dict):
                v.pop("_Gb_rows", None)
        # sensitivity: exact-idleness + pause matching
        c3, ctl3 = build_kernel_inputs(P, pause_matched=True, fine=True)
        r3 = matched(c3, ctl3, ids2, nd, "fine")
        Gb3 = h04lib.curves(r3, W)
        st3 = shape_tests(Gb3, {"hr": F_hr_boot(keep["nudge_target_iso"]["M"], ro["day"], W, nd)}, W)
        out["fine_matched"] = {"A30": st3["A30"], "phi_1_5": st3["phi_1_5"], "phi_1_5_pred_hr": st3["phi_1_5_pred_hr"],
                               "phi_1_5_diff_hr": st3["phi_1_5_diff_hr"], "phi_6_15": st3["phi_6_15"],
                               "pre15": ci(np.nansum(Gb3[:, L0 - 15:L0], 1)), "G": Gb3[0].tolist()}
    out["runtime_s"] = time.time() - t0
    jdump(out, folder / "c8.json")
    s = out["sets"].get("nudge_target_iso", {})
    if "shape" in s:
        sh = s["shape"]
        print(f"{gname(g)}: nudge cells {s['n_cells']}, A30 {sh['A30'][0]:.2f} [{sh['A30'][1]:.2f},{sh['A30'][2]:.2f}], "
              f"phi15 {sh['phi_1_5'][0]:.2f} pred {sh['phi_1_5_pred_hr'][0]:.2f}, "
              f"cv best {max(s.get('cv', {}).get('best_share', {'-': 0}).items(), key=lambda x: x[1])} "
              f"({time.time() - t0:.0f}s)", flush=True)
    else:
        print(f"{gname(g)}: nudge cells {s.get('n_cells')} (underpowered) ({time.time() - t0:.0f}s)", flush=True)
    # raw pieces for pooling
    return {"out": out, "keep": keep, "nd": nd}


def pooled(results: dict, set_name="nudge_target_iso", periods=None, label="pooled_regime3"):
    """Exception (d): concatenate per-period matched day sums (each period's own controls) and analyse as one."""
    parts = [(g, v) for g, v in results.items() if v and set_name in v["keep"] and (periods is None or g in periods)]
    if not parts:
        return None
    off = 0
    ds, dc, taus, days, Ms, CMs, y1, c1, n1 = [], [], [], [], [], [], [], [], []
    for g, v in parts:
        k = v["keep"][set_name]
        ds.append(k["r"].day_sum); dc.append(k["r"].day_cnt); y1.append(k["r"].day_y1); c1.append(k["r"].day_c1)
        n1.append(k["r"].day_n1)
        taus.append(k["tau"]); days.append(k["day"] + off); Ms.append(k["M"]); CMs.append(k["CM"])
        off += v["nd"]
    r = h04lib.Resp(label, int(sum(len(t) for t in taus)), 0, np.nan, np.vstack(ds), np.vstack(dc), np.concatenate(y1),
                    np.concatenate(c1), np.concatenate(n1))
    nd = off
    W = h04lib.boot_weights(nd, B, seed=20261004)
    Gb = h04lib.curves(r, W)
    tau = np.concatenate(taus); day = np.concatenate(days); M = np.concatenate(Ms); CM = np.concatenate(CMs)
    Fb = {"hr": F_hr_boot(M, day, W, nd), "step": F_boot(tau, day, W, nd)}
    out = {"label": label, "periods": [gname(g) for g, _ in parts], "n_cells": int(len(tau)), "n_days": nd,
           "shape": shape_tests(Gb, Fb, W), "pre15": ci(np.nansum(Gb[:, L0 - 15:L0], 1)),
           "G": Gb[0].tolist(), "G_lo": np.nanpercentile(Gb[1:], 2.5, 0).tolist(),
           "G_hi": np.nanpercentile(Gb[1:], 97.5, 0).tolist(), "F_hr": Fb["hr"][0].tolist(),
           "F_step": Fb["step"][0].tolist(),
           "cv": cross_validate(r, Gb, tau, day, nd, M, CM, n_split=N_SPLIT, seed=11), "fit": full_fit(Gb, tau, M, CM)}
    # H04's published pooled regime-III kernel (explore_kernels.json) vs this pooled prediction
    try:
        h4 = json.loads((ROOT / "data/processed/H04-reversible-forcing/explore_kernels.json").read_text())["III"]["G"][set_name]
        g4 = np.array(h4["G"], float)
        f = np.array(out["F_hr"]); sl = slice(L0 + 1, L0 + 46)
        A = float(np.nansum(g4[sl] * f[sl]) / np.nansum(f[sl] ** 2))
        out["h04_published"] = {"G": h4["G"], "A30": h4.get("A30"), "phi_1_5": float(phi(g4[None], 1, 5)[0]),
                                "phi_6_15": float(phi(g4[None], 6, 15)[0]), "A_fit_to_F_hr": A,
                                "phi_1_5_pred_hr": float(phi(f[None], 1, 5)[0]), "phi_6_15_pred_hr": float(phi(f[None], 6, 15)[0])}
    except Exception as e:  # noqa: BLE001
        out["h04_published"] = {"error": str(e)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--pooled", action="store_true")
    a = ap.parse_args()
    chat = chat_table()
    res = {}
    for g in (a.period or C8_PERIODS):
        res[g] = run_period(g, chat)
    if a.pooled:
        out = {"regime3_all": pooled(res, periods=[g for g in res if g in REGIME_III]),
               "regime3_4h": pooled(res, periods=[g for g in res if g in REGIME_III and g != 51], label="pooled_regime3_4h"),
               "pre_regime3": pooled(res, periods=[g for g in res if g not in REGIME_III], label="pooled_pre_regime3")}
        for name in ("human_mentioned_iso", "human_all_iso"):
            out[f"{name}_all"] = pooled(res, set_name=name, label=f"pooled_{name}")
        jdump(out, OUT / "c8_pooled.json")
        p = out["regime3_all"]
        if p:
            print(f"POOLED regime III: cells {p['n_cells']} A30 {p['shape']['A30']} phi15 {p['shape']['phi_1_5']} "
                  f"pred {p['shape']['phi_1_5_pred_hr']} cv {p['cv'].get('best_share')}", flush=True)
    write_provenance("c8 (G<NN>/c8.json, c8_pooled.json)", "hypotheses/H08-context-is-the-coupling/analysis/kernels.py",
                     ["activity_bins", "chat_core", "exposure", "calendar", "actions", "events_core", "roster",
                      "H04 explore_kernels.json"],
                     {"B": B, "n_split": N_SPLIT, "design": "h04lib (imported)", "amendments": "A1-A5",
                      "periods": [gname(g) for g in res]})


if __name__ == "__main__":
    main()
