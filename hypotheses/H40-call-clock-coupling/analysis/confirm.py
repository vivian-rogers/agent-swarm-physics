"""H40 confirmatory tests on the LOCKED HOLDOUT. Written after exploratory round 1; NOT RUN.

Guard: the holdout is touched only with BOTH flags
  uv run python hypotheses/H40-call-clock-coupling/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Dry run on non-holdout stand-ins (same code path, stand-in periods and fake split dates):
  uv run python hypotheses/H40-call-clock-coupling/analysis/confirm.py --dry-run

Targets (predictions frozen in FROZEN below and on the card, "Confirmatory predictions"):
  C1-C3  NE20 (2026-06-03, inside #45): one tool call per turn for Anthropic agents. DiD Anthropic vs others,
         pre 06-01..06-02 vs post 06-03..06-05: first stage (log call rate), per-call coupling, per-hour coupling.
  C4-C5  NE44 (2026-06-11, inside #46; confounded with NE22, the 200-event cap, same day): pause default 12 h -> 5 min.
         First stage (read-out wait of messages arriving during pauses), per-call coupling at timer-wake read-outs,
         per-hour coupling of messages arriving during pauses.
  C6     transfer: eta (calls n >= 2) on holdout periods #45, #46, #47 (regime III) and #28 (regime I).
Reuse policy (hypotheses/holdout.md): #45-#50 are targeted by H04, H30 and H35 confirm scripts (activity responses to
nudges). H40's statistic (reply hazard on the recipient's call clock, DQ2 reply labels) is a different statistic and
modality; nobody has examined reply timing on these periods. Disclose in both cards and LOG.md when run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h40lib as L  # noqa: E402
import replication as R  # noqa: E402

# frozen after round 1 (see card); the script refuses to confirm while any value is None
FROZEN = {   # frozen 2026-10-04 after exploratory round 1 (card, "Confirmatory predictions")
    "eps5_III": 0.57,          # round-1 pooled regime-III eps(5 min) [0.36, 0.78]
    "C1_min_did_logr": 0.10,   # NE20 first stage: |DiD in log call rate| >= 0.10, else C2/C3 not scored
    "C2_max_abs_did_alpha": 0.5,
    "C4_max_W_ratio": 0.8,     # NE44: median wait of pause-wake read-outs falls by >= 20%
    "C5_max_abs_dalpha": 0.5,
    "C6_eta_hi_below": 0.5,    # regime-III transfer periods (#45, #46, #47); #28 (regime I) descriptive
    "C6_regime_I_expect": "eta > 0 (round 1: regime I pooled 0.51); descriptive only",
}

REAL = dict(ne20=dict(goal=45, split="2026-06-03", treated_lab="Anthropic"),
            ne44=dict(goal=46, split="2026-06-11"),
            transfer=[45, 46, 47, 28])
STANDIN = dict(ne20=dict(goal=44, split="2026-05-28", treated_lab="Anthropic"),
               ne44=dict(goal=51, split="2026-07-13", unit="51c"),
               transfer=[38, 40, 19])


def git_clean_for(paths) -> bool:
    import subprocess
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *paths], capture_output=True, text=True).stdout
    return out.strip() == ""


def period_data(calls, goal, units, btid, allow_holdout):
    it = L.build_items(calls, goal, units, btid, allow_holdout=allow_holdout)
    if it.height == 0:
        raise RuntimeError(f"no items for #{goal}")
    return it


def did_ne20(calls, units, btid, cfg, allow_holdout) -> dict:
    """Per agent x side (pre/post split): call rate, model-free per-call beta(10) and per-hour P(5 min), and per-call
    coupling alpha from a hazard fit with agent x side intercepts (shared mechanism; the transition is the object)."""
    it = period_data(calls, cfg["goal"], units, btid, allow_holdout)
    split = cfg["split"]
    it = it.with_columns(pl.when(pl.col("pt_date") >= split).then(pl.lit("post")).otherwise(pl.lit("pre")).alias("side"))
    ros = L.roster().select(pl.col("agent").cast(pl.Int16).alias("recv"), "lab")
    it = it.join(ros, on="recv", how="left")
    # pseudo-units: agent x side
    au = it.select("recv", "side").unique().sort(["side", "recv"]).with_row_index("au2").with_columns(pl.col("au2").cast(pl.Int32))
    it = it.join(au, on=["recv", "side"], how="left").rename({"au2": "au"}).sort("c1").with_row_index("item2")
    n_au = it["au"].max() + 1
    cells = R.cells_for(calls, it, "r_tid")
    f, _ = L.fit_cells(cells, L.SPEC_FULL, n_au=n_au)
    nrep = np.bincount(cells["au"].to_numpy(), weights=cells["y"].to_numpy(), minlength=n_au)
    # call rates per agent x side
    sel = np.flatnonzero((calls.goal == cfg["goal"]) & (allow_holdout | ~calls.holdout))
    cd = pl.DataFrame({"recv": calls.agent[sel], "pt_date": [calls.days[d] for d in calls.day[sel]], "t": calls.t[sel],
                       "t_end": calls.t_end[sel]})
    cd = cd.with_columns(pl.when(pl.col("pt_date") >= split).then(pl.lit("post")).otherwise(pl.lit("pre")).alias("side"))
    rate = (cd.group_by(["recv", "side", "pt_date"]).agg(pl.len().alias("n"), ((pl.col("t_end").max() - pl.col("t").min()) / 3600).alias("h"))
            .group_by(["recv", "side"]).agg(pl.col("n").sum(), pl.col("h").sum()).with_columns((pl.col("n") / pl.col("h")).alias("rate")))
    rt = R.reply_timing(calls, it)
    mf = (it.select("recv", "side", "au").with_columns(pl.Series("y10", (rt["n_r"] <= 10) & rt["full10"]), pl.Series("f10", rt["full10"]),
                                                       pl.Series("y5", (rt["a_r"] <= 300) & rt["full5"]), pl.Series("f5", rt["full5"]))
          .group_by(["recv", "side", "au"]).agg(pl.col("y10").sum(), pl.col("f10").sum(), pl.col("y5").sum(), pl.col("f5").sum()))
    tab = mf.join(rate, on=["recv", "side"], how="left").join(ros, on="recv", how="left")
    tab = tab.with_columns(pl.Series("alpha", f.fe[tab["au"].to_numpy()]), pl.Series("alpha_se", f.fe_se[tab["au"].to_numpy()]),
                           pl.Series("nrep", nrep[tab["au"].to_numpy()]))
    w = tab.pivot(on="side", index=["recv", "lab"], values=["rate", "alpha", "alpha_se", "nrep", "y5", "f5", "y10", "f10"]).drop_nulls()
    w = w.filter((pl.col("nrep_pre") >= 3) & (pl.col("nrep_post") >= 3) & (pl.col("y5_pre") >= 1) & (pl.col("y5_post") >= 1))
    treated = (w["lab"] == cfg["treated_lab"]).to_numpy()
    dlr = np.log(w["rate_post"].to_numpy() / w["rate_pre"].to_numpy())
    da = w["alpha_post"].to_numpy() - w["alpha_pre"].to_numpy()
    dse = np.sqrt(w["alpha_se_pre"].to_numpy() ** 2 + w["alpha_se_post"].to_numpy() ** 2)
    dh = np.log((w["y5_post"] / w["f5_post"]).to_numpy() / (w["y5_pre"] / w["f5_pre"]).to_numpy())

    def did(x, se=None):
        a, o = x[treated], x[~treated]
        if len(a) == 0 or len(o) == 0:
            return dict(est=None)
        est = a.mean() - o.mean()
        s = np.sqrt(a.var(ddof=1) / len(a) + o.var(ddof=1) / len(o)) if len(a) > 1 and len(o) > 1 else np.nan
        return dict(est=float(est), se=float(s), lo=float(est - 1.96 * s), hi=float(est + 1.96 * s), n_t=int(len(a)), n_c=int(len(o)))
    return dict(n_agents=w.height, did_logr=did(dlr), did_alpha=did(da), did_loghour=did(dh),
                eta=f.get("eta"), eta_se=f.se("eta"))


def ne44(calls, units, btid, cfg, allow_holdout) -> dict:
    it = period_data(calls, cfg["goal"], units, btid, allow_holdout)
    if cfg.get("unit"):
        it = it.filter(pl.col("unit_id") == cfg["unit"])
    au = it.select("recv", "unit_id").unique().sort(["unit_id", "recv"]).with_row_index("au").with_columns(pl.col("au").cast(pl.Int32))
    it = it.join(au, on=["recv", "unit_id"], how="left")
    split = cfg["split"]
    c1 = it["c1"].to_numpy()
    wake = calls.gap[c1] == L.GAP_CODE["pause"]
    post = (it["pt_date"] >= split).to_numpy()
    W = it["W"].to_numpy()
    rt = R.reply_timing(calls, it)
    y1 = (it["r_tid"] == it["c1"]).to_numpy()
    y5 = (rt["a_r"] <= 300) & rt["full5"]
    k = calls.k_new[c1].astype(float)
    out = dict(n_wake_pre=int((wake & ~post).sum()), n_wake_post=int((wake & post).sum()))
    if (wake & ~post).sum() and (wake & post).sum():
        out["W_ratio_post_pre"] = float(np.median(W[wake & post]) / np.median(W[wake & ~post]))
        # per-call coupling at wake read-outs: log-hazard shift post vs pre, adjusted for batch, rank, mention, agent FE
        import scipy.sparse as sp
        sub = np.flatnonzero(wake)
        aucode = it["au"].to_numpy()[sub]
        n_au = int(aucode.max()) + 1
        FE = sp.csr_matrix((np.ones(len(sub)), (np.arange(len(sub)), aucode)), shape=(len(sub), n_au))
        X = np.column_stack([post[sub].astype(float), np.log1p(k[sub]), np.log(it["rank"].to_numpy()[sub]),
                             it["ment"].to_numpy()[sub].astype(float)])
        fpost, _ = L.fit(FE, X, np.zeros(len(sub)), y1[sub].astype(float), np.ones(len(sub)))
        out["dalpha_wake"] = dict(est=float(fpost.beta[0]), se=float(np.sqrt(fpost.cov[0, 0])))
        f5 = rt["full5"]
        out["P5_wake_pre"] = float(y5[wake & ~post & f5].mean()) if (wake & ~post & f5).sum() else None
        out["P5_wake_post"] = float(y5[wake & post & f5].mean()) if (wake & post & f5).sum() else None
    return out


def transfer(calls, units, btid, goals, allow_holdout, B=100) -> dict:
    out = {}
    for g in goals:
        it = period_data(calls, g, units, btid, allow_holdout)
        au = it.select("recv", "unit_id").unique().sort(["unit_id", "recv"]).with_row_index("au2").with_columns(pl.col("au2").cast(pl.Int32))
        it = it.join(au, on=["recv", "unit_id"], how="left").rename({"au2": "au"})
        cells = R.cells_for(calls, it, "r_tid")
        n_au = int(it["au"].max()) + 1
        f, full = L.fit_cells(cells, L.SPEC_FULL, n_au=n_au)
        dr, _, names = L.day_bootstrap(cells, L.SPEC_FULL, B, L.SEED + 9000 + g, start=full, n_au=n_au)
        se = float(np.nanmax([f.se("eta"), np.nanstd(dr[:, names.index("eta")])]))
        out[f"G{g:02d}"] = dict(eta=f.get("eta"), se=se, lo=f.get("eta") - 1.96 * se, hi=f.get("eta") + 1.96 * se,
                                replies=float(cells["y"].sum()), phi=f.get("phi"), psi=f.get("psi"))
    return out


def score(res: dict) -> dict:
    F = FROZEN
    v = {}
    n20 = res["ne20"]
    fs = n20["did_logr"].get("est")
    v["C1"] = bool(fs is not None and abs(fs) >= F["C1_min_did_logr"]) if F["C1_min_did_logr"] is not None else None
    if v["C1"]:
        da = n20["did_alpha"]
        v["C2"] = bool(da["lo"] <= 0 <= da["hi"] and abs(da["est"]) <= F["C2_max_abs_did_alpha"])
        pred = F["eps5_III"] * fs
        dh = n20["did_loghour"]
        v["C3"] = bool(dh["lo"] <= pred <= dh["hi"] and np.sign(dh["est"]) == np.sign(fs))
    n44 = res["ne44"]
    v["C4"] = bool(n44.get("W_ratio_post_pre", 9) <= F["C4_max_W_ratio"]) if F["C4_max_W_ratio"] is not None else None
    if "dalpha_wake" in n44:
        d = n44["dalpha_wake"]
        v["C5"] = bool(abs(d["est"]) <= F["C5_max_abs_dalpha"] and d["est"] - 1.96 * d["se"] <= 0 <= d["est"] + 1.96 * d["se"]
                       and (n44["P5_wake_post"] or 0) > (n44["P5_wake_pre"] or 1))
    v["C6"] = {k: bool(x["hi"] < F["C6_eta_hi_below"]) for k, x in res["transfer"].items() if k != "G28"}
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.confirm:
        if not a.ack:
            sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
        if any(v is None for v in FROZEN.values()):
            sys.exit("refusing: FROZEN predictions are not all set")
        if not git_clean_for(["hypotheses/H40-call-clock-coupling/analysis/confirm.py", "hypotheses/H40-call-clock-coupling/README.md"]):
            sys.exit("refusing: commit confirm.py and the card (predictions) before the confirmatory run")
        cfg, allow = REAL, True
    elif a.dry_run:
        cfg, allow = STANDIN, False
    else:
        sys.exit("use --dry-run, or --confirm --i-understand-this-uses-the-locked-holdout")
    calls = L.load_calls()
    units = L.unit_map()
    btid = L._call_tid_of_messages(calls)
    res = dict(mode="confirm" if a.confirm else "dry-run", run_at=dt.datetime.now(dt.timezone.utc).isoformat(),
               ne20=did_ne20(calls, units, btid, cfg["ne20"], allow), ne44=ne44(calls, units, btid, cfg["ne44"], allow),
               transfer=transfer(calls, units, btid, cfg["transfer"], allow, B=100 if a.confirm else 10))
    if all(v is not None for v in FROZEN.values()):
        res["verdicts"] = score(res)
    out = L.OUT / ("confirm" if a.confirm else "confirm_dryrun")
    out.mkdir(parents=True, exist_ok=True)
    L.jdump(res, out / "confirm.json")
    print({k: v for k, v in res.items() if k != "transfer"})
    print(res["transfer"])


if __name__ == "__main__":
    main()
