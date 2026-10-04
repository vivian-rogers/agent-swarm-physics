"""H50 period-native tests (layer 2): NE43 (lever switch-offs), G51 (human input: field vs relay), NE14 (regime I vs III:
message-triggered calls), G38 (pause gates). Reads the scheme units and the replication outputs.

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/native.py [--only NE43,G51,NE14,G38]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h50lib as L  # noqa: E402
from build import load_unit  # noqa: E402
from run_unit import tolist  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"


def unit(u):
    U = load_unit(OUT / "units" / f"{u}.npz")
    U["N"] = int(U["N"])
    return U


def res(u):
    for p in OUT.glob(f"*/{u}.json"):
        return json.loads(p.read_text())
    return None


def onsets(U):
    """Per day: agents' first-call offsets from the window start (s), and whether each agent's first call precedes the
    first peer message visible to it that day."""
    c, m, mp = U["calls"], U["msgs"], U["mpairs"]
    rows = []
    for d in range(len(U["day_t0"])):
        ws = U["day_t0"][d] + 900
        sel = c["day"] == d
        ags = np.unique(c["agent"][sel])
        pm = mp["msg"][m["day"][mp["msg"]] == d]
        pr = mp["rec"][m["day"][mp["msg"]] == d]
        for a in ags:
            tc0 = c["tc"][sel & (c["agent"] == a)].min()
            vis = m["t"][pm[pr == a]]
            tvis = vis.min() if len(vis) else np.inf
            rows.append(dict(day=d, agent=int(a), off_s=float(tc0 - ws), before_first_peer=bool(tc0 < tvis),
                             first_peer_off_s=float(tvis - ws) if np.isfinite(tvis) else None))
    df = pl.DataFrame(rows)
    per_day = df.group_by("day").agg(pl.col("off_s").quantile(0.25).alias("q25"), pl.col("off_s").quantile(0.75).alias("q75"),
                                     pl.col("off_s").median().alias("med"), pl.col("before_first_peer").mean().alias("share_before"),
                                     pl.len().alias("n"))
    per_day = per_day.with_columns((pl.col("q75") - pl.col("q25")).alias("iqr"))
    return df, per_day


# ============================================================================== NE43
def ne43():
    out = {}
    for seg in ("NE43A", "NE43B", "NE43C"):
        U = unit(seg)
        r = res(seg)
        df, pdy = onsets(U)
        med_int = L.median_call_interval(U)
        out[seg] = dict(
            days=int(len(U["day_t0"])), N=U["N"],
            J1_talk=[r["gate_talk"]["jumps"][0], r["gate_talk"]["j_lo"][0], r["gate_talk"]["j_hi"][0]],
            J1_act=[r["gate_act"]["jumps"][0], r["gate_act"]["j_lo"][0], r["gate_act"]["j_hi"][0]],
            rho_trim=r["c1"]["A_trim"]["rho_raw"], S_trim=r["c1"]["A_trim"]["S_raw"],
            rho_span=r["c1"]["A_span"]["rho_raw"], rho_full=r["c1"]["A_full"]["rho_raw"],
            fF_A_full=r["c1"]["A_full"]["f_F"], fF_A_full_null=r["c1"]["A_full"]["f_F_null"],
            fF_A_trim=r["c1"]["A_trim"]["f_F"], fF_A_trim_no_nudge=r["c1_f_F_no_nudge"]["A_trim"],
            fF_A_span=r["c1"]["A_span"]["f_F"], fF_A_span_no_nudge=r["c1_f_F_no_nudge"]["A_span"],
            fF_T_span=r["c1"]["T_span"]["f_F"], fF_T_span_no_nudge=r["c1_f_F_no_nudge"]["T_span"],
            onset_iqr_s_median=float(pdy["iqr"].median()), onset_iqr_cc=float(pdy["iqr"].median() / med_int),
            onset_med_s=float(pdy["med"].median()), share_first_before_peer=float(df["before_first_peer"].mean()),
            med_call_s=med_int,
            edge_G30_A=r["fir"]["A"]["edge_on"].get("G30"), edge_G30_A_ci=[r["fir"]["A"]["edge_on"].get("G30_lo"), r["fir"]["A"]["edge_on"].get("G30_hi")],
            nudge_target=dict(n=r["exo"]["nudge_target"]["n"], onset_talk=r["exo"]["nudge_target"].get("onset_talk"),
                              onset_act=r["exo"]["nudge_target"].get("onset_act"),
                              J_talk=r["exo"]["nudge_target"].get("gate_talk", {}).get("jumps"),
                              J_talk_lo=r["exo"]["nudge_target"].get("gate_talk", {}).get("j_lo"),
                              J_act=r["exo"]["nudge_target"].get("gate_act", {}).get("jumps"),
                              J_act_lo=r["exo"]["nudge_target"].get("gate_act", {}).get("j_lo"),
                              J_act_hi=r["exo"]["nudge_target"].get("gate_act", {}).get("j_hi")),
            fir_nudge_A=r["fir"]["A"]["nudge"], fir_nudge_T=r["fir"]["T"]["nudge"],
            cf_talk_span=r["cf_talk"]["span_k1"]["f_C"])
    B, C, A = out["NE43B"], out["NE43C"], out["NE43A"]
    out["checks"] = dict(
        i_nudge_share_trim=B["fF_A_trim"] - B["fF_A_trim_no_nudge"],
        i_nudge_share_span=B["fF_A_span"] - B["fF_A_span_no_nudge"],
        i_nudge_share_talk=B["fF_T_span"] - B["fF_T_span_no_nudge"],
        ii_onset_iqr_ratio_B_over_A=B["onset_iqr_s_median"] / A["onset_iqr_s_median"] if A["onset_iqr_s_median"] else None,
        iii_J1_C_over_B=C["J1_talk"][0] / B["J1_talk"][0],
        iii_C_in_B_CI=bool(B["J1_talk"][1] <= C["J1_talk"][0] <= B["J1_talk"][2]),
        iv_rho_trim_C_over_B=C["rho_trim"] / B["rho_trim"] if B["rho_trim"] else None,
    )
    return out


# ============================================================================== G51 human input
G51_UNITS = ["51a", "51b", "51c", "51d", "51e", "51f", "51g", "51h", "51i", "51j", "51k", "51l"]


def g51():
    st = {k: [] for k in ("target", "bystander", "plain", "reply_by", "peer")}
    counts = {k: 0 for k in st}
    nmsg = dict(mention=0, plain=0, replied=0)
    reply_lat = []
    for u in G51_UNITS:
        U = unit(u)
        c, m, mp, inp, ip = U["calls"], U["msgs"], U["mpairs"], U["inputs"], U["ipairs"]
        keys = L.call_keys(U)
        W = 1.5 * L.median_call_interval(U)
        yT = c["talk"].astype(float)
        kp = inp["kind"][ip["inp"]]
        hum = kp == L.K["human"]
        named = inp["n_targets"][ip["inp"]] > 0
        t_p, d_p = inp["t"][ip["inp"]], inp["day"][ip["inp"]]
        sets = dict(target=hum & ip["tgt"], bystander=hum & named & ~ip["tgt"], plain=hum & ~named)
        for k, sel in sets.items():
            if sel.sum() == 0:
                st[k].append(L.gate_stats(U, keys, t_p[:0], d_p[:0], ip["rec"][:0], yT, K=4, W=W))
                continue
            st[k].append(L.gate_stats(U, keys, t_p[sel], d_p[sel], ip["rec"][sel], yT, K=4, W=W))
            counts[k] += int(sel.sum())
        # relay: each named human message -> its target's first chat message within 30 min; source = that reply,
        # recipients = the human message's non-target recipients (bystanders) who can see the reply
        hids = np.where(inp["kind"] == L.K["human"])[0]
        te, de, rr = [], [], []
        for h in hids:
            recs = ip["rec"][ip["inp"] == h]
            tg = ip["rec"][(ip["inp"] == h) & ip["tgt"]]
            if inp["n_targets"][h] > 0:
                nmsg["mention"] += 1
            else:
                nmsg["plain"] += 1
                continue
            if len(tg) == 0:
                continue
            th = inp["t"][h]
            cand = np.where(np.isin(m["sender"], tg) & (m["t"] > th) & (m["t"] < th + 1800))[0]
            if len(cand) == 0:
                continue
            j = cand[np.argmin(m["t"][cand])]
            nmsg["replied"] += 1
            reply_lat.append(float(m["t"][j] - th))
            vis = mp["rec"][mp["msg"] == j]
            by = np.setdiff1d(np.intersect1d(vis, recs), tg)
            for b in by:
                te.append(m["t"][j])
                de.append(m["day"][j])
                rr.append(b)
        te, de, rr = np.asarray(te, float), np.asarray(de, np.int64), np.asarray(rr, np.int64)
        st["reply_by"].append(L.gate_stats(U, keys, te, de, rr, yT, K=4, W=W))
        counts["reply_by"] += len(te)
        # generic peer gate (pooled #51)
        pe, pd_, pr = m["t"][mp["msg"]], m["day"][mp["msg"]], mp["rec"]
        st["peer"].append(L.gate_stats(U, keys, pe, pd_, pr, yT, K=4, W=W))
        counts["peer"] += len(pe)
    out = dict(counts=counts, messages=nmsg, reply_latency_s=dict(q25=float(np.percentile(reply_lat, 25)),
                                                                 q50=float(np.median(reply_lat)),
                                                                 q75=float(np.percentile(reply_lat, 75))) if reply_lat else None)
    for k, lst in st.items():
        out[k] = L.kernel_from_stats(L.concat_stats(lst))
    out["ratio_bystander_target"] = float(out["bystander"]["jumps"][0] / out["target"]["jumps"][0]) if out["target"]["jumps"][0] else None
    return out


# ============================================================================== NE14 regime I vs III
def ne14():
    u = pl.read_parquet(OUT / "units.parquet").filter(pl.col("eligible") & (pl.col("kind") == "period_unit"))
    per_unit = []
    pooled = {}
    for r in u.iter_rows(named=True):
        U = unit(r["unit"])
        m, mp, inp, ip = U["msgs"], U["mpairs"], U["inputs"], U["ipairs"]
        keys = L.call_keys(U)
        te = np.r_[m["t"][mp["msg"]], inp["t"][ip["inp"]]]
        rec = np.r_[mp["rec"], ip["rec"]]
        gt = L.gap_trigger(U, keys, te, rec)
        ok = gt["ok"]
        row = dict(unit=r["unit"], regime=r["regime"], goal_no=r["goal_no"])
        for lab, sel in (("all", ok), ("chat", ok & gt["chat"]), ("wait", ok & gt["wait"]), ("pause", ok & gt["pause"]),
                         ("busy_gap", ok & ~gt["wait"] & ~gt["pause"])):
            n = int(sel.sum())
            row[f"n_{lab}"] = n
            row[f"ratio_{lab}"] = float(gt["real"][sel].mean() / gt["exp"][sel].mean()) if n >= 30 else None
            row[f"real_{lab}"] = float(gt["real"][sel].mean()) if n else None
            row[f"exp_{lab}"] = float(gt["exp"][sel].mean()) if n else None
            key = (r["regime"], lab)
            pooled.setdefault(key, [[], [], []])
            pooled[key][0].append(gt["real"][sel])
            pooled[key][1].append(gt["exp"][sel])
            pooled[key][2].append(gt["day"][sel] + 1000 * len(per_unit))
        rr = res(r["unit"])
        if rr:
            row.update(J1=rr["gate_talk"]["jumps"][0], J1_lo=rr["gate_talk"]["j_lo"][0], J1_hi=rr["gate_talk"]["j_hi"][0],
                       kappa=rr["gate_k1"]["talk"].get("kappa"), fFex_A_full=rr["c1"]["A_full"]["f_F"] - rr["c1"]["A_full"]["f_F_null"],
                       fF_A_full=rr["c1"]["A_full"]["f_F"], fC_T=rr["cf_talk"]["span_k1"]["f_C"],
                       talk_rate=rr["talk_rate"], med_call_s=rr["med_call_s"], N=rr["N"], n_days=rr["n_days"])
        per_unit.append(row)
    rng = np.random.default_rng(14)
    pool = {}
    for (reg, lab), (a, b, d) in pooled.items():
        a, b, d = np.concatenate(a), np.concatenate(b), np.concatenate(d)
        if len(a) < 30:
            continue
        ud = np.unique(d)
        bs = []
        for _ in range(400):
            w = np.bincount(np.searchsorted(ud, rng.choice(ud, len(ud))), minlength=len(ud))
            ww = w[np.searchsorted(ud, d)]
            bs.append((ww * a).sum() / (ww * b).sum())
        pool[f"{reg}_{lab}"] = dict(n=int(len(a)), ratio=float(a.mean() / b.mean()), lo=float(np.percentile(bs, 2.5)),
                                    hi=float(np.percentile(bs, 97.5)), real=float(a.mean()), exp=float(b.mean()))
    df = pl.DataFrame(per_unit)
    summ = {}
    for reg in ("I", "II", "III"):
        s = df.filter(pl.col("regime") == reg)
        if len(s) == 0:
            continue
        summ[reg] = dict(n_units=len(s), J1_pos=int((s["J1_lo"] > 0).sum()), J1_neg=int((s["J1_hi"] < 0).sum()),
                         J1_median=float(s["J1"].median()), kappa_median=float(s["kappa"].median()),
                         fFex_A_full_median=float(s["fFex_A_full"].median()), fC_T_median=float(s["fC_T"].median()),
                         talk_rate_median=float(s["talk_rate"].median()))
    from scipy.stats import mannwhitneyu
    a, b = df.filter(pl.col("regime") == "III")["fFex_A_full"].to_numpy(), df.filter(pl.col("regime") == "I")["fFex_A_full"].to_numpy()
    k3, k1 = df.filter(pl.col("regime") == "III")["kappa"].to_numpy(), df.filter(pl.col("regime") == "I")["kappa"].to_numpy()
    summ["tests"] = dict(fFex_III_minus_I=float(np.median(a) - np.median(b)), fFex_MW_p=float(mannwhitneyu(a, b).pvalue),
                         kappa_I_minus_III=float(np.nanmedian(k1) - np.nanmedian(k3)),
                         kappa_MW_p=float(mannwhitneyu(k1[np.isfinite(k1)], k3[np.isfinite(k3)]).pvalue))
    df.write_parquet(OUT / "NE14" / "per_unit.parquet") if (OUT / "NE14").exists() else None
    return dict(per_unit=per_unit, pooled=pool, summary=summ)


# ============================================================================== G38 pause gates
G38_UNITS = ["38a", "38b", "38c", "38d", "38e"]


def g38():
    on_rows, stop_rows = [], []
    st_pause = []
    for u in G38_UNITS:
        U = unit(u)
        c, m, mp, inp, ip = U["calls"], U["msgs"], U["mpairs"], U["inputs"], U["ipairs"]
        keys = L.call_keys(U)
        W = 1.5 * L.median_call_interval(U)
        df, pdy = onsets(U)
        df = df.with_columns(pl.lit(u).alias("unit"))
        on_rows.append(df)
        # pause bookends
        pids = np.where(inp["kind"] == L.K["pause"])[0]
        for p in pids:
            tp, d = inp["t"][p], inp["day"][p]
            for a in np.unique(c["agent"][c["day"] == d]):
                sel = np.where((c["agent"] == a) & (c["day"] == d))[0]
                tcs = c["tc"][sel]
                after = sel[tcs > tp]
                last_all = sel[-1]
                if len(after) == 0:
                    stop_rows.append(dict(unit=u, day=int(d), agent=int(a), read=False,
                                          last_end_off_s=float(c["tl"][last_all] - tp),
                                          last_start_off_s=float(c["tc"][last_all] - tp),
                                          last_was_idle=bool(~c["act"][last_all])))
                    continue
                r1 = after[0]
                last = sel[-1]
                n_after = int(len(after))
                # peer messages the agent reads after the pause read-out
                pm = mp["msg"][(mp["rec"] == a)]
                tmsg = m["t"][pm]
                n_peer_after = int(((tmsg > c["tc"][r1]) & (m["day"][pm] == d)).sum())
                stop_rows.append(dict(unit=u, day=int(d), agent=int(a), read=True, readout_delay_s=float(c["tc"][r1] - tp),
                                      last_start_off_s=float(c["tc"][last] - tp), last_was_idle=bool(~c["act"][last]),
                                      n_calls_after=n_after, n_peer_after=n_peer_after,
                                      last_end_off_s=float(c["tl"][last] - tp), talk_at_readout=bool(c["talk"][r1]),
                                      talk_after=int(c["talk"][after].sum())))
        sel = (inp["kind"][ip["inp"]] == L.K["pause"])
        st_pause.append(L.gate_stats(U, keys, inp["t"][ip["inp"]][sel], inp["day"][ip["inp"]][sel], ip["rec"][sel],
                                     c["talk"].astype(float), K=2, W=W))
    on = pl.concat(on_rows)
    stp = pl.DataFrame(stop_rows)
    rd = stp.filter(pl.col("read"))
    from scipy.stats import spearmanr
    rho = spearmanr(rd["n_peer_after"].to_numpy(), rd["n_calls_after"].to_numpy()) if len(rd) >= 5 else None
    # per-day dispersion of every agent's last-call end, relative to the pause message
    disp = stp.group_by("unit", "day").agg((pl.col("last_end_off_s").quantile(0.75) - pl.col("last_end_off_s").quantile(0.25)).alias("iqr"),
                                           pl.col("last_end_off_s").median().alias("med"),
                                           (pl.col("last_end_off_s").quantile(0.9) - pl.col("last_end_off_s").quantile(0.1)).alias("w80"))
    stp.write_parquet(OUT / "G38" / "pause_stops.parquet")
    out = dict(
        resume=dict(n_agent_days=len(on), share_first_before_peer=float(on["before_first_peer"].mean()),
                    onset_off_s_median=float(on["off_s"].median()),
                    onset_iqr_s_median=float(on.group_by("unit", "day").agg((pl.col("off_s").quantile(0.75) - pl.col("off_s").quantile(0.25)).alias("iqr"))["iqr"].median())),
        pause=dict(n_agent_days=len(stp), share_read=float(stp["read"].mean()),
                   readout_delay_s_median=float(rd["readout_delay_s"].median()),
                   n_calls_after_median=float(rd["n_calls_after"].median()),
                   n_calls_after_q90=float(rd["n_calls_after"].quantile(0.9)),
                   spearman_peer_after_vs_calls_after=float(rho.statistic) if rho else None,
                   spearman_p=float(rho.pvalue) if rho else None,
                   last_end_iqr_s_median=float(disp["iqr"].median()), last_end_w80_s_median=float(disp["w80"].median()),
                   last_end_med_s=float(disp["med"].median()),
                   share_last_end_before_msg=float((stp["last_end_off_s"] < 0).mean()),
                   share_last_end_within_120s=float((stp["last_end_off_s"].abs() <= 120).mean()),
                   last_end_off_q=[float(x) for x in stp["last_end_off_s"].quantile([0.1, 0.25, 0.5, 0.75, 0.9]) ] if False else
                   [float(stp["last_end_off_s"].quantile(q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)],
                   share_last_call_idle=float(stp["last_was_idle"].mean()),
                   talk_at_readout=float(rd["talk_at_readout"].mean()) if len(rd) else None),
        pause_gate=L.kernel_from_stats(L.concat_stats(st_pause)),
    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="NE43,G51,NE14,G38")
    args = ap.parse_args()
    fns = dict(NE43=ne43, G51=g51, NE14=ne14, G38=g38)
    for k in args.only.split(","):
        (OUT / k).mkdir(parents=True, exist_ok=True)
        r = fns[k]()
        (OUT / k / "native.json").write_text(json.dumps(tolist(r), indent=1, default=float))
        print(k, json.dumps(tolist({kk: vv for kk, vv in r.items() if kk != "per_unit"}), default=float)[:3000])


if __name__ == "__main__":
    main()
