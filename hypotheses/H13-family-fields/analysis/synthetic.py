"""H13 synthetic validation (axis F): plant family fields and K x K family couplings at village N and sampling.

Village sampling taken from the built scheme (design facts only: family compositions, room assignments of #41,
chat statements per agent-day and per agent-window); no family statistic of the real data is used.

F1  family-field detection: power / false-positive rate of T_field (lab permutation), R2_fam, LOO classification,
    vs the family share phi of the agent-level offset variance; compositions of units 37, 41, 51b.
F2  static vs period-specific family fields: invariance check (split-half cos, family and agent level) and the
    fixed-offset rival S-b (T'/T, subtraction vs projection), 12 units of one regime.
F3  content co-movement K x K: planted block couplings J_in / J_out in window-level Gaussian soft spins;
    recovery of Delta_content, size and power of the lab-permutation test, rotation null.
F4  talk-spin K x K: kinetic Ising with family-block couplings (H05 simulator); Delta_talk recovery, size, power;
    and a room-only coupling world (does the family test fire when couplings follow rooms?).
F5  family vs room for the content field (#41 composition and room assignment): b_lab / b_room size and power.

Usage: uv run python hypotheses/H13-family-fields/analysis/synthetic.py [--fast]
Writes data/processed/H13-family-fields/synthetic_validation.json and figures/synthetic_validation.pdf.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "H05-rooms-cut/analysis"))
import h13lib as L  # noqa: E402
from ep import simulate_kinetic_ising  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H13-family-fields"
FIG = HERE.parent / "figures"
FAST = "--fast" in sys.argv
D32 = 32
# calibrated so synthetic instrument statistics match the real ones (|v| ~ 0.65, |m_d| ~ 0.4, |delta| ~ 0.5,
# agent day-to-day consistency ~ 0.55; see calibrate())
SIG_G, SIG_O, SIG_X = 0.55, 0.62, 0.42


def design():
    meta = json.loads((DATA / "units.json").read_text())
    comp, ns, nw = {}, [], []
    for u, v in meta.items():
        ad = pl.read_parquet(DATA / v["gdir"] / f"u{u}_agent_day.parquet")
        ns += ad["n"].to_list()
        w = pl.read_parquet(DATA / v["gdir"] / f"u{u}_win30.parquet")
        nw += w["n"].to_list()
        e = ad.filter(pl.col("n") >= 3).group_by("agent").agg(pl.col("lab").first(), pl.len().alias("nd")) \
              .filter(pl.col("nd") >= 2)
        comp[u] = sorted(e["lab"].to_list())
    ad41 = pl.read_parquet(DATA / "G41/u41_agent_day.parquet").filter(pl.col("n") >= 3)
    r41 = ad41.group_by("agent").agg(pl.col("lab").first(), pl.col("room").mode().first()).sort("agent")
    return comp, np.array(ns), np.array(nw), r41["lab"].to_list(), r41["room"].to_numpy()


# ----------------------------------------------------------------------------- generators
def statements_mean(rng, mu, n):
    """mean of n unit-normalized statements z = mu + eps (eps ~ N(0, I))."""
    Z = mu[None, :] + rng.normal(size=(n, len(mu)))
    return L.unit(Z).mean(0)


def gen_unit(rng, offsets, D, nsamp, sig_g=SIG_G, sig_x=SIG_X, xfun=None):
    """offsets: (N, d) static agent offsets. Returns (V, days, agents) agent-day mean vectors (n >= 3 kept)."""
    N, d = offsets.shape
    V, dd, aa = [], [], []
    for day in range(D):
        g = rng.normal(0, sig_g, d)
        X = xfun(rng) if xfun is not None else rng.normal(0, sig_x, (N, d))
        for i in range(N):
            n = int(rng.choice(nsamp))
            if n < 3:
                continue
            V.append(statements_mean(rng, g + offsets[i] + X[i], n)); dd.append(day); aa.append(i)
    return np.array(V), np.array(dd), np.array(aa)


def fam_offsets(rng, labs, phi, sig_o=SIG_O, d=D32, hf=None):
    fam, multi = L.fam_labels(labs)
    labsu = sorted(set(labs))
    if hf is None:
        hf = {l: rng.normal(0, np.sqrt(phi) * sig_o, d) for l in labsu}
    a = rng.normal(0, np.sqrt(1 - phi) * sig_o, (len(labs), d))
    return np.array([hf[l] for l in labs]) + a, fam, len(multi)


def unit_field(rng, V, dd, aa, fam_all, K, nperm, jack=False):
    D = L.day_demean(V, dd, aa)
    ags, H, _ = L.agent_means(D, aa)
    fam = fam_all[ags]
    # recode: singletons can appear after filtering; keep codes (K fixed by full composition)
    r = L.field_test(H, fam, K, nperm=nperm, rng=rng, jack=jack)
    return r, H, fam


def calibrate(rng, nsamp, labs, D=5):
    off, fam, K = fam_offsets(rng, labs, 0.3)
    V, dd, aa = gen_unit(rng, off, D, nsamp)
    Dm = L.day_demean(V, dd, aa)
    md = np.mean([np.linalg.norm(V[dd == d].mean(0)) for d in np.unique(dd)])
    cons = []
    for a in np.unique(aa):
        X = L.unit(Dm[aa == a])
        if len(X) >= 2:
            C = X @ X.T; cons.append(C[np.triu_indices(len(X), 1)].mean())
    return {"|v|": float(np.linalg.norm(V, axis=1).mean()), "|m_d|": float(md),
            "|delta|": float(np.linalg.norm(Dm, axis=1).mean()), "agent_daycons": float(np.mean(cons))}


# ----------------------------------------------------------------------------- F1
def f1(rng, comp, nsamp, units=("37", "41", "51b"), Ds={"37": 3, "41": 5, "51b": 19}):
    phis = (0.0, 0.05, 0.1, 0.2, 0.35)
    out = {}
    for u in units:
        labs = comp[u]
        out[u] = {"N": len(labs), "D": Ds[u], "composition": {l: labs.count(l) for l in sorted(set(labs))}, "phi": {}}
        for phi in phis:
            reps = (60 if FAST else 200) if phi == 0 else (30 if FAST else 100)
            T, P, R2, ACC, PA = [], [], [], [], []
            for _ in range(reps):
                off, fam_all, K = fam_offsets(rng, labs, phi)
                V, dd, aa = gen_unit(rng, off, Ds[u], nsamp)
                r, H, fam = unit_field(rng, V, dd, aa, fam_all, K, nperm=300)
                T.append(r["obs"]); P.append(r["p"])
                R2.append(L.r2_fam(H, fam, K))
                lp = L.loo_perm(H, fam, K, nperm=100, rng=rng)
                ACC.append(lp["obs"]); PA.append(lp["p"])
            P, PA = np.array(P), np.array(PA)
            out[u]["phi"][str(phi)] = {"reps": reps, "reject_T": float(np.mean(P < 0.05)), "T_median": float(np.median(T)),
                                       "R2_median": float(np.nanmedian(R2)), "loo_acc_median": float(np.nanmedian(ACC)),
                                       "reject_loo": float(np.mean(PA < 0.05))}
            print("F1", u, phi, out[u]["phi"][str(phi)], flush=True)
    return out


# ----------------------------------------------------------------------------- F2
def f2(rng, nsamp, labs, U=12, D=5, present=0.85):
    """Same agent pool in U units of one regime (each agent present with prob `present`). Agent offset in unit u:
    family part (variance share phi; static share psi) + agent part (static share rho)."""
    rho = 0.5
    res = {}
    fam_all, multi = L.fam_labels(labs)
    K = len(multi)
    N = len(labs)
    lab_of = {i: l for i, l in enumerate(labs)}
    for name, (phi, psi) in {"no family field": (0.0, 1.0), "static (psi=1)": (0.3, 1.0), "half (psi=0.5)": (0.3, 0.5),
                             "period-specific (psi=0)": (0.3, 0.0)}.items():
        reps = 8 if FAST else 25
        acc = {k: [] for k in ("fam_med", "null_med", "p_regroup", "cross", "agent", "sb_proj", "sb_sub", "sb_p", "T_raw")}
        for _ in range(reps):
            s_o = SIG_O
            h0 = {l: rng.normal(0, np.sqrt(phi * psi) * s_o, D32) for l in set(labs)}
            a0 = rng.normal(0, np.sqrt((1 - phi) * rho) * s_o, (N, D32))
            Hu = []
            for u in range(U):
                hu = {l: rng.normal(0, np.sqrt(phi * (1 - psi)) * s_o, D32) for l in set(labs)}
                au = rng.normal(0, np.sqrt((1 - phi) * (1 - rho)) * s_o, (N, D32))
                off = np.array([h0[l] + hu[l] for l in labs]) + a0 + au
                V, dd, aa = gen_unit(rng, off, D, nsamp)
                pres = rng.random(N) < present
                k = pres[aa]
                Dm = L.day_demean(V[k], dd[k], aa[k])
                ags, H, _ = L.agent_means(Dm, aa[k])
                Hu.append({int(a): h for a, h in zip(ags, L.unit(H))})
            inv = L.invariance(Hu, lab_of, [multi[k] for k in range(K)], nperm=100 if FAST else 200, rng=rng)
            acc["fam_med"].append(inv["family_median"]); acc["null_med"].append(inv["null_regroup_median_mean"])
            acc["p_regroup"].append(inv["p_regroup"]); acc["cross"].append(inv["crossfamily_cos"]); acc["agent"].append(inv["agent_median"])
            # S-b on unit 0 (agents with other-unit data)
            ags0 = sorted(Hu[0])
            S = np.array([np.mean([Hu[u][a] for u in range(1, U) if a in Hu[u]], 0) for a in ags0])
            Hn = np.array([Hu[0][a] for a in ags0])
            proj, sub = L.fixed_offset_residual(Hn, S)
            f0 = fam_all[ags0]
            t0 = L.field_test(Hn, f0, K, nperm=200, rng=rng, jack=False)
            tp = L.field_test(proj, f0, K, nperm=200, rng=rng, jack=False)
            ts = L.field_test(sub, f0, K, nperm=0 or 1, rng=rng, jack=False)
            acc["T_raw"].append(t0["obs"]); acc["sb_p"].append(tp["p"])
            acc["sb_proj"].append(tp["obs"] / t0["obs"] if t0["obs"] > 0 else np.nan)
            acc["sb_sub"].append(ts["obs"] / t0["obs"] if t0["obs"] > 0 else np.nan)
        res[name] = {"phi": phi, "psi": psi, "reps": reps,
                     "family_splithalf_median": float(np.mean(acc["fam_med"])),
                     "regroup_null_median": float(np.mean(acc["null_med"])),
                     "reject_regroup": float(np.mean(np.array(acc["p_regroup"]) < 0.05)),
                     "crossfamily_cos": float(np.mean(acc["cross"])), "agent_splithalf_median": float(np.mean(acc["agent"])),
                     "T_raw_median": float(np.median(acc["T_raw"])),
                     "Sb_ratio_project_median": float(np.nanmedian(acc["sb_proj"])),
                     "Sb_ratio_subtract_median": float(np.nanmedian(acc["sb_sub"])),
                     "Sb_reject": float(np.mean(np.array(acc["sb_p"]) < 0.05))}
        print("F2", name, res[name], flush=True)
    return {"rho_agent_static": rho, "U": U, "D": D, "present": present, "scenarios": res}


# ----------------------------------------------------------------------------- F3
def block_J_matrix(fam, K, j_in, j_out):
    same = (fam[:, None] == fam[None, :]) & (fam[:, None] < K)
    J = np.where(same, j_in, j_out).astype(float)
    np.fill_diagonal(J, 0)
    return J


def f3(rng, labs, nw, W=8, D=5, present=0.55):
    fam_all, multi = L.fam_labels(labs)
    K = len(multi)
    N = len(labs)
    nwp = nw[nw >= 2]
    out = {}
    for j_in, j_out in ((0.0, 0.0), (0.03, 0.03), (0.06, 0.02), (0.10, 0.02), (0.15, 0.02)):
        J = block_J_matrix(fam_all, K, j_in, j_out)
        C = np.linalg.inv(np.eye(N) - J)
        Lc = np.linalg.cholesky(C)
        reps = 20 if FAST else 60
        dl, pv, rot_ok, rmean, pv2, con2 = [], [], [], [], [], []
        for _ in range(reps):
            off = rng.normal(0, SIG_O, (N, D32))
            V, wi, ag = [], [], []
            for w in range(W * D):
                g = rng.normal(0, SIG_G, D32)
                X = SIG_X * (Lc @ rng.normal(size=(N, D32)))
                for i in range(N):
                    if rng.random() > present:
                        continue
                    n = int(rng.choice(nwp))
                    V.append(statements_mean(rng, g + off[i] + X[i], n)); wi.append(w); ag.append(i)
            V, wi, ag = np.array(V), np.array(wi), np.array(ag)
            ags, X, keep = L.comove_matrix(ag, wi, V)
            R = L.comove_r(ags, ag, wi, X, keep)
            ags2, X2, keep2 = L.comove_matrix(ag, wi, V, window_demean=True)
            R2 = L.comove_r(ags2, ag, wi, X2, keep2)
            fam = fam_all[ags]
            ii, jj = L.pairs(len(ags))
            r = R[ii, jj]; ok = np.isfinite(r)
            q = L.kxk_from_pairs(ii[ok], jj[ok], r[ok], np.ones(ok.sum()), fam, K)
            null = []
            for _ in range(100 if FAST else 300):
                null.append(L.block_J(ii[ok], jj[ok], r[ok], np.ones(ok.sum()), rng.permutation(fam))["J_in_minus_out"])
            null = np.array(null)
            dl.append(q["J_in_minus_out"]); pv.append((1 + np.sum(null >= q["J_in_minus_out"])) / (1 + len(null)))
            r2 = R2[ii, jj]; ok2 = np.isfinite(r2)
            wa2 = L.wa_perm(r2[ok2], ii[ok2], jj[ok2], fam, K, nperm=100 if FAST else 300, rng=rng)
            pv2.append(wa2["p"]); con2.append(wa2["obs"])
            # rotation null for overall co-movement
            rot = {a: L.random_rotation(D32, rng) for a in ags}
            Rr = L.comove_r(ags, ag, wi, X, keep, rot=rot)
            rmean.append(np.nanmean(R[ii, jj])); rot_ok.append(np.nanmean(Rr[ii, jj]))
        pv = np.array(pv)
        out[f"{j_in}/{j_out}"] = {"reps": reps, "true_delta": j_in - j_out, "delta_hat_median": float(np.median(dl)),
                                  "delta_hat_sd": float(np.std(dl)), "reject": float(np.mean(pv < 0.05)),
                                  "mean_r": float(np.mean(rmean)), "mean_r_rotation": float(np.mean(rot_ok)),
                                  "windowdemeaned_contrast_median": float(np.median(con2)),
                                  "windowdemeaned_reject": float(np.mean(np.array(pv2) < 0.05))}
        print("F3", j_in, j_out, out[f"{j_in}/{j_out}"], flush=True)
    return {"N": N, "windows": W * D, "present": present, "scenarios": out}


# ----------------------------------------------------------------------------- F4
def talk_pairs(S, days):
    from importlib import import_module
    sys.path.insert(0, str(HERE.parent / "scheme"))
    corr_cols = import_module("build").corr_cols
    nd = len(np.unique(days))
    N = S.shape[1]
    ii, jj = L.pairs(N)
    X = [S[days == k].astype(float) for k in range(nd)]
    Rm = np.full((len(ii), nd), np.nan); Sv = np.full_like(Rm, np.nan)
    for d in range(nd):
        C0 = corr_cols(X[d], X[d])
        sur = [0.5 * (corr_cols(X[d], X[e]) + corr_cols(X[d], X[e]).T)[ii, jj] for e in range(nd) if e != d]
        act = (X[d].mean(0) + 1) / 2
        v = 4 * act * (1 - act)
        Rm[:, d] = C0[ii, jj] - np.nanmean(sur, 0)
        Sv[:, d] = np.sqrt(v[ii] * v[jj])
    return Rm, Sv, ii, jj


def f4(rng, labs, rooms, D=5, Lday=240):
    fam_all, multi = L.fam_labels(labs)
    K = len(multi)
    N = len(labs)
    out = {}
    worlds = {"null 0.02/0.02": ("fam", 0.02, 0.02), "family 0.08/0.02": ("fam", 0.08, 0.02),
              "family 0.15/0.02": ("fam", 0.15, 0.02), "room-only 0.06/0.02": ("room", 0.06, 0.02)}
    for name, (kind, jin, jout) in worlds.items():
        reps = 15 if FAST else 50
        dl, pv, act, bl, br, pl_, pr = [], [], [], [], [], [], []
        for _ in range(reps):
            grp = fam_all if kind == "fam" else rooms
            Kg = K if kind == "fam" else 99
            J = np.where((grp[:, None] == grp[None, :]) & (grp[:, None] < Kg), jin, jout).astype(float)
            J += rng.normal(0, 0.01, J.shape)
            np.fill_diagonal(J, 0.0)
            h = rng.normal(-0.95, 0.15, N) + J.sum(1)       # compensate the silent-state field so activity ~5%
            np.fill_diagonal(J, 0.3)
            ht = np.zeros(Lday); ht[:20] = np.linspace(-0.6, 0, 20)
            S, days = simulate_kinetic_ising(J, h, D, Lday, rng=rng, h_t=ht)
            act.append(float((S > 0).mean()))
            Rm, Sv, ii, jj = talk_pairs(S, days)
            res = L.kxk_test(Rm, Sv, ii, jj, fam_all, K, nboot=0, nperm=100 if FAST else 300, rng=rng)
            dl.append(res["delta"]); pv.append(res["p_perm"])
            Y = np.full((N, N), np.nan)
            Y[ii, jj] = Y[jj, ii] = np.nanmean(Rm, 1)
            fr = L.famroom(Y, fam_all, rooms, K, nperm=100 if FAST else 300, rng=rng, jack=False)
            bl.append(fr["b_lab"]); br.append(fr["b_room"]); pl_.append(fr["p_lab"]); pr.append(fr["p_room"])
        out[name] = {"reps": reps, "activity": float(np.mean(act)), "delta_hat_median": float(np.median(dl)),
                     "reject_family_delta": float(np.mean(np.array(pv) < 0.05)),
                     "b_lab_median": float(np.median(bl)), "b_room_median": float(np.median(br)),
                     "reject_b_lab": float(np.mean(np.array(pl_) < 0.05)), "reject_b_room": float(np.mean(np.array(pr) < 0.05))}
        print("F4", name, out[name], flush=True)
    return {"N": N, "D": D, "L": Lday, "worlds": out}


# ----------------------------------------------------------------------------- F5
def f5(rng, labs, rooms, nsamp, D=5):
    fam_all, multi = L.fam_labels(labs)
    K = len(multi)
    N = len(labs)
    out = {}
    for name, (pf, pr) in {"none": (0, 0), "family 0.3": (0.3, 0), "room 0.3": (0, 0.3), "both 0.3/0.3": (0.3, 0.3)}.items():
        reps = 20 if FAST else 80
        bl, br, pl_, pr_ = [], [], [], []
        for _ in range(reps):
            hf = {l: rng.normal(0, np.sqrt(pf) * SIG_O, D32) for l in set(labs)}
            hr = {r: rng.normal(0, np.sqrt(pr) * SIG_O, D32) for r in set(rooms.tolist())}
            off = np.array([hf[l] + hr[r] for l, r in zip(labs, rooms)]) + rng.normal(0, np.sqrt(1 - pf - pr) * SIG_O, (N, D32))
            V, dd, aa = gen_unit(rng, off, D, nsamp)
            Dm = L.day_demean(V, dd, aa)
            ags, H, _ = L.agent_means(Dm, aa)
            Y = L.unit(H) @ L.unit(H).T
            fr = L.famroom(Y, fam_all[ags], rooms[ags], K, nperm=150 if FAST else 400, rng=rng, jack=False)
            bl.append(fr["b_lab"]); br.append(fr["b_room"]); pl_.append(fr["p_lab"]); pr_.append(fr["p_room"])
        out[name] = {"reps": reps, "b_lab_median": float(np.median(bl)), "b_room_median": float(np.median(br)),
                     "reject_b_lab": float(np.mean(np.array(pl_) < 0.05)), "reject_b_room": float(np.mean(np.array(pr_) < 0.05))}
        print("F5", name, out[name], flush=True)
    return out


def figure(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 4, figsize=(13, 3.1))
    for u, c in zip(res["F1"], ("#999", "#2a7", "#36c")):
        ph = sorted(res["F1"][u]["phi"], key=float)
        ax[0].plot([float(p) for p in ph], [res["F1"][u]["phi"][p]["reject_T"] for p in ph], "o-", color=c, label=f"unit {u} (N={res['F1'][u]['N']}, D={res['F1'][u]['D']})")
    ax[0].axhline(0.05, color="k", lw=0.5, ls=":")
    ax[0].set_xlabel("family share φ of agent offset variance"); ax[0].set_ylabel("P(reject), α = 0.05")
    ax[0].set_title("F1 family-field test power", fontsize=9); ax[0].legend(fontsize=6)
    sc = res["F2"]["scenarios"]
    ks = list(sc)
    x = np.arange(len(ks))
    ax[1].bar(x - 0.27, [sc[k]["family_splithalf_median"] for k in ks], 0.18, label="family split-half cos")
    ax[1].bar(x - 0.09, [sc[k]["regroup_null_median"] for k in ks], 0.18, label="random-regrouping null")
    ax[1].bar(x + 0.09, [sc[k]["agent_splithalf_median"] for k in ks], 0.18, label="agent split-half cos")
    ax[1].bar(x + 0.27, [sc[k]["Sb_reject"] for k in ks], 0.18, label="S-b T' test P(reject)")
    ax[1].axhline(0.5, color="k", lw=0.5, ls=":")
    ax[1].set_xticks(x); ax[1].set_xticklabels([k.replace(" (", "\n(") for k in ks], fontsize=6); ax[1].set_title("F2 invariance and fixed-offset rival", fontsize=9)
    ax[1].legend(fontsize=6)
    s3 = res["F3"]["scenarios"]
    k3 = list(s3)
    ax[2].plot([s3[k]["true_delta"] for k in k3], [s3[k]["delta_hat_median"] for k in k3], "o", color="#36c", label="Δ̂ median")
    for k in k3:
        ax[2].annotate(f"{s3[k]['reject']:.2f}", (s3[k]["true_delta"], s3[k]["delta_hat_median"]), fontsize=6)
    ax[2].set_xlabel("true J_in − J_out"); ax[2].set_ylabel("recovered Δ_content"); ax[2].set_title("F3 content K×K (labels: power)", fontsize=9)
    w4 = res["F4"]["worlds"]
    k4 = list(w4)
    ax[3].barh(np.arange(len(k4)) + 0.2, [w4[k]["reject_family_delta"] for k in k4], 0.35, label="family Δ_talk test")
    ax[3].barh(np.arange(len(k4)) - 0.2, [w4[k]["reject_b_lab"] for k in k4], 0.35, label="room-adjusted b_lab")
    ax[3].set_yticks(np.arange(len(k4))); ax[3].set_yticklabels(k4, fontsize=6); ax[3].axvline(0.05, color="k", lw=0.5, ls=":")
    ax[3].set_title("F4 talk spins: P(reject)", fontsize=9); ax[3].legend(fontsize=6)
    fig.tight_layout(); fig.savefig(FIG / "synthetic_validation.pdf"); plt.close(fig)


def main():
    t0 = time.time()
    rng = np.random.default_rng(20261003)
    comp, nsamp, nw, labs41, rooms41 = design()
    rooms41 = np.array([0 if r == 2 else 1 for r in rooms41])
    res = {"calibration_synthetic": calibrate(rng, nsamp, comp["41"]),
           "calibration_real_median": {"|v|": 0.63, "|m_d|": 0.40, "|delta|": 0.53, "agent_daycons": 0.55},
           "sigmas": {"g": SIG_G, "o": SIG_O, "x": SIG_X}}
    print("calibration", res["calibration_synthetic"], flush=True)
    res["F1"] = f1(rng, comp, nsamp)
    res["F2"] = f2(rng, nsamp, comp["41"])
    res["F3"] = f3(rng, comp["41"], nw)
    res["F4"] = f4(rng, labs41, rooms41)
    res["F5"] = f5(rng, labs41, rooms41, nsamp)
    res["seconds"] = time.time() - t0
    (DATA / "synthetic_validation.json").write_text(json.dumps(res, indent=1))
    figure(res)
    print("done", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
