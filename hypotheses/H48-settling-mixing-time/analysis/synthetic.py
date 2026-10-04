"""H48 synthetic validation (axis F): content dynamics on the REAL read-out schedules and statement times/counts of
every replication period, through the identical S1 estimator and LOPO test.

Truths (card Model): RD read-out DeGroot toward read senders' work; RC coverage completion (depth kappa = 5);
FD field decay on the active-hour clock (tau_f lognormal, independent of reading); FC field decay on the agent's own
call count. (A cross-check with the shared simulator's ContentModel('ou', A_k) was planned, not run in round 1.)

  uv run python hypotheses/H48-settling-mixing-time/analysis/synthetic.py [--reps 30] [--workers 2]
Writes data/processed/H48-settling-mixing-time/synthetic/{fits.parquet, lopo.parquet, summary.json}.
Uses schedules and statement times only (no content outcomes)."""
from __future__ import annotations

import argparse
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h48lib as L  # noqa: E402
from h48lib import hc  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

OUT = hc.OUT / "synthetic"
D_ = 32
PAR = dict(h=1.0, A=1.0, Ainf=0.35, aw=0.9, sigma=1.3, alpha=0.004, kappa=5.0, tau_med=5.0, tau_sd=0.6,
           kappa_c=650.0, day_sd=0.0)
PREDICTORS = {  # name -> (column, transform): log of the column; 'inv' = log(1/x); 'lin' = raw
    "T90_k1_room": ("k1_room_T90", "log"), "T50_k1_room": ("k1_room_T50", "log"),
    "T90_k5_room": ("k5_room_T90", "log"), "T90_tr_room": ("tr_room_T90", "log"),
    "T99_k1_room": ("k1_room_T99", "log"),
    "tmix_batch_bulk": ("tmix_batch_bulk", "log"), "tmix_batch_worst": ("tmix_batch_worst", "log"),
    "tmix_count_bulk": ("tmix_count_bulk", "log"), "dg_bulk": ("dg_bulk", "log"), "dg_worst": ("dg_worst", "log"),
    "reading_rate": ("u", "inv"), "call_rate": ("call_rate", "inv"),
    "l2_sym_min": ("l2_sym_min", "inv"), "l2_dir_min": ("l2_dir_min", "inv"), "ul2_rw_min": ("ul2_rw_min", "inv"),
    "dg50_gamma": ("dg50_gamma", "inv"),
    "n_rooms": ("n_rooms", "lin"), "N": ("N", "log"), "hours_per_day": ("hours_per_day", "log"),
}


def aniso(rng, d=D_, k0=4.0):
    lam = np.exp(-np.arange(d) / k0)
    lam /= lam.sum()
    Q = np.linalg.qr(rng.standard_normal((d, d)))[0]
    return Q * np.sqrt(lam)            # E|L eps|^2 = 1


class Sched:
    def __init__(self, g: int):
        P = L.load_period(g)
        ro = P["roster"].filter(pl.col("on_day1"))
        self.g = g
        self.agents = sorted(int(x) for x in ro["agent"].to_list())
        self.blocks = L.blocks_of(P["roster"])
        pos = {a: n for n, a in enumerate(self.agents)}
        self.N = len(self.agents)
        de = L.day_ends(g)
        self.day_ends = np.asarray(de, float)
        self.a_max = float(de[min(hc.MAX_FIT_DAYS, len(de)) - 1])
        lab = np.full(self.N, -1)
        for b, ags in self.blocks.items():
            for a in ags:
                lab[pos[a]] = b
        self.lab = lab
        bs = {b: (lab == b).sum() for b in self.blocks}
        self.nb = np.array([bs.get(l_, self.N) for l_ in lab])
        st = P["stmts"].filter(pl.col("agent").is_in(self.agents) & (pl.col("a") >= 0) & (pl.col("a") <= self.a_max)
                               & ~pl.col("pre_kick"))
        self.s_agent = np.array([pos[int(x)] for x in st["agent"].to_list()])
        self.s_a = st["a"].to_numpy().astype(float)
        r = P["reads"].filter(pl.col("reader").is_in(self.agents) & pl.col("sender").is_in(self.agents)
                              & (pl.col("a_read") <= self.a_max)).sort("a_read", "turn_id")
        self.r_i = np.array([pos[int(x)] for x in r["reader"].to_list()], dtype=int)
        self.r_s = np.array([pos[int(x)] for x in r["sender"].to_list()], dtype=int)
        self.r_t = r["a_read"].to_numpy().astype(float)
        tid = r["turn_id"].to_numpy()
        self.c_start = np.r_[0, np.flatnonzero(np.diff(tid) != 0) + 1] if len(tid) else np.array([], int)
        self.c_end = np.r_[self.c_start[1:], len(tid)] if len(tid) else np.array([], int)
        c = P["calls"].filter(pl.col("agent").is_in(self.agents) & (pl.col("a") <= self.a_max))
        self.own_calls = {pos[int(a)]: np.sort(np.asarray(t, float)) for a, t in
                          c.group_by("agent").agg(pl.col("a")).iter_rows()}


def simulate(S: Sched, truth: str, rng, par=PAR) -> tuple[np.ndarray, dict]:
    N = S.N
    Lm = aniso(rng)
    k = rng.standard_normal(D_); k /= np.linalg.norm(k)
    h = rng.standard_normal((N, D_)); h *= par["h"] / np.linalg.norm(h, axis=1, keepdims=True)
    w = rng.standard_normal((N, D_)); w *= par["aw"] / np.linalg.norm(w, axis=1, keepdims=True)
    A, Ainf = par["A"], par["Ainf"]
    ns = len(S.s_a)
    X = np.zeros((ns, D_))
    truth_info = {}
    if truth in ("FD", "FC"):
        if truth == "FD":
            tau = float(np.exp(np.log(par["tau_med"]) + par["tau_sd"] * rng.standard_normal()))
            f = np.exp(-S.s_a / tau)
            truth_info["tau_true"] = tau
        else:
            f = np.zeros(ns)
            for i in range(N):
                m = S.s_agent == i
                ct = S.own_calls.get(i, np.array([]))
                f[m] = np.exp(-np.searchsorted(ct, S.s_a[m], side="right") / par["kappa_c"])
            rates = np.array([len(S.own_calls.get(i, [])) for i in range(N)]) / max(S.a_max, 1e-9)
            truth_info["tau_true"] = float(par["kappa_c"] / np.median(rates[rates > 0]))
        X = (Ainf + (A - Ainf) * f)[:, None] * k[None] + (1 - f)[:, None] * w[S.s_agent]
    elif truth == "RD":
        al = par["alpha"]
        y = np.tile((A - Ainf) * k, (N, 1))
        times = [[0.0] for _ in range(N)]
        states = [[y[i].copy()] for i in range(N)]
        for s0, e0 in zip(S.c_start, S.c_end):
            i = S.r_i[s0]
            y[i] = (1 - al) * y[i] + al * w[S.r_s[s0:e0]].mean(0)
            times[i].append(S.r_t[s0])
            states[i].append(y[i].copy())
        for i in range(N):
            m = np.flatnonzero(S.s_agent == i)
            if len(m) == 0:
                continue
            tt = np.asarray(times[i]); ss = np.asarray(states[i])
            ix = np.searchsorted(tt, S.s_a[m], side="right") - 1
            X[m] = Ainf * k + ss[np.clip(ix, 0, len(tt) - 1)]
        u = np.array([len(times[i]) - 1 for i in range(N)]) / max(S.a_max, 1e-9)
        truth_info["tau_true"] = float(1.0 / (al * max(np.median(u), 1e-9)))
    elif truth == "RC":
        kap = par["kappa"]
        for i in range(N):
            m = np.flatnonzero(S.s_agent == i)
            if len(m) == 0:
                continue
            ev = np.flatnonzero(S.r_i == i)
            peers = np.flatnonzero((S.lab == S.lab[i]) & (np.arange(N) != i)) if S.lab[i] >= 0 else \
                np.flatnonzero(np.arange(N) != i)
            npeer = max(len(peers), 1)
            if len(ev):
                onehot = np.zeros((len(ev) + 1, N))
                onehot[np.arange(1, len(ev) + 1), S.r_s[ev]] = 1.0
                cum = np.cumsum(onehot, axis=0)
                ix = np.searchsorted(S.r_t[ev], S.s_a[m], side="right")
                n_ij = cum[ix]
            else:
                n_ij = np.zeros((len(m), N))
            gg = 1 - np.exp(-n_ij / kap)
            gbar = gg[:, peers].sum(1) / npeer
            X[m] = (Ainf + (A - Ainf) * (1 - gbar))[:, None] * k[None] + (gg[:, peers] @ w[peers]) / math.sqrt(npeer)
        truth_info["tau_true"] = np.nan
    else:
        raise ValueError(truth)
    Zs = h[S.s_agent] + X + par["sigma"] * (rng.standard_normal((ns, D_)) @ Lm.T)
    if par.get("day_sd", 0) > 0:          # shared day drive (post-hoc calibration): one random field per active day
        dayk = np.searchsorted(S.day_ends, S.s_a, side="left")
        G = par["day_sd"] * (rng.standard_normal((dayk.max() + 1, D_)) @ Lm.T) * math.sqrt(D_) / math.sqrt(D_)
        Zs = Zs + G[dayk]
    Zs /= np.linalg.norm(Zs, axis=1, keepdims=True)
    Dq = rng.standard_normal((30, D_)); Dq /= np.linalg.norm(Dq, axis=1, keepdims=True)
    return Zs, {"k": k, "D": Dq, **truth_info}


def one_period(args):
    g, truths, reps, seed, par = args
    PAR.update(par)
    S = Sched(g)
    rows = []
    for truth in truths:
        for r in range(reps):
            rng = np.random.default_rng([seed, g, r, truths.index(truth)])
            Z, info = simulate(S, truth, rng, PAR)
            f, _ = L.s1_fit(S.s_a, S.s_agent, Z, info["k"], info["D"], S.a_max)
            rows.append(dict(goal_no=g, truth=truth, rep=r, tau_true=info.get("tau_true", np.nan),
                             tau_hat=f["tau"] if f else np.nan, detected=bool(f and f["detected"]),
                             dbic=f["dbic"] if f else np.nan, A0=f["A_0"] if f else np.nan,
                             Ainf=f["A_inf"] if f else np.nan))
    print(f"#{g} done", flush=True)
    return rows


def lopo_table(fits: pl.DataFrame, X: pl.DataFrame, n_perm: int, groups_col=None) -> list[dict]:
    out = []
    for (truth, rep), sub in fits.group_by(["truth", "rep"]):
        s = sub.filter(pl.col("detected")).join(X, on="goal_no")
        if s.height < 8:
            continue
        y = np.log(s["tau_hat"].to_numpy())
        for name, (col, tr) in PREDICTORS.items():
            x = s[col].to_numpy().astype(float)
            ok = np.isfinite(x) & (x > 0 if tr != "lin" else np.isfinite(x))
            if ok.sum() < 8:
                continue
            xv = np.log(x[ok]) if tr == "log" else (-np.log(x[ok]) if tr == "inv" else x[ok])
            res = L.lopo_compare(y[ok], xv, n_perm=n_perm, seed=rep)
            out.append(dict(truth=truth, rep=rep, predictor=name, gain=res["gain"], p=res["p_perm"],
                            slope=res["slope"], n=res["n"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--n-perm", type=int, default=300)
    ap.add_argument("--periods", default=None)
    ap.add_argument("--lopo-only", action="store_true", help="reuse synthetic/fits.parquet")
    ap.add_argument("--sigma", type=float, default=None, help="statement noise (post-hoc calibration runs)")
    ap.add_argument("--A", type=float, default=None, help="kickoff amplitude (post-hoc calibration runs)")
    ap.add_argument("--truths", default="RD,RC,FD,FC")
    ap.add_argument("--day-sd", type=float, default=None)
    ap.add_argument("--tag", default="", help="output subfolder for calibration runs")
    a = ap.parse_args()
    global OUT
    if a.tag:
        OUT = hc.OUT / "synthetic" / a.tag
    if a.sigma is not None:
        PAR["sigma"] = a.sigma
    if a.day_sd is not None:
        PAR["day_sd"] = a.day_sd
    if a.A is not None:          # scale the kickoff amplitude and plateau together
        PAR["Ainf"] = PAR["Ainf"] * a.A / PAR["A"]
        PAR["A"] = a.A
    OUT.mkdir(parents=True, exist_ok=True)
    periods = [int(x) for x in a.periods.split(",")] if a.periods else hc.REPLICATION
    truths = a.truths.split(",")
    t0 = time.time()
    rows = []
    jobs = [(g, truths, a.reps, hc.SEED, dict(PAR)) for g in sorted(periods, key=lambda g: -1 if g == 51 else g)]
    if a.lopo_only:
        fits = pl.read_parquet(OUT / "fits.parquet")
    else:
        with ProcessPoolExecutor(max_workers=min(a.workers, 2)) as ex:
            for r in ex.map(one_period, jobs):
                rows += r
        fits = pl.DataFrame(rows)
        fits.write_parquet(OUT / "fits.parquet")
    X = pl.read_parquet(hc.OUT / "readout_period.parquet")
    lp = pl.DataFrame(lopo_table(fits, X, a.n_perm))
    lp.write_parquet(OUT / "lopo.parquet")
    summ = {"params": PAR, "reps": a.reps, "periods": periods, "n_perm": a.n_perm, "truths": {}}
    for truth in truths:
        f = fits.filter(pl.col("truth") == truth)
        det = f.group_by("rep").agg(pl.col("detected").mean())["detected"]
        rec = []
        for rep, sub in f.filter(pl.col("detected")).group_by("rep"):
            if truth in ("RD", "FD", "FC") and sub.height >= 6 and np.isfinite(sub["tau_true"].to_numpy().astype(float)).all():
                rho = stats.spearmanr(sub["tau_true"], sub["tau_hat"]).statistic
                rec.append(rho)
        d = {"detect_rate_median": float(det.median()), "recovery_rho_median": float(np.nanmedian(rec)) if rec else None,
             "tau_hat_median_h": float(f.filter(pl.col("detected"))["tau_hat"].median() or np.nan),
             "predictors": {}}
        for name in PREDICTORS:
            s = lp.filter((pl.col("truth") == truth) & (pl.col("predictor") == name))
            if s.height == 0:
                continue
            g_, p_ = s["gain"].to_numpy(), s["p"].to_numpy()
            d["predictors"][name] = {"median_gain": float(np.median(g_)), "pass_rate": float(np.mean((g_ >= 0.10) & (p_ < 0.05))),
                                     "beats_m0_rate": float(np.mean(g_ > 0)), "median_slope": float(s["slope"].median()),
                                     "n_datasets": s.height}
        summ["truths"][truth] = d
    summ["runtime_s"] = time.time() - t0
    hc.save_json(OUT / "summary.json", summ)
    pp = hc.OUT / "_provenance.json"
    prov = hc.load_json(pp)
    prov.setdefault("derived", {})["synthetic"] = {"built_by": "hypotheses/H48-settling-mixing-time/analysis/synthetic.py",
                                                   "git_commit": hc.common.git_commit(), "params": PAR, "reps": a.reps}
    hc.save_json(pp, prov)
    for truth, d in summ["truths"].items():
        print(truth, "detect", round(d["detect_rate_median"], 2), "rho", d["recovery_rho_median"], "tau_med", d["tau_hat_median_h"])
        for name, v in d["predictors"].items():
            print(f"   {name:18s} gain {v['median_gain']:+.2f} pass {v['pass_rate']:.2f} slope {v['median_slope']:+.2f}")


if __name__ == "__main__":
    main()
