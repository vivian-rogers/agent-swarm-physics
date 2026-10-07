"""Real per-call project labels for an H137 skeleton, from the shared builder infra/shared/project_calls.py
(H133's agent state (categorical, project per call) and project hop (call); label = E 100 carry).

labels_for(S) returns arrays aligned to the skeleton's calls:
  label[c]  project after call c (int code, -1 = none), cur[c] = label at the agent's previous call (prev_label),
  hop[c]    project hop (call) flag. Project names are coded per unit (never written out).
Reserved rows are masked by the skeleton (holdout_mask) and asserted here.
"""
from __future__ import annotations

import numpy as np
import polars as pl

import h137lib as L

def labels_for(S: dict, variant: str = "e100", keep_names: bool = False) -> dict:
    pc = (pl.scan_parquet(L.SH / "project_calls.parquet")
          .filter(pl.col("turn_id").is_in(S["turn"].tolist()))
          .select("turn_id", "holdout", "label", "prev_label", "hop", "hop_e50", "hop_e300", "proj",
                  "label_e50_null", "label_e300_null")
          .collect())
    assert not pc["holdout"].any(), "reserved rows reached H137"
    pc = pl.DataFrame({"turn_id": S["turn"], "k": np.arange(S["n"])}).join(pc, on="turn_id", how="left").sort("k")
    if variant == "e100":
        lab, prv, hop = pc["label"], pc["prev_label"], pc["hop"].fill_null(False)
    else:
        e = variant[1:]
        nulls = pc[f"label_e{e}_null"].fill_null(True)
        lab = pl.Series(np.where(nulls.to_numpy(), None, pc["label"].to_numpy()))
        # previous call's label under the variant: shift within agent
        ag = S["ag"]
        prv_arr = np.full(S["n"], None, dtype=object)
        la = lab.to_numpy()
        for ix in S["by_agent"]:
            prv_arr[ix[1:]] = la[ix[:-1]]
        prv = pl.Series(prv_arr)
        hop = pc[f"hop_e{e}"].fill_null(False)
    names = sorted(set(x for x in lab.to_list() + prv.to_list() if x is not None))
    code = {n: k for k, n in enumerate(names)}
    label = np.array([code[x] if x is not None else -1 for x in lab.to_list()], dtype=np.int64)
    cur = np.array([code[x] if x is not None else -1 for x in prv.to_list()], dtype=np.int64)
    out = {"label": label, "cur": cur, "hop": hop.to_numpy().astype(bool), "n_projects": len(names)}
    if keep_names:  # in memory only (kickoff-naming variant); never written out
        out["names"] = names
    return out
