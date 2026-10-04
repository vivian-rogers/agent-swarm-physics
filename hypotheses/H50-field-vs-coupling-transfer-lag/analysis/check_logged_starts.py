"""Robustness: the read-out jump restricted to recipients whose call starts are LOGGED (Gemini HTTP timing; start_conf
high), per unit, vs the same recipients' jump in the main estimate. Guards against a latency-placement artifact in
chat-mode calls (talk calls run longer than the median latency, so a latency-placed start can fall after a message
that really arrived during generation)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h50lib as L  # noqa: E402
from build import load_unit  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
cw = pl.read_parquet(ROOT / "data/processed/shared/call_windows.parquet", columns=["turn_id", "start_conf", "start_src"])
conf = dict(zip(cw["turn_id"].to_list(), cw["start_conf"].cast(pl.String).to_list()))
rows = []
units = pl.read_parquet(OUT / "units.parquet").filter(pl.col("eligible") & (pl.col("kind") == "period_unit"))
for u, reg in zip(units["unit"], units["regime"]):
    U = load_unit(OUT / "units" / f"{u}.npz")
    U["N"] = int(U["N"])
    c, m, mp = U["calls"], U["msgs"], U["mpairs"]
    hi = np.array([conf.get(int(t)) == "high" for t in c["turn_id"]])
    share = np.bincount(c["agent"], weights=hi, minlength=U["N"]) / np.maximum(np.bincount(c["agent"], minlength=U["N"]), 1)
    logged_agents = np.where(share >= 0.8)[0]
    if len(logged_agents) == 0:
        continue
    keys = L.call_keys(U)
    W = 1.5 * L.median_call_interval(U)
    sel = np.isin(mp["rec"], logged_agents)
    if sel.sum() < 300:
        continue
    yT = c["talk"].astype(float)
    te, de, rec = m["t"][mp["msg"]][sel], m["day"][mp["msg"]][sel], mp["rec"][sel]
    g = L.gate_kernel(U, keys, te, de, rec, yT, K=2, W=W, nboot=200)
    # same recipients' talk calls: share in chat mode
    rows.append(dict(unit=u, regime=reg, n_logged_agents=len(logged_agents), pairs=int(sel.sum()),
                     J1=g["jumps"][0], lo=g["j_lo"][0], hi=g["j_hi"][0], J2=g["jumps"][1],
                     chat_share_talk=float(c["chat"][np.isin(c["agent"], logged_agents) & c["talk"]].mean())))
df = pl.DataFrame(rows)
df.write_parquet(OUT / "check_logged_starts.parquet")
pl.Config.set_tbl_rows(80)
print(df)
for reg in ("I", "II", "III"):
    s = df.filter(pl.col("regime") == reg)
    if len(s):
        se = ((s["hi"] - s["lo"]) / 3.92).to_numpy()
        w = 1 / se ** 2
        mm = (w * s["J1"].to_numpy()).sum() / w.sum()
        print(reg, "units", len(s), "pos", int((s["lo"] > 0).sum()), "neg", int((s["hi"] < 0).sum()), "IVW", round(mm, 4), "+-", round(1.96 / np.sqrt(w.sum()), 4))
