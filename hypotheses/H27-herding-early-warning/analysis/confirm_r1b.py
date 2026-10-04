"""H27 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN ON ROUND-1B INPUTS (2026-10-04). WRITTEN, NOT RUN.

Re-freeze of `confirm_holdout.py` (left byte-for-byte untouched), written before any holdout data was read (holdout
ledger item 18, batch D). What changed is listed in `CONFIRM_R1B.md`. In short:
  * labels: shared deterministic `project_states` (w_min 15/30, sources all; infra/shared/project_states.py), built in
    this script for the targets, instead of H11's round-1 nondeterministic builder. Labels are ranked on each target's
    own rows (identical to the shared ranking for a fully held-out period; the #51 tail is ranked on the tail);
  * C1-C4 unchanged (same thresholds, same frozen tau*, same O1 onset rule, same rate-matched shift null);
  * C5 -> C5-r1b: the link precursor is timed by the first LEDGER read of the link by an agent other than its poster
    (context_ledger_items x call_windows.t_call), not by posting time, and an in-flight arm (links posted in the 30 min
    before the onset but unread by anyone at the onset window start) is reported beside it (H28's blind window);
  * new C6-r1b (work ledger, DQ4): work-commit onsets never lead attention onsets of the same project.
Activity bins, outages and embeddings are not inputs of H27, so `activity_bins_fixed`, `outages_fixed`, the DQ8 trim
and the embedding models do not apply.

  uv run python hypotheses/H27-herding-early-warning/analysis/confirm_r1b.py --dry-run
      the identical pipeline on non-holdout stand-ins (#30, #31, #38), built into
      data/processed/H27-herding-early-warning/confirm_r1b_dryrun/; checks the label builder against the round-1b
      series (data/processed/H27-herding-early-warning/r1b/); prints the holdout-ledger reuse status (ledger only).
  uv run python hypotheses/H27-herding-early-warning/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
      refuses unless this script, CONFIRM_R1B.md, the card and the code it imports are committed and unmodified, and
      unless infra/shared/holdout_ledger.check() allows every target. Writes data/processed/H27-.../holdout_r1b/.

Reuse disclosure (hypotheses/holdout.md): H05 ran #32/#34 (room activity couplings); H02 and H04 ran #45 and H04 ran
#46-#50 (activity timing, Hawkes, kick response). H27's statistic (project-label onset timing, early-warning trends,
ledger-timed link precursor) is a different, unexamined statistic and modality. H11, H28, H31 and H01 plan uses of
the same targets; whoever runs second discloses in both cards and LOG.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H27-herding-early-warning"
DOUT = ROOT / "data/processed/H27-herding-early-warning"
R1B = DOUT / "r1b"                       # round-1b exploration series (builder check only)
HOLD = DOUT / "holdout_r1b"
DRY = DOUT / "confirm_r1b_dryrun"
SH = ROOT / "data/processed/shared"

os.environ["H27_DATA"] = str(R1B)       # explore's exploration guard points at the round-1b folder
os.environ["H27_STATE"] = "project"     # primary state: attention (project) labels, as frozen
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2" if _v == "POLARS_MAX_THREADS" else "1"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(HYP / "analysis"))
sys.path.insert(0, str(HYP / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT))
import ews_core as E  # noqa: E402
import explore as X  # noqa: E402
import project_states as PS  # noqa: E402
from infra.shared import common as C  # noqa: E402

HYP_ID = "H27"
TARGETS = [22, 28, 29, 32, 34, 45, 46, 47, 49, 50, 51]   # unchanged from confirm_holdout.py
TAIL51 = ("2026-09-07", "2026-09-21")                     # PT, end exclusive (holdout.json)
STAND_INS = [30, 31, 38]                                  # unchanged from confirm_holdout.py
WINDOWS = (15, 30)
QCOLS = [f"k{a}" for a in range(1, PS.Q_MAX + 1)]
WORK_FILTER = (pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent")
               & ~pl.col("automated") & pl.col("author_agent").is_not_null())

# ------------------------------------------------------------------ re-frozen confirmatory rule
# Re-frozen 2026-10-04 on round-1b inputs, before any holdout data was read. C1-C4: unchanged from confirm_holdout.py
# (round 1b on shared labels reproduced round 1: 21 onsets, AUC 0.62 [0.50, 0.76], tau_AR1 AUC 0.41, alarm 5/21 vs
# level 5/21). C5-r1b and C6-r1b: see CONFIRM_R1B.md (one-line reasons in REASONS).
FROZEN = dict(
    lead=4, W=15, min_eval_onsets=5,
    c1_auc_min=0.70, c2_auc_max=0.60, c3_ar1_auc_max=0.55, c4_n2_alpha=0.05,
    c5_min_onsets=5, c5_mh_or_min=2.0, c5_alpha=0.05, c5_pre_min=30,
    c6_min_pairs=3,
    inputs="shared project_states (w 15/30, sources all, ranked on the target's own rows); DQ4 work commits "
           "(canonical & ~imported & agent & ~automated); context ledger first read by a non-poster for links",
)
REASONS = {
    "C5-r1b": "links are timed at their first ledger read by a non-poster (exposure acts at the receiving call; "
              "STANDARDS 2); round 1b found 11/21 onsets after a posted link, a contemporaneous-convergence-open statistic",
    "C6-r1b": "new: round 1b found work onsets at lag 0-1 window after attention onsets (never before) in 4/4 pairs",
}
PREDICTIONS = {
    "C1": "composite AUC >= 0.70 and CI lower bound > 0.5 (H27 as hypothesized; expected NOT confirmed)",
    "C2": "composite AUC < 0.60 or CI includes 0.5 (round-1/1b negative replicates)",
    "C3": "tau_AR1 AUC <= 0.55 (no slowing down)",
    "C4": "EWS alarm hits do not beat the rate-matched shift null (p >= 0.05) or the level alarm hits >= as many onsets",
    "C5-r1b": "a chat link to the project READ (ledger, non-poster) in the 30 min before the onset window: "
              "MH OR > 2 and within-period permutation p < 0.05 (>= 5 onsets, else inconclusive)",
    "C6-r1b": "for projects with onsets in both spaces (W 15), no work-ledger onset precedes the attention onset by >= 1 "
              "window (>= 3 pairs, else inconclusive)",
}


# ------------------------------------------------------------------ guards
def committed_clean(paths) -> bool:
    for p in paths:
        r = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", str(p)], capture_output=True)
        if r.returncode != 0:
            return False
        r = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(p)], capture_output=True, text=True)
        if r.returncode != 0 or r.stdout.strip():
            return False
    return True


def ledger_status(strict: bool) -> bool:
    """holdout_ledger.check() for every target (ledger only; no data)."""
    from infra.shared import holdout_ledger as hl
    ok = True
    for g in TARGETS:
        t = "#51-tail" if g == 51 else f"G{g:02d}"
        r = hl.check(HYP_ID, t, "project labels", ["project_potts"])
        print(f"ledger {t}: allowed={r['allowed']} needs_disclosure={r['needs_disclosure']} "
              f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
              f"same_family_runs={sorted({u['hypothesis'] for u in r['prior_runs_same_family']})} "
              f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}")
        ok &= r["allowed"]
    return ok or not strict


# ------------------------------------------------------------------ builder (shared deterministic labels)
def series(lab: pl.DataFrame, wins: pl.DataFrame) -> pl.DataFrame:
    """Same as scheme/build.py: series() (counts per label per window)."""
    wins = wins.sort("day", "win").with_row_index("gwin").with_columns(pl.col("gwin").cast(pl.Int32))
    n = lab.group_by("day", "win").agg(pl.len().cast(pl.Int16).alias("n"))
    real = lab.filter(pl.col("label") > 0)
    k = real.group_by("day", "win", "label").agg(pl.len().cast(pl.Int16).alias("k"))
    s = wins.select("gwin", "day", "win", "pt_date").join(n, on=["day", "win"], how="left")
    if k.height:
        kw = k.pivot(on="label", index=["day", "win"], values="k")
        kw = kw.rename({c: f"k{c}" for c in kw.columns if c not in ("day", "win")})
        s = s.join(kw, on=["day", "win"], how="left")
    for c in QCOLS:
        if c not in s.columns:
            s = s.with_columns(pl.lit(0).alias(c))
    s = s.with_columns([pl.col(c).fill_null(0).cast(pl.Int16) for c in QCOLS] + [pl.col("n").fill_null(0).cast(pl.Int16)])
    return s.select("gwin", "day", "win", "pt_date", "n", *QCOLS).sort("gwin")


def target_calendar(goals, allow_holdout):
    cal = PS.load_calendar(goals, allow_holdout=allow_holdout)
    if not allow_holdout:
        assert not cal["ho"].any()
    parts = []
    for g in goals:
        c = cal.filter(pl.col("goal_no") == g)
        if g == 51 and allow_holdout:
            c = c.filter((pl.col("pt_date") >= TAIL51[0]) & (pl.col("pt_date") < TAIL51[1]))
            assert c["ho"].all()
        elif allow_holdout:
            assert c["ho"].all(), f"#{g} is not fully held out"
        c = c.sort("pt_date").with_columns((pl.col("pt_date").rank("dense").cast(pl.Int16) - 1).alias("day"))
        parts.append(c)
    return pl.concat(parts)


def attention_labels(cal, W):
    days = cal["pt_date"].to_list()
    ps = (pl.scan_parquet(SH / "project_states.parquet")
          .filter((pl.col("w_min") == W) & (pl.col("sources").cast(pl.String) == "all") & pl.col("pt_date").is_in(days))
          .collect())
    ps = ps.drop("day", "label").join(cal.select("pt_date", "goal_no", "day"), on=["pt_date", "goal_no"], how="inner")
    return ps.select("goal_no", "pt_date", "day", "win", "agent", pl.col("project").cast(pl.String), "room")


def work_labels(cal, W, wins):
    wc = pl.scan_parquet(SH / "work_commits.parquet").filter(WORK_FILTER).select(
        pl.col("repo").cast(pl.String).alias("project"), "t", pl.col("author_agent").alias("agent")).collect()
    wc = PS.assign_windows(wc, cal, W)
    fs = pl.read_parquet(SH / "work_repos.parquet").select(pl.col("repo").cast(pl.String).alias("project"),
                                                          pl.col("first_commit_t").alias("first_seen")).drop_nulls()
    lab = PS.modal(wc, "project", fs)
    return PS.attach_rooms(lab, wins).select("goal_no", "pt_date", "day", "win", "agent", "project", "room")


def build(goals, out: Path, allow_holdout: bool):
    """Series for attention (series_w*) and work (series_work_w*) labels, per goal, into out/G<NN>/."""
    out.mkdir(parents=True, exist_ok=True)
    cal = target_calendar(goals, allow_holdout)
    cov, cov_w = {}, {}
    for W in WINDOWS:
        wins_all = PS.window_table(cal, W)
        for kind, lab_all in (("project", attention_labels(cal, W)), ("work", work_labels(cal, W, wins_all))):
            for g in goals:
                lab = lab_all.filter(pl.col("goal_no") == g)
                wins = wins_all.filter(pl.col("goal_no") == g)
                if lab.height == 0:
                    continue
                lab, proj = PS.label_projects(lab)            # ranked on this target's own rows
                f = out / f"G{g:02d}"
                f.mkdir(parents=True, exist_ok=True)
                s = series(lab, wins)
                sfx = "" if kind == "project" else "_work"
                s.write_parquet(f / f"series{sfx}_w{W}.parquet", compression="zstd")
                pj = proj.filter(pl.col("label") > 0).select("label", "project", "aw", "share", "n_agents").sort("label")
                pj.write_parquet(f / (f"projects_w{W}.parquet" if kind == "project" else f"projects_work_w{W}.parquet"),
                                 compression="zstd")
                q = int(pj["label"].max() or 0) if pj.height else 0
                (cov if kind == "project" else cov_w).setdefault(str(g), {})[f"w{W}"] = dict(
                    windows=s.height, days=int(s["day"].n_unique()), q=q, frac_n_ge3=float((s["n"] >= 3).mean()),
                    mean_n=float(s["n"].mean()))
    (out / "coverage.json").write_text(json.dumps(cov, indent=1))
    (out / "coverage_work.json").write_text(json.dumps(cov_w, indent=1))
    (out / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H27-herding-early-warning/analysis/confirm_r1b.py", "git_commit": C.git_commit(),
        "inputs": [{"source": "ai-village", "revision": C.REVISION,
                    "tables": ["project_states", "work_commits", "work_repos", "calendar", "rooms_timeline",
                               "artifact_mentions", "artifacts", "context_ledger_items", "call_windows", "chat_core"]}],
        "params": {"goals": goals, "allow_holdout": allow_holdout, "windows": list(WINDOWS), "frozen": FROZEN},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))


def builder_check(goals):
    """Dry run: the rebuilt stand-in attention series equal the round-1b exploration series (same labels)."""
    out = {}
    for g in goals:
        for W in WINDOWS:
            a = pl.read_parquet(DRY / f"G{g:02d}" / f"series_w{W}.parquet")
            b = pl.read_parquet(R1B / f"G{g:02d}" / f"series_w{W}.parquet")
            same = a.height == b.height and a.select("n", *QCOLS).equals(b.select("n", *[c for c in QCOLS if c in b.columns]))
            out[f"G{g:02d}_w{W}"] = bool(same)
    return out


# ------------------------------------------------------------------ C5-r1b: ledger-timed link precursor
def link_reads(goals, allow_holdout):
    """project -> (post times, first non-poster ledger read times, sender kind) for chat links (strict mentions)."""
    pm = PS.project_map()
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "goal_no", "speaker_kind", "agent", "t"]).filter(
        pl.col("goal_no").is_in(goals))
    am = (pl.scan_parquet(SH / "artifact_mentions.parquet")
          .filter((pl.col("source").cast(pl.String) == "chat") & pl.col("how").cast(pl.String).is_in(["url", "output", "bare"])
                  & pl.col("message_id").is_not_null()).select("artifact", "message_id").collect()
          .join(pm, on="artifact", how="inner").select("message_id", "project").unique())
    m = am.join(cc, on="message_id", how="inner")
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id", "omitted")
             .filter(pl.col("message_id").is_in(m["message_id"].unique().implode()) & ~pl.col("omitted")).collect())
    cw = pl.scan_parquet(SH / "call_windows.parquet").select("turn_id", "agent", "t_call", "holdout").collect()
    rd = items.join(cw, on="turn_id", how="inner")
    if not allow_holdout:
        rd = rd.filter(~pl.col("holdout"))
    snd = m.select("message_id", pl.col("agent").alias("sender")).unique("message_id")
    rd = rd.join(snd, on="message_id", how="left").filter(pl.col("sender").is_null() | (pl.col("agent") != pl.col("sender")))
    first = rd.group_by("message_id").agg(pl.col("t_call").min().alias("t_read"))
    m = m.join(first, on="message_id", how="left").with_columns(
        pl.col("t").dt.epoch("s").alias("ts"), pl.col("t_read").dt.epoch("s").alias("tr"),
        (pl.col("speaker_kind").cast(pl.String) == "agent").alias("by_agent"))
    out = {}
    for (nm,), d in m.group_by(["project"]):
        out[nm] = (d["ts"].to_numpy().astype(float), d["tr"].fill_null(np.inf).to_numpy().astype(float),
                   d["by_agent"].to_numpy())
    return out


def _any_in(arr, lo, hi):
    return bool(arr is not None and len(arr) and np.any((arr >= lo) & (arr < hi)))


def mh_perm(df: pl.DataFrame, col: str, seed=11, n_perm=2000):
    a_ = int(df.filter(pl.col("onset"))[col].sum())
    n1 = int(df["onset"].sum())
    num = den = 0.0
    strata = []
    for (_,), d in df.group_by(["goal"]):
        if not d["onset"].any():
            continue
        on_ = d["onset"].to_numpy().astype(bool)
        x = d[col].to_numpy().astype(bool)
        a1, b1 = int((on_ & x).sum()), int((on_ & ~x).sum())
        c1, d1 = int((~on_ & x).sum()), int((~on_ & ~x).sum())
        nn = a1 + b1 + c1 + d1
        num += a1 * d1 / nn
        den += b1 * c1 / nn
        strata.append((on_, x))
    if not strata:
        return dict(onsets_with=a_, onsets=n1, mh_odds_ratio=None, perm_p_within_period=None)
    obs = sum(int((o & x).sum()) for o, x in strata)
    rng = np.random.default_rng(seed)
    perm = np.array([sum(int((rng.permutation(o) & x).sum()) for o, x in strata) for _ in range(n_perm)])
    return dict(onsets_with=a_, onsets=n1, mh_odds_ratio=float(num / den) if den else None,
                perm_p_within_period=float((1 + (perm >= obs).sum()) / (1 + n_perm)), perm_mean=float(perm.mean()))


def link_precursor(periods, base, allow_holdout, W=15, p=E.P0):
    """Same onset / placebo windows as assemble.trigger_check; link timed by its first non-poster ledger read."""
    pre = FROZEN["c5_pre_min"] * 60
    links = link_reads(periods, allow_holdout)
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start")
    rows = []
    for g in periods:
        k, n, win, day, s = X.load_series(g, W, base)
        on = E.find_onsets(k, n, win, day, p)
        ind = E.all_window_indicators(k, n, p)
        watch = ind["valid"] & ind["matched"]
        sj = s.join(cal, on="pt_date", how="left")
        t0 = sj["win_start"].dt.epoch("s").to_numpy().astype(float) + sj["win"].to_numpy().astype(np.int64) * W * 60
        projs = pl.read_parquet(base / f"G{g:02d}" / f"projects_w{W}.parquet")
        names = dict(zip(projs["label"].to_list(), projs["project"].to_list()))
        T, q = k.shape
        onset_set = {(o["project"], o["w0"]) for o in on}
        for a in range(q):
            ts, tr, ag = links.get(names.get(a + 1), (None, None, None))
            w0s = [o["w0"] for o in on if o["project"] == a]
            for t in range(T):
                is_on = (a, t) in onset_set
                if not is_on and (not watch[t, a] or any(t - 4 < w0 <= t + p.horizon for w0 in w0s)):
                    continue
                lo, hi = t0[t] - pre, t0[t]
                rd = tr is not None and len(tr) and np.any((tr >= lo) & (tr < hi))
                rows.append(dict(
                    goal=g, onset=is_on,
                    link_posted=_any_in(ts, lo, hi),
                    link_read=bool(rd),
                    link_read_agent=bool(tr is not None and len(tr) and np.any((tr >= lo) & (tr < hi) & ag)),
                    link_read_other=bool(tr is not None and len(tr) and np.any((tr >= lo) & (tr < hi) & ~ag)),
                    link_inflight=bool(ts is not None and len(ts) and np.any((ts >= lo) & (ts < hi) & (tr >= hi)))))
    df = pl.DataFrame(rows) if rows else pl.DataFrame(schema={"goal": pl.Int64, "onset": pl.Boolean})
    return {c: mh_perm(df, c) for c in ("link_posted", "link_read", "link_read_agent", "link_read_other", "link_inflight")} \
        if df.height else {}


# ------------------------------------------------------------------ C6-r1b: work vs attention onset order
def onset_order(periods, base, W=15, p=E.P0):
    lags = []
    for g in periods:
        f = base / f"G{g:02d}"
        if not (f / f"series_work_w{W}.parquet").exists():
            continue
        on = {}
        for kind, sfx, pf in (("att", "", f"projects_w{W}.parquet"), ("work", "_work", f"projects_work_w{W}.parquet")):
            s = pl.read_parquet(f / f"series{sfx}_w{W}.parquet").sort("gwin")
            pj = pl.read_parquet(f / pf)
            q = int(pj["label"].max() or 0) if pj.height else 0
            if q == 0:
                on[kind] = []
                continue
            k = s.select([f"k{a}" for a in range(1, q + 1)]).to_numpy().astype(int)
            names = dict(zip(pj["label"].to_list(), pj["project"].to_list()))
            on[kind] = [(names.get(o["project"] + 1), o["w0"]) for o in
                        E.find_onsets(k, s["n"].to_numpy().astype(int), s["win"].to_numpy(), s["day"].to_numpy(), p)]
        for pr, w0w in on.get("work", []):
            att = [w0 for pa, w0 in on.get("att", []) if pa == pr]
            if att:
                d = np.array(w0w) - np.array(att)
                lags.append(dict(goal=g, lag=int(d[np.argmin(np.abs(d))])))
    n = len(lags)
    if n < FROZEN["c6_min_pairs"]:
        return dict(n_pairs=n, verdict="inconclusive (underpowered)", lags=[x["lag"] for x in lags])
    lead = sum(x["lag"] <= -1 for x in lags)
    return dict(n_pairs=n, n_work_leads=int(lead), median_lag=float(np.median([x["lag"] for x in lags])),
                lags=[x["lag"] for x in lags], verdict="confirmed" if lead == 0 else "not confirmed")


# ------------------------------------------------------------------ scoring
def score(arm, base, allow_holdout):
    A = arm["auc"][FROZEN["lead"]]
    a, ci = A["composite"]["auc"], A["composite"]["ci"]
    a_ar1 = A["tau_ar1"]["auc"]
    n_eval = A["n_onset_segments"]
    ews, lvl = arm["operator"]["ews"], arm["operator"]["level"]
    out = dict(auc=a, ci=ci, auc_ar1=a_ar1, n_eval=n_eval, n_onsets=ews["n_onsets"],
               ews={k: ews[k] for k in ("hits", "n_onsets", "far", "ppv", "median_lead_h", "N2_p", "false_alarms_per_day") if k in ews},
               level={k: lvl[k] for k in ("hits", "n_onsets", "far", "ppv", "median_lead_h", "false_alarms_per_day")})
    if n_eval < FROZEN["min_eval_onsets"]:
        out.update(C1="inconclusive (underpowered)", C2="inconclusive (underpowered)", C3="inconclusive (underpowered)")
    else:
        out["C1"] = "confirmed" if (a >= FROZEN["c1_auc_min"] and ci[0] > 0.5) else "not confirmed"
        out["C2"] = "confirmed" if (a < FROZEN["c2_auc_max"] or ci[0] <= 0.5) else "not confirmed"
        out["C3"] = "confirmed" if (a_ar1 is not None and a_ar1 <= FROZEN["c3_ar1_auc_max"]) else "not confirmed"
    if ews["n_onsets"] == 0:
        out["C4"] = "inconclusive (no onsets)"
    else:
        out["C4"] = "confirmed" if (ews.get("N2_p", 1.0) >= FROZEN["c4_n2_alpha"] or lvl["hits"] >= ews["hits"]) else "not confirmed"
    lp = link_precursor(arm["periods"], base, allow_holdout)
    out["C5_r1b_links"] = lp
    tr = lp.get("link_read", {})
    if tr.get("onsets", 0) < FROZEN["c5_min_onsets"] or tr.get("mh_odds_ratio") is None:
        out["C5-r1b"] = "inconclusive (underpowered)"
    else:
        out["C5-r1b"] = "confirmed" if (tr["mh_odds_ratio"] > FROZEN["c5_mh_or_min"]
                                        and tr["perm_p_within_period"] < FROZEN["c5_alpha"]) else "not confirmed"
    oo = onset_order(arm["periods"], base)
    out["C6_r1b_order"] = oo
    out["C6-r1b"] = oo["verdict"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run == a.confirm:
        raise SystemExit("choose exactly one of --dry-run or --confirm")
    tau_star = X.load_tau_star()
    if a.dry_run:
        print(f"DRY RUN on non-holdout stand-ins {STAND_INS} (no holdout data read). tau* = {tau_star:.3f}")
        ledger_status(strict=False)
        assert not set(STAND_INS) & set(C.load_holdout()["goal_periods_held_out"])
        build(STAND_INS, DRY, allow_holdout=False)
        chk = builder_check(STAND_INS)
        print("builder check (rebuilt == round-1b series):", chk)
        arm = X.run_arm(FROZEN["W"], E.P0, tau_star, goals=STAND_INS, base=DRY, robust=False, n_shift=100)
        res = score(arm, DRY, allow_holdout=False)
        (DRY / "confirm_r1b_dryrun.json").write_text(json.dumps(
            dict(stand_ins=STAND_INS, frozen=FROZEN, predictions=PREDICTIONS, reasons=REASONS, builder_check=chk,
                 result=res, run_at=dt.datetime.now(dt.timezone.utc).isoformat()), indent=1, default=float))
        print(json.dumps({k: v for k, v in res.items() if k not in ("ews", "level")}, indent=1, default=float))
        return
    if not a.ack:
        raise SystemExit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
    must = [Path(__file__).resolve(), HYP / "analysis/CONFIRM_R1B.md", HYP / "README.md", HYP / "analysis/ews_core.py",
            HYP / "analysis/explore.py", ROOT / "infra/shared/project_states.py", ROOT / "hypotheses/holdout.json"]
    if not committed_clean(must):
        raise SystemExit("refusing: commit confirm_r1b.py, CONFIRM_R1B.md, the card and the code it imports first "
                         "(holdout reuse policy, item 1)")
    if not ledger_status(strict=True):
        raise SystemExit("refusing: holdout_ledger.check() reports a same-family prior run on a target; Vivian decides")
    build(TARGETS, HOLD, allow_holdout=True)
    arm = X.run_arm(FROZEN["W"], E.P0, tau_star, goals=TARGETS, base=HOLD, robust=False, n_shift=500)
    res = score(arm, HOLD, allow_holdout=True)
    (HOLD / "holdout_r1b_results.json").write_text(json.dumps(
        dict(targets=TARGETS, frozen=FROZEN, predictions=PREDICTIONS, reasons=REASONS, result=res,
             periods=arm["periods"], per_period=arm["per_period"], run_at=dt.datetime.now(dt.timezone.utc).isoformat()),
        indent=1, default=float))
    print(json.dumps({k: v for k, v in res.items() if k not in ("ews", "level")}, indent=1, default=float))


if __name__ == "__main__":
    main()
