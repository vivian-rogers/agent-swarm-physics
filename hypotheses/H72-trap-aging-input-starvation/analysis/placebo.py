"""H72 in-flight placebo on the corrected window (amendment A2, post hoc bug fix).

Messages by others posted in the gate's room during the gate call's model latency (t_call, t_call + latency] cannot be
in the gate's context and cannot answer its output. Their coefficient, added to the two-clock model, should be ~0.
The first version used (t_call, t_end], which for a pause call includes the timer and is outcome-dependent.
Usage: uv run python hypotheses/H72-trap-aging-input-starvation/analysis/placebo.py  (updates G<NN>/results.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h72lib as L  # noqa: E402


def main():
    g = pl.read_parquet(L.OUT / "gates.parquet")
    for f in sorted(L.OUT.glob("G*/results.json")):
        r = json.loads(f.read_text())
        if "beta_a0" not in r["primary"]:
            continue
        per = int(r["period"][1:])
        P = L.prep(g.filter(pl.col("goal_no") == per), "sus", "novel")
        if np.std(P["inflight"]) == 0:
            r["placebo_v2"] = {"note": "no in-flight messages"}
        else:
            pt = L.point(P, extra={"inflight": P["inflight"]})
            r["placebo_v2"] = {"beta_inflight": pt["beta_inflight"], "se_inflight": pt["se_inflight"],
                               "ci_inflight": [pt["beta_inflight"] - 1.96 * pt["se_inflight"],
                                               pt["beta_inflight"] + 1.96 * pt["se_inflight"]],
                               "beta_s_with": pt["beta_s"], "beta_a_with": pt["beta_a"],
                               "share_with_inflight": float(np.mean(P["inflight"] > 0))}
        r["placebo_v1_note"] = "v1 window (t_call, t_end] is outcome-dependent for pause calls; superseded by placebo_v2"
        f.write_text(json.dumps(r, indent=1, default=float))
        print(r["period"], {k: round(v, 3) if isinstance(v, float) else v for k, v in r["placebo_v2"].items()
                            if k != "ci_inflight"}, [round(x, 3) for x in r["placebo_v2"].get("ci_inflight", [])])


if __name__ == "__main__":
    main()
