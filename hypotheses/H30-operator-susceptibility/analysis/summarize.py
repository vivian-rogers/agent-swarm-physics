"""H30 cross-period synthesis: table, regime comparison (random effects), figures.

Reads data/processed/H30-operator-susceptibility/G<NN>/{results.json, daily.parquet}; writes summary.json there and
figures/H30_summary.pdf (one page), figures/summary_obs.pdf (summary-page observable).
Run: uv run python hypotheses/H30-operator-susceptibility/analysis/summarize.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h30lib import *  # noqa: E402,F403

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PERIODS = ["G04", "G05", "G06", "G13", "G30", "G31", "G33", "G35", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
REG = {}


def sane(c, lim=50):
    if not c or c[0] is None or not np.isfinite(c[0]):
        return None
    if c[1] is None or c[2] is None or not np.isfinite(c[1]) or not np.isfinite(c[2]) or abs(c[1]) > lim or abs(c[2]) > lim:
        return [c[0], None, None]
    return c


def se_of(c):
    return (c[2] - c[1]) / 3.92 if c and c[1] is not None and c[2] is not None and c[2] - c[1] > 1e-6 else None


def dl_meta(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) < 2:
        return None
    w = 1 / se ** 2
    mu = (w * est).sum() / w.sum()
    Q = (w * (est - mu) ** 2).sum(); df = len(est) - 1
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - df) / c)
    ws = 1 / (se ** 2 + tau2)
    m = (ws * est).sum() / ws.sum(); s = np.sqrt(1 / ws.sum())
    return {"k": int(len(est)), "mean": float(m), "lo": float(m - 1.96 * s), "hi": float(m + 1.96 * s), "tau2": float(tau2),
            "I2": float(max(0, (Q - df) / Q)) if Q > 0 else 0.0, "p_Q": float(stats.chi2.sf(Q, df))}


def main():
    R = {p: json.loads((OUT / p / "results.json").read_text()) for p in PERIODS if (OUT / p / "results.json").exists()}
    table = []
    for p, r in R.items():
        st = r.get("stability", {})
        row = {"period": p, "regime": r["regime"], "days": r["n_days"],
               "nudges": r["n_messages"].get("nudge", 0), "humans": r["n_messages"].get("human", 0),
               "act_Ntgt_prereg": sane(r.get("act_nofe", {}).get("N_tgt")), "act_Ntgt_dayfe": sane(r["act"].get("N_tgt")),
               "act_Ntgt_n": r["act_n"].get("N_tgt"),
               "act_Nby_prereg": sane(r.get("act_nofe", {}).get("N_by")),
               "act_Hund_prereg": sane(r.get("act_nofe", {}).get("H_und")), "act_Hmen_prereg": sane(r.get("act_nofe", {}).get("H_men")),
               "first_Ntgt": sane((r.get("act_first") or {}).get("N_tgt")), "repeat_Ntgt": sane((r.get("act_repeat") or {}).get("N_tgt")),
               "con_Hund": sane((r["con"].get("H_und") or {}).get("orth")), "con_Hmen": sane((r["con"].get("H_men") or {}).get("orth")),
               "con_Ntgt": sane((r["con"].get("N_tgt") or {}).get("orth")),
               "stab_act_Ntgt": {k: st.get("act_N_tgt", {}).get(k) for k in ("n_days_eligible", "p_perm_msg", "R1_perm_msg", "lag1", "p_lag1")},
               "stab_con_Hund": {k: st.get("con_H_und", {}).get(k) for k in ("n_days_eligible", "p_perm_msg", "R1_perm_msg", "lag1")},
               "verdict": r["verdict"]["overall"]}
        table.append(row)
    S = {"table": table}
    # regime comparison of the per-nudge activity response (pre-registered model), random effects
    for lab, sel in (("I_II", lambda r: r["regime"] in ("I", "II")), ("III_excl_G51", lambda r: r["regime"] == "III" and r["period"] != "G51"),
                     ("III_all", lambda r: r["regime"] == "III")):
        rows = [t for t in table if sel(t) and t["act_Ntgt_prereg"] and (t["act_Ntgt_n"] or 0) >= 5]
        S[f"meta_Ntgt_{lab}"] = dl_meta([t["act_Ntgt_prereg"][0] for t in rows], [se_of(t["act_Ntgt_prereg"]) or np.nan for t in rows])
        S[f"meta_Ntgt_{lab}"] = (S[f"meta_Ntgt_{lab}"] or {}) | {"periods": [t["period"] for t in rows]}
    rows = [t for t in table if t["con_Hund"] and t["con_Hund"][1] is not None]
    S["meta_con_Hund"] = dl_meta([t["con_Hund"][0] for t in rows], [se_of(t["con_Hund"]) for t in rows])
    rows = [t for t in table if t["con_Hmen"] and t["con_Hmen"][1] is not None]
    S["meta_con_Hmen"] = dl_meta([t["con_Hmen"][0] for t in rows], [se_of(t["con_Hmen"]) for t in rows])
    # low-power nudge periods: share of positive point estimates (P1 count rule)
    low = [t for t in table if t["period"] in ("G30", "G31", "G33", "G35", "G37", "G39", "G40", "G42", "G44") and t["act_Ntgt_prereg"]]
    S["P1_low_power_positive"] = [sum(t["act_Ntgt_prereg"][0] > 0 for t in low), len(low)]
    jdump(S, OUT / "summary.json")
    figures(R, table, S)
    print(json.dumps({k: v for k, v in S.items() if k != "table"}, indent=1, default=str))


def figures(R, table, S):
    FIG.mkdir(parents=True, exist_ok=True)
    g51 = pl.read_parquet(OUT / "G51" / "daily.parquet")
    g04 = pl.read_parquet(OUT / "G04" / "daily.parquet")

    def daily_panel(ax, d, ch, cls, per, ylab, title, color):
        d = d.filter((pl.col("channel") == ch) & (pl.col("cls") == cls) & (pl.col("n") >= 3)).sort("goal_day")
        x = d["goal_day"].to_numpy(); y = d["chi"].to_numpy(); e = 1.96 * d["se"].to_numpy()
        ax.errorbar(x, y, yerr=e, fmt="o", ms=3, lw=0.7, color=color, ecolor=color, alpha=0.85)
        if per and per[0] is not None:
            ax.axhspan(per[1], per[2], color=color, alpha=0.12, lw=0)
            ax.axhline(per[0], color=color, lw=1)
        ax.axhline(0, color="0.5", lw=0.6)
        ax.set_xlabel("day in goal period"); ax.set_ylabel(ylab); ax.set_title(title, fontsize=9)

    def forest(ax, items, xlab, title):
        ys = np.arange(len(items))[::-1]
        for y, (lab, c, col) in zip(ys, items):
            if not c or c[0] is None:
                continue
            if c[1] is not None:
                ax.plot([c[1], c[2]], [y, y], color=col, lw=1.2)
            ax.plot([c[0]], [y], "o", color=col, ms=4)
        ax.set_yticks(ys); ax.set_yticklabels([i[0] for i in items], fontsize=7)
        ax.axvline(0, color="0.5", lw=0.6); ax.set_xlabel(xlab); ax.set_title(title, fontsize=9)

    T = {t["period"]: t for t in table}
    blue, orange, grey = "#2b6cb0", "#c05621", "#718096"
    # ---- one-page card summary
    fig, ax = plt.subplots(2, 2, figsize=(10, 7.2))
    daily_panel(ax[0, 0], g51, "act", "N_tgt", R["G51"]["act"]["N_tgt"], "extra active min per nudge (30 min)",
                "(a) G51 daily activity gauge χ_act(N_tgt), day FE", blue)
    st = R["G51"]["stability"]["act_N_tgt"]
    ax[0, 0].text(0.02, 0.97, f"perm p (msg) {st.get('p_perm_msg'):.2f}; R₁ {st.get('R1_perm_msg'):.2f}; lag-1 {st.get('lag1'):.2f}",
                  transform=ax[0, 0].transAxes, fontsize=7, va="top")
    daily_panel(ax[0, 1], g04, "con", "H_und", R["G04"]["con"]["H_und"]["orth"], "content χ (cosine)",
                "(b) G04 daily content gauge χ_con(H_und)", orange)
    st = R["G04"]["stability"]["con_H_und"]
    ax[0, 1].text(0.02, 0.97, f"perm p (msg) {st.get('p_perm_msg'):.3f}; R₁ {st.get('R1_perm_msg'):.2f}; lag-1 {st.get('lag1'):.2f}",
                  transform=ax[0, 1].transAxes, fontsize=7, va="top")
    items = []
    for p in ("G30", "G31", "G33", "G35", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"):
        t = T.get(p)
        if t and t["act_Ntgt_prereg"]:
            items.append((f"{p} ({t['regime']}, n {t['act_Ntgt_n']})", t["act_Ntgt_prereg"], blue))
    items.append(("G51 first nudge (day FE)", T["G51"]["first_Ntgt"], grey))
    items.append(("G51 repeat nudge (day FE)", T["G51"]["repeat_Ntgt"], grey))
    forest(ax[1, 0], items, "extra active min per nudge", "(c) nudge activity response by period")
    ax[1, 0].set_xlim(-4, 4)
    items = []
    for p in ("G04", "G05", "G06", "G13", "G44", "G51", "G38"):
        t = T.get(p)
        if t and t["con_Hund"]:
            items.append((f"{p} H_und", t["con_Hund"], orange))
        if t and t["con_Hmen"]:
            items.append((f"{p} H_men", t["con_Hmen"], "#9c4221"))
    for p in ("G38", "G41", "G51"):
        t = T.get(p)
        if t and t["con_Ntgt"]:
            items.append((f"{p} N_tgt", t["con_Ntgt"], blue))
    forest(ax[1, 1], items, "content χ (cosine, orthogonalized)", "(d) content response by period")
    fig.suptitle("H30 operator susceptibility χ_op: nudges move activity, humans move content; neither gauge is stable day to day",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(FIG / "H30_summary.pdf"); plt.close(fig)
    # ---- summary-page observable (two panels)
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 2.9))
    daily_panel(ax[0], g51, "act", "N_tgt", R["G51"]["act"]["N_tgt"], "extra active min / nudge", "(a) G51: daily nudge gauge", blue)
    ax[0].set_ylim(-4, 6)
    items = []
    for p in ("G38", "G41", "G51"):
        t = T[p]
        items.append((f"{p} nudge→activity", t["act_Ntgt_prereg"], blue))
    items.append(("G51 first nudge", T["G51"]["first_Ntgt"], grey))
    items.append(("G51 repeat nudge", T["G51"]["repeat_Ntgt"], grey))
    for p in ("G04", "G05", "G06", "G13"):
        t = T[p]
        items.append((f"{p} human→content ×20", [x * 20 if x is not None else None for x in t["con_Hund"]], orange))
    forest(ax[1], items, "activity (min) | content (cosine ×20)", "(b) period-level χ_op")
    ax[1].set_xlim(-1.5, 3)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)


if __name__ == "__main__":
    main()
