"""H136 synthetic validation (axis F) on real kickoff skeletons. No real freeze time is read.

Skeleton per unit: t_k, each reader's real kickoff read-out call t_r,i, real own non-summary call times after t_k
(DQ1 call_windows, reserved rows dropped), first call of the kickoff day, the delayed-active-reader flag
(scheme/structure.py). Planted freeze call per world (500 runs each):
  W0 no coupling : a uniformly drawn own call in the first 240 active min after t_k (no field, no read).
  W1 read-locked : the K-th own call after t_r (K = 0 is the read call), K ~ Geometric(0.5) - 1.
  W2 clock       : the first own call at or after max(t_k + D, t_r), D ~ log-normal(median 20 active min, log-SD 0.8).
  W3 late starter: the first own call at or after (first call of the day + D), same D; reads unrelated.
W4 (copy) is not run: it needs peer-link reads of the named target, which the precondition stop does not open.

Tests per run, on two samples: (a) the card's sample, delayed active readers (O1/O3 need >= 3 points; fewer counts
as "no decision"); (b) all kickoff readers of the unit (descriptive widening, not the card's test).
  O1: Theil-Sen slope b of D_f on D_r (95% CI, scipy). "Read-lock call": CI contains 1 and excludes 0.
  O3: Spearman rho(K, D_r); 95% CI by Fisher z. "Clock call": CI upper < 0.
  O4: median absolute deviation (own calls) of the freeze from each anchor (kickoff read, first call of the day,
      kickoff post); the winner is the strictly smallest; ties are reported as ties.
Power = P(read-lock call | W1); size = P(read-lock call | W2); for O3, power = P(clock call | W2), size = P(clock call | W1).

  uv run python hypotheses/H136-freeze-at-first-kickoff-read/analysis/synthetic.py
Writes data/processed/H136-.../synthetic/synthetic.json.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h136lib as L  # noqa: E402
from common import git_commit  # noqa: E402

UNITS = ["G39", "G40", "G42", "G44best", "G26"]     # card: G39, G40, G42, G44 #best and one regime-I kickoff
NRUN = 500
SEED = 20261007
W0_SPAN = 240.0


def skeleton(unit: str, readers: pl.DataFrame, clk: L.Clock) -> list[dict]:
    r = readers.filter(pl.col("unit") == unit).sort("agent")
    t_k = r["t_k"][0]
    goal = {n: g for n, g, _ in L.UNITS}[unit]
    cal = L.calendar()
    days = cal.filter(pl.col("goal_no") == goal).sort("pt_date")["pt_date"].to_list()[:2]
    cw = L.calls(days)
    ak = float(clk([L.us(t_k)])[0])
    out = []
    for row in r.iter_rows(named=True):
        c = cw.filter((pl.col("agent") == row["agent"]) & (pl.col("t_call") >= row["t_r"]))
        tc = c["t_call"].dt.epoch("us").to_numpy()
        a = clk(tc) - ak
        fc = row["first_call_day"]
        afc = float(clk([L.us(fc)])[0] - ak) if fc is not None else 0.0
        out.append(dict(agent=row["agent"], D_r=row["D_r_min"], a_calls=a, a_first=afc,
                        dar=bool(row["delayed_active_reader"])))
    return out


def plant(sk: list[dict], world: str, rng) -> list[tuple[float, int, int, int]]:
    """Per reader: (D_f, K calls after read, calls after first-of-day, calls after kickoff post)."""
    res = []
    for s in sk:
        a = s["a_calls"]                       # active min after t_k of own calls from the read call on (a[0] = read)
        if len(a) == 0:
            res.append(None)
            continue
        if world == "W0":
            # calls before the read are not in the skeleton; W0 draws among calls from the read on within the span
            ok = np.flatnonzero(a <= W0_SPAN)
            j = int(rng.choice(ok)) if len(ok) else 0
        elif world == "W1":
            j = min(int(rng.geometric(0.5)) - 1, len(a) - 1)
        elif world == "W2":
            D = math.exp(math.log(20.0) + 0.8 * rng.standard_normal())
            j = int(np.searchsorted(a, max(D, s["D_r"]), side="left"))
            j = min(j, len(a) - 1)
        elif world == "W3":
            D = math.exp(math.log(20.0) + 0.8 * rng.standard_normal())
            j = int(np.searchsorted(a, s["a_first"] + D, side="left"))
            j = min(j, len(a) - 1)
        else:
            raise ValueError(world)
        # own calls between anchors: the read is call 0 of the skeleton; the first call of the day and the kickoff
        # post precede or equal it, so their counts differ from K only by calls before the read (0 for all readers
        # in the real skeletons except where read_is_first_call is false: counted by n_pre)
        res.append((float(a[j]), j, j + s.get("n_pre_day", 0), j + s.get("n_pre_post", 0)))
    return res


def theil(x, y):
    if len(x) < 3 or np.ptp(x) == 0:
        return None
    b, a, lo, hi = stats.theilslopes(y, x, alpha=0.95)
    return float(b), float(lo), float(hi)


def spearman_ci(x, y):
    n = len(x)
    if n < 4 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return None
    rho = stats.spearmanr(x, y).statistic
    if not np.isfinite(rho):
        return None
    z = np.arctanh(np.clip(rho, -0.9999, 0.9999))
    se = 1.06 / math.sqrt(n - 3) if n > 3 else float("inf")
    return float(rho), float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se))


def mad(v):
    v = np.asarray(v, float)
    return float(np.median(np.abs(v - np.median(v)))) if len(v) else float("nan")


def run_unit(sk, rng) -> dict:
    out = {}
    for world in ("W0", "W1", "W2", "W3"):
        acc = {s: {"o1_lock": 0, "o1_nodec": 0, "o3_clock": 0, "o3_nodec": 0, "b": [], "rho": []} for s in ("dar", "all")}
        o4 = {"read": 0, "day": 0, "post": 0, "tie": 0}
        for _ in range(NRUN):
            pl_ = plant(sk, world, rng)
            for samp in ("dar", "all"):
                idx = [i for i, s in enumerate(sk) if pl_[i] is not None and (samp == "all" or s["dar"])]
                Dr = np.array([sk[i]["D_r"] for i in idx])
                Df = np.array([pl_[i][0] for i in idx])
                K = np.array([pl_[i][1] for i in idx])
                t = theil(Dr, Df)
                A = acc[samp]
                if t is None:
                    A["o1_nodec"] += 1
                else:
                    A["b"].append(t[0])
                    A["o1_lock"] += int(t[1] <= 1 <= t[2] and not (t[1] <= 0 <= t[2]))
                s3 = spearman_ci(Dr, K)
                if s3 is None:
                    A["o3_nodec"] += 1
                else:
                    A["rho"].append(s3[0])
                    A["o3_clock"] += int(s3[2] < 0)
            v = [p for p in pl_ if p is not None]
            m = {"read": mad([p[1] for p in v]), "day": mad([p[2] for p in v]), "post": mad([p[3] for p in v])}
            best = min(m.values())
            win = [k for k, x in m.items() if x == best]
            o4[win[0] if len(win) == 1 else "tie"] += 1
        res = {}
        for samp, A in acc.items():
            res[samp] = {"n": int(sum(1 for s in sk if (samp == "all" or s["dar"]))),
                         "p_o1_readlock_call": A["o1_lock"] / NRUN, "p_o1_no_decision": A["o1_nodec"] / NRUN,
                         "p_o3_clock_call": A["o3_clock"] / NRUN, "p_o3_no_decision": A["o3_nodec"] / NRUN,
                         "b_median": float(np.median(A["b"])) if A["b"] else None,
                         "b_q05_q95": [float(np.quantile(A["b"], 0.05)), float(np.quantile(A["b"], 0.95))] if A["b"] else None,
                         "rho_median": float(np.median(A["rho"])) if A["rho"] else None}
        res["o4_winner_share"] = {k: v / NRUN for k, v in o4.items()}
        out[world] = res
    return out


def main():
    readers = pl.read_parquet(L.OUTD / "structure/readers.parquet")
    clk = L.Clock()
    rng = np.random.default_rng(SEED)
    res = {"built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "git_commit": git_commit(), "n_run": NRUN,
           "seed": SEED, "units": {}}
    for u in UNITS:
        sk = skeleton(u, readers, clk)
        r = readers.filter(pl.col("unit") == u).sort("agent")
        # calls before the read on the kickoff day (first call of the day not the read) for O4's anchors
        for s, rif in zip(sk, r["read_is_first_call"].to_list()):
            s["n_pre_day"] = 0 if rif else 1
            s["n_pre_post"] = 0
        U = run_unit(sk, rng)
        W1, W2 = U["W1"], U["W2"]
        for samp in ("dar", "all"):
            U[f"pass_rule_{samp}"] = {"o1_power_W1": W1[samp]["p_o1_readlock_call"], "o1_size_W2": W2[samp]["p_o1_readlock_call"],
                                      "o3_power_W2": W2[samp]["p_o3_clock_call"], "o3_size_W1": W1[samp]["p_o3_clock_call"],
                                      "passes": (W1[samp]["p_o1_readlock_call"] >= 0.8 and W2[samp]["p_o1_readlock_call"] <= 0.10)}
        U["D_r_all"] = sorted(round(s["D_r"], 2) for s in sk)
        res["units"][u] = U
        print(u, {s: U[f"pass_rule_{s}"] for s in ("dar", "all")})
    out = L.OUTD / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    (out / "synthetic.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
