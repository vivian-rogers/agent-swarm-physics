"""H39 round 1b native step tests (predictions dated in the NE folders before running): NE43 (two steps inside #51:
bookends off 08-05, nudger off 08-21) and NE10 (nudger on 02-13) on B4 (minute grid, round-1 step machinery) and on
V4 (Jev v3.1 states, soft 5-min transitions; `v3states.py`), judged against within-goal day boundaries of the same
shape (outside the tested windows).

Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/r1b_native.py
Writes data/processed/H39-catalysts-vs-fields/r1b/steps_native.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2" if _v == "POLARS_MAX_THREADS" else "1"

import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h39lib as L  # noqa: E402
import run_steps as RS  # noqa: E402
import v3states as V3  # noqa: E402


class V4Data:
    def __init__(self, days):
        b = V3.load_v3(days)
        self.seq = {}
        for (d, a), g in b.group_by(["pt_date", "agent"], maintain_order=True):
            if g.height >= 3:
                self.seq.setdefault(d, {})[int(a)] = g.select(V3.V4_NAMES).to_numpy()

    def units(self, pre, post):
        ap = set().union(*[set(self.seq.get(d, {})) for d in pre])
        bp = set().union(*[set(self.seq.get(d, {})) for d in post])
        agents = sorted(ap & bp)
        us = []
        for days in (pre, post):
            Ps, ag, dd, th = [], [], [], []
            for k, d in enumerate(days):
                for a in agents:
                    P = self.seq.get(d, {}).get(a)
                    if P is None:
                        continue
                    Ps.append(P)
                    ag.append(a)
                    dd.append(k)
                    th.append(np.zeros(len(P), np.int8))
            us.append(L.build_soft_unit(Ps, ag, dd, th, 4) if Ps else None)
        return us, agents


def v4_compare(V, pre, post, B):
    us, agents = V.units(pre, post)
    if len(agents) < 3 or us[0] is None or us[1] is None:
        return {"status": "too few agents"}
    r = L.run_step(us[0], us[1], B=B)
    r["status"] = "ok"
    return r


def pct(x, arr):
    arr = np.asarray([a for a in arr if a is not None and np.isfinite(a)])
    return float(np.mean(arr < x) * 100) if len(arr) else None


def judge(r, pl_list, fam, idle_ix):
    j = L.judge_step(r, pl_list)
    j["dpi_idle_pct"] = pct(r["dpi"][idle_ix], [p["dpi"][idle_ix] for p in pl_list])
    j["esc_idle_pct"] = pct(r["esc"][idle_ix], [p["esc"][idle_ix] for p in pl_list])
    j["state_family"] = fam
    return j


def run_step_test(D, V, goal, pre, post, B, exclude, label):
    out = {"label": label, "pre": pre, "post": post}
    rb = RS.compare(D, pre, post, B, content=False)
    out["b4"] = rb.get("b4")
    out["n_agents_b4"] = rb.get("n_agents")
    out["v4"] = v4_compare(V, pre, post, B)
    shape = (len(pre), len(post))
    pb, pv = [], []
    for g, a, b in RS.all_boundaries(D, shape, exclude):
        if g != goal:
            continue
        r = RS.compare(D, a, b, 2, content=False)
        if r.get("status") == "ok":
            pb.append(r["b4"])
        rv = v4_compare(V, a, b, 2)
        if rv.get("status") == "ok":
            pv.append(rv)
    out["n_placebo_b4"], out["n_placebo_v4"] = len(pb), len(pv)
    if out["b4"] and len(pb) >= 5:
        out["judge_b4"] = judge(out["b4"], pb, "B4", 2)
    if out["v4"].get("status") == "ok" and len(pv) >= 5:
        out["judge_v4"] = judge(out["v4"], pv, "V4", 2)
    return out


def main():
    t0 = time.time()
    D = RS.Data()
    days51 = sorted(D.goal_days(51))
    days30 = sorted(D.goal_days(30))
    V = V4Data(days51 + days30)
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    res = {}
    i1, i2 = days51.index("2026-08-05"), days51.index("2026-08-21")
    post2_all = [d for d in days51[i2:] if d < "2026-09-03"]
    for n in (5, 2):
        s1_pre, s1_post = days51[i1 - n:i1], days51[i1:i1 + n]
        s2_pre, s2_post = days51[i2 - n:i2], post2_all[:n]
        excl = set(days51[i1 - n:i1 + n]) | set(days51[i2 - n:i2]) | set(post2_all[:n])
        res[f"NE43_S1_bookends_off_{n}x{n}"] = run_step_test(D, V, 51, s1_pre, s1_post, 300, excl, "bookends off (08-05)")
        res[f"NE43_S2_nudger_off_{n}x{n}"] = run_step_test(D, V, 51, s2_pre, s2_post, 300, excl, "nudger off (08-21)")
        for k in (f"NE43_S1_bookends_off_{n}x{n}", f"NE43_S2_nudger_off_{n}x{n}"):
            r = res[k]
            jb, jv = r.get("judge_b4", {}), r.get("judge_v4", {})
            print(k, "B4", jb.get("cls"), "K", round(r["b4"]["K"], 3) if r.get("b4") else None, "esc_idle_pct", jb.get("esc_idle_pct"),
                  "dpi_idle_pct", jb.get("dpi_idle_pct"), "| V4", jv.get("cls"), "K", round(r["v4"].get("K", np.nan), 3),
                  "esc_wait_pct", jv.get("esc_idle_pct"), "dpi_wait_pct", jv.get("dpi_idle_pct"),
                  "n_pl", r["n_placebo_b4"], r["n_placebo_v4"], f"({time.time() - t0:.0f}s)", flush=True)
    # NE10: 02-11, 02-12 -> 02-13, placebo = same-era (regime I, <= 3 h? use all goals of the era) boundaries of shape 2+1
    i = days30.index("2026-02-13")
    pre, post = days30[i - 2:i], days30[i:i + 1]
    out = {"label": "nudger on (02-13)", "pre": pre, "post": post}
    rb = RS.compare(D, pre, post, 300, content=False)
    out["b4"] = rb.get("b4")
    out["v4"] = v4_compare(V, pre, post, 300)
    era = RS.era_of(str(D.meta[post[0]]["regime"]), D.meta[post[0]]["documented_hours"])
    era_days = [d for d, m in D.meta.items() if RS.era_of(str(m["regime"]), m["documented_hours"]) == era]
    Vp = V4Data(era_days)
    pb, pv = [], []
    for g, a, b in RS.all_boundaries(D, (2, 1), set(days30[i - 3:i + 1])):
        if RS.era_of(str(D.meta[b[0]]["regime"]), D.meta[b[0]]["documented_hours"]) != era:
            continue
        r = RS.compare(D, a, b, 2, content=False)
        if r.get("status") == "ok":
            pb.append(r["b4"])
        rv = v4_compare(Vp, a, b, 2)
        if rv.get("status") == "ok":
            pv.append(rv)
    out["era"], out["n_placebo_b4"], out["n_placebo_v4"] = era, len(pb), len(pv)
    if out["b4"] and len(pb) >= 5:
        out["judge_b4"] = judge(out["b4"], pb, "B4", 2)
    if out["v4"].get("status") == "ok" and len(pv) >= 5:
        out["judge_v4"] = judge(out["v4"], pv, "V4", 2)
    res["NE10"] = out
    print("NE10 B4", out.get("judge_b4", {}).get("cls"), "V4", out.get("judge_v4", {}).get("cls"),
          "V4 dpi", [round(x, 3) for x in out["v4"].get("dpi", [])], "n_pl", len(pb), len(pv), flush=True)
    L.jdump(res, L.OUT / "r1b" / "steps_native.json")
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
