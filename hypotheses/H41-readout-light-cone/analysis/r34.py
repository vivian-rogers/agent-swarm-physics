"""H41 round 2, R3 (lags vs cone hops; phase quantization) and R4 (co-generation: start-time RD, common stimulus).

  uv run python hypotheses/H41-readout-light-cone/analysis/r34.py synth4 [--seeds 4]   # Y0-Y4 worlds (R4)
  uv run python hypotheses/H41-readout-light-cone/analysis/r34.py synth3 [--seeds 4]   # T1d / T2 / W_L worlds (R3)
  uv run python hypotheses/H41-readout-light-cone/analysis/r34.py units [--only 38]    # R4 unit tables, real data
  uv run python hypotheses/H41-readout-light-cone/analysis/r34.py real4 | real3

Definitions: README "Round 2", R3 and R4 (written 2026-10-05 03:50 UTC, before any round-2 statistic).
Synthetic worlds reuse analysis/synthetic.py's skeleton loader and the round-1 `scheme/build.py: analyze`.
Outputs: data/processed/H41-readout-light-cone/r2/{R3,R4}/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(HERE))
import h41core as C  # noqa: E402
import build as BLD  # noqa: E402
import synthetic as SYN  # noqa: E402

OUT = C.OUT / "r2"
H_HAZ = 7200.0
CS_BACK = 1800.0
CS_SHARE_MAX = 0.5
DBINS = BLD.DBINS
W_RD = (60.0, 120.0)
CLS_NAME = {0: "U", 1: "D", 2: "N", 3: "W"}
B_REAL = 400
B_SYN = 200
EPS0 = SYN.EPS0
HORIZON = SYN.HORIZON


def qci(v) -> tuple:
    """Percentile 95% interval that tolerates infinite draws (no-event denominators)."""
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    if len(v) < 20:
        return (np.nan, np.nan)
    w = np.clip(v, -1e12, 1e12)
    lo, hi = np.quantile(w, .025), np.quantile(w, .975)
    f = lambda x: float(np.inf if x >= 1e11 else (-np.inf if x <= -1e11 else x))
    return (f(lo), f(hi))


# ============================================================================================ common stimulus index
class CSIndex:
    """Specific artifact touches per agent (actions, how in url/output/bare); artifacts expand to {itself, parent}.

    An artifact key is specific on a PT day if it is touched by <= 50% of that day's active agents.
    """

    def __init__(self, sk: C.Skeleton):
        days = list(sk.days)
        art = pl.read_parquet(C.SH / "artifacts.parquet", columns=["artifact", "parent"])
        par = dict(zip(art["artifact"].to_list(), art["parent"].to_list()))
        lo = sk.t_min - 86400
        hi = sk.t_max + 3600
        am = (pl.scan_parquet(C.SH / "artifact_mentions.parquet")
              .filter((pl.col("source").cast(pl.Utf8) == "action") & pl.col("how").cast(pl.Utf8).is_in(["url", "output", "bare"])
                      & pl.col("agent").is_not_null())
              .select(C.ts("t").alias("t"), pl.col("agent").cast(pl.Int64), "artifact")
              .filter((pl.col("t") >= lo) & (pl.col("t") <= hi)).collect())
        am = am.with_columns(pl.from_epoch((pl.col("t") * 1e6).cast(pl.Int64), time_unit="us")
                             .dt.replace_time_zone("UTC").dt.convert_time_zone("America/Los_Angeles").dt.date()
                             .cast(pl.Utf8).alias("pt"))
        am = am.filter(pl.col("pt").is_in(days))
        keys_a, keys_k, keys_t, keys_d = [], [], [], []
        for a, t, x, d in zip(am["agent"].to_list(), am["t"].to_list(), am["artifact"].to_list(), am["pt"].to_list()):
            for k in (x, par.get(x)):
                if k is None:
                    continue
                keys_a.append(a)
                keys_k.append(int(k))
                keys_t.append(t)
                keys_d.append(d)
        k = pl.DataFrame({"agent": keys_a, "key": keys_k, "t": keys_t, "pt": keys_d},
                         schema={"agent": pl.Int64, "key": pl.Int64, "t": pl.Float64, "pt": pl.Utf8})
        # active agents per day: agents with a receiving call
        act = {}
        for d in days:
            act[d] = len(set(sk.c_agent[sk.c_day == d].tolist()))
        sh = k.group_by("pt", "key").agg(pl.col("agent").n_unique().alias("na"))
        sh = sh.with_columns(pl.col("pt").replace_strict(act, default=1).alias("nact"))
        spec = sh.filter(pl.col("na") <= CS_SHARE_MAX * pl.col("nact")).select("pt", "key")
        k = k.join(spec, on=["pt", "key"], how="inner").sort("agent", "t")
        self.by = {}
        for (a,), sub in k.group_by(["agent"], maintain_order=True):
            self.by[int(a)] = (sub["t"].to_numpy(), sub["key"].to_numpy())

    def keys(self, agent: int, lo: float, hi: float) -> set:
        v = self.by.get(int(agent))
        if v is None:
            return set()
        i0, i1 = np.searchsorted(v[0], lo, side="left"), np.searchsorted(v[0], hi, side="left")
        return set(v[1][i0:i1].tolist())


# ============================================================================================ R4 units
def build_units(sk: C.Skeleton, ri: C.RoomIndex, items: pl.DataFrame, adopt: pl.DataFrame, cal: pl.DataFrame,
                cs: CSIndex | None, goal: int) -> pl.DataFrame:
    """Unit rows: (item, in-room agent, call) for the in-flight talk call and the first talk call starting after t0."""
    day_end = dict(zip(cal["pt_date"].to_list(), cal["we"].to_list()))
    day_ws = dict(zip(cal["pt_date"].to_list(), cal["ws"].to_list()))
    ad = {}
    for mk, a, ci in zip(adopt["marker"].to_list(), adopt["agent"].to_list(), adopt["ci_use"].to_list()):
        ad[(int(mk), int(a))] = int(ci)
    by_m0 = {}
    for mk, m0, cl in zip(items["marker"].to_list(), items["m0"].to_list(), items["cls"].to_list()):
        by_m0.setdefault(int(m0), []).append((int(mk), int(cl)))
    src_meta = items.unique("m0").select("m0", "t0", "src", "room0", "day0")
    talk = {}
    for a, s in sk.agent_calls.items():
        tk = np.flatnonzero(sk.c_talk[s])
        talk[a] = (tk, sk.c_t[s][tk], sk.c_first[s][tk])
    agents = np.array(sorted(int(a) for a in sk.agents))
    cols = {k: [] for k in ["m0", "marker", "cls", "agent", "side", "s", "lat", "d", "adopt", "src", "day", "clus", "cs"]}
    for r in src_meta.iter_rows(named=True):
        m0, t0, src, room0, day0 = int(r["m0"]), float(r["t0"]), int(r["src"]), int(r["room0"]), r["day0"]
        hz_end = min(t0 + H_HAZ, day_end.get(day0, t0 + H_HAZ))
        clus = f"{goal}:{day0}:{int((t0 - day_ws.get(day0, t0)) // 3600)}"
        src_keys = cs.keys(src, t0 - CS_BACK, t0 + 1e-6) if (cs is not None and 0 <= src < 64) else None
        its = by_m0[m0]
        for a in agents:
            if a == src or ri.at(a, t0) != room0:
                continue
            tk, tc, tf = talk[a]
            if len(tk) == 0:
                continue
            j = int(np.searchsorted(tc, t0, side="left"))  # first talk call with t_call >= t0
            units = []
            # in-flight: the agent's latest call (any kind) with t_call < t0 must be a talk call whose message is after t0
            s_ = sk.agent_calls[a]
            k_all = int(np.searchsorted(sk.c_t[s_], t0, side="left")) - 1
            if k_all >= 0 and sk.c_talk[s_][k_all]:
                tcall, tfirst = sk.c_t[s_][k_all], sk.c_first[s_][k_all]
                if tfirst > t0 and tfirst <= hz_end:
                    units.append((-1, k_all, tcall, tfirst))
            if j < len(tk) and tc[j] > t0 and tf[j] <= hz_end:
                units.append((1, int(tk[j]), tc[j], tf[j]))
            if not units:
                continue
            ck = None
            for side, ci, tcall, tfirst in units:
                if src_keys is not None:
                    ak = cs.keys(a, t0 - CS_BACK, tfirst)
                    ck = bool(src_keys & ak)
                for mk, cl in its:
                    ca = ad.get((mk, a))
                    if side == 1 and ca is not None and len(units) == 2 and ca == units[0][1]:
                        continue  # adopted at the in-flight call: no longer at risk
                    if side == 1 and ca is not None and ca < ci:
                        continue
                    cols["m0"].append(m0)
                    cols["marker"].append(mk)
                    cols["cls"].append(cl)
                    cols["agent"].append(a)
                    cols["side"].append(side)
                    cols["s"].append(tcall - t0)
                    cols["lat"].append(tfirst - tcall)
                    cols["d"].append(tfirst - t0)
                    cols["adopt"].append(ca is not None and ca == ci)
                    cols["src"].append(src)
                    cols["day"].append(day0)
                    cols["clus"].append(clus)
                    cols["cs"].append(ck)
    return pl.DataFrame(cols, schema={"m0": pl.Int64, "marker": pl.Int64, "cls": pl.Int8, "agent": pl.Int16,
                                      "side": pl.Int8, "s": pl.Float64, "lat": pl.Float64, "d": pl.Float64,
                                      "adopt": pl.Boolean, "src": pl.Int64, "day": pl.Utf8, "clus": pl.Utf8,
                                      "cs": pl.Boolean})


# ============================================================================================ R4 estimators
def _dbin(d):
    return np.searchsorted(DBINS, d, side="right")


def j_mh(u: pl.DataFrame) -> float:
    """Delay-matched in-flight vs first post-t0 talk call (round-1 estimator, on units)."""
    if u.height == 0:
        return np.nan
    d = u["d"].to_numpy()
    b = _dbin(d)
    if "goal" in u.columns:  # period x delay-bin strata (pre-registered pooling with period strata)
        b = u["goal"].to_numpy().astype(np.int64) * 100 + b
    side = u["side"].to_numpy()
    y = u["adopt"].to_numpy().astype(float)
    top = bot = 0.0
    for k in np.unique(b):
        m = b == k
        m1, m0 = m & (side == 1), m & (side == -1)
        n1, n0 = m1.sum(), m0.sum()
        if n1 == 0 or n0 == 0:
            continue
        a1, a0 = y[m1].sum(), y[m0].sum()
        N = n1 + n0
        top += a1 * n0 / N
        bot += a0 * n1 / N
    if bot == 0:
        return np.inf if top > 0 else np.nan
    return top / bot


def _ll_limit(s: np.ndarray, y: np.ndarray, w: float) -> float:
    """Local-linear (triangular kernel) intercept at s = 0 from one side."""
    if len(s) < 3:
        return np.nan
    k = np.clip(1 - np.abs(s) / w, 0, None)
    if k.sum() == 0:
        return np.nan
    X = np.column_stack([np.ones_like(s), s])
    WX = X * k[:, None]
    try:
        beta = np.linalg.solve(X.T @ WX + 1e-12 * np.eye(2), WX.T @ y)
    except np.linalg.LinAlgError:
        return np.nan
    return float(beta[0])


def rd_limits(u: pl.DataFrame, w: float):
    s = u["s"].to_numpy()
    y = u["adopt"].to_numpy().astype(float)
    side = u["side"].to_numpy()
    mL = (side == -1) & (s >= -w) & (s < 0)
    mR = (side == 1) & (s > 0) & (s <= w)
    return _ll_limit(s[mL], y[mL], w), _ll_limit(s[mR], y[mR], w), int(mL.sum()), int(mR.sum())


def j_rd(u: pl.DataFrame, w: float = 60.0, by: str | None = "goal") -> float:
    """Start-time RD ratio; with several periods, MH-like weighted limits (weights = units in the window)."""
    if u.height == 0:
        return np.nan
    if by is None or by not in u.columns or u[by].n_unique() == 1:
        L, R, nL, nR = rd_limits(u, w)
        if not np.isfinite(L) or not np.isfinite(R):
            return np.nan
        if L <= 0:
            return np.inf if R > 0 else np.nan
        return R / L
    num = den = 0.0
    for (g,), sub in u.group_by([by]):
        L, R, nL, nR = rd_limits(sub, w)
        if not (np.isfinite(L) and np.isfinite(R)) or nL < 3 or nR < 3:
            continue
        wt = nL + nR
        num += wt * R
        den += wt * L
    if den <= 0:
        return np.inf if num > 0 else np.nan
    return num / den


def psi(u: pl.DataFrame) -> float:
    """MH ratio over delay bins of the in-flight hazard with CS = 1 vs CS = 0."""
    x = u.filter((pl.col("side") == -1) & pl.col("cs").is_not_null())
    if x.height == 0 or int(x["adopt"].sum()) < 10:  # amendment R2-A2: >= 10 in-flight adoptions
        return np.nan
    b = _dbin(x["d"].to_numpy())
    if "goal" in x.columns:
        b = x["goal"].to_numpy().astype(np.int64) * 100 + b
    c = x["cs"].to_numpy().astype(bool)
    y = x["adopt"].to_numpy().astype(float)
    top = bot = 0.0
    for k in np.unique(b):
        m = b == k
        m1, m0 = m & c, m & ~c
        n1, n0 = m1.sum(), m0.sum()
        if n1 == 0 or n0 == 0:
            continue
        N = n1 + n0
        top += y[m1].sum() * n0 / N
        bot += y[m0].sum() * n1 / N
    if bot == 0:
        return np.inf if top > 0 else np.nan
    return top / bot


def r4_stats(u: pl.DataFrame) -> dict:
    out = dict(J_mh=j_mh(u), J_rd60=j_rd(u, 60.0), J_rd120=j_rd(u, 120.0), psi=psi(u),
               J_mh_cs0=j_mh(u.filter(pl.col("cs") == False)), J_rd60_cs0=j_rd(u.filter(pl.col("cs") == False), 60.0))  # noqa: E712
    inf_ad = u.filter((pl.col("side") == -1) & pl.col("adopt"))
    post_ad = u.filter((pl.col("side") == 1) & pl.col("adopt"))
    out["cs_share_inflight_adopt"] = float(inf_ad["cs"].drop_nulls().mean()) if inf_ad["cs"].drop_nulls().len() else np.nan
    out["cs_share_post_adopt"] = float(post_ad["cs"].drop_nulls().mean()) if post_ad["cs"].drop_nulls().len() else np.nan
    out["cs_share_units"] = float(u["cs"].drop_nulls().mean()) if u["cs"].drop_nulls().len() else np.nan
    out["n_units"] = u.height
    out["n_inflight"] = int((u["side"] == -1).sum())
    out["adopt_inflight"] = int(inf_ad.height)
    out["adopt_post"] = int(post_ad.height)
    return out


def boot_stats(u: pl.DataFrame, fn, keys, B: int, seed: int = 0) -> dict:
    cl = u["clus"].to_numpy()
    uc, inv = np.unique(cl, return_inverse=True)
    idx = [np.flatnonzero(inv == i) for i in range(len(uc))]
    rng = np.random.default_rng(seed)
    vals = {k: [] for k in keys}
    for _ in range(B):
        pick = rng.integers(0, len(uc), len(uc))
        ii = np.concatenate([idx[p] for p in pick])
        r = fn(u[ii])
        for k in keys:
            vals[k].append(r[k])
    res = {}
    for k in keys:
        v = np.array(vals[k], float)
        res[k + "_ci"] = qci(v)
    return res


# ============================================================================================ extended simulator
class SimR(SYN.Sim):
    """Round-1 simulator plus R3/R4 truths: decaying relay (T1d), common-stimulus pulse, latency-weighted field."""

    def __init__(self, sk, ri, rng, cs: CSIndex | None = None):
        super().__init__(sk, ri, rng)
        self.cs = cs
        lat = {}
        for a, s in sk.agent_calls.items():
            lat[a] = np.clip(sk.c_first[s] - sk.c_t[s], 0.0, 600.0)
        self.lat = lat
        allat = np.concatenate([lat[a][sk.c_talk[s]] for a, s in sk.agent_calls.items()])
        self.lat_med = float(np.median(allat[allat > 0])) if np.any(allat > 0) else 10.0

    def run_item2(self, m0, q, relay=True, field=0.0, field_len=False, cs_p=0.0):
        sk, rng = self.sk, self.rng
        t0 = float(sk.msgs["t"][m0])
        src = int(sk.msgs["agent"][m0])
        lo = np.searchsorted(self.tt, t0, side="right")
        hi = np.searchsorted(self.tt, t0 + HORIZON, side="right")
        BIG = 10 ** 12
        exp_ci = {}
        rd = self.readers

        def add_carrier(mr):
            v = rd.get(int(mr))
            if v is None:
                return
            for r_, c_ in zip(v[0], v[1]):
                r_ = int(r_)
                if c_ < exp_ci.get(r_, BIG):
                    exp_ci[r_] = int(c_)

        add_carrier(m0)
        cs_set = set()
        if cs_p > 0 and self.cs is not None:
            sk_ = self.cs.keys(src, t0 - CS_BACK, t0 + 1e-6)
            if sk_:
                for a in sk.agents:
                    a = int(a)
                    if a != src and (self.cs.keys(a, t0 - CS_BACK, t0 + 600.0) & sk_):
                        cs_set.add(a)
        t_on = t0 - rng.uniform(0, 300)
        adopted = {src}
        uses = [m0]
        for k in range(lo, hi):
            a = int(self.ta[k])
            ci = int(self.tci[k])
            t = float(self.tt[k])
            if a in adopted:
                if a != src and rng.random() < 0.3:
                    uses.append(int(self.tm[k]))
                    add_carrier(self.tm[k])
                continue
            f = EPS0
            if field > 0:
                fl = field * np.exp(-max(t - t_on, 0.0) / 600.0)
                if field_len:
                    fl *= self.lat[a][ci] / self.lat_med
                f += fl
            if cs_p > 0 and a in cs_set and (t0 - 300.0) <= t <= (t0 + 600.0):
                f += cs_p
            rel = 0.0
            ce = exp_ci.get(a, BIG)
            if relay and ce <= ci:
                t_exp = sk.c_t[sk.agent_calls[a]][ce]
                rel = q * np.exp(-max(t - t_exp, 0.0) / 600.0)
            lam = 1 - (1 - min(f, 0.95)) * (1 - rel)
            if rng.random() < lam:
                adopted.add(a)
                uses.append(int(self.tm[k]))
                add_carrier(self.tm[k])
        return uses


def synth_items(sk, sim: SimR, n_items: int, world: dict, rng):
    msgs = sk.msgs
    cand = msgs.filter((pl.col("kind") == "agent") & pl.col("ci_talk").is_not_null()
                       & pl.col("agent").is_in(list(map(int, sk.agents))) & (pl.col("t") < sk.t_max - HORIZON))
    seeds = rng.choice(cand["mrow"].to_numpy(), size=min(n_items, cand.height), replace=False)
    urows = []
    for j, m0 in enumerate(seeds):
        for mr in sim.run_item2(int(m0), **world):
            urows.append((-(j + 1), mr))
    u = (pl.DataFrame({"marker": [r[0] for r in urows], "mrow": [r[1] for r in urows]},
                      schema={"marker": pl.Int64, "mrow": pl.Int64}).unique(["marker", "mrow"])
         .join(msgs.select("message_id", "mrow", "t", "room", "kind", "agent", "node", "ci_talk", "pt_date")
               .with_columns(pl.col("mrow").cast(pl.Int64)), on="mrow", how="inner").sort("marker", "t", "mrow"))
    nov = pl.DataFrame({"marker": np.arange(-len(seeds), 0, dtype=np.int64), "cls": np.full(len(seeds), 1, np.int64)})
    return u, nov


def quick_items_adopt(u: pl.DataFrame, nov: pl.DataFrame, sk) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Items and adoptions without cones (enough for R4 units)."""
    first = u.group_by("marker", maintain_order=True).first()
    items = first.select("marker", pl.col("mrow").alias("m0"), pl.col("t").alias("t0"), pl.col("room").alias("room0"),
                         pl.col("node").alias("src"), pl.col("pt_date").alias("day0")).join(nov, on="marker")
    ad = (u.join(items.select("marker", "t0", "src"), on="marker")
          .filter((pl.col("kind") == "agent") & (pl.col("t") > pl.col("t0")) & (pl.col("node") != pl.col("src"))
                  & pl.col("ci_talk").is_not_null())
          .group_by("marker", "agent", maintain_order=True).first()
          .select("marker", "agent", pl.col("ci_talk").alias("ci_use")))
    return items, ad


WORLDS4 = {
    "Y0_relay": dict(q=0.4, relay=True),
    "Y1_relay_cs": dict(q=0.4, relay=True, cs_p=0.15),
    "Y2_lenfield": dict(q=0.0, relay=False, field=0.10, field_len=True),
    "Y3_field": dict(q=0.0, relay=False, field=0.10),
    "Y4_relay_lenfield": dict(q=0.4, relay=True, field=0.10, field_len=True),
}


def real_item_count(goal: int, days, cap: int = 4000) -> int:
    """Amendment R2-A1: synthetic runs use the real number of novel items on the skeleton's days (capped)."""
    it = pl.read_parquet(C.OUT / f"G{goal:02d}/items.parquet", columns=["day0"])
    return int(min(cap, it.filter(pl.col("day0").is_in(list(days))).height))


def run_synth4(seeds: int, n_items: int | None = None):
    cal = C.calendar()
    rows = []
    for skn in ["38", "31", "51"]:
        sk = SYN.skeleton(skn, cal)
        ri = C.RoomIndex(sk)
        cs = CSIndex(sk)
        n_items = real_item_count(int(skn), sk.days)
        print(f"skeleton {skn}: {n_items} items per run", flush=True)
        for wname, world in WORLDS4.items():
            for rep in range(seeds):
                rng = np.random.default_rng(5000 + 31 * rep + sum(map(ord, wname + skn)))
                sim = SimR(sk, ri, rng, cs)
                t_a = time.time()
                u, nov = synth_items(sk, sim, n_items, world, rng)
                items, ad = quick_items_adopt(u, nov, sk)
                units = build_units(sk, ri, items, ad, cal, cs, int(skn)).with_columns(pl.lit(int(skn)).alias("goal"))
                st = r4_stats(units)
                ci = boot_stats(units, r4_stats, ["J_mh", "J_rd60", "psi", "J_mh_cs0"], B_SYN, seed=rep)
                row = dict(skel=skn, world=wname, rep=rep, **st, **{k: v for k, v in ci.items()},
                           secs=round(time.time() - t_a, 1))
                rows.append(row)
                print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
        pl.DataFrame(rows, infer_schema_length=None).write_parquet(OUT / "R4" / "synth.parquet")
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(OUT / "R4" / "synth.parquet")
    return df


# ============================================================================================ R3
def r3_hop_stats(adf: pl.DataFrame) -> dict:
    x = adf.filter(pl.col("in_cone") & (pl.col("H_tr") >= 1))
    n = x["n"].to_numpy().astype(float)
    H = x["H_tr"].to_numpy()
    res = dict(n_H1=int((H == 1).sum()), n_H2=int((H == 2).sum()), n_H3=int((H >= 3).sum()))
    if res["n_H1"] < 5 or res["n_H2"] < 5:
        return res
    m1, m2 = np.median(n[H == 1]), np.median(n[H == 2])
    res["M2"] = float(m2 / m1) if m1 > 0 else np.nan
    res["F2"] = float(np.quantile(n[H == 2], .1) / max(np.quantile(n[H == 1], .1), 1.0))
    if res["n_H3"] >= 5:
        res["M3"] = float(np.median(n[H >= 3]) / m1) if m1 > 0 else np.nan
    from scipy.stats import spearmanr
    res["rho"] = float(spearmanr(n, H).statistic)
    res["mult_H1"] = float(np.median(n[H == 1]))
    res["mult_H2"] = float(np.median(n[H == 2] / 2))
    if res["n_H3"] >= 5:
        res["mult_H3"] = float(np.median(n[H >= 3] / H[H >= 3]))
    return res


def r3_perm(adf: pl.DataFrame, sk: C.Skeleton, draws: int = 500, seed: int = 0) -> dict:
    """Entry-conditioned lag permutation: lag redrawn from in-cone lags with t0 + lag >= cone entry; n recounted."""
    x = adf.filter(pl.col("in_cone") & (pl.col("H_tr") >= 1))
    obs = r3_hop_stats(adf)
    if "M2" not in obs:
        return {**obs, "perm": None}
    t0 = x["t0"].to_numpy()
    te = x["T_entry"].to_numpy()
    ag = x["agent"].to_numpy()
    H = x["H_tr"].to_numpy()
    lag = x["t_use"].to_numpy() - t0
    lag_sorted = np.sort(lag)
    need = te - t0
    rng = np.random.default_rng(seed)
    calls = {int(a): sk.c_t[sk.agent_calls[int(a)]] for a in np.unique(ag)}
    M2s = []
    for _ in range(draws):
        n_new = np.empty(len(x))
        for i in range(len(x)):
            k0 = np.searchsorted(lag_sorted, need[i], side="left")
            if k0 >= len(lag_sorted):
                l_ = lag[i]
            else:
                l_ = lag_sorted[rng.integers(k0, len(lag_sorted))]
            ct = calls[int(ag[i])]
            n_new[i] = np.searchsorted(ct, t0[i] + l_, side="right") - np.searchsorted(ct, t0[i], side="right")
        m1 = np.median(n_new[H == 1])
        M2s.append(np.median(n_new[H == 2]) / m1 if m1 > 0 else np.nan)
    M2s = np.array(M2s, float)
    M2s = M2s[np.isfinite(M2s)]
    obs["M2_null_mean"] = float(M2s.mean())
    obs["M2_null_q95"] = float(np.quantile(M2s, .95))
    obs["dM"] = float(obs["M2"] - M2s.mean())
    obs["p_perm"] = float((1 + np.sum(M2s >= obs["M2"])) / (1 + len(M2s)))
    return obs


def r3_phase(adf: pl.DataFrame, sk: C.Skeleton) -> dict:
    e = adf.filter(pl.col("in_cone") & pl.col("exposed") & pl.col("first_exp_ci").is_not_null() & (pl.col("parent") >= 0)
                   & (pl.col("parent") < 64) & pl.col("tau_c").is_not_null() & pl.col("tau_c").is_finite()
                   & (pl.col("tau_c") > 0))
    if e.height < 20:
        return dict(n_phase=e.height)
    tau = e["tau_c"].to_numpy()
    xm = e["dt_hop"].to_numpy() / tau
    tce = np.array([sk.c_t[sk.agent_calls[int(a)]][int(c)] for a, c in zip(e["agent"].to_list(), e["first_exp_ci"].to_list())])
    xe = (e["t_use"].to_numpy() - tce) / tau
    R = lambda x: float(np.abs(np.mean(np.exp(2j * np.pi * x))))
    return dict(n_phase=e.height, R_m=R(xm), R_e=R(xe), R_crit=float(np.sqrt(-np.log(0.05) / e.height)))


WORLDS3 = {
    "T1d_relay": dict(q=0.4, relay=True),
    "T2_field": dict(q=0.0, relay=False, field=0.10),
    "WL_lenfield": dict(q=0.0, relay=False, field=0.10, field_len=True),
}


def skeleton3(name: str, cal):
    if name == "51f":
        return C.load_skeleton(51, cal, days_filter=lambda d: "2026-08-05" <= d <= "2026-08-22")
    return C.load_skeleton(int(name), cal)


def run_synth3(seeds: int, n_items: int = 600):
    cal = C.calendar()
    rows = []
    for skn in ["51f", "36"]:
        sk = skeleton3(skn, cal)
        ri = C.RoomIndex(sk)
        for wname, world in WORLDS3.items():
            for rep in range(seeds):
                rng = np.random.default_rng(7000 + 31 * rep + sum(map(ord, wname + skn)))
                sim = SimR(sk, ri, rng, None)
                t_a = time.time()
                u, nov = synth_items(sk, sim, n_items, world, rng)
                items, adf, hz, _ = BLD.analyze(sk, u, nov, cal, ri)
                if adf.height == 0:
                    continue
                st = r3_perm(adf, sk, draws=200, seed=rep)
                ph = r3_phase(adf, sk)
                row = dict(skel=skn, world=wname, rep=rep, n_adopt=adf.height, **st, **ph, secs=round(time.time() - t_a, 1))
                rows.append(row)
                print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
        pl.DataFrame(rows, infer_schema_length=None).write_parquet(OUT / "R3" / "synth.parquet")
    return pl.DataFrame(rows, infer_schema_length=None)


# ============================================================================================ real runs
def eligible():
    return [int(m["goal"]) for m in json.loads((C.OUT / "periods_meta.json").read_text())]


def real_units(goals):
    cal = C.calendar()
    od = OUT / "R4"
    od.mkdir(parents=True, exist_ok=True)
    for g in goals:
        t_a = time.time()
        sk = C.load_skeleton(g, cal)
        ri = C.RoomIndex(sk)
        cs = CSIndex(sk)
        items = pl.read_parquet(C.OUT / f"G{g:02d}/items.parquet")
        adf = pl.read_parquet(C.OUT / f"G{g:02d}/adoptions.parquet")
        u = build_units(sk, ri, items, adf, cal, cs, g).with_columns(pl.lit(g).alias("goal"))
        u.write_parquet(od / f"units_G{g:02d}.parquet", compression="zstd")
        print(f"G{g:02d}: {u.height} units, {time.time() - t_a:.0f}s", flush=True)


def regime_of(g: int) -> str:
    return "I" if g <= 31 else ("II" if g <= 36 else "III")


def real4(goals):
    res = {}
    allu = []
    for g in goals:
        p = OUT / "R4" / f"units_G{g:02d}.parquet"
        if p.exists():
            allu.append(pl.read_parquet(p))
    U = pl.concat(allu, how="vertical_relaxed")
    U = U.with_columns(pl.col("goal").map_elements(regime_of, return_dtype=pl.Utf8).alias("regime"))
    keys = ["J_mh", "J_rd60", "psi", "J_mh_cs0", "J_rd60_cs0"]
    # per period x class (J_rd / J_mh), pooled per regime x class
    for (g,), sub in U.group_by(["goal"]):
        for c in [1, 2, 3, 0]:
            x = sub.filter(pl.col("cls") == c)
            if x.height == 0:
                continue
            st = r4_stats(x)
            ci = boot_stats(x, r4_stats, keys, B=200, seed=g)
            res[f"G{g:02d}_{CLS_NAME[c]}"] = {**st, **ci}
    for reg in ["I", "II", "III"]:
        for c in [1, 2, 3, 0]:
            x = U.filter((pl.col("regime") == reg) & (pl.col("cls") == c))
            if x.height == 0:
                continue
            st = r4_stats(x)
            ci = boot_stats(x, r4_stats, keys, B=B_REAL, seed=7)
            res[f"pooled_{reg}_{CLS_NAME[c]}"] = {**st, **ci}
            print(reg, CLS_NAME[c], {k: (round(v, 3) if isinstance(v, float) else v) for k, v in {**st, **ci}.items()},
                  flush=True)
    # descriptive: shared DQ2 reply parent between m0 and the in-flight adoption message, by class
    (OUT / "R4" / "results_real.json").write_text(json.dumps(res, indent=1, default=float))
    return res


def real3(goals):
    cal = C.calendar()
    res = {}
    for g in goals:
        adf = pl.read_parquet(C.OUT / f"G{g:02d}/adoptions.parquet")
        sk = C.load_skeleton(g, cal)
        ph = r3_phase(adf, sk)
        hs = r3_hop_stats(adf)
        row = {**ph, **hs}
        if hs.get("n_H2", 0) >= 30:
            row = {**row, **r3_perm(adf, sk, draws=500, seed=g)}
            if g == 51:  # #focus era only (hopping rooms), descriptive split
                a2 = adf.filter(pl.col("day0") >= "2026-08-05")
                row["focus_era"] = r3_perm(a2, sk, draws=500, seed=g + 1)
        res[f"G{g:02d}"] = row
        print(g, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items() if not isinstance(v, dict)},
              flush=True)
    (OUT / "R3").mkdir(parents=True, exist_ok=True)
    (OUT / "R3" / "results_real.json").write_text(json.dumps(res, indent=1, default=float))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["synth4", "synth3", "units", "real4", "real3"])
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    for d in ("R3", "R4"):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    goals = [int(x) for x in a.only.split(",") if x] or eligible()
    if a.step == "synth4":
        run_synth4(a.seeds)
    elif a.step == "synth3":
        run_synth3(a.seeds)
    elif a.step == "units":
        real_units(goals)
    elif a.step == "real4":
        real4(goals)
    elif a.step == "real3":
        real3(goals)


if __name__ == "__main__":
    main()
