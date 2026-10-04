"""H95 exploratory round 1: slack S vs kickoff specificity x across the nine regime-III kickoff units (replication)
and the room natives N1 (G44) and N2 (G38).

  uv run python hypotheses/H95-slack-specificity-gauge/analysis/run.py
Writes data/processed/H95-slack-specificity-gauge/<G..>/results.json, results/across.json, per-period estimates and
figures/.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h95lib as L  # noqa: E402
import build as B  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as EST  # noqa: E402

RNG = np.random.default_rng(20261095)
NBOOT = 200
NPERM_S0 = 200
UNITS = [(37, None), (38, None), (39, None), (40, None), (41, None), (42, None), (44, "best"), (44, "rest"), (51, None)]
H54_KICK = L.ROOT / "data/processed/H54-kickoff-quench-target/kickoffs.parquet"
ROOM_ID = {"best": 2, "rest": 3}


def s_text(goal: int, room: str | None) -> float:
    k = pl.read_parquet(H54_KICK, columns=["goal_no", "room", "S_text"]).filter(pl.col("goal_no") == goal)
    if room is not None:
        r = k.filter(pl.col("room") == ROOM_ID[room])
        if r.height:
            return float(r["S_text"][0])
    r = k.filter(pl.col("room").is_null())
    return float(r["S_text"][0]) if r.height else np.nan


def unit_result(goal: int, room: str | None, agents=None, clk=None, tag=None) -> dict:
    clk = B.clock(goal) if clk is None else clk
    H = B.horizon(clk)
    E = B.ensemble(goal, "null", H, clk, agents)
    repos = B.repo_list(goal, clk)
    named = B.named_codes(goal, repos)
    named_s = B.named_codes(goal, repos, strict=True)
    s = L.settle_stats(E)
    bt = L.bootstrap(E, NBOOT, RNG)
    first_len = float(clk.filter(~pl.col("pre")).sort("off_h")["len_h"][0])
    x = L.specificity(E, named)
    c, top = L.concentration(E)
    s0 = [L.settle_stats(L.permuted_ensemble(E, RNG))["S_e"] for _ in range(NPERM_S0)]
    S0 = float(np.nanmedian(s0)) if np.isfinite(s0).any() else np.nan
    S12 = np.nan
    if len(E.agents) >= 13:
        v = [L.settle_stats(L.subsample(E, RNG.choice(len(E.agents), 12, replace=False)))["S_e"] for _ in range(50)]
        S12 = float(np.nanmedian(v))
    pre = None
    try:
        Ep = B.ensemble(goal, "pre", H, clk, agents)
        sp = L.settle_stats(Ep)
        pre = {k: sp[k] for k in ("T_e", "W_e", "A_e", "S_e")}
    except RuntimeError as e:
        pre = {"why": str(e)}
    out = {"goal": goal, "room": room, "tag": tag, "H": H, "N": len(E.agents), "n_named_repos": len(named),
           "x": x, "x_strict": L.specificity(E, named_s), "x_day1": L.specificity(E, named, first_len),
           "x_agentw": L.specificity(E, named, agent_weighted=True), "conc": c, "top_share": top,
           "n_day1_commits": int(len(L.day1_shares(E))), "S_text": s_text(goal, room),
           **{k: s[k] for k in ("T_e", "W_e", "A_e", "S_e", "R_e", "T_90", "S_90", "A_ss", "D0", "Df")},
           "S_ci": bt["S_e"], "T_ci": bt["T_e"], "S_cens": bt["S_e_cens"], "S0": S0,
           "S_norm": s["S_e"] / S0 if (S0 and np.isfinite(S0) and S0 > 0) else np.nan, "S12": S12, "W_pre": pre,
           "curve_D": s["curve_D"]}
    out["verdict"] = verdict(out)
    return out


def verdict(r) -> str:
    S, x = r["S_e"], r["x"]
    if r["N"] < 4 or not np.isfinite(S) or not np.isfinite(x):
        return "n/a"
    if (x >= 0.5 and S <= 2) or (x < 0.5 and S >= 3):
        return "supported"
    if (x >= 0.5 and S >= 3) or (x < 0.3 and S <= 2):
        return "failed"
    return "mixed"


def exact_spearman(x, y) -> tuple[float, float, int]:
    """Spearman rho and one-sided (negative-tail) exact permutation p over all n! orderings (n <= 9)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    if n < 3:
        return np.nan, np.nan, n
    rx, ry = rankdata(x), rankdata(y)
    rx = (rx - rx.mean()) / np.sqrt(((rx - rx.mean()) ** 2).sum())
    ryc = ry - ry.mean()
    ryc = ryc / np.sqrt((ryc ** 2).sum())
    r0 = float(rx @ ryc)
    P = np.array(list(itertools.permutations(range(n))), dtype=np.int8)
    rp = ryc[P] @ rx
    return r0, float((rp <= r0 + 1e-12).mean()), n


def partial_spearman(x, y, z) -> float:
    x, y, z = (np.asarray(v, float) for v in (x, y, z))
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    rx, ry, rz = rankdata(x[ok]), rankdata(y[ok]), rankdata(z[ok])

    def res(a, b):
        A = np.c_[np.ones(len(b)), b]
        return a - A @ np.linalg.lstsq(A, a, rcond=None)[0]
    ex, ey = res(rx, rz), res(ry, rz)
    return float(np.corrcoef(ex, ey)[0, 1])


def gauge_band(N: int, x: float) -> tuple[float, float, float] | None:
    f = L.OUTD / "synthetic/gauge.parquet"
    if not f.exists() or not np.isfinite(x):
        return None
    g = pl.read_parquet(f)
    Nn = min([4, 12, 15, 27], key=lambda v: abs(v - N))
    g = g.filter(pl.col("N") == Nn)
    m = g.group_by("q").agg(pl.col("x").median().alias("xm"), pl.col("S_e").quantile(0.1).alias("lo"),
                            pl.col("S_e").quantile(0.9).alias("hi")).sort("q")
    k = int(np.argmin(np.abs(m["xm"].to_numpy() - x)))
    return float(m["q"][k]), float(m["lo"][k]), float(m["hi"][k])


def native_g44(res_units: dict) -> dict:
    b, r = res_units["G44best"], res_units["G44rest"]
    out = {"x_best": b["x"], "x_rest": r["x"], "dx": b["x"] - r["x"], "S_best": b["S_e"], "S_rest": r["S_e"],
           "S_ratio_rest_best": r["S_e"] / b["S_e"] if b["S_e"] else np.nan,
           "S0_best": b["S0"], "S0_rest": r["S0"], "N_best": b["N"], "N_rest": r["N"]}
    ok = np.isfinite(out["dx"]) and out["dx"] >= 0.3 and np.isfinite(out["S_ratio_rest_best"]) and out["S_ratio_rest_best"] >= 2
    some = (np.isfinite(out["dx"]) and out["dx"] >= 0.3) or (np.isfinite(out["S_ratio_rest_best"]) and out["S_ratio_rest_best"] >= 2)
    out["verdict"] = "supported" if ok else ("mixed" if some else "failed")
    return out


def native_g38() -> dict:
    clk = B.clock(38)
    H = B.horizon(clk)
    committing = set(B.ensemble(38, "null", H, clk).agents)
    rooms = {k: [a for a in v if a in committing] for k, v in B.rooms_38(clk).items()}
    rooms = {k: v for k, v in rooms.items() if len(v) >= 3}
    big = sorted(rooms, key=lambda k: -len(rooms[k]))[:2]
    out = {"rooms": {int(k): len(v) for k, v in rooms.items()}, "room_rule": "committing agents, majority room in the first 4 active h"}
    rr = {}
    for k in big:
        rr[int(k)] = unit_result(38, None, rooms[k], clk, tag=f"room{k}")
        rr[int(k)].pop("curve_D", None)
    out["per_room"] = rr
    if len(rr) == 2:
        a, b = list(rr.values())
        hi, lo = (a, b) if a["x"] >= b["x"] else (b, a)
        out["dx"] = hi["x"] - lo["x"]
        out["S_hi_x"], out["S_lo_x"] = hi["S_e"], lo["S_e"]
        out["T_hi_x"], out["T_lo_x"] = hi["T_e"], lo["T_e"]
        ok = out["dx"] >= 0.2 and hi["S_e"] < lo["S_e"] and hi["T_e"] <= lo["T_e"]
        part = hi["S_e"] < lo["S_e"] or hi["T_e"] < lo["T_e"]
        out["verdict"] = "supported" if ok else ("mixed" if part else "failed")
    else:
        out["verdict"] = "n/a"
    return out


def main():
    res = {}
    for g, room in UNITS:
        name = f"G{g:02d}" + (room or "")
        if room is None:
            r = unit_result(g, None, tag=name)
        else:
            r = unit_result(g, room, B.rooms_44()[room], tag=name)
        res[name] = r
        print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()
                     if k in ("N", "H", "x", "x_strict", "conc", "S_e", "T_e", "S0", "S_norm", "S12", "A_ss", "S_text", "verdict")},
              flush=True)
    sens = unit_result(36, None, tag="G36")
    print("G36 (sensitivity)", {k: sens[k] for k in ("N", "x", "S_e", "T_e")}, flush=True)
    names = list(res)
    x = [res[n]["x"] for n in names]
    S = [res[n]["S_e"] for n in names]
    T = [res[n]["T_e"] for n in names]
    Sn = [res[n]["S_norm"] for n in names]
    St = [res[n]["S_text"] for n in names]
    cc = [res[n]["conc"] for n in names]
    nul = L.OUTD / "synthetic/churn_null.parquet"
    q05 = float(pl.read_parquet(nul)["rho_S_x"].quantile(0.05)) if nul.exists() else np.nan
    rS = exact_spearman(x, S)
    across = {"units": names, "rho_S_x": rS, "rho_T_x": exact_spearman(x, T), "rho_Snorm_x": exact_spearman(x, Sn),
              "rho_S_Stext": exact_spearman(St, S), "rho_S_conc": exact_spearman(cc, S),
              "partial_rho_S_x_given_conc": partial_spearman(x, S, cc), "churn_null_q05": q05,
              "rho_S_xstrict": exact_spearman([res[n]["x_strict"] for n in names], S),
              "rho_S_xday1": exact_spearman([res[n]["x_day1"] for n in names], S),
              "rho_S_xagentw": exact_spearman([res[n]["x_agentw"] for n in names], S),
              "rho_S12_x": exact_spearman(x, [res[n]["S12"] if np.isfinite(res[n]["S12"]) else res[n]["S_e"] for n in names]),
              "with_G36": exact_spearman(x + [sens["x"]], S + [sens["S_e"]]) if len(x) < 9 else None,
              "without_G51": exact_spearman([v for n, v in zip(names, x) if n != "G51"], [v for n, v in zip(names, S) if n != "G51"]),
              "G36": {k: sens[k] for k in ("N", "x", "S_e", "T_e", "conc")}}
    band = {}
    for n in names:
        b = gauge_band(res[n]["N"], res[n]["x"])
        if b:
            band[n] = {"q_match": b[0], "S_lo": b[1], "S_hi": b[2], "inside": bool(b[1] <= res[n]["S_e"] <= b[2])}
    across["gauge_band"] = band
    across["n_inside_band"] = int(sum(v["inside"] for v in band.values()))
    p1 = np.isfinite(rS[0]) and rS[0] <= -0.5 and rS[1] < 0.05 and rS[0] < q05
    across["P1"] = "supported" if p1 else ("inconclusive (power 0.29)" if not (np.isfinite(rS[0]) and rS[0] > 0.3) else "failed")
    print("ACROSS", {k: v for k, v in across.items() if k not in ("gauge_band",)}, flush=True)
    nat = {"N1_G44": native_g44(res), "N2_G38": native_g38()}
    print("N1", nat["N1_G44"], flush=True)
    print("N2", {k: v for k, v in nat["N2_G38"].items() if k != "per_room"}, flush=True)
    for n, r in res.items():
        d = L.OUTD / n[:3]
        L.write_json(d / (f"results_{n[3:]}.json" if n[3:] else "results.json"), r)
    L.write_json(L.OUTD / "results" / "across.json", across | {"per_unit": {n: {k: v for k, v in r.items() if k != "curve_D"}
                                                                             for n, r in res.items()}})
    L.write_json(L.OUTD / "results" / "natives.json", nat)
    rows = []
    for n, r in res.items():
        g = r["goal"]
        unit = (str(g) if g in (37, 39, 40, 41) else f"G{g:02d}") if r["room"] is None else f"local:44{r['room']}"
        if g == 42:
            unit = "G42"
        base = {"goal_no": g, "period_unit": unit, "unit_local": n if r["room"] else None, "n": float(r["N"]),
                "n_kind": "agents", "role": "replication", "status": "ok",
                "source": f"data/processed/H95-slack-specificity-gauge/G{g:02d}/" + (f"results_{r['room']}.json" if r["room"] else "results.json")}
        rows.append(base | {"statistic": "kickoff_specificity_x_day1_named_share", "channel": "work_commits",
                            "estimate": float(r["x"]), "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                            "method": "share of first-4-active-hour agent-work commits on repos whose artifacts H54 flags named",
                            "null": None})
        rows.append(base | {"statistic": "speed_limit_slack_S_e", "channel": "work_commits:null",
                            "estimate": float(r["S_e"]), "ci_lo": r["S_ci"][0], "ci_hi": r["S_ci"][1], "ci_level": 0.95,
                            "ci_kind": "percentile", "method": "H75 slack A T_e / W (W_null start), agent bootstrap B=200",
                            "null": f"within-agent label permutation S0={r['S0']:.2f}"})
    EST.write_estimates([r for r in rows if np.isfinite(r["estimate"])], hypothesis="H95")
    nrows = [{"goal_no": 44, "period_unit": "G44", "statistic": "room_slack_ratio_rest_over_best", "channel": "work_commits:null",
              "estimate": float(nat["N1_G44"]["S_ratio_rest_best"]), "ci_lo": None, "ci_hi": None, "ci_kind": "none",
              "n": float(nat["N1_G44"]["N_best"] + nat["N1_G44"]["N_rest"]), "n_kind": "agents", "role": "native",
              "method": "H75 slack per room (DQ6 room assignment); ratio #rest/#best",
              "null": f"x_best - x_rest = {nat['N1_G44']['dx']:.2f}", "status": "ok",
              "source": "data/processed/H95-slack-specificity-gauge/results/natives.json"}]
    if "dx" in nat["N2_G38"]:
        nrows.append({"goal_no": 38, "period_unit": "G38", "statistic": "room_slack_hi_x_minus_lo_x",
                      "channel": "work_commits:null", "estimate": float(nat["N2_G38"]["S_hi_x"] - nat["N2_G38"]["S_lo_x"]),
                      "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": float(sum(nat["N2_G38"]["rooms"].values())),
                      "n_kind": "agents", "role": "native", "method": "H75 slack per #38 room (rooms_timeline, first 4 h)",
                      "null": f"dx = {nat['N2_G38']['dx']:.2f}", "status": "ok",
                      "source": "data/processed/H95-slack-specificity-gauge/results/natives.json"})
    EST.write_estimates([r for r in nrows if np.isfinite(r["estimate"])], hypothesis="H95")


if __name__ == "__main__":
    main()
