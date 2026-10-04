"""H59 native tests: NE43 (G51 split at the nudger stop), G05 (#5 human dose), NE38 (operator message to one agent).

Usage: uv run python analysis/natives.py [--only NE43,G05,NE38]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h59lib as L  # noqa: E402
import run_period as RP  # noqa: E402

NE43_DAY = "2026-08-21"
NE38_DAY = "2026-07-29"
OPUS5 = 40


def g51():
    d = L.arrays(L.load(51))
    b = L.baseline(d)
    return d, b, L.KD(d, b["off"])


def ne43(d, kd, nboot=40, seed=3):
    rng = np.random.default_rng(seed)
    post_day = np.array([x >= NE43_DAY for x in d["days"]])
    side = post_day[kd.day]                                     # True = post (nudger off)
    cls_side = {}
    for s in (False, True):
        cls_side[s] = [c for c in range(len(L.CLASSES)) if int((kd.D[:, c, 0] * (side == s)).sum()) >= L.MIN_REC]
    common = [c for c in cls_side[False] if c in cls_side[True]]
    fits, boots = {}, {False: [], True: []}
    for s in (False, True):
        lv = L.Lever(cls_side[s], "lever")
        w = (side == s).astype(float)
        v = L.fit_param(kd, lv, w)
        fits[s] = (lv, v)
        dd = np.unique(kd.day[side == s])
        for _ in range(nboot):
            sel = rng.choice(dd, len(dd), replace=True)
            wd = np.bincount(sel, minlength=kd.ndays).astype(float)
            boots[s].append(L.fit_param(kd, lv, wd[kd.day] * w, v0=v))
    out = {"classes_pre": [L.CLASSES[c] for c in cls_side[False]], "classes_post": [L.CLASSES[c] for c in cls_side[True]],
           "n_days": [int(len(np.unique(kd.day[side == s]))) for s in (False, True)], "triples": {}, "delta": {}}
    for s, nm in ((False, "pre"), (True, "post")):
        lv, v = fits[s]
        bs = np.array(boots[s])
        out["triples"][nm] = {"theta_deg": float(np.degrees(v[5])), "K": [1.0] + list(map(float, v[:5]))}
        for c in cls_side[s]:
            a, b_, _ = lv.map[c]
            out["triples"][nm][L.CLASSES[c]] = {"kappa": float(v[a]), "h": float(v[b_]),
                                                "kappa_ci": list(np.percentile(bs[:, a], [2.5, 97.5])),
                                                "h_ci": list(np.percentile(bs[:, b_], [2.5, 97.5]))}
    for c in common:
        lp, vp = fits[False]
        lq, vq = fits[True]
        bp, bq = np.array(boots[False]), np.array(boots[True])
        for k, idx in (("kappa", 0), ("h", 1)):
            ip, iq = lp.map[c][idx], lq.map[c][idx]
            dlt = bq[:, iq] - bp[:, ip]
            out["delta"].setdefault(L.CLASSES[c], {})[k] = {"est": float(vq[iq] - vp[ip]),
                                                            "ci": [float(np.percentile(dlt, 2.5)), float(np.percentile(dlt, 97.5))]}
    # cross-NE transfer: pre parameters on post rows vs a 5-fold day CV refit on post
    lp, vp = fits[False]
    Bpre = np.zeros((len(L.CLASSES), L.NL, 3, 3))
    Bfull = lp.B(vp)
    for c in cls_side[True]:
        if c in cls_side[False]:
            Bpre[c] = Bfull[c]
    w1 = np.ones(kd.m)
    _, _, ll0 = kd.nll_grad(np.zeros_like(Bpre), w1)
    _, _, llp = kd.nll_grad(Bpre, w1)
    post = side
    fold = kd.day % 5
    llcv = np.zeros(kd.m)
    lq = L.Lever(cls_side[True], "lever")
    for f in range(5):
        tr = (post & (fold != f)).astype(float)
        v = L.fit_param(kd, lq, tr)
        _, _, ll = kd.nll_grad(lq.B(v), w1)
        te = post & (fold == f)
        llcv[te] = ll[te]
    pd = np.bincount(kd.day[post], (llp - ll0)[post], minlength=kd.ndays)
    cd = np.bincount(kd.day[post], (llcv - ll0)[post], minlength=kd.ndays)
    dd = np.unique(kd.day[post])
    rb = []
    for _ in range(300):
        sel = rng.choice(dd, len(dd), replace=True)
        wv = np.bincount(sel, minlength=kd.ndays)
        a, b_ = (pd * wv).sum(), (cd * wv).sum()
        rb.append(a / b_ if b_ > 0 else np.nan)
    S_pre, S_cv = float(pd.sum()), float(cd.sum())
    out["transfer"] = {"S_pre_on_post": S_pre, "S_post_cv": S_cv, "ratio": S_pre / S_cv if S_cv > 0 else None,
                       "ratio_ci": [float(np.nanpercentile(rb, 2.5)), float(np.nanpercentile(rb, 97.5))]}
    inv = all(out["delta"][c][k]["ci"][0] <= 0 <= out["delta"][c][k]["ci"][1] for c in out["delta"] for k in ("kappa", "h")
              if c in ("A", "Hu"))
    tr_ok = out["transfer"]["ratio"] is not None and out["transfer"]["ratio"] >= 0.8
    out["verdict"] = "supported" if (inv and tr_ok) else ("failed" if (not inv and not tr_ok) else "mixed")
    out["checks"] = {"triples_invariant_A_Hu": inv, "transfer_ge_0.8": tr_ok}
    return out


def ne38(d, kd):
    day = d["days"].index(NE38_DAY)
    # locate Opus 5's receiving call: agent codes in `d` are dense ranks, so use the raw agent column
    raw = L.load(51)["agent"].to_numpy()[kd.idx]
    hm = kd.D[:, L.CLASSES.index("Hm"), 0] > 0
    rows = np.flatnonzero((kd.day == day) & (raw == OPUS5) & hm)
    cls = L.powered(d)
    lv = L.Lever(cls, "lever")
    w = (kd.day != day).astype(float)
    v = L.fit_param(kd, lv, w)
    B = lv.B(v)
    out = {"n_rows": int(len(rows)), "rows": []}
    E0 = kd.off[rows].copy()
    E1 = E0 + L.contrib(kd, B)[rows]
    for k, r in enumerate(rows):
        i = kd.fs[r]
        p = []
        for E in (E0[k], E1[k]):
            e = E.copy()
            e[i] = 0
            q = np.exp(e - e.max())
            p.append(q / q.sum())
        out["rows"].append({"from": L.STATES[i], "to": L.STATES[kd.y[r]], "p_baseline": list(map(float, p[0])),
                            "p_lever": list(map(float, p[1])),
                            "llr_lever_vs_baseline": float(np.log(p[1][kd.y[r]]) - np.log(p[0][kd.y[r]]))})
    tri = {L.CLASSES[c]: {"kappa": float(v[lv.map[c][0]]), "h": float(v[lv.map[c][1]])} for c in cls}
    out["triples_wo_day"] = tri
    out["theta_deg"] = float(np.degrees(v[5]))
    return out


def g05_dose():
    res = RP.run(5, nboot=100)
    d = L.arrays(L.load(5))
    b = L.baseline(d)
    kd = L.KD(d, b["off"])
    cls = L.powered(d)
    tri, v, lv = L.triples(kd, cls, nboot=0)
    c = L.CLASSES.index("Hu")
    n0 = d["n0"][kd.idx, c]
    rec = kd.D[:, c, 0] > 0
    groups = [rec & (n0 == 1), rec & (n0 == 2), rec & (n0 >= 3)]
    s, cov = RP.amp_groups(kd, lv.B(v), c, groups)
    g = np.array([-s[2] / s[0] ** 2, 0, 1 / s[0]])
    se = float(np.sqrt(max(g @ cov @ g, 0))) if np.all(np.isfinite(cov)) else np.nan
    ratio = float(s[2] / s[0])
    res["dose"] = {"n_reads": [int(m.sum()) for m in groups], "scale": list(map(float, s)),
                   "scale_se": list(map(float, np.sqrt(np.clip(np.diag(cov), 0, None)))), "ratio_3plus_vs_1": ratio,
                   "ratio_ci": [ratio - 1.96 * se, ratio + 1.96 * se],
                   "mean_msgs_3plus": float(n0[groups[2]].mean()) if groups[2].any() else None}
    sat = ratio <= 2.0
    loco_v = res["verdict"]
    res["native_verdict"] = ("supported" if sat and loco_v == "supported" else
                             "failed" if (not sat and loco_v == "failed") else "mixed")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="NE43,G05,NE38")
    a = ap.parse_args()
    only = a.only.split(",")
    od = L.OUT / "native"
    od.mkdir(parents=True, exist_ok=True)
    if "NE43" in only or "NE38" in only:
        d, b, kd = g51()
        if "NE43" in only:
            r = ne43(d, kd)
            (od / "NE43.json").write_text(json.dumps(r, indent=1, default=float))
            print("NE43", json.dumps({k: r[k] for k in ("delta", "transfer", "verdict")}, default=float))
        if "NE38" in only:
            r = ne38(d, kd)
            (od / "NE38.json").write_text(json.dumps(r, indent=1, default=float))
            print("NE38", json.dumps(r, default=float))
    if "G05" in only:
        r = g05_dose()
        (od / "G05.json").write_text(json.dumps(r, indent=1, default=float))
        print("G05", r["verdict"], r["cells"], json.dumps(r["dose"]), r["native_verdict"])


if __name__ == "__main__":
    main()
