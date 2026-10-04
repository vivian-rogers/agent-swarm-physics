"""H26 exploratory round 1 on real data (non-holdout; asserted): drive-removed content vs activity vs talk loop gains.

Per H01 unit (regime III + #35): Panels for content (dedup primary; raw variant), activity and talk at three
resolutions (day; w30 = equal-time 30-min windows, deviations from the agent's unit mean; wd = within-day), ladder
L0/L1/L2/L3/L4 (h26lib), bootstrap over days, N1 time-shuffle and N2 room-permutation nulls, H01's P9 replica (raw and
dedup), the measured-drive share (O5), n_eff and the isotropic-surrogate width (H20 lesson).

Usage: uv run python hypotheses/H26-content-near-critical/analysis/explore.py [--units 41,44] [--fast]
Writes data/processed/H26-content-near-critical/G<NN>/<unit>.json and results_units.parquet.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h26lib as L  # noqa: E402  (thread caps 2)

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H01-emergent-superagents-exist/analysis"))
sys.path.insert(0, str(ROOT / "hypotheses/H01-emergent-superagents-exist/scheme"))
from common import holdout_mask  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

D = ROOT / "data/processed/H26-content-near-critical"
SEED = 20261004
NS = 3
FAST = "--fast" in sys.argv
B_BOOT = 100 if FAST else 400
N_N1 = 30 if FAST else 100
N_N2 = 50 if FAST else 200
UNITS = ["35", "36b", "37", "38a", "38b", "38c", "39", "40", "41", "42", "44", "51a", "51b", "51c", "51d", "51e"]
TWO_ROOM_MIN = 2       # agents per room needed on a slot for the room contrast


def stable_seed(*parts):
    import zlib
    return zlib.crc32("|".join(map(str, parts)).encode()) & 0x7FFFFFFF


class Data:
    def __init__(self):
        self.st = pl.read_parquet(D / "statements.parquet").with_row_index("i")
        days = sorted(self.st["pt_date"].unique().to_list())
        cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet")
        hm = dict(zip(cal["pt_date"].to_list(), holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))
        hol = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
        assert not any(hm.get(d) or hol.get(d) for d in days), "holdout day in exploration"
        self.V = np.load(D / "vec32.npy")
        self.act = pl.read_parquet(D / "activity.parquet")
        self.rooms = pl.read_parquet(D / "rooms.parquet")
        self.outage = pl.read_parquet(D / "outage.parquet")
        self.exo = pl.read_parquet(D / "exo.parquet").with_row_index("i")
        self.Ve = np.load(D / "exo_vec32.npy")
        z = np.load(D / "static.npz")
        self.static = {k: z[k] for k in z.files}
        self.units = {u["unit"]: u for u in json.loads((ROOT / "data/processed/H01-emergent-superagents-exist/units.json").read_text())}


def slot_tables(Dt: Data, u: str, res: str):
    """Slot index per (pt_date, win30) for the unit; day index; outage flags."""
    days = Dt.units[u]["days"]
    nwin = (Dt.st.filter(pl.col("unit") == u).group_by("pt_date").agg(pl.col("n_win").first()))
    nw = dict(zip(nwin["pt_date"].to_list(), nwin["n_win"].to_list()))
    W = max(nw.values()) if nw else 8
    return days, W


def build_panels(Dt: Data, u: str, dedup=True, drop_outage=True):
    """Return {(ch, res): Panel} for ch in c, a, k and res in day, w30, wd; plus bookkeeping."""
    rng = np.random.default_rng(stable_seed(u, "panels", dedup))
    days, W = slot_tables(Dt, u, "w30")
    st = Dt.st.filter(pl.col("unit") == u)
    if dedup:
        st = st.filter(~pl.col("dup"))
    agents = sorted(st["agent"].unique().to_list())
    out_bad = set()
    if drop_outage:
        o = Dt.outage.filter(pl.col("pt_date").is_in(days) & (pl.col("idle_share") >= 0.5))
        out_bad = set(zip(o["pt_date"].to_list(), o["win30"].to_list()))
    rooms = Dt.rooms.filter(pl.col("unit") == u)
    room_w = {(a, d, w): (-1 if r is None else r) for a, d, w, r in rooms.select("agent", "pt_date", "win30", "room").iter_rows()}
    dmap = {d: i for i, d in enumerate(days)}
    # modal room per agent-day (over the agent's windows)
    rd = (rooms.filter(pl.col("room").is_not_null()).group_by("agent", "pt_date").agg(pl.col("room").mode().first()))
    room_d = {(a, d): r for a, d, r in rd.iter_rows()}
    exo = Dt.exo.filter(pl.col("unit") == u)
    panels = {}
    Sbasis = Dt.static.get(u)
    for res in ("day", "w30", "wd"):
        # ---------------- content
        s = st.select("i", "agent", "pt_date", "win30")
        if out_bad:   # outage windows dropped at every resolution (Amendment 2)
            keep = [(d, w) not in out_bad for d, w in zip(s["pt_date"].to_list(), s["win30"].to_list())]
            s = s.filter(pl.Series(keep))
        key_cols = ["agent", "pt_date"] if res == "day" else ["agent", "pt_date", "win30"]
        g = s.group_by(key_cols, maintain_order=True).agg(pl.col("i")).sort(key_cols)
        n = g.height
        X = np.full((n, 32), np.nan, np.float32)
        A = np.full((n, NS, 32), np.nan, np.float32); B = np.full((n, NS, 32), np.nan, np.float32)
        for o, ix in enumerate(g["i"].to_list()):
            ix = np.asarray(ix)
            X[o] = Dt.V[ix].mean(0)
            if len(ix) >= 2:
                for sp in range(NS):
                    p = rng.permutation(ix); h = len(p) // 2
                    A[o, sp] = Dt.V[p[:h]].mean(0); B[o, sp] = Dt.V[p[h:]].mean(0)
        ag = g["agent"].to_numpy().astype(int)
        dd = np.array([dmap[x] for x in g["pt_date"].to_list()])
        if res == "day":
            t = dd; wod = np.zeros(n, int)
            room = np.array([room_d.get((a, d_), -1) for a, d_ in zip(ag, g["pt_date"].to_list())])
        else:
            ww = g["win30"].to_numpy().astype(int)
            t = dd * W + ww; wod = ww
            room = np.array([room_w.get((a, d_, w_), -1) for a, d_, w_ in zip(ag, g["pt_date"].to_list(), ww)])
        grp = dd * 1000 + ag if res == "wd" else ag
        # exogenous directions per slot (all rooms; union), and counts per (room, slot) for scalars
        exo_dirs, exo_cnt = {}, {}
        e = exo.select("i", "pt_date", "win30", "room", "speaker_kind")
        ed = np.array([dmap.get(x, -1) for x in e["pt_date"].to_list()])
        ew = e["win30"].to_numpy().astype(int); er = e["room"].to_numpy().astype(int); ei = e["i"].to_numpy()
        eh = (e["speaker_kind"] == "human").to_numpy()
        slots = np.unique(t)
        for sl in slots:
            if res == "day":
                m = ed == sl
            else:
                d0, w0 = divmod(int(sl), W)
                m = (ed == d0) & (ew <= w0) & (ew >= w0 - 3)
            exo_dirs[int(sl)] = L.orthobasis(Dt.Ve[ei[m]]) if m.any() else None
            for r in np.unique(er[m]):
                mm = m & (er == r)
                exo_cnt[(int(sl), int(r))] = (int((mm & eh).sum()), int((mm & ~eh).sum()))
        Pc = L.Panel(agent=ag, t=t, day=dd, wod=wod, room=room, X=X, A=A, B=B, grp=grp, static=Sbasis,
                     exo=exo_dirs, res=res, meta={"unit": u, "W": W})
        panels[("c", res)] = Pc
        # ---------------- activity and talk
        a = Dt.act.filter((pl.col("unit") == u) & pl.col("agent").is_in(agents))
        if out_bad:
            keep = [(d_, w_) not in out_bad for d_, w_ in zip(a["pt_date"].to_list(), a["win30"].to_list())]
            a = a.filter(pl.Series(keep))
        if res == "day":
            a = a.group_by("agent", "pt_date").agg(pl.col(c).sum() for c in a.columns if c.startswith("n_")).sort("agent", "pt_date")
        else:
            a = a.sort("agent", "pt_date", "win30")
        n = a.height
        ag = a["agent"].to_numpy().astype(int)
        dd = np.array([dmap[x] for x in a["pt_date"].to_list()])
        if res == "day":
            t = dd; wod = np.zeros(n, int)
            room = np.array([room_d.get((a_, d_), -1) for a_, d_ in zip(ag, a["pt_date"].to_list())])
        else:
            ww = a["win30"].to_numpy().astype(int)
            t = dd * W + ww; wod = ww
            room = np.array([room_w.get((a_, d_, w_), -1) for a_, d_, w_ in zip(ag, a["pt_date"].to_list(), ww)])
        grp = dd * 1000 + ag if res == "wd" else ag
        Z = np.array([exo_cnt.get((int(sl), int(r)), (0, 0)) for sl, r in zip(t, room)], float)
        nmin = a["n_min"].to_numpy().astype(float)
        for ch, col in (("a", "act"), ("k", "talk")):
            Xs = (a[f"n_{col}"].to_numpy() / np.maximum(nmin, 1))[:, None]
            As = np.zeros((n, NS, 1)); Bs = np.zeros((n, NS, 1))
            for sp in range(NS):
                nA = a[f"n_min_A{sp}"].to_numpy().astype(float); cA = a[f"n_{col}_A{sp}"].to_numpy().astype(float)
                nB = nmin - nA; cB = a[f"n_{col}"].to_numpy() - cA
                okh = (nA >= 3) & (nB >= 3)
                As[:, sp, 0] = np.where(okh, cA / np.maximum(nA, 1), np.nan)
                Bs[:, sp, 0] = np.where(okh, cB / np.maximum(nB, 1), np.nan)
            Xs = np.where(nmin[:, None] >= 6, Xs, np.nan)
            # Amendment 2: no exogenous-count regression for day-level scalars (2 slopes vs D x R room-day cells
            # over-fits; #37 test: rho_c flipped from +0.95 to -0.27)
            panels[(ch, res)] = L.Panel(agent=ag, t=t, day=dd, wod=wod, room=room, X=Xs, A=As, B=Bs, grp=grp,
                                        Z=None if res == "day" else Z, res=res, meta={"unit": u, "W": W})
    return panels, {"agents": agents, "days": days, "W": W, "n_outage_windows": len(out_bad)}


def is_two_room(P: L.Panel):
    ok = P.room >= 0
    cnt = {}
    for tt, r in zip(P.t[ok], P.room[ok]):
        cnt.setdefault(tt, {}).setdefault(r, 0)
        cnt[tt][r] += 1
    n2 = sum(1 for v in cnt.values() if sum(c >= TWO_ROOM_MIN for c in v.values()) >= 2)
    return n2 >= max(2, 0.3 * len(cnt))


def analyze_panel(P: L.Panel, ch: str, rng, do_nulls=True):
    levels = (0, 1, 2, 4) if ch == "c" else (0, 2, 4)
    if P.res == "day" and len(np.unique(P.day)) < 8:   # Amendment 2: day-level L4 only with >= 8 days
        levels = tuple(lv for lv in levels if lv != 4)
    out = {}
    two = is_two_room(P)
    for lv in levels:
        C, g, (dX, okX) = L.run_level(P, lv)
        rec = {k: (float(v) if v is not None and np.isfinite(v) else None) for k, v in g.items()
               if k in ("g_all", "g_room", "g_ex", "g_ex_raw", "rho_w", "rho_c", "rho_ex", "rho_ex_raw", "rho_all",
                        "Nr", "Nall", "S_mean", "npair_w", "npair_c")}
        if lv in (0, 2):
            bs = L.bootstrap(C, B=B_BOOT, rng=rng, keys=("g_all", "g_room", "g_ex", "rho_ex"))
            for k in ("g_all", "g_room", "g_ex", "rho_ex"):
                rec[f"ci_{k}"] = L.ci(bs[k])
            rec["_boot"] = {k: bs[k].tolist() for k in ("g_room", "g_ex", "g_all")}
        if lv == 2 and do_nulls:
            # N1 time shuffle (anisotropic by construction)
            n1 = []
            for _ in range(N_N1):
                Ps = L.shuffle_time(P, rng)
                _, gs, _ = L.run_level(Ps, 2)
                n1.append((gs["g_room"], gs["g_all"], gs["rho_w"]))
            n1 = np.array(n1, float)
            rec["N1_g_room_q95"] = float(np.nanpercentile(n1[:, 0], 95))
            rec["N1_g_room_median"] = float(np.nanmedian(n1[:, 0]))
            rec["N1_rho_w_sd"] = float(np.nanstd(n1[:, 2]))
            rec["p_N1_g_room"] = float((1 + np.sum(n1[:, 0] >= g["g_room"])) / (1 + len(n1)))
            if two:
                dXb, dA, dB, okXb, okS = L.deviations(P, 2)
                n2 = []
                for _ in range(N_N2):
                    room2 = L.permute_rooms(P, rng)
                    n2.append(L.gains(L.contributions(P, dXb, dA, dB, okXb, okS, room=room2))["rho_ex"])
                n2 = np.array(n2, float)
                rec["N2_rho_ex_q95"] = float(np.nanpercentile(n2, 95))
                rec["p_N2_rho_ex"] = float((1 + np.sum(n2 >= g["rho_ex"])) / (1 + np.isfinite(n2).sum()))
            if ch == "c":
                rec["n_eff"] = L.n_eff(dX, okX)
                # isotropic Gaussian surrogate (pre-registered as the too-narrow comparison only)
                iso = []
                nrm = np.sqrt((dX ** 2).sum(1))
                _, dA_, dB_, _, okS_ = L.deviations(P, 2)
                for _ in range(N_N1):
                    Zs = rng.standard_normal(dX.shape); Zs /= np.linalg.norm(Zs, axis=1, keepdims=True)
                    Zs *= nrm[:, None]
                    Cs = L.contributions(P, Zs, dA_, dB_, okX, okS_)
                    iso.append(L.gains(Cs)["rho_w"])
                rec["iso_rho_w_sd"] = float(np.nanstd(iso))
        rec["two_room"] = bool(two)
        out[f"L{lv}"] = rec
    if "L2" in out:
        out["L3"] = {k: out["L2"].get(k) for k in ("g_ex", "g_ex_raw", "rho_ex", "rho_ex_raw", "rho_w", "rho_c", "Nr",
                                                    "ci_g_ex", "ci_rho_ex", "N2_rho_ex_q95", "p_N2_rho_ex", "two_room")}
    return out


def drive_share(P: L.Panel, Dt: Data, u: str, rng, n_null=200):
    """O5: share of room-slot mean-deviation variance (L1) along that room-slot's own exogenous directions, vs the same
    statistic with exogenous directions taken from a random other room-slot of the unit."""
    dX, _, _, okX, _ = L.deviations(P, 1)
    W = P.meta["W"]
    exo = Dt.exo.filter(pl.col("unit") == u)
    days = Dt.units[u]["days"]; dmap = {d: i for i, d in enumerate(days)}
    ed = np.array([dmap.get(x, -1) for x in exo["pt_date"].to_list()])
    ew = exo["win30"].to_numpy().astype(int); er = exo["room"].to_numpy().astype(int); ei = exo["i"].to_numpy()
    rows = []
    for r in np.unique(P.room[P.room >= 0]):
        for tt in np.unique(P.t[(P.room == r) & okX]):
            m = (P.room == r) & (P.t == tt) & okX
            if m.sum() < 2:
                continue
            mv = dX[m].mean(0)
            if P.res == "day":
                me = (ed == tt) & (er == r)
            else:
                d0, w0 = divmod(int(tt), W)
                me = (ed == d0) & (er == r) & (ew <= w0) & (ew >= w0 - 3)
            Q = L.orthobasis(Dt.Ve[ei[me]]) if me.any() else None
            rows.append((mv, Q))
    with_q = [(mv, Q) for mv, Q in rows if Q is not None and Q.size]
    if len(with_q) < 2:
        return {"n_room_slots": len(rows), "n_with_exo": len(with_q)}
    share = np.mean([np.sum((Q @ mv) ** 2) / max(mv @ mv, 1e-12) for mv, Q in with_q])
    allQ = [Q for _, Q in with_q]
    nul = []
    for _ in range(n_null):
        nul.append(np.mean([np.sum((allQ[rng.integers(len(allQ))] @ mv) ** 2) / max(mv @ mv, 1e-12) for mv, _ in with_q]))
    k_mean = float(np.mean([Q.shape[0] for Q in allQ]))
    # share of ALL room-slot mean variance (slots without exogenous input contribute 0)
    tot = sum(mv @ mv for mv, _ in rows)
    exp_all = sum(np.sum((Q @ mv) ** 2) for mv, Q in with_q) / max(tot, 1e-12)
    exp_null = float(np.mean(nul)) * sum(mv @ mv for mv, _ in with_q) / max(tot, 1e-12)
    return {"n_room_slots": len(rows), "n_with_exo": len(with_q), "share_with_exo": float(share),
            "share_null_mean": float(np.mean(nul)), "share_null_q95": float(np.percentile(nul, 95)),
            "p": float((1 + np.sum(np.array(nul) >= share)) / (1 + len(nul))), "k_mean": k_mean,
            "excess_share_of_all_room_variance": float(exp_all - exp_null)}


def h01_replica(u: str, Dt: Data):
    """H01's P9 (mf_fit) on H01's own unit, raw and with self-repeats removed."""
    from h01data import Scheme
    from h01lib import Unit, mf_fit
    from h01common import unit as unitf
    global _SCH
    if "_SCH" not in globals():
        _SCH = Scheme(d=32)
    S = _SCH
    uo = S.unit(u)
    r1 = mf_fit(uo, np.random.default_rng(stable_seed(u, "mf")))
    st = Dt.st.filter(pl.col("unit") == u)
    dupset = set(st.filter(pl.col("dup"))["h01_row"].to_list())
    rows = [np.array([x for x in rr if x not in dupset]) for rr in uo.rows]
    keep = np.array([len(rr) >= 1 for rr in rows])
    V = np.stack([unitf(S.U[rr].mean(0)) if len(rr) else np.zeros(32) for rr in rows])
    ud = Unit(**{**uo.__dict__, "V": V[keep], "rows": [r for r, k in zip(rows, keep) if k], "agents": uo.agents[keep],
                 "day": uo.day[keep], "room": uo.room[keep], "nstmt": np.array([len(r) for r in rows])[keep]})
    r2 = mf_fit(ud, np.random.default_rng(stable_seed(u, "mf")))
    pick = lambda r: None if r is None else {k: r[k] for k in ("bJ_over_n", "R", "rho", "Nbar", "m_g")}  # noqa: E731
    return {"raw": pick(r1), "dedup": pick(r2)}


def main():
    t0 = time.time()
    sel = UNITS
    for a in sys.argv[1:]:
        if a.startswith("--units"):
            sel = sys.argv[sys.argv.index(a) + 1].split(",")
    Dt = Data()
    flat = []
    for u in sel:
        goal = Dt.units[u]["goal_no"]
        gdir = D / f"G{goal:02d}"; gdir.mkdir(parents=True, exist_ok=True)
        rng = np.random.default_rng(stable_seed(u, "explore"))
        res = {"unit": u, "goal_no": goal, "days": Dt.units[u]["days"]}
        for dedup in (True, False):
            panels, info = build_panels(Dt, u, dedup=dedup)
            tag = "dedup" if dedup else "raw"
            res[f"info_{tag}"] = info
            for (ch, r), P in panels.items():
                if not dedup and ch != "c":
                    continue
                if not dedup and r == "wd":
                    continue
                res[f"{ch}_{r}_{tag}" if ch == "c" else f"{ch}_{r}"] = analyze_panel(P, ch, rng, do_nulls=dedup)
            if dedup:
                res["drive_share_day"] = drive_share(panels[("c", "day")], Dt, u, rng)
                res["drive_share_w30"] = drive_share(panels[("c", "w30")], Dt, u, rng)
        res["h01_p9"] = h01_replica(u, Dt)
        (gdir / f"{u}.json").write_text(json.dumps(res, indent=1, default=float))
        for key, v in res.items():
            if not isinstance(v, dict) or "L0" not in v:
                continue
            for lv, rec in v.items():
                flat.append({"unit": u, "goal_no": goal, "panel": key, "level": lv,
                             **{k: (x if not isinstance(x, list) else None) for k, x in rec.items() if not k.startswith("_")},
                             **{f"{k}_lo": x[0] for k, x in rec.items() if k.startswith("ci_") and isinstance(x, list)},
                             **{f"{k}_hi": x[1] for k, x in rec.items() if k.startswith("ci_") and isinstance(x, list)}})
        print(f"{u} done {time.time() - t0:.0f}s", flush=True)
    df = pl.DataFrame(flat, infer_schema_length=None)
    name = "results_units.parquet" if sel == UNITS else f"results_units_{'_'.join(sel)}.parquet"
    df.write_parquet(D / name, compression="zstd")
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
