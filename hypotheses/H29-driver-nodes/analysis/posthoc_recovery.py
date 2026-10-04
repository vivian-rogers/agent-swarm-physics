"""H29 post-hoc recovery check at the FITTED magnitude (Amendment 1 item 5; run after the real fit, disclosed).

Generator as in synthetic.py, with the fitted structure: unnamed pull a_u per message, named pull = named_mult x a_u
(fitted in #51: visibility jump unnamed ~0.01, named ~0.11), sender heterogeneity sigma_s = 0.7. The Amendment-2
(post hoc) pipeline is applied: boundary test, proximity-adjusted network, D ranking, split halves, V2.
Question: if the model were exactly true at the fitted effect sizes, would the driver ranking be recovered, and could
the held-out spread validator (V2) confirm it at village sampling?

  uv run python hypotheses/H29-driver-nodes/analysis/posthoc_recovery.py
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402
import synthetic as S  # noqa: E402

COND = {"fit51": dict(a=0.01, named_mult=11.0), "fit2room": dict(a=0.01, named_mult=8.0),
        "strong": dict(a=0.03, named_mult=4.0)}


def run(job):
    unit, cond, rep = job
    t = time.time()
    U = L.load_unit(unit)
    sk = S.Skeleton(U)
    rng = np.random.default_rng(L.SEED + 77 * rep + len(cond))
    P = S.draw_params(sk, rng, a_mean=COND[cond]["a"], sigma_s=0.7)
    P["named_mult"] = COND[cond]["named_mult"]
    Usyn, Dtrue = S.simulate_unit(sk, P, nonlinear=False, seed=L.SEED + 500 + rep, truth=True)
    R = L.add_timing(Usyn, L.row_stats(Usyn, seed=rep))
    agents = L.network_agents(Usyn)
    ai = [sk.apos[a] for a in agents]
    dtr = Dtrue[ai]
    F = L.fit_network_v2(Usyn, R, agents, B_pair=60)
    nd = len(Usyn["meta"]["days"])
    even = {d for d in range(nd) if d % 2 == 0}
    odd = set(range(nd)) - even
    Fe = L.fit_network_v2(Usyn, R, agents, day_set=even, B_pair=40)
    Fo = L.fit_network_v2(Usyn, R, agents, day_set=odd, B_pair=40)
    dmap = {d: i for i, d in enumerate(Usyn["meta"]["days"])}
    am = Usyn["msgs"].filter(pl.col("kind") == 0).with_columns(
        pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day_idx"))
    hs = L.horizon_spread(Usyn, am)
    Hs, v2, v2t, v2v = [], [], [], []
    for test, Ftr in ((odd, Fe), (even, Fo)):
        hrs = L.active_hours(Usyn, [Usyn["meta"]["days"][d] for d in test])
        H = L.hourly_spread(hs, agents, hrs, day_set=test)
        Hs.append(H)
        v2.append(L.spearman(Ftr["D"], H))
        v2t.append(L.spearman(dtr, H))
        v2v.append(L.spearman(Ftr["vol"], H))
    rdn = L.rd_kappa(R.filter(~pl.col("vis") | pl.col("ment_j")), B=100)
    rdu = L.rd_kappa(R.filter(~pl.col("vis") | ~pl.col("ment_j")), B=100)
    out = dict(unit=unit, cond=cond, rep=rep, jump=F["rd"]["jump"], jump_named=rdn["jump"], jump_unnamed=rdu["jump"],
               rho_D=L.spearman(F["D"], dtr), rho_vol_truth=L.spearman(F["vol"], dtr),
               top_in_top3=bool(int(np.nanargmax(dtr)) in set(np.argsort(-F["D"])[:3])),
               split_half=L.spearman(Fe["D"], Fo["D"]), V2_D=float(np.nanmean(v2)), V2_truth=float(np.nanmean(v2t)),
               V2_vol=float(np.nanmean(v2v)), H_split=L.spearman(Hs[0], Hs[1]), secs=time.time() - t)
    return out


def main():
    jobs = ([("G51b", "fit51", r) for r in range(4)] + [("G38", "fit2room", r) for r in range(6)]
            + [("G41", "fit2room", r) for r in range(6)] + [("G51b", "strong", r) for r in range(2)])
    res = []
    with ProcessPoolExecutor(max_workers=2) as ex:
        for r in ex.map(run, jobs):
            res.append(r)
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    L.jdump(res, L.OUT / "synthetic" / "posthoc_recovery.json")
    groups = {}
    for r in res:
        groups.setdefault((r["unit"], r["cond"]), []).append(r)
    summ = {}
    for k, rs in groups.items():
        summ[f"{k[0]}/{k[1]}"] = {m: float(np.nanmedian([r[m] for r in rs])) for m in
                                  ("jump", "jump_named", "jump_unnamed", "rho_D", "rho_vol_truth", "split_half", "V2_D",
                                   "V2_truth", "V2_vol", "H_split")}
        summ[f"{k[0]}/{k[1]}"]["top_in_top3"] = float(np.mean([r["top_in_top3"] for r in rs]))
        summ[f"{k[0]}/{k[1]}"]["n"] = len(rs)
    L.jdump(summ, L.OUT / "synthetic" / "posthoc_recovery_summary.json")
    for k, v in summ.items():
        print(k, {m: round(x, 3) for m, x in v.items()})


if __name__ == "__main__":
    main()
