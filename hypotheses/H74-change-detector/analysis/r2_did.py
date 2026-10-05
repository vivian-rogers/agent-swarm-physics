"""H74 round 2, R4: provider API response-format changes as family-targeted difference-in-differences (card: Round 2).
DiD = mean over target-family agents of (post - pre) minus the same over other agents; pre = 5 scored days before day
0, post = days 0..+4; agents need >= 3 days on each side; windows may not cross a reserved gap. Null: the same DiD for
the same target family at every eligible non-event day of the same regime (no provider date within the window).
Two-sided rank p; Holm over 5 events x 5 outcomes. Non-reserved days only.
Run: uv run python hypotheses/H74-change-detector/analysis/r2_did.py
Output: data/processed/H74-change-detector/r2/did.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from r2_common import OUT, OUT1, PROVIDER, SH, load_frame  # noqa: E402

OUTCOMES = ["log_out", "log_turnaround", "infra_err_share", "rec_per_call", "cache_share"]
PRE, POST = 5, 5


def holm(ps):
    ps = np.asarray(ps, float)
    order = np.argsort(ps)
    adj = np.empty(ps.size)
    run = 0.0
    for r, k in enumerate(order):
        run = max(run, min(1.0, (ps.size - r) * ps[k]))
        adj[k] = run
    return adj


def main():
    fr = load_frame("ext")
    agd = pl.read_parquet(OUT1 / "agent_day_features.parquet")
    lab = dict(pl.read_parquet(SH / "roster.parquet").select("agent", "lab").iter_rows())
    T = fr.T
    # contiguous windows: no missing calendar active day (reserved gap) between t-PRE and t+POST-1
    ok_win = np.zeros(T, bool)
    for t in range(PRE, T - POST + 1):
        ok_win[t] = (fr.cpos[t + POST - 1] - fr.cpos[t - PRE]) == (PRE + POST - 1)
    prov_idx = {e: fr.day_pos[next(x for x in fr.cal_days if x >= d)] for e, d, _, _ in PROVIDER}
    near_prov = np.zeros(T, bool)
    for i in prov_idx.values():
        near_prov[max(0, i - PRE - POST):min(T, i + PRE + POST)] = True
    mats = {}
    agents = sorted(agd["agent"].unique().to_list())
    apos = {a: j for j, a in enumerate(agents)}
    for f in OUTCOMES:
        Mx = np.full((len(agents), T), np.nan)
        for a, d, v in agd.select("agent", "pt_date", f).iter_rows():
            if d in fr.day_pos and v is not None:
                Mx[apos[a], fr.day_pos[d]] = v
        mats[f] = Mx
    fam = np.array([lab.get(a) for a in agents])

    def did(Mx, t, target):
        pre = Mx[:, t - PRE:t]; post = Mx[:, t:t + POST]
        npre = np.isfinite(pre).sum(1); npost = np.isfinite(post).sum(1)
        ok = (npre >= 3) & (npost >= 3)
        with np.errstate(all="ignore"):
            delta = np.nanmean(post, 1) - np.nanmean(pre, 1)
        tg = ok & (fam == target); ct = ok & (fam != target)
        if tg.sum() < 2 or ct.sum() < 2:
            return None, int(tg.sum()), int(ct.sum())
        return float(np.mean(delta[tg]) - np.mean(delta[ct])), int(tg.sum()), int(ct.sum())

    rows = []
    for e, d, target, label in PROVIDER:
        t = prov_idx[e]
        reg = fr.regime[t]
        null_days = [u for u in range(PRE, T - POST + 1) if ok_win[u] and not near_prov[u] and fr.regime[u] == reg
                     and fr.eligible[u]]
        for f in OUTCOMES:
            est, ntg, nct = did(mats[f], t, target) if ok_win[t] else (None, 0, 0)
            nulls = [x for x in (did(mats[f], u, target)[0] for u in null_days) if x is not None]
            p = float((1 + np.sum(np.abs(nulls) >= abs(est))) / (1 + len(nulls))) if est is not None and nulls else None
            rows.append({"event": e, "day0": fr.dl[t], "target": target, "outcome": f, "did": est, "n_target": ntg,
                         "n_control": nct, "n_null": len(nulls), "p": p,
                         "null_q025_q975": [float(np.percentile(nulls, 2.5)), float(np.percentile(nulls, 97.5))] if nulls else None})
    ps = [r["p"] if r["p"] is not None else 1.0 for r in rows]
    for r, a in zip(rows, holm(ps)):
        r["p_holm"] = float(a)
    (OUT / "did.json").write_text(json.dumps({"rows": rows, "n_tests": len(rows),
                                              "n_holm_005": int(sum(r["p_holm"] < 0.05 for r in rows))}, indent=1))
    for r in rows:
        print(r["event"], r["day0"], r["target"], r["outcome"], None if r["did"] is None else round(r["did"], 3),
              r["n_target"], r["n_control"], r["n_null"], r["p"], round(r["p_holm"], 3))
    print("Holm < 0.05:", sum(r["p_holm"] < 0.05 for r in rows))


if __name__ == "__main__":
    main()
