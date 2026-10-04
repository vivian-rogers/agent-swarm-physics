"""H114 summary: prediction scoring, period pools, natives (NE42, G51 assigned pairs), estimates rows, figures.

Usage: uv run python hypotheses/H114-griffiths-phase-pairs/analysis/summarize.py [--no-estimates]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import mannwhitneyu, spearmanr, fisher_exact

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h114lib as L  # noqa: E402

ROOT = L.ROOT
RES = L.OUT / "results"
FIG = ROOT / "hypotheses/H114-griffiths-phase-pairs/figures"
SH = ROOT / "data/processed/shared"


def se_from_ci(lo, hi):
    return (hi - lo) / (2 * 1.96)


def frac(mask):
    mask = [bool(x) for x in mask if x is not None]
    return [sum(mask), len(mask), (sum(mask) / len(mask)) if mask else float("nan")]


def load():
    d = pl.read_parquet(RES / "units.parquet")
    d = d.with_columns(((pl.col("n_links") >= 100) & (pl.col("n_tail") >= 30) & pl.col("dh").is_finite())
                       .alias("usable"))
    return d


def score(d: pl.DataFrame, P: pl.DataFrame) -> dict:
    S = {}
    u = d.filter(pl.col("usable"))
    S["n_units"], S["n_usable"] = d.height, u.height
    S["P1"] = frac((u["dh_lo"] > 0).to_list())
    S["P1_point"] = frac((u["dh"] > 0).to_list())
    S["P1_by_regime"] = {r: frac((u.filter(pl.col("regime") == r)["dh_lo"] > 0).to_list()) for r in ("I", "II", "III")}
    S["P2"] = frac((u["delta_h_lo"] > 0).to_list())
    S["P2_by_regime"] = {r: frac((u.filter(pl.col("regime") == r)["delta_h_lo"] > 0).to_list()) for r in ("I", "II", "III")}
    S["P3"] = frac((d.filter(pl.col("n_links") >= 100)["n_strong"] > 0).to_list())
    S["strong_total"] = int(d["n_strong"].sum())
    S["pingpong_total"] = int(d["n_pingpong"].sum())
    ws = u.filter(pl.col("n_strong") > 0)
    ok = (ws["dh_cut_lo"] <= 0) & (ws["dh_cut_hi"] >= 0) & (ws["dh_cut"] < ws["dh_rand_q05"])
    S["P4"] = {"n_units_with_strong": ws.height, "carry": frac(ok.to_list()),
               "below_rand_q05": frac((ws["dh_cut"] < ws["dh_rand_q05"]).to_list()),
               "cut_ci_incl0": frac(((ws["dh_cut_lo"] <= 0) & (ws["dh_cut_hi"] >= 0)).to_list()),
               "median_strong_link_share": float(ws["strong_link_share"].median()) if ws.height else None}
    S["P5"] = {"M1_under": frac((u["h_tail_lo"] > u["h_tail_M1"]).to_list()),
               "M2_closer": frac(((u["h_tail"] - u["h_tail_M2"]).abs() < (u["h_tail"] - u["h_tail_M1"]).abs()).to_list()),
               "median_M2_minus_M1": float((u["h_tail_M2"] - u["h_tail_M1"]).median())}
    S["P6"] = frac((u["h_tail_lo"] > u["h_tail_M2"]).to_list())
    rho, p = spearmanr(u["dh"].to_numpy(), u["strong_link_share"].fill_null(0).to_numpy())
    S["P7"] = {"rho_dh_share": float(rho), "p": float(p), "n": u.height,
               "alpha_identifiable": False, "median_alpha": float(u["alpha"].median()),
               "vuong_pl_share": frac((u["vuong_z"] > 1.645).to_list())}
    # naming and family
    ros = pl.read_parquet(SH / "roster.parquet").select("agent", "lab")
    Pf = (P.join(ros.rename({"agent": "reader", "lab": "lab_r"}).with_columns(pl.col("reader").cast(pl.Int16)), on="reader", how="left")
          .join(ros.rename({"agent": "author", "lab": "lab_a"}).with_columns(pl.col("author").cast(pl.Int16)), on="author", how="left")
          .with_columns((pl.col("lab_r") == pl.col("lab_a")).alias("same_lab")))
    el = Pf.filter(pl.col("R") >= L.R_MIN)
    st = el.filter(pl.col("strong"))
    ot = el.filter(~pl.col("strong"))
    nm_s = st["L_named"].sum() / max(st["L"].sum(), 1)
    nm_o = ot["L_named"].sum() / max(ot["L"].sum(), 1)
    a, b = int(st["same_lab"].sum()), int(st.height - st["same_lab"].sum())
    c, dd = int(ot["same_lab"].sum()), int(ot.height - ot["same_lab"].sum())
    orr, pf = fisher_exact([[a, b], [c, dd]]) if st.height else (float("nan"), float("nan"))
    S["P8"] = {"named_share_strong": float(nm_s), "named_share_other": float(nm_o),
               "naming_ratio": float(nm_s / nm_o) if nm_o > 0 else None, "family_OR": float(orr), "family_p": float(pf),
               "n_strong_pairs": st.height, "n_eligible_pairs": el.height}
    # persistence of strong pairs across periods
    sp = (P.filter(pl.col("strong")).join(d.select("unit_id", "goal_no"), on="unit_id")
          .group_by("reader", "author").agg(pl.col("goal_no").n_unique().alias("n_periods")))
    S["persistence"] = {"n_strong_directed": sp.height, "in_2plus_periods": int((sp["n_periods"] >= 2).sum())}
    S["variants"] = {}
    for v in ("untrim", "p08", "nohuman"):
        f = RES / f"units_{v}.parquet"
        if f.exists():
            x = pl.read_parquet(f).filter((pl.col("n_links") >= 100) & (pl.col("n_tail") >= 30) & pl.col("dh").is_finite())
            S["variants"][v] = {"P1": frac((x["dh_lo"] > 0).to_list()), "P2": frac((x["delta_h_lo"] > 0).to_list()),
                                "median_dh": float(x["dh"].median()), "median_delta_h": float(x["delta_h"].median()),
                                "units_with_strong": int((x["n_strong"] > 0).sum())}
    S["medians"] = {r: {"g_rep": float(u.filter(pl.col("regime") == r)["g_rep"].median()),
                        "h_1": float(u.filter(pl.col("regime") == r)["h_1"].median()),
                        "h_tail": float(u.filter(pl.col("regime") == r)["h_tail"].median()),
                        "h_tail_M1": float(u.filter(pl.col("regime") == r)["h_tail_M1"].median()),
                        "dh": float(u.filter(pl.col("regime") == r)["dh"].median()),
                        "delta_h": float(u.filter(pl.col("regime") == r)["delta_h"].median()),
                        "g_pair_max": float(u.filter(pl.col("regime") == r)["g_pair_max"].median()),
                        "n": u.filter(pl.col("regime") == r).height} for r in ("I", "II", "III")}
    # momentum: h_1 vs g_rep
    S["momentum"] = {"h1_gt_grep": frac((u["h_1"] > u["g_rep"]).to_list()),
                     "median_h1_minus_grep": float((u["h_1"] - u["g_rep"]).median())}
    return S


def periods(d: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for (g,), grp in d.sort("unit_id").group_by(["goal_no"], maintain_order=True):
        ok = grp.filter(pl.col("usable"))
        if ok.height:
            se = se_from_ci(ok["dh_lo"].to_numpy(), ok["dh_hi"].to_numpy())
            mu, lo, hi, tau2 = L.re_pool(ok["dh"].to_numpy(), se)
            se2 = se_from_ci(ok["delta_h_lo"].to_numpy(), ok["delta_h_hi"].to_numpy())
            mu2, lo2, hi2, _ = L.re_pool(ok["delta_h"].to_numpy(), se2)
        else:
            mu = lo = hi = mu2 = lo2 = hi2 = float("nan")
        n_strong = int(grp["n_strong"].sum())
        ws = ok.filter(pl.col("n_strong") > 0)
        n_carry = int(((ws["dh_cut_lo"] <= 0) & (ws["dh_cut_hi"] >= 0) & (ws["dh_cut"] < ws["dh_rand_q05"])).sum()) if ws.height else 0
        carry = bool(ws.height and n_carry >= ws.height / 2)     # at least half of the units that have strong pairs
        if not ok.height:
            v = "descriptive"
        elif not (lo > 0):
            v = "failed"
        elif n_strong == 0:
            v = "failed"
        elif carry:
            v = "supported"
        else:
            v = "mixed"
        rows.append({"goal_no": int(g), "regime": grp["regime"][0], "units": ",".join(grp["unit_id"].to_list()),
                     "n_links": int(grp["n_links"].sum()), "dh": mu, "dh_lo": lo, "dh_hi": hi, "delta_h": mu2,
                     "delta_h_lo": lo2, "delta_h_hi": hi2, "g_rep": float(grp["g_rep"].drop_nans().mean()),
                     "n_strong": n_strong, "n_units_strong": ws.height, "n_units_carry": n_carry, "carry": carry,
                     "verdict": v})
    return pl.DataFrame(rows)


def natives(d: pl.DataFrame, P: pl.DataFrame) -> dict:
    N = {}
    get = lambda u, c: d.filter(pl.col("unit_id") == u)[c][0]  # noqa: E731
    o = {u: {c: get(u, c) for c in ("dh", "dh_lo", "dh_hi", "delta_h", "strong_link_share", "n_strong", "g_rep",
                                    "h_tail", "g_pair_max", "g_pair_med")} for u in ("39", "40", "41")}
    side_sh = (o["39"]["strong_link_share"] + o["41"]["strong_link_share"]) / 2
    side_dh = (o["39"]["dh"] + o["41"]["dh"]) / 2
    N["NE42"] = {"units": o, "N42a": o["40"]["strong_link_share"] < side_sh, "N42b": o["40"]["dh"] < side_dh,
                 "share_side": side_sh, "dh_side": side_dh}
    gt = (pl.read_parquet(SH / "ground_truth_labels.parquet")
          .filter((pl.col("goal_no") == 51) & ~pl.col("holdout") & pl.col("label_kind").is_in(["rival_pair", "opposed_pair"]))
          .select("agent_a", "agent_b", "label_kind").drop_nulls())
    pairs = set()
    for a_, b_, _ in gt.iter_rows():
        pairs.add((int(a_), int(b_)))
        pairs.add((int(b_), int(a_)))
    p51 = P.filter(pl.col("unit_id").str.starts_with("51") & (pl.col("R") >= L.R_MIN))
    p51 = p51.with_columns(pl.struct("reader", "author").map_elements(lambda s: (s["reader"], s["author"]) in pairs,
                                                                     return_dtype=pl.Boolean).alias("assigned"))
    a = int((p51["assigned"] & p51["strong"]).sum())
    b = int((p51["assigned"] & ~p51["strong"]).sum())
    c = int((~p51["assigned"] & p51["strong"]).sum())
    dd = int((~p51["assigned"] & ~p51["strong"]).sum())
    orr, pf = fisher_exact([[a, b], [c, dd]])
    ga = p51.filter(pl.col("assigned"))["g"].to_numpy()
    go = p51.filter(~pl.col("assigned"))["g"].to_numpy()
    mw = mannwhitneyu(ga, go, alternative="greater") if len(ga) and len(go) else None
    N["G51"] = {"n_assigned_directed_rows": int(p51["assigned"].sum()), "table": [[a, b], [c, dd]], "OR": float(orr),
                "fisher_p": float(pf), "median_g_assigned": float(np.median(ga)) if len(ga) else None,
                "median_g_other": float(np.median(go)) if len(go) else None,
                "mw_p_greater": float(mw.pvalue) if mw else None, "G51a": bool(orr >= 2 and a > 0),
                "G51b": bool(mw is not None and mw.pvalue < 0.05)}
    return N


def figures(d: pl.DataFrame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    u = d.filter(pl.col("usable"))
    col = {"I": "#86b6ef", "II": "#fab219", "III": "#1c5cab"}
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for reg in ("I", "III"):
        x = u.filter(pl.col("regime") == reg)
        H = np.array([json.loads(h)[:9] for h in x["hazard"].to_list()], float)
        med = np.nanmedian(H, 0)
        q1, q3 = np.nanpercentile(H, 25, 0), np.nanpercentile(H, 75, 0)
        dgr = np.arange(len(med))
        ax[0].plot(dgr, med, "o-", color=col[reg], ms=3, label=f"regime {reg}: observed h(d)")
        ax[0].fill_between(dgr, q1, q3, color=col[reg], alpha=0.2)
        ax[0].axhline(float(x["g_rep"].median()), color=col[reg], ls="--", lw=0.8)
        ax[0].axhline(float(x["h_tail_M1"].median()), color=col[reg], ls=":", lw=0.9)
    ax[0].set_xlabel("reply depth d")
    ax[0].set_ylabel("continuation hazard h(d)")
    ax[0].set_ylim(0, 1)
    ax[0].plot([], [], "k--", lw=0.8, label="geometric (g_rep)")
    ax[0].plot([], [], "k:", lw=0.9, label="M1 rank-1 heterogeneity")
    ax[0].legend(fontsize=6, frameon=False, loc="lower right")
    for reg in ("I", "II", "III"):
        x = u.filter(pl.col("regime") == reg)
        ax[1].errorbar(x["dh"], x["delta_h"], xerr=[x["dh"] - x["dh_lo"], x["dh_hi"] - x["dh"]],
                       yerr=[x["delta_h"] - x["delta_h_lo"], x["delta_h_hi"] - x["delta_h"]], fmt="o", ms=3,
                       color=col[reg], alpha=0.75, lw=0.5, label=f"regime {reg}")
    ax[1].axhline(0, color="k", lw=0.6)
    ax[1].axvline(0, color="k", lw=0.6)
    ax[1].set_xlabel(r"tail excess $\Delta h = h_{\rm tail} - g_{\rm rep}$")
    ax[1].set_ylabel(r"Griffiths rise $\delta h = h_{\rm tail} - h(1)$")
    ax[1].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs_col.pdf")
    fig.savefig(FIG / "summary_obs_col.png", dpi=160)
    s = pl.read_parquet(L.OUT / "synthetic/runs.parquet")
    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    wl = ["W0", "W1", "W2", "W2s", "W3"]
    lab = {"W0": "uniform", "W1": "agent\nhetero.", "W2": "pairs\ng≈0.5", "W2s": "pairs\ng≈0.8", "W3": "thread\nmomentum"}
    for k, w in enumerate(wl):
        x = s.filter(pl.col("world") == w)
        jit = np.random.default_rng(k).uniform(-0.15, 0.15, x.height)
        ax.scatter(k + jit - 0.12, x["dh"], s=5, color="#1c5cab", alpha=0.6)
        ax.scatter(k + jit + 0.12, x["delta_h"], s=5, color="#d03b3b", alpha=0.6)
    ax.scatter([], [], color="#1c5cab", s=8, label=r"$\Delta h$ (tail excess)")
    ax.scatter([], [], color="#d03b3b", s=8, label=r"$\delta h$ (rise)")
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xticks(range(len(wl)))
    ax.set_xticklabels([lab[w] for w in wl], fontsize=6.5)
    ax.legend(fontsize=6.5, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_col.pdf")
    fig.savefig(FIG / "synthetic_col.png", dpi=160)


def estimates(d: pl.DataFrame, N: dict):
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import estimates as E
    rows = []
    src = "data/processed/H114-griffiths-phase-pairs/results/units.parquet"
    for r in d.iter_rows(named=True):
        if not (r["dh"] is not None and math.isfinite(r["dh"])):
            continue
        base = dict(period_unit=r["unit_id"], goal_no=r["goal_no"], n=float(r["n_msgs_win"]),
                    n_kind="agent messages in window", role="replication", ci_level=0.95, ci_kind="percentile",
                    first_day=r["first_day"], last_day=r["last_day"], source=src)
        rows.append({**base, "statistic": "reply_tail_excess", "channel": "reply_dq2", "estimate": r["dh"],
                     "ci_lo": r["dh_lo"], "ci_hi": r["dh_hi"],
                     "method": "h_tail(d>=4) - g_rep on DQ2 parent depth; day/hour-block bootstrap",
                     "null": "geometric at g_rep (M0); M1 rank-1 heterogeneity reported"})
        rows.append({**base, "statistic": "reply_griffiths_rise", "channel": "reply_dq2", "estimate": r["delta_h"],
                     "ci_lo": r["delta_h_lo"], "ci_hi": r["delta_h_hi"], "method": "h_tail - h(1)",
                     "null": "0 (first-order momentum or uniform)"})
        rows.append({**base, "statistic": "reply_branching_ratio", "channel": "reply_dq2", "estimate": r["g_rep"],
                     "ci_lo": r["g_rep_lo"], "ci_hi": r["g_rep_hi"], "method": "agent parent links / agent messages",
                     "null": "none"})
        rows.append({**base, "statistic": "strong_pair_count", "channel": "reply_dq2", "estimate": float(r["n_strong"]),
                     "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": float(r["n_pairs_elig"]),
                     "n_kind": "directed pairs with R >= 10",
                     "method": "pairs with Garwood lower bound of L/R > 0.5", "null": "M1 synthetic: <= 0.2 per unit"})
    ne = N["NE42"]
    rows.append(dict(period_unit="40", goal_no=40, statistic="ne42_tail_excess_change", channel="reply_dq2",
                     estimate=ne["units"]["40"]["dh"] - ne["dh_side"], ci_lo=None, ci_hi=None, ci_kind="none", n=3.0,
                     n_kind="units", method="dh(#40) - mean dh(#39, #41)", null="0", role="native",
                     source="data/processed/H114-griffiths-phase-pairs/results/summary.json"))
    g = N["G51"]
    rows.append(dict(period_unit="51g", goal_no=51, statistic="g51_assigned_pair_strong_OR", channel="reply_dq2",
                     estimate=g["OR"] if math.isfinite(g["OR"]) else None, ci_lo=None, ci_hi=None, ci_kind="none",
                     n=float(sum(map(sum, g["table"]))), n_kind="directed pair-unit rows with R >= 10",
                     method="Fisher OR, assigned (rival/opposed) vs other pairs, strong vs not, units 51a-51l",
                     null="OR = 1", role="native", notes="period_unit 51g stands for the #51 non-holdout pool",
                     source="data/processed/H114-griffiths-phase-pairs/results/summary.json"))
    rows = [r for r in rows if r.get("estimate") is not None]
    E.write_estimates(rows, hypothesis="H114")
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    d = load()
    P = pl.read_parquet(RES / "pairs.parquet")
    S = score(d, P)
    Pp = periods(d)
    N = natives(d, P)
    Pp.write_parquet(RES / "periods.parquet")
    (RES / "summary.json").write_text(json.dumps({"scores": S, "natives": N, "periods": Pp.to_dicts()}, indent=1,
                                                 default=lambda o: bool(o) if isinstance(o, np.bool_) else str(o)))
    figures(d)
    if not a.no_estimates:
        print("estimates rows:", estimates(d, N))
    print(json.dumps(S, indent=1, default=str))
    print(json.dumps(N, indent=1, default=str))
    pl.Config.set_tbl_rows(50)
    print(Pp.select("goal_no", "regime", "n_links", "dh", "dh_lo", "dh_hi", "delta_h", "n_strong", "carry", "verdict"))


if __name__ == "__main__":
    main()
