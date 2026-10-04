"""H112 synthetic validation on real call skeletons (axis F; run before any real departure statistic).

Each world replays a period's real non-holdout call schedule (call_windows t_call per agent; one room) with synthetic
project choices from the H112 model (card, "Model"):
  - at each call an agent updates with prob p_u, plus p_r if it read news (a claim) at this call (read-out-triggered
    update, H50's hop-1 response);
  - an update draws a project from softmax(h_j + J * n_hat_j), n_hat_j = the number of other agents it BELIEVES are on j
    (beliefs change only when a claim is read at a call whose t_call is after the claim's post time);
  - a switch posts a claim with prob p_c (latency 5-30 s), read by every other agent at its first later call;
  - at each call the agent touches its current project with prob p_t (touches are what the pipeline sees);
  - W3/W4: a common project field: projects die at rate lam (per active hour) for 60 min; hosts of a dead project
    re-choose at their next call (a shared end of interest, no coupling).
Calibration (skeleton rates only, no departure statistic): p_u = real switch-ins per call; p_t = real touches per call;
p_c = share of real switch-ins with an own claim naming the project within +-15 min; h_j = log popularity of the top
projects by touches.
The synthetic frames run through the same scheme code (h112scheme.build_from_frames) and statistics (h112lib).

Usage: uv run python hypotheses/H112-crossing-claims-two-cycles/analysis/synthetic.py [--runs 30] [--period 38 ...]
Output: data/processed/H112-crossing-claims-two-cycles/synthetic/{runs.parquet, summary.json}
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h112lib as L  # noqa: E402
import h112scheme as S  # noqa: E402

OUT = S.ROOT / "data/processed/H112-crossing-claims-two-cycles/synthetic"
WORLDS = {"W0": dict(J=0.0, field=False), "W1": dict(J=-2.0, field=False), "W2": dict(J=2.0, field=False),
          "W3": dict(J=0.0, field=True), "W4": dict(J=-2.0, field=True),
          # W5/W6 (added in A1, before real data): agents also learn a project's current hosts when they touch it
          # (the artifact shows who works there), so unaware co-switchers discover each other after the move: the
          # HH343 world (a Little 2-cycle for J < 0). W6 is its J = 0 size check.
          "W5": dict(J=-2.0, field=False, aware=True), "W6": dict(J=0.0, field=False, aware=True)}
SKELETONS = {18: None, 31: None, 38: None, 51: ["2026-07-10", "2026-07-11", "2026-07-13", "2026-07-14", "2026-07-15",
                                                  "2026-07-16", "2026-07-17", "2026-07-20", "2026-07-21", "2026-07-22",
                                                  "2026-07-23"]}
P_R = 0.3
POOL: dict = {}
M_MAX = 40
LAM_DEATH_PER_H = 0.5


def calibrate(g: int, days: list[str]) -> dict:
    touches = S.load_touches(g, days); calls = S.load_calls_period(g, days); claims = S.load_claims(g, days)
    sw = S.switch_ins(touches)
    c = claims.select("agent", "project", pl.col("t").alias("tc"))
    j = sw.join(c, on=["agent", "project"], how="inner").filter(((pl.col("tc") - pl.col("t")).dt.total_seconds().abs() <= 900))
    p_c = j["sid"].n_unique() / max(len(sw), 1)
    pop = touches.group_by("project").len().sort("len", descending=True)
    pop = pop.head(M_MAX)
    return {"calls": calls, "p_u": len(sw) / max(len(calls), 1), "p_t": min(0.9, len(touches) / max(len(calls), 1)),
            "p_c": p_c, "h": np.log(pop["len"].to_numpy().astype(float)), "n_proj": len(pop)}


def simulate(cal: dict, J: float, field: bool, seed: int, aware: bool = False):
    rng = np.random.default_rng(seed)
    calls = cal["calls"]; h = cal["h"] - cal["h"].max(); M = len(h)
    p_u, p_t, p_c = cal["p_u"], cal["p_t"], cal["p_c"]
    T, C, R = [], [], []  # touches (agent, t_us, day, proj); claims (mid, t_us, day, agent, proj); receipts (mid, rcv, t_us)
    mid = 0
    for (day,), g in calls.group_by(["pt_date"], maintain_order=True):
        g = g.sort("t_call", "agent")
        ag = g["agent"].to_numpy(); tc = g["t_call"].dt.epoch("us").to_numpy()
        agents = np.unique(ag)
        proj = {int(a): int(rng.choice(M, p=np.exp(h) / np.exp(h).sum())) for a in agents}
        belief = {int(a): {} for a in agents}
        inbox = {int(a): [] for a in agents}
        dead_until = np.zeros(M, np.int64)
        next_death = tc[0] + int(rng.exponential(3600 / LAM_DEATH_PER_H) * 1e6) if field else None
        for a, t in zip(ag.tolist(), tc.tolist()):
            if field and t >= next_death:
                k = int(rng.integers(M)); dead_until[k] = t + 3600 * 1_000_000
                next_death = t + int(rng.exponential(3600 / LAM_DEATH_PER_H) * 1e6)
            news = False
            box = inbox[a]
            if box:
                keep = []
                for item in box:
                    if item[0] < t:
                        belief[a][item[1]] = item[2]; news = True
                        if item[3] is not None:
                            R.append((item[3], a, t))
                    else:
                        keep.append(item)
                inbox[a] = keep
            forced = field and dead_until[proj[a]] > t
            pu = p_u + (P_R if news else 0.0)
            if forced or rng.random() < pu:
                nh = np.zeros(M)
                for b, pj in belief[a].items():
                    if b != a:
                        nh[pj] += 1
                u = h + J * nh
                if field:
                    u = np.where(dead_until > t, -np.inf, u)
                p = np.exp(u - u.max()); p /= p.sum()
                new = int(rng.choice(M, p=p))
                if new != proj[a]:
                    proj[a] = new
                    T.append((a, t + 2_000_000, day, new))
                    if rng.random() < p_c:
                        tp = t + int(rng.uniform(5, 30) * 1e6)
                        C.append((f"m{mid}", tp, day, a, new))
                        for b in agents:
                            if int(b) != a:
                                inbox[int(b)].append((tp, a, new, f"m{mid}"))
                        mid += 1
            if rng.random() < p_t:
                T.append((a, t + 3_000_000, day, proj[a]))
                if aware:  # the touched artifact reveals its other current hosts (read at the next call)
                    for b in agents:
                        b = int(b)
                        if b != a and proj[b] == proj[a] and belief[a].get(b) != proj[a]:
                            inbox[a].append((t + 3_000_000, b, proj[a], None))
    def frame(rows, cols, tcols):
        df = pl.DataFrame(rows, schema=cols, orient="row")
        for c in tcols:
            df = df.with_columns(pl.from_epoch(pl.col(c), time_unit="us").dt.replace_time_zone("UTC"))
        return df
    touches = frame(T, ["agent", "t", "pt_date", "project"], ["t"]).with_columns(pl.col("project").cast(pl.String)) \
        .sort("agent", "t")
    claims = frame(C, ["message_id", "t", "pt_date", "agent", "project"], ["t"]).with_columns(pl.col("project").cast(pl.String))
    rec = frame(R, ["message_id", "recipient", "t_recv"], ["t_recv"])
    return touches, claims, rec


def run_one(cal, g, world, seed):
    w = WORLDS[world]
    touches, claims, rec = simulate(cal, w["J"], w["field"], seed, w.get("aware", False))
    r = S.build_from_frames(touches, claims, rec, cal["calls"])
    pf = L.pair_frame(r["pairs"], unit=f"G{g}")
    c = L.contrasts(pf, n_perm=0) if len(pf) else {"n_pairs": 0}
    POOL.setdefault((world, seed % 1000), []).append(pf)
    solo = r["solo"].with_columns(pl.lit(f"G{g}").alias("unit"), pl.lit(False).alias("named")) if len(r["solo"]) else r["solo"]
    st_r = L.stick_ratio(pf.with_columns(pl.lit(False).alias("named")), solo) if len(pf) else {}
    # claimed-only variant: pairs where the partner posted a claim (read vs in flight among claimed)
    row = {"period": g, "world": world, "seed": seed, "n_pairs": c.get("n_pairs", 0),
           "n_read": c.get("n_read", 0), "n_silent": c.get("n_silent", 0), "n_inflight": c.get("n_inflight", 0),
           "p_any_read": c.get("p_any_read"), "p_any_silent": c.get("p_any_silent"), "p_any_inflight": c.get("p_any_inflight")}
    for k in ("rr_u", "rr_f"):
        d = c.get(k, {})
        row.update({f"{k}": d.get("rr"), f"{k}_lo": d.get("lo"), f"{k}_hi": d.get("hi")})
    row.update({"stick": st_r.get("rr"), "stick_lo": st_r.get("lo"), "stick_hi": st_r.get("hi")})
    for k in ("M_unaware", "M_read"):
        d = c.get(k, {})
        row.update({k: d.get("M"), f"{k}_lo": d.get("lo"), f"{k}_hi": d.get("hi")})
    return row


def summarize(df: pl.DataFrame) -> dict:
    out = {}
    for (g, w), d in df.group_by(["period", "world"], maintain_order=True):
        def frac(col_lo, col_hi, side):
            lo = d[col_lo].fill_nan(None).drop_nulls(); hi = d[col_hi].fill_nan(None).drop_nulls()
            if len(lo) == 0:
                return None
            lo_c = d[col_lo].fill_nan(None); hi_c = d[col_hi].fill_nan(None)  # polars ranks NaN above numbers (H63)
            return float(((lo_c > 1) if side == "gt" else (hi_c < 1)).fill_null(False).mean())
        out[f"G{g}|{w}"] = {
            "n_pairs_med": float(d["n_pairs"].median()), "n_inflight_med": float(d["n_inflight"].median()),
            "rr_u_med": float(d["rr_u"].fill_nan(None).median() or float("nan")),
            "rr_u_ci_gt1": frac("rr_u_lo", "rr_u_hi", "gt"), "rr_u_ci_lt1": frac("rr_u_lo", "rr_u_hi", "lt"),
            "rr_f_med": float(d["rr_f"].fill_nan(None).median() or float("nan")) if d["rr_f"].fill_nan(None).drop_nulls().len() else None,
            "rr_f_ci_gt1": frac("rr_f_lo", "rr_f_hi", "gt"), "rr_f_ci_lt1": frac("rr_f_lo", "rr_f_hi", "lt"),
            "p_any_read_med": float(d["p_any_read"].fill_nan(None).median() or float("nan")),
            "p_any_silent_med": float(d["p_any_silent"].fill_nan(None).median() or float("nan")),
            "p_any_inflight_med": float(d["p_any_inflight"].fill_nan(None).median() or float("nan")) if d["p_any_inflight"].fill_nan(None).drop_nulls().len() else None,
            "M_unaware_med": float(d["M_unaware"].fill_nan(None).median() or float("nan")),
            "stick_med": float(d["stick"].fill_nan(None).median() or float("nan")),
            "stick_ci_lt1": frac("stick_lo", "stick_hi", "lt"), "stick_ci_gt1": frac("stick_lo", "stick_hi", "gt"),
            "M_read_med": float(d["M_read"].fill_nan(None).median() or float("nan")),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--worlds", default=",".join(WORLDS))
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for g in (a.period or list(SKELETONS)):
        days = SKELETONS.get(g) or S.period_days(g)
        days = [d for d in days if d in S.period_days(g)]  # never a held-out day
        cal = calibrate(g, days)
        print(f"G{g}: calls {len(cal['calls'])} p_u {cal['p_u']:.4f} p_t {cal['p_t']:.3f} p_c {cal['p_c']:.3f} "
              f"projects {cal['n_proj']}", flush=True)
        for w in a.worlds.split(","):
            t0 = time.time()
            for s in range(a.runs):
                rows.append(run_one(cal, g, w, 1000 * g + s))
            print(f"  {w}: {a.runs} runs {time.time() - t0:.0f}s", flush=True)
        pl.DataFrame(rows).write_parquet(OUT / "runs.parquet")
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / "runs.parquet")
    summ = summarize(df)
    # pooled over skeletons (MH with period strata), per world and seed index
    prow = []
    for (w, s_), pfs in POOL.items():
        pfs = [x for x in pfs if len(x)]
        if not pfs:
            continue
        pf = pl.concat(pfs, how="diagonal_relaxed")
        st = L.strata_of(pf)
        r = L.mh_rr(pf["any"].to_numpy(), pf["unaware"].to_numpy(), st)
        row = {"world": w, "seed": s_, "rr": r["rr"], "lo": r["lo"], "hi": r["hi"]}
        if w == "W0":  # planted RR = 2 on the W0 frames: unaware outcomes redrawn at min(1, 2 x the stratum's read rate)
            rng = np.random.default_rng(s_)
            y = pf["any"].to_numpy().astype(float); u = pf["unaware"].to_numpy()
            y2 = y.copy()
            for stv in np.unique(st):
                m = st == stv
                pr = y[m & ~u].mean() if (m & ~u).sum() else y[m].mean()
                y2[m & ~u] = rng.random((m & ~u).sum()) < pr
                y2[m & u] = rng.random((m & u).sum()) < min(1.0, 2 * pr)
            r2 = L.mh_rr(y2, u, st)
            row.update({"planted_rr": r2["rr"], "planted_lo": r2["lo"], "planted_hi": r2["hi"]})
        prow.append(row)
    pdf = pl.DataFrame(prow).with_columns(pl.col(pl.Float64).fill_nan(None))
    pdf.write_parquet(OUT / "pooled.parquet")
    for (w,), d in pdf.group_by(["world"], maintain_order=True):
        summ[f"pooled|{w}"] = {"rr_u_med": float(d["rr"].median()), "rr_u_ci_gt1": float((d["lo"] > 1).fill_null(False).mean()),
                               "rr_u_ci_lt1": float((d["hi"] < 1).fill_null(False).mean()),
                               "rr_u_ge2_ci_gt1": float(((d["rr"] >= 2) & (d["lo"] > 1)).fill_null(False).mean())}
        if w == "W0" and "planted_rr" in d.columns:
            summ["pooled|W0"].update({"planted_rr2_med": float(d["planted_rr"].median()),
                                      "planted_rr2_power_ci_gt1": float((d["planted_lo"] > 1).fill_null(False).mean())})
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1))
    for k, v in summ.items():
        print(k, json.dumps({kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()}))


if __name__ == "__main__":
    main()
