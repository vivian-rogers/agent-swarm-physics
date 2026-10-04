"""H54 synthetic validation (axis F), run before any real-data statistic along a kickoff/goal/plan direction.

Vector-spin swarms in the real 32-d whitened geometry (per-regime covariance from calibrate.py), at village sampling
(real eligible periods, day-1 agent counts, per-agent statement counts, kickoff chunk counts, previous-period availability).

Generative model for period p (regime r), agent i:
  day-1 state      x_i = sqrt(f) t_p + sqrt((1-f) ra) a_i + sqrt((1-f) re) e_i, then herding x_i <- x_i + J mean(x)
                   (t_p target, a_i persistent agent offset shared across periods, e_i idiosyncratic; ra, re from the
                   regime's later-day persistence and pairwise alignment)
  previous day     x_i^prev = sqrt(fl) t_{p-1} + ... (fl = regime's later-day pairwise alignment)
  statements       z = unit(unit(x_i) + tau eps), eps ~ N(0, Sigma_r) scaled to unit mean norm
  kickoff text     k_p = unit(c_k t_p + sqrt(1-c_k^2) xi_p + gamma_p u_gen), gamma_p = gamma0 * chunks_p / mean(chunks)
                   (u_gen = the direction every centroid shares: mean agent offset; long kickoffs look generic)
Truths: H54 (target = t_p), R0 (the swarm's shared topic is independent of the kickoff), R1 (inertia: shared topic = t_{p-1}).
Checks S1 (target identification), S2 (spread vs specificity), S3 (Potts naming layer and the counting artifact),
S4 (#51 role swap), S5 (#44 room swap). Output: data/processed/H54-kickoff-quench-target/synthetic/results.json
Usage: uv run python synthetic.py [--reps 200]
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import polars as pl

import h54est as E
import h54lib as L

TAU = 1.3


def real_structure():
    st, _, _ = L.load_stmt()
    d1 = st.filter((pl.col("day") == 1) & ~pl.col("pre_kick"))
    cnt = d1.group_by("goal_no", "agent").len().filter(pl.col("len") >= L.N_MIN)
    g = L.goals().filter(pl.col("kind") == "kickoff")
    chunks = dict(zip(g["goal_no"].to_list(), g["n_chunks"].to_list()))
    prev = set(st.filter(pl.col("day") == 0)["goal_no"].unique().to_list())
    ko = pl.read_parquet(L.OUT / "kickoffs.parquet").filter(pl.col("room").is_null())
    spec = dict(zip(ko["goal_no"].to_list(), ko["S_text"].to_list()))
    specc = dict(zip(ko["goal_no"].to_list(), ko["S_count"].to_list()))
    out = []
    for p in L.eligible():
        ns = cnt.filter(pl.col("goal_no") == p)["len"].to_list()
        out.append({"p": p, "reg": L.period_regime(p), "ns": ns, "chunks": chunks[p], "prev": p in prev,
                    "S_text": spec[p], "S_count": specc[p]})
    return out


class World:
    def __init__(self, cal, rng):
        self.rng = rng
        self.Lc = {}
        self.ratio = {}
        for r in ("I", "II", "III"):
            C = np.load(L.OUT / "synthetic" / f"spectrum_{r}.npy")
            C = C / np.trace(C)
            w, U = np.linalg.eigh(C)
            self.Lc[r] = U * np.sqrt(np.clip(w, 0, None))
            q, pe = cal[r]["q_later_median"], cal[r]["persist_median"]
            fa = max(pe - q, 0.02)
            fe = max(1 - pe, 0.02)
            self.ratio[r] = (fa / (fa + fe), fe / (fa + fe), max(q, 0.02))

    def draw(self, r, n=1):
        x = self.rng.standard_normal((n, L.D)) @ self.Lc[r].T
        return E.unit(x)

    def noise(self, r, n):
        x = self.rng.standard_normal((n, L.D)) @ self.Lc[r].T
        return x * np.sqrt(L.D) / np.sqrt(L.D)  # trace-normalized: E|x|^2 = 1


def simulate(struct, cal, f, ck, gamma0, J, truth, rng, pool=46):
    W = World(cal, rng)
    P = len(struct)
    A = {r: W.draw(r, pool) for r in ("I", "II", "III")}
    ugen = {r: E.unit(A[r].mean(0)) for r in A}
    T = {s["p"]: W.draw(s["reg"])[0] for s in struct}
    Tsh = {s["p"]: W.draw(s["reg"])[0] for s in struct}      # R0: an unrelated shared topic
    mchunk = np.mean([s["chunks"] for s in struct])
    K = np.zeros((P, L.D))
    cents, prevc, groups, depthrows = [], [], [], []
    plist = [s["p"] for s in struct]
    for k, s in enumerate(struct):
        r, p = s["reg"], s["p"]
        xi = W.draw(r)[0]
        K[k] = E.unit(ck * T[p] + np.sqrt(1 - ck ** 2) * xi + gamma0 * (s["chunks"] / mchunk) * ugen[r])
        ra, re, fl = W.ratio[r]
        tgt = T[p] if truth == "H54" else (Tsh[p] if truth == "R0" else T.get(p - 1, Tsh[p]))
        N = len(s["ns"])
        start = (k * 2) % (pool - N) if pool > N else 0
        ai = A[r][start:start + N]
        e = W.draw(r, N)
        x = np.sqrt(f) * tgt + np.sqrt((1 - f) * ra) * ai + np.sqrt((1 - f) * re) * e
        x = E.unit(x + J * x.mean(0))
        g = []
        for i, n in enumerate(s["ns"]):
            z = E.unit(x[i] + TAU * W.noise(r, n))
            g.append(z)
        groups.append(g)
        V = np.vstack([E.unit(z.mean(0)) for z in g])
        cents.append(V.mean(0))
        depthrows.append(V)
        if s["prev"]:
            tp = T.get(p - 1, Tsh[p])
            xp = E.unit(np.sqrt(fl) * tp + np.sqrt((1 - fl) * ra) * ai + np.sqrt((1 - fl) * re) * W.draw(r, N))
            Vp = np.vstack([E.unit(E.unit(xp[i] + TAU * W.noise(r, n)).mean(0)) for i, n in enumerate(s["ns"])])
            prevc.append(Vp.mean(0))
        else:
            prevc.append(None)
    C = np.vstack([E.unit(c) for c in cents])
    S = C @ K.T
    Sh = E.colcenter(S)
    disp = np.full((P, P), np.nan)
    for k in range(P):
        if prevc[k] is not None:
            disp[k] = E.unit(cents[k] - prevc[k]) @ K.T
    Dex = np.array([np.mean(depthrows[k] @ K[k]) - np.mean(depthrows[k] @ np.delete(K, k, 0).T) for k in range(P)])
    Draw = np.array([np.mean(depthrows[k] @ K[k]) for k in range(P)])
    return {"S": S, "Sh": Sh, "disp": disp, "groups": groups, "Dex": Dex, "Draw": Draw, "plist": plist}


def s1_s2(struct, cal, reps, rng):
    res = {}
    spec = np.array([s["S_text"] for s in struct])
    specc = np.array([s["S_count"] for s in struct])
    chunks = np.array([s["chunks"] for s in struct], float)
    cells = [("H54", f, ck, 0.5, 0.3) for f in (0.05, 0.15, 0.3) for ck in (0.3, 0.5, 0.7)]
    cells += [("R0", 0.15, 0.5, g, 0.3) for g in (0.0, 0.5)] + [("R1", 0.15, 0.5, 0.5, 0.3), ("H54", 0.15, 0.5, 0.0, 0.3),
                                                                ("H54", 0.15, 0.5, 0.5, 0.0)]
    for truth, f, ck, g0, J in cells:
        key = f"{truth}_f{f}_ck{ck}_g{g0}_J{J}"
        rows = []
        for _ in range(reps):
            o = simulate(struct, cal, f, ck, g0, J, truth, rng)
            pi_raw = E.own_percentiles(o["S"])
            pi = E.own_percentiles(o["Sh"])
            t1 = E.top1(o["Sh"])
            v = E.p1_verdict(pi, t1)
            pid = E.own_percentiles(o["disp"])
            q = np.array([E.rarefied_q(gg, 5, 10, rng) for gg in o["groups"]])
            sig = 1 - q
            rs_null, ps_null, _ = E.spearman(spec, sig, "less")
            rd_raw, _, _ = E.spearman(specc, np.diag(o["S"]))
            rd_cc, _, _ = E.spearman(specc, np.diag(o["Sh"]))
            rc_raw, _, _ = E.spearman(chunks, np.diag(o["S"]))
            rc_cc, _, _ = E.spearman(chunks, np.diag(o["Sh"]))
            nN = np.array([len(gg) for gg in o["groups"]])
            nmed = np.array([np.median([len(z) for z in gg]) for gg in o["groups"]])
            rN, _, _ = E.spearman(nN, sig)
            rn, _, _ = E.spearman(nmed, sig)
            rows.append([v["median_pi"], v["top1"], v["p_wilcoxon"], float(v["verdict"] == "supported"),
                         float(np.nanmedian(pi_raw)), float(np.nanmedian(pid)), float(np.nanmean(q)),
                         float(ps_null < 0.05), rd_raw, rd_cc, rc_raw, rc_cc, rN, rn])
        a = np.array(rows, float)
        cols = ["median_pi", "top1", "p_wilcoxon", "P1_pass", "median_pi_raw", "median_pi_disp", "q_day1", "spread_spec_FP",
                "rho_Scount_Sraw", "rho_Scount_Scc", "rho_chunks_Sraw", "rho_chunks_Scc", "rho_N_spread", "rho_n_spread"]
        res[key] = {c: float(np.nanmedian(a[:, j])) for j, c in enumerate(cols)}
        res[key]["P1_pass_rate"] = float(np.nanmean(a[:, 3]))
        res[key]["spread_spec_FP_rate"] = float(np.nanmean(a[:, 7]))
        res[key]["rho_chunks_Sraw_q90"] = float(np.nanpercentile(a[:, 10], 90))
        res[key]["rho_chunks_Scc_q90"] = float(np.nanpercentile(a[:, 11], 90))
        print(key, {k: round(v, 3) for k, v in res[key].items()})
    # S2 power: day-1 target share rises with specificity
    pw = {}
    for b in (0.3, 0.6):
        hits = []
        for _ in range(max(60, reps // 2)):
            fs = np.clip(0.15 * np.exp(b * spec), 0.01, 0.8)
            qs = []
            for k, s in enumerate(struct):
                o = simulate([s], cal, float(fs[k]), 0.5, 0.5, 0.3, "H54", rng)
                qs.append(E.rarefied_q(o["groups"][0], 5, 10, rng))
            rho, p, _ = E.spearman(spec, 1 - np.array(qs), "less")
            hits.append([rho, p < 0.05])
        h = np.array(hits, float)
        pw[f"b{b}"] = {"median_rho": float(np.median(h[:, 0])), "power": float(h[:, 1].mean())}
        print("S2 power", b, pw[f"b{b}"])
    res["S2_power"] = pw
    return res


def s3_potts(struct, reps, rng):
    """Projects layer. 20 periods with project rows (as H31: ~7 candidates per period)."""
    P = 20
    specc = np.array([s["S_count"] for s in struct])[:P]
    out = {}
    for truth in ("T0_no_naming", "T1_naming", "T2_naming_x_spec"):
        rows = []
        for _ in range(reps):
            named_m, frozen_m, strata, S_rows = [], [], [], []
            per_frac = []
            for k in range(P):
                Kp = rng.integers(4, 12)
                pin = 1 / (1 + np.exp(-(-1.5 + 1.0 * specc[k])))
                named = rng.random(Kp) < pin
                f0 = 0.05
                if truth == "T0_no_naming":
                    pf = np.full(Kp, f0)
                elif truth == "T1_naming":
                    pf = np.where(named, 0.35, f0)
                else:
                    pf = np.where(named, 1 / (1 + np.exp(-(-0.7 + 1.0 * specc[k]))), f0)
                frozen = rng.random(Kp) < pf
                # measurement: loose naming has false positives; frozen classification misses some
                nm = np.where(named, rng.random(Kp) < 0.85, rng.random(Kp) < 0.15)
                fm = np.where(frozen, rng.random(Kp) < 0.8, rng.random(Kp) < 0.01)
                named_m += list(nm)
                frozen_m += list(fm)
                strata += [k] * Kp
                S_rows += [specc[k]] * Kp
                per_frac.append(fm.mean())
            t = E.naming_table(named_m, frozen_m, strata, n_perm=300, rng=rng)
            rf, pf_, _ = E.spearman(specc, per_frac, "greater")
            nm_a, fm_a, S_a = np.array(named_m, float), np.array(frozen_m, float), np.array(S_rows)
            try:
                w, se = E.logistic(fm_a[nm_a == 1], S_a[nm_a == 1][:, None])
                zS = w[1] / se[1]
            except Exception:
                zS = np.nan
            rows.append([t["precision"], t["enrichment"], float(t["p_fisher"] < 0.05), float(E.p2_verdict(t) == "supported"),
                         t["n_frozen"], rf, float(pf_ < 0.05), float(zS > 1.645) if np.isfinite(zS) else np.nan])
        a = np.array(rows, float)
        out[truth] = {"precision": float(np.nanmedian(a[:, 0])), "enrichment": float(np.nanmedian(a[:, 1])),
                      "fisher_rate": float(np.nanmean(a[:, 2])), "P2_pass_rate": float(np.nanmean(a[:, 3])),
                      "n_frozen": float(np.nanmedian(a[:, 4])), "period_frac_vs_spec_rho": float(np.nanmedian(a[:, 5])),
                      "period_frac_vs_spec_sig_rate": float(np.nanmean(a[:, 6])),
                      "per_project_spec_effect_sig_rate": float(np.nanmean(a[:, 7]))}
        print("S3", truth, {k: round(v, 3) for k, v in out[truth].items()})
    return out


def s4_g51(cal, reps, rng, N=21, n_stmt=84):
    W = World(cal, rng)
    ra, re, _ = W.ratio["III"]
    roles = np.array(list(range(16)) + [0, 1, 2, 3, 4])
    out = {}
    for fp in (0.0, 0.05, 0.1, 0.2):
        for cg in (0.3, 0.5):
            acc, sig = [], []
            for _ in range(reps):
                Tr = W.draw("III", 16)
                t51 = W.draw("III")[0]
                a = W.draw("III", N)
                e = W.draw("III", N)
                fs = 0.1
                x = (np.sqrt(fp) * Tr[roles] + np.sqrt(fs) * t51 + np.sqrt(max(1 - fp - fs, 0) * ra) * a
                     + np.sqrt(max(1 - fp - fs, 0) * re) * e)
                V = np.vstack([E.unit(E.unit(E.unit(x[i]) + TAU * W.noise("III", n_stmt)).mean(0)) for i in range(N)])
                Gt = E.unit(cg * Tr + np.sqrt(1 - cg ** 2) * W.draw("III", 16))
                G = Gt[roles]
                ac, _ = E.swap_pairs(V, G, roles)
                acc.append(ac)
                sig.append(E.swap_perm_p(V, G, roles, n_perm=200, rng=rng) < 0.01)
            out[f"fp{fp}_cg{cg}"] = {"accuracy": float(np.median(acc)), "p<0.01_rate": float(np.mean(sig)),
                                     "acc_q05": float(np.percentile(acc, 5)), "acc_q95": float(np.percentile(acc, 95))}
            print("S4", fp, cg, out[f"fp{fp}_cg{cg}"])
    return out


def s5_g44(cal, reps, rng, nb=4, nr=12, n_stmt=30):
    W = World(cal, rng)
    ra, re, _ = W.ratio["III"]
    out = {}
    for f in (0.0, 0.05, 0.15, 0.3):
        accs, pct = [], []
        for _ in range(reps):
            tb, tr = W.draw("III", 2)
            kb = E.unit(0.5 * tb + np.sqrt(0.75) * W.draw("III")[0])
            kr = E.unit(0.5 * tr + np.sqrt(0.75) * W.draw("III")[0])
            rooms = np.array([2] * nb + [3] * nr)
            tg = np.vstack([tb] * nb + [tr] * nr)
            n = nb + nr
            x = np.sqrt(f) * tg + np.sqrt((1 - f) * ra) * W.draw("III", n) + np.sqrt((1 - f) * re) * W.draw("III", n)
            V = np.vstack([E.unit(E.unit(E.unit(x[i]) + TAU * W.noise("III", n_stmt)).mean(0)) for i in range(n)])
            rs = E.room_swap(V, rooms, {2: kb, 3: kr})
            d0 = E.axis_separation(V, rooms, kb - kr)
            Kd = W.draw("III", 30)
            null = [E.axis_separation(V, rooms, Kd[i] - Kd[j]) for i in range(30) for j in range(i + 1, 30)][:200]
            null = np.abs(np.array(null))
            accs.append(rs["accuracy"])
            pct.append(float(np.mean(null < d0)))
        out[f"f{f}"] = {"room_swap_acc": float(np.median(accs)), "acc>=0.8_rate": float(np.mean(np.array(accs) >= 0.8)),
                        "axis_pct": float(np.median(pct)), "axis_pct>=0.95_rate": float(np.mean(np.array(pct) >= 0.95))}
        print("S5", f, out[f"f{f}"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--only", default="s1,s3,s4,s5")
    a = ap.parse_args()
    t0 = time.time()
    rng = np.random.default_rng(20261004)
    cal = json.loads((L.OUT / "synthetic" / "calibration.json").read_text())
    struct = real_structure()
    res = {"reps": a.reps, "tau": TAU, "periods": [s["p"] for s in struct]}
    path = L.OUT / "synthetic" / "results.json"
    if path.exists():
        res = {**json.loads(path.read_text()), **res}
    only = a.only.split(",")
    if "s1" in only:
        res["S1_S2"] = s1_s2(struct, cal, a.reps, rng)
    if "s3" in only:
        res["S3"] = s3_potts(struct, a.reps, rng)
    if "s4" in only:
        res["S4_g51"] = s4_g51(cal, max(50, a.reps // 4), rng)
    if "s5" in only:
        res["S5_g44"] = s5_g44(cal, max(100, a.reps // 2), rng)
    res["runtime_s"] = time.time() - t0
    L.write_json(path, res)
    L.provenance("analysis/synthetic.py", ["H54 stmt counts", "kickoffs.parquet (S_text, S_count)", "goal_fields chunk counts", "synthetic/calibration.json"], {"seed": 20261004, "reps": a.reps, "tau": TAU})
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
