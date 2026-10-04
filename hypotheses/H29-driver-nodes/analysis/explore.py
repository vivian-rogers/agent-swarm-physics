"""H29 exploratory round 1 on real data (non-holdout units only; the scheme already dropped holdout days).

  uv run python hypotheses/H29-driver-nodes/analysis/explore.py               # all units, 2 processes
  uv run python hypotheses/H29-driver-nodes/analysis/explore.py --unit G38

Per unit: O1 kappa (+ named/unnamed, humans), O9 dilution, O2 network, O3 structural controllability, O4 Gramian
ranking (+ split halves, robustness), O5 net current, O6 validators V1/V2 cross-fitted on even/odd days, O7 rivals,
O8 scaling inputs, O10 human messages. Writes data/processed/H29-driver-nodes/<unit>/results.json and agents.parquet.
"""
from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402

COUNTED = ["G38", "G39", "G40", "G41", "G42", "G44", "G51b", "G51c", "G51d"]
DESCRIPTIVE = ["G37", "G51a", "G51e"]
K_BINS = [(1, 1), (2, 3), (4, 7), (8, 15), (16, 10_000)]


def subset_kappa(R: pl.DataFrame, expr, B: int = 500, seed: int = L.SEED) -> dict:
    """kappa with the visible rows restricted by expr and the full invisible set as placebo."""
    return L.kappa_unit(R.filter((~pl.col("vis")) | (pl.col("vis") & expr)), B=B, seed=seed)


def dilution(R: pl.DataFrame, B: int = 300, seed: int = L.SEED) -> dict:
    """kappa per visible-set size bin, and beta from kappa_b = kappa0 (k_b / 3)^-beta (WLS, grid), day bootstrap."""
    inv = R.filter(~pl.col("vis"))
    days = sorted(set(R["day_idx"].to_list()))
    dpos = {d: i for i, d in enumerate(days)}
    mats, kc = [], []
    for lo, hi in K_BINS:
        Rb = pl.concat([R.filter(pl.col("vis") & (pl.col("k") >= lo) & (pl.col("k") <= hi)), inv])
        Ds = L.day_sums(Rb)
        M = np.zeros((len(days), len(L.SUM_COLS)))
        for r in Ds.iter_rows(named=True):
            M[dpos[r["day_idx"]]] = [r[c] for c in L.SUM_COLS]
        mats.append(M)
        sub = R.filter(pl.col("vis") & (pl.col("k") >= lo) & (pl.col("k") <= hi))
        kc.append(float(sub["k"].mean()) if sub.height else np.nan)
    kc = np.array(kc)

    def kap(w):
        return np.array([L.kappa_from_sums(dict(zip(L.SUM_COLS, (M * w[:, None]).sum(0))))["kappa"] for M in mats])

    k0 = kap(np.ones(len(days)))
    rng = np.random.default_rng(seed)
    bs = np.array([kap(np.bincount(rng.integers(len(days), size=len(days)), minlength=len(days)).astype(float))
                   for _ in range(B)]) if len(days) >= 2 else np.full((1, len(K_BINS)), np.nan)
    var = np.nanvar(bs, axis=0)
    grid = np.linspace(-1.5, 2.5, 81)

    def fit(kv, vv):
        ok = np.isfinite(kv) & np.isfinite(vv) & (vv > 0) & np.isfinite(kc)
        if ok.sum() < 3:
            return np.nan, np.nan
        w = 1 / vv[ok]
        best = (np.inf, np.nan, np.nan)
        for b in grid:
            f = (kc[ok] / 3.0) ** (-b)
            c0 = (w * f * kv[ok]).sum() / (w * f * f).sum()
            sse = (w * (kv[ok] - c0 * f) ** 2).sum()
            if sse < best[0]:
                best = (sse, b, c0)
        return best[1], best[2]

    beta, c0 = fit(k0, var)
    bb = np.array([fit(b, var)[0] for b in bs]) if len(days) >= 2 else np.array([np.nan])
    bb = bb[np.isfinite(bb)]
    return dict(k_center=kc, kappa_bins=k0, kappa_bins_se=np.sqrt(var), beta=beta, kappa0=c0,
                beta_ci=[float(np.percentile(bb, 5)), float(np.percentile(bb, 95))] if len(bb) else None,
                n_rows=[int(R.filter(pl.col("vis") & (pl.col("k") >= lo) & (pl.col("k") <= hi)).height) for lo, hi in K_BINS])


def significant_edges(pk: dict, q: float = 0.1) -> np.ndarray:
    z = pk["z"]
    N = z.shape[0]
    ok = np.isfinite(z)
    adj = np.zeros((N, N))
    if not ok.any():
        return adj
    p = 1 - norm.cdf(z[ok])  # one-sided: pull > 0
    o = np.argsort(p)
    m = len(p)
    thr = q * (np.arange(1, m + 1)) / m
    passed = np.zeros(m, bool)
    below = np.where(p[o] <= thr)[0]
    if len(below):
        passed[o[: below.max() + 1]] = True
    idx = np.argwhere(ok)
    for (i, j), s in zip(idx, passed):
        adj[i, j] = float(s)
    return adj


def modal_room(U: dict, agents: list[int]) -> dict:
    T = U["turns"]
    g = T.group_by("agent", "room").len().sort("len", descending=True).unique("agent", keep="first")
    return {int(a): int(r) for a, r in zip(g["agent"].to_list(), g["room"].to_list())}


def jaccard(a, b) -> float:
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if (a | b) else np.nan


def per_message_outpull(F: dict) -> np.ndarray:
    """Predicted one-step per-message spread of sender k: sum_j kappa_kj * (share of k's messages absorbed by j)."""
    K = np.where(np.isfinite(F["K"]), F["K"], 0.0)
    vol = np.where(F["vol"] > 0, F["vol"], np.nan)
    return (K * F["r"]).sum(1) / vol


def explore_unit(name: str) -> dict:
    t0 = time.time()
    emb = L.Emb()
    U = L.attach_vectors(L.load_unit(name), emb)
    R = L.row_stats(U)
    agents = L.network_agents(U)
    days = U["meta"]["days"]
    nd = len(days)
    even = {d for d in range(nd) if d % 2 == 0}
    odd = set(range(nd)) - even
    res = dict(unit=name, n_days=nd, n_agents=len(agents), agents=agents, counted=name in COUNTED)
    # O1
    ku = L.kappa_unit(R, B=1000)
    res["kappa"] = ku
    res["named_agent"] = subset_kappa(R, (pl.col("kind") == 0) & pl.col("ment_j"))
    res["unnamed_agent"] = subset_kappa(R, (pl.col("kind") == 0) & ~pl.col("ment_j"))
    res["human_named"] = subset_kappa(R, (pl.col("kind") == 1) & pl.col("ment_j"))
    res["human_bystander"] = subset_kappa(R, (pl.col("kind") == 1) & ~pl.col("ment_j"))
    res["dilution"] = dilution(R)
    # O2-O5 full fit
    F = L.fit_network(U, R, agents, B_unit=200, B_pair=300)
    adj = significant_edges(F["pair"])
    res["n_sig_edges"] = int(adj.sum())
    res["n_pairs_est"] = int(np.isfinite(F["pair"]["K"]).sum())
    res["lsb"] = L.lsb_drivers(adj, self_loops=False)
    res["lsb_self"] = L.lsb_drivers(adj, self_loops=True)
    # all positive estimated edges (dense) for the structural point
    res["lsb_dense_self"] = L.lsb_drivers((F["A"] > 0).astype(float), self_loops=True)
    res["gamma"] = F["gamma"]
    res["rho_D_net"] = L.spearman(F["D"], F["net"])
    res["rho_D_out"] = L.spearman(F["D"], F["out"])
    res["rho_D_vol"] = L.spearman(F["D"], F["vol"])
    res["rho_D_AC"] = L.spearman(F["D"], F["AC"])
    res["E_star"] = float(np.nanmin(F["E"]))
    res["E_med"] = float(np.nanmedian(F["E"]))
    res["D_max"] = float(np.nanmax(F["D"]))
    res["A_total_per_h"] = float(F["A"].sum())
    res["mean_in_strength"] = float(F["inn"].mean())
    res["net_spread"] = float(np.std(F["net"]))
    # robustness
    rob = {}
    for gm in (0.5, 2.0):
        Fg = L.fit_network(U, R, agents, gamma=F["gamma"] * gm, B_unit=20, B_pair=100)
        rob[f"gamma_x{gm}"] = L.spearman(Fg["D"], F["D"])
    Fs = L.fit_network(U, R, agents, clip=False, gamma=F["gamma"], B_unit=20, B_pair=100)
    rob["signed"] = L.spearman(Fs["D"], F["D"])
    Uraw = L.attach_vectors(L.load_unit(name), emb, kind="raw")
    Rraw = L.row_stats(Uraw)
    Fr = L.fit_network(Uraw, Rraw, agents, gamma=F["gamma"], B_unit=200, B_pair=100)
    rob["raw384"] = L.spearman(Fr["D"], F["D"])
    rob["raw384_kappa"] = Fr["kappa_unit"]["kappa"]
    rob["raw384_kappa_ci"] = Fr["kappa_unit"].get("kappa_ci")
    res["robust"] = rob
    # split halves
    hs = None
    if len(even) and len(odd):
        Fe = L.fit_network(U, R, agents, day_set=even, B_unit=100, B_pair=200)
        Fo = L.fit_network(U, R, agents, day_set=odd, B_unit=100, B_pair=200)
        res["split_half"] = {k: L.spearman(Fe[k], Fo[k]) for k in ("D", "net", "out", "vol", "AC")}
        res["kappa_even"] = Fe["kappa_unit"]["kappa"]
        res["kappa_odd"] = Fo["kappa_unit"]["kappa"]
        de = L.lsb_drivers(significant_edges(Fe["pair"]))["drivers"]
        do = L.lsb_drivers(significant_edges(Fo["pair"]))["drivers"]
        res["lsb_jaccard"] = jaccard(de, do)
        top3e, top3o = set(np.argsort(-Fe["D"])[:3].tolist()), set(np.argsort(-Fo["D"])[:3].tolist())
        res["top3_overlap"] = len(top3e & top3o) / 3
        # validators
        dmap = {d: i for i, d in enumerate(days)}
        am = U["msgs"].filter(pl.col("kind") == 0).with_columns(
            pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day_idx"))
        hs = L.horizon_spread(U, am)
        pm = L.per_message_spread(R)
        folds = []
        for train, test, Ftr in ((even, odd, Fe), (odd, even, Fo)):
            hrs = L.active_hours(U, [days[d] for d in test])
            H = L.hourly_spread(hs, agents, hrs, day_set=test)
            p1 = pm.filter(pl.col("day_idx").is_in(list(test)) & (pl.col("kind") == 0)).group_by("sender").agg(
                pl.col("spread1").mean())
            mp = dict(zip(p1["sender"].to_list(), p1["spread1"].to_list()))
            S1 = np.array([mp.get(a, np.nan) for a in agents])
            expo = Ftr["r"].sum(1)
            folds.append(dict(V1=L.spearman(per_message_outpull(Ftr), S1), V2_D=L.spearman(Ftr["D"], H),
                              V2_vol=L.spearman(Ftr["vol"], H), V2_expo=L.spearman(expo, H),
                              V2_out=L.spearman(Ftr["out"], H), V2_net=L.spearman(Ftr["net"], H),
                              V2_AC=L.spearman(Ftr["AC"], H), H=H.tolist(), D_train=Ftr["D"].tolist()))
        res["folds"] = folds
        res["V"] = {k: float(np.nanmean([f[k] for f in folds])) if any(np.isfinite(f[k]) for f in folds) else None
                    for k in ("V1", "V2_D", "V2_vol", "V2_expo", "V2_out", "V2_net", "V2_AC")}
        # model-free reliability of the validator itself (does H_k replicate across halves?)
        Hs = [np.array(f["H"]) for f in folds]
        res["H_split_half"] = L.spearman(Hs[0], Hs[1])
        # humans: messages naming exactly one network agent; that agent's driver rank from the other half
        hm = U["msgs"].filter((pl.col("kind") == 1) & (pl.col("mentions").list.len() == 1)).with_columns(
            pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day_idx"),
            pl.col("mentions").list.first().alias("named"))
        hm = hm.filter(pl.col("named").is_in(agents))
        hum = []
        if hm.height:
            hh = L.horizon_spread(U, hm.drop("named"))
            nm = dict(zip(hm["msg"].to_list(), hm["named"].to_list()))
            pos = {a: i for i, a in enumerate(agents)}
            for r in hh.iter_rows(named=True):
                k = nm[r["msg"]]
                Fother = Fo if r["day_idx"] in even else Fe
                Dv = Fother["D"]
                pct = float((Dv < Dv[pos[k]]).mean() + 0.5 * (Dv == Dv[pos[k]]).mean())
                hum.append(dict(msg=r["msg"], named=k, pct=pct, spreadH=r["spreadH"], dd=r["dd"],
                                spread_norm=r["spreadH"] / r["dd"] if r["dd"] else None, n=r["n_same"] + r["n_other"]))
        res["humans"] = hum
    # two rooms
    rooms = modal_room(U, agents)
    rc = {}
    for a in agents:
        rc[rooms.get(a, -1)] = rc.get(rooms.get(a, -1), 0) + 1
    res["room_sizes"] = {str(k): v for k, v in rc.items()}
    if len([r for r, n in rc.items() if n >= 2]) >= 2:
        big = max(rc, key=rc.get)
        top = agents[int(np.nanargmax(F["D"]))]
        res["top_driver_room"] = rooms.get(top)
        res["larger_room"] = big
        res["top_in_larger_room"] = bool(rooms.get(top) == big)
        Rr = R.join(U["turns"].select("talk_id", "room"), on="talk_id", how="left")
        per_room = {}
        for r, n in rc.items():
            if n < 2:
                continue
            kk = subset_kappa(Rr.filter((pl.col("room") == r) | ~pl.col("vis")), pl.col("kind") == 0, B=300)
            per_room[str(r)] = dict(n_agents=n, kappa=kk["kappa"], kappa_ci=kk.get("kappa_ci"), kappa_x=kk["kappa_x"],
                                    n_V=kk["n_V"])
        res["per_room"] = per_room
    # per-agent table
    names = dict(zip(*[c.to_list() for c in pl.read_parquet(L.SH / "roster.parquet").select("agent", "name").get_columns()]))
    tab = pl.DataFrame(dict(agent=agents, name=[names.get(a, str(a)) for a in agents],
                            room=[rooms.get(a, -1) for a in agents], D=F["D"], E=F["E"], AC=F["AC"], G=F["G"],
                            net=F["net"], out=F["out"], inn=F["inn"], vol=F["vol"], expo=F["r"].sum(1),
                            lsb_class=res["lsb"]["classes"]))
    tab.write_parquet(L.OUT / name / "agents.parquet")
    res["top_driver"] = names.get(agents[int(np.nanargmax(F["D"]))])
    res["top3"] = [names.get(agents[i]) for i in np.argsort(-F["D"])[:3]]
    np.save(L.OUT / name / "A.npy", F["A"].astype(np.float32))
    res["secs"] = time.time() - t0
    L.jdump(res, L.OUT / name / "results.json")
    return res


def short(res: dict) -> str:
    k = res["kappa"]
    v = res.get("V") or {}
    sh = res.get("split_half") or {}
    return (f"{res['unit']}: N={res['n_agents']} days={res['n_days']} kappa {k['kappa']:.4f} {k.get('kappa_ci')} "
            f"contam {k['contamination']:.4f} kx {k['kappa_x']:.4f} | split D {sh.get('D')} | V2 D {v.get('V2_D')} vol "
            f"{v.get('V2_vol')} | top {res.get('top_driver')} | E* {res['E_star']:.3g} ({res['secs']:.0f}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", default=None)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    units = [a.unit] if a.unit else COUNTED + DESCRIPTIVE
    t = time.time()
    with ProcessPoolExecutor(max_workers=min(2, a.workers)) as ex:
        for r in ex.map(explore_unit, units):
            print(short(r), flush=True)
    L.write_provenance("explore", "hypotheses/H29-driver-nodes/analysis/explore.py",
                       {"units": units, "estimator": "marginal", "T_horizon_h": L.T_HORIZON_H, "spread_h": L.SPREAD_H,
                        "n_min_pair": L.N_MIN_PAIR, "bh_q": 0.1})
    print(f"done {time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
