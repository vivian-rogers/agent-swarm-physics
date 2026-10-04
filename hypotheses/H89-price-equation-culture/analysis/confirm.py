"""H89 confirmatory test on the locked holdout. WRITTEN 2026-10-04, FROZEN, NOT RUN on the holdout.

  uv run python hypotheses/H89-price-equation-culture/analysis/confirm.py --dry-run
      runs the frozen pipeline on non-holdout stand-ins (safe; exploration data only)
  uv run python hypotheses/H89-price-equation-culture/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      builds held-out traits and in-cone adoptions in memory (markers extracted from held-out text in memory; no text
      written), scores the frozen predictions. Refuses without BOTH flags. Calls holdout_ledger.check() first and
      writes confirm/confirm_sealed.json (SHA-256 of this docstring) BEFORE touching held-out data.

Targets (locked holdout; reuse policy in hypotheses/holdout.md):
  T1 #15 (regime I; Claude Sonnet 4.5 joins 2025-09-30 inside the period)
  T2 #22 (regime I; GPT-5.2 joins 2025-12-12)
  T3 #29 (regime I; Claude Opus 4.6 joins 2026-02-06)
  T4 #34 = NE30 (regime II; Gemini 3 Pro leaves and Gemini 3.1 Pro joins 2026-03-09: same-family succession)
  T5 #51 tail (2026-09-07 -> 09-21, regime III; the tail alone, novelty relative to all earlier chat)
Stand-ins for --dry-run: #18, #20, #19, #31 (NE29), #51 days 08-24 -> 09-04.
Reuse disclosure: #15, #22, #29, #34 and the #51 tail are targets of other unrun confirm scripts (H34, H61, H62,
H73 and others in the holdout ledger) using chat content; this statistic (a Price partition of agent-day trait
change) is new. If run, disclose in both cards and LOG.md.

Frozen predictions (from round 1, frozen 2026-10-04 before any holdout use; energy shares, cross-fitted, A1 rule
rho >= 0.3 for a trait to count):
  C1 content moves by transmission: s_Trans(content) >= 0.5 and the largest term in >= 4/5 eligible targets, bge and
     gte separately. (Round 1: 33/33, median 0.98.)
  C2 selection is not a material share: |s_Sel| <= 0.2 for content (bge), style and conventions in every eligible
     target. (Round 1: 33/33 each; median |s_Sel| 0.01-0.03.)
  C3 style moves by migration more than content does: s_Mig(style) > s_Mig(content, bge) in >= 3/4 of eligible targets
     with at least one entry or exit. (Round 1, ties at zero turnover excluded: 21/26; pre-registered all-period form
     21/33 failed.)
  C4 no village attractor, partial persistence: persistence C(content, bge) < 0 in every eligible target with >= 4
     transitions, and its median > -0.5 (the iid-topic value). (Round 1: C > 0 in 0/29; median -0.28.)
  C5 not killed: residual R(content, bge) >= 0.1 with jackknife CI > 0 in >= 4/5 eligible targets. (Round 1: 33/33.)
  C6 NE30 (T4): at the succession transition the roster-migration share of style exceeds that of content (bge).
     (Round 1 analogue NE29: 0.164 vs 0.051 at the entry, 0.033 vs -0.002 at the exit.)
  Overall: CONFIRMED if C1, C2 and C3 pass; the egregore reading stays rejected if C4 passes.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h89lib as L  # noqa: E402
import idea_ledger as IL  # noqa: E402
import build as BLD  # noqa: E402
import replication as REP  # noqa: E402

OUT = L.DATA / "confirm"
FIRST_SEEN = ROOT / "data/processed/H34-idea-cascades/markers/first_seen.parquet"
TARGETS = {"T1": dict(goal=15), "T2": dict(goal=22), "T3": dict(goal=29), "T4": dict(goal=34, succession="2026-03-09"),
           "T5": dict(goal=51, tail=("2026-09-07", "2026-09-22"))}
STANDINS = {"T1": dict(goal=18), "T2": dict(goal=20), "T3": dict(goal=19), "T4": dict(goal=31, succession="2026-02-18"),
            "T5": dict(goal=51, window=("2026-08-24", "2026-09-05"))}
LEDGER_TARGETS = {"T1": "G15", "T2": "G22", "T3": "G29", "T4": "NE30", "T5": "#51-tail"}


def heldout_period(base: IL.Base, g: int, days: list[str]) -> dict:
    """idea_ledger period on held-out days, with novel-idea uses extracted in memory (H61's rule: novel = first seen
    in the corpus at or after the target's first message)."""
    import idea_markers as M
    P = IL.load_period(base, g, days=days, allow_holdout=True, with_markers=False)
    uses = M.uses_for_rows(P["rows"], allow_holdout=True)
    t_start = int(P["t"].min())
    fs = pl.read_parquet(FIRST_SEEN).select("marker", "first_t")
    old = fs.filter(pl.col("first_t").dt.epoch("us") < t_start)["marker"]
    uses = uses.filter(~pl.col("marker").is_in(old.implode()))
    pos_of = {int(r): i for i, r in enumerate(P["rows"])}
    P["use_pos"] = np.array([pos_of[int(m)] for m in uses["msg"].to_numpy()], dtype=np.int64)
    P["use_marker"] = uses["marker"].to_numpy().astype(np.int64)
    P["use_cls"] = uses["cls"].to_numpy().astype(np.int8)
    return P


def standin_period(base: IL.Base, g: int, window=None) -> dict:
    days = base.period_days(g)
    if window:
        days = [d for d in days if window[0] <= d < window[1]]
    return IL.load_period(base, g, days=days)


def period_from_build(g: int, ad: pl.DataFrame, adop: pl.DataFrame, npz: dict) -> L.Period:
    days = [str(x) for x in npz["days"]]
    keys = {(int(a), int(d)): k for k, (a, d) in enumerate(zip(npz["agent"], npz["day"]))}
    traits = {t: np.asarray(npz[t], dtype=np.float64) for t in L.TRAITS}
    active, F = {}, {}
    for r in ad.iter_rows(named=True):
        F[(r["agent"], r["day"])] = (r["F_all"], r["F_notrait"])
        if r["active"]:
            active.setdefault(r["day"], []).append(r["agent"])
    active = {d: sorted(v) for d, v in active.items()}
    A = {"read": [], "plc": []}
    for r in adop.iter_rows(named=True):
        A[r["kind"]].append((r["day"], r["adopter"], tuple(r["sources"]), tuple(r["named_sources"] or []), r["in_trait"]))
    kick = np.load(L.DATA / "kickoff.npz") if g in [int(k[1:3]) for k in np.load(L.DATA / "kickoff.npz").files] else None
    kk = {}
    if kick is not None:
        for tag, model in L.CONTENT.items():
            if f"G{g:02d}_{model}" in kick.files:
                kk[tag] = kick[f"G{g:02d}_{model}"].astype(np.float64)
    else:
        kd = BLD.kickoff_dirs([g])
        for tag, model in L.CONTENT.items():
            if f"G{g:02d}_{model}" in kd:
                kk[tag] = kd[f"G{g:02d}_{model}"].astype(np.float64)
    return L.Period(g, days, keys, traits, active, F, A, kk)


def score_target(Pb: L.Period, spec: dict) -> dict:
    res, dg = L.run_period(Pb)
    r = dict(goal=Pb.goal, n_trans=len(res), n_in=sum(d["n_in"] for d in dg),
             n_events=sum(d["nE"] + d["nI"] for d in dg), eligible=len(res) >= 2 and sum(d["n_in"] for d in dg) >= 20)
    if not r["eligible"]:
        return r
    full = REP.stats_all(Pb)
    se, _ = REP.jk(Pb, full)
    r.update(full)
    r.update({f"{k}.se": v for k, v in se.items()})
    r["reliable"] = {t: REP.ok(r, t) for t in L.TRAITS}
    if spec.get("succession"):
        d_of = {d: i for i, d in enumerate(Pb.days)}
        d1 = d_of.get(spec["succession"])
        if d1 is not None and d1 in Pb.active:
            d0 = max(d for d in Pb.active if d < d1)
            tr, _ = L.price_transition(Pb, d0, d1)
            for tag in ("style", "content_bge"):
                dz = tr[tag]["dz"]
                den = L.xf(dz, dz)
                r[f"succ.{tag}"] = L.xf(L.group_vec(tr[tag]["terms"], "mig_roster"), dz) / den if den > 0 else np.nan
    return r


def verdicts(rs: dict) -> dict:
    E = [r for r in rs.values() if r.get("eligible")]
    out = {}
    for tag in ("content_bge", "content_gte"):
        s = [r for r in E if r["reliable"][tag]]
        k = sum(r[f"{tag}.s_trans"] >= 0.5 and r[f"{tag}.s_trans"] >= max(r[f"{tag}.s_sel"], r[f"{tag}.s_mig"]) for r in s)
        out[f"C1_{tag}"] = dict(n=len(s), k=k, pass_=bool(s and k >= 0.8 * len(s)))
    out["C1"] = out["C1_content_bge"]["pass_"] and out["C1_content_gte"]["pass_"]
    out["C2"] = all(abs(r[f"{t}.s_sel"]) <= 0.2 for r in E for t in ("content_bge", "style", "conv") if r["reliable"][t])
    s = [r for r in E if r["reliable"]["style"] and r["reliable"]["content_bge"] and r["n_events"] > 0]
    k = sum(r["style.s_mig"] > r["content_bge.s_mig"] for r in s)
    out["C3"] = dict(n=len(s), k=k, pass_=bool(s and k >= 0.75 * len(s)))
    s = [r for r in E if r["reliable"]["content_bge"] and r["n_trans"] >= 4]
    Cs = [r["content_bge.C"] for r in s]
    out["C4"] = dict(n=len(s), C=Cs, pass_=bool(s and all(c < 0 for c in Cs) and np.median(Cs) > -0.5))
    s = [r for r in E if r["reliable"]["content_bge"]]
    k = sum(r["content_bge.R"] >= 0.1 and r["content_bge.R"] - 1.96 * r["content_bge.R.se"] > 0 for r in s)
    out["C5"] = dict(n=len(s), k=k, pass_=bool(s and k >= 0.8 * len(s)))
    t4 = [r for r in rs.values() if "succ.style" in r]
    out["C6"] = dict(values=[(r["succ.style"], r["succ.content_bge"]) for r in t4],
                     pass_=bool(t4 and all(r["succ.style"] > r["succ.content_bge"] for r in t4)))
    out["overall"] = "CONFIRMED" if (out["C1"] and out["C2"] and out["C3"]["pass_"]) else "NOT CONFIRMED"
    return out


def run(confirm: bool):
    OUT.mkdir(parents=True, exist_ok=True)
    base = IL.Base(allow_holdout=confirm)
    sh = BLD.Shared()
    rs = {}
    specs = TARGETS if confirm else STANDINS
    for key, spec in specs.items():
        g = spec["goal"]
        if confirm:
            days = base.period_days(g, allow_holdout=True)
            if spec.get("tail"):
                days = [d for d in days if spec["tail"][0] <= d < spec["tail"][1]]
            P = heldout_period(base, g, days)
        else:
            P = standin_period(base, g, spec.get("window"))
        r = BLD.build_period(base, sh, g, P=P)
        if r is None:
            rs[key] = dict(goal=g, eligible=False)
            continue
        ad, adop, npz = r
        npz.pop("_resid", None)
        Pb = period_from_build(g, ad, adop, npz)
        rs[key] = score_target(Pb, spec)
        print(f"{key} (G{g:02d}): eligible {rs[key].get('eligible')}, transitions {rs[key].get('n_trans')}")
    v = verdicts(rs)
    name = "confirm_results.json" if confirm else "confirm_dryrun.json"
    (OUT / name).write_text(json.dumps(dict(results=rs, verdicts=v, run_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                                            mode="confirm" if confirm else "dry-run"), indent=1, default=float))
    print(json.dumps(v, indent=1, default=float))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.confirm:
        if not a.ack:
            sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
        import holdout_ledger as HL
        for key, tgt in LEDGER_TARGETS.items():
            st = HL.check("H89", tgt, modality="chat content (Price partition of agent-day traits)")
            if not st["allowed"]:
                sys.exit(f"refusing: holdout ledger forbids {tgt}: {st['prior_runs_same_family']}")
            if st["needs_disclosure"]:
                print(f"disclosure needed for {tgt}: {len(st['prior_runs'])} prior runs, {len(st['competing_planned'])} planned")
        OUT.mkdir(parents=True, exist_ok=True)
        seal = dict(sha256=hashlib.sha256(__doc__.encode()).hexdigest(),
                    sealed_at=dt.datetime.now(dt.timezone.utc).isoformat())
        (OUT / "confirm_sealed.json").write_text(json.dumps(seal, indent=1))
        run(confirm=True)
    elif a.dry_run:
        run(confirm=False)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
