"""H117 exploratory round 1: coupling-shift test at mid-goal field steps (replication + natives) against placebo splits.

For every split (documented step or placebo day boundary, k = 2 active days per side):
  E1 KI-5 block fits per side (per-recipient logistic, block fields, cluster-robust SEs) -> Q, D_F over fixed pairs;
  E1-naive -> Q_naive; field first stage F; switched-pair Q (where switched pairs exist); row Q per agent;
  E2 (regime III) per-recipient read-gated inflow J^R_i and same-room in-flight J^U_i -> Q_R and mean J^R - J^U.
Placebo pool: every k = 2 window inside one non-holdout period_units unit of the same regime (no documented step
inside; 51g windows may not straddle 2026-08-20). Holdout days raise in ki_talk (never loaded).

Usage: uv run python hypotheses/H117-coupling-invariant-rule-reset/analysis/run.py [--no-e2] [--only NE17,...]
Outputs: data/processed/H117-coupling-invariant-rule-reset/{splits.parquet, rowq.parquet, J/*.npz, _provenance.json}
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import ki_talk as K  # noqa: E402

OUT = K.ROOT / "data/processed/H117-coupling-invariant-rule-reset"
KDAYS = 2
FIX_HI, SW_LO = 0.90, 0.20   # Amendment 0 (co-location thresholds; the card's 0.95 / 0.05 dropped movers' partial days)

STEPS = {  # name: (before, after, regime, role, folder, goal)
    "NE06": (["2025-11-18", "2025-11-19"], ["2025-11-20", "2025-11-21"], "I", "replication", "NE06", 20),
    "NE07": (["2025-12-02", "2025-12-03"], ["2025-12-04", "2025-12-05"], "I", "replication", "NE07", 21),
    "NE16": (["2026-03-24", "2026-03-25"], ["2026-03-26", "2026-03-27"], "III", "replication", "NE16", 36),
    "NE17": (["2026-04-10", "2026-04-13"], ["2026-04-14", "2026-04-15"], "III", "replication", "NE17", 38),
    "NE38": (["2026-07-27", "2026-07-28"], ["2026-07-29", "2026-07-30"], "III", "replication", "NE38", 51),
    "NE43a": (["2026-08-03", "2026-08-04"], ["2026-08-05", "2026-08-06"], "III", "replication", "NE43", 51),
    "NE43b": (["2026-08-18", "2026-08-19"], ["2026-08-21", "2026-08-24"], "III", "replication", "NE43", 51),
    "NE36": (["2026-03-31", "2026-04-01"], ["2026-04-02", "2026-04-03"], "III", "native", "NE36", 38),
    "G42": (["2026-05-14", "2026-05-15"], ["2026-05-18", "2026-05-19"], "III", "native", "G42", 42),
}
STEPS_K3 = {  # Amendment 1: declared k = 3 sensitivity for the #51 steps
    "NE38_k3": (["2026-07-24", "2026-07-27", "2026-07-28"], ["2026-07-29", "2026-07-30", "2026-07-31"], "III",
                "replication", "NE38", 51),
    "NE43a_k3": (["2026-07-31", "2026-08-03", "2026-08-04"], ["2026-08-05", "2026-08-06", "2026-08-07"], "III",
                 "replication", "NE43", 51),
}
NE43B_DAY = "2026-08-20"


def placebo_windows(regime: str, k: int = KDAYS) -> list:
    pu = pl.read_parquet(K.SH / "period_units.parquet").filter(~pl.col("holdout") & (pl.col("regime") == regime))
    out = []
    for r in pu.iter_rows(named=True):
        days = sorted(r["days"])
        for b in range(k, len(days) - k + 1):
            bef, aft = days[b - k:b], days[b:b + k]
            win = bef + aft
            if any(d == NE43B_DAY for d in win) or (min(win) < NE43B_DAY < max(win)):
                continue
            out.append({"name": f"pl{k}_{r['unit_id']}_{aft[0]}", "before": bef, "after": aft, "regime": regime,
                        "unit": r["unit_id"], "goal": int(r["goal_no"]), "k": k})
    return out


def e2_inflow(days, agents):
    """Per recipient: J^R (read, same room, matched window), J^U (same-room in-flight) with SEs."""
    calls = K.calls_frame(days, agents)
    msgs = K.messages_frame(days)
    senders = sorted(set(msgs["agent"].to_list()))
    R, U, Us = K.e2_counts(calls, msgs, senders)
    rec = calls["agent"].to_numpy()
    y_all = calls["talk"].to_numpy().astype(float)
    tday = calls["pt_date"].to_numpy()
    tmin = (calls["tc_us"].to_numpy() // 60_000_000) // K.BLOCK_MIN
    res = {}
    for a in agents:
        sel = rec == a
        if sel.sum() < 200 or y_all[sel].sum() < 10:
            continue
        y = y_all[sel]
        yp = np.r_[0.0, y[:-1]]
        XR = np.log1p(R[sel]).sum(1); XU = np.log1p(Us[sel]).sum(1)
        if (XR > 0).sum() < 30 or (XU > 0).sum() < 30:
            continue
        key = np.array([f"{d}|{m}" for d, m in zip(tday[sel], tmin[sel])])
        _, g = np.unique(key, return_inverse=True)
        X = np.column_stack([np.ones(len(y)), yp, XR, XU])
        r = K.fit_logit_fe(y, X, g, np.array([0.0, K.LAM, K.LAM, K.LAM]), lam_fe=K.LAM)
        res[a] = (r["b"][2], r["se"][2], r["b"][3], r["se"][3], int(sel.sum()))
    return res


def run_split(sp: dict, do_e2: bool = True, save_J: bool = False, focus: dict | None = None) -> dict:
    bef, aft = sp["before"], sp["after"]
    spins = K.day_spins(bef + aft)
    ag = K.eligible(spins, [bef, aft])
    row = {"name": sp["name"], "regime": sp["regime"], "unit": sp.get("unit"), "goal": sp.get("goal"), "k": sp.get("k", 2),
           "kind": sp.get("kind", "placebo"), "n_agents": len(ag)}
    if len(ag) < 4:
        row["skip"] = "fewer than 4 eligible agents"
        return row
    sb, sa = K.stack(spins, bef, ag), K.stack(spins, aft, ag)
    cb = K.coloc_share(K.colocation(sb, ag)); ca = K.coloc_share(K.colocation(sa, ag))
    N = len(ag)
    off = ~np.eye(N, dtype=bool)
    fixed = off & (cb >= FIX_HI) & (ca >= FIX_HI)
    switched = off & (((cb >= FIX_HI) & (ca <= SW_LO)) | ((cb <= SW_LO) & (ca >= FIX_HI)))
    Jb, SEb, cvb = K.fit_e1_full(sb, "block")
    Ja, SEa, cva = K.fit_e1_full(sa, "block")
    q = K.q_stats(Ja, SEa, Jb, SEb, fixed)
    row.update({"Q": q["Q"], "DF": q["DF"], "n_pairs": q["n_pairs"], "Jbar_b": q.get("Jbar_b"),
                "Jbar_a": q.get("Jbar_a"), "conv": bool(cvb.all() and cva.all())})
    qs = K.q_stats(Ja, SEa, Jb, SEb, switched)
    row.update({"Q_switched": qs["Q"], "n_switched": qs["n_pairs"]})
    Jnb, SEnb, _ = K.fit_e1_full(sb, "naive")
    Jna, SEna, _ = K.fit_e1_full(sa, "naive")
    row["Q_naive"] = K.q_stats(Jna, SEna, Jnb, SEnb, fixed)["Q"]
    mb, smb = K.fit_e1_mf(sb, fixed); ma, sma = K.fit_e1_mf(sa, fixed)
    row["Q_mf"] = float(np.nanmean((ma - mb) ** 2 / (sma ** 2 + smb ** 2)))
    row["mf_b"] = float(np.nanmean(mb)); row["mf_a"] = float(np.nanmean(ma))
    hb, seb = K.field_logit(sb); ha, sea = K.field_logit(sa)
    row["F"] = K.f_stat(ha, sea, hb, seb)
    row["dh_mean"] = float(np.mean(ha - hb))
    row["talk_rate_b"] = float(np.mean(1 / (1 + np.exp(-hb))))
    # row Q per agent (fixed pairs that involve agent k)
    rowq = []
    zsq = None
    Jsa, Vsa = K.sym(Ja, SEa); Jsb, Vsb = K.sym(Jb, SEb)
    zsq = (Jsa - Jsb) ** 2 / (Vsa + Vsb)
    for n, a in enumerate(ag):
        m = fixed[n]
        rowq.append({"name": sp["name"], "agent": int(a), "rowQ": float(np.nanmean(zsq[n][m])) if m.any() else np.nan,
                     "n_pairs": int(m.sum()), "dh": float(ha[n] - hb[n]),
                     "z_dh": float((ha[n] - hb[n]) / np.sqrt(sea[n] ** 2 + seb[n] ** 2))})
    row["_rowq"] = rowq
    if focus:
        for lab, a in focus.items():
            if a in ag:
                n = ag.index(a)
                m = switched[n]
                row[f"Q_sw_{lab}"] = float(np.nanmean(zsq[n][m])) if m.any() else np.nan
                row[f"n_sw_{lab}"] = int(m.sum())
    if do_e2 and sp["regime"] != "I":
        try:
            eb, ea = e2_inflow(bef, ag), e2_inflow(aft, ag)
            common = sorted(set(eb) & set(ea))
            if len(common) >= 3:
                d = np.array([ea[a][0] - eb[a][0] for a in common])
                v = np.array([ea[a][1] ** 2 + eb[a][1] ** 2 for a in common])
                row["Q_R"] = float(np.mean(d ** 2 / v))
                row["n_R"] = len(common)
                for lab, e in (("b", eb), ("a", ea)):
                    jr = np.array([e[a][0] for a in common]); ju = np.array([e[a][2] for a in common])
                    row[f"JR_{lab}"] = float(jr.mean()); row[f"JU_{lab}"] = float(ju.mean())
                    row[f"JRmJU_{lab}"] = float((jr - ju).mean())
                    row[f"JRmJU_se_{lab}"] = float((jr - ju).std(ddof=1) / np.sqrt(len(common)))
        except Exception as ex:  # noqa: BLE001
            row["e2_error"] = repr(ex)[:200]
    if save_J:
        (OUT / "J").mkdir(parents=True, exist_ok=True)
        np.savez_compressed(OUT / "J" / f"{sp['name']}.npz", agents=np.array(ag), Jb=Jb, SEb=SEb, Ja=Ja, SEa=SEa,
                            Jnb=Jnb, Jna=Jna, hb=hb, ha=ha, seb=seb, sea=sea, cb=cb, ca=ca, fixed=fixed,
                            switched=switched)
    return row


def _job(args):
    sp, do_e2, save, focus = args
    t = time.time()
    try:
        r = run_split(sp, do_e2, save, focus)
    except K.HoldoutError:
        raise
    except Exception as ex:  # noqa: BLE001
        r = {"name": sp["name"], "regime": sp["regime"], "kind": sp.get("kind", "placebo"), "error": repr(ex)[:300]}
    r["sec"] = round(time.time() - t, 1)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-e2", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--no-placebo", action="store_true")
    a = ap.parse_args()
    names = K.roster_names()
    rid = {v: k for k, v in names.items()}
    focus_ne43 = {"gemini25": rid["Gemini 2.5 Pro"], "opus48": rid["Claude Opus 4.8"]}
    focus_ne36 = {"sonnet46": rid["Claude Sonnet 4.6"]}
    jobs = []
    for nm, (bef, aft, reg, role, folder, goal) in {**STEPS, **STEPS_K3}.items():
        if a.only and nm not in a.only.split(","):
            continue
        focus = focus_ne43 if nm == "NE43a" else focus_ne36 if nm == "NE36" else None
        jobs.append(({"name": nm, "before": bef, "after": aft, "regime": reg, "kind": role, "goal": goal,
                      "k": len(bef)},
                     not a.no_e2, True, focus))
    if not a.no_placebo:
        for reg in ("I", "III"):
            for sp in placebo_windows(reg):
                jobs.append((sp, not a.no_e2, False, None))
        for sp in placebo_windows("III", 3):
            jobs.append((sp, not a.no_e2, False, None))
    print(f"{len(jobs)} splits", flush=True)
    t = time.time()
    with ProcessPoolExecutor(2) as ex:
        rows = list(ex.map(_job, jobs))
    rowq = [q for r in rows for q in r.pop("_rowq", [])]
    OUT.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    tag = "" if not a.only else "_only"
    df.write_parquet(OUT / f"splits{tag}.parquet")
    if rowq:
        pl.DataFrame(rowq).write_parquet(OUT / f"rowq{tag}.parquet")
    sys.path.insert(0, str(K.ROOT / "infra/shared"))
    from common import git_commit
    (OUT / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H117-coupling-invariant-rule-reset/analysis/run.py",
        "git_commit": git_commit(),
        "inputs": [{"source": "shared", "tables": ["activity_bins_fixed", "calendar", "period_units", "roster",
                                                     "rooms_timeline", "context_ledger_turns", "call_windows",
                                                     "chat_core"]}],
        "params": {"k_days": KDAYS, "box": K.BOX, "block_min": K.BLOCK_MIN, "lam": K.LAM, "min_talk": K.MIN_TALK},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}, indent=1))
    print(f"done in {time.time() - t:.0f} s")
    with pl.Config(tbl_rows=200, tbl_cols=30, tbl_width_chars=250):
        print(df.filter(pl.col("kind") != "placebo").select([c for c in ("name", "n_agents", "n_pairs", "Q", "DF", "Q_naive", "F", "Q_switched", "Q_R") if c in df.columns]))


if __name__ == "__main__":
    main()
