"""H102 round 1 (exploratory, non-holdout): bimodality per unit, hopper positions, dose-response, field alignment,
for both embedding models and two variants (+ dedupe on the primary).

Writes data/processed/H102-room-domain-walls/results/raw_<tag>.json and raw_all.json.
Usage: uv run python hypotheses/H102-room-domain-walls/analysis/run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h102lib as L  # noqa: E402

RES = L.DATA / "results"
VARIANTS = [("bge_small", "style_resid", False), ("gte_modernbert", "style_resid", False),
            ("bge_small", "white32", False), ("gte_modernbert", "white32", False), ("bge_small", "style_resid", True)]


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return o


def all_agent_dose(fr, Xc, ah, rd, unit, A, B, n_boot=1000, seed=0):
    """Secondary: every home-A agent-day, s(home) on log1p(R_dom) (items from other-domain senders) and log1p(U),
    agent fixed effects. Uses full-data core centroids (leave-one-out for stayers)."""
    core = [a for a, v in ah.items() if v[1] in ("stayer", "core")]
    cB = np.mean([ah[a][2] for a in core if ah[a][0] == B], 0)
    r = {(x["agent"], x["pt_date"]): x for x in rd.filter(pl.col("unit") == unit).to_dicts()}
    rows = []
    g = fr.filter((pl.col("home") == A) & (pl.col("room_at") == A))
    for (k, d), gd in g.group_by("agent", "pt_date"):
        if gd.height < 3 or (k, d) not in r or k not in ah:
            continue
        cA = np.mean([ah[a][2] for a in core if ah[a][0] == A and a != k], 0)
        u = cB - cA
        s = float((Xc[gd["ix"].to_numpy()].mean(0) - cA) @ u / (u @ u))
        rows.append((k, d, s, gd.height, np.log1p(r[(k, d)]["R_dom"]), np.log1p(r[(k, d)]["U"])))
    k_, d_, y, w, R, U = map(np.array, zip(*rows))

    def fit(ix):
        kk, Y, RR, UU, ww = k_[ix], y[ix].copy(), R[ix].copy(), U[ix].copy(), w[ix]
        for a in np.unique(kk):
            m = kk == a
            for arr in (Y, RR, UU):
                arr[m] -= np.average(arr[m], weights=ww[m])
        W = np.sqrt(ww)
        return np.linalg.lstsq(np.column_stack([RR, UU]) * W[:, None], Y * W, rcond=None)[0]
    b = fit(np.arange(len(y)))
    rng = np.random.default_rng(seed)
    days = np.array(sorted(set(d_)))
    bs = []
    for _ in range(n_boot):
        dd = rng.choice(days, len(days))
        bs.append(fit(np.concatenate([np.nonzero(d_ == x)[0] for x in dd])))
    bs = np.array(bs)
    return {"n": int(len(y)), "n_agents": int(len(np.unique(k_))), "kappa_Rdom": float(b[0]), "kappa_U": float(b[1]),
            "kappa_Rdom_ci_day": [float(np.percentile(bs[:, 0], 2.5)), float(np.percentile(bs[:, 0], 97.5))],
            "kappa_U_ci_day": [float(np.percentile(bs[:, 1], 2.5)), float(np.percentile(bs[:, 1], 97.5))]}


def reverse_hoppers(fr, Xc, ah, A, B):
    """#focus core members' statements made in #general: their s relative to their own home (B), using the other
    core member as the home centroid (leave-one-out) and #general stayers as the other centroid."""
    core = [a for a, v in ah.items() if v[1] == "core"]
    gen = [a for a, v in ah.items() if v[1] == "stayer" and v[0] == A]
    cA = np.mean([ah[a][2] for a in gen], 0)
    out = {}
    for c in core:
        others = [a for a in core if a != c]
        if not others:
            continue
        cB = np.mean([ah[a][2] for a in others], 0)
        u = cA - cB; den = u @ u
        g = fr.filter(pl.col("agent") == c)
        ih = g.filter(pl.col("room_at") == B)["ix"].to_numpy(); io = g.filter(pl.col("room_at") == A)["ix"].to_numpy()
        out[int(c)] = {"n_home": len(ih), "n_other": len(io),
                       "s_home": float((Xc[ih].mean(0) - cB) @ u / den) if len(ih) else None,
                       "s_other": float((Xc[io].mean(0) - cB) @ u / den) if len(io) else None}
    return out


def one(model, variant, dedupe, full=True):
    st, Xc, dom, rd = L.load(model, variant, dedupe)
    fields = pl.read_parquet(L.DATA / "fields.parquet")
    F = np.load(L.DATA / f"fields_{model}.npy")
    out = {"model": model, "variant": variant, "dedupe": dedupe, "units": {}}
    for u in L.UNITS:
        fr = L.unit_frame(st, dom, u)
        A, B = L.rooms_of(dom, u)
        ah = L.agent_halves(fr, Xc)
        r = {"A": A, "B": B}
        bt = L.bimodality_test(ah, A, B, n_null=1000 if full else 200, seed=1)
        if bt:
            wc = bt.pop("wc")
            s_all = np.array([v[0] for a, v in wc.items()])
            r["bimodality"] = bt
            r["I_all"] = float(np.mean((s_all >= 0.25) & (s_all <= 0.75)))
            r["s_by_agent"] = {int(a): {"s": v[0], "z": v[1], "home": int(v[2]), "role": ah[a][1]} for a, v in wc.items()}
        ru = rd.filter(pl.col("unit") == u)
        r["P_hop"] = float(ru["R_hop"].sum() / max(ru["n_items"].sum(), 1))
        r["P_dom"] = float(ru["R_dom"].sum() / max(ru["n_items"].sum(), 1))
        if fr.filter(pl.col("role") == "hopper").height:
            hp = L.hopper_positions(fr, Xc, ah, A, B)
            r["hoppers"] = hp
            if u == "51g":
                r["dose"] = L.dose_response(hp, rd, u, n_boot=2000 if full else 200, seed=3)
                r["dose_lag"] = L.dose_response(hp, rd, u, n_boot=2000 if full else 200, seed=4, lag=True)
                r["dose_all_agents"] = all_agent_dose(fr, Xc, ah, rd, u, A, B, n_boot=1000 if full else 200)
                r["reverse_hoppers"] = reverse_hoppers(fr, Xc, ah, A, B)
        if u in ("G38", "G44"):
            g = int(u[1:])
            f = fields.filter((pl.col("goal_no") == g) & (pl.col("kind") == "kickoff_room"))
            vb = F[f.filter(pl.col("room") == L.BEST)["frow"][0]]; vr = F[f.filter(pl.col("room") == L.REST)["frow"][0]]
            uf = vb - vr; uf /= np.linalg.norm(uf)
            r["field_alignment"] = L.field_alignment(ah, A, B, uf)
        out["units"][u] = r
    return clean(out)


def main():
    RES.mkdir(parents=True, exist_ok=True)
    allr = {}
    for model, variant, dd in VARIANTS:
        tag = f"{model}_{variant}{'_dedupe' if dd else ''}"
        r = one(model, variant, dd, full=(variant == "style_resid" and not dd))
        allr[tag] = r
        (RES / f"raw_{tag}.json").write_text(json.dumps(r, indent=1))
        print("done", tag, flush=True)
    (RES / "raw_all.json").write_text(json.dumps(allr, indent=1))


if __name__ == "__main__":
    main()
