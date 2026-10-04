"""H79 analysis per goal period: maxRAF / maxCAF coverage, catalyst classes, catalytic cycles vs the rewired null,
time arrow, strict-reactant sensitivity; natives G40 and NE29.

uv run python hypotheses/H79-artifact-autocatalytic-set/analysis/run.py [--period G51] [--natives]
Writes data/processed/H79-artifact-autocatalytic-set/results/<period>.json, natives.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import raflib as RL  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H79-artifact-autocatalytic-set"
RES = D / "results"
N_NULL = 100
REPLICATION = ["G51", "G31", "G38", "G41"]


def load(goal: int):
    ev = pl.read_parquet(D / "events.parquet").filter(pl.col("goal_no") == goal)
    events = []
    for r in ev.iter_rows(named=True):
        events.append({"eid": r["event_id"], "product": r["product"], "cat": r["cat"] or [], "cat_rev": r["cat_rev"] or [],
                       "reads": r["reads"] or [], "n_commits": r["n_commits"], "t_first": r["t_first"].timestamp(),
                       "kind": r["kind"], "agent": r["agent"], "day": r["pt_date"]})
    food = set(pl.read_parquet(D / "food.parquet").filter(pl.col("goal_no") == goal)["artifact"].to_list())
    return events, food


def strip(s: dict) -> dict:
    return {k: v for k, v in s.items() if not k.startswith("_")}


def n3(c):
    return sum(v for k, v in c["by_len"].items() if k >= 3)


def analyse(goal: int, seed: int = 0) -> dict:
    events, food = load(goal)
    rng = np.random.default_rng(seed)
    real = RL.summarize(events, food)
    strict = RL.summarize(events, food, strict=True)
    rev = RL.summarize(events, food, catkey="cat_rev")
    # rewired null: cycles (support >= 3 and any), coverage, in-period-tool share
    nulls = {"n3_s3": [], "n3_any": [], "coverage": [], "inperiod": [], "S3_s3": []}
    for _ in range(N_NULL):
        s = RL.summarize(RL.rewire(events, rng), food)
        nulls["n3_s3"].append(n3(s["cycles_support3"]))
        nulls["n3_any"].append(n3(s["cycles"]))
        nulls["S3_s3"].append(s["cycles_support3"]["S3"])
        nulls["coverage"].append(s["coverage"])
        nulls["inperiod"].append(s["inperiod_tool_share_work"])
    p = lambda obs, xs: (1 + sum(x >= obs for x in xs)) / (1 + len(xs))  # noqa: E731
    # time arrow: catalysed coverage real / reversed, bootstrap over days
    ag = [e for e in events if e["kind"] != "auto"]
    days = sorted({e["day"] for e in ag})
    per = {d: [0, 0, 0] for d in days}
    for e in ag:
        per[e["day"]][0] += e["n_commits"]
        per[e["day"]][1] += e["n_commits"] * bool(e["cat"])
        per[e["day"]][2] += e["n_commits"] * bool(e["cat_rev"])
    arr = np.array([per[d] for d in days], float)
    ratio = arr[:, 1].sum() / max(arr[:, 2].sum(), 1)
    bs = []
    for _ in range(2000):
        a = arr[rng.integers(0, len(days), len(days))]
        if a[:, 2].sum() > 0:
            bs.append(a[:, 1].sum() / a[:, 2].sum())
    # day bootstrap for coverage (RAF membership fixed at the period level)
    raf_e = set()
    for r in real["_raf"]:
        raf_e.update(real["_R"][r]["eids"])
    cov_d = {d: [0, 0] for d in days}
    for e in ag:
        cov_d[e["day"]][0] += e["n_commits"]
        cov_d[e["day"]][1] += e["n_commits"] * (e["eid"] in raf_e)
    ca = np.array([cov_d[d] for d in days], float)
    cb = []
    for _ in range(2000):
        a = ca[rng.integers(0, len(days), len(days))]
        cb.append(a[:, 1].sum() / a[:, 0].sum())
    out = {"goal_no": goal, "n_days": len(days), "food_size": len(food), "real": strip(real),
           "strict": strip(strict), "reversed": strip(rev),
           "coverage_ci": [float(np.percentile(cb, 2.5)), float(np.percentile(cb, 97.5))],
           "null": {"n3_support3_mean": float(np.mean(nulls["n3_s3"])), "p_n3_support3": p(n3(real["cycles_support3"]), nulls["n3_s3"]),
                    "S3_support3_rate": float(np.mean(nulls["S3_s3"])),
                    "p_low_n3_support3": (1 + sum(x <= n3(real["cycles_support3"]) for x in nulls["n3_s3"])) / (1 + N_NULL),
                    "p_low_n3_any": (1 + sum(x <= n3(real["cycles"]) for x in nulls["n3_any"])) / (1 + N_NULL),
                    "n3_any_mean": float(np.mean(nulls["n3_any"])), "p_n3_any": p(n3(real["cycles"]), nulls["n3_any"]),
                    "coverage_mean": float(np.mean(nulls["coverage"])), "p_coverage": p(real["coverage"], nulls["coverage"]),
                    "inperiod_mean": float(np.mean(nulls["inperiod"])),
                    "p_inperiod": p(real["inperiod_tool_share_work"], nulls["inperiod"])},
           "time_arrow": {"catalysed_real": float(arr[:, 1].sum() / arr[:, 0].sum()),
                          "catalysed_reversed": float(arr[:, 2].sum() / arr[:, 0].sum()), "ratio": float(ratio),
                          "ratio_ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]},
           "n3_support3": n3(real["cycles_support3"]), "n3_any": n3(real["cycles"])}
    # who made the catalysts in cycles (support >= 3): number of distinct first agents
    sp = pl.read_parquet(D / "species.parquet")
    fa = dict(zip(sp["artifact"].to_list(), sp["first_agent"].to_list()))
    G = RL.catalytic_graph(real["_raf"], food, real["_R"], 3)
    comp = [c for c in RL.sccs(G) if len(c) >= 2]
    out["support3_scc"] = [{"size": len(c), "makers": len({fa.get(x) for x in c})} for c in comp]
    return out


def verdict(r: dict) -> dict:
    v = {"P1": r["real"]["coverage"] <= 0.20,
         "P2": (r["real"]["cycles_support3"]["S3"] == 0) or (r["null"]["p_n3_support3"] >= 0.05),
         "P3a": (r["real"]["self_share_of_raf_commits_all"] >= 0.5),
         "P3b": r["real"]["inperiod_tool_share_work"] <= 0.05,
         "P4": r["time_arrow"]["ratio_ci"][0] > 1,
         "P5": r["real"]["caf_over_raf_commits"] >= 0.90}
    return {k: bool(x) for k, x in v.items()}


def natives():
    out = {}
    # G40 vs G41 food-tool share
    g40, g41 = analyse(40), json.loads((RES / "G41.json").read_text())
    out["G40"] = {"result": g40, "verdict": verdict(g40),
                  "N1a": (g40["real"]["cycles_support3"]["S3"] == 0) or (g40["null"]["p_n3_support3"] >= 0.05),
                  "N1b": g40["real"]["inperiod_tool_share_work"] <= 0.05,
                  "N1c": g40["real"]["food_tool_share_work"] > g41["real"]["food_tool_share_work"],
                  "food_tool_G40": g40["real"]["food_tool_share_work"], "food_tool_G41": g41["real"]["food_tool_share_work"]}
    (RES / "G40.json").write_text(json.dumps(g40, indent=1, default=float))
    # NE29: the retiree's repos as catalysts after 2026-02-19
    sp = pl.read_parquet(D / "species.parquet")
    mine = set(sp.filter(pl.col("first_agent") == 0)["artifact"].to_list())
    ev = pl.read_parquet(D / "events.parquet").filter((pl.col("kind") == "agent") & (pl.col("pt_date") > "2026-02-19")
                                                     & (pl.col("agent") != 0))
    rows = []
    for g, d in ev.group_by("goal_no"):
        tot = d["n_commits"].sum()
        hit = d.filter(pl.col("cat").list.eval(pl.element().is_in(list(mine))).list.any())
        hit_x = hit.filter(~pl.col("product").is_in(list(mine)))
        rows.append({"goal_no": int(g[0]), "work_commits": int(tot), "catalysed_by_retiree_repos": int(hit["n_commits"].sum()),
                     "share": float(hit["n_commits"].sum() / tot) if tot else None,
                     "share_other_products": float(hit_x["n_commits"].sum() / tot) if tot else None})
    rows.sort(key=lambda r: r["goal_no"])
    cyc_hits = []
    for gname in REPLICATION + ["G40"]:
        g = int(gname[1:])
        events, food = load(g)
        s = RL.summarize(events, food)
        G = RL.catalytic_graph(s["_raf"], food, s["_R"], 3)
        nodes = {v for c in RL.sccs(G) if len(c) >= 2 for v in c}
        cyc_hits.append({"goal_no": g, "retiree_repos_on_support3_scc": len(nodes & mine)})
    out["NE29"] = {"n_retiree_repos": len(mine), "followup": rows, "cycles": cyc_hits,
                   "N2a": all((r["share"] or 0) <= 0.01 for r in rows),
                   "N2b": all(c["retiree_repos_on_support3_scc"] == 0 for c in cyc_hits),
                   "max_share": max((r["share"] or 0) for r in rows) if rows else None}
    (RES / "natives.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "result"} for k, v in out.items()}, indent=1,
                     default=float))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default=None)
    ap.add_argument("--natives", action="store_true")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    if a.natives:
        natives()
        return
    for pname in ([a.period] if a.period else REPLICATION):
        r = analyse(int(pname[1:]))
        r["verdict"] = verdict(r)
        (RES / f"{pname}.json").write_text(json.dumps(r, indent=1, default=float))
        rr = r["real"]
        print(pname, {k: round(rr[k], 4) if isinstance(rr[k], float) else rr[k] for k in (
            "coverage", "coverage_all_identity", "catalysed_share", "self_share_of_raf_commits_all", "self_share_work",
            "food_tool_share_work", "inperiod_tool_share_work", "caf_over_raf_commits", "n_reactions", "n_raf_reactions")})
        print("   cycles", rr["cycles"]["by_len"], "support3", rr["cycles_support3"]["by_len"], "null", r["null"],
              "arrow", r["time_arrow"], "strict cov", round(r["strict"]["coverage"], 4), r["verdict"])


if __name__ == "__main__":
    main()
