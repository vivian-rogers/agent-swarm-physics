"""H39 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN ON ROUND-1B INPUTS. Written 2026-10-04; NOT RUN.

Re-freeze of `confirm.py` (left byte-for-byte untouched), written before any holdout access. Details in
`CONFIRM_R1B.md`. Inputs switched (round 1b, `scheme/build.py --r1b`, `run_period.py --data r1b`):
  * nudge target = the leading @ only (N_tgt); agents named second become N_oth (busy minutes, not episodes);
  * DQ8 lever_design presence cut (h39lib.LEVER["presence_cut"] = True): an episode needs one transition and its
    window is cut at the end of presence (round 1 conditioned on future presence);
  * second state space: Jev v3.1 behavior states lumped to V4 (work / coord / wait / maint; 5-min windows, soft
    transitions); new secondary criteria C1v-r1b, C2v-r1b, C6v-r1b score the nudge and erasure claims on V4;
  * receiving-call timing (DQ1 t_rc) reported as a sensitivity for kicks (not scored: the read-out call itself falls
    outside a post-kick window, Known issue 90).
Not changed: B4/B6 states come from H14's minute grid (never read `activity_bins`); content drift (C4) and kickoff steps
(C7) stay on bge, because no gte agent-window vectors exist (`embeddings/agent_win30_vec.npy` is bge only) and C7's
placebo pool is frozen on bge. This is disclosed as a deviation from the two-model rule.

Refuses to touch held-out days unless called with BOTH --confirm --i-understand-this-uses-the-locked-holdout, the H39
folder is committed and clean, and infra/shared/holdout_ledger.check() shows no same-family run of the same modality on
a target. `--dry-run` runs the identical code on non-holdout stand-ins (late #51, G38/G41/G42/G44, regime-III
kickoffs, a G38 day pair) and writes OUT/r1b/confirm_r1b_dryrun/ (or --out).

Holdout reuse (ledger L256-L269): #45 (H02 activity timing; H04 kick-response, activity timing), #46-#50 / NE21+NE23
(H04), #51 tail (planned by H08, H12, H18, H19, H29, H30, H34). H39's observables (matched-window stationary
decomposition of behavior-state transitions, content drift toward the kick message, kickoff steps) are different
statistics and modalities (ledger: behavior states / message content).

Predictions ("-r1b" = changed or new; reasons in CONFIRM_R1B.md):
| ID      | Target                   | Statement                                                                   | Primary |
| C1      | #45-#47, #49, #50 pooled | nudges (leading @, presence cut), B4: pooled K > 0, 95% CI excluding 0       | yes |
| C1v-r1b | same                     | nudges, V4: pooled K > 0, CI excluding 0 [1b +0.246 [0.17, 0.32]]           | no  |
| C2      | same                     | nudges, B4: pooled idle escape ln ratio > 0 and Delta pi_idle < 0 (CIs)     | no  |
| C2v-r1b | same                     | nudges, V4: wait escape ln ratio > 0 and Delta pi_wait < 0 (CIs)            | no  |
| C3      | #51 tail                 | @-mentions, B4: |K| < 0.10 and phi_exc < 0.10                              | yes |
| C4      | #51 tail                 | @-mentions and human messages: content drift toward the message > 0 (p<0.05) | yes |
| C5      | #51 tail                 | human messages, B4: |K| < 0.10 and phi_exc < 0.10                          | no  |
| C6      | #45-#47, #49, #50 pooled | forced erasure (A2 chain), B4: Delta pi_idle < 0 and Delta pi_work > 0       | yes |
| C6v-r1b | same                     | forced erasure, V4: Delta pi_wait < 0 and Delta pi_work > 0 [1b -0.21/+0.17] | no  |
| C7      | kickoffs #44->#45 ... #49->#50 | content phi above the frozen regime-III placebo p95 in >= 50%         | no  |
| C8      | NE23 (06-13 off vs 06-12 on)   | Delta pi_idle (off - on) > 0 (descriptive)                            | no  |
Overall (unchanged): supported if C1 and at least two of C3/C4/C6 pass; failed if C1 fails and at most one of
C3/C4/C6 passes; otherwise mixed. Power warning (unchanged): C1 may be underpowered on #45-#50.

Usage:
  uv run python hypotheses/H39-catalysts-vs-fields/analysis/confirm_r1b.py --dry-run [--out DIR]
  uv run python hypotheses/H39-catalysts-vs-fields/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2" if _v == "POLARS_MAX_THREADS" else "1"

import argparse  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import confirm as C0  # noqa: E402  (round-1 helpers: days_for, consolidation_kinds, HoldoutData, targets)
import h39lib as L  # noqa: E402
import run_period as RP  # noqa: E402
import run_steps as RS  # noqa: E402
import v3states as V3  # noqa: E402

SCHEME = C0.SCHEME
H14 = C0.H14
SH = C0.SH
HYP = "H39"
TARGETS, STANDINS = C0.TARGETS, C0.STANDINS
L.LEVER["presence_cut"] = True           # DQ8 lever_design (round 1b)
LEDGER_T = {"G45": None, "G46": None, "G47": None, "G48": None, "G49": None, "G50": None, "#51-tail": None, "NE21+NE23": None}


def kick_table_r1b(days: list[str], allow_holdout: bool) -> pl.DataFrame:
    """scheme/build.py: load_kick_table_r1b with the holdout guard of load_kick_table passed through."""
    k = SCHEME.load_kick_table(days, allow_holdout=allow_holdout)
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
    k = k.join(chat.with_columns(pl.col("msg").cast(pl.UInt32)), on="msg", how="left")
    nid = k.filter(pl.col("cls").cast(pl.Utf8) == "N_tgt")["message_id"].unique().to_list()
    lt = SCHEME.leading_targets(nid)
    k = k.with_columns(pl.col("message_id").replace_strict(lt, default=None, return_dtype=pl.Int64).alias("lead"))
    k = k.with_columns(pl.when((pl.col("cls").cast(pl.Utf8) == "N_tgt") & (pl.col("agent").cast(pl.Int64) != pl.col("lead").fill_null(-1)))
                       .then(pl.lit("N_oth")).otherwise(pl.col("cls").cast(pl.Utf8)).cast(pl.Categorical).alias("cls"))
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("message_id").is_in(k["message_id"].unique().implode()))
          .select("turn_id", "message_id").collect())
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("turn_id").is_in(it["turn_id"].implode()))
          .select("turn_id", pl.col("agent").cast(pl.Int8), pl.col("t_call").alias("t_rc"), pl.col("pt_date").alias("rc_date")).collect())
    it = it.join(cw, on="turn_id", how="inner").drop("turn_id")
    k = k.join(it, on=["message_id", "agent"], how="left")
    k = k.with_columns(pl.when(pl.col("rc_date") == pl.col("pt_date")).then(pl.col("t_rc")).otherwise(None).alias("t_rc"))
    return k.select("agent", "t", "pt_date", "cls", "msg", "emb", "t_rc").sort("agent", "t")


def allow_holdout_v3():
    """Confirm path only: v3states.load_v3 refuses holdout rows (exploration guard). Re-bind a copy without it."""
    def load_v3_h(days):
        b = pl.scan_parquet(V3.SH / "behavior_states_v3.parquet").filter(pl.col("pt_date").is_in(days)).collect()
        b = b.with_columns([pl.sum_horizontal([pl.col(f"p_{s}") for s in V3.LUMP[k]]).alias(k) for k in V3.V4_NAMES])
        b = b.with_columns([pl.when(pl.col("active") & pl.col("labeled")).then(pl.col(k))
                            .otherwise(pl.lit(1.0 if k == "wait" else 0.0)).alias(k) for k in V3.V4_NAMES])
        tot = pl.sum_horizontal([pl.col(k) for k in V3.V4_NAMES])
        b = b.with_columns([(pl.col(k) / tot).alias(k) for k in V3.V4_NAMES])
        return b.filter(pl.col("in_span")).select("pt_date", "agent", "w", "t0", "t1", *V3.V4_NAMES, "n_errors").sort("pt_date", "agent", "w")
    V3.load_v3 = load_v3_h


def point_unit(days, cal, allow_holdout, classes, erasure=False, B=300, P=200, v4=False, gno=0):
    _, states = H14.build(days, {})
    kicks = kick_table_r1b(days, allow_holdout)
    er = C0.consolidation_kinds(days, allow_holdout)
    seg = RP.load_period(days, cal, states=states, kicks=kicks, erasures=er if erasure else None, busy_only=("N_oth",))
    out = {"n_agent_days": len(seg["b6"]), "days": days}
    U4 = RP.make_units(seg)
    for c in classes:
        out[c] = L.run_point(U4, c, B=B, P=P, seed=L.SEED + 4040)
    if erasure:
        Ue = RP.make_units(seg, erasure=True)
        pool = L.control_pool(Ue, L.W_DEFAULT, quiet=10)
        g, s0, ab = RP.erasure_episodes(Ue, "CF", L.W_DEFAULT, 10, 3)
        out["CF_b4_nocons"] = L.run_point(Ue, "CF", B=B, P=P, seed=L.SEED + 4041, g_override=g, s0_override=s0,
                                          age_override=ab, pool_mask=pool, quiet=10, keep_states=[0, 1, 2])
    # receiving-call timing sensitivity (reported)
    seg_rc = RP.load_period(days, cal, states=states, kicks=kicks, busy_only=("N_oth",), time_col="t_rc")
    U4rc = RP.make_units(seg_rc)
    out["sens_rc"] = {c: {k: v for k, v in L.run_point(U4rc, c, B=max(B // 2, 50), P=max(P // 2, 50), seed=L.SEED + 4043).items()
                          if k in ("n_ep", "K", "K_ci", "phi_exc", "dpi", "esc", "status")} for c in classes}
    if v4:
        out["v4"] = V3.run_v3(days, cal, kicks, er, "III", gno, B=B, P=P, classes=classes)
    return out, seg, U4


def pooled(units, state_idx_esc, state_idx_dpi):
    nu = [u for u in units if u.get("n_ep", 0) >= 10 and "K_boot_se" in u]
    if not nu:
        return None
    mk = L.dl_meta([u["K"] for u in nu], [u["K_boot_se"] for u in nu])
    me = L.dl_meta([u["esc"][state_idx_esc] for u in nu], [u["esc_boot_se"][state_idx_esc] for u in nu])
    md = L.dl_meta([u["dpi"][state_idx_dpi] for u in nu], [u["dpi_boot_se"][state_idx_dpi] for u in nu])
    return dict(K=mk, esc=me, dpi=md, n_ep=int(sum(u["n_ep"] for u in nu)))


def pooled_erasure(units, i_idle, i_work):
    pw = [u for u in units if u and u.get("status") == "ok" and "dpi_boot_se" in u]
    if not pw:
        return None
    mi = L.dl_meta([u["dpi"][i_idle] for u in pw], [u["dpi_boot_se"][i_idle] for u in pw])
    mw = L.dl_meta([u["dpi"][i_work] for u in pw], [u["dpi_boot_se"][i_work] for u in pw])
    return dict(idle=mi, work=mw)


def ledger_gate(strict: bool) -> list[str]:
    sys.path.insert(0, str(L.ROOT))
    from infra.shared import holdout_ledger as hl
    led = hl.load()
    bad = []
    for t in LEDGER_T:
        for e in [e for e in led["entries"] if e["hypothesis"] == HYP and e["target"] == t] or [None]:
            mod = e["modality"] if e else "behavior states"
            fam = e["estimator_family"] if e else ["kick_response"]
            r = hl.check(HYP, t, mod, fam)
            same_mod = sorted({u["hypothesis"] for u in r["prior_runs_same_family"] if u["modality"] == mod})
            print(f"ledger {t} [{mod}]: allowed={r['allowed']} same_family_same_modality_runs={same_mod} "
                  f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})}", flush=True)
            if same_mod:
                bad.append(f"{t} {mod}: {same_mod}")
    return bad if strict else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", type=Path, default=None, help="dry-run output directory")
    a = ap.parse_args()
    if a.dry_run and (a.confirm or a.ack):
        sys.exit("Choose exactly one: --dry-run, or --confirm --i-understand-this-uses-the-locked-holdout.")
    if not a.dry_run and not (a.confirm and a.ack):
        sys.exit("Refusing: a real (holdout) run needs BOTH --confirm and --i-understand-this-uses-the-locked-holdout. "
                 "Use --dry-run for the non-holdout stand-ins.")
    real = not a.dry_run
    if real:
        dirty = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", "hypotheses/H39-catalysts-vs-fields"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("Refusing: commit the H39 card, confirm_r1b.py and CONFIRM_R1B.md before the holdout run.")
    bad = ledger_gate(strict=real)
    if bad:
        sys.exit("Refusing (holdout ledger, same family and modality): " + "; ".join(bad))
    if real:
        allow_holdout_v3()
    T = TARGETS if real else STANDINS
    outdir = L.OUT / "r1b" / "confirm_r1b" if real else (a.out or L.OUT / "r1b" / "confirm_r1b_dryrun")
    t0 = time.time()
    cal = pl.read_parquet(SH / "calendar.parquet")
    res = {"mode": "CONFIRMATORY r1b (holdout)" if real else "dry run r1b on non-holdout stand-ins (not evidence)", "targets": {}}
    C = {}
    # ---- #51 tail: mentions, human messages, content drift (nudges descriptive)
    d51 = C0.days_for(cal, goal=T["tail51"]["goal"], date_from=T["tail51"]["date_from"], date_to=T["tail51"]["date_to"], allow_holdout=real)
    u51, seg51, U51 = point_unit(d51, cal, real, ("N_tgt", "A_men", "H_any"))
    u51["content"] = RP.content_drift(seg51, d51, cal, "III", ("A_men", "H_any"), U51, L.W_DEFAULT, np.random.default_rng(L.SEED), B=300, P=100)
    res["targets"]["tail51"] = u51
    m = u51["A_men"]
    C["C3"] = bool("K" in m and abs(m["K"]) < 0.10 and m["phi_exc"] < 0.10)
    cd = u51["content"]
    C["C4"] = bool(all(isinstance(cd.get(c), dict) and cd[c].get("field_c", -1) > 0 and cd[c].get("p_field_c", 1) < 0.05 for c in ("A_men", "H_any")))
    h = u51["H_any"]
    C["C5"] = bool("K" in h and abs(h["K"]) < 0.10 and h["phi_exc"] < 0.10)
    print("tail51 done", f"{time.time() - t0:.0f}s", flush=True)
    # ---- 4-h regime-III periods: nudges and erasure, B4 and V4
    er_b4, er_v4, nud_b4, nud_v4 = [], [], [], []
    for g in T["erasure"]["goals"]:
        dg = C0.days_for(cal, goal=g, allow_holdout=real)
        if not dg:
            continue
        ue, _, _ = point_unit(dg, cal, real, ("N_tgt",), erasure=True, B=300, P=100, v4=True, gno=g)
        er_b4.append(ue["CF_b4_nocons"]); nud_b4.append(ue["N_tgt"])
        v4 = ue.get("v4", {})
        nud_v4.append(v4.get("N_tgt", {})); er_v4.append(v4.get("erasure_CF", {}))
        res["targets"].setdefault("periods", {})[f"G{g:02d}"] = {"erasure_b4": ue["CF_b4_nocons"], "nudges_b4": ue["N_tgt"],
                                                                 "sens_rc": ue["sens_rc"], "v4_nudges": v4.get("N_tgt"),
                                                                 "v4_erasure_CF": v4.get("erasure_CF")}
        print(f"G{g:02d} done", f"{time.time() - t0:.0f}s", flush=True)
    pb = pooled(nud_b4, 2, 2)            # B4 states: 2 = idle
    pv = pooled(nud_v4, 2, 2)            # V4 states: [work, coord, wait, maint], 2 = wait
    res["targets"]["nudges_pooled_b4"], res["targets"]["nudges_pooled_v4"] = pb, pv
    C["C1"] = bool(pb and pb["K"]["ci"][0] > 0)
    C["C2"] = bool(pb and pb["esc"]["ci"][0] > 0 and pb["dpi"]["ci"][1] < 0)
    C["C1v-r1b"] = bool(pv and pv["K"]["ci"][0] > 0)
    C["C2v-r1b"] = bool(pv and pv["esc"]["ci"][0] > 0 and pv["dpi"]["ci"][1] < 0)
    eb = pooled_erasure(er_b4, 2, 0)      # B4 A2 chain [work, chat, idle]
    ev = pooled_erasure(er_v4, 2, 0)      # V4 [work, coord, wait, maint]
    res["targets"]["erasure_pooled_b4"], res["targets"]["erasure_pooled_v4"] = eb, ev
    C["C6"] = bool(eb and eb["idle"]["ci"][1] < 0 and eb["work"]["ci"][0] > 0)
    C["C6v-r1b"] = bool(ev and ev["idle"]["ci"][1] < 0 and ev["work"]["ci"][0] > 0)
    # ---- kickoffs: content field vs the frozen round-1 regime-III placebo pool (bge)
    frozen = json.loads((L.OUT / "steps" / "steps_results.json").read_text())["placebo"]["2x2"]
    pool = [p for p in frozen if p["era"] == "III-4h" and "c6" in p and "phi" in p["c6"]]
    kres = []
    for g0, g1 in T["kickoffs"]:
        pre = C0.days_for(cal, goal=g0, allow_holdout=real)[-2:]
        post = C0.days_for(cal, goal=g1, allow_holdout=real)[:2]
        if not pre or not post:
            continue
        D = C0.HoldoutData(pre + post, real)
        r = RS.compare(D, pre, post, 300)
        if "c6" in r:
            r["judge_c6"] = L.judge_step(r["c6"], [p["c6"] for p in pool])
        kres.append(dict(id=f"K{g0:02d}-{g1:02d}", pre=pre, post=post, b4=r.get("b4"), c6=r.get("c6"), judge_c6=r.get("judge_c6")))
    res["targets"]["kickoffs"] = kres
    jk = [k["judge_c6"] for k in kres if k.get("judge_c6") and "phi_p95" in k["judge_c6"]]
    C["C7"] = bool(jk and np.mean([j["phi_pct"] >= 95 for j in jk]) >= 0.5)
    # ---- NE23 step (descriptive)
    off, on = T["ne23"]["off"], T["ne23"]["on"]
    D = C0.HoldoutData(on + off, real)
    r = RS.compare(D, on, off, 300, content=False)
    res["targets"]["ne23"] = r
    C["C8"] = bool(r.get("b4") and r["b4"]["dpi"][2] > 0)
    sec = sum(C[k] for k in ("C3", "C4", "C6"))
    overall = "supported" if C["C1"] and sec >= 2 else ("failed" if (not C["C1"] and sec <= 1) else "mixed")
    res["predictions"], res["overall"], res["runtime_s"] = C, overall, time.time() - t0
    outdir.mkdir(parents=True, exist_ok=True)
    L.jdump(res, outdir / "confirm_r1b_results.json")
    print(json.dumps({"mode": res["mode"], "predictions": C, "overall": overall}, indent=1))


if __name__ == "__main__":
    main()
