"""H12 per-unit pipeline (one goal period, or a sub-unit split at a step change), non-holdout only.

Arm (a), random-matrix: activity and talk spins (1-min) and content overlap (30-min windows, whitened d = 32,
kind-centered), each against the cross-day edge (primary), the within-day circular-shift edge (secondary), naive and
T_eff Marchenko-Pastur, and (activity) the lull-filtered cross-day edge. Top-mode shape, label separations
(room, lab), H02-style block-demeaned variant.
Arm (b), dimensionality: PR30 per 30-min window (chat, cap 8, n 30, 20 draws), PRday per day (6 agents x 15 chat,
50 draws), between-agent PR, spread TV, effective rank; chat+intent variants.

Outputs: data/processed/H12-groupthink-dimensional-collapse/G<NN>/{rmt_<unit>.json, pr30_<unit>.parquet,
prday_<unit>.parquet}.

Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/run_units.py [unit ...] [--workers 2]
"""
from __future__ import annotations

import json
import math
import sys
import time
from multiprocessing import Pool

import h12lib as L
import numpy as np
import polars as pl

N_SURR = 200
D = 32
MIN_TALK = 10


def guard(pt_dates, goal_nos):
    assert not any(L.holdout_mask(list(pt_dates), list(goal_nos))), "holdout day in an exploratory unit"


def unit_row(unit: str) -> dict:
    u = pl.read_parquet(L.OUT / "units.parquet").filter(pl.col("unit") == unit)
    assert u.height == 1, unit
    return u.row(0, named=True)


def labels(unit: str, agents: list[int]):
    au = pl.read_parquet(L.OUT / "agents_units.parquet").filter(pl.col("unit") == unit)
    m = {r["agent"]: r for r in au.iter_rows(named=True)}
    room = np.array([m.get(a, {}).get("room_modal", -1) if m.get(a, {}).get("room_modal") is not None else -1 for a in agents])
    lab = np.array([m.get(a, {}).get("lab") or "?" for a in agents])
    return room, lab


def eig_shape(V, w, k_show=3):
    return [{"l": float(w[j]), **L.mode_summary(V[:, j])} for j in range(min(k_show, V.shape[1]))]


def separations(V, room, lab, rng, k_show=3):
    out = []
    for j in range(min(k_show, V.shape[1])):
        rr = room >= 0
        two_rooms = len(np.unique(room[rr])) >= 2 and min(np.bincount(np.unique(room[rr], return_inverse=True)[1])) >= 3
        labs, cnt = np.unique(lab, return_counts=True)
        big = labs[cnt >= 3]
        lm = np.isin(lab, big)
        out.append({"p_room": L.label_separation(V[rr, j], room[rr], rng) if two_rooms else None,
                    "p_lab": L.label_separation(V[lm, j], lab[lm], rng) if len(big) >= 2 else None})
    return out


# ---------------------------------------------------------------------------------------------- arm (a)
def spin_days(unit, which):
    sp = pl.read_parquet(L.OUT / "spins.parquet").filter(pl.col("unit") == unit)
    guard(sp["pt_date"].unique().to_list(), [int(unit.rstrip("abcdefgh"))] * sp["pt_date"].n_unique())
    agents = sorted(sp["agent"].unique().to_list())
    days = []
    for d in sorted(sp["day"].unique().to_list()):
        x = sp.filter(pl.col("day") == d)
        Ld = int(x["minute"].max()) + 1
        S = np.ones((len(agents), Ld), dtype=np.int8)
        ai = np.searchsorted(agents, x["agent"].to_numpy())
        S[ai, x["minute"].to_numpy()] = x["state"].to_numpy()
        days.append(np.where(S >= 3, 1, -1).astype(np.int8) if which == "act" else np.where(S == 4, 1, -1).astype(np.int8))
    X = np.concatenate(days, 1)
    keep = X.std(1) > 0
    if which == "talk":
        keep &= (X > 0).sum(1) >= MIN_TALK
    agents = [a for a, k in zip(agents, keep) if k]
    return [d[keep] for d in days], agents


def block_demeaned_eig(days):
    out = []
    for A in days:
        A = A.astype(float); B = A.copy()
        for s in range(0, A.shape[1], 30):
            blk = A[:, s:s + 30]
            B[:, s:s + 30] = blk - blk.mean(1, keepdims=True)
        out.append(B)
    X = np.concatenate(out, 1)
    w, V, C = L.corr_eig(X, vectors=True)
    u = np.ones(len(w)) / np.sqrt(len(w))
    return float(w[0]), float(u @ C @ u), L.mode_summary(V[:, 0])


def rmt_spins(unit, which, rng):
    days, agents = spin_days(unit, which)
    N = len(agents)
    if N < 4:
        return {"N": N}
    X = np.concatenate(days, 1); T = X.shape[1]
    w, V, C = L.corr_eig(X, vectors=True)
    u = np.ones(N) / np.sqrt(N)
    cd = L.spectrum_test(days, N_SURR, rng, "spin", "crossday")
    ci = L.spectrum_test(days, N_SURR, rng, "spin", "circ")
    tau = L.bartlett_tau(days)
    room, lab = labels(unit, agents)
    out = {"N": N, "T": T, "D": len(days), "agents": agents, "eig": w.tolist(),
           "edge_cd": cd["edge"], "k_cd": cd["k"], "k_rank": cd["k_rank"], "null_l1_med": cd["null_l1_med"],
           "null_q95": cd["null_eigs_q95"].tolist(),
           "edge_circ": ci["edge"], "k_circ": ci["k"], "edge_mp": L.mp_edge(N, T), "k_mp": int((w > L.mp_edge(N, T)).sum()),
           "tauB": tau, "edge_mpeff": L.mp_edge(N, T / tau), "k_mpeff": int((w > L.mp_edge(N, T / tau)).sum()),
           "VR": float(u @ C @ u), "rho_bar": float((C.sum() - N) / (N * (N - 1))),
           "modes": eig_shape(V, w), "sep": separations(V, room, lab, rng),
           "active_frac": float((X > 0).mean())}
    if which == "act":
        lu = L.spectrum_test(days, N_SURR, rng, "spin", "crossday", lull=True)
        Xl = L.lull_filter(X)
        wl, Vl, Cl = L.corr_eig(Xl, vectors=True)
        out.update({"k_lull": lu["k"], "edge_lull": lu["edge"], "eig_lull": wl.tolist(), "T_lull": int(Xl.shape[1]),
                    "lull_frac": float(1 - Xl.shape[1] / T), "modes_lull": eig_shape(Vl, wl, 1)})
        l1b, vrb, mb = block_demeaned_eig(days)
        out.update({"l1_block": l1b, "VR_block": vrb, "mode_block": mb})
    return out


def content_days(unit, rows, Wv, cal, kind=None, d=D):
    x = rows if kind is None else rows.filter(pl.col("kind") == kind)
    x = x.filter(pl.col("win30").is_not_null())
    dates = sorted(cal["pt_date"].to_list())
    Wd = {r["pt_date"]: max(1, math.ceil(r["window_s"] / 1800)) for r in cal.iter_rows(named=True)}
    # content agents: >= 1 statement on >= 80% of days and in >= 20% of windows
    tot = sum(Wd[t] for t in dates)
    g = x.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"),
                                pl.struct("pt_date", "win30").n_unique().alias("nw"))
    agents = sorted(g.filter((pl.col("nd") >= 0.8 * len(dates)) & (pl.col("nw") >= 0.2 * tot))["agent"].to_list())
    x = x.filter(pl.col("agent").is_in(agents))
    V = Wv[x["row"].to_numpy(), :d].astype(np.float64)
    # kind-centering per agent (unit mean per statement kind)
    key = x["agent"].cast(pl.String) + "|" + x["kind"]
    _, inv = np.unique(key.to_numpy(), return_inverse=True)
    mu = np.zeros((inv.max() + 1, d)); np.add.at(mu, inv, V); mu /= np.bincount(inv)[:, None]
    V = V - mu[inv]
    ai = np.searchsorted(agents, x["agent"].to_numpy())
    days = []
    for t in dates:
        m = (x["pt_date"] == t).to_numpy()
        S = np.zeros((len(agents), Wd[t], d)); n = np.zeros((len(agents), Wd[t]))
        wi = np.minimum(x["win30"].to_numpy()[m], Wd[t] - 1)
        np.add.at(S, (ai[m], wi), V[m]); np.add.at(n, (ai[m], wi), 1)
        days.append(S / np.maximum(n, 1)[:, :, None])
    return days, agents


def rmt_content(unit, rows, Wv, cal, rng, kind=None, d=D):
    days, agents = content_days(unit, rows, Wv, cal, kind, d)
    N = len(agents)
    if N < 4:
        return {"N": N}
    X = np.concatenate(days, 1)
    w, V, Q = L.overlap_eig(X, vectors=True)
    cd = L.spectrum_test(days, N_SURR, rng, "content", "crossday")
    room, lab = labels(unit, agents)
    u = np.ones(N) / np.sqrt(N)
    return {"N": N, "T": int(X.shape[1]), "d": d, "agents": agents, "eig": w.tolist(), "edge_cd": cd["edge"], "k_cd": cd["k"],
            "k_rank": cd["k_rank"], "null_l1_med": cd["null_l1_med"], "edge_mp": L.mp_edge(N, X.shape[1] * d),
            "k_mp": int((w > L.mp_edge(N, X.shape[1] * d)).sum()), "VR": float(u @ Q @ u),
            "modes": eig_shape(V, w), "sep": separations(V, room, lab, rng),
            "fill": float((np.abs(X).sum(2) > 0).mean())}


# ---------------------------------------------------------------------------------------------- arm (b)
def pr_unit(unit, rows, Wv, rng):
    x = rows.filter(pl.col("win30").is_not_null())
    out30, outday = [], []
    dates = sorted(x["pt_date"].unique().to_list())
    for di, t in enumerate(dates):
        xd = x.filter(pl.col("pt_date") == t)
        for w in sorted(xd["win30"].unique().to_list()):
            xw = xd.filter(pl.col("win30") == w)
            ch = xw.filter(pl.col("kind") == "chat")
            r = L.pr_rarefied(Wv[ch["row"].to_numpy(), :D].astype(np.float64), ch["agent"].to_numpy(), 30, 8, 20, rng)
            ra = L.pr_rarefied(Wv[xw["row"].to_numpy(), :D].astype(np.float64), xw["agent"].to_numpy(), 30, 8, 20, rng, erank=False)
            out30.append({"unit": unit, "pt_date": t, "day": di, "win30": int(w), "n_chat": ch.height, "n_agents_chat": ch["agent"].n_unique(),
                          "pr": r["pr"], "pr_naive": r["pr_naive"], "tv": r["tv"], "erank": r["erank"], "pr_all": ra["pr"], "tv_all": ra["tv"]})
        ch = xd.filter(pl.col("kind") == "chat")
        Y = Wv[ch["row"].to_numpy(), :D].astype(np.float64); ag = ch["agent"].to_numpy()
        rd = L.pr_balanced(Y, ag, 6, 15, 50, rng)
        rda = L.pr_balanced(Wv[xd["row"].to_numpy(), :D].astype(np.float64), xd["agent"].to_numpy(), 6, 15, 50, rng, erank=False)
        bt = L.between_pr(Y, ag, rng, splits=20)
        outday.append({"unit": unit, "pt_date": t, "day": di, "n_chat": ch.height, "n_agents_chat": ch["agent"].n_unique(),
                       "prday": rd["pr"], "tvday": rd["tv"], "erankday": rd["erank"], "n_elig": rd["n_elig"], "prday_all": rda["pr"],
                       "pr_between": bt["pr_between"], "pr_between_naive": bt["pr_between_naive"], "pr_between_pop": bt["pr_between_pop"],
                       "N_between": bt["N"]})
    return pl.DataFrame(out30, infer_schema_length=None), pl.DataFrame(outday, infer_schema_length=None)


def run(unit: str) -> str:
    t0 = time.time()
    ur = unit_row(unit)
    g = ur["goal_no"]
    od = L.OUT / f"G{g:02d}"; od.mkdir(parents=True, exist_ok=True)
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date").is_in(ur["days"]))
    guard(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    idx = pl.read_parquet(L.OUT / "stmt_index.parquet").filter(pl.col("unit") == unit)
    guard(idx["pt_date"].unique().to_list(), [g] * idx["pt_date"].n_unique())
    Wv = np.load(L.OUT / "stmt_white_d64.npy", mmap_mode="r")
    rng = np.random.default_rng([L.SEED, L.stable_seed(unit)])
    res = {"unit": unit, "goal_no": g, "regime": ur["regime"], "mode": ur["mode"], "n_days": ur["n_days"], "scored": ur["scored"]}
    do_rmt = (ur["N_present"] or 0) >= 6 and ur["n_days"] >= 2
    if do_rmt:
        res["act"] = rmt_spins(unit, "act", rng)
        res["talk"] = rmt_spins(unit, "talk", rng)
        res["content"] = rmt_content(unit, idx, Wv, cal, rng)
        res["content_d8"] = rmt_content(unit, idx, Wv, cal, rng, d=8)
        res["content_chat"] = rmt_content(unit, idx, Wv, cal, rng, kind="chat")
    (od / f"rmt_{unit}.json").write_text(json.dumps(res))
    p30, pday = pr_unit(unit, idx, Wv, rng)
    p30.write_parquet(od / f"pr30_{unit}.parquet"); pday.write_parquet(od / f"prday_{unit}.parquet")
    return f"{unit}: rmt={do_rmt} windows={p30.height} days={pday.height} {time.time() - t0:.0f}s"


def main():
    argv = sys.argv[1:]
    workers = 2
    if "--workers" in argv:
        i = argv.index("--workers"); workers = min(2, int(argv[i + 1])); argv = argv[:i] + argv[i + 2:]
    args = argv
    units = args or pl.read_parquet(L.OUT / "units.parquet").sort("goal_no", "unit")["unit"].to_list()
    with Pool(workers) as pool:
        for msg in pool.imap_unordered(run, units):
            print(msg, flush=True)
    L.write_provenance("hypotheses/H12-groupthink-dimensional-collapse/analysis/run_units.py",
                       ["H12 spins.parquet, stmt_index.parquet, stmt_white_d64.npy, agents_units.parquet; shared calendar"],
                       {"n_surr": N_SURR, "d": D, "pr30": "chat, cap 8, n 30, 20 draws", "prday": "6 agents x 15 chat, 50 draws",
                        "content_agents": ">=1 statement on >=80% of days and >=20% of windows", "min_talk_minutes": MIN_TALK,
                        "seed": L.SEED})


if __name__ == "__main__":
    main()
