"""Per-day agent matrices for the random-matrix hypotheses H91 (eigenvector rotation) and H92 (RMT-cleaned forecasts).

Moved from the byte-identical copies hypotheses/H91-eigenvector-rotation-signal/scheme/daymat.py and
hypotheses/H92-rmt-cleaned-forecast/scheme/daymat.py (STANDARDS §8, 2026-10-04); the functions are verbatim, and the
build step is their scheme/build.py. The hypothesis copies stay in place.

Content (model-11 spins, H12's construction at day resolution): for agent i, non-holdout active day d and 30-min
window w, x_i(w) = mean over i's statements in w of (u - mu_{i,d,kind}), u = regime-whitened unit 32-d statement
vector (DQ5 `statements_<variant>32_<model>.npy`), mu = i's mean on day d for that statement kind. Missing windows = 0.
W_d = ceil(window_s / 1800) (H12). Agent-day eligible with statements in >= max(2, ceil(W_d / 4)) windows; day
eligible with W_d >= 4 and >= 4 eligible agents.

Spins (model-01 spins): activity_bins_fixed minute states (missing = silent). Activity spin +1 if state >= 3; talk spin
+1 if state == 4. Each day is trimmed to the all-present window of its activity population (H12 `trim_rows`, DQ8:
minutes in which every agent with >= 1 active minute that day is between its first and last active minute). Talk-
eligible agent-day: >= 5 talk minutes in the kept window; activity-eligible: >= 5 active and >= 5 inactive kept
minutes. Day eligible: >= 60 kept minutes and >= 4 eligible agents.

Holdout: rows are dropped with infra/shared/common.holdout_mask and a hard assertion that calendar.holdout agrees.
The module flag ALLOW_HOLDOUT (default False) is set ONLY by a guarded confirm script after its sign-off checks, in
memory; the CLI never sets it and the shared outputs never contain held-out days.
Claude Code (roster.claude_code) is excluded. No text is read.

Also: matrix helpers (overlap, correlation, top eigenvectors, subspace distance) and the synthetic day generator used
by both hypotheses' synthetic studies (village-skeleton counts, no real data).

Outputs (data/processed/shared/day_matrices/, + _provenance.json): content_<bge|gte>{,_style_resid_period,_restate}.npz,
spins.npz, rooms.parquet, days.parquet (same files as H91's and H92's scheme folders).
Usage: uv run python infra/shared/day_matrices.py            (build)
       uv run python infra/shared/day_matrices.py --verify   (compare every array and table with H91's and H92's)
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import math  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import holdout_mask  # noqa: E402

MODELS = {"bge": "bge_small", "gte": "gte_modernbert"}
D = 32
MIN_TALK = 5
MIN_KEPT = 60
MIN_AGENTS = 4
# Set ONLY by a guarded analysis/confirm.py after its sign-off checks; exploratory code never touches it.
ALLOW_HOLDOUT = False


# ============================================================================================ tables
def calendar() -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = np.array(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()), bool)
    assert (hm == cal["holdout"].to_numpy()).all(), "calendar.holdout disagrees with holdout_mask"
    if not ALLOW_HOLDOUT:
        cal = cal.filter(~pl.Series(hm))
    cal = cal.filter(pl.col("goal_no").is_not_null())
    cal = cal.with_columns(pl.col("window_s").map_elements(lambda s: max(1, math.ceil(s / 1800)), return_dtype=pl.Int32)
                           .alias("W"))
    pu = pl.read_parquet(SH / "period_units.parquet")
    pu = pu if ALLOW_HOLDOUT else pu.filter(~pl.col("holdout"))
    u = pu.select("unit_id", "days").explode("days").rename({"days": "pt_date"})
    cal = cal.join(u, on="pt_date", how="left")
    return cal.select("pt_date", "goal_no", "regime", "weekday", "window_s", "W", "unit_id", "holdout").sort("pt_date")


def claude_code_agents() -> set:
    r = pl.read_parquet(SH / "roster.parquet")
    return set(r.filter(pl.col("claude_code"))["agent"].to_list())


def statements(dedupe: str = "none") -> pl.DataFrame:
    """Non-holdout statements with a window index, Claude Code excluded; `row` indexes the DQ5 vector arrays.
    dedupe: none | restate (drop either model's self-repeat flag) | copies (drop self_repeat_both)."""
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("row")
    hm = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()), bool)
    assert (hm == st["holdout"].to_numpy()).all(), "statements.holdout disagrees with holdout_mask"
    if not ALLOW_HOLDOUT:
        st = st.filter(~pl.Series(hm))
    if dedupe != "none":
        fl = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", "self_repeat", "self_repeat_both"])
        col = "self_repeat" if dedupe == "restate" else "self_repeat_both"
        drop = set(fl.filter(pl.col(col))["srow"].to_list())
        st = st.filter(~pl.col("row").is_in(list(drop)))
    cc = claude_code_agents()
    st = st.filter(pl.col("win30").is_not_null() & ~pl.col("agent").is_in(list(cc)))
    assert ALLOW_HOLDOUT or not st["holdout"].any()
    return st


# ============================================================================================ content
def build_content(model: str = "bge", variant: str = "white32", dedupe: str = "none") -> dict:
    """Per eligible day: {'date': {'agents': int array, 'Z': N x W x 32 float32}} (kind- and agent-day-centered)."""
    cal = calendar()
    Wd = dict(zip(cal["pt_date"].to_list(), cal["W"].to_list()))
    st = statements(dedupe).filter(pl.col("pt_date").is_in(list(Wd)))
    fname = f"statements_{variant}_{MODELS[model]}.npy" if variant == "white32" else \
        f"statements_{variant}32_{MODELS[model]}.npy"
    V = np.load(ED / fname, mmap_mode="r")
    out = {}
    for (date,), g in st.group_by(["pt_date"], maintain_order=False):
        W = Wd[date]
        if W < 4:
            continue
        X = np.asarray(V[g["row"].to_numpy()], dtype=np.float64)
        X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
        ag = g["agent"].to_numpy().astype(int)
        kd = (g["kind"] == "chat").to_numpy().astype(int)
        key = ag * 2 + kd
        _, inv = np.unique(key, return_inverse=True)
        mu = np.zeros((inv.max() + 1, D)); np.add.at(mu, inv, X); mu /= np.bincount(inv)[:, None]
        X = X - mu[inv]
        agents = np.unique(ag)
        ai = np.searchsorted(agents, ag)
        wi = np.minimum(g["win30"].to_numpy().astype(int), W - 1)
        S = np.zeros((len(agents), W, D)); n = np.zeros((len(agents), W))
        np.add.at(S, (ai, wi), X); np.add.at(n, (ai, wi), 1)
        nw = (n > 0).sum(1)
        keep = nw >= max(2, math.ceil(W / 4))
        if keep.sum() < MIN_AGENTS:
            continue
        Z = S[keep] / np.maximum(n[keep], 1)[:, :, None]
        out[date] = {"agents": agents[keep], "Z": Z.astype(np.float32)}
    return dict(sorted(out.items()))


def modal_rooms(dedupe: str = "none") -> pl.DataFrame:
    """Each agent's modal room per day (from statements.room; ties -> lowest room code)."""
    st = statements(dedupe).filter(pl.col("room").is_not_null())
    return (st.group_by("pt_date", "agent", "room").len()
            .sort(["pt_date", "agent", "len", "room"], descending=[False, False, True, False])
            .group_by("pt_date", "agent", maintain_order=True).first().select("pt_date", "agent", "room"))


# ============================================================================================ spins
def trim_rows(A: np.ndarray) -> np.ndarray:
    """All-present window (H12 h12lib.trim_rows; DQ8 all_present_window). A: N x L (+1 active, -1 not)."""
    act = A > 0
    has = act.any(1)
    if not has.any():
        return np.zeros(A.shape[1], bool)
    L = A.shape[1]
    first = np.argmax(act, axis=1); last = L - 1 - np.argmax(act[:, ::-1], axis=1)
    idx = np.arange(L)
    inside = (idx[None, :] >= first[:, None]) & (idx[None, :] <= last[:, None])
    return inside[has].all(0)


def build_spins() -> dict:
    """Per eligible day: {'date': {'agents', 'act' (N x K int8), 'talk_ok', 'act_ok' (bool N), 'minutes' (K)}};
    rows = activity population (>= 1 active minute that day), columns = kept (all-present) minutes."""
    cal = calendar()
    dates = cal["pt_date"].to_list()
    cc = claude_code_agents()
    ab = (pl.scan_parquet(SH / "activity_bins_fixed.parquet").select("pt_date", "minute", "agent", "state")
          .filter(pl.col("pt_date").is_in(dates) & ~pl.col("agent").is_in(list(cc))).collect())
    out = {}
    for (date,), g in ab.group_by(["pt_date"]):
        agents = np.unique(g["agent"].to_numpy().astype(int))
        L = int(g["minute"].max()) + 1
        S = np.ones((len(agents), L), np.int8)
        S[np.searchsorted(agents, g["agent"].to_numpy()), g["minute"].to_numpy()] = g["state"].to_numpy()
        act = np.where(S >= 3, 1, -1).astype(np.int8)
        pop = (act > 0).any(1)
        agents, S, act = agents[pop], S[pop], act[pop]
        if len(agents) < MIN_AGENTS:
            continue
        keep = trim_rows(act)
        if keep.sum() < MIN_KEPT:
            continue
        S, act = S[:, keep], act[:, keep]
        talk = np.where(S == 4, 1, -1).astype(np.int8)
        talk_ok = (talk > 0).sum(1) >= MIN_TALK
        nact = (act > 0).sum(1)
        act_ok = (nact >= 5) & ((act.shape[1] - nact) >= 5)
        out[date] = {"agents": agents, "act": act, "talk": talk, "talk_ok": talk_ok, "act_ok": act_ok,
                     "minutes": np.flatnonzero(keep).astype(np.int32)}
    return dict(sorted(out.items()))


# ============================================================================================ io
def save_days(path: Path, days: dict, keys: tuple):
    arr = {}
    for i, (date, rec) in enumerate(days.items()):
        arr[f"{i}__date"] = np.array(date)
        for k in keys:
            arr[f"{i}__{k}"] = rec[k] if k not in ("Z",) else rec[k].astype(np.float16)
    np.savez_compressed(path, **arr)


def load_days(path: Path) -> dict:
    z = np.load(path, allow_pickle=False)
    idx = sorted({int(k.split("__")[0]) for k in z.files})
    out = {}
    for i in idx:
        date = str(z[f"{i}__date"])
        rec = {k.split("__", 1)[1]: z[k] for k in z.files if k.startswith(f"{i}__") and not k.endswith("__date")}
        if "Z" in rec:
            rec["Z"] = rec["Z"].astype(np.float64)
        out[date] = rec
    return dict(sorted(out.items()))


# ============================================================================================ matrices
def overlap(Z: np.ndarray) -> np.ndarray:
    """Q_ij = <z_i . z_j>_w / d with unit mean-square scaling per agent (H12 overlap_eig). Z: N x W x d."""
    N = Z.shape[0]
    X = Z.reshape(N, -1)
    s = np.sqrt((X ** 2).mean(1, keepdims=True))
    X = X / np.where(s > 0, s, 1.0)
    return X @ X.T / X.shape[1]


def corr(S: np.ndarray) -> np.ndarray:
    X = S.astype(np.float64)
    X = X - X.mean(1, keepdims=True)
    sd = X.std(1, keepdims=True)
    X = X / np.where(sd > 0, sd, 1.0)
    return X @ X.T / X.shape[1]


def standardize(S: np.ndarray) -> np.ndarray:
    X = S.astype(np.float64)
    X = X - X.mean(1, keepdims=True)
    sd = X.std(1, keepdims=True)
    return X / np.where(sd > 0, sd, 1.0)


def topvecs(M: np.ndarray, k: int) -> np.ndarray:
    w, V = np.linalg.eigh(M)
    return V[:, ::-1][:, :k]


def subspace_dist(Va: np.ndarray, Vb: np.ndarray) -> float:
    k = Va.shape[1]
    return float(np.sqrt(max(0.0, 1.0 - np.sum((Va.T @ Vb) ** 2) / k)))


# ============================================================================================ synthetic
def synth_content_day(rng, N, W, loads, rho_w=0.0, fill=0.75, d=D, noise=1.0):
    """One synthetic content day. loads: N x K loadings on K shared window factors (each factor a random d-vector per
    window with AR(1) persistence rho_w across windows). Per-agent noise has the same AR(1). Missing windows (prob
    1 - fill) are 0; the day is then agent-day centered on present windows (as the real construction)."""
    K = loads.shape[1]

    def ar(shape):
        x = np.empty(shape)
        x[..., 0, :] = rng.standard_normal(shape[:-2] + (shape[-1],))
        for w in range(1, shape[-2]):
            x[..., w, :] = rho_w * x[..., w - 1, :] + np.sqrt(1 - rho_w ** 2) * rng.standard_normal(shape[:-2] + (shape[-1],))
        return x
    F = ar((K, W, d)) if K else np.zeros((0, W, d))
    E = ar((N, W, d)) * noise
    X = np.einsum("nk,kwd->nwd", loads, F) + E
    pres = rng.random((N, W)) < fill
    for i in range(N):
        if pres[i].sum() < 2:
            pres[i, rng.choice(W, 2, replace=False)] = True
    X = X * pres[:, :, None]
    mu = X.sum(1) / pres.sum(1)[:, None]
    X = (X - mu[:, None, :]) * pres[:, :, None]
    return X


def synth_spin_day(rng, N, L, loads, rate=0.1, rho_t=0.9, block=30):
    """One synthetic talk day: latent AR(1) Gaussians with factor structure, thresholded at the rate quantile.
    Returns N x L int8 spins (+1 talk)."""
    K = loads.shape[1]
    F = np.empty((K, L)); E = np.empty((N, L))
    F[:, 0] = rng.standard_normal(K); E[:, 0] = rng.standard_normal(N)
    a = np.sqrt(1 - rho_t ** 2)
    for t in range(1, L):
        F[:, t] = rho_t * F[:, t - 1] + a * rng.standard_normal(K)
        E[:, t] = rho_t * E[:, t - 1] + a * rng.standard_normal(N)
    sc = np.sqrt(np.maximum(1 - (loads ** 2).sum(1), 0.05))
    Y = loads @ F + sc[:, None] * E
    thr = np.quantile(Y, 1 - rate, axis=1, keepdims=True)
    return np.where(Y > thr, 1, -1).astype(np.int8)


def room_loads(N, a_market, a_room, rooms):
    """Loadings: one uniform market factor plus one factor per room."""
    R = int(rooms.max()) + 1
    L = np.zeros((N, 1 + R))
    L[:, 0] = a_market
    L[np.arange(N), 1 + rooms] = a_room
    return L


# ============================================================================================ build + verify
OUT = SH / "day_matrices"
VARIANTS = [("white32", "none", ""), ("style_resid_period", "none", "_style_resid_period"), ("white32", "restate", "_restate")]
SPIN_KEYS = ("agents", "act", "talk", "talk_ok", "act_ok", "minutes")
HYPS = [ROOT / "data/processed/H91-eigenvector-rotation-signal", ROOT / "data/processed/H92-rmt-cleaned-forecast"]


def build(out: Path = OUT):
    """H91 / H92 scheme/build.py: every content variant, spins, modal rooms and the eligibility table."""
    import datetime as dt
    import json
    import time
    from common import REVISION, git_commit
    assert not ALLOW_HOLDOUT, "the shared build never includes held-out days"
    t0 = time.time()
    out.mkdir(parents=True, exist_ok=True)
    cal = calendar()
    elig = {}
    for m in MODELS:
        for var, ded, suf in VARIANTS:
            days = build_content(m, var, ded)
            save_days(out / f"content_{m}{suf}.npz", days, ("agents", "Z"))
            elig[f"content_{m}{suf}"] = {d: len(r["agents"]) for d, r in days.items()}
            print(f"content {m}{suf}: {len(days)} days ({time.time() - t0:.0f}s)", flush=True)
    sp = build_spins()
    save_days(out / "spins.npz", sp, SPIN_KEYS)
    elig["talk"] = {d: int(r["talk_ok"].sum()) for d, r in sp.items()}
    elig["act"] = {d: int(r["act_ok"].sum()) for d, r in sp.items()}
    modal_rooms().write_parquet(out / "rooms.parquet", compression="zstd")
    dd = cal
    for k, v in elig.items():
        dd = dd.join(pl.DataFrame({"pt_date": list(v), f"n_{k}": list(v.values())}, schema={"pt_date": pl.String, f"n_{k}": pl.Int32}),
                     on="pt_date", how="left")
    dd.write_parquet(out / "days.parquet", compression="zstd")
    prov = {"built_by": "infra/shared/day_matrices.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/calendar", "shared/roster", "shared/period_units", "shared/activity_bins_fixed",
                                   "shared/statement_flags", "shared/embeddings/statements",
                                   "shared/embeddings/statements_white32_{bge_small,gte_modernbert}",
                                   "shared/embeddings/statements_style_resid_period32_{bge_small,gte_modernbert}"]}],
            "params": {"d": D, "window_s": 1800, "min_windows": "max(2, ceil(W/4))", "min_W": 4,
                       "min_agents": MIN_AGENTS, "min_talk_minutes": MIN_TALK, "min_kept_minutes": MIN_KEPT,
                       "trim": "all-present window of the activity population (DQ8)", "claude_code": "excluded",
                       "holdout": "dropped (holdout_mask + calendar.holdout assertion)", "text_stored": False,
                       "source": "H91 / H92 scheme/daymat.py + scheme/build.py (identical copies; rules unchanged)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"done in {time.time() - t0:.0f}s -> {out}")


def _same_npz(a: Path, b: Path) -> bool:
    za, zb = np.load(a, allow_pickle=False), np.load(b, allow_pickle=False)
    return sorted(za.files) == sorted(zb.files) and all(np.array_equal(za[k], zb[k]) for k in za.files)


def verify() -> bool:
    """Every array of every npz, and days/rooms parquet, equal to H91's and H92's scheme outputs (read-only)."""
    import json
    names = [f"content_{m}{suf}.npz" for m in MODELS for _, _, suf in VARIANTS] + ["spins.npz"]
    res, ok = {}, True
    for h in HYPS:
        r = {}
        for n in names:
            r[n] = "identical" if (h / n).exists() and (OUT / n).exists() and _same_npz(h / n, OUT / n) else "differ"
        for n in ("days.parquet", "rooms.parquet"):
            r[n] = ("identical" if (h / n).exists() and (OUT / n).exists()
                    and pl.read_parquet(h / n).equals(pl.read_parquet(OUT / n)) else "differ")
        ok &= all(v == "identical" for v in r.values())
        res[h.name[:3]] = r
    res["ok"] = bool(ok)
    print(json.dumps(res, indent=1), flush=True)
    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    build()
