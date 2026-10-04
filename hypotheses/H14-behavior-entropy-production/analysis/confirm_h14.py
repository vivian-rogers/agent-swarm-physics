"""H14 confirmatory test on the LOCKED HOLDOUT. Written in exploratory round 1 (2026-10-03); NOT RUN.

Refuses to run on holdout data unless BOTH flags are given:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` runs the identical pipeline and criteria on non-holdout stand-in periods (no holdout day is read) and
writes to data/processed/H14-behavior-entropy-production/confirm_dryrun/.

Pre-registered criteria: see CRITERIA below and the card (README.md, "Confirmatory test"). They were written after
exploratory round 1 and before any holdout use; the card hash is printed at run time so the version can be audited.

Holdout periods used (hypotheses/holdout.json):
  regime III: #45 (5 d), #46 (6 d, 8 h), #47 (5 d), #49 (4 d), #50 (5 d, 8 h), #51 tail (2026-09-07 -> 09-18);
  regime I:   #22, #28, #29 (5 d each; 4 h).
  #43 and #48 (1 day each) are too short for day-fold cross-fitting and are not used.
Stand-ins for --dry-run (non-holdout, same regime and structure): #39, #40, #41, #42, #44, #51 07-06 -> 07-17 (regime III),
#23, #24, #25 (regime I).

Usage:
  uv run python hypotheses/H14-behavior-entropy-production/analysis/confirm_h14.py --dry-run [--fast]
  uv run python hypotheses/H14-behavior-entropy-production/analysis/confirm_h14.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h14lib as L  # noqa: E402,F401  (thread env)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import run_period as RP  # noqa: E402
from build_states import build  # noqa: E402

sys.path.insert(0, str(HERE.parents[2] / "infra/shared"))
from common import holdout_mask  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H14-behavior-entropy-production"
CARD = HERE.parent / "README.md"

HOLDOUT = {
    "G45": dict(goals=[45], regime="III"), "G46": dict(goals=[46], regime="III"), "G47": dict(goals=[47], regime="III"),
    "G49": dict(goals=[49], regime="III"), "G50": dict(goals=[50], regime="III"),
    "G51tail": dict(goals=[51], regime="III", from_="2026-09-07", to="2026-09-21"),
    "G22": dict(goals=[22], regime="I"), "G28": dict(goals=[28], regime="I"), "G29": dict(goals=[29], regime="I"),
}
STAND_INS = {
    "G45": dict(goals=[39], regime="III"), "G46": dict(goals=[40], regime="III"), "G47": dict(goals=[41], regime="III"),
    "G49": dict(goals=[44], regime="III"), "G50": dict(goals=[42], regime="III"),
    "G51tail": dict(goals=[51], regime="III", from_="2026-07-06", to="2026-07-18"),
    "G22": dict(goals=[23], regime="I"), "G28": dict(goals=[24], regime="I"), "G29": dict(goals=[25], regime="I"),
}

# ============================================================================ pre-registered criteria
# Written 2026-10-03 after exploratory round 1 (all non-holdout) and before any holdout use. Thresholds come from the
# exploratory numbers quoted in each docstring; the card's "Confirmatory test" section is the authoritative text.
R3 = ["G45", "G46", "G47", "G49", "G50", "G51tail"]
R1 = ["G22", "G28", "G29"]
EXPLORATORY = ["G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
RNG = np.random.default_rng(20261003)


def _have(out, names):
    return [n for n in names if n in out]


def c1_fine_arrow(out):
    """Fine action classes: >= 75% of test agents above the DB null (Newton) in >= 5 of the 6 regime-III periods
    (exploration 0.80-1.00 in 9/9 periods)."""
    v = {n: out[n][1]["act_frac_above_null"] for n in _have(out, R3)}
    k = sum(x >= 0.75 for x in v.values())
    return {"values": v, "k": k, "pass": bool(k >= min(5, len(v)) and len(v) >= 5)}


def c2_regime_contrast(out):
    """Every regime-I period's median coarse Newton Sigma_i is >= 3x every regime-III period's (exploration 7-29x)."""
    m1 = {n: out[n][1]["median_newton"] for n in _have(out, R1)}
    m3 = {n: out[n][1]["median_newton"] for n in _have(out, R3)}
    ok = all(a >= 3 * max(b, 1e-12) for a in m1.values() for b in m3.values())
    return {"regime_I": m1, "regime_III": m3, "pass": bool(ok and m1 and m3)}


def c3_small_coarse_arrow(out):
    """Regime-III median coarse Newton Sigma_i in [0, 0.02] nats/transition in >= 5 of 6 periods (exploration 0.0025-0.010)."""
    v = {n: out[n][1]["median_newton"] for n in _have(out, R3)}
    k = sum(0 <= x <= 0.02 for x in v.values())
    return {"values": v, "k": k, "pass": bool(k >= min(5, len(v)) and len(v) >= 5)}


def c4_long_window(out):
    """#51 tail: >= 80% of test agents above the DB null on coarse turns (exploration G51 0.97)."""
    if "G51tail" not in out:
        return {"pass": None}
    v = out["G51tail"][1]["P2_frac_above_null_newton"]
    return {"value": v, "n": out["G51tail"][1]["P2_n"], "pass": bool(v >= 0.8)}


def c5_current(out):
    """work -> chat -> consolidate -> work positive in > 50% of agents in >= 4 of 6 regime-III periods, and the pooled
    sign test over agents p < 0.01 (exploration: > 50% in 6/8, G51 0.81)."""
    from scipy.stats import binomtest
    fr, pos, tot = {}, 0, 0
    for n in _have(out, R3):
        a = out[n][0].filter(pl.col("eligible"))["aff_work>chat>cons"].to_numpy()
        fr[n] = float(np.mean(a > 0))
        pos += int((a > 0).sum()); tot += len(a)
    p = float(binomtest(pos, tot, 0.5, alternative="greater").pvalue) if tot else np.nan
    k = sum(x > 0.5 for x in fr.values())
    return {"frac_pos": fr, "k": k, "pooled_p": p, "pass": bool(k >= 4 and p < 0.01)}


def c6_no_family_arrow(out):
    """HH19 null replicates: stratified lab-permutation eta^2 p > 0.05 and Anthropic - OpenAI two-sided p > 0.05
    (exploration p = 0.89 and 0.85). Low power (S2c: 0.32 at a 2x family difference), so a pass is weak evidence."""
    import summarize as SU
    ag = {n: out[n][0] for n in _have(out, R3)}
    fm = SU.family_meta(ag, list(ag), "newton_exc")
    return {"p_eta2": fm["p_eta2"], "p_two": fm["p_two"], "sum_diff": fm["sum_diff_anth_minus_openai"],
            "pass": bool(fm["p_eta2"] > 0.05 and fm["p_two"] > 0.05)}


def _pct_ranks(df, col):
    d = df.filter(pl.col("eligible") & pl.col(col).is_not_nan())
    v = d[col].to_numpy()
    r = (np.argsort(np.argsort(v)) + 0.5) / max(len(v), 1)
    return dict(zip(d["agent"].to_list(), r))


def c7_agent_trait(out, col="min_newton_exc", nperm=10000):
    """Out-of-sample agent trait: Spearman(exploratory mean percentile rank, holdout mean percentile rank) > 0, one-sided
    permutation p < 0.05, for agents eligible in >= 2 exploratory regime-III periods and >= 1 holdout regime-III period.
    Primary on the minute grid (exploration mean pairwise Spearman 0.24, p = 0.0005); turns reported (0.13, p = 0.02)."""
    from scipy.stats import spearmanr
    res = {}
    for c in (col, "newton_exc"):
        ex, ho = {}, {}
        for g in EXPLORATORY:
            f = DATA / g / "agents.parquet"
            if f.exists():
                for a, r in _pct_ranks(pl.read_parquet(f), c).items():
                    ex.setdefault(a, []).append(r)
        for n in _have(out, R3):
            for a, r in _pct_ranks(out[n][0], c).items():
                ho.setdefault(a, []).append(r)
        common = [a for a in ho if len(ex.get(a, [])) >= 2]
        if len(common) < 5:
            res[c] = {"n": len(common), "pass": None}
            continue
        x = np.array([np.mean(ex[a]) for a in common])
        y = np.array([np.mean(ho[a]) for a in common])
        rho = spearmanr(x, y)[0]
        null = np.array([spearmanr(x, RNG.permutation(y))[0] for _ in range(nperm)])
        res[c] = {"n": len(common), "rho": float(rho), "p": float((1 + (null >= rho).sum()) / (nperm + 1)),
                  "pass": bool(rho > 0 and (1 + (null >= rho).sum()) / (nperm + 1) < 0.05)}
    return {"primary": res.get(col), "turns": res.get("newton_exc"), "pass": (res.get(col) or {}).get("pass")}


def c8_collective(out):
    """HH67: (a) Delta_MF and Delta_PW within the cross-day null in every regime-III period after Holm (null replication);
    (b) #51 tail PW excess / Sigma_1 < 0.3 (strong form fails); (c, low credence) Delta_MF above the null (p < 0.05) in
    >= 2 of 3 regime-I periods (exploration: one borderline p = 0.0495 in G27)."""
    import summarize as SU
    names = [n for n in _have(out, R3) if "delta_mf_p" in out[n][1].get("collective", {})]
    pm = SU.holm([out[n][1]["collective"]["delta_mf_p"] for n in names]) if names else []
    pp = SU.holm([out[n][1]["collective"]["delta_pw_p"] for n in names]) if names else []
    a = bool(all(x >= 0.05 for x in pm) and all(x >= 0.05 for x in pp)) if names else None
    t = out.get("G51tail", (None, {}, None))[1].get("collective", {})
    b = bool(t.get("ratio_delta_pw_exc_to_sigma1_cfx", np.inf) < 0.3) if t else None
    r1 = [out[n][1]["collective"].get("delta_mf_p", np.nan) for n in _have(out, R1) if "collective" in out[n][1]]
    c = bool(sum(x < 0.05 for x in r1) >= 2) if r1 else None
    return {"holm_mf": dict(zip(names, map(float, pm))), "holm_pw": dict(zip(names, map(float, pp))),
            "a_null_replicates": a, "b_strong_form_fails_tail": b, "regime_I_mf_p": r1, "c_regime_I_detected": c, "pass": a}


def c9_scaffold(out):
    """Removing consolidate loses >= 50% of the median coarse excess in >= 4 of 6 regime-III periods (exploration 0.52-1.00
    in 8/8): most coarse irreversibility is carried by the scaffold's consolidation boundary (rival R1)."""
    v = {n: out[n][1].get("P9_median_share_lost", np.nan) for n in _have(out, R3)}
    k = sum((x >= 0.5) for x in v.values() if np.isfinite(x))
    return {"values": v, "k": k, "pass": bool(k >= 4)}


CRITERIA = {"C1_fine_arrow": c1_fine_arrow, "C2_regime_contrast": c2_regime_contrast, "C3_small_coarse_arrow": c3_small_coarse_arrow,
            "C4_long_window": c4_long_window, "C5_current": c5_current, "C6_no_family_arrow": c6_no_family_arrow,
            "C7_agent_trait": c7_agent_trait, "C8_collective": c8_collective, "C9_scaffold": c9_scaffold}
VERDICT_RULE = ("Descriptive structure CONFIRMED if C1, C2, C5 and C9 all pass. HH19 (per-family arrow) stays refuted if C6 passes "
                "(weak, low power). Agent-level arrow CONFIRMED if C7 passes. HH67 weak form stays unsupported if C8(a) passes; "
                "C8(c) is low credence and reported only. C3 and C4 refine magnitudes; a failure of C3 or C4 is reported, not fatal.")


def card_hash():
    return hashlib.sha256(CARD.read_bytes()).hexdigest()[:16]


def days_for(spec, holdout: bool):
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet")
    c = cal.filter(pl.col("goal_no").is_in(spec["goals"]))
    if "from_" in spec:
        c = c.filter((pl.col("pt_date") >= spec["from_"]) & (pl.col("pt_date") < spec["to"]))
    hm = np.array(holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list()))
    if holdout:
        c = c.filter(pl.Series(hm))
        assert len(c) and hm.any(), "confirm period has no holdout days"
    else:
        c = c.filter(pl.Series(~hm))
        assert not any(holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())), "dry-run touched a holdout day"
    return c.sort("pt_date")


def run_all(holdout: bool, fast: bool):
    table = HOLDOUT if holdout else STAND_INS
    out_root = DATA / ("confirm" if holdout else "confirm_dryrun")
    out = {}
    for name, spec in table.items():
        cal_days = days_for(spec, holdout)
        if len(cal_days) < 2:
            print(f"skip {name}: {len(cal_days)} days")
            continue
        st, sm = build(cal_days["pt_date"].to_list())
        RP.PERIODS[name] = {"goals": spec["goals"]}
        df, res = RP.run(name, st, sm, cal_days, fast=fast, out_dir=out_root / name, fig_dir=out_root / name / "figures",
                         label="confirmatory" if holdout else "dry-run")
        out[name] = (df, res, spec)
    return out


def evaluate(out):
    """Evaluate CRITERIA on the per-period outputs. Returns {criterion: {value, pass}}."""
    ev = {}
    for k, fn in CRITERIA.items():
        try:
            ev[k] = fn(out)
        except Exception as e:  # report, don't hide
            ev[k] = {"error": repr(e), "pass": None}
    return ev


def main():
    holdout = "--confirm" in sys.argv
    dry = "--dry-run" in sys.argv
    if holdout and "--i-understand-this-uses-the-locked-holdout" not in sys.argv:
        raise SystemExit("Refusing: confirmatory runs need --confirm --i-understand-this-uses-the-locked-holdout.")
    if holdout and dry:
        raise SystemExit("Choose one of --confirm or --dry-run.")
    if not holdout and not dry:
        raise SystemExit("Nothing to do: pass --dry-run (non-holdout stand-ins) or the two confirm flags.")
    print(f"card hash {card_hash()} ({'CONFIRMATORY, LOCKED HOLDOUT' if holdout else 'dry run on non-holdout stand-ins'})")
    out = run_all(holdout, "--fast" in sys.argv)
    ev = evaluate(out)
    summary = {"mode": "confirm" if holdout else "dry-run", "card_hash": card_hash(), "criteria": ev, "verdict_rule": VERDICT_RULE}
    root = DATA / ("confirm" if holdout else "confirm_dryrun")
    root.mkdir(parents=True, exist_ok=True)
    (root / "confirm_results.json").write_text(json.dumps(summary, indent=1, default=float))
    print(json.dumps(summary, indent=1, default=float))


if __name__ == "__main__":
    main()
