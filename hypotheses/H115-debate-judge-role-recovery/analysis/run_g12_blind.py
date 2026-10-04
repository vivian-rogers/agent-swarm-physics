"""H115 G12 blind step: per-debate sink rankings from talk spins only, frozen and hashed BEFORE any role label is read.

  uv run python hypotheses/H115-debate-judge-role-recovery/analysis/run_g12_blind.py

Reads data/processed/H115-debate-judge-role-recovery/G12/ (built from DQ6 `phase` rows only) and writes
G12/frozen_ranking.json plus its SHA-256 (G12/frozen_ranking.sha256). No `judge`, `team` or `debate_result` row is
loaded by this script or by anything it imports.

Estimators (card, Model; lambda frozen by Amendment A1):
  primary   additive in/out fit, all non-summary calls inside the all-present trim, agent x mode + agent x phase intercepts
  variant1  full J with ridge (same rows)
  variant2  chat-mode clock (H67-R1): chat-mode calls only, reads OR-accumulated since the previous chat-mode call
  variant3  untrimmed (all calls in the debate window)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h115lib as L  # noqa: E402

LAM = None  # set from Amendment A1 below
A1 = json.loads((L.DATA / "synthetic" / "amendment_A1.json").read_text())
LAM = float(A1["lambda"])
LAM_FULL = float(A1["lambda_fullJ"])


def main():
    calls, XR, XP, agents = L.load("G12")
    chat_mask, XRc = L.chat_clock(calls, XR)
    wins = sorted(w for w in calls["win"].unique().to_list() if w is not None)
    out = {"lambda": LAM, "lambda_fullJ": LAM_FULL, "agents": agents, "debates": {}}
    for w in wins:
        rec = {}
        for var in ("primary", "fullJ", "chatclock", "untrimmed"):
            m = (calls["win"] == w).fill_null(False).to_numpy()
            if var != "untrimmed":
                m &= calls["trim"].to_numpy()
            Xr = XR
            if var == "chatclock":
                m &= chat_mask
                Xr = XRc
            cw = calls.filter(pl.Series(m))
            ph = np.array([p if p is not None else "none" for p in cw["phase"].to_list()])
            pres = L.present_agents(cw)
            if len(pres) < 3:
                rec[var] = None
                continue
            if var == "fullJ":
                f = L.fit_fullJ(cw, Xr[m], XP[m], agents, pres, LAM_FULL, phase=ph)
            else:
                f = L.fit_additive(cw, Xr[m], XP[m], agents, pres, LAM, phase=ph)
            rec[var] = {"pres": pres, "S": [round(float(x), 6) for x in f["S"]],
                        "SP": [round(float(x), 6) for x in f["SP"]],
                        "rank": L.ranks_desc(f["S"]).tolist(), "rankP": L.ranks_desc(f["SP"]).tolist(),
                        "n_calls": f["n"]}
            if var == "primary":
                rec[var]["alpha"] = [round(float(x), 6) for x in f["alpha"]]
                rec[var]["beta"] = [round(float(x), 6) for x in f["beta"]]
        rec["top_sink_primary"] = (rec["primary"]["pres"][int(np.argmin(rec["primary"]["rank"]))]
                                   if rec.get("primary") else None)
        out["debates"][w] = rec
    blob = json.dumps(out, indent=1, sort_keys=True).encode()
    h = hashlib.sha256(blob).hexdigest()
    d = L.DATA / "G12"
    (d / "frozen_ranking.json").write_bytes(blob)
    (d / "frozen_ranking.sha256").write_text(h + "\n")
    print("frozen", h)
    for w in wins:
        r = out["debates"][w]
        print(w, "top sink (primary):", r["top_sink_primary"])


if __name__ == "__main__":
    main()
