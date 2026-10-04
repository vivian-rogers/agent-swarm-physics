"""H58 replication summary (card P1-P5, P8) from results/units/*.json; P8 evaluates qualifying member sets on the next
goal period's data. Writes results/replication.json. Run after run.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h58data as HD  # noqa: E402
import h58lib as L  # noqa: E402
from run import jsonable  # noqa: E402

RES = HD.D / "results"
NEXT = {"30": "31", "31": "33", "33": "35", "35": "36b", "36b": "37", "37": "38a", "38c": "39", "39": "40", "40": "41",
        "41": "42", "42": "44", "44": "51a"}


def fin(x):
    return x is not None and np.isfinite(x)


def zmin(c):
    vals = [c.get("z_comp"), c.get("z_shift")]
    vals = [v for v in vals if fin(v)]
    return min(vals) if len(vals) == 2 else None


def main():
    meta = HD.units_meta()
    order = [x["unit"] for x in meta]
    U = {u: json.loads((RES / "units" / f"{u}.json").read_text()) for u in order if (RES / "units" / f"{u}.json").exists()}
    out = {"units_order": [u for u in order if u in U], "per_unit": {}}
    p1, p2_room, p2_lab, p3, p4a, p4b, p5 = [], [], [], [], [], [], []
    quals = {}
    for u in out["units_order"]:
        r = U[u]
        C = r["candidates"]
        s = C["search"][0] if C["search"] else None
        multi_q = [c for c in C["multi"] if c["qualifies"]]
        search_q = bool(s and s.get("qualifies_search"))
        cand_q = multi_q + ([s] if search_q else [])
        quals[u] = cand_q
        p1.append(bool(cand_q))
        med = r["summary"]["median_z"]
        if med.get("multi") is not None and C["room"] and med.get("room") is not None:
            p2_room.append(med["multi"] > med["room"])
        if med.get("multi") is not None and C["lab"] and med.get("lab") is not None:
            p2_lab.append(med["multi"] > med["lab"])
        multi_room = len({a for c in C["room"] for a in c["members"]}) > 0
        for c in cand_q:
            if multi_room:
                p3.append(len(c["rooms"]) >= 2)
            if fin(c.get("iota")) and fin(c.get("iota_members")):
                p4a.append(c["iota"] >= c["iota_members"])
            if fin(c.get("z_iota_shift")):
                p4b.append(c["z_iota_shift"] >= 2)
        best = s if s else (max(C["multi"], key=lambda c: c["g"] if fin(c["g"]) else -9) if C["multi"] else None)
        if best is not None and fin(best.get("g_night")) and fin(best.get("z_night_comp")):
            p5.append(bool(best["g_night"] > 0 and best["z_night_comp"] >= 2))
        sing = [x for x in r["singletons"] if fin(x.get("iota"))]
        plot = []
        for kind in ("search", "multi", "room", "lab"):
            for c in C.get(kind, []):
                plot.append({"kind": kind, "z": zmin(c), "qualifies": bool(c.get("qualifies_search") if kind == "search" else c["qualifies"]),
                             "n": c["n"], "g": c["g"]})
        out["per_unit"][u] = {
            "nA": r["nA"], "nB": r["nB"], "nD": r["nD"], "n_commits": r["n_commits"],
            "any_candidate": bool(cand_q), "n_multi": len(C["multi"]), "n_multi_qual": len(multi_q),
            "search": None if s is None else {k: s.get(k) for k in ("agents", "n", "g", "z_comp", "z_shift", "specificity",
                                                                    "g_out", "p_search", "qualifies", "qualifies_search",
                                                                    "share_join", "g_lag", "g_content", "g_night",
                                                                    "z_night_comp", "iota", "iota_members", "iota_shift_mu",
                                                                    "z_iota_shift", "rooms", "repos", "colonial",
                                                                    "organismal", "environmental")},
            "median_z": med, "singleton_iota_median": float(np.median([x["iota"] for x in sing])) if sing else None,
            "singleton_colonial_median": float(np.median([x["colonial"] for x in sing])) if sing else None,
            "qualifying": [{"from": ("search" if c is s else "multi"), "agents": c["agents"], "g": c["g"],
                            "z_comp": c["z_comp"], "z_shift": c["z_shift"], "specificity": c.get("specificity"),
                            "rooms": c["rooms"], "n": c["n"]} for c in cand_q],
            "candidates_plot": plot, "variants": r.get("variants")}
    # P8: qualifying member sets evaluated on the next goal period
    p8 = []
    for u, nxt in NEXT.items():
        if u not in quals or not quals[u] or not (RES / "units" / f"{nxt}.json").exists():
            continue
        Un = HD.load_unit(nxt)
        cn = L.CompNull(Un, n_draw=200, seed=8)
        for c in quals[u]:
            mem = [Un.agents.index(a) for a in c["agents"] if a in Un.agents and Un.act_a[Un.agents.index(a)] > 0]
            if len(mem) < 2:
                p8.append({"from": u, "to": nxt, "agents": c["agents"], "evaluable": False})
                continue
            ev = L.evaluate(Un, mem, cn, n_shift=60, seed=8)
            p8.append({"from": u, "to": nxt, "agents": c["agents"], "evaluable": True, "g": ev["g"],
                       "z_comp": ev["z_comp"], "z_shift": ev["z_shift"], "keeps": bool(fin(ev["z_comp"]) and ev["z_comp"] >= 2),
                       "qualifies": ev["qualifies"]})
    ev8 = [x for x in p8 if x.get("evaluable")]
    n = len(out["units_order"])
    out["predictions"] = {
        "P1": {"units_with_candidate": int(sum(p1)), "n_units": n, "share": sum(p1) / n if n else None,
               "verdict": "supported" if sum(p1) >= 2 / 3 * n else ("failed" if sum(p1) <= n / 3 else "mixed")},
        "P2": {"multi_gt_room": [int(sum(p2_room)), len(p2_room)], "multi_gt_lab": [int(sum(p2_lab)), len(p2_lab)]},
        "P3": {"spanning": [int(sum(p3)), len(p3)]},
        "P4": {"as_written_iota_ge_members": [int(sum(p4a)), len(p4a)], "amended_iota_gt_aggregation": [int(sum(p4b)), len(p4b)]},
        "P5": {"night_best_unit": [int(sum(p5)), len(p5)]},
        "P8": {"keeps": [int(sum(x["keeps"] for x in ev8)), len(ev8)], "rows": p8},
    }
    # pooled descriptive: search results' g and specificity; singletons
    gs = [out["per_unit"][u]["search"]["g"] for u in out["units_order"] if out["per_unit"][u]["search"] and fin(out["per_unit"][u]["search"]["g"])]
    out["pooled"] = {"search_g_median": float(np.median(gs)) if gs else None,
                     "search_qualifying_units": [u for u in out["units_order"] if out["per_unit"][u]["search"]
                                                 and out["per_unit"][u]["search"].get("qualifies_search")]}
    (RES / "replication.json").write_text(json.dumps(jsonable(out), indent=1))
    print(json.dumps(jsonable(out["predictions"]), indent=1)[:5000])
    for u in out["units_order"]:
        pu = out["per_unit"][u]
        s = pu["search"] or {}
        print(u, "cand" if pu["any_candidate"] else "-", f"multi {pu['n_multi_qual']}/{pu['n_multi']}",
              "search n", s.get("n"), "g", None if s.get("g") is None else round(s["g"], 3),
              "zc", None if s.get("z_comp") is None else round(s["z_comp"], 1),
              "zs", None if s.get("z_shift") is None else round(s["z_shift"], 1),
              "spec", None if s.get("specificity") is None else round(s["specificity"], 2), "p", s.get("p_search"))


if __name__ == "__main__":
    main()
