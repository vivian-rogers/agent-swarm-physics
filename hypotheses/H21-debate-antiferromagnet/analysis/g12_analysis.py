"""H21 x G12: two-sublattice order in the debate week, on real data (exploratory; #12 is not held out).

Run only after the card's Observables / Null / Prediction and G12/README.md "Prediction" are written and dated.
Inputs: data/processed/H21-debate-antiferromagnet/G12/ (built by scheme/build_g12.py) + shared whitener (regime I)
and the shared unmasked embeddings (robustness only).
Outputs: data/processed/H21-debate-antiferromagnet/G12/results.json, per_debate.csv, verdict_rows.csv;
figures in hypotheses/H21-debate-antiferromagnet/goalperiod-subhypotheses/G12/figures/.

Usage: uv run python hypotheses/H21-debate-antiferromagnet/analysis/g12_analysis.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import afmlib as L  # noqa: E402
import h21core as C  # noqa: E402
from common import holdout_mask, load_whitener  # noqa: E402

DATA = ROOT / "data/processed/H21-debate-antiferromagnet/G12"
SH = ROOT / "data/processed/shared"
FIG = HERE.parent / "goalperiod-subhypotheses/G12/figures"
RNG = 20261003


def load(dim=32, masked=True):
    st_pl = pl.read_parquet(DATA / "statements.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == 12)
    assert not any(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    W = load_whitener("I", dim)
    if masked:
        E = np.load(DATA / "emb_masked.npy").astype(np.float32)
    else:
        Es = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
        E = np.asarray(Es[st_pl["chat_row"].to_numpy()], dtype=np.float32)
    X = W(E).astype(np.float64)
    deb = json.loads((DATA / "debates_resolved.json").read_text())
    name2a = dict(zip(st_pl["name"], st_pl["agent"]))
    t0 = st_pl["t"].min()

    def sec(s):
        return (dt.datetime.fromisoformat(s) - t0).total_seconds()

    debates = [{"debate": d["debate"], "gov": [name2a[x] for x in d["gov"]], "opp": [name2a[x] for x in d["opp"]],
                "judge": name2a.get(d["judge"]), "winner": {"Gov": 1, "Opp": -1}.get(d.get("winner"), 0),
                "t_teams": sec(d["t_teams"]), "t_first_speech": sec(d["t_first_speech"]), "t_verdict": sec(d["t_verdict"]),
                "t_post_end": sec(d["_t_post_end"])} for d in deb]
    lab_of = dict(zip(st_pl["agent"].to_list(), st_pl["lab"].to_list()))
    return st_pl, C.to_np(st_pl), X, debates, lab_of, W


def magnetizations(X, st, debates, phase, Xc):
    """Uniform vs staggered magnetisation (agent-centred unit spins, NOT debate-centred) and topic alignment."""
    out = []
    mot = np.load(DATA / "motions.npz")
    W = load_whitener("I", X.shape[1])
    topic = {int(d): L.unit(W(e[0][None])[0]) for d, e in zip(mot["debates"], mot["emb"])}
    for deb in debates:
        members = deb["gov"] + deb["opp"]
        m = (st["debate"] == deb["debate"]) & (st["phase"] == phase) & np.isin(st["agent"], members)
        ids, V, _ = L.window_means(Xc, st["agent"], m, 2)
        if len(ids) < 4:
            continue
        eps = np.array([C.team_of(deb, a) for a in ids])
        if (eps == 1).sum() < 1 or (eps == -1).sum() < 1:
            continue
        S = L.unit(V)
        mA, mB = S[eps == 1].mean(0), S[eps == -1].mean(0)
        Mu, Ms = (mA + mB) / 2, (mA - mB) / 2
        null_ms = [np.linalg.norm((S[e == 1].mean(0) - S[e == -1].mean(0)) / 2)
                   for e in L.partitions(len(eps), int((eps == 1).sum()))]
        g = topic.get(deb["debate"])
        out.append({"debate": deb["debate"], "phase": phase, "abs_Mu": float(np.linalg.norm(Mu)), "abs_Ms": float(np.linalg.norm(Ms)),
                    "abs_Ms_null_mean": float(np.mean(null_ms)), "Mu_topic": float(Mu @ g) if g is not None else np.nan,
                    "canting_cos": float(L.unit(Mu) @ L.unit(Ms))})
    return out


def time_course(X, st, debates, Xc, bin_s=300, lo=-1800, hi=1200):
    """sigma(tau) around the verdict: LOAO frame and axis from the other debaters' debate-phase vectors."""
    rows = []
    for deb in debates:
        members = deb["gov"] + deb["opp"]
        md = (st["debate"] == deb["debate"]) & (st["phase"] == "deb") & np.isin(st["agent"], members)
        ids, V, _ = L.window_means(Xc, st["agent"], md, 2)
        if len(ids) < 4:
            continue
        eps = np.array([C.team_of(deb, a) for a in ids])
        frames = {a: L.loao_frame(V, eps, i) for i, a in enumerate(ids)}
        epsd = dict(zip(ids, eps))
        tau = st["ts"] - deb["t_verdict"]
        inwin = (st["debate"] == deb["debate"]) & np.isin(st["phase"], ["deb", "post"]) & np.isin(st["agent"], list(ids))
        for b0 in range(lo, hi, bin_s):
            mm = inwin & (tau >= b0) & (tau < b0 + bin_s)
            for a in ids:
                r = np.flatnonzero(mm & (st["agent"] == a))
                if len(r) == 0:
                    continue
                c, ax = frames[a]
                s = L.unit(Xc[r].mean(0) - c)
                rows.append({"debate": deb["debate"], "bin": b0 + bin_s / 2, "agent": int(a),
                             "sigma": float(epsd[a] * (s @ ax)),
                             "winner_side": int(epsd[a] * deb["winner"])})
    return rows


def run(dim=32, masked=True, min_n=2, weights=None, phase="deb", full=True):
    st_pl, st, X, debates, lab_of, W = load(dim, masked)
    Xc = L.agent_center(X, st["agent"])
    wts = st_pl["length"].to_numpy().clip(1, 1500).astype(float) if weights == "length" else None
    Wd = C.build_windows(X, st, debates, phase, min_n=min_n, weights=wts, Xc=Xc)
    res = {"config": {"dim": dim, "masked": masked, "min_n": min_n, "weights": weights, "phase": phase},
           "static": C.static_tests(Wd, 50000, RNG)}
    res["static"]["delta_ci"] = C.ci_debates(Wd, "delta", 5000, RNG)
    res["static"]["ms_ci"] = C.ci_debates(Wd, "ms", 5000, RNG)
    if not full:
        return res
    nd, nm = L.rotation_null([{"agents": w["agents"], "V": w["V"], "eps": w["eps"]} for w in Wd], 2000, RNG)
    res["rotation_null"] = {"p_delta": L.p_upper(res["static"]["delta"], nd), "p_ms": L.p_upper(res["static"]["ms"], nm),
                            "delta_q95": float(np.quantile(nd, 0.95)), "ms_q95": float(np.quantile(nm, 0.95))}
    res["generic"] = C.generic_tests(Wd, 50000, RNG)
    # a-priori text axes: pro-minus-con templates of the motion; and with the cross-debate template mean removed
    mot = np.load(DATA / "motions.npz")
    ax_raw = {int(d): W(e[1][None])[0] - W(e[2][None])[0] for d, e in zip(mot["debates"], mot["emb"])}
    gmean = np.mean([L.unit(v) for v in ax_raw.values()], axis=0)
    ax_spec = {d: L.unit(v) - (L.unit(v) @ L.unit(gmean)) * L.unit(gmean) for d, v in ax_raw.items()}
    res["text_axis"] = {"raw": C.text_axis_tests(Wd, ax_raw, 50000, RNG), "motion_specific": C.text_axis_tests(Wd, ax_spec, 50000, RNG)}
    # family confound
    res["family"] = {"lab_overlap": C.lab_overlap(debates, lab_of),
                     "no_agent_centre": C.static_tests(C.build_windows(X, st, debates, phase, agent_centre=False, min_n=min_n), 50000, RNG),
                     "pair_regression_centred": C.pair_regression(Wd, lab_of, 5000, RNG),
                     "pair_fixed_effects": C.pair_fe_regression(Wd, 5000, RNG),
                     "pair_fixed_effects_uncentred": C.pair_fe_regression(
                         C.build_windows(X, st, debates, phase, agent_centre=False, min_n=min_n), 5000, RNG),
                     "pair_regression_uncentred": C.pair_regression(C.build_windows(X, st, debates, phase, agent_centre=False, min_n=min_n),
                                                                    lab_of, 5000, RNG)}
    lab_lbl = {}
    for deb in debates:
        ag = deb["gov"] + deb["opp"]
        lbl = {a: (1 if lab_of[a] == "Anthropic" else -1) for a in ag}
        if 0 < sum(v == 1 for v in lbl.values()) < len(ag):
            lab_lbl[deb["debate"]] = lbl
    res["family"]["lab_partition_placebo_centred"] = C.static_tests(C.build_windows(X, st, debates, phase, Xc=Xc, label_override=lab_lbl), 50000, RNG)
    res["family"]["lab_partition_placebo_uncentred"] = C.static_tests(
        C.build_windows(X, st, debates, phase, agent_centre=False, label_override=lab_lbl), 50000, RNG)
    # verdict / judge field
    vt = C.verdict_tests(X, st, debates, Xc=Xc, n_perm=5000, rng=RNG)
    res["verdict"] = {k: v for k, v in vt.items() if k != "rows"}
    verdict_rows = {}
    for deb in debates:
        r = np.flatnonzero((st_pl["is_verdict"].to_numpy()) & (st["debate"] == deb["debate"]))
        if len(r):
            verdict_rows[deb["debate"]] = int(r[0])
    res["judge_check"] = C.judge_check(Xc, st, debates, verdict_rows)
    # staggered susceptibility from fluctuations
    ser = C.fluct_series(X, st, debates, 180, Xc=Xc)
    res["fluct"] = C.fluct_tests(ser, 20000, RNG)
    res["fluct"]["series"] = [[a.tolist(), b.tolist()] for a, b in ser]
    res["fluct_120s"] = C.fluct_tests(C.fluct_series(X, st, debates, 120, Xc=Xc), 20000, RNG)
    res["fluct_300s"] = C.fluct_tests(C.fluct_series(X, st, debates, 300, Xc=Xc), 20000, RNG)
    # magnetisations by phase, and the static test in the pre and post phases
    res["magnetization"] = sum([magnetizations(X, st, debates, ph, Xc) for ph in ("pre", "deb", "post")], [])
    res["phases"] = {ph: C.static_tests(C.build_windows(X, st, debates, ph, min_n=1 if ph != "deb" else min_n, Xc=Xc), 50000, RNG)
                     for ph in ("pre", "post")}
    res["time_course"] = time_course(X, st, debates, Xc)
    res["_verdict_rows"] = vt.get("rows", [])
    return res


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    main_res = run()
    robust = {}
    for name, kw in {"dim16": {"dim": 16}, "dim64": {"dim": 64}, "unmasked": {"masked": False},
                     "length_weighted": {"weights": "length"}, "min_n1": {"min_n": 1}, "min_n3": {"min_n": 3}}.items():
        r = run(full=False, **kw)
        if name == "unmasked":
            r_full = run(masked=False)
            r["generic"] = r_full["generic"]
        robust[name] = r
        print(name, {k: r["static"][k] for k in ("delta", "p_delta", "ms", "p_ms", "recovered", "p_recovered")}, flush=True)
    st_pl, st, X, debates, lab_of, W = load()
    Wd7 = [w for w in C.build_windows(X, st, debates, "deb", Xc=L.agent_center(X, st["agent"])) if w["debate"] != 7]
    robust["drop_debate7"] = {"static": C.static_tests(Wd7, 50000, RNG)}
    print("drop7", {k: robust["drop_debate7"]["static"][k] for k in ("delta", "p_delta", "ms", "p_ms", "recovered", "p_recovered")})
    main_res["robustness"] = robust
    vrows = main_res.pop("_verdict_rows")
    pl.DataFrame([{k: v for k, v in r.items() if k != "delta_all"} for r in main_res["static"]["per_debate"]]).write_csv(DATA / "per_debate.csv")
    if vrows:
        pl.DataFrame(vrows).write_csv(DATA / "verdict_rows.csv")
    tc = main_res.pop("time_course")
    if tc:
        pl.DataFrame(tc).write_csv(DATA / "time_course.csv")
    (DATA / "results.json").write_text(json.dumps(main_res, indent=1, default=float))
    s = main_res["static"]
    print(json.dumps({k: s[k] for k in ("n_debates", "delta", "delta_ci", "p_delta", "ms", "ms_ci", "p_ms", "recovered",
                                         "recovered_expected_null", "p_recovered", "mean_rank_pct")}, default=float))
    for k in ("rotation_null", "generic", "text_axis", "verdict", "judge_check", "fluct", "fluct_120s", "fluct_300s"):
        print(k, json.dumps(main_res[k], default=float)[:900])
    print("family", json.dumps({k: (v if not isinstance(v, dict) or "per_debate" not in v else {kk: vv for kk, vv in v.items() if kk != "per_debate"})
                                for k, v in main_res["family"].items()}, default=float)[:1500])
    print("phases", json.dumps({k: {kk: v[kk] for kk in ("n_debates", "delta", "p_delta", "ms", "p_ms", "recovered", "p_recovered")}
                                for k, v in main_res["phases"].items() if v.get("n_debates")}, default=float))


if __name__ == "__main__":
    main()
