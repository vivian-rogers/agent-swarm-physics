"""H44 synthetic validation (axis F), run before the real event study.

Agents with a context store wiped at the real reset positions of a real regime-III period (real agent-days, real call
counts, real forced / voluntary / session resets, real forced events and pseudo-erasures). Call categories follow a
first-order Markov chain whose baseline transition matrix is calibrated on the period's mid-segment calls (pos 11-30;
no reset-aligned statistic is used), with per-agent category tilts. Three planted worlds:
  (i)  thrash:    after a consolidation reset, P_k(.|c) = (1 - g_k) T_a(c, .) + g_k Q_a, g_k = 0.8 exp(-(k-1)/5),
                  Q_a ∝ pi_a * exp(+1.2 [re-acquisition] - 1.5 [write])  (field quench: persistence lost, reads up,
                  writes down)
  (ii) pure dip:  P_k(write|c) = T_a(c, write)(1 - d_k), d_1 = 0.9, d_2..10 = 0.4, the removed mass spread
                  proportionally over the other categories of the row (non-write composition kept)
  (iii) none.
The real estimators (h44lib.panel / window_stats / classify) are applied; the pipeline must call (i) thrash, (ii) dip,
(iii) none. Susceptibility: planted reply rates on the real reply pools (none vs pre-read x0.7 / post-read x1.4 after a
reset) recovered by h44lib.reply_rates.
Outputs: data/processed/H44-erasure-reacquisition-thrash/synthetic/synthetic.json, figures/synthetic_validation.pdf
Usage: uv run python hypotheses/H44-erasure-reacquisition-thrash/analysis/synthetic.py [--reps 12,30,40]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h44lib as L  # noqa: E402
from h44lib import C  # noqa: E402

OUTS = C.OUT / "synthetic"
NC = len(C.CATS)
WRITE = C.CAT["write"]
RQ = np.zeros(NC); RQ[C.REACQ_IDX] = 1


def calibrate(calls: pl.DataFrame):
    mid = calls.filter((pl.col("pos") >= 11) & (pl.col("pos") <= 30)).sort("agent", "pt_date", "seq")
    prev = mid["cat"].shift(1).to_numpy()
    same = ((mid["agent"] == mid["agent"].shift(1)) & (mid["pt_date"] == mid["pt_date"].shift(1))
            & (mid["seq"] == mid["seq"].shift(1) + 1)).fill_null(False).to_numpy()
    cur = mid["cat"].to_numpy()
    T = np.ones((NC, NC)) * 0.5
    np.add.at(T, (prev[same].astype(int), cur[same].astype(int)), 1)
    T = T / T.sum(1, keepdims=True)
    pi = np.bincount(cur, minlength=NC) + 1.0
    pi = pi / pi.sum()
    tilt = {}
    for a, g in mid.group_by("agent"):
        f = np.bincount(g["cat"].to_numpy(), minlength=NC) + 1.0
        tilt[a[0]] = np.sqrt((f / f.sum()) / pi)
    return T, pi, tilt


def simulate(calls: pl.DataFrame, T, pi, tilt, world: str, rng) -> np.ndarray:
    """Vectorized over agent-days: step s draws every sequence's s-th call."""
    df = calls.select("agent", "pt_date", "seq", "pos", "seg_kind").with_row_index("i")
    groups = df.group_by("agent", "pt_date", maintain_order=True).agg(pl.col("i"), pl.col("pos"), pl.col("seg_kind"))
    L_ = groups["i"].list.len().to_numpy()
    G = len(L_)
    maxL = L_.max()
    I = np.full((G, maxL), -1, np.int64); POS = np.zeros((G, maxL), np.int32); CONS = np.zeros((G, maxL), bool)
    for g, (ii, pp, sk) in enumerate(zip(groups["i"].to_list(), groups["pos"].to_list(), groups["seg_kind"].to_list())):
        I[g, :len(ii)] = ii
        POS[g, :len(ii)] = pp
        CONS[g, :len(ii)] = np.isin(np.array(sk), ["forced", "voluntary"])
    ag = groups["agent"].to_numpy()
    TA = np.stack([T * tilt.get(a, np.ones(NC))[None, :] for a in ag])        # G x NC x NC
    TA = TA / TA.sum(2, keepdims=True)
    piA = np.stack([pi * tilt.get(a, np.ones(NC)) for a in ag]); piA /= piA.sum(1, keepdims=True)
    Q = piA * np.exp(1.2 * RQ - 1.5 * (np.arange(NC) == WRITE))[None, :]
    Q /= Q.sum(1, keepdims=True)
    out = np.zeros(len(df), np.int8)
    cur = np.array([rng.choice(NC, p=p) for p in piA])
    for s in range(maxL):
        live = I[:, s] >= 0
        if s > 0:
            P = TA[np.arange(G), cur]                                         # G x NC
            k = POS[:, s]
            post = CONS[:, s] & (k >= 1)
            if world == "thrash":
                g = np.where(post, 0.8 * np.exp(-(k - 1) / 5.0), 0.0)[:, None]
                P = (1 - g) * P + g * Q
            elif world == "dip":
                d = np.where(post & (k == 1), 0.9, np.where(post & (k >= 2) & (k <= 10), 0.4, 0.0))
                pw = P[:, WRITE] * (1 - d)
                rest = 1 - P[:, WRITE]
                scale = np.where(rest > 0, (1 - pw) / np.clip(rest, 1e-12, None), 1.0)
                P = P * scale[:, None]
                P[:, WRITE] = pw
            u = rng.random(G)[:, None]
            nxt = (P.cumsum(1) < u).sum(1).clip(0, NC - 1)
            cur = np.where(live, nxt, cur)
        out[I[live, s]] = cur[live]
    return out


def synth_calls(calls, cats, rng):
    w = cats == WRITE
    return calls.with_columns(pl.Series("cat", cats, dtype=pl.Int8), pl.Series("any_write", w),
                              pl.Series("n_work", (w & (rng.random(len(cats)) < 0.31)).astype(np.int16)),
                              pl.Series("talk", cats == C.CAT["talk"]), pl.lit(0, pl.Int16).alias("n_fail"),
                              pl.lit(False).alias("in_loop"))


def run_world(period: str, reps: int, B: int, seed: int) -> dict:
    calls = pl.read_parquet(C.OUT / "calls.parquet").filter(pl.col("period") == period)
    ev = pl.read_parquet(C.OUT / "events.parquet").filter(pl.col("period") == period)
    T, pi, tilt = calibrate(calls)
    res = {"period": period, "n_calls": calls.height, "n_forced": int((ev["ev_kind"] == "forced").sum()), "worlds": {}}
    rng = np.random.default_rng(seed)
    for world in ("thrash", "dip", "none"):
        rows = []
        for r in range(reps):
            t0 = time.time()
            sc = synth_calls(calls, simulate(calls, T, pi, tilt, world, rng), rng)
            row = {}
            for kind in ("forced", "pseudo31"):
                p = L.panel(sc, ev.filter(pl.col("ev_kind") == kind), -20, 20 if kind == "forced" else 10)
                st = L.window_stats(p, B=B, seed=seed + r, windows=("post5", "post10", "far", "near"))
                c5, c10 = st["contrasts"]["post5_vs_far"], st["contrasts"]["post10_vs_far"]
                row[kind] = {"class": L.classify(st), "Theta": c5["Theta"], "dR": c5["dR"], "Omega": c10["Omega"],
                             "d_sigma": c5["d_sigma"], "d_H": c5["d_H"], "Theta_c": c5["Theta_c"]}
            rows.append(row)
            C.log(period, world, r, row["forced"]["class"], round(row["forced"]["Theta"][0], 4),
                  round(row["forced"]["Theta_c"][0], 4),
                  round(row["forced"]["Omega"][0], 3), f"{time.time() - t0:.1f}s")
        cls = [x["forced"]["class"] for x in rows]
        pcls = [x["pseudo31"]["class"] for x in rows]
        want = {"thrash": "thrash", "dip": "dip", "none": "none"}[world]
        res["worlds"][world] = {
            "accuracy": float(np.mean([c == want for c in cls])), "classes": {c: cls.count(c) for c in set(cls)},
            "pseudo_false_pos": float(np.mean([c != "none" for c in pcls])),
            "Theta_mean": float(np.mean([x["forced"]["Theta"][0] for x in rows])),
            "Thetac_mean": float(np.mean([x["forced"]["Theta_c"][0] for x in rows])),
            "Theta_raw_pos_rate": float(np.mean([x["forced"]["Theta"][1] > 0 for x in rows])),
            "Thetac_pos_rate": float(np.mean([x["forced"]["Theta_c"][1] > 0 for x in rows])),
            "Omega_mean": float(np.mean([x["forced"]["Omega"][0] for x in rows])),
            "dsigma_mean": float(np.mean([x["forced"]["d_sigma"][0] for x in rows])),
            "dH_mean": float(np.mean([x["forced"]["d_H"][0] for x in rows])),
            "Theta_ci_width": float(np.mean([x["forced"]["Theta"][2] - x["forced"]["Theta"][1] for x in rows])),
            "reps": rows}
    return res


def synth_replies(period: str, reps: int, seed: int) -> dict:
    rp = pl.read_parquet(C.OUT / "reply_pools.parquet").filter(pl.col("period") == period)
    rng = np.random.default_rng(seed)
    r_age = np.array([1.0, 0.5, 0.25, 0.1, 0.05])
    out = {}
    real_rate = float(rp["has_parent"].mean())
    for world in ("none", "susceptible"):
        vals = []
        for r in range(reps):
            ne = np.stack(rp["n_e"].to_numpy()).reshape(-1, 3, 5).astype(float)
            npp = np.stack(rp["n_p"].to_numpy()).reshape(-1, 3, 5).astype(float)
            post_e = (rp["seg_kind"].is_in(["forced", "voluntary"]) & (rp["pos"] <= 20)).to_numpy()
            mult = np.ones((len(rp), 3, 5))
            if world == "susceptible":
                mult[post_e, 0, :] = 1.4          # post-read messages after a reset
                mult[post_e, 2, :] = 0.7          # messages read before the reset (erased)
            lam = (ne * r_age[None, None, :] * mult)
            tot = lam.sum((1, 2))
            scale = -np.log(1 - real_rate) / max(np.median(tot[tot > 0]), 1e-9)
            has = rng.random(len(rp)) < 1 - np.exp(-scale * tot)
            pc = np.full(len(rp), -1); pa = np.full(len(rp), -1)
            flat = lam.reshape(len(rp), -1)
            for i in np.nonzero(has & (tot > 0))[0]:
                j = rng.choice(flat.shape[1], p=flat[i] / flat[i].sum())
                pc[i], pa[i] = j // 5, j % 5
            # pseudo classes: map the chosen message's (erasure class, age) cell onto the pseudo split by drawing from
            # the n_p cells consistent with it (post / pre_ctx share the erasure "post" class)
            pcp = pc.copy()
            for i in np.nonzero(pc == 0)[0]:
                a_ = pa[i]
                w0, w1 = npp[i, 0, a_], npp[i, 1, a_]
                pcp[i] = 0 if rng.random() < w0 / max(w0 + w1, 1e-9) else 1
            sim = rp.with_columns(pl.Series("has_parent", has), pl.Series("par_cls_e", pc, dtype=pl.Int8),
                                  pl.Series("par_cls_p", pcp, dtype=pl.Int8), pl.Series("par_age", pa, dtype=pl.Int8))
            st = L.reply_rates(sim, "forced", B=200, seed=seed + r)
            vals.append({"log_did": st["log_did"], "rr_post": st["rr_post"], "rr_has_parent": st["rr_has_parent"]})
        out[world] = {"log_did_mean": float(np.mean([v["log_did"][0] for v in vals])),
                      "log_did_cover0": float(np.mean([v["log_did"][1] <= 0 <= v["log_did"][2] for v in vals])),
                      "rr_post_mean": float(np.mean([v["rr_post"][0] for v in vals])),
                      "rr_post_excl1": float(np.mean([v["rr_post"][1] > 1 for v in vals])),
                      "did_excl0_neg": float(np.mean([v["log_did"][2] < 0 for v in vals])), "reps": vals}
        C.log("replies", period, world, out[world]["log_did_mean"], out[world]["rr_post_mean"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", default="10,24,40")
    ap.add_argument("--B", type=int, default=300)
    a = ap.parse_args()
    reps = [int(x) for x in a.reps.split(",")]
    OUTS.mkdir(parents=True, exist_ok=True)
    res = {"design": __doc__.split("Outputs:")[0].strip(), "periods": {}}
    for per, n in zip(("G51", "G38", "G37"), reps):
        res["periods"][per] = run_world(per, n, a.B, seed={"G51": 101, "G38": 202, "G37": 303}[per])
        (OUTS / "synthetic.json").write_text(json.dumps(res, indent=1, default=float))
    res["replies"] = {per: synth_replies(per, n, seed=11) for per, n in (("G51", 20), ("G38", 30))}
    (OUTS / "synthetic.json").write_text(json.dumps(res, indent=1, default=float))
    C.log("done")


if __name__ == "__main__":
    main()
