"""H42 synthetic validation (axis F): can the pipeline tell read-out-gated from exponential cross-excitation?

Talk processes are simulated on the skeletons of real units (one-room units: #27 regime I, #33 regime II, #40 and #51c
regime III): the real receiving-call grids (call starts redrawn uniformly inside [t_call_lo, t_call_hi], sorted), real
call classes, spans and masks. Every arm has a shared rate modulation m(t) = exp(0.5 z - 0.125), z an OU process with a
15-min timescale, common to all agents within a day (a shared field that must not be read as cross-excitation).

Truths (cluster construction; generation by generation):
  B  read-out gated: immigrants are Poisson counts at each receiving call with mean p_{i,class} m(t); a message by j at s
     gives each other present agent i Poisson children at i's calls k1+m (k1 = first true call start > s) with means
     w_bin/M_bin (shape 70% at m = 0, 20% at m = 1, 10% at m = 2-3); self children at i's later calls with weights
     proportional to exp(-(c_k - t)/300 s). Child time = call start + log-normal talk delay of agent i.
  A  ungated exponential: immigrants Poisson in continuous time at rate mu_i m(t) on the span; cross children of a
     message at s + Exp(30 s) for every other present agent; self children at t + Exp(60 s).
  0  B machinery with no cross-excitation.
Planted cross-branching n_x in {0.15, 0.30} (per message, over all recipients), self n_s = 0.15.

The analysis sees the point-estimate t_call grids (the uncertainty is propagated), runs worlds pr, A and B with
day-blocked CV, and 5 shift-null surrogates (in sample) for B (worlds pr and B) and A (world A).

Writes data/processed/H42-readout-hawkes-kernel/synthetic/synthetic.parquet. Usage: ... synthetic.py [--reps 2]
"""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h42lib as L  # noqa: E402

UNITS = ["27", "33", "40", "51c"]
TRUTHS = [("B", 0.15), ("B", 0.30), ("A", 0.30), ("0", 0.0)]
N_S = 0.15
B_SHAPE = [(0, 0, 0.7), (1, 1, 0.2), (2, 3, 0.1)]
OUT = L.DATA / "synthetic"


def ou(T, rng, tau=900.0, dt=30.0):
    n = int(T // dt) + 2
    z = np.zeros(n)
    a = np.exp(-dt / tau)
    for k in range(1, n):
        z[k] = a * z[k - 1] + np.sqrt(1 - a * a) * rng.normal()
    return lambda t: np.exp(0.5 * z[np.minimum((np.asarray(t) // dt).astype(int), n - 1)] - 0.125)


def skeleton(u: L.Unit, rng):
    """true and estimated call grids, classes, spans, delay params per (day, agent)."""
    grids = L.Grids(u, "point")
    lnp, pool = L.lognorm_params(u, grids)
    rc = u.calls.filter(pl.col("recv")).sort("day", "agent", "t_call")
    sk = {}
    for (d, a), g in rc.group_by(["day", "agent"], maintain_order=True):
        lo, hi = g["t_lo"].to_numpy(), g["t_hi"].to_numpy()
        tt = np.sort(rng.uniform(np.minimum(lo, hi), np.maximum(lo, hi)))
        cls = (2 * (g["ctx_mode"].to_numpy() == "cu") + g["wake"].to_numpy()).astype(int)
        sk[(d, a)] = {"true": tt, "cls": cls, "ln": lnp.get(a, pool)}
    sp = {(d, a): (x, y) for d, a, x, y in u.spans.select("day", "agent", "a", "b").iter_rows()}
    return sk, sp


def real_rates(u: L.Unit, sk):
    """per (agent, class) talk probability per call and per-agent talk rate per span second."""
    tk = u.talk
    pc, cnt = {}, {}
    for (d, a), s in sk.items():
        t = tk.filter((pl.col("day") == d) & (pl.col("agent") == a))["t"].to_numpy()
        k = np.searchsorted(s["true"], t, side="right") - 1
        k = k[k >= 0]
        for c in range(4):
            m = s["cls"] == c
            pc.setdefault((a, c), [0, 0])
            pc[(a, c)][0] += np.isin(k, np.where(m)[0]).sum()
            pc[(a, c)][1] += m.sum()
    p = {key: (v[0] / v[1] if v[1] else 0.0) for key, v in pc.items()}
    return p


def simulate(u: L.Unit, truth: str, n_x: float, rng):
    sk, sp = skeleton(u, rng)
    days = u.days["day"].to_list()
    T = dict(zip(days, u.days["T"].to_list()))
    p = real_rates(u, sk)
    scale = max(1e-3, 1.0 - n_x - N_S)
    events = []           # (day, agent, t, gen_kind)
    for d in days:
        m = ou(T[d], rng)
        present = [a for (dd, a) in sk if dd == d and (dd, a) in sp]
        Np = len(present)
        if Np < 2:
            continue
        alpha = n_x / (Np - 1)
        # immigrants
        gen = []
        for a in present:
            s = sk[(d, a)]
            if truth in ("B", "0"):
                lam = np.array([p.get((a, c), 0.0) for c in s["cls"]]) * m(s["true"]) * scale
                cnt = rng.poisson(lam)
                for k in np.where(cnt > 0)[0]:
                    for _ in range(cnt[k]):
                        gen.append((a, child_time(s, k, sp[(d, a)][1], rng)))
            else:
                x0, x1 = sp[(d, a)]
                n_tot = int(sum(p.get((a, c), 0.0) * (s["cls"] == c).sum() for c in range(4)))
                rate = scale * n_tot / max(x1 - x0, 1.0)
                # thinning against m(t) <= e^{2} bound
                nn = rng.poisson(rate * (x1 - x0) * 3.0)
                ts = rng.uniform(x0, x1, nn)
                keep = rng.uniform(0, 3.0, nn) < m(ts)
                gen += [(a, t) for t in ts[keep]]
        allev = [(d, a, t, "imm") for a, t in gen]
        frontier = gen
        while frontier:
            nxt = []
            for a, t in frontier:
                # self children
                for _ in range(rng.poisson(N_S)):
                    ct = place_child(sk, sp, d, a, t, truth, "self", rng)
                    if ct is not None:
                        nxt.append((a, ct, "self"))
                # cross children
                if truth != "0":
                    for i in present:
                        if i == a:
                            continue
                        if truth == "B":
                            s = sk[(d, i)]
                            k1 = np.searchsorted(s["true"], t, side="right")
                            for m0, m1, wsh in B_SHAPE:
                                for mm in range(m0, m1 + 1):
                                    k = k1 + mm
                                    if k < len(s["true"]):
                                        for _ in range(rng.poisson(alpha * wsh / (m1 - m0 + 1))):
                                            nxt.append((i, child_time(s, k, sp[(d, i)][1], rng), "cross"))
                        else:
                            for _ in range(rng.poisson(alpha)):
                                ct = t + rng.exponential(30.0)
                                if sp[(d, i)][0] <= ct <= sp[(d, i)][1]:
                                    nxt.append((i, ct, "cross"))
            allev += [(d, a, t, kind) for a, t, kind in nxt]
            frontier = [(a, t) for a, t, _ in nxt]
        events += allev
    ev = pl.DataFrame(events, schema={"day": pl.Int16, "agent": pl.Int8, "t": pl.Float64, "kind": pl.String},
                      orient="row").sort("day", "agent", "t")
    return ev


def child_time(s, k, span_end, rng):
    mu, sg = s["ln"]
    t0 = s["true"][k]
    nxt = s["true"][k + 1] if k + 1 < len(s["true"]) else span_end
    dl = np.exp(rng.normal(mu, sg))
    return float(min(t0 + dl, max(t0 + 0.5, nxt - 0.05)))


def place_child(sk, sp, d, a, t, truth, kind, rng):
    if truth in ("B", "0"):
        s = sk[(d, a)]
        k0 = np.searchsorted(s["true"], t, side="right")
        if k0 >= len(s["true"]):
            return None
        dt = s["true"][k0:] - t
        w = np.exp(-dt / 300.0)
        if w.sum() <= 0:
            return None
        k = k0 + rng.choice(len(w), p=w / w.sum())
        return child_time(s, k, sp[(d, a)][1], rng)
    ct = t + rng.exponential(60.0)
    return ct if ct <= sp[(d, a)][1] else None


def synth_unit(u: L.Unit, ev: pl.DataFrame) -> L.Unit:
    """replace talk and agent items by the synthetic messages (recipients: every other present agent, same day)."""
    talk = ev.select(pl.lit(u.unit_id).alias("unit_id"), "day", "agent", "t", pl.lit(0).cast(pl.Int8).alias("room"),
                     pl.lit(0).alias("turn_id"))
    present = u.spans.select("day", pl.col("agent").alias("recipient"))
    it = (ev.select("day", pl.col("agent").alias("sender"), pl.col("t").alias("s")).join(present, on="day")
          .filter(pl.col("recipient") != pl.col("sender"))
          .select(pl.lit(u.unit_id).alias("unit_id"), "day", "recipient", "sender", pl.lit("agent").alias("kind"), "s",
                  pl.lit(0).alias("turn_id"), pl.lit(False).alias("ment"), pl.lit(False).alias("uncertain"),
                  pl.lit(0).cast(pl.Int8).alias("room")))
    exo = u.items.filter(pl.col("kind") != "agent")
    v = L.Unit(u.unit_id, u.goal, u.regime, u.days, u.calls, talk.cast({"day": pl.Int16}),
               pl.concat([exo, it.cast(exo.schema)], how="vertical"), u.mask)
    v.spans = u.spans
    return v


def evaluate(v: L.Unit, rng):
    out = {}
    worlds = {"pr": (L.TALK_SPECS, ["S0", "A", "A_g", "B", "C"]), "A": (L.WORLD_A_SPECS, ["S0", "A", "B_t"]),
              "B": (L.WORLD_B_SPECS, ["S0", "B", "A_g", "C_g"])}
    for w, (SP, specs) in worlds.items():
        ds = L.build_talk(v, world=w)
        fits = {}
        for s in specs:
            f = L.fit_spec(ds, SP, s, warm=fits.get("S0"))
            fits[s] = f
            br = L.branching(ds, f)
            out[f"{w}:{s}:nx"] = br["n_cross"]
            out[f"{w}:{s}:ll"] = f.ll
            if s == "B":
                c = br["contrib"]
                out[f"{w}:B:share01"] = (c.get("B_0", 0) + c.get("B_1", 0)) / max(br["n_cross"], 1e-12)
            if s in ("C", "C_g"):
                c = br["contrib"]
                bm = sum(x for k, x in c.items() if L.colfam(k) == "B")
                out[f"{w}:{s}:Bshare"] = bm / max(br["n_cross"], 1e-12)
        cvr = L.cv(ds, SP, specs)
        for s, (ll, n) in cvr.items():
            out[f"{w}:{s}:cv"] = ll / max(n, 1)
        # shift null for the world's own cross spec
        own = {"pr": "B", "A": "A", "B": "B"}[w]
        nulls = []
        for _ in range(5):
            items, _k = L.shift_items(v, rng)
            dn = L.build_talk(v, world=w, items_override=items, only_cross=True, base=ds)
            f0 = L.fit_spec(dn, SP, "S0")
            f1 = L.fit_spec(dn, SP, own, warm=f0)
            nulls.append(L.branching(dn, f1)["n_cross"])
        out[f"{w}:{own}:null_q95"] = float(np.quantile(nulls, 0.95))
        out[f"{w}:{own}:null_mean"] = float(np.mean(nulls))
        db = []
        for k in range(1, min(3, v.n_days - 1) + 1):
            items = L.dayblock_items(v, k)
            dn = L.build_talk(v, world=w, items_override=items, only_cross=True, base=ds)
            f0 = L.fit_spec(dn, SP, "S0")
            f1 = L.fit_spec(dn, SP, own, warm=f0)
            db.append(L.branching(dn, f1)["n_cross"])
        out[f"{w}:{own}:db_mean"] = float(np.mean(db)) if db else np.nan
        out[f"{w}:{own}:db_max"] = float(np.max(db)) if db else np.nan
    return out


def task(args):
    uid, truth, n_x, rep = args
    rng = np.random.default_rng(1000 * rep + hash((uid, truth, n_x)) % 997)
    t0 = time.time()
    u = L.load_unit(uid)
    ev = simulate(u, truth, n_x, rng)
    v = synth_unit(u, ev)
    n = len(ev)
    nx_real = float((ev["kind"] == "cross").sum() / max(n, 1))
    res = {"unit_id": uid, "truth": truth, "n_x_planted": n_x, "rep": rep, "n_events": n, "n_real_talk": len(u.talk),
           "n_x_true": nx_real, "n_s_true": float((ev["kind"] == "self").sum() / max(n, 1))}
    res.update(evaluate(v, rng))
    res["secs"] = time.time() - t0
    return res


def main():
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 2
    tasks = [(u, t, x, r) for r in range(reps) for u in UNITS for t, x in TRUTHS]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with Pool(2, maxtasksperchild=2) as pool:
        for res in pool.imap_unordered(task, tasks):
            rows.append(res)
            print(res["unit_id"], res["truth"], res["n_x_planted"], res["rep"], f"n={res['n_events']}",
                  f"true={res['n_x_true']:.3f}", f"pr:B={res['pr:B:nx']:.3f}", f"A:A={res['A:A:nx']:.3f}",
                  f"B:B={res['B:B:nx']:.3f}", f"{res['secs']:.0f}s", flush=True)
            pl.DataFrame(rows).write_parquet(OUT / "synthetic.parquet")
    (OUT / "_note.json").write_text(json.dumps({"units": UNITS, "truths": TRUTHS, "reps": reps, "n_s": N_S}))


if __name__ == "__main__":
    main()
