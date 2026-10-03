"""Village-level Hawkes model for agent chat messages with exogenous kick kernels (H04).

Discrete time, bins of DT seconds inside each day's empirical window (days are independent realizations).
Expected count in bin t of day d:

    L_t = mu_d * b_q(t) * DT
          + sum_{j=1,2} a_j (1 - e^{-B_j DT}) z_j(t)              (endogenous; n = a_1 + a_2)
          + sum_{c in human, nudge} e_c (1 - e^{-G_c DT}) w_c(t)  (exogenous; e_c = messages triggered per kick)

with z(t) = sum_{k>=1} e^{-B (k-1) DT} y(t-k) (an AR(1) filter of the counts; lfilter per day). mu_d is profiled
per day (Newton), b_q is a 4-step within-day profile with mean 1. Poisson likelihood, L-BFGS-B on log params.

Events: chat messages by agents (chat_core speaker_kind == agent, including the Claude Code agent, whose messages
are part of the village chat). Kicks: human messages and nudges (h04lib.load_messages).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h04lib import *  # noqa: E402,F403

from scipy.optimize import minimize  # noqa: E402
from scipy.signal import lfilter  # noqa: E402

DT = 10.0
NQ = 4
PNAMES = ["a1", "B1", "a2", "B2", "eh", "Gh", "en", "Gn", "b1", "b2", "b3"]
BOUNDS = {"a1": (1e-4, 3), "B1": (1 / 600, 1 / 10), "a2": (1e-4, 3), "B2": (1 / 14400, 1 / 600),
          "eh": (1e-4, 20), "Gh": (1 / 14400, 1 / 10), "en": (1e-4, 20), "Gn": (1 / 14400, 1 / 10),
          "b1": (np.exp(-3), np.exp(3)), "b2": (np.exp(-3), np.exp(3)), "b3": (np.exp(-3), np.exp(3))}
INIT = {"a1": 0.2, "B1": 1 / 60, "a2": 0.2, "B2": 1 / 1800, "eh": 0.5, "Gh": 1 / 300, "en": 0.5, "Gn": 1 / 300,
        "b1": 1.0, "b2": 1.0, "b3": 1.0}


@dataclass
class Series:
    days: list[str]
    y: list[np.ndarray]      # agent messages per bin
    xh: list[np.ndarray]     # human messages per bin
    xn: list[np.ndarray]     # nudges per bin
    q: list[np.ndarray]      # within-day quarter per bin

    def subset(self, idx):
        return Series([self.days[i] for i in idx], [self.y[i] for i in idx], [self.xh[i] for i in idx],
                      [self.xn[i] for i in idx], [self.q[i] for i in idx])

    @property
    def n_events(self):
        return int(sum(v.sum() for v in self.y))


def build_series(days: list[str], agents: set[int] | None = None) -> Series:
    """agents: restrict the event stream (agent messages) and nudges (to targets in the set) to these agent codes."""
    cal = calendar().filter(pl.col("pt_date").is_in(days)).select("pt_date", "win_start", "window_s")
    meta = {d: (ws, w) for d, ws, w in cal.iter_rows()}
    chat = pl.read_parquet(S / "chat_core.parquet", columns=["t", "pt_date", "speaker_kind", "agent"]).filter(
        pl.col("pt_date").is_in(days) & (pl.col("speaker_kind").cast(pl.Utf8) == "agent"))
    msgs = load_messages(days)
    if agents is not None:
        ag = pl.Series(sorted(agents), dtype=pl.Int8)
        chat = chat.filter(pl.col("agent").is_in(ag.implode()))
        msgs = msgs.filter((pl.col("kind") != "nudge") | pl.col("valid_mentions").list.eval(pl.element().is_in(ag.implode())).list.any())
    out = Series([], [], [], [], [])
    for d in sorted(days):
        if d not in meta or not meta[d][1]:
            continue
        ws, w = meta[d]
        nb = int(w // DT) + 1

        def binc(ts):
            k = ((ts - ws).dt.total_seconds() // DT).cast(pl.Int64).to_numpy()
            k = k[(k >= 0) & (k < nb)]
            return np.bincount(k, minlength=nb).astype(float)
        out.days.append(d)
        out.y.append(binc(chat.filter(pl.col("pt_date") == d)["t"]))
        out.xh.append(binc(msgs.filter((pl.col("pt_date") == d) & (pl.col("kind") == "human"))["t"]))
        out.xn.append(binc(msgs.filter((pl.col("pt_date") == d) & (pl.col("kind") == "nudge"))["t"]))
        out.q.append(np.minimum(np.arange(nb) * NQ // nb, NQ - 1))
    return out


def _filt(x, B):
    return lfilter([0.0, 1.0], [1.0, -np.exp(-B * DT)], x)


class Model:
    def __init__(self, ser: Series, free: list[str]):
        self.s, self.free = ser, free
        self.Y = np.concatenate(ser.y); self.Q = np.concatenate(ser.q)
        self.off = np.cumsum([0] + [len(v) for v in ser.y])
        self.dayid = np.repeat(np.arange(len(ser.y)), [len(v) for v in ser.y])
        self._cache = {}

    def z(self, key, B):
        ck = (key, round(float(B), 14))
        if ck not in self._cache:
            src = {"y": self.s.y, "h": self.s.xh, "n": self.s.xn}[key]
            self._cache[ck] = np.concatenate([_filt(v, B) for v in src])
            if len(self._cache) > 64:
                self._cache.pop(next(iter(self._cache)))
        return self._cache[ck]

    def params(self, theta):
        p = {k: 0.0 for k in PNAMES}
        p.update({"b1": 1.0, "b2": 1.0, "b3": 1.0, "B1": INIT["B1"], "B2": INIT["B2"], "Gh": INIT["Gh"], "Gn": INIT["Gn"]})
        p.update({k: float(np.exp(v)) for k, v in zip(self.free, theta)})
        return p

    def parts(self, p):
        E = (p["a1"] * (1 - np.exp(-p["B1"] * DT)) * self.z("y", p["B1"]) + p["a2"] * (1 - np.exp(-p["B2"] * DT)) * self.z("y", p["B2"])
             + p["eh"] * (1 - np.exp(-p["Gh"] * DT)) * self.z("h", p["Gh"]) + p["en"] * (1 - np.exp(-p["Gn"] * DT)) * self.z("n", p["Gn"]))
        bl = np.array([p["b1"], p["b2"], p["b3"], 1.0]); bl = NQ * bl / bl.sum()
        Bt = bl[self.Q] * DT
        return E, Bt

    def profile_mu(self, E, Bt, iters=30):
        nd = len(self.off) - 1
        sB = np.add.reduceat(Bt, self.off[:-1])
        sY = np.add.reduceat(self.Y, self.off[:-1])
        sE = np.add.reduceat(E, self.off[:-1])
        mu = np.maximum((sY - sE) / sB, 0.05 * sY / sB + 1e-9)
        pos = self.Y > 0
        yb, Bb, Eb, db = self.Y[pos], Bt[pos], E[pos], self.dayid[pos]
        for _ in range(iters):
            den = mu[db] * Bb + Eb
            f = np.bincount(db, weights=yb * Bb / den, minlength=nd) - sB
            fp = -np.bincount(db, weights=yb * Bb ** 2 / den ** 2, minlength=nd)
            step = np.where(fp < 0, f / fp, 0.0)
            mu = np.maximum(mu - step, mu / 10)
        return mu

    def loglik(self, theta, per_day=False):
        p = self.params(theta)
        E, Bt = self.parts(p)
        mu = self.profile_mu(E, Bt)
        L = mu[self.dayid] * Bt + E
        ll = self.Y * np.log(np.maximum(L, 1e-300)) - L
        return np.add.reduceat(ll, self.off[:-1]) if per_day else float(ll.sum())

    def fit(self, x0=None):
        if x0 is None:
            x0 = np.log([INIT[k] for k in self.free])
        bnds = [tuple(np.log(BOUNDS[k])) for k in self.free]
        r = minimize(lambda th: -self.loglik(th) / max(1, self.Y.sum()), x0, method="L-BFGS-B", bounds=bnds,
                     options={"maxiter": 400, "eps": 1e-5})
        self.theta, self.res = r.x, r
        return self

    def summary(self):
        p = self.params(self.theta)
        out = {k: p[k] for k in self.free}
        out["n"] = p["a1"] + p["a2"]
        out["tau_fast_s"], out["tau_slow_s"] = 1 / p["B1"], 1 / p["B2"]
        if "eh" in self.free:
            out["tau_h_s"] = 1 / p["Gh"]
        if "en" in self.free:
            out["tau_n_s"] = 1 / p["Gn"]
        out["loglik_per_event"] = self.loglik(self.theta) / max(1, self.Y.sum())
        out["converged"] = bool(self.res.success)
        out["n_events"] = int(self.Y.sum()); out["n_days"] = len(self.off) - 1
        out["n_human"] = int(sum(v.sum() for v in self.s.xh)); out["n_nudge"] = int(sum(v.sum() for v in self.s.xn))
        return out

    def rescaled_ks(self, seed=RNG_SEED):
        """Time-rescaling: compensator increments between consecutive events (jittered within bins) ~ Exp(1)."""
        from scipy.stats import kstest
        rng = np.random.default_rng(seed)
        p = self.params(self.theta)
        E, Bt = self.parts(p)
        mu = self.profile_mu(E, Bt)
        L = mu[self.dayid] * Bt + E
        gaps = []
        for d in range(len(self.off) - 1):
            a, b = self.off[d], self.off[d + 1]
            cum = np.concatenate([[0.0], np.cumsum(L[a:b])])
            ev = np.repeat(np.arange(b - a), self.Y[a:b].astype(int))
            if len(ev) < 3:
                continue
            tt = np.sort(cum[ev] + rng.random(len(ev)) * L[a:b][ev])
            gaps.append(np.diff(tt))
        g = np.concatenate(gaps)
        return float(kstest(g, "expon").statistic)


def free_params(ser: Series, exo=True):
    f = ["a1", "B1", "a2", "B2", "b1", "b2", "b3"]
    if exo and sum(v.sum() for v in ser.xh) >= 5:
        f += ["eh", "Gh"]
    if exo and sum(v.sum() for v in ser.xn) >= 5:
        f += ["en", "Gn"]
    return f


def null_params():
    return ["b1", "b2", "b3"]


def fit_suite(ser: Series, exo=True) -> Model:
    return Model(ser, free_params(ser, exo)).fit()


def cv(ser: Series, k=5, seed=RNG_SEED) -> dict:
    """Day-blocked k-fold CV: kernel and profile fitted on train days; mu_d profiled on each test day (both models)."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(ser.days))
    folds = np.array_split(idx, k)
    tot = {"hawkes": 0.0, "hawkes_noexo": 0.0, "poisson": 0.0}
    nev = 0
    per_fold = []
    for f in folds:
        tr = np.setdiff1d(idx, f)
        trs, tes = ser.subset(sorted(tr)), ser.subset(sorted(f))
        row = {}
        for name, free in (("hawkes", free_params(trs)), ("hawkes_noexo", free_params(trs, False)), ("poisson", null_params())):
            m = Model(trs, free).fit()
            mt = Model(tes, free)
            row[name] = mt.loglik(m.theta)
            tot[name] += row[name]
        ne = tes.n_events
        nev += ne
        per_fold.append({k_: v / max(1, ne) for k_, v in row.items()})
    return {"dll_per_event_vs_poisson": (tot["hawkes"] - tot["poisson"]) / nev,
            "dll_per_event_exo_vs_noexo": (tot["hawkes"] - tot["hawkes_noexo"]) / nev,
            "folds_hawkes_beats_poisson": int(sum(r["hawkes"] > r["poisson"] for r in per_fold)),
            "folds_exo_beats_noexo": int(sum(r["hawkes"] > r["hawkes_noexo"] for r in per_fold)), "k": k}


def simulate(m: Model, seed: int) -> Series:
    """Simulate agent-message counts from a fitted model with the same days, kicks, mu_d and profile."""
    rng = np.random.default_rng(seed)
    p = m.params(m.theta)
    E, Bt = m.parts(p)
    mu = m.profile_mu(E, Bt)
    ys = []
    exo = (p["eh"] * (1 - np.exp(-p["Gh"] * DT)) * m.z("h", p["Gh"]) + p["en"] * (1 - np.exp(-p["Gn"] * DT)) * m.z("n", p["Gn"]))
    d1, d2 = np.exp(-p["B1"] * DT), np.exp(-p["B2"] * DT)
    c1, c2 = p["a1"] * (1 - d1), p["a2"] * (1 - d2)
    for d in range(len(m.off) - 1):
        a, b = m.off[d], m.off[d + 1]
        base = mu[d] * Bt[a:b] + exo[a:b]
        y = np.zeros(b - a); z1 = z2 = 0.0
        u = rng.random(b - a)
        for t in range(b - a):
            lam = base[t] + c1 * z1 + c2 * z2
            # Poisson draw via inversion on a pre-drawn uniform (counts per 10 s bin are small)
            k, pk = 0, np.exp(-lam)
            cdf = pk
            while u[t] > cdf and k < 50:
                k += 1; pk *= lam / k; cdf += pk
            y[t] = k
            z1 = d1 * z1 + k; z2 = d2 * z2 + k
        ys.append(y)
    return Series(m.s.days, ys, m.s.xh, m.s.xn, m.s.q)


def recovery(m: Model, reps=3) -> dict:
    true = m.summary()
    rec = []
    for r in range(reps):
        sim = simulate(m, RNG_SEED + r)
        f = Model(sim, m.free).fit().summary()
        rec.append({k: f.get(k) for k in ("n", "en", "eh", "tau_fast_s", "tau_slow_s")})
    return {"true": {k: true.get(k) for k in ("n", "en", "eh", "tau_fast_s", "tau_slow_s")}, "refits": rec}
