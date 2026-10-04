"""H31 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN ON ROUND-1B INPUTS (written 2026-10-04; NOT RUN).

Re-freeze of `confirm_holdout.py` (left byte-for-byte untouched, as is `frozen_rule.json`; holdout.md ledger item 17).
Written before any holdout data was read. Details and reasons: `CONFIRM_R1B.md`.

What changed vs confirm_holdout.py ("pipeline identical to round 1")
  * Visibility and timing: DQ1 context ledger (`context_ledger_items`, `call_windows`): a read is (message, recipient,
    receiving call); t_seen = the receiving call's t_call, t_upd = its first record (scheme/build.py
    `--visibility ledger`, the round-1b build). Round 1 used H18's call-start rule.
  * Project states: shared deterministic `project_states` (w_min 30, sources "all"; label ranking on non-holdout rows
    where a period has any, else all rows), not H11's nondeterministic `modal()` labels rebuilt by H11's code.
  * Content (E-C): alignment from DQ5 white32 agent-window vectors under BOTH models (bge-small, gte-modernbert);
    the round-1 bge construction is reported alongside. E-C claims must hold under both models.
  * Frozen rule: the round-1b exploratory rule (`data/processed/H31-consensus-time-spectral-gap/r1b/frozen_rule.json`,
    values copied into FROZEN_R1B below; sha recorded). Its forecast-protocol choice changed from the constant (M0) to
    the reading-rate x random-walk gap rule M_ul2_rw (LOPO log-RMSE 1.049 vs 1.075).
  * Not inputs: activity_bins, outages, failures, work ledger (the work-space E-P is exploratory only), leading-@
    (lambda2^ment uses `mentions_roster` and is not in any criterion).
  * Guards added: holdout-ledger gate (blocks a target with a same-family, same-modality prior run; none found).

Targets (unchanged): E-P #29, #46, #47, #50; E-C #29, #46, #47, #49, #50.
Predictions ("-r1b" = changed):
  C1-r1b   On target uncensored E-P events, log tau = 4.625 - log lambda2^w,sym (slope-1 rule, intercept re-fitted on
           round-1b events) has lower log-RMSE than the constant log tau = 1.274. Credence 0.25. Reason: intercepts
           re-calibrated on ledger visibility and shared labels.
  C1b-r1b  (post hoc) free slope: log tau = 2.534 + 0.376 log(1/lambda2) beats the constant. Credence 0.45.
  C2-r1b   >= 70% of target uncensored E-P events fall inside the CHOSEN rule's 80% interval; the chosen rule is now
           M_ul2_rw: log tau = 4.654 - log(u lambda2^rw), residual (pred - y) interval [-1.097, 1.527]. Credence 0.5 (LOPO margin over M0 only 2.4%).
           Reason: the frozen protocol picks M_ul2_rw on round-1b data.
  C2b-r1b  (new, follows from C2-r1b) the chosen M_ul2_rw rule has lower log-RMSE than the constant. Credence 0.5.
           Reported, decides nothing: the constant rule's 80%-interval coverage (the round-1 protocol choice).
  C3-r1b   Content never converges: at most 1 E-C convergence event over all target blocks under EACH model (bge, gte).
           Credence 0.7. Reason: round 1 froze no content rule, so the original C3 was always n/a; round 1 and 1b found
           0/35 convergence blocks and 12 divergences.
  C4       (descriptive) sign of the slope of log tau on log(1/lambda2) across target events; event counts.
  H31 is CONFIRMED only if C1-r1b passes; the forecast rule is CONFIRMED if C2-r1b passes.

Reuse (hypotheses/holdout.md; ledger L188-L196): #46-#50 lie in NE21+NE23, used by H04 (activity timing; another
modality). Planned same-family users: H27 (project_potts; #29, #46, #47, #50), H01 (#46, #47, #50); content users
H12, H13, H26, H33, H36 ... on the E-C targets. Disclose in both cards and LOG.md.

Guard: refuses without --confirm --i-understand-this-uses-the-locked-holdout; refuses unless this script and the card
are committed unmodified. --dry-run builds non-holdout stand-ins (E-P #30, #41, #42, #44; E-C + #39) through the same
in-memory path into data/processed/H31-consensus-time-spectral-gap/confirm_r1b_dryrun/ and checks that its labels equal
H11's round-1b label files and its event counts equal the round-1b exploration.

  uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/confirm_r1b.py --dry-run
  uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ["H31_STATE"] = "project"
import argparse  # noqa: E402
import hashlib  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h31lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import holdout_ledger as HL  # noqa: E402

HYP = "H31"
SH = L.ROOT / "data/processed/shared"
TARGETS_EP = [29, 46, 47, 50]
TARGETS_EC = [29, 46, 47, 49, 50]
STANDINS_EP = [30, 41, 42, 44]
STANDINS_EC = [30, 41, 42, 44, 39]
OUT_DRY = L.ROOT / "data/processed/H31-consensus-time-spectral-gap/confirm_r1b_dryrun"
OUT_CONF = L.ROOT / "data/processed/H31-consensus-time-spectral-gap/confirm_r1b"
R1B_RULE_FILE = L.ROOT / "data/processed/H31-consensus-time-spectral-gap/r1b/frozen_rule.json"
FROZEN_R1B = {  # copied from R1B_RULE_FILE (round-1b exploration, non-holdout only), 2026-10-04
    "chosen": "M_ul2_rw", "predictor": "ul2_rw", "log_c": 4.654376251881274,
    "lopo_resid_q10_q90": [-1.0971505464746272, 1.5271845714973056],
    "constant_rule": {"log_c": 1.274014907619095, "lopo_resid_q10_q90": [-1.27490554727388, 1.3291895166104843]},
    "lambda_rule": {"log_c": 4.625143402308066},
    "lambda_free_rule_posthoc": {"log_c": 2.5337588737640018, "b": 0.3759163422534853},
    "n_events": 31, "n_periods": 13,
    "C3_max_convergence_per_model": 1,
}
SIGN = {"l2_sym": -1, "g_tr": -1, "tau_V": 1, "tau_wave": 1, "ul2_rw": -1, "l2_sym_core": -1}
VEC = {"bge": "agent_win30_white32_bge_small.npy", "gte": "agent_win30_white32_gte_modernbert.npy"}
LEDGER = [("project labels", ["project_potts"], TARGETS_EP), ("message content", ["content_alignment"], TARGETS_EC)]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def committed_or_die():
    for p in (Path(__file__).resolve(), L.HYP / "README.md"):
        r = subprocess.run(["git", "-C", str(L.ROOT), "ls-files", "--error-unmatch", str(p)], capture_output=True)
        d = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", str(p)], capture_output=True, text=True).stdout
        if r.returncode != 0 or d.strip():
            raise SystemExit(f"refusing (holdout reuse policy): commit {p} unmodified before the confirmatory run")


def ledger_gate():
    rep, bad = {}, []
    for mod, fam, goals in LEDGER:
        for g in goals:
            t = f"G{g:02d}"
            r = HL.check(HYP, t, mod, fam)
            same = sorted({x["hypothesis"] for x in r["prior_runs_same_family"] if x["modality"] == mod})
            rep[f"{t} [{mod}]"] = {"allowed": r["allowed"], "same_family_same_modality_runs": same,
                                   "prior_runs": sorted({x["hypothesis"] for x in r["prior_runs"]}),
                                   "competing_planned": sorted({x["hypothesis"] for x in r["competing_planned"]})}
            if same:
                bad.append(f"{t} [{mod}]")
    return rep, bad


def shared_states(g: int, cal: pl.DataFrame, allow_holdout: bool) -> pl.DataFrame:
    """Shared deterministic project states (W = 30, sources all) for goal g, mapped to the build's day index."""
    ps = pl.scan_parquet(SH / "project_states.parquet").filter(
        (pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all") & (pl.col("goal_no") == g))
    if not allow_holdout:
        ps = ps.filter(~pl.col("holdout"))
    ps = ps.collect()
    return (ps.drop("day").join(cal.select("pt_date", "day"), on="pt_date", how="inner")
            .select("pt_date", "day", "win", "agent", "room", "label", pl.col("project").cast(pl.String)))


def alignment_model(S, sh, g, cal, model):
    """S.alignment_period with DQ5 white32 vectors of `model` (already whitened; unit-normalized here)."""
    grid = S.window_grid(cal)
    ros = sh.roster.filter(~pl.col("claude_code"))
    ra = S.rooms_at(sh, [int(a) for a in ros["agent"].to_list()], S._us(grid["t_mid"]))
    aw = pl.read_parquet(SH / "embeddings/agent_win30.parquet").filter(
        (pl.col("goal_no") == g) & pl.col("pt_date").is_in(cal["pt_date"].to_list()) & (pl.col("n_chat") + pl.col("n_intent") > 0))
    if aw.height == 0:
        return None
    vec = np.load(SH / "embeddings" / VEC[model], mmap_mode="r")
    aw = aw.join(cal.select("pt_date", "day"), on="pt_date")
    Z = np.asarray(vec[aw["gid"].to_numpy()], dtype=np.float32)
    Z /= np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-9)
    key = {(d, w): i for i, (d, w) in enumerate(zip(grid["day"].to_list(), grid["win"].to_list()))}
    days, wins, ags = aw["day"].to_numpy(), aw["win30"].to_numpy(), aw["agent"].to_numpy()
    room = np.full(len(days), -1, np.int16)
    for i in range(len(days)):
        k = key.get((int(days[i]), int(wins[i])))
        if k is not None and int(ags[i]) in ra:
            room[i] = ra[int(ags[i])][k]
    df = pl.DataFrame({"day": days, "win": wins, "agent": ags, "room": room, "i": np.arange(len(days))})
    rows = []
    for (d, w, r), sub in df.filter(pl.col("room") >= 0).group_by(["day", "win", "room"]):
        idx = sub["i"].to_numpy()
        n = len(idx)
        if n < 2:
            continue
        Cm = Z[idx] @ Z[idx].T
        rows.append({"day": int(d), "win": int(w), "room": int(r), "n_agents": n,
                     "A": float((Cm.sum() - np.trace(Cm)) / (n * (n - 1)))})
    if not rows:
        return None
    return pl.DataFrame(rows).join(grid.select("day", "win", "act_mid"), on=["day", "win"], how="left").sort("room", "day", "win")


def build(goals, out: Path, allow_holdout: bool) -> dict:
    """Round-1b build (ledger visibility, shared labels) of the given goals into out/, plus per-model alignment."""
    S = _load("h31_scheme_build", L.HYP / "scheme/build.py")
    sh = S.Shared()
    checks = {}
    for g in goals:
        res = S.build_period(sh, g, allow_holdout=allow_holdout, verbose=not allow_holdout, visibility="ledger",
                             labels="shared")
        if res is None:
            continue
        cal_full = S.period_days(sh, g, allow_holdout)
        lab = shared_states(g, res["cal"], allow_holdout)
        if not allow_holdout and 30 in res["states"]:   # reproduction: shared labels == H11 round-1b label files
            ref = res["states"][30].sort("pt_date", "win", "agent")
            mine = lab.sort("pt_date", "win", "agent")
            checks[f"G{g:02d}_labels_equal_h11_r1b"] = bool(ref.select("pt_date", "win", "agent", "label").equals(
                mine.select("pt_date", "win", "agent", "label")))
        res["states"] = {30: lab}
        S.write_period(g, res, out)
        for m in VEC:
            al = alignment_model(S, sh, g, cal_full, m)
            if al is not None:
                al.write_parquet(out / f"G{g:02d}" / f"alignment_{m}.parquet", compression="zstd")
    return checks


def evaluate(goals_ep, goals_ec, root: Path, rule: dict) -> dict:
    from explore import label_matrix
    from predictors import block_predictors
    ev, ec = [], []
    for g in sorted(set(goals_ep) | set(goals_ec)):
        P = L.load_period(g, root)
        if P["days"] is None:
            continue
        al = {"bge_r1": P["alignment"]}
        for m in VEC:
            f = root / f"G{g:02d}" / f"alignment_{m}.parquet"
            al[m] = pl.read_parquet(f) if f.exists() else None
        for b in L.blocks_of(P):
            pr = block_predictors(P, b, with_voter=True)
            if pr is None:
                continue
            if g in goals_ep and P["states30"] is not None:
                lab, act_h, Nb, _ = label_matrix(P, b, 30)
                for e in L.detect_project_events(lab, act_h, Nb):
                    if e["consensus"]:
                        ev.append(dict(goal_no=g, room=b, frozen=e["frozen"], tau_h=e["tau_h"], **pr))
            if g in goals_ec:
                row = dict(goal_no=g, room=b)
                for m, a in al.items():
                    row[m] = L.detect_content_event(a, b, L.period_T(P) / 3600).get("kind") if a is not None else "n/a"
                ec.append(row)
    out = {"n_consensus": len(ev)}
    ev = pl.DataFrame(ev) if ev else pl.DataFrame()
    if ev.height:
        unc = ev.filter(~pl.col("frozen"))
        out["n_uncensored"], out["n_frozen"] = unc.height, ev.height - unc.height
        if unc.height:
            y = np.log(unc["tau_h"].to_numpy())
            l2 = unc["l2_sym"].to_numpy()
            p0 = np.full(len(y), rule["constant_rule"]["log_c"])
            r0 = L.rmse(y, p0)
            p_lam = rule["lambda_rule"]["log_c"] - np.log(l2)
            out["C1-r1b"] = dict(rmse_lambda=L.rmse(y, p_lam), rmse_const=r0, verdict="PASS" if L.rmse(y, p_lam) < r0 else "FAIL")
            fr = rule["lambda_free_rule_posthoc"]
            p_f = fr["log_c"] + fr["b"] * (-np.log(l2))
            out["C1b-r1b"] = dict(rmse_free=L.rmse(y, p_f), rmse_const=r0, verdict="PASS" if L.rmse(y, p_f) < r0 else "FAIL")
            p = rule["predictor"]
            pc = rule["log_c"] + SIGN[p] * np.log(np.maximum(unc[p].to_numpy(), 1e-6))
            lo, hi = rule["lopo_resid_q10_q90"]
            inside = ((pc - y) >= lo) & ((pc - y) <= hi)
            out["C2-r1b"] = dict(rule=rule["chosen"], frac_inside_80=float(inside.mean()),
                                 verdict="PASS" if inside.mean() >= 0.7 else "FAIL")
            out["C2b-r1b"] = dict(rmse_chosen=L.rmse(y, pc), rmse_const=r0, verdict="PASS" if L.rmse(y, pc) < r0 else "FAIL")
            lo0, hi0 = rule["constant_rule"]["lopo_resid_q10_q90"]   # reported only: the round-1 choice (constant)
            in0 = ((p0 - y) >= lo0) & ((p0 - y) <= hi0)
            out["C2c_reported_constant"] = dict(frac_inside_80=float(in0.mean()), decides="nothing")
            if unc.height >= 3 and np.ptp(np.log(l2)) > 0:
                out["C4_slope"] = float(L.ols(-np.log(l2), y)[1])
    ecd = pl.DataFrame(ec) if ec else pl.DataFrame()
    if ecd.height:
        kinds = {m: {k: int(v) for k, v in zip(*np.unique(ecd[m].to_numpy().astype(str), return_counts=True))}
                 for m in ("bge_r1", *VEC)}
        nconv = {m: kinds[m].get("convergence", 0) for m in VEC}
        out["ec_kinds"] = kinds
        out["C3-r1b"] = dict(n_blocks=ecd.height, n_convergence=nconv,
                             verdict="PASS" if all(v <= rule["C3_max_convergence_per_model"] for v in nconv.values()) else "FAIL")
    else:
        out["C3-r1b"] = dict(verdict="n/a (no E-C blocks)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    rule = FROZEN_R1B
    src_sha = hashlib.sha256(R1B_RULE_FILE.read_bytes()).hexdigest()[:16] if R1B_RULE_FILE.exists() else None
    src = json.loads(R1B_RULE_FILE.read_text()) if R1B_RULE_FILE.exists() else {}
    drift = [k for k in ("chosen", "log_c") if src and src.get(k) != rule[k]]
    gate, bad = ledger_gate()
    held = set(json.loads((L.ROOT / "hypotheses/holdout.json").read_text())["goal_periods_held_out"])
    t0 = time.time()
    if a.dry_run and not (a.confirm or a.ack):
        assert not (set(STANDINS_EP + STANDINS_EC) & held), "stand-ins must be non-holdout"
        print(f"DRY RUN r1b on non-holdout stand-ins (E-P {STANDINS_EP}, E-C {STANDINS_EC}); r1b rule file sha {src_sha}; "
              f"embedded-rule drift {drift or 'none'}", flush=True)
        checks = build(sorted(set(STANDINS_EP + STANDINS_EC)), OUT_DRY, allow_holdout=False)
        res = evaluate(STANDINS_EP, STANDINS_EC, OUT_DRY, rule)
        ref = pl.read_parquet(L.ROOT / "data/processed/H31-consensus-time-spectral-gap/r1b/events_ep_w30.parquet").filter(
            pl.col("goal_no").is_in(STANDINS_EP) & pl.col("consensus"))
        checks["events_r1b_exploration"] = {"n_consensus": ref.height, "n_frozen": int(ref["frozen"].sum())}
        checks["events_this_build"] = {"n_consensus": res.get("n_consensus"), "n_frozen": res.get("n_frozen")}
        res.update({"checks": checks, "ledger": gate, "ledger_blocked": bad, "rule_source_sha": src_sha,
                    "secs": round(time.time() - t0, 1)})
        OUT_DRY.mkdir(parents=True, exist_ok=True)
        (OUT_DRY / "confirm_r1b_dryrun.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps(res, indent=1, default=float))
        print("NOTE: stand-ins were explored in rounds 1 and 1b, so this checks the code path only.")
        return
    if not (a.confirm and a.ack) or a.dry_run:
        raise SystemExit("refusing: the confirmatory run uses the locked holdout. Pass --confirm "
                         "--i-understand-this-uses-the-locked-holdout (after Vivian's sign-off), or --dry-run.")
    committed_or_die()
    if bad:
        raise SystemExit(f"refusing: same-family same-modality prior run on {bad} (holdout ledger); needs Vivian's ruling")
    assert set(TARGETS_EP + TARGETS_EC) <= held, "targets must be held-out periods"
    print("DISCLOSURE (paste into the H31, H04 and H27 cards and LOG.md): H31 r1b confirmatory run uses held-out periods "
          f"{sorted(set(TARGETS_EP + TARGETS_EC))}; #46-#50 lie in NE21+NE23 (H04, activity timing). H31 computes "
          f"consensus-event timing from shared project states and content alignment (bge + gte). Rule sha {src_sha}.")
    print("Ledger gate:", json.dumps(gate, indent=1))
    OUT_CONF.mkdir(parents=True, exist_ok=True)
    build(sorted(set(TARGETS_EP + TARGETS_EC)), OUT_CONF, allow_holdout=True)
    res = evaluate(TARGETS_EP, TARGETS_EC, OUT_CONF, rule)
    res.update({"rule": rule, "rule_source_sha": src_sha, "ledger": gate})
    (OUT_CONF / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
