"""H128 synthetic validation (axis F): kinetic Potts quench worlds on the real skeleton of every period and room unit.

Worlds (card): Q0 coarsening (bJ 4), Q0w weak coarsening (bJ 2), Q1 shared field (h_T 6), Q2 per-agent field
(h_Ti 6), Q3 exogenous finish (bJ 0, lifetimes ~ Exp(4 active h)). Synthetic repo labels per real agent-window,
replayed through the shared host code (W 30, E 100) and the same curve code as the real data.

Reports per skeleton x world: class rates (freeze / slow / fast_other) for the primary observable dw (A1) and for N_p
(HH-literal), merge share c_m, power-law selection rate, alpha-hat spread and bootstrap CI width (Q0, Q0w).
Output: data/processed/H128-coarsening-vs-freeze/synthetic/{runs.parquet, summary.json}.

Usage: uv run python hypotheses/H128-coarsening-vs-freeze/analysis/synthetic.py [--runs 60]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h128lib as L  # noqa: E402

WORLDS = ["Q0", "Q0w", "Q1", "Q2", "Q3"]


def room_agents() -> dict:
    """Room units for the natives: #44 by DQ6 room assignment; #37 by the agent's room at its first commit."""
    gt = pl.read_parquet(L.ROOT / "data/processed/shared/ground_truth_labels.parquet").filter(
        (pl.col("label_kind") == "room_assignment") & (pl.col("goal_no") == 44) & pl.col("preferred") & ~pl.col("holdout"))
    out = {"44best": set(gt.filter(pl.col("value") == "best")["agent"].cast(pl.Int64).to_list()),
           "44rest": set(gt.filter(pl.col("value") == "rest")["agent"].cast(pl.Int64).to_list())}
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import rooms_asof as RA
    c = L.RH.load_commits(37, L.RH.period_days(37))
    first = c.group_by("agent").agg(pl.col("t").min()).sort("agent")
    first = RA.room_asof(first, t="t", agent="agent", out="room")
    for room, name in ((2, "37best"), (3, "37rest")):
        out[name] = set(first.filter(pl.col("room") == room)["agent"].cast(pl.Int64).to_list())
    return out


def unit_days(g: int) -> list[str] | None:
    if g == 51:   # 51a: the first 20 active hours (3 days of ~8 h), before NE32
        return L.RH.period_days(51)[:3]
    return None


def skeletons() -> dict:
    out = {}
    for g in L.REPL + [44]:
        out[f"G{g:02d}"] = (g, None, unit_days(g))
    ra = room_agents()
    for k, ag in ra.items():
        out[k] = (int(k[:2]), ag, None)
    return out


def restrict(sk: dict, agents: set | None) -> dict:
    if agents is None:
        return sk
    s = dict(sk)
    for k in ("calls", "commits", "wins"):
        s[k] = sk[k].filter(pl.col("agent").is_in(list(agents)))
    s["leave"] = {a: t for a, t in sk["leave"].items() if a in agents}
    return s


def one_run(sk, world, rng, boot=0):
    lab = L.simulate_labels(sk, world, rng)
    ev = L.synthetic_events(sk, lab)
    cur, de = L.curve_from_events(ev, sk["clock"])
    r = {}
    for col in ("dw", "N_p"):
        s = L.curve_stats(cur, de, col=col, boot=boot if col == "dw" else 0, rng=rng)
        r[col] = s
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=60)
    ap.add_argument("--boot_runs", type=int, default=12)
    a = ap.parse_args()
    out = L.D / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    for name, (g, agents, days) in skeletons().items():
        base = L.skeleton(g) if days is None else skeleton_days(g, days)
        sk = restrict(base, agents)
        for w in WORLDS:
            rng = np.random.default_rng(zlib.crc32(f"{name}|{w}".encode()))
            for i in range(a.runs):
                boot = 200 if (w in ("Q0", "Q0w") and i < a.boot_runs) else 0
                r = one_run(sk, w, rng, boot=boot)
                d, n = r["dw"], r["N_p"]
                rows.append({"skeleton": name, "world": w, "run": i,
                             "dw_class": d.get("class"), "dw_tf": d.get("t_f"), "dw_sel": d.get("selected"),
                             "dw_alpha": d.get("alpha"), "dw_alpha_lo": (d.get("alpha_ci") or [None, None])[0],
                             "dw_alpha_hi": (d.get("alpha_ci") or [None, None])[1], "dw_Au": d.get("A_u"),
                             "testable": d.get("testable"),
                             "np_class": n.get("class"), "np_tf": n.get("t_f"), "np_sel": n.get("selected"),
                             "np_alpha": n.get("alpha"), "c_m": n.get("c_m"), "R_d": n.get("R_d")})
        print(f"{name} done {time.time() - t0:.0f}s", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(out / "runs.parquet")
    summ = summarize(df)
    (out / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ["rule"], indent=1, default=float))


def skeleton_days(g, days):
    sk = L.skeleton(g)
    s = dict(sk)
    for k in ("calls", "commits", "wins"):
        s[k] = sk[k].filter(pl.col("pt_date").is_in(days))
    s["clock"] = L.ActiveClock(days)
    s["days"] = days
    return s


def summarize(df: pl.DataFrame) -> dict:
    res, rule = {}, {}
    for (name,), g in df.group_by(["skeleton"], maintain_order=True):
        r = {}
        for (w,), x in g.group_by(["world"], maintain_order=True):
            n = x.height
            e = {f"{o}_{c}": x.filter(pl.col(f"{o}_class") == c).height / n for o in ("dw", "np")
                 for c in ("freeze", "slow", "fast_other")}
            e["dw_power_sel"] = x.filter(pl.col("dw_sel") == "power").height / n
            e["np_power_sel"] = x.filter(pl.col("np_sel") == "power").height / n
            e["c_m_median"] = x["c_m"].drop_nulls().drop_nans().median()
            al = x["dw_alpha"].drop_nulls()
            e["dw_alpha_median"] = al.median()
            e["dw_alpha_sd"] = al.std()
            ci = x.filter(pl.col("dw_alpha_lo").is_not_null())
            e["dw_alpha_ci_width_median"] = (ci["dw_alpha_hi"] - ci["dw_alpha_lo"]).median() if ci.height else None
            e["np_alpha_median"] = x["np_alpha"].drop_nulls().median()
            e["testable"] = x["testable"].mean()
            r[w] = e
        res[name] = r
        ok_a = (r["Q0"]["dw_slow"] + r["Q0"]["dw_fast_other"]) >= 0.7
        ok_b = r["Q1"]["dw_freeze"] >= 0.8 and r["Q2"]["dw_freeze"] >= 0.8
        ok_c = (r["Q3"]["c_m_median"] or 0) <= 0.2 and r["Q3"]["dw_freeze"] >= 0.8
        alpha_id = (r["Q0"]["dw_alpha_sd"] or 9) <= 0.2 and (r["Q0"]["dw_alpha_ci_width_median"] or 9) <= 0.6
        ok_np_b = r["Q1"]["np_freeze"] >= 0.8 and r["Q2"]["np_freeze"] >= 0.8
        rule[name] = {"a_Q0_not_freeze": ok_a, "b_fields_freeze": ok_b, "c_finish_not_coarsening": ok_c,
                      "valid": bool(ok_a and ok_b and ok_c), "alpha_identified": bool(alpha_id),
                      "N_p_rule_b": bool(ok_np_b)}
    return {"by_skeleton": res, "rule": rule}


if __name__ == "__main__":
    main()
