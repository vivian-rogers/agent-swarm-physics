"""H115 synthetic check of the estimator variants (full J, chat-mode clock), before real data.

Same worlds as synthetic.py (sink a in {0, 0.3, 0.6}, b = 0); planted judge's rank under the full-J fit (lambda 4, 16)
and under the additive fit on the chat-mode clock (lambda 4). 50 reps each.
  uv run python hypotheses/H115-debate-judge-role-recovery/analysis/synthetic_variants.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h115lib as L  # noqa: E402
import synthetic as S  # noqa: E402

CS = L.CS


def world(args):
    a_s, rep = args
    if not S._G:
        S._init()
    calls, agents, h0, widx, wl, phase = (S._G[k] for k in ("calls", "agents", "h", "widx", "wl", "phase"))
    A = len(agents)
    rng = np.random.default_rng(5000 + 1000 * rep + int(100 * a_s))
    base = np.full((A, A), S.J0)
    np.fill_diagonal(base, 0)
    mats, judges = [], []
    for d in range(len(wl)):
        k = int(rng.integers(A))
        J = base.copy()
        J[k, [q for q in range(A) if q != k]] += a_s
        mats.append(J)
        judges.append(agents[k])
    s, XRs, XPs = CS.simulate(calls, agents, h0, lambda i: mats[widx[i]] if widx[i] >= 0 else base,
                              np.full(A, S.JSELF), seed=rep + 31)
    cs = calls.with_columns(pl.Series("s", s))
    chat, XRc = L.chat_clock(cs, XRs)
    out = {"a": a_s, "full4": [], "full16": [], "chat4": []}
    for d in range(len(wl)):
        m = widx == d
        cw = cs.filter(pl.Series(m))
        pres = L.present_agents(cw)
        k = judges[d]
        for lam, key in ((4.0, "full4"), (16.0, "full16")):
            f = L.fit_fullJ(cw, XRs[m], XPs[m], agents, pres, lam, phase=phase[m])
            out[key].append(int(L.ranks_desc(f["S"])[pres.index(k)]) if k in pres else np.nan)
        mc = m & chat
        cwc = cs.filter(pl.Series(mc))
        presc = L.present_agents(cwc)
        if k in presc and len(presc) >= 3:
            f = L.fit_additive(cwc, XRc[mc], XPs[mc], agents, presc, 4.0, phase=phase[mc])
            out["chat4"].append(int(L.ranks_desc(f["S"])[presc.index(k)]))
        else:
            out["chat4"].append(np.nan)
    return out


if __name__ == "__main__":
    jobs = [(a, r) for a in (0.0, 0.3, 0.6) for r in range(50)]
    with ProcessPoolExecutor(max_workers=2, initializer=S._init) as ex:
        res = list(ex.map(world, jobs, chunksize=2))
    summ = []
    for a in (0.0, 0.3, 0.6):
        rr = [r for r in res if r["a"] == a]
        row = {"a": a}
        for key in ("full4", "full16", "chat4"):
            R = np.array([r[key] for r in rr], dtype=float)
            med = np.nanmedian(R, 1)
            n1 = np.nansum(R == 1, 1)
            row[key] = {"p_rank1": float(np.nanmean(R == 1)), "support_rate": float(np.mean((med <= 2) & (n1 >= 4))),
                        "kill_rate": float(np.mean(med >= 4))}
        summ.append(row)
        print(json.dumps(row))
    (L.DATA / "synthetic" / "synthetic_variants.json").write_text(json.dumps(summ, indent=1))
