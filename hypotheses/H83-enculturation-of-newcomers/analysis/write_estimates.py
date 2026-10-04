"""Write H83 rows to the shared per_period_estimates table (non-holdout only)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h83lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

rep = json.loads((L.DATA / "replication" / "replication.json").read_text())
nat = json.loads((L.DATA / "natives" / "natives.json").read_text())
newc = L.newcomers()
info = {int(a): (g, u, jd) for a, g, u, jd in newc.select("agent", "join_goal", "join_unit", "join_day").iter_rows()}
SRC = "data/processed/H83-enculturation-of-newcomers/replication/replication.json"
rows = []
for a, r in rep["joins"].items():
    g, u, jd = info[int(a)]
    base = dict(goal_no=g, period_unit=f"local:join{a}", unit_local=f"join of agent {a} in unit {u}", first_day=jd,
                last_day=jd, role="replication", source=SRC, ci_kind="none",
                notes="windows: tenure days 2-4 (E) and 8-14 (L) after the join; may cross into later goal periods; "
                      "held-out days excluded")
    G = r["G"]
    rows.append({**base, "statistic": "enculturation_dG", "channel": "content_bge", "estimate": G["delta"],
                 "n": G["n_stmts_E"] + G["n_stmts_L"], "n_kind": "statements",
                 "method": "DiD of mean statement cosine with the veterans' same-day centroid (E->L), newcomer minus "
                           "same-day veterans; style_resid_period, kickoff span projected out", "null": "kickoff-only (0); synthetic null 95th pct +0.032 for the pooled mean"})
    if r.get("G_gte"):
        rows.append({**base, "statistic": "enculturation_dG", "channel": "content_gte", "estimate": r["G_gte"]["delta"],
                     "n": r["G_gte"]["n_stmts_E"] + r["G_gte"]["n_stmts_L"], "n_kind": "statements",
                     "method": "as content_bge with gte-modernbert vectors", "null": "kickoff-only (0)"})
    rows.append({**base, "statistic": "village_gap_E", "channel": "content_bge", "estimate": G["gap_E"],
                 "n": G["n_stmts_E"], "n_kind": "statements",
                 "method": "newcomer minus veterans' mean alignment, tenure days 2-4", "null": "0"})
    if r.get("K"):
        rows.append({**base, "statistic": "family_signature_dK", "channel": "content_bge", "estimate": r["K"]["delta"],
                     "n": r["K"]["n_stmts_E"] + r["K"]["n_stmts_L"], "n_kind": "statements",
                     "method": "DiD of M.(F_family - F_other) (first-day newcomer baselines, same regime, unnormalized)",
                     "null": "0"})
        rows.append({**base, "statistic": "family_signature_K_E", "channel": "content_bge", "estimate": r["K"]["gap_E"],
                     "n": r["K"]["n_stmts_E"], "n_kind": "statements",
                     "method": "newcomer minus veterans, M.(F_family - F_other), tenure days 2-4", "null": "0"})
    if r.get("S"):
        rows.append({**base, "statistic": "style_distance_dS", "channel": "style20", "estimate": r["S"]["delta"],
                     "n": r["S"]["n_stmts_E"] + r["S"]["n_stmts_L"], "n_kind": "messages",
                     "method": "DiD of mean squared distance to the veterans' day style centroid (20 standardized H13 features)",
                     "null": "0"})
g38 = nat["bge"]["G38"]
rows.append(dict(goal_no=38, period_unit="local:G38-rooms", unit_local="G38 04-20..04-24, two rooms", first_day="2026-04-20",
                 last_day="2026-04-24", role="native", statistic="own_room_minus_other_room_alignment", channel="content_bge",
                 estimate=g38["R_new"], ci_lo=g38["R_new_ci"][0], ci_hi=g38["R_new_ci"][1], ci_level=0.95, ci_kind="percentile",
                 n=g38["n_new_agent_days"], n_kind="agent-days", method="newcomers' (Opus 4.7, Kimi K2.6) alignment with own-room "
                 "minus other-room veterans; agent-day bootstrap", null="0", source="data/processed/H83-enculturation-of-newcomers/natives/natives.json"))
ne27 = nat["bge"]["NE27"]
rows.append(dict(goal_no=10, period_unit="local:G10-NE27", unit_local="NE27 batch, tenure days 2-4", first_day=ne27["E_days"][0],
                 last_day=ne27["E_days"][-1], role="native", statistic="village_gap_E_batch", channel="content_bge",
                 estimate=ne27["gap_E"], ci_lo=ne27["gap_E_ci"][0], ci_hi=ne27["gap_E_ci"][1], ci_level=0.95,
                 ci_kind="percentile", n=ne27["n_agent_days"], n_kind="agent-days",
                 method="NE27 newcomers' gap to the four veterans' same-day centroid; agent-day bootstrap", null="0",
                 source="data/processed/H83-enculturation-of-newcomers/natives/natives.json"))
w = E.write_estimates(rows, hypothesis="H83")
print("wrote", w.height)
