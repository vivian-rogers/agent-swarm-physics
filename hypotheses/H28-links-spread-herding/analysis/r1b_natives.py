"""H28 round 1b natives (2026-10-04). Predictions are in goalperiod-subhypotheses/NE09/README.md and G31/README.md
(written 16:40 UTC, before this script was run).

  uv run python hypotheses/H28-links-spread-herding/analysis/r1b_natives.py ne09     # blind-window test on ledger visibility
  uv run python hypotheses/H28-links-spread-herding/analysis/r1b_natives.py estimates  # per-period rows -> per_period_estimates

ne09: for every (link, susceptible recipient) pair -- recipient off X (no touch of X in the 60 min before posting), same
day -- the blind window (t_post, t_vis] (t_vis = the recipient's ledger receiving call) and the read window
(t_vis, t_vis + 15 min]. Switch (arrival) rates per minute in each window vs the same pairs under the link time-shift null
(39 draws, t_vis recomputed from the recipient's receiving calls). Writes r1b/ne09_blind.json.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ["H28_DATA"] = "r1b"
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h28core as hc  # noqa: E402
from h28lib import OUT, gname, write_provenance  # noqa: E402

HERD = [18, 19, 24, 25, 26, 30, 31]
PRE = [18, 19]
READ_MS = 15 * 60_000


def arrivals(P):
    T, K = P["touches"], P["K"]
    m = T["x"] >= 0
    key, t = T["ai"][m] * K + T["x"][m], T["t"][m]
    o = np.lexsort((t, key))
    key, t = key[o], t[o]
    newk = np.r_[True, key[1:] != key[:-1]]
    gap = np.r_[np.inf, np.diff(t)]
    arr = newk | (gap > hc.GAP_MS)
    return key * hc.BIG + t, key[arr] * hc.BIG + t[arr]


def pair_counts(P, lt, tv, tcomp, acomp):
    L, E, K = P["links"], P["expo"], P["K"]
    ex_x = L["x"][E["lid"]]
    m = (ex_x >= 0) & (tv >= 0)
    kk = E["ri"][m] * K + ex_x[m]
    tp, tvv, lid = lt[E["lid"][m]], tv[m], E["lid"][m]
    ws = np.array([d["ws_ms"] for d in P["days"]]); we = np.array([d["we_ms"] for d in P["days"]])
    di = np.clip(np.searchsorted(ws, tp, "right") - 1, 0, len(ws) - 1)
    ok = (tvv >= tp) & (tvv <= we[di]) & (hc._count(tcomp, kk * hc.BIG + tp - hc.GAP_MS, kk * hc.BIG + tp) == 0)
    kk, tp, tvv, lid = kk[ok], tp[ok], tvv[ok], lid[ok]
    base = kk * hc.BIG
    nb = np.searchsorted(acomp, base + tvv, "right") - np.searchsorted(acomp, base + tp, "right")
    nr = np.searchsorted(acomp, base + tvv + READ_MS, "right") - np.searchsorted(acomp, base + tvv, "right")
    # first arrival after t_vis (lag from visibility, for N9c)
    j = np.searchsorted(acomp, base + tvv, "right")
    nxt = acomp[np.clip(j, 0, len(acomp) - 1)] - base        # epoch-ms times exceed BIG: decode by offset, not by //
    same = (j < len(acomp)) & (nxt >= tvv) & (nxt - tvv < 2 * 86_400_000)
    lag = np.where(same, (nxt - tvv) / 60000.0, np.inf)
    return dict(nb=nb, nr=nr, db=(tvv - tp) / 60000.0, lid=L["msg"][lid], lag=lag, delay_s=(tvv - tp) / 1000.0)


def ne09(shifts=39, boot=2000):
    res, pooled = {}, {"obs": [], "null_rb": [], "null_rr": []}
    for g in HERD:
        P = hc.load_period(OUT / gname(g))
        tcomp, acomp = arrivals(P)
        tcomp = np.sort(tcomp)
        obs = pair_counts(P, P["links"]["t"], P["expo"]["t_vis"], tcomp, acomp)
        rng = np.random.default_rng(2809 + g)
        rb, rr, lags = [], [], []
        for _ in range(shifts):
            lt, tv = hc.shift_links(P, rng)
            c = pair_counts(P, lt, tv, tcomp, acomp)
            rb.append(c["nb"].sum() / max(c["db"].sum(), 1e-9)); rr.append(c["nr"].sum() / (len(c["nr"]) * 15.0))
            lags.append(np.histogram(c["lag"][np.isfinite(c["lag"]) & (c["lag"] < 240)], bins=np.arange(0, 245, 5))[0])
        rb0, rr0 = float(np.mean(rb)), float(np.mean(rr))
        ob = obs["nb"].sum() / max(obs["db"].sum(), 1e-9)
        orr = obs["nr"].sum() / (len(obs["nr"]) * 15.0)
        h = np.histogram(obs["lag"][np.isfinite(obs["lag"]) & (obs["lag"] < 240)], bins=np.arange(0, 245, 5))[0]
        exc = h - np.mean(lags, 0)
        cum = np.cumsum(np.clip(exc, 0, None))
        med = float(np.searchsorted(cum, cum[-1] / 2) * 5 + 2.5) if cum[-1] > 0 else float("nan")
        res[g] = dict(pre_ne09=g in PRE, pairs=int(len(obs["nb"])), blind_minutes=float(obs["db"].sum()),
                      median_delay_s=float(np.median(obs["delay_s"])), blind_switches=int(obs["nb"].sum()),
                      read_switches=int(obs["nr"].sum()), rate_blind=ob, rate_read=orr, null_rate_blind=rb0, null_rate_read=rr0,
                      E_blind=ob / rb0 if rb0 > 0 else float("nan"), E_read=orr / rr0 if rr0 > 0 else float("nan"),
                      median_excess_lag_from_vis_min=med)
        pooled["obs"].append((g, obs)); pooled["null_rb"].append(rb0); pooled["null_rr"].append(rr0)
        print(g, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in res[g].items()}, flush=True)

    def pool(gs, rng):
        """E_blind, E_read pooled over periods gs: sum obs / sum expected (expected = null rate x exposure time);
        cluster bootstrap over link messages within periods."""
        rows = [(o, rb, rr) for (g, o), rb, rr in zip(pooled["obs"], pooled["null_rb"], pooled["null_rr"]) if g in gs]

        def stat(sel):
            ob = sum(o["nb"][s].sum() for (o, _, _), s in zip(rows, sel)); eb = sum(rb * o["db"][s].sum() for (o, rb, _), s in zip(rows, sel))
            orr = sum(o["nr"][s].sum() for (o, _, _), s in zip(rows, sel)); er = sum(rr * 15.0 * len(o["nr"][s]) for (o, _, rr), s in zip(rows, sel))
            return ob / eb if eb > 0 else np.nan, orr / er if er > 0 else np.nan
        full = [np.arange(len(o["nb"])) for o, _, _ in rows]
        Eb, Er = stat(full)
        bs = []
        for _ in range(boot):
            sel = []
            for o, _, _ in rows:
                u, inv = np.unique(o["lid"], return_inverse=True)
                pick = rng.integers(0, len(u), len(u))
                cnt = np.bincount(pick, minlength=len(u))
                sel.append(np.repeat(np.arange(len(inv)), cnt[inv]))
            bs.append(stat(sel))
        bs = np.array(bs, float)
        q = lambda c: np.nanquantile(bs[:, c], [0.05, 0.95]).tolist()
        return dict(E_blind=float(Eb), E_blind_ci90=q(0), E_read=float(Er), E_read_ci90=q(1),
                    ratio_blind_read=float(Eb / Er) if Er else float("nan"),
                    p_blind_le1=float(np.mean(bs[:, 0] <= 1)))
    rng = np.random.default_rng(28)
    out = dict(periods=res, pooled_all=pool(HERD, rng), pooled_pre=pool(PRE, rng),
               pooled_post=pool([g for g in HERD if g not in PRE], rng))
    pre_d = [res[g]["median_delay_s"] for g in PRE]; post_d = [res[g]["median_delay_s"] for g in HERD if g not in PRE]
    out["N9a"] = dict(pre_median_delay_s=pre_d, post_median_delay_s=post_d, ratio=float(np.median(pre_d) / np.median(post_d)),
                      holds=bool(0.5 <= np.median(pre_d) / np.median(post_d) <= 2))
    pa = out["pooled_all"]
    out["N9b"] = dict(holds=bool(pa["E_blind_ci90"][0] > 1 and pa["E_blind"] >= 0.5 * pa["E_read"]))
    pre_l = [res[g]["median_excess_lag_from_vis_min"] for g in PRE]; post_l = [res[g]["median_excess_lag_from_vis_min"] for g in HERD if g not in PRE]
    out["N9c"] = dict(pre=pre_l, post=post_l, holds=bool(np.nanmedian(post_l) >= np.nanmedian(pre_l)))
    (OUT / "r1b").mkdir(exist_ok=True)
    (OUT / "r1b" / "ne09_blind.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: out[k] for k in ("pooled_all", "pooled_pre", "pooled_post", "N9a", "N9b", "N9c")}, indent=1, default=float))
    write_provenance(OUT / "r1b", "hypotheses/H28-links-spread-herding/analysis/r1b_natives.py", ["H28 r1b/G<NN>/ + round-1 G<NN>/"],
                     {"shifts": shifts, "boot": boot, "read_window_min": 15, "periods": HERD}, key="ne09_blind")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ne09"
    if cmd == "ne09":
        ne09()
