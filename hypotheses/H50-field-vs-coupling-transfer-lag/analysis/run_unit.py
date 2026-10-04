"""H50 replication pipeline: one estimator for every eligible non-holdout unit.

Per unit (scheme output units/<unit>.npz):
  Part A  swarm FIR (activity, talk) on edge / pause / human / nudge / platform inputs: dead time, gain, decay,
          corner, pre-trend, ringing (+ day-bootstrap CIs); Welch sums for regime-pooled Bode plots.
  Part B  gate on exogenous inputs (human messages: named target vs others; nudges: target vs bystander):
          boundary-RD hop kernel (talk, act), onset hop.
  C2      gate on peer chat: hop kernel (talk K=6, act K=3), W = 1.5 x median call interval; variants
          (no-reply sources, high-confidence starts, mention vs not, 3W); kappa; read-out delay quantiles.
  C1      equal-time co-movement S (activity: span / full / trim; talk: span / full), measured-field share f_F
          vs shifted-input null, lagged peer share; f_F without the nudge classes (NE43).
  CF      coupling share of talk co-movement from the gated hop-1 kernel (raw and after the field fit).
  HH190   per-agent hop-1 talk jump (units with >= 3000 pairs).
Outputs: data/processed/H50-field-vs-coupling-transfer-lag/G<NN>/<unit>.json (+ <unit>_welch.npz).

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/run_unit.py [--only 38a,51c] [--jobs 2]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "POLARS_MAX_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h50lib as L  # noqa: E402
from build import load_unit  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
NBOOT = 200


def tolist(d):
    if isinstance(d, dict):
        return {k: tolist(v) for k, v in d.items() if not (isinstance(v, np.ndarray) and v.ndim > 1 and v.size > 2000)}
    if isinstance(d, np.ndarray):
        return d.tolist()
    if isinstance(d, (np.floating, np.integer)):
        return d.item()
    if isinstance(d, (list, tuple)):
        return [tolist(x) for x in d]
    return d


def responding_mask(U, keys, te, rec, snd):
    """True where the source message's sender had newly read a message from the recipient at one of its last two
    receiving calls before posting (the source is a reply to the recipient)."""
    m, mp = U["msgs"], U["mpairs"]
    c = U["calls"]
    # read-out call index for every (msg, recipient) pair
    i1_all = mp["turn_pos"]
    s_all = m["sender"][mp["msg"]]
    rec_all = mp["rec"]
    ok = s_all >= 0
    kset = (rec_all[ok].astype(np.int64) * 10_000_000 + i1_all[ok]) * 64 + s_all[ok]
    kset = np.unique(kset)
    # the sender's call that produced the message: last call of the sender with tc < t_msg
    out = np.zeros(len(te), bool)
    v = snd >= 0
    kc = np.searchsorted(keys, snd[v].astype(np.float64) * L.KEYMUL + te[v] - 0.5, side="right") - 1
    for back in (0, 1):
        q = (snd[v].astype(np.int64) * 10_000_000 + (kc - back)) * 64 + rec[v]
        pos = np.searchsorted(kset, q)
        pos = np.minimum(pos, len(kset) - 1)
        out[np.where(v)[0]] |= kset[pos] == q
    return out


def run(unit):
    t0 = time.time()
    U = load_unit(OUT / "units" / f"{unit}.npz")
    U["N"] = int(U["N"])
    c, m, mp = U["calls"], U["msgs"], U["mpairs"]
    keys = L.call_keys(U)
    D = len(U["day_t0"])
    W = 1.5 * L.median_call_interval(U)
    res = dict(unit=unit, regime=str(U["regime"]), goal_no=int(U["goal_no"]), N=U["N"], n_days=D,
               n_calls=int(len(c["tc"])), n_msgs=int(len(m["t"])), n_pairs=int(len(mp["msg"])),
               talk_rate=float(c["talk"].mean()), act_rate=float(c["act"].mean()), W=W,
               med_call_s=L.median_call_interval(U), w_read_s=L.mean_readout_wait(U),
               chat_mode_share=float(c["chat"].mean()) if "chat" in c else None)
    yT, yA = c["talk"].astype(float), c["act"].astype(float)
    yW = (c["act"] & ~c["talk"]).astype(float)        # pure work call (neither talk nor idle)
    yI = (~c["act"] & ~c["talk"]).astype(float)       # pure idle call (pause / wait without talk)
    # ------------------------------------------------------------------ C2 peer gate
    te, de, rec = m["t"][mp["msg"]], m["day"][mp["msg"]], mp["rec"]
    snd = m["sender"][mp["msg"]]
    gk = L.gate_kernel(U, keys, te, de, rec, yT, K=6, W=W, nboot=NBOOT)
    ga = L.gate_kernel(U, keys, te, de, rec, yA, K=3, W=W, nboot=NBOOT)
    gt = L.gate_test(U, keys, te, de, rec, {"talk": yT, "act": yA}, W=W, nboot=NBOOT)
    res["gate_talk"] = gk
    res["gate_act"] = ga
    res["gate_work"] = L.gate_kernel(U, keys, te, de, rec, yW, K=3, W=W, nboot=NBOOT)
    res["gate_idle"] = L.gate_kernel(U, keys, te, de, rec, yI, K=3, W=W, nboot=NBOOT)
    res["gate_k1"] = {k: {kk: vv for kk, vv in v.items() if kk != "boot_J"} for k, v in gt.items()}
    hr = L.hop_response(U, keys, te, de, rec, {"talk": yT, "act": yA}, nboot=100)
    res["peer_hop"] = hr
    var = {}
    resp = responding_mask(U, keys, te, rec, snd)
    res["share_reply_sources"] = float(resp.mean())
    sel_sets = dict(no_reply=~resp, ment=mp["ment"].astype(bool), no_ment=~mp["ment"].astype(bool),
                    certain=~mp["uncertain"].astype(bool))
    for name, sel in sel_sets.items():
        if sel.sum() < 200:
            continue
        g = L.gate_kernel(U, keys, te[sel], de[sel], rec[sel], yT, K=1, W=W, nboot=NBOOT)
        var[name] = dict(J1=g["jumps"][0], lo=g["j_lo"][0], hi=g["j_hi"][0], n=int(sel.sum()))
    # high-confidence starts only: drop low-confidence calls entirely
    Uh = dict(U)
    keep = ~c["low"]
    Uh["calls"] = {k: v[keep] for k, v in c.items()}
    kh = L.call_keys(Uh)
    g = L.gate_kernel(Uh, kh, te, de, rec, Uh["calls"]["talk"].astype(float), K=1, W=W, nboot=NBOOT)
    var["high_conf_calls"] = dict(J1=g["jumps"][0], lo=g["j_lo"][0], hi=g["j_hi"][0])
    g = L.gate_kernel(U, keys, te, de, rec, yT, K=1, W=3 * W, nboot=NBOOT)
    var["W3"] = dict(J1=g["jumps"][0], lo=g["j_lo"][0], hi=g["j_hi"][0])
    res["gate_variants"] = var
    # ------------------------------------------------------------------ Part B exogenous gates
    inp, ip = U["inputs"], U["ipairs"]
    kp = inp["kind"][ip["inp"]]
    t_p, d_p = inp["t"][ip["inp"]], inp["day"][ip["inp"]]
    exo = {}
    for name, sel in (("human_target", (kp == L.K["human"]) & ip["tgt"]), ("human_other", (kp == L.K["human"]) & ~ip["tgt"]),
                      ("nudge_target", (kp == L.K["nudge"]) & ip["tgt"]), ("nudge_bystander", (kp == L.K["nudge"]) & ~ip["tgt"]),
                      ("pause", kp == L.K["pause"])):
        if sel.sum() < 20:
            exo[name] = dict(n=int(sel.sum()))
            continue
        gT = L.gate_kernel(U, keys, t_p[sel], d_p[sel], ip["rec"][sel], yT, K=4, W=W, nboot=NBOOT)
        gA = L.gate_kernel(U, keys, t_p[sel], d_p[sel], ip["rec"][sel], yA, K=4, W=W, nboot=NBOOT)
        h = L.hop_response(U, keys, t_p[sel], d_p[sel], ip["rec"][sel], {"talk": yT, "act": yA}, nboot=100)
        exo[name] = dict(n=int(sel.sum()), n_events=int(len(np.unique(ip["inp"][sel]))), gate_talk=gT, gate_act=gA,
                         onset_talk=next((k + 1 for k, l in enumerate(gT["j_lo"]) if l > 0), None),
                         onset_act=next((k + 1 for k, l in enumerate(gA["j_lo"]) if l > 0), None),
                         hop=h)
    res["exo"] = exo
    # ------------------------------------------------------------------ Part A swarm FIR
    grid = L.make_grid(U)
    Xs = L.swarm_inputs(U, grid)
    fir = {}
    welch = {}
    for which in ("A", "T"):
        ys = L.swarm_output(grid, which)
        st = L.fir_stats(ys, Xs)
        days_ok = [s for s in st if s is not None]
        if len(days_ok) < 2:
            continue
        g, lam = L.fir_fit(st, len(L.SWARM_CLASSES))
        bs = L.fir_boot(st, len(L.SWARM_CLASSES), lam, nboot=NBOOT) if len(days_ok) >= 3 else None
        f = dict(lam=lam, kernels=g)
        for ci, cl in enumerate(L.SWARM_CLASSES):
            nin = float(sum(x[ci].sum() for x in Xs))
            met = L.kernel_metrics(g[ci], w_read_min=res["w_read_s"] / 60)
            met["n_inputs"] = nin
            if bs is not None and nin > 0:
                mb = [L.kernel_metrics(b[ci]) for b in bs]
                for k in ("G30", "dead_min", "corner_period_min", "decay_min", "pre"):
                    v = np.array([x[k] for x in mb], float)
                    v = v[np.isfinite(v)]
                    if len(v) > 20:
                        met[k + "_lo"], met[k + "_hi"] = float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))
                kb = bs[:, ci, :]
                met["kern_lo"] = np.percentile(kb, 2.5, 0)
                met["kern_hi"] = np.percentile(kb, 97.5, 0)
            f[cl] = met
        fir[which] = f
        ws = L.welch_sums(ys, Xs)
        welch[which] = ws
        summ, _, _ = L.welch_summary(ws)
        fir[which]["welch"] = {cl: summ[ci] for ci, cl in enumerate(L.SWARM_CLASSES)}
    res["fir"] = fir
    # ------------------------------------------------------------------ C1 decomposition
    Xa = L.agent_inputs(U, grid)
    Xp = L.peer_series(U, grid)
    c1 = {}
    keepc = None
    for which, variants in (("A", ("span", "full", "trim")), ("T", ("span", "full"))):
        for variant in variants:
            r = L.c1_decompose(grid, Xa, Xp, which=which, variant=variant)
            c1[f"{which}_{variant}"] = r
    # f_F without the nudge classes (indices 4, 5 of AGENT_CLASSES)
    keepc = [i for i, cl in enumerate(L.AGENT_CLASSES) if not cl.startswith("nudge")]
    Xa_nn = [x[keepc] for x in Xa]
    nonudge = {}
    for which, variant in (("A", "span"), ("A", "trim"), ("T", "span")):
        r = L.c1_decompose(grid, Xa_nn, Xp, which=which, variant=variant, nnull=0)
        nonudge[f"{which}_{variant}"] = r["f_F"]
    # attribution of the activity field excess: schedule edges (edge_on, pause) vs the other classes
    edge_idx = [L.AGENT_CLASSES.index("edge_on"), L.AGENT_CLASSES.index("pause")]
    rest_idx = [i for i in range(len(L.AGENT_CLASSES)) if i not in edge_idx]
    attr = {}
    for which, variant in (("A", "full"), ("A", "trim"), ("T", "span")):
        for lab, idx in (("edges", edge_idx), ("rest", rest_idx)):
            r = L.c1_decompose(grid, [x[idx] for x in Xa], Xp, which=which, variant=variant, nnull=3)
            attr[f"{which}_{variant}_{lab}"] = dict(f_F=r["f_F"], f_F_null=r["f_F_null"])
    res["c1_attr"] = attr
    res["c1"] = {k: L.floats(v) for k, v in c1.items()}
    res["c1_kern_exo_A_span"] = c1["A_span"]["kern_exo"]
    res["c1_f_F_no_nudge"] = nonudge
    # ------------------------------------------------------------------ CF coupling share (talk)
    kern = np.asarray(gk["kernel"])
    cf = {}
    for lab, dlt in (("k1", np.r_[max(kern[0], 0), np.zeros(5)]),
                     ("k1_lo", np.r_[max(gk["k_lo"][0], 0), np.zeros(5)]),
                     ("k1_hi", np.r_[max(gk["k_hi"][0], 0), np.zeros(5)])):
        ser = L.cf_coupling_series(U, grid, keys, te, de, rec, dlt)
        for variant in ("span", "full"):
            cf[f"{variant}_{lab}"] = L.cf_share(grid, ser, "T", variant)
            if lab == "k1":
                r = c1[f"T_{variant}"]
                cf[f"{variant}_afterF"] = L.cf_share_resid(r["resid_F"], r["masks"], ser)
    res["cf_talk"] = cf
    # ------------------------------------------------------------------ HH190 per-agent jumps
    per = {}
    if len(te) >= 3000:
        for a in range(U["N"]):
            sel = rec == a
            if sel.sum() < 300:
                continue
            g = L.gate_kernel(U, keys, te[sel], de[sel], rec[sel], yT, K=1, W=W, nboot=100)
            per[int(U["agent_codes"][a])] = dict(J1=g["jumps"][0], lo=g["j_lo"][0], hi=g["j_hi"][0], se=float(g["k_se"][0]),
                                                 n=int(sel.sum()), talk_rate=float(yT[c["agent"] == a].mean()))
    res["per_agent"] = per
    res["secs"] = time.time() - t0
    gdir = OUT / f"G{int(U['goal_no']):02d}"
    if unit.startswith("NE43"):
        gdir = OUT / "NE43"
    gdir.mkdir(parents=True, exist_ok=True)
    (gdir / f"{unit}.json").write_text(json.dumps(tolist(res)))
    if welch:
        np.savez_compressed(gdir / f"{unit}_welch.npz", **{f"{w}_{k}": v for w, ws in welch.items() for k, v in ws.items()})
    return unit, res["secs"], gk["jumps"][0], gk["j_lo"][0], gk["j_hi"][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=2)
    args = ap.parse_args()
    units = sorted(p.stem for p in (OUT / "units").glob("*.npz"))
    if args.only:
        units = [u for u in units if u in args.only.split(",")]
    # big units first
    sizes = {u: (OUT / "units" / f"{u}.npz").stat().st_size for u in units}
    units.sort(key=lambda u: -sizes[u])
    with ProcessPoolExecutor(max_workers=min(args.jobs, 2)) as ex:
        for u, s, j, lo, hi in ex.map(run, units):
            print(f"{u}: {s:.0f}s J1_talk {j:.4f} [{lo:.4f}, {hi:.4f}]", flush=True)


if __name__ == "__main__":
    main()
