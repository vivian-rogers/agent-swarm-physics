"""Cross-period synthesis for H50: per-unit table, regime summaries, prediction checks (P2-P6), pooled Bode spectra,
per-agent transfer (HH190), and the cross-period figures.

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/summarize.py
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
import h50lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
FIG = ROOT / "hypotheses/H50-field-vs-coupling-transfer-lag/figures"
BLUE, ORANGE, AQUA, GRAY, INK, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b", "#4a3aa7"
RCOL = {"I": BLUE, "II": VIOLET, "III": ORANGE}


def load_all():
    rows = {}
    for p in sorted(OUT.glob("G*/*.json")) + sorted(OUT.glob("NE43/NE43*.json")):
        if p.name == "native.json":
            continue
        r = json.loads(p.read_text())
        rows[r["unit"]] = r
    return rows


def onset(lo):
    return next((k + 1 for k, l in enumerate(lo) if l is not None and l > 0), None)


def unit_table(R):
    out = []
    for u, r in R.items():
        g = r["gate_talk"]
        ga = r["gate_act"]
        c1 = r["c1"]
        row = dict(unit=u, regime=r["regime"], goal_no=r["goal_no"], N=r["N"], n_days=r["n_days"], n_pairs=r["n_pairs"],
                   ne43=u.startswith("NE43"), talk_rate=r["talk_rate"], med_call_s=r["med_call_s"], W=r["W"],
                   chat_share=r.get("chat_mode_share"),
                   J1=g["jumps"][0], J1_lo=g["j_lo"][0], J1_hi=g["j_hi"][0], J1_se=(g["j_hi"][0] - g["j_lo"][0]) / 3.92,
                   J2=g["jumps"][1], J2_lo=g["j_lo"][1], J2_hi=g["j_hi"][1],
                   K6=g["kernel"][5], K6_lo=g["k_lo"][5], K6_hi=g["k_hi"][5],
                   onset_talk=onset(g["j_lo"]), J1_act=ga["jumps"][0], J1_act_lo=ga["j_lo"][0], J1_act_hi=ga["j_hi"][0],
                   kappa=r["gate_k1"]["talk"].get("kappa"), Ep=r["gate_k1"]["talk"].get("Ep"), Em=r["gate_k1"]["talk"].get("Em"),
                   base_talk=r["gate_k1"]["talk"].get("base"),
                   readout_q50=r["peer_hop"]["readout_delay_s"]["q50"], readout_q90=r["peer_hop"]["readout_delay_s"]["q90"],
                   share_reply=r.get("share_reply_sources"),
                   J1_noreply=r["gate_variants"].get("no_reply", {}).get("J1"), J1_noreply_lo=r["gate_variants"].get("no_reply", {}).get("lo"),
                   J1_highconf=r["gate_variants"].get("high_conf_calls", {}).get("J1"),
                   J1_W3=r["gate_variants"].get("W3", {}).get("J1"),
                   J1_ment=r["gate_variants"].get("ment", {}).get("J1"), J1_noment=r["gate_variants"].get("no_ment", {}).get("J1"),
                   J1_certain=r["gate_variants"].get("certain", {}).get("J1"))
        for k in ("A_full", "A_trim", "A_span", "T_span", "T_full"):
            if k in c1:
                row[f"S_{k}"] = c1[k]["S_raw"]
                row[f"rho_{k}"] = c1[k]["rho_raw"]
                row[f"fF_{k}"] = c1[k]["f_F"]
                row[f"fFex_{k}"] = c1[k]["f_F"] - c1[k]["f_F_null"] if c1[k]["f_F"] is not None and c1[k]["f_F_null"] is not None else None
                row[f"fFnullsd_{k}"] = c1[k].get("f_F_null_sd")
                row[f"flag_{k}"] = c1[k].get("f_lag")
        for oc in ("work", "idle"):
            g2 = r.get(f"gate_{oc}")
            if g2:
                row[f"J1_{oc}"] = g2["jumps"][0]
                row[f"J1_{oc}_lo"] = g2["j_lo"][0]
                row[f"J1_{oc}_hi"] = g2["j_hi"][0]
        for k, v in r.get("c1_attr", {}).items():
            row[f"attr_{k}"] = (v["f_F"] - v["f_F_null"]) if v["f_F"] is not None and v["f_F_null"] is not None else None
        cf = r["cf_talk"]
        row["fC_T_span"] = cf["span_k1"]["f_C"]
        row["fC_T_span_lo"] = cf["span_k1_lo"]["f_C"]
        row["fC_T_span_hi"] = cf["span_k1_hi"]["f_C"]
        row["fC_T_full"] = cf["full_k1"]["f_C"]
        aF = cf.get("span_afterF", {})
        row["S_T_span_afterF"] = aF.get("S")
        row["S_T_span_afterFC"] = aF.get("S_cf")
        for which in ("A", "T"):
            f = r["fir"].get(which, {})
            for cl in L.SWARM_CLASSES:
                m = f.get(cl, {})
                if not m or not m.get("n_inputs"):
                    continue
                row[f"fir{which}_{cl}_G30"] = m.get("G30")
                row[f"fir{which}_{cl}_G30_lo"] = m.get("G30_lo")
                row[f"fir{which}_{cl}_G30_hi"] = m.get("G30_hi")
                row[f"fir{which}_{cl}_dead"] = m.get("dead_min")
                row[f"fir{which}_{cl}_corner"] = m.get("corner_period_min")
                row[f"fir{which}_{cl}_decay"] = m.get("decay_min")
                row[f"fir{which}_{cl}_pre"] = m.get("pre")
                row[f"fir{which}_{cl}_ring"] = m.get("ring")
                row[f"fir{which}_{cl}_n"] = m.get("n_inputs")
                w = f.get("welch", {}).get(cl, {})
                for b in range(4):
                    row[f"fir{which}_{cl}_coh{b}"] = w.get(f"coh_b{b}")
                row[f"fir{which}_{cl}_gd"] = w.get("group_delay_min")
        for name, e in r["exo"].items():
            row[f"exo_{name}_n"] = e.get("n")
            if "gate_talk" in e:
                row[f"exo_{name}_J1T"] = e["gate_talk"]["jumps"][0]
                row[f"exo_{name}_J1T_lo"] = e["gate_talk"]["j_lo"][0]
                row[f"exo_{name}_J1T_hi"] = e["gate_talk"]["j_hi"][0]
                row[f"exo_{name}_J1A"] = e["gate_act"]["jumps"][0]
                row[f"exo_{name}_J1A_lo"] = e["gate_act"]["j_lo"][0]
                row[f"exo_{name}_J1A_hi"] = e["gate_act"]["j_hi"][0]
                row[f"exo_{name}_onsetT"] = e.get("onset_talk")
                row[f"exo_{name}_onsetA"] = e.get("onset_act")
                row[f"exo_{name}_KT"] = e["gate_talk"]["kernel"][-1]
                row[f"exo_{name}_KT_lo"] = e["gate_talk"]["k_lo"][-1]
                row[f"exo_{name}_KA"] = e["gate_act"]["kernel"][-1]
                row[f"exo_{name}_KA_lo"] = e["gate_act"]["k_lo"][-1]
                row[f"exo_{name}_KA_hi"] = e["gate_act"]["k_hi"][-1]
        out.append(row)
    return pl.DataFrame(out, infer_schema_length=None)


def ivw(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    if not ok.any():
        return np.nan, np.nan, np.nan
    w = 1 / se[ok] ** 2
    m = (w * est[ok]).sum() / w.sum()
    s = 1 / np.sqrt(w.sum())
    return float(m), float(m - 1.96 * s), float(m + 1.96 * s)


def pooled_exo(T, name, col):
    out = {}
    for reg in ("I", "II", "III"):
        s = T.filter((pl.col("regime") == reg) & ~pl.col("ne43"))
        if f"exo_{name}_{col}" not in s.columns:
            continue
        s = s.filter(pl.col(f"exo_{name}_{col}").is_not_null())
        if len(s) == 0:
            continue
        se = (s[f"exo_{name}_{col}_hi"] - s[f"exo_{name}_{col}_lo"]).to_numpy() / 3.92
        out[reg] = dict(zip(("est", "lo", "hi"), ivw(s[f"exo_{name}_{col}"].to_numpy(), se))) | dict(
            n_units=len(s), n_pos=int((s[f"exo_{name}_{col}_lo"] > 0).sum()), n_pairs=int(s[f"exo_{name}_n"].sum()))
    return out


def bode(R):
    sums = {}
    for u, r in R.items():
        if u.startswith("NE43"):
            continue
        p = OUT / f"G{r['goal_no']:02d}" / f"{u}_welch.npz"
        if not p.exists():
            continue
        z = np.load(p)
        for which in ("A", "T"):
            key = (r["regime"], which)
            if f"{which}_Sxx" not in z.files:
                continue
            if key not in sums:
                sums[key] = dict(Sxx=z[f"{which}_Sxx"].copy(), Syy=z[f"{which}_Syy"].copy(), Sxy=z[f"{which}_Sxy"].copy(),
                                 n=int(z[f"{which}_n"]), f=z[f"{which}_f"])
            else:
                s = sums[key]
                s["Sxx"] += z[f"{which}_Sxx"]
                s["Syy"] += z[f"{which}_Syy"]
                s["Sxy"] += z[f"{which}_Sxy"]
                s["n"] += int(z[f"{which}_n"])
    out = {}
    for key, s in sums.items():
        summ, coh, H = L.welch_summary(s)
        out[f"{key[0]}_{key[1]}"] = dict(bands={cl: summ[i] for i, cl in enumerate(L.SWARM_CLASSES)}, n_segments=s["n"])
        s["coh"], s["H"] = coh, H
    return out, sums


def per_agent(R):
    rost = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet").select("agent", "name", "lab")
    acc = {}
    for u, r in R.items():
        if u.startswith("NE43"):
            continue
        for a, v in r.get("per_agent", {}).items():
            se = v["se"] if v.get("se") else (v["hi"] - v["lo"]) / 3.92
            acc.setdefault((r["regime"], int(a)), []).append((v["J1"], se, v["n"], v["talk_rate"]))
    rows = []
    for (reg, a), lst in acc.items():
        est, lo, hi = ivw([x[0] for x in lst], [x[1] for x in lst])
        rows.append(dict(regime=reg, agent=a, J1=est, lo=lo, hi=hi, n_units=len(lst), n_pairs=sum(x[2] for x in lst),
                         talk_rate=float(np.mean([x[3] for x in lst]))))
    df = pl.DataFrame(rows).join(rost, on="agent", how="left")
    return df


def main():
    R = load_all()
    T = unit_table(R)
    T.write_parquet(OUT / "unit_table.parquet")
    rep = T.filter(~pl.col("ne43"))
    S = {}
    for reg in ("I", "II", "III"):
        s = rep.filter(pl.col("regime") == reg)
        if len(s) == 0:
            continue
        S[reg] = dict(
            n_units=len(s), J1_pos=int((s["J1_lo"] > 0).sum()), J1_neg=int((s["J1_hi"] < 0).sum()),
            J1_median=float(s["J1"].median()), J1_pooled=ivw(s["J1"], s["J1_se"]),
            J1_rel_median=float((s["J1"] / s["base_talk"]).median()),
            onset1=int((s["onset_talk"] == 1).sum()), onset_other=int(((s["onset_talk"] != 1) & s["onset_talk"].is_not_null()).sum()),
            J2_neg=int((s["J2_hi"] < 0).sum()), J2_pos=int((s["J2_lo"] > 0).sum()),
            K6_pos=int((s["K6_lo"] > 0).sum()),
            J1act_pos=int((s["J1_act_lo"] > 0).sum()), J1act_neg=int((s["J1_act_hi"] < 0).sum()),
            J1act_median=float(s["J1_act"].median()),
            kappa_median=float(s["kappa"].median()), readout_q50_median=float(s["readout_q50"].median()),
            med_call_median=float(s["med_call_s"].median()),
            fFex_A_full_median=float(s["fFex_A_full"].median()), fFex_A_trim_median=float(s["fFex_A_trim"].median()),
            fFex_T_span_median=float(s["fFex_T_span"].median()),
            fFex_A_full_gt010=int((s["fFex_A_full"] > 0.10).sum()),
            S_A_full_median=float(s["S_A_full"].median()), rho_A_full_median=float(s["rho_A_full"].median()),
            rho_A_trim_median=float(s["rho_A_trim"].median()), S_T_span_median=float(s["S_T_span"].median()),
            rho_T_span_median=float(s["rho_T_span"].median()),
            fC_T_span_median=float(s["fC_T_span"].median()),
            fC_gt_fFexT=int((s["fC_T_span"] > s["fFex_T_span"]).sum()),
            flag_A_full_median=float(s["flag_A_full"].median()), flag_T_span_median=float(s["flag_T_span"].median()),
            J1_noreply_pos=int((s["J1_noreply_lo"] > 0).sum()),
            J1_W3_median=float(s["J1_W3"].median()), J1_highconf_median=float(s["J1_highconf"].median()),
            J1_ment_median=float(s["J1_ment"].median()) if s["J1_ment"].null_count() < len(s) else None,
            J1_noment_median=float(s["J1_noment"].median()),
            share_reply_median=float(s["share_reply"].median()),
            J1_work_pos=int((s["J1_work_lo"] > 0).sum()), J1_work_neg=int((s["J1_work_hi"] < 0).sum()),
            J1_work_median=float(s["J1_work"].median()),
            J1_idle_pos=int((s["J1_idle_lo"] > 0).sum()), J1_idle_neg=int((s["J1_idle_hi"] < 0).sum()),
            J1_idle_median=float(s["J1_idle"].median()),
            attr_A_full_edges_median=float(s["attr_A_full_edges"].median()), attr_A_full_rest_median=float(s["attr_A_full_rest"].median()),
            attr_A_trim_edges_median=float(s["attr_A_trim_edges"].median()), attr_A_trim_rest_median=float(s["attr_A_trim_rest"].median()),
            attr_T_span_edges_median=float(s["attr_T_span_edges"].median()), attr_T_span_rest_median=float(s["attr_T_span_rest"].median()),
            fC_T_span_ge09=int((s["fC_T_span"] >= 0.9).sum()), fC_T_span_lo_median=float(s["fC_T_span_lo"].median()),
        )
        # Part A metrics per class (units with inputs)
        for which in ("A", "T"):
            for cl in L.SWARM_CLASSES:
                c = f"fir{which}_{cl}_G30"
                if c not in s.columns:
                    continue
                ss = s.filter(pl.col(c).is_not_null())
                if len(ss) == 0:
                    continue
                S[reg][f"fir{which}_{cl}"] = dict(
                    n_units=len(ss), G30_median=float(ss[c].median()),
                    G30_pos=int((ss[f"{c}_lo"] > 0).sum()) if f"{c}_lo" in ss.columns else None,
                    G30_neg=int((ss[f"{c}_hi"] < 0).sum()) if f"{c}_hi" in ss.columns else None,
                    dead_median=float(ss[f"fir{which}_{cl}_dead"].median()),
                    corner_median=float(ss[f"fir{which}_{cl}_corner"].drop_nans().median()) if ss[f"fir{which}_{cl}_corner"].drop_nans().len() else None,
                    decay_median=float(ss[f"fir{which}_{cl}_decay"].drop_nans().median()) if ss[f"fir{which}_{cl}_decay"].drop_nans().len() else None,
                    pre_median=float(ss[f"fir{which}_{cl}_pre"].median()),
                    ring_median=float(ss[f"fir{which}_{cl}_ring"].drop_nans().median()) if ss[f"fir{which}_{cl}_ring"].drop_nans().len() else None,
                    coh_low_median=float(ss[f"fir{which}_{cl}_coh1"].median()), coh_fast_median=float(ss[f"fir{which}_{cl}_coh3"].median()),
                    gd_median=float(ss[f"fir{which}_{cl}_gd"].drop_nans().median()) if ss[f"fir{which}_{cl}_gd"].drop_nans().len() else None)
    exo = {}
    for name in ("human_target", "human_other", "nudge_target", "nudge_bystander", "pause"):
        exo[name] = dict(J1T=pooled_exo(rep, name, "J1T"), J1A=pooled_exo(rep, name, "J1A"),
                         KA=pooled_exo(rep, name, "KA"))
        oc = f"exo_{name}_onsetT"
        if oc in rep.columns:
            for reg in ("I", "II", "III"):
                ss = rep.filter((pl.col("regime") == reg) & pl.col(oc).is_not_null())
                exo[name].setdefault("onsets", {})[reg] = ss[oc].value_counts().sort(oc).rows() if len(ss) else []
    bd, sums = bode(R)
    pa = per_agent(R)
    pa.write_parquet(OUT / "per_agent.parquet")
    pa_s = {}
    for reg in ("I", "III"):
        p = pa.filter((pl.col("regime") == reg) & (pl.col("n_pairs") >= 1000))
        if len(p) == 0:
            continue
        se = (p["hi"] - p["lo"]) / 3.92
        Q = float((((p["J1"] - ivw(p["J1"], se)[0]) / se) ** 2).sum())
        pa_s[reg] = dict(n_agents=len(p), J1_median=float(p["J1"].median()), J1_q10=float(p["J1"].quantile(0.1)),
                         J1_q90=float(p["J1"].quantile(0.9)), n_pos=int((p["lo"] > 0).sum()), Q=Q, df=len(p) - 1,
                         by_lab={lab: float(g["J1"].median()) for lab, g in p.group_by("lab") if lab[0] is not None
                                 for lab in [lab[0]]} if False else
                         {str(k): float(v) for k, v in p.group_by("lab").agg(pl.col("J1").median()).iter_rows()},
                         rho_talk=float(np.corrcoef(p["J1"].to_numpy(), p["talk_rate"].to_numpy())[0, 1]))
    summary = dict(regimes=S, exo=exo, bode=bd, per_agent=pa_s)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
    print(json.dumps(summary, indent=1, default=float)[:12000])
    figures(T, sums, R)


def figures(T, sums, R):
    FIG.mkdir(parents=True, exist_ok=True)
    rep = T.filter(~pl.col("ne43")).sort("goal_no", "unit")
    # ---------- Fig 1: per-unit J1 (talk) and decomposition
    for tag, size in (("summary_obs", (7.0, 4.2)), ("summary_obs_col", (3.4, 3.3))):
        fig, axes = plt.subplots(2, 1, figsize=size, sharex=True)
        x = np.arange(len(rep))
        ax = axes[0]
        for reg, col in RCOL.items():
            s = rep.with_row_index("i").filter(pl.col("regime") == reg)
            if len(s) == 0:
                continue
            i = s["i"].to_numpy()
            ax.errorbar(i, s["J1"], yerr=[s["J1"] - s["J1_lo"], s["J1_hi"] - s["J1"]], fmt="o", ms=2.5, color=col, lw=0.7,
                        label=f"regime {reg}", capsize=0)
        ax.axhline(0, color=GRAY, lw=0.6)
        ax.set_ylabel("read-out jump $J_1$\n(talk, per message)", fontsize=6.5)
        ax.legend(fontsize=5.5, frameon=False, ncol=3, loc="upper left")
        ax.tick_params(labelsize=6)
        ax = axes[1]
        ax.plot(x, rep["fFex_A_full"], "s", ms=2.5, color=GRAY, label="activity field excess (full window)")
        ax.plot(x, rep["fC_T_span"].clip(-0.5, 1.5), "o", ms=2.5, color=ORANGE, label="talk coupling share $f_C$ (CF)")
        ax.plot(x, rep["fFex_T_span"].clip(-0.5, 1.5), "^", ms=2.5, color=BLUE, label="talk field excess")
        ax.axhline(0, color=GRAY, lw=0.6)
        ax.set_ylim(-0.5, 1.5)
        ax.set_ylabel("share of equal-time\nco-movement", fontsize=6.5)
        ax.legend(fontsize=5.2, frameon=False, loc="upper left", ncol=1)
        ax.tick_params(labelsize=6)
        gl = rep["goal_no"].to_numpy()
        ticks = [i for i in range(len(gl)) if i == 0 or gl[i] != gl[i - 1]]
        ax.set_xticks(ticks)
        ax.set_xticklabels([str(gl[i]) for i in ticks], fontsize=4.5 if tag.endswith("col") else 5.5, rotation=90)
        ax.set_xlabel("period unit (goal #)", fontsize=6.5)
        for a in axes:
            for sp in ("top", "right"):
                a.spines[sp].set_visible(False)
        fig.tight_layout()
        fig.savefig(FIG / f"{tag}.pdf")
        plt.close(fig)
    # ---------- Fig 2: Bode (pooled per regime): coherence and transfer phase for activity
    fig, axes = plt.subplots(2, 3, figsize=(7.0, 3.8), sharex=True)
    for j, reg in enumerate(("I", "II", "III")):
        s = sums.get((reg, "A"))
        if s is None:
            continue
        f = s["f"]
        sel = f > 0
        for cl, col in (("edge_on", INK), ("human", BLUE), ("nudge", ORANGE), ("platform", AQUA), ("pause", GRAY)):
            ci = L.SWARM_CLASSES.index(cl)
            if s["Sxx"][ci, sel].sum() <= 0:
                continue
            axes[0, j].plot(f[sel], s["coh"][ci, sel], color=col, lw=1, label=cl)
            ph = np.unwrap(np.angle(s["Sxy"][ci, sel]))
            axes[1, j].plot(f[sel], ph, color=col, lw=1)
        axes[0, j].set_title(f"regime {reg} (activity)", fontsize=7)
        axes[0, j].set_xscale("log")
        axes[1, j].set_xlabel("frequency (cycles/min)", fontsize=6.5)
        for a in axes[:, j]:
            a.tick_params(labelsize=6)
            for sp in ("top", "right"):
                a.spines[sp].set_visible(False)
    axes[0, 0].set_ylabel("coherence $\\gamma^2$", fontsize=6.5)
    axes[1, 0].set_ylabel("phase (rad)", fontsize=6.5)
    axes[0, 0].legend(fontsize=5.5, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "bode.pdf")
    plt.close(fig)
    # ---------- Fig 3: hop kernels (jumps) pooled per regime, peer and exogenous
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6))
    for reg, col in RCOL.items():
        s = rep.filter(pl.col("regime") == reg)
        if len(s) == 0:
            continue
        js, ses = [], []
        for u in s["unit"]:
            g = R[u]["gate_talk"]
            js.append(g["jumps"])
            ses.append((np.array(g["j_hi"]) - np.array(g["j_lo"])) / 3.92)
        js, ses = np.array(js, float), np.array(ses, float)
        pooled = [ivw(js[:, k], ses[:, k]) for k in range(js.shape[1])]
        m = np.array([p[0] for p in pooled])
        lo = np.array([p[1] for p in pooled])
        hi = np.array([p[2] for p in pooled])
        k = np.arange(1, len(m) + 1) + {"I": -0.15, "II": 0, "III": 0.15}[reg]
        axes[0].errorbar(k, m, yerr=[m - lo, hi - m], fmt="o-", ms=3, lw=1, color=col, label=f"regime {reg}", capsize=0)
    axes[0].axhline(0, color=GRAY, lw=0.6)
    axes[0].set_xlabel("boundary k (hop k vs hop k−1)", fontsize=6.5)
    axes[0].set_ylabel("jump in P(talk call)", fontsize=6.5)
    axes[0].set_title("peer message → recipient (pooled, IVW)", fontsize=7)
    axes[0].legend(fontsize=6, frameon=False)
    for name, col, mk in (("human_target", BLUE, "o"), ("human_other", AQUA, "s"), ("nudge_target", ORANGE, "^"), ("nudge_bystander", GRAY, "v")):
        for reg, dx in (("I", -0.1), ("III", 0.1)):
            s = rep.filter((pl.col("regime") == reg) & pl.col(f"exo_{name}_J1T").is_not_null()) if f"exo_{name}_J1T" in rep.columns else None
            if s is None or len(s) == 0:
                continue
            js, ses = [], []
            for u in s["unit"]:
                g = R[u]["exo"][name]["gate_talk"]
                js.append(g["jumps"])
                ses.append((np.array(g["j_hi"]) - np.array(g["j_lo"])) / 3.92)
            js, ses = np.array(js, float), np.array(ses, float)
            pooled = [ivw(js[:, k], ses[:, k]) for k in range(js.shape[1])]
            m = np.array([p[0] for p in pooled])
            lo = np.array([p[1] for p in pooled])
            hi = np.array([p[2] for p in pooled])
            k = np.arange(1, len(m) + 1) + dx
            axes[1].errorbar(k, m, yerr=[m - lo, hi - m], fmt=mk + ("-" if reg == "III" else "--"), ms=3, lw=0.9, color=col,
                             label=f"{name.replace('_', ' ')} ({reg})", capsize=0)
    axes[1].axhline(0, color=GRAY, lw=0.6)
    axes[1].set_xlabel("boundary k", fontsize=6.5)
    axes[1].set_title("exogenous input → recipient (talk)", fontsize=7)
    axes[1].legend(fontsize=5, frameon=False, ncol=2)
    for a in axes:
        a.tick_params(labelsize=6)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "hop_kernels.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
