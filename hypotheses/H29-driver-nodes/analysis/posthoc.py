"""H29 Amendment 2 (POST HOC, after the first real-data run of explore.py): visibility-boundary test and the
proximity-adjusted influence network. Labeled post hoc everywhere it is reported.

Why: the pre-registered invisible placebo (H18's rule) is contaminated: 39-70% of 'invisible' rows come from call
windows longer than 30 s (PAUSE or long tool calls, after which the wake call does see the messages), and content
similarity falls steeply with time-to-reply, so even truly invisible messages (posted within seconds of the reply) are
the closest in time of all. The boundary test compares visible and truly invisible messages at matched time-to-reply.

  uv run python hypotheses/H29-driver-nodes/analysis/posthoc.py
"""
from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402
from explore import COUNTED, DESCRIPTIVE, jaccard, modal_room, per_message_outpull, significant_edges  # noqa: E402


def posthoc_unit(name: str) -> dict:
    t0 = time.time()
    emb = L.Emb()
    U = L.attach_vectors(L.load_unit(name), emb)
    R = L.add_timing(U, L.row_stats(U))
    agents = L.network_agents(U)
    days = U["meta"]["days"]
    nd = len(days)
    even = {d for d in range(nd) if d % 2 == 0}
    odd = set(range(nd)) - even
    res = dict(unit=name, n_days=nd, n_agents=len(agents), counted=name in COUNTED)
    res["rd"] = L.rd_kappa(R, B=1000)
    res["rd_named"] = L.rd_kappa(R.filter(~pl.col("vis") | pl.col("ment_j")), B=500)
    res["rd_unnamed"] = L.rd_kappa(R.filter(~pl.col("vis") | ~pl.col("ment_j")), B=500)
    # like-for-like controls (primary): named visible vs named truly-invisible; unnamed vs unnamed
    res["rd_named_ll"] = L.rd_kappa(R.filter(pl.col("ment_j")), B=1000)
    res["rd_unnamed_ll"] = L.rd_kappa(R.filter(~pl.col("ment_j")), B=1000)
    # pre-registered kappa with the placebo restricted to truly invisible rows (no proximity matching)
    res["kappa_trueinv"] = L.kappa_unit(R.filter(pl.col("vis") | (pl.col("c") <= L.C_MAX_S)), B=500)
    F = L.fit_network_v2(U, R, agents, B_pair=300)
    res["base"] = F["base"]
    res["gamma"] = F["gamma"]
    adj = significant_edges(F["pair"])
    res["n_sig_edges"] = int(adj.sum())
    res["n_pairs_est"] = int(np.isfinite(F["pair"]["K"]).sum())
    res["lsb"] = L.lsb_drivers(adj)
    res["lsb_self"] = L.lsb_drivers(adj, self_loops=True)
    res["lsb_dense_self"] = L.lsb_drivers((F["A"] > 0).astype(float), self_loops=True)
    res["rho_D_net"] = L.spearman(F["D"], F["net"])
    res["rho_D_vol"] = L.spearman(F["D"], F["vol"])
    res["rho_D_out"] = L.spearman(F["D"], F["out"])
    res["E_star"] = float(np.nanmin(F["E"]))
    res["E_med"] = float(np.nanmedian(F["E"]))
    res["E_vol_top"] = float(F["E"][int(np.argmax(F["vol"]))])
    res["A_total_per_h"] = float(F["A"].sum())
    res["mean_out_per_h"] = float(F["out"].mean())
    res["mean_r_per_h"] = float(F["r"].sum(1).mean())
    rob = {}
    for gm in (0.5, 2.0):
        rob[f"gamma_x{gm}"] = L.spearman(L.fit_network_v2(U, R, agents, gamma=F["gamma"] * gm, base=F["base"],
                                                          B_pair=60)["D"], F["D"])
    rob["base_x0.5"] = L.spearman(L.fit_network_v2(U, R, agents, gamma=F["gamma"], base=0.5 * F["base"], B_pair=60)["D"], F["D"])
    rob["base_x2"] = L.spearman(L.fit_network_v2(U, R, agents, gamma=F["gamma"], base=2 * F["base"], B_pair=60)["D"], F["D"])
    Uraw = L.attach_vectors(L.load_unit(name), emb, kind="raw")
    Rraw = L.add_timing(Uraw, L.row_stats(Uraw))
    Fr = L.fit_network_v2(Uraw, Rraw, agents, gamma=F["gamma"], B_pair=100)
    rob["raw384"] = L.spearman(Fr["D"], F["D"])
    rob["raw384_jump"] = Fr["rd"]["jump"]
    rob["raw384_jump_ci"] = Fr["rd"].get("ci")
    res["robust"] = rob
    if len(even) and len(odd):
        Fe = L.fit_network_v2(U, R, agents, day_set=even, B_pair=200)
        Fo = L.fit_network_v2(U, R, agents, day_set=odd, B_pair=200)
        res["split_half"] = {k: L.spearman(Fe[k], Fo[k]) for k in ("D", "net", "out", "vol", "AC")}
        res["jump_even"], res["jump_odd"] = Fe["rd"]["jump"], Fo["rd"]["jump"]
        res["lsb_jaccard"] = jaccard(L.lsb_drivers(significant_edges(Fe["pair"]))["drivers"],
                                     L.lsb_drivers(significant_edges(Fo["pair"]))["drivers"])
        res["top3_overlap"] = len(set(np.argsort(-Fe["D"])[:3]) & set(np.argsort(-Fo["D"])[:3])) / 3
        res["top1_same"] = bool(int(np.argmax(Fe["D"])) == int(np.argmax(Fo["D"])))
        dmap = {d: i for i, d in enumerate(days)}
        am = U["msgs"].filter(pl.col("kind") == 0).with_columns(
            pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day_idx"))
        hs = L.horizon_spread(U, am)
        pm = L.per_message_spread(R)
        folds, Hs, S1s = [], [], []
        for train, test, Ftr in ((even, odd, Fe), (odd, even, Fo)):
            hrs = L.active_hours(U, [days[d] for d in test])
            H = L.hourly_spread(hs, agents, hrs, day_set=test)
            p1 = pm.filter(pl.col("day_idx").is_in(list(test)) & (pl.col("kind") == 0)).group_by("sender").agg(
                pl.col("spread1").mean())
            mp = dict(zip(p1["sender"].to_list(), p1["spread1"].to_list()))
            S1 = np.array([mp.get(a, np.nan) for a in agents])
            Hs.append(H)
            S1s.append(S1)
            folds.append(dict(V1=L.spearman(per_message_outpull(Ftr), S1), V2_D=L.spearman(Ftr["D"], H),
                              V2_vol=L.spearman(Ftr["vol"], H), V2_expo=L.spearman(Ftr["r"].sum(1), H),
                              V2_out=L.spearman(Ftr["out"], H), V2_net=L.spearman(Ftr["net"], H),
                              V2_AC=L.spearman(Ftr["AC"], H)))
        res["V"] = {k: (float(np.nanmean([f[k] for f in folds])) if any(np.isfinite(f[k]) for f in folds) else None)
                    for k in folds[0]}
        res["H_split_half"] = L.spearman(Hs[0], Hs[1])
        res["S1_split_half"] = L.spearman(S1s[0], S1s[1])
        # per-agent arrays for figures
        res["D_even"], res["D_odd"] = Fe["D"].tolist(), Fo["D"].tolist()
        res["H_even"], res["H_odd"] = Hs[1].tolist(), Hs[0].tolist()   # H measured on even days / odd days
        res["vol_even"], res["vol_odd"] = Fe["vol"].tolist(), Fo["vol"].tolist()
    rooms = modal_room(U, agents)
    rc = {}
    for a in agents:
        rc[rooms.get(a, -1)] = rc.get(rooms.get(a, -1), 0) + 1
    res["room_sizes"] = {str(k): v for k, v in rc.items()}
    if len([r for r, n in rc.items() if n >= 2]) >= 2:
        big = max(rc, key=rc.get)
        top = agents[int(np.nanargmax(F["D"]))]
        res["top_in_larger_room"] = bool(rooms.get(top) == big)
        # per-room proximity-adjusted mean pull of the room's recipients (base + mean residual), descriptive
        Rr = R.join(U["turns"].select("talk_id", "room"), on="talk_id", how="left")
        pr = {}
        for r, n in rc.items():
            if n < 2:
                continue
            Rx = Rr.filter(((pl.col("room") == r) | ~pl.col("vis")))
            rdx = L.rd_kappa(Rx, B=300)
            Kr = F["K"][np.ix_([i for i, a in enumerate(agents) if rooms.get(a) == r],
                               [i for i, a in enumerate(agents) if rooms.get(a) == r])]
            pr[str(r)] = dict(n_agents=n, rd_jump=rdx["jump"], rd_ci=rdx.get("ci"), mean_pair_kappa=float(np.nanmean(Kr)))
        res["per_room"] = pr
    names = dict(zip(*[c.to_list() for c in pl.read_parquet(L.SH / "roster.parquet").select("agent", "name").get_columns()]))
    tab = pl.DataFrame(dict(agent=agents, name=[names.get(a, str(a)) for a in agents], room=[rooms.get(a, -1) for a in agents],
                            D=F["D"], E=F["E"], AC=F["AC"], net=F["net"], out=F["out"], inn=F["inn"], vol=F["vol"],
                            expo=F["r"].sum(1), lsb_class=res["lsb"]["classes"]))
    tab.write_parquet(L.OUT / name / "agents_v2.parquet")
    np.save(L.OUT / name / "A_v2.npy", F["A"].astype(np.float32))
    res["agents"] = agents
    res["names"] = [names.get(a, str(a)) for a in agents]
    res["D"] = F["D"].tolist()
    res["vol"] = F["vol"].tolist()
    res["top_driver"] = names.get(agents[int(np.nanargmax(F["D"]))])
    res["top3"] = [names.get(agents[i]) for i in np.argsort(-F["D"])[:3]]
    res["top_vol"] = names.get(agents[int(np.argmax(F["vol"]))])
    res["secs"] = time.time() - t0
    L.jdump(res, L.OUT / name / "results_posthoc.json")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", default=None)
    a = ap.parse_args()
    units = [a.unit] if a.unit else COUNTED + DESCRIPTIVE
    t = time.time()
    with ProcessPoolExecutor(max_workers=2) as ex:
        for r in ex.map(posthoc_unit, units):
            v = r.get("V") or {}
            sh = r.get("split_half") or {}
            print(f"{r['unit']}: jump {r['rd']['jump']:.4f} {r['rd']['ci']} | split D {sh.get('D')} vol {sh.get('vol')} | "
                  f"V2 D {v.get('V2_D')} vol {v.get('V2_vol')} out {v.get('V2_out')} | H split {r.get('H_split_half')} | "
                  f"top {r['top_driver']} (vol top {r['top_vol']}) ({r['secs']:.0f}s)", flush=True)
    L.write_provenance("posthoc", "hypotheses/H29-driver-nodes/analysis/posthoc.py",
                       {"units": units, "amendment": 2, "dt_bins_rd": L.DT_BINS_RD, "c_max_s": L.C_MAX_S,
                        "dt_bins_adj": L.DT_BINS_ADJ})
    print(f"done {time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
