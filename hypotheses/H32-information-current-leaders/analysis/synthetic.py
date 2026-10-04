"""H32 synthetic validation (axis F): the full pipeline on synthetic content generated on real message skeletons.

Skeletons (times, speakers, rooms, days, exposure, intentions timing) from #26 (1 room, 10 agents, 5 days),
#13 (1 room, 6 agents, 10 days) and #44 (2 rooms, 17 agents, 4 days). Content (dim 32), per chat message of agent j:
    v = a_own e_j + a_g g0 + a_f phi_{d,r} + a_s h_j + sum_i kappa_ij S_ij(t) + kappa_H S_Hj(t) + a_D D_j(t) + sigma xi
    u = unit(v);  e_j <- (1 - lam) e_j + lam u
S_ij = decayed sum (tau = 15 min, same day) of i's earlier messages that j had seen (room rule); D_j(t) = a latent
piecewise-constant drive direction (switches ~ every 45 active min) that the fast responder F follows at once and
everyone else 20 min later. Humans' and automated messages: unit(0.3 g0 + noise). Intentions: unit(e_j + noise).

Scenarios: S0 null; S1 one leader at three strengths; S2 fast responder only; S3 leader + fast responder;
S4 distributed (all pairs); S5 human source only. Calibration (nuisance only, no transfer statistic): the
within-agent consecutive cosine and the cross-agent same day x room cosine of field-removed vectors, matched to the
real skeleton periods (`calibrate`).

Usage: uv run python hypotheses/H32-information-current-leaders/analysis/synthetic.py [calibrate|run|summarize]
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ["_" + _v] = "1"
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import warnings  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ic_core as C  # noqa: E402

warnings.filterwarnings("ignore", category=RuntimeWarning)
OUTD = C.DATA / "synthetic"
SKELS = [26, 13, 44]
BASE = dict(a_own=1.0, a_g=0.6, a_f=0.5, a_s=0.5, sigma=1.6, lam=0.25)
N_REP = 10
N_NULL = 20


def nuisance_stats(sk: C.Skeleton):
    """Within-agent consecutive cosine and cross-agent same day x room cosine of the (field-removed) vectors."""
    z = C.unit(sk.z)
    ag = sk.spk < 100
    w = []
    for a in sk.agents:
        idx = np.flatnonzero(sk.spk == a)
        if len(idx) > 2:
            w.append(np.mean(np.sum(z[idx[1:]] * z[idx[:-1]], 1)))
    cross = []
    key = sk.day.astype(np.int64) * 100 + sk.room
    rng = np.random.default_rng(0)
    for k in np.unique(key[ag]):
        idx = np.flatnonzero(ag & (key == k))
        if len(idx) < 4:
            continue
        a = rng.choice(idx, 400); b = rng.choice(idx, 400)
        m = sk.spk[a] != sk.spk[b]
        cross.append(np.mean(np.sum(z[a[m]] * z[b[m]], 1)))
    return {"within": float(np.mean(w)), "cross": float(np.mean(cross))}


def generate(sk: C.Skeleton, rng, prm: dict, leaders=(), kappa=0.0, kappa_dist=0.0, fast=None, a_D=0.0, kappa_H=0.0,
             L_s=1200.0, switch_s=2700.0):
    d = sk.z.shape[1]
    agents = [int(a) for a in sk.agents]
    aidx = {a: k for k, a in enumerate(agents)}
    g0 = C.unit(rng.standard_normal(d))
    hsty = {a: C.unit(rng.standard_normal(d)) for a in agents}
    phi = {}
    # latent drive: switch times in active time
    n_sw = int(sk.a_total / switch_s * 3) + 5
    sw = np.cumsum(rng.exponential(switch_s, n_sw)); dirs = C.unit(rng.standard_normal((n_sw + 1, d)))

    def drive(a_t):
        return dirs[np.searchsorted(sw, a_t)]
    R = C.exposure_matrix(sk, sk.t, sk.room, np.array(agents))
    tau = C.P["tau"]; win = C.P["win_mult"] * tau
    z = np.zeros_like(sk.z)
    e = {a: np.zeros(d) for a in agents}
    lam = prm["lam"]
    # merge chat and intentions in time order
    order = sorted([(t, 0, k) for k, t in enumerate(sk.t)] + [(t, 1, k) for k, t in enumerate(sk.it_t)])
    itz = np.zeros_like(sk.it_z)
    psi_l, psi_d = [], []
    leaders = set(int(x) for x in leaders)
    for t, kind, k in order:
        if kind == 1:
            a = int(sk.it_spk[k])
            itz[k] = C.unit(e.get(a, np.zeros(d)) + 0.5 * rng.standard_normal(d) / np.sqrt(d))
            continue
        j = int(sk.spk[k])
        if j >= 100:
            z[k] = C.unit(0.3 * g0 + rng.standard_normal(d) / np.sqrt(d))
            continue
        dd, rr = int(sk.day[k]), int(sk.room[k])
        if (dd, rr) not in phi:
            phi[(dd, rr)] = C.unit(rng.standard_normal(d))
        v = prm["a_own"] * e[j] + prm["a_g"] * g0 + prm["a_f"] * phi[(dd, rr)] + prm["a_s"] * hsty[j] \
            + prm["sigma"] * rng.standard_normal(d) / np.sqrt(d)
        coup = np.zeros(d); lead = np.zeros(d)
        if leaders or kappa_dist or kappa_H:
            lo = np.searchsorted(sk.t, t - win); x = np.arange(lo, k)
            x = x[(sk.day[x] == dd) & (sk.spk[x] != j)]
            if len(x):
                hum = sk.spk[x] >= 100
                seen = np.zeros(len(x), bool)
                seen[~hum] = R[x[~hum], aidx[j]] == 1
                seen[hum] = R[x[hum], aidx[j]] == 1
                w = np.exp(-(t - sk.t[x]) / tau)
                for xi, wi, si in zip(x, w, seen):
                    if not si:
                        continue
                    s = int(sk.spk[xi])
                    if s in leaders:
                        lead += kappa * wi * z[xi]
                    elif s < 100 and kappa_dist:
                        coup += kappa_dist * wi * z[xi]
                    elif s >= 100 and kappa_H and s == C.HUMAN:
                        coup += kappa_H * wi * z[xi]
        dr = np.zeros(d)
        if fast is not None and a_D:
            at = sk.a[k]
            dr = a_D * (drive(at) if j == fast else drive(at - L_s))
        v = v + coup + lead + dr
        if j not in leaders and np.any(lead):
            psi_l.append(lead @ lead / (v @ v))
        if np.any(dr):
            psi_d.append(dr @ dr / (v @ v))
        z[k] = C.unit(v)
        e[j] = (1 - lam) * e[j] + lam * z[k]
    return z, itz, g0, {"psi_leader": float(np.mean(psi_l)) if psi_l else 0.0,
                        "psi_drive": float(np.mean(psi_d)) if psi_d else 0.0}


def project(sk: C.Skeleton, z, itz, g0, rng, K=None):
    K = C.P["K_field"] if K is None else K
    ag = sk.spk < 100
    fields = {"white": (g0 + 0.3 * rng.standard_normal(len(g0)) / np.sqrt(len(g0)))[None, :], "kind": np.array([0])}
    Q = C.field_basis(sk.goal_no, "I", z[ag], sk.day[ag], sk.room[ag], K, z.shape[1], fields)
    return sk.with_z(z - (z @ Q) @ Q.T, itz - (itz @ Q) @ Q.T)


def pick_agents(sk: C.Skeleton, room=None):
    cnt = {int(a): int((sk.spk == a).sum()) for a in sk.agents}
    ok = [a for a in cnt if cnt[a] >= 40]
    if room is not None:
        ok = [a for a in ok if np.any(sk.room[sk.spk == a] == room)]
    s = sorted(ok, key=lambda a: cnt[a])
    return s[len(s) // 2], s[max(0, len(s) // 2 - 1)], cnt   # median-count agent (leader), next lower (fast responder)


def calibrate():
    out = {}
    for g in SKELS:
        sk = C.load_period(g)
        real = nuisance_stats(sk)
        rng = np.random.default_rng(1)
        res = []
        for sigma in (1.0, 1.4, 1.8, 2.4):
            for a_own in (0.6, 1.0, 1.5):
                prm = dict(BASE, sigma=sigma, a_own=a_own)
                z, itz, g0, _ = generate(sk, rng, prm)
                s = nuisance_stats(project(sk, z, itz, g0, rng))
                res.append({"sigma": sigma, "a_own": a_own, **s,
                            "err": (s["within"] - real["within"]) ** 2 + (s["cross"] - real["cross"]) ** 2})
        best = min(res, key=lambda r: r["err"])
        out[g] = {"real": real, "best": best, "grid": res}
        print(g, "real", real, "best", best, flush=True)
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / "calibration.json").write_text(json.dumps(out, indent=1))


def kappa_for(sk, prm, leader, target_psi, rng):
    """Find kappa giving the target leader share of followers' variance (two-step power-law fit)."""
    k = 0.2
    for _ in range(3):
        _, _, _, info = generate(sk, rng, prm, leaders=[leader], kappa=k)
        p = max(info["psi_leader"], 1e-6)
        k = k * np.sqrt(target_psi / p)
    return float(k)


def one_run(args):
    g, scen, rep, prm, kap, adrive, kd, kh = args
    sk = C.load_period(g)
    rng = np.random.default_rng(C.SEED + 1000 * g + 17 * rep + hash(scen) % 997)
    two_room = len(sk.meta["rooms_populated"]) >= 2
    room_l = 3 if g == 44 else None
    L, F, cnt = pick_agents(sk, room=room_l)
    kw = {}
    if scen.startswith("S1") or scen == "S3":
        kw.update(leaders=[L], kappa=kap)
    if scen in ("S2", "S3"):
        kw.update(fast=F, a_D=adrive)
    if scen == "S4":
        kw.update(kappa_dist=kd)
    if scen == "S5":
        kw.update(kappa_H=kh)
    z, itz, g0, info = generate(sk, rng, prm, **kw)
    sk2 = project(sk, z, itz, g0, rng)
    modes = ("seen", "seen_beyond_unseen", "unseen") if two_room else ("seen",)
    r = C.run_unit(sk2, n_null=N_NULL, seed=C.SEED + rep, modes=modes, do_human=True, n_withinday=N_NULL)
    nodes = r["nodes"]
    out = np.nan_to_num(r["out"], nan=-np.inf); net = np.nan_to_num(r["net"], nan=-np.inf)
    rank = lambda v, a: int(1 + np.sum(v > v[nodes.index(a)])) if a in nodes else None
    top = nodes[int(np.argmax(out))]
    ident = (r["cent"]["pQ"] < 0.05) and (np.nanmax(r["z_out"]) >= 2)
    rec = {"g": g, "scen": scen, "rep": rep, "N": len(nodes), "leader": L, "fast": F, **info,
           "T": r["T"], "p_T": r["p_T"], "top": top, "identified": bool(ident), "z_top": float(np.nanmax(r["z_out"])),
           "rank_L_out": rank(out, L), "rank_L_net": rank(net, L), "rank_F_out": rank(out, F), "rank_F_net": rank(net, F),
           "top_net": nodes[int(np.argmax(net))], **{f"cent_{k}": v for k, v in r["cent"].items()},
           "human_out": r.get("human", {}).get("out"), "human_z": r.get("human", {}).get("z"), "human_p": r.get("human", {}).get("p"),
           "human_rank": int(1 + np.sum(out > r.get("human", {}).get("out", np.inf))) if "human" in r else None,
           "count_rank_L": int(1 + sum(cnt[a] > cnt[L] for a in cnt)),
           "count_rank_top": int(1 + sum(cnt[a] > cnt.get(top, 0) for a in cnt)),
           "p_standout": r["p_standout"], "p_max": r["p_max"], "standout": r["standout"],
           "phi_nullvar": r["cent_nullvar"]["phi"], "pQ_nullvar": r["cent_nullvar"]["pQ"],
           "ident_v1": bool(r["p_max"] < 0.05 and r["p_standout"] < 0.05),
           "p_T_wd": r["withinday"]["p_T"], "T_wd": r["withinday"]["T"],
           "ident_wd": bool(r["withinday"]["p_max"] < 0.05 and r["withinday"]["p_standout"] < 0.05),
           "rank_L_out_wd": rank(np.nan_to_num(r["withinday"]["out"], nan=-np.inf), L)}
    if two_room:
        ix = {a: k for k, a in enumerate(nodes)}
        for m in ("seen_beyond_unseen", "unseen"):
            rec[f"T_{m}"] = r[f"T_{m}"]; rec[f"p_T_{m}"] = r[f"p_T_{m}"]
            if F in ix:
                rec[f"F_out_{m}"] = float(np.nanmean(r[f"dG_{m}"][ix[F]]))
            if L in ix:
                rec[f"L_out_{m}"] = float(np.nanmean(r[f"dG_{m}"][ix[L]]))
        rec["L_out_seen"] = float(r["out"][ix[L]]) if L in ix else None
        rec["F_out_seen"] = float(r["out"][ix[F]]) if F in ix else None
    return rec


def run():
    cal = json.loads((OUTD / "calibration.json").read_text())
    jobs = []
    meta = {}
    for g in SKELS:
        b = cal[str(g)]["best"]
        prm = dict(BASE, sigma=b["sigma"], a_own=b["a_own"])
        sk = C.load_period(g)
        rng = np.random.default_rng(5)
        L, F, _ = pick_agents(sk, room=3 if g == 44 else None)
        ks = {p: kappa_for(sk, prm, L, p, rng) for p in (0.005, 0.02, 0.05)}
        # drive strength: ~5% of variance; distributed: same total coupling as S1-mid spread over N-1 senders
        adrive = 0.55 * prm["sigma"] / np.sqrt(1.0)
        kd = ks[0.02] / np.sqrt(max(len(sk.agents) - 1, 1))
        kh = ks[0.05]
        meta[g] = {"prm": prm, "kappa": ks, "a_D": adrive, "kappa_dist": kd, "kappa_H": kh, "leader": L, "fast": F}
        for rep in range(N_REP):
            for scen, kap in (("S0", 0), ("S1a", ks[0.005]), ("S1b", ks[0.02]), ("S1c", ks[0.05]), ("S2", 0), ("S3", ks[0.02]),
                              ("S4", 0), ("S5", 0)):
                jobs.append((g, scen, rep, prm, kap, adrive, kd, kh))
    print("jobs", len(jobs), meta, flush=True)
    t0 = time.time()
    recs = []
    with Pool(2) as pool:
        for k, rec in enumerate(pool.imap_unordered(one_run, jobs)):
            recs.append(rec)
            if k % 20 == 0:
                print(k, f"{time.time() - t0:.0f}s", rec["g"], rec["scen"], rec["rank_L_out"], rec["identified"], flush=True)
                (OUTD / "synthetic_runs.json").write_text(json.dumps({"meta": meta, "runs": recs}, default=float))
    (OUTD / "synthetic_runs.json").write_text(json.dumps({"meta": meta, "runs": recs}, default=float))
    print("done", f"{time.time() - t0:.0f}s")


def summarize():
    d = json.loads((OUTD / "synthetic_runs.json").read_text())
    runs = d["runs"]
    import collections
    rows = collections.defaultdict(list)
    for r in runs:
        rows[(r["g"], r["scen"])].append(r)
    summ = {}
    for (g, s), rs in sorted(rows.items()):
        f = lambda k: [x[k] for x in rs if x.get(k) is not None]
        e = {"n": len(rs), "psi_leader": float(np.mean(f("psi_leader"))), "psi_drive": float(np.mean(f("psi_drive"))),
             "p_T<0.05": float(np.mean([x["p_T"] < 0.05 for x in rs])), "T_mean": float(np.mean(f("T"))),
             "identified": float(np.mean(f("identified"))),
             "top1_L_out": float(np.mean([x["rank_L_out"] == 1 for x in rs])),
             "top1_L_net": float(np.mean([x["rank_L_net"] == 1 for x in rs])),
             "rank_L_out_median": float(np.median(f("rank_L_out"))),
             "top1_F_out": float(np.mean([x["rank_F_out"] == 1 for x in rs])),
             "phi_median": float(np.nanmedian(f("cent_phi"))), "gini_median": float(np.nanmedian(f("cent_gini"))),
             "pQ<0.05": float(np.mean([x["cent_pQ"] < 0.05 for x in rs])),
             "human_rank1": float(np.mean([x["human_rank"] == 1 for x in rs if x["human_rank"] is not None])),
             "human_p<0.05": float(np.mean([x["human_p"] < 0.05 for x in rs if x["human_p"] is not None])),
             "N": rs[0]["N"],
             "ident_v1": float(np.mean([x.get("ident_v1", False) for x in rs])),
             "p_standout<0.05": float(np.mean([x["p_standout"] < 0.05 for x in rs if x.get("p_standout") is not None])),
             "p_max<0.05": float(np.mean([x["p_max"] < 0.05 for x in rs if x.get("p_max") is not None])),
             "phi_nullvar_median": float(np.nanmedian(f("phi_nullvar"))) if f("phi_nullvar") else None,
             "phi_nullvar_iqr": np.nanquantile(f("phi_nullvar"), [0.25, 0.75]).tolist() if f("phi_nullvar") else None,
             "top_is_most_talkative": float(np.mean([x.get("count_rank_top") == 1 for x in rs])),
             "top1_F_net": float(np.mean([x["rank_F_net"] == 1 for x in rs])),
             "p_T_wd<0.05": float(np.mean([x["p_T_wd"] < 0.05 for x in rs if x.get("p_T_wd") is not None])),
             "ident_wd": float(np.mean([x.get("ident_wd", False) for x in rs])),
             "p_T<0.05_both": float(np.mean([(x["p_T"] < 0.05) and (x.get("p_T_wd", 1) < 0.05) for x in rs]))}
        if "T_unseen" in rs[0]:
            e.update({"T_seen_beyond_unseen": float(np.mean(f("T_seen_beyond_unseen"))), "T_unseen": float(np.mean(f("T_unseen"))),
                      "p_unseen<0.05": float(np.mean([x["p_T_unseen"] < 0.05 for x in rs])),
                      "p_sbu<0.05": float(np.mean([x["p_T_seen_beyond_unseen"] < 0.05 for x in rs])),
                      "F_out_unseen": float(np.nanmean(f("F_out_unseen"))) if f("F_out_unseen") else None,
                      "F_out_seen": float(np.nanmean(f("F_out_seen"))) if f("F_out_seen") else None,
                      "L_out_unseen": float(np.nanmean(f("L_out_unseen"))) if f("L_out_unseen") else None,
                      "L_out_seen": float(np.nanmean(f("L_out_seen"))) if f("L_out_seen") else None})
        summ[f"G{g}_{s}"] = e
        print(f"G{g} {s}", json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in e.items()}))
    (OUTD / "synthetic_summary.json").write_text(json.dumps({"meta": d["meta"], "summary": summ}, indent=1, default=float))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"  # noqa
    {"calibrate": calibrate, "run": run, "summarize": summarize}[cmd]()
