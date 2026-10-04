"""H28 confirmatory test on the locked holdout (#22, #28, #45). WRITTEN, NOT RUN.

  uv run python hypotheses/H28-links-spread-herding/analysis/confirm_holdout.py --dry-run
      runs the frozen pipeline on non-holdout stand-ins (#31 for #22, #30 for #28, #41 for #45); touches no holdout data
  uv run python hypotheses/H28-links-spread-herding/analysis/confirm_holdout.py --confirm --i-understand-this-uses-the-locked-holdout
      builds the scheme for the held-out periods into data/processed/H28-links-spread-herding/confirm/ and applies the
      frozen rule. Refuses unless this script and the card are committed and unmodified (reuse policy, hypotheses/holdout.md).

Reuse disclosure (hypotheses/holdout.md, "Reuse of a held-out period by a second hypothesis"): H11's frozen confirmatory
test targets the same periods (equal-time co-occupancy of project labels); H02 has run #45 (1-min activity timing) and
H23 will reuse #45 (message style). H28's statistic (lagged link-exposure -> arrival hazard against a link time-shift
null, lead placebo and other-room placebo) is a different statistic that nobody has computed on these periods. If H11
or H23 has already run on a target, this run is a second use and must be disclosed in both cards and LOG.md.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import numpy as np  # noqa: E402

import h28core as hc  # noqa: E402
from h28lib import OUT, ROOT, gname, held_goals  # noqa: E402

TARGETS = {22: dict(standin=31, rooms=1), 28: dict(standin=30, rooms=1), 45: dict(standin=41, rooms=2)}

# ---- Frozen decision rule (written 2026-10-04 after round 1, before any holdout data was read) --------------------
FROZEN = dict(
    shifts=99, alpha=0.05, z_shift=2.0,
    # Original H28 claim (links drive switches):
    # C1 (per target): kappa > 0, cluster-robust p < 0.05 and z_shift >= 2 (the round-1 P1 rule)
    # C2 (common drive): kappa - kappa_lead > 0 with one-sided p < 0.05 in >= 2 of 3 targets
    # C3 (room placebo, #45 only): kappa_other < kappa_same and kappa_other's 95% CI contains 0
    # C4 (branching): R_link < 0.5 in every target
    # CONFIRMED if C1 holds in >= 2/3 targets and C2, C3, C4 hold; REFUTED if C1 fails (kappa <= 0 or z_shift < 2)
    # in >= 2/3 targets; otherwise INCONCLUSIVE.
    # Round-1 pattern (co-burst reading), evaluated separately:
    # R1 kappa > 0 with p < 0.05 in >= 2/3 targets (links co-move with switches);
    # R2 kappa_lead >= kappa (joint model) in >= 2/3 targets (future links predict switches at least as well);
    # R3 R_link in [0.05, 0.45] in every target.
    # PATTERN HOLDS if R1, R2 and R3 all hold; PATTERN FAILS if R2 fails in >= 2/3 targets.
    # Round-1 expectation: original claim REFUTED or INCONCLUSIVE; round-1 pattern HOLDS.
)


def committed_clean(paths) -> bool:
    for p in paths:
        r = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", str(p)], capture_output=True)
        if r.returncode != 0:
            return False
        r = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "HEAD", "--", str(p)])
        if r.returncode != 0:
            return False
    return True


def evaluate(P, seed=0):
    from scipy.stats import norm
    rng = np.random.default_rng(seed)
    R, B, G = hc.build_rows(P)
    P["_B"] = B
    F = hc.link_features(P, R)
    res = hc.fit(R, F, "primary")
    k, se = hc.coef(res, "E60")
    null = []
    for _ in range(FROZEN["shifts"]):
        lt, tv = hc.shift_links(P, rng)
        null.append(hc.coef(hc.fit(R, hc.link_features(P, R, link_t=lt, t_vis=tv), "primary"), "E60")[0])
    null = np.array([v for v in null if np.isfinite(v)])
    z = (k - null.mean()) / null.std(ddof=1)
    p = 2 * norm.sf(abs(k / se))
    rl = hc.fit(R, F, "lead")
    i, j = rl["names"].index("E60"), rl["names"].index("lead60")
    d = rl["beta"][i] - rl["beta"][j]
    vd = rl["V"][i, i] + rl["V"][j, j] - 2 * rl["V"][i, j]
    out = dict(kappa=k, se=se, p=p, z_shift=z, diff_lead=d, p_diff_lead=float(norm.sf(d / np.sqrt(vd))),
               kappa_joint=float(rl["beta"][i]), kappa_lead=float(rl["beta"][j]),
               arrivals=int(R["y"].sum()), links=int((P["links"]["x"] >= 0).sum()))
    out["C1"] = bool(k > 0 and p < FROZEN["alpha"] and z >= FROZEN["z_shift"])
    out["C2"] = bool(d > 0 and out["p_diff_lead"] < FROZEN["alpha"])
    if F["other60"].sum() > 0:          # a second room with links to universe projects exists
        rr = hc.fit(R, F, "room")
        ko, so = hc.coef(rr, "other60")
        ks, _ = hc.coef(rr, "E60")
        out.update(kappa_other=ko, se_other=so, kappa_same=ks, C3=bool(ko < ks and abs(ko / so) < 1.96))
    att = hc.attributable(res, R, F, hc.count_exposures(P), link_names=("E60",), draws=0)
    out.update(lam=att["lam"], R_link=att["R_link"], C4=bool(att["R_link"] < 0.5))
    out["R1"] = bool(k > 0 and p < FROZEN["alpha"])
    out["R2"] = bool(out["kappa_lead"] >= out["kappa_joint"])
    out["R3"] = bool(0.05 <= att["R_link"] <= 0.45)
    return out


def decide(per):
    n = len(per)
    c1 = sum(v["C1"] for v in per.values())
    c2 = sum(v["C2"] for v in per.values()) >= 2
    c3 = all(v.get("C3", True) for v in per.values())
    c4 = all(v["C4"] for v in per.values())
    fail = sum((v["kappa"] <= 0) or (v["z_shift"] < FROZEN["z_shift"]) for v in per.values())
    if c1 >= 2 and c2 and c3 and c4:
        claim = "CONFIRMED"
    elif fail >= 2 * n / 3:
        claim = "REFUTED"
    else:
        claim = "INCONCLUSIVE"
    r1 = sum(v["R1"] for v in per.values()) >= 2 * n / 3
    r2n = sum(v["R2"] for v in per.values())
    r3 = all(v["R3"] for v in per.values())
    pattern = "HOLDS" if (r1 and r2n >= 2 * n / 3 and r3) else "FAILS" if (n - r2n) >= 2 * n / 3 else "INCONCLUSIVE"
    return dict(claim=claim, pattern=pattern)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run == a.confirm:
        raise SystemExit("choose exactly one of --dry-run or --confirm")
    per = {}
    if a.dry_run:
        for g, t in TARGETS.items():
            s = t["standin"]
            assert s not in held_goals()
            P = hc.load_period(OUT / gname(s))
            per[f"standin_{s}_for_{g}"] = evaluate(P, seed=s)
            print(s, json.dumps(per[f"standin_{s}_for_{g}"], default=float))
        verdict = decide(per)
        (OUT / "confirm_dryrun.json").write_text(json.dumps(dict(verdict=verdict, per=per, frozen=FROZEN), indent=1, default=float))
        print("DRY RUN verdict on stand-ins:", verdict)
        return
    if not a.ack:
        raise SystemExit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
    card = HERE.parent / "README.md"
    if not committed_clean([Path(__file__).resolve(), card, HERE / "h28core.py", HERE.parent / "scheme/build.py"]):
        raise SystemExit("refusing: commit this script, h28core.py, scheme/build.py and the card (predictions) before the "
                         "confirmatory run (reuse policy, hypotheses/holdout.md)")
    sys.path.insert(0, str(HERE.parent / "scheme"))
    import build as h28build  # noqa: E402
    sh = h28build.Shared()
    out_dir = OUT / "confirm"
    for g in TARGETS:
        assert g in held_goals(), f"#{g} is not in the holdout"
        h28build.build_period(sh, g, allow_holdout=True, only_holdout=True, out=out_dir)
        per[g] = evaluate(hc.load_period(out_dir / gname(g)), seed=g)
        print(g, json.dumps(per[g], default=float))
    verdict = decide(per)
    (out_dir / "confirm_result.json").write_text(json.dumps(dict(verdict=verdict, per=per, frozen=FROZEN), indent=1, default=float))
    print("CONFIRMATORY verdict:", verdict)


if __name__ == "__main__":
    main()
