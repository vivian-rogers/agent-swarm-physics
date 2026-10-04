"""H64 round 1 on real data: replication layer (antagonism excess E_p, position-opposition rate r_p per eligible
period) and the natives G12, G26, G23 (prize-gated DiD with relation permutation). Rules: card + Amendment A1.

    uv run python hypotheses/H64-conflict-scarce-prize/analysis/run.py [replication|natives|all]
Writes data/processed/H64-conflict-scarce-prize/{replication,natives}/*.json.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "1")

import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import mannwhitneyu  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h64lib as L  # noqa: E402

DATA = L.ROOT / "data/processed/H64-conflict-scarce-prize"
COMPETITION = (6, 23, 26, 27)
ASSIGNED = (12,)
NOPRIZE_RIVALRY = (51,)
MIN_REPLIES = 300
MIN_SPEAKERS = 4


def prize_class(g: int) -> str:
    if g in ASSIGNED:
        return "assigned"
    if g in COMPETITION:
        return "competition"
    if g in NOPRIZE_RIVALRY:
        return "rivalry_no_prize"
    return "prize_free"


def eligible() -> list:
    rp = pl.read_parquet(DATA / "replies.parquet")
    c = rp.group_by("goal_no").agg(pl.len().alias("n"), pl.col("b_agent").n_unique().alias("N"))
    gs = sorted(c.filter((pl.col("n") >= MIN_REPLIES) & (pl.col("N") >= MIN_SPEAKERS))["goal_no"].to_list())
    units = []
    for g in gs:
        if g == 51:
            cu = rp.filter(pl.col("goal_no") == 51).group_by("unit_id").agg(
                pl.len().alias("n"), pl.col("b_agent").n_unique().alias("N"))
            for u in sorted(cu.filter((pl.col("n") >= MIN_REPLIES) & (pl.col("N") >= MIN_SPEAKERS))["unit_id"]):
                units.append((g, u))
        else:
            units.append((g, None))
    return units


def day_boot(df: pl.DataFrame, cols: list, B: int = 1000, rng=None) -> dict:
    rng = rng or np.random.default_rng(3)
    days = df["pt_date"].to_numpy()
    ud, inv = np.unique(days, return_inverse=True)
    X = {c: df[c].cast(pl.Float64).to_numpy() for c in cols}
    sums = {c: np.bincount(inv, X[c], len(ud)) for c in cols}
    cnt = np.bincount(inv, None, len(ud))
    out = {}
    for c in cols:
        est = float(X[c].mean())
        bs = []
        for _ in range(B):
            k = rng.integers(0, len(ud), len(ud))
            bs.append(sums[c][k].sum() / cnt[k].sum())
        out[c] = (est, float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975)))
    return out


def repl_job(args):
    g, u = args
    t0 = time.time()
    rp = pl.read_parquet(DATA / "replies.parquet").filter(pl.col("goal_no") == g)
    if u is not None:
        rp = rp.filter(pl.col("unit_id") == u)
    spk, tgt, N, _ = L.reindex(rp["b_agent"].to_numpy(), rp["a_agent"].to_numpy())
    ex = L.excess(spk, tgt, rp["y"].to_numpy(), rp["block"].to_numpy(), N, R=200, rng=np.random.default_rng(g))
    bt = day_boot(rp, ["pos_opp", "conf_opp", "y", "s"])
    sub_cov = float(rp.filter(pl.col("conf_opp"))["has_sub"].mean()) if rp["conf_opp"].sum() else float("nan")
    return {"goal": g, "unit": u or str(g), "prize_class": prize_class(g), "n": rp.height, "N": int(N),
            "n_days": int(rp["pt_date"].n_unique()), "regime": rp["regime"][0],
            "r_pos": bt["pos_opp"], "r_opp": bt["conf_opp"], "ybar": bt["y"], "sbar": bt["s"],
            "subtype_coverage": sub_cov, **ex, "runtime_s": time.time() - t0}


def replication(workers=2):
    units = eligible()
    with Pool(workers) as p:
        res = p.map(repl_job, sorted(units, key=lambda x: -(x[0] == 51)), chunksize=1)
    # period-level r_p for #51 (all head replies) for P4
    rp51 = pl.read_parquet(DATA / "replies.parquet").filter(pl.col("goal_no") == 51)
    b51 = day_boot(rp51, ["pos_opp", "conf_opp"])
    per = [r for r in res if r["goal"] != 51]
    pf = [r for r in per if r["prize_class"] == "prize_free"]
    comp = [r for r in per if r["prize_class"] == "competition"]
    med = float(np.median([r["r_pos"][0] for r in pf]))
    q75 = float(np.quantile([r["r_pos"][0] for r in pf], 0.75))
    mw = mannwhitneyu([r["r_pos"][0] for r in comp], [r["r_pos"][0] for r in pf], alternative="greater")
    mw2 = mannwhitneyu([r["r_opp"][0] for r in comp], [r["r_opp"][0] for r in pf], alternative="greater")
    allp = per + [{"goal": 51, "r_pos": b51["pos_opp"]}]
    top = max(allp, key=lambda r: r["r_pos"][0])["goal"]
    pf_units = [r for r in res if r["prize_class"] == "prize_free"]
    summ = {
        "P1": {"competition_above_median": int(sum(r["r_pos"][0] > med for r in comp)), "n_comp": len(comp),
               "prize_free_median": med, "mw_p": float(mw.pvalue),
               "pass": bool(sum(r["r_pos"][0] > med for r in comp) >= 3 and mw.pvalue < 0.10),
               "r_opp_mw_p": float(mw2.pvalue),
               "r_opp_comp_above_median": int(sum(r["r_opp"][0] > np.median([x["r_opp"][0] for x in pf])
                                                  for r in comp))},
        "P2": {"prize_free_units": len(pf_units),
               "excess_robust": int(sum(r["p_af_robust"] <= 0.05 for r in pf_units)),
               "share_no_excess": float(np.mean([r["p_af_robust"] > 0.05 for r in pf_units])),
               "pass": bool(np.mean([r["p_af_robust"] > 0.05 for r in pf_units]) >= 0.8)},
        "P3": {"top_r_pos_goal": top, "pass": top == 12},
        "P4": {"r51": b51["pos_opp"], "prize_free_q75": q75, "pass": bool(b51["pos_opp"][0] < q75)},
        "P5": {"naive_gt_robust": int(sum(r["n_neg_naive"] > r["n_neg_robust"] for r in res)), "n_units": len(res)},
    }
    out = DATA / "replication"
    out.mkdir(parents=True, exist_ok=True)
    (out / "units.json").write_text(json.dumps(res, indent=1, default=float))
    (out / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float))


# ------------------------------------------------------------------------------------------------ natives
def did_block(d: pl.DataFrame, outcome: str, win: np.ndarray, clus: np.ndarray, heat_unit=None, B=1000, seed=0):
    spk, tgt, N, codes = L.reindex(d["b_agent"].to_numpy(), d["a_agent"].to_numpy())
    y = d[outcome].cast(pl.Float64).to_numpy()
    return L.did(y, spk, tgt, win, d["R"].to_numpy(), d["O"].to_numpy(), clus, B=B,
                 rng=np.random.default_rng(seed), heat_unit=heat_unit), (spk, tgt, y)


def perm_stats(spk, tgt, y, win, R_perm, O_perm):
    e = L.did_fit(y, spk, tgt, win, R_perm, O_perm)
    return e["g_open"], e["delta"], e["g_set"]


def native_g12(outcome="s", P=5000):
    d = pl.read_parquet(DATA / "g12_rel.parquet")
    win = d["wblock"].to_numpy()
    res, (spk, tgt, y) = did_block(d, outcome, win, d["debate"].to_numpy(), heat_unit=d["debate"].to_numpy())
    # team permutation within debate
    gt = pl.read_parquet(L.ROOT / "data/processed/shared/ground_truth_labels.parquet").filter(
        pl.col("preferred") & ~pl.col("holdout") & (pl.col("goal_no") == 12) & (pl.col("label_kind") == "team"))
    teams = {u: dict(x.select("agent", "value").iter_rows()) for (u,), x in gt.group_by(["unit"])}
    rng = np.random.default_rng(12)
    deb = d["debate"].to_numpy()
    ba = d["b_agent"].to_numpy()
    aa = d["a_agent"].to_numpy()
    O = d["O"].to_numpy()
    nul = []
    for _ in range(P):
        R = np.zeros(len(d))
        for u, T in teams.items():
            ags = list(T)
            vals = rng.permutation([T[a] for a in ags])
            Tp = dict(zip(ags, vals))
            m = deb == u
            R[m] = [Tp[b] != Tp[a] for b, a in zip(ba[m], aa[m])]
        nul.append(perm_stats(spk, tgt, y, win, R, O))
    nul = np.array(nul)
    e = res["est"]
    out = {"outcome": outcome, **res, "p_open": L.perm_p(e["g_open"], nul[:, 0]), "p_delta": L.perm_p(e["delta"], nul[:, 1]),
           "p_set_two": float(min(1, 2 * min(L.perm_p(e["g_set"], nul[:, 2]), L.perm_p(e["g_set"], nul[:, 2], "greater"))))}
    out["N1a_pass"] = bool(e["g_open"] < 0 and out["p_open"] < 0.01 and res["ci"]["g_open"][1] < 0)
    out["N1b_pass"] = bool(e["delta"] < 0 and out["p_delta"] < 0.05 and res["ci"]["g_set"][0] <= 0 <= res["ci"]["g_set"][1]
                           and abs(e["g_set"]) < 0.5 * abs(e["g_open"]))
    out["N1c_heat_ci_includes_0"] = bool(res["ci"]["phi"][0] <= 0 <= res["ci"]["phi"][1])
    # cell means (descriptive)
    out["cells"] = d.group_by("phase", "R").agg(pl.col(outcome).mean().alias("mean"), pl.len().alias("n")).sort(
        "phase", "R").to_dicts()
    # N1d resentment: post-verdict opposite-team replies, losers -> winners minus winners -> losers
    p = d.filter((pl.col("phase") == "post") & (pl.col("R") == 1))
    if p.height >= 10:
        lw = p.filter(~pl.col("b_won"))[outcome].mean() - p.filter(pl.col("b_won"))[outcome].mean()
        debs = p["debate"].unique().to_list()
        bs = []
        for _ in range(2000):
            pick = rng.choice(debs, len(debs))
            q = pl.concat([p.filter(pl.col("debate") == k) for k in pick])
            if q["b_won"].all() or (~q["b_won"]).all():
                continue
            bs.append(q.filter(~pl.col("b_won"))[outcome].mean() - q.filter(pl.col("b_won"))[outcome].mean())
        out["N1d"] = {"losers_minus_winners": float(lw), "ci": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
                      "n": p.height, "n_loser": int((~p["b_won"]).sum())}
        out["N1d_pass"] = bool(out["N1d"]["ci"][0] <= 0 <= out["N1d"]["ci"][1])
    return out


def native_g26(outcome="s"):
    d = pl.read_parquet(DATA / "g26_rel.parquet")
    dm = d.filter(pl.col("window") != "confirmatory")
    win = dm["window"].to_numpy()
    res, (spk, tgt, y) = did_block(dm, outcome, win, dm["block"].to_numpy())
    ba, aa, O = dm["b_agent"].to_numpy(), dm["a_agent"].to_numpy(), dm["O"].to_numpy()
    agents = sorted(set(ba) | set(aa))
    nul = []
    for tri in itertools.combinations(agents, 3):
        R = (np.isin(ba, tri) & np.isin(aa, tri)).astype(float)
        if (R * O).sum() == 0 or (R * (1 - O)).sum() == 0:
            continue
        nul.append(perm_stats(spk, tgt, y, win, R, O))
    nul = np.array(nul)
    e = res["est"]
    out = {"outcome": outcome, **res, "p_open": L.perm_p(e["g_open"], nul[:, 0]),
           "p_delta": L.perm_p(e["delta"], nul[:, 1]), "n_perm": len(nul)}
    out["N2a_pass"] = bool(e["g_open"] < 0 and out["p_open"] < 0.05)
    # confirmatory window: rival contrast there (descriptive)
    dc = d.filter(pl.col("window") != "open").with_columns(O=(pl.col("window") == "confirmatory").cast(pl.Int8))
    rc, _ = did_block(dc, outcome, dc["window"].to_numpy(), dc["block"].to_numpy(), B=500)
    out["confirmatory_vs_settled"] = {"g_conf": rc["est"]["g_open"], "g_set": rc["est"]["g_set"],
                                      "ci_conf": rc["ci"]["g_open"], "n_rival_conf": rc["n_rival_open"]}
    out["cells"] = d.group_by("window", "R").agg(pl.col(outcome).mean().alias("mean"), pl.len().alias("n")).sort(
        "window", "R").to_dicts()
    return out


def native_g23(outcome="s", P=5000):
    d = pl.read_parquet(DATA / "g23_rel.parquet")
    games = pl.read_parquet(DATA / "g23_games.parquet")
    win = d["pt_date"].to_numpy()
    res, (spk, tgt, y) = did_block(d, outcome, win, d["block"].to_numpy())
    ba, aa = d["b_agent"].to_numpy(), d["a_agent"].to_numpy()
    tt = d["t"].dt.epoch("us").to_numpy()
    gl = [(a1, a2, t0, t1) for a1, a2, t0, t1 in games.select("a1", "a2", pl.col("t0").dt.epoch("us"),
                                                              pl.col("t1").dt.epoch("us")).iter_rows()]
    agents = sorted(set(ba) | set(aa) | {x for g in gl for x in g[:2]})
    rng = np.random.default_rng(23)
    nul = []
    for _ in range(P):
        perm = dict(zip(agents, rng.permutation(agents)))
        R = np.zeros(len(d))
        O = np.zeros(len(d))
        for a1, a2, t0, t1 in gl:
            p1, p2 = perm[a1], perm[a2]
            m = ((ba == p1) & (aa == p2)) | ((ba == p2) & (aa == p1))
            R[m] = 1
            O[m & (tt >= t0) & (tt < t1)] = 1
        if (R * O).sum() == 0 or (R * (1 - O)).sum() == 0:
            continue
        nul.append(perm_stats(spk, tgt, y, win, R, O))
    nul = np.array(nul)
    e = res["est"]
    out = {"outcome": outcome, **res, "p_open": L.perm_p(e["g_open"], nul[:, 0]),
           "p_delta": L.perm_p(e["delta"], nul[:, 1]), "n_perm": len(nul),
           "n_games": games.height, "n_opp_pairs": len({(a, b) for a, b, *_ in gl})}
    out["testable"] = bool(res["n_rival_open"] >= 15)
    out["N3a_pass"] = bool(out["testable"] and e["g_open"] < 0 and out["p_open"] < 0.05)
    out["cells"] = d.group_by("R", "O").agg(pl.col(outcome).mean().alias("mean"), pl.len().alias("n")).sort(
        "R", "O").to_dicts()
    return out


def natives():
    out = DATA / "natives"
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    for name, f in (("G12", native_g12), ("G26", native_g26), ("G23", native_g23)):
        res[name] = {"soft": f("s"), "hard": f("y")}
        (out / f"{name}.json").write_text(json.dumps(res[name], indent=1, default=float))
        s = res[name]["soft"]
        print(name, {k: v for k, v in s.items() if k not in ("cells", "ci", "se")}, s["ci"])


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    if w in ("replication", "all"):
        replication()
    if w in ("natives", "all"):
        natives()
