"""H29 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN ON ROUND-1B INPUTS. Written 2026-10-04; NOT RUN on the holdout.

Re-freeze of `confirm.py` (left byte-for-byte untouched), written before any holdout data was read. Changes (details in
`CONFIRM_R1B.md`):
  * visibility: DQ1 context ledger (`scheme/build.py: build_unit_ledger`; talk turn -> its model call, V/I sets from
    receiving calls; every invisible row strictly invisible, C_MAX_S = inf) instead of H18's call-start rule;
  * content: every statistic with BOTH embedding models (bge-small primary, gte-modernbert), each whitened in its own
    regime basis; a criterion passes only if it passes under both (C1-r1b, C2-r1b);
  * C3 re-written (C3-r1b): the 30-s call-window clause measured the old rule's bias and no longer applies;
  * new C7-r1b: the round-1b reply-graph network ranking (DQ2 `reply_graph`) predicts held-out 2-h swarm spread.
Activity tables, outages, work and failures are not inputs of H29. Nudges are not used (named = any roster mention).

Targets (unchanged): G47 (inside NE21+NE23; H04 ran activity timing there), G51tail (#51 tail), G45 optional
(--include-g45; H02 and H04 ran activity timing; H23 plans message wording). H29's observable is message content.

Preconditions for a real run (checked, refuses otherwise):
  1. both flags --confirm --i-understand-this-uses-the-locked-holdout;
  2. this script, CONFIRM_R1B.md, h29lib.py, r1b_extra.py, scheme/build.py and the card committed and unmodified;
  3. LOG.md and the card have a line naming H29 + the target + reuse/confirmation (G47: also H04's card; G45: H02, H23);
  4. infra/shared/holdout_ledger.check() allows every target (no same-family prior run).
Without the flags it DRY-RUNS on non-holdout ledger stand-ins (r1b/G38 for G47, r1b/G51d for the #51 tail, r1b/G44 for
G45), reading nothing from the holdout. The ledger check is printed in the dry run too (it reads the ledger only).

FROZEN predictions (round-1b re-freeze; Amendment 2 estimators; day-block bootstrap, 1000 draws). "Both" = bge and gte.
  C1-r1b address-gated influence (primary, #51 tail): named like-for-like jump CI > 0 and named >= 2.5 x unnamed, under
     both models. (Was bge only. Round 1b: named 0.05-0.08, unnamed 0.00-0.013 in G51b-d under both.)
  C1b (secondary, G47): named jump CI > 0 under bge (unchanged; underpowered in two-room weeks, failure is not evidence
     against C1).
  C2-r1b broadcast influence is weak: in the #51 tail, unnamed jump < 0.03 and upper CI < 0.05 under both models; in
     G47 (and G45) the point estimate < 0.03 under both models. (Was: CI clause in every target, bge. Reason: under the
     ledger the strictly-invisible control rows shrink (G41 867 -> 566), so two-room-week CIs widen; round 1b calls the
     two-room weeks underpowered. Disclosed: the G38 stand-in dry run (upper CI 0.063) prompted this check.)
  C3-r1b co-response, not leakage: the pre-registered kappa < 0 (CI below 0) in the #51 tail under bge. (Reason: under
     the ledger every invisible row is strictly invisible; round 1b kept kappa < 0 in 7/9 units, so the negative kappa
     is co-response to the same prior turn. The "> 30% of invisible rows from call windows > 30 s" clause is dropped.)
  C4 no validated content-pull driver ranking: cross-fitted Spearman(D, held-out spread) < 0.3 in every target (bge;
     gte reported). Original claim CONFIRMED instead if rho >= 0.3 everywhere AND >= volume's rho + 0.1. (unchanged)
  C5 #51 tail Spearman(D, message volume) >= 0.5 (unchanged, bge).
  C6 E_med(#51 tail) / E_med(G47) within [0.5, 2] x (N_tail / N_47)^2 (unchanged, bge).
  C7-r1b reply network: the mean over targets of the cross-fitted Spearman(D_rep, held-out spread) is > 0 and exceeds
     the mean of volume's rho, under bge (gte reported). (New: round 1b pooled 0.23 [0.05, 0.39], 6/9 > 0, volume ~0.)
Verdicts: 'address-gated influence' CONFIRMED if C1-r1b and C2-r1b pass; 'no validated content-pull ranking' CONFIRMED
if C4 passes; 'reply current ranks relays' CONFIRMED if C7-r1b passes.

Usage:
  uv run python hypotheses/H29-driver-nodes/analysis/confirm_r1b.py [--out FILE]      # dry run on ledger stand-ins
  uv run python hypotheses/H29-driver-nodes/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

os.environ["H29_DATA"] = "r1b"           # ledger units, C_MAX_S = inf (read by h29lib at import)
os.environ["H29_EMB"] = "bge_small"      # primary; gte is built explicitly below
os.environ.setdefault("POLARS_MAX_THREADS", "2")
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import importlib.util  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402
import r1b_extra as X  # noqa: E402

ROOT = L.ROOT
ME = Path(__file__).resolve()
CARD = L.HYP / "README.md"
LOG = ROOT / "LOG.md"
SCHEME = L.HYP / "scheme/build.py"
HYP = "H29"
MODELS = ("bge_small", "gte_modernbert")
STANDINS = {"G47": "G38", "G51tail": "G51d", "G45": "G44"}
LEDGER_T = {"G47": "G47", "G51tail": "#51-tail", "G45": "G45"}
LABEL = {"G47": ("G47", "#47"), "G51tail": ("#51 tail", "G51tail", "#51-tail"), "G45": ("G45", "#45")}
OTHER_CARDS = {"G47": [ROOT / "hypotheses/H04-reversible-forcing/README.md"],
               "G45": [ROOT / "hypotheses/H02-couplings-are-real/README.md",
                       ROOT / "hypotheses/H23-leader-distillation-copy/README.md"],
               "G51tail": []}
assert L.DATA_VERSION == "r1b" and np.isinf(L.C_MAX_S)


def _git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True)


def preconditions(targets: list[str]) -> list[str]:
    fails = []
    for f in (ME, ME.parent / "CONFIRM_R1B.md", CARD, ME.parent / "h29lib.py", ME.parent / "r1b_extra.py", SCHEME):
        rel = str(f.relative_to(ROOT))
        if _git("ls-files", "--error-unmatch", rel).returncode != 0:
            fails.append(f"not committed: {rel}")
        elif _git("diff", "--quiet", "HEAD", "--", rel).returncode != 0:
            fails.append(f"modified since last commit: {rel}")
    for t in targets:
        labels = LABEL[t]
        disclose = lambda line: ("H29" in line and any(x in line for x in labels)
                                 and re.search(r"reus|confirmat", line, re.I) is not None)
        for doc in [LOG, CARD] + OTHER_CARDS[t]:
            if not any(disclose(l) for l in doc.read_text().splitlines()):
                fails.append(f"{doc.relative_to(ROOT)} has no line disclosing H29's use of {labels[0]} "
                             "(H29 + target + reuse/confirmation)")
    return fails


def ledger_status(targets) -> list[str]:
    """holdout_ledger.check() per target with H29's own ledger modality/families; reads the ledger only."""
    sys.path.insert(0, str(ROOT))
    from infra.shared import holdout_ledger as hl
    led = hl.load()
    bad = []
    for t in targets:
        lt = LEDGER_T[t]
        mine = [e for e in led["entries"] if e["hypothesis"] == HYP and e["target"] == lt]
        fam = sorted({f for e in mine for f in e["estimator_family"]})
        r = hl.check(HYP, lt, "message content", fam)
        print(f"ledger {lt}: allowed={r['allowed']} needs_disclosure={r['needs_disclosure']} "
              f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
              f"same_family_runs={sorted({u['hypothesis'] for u in r['prior_runs_same_family']})} "
              f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}")
        if not r["allowed"]:
            bad.append(f"ledger: same-family prior run on {lt}")
    return bad


def load_scheme():
    spec = importlib.util.spec_from_file_location("h29_scheme_build", SCHEME)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def unit_stats(U: dict, label: str, full: bool) -> dict:
    """Confirmatory statistics for one unit and one embedding model (code paths of confirm.py on ledger units).
    full=False skips the network fits (gte: only the jumps, kappa and the content-pull V2 are scored)."""
    R = L.add_timing(U, L.row_stats(U))
    agents = L.network_agents(U)
    days = U["meta"]["days"]
    nd = len(days)
    even = {d for d in range(nd) if d % 2 == 0}
    odd = set(range(nd)) - even
    out = dict(unit=label, n_days=nd, n_agents=len(agents))
    ku = L.kappa_unit(R, B=1000)
    out["kappa_pre"], out["kappa_pre_ci"] = ku["kappa"], ku.get("kappa_ci")
    rn = L.rd_kappa(R.filter(pl.col("ment_j")), B=1000)
    ru = L.rd_kappa(R.filter(~pl.col("ment_j")), B=1000)
    out.update(named=rn["jump"], named_ci=rn.get("ci"), unnamed=ru["jump"], unnamed_ci=ru.get("ci"))
    F = L.fit_network_v2(U, R, agents, B_pair=300)
    out["rho_D_vol"] = L.spearman(F["D"], F["vol"])
    out["E_med"] = float(np.nanmedian(F["E"]))
    if len(even) and len(odd):
        Fe = L.fit_network_v2(U, R, agents, day_set=even, B_pair=200)
        Fo = L.fit_network_v2(U, R, agents, day_set=odd, B_pair=200)
        dmap = {d: i for i, d in enumerate(days)}
        am = U["msgs"].filter(pl.col("kind") == 0).with_columns(
            pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day_idx"))
        hs = L.horizon_spread(U, am)
        vD, vV = [], []
        for test, Ftr in ((odd, Fe), (even, Fo)):
            H = L.hourly_spread(hs, agents, L.active_hours(U, [days[d] for d in test]), day_set=test)
            vD.append(L.spearman(Ftr["D"], H)); vV.append(L.spearman(Ftr["vol"], H))
        out["V2_D"], out["V2_vol"] = float(np.nanmean(vD)), float(np.nanmean(vV))
    if full:
        out["reply"] = reply_network(U, R, agents)
    return out


def reply_network(U, R, agents) -> dict:
    """Round-1b reply-graph network (r1b_extra.reply_network_unit on an already loaded unit)."""
    days = U["meta"]["days"]
    nd = len(days)
    even = {d for d in range(nd) if d % 2 == 0}
    odd = set(range(nd)) - even
    par = X.parent_premium(R, U)
    c = par["pull_parent"]
    c = max(c, 0.01) if np.isfinite(c) else 0.01
    g = L.gamma_unit(U)["gamma"]

    def fit(ds):
        r = X.reply_rates(U, agents, ds)
        sc = L.gramian_scores(L.build_Q(c * r, g))
        return dict(D=sc["D"], vol=L.message_rates(U, agents, ds), inrate=r.sum(1))
    res = dict(c=c)
    if not (even and odd):
        return res
    Fe, Fo = fit(even), fit(odd)
    res["split_half_D"] = L.spearman(Fe["D"], Fo["D"])
    dmap = {d: i for i, d in enumerate(days)}
    am = U["msgs"].filter(pl.col("kind") == 0).with_columns(
        pl.col("pt_date").replace_strict(dmap, default=None, return_dtype=pl.Int16).alias("day_idx")).filter(
        pl.col("day_idx").is_not_null())
    hs = L.horizon_spread(U, am)
    folds = []
    for test, Ftr in ((odd, Fe), (even, Fo)):
        H = L.hourly_spread(hs, agents, L.active_hours(U, [days[d] for d in test]), day_set=test)
        folds.append((L.spearman(Ftr["D"], H), L.spearman(Ftr["vol"], H), L.spearman(Ftr["inrate"], H)))
    res["V2_Drep"], res["V2_vol"], res["V2_inrate"] = (float(np.nanmean([f[i] for f in folds])) for i in range(3))
    return res


def verdicts(S: dict[str, dict[str, dict]], tail: str, g47: str) -> dict:
    """S[model][target] -> stats. bge = primary."""
    b, gt = S["bge_small"], S["gte_modernbert"]
    v = {}

    def c1(st):
        t = st[tail]
        return bool(t["named_ci"] and t["named_ci"][0] > 0 and t["named"] >= 2.5 * max(t["unnamed"], 1e-9))

    def c2(st):
        t = st[tail]
        return bool(t["unnamed"] < 0.03 and t["unnamed_ci"] and t["unnamed_ci"][1] < 0.05
                    and all(s["unnamed"] < 0.03 for s in st.values()))
    v["C1_bge"], v["C1_gte"] = c1(b), c1(gt)
    v["C1_r1b"] = v["C1_bge"] and v["C1_gte"]
    if g47 in b:
        v["C1b"] = bool(b[g47]["named_ci"] and b[g47]["named_ci"][0] > 0)
    v["C2_bge"], v["C2_gte"] = c2(b), c2(gt)
    v["C2_r1b"] = v["C2_bge"] and v["C2_gte"]
    v["C3_r1b"] = bool(b[tail]["kappa_pre_ci"] and b[tail]["kappa_pre_ci"][1] < 0)
    v["C4"] = all((s.get("V2_D") if s.get("V2_D") is not None else 1) < 0.3 for s in b.values())
    v["C4_gte"] = all((s.get("V2_D") if s.get("V2_D") is not None else 1) < 0.3 for s in gt.values())
    v["C4_original_claim"] = all((s.get("V2_D") or -1) >= 0.3 and (s.get("V2_D") or -1) >= (s.get("V2_vol") or 0) + 0.1
                                 for s in b.values())
    v["C5"] = (b[tail]["rho_D_vol"] or -1) >= 0.5
    if g47 in b:
        ratio = (b[tail]["E_med"] / b[g47]["E_med"]) / (b[tail]["n_agents"] / b[g47]["n_agents"]) ** 2
        v["C6_ratio"], v["C6"] = float(ratio), 0.5 <= ratio <= 2.0

    def c7(st):
        rd = [s["reply"].get("V2_Drep") for s in st.values() if "reply" in s]
        rv = [s["reply"].get("V2_vol") for s in st.values() if "reply" in s]
        if not rd or any(x is None for x in rd):
            return None
        return bool(np.nanmean(rd) > 0 and np.nanmean(rd) > np.nanmean(rv))
    v["C7_r1b"], v["C7_gte"] = c7(b), c7(gt)
    v["address_gated_confirmed"] = bool(v["C1_r1b"] and v["C2_r1b"])
    v["no_validated_content_ranking_confirmed"] = bool(v["C4"])
    v["reply_current_ranks_relays_confirmed"] = bool(v["C7_r1b"])
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--include-g45", action="store_true")
    ap.add_argument("--out", type=Path, default=L.OUT_BASE / "r1b" / "confirm_r1b_dryrun.json", help="dry-run result file")
    a = ap.parse_args()
    targets = ["G47", "G51tail"] + (["G45"] if a.include_g45 else [])
    embs = {m: L.Emb(model=m) for m in MODELS}
    S = {m: {} for m in MODELS}
    if a.confirm or a.ack:
        if not (a.confirm and a.ack):
            raise SystemExit("refusing: both --confirm and --i-understand-this-uses-the-locked-holdout are required")
        fails = preconditions(targets) + ledger_status(targets)
        if fails:
            raise SystemExit("refusing to touch the locked holdout:\n  " + "\n  ".join(fails))
        # reply-parent pairs of the held-out days (r1b_extra filters ~holdout for exploration)
        X.RP = (pl.read_parquet(L.SH / "reply_pairs.parquet",
                                columns=["b_msg", "a_msg", "pair_set", "p_reply", "parent", "labelled", "a_agent",
                                         "b_agent", "a_kind", "pt_date", "holdout"]).filter(pl.col("pair_set") == "cand"))
        B = load_scheme()
        sh = B.h18.Shared()
        root = L.OUT_BASE / "confirm_r1b"
        for t in targets:
            res = B.build_unit_ledger(sh, t, B.HOLDOUT_UNITS[t], allow_holdout=True)
            if res is None:
                raise SystemExit(f"no data for {t}")
            B.write_unit(t, res, root=root)
            for m in MODELS:
                U = L.attach_vectors(L.load_unit(t, root=root), embs[m])
                S[m][t] = unit_stats(U, t, full=True)
        B.write_provenance(targets, root=root, extra={"confirmatory": True, "visibility": "DQ1 context ledger",
                                                      "models": list(MODELS)})
        out = dict(mode="CONFIRMATORY r1b (locked holdout)", stats=S, verdicts=verdicts(S, "G51tail", "G47"))
        L.jdump(out, root / "confirm_r1b_results.json")
    else:
        ledger_status(targets)
        for t in targets:
            s = STANDINS[t]
            for m in MODELS:
                U = L.attach_vectors(L.load_unit(s, root=L.OUT_BASE / "r1b"), embs[m])
                S[m][t] = unit_stats(U, f"{t} (dry run on r1b/{s}, {m})", full=True)
                print(m, t, "done", flush=True)
        out = dict(mode="DRY RUN r1b on non-holdout ledger stand-ins", stats=S, verdicts=verdicts(S, "G51tail", "G47"))
        a.out.parent.mkdir(parents=True, exist_ok=True)
        L.jdump(out, a.out)
    for m, st in out["stats"].items():
        for k, s in st.items():
            print(m, k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in s.items()})
    print(out["mode"], out["verdicts"])


if __name__ == "__main__":
    main()
