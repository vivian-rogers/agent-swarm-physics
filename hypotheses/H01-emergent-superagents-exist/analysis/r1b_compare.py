"""H01 round 1b: round-1 (D3.1.a / D3.2) headline statistics, round 1 vs each round-1b instrument, side by side.

Reads data/processed/H01-emergent-superagents-exist/explore.json (round 1 as reported) and r1b/<tag>/explore.json
(analysis/explore.py --r1b <tag>); writes r1b/compare.json and prints a table. Also the angle between round-1 and
shared goal fields per unit (g-hat and room kickoffs; bge, whitened d = 32).

Usage: uv run python hypotheses/H01-emergent-superagents-exist/analysis/r1b_compare.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h01common import OUT  # noqa: E402

import numpy as np  # noqa: E402

TAGS = ["bge_none", "bge_restate", "bge_copies", "gte_none", "gte_restate", "gte_copies", "bge_restate_style",
        "gte_restate_style", "bge_restate_ledger"]


def g(d, *path, default=None):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return default
        d = d[p]
    return d


def row(r: dict) -> dict:
    P1, P2, P3 = g(r, "p1", "P1", default={}), g(r, "p1", "P2", default={}) or {}, g(r, "p1", "P3", default={})
    P5, P6, P7 = g(r, "p56", "P5", default={}), g(r, "p56", "P6", default={}), g(r, "p56", "P7", default={})
    tw = g(P6, "two_room", default={}) or {}
    out = {
        "P1_median_dH": g(P1, "median_dH"), "P1_frac_neg": g(P1, "frac_dH_neg"), "P1_frac_p05": g(P1, "frac_p05"),
        "P1_units_both": g(P1, "n_units_meeting_both"), "P1_n_units": g(P1, "n_units_with_days"), "P1_pass": g(P1, "pass"),
        "P2_lab_raw_median": g(P2, "lab_raw", "median_dH"), "P2_lab_frac_neg": g(P2, "lab_raw", "frac_dH_neg"),
        "P2_lab_shrink": g(P2, "lab_shrink"), "P2_room_shrink": g(P2, "room_shrink"), "P2_pass": g(P2, "pass"),
        "P3_frac_below_q05": g(P3, "frac_below_q05"),
        "P3_jump_within": g(P3, "goal_change_jumps", "median_within"), "P3_jump_across": g(P3, "goal_change_jumps", "median_across"),
        "P4_pol_8": g(r, "p4", "P4", "pol_g_8"), "P4_pol_21": g(r, "p4", "P4", "pol_g_21"),
        "P5_n_ge06": g(P5, "n_ge_0.6"), "P5_n": g(P5, "n_units"), "P5_median_r2": g(P5, "median_r2"),
        "P5_median_rot": g(P5, "median_r2_rot"),
        "P6_re": g(P6, "re_slope", "mu"), "P6_re_se": g(P6, "re_slope", "se"), "P6_re_p": g(P6, "re_slope", "p_two"),
        "P6_p_rot": g(P6, "re_slope", "p_rot_null"), "P6_p_shuf": g(P6, "re_slope", "p_shuf_null"),
        "P6_I2": g(P6, "re_slope", "I2"), "P6_npos": g(P6, "n_pos"), "P6_n": g(P6, "n_units"),
        "P6_dir1": g(P6, "re_dir_lo_saw_hi", "mu"), "P6_dir1_p": g(P6, "re_dir_lo_saw_hi", "p_two"),
        "P6_dir2": g(P6, "re_dir_hi_saw_lo", "mu"), "P6_dir2_p": g(P6, "re_dir_hi_saw_lo", "p_two"),
        "P6_joint_same": g(P6, "re_joint_same", "mu"), "P6_joint_lag": g(P6, "re_joint_lag", "mu"),
        "P6_room_pos": int(sum(1 for v in tw.values() if v["within_minus_cross"] > 0)) if tw else None,
        "P6_room_n": len(tw) if tw else None,
        "P6_room_p05": int(sum(1 for v in tw.values() if v["p_agent_room_perm"] < 0.05)) if tw else None,
        "P6_wc": {k: v["within_minus_cross"] for k, v in tw.items()},
        "P6_wc_roomfield": {k: v["roomfield_removed"] for k, v in tw.items()},
        "P6_pass": g(P6, "pass"),
        "P7_did": g(P7, "new", "did"), "P7_se": g(P7, "new", "se"), "P7_p_perm": g(P7, "new", "p_perm_one_sided"),
        "P9_median": g(r, "p9", "P9", "median_bJn"), "P9_n_ge05": g(r, "p9", "P9", "n_bJn_ge_0.5"), "P9_n": g(r, "p9", "P9", "n_units"),
        "per_unit_P1": {k: g(v, "room", "median_dH") for k, v in (g(r, "p1", "per_unit", default={}) or {}).items()},
        "per_unit_slope": {k: (v.get("slope"), v.get("slope_se")) for k, v in (g(r, "p56", "per_unit", default={}) or {}).items()},
        "per_unit_r2": {k: (v.get("r2"), v.get("r2_rot_mean")) for k, v in (g(r, "p56", "per_unit", default={}) or {}).items()},
        "per_unit_P9": {k: v.get("bJ_over_n") for k, v in (g(r, "p9", "units", default={}) or {}).items()},
    }
    return out


def field_angles() -> dict:
    """Principal angle (deg) between round-1 and shared g-hat per regime-III unit (bge, round-1 basis)."""
    from h01data import P56_UNITS, Scheme
    S0 = Scheme(d=32, shared_room_kickoffs=False)
    S1 = Scheme(d=32, base=OUT / "r1b" / "bge_none")
    out = {}
    for name in P56_UNITS:
        ui = S0.units[name]
        R = ui["regimes"][-1] if len(ui["regimes"]) == 1 else ui["regimes"][0]
        a, b = S0.ghat(ui["goal_no"], R), S1.ghat(ui["goal_no"], R)
        rec = {"ghat_deg": float(np.degrees(np.arccos(np.clip(a["ghat"] @ b["ghat"], -1, 1))))}
        if a["kick"] is not None and b["kick"] is not None:
            rec["kick_deg"] = float(np.degrees(np.arccos(np.clip(a["kick"] @ b["kick"], -1, 1))))
        rooms = {}
        for r_, v in a["room"].items():
            if r_ in b["room"]:
                rooms[str(r_)] = float(np.degrees(np.arccos(np.clip(v @ b["room"][r_], -1, 1))))
        rec["room_deg"] = rooms
        out[name] = rec
    return out


def main():
    res = {"r1": row(json.loads((OUT / "explore.json").read_text()))}
    for t in TAGS:
        p = OUT / "r1b" / t / "explore.json"
        if p.exists():
            res[t] = row(json.loads(p.read_text()))
    res["field_angles"] = field_angles()
    (OUT / "r1b" / "compare.json").write_text(json.dumps(res, indent=1, default=float))
    keys = [k for k in res["r1"] if not isinstance(res["r1"][k], dict)]
    cols = ["r1"] + [t for t in TAGS if t in res]
    print("stat".ljust(20) + "".join(c[:13].rjust(14) for c in cols))
    for k in keys:
        vals = []
        for c in cols:
            v = res[c].get(k)
            vals.append(("–" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))).rjust(14))
        print(k.ljust(20) + "".join(vals))
    print("field angles", json.dumps(res["field_angles"], indent=None))


if __name__ == "__main__":
    main()
