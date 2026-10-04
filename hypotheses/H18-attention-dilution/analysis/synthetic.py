"""H18 synthetic validation (axis F), run before any real-data fit.

  uv run python hypotheses/H18-attention-dilution/analysis/synthetic.py A   # known rules on real village skeletons
  uv run python hypotheses/H18-attention-dilution/analysis/synthetic.py B   # generative agents: timing, rooms, boundary

A. Village sampling: the real talk turns, pending sets (who, when, rank, mentions-of-i flags) and agent-days of a
   non-holdout period, with *synthetic* responses drawn from a known rule (const, inv, sat k0=3, rec rho=0.5, pow 0.5),
   agent x day propensities log theta ~ N(mu, 0.7^2), mention factor 4, mean addressing rate ~0.15. Recovery of beta
   (M_pow) and selection by within-day-block held-out likelihood. Real responses are never read.
B. Generative agents (regime-III-like: 13 agents, two rooms 3 + 10 or one room of 13, 4 h days, model calls with 4-12 s
   latency, timer pauses, spontaneous talk), with an optional reactive mechanism (a newly seen message "demands" a reply
   at once: endogenous timing). Scenarios: exogenous budget / constant, reactive constant (the strongest null), reactive
   budget, room-blind k, and the naive window boundary (talk times instead of call starts). Output through the same
   scheme.build.assemble() as real data, then the D1 and D2 fits.

Outputs: data/processed/H18-attention-dilution/synthetic/{A,B}.parquet, figures/synthetic.pdf (via figures.py).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import heapq
import math
import sys
import time
from bisect import bisect_left
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
from h18lib import Units, cv, fit  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H18-attention-dilution"
OUTD = DATA / "synthetic"

RULES_A = {"const": ("const", None), "inv": ("inv", None), "sat3": ("sat", 3.0), "rec0.5": ("rec", 0.5),
           "pow0.5": ("pow", 0.5)}
CV_MODELS = ["const", "inv", "sat", "rec"]


# ------------------------------------------------------------------------------------------------ A
def true_shape(rule, par, U: Units, gamma):
    w = U.n0 + math.exp(gamma) * U.nM
    if rule == "const":
        return w
    if rule == "inv":
        return w / U.k
    if rule == "sat":
        return w * (1 + par) / (par + U.k)
    if rule == "pow":
        return w * U.k ** (-par)
    if rule == "rec":
        mw = par ** (U.m_rank - 1.0) * np.where(U.m_ment > 0, math.exp(gamma), 1.0)
        return np.bincount(U.m_uid, weights=mw, minlength=U.n)
    raise ValueError(rule)


def synth_responses(U: Units, rule, par, rng, base=0.15, gamma=math.log(4), sd=0.7):
    S = true_shape(rule, par, U, gamma)
    z = rng.normal(0, sd, size=int(U.c.max()) + 1)
    # choose mu so that the mean addressing probability ~ base
    lo, hi = -15.0, 10.0
    for _ in range(50):
        mu = 0.5 * (lo + hi)
        p = -np.expm1(-np.exp(mu + z[U.c]) * S)
        lo, hi = (mu, hi) if p.mean() < base else (lo, mu)
    return (rng.random(U.n) < p).astype(float)


def run_A(periods=("G38", "G41", "G25", "G51"), reps=8, cv_reps=4, seed=7):
    rng = np.random.default_rng(seed)
    rows = []
    for gp in periods:
        d = DATA / gp
        talks = pl.read_parquet(d / "talks.parquet")
        pend = pl.read_parquet(d / "pending.parquet").drop("resp").with_columns(pl.lit(False).alias("resp"))
        U = Units(talks, pend, "talk_id")
        if gp == "G51":   # subsample days for speed (village sampling still real)
            keep = np.isin(U.day, rng.choice(len(U.days), size=min(12, len(U.days)), replace=False))
            U = U.subset(keep)
        print(gp, "units", U.n, "median k", float(np.median(U.k)), flush=True)
        for name, (rule, par) in RULES_A.items():
            for rep in range(reps):
                t0 = time.time()
                U.r = synth_responses(U, rule, par, rng)
                fp = fit("pow", U)
                row = dict(period=gp, rule=name, rep=rep, n=U.n, beta=fp["params"]["beta"],
                           gamma=fp["params"]["g"], rate=float(U.r.mean()))
                if rep < cv_reps:
                    ll = cv(CV_MODELS, U, "block")
                    tot = {m: float(np.nanmean(v)) for m, v in ll.items()}
                    row.update({f"cv_{m}": v for m, v in tot.items()})
                    row["cv_best"] = max(tot, key=tot.get)
                rows.append(row)
                print(f"  {gp} {name} rep{rep} beta={row['beta']:.2f} best={row.get('cv_best', '-')} "
                      f"rate={row['rate']:.3f} {time.time() - t0:.1f}s", flush=True)
    OUTD.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(rows)
    df.write_parquet(OUTD / "A.parquet")
    return df


# ------------------------------------------------------------------------------------------------ B
PAUSE_CHOICES = np.array([60, 120, 180, 300, 600], dtype=float)


def simulate(rule="inv", reactive=False, rooms=(3, 10), days=10, day_s=4 * 3600, q_s=0.012, q_pause=0.004,
             q_r=0.04, base_theta=0.35, gamma=math.log(4), sd=0.5, k0=3.0, rho=0.5, seed=0):
    """Event-driven simulation; returns the assemble() input dict plus a room-blind exposure."""
    rng = np.random.default_rng(seed)
    N = sum(rooms)
    room_of = np.concatenate([[r] * n for r, n in enumerate(rooms)])
    msgs_t, msgs_sender, msgs_room, msgs_ment, msgs_day = [], [], [], [], []
    room_msgs = {r: [] for r in range(len(rooms))}       # (t, msg_index) sorted by t
    room_times = {r: [] for r in range(len(rooms))}
    turns = {a: [] for a in range(N)}
    pauses = {a: ([], [], []) for a in range(N)}
    day_names = [f"2099-01-{i + 1:02d}" for i in range(days)]
    win = {}
    for di, dname in enumerate(day_names):
        t_day0 = di * 86400.0
        win[dname] = (int(t_day0 * 1e6), int((t_day0 + day_s) * 1e6))
        theta = {a: base_theta * math.exp(sd * rng.normal()) for a in range(N)}
        heap = []
        st = {}
        for a in range(N):
            t0 = t_day0 + rng.uniform(0, 30)
            st[a] = dict(prev_start=t0, last_talk_start=None, n_calls=0)
            heapq.heappush(heap, (t0, 1, a))      # 1 = call start
        while heap:
            t, typ, a = heapq.heappop(heap)
            if t > t_day0 + day_s:
                continue
            if typ == 0:   # post event (message or turn log) handled at push time
                continue
            S = st[a]
            r = room_of[a]
            lat = rng.uniform(4, 12)
            tend = t + lat
            times = room_times[r]
            lo_v = bisect_left(times, S["prev_start"])
            hi = bisect_left(times, t)
            V = [room_msgs[r][q][1] for q in range(lo_v, hi) if msgs_sender[room_msgs[r][q][1]] != a]
            talk, addressed = False, set()
            if S["last_talk_start"] is not None:
                lo_p = bisect_left(times, S["last_talk_start"])
                P = [room_msgs[r][q][1] for q in range(lo_p, hi) if msgs_sender[room_msgs[r][q][1]] != a]
            else:
                P = []
            k = len(P)
            if reactive and V:
                for m in V:
                    qq = q_r if rule == "const" else min(1.0, q_r * 4.0 / max(k, 1))
                    if rng.random() < qq:
                        talk = True
                        addressed.add(msgs_sender[m])
            if not talk and rng.random() < q_s:
                talk = True
            if talk and k:
                for idx_m, m in enumerate(P):
                    rank = k - idx_m
                    if rule == "const":
                        h = 1.0
                    elif rule == "inv":
                        h = 1.0 / k
                    elif rule == "sat":
                        h = (1 + k0) / (k0 + k)
                    elif rule == "rec":
                        h = rho ** (rank - 1)
                    else:
                        raise ValueError(rule)
                    if a in msgs_ment[m]:
                        h *= math.exp(gamma)
                    if rng.random() < -math.expm1(-theta[a] * h * (0.25 if reactive else 1.0)):
                        addressed.add(msgs_sender[m])
            if talk:
                mi = len(msgs_t)
                msgs_t.append(tend)
                msgs_sender.append(a)
                msgs_room.append(r)
                msgs_ment.append(addressed)
                msgs_day.append(dname)
                room_msgs[r].append((tend, mi))
                room_times[r].append(tend)
                S["last_talk_start"] = t
                turns[a].append(tend)
                S["prev_start"] = t
                heapq.heappush(heap, (tend, 1, a))
            elif rng.random() < q_pause:
                dur = float(rng.choice(PAUSE_CHOICES))
                turns[a].append(tend)
                pauses[a][0].append(tend)
                pauses[a][1].append(dur)
                pauses[a][2].append(dname)
                S["prev_start"] = t
                heapq.heappush(heap, (tend + dur, 1, a))   # the wake call starts at expiry
            else:
                turns[a].append(tend)
                S["prev_start"] = t
                heapq.heappush(heap, (tend, 1, a))
        # room message lists are per day; keep growing (times are absolute)
    # build assemble() input
    order = np.argsort(msgs_t, kind="stable")
    m_t = (np.array(msgs_t)[order] * 1e6).astype(np.int64)
    sender = np.array(msgs_sender, dtype=np.int16)[order]
    room = np.array(msgs_room)[order]
    ment = [msgs_ment[i] for i in order]
    dayv = np.array(msgs_day)[order]
    msgs = dict(t=m_t, msg=np.arange(len(m_t)), kind=np.zeros(len(m_t), dtype=np.int8), sender=sender, day=dayv, ment=ment)
    expo, expo_blind = {}, {}
    for a in range(N):
        expo[a] = np.where((room == room_of[a]) & (sender != a))[0]
        expo_blind[a] = np.where(sender != a)[0]
    tdict = {a: np.sort((np.array(turns[a]) * 1e6).astype(np.int64)) for a in range(N)}
    pz = {a: ((np.array(pauses[a][0]) * 1e6).astype(np.int64), np.array(pauses[a][1]), np.array(pauses[a][2]))
          for a in range(N) if pauses[a][0]}
    inp = dict(days=day_names, win=win, msgs=msgs, expo=expo, turns=tdict, pauses=pz,
               room_at=lambda b, tt: np.full(len(tt), room_of[b], dtype=np.int16),
               on_roster={d: list(range(N)) for d in day_names}, detectable=set(range(N)), cc=set(), goal=0)
    return inp, expo_blind


def d2_units(res, window_s=60.0, kcol="k"):
    """D2 units with the response window: first talk within window_s of the wake (None = whole stint).
    kcol: 'k' = batch size; 'k_pend' = whole unanswered backlog at the wake call (units are still batch messages)."""
    w = res["wakes"]
    if kcol != "k":
        w = w.with_columns(pl.col(kcol).alias("k"))
    wp = res["wake_pending"]
    if window_s is not None:
        ok = w.filter(pl.col("talked") & (pl.col("delay_s") <= window_s)).select("wake_id")
        wp = wp.with_columns((pl.col("resp") & pl.col("wake_id").is_in(ok["wake_id"].implode())).alias("resp"))
    return Units(w, wp, "wake_id")


def fit_designs(res):
    out = {}
    U1 = Units(res["talks"], res["pending"], "talk_id")
    out["n_D1"] = U1.n
    out["beta_D1"] = fit("pow", U1)["params"]["beta"]
    f_rec, f_inv, f_cst = fit("rec", U1), fit("inv", U1), fit("const", U1)
    out["aic_best_D1"] = min([("rec", f_rec["aic"]), ("inv", f_inv["aic"]), ("const", f_cst["aic"]),
                              ("sat", fit("sat", U1)["aic"])], key=lambda x: x[1])[0]
    ok = res["wakes"].height and res["wake_pending"].filter(pl.col("scored")).height > 50
    for lab, W, kc in (("D2", 60.0, "k"), ("D2w300", 300.0, "k"), ("D2stint", None, "k"),
                       ("D2p", 60.0, "k_pend"), ("D2pw300", 300.0, "k_pend"), ("D2pstint", None, "k_pend")):
        if ok:
            U2 = d2_units(res, W, kc)
            out["n_" + lab] = U2.n
            out["beta_" + lab] = fit("pow", U2)["params"]["beta"] if U2.r.sum() >= 10 else float("nan")
            out["rate_" + lab] = float(U2.r.mean())
        else:
            out["n_" + lab], out["beta_" + lab], out["rate_" + lab] = 0, float("nan"), float("nan")
    out["rate_D1"] = float(U1.r.mean())
    out["median_k"] = float(np.median(U1.k))
    out["talks_per_agent_day"] = res["talks"].height / max(1, res["talks"].select("agent", "pt_date").n_unique())
    return out


SCEN_B = {
    "exo_inv": dict(rule="inv", reactive=False),
    "exo_const": dict(rule="const", reactive=False, base_theta=0.06),
    "exo_sat3": dict(rule="sat", reactive=False),
    "exo_rec": dict(rule="rec", reactive=False, base_theta=0.25),
    "react_const": dict(rule="const", reactive=True, q_s=0.006, base_theta=0.06),
    "react_inv": dict(rule="inv", reactive=True, q_s=0.006),
}


def run_B(reps=8, seed=11):
    from build import assemble
    rows = []
    for name, kw in SCEN_B.items():
        for rep in range(reps):
            t0 = time.time()
            inp, blind = simulate(seed=seed + 100 * rep + list(SCEN_B).index(name), **kw)
            res = assemble(inp)
            row = dict(scenario=name, rep=rep, variant="main", **fit_designs(res))
            rows.append(row)
            if name in ("exo_inv", "exo_const") and rep < 3:
                # room-blind k (counts the other room's messages)
                inp_b = dict(inp, expo=blind)
                rb = assemble(inp_b)
                rows.append(dict(scenario=name, rep=rep, variant="room_blind", **fit_designs(rb)))
                # naive boundary: talk times instead of call starts (turns = own talk times only, shifted +1 s)
                tt = {}
                for a in inp["turns"]:
                    own = inp["msgs"]["t"][inp["msgs"]["sender"] == a]
                    tt[a] = np.sort(np.concatenate([own + int(1.5e6), inp["pauses"][a][0] if a in inp["pauses"] else []]).astype(np.int64))
                inp_n = dict(inp, turns=tt)
                rn = assemble(inp_n)
                if rn is not None:
                    rows.append(dict(scenario=name, rep=rep, variant="naive_boundary", **fit_designs(rn)))
            print(f"{name} rep{rep}: beta_D1={row['beta_D1']:.2f} D2(60s)={row['beta_D2']:.2f} "
                  f"D2(300s)={row['beta_D2w300']:.2f} D2(stint)={row['beta_D2stint']:.2f} D2p(60)={row['beta_D2p']:.2f} "
                  f"D2p(300)={row['beta_D2pw300']:.2f} D2p(stint)={row['beta_D2pstint']:.2f} best={row['aic_best_D1']} "
                  f"nD1={row['n_D1']} nD2={row['n_D2']} rate={row['rate_D1']:.3f} rateD2={row['rate_D2']:.3f} "
                  f"k~{row['median_k']} talks/ad={row['talks_per_agent_day']:.0f} {time.time() - t0:.0f}s", flush=True)
    OUTD.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(rows)
    df.write_parquet(OUTD / "B.parquet")
    return df


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "A"
    if which == "A":
        print(run_A())
    else:
        print(run_B())
