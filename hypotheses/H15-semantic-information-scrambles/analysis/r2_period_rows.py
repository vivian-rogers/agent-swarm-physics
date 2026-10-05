"""H15 round 2 rows for the shared per-period estimates table (infra/shared/estimates.py: write_estimates).

    uv run python hypotheses/H15-semantic-information-scrambles/analysis/r2_period_rows.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC = "data/processed/H15-semantic-information-scrambles/r2/results.json"
NK = "forced erasures (F) + pseudo-erasures (P)"
M_RR = "Poisson FE (agent-period x arm), exp(b class x F), log1p(V_pre); "


def ok(x):
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)


def rows() -> list[dict]:
    r = json.loads((L.DATA / "results.json").read_text())
    out = []

    def add(common, stat, est, lo, hi, n, method, null, kind, notes=None, post_hoc=False):
        if not ok(est):
            return
        out.append({**common, "statistic": stat, "estimate": est, "ci_lo": lo if ok(lo) else None,
                    "ci_hi": hi if ok(hi) else None, "n": n, "method": method, "null": null,
                    "ci_kind": kind if ok(lo) else "none", "post_hoc": post_hoc, "notes": notes})

    for p in L.PERIODS:
        g = int(p[1:3])
        common = {"period_unit": E.map_unit(g), "goal_no": g, "unit_local": L.FOLDER.get(p, p), "role": "replication",
                  "ci_level": 0.95, "source": SRC, "n_kind": NK}
        a = r["R1a"]["per"][p]
        add({**common, "channel": "context:call"}, "r2_reread_share_diff", a["diff"], a["lo"], a["hi"],
            a["n_F"] + a["n_P"], "read-or-search share of calls 1-5, F minus P (cluster bootstrap SE)", "0", "se_z")
        for key, stat, y in (("T1xF", "r2_trail_RR_T1", "V20"), ("T2xF", "r2_trail_RR_T2", "V20")):
            d = r["R1b"]["per"].get(p, {}).get(key)
            if isinstance(d, dict):
                add({**common, "channel": "artifact_trail:call"}, stat, d["RR"], d["lo_sw"], d["hi_sw"],
                    r["R1b"]["per"][p]["n"], M_RR + f"outcome {y}; own commits to A_prev 24 h, older than call -40",
                    "1 (trail-blind dip)", "se_z")
        for key, ch in (("LxF", "last_files"), ("MxF", "new_messages"), ("GpxF", "notes_or_search"),
                        ("GnxF", "note_names_repo")):
            d = r["R2"]["per"].get(p, {}).get(key)
            if isinstance(d, dict):
                add({**common, "channel": f"{ch}:call"}, "r2_firstread_RR", d["RR"], d["lo_sw"], d["hi_sw"],
                    r["R2"]["per"][p]["n"], M_RR + "class in calls 1-2, outcome work commits in calls 3-20",
                    "1 (no extra value after erasure)", "se_z")
        t = r["R3"]["per"].get(p)
        if t:
            cm = {**common, "channel": "memory_note:commands", "n_kind": "consolidation notes"}
            for k, stat, null in (("E_s", "r3_excess_recall_swap", "0 (window swap, same agent >= 3 days)"),
                                  ("Enov_s", "r3_excess_recall_swap_novel", "0 (window swap, novel terms)"),
                                  ("E_x", "r3_excess_recall_xagent", "+0.035 (synthetic floor of the cross-agent null)"),
                                  ("r_post", "r3_recall_post", "none"),
                                  ("pre_minus_post", "r3_recall_pre_minus_post", "0"),
                                  ("decay", "r3_excess_decay_10_vs_31", "0")):
                d = t[k]
                add(cm, stat, d["est"], d["lo"], d["hi"], d["n"],
                    "IDF-weighted recall of note terms in the next segment's command text (agent-day cluster bootstrap)",
                    null, "percentile")
    # NE41 pooled (native)
    common = {"period_unit": "local:NE41", "goal_no": 51, "unit_local": "NE41 pooled regime III", "role": "native",
              "ci_level": 0.95, "source": SRC, "n_kind": NK}
    for key, ch in (("LxF", "last_files"), ("MxF", "new_messages"), ("GpxF", "notes_or_search"),
                    ("GnxF", "note_names_repo")):
        d = r["R2"]["NE41"][key]
        add({**common, "channel": f"{ch}:call"}, "r2_firstread_RR", d["RR"], d["lo_boot"], d["hi_boot"],
            r["R2"]["NE41"]["n"], M_RR + "class in calls 1-2, outcome calls 3-20; agent-day cluster bootstrap B=300",
            "1", "percentile")
    d = r["R2"]["proxy_none"]
    add({**common, "channel": "none_of_first_reads:call"}, "r2_firstread_RR", d["RR"], d["lo_boot"], d["hi_boot"],
        r["R2"]["NE41"]["n"], M_RR + "no L, M or Gp in calls 1-2 (scramble by proxy)", "1", "percentile")
    c = r["R2"]["concentration"]
    add({**common, "channel": "first_reads:call"}, "r2_dip_share_first_reads", c["dip_share_U12"]["share"],
        c["dip_share_U12"]["share_ci"][0], c["dip_share_U12"]["share_ci"][1], r["R2"]["NE41"]["n"],
        "share of the erasure dip (calls 6-20) removed when L or M occurs in calls 1-2 (stratum FE, explicit F)", "0",
        "percentile")
    add({**common, "channel": "first_reads:call"}, "r2_concentration_ratio", c["ratio"], c["ratio_ci"][0],
        c["ratio_ci"][1], r["R2"]["NE41"]["n"], "RR(L or M in calls 1-2) / RR(first in calls 3-5), outcome calls 6-20",
        "1", "percentile")
    for key, stat in (("T1xF", "r2_trail_RR_T1"), ("T2xF", "r2_trail_RR_T2")):
        d = r["R1b"]["NE41"][key]
        add({**common, "channel": "artifact_trail:call"}, stat, d["RR"], d["lo_boot"], d["hi_boot"],
            r["R1b"]["NE41"]["n"], M_RR + "outcome V20; cluster bootstrap B=300", "1", "percentile")
    return out


if __name__ == "__main__":
    rr = rows()
    E.write_estimates(rr, hypothesis="H15")
    print("wrote", len(rr), "rows")
