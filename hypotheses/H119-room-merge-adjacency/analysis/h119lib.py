"""H119 helpers: NE42 design (weeks, pair classes from the room timeline), contrasts with Wald CIs."""
from __future__ import annotations

import numpy as np

import ki_talk as K

NE42_WEEKS = {
    "39": ["2026-04-27", "2026-04-28", "2026-04-29", "2026-04-30", "2026-05-01"],
    "40": ["2026-05-04", "2026-05-05", "2026-05-06", "2026-05-07", "2026-05-08"],
    "41": ["2026-05-11", "2026-05-12", "2026-05-13", "2026-05-14", "2026-05-15"],
}
BEST = {"Claude Opus 4.7", "GPT-5.5", "Gemini 3.1 Pro", "Kimi K2.6"}
REST = {"Claude Haiku 4.5", "Claude Opus 4.5", "Claude Opus 4.6", "Claude Sonnet 4.5", "Claude Sonnet 4.6",
        "DeepSeek-V3.2", "GPT-5.1", "GPT-5.2", "GPT-5.4", "Gemini 2.5 Pro"}
GPT5 = "GPT-5"
CLASS_IDS = [0, 1, 2, 3]   # within, cross, GPT-5 x #rest (mirror arm), GPT-5 x #best (never adjacent)
CLASS_NAMES = {0: "within", 1: "cross", 2: "g5_rest", 3: "g5_best"}
Z = 1.959964
FIX_HI, SW_LO = 0.90, 0.20   # Amendment 0: co-located >= 90% of kept minutes / <= 20% (movers' partial first days, hops)


def group_of(name: str) -> str | None:
    if name in BEST:
        return "best"
    if name in REST:
        return "rest"
    if name == GPT5:
        return "gpt5"
    return None


def ne42_classes(agents) -> np.ndarray:
    names = K.roster_names()
    gr = [group_of(names[a]) for a in agents]
    N = len(agents)
    C = -np.ones((N, N), int)
    for i in range(N):
        for j in range(N):
            if i == j or gr[i] is None or gr[j] is None:
                continue
            pair = {gr[i], gr[j]}
            if gr[i] == gr[j]:
                C[i, j] = 0
            elif pair == {"best", "rest"}:
                C[i, j] = 1
            elif pair == {"gpt5", "rest"}:
                C[i, j] = 2
            elif pair == {"gpt5", "best"}:
                C[i, j] = 3
    return C


def _ci(est, var):
    se = float(np.sqrt(max(var, 0))) if np.isfinite(var) else np.nan
    return est, est - Z * se, est + Z * se, se


def ne42_contrasts(fits: dict) -> dict:
    out = {}
    J = {w: f["J"] for w, f in fits.items()}
    V = {w: f["V"] for w, f in fits.items()}
    short = {0: "Jw", 1: "Jx", 2: "Jg5r", 3: "Jg5b"}
    for w in fits:
        for c, nm in CLASS_NAMES.items():
            out[f"{short[c]}_{w}"] = float(J[w][c])
            out[f"se_{nm}_{w}"] = float(np.sqrt(V[w][c, c])) if np.isfinite(V[w][c, c]) else np.nan
    x, w_ = 1, 0
    M = J["40"][x] - 0.5 * (J["39"][x] + J["41"][x])
    vM = V["40"][x, x] + 0.25 * (V["39"][x, x] + V["41"][x, x])
    out["M"], out["M_lo"], out["M_hi"], out["M_se"] = _ci(M, vM)

    def dxw(w):
        return J[w][x] - J[w][w_], V[w][x, x] + V[w][w_, w_] - 2 * V[w][x, w_]
    d40, v40 = dxw("40"); d39, v39 = dxw("39"); d41, v41 = dxw("41")
    out["MD"], out["MD_lo"], out["MD_hi"], out["MD_se"] = _ci(d40 - 0.5 * (d39 + d41), v40 + 0.25 * (v39 + v41))
    out["Rm"], out["Rm_lo"], out["Rm_hi"], out["Rm_se"] = _ci(J["41"][x] - J["39"][x], V["41"][x, x] + V["39"][x, x])
    out["Pm"], out["Pm_lo"], out["Pm_hi"], out["Pm_se"] = _ci(d40, v40)
    g = 2
    G5 = J["40"][g] - 0.5 * (J["39"][g] + J["41"][g])
    out["G5"], out["G5_lo"], out["G5_hi"], out["G5_se"] = _ci(G5, V["40"][g, g] + 0.25 * (V["39"][g, g] + V["41"][g, g]))
    for w in fits:
        out[f"Jx_{w}_lo"] = J[w][x] - Z * np.sqrt(V[w][x, x]); out[f"Jx_{w}_hi"] = J[w][x] + Z * np.sqrt(V[w][x, x])
    return out


def e2_contrasts(r: dict, C: int = 4) -> dict:
    out = {}
    V = r["V"]
    for c, nm in CLASS_NAMES.items():
        jr, ju = r["JR"][c], r["JU"][c]
        out[f"JR_{nm}"], out[f"JU_{nm}"] = float(jr), float(ju)
        out[f"nzR_{nm}"], out[f"nzU_{nm}"] = int(r["nzR"][c]), int(r["nzU"][c])
        e, lo, hi, se = _ci(jr, V[c, c]) if np.isfinite(jr) else (np.nan,) * 4
        out[f"JR_{nm}_lo"], out[f"JR_{nm}_hi"] = lo, hi
        e, lo, hi, se = _ci(ju, V[C + c, C + c]) if np.isfinite(ju) else (np.nan,) * 4
        out[f"JU_{nm}_lo"], out[f"JU_{nm}_hi"] = lo, hi
        if np.isfinite(jr) and np.isfinite(ju):
            e, lo, hi, se = _ci(jr - ju, V[c, c] + V[C + c, C + c] - 2 * V[c, C + c])
        else:
            e = lo = hi = se = np.nan
        out[f"CRU_{nm}"], out[f"CRU_{nm}_lo"], out[f"CRU_{nm}_hi"] = e, lo, hi
    # short aliases used by the synthetic summary
    out["CRU_x"], out["CRU_x_lo"] = out["CRU_cross"], out["CRU_cross_lo"]
    out["CRU_w"], out["CRU_w_lo"] = out["CRU_within"], out["CRU_within_lo"]
    out["JRx_lo"], out["JUx_lo"] = out["JR_cross_lo"], out["JU_cross_lo"]
    return out


def switch_classes(cb: np.ndarray, ca: np.ndarray) -> np.ndarray:
    """Pair classes from co-location shares before (cb) and after (ca): 0 fixed, 1 on, 2 off, 3 never, -1 other."""
    N = cb.shape[0]
    cls = -np.ones((N, N), int)
    off = ~np.eye(N, dtype=bool)
    hi, lo = FIX_HI, SW_LO
    cls[off & (cb >= hi) & (ca >= hi)] = 0
    cls[off & (cb <= lo) & (ca >= hi)] = 1
    cls[off & (cb >= hi) & (ca <= lo)] = 2
    cls[off & (cb <= lo) & (ca <= lo)] = 3
    return cls


def switch_contrast(fb: dict, fa: dict, n_on: int, n_off: int) -> dict:
    """S = d_on - d_off (both arms), d_on - d_fixed (on only), d_fixed - d_off (off only); d = after - before."""
    from math import erf
    d = fa["J"] - fb["J"]
    Vd = fa["V"] + fb["V"]
    row = {}
    for k, nm in enumerate(("fixed", "on", "off", "never")):
        row[f"J_{nm}_b"] = float(fb["J"][k]); row[f"J_{nm}_a"] = float(fa["J"][k])
        row[f"d_{nm}"] = float(d[k]); row[f"d_{nm}_se"] = float(np.sqrt(Vd[k, k])) if np.isfinite(Vd[k, k]) else np.nan
    has_on = n_on > 0 and np.isfinite(d[1])
    has_off = n_off > 0 and np.isfinite(d[2])
    if has_on and has_off:
        S, var = d[1] - d[2], Vd[1, 1] + Vd[2, 2] - 2 * Vd[1, 2]
    elif has_on:
        S, var = d[1] - d[0], Vd[1, 1] + Vd[0, 0] - 2 * Vd[0, 1]
    elif has_off:
        S, var = d[0] - d[2], Vd[2, 2] + Vd[0, 0] - 2 * Vd[0, 2]
    else:
        return row
    se = float(np.sqrt(max(var, 1e-12)))
    row.update({"S": float(S), "S_se": se, "S_lo": float(S - Z * se), "S_hi": float(S + Z * se),
                "S_p1": float(0.5 * (1 - erf(S / se / np.sqrt(2))))})
    return row
