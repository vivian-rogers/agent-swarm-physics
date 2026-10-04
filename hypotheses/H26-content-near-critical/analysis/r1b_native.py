"""H26 round 1b native tests (2026-10-04; predictions in goalperiod-subhypotheses/{NE42,G12}/README.md, written first).

NE42  #39 -> #40 -> #41 with each agent's modal #39 room as a pseudo-room in all three periods (GPT-5 excluded):
      H26's room excess g_ex (L3 = L2 deviations, within minus cross, cross-share normalized) for content, activity and
      talk at day and w30 resolution, round-1b inputs (r1b/<tag>/ from scheme/build.py), day bootstrap (400 draws);
      the #40 - mean(#39, #41) difference with independent day bootstraps per period.
G12   #12 debates, motion field on vs off: 10-min slots; on = inside a debate's team window (DQ6). Content states =
      agent x slot means of unit statement vectors (H01 round-1b scheme: restatements removed, bge and gte).
      Deviations from the agent's #12 mean, then the static goal/kickoff directions (shared goal table) and the
      exogenous (human, automated) message directions of slots t-3..t projected out (L2). Whole-room gain g_room
      (one room: an upper bound) summed separately over on and off slots; motion removal = for each debate, the
      leave-one-agent-out mean direction of the other agents' on-slot deviations projected out (g_on_rm).
      Bootstrap: debates (on) and days (off), 400 draws.

Writes data/processed/H26-content-near-critical/r1b/native.json.
Usage: uv run python hypotheses/H26-content-near-critical/analysis/r1b_native.py
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.argv += [] if "--r1b" in sys.argv else ["--r1b", "bge_fixed"]   # explore.py reads --r1b at import; reset per tag below
sys.path.insert(0, str(HERE))
import h26lib as L  # noqa: E402
import explore as EX  # noqa: E402
sys.path.insert(0, str(ROOT / "hypotheses/H01-emergent-superagents-exist/analysis"))
sys.path.insert(0, str(ROOT / "hypotheses/H01-emergent-superagents-exist/scheme"))
from h01data import Scheme  # noqa: E402
from h01common import guard_holdout, unit, whiten_apply  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

DD = ROOT / "data/processed/H26-content-near-critical"
H01 = ROOT / "data/processed/H01-emergent-superagents-exist"
SH = ROOT / "data/processed/shared"
GPT5 = 10
B = 400


# ============================================================================ NE42
def ne42(tag: str, channels=("c", "a", "k")) -> dict:
    EX.D = DD / "r1b" / tag
    Dt = EX.Data()
    r39 = Dt.rooms.filter((pl.col("unit") == "39") & pl.col("room").is_not_null())
    lab = {a: int(r) for a, r in r39.group_by("agent").agg(pl.col("room").mode().first()).iter_rows() if a != GPT5}
    out = {"labels": {str(k): v for k, v in lab.items()}}
    boots = {}
    for u in ("39", "40", "41"):
        panels, info = EX.build_panels(Dt, u, dedup=True)
        rng = np.random.default_rng(EX.stable_seed(u, "r1b_ne42", tag))
        for ch in channels:
            for res in ("day", "w30"):
                P = panels[(ch, res)]
                room = np.array([lab.get(int(a), -1) for a in P.agent])
                Pp = replace(P, room=room)
                C, gg, _ = L.run_level(Pp, 2)
                bs = L.bootstrap(C, B=B, rng=rng, keys=("g_ex", "rho_ex", "g_room", "g_all"))
                # actual-room excess for reference (#39, #41 two rooms; #40 merged)
                Ca, ga, _ = L.run_level(P, 2)
                key = f"{ch}_{res}"
                out.setdefault(u, {})[key] = {
                    "g_ex_pseudo": gg["g_ex"], "rho_w": gg["rho_w"], "rho_c": gg["rho_c"], "Nr": gg["Nr"],
                    "ci_g_ex_pseudo": L.ci(np.clip(bs["g_ex"], -1, 1)), "g_all": gg["g_all"],
                    "g_ex_actual_rooms": ga["g_ex"] if np.isfinite(ga.get("rho_c", np.nan)) else None}
                boots[(u, key)] = np.clip(bs["g_ex"], -1, 1)
    for ch in channels:
        for res in ("day", "w30"):
            key = f"{ch}_{res}"
            vals = {u: out[u][key]["g_ex_pseudo"] for u in ("39", "40", "41")}
            v = {u: (np.clip(x, -1, 1) if x is not None and np.isfinite(x) else np.nan) for u, x in vals.items()}
            d = v["40"] - 0.5 * (v["39"] + v["41"])
            bd = boots[("40", key)] - 0.5 * (boots[("39", key)] + boots[("41", key)])
            out.setdefault("diff_40_minus_mean_39_41", {})[key] = {"est": float(d), "ci": L.ci(bd)}
    c = out["diff_40_minus_mean_39_41"]
    gx = lambda u, k: out[u][k]["g_ex_pseudo"]  # noqa: E731
    if "c" in channels:
        out["N1a_pass"] = bool(np.clip(gx("40", "c_w30"), -1, 1) < 0.15 and gx("39", "c_w30") >= 0.3 and gx("41", "c_w30") >= 0.3)
    if "a" in channels:
        out["N1b_pass"] = bool(abs(c["a_w30"]["est"]) < 0.2)
        out["N1c_pass"] = bool(np.clip(gx("40", "k_w30"), -1, 1) < 0.15)
    return out


# ============================================================================ G12
def g12(h01tag: str, model: str, rng) -> dict:
    S = Scheme(d=32, base=H01 / "r1b" / h01tag)
    st = S.st.filter(pl.col("goal_no") == 12)
    days = sorted(st["pt_date"].unique().to_list())
    guard_holdout(days)
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days)).select("pt_date", "win_start", "window_s")
    ws = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    W = int(max(cal["window_s"].to_list()) // 600) + 1
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 12) & pl.col("preferred") & ~pl.col("holdout") & (pl.col("label_kind") == "team"))
    deb = gt.group_by("unit").agg(pl.col("t_valid_from").min().alias("t0"), pl.col("t_valid_to").max().alias("t1")).sort("t0")
    dmap = {d: i for i, d in enumerate(days)}

    def slot_of(t, d):
        return int((t - ws[d]).total_seconds() // 600)
    st = st.with_columns(pl.struct("t", "pt_date").map_elements(lambda s: slot_of(s["t"], s["pt_date"]), return_dtype=pl.Int64).alias("w"))
    st = st.filter(pl.col("w") >= 0)
    # on/off and debate id per (day, slot): slot midpoint inside a debate window
    import datetime as dt
    on_id = {}
    for d in days:
        for w in range(W):
            mid = ws[d] + dt.timedelta(seconds=600 * w + 300)
            for k, (t0, t1) in enumerate(deb.select("t0", "t1").iter_rows()):
                if t0 <= mid < t1:
                    on_id[(dmap[d], w)] = k
    g = st.group_by("agent", "pt_date", "w", maintain_order=True).agg(pl.col("row")).sort("agent", "pt_date", "w")
    n = g.height; NS = 3
    X = np.full((n, 32), np.nan); A = np.full((n, NS, 32), np.nan); Bm = np.full((n, NS, 32), np.nan)
    for o, ix in enumerate(g["row"].to_list()):
        ix = np.asarray(ix)
        X[o] = S.U[ix].mean(0)
        if len(ix) >= 2:
            for sp in range(NS):
                p = rng.permutation(ix); h = len(p) // 2
                A[o, sp] = S.U[p[:h]].mean(0); Bm[o, sp] = S.U[p[h:]].mean(0)
    ag = g["agent"].to_numpy().astype(int); dd = np.array([dmap[x] for x in g["pt_date"].to_list()]); ww = g["w"].to_numpy().astype(int)
    t = dd * W + ww
    on = np.array([(d_, w_) in on_id for d_, w_ in zip(dd, ww)])
    debk = np.array([on_id.get((d_, w_), -1) for d_, w_ in zip(dd, ww)])
    # static directions (goal + kickoff, shared table) and exogenous directions (human / automated messages)
    gh = S.ghat(12, "I")
    static = L.orthobasis(np.array([v for v in (gh["goal"], gh["kick"]) if v is not None]))
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "speaker_kind"])
            .filter(pl.col("pt_date").is_in(days) & pl.col("speaker_kind").is_in(["human", "automated"])))
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("emb_row")
    chat = chat.join(ci, on="message_id", how="inner")
    E = np.load(SH / f"embeddings/chat_{'bge_small' if model == 'bge_small' else 'gte_modernbert'}.npy", mmap_mode="r")
    Xe = unit(whiten_apply(np.asarray(E[chat["emb_row"].to_numpy()], dtype=np.float32), S.bases["I"], 32))
    ed = np.array([dmap[x] for x in chat["pt_date"].to_list()])
    ew = np.array([slot_of(tt, d) for tt, d in zip(chat["t"].to_list(), chat["pt_date"].to_list())])
    exo = {}
    for sl in np.unique(t):
        d0, w0 = divmod(int(sl), W)
        m = (ed == d0) & (ew <= w0) & (ew >= w0 - 3)
        exo[int(sl)] = L.orthobasis(Xe[m]) if m.any() else None
    P = L.Panel(agent=ag, t=t, day=dd, wod=ww, room=np.zeros(n, int), X=X, A=A, B=Bm, grp=ag, static=static, exo=exo,
                res="w30", meta={"unit": "12", "W": W})
    dX, dA, dB, okX, okS = L.deviations(P, 2)

    def gain(mask, dayvec, dXm=dX, dAm=dA, dBm=dB):
        Pm = replace(P, agent=P.agent[mask], t=P.t[mask], day=dayvec[mask], wod=P.wod[mask], room=P.room[mask],
                     X=P.X[mask], A=P.A[mask], B=P.B[mask], grp=P.grp[mask])
        C = L.contributions(Pm, dXm[mask], dAm[mask], dBm[mask], okX[mask], okS[mask])
        g0 = L.gains(C)
        bs = L.bootstrap(C, B=B, rng=rng, keys=("g_room", "rho_w"))
        return {"g_room": g0["g_room"], "rho_w": g0["rho_w"], "Nr": g0["Nr"], "ci": L.ci(np.clip(bs["g_room"], -1, 1)),
                "n_obs": int((okX & mask).sum()), "n_units": int(len(np.unique(dayvec[mask])))}
    res = {"W_slots": W, "n_debates": int(deb.height), "n_on_rows": int(on.sum()), "n_off_rows": int((~on).sum())}
    res["on"] = gain(on, debk)
    res["off"] = gain(~on, dd)
    # motion removal: leave-one-agent-out debate mean direction of the other agents' on-slot deviations
    dXr, dAr, dBr = dX.copy(), dA.copy(), dB.copy()
    for k in np.unique(debk[on]):
        mk = on & (debk == k) & okX
        for a in np.unique(ag[mk]):
            oth = mk & (ag != a)
            if oth.sum() < 2:
                continue
            q = dX[oth].mean(0); nq = np.linalg.norm(q)
            if nq < 1e-12:
                continue
            q = (q / nq)[None]
            me = on & (debk == k) & (ag == a)
            dXr[me] = dX[me] - (dX[me] @ q.T) @ q
            dAr[me] = dA[me] - (dA[me] @ q.T) @ q
            dBr[me] = dB[me] - (dB[me] @ q.T) @ q
    res["on_rm"] = gain(on, debk, dXr, dAr, dBr)
    go, gf, gr = res["on"]["g_room"], res["off"]["g_room"], res["on_rm"]["g_room"]
    res["N2a"] = bool(go > gf)
    res["N2b"] = bool(go > 0 and gr <= 0.5 * go)
    return res


def main():
    path = DD / "r1b" / "native.json"
    out = json.loads(path.read_text()) if path.exists() else {}
    out["NE42"] = {"bge_fixed": ne42("bge_fixed"), "gte_fixed": ne42("gte_fixed", channels=("c",))}
    for t, r in out["NE42"].items():
        print("NE42", t, {u: {k: round(v["g_ex_pseudo"], 3) if v["g_ex_pseudo"] is not None and np.isfinite(v["g_ex_pseudo"]) else None
                              for k, v in r[u].items()} for u in ("39", "40", "41")},
              {k: v for k, v in r.items() if k.startswith("N1")}, flush=True)
    out["G12"] = {}
    for h01tag, model in (("bge_restate", "bge_small"), ("gte_restate", "gte_modernbert")):
        r = g12(h01tag, model, np.random.default_rng(20261004 + 12))
        out["G12"][h01tag] = r
        print("G12", h01tag, {k: (round(r[k]["g_room"], 3), [round(x, 3) for x in r[k]["ci"]]) for k in ("on", "off", "on_rm")},
              r["N2a"], r["N2b"], flush=True)
    path.write_text(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, "item") else (None if o is None else str(o))))


if __name__ == "__main__":
    main()
