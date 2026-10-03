"""H04 CONFIRMATORY test on the locked holdout: NE21 (hours 4 -> 8 -> 4 -> 8 h) and NE23 (nudger off/on).

*** WRITTEN 2026-10-03, NOT RUN. Running it on the holdout is a one-shot confirmation. ***
Predictions C1-C4 and MF-C are on the card (hypotheses/H04-reversible-forcing/README.md), including the dated
amendment of C3 (Onsager T_eff instead of the CKP T_eff, which exploration showed to be unidentifiable).

Usage
  uv run python .../confirm_ne21_ne23.py --dry-run     # same pipeline on NON-holdout surrogate segments (code check)
  uv run python .../confirm_ne21_ne23.py --confirm --i-understand-this-uses-the-locked-holdout

Per segment: matched Green's functions (nudge -> target, human -> room/mentioned), Hawkes branching ratio n and
exogenous kernels (day bootstrap), Onsager FD ratio X(30) and T_eff = 1/X, the h-free FDT shape test, the CKP ratio
(reported even if unidentifiable), the mean-field loop gain K, tau_0, tau_pred = tau_0/(1-K) and the kernel decay
time (H04-MF). NE23: manipulation check, idle metrics and n for the #best agents in the off session vs. B1 and A2.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h04lib  # noqa: E402
from h04lib import *  # noqa: E402,F403
from hawkes import Model, build_series, fit_suite, simulate  # noqa: E402
from explore import run_suite  # noqa: E402
from ne10 import day_metrics  # noqa: E402

# ----------------------------------------------------------------------------- segment definitions (PT dates, end exclusive)
SEGMENTS = {  # name: (start, end, documented hours expected)
    "A1": ("2026-05-26", "2026-06-06", 4),   # #44 (non-holdout) + #45 (holdout); 06-03 disables parallel tool use
    "B1": ("2026-06-08", "2026-06-13", 8),   # #46 weekdays; 06-11: default pause 12 h -> 5 min, NE22 cap
    "A2": ("2026-06-15", "2026-06-27", 4),   # #47-#49; nudger re-enabled 06-15
    "B2": ("2026-06-29", "2026-07-04", 8),   # #50; GitLab migration (NE24) on 06-29
}
SENSITIVITY = {"B1a_pre0611": ("2026-06-08", "2026-06-11", 8), "B1b_post0611": ("2026-06-11", "2026-06-13", 8),
               "A1_only45": ("2026-06-01", "2026-06-06", 4)}
OFF = ("2026-06-13", "2026-06-14")          # Saturday-evening session, #best agents only, nudger disabled
EXTENSION = {"B2x_nonholdout_51": ("2026-07-06", "2026-07-18", 8)}  # 8 h continues in #51 (not holdout)

# Non-holdout surrogates for --dry-run (code check only; numbers are meaningless for the hypothesis)
DRY = {"A1": ("2026-05-04", "2026-05-16", 4), "B1": ("2026-07-06", "2026-07-11", 8),
       "A2": ("2026-05-18", "2026-05-30", 4), "B2": ("2026-07-13", "2026-07-18", 8)}
DRY_SENS = {"B1a_pre0611": ("2026-07-06", "2026-07-09", 8), "B1b_post0611": ("2026-07-09", "2026-07-11", 8),
            "A1_only45": ("2026-05-11", "2026-05-16", 4)}
DRY_OFF = ("2026-07-20", "2026-07-21")
DRY_EXT = {"B2x_nonholdout_51": ("2026-07-20", "2026-07-25", 8)}

NBOOT_HAWKES = 100
PLACEBO = OUT / "explore_placebo_switch.json"   # non-holdout week-to-week noise floor (placebo_switch.py)


def placebo_p95(key):
    """95th percentile of |ABAB contrast| over runs of four adjacent same-hours non-holdout weeks."""
    if not PLACEBO.exists():
        return None
    return json.loads(PLACEBO.read_text()).get("placebo_ABAB_contrast", {}).get(key, {}).get("abs_p95")
NBOOT_PARAM = 20


def seg_days(cal, start, end, hours, allow_holdout):
    days = select_days(cal, allow_holdout=allow_holdout, date_from=start, date_to=end)
    meta = cal.filter(pl.col("pt_date").is_in(days)).select("pt_date", "documented_hours", "weekday")
    bad = [d for d, h, w in meta.iter_rows() if hours is not None and h != hours]
    return days, bad


def hawkes_segment(days, agents=None, nboot=None) -> dict:
    nboot = NBOOT_HAWKES if nboot is None else nboot
    ser = build_series(days, agents)
    if ser.n_events < 50:
        return {"n_events": ser.n_events, "note": "too few events"}
    m = fit_suite(ser)
    out = {"fit": m.summary()}
    rng = np.random.default_rng(RNG_SEED)
    rows = {"n": [out["fit"]["n"]], "a1": [out["fit"]["a1"]], "en": [out["fit"].get("en", np.nan)], "eh": [out["fit"].get("eh", np.nan)]}
    if len(ser.days) >= 3:
        out["boot"] = "day"
        for _ in range(nboot):
            idx = rng.integers(0, len(ser.days), len(ser.days))
            f = Model(ser.subset(list(idx)), m.free).fit(x0=m.theta).summary()
            for k in rows:
                rows[k].append(f.get(k, np.nan))
    else:  # a single session: parametric bootstrap (simulate from the fit, refit)
        out["boot"] = "parametric"
        for r in range(NBOOT_PARAM):
            f = Model(simulate(m, RNG_SEED + r), m.free).fit(x0=m.theta).summary()
            for k in rows:
                rows[k].append(f.get(k, np.nan))
    out["_rows"] = {k: np.array(v, float) for k, v in rows.items()}
    out["n_ci"] = ci(out["_rows"]["n"]); out["a1_ci"] = ci(out["_rows"]["a1"])
    out["en_ci"] = ci(out["_rows"]["en"]); out["eh_ci"] = ci(out["_rows"]["eh"])
    return out


def activity_metrics(days, agents=None) -> dict:
    D = load_days(days)
    ag = agents or set(int(a) for d in D for a in d.agents)
    m = [day_metrics(d, ag) for d in D]
    tot = {k: sum(x[k] for x in m) for k in m[0]}
    return {"idle_fraction": tot["idle"] / tot["min"], "active_fraction": tot["active"] / tot["min"],
            "mean_inactive_run_min": tot["run_len"] / max(1, tot["runs"]),
            "escape_hazard_after10": tot["exit10"] / max(1, tot["expo10"]), "agent_minutes": tot["min"]}


def paired(a_rows, b_rows, op):
    """CI for op(a, b) from independent bootstrap rows (row 0 = point)."""
    a, b = np.asarray(a_rows, float), np.asarray(b_rows, float)
    n = min(len(a), len(b))
    with np.errstate(invalid="ignore", divide="ignore"):
        return ci(op(a[:n], b[:n]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run == (a.confirm and a.ack):
        sys.exit("Refusing: pass --dry-run (non-holdout surrogates) or --confirm --i-understand-this-uses-the-locked-holdout.")
    holdout = not a.dry_run
    global NBOOT_HAWKES, NBOOT_PARAM
    if a.dry_run:  # code check only: few bootstrap refits
        NBOOT_HAWKES, NBOOT_PARAM = 5, 3
    segs, sens, off, ext = (SEGMENTS, SENSITIVITY, OFF, EXTENSION) if holdout else (DRY, DRY_SENS, DRY_OFF, DRY_EXT)
    tag = "confirm" if holdout else "dryrun"
    t0 = time.time()
    cal = calendar()
    res = {"mode": tag, "started_at": dt.datetime.now(dt.timezone.utc).isoformat(), "segments": {}, "sensitivity": {},
           "extension": {}, "hours_mismatch": {}}

    # ------------------------------------------------------------- NE21 segments (+ pooled 4 h / 8 h)
    seg_days_ = {}
    for name, (s0, s1, h) in {**segs, **sens, **ext}.items():
        allow = holdout and name not in ext  # the extension is non-holdout anyway
        days, bad = seg_days(cal, s0, s1, h, allow)
        seg_days_[name] = days
        res["hours_mismatch"][name] = bad
    seg_days_["pooled_4h"] = sorted(seg_days_["A1"] + seg_days_["A2"])
    seg_days_["pooled_8h"] = sorted(seg_days_["B1"] + seg_days_["B2"])
    rows = {}
    for name, days in seg_days_.items():
        if len(days) < 2:
            res["segments"][name] = {"note": "fewer than 2 active days", "days": days}
            continue
        g = run_suite(f"{tag}:{name}", days, keep_rows=True)
        rows[name] = {k: np.asarray(v, float) for k, v in g.pop("_rows").items()}
        hk = hawkes_segment(days) if name not in ("pooled_4h", "pooled_8h") else {}
        if hk.get("_rows"):
            rows[name].update({f"hawkes_{k}": v for k, v in hk.pop("_rows").items()})
        entry = {"days": days, "G": g["G"], "linearity": g["linearity"], "fd": g["fd"], "mf": g["mf"], "hawkes": hk,
                 "activity": activity_metrics(days)}
        bucket = "segments" if name in segs or name.startswith("pooled") else ("sensitivity" if name in sens else "extension")
        res[bucket][name] = entry
        print(f"[{name}] done {time.time() - t0:.0f}s", flush=True)

    # ------------------------------------------------------------- NE23: off session vs B1 / A2 for the same agents
    off_days, _ = seg_days(cal, off[0], off[1], None, holdout)
    ne23 = {"off_days": off_days}
    if off_days:
        Doff = load_days(off_days)
        off_agents = set(int(a) for d in Doff for i, a in enumerate(d.agents) if (d.state[i] >= 2).any())
        msgs = load_messages(off_days)
        ne23["manipulation_check_nudges_in_off"] = int((msgs["kind"] == "nudge").sum())
        ne23["off_agents"] = sorted(off_agents)
        for name, days in (("off", off_days), ("B1", seg_days_["B1"]), ("A2", seg_days_["A2"])):
            ne23[f"activity_{name}"] = activity_metrics(days, off_agents)
            hk = hawkes_segment(days, off_agents)
            if hk.get("_rows"):
                rows[f"ne23_{name}"] = hk.pop("_rows")
            ne23[f"hawkes_{name}"] = hk
    res["ne23"] = ne23

    # ------------------------------------------------------------- verdicts (rules from the card)
    V = {}
    R = lambda s, k: rows.get(s, {}).get(k)
    order = ["A1", "B1", "A2", "B2"]
    def abab(key):
        """4 h minus 8 h ABAB contrast D = (A1 + A2)/2 - (B1 + B2)/2 with its bootstrap CI."""
        r = [R(s_, key) for s_ in order]
        m = min(len(x) for x in r)
        return ci((r[0][:m] + r[2][:m]) / 2 - (r[1][:m] + r[3][:m]) / 2)

    for key, pk in (("hawkes_n", "n"), ("hawkes_a1", "a1")):
        if all(R(s_, key) is not None for s_ in order):
            dn = {f"{x}-{y}": paired(R(x, key), R(y, key), lambda u, v: u - v)
                  for x, y in (("A1", "B1"), ("A2", "B1"), ("A2", "B2"))}
            sign_ok = sum(v[0] > 0 for v in dn.values())
            ns = [R(s_, key)[0] for s_ in order]
            mono = bool(np.all(np.diff(ns) > 0) or np.all(np.diff(ns) < 0))
            D, thr = abab(key), placebo_p95(pk)
            beyond = bool(thr is not None and D[0] > thr)
            verdict = ("falsified" if (mono or sign_ok < 2) else
                       "supported" if (beyond and sign_ok >= 2) else "not distinguishable from week-to-week variation")
            V[f"C1_reversal_of_{pk}" + ("" if pk == "n" else " (secondary)")] = {
                pk: dict(zip(order, ns)), "delta(4h-8h)": dn, "switches_with_predicted_sign": sign_ok, "monotone_drift": mono,
                "ABAB_contrast": D, "placebo_abs_p95": thr, "verdict": verdict}
    for k in ("nudge_target_iso", "human_all_iso"):
        a8, a4 = R("pooled_8h", f"A30:{k}"), R("pooled_4h", f"A30:{k}")
        if a8 is not None and a4 is not None:
            r = paired(a8, a4, lambda u, v: u / v)
            verdict = ("holds" if 0.7 <= r[0] <= 1.3 and r[1] <= 1 <= r[2] else
                       "fails" if (r[2] < 0.7 or r[1] > 1.3) else "inconclusive")
            V[f"C2_kernel_invariant_{k}"] = {"A30_8h_over_4h": r, "verdict": verdict}
    for k in ("nudge_target_iso", "human_all_iso"):
        if not all(R(s, f"X30:{k}") is not None for s in order):
            V[f"C3_Teff_reverses_{k}"] = {"verdict": "untestable (fewer than 10 kicked activations in some segment)",
                                          "available": [s for s in order if R(s, f"X30:{k}") is not None]}
        else:
            T = [1 / R(s, f"X30:{k}")[0] for s in order]
            d = np.sign(np.diff(T))
            V[f"C3_Teff_reverses_{k}"] = {"Teff_onsager": dict(zip(order, T)),
                                          "Teff_ci": {s: ci(1 / R(s, f"X30:{k}")) for s in order},
                                          "signs": d.tolist(),
                                          "verdict": "supported" if (d[0] == -d[1] == d[2] and d[0] != 0) else "falsified"}
    if ne23.get("off_days"):
        c4 = {"manipulation_check": ne23["manipulation_check_nudges_in_off"] == 0}
        ao, a1, a2 = ne23["activity_off"], ne23["activity_B1"], ne23["activity_A2"]
        c4["idle_higher_off"] = bool(ao["idle_fraction"] > max(a1["idle_fraction"], a2["idle_fraction"]))
        c4["inactive_run_longer_off"] = bool(ao["mean_inactive_run_min"] > max(a1["mean_inactive_run_min"], a2["mean_inactive_run_min"]))
        if R("A2", "A30:nudge_target_iso") is not None and R("B1", "A30:nudge_target_iso") is not None:
            r = paired(R("A2", "A30:nudge_target_iso"), R("B1", "A30:nudge_target_iso"), lambda u, v: u / v)
            c4["kernel_returns_A2_over_B1"] = r
            c4["kernel_returns"] = bool(0.7 <= r[0] <= 1.3)
        if rows.get("ne23_off") and rows.get("ne23_B1"):
            dn = paired(rows["ne23_off"]["n"], rows["ne23_B1"]["n"], lambda u, v: u - v)
            c4["n_off_minus_B1"] = dn
            c4["n_unchanged"] = bool(abs(dn[0]) < 0.1)
        keys = ["manipulation_check", "idle_higher_off", "inactive_run_longer_off", "kernel_returns", "n_unchanged"]
        c4["verdict"] = ("supported" if all(c4.get(k) for k in keys) else
                         "partial" if sum(bool(c4.get(k)) for k in keys) >= 3 else "not supported")
        V["C4_NE23"] = c4
    if all(R(s, "K") is not None for s in order):
        Ks = [R(s, "K")[0] for s in order]
        dK = {f"{x}-{y}": paired(R(x, "K"), R(y, "K"), lambda u, v: u - v) for x, y in (("A1", "B1"), ("A2", "B1"), ("A2", "B2"))}
        flips = sum(v[0] > 0 for v in dK.values())
        gap = {s: paired(R(s, "tauG_relax:nudge_target_iso"), R(s, "tau_pred"), lambda u, v: u / v)
               for s in order if R(s, "tauG_relax:nudge_target_iso") is not None}
        DK, thrK = abab("K"), placebo_p95("K")
        V["MF_C"] = {"K": dict(zip(order, Ks)), "delta_K(4h-8h)": dK, "flips_with_predicted_sign": flips,
                     "ABAB_contrast_K": DK, "placebo_abs_p95": thrK, "beyond_placebo": bool(thrK is not None and DK[0] > thrK),
                     "tauG_over_taupred_nudge": gap,
                     "gap_persists(>=3 in every segment)": bool(gap and all(v[0] >= 3 for v in gap.values())),
                     "verdict_K": ("falsified" if flips < 2 else
                                   "supported" if (flips >= 2 and thrK is not None and DK[0] > thrK) else
                                   "not distinguishable from week-to-week variation")}
    res["verdicts"] = V
    res["runtime_s"] = time.time() - t0
    OUT.mkdir(parents=True, exist_ok=True)
    jdump(res, OUT / f"{tag}_ne21_ne23.json")
    write_provenance(f"{tag}_ne21_ne23.json", "hypotheses/H04-reversible-forcing/analysis/confirm_ne21_ne23.py",
                     ["calendar", "activity_bins", "chat_core", "exposure", "roster", "kicks"],
                     {"mode": tag, "segments": segs, "sensitivity": sens, "off": off, "extension": ext,
                      "boot_hawkes": NBOOT_HAWKES, "boot_param": NBOOT_PARAM})
    for k, v in V.items():
        print(k, "->", v.get("verdict", v.get("verdict_K")), flush=True)


if __name__ == "__main__":
    main()
