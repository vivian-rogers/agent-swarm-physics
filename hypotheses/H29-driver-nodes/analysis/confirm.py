"""H29 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN on the holdout.

Targets:
  G47      (2026-06-15 -> 06-19; inside the NE21+NE23 window, which H04 used for ACTIVITY timing / Hawkes n). Reuse policy
           applies: H29's observable is message CONTENT (embedding pull), a different modality, unexamined.
  G51tail  (2026-09-07 -> 09-18; the #51 tail). Other cards (H12, H13, H22) have written but not run content-based
           confirmations on it; if any has run by then, the reuse policy applies and must be disclosed.
  G45      optional (--include-g45): H02 used activity timing; H23 plans message WORDING. H29's statistic (embedding
           pull after exposure) is different, but G45 needs its own disclosure.
Preconditions for a real run (checked, refuses otherwise):
  1. both flags --confirm --i-understand-this-uses-the-locked-holdout;
  2. this script, h29lib.py, scheme/build.py and the H29 card committed and unmodified (predictions frozen);
  3. LOG.md has a line naming H29 + the target (G47 / #51 tail / #45) + reuse/confirmation, and for G47 the H04 card
     too, for G45 the H02 and H23 cards.
Without the flags it DRY-RUNS the identical pipeline on non-holdout stand-ins (G38 for G47, G51d for the #51 tail),
reading nothing from the holdout.

FROZEN predictions (from round 1; Amendment 2 estimators; day-block bootstrap, 1000 draws):
  Visibility jumps use like-for-like controls (named visible vs named truly-invisible rows; unnamed vs unnamed).
  C1 address-gated influence (primary, #51 tail). Visibility jump for NAMED recipients > 0 with 95% CI excluding 0,
     and named jump >= 2.5 x unnamed jump (round 1, #51 segments: ratios 2.9-6.5). C1b (secondary, G47): named jump CI excludes 0 (round 1: 4/6 two-room-era
     units; the G38 dry-run stand-in fails it, so a C1b failure alone is not evidence against C1).
  C2 broadcast influence is weak. Unnamed-recipient jump: point estimate < 0.03 and upper CI < 0.05 in every target.
  C3 the pre-registered invisible placebo is biased by the visibility rule: pre-registered kappa < 0 (CI below 0) in
     the #51 tail, and > 30% of invisible rows come from call windows > 30 s in every target.
  C4 no validated 'where to inject' ranking (H29's original claim predicts the opposite). Cross-fitted (even/odd day)
     Spearman of the post-hoc driver score with held-out 2-h swarm spread < 0.3 in every target. H29's original claim
     is CONFIRMED instead if rho >= 0.3 in every target AND exceeds message volume's rho by >= 0.1.
  C5 in one large room the driver score reduces to volume: #51 tail Spearman(D, message volume) >= 0.5.
  C6 steering cost of the median agent grows ~N^2: E_med(#51 tail) / E_med(G47) within [0.5, 2] x (N_tail / N_47)^2.
Verdict: 'address-gated influence' CONFIRMED if C1 and C2 pass; 'no validated driver ranking' CONFIRMED if C4 passes;
the original H29 driver-ranking claim is confirmed only by C4's alternative clause.

Usage:
  uv run python hypotheses/H29-driver-nodes/analysis/confirm.py                    # dry run on G38 / G51d
  uv run python hypotheses/H29-driver-nodes/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402

ROOT = L.ROOT
ME = Path(__file__).resolve()
CARD = L.HYP / "README.md"
LOG = ROOT / "LOG.md"
SCHEME = L.HYP / "scheme/build.py"
STANDINS = {"G47": "G38", "G51tail": "G51d", "G45": "G44"}
LABEL = {"G47": ("G47", "#47"), "G51tail": ("#51 tail", "G51tail", "#51-tail"), "G45": ("G45", "#45")}
OTHER_CARDS = {"G47": [ROOT / "hypotheses/H04-reversible-forcing/README.md"],
               "G45": [ROOT / "hypotheses/H02-couplings-are-real/README.md",
                       ROOT / "hypotheses/H23-leader-distillation-copy/README.md"],
               "G51tail": []}


def _git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True)


def preconditions(targets: list[str]) -> list[str]:
    fails = []
    for f in (ME, CARD, ME.parent / "h29lib.py", SCHEME):
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


def load_scheme():
    spec = importlib.util.spec_from_file_location("h29_scheme_build", SCHEME)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def unit_stats(U: dict, label: str) -> dict:
    """The confirmatory statistics for one unit (same code paths as explore.py / posthoc.py)."""
    R = L.add_timing(U, L.row_stats(U))
    agents = L.network_agents(U)
    days = U["meta"]["days"]
    nd = len(days)
    even = {d for d in range(nd) if d % 2 == 0}
    odd = set(range(nd)) - even
    out = dict(unit=label, n_days=nd, n_agents=len(agents))
    ku = L.kappa_unit(R, B=1000)
    out["kappa_pre"] = ku["kappa"]
    out["kappa_pre_ci"] = ku.get("kappa_ci")
    rn = L.rd_kappa(R.filter(pl.col("ment_j")), B=1000)     # like-for-like: named visible vs named invisible
    ru = L.rd_kappa(R.filter(~pl.col("ment_j")), B=1000)    # unnamed visible vs unnamed invisible
    inv = R.filter(~pl.col("vis"))
    out.update(named=rn["jump"], named_ci=rn.get("ci"), unnamed=ru["jump"], unnamed_ci=ru.get("ci"),
               frac_inv_long=float(inv["c"].gt(L.C_MAX_S).mean()) if inv.height else None)
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
            vD.append(L.spearman(Ftr["D"], H))
            vV.append(L.spearman(Ftr["vol"], H))
        out["V2_D"] = float(np.nanmean(vD))
        out["V2_vol"] = float(np.nanmean(vV))
    return out


def verdicts(stats: dict[str, dict], tail_key: str, g47_key: str) -> dict:
    v = {}
    sts = list(stats.values())
    t = stats[tail_key]
    v["C1"] = bool(t["named_ci"] and t["named_ci"][0] > 0 and t["named"] >= 2.5 * max(t["unnamed"], 1e-9))
    if g47_key in stats:
        g = stats[g47_key]
        v["C1b"] = bool(g["named_ci"] and g["named_ci"][0] > 0)
    v["C2"] = all(s["unnamed"] < 0.03 and s["unnamed_ci"] and s["unnamed_ci"][1] < 0.05 for s in sts)
    v["C3"] = bool(t["kappa_pre_ci"] and t["kappa_pre_ci"][1] < 0) and all((s["frac_inv_long"] or 0) > 0.3 for s in sts)
    v["C4"] = all((s.get("V2_D") if s.get("V2_D") is not None else 1) < 0.3 for s in sts)
    v["C4_original_claim"] = all((s.get("V2_D") or -1) >= 0.3 and (s.get("V2_D") or -1) >= (s.get("V2_vol") or 0) + 0.1
                                 for s in sts)
    v["C5"] = (t["rho_D_vol"] or -1) >= 0.5
    if g47_key in stats:
        g = stats[g47_key]
        ratio = (t["E_med"] / g["E_med"]) / (t["n_agents"] / g["n_agents"]) ** 2
        v["C6_ratio"] = float(ratio)
        v["C6"] = 0.5 <= ratio <= 2.0
    v["address_gated_confirmed"] = bool(v["C1"] and v["C2"])
    v["no_validated_ranking_confirmed"] = bool(v["C4"])
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--include-g45", action="store_true")
    a = ap.parse_args()
    targets = ["G47", "G51tail"] + (["G45"] if a.include_g45 else [])
    emb = L.Emb()
    if a.confirm or a.ack:
        if not (a.confirm and a.ack):
            raise SystemExit("refusing: both --confirm and --i-understand-this-uses-the-locked-holdout are required")
        fails = preconditions(targets)
        if fails:
            raise SystemExit("refusing to touch the locked holdout:\n  " + "\n  ".join(fails))
        B = load_scheme()
        sh = B.h18.Shared()
        root = L.OUT / "confirm"
        stats = {}
        for t in targets:
            res = B.build_unit(sh, t, B.HOLDOUT_UNITS[t], allow_holdout=True)
            if res is None:
                raise SystemExit(f"no data for {t}")
            B.write_unit(t, res, root=root)
            U = L.attach_vectors(L.load_unit(t, root=root), emb)
            stats[t] = unit_stats(U, t)
        B.write_provenance(targets, root=root, extra={"confirmatory": True})
        out = dict(mode="CONFIRMATORY (locked holdout)", stats=stats, verdicts=verdicts(stats, "G51tail", "G47"))
        L.jdump(out, root / "confirm_results.json")
    else:
        stats = {}
        for t in targets:
            s = STANDINS[t]
            U = L.attach_vectors(L.load_unit(s), emb)   # non-holdout stand-in, already built by scheme/build.py
            stats[t] = unit_stats(U, f"{t} (dry run on {s})")
        out = dict(mode="DRY RUN on non-holdout stand-ins", stats=stats, verdicts=verdicts(stats, "G51tail", "G47"))
        L.jdump(out, L.OUT / "confirm_dryrun.json")
    for k, s in out["stats"].items():
        print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in s.items()})
    print(out["mode"], out["verdicts"])


if __name__ == "__main__":
    main()
