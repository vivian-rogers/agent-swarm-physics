"""H30 round 1b (2026-10-04): input decomposition, native tests, cross-period summary, figures, per-period estimates.

Reads round-1 outputs (OUT/G<NN>/) and round-1b outputs (OUT/r1b/G<NN>/, from scheme/build.py --data r1b and
run_period.py --data r1b). Writes OUT/r1b/{summary_r1b.json, decomposition.json, natives.json},
figures/summary_obs_r1b.pdf, figures/r1b_natives.pdf, and per-period rows via infra/shared/estimates.write_estimates.
Run: uv run python hypotheses/H30-operator-susceptibility/analysis/r1b_extra.py [--no-decompose] [--no-estimates]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h30lib import *  # noqa: E402,F403
from summarize import dl_meta, sane, se_of  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PERIODS = ["G04", "G05", "G06", "G13", "G30", "G31", "G33", "G35", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
R1B = out_root("r1b")
LOW = ("G30", "G31", "G33", "G35", "G37", "G39", "G40", "G41", "G42", "G44")
TWELVE_H = ("G37", "G38", "G39", "G40", "G41", "G42", "G44")
B = 1000


def load(p, data):
    f = out_root(data) / p / "results.json"
    return json.loads(f.read_text()) if f.exists() else None


def remap_rows(kicks: pl.DataFrame, panels) -> pl.DataFrame:
    """Re-index kick rows onto these panels' agent order (round-1 kick rows refer to round-1 panels)."""
    amap = {(pp.day, int(a)): i for pp in panels for i, a in enumerate(pp.agents)}
    rows = [amap.get((d, a), -1) for d, a in kicks.select("day", "agent").iter_rows()]
    return kicks.with_columns(pl.Series("row", rows, dtype=pl.Int32)).filter(pl.col("row") >= 0)


def fit_pair(base, X, W):
    out = {}
    for lab, fe in (("dayfe", "day"), ("nofe", None)):
        pc = period_ci(fit_activity(base, X, fe2=fe), W)
        out[lab] = {c: pc.get(c) for c in ("N_tgt", "N_by") if c in pc}
    return out


def decompose(p: str) -> dict:
    """(a) round 1 · (b) fixed bins only · (c) + leading @ and ledger recipients (posting minute) ·
    (d) + receiving-call timing (A1 future-undirected adjustment kept) · (e) full round 1b (past-only)."""
    info = json.loads((OUT / p / "build.json").read_text())
    days = info["days"]
    r1, rb = load(p, "r1"), load(p, "r1b")
    res = {"a_round1": {"nofe": {"N_tgt": r1["act_nofe"].get("N_tgt")}, "dayfe": {"N_tgt": r1["act"].get("N_tgt")}}}
    panels, _ = load_panels(days, data="r1b")
    W = boot_weights(len(panels), B)
    k1 = remap_rows(pl.read_parquet(OUT / p / "kicks.parquet"), panels)
    base = build_base(panels, kicks=k1, strata="full")
    res["b_fixed_bins"] = fit_pair(base, kick_columns(base, k1), W)
    kb = pl.read_parquet(R1B / p / "kicks.parquet")
    cal = calendar()
    ws = {d: w.timestamp() for d, w in zip(cal["pt_date"].to_list(), cal["win_start"].to_list())}
    nmin = {pp.day: pp.n_min for pp in panels}
    kpost = kb.with_columns(pl.struct("pt_date", "ts_post").map_elements(lambda s: int((s["ts_post"] - ws[s["pt_date"]]) // 60),
                                                                         return_dtype=pl.Int32).alias("minute"))
    kpost = kpost.filter((pl.col("minute") >= 0) & (pl.col("minute") < pl.col("day").replace_strict(nmin, return_dtype=pl.Int32)))
    base = build_base(panels, kicks=kpost, strata="full")
    res["c_leading_at_posting"] = fit_pair(base, kick_columns(base, kpost), W)
    res["d_receiving_call_A1adj"] = {"nofe": {"N_tgt": rb.get("act_futadj_nofe", {}).get("N_tgt")},
                                     "dayfe": {"N_tgt": rb.get("act_futadj", {}).get("N_tgt")}}
    res["e_round1b"] = {"nofe": {"N_tgt": rb["act_nofe"].get("N_tgt")}, "dayfe": {"N_tgt": rb["act"].get("N_tgt")}}
    res["n_kicks"] = {"round1": int(k1.filter(pl.col("cls") == "N_tgt").height),
                      "round1b": int(kb.filter(pl.col("cls") == "N_tgt").height)}
    return res


# =============================================================================== natives

def native_g05() -> dict:
    """#5 human dose: per-message orthogonalized chi_con by k_h = human messages read in the same receiving call."""
    kb = pl.read_parquet(R1B / "G05" / "kicks.parquet").with_row_index("pair").with_columns(pl.col("pair").cast(pl.Int64))
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg").with_columns(pl.col("msg").cast(pl.Int64))
    kb = kb.join(chat, on="msg", how="left")
    days = json.loads((R1B / "G05" / "build.json").read_text())["days"]
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(days)).select("turn_id", "agent").collect())
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(cw["turn_id"].implode()))
          .select("turn_id", "message_id", "kind").collect().join(cw, on="turn_id", how="inner"))
    kh = it.filter(pl.col("kind") == "human").group_by("turn_id").len().rename({"len": "k_h"})
    it = it.filter(pl.col("kind") == "human").join(kh, on="turn_id").select("message_id", pl.col("agent").cast(pl.Int32), "k_h")
    kb = kb.join(it, on=["message_id", "agent"], how="left")
    out = {"bins": [[1, 1], [2, 3], [4, 7], [8, 10 ** 6]]}
    nd = len(days)
    Wb = boot_weights(nd, B)
    for model, fn in (("bge_small", "content.parquet"), ("gte_modernbert", "content_gte.parquet")):
        cs = pl.read_parquet(R1B / "G05" / fn).join(kb.select("pair", "k_h"), on="pair", how="left").filter(
            pl.col("chi_orth").is_not_nan() & pl.col("k_h").is_not_null())
        res = {}
        for cls_lab, sel in (("all", ["H_und", "H_men"]), ("H_und", ["H_und"]), ("H_men", ["H_men"])):
            sub = cs.filter(pl.col("cls").is_in(sel))
            rows = []
            boots = []
            kc = []
            for lo, hi in out["bins"]:
                b = sub.filter((pl.col("k_h") >= lo) & (pl.col("k_h") <= hi))
                S = np.bincount(b["day"].to_numpy(), weights=b["chi_orth"].to_numpy(), minlength=nd)
                N = np.bincount(b["day"].to_numpy(), minlength=nd).astype(float)
                with np.errstate(invalid="ignore", divide="ignore"):
                    bt = (Wb @ S) / (Wb @ N)
                boots.append(bt)
                kc.append(float(b["k_h"].mean()) if b.height else np.nan)
                rows.append({"n": b.height, "k_mean": kc[-1], "chi": ci(bt)})
            boots = np.array(boots)          # (bins, B+1)
            kc = np.array(kc)
            ok = np.isfinite(kc) & np.array([r["n"] >= 30 for r in rows])

            def slope(y):
                m = ok & np.isfinite(y) & (y > 0)
                if m.sum() < 3:
                    return np.nan
                return float(np.polyfit(np.log(kc[m]), np.log(y[m]), 1)[0])
            sl = np.array([slope(boots[:, j]) for j in range(boots.shape[1])])
            ratio = boots[0] / boots[-1] if rows[-1]["n"] >= 30 else np.full(boots.shape[1], np.nan)
            lin = np.array([float(np.polyfit(np.log(kc[ok]), boots[ok, j], 1)[0]) if ok.sum() >= 3 and np.isfinite(boots[ok, j]).all() else np.nan
                            for j in range(boots.shape[1])])
            res[cls_lab] = {"bins": rows, "loglog_slope": ci(sl), "ratio_k1_over_k8plus": ci(ratio),
                            "linear_slope_per_log_k": ci(lin)}
        out[model] = res
    return out


def native_ne44(tab) -> dict:
    out = {}
    for key, lab in (("act_N_tgt", "chi_act"), ("first_N_tgt", "first")):
        rows = [t for t in tab if t["period"] in TWELVE_H and t.get(key) and t[key][1] is not None]
        m = dl_meta([t[key][0] for t in rows], [se_of(t[key]) for t in rows])
        g51 = next(t for t in tab if t["period"] == "G51")[key]
        se51 = se_of(g51)
        if m:
            s12 = (m["hi"] - m["lo"]) / 3.92
            d = m["mean"] - g51[0]
            sd = np.sqrt(s12 ** 2 + se51 ** 2)
            out[lab] = {"twelve_h_pooled": m, "twelve_h_periods": [t["period"] for t in rows], "G51": g51,
                        "diff": [d, d - 1.96 * sd, d + 1.96 * sd]}
    return out


def native_ne10(tab) -> dict:
    rows = [t for t in tab if t["period"] in ("G30", "G31") and t.get("act_N_tgt") and t["act_N_tgt"][1] is not None]
    m = dl_meta([t["act_N_tgt"][0] for t in rows], [se_of(t["act_N_tgt"]) for t in rows])
    g51f = next(t for t in tab if t["period"] == "G51")["first_N_tgt"]
    per = {t["period"]: t["act_N_tgt"] for t in rows}
    return {"pooled": m, "per_period": per, "G51_first": g51f, "n_kicks": {t["period"]: t["act_n"] for t in rows}}


# =============================================================================== summary

def table_r1b() -> list:
    tab = []
    for p in PERIODS:
        r = load(p, "r1b")
        if r is None:
            continue
        st = r.get("stability", {})
        tab.append({"period": p, "regime": r["regime"], "days": r["n_days"], "act_n": r["act_n"].get("N_tgt"),
                    "act_N_tgt": sane(r["act"].get("N_tgt")), "act_N_tgt_nofe": sane(r.get("act_nofe", {}).get("N_tgt")),
                    "act_N_by": sane(r["act"].get("N_by")), "act_H_und": sane(r["act"].get("H_und")),
                    "act_H_men": sane(r["act"].get("H_men")),
                    "first_N_tgt": sane((r.get("act_first") or {}).get("N_tgt")),
                    "repeat_N_tgt": sane((r.get("act_repeat") or {}).get("N_tgt")),
                    "lull": sane((r.get("lull_split", {}).get("lull") or {}).get("N_tgt")),
                    "no_lull": sane((r.get("lull_split", {}).get("no_lull") or {}).get("N_tgt")),
                    "con_H_und": sane((r["con"].get("H_und") or {}).get("orth")),
                    "con_H_men": sane((r["con"].get("H_men") or {}).get("orth")),
                    "con_N_tgt": sane((r["con"].get("N_tgt") or {}).get("orth")),
                    "con_gte_H_und": sane(((r.get("con_gte") or {}).get("H_und") or {}).get("orth")),
                    "con_gte_H_men": sane(((r.get("con_gte") or {}).get("H_men") or {}).get("orth")),
                    "con_gte_N_tgt": sane(((r.get("con_gte") or {}).get("N_tgt") or {}).get("orth")),
                    "n_con": {c: (r["con"].get(c) or {}).get("n") for c in CLASSES},
                    "stab_act_N_tgt": {k: st.get("act_N_tgt", {}).get(k) for k in ("n_days_eligible", "p_perm_msg", "R1_perm_msg", "lag1", "p_lag1")},
                    "stab_con_H_und": {k: st.get("con_H_und", {}).get(k) for k in ("n_days_eligible", "p_perm_msg", "R1_perm_msg", "lag1")},
                    "age": (r.get("covariates", {}).get("act_N_tgt") or {}).get("age"),
                    "fill_phase": r.get("fill_phase", {}).get("chi"),
                    "family": r.get("family"), "pre_placebo": r.get("pre_placebo", {}).get("N_tgt"),
                    "pre_placebo_nofe": r.get("pre_placebo_nofe", {}).get("N_tgt"), "swap": r.get("swap_null", {}).get("N_tgt"),
                    "verdict": r["verdict"]["overall"], "rows": r["verdict"]["rows"],
                    "kick_counts": json.loads((R1B / p / "build.json").read_text()).get("kick_counts_r1b")})
    return tab


def summary(tab) -> dict:
    S = {"table": tab}
    for lab, sel in (("I_II", lambda t: t["regime"] in ("I", "II")), ("III_excl_G51", lambda t: t["regime"] == "III" and t["period"] != "G51"),
                     ("III_all", lambda t: t["regime"] == "III")):
        rows = [t for t in tab if sel(t) and t["act_N_tgt"] and t["act_N_tgt"][1] is not None and (t["act_n"] or 0) >= 5]
        S[f"meta_Ntgt_{lab}"] = (dl_meta([t["act_N_tgt"][0] for t in rows], [se_of(t["act_N_tgt"]) for t in rows]) or {}) | {
            "periods": [t["period"] for t in rows]}
    for key in ("con_H_und", "con_H_men", "con_gte_H_und", "con_gte_H_men"):
        rows = [t for t in tab if t[key] and t[key][1] is not None]
        S[f"meta_{key}"] = dl_meta([t[key][0] for t in rows], [se_of(t[key]) for t in rows])
        S[f"n_{key}_ci_pos"] = [sum(t[key][1] > 0 for t in rows), len(rows)]
    low = [t for t in tab if t["period"] in LOW and t["act_N_tgt"]]
    S["P1_low_power_positive"] = [sum(t["act_N_tgt"][0] > 0 for t in low), len(low)]
    return S


def figures(tab, S, D, N):
    FIG.mkdir(parents=True, exist_ok=True)
    T = {t["period"]: t for t in tab}
    blue, orange, grey, red = "#2b6cb0", "#c05621", "#718096", "#c53030"
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
    # (a) decomposition of the G51 / G38 nudge response
    labs = [("a_round1", "round 1"), ("b_fixed_bins", "+ fixed bins"), ("c_leading_at_posting", "+ leading @"),
            ("d_receiving_call_A1adj", "+ receiving call"), ("e_round1b", "+ past-only (1b)")]
    for k, (p, col) in enumerate((("G51", blue), ("G38", orange))):
        if p not in D:
            continue
        ys = np.arange(len(labs))[::-1] + (0.18 if k == 0 else -0.18)
        for y, (key, _) in zip(ys, labs):
            c = (D[p][key].get("dayfe") or {}).get("N_tgt")
            if c and c[0] is not None:
                if c[1] is not None and np.isfinite(c[1]):
                    ax[0].plot([c[1], c[2]], [y, y], color=col, lw=1.1)
                ax[0].plot([c[0]], [y], "o", color=col, ms=3.5, label=p if key == "a_round1" else None)
    ax[0].set_yticks(np.arange(len(labs))[::-1]); ax[0].set_yticklabels([l for _, l in labs], fontsize=7)
    ax[0].axvline(0, color="0.5", lw=0.6); ax[0].set_xlabel("extra active min per nudge (day FE)")
    ax[0].set_title("(a) what moved the nudge response", fontsize=9); ax[0].legend(fontsize=7, frameon=False)
    # (b) situational chi in G51 + human content
    items = [("G51 first nudge", T["G51"]["first_N_tgt"], blue), ("G51 repeat nudge", T["G51"]["repeat_N_tgt"], blue),
             ("G51 swarm lull", T["G51"]["lull"], red), ("G51 not lull", T["G51"]["no_lull"], red),
             ("G51 bystander", T["G51"]["act_N_by"], grey)]
    for p in ("G04", "G05", "G13", "G51"):
        if T[p]["con_H_und"]:
            items.append((f"{p} human→content ×20", [x * 20 if x is not None else None for x in T[p]["con_H_und"]], orange))
    ys = np.arange(len(items))[::-1]
    for y, (lab, c, col) in zip(ys, items):
        if not c or c[0] is None:
            continue
        if c[1] is not None:
            ax[1].plot([c[1], c[2]], [y, y], color=col, lw=1.1)
        ax[1].plot([c[0]], [y], "o", color=col, ms=3.5)
    ax[1].set_yticks(ys); ax[1].set_yticklabels([i[0] for i in items], fontsize=7)
    ax[1].axvline(0, color="0.5", lw=0.6); ax[1].set_xlabel("activity (min) | content (cosine ×20)")
    ax[1].set_title("(b) round 1b situational χ_op", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "summary_obs_r1b.pdf"); plt.close(fig)
    # natives
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 2.9))
    g = N.get("G05", {}).get("bge_small", {})
    for cls_lab, col in (("H_und", orange), ("H_men", "#9c4221")):
        rr = g.get(cls_lab, {}).get("bins", [])
        x = [r["k_mean"] for r in rr if r["n"] >= 30]
        y = [r["chi"] for r in rr if r["n"] >= 30]
        if x:
            ax[0].errorbar(x, [c[0] for c in y], yerr=[[c[0] - c[1] for c in y], [c[2] - c[0] for c in y]], fmt="o-", ms=3,
                           color=col, label=cls_lab, lw=0.9)
    ax[0].set_xscale("log"); ax[0].axhline(0, color="0.5", lw=0.6)
    ax[0].set_xlabel("human messages read in the same call (k_h)"); ax[0].set_ylabel("χ_con per message")
    ax[0].set_title("(a) #5: content pull vs read-out dose", fontsize=9); ax[0].legend(fontsize=7, frameon=False)
    items = []
    for p in TWELVE_H + ("G51",):
        t = T.get(p)
        if t and t["act_N_tgt"]:
            items.append((f"{p} (n {t['act_n']})", t["act_N_tgt"], blue if p != "G51" else red))
    ne = N.get("NE44", {}).get("chi_act")
    if ne:
        m = ne["twelve_h_pooled"]
        items.append(("12-h pooled", [m["mean"], m["lo"], m["hi"]], "#2c5282"))
    ys = np.arange(len(items))[::-1]
    for y, (lab, c, col) in zip(ys, items):
        if c[1] is not None:
            ax[1].plot([max(c[1], -4), min(c[2], 6)], [y, y], color=col, lw=1.1)
        ax[1].plot([c[0]], [y], "o", color=col, ms=3.5)
    ax[1].set_yticks(ys); ax[1].set_yticklabels([i[0] for i in items], fontsize=7)
    ax[1].axvline(0, color="0.5", lw=0.6); ax[1].set_xlim(-4, 6)
    ax[1].set_xlabel("χ_act(N_tgt), extra active min per nudge")
    ax[1].set_title("(b) NE44: 12-h pause default vs 5-min (G51)", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "r1b_natives.pdf"); plt.close(fig)


def estimates_rows(tab, N) -> list:
    rows = []
    meth = {"chi_act": "local projection, kick at the receiving call, strata through m-1 + call indicator, past-only kick "
                       "adjustment, day FE; day-block bootstrap (r1b)",
            "chi_con": "orthogonalized content shift toward the message vs same-kind other-day messages, receiving-call "
                       "timing; day-block bootstrap (r1b)"}
    for t in tab:
        g = int(t["period"][1:])
        r = load(t["period"], "r1b")
        for stat, ch, c, n, nk in (("chi_act", "N_tgt", t["act_N_tgt"], t["act_n"], "kicks"),
                                   ("chi_act", "N_by", t["act_N_by"], r["act_n"].get("N_by"), "kicks"),
                                   ("chi_act", "H_und", t["act_H_und"], r["act_n"].get("H_und"), "kicks"),
                                   ("chi_act", "H_men", t["act_H_men"], r["act_n"].get("H_men"), "kicks"),
                                   ("chi_act_first", "N_tgt", t["first_N_tgt"], None, "kicks"),
                                   ("chi_con", "H_und", t["con_H_und"], t["n_con"].get("H_und"), "pairs"),
                                   ("chi_con", "H_men", t["con_H_men"], t["n_con"].get("H_men"), "pairs"),
                                   ("chi_con", "N_tgt", t["con_N_tgt"], t["n_con"].get("N_tgt"), "pairs"),
                                   ("chi_con_gte", "H_und", t["con_gte_H_und"], None, "pairs")):
            if not c or c[0] is None or not n and stat not in ("chi_act_first", "chi_con_gte"):
                continue
            if (n or 0) < 5 and stat not in ("chi_act_first", "chi_con_gte"):
                continue
            base = "chi_con" if stat.startswith("chi_con") else "chi_act"
            rows.append(dict(period_unit=t["period"], goal_no=g, statistic=stat, channel=ch, estimate=float(c[0]),
                             ci_lo=None if c[1] is None else float(c[1]), ci_hi=None if c[2] is None else float(c[2]),
                             ci_level=0.95 if c[1] is not None else None, ci_kind="percentile" if c[1] is not None else "none",
                             n=None if n is None else float(n), n_kind=nk,
                             method=meth[base] + (" (gte-modernbert)" if stat.endswith("_gte") else ""),
                             null="day-swap kick null (activity) / pseudo-true message null (content)", role="replication",
                             first_day=r and json.loads((R1B / t["period"] / "build.json").read_text())["days"][0],
                             last_day=json.loads((R1B / t["period"] / "build.json").read_text())["days"][-1],
                             status="ok" if (n or 30) >= 30 else "underpowered",
                             source=f"data/processed/H30-operator-susceptibility/r1b/{t['period']}/results.json",
                             notes="round 1b: activity_bins_fixed, leading-@ nudge target, DQ1 receiving call"))
    g = N.get("G05", {}).get("bge_small", {}).get("all")
    if g:
        c = g["loglog_slope"]
        rows.append(dict(period_unit="G05", goal_no=5, statistic="chi_con_dilution_slope", channel="human",
                         estimate=float(c[0]), ci_lo=c[1], ci_hi=c[2], ci_level=0.95, ci_kind="percentile",
                         n=float(sum(b["n"] for b in g["bins"])), n_kind="pairs",
                         method="log-log slope of per-message chi_con on human messages read in the same receiving call (bins 1, 2-3, 4-7, 8+); day bootstrap",
                         null=None, role="native", first_day="2025-06-19", last_day="2025-06-25", status="ok",
                         source="data/processed/H30-operator-susceptibility/r1b/natives.json",
                         notes="round 1b native test (#5 human dose)"))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-decompose", action="store_true")
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    tab = table_r1b()
    S = summary(tab)
    D = {}
    if not a.no_decompose:
        for p in ("G51", "G38", "G41"):
            D[p] = decompose(p)
            print(p, json.dumps({k: (v.get("dayfe", {}).get("N_tgt") if isinstance(v, dict) else v) for k, v in D[p].items()}, default=str), flush=True)
        jdump(D, R1B / "decomposition.json")
    elif (R1B / "decomposition.json").exists():
        D = json.loads((R1B / "decomposition.json").read_text())
    N = {"G05": native_g05(), "NE44": native_ne44(tab), "NE10": native_ne10(tab)}
    jdump(N, R1B / "natives.json")
    S["natives"] = N
    S["decomposition"] = D
    jdump(S, R1B / "summary_r1b.json")
    figures(tab, S, D, N)
    print(json.dumps({k: v for k, v in S.items() if k not in ("table", "decomposition")}, indent=1, default=str)[:6000])
    if not a.no_estimates:
        sys.path.insert(0, str(ROOT / "infra/shared"))
        import estimates as E
        rows = estimates_rows(tab, N)
        E.write_estimates(rows, hypothesis="H30")
        print("estimates written:", len(rows))


if __name__ == "__main__":
    main()
