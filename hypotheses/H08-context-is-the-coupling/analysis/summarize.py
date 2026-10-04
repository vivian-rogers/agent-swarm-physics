"""Collect H08 round-1 numbers into data/processed/H08-context-is-the-coupling/summary.json and print the
'Results by goal period' table rows for the card."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403

ALL = [24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]


def load(p):
    p = OUT / p
    return json.loads(p.read_text()) if p.exists() else None


def pp(x):
    return f"{100 * x[0]:+.2f} [{100 * x[1]:+.2f}, {100 * x[2]:+.2f}]"


def main():
    tab = load("period_table.json")
    S = {"c9": {}, "counts": {}}
    rows = []
    cnt = {k: 0 for k in ("V1", "V2", "V3_pass", "V3_n", "V4", "V5_pass", "V5_n", "A6_ok", "clean_addr", "clean_talk", "floor_clean")}
    for g in ALL:
        d = load(f"{gname(g)}/c9.json"); p = d["primary"]; c = d["posthoc_clean"]
        v1 = p["talk"]["D"][1] > 0; v2 = p["addr"]["D"][1] > 0
        cnt["V1"] += v1; cnt["V2"] += v2; cnt["V4"] += p["talk"]["G"]["2"][0] < p["talk"]["G"]["1"][0]
        cnt["A6_ok"] += p["addr"]["pre"][1] <= 0 <= p["addr"]["pre"][2]
        cnt["clean_addr"] += c["addr"]["D"][1] > 0; cnt["clean_talk"] += c["talk"]["D"][1] > 0
        cnt["floor_clean"] += abs(c["addr"]["G"]["0"][0]) < c["addr"]["G"]["1"][0] / 3
        if "other_room" in d and "talk" in d["other_room"]:
            o = d["other_room"]; cnt["V3_n"] += 1
            cnt["V3_pass"] += all(abs(o[k]["D"][0]) < abs(p[k]["D"][0]) / 3 and o[k]["D"][1] <= 0 <= o[k]["D"][2] for k in ("talk", "addr"))
        if PERIODS[g]["regime"] in ("III", "II/III"):
            cnt["V5_n"] += 1; cnt["V5_pass"] += 10 <= d["W_active_s"][1] <= 40
        c8 = load(f"{gname(g)}/c8.json"); s8 = (c8 or {}).get("sets", {}).get("nudge_target_iso", {})
        c3 = load(f"{gname(g)}/c3.json")
        c8s = (f"{s8['n_cells']} cells" + (f", Φ {s8['shape']['phi_1_5'][0]:.2f} vs {s8['shape']['phi_1_5_pred_hr'][0]:.2f}"
                                          if s8.get('n_cells', 0) >= 30 else "")) if s8 else "—"
        c3s = pp(c3["beta"]["erased_F"]) if c3 and "beta" in c3 else "—"
        c1 = load("cc/c1.json")["periods"].get(gname(g)) if g in CC_PERIODS else None
        c1s = (f"recall {c1['recall']:.2f}, replay {100 * (c1.get('replay_share') or 0):.0f}%" if c1 and c1.get("n_fetches") else
               ("no fetches" if g in CC_PERIODS else "—"))
        rows.append(f"| [{gname(g)}](goalperiod-subhypotheses/{gname(g)}/README.md) | {PERIODS[g]['regime']} · {PERIODS[g]['mode']} | "
                    f"{d['n_days']} | {pp(p['talk']['D'])} | {pp(p['addr']['D'])} | {pp(c['addr']['D'])} | {c8s} | {c1s} | {c3s} | "
                    f"{tab[gname(g)]['verdict']} |")
        S["c9"][gname(g)] = {"D_talk": p["talk"]["D"], "D_addr": p["addr"]["D"], "clean_D_addr": c["addr"]["D"],
                             "clean_D_talk": c["talk"]["D"], "W_active_s": d["W_active_s"]}
    S["counts"] = {k: int(v) for k, v in cnt.items()}
    S["verdicts"] = {k: v["verdict"] for k, v in tab.items()}
    jdump(S, OUT / "summary.json")
    print("\n".join(rows))
    print(S["counts"])


if __name__ == "__main__":
    main()
