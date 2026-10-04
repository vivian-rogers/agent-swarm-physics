"""H115 replication (R1): blind sink rank of the designated leader in G26, G35, G44 role windows.

  uv run python hypotheses/H115-debate-judge-role-recovery/analysis/run_replication.py [--skel 100]

Per window: the additive in/out fit (lambda from A1) on trimmed calls (G26, G35: the day's all-present trim; G44: the
#best agents' all-present trim per day), the leader's normalized sink rank u_L = (r - 1)/(n - 1) under S (read) and
SP (in-flight). Field-only skeleton null: J = 0 worlds on the real skeleton with each agent's real talk rate per
window x call mode; the leader's u_L distribution (H65 Known issue: single-agent ranks need a skeleton null).
Writes data/processed/H115-debate-judge-role-recovery/<G>/replication.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h115lib as L  # noqa: E402

CS = L.CS
LAM = float(json.loads((L.DATA / "synthetic" / "amendment_A1.json").read_text())["lambda"])


def leaders(period: str) -> dict:
    g = int(period[1:])
    ld = (pl.scan_parquet(CS.SH / "ground_truth_labels.parquet")
          .filter((pl.col("goal_no") == g) & pl.col("preferred") & ~pl.col("holdout") & (pl.col("label_kind") == "leader"))
          .collect())
    if period == "G35":
        out = {}
        for unit, det, ag in ld.select("unit", "detail", "agent").iter_rows():
            out[f"{unit.replace('day_', '')}_{'best' if 'room=best' in det else 'rest'}"] = int(ag)
        return out
    return {"*": int(ld["agent"][0])}


def window_mask(calls, period, w):
    m = (calls["win"] == w).fill_null(False).to_numpy()
    if period == "G44":
        sub = calls.filter(pl.Series(m))
        keep = CS.all_present_trim(sub, min_calls=20)
        mm = np.zeros(calls.height, bool)
        mm[np.where(m)[0][keep]] = True
        return mm
    return m & calls["trim"].to_numpy()


_S = {}


def _init(period):
    calls, XR, XP, agents = L.load(period)
    wins = sorted(w for w in calls["win"].unique().to_list() if w is not None)
    masks = {w: window_mask(calls, period, w) for w in wins}
    s = calls["s"].to_numpy()
    a = calls["agent"].to_numpy()
    md = calls["mode"].to_numpy()
    win = np.array([w if w is not None else "none" for w in calls["win"].to_list()])
    h = np.zeros(calls.height)
    keys = np.char.add(np.char.add(a.astype(str), "|"), np.char.add(win, np.char.add("|", md.astype(str))))
    for k in np.unique(keys):
        sel = keys == k
        p = ((s[sel] > 0).sum() + 0.5) / (sel.sum() + 1.0)
        h[sel] = 0.5 * np.log(p / (1 - p))
    _S.update(period=period, calls=calls, XR=XR, XP=XP, agents=agents, wins=wins, masks=masks, h=h,
              lead=leaders(period))


def lead_of(w):
    ld = _S["lead"]
    return ld.get(w, ld.get("*"))


def fit_all(s=None, XR=None, XP=None):
    calls, agents = _S["calls"], _S["agents"]
    XR = _S["XR"] if XR is None else XR
    XP = _S["XP"] if XP is None else XP
    out = {}
    for w in _S["wins"]:
        m = _S["masks"][w]
        cw = calls.filter(pl.Series(m))
        pres = L.present_agents(cw)
        k = lead_of(w)
        if k is None or k not in pres or len(pres) < 3:
            out[w] = None
            continue
        f = L.fit_additive(cw, XR[m], XP[m], agents, pres, LAM, s_override=None if s is None else s[m])
        q = pres.index(k)
        n = len(pres)
        out[w] = {"n": n, "rank": int(L.ranks_desc(f["S"])[q]), "rankP": int(L.ranks_desc(f["SP"])[q]),
                  "u": (L.ranks_desc(f["S"])[q] - 1) / (n - 1), "uP": (L.ranks_desc(f["SP"])[q] - 1) / (n - 1),
                  "n_calls": f["n"], "lead": k}
    return out


def skel(seed):
    calls, agents = _S["calls"], _S["agents"]
    A = len(agents)
    Z = np.zeros((A, A))
    s, XRs, XPs = CS.simulate(calls, agents, _S["h"], lambda k: Z, np.zeros(A), seed=seed)
    r = fit_all(s, XRs, XPs)
    return {w: (None if v is None else v["u"]) for w, v in r.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skel", type=int, default=100)
    ap.add_argument("--periods", default="G26,G35,G44")
    a = ap.parse_args()
    for period in a.periods.split(","):
        _init(period)
        obs = fit_all()
        with ProcessPoolExecutor(max_workers=2, initializer=_init, initargs=(period,)) as ex:
            sk = list(ex.map(skel, range(7000, 7000 + a.skel), chunksize=4))
        res = {"period": period, "lambda": LAM, "windows": obs, "skeleton": {}}
        for w, v in obs.items():
            if v is None:
                continue
            null = np.array([d[w] for d in sk if d.get(w) is not None])
            res["skeleton"][w] = {"mean_u_null": float(null.mean()), "p_null_ge": float((null >= v["u"]).mean())}
        ok = [v for v in obs.values() if v is not None]
        res["summary"] = {"n_windows": len(ok), "n_source_half": int(sum(v["u"] >= 0.5 for v in ok)),
                          "mean_u": float(np.mean([v["u"] for v in ok])) if ok else None,
                          "mean_uP": float(np.mean([v["uP"] for v in ok])) if ok else None,
                          "mean_u_null": float(np.mean([res["skeleton"][w]["mean_u_null"] for w in res["skeleton"]]))
                          if res["skeleton"] else None}
        (L.DATA / period / "replication.json").write_text(json.dumps(res, indent=1, default=float))
        print(period, json.dumps(res["summary"]), json.dumps(obs, default=float))


if __name__ == "__main__":
    main()
