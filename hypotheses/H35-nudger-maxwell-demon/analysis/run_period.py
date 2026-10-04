"""H35 per-period analysis: information used, work bought, gate model, policy values, efficiencies.

Reads data/processed/H35-nudger-maxwell-demon/<period>/{grid,gates,nudges}.parquet (built by scheme/build.py) and writes
results.json next to them. Day-block bootstrap for CIs. Same estimators as the synthetic validation (h35lib).

Usage: uv run python hypotheses/H35-nudger-maxwell-demon/analysis/run_period.py G51 [G38 ...] [--B 300]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h35lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

CELLS_K = (1, 2, 3, 4)
CELLS_D = (0, 1, 2)


def gate_cells(gt: pl.DataFrame, gcol: str):
    p = np.zeros((4, 3)); m = np.zeros((4, 3)); gs = np.zeros((4, 3))
    for kb, db, mm, gv in gt.select("Kb", "declb", "M", gcol).iter_rows():
        if kb < 1 or gv is None or not np.isfinite(gv):
            continue
        p[kb - 1, db] += 1; m[kb - 1, db] += mm; gs[kb - 1, db] += gv
    ok = p > 0
    return p, m, np.where(ok, gs / np.maximum(p, 1), np.nan), ok


def eff_from_gates(gt: pl.DataFrame, gcol: str) -> dict:
    p, m, g, ok = gate_cells(gt, gcol)
    e = L.efficiencies(p[ok], m[ok] / p[ok], g[ok])
    if "error" in e:
        return e
    e["cell_g"] = np.where(ok, g, np.nan).round(5).tolist()
    e["cell_n"] = p.astype(int).tolist()
    e["cell_nudged"] = m.astype(int).tolist()
    e["gate_once"] = {}
    for ks in (1, 2, 3):
        s = gt.filter((pl.col("k_r") == ks) & pl.col(gcol).is_not_null() & pl.col(gcol).is_not_nan())
        e["gate_once"][ks] = float(s[gcol].mean()) if s.height else float("nan")
        e[f"eligible_gates_k{ks}"] = s.height
    e["logged_mean_direct"] = float(gt.filter(pl.col("M") == 1)[gcol].mean()) if gt["M"].sum() else float("nan")
    for ks in (1, 2):
        e[f"ratio_gate_once{ks}_vs_logged"] = (e["gate_once"][ks] / e["V_log_per_nudge"]
                                               if e["V_log_per_nudge"] and np.isfinite(e["V_log_per_nudge"]) else float("nan"))
    cur = e.get("_curve")
    if cur is not None:
        r = e["r"]
        e["frontier_bits_per_nudge"] = (cur["I_nats"] / L.LN2 / r).round(4).tolist()
        e["frontier_value_per_nudge"] = (cur["V"] / r).round(5).tolist()
    return e


def gate_block(gates: pl.DataFrame, rng, B: int) -> dict:
    out = {"n_gates": gates.height, "n_nudged_gates": int(gates["M"].sum()),
           "n_dir_other_gates": int(gates["dir_other"].sum()),
           "censored": int((gates["outcome_r"] == "censored").sum())}
    # descriptive: escape by K bin and nudge
    out["escape_by_K_nudge"] = [dict(zip(["Kb", "M", "n", "escape"], r)) for r in
                                gates.filter(pl.col("outcome_r") != "censored").group_by("Kb", "M")
                                .agg(pl.len(), pl.col("escape").mean()).sort("Kb", "M").iter_rows()]
    fits = {}
    for v in ("shared", "separate"):
        f = L.gate_fit(gates, v)
        fits[v] = {"beta": dict(zip(f["names"], f["beta"].round(4).tolist())),
                   "se": dict(zip(f["names"], f["se"].round(4).tolist())), "n": f["n"], "n_events": f["n_events"]}
    out["fit"] = fits
    sh = fits["shared"]
    z = sh["beta"]["kick_x_lnk"] / sh["se"]["kick_x_lnk"] if sh["se"]["kick_x_lnk"] > 0 else float("nan")
    out["kick_slope_z"] = z
    out["B_per_escape"] = L.gate_minutes_per_escape(gates)
    g = gates.with_columns(pl.Series("dp", L.crossfit_dp(gates, "shared")), pl.Series("dp_sep", L.crossfit_dp(gates, "separate")))
    Bmap = {k: v for k, v in out["B_per_escape"].items()}
    g = g.with_columns(pl.col("Kb").replace_strict(Bmap, default=None, return_dtype=pl.Float64).alias("B_k"))
    g = g.with_columns((pl.col("dp") * pl.col("B_k")).alias("gmin"), (pl.col("dp_sep") * pl.col("B_k")).alias("gmin_sep"))
    gk = g.filter((pl.col("Kb") >= 1) & pl.col("dp").is_not_null() & pl.col("dp").is_not_nan())
    out["eff_escapes"] = eff_from_gates(gk, "dp")
    out["eff_escapes_separate"] = eff_from_gates(gk.filter(pl.col("dp_sep").is_not_null() & pl.col("dp_sep").is_not_nan()), "dp_sep")
    out["eff_minutes"] = eff_from_gates(gk.filter(pl.col("gmin").is_not_null() & pl.col("gmin").is_not_nan()), "gmin")
    out["eff_minutes_separate"] = eff_from_gates(gk.filter(pl.col("gmin_sep").is_not_null() & pl.col("gmin_sep").is_not_nan()), "gmin_sep")
    # gate-level information add-ons (controller memory, agent identity)
    x = L.codes(gk["Kb"].to_numpy(), gk["declb"].to_numpy())
    mg = gk["M"].to_numpy()
    out["gate_info"] = {"I_x_bits_MM": L.mi(x, mg) / L.LN2,
                        "I_N_given_x_bits_MM": L.cmi(gk["Nb"].to_numpy(), x, mg) / L.LN2,
                        "I_agent_given_x_bits_MM": L.cmi(np.unique(gk["agent"].to_numpy(), return_inverse=True)[1], x, mg) / L.LN2,
                        "r_gate": float(mg.mean())}
    # day-block bootstrap of the whole gate pipeline (refit, cross-fit, efficiencies)
    days = np.array(sorted(gates["pt_date"].unique().to_list()))
    keys = ("V_rand_per_nudge", "V_log_per_nudge", "dV_per_nudge", "bits_per_nudge", "eta_SU", "eta_KW",
            "kappa_min_per_bit_per_nudge", "Vstar_at_I_per_nudge", "sigma_g", "ratio_gate_once1_vs_logged",
            "ratio_gate_once2_vs_logged", "logged_mean_direct")
    boots = {"escapes": {k: [] for k in keys}, "minutes": {k: [] for k in keys}, "kick_x_lnk": [], "nudge_offset": [],
             "g1_minus_g4": []}
    for b in range(B):
        pick = rng.choice(days, len(days), replace=True)
        parts = []
        for j, d in enumerate(pick):
            parts.append(gates.filter(pl.col("pt_date") == d).with_columns(pl.lit(f"{d}#{j}").alias("pt_date")))
        gb = pl.concat(parts)
        try:
            f = L.gate_fit(gb, "shared")
            boots["kick_x_lnk"].append(f["beta"][f["names"].index("kick_x_lnk")])
            boots["nudge_offset"].append(f["beta"][f["names"].index("nudge_offset")])
            Bb = L.gate_minutes_per_escape(gb)
            gb = gb.with_columns(pl.Series("dp", L.crossfit_dp(gb, "shared")))
            gb = gb.with_columns(pl.col("Kb").replace_strict(Bb, default=None, return_dtype=pl.Float64).alias("B_k"))
            gb = gb.with_columns((pl.col("dp") * pl.col("B_k")).alias("gmin"))
            gkb = gb.filter((pl.col("Kb") >= 1) & pl.col("dp").is_not_null() & pl.col("dp").is_not_nan())
            for lab, col in (("escapes", "dp"), ("minutes", "gmin")):
                s = gkb.filter(pl.col(col).is_not_null() & pl.col(col).is_not_nan())
                e = eff_from_gates(s, col)
                for k in keys:
                    boots[lab][k].append(e.get(k, np.nan))
                if lab == "escapes":
                    cg = np.array(e["cell_g"], float)
                    boots["g1_minus_g4"].append(np.nanmean(cg[0]) - np.nanmean(cg[3]))
        except Exception:
            continue
    def q(v):
        v = np.array(v, float)
        v = v[np.isfinite(v)]
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) > 10 else [None, None]
    out["boot"] = {"B": B, "escapes": {k: q(v) for k, v in boots["escapes"].items()},
                   "minutes": {k: q(v) for k, v in boots["minutes"].items()},
                   "kick_x_lnk": q(boots["kick_x_lnk"]), "nudge_offset": q(boots["nudge_offset"]),
                   "g1_minus_g4": q(boots["g1_minus_g4"])}
    out["g1_minus_g4_point"] = float(np.nanmean(np.array(out["eff_escapes"]["cell_g"], float)[0])
                                     - np.nanmean(np.array(out["eff_escapes"]["cell_g"], float)[3]))
    return out


def nudge_timing(grid: pl.DataFrame, gates: pl.DataFrame | None, nud: pl.DataFrame) -> dict:
    """Where nudges land: state shares, and seconds from the agent's latest PAUSE to the nudge (regime III)."""
    out = {"n_messages": nud.height, "n_targeted": int(nud["target"].is_not_null().sum()),
           "multi_mention_share": float((nud["n_mentions"] > 1).mean()) if nud.height else None,
           "h04_vs_leading_extra_targets": int((nud["n_mentions"].fill_null(0) - 1).clip(0).sum()) if nud.height else 0,
           "grid_nudge_epochs": int(grid["M"].sum())}
    if gates is not None and gates.height and nud.height:
        lag = []
        gp = {k: v.sort("t_pause")["t_pause"].to_numpy() for k, v in gates.group_by(["agent", "pt_date"])}
        for a, d, ts in nud.drop_nulls("target").select("target", "pt_date", "ts").iter_rows():
            arr = gp.get((int(a), d))
            if arr is None or len(arr) == 0:
                lag.append(np.nan); continue
            j = np.searchsorted(arr, ts, "right") - 1
            lag.append(ts - arr[j] if j >= 0 else np.nan)
        lag = np.array(lag)
        f = lag[np.isfinite(lag)]
        out["sec_since_last_pause"] = {"n": int(len(f)), "q10": float(np.percentile(f, 10)) if len(f) else None,
                                       "median": float(np.median(f)) if len(f) else None,
                                       "q90": float(np.percentile(f, 90)) if len(f) else None,
                                       "share_within_60s": float((f <= 60).mean()) if len(f) else None,
                                       "share_within_300s": float((f <= 300).mean()) if len(f) else None}
        out["share_nudges_in_gate_table"] = float(gates["M"].sum() / max(1, nud["target"].is_not_null().sum()))
    return out


def minute_random_benchmark(grid: pl.DataFrame, work: dict, rng) -> dict:
    """Random-minute benchmark bounds: nudges uniform over present agent-minutes.

    Groups = pause status (in a declared pause or overdue vs not) x D bin. Value(random) = sum over groups of share x
    response; for groups the nudger visits (>= 10 first nudges), the matched first-nudge residual mean; for groups it
    never visits (mostly active agents), bounds [0, max(0, agent-mention response there)]."""
    first = work["first_pastonly"]
    idx, res = first["_idx"], first["_resid"]
    grp = (grid["Gb"].to_numpy() > 0).astype(int) * 6 + grid["Db"].to_numpy()
    NG = 12
    share = np.bincount(grp, minlength=NG) / len(grp)
    resp = np.full(NG, np.nan)
    nvis = np.bincount(grp[idx], minlength=NG)
    for b in range(NG):
        if nvis[b] >= 10:
            resp[b] = float(res[grp[idx] == b].mean())
    am = grid["amen_now"].to_numpy() > 0
    M = grid["M"].to_numpy() > 0
    past = grid["past_dir"].to_numpy()
    tr = am & ~M & (past == 0)
    ct = ~M & ~am & (past == 0) & (grid["dir_now"].to_numpy() == 0)
    r = L.matched_att(grid, tr, ct, "y30")
    proxy = np.full(NG, np.nan)
    for b in range(NG):
        sel = grp[r["idx"]] == b
        if sel.sum() >= 20:
            proxy[b] = float(r["resid"][sel].mean())
    lo = hi = 0.0
    for b in range(NG):
        if np.isfinite(resp[b]):
            lo += share[b] * resp[b]; hi += share[b] * resp[b]
        else:
            hi += share[b] * max(0.0, proxy[b] if np.isfinite(proxy[b]) else 0.0)
    labels = [("pause:" if b >= 6 else "nopause:") + L.D_LABELS[b % 6] for b in range(NG)]
    return {"groups": labels, "share_minutes": share.round(4).tolist(), "nudge_resp": resp.round(3).tolist(),
            "first_nudges": nvis.tolist(), "mention_resp": proxy.round(3).tolist(),
            "share_minutes_visited": float(share[np.isfinite(resp)].sum()),
            "V_random_minute_bounds": [float(lo), float(hi)]}


K_LAB5 = ["0", "1", "2-3", "4-9", ">=10"]


def minute_k_efficiency(grid: pl.DataFrame, work: dict, rng, B: int = 1000) -> dict:
    """Efficiency in the minute-level trap-age space X = K bin (0, 1, 2-3, 4-9, >=10), work in extra active minutes.

    p(K) = share of present agent-minutes; pi_log(K) = nudge epochs / epochs; g(K) = first-nudge matched ATT (A30) per
    K bin, empirical-Bayes shrunk. Every bin is visited by the logged nudger (no extrapolation). Day-block bootstrap with
    multinomial day weights on the per-day aggregates (control means held fixed)."""
    first = work["first_pastonly"]
    idx, res = first["_idx"], first["_resid"]
    days_all = grid["pt_date"].to_numpy()
    ud, di = np.unique(days_all, return_inverse=True)
    nd = len(ud)
    Kb = grid["Kb"].to_numpy().astype(int)
    M = grid["M"].to_numpy().astype(float)
    ep = np.zeros((nd, 5)); nu = np.zeros((nd, 5)); rs = np.zeros((nd, 5)); rc = np.zeros((nd, 5))
    np.add.at(ep, (di, Kb), 1.0); np.add.at(nu, (di, Kb), M)
    np.add.at(rs, (di[idx], Kb[idx]), res); np.add.at(rc, (di[idx], Kb[idx]), 1.0)

    def one(w):
        e_, n_, s_, c_ = w @ ep, w @ nu, w @ rs, w @ rc
        with np.errstate(invalid="ignore", divide="ignore"):
            mean = s_ / c_
        return e_, n_, mean, c_

    e0, n0, m0, c0 = one(np.ones(nd))
    # per-bin SE from a quick day bootstrap of the raw means
    W = rng.multinomial(nd, np.full(nd, 1 / nd), size=B).astype(float)
    raw = np.array([one(w)[2] for w in W])
    se = np.nanstd(raw, axis=0)
    if np.sum(c0 >= 3) < 3:
        return {"error": f"too few first nudges per trap-age bin: {c0.astype(int).tolist()}"}
    g0, tau2 = L.shrink(m0, se, c0)
    ok = e0 > 0
    p0 = e0[ok] / e0[ok].sum()
    pi0 = n0[ok] / e0[ok]
    eff = L.efficiencies(p0, pi0, g0[ok])
    if "error" in eff:
        return eff
    out = {"labels": K_LAB5, "p": p0.round(5).tolist(), "pi_log": pi0.round(6).tolist(), "g_raw": m0.round(3).tolist(),
           "g_se": se.round(3).tolist(), "g_shrunk": g0.round(3).tolist(), "n_first": c0.astype(int).tolist(), "tau2": tau2,
           "share_of_nudges": (n0 / n0.sum()).round(4).tolist()}
    out.update({k: v for k, v in eff.items() if not k.startswith("_")})
    cur = eff["_curve"]
    out["frontier_bits_per_nudge"] = (cur["I_nats"] / L.LN2 / eff["r"]).round(4).tolist()
    out["frontier_value_per_nudge"] = (cur["V"] / eff["r"]).round(5).tolist()
    # single-bin policies at the logged budget (value per nudge = g of that bin)
    out["bin_policy_value_per_nudge"] = dict(zip(K_LAB5, g0.round(3).tolist()))
    best = int(np.nanargmax(g0))
    out["best_bin"] = K_LAB5[best]
    out["ratio_best_bin_vs_logged"] = float(g0[best] / eff["V_log_per_nudge"]) if eff["V_log_per_nudge"] else float("nan")
    keys = ("V_rand_per_nudge", "V_log_per_nudge", "dV_per_nudge", "eta_SU", "eta_KW", "kappa_min_per_bit_per_nudge",
            "Vstar_at_I_per_nudge", "bits_per_nudge", "ratio_best_bin_vs_logged", "g_K1to9_minus_K10")
    bs = {k: [] for k in keys}
    for w in W:
        e_, n_, m_, c_ = one(w)
        if np.any(c_ < 3):
            continue
        g_, _ = L.shrink(m_, se, c_)
        ef = L.efficiencies(e_ / e_.sum(), n_ / e_, g_)
        if "error" in ef:
            continue
        for k in keys[:-2]:
            bs[k].append(ef[k])
        bs["ratio_best_bin_vs_logged"].append(np.nanmax(g_[1:4]) / ef["V_log_per_nudge"] if ef["V_log_per_nudge"] else np.nan)
        bs["g_K1to9_minus_K10"].append(np.nanmean(g_[1:4]) - g_[4])
    out["g_K1to9_minus_K10"] = float(np.nanmean(g0[1:4]) - g0[4])
    out["boot"] = {k: ([float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] if len(v) > 20 else [None, None])
                   for k, v in bs.items()}
    out["boot_n"] = len(bs["eta_SU"])
    return out


def coarse_efficiency(mr: dict, grid: pl.DataFrame) -> dict:
    """Efficiency in the coarse minute space (pause status x D bin, 12 groups); unvisited groups at g = 0 (lower) or at
    max(0, agent-mention response) (upper)."""
    p = np.array(mr["share_minutes"], float)
    grp = (grid["Gb"].to_numpy() > 0).astype(int) * 6 + grid["Db"].to_numpy()
    M = grid["M"].to_numpy()
    ep = np.bincount(grp, minlength=12).astype(float)
    nu = np.bincount(grp, weights=M, minlength=12)
    pi = np.where(ep > 0, nu / np.maximum(ep, 1), 0)
    resp = np.array([np.nan if x is None else x for x in mr["nudge_resp"]], float)
    prox = np.array([np.nan if x is None else x for x in mr["mention_resp"]], float)
    out = {}
    for lab, fill in (("unvisited_zero", np.zeros(12)), ("unvisited_mention", np.maximum(0, np.nan_to_num(prox)))):
        g = np.where(np.isfinite(resp), resp, fill)
        ok = p > 0
        e = L.efficiencies(p[ok], pi[ok], g[ok])
        out[lab] = {k: v for k, v in e.items() if not k.startswith("_")}
    return out


def run(period: str, B: int = 300) -> dict:
    t0 = time.time()
    rng = np.random.default_rng(L.SEED)
    d = L.OUT / period
    grid = pl.read_parquet(d / "grid.parquet")
    nud = pl.read_parquet(d / "nudges.parquet")
    gates = pl.read_parquet(d / "gates.parquet") if (d / "gates.parquet").exists() else None
    res = {"period": period, "n_days": grid["pt_date"].n_unique(), "n_agents": grid["agent"].n_unique(),
           "n_epochs": grid.height}
    res["timing"] = nudge_timing(grid, gates, nud)
    if grid["M"].sum() == 0:
        res["note"] = "no nudges in the grid"
        L.jdump(res, d / "results.json")
        return res
    res["info"] = L.info_block(grid, rng, n_null=50)
    res["propensity"] = {"D": L.propensity_profile(grid, "Db", L.D_LABELS), "G": L.propensity_profile(grid, "Gb", L.G_LABELS),
                         "K": L.propensity_profile(grid, "Kb", L.K_LABELS), "N": L.propensity_profile(grid, "Nb", L.N_LABELS)}
    work = L.work_minute(grid, rng, B=1000)
    res["work"] = work
    # value of information at minute level (bounds) and per-bit
    try:
        res["minute_random"] = minute_random_benchmark(grid, work, rng)
        att = work["first_pastonly"]["y30"][0]
        b = res["info"]["I_X"]["bits_per_nudge"]
        lo, hi = res["minute_random"]["V_random_minute_bounds"]
        res["minute_value_of_info"] = {"dV_per_nudge_range": [att - hi, att - lo], "bits_per_nudge": b,
                                       "kappa_range_min_per_bit": [(att - hi) / b, (att - lo) / b] if b > 0 else None}
    except Exception as ex:
        res["minute_random"] = {"error": repr(ex)}
    try:
        res["minute_k_eff"] = minute_k_efficiency(grid, work, rng)
    except Exception as ex:
        res["minute_k_eff"] = {"error": repr(ex)}
    if "V_random_minute_bounds" in res.get("minute_random", {}):
        try:
            res["coarse_eff"] = coarse_efficiency(res["minute_random"], grid)
        except Exception as ex:
            res["coarse_eff"] = {"error": repr(ex)}
    # CATE by K bin (minute level, first nudges, shrunk)
    first = work["first_pastonly"]
    kb = grid["Kb"].to_numpy()[first["_idx"]]
    days = grid["pt_date"].to_numpy()[first["_idx"]]
    cm, cs, cn = [], [], []
    for b in range(5):
        sel = kb == b
        if sel.sum() >= 5:
            pt, lo, hi = L.day_boot_mean(first["_resid"][sel], days[sel], rng, 500)
            cm.append(pt); cs.append((hi - lo) / 3.92 if np.isfinite(hi) else np.nan); cn.append(int(sel.sum()))
        else:
            cm.append(np.nan); cs.append(np.nan); cn.append(int(sel.sum()))
    shr, tau2 = L.shrink(np.array(cm), np.array(cs), np.array(cn))
    res["cate_minute_by_K"] = {"labels": L.K_LABELS, "mean": cm, "se": cs, "n": cn, "shrunk": shr.tolist(), "tau2": tau2}
    if gates is not None and gates.height and gates["M"].sum() >= 5:
        res["gate"] = gate_block(gates, rng, B)
    res["seconds"] = round(time.time() - t0, 1)
    res["provenance"] = {"built_by": "hypotheses/H35-nudger-maxwell-demon/analysis/run_period.py", "git_commit": L.git_commit(),
                         "inputs": [f"data/processed/H35-nudger-maxwell-demon/{period}/{{grid,gates,nudges}}.parquet"],
                         "params": {"B": B, "n_null": 50, "seed": L.SEED}, "built_at": L.dt.datetime.now(L.dt.timezone.utc).isoformat()}
    L.jdump(res, d / "results.json")
    return res


if __name__ == "__main__":
    args = sys.argv[1:]
    B = 300
    if "--B" in args:
        B = int(args[args.index("--B") + 1])
        args = [a for i, a in enumerate(args) if a != "--B" and (i == 0 or args[i - 1] != "--B")]
    for p in args:
        r = run(p, B)
        print(p, "done", r.get("seconds"), "s", flush=True)
