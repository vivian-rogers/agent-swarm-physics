"""H06 confirmatory test on the locked holdout free week #22, RE-FROZEN ON ROUND-1B INPUTS (2026-10-04). NOT RUN.

`confirm_holdout.py` is left byte-for-byte untouched; what changed is in `CONFIRM_R1B.md`. In short:
  * intention clusters on DQ5 gte-modernbert `style_resid_period` vectors (round 1b primary, `gte_sr`) and the second
    model bge-small (`bge_sr`), instead of round 1's own bge whitening. For a held-out period the shared file holds the
    regime-fallback style fit, so the script refits the style regression on the period's own intent statements
    (infra/shared/style_resid.py: fit_style / apply_style, >= MIN_FIT_PERIOD rows; else the regime fallback), as the
    style_resid docstring prescribes for confirmatory runs. The dry run checks the refit against the shared vectors;
  * artifact labels from the shared deterministic `project_states` (w 30, sources all), not H11's nondeterministic files;
  * work labels (DQ4 work ledger: canonical & ~imported & agent & ~automated) as a new label set;
  * a ledger copying-channel test (context_ledger_items x call_windows: read vs posted-unread vs not mentioned);
  * predictions: C1, C2 and C4 rules unchanged on the primary set; C2-r1b and C3-r1b require both embedding models
    (round 1b: LLRs and beta flip with the model, fragmentation does not); new C5-r1b (work) and C6-r1b (copying).
  * holdout_ledger.check() and a commit check guard the confirm path.
Activity bins, outages and talk spins are not H06 inputs; the DQ8 trim does not apply.

Usage:
  uv run python .../confirm_r1b.py --dry-run          # non-holdout stand-ins (#11, #16), 2 processes; no holdout read
  uv run python .../confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
from multiprocessing import get_context
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2" if _v == "POLARS_MAX_THREADS" else "1"
os.environ["H06_DATA"] = "r1b"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import explore as X  # noqa: E402
import ncd_core as M  # noqa: E402
import round1b as R1  # noqa: E402
import build as B  # noqa: E402  (round-1 scheme: calendar, windows, carry_forward, cluster_intents, room_at)
import build_r1b as BR  # noqa: E402

ROOT = X.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
from infra.shared import common as C  # noqa: E402

HYP = "H06"
SH = ROOT / "data/processed/shared"
EMB = SH / "embeddings"
OUT = ROOT / "data/processed/H06-neutral-cooperative-dynamics"
TARGET = "G22"
STANDINS = ["G11", "G16"]                 # unchanged from confirm_holdout.py (N = 7 free weeks; #22 has N = 9)
LADDER = ["km8", "km24", "km64", "wd8", "wd24", "wd64"]
PRIMARY = "km24"
SECOND = "bge_sr_km24"                    # the second embedding model, style-residualized (round 1b comparison set)
VARIANTS = {"gte_sr": ("gte_modernbert", "statements_style_resid_period32_gte_modernbert"),
            "bge_sr": ("bge_small", "statements_style_resid_period32_bge_small")}

FROZEN = {
    "written": "2026-10-04, re-frozen on round-1b inputs before any #22 data was read",
    "C1": "(unchanged) H06 P1 rule on gte_sr km24 ladder: LLR_NH >= 2, LLR_NC >= 2 in >= 4/6 clusterings, NCD adequate "
          "(joint PPC p >= 0.01), mu_NCD < mu_L/2. Round 1/1b predict C1 FAILS.",
    "C2": "(unchanged rule) on gte_sr km24: (a) joint PPC p < 0.01 for NCD and Hubbell; (b) copy-consistency < 0.8 and "
          "outside NCD's 95% interval; (c) singleton fraction above NCD's 97.5% point. C2 holds if (a) and ((b) or (c)); "
          "refuted if NCD adequate and (b), (c) both fail.",
    "C2-r1b": "C2 holds on gte_sr km24 AND on bge_sr km24 (confirmed); refuted if refuted on either; else inconclusive. "
              "Reason: round 1b found fragmentation and inadequacy robust to the embedding model and style removal.",
    "C3-r1b": "(secondary) beta_hat not below the Hubbell predictive median on gte_sr km24 AND on bge_sr km24; if the two "
              "models disagree: 'embedding-dependent' (not confirmed). Reason: round 1b beta_hat changed sign with the model.",
    "C4": "(unchanged) lambda_bar above the day-shift independent-agents null (one-sided p < 0.05), gte_sr km24.",
    "C5-r1b": "(secondary, new) work labels (DQ4), if testable (>= 3 labelled slots per window, >= 20 changes): NCD not "
              "adequate (joint PPC p < 0.01) and singleton fraction >= 0.6; else n/a. Reason: round 1b R1b-3(b,c).",
    "C6-r1b": "(secondary, new) copying channel on attention labels: MH OR(read vs posted-unread) > 1.5 with lower 95% "
              "bound > 1; inconclusive with < 5 switches in either class. Reason: round 1b pooled OR 8.6 [4.5, 16.4].",
    "overall": "C1 confirmed -> 'NCD supported'; else 'C1 not confirmed; C2-r1b confirmed / refuted / inconclusive'",
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
    from infra.shared import holdout_ledger as hl
    r = hl.check(HYP, TARGET, "message content", ["content_alignment", "artifact_lineage"])
    print(f"ledger {TARGET}: allowed={r['allowed']} needs_disclosure={r['needs_disclosure']} "
          f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
          f"same_family_runs={sorted({u['hypothesis'] for u in r['prior_runs_same_family']})} "
          f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}", flush=True)
    return r["allowed"] or not strict


# ------------------------------------------------------------------ inputs
def period_style_vectors(goal: int, srows: np.ndarray, model: str, shared_file: str) -> tuple[np.ndarray, dict]:
    """style_resid_period vectors for the goal's intent statements `srows`: refit within (goal, regime, intent) on the
    period's own rows when it has >= MIN_FIT_PERIOD of them (style_resid.py's rule; for a held-out period the shared
    file holds the regime fallback). Returns (vectors, info)."""
    import embed_models as EM
    import style_resid as SR
    st = pl.read_parquet(EMB / "statements.parquet").with_row_index("srow")
    sub = st.filter(pl.col("srow").is_in(srows.tolist())).sort("srow")
    assert (sub["srow"].to_numpy() == srows).all()
    assert (sub["kind"] == "intent").all() and sub["goal_no"].n_unique() == 1 and sub["regime"].n_unique() == 1
    shared = np.asarray(np.load(EMB / f"{shared_file}.npy", mmap_mode="r")[srows], dtype=np.float64)
    if len(srows) < SR.MIN_FIT_PERIOD:
        return shared, {"fit": "regime_fallback (shared)", "n": int(len(srows))}
    U = np.asarray(np.load(EMB / f"statements_white32_{EM.MODELS[model]['suffix']}.npy", mmap_mode="r")[srows], dtype=np.float64)
    U /= np.maximum(np.linalg.norm(U, axis=1, keepdims=True), 1e-12)
    F = SR.style_matrix(sub.select("kind", "src_row"))
    allm = np.ones(len(srows), bool)
    c, r2 = SR.fit_style(U, F, allm)
    R = SR.apply_style(U, F, allm, c)
    cos = (R * (shared / np.maximum(np.linalg.norm(shared, axis=1, keepdims=True), 1e-12))).sum(1)
    return R, {"fit": "period refit", "n": int(len(srows)), "style_r2": r2,
               "cos_to_shared_min": float(cos.min()), "cos_to_shared_median": float(np.median(cos))}


def int_labels(goal, cal, wins, allow_holdout):
    """build_r1b.int_labels for the two style-residualized variants, holdout filter lifted only on the confirm path."""
    st = pl.read_parquet(EMB / "statements.parquet").with_row_index("srow").filter(
        (pl.col("kind") == "intent") & (pl.col("goal_no") == goal))
    if not allow_holdout:
        st = st.filter(~pl.col("holdout"))
    period_rows = np.sort(st["srow"].to_numpy())
    vec, info = {}, {}
    for var, (model, fname) in VARIANTS.items():
        V, info[var] = period_style_vectors(goal, period_rows, model, fname)
        vec[var] = dict(zip(period_rows.tolist(), range(len(period_rows)))), V
    st = st.join(cal.select("pt_date", "day", "win_start", "win_end"), on="pt_date", how="inner")
    st = st.filter((pl.col("t") >= pl.col("win_start")) & (pl.col("t") <= pl.col("win_end")))
    st = st.with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // (B.W * 60)).cast(pl.Int16).alias("win"))
    st = B.room_at(st.drop("room"), "t")
    st = st.join(wins.select("day", "win", "gwin"), on=["day", "win"], how="inner").sort("t", "srow")
    assert len(st["regime"].unique()) == 1
    rows = st["srow"].to_numpy()
    cl_all = {}
    for var in VARIANTS:
        pos, V = vec[var]
        Xv = V[[pos[r] for r in rows]].copy()
        Xv /= np.maximum(np.linalg.norm(Xv, axis=1, keepdims=True), 1e-9)
        cl = B.cluster_intents(Xv, len(Xv), B.SEED + goal)
        cl_all.update({BR.col(var, k): v for k, v in cl.items()})
    intents = st.select("t", "agent", "room", "day", "win", "gwin").with_columns([pl.Series(k, v) for k, v in cl_all.items()])
    cols = list(cl_all)
    last = intents.sort("t").group_by("gwin", "agent", maintain_order=True).agg(
        [pl.col("room").last()] + [pl.col(k).last() for k in cols])
    lab = None
    for k in ["room"] + cols:
        cf = B.carry_forward(last.select("gwin", "agent", k), wins, k, B.CARRY)
        lab = cf if lab is None else lab.join(cf.drop("age"), on=["gwin", "agent"], how="full", coalesce=True)
    return lab.join(wins.select("gwin", "day", "win"), on="gwin").sort("gwin", "agent"), info


def art_labels(goal, wins, allow_holdout):
    ps = pl.read_parquet(SH / "project_states.parquet").filter(
        (pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all") & (pl.col("goal_no") == goal))
    if not allow_holdout:
        ps = ps.filter(~pl.col("holdout"))
    return BR.project_labels(ps.select("pt_date", "win", "agent", "room", "project"), wins, None)


def build_scope(scope: str, out: Path, allow_holdout: bool) -> dict:
    goal = int(scope[1:3])
    held = set(C.load_holdout()["goal_periods_held_out"])
    assert (goal in held) == allow_holdout, "target / stand-in mismatch"
    cal = B.calendar(goal, allow_holdout=allow_holdout)
    if allow_holdout:
        assert cal["ho"].all()
    else:
        assert not cal["ho"].any()
    wins = B.windows(cal)
    out.mkdir(parents=True, exist_ok=True)
    lint, sinfo = int_labels(goal, cal, wins, allow_holdout)
    art, pa = art_labels(goal, wins, allow_holdout)
    work, pw = BR.work_labels(goal, cal, wins, None)
    for nm, df in (("windows", wins), ("labels_int", lint), ("labels_art", art), ("labels_work", work),
                   ("projects_art", pa), ("projects_work", pw)):
        df.write_parquet(out / f"{nm}.parquet", compression="zstd")
    info = {"scope": scope, "goal": goal, "style_refit": sinfo, "allow_holdout": allow_holdout}
    (out / "scope.json").write_text(json.dumps(info, indent=1, default=str))
    (out / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H06-neutral-cooperative-dynamics/analysis/confirm_r1b.py", "git_commit": C.git_commit(),
        "inputs": [{"source": "ai-village", "revision": C.REVISION,
                    "tables": ["calendar", "rooms_timeline", "project_states", "work_commits", "work_repos",
                               "embeddings/statements", "embeddings/statements_white32_{bge_small,gte_modernbert}",
                               "embeddings/statements_style_resid_period32_{bge_small,gte_modernbert}",
                               "text_features + intentions_text (style features, memory only)",
                               "artifact_mentions", "artifacts", "chat_core", "context_ledger_items", "call_windows"]}],
        "params": {"frozen": FROZEN, "variants": VARIANTS, "W": B.W, "carry": B.CARRY},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1, default=str))
    return info


# ------------------------------------------------------------------ analysis
def load(folder: Path, allow_holdout: bool):
    wins = pl.read_parquet(folder / "windows.parquet").sort("gwin")
    dates = sorted(set(wins["pt_date"].to_list()))
    g = int(folder.name[1:3])
    if not allow_holdout:
        assert not any(C.holdout_mask(dates, [g] * len(dates))), "holdout"
    keep = wins["gwin"].to_list()
    remap = {x: i for i, x in enumerate(keep)}
    _, day = np.unique(wins["day"].to_numpy(), return_inverse=True)
    labs = {nm: pl.read_parquet(folder / f"labels_{nm}.parquet").filter(pl.col("gwin").is_in(keep)) for nm in ("int", "art", "work")}
    return wins, day, remap, labs


def copying(folder: Path, wins, day, remap, labs, allow_holdout):
    """Round 1b R1b-4 on one scope (attention labels): V read / U posted-unread / N, MH over abundance strata."""
    g = int(folder.name[1:3])
    msgs = R1._messages([g])
    reads = R1._reads([g], msgs["message_id"].unique().to_list())
    df = labs["art"]
    if df.height == 0:
        return {"ok": False}
    proj = pl.read_parquet(folder / "projects_art.parquet")
    pid2name = dict(zip(proj["project_id"].to_list(), proj["project"].to_list()))
    lab, agents = X.matrix(df, "project_id", remap, wins.height)
    T, N = lab.shape
    half = dt.timedelta(minutes=15)
    ws = [t - half for t in wins["t_mid"].to_list()]
    we = [t + half for t in wins["t_mid"].to_list()]
    import bisect
    rd_by = {}
    for mid, rc, tc in reads.iter_rows():
        if rc not in rd_by.setdefault(mid, {}) or tc < rd_by[mid][rc]:
            rd_by[mid][rc] = tc

    def widx(t_):
        i = bisect.bisect_right(ws, t_) - 1
        return i if 0 <= i < T and t_ < we[i] else None
    ai = {ag: i for i, ag in enumerate(agents)}
    V, posted = {}, {}
    for mid, tm_, snd, pr in msgs.select("message_id", "t", "agent", "project").iter_rows():
        tp = widx(tm_)
        if tp is not None:
            posted.setdefault(tp, []).append((mid, snd, pr))
        for rc, tr in rd_by.get(mid, {}).items():
            if rc == snd or rc not in ai:
                continue
            tw = widx(tr)
            if tw is not None:
                V.setdefault((tw, ai[rc]), set()).add(pr)
    rows = []
    for t in range(T - 1):
        if day[t] != day[t + 1]:
            continue
        held = {}
        for a in range(N):
            if lab[t, a] >= 0:
                held.setdefault(lab[t, a], set()).add(a)
        for a in range(N):
            if lab[t, a] < 0 or lab[t + 1, a] < 0:
                continue
            Va = V.get((t, a), set())
            Ua = {pr for mid, snd, pr in posted.get(t, []) if snd != agents[a]
                  and (rd_by.get(mid, {}).get(agents[a]) is None or rd_by[mid][agents[a]] >= we[t])}
            for q, hs in held.items():
                if q == lab[t, a] or not (hs - {a}):
                    continue
                name = pid2name.get(int(q))
                rows.append((min(len(hs - {a}), 3), "V" if name in Va else ("U" if name in Ua else "N"), int(lab[t + 1, a] == q)))
    out = {"n_candidates": {c: sum(r[1] == c for r in rows) for c in "VUN"},
           "n_switches": {c: sum(r[1] == c and r[2] for r in rows) for c in "VUN"}}
    for e, ref in (("V", "N"), ("V", "U"), ("U", "N")):
        tab = []
        for k in (1, 2, 3):
            sub = [r for r in rows if r[0] == k]
            tab.append((sum(r[1] == e and r[2] for r in sub), sum(r[1] == e and not r[2] for r in sub),
                        sum(r[1] == ref and r[2] for r in sub), sum(r[1] == ref and not r[2] for r in sub)))
        out[f"OR_{e}_vs_{ref}"] = R1.mh_or(tab)
    out["ok"] = True
    return out


def run_scope(args):
    scope, folder, allow_holdout = args
    folder = Path(folder)
    t0 = time.time()
    wins, day, remap, labs = load(folder, allow_holdout)
    T = wins.height
    S, free = {}, {}
    lint = labs["int"]
    agents = sorted(set(lint["agent"].to_list()))
    cols = [k for k in LADDER + [SECOND] if k in lint.columns and (lint[k] >= 0).any()]
    li = {k: X.matrix(lint, k, remap, T, agents)[0] for k in cols}
    if PRIMARY in li:
        mask = li[PRIMARY] >= 0
        bank = M.Bank(mask, day, seed=M._seed(scope, "int"))
        for k, lab in li.items():
            assert ((lab >= 0) == mask).all()
            free[k] = R1.freestats(lab, day, M._seed(scope, k, "r1b"))
            S[k] = R1.slim(X.analyse_labelset(f"{scope}/{k}", lab, day, bank, extra=(k in (PRIMARY, SECOND)), seed=0))
    for nm in ("art", "work"):
        df = labs[nm]
        if df.height == 0:
            continue
        lab, _ = X.matrix(df, "project_id", remap, T)
        free[nm] = R1.freestats(lab, day, M._seed(scope, nm, "r1b"))
        if (lab >= 0).sum(1).mean() < X.MIN_PER_WIN:
            S[nm] = {"testable": False, "mean_per_win": float((lab >= 0).sum(1).mean())}
            continue
        S[nm] = R1.slim(X.analyse_labelset(f"{scope}/{nm}", lab, day, M.Bank(lab >= 0, day, seed=M._seed(scope, nm, "r1b")),
                                           extra=True))
    res = {"scope": scope, "T": T, "sets": S, "free": free,
           "P1": X.verdict_p1({k: S[k] for k in LADDER if k in S}) if PRIMARY in S else {"verdict": "n/a"},
           "copying": copying(folder, wins, day, remap, labs, allow_holdout)}
    res["verdicts"] = decide(res)
    res["secs"] = time.time() - t0
    (folder / "confirm_r1b.json").write_text(json.dumps(res, indent=1, default=float))
    return scope, res


def c2_on(p):
    if not p or not p.get("testable"):
        return None, None, {}
    f = p["fits"]
    a = (f["ncd"]["ppc_joint"] < 0.01) and (f["hubbell"]["ppc_joint"] < 0.01)
    b = (p["copyfrac"] < 0.8) and not (f["ncd"]["pred"]["copyfrac"][1] <= p["copyfrac"] <= f["ncd"]["pred"]["copyfrac"][2])
    c = p["obs"]["single"] > f["ncd"]["pred"]["single"][2]
    return bool(a and (b or c)), bool(f["ncd"]["adequate"] and not b and not c), \
        {"a_models_inadequate": a, "b_copy_low": b, "c_singletons_high": c,
         "ppcj": {m: f[m]["ppc_joint"] for m in M.MODELS}, "copyfrac": p["copyfrac"], "single": p["obs"]["single"],
         "single_pred_ncd": f["ncd"]["pred"]["single"], "LLR_NH": p["LLR_NH"], "LLR_NC": p["LLR_NC"]}


def c3_on(p):
    if not p or not p.get("testable"):
        return None, {}
    b, med = p["obs"]["beta"], p["fits"]["hubbell"]["pred"]["beta"][3]
    return bool(not (np.isfinite(b) and b < med)), {"beta": b, "beta_hub_median": med}


def decide(r):
    S = r["sets"]
    V = {}
    V["C1_ncd_supported"] = r["P1"].get("verdict") == "supported"
    c2p, c2p_ref, n1 = c2_on(S.get(PRIMARY))
    c2s, c2s_ref, n2 = c2_on(S.get(SECOND))
    V["C2_gte_sr"], V["C2_bge_sr"] = {"holds": c2p, "refuted": c2p_ref, **n1}, {"holds": c2s, "refuted": c2s_ref, **n2}
    if c2p is None or c2s is None:
        V["C2-r1b"] = "n/a (insufficient labels)"
    else:
        V["C2-r1b"] = "confirmed" if (c2p and c2s) else ("refuted" if (c2p_ref or c2s_ref) else "inconclusive")
    h3p, d3p = c3_on(S.get(PRIMARY))
    h3s, d3s = c3_on(S.get(SECOND))
    V["C3-r1b"] = {"verdict": "n/a" if h3p is None or h3s is None else (
        "confirmed" if (h3p and h3s) else ("embedding-dependent" if h3p != h3s else "not confirmed")),
        "gte_sr": d3p, "bge_sr": d3s}
    nul = (S.get(PRIMARY) or {}).get("null_ind", {})
    V["C4_coordination"] = bool(nul.get("lam_p_greater", 1.0) < 0.05)
    w = S.get("work")
    if not w or not w.get("testable"):
        V["C5-r1b"] = "n/a (work labels not testable)"
    else:
        ok = w["fits"]["ncd"]["ppc_joint"] < 0.01 and w["obs"]["single"] >= 0.6
        V["C5-r1b"] = {"verdict": "confirmed" if ok else "not confirmed", "ncd_ppc_joint": w["fits"]["ncd"]["ppc_joint"],
                       "single": w["obs"]["single"]}
    cp = r.get("copying", {})
    if not cp.get("ok") or min(cp["n_switches"]["V"], cp["n_switches"]["U"]) < 5:
        V["C6-r1b"] = {"verdict": "inconclusive (underpowered)", **({k: cp[k] for k in ("n_switches", "n_candidates")} if cp.get("ok") else {})}
    else:
        o = cp["OR_V_vs_U"]
        V["C6-r1b"] = {"verdict": "confirmed" if (o["or"] > 1.5 and o["lo"] > 1) else "not confirmed", "OR_V_vs_U": o,
                       "n_switches": cp["n_switches"]}
    V["overall"] = ("C1 confirmed (NCD supported)" if V["C1_ncd_supported"] else f"C1 not confirmed; C2-r1b {V['C2-r1b']}")
    return V


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        ledger_status(strict=False)
        base = OUT / "confirm_r1b_dryrun"
        infos = {s: build_scope(s, base / s, allow_holdout=False) for s in STANDINS}
        for s, i in infos.items():
            print(f"[dry run, stand-in {s}] style refit: {json.dumps(i['style_refit'], default=float)}", flush=True)
        with get_context("spawn").Pool(2) as pool:
            res = dict(pool.map(run_scope, [(s, str(base / s), False) for s in STANDINS]))
        (base / "confirm_r1b_dryrun.json").write_text(json.dumps(
            {"frozen": FROZEN, "standins": {s: {"verdicts": r["verdicts"], "P1": r["P1"], "secs": r["secs"],
                                                "style_refit": infos[s]["style_refit"]} for s, r in res.items()},
             "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1, default=float))
        for s, r in res.items():
            print(f"[dry run, stand-in {s}] {json.dumps(r['verdicts'], default=float)}", flush=True)
        return
    if not (a.confirm and a.ack):
        raise SystemExit("refusing: the confirmatory run reads the locked holdout (#22). "
                         "Use --dry-run, or --confirm --i-understand-this-uses-the-locked-holdout after sign-off.")
    must = [Path(__file__).resolve(), HERE / "CONFIRM_R1B.md", HERE.parent / "README.md", HERE / "explore.py",
            HERE / "ncd_core.py", HERE / "round1b.py", HERE.parent / "scheme/build.py", HERE.parent / "scheme/build_r1b.py",
            ROOT / "infra/shared/style_resid.py"]
    if not committed_clean(must):
        raise SystemExit("refusing: commit confirm_r1b.py, CONFIRM_R1B.md, the card and the code it imports first")
    if not ledger_status(strict=True):
        raise SystemExit("refusing: holdout_ledger.check() reports a same-family prior run on #22; Vivian decides")
    folder = OUT / "confirm_r1b" / TARGET
    build_scope(TARGET, folder, allow_holdout=True)
    _, r = run_scope((TARGET, str(folder), True))
    print(json.dumps(r["verdicts"], indent=1, default=float))


if __name__ == "__main__":
    main()
