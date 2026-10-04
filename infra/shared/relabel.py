"""Room-relabel nulls for statistics that compare two periods (room remanence, carry-over of a room difference).

Moved from H100 (`analysis/h100lib.remanence`, the O7 null; round-3 consolidation, STANDARDS §8, 2026-10-04).
Single-period relabels stay in `nulls.room_relabel`.

Why a joint relabel. A two-period statistic such as room remanence R = cos(Delta_P1, Delta_P2) (Delta = room-mean
difference of agent vectors) is positive without any room memory whenever (a) the same agents sit in the same rooms in
both periods and (b) each agent carries a constant that the preprocessing did not fully remove (a leftover agent
constant). Relabelling the two periods independently breaks (a) and centres the null near 0, so the test rejects at
far above its nominal size (H100: median R ~ 0.15 in null worlds). The joint relabel draws each period's partition at
random but gives an agent present in both periods the same pseudo-room in both, so the agent part of R stays in the
null. H100 measured size 0.025 at alpha 0.05 with it.

Rule (H100 verbatim, `joint_relabel`): l1 = permutation of period-1 labels; l2 = permutation of period-2 labels; then
every agent present in both periods gets l2 := its l1. Period-2 room sizes can therefore drift from the observed ones;
draws where a period-2 room ends up empty are skipped. The two-sided p is (1 + #{|R_null| >= |R|}) / (1 + n_null)
with n_null the requested number of draws (H100's convention).

Functions:
  joint_relabel(lab1, ag1, lab2, ag2, rng)          -> (l1, l2)
  independent_relabel(lab1, lab2, rng)             -> (l1, l2)   (the biased null; for comparison only)
  room_diff_cos(v1, l1, v2, l2, a, b)              -> cos of the two room-difference vectors
  remanence_test(v1, lab1, ag1, v2, lab2, ag2, n_null, seed, joint=True)   -> H100's remanence() result dict
  size_test(...)                                   -> synthetic size of both nulls (no room memory planted)

Verify: uv run python infra/shared/relabel.py --verify
  (1) remanence_test reproduces h100lib.remanence (R, null sd, z, p) on H100's real tables for every consecutive
      same-name period pair it reports (read-only import); (2) synthetic size: joint relabel within the binomial band
      around 0.05 or below; independent relabel inflated.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BEST, REST = 2, 3


def joint_relabel(lab1, ag1, lab2, ag2, rng) -> tuple[np.ndarray, np.ndarray]:
    """H100's joint relabel: independent permutations, then shared agents copy their period-1 pseudo-room."""
    l1 = rng.permutation(np.asarray(lab1))
    l2 = rng.permutation(np.asarray(lab2))
    pos2 = {a: j for j, a in enumerate(ag2)}
    for i, a in enumerate(ag1):
        if a in pos2:
            l2[pos2[a]] = l1[i]
    return l1, l2


def independent_relabel(lab1, lab2, rng) -> tuple[np.ndarray, np.ndarray]:
    """Independent permutations of the two periods (biased for two-period statistics; see the module docstring)."""
    return rng.permutation(np.asarray(lab1)), rng.permutation(np.asarray(lab2))


def room_diff_cos(v1, l1, v2, l2, a: int = BEST, b: int = REST) -> float:
    d1 = v1[l1 == a].mean(0) - v1[l1 == b].mean(0)
    d2 = v2[l2 == a].mean(0) - v2[l2 == b].mean(0)
    return float(d1 @ d2 / np.linalg.norm(d1) / np.linalg.norm(d2))


def remanence_test(v1, lab1, ag1, v2, lab2, ag2, n_null: int = 2000, seed: int = 0, joint: bool = True,
                   a: int = BEST, b: int = REST) -> dict:
    """R = cos(Delta_1, Delta_2) and its relabel null. v*: agent x d vectors (rows aligned with ag*), lab*: room
    codes. joint=True is H100's O7 null (same random stream as h100lib.remanence for the same seed)."""
    lab1, lab2 = np.asarray(lab1), np.asarray(lab2)
    R = room_diff_cos(v1, lab1, v2, lab2, a, b)
    rng = np.random.default_rng(seed)
    nul = []
    for _ in range(n_null):
        l1, l2 = joint_relabel(lab1, ag1, lab2, ag2, rng) if joint else independent_relabel(lab1, lab2, rng)
        if (l2 == a).sum() == 0 or (l2 == b).sum() == 0:
            continue
        nul.append(room_diff_cos(v1, l1, v2, l2, a, b))
    nul = np.array(nul)
    return {"R": R, "null_sd": float(nul.std()), "z": float((R - nul.mean()) / nul.std()),
            "p_two": float((1 + (np.abs(nul) >= abs(R)).sum()) / (1 + n_null)), "null_mean": float(nul.mean()),
            "n_null_kept": int(len(nul))}


def size_test(worlds: int = 300, n_null: int = 199, n_agents: int = 12, stay: float = 0.85, d: int = 32,
              leftover: float = 1.0, noise: float = 1.0, seed: int = 20261004) -> dict:
    """Two periods, no room memory: agent vectors x_iP = c_i + e_iP, c_i ~ N(0, leftover^2 I) shared by both periods
    (the leftover agent constant), e ~ N(0, noise^2 I). Rooms: period 1 random halves; in period 2 each agent keeps its
    room w.p. `stay`, else is redrawn; one agent leaves and one newcomer joins. Returns the rejection rate (two-sided
    p <= 0.05) and the median R for the joint and the independent relabel."""
    rng = np.random.default_rng(seed)
    rej = {"joint": 0, "independent": 0}
    Rs = []
    for w in range(worlds):
        c = rng.normal(0, leftover, (n_agents + 1, d))
        ag1 = list(range(n_agents))
        ag2 = list(range(1, n_agents + 1))
        lab1 = rng.permutation(np.array([BEST] * (n_agents // 2) + [REST] * (n_agents - n_agents // 2)))
        room1 = dict(zip(ag1, lab1))
        lab2 = np.array([room1[a] if (a in room1 and rng.random() < stay) else rng.choice([BEST, REST]) for a in ag2])
        if (lab2 == BEST).sum() < 2 or (lab2 == REST).sum() < 2:
            lab2[:2] = [BEST, REST]
        v1 = c[ag1] + rng.normal(0, noise, (len(ag1), d))
        v2 = c[ag2] + rng.normal(0, noise, (len(ag2), d))
        for kind in rej:
            r = remanence_test(v1, lab1, ag1, v2, lab2, ag2, n_null=n_null, seed=int(rng.integers(1 << 31)),
                               joint=kind == "joint")
            rej[kind] += r["p_two"] <= 0.05
        Rs.append(r["R"])
    lo, hi = _band(worlds)
    return {"worlds": worlds, "n_null": n_null, "stay": stay, "leftover_over_noise": leftover / noise,
            "size_joint": rej["joint"] / worlds, "size_independent": rej["independent"] / worlds,
            "median_R_null_worlds": float(np.median(Rs)), "band_at_0.05": [lo, hi]}


def _band(reps: int, alpha: float = 0.05) -> tuple[float, float]:
    from scipy.stats import binom
    return float(binom.ppf(0.025, reps, alpha) / reps), float(binom.ppf(0.975, reps, alpha) / reps)


# ---------------------------------------------------------------------------------------------- verify
def _h100_reproduction() -> dict:
    """remanence_test vs h100lib.remanence on H100's real tables (bge style_resid), same seed and inputs."""
    import importlib.util
    p = ROOT / "hypotheses/H100-room-symmetry-breaking/analysis/h100lib.py"
    data = ROOT / "data/processed/H100-room-symmetry-breaking"
    if not (p.exists() and (data / "agent_days.parquet").exists()):
        return {"status": "H100 tables absent"}
    spec = importlib.util.spec_from_file_location("h100lib_ro", p)
    L = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(L)
    import polars as pl
    tab, X = L.load("bge_small", "style_resid")
    Xc = L.day_center(tab, X)
    fields = pl.read_parquet(data / "fields.parquet")
    F = np.load(data / "fields_bge_small.npy")
    out, ok = {}, True
    pairs = [(P1, P2) for P1, P2 in zip(L.MULTI[:-1], L.MULTI[1:])]
    for P1, P2 in pairs:
        try:
            ref = L.remanence(tab, Xc, fields, F, P1, P2, n_null=500, seed=3)
        except Exception as e:  # noqa: BLE001  (a pair H100 cannot score)
            out[f"{P1}-{P2}"] = f"skipped ({type(e).__name__})"
            continue
        vs, labs, ags = [], [], []
        for P in (P1, P2):   # H100's O7 inputs (composition and field removed), rebuilt with its own helpers
            ap = L.agent_period(tab, Xc, P, 1)
            agents = sorted(ap)
            x = np.array([ap[a][1] for a in agents])
            A, _ = L.constants(tab, Xc, exclude={P1, P2})
            x = x - np.array([A.get(a, np.zeros(x.shape[1])) for a in agents])
            E, _ = L.field_basis(fields, F, P)
            vs.append(L.remove_dirs(x, E))
            labs.append(np.array([ap[a][0] for a in agents]))
            ags.append(agents)
        mine = remanence_test(vs[0], labs[0], ags[0], vs[1], labs[1], ags[1], n_null=500, seed=3)
        same = all(mine[k] == ref[k] for k in ("R", "null_sd", "z", "p_two"))
        out[f"{P1}-{P2}"] = "identical" if same else {k: (ref[k], mine[k]) for k in ("R", "null_sd", "z", "p_two")}
        ok &= same
    out["ok"] = bool(ok)
    return out


def verify() -> dict:
    res = {"h100_reproduction": _h100_reproduction()}
    res["size"] = size_test()
    res["size_weak_leftover"] = size_test(leftover=0.4)
    lo, hi = res["size"]["band_at_0.05"]
    ok_size = all(res[k]["size_joint"] <= hi and res[k]["size_independent"] > hi for k in ("size", "size_weak_leftover"))
    res["ok"] = bool(res["h100_reproduction"].get("ok", True) and ok_size)
    print(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify()["ok"] else 1)
    print(__doc__)
