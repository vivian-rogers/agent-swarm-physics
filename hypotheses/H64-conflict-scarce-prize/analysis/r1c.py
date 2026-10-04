"""H64 round 1c: the prize clauses re-tested with the validated stance v2.1 conflict flag (card "Round 1c",
pre-registered 2026-10-04 22:12 UTC).

  uv run python hypotheses/H64-conflict-scarce-prize/analysis/r1c.py build        # join v2 onto H64's reply tables
  uv run python hypotheses/H64-conflict-scarce-prize/analysis/r1c.py synth        # synthetic validation first
  uv run python hypotheses/H64-conflict-scarce-prize/analysis/r1c.py natives      # N1a-e, N2a, N3a (v2 outcomes)
  uv run python hypotheses/H64-conflict-scarce-prize/analysis/r1c.py replication  # P1-P4 (v2 rates, NG excess pairs)

Outcome D = disagree_validated_agent (positive contrast = more disagreement); secondary s2 = p_agree - p_disagree.
Round-1 estimators are reused unchanged (analysis/h64lib.py, analysis/run.py with DATA pointed at the r1c folder);
the label-noise null is analysis/stance_noise.py. Writes data/processed/H64-conflict-scarce-prize/r1c/.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import mannwhitneyu  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h64lib as L  # noqa: E402
import run as RUN  # noqa: E402
import stance_noise as SN  # noqa: E402

ROOT = L.ROOT
SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H64-conflict-scarce-prize"
OUT = DATA / "r1c"
SEED = 20261064
V2C = ["B_message_id", "A_message_id", "disagree_validated_agent", "s2_soft", "stance2", "stance2_conf"] + \
      [f"p_{k}" for k in SN.CLASSES]


def jd(o):
    def d(x):
        if isinstance(x, dict):
            return {str(k): d(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [d(v) for v in x]
        if isinstance(x, np.ndarray):
            return d(x.tolist())
        if isinstance(x, (np.floating, float)):
            return None if not np.isfinite(x) else float(x)
        if isinstance(x, np.integer):
            return int(x)
        if isinstance(x, np.bool_):
            return bool(x)
        return x
    return json.dumps(d(o), indent=1, default=str)


def add_v2(df: pl.DataFrame, v2: pl.DataFrame) -> pl.DataFrame:
    out = df.join(v2, on=["B_message_id", "A_message_id"], how="left")
    assert out["disagree_validated_agent"].null_count() == 0, "pairs without a v2 label"
    g = SN.fp_profile(out)
    return out.with_columns(D=pl.col("disagree_validated_agent").cast(pl.Float64), s2=pl.col("s2_soft").cast(pl.Float64),
                            g=pl.Series(g))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    v2 = SN.load_v2(V2C)
    for f in ("replies", "g12_rel", "g26_rel", "g23_rel"):
        d = add_v2(pl.read_parquet(DATA / f"{f}.parquet"), v2.select(V2C))
        d.write_parquet(OUT / f"{f}.parquet", compression="zstd")
        print(f, d.height)
    pl.read_parquet(DATA / "g23_games.parquet").write_parquet(OUT / "g23_games.parquet")
    # global false-positive normalization (shared ruler over all H64 replies): f_e = fbar * g_e / mean_all(g)
    r = pl.read_parquet(OUT / "replies.parquet")
    meta = {"Dbar_all": float(r["D"].mean()), "gmean_all": float(r["g"].mean()), "n": r.height,
            "built_by": "hypotheses/H64-conflict-scarce-prize/analysis/r1c.py build", "inputs": ["H64 replies/g12/g26/g23", "shared/reply_stance_v2"]}
    (OUT / "_provenance.json").write_text(jd({**meta, "git_commit": __import__("common").git_commit(),
                                              "built_at": __import__("datetime").datetime.utcnow().isoformat() + "Z"}))


# ============================================================================================ #12 helpers
def g12_frame():
    d = pl.read_parquet(OUT / "g12_rel.parquet")
    spk, tgt, N, codes = L.reindex(d["b_agent"].to_numpy(), d["a_agent"].to_numpy())
    return d, spk, tgt, N


def teams12():
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        pl.col("preferred") & ~pl.col("holdout") & (pl.col("goal_no") == 12) & (pl.col("label_kind") == "team"))
    return {u: dict(x.select("agent", "value").iter_rows()) for (u,), x in gt.group_by(["unit"])}


def perm_R(d, teams, rng):
    deb, ba, aa = d["debate"].to_numpy(), d["b_agent"].to_numpy(), d["a_agent"].to_numpy()
    R = np.zeros(len(d))
    for u, T in teams.items():
        ags = list(T)
        Tp = dict(zip(ags, rng.permutation([T[a] for a in ags])))
        m = deb == u
        R[m] = [Tp[b] != Tp[a] for b, a in zip(ba[m], aa[m])]
    return R


# ============================================================================================ synthetic
def synth_g12_job(args):
    orv, reps, P, seed = args
    rng = np.random.default_rng(seed)
    d, spk, tgt, N = g12_frame()
    win = d["wblock"].to_numpy()
    R = d["R"].to_numpy().astype(float)
    O = d["O"].to_numpy().astype(float)
    teams = teams12()
    _, winc = np.unique(win, return_inverse=True)
    ng = SN.NoiseNull([spk, tgt, winc], d["D"].to_numpy(), d["g"].to_numpy(), d["debate"].to_numpy())
    perms = [perm_R(d, teams, rng) for _ in range(P)]
    hits = []
    for _ in range(reps):
        y = ng.draw(rng, beta=np.log(orv), x=R * O)
        e = L.did_fit(y, spk, tgt, win, R, O)
        nul = np.array([[(q := L.did_fit(y, spk, tgt, win, Rp, O))["g_open"], q["delta"], q["g_set"]] for Rp in perms])
        p_open = L.perm_p(e["g_open"], nul[:, 0], "greater")
        p_delta = L.perm_p(e["delta"], nul[:, 1], "greater")
        hits.append({"g_open": e["g_open"], "delta": e["delta"], "g_set": e["g_set"], "p_open": p_open, "p_delta": p_delta,
                     "N1a": bool(e["g_open"] > 0 and p_open < 0.01),
                     "N1b_core": bool(e["delta"] > 0 and p_delta < 0.05 and abs(e["g_set"]) < 0.5 * abs(e["g_open"]))})
    return orv, hits


def synth_excess_job(args):
    g, unit, reps, R, seed = args
    rng = np.random.default_rng(seed)
    rp = pl.read_parquet(OUT / "replies.parquet").filter(pl.col("goal_no") == g)
    if unit:
        rp = rp.filter(pl.col("unit_id") == unit)
    spk, tgt, N, _ = L.reindex(rp["b_agent"].to_numpy(), rp["a_agent"].to_numpy())
    blk = rp["block"].to_numpy()
    ng = SN.NoiseNull([spk, tgt], rp["D"].to_numpy(), rp["g"].to_numpy(), blk)
    fires = []
    for _ in range(reps):
        y = ng.draw(rng)
        obs = L.pair_tests(spk, tgt, -y, blk, N, robust=True)[0]
        ng2 = SN.NoiseNull([spk, tgt], y, rp["g"].to_numpy(), blk)
        nul = np.array([L.pair_tests(spk, tgt, -ng2.draw(rng), blk, N, robust=True)[0] for _ in range(R)])
        fires.append(bool(obs > np.quantile(nul, 0.95)))
    return f"{g}{unit or ''}", float(np.mean(fires))


def synth():
    t0 = time.time()
    ORS = [1.0, 2.0, 3.0, 5.0]
    with Pool(2) as p:
        res = p.map(synth_g12_job, [(o, 200, 500, SEED + int(10 * o)) for o in ORS], chunksize=1)
        ex = p.map(synth_excess_job, [(13, None, 30, 100, 1), (26, None, 30, 100, 2), (38, None, 30, 100, 3),
                                      (41, None, 30, 100, 4)], chunksize=1)
    out = {"G12_DiD_D": {}, "excess_pairs_size": dict(ex)}
    for o, hits in res:
        out["G12_DiD_D"][str(o)] = {"power_N1a": float(np.mean([h["N1a"] for h in hits])),
                                    "power_N1b_core": float(np.mean([h["N1b_core"] for h in hits])),
                                    "mean_g_open": float(np.mean([h["g_open"] for h in hits])),
                                    "mean_delta": float(np.mean([h["delta"] for h in hits])),
                                    "p_open_lt_0.05": float(np.mean([h["p_open"] < 0.05 for h in hits]))}
    out["note"] = ("G12: planted true log-OR on opponent replies while open, on the real #12 reply structure with "
                   "speaker/target/window fields and differential false positives; team permutation (500) per replicate; "
                   "the cluster-bootstrap CI conditions are omitted in the synthetic. Excess pairs: NG world with no pair "
                   "effect, cluster-robust count vs a re-fitted NG null (100 draws), 30 replicates.")
    out["seconds"] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "synth.json").write_text(jd(out))
    print(jd(out))


# ============================================================================================ natives
def verdict_reads():
    """Per (debate, debater) the first ledger call whose context holds the debate's verdict message."""
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        pl.col("preferred") & ~pl.col("holdout") & (pl.col("goal_no") == 12))
    res = gt.filter(pl.col("label_kind") == "debate_result").select("unit", "source_ref", "t_valid_from")
    res = res.with_columns(pl.col("source_ref").str.extract(r"message_id=([0-9a-f\-]+)").alias("mid"))
    items = pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("message_id").is_in(res["mid"].to_list())) \
        .select("turn_id", "message_id").collect()
    turns = pl.read_parquet(SH / "context_ledger_turns.parquet", columns=["turn_id", "agent", "t_call", "holdout"]).join(
        items, on="turn_id")
    assert turns["holdout"].sum() == 0
    first = turns.group_by("message_id", "agent").agg(pl.col("t_call").min().alias("t_read"))
    return res.join(first, left_on="mid", right_on="message_id", how="left").select("unit", "agent", "t_read", "t_valid_from")


def native_g12_read(outcome="negD", P=5000):
    d = pl.read_parquet(OUT / "g12_rel.parquet")
    vr = verdict_reads().rename({"unit": "debate", "agent": "b_agent"})
    d = d.join(vr.with_columns(pl.col("b_agent").cast(pl.Int8)), on=["debate", "b_agent"], how="left")
    post = d.filter(pl.col("phase") == "post")
    unread = post.filter(pl.col("t_read").is_null() | (pl.col("t") < pl.col("t_read")))
    out = {"post_replies": post.height, "post_unread": unread.height, "post_unread_opponent": int(unread["R"].sum()),
           "read_lag_s_median": float(vr.with_columns((pl.col("t_read") - pl.col("t_valid_from")).dt.total_seconds().alias("lag"))["lag"].median() or np.nan),
           "n_debater_reads": int(vr["t_read"].is_not_null().sum()), "n_debater_rows": vr.height}
    out["testable"] = bool(out["post_unread_opponent"] >= 15)
    if out["testable"]:
        d2 = d.with_columns(O=((pl.col("phase") != "post") | pl.col("t_read").is_null() | (pl.col("t") < pl.col("t_read"))).cast(pl.Int8))
        d2.write_parquet(OUT / "g12_rel_read.parquet")
        out["did_read"] = {k: v for k, v in native_on(d2, outcome).items() if k in ("est", "ci", "p_open", "p_delta")}
    return out


def native_on(d, outcome):
    tmp = OUT / "_tmp_g12.parquet"
    d.write_parquet(tmp)
    old = RUN.DATA
    try:
        RUN.DATA = OUT
        (OUT / "g12_rel.parquet").rename(OUT / "_g12_keep.parquet")
        tmp.rename(OUT / "g12_rel.parquet")
        return RUN.native_g12(outcome)
    finally:
        (OUT / "g12_rel.parquet").unlink(missing_ok=True)
        (OUT / "_g12_keep.parquet").rename(OUT / "g12_rel.parquet")
        RUN.DATA = old


def ng_g12(res_D, R=2000):
    """NG p for g_open and delta: D simulated under fields (speaker, target, window) with no relation term."""
    d, spk, tgt, N = g12_frame()
    win = d["wblock"].to_numpy()
    _, winc = np.unique(win, return_inverse=True)
    Rr, O = d["R"].to_numpy().astype(float), d["O"].to_numpy().astype(float)
    ng = SN.NoiseNull([spk, tgt, winc], d["D"].to_numpy(), d["g"].to_numpy(), d["debate"].to_numpy())
    rng = np.random.default_rng(SEED + 5)
    nul = np.array([[(q := L.did_fit(ng.draw(rng), spk, tgt, win, Rr, O))["g_open"], q["delta"]] for _ in range(R)])
    fexp, fbar = ng.f_expected()
    ef = L.did_fit(fexp, spk, tgt, win, Rr, O)
    e = res_D["est"]
    return {"p_NG_open": SN.p_greater(e["g_open"], nul[:, 0]), "p_NG_delta": SN.p_greater(e["delta"], nul[:, 1]),
            "T_f_open": ef["g_open"], "T_f_delta": ef["delta"], "fbar": fbar,
            "g_open_corrected": (e["g_open"] - ef["g_open"]) / (SN.R_POINT - fbar),
            "delta_corrected": (e["delta"] - ef["delta"]) / (SN.R_POINT - fbar)}


def natives():
    t0 = time.time()
    RUN.DATA = OUT
    out = {}
    # D enters run.py's estimators as y = -D so that run.py's sign rules (negative = antagonism) apply unchanged
    for f in ("g12_rel", "g26_rel", "g23_rel"):
        d = pl.read_parquet(OUT / f"{f}.parquet")
        if "negD" not in d.columns:
            d.with_columns(negD=-pl.col("D")).write_parquet(OUT / f"{f}.parquet")
    for name, fn in (("G12", RUN.native_g12), ("G26", RUN.native_g26), ("G23", RUN.native_g23)):
        out[name] = {"negD": fn("negD"), "s2": fn("s2")}
        print(name, {k: v for k, v in out[name]["negD"].items() if k not in ("cells", "ci", "se")}, out[name]["negD"]["ci"], flush=True)
    out["G12"]["NG"] = ng_g12({"est": {k: -v for k, v in out["G12"]["negD"]["est"].items()}})
    out["G12"]["read_timing"] = native_g12_read()
    out["seconds"] = round(time.time() - t0, 1)
    (OUT / "natives.json").write_text(jd(out))
    print(jd({"G12_NG": out["G12"]["NG"], "read": out["G12"]["read_timing"]}))


# ============================================================================================ replication
def repl_job(args):
    g, u, fbar_all, gmean_all, k_hi, k_lo = args
    t0 = time.time()
    rp = pl.read_parquet(OUT / "replies.parquet").filter(pl.col("goal_no") == g)
    if u is not None:
        rp = rp.filter(pl.col("unit_id") == u)
    spk, tgt, N, _ = L.reindex(rp["b_agent"].to_numpy(), rp["a_agent"].to_numpy())
    D = rp["D"].to_numpy()
    blk = rp["block"].to_numpy()
    rng = np.random.default_rng(g * 7 + (0 if u is None else len(u)))
    obs_r = L.pair_tests(spk, tgt, -D, blk, N, robust=True)
    obs_n = L.pair_tests(spk, tgt, -D, blk, N, robust=False)
    ng = SN.NoiseNull([spk, tgt], D, rp["g"].to_numpy(), blk)
    nr, nn = [], []
    for _ in range(200):
        y = ng.draw(rng)
        nr.append(L.pair_tests(spk, tgt, -y, blk, N, robust=True)[0])
        nn.append(L.pair_tests(spk, tgt, -y, blk, N, robust=False)[0])
    nr, nn = np.array(nr), np.array(nn)
    bt = RUN.day_boot(rp, ["D", "s2"])
    fe = fbar_all * rp["g"].to_numpy() / gmean_all
    fbar_p = float(fe.mean())
    return {"goal": g, "unit": u or str(g), "prize_class": RUN.prize_class(g), "n": rp.height, "N": int(N),
            "regime": rp["regime"][0], "d": bt["D"], "s2bar": bt["s2"], "fbar_p": fbar_p,
            "d_corr": (bt["D"][0] - fbar_p) / (SN.R_POINT - fbar_p),
            "d_corr_hiFP": (bt["D"][0] - fbar_p * k_hi) / (SN.R_RANGE[0] - fbar_p * k_hi),
            "d_corr_loFP": (bt["D"][0] - fbar_p * k_lo) / (SN.R_RANGE[1] - fbar_p * k_lo),
            "n_neg_robust": obs_r[0], "n_tested_robust": obs_r[1], "null_mean_robust": float(nr.mean()),
            "p_ng_robust": float((1 + (nr >= obs_r[0]).sum()) / 201), "n_neg_naive": obs_n[0],
            "null_mean_naive": float(nn.mean()), "p_ng_naive": float((1 + (nn >= obs_n[0]).sum()) / 201),
            "runtime_s": time.time() - t0}


def replication():
    t0 = time.time()
    RUN.DATA = OUT
    units = RUN.eligible()
    meta = json.loads((OUT / "_provenance.json").read_text())
    fbar_all = SN.implied_fpr(meta["Dbar_all"], SN.PI_POINT, SN.R_POINT)
    # corners of the precision/recall box: most false positives (pi 0.54, r 0.50) and fewest (pi 0.80, r 0.75)
    k_hi = SN.implied_fpr(meta["Dbar_all"], SN.PI_RANGE[0], SN.R_RANGE[0]) / fbar_all
    k_lo = SN.implied_fpr(meta["Dbar_all"], SN.PI_RANGE[1], SN.R_RANGE[1]) / fbar_all
    with Pool(2) as p:
        res = p.map(repl_job, [(g, u, fbar_all, meta["gmean_all"], k_hi, k_lo) for g, u in sorted(units, key=lambda x: -(x[0] == 51))], chunksize=1)
    rp51 = pl.read_parquet(OUT / "replies.parquet").filter(pl.col("goal_no") == 51)
    b51 = RUN.day_boot(rp51, ["D"])
    fe51 = float((fbar_all * rp51["g"].to_numpy() / meta["gmean_all"]).mean())
    per = [r for r in res if r["goal"] != 51]
    pf = [r for r in per if r["prize_class"] == "prize_free"]
    comp = [r for r in per if r["prize_class"] == "competition"]
    summ = {"fbar_all": fbar_all}
    for key, get in (("raw", lambda r: r["d"][0]), ("corrected", lambda r: r["d_corr"]), ("corrected_hiFP", lambda r: r["d_corr_hiFP"]), ("corrected_loFP", lambda r: r["d_corr_loFP"])):
        med = float(np.median([get(r) for r in pf]))
        mw = mannwhitneyu([get(r) for r in comp], [get(r) for r in pf], alternative="greater")
        above = int(sum(get(r) > med for r in comp))
        summ[f"P1_{key}"] = {"prize_free_median": med, "competition_above_median": above, "n_comp": len(comp),
                             "mw_p": float(mw.pvalue), "pass": bool(above >= 3 and mw.pvalue < 0.10),
                             "competition": {r["goal"]: get(r) for r in comp}}
    pf_units = [r for r in res if r["prize_class"] == "prize_free"]
    summ["P2"] = {"prize_free_units": len(pf_units), "excess_robust": int(sum(r["p_ng_robust"] <= 0.05 for r in pf_units)),
                  "share_no_excess": float(np.mean([r["p_ng_robust"] > 0.05 for r in pf_units])),
                  "pass": bool(np.mean([r["p_ng_robust"] > 0.05 for r in pf_units]) >= 0.8),
                  "units_51_excess": int(sum(r["p_ng_robust"] <= 0.05 for r in res if r["goal"] == 51)),
                  "units_51": int(sum(r["goal"] == 51 for r in res))}
    allp = [(r["goal"], r["d"][0]) for r in per] + [(51, b51["D"][0])]
    top = max(allp, key=lambda x: x[1])
    summ["P3"] = {"top_goal": top[0], "top_d": top[1], "d12": next(r["d"][0] for r in per if r["goal"] == 12),
                  "rank12": 1 + sum(v > next(r["d"][0] for r in per if r["goal"] == 12) for _, v in allp), "pass": top[0] == 12}
    q75 = float(np.quantile([r["d"][0] for r in pf], 0.75))
    summ["P4"] = {"d51": b51["D"], "d51_corr": (b51["D"][0] - fe51) / (SN.R_POINT - fe51), "prize_free_q75": q75,
                  "pass": bool(b51["D"][0] < q75)}
    summ["P5_naive_gt_robust"] = int(sum(r["n_neg_naive"] > r["n_neg_robust"] for r in res))
    (OUT / "replication_units.json").write_text(jd(res))
    (OUT / "replication_summary.json").write_text(jd(summ))
    print(jd(summ), round(time.time() - t0, 1))


if __name__ == "__main__":
    {"build": build, "synth": synth, "natives": natives, "replication": replication}[sys.argv[1]]()
