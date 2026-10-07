"""H139 synthetic validation on real skeletons (axis F; runs before any real-data statistic).

Keeps each unit's real statements (agent, time, room, producing call), per-call clock, reads (which message each call
read) and forced resets. Only the 32-d content vectors are synthetic:
  z_B = h_i + s_i(n_B) + k_i(n_B) + o_i(n_B) + D_room(t_B) + eps_B
  s: slow OU well on the call clock, rate g_s, stationary variance 0.2 per dimension (restarted each day)
  k: read kicks, k(n) = sum_{reads r of i at n_r <= n, same day} J u_m(r) (1 - g_k)^(n - n_r); u_m = a random unit
     direction per read message (its idiosyncratic direction; the same for every reader of that message)
  o: own fast innovations (R-innovation), AR(1) on the call clock with rate g_k, total amplitude A_own
  D: room drive, OU in seconds (variance D per dimension, time scale TD)
  eps: statement noise 0.6 per dimension; h_i ~ N(0, 0.25) per dimension.
Context-held worlds erase k (and o) at a forced reset.

Worlds (card, synthetic plan; '+' = added here, not registered, labelled in the card):
  W0        no fast part                                   (no-coupling world)
  W1        reads only, J 0.044, g_k 0.15                  (H139)
  W1x5      W1 + own fast innovations: total fast = 5 A_pred
  W1x20     W1 + own fast innovations: total fast = 20 A_pred  (R-innovation, strongest-rival world for P1)
  Wctx      W1 with the kick erased at forced resets       (context-held kick)
  Wdrive+   no fast part, strong fast room drive (0.2 per dim, 5 min)   (R-drive rival)
  Wslow+    W1 under a slow drive (0.1 per dim, 3 h)
  L<A>+     W1 + own fast innovations: total fast amplitude A (absolute; ladder for A_min)
  Lctx<A>+  as L<A> but the fast part (reads and own) is erased at forced resets (R_fast at a resolvable size)

    uv run python hypotheses/H139-two-rate-variance-split/analysis/synthetic.py --units 51c --reps 100
Output: data/processed/H139-two-rate-variance-split/synthetic/runs_<unit>.parquet (checkpoint per unit) and
summary.json (after --summarize).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import zlib  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h139lib as L  # noqa: E402

OUT = L.DATA / "synthetic"
DIM = 32
VAR = {"h": 0.25, "s": 0.2, "eps": 0.6}
J0, GK0, GS0 = 0.044, 0.15, 0.01
UNIT_PERIOD = {"51c": "G51", "51d": "G51", "51g": "G51", "38a": "G38", "38b": "G38", "38e": "G38", "41": "G41",
               "51a": "G51", "51e": "G51", "51f": "G51", "51h": "G51", "37": "G37", "39": "G39", "40": "G40", "42b": "G42"}
BASE = dict(J=J0, gk=GK0, gs=GS0, D=0.05, TD=1800.0, own_mult=0.0, own_abs=0.0, ctx=False, ctx_own=False)
LADDER = [0.1, 0.3, 0.5, 1.0, 2.0, 3.0]
WORLDS = {
    "W0": {**BASE, "J": 0.0},
    "W1": dict(BASE),
    "W1x5": {**BASE, "own_mult": 5.0},
    "W1x20": {**BASE, "own_mult": 20.0},
    "Wctx": {**BASE, "ctx": True},
    "Wdrive": {**BASE, "J": 0.0, "D": 0.2, "TD": 300.0},
    "Wslow": {**BASE, "D": 0.1, "TD": 10800.0},
    **{f"L{a:g}": {**BASE, "own_abs": a} for a in LADDER},
    "Lctx3": {**BASE, "own_abs": 3.0, "ctx": True, "ctx_own": True},
}


class Sim:
    def __init__(self, S: L.Skel):
        self.S = S
        st = S.st
        self.ag = st["agent"].to_numpy()
        self.n = st["n"].to_numpy()
        self.nf = st["nf"].to_numpy()
        self.t = st["t"].dt.epoch("us").to_numpy() / 1e6
        self.room = st["room"].to_numpy()
        self.agents = np.unique(self.ag)
        # statements grouped by agent-day, in call order
        self.groups = []
        rd = S.rd
        rkey = {}
        r_reader = rd["reader"].to_numpy()
        r_day = rd["pt_date"].to_numpy()
        for k, key in enumerate(zip(r_reader, r_day)):
            rkey.setdefault(key, []).append(k)
        self.r_n = rd["n"].to_numpy()
        self.r_nf = rd["nf"].to_numpy()
        _, self.r_msg = np.unique(rd["srow_m"].to_numpy(), return_inverse=True)
        self.n_msg = int(self.r_msg.max()) + 1 if len(self.r_msg) else 0
        for r, key in enumerate(S.ad_keys):
            idx = np.flatnonzero(S.ad == r)
            idx = idx[np.argsort(self.n[idx], kind="stable")]
            self.groups.append((idx, np.asarray(rkey.get(key, []), int)))
        self.rooms = {r: np.flatnonzero(self.room == r)[np.argsort(self.t[self.room == r], kind="stable")]
                      for r in np.unique(self.room)}

    def apred(self, J=J0, gk=GK0):
        return self.S.rbar * J * J * L.kick_memory(gk)

    def _ar_at(self, idx, rate, var, rng, reset=None):
        """AR(1) on the call clock sampled at statement calls idx (sorted by n); stationary variance var per dim.
        reset: bool per position, True = a forced reset since the previous statement (fresh draw)."""
        out = np.zeros((len(idx), DIM))
        a = 1.0 - rate
        prev_n = None
        for k, i in enumerate(idx):
            if prev_n is None or (reset is not None and reset[k]):
                out[k] = rng.normal(0, np.sqrt(var), DIM)
            else:
                dn = self.n[i] - prev_n
                if dn == 0:
                    out[k] = out[k - 1]
                else:
                    ad = a ** dn
                    out[k] = ad * out[k - 1] + np.sqrt(var * (1 - ad * ad)) * rng.normal(0, 1, DIM)
            prev_n = self.n[i]
        return out

    def simulate(self, P: dict, seed: int):
        rng = np.random.default_rng(seed)
        nS = len(self.ag)
        Z = np.zeros((nS, DIM))
        h = {a: rng.normal(0, np.sqrt(VAR["h"]), DIM) for a in self.agents}
        U = rng.normal(0, 1, (self.n_msg, DIM))
        U /= np.linalg.norm(U, axis=1, keepdims=True)
        lam = 1.0 - P["gk"]
        apred = self.apred(J0, P["gk"])
        a_own = P["own_abs"] if P["own_abs"] > 0 else max(P["own_mult"] - 1.0, 0.0) * apred
        kk_sq = []
        for idx, rr in self.groups:
            if len(idx) == 0:
                continue
            a = self.ag[idx[0]]
            z = np.tile(h[a], (len(idx), 1))
            z += self._ar_at(idx, P["gs"], VAR["s"], rng)
            if a_own > 0:
                reset = None
                if P["ctx_own"]:
                    reset = np.r_[False, self.nf[idx][1:] != self.nf[idx][:-1]]
                z += self._ar_at(idx, P["gk"], a_own / DIM, rng, reset)
            if P["J"] > 0 and len(rr):
                lag = self.n[idx][:, None] - self.r_n[rr][None, :]
                M = np.where(lag >= 0, lam ** np.maximum(lag, 0), 0.0)
                if P["ctx"]:
                    M = M * (self.nf[idx][:, None] == self.r_nf[rr][None, :])
                k = P["J"] * (M @ U[self.r_msg[rr]])
                z += k
                kk_sq.append((k ** 2).sum(1))
            Z[idx] = z
        if P["D"] > 0:
            for r, k in self.rooms.items():
                tt = self.t[k]
                v = np.zeros((len(k), DIM))
                v[0] = rng.normal(0, np.sqrt(P["D"]), DIM)
                al = np.exp(-np.diff(tt) / P["TD"])
                e = rng.normal(0, 1, (len(k) - 1, DIM))
                for j in range(1, len(k)):
                    v[j] = al[j - 1] * v[j - 1] + np.sqrt(P["D"] * (1 - al[j - 1] ** 2)) * e[j - 1]
                Z[k] += v
        Z += rng.normal(0, np.sqrt(VAR["eps"]), Z.shape)
        A_emp = (float(np.concatenate(kk_sq).mean()) if kk_sq else 0.0) + a_own
        A_true = (apred if P["J"] > 0 else 0.0) + a_own
        return Z, A_true, A_emp, apred


def run_unit(unit: str, worlds: list[str], reps: int, B: int, out: Path):
    S = L.load_skeleton(UNIT_PERIOD[unit], unit)
    sim = Sim(S)
    F = L.Fitter(S.hist)
    path = out / f"runs_{unit}.parquet"
    rows = pl.read_parquet(path).to_dicts() if path.exists() else []
    done = {(r["world"], r["rep"]) for r in rows}
    print(f"{unit}: {S.st.height} statements, {len(S.ad_keys)} agent-days, r_bar {S.rbar:.3f}, "
          f"A_pred {sim.apred():.5f}, pairs lag 1-7 {int(S.hist[:5].sum())}", flush=True)
    for w in worlds:
        P = WORLDS[w]
        for rep in range(reps):
            if (w, rep) in done:
                continue
            t0 = time.time()
            seed = zlib.crc32(f"H139|{unit}|{w}|{rep}".encode()) % (2 ** 31)
            Z, A_true, A_emp, apred = sim.simulate(P, seed)
            res = {}
            for mode in ("corrected", "raw"):
                acc, _ = L.accumulate(S, Z, mode)
                r = L.analyze(S, acc, F, P["gk"], apred, B=B if mode == "corrected" else 0, seed=seed + 1,
                              oof=(mode == "corrected"), free=(mode == "corrected"), natives=(mode == "corrected"))
                if mode == "corrected":
                    res = r
                else:
                    res["raw_A_k"] = r.get("A_k", np.nan)
                    res["raw_f_s"] = r.get("f_s", np.nan)
            res.pop("boot_A_k", None)
            res.pop("boot_f_s", None)
            res.pop("boot_R_fast", None)
            res.update({"unit": unit, "world": w, "rep": rep, "A_true": A_true, "A_emp": A_emp, "rbar": S.rbar,
                        "secs": time.time() - t0})
            rows.append(res)
            if rep % 10 == 0 or rep == reps - 1:
                print(f"{unit} {w} {rep}: A_k {res.get('A_k', np.nan):.4f} ci {np.round(res.get('ci_A_k', [np.nan] * 2), 3)} "
                      f"A_true {A_true:.4f} Q {res.get('Q_k', np.nan):.2f} f_s {res.get('f_s', np.nan):.3f} "
                      f"R_fast {res.get('R_fast', np.nan):.2f} ({res['secs']:.1f}s)", flush=True)
                _write(rows, path)
    _write(rows, path)


def _write(rows, path):
    df = pl.DataFrame([{k: (json.dumps(v) if isinstance(v, (list, tuple)) else v) for k, v in r.items()} for r in rows],
                      infer_schema_length=None)
    df.write_parquet(path, compression="zstd")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="51c,51d,51g,38a,38b,38e,41")
    ap.add_argument("--worlds", default=",".join(WORLDS))
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--B", type=int, default=200)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for u in a.units.split(","):
        run_unit(u, a.worlds.split(","), a.reps, a.B, OUT)


if __name__ == "__main__":
    main()
