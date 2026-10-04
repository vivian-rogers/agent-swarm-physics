"""H47 exploratory round 1 on real data (non-holdout only; asserted).

Sections (--only a,b,...; default all):
  coherence   replication layer: room correlation function per multi-room period (w30 primary, day secondary), N1/N2
              permutations, robustness (L0, no dedup, DQ5 style vectors, DQ6 assigned rooms), instruction share
  separation  G41 / G38 / G44 native: between-room centroid separation per day (F vs within-day relabel null)
  ne42        NE42 native: partition ratio r_X in #39 / #40 / #41, joint partition permutation, DiD
  g51         G51 native: r_F in 51f / 51g / 51h (focus-label permutation), G in single-room units, 51g C_B
  detector    room events: R1_swarm (H36's z, read-only) vs R1_room vs R1_loc vs R1_comb; placebo days
  leadership  goal changes in multi-room periods: lead index L, dT50, cohort-relabel permutation, Stouffer
Writes data/processed/H47-room-coherence-length/results/*.json (+ parquet tables).

Usage: uv run python hypotheses/H47-room-coherence-length/analysis/explore.py [--only coherence] [--fast]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h47lib as L  # noqa: E402  (thread caps)

sys.path.insert(0, str(L.ROOT / "infra/shared"))
sys.path.insert(0, str(L.ROOT / "hypotheses/H36-reorganization-alarm/analysis"))
from common import holdout_mask  # noqa: E402
from h36lib import auc, auc_ci, trailing_z  # noqa: E402  (read-only import)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

FAST = "--fast" in sys.argv
ONLY = None
if "--only" in sys.argv:
    ONLY = set(sys.argv[sys.argv.index("--only") + 1].split(","))
RES = L.OUT / "results"
NS = 3
N_PERM = 80 if FAST else 300
N_PERM_ROB = 40 if FAST else 100
PERIODS_MULTI = [35, 36, 37, 38, 39, 41, 42, 44, 51]


def want(x):
    return ONLY is None or x in ONLY


# ============================================================================================ data
class Data:
    def __init__(self):
        self.st = pl.read_parquet(L.OUT / "statements.parquet")
        cal = pl.read_parquet(L.SH / "calendar.parquet")
        hm = dict(zip(cal["pt_date"].to_list(), holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))
        days = self.st["pt_date"].unique().to_list()
        assert not any(hm.get(d, True) for d in days), "holdout (or unknown) day in H47 exploration"
        self.cal = cal.with_columns(pl.col("regime").cast(pl.String)).sort("pt_date")
        self.hm = hm
        self.V = np.load(L.OUT / "vec32.npy").astype(np.float32)
        self.Vs = np.load(L.OUT / "vec32_style.npy").astype(np.float32)
        self.units = pl.read_parquet(L.OUT / "units.parquet")
        me = pl.read_parquet(L.OUT / "mentions.parquet")
        self.mw = {}
        for u, a, b, w in me.iter_rows():
            self.mw.setdefault(u, {})[(int(a), int(b))] = float(w)
        z = np.load(L.OUT / "static.npz")
        self.static = {k: z[k] for k in z.files}

    def unit_ids(self, g, multi_only=True):
        u = self.units.filter(pl.col("goal_no") == g).sort("seq")
        if multi_only:
            u = u.filter(pl.col("multiroom"))
        return u["unit_id"].to_list()


def build_panel(Dt: Data, u: str, res="w30", vec="white", dedup=True, room_col="room", static="all"):
    rng = np.random.default_rng(L.stable_seed(u, res, vec, dedup, room_col))
    st = Dt.st.filter((pl.col("unit_id") == u) & ~pl.col("voff")).with_columns(pl.col("win30").fill_null(0).clip(0, None))
    if dedup:
        st = st.filter(~pl.col("dup"))
    if st.height == 0:
        return None
    if room_col != "room":
        st = st.with_columns(pl.coalesce(pl.col(room_col), pl.col("room")).alias("rr"))
    else:
        st = st.with_columns(pl.col("room").alias("rr"))
    st = st.filter(pl.col("rr").is_not_null())
    V = Dt.V if vec == "white" else Dt.Vs
    days = sorted(st["pt_date"].unique().to_list())
    dmap = {d: i for i, d in enumerate(days)}
    W = int(st["win30"].max()) + 1
    key = ["agent", "pt_date"] if res == "day" else ["agent", "pt_date", "win30"]
    g = st.group_by(key, maintain_order=True).agg(pl.col("sid"), pl.col("rr").mode().sort().first().alias("room")).sort(key)
    n = g.height
    X = np.full((n, 32), np.nan); A = np.full((n, NS, 32), np.nan); B = np.full((n, NS, 32), np.nan)
    for o, ix in enumerate(g["sid"].to_list()):
        ix = np.asarray(ix)
        X[o] = V[ix].mean(0)
        if len(ix) >= 2:
            for sp in range(NS):
                p = rng.permutation(ix); h = len(p) // 2
                A[o, sp] = V[p[:h]].mean(0); B[o, sp] = V[p[h:]].mean(0)
    ag = g["agent"].to_numpy().astype(int)
    dd = np.array([dmap[x] for x in g["pt_date"].to_list()])
    if res == "day":
        t = dd; wod = np.zeros(n, int)
    else:
        wod = g["win30"].to_numpy().astype(int); t = dd * W + wod
    S = Dt.static.get(f"{static}_{u}") if static else None
    return L.Panel(agent=ag, t=t, day=dd, wod=wod, room=g["room"].to_numpy().astype(int), X=X, A=A, B=B, grp=ag.copy(),
                   static=S, res=res, meta=dict(unit=u, days=days, n_obs=n, n_stmt=st.height))


def pool_C(Cs):
    ags = sorted(set().union(*[set(int(a) for a in C["agents"]) for C in Cs]))
    idx = {a: i for i, a in enumerate(ags)}
    N = len(ags); Dtot = sum(C["Cw"].shape[0] for C in Cs)
    out = {k: np.zeros((Dtot, N, N)) for k in ("Cw", "Nw", "Cc", "Nc")}
    s_sum = np.zeros((Dtot, N)); s_cnt = np.zeros((Dtot, N))
    d0 = 0
    for C in Cs:
        m = np.array([idx[int(a)] for a in C["agents"]]); D = C["Cw"].shape[0]
        for k in out:
            out[k][d0:d0 + D][:, m[:, None], m[None, :]] = C[k]
        s_sum[d0:d0 + D][:, m] = C["s_sum"]; s_cnt[d0:d0 + D][:, m] = C["s_cnt"]
        d0 += D
    return dict(**out, s_sum=s_sum, s_cnt=s_cnt, agents=np.array(ags), days=np.arange(Dtot))


def period_mw(Dt, units):
    mw = {}
    for u in units:
        for k, v in Dt.mw.get(u, {}).items():
            mw[k] = mw.get(k, 0.0) + v
    return mw


def period_coherence(Dt, units, res="w30", level=1, n_perm=N_PERM, rng=None, tiers=True, **kw):
    """Pooled coherence over a period's units: observed + joint room-relabel permutation + tier permutation."""
    rng = np.random.default_rng(0) if rng is None else rng
    Ps, devs, Cs = [], [], []
    for u in units:
        P = build_panel(Dt, u, res=res, **kw)
        if P is None or len(np.unique(P.day)) < (3 if res == "day" else 1):
            continue
        dv = L.deviations(P, level)
        Ps.append(P); devs.append(dv); Cs.append(L.contributions(P, *dv))
    if not Cs:
        return None
    C = pool_C(Cs)
    T = None
    if tiers:
        T, med = L.mention_tiers(C, period_mw(Dt, [P.meta["unit"] for P in Ps]))
        if not (T >= 0).any():
            T = None
    obs = L.coherence_from_C(C, T)
    out = dict(obs=obs, units=[P.meta["unit"] for P in Ps], n_obs=int(sum(P.meta["n_obs"] for P in Ps)),
               n_stmt=int(sum(P.meta["n_stmt"] for P in Ps)), n_agents=int(len(C["agents"])))
    if n_perm and np.isfinite(obs["D_B"]):
        nul = []
        for _ in range(n_perm):
            Cp = pool_C([L.contributions(P, *dv, room=L.permute_rooms(P, rng)) for P, dv in zip(Ps, devs)])
            o = L.coherence_from_C(Cp)
            nul.append((o["D_B"], o["C_B"]))
        nul = np.array(nul, float)
        ok = np.isfinite(nul[:, 0])
        out["p_DB"] = float((1 + (nul[ok, 0] >= obs["D_B"]).sum()) / (1 + ok.sum()))
        out["null_DB_q"] = [float(np.percentile(nul[ok, 0], q)) for q in (2.5, 50, 97.5)]
        out["null_CB_med"] = float(np.nanmedian(nul[:, 1]))
    if n_perm and T is not None and np.isfinite(obs.get("G", np.nan)):
        gn = np.array([L.coherence_from_C(C, L.permute_tiers(T, rng))["G"] for _ in range(n_perm)], float)
        gn = gn[np.isfinite(gn)]
        out["p_G_low"] = float((1 + (gn <= obs["G"]).sum()) / (1 + gn.size))
    if len(C["days"]) >= 3:
        bs = L.day_bootstrap(C, lambda C_, w: [L.coherence_from_C(C_, None, w)[k] for k in ("C_B", "D_B", "rho_w", "rho_c")],
                             B=200, rng=rng)
        out["boot_ci"] = {k: [float(np.nanpercentile(bs[:, i], 2.5)), float(np.nanpercentile(bs[:, i], 97.5))]
                          for i, k in enumerate(("C_B", "D_B", "rho_w", "rho_c"))}
    return out


def verdict_repl(o):
    if o is None or not np.isfinite(o["obs"].get("C_B", np.nan)):
        return "n/a"
    cb, p = o["obs"]["C_B"], o.get("p_DB", np.nan)
    if cb <= 0.3 and p < 0.05:
        return "supported"
    if cb >= 0.6 or p > 0.2:
        return "failed"
    return "mixed"


# ============================================================================================ coherence
def run_coherence(Dt):
    rng = np.random.default_rng(L.SEED)
    out = {}
    for g in PERIODS_MULTI:
        units = Dt.unit_ids(g)
        if not units:
            continue
        t0 = time.time()
        r = dict(units=units)
        r["w30"] = period_coherence(Dt, units, "w30", 1, N_PERM, rng)
        r["day"] = period_coherence(Dt, units, "day", 1, N_PERM, rng)
        r["verdict_rule"] = verdict_repl(r["w30"])
        # per unit (w30, descriptive)
        r["per_unit"] = {u: period_coherence(Dt, [u], "w30", 1, N_PERM_ROB, rng) for u in units}
        # robustness (w30)
        rob = {}
        rob["L0"] = period_coherence(Dt, units, "w30", 0, N_PERM_ROB, rng)
        rob["no_dedup"] = period_coherence(Dt, units, "w30", 1, N_PERM_ROB, rng, dedup=False)
        rob["style"] = period_coherence(Dt, units, "w30", 1, N_PERM_ROB, rng, vec="style")
        if g != 51:
            rob["assigned"] = period_coherence(Dt, units, "w30", 1, N_PERM_ROB, rng, room_col="room_assigned")
        rob["L1_instr_only"] = period_coherence(Dt, units, "w30", 1, 0, rng, static="instr", tiers=False)
        r["robust"] = rob
        d0 = rob["L0"]["obs"]["D_B"] if rob["L0"] else np.nan
        d1 = r["w30"]["obs"]["D_B"] if r["w30"] else np.nan
        di = rob["L1_instr_only"]["obs"]["D_B"] if rob["L1_instr_only"] else np.nan
        r["instr_share_all"] = (d0 - d1) / d0 if (np.isfinite(d0) and d0 > 0) else np.nan
        r["instr_share_instr"] = (d0 - di) / d0 if (np.isfinite(d0) and d0 > 0) else np.nan
        out[f"G{g}"] = r
        o = r["w30"]["obs"]
        print(f"G{g} w30 rho_w {o['rho_w']:.3f} rho_c {o['rho_c']:.3f} C_B {o['C_B']:.3f} p {r['w30'].get('p_DB')} "
              f"G {o.get('G', np.nan):.3f} -> {r['verdict_rule']}  ({time.time() - t0:.0f}s)", flush=True)
    L.jdump(out, RES / "coherence.json")
    return out


# ============================================================================================ separation (native)
def run_separation(Dt):
    rng = np.random.default_rng(L.SEED + 1)
    out = {}
    for g in (38, 41, 44, 36, 37, 39, 42, 35):
        units = Dt.unit_ids(g)
        st = Dt.st.filter(pl.col("unit_id").is_in(units) & ~pl.col("dup") & ~pl.col("voff") & pl.col("room").is_in([2, 3]))
        days = sorted(st["pt_date"].unique().to_list())
        rows = []
        for di, d in enumerate(days):
            s = st.filter(pl.col("pt_date") == d)
            ga = s.group_by("agent").agg(pl.col("sid"), pl.col("room").mode().sort().first().alias("room"), pl.len().alias("n")).filter(pl.col("n") >= 3)
            if ga.height < 4:
                continue
            Xa = np.array([Dt.V[np.asarray(ix)].mean(0) for ix in ga["sid"].to_list()])
            rr = ga["room"].to_numpy()
            if min((rr == 2).sum(), (rr == 3).sum()) < 2:
                continue

            def F(lab):
                a, b = Xa[lab == 2], Xa[lab == 3]
                ma, mb = a.mean(0), b.mean(0)
                sa = ((a - ma) ** 2).sum(1).sum() / max(len(a) - 1, 1)
                sb = ((b - mb) ** 2).sum(1).sum() / max(len(b) - 1, 1)
                return float(((ma - mb) ** 2).sum() / (sa / len(a) + sb / len(b)))
            f0 = F(rr)
            nul = np.array([F(rng.permutation(rr)) for _ in range(500)])
            rows.append(dict(day=d, di=di, n=int(ga.height), F=f0, z=float((f0 - nul.mean()) / nul.std(ddof=1)),
                             p=float((1 + (nul >= f0).sum()) / 501)))
        if not rows:
            continue
        df = pl.DataFrame(rows)
        from scipy.stats import spearmanr
        rho = spearmanr(df["di"].to_numpy(), df["F"].to_numpy()).statistic if df.height >= 3 else np.nan
        out[f"G{g}"] = dict(days=rows, spearman_F_day=float(rho) if np.isfinite(rho) else np.nan,
                            day0_F=rows[0]["F"], day0_z=rows[0]["z"], median_F=float(np.median(df["F"])))
        print(f"G{g} separation day0 F {rows[0]['F']:.1f} z {rows[0]['z']:.1f}; spearman {rho:.2f}; days {len(rows)}", flush=True)
    L.jdump(out, RES / "separation.json")
    return out


# ============================================================================================ NE42 (native)
def modal_room(Dt, units):
    s = Dt.st.filter(pl.col("unit_id").is_in(units) & ~pl.col("dup"))
    return dict(s.group_by("agent").agg(pl.col("room").mode().sort().first()).iter_rows())


def run_ne42(Dt):
    rng = np.random.default_rng(L.SEED + 2)
    m39, m41 = modal_room(Dt, ["39"]), modal_room(Dt, ["41"])
    part = {a: (0 if r == 2 else 1) for a, r in m39.items() if a in m41 and m41[a] == r and r in (2, 3)}
    dropped = sorted(set(m39) ^ set(m41) | {a for a in m39 if a in m41 and m39[a] != m41[a]})
    Cs = {}
    for u in ("39", "40", "41"):
        P = build_panel(Dt, u, "w30")
        Cs[u] = L.contributions(P, *L.deviations(P, 1))
    obs = {u: L.partition_ratio(Cs[u], part) for u in Cs}
    did = obs["40"]["r_X"] - 0.5 * (obs["39"]["r_X"] + obs["41"]["r_X"])
    nul = []
    for _ in range(1000 if not FAST else 200):
        pp = L.permute_partition(part, rng)
        r = {u: L.partition_ratio(Cs[u], pp)["r_X"] for u in Cs}
        nul.append([r["39"], r["40"], r["41"], r["40"] - 0.5 * (r["39"] + r["41"])])
    nul = np.array(nul, float)
    p_did = float((1 + (nul[:, 3] >= did).sum()) / (1 + np.isfinite(nul[:, 3]).sum()))
    p_unit = {u: float((1 + (nul[:, i] <= obs[u]["r_X"]).sum()) / (1 + np.isfinite(nul[:, i]).sum())) for i, u in enumerate(("39", "40", "41"))}
    bs = []
    for _ in range(300):
        r = {}
        for u, C in Cs.items():
            D = C["Cw"].shape[0]
            w = np.bincount(rng.integers(0, D, D), minlength=D)
            r[u] = L.partition_ratio(C, part, w)["r_X"]
        bs.append(r["40"] - 0.5 * (r["39"] + r["41"]))
    bs = np.array(bs, float)
    out = dict(partition={int(k): int(v) for k, v in part.items()}, n_part=[int(sum(v == 0 for v in part.values())), int(sum(v == 1 for v in part.values()))],
               dropped=[int(a) for a in dropped], obs=obs, DiD=did, p_DiD=p_did, p_unit_low=p_unit,
               DiD_ci=[float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
               null_rX_median=[float(np.nanmedian(nul[:, i])) for i in range(3)])
    print("NE42", {u: round(obs[u]["r_X"], 3) for u in obs}, "DiD", round(did, 3), "p", p_did, flush=True)
    L.jdump(out, RES / "ne42.json")
    return out


# ============================================================================================ G51 (native)
def run_g51(Dt):
    rng = np.random.default_rng(L.SEED + 3)
    units51 = Dt.units.filter(pl.col("goal_no") == 51).sort("seq")["unit_id"].to_list()
    out = {"single_room_G": {}}
    for u in units51:
        if u == "51g":
            continue
        P = build_panel(Dt, u, "w30")
        if P is None:
            continue
        r = L.panel_coherence(P, level=1, mw=Dt.mw.get(u, {}), n_perm=N_PERM, rng=rng, need_cross=False)
        o = r["obs"]
        out["single_room_G"][u] = dict(rho_w=o["rho_w"], rho_hi=o.get("rho_hi"), rho_lo=o.get("rho_lo"), G=o.get("G"),
                                       p_G_low=r.get("p_G_low"), n_agents=int(len(r["C"]["agents"])), tier_median=o.get("tier_median"))
        print(u, "G", o.get("G"), "rho_w", round(o["rho_w"], 3), flush=True)
    Gs = [v["G"] for v in out["single_room_G"].values() if v["G"] is not None and np.isfinite(v["G"])]
    out["median_G_single"] = float(np.median(Gs)) if Gs else np.nan
    # focus members
    s = Dt.st.filter((pl.col("unit_id") == "51g") & ~pl.col("dup"))
    ad = s.group_by("agent", "pt_date").agg(pl.col("room").mode().sort().first())
    fc = ad.filter(pl.col("room") == 15).group_by("agent").len().filter(pl.col("len") >= 2)
    F = set(fc["agent"].to_list())
    out["focus_members"] = sorted(int(a) for a in F)
    out["focus_days_per_member"] = {int(a): int(n) for a, n in fc.iter_rows()}
    Cs = {}
    for u in ("51f", "51g", "51h"):
        P = build_panel(Dt, u, "w30")
        Cs[u] = L.contributions(P, *L.deviations(P, 1))

    def rF(C, Fset, w=None):
        ags = list(C["agents"]); isF = np.array([int(a) in Fset for a in ags])
        FG = isF[:, None] ^ isF[None, :]
        GG = (~isF)[:, None] & (~isF)[None, :]
        a, na = L.class_rho(C, FG, "all", w); b, nb = L.class_rho(C, GG, "all", w)
        return (a / b if (np.isfinite(a) and np.isfinite(b) and b > 0) else np.nan), a, b, na, nb
    obs = {u: rF(Cs[u], F) for u in Cs}
    did = obs["51g"][0] - 0.5 * (obs["51f"][0] + obs["51h"][0])
    common = set(int(a) for a in Cs["51f"]["agents"]) & set(int(a) for a in Cs["51g"]["agents"]) & set(int(a) for a in Cs["51h"]["agents"])
    pool = sorted(common)
    nul = []
    for _ in range(1000 if not FAST else 200):
        Fp = set(rng.choice(pool, len(F & common), replace=False).tolist())
        r = {u: rF(Cs[u], Fp)[0] for u in Cs}
        nul.append(r["51g"] - 0.5 * (r["51f"] + r["51h"]))
    nul = np.array(nul, float)
    out["r_F"] = {u: dict(r_F=obs[u][0], rho_FG=obs[u][1], rho_GG=obs[u][2], n_FG=obs[u][3], n_GG=obs[u][4]) for u in obs}
    out["DiD"] = did
    out["p_DiD_low"] = float((1 + (nul <= did).sum()) / (1 + np.isfinite(nul).sum()))
    out["n_focus_in_common"] = len(F & common)
    print("G51 r_F", {u: round(obs[u][0], 3) for u in obs}, "DiD", round(did, 3), out["p_DiD_low"], flush=True)
    L.jdump(out, RES / "g51.json")
    return out


# ============================================================================================ detector
def run_detector(Dt):
    rng = np.random.default_rng(L.SEED + 4)
    sc = pl.read_parquet(L.ROOT / "data/processed/H36-reorganization-alarm/scores.parquet").select("aday", "pt_date", "goal_no", "R1", "placebo", "dist_event")
    ds = pl.read_parquet(L.ROOT / "data/processed/H36-reorganization-alarm/day_stats.parquet").select("pt_date", "R1_shift")
    ard = pl.read_parquet(L.OUT / "agent_room_day.parquet")
    adall = pl.read_parquet(L.SH / "embeddings/agent_day.parquet")
    av = np.load(L.SH / "embeddings/agent_day_vec.npy").astype(np.float32)
    mu = av[adall.filter(~pl.col("holdout"))["gid"].to_numpy()].mean(0)     # H36's centering (Amendment 0e there)
    cc = set(pl.read_parquet(L.SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list())
    cal = Dt.cal.select("pt_date", "goal_no", "holdout").with_row_index("aday")
    days = cal["pt_date"].to_list(); hol = cal["holdout"].to_list()
    vec = {}
    for gid, a, d, r in ard.select("gid", "agent", "pt_date", "room").iter_rows():
        if a in cc:
            continue
        x = av[gid] - mu
        vec.setdefault(d, {})[a] = (x / max(np.linalg.norm(x), 1e-9), int(r))
    # check: my swarm R1 (all agent_day rows incl. Claude Code) vs H36's R1_shift
    rows = []
    perroom = {}
    for i in range(1, len(days)):
        d, dp = days[i], days[i - 1]
        if hol[i] or hol[i - 1] or d < "2026-02-25" or d not in vec or dp not in vec:
            continue
        common = sorted(set(vec[d]) & set(vec[dp]))
        if len(common) < 3:
            continue
        Vd = np.array([vec[d][a][0] for a in common]); Vp = np.array([vec[dp][a][0] for a in common])
        rd = np.array([vec[d][a][1] for a in common]); rp = np.array([vec[dp][a][1] for a in common])
        multi = (len([r for r in np.unique(rd) if (rd == r).sum() >= 2]) >= 2) or (len([r for r in np.unique(rp) if (rp == r).sum() >= 2]) >= 2)
        z, coh = L.r1_loc(Vd, Vp, rd, rp, rng, n_rand=100 if FAST else 300) if multi else (np.nan, [])
        for r in np.unique(rd):
            m = rd == r
            if m.sum() >= 2:
                perroom.setdefault(int(r), {})[d] = L.r1_shift(Vd[m].mean(0), Vp[m].mean(0))
        best = max(coh, key=lambda c: c["z"]) if coh else None
        rows.append(dict(pt_date=d, n_common=len(common), multiroom=bool(multi), R1_loc=z,
                         loc_best=("|".join(best["tags"]) + f":{best['size']}") if best else None,
                         rooms_d=",".join(f"{int(r)}:{int((rd == r).sum())}" for r in np.unique(rd))))
    det = pl.DataFrame(rows)
    # per-room R1 with trailing z per room over its own (non-holdout) history
    zroom = {}
    for r, ser in perroom.items():
        ds_ = sorted(ser)
        z = trailing_z(np.array([ser[d] for d in ds_]))
        for d, v in zip(ds_, z):
            zroom.setdefault(d, {})[r] = v
    det = det.with_columns(
        pl.Series("R1_room", [np.nanmax([v for v in zroom.get(d, {}).values() if np.isfinite(v)]) if any(np.isfinite(v) for v in zroom.get(d, {}).values()) else np.nan for d in det["pt_date"].to_list()]),
        pl.Series("R1_room_which", [max(((r, v) for r, v in zroom.get(d, {}).items() if np.isfinite(v)), key=lambda x: x[1], default=(None, None))[0] for d in det["pt_date"].to_list()], dtype=pl.Int64))
    det = det.join(sc, on="pt_date", how="left").join(ds, on="pt_date", how="left")
    det = det.with_columns(pl.max_horizontal(pl.col("R1").fill_nan(None), pl.col("R1_loc").fill_nan(None)).alias("R1_comb"))
    # events
    ev = [("NE42a", "2026-05-04", "merge into #universe-coordination", True),
          ("NE42b", "2026-05-11", "split back to #best/#rest", True),
          ("focus-open", "2026-08-05", "#focus room opens", False),
          ("focus-close", "2026-08-24", "#focus empties (51h)", False),
          ("side-room", "2026-07-24", "side-room (1 agent; roster join same day)", True)]
    # minor: transfers between #best and #rest (>= 2 agents switching modal room on a goal kickoff)
    for d in ("2026-04-02", "2026-04-27"):
        i = days.index(d)
        dp = days[i - 1]
        sw = [a for a in set(vec.get(d, {})) & set(vec.get(dp, {})) if {vec[d][a][1], vec[dp][a][1]} == {2, 3}]
        if len(sw) >= 2:
            ev.append((f"transfer-{d[5:]}", d, f"{len(sw)} agents switch #best/#rest (goal kickoff)", True))
    detd = det["pt_date"].to_list()
    idx = {d: i for i, d in enumerate(detd)}
    # placebo: H36 placebo, multi-room, and >= 3 rows from focus-close (an event H36 did not catalogue)
    fcl = idx.get("2026-08-24")
    plac = [(p and m and (fcl is None or abs(i - fcl) >= 3)) for i, (p, m) in enumerate(zip(det["placebo"].fill_null(False).to_list(), det["multiroom"].to_list()))]
    det = det.with_columns(pl.Series("placebo_mr", plac))
    scores = ["R1", "R1_room", "R1_loc", "R1_comb"]
    P = {s: det.filter(pl.col("placebo_mr"))[s].fill_null(np.nan).to_numpy().astype(float) for s in scores}
    far3 = {s: float(np.nanmean(P[s] >= 3)) for s in scores}
    # threshold for R1_loc matched to R1 >= 3's placebo FAR (if that FAR is 0, use 3)
    thr = {"R1": 3.0, "R1_room": 3.0, "R1_comb": 3.0}
    fr = far3["R1"]
    thr["R1_loc"] = float(np.nanquantile(P["R1_loc"], 1 - fr)) if fr > 0 else 3.0
    evrows = []
    for ref, d, lab, conf in ev:
        i = idx.get(d)
        rec = dict(ref=ref, day0=d, label=lab, goal_confounded=conf, scorable=i is not None)
        if i is not None:
            for s in scores:
                vals = {o: (det[s][i + o] if 0 <= i + o < det.height else None) for o in (-1, 0, 1)}
                vals = {o: (float(v) if v is not None and np.isfinite(v) else np.nan) for o, v in vals.items()}
                rec[f"{s}_d0"] = vals[0]; rec[f"{s}_dm1"] = vals[-1]; rec[f"{s}_dp1"] = vals[1]
                rec[f"{s}_hit"] = bool(any(np.isfinite(v) and v >= thr[s] for v in vals.values()))
            rec["loc_best_d0"] = det["loc_best"][i]
            rec["rooms_d0"] = det["rooms_d"][i]
            rec["R1_room_which_d0"] = det["R1_room_which"][i]
        evrows.append(rec)
    evdf = pl.DataFrame(evrows)
    res = dict(thresholds=thr, placebo_n=int(np.sum(plac)), far_placebo={s: float(np.nanmean(P[s] >= thr[s])) for s in scores},
               far3=far3, events=evrows)
    for subset, name in ((lambda r: r["scorable"], "all_room_events"), (lambda r: r["scorable"] and not r["goal_confounded"], "clean_room_events")):
        sel = [r for r in evrows if subset(r)]
        res[name] = {}
        for s in scores:
            pos = np.array([r[f"{s}_d0"] for r in sel], float)
            res[name][s] = dict(AUC=auc(pos, P[s]), AUC_ci=list(auc_ci(pos, P[s], rng, 1000)), n_events=int(np.isfinite(pos).sum()),
                                hits=int(sum(r[f"{s}_hit"] for r in sel)))
    # goal kickoffs in multi-room periods (secondary: is the shift room-localized?)
    gk = {"#36": "2026-03-23", "#37": "2026-03-30", "#38": "2026-04-02", "#39": "2026-04-27", "#40": "2026-05-04", "#41": "2026-05-11",
          "#42": "2026-05-18", "#44": "2026-05-26"}
    res["goal_kickoffs"] = {g: {s: (float(det[s][idx[d]]) if d in idx and det[s][idx[d]] is not None and np.isfinite(det[s][idx[d]]) else None) for s in scores} | {"loc_best": det["loc_best"][idx[d]] if d in idx else None}
                            for g, d in gk.items()}
    # sanity: my swarm R1 vs H36's R1_shift is not identical by construction (H36 includes Claude Code); report correlation
    det.write_parquet(RES / "detector_days.parquet")
    L.jdump(res, RES / "detector.json")
    for r in evrows:
        print(r["ref"], {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items() if k.endswith("_d0") or k.endswith("_hit")}, flush=True)
    print("AUC", {k: {s: round(v["AUC"], 2) if v["AUC"] == v["AUC"] else None for s, v in res[k].items()} for k in ("all_room_events", "clean_room_events")})
    return res


# ============================================================================================ leadership
def run_leadership(Dt):
    rng = np.random.default_rng(L.SEED + 5)
    sh = pl.read_parquet(L.SH / "embeddings/statements.parquet", columns=["kind", "src_row"]).with_row_index("st_row")
    st = Dt.st.join(sh, on="st_row", how="left")
    chat_raw = np.load(L.SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    int_raw = np.load(L.SH / "embeddings/intentions_bge_small.npy", mmap_mode="r")
    kk = pl.read_parquet(L.OUT / "kickoffs.parquet")
    kick = {(g, r): t for g, r, t in kk.iter_rows()}
    cal = Dt.cal.filter(~pl.col("holdout"))
    nh_days = cal["pt_date"].to_list()
    goal_of = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    events = {36: "2026-03-23", 37: "2026-03-30", 38: "2026-04-02", 39: "2026-04-27", 40: "2026-05-04", 41: "2026-05-11",
              42: "2026-05-18", 44: "2026-05-26"}
    out = {}

    def rawvec(s):
        k = s["kind"].to_numpy(); src = s["src_row"].to_numpy().astype(np.int64)
        X = np.zeros((len(k), 384), np.float32)
        for name, arr in (("chat", chat_raw), ("intent", int_raw)):
            m = k == name
            if m.any():
                o = np.argsort(src[m]); tmp = np.empty((m.sum(), 384), np.float32)
                tmp[o] = np.asarray(arr[src[m][o]], np.float32); X[m] = tmp
        return X
    zs = []
    for g, d0 in events.items():
        i0 = nh_days.index(d0)
        pre = nh_days[i0 - 1]
        post = [d for d in nh_days[i0 + 1:i0 + 3] if goal_of[d] == g]
        s = st.filter(~pl.col("dup"))
        s0 = s.filter(pl.col("pt_date") == d0)
        if g == 40:
            ref = s.filter(pl.col("pt_date") == pre)
        else:
            ref = s0
        cm = dict(ref.group_by("agent").agg(pl.col("room").mode().sort().first()).iter_rows())
        coh = {int(a): (0 if r == 2 else 1) for a, r in cm.items() if r in (2, 3)}
        if g == 41:
            kt = {0: kick.get((41, 4)), 1: kick.get((41, 4))}
        else:
            kt = {0: kick.get((g, 2)), 1: kick.get((g, 3))}
        s0 = s0.filter(pl.col("agent").is_in(list(coh)))
        tau = np.array([(t - kt[coh[int(a)]]).total_seconds() / 60 for t, a in zip(s0["t"].to_list(), s0["agent"].to_list())])
        keep = tau >= 0
        spre = s.filter((pl.col("pt_date") == pre) & pl.col("agent").is_in(list(coh)))
        spost = s.filter(pl.col("pt_date").is_in(post) & pl.col("agent").is_in(list(coh)))
        ev = dict(tau=tau[keep], X=rawvec(s0)[keep], agent=s0["agent"].to_numpy()[keep], Xpre=rawvec(spre), apre=spre["agent"].to_numpy(),
                  Xpost=rawvec(spost), apost=spost["agent"].to_numpy(), coh=coh)
        r = L.lead_test(ev, rng, n_perm=200 if FAST else 500, n_boot=100 if FAST else 300)
        # per-statement projection noise on post days (y units) for comparison with the synthetic 0.7
        pre_m = L.cohort_means(ev["apre"], ev["Xpre"], coh); post_m = L.cohort_means(ev["apost"], ev["Xpost"], coh)
        cpost = np.array([coh[int(a)] for a in ev["apost"]])
        ysd = []
        for c in (0, 1):
            dl = post_m[c] - pre_m[c]
            y = (ev["Xpost"][cpost == c] - pre_m[c]) @ dl / max(np.linalg.norm(dl) ** 2, 1e-12)
            ysd.append(float(np.std(y)))
        z = r["obs"]["L"] / r["null_L_sd"] if r["null_L_sd"] > 0 and np.isfinite(r["obs"]["L"]) else np.nan
        zs.append(z)
        out[f"#{g}"] = dict(day0=d0, pre=pre, post=post, n_best=int(sum(v == 0 for v in coh.values())), n_rest=int(sum(v == 1 for v in coh.values())),
                            n_stmt_day0=int(keep.sum()), L=r["obs"]["L"], dT50_bins=r["obs"]["dT50"], n_common_bins=r["obs"]["n_common"],
                            p_L=r["p_L"], p_T50=r["p_T50"], L_ci=r["L_ci"], z=z, y_noise_sd=ysd,
                            yb=r["yb"], nb=r["nb"], kick_lag_s=(kt[1] - kt[0]).total_seconds() if kt[0] and kt[1] else None,
                            cohorts="previous rooms" if g == 40 else ("new rooms (kickoff in the merged room)" if g == 41 else "rooms"))
        print(f"#{g} L {r['obs']['L']:.3f} p {r['p_L']:.3f} dT50 {r['obs']['dT50']} p {r['p_T50']:.3f} ci {r['L_ci']} ysd {ysd}", flush=True)
    zz = np.array([z for z in zs if np.isfinite(z)])
    from scipy.stats import norm
    Z = float(zz.sum() / np.sqrt(len(zz))) if len(zz) else np.nan
    sig = [k for k, v in out.items() if v["p_L"] < 0.05]
    out["_pooled"] = dict(stouffer_Z=Z, p_two_sided=float(2 * norm.sf(abs(Z))) if np.isfinite(Z) else np.nan, n=len(zz),
                          n_best_ahead=int((zz > 0).sum()), n_sig=len(sig), sig=sig,
                          same_leader_share_sig=(max(sum(out[k]["L"] > 0 for k in sig), sum(out[k]["L"] < 0 for k in sig)) / len(sig)) if sig else np.nan)
    print("pooled", out["_pooled"])
    L.jdump(out, RES / "leadership.json")
    return out


def main():
    t0 = time.time()
    RES.mkdir(parents=True, exist_ok=True)
    Dt = Data()
    if want("coherence"):
        run_coherence(Dt)
    if want("separation"):
        run_separation(Dt)
    if want("ne42"):
        run_ne42(Dt)
    if want("g51"):
        run_g51(Dt)
    if want("detector"):
        run_detector(Dt)
    if want("leadership"):
        run_leadership(Dt)
    print("done", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
