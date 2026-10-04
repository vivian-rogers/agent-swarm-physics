"""H47 synthetic validation (axis F), run before any real-data statistic.

Three families of synthetic worlds at village sampling, analysed with exactly the real-data estimators (h47lib):
  1. Coherence worlds: N = 15 agents in rooms of 5 + 10, 5 days x 10 thirty-minute windows, 32-d content with
     fluctuations in 8 dimensions (H20 lesson), Poisson statements (mean 3 per agent-window), large statement noise.
     Linear soft-spin kinetics (card, Model). Scenarios: S0 nothing; S1 global drive; S2 room broadcast coupling;
     S3 room drive (J = 0); S4 pairwise conversation coupling (2 partners); S5 mix. Mentions: Poisson for every pair,
     boosted for coupled partners in S4. Estimators: rho_w, rho_c, C_B, D_B with N1 room-relabel permutation; G with
     N2 tier permutation.
  2. A-B-A worlds (NE42 analogue): 2 rooms -> 1 room -> 2 rooms (5 days each). Variant "channel" (coupling follows the
     current room) vs "identity" (J = 0, a room drive that follows the old partition in every phase). r_X per phase.
  3. Detector worlds (day level, 80 days): room events (one room's field jumps), global events (all jump), and a
     #focus-like event (2 of 27 agents move to a new room and shift). R1_swarm (H36's R1, trailing z) vs R1_loc.
  4. Leadership worlds (intraday): two cohorts responding to a kickoff with equal or shifted onsets; symmetric and
     asymmetric sampling (sizes 5 vs 11, rates x2, one cohort starting 20 min late). L and dT50 with N5.

Usage: uv run python hypotheses/H47-room-coherence-length/analysis/synthetic.py [--fast]
Writes data/processed/H47-room-coherence-length/synthetic/synthetic_summary.json and figures/synthetic_validation.pdf
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h47lib as L  # noqa: E402  (thread caps)

sys.path.insert(0, str(L.ROOT / "hypotheses/H36-reorganization-alarm/analysis"))
from h36lib import auc, trailing_z  # noqa: E402  (read-only import)

import numpy as np  # noqa: E402

FAST = "--fast" in sys.argv
OUTD = L.OUT / "synthetic"
D, K = 32, 8


# =========================================================================================== 1. coherence worlds
SCEN = {
    "S0_none":      dict(J=0.0, Jp=0.0, ag=0.0, ar=0.0),
    "S1_global":    dict(J=0.0, Jp=0.0, ag=0.6, ar=0.0),
    "S2_roomJ":     dict(J=0.7, Jp=0.0, ag=0.15, ar=0.0),
    "S2b_roomJ_noglobal": dict(J=0.7, Jp=0.0, ag=0.0, ar=0.0),
    "S3_roomdrive": dict(J=0.0, Jp=0.0, ag=0.15, ar=0.6),
    "S4_pairwise":  dict(J=0.0, Jp=0.8, ag=0.15, ar=0.0),
    "S5_mix":       dict(J=0.45, Jp=0.0, ag=0.3, ar=0.3),
}


def ar1(T, a, rho, rng, k=K):
    x = np.zeros((T, k))
    if a == 0:
        return x
    s = a * np.sqrt(1 - rho**2)
    x[0] = rng.normal(0, a, k)
    for t in range(1, T):
        x[t] = rho * x[t - 1] + rng.normal(0, s, k)
    return x


def latent(rooms_t, J, Jp, ag, ar, partners, T, rng, phi=0.6, sig_eta=0.55):
    """rooms_t: (T, N) room labels per slot. Returns s (T, N, K)."""
    N = rooms_t.shape[1]
    hg = ar1(T, ag, 0.85, rng)
    nroom = int(rooms_t.max()) + 1
    hr = np.stack([ar1(T, ar, 0.85, rng) for _ in range(nroom)], 1)   # (T, R, K)
    s = np.zeros((T, N, K))
    s[0] = rng.normal(0, sig_eta, (N, K))
    for t in range(1, T):
        r = rooms_t[t]
        prev = s[t - 1]
        drive = np.zeros((N, K))
        if J:
            for q in np.unique(r):
                m = r == q
                drive[m] += J * prev[m].mean(0)
        if Jp:
            for i in range(N):
                if partners[i]:
                    drive[i] += Jp * prev[partners[i]].mean(0)
        drive += hg[t][None, :] + hr[t, r]
        s[t] = phi * prev + (1 - phi) * drive + rng.normal(0, sig_eta, (N, K))
    return s


def observe(s, rooms_t, days, W, rng, lam_mean=3.0, sig_eps=1.0, NS=3):
    """Statements -> Panel arrays (agent, t, day, wod, room, X, A, B, grp)."""
    T, N, _ = s.shape
    lam = rng.gamma(2.0, lam_mean / 2.0, N)
    static = rng.normal(0, 1.0, (N, D))
    rows = []
    X, A, B = [], [], []
    for t in range(T):
        for i in range(N):
            n = rng.poisson(lam[i])
            if n == 0:
                continue
            base = static[i].copy(); base[:K] += s[t, i]
            st = base[None, :] + rng.normal(0, sig_eps, (n, D))
            X.append(st.mean(0))
            a = np.full((NS, D), np.nan); b = np.full((NS, D), np.nan)
            if n >= 2:
                for sp in range(NS):
                    p = rng.permutation(n); h = n // 2
                    a[sp] = st[p[:h]].mean(0); b[sp] = st[p[h:]].mean(0)
            A.append(a); B.append(b)
            rows.append((i, t, t // W, t % W, rooms_t[t, i]))
    r = np.array(rows)
    return L.Panel(agent=r[:, 0], t=r[:, 1], day=r[:, 2], wod=r[:, 3], room=r[:, 4], X=np.array(X),
                   A=np.array(A), B=np.array(B), grp=r[:, 0].copy(), static=None, res="w30")


def make_partners(sizes, rng, k=2):
    partners, start = [], 0
    for sz in sizes:
        idx = list(range(start, start + sz))
        for i in idx:
            others = [j for j in idx if j != i]
            partners.append(list(rng.choice(others, min(k, len(others)), replace=False)) if others else [])
        start += sz
    return partners


def mentions(partners, sizes, boost, rng):
    N = sum(sizes)
    room = np.repeat(np.arange(len(sizes)), sizes)
    mw = {}
    for i in range(N):
        for j in range(i + 1, N):
            if room[i] != room[j]:
                continue
            lam = 1.0 + (boost if (j in partners[i] or i in partners[j]) else 0.0)
            mw[(i, j)] = float(rng.poisson(lam))
    return mw


def coherence_world(scn, rng, sizes=(5, 10), days=5, W=10, n_perm=100):
    p = SCEN[scn]
    N = sum(sizes); T = days * W
    rooms_t = np.tile(np.repeat(np.arange(len(sizes)), sizes), (T, 1))
    partners = make_partners(sizes, rng) if p["Jp"] else [[] for _ in range(N)]
    s = latent(rooms_t, p["J"], p["Jp"], p["ag"], p["ar"], partners, T, rng)
    P = observe(s, rooms_t, days, W, rng)
    mw = mentions(partners if p["Jp"] else make_partners(sizes, rng), sizes, 6.0 if p["Jp"] else 0.0, rng)
    res = L.panel_coherence(P, level=0, mw=mw, n_perm=n_perm, rng=rng)
    o = res["obs"]
    return dict(rho_w=o["rho_w"], rho_c=o["rho_c"], C_B=o["C_B"], D_B=o["D_B"], G=o.get("G", np.nan),
                p_DB=res.get("p_DB", np.nan), p_G=res.get("p_G_low", np.nan))


# =========================================================================================== 2. A-B-A worlds
def aba_world(variant, rng, sizes=(5, 10), days=5, W=10, n_perm=100):
    N = sum(sizes); Tp = days * W
    part = np.repeat(np.arange(len(sizes)), sizes)
    rooms_t = np.vstack([np.tile(part, (Tp, 1)), np.zeros((Tp, N), int), np.tile(part, (Tp, 1))])
    T = 3 * Tp
    if variant == "channel":
        s = latent(rooms_t, 0.7, 0.0, 0.15, 0.0, [[] for _ in range(N)], T, rng)
    else:   # identity drive follows the old partition in every phase, no coupling
        s = latent(np.tile(part, (T, 1)), 0.0, 0.0, 0.15, 0.6, [[] for _ in range(N)], T, rng)
    out = {}
    for ph, lab in enumerate(("A1", "B", "A2")):
        sl = slice(ph * Tp, (ph + 1) * Tp)
        P = observe(s[sl], rooms_t[sl], days, W, rng)
        dX, dA, dB, okX, okS = L.deviations(P, 0)
        C = L.contributions(P, dX, dA, dB, okX, okS)
        pmap = {i: int(part[i]) for i in range(N)}
        r = L.partition_ratio(C, pmap)
        nul = [L.partition_ratio(C, L.permute_partition(pmap, rng))["r_X"] for _ in range(n_perm)]
        out[lab] = dict(r_X=r["r_X"], null_med=float(np.nanmedian(nul)))
    out["DiD"] = out["B"]["r_X"] - 0.5 * (out["A1"]["r_X"] + out["A2"]["r_X"])
    return out


# =========================================================================================== 3. detector worlds
def detector_world(rng, kind="two_room", days=80, n_rand=200):
    """Day-level agent vectors with room events, global events and placebo days. Returns score arrays."""
    if kind == "two_room":
        sizes = (5, 10)
    else:
        sizes = (27,)
    N = sum(sizes)
    room = np.repeat(np.arange(len(sizes)), sizes)
    rooms_d = np.tile(room, (days, 1))
    static = rng.normal(0, 1.0, (N, D))
    g = np.cumsum(rng.normal(0, 0.15, (days, D)), 0)          # slow global drift
    nroom = 3
    h = np.cumsum(rng.normal(0, 0.15, (days, nroom, D)), 0)   # slow room drifts
    ev_days = list(range(14, days - 4, 8))
    events = []
    for k, e in enumerate(ev_days):
        if kind == "two_room":
            if k % 2 == 0:
                r = int(rng.integers(0, 2))
                h[e:, r] += rng.normal(0, 1.0, D) * 0.9         # one room's field jumps
                events.append((e, "room"))
            else:
                g[e:] += rng.normal(0, 1.0, D) * 0.9            # global jump (goal change)
                events.append((e, "global"))
        else:
            if k % 2 == 0:
                mv = rng.choice(N, 2, replace=False)            # #focus-like: 2 agents move to room 1 and shift
                rooms_d[e:e + 4, mv] = 1
                h[e:e + 4, 1] = h[e:e + 4, 0] + rng.normal(0, 1.0, D) * 0.9
                events.append((e, "small_room"))
            else:
                g[e:] += rng.normal(0, 1.0, D) * 0.9
                events.append((e, "global"))
    V = static[None] + g[:, None, :] + h[np.arange(days)[:, None], rooms_d] + rng.normal(0, 1.6, (days, N, D))
    V = V - V.reshape(-1, D).mean(0)
    V = V / np.linalg.norm(V, axis=2, keepdims=True)
    r1 = np.full(days, np.nan); rl = np.full(days, np.nan)
    per_room = {r: np.full(days, np.nan) for r in range(nroom)}
    for d in range(1, days):
        r1[d] = L.r1_shift(V[d].mean(0), V[d - 1].mean(0))
        if len(np.unique(rooms_d[d])) > 1 or len(np.unique(rooms_d[d - 1])) > 1:
            rl[d], _ = L.r1_loc(V[d], V[d - 1], rooms_d[d], rooms_d[d - 1], rng, n_rand=n_rand)
        for r in np.unique(rooms_d[d]):
            m = rooms_d[d] == r
            if m.sum() >= 2:
                per_room[r][d] = L.r1_shift(V[d][m].mean(0), V[d - 1][m].mean(0))
    z = trailing_z(r1)
    zr_all = np.vstack([trailing_z(per_room[r]) for r in range(nroom)])
    with np.errstate(all="ignore"):
        naive = np.where(np.isfinite(zr_all).any(0), np.nanmax(np.where(np.isfinite(zr_all), zr_all, -np.inf), 0), np.nan)
    evd = {e for e, _ in events}
    plac = [d for d in range(12, days) if min(abs(d - e) for e in evd) >= 3]
    return dict(z=z, rl=rl, naive=naive, events=events, plac=plac, multiroom=np.array([len(np.unique(rooms_d[d])) > 1 for d in range(days)]))


# =========================================================================================== 4. leadership worlds
def lead_world(rng, variant, lead_min=0.0, n_perm=200, sig=0.7):
    sizes = (5, 11)
    if variant == "sym":
        rates = (1 / 12, 1 / 12); late = (0.0, 0.0); sizes = (8, 8)
    elif variant == "asym":
        rates = (1 / 8, 1 / 16); late = (0.0, 0.0)
    else:   # asym + late start in cohort 1
        rates = (1 / 8, 1 / 16); late = (0.0, 20.0)
    delta = rng.normal(0, 1, D); delta /= np.linalg.norm(delta)
    y0, theta, dur = 0.4, 45.0, 240.0
    taus, Xs, ags = [], [], []
    Xpre, apre, Xpost, apost = [], [], [], []
    coh = {}
    a = 0
    for c in (0, 1):
        for _ in range(sizes[c]):
            coh[a] = c
            off = rng.normal(0, 0.35 * sig, D)
            t0 = (lead_min if c == 1 else 0.0) + rng.normal(0, 10.0)
            n = rng.poisson(rates[c] * dur)
            tt = np.sort(rng.uniform(late[c], dur, n))
            y = np.where(tt >= t0, y0 + (1 - y0) * (1 - np.exp(-(tt - t0) / theta)), 0.0)
            Xs.append(off + y[:, None] * delta + rng.normal(0, sig, (n, D))); taus.append(tt); ags += [a] * n
            Xpre.append(off + rng.normal(0, sig, (20, D))); apre += [a] * 20
            Xpost.append(off + delta + rng.normal(0, sig, (40, D))); apost += [a] * 40
            a += 1
    ev = dict(tau=np.concatenate(taus), X=np.vstack(Xs), agent=np.array(ags), Xpre=np.vstack(Xpre), apre=np.array(apre),
              Xpost=np.vstack(Xpost), apost=np.array(apost), coh=coh)
    r = L.lead_test(ev, rng, n_perm=n_perm, n_boot=0)
    return dict(L=r["obs"]["L"], dT50=r["obs"]["dT50"], p_L=r["p_L"], p_T50=r["p_T50"])


# =========================================================================================== main
def main():
    t0 = time.time()
    rng = np.random.default_rng(L.SEED)
    nw = 12 if FAST else 40
    summ = {"coherence": {}, "aba": {}, "detector": {}, "leadership": {}}
    raw = {"coherence": {}}
    for scn in SCEN:
        rs = [coherence_world(scn, rng, n_perm=60 if FAST else 100) for _ in range(nw)]
        arr = {k: np.array([r[k] for r in rs], float) for k in rs[0]}
        raw["coherence"][scn] = arr
        summ["coherence"][scn] = {
            "rho_w": float(np.nanmedian(arr["rho_w"])), "rho_c": float(np.nanmedian(arr["rho_c"])),
            "C_B_med": float(np.nanmedian(arr["C_B"])), "C_B_iqr": [float(np.nanpercentile(arr["C_B"], 25)), float(np.nanpercentile(arr["C_B"], 75))],
            "rej_DB_05": float(np.nanmean(arr["p_DB"] < 0.05)), "G_med": float(np.nanmedian(arr["G"])),
            "G_iqr": [float(np.nanpercentile(arr["G"], 25)), float(np.nanpercentile(arr["G"], 75))],
            "rej_G_05": float(np.nanmean(arr["p_G"] < 0.05)), "n": nw}
        print(scn, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in summ["coherence"][scn].items()}, flush=True)
    for var in ("channel", "identity"):
        rs = [aba_world(var, rng, n_perm=60 if FAST else 100) for _ in range(max(nw // 2, 8))]
        summ["aba"][var] = {ph: float(np.nanmedian([r[ph]["r_X"] for r in rs])) for ph in ("A1", "B", "A2")}
        summ["aba"][var]["DiD_med"] = float(np.nanmedian([r["DiD"] for r in rs]))
        summ["aba"][var]["DiD_gt04"] = float(np.nanmean([r["DiD"] > 0.4 for r in rs]))
        raw.setdefault("aba", {})[var] = rs
        print("ABA", var, summ["aba"][var], flush=True)
    for kind in ("two_room", "focus_like"):
        zr, zg, lr, lg, zp, lp, nr, ng, npl = [], [], [], [], [], [], [], [], []
        hits = {"swarm_room": [], "loc_room": []}
        for _ in range(6 if FAST else 20):
            w = detector_world(rng, kind, n_rand=100 if FAST else 200)
            for e, typ in w["events"]:
                if typ == "global":
                    zg.append(w["z"][e]); lg.append(w["rl"][e]); ng.append(w["naive"][e])
                else:
                    zr.append(w["z"][e]); lr.append(w["rl"][e]); nr.append(w["naive"][e])
            plac = [d for d in w["plac"] if w["multiroom"][d] or w["multiroom"][d - 1]] if kind != "two_room" else w["plac"]
            zp += [w["z"][d] for d in plac]; lp += [w["rl"][d] for d in plac]; npl += [w["naive"][d] for d in plac]
        zr, zg, lr, lg, zp, lp, nr, ng, npl = map(lambda x: np.array(x, float), (zr, zg, lr, lg, zp, lp, nr, ng, npl))
        summ["detector"][kind] = {
            "AUC_swarm_room": auc(zr, zp), "AUC_loc_room": auc(lr, lp),
            "AUC_swarm_global": auc(zg, zp), "AUC_loc_global": auc(lg, lp),
            "AUC_naive_room": auc(nr, npl), "AUC_naive_global": auc(ng, npl),
            "AUC_comb_room": auc(np.fmax(zr, lr), np.fmax(zp, lp)), "AUC_comb_global": auc(np.fmax(zg, lg), np.fmax(zp, lp)),
            "hit_naive_room_z3": float(np.nanmean(nr >= 3)), "far_naive_z3": float(np.nanmean(npl >= 3)),
            "n_room": int(np.isfinite(zr).sum()), "n_global": int(np.isfinite(zg).sum()), "n_plac": int(np.isfinite(zp).sum()),
            "hit_swarm_room_z3": float(np.nanmean(zr >= 3)), "hit_loc_room_z2": float(np.nanmean(lr >= 2)),
            "far_swarm_z3": float(np.nanmean(zp >= 3)), "far_loc_z2": float(np.nanmean(lp >= 2)),
            "far_loc_z3": float(np.nanmean(lp >= 3)), "hit_loc_room_z3": float(np.nanmean(lr >= 3))}
        print("DET", kind, {k: round(v, 3) for k, v in summ["detector"][kind].items()}, flush=True)
    nl = 30 if FAST else 100
    for var in ("sym", "asym", "asym_late"):
        for lead in (0.0, 30.0):
            rs = [lead_world(rng, var, lead, n_perm=100 if FAST else 200) for _ in range(nl)]
            pL = np.array([r["p_L"] for r in rs], float); pT = np.array([r["p_T50"] for r in rs], float)
            key = f"{var}_lead{int(lead)}"
            summ["leadership"][key] = {"rej_L_05": float(np.nanmean(pL < 0.05)), "rej_T50_05": float(np.nanmean(pT < 0.05)),
                                       "L_med": float(np.nanmedian([r["L"] for r in rs])),
                                       "dT50_med": float(np.nanmedian([r["dT50"] for r in rs])),
                                       "L_pos_share": float(np.nanmean([r["L"] > 0 for r in rs])), "n": nl}
            print("LEAD", key, {k: round(v, 3) for k, v in summ["leadership"][key].items()}, flush=True)
    summ["params"] = dict(scenarios=SCEN, coherence="N=15 (5+10), 5 days x 10 windows, phi=0.6, sig_eta=0.55, "
                          "statements Poisson Gamma(2, mean 3), sig_eps=1 per coord, D=32, K=8 active dims",
                          detector="80 days, events every 8 days alternating room/global (jump 0.9 per coord), day noise 1.6",
                          leadership="cohorts 5 vs 11 (asym) or 8 vs 8 (sym); rates 1/8 vs 1/16 min; y0=0.4, theta=45 min, "
                          "sig=0.7 per coord, |delta|=1; late start 20 min; lead 30 min", fast=FAST,
                          seconds=round(time.time() - t0, 1))
    OUTD.mkdir(parents=True, exist_ok=True)
    L.jdump(summ, OUTD / "synthetic_summary.json")
    np.savez_compressed(OUTD / "synthetic_raw.npz", **{f"coh_{s}_{k}": v for s, d in raw["coherence"].items() for k, v in d.items()})
    figure(summ, raw)
    print("done", round(time.time() - t0, 1), "s")


def figure(summ, raw):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    L.FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(1, 4, figsize=(13, 3.2))
    names = list(SCEN)
    lab = ["none", "global", "room J", "room J, no glob.", "room drive", "pairwise", "mix"]
    data = [raw["coherence"][s]["C_B"] for s in names]
    ax[0].boxplot([d[np.isfinite(d)] for d in data], showfliers=False)
    ax[0].set_xticks(range(1, 8)); ax[0].set_xticklabels(lab, rotation=40, ha="right", fontsize=8)
    ax[0].axhline(0.3, ls="--", c="gray", lw=0.8); ax[0].set_ylim(-1.5, 2.0)
    ax[0].set_title("room contrast C_B = rho_c / rho_w", fontsize=9)
    dataG = [raw["coherence"][s]["G"] for s in names]
    ax[1].boxplot([d[np.isfinite(d)] for d in dataG], showfliers=False)
    ax[1].set_xticks(range(1, 8)); ax[1].set_xticklabels(lab, rotation=40, ha="right", fontsize=8)
    ax[1].axhline(0.6, ls="--", c="gray", lw=0.8); ax[1].set_ylim(-1.5, 2.5)
    ax[1].set_title("tier ratio G = rho_low / rho_high", fontsize=9)
    det = summ["detector"]
    cats = ["room (2 rooms)", "global", "focus-like", "global (27)"]
    sw = [det["two_room"]["AUC_swarm_room"], det["two_room"]["AUC_swarm_global"], det["focus_like"]["AUC_swarm_room"], det["focus_like"]["AUC_swarm_global"]]
    lo = [det["two_room"]["AUC_loc_room"], det["two_room"]["AUC_loc_global"], det["focus_like"]["AUC_loc_room"], det["focus_like"]["AUC_loc_global"]]
    na = [det["two_room"]["AUC_naive_room"], det["two_room"]["AUC_naive_global"], det["focus_like"]["AUC_naive_room"], det["focus_like"]["AUC_naive_global"]]
    x = np.arange(4)
    ax[2].bar(x - 0.27, sw, 0.27, label="R1 swarm", color="#888")
    ax[2].bar(x, na, 0.27, label="R1 per-room", color="#9ae6b4")
    ax[2].bar(x + 0.27, lo, 0.27, label="R1 loc", color="#2b6cb0")
    ax[2].set_xticks(x); ax[2].set_xticklabels(cats, rotation=30, ha="right", fontsize=8)
    ax[2].axhline(0.5, c="k", lw=0.6); ax[2].set_ylim(0, 1.05); ax[2].legend(fontsize=7)
    ax[2].set_title("detector AUC (day 0 vs placebo)", fontsize=9)
    ld = summ["leadership"]
    keys = ["sym_lead0", "asym_lead0", "asym_late_lead0", "asym_lead30", "asym_late_lead30"]
    labs = ["null sym", "null asym", "null asym+late", "lead 30 asym", "lead 30 late"]
    x = np.arange(len(keys))
    ax[3].bar(x - 0.18, [ld[k]["rej_L_05"] for k in keys], 0.36, label="L", color="#2b6cb0")
    ax[3].bar(x + 0.18, [ld[k]["rej_T50_05"] for k in keys], 0.36, label="dT50", color="#c05621")
    ax[3].axhline(0.05, c="k", lw=0.6, ls="--")
    ax[3].set_xticks(x); ax[3].set_xticklabels(labs, rotation=30, ha="right", fontsize=8)
    ax[3].set_ylim(0, 1.05); ax[3].legend(fontsize=7); ax[3].set_title("leader detected (p < 0.05)", fontsize=9)
    fig.tight_layout()
    fig.savefig(L.FIG / "synthetic_validation.pdf"); fig.savefig(L.FIG / "synthetic_validation.png", dpi=130)


def lead_calibrated():
    """Post hoc (after seeing the real per-statement projection noise, 0.17-0.6, median ~0.25): leadership power at
    sig = 0.25 and 0.4. Does not change any verdict; used only to read the null result."""
    rng = np.random.default_rng(L.SEED + 99)
    out = {}
    for sig in (0.25, 0.4):
        for var in ("asym", "asym_late"):
            for lead in (0.0, 15.0, 30.0):
                rs = [lead_world(rng, var, lead, n_perm=200, sig=sig) for _ in range(60)]
                pL = np.array([r["p_L"] for r in rs], float)
                out[f"sig{sig}_{var}_lead{int(lead)}"] = {"rej_L_05": float(np.nanmean(pL < 0.05)), "L_med": float(np.nanmedian([r["L"] for r in rs])), "n": 60}
                print(sig, var, lead, out[f"sig{sig}_{var}_lead{int(lead)}"], flush=True)
    L.jdump(out, OUTD / "lead_calibrated_posthoc.json")


if __name__ == "__main__":
    if "--lead-calib" in sys.argv:
        lead_calibrated()
    else:
        main()
