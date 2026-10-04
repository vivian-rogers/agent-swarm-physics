"""H87 analysis helpers: the paired-bootstrap kappa table on the shared estimator (infra/shared/semantic_kappa.py).

Population (H70's): events with n_win >= 10, V not null, A_prev >= 0. Strata agent|period (FE and permutation floor),
clusters agent|pt_date (bootstrap; resampled clusters keep their original stratum, H70 Amendment A2).

Rows at call scale (F scramble vs P placebo):
  open-channel rows c in A, M, G, Q: I_c = MM plug-in I(X; S_c) on F minus the within-stratum permutation floor;
      dV_c = semantic_kappa.did_value (Poisson, stratum x arm FE, log1p V_pre) of open_c x scramble.
  C: I_C = I_P(X; S_C) - I_F(X; S_C); dV_C = semantic_kappa.scramble_cost.
  own-scramble value variants (dV only): H dose (any human item in calls 1-5), G any (any agent item received),
      M size (top vs bottom within-stratum tercile of memory chars; middle tercile dropped).
  V40 variants: every dV recomputed with V40.
kappa_c = dV_c / I_c on the same bootstrap draw (undefined where I_c <= MIN_I). Paired P(kappa_i > kappa_j) over draws
where both are defined.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H87-kappa-channel-table"
H84D = ROOT / "data/processed/H84-search-outage-memory-scramble"
sys.path.insert(0, str(ROOT / "infra/shared"))
import semantic_kappa as K  # noqa: E402

MIN_WIN, MIN_I = 10, 0.02
OPEN_ROWS = {"A": ("A_prev", "openA"), "M": ("S_M", "openM"), "G": ("S_G", "openG"), "Q": ("S_Q", "openQ")}
ORDER = ["A", "C", "G", "K", "M"]  # HH ordering (P1); K is day scale (separate native)


def load(path: Path | None = None) -> pl.DataFrame:
    ev = pl.read_parquet(path or DATA / "events_plus.parquet")
    return ev.filter((pl.col("n_win") >= MIN_WIN) & pl.col("V").is_not_null() & (pl.col("A_prev") >= 0))


def call_frame(ev: pl.DataFrame) -> dict:
    e = ev.filter(pl.col("etype").is_in(["F", "P"]))
    st = (e["agent"].cast(pl.Utf8) + "|" + e["period"]).to_numpy()
    mem = e["mem_chars"].fill_null(-1).to_numpy().astype(float)
    # within-stratum tercile of memory size (-1 = missing)
    terc = np.full(len(mem), -1)
    stc = K._codes(st)
    for s in np.unique(stc):
        ix = np.flatnonzero((stc == s) & (mem >= 0))
        if len(ix) >= 6:
            r = np.argsort(np.argsort(mem[ix]))
            terc[ix] = (3 * r) // len(ix)
    f = {"stratum": st, "cluster": (e["agent"].cast(pl.Utf8) + "|" + e["pt_date"]).to_numpy(),
         "scramble": (e["etype"] == "F").to_numpy(), "X": e["X_next"].to_numpy(), "V": e["V"].to_numpy(),
         "V40": e["V40"].to_numpy(), "V_pre": e["V_pre"].to_numpy(), "S_C": e["S_C"].to_numpy(),
         "anyH": (e["n_human_items"] > 0).to_numpy(), "anyG": (e["n_agent_items"] > 0).to_numpy(), "mem_terc": terc,
         "period": e["period"].to_numpy()}
    for c, (s, o) in OPEN_ROWS.items():
        f[f"S_{c}"] = e[s].to_numpy()
        f[f"open{c}"] = e[o].to_numpy()
    return f


def _mi(x, s, st, n_perm, rng):
    return K.mi_corrected(x, s, st, n_perm=n_perm, rng=rng)["I"] if len(x) > 10 else float("nan")


def _stats(f: dict, idx: np.ndarray, n_perm: int, rng, rows=("A", "M", "G", "Q"), variants: bool = True) -> dict:
    sc = f["scramble"][idx]
    st = f["stratum"][idx]
    X, V, V40, Vp = f["X"][idx], f["V"][idx], f["V40"][idx], f["V_pre"][idx]
    out = {}
    for c in rows:
        S = f[f"S_{c}"][idx]
        out[f"I_{c}"] = _mi(X[sc], S[sc], st[sc], n_perm, rng)
        d = K.did_value(V, f[f"open{c}"][idx], sc, st, Vp)
        out[f"dV_{c}"], out[f"rel_{c}"] = d["dV"], d["dV_rel"]
        if variants:
            d40 = K.did_value(V40, f[f"open{c}"][idx], sc, st, Vp)
            out[f"dV40_{c}"], out[f"rel40_{c}"] = d40["dV"], d40["dV_rel"]
    S = f["S_C"][idx]
    Ip = _mi(X[~sc], S[~sc], st[~sc], n_perm, rng)
    Is = _mi(X[sc], S[sc], st[sc], n_perm, rng)
    out["Ip_C"], out["Is_C"] = Ip, Is
    cst = K.scramble_cost(V, sc, st, Vp)
    out["dV_C"], out["rel_C"] = cst["cost"], cst["cost_rel"]
    if variants:
        c40 = K.scramble_cost(V40, sc, st, Vp)
        out["dV40_C"], out["rel40_C"] = c40["cost"], c40["cost_rel"]
        for nm, o in (("Hdose", f["anyH"][idx]), ("Gany", f["anyG"][idx])):
            d = K.did_value(V, o, sc, st, Vp)
            out[f"dV_{nm}"], out[f"rel_{nm}"] = d["dV"], d["dV_rel"]
        t = f["mem_terc"][idx]
        k = (t == 0) | (t == 2)
        d = K.did_value(V[k], t[k] == 2, sc[k], st[k], Vp[k])
        out["dV_Msize"], out["rel_Msize"] = d["dV"], d["dV_rel"]
    return out


def paired_table(f: dict, B: int = 300, n_perm: int = 200, n_perm_boot: int = 10, seed: int = 0,
                 rows=("A", "M", "G", "Q"), variants: bool = True) -> dict:
    rng = np.random.default_rng(seed)
    n = len(f["X"])
    point = _stats(f, np.arange(n), n_perm, rng, rows, variants)
    point["I_C"] = point["Ip_C"] - point["Is_C"]
    cl = K._codes(f["cluster"])
    order = np.argsort(cl, kind="stable")
    members = np.split(order, np.flatnonzero(np.diff(cl[order])) + 1)
    ncl = len(members)
    draws = []
    for _ in range(B):
        idx = np.concatenate([members[j] for j in rng.integers(0, ncl, ncl)])
        draws.append(_stats(f, idx, n_perm_boot, rng, rows, variants))
    keys = list(draws[0])
    D = {k: np.array([d[k] for d in draws], float) for k in keys}
    # bootstrap bias of plug-in MI under duplicated clusters: recentre on the point estimate (as kappa_row)
    for k in keys:
        if k.startswith("I_") or k in ("Ip_C", "Is_C"):
            D[k] = D[k] - (np.nanmean(D[k]) - point[k])
    D["I_C"] = D["Ip_C"] - D["Is_C"]
    res = {"n_scramble": int(f["scramble"].sum()), "n_placebo": int((~f["scramble"]).sum()), "n_clusters": ncl,
           "B": B, "rows": {}}
    kap = {}
    for c in list(rows) + ["C"]:
        I, dV = D[f"I_{c}"], D[f"dV_{c}"]
        kb = np.where(I > MIN_I, dV / np.where(I > MIN_I, I, 1.0), np.nan)
        kap[c] = kb
        pI, pdV = point[f"I_{c}"], point[f"dV_{c}"]
        r = {"I": pI, "I_ci": ci(I), "I_se": float(np.nanstd(I)), "dV": pdV, "dV_ci": ci(dV),
             "dV_se": float(np.nanstd(dV)), "dV_rel": point[f"rel_{c}"], "dV_rel_ci": ci(D[f"rel_{c}"]),
             "kappa": float(pdV / pI) if pI > MIN_I else float("nan"), "kappa_ci": ci(kb),
             "kappa_undefined_share": float(np.mean(~np.isfinite(kb)))}
        if c != "C":
            o = f[f"open{c}"]
            r["open_share_F"] = float(o[f["scramble"]].mean())
            r["open_share_P"] = float(o[~f["scramble"]].mean())
            r["n_open_F"] = int(o[f["scramble"]].sum())
        else:
            r["I_placebo"], r["I_scramble"] = point["Ip_C"], point["Is_C"]
        if variants:
            r["dV40"], r["dV40_ci"] = point[f"dV40_{c}"], ci(D[f"dV40_{c}"])
            r["dV40_rel"], r["dV40_rel_ci"] = point[f"rel40_{c}"], ci(D[f"rel40_{c}"])
        res["rows"][c] = r
    if variants:
        res["own_scramble"] = {nm: {"dV": point[f"dV_{nm}"], "dV_ci": ci(D[f"dV_{nm}"]), "dV_rel": point[f"rel_{nm}"],
                                    "dV_rel_ci": ci(D[f"rel_{nm}"])} for nm in ("Hdose", "Gany", "Msize")}
    pairs = {}
    names = list(rows) + ["C"]
    for i in names:
        for j in names:
            if i == j:
                continue
            ok = np.isfinite(kap[i]) & np.isfinite(kap[j])
            pairs[f"{i}>{j}"] = {"p": float(np.mean(kap[i][ok] > kap[j][ok])) if ok.sum() >= 20 else None,
                                 "n_defined": int(ok.sum())}
    res["paired"] = pairs
    res["kappa_draws"] = {c: [None if not np.isfinite(x) else float(x) for x in kap[c]] for c in names}
    return res


def kickoff_row(ev: pl.DataFrame, B: int = 300, n_perm: int = 200, seed: int = 0) -> dict:
    """K row at day scale: nights N (continuation #40 dropped); scramble = new-goal night. Strata = agent (a new-goal
    night is the only one in its agent|period stratum); bootstrap clusters = PT day (all agents share a goal change).
    I_K = I_within(X; A_prev) - I_newgoal(X; A_prev); dV_K = scramble_cost(V, newgoal | agent FE, log1p V_pre)."""
    e = ev.filter((pl.col("etype") == "N") & ~pl.col("continuation"))
    rng = np.random.default_rng(seed)
    st = e["agent"].cast(pl.Utf8).to_numpy()
    sc = e["newgoal"].to_numpy()
    X, S, V, V40, Vp = (e[c].to_numpy() for c in ("X_next", "A_prev", "V", "V40", "V_pre"))

    def stat(idx, npm):
        a = _mi(X[idx][~sc[idx]], S[idx][~sc[idx]], st[idx][~sc[idx]], npm, rng)
        b = _mi(X[idx][sc[idx]], S[idx][sc[idx]], st[idx][sc[idx]], npm, rng)
        c = K.scramble_cost(V[idx], sc[idx], st[idx], Vp[idx])
        c40 = K.scramble_cost(V40[idx], sc[idx], st[idx], Vp[idx])
        return a, b, c["cost"], c["cost_rel"], c40["cost"]
    p = stat(np.arange(len(X)), n_perm)
    cl = K._codes(e["pt_date"].to_numpy())
    order = np.argsort(cl, kind="stable")
    members = np.split(order, np.flatnonzero(np.diff(cl[order])) + 1)
    d = np.array([stat(np.concatenate([members[j] for j in rng.integers(0, len(members), len(members))]), 10)
                  for _ in range(B)])
    d[:, 0] -= d[:, 0].mean() - p[0]
    d[:, 1] -= d[:, 1].mean() - p[1]
    IK = d[:, 0] - d[:, 1]
    kb = np.where(IK > MIN_I, d[:, 2] / np.where(IK > MIN_I, IK, 1), np.nan)
    I_K = p[0] - p[1]
    return {"I_within": p[0], "I_newgoal": p[1], "I": I_K, "I_ci": ci(IK), "dV": p[2], "dV_ci": ci(d[:, 2]),
            "dV_rel": p[3], "dV_rel_ci": ci(d[:, 3]), "dV40": p[4], "dV40_ci": ci(d[:, 4]),
            "kappa": float(p[2] / I_K) if I_K > MIN_I else float("nan"), "kappa_ci": ci(kb),
            "kappa_undefined_share": float(np.mean(~np.isfinite(kb))), "n_newgoal": int(sc.sum()),
            "n_within": int((~sc).sum()), "n_days": len(members), "B": B,
            "kappa_draws": [None if not np.isfinite(x) else float(x) for x in kb]}


def ci(a) -> list:
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if len(a) > 10 else [None, None]
