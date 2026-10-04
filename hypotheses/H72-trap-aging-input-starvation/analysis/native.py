"""H72 native tests (predictions dated 2026-10-04 in the card, before running).

N1 NE43   G51 B = 08-07..08-20 (nudges on) vs C = 08-21..09-02 (no nudges): clock shift, slope invariance, C indicator.
N2 blocked spells (Jev v3.1 p_blocked >= 0.5 runs) in G51 and G27: aging slope with and without directed starvation.
N3 #focus room (G51 08-05..08-24): input supply by room and whether the s clocks absorb the room coefficient.
Usage: uv run python hypotheses/H72-trap-aging-input-starvation/analysis/native.py
Writes data/processed/H72-trap-aging-input-starvation/native/native.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h72lib as L  # noqa: E402

HF = L.HF
B = 200


def boot_terms(P, terms, extra_fn, keys, B=B, seed=0, link="logit"):
    rng = np.random.default_rng(seed)
    rpd = HF.rows_per_day(P["day"])
    D = []
    for _ in range(B):
        idx = HF.block_resample(P["day"], rng, rpd)
        ex = {k: v[idx] for k, v in extra_fn().items()} if extra_fn else None
        Q = sub(P, idx)
        f, nm = L.fit_terms(Q, terms, link=link, extra=ex)
        D.append([L.coef(f, nm, k)[0] if k in nm else np.nan for k in keys])
    return np.array(D)


def sub(P, idx):
    Q = {k: (v[idx] if isinstance(v, np.ndarray) and len(v) == P["n"] else v) for k, v in P.items()}
    Q["nuis"] = {k: v[idx] for k, v in P["nuis"].items()}
    Q["n"] = len(idx)
    return Q


def ci(x):
    x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def n1(g):
    d = g.filter(pl.col("goal_no") == 51)
    Bw = d.filter(pl.col("pt_date").is_between(pl.lit("2026-08-07"), pl.lit("2026-08-20")))
    Cw = d.filter(pl.col("pt_date").is_between(pl.lit("2026-08-21"), pl.lit("2026-09-02")))
    out = {"design": {}}
    for nm, w in (("B", Bw), ("C", Cw)):
        out["design"][nm] = {"gates": w.height, "median_s_dir_min": float(w["s_dir"].median() / 60),
                             "median_s_novel_min": float(w["s_novel"].median() / 60),
                             "median_a_sus_min": float(w["a_sus"].median() / 60)}
    out["design"]["s_dir_ratio_C_over_B"] = out["design"]["C"]["median_s_dir_min"] / out["design"]["B"]["median_s_dir_min"]
    fits = {}
    for nm, w in (("B", Bw), ("C", Cw)):
        P = L.prep(w, "sus", "novel")
        pt = L.point(P)
        D = boot_terms(P, ("la", "ls"), None, ["la", "ls"], seed=1 if nm == "B" else 2)
        fits[nm] = {"beta_a": pt["beta_a"], "beta_s": pt["beta_s"], "beta_a0": pt["beta_a0"], "draws": D,
                    "ci_a": ci(D[:, 0]), "ci_s": ci(D[:, 1]), "n": P["n"], "escapes": int(P["y"].sum())}
    dA = fits["C"]["draws"][:, 0] - fits["B"]["draws"][:, 0]
    dS = fits["C"]["draws"][:, 1] - fits["B"]["draws"][:, 1]
    out["fits"] = {k: {kk: vv for kk, vv in v.items() if kk != "draws"} for k, v in fits.items()}
    out["delta_beta_a"] = {"est": fits["C"]["beta_a"] - fits["B"]["beta_a"], "ci": ci(dA)}
    out["delta_beta_s"] = {"est": fits["C"]["beta_s"] - fits["B"]["beta_s"], "ci": ci(dS)}
    # pooled with a C indicator
    BC = pl.concat([Bw, Cw])
    P = L.prep(BC, "sus", "novel")
    Cind = (P["days"] >= "2026-08-21").astype(float)
    f, nm = L.fit_terms(P, ("la", "ls"), extra={"C": Cind})
    D = boot_terms(P, ("la", "ls"), lambda: {"C": Cind}, ["C"], seed=3)
    out["C_indicator"] = {"est": L.coef(f, nm, "C")[0], "ci": ci(D[:, 0])}
    out["verdict"] = {
        "a_design_sdir_up_20pct": out["design"]["s_dir_ratio_C_over_B"] >= 1.2,
        "b_invariance": bool(abs(out["delta_beta_a"]["est"]) < 0.3 and abs(out["delta_beta_s"]["est"]) < 0.3
                             and out["delta_beta_a"]["ci"][0] <= 0 <= out["delta_beta_a"]["ci"][1]
                             and out["delta_beta_s"]["ci"][0] <= 0 <= out["delta_beta_s"]["ci"][1]),
        "c_indicator_ci_includes_0": out["C_indicator"]["ci"][0] <= 0 <= out["C_indicator"]["ci"][1]}
    return out


def blocked_P(b, per):
    d = b.filter((pl.col("goal_no") == per) & pl.col("y_leave").is_not_null())
    s_none = d["s_dir"].is_null().to_numpy()
    s_raw = np.where(s_none, d["s_lc"].fill_null(L.FLOOR).to_numpy(), d["s_dir"].fill_null(L.FLOOR).to_numpy())
    nuis = {"win_dir": np.log1p(d["win_dir"].to_numpy().astype(float)),
            "win_novel": np.log1p(d["win_novel"].to_numpy().astype(float)),
            "win_calls": np.log1p(d["win_calls"].to_numpy().astype(float)),
            "s_none": s_none.astype(float)}
    nuis = {k: v for k, v in nuis.items() if np.std(v) > 0}
    days = d["pt_date"].to_numpy()
    return {"y": d["y_leave"].cast(pl.Float64).to_numpy(), "la": np.log(d["j"].to_numpy().astype(float)),
            "ls": L.lmin(s_raw), "nuis": nuis, "agent": d["agent"].to_numpy(),
            "day": np.unique(days, return_inverse=True)[1], "days": days, "n": d.height,
            "spells": int(d.select("agent", "pt_date", "spell").unique().height)}


def n2(b):
    out = {}
    for per in (51, 27):
        P = blocked_P(b, per)
        pt = L.point(P)
        bt = L.bootstrap(P, B, seed=per + 7)
        r = {"windows": P["n"], "spells": P["spells"], "leaves": int(P["y"].sum()),
             "beta_age0": pt["beta_a0"], "ci_age0": bt["ci_a0"], "beta_age": pt["beta_a"], "ci_age": bt["ci_a"],
             "beta_s": pt["beta_s"], "ci_s": bt["ci_s"], "rho": pt["rho"], "ci_rho": bt["ci_rho"]}
        r["pass"] = bool(r["ci_age0"][1] < 0 and r["rho"] < 0.3 and r["ci_s"][0] <= 0 <= r["ci_s"][1])
        ptc = L.point(P, link="cloglog")
        r["cloglog"] = {k: ptc[k] for k in ("beta_a0", "beta_a", "beta_s", "se_a", "se_s")}
        out[f"G{per:02d}"] = r
    return out


def n3(g):
    d = g.filter((pl.col("goal_no") == 51) & pl.col("pt_date").is_between(pl.lit("2026-08-05"), pl.lit("2026-08-24"))
                 & pl.col("room").is_in([0, 15]))
    both = d.group_by("agent").agg(pl.col("room").n_unique().alias("nr")).filter(pl.col("nr") == 2)["agent"]
    d = d.filter(pl.col("agent").is_in(both))
    out = {"agents": int(len(both)), "gates": d.height,
           "gates_focus": int((d["room"] == 15).sum())}
    out["median_s_novel_min"] = {"focus": float(d.filter(pl.col("room") == 15)["s_novel"].median() / 60),
                                 "general": float(d.filter(pl.col("room") == 0)["s_novel"].median() / 60)}
    out["s_ratio_focus_over_general"] = out["median_s_novel_min"]["focus"] / out["median_s_novel_min"]["general"]
    P = L.prep(d, "sus", "novel")
    F = (P["room"] == 15).astype(float)
    out["escapes"] = int(P["y"].sum())
    f0, n0 = L.fit_terms(P, ("la",), extra={"F": F})
    f1, n1_ = L.fit_terms(P, ("la", "ls"), extra={"F": F})
    rng = np.random.default_rng(15)
    rpd = HF.rows_per_day(P["day"])
    D = []
    for _ in range(B):
        idx = HF.block_resample(P["day"], rng, rpd)
        Q = sub(P, idx)
        a, na = L.fit_terms(Q, ("la",), extra={"F": F[idx]})
        c, nc = L.fit_terms(Q, ("la", "ls"), extra={"F": F[idx]})
        D.append([L.coef(a, na, "F")[0], L.coef(c, nc, "F")[0]])
    D = np.array(D)
    bF0, bF1 = L.coef(f0, n0, "F")[0], L.coef(f1, n1_, "F")[0]
    out["beta_F_without_s"] = {"est": bF0, "ci": ci(D[:, 0])}
    out["beta_F_with_s"] = {"est": bF1, "ci": ci(D[:, 1])}
    out["delta_F"] = {"est": bF1 - bF0, "ci": ci(D[:, 1] - D[:, 0])}
    out["pass_b"] = bool(abs(bF1 - bF0) < max(0.1, 0.3 * abs(bF0)))
    out["pass_a"] = bool(out["s_ratio_focus_over_general"] >= 2)
    return out


def main():
    g = pl.read_parquet(L.OUT / "gates.parquet")
    b = pl.read_parquet(L.OUT / "blocked.parquet")
    res = {"N1_NE43": n1(g)}
    print("N1", json.dumps({k: v for k, v in res["N1_NE43"].items() if k != "fits"}, default=float), flush=True)
    res["N2_blocked"] = n2(b)
    print("N2", json.dumps(res["N2_blocked"], default=float), flush=True)
    res["N3_focus"] = n3(g)
    print("N3", json.dumps(res["N3_focus"], default=float), flush=True)
    (L.OUT / "native").mkdir(parents=True, exist_ok=True)
    (L.OUT / "native/native.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
