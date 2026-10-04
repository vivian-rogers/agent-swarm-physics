"""H53 synthetic validation (axis F): plant adoption mechanisms on the REAL call schedules, rooms, seeds, read-out ages,
susceptible and commitment flags, then run the real estimator suite and check which world it recovers.

Worlds (card, "Synthetic validation plan"):
  W0     activity null: constant per-call hazard h*A_X from a_seed - 2 h (no seed effect)
  WN2/4  receptive nucleation: at the read-out call P = p*A_X*(m if timely & uncommitted else 1), m = 2 / 4; W0 at half rate
  WS     poster status: at the read-out call P = p*A_X*exp(0.7 z_status), no timing; W0 at half rate
  WF0    shared field at the seed: every susceptible agent in every room, per-call hazard h*A_X*exp(-(a - a_seed)/30 min)
  WFpre  attention burst: the same pulse starting U(0, 60) active min before the seed
A_X ~ Gamma(shape 0.3, mean 1). Rates calibrated to a mean in-room wave of 0.3 or 1.0 (chosen before any real outcome).
Real pre-seed adopters are dropped from the risk set and never used (no real outcome enters the synthetic data).

Usage: uv run python hypotheses/H53-announcement-nucleation/analysis/synthetic.py [--reps 20] [--quick]
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import polars as pl

from h53core import (FU_S, H_S, OUT, agent_rr, agent_table, cv_compare, eligible_periods, field_diagnostics, load, prep,
                     seed_models, shift_slopes)

SYN = OUT / "synthetic"
WORLDS = ["W0", "WN2", "WN4", "WS", "WF0", "WFpre"]
SYN_MODELS = {"M0": [], "M_N": ["lN"], "M_U": ["lU"], "M_R": ["lR"], "M_status": ["lstat", "human"],
              "M_full": ["lN", "lU", "lstat", "human", "share", "tod", "first30"],
              "M_full+R": ["lN", "lU", "lstat", "human", "share", "tod", "first30", "lR"]}


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


class Sched:
    """Flattened per-pair call schedules for the risk set."""

    def __init__(self, seeds, rec):
        s, r = prep(seeds, rec)
        self.s0, self.r0 = s, r
        elig = set(eligible_periods(s))
        self.goals = elig
        r = r.filter(pl.col("goal_no").is_in(list(elig)))
        self.risk = r.filter(pl.col("sus")).sort("sid", "agent")
        cc = pl.read_parquet(OUT / "calls_cache.parquet").filter(pl.col("recv") & ~pl.col("ho_call")).drop_nulls("a")
        calls = {int(a): sub["a"].to_numpy() for (a,), sub in cc.sort("agent", "a").group_by(["agent"], maintain_order=True)}
        A, P, RI = [], [], []
        off = [0]
        a_seed = self.risk["a_seed"].to_numpy()
        a_read = self.risk["a_read"].fill_null(np.nan).to_numpy()
        ag = self.risk["agent"].to_numpy()
        inroom = self.risk["in_room"].to_numpy()
        for k in range(self.risk.height):
            ca = calls.get(int(ag[k]), np.zeros(0))
            lo = np.searchsorted(ca, a_seed[k] - 7200, "left")
            hi = np.searchsorted(ca, a_seed[k] + H_S + FU_S, "right")
            sl = ca[lo:hi]
            A.append(sl); P.append(np.full(len(sl), k, np.int32))
            if inroom[k] and np.isfinite(a_read[k]):
                j = np.searchsorted(sl, a_read[k] - 1e-6, "left")
                RI.append(j if j < len(sl) else -1)
            else:
                RI.append(-1)
            off.append(off[-1] + len(sl))
        self.ca = np.concatenate(A); self.pidx = np.concatenate(P); self.off = np.array(off); self.ri = np.array(RI)
        self.n = self.risk.height
        self.a_seed_p = a_seed
        sidp = self.risk["sid"].to_numpy()
        self.sid_u, self.sid_ix = np.unique(sidp, return_inverse=True)
        self.timely_unc = (self.risk["timely"] & self.risk["unc"]).to_numpy()
        self.inroom = inroom
        # poster status z within period (humans 0)
        st = s.filter(pl.col("goal_no").is_in(list(elig))).select("sid", "goal_no", "lstat", "human")
        st = st.with_columns(((pl.col("lstat") - pl.col("lstat").mean().over("goal_no")) / pl.col("lstat").std().over("goal_no")).fill_nan(0).fill_null(0).alias("z"))
        st = st.with_columns(pl.when(pl.col("human") > 0).then(0.0).otherwise(pl.col("z")).alias("z"))
        zmap = dict(zip(st["sid"].to_list(), st["z"].to_list()))
        self.z_seed = np.array([zmap.get(int(x), 0.0) for x in self.sid_u])
        log(f"risk pairs {self.n}, calls {len(self.ca)}, seeds {len(self.sid_u)}, periods {sorted(elig)}")

    def first_hit(self, prob, rng):
        """prob per flattened call -> adoption active time per pair (nan if none)."""
        hit = rng.random(len(prob)) < prob
        out = np.full(self.n, np.nan)
        idx = np.nonzero(hit)[0]
        if len(idx):
            p = self.pidx[idx]
            first = np.unique(p, return_index=True)
            out[first[0]] = self.ca[idx[first[1]]]
        return out

    def simulate(self, world, rate, rng):
        A = rng.gamma(0.3, 1 / 0.3, len(self.sid_u))[self.sid_ix]   # per pair
        Ac = A[self.pidx]
        dt = self.ca - self.a_seed_p[self.pidx]
        if world == "W0":
            return self.first_hit(1 - np.exp(-rate * Ac), rng)
        if world in ("WF0", "WFpre"):
            ons = np.zeros(len(self.sid_u)) if world == "WF0" else -rng.uniform(0, 3600, len(self.sid_u))
            d2 = dt - ons[self.sid_ix][self.pidx]
            haz = np.where(d2 > 0, rate * Ac * np.exp(-np.clip(d2, 0, None) / 1800), 0.0)
            return self.first_hit(1 - np.exp(-haz), rng)
        # read-out-call worlds: a weak per-call background (0.002 x the event scale) plus an event at the read-out call
        bg = self.first_hit(1 - np.exp(-0.002 * rate * Ac * (dt > -7200)), rng)
        if world.startswith("WN"):
            m = float(world[2:])
            P = rate * A * np.where(self.timely_unc, m, 1.0)
        else:  # WS
            P = rate * A * np.exp(0.7 * self.z_seed[self.sid_ix])
        P = np.clip(P, 0, 1)
        ev = np.full(self.n, np.nan)
        ok = (self.ri >= 0) & (rng.random(self.n) < P)
        k = rng.geometric(0.5, self.n) - 1
        for p in np.nonzero(ok)[0]:
            j = self.off[p] + self.ri[p] + k[p]
            if j < self.off[p + 1]:
                ev[p] = self.ca[j]
        return np.fmin(bg, ev)

    def to_tables(self, sim):
        """Synthetic recipients table: a_label replaced by simulated times; k_adopt / n_fu from the simulated call index."""
        r = self.r0.filter(pl.col("goal_no").is_in(list(self.goals)))
        risk = self.risk.with_columns(pl.Series("a_sim", sim))
        # k_adopt: index of adoption call relative to the read-out call (1 = the read-out call)
        kad = np.full(self.n, np.nan)
        nfu = np.full(self.n, np.nan)
        for p in range(self.n):
            if self.ri[p] < 0:
                continue
            sl = self.ca[self.off[p]:self.off[p + 1]]
            ar = sl[self.ri[p]]
            nfu[p] = np.searchsorted(sl, ar + FU_S, "right") - self.ri[p]
            if np.isfinite(sim[p]):
                kad[p] = np.searchsorted(sl, sim[p], "left") - self.ri[p] + 1
        risk = risk.with_columns(pl.Series("k_sim", kad), pl.Series("nfu_sim", nfu))
        r = r.join(risk.select("sid", "agent", "a_sim", "k_sim", "nfu_sim"), on=["sid", "agent"], how="left")
        r = r.with_columns(pl.when(pl.col("sus")).then(pl.col("a_sim")).otherwise(pl.col("a_seed") - 1e6).alias("a_label"),
                           pl.col("k_sim").fill_nan(None).cast(pl.Int64).alias("k_adopt"), pl.col("nfu_sim").fill_nan(None).cast(pl.Int64).alias("n_fu"))
        rec = r.drop("a_sim", "k_sim", "nfu_sim", "t_flread", "sus", "unc", "timely", "sus_in", "recept", "adopt_H", "a_seed", "a_gend", "censored")
        seeds = self.s0.select([pl.col(c) for c in self.s0.columns if c not in
                               ("N_sus", "U", "R", "S", "N_out", "S_out", "lN", "lU", "lR", "lstat", "human_f", "first30", "eligible")])
        seeds = seeds.with_columns(pl.col("human").cast(pl.Boolean))
        return seeds.filter(pl.col("goal_no").is_in(list(self.goals))), rec

    def mean_wave(self, sim):
        inwin = self.inroom & np.isfinite(sim) & (sim > self.a_seed_p) & (sim <= self.a_seed_p + H_S)
        el = self.s0.filter(pl.col("eligible") & pl.col("goal_no").is_in(list(self.goals)))["sid"].to_numpy()
        m = np.isin(self.risk["sid"].to_numpy(), el)
        return inwin[m].sum() / len(el)


def calibrate(sc: Sched, world, target, rng_seed=7):
    lo, hi = -14.0, 3.0
    for _ in range(18):
        mid = (lo + hi) / 2
        vals = [sc.mean_wave(sc.simulate(world, np.exp(mid), np.random.default_rng(rng_seed + i))) for i in range(3)]
        if np.mean(vals) < target:
            lo = mid
        else:
            hi = mid
    return float(np.exp((lo + hi) / 2))


def run_estimators(seeds, rec, rng, cv="kfold"):
    s, r = prep(seeds, rec)
    out = {}
    mod, cvll, goals = seed_models(s, cv=cv, models=SYN_MODELS, rng=rng)
    out["models"] = {k: dict(cv_ll=v["cv_ll"], coef=v["coef"], se=v["se"], cols=v["cols"]) for k, v in mod.items()}
    out["cmp"] = {f"M_R-{b}": cv_compare(cvll, goals, "M_R", b, nboot=500, rng=rng) for b in ("M_N", "M_U", "M_status", "M0")}
    out["cmp"]["M_full+R-M_full"] = cv_compare(cvll, goals, "M_full+R", "M_full", nboot=500, rng=rng)
    at = agent_table(s, r)
    out["agent"] = agent_rr(at)
    out["agent_int"] = agent_rr(at, xcols=("x_recept", "x_timely", "x_unc", "lcalls", "talk"))
    out["field"] = field_diagnostics(s, r)
    out["shift"] = shift_slopes(s, r)
    return out


def classify_v2(o):
    """Decision rule v2 (Amendment 1, frozen from the synthetic results before any real data):
    nucleation = RR_timely CI > 1, F1 >= 3, F4 >= 2 and F2 <= 0.6 (where rooms exist);
    status = status slope CI > 0 with RR_timely CI including 1;
    field = F1 < 3 or F2 > 0.6 (pre-ramp or all-room field); seed-locked field = F1 >= 3 but F4 < 2;
    read-out-triggered (no timing) = F1 >= 3, F4 >= 2, RR_timely CI includes 1, no status; else null."""
    a = o["agent"].get("x_timely", {})
    rr_pos = a.get("lo", 0) > 1
    f = o["field"]
    f1, f2, f4 = f["F1"]["ratio"], f["F2"]["ratio"], f["F4"].get("ratio")
    mf = o["models"]["M_full+R"]
    ist = mf["cols"].index("lstat")
    stat_pos = (mf["coef"][ist] - 1.96 * mf["se"][ist]) > 0
    step = f1 is not None and f1 >= 3
    lock = f4 is not None and f4 >= 2
    allroom = f2 is not None and f2 > 0.6
    if rr_pos and step and lock and not allroom:
        return "nucleation"
    if stat_pos and not rr_pos:
        return "status"
    if not step or allroom:
        return "field"
    if not lock:
        return "seed-locked field"
    return "read-out (no timing)"


def classify(o):
    """Frozen decision rule (card). Returns world label."""
    a = o["agent"].get("x_timely", {})
    rr_pos = a.get("lo", 0) > 1
    beat = all(o["cmp"][k]["lo90"] > 0 for k in ("M_R-M_N", "M_R-M_U"))
    f = o["field"]
    f1 = f["F1"]["ratio"]
    f2 = f["F2"]["ratio"]
    field_flag = (f1 is not None and f1 < 3) or (f2 is not None and f2 > 0.3)
    mf = o["models"]["M_full+R"]
    cols = mf["cols"]
    ist = cols.index("lstat")
    stat_pos = (mf["coef"][ist] - 1.96 * mf["se"][ist]) > 0
    if rr_pos and beat and not field_flag:
        return "nucleation"
    if stat_pos and not rr_pos:
        return "status"
    if field_flag:
        return "field"
    return "null"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--targets", default="0.3,1.0")
    ap.add_argument("--worlds", default=",".join(WORLDS))
    a = ap.parse_args()
    SYN.mkdir(parents=True, exist_ok=True)
    seeds, rec = load()
    sc = Sched(seeds, rec)
    results = []
    cal_rates = {}
    for target in [float(x) for x in a.targets.split(",")]:
        for w in a.worlds.split(","):
            rate = calibrate(sc, w, target)
            cal_rates[f"{w}@{target}"] = rate
            log(f"{w} target {target}: rate {rate:.3g}")
            for rep in range(a.reps):
                rng = np.random.default_rng(1000 * rep + WORLDS.index(w) * 7919 + int(target * 10))
                sim = sc.simulate(w, rate, rng)
                sd, rd = sc.to_tables(sim)
                o = run_estimators(sd, rd, rng)
                o.update(world=w, target=target, rep=rep, mean_wave=float(sc.mean_wave(sim)), label=classify(o), label_v2=classify_v2(o))
                results.append(o)
                ag = o["agent"].get("x_timely", {})
                log(f"  {w} {target} rep {rep}: wave {o['mean_wave']:.2f} RR {ag.get('rr', float('nan')):.2f} [{ag.get('lo', float('nan')):.2f},{ag.get('hi', float('nan')):.2f}] "
                    f"M_R-M_N {o['cmp']['M_R-M_N']['diff']:.1f} F1 {o['field']['F1']['ratio']} F2 {o['field']['F2']['ratio']} -> {o['label']}")
            (SYN / "synthetic_results.json").write_text(json.dumps(dict(rates=cal_rates, results=results), default=str))
    from h53lib import provenance
    provenance("analysis/synthetic.py", ["calls_cache (H53)", "seeds (H53)", "recipients (H53)"], dict(worlds=WORLDS, reps=a.reps, targets=a.targets), "hypotheses/H53-announcement-nucleation/analysis/synthetic.py")
    log("done")


if __name__ == "__main__":
    main()
