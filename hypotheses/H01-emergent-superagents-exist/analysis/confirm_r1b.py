"""H01 CONFIRMATORY test of D3.2 (coupling) on the LOCKED HOLDOUT -- ROUND-1B RE-FREEZE of `confirm_d32.py`.
Written 2026-10-04 after round 1b, before any holdout outcome was computed. NOT RUN. `confirm_d32.py` is left
byte-for-byte unchanged; this script supersedes it only if Vivian adopts it (see CONFIRM_R1B.md).

!!! Running with --confirm consumes the holdout for H01. It refuses unless BOTH flags are given:
!!!     --confirm --i-understand-this-uses-the-locked-holdout
!!! --dry-run runs every code path on NON-holdout stand-in windows and asserts that no holdout day is touched.

Design: identical to confirm_d32.py (A NE12 placebo, B #voted-out via daily co-location, C NE15 split DiD, D pooled
TWFE, E transfer to #45-#47), with every input switched to the round-1b instruments (scheme/build_r1b.py):
  * statement vectors from the shared DQ5 embeddings in TWO models (bge_small, gte_modernbert), each whitened with the
    round-1b per-regime basis and k = 40 ruler fitted on non-holdout statements (r1b/<tag>/basis_<R>.npz);
  * restatements removed (chat rows carrying the model's own DQ5 self-repeat flag; `statement_flags`);
  * a style-residualized variant per model (DQ5 `statements_style_resid_period32`; held-out periods fall back to the
    regime fit, by the shared builder's rule) -- descriptive only;
  * goal fields from the shared goal table (fixes the #38 room swap; held-out rows only under --confirm);
  * pair-day exposure from the DQ1 context ledger (messages of j that entered one of i's calls), not `exposure`.
  activity_bins, the DQ8 trim, the work ledger, failures and nudge targets are not inputs of this design.
Instruments: bge_restate (primary), gte_restate (co-primary), bge_restate_style, gte_restate_style (descriptive).

Holdout reuse (hypotheses/holdout.md policy; infra/shared/holdout_ledger.py check() is called before any confirm
computation): H05 ran on NE12 / #32 and #34 days 03-05..03-13 (talk and activity, not content); H02 (#45) and H04
(#45-#50, NE21+NE23) ran activity-timing and Curie-Weiss-family statistics. This re-freeze drops P9 (the content
mean-field betaJ0/n, Curie-Weiss family) from the transfer test, which removes the only same-family collision; the
remaining statistics are content-modality and need disclosure in both cards and LOG.md.

Usage:
  uv run python hypotheses/H01-emergent-superagents-exist/analysis/confirm_r1b.py --dry-run
  ... --confirm --i-understand-this-uses-the-locked-holdout        # CONSUMES THE HOLDOUT; needs sign-off
Writes data/processed/H01-emergent-superagents-exist/confirm_r1b[_dryrun]/ (per-instrument window tables + results).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
DRY = "--dry-run" in sys.argv
CONFIRM = "--confirm" in sys.argv and "--i-understand-this-uses-the-locked-holdout" in sys.argv
if not (DRY or CONFIRM):
    sys.exit("Refusing to run: pass --dry-run (non-holdout stand-ins) or "
             "--confirm --i-understand-this-uses-the-locked-holdout (consumes the H01 holdout; needs sign-off).")
if DRY and CONFIRM:
    sys.exit("Pass either --dry-run or --confirm, not both.")
sys.argv = [sys.argv[0]]  # keep explore's CLI parser at its defaults

from h01common import OUT, ROOT, SEED, SH, assign, guard_holdout, holdout_days, unit, unit_of, whiten_apply  # noqa: E402
from h01data import Scheme  # noqa: E402
from h01lib import fe_slope, pair_table, partition_test, random_effects, rarefied_counts, rarefied_vectors, rotate_agents  # noqa: E402
import build  # noqa: E402
import build_r1b  # noqa: E402
import explore  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ODIR = OUT / ("confirm_r1b_dryrun" if DRY else "confirm_r1b")
R1B = OUT / "r1b"
EMB = SH / "embeddings"
N_PERM = 500

# instrument -> (model, dedupe flag column, style?, r1b basis folder, role)
INSTRUMENTS = {
    "bge_restate": ("bge_small", "self_repeat", False, "bge_restate", "primary"),
    "gte_restate": ("gte_modernbert", "self_repeat_gte", False, "gte_restate", "co-primary"),
    "bge_restate_style": ("bge_small", "self_repeat", True, "bge_restate_style", "descriptive"),
    "gte_restate_style": ("gte_modernbert", "self_repeat_gte", True, "gte_restate_style", "descriptive"),
}
PRIMARY = ("bge_restate", "gte_restate")

# ============================================================================ pre-registered predictions (re-frozen)
# Original ids kept where the prediction is unchanged; "-r1b" marks a prediction changed because round 1b changed
# the exploratory result it rested on. Nothing here was tuned on held-out data (none has been read).
PREDICTIONS = {
    "C1-r1b_ne15_cut_did": "NE15 cut arm vs stay pairs: DiD of the rarefied residual cosine < 0, pair-clustered 95% CI excluding 0 "
                           "AND assignment-permutation one-sided p < 0.05, in BOTH bge_restate and gte_restate. "
                           "Reason: round 1b showed single-model significance is instrument-dependent (P6, P7).",
    "C1s-r1b_style": "Descriptive expectation: the style-residualized DiD is smaller in magnitude than the whitened DiD in both "
                     "models (round 1b: the #40 merge DiD fell from +0.17/+0.10 to +0.06/+0.01 after style removal). Not in the verdict.",
    "C2_stay_hold": "Descriptive (unchanged): stay-pair change post - pre.",
    "C3-r1b_twfe": "Pooled TWFE over 02-09..03-20: beta(co-location) > 0 with pair-clustered z > 1.96 in BOTH bge_restate and "
                   "gte_restate. Reason: as C1-r1b.",
    "C4_ne12_placebo": "Unchanged: no pair separated across 02-25 (asserted); all-pair mean residual cosine does not drop at 02-25 "
                       "(day-block bootstrap 95% CI of post - pre includes 0 or lies above it), in both primary instruments.",
    "C5_toward_field_only": "Unchanged: the cut arm's residual cosine moves toward the rotation-null level after the split "
                            "(bge_restate; gte_restate reported).",
    "C6-r1b_transfer": "Held-out two-room days #45-#47: P1 rule (>= 60% of days dH < 0 AND median dH <= -0.1 nats) reported per model "
                       "(round 1b: gte meets it, bge 0.002 short); P6 RE exposure slope on LEDGER exposure > 0 in both models "
                       "(direction only). P9 (content mean-field betaJ0/n) is DROPPED: H26 showed drives alone reproduce the "
                       "round-1 value, so it cannot test coupling, and it is the Curie-Weiss-family statistic that collides with "
                       "H02's and H04's executed runs on #45-#47.",
    "overall-r1b": "D3.2 (coupling) confirmed if C1-r1b and C3-r1b pass and C4 holds (all in both primary instruments). "
                   "Refuted if, in both primary instruments, C1 and C3 have the wrong sign or both CIs contain 0 with |effect| < 0.05. "
                   "'model-dependent' if the two primary instruments disagree on C1 or C3. Otherwise inconclusive. "
                   "Power is low: ~40 cut pairs and 5 post days.",
}

if CONFIRM:
    W = {"A_pre": ("2026-02-16", "2026-02-24"), "A_post": ("2026-02-25", "2026-03-04"),
         "C_pre": ("2026-03-02", "2026-03-13"), "C_post": ("2026-03-16", "2026-03-20"),
         "D_all": ("2026-02-09", "2026-03-20"), "E_all": ("2026-06-01", "2026-06-19")}
    BASIS = {"D_all": "II", "E_all": "III"}
    EXTRA_SPLITS = {32: ["2026-02-25"]}
    GPT5_LIKE = []
else:  # stand-ins as in confirm_d32.py: placebo #41 -> #42; split 05-11 (#40 merged -> #41 split); TWFE #39-#42
    W = {"A_pre": ("2026-05-11", "2026-05-15"), "A_post": ("2026-05-18", "2026-05-22"),
         "C_pre": ("2026-05-04", "2026-05-08"), "C_post": ("2026-05-11", "2026-05-15"),
         "D_all": ("2026-04-27", "2026-05-22"), "E_all": ("2026-05-11", "2026-05-22")}
    BASIS = {"D_all": "III", "E_all": "III"}
    EXTRA_SPLITS = {}
    GPT5_LIKE = [10]

LEDGER_TARGETS = ["NE12", "G32", "G34", "NE30", "G45", "G46", "G47", "NE21+NE23"]


def pred_hash():
    return hashlib.sha256(json.dumps(PREDICTIONS, sort_keys=True).encode()).hexdigest()[:16]


def cal_days(lo, hi):
    cal = pl.read_parquet(SH / "calendar.parquet")
    return sorted(cal.filter((pl.col("pt_date") >= lo) & (pl.col("pt_date") <= hi) & (pl.col("goal_no") > 0))["pt_date"].to_list())


def ledger_checks():
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import holdout_ledger as HL
    out = {}
    for t in LEDGER_TARGETS:
        c = HL.check("H01", t, "message content", ["content_alignment"])
        out[t] = {"allowed": c["allowed"], "needs_disclosure": c["needs_disclosure"],
                  "prior_runs": sorted({u["hypothesis"] for u in c["prior_runs"]}),
                  "prior_runs_same_family": sorted({u["hypothesis"] for u in c["prior_runs_same_family"]}),
                  "competing_planned": sorted({u["hypothesis"] for u in c["competing_planned"]})}
    return out


# ============================================================================ window tables (round-1b instruments)
def shared_goal_rows(goal_nos, regime, model):
    """Shared goal table -> H01 goals.parquet layout for the window's goal periods; gid = shared gid."""
    sg = pl.read_parquet(EMB / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    G = np.load(EMB / build_r1b.GOALVEC[model]).astype(np.float32)
    rows = []
    for r in sg.iter_rows(named=True):
        kind = {"goal": "goal", "kickoff_room": "kickoff", "agent_goal": "agent_goal"}.get(r["kind"])
        if kind is None or int(r["goal_no"]) not in goal_nos or (r["holdout"] and not CONFIRM):
            continue
        rows.append({"goal_no": int(r["goal_no"]), "kind": kind,
                     "room": int(r["room"]) if (kind == "kickoff" and r["room"] is not None) else -1,
                     "agent": int(r["agent"]) if (kind == "agent_goal" and r["agent"] is not None) else -1,
                     "valid_from": r["valid_from"], "valid_to": r["valid_to"], "n_chunks": int(r["n_chunks"] or 0),
                     "n_chars": int(r["n_chars"] or 0), "regime": regime, "gid": int(r["gid"])})
    return pl.DataFrame(rows, infer_schema_length=None), G


_CACHE = {}


def base_statements(key, days):
    if key in _CACHE:
        return _CACHE[key]
    if DRY:
        guard_holdout(days)
        assert not (set(days) & holdout_days()), "dry run touched a holdout day"
    st = build.load_statements(days, allow_holdout=CONFIRM)
    if DRY:
        guard_holdout(sorted(st["pt_date"].unique().to_list()))
    st = st.with_columns(pl.struct("goal_no", "pt_date").map_elements(
        lambda s: (f"{s['goal_no']}{'ab'[int(s['pt_date'] >= EXTRA_SPLITS[s['goal_no']][0])]}" if s["goal_no"] in EXTRA_SPLITS
                   else unit_of(s["goal_no"], s["pt_date"])), return_dtype=pl.Utf8).alias("unit"),
        pl.lit(BASIS[key]).alias("regime"))
    srow = build_r1b.shared_rows(st)
    rm = build.room_membership(st, days)
    pe = build_r1b.ledger_exposure(days)          # corrected visibility (DQ1 context ledger)
    if DRY:
        guard_holdout(sorted(pe["pt_date"].unique().to_list()))
    _CACHE[key] = (st, srow, rm, pe)
    return _CACHE[key]


def build_window(key, days, inst):
    model, flagcol, style, btag, _role = INSTRUMENTS[inst]
    st, srow, rm, pe = base_statements(key, days)
    out = ODIR / inst / key
    out.mkdir(parents=True, exist_ok=True)
    bz = np.load(R1B / btag / f"basis_{BASIS[key]}.npz")
    b = {k: bz[k] for k in bz.files}
    if style:
        Zs = np.load(EMB / f"statements_style_resid_period32_{build_r1b.SUFFIX[model]}.npy", mmap_mode="r")
        o = np.argsort(srow)
        tmp = np.asarray(Zs[srow[o]], dtype=np.float32)
        Z = np.empty_like(tmp); Z[o] = tmp
        Z[~np.isfinite(Z).all(1)] = 0.0
        dstore = 32
    else:
        Z = whiten_apply(build_r1b.raw_embeddings(st, model), b, 64)
        dstore = 64
    lab = assign(unit(Z[:, :32]).astype(np.float32), b["centroids_k40_d32"])
    fl = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", flagcol])
    assert (fl["srow"].to_numpy() == np.arange(fl.height)).all()
    keep = ~(fl[flagcol].to_numpy()[srow].astype(bool) & (st["kind"].to_numpy() == 0))
    st2 = st.filter(pl.Series(keep)); Z2 = Z[keep]; lab2 = lab[keep]
    st2.write_parquet(out / "statements.parquet")
    np.save(out / "vectors_w64.npy", Z2[:, :dstore].astype(np.float16))
    pl.DataFrame({"k20": lab2, "k40": lab2, "k80": lab2, "k40_d16": lab2, "k40_d64": lab2}).write_parquet(out / "clusters.parquet")
    for R in ("I", "II", "III"):
        np.savez(out / f"basis_{R}.npz", **b)
    cnt = st2.group_by("agent", "pt_date").agg(pl.len().alias("n_stmt"), pl.col("unit").first(), pl.col("goal_no").first(),
                                               pl.col("regime").first())
    cnt.join(rm, on=["agent", "pt_date"], how="left").write_parquet(out / "agent_day.parquet")
    pe.write_parquet(out / "pair_day_exposure.parquet")
    gt, G = shared_goal_rows(set(st2["goal_no"].unique().to_list()), BASIS[key], model)
    gt.write_parquet(out / "goals.parquet")
    np.save(out / "goals_raw.npy", G)
    units = (st2.group_by("unit").agg(pl.col("goal_no").first(), pl.col("pt_date").unique().sort().alias("days"),
                                      pl.col("agent").n_unique().alias("n_agents")).sort(pl.col("days").list.first()))
    (out / "units.json").write_text(json.dumps([{"unit": u, "goal_no": int(g), "regimes": [BASIS[key]], "days": list(d), "n_agents": int(n)}
                                                for u, g, d, n in units.iter_rows()], indent=1))
    return Scheme(d=32, allow_holdout=CONFIRM, base=out), int((~keep).sum())


def panel(S: Scheme, days, rng):
    """Pair-day panel over `days` (as confirm_d32.py): rarefied residual cosine, one h per agent (its first window day)."""
    ad = S.ad.filter(pl.col("pt_date").is_in(days)).sort("pt_date")
    first, ndays = {}, {}
    for a, d in ad.select("agent", "pt_date").iter_rows():
        first.setdefault(a, d); ndays[a] = ndays.get(a, 0) + 1
    parts = []
    for name, ui in S.units.items():
        ud = [d for d in ui["days"] if d in days]
        if not ud:
            continue
        u = S.unit(name, days=ud)
        u.h = {a: S.adV[(a, first[a])] for a in np.unique(u.agents) if ndays.get(a, 0) >= 2}
        u.h_firstday = {a for a in u.h if first[a] in ud}
        Vr = rarefied_vectors(u, 8, 10, rng)
        pt = pair_table(u, n_min=8, Vover=Vr)
        if pt is None:
            continue
        pt["pt_date"] = np.array([ud[t] for t in pt["day"]]); pt["unit"] = np.array([name] * len(pt["r"]))
        _Vrot, hrot, Vrr = rotate_agents(u, rng, extra=Vr)
        p0 = pair_table(u, n_min=8, Vover=Vrr, hover=hrot)
        pt["r_rot"] = p0["r"] if p0 is not None and len(p0["r"]) == len(pt["r"]) else np.full(len(pt["r"]), np.nan)
        parts.append(pt)
    P = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    dmap = {d: i for i, d in enumerate(sorted(set(P["pt_date"])))}
    P["day"] = np.array([dmap[d] for d in P["pt_date"]])
    return P


def room_by_period(S: Scheme, days):
    ad = S.ad.filter(pl.col("pt_date").is_in(days) & pl.col("room_mode").is_not_null())
    return {int(a[0]): int(g["room_mode"].mode().sort()[0]) for a, g in ad.group_by("agent")}


def run_instrument(inst, rng):
    res = {"instrument": inst, "role": INSTRUMENTS[inst][4]}
    days_D = cal_days(*W["D_all"])
    S, ndrop = build_window("D_all", days_D, inst)
    res["n_chat_dropped_restate"] = ndrop
    P = panel(S, days_D, rng)
    # ---------------- A placebo
    dA0, dA1 = cal_days(*W["A_pre"]), cal_days(*W["A_post"])
    rA = room_by_period(S, dA0); rA1 = room_by_period(S, dA1)
    both = sorted(set(rA) & set(rA1))
    separated = [(int(a), int(b)) for i, a in enumerate(both) for b in both[i + 1:] if rA[a] == rA[b] and rA1[a] != rA1[b]]
    daymean = {d: float(P["r"][P["pt_date"] == d].mean()) for d in dA0 + dA1 if (P["pt_date"] == d).any()}
    pre = np.array([daymean[d] for d in dA0 if d in daymean]); post = np.array([daymean[d] for d in dA1 if d in daymean])
    boots = [rng.choice(post, len(post)).mean() - rng.choice(pre, len(pre)).mean() for _ in range(2000)]
    res["A_placebo"] = {"n_pairs_separated": len(separated), "post_minus_pre": float(post.mean() - pre.mean()),
                        "ci95": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]}
    res["C4_pass"] = bool(len(separated) == 0 and res["A_placebo"]["ci95"][1] >= 0)
    if CONFIRM:
        assert len(separated) == 0, "NE12 premise violated: a pair was separated across 02-25"
    # ---------------- D pooled TWFE
    P["coloc"] = P["same"].astype(float)
    f = fe_slope(P, ["coloc"])
    res["D_twfe"] = None if f is None else {"beta": float(f["b"][0]), "se": float(f["se"][0]), "z": float(f["b"][0] / f["se"][0]),
                                             "n": f["n"], "n_pairs": f["n_pairs"]}
    res["C3_pass"] = bool(f is not None and f["b"][0] / f["se"][0] > 1.96)
    # ---------------- C split DiD
    dC0, dC1 = cal_days(*W["C_pre"]), cal_days(*W["C_post"])
    r0 = room_by_period(S, dC0); r1 = room_by_period(S, dC1)
    mC = np.isin(P["pt_date"], dC0 + dC1)
    post_ind = np.isin(P["pt_date"], dC1).astype(float)

    def arms(rpost):
        g = []
        for i, j in zip(P["i"], P["j"]):
            if i in GPT5_LIKE or j in GPT5_LIKE or i not in r0 or j not in r0 or i not in rpost or j not in rpost:
                g.append("na"); continue
            s0 = r0[i] == r0[j]; s1 = rpost[i] == rpost[j]
            g.append("stay" if s0 and s1 else ("cut" if s0 and not s1 else "other"))
        return np.array(g)
    G = arms(r1)
    m = mC & np.isin(G, ["stay", "cut"])
    P["treat"] = ((G == "cut") & (post_ind == 1)).astype(float)
    fC = fe_slope(P, ["treat"], mask=m)
    C = {"n_cut_pairs": int(len(np.unique((P["i"] * 1000 + P["j"])[m & (G == "cut")]))),
         "n_stay_pairs": int(len(np.unique((P["i"] * 1000 + P["j"])[m & (G == "stay")])))}
    if fC is not None:
        C.update({"did": float(fC["b"][0]), "se": float(fC["se"][0]),
                  "ci95": [float(fC["b"][0] - 1.96 * fC["se"][0]), float(fC["b"][0] + 1.96 * fC["se"][0])]})
        ags = [a for a in r1 if a not in GPT5_LIKE]; labs = [r1[a] for a in ags]
        nulls = []
        for _ in range(N_PERM):
            rp = dict(r1); rp.update(dict(zip(ags, rng.permutation(labs))))
            Gp = arms(rp); mp = mC & np.isin(Gp, ["stay", "cut"])
            if (Gp[mp] == "cut").sum() == 0 or (Gp[mp] == "stay").sum() == 0:
                continue
            P["treat"] = ((Gp == "cut") & (post_ind == 1)).astype(float)
            fp = fe_slope(P, ["treat"], mask=mp)
            if fp is not None:
                nulls.append(float(fp["b"][0]))
        C["p_perm_one_sided"] = float((1 + np.sum(np.array(nulls) <= C["did"])) / (1 + len(nulls)))
        for g_ in ("cut", "stay"):
            for k, dd in (("pre", dC0), ("post", dC1)):
                mm = (G == g_) & np.isin(P["pt_date"], dd)
                C[f"{g_}_{k}_mean"] = float(P["r"][mm].mean()) if mm.any() else None
                C[f"{g_}_{k}_rot_mean"] = float(np.nanmean(P["r_rot"][mm])) if mm.any() else None
    res["C_split"] = C
    res["C1_pass"] = bool("did" in C and C["did"] < 0 and C["ci95"][1] < 0 and C["p_perm_one_sided"] < 0.05)
    if C.get("cut_pre_mean") is not None and C.get("cut_post_mean") is not None:
        null = np.nanmean([C["cut_pre_rot_mean"], C["cut_post_rot_mean"]])
        res["C5_pass"] = bool(abs(C["cut_post_mean"] - null) < abs(C["cut_pre_mean"] - null))
    # ---------------- E transfer (P1, P6 on ledger exposure; P9 dropped)
    if INSTRUMENTS[inst][4] != "descriptive":
        days_E = cal_days(*W["E_all"])
        SE, _ = build_window("E_all", days_E, inst)
        E = {"P1_days": [], "P6": {}}
        for name in SE.units:
            u = SE.unit(name)
            for t in range(int(u.day.max()) + 1):
                idx = np.where((u.day == t) & (u.nstmt >= 8) & (u.room >= 0))[0]
                labs_ = u.room[idx]
                if len(idx) < 4 or (np.bincount(np.unique(labs_, return_inverse=True)[1]) >= 2).sum() < 2:
                    continue
                E["P1_days"].append({"unit": name, "day": u.day_names[t],
                                     **partition_test(rarefied_counts(u, idx, 40, 8, 20, rng), labs_, 1000, rng)})
            two = len([r for r in np.unique(u.room) if r >= 0 and (u.room == r).sum() >= 2]) >= 2
            r6 = explore.unit_p56(u, rng, two)
            E["P6"][name] = {k: v for k, v in r6.items() if not isinstance(v, list)}
        dH = np.array([d["dH"] for d in E["P1_days"]])
        E["P1"] = {"n_days": int(len(dH)), "frac_dH_neg": float((dH < 0).mean()) if len(dH) else None,
                   "median_dH": float(np.median(dH)) if len(dH) else None,
                   "pass": bool(len(dH) and (dH < 0).mean() >= 0.6 and np.median(dH) <= -0.1)}
        s6 = [(v["slope"], v["slope_se"]) for v in E["P6"].values() if "slope" in v]
        E["P6_re"] = random_effects([a for a, _ in s6], [b for _, b in s6]) if len(s6) >= 2 else None
        E["P6_pass"] = bool(E["P6_re"] is not None and E["P6_re"].get("mu", E["P6_re"].get("b", -1)) > 0)
        res["E_transfer"] = E
    return res


def overall(R):
    a, b = (R[i] for i in PRIMARY)
    ok = [x["C1_pass"] and x["C3_pass"] and x["C4_pass"] for x in (a, b)]
    wrong = [("did" in x["C_split"] and x["D_twfe"] and x["C_split"]["did"] >= 0 and x["D_twfe"]["beta"] <= 0) for x in (a, b)]
    small = [("did" in x["C_split"] and x["D_twfe"] and x["C_split"]["ci95"][0] <= 0 <= x["C_split"]["ci95"][1]
              and abs(x["C_split"]["did"]) < 0.05 and x["D_twfe"]["z"] < 1.96 and abs(x["D_twfe"]["beta"]) < 0.05) for x in (a, b)]
    if all(ok):
        return "confirmed"
    if all(w or s for w, s in zip(wrong, small)):
        return "refuted"
    if ok[0] != ok[1] or a["C1_pass"] != b["C1_pass"] or a["C3_pass"] != b["C3_pass"]:
        return "model-dependent"
    return "inconclusive"


def main():
    rng = np.random.default_rng(SEED)
    res = {"mode": "dry_run" if DRY else "CONFIRM", "run_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "script": "confirm_r1b.py (re-freeze of confirm_d32.py)", "predictions_hash": pred_hash(),
           "predictions": PREDICTIONS, "windows": W, "basis": BASIS, "ledger": ledger_checks()}
    if CONFIRM:
        blocked = [t for t, c in res["ledger"].items() if not c["allowed"]]
        if blocked:
            sys.exit(f"holdout_ledger.check refuses targets {blocked} (same-family prior run); resolve before running.")
        print("!!! CONFIRMATORY RUN: consuming the H01 holdout (round-1b re-freeze).", flush=True)
    ODIR.mkdir(parents=True, exist_ok=True)
    R = {}
    for inst in INSTRUMENTS:
        R[inst] = run_instrument(inst, np.random.default_rng([SEED, list(INSTRUMENTS).index(inst)]))
        x = R[inst]
        print(inst, {"C1": x["C1_pass"], "C3": x["C3_pass"], "C4": x["C4_pass"], "C5": x.get("C5_pass"),
                     "did": x["C_split"].get("did"), "twfe_z": (x["D_twfe"] or {}).get("z")}, flush=True)
    res["instruments"] = R
    res["C1s_style_smaller"] = {m: (abs(R[f"{m}_restate_style"]["C_split"].get("did", np.nan))
                                    < abs(R[f"{m}_restate"]["C_split"].get("did", np.nan))) for m in ("bge", "gte")}
    res["C6"] = {i: {"P1": R[i]["E_transfer"]["P1"], "P6_re": R[i]["E_transfer"]["P6_re"], "P6_pass": R[i]["E_transfer"]["P6_pass"]}
                 for i in PRIMARY}
    res["overall"] = overall(R)
    (ODIR / "confirm_r1b.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print("overall:", res["overall"], "| C1s style smaller:", res["C1s_style_smaller"])
    print("C6:", json.dumps(res["C6"], default=str))
    print("ledger:", json.dumps(res["ledger"]))


if __name__ == "__main__":
    main()
