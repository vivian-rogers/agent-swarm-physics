"""H85 post hoc (labelled PH in the card; run after the pre-registered results were seen).
PH1  decompose the per-message addressing slope: ln(ment/msg) = ln(share of messages naming >= 1 agent)
     + ln(names per naming message); M1 slopes with goal-cluster CIs.
PH2  per-agent talk share: slope of ln(talk calls / all calls) on ln N, using H86's per-call counts (bins15 calls).
Writes posthoc/posthoc.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h85lib as L  # noqa: E402


def main():
    u = pl.read_parquet(L.DATA / "units.parquet").filter((pl.col("msg") >= 20) & (pl.col("ment_msgs") > 0))
    res = {}
    for name, y in (("naming_share", np.log(u["ment_msgs"].to_numpy() / u["msg"].to_numpy())),
                    ("names_per_naming_msg", np.log(u["ment"].to_numpy() / u["ment_msgs"].to_numpy()))):
        f = L.fit_beta(y, np.log(u["N"].to_numpy()), u["regime"].to_numpy(), u["goal_no"].to_numpy(), B=2000)
        f.pop("coefs")
        res[name] = f
        for r in ("I", "III"):
            s = u["regime"].to_numpy() == r
            res[name][f"within_{r}"] = float(L.ols(L.design(np.log(u["N"].to_numpy()[s]), None)[0], y[s])[0])
    calls = (pl.read_parquet(L.ROOT / "data/processed/H86-taylor-law-field-gauge/bins15.parquet")
             .group_by("unit_id").agg(pl.col("calls").sum().alias("calls_all")))
    v = u.join(calls, on="unit_id")
    for name, y in (("calls_per_agent_hour", np.log(v["calls_all"].to_numpy() / (v["N"].to_numpy() * v["T_h"].to_numpy()))),
                    ("talk_share_of_calls", np.log(v["talk_calls"].to_numpy() / v["calls_all"].to_numpy()))):
        f = L.fit_beta(y, np.log(v["N"].to_numpy()), v["regime"].to_numpy(), v["goal_no"].to_numpy(), B=2000)
        f.pop("coefs")
        res[name] = f
        for r in ("I", "III"):
            s = v["regime"].to_numpy() == r
            res[name][f"within_{r}"] = float(L.ols(L.design(np.log(v["N"].to_numpy()[s]), None)[0], y[s])[0])
    out = L.DATA / "posthoc"
    out.mkdir(parents=True, exist_ok=True)
    (out / "posthoc.json").write_text(json.dumps(res, indent=1, default=float))
    for k, f in res.items():
        print(k, round(f["beta"], 3), [round(f["ci_lo"], 3), round(f["ci_hi"], 3)], "I", round(f["within_I"], 3), "III", round(f["within_III"], 3))


if __name__ == "__main__":
    main()
