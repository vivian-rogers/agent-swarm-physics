"""H30 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN ON ROUND-1B INPUTS (written 2026-10-04; NOT RUN).

Re-freeze of `confirm.py` (left byte-for-byte untouched), written before any holdout data was read. Details and reasons
in `CONFIRM_R1B.md`. Inputs switched (round 1b, `--data r1b` paths of scheme/build.py and analysis/run_period.py):
  * activity: `activity_bins_fixed` (outage masks recomputed from it) instead of `activity_bins`;
  * nudge target: the leading @ only (shared `kicks_classified` + h30lib.leading_targets); named-second agents are
    bystanders;
  * kick time and recipients: the recipient's receiving call (DQ1 `context_ledger_items` -> `call_windows.t_call`);
  * design: strata through m - 1 plus a call-at-m indicator, past-only kick adjustment (no future-kick regressors,
    DQ8 lever_design), DAY FIXED EFFECT primary for levels (round 1 used the no-FE model);
  * content: pre/post windows at the receiving call, bge-small and gte-modernbert; content criteria pass only if they
    pass under both models.
Outcome stays active minutes (H30 measures attention response, not work; see infra/README.md Known issue 83).

Targets and reuse (hypotheses/holdout.md; ledger L179-L187):
  T1  #51 tail (2026-09-07 -> 09-21): primary for content. The nudger is silent after 2026-08-20 (NE43; found on
      non-holdout days), so every nudge criterion on T1 is expected n/a; the code handles zero nudges (dry-run stand-in
      T1z: non-holdout #51 days 2026-08-24 -> 09-04, after the nudger stopped).
  T2  #45: CONTENT by default. H04 ran nudge -> activity responses (kick_response family, activity timing) on #45 and
      #46-#50, so H30's activity statistics there are a same-family, same-modality second use (policy item 2).
      `--include-g45-activity` re-enables C45-1-r1b and #45's share of C-act-r1b; use it only on Vivian's written
      override (LOG.md). Without it, C-act-r1b is untestable on the holdout.
  T3  #46-#50: CONTENT ONLY (unchanged).
Refuses to run on the holdout without BOTH --confirm and --i-understand-this-uses-the-locked-holdout, refuses if the H30
folder has uncommitted changes, and refuses if infra/shared/holdout_ledger.check() finds a same-family prior run of the
SAME modality on a target it will compute (a same-family run in another modality is disclosed, not blocking).
--dry-run runs the identical code on non-holdout stand-ins (T1: #51 2026-08-07 -> 08-21; T1z: #51 08-24 -> 09-04;
T2: #44; T3: #41 and #42), with #44 activity included to exercise that path.

Predictions (C-*). Day-block bootstrap 95% CIs (1000 draws). "-r1b" marks a changed criterion.
  C-act-r1b (primary, activity) random-effects pooled chi_act(N_tgt), DAY-FE model, over activity-eligible targets
                    (T1 if >= 30 N_tgt kicks; T2 only with --include-g45-activity): > 0, CI excluding 0.
                    [round 1b: G51 0.98 [0.63, 1.37]; G38 0.95 [0.38, 1.54]] (was: no-FE model; reason: round 1b makes
                    day FE primary for levels; with past-only controls FE and no-FE agree, 0.98 vs 1.07)
  C51-1-r1b (secondary, conditional) chi_act(N_tgt), day FE, on T1 > 0 with CI excluding 0 (n/a if < 30 kicks).
  C51-2-r1b (primary)  chi_con(H_und), orthogonalized: > 0 with CI excluding 0 under BOTH models.
                    [round 1b pooled 0.024 bge / 0.024 gte] (was: bge only; reason: DQ5 both-model rule)
  C51-3 (secondary)    first-nudge chi_act (day FE) > repeat-nudge chi_act (day FE): point difference > 0.
                    [round 1b 1.21 vs 0.44] (unchanged)
  C51-4-r1b (secondary) bystander chi_act(N_by), day FE: |point| <= 0.3. [round 1b -0.01] (was: no-FE model)
  C51-5 (secondary)    daily chi_act(N_tgt): message-permutation p >= 0.05 or R1 < 0.5, and lag-1 p >= 0.05.
                    [round 1b G51: p 0.026, R1 0.48, lag-1 p 0.22 -> passes by R1] (unchanged)
  C51-6-r1b (secondary) chi_con(N_tgt): |point| < 0.02 under both models. [round 1b 0.002]
  C45-1-r1b (secondary, needs --include-g45-activity) chi_act(N_tgt), day FE, point > 0.
  C45-2-r1b (secondary) chi_con(H_und) point > 0 under both models.
  C4650-1-r1b (primary for T3) random-effects pooled chi_con over human recipients (H_und + H_men) across #46-#50:
                    > 0 with CI excluding 0 under both models. [round 1b pooled H_und 0.024, H_men 0.041]
  C4650-2-r1b (secondary) pooled chi_con(N_tgt) across #46-#50: |point| < 0.02 under both models.
Overall: supported if every testable primary passes; failed if no testable primary passes; mixed otherwise.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h30lib import *  # noqa: E402,F403
import h30lib  # noqa: E402
import run_period as RP  # noqa: E402
import build as B  # noqa: E402

FLAGS = ("--confirm", "--i-understand-this-uses-the-locked-holdout")
DATA = "r1b"
HYP = "H30"
MODELS = {"bge": "content.parquet", "gte": "content_gte.parquet"}


def holdout_days_of(goal: int, start: str | None = None, end: str | None = None) -> list[str]:
    c = calendar().filter((pl.col("goal_no") == goal) & (pl.col("window_s") > 0))
    if start:
        c = c.filter(pl.col("pt_date") >= start)
    if end:
        c = c.filter(pl.col("pt_date") < end)
    return sorted(c["pt_date"].to_list())


def targets(mode: str) -> dict:
    if mode == "confirm":
        return {"T1": [("G51", "G51", holdout_days_of(51, "2026-09-07", "2026-09-21"))],
                "T2": ("G45", holdout_days_of(45)),
                "T3": [(f"G{g}", holdout_days_of(g)) for g in (46, 47, 48, 49, 50)]}
    g51 = [d for d in period_days(51) if "2026-08-07" <= d < "2026-08-21"]   # last 10 non-holdout days with nudges
    g51z = [d for d in period_days(51) if "2026-08-24" <= d < "2026-09-05"]  # non-holdout, nudger silent (tail-like)
    return {"T1": [("G51", "G51", g51), ("G51z", "G51", g51z)], "T2": ("G44", period_days(44)),
            "T3": [("G41", period_days(41)), ("G42", period_days(42))]}


def fval(c):
    return None if not c or c[0] is None else c[0]


def ok_pos(c):
    return bool(c and c[0] is not None and c[1] is not None and c[2] is not None and c[2] - c[1] > 1e-9 and c[1] > 0)


def allow_holdout_operator_messages():
    """Confirm path only: h30lib.load_operator_messages_r1b refuses holdout rows (exploration guard). Re-bind, in the
    build module only, a copy without that guard. Same columns and rules."""
    def load_r1b_holdout(days):
        kc = (pl.read_parquet(SH / "kicks_classified.parquet")
              .filter(pl.col("pt_date").is_in(days) & pl.col("kind").cast(pl.Utf8).is_in(["nudge", "human_message"])))
        chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "regime", "length"]).with_row_index("msg")
        emb = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("emb_row")
        m = (kc.select("message_id", "t", "pt_date", "goal_no", "room", pl.col("kind").cast(pl.Utf8).alias("k0"),
                       pl.col("targets").alias("named"))
             .join(chat, on="message_id", how="left").join(emb, on="message_id", how="left"))
        lt = h30lib.leading_targets(m.filter(pl.col("k0") == "nudge")["message_id"].to_list())
        m = m.with_columns(pl.when(pl.col("k0") == "nudge").then(pl.lit("nudge")).otherwise(pl.lit("human")).alias("kind"),
                           pl.col("message_id").replace_strict(lt, default=None, return_dtype=pl.Int64).alias("target"),
                           pl.col("named").fill_null(pl.lit([], dtype=pl.List(pl.Int8))),
                           pl.lit([], dtype=pl.List(pl.Int8)).alias("recipients"))
        return m.select("msg", "message_id", "t", "pt_date", "goal_no", "regime", "room", "kind", "named", "recipients",
                        "length", "emb_row", "target").sort("t")
    B.load_operator_messages_r1b = load_r1b_holdout


def ledger_gate(use: dict, strict: bool) -> list[str]:
    """use: ledger target -> modality H30 will compute there. Blocks only a same-family prior run of the same modality."""
    sys.path.insert(0, str(ROOT))
    from infra.shared import holdout_ledger as hl
    led = hl.load()
    bad = []
    for t, mods in use.items():
        for mod in mods:
            mine = [e for e in led["entries"] if e["hypothesis"] == HYP and e["target"] == t and e["modality"] == mod]
            fam = sorted({f for e in mine for f in e["estimator_family"]}) or ["kick_response"]
            r = hl.check(HYP, t, mod, fam)
            same_mod = [u["hypothesis"] for u in r["prior_runs_same_family"] if u["modality"] == mod]
            print(f"ledger {t} [{mod}]: allowed={r['allowed']} same_family_same_modality_runs={sorted(set(same_mod))} "
                  f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
                  f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}")
            if same_mod:
                bad.append(f"ledger: {t} {mod}: same-family same-modality prior run by {sorted(set(same_mod))}")
    return bad if strict else []


def con_stat(out: Path, cls_list, nd: int, W) -> dict:
    res = {}
    for m, fn in MODELS.items():
        cs = pl.read_parquet(out / fn)
        sub = cs.filter(pl.col("cls").is_in(cls_list) & pl.col("chi_orth").is_not_nan())
        res[m] = boot_mean_by_day(sub, "chi_orth", np.arange(nd), W) if sub.height >= 10 else None
        res[m + "_n"] = sub.height
    return res


def content_only(p: str, days: list[str], allow: bool, out: Path) -> dict:
    info = B.build_period(p, allow_holdout=allow, days=days, out_dir=out, data=DATA)
    nd = info["n_days"]; W = boot_weights(nd, 1000)
    return {"n_days": nd, "con_human": con_stat(out, ["H_und", "H_men"], nd, W),
            "con_Ntgt": con_stat(out, ["N_tgt"], nd, W)}


def con_of(R, cls, m):
    key = "con" if m == "bge" else "con_gte"
    return ((R.get(key) or {}).get(cls) or {}).get("orth")


def dl(est, ses):
    est, ses = np.asarray(est, float), np.asarray(ses, float)
    ok = np.isfinite(est) & np.isfinite(ses) & (ses > 0)
    est, ses = est[ok], ses[ok]
    if len(est) == 0:
        return None
    w = 1 / ses ** 2; mu = (w * est).sum() / w.sum()
    Q = (w * (est - mu) ** 2).sum(); df = max(len(est) - 1, 1)
    tau2 = max(0.0, (Q - df) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    ws = 1 / (ses ** 2 + tau2); m = (ws * est).sum() / ws.sum(); s = np.sqrt(1 / ws.sum())
    return [float(m), float(m - 1.96 * s), float(m + 1.96 * s)]


def pool(cis):
    cis = [c for c in cis if c and c[1] is not None]
    return dl([c[0] for c in cis], [(c[2] - c[1]) / 3.92 for c in cis]) if cis else None


def run_T1(p, days, allow, d1):
    B.build_period(p, allow_holdout=allow, days=days, out_dir=d1, data=DATA)
    return RP.run_period(p, days=days, allow_holdout=allow, out_dir=d1, fig_dir=d1 / "figures", do_h04=False, n_swap=10,
                         data=DATA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="understand", action="store_true")
    ap.add_argument("--include-g45-activity", action="store_true",
                    help="confirm only, on Vivian's written override: compute #45 nudge->activity (same family as H04)")
    ap.add_argument("--root", type=Path, default=None, help="dry-run output root (default OUT/r1b/confirm_r1b_dryrun)")
    a = ap.parse_args()
    use = {"#51-tail": ["message content", "activity timing"], "G45": ["message content"],
           **{f"G{g}": ["message content"] for g in (46, 47, 48, 49, 50)}}
    if a.include_g45_activity:
        use["G45"].append("activity timing")
    if not a.dry_run:
        if not (a.confirm and a.understand):
            sys.exit(f"Refusing: the confirmatory run needs both {FLAGS[0]} and {FLAGS[1]} (or use --dry-run).")
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "hypotheses/H30-operator-susceptibility"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("Refusing: commit the H30 card, confirm_r1b.py and CONFIRM_R1B.md before the holdout run (reuse policy 1).")
        bad = ledger_gate(use, strict=True)
        if bad:
            sys.exit("Refusing (holdout ledger):\n  " + "\n  ".join(bad))
        allow_holdout_operator_messages()
    else:
        ledger_gate({**use, "G45": ["message content", "activity timing"]}, strict=False)
    mode = "dryrun" if a.dry_run else "confirm"
    allow = not a.dry_run
    root = (a.root or OUT / "r1b" / "confirm_r1b_dryrun") if a.dry_run else OUT / "r1b" / "confirm_r1b"
    T = targets(mode)
    g45_act = a.dry_run or a.include_g45_activity
    out = {"mode": mode, "data": DATA, "g45_activity": g45_act,
           "targets": {"T1": [x[0] for x in T["T1"]], "T2": T["T2"][0], "T3": [x[0] for x in T["T3"]]}}
    rows = []

    def add(id_, primary, obs, passed):
        rows.append({"id": id_, "primary": primary, "observed": obs, "pass": passed})

    # ---- T1 (#51 tail, or stand-ins: G51 with nudges and G51z without)
    R1s = {}
    for key, p, days in T["T1"]:
        R1s[key] = run_T1(p, days, allow, root / "T1" / key)
    R1 = R1s["G51"]
    n_t1 = R1["act_n"].get("N_tgt") or 0
    nud = n_t1 >= 30
    c11 = R1["act"].get("N_tgt") if nud else None
    add("C51-1-r1b", False, {"chi": c11, "n_kicks": n_t1}, ok_pos(c11) if nud else None)
    c12 = {m: con_of(R1, "H_und", m) for m in MODELS}
    add("C51-2-r1b", True, c12, all(ok_pos(c) for c in c12.values()))
    fr, rp = (R1.get("act_first") or {}).get("N_tgt"), (R1.get("act_repeat") or {}).get("N_tgt")
    add("C51-3", False, {"first": fr, "repeat": rp},
        (bool(fval(fr) is not None and fval(rp) is not None and fval(fr) > fval(rp))) if nud else None)
    c14 = R1["act"].get("N_by")
    add("C51-4-r1b", False, c14, bool(fval(c14) is not None and abs(fval(c14)) <= 0.3) if nud else None)
    s = R1["stability"].get("act_N_tgt", {})
    no_signal = (s.get("p_perm_msg", 1) >= 0.05 or (s.get("R1_perm_msg") or 0) < 0.5) and (s.get("p_lag1") is None or s["p_lag1"] >= 0.05)
    add("C51-5", False, {k: s.get(k) for k in ("n_days_eligible", "p_perm_msg", "R1_perm_msg", "lag1", "p_lag1")},
        bool(no_signal) if nud else None)
    c16 = {m: con_of(R1, "N_tgt", m) for m in MODELS}
    add("C51-6-r1b", False, c16, (all(fval(c) is not None and abs(fval(c)) < 0.02 for c in c16.values())) if nud else None)
    if "G51z" in R1s:   # dry-run only: the tail-like no-nudge stand-in must run through and give content
        Rz = R1s["G51z"]
        out["T1z_check"] = {"n_Ntgt": Rz["act_n"].get("N_tgt"), "C51-2-r1b": {m: con_of(Rz, "H_und", m) for m in MODELS}}
    # ---- T2 (#45 or stand-in): content always; activity only with the override (always in the dry run)
    p, days = T["T2"]
    d2 = root / "T2"
    if g45_act:
        B.build_period(p, allow_holdout=allow, days=days, out_dir=d2, data=DATA)
        R2 = RP.run_period(p, days=days, allow_holdout=allow, out_dir=d2, fig_dir=d2 / "figures", do_h04=False, n_swap=10,
                           data=DATA)
        c21 = R2["act"].get("N_tgt")
        add("C45-1-r1b", False, c21, bool(fval(c21) is not None and fval(c21) > 0))
        c22 = {m: con_of(R2, "H_und", m) for m in MODELS}
        acts = ([c11] if c11 else []) + ([c21] if c21 and (R2["act_n"].get("N_tgt") or 0) >= 10 else [])
    else:
        t2 = content_only(p, days, allow, d2)
        add("C45-1-r1b", False, "n/a: blocked (H04 same-family activity run on #45)", None)
        c22 = {m: None for m in MODELS}
        nd = t2["n_days"]; W = boot_weights(nd, 1000)
        c22 = con_stat(d2, ["H_und"], nd, W)
        c22 = {m: c22[m] for m in ("bge", "gte")}
        acts = [c11] if c11 else []
    add("C45-2-r1b", False, c22, all(fval(c) is not None and fval(c) > 0 for c in c22.values()))
    pooled_act = pool(acts)
    add("C-act-r1b", True, {"pooled": pooled_act, "k": len(acts)}, ok_pos(pooled_act) if acts else None)
    # ---- T3 (#46-#50 or stand-ins): content only
    t3 = {p: content_only(p, days, allow, root / "T3" / p) for p, days in T["T3"]}
    ph = {m: pool([v["con_human"][m] for v in t3.values()]) for m in MODELS}
    add("C4650-1-r1b", True, {"pooled": ph, "per_period": {k: v["con_human"] for k, v in t3.items()}},
        all(ok_pos(ph[m]) for m in MODELS))
    pn = {m: pool([v["con_Ntgt"][m] for v in t3.values()]) for m in MODELS}
    add("C4650-2-r1b", False, pn, all(pn[m] is not None and abs(pn[m][0]) < 0.02 for m in MODELS))
    prim = [r["pass"] for r in rows if r["primary"] and r["pass"] is not None]
    overall = ("untestable" if not prim else "supported" if all(prim) else ("failed" if not any(prim) else "mixed"))
    out.update({"rows": rows, "overall": overall, "t3": t3})
    root.mkdir(parents=True, exist_ok=True)
    jdump(out, root / "confirm_r1b_results.json")
    print(f"[{mode} r1b] overall: {overall}")
    for r in rows:
        print(f"  {r['id']:12s} {'P' if r['primary'] else 's'} pass={r['pass']}  {r['observed']}")
    if "T1z_check" in out:
        print("  T1z (no-nudge stand-in) check:", out["T1z_check"])


if __name__ == "__main__":
    main()
