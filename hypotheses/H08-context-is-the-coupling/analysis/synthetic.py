"""H08 synthetic validation (axis F), run before any real-data fit.

  uv run python hypotheses/H08-context-is-the-coupling/analysis/synthetic.py c8 [--reps 8]
  uv run python hypotheses/H08-context-is-the-coupling/analysis/synthetic.py c9

C8: real non-holdout skeletons (#38, 15 days of #51): real activity states, real turns and the real kicks (kept as
direct hits so they stay out of the controls, but relabelled so they are not in the treated set). Synthetic kicks go to
nudger-like cells (agent idle or silent at m-1 and for >= 8 of the previous 15 min; no real direct kick in [-30, +60];
>= 90 min apart per agent). After each kick, inactive minutes become active with probability P_RESP for 60 min from
the response onset, which is set by the truth:
  context   the read-out minute (first turn whose call started after the kick)
  immediate the kick minute
  delay8    8 minutes after the kick
  memory    the minute after the agent's next consolidation turn
Then the full C8 pipeline (H04 kernel, F_obs, Phi tests, day-split CV) is run on the synthetic kicks.

C9: real #38 turns; synthetic messages at random times; recipients respond (talk + address the sender) with
probability Q at the read-out turn ("context") or, for a "common cause" latent event, sender and recipient both respond
to the latent event at their own read-out turns (the recipient's talk is not caused by the sender's message).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c8lib import *  # noqa: E402,F403

P_RESP = 0.12
N_KICK = {38: 200, 51: 300}
TRUTHS = ["context", "immediate", "delay8", "memory"]
MATCH = {"fine": True, "pause_matched": True}     # amendment A1 (2026-10-04): finer pre-treatment matching
B = 200
SDIR = OUT / "synthetic"


def candidate_cells(P: Prep, mode: str = "nudger"):
    """Control-eligible agent-minutes (day, row, minute) inactive at m-1; mode "nudger" also needs >= 8 of the previous
    15 minutes inactive (the nudger's idle trigger); mode "random" takes any inactive-at-m-1 cell."""
    out = []
    for k, d in enumerate(P.D):
        st = d.state
        inact = (st <= 2).astype(np.int64)
        win15 = h04lib.window_sum(inact, -15, -1)
        dirw = h04lib.window_sum(d.hits_dir, -30, 60)
        nm = st.shape[1]
        for i in range(st.shape[0]):
            m = np.arange(15, nm - 61)
            ok = (st[i, m - 1] <= 2) & (dirw[i, m] == 0)
            if mode == "nudger":
                ok &= win15[i, m] >= 8
            for mm in m[ok]:
                out.append((k, i, int(mm)))
    return out


def pick_kicks(cands, n, rng):
    perm = rng.permutation(len(cands))
    last = {}
    sel = []
    for j in perm:
        k, i, m = cands[j]
        if any(abs(m - x) < 90 for x in last.get((k, i), [])):
            continue
        last.setdefault((k, i), []).append(m)
        sel.append(cands[j])
        if len(sel) >= n:
            break
    return sel


def onset_minute(P: Prep, truth, k, i, m, tk):
    d = P.D[k]
    tr = P.T.get((int(d.agents[i]), d.pt_date))
    mstart = P.win_us[k] + m * 60 * US
    if truth == "immediate":
        return 0
    if truth == "delay8":
        return 8
    if tr is None:
        return None
    if truth == "context":
        idx = int(readout_idx(tr, np.array([tk]))[0])
        return None if idx >= len(tr.t) else int((tr.t[idx] - mstart) // (60 * US))
    if truth == "memory":
        j = np.nonzero((tr.t > tk) & tr.cons)[0]
        return None if not len(j) else int((tr.t[j[0]] - mstart) // (60 * US)) + 1
    raise ValueError(truth)


CONFIGS = ([("random", t, 0.35) for t in TRUTHS] + [("random", t, P_RESP) for t in TRUTHS]
           + [("nudger", "null", P_RESP), ("nudger", "context", P_RESP)])


def run_c8(g: int, days: list[str], reps: int, seed: int, configs=CONFIGS):
    t0 = time.time()
    P = Prep(days)
    real = P.resp.with_columns(pl.when(pl.col("kind") == "nudge").then(pl.lit("human")).otherwise(pl.col("kind")).alias("kind"))
    P.attach(real)
    cands = {m: candidate_cells(P, m) for m in ("nudger", "random")}
    states0 = [d.state.copy() for d in P.D]
    rng = np.random.default_rng(seed)
    res = []
    for rep in range(reps):
        kicks_by = {m: pick_kicks(cands[m], N_KICK[g], rng) for m in cands}
        tks_by = {m: [P.win_us[k] + mm * 60 * US + int(rng.uniform(0, 60) * US) for k, i, mm in kicks_by[m]] for m in cands}
        for sel, truth, p_resp in configs:
            kicks, tks = kicks_by[sel], tks_by[sel]
            for k, d in enumerate(P.D):
                d.state = states0[k].copy()
            r2 = np.random.default_rng(seed * 1000 + rep)
            n_resp = 0
            for (k, i, m), tk in zip(kicks, tks):
                if truth == "null":
                    continue
                on = onset_minute(P, truth, k, i, m, tk)
                if on is None:
                    continue
                st = P.D[k].state
                lo, hi = m + max(on, 0), min(m + on + 60, st.shape[1])
                if lo >= hi:
                    continue
                seg = st[i, lo:hi]
                flip = (seg <= 2) & (r2.uniform(size=hi - lo) < p_resp)
                seg[flip] = 3
                n_resp += 1
            syn = pl.DataFrame({"day": [k for k, i, m in kicks], "minute": [m for k, i, m in kicks],
                                "row": [i for k, i, m in kicks],
                                "agent": [int(P.D[k].agents[i]) for k, i, m in kicks],
                                "kind": ["nudge"] * len(kicks), "role": ["target"] * len(kicks),
                                "msg": list(range(50_000_000, 50_000_000 + len(kicks)))},
                               schema=real.schema)
            for j, tk in enumerate(tks):
                P.msg_t[50_000_000 + j] = tk
            allr = pl.concat([real, syn])
            P.attach(allr)
            c, ctl = build_kernel_inputs(P, **MATCH)
            sets = h04lib.build_sets(P.D, allr, c)
            ids = sets["nudge_target_iso"]["ids"]
            nd = len(P.D)
            r = matched(c, ctl, ids, nd, "syn")
            W = h04lib.boot_weights(nd, B, seed=seed + rep)
            Gb = h04lib.curves(r, W)
            ro = treated_readout(P, c, ids, syn)
            h = headroom_profiles(P, c, seed=rep)
            hk = hkey_cells(P, c, ids)
            Mhr = F_hr_cells(ro["tau_obs"], hk // 16, h, hk)
            CM = control_matrix(c, ctl, ids)
            Fb = {"obs": F_boot(ro["tau_obs"], ro["day"], W, nd), "hr": F_hr_boot(Mhr, ro["day"], W, nd)}
            st_ = shape_tests(Gb, Fb, W)
            cv = cross_validate(r, Gb, ro["tau_obs"], ro["day"], nd, Mhr, CM, n_split=60, seed=rep) if truth != "null" else {}
            res.append({"period": gname(g), "rep": rep, "selection": sel, "truth": truth, "p": p_resp, "match": dict(MATCH),
                        "n_kicks": len(ids), "n_resp": n_resp,
                        "A30": st_["A30"], "plateau": st_["plateau_mean"], "pre": ci(np.nansum(Gb[:, L0 - 15:L0], 1)),
                        "phi15": st_["phi_1_5"], "phi15_pred": st_["phi_1_5_pred_obs"],
                        "phi15_diff": st_["phi_1_5_diff_obs"], "phi615": st_["phi_6_15"],
                        "phi15_pred_hr": st_["phi_1_5_pred_hr"], "phi15_diff_hr": st_["phi_1_5_diff_hr"],
                        "phi615_pred_hr": st_["phi_6_15_pred_hr"], "phi615_diff_hr": st_["phi_6_15_diff_hr"],
                        "phi615_pred": st_["phi_6_15_pred_obs"], "phi615_diff": st_["phi_6_15_diff_obs"],
                        "t_half_obs": st_["t_half_obs"], "t_half_hr": st_["t_half_hr"], "cv": cv,
                        "G": Gb[0].tolist(), "Fhr": Fb["hr"][0].tolist(), "F": Fb["obs"][0].tolist()})
            best = max(cv.get("best_share", {"-": 0}).items(), key=lambda x: x[1]) if cv else "-"
            print(f"[{gname(g)} rep {rep} {sel} {truth} p={p_resp}] kicks {len(ids)} A30 {st_['A30'][0]:.2f} "
                  f"phi15 {st_['phi_1_5'][0]:.2f} hr {st_['phi_1_5_pred_hr'][0]:.2f} step {st_['phi_1_5_pred_obs'][0]:.2f} | "
                  f"6-15 {st_['phi_6_15'][0]:.2f} hr {st_['phi_6_15_pred_hr'][0]:.2f} best {best} {time.time() - t0:.0f}s",
                  flush=True)
    for k, d in enumerate(P.D):
        d.state = states0[k]
    return res


def summarize_c8(res):
    out = {}
    keys = sorted({(r["period"], r["selection"], r["truth"], r["p"]) for r in res})
    for g, sel, truth, p in keys:
        rr = [r for r in res if (r["period"], r["selection"], r["truth"], r["p"]) == (g, sel, truth, p)]
        def cov(name):
            return float(np.mean([np.isfinite(r[name][1]) and r[name][1] <= 0 <= r[name][2] for r in rr]))
        ent = {"reps": len(rr), "A30_mean": float(np.mean([r["A30"][0] for r in rr])),
               "A30_sig_share": float(np.mean([r["A30"][1] > 0 for r in rr])),
               "pre15_mean": float(np.mean([r["pre"][0] for r in rr])),
               "phi15_mean": float(np.nanmean([r["phi15"][0] for r in rr])),
               "phi15_pred_hr_mean": float(np.nanmean([r["phi15_pred_hr"][0] for r in rr])),
               "phi15_pred_step_mean": float(np.nanmean([r["phi15_pred"][0] for r in rr])),
               "phi615_mean": float(np.nanmean([r["phi615"][0] for r in rr])),
               "phi615_pred_hr_mean": float(np.nanmean([r["phi615_pred_hr"][0] for r in rr])),
               "phi15_diff_hr_covers0": cov("phi15_diff_hr"), "phi615_diff_hr_covers0": cov("phi615_diff_hr"),
               "phi15_diff_step_covers0": cov("phi15_diff")}
        # pooled curve over reps (bias check independent of per-rep noise)
        G = np.nanmean([r["G"] for r in rr], 0); Fh = np.nanmean([r["Fhr"] for r in rr], 0)
        ent["pooled_phi15"] = float(phi(G[None], 1, 5)[0]); ent["pooled_phi15_pred_hr"] = float(phi(Fh[None], 1, 5)[0])
        ent["pooled_phi615"] = float(phi(G[None], 6, 15)[0]); ent["pooled_phi615_pred_hr"] = float(phi(Fh[None], 6, 15)[0])
        if rr[0]["cv"]:
            ent["best_share_mean"] = {m: float(np.mean([r["cv"].get("best_share", {}).get(m, 0) for r in rr])) for m in MODELS}
            ent["ctx_beats_share_mean"] = {m: float(np.nanmean([r["cv"].get("ctx_wins_share", {}).get(m, np.nan) for r in rr]))
                                           for m in MODELS if m != "ctx"}
            ent["ratio_to_ctx_median"] = {m: float(np.nanmedian([r["cv"].get("ratio_to_ctx", {}).get(m, np.nan) for r in rr]))
                                          for m in MODELS}
        out[f"{g}/{sel}/{truth}/p{p}"] = ent
    return out


# ----------------------------------------------------------------------------- C9

def run_c9(g: int, days: list[str], reps: int, seed: int, q: float = 0.15):
    T0 = build_turns(days)
    win = windows(days)
    rng = np.random.default_rng(seed)
    out = []
    for truth in ("context", "common_cause", "null"):
        for rep in range(reps):
            T = {k: Turns(t=v.t, s=v.s, talk=v.talk.copy(), pause=v.pause, pause_s=v.pause_s, cons=v.cons,
                          ment=v.ment.copy(), msg=v.msg, unc=v.unc, ctx=v.ctx) for k, v in T0.items()}
            units = []
            for d in days:
                ags = [a for (a, dd) in T if dd == d]
                if len(ags) < 3:
                    continue
                ws, we = win[d]
                n = int((we - ws) / US / 3600 * 6)          # ~6 synthetic messages per hour
                for _ in range(n):
                    j = int(rng.choice(ags))
                    tc = int(rng.uniform(ws, we))
                    if truth == "common_cause":
                        trj = T[(j, d)]
                        ij = int(readout_idx(trj, np.array([tc]))[0])
                        if ij >= len(trj.t):
                            continue
                        tm = int(trj.t[ij]) + 1                 # the sender posts at its read-out of the latent event
                    else:
                        tm = tc
                    for i in ags:
                        if i == j:
                            continue
                        tr = T[(i, d)]
                        if truth == "context":
                            ix = int(readout_idx(tr, np.array([tm]))[0])
                            if ix < len(tr.t) and rng.uniform() < q:
                                tr.talk[ix] = True; tr.ment[ix] |= np.uint64(1 << j)
                        elif truth == "common_cause":
                            ix = int(readout_idx(tr, np.array([tc]))[0])
                            if ix < len(tr.t) and rng.uniform() < q:
                                tr.talk[ix] = True
                        units.append((i, d, tm, j))
            # measure
            rows = {"real": [], "pseudo": []}
            by = {}
            for (i, d, tm, j) in units:
                by.setdefault((i, d), []).append((tm, j))
            for (i, d), lst in by.items():
                tr = T[(i, d)]
                tm = np.array([x[0] for x in lst], np.int64); sj = np.array([x[1] for x in lst], np.int16)
                ws, we = win[d]
                tp = tm + (rng.uniform(20, 60, len(tm)) * 60 * US * rng.choice([-1, 1], len(tm))).astype(np.int64)
                for lab, tt in (("real", tm), ("pseudo", tp)):
                    ok = (tt >= ws) & (tt <= we)
                    idx = readout_idx(tr, tt)
                    n = len(tr.t)
                    prev = np.clip(idx - 1, 0, n - 1)
                    infl = (idx > 0) & (idx < n) & (tr.t[prev] > tt)
                    for o in range(-2, 4):
                        jx = idx + o - 1
                        v = ok & infl & (jx >= 0) & (jx < n)
                        jj = np.clip(jx, 0, n - 1)
                        rows[lab].append(np.stack([np.full(v.sum(), o), tr.talk[jj][v].astype(int),
                                                   ((tr.ment[jj][v] >> sj[v].astype(np.uint64)) & np.uint64(1)).astype(int)], 1))
            R = {lab: np.concatenate(v) for lab, v in rows.items()}
            G = {}
            for o in range(-2, 4):
                a = R["real"][R["real"][:, 0] == o]; p = R["pseudo"][R["pseudo"][:, 0] == o]
                G[o] = (a[:, 1].mean() - p[:, 1].mean(), a[:, 2].mean() - p[:, 2].mean())
            out.append({"truth": truth, "rep": rep, "q": q, "G_talk": {o: G[o][0] for o in G}, "G_addr": {o: G[o][1] for o in G},
                        "D_talk": G[1][0] - G[0][0], "D_addr": G[1][1] - G[0][1], "n_units": len(units)})
            print(f"[C9 {truth} rep {rep}] D_talk {G[1][0] - G[0][0]:+.4f} D_addr {G[1][1] - G[0][1]:+.4f} "
                  f"G_talk(-1,0,1,2) {G[-1][0]:+.4f} {G[0][0]:+.4f} {G[1][0]:+.4f} {G[2][0]:+.4f}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["c8", "c9"])
    ap.add_argument("--reps", type=int, default=6)
    a = ap.parse_args()
    SDIR.mkdir(parents=True, exist_ok=True)
    if a.what == "c8":
        res = []
        res += run_c8(38, period_days(38), a.reps, 3801)
        res += run_c8(51, period_days(51)[:15], a.reps, 5101)
        summ = summarize_c8(res)
        jdump({"runs": res, "summary": summ, "P_RESP": P_RESP, "N_KICK": N_KICK}, SDIR / "c8_synthetic.json")
        for k, v in summ.items():
            print(k, v)
        write_provenance("synthetic/c8_synthetic.json", "hypotheses/H08-context-is-the-coupling/analysis/synthetic.py",
                         ["activity_bins", "actions", "events_core", "chat_core", "exposure", "calendar", "roster"],
                         {"P_RESP": P_RESP, "N_KICK": N_KICK, "reps": a.reps, "truths": TRUTHS, "B": B,
                          "skeletons": "G38 (all non-holdout days), G51 first 15 non-holdout days"})
    else:
        res = run_c9(38, period_days(38), a.reps, 3809)
        jdump({"runs": res}, SDIR / "c9_synthetic.json")
        write_provenance("synthetic/c9_synthetic.json", "hypotheses/H08-context-is-the-coupling/analysis/synthetic.py",
                         ["actions", "events_core", "calendar"], {"q": 0.15, "reps": a.reps, "skeleton": "G38 turns"})


if __name__ == "__main__":
    main()
