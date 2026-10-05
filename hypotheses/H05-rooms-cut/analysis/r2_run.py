"""H05 round 2 on real non-reserved data (2026-10-05): R1 (rooms vs shared artifacts), R2 (attention reallocation),
R3 (leak conductance). Predictions and amendments A1-A4: card, "Round 2". Estimators: r2_common.py, r2_leak.py
(validated in r2_synthetic.py first).

Usage: H05_DATA=r1b uv run python hypotheses/H05-rooms-cut/analysis/r2_run.py
Output: data/processed/H05-rooms-cut/r2/r2_results.json, r1_pair_days.parquet, r3_first_exposures.parquet,
_provenance.json. No text is read or written.
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("H05_DATA", "r1b")
import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2_common as C  # noqa: E402
import r2_leak as L  # noqa: E402
from pairs import twfe  # noqa: E402

RNG = np.random.default_rng(20261005)
NPERM = 2000
NBOOT = 2000


def goal_of(ad):
    return dict(ad.group_by("pt_date").agg(pl.col("goal_no").first()).iter_rows())


def lab39(ad):
    d39 = ad.filter(pl.col("goal_no") == 39)
    m = d39.group_by("agent", "room_mode").len().sort("len", descending=True).group_by("agent").agg(pl.col("room_mode").first())
    return {int(a): int(r) for a, r in m.iter_rows() if int(a) != 10}


def boot_mean_diff(a, b, n=NBOOT):
    a, b = np.asarray(a, float), np.asarray(b, float)
    bs = [RNG.choice(a, len(a)).mean() - RNG.choice(b, len(b)).mean() for _ in range(n)]
    return [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


# ================================================================================================ R1
def run_r1(ad):
    rooms = C.room_dict(ad)
    goal = goal_of(ad)
    wc = C.load_commits()
    mats = C.commit_mats(wc, ad)
    pdd = C.commit_pair_days(mats, rooms)
    pdd = pdd.with_columns(pl.col("pt_date").replace_strict(goal, return_dtype=pl.Int64).alias("goal_no"))
    C.OUT.mkdir(parents=True, exist_ok=True)
    pdd.write_parquet(C.OUT / "r1_pair_days.parquet", compression="zstd")
    out = {"n_pair_days": pdd.height}
    # P1: co-edit share within vs cross per two-room window
    p1 = {}
    for g in C.TWO_ROOM_GOALS:
        t = pdd.filter(pl.col("goal_no") == g)
        w = t.filter(pl.col("same_room")); x = t.filter(~pl.col("same_room"))
        sw = float(w["coedit"].mean()) if w.height else None
        sx = float(x["coedit"].mean()) if x.height else None
        p1[str(g)] = {"within_share": sw, "cross_share": sx, "n_within": w.height, "n_cross": x.height,
                      "ratio_cross_within": (sx / sw) if (sw and sx is not None) else None,
                      "pass": bool(sx is not None and sw and sx <= 0.5 * sw)}
    out["P1_windows"] = p1
    out["P1_n_pass"] = int(sum(v["pass"] for v in p1.values()))
    lab = lab39(ad)
    cut = pdd.filter(pl.col("i").is_in(list(lab)) & pl.col("j").is_in(list(lab)))
    cut = cut.filter(pl.struct("i", "j").map_elements(lambda s: lab[s["i"]] != lab[s["j"]], return_dtype=pl.Boolean))
    ne42 = {g: float(cut.filter(pl.col("goal_no") == g)["coedit"].mean()) for g in (39, 40, 41)}
    out["P1_NE42_cut_pairs_coedit_share"] = ne42
    out["P1_NE42_drop_frac"] = 1 - ne42[41] / ne42[40] if ne42[40] else None
    # P2: partition contrast on cross-room pair-days
    e = pdd.filter(pl.col("E_x").is_not_null())
    e = e.with_columns(pl.Series("ter", C.tertile(np.minimum(e["n_i"], e["n_j"]).to_numpy().astype(float))))
    out["P2_cross"] = C.strata_contrast(e.filter(~pl.col("same_room")), "E_x", "coedit", ["goal_no", "ter"], NPERM, RNG)
    out["P2_within"] = C.strata_contrast(e.filter(pl.col("same_room")), "E_x", "coedit", ["goal_no", "ter"], NPERM, RNG)
    out["P2_cross_by_goal"] = {str(g): {"n_coedit": int(t.filter(pl.col("coedit")).height), "n": t.height,
                                        "mean_coedit": t.filter(pl.col("coedit"))["E_x"].mean(),
                                        "mean_other": t.filter(~pl.col("coedit"))["E_x"].mean()}
                               for (g,), t in e.filter(~pl.col("same_room")).group_by("goal_no")}
    # P3: #focus
    f = pdd.filter(pl.col("goal_no") == 51)
    arm = pl.col("i").is_in(list(C.FOCUS)) ^ pl.col("j").is_in(list(C.FOCUS))
    both = pl.col("i").is_in(list(C.FOCUS)) & pl.col("j").is_in(list(C.FOCUS))
    pre = (pl.col("pt_date") >= C.FOCUS_PRE[0]) & (pl.col("pt_date") <= C.FOCUS_PRE[1])
    dur = (pl.col("pt_date") >= C.FOCUS_DUR[0]) & (pl.col("pt_date") <= C.FOCUS_DUR[1])
    p3 = {}
    for nm, sel in (("pre", pre), ("during", dur)):
        p3[nm] = {"cut_arm_coedit_share": float(f.filter(sel & arm)["coedit"].mean()),
                  "stay_coedit_share": float(f.filter(sel & ~arm & ~both)["coedit"].mean()),
                  "cut_arm_pairdays": f.filter(sel & arm).height,
                  "cut_arm_E_x_mean": f.filter(sel & arm)["E_x"].mean(), "cut_arm_E_x_n": f.filter(sel & arm)["E_x"].drop_nulls().len(),
                  "stay_E_x_mean": f.filter(sel & ~arm & ~both)["E_x"].mean(), "stay_E_x_n": f.filter(sel & ~arm & ~both)["E_x"].drop_nulls().len()}
    p3["cut_arm_coedit_ratio_during_pre"] = (p3["during"]["cut_arm_coedit_share"] / p3["pre"]["cut_arm_coedit_share"]
                                             if p3["pre"]["cut_arm_coedit_share"] else None)
    # DiD of E_x with a pair-cluster bootstrap
    def pair_means(sel):
        return f.filter(sel).filter(pl.col("E_x").is_not_null()).group_by("i", "j").agg(pl.col("E_x").mean())
    ca_pre, ca_dur = pair_means(pre & arm), pair_means(dur & arm)
    st_pre, st_dur = pair_means(pre & ~arm & ~both), pair_means(dur & ~arm & ~both)
    if min(ca_pre.height, ca_dur.height, st_pre.height, st_dur.height) > 0:
        did = (ca_dur["E_x"].mean() - ca_pre["E_x"].mean()) - (st_dur["E_x"].mean() - st_pre["E_x"].mean())
        bs = []
        for _ in range(NBOOT):
            bs.append((RNG.choice(ca_dur["E_x"].to_numpy(), ca_dur.height).mean() - RNG.choice(ca_pre["E_x"].to_numpy(), ca_pre.height).mean())
                      - (RNG.choice(st_dur["E_x"].to_numpy(), st_dur.height).mean() - RNG.choice(st_pre["E_x"].to_numpy(), st_pre.height).mean()))
        p3["E_x_DiD"] = float(did)
        p3["E_x_DiD_ci95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        p3["n_pairs"] = {"cut_pre": ca_pre.height, "cut_during": ca_dur.height, "stay_pre": st_pre.height, "stay_during": st_dur.height}
    out["P3_focus"] = p3
    # P4: cross-room talk kappa_x on co-edit vs non-co-edit pair-days
    tk = pl.read_parquet(C.R1B / "pair_day_bin1.parquet").filter(pl.col("spin") == "talk").select(
        "pt_date", pl.col("i").cast(pl.Int16), pl.col("j").cast(pl.Int16), "kappa_x", "act_i", "act_j")
    q = pdd.select("pt_date", "i", "j", "same_room", "coedit", "goal_no").join(tk, on=["pt_date", "i", "j"])
    q = q.filter(~pl.col("same_room") & pl.col("kappa_x").is_not_null())
    q = q.with_columns(pl.Series("ter", C.tertile(np.minimum(q["act_i"], q["act_j"]).to_numpy().astype(float))))
    r = C.strata_contrast(q, "kappa_x", "coedit", ["goal_no", "ter"], NPERM, RNG)
    r["p_perm_two_sided"] = min(1.0, 2 * min(r["p_perm_one_sided"], 1 - r["p_perm_one_sided"] + 1 / (NPERM + 1))) if r.get("p_perm_one_sided") is not None else None
    out["P4_talk_kappa_cross"] = r
    return out


# ================================================================================================ R2
def run_r2(ad):
    out = {}
    nroom = {(d, int(a)): int(n) for d, a, n in ad.select("pt_date", "agent", "n_room").iter_rows()}
    rmode = {(d, int(a)): int(r) for d, a, r in ad.select("pt_date", "agent", "room_mode").iter_rows()}
    for mask in ("none", "trim"):
        p = C.R1B / ("" if mask == "none" else "trim") / "pair_day_bin1.parquet"
        pdf = pl.read_parquet(p).filter((pl.col("spin") == "talk") & (pl.col("regime") == "III") & (pl.col("coloc") >= 0.75)
                                        & (pl.col("known") > 0.5))
        C.assert_no_reserved(pdf["pt_date"].unique().to_list())
        kr = [(nroom[(d, int(i))] - 1) if rmode.get((d, int(i))) == rmode.get((d, int(j))) and (d, int(i)) in nroom else None
              for d, i, j in pdf.select("pt_date", "i", "j").iter_rows()]
        pdf = pdf.with_columns(pl.Series("kroom", kr, dtype=pl.Float64))
        res = C.r2_kappa_twfe(pdf, twfe)
        b = res.get("beta_hat")
        res["consistent_with"] = {"beta0": bool(b is not None and -0.43 <= b <= 0.24),
                                  "beta045": bool(b is not None and 0.13 <= b <= 0.71),
                                  "beta1": bool(b is not None and 1.98 <= b <= 2.52)}
        res["P1_pass_A2"] = bool(res["consistent_with"]["beta045"] and not res["consistent_with"]["beta0"])
        # without #51 (two-room era only), information
        res["two_room_era_only"] = C.r2_kappa_twfe(pdf.filter(pl.col("goal_no") <= 44), twfe)
        out[f"P1_kappa_{mask}"] = res
    # P2: ledger uptake
    u = C.uptake_pairdays(ad)
    out["P2_uptake_mention"] = C.uptake_fit(u, "y")
    out["P2_uptake_reply"] = C.uptake_fit(u, "y_reply")
    out["P2_uptake_mention_two_room_era"] = C.uptake_fit(u.filter(pl.col("goal_no") <= 44), "y")
    out["P2_uptake_mention_51"] = C.uptake_fit(u.filter(pl.col("goal_no") == 51), "y")
    # P3: NE42 levels (stay pairs together in #39, #40, #41)
    goal = goal_of(ad)
    lab = lab39(ad)
    t = pl.read_parquet(C.R1B / "pair_day_bin1.parquet").filter((pl.col("spin") == "talk") & pl.col("i").is_in(list(lab)) & pl.col("j").is_in(list(lab)))
    per = {g: t.filter(pl.col("goal_no") == g).group_by("i", "j").agg(pl.col("kappa_x").mean(), pl.col("coloc").mean()) for g in (39, 40, 41)}
    m = per[39].join(per[40], on=["i", "j"], suffix="_40").join(per[41], on=["i", "j"], suffix="_41")
    m = m.filter(pl.struct("i", "j").map_elements(lambda s: lab[s["i"]] == lab[s["j"]], return_dtype=pl.Boolean)
                 & (pl.col("coloc") >= 0.75) & (pl.col("coloc_40") >= 0.75) & (pl.col("coloc_41") >= 0.75)).drop_nulls()
    k39, k40, k41 = (m[c].to_numpy() for c in ("kappa_x", "kappa_x_40", "kappa_x_41"))
    best = np.array([lab[int(i)] == 2 for i in m["i"].to_list()])
    f_merge = np.where(best, (13 / 3) ** -0.45, (13 / 10) ** -0.45)
    stat = f_merge * k39 - k40          # excess merge drop beyond dilution
    bs = np.array([stat[RNG.integers(0, len(stat), len(stat))].mean() for _ in range(NBOOT)])
    s41 = k41 - k39
    bs41 = np.array([s41[RNG.integers(0, len(s41), len(s41))].mean() for _ in range(NBOOT)])
    out["P3_NE42"] = {"n_stay_pairs": int(len(stat)), "kappa_39": float(k39.mean()), "kappa_40": float(k40.mean()),
                      "kappa_41": float(k41.mean()), "pred_40_dilution": float((f_merge * k39).mean()),
                      "excess_merge_drop": float(stat.mean()), "excess_merge_drop_se": float(bs.std()),
                      "excess_merge_drop_ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                      "fails": bool(stat.mean() > 2 * bs.std()),
                      "k41_minus_k39": float(s41.mean()), "k41_minus_k39_ci95": [float(np.percentile(bs41, 2.5)), float(np.percentile(bs41, 97.5))]}
    # NE15 arithmetic (published C5 numbers; no data read)
    out["NE15_arithmetic"] = {"published_J_in_pre": 0.023, "published_J_in_pre_ci95": [-0.013, 0.059],
                              "published_J_in_post": 0.139, "published_J_in_post_ci95": [0.06, 0.35],
                              "f_beta045": [1.18, 1.23], "f_beta1": [1.54, 1.69],
                              "pred_post_beta045": [0.023 * 1.18, 0.023 * 1.23], "pred_post_beta045_upper_pre": 0.059 * 1.23,
                              "share_of_log_rise_beta045": [0.09, 0.12], "share_of_log_rise_beta1": [0.24, 0.29]}
    return out


# ================================================================================================ R3
def run_r3(ad):
    inp = L.build_inputs(ad)
    fe = L.first_exposures(inp["cand"], inp["exp"])
    fe.write_parquet(C.OUT / "r3_first_exposures.parquet", compression="zstd")
    out = {"n_items": int(fe["artifact"].n_unique()), "n_candidates_cross": int(fe["cross"].sum()),
           "n_candidates_within": int((~fe["cross"]).sum()),
           "items_by_segment": dict(fe.group_by("seg").agg(pl.col("artifact").n_unique()).iter_rows())}
    for ch in ("search", "output"):
        out[f"P1_{ch}_cross"] = L.conductance(fe, ch, True, RNG, n_boot=NBOOT)
    out["chat_within"] = L.conductance(fe, "chat", False, RNG, n_boot=NBOOT)
    out["chat_cross_relay"] = L.conductance(fe, "chat", True, RNG, n_boot=NBOOT)
    out["output_within_reference"] = L.conductance(fe, "output", False, RNG, n_boot=NBOOT)
    out["search_within_reference"] = L.conductance(fe, "search", False, RNG, n_boot=NBOOT)
    cw = out["chat_within"].get("excess")
    out["P2_ratio_to_chat"] = {ch: (out[f"P1_{ch}_cross"].get("excess") / cw) if (cw and out[f"P1_{ch}_cross"].get("excess") is not None) else None
                               for ch in ("search", "output")}
    out["P3_routes"] = L.routes(fe)
    # per segment (descriptive): output channel and crossing counts
    seg = {}
    for (s,), g in fe.group_by("seg"):
        seg[s] = {"cand_cross": int(g["cross"].sum()),
                  "cross_adoptions": int(g.filter(pl.col("cross") & pl.col("t_adopt").is_not_null() & (pl.col("t_adopt") <= pl.col("tc"))).height),
                  "output": L.conductance(g, "output", True, RNG, n_boot=500)}
    out["by_segment"] = seg
    return out


def main():
    ad = C.agent_days()
    res = {"built_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    res["R1"] = run_r1(ad); print("R1 done", flush=True)
    res["R2"] = run_r2(ad); print("R2 done", flush=True)
    res["R3"] = run_r3(ad); print("R3 done", flush=True)
    (C.OUT / "r2_results.json").write_text(json.dumps(res, indent=1, default=float))
    commit = subprocess.run(["git", "-C", str(C.ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    prov = {"built_by": "hypotheses/H05-rooms-cut/analysis/r2_run.py (+ r2_synthetic.py for synthetic.json)", "git_commit": commit,
            "inputs": [{"source": "ai-village", "tables": ["work_commits", "artifacts", "artifact_mentions", "search_events",
                                                           "work_repos", "context_ledger_items", "call_windows", "rooms_timeline",
                                                           "pending_sets", "calendar", "H05 r1b agent_day + pair_day_bin1"]}],
            "params": {"bin_min": C.BIN_MIN, "resp_bins": C.RESP_BINS, "W_s": L.W_S, "beta_h18": C.BETA_H18, "seed": 20261005,
                       "reserved_data": "excluded (holdout_mask)"},
            "built_at": res["built_at_utc"]}
    (C.OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(json.dumps(res, indent=1, default=float)[:20000])


if __name__ == "__main__":
    main()
