"""H16 CONFIRMATORY test on the locked holdout (#32 regime I, #45 regime III), RE-FROZEN ON ROUND-1B INPUTS.
WRITTEN 2026-10-04, NOT RUN. `confirm.py` is left byte-for-byte untouched; what changed is in `CONFIRM_R1B.md`:
  * error loops on REAL failures (TS3r: turn_outcomes.failed for bash/type, platform error_class otherwise), not stderr;
  * nudge target = the leading @ (H35); every other nudge reader is N_by;
  * kick recipients from the CONTEXT LEDGER (context_ledger_items x call_windows), not the old `exposure` table:
      - spell hazards (TS1/TS1r/TS3r/TS4/TS5) keep posting-time look-backs, restricted to agents that read the message
        (a read-time clock inside a silence would put every read at the escape call itself);
      - pause gates (TS2r) count a kick only if the ledger shows it read by the gate call (receiving-call timing:
        read time - 30 s < gate), and an in-flight placebo (directed kicks posted after the gate call's context was
        assembled, before its outcome) is reported beside C45-3-r1b;
  * the swarm block (d) is dropped (descriptive, unscored; its Curie-Weiss statistic is the family H02 ran on #45);
    an outage sensitivity censors TS1r spells at `outages_fixed` runs with >= 10 all-silent minutes (round 1's A3
    rule, now on the fixed activity clock instead of H16's own minute-grid scan);
  * predictions changed where round 1b changed the result (ids *-r1b, one-line reasons in REASONS);
  * every prediction carries an estimator family; infra/shared/holdout_ledger.check() is called per (target, family).
    A family with a same-family prior run on the target (H04's kick response on #45) is NOT computed on the confirm
    path and its predictions are 'blocked (reuse policy)', unless --reuse-ruling FAMILY records Vivian's written ruling.

Usage:
  uv run python hypotheses/H16-metastable-traps-kramers/analysis/confirm_r1b.py --dry-run
      stand-ins G31 (to 02-20) for #32 and G44 for #45, non-holdout; writes <OUT>/confirm_r1b_dryrun/.
  uv run python hypotheses/H16-metastable-traps-kramers/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
      refuses unless this script, CONFIRM_R1B.md, the card and the code it imports are committed and unmodified.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2" if _v == "POLARS_MAX_THREADS" else "1"

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h16lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
sys.path.insert(0, str(L.ROOT))
import r1blib as RB  # noqa: E402
import run_period as RP  # noqa: E402
import confirm as C0  # noqa: E402  (frozen rule functions, reused unchanged)

HYP = "H16"
SH = L.SH
GATE_TOL_S = 30.0          # a kick read at the gate call (t_call ~ pause expiry + 3.2 s) counts for the gate
INFLIGHT_LAG_S = 3.2       # gate call's context assembled ~3.2 s after pause expiry (ledger calibration)
INFLIGHT_MAX_S = 60.0      # in-flight window: (hi + 3.2 s, min(t_gate, hi + 60 s))
TARGETS = {
    "G32": dict(goal=32, regime="I", standin=dict(goal=31, date_to="2026-02-20")),
    "G45": dict(goal=45, regime="III", standin=dict(goal=44, date_to=None)),
}
FAMILY = {"aging": "behavior_states", "kick": "kick_response"}


# ============================================================================ predictions
def rule_loop_no_aging(R, key):
    d = C0._deep(R, key)
    if d is None:
        return "too few", None
    b, lo, hi = C0._wald(d)
    return f"beta {b:.2f}, Wald [{lo:.2f}, {hi:.2f}], {d['events']} escapes", bool(not (b < -0.3 and hi < 0))


def rule_directed_not_break(R, key):
    c = R["c"].get(key, {})
    if not c.get("ok") or c.get("directed_rows", 0) < 30:
        return f"n/a ({c.get('directed_rows', 0)} directed rows)", None
    b, s = c["directed_lnHR"], c["directed_se"]
    return f"directed lnHR {b:.2f} +- {1.96 * s:.2f}, {c['directed_rows']} rows", bool(b <= 0 or b - 1.96 * s <= 0)


REASONS = {
    "C45-3-r1b": "same rule; the directed kick is now read by the gate call (ledger) with the leading-@ target (round 1b: "
                 "ORs moved < 1 SE under leading-@; 5/7 periods pass)",
    "C45-4-r1b": "round 1b: real-failure loops age only in #51 (3/10 point estimates < -0.3, G44 +1.63); the stderr "
                 "aging was an artifact, so a 5-day regime-III period is predicted NOT to show TS3r aging",
    "C45-6-r1b": "same rule; undirected recipients now from the ledger (round 1b: 6/8 above the day-swap null)",
    "C45-7-r1b": "new: directed kicks do not break real-failure loops (round 1b: 9/9 powered periods)",
    "C32-1-r1b": "round 1b: TS3r flat or timer-like in short regime-I periods (G27 -0.19, G30 +1.27, G31 -0.77, wide CIs); "
                 "predicted NOT to age; demoted to secondary (a negative without a power check)",
    "C32-2-r1b": "same rule; undirected recipients now from the ledger",
    "C32-5-r1b": "new primary: directed kicks do not break real-failure loops (round 1b: 9/9 incl. G27 regime I)",
}

PREDICTIONS: dict = {
    "G45": {
        "C45-1": dict(rule=C0.rule_ts1r_aging_wald, primary=True, fam="aging",
                      statement="TS1r deep-window escape hazard ages within agent: beta < -0.3 and Wald CI below 0 (unchanged)"),
        "C45-2": dict(rule=C0.rule_gate_aging_wald, primary=True, fam="aging",
                      statement="TS2r per-gate escape falls with re-pause count: Wald CI below 0 (unchanged)"),
        "C45-3-r1b": dict(rule=C0.rule_gate_directed_r, primary=True, fam="kick",
                          statement="a directed kick read by the gate call raises gate escape odds: TS2r OR(dose 1) >= 1.5, CI excl. 1"),
        "C45-4-r1b": dict(rule=rule_loop_no_aging, args=("TS3",), primary=False, fam="aging",
                          statement="TS3r real-failure loops do NOT age (not: beta < -0.3 with Wald CI below 0)"),
        "C45-5": dict(rule=C0.rule_dose_not_kramers, primary=False, fam="kick",
                      statement="where powered, the dose law is additive or saturating in the majority of cells (unchanged)"),
        "C45-6-r1b": dict(rule=C0.rule_undirected_above_null, primary=False, fam="kick",
                          statement="undirected room messages (ledger readers) raise TS1 escape above the day-swap null p95"),
        "C45-7-r1b": dict(rule=rule_directed_not_break, args=("TS3",), primary=False, fam="kick",
                          statement="directed kicks do not raise the TS3r break hazard (lnHR <= 0 or CI incl. 0; >= 30 rows)"),
    },
    "G32": {
        "C32-1-r1b": dict(rule=rule_loop_no_aging, args=("TS3",), primary=False, fam="aging",
                          statement="TS3r real-failure loops do NOT age (not: beta < -0.3 with Wald CI below 0)"),
        "C32-2-r1b": dict(rule=C0.rule_undirected_not_above_null, primary=True, fam="kick",
                          statement="regime I: undirected kicks (ledger readers) do NOT raise escape from >= 3-min silences above the day-swap null p95"),
        "C32-3": dict(rule=C0.rule_loop_aging_wald, args=("TS4",), primary=False, fam="aging",
                      statement="TS4 identical-command loops age: beta < -0.3 and Wald CI below 0 (unchanged)"),
        "C32-4": dict(rule=C0.rule_dose_not_kramers, primary=False, fam="kick",
                      statement="where powered, the dose law is additive or saturating (unchanged)"),
        "C32-5-r1b": dict(rule=rule_directed_not_break, args=("TS3",), primary=True, fam="kick",
                          statement="directed kicks do not raise the TS3r break hazard (lnHR <= 0 or CI incl. 0; >= 30 rows)"),
    },
}


# ============================================================================ guards
def committed_clean(paths) -> bool:
    for p in paths:
        r = subprocess.run(["git", "-C", str(L.ROOT), "ls-files", "--error-unmatch", str(p)], capture_output=True)
        if r.returncode != 0:
            return False
        r = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", str(p)], capture_output=True, text=True)
        if r.returncode != 0 or r.stdout.strip():
            return False
    return True


def ledger_status(rulings=()) -> dict:
    """target -> {family name: allowed}; ledger only, no data. rulings: families Vivian ruled distinct in writing."""
    from infra.shared import holdout_ledger as hl
    out = {}
    for t in TARGETS:
        out[t] = {}
        for key, fam in FAMILY.items():
            r = hl.check(HYP, t, "activity timing", [fam])
            ok = r["allowed"] or fam in rulings
            out[t][key] = ok
            print(f"ledger {t} [{fam}]: allowed={r['allowed']}{' (ruling recorded)' if fam in rulings and not r['allowed'] else ''} "
                  f"needs_disclosure={r['needs_disclosure']} prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
                  f"same_family_runs={sorted({u['hypothesis'] for u in r['prior_runs_same_family']})} "
                  f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}")
    return out


# ============================================================================ inputs (ledger kicks)
def load_kicks_ledger(days, allow_holdout=False):
    """Kick times per agent and class, recipients = ledger readers. Returns (K_post, K_read, info): K_post holds posting
    times, K_read the reader's first receiving-call t_call. Classes as h16lib.load_kicks; N_tgt = leading-@ target."""
    if not allow_holdout:
        L.assert_no_holdout(days)
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "speaker_kind", "agent"])
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    assert chat.height == men.height and (chat["message_id"] == men["message_id"]).all(), "chat_mentions_clean misaligned"
    chat = chat.with_columns(men["mentions_roster"].alias("men")).filter(pl.col("pt_date").is_in(days)).rename({"agent": "sender"})
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id", "omitted")
             .filter(pl.col("message_id").is_in(chat["message_id"].implode()) & ~pl.col("omitted")).collect())
    cw = pl.scan_parquet(SH / "call_windows.parquet").select("turn_id", "agent", "t_call", "holdout").collect()
    rd = items.join(cw, on="turn_id", how="inner")
    if not allow_holdout:
        rd = rd.filter(~pl.col("holdout"))          # margin calls on held-out days (RE-D1): filter, never assert
    rd = rd.group_by("message_id", "agent").agg(pl.col("t_call").min().alias("t_read"))
    ex = rd.join(chat, on="message_id", how="inner").filter(pl.col("sender").is_null() | (pl.col("agent") != pl.col("sender")))
    ok = L._roster_ok()
    ex = ex.filter(pl.col("agent").is_in(list(ok)))
    nud = RB.nudge_targets(days, allow_holdout=allow_holdout).select("message_id", "target")
    ex = ex.join(nud, on="message_id", how="left")
    sk = pl.col("speaker_kind").cast(pl.Utf8)
    directed = pl.col("men").list.contains(pl.col("agent")).fill_null(False)
    is_nudge = pl.col("message_id").is_in(nud["message_id"].implode())
    ex = ex.with_columns(
        pl.when((sk == "agent") & directed).then(pl.lit("A_men"))
        .when(sk == "agent").then(pl.lit("A_und"))
        .when((sk == "human") & directed).then(pl.lit("H_men"))
        .when(sk == "human").then(pl.lit("H_und"))
        .when(is_nudge & (pl.col("agent").cast(pl.Int16) == pl.col("target").fill_null(-1))).then(pl.lit("N_tgt"))
        .when(is_nudge).then(pl.lit("N_by"))
        .otherwise(pl.lit("drop")).alias("kc"),
        (pl.col("t").dt.epoch("us") / 1e6).alias("ts"), (pl.col("t_read").dt.epoch("us") / 1e6).alias("tr"))
    ex = ex.filter(pl.col("kc") != "drop")
    K_post, K_read = {}, {}
    for (a, c), g in ex.group_by(["agent", "kc"]):
        K_post.setdefault(int(a), {})[c] = np.sort(g["ts"].to_numpy())
        K_read.setdefault(int(a), {})[c] = np.sort(g["tr"].to_numpy())
    info = {"kick_recipients": "context ledger (non-omitted items, first receiving call per reader)",
            "N_tgt": "leading-@ nudge target, if it read the nudge", "gate_timing": f"read time - {GATE_TOL_S:.0f} s"}
    return K_post, K_read, info


def build_period_r1b(name, days, out: Path, allow_holdout=False) -> dict:
    """Mirror of scheme/build.py: build_period(r1b=True) with ledger kicks."""
    out.mkdir(parents=True, exist_ok=True)
    W = L.windows(days)
    rows = RB.load_rows_r1b(days, allow_holdout=allow_holdout)
    K, K_read, info = load_kicks_ledger(days, allow_holdout=allow_holdout)
    K_gate = {a: {c: v - GATE_TOL_S for c, v in cl.items()} for a, cl in K_read.items()}
    ts1 = L.build_ts1(rows, W, K)
    ts1r = L.build_ts1(rows, W, K, robust=True)
    ts2 = L.build_ts2(rows, W, K_gate)
    ts3 = L.build_turn_loops(rows, W, K, "err")
    ts4 = L.build_turn_loops(rows, W, K, "cmd")
    kk = [pl.DataFrame({"agent": np.full(len(arr), a, np.int16), "ts": arr, "kclass": [c] * len(arr)})
          for a, cl in K.items() for c, arr in cl.items()]
    kk = pl.concat(kk) if kk else pl.DataFrame({"agent": [], "ts": [], "kclass": []})
    tables = [("ts1", ts1), ("ts1r", ts1r), ("ts2", ts2), ("ts3", ts3), ("ts4", ts4), ("kicks", kk),
              ("ts5", RB.build_window_traps(days, K, "blocked", allow_holdout)),
              ("ts6", RB.build_window_traps(days, K, "loop", allow_holdout))]
    for nm, df in tables:
        df.write_parquet(out / f"{nm}.parquet", compression="zstd")
    L.write_provenance(out, "hypotheses/H16-metastable-traps-kramers/analysis/confirm_r1b.py",
                       ["events_core", "actions", "actions_bash_head_fixed", "behavior_states/turn_outcomes",
                        "behavior_states_v3", "artifact_commands_text (hashed)", "chat_core", "chat_mentions_clean",
                        "chat_text (leading @, memory only)", "kicks_classified", "context_ledger_items", "call_windows",
                        "outages_fixed/outages", "calendar", "roster"],
                       {"period": name, "days": days, "allow_holdout": allow_holdout, **info})
    return {"days": days, "W": W, "K": K}


def inflight_placebo(ts2: pl.DataFrame, K: dict):
    """TS2r gates: directed kicks POSTED after the gate call's context was assembled (hi + 3.2 s) and before its outcome
    (min(t_gate, hi + 60 s)) cannot be read at the gate. Their lnOR, in the same logit as the read kicks, is the
    contemporaneous-convergence placebo. Descriptive (outcome-dependent window length; nudger targets idle agents)."""
    g = RP.ts2_robust_view(ts2)
    if g.height < 30:
        return {"ok": False}
    g = g.filter((pl.col("outcome") != "censored") & pl.col("declared_s").is_not_null() & (pl.col("declared_s") > 0))
    tp, dcl, tg = g["t_pause"].to_numpy(), g["declared_s"].to_numpy(), g["t_gate"].to_numpy()
    hi = np.minimum(tg, tp + dcl)
    lo_p, hi_p = hi + INFLIGHT_LAG_S, np.minimum(tg, hi + INFLIGHT_MAX_S)
    ag = g["agent"].to_numpy()
    pl_n = np.zeros(g.height, int)
    for a in np.unique(ag):
        m = ag == a
        kc = L.kick_counts(K, int(a), lo_p[m], np.maximum(hi_p[m], lo_p[m]), classes=RP.GROUPS["directed"])
        pl_n[m] = np.sum([kc[c] for c in RP.GROUPS["directed"]], axis=0)
    y = (g["outcome"] != "repause").to_numpy().astype(int)
    gd = np.sum([g[f"n_{c}"].to_numpy() for c in RP.GROUPS["directed"]], axis=0)
    X = np.stack([np.log(g["k"].to_numpy().astype(float)), np.log(g["declared_s"].to_numpy()),
                  (gd > 0).astype(float), (pl_n > 0).astype(float)], 1)
    if (pl_n > 0).sum() < 5:
        return {"ok": False, "placebo_gates": int((pl_n > 0).sum())}
    f = L.glm_fe(y, X, ag, "logit")
    return {"ok": True, "read_lnOR": float(f["beta"][2]), "read_se": float(f["se"][2]), "read_gates": int((gd > 0).sum()),
            "inflight_lnOR": float(f["beta"][3]), "inflight_se": float(f["se"][3]), "inflight_gates": int((pl_n > 0).sum()),
            "window_s_median": float(np.median(np.maximum(hi_p - lo_p, 0)))}


def village_off_sensitivity(folder: Path, days, rng, B, allow_holdout):
    # round-1 A3 rule (all present agents silent >= 10 min), now on the fixed activity clock (outages_fixed)
    o = pl.read_parquet(SH / "outages_fixed/outages.parquet").filter(pl.col("pt_date").is_in(days) & (pl.col("k0_longest") >= 10))
    if not allow_holdout:
        assert not o["holdout"].any()
    iv = sorted(zip((o["t_start"].dt.epoch("us") / 1e6).to_list(), (o["t_end"].dt.epoch("us") / 1e6).to_list()))
    ts1r = pl.read_parquet(folder / "ts1r.parquet")
    d = RP.dwell_ts1(RP.censor_outages(ts1r, iv), rng, B, "ts1r") if iv else None
    return {"n_silent_runs_ge10min": len(iv), "TS1r_deep": d.get("deep") if d else "no all-silent runs >= 10 min"}


def analyze_r1b(folder: Path, regime: str, rng, kicks_allowed: bool, B=200, n_null=100):
    rd = lambda n: pl.read_parquet(folder / f"{n}.parquet")
    ts1, ts1r, ts2, ts3, ts4, kk = (rd(n) for n in ("ts1", "ts1r", "ts2", "ts3", "ts4", "kicks"))
    days = sorted(set(ts1["pt_date"].to_list()) | set(ts1r["pt_date"].to_list()))
    W = L.windows(days)
    R = {"regime": regime, "n_days": len(days)}
    R["a"] = {"TS1r": RP.dwell_ts1(ts1r, rng, B, "ts1r"), "TS1": RP.dwell_ts1(ts1, rng, max(B // 2, 20), "ts1"),
              "TS2r": RP.dwell_ts2(RP.ts2_robust_view(ts2), rng, B) if regime == "III" else {"ok": False, "reason": "regime"},
              "TS3": RP.dwell_loops(ts3, rng, B, L.LOOP_MIN), "TS4": RP.dwell_loops(ts4, rng, B, L.LOOP_MIN),
              "TS5": RB.dwell_windows(rd("ts5"), rng, B), "TS6": RB.dwell_windows(rd("ts6"), rng, B)}
    if not kicks_allowed:
        R["c"] = {"blocked": "kick_response family not computed (reuse policy)"}
        return R
    K = RP.kicks_dict(kk) if kk.height else {}
    R["c"] = {"TS1": RP.kicks_ts1(ts1, K, W, rng, n_null, "ts1"), "TS1r": RP.kicks_ts1(ts1r, K, W, rng, 0, "ts1r"),
              "TS2r": RP.kicks_ts2(RP.ts2_robust_view(ts2)) if regime == "III" else {"ok": False, "reason": "regime"},
              "TS3": RP.kicks_loops(ts3), "TS4": RP.kicks_loops(ts4)}
    R["c"]["TS2r_inflight_placebo"] = inflight_placebo(ts2, K) if regime == "III" else {"ok": False, "reason": "regime"}
    return R


def score(R, target, allowed):
    out = []
    for pid, spec in PREDICTIONS[target].items():
        if not allowed[spec["fam"]]:
            out.append({"id": pid, "statement": spec["statement"], "observed": "not computed", "verdict": "blocked (reuse policy)"})
            continue
        try:
            obs, ok = spec["rule"](R, *spec.get("args", ()))
        except KeyError as e:
            obs, ok = f"n/a ({e})", None
        out.append({"id": pid, "statement": spec["statement"], "observed": obs,
                    "verdict": "pass" if ok else ("fail" if ok is False else "n/a")})
    prim = [o for o in out if PREDICTIONS[target][o["id"]]["primary"] and not o["verdict"].startswith("blocked")]
    npass = sum(o["verdict"] == "pass" for o in prim)
    nfail = sum(o["verdict"] == "fail" for o in prim)
    overall = "supported" if (nfail == 0 and npass >= 1) else ("failed" if npass == 0 and nfail >= 1 else "mixed")
    return {"rows": out, "overall": overall,
            "rule": "unblocked primary predictions: all scored pass -> supported; none pass -> failed; else mixed"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--reuse-ruling", nargs="*", default=[], help="estimator families Vivian ruled distinct in writing (LOG.md)")
    a = ap.parse_args()
    if a.dry_run == a.confirm:
        raise SystemExit("choose exactly one of --dry-run or --confirm")
    if a.confirm and not a.ack:
        raise SystemExit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
    allowed = ledger_status(set(a.reuse_ruling))
    if a.confirm:
        must = [Path(__file__).resolve(), HERE / "CONFIRM_R1B.md", HERE.parent / "README.md", HERE / "confirm.py",
                HERE / "h16lib.py", HERE / "r1blib.py", HERE / "run_period.py"]
        if not committed_clean(must):
            raise SystemExit("refusing: commit confirm_r1b.py, CONFIRM_R1B.md, the card and the code it imports first "
                             "(holdout reuse policy)")
    outroot = L.OUT / ("confirm_r1b_dryrun" if a.dry_run else "confirm_r1b")
    allres = {"mode": "dry-run (non-holdout stand-ins)" if a.dry_run else "CONFIRMATORY (locked holdout)",
              "ledger_allowed": allowed, "reuse_rulings": a.reuse_ruling, "reasons": REASONS,
              "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    for target, spec in TARGETS.items():
        if a.dry_run:
            st = spec["standin"]
            days = L.period_days(st["goal"], allow_holdout=False, date_to=st.get("date_to"))
            L.assert_no_holdout(days)
            allow, ok = False, {"aging": True, "kick": True}       # stand-ins are not blocked; target status reported
        else:
            days = L.period_days(spec["goal"], allow_holdout=True)
            allow, ok = True, allowed[target]
        folder = outroot / target
        build_period_r1b(target + ("-standin" if a.dry_run else ""), days, folder, allow_holdout=allow)
        rng = np.random.default_rng(L.SEED + 1000 + spec["goal"])
        R = analyze_r1b(folder, spec["regime"], rng, kicks_allowed=ok["kick"])
        R["village_off_sensitivity"] = village_off_sensitivity(folder, days, rng, 100, allow)
        R["score"] = score(R, target, ok)
        if a.dry_run:
            R["blocked_on_real_target"] = [p for p, s in PREDICTIONS[target].items() if not allowed[target][s["fam"]]]
        L.jdump(R, folder / "results.json")
        allres[target] = {"score": R["score"], "inflight": R["c"].get("TS2r_inflight_placebo"),
                          "village_off": R["village_off_sensitivity"], **({"days": days} if a.dry_run else {})}
        print(target, R["score"]["overall"])
        for row in R["score"]["rows"]:
            print("  ", row["id"], row["verdict"], "|", row["observed"])
        if a.dry_run:
            print("  blocked on the real target:", R["blocked_on_real_target"])
            print("  in-flight placebo:", R["c"].get("TS2r_inflight_placebo"))
            print("  village-off sensitivity:", R["village_off_sensitivity"])
    L.jdump(allres, outroot / "confirm_r1b_results.json")


if __name__ == "__main__":
    main()
