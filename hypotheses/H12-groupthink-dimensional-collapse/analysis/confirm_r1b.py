"""H12 confirmatory test on the LOCKED HOLDOUT -- ROUND-1B RE-FREEZE of `confirm.py` (card Amendment 2). Written
2026-10-04 after round 1b, before any holdout data was read. NOT RUN. `confirm.py` stays byte-for-byte unchanged; its
unit / day selection and per-unit helpers are imported.

Why (holdout ledger item 8, RE-A1): confirm.py reads the buggy `activity_bins` (about half of all events dropped) and
the cross-day edge; RE-A1 expects C1-C3 and C5 to fail as frozen. Round 1b: under the DQ8-calibrated null (each day
trimmed to its all-present window, block-shift edge) the activity "market mode" survives in 7/24 exploratory units, talk
modes in 21/24, content modes in 24/24 in both embedding models; the lull filter is biased (H25) and joint lulls nearly
vanish on the fixed table (median share 0.009); day-1 PR expansion (C5) is fragile (bge 13/16, gte 11/16, restatements
removed 9/15); "loops" are restatement (DQ5), not copying.

Inputs: activity_bins_fixed (H12_DATA_VERSION=fixed); trimmed block-shift edge (h12lib.trim_rows,
spectrum_test_blockshift; + H38's explained joint silences from outages_fixed as a variant); statement vectors in BOTH
models (bge_small, gte_modernbert; regime whitener, 64-d, non-holdout fit); DQ5 statement_flags for restatements.
Context-ledger visibility, the work ledger, failures and nudge targets are not inputs of this design.

Re-frozen predictions (ids kept where unchanged; units and transitions as confirm.py):
  C1-r1b  activity mode is mostly the scheduler: k_trim_bs(activity) >= 1 in <= 1/2 of the eligible held-out units.
          (Replaces "k_cd(activity) = 1 in >= 2/3"; exploration under the calibrated null: 7/24.)
  C1t-r1b NEW: a talk mode exists: k_trim_bs(talk) >= 1 in >= 2/3 of the eligible held-out units (exploration 21/24).
  C2-r1b  uniform shape among units with k_cd(activity) >= 1: sign share >= 0.8 AND VR/lambda1 >= 0.7 in >= 2/3. (The
          0.85 of confirm.py was set from buggy-table values; 0.7 is the card's pre-registered P2 threshold; round 1b
          16/18.)
  C3      RETIRED: the lull filter is biased (H25 synthetic) and joint lulls nearly vanish on the fixed table, so the
          lull-fraction / lull-drop correlation has no range. Reported descriptively only.
  C4-r1b  content mode k_cd(content) >= 1 in >= 2/3 AND surviving agent-day centering in >= 2/3, in BOTH models.
  C5-r1b  PRday(day 1) > median PRday(days 2+) in >= 2/3 of periods with >= 3 days, in BOTH models AND with
          restatements removed (either model's DQ5 flag) in both models. (Stricter: round 1b showed it is fragile.)
  C6-r1b  median relative first-hour PR change over the held-out transitions > 0, in both models.
  C7      unchanged: #22 mean PRday (bge) > 14.82; gte reported descriptively (no frozen gte threshold).
  C8-r1b  Spearman(restatement share per regime-III held-out day [DQ5 flag of either model, chat], PRday) <= -0.5 in
          both models (replaces the raw bge cos > 0.95 near-duplicate share; DQ5: restatement, not copying).
Ledger gate (holdout items 2, 3, 4): the activity/talk spectra (C1-r1b, C1t-r1b, C2-r1b) are Curie-Weiss-family
statistics on #32/#34 (H05's executed run), #45 (H02's) and #46-#50 (H04's). They are computed only on #28, #29 and
the #51 tail unless --vivian-approved-activity-reuse is given. Content criteria use every held-out unit.

Usage:
  uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/confirm_r1b.py --dry-run
  uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

os.environ["H12_DATA_VERSION"] = "fixed"
for _v in ("OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h12lib as L  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

import run_units as R  # noqa: E402
import confirm as CF  # noqa: E402  (frozen select_days / unit_name / spin_days_mem; main() is not called)

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import embed_models as EM  # noqa: E402
import holdout_ledger as HL  # noqa: E402

assert L.DATA_VERSION == "fixed"
FLAG_A, FLAG_B = "--confirm", "--i-understand-this-uses-the-locked-holdout"
MODELS = {"bge": "bge_small", "gte": "gte_modernbert"}
ACT_OK_GOALS = {28, 29, 51}            # activity/talk spectra allowed here without override (no same-family prior run)
LEDGER = {"G28": 28, "G29": 29, "G32": 32, "G34": 34, "G45": 45, "G46": 46, "G47": 47, "G49": 49, "G50": 50, "#51-tail": 51}


def load_data(sel: pl.DataFrame):
    ab = (pl.scan_parquet(L.AB).select("pt_date", "minute", "agent", "state")
          .filter(pl.col("pt_date").is_in(sel["pt_date"].to_list())).collect().join(sel.select("pt_date", "unit"), on="pt_date"))
    st = (pl.read_parquet(L.SH / "embeddings/statements.parquet").with_row_index("srow")
          .filter(pl.col("pt_date").is_in(sel["pt_date"].to_list())).join(sel.select("pt_date", "unit"), on="pt_date"))
    fl = pl.read_parquet(L.SH / "statement_flags.parquet", columns=["srow", "self_repeat", "self_repeat_gte"])
    st = st.with_columns(pl.Series("restate", (fl["self_repeat"].to_numpy() | fl["self_repeat_gte"].to_numpy())[st["srow"].to_numpy()]
                                   & (st["kind"] == "chat").to_numpy()))
    kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy(); reg = st["regime"].to_numpy()
    Wv = {}
    for mk, model in MODELS.items():
        Ec = np.load(L.SH / f"embeddings/chat_{model}.npy", mmap_mode="r")
        Ei = np.load(L.SH / f"embeddings/intentions_{model}.npy", mmap_mode="r")
        W = np.zeros((st.height, 64), dtype=np.float32)
        for r in np.unique(reg):
            Wr = EM.load_whitener(r, 64, model)
            for k, E in (("chat", Ec), ("intent", Ei)):
                m = (reg == r) & (kind == k)
                if m.any():
                    o = np.argsort(src[m])
                    z = np.empty((m.sum(), 64), np.float32)
                    z[o] = Wr(np.asarray(E[src[m][o]], dtype=np.float32))
                    W[m] = z
        Wv[mk] = W
    return ab, st.with_row_index("row"), Wv


def spin_variants(ab_u: pl.DataFrame, rng, n_surr):
    """Activity and talk spins per day (confirm.spin_days_mem), trimmed to the activity all-present window, block-shift
    edge (run_units.r1b_spin_variants, on in-memory spins); trim_stall_bs also drops H38's explained joint silences."""
    act = CF.spin_days_mem(ab_u, "act")
    talk_all = CF.spin_days_mem(ab_u, "talk")
    dates = sorted(ab_u["pt_date"].unique().to_list())
    sm = (pl.read_parquet(L.STALLS_FIXED, columns=["pt_date", "minute", "js", "explained"])
          .filter(pl.col("pt_date").is_in(dates) & pl.col("js") & pl.col("explained")))
    X = np.concatenate(talk_all, 1)
    keep_t = (X > 0).sum(1) >= R.MIN_TALK
    talk = [d[keep_t] for d in talk_all]
    out = {}
    for ch, days in (("act", act), ("talk", talk)):
        if days[0].shape[0] < 4:
            out[ch] = {"N": int(days[0].shape[0])}
            continue
        for name in ("trim_bs", "trim_stall_bs"):
            kd, km = [], []
            for A_act, A, dt_ in zip(act, days, dates):
                keep = L.trim_rows(A_act)
                if name == "trim_stall_bs":
                    bad = sm.filter(pl.col("pt_date") == dt_)["minute"].to_numpy()
                    keep[bad[bad < A.shape[1]]] = False
                kd.append(A[:, keep]); km.append(np.flatnonzero(keep))
            T = sum(x.shape[1] for x in kd)
            if T <= days[0].shape[0]:
                out.setdefault(ch, {})[name] = {"k": None}
                continue
            r = L.spectrum_test_blockshift(kd, km, n_surr, rng)
            out.setdefault(ch, {})[name] = {"k": r["k"], "l1_edge": float(r["eig"][0] / r["edge"]) if r["edge"] else None}
        out[ch]["N"] = int(days[0].shape[0])
    return out


def unit_stats(u, ab, st, Wv, sel, rng, n_surr, do_spins):
    ab_u = ab.filter(pl.col("unit") == u)
    days = CF.spin_days_mem(ab_u, "act")
    o = {"unit": u, "N": days[0].shape[0], "D": len(days)}
    if o["N"] >= 4 and len(days) >= 2:
        X = np.concatenate(days, 1)
        w, V, C = L.corr_eig(X, vectors=True)
        cd = L.spectrum_test(days, n_surr, rng, "spin", "crossday")
        u_ = np.ones(len(w)) / np.sqrt(len(w))
        o.update({"k_cd": cd["k"], "sign_share": L.mode_summary(V[:, 0])["sign_share"], "VR_l1": float(u_ @ C @ u_ / w[0]),
                  "lull_frac": float(1 - L.lull_filter(X).shape[1] / X.shape[1])})
        if do_spins:
            o["spins_r1b"] = spin_variants(ab_u, rng, n_surr)
    cal_u = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date").is_in(sel.filter(pl.col("unit") == u)["pt_date"].to_list()))
    rows = st.filter(pl.col("unit") == u)
    for mk in MODELS:
        cdays, cag = R.content_days(u, rows, Wv[mk], cal_u)
        if len(cag) >= 4:
            cc = L.spectrum_test(cdays, n_surr, rng, "content", "crossday")
            dc = []
            for A in cdays:
                pres = np.abs(A).sum(2) > 0
                mu = A.sum(1) / np.maximum(pres.sum(1), 1)[:, None]
                dc.append(np.where(pres[:, :, None], A - mu[:, None, :], 0.0))
            ccd = L.spectrum_test(dc, n_surr, rng, "content", "crossday")
            o[f"k_content_{mk}"] = cc["k"]; o[f"k_content_dc_{mk}"] = ccd["k"]
    return o


def frac(xs):
    xs = [x for x in xs if x is not None]
    return (float(np.mean(xs)) if xs else None), len(xs)


def run(holdout: bool, act_override: bool):
    goals = CF.HOLDOUT_GOALS if holdout else CF.STANDIN_GOALS
    trans = CF.TRANSITIONS_HO if holdout else CF.STANDIN_TRANSITIONS
    free = CF.FREE_CHECK if holdout else CF.STANDIN_FREE
    n_surr = CF.N_SURR if holdout else 50
    tgoals = sorted(set(goals) | {g for t in trans for g in t} | {free})
    sel = CF.select_days(holdout, tgoals)
    ab, st, Wv = load_data(sel)
    rng = np.random.default_rng([L.SEED, 17 if holdout else 18])
    units = [u for u in sel["unit"].unique().sort().to_list() if int(u.rstrip("abt")) in goals or u == "51t"]
    goal_of = lambda u: 51 if u == "51t" else int(u.rstrip("ab"))   # noqa: E731
    act_ok = lambda u: (not holdout) or act_override or goal_of(u) in ACT_OK_GOALS   # noqa: E731
    res = [unit_stats(u, ab, st, Wv, sel, rng, n_surr, act_ok(u)) for u in units]
    res = [r for r in res if r["N"] >= 10 and r["D"] >= 2]
    O = {"mode": "CONFIRM (holdout, round-1b re-freeze)" if holdout else "DRY RUN (non-holdout stand-ins, round-1b re-freeze)",
         "activity_units": [r["unit"] for r in res if "spins_r1b" in r], "units": res}
    sp = [r for r in res if "spins_r1b" in r]
    f1, n1 = frac([None if r["spins_r1b"].get("act", {}).get("trim_bs", {}).get("k") is None else r["spins_r1b"]["act"]["trim_bs"]["k"] >= 1 for r in sp])
    O["C1-r1b"] = {"frac_act_mode_trim_bs": f1, "n": n1, "pass": bool(f1 is not None and f1 <= 0.5)}
    ft, nt = frac([None if r["spins_r1b"].get("talk", {}).get("trim_bs", {}).get("k") is None else r["spins_r1b"]["talk"]["trim_bs"]["k"] >= 1 for r in sp])
    O["C1t-r1b"] = {"frac_talk_mode_trim_bs": ft, "n": nt, "pass": bool(ft is not None and ft >= 2 / 3)}
    s1 = [r for r in sp if r.get("k_cd", 0) >= 1]
    f2 = float(np.mean([(r["sign_share"] >= 0.8) and (r["VR_l1"] >= 0.7) for r in s1])) if s1 else None
    O["C2-r1b"] = {"frac": f2, "n": len(s1), "pass": bool(f2 is not None and f2 >= 2 / 3)}
    O["C3_retired_descriptive"] = {"lull_frac": {r["unit"]: r.get("lull_frac") for r in res}}
    O["C4-r1b"] = {}
    for mk in MODELS:
        cc = [r for r in res if r.get(f"k_content_{mk}") is not None]
        fa = float(np.mean([r[f"k_content_{mk}"] >= 1 for r in cc])) if cc else None
        fb = float(np.mean([r[f"k_content_dc_{mk}"] >= 1 for r in cc])) if cc else None
        O["C4-r1b"][mk] = {"frac_k": fa, "frac_dc": fb, "pass": bool(cc and fa >= 2 / 3 and fb >= 2 / 3)}
    O["C4-r1b"]["pass"] = all(O["C4-r1b"][mk]["pass"] for mk in MODELS)
    # PR tables per model, with and without restatements
    PR = {}
    for mk in MODELS:
        for tag, rows in (("all", st), ("dedup", st.filter(~pl.col("restate")))):
            p30s, pdays = [], []
            for u in sel["unit"].unique().to_list():
                a_, b_ = R.pr_unit(u, rows.filter(pl.col("unit") == u), Wv[mk], rng)
                p30s.append(a_); pdays.append(b_)
            PR[(mk, tag)] = (pl.concat(p30s, how="diagonal_relaxed"), pl.concat(pdays, how="diagonal_relaxed"))
    O["C5-r1b"] = {}
    for key, (p30, pday) in PR.items():
        hi = n = 0
        for g in goals:
            dd = sorted(sel.filter(pl.col("goal_no") == g)["pt_date"].to_list())
            if len(dd) < 3:
                continue
            d1 = pday.filter(pl.col("pt_date") == dd[0])["prday"]
            later = pday.filter(pl.col("pt_date").is_in(dd[1:]))["prday"].drop_nans()
            if len(d1) and d1[0] == d1[0] and len(later):
                n += 1; hi += int(d1[0] > later.median())
        O["C5-r1b"][f"{key[0]}_{key[1]}"] = {"n": n, "day1_higher": hi, "pass": bool(n and hi / n >= 2 / 3)}
    O["C5-r1b"]["pass"] = all(v["pass"] for v in O["C5-r1b"].values())
    O["C6-r1b"] = {}
    for mk in MODELS:
        p30 = PR[(mk, "all")][0]
        rels = []
        for a, b in trans:
            da = sorted(sel.filter(pl.col("goal_no") == a)["pt_date"].to_list()); db = sorted(sel.filter(pl.col("goal_no") == b)["pt_date"].to_list())
            if not da or not db:
                continue
            fa = p30.filter((pl.col("pt_date") == da[-1]) & (pl.col("win30") <= 1))["pr"].drop_nans()
            fb = p30.filter((pl.col("pt_date") == db[0]) & (pl.col("win30") <= 1))["pr"].drop_nans()
            if len(fa) and len(fb):
                rels.append((fb.mean() - fa.mean()) / fa.mean())
        O["C6-r1b"][mk] = {"n": len(rels), "median_rel": float(np.median(rels)) if rels else None, "pass": bool(rels and np.median(rels) > 0)}
    O["C6-r1b"]["pass"] = all(O["C6-r1b"][mk]["pass"] for mk in MODELS)
    fd = sorted(sel.filter(pl.col("goal_no") == free)["pt_date"].to_list())
    O["C7"] = {mk: PR[(mk, "all")][1].filter(pl.col("pt_date").is_in(fd))["prday"].drop_nans().mean() for mk in MODELS}
    O["C7"].update({"threshold_bge": CF.SHARED_I_MEDIAN_ROUND1, "pass": bool(O["C7"]["bge"] is not None and O["C7"]["bge"] > CF.SHARED_I_MEDIAN_ROUND1)})
    r3 = sel.filter(pl.col("regime") == "III")["pt_date"].to_list()
    share = (st.filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(r3)).group_by("pt_date")
             .agg(pl.col("restate").mean().alias("restate_share"), pl.len().alias("n")).filter(pl.col("n") >= 20))
    O["C8-r1b"] = {}
    for mk in MODELS:
        j = PR[(mk, "all")][1].join(share, on="pt_date").filter(pl.col("prday").is_not_nan())
        rho = spearmanr(j["restate_share"], j["prday"]).statistic if j.height >= 4 else float("nan")
        O["C8-r1b"][mk] = {"n_days": j.height, "rho": float(rho), "pass": bool(rho <= -0.5)}
    O["C8-r1b"]["pass"] = all(O["C8-r1b"][mk]["pass"] for mk in MODELS)
    return O


def ledger_checks():
    out = {}
    for t in LEDGER:
        c = HL.check("H12", t, "message content", ["content_alignment", "spectral_mode"])
        a = HL.check("H12", t, "activity timing", ["curie_weiss_gain", "spectral_mode"])
        out[t] = {"content_allowed": c["allowed"], "activity_allowed": a["allowed"],
                  "prior_runs": sorted({u["hypothesis"] for u in c["prior_runs"]}),
                  "activity_same_family_runs": sorted({u["hypothesis"] for u in a["prior_runs_same_family"]})}
    return out


def main():
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    confirm = FLAG_A in argv and FLAG_B in argv
    if dry and confirm:
        sys.exit("choose either --dry-run or the two confirmation flags, not both")
    if not dry and not confirm:
        print("Refusing to run: this script reads the locked holdout. Use --dry-run for non-holdout stand-ins, or\n"
              f"  {FLAG_A} {FLAG_B}\nafter sign-off.", file=sys.stderr)
        sys.exit(2)
    led = ledger_checks()
    override = "--vivian-approved-activity-reuse" in argv
    if confirm:
        bad = [t for t, c in led.items() if not c["content_allowed"]]
        if bad:
            sys.exit(f"holdout_ledger.check refuses content targets {bad}")
        print("CONFIRMATORY RUN ON THE LOCKED HOLDOUT (H12, round-1b re-freeze).", flush=True)
    O = run(holdout=confirm, act_override=override)
    O["ledger"] = led
    outdir = L.OUT / ("confirm_r1b" if confirm else "confirm_r1b_dryrun")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "confirm_results.json").write_text(json.dumps(O, indent=1, default=float))
    print(json.dumps({k: (v.get("pass") if isinstance(v, dict) else None) for k, v in O.items() if k.startswith("C")}, indent=1))


if __name__ == "__main__":
    main()
