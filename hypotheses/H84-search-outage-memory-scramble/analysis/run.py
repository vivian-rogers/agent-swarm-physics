"""H84 round 1 on real data (exploratory; holdout masked upstream in the scheme).

  N1 G37 outage: dose DiD for V1-V4, first stage, substitution, recovery; placebo pairs, kickoff-matched pairs,
     dose permutation, leave-one-agent-out.
  N2 NE18 (04-20) search rework: dose x post DiD with placebo boundaries.
  N3 G51 failed answers: Poisson rate ratio of work commits and return-to-own-artifact difference.
  Replication: I_Q (bits) at search calls per eligible period (>= 30 mapped search calls, regime III, non-holdout).
  kappa inputs for H87: dV_Q at the mean searcher dose (commits per 20 calls) and pooled I_Q.
Output: data/processed/H84-search-outage-memory-scramble/results/results.json
Usage: uv run python hypotheses/H84-search-outage-memory-scramble/analysis/run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h84lib as L  # noqa: E402
import semantic_kappa as K  # noqa: E402  (infra/shared, on sys.path via h84lib)

SIGNS = {"V1_continuity": -1, "V2_duplicates": 1, "V3_earlier_goal_refs": -1, "V4_commits_per20": -1,
         "S_search_per100": 1, "S_rereads_per100": 1}
NE18_PRE = ("2026-04-06", "2026-04-17")
NE18_POST = ("2026-04-20", "2026-04-24")
ELIG_MIN = 30


def ne18_frames(panel: pl.DataFrame):
    days = sorted(panel["pt_date"].unique().to_list())
    pre = [d for d in days if NE18_PRE[0] <= d <= NE18_PRE[1]]
    post = [d for d in days if NE18_POST[0] <= d <= NE18_POST[1]]
    dose = L.dose_table(panel, pre)
    real = {"B": post[0], "days": pre + post, "post": post}
    blocked = set(post) | set(L.OUTAGE) | set(L.RECOVERY)
    placebos = []
    for i, b in enumerate(days):
        if not ("2026-04-13" <= b <= "2026-05-18") or i < 10 or i + 5 > len(days):
            continue
        pw = days[i:i + 5]
        if blocked & set(pw):
            continue
        placebos.append({"B": b, "days": days[i - 10:i] + pw, "post": pw})
    return real, placebos, dose


def first_stage(panel, srch, dose):
    out = {}
    for a in dose.filter(pl.col("dose") >= L.SEARCHER_MIN)["agent"].to_list():
        s = srch.filter(pl.col("agent") == a)
        pre = s.filter(pl.col("pt_date").is_in(L.DOSE_DAYS))
        on = s.filter(pl.col("pt_date").is_in(L.OUTAGE))
        p = panel.filter(pl.col("agent") == a)
        rate = lambda days: float(100 * p.filter(pl.col("pt_date").is_in(days))["search_calls"].sum()  # noqa: E731
                                  / max(p.filter(pl.col("pt_date").is_in(days))["calls"].sum(), 1))
        out[int(a)] = {"n_pre": pre.height, "n_outage": on.height,
                       "ans_med_pre": float(pre["ans_chars"].median()) if pre.height else None,
                       "ans_med_outage": float(on["ans_chars"].median()) if on.height else None,
                       "rate_pre": rate(L.DOSE_DAYS), "rate_outage": rate(L.OUTAGE)}
    return out


def g37(panel, srch):
    dose = L.dose_table(panel, L.DOSE_DAYS)
    panel = panel.filter(pl.col("agent").is_in(dose["agent"].implode()))
    dbar = float(dose.filter(pl.col("dose") >= L.SEARCHER_MIN)["dose"].mean())
    excl = L.DOSE_DAYS + L.OUTAGE + L.RECOVERY
    pairs, pairs_k = L.placebo_pairs(panel, excl), L.placebo_pairs(panel, excl, kickoff_matched=True)
    res = {"dose": dict(zip([int(x) for x in dose["agent"]], [float(x) for x in dose["dose"]])),
           "dbar_searchers": dbar, "n_searchers": int((dose["dose"] >= L.SEARCHER_MIN).sum()),
           "pairs": pairs, "pairs_kickoff": pairs_k, "first_stage": first_stage(panel, srch, dose), "tests": {}}
    for k, sgn in SIGNS.items():
        f = L.frame(panel, k, dose)
        t = L.did_test(f, L.OUTAGE, [L.RECOVERY], pairs, pairs_k, sign=sgn)
        rec = L.beta(f, L.RECOVERY, [L.OUTAGE])
        t["beta_rec"] = rec
        t["rec_in_central80"] = bool(L.central80(rec, t["placebo"]))
        t["effect_at_dbar"] = t["beta"] * dbar
        t["effect_at_dbar_placebo_sd"] = t["placebo"]["sd"] * dbar
        t["mean_y_searchers_pre"] = float(f.filter(pl.col("dose") >= L.SEARCHER_MIN)
                                          .filter(~pl.col("pt_date").is_in(L.OUTAGE + L.RECOVERY))["y"].mean())
        # weighted variant for V1 (by commits)
        if k == "V1_continuity":
            d = f["dose"].to_numpy()
            days = f["pt_date"].to_numpy()
            X = np.column_stack([d * np.isin(days, L.OUTAGE), d * np.isin(days, L.RECOVERY)])
            t["beta_weighted"] = float(L.twfe(f["y"].to_numpy(), f["agent"].to_numpy(), days, X,
                                              w=f["commits"].to_numpy().astype(float))[0])
            # binary dose variant (searcher vs not)
            fb = f.with_columns((pl.col("dose") >= L.SEARCHER_MIN).cast(pl.Float64).alias("dose"))
            t["beta_binary"] = L.beta(fb, L.OUTAGE, [L.RECOVERY])
        res["tests"][k] = t
        print("G37", k, round(t["beta"], 4), "p_rank", t["placebo"]["p_rank"], "perm", t["perm_p"], flush=True)
    return res


def ne18(panel, srch):
    real, placebos, dose = ne18_frames(panel)
    pan = panel.filter(pl.col("agent").is_in(dose["agent"].implode()))
    dbar = float(dose.filter(pl.col("dose") >= L.SEARCHER_MIN)["dose"].mean())
    res = {"dose": dict(zip([int(x) for x in dose["agent"]], [float(x) for x in dose["dose"]])), "dbar_searchers": dbar,
           "n_searchers": int((dose["dose"] >= L.SEARCHER_MIN).sum()), "placebo_B": [p["B"] for p in placebos],
           "tests": {}}
    fs = {}
    for a in dose.filter(pl.col("dose") >= L.SEARCHER_MIN)["agent"].to_list():
        s = srch.filter(pl.col("agent") == a)
        pr = s.filter(pl.col("pt_date").is_in(real["days"][:-len(real["post"])]))
        po = s.filter(pl.col("pt_date").is_in(real["post"]))
        fs[int(a)] = {"n_pre": pr.height, "n_post": po.height,
                      "ans_med_pre": float(pr["ans_chars"].median()) if pr.height else None,
                      "ans_med_post": float(po["ans_chars"].median()) if po.height else None}
    res["first_stage"] = fs
    for k in ("V1_continuity", "V3_earlier_goal_refs", "V4_commits_per20", "S_search_per100", "S_rereads_per100"):
        sgn = -SIGNS[k] if k.startswith("V") else 1
        bs = []
        for spec in [real] + placebos:
            f = L.frame(pan.filter(pl.col("pt_date").is_in(spec["days"])), k, dose)
            bs.append(L.beta(f, spec["post"], []))
        b, pb = bs[0], np.array([x for x in bs[1:] if np.isfinite(x)])
        res["tests"][k] = {"beta": b, "effect_at_dbar": b * dbar, "n_placebo": len(pb),
                           "p_rank": float((1 + np.sum(sgn * pb >= sgn * b)) / (1 + len(pb))),
                           "q10": float(np.percentile(pb, 10)), "q90": float(np.percentile(pb, 90))}
        print("NE18", k, round(b, 4), res["tests"][k]["p_rank"], flush=True)
    return res


def iq_row(df: pl.DataFrame, B: int = 300, seed: int = 0) -> dict:
    x, s = df["X_next"].to_numpy(), df["S_Q"].to_numpy()
    st = df["agent"].to_numpy()
    rng = np.random.default_rng(seed)
    info = K.mi_corrected(x, s, st, n_perm=200, rng=rng)
    cl = (df["agent"].cast(pl.Utf8) + "|" + df["pt_date"]).to_numpy()
    u, ci = np.unique(cl, return_inverse=True)
    members = [np.flatnonzero(ci == j) for j in range(len(u))]
    Ib = []
    for _ in range(B):
        idx = np.concatenate([members[j] for j in rng.integers(0, len(u), len(u))])
        raw = K.mi_mm(x[idx], s[idx])
        fl = np.mean([K.mi_mm(x[idx], K.permute_within(s[idx], K._codes(st[idx]), rng)) for _ in range(10)])
        Ib.append(raw - fl)
    Ib = np.array(Ib)
    Ib = Ib - (Ib.mean() - info["I"])
    ok = (df["X_next"] >= 0) & (df["A_prev"] >= 0)
    ret = df.filter(ok)
    named = ret.filter(pl.col("S_Q") == pl.col("A_prev"))
    other = ret.filter(pl.col("S_Q") != pl.col("A_prev"))
    return {**info, "I_ci": [float(np.percentile(Ib, 2.5)), float(np.percentile(Ib, 97.5))], "I_se": float(Ib.std()),
            "n_clusters": len(u), "open_share": float((df["S_Q"] == df["A_prev"]).mean()),
            "named_share": float((df["S_Q"] >= 0).mean()),
            "p_return_named": float((named["X_next"] == named["A_prev"]).mean()) if named.height else None,
            "n_return_named": named.height,
            "p_return_other": float((other["X_next"] == other["A_prev"]).mean()) if other.height else None,
            "n_return_other": other.height}


def replication(sc: pl.DataFrame) -> dict:
    out = {}
    sc = sc.filter(pl.col("n_win") >= 10)
    for g in sorted(sc["goal_no"].unique().to_list()):
        d = sc.filter(pl.col("goal_no") == g)
        if d.height < ELIG_MIN:
            continue
        r = iq_row(d, seed=int(g))
        r["verdict"] = ("supported" if r["p_perm"] < 0.05 else ("failed" if r["n"] >= 100 else "descriptive"))
        r["units"] = sorted(d["unit_id"].drop_nulls().unique().to_list())
        r["n_agents"] = int(d["agent"].n_unique())
        r["days"] = [d["pt_date"].min(), d["pt_date"].max(), int(d["pt_date"].n_unique())]
        out[f"G{g:02d}"] = r
        print("rep", g, d.height, round(r["I"], 4), r["p_perm"], flush=True)
    est = [v["I"] for v in out.values()]
    se = [v["I_se"] for v in out.values()]
    out["_pooled_I_Q"] = K.dl_pool(est, se)
    return out


def g51(sc: pl.DataFrame, B: int = 300) -> dict:
    d = sc.filter((pl.col("goal_no") == 51) & (pl.col("n_win") >= 10)).with_columns(
        (pl.col("ans_chars") < 150).alias("failed"))
    V = d["V"].to_numpy()
    X = np.column_stack([d["failed"].to_numpy().astype(float), np.log1p(d["query_chars"].to_numpy()),
                         np.log1p(d["ctx_pos"].fill_null(0).to_numpy().astype(float))])
    grp = d["agent"].to_numpy()
    b = K.poisson_fe(V, X, grp)
    r = d.filter((pl.col("X_next") >= 0) & (pl.col("A_prev") >= 0)).with_columns(
        (pl.col("X_next") == pl.col("A_prev")).cast(pl.Float64).alias("ret"))
    Xr = np.column_stack([r["failed"].to_numpy().astype(float), np.log1p(r["query_chars"].to_numpy()),
                          np.log1p(r["ctx_pos"].fill_null(0).to_numpy().astype(float))])
    one = np.zeros(r.height)
    br = L.twfe(r["ret"].to_numpy(), r["agent"].to_numpy(), one, Xr)
    rng = np.random.default_rng(51)
    cl = (d["agent"].cast(pl.Utf8) + "|" + d["pt_date"]).to_numpy()
    u, ci = np.unique(cl, return_inverse=True)
    mem = [np.flatnonzero(ci == j) for j in range(len(u))]
    clr = (r["agent"].cast(pl.Utf8) + "|" + r["pt_date"]).to_numpy()
    pos_r = {c: np.flatnonzero(clr == c) for c in np.unique(clr)}
    RR, DR = [], []
    for _ in range(B):
        pick = rng.integers(0, len(u), len(u))
        idx = np.concatenate([mem[j] for j in pick])
        bb = K.poisson_fe(V[idx], X[idx], grp[idx])
        RR.append(np.exp(bb[0]))
        ir = np.concatenate([pos_r.get(u[j], np.array([], int)) for j in pick])
        if len(ir) > 20:
            DR.append(L.twfe(r["ret"].to_numpy()[ir], r["agent"].to_numpy()[ir], one[ir], Xr[ir])[0])
    q = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]  # noqa: E731
    return {"n": d.height, "n_failed": int(d["failed"].sum()), "n_clusters": len(u),
            "rr_failed": float(np.exp(b[0])), "rr_ci": q(RR), "n_return": r.height,
            "d_return_failed": float(br[0]), "d_return_ci": q(DR),
            "V_mean_ok": float(d.filter(~pl.col("failed"))["V"].mean()),
            "V_mean_failed": float(d.filter(pl.col("failed"))["V"].mean())}


def main():
    panel = L.load_panel()
    srch = pl.read_parquet(L.DATA / "search_events.parquet")
    sc = pl.read_parquet(L.DATA / "search_calls.parquet")
    res = {"G37": g37(panel, srch), "NE18": ne18(panel, srch), "G51": g51(sc), "replication": replication(sc)}
    t = res["G37"]["tests"]["V4_commits_per20"]
    res["kappa_inputs"] = {
        "dV_Q_commits_per20_at_dbar": -t["effect_at_dbar"], "dV_Q_se_placebo": t["effect_at_dbar_placebo_sd"],
        "I_Q_pooled": res["replication"]["_pooled_I_Q"],
        "note": "dV_Q = -(beta_V4 x mean searcher dose): commits per 20 calls lost on outage days at the mean searcher "
                "dose; SE = placebo SD of beta x dose. I_Q = DL-pooled per-period I(X+; S_Q) at search calls."}
    out = L.DATA / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(res, indent=1, default=float))
    print("written", out / "results.json")


if __name__ == "__main__":
    main()
