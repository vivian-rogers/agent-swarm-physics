"""H40: cross-period summary, prediction scoring and synthetic summary.

  uv run python hypotheses/H40-call-clock-coupling/analysis/summarize.py
Writes data/processed/H40-call-clock-coupling/results/{replication_table.parquet, summary.json, synthetic_summary.parquet}.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h40lib as L  # noqa: E402

RES = L.OUT / "results"
POWER_SE = 0.25          # a period is "powered" for eta if its SE <= 0.25 (CI half-width <= ~0.5)
NATIVE = {18: "N3", 36: "N4", 51: "N1"}


def titles() -> dict:
    t = {}
    for line in (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def verdict(eta, lo, hi, se, dll):
    if not np.isfinite(se) or se > 0.5:
        return "n/a"
    if hi < 0.5 and dll > 0:
        return "supported"
    if lo > 0.5 or (eta >= 0.5 and dll <= 0):
        return "failed"
    return "mixed"


def gap_ok(r, g, min_rep=20):
    """enough replies at later calls of this gap kind for a gap-specific eta."""
    return True


def load_table() -> pl.DataFrame:
    rows = []
    for p in sorted(RES.glob("G*.json")):
        r = json.loads(p.read_text())
        c, se = r["coef"], r["se"]
        b, mf, h, e = r["between"], r["modelfree"], r["heldout"], r["eps"]
        eg = r.get("eta_by_gap", {})
        sens = r.get("sensitivity", {})
        row = dict(goal=r["goal"], regime=r["regime"], n_items=r["n_items"], replies=r["n_replies_window"],
                   n_days=r["n_days"], eta=c.get("eta"), eta_se=se.get("eta"), eta_lo=r["boot_ci"]["eta"][0],
                   eta_hi=r["boot_ci"]["eta"][1], eta1=c.get("eta1"), eta1_se=se.get("eta1"), phi=c.get("phi"),
                   phi_se=se.get("phi"), psi=c.get("psi"), psi_se=se.get("psi"), chi=c.get("chi"), chi_se=se.get("chi"),
                   logk=c.get("logk"), prev_talk=c.get("prev_talk"), reset=c.get("reset_since"),
                   s=b.get("s"), s_se=b.get("s_se"), s_lo=b.get("s_lo"), s_hi=b.get("s_hi"), s_tau=b.get("tau"),
                   s_nau=b.get("n_au"), s_ctrl=b.get("s_ctrl"), s_ctrl_se=b.get("s_ctrl_se"), sd_logr=b.get("sd_logr"),
                   mf_call=mf.get("slope_call10"), mf_call_se=mf.get("slope_call10_se"),
                   mf_wall=mf.get("slope_wall5"), mf_wall_se=mf.get("slope_wall5_se"),
                   D_call=mf["collapse"]["D_call"], D_wall=mf["collapse"]["D_wall"],
                   lr_call=mf["collapse"]["logratio_call"], lr_wall=mf["collapse"]["logratio_wall"],
                   dll=h["dll_call_wall"], dll_full=h["dll_full_call"],
                   eps5=e["300"]["est"], eps5_se=e["300"]["se"], eps15=e["900"]["est"], eps15_se=e["900"]["se"],
                   eps30=e["1800"]["est"], eps30_se=e["1800"]["se"],
                   eta_busy=eg.get("busy", {}).get("est"), eta_busy_se=eg.get("busy", {}).get("se"),
                   eta_pause=eg.get("pause", {}).get("est"), eta_pause_se=eg.get("pause", {}).get("se"),
                   eta_longprev=eg.get("long_prev", {}).get("est"), eta_longprev_se=eg.get("long_prev", {}).get("se"),
                   eta_forced=eg.get("after_forced", {}).get("est"), eta_forced_se=eg.get("after_forced", {}).get("se"),
                   eta_chat=eg.get("chat_busy", {}).get("est"), eta_chat_se=eg.get("chat_busy", {}).get("se"),
                   chat_hr=r["coef_gap"].get("chat"),
                   sens_any=sens.get("any_tid", {}).get("eta"), sens_addr=sens.get("addr_tid", {}).get("eta"),
                   sens_certain=sens.get("certain_only", {}).get("eta"),
                   sens_jit=float(np.mean([j["eta"] for j in sens.get("jitter", [])])) if sens.get("jitter") else None,
                   sens_addr_phi=sens.get("addr_tid", {}).get("phi"), sens_addr_psi=sens.get("addr_tid", {}).get("psi"))
        rows.append(row)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df = df.with_columns(pl.struct(["eta", "eta_lo", "eta_hi", "eta_se", "dll"]).map_elements(
        lambda s: verdict(s["eta"], s["eta_lo"], s["eta_hi"], s["eta_se"], s["dll"]), return_dtype=pl.String).alias("verdict"))
    df = df.with_columns(pl.col("goal").map_elements(lambda g: NATIVE.get(g, ""), return_dtype=pl.String).alias("native"))
    return df.sort("goal")


def re_pool(df, col, se_col, filt=None):
    d = df if filt is None else df.filter(filt)
    d = d.filter(pl.col(col).is_not_null() & pl.col(se_col).is_not_null() & pl.col(col).is_finite())
    return L.re_mean(d[col].to_numpy(), d[se_col].to_numpy())


def synthetic_summary() -> pl.DataFrame:
    parts = []
    for p in sorted((L.OUT / "synthetic").glob("*.parquet")):
        if p.stem == "G37":
            continue      # smoke test only
        parts.append(pl.read_parquet(p))
    if not parts:
        return pl.DataFrame()
    df = pl.concat(parts, how="diagonal_relaxed")
    df = df.with_columns(((pl.col("eta") - pl.col("true_eta")).abs() < 1.96 * pl.col("se_eta")).alias("cover"),
                         (pl.col("eta") + 1.96 * pl.col("se_eta") < 1).alias("rej1"),
                         (pl.col("eta") - 1.96 * pl.col("se_eta") > 0).alias("rej0"))
    g = df.group_by(["goal", "unit", "scenario"]).agg(
        pl.len().alias("reps"), pl.col("true_eta").first(), pl.col("eta").mean().alias("eta_mean"),
        pl.col("eta").std().alias("eta_sd"), pl.col("se_eta").mean().alias("se_mean"), pl.col("cover").mean(),
        pl.col("rej1").mean(), pl.col("rej0").mean(), pl.col("phi").mean(), pl.col("psi").mean(),
        pl.col("true_s").first(), pl.col("s").mean().alias("s_mean"), pl.col("s").std().alias("s_sd"),
        (pl.col("dll_call_wall") > 0).mean().alias("call_wins"), pl.col("dll_call_wall").count().alias("n_heldout"),
        pl.col("eps_true_300").mean(), pl.col("eps_est_300").mean(), pl.col("eps_true_1800").mean(),
        pl.col("eps_est_1800").mean(), pl.col("n_replies").mean()).sort(["goal", "scenario"])
    return g


def main():
    df = load_table()
    RES.mkdir(parents=True, exist_ok=True)
    df.write_parquet(RES / "replication_table.parquet")
    pw = df.filter(pl.col("eta_se") <= POWER_SE)
    S = dict(n_periods=df.height, n_powered=pw.height, verdicts=df["verdict"].value_counts().to_dicts())
    S["RE_eta"] = {k: re_pool(df, "eta", "eta_se", f) for k, f in
                   (("all", None), ("I", pl.col("regime") == "I"), ("II", pl.col("regime") == "II"),
                    ("III", pl.col("regime") == "III"))}
    S["RE_eta1"] = {k: re_pool(df, "eta1", "eta1_se", f) for k, f in
                    (("all", None), ("I", pl.col("regime") == "I"), ("III", pl.col("regime") == "III"))}
    for nm in ("eta_busy", "eta_pause", "eta_longprev", "eta_forced", "eta_chat"):
        S[f"RE_{nm}"] = {k: re_pool(df.filter(pl.col(f"{nm}_se") < 1.0), nm, f"{nm}_se", f) for k, f in
                         (("all", None), ("I", pl.col("regime") == "I"), ("III", pl.col("regime") == "III"))}
    for nm in ("phi", "psi", "chi"):
        S[f"RE_{nm}"] = {k: re_pool(df, nm, f"{nm}_se", f) for k, f in
                         (("all", None), ("I", pl.col("regime") == "I"), ("III", pl.col("regime") == "III"))}
    S["RE_s"] = {k: re_pool(df.filter(pl.col("s_se") < 2), "s", "s_se", f) for k, f in
                 (("all", None), ("I", pl.col("regime") == "I"), ("III", pl.col("regime") == "III"))}
    S["RE_mf_call"] = {k: re_pool(df.filter(pl.col("mf_call_se") < 2), "mf_call", "mf_call_se", f) for k, f in
                       (("all", None), ("I", pl.col("regime") == "I"), ("III", pl.col("regime") == "III"))}
    S["RE_mf_wall"] = {k: re_pool(df.filter(pl.col("mf_wall_se") < 2), "mf_wall", "mf_wall_se", f) for k, f in
                       (("all", None), ("I", pl.col("regime") == "I"), ("III", pl.col("regime") == "III"))}
    for nm in ("eps5", "eps15", "eps30"):
        S[f"RE_{nm}"] = {k: re_pool(df, nm, f"{nm}_se", f) for k, f in
                         (("all", None), ("I", pl.col("regime") == "I"), ("III", pl.col("regime") == "III"))}
    # prediction scoring
    P = {}
    re_all = S["RE_eta"]["all"]
    P["P1"] = dict(pooled=re_all, pooled_in_band=bool(re_all["lo"] >= -0.25 and re_all["hi"] <= 0.25),
                   share_powered_eta_below_half=float((pw["eta"] < 0.5).mean()) if pw.height else None,
                   n_powered=pw.height)
    r3 = pw.filter(pl.col("regime") == "III")
    p2 = r3.with_columns(((pl.col("phi") + 1.96 * pl.col("phi_se") < 0) & (pl.col("phi").abs() > pl.col("psi").abs())).alias("ok"))
    P["P2"] = dict(n=p2.height, share=float(p2["ok"].mean()) if p2.height else None, RE_phi=S["RE_phi"]["III"],
                   RE_psi=S["RE_psi"]["III"])
    P["P3"] = dict(RE_s=S["RE_s"]["all"], RE_mf_call=S["RE_mf_call"]["all"], RE_mf_wall=S["RE_mf_wall"]["all"])
    P["P4"] = dict(share_dll_pos=float((pw["dll"] > 0).mean()) if pw.height else None,
                   share_all=float((df["dll"] > 0).mean()))
    P["P5"] = dict(share_collapse_call=float((pw["D_call"] < pw["D_wall"]).mean()) if pw.height else None,
                   share_all=float((df["D_call"] < df["D_wall"]).mean()))
    P["P6"] = dict(RE_eps5_III=S["RE_eps5"]["III"], RE_eps30_III=S["RE_eps30"]["III"], RE_eps5_all=S["RE_eps5"]["all"],
                   RE_eps30_all=S["RE_eps30"]["all"])
    S["predictions"] = P
    syn = synthetic_summary()
    if syn.height:
        syn.write_parquet(RES / "synthetic_summary.parquet")
        S["synthetic"] = syn.to_dicts()
    L.jdump(S, RES / "summary.json")
    pl.Config.set_tbl_rows(60); pl.Config.set_tbl_cols(30); pl.Config.set_tbl_width_chars(260)
    print(df.select("goal", "regime", "replies", "eta", "eta_se", "eta1", "phi", "psi", "chi", "eta_chat", "eta_pause",
                    "s", "s_se", "mf_call", "mf_wall", "D_call", "D_wall", "dll", "eps5", "eps30", "verdict")
          .with_columns(pl.col(pl.Float64).round(2)))
    print(json.dumps({k: v for k, v in S.items() if k.startswith("RE_") or k == "predictions"}, indent=0, default=float)[:6000])
    if syn.height:
        print(syn.with_columns(pl.col(pl.Float64).round(3)))


if __name__ == "__main__":
    main()
