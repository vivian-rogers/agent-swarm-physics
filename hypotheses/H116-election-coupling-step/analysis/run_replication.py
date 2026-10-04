"""H116 replication: role steps in out-coupling for designated agents with out-of-role data in the same unit.

  uv run python hypotheses/H116-election-coupling-step/analysis/run_replication.py [--perm 200] [--periods G12,G35]

G12: windows = the ten debate episodes (DQ6 `phase` timing), designated agent = the debate's judge (DQ6 `judge`; read
only after H115's freeze, hash checked). G35: windows = room-days (rooms #best and #rest, 03-16..03-20), designated
agent = the room-day's lead designer (DQ6 `leader`, 03-16..03-18; none on 03-19/20).
Model (h116lib.role_design): agent x window x mode intercepts; per-sender out-coupling beta_a and per-recipient
in-coupling alpha_a pooled over windows; dOut = extra out-coupling of the designated agent inside its role window,
dIn = its extra in-coupling; in-flight analogs. Null: the designated label permuted among each window's present agents.
Writes data/processed/H116-election-coupling-step/<G>/replication.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h116lib as L  # noqa: E402

CS = L.CS
LAM = float(json.loads((L.DATA / "synthetic" / "amendment_A1.json").read_text())["lambda"])
H115_FROZEN = L.ROOT / "data/processed/H115-debate-judge-role-recovery/G12/frozen_ranking.sha256"


def gt(goal, kinds):
    return (pl.scan_parquet(CS.SH / "ground_truth_labels.parquet")
            .filter((pl.col("goal_no") == goal) & pl.col("preferred") & ~pl.col("holdout")
                    & pl.col("label_kind").is_in(kinds)).collect())


def windows(period):
    calls, XR, XP, agents = L.load(period)
    trim = calls["trim"].to_numpy()
    out = []
    if period == "G12":
        if not H115_FROZEN.exists():
            raise SystemExit("H115's G12 ranking is not frozen yet; refusing to read judge labels")
        ph = gt(12, ["phase"]).group_by("unit").agg(pl.col("t_valid_from").min().alias("a"),
                                                    pl.col("t_valid_to").max().alias("b")).sort("a")
        jd = {u: int(a) for u, a in gt(12, ["judge"]).select("unit", "agent").iter_rows()}
        for k, (u, a, b) in enumerate(ph.iter_rows()):
            m = ((calls["t_call"] >= a) & (calls["t_call"] < b)).to_numpy() & trim
            out.append((u, m, jd.get(u)))
    else:
        ld = gt(35, ["leader"])
        lead = {}
        for unit, det, ag in ld.select("unit", "detail", "agent").iter_rows():
            lead[(unit.replace("day_", ""), 2 if "room=best" in det else 3)] = int(ag)
        room = calls["room"].to_numpy()
        for day in sorted(calls["pt_date"].unique().to_list()):
            for r in (2, 3):
                m = (calls["pt_date"] == day).to_numpy() & (room == r) & trim
                if m.sum() > 50:
                    out.append((f"{day}_{r}", m, lead.get((day, r))))
    return calls, XR, XP, agents, out


_S = {}


def _init(period):
    calls, XR, XP, agents, W = windows(period)
    Ws = []
    for k, (u, m, lead) in enumerate(W):
        cw = calls.filter(pl.Series(m))
        vc = cw.group_by("agent").len()
        pres = sorted(int(a) for a, n in vc.iter_rows() if n >= 5)
        Ws.append({"calls": cw, "XR": XR[m], "XP": XP[m], "pres": pres, "lead": lead if lead in pres else None,
                   "wid": k, "unit": u})
    _S.update(period=period, agents=agents, W=Ws)


def perm(seed):
    rng = np.random.default_rng(seed)
    Wp = []
    for w in _S["W"]:
        w2 = dict(w)
        if w["lead"] is not None:
            w2["lead"] = int(rng.choice(w["pres"]))
        Wp.append(w2)
    f = L.fit_role(Wp, _S["agents"], LAM)
    return f["dOut"], f["dIn"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--periods", default="G12,G35")
    a = ap.parse_args()
    for period in a.periods.split(","):
        _init(period)
        obs = L.fit_role(_S["W"], _S["agents"], LAM, se=True)
        with ProcessPoolExecutor(max_workers=2, initializer=_init, initargs=(period,)) as ex:
            pr = np.array(list(ex.map(perm, range(3000, 3000 + a.perm), chunksize=4)))
        res = {"period": period, "lambda": LAM, "obs": obs, "n_windows": len(_S["W"]),
               "n_role_windows": int(sum(w["lead"] is not None for w in _S["W"])),
               "p_perm_dOut_greater": float((pr[:, 0] >= obs["dOut"]).mean()),
               "p_perm_dIn_greater": float((pr[:, 1] >= obs["dIn"]).mean()),
               "perm_sd_dOut": float(pr[:, 0].std()), "perm_mean_dOut": float(pr[:, 0].mean()),
               "perm_q95_dOut": float(np.percentile(pr[:, 0], 95)),
               "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        out = L.DATA / period
        (out / "replication.json").write_text(json.dumps(res, indent=1, default=float))
        print(period, json.dumps(res, default=float))


if __name__ == "__main__":
    main()
