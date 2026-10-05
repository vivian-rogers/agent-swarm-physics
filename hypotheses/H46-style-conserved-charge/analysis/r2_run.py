"""H46 round 2 real-data run (non-reserved data only). Pre-registered in the card, section "Round 2", 2026-10-05 02:50 UTC;
amendments R2-A1..A4 after the synthetic validation.

  r1  genre-controlled style: NE41 (tc, g, gp; genre-matched strata), #12 judges and #51 Prankster (round-1 native code
      on the new matrices), goal switches (O1 class test, O2 fingerprint) and content with bge and gte.
  r2  drift-and-reset model on regime III: variance growth, cross-products within vs across forced erasures, the
      covariance-implied growth, the self-imitation pull with the room control; pooled, per lab, per goal period.
  r3  function-word charge (messages with >= 10 tokens): every NE class, NE41, fingerprints across goal switches.
Outputs: data/processed/H46-style-conserved-charge/r2/{r1,r2,r3}.json
Usage: uv run python hypotheses/H46-style-conserved-charge/analysis/r2_run.py [r1] [r2] [r3]
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402
import native as N  # noqa: E402
import r2lib as R  # noqa: E402


def dumps(x):
    return json.dumps(x, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))


def goal_tests(m, mats, chans, fp_vars, bounds_cls=("goal",)):
    dt_ = L.day_table(m, mats)
    L.add_demeaned(dt_, list(mats))
    bounds = pl.read_parquet(L.DATA / "boundaries.parquet")
    bounds = bounds.filter(pl.col("cls").is_in(list(bounds_cls)) & (pl.col("ne") != "NE14"))
    fd = L.unit_first_days()
    rows = L.eval_boundaries(bounds, dt_, {c: c for c in chans}, fd)
    out = {"tests": {}, "fingerprint": {}}
    for cls in bounds_cls:
        sub = rows.filter(pl.col("cls") == cls)
        out["tests"][cls] = {c: {k: v for k, v in L.class_test(sub, c).items()} for c in chans}
    fps = []
    for b in bounds.filter(pl.col("cls") == "goal").iter_rows(named=True):
        for c in fp_vars:
            r = L.fingerprint_boundary(dt_, c + "_dm", set(b["pre"]), set(b["post"]))
            if "cross" in r:
                fps.append({"label": b["label"], "variant": c, **r})
    fp = pl.DataFrame(fps)
    for c in fp_vars:
        f = fp.filter(pl.col("variant") == c)
        out["fingerprint"][c] = {"cross": float(f["cross"].mean()), "chance": float(f["chance"].mean()),
                                 "share_ge_3x": float((f["cross"] >= 3 * f["chance"]).mean()), "n": f.height,
                                 "per_boundary": dict(zip(f["label"].to_list(), f["cross"].round(3).to_list()))}
    piv = fp.pivot(values="cross", index="label", on="variant")
    for a in fp_vars:
        for b_ in fp_vars:
            if a < b_:
                out["fingerprint"][f"share_{a}_gt_{b_}"] = float((piv[a] > piv[b_]).mean())
    return out, rows


# ----------------------------------------------------------------------------------------------- R1
def run_r1(m, V):
    out = {}
    t0 = time.time()
    pr, i1, i2 = R.ne41_pairs(m)
    cb, cg = R.content(m, "bge"), R.content(m, "gte")
    ne = {}
    for v in ("tc", "g", "gp"):
        ne[v] = R.ne41_test(pr, i1, i2, V[v])
    ne["content_bge"] = R.ne41_test(pr, i1, i2, cb, cosine=True)
    ne["content_gte"] = R.ne41_test(pr, i1, i2, cg, cosine=True)
    cellm = (m["is_reply"].cast(pl.Int8) * 2 + (m["n_mention"] > 0).cast(pl.Int8)).to_numpy()
    cell = cellm[i1] * 4 + cellm[i2]
    for v in ("tc", "gp"):
        ne[v + "_genre_matched"] = R.ne41_test(pr, i1, i2, V[v], cell=cell)
    out["NE41"] = {"n_pairs": {k: int((pr["label"] == k).sum()) for k in ("within", "forced", "voluntary")}, **ne}
    print("NE41", {k: (round(v["forced"]["T"], 3), round(v["forced"]["lo"], 3), round(v["forced"]["hi"], 3))
                   for k, v in ne.items()}, f"{time.time() - t0:.0f}s", flush=True)
    # natives on the new matrices: monkeypatch the round-1 native module
    idx = {k: i for i, k in enumerate(m["msg"].to_list())}
    MATS = {"tc": V["tc"], "g": V["g"], "gp": V["gp"], "content": cb}

    def mats_for(sub):
        rows = np.array([idx[k] for k in sub["msg"].to_list()])
        return {c: MATS[c][rows] for c in N.CH}
    N.mats_for = mats_for
    N.CH = ("tc", "g", "gp", "content")
    g12 = N.g12(m)
    out["G12"] = {k: v for k, v in g12.items() if k.startswith(("role9", "onetime", "fp_", "side_", "switch_"))}
    g51 = N.g51(m)
    out["G51"] = {"prankster": {a: v for a, v in g51["agents"].items() if v["group"] == "prankster"},
                  "agents": g51["agents"], "NE38": g51["NE38"],
                  **{k: v for k, v in g51.items() if k.startswith("summary_")}}
    print("G12", dumps({k: v for k, v in out["G12"].items() if k.startswith(("role9", "onetime"))})[:1500], flush=True)
    print("G51 prankster", dumps(out["G51"]["prankster"])[:800], flush=True)
    # goal switches
    mats = {"tc": V["tc"], "g": V["g"], "gp": V["gp"], "content": R.content(m, "bge"), "content_gte": cg}
    gt, rows = goal_tests(m, mats, list(mats), ["tc", "gp", "content"])
    out["goal"] = gt
    rows.write_parquet(R.R2 / "r1_goal_rows.parquet")
    print("goal", {c: round(gt["tests"]["goal"][c]["T"], 3) for c in mats}, dumps(
        {k: (v["cross"] if isinstance(v, dict) else v) for k, v in gt["fingerprint"].items()}), flush=True)
    return out


# ----------------------------------------------------------------------------------------------- R2
def run_r2(m, V):
    sel = m["regime"].to_numpy() == "III"
    m3 = m.filter(pl.Series(sel))
    ag3 = m3["agent"].to_numpy()
    lp = R.lag_pairs(m3)
    rows, refs, labs, gaps, nref = R.pull_obs(m3)
    labg = dict(zip(m3["agent"].to_list(), m3["labg"].to_list()))
    out = {}
    for v in ("gp", "tc"):
        t0 = time.time()
        Xc = R.unit_center(V[v][sel], m3)
        G = R.growth(Xc, m3)
        res = {"pooled": {}}
        gf = R.growth_fit(G, n_boot=500)
        cp = R.cross_products(Xc, lp, n_boot=500)
        cpv = R.cross_products(Xc, lp, across="voluntary", n_boot=300)
        room = R.room_deviation(Xc, m3, rows) if v == "gp" else None
        pu = R.pull(Xc, rows, refs, labs, gaps, nref, ag3, room_dev=room, n_boot=500)
        res["pooled"] = {"growth": gf, "cross": cp, "cross_voluntary": cpv, "implied": R.implied_growth(cp, lp, gf),
                         "pull": pu}
        print(v, "pooled", dumps({"dbar": gf["dbar"], "dbar_ci": gf.get("dbar_ci"), "slope_ci": gf.get("slope_ci"),
                                  "phi": gf["phi"], "phi_ci": gf.get("phi_ci"),
                                  "dC": {l: (x["dC"], x["dC_ci"]) for l, x in cp["lags"].items()},
                                  "phi_C": cp.get("phi_C"), "phi_C_ci": cp.get("phi_C_ci"),
                                  "implied": res["pooled"]["implied"],
                                  "pull": {k: pu[k] for k in pu if k.startswith(("rho", "diff", "room"))}}), flush=True)
        res["labs"] = {}
        for lg in ("Anthropic", "OpenAI", "Google", "DeepSeek", "other"):
            ags = np.array([a for a, g in labg.items() if g == lg])
            if len(ags) < 2:
                continue
            gl = R.growth_fit(G, agents_sel=ags, n_boot=300)
            lpl = lp.filter(pl.col("agent").is_in(ags.tolist()))
            cl = R.cross_products(Xc, lpl, n_boot=300)
            keep = np.isin(ag3[rows], ags)
            pl_ = R.pull(Xc, rows[keep], refs[keep], labs[keep], gaps[keep], nref[keep], ag3, n_boot=300)
            res["labs"][lg] = {"n_agents": int(len(ags)), "growth": gl, "cross": cl,
                               "implied": R.implied_growth(cl, lpl, gl), "pull": pl_}
            print(v, lg, round(gl["dbar"], 3), gl.get("dbar_ci"), "dC1", round(cl["lags"][1]["dC"], 3),
                  cl["lags"][1]["dC_ci"], "phiC", cl.get("phi_C"), "rho", round(pl_["rho_within"], 3),
                  round(pl_["rho_forced"], 3), flush=True)
        if v == "gp":   # per goal period (replication rows)
            res["periods"] = {}
            gno = m3["goal_no"].to_numpy()
            for g in np.unique(gno):
                agp = lp.join(pl.DataFrame({"i": np.arange(len(m3), dtype=np.uint32), "g": gno}), on="i")
                lpg = agp.filter(pl.col("g") == g).drop("g")
                if (lpg.filter((pl.col("lag") == 1) & (pl.col("label") == "forced")).height < 100):
                    continue
                cg_ = R.cross_products(Xc, lpg, n_boot=200)
                keep = gno[rows] == g
                pg = R.pull(Xc, rows[keep], refs[keep], labs[keep], gaps[keep], nref[keep], ag3, n_boot=200)
                res["periods"][int(g)] = {"cross": cg_, "pull": pg, "n_agents": int(len(np.unique(ag3[gno == g])))}
                print(v, "G", g, round(cg_["lags"][1]["dC"], 3), cg_["lags"][1]["dC_ci"], round(pg["diff"], 3),
                      pg.get("diff_ci"), flush=True)
        out[v] = res
        print(v, f"{time.time() - t0:.0f}s", flush=True)
    return out


# ----------------------------------------------------------------------------------------------- R3
def run_r3(m, V):
    keep = m["n_tok"].to_numpy() >= R.MIN_TOK
    mf = m.filter(pl.Series(keep))
    W = {k: v[keep] for k, v in V.items() if not k.startswith("_")}
    W["content"] = R.content(mf, "bge")
    W["fw_tc"] = np.hstack([W["fw"], W["tc"]])
    out = {"n_messages": int(mf.height), "words": [w[2:] for w in V["_words"]]}
    chans = ["tc", "core", "fw", "fw_g", "content"]
    gt, rows = goal_tests(mf, {c: W[c] for c in chans + ["fw_tc"]}, chans, ["tc", "fw", "fw_tc", "content"],
                          bounds_cls=("goal", "rooms", "nudger", "roster", "scaffold"))
    out["classes"] = gt
    rows.write_parquet(R.R2 / "r3_rows.parquet")
    print("R3 classes", {cls: {c: round(t[c].get("T", np.nan), 3) for c in chans} for cls, t in gt["tests"].items()},
          flush=True)
    print("R3 fp", dumps({k: (v["cross"] if isinstance(v, dict) else v) for k, v in gt["fingerprint"].items()}), flush=True)
    m3 = mf.filter(pl.col("regime") == "III")
    i3 = np.where(mf["regime"].to_numpy() == "III")[0]
    pr, i1, i2 = R.ne41_pairs(m3)
    out["NE41"] = {c: R.ne41_test(pr, i1, i2, W[c][i3], cosine=(c == "content")) for c in chans}
    print("R3 NE41", {c: (round(v["forced"]["T"], 3), round(v["forced"]["lo"], 3), round(v["forced"]["hi"], 3))
                      for c, v in out["NE41"].items()}, flush=True)
    # feature excess at goal switches for fw (which words carry any shift)
    return out


def main():
    only = sys.argv[1:] or ["r1", "r2", "r3"]
    m = R.load()
    words = R.fw_words(m)
    V = R.variants(m, words)
    V["_words"] = words
    for name, fn in (("r1", run_r1), ("r2", run_r2), ("r3", run_r3)):
        if name in only:
            res = fn(m, V)
            (R.R2 / f"{name}.json").write_text(dumps(res))


if __name__ == "__main__":
    main()
