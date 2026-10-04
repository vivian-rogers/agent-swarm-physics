"""H59 confirmatory script (frozen 2026-10-04). NOT RUN in round 1.

Target: the #51 tail (2026-09-07 -> 09-21, locked holdout). Classes there: A, Hu, Hm (no nudges after 08-20).
#45 is not used: H04's executed run there is in the same estimator family (kick response), so the reuse policy blocks it.

Frozen from the G51 head (data/processed/H59-one-lever-model/G51/results.json, round 1):
  theta = 72.7 deg; K = (1, 0.44, 0.17, 0.10, 0.06, 0.09); triples (kappa, h): A (0.141, 3.774), Hu (-0.125, 1.770),
  Hm (0.595, 4.394).
Claims ("one lever at the read-out; class-specific tails"):
  C1  read-out transfer, A: with theta and K frozen, refitting only (kappa_A, h_A) (5-fold day CV) keeps >= 0.7 of the
      class-specific free fit's skill on early rows (A read 0-2 calls ago). Head: 0.77.
  C2  frozen-parameter transfer: the frozen head model predicts the tail's kicked transitions with >= 0.8 of the skill
      of a 5-fold day-CV refit of the one-lever model on the tail.
  C3  A triple stability: tail fit h_A in [2.5, 5.0] and kappa_A in [-0.05, 0.35].
  C4  no inbox decay for mentions: A stale/fresh lag-0 amplitude ratio in [0.8, 1.25].
  C5  tails are class-specific (round-1 finding): full-row A transfer T = S_H59 / S_free < 0.8.
"One lever at the read-out" is confirmed if C1, C2 and C3 pass; C4, C5 are reported.

Guards: --confirm and env H59_CONFIRM=1 and --disclosed (reuse of the #51 tail disclosed in the cards and LOG.md first;
the holdout ledger lists many planned users: H39 and H30 plan behavior-state / kick-response statistics there).
--dry-run uses non-holdout stand-in days (2026-08-24 -> 09-06; in-sample, pipeline check only).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h59lib as L  # noqa: E402
import run_period as RP  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
FROZEN = {"theta_deg": 72.7, "K": [1.0, 0.44, 0.17, 0.10, 0.06, 0.09],
          "triples": {"A": (0.141, 3.774), "Hu": (-0.125, 1.770), "Hm": (0.595, 4.394)}}
TAIL = ("2026-09-07", "2026-09-21")
STANDIN = ("2026-08-24", "2026-09-07")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def tail_transitions() -> pl.DataFrame:
    h43 = _load("h43build_ro", ROOT / "hypotheses/H43-kick-refractory-window/scheme/build.py")
    calls, _ = h43.calls_frame(include_holdout=True, goal_nos=[51])
    calls = calls.filter((pl.col("pt_date") >= TAIL[0]) & (pl.col("pt_date") < TAIL[1]))
    b = _load("h59build", ROOT / "hypotheses/H59-one-lever-model/scheme/build.py")
    tr, _ = b.build([51], calls=calls)
    return tr


def frozen_B(classes):
    th = np.radians(FROZEN["theta_deg"])
    u, _ = L.u_vec(th)
    B = np.zeros((len(L.CLASSES), L.NL, 3, 3))
    for c in classes:
        k, h = FROZEN["triples"][c]
        core = k + h * (u[None, :] - u[:, None]) / 2
        np.fill_diagonal(core, 0)
        B[L.CLASSES.index(c)] = np.array(FROZEN["K"])[:, None, None] * core[None]
    return B


def evaluate(t: pl.DataFrame) -> dict:
    d = L.arrays(t)
    b = L.baseline(d)
    kd = L.KD(d, b["off"])
    cls = [c for c in L.powered(d) if L.CLASSES[c] in FROZEN["triples"]]
    names = [L.CLASSES[c] for c in cls]
    w1 = np.ones(kd.m)
    Bfz = frozen_B(names)
    out = {"classes": names, "n_days": len(d["days"])}
    a = L.CLASSES.index("A")
    # C1: A, frozen theta/K, others frozen; CV of (kappa, h) vs free on early rows
    others = np.zeros_like(Bfz)
    for c in cls:
        if c != a:
            others[c] = Bfz[c]
    extra = L.contrib(kd, others)
    ex = kd.D[:, a, :].any(1)
    early = kd.D[:, a, 0:3].any(1)
    fold = kd.day % 5
    ll = {m: np.zeros(kd.m) for m in ("M0", "lever", "free")}
    _, _, ll0 = kd.nll_grad(np.zeros_like(Bfz), w1, extra)
    ml = L.Lever([a], "lever")
    fx = {i: FROZEN["K"][i + 1] for i in range(5)}
    fx[5] = np.radians(FROZEN["theta_deg"])
    for f in range(5):
        tr = (ex & (fold != f)).astype(float)
        te = ex & (fold == f)
        if tr.sum() < 20 or not te.any():
            continue
        v = L.fit_param(kd, ml, tr, extra, fixed=fx)
        ll["lever"][te] = kd.nll_grad(ml.B(v), w1, extra)[2][te]
        Bf = L.fit_free(kd, a, tr, extra)
        ll["free"][te] = kd.nll_grad(Bf, w1, extra)[2][te]
    S = {m: float((ll[m] - ll0)[ex & early].sum()) for m in ("lever", "free")}
    Sall = {m: float((ll[m] - ll0)[ex].sum()) for m in ("lever", "free")}
    r1 = S["lever"] / S["free"] if S["free"] > 0 else None
    out["C1"] = {"S_early": S, "ratio": r1, "pass": r1 is not None and r1 >= 0.7}
    T5 = Sall["lever"] / Sall["free"] if Sall["free"] > 0 else None
    out["C5"] = {"S_all": Sall, "T": T5, "pass": T5 is not None and T5 < 0.8}
    # C2: frozen model vs tail CV refit of the full one-lever model
    _, _, llz = kd.nll_grad(np.zeros_like(Bfz), w1)
    _, _, llf = kd.nll_grad(Bfz, w1)
    lq = L.Lever(cls, "lever")
    llcv = np.zeros(kd.m)
    for f in range(5):
        v = L.fit_param(kd, lq, (fold != f).astype(float))
        te = fold == f
        llcv[te] = kd.nll_grad(lq.B(v), w1)[2][te]
    s_f, s_cv = float((llf - llz).sum()), float((llcv - llz).sum())
    r2 = s_f / s_cv if s_cv > 0 else None
    out["C2"] = {"S_frozen": s_f, "S_tail_cv": s_cv, "ratio": r2, "pass": r2 is not None and r2 >= 0.8}
    # C3: tail triple of A
    tri, v, lv = L.triples(kd, cls, nboot=0)
    kA, hA = tri["A"]["kappa"]["est"], tri["A"]["h"]["est"]
    out["C3"] = {"kappa_A": kA, "h_A": hA, "theta_deg": tri["theta_deg"]["est"],
                 "pass": (2.5 <= hA <= 5.0) and (-0.05 <= kA <= 0.35)}
    # C4: stale/fresh for A
    age = d["age0"][kd.idx, a]
    rec = kd.D[:, a, 0] > 0
    med = np.nanmedian(age[rec])
    s, _ = RP.amp_groups(kd, lv.B(v), a, [rec & (age <= med), rec & (age > med)])
    ratio = float(s[1] / s[0])
    out["C4"] = {"ratio": ratio, "pass": 0.8 <= ratio <= 1.25}
    out["confirmed_one_lever_at_readout"] = bool(out["C1"]["pass"] and out["C2"]["pass"] and out["C3"]["pass"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--disclosed", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        t = L.load(51).filter((pl.col("pt_date") >= STANDIN[0]) & (pl.col("pt_date") < STANDIN[1]))
        res = evaluate(t)
        od = L.OUT / "confirm_dryrun"
        od.mkdir(parents=True, exist_ok=True)
        (od / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps(res, default=float))
        return
    if not (a.confirm and os.environ.get("H59_CONFIRM") == "1" and a.disclosed):
        sys.exit("refusing: confirmatory run needs --confirm, H59_CONFIRM=1 and --disclosed (see docstring)")
    import holdout_ledger as HL
    chk = HL.check("H59", "#51-tail", "behavior states", ["kick_response", "behavior_states"])
    print(json.dumps({k: chk[k] for k in ("allowed", "needs_disclosure")}))
    if not chk["allowed"]:
        sys.exit("holdout ledger: a prior run on the #51 tail used the same estimator family")
    res = evaluate(tail_transitions())
    od = L.OUT / "confirm"
    od.mkdir(parents=True, exist_ok=True)
    (od / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, default=float))


if __name__ == "__main__":
    main()
