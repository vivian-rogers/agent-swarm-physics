"""H05 round 2: synthetic validation of the R1, R2 and R3 estimators on real skeletons (2026-10-05).
Run before any round-2 statistic on real data. Real outcomes are never read here: R1 uses the real days, agents,
rooms, co-edit flags and commit counts but replaces commit times; R2-P1 uses the real talk-spin presence, rooms and
talk rates but replaces the spins; R2-P2 uses real pending-set opportunity counts but replaces responses; R3 uses real
items, candidates and exposure times but replaces adoptions.

Usage: H05_DATA=r1b uv run python hypotheses/H05-rooms-cut/analysis/r2_synthetic.py [--part r1|r2k|r2u|r3|all] [--reps N]
Output: data/processed/H05-rooms-cut/r2/synthetic.json
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("H05_DATA", "r1b")
import json  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2_common as C  # noqa: E402

PART = sys.argv[sys.argv.index("--part") + 1] if "--part" in sys.argv else "all"
REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 20
OUTF = C.OUT / "synthetic.json"
J0_SYN = float(sys.argv[sys.argv.index("--j0") + 1]) if "--j0" in sys.argv else 0.3


def save(key, val):
    C.OUT.mkdir(parents=True, exist_ok=True)
    d = json.loads(OUTF.read_text()) if OUTF.exists() else {}
    d[key] = val
    OUTF.write_text(json.dumps(d, indent=1, default=float))


# ============================================================================================ R1
def r1_world(mats, rng, p_couple, drive="none", couple_on=None, tod=None):
    """Synthetic commit bins. Each agent-day keeps its real commit count n and fires at a rate following the pooled
    time-of-day profile `tod` (scheduler field). drive: 'all' = shared same-day bursts for everyone; 'coedit' =
    bursts shared only by co-editors of the day (a repository-level common drive). p_couple: after each commit of j,
    i commits in the next 30 min with this probability, for pairs in couple_on[d] (set of (i, j))."""
    out = {}
    for d, m in mats.items():
        T, N = m["C"].shape
        prof = np.interp(np.linspace(0, 1, T), np.linspace(0, 1, len(tod)), tod)
        prof = prof / prof.sum()
        C2 = np.zeros((T, N))
        bursts = rng.choice(T, size=min(3, T), replace=False) if drive != "none" and T > 3 else []
        ag = [int(a) for a in m["agents"]]
        drive_set = set()
        if drive == "coedit":
            for x in range(N):
                for y in range(x + 1, N):
                    if m["repos"][ag[x]] & m["repos"][ag[y]]:
                        drive_set |= {x, y}
        for x in range(N):
            n = int((m["C"][:, x] > 0).sum())   # real occupied bins
            if n == 0:
                continue
            w = prof.copy()
            if drive == "all" or (drive == "coedit" and x in drive_set):
                for b in bursts:
                    w[b: b + 2] *= 6
            w = w / w.sum()
            C2[rng.choice(T, size=min(n, T), replace=False, p=w), x] = 1
        if couple_on and d in couple_on:
            idx = {a: k for k, a in enumerate(ag)}
            base = C2.copy()   # responses are triggered by the base trains only (no cascades)
            for (i, j) in couple_on[d]:
                for src, dst in ((idx[j], idx[i]), (idx[i], idx[j])):
                    for t in np.where(base[:, src] > 0)[0]:
                        if rng.random() < p_couple and t + 1 < T:
                            C2[min(T - 1, t + rng.integers(1, C.RESP_BINS + 1)), dst] = 1
        out[d] = {"agents": m["agents"], "C": C2, "n": C2.sum(0).astype(int), "repos": m["repos"]}
    return out


def r1_contrast(pdd, rng, n_perm=300):
    t = pdd.filter(~pl.col("same_room") & pl.col("E_x").is_not_null())
    t = t.with_columns(pl.Series("ter", C.tertile(np.minimum(t["n_i"], t["n_j"]).to_numpy().astype(float))),
                       pl.col("pt_date").alias("g"))
    gd = dict(C.agent_days().group_by("pt_date").agg(pl.col("goal_no").first()).iter_rows())
    t = t.with_columns(pl.col("pt_date").replace_strict(gd, return_dtype=pl.Int64).alias("goal_no"))
    return C.strata_contrast(t, "E_x", "coedit", ["goal_no", "ter"], n_perm, rng)


def part_r1():
    rng = np.random.default_rng(1)
    ad = C.agent_days()
    rooms = C.room_dict(ad)
    wc = C.load_commits()
    mats = C.commit_mats(wc, ad)
    # pooled time-of-day profile of real commits (marginal only)
    prof = np.zeros(50)
    for m in mats.values():
        T = m["C"].shape[0]
        s = m["C"].sum(1)
        prof += np.interp(np.linspace(0, 1, 50), np.linspace(0, 1, T), s)
    prof = np.maximum(prof, prof.max() * 0.02)
    couple = {}
    for d, m in mats.items():
        ag = [int(a) for a in m["agents"]]
        for x in range(len(ag)):
            for y in range(x + 1, len(ag)):
                if m["repos"][ag[x]] & m["repos"][ag[y]] and rooms[d].get(ag[x]) != rooms[d].get(ag[y]):
                    couple.setdefault(d, set()).add((ag[x], ag[y]))   # plant on cross-room co-edit pairs
    res = {}
    for name, p, drive in (("null", 0.0, "none"), ("null_shared_drive", 0.0, "all"), ("coedit_drive_impostor", 0.0, "coedit"),
                           ("couple_0.1", 0.1, "none"), ("couple_0.2", 0.2, "none"), ("couple_0.3", 0.3, "none")):
        rs = []
        for r in range(REPS):
            w = r1_world(mats, rng, p, drive, couple, prof)
            pdd = C.commit_pair_days(w, rooms)
            c = r1_contrast(pdd, rng)
            rs.append(c)
        diffs = np.array([x.get("diff", np.nan) for x in rs])
        ps = np.array([x.get("p_perm_one_sided") or np.nan for x in rs])
        res[name] = {"p_couple": p, "drive": drive, "reps": REPS, "diff_mean": float(np.nanmean(diffs)),
                     "diff_sd": float(np.nanstd(diffs)), "reject_rate_p05": float(np.nanmean(ps < 0.05)),
                     "n_cross_coedit_mean": float(np.mean([x.get("n_flag", 0) for x in rs])),
                     "n_cross_mean": float(np.mean([x.get("n", 0) for x in rs]))}
        print("R1", name, res[name], flush=True)
    save("R1", res)


# ============================================================================================ R2-P1 (kappa_x)
def part_r2k():
    import explore_rooms as X
    from pairs import twfe
    rng = np.random.default_rng(2)
    days, mats, goal, regime = X.load_days()
    d3 = [d for d in days if regime[d] == "III"]
    ad = C.agent_days()
    nroom = {(d, int(a)): int(n) for d, a, n in ad.select("pt_date", "agent", "n_room").iter_rows()}
    roomd = C.room_dict(ad)

    def synth(beta, J0, c_tod=0.5):
        out = {}
        for d in d3:
            m = mats[d]
            A = m["talk"]
            L, N = A.shape
            p = np.clip((A > 0).mean(0), 0.01, 0.6)
            R = m["room"]
            ag = [int(a) for a in m["agents"]]
            prof = np.convolve((A > 0).mean(1), np.ones(31) / 31, mode="same")
            z = (prof - prof.mean()) / (prof.std() + 1e-9)
            k = np.array([max(nroom.get((d, a), 2) - 1, 1) for a in ag], dtype=float)
            S = -np.ones((L, N), dtype=np.int8)
            S[0] = np.where(rng.random(N) < p, 1, -1)
            h0 = np.log(p / (1 - p))
            for t in range(L - 1):
                same = (R[t][:, None] == R[t][None, :]) & (R[t][:, None] >= 0)
                np.fill_diagonal(same, False)
                J = J0 * (k[:, None] / 10.0) ** (-beta) * same
                s = S[t].astype(float)
                m_ = 2 * p - 1
                H = h0 + c_tod * z[t] + J @ (s - m_)
                S[t + 1] = np.where(rng.random(N) < 1 / (1 + np.exp(-H)), 1, -1)
            mm = dict(m)
            mm["talk"] = S
            out[d] = mm
        return out

    res = {}
    for beta in (0.0, 0.25, 0.45, 0.7, 1.0):
        rs = []
        for r in range(REPS):
            sm = synth(beta, J0=J0_SYN)
            pdf = X.pair_days(d3, sm, goal, regime, "talk")
            pdf = pdf.filter((pl.col("coloc") >= 0.75) & (pl.col("known") > 0.5))
            kr = [nroom.get((d, int(i))) if roomd[d].get(int(i)) == roomd[d].get(int(j)) else None
                  for d, i, j in pdf.select("pt_date", "i", "j").iter_rows()]
            pdf = pdf.with_columns(pl.Series("kroom", [None if k is None else k - 1 for k in kr], dtype=pl.Float64))
            rs.append(C.r2_kappa_twfe(pdf, twfe))
        bh = np.array([x.get("beta_hat", np.nan) for x in rs])
        cov = np.mean([(x["beta_ci95"][0] <= beta <= x["beta_ci95"][1]) for x in rs if "beta_ci95" in x])
        rej0 = np.mean([(x["beta_ci95"][0] > 0) for x in rs if "beta_ci95" in x])
        inc45 = np.mean([(x["beta_ci95"][0] <= 0.45 <= x["beta_ci95"][1]) for x in rs if "beta_ci95" in x])
        res[f"beta_{beta}"] = {"reps": REPS, "J0": J0_SYN, "k_ref": 10, "beta_hat_mean": float(np.nanmean(bh)), "beta_hat_sd": float(np.nanstd(bh)),
                               "beta_hat_q025_q975": [float(np.nanpercentile(bh, 2.5)), float(np.nanpercentile(bh, 97.5))],
                               "beta_hat_all": [float(x) for x in bh],
                               "coverage_true": float(cov), "ci_excludes_0_rate": float(rej0), "ci_includes_045_rate": float(inc45),
                               "kappa_bar_mean": float(np.mean([x["kappa_bar"] for x in rs])),
                               "se_mean": float(np.mean([x["se"] for x in rs])) / max(float(np.mean([x["kappa_bar"] for x in rs])), 1e-9)}
        print("R2k", beta, res[f"beta_{beta}"], flush=True)
    save("R2_P1_kappa", res)


# ============================================================================================ R2-P2 (uptake)
def part_r2u():
    rng = np.random.default_rng(3)
    ad = C.agent_days()
    u = C.uptake_pairdays(ad).select("i", "j", "pt_date", "goal_no", "n", "kroom")
    pairs = (u["i"].cast(pl.Int32) * 100 + u["j"].cast(pl.Int32)).to_numpy()
    _, pc = np.unique(pairs, return_inverse=True)
    days = u["pt_date"].to_numpy()
    _, dc = np.unique(days, return_inverse=True)
    n = u["n"].to_numpy()
    k = u["kroom"].to_numpy().astype(float)
    g = u["goal_no"].to_numpy()
    res = {}
    for name, beta, field in (("beta0", 0.0, 0.0), ("beta0_goalfield", 0.0, 0.5), ("beta045", 0.45, 0.0),
                              ("beta045_goalfield", 0.45, 0.5), ("beta1", 1.0, 0.0)):
        bh, cov, rej0 = [], [], []
        for r in range(max(REPS, 100)):
            a = rng.normal(np.log(0.15), 0.6, pc.max() + 1)
            dd = rng.normal(0, 0.3, dc.max() + 1)
            gf = field * (g == 40) - field * 0.5 * (g == 51)   # a goal-specific field that tracks the merge
            p = np.clip(np.exp(a[pc] + dd[dc] + gf - beta * np.log(k / 4.0)), 0, 0.95)
            y = rng.binomial(n, p)
            uu = u.with_columns(pl.Series("y", y))
            f = C.uptake_fit(uu)
            bh.append(f["beta_u"]); cov.append(f["beta_ci95"][0] <= beta <= f["beta_ci95"][1]); rej0.append(f["beta_ci95"][0] > 0)
        res[name] = {"beta": beta, "goal_field": field, "reps": len(bh), "beta_hat_mean": float(np.mean(bh)),
                     "beta_hat_sd": float(np.std(bh)), "coverage": float(np.mean(cov)), "ci_excludes_0_rate": float(np.mean(rej0))}
        print("R2u", name, res[name], flush=True)
    save("R2_P2_uptake", res)


# ============================================================================================ R3
def part_r3():
    import r2_leak as L
    rng = np.random.default_rng(4)
    ad = C.agent_days()
    inp = L.build_inputs(ad)
    cand = inp["cand"].drop("t_adopt")
    W = L.W_S * 1_000_000
    # activity skeleton: each agent's real deliberate artifact-use times (when the agent is busy with artifacts)
    busy = {int(b): np.sort(g["tu"].to_numpy()) for (b,), g in inp["delib"].group_by("b")}
    exp = inp["exp"]
    # first exposures without adoption cap (needed to plant responses)
    fe0 = L.first_exposures(cand.with_columns(pl.lit(None, dtype=pl.Int64).alias("t_adopt")), exp)
    res = {}
    for name, g_leak, g_chat, lam, act in (("null_flat", 0.0, 0.1, 0.02, False), ("null_activity", 0.0, 0.1, 0.02, True),
                                           ("leak_0.05", 0.05, 0.1, 0.02, True), ("leak_0.10", 0.10, 0.1, 0.02, True),
                                           ("leak_0.20", 0.20, 0.1, 0.02, True)):
        rs = {"search": [], "output": [], "chat_within": []}
        for r in range(REPS):
            F = fe0.to_dict(as_series=False)
            ta = []
            for q in range(len(F["b"])):
                b, tb, tc = F["b"][q], F["tb"][q], F["tc"][q]
                best = None
                # background: daily hazard lam over the open follow-up; times drawn from the agent's busy times (act)
                span_days = max((tc - tb) / (86400 * 1e6), 0)
                if rng.random() < 1 - np.exp(-lam * span_days):
                    bt = busy.get(int(b))
                    if act and bt is not None:
                        cands = bt[(bt > tb) & (bt < tc)]
                        best = int(rng.choice(cands)) if len(cands) else None
                    else:
                        best = int(rng.integers(tb + 1, max(tc, tb + 2)))
                for ch, gg in (("search", g_leak), ("output", g_leak), ("chat", g_chat)):
                    te = F[f"t_{ch}"][q]
                    if te is not None and rng.random() < gg:
                        tt = int(te + rng.integers(1, W))
                        if tt < tc and (best is None or tt < best):
                            best = tt
                ta.append(best)
            c2 = cand.with_columns(pl.Series("t_adopt", ta, dtype=pl.Int64))
            fe = L.first_exposures(c2, exp)
            for ch in ("search", "output"):
                rs[ch].append(L.conductance(fe, ch, True, rng, n_boot=200))
            rs["chat_within"].append(L.conductance(fe, "chat", False, rng, n_boot=200))
        summ = {}
        for ch, lst in rs.items():
            lst = [x for x in lst if x.get("n_exposures", 0) > 0]
            if not lst:
                summ[ch] = {"n": 0}; continue
            summ[ch] = {"n_exposures_mean": float(np.mean([x["n_exposures"] for x in lst])),
                        "excess_mean": float(np.mean([x["excess"] for x in lst])),
                        "excess_sd": float(np.std([x["excess"] for x in lst])),
                        "reject_lift_ci_gt1": float(np.mean([(x["lift_ci95"] is not None and x["lift_ci95"][0] > 1) for x in lst])),
                        "reject_excess_ci_gt0": float(np.mean([x["excess_ci95"][0] > 0 for x in lst]))}
        res[name] = {"g_leak": g_leak, "g_chat": g_chat, "lambda_per_day": lam, "activity_timed": act, "reps": REPS, **summ}
        print("R3", name, json.dumps(res[name]), flush=True)
    save("R3", res)


if __name__ == "__main__":
    t0 = time.time()
    for p, f in (("r1", part_r1), ("r2u", part_r2u), ("r3", part_r3), ("r2k", part_r2k)):
        if PART in (p, "all"):
            f()
            print(p, "done", round(time.time() - t0), "s", flush=True)
