"""H39 point levers in one goal period: nudges, human messages, @-mentions, context erasures (NE41), on B4/B6
behavior states (field vs catalytic effects), plus content drift vs diffusion toward the kick message.

Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/run_period.py --period G51 [--quick]
Writes data/processed/H39-catalysts-vs-fields/G<NN>/results.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2" if _v == "POLARS_MAX_THREADS" else "1"

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h39lib as L  # noqa: E402

ROOT = L.ROOT
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import load_whitener  # noqa: E402

B6_TO_B4 = np.array([0, 0, 0, 1, 2, 3], np.int8)   # browse, type, shell -> work; chat; idle; consolidate
B4_NAMES = ["work", "chat", "idle", "consolidate"]
B6_NAMES = ["browse", "type", "shell", "chat", "idle", "consolidate"]
CLASSES = ("N_tgt", "H_men", "H_und", "H_any", "A_men")
HOLD = __import__("json").loads((ROOT / "hypotheses/holdout.json").read_text())


def period_days(goal_no: int, cal: pl.DataFrame) -> list[str]:
    c = cal.filter((pl.col("goal_no") == goal_no) & (pl.col("window_s") > 0) & (~pl.col("holdout")))
    days = sorted(c["pt_date"].to_list())
    for d in days:
        assert goal_no not in HOLD["goal_periods_held_out"]
        assert not any(w["start"] <= d < w["end"] for w in HOLD["ne_windows"]), "holdout leak"
    return days


def load_period(days: list[str], cal: pl.DataFrame, allow_holdout: bool = False, states: pl.DataFrame | None = None,
                kicks: pl.DataFrame | None = None, erasures: pl.DataFrame | None = None):
    """Per agent-day trimmed sequences + kick / erasure minutes. Returns a dict of lists (segment order)."""
    if states is None:
        states = pl.read_parquet(L.OUT / "states_b6.parquet")
    st = states.filter(pl.col("pt_date").is_in(days) & pl.col("present")).sort("pt_date", "agent", "minute")
    win = {r["pt_date"]: (r["win_start"], int(r["window_s"] // 60) + 1) for r in cal.filter(pl.col("pt_date").is_in(days)).iter_rows(named=True)}
    if kicks is None:
        kicks = pl.read_parquet(L.OUT / "kicks.parquet")
    kk = kicks.filter(pl.col("pt_date").is_in(days))
    ws = pl.DataFrame({"pt_date": list(win), "win_start": [win[d][0] for d in win]})
    kk = kk.join(ws, on="pt_date").with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int32).alias("minute"))
    kgroups = {k: g for k, g in kk.group_by(["pt_date", "agent"])}
    eg = {}
    if erasures is not None:
        ee = erasures.filter(pl.col("pt_date").is_in(days)).join(ws, on="pt_date").with_columns(
            ((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int32).alias("minute"))
        eg = {k: g for k, g in ee.group_by(["pt_date", "agent"])}
    seg = dict(b6=[], agent=[], day=[], date=[], third=[], first=[], ev={c: [] for c in CLASSES}, busy=[],
               er={"CF": [], "CV": [], "other": []}, er_busy=[], kick_rows=[])
    dix = {d: i for i, d in enumerate(days)}
    for (d, a), g in st.group_by(["pt_date", "agent"], maintain_order=True):
        m = g["minute"].to_numpy()
        nrec = g["n_rec"].to_numpy()
        occ = np.flatnonzero(nrec > 0)
        if len(occ) < 2:
            continue
        lo, hi = m[occ[0]], m[occ[-1]]
        sel = (m >= lo) & (m <= hi)
        x = g["coarse_min"].to_numpy()[sel].astype(np.int8)
        mm = m[sel]
        if len(mm) != hi - lo + 1:   # grid should be complete
            full = np.full(hi - lo + 1, 4, np.int8)
            full[mm - lo] = x
            x = full
        Lw = win[d][1]
        th = ((np.arange(lo, hi + 1) * 3) // max(Lw, 1)).clip(0, 2).astype(np.int8)
        seg["b6"].append(x)
        seg["agent"].append(int(a))
        seg["day"].append(dix[d])
        seg["date"].append(d)
        seg["third"].append(th)
        seg["first"].append(int(lo))
        b = np.zeros(len(x), bool)
        kg = kgroups.get((d, a))
        rows = {}
        for c in CLASSES:
            if kg is None:
                seg["ev"][c].append(np.zeros(0, np.int64))
                continue
            if c == "H_any":
                sub = kg.filter(pl.col("cls").cast(pl.Utf8).is_in(["H_men", "H_und"]))
            else:
                sub = kg.filter(pl.col("cls").cast(pl.Utf8) == c)
            loc = sub["minute"].to_numpy() - lo
            okm = (loc >= 0) & (loc < len(x))
            seg["ev"][c].append(np.unique(loc[okm]).astype(np.int64))
            if c != "H_any":
                b[loc[okm]] = True
            # first message row per (class, local minute) for content drift
            for lm, e in zip(loc[okm], sub["emb"].to_numpy()[okm]):
                rows.setdefault((c, int(lm)), int(e))
                if c in ("H_men", "H_und"):
                    rows.setdefault(("H_any", int(lm)), int(e))
        seg["busy"].append(b)
        seg["kick_rows"].append(rows)
        eb = b.copy()
        egg = eg.get((d, a))
        for kind in ("CF", "CV", "other"):
            if egg is None:
                seg["er"][kind].append(np.zeros(0, np.int64))
                continue
            loc = egg.filter(pl.col("kind") == kind)["minute"].to_numpy() - lo
            okm = (loc >= 0) & (loc < len(x))
            seg["er"][kind].append(np.unique(loc[okm]).astype(np.int64))
            eb[loc[okm]] = True
        seg["er_busy"].append(eb)
    return seg


def make_units(seg, q6=False, erasure=False):
    seqs = seg["b6"] if q6 else [B6_TO_B4[s] for s in seg["b6"]]
    q = 6 if q6 else 4
    act = (0, 1, 2, 3) if q6 else (0, 1)
    if erasure:
        return L.build_unit(seqs, seg["agent"], seg["day"], seg["third"], q, events=seg["er"], busy=seg["er_busy"],
                            offsets=seg["first"], active_states=act)
    return L.build_unit(seqs, seg["agent"], seg["day"], seg["third"], q, events=seg["ev"], busy=seg["busy"],
                        offsets=seg["first"], active_states=act)


def erasure_episodes(U: L.Unit, kind: str, W: int, quiet: int, cons_state: int):
    """CF/CV events: quiet before (no kick or other consolidation in [g-quiet, g-1]); window inside the segment;
    s0 = last non-consolidate state within 10 min before g (and its age bin)."""
    g = np.unique(U.events.get(kind, np.zeros(0, np.int64)))
    if len(g) == 0:
        return g, g, g
    ok = (U.left[g] >= W + 1) & (U.busy_in(-quiet, -1)[g] == 0)
    g = g[ok]
    s0, ab, keep = [], [], []
    for gi in g:
        j = gi - 1
        lo = U.seg_start[U.seg_of[gi]]
        while j >= max(lo, gi - 10) and U.x[j] == cons_state:
            j -= 1
        if j >= max(lo, gi - 10) and U.x[j] != cons_state:
            s0.append(U.x[j])
            ab.append(U.agebin[j])
            keep.append(True)
        else:
            keep.append(False)
    keep = np.array(keep, bool)
    return g[keep], np.array(s0, np.int8), np.array(ab, np.int8)


def content_drift(seg, days, cal, regime: str, classes, U4: L.Unit, W: int, rng, B=300, P=200, R=10):
    """O6: displacement of the agent's 30-min content vector across a kick, split into drift toward the kick
    message (field) and perpendicular diffusion (catalysis), against matched no-kick window triples."""
    idx = pl.read_parquet(SH / "embeddings/agent_win30.parquet").with_row_index("row").filter(pl.col("pt_date").is_in(days))
    if idx.height < 50:
        return {"status": "too few content windows"}
    V = np.load(SH / "embeddings/agent_win30_vec.npy", mmap_mode="r")
    Wh = load_whitener(regime, 32)
    X = Wh(np.asarray(V[idx["row"].to_numpy()], np.float32))
    pos = {(int(a), d, int(w)): i for i, (a, d, w) in enumerate(idx.select("agent", "pt_date", "win30").iter_rows())}
    E = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    win = {r["pt_date"]: r["win_start"] for r in cal.filter(pl.col("pt_date").is_in(days)).iter_rows(named=True)}
    # busy 30-min windows per (agent, date) from minute-level busy
    busyw = {}
    for k in range(len(seg["b6"])):
        b = np.flatnonzero(seg["busy"][k]) + seg["first"][k]
        busyw[(seg["agent"][k], seg["date"][k])] = set((b // 30).tolist())
    # control triples per agent: (pre, post) rows with no busy window in w-1..w+1
    ctrl = {}
    for (a, d, w), i in pos.items():
        if (a, d, w - 1) in pos and (a, d, w + 1) in pos:
            bw = busyw.get((a, d), set())
            if not ({w - 1, w, w + 1} & bw):
                ctrl.setdefault(a, []).append((pos[(a, d, w - 1)], pos[(a, d, w + 1)], days.index(d)))
    out = {}
    for c in classes:
        g = L.episodes_for(U4, c, W, L.QUIET)
        eps = []
        for gi in g:
            k = U4.seg_of[gi]
            a, d = seg["agent"][k], seg["date"][k]
            lm = int(gi - U4.seg_start[k])
            erow = seg["kick_rows"][k].get((c, lm), -1)
            if erow < 0:
                continue
            w = (lm + seg["first"][k]) // 30
            if (a, d, w - 1) in pos and (a, d, w + 1) in pos and a in ctrl and len(ctrl[a]) >= 3:
                eps.append((pos[(a, d, w - 1)], pos[(a, d, w + 1)], erow, a, days.index(d)))
        if len(eps) < 5:
            out[c] = {"status": "too few content episodes", "n_ep": len(eps)}
            continue
        U_msg = Wh(np.asarray(E[[e[2] for e in eps]], np.float32))

        def stats(pre, post, u):
            d_ = X[post] - X[pre]
            e_ = u - X[pre]
            e_ = e_ / np.maximum(np.linalg.norm(e_, axis=-1, keepdims=True), 1e-9)
            par = (d_ * e_).sum(-1)
            perp2 = (d_ ** 2).sum(-1) - par ** 2
            return par, perp2

        pre = np.array([e[0] for e in eps])
        post = np.array([e[1] for e in eps])
        parK, perpK = stats(pre, post, U_msg)
        C = np.array([[ctrl[e[3]][j] for j in rng.integers(0, len(ctrl[e[3]]), R)] for e in eps])  # (n, R, 3)
        parC, perpC = stats(C[..., 0], C[..., 1], U_msg[:, None, :])
        field_e = parK - parC.mean(1)
        fc = float(field_e.mean())
        sd_par = float(np.std(parC))
        cc = float(np.log(perpK.mean() / perpC.mean()))
        dy = np.array([e[4] for e in eps])
        ud, inv = np.unique(dy, return_inverse=True)
        bf, bc = [], []
        for _ in range(B):
            cnt = np.bincount(rng.integers(0, len(ud), len(ud)), minlength=len(ud))[inv].astype(float)
            if cnt.sum() == 0:
                continue
            bf.append(np.sum(cnt * field_e) / cnt.sum())
            bc.append(np.log(np.sum(cnt * perpK) / np.sum(cnt * perpC.mean(1))))
        pf, pc = [], []
        for _ in range(P):
            Pt = np.array([ctrl[e[3]][rng.integers(0, len(ctrl[e[3]]))] for e in eps])
            pa, pp = stats(Pt[:, 0], Pt[:, 1], U_msg)
            Cc = np.array([[ctrl[e[3]][j] for j in rng.integers(0, len(ctrl[e[3]]), R)] for e in eps])
            ca, cp = stats(Cc[..., 0], Cc[..., 1], U_msg[:, None, :])
            pf.append(float((pa - ca.mean(1)).mean()))
            pc.append(float(np.log(pp.mean() / cp.mean())))
        pf, pc = np.array(pf), np.array(pc)
        out[c] = dict(status="ok" if len(eps) >= L.MIN_EP else "underpowered", n_ep=len(eps), field_c=fc,
                      field_c_std=fc / sd_par if sd_par > 0 else float("nan"), sd_par_ctrl=sd_par,
                      field_c_ci=np.percentile(bf, [2.5, 97.5]).tolist(), field_c_se=float(np.std(bf)),
                      cat_c=cc, cat_c_ci=np.percentile(bc, [2.5, 97.5]).tolist(), cat_c_se=float(np.std(bc)),
                      p_field_c=float((1 + np.sum(np.abs(pf - np.median(pf)) >= abs(fc - np.median(pf)))) / (P + 1)),
                      p_cat_c=float((1 + np.sum(np.abs(pc - np.median(pc)) >= abs(cc - np.median(pc)))) / (P + 1)),
                      placebo_field_sd=float(np.std(pf)), placebo_cat_sd=float(np.std(pc)))
    return out


def run(period: str, quick: bool = False, W: int = L.W_DEFAULT):
    t0 = time.time()
    gno = int(period[1:3])
    cal = pl.read_parquet(SH / "calendar.parquet")
    days = period_days(gno, cal)
    regime = str(cal.filter(pl.col("pt_date") == days[0])["regime"][0])
    er = pl.read_parquet(L.OUT / "erasures.parquet") if regime == "III" else None
    seg = load_period(days, cal, erasures=er)
    B, P = (100, 50) if quick else (300, 200)
    rng = np.random.default_rng(L.SEED + gno)
    res = dict(period=period, goal_no=gno, regime=regime, days=days, n_agent_days=len(seg["b6"]), W=W,
               n_minutes=int(sum(len(s) for s in seg["b6"])), states_b4=B4_NAMES, states_b6=B6_NAMES)
    U4 = make_units(seg)
    U6 = make_units(seg, q6=True)
    res["occupancy_b4"] = (np.bincount(U4.x, minlength=4) / len(U4.x)).tolist()
    res["b4"], res["b6"], res["sens"] = {}, {}, {}
    for c in CLASSES:
        r = L.run_point(U4, c, W=W, B=B, P=P, seed=L.SEED + gno, keep_draws=True)
        res["b4"][c] = r
        if r.get("n_ep", 0) >= L.MIN_EP:
            res["b6"][c] = L.run_point(U6, c, W=W, B=max(B // 2, 50), P=max(P // 2, 50), seed=L.SEED + gno + 1)
            for Ws in (15, 60):
                rr = L.run_point(U4, c, W=Ws, B=100, P=50, seed=L.SEED + gno + Ws)
                res["sens"][f"{c}_W{Ws}"] = {k: rr.get(k) for k in ("n_ep", "K", "K_ci", "phi", "phi_exc", "p_F", "dpi", "esc", "status")}
        print(f"  {period} {c}: n_ep {r.get('n_ep')} K {r.get('K', float('nan')):.3f} phi_exc {r.get('phi_exc', float('nan')):.3f} pF {r.get('p_F', float('nan')):.3f} ({time.time() - t0:.0f}s)", flush=True)
    # ---- context erasures (regime III)
    if regime == "III":
        res["erasure"] = {}
        for q6 in (False, True):
            Ue = make_units(seg, q6=q6, erasure=True)
            cons = 5 if q6 else 3
            pool = L.control_pool(Ue, W, quiet=10)
            for kind in ("CF", "CV"):
                g, s0, ab = erasure_episodes(Ue, kind, W, 10, cons)
                r = L.run_point(Ue, kind, W=W, B=B if not q6 else max(B // 2, 50), P=P if not q6 else max(P // 2, 50),
                                seed=L.SEED + gno + 7, g_override=g, s0_override=s0, age_override=ab, pool_mask=pool,
                                quiet=10, keep_draws=not q6)
                res["erasure"][f"{kind}_{'b6' if q6 else 'b4'}"] = r
                # Amendment A2: the consolidation clock mechanically depletes transitions into consolidate right
                # after any consolidation; the work/chat/idle chain without the consolidate state is reported too.
                keep = [0, 1, 2, 3, 4] if q6 else [0, 1, 2]
                r2 = L.run_point(Ue, kind, W=W, B=max(B // 2, 50), P=max(P // 2, 50), seed=L.SEED + gno + 9,
                                 g_override=g, s0_override=s0, age_override=ab, pool_mask=pool, quiet=10,
                                 keep_draws=not q6, keep_states=keep)
                res["erasure"][f"{kind}_{'b6' if q6 else 'b4'}_nocons"] = r2
                print(f"  {period} erasure {kind} {'b6' if q6 else 'b4'}: n_ep {r.get('n_ep')} K {r.get('K', float('nan')):.3f} pF {r.get('p_F', float('nan')):.3f}; no-cons K {r2.get('K', float('nan')):.3f}", flush=True)
    # ---- content drift / diffusion toward the kick message
    try:
        res["content"] = content_drift(seg, days, cal, regime, ("N_tgt", "H_any", "H_men", "A_men"), U4, W, rng,
                                       B=B, P=max(P // 2, 50))
    except Exception as e:  # pragma: no cover
        res["content"] = {"status": f"error {e!r}"}
    res["runtime_s"] = time.time() - t0
    L.jdump(res, L.OUT / period / "results.json")
    # keep bootstrap draws (small) for class probabilities
    draws = {}
    for c, r in res["b4"].items():
        if "_boot" in r:
            draws[c] = {k: np.asarray(v, np.float32) for k, v in r["_boot"].items()}
    for k, r in res.get("erasure", {}).items():
        if "_boot" in r:
            draws[f"erasure_{k}"] = {kk: np.asarray(v, np.float32) for kk, v in r["_boot"].items()}
    np.savez_compressed(L.OUT / period / "boot_draws.npz", **{f"{c}__{k}": v for c, d in draws.items() for k, v in d.items()})
    print(f"{period} done in {time.time() - t0:.0f}s", flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", required=True)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    run(a.period, a.quick)
