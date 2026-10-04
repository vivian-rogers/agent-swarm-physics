"""H13 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN ON ROUND-1B INPUTS (2026-10-04). WRITTEN, NOT RUN.

`confirm.py` is left byte-for-byte untouched (its helper and verdict functions are imported, not copied). What changed
is in `CONFIRM_R1B.md`. In short:
  * content: shared DQ5 statement vectors in BOTH embedding models (bge-small, gte-modernbert; scheme/build.py round-1b
    path), every C evaluated per model; overall CONFIRMED / REFUTED only when both models agree;
  * style rivals: H13's own within-unit S-a (C2, pre-registered) and the shared `style_resid_period` vectors (new
    C2p-r1b). For held-out periods the shared file holds the regime fallback, so the style regression is refit on the
    period's own chat statements (style_resid.fit_style / apply_style; style_resid's rule for confirmatory runs);
  * talk spins from `activity_bins_fixed`, each day TRIMMED to the all-present window (DQ8; infra/shared/nulls.py:
    all_present_window over agents passing the >= 4-flip rule), with a 30-min block-shift surrogate as the coupling
    baseline instead of the cross-day surrogate (STANDARDS 3: trim first, then block shifts) -> C5-r1b;
  * C3 transfer: exploration family fields from the same model's round-1b run (r1b/<model>_none/), and the exploration
    unit list captured before it is overwritten (confirm.py reassigns explore.COUNTED to the held-out units before
    explore_fields() reads it, which would fail on the real run);
  * holdout_ledger.check() per target and a commit check on the confirm path.

  uv run python hypotheses/H13-family-fields/analysis/confirm_r1b.py --dry-run
      every code path on the non-holdout stand-ins of confirm.py; writes data/processed/H13-family-fields/confirm_r1b_dryrun/
  uv run python hypotheses/H13-family-fields/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"

import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h13lib as L  # noqa: E402
import explore as E  # noqa: E402
import build as B  # noqa: E402
import confirm as C0  # noqa: E402  (frozen helpers: room_rule, style_feature_T, verdicts, PREDICTIONS, HOLDOUT_UNITS)

ROOT = B.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT))
import nulls as NU  # noqa: E402

HYP = "H13"
DATA = E.DATA
SH = B.SH
ED = B.ED
MODELS = ("bge_small", "gte_modernbert")
EXPLORE_COUNTED = list(E.COUNTED)          # captured before run() reassigns explore.COUNTED
HOLDOUT_UNITS = dict(C0.HOLDOUT_UNITS)     # unchanged
DRYRUN_UNITS = dict(C0.DRYRUN_UNITS)       # unchanged
N_SUR = 20                                 # block-shift surrogates per day (talk baseline)
BLOCK_MIN = 30
MIN_TRIM_MIN = 30                          # days whose all-present window is shorter are dropped from talk

PREDICTIONS = {
    **{k: v for k, v in C0.PREDICTIONS.items() if k in ("C1", "C2", "C3", "C4", "C6")},
    "C2p-r1b": "RE(T_field on shared style_resid_period, period refit) CI includes 0 and point <= 0.25 x RE(raw)",
    "C5-r1b": "(C5's thresholds, new talk input) RE(delta_talk) CI includes 0 and |mu| < 0.05, talk = activity_bins_fixed "
              "spins trimmed to the all-present window minus a 30-min block-shift baseline; RE(delta_content) CI includes 0 "
              "and |mu| < 0.03; room-adjusted talk b_lab n.s. in all but at most one two-room held-out unit",
    "per_model": "every C is scored in bge-small and in gte-modernbert; a C passes if it passes in both, fails if it fails "
                 "in both, else 'model-dependent'",
    "overall": "CONFIRMED if C1, C2, C3, C5-r1b pass in both models; REFUTED if confirm.py's refutation rule (with C5-r1b's "
               "talk) fires in both models; else INCONCLUSIVE",
}
REASONS = {
    "C2p-r1b": "round 1b: the shared style rival leaves 1/9 (bge) and 0/8 (gte) units, retention 0.07-0.09",
    "C5-r1b": "the cross-day surrogate on untrimmed activity is anti-conservative (DQ8 size table: 28-34%); round 1b on "
              "the fixed table: RE -0.003 [-0.021, 0.016]; thresholds unchanged",
    "models": "round 1b replicated every content verdict in both models (P1 9/15 vs 8/15)",
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
    ok = True
    for t in sorted({("#51-tail" if s[1] == 51 else f"G{s[1]:02d}") for s in HOLDOUT_UNITS.values()}):
        for mod, fam in (("message content", ["content_alignment"]), ("activity timing", ["other"])):
            r = hl.check(HYP, t, mod, fam)
            print(f"ledger {t} [{mod}]: allowed={r['allowed']} needs_disclosure={r['needs_disclosure']} "
                  f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
                  f"same_family_runs={sorted({u['hypothesis'] for u in r['prior_runs_same_family']})} "
                  f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}", flush=True)
            ok &= r["allowed"]
    return ok or not strict


# ------------------------------------------------------------------ talk: fixed bins, all-present trim, block shift
def talk_pairdays_trim(days, agent_room, seed):
    ab = pl.read_parquet(SH / "activity_bins_fixed.parquet",
                         columns=["pt_date", "minute", "agent", "state", "turns", "talk", "idle", "consolidate", "other_event"]
                         ).filter(pl.col("pt_date").is_in(days))
    agents = np.array(sorted(ab["agent"].unique().to_list()))
    N = len(agents)
    rng = np.random.default_rng(seed)
    out, info = [], {}
    pi, pj = np.triu_indices(N, 1)
    for (d,), g in ab.group_by("pt_date", maintain_order=True):
        Lm = int(g["minute"].max()) + 1
        A = -np.ones((Lm, N))
        Ev = np.zeros((Lm, N), bool)
        ai = np.searchsorted(agents, g["agent"].to_numpy())
        mi = g["minute"].to_numpy()
        A[mi, ai] = np.where(g["state"].to_numpy() == 4, 1.0, -1.0)
        Ev[mi, ai] = (g.select(pl.sum_horizontal("turns", "talk", "idle", "consolidate", "other_event")).to_series().to_numpy() > 0)
        valid = np.zeros(N, bool)
        valid[np.unique(ai)] = True
        valid &= (A[1:] != A[:-1]).sum(0) >= 4
        P = np.zeros((Lm, N), bool)
        for k in np.flatnonzero(valid & Ev.any(0)):
            ix = np.flatnonzero(Ev[:, k])
            P[ix[0]:ix[-1] + 1, k] = True
        keep = NU.all_present_window(P[:, valid]) if valid.any() else np.zeros(Lm, bool)
        info[d] = {"minutes": int(Lm), "kept": int(keep.sum()), "agents": int(valid.sum())}
        if keep.sum() < MIN_TRIM_MIN:
            continue
        m = np.flatnonzero(keep)
        S = A[m]
        valid &= (S[1:] != S[:-1]).sum(0) >= 4
        sel = valid[pi] & valid[pj]
        a, b = pi[sel], pj[sel]
        C = B.corr_cols(S, S)
        Cs = np.zeros_like(C)
        for _ in range(N_SUR):
            Y = NU.block_shift([S], [m], rng, block_min=BLOCK_MIN)[0]
            Cs += np.nan_to_num(B.corr_cols(Y, Y))
        Cs /= N_SUR
        act = (S.mean(0) + 1) / 2
        rr = lambda k: np.array([agent_room.get((int(agents[x]), d), -1) for x in k], dtype=np.int16)
        out.append(pl.DataFrame({"pt_date": [d] * len(a), "i": agents[a].astype(np.int8), "j": agents[b].astype(np.int8),
                                 "c0": C[a, b].astype(np.float32), "c0_sur": Cs[a, b].astype(np.float32),
                                 "act_i": act[a].astype(np.float32), "act_j": act[b].astype(np.float32),
                                 "room_i": rr(a), "room_j": rr(b)}))
    return (pl.concat(out) if out else None), info


# ------------------------------------------------------------------ style_resid_period refit for the period
def styp_refit(goal: int, model: str, allow_holdout: bool):
    """Statement-level style_resid_period vectors for the goal's chat statements, refit within (goal, regime, chat):
    on non-holdout rows when >= MIN_FIT_PERIOD (= the shared fit), else on all of the period's rows (held-out
    periods; confirm path only), else the shared regime-fallback vectors. Returns (srow -> row, R, info)."""
    import embed_models as EM
    import style_resid as SR
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow").filter(
        (pl.col("kind") == "chat") & (pl.col("goal_no") == goal))
    if not allow_holdout:
        st = st.filter(~pl.col("holdout"))
    st = st.sort("srow")
    rows = st["srow"].to_numpy()
    sfx = EM.MODELS[model]["suffix"]
    shared = np.asarray(np.load(ED / f"statements_style_resid_period32_{sfx}.npy", mmap_mode="r")[rows], np.float64)
    pos = {int(r): i for i, r in enumerate(rows)}
    fitm = ~st["holdout"].to_numpy()
    if fitm.sum() < SR.MIN_FIT_PERIOD:
        fitm = np.ones(len(rows), bool)
        level = "period refit (all rows of a held-out period)"
    else:
        level = "period refit (non-holdout rows)"
    if fitm.sum() < SR.MIN_FIT_PERIOD:
        return pos, shared, {"fit": "regime_fallback (shared)", "n": int(len(rows))}
    U = np.asarray(np.load(ED / f"statements_white32_{sfx}.npy", mmap_mode="r")[rows], np.float64)
    U /= np.maximum(np.linalg.norm(U, axis=1, keepdims=True), 1e-12)
    F = SR.style_matrix(st.select("kind", "src_row"))
    c, r2 = SR.fit_style(U, F, fitm)
    R = SR.apply_style(U, F, np.ones(len(rows), bool), c)
    sh = shared / np.maximum(np.linalg.norm(shared, axis=1, keepdims=True), 1e-12)
    cos = (R * sh).sum(1)
    return pos, R, {"fit": level, "n_fit": int(fitm.sum()), "style_r2": r2, "cos_to_shared_min": float(cos.min()),
                    "cos_to_shared_median": float(np.median(cos))}


def write_styp(base, meta, u, spec_model, pos, R):
    """Overwrite u<unit>_agent_day_styp.npy with agent-day means of the refit vectors (build.py's grouping)."""
    gdir = meta[u]["gdir"]
    ad = pl.read_parquet(base / gdir / f"u{u}_agent_day.parquet").select("agent", "pt_date")
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow").filter(
        (pl.col("kind") == "chat") & pl.col("pt_date").is_in(meta[u]["days"]))
    grp = st.group_by("agent", "pt_date").agg(pl.col("srow"))
    j = ad.with_row_index("k").join(grp, on=["agent", "pt_date"], how="left").sort("k")
    import embed_models as EM
    shared = np.load(ED / f"statements_style_resid_period32_{EM.MODELS[spec_model]['suffix']}.npy", mmap_mode="r")

    def vec(r):                       # statements outside the fitted (goal, regime, chat) group keep the shared vector
        if int(r) in pos:
            return R[pos[int(r)]]
        x = np.asarray(shared[int(r)], np.float64)
        return x / max(np.linalg.norm(x), 1e-12)
    V = np.stack([np.mean([vec(r) for r in rr], 0) for rr in j["srow"].to_list()]).astype(np.float32)
    old = np.load(base / gdir / f"u{u}_agent_day_styp.npy").astype(np.float64)
    np.save(base / gdir / f"u{u}_agent_day_styp.npy", V)
    num = (old * V).sum(1)
    den = np.linalg.norm(old, axis=1) * np.linalg.norm(V, axis=1)
    return float(np.min(num / np.maximum(den, 1e-12)))


# ------------------------------------------------------------------ one model
def explore_fields(model):
    base = DATA / "r1b" / f"{model}_none"
    Z = np.load(base / "agent_fields_explore.npz")
    meta = json.loads((base / "units.json").read_text())
    return [{int(r[0]): np.array(r[1:]) for r in Z[f"u{u}"]} for u in EXPLORE_COUNTED if meta[u]["regime"] == "III"]


def run_model(model, units, base, allow_holdout, tag, talk, rng, lab_of):
    meta = B.build_units(units, base, allow_holdout=allow_holdout, tag=f"{tag} {model}", model=model, dedupe="none",
                         talk_table="activity_bins_fixed")
    checks = {}
    for u, spec in units.items():
        if u not in meta:
            continue
        gd = base / meta[u]["gdir"]
        if talk.get(u) is not None:
            talk[u].write_parquet(gd / f"u{u}_talk_pairday.parquet", compression="zstd")
        elif (gd / f"u{u}_talk_pairday.parquet").exists():
            (gd / f"u{u}_talk_pairday.parquet").unlink()
        pos, R, info = styp_refit(meta[u]["goal_no"], model, allow_holdout)
        info["agent_day_cos_min_vs_shared"] = write_styp(base, meta, u, model, pos, R)
        checks[u] = info
    counted = [u for u in units if u in meta and len(meta[u]["days"]) >= 3]
    two = {u for u in units if u in meta and C0.room_rule(base, meta, u, lab_of)}
    E.COUNTED, E.TWO_ROOM, E.ONE_ROOM, E.EXCLUDE_B = counted, two, set(units) - two, {}
    E.STYLE = "own"
    res = {}
    for u in [x for x in units if x in meta]:
        r = E.run_unit(meta, u, lab_of, rng, base=base)
        if u in two:
            ad = pl.read_parquet(base / meta[u]["gdir"] / f"u{u}_agent_day.parquet")
            ags = np.array(sorted(int(a) for a in r["_Hs"]))
            Hs = np.array([r["_Hs"][a] for a in ags])
            fam, multi = L.fam_labels([lab_of[a] for a in ags])
            rooms = E.agent_rooms(ad, ags)
            r["c"]["y2_field_style"] = L.famroom(L.unit(Hs) @ L.unit(Hs).T, fam, rooms, len(multi), nperm=E.NP, rng=rng, jack=False)
        r["style_features_T"] = C0.style_feature_T(base, meta, u, lab_of, rng)
        # C2p-r1b: the shared style rival (period refit), same estimator as a2
        ad = pl.read_parquet(base / meta[u]["gdir"] / f"u{u}_agent_day.parquet")
        Vp = np.load(base / meta[u]["gdir"] / f"u{u}_agent_day_styp.npy").astype(np.float64)
        ags_p, Hp, _ = E.content_fields(ad, Vp)
        fam, multi = L.fam_labels([lab_of[a] for a in ags_p])
        roles = meta[u].get("roles", {})
        keep = E.role_keep(ags_p, roles) if roles else None
        r["a2p"] = L.field_test(Hp, fam, len(multi), keep_pairs=keep, nperm=E.NP_FIELD, rng=rng)
        res[u] = r
    ex = explore_fields(model)
    ho = [{int(a): np.array(v) for a, v in res[u]["_H"].items()} for u in counted if meta[u]["regime"] == "III"]
    tr = L.invariance(ex + ho, lab_of, E.BIG3, nperm=E.NP, rng=rng, A=list(range(len(ex))), B=list(range(len(ex), len(ex) + len(ho))))
    S = {}
    for name, fe, fs, us in (
            ("T_field", lambda r: r["a1"]["obs"], lambda r: r["a1"]["se_jack"], counted),
            ("T_field_style", lambda r: r["a2"]["obs"], lambda r: r["a2"]["se_jack"], counted),
            ("T_field_stylep", lambda r: r["a2p"]["obs"], lambda r: r["a2p"].get("se_jack", np.nan), counted),
            ("delta_talk", lambda r: r.get("b1", {}).get("delta", np.nan), lambda r: r.get("b1", {}).get("delta_se", np.nan), counted),
            ("delta_content", lambda r: r["b2"].get("delta", np.nan), lambda r: r["b2"].get("delta_se_jack", np.nan), counted),
            ("b_room_y3", lambda r: r["c"]["y3_comove"]["b_room"], lambda r: r["c"]["y3_comove"]["se_room"], [u for u in counted if u in two])):
        S[name] = L.dl_meta([fe(res[u]) for u in us], [fs(res[u]) for u in us]); S[name]["units"] = us
    V = C0.verdicts(res, counted, two, tr, S)
    V["C5-r1b"] = V.pop("C5")
    sp, raw = S["T_field_stylep"], S["T_field"]
    V["C2p-r1b"] = {"pass": bool((sp.get("lo", 1) <= 0 <= sp.get("hi", -1)) and sp.get("mu", 1) <= 0.25 * raw.get("mu", 0)),
                    "re_stylep": sp}
    return {"verdicts": V, "transfer": tr, "meta": S, "designation": {"counted": counted, "two_room": sorted(two)},
            "style_refit": checks, "units": {u: {k: v for k, v in r.items() if not k.startswith("_")} for u, r in res.items()}}


def combine(per):
    out = {}
    for c in ("C1", "C2", "C2p-r1b", "C3", "C4", "C5-r1b", "C6"):
        v = [per[m]["verdicts"][c]["pass"] for m in MODELS]
        out[c] = "pass" if all(v) else ("fail" if not any(v) else "model-dependent")
    o = [per[m]["verdicts"]["overall"] for m in MODELS]
    out["overall"] = "CONFIRMED" if all(x == "CONFIRMED" for x in o) else (
        "REFUTED" if all(x == "REFUTED" for x in o) else "INCONCLUSIVE")
    out["overall_per_model"] = dict(zip(MODELS, o))
    return out


def run(units, root, allow_holdout, tag):
    t0 = time.time()
    rng = np.random.default_rng(20261006)
    lab_of, _ = E.roster()
    talk, tinfo = {}, {}
    for u, spec in units.items():
        days = B.unit_days(spec, allow_holdout=allow_holdout)
        st = pl.read_parquet(ED / "statements.parquet", columns=["kind", "agent", "pt_date", "room"]).filter(
            (pl.col("kind") == "chat") & pl.col("pt_date").is_in(days))
        ar = st.group_by("agent", "pt_date").agg(pl.col("room").mode().first())
        agent_room = {(int(a), d): int(r) for a, d, r in ar.iter_rows() if r is not None}
        talk[u], tinfo[u] = talk_pairdays_trim(days, agent_room, seed=20261006 + sum(map(ord, u)))
    per = {m: run_model(m, units, root / m, allow_holdout, tag, talk, rng, lab_of) for m in MODELS}
    out = {"tag": tag, "card_prediction_hash": C0.card_hash(), "predictions": PREDICTIONS, "reasons": REASONS,
           "verdicts": combine(per), "talk_trim": tinfo, "per_model": per,
           "run_at": dt.datetime.now(dt.timezone.utc).isoformat(), "seconds": round(time.time() - t0, 1)}
    (root / f"confirm_r1b_{tag}.json").write_text(json.dumps(E.clean(out), indent=1))
    print(json.dumps(E.clean({"verdicts": out["verdicts"],
                              "per_model": {m: per[m]["verdicts"] for m in MODELS},
                              "style_refit": {m: per[m]["style_refit"] for m in MODELS},
                              "talk_trim_share": {u: round(sum(v["kept"] for v in tinfo[u].values()) /
                                                           max(sum(v["minutes"] for v in tinfo[u].values()), 1), 3)
                                                  for u in tinfo}}), indent=1))
    return out


def main():
    if "--dry-run" in sys.argv:
        print("DRY RUN on non-holdout stand-ins:", list(DRYRUN_UNITS))
        ledger_status(strict=False)
        run(DRYRUN_UNITS, DATA / "confirm_r1b_dryrun", allow_holdout=False, tag="dryrun")
        return
    if not ("--confirm" in sys.argv and "--i-understand-this-uses-the-locked-holdout" in sys.argv):
        sys.exit("Refusing to run: this script reads the LOCKED HOLDOUT. Pass --dry-run to test on non-holdout stand-ins, or "
                 "--confirm --i-understand-this-uses-the-locked-holdout (only after sign-off).")
    must = [Path(__file__).resolve(), HERE / "CONFIRM_R1B.md", HERE.parent / "README.md", HERE / "confirm.py",
            HERE / "explore.py", HERE / "h13lib.py", HERE.parent / "scheme/build.py", ROOT / "infra/shared/nulls.py",
            ROOT / "infra/shared/style_resid.py"]
    if not committed_clean(must):
        sys.exit("refusing: commit confirm_r1b.py, CONFIRM_R1B.md, the card and the code it imports first")
    if not ledger_status(strict=True):
        sys.exit("refusing: holdout_ledger.check() reports a same-family prior run on a target; Vivian decides")
    run(HOLDOUT_UNITS, DATA / "confirm_r1b", allow_holdout=True, tag="holdout")


if __name__ == "__main__":
    main()
