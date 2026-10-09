"""H147 synthetic validation (axis F), on the real #51 skeleton, before any real-data outcome.

Skeleton: real statements (agent, time, bin), real F / P events with their call windows, the real agent x bin panel
(presence, own-repo commits, role alignment, talk share), real dated events and placebo days. Patterns are synthetic:
a set of candidate hosts carries the pattern (a latent carry state per agent, persistence and recruitment by
prevalence), and a carrying agent's statements express one of K's 8 elements with probability p_on (others p_bg).

Worlds
  wipes   W_art (artifact-held: a wipe changes nothing; c = 0), W_ctx(c) (context-held: after a current host's forced
          erasure each of its own K hits in calls 1..20 is deleted with probability c; c = 0.1, 0.2, 0.3, exact
          truth dV = -c), W_reset (mechanistic: a wipe resets the host's carry state to 0; no exact truth).
          The segment-position rival is in every world, because the real statements are 2x rarer in calls 1..20
          after a wipe than in calls 21..40 (scheme check); frequency-matched pseudo-patterns carry it too.
  hubs    W_hub (the lost agent holds ~0.6-0.7 of K's hits and goes silent on K in the event window; others unchanged:
          beta = 1), W_dist (the lost agent holds ~0.25 and the others absorb its share: beta = 0), W_null (no change).
  ops     W_op(-0.2) (all carriers' p_on x 0.8 after the event for the window) and W_null; prevalence change vs
          placebo days.
  hosts   real own-repo commits; hosting from synthetic patterns that follow the real statement volume (the talk-vs-work
          rival: hosting needs statements, statements displace commits); planted delta in {-0.2, -0.1, 0, +0.1, +0.2}
          by binomial thinning (exact relative truth); the same for role alignment (additive delta x baseline).

Usage: uv run python hypotheses/H147-egregore-value-and-hosts-51/analysis/synthetic.py [--reps 20] [--part wipes|hubs|ops|hosts|all]
Output: data/processed/H147-egregore-value-and-hosts-51/synthetic/*.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h147lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

C = L.C
OUT = C.OUT / "synthetic"
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:7.0f}s]", *a, flush=True)


class Gen:
    """Statement-level pattern generator on the real skeleton."""

    def __init__(self, sk: L.Skeleton):
        st = sk.stm.select("agent", "t", "bin", "pt_date").sort("t")
        self.a = st["agent"].to_numpy().astype(np.int16)
        self.t = st["t"].dt.epoch("us").to_numpy()
        self.bin = st["bin"].fill_null(-1).to_numpy().astype(np.int32)
        days = st["pt_date"].to_numpy()
        self.day = np.unique(days, return_inverse=True)[1]
        self.n_days = int(self.day.max()) + 1
        self.sk = sk
        f = sk.ev.filter(pl.col("etype") == "F")
        self.F_by_agent = {int(a): np.sort(f.filter(pl.col("agent") == a)["t"].dt.epoch("us").to_numpy())
                           for a in f["agent"].unique()}
        cnt = np.bincount(self.a.astype(int), minlength=64)
        self.active_agents = np.flatnonzero(cnt >= 150)

    def pattern(self, rng, hosts, n_el=8, p_on=0.35, p_bg=0.03, d=0.08, r0=0.01, r1=0.15, day_sd=0.3,
                hub=None, hub_mult=1.0, hub_window=None, absorb=False, scale_after=None, reset=False):
        hosts = set(int(h) for h in hosts)
        nh = len(hosts)
        fday = np.exp(rng.normal(0, day_sd, self.n_days))
        z = {h: rng.random() < 0.3 for h in hosts}
        carriers = sum(z.values())
        last_t = {h: -1 for h in hosts}
        wptr = {h: 0 for h in hosts}
        n = len(self.t)
        u1, u2, u3 = rng.random(n), rng.random(n), rng.random(n)
        el = rng.integers(0, n_el, n)
        keep = np.zeros(n, bool)
        absorb_mult = 1.0
        for j in range(n):
            a = int(self.a[j])
            tj = self.t[j]
            if a in hosts:
                if reset:
                    ft = self.F_by_agent.get(a)
                    if ft is not None:
                        p = wptr[a]
                        while p < len(ft) and ft[p] <= tj:
                            if ft[p] > last_t[a] and z[a]:
                                z[a] = False
                                carriers -= 1
                            p += 1
                        wptr[a] = p
                last_t[a] = tj
                if z[a]:
                    if u1[j] < d:
                        z[a] = False
                        carriers -= 1
                elif u1[j] < r0 + r1 * carriers / nh:
                    z[a] = True
                    carriers += 1
                if z[a]:
                    p = p_on * fday[self.day[j]]
                    if hub is not None and a == hub:
                        p *= hub_mult
                    if hub_window is not None and hub_window[0] <= tj < hub_window[1]:
                        if a == hub:
                            p = 0.0
                        elif absorb:
                            p *= absorb_mult
                    if scale_after is not None and scale_after[0] <= tj < scale_after[1]:
                        p *= scale_after[2]
                    keep[j] = u2[j] < min(p, 0.95)
                else:
                    keep[j] = u2[j] < p_bg
            else:
                keep[j] = u3[j] < p_bg * 0.5
        return L.Hits(self.a[keep], self.t[keep], el[keep], self.bin[keep])

    def hosts(self, rng, n):
        return rng.choice(self.active_agents, size=n, replace=False)


def thin_after_wipes(sk: L.Skeleton, hits: L.Hits, c: float, rng) -> L.Hits:
    """Exact context-held plant: delete each own K hit in calls 1..20 after a current host's forced erasure w.p. c."""
    if c <= 0:
        return hits
    wf = L.wipe_frame(sk, hits)
    sel = np.flatnonzero(wf["host"] & sk.e_F)
    drop = np.zeros(len(hits), bool)
    for i in sel:
        a = sk.e_agent[i]
        lo, hi = sk.e_t[i], sk.e_post[i]
        j0, j1 = np.searchsorted(hits.t, lo, "left"), np.searchsorted(hits.t, hi, "left")
        if j1 > j0:
            m = np.flatnonzero(hits.agent[j0:j1] == a) + j0
            drop[m] |= rng.random(len(m)) < c
    k = ~drop
    return L.Hits(hits.agent[k], hits.t[k], hits.e[k], hits.bin[k])


# ------------------------------------------------------------------------------------------------ wipes
def run_wipes(sk, gen, reps, n_pseudo=20, B=100):
    worlds = [("W_art", 0.0, False), ("W_ctx10", 0.1, False), ("W_ctx20", 0.2, False), ("W_ctx30", 0.3, False),
              ("W_reset", 0.0, True)]
    keys = L.VALUE_KEYS
    res = {w[0]: [] for w in worlds}
    t_prof = None
    for r in range(reps):
        rng = np.random.default_rng(1000 + r)
        nh = int(rng.choice([5, 8, 12]))
        hosts = gen.hosts(rng, nh)
        base_seed = 50_000 + r
        # pseudo-patterns: frequency-matched artifact-held patterns on fresh host sets (no plant)
        t1 = time.time()
        pv = {k: [] for k in keys}
        pi_ = []
        for k in range(n_pseudo):
            prng = np.random.default_rng(base_seed * 100 + k)
            ph = gen.pattern(prng, gen.hosts(prng, nh))
            wf = L.wipe_frame(sk, ph)
            v = L.value_fit(sk, wf)
            for kk in keys:
                pv[kk].append(v[kk])
            pi_.append(L.info_fit(sk, wf, n_perm=20)["I_K"])
        if t_prof is None:
            t_prof = (time.time() - t1) / n_pseudo
        for name, c, reset in worlds:
            wrng = np.random.default_rng(base_seed)
            h = gen.pattern(wrng, hosts, reset=reset)
            h = thin_after_wipes(sk, h, c, np.random.default_rng(base_seed + 7))
            wf = L.wipe_frame(sk, h)
            v = L.value_fit(sk, wf)
            inf = L.info_fit(sk, wf, n_perm=50)
            bv, bi = L.boot_value_info(sk, wf, B=B, seed=r)
            row = {"rep": r, "n_hosts": nh, "n_host_events": v["n_host_events"], "n_F": v["n_F"],
                   "truth_dV": -c if not reset else None}
            for kk in keys:
                e = L.excess_ci(v[kk], bv[kk], pv[kk])
                row[kk] = {"raw": float(np.exp(v[kk]) - 1), **e}
                for form in ("boot", "comb", "pq"):
                    ci = e[form]
                    row[kk]["fals_" + form] = bool(e["excess"] <= -0.10 and np.isfinite(ci[1]) and ci[1] < 0)
                    row[kk]["excl0_" + form] = bool(np.isfinite(ci[0]) and (ci[1] < 0 or ci[0] > 0))
            ii = np.asarray(pi_, float)
            ii = ii[np.isfinite(ii)]
            ci_i = L.q(bi - np.nanmean(bi) + inf["I_K"] - np.median(ii))
            row["I_K_raw"] = inf["I_K"]
            row["I_excess"] = float(inf["I_K"] - np.median(ii))
            row["I_ci"] = ci_i
            row["I_identified"] = bool(np.isfinite(ci_i[0]) and ci_i[0] > 0)
            res[name].append(row)
        log(f"wipes rep {r}: " + ", ".join(f"{w}: rate {res[w][-1]['b_rate']['excess']:+.3f} "
                                           f"oth {res[w][-1]['b_oth']['excess']:+.3f} I {res[w][-1]['I_excess']:+.4f}"
                                           for w, _, _ in worlds))
    summ = {}
    for w, c, reset in worlds:
        a = res[w]
        d = {"planted_dV": None if reset else -c, "reps": len(a),
             "median_host_events": float(np.median([x["n_host_events"] for x in a])),
             "mean_I_excess": float(np.mean([x["I_excess"] for x in a])),
             "rate_I_identified": float(np.mean([x["I_identified"] for x in a]))}
        for kk in keys:
            ex = np.array([x[kk]["excess"] for x in a], float)
            d[kk] = {"mean_excess": float(np.nanmean(ex)), "sd_excess": float(np.nanstd(ex)),
                     "bias": (float(np.nanmean(ex) + c) if not reset else None),
                     "mean_raw": float(np.nanmean([x[kk]["raw"] for x in a])),
                     "rate_within5": float(np.mean(np.abs(ex) <= 0.05)),
                     **{f"rate_fals_{f}": float(np.mean([x[kk]["fals_" + f] for x in a])) for f in ("boot", "comb", "pq")},
                     **{f"rate_excl0_{f}": float(np.mean([x[kk]["excl0_" + f] for x in a])) for f in ("boot", "comb", "pq")}}
        summ[w] = d
    return {"summary": summ, "reps": res, "cost_per_pseudo_s": t_prof, "n_pseudo": n_pseudo, "B": B}


# ------------------------------------------------------------------------------------------------ hubs and ops
def run_hubs(sk, gen, reps):
    out = {}
    events = [e for e in sk.sev["events"] if e["kind"] == "hub_loss"]
    for e in events:
        hub = int(e["agent"])
        t0 = int(C.from_active(np.array([e["a_start"]]))[0])
        t1 = int(C.from_active(np.array([e["a_end"]]))[0])
        res = {"W_hub": [], "W_dist": [], "W_null": []}
        for r in range(reps):
            rng = np.random.default_rng(7000 + r)
            others = [a for a in gen.hosts(rng, 9) if a != hub][:7]
            hosts = list(others) + [hub]
            for name, mult, win, absorb in (("W_hub", 12.0, (t0, t1), False), ("W_dist", 1.5, (t0, t1), True),
                                            ("W_null", 6.0, None, False)):
                wrng = np.random.default_rng(90_000 + r)
                # absorbing world: others' p_on scaled so the expected total is unchanged (set after a dry run)
                h = gen.pattern(wrng, hosts, hub=hub, hub_mult=mult, hub_window=win, absorb=absorb, r0=0.05, d=0.03)
                if absorb:
                    # re-run with absorb multiplier from the dry-run share
                    rb = L.hub_beta(sk, h, e["id"])
                    s = rb["s"] if np.isfinite(rb["s"]) else 0.2
                    gen_mult = 1.0 / max(1e-3, 1 - s)
                    h = _absorb_pattern(gen, np.random.default_rng(90_000 + r), hosts, hub, mult, (t0, t1), gen_mult)
                b = L.hub_beta(sk, h, e["id"])
                bv = L.hub_beta(sk, h, e["id"], same_weekday=False)
                res[name].append({"beta": b["beta"], "s": b["s"], "L": b["L"], "exceeds": b["exceeds_placebo95"],
                                  "beta_allwd": bv["beta"], "exceeds_allwd": bv["exceeds_placebo95"],
                                  "n_placebo": b["n_placebo"], "n_placebo_allwd": bv["n_placebo"]})
        out[e["id"]] = {w: {"mean_beta": float(np.nanmean([x["beta"] for x in v])),
                            "sd_beta": float(np.nanstd([x["beta"] for x in v])),
                            "mean_s": float(np.nanmean([x["s"] for x in v])),
                            "rate_exceeds": float(np.mean([x["exceeds"] for x in v])),
                            "mean_beta_allwd": float(np.nanmean([x["beta_allwd"] for x in v])),
                            "rate_exceeds_allwd": float(np.mean([x["exceeds_allwd"] for x in v])),
                            "n_placebo": v[0]["n_placebo"], "n_placebo_allwd": v[0]["n_placebo_allwd"]}
                        for w, v in res.items()}
        log("hub", e["id"], {w: (round(s["mean_beta"], 2), s["rate_exceeds"]) for w, s in out[e["id"]].items()})
    return out


def _absorb_pattern(gen, rng, hosts, hub, mult, win, gen_mult):
    # same generator, others' emission multiplied by gen_mult inside the window
    import types
    g = gen
    h = g.pattern(rng, hosts, hub=hub, hub_mult=mult, hub_window=win, absorb=True, r0=0.05, d=0.03)
    # emulate absorption by scaling: regenerate with scale_after for non-hub agents is not separable in pattern();
    # instead add extra hits for the others inside the window at the expected missing rate
    m_in = (h.t >= win[0]) & (h.t < win[1]) & (h.agent != hub)
    extra = rng.random(m_in.sum()) < (gen_mult - 1.0)
    idx = np.flatnonzero(m_in)[extra]
    if len(idx):
        t = np.r_[h.t, h.t[idx] + 1]
        return L.Hits(np.r_[h.agent, h.agent[idx]], t, np.r_[h.e, h.e[idx]], np.r_[h.bin, h.bin[idx]])
    _ = types
    return h


def run_ops(sk, gen, reps):
    out = {}
    events = [e for e in sk.sev["events"] if e["kind"] == "operator"]
    for e in events:
        t0 = int(C.from_active(np.array([e["a_start"]]))[0])
        t1 = int(C.from_active(np.array([e["a_end"]]))[0])
        res = {"W_op20": [], "W_null": []}
        for r in range(reps):
            rng = np.random.default_rng(3000 + r)
            hosts = gen.hosts(rng, 10)
            for name, sc in (("W_op20", (t0, t1, 0.8)), ("W_null", None)):
                h = gen.pattern(np.random.default_rng(40_000 + r), hosts, scale_after=sc, r0=0.05, d=0.03)
                p = L.prevalence_change(sk, h, e["id"])
                pv = L.prevalence_change(sk, h, e["id"], same_weekday=False)
                res[name].append({"rel": p["rel_change"], "net": p["net"], "exceeds": p["exceeds_placebo95"],
                                  "net_allwd": pv["net"], "exceeds_allwd": pv["exceeds_placebo95"],
                                  "le20": bool(p["net"] <= -0.20)})
        out[e["id"]] = {w: {"mean_net": float(np.nanmean([x["net"] for x in v])),
                            "sd_net": float(np.nanstd([x["net"] for x in v])),
                            "rate_exceeds": float(np.mean([x["exceeds"] for x in v])),
                            "rate_exceeds_allwd": float(np.mean([x["exceeds_allwd"] for x in v])),
                            "rate_le20": float(np.mean([x["le20"] for x in v]))} for w, v in res.items()}
        log("op", e["id"], {w: (round(s["mean_net"], 3), s["rate_exceeds"]) for w, s in out[e["id"]].items()})
    return out


# ------------------------------------------------------------------------------------------------ hosts
def plant_commits(hp: L.HostPanel, host_ab, delta, rng):
    h = host_ab[hp.ai, hp.bin]
    c = hp.commits.astype(np.int64)
    out = c.copy()
    if delta < 0:
        out[h] = rng.binomial(c[h], 1 + delta)
    elif delta > 0:
        out[~h] = rng.binomial(c[~h], 1 / (1 + delta))
    return out.astype(float)


def run_hosts(sk, gen, reps, n_pseudo=20, B=100):
    """Host relation: forms A2 (activity held, primary) and card (no activity covariates); raw within-agent estimate
    with its cluster-bootstrap CI, and the excess over the pseudo-pattern median."""
    hp = L.HostPanel(sk)
    deltas = [-0.2, -0.1, 0.0, 0.1, 0.2]
    forms = (("A2", True), ("card", False))
    res = {d: [] for d in deltas}
    base_commits = hp.commits.copy()
    base_align = {k: v.copy() for k, v in hp.align.items()}
    for r in range(reps):
        rng = np.random.default_rng(5000 + r)
        nh = int(rng.choice([5, 8, 12]))
        hosts = gen.hosts(rng, nh)
        h = gen.pattern(np.random.default_rng(60_000 + r), hosts)
        HA = L.host_matrix(sk, h)
        pseudo = []
        for k in range(n_pseudo):
            prng = np.random.default_rng(600_000 + r * 100 + k)
            pseudo.append(L.host_matrix(sk, gen.pattern(prng, gen.hosts(prng, nh))))
        for d in deltas:
            prng = np.random.default_rng(r * 10 + int((d + 1) * 100))
            hp.commits = base_commits.copy()
            hp.commits = plant_commits(hp, HA, d, prng)
            hmask = HA[hp.ai, hp.bin]
            for k_, v in base_align.items():
                base = np.nanmean(v[~hmask])
                hp.align[k_] = v + np.where(hmask, d * base, 0.0)
            row = {"rep": r, "n_hosts": nh}
            for fname, act in forms:
                est = L.host_fit(hp, HA, activity=act)
                ps = [L.host_fit(hp, P, activity=act, outcomes=("commits", "align_bge")) for P in pseudo]
                pmed = {o: float(np.nanmedian([p[o] for p in ps])) for o in ("commits", "align_bge")}
                bt = L.host_boot(hp, HA, B=B, seed=r, outcomes=("commits", "align_bge"), activity=act)
                ci_c = L.q(bt["commits"])
                ci_a = L.q(bt["align_bge"])
                exc_c = (1 + est["commits"]) / (1 + pmed["commits"]) - 1
                eci_c = [float((1 + x) / (1 + pmed["commits"]) - 1) for x in ci_c]
                exc_a = est["align_bge"] - pmed["align_bge"]
                eci_a = [float(x - pmed["align_bge"]) for x in ci_a]
                row[fname] = {"n_host_bins": est["n_host_bins"], "raw_c": est["commits"], "ci_c": ci_c,
                              "raw_a": est["align_bge"], "ci_a": ci_a, "exc_c": float(exc_c), "eci_c": eci_c,
                              "exc_a": float(exc_a), "eci_a": eci_a, "pmed_c": pmed["commits"],
                              "class_raw": L.classify(est["commits"], est["align_bge"], ci_c, ci_a),
                              "class_exc": L.classify(exc_c, exc_a, eci_c, eci_a),
                              "c_excl0_raw": bool(np.isfinite(ci_c[0]) and (ci_c[0] > 0 or ci_c[1] < 0)),
                              "c_excl0_exc": bool(np.isfinite(eci_c[0]) and (eci_c[0] > 0 or eci_c[1] < 0)),
                              "c_beyond5_raw": bool(np.isfinite(ci_c[0]) and (ci_c[0] > 0.05 or ci_c[1] < -0.05))}
            res[d].append(row)
        hp.commits = base_commits.copy()
        hp.align = {k: v.copy() for k, v in base_align.items()}
        log(f"hosts rep {r}: " + ", ".join(f"{d:+.1f}: A2 {res[d][-1]['A2']['raw_c']:+.3f} ({res[d][-1]['A2']['class_raw']})"
                                           f" card {res[d][-1]['card']['raw_c']:+.3f}" for d in deltas))
    summ = {}
    for d in deltas:
        a = res[d]
        sd = {"planted": d, "reps": len(a)}
        for fname, _ in forms:
            x = [z[fname] for z in a]
            sd[fname] = {
                "median_host_bins": float(np.median([z["n_host_bins"] for z in x])),
                "mean_raw_c": float(np.nanmean([z["raw_c"] for z in x])), "sd_raw_c": float(np.nanstd([z["raw_c"] for z in x])),
                "mean_exc_c": float(np.nanmean([z["exc_c"] for z in x])), "sd_exc_c": float(np.nanstd([z["exc_c"] for z in x])),
                "mean_raw_a": float(np.nanmean([z["raw_a"] for z in x])), "mean_exc_a": float(np.nanmean([z["exc_a"] for z in x])),
                "n_nan_c": int(np.sum(~np.isfinite([z["raw_c"] for z in x]))),
                "rate_c_excl0_raw": float(np.mean([z["c_excl0_raw"] for z in x])),
                "rate_c_excl0_exc": float(np.mean([z["c_excl0_exc"] for z in x])),
                "rate_c_beyond5_raw": float(np.mean([z["c_beyond5_raw"] for z in x])),
                "class_raw": {c: float(np.mean([z["class_raw"] == c for z in x])) for c in ("mutualist", "parasitic", "neutral")},
                "class_exc": {c: float(np.mean([z["class_exc"] == c for z in x])) for c in ("mutualist", "parasitic", "neutral")}}
        summ[str(d)] = sd
    return {"summary": summ, "reps": {str(k): v for k, v in res.items()}, "n_pseudo": n_pseudo, "B": B}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--part", default="all")
    ap.add_argument("--pseudo", type=int, default=20)
    ap.add_argument("--B", type=int, default=100)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    sk = L.load_skeleton()
    gen = Gen(sk)
    L.set_base(sk, gen.a, gen.t)          # synthetic: every statement is an element event
    log("skeleton:", len(gen.t), "statements;", sk.ev.height, "events")
    parts = ["hubs", "ops", "hosts", "wipes"] if a.part == "all" else a.part.split(",")
    for p in parts:
        t1 = time.time()
        if p == "wipes":
            r = run_wipes(sk, gen, a.reps, n_pseudo=a.pseudo, B=a.B)
        elif p == "hubs":
            r = run_hubs(sk, gen, a.reps)
        elif p == "ops":
            r = run_ops(sk, gen, a.reps)
        elif p == "hosts":
            r = run_hosts(sk, gen, a.reps, n_pseudo=a.pseudo, B=a.B)
        r = {"part": p, "runtime_s": time.time() - t1, "reps": a.reps, "result": r} if p in ("hubs", "ops") else \
            {"part": p, "runtime_s": time.time() - t1, **r}
        (OUT / f"{p}.json").write_text(json.dumps(r, indent=1, default=float))
        log(p, "done", f"{time.time() - t1:.0f}s")


if __name__ == "__main__":
    main()
