"""H140 synthetic validation on real skeletons (axis F; runs before any real-data H140 statistic).

Skeleton: every agent statement of the unit with its real author, time, room, producing call index n, context segment,
self-share s_self (ctx_pos / (ctx_pos + k_ctx)), and, for scored talk calls, the real batch (pending set), in-flight set
and window-field members. Only the 32-d vectors are synthetic. Statements are generated in time order, R replicates at once:
  W0      no coupling:  y = h_a + e
  W-DG    HH383:        y = s_self p + g1 k^-0.75 sum(batch) + 0.1 h_a + e            (w1 = 1, b = 0.75, g1 = 0.1)
  W-DGh   power world:  y = (0.25 + 0.5 s_self) p + g1 k^-0.75 sum(batch) + 0.1 h_a + e   (w1 = 0.5)
  W-lin   R-linear:     as W-DG with b = 0, g1 = 0.01                                     (w1 = 1, a = 1)
  W-well  R-well (H130): y = h_a + x_a(n) + kick_a(n) + e; x_a OU per call at gamma 0.0094; each read message adds
                        0.044 (x_m - h_a) to kick_a, which decays at 0.15 per call                  (w1 = 0)
  W-field H113 W1:      y = 0.5 p + f_room(t) + 0.1 h_a + e; f_room OU in time, tau = 30 min; no reading (w1 = 0)
p = mean of the author's last two statements in the segment (the author's well h_a if none), e ~ N(0, I).
The vectors are rescaled so that the median |y_perp|^2 matches the real one (the estimator is scale-free; this sets units
only). The scheme (h140scheme.gram_rows) and the estimator (h140lib.fit) are the ones used on real data.

Usage: uv run python .../analysis/synthetic.py --set main   (skeletons 51c, 51g, #38, #41; all worlds)
       uv run python .../analysis/synthetic.py --set pool   (all 12 #51 units; W-DGh and W-well; S2 pool power)
Output: data/processed/H140-degroot-readout-self-weight/synthetic/{runs_<set>.parquet, summary_<set>.json}
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
import h140lib as L  # noqa: E402
import h140scheme as S  # noqa: E402

OUT = S.ROOT / "data/processed/H140-degroot-readout-self-weight/synthetic"
GRID = L.B_GRID
WORLDS = {
    "W0": dict(kind="none"),
    "W-DG": dict(kind="dg", w0=0.0, w1=1.0, b=0.75, g1=0.1),
    "W-DGh": dict(kind="dg", w0=0.25, w1=0.5, b=0.75, g1=0.1),
    "W-lin": dict(kind="dg", w0=0.0, w1=1.0, b=0.0, g1=0.01),
    "W-well": dict(kind="well", gamma=0.0094, J=0.044, gk=0.15),
    "W-field": dict(kind="field", tau=1800.0),
}
TRUE_W1 = {"W0": 0.0, "W-DG": 1.0, "W-DGh": 0.5, "W-lin": 1.0, "W-well": 0.0, "W-field": 0.0}
TRUE_A = {"W-DG": 0.25, "W-DGh": 0.25, "W-lin": 1.0}
SKELETONS = {"51c": (51, ["51c"]), "51g": (51, ["51g"]), "G38": (38, None), "G41": (41, None)}
POOL_UNITS = ["51a", "51b", "51c", "51d", "51e", "51f", "51g", "51h", "51i", "51j", "51k", "51l"]


def real_yperp_median(sk: S.Skeleton, model: str = "bge_small") -> float:
    """Median |y_perp|^2 of the real statements (no product with any other vector is formed)."""
    V = S.real_vectors(sk, model)
    nu = len(sk.units)
    mu = np.vstack([V[sk.unit_of_st == u].mean(0) for u in range(nu)])
    Y = V[sk.y_idx] - mu[sk.unit_of_row]
    for rm in np.unique(sk.rooms):
        sel = sk.rooms == rm
        Y[sel] = Y[sel] @ S.orth_projector(S.goal_basis(sk.goal_no, rm if rm >= 0 else None, model, sk.regime))
    return float(np.median((Y ** 2).sum(1)))


def generate(sk: S.Skeleton, w: dict, R: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ex = sk.extra
    T = ex["t_us"]; A = ex["agent"]; NN = ex["n"]; prev = ex["prev"]; bat = ex["batch"]
    sig = np.array(ex["s_self"], dtype=float)
    sig = np.where(np.isfinite(sig), sig, np.nanmedian(sig))
    nst = len(T)
    ag, aix = np.unique(A, return_inverse=True)
    Hw = rng.normal(0, 1, (R, len(ag), 32))
    V = np.zeros((R, nst, 32))
    E = rng.normal(0, 1, (R, nst, 32))
    order = np.argsort(T, kind="stable")
    kind = w["kind"]
    if kind == "field":
        F = np.zeros((R, nst, 32))
        rooms = ex["room"]
        for rm in np.unique(rooms):
            ir = order[rooms[order] == rm]
            cur = rng.normal(0, 1, (R, 32)); tp = None
            for j in ir:
                if tp is not None:
                    r = np.exp(-max(T[j] - tp, 0) / 1e6 / w["tau"])
                    cur = r * cur + np.sqrt(1 - r * r) * rng.normal(0, 1, (R, 32))
                F[:, j] = cur; tp = T[j]
    if kind == "well":
        X = rng.normal(0, 1, (R, len(ag), 32)); K = np.zeros((R, len(ag), 32)); last = np.full(len(ag), -1)
    for j in order:
        a = aix[j]
        if kind == "none":
            V[:, j] = Hw[:, a] + E[:, j]
            continue
        pv = prev[j][:2]
        p = V[:, pv].mean(1) if len(pv) else Hw[:, a]
        if kind == "dg":
            b = bat.get(int(j), [])
            up = w["g1"] * len(b) ** (-w["b"]) * V[:, b].sum(1) if b else 0.0
            V[:, j] = (w["w0"] + w["w1"] * sig[j]) * p + up + 0.1 * Hw[:, a] + E[:, j]
        elif kind == "field":
            V[:, j] = 0.5 * p + F[:, j] + 0.1 * Hw[:, a] + E[:, j]
        elif kind == "well":
            d = int(NN[j] - last[a]) if (last[a] >= 0 and NN[j] >= 0) else 10_000
            d = max(d, 1)
            r = (1 - w["gamma"]) ** d
            X[:, a] = r * X[:, a] + np.sqrt(1 - r * r) * rng.normal(0, 1, (R, 32))
            K[:, a] *= (1 - w["gk"]) ** d
            b = bat.get(int(j), [])
            if b:
                K[:, a] += w["J"] * (V[:, b] - Hw[:, a][:, None, :]).sum(1)
            V[:, j] = Hw[:, a] + X[:, a] + K[:, a] + E[:, j]
            if NN[j] >= 0:
                last[a] = NN[j]
    return V


def one_fit(sk, Vr, Gb, field: bool, spec: str, B: int, seed: int) -> dict:
    g, _, _ = S.gram_rows(sk, Vr, field=field, Gb=Gb, with_items=False, with_sur=False)
    d, G, _ = L.prep(sk.rows, g)
    return L.fit(d, G, spec, B=B, seed=seed, grid=GRID)


def run_skeleton(name: str, sk: S.Skeleton, worlds: list[str], R: int, B: int, seed0: int, specs, scale_ref: float) -> list[dict]:
    rows = []
    Gb = {rm: S.orth_projector(S.goal_basis(sk.goal_no, rm if rm >= 0 else None, "bge_small", sk.regime)) for rm in np.unique(sk.rooms)}
    for wn in worlds:
        t0 = time.time()
        V = generate(sk, WORLDS[wn], R, seed0 + 101 * list(WORLDS).index(wn))
        # scale calibration on replicate 0
        g0, _, _ = S.gram_rows(sk, V[0], Gb=Gb, with_items=False, with_sur=False)
        sc = np.sqrt(scale_ref / max(float(np.median(g0["g_y_y"].to_numpy())), 1e-12))
        for r in range(R):
            Vr = V[r] * sc
            row = {"skeleton": name, "world": wn, "rep": r}
            for tag, field, spec, bb in specs:
                f = one_fit(sk, Vr, Gb, field, spec, bb, seed0 + r)
                for kk in ("n", "w0", "w1", "w1_lo", "w1_hi", "w2", "w2_lo", "w2_hi", "b", "b_lo", "b_hi", "a", "a_lo", "a_hi",
                           "gamma1", "gammaF", "w_anchor", "w1_se", "a_se"):
                    if kk in f:
                        row[f"{tag}_{kk}"] = f[kk]
            rows.append(row)
        print(f"  {name} {wn}: {R} reps {time.time() - t0:.0f}s", flush=True)
    return rows


def summarize(df: pl.DataFrame, tags) -> dict:
    out = {}
    for (sk, wn), d in df.group_by(["skeleton", "world"], maintain_order=True):
        s = {"reps": len(d)}
        tw = TRUE_W1[wn]; ta = TRUE_A.get(wn)
        for t in tags:
            if f"{t}_w1" not in d.columns:
                continue
            w1 = d[f"{t}_w1"]
            if w1.median() is None:
                continue
            s[f"{t}_w1_med"] = w1.median()
            s[f"{t}_w1_bias"] = w1.median() - tw
            if f"{t}_w1_lo" in d.columns:
                lo, hi = d[f"{t}_w1_lo"], d[f"{t}_w1_hi"]
                s[f"{t}_w1_pos"] = float((lo > 0).mean())         # CI above 0
                s[f"{t}_w1_cover"] = float(((lo <= tw) & (hi >= tw)).mean())
                s[f"{t}_w1_ciw"] = (hi - lo).median()
                s[f"{t}_a_med"] = d[f"{t}_a"].median()
                if ta is not None:
                    s[f"{t}_a_bias"] = d[f"{t}_a"].median() - ta
                    s[f"{t}_a_cover"] = float(((d[f"{t}_a_lo"] <= ta) & (d[f"{t}_a_hi"] >= ta)).mean())
                s[f"{t}_a_excl1"] = float((d[f"{t}_a_hi"] < 1).mean())
                if f"{t}_w2_lo" in d.columns:
                    s[f"{t}_w2_pos"] = float((d[f"{t}_w2_lo"] > 0).mean())
        out[f"{sk}|{wn}"] = s
    return out


def pool_summary(df: pl.DataFrame, tags=("main", "A1")) -> dict:
    """S2: per replicate, the DL pool of w1 over the #51 units; power = share with pooled CI above 0."""
    out = {}
    for t in tags:
        for wn, d in df.group_by("world"):
            res = []
            for r, dr in d.group_by("rep"):
                p = L.dl_pool(dr[f"{t}_w1"].to_numpy(), dr[f"{t}_w1_se"].to_numpy())
                res.append((p.get("est"), p.get("lo"), p.get("hi")))
            res = np.array(res, dtype=float)
            tw = TRUE_W1[wn[0]]
            out[f"{t}|{wn[0]}"] = {"reps": len(res), "pool_w1_med": float(np.nanmedian(res[:, 0])),
                                   "pool_pos": float(np.mean(res[:, 1] > 0)),
                                   "pool_in_band": float(np.mean((res[:, 0] >= 0.5) & (res[:, 0] <= 1.5) & (res[:, 1] > 0))),
                                   "pool_cover": float(np.mean((res[:, 1] <= tw) & (res[:, 2] >= tw)))}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="main", choices=["main", "pool"])
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--B", type=int, default=100)
    ap.add_argument("--skeleton", action="append")
    ap.add_argument("--worlds")
    ap.add_argument("--summarize-only", action="store_true")
    a = ap.parse_args()
    if a.summarize_only:
        df = pl.read_parquet(OUT / f"runs_{a.set}.parquet")
        summ = summarize(df, ["main", "mainF", "noDn", "ols", "mt", "mk", "A1", "A1noDn", "A1F"]) if a.set == "main" else \
            {"per_unit": summarize(df, ["main", "A1"]), "pool": pool_summary(df.filter(pl.col("A1_w1_se").is_not_null()))}
        (OUT / f"summary_{a.set}.json").write_text(json.dumps(summ, indent=1, default=float))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    if a.set == "main":
        specs = [("main", False, "main", a.B), ("mainF", True, "main", a.B), ("noDn", False, "noDn", a.B), ("ols", False, "ols", 0),
                 ("mt", False, "main_t", a.B), ("mk", False, "main_k", a.B),
                 ("A1", False, "A1", a.B), ("A1noDn", False, "A1noDn", a.B), ("A1F", True, "A1", a.B)]
        worlds = a.worlds.split(",") if a.worlds else list(WORLDS)
        for name in (a.skeleton or list(SKELETONS)):
            g, units = SKELETONS[name]
            sk = S.build_skeleton(g, only_units=units)
            ref = real_yperp_median(sk)
            print(f"{name}: statements {len(sk.st)}, rows {len(sk.rows)}, ref |y|^2 {ref:.3f}", flush=True)
            rows += run_skeleton(name, sk, worlds, a.reps, a.B, 1000 * len(rows) + 7, specs, ref)
            pl.DataFrame(rows).write_parquet(OUT / "runs_main.parquet")
        df = pl.DataFrame(rows)
        summ = summarize(df, ["main", "mainF", "noDn", "ols", "mt", "mk", "A1", "A1noDn", "A1F"])
    else:
        specs = [("main", False, "main", a.B), ("A1", False, "A1", a.B)]
        worlds = a.worlds.split(",") if a.worlds else ["W-DGh", "W-well", "W-field"]
        for u in POOL_UNITS:
            sk = S.build_skeleton(51, only_units=[u])
            if len(sk.rows) < 30:
                continue
            ref = real_yperp_median(sk)
            print(f"{u}: statements {len(sk.st)}, rows {len(sk.rows)}", flush=True)
            rows += run_skeleton(u, sk, worlds, a.reps, a.B, 5000 + 31 * len(rows), specs, ref)
            pl.DataFrame(rows).write_parquet(OUT / "runs_pool.parquet")
        df = pl.DataFrame(rows)
        summ = {"per_unit": summarize(df, ["main"]), "pool": pool_summary(df)}
    df.write_parquet(OUT / f"runs_{a.set}.parquet")
    (OUT / f"summary_{a.set}.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=lambda x: round(float(x), 3)))


if __name__ == "__main__":
    main()
