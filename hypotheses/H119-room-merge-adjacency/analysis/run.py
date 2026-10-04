"""H119 exploratory round 1: does the fitted talk-spin coupling follow the known adjacency (NE42 + switch events)?

NE42 (native): E1 class model per week (#39, #40, #41) and per day; full-J block averages per week; E2 read vs
in-flight per week; relabel null for the merge DiD. Switch events (replication): E1 class model per side with pair
classes from minute-level co-location (fixed / on / off) and the switch contrast S.
Holdout days raise in ki_talk (never loaded).

Usage: uv run python hypotheses/H119-room-merge-adjacency/analysis/run.py [--relabel 499] [--skip-e2]
Outputs: data/processed/H119-room-merge-adjacency/{ne42_weeks.json, ne42_days.parquet, ne42_fullJ.parquet,
         e2_ne42.parquet, switch_units.parquet, relabel.parquet, _provenance.json}
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
from scipy.stats import mannwhitneyu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(HERE))
import ki_talk as K  # noqa: E402
import h119lib as L  # noqa: E402

OUT = K.ROOT / "data/processed/H119-room-merge-adjacency"
Z = 1.959964

SWITCHES = {  # name: (before, after, folder, goal of the after side)
    "move_0402": (["2026-03-31", "2026-04-01"], ["2026-04-02", "2026-04-03"], "G38", 38),
    "move_0427": (["2026-04-23", "2026-04-24"], ["2026-04-27", "2026-04-28"], "G39", 39),
    "move_0525": (["2026-05-21", "2026-05-22"], ["2026-05-26", "2026-05-27"], "G44", 44),
    "focus_off": (["2026-08-03", "2026-08-04"], ["2026-08-05", "2026-08-06"], "G51", 51),
    "focus_on": (["2026-08-20", "2026-08-21"], ["2026-08-25", "2026-08-26"], "G51", 51),   # Amendment 0: 08-24 return at 18:10 UTC
}


def ne42_setup():
    alld = [d for w in L.NE42_WEEKS.values() for d in w]
    sp = K.day_spins(alld)
    ag = K.eligible(sp, list(L.NE42_WEEKS.values()))
    cls = L.ne42_classes(ag)
    st = {w: K.stack(sp, days, ag) for w, days in L.NE42_WEEKS.items()}
    return sp, ag, cls, st


def coloc_check(st, ag, cls):
    """Minute-level co-location share per class and week (sanity check of the designated classes)."""
    out = {}
    for w, s in st.items():
        sh = K.coloc_share(K.colocation(s, ag))
        for c, nm in L.CLASS_NAMES.items():
            m = cls == c
            out[f"{nm}_{w}"] = float(sh[m].mean()) if m.any() else np.nan
    return out


def week_fits(st, cls):
    return {w: K.fit_e1_class(s, cls, L.CLASS_IDS) for w, s in st.items()}


def full_J_blocks(st, cls):
    rows = []
    for w, s in st.items():
        J, SE, cv = K.fit_e1_full(s, "block")
        Js, Vs = K.sym(J, SE)
        for c, nm in L.CLASS_NAMES.items():
            m = (cls == c) & np.isfinite(J)
            if not m.any():
                continue
            iu = np.triu_indices(len(cls), 1)
            mu = m[iu]
            v = Js[iu][mu]
            se = float(np.sqrt(Vs[iu][mu].sum()) / mu.sum())
            rows.append({"week": w, "class": nm, "Jsym_mean": float(v.mean()), "se": se, "n_pairs": int(mu.sum()),
                         "Jdir_mean": float(J[m].mean())})
    return pl.DataFrame(rows)


def daily(st, cls):
    rows = []
    for w, s in st.items():
        for day in s:
            try:
                f = K.fit_e1_class([day], cls, L.CLASS_IDS)
                rows.append({"week": w, "day": day[0], "Jw": float(f["J"][0]), "Jx": float(f["J"][1]),
                             "se_w": float(f["se"][0]), "se_x": float(f["se"][1]),
                             "Jg5r": float(f["J"][2]), "Jg5b": float(f["J"][3])})
            except Exception as ex:  # noqa: BLE001
                rows.append({"week": w, "day": day[0], "error": repr(ex)[:100]})
    return pl.DataFrame(rows, infer_schema_length=None)


def e2_week(days, ag, cls):
    calls = K.calls_frame(days, ag)
    msgs = K.messages_frame(days)
    R, U, Us = K.e2_counts(calls, msgs, ag)
    ai = {a: i for i, a in enumerate(ag)}
    fn = lambda i, j: int(cls[ai[i], ai[j]]) if (i in ai and j in ai) else -1  # noqa: E731
    y, X, g, A = K.e2_design(calls, R, U, ag, fn, L.CLASS_IDS)
    r = K.fit_e2(y, X, g, A, len(L.CLASS_IDS))
    out = L.e2_contrasts(r)
    out["n_calls"] = int(len(y)); out["talk_rate"] = float(y.mean())
    # same-room-only in-flight variant
    y2, X2, g2, A2 = K.e2_design(calls, R, Us, ag, fn, L.CLASS_IDS)
    r2 = K.fit_e2(y2, X2, g2, A2, len(L.CLASS_IDS))
    o2 = L.e2_contrasts(r2)
    for k in ("JU_cross", "JU_cross_lo", "JU_cross_hi", "CRU_cross", "CRU_cross_lo", "CRU_cross_hi", "JU_within",
              "CRU_within", "CRU_within_lo", "CRU_within_hi"):
        out[f"sameroomU_{k}"] = o2[k]
    return out


_RL = {}


def _rl_init():
    sp, ag, cls, st = ne42_setup()
    _RL.update({"ag": ag, "cls": cls, "st": st})


def _rl_job(seed):
    """Random 4-vs-rest partition of the non-GPT-5 agents (sizes kept); GPT-5 classes kept as they are."""
    rng = np.random.default_rng(seed)
    ag, cls, st = _RL["ag"], _RL["cls"], _RL["st"]
    names = K.roster_names()
    core = [n for n, a in enumerate(ag) if L.group_of(names[a]) in ("best", "rest")]
    nbest = sum(L.group_of(names[ag[n]]) == "best" for n in core)
    pick = set(rng.choice(core, nbest, replace=False).tolist())
    c2 = cls.copy()
    for i in core:
        for j in core:
            if i != j:
                c2[i, j] = 0 if ((i in pick) == (j in pick)) else 1
    f = week_fits(st, c2)
    c = L.ne42_contrasts(f)
    return {"seed": seed, "M": c["M"], "MD": c["MD"], "Rm": c["Rm"]}


def switch_unit(name, bef, aft, do_e2=True):
    spins = K.day_spins(bef + aft)
    ag = K.eligible(spins, [bef, aft])
    sb, sa = K.stack(spins, bef, ag), K.stack(spins, aft, ag)
    cb = K.coloc_share(K.colocation(sb, ag)); ca = K.coloc_share(K.colocation(sa, ag))
    N = len(ag)
    cls = L.switch_classes(cb, ca)
    ids = [0, 1, 2, 3]
    fb = K.fit_e1_class(sb, cls, ids); fa = K.fit_e1_class(sa, cls, ids)
    row = {"name": name, "n_agents": N, "n_fixed": int((cls == 0).sum()), "n_on": int((cls == 1).sum()),
           "n_off": int((cls == 2).sum()), "n_never": int((cls == 3).sum())}
    row.update(L.switch_contrast(fb, fa, row["n_on"], row["n_off"]))
    if do_e2:
        # read vs in-flight for the switched pairs on the side where they share a room (on: after; off: before)
        ai = {a: i for i, a in enumerate(ag)}
        for arm, code, days in (("on", 1, aft), ("off", 2, bef)):
            if row[f"n_{arm}"] == 0:
                continue
            try:
                calls = K.calls_frame(days, ag)
                msgs = K.messages_frame(days)
                R, U, Us = K.e2_counts(calls, msgs, ag)
                fn = lambda i, j, c=code: (0 if cls[ai[i], ai[j]] == 0 else 1 if cls[ai[i], ai[j]] == c else -1)  # noqa: E731
                y, X, g, A = K.e2_design(calls, R, U, ag, fn, [0, 1])
                r = K.fit_e2(y, X, g, A, 2)
                V = r["V"]
                jr, ju = r["JR"][1], r["JU"][1]
                row[f"e2_{arm}_JR"], row[f"e2_{arm}_JU"] = float(jr), float(ju)
                row[f"e2_{arm}_nzR"] = int(r["nzR"][1])
                if np.isfinite(jr) and np.isfinite(ju):
                    se = float(np.sqrt(V[1, 1] + V[3, 3] - 2 * V[1, 3]))
                    row[f"e2_{arm}_CRU"], row[f"e2_{arm}_CRU_lo"] = float(jr - ju), float(jr - ju - Z * se)
                    row[f"e2_{arm}_CRU_hi"] = float(jr - ju + Z * se)
                row[f"e2_{arm}_JR_fixed"], row[f"e2_{arm}_JU_fixed"] = float(r["JR"][0]), float(r["JU"][0])
            except Exception as ex:  # noqa: BLE001
                row[f"e2_{arm}_error"] = repr(ex)[:150]
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--relabel", type=int, default=499)
    ap.add_argument("--skip-e2", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t = time.time()
    sp, ag, cls, st = ne42_setup()
    names = K.roster_names()
    res = {"agents": [names[x] for x in ag], "n_agents": len(ag),
           "class_counts": {nm: int((cls == c).sum()) for c, nm in L.CLASS_NAMES.items()}}
    res["coloc_check"] = coloc_check(st, ag, cls)
    wf = week_fits(st, cls)
    res["contrasts"] = L.ne42_contrasts(wf)
    res["week_fit_conv"] = {w: bool(f["conv"]) for w, f in wf.items()}
    print("NE42 class model done", round(time.time() - t), flush=True)
    full_J_blocks(st, cls).write_parquet(OUT / "ne42_fullJ.parquet")
    dd = daily(st, cls)
    dd.write_parquet(OUT / "ne42_days.parquet")
    merged = dd.filter(pl.col("week") == "40")["Jx"].to_numpy()
    unmerged = dd.filter(pl.col("week") != "40")["Jx"].to_numpy()
    res["daily_mw_p"] = float(mannwhitneyu(merged, unmerged, alternative="greater").pvalue)
    res["daily_Jx_merged_mean"] = float(merged.mean()); res["daily_Jx_unmerged_mean"] = float(unmerged.mean())
    d39 = dd.filter(pl.col("week") == "39")["Jx"].to_numpy()
    res["daily_Jx_0504"] = float(dd.filter(pl.col("day") == "2026-05-04")["Jx"][0])
    res["daily_Jx_39_range"] = [float(d39.min()), float(d39.max())]
    print("daily done", round(time.time() - t), flush=True)
    if not a.skip_e2:
        e2rows = []
        for w, days in L.NE42_WEEKS.items():
            o = e2_week(days, ag, cls)
            o["week"] = w
            e2rows.append(o)
        pl.DataFrame(e2rows, infer_schema_length=None).write_parquet(OUT / "e2_ne42.parquet")
        print("E2 done", round(time.time() - t), flush=True)
    sw = [switch_unit(n, b, a_, not a.skip_e2) for n, (b, a_, f, g) in SWITCHES.items()]
    pl.DataFrame(sw, infer_schema_length=None).write_parquet(OUT / "switch_units.parquet")
    print("switch units done", round(time.time() - t), flush=True)
    if a.relabel:
        with ProcessPoolExecutor(2, initializer=_rl_init) as ex:
            rl = list(ex.map(_rl_job, range(a.relabel), chunksize=8))
        rl = pl.DataFrame(rl)
        rl.write_parquet(OUT / "relabel.parquet")
        c = res["contrasts"]
        for k in ("M", "MD", "Rm"):
            v = rl[k].to_numpy()
            res[f"relabel_p_{k}"] = float((1 + (v >= c[k]).sum()) / (1 + len(v)))
        print("relabel done", round(time.time() - t), flush=True)
    (OUT / "ne42_weeks.json").write_text(json.dumps(res, indent=1, default=float))
    sys.path.insert(0, str(K.ROOT / "infra/shared"))
    from common import git_commit
    (OUT / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H119-room-merge-adjacency/analysis/run.py", "git_commit": git_commit(),
        "inputs": [{"source": "shared", "tables": ["activity_bins_fixed", "calendar", "period_units", "roster",
                                                     "rooms_timeline", "context_ledger_turns", "call_windows",
                                                     "chat_core"]}],
        "params": {"box": K.BOX, "block_min": K.BLOCK_MIN, "lam": K.LAM, "min_talk": K.MIN_TALK,
                   "relabel": a.relabel},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "agents"}, indent=1, default=float))


if __name__ == "__main__":
    main()
