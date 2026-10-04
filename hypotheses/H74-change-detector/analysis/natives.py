"""H74 native tests (NE43, NE45, NE40, NE14) from the scored days, plus the summary figures.
Run after run_detector.py: uv run python hypotheses/H74-change-detector/analysis/natives.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h74lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H74-change-detector"
HYP = ROOT / "hypotheses/H74-change-detector"
SH = ROOT / "data/processed/shared"
CH = ["S", "M", "O", "D", "C", "F"]


def window(sc, cal_days, d0):
    i = cal_days.index(d0)
    w = sc.filter(pl.col("pt_date").is_in(cal_days[max(0, i - 1):i + 2])).sort("pt_date")
    return {c: (float(w[f"z_{c}"].fill_nan(None).max()) if w[f"z_{c}"].fill_nan(None).drop_nulls().len() else None) for c in CH} | {
        "days": w["pt_date"].to_list(), "top": w["top"].to_list(), "feat_D": w["feat_D"].to_list(), "feat_M": w["feat_M"].to_list(),
        "feat_O": w["feat_O"].to_list(), "s_detail": [x[:200] for x in w["s_detail"].to_list()]}


def main():
    sc = pl.read_parquet(OUT / "scores.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("n_agent_events") > 0).sort("pt_date")
    cal_days = cal["pt_date"].to_list()
    ev = pl.read_parquet(OUT / "events.parquet")
    res = {}
    # NE43
    g51 = sc.filter(pl.col("goal_no") == 51).sort("pt_date")
    d51 = g51["pt_date"].to_list()
    excl = set()
    stepdays = ["2026-08-05", "2026-08-21", "2026-07-29", "2026-07-06"] + ev.filter((pl.col("cls") == "roster") & pl.col("day0").is_in(d51))["day0"].to_list()
    for d in stepdays:
        if d in cal_days:
            i = cal_days.index(d)
            excl.update(cal_days[max(0, i - 2):i + 3])
    quiet = g51.filter(~pl.col("pt_date").is_in(list(excl)))
    res["NE43"] = {"a_0805": window(sc, cal_days, "2026-08-05"), "b_0821": window(sc, cal_days, "2026-08-21"),
                   "quiet_days": quiet.height, "quiet_alarm_rate": float((quiet["z_F"].fill_nan(None).fill_null(0) >= L.TAU).mean()),
                   "quiet_alarms": quiet.filter(pl.col("z_F") >= L.TAU).select("pt_date", "z_F", "top").rows()}
    # NE45
    rj = ev.filter((pl.col("cls") == "roster") & pl.col("day0").is_in(d51) & ~pl.col("held0"))["day0"].unique().sort().to_list()
    s_at_joins = [(d, window(sc, cal_days, d)["S"]) for d in rj]
    res["NE45"] = {"w_0729": window(sc, cal_days, "2026-07-29"), "roster_join_days": len(rj),
                   "S_alarms_at_joins": sum(1 for _, s in s_at_joins if s is not None and s >= L.TAU), "S_at_joins": s_at_joins}
    # NE40 and the 03-31 outage
    res["NE40"] = {"w_0420": window(sc, cal_days, "2026-04-20"), "w_0331": window(sc, cal_days, "2026-03-31")}
    # NE14
    res["NE14"] = {"w_0324": window(sc, cal_days, "2026-03-24")}
    (OUT / "native").mkdir(exist_ok=True)
    (OUT / "native" / "results.json").write_text(json.dumps(res, indent=1, default=str))
    for k, v in res.items():
        print(k, json.dumps({kk: (vv if not isinstance(vv, dict) else {c: vv.get(c) for c in CH + ["top"]}) for kk, vv in v.items()}, default=str)[:900])

    # ------------------------------------------------------------------ figures
    rr = json.loads((OUT / "replication" / "results.json").read_text())
    classes = ["scaffold_tool", "scaffold_prompt", "scaffold_family", "operator", "operator_schedule", "goal", "roster", "room", "undocumented"]
    M = np.array([[rr["classes"].get(c, {}).get(ch, {}).get("auc", np.nan) for ch in CH] for c in classes], float)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1.15, 1]})
    im = ax[0].imshow(M, cmap="RdBu_r", vmin=0.2, vmax=0.95, aspect="auto")
    ax[0].set_xticks(range(len(CH)), ["S\nschema", "M\nmix", "O\noracle", "D\ndrive", "C\ntopic", "fused"], fontsize=7)
    ax[0].set_yticks(range(len(classes)), [c.replace("_", " ") + f" ({rr['classes'].get(c, {}).get('F', {}).get('n', 0)})" for c in classes], fontsize=7)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if np.isfinite(M[i, j]):
                ax[0].text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=6)
    ax[0].set_title("AUC: event window vs placebo window", fontsize=8)
    plt.colorbar(im, ax=ax[0], fraction=0.04)
    s = sc.filter(pl.col("goal_no") == 51).sort("pt_date")
    x = np.arange(s.height)
    for ch, col in zip(["S", "M", "O", "D", "C"], ["#2a78d6", "#7a7a7a", "#e3a008", "#d03b3b", "#0ca30c"]):
        ax[1].plot(x, np.clip(s[f"z_{ch}"].fill_nan(None).fill_null(0).to_numpy(), -1, 12), lw=0.9, color=col, label=ch)
    ax[1].axhline(L.TAU, color="k", ls=":", lw=0.8)
    dl = s["pt_date"].to_list()
    for d, lab in (("2026-07-29", "NE45"), ("2026-08-05", "NE43a"), ("2026-08-21", "NE43b")):
        if d in dl:
            ax[1].axvline(dl.index(d), color="k", lw=0.6, alpha=0.5)
            ax[1].text(dl.index(d), 12.3, lab, fontsize=6, ha="center")
    ax[1].set_xticks(x[::6], [d[5:] for d in dl[::6]], fontsize=6, rotation=45)
    ax[1].set_ylabel("channel score (clipped at 12)", fontsize=7)
    ax[1].set_title("#51 daily channel scores", fontsize=8)
    ax[1].legend(fontsize=6, ncol=5, loc="upper left", bbox_to_anchor=(0, 0.93))
    ax[1].tick_params(labelsize=6)
    fig.tight_layout()
    (HYP / "figures").mkdir(exist_ok=True)
    fig.savefig(HYP / "figures" / "summary_obs.pdf")
    # synthetic figure
    syn = json.loads((OUT / "synthetic" / "summary.json").read_text())
    types = ["schema", "mix5", "mix3", "oracle", "drive", "content", "roster", "goalmix"]
    S = np.array([[syn["hit_rate"][t][c] for c in CH] for t in types])
    fig, ax = plt.subplots(figsize=(3.4, 2.0))
    ax.imshow(S, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            ax.text(j, i, f"{S[i, j]:.2f}", ha="center", va="center", fontsize=5.5, color="w" if S[i, j] > 0.6 else "k")
    ax.set_xticks(range(len(CH)), ["S", "M", "O", "D", "C", "fused"], fontsize=6)
    ax.set_yticks(range(len(types)), types, fontsize=6)
    ax.set_title(f"synthetic hit rate at tau=4 (fused FAR/day {syn['far_per_day']['F']:.3f})", fontsize=6.5)
    fig.tight_layout()
    fig.savefig(HYP / "figures" / "synthetic.pdf")


if __name__ == "__main__":
    main()
