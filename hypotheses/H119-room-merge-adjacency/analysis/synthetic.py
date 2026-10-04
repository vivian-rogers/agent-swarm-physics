"""H119 P0: synthetic validation on the real NE42 skeleton (#39 | #40 | #41), axis F.

E1 worlds (minute talk spins on the real kept grids, real agents, real minute-level rooms, block-rate baselines with
per-agent rate calibration): every world has a global OU drive (tau 10 min, sd 0.5, agent lags 0-3 min).
  coupling_J   adjacency-gated coupling J_ij(t) = J * colocated_ij(t), J in {0.3, 0.6}
  roomdrive    no coupling; each room has its own OU drive (tau 10 min, sd 0.7) seen with agent lags 0-3 min
  remanence    coupling J = 0.6, and cross pairs keep 0.5 J in #41 although they sit in different rooms
Readouts: class model (within, cross, GPT-5 x #rest, GPT-5 x #best) per week -> M, M_D, Rm, P_m with Wald CIs.
E2 worlds (real #40 call skeleton: eligible agents' ledger calls, t_call, latency, room; messages simulated from
simulated talk calls, posted at t_call + latency):
  read_J    P(talk) = sigma(base_i + J sum_j log(1+R_cj) + room drive), J in {0.3, 0.6}
  drive     J = 0; room OU drive (tau 600 s, sd 1.0) seen with agent lags 0-180 s (H90's impostor)
Readout: C_RU = J^R_x - J^U_x (cross class) and J^R_w - J^U_w with Wald CIs.

Usage: uv run python hypotheses/H119-room-merge-adjacency/analysis/synthetic.py [--worlds 30] [--part e1|e2|both]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zlib
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(HERE))
import ki_talk as K  # noqa: E402
import h119lib as L  # noqa: E402

OUT = K.ROOT / "data/processed/H119-room-merge-adjacency/synthetic"


# ------------------------------------------------------------------ E1 skeleton
def e1_skeleton():
    weeks = L.NE42_WEEKS
    alld = [d for w in weeks.values() for d in w]
    sp = K.day_spins(alld)
    ag = K.eligible(sp, list(weeks.values()))
    sk = {"agents": ag, "weeks": {}}
    for w, days in weeks.items():
        st = K.stack(sp, days, ag)
        rooms = K.colocation(st, ag)
        prof = []
        for (d, S, mins, t0), R in zip(st, rooms):
            blk = mins // K.BLOCK_MIN
            ub, inv = np.unique(blk, return_inverse=True)
            P = np.zeros((len(ag), len(ub)))
            for n in range(len(ag)):
                k = np.bincount(inv, (S[n] > 0).astype(float), len(ub))
                c = np.bincount(inv, None, len(ub))
                P[n] = (k + 0.25) / (c + 1.0)
            prof.append((d, mins, inv, P, R))
        sk["weeks"][w] = prof
    sk["classes"] = L.ne42_classes(ag)
    return sk


def ou(T, tau, sd, rng):
    a = np.exp(-1.0 / tau)
    x = np.zeros(T)
    e = rng.normal(0, sd * np.sqrt(1 - a * a), T)
    x[0] = rng.normal(0, sd)
    for t in range(1, T):
        x[t] = a * x[t - 1] + e[t]
    return x


def sim_day(P, inv, R, J, off, lags, rng, room_sd, keep_cross=None, Kself=0.3, Kbox=0.5):
    N, T = R.shape[0], R.shape[1]
    lp = np.log(P / (1 - P))
    base = lp - Kself * 2 * P - Kbox * 2 * P
    g = ou(T + 4, 10.0, 0.5, rng)
    rooms_u = np.unique(R[R >= 0])
    rd = {r: ou(T + 4, 10.0, room_sd, rng) if room_sd > 0 else np.zeros(T + 4) for r in rooms_u}
    S = -np.ones((N, T), np.int8)
    S[:, 0] = np.where(rng.random(N) < P[:, inv[0]], 1, -1)
    cs = np.zeros((N, T + 1)); cs[:, 1] = S[:, 0]
    for t in range(T - 1):
        lo = max(0, t - K.BOX + 1)
        m = (cs[:, t + 1] - cs[:, lo]) / (t + 1 - lo)
        A = (R[:, t][:, None] == R[:, t][None, :]) & (R[:, t][:, None] >= 0)
        Jt = J * A
        if keep_cross is not None:
            Jt = Jt + keep_cross
        np.fill_diagonal(Jt, 0)
        dr = np.array([rd[R[n, t]][t + 4 - lags[n]] if R[n, t] >= 0 else 0.0 for n in range(N)])
        eta = base[:, inv[t + 1]] + off + g[t + 4 - lags] + dr + Kself * (S[:, t] + 1) + Kbox * (m + 1) + Jt @ (m + 1)
        S[:, t + 1] = np.where(rng.random(N) < 1 / (1 + np.exp(-eta)), 1, -1)
        cs[:, t + 2] = cs[:, t + 1] + S[:, t + 1]
    return S


def e1_world(args):
    kind, J, seed = args
    sk = SK["e1"]
    rng = np.random.default_rng(seed)
    N = len(sk["agents"])
    lags = rng.integers(0, 4, N)
    room_sd = 0.7 if kind == "roomdrive" else 0.0
    Jc = 0.0 if kind == "roomdrive" else J
    cls = sk["classes"]
    # calibrate per-agent offsets on #39 (two passes)
    off = np.zeros(N)
    target = np.array([np.mean(np.concatenate([P[n, inv] for d, mins, inv, P, R in sk["weeks"]["39"]])) for n in range(N)])
    for _ in range(2):
        r = np.zeros(N); c = 0
        for d, mins, inv, P, R in sk["weeks"]["39"][:2]:
            S = sim_day(P, inv, R, Jc, off, lags, rng, room_sd)
            r += (S > 0).sum(1); c += S.shape[1]
        r = np.clip(r / c, 1e-3, 1 - 1e-3)
        off += np.log(target / (1 - target)) - np.log(r / (1 - r))
    res = {"kind": kind, "J": J, "seed": seed}
    fits = {}
    for w, prof in sk["weeks"].items():
        keep = None
        if kind == "remanence" and w == "41":
            keep = np.where(cls == 1, 0.5 * J, 0.0)
        st = []
        for d, mins, inv, P, R in prof:
            S = sim_day(P, inv, R, Jc, off, lags, rng, room_sd, keep_cross=keep)
            st.append((d, S, mins, None))
        fits[w] = K.fit_e1_class(st, cls, L.CLASS_IDS)
    res.update(L.ne42_contrasts(fits))
    return res


# ------------------------------------------------------------------ E2 skeleton
def e2_skeleton():
    ag = SK["e1"]["agents"] if "e1" in SK else e1_skeleton()["agents"]
    days = L.NE42_WEEKS["40"]
    calls = K.calls_frame(days, ag)
    rate = calls.group_by("agent").agg(pl.col("talk").mean().alias("p"))
    return {"agents": ag, "calls": calls, "rate": dict(zip(rate["agent"].to_list(), rate["p"].to_list()))}


def e2_world(args):
    kind, J, seed = args
    sk = SK["e2"]
    rng = np.random.default_rng(seed)
    calls = sk["calls"]
    ag = sk["agents"]
    lag = {a: rng.uniform(0, 180) for a in ag}
    tc = calls["tc_us"].to_numpy() / 1e6
    Lc = calls["latency_s"].to_numpy()
    rec = calls["agent"].to_numpy()
    room = calls["room"].to_numpy()
    order = np.argsort(tc, kind="stable")
    t0, t1 = tc.min() - 400, tc.max() + 400
    grid = np.arange(t0, t1, 10.0)
    drives = {}
    sd = 1.0 if kind == "drive" else 0.3
    for r_ in np.unique(room):
        a = np.exp(-10.0 / 600.0)
        x = np.zeros(len(grid)); e = rng.normal(0, sd * np.sqrt(1 - a * a), len(grid)); x[0] = rng.normal(0, sd)
        for k in range(1, len(grid)):
            x[k] = a * x[k - 1] + e[k]
        drives[r_] = x
    base = {a: np.log(max(sk["rate"].get(a, 0.03), 1e-3) / (1 - max(sk["rate"].get(a, 0.03), 1e-3))) - 0.2 for a in ag}
    Jr = J if kind == "read_J" else 0.0
    y = np.zeros(len(tc), bool)
    recent = deque()  # (t_post, sender, room)
    pending = []      # heap-like list of future posts
    import heapq
    for c in order:
        t = tc[c]
        while pending and pending[0][0] < t:
            recent.append(heapq.heappop(pending))
        while recent and recent[0][0] < t - 600:
            recent.popleft()
        a = rec[c]
        cnt = {}
        for (tp, s, r_) in recent:
            if s != a and r_ == room[c] and t - Lc[c] <= tp < t:
                cnt[s] = cnt.get(s, 0) + 1
        x = sum(np.log1p(v) for v in cnt.values())
        k = int((t - lag[a] - t0) // 10.0)
        f = drives[room[c]][min(max(k, 0), len(grid) - 1)]
        p = 1 / (1 + np.exp(-(base[a] + Jr * x + f)))
        if rng.random() < p:
            y[c] = True
            heapq.heappush(pending, (t + Lc[c], a, room[c]))
    posts = sorted(list(recent) + pending + [])
    # rebuild the full message list: every simulated talk call posts at t_call + L
    tp = tc[y] + Lc[y]
    msgs = pl.DataFrame({"t_us": (tp * 1e6).astype(np.int64), "agent": rec[y], "room": room[y]})
    cf = calls.with_columns(pl.Series("talk", y))
    senders = ag
    R, U, Us = K.e2_counts(cf, msgs, senders)
    cls = SK["e1"]["classes"] if "e1" in SK else None
    ai = {a_: i for i, a_ in enumerate(ag)}
    fn = lambda i, j: int(cls[ai[i], ai[j]]) if (i in ai and j in ai) else -1  # noqa: E731
    yv, X, g, A = K.e2_design(cf, R, U, senders, fn, L.CLASS_IDS)
    r = K.fit_e2(yv, X, g, A, len(L.CLASS_IDS))
    out = {"kind": kind, "J": J, "seed": seed, "talk_rate": float(y.mean())}
    out.update(L.e2_contrasts(r))
    return out


# ------------------------------------------------------------------ switch units (P7 power)
def sw_skeleton(name):
    import run as RUN
    bef, aft, folder, goal = RUN.SWITCHES[name]
    sp = K.day_spins(bef + aft)
    ag = K.eligible(sp, [bef, aft])
    sides = {}
    shares = []
    for lab, days in (("b", bef), ("a", aft)):
        st = K.stack(sp, days, ag)
        rooms = K.colocation(st, ag)
        shares.append(K.coloc_share(rooms))
        prof = []
        for (d, S, mins, t0), R in zip(st, rooms):
            blk = mins // K.BLOCK_MIN
            ub, inv = np.unique(blk, return_inverse=True)
            P = np.zeros((len(ag), len(ub)))
            for n in range(len(ag)):
                k = np.bincount(inv, (S[n] > 0).astype(float), len(ub))
                c = np.bincount(inv, None, len(ub))
                P[n] = (k + 0.25) / (c + 1.0)
            prof.append((d, mins, inv, P, R))
        sides[lab] = prof
    cls = L.switch_classes(*shares)
    return {"agents": ag, "sides": sides, "classes": cls}


def sw_world(args):
    name, kind, J, seed = args
    sk = SK["sw"][name]
    rng = np.random.default_rng(seed)
    N = len(sk["agents"])
    lags = rng.integers(0, 4, N)
    room_sd = 0.7 if kind == "roomdrive" else 0.0
    Jc = 0.0 if kind == "roomdrive" else J
    off = np.zeros(N)
    target = np.array([np.mean(np.concatenate([P[n, inv] for d, mins, inv, P, R in sk["sides"]["b"]])) for n in range(N)])
    for _ in range(3):
        r = np.zeros(N); c = 0
        for d, mins, inv, P, R in sk["sides"]["b"]:
            S = sim_day(P, inv, R, Jc, off, lags, rng, room_sd)
            r += (S > 0).sum(1); c += S.shape[1]
        r = np.clip(r / c, 1e-3, 1 - 1e-3)
        off += 0.7 * (np.log(target / (1 - target)) - np.log(r / (1 - r)))
    fits = {}
    for lab, prof in sk["sides"].items():
        st = [(d, sim_day(P, inv, R, Jc, off, lags, rng, room_sd), mins, None) for d, mins, inv, P, R in prof]
        fits[lab] = K.fit_e1_class(st, sk["classes"], [0, 1, 2, 3])
    cls = sk["classes"]
    out = {"unit": name, "kind": kind, "J": J, "seed": seed}
    out.update(L.switch_contrast(fits["b"], fits["a"], int((cls == 1).sum()), int((cls == 2).sum())))
    return out


SK = {}


def _init(parts):
    if "sw" in parts:
        import run as RUN
        SK["sw"] = {n: sw_skeleton(n) for n in RUN.SWITCHES}
    if "e1" in parts or "e2" in parts:
        SK["e1"] = e1_skeleton()
    if "e2" in parts:
        SK["e2"] = e2_skeleton()


def summarize(df: pl.DataFrame, part: str) -> dict:
    s = {}
    for (kind, J), g in df.group_by(["kind", "J"], maintain_order=True):
        d = {"worlds": g.height}
        if part == "e1":
            d["M_detect"] = float((g["M_lo"] > 0).mean())
            d["MD_detect"] = float((g["MD_lo"] > 0).mean())
            d["Rm_detect"] = float((g["Rm_lo"] > 0).mean())
            d["Pm_below"] = float((g["Pm_hi"] < 0).mean())
            d["M_median"] = float(g["M"].median()); d["Rm_median"] = float(g["Rm"].median())
            d["Jx40_median"] = float(g["Jx_40"].median()); d["Jw40_median"] = float(g["Jw_40"].median())
        else:
            d["CRU_x_detect"] = float((g["CRU_x_lo"] > 0).mean())
            d["CRU_w_detect"] = float((g["CRU_w_lo"] > 0).mean())
            d["JRx_detect"] = float((g["JRx_lo"] > 0).mean())
            d["JUx_detect"] = float((g["JUx_lo"] > 0).mean())
            d["CRU_x_median"] = float(g["CRU_x"].median())
            d["talk_rate"] = float(g["talk_rate"].mean())
        s[f"{kind}_{J}"] = d
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=30)
    ap.add_argument("--part", default="both")
    a = ap.parse_args()
    parts = ["e1", "e2"] if a.part == "both" else a.part.split(",")
    OUT.mkdir(parents=True, exist_ok=True)
    summ = {}
    t = time.time()
    with ProcessPoolExecutor(2, initializer=_init, initargs=(parts,)) as ex:
        if "e1" in parts:
            jobs = [(k, J, zlib.crc32(f"{k}{J}{i}".encode())) for k, J in
                    (("coupling", 0.3), ("coupling", 0.6), ("roomdrive", 0.0), ("remanence", 0.6)) for i in range(a.worlds)]
            df = pl.DataFrame(list(ex.map(e1_world, jobs)), infer_schema_length=None)
            df.write_parquet(OUT / "p0_e1.parquet")
            summ["e1"] = summarize(df, "e1")
        if "e2" in parts:
            jobs = [(k, J, zlib.crc32(f"e2{k}{J}{i}".encode())) for k, J in
                    (("read_J", 0.3), ("read_J", 0.6), ("drive", 0.0)) for i in range(a.worlds)]
            df = pl.DataFrame(list(ex.map(e2_world, jobs)), infer_schema_length=None)
            df.write_parquet(OUT / "p0_e2.parquet")
            summ["e2"] = summarize(df, "e2")
        if "sw" in parts:
            import run as RUN
            jobs = [(n, k, J, zlib.crc32(f"sw{n}{k}{J}{i}".encode())) for n in RUN.SWITCHES for k, J in
                    (("coupling", 0.3), ("coupling", 0.6), ("roomdrive", 0.0)) for i in range(a.worlds)]
            df = pl.DataFrame(list(ex.map(sw_world, jobs)), infer_schema_length=None)
            df.write_parquet(OUT / "p0_sw.parquet")
            s = {}
            for (n, k, J), g in df.group_by(["unit", "kind", "J"], maintain_order=True):
                ok = g.filter(pl.col("S").is_not_null()) if "S" in g.columns else g.head(0)
                s[f"{n}_{k}_{J}"] = {"worlds": g.height, "S_detect": float((ok["S_p1"] < 0.05).mean()) if ok.height else None,
                                     "S_median": float(ok["S"].median()) if ok.height else None}
            summ["sw"] = s
    summ["_meta"] = {"worlds": a.worlds, "seconds": round(time.time() - t, 1)}
    prev = {}
    pj = OUT / "p0_summary.json"
    if pj.exists():
        prev = json.loads(pj.read_text())
    prev.update(summ)
    pj.write_text(json.dumps(prev, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
