"""H23 confirmatory test on goal period #45 ("Follow your leader!", 2026-06-01 -> 06-05), LOCKED HOLDOUT.

Status: written 2026-10-03 after the G44 exploratory round; NOT RUN on #45.

Observable: the CONTENT of chat messages in #best during #45 (the Fine-Tuned Leader, roster agent 30, runs the same
weights kimi-leader-v7-aug-64 as agent 28 in #44). H02 used #45 for activity timing only (1-min activity spins);
nobody has examined #45 message content. Reuse policy (`hypotheses/holdout.md`, "Reuse of a held-out period by a
second hypothesis"): this script refuses to run on #45 unless
  1. this script and the H23 card are committed and unmodified (git), i.e. predictions frozen before the run;
  2. the flags --confirm --i-understand-this-uses-the-locked-holdout are given;
  3. the reuse is disclosed in both cards (H23 and H02) and in LOG.md (checked by grep for 'H23' near '#45').
Without the flags it runs a DRY RUN: the identical pipeline on the non-holdout G44 period (agent 28, v7-aug-64
segment) as a stand-in, reading nothing from #45.

FROZEN predictions (C1-C5), evaluated on the 70 leader messages of #45; controls = every other agent message in #best
during #45 (Kimi K2.6 = K_same); corpus = the 31 recovered v7-aug-64 targets; coder = plan-act coder v3 (h23lib);
base field = Kimi K2.6 in #38-#42, #44 (G44 table). One-sided permutation tests, 10,000 draws.
  C1 vocabulary copied (primary). Corpus-distinctive marker rate: leader / CTRL >= 1.2 and p < 0.05;
     and leader > Kimi K2.6 same-period (p < 0.10)  [the R1 test #44 could not make with 6 Kimi messages].
  C2 phrasing not copied. Pooled bigram copy information of the leader vs CTRL <= 0.01 bits/bigram, and the
     leader's mean bigram copy fraction < 0.5 x the offline sibling outputs' (0.182 in G44).
  C3 plans not copied. Coder directive share: leader <= corpus - 0.25 and JSD(leader, corpus) > 95th percentile of
     corpus self-resampling at n = 70; corpus -> leader channel (fine): excess copy c_ex < 0.10 and copy efficiency
     (c_ex / perfect-copy c_ex) < 0.5.
  C4 plans follow the room (rival R2 at the plan level). JSD(leader, leader contexts) < JSD(leader, corpus), and the
     leader's lexical context copy (token-matched bigrams) is not above the controls' (one-sided p > 0.10).
  C5 embedding (exception (b), descriptive-level). d = cos(z, C) - cos(z, K): leader > Kimi K2.6 same-period
     (p < 0.10). The field-level P3c is not run unless the G44 invariance check passed (it failed in G44).
Verdict: H23 "copies vocabulary" CONFIRMED if C1 and C2 pass; "plans not copied" CONFIRMED if C3 passes;
R1 rejected if C1's Kimi clause and C5 pass; R2 favored at the plan level if C4 passes.

Usage:
  uv run python hypotheses/H23-leader-distillation-copy/analysis/confirm_g45.py            # dry run on G44
  uv run python hypotheses/H23-leader-distillation-copy/analysis/confirm_g45.py --confirm \
      --i-understand-this-uses-the-locked-holdout                                           # the real test
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h23lib as L  # noqa: E402
from h23run import run_period, _np  # noqa: E402

ROOT = L.ROOT
CARD = ROOT / "hypotheses/H23-leader-distillation-copy/README.md"
H02 = ROOT / "hypotheses/H02-couplings-are-real/README.md"
LOG = ROOT / "LOG.md"
ME = Path(__file__).resolve()
OFFLINE_C2_G44 = 0.182


def _git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True)


def preconditions() -> list[str]:
    fails = []
    for f in (ME, CARD, ME.parent / "h23lib.py", ME.parent / "h23run.py", ME.parents[1] / "scheme/build_messages.py"):
        rel = str(f.relative_to(ROOT))
        if _git("ls-files", "--error-unmatch", rel).returncode != 0:
            fails.append(f"not committed: {rel}")
        elif _git("diff", "--quiet", "HEAD", "--", rel).returncode != 0:
            fails.append(f"modified since last commit: {rel}")
    disclose = lambda line: ("H23" in line and ("#45" in line or "G45" in line)
                             and re.search(r"reus|confirmat", line, re.I) is not None)
    if not any(disclose(l) for l in H02.read_text().splitlines()):
        fails.append("H02 card has no line disclosing H23's reuse of #45 (H23 + #45 + reuse/confirmation)")
    if not any(disclose(l) for l in LOG.read_text().splitlines()):
        fails.append("LOG.md has no line disclosing H23's reuse of #45 (H23 + #45 + reuse/confirmation)")
    return fails


def evaluate(R: dict) -> dict:
    t1, t3 = R["O1"]["tests"], R["O3"]["tests"]
    out = {}
    a = t1["r_corpus:leader>CTRL"]
    k = t1["r_corpus:leader>K_same"]
    ratio = a["mean_a"] / a["mean_b"] if a["mean_b"] else float("nan")
    out["C1"] = {"pass": bool(ratio >= 1.2 and a["p"] < 0.05 and k["p"] < 0.10), "ratio_ctrl": ratio,
                 "p_ctrl": a["p"], "p_kimi": k["p"], "leader": a["mean_a"], "ctrl": a["mean_b"], "kimi": k["mean_b"]}
    ci = R["O1"]["copy_information"]["n2"]
    c2 = R["O1"]["means"]["leader"]["c2"][0]
    out["C2"] = {"pass": bool(ci["I_copy_bits_vs_ctrl"] <= 0.01 and c2 < 0.5 * OFFLINE_C2_G44),
                 "I_copy_bigram_bits": ci["I_copy_bits_vs_ctrl"], "leader_c2": c2}
    ds = R["O2"]["directive_share"]
    ch = R["O2"]["corpus_channel"]["leader"]["fine"]
    out["C3"] = {"pass": bool(ds["leader"][0] <= ds["corpus"][0] - 0.25
                              and R["O2"]["jsd"]["leader"] > R["O2"]["jsd_corpus_self_n"]["p95"]
                              and ch["c_ex"] < 0.10 and (np.isnan(ch["copy_efficiency"]) or ch["copy_efficiency"] < 0.5)),
                 "directive_leader": ds["leader"][0], "directive_corpus": ds["corpus"][0],
                 "jsd": R["O2"]["jsd"]["leader"], "jsd_p95": R["O2"]["jsd_corpus_self_n"]["p95"],
                 "c_ex": ch["c_ex"], "copy_efficiency": ch["copy_efficiency"]}
    r2 = R["R2"]["test_ctx_c2:leader>CTRL"]
    jl = R["O2"]["jsd_leader"]
    out["C4"] = {"pass": bool(jl["leader_ctx"] < jl["corpus"] and r2["p"] > 0.10),
                 "jsd_leader_ctx": jl["leader_ctx"], "jsd_leader_corpus": jl["corpus"], "p_ctx_copy": r2["p"]}
    d = t3.get("d:leader>K_same", {"p": float("nan"), "diff": float("nan")})
    out["C5"] = {"pass": bool(d["p"] < 0.10), "p": d["p"], "diff": d["diff"]}
    out["H23_vocabulary_copied"] = out["C1"]["pass"] and out["C2"]["pass"]
    out["H23_plans_not_copied"] = out["C3"]["pass"]
    out["R1_rejected"] = bool(out["C1"]["p_kimi"] < 0.10 and out["C5"]["pass"])
    out["R2_favored_on_plans"] = out["C4"]["pass"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    args = ap.parse_args()
    from build_messages import build
    if args.confirm or args.ack:
        if not (args.confirm and args.ack):
            raise SystemExit("refusing: both --confirm and --i-understand-this-uses-the-locked-holdout are required")
        fails = preconditions()
        if fails:
            raise SystemExit("refusing (holdout reuse policy):\n  - " + "\n  - ".join(fails))
        pdir = L.OUT / "G45"
        build(45, pdir, allow_holdout=True)             # live = whole period; leader = agent 30
        R = run_period(pdir, {"checkpoints": ["kimi-v7-aug-64"]})
        mode = "CONFIRMATORY #45 (locked holdout)"
    else:
        # dry run: identical code path on the non-holdout G44 v7-aug-64 segment; nothing from #45 is read
        pdir = L.OUT / "G44" / "dryrun_confirm"
        pdir.mkdir(parents=True, exist_ok=True)
        for f in ("messages.parquet", "vectors.npz"):
            shutil.copy(L.OUT / "G44" / f, pdir / f)
        R = run_period(pdir, {"checkpoints": ["kimi-v7-aug-64"]})
        mode = "DRY RUN on G44 (non-holdout stand-in)"
    V = evaluate(R)
    V["mode"] = mode
    V["n"] = R["n"]
    (pdir / "confirm_verdicts.json").write_text(json.dumps(V, indent=1, default=_np))
    print(json.dumps(V, indent=1, default=_np))


if __name__ == "__main__":
    main()
