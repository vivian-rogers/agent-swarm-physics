"""H25 exploratory round 1: the daily criticality dial on every non-holdout day, per channel, and the card's tests.

Primary dial (public API, dial.compute_dial): activity and talk with null-calibrated stalls masked and 30-min block
detrending; content with agent-day centering, the day's exogenous directions removed (F2) and self near-copies dropped.
Sensitivity variants (dial's lower-level functions, identical estimator):
  activity/talk: stall none | auto (primary) | lull (H12 filter) | h38_sched | h38_exo; block 15 | 60 (auto);
                 sched (cross-fitted time-of-day profile instead of block means; auto); scale5/scale10 diagnostics
  content:       F1 (agent-day centering only) | F2 (primary) | F3 (F2 + 3 directions cross-fitted on the period's
                 other days) | F2nodedup | F2split (split-half noise correction) | F2tod (POST HOC, added after a 3-day
                 smoke test: F2 plus a cross-fitted time-of-day content profile, i.e. each 30-min window position's
                 mean collective content on the period's other days, subtracted: the content "daily schedule")
Outputs (data/processed/H25-criticality-dial/): dial_daily.parquet, dial_period.parquet, events.parquet,
results/explore.json, G<NN>/dial_daily.parquet + G<NN>/results.json.
Usage: uv run python hypotheses/H25-criticality-dial/analysis/explore.py [--data-version fixed]
Round 1b (2026-10-04): --data-version fixed reads inputs_r1b/ (spins from activity_bins_fixed, H38 masks from the
shared outages_fixed sidecar) and writes everything under data/processed/H25-criticality-dial/r1b/. Both versions add
the DQ8-design variant `trim` (activity, talk): the auto stall mask AND the all-present window (every population agent
between its first and last active minute of the day), applied before the block-shift null is drawn.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

if "--data-version" in sys.argv:
    os.environ["H25_DATA_VERSION"] = sys.argv[sys.argv.index("--data-version") + 1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h25common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

import dial as D  # noqa: E402

INP = C.INP_BASE            # statements, exo (version-independent)
INPV = C.INPV               # spins, h38_masks, refs (version-dependent)
RES = C.RESD / "results"
N_BOOT, N_NULL = 300, 100
MIN_ACT, MIN_TALK = 10, 5

_G: dict = {}


def seed_of(*xs) -> int:
    return int(hashlib.sha1("|".join(map(str, xs)).encode()).hexdigest()[:8], 16)


def load():
    spins = pl.read_parquet(INPV / "spins.parquet")
    st = pl.read_parquet(INP / "statements.parquet")
    V = np.load(INP / "statements_vec.npy").astype(np.float32)
    ex = pl.read_parquet(INP / "exo.parquet")
    EV = np.load(INP / "exo_vec.npy").astype(np.float32)
    h38 = pl.read_parquet(INPV / "h38_masks.parquet") if (INPV / "h38_masks.parquet").exists() else None
    cal = C.calendar_nonholdout()
    C.assert_no_holdout(cal["pt_date"], cal["goal_no"])
    assert set(spins["pt_date"].unique().to_list()) <= set(cal["pt_date"].to_list())
    return spins, st, V, ex, EV, h38, cal


# ----------------------------------------------------------------------------- per-day work
def day_matrices(sp: pl.DataFrame):
    agents = sorted(sp["agent"].unique().to_list())
    piv = sp.pivot(on="agent", index="minute", values="state").sort("minute")
    St = piv.select([str(a) for a in agents]).fill_null(1).to_numpy()
    return piv["minute"].to_numpy(), agents, St


def sched_profile(spins_period: pl.DataFrame, day: str, agents, minute, thr):
    """Cross-fitted time-of-day profile: each agent's mean spin in each 30-min time-of-day bin over the OTHER days."""
    o = spins_period.filter((pl.col("pt_date") != day) & pl.col("agent").is_in(agents))
    if o.height == 0:
        return None
    prof = (o.with_columns((pl.col("minute") // 30).alias("tb"), pl.when(pl.col("state") >= thr).then(1.0).otherwise(-1.0).alias("s"))
            .group_by("agent", "tb").agg(pl.col("s").mean()))
    P = np.full((len(minute), len(agents)), np.nan)
    tb = minute // 30
    for j, a in enumerate(agents):
        pa = prof.filter(pl.col("agent") == a)
        if pa.height:
            mp = dict(zip(pa["tb"].to_list(), pa["s"].to_list()))
            P[:, j] = [mp.get(int(t), np.nan) for t in tb]
    return P


def run_binary_variants(day, sp, sp_period, h38d, rng):
    minute, agents, St = day_matrices(sp)
    active, talk, anyev = St >= 3, St == 4, St >= 2
    nact, ntalk = active.sum(0), talk.sum(0)
    popA = nact >= MIN_ACT
    m_auto, Lstar = D.find_stalls(anyev[:, popA], minute) if popA.sum() >= 1 else (np.zeros(len(minute), bool), None)
    masks = {"none": np.ones(len(minute), bool), "auto": ~m_auto}
    masks["lull"] = active[:, popA].sum(1) >= 2
    # round 1b (DQ8): all-present window of the activity population (first..last active minute of every agent)
    T_ = len(minute)
    if popA.sum() >= 1:
        A_ = active[:, popA]
        has = A_.any(0)
        f_ = np.argmax(A_, axis=0); l_ = T_ - 1 - np.argmax(A_[::-1], axis=0)
        win = ((np.arange(T_)[:, None] >= f_[None, :]) & (np.arange(T_)[:, None] <= l_[None, :]))[:, has].all(1)
    else:
        win = np.ones(T_, bool)
    masks["trim"] = masks["auto"] & win
    if h38d is not None and h38d.height:
        for k in ("sched", "exo"):
            mm = set(h38d.filter(pl.col(k))["minute"].to_list())
            masks[f"h38_{k}"] = ~np.isin(minute, list(mm))
    rows = []
    for ch, X, cnt, thr, mth in (("activity", active, nact, MIN_ACT, 3), ("talk", talk, ntalk, MIN_TALK, 4)):
        pop = cnt >= thr
        base = {"pt_date": day, "channel": ch, "N_pop": int(pop.sum()), "T_day": int(len(minute)), "stall_min": int(m_auto.sum()),
                "stall_Lstar": Lstar}
        if pop.sum() < 3:
            rows.append({**base, "variant": "auto", "flag": "too_few_agents"}); continue
        S = np.where(X[:, pop], 1.0, -1.0)
        todo = [(v, masks[v], 30, None) for v in masks] + [("b15", masks["auto"], 15, None), ("b60", masks["auto"], 60, None)]
        P = sched_profile(sp_period, day, [a for a, p in zip(agents, pop) if p], minute, mth)
        if P is not None:
            P = np.where(np.isnan(P), S.mean(0, keepdims=True), P)
            todo.append(("sched", masks["auto"], 30, P))
        for v, valid, bm, center in todo:
            r = D.binary_day(S, minute, valid=valid, center=center, block_min=bm, n_boot=N_BOOT, n_null=N_NULL, rng=rng)
            if r is None:
                rows.append({**base, "variant": v, "flag": "too_short"}); continue
            rows.append({**base, "variant": v, "N": r.N, "T": r.T, "VR": r.VR, "g": r.g, "se": r.se, "lo": r.lo, "hi": r.hi,
                         "null_mean": r.null_mean, "null_q95": r.null_q95, "p_null": r.p_null, "q_bar": r.q_bar,
                         "masked_min": int((~valid).sum()), "flag": "ok"})
        for dl in (5, 10):
            gs, gl = D.vr_scale(S, minute, valid=masks["auto"], delta=dl, block_min=60)
            rows.append({**base, "variant": f"scale{dl}", "g": gs, "g_long": gl, "flag": "ok" if np.isfinite(gs) else "too_short"})
    return rows


def content_parts(day, st, V, ex, EV, dedup=True):
    s = st.with_row_index("_i").filter(pl.col("pt_date") == day)
    if dedup:
        s = s.filter(~pl.col("dup"))
    if s.height < 6:
        return None
    s = s.sort("agent", "window", "minute")
    U = V[s["_i"].to_numpy()]
    e = ex.with_row_index("_i").filter(pl.col("pt_date") == day)
    E = EV[e["_i"].to_numpy()] if e.height else None
    return U, s["agent"].to_numpy(), s["window"].to_numpy(), D.exo_directions(E, 5) if E is not None else None


def collective_trajectory(U, ag, wn, rd):
    """Cross-agent mean of agent-day-centered window means (F2), per window with >= 2 agents (for F3 cross-fitting)."""
    if rd is not None:
        Q = D._orth_basis([rd], U.shape[1]); U = U - (U @ Q) @ Q.T
    out = []
    df = pl.DataFrame({"a": ag, "w": wn})
    for a in np.unique(ag):
        m = ag == a
        ws = np.unique(wn[m])
        if len(ws) < 2:
            continue
        Vw = np.array([U[m & (wn == w)].mean(0) for w in ws])
        Vw -= Vw.mean(0)
        out += [(w, v) for w, v in zip(ws, Vw)]
    if not out:
        return None
    W = np.array([w for w, _ in out]); X = np.array([v for _, v in out])
    rows = [X[W == w].mean(0) for w in np.unique(W) if (W == w).sum() >= 2]
    return np.array(rows) if rows else None


def window_profile(U, ag, wn, rd) -> dict:
    """{window: cross-agent mean of agent-day-centered window means} after F2 (for the F2tod profile)."""
    if rd is not None:
        Q = D._orth_basis([rd], U.shape[1]); U = U - (U @ Q) @ Q.T
    acc: dict = {}
    for a in np.unique(ag):
        m = ag == a
        ws = np.unique(wn[m])
        if len(ws) < 2:
            continue
        Vw = np.array([U[m & (wn == w)].mean(0) for w in ws]); Vw -= Vw.mean(0)
        for w, v in zip(ws, Vw):
            acc.setdefault(int(w), []).append(v)
    return {w: np.mean(v, 0) for w, v in acc.items() if len(v) >= 2}


def run_content_variants(day, parts, parts_nodedup, f3dirs, rng, todprof=None):
    rows = []
    if parts is None:
        return [{"pt_date": day, "channel": "content", "variant": "F2", "flag": "too_few_statements"}]
    U, ag, wn, rd = parts
    for v in ("F1", "F2", "F3", "F2nodedup", "F2split", "F2tod"):
        if v == "F3" and f3dirs is None:
            continue
        if v == "F2tod" and not todprof:
            continue
        if v == "F2nodedup":
            if parts_nodedup is None:
                continue
            Uv, agv, wnv, rdv = parts_nodedup
        else:
            Uv, agv, wnv, rdv = U, ag, wn, rd
        dirs = None if v == "F1" else rdv
        if v == "F3":
            dirs = f3dirs if dirs is None else np.vstack([dirs, f3dirs])
        if v == "F2tod":  # subtract the cross-fitted window-position profile (projected the same way as the data)
            prof = np.array([todprof.get(int(w), np.zeros(Uv.shape[1])) for w in wnv])
            if rdv is not None:
                Q = D._orth_basis([rdv], Uv.shape[1]); prof = prof - (prof @ Q) @ Q.T
            Uv = Uv - prof
        r = D.content_day(Uv, agv, wnv, remove_dirs=dirs, n_boot=N_BOOT, n_null=N_NULL, rng=rng,
                          method="split" if v == "F2split" else "moment")
        base = {"pt_date": day, "channel": "content", "variant": v}
        if r is None:
            rows.append({**base, "flag": "too_few_agents"}); continue
        rows.append({**base, "N": r.N, "T": r.W, "VR": r.VR, "g": r.g, "se": r.se, "lo": r.lo, "hi": r.hi, "null_mean": r.null_mean,
                     "null_q95": r.null_q95, "p_null": r.p_null, "n_stmt": r.n_stmt, "k_removed": r.k_removed, "flag": "ok"})
    return rows


def job(day):
    spins, st, V, ex, EV, h38, cal, f3, tod = (_G[k] for k in ("spins", "st", "V", "ex", "EV", "h38", "cal", "f3", "tod"))
    g = int(cal.filter(pl.col("pt_date") == day)["goal_no"][0])
    rng = np.random.default_rng(seed_of("H25", day))
    sp = spins.filter(pl.col("pt_date") == day)
    spp = spins.filter(pl.col("goal_no") == g)
    h38d = h38.filter(pl.col("pt_date") == day) if h38 is not None else None
    rows = run_binary_variants(day, sp, spp, h38d, rng)
    rows += run_content_variants(day, content_parts(day, st, V, ex, EV), content_parts(day, st, V, ex, EV, dedup=False), f3.get(day), rng,
                                 todprof=tod.get(day))
    # the public API on the primary variant (must agree with the 'auto' / 'F2' rows up to bootstrap noise)
    ms = sp.select(pl.col("pt_date").alias("day"), pl.col("minute").cast(pl.Int32), "agent", (pl.col("state") >= 3).alias("active"),
                   (pl.col("state") == 4).alias("talk"), (pl.col("state") >= 2).alias("any_event"))
    s = st.with_row_index("_i").filter((pl.col("pt_date") == day) & ~pl.col("dup"))
    e = ex.with_row_index("_i").filter(pl.col("pt_date") == day)
    api = D.compute_dial(ms, statements=s.select(pl.col("pt_date").alias("day"), "minute", "agent", "window"),
                         statement_vectors=V[s["_i"].to_numpy()],
                         exo_statements=e.select(pl.col("pt_date").alias("day"), "minute") if e.height else None,
                         exo_vectors=EV[e["_i"].to_numpy()] if e.height else None, n_boot=200, n_null=50, seed=seed_of("api", day))
    for r in api.iter_rows(named=True):
        rows.append({"pt_date": day, "channel": r["channel"], "variant": "api", "N": r.get("N"), "T": r.get("T"),
                     "g": r.get("g"), "se": r.get("se"), "lo": r.get("lo"), "hi": r.get("hi"), "null_q95": r.get("null_q95"),
                     "flag": r.get("flag")})
    return rows


def init_worker(d):
    _G.update(d)


def f3_directions(st, V, ex, EV, cal) -> tuple[dict, dict]:
    """For each day: top-3 directions of the period's collective content trajectory on its OTHER days (cross-fitted),
    and the cross-fitted window-position profile (mean over the other days' window profiles) for F2tod."""
    traj, wprof = {}, {}
    for day in cal["pt_date"].to_list():
        p = content_parts(day, st, V, ex, EV)
        traj[day] = collective_trajectory(*p) if p is not None else None
        wprof[day] = window_profile(*p) if p is not None else {}
    tod = {}
    for g in cal["goal_no"].unique().to_list():
        days = cal.filter(pl.col("goal_no") == g)["pt_date"].to_list()
        for d in days:
            acc: dict = {}
            for x in days:
                if x != d:
                    for w, v in wprof.get(x, {}).items():
                        acc.setdefault(w, []).append(v)
            if acc:
                tod[d] = {w: np.mean(v, 0) for w, v in acc.items()}
    out = {}
    for g in cal["goal_no"].unique().to_list():
        days = cal.filter(pl.col("goal_no") == g)["pt_date"].to_list()
        for d in days:
            others = [traj[x] for x in days if x != d and traj.get(x) is not None]
            if not others:
                continue
            X = np.vstack(others)
            if len(X) < 4:
                continue
            _, _, Vt = np.linalg.svd(X, full_matrices=False)
            out[d] = Vt[:3]
    return out, tod


# ----------------------------------------------------------------------------- tests
def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5:
        return {"rho": np.nan, "p": np.nan, "n": int(ok.sum())}
    r, p = stats.spearmanr(a[ok], b[ok])
    return {"rho": float(r), "p": float(p), "n": int(ok.sum())}


def period_table(daily: pl.DataFrame, cal: pl.DataFrame) -> pl.DataFrame:
    rows = []
    ok = daily.filter((pl.col("flag") == "ok") & pl.col("g").is_not_null() & pl.col("se").is_not_null())
    for (g, ch, v), d in ok.group_by(["goal_no", "channel", "variant"]):
        a = D.aggregate_days(d["g"].to_numpy(), d["se"].to_numpy())
        rows.append({"goal_no": g, "channel": ch, "variant": v, **{k: a.get(k) for k in ("k", "fe", "se_fe", "re", "se_re", "tau2", "Q", "p_Q", "I2", "median")},
                     "frac_hi_lt_08": float((d["hi"] < 0.8).mean()), "max_lo": float(d["lo"].max()),
                     "N_med": float(d["N"].median()) if "N" in d.columns else None})
    return pl.DataFrame(rows).sort("goal_no", "channel", "variant")


def event_tests(daily: pl.DataFrame, cal: pl.DataFrame, rng) -> tuple[dict, pl.DataFrame]:
    prim = {"activity": "auto", "talk": "auto", "content": "F2"}
    out, ev_rows = {}, []
    held = set(C.load_holdout()["goal_periods_held_out"])
    gp = cal.group_by("goal_no").agg(pl.col("pt_date").sort()).sort("goal_no")
    gdays = {int(r["goal_no"]): r["pt_date"] for r in gp.iter_rows(named=True)}
    for ch, v in prim.items():
        d = daily.filter((pl.col("channel") == ch) & (pl.col("variant") == v) & (pl.col("flag") == "ok") & pl.col("se").is_finite() & (pl.col("se") > 0))
        gmap = dict(zip(d["pt_date"].to_list(), zip(d["g"].to_list(), d["se"].to_list())))

        def step(before, after):
            b = [gmap[x] for x in before if x in gmap]; a = [gmap[x] for x in after if x in gmap]
            if len(b) < 1 or len(a) < 1:
                return None
            fb = D.aggregate_days([x[0] for x in b], [x[1] for x in b]); fa = D.aggregate_days([x[0] for x in a], [x[1] for x in a])
            # random-effects means: day-to-day heterogeneity counts as noise around the step
            delta = fa["re"] - fb["re"]; se = float(np.sqrt(fa["se_re"] ** 2 + fb["se_re"] ** 2))
            return {"delta": float(delta), "se": se, "z": float(delta / se) if se > 0 else np.nan, "nb": len(b), "na": len(a)}
        # (a) regime switch 2026-03-24: regime-II days of #35-#36 vs regime-III days of #36-#37
        before = [x for x in gdays.get(35, []) + gdays.get(36, []) if x < "2026-03-24"]
        after = [x for x in gdays.get(36, []) + gdays.get(37, []) if x >= "2026-03-24"]
        s = step(before, after)
        if s:
            s.update({"lo90": s["delta"] - 1.645 * s["se"], "hi90": s["delta"] + 1.645 * s["se"]})
        out[f"regime_switch_{ch}"] = s
        # (b) goal changes between adjacent non-holdout periods
        evs = []
        goals = sorted(gdays)
        for g0, g1 in zip(goals[:-1], goals[1:]):
            if g1 != g0 + 1 or g0 in held or g1 in held:
                continue
            s2 = step(gdays[g0][-2:], gdays[g1][:2])
            if s2:
                tag = {(7, 8): "hours 2h->3h", (17, 18): "hours 3h->4h", (39, 40): "room merge", (40, 41): "room split",
                       (35, 36): "regime switch inside #36 follows", (9, 10): "batch join"}.get((g0, g1), "")
                evs.append({"channel": ch, "kind": "goal_change", "boundary": f"#{g0}->#{g1}", "date": gdays[g1][0], "tag": tag, **s2})
        plac = []
        for g, days in gdays.items():
            for k in range(1, len(days) - 2):
                s3 = step(days[max(0, k - 1):k + 1], days[k + 1:k + 3])
                if s3 and k + 1 < len(days):
                    plac.append({"channel": ch, "kind": "placebo", "boundary": f"#{g} {days[k]}|{days[k + 1]}", "date": days[k + 1], "tag": "", **s3})
        # (c) exploratory within-period events in #51
        for date, tag in (("2026-07-09", "NE32 isolated newcomers"), ("2026-09-03", "NE33 batch join")):
            days = gdays.get(51, [])
            if date in days:
                k = days.index(date)
                s4 = step(days[max(0, k - 2):k], days[k:k + 2])
                if s4:
                    evs.append({"channel": ch, "kind": "within_51", "boundary": f"#51 {date}", "date": date, "tag": tag, **s4})
        ev_rows += evs + plac
        ze = np.array([abs(e["z"]) for e in evs if e["kind"] == "goal_change" and np.isfinite(e["z"])])
        zp = np.array([abs(p["z"]) for p in plac if np.isfinite(p["z"])])
        if len(ze) and len(zp) >= len(ze):
            draws = np.array([rng.choice(zp, size=len(ze), replace=False).mean() for _ in range(5000)])
            out[f"goal_change_{ch}"] = {"n_events": int(len(ze)), "n_placebo": int(len(zp)), "mean_abs_z_events": float(ze.mean()),
                                        "placebo_q95": float(np.quantile(draws, 0.95)), "p": float((1 + (draws >= ze.mean()).sum()) / 5001),
                                        "mean_abs_z_placebo": float(zp.mean())}
    return out, pl.DataFrame(ev_rows)


def lopo_map(x, y):
    """LOPO squared errors: affine y ~ a + b x vs constant, per period."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    e_map, e_c = [], []
    for i in range(len(x)):
        m = np.arange(len(x)) != i
        b, a = np.polyfit(x[m], y[m], 1)
        e_map.append((y[i] - (a + b * x[i])) ** 2); e_c.append((y[i] - y[m].mean()) ** 2)
    return np.array(e_map), np.array(e_c)


def lopo_regime(y, reg):
    y = np.asarray(y, float); reg = np.asarray(reg)
    e = []
    for i in range(len(y)):
        m = (np.arange(len(y)) != i) & (reg == reg[i]) & np.isfinite(y)
        e.append((y[i] - y[m].mean()) ** 2 if m.sum() else np.nan)
    return np.array(e)


def tests(daily, per, refs, cal, ev_out) -> dict:
    R = {}
    prim = {"activity": "auto", "talk": "auto", "content": "F2"}
    okd = daily.filter((pl.col("flag") == "ok") & pl.col("g").is_not_null())
    # P1 subcritical
    p1 = {}
    for ch, v in prim.items():
        d = okd.filter((pl.col("channel") == ch) & (pl.col("variant") == v) & pl.col("hi").is_not_null())
        p1[ch] = {"n_days": d.height, "frac_hi_lt_08": float((d["hi"] < 0.8).mean()), "n_lo_gt_05": int((d["lo"] > 0.5).sum()),
                  "n_lo_gt_08": int((d["lo"] > 0.8).sum()), "max_hi": float(d["hi"].max()), "max_g": float(d["g"].max())}
    p1["verdict"] = ("supported" if p1["activity"]["frac_hi_lt_08"] >= 0.95 and p1["talk"]["frac_hi_lt_08"] >= 0.95
                     and p1["activity"]["n_lo_gt_05"] == 0 and p1["talk"]["n_lo_gt_05"] == 0 and p1["content"]["frac_hi_lt_08"] >= 0.90
                     else "failed")
    R["P1"] = p1
    # P2 levels
    med = {ch: float(okd.filter((pl.col("channel") == ch) & (pl.col("variant") == v))["g"].median()) for ch, v in prim.items()}
    R["P2"] = {"median_daily": med, "verdict": "supported" if 0.03 <= med["activity"] <= 0.20 and 0.03 <= med["talk"] <= 0.25 else "failed"}
    # P3a consistency with H19 (stalls kept), P3b stall effect
    pv = per.filter(pl.col("variant").is_in(["none", "auto", "F1", "F2", "F3", "F2tod"]))
    def pcol(ch, v, col="fe"):
        x = pv.filter((pl.col("channel") == ch) & (pl.col("variant") == v)).select("goal_no", pl.col(col).alias(f"{ch}_{v}_{col}"))
        return x
    tab = refs
    for ch in ("activity", "talk"):
        for v in ("none", "auto"):
            for col in ("fe", "se_fe", "median", "re", "se_re"):
                tab = tab.join(pcol(ch, v, col).with_columns(pl.col("goal_no").cast(pl.Int64)), on="goal_no", how="left")
    for v in ("F1", "F2", "F3", "F2tod"):
        for col in ("fe", "median", "re"):
            tab = tab.join(pcol("content", v, col).with_columns(pl.col("goal_no").cast(pl.Int64)), on="goal_no", how="left")
    reg = cal.group_by("goal_no").agg(pl.col("regime").mode().first()).with_columns(pl.col("goal_no").cast(pl.Int64))
    tab = tab.join(reg, on="goal_no", how="left")
    p3 = {}
    for ch, ref in (("activity", "h19_active"), ("talk", "h19_talk")):
        x, y = tab[f"{ch}_none_fe"].to_numpy(), tab[ref].to_numpy()
        ok = np.isfinite(x) & np.isfinite(y)
        p3[ch] = {**spearman(x, y), "median_abs_diff": float(np.median(np.abs(x[ok] - y[ok]))), "median_diff": float(np.median(x[ok] - y[ok]))}
    p3["verdict_a"] = ("supported" if p3["activity"]["rho"] >= 0.8 and p3["activity"]["median_abs_diff"] <= 0.03 and p3["talk"]["rho"] >= 0.7
                       else "failed")
    a = okd.filter(pl.col("channel") == "activity")
    w = (a.filter(pl.col("variant") == "none").select("pt_date", pl.col("g").alias("g_none"), "stall_min", "T_day")
         .join(a.filter(pl.col("variant") == "auto").select("pt_date", pl.col("g").alias("g_auto")), on="pt_date")
         .join(cal.select("pt_date", "goal_no"), on="pt_date"))
    ws = w.filter(pl.col("stall_min") > 0).with_columns((pl.col("g_auto") - pl.col("g_none")).alias("dg"),
                                                         (pl.col("stall_min") / pl.col("T_day")).alias("sf"))
    pm = ws.group_by("goal_no").agg(pl.col("dg").mean(), pl.col("sf").mean())
    p3["stall"] = {"n_days_with_stalls": ws.height, "n_days": w.height, "median_dg": float(ws["dg"].median()) if ws.height else np.nan,
                   "rho_day_sf_drop": spearman(ws["sf"], -ws["dg"]), "rho_period_sf_drop": spearman(pm["sf"], -pm["dg"])}
    p3["verdict_b"] = ("supported" if ws.height and p3["stall"]["median_dg"] < 0 and (p3["stall"]["rho_period_sf_drop"]["rho"] or 0) > 0.3 else "failed")
    R["P3"] = p3
    # P4 H03 out of sample
    talk, act, n = tab["talk_auto_fe"].to_numpy(), tab["activity_auto_fe"].to_numpy(), tab["h03_n_talk"].to_numpy()
    nx, ns = tab["h03_nx_fast"].to_numpy(), tab["h03_ns_fast"].to_numpy()
    p4 = {"a_talk_vs_n": spearman(talk, n), "b_activity_vs_n": spearman(act, n), "talk_vs_nx_fast": spearman(talk, nx)}
    ok = np.isfinite(talk) & np.isfinite(n)
    em, ec = lopo_map(talk[ok], n[ok])
    er = lopo_regime(n[ok], tab["regime"].to_numpy()[ok])
    p4["c_lopo"] = {"sse_map": float(em.sum()), "sse_const": float(ec.sum()), "sse_regime": float(np.nansum(er)), "n": int(ok.sum()),
                    "map_beats_const": bool(em.sum() < ec.sum()), "map_beats_regime": bool(em.sum() < np.nansum(er))}
    for wv in (0.6, 0.85):
        gm = 2 * wv * nx / (1 + 2 * wv * (nx + ns))
        okm = np.isfinite(gm) & np.isfinite(talk)
        p4[f"d_frac_talk_gt_map_w{wv}"] = float((talk[okm] > gm[okm]).mean()); p4["d_n"] = int(okm.sum())
        p4[f"d_median_ratio_w{wv}"] = float(np.median(talk[okm] / np.maximum(gm[okm], 1e-3)))
    p4["verdict"] = {"a": "supported" if (p4["a_talk_vs_n"]["rho"] or 0) >= 0.3 else "failed",
                     "b": "supported" if abs(p4["b_activity_vs_n"]["rho"]) < 0.3 else "failed",
                     "c": "supported" if p4["c_lopo"]["map_beats_const"] else "failed",
                     "d": "supported" if p4["d_frac_talk_gt_map_w0.6"] >= 2 / 3 else "failed"}
    R["P4"] = p4
    # P5 heterogeneity
    pa = per.filter((pl.col("channel") == "activity") & (pl.col("variant") == "auto") & (pl.col("k") >= 5))
    R["P5"] = {"n_periods": pa.height, "n_Q_sig": int((pa["p_Q"] < 0.05).sum()), "frac": float((pa["p_Q"] < 0.05).mean()) if pa.height else np.nan,
               "median_I2": float(pa["I2"].median()) if pa.height else np.nan,
               "talk_frac": float((per.filter((pl.col("channel") == "talk") & (pl.col("variant") == "auto") & (pl.col("k") >= 5))["p_Q"] < 0.05).mean()),
               "content_frac": float((per.filter((pl.col("channel") == "content") & (pl.col("variant") == "F2") & (pl.col("k") >= 5))["p_Q"] < 0.05).mean())}
    R["P5"]["verdict"] = "supported" if R["P5"]["frac"] >= 0.5 else "failed"
    # P6 content vs activity
    cm, am = tab["content_F2_median"].to_numpy(), tab["activity_auto_median"].to_numpy()
    okc = np.isfinite(cm) & np.isfinite(am)
    c2 = okd.filter((pl.col("channel") == "content") & (pl.col("variant") == "F2")).select("pt_date", pl.col("g").alias("g2"))
    c1 = okd.filter((pl.col("channel") == "content") & (pl.col("variant") == "F1")).select("pt_date", pl.col("g").alias("g1"))
    c3 = okd.filter((pl.col("channel") == "content") & (pl.col("variant") == "F3")).select("pt_date", pl.col("g").alias("g3"))
    j = c2.join(c1, on="pt_date").join(c3, on="pt_date", how="left")
    p6 = {"a_frac_content_gt_activity": float((cm[okc] > am[okc]).mean()), "a_n": int(okc.sum()),
          "b_median_content_F2": med["content"], "c_median_F2_minus_F1": float((j["g2"] - j["g1"]).median()),
          "median_F3_minus_F2": float((j["g3"] - j["g2"]).drop_nulls().median()), "median_F1": float(j["g1"].median()),
          "median_F3": float(j["g3"].drop_nulls().median())}
    p6["verdict"] = {"a": "supported" if p6["a_frac_content_gt_activity"] >= 0.7 else "failed",
                     "b_range": "supported" if 0.15 <= med["content"] <= 0.6 else "failed",
                     "b_below_074": "supported" if med["content"] < 0.74 else "failed",
                     "c": "supported" if p6["c_median_F2_minus_F1"] < 0 else "failed"}
    R["P6"] = p6
    # P7 events
    rs_a, rs_t = ev_out.get("regime_switch_activity"), ev_out.get("regime_switch_talk")
    R["P7"] = {"a": {"activity": rs_a, "talk": rs_t,
                     "verdict": "supported" if rs_a and rs_t and rs_a["lo90"] > 0 and rs_t["hi90"] < 0 else "failed"},
               "b": {ch: ev_out.get(f"goal_change_{ch}") for ch in ("activity", "talk", "content")}}
    ga, gt = ev_out.get("goal_change_activity"), ev_out.get("goal_change_talk")
    R["P7"]["b"]["verdict"] = ("supported" if ga and gt and ga["mean_abs_z_events"] <= ga["placebo_q95"] and gt["mean_abs_z_events"] <= gt["placebo_q95"]
                               else "failed")
    # round 1b: share of days above the per-day independent-agent ceiling (block-shift null q95), round-1 design (auto:
    # whole-day grid minus stalls) vs DQ8 design (trim: all-present window), and P3a against the fixed H19 reference
    ab = {}
    for ch in ("activity", "talk"):
        for v in ("none", "auto", "trim"):
            d = okd.filter((pl.col("channel") == ch) & (pl.col("variant") == v) & pl.col("null_q95").is_not_null())
            ab[f"{ch}_{v}"] = {"n_days": d.height, "frac_above_null_q95": float((d["g"] > d["null_q95"]).mean()) if d.height else None,
                               "median_g": float(d["g"].median()) if d.height else None}
    dc = okd.filter((pl.col("channel") == "content") & (pl.col("variant") == "F2") & pl.col("null_q95").is_not_null())
    ab["content_F2"] = {"n_days": dc.height, "frac_above_null_q95": float((dc["g"] > dc["null_q95"]).mean()) if dc.height else None}
    R["null_ceiling"] = ab
    if "h19f_active" in tab.columns:
        p3f = {}
        for ch, ref in (("activity", "h19f_active"), ("talk", "h19f_talk")):
            x, y = tab[f"{ch}_none_fe"].to_numpy(), tab[ref].to_numpy().astype(float)
            ok = np.isfinite(x) & np.isfinite(y)
            p3f[ch] = {**spearman(x, y), "median_abs_diff": float(np.median(np.abs(x[ok] - y[ok]))), "median_diff": float(np.median(x[ok] - y[ok]))}
            xr = tab[f"{ch}_none_re"].to_numpy()
            okr = np.isfinite(xr) & np.isfinite(y)
            p3f[ch]["re"] = {**spearman(xr, y), "median_abs_diff": float(np.median(np.abs(xr[okr] - y[okr])))}
        p3f["verdict_a"] = ("supported" if p3f["activity"]["rho"] >= 0.8 and p3f["activity"]["median_abs_diff"] <= 0.03 and p3f["talk"]["rho"] >= 0.7
                            else "failed")
        R["P3_fixed_ref"] = p3f
    R["_table"] = tab
    return R


def period_verdicts(per, refs, tab) -> pl.DataFrame:
    rows = []
    for g in sorted(per["goal_no"].unique().to_list()):
        p = per.filter(pl.col("goal_no") == g)
        def get(ch, v, col):
            x = p.filter((pl.col("channel") == ch) & (pl.col("variant") == v))
            return x[col][0] if x.height else None
        sub = [get(ch, v, "frac_hi_lt_08") for ch, v in (("activity", "auto"), ("talk", "auto"), ("content", "F2"))]
        maxlo = [get(ch, v, "max_lo") for ch, v in (("activity", "auto"), ("talk", "auto"), ("content", "F2"))]
        i_ok = all(s is None or s == 1.0 for s in sub)
        crit = any(m is not None and m > 0.8 for m in maxlo)
        r = refs.filter(pl.col("goal_no") == g)
        def cons(ch, ref):
            fe, se = get(ch, "none", "fe"), get(ch, "none", "se_fe")
            if fe is None or r.height == 0 or r[ref][0] is None:
                return None
            tol = max(0.05, 2 * float(np.sqrt((se or 0) ** 2 + (r[f"se_{ref}"][0] or 0) ** 2)))
            return abs(fe - r[ref][0]) <= tol
        fixed_ref = "h19f_active" in refs.columns  # round 1b: H19's estimator recomputed on activity_bins_fixed
        ii = ([cons("activity", "h19f_active"), cons("talk", "h19f_talk")] if fixed_ref else
              [cons("activity", "h19_active"), cons("talk", "h19_talk")])
        ii_r1ref = [cons("activity", "h19_active"), cons("talk", "h19_talk")]
        ii_ok = all(x is None or x for x in ii)
        cmed = get("content", "F2", "median")
        iii_ok = cmed is None or cmed < 0.74
        if crit or (not ii_ok and not iii_ok):
            v = "failed"
        elif i_ok and ii_ok and iii_ok:
            v = "supported"
        else:
            v = "mixed"
        rows.append({"goal_no": g, "verdict": v, "i_subcritical": i_ok, "ii_h19": ii_ok, "iii_content_lt074": iii_ok, "any_lo_gt08": crit,
                     "act": get("activity", "auto", "fe"), "act_none": get("activity", "none", "fe"), "talk": get("talk", "auto", "fe"),
                     "talk_none": get("talk", "none", "fe"), "content": get("content", "F2", "fe"), "content_med": cmed,
                     "act_med": get("activity", "auto", "median"), "talk_med": get("talk", "auto", "median"),
                     "act_I2": get("activity", "auto", "I2"), "act_pQ": get("activity", "auto", "p_Q"),
                     "k_act": get("activity", "auto", "k"), "k_content": get("content", "F2", "k"),
                     "h19_active": r["h19_active"][0] if r.height else None, "h19_talk": r["h19_talk"][0] if r.height else None,
                     "h03_n_talk": r["h03_n_talk"][0] if r.height else None,
                     "h19f_active": r["h19f_active"][0] if (r.height and fixed_ref) else None,
                     "h19f_talk": r["h19f_talk"][0] if (r.height and fixed_ref) else None,
                     "ii_vs_round1_h19": all(x is None or x for x in ii_r1ref)})
    return pl.DataFrame(rows)


def main():
    spins, st, V, ex, EV, h38, cal = load()
    days = cal["pt_date"].to_list()
    print(f"{len(days)} non-holdout days; building F3 cross-fitted directions", flush=True)
    f3, tod = f3_directions(st, V, ex, EV, cal)
    shared = {"spins": spins, "st": st, "V": V, "ex": ex, "EV": EV, "h38": h38, "cal": cal, "f3": f3, "tod": tod}
    with Pool(2, initializer=init_worker, initargs=(shared,)) as pool:
        rows = [r for rr in pool.imap(job, days, chunksize=2) for r in rr]
    daily = pl.DataFrame(rows, infer_schema_length=None).join(cal.select("pt_date", "goal_no", "regime"), on="pt_date", how="left")
    C.assert_no_holdout(daily["pt_date"], daily["goal_no"])
    C.RESD.mkdir(parents=True, exist_ok=True)
    daily.write_parquet(C.RESD / "dial_daily.parquet", compression="zstd")
    per = period_table(daily, cal)
    per.write_parquet(C.RESD / "dial_period.parquet")
    refs = pl.read_parquet(INPV / "refs.parquet")
    ev_out, ev_rows = event_tests(daily, cal, np.random.default_rng(C.SEED))
    ev_rows.write_parquet(C.RESD / "events.parquet")
    R = tests(daily, per, refs, cal, ev_out)
    tab = R.pop("_table")
    tab.write_parquet(C.RESD / "period_compare.parquet")
    pv = period_verdicts(per, refs, tab)
    pv.write_parquet(C.RESD / "period_verdicts.parquet")
    R["period_verdicts"] = pv.group_by("verdict").len().to_dicts()
    # API vs low-level agreement (sanity)
    api = daily.filter(pl.col("variant") == "api").select("pt_date", "channel", pl.col("g").alias("g_api"))
    low = daily.filter(((pl.col("variant") == "auto") & pl.col("channel").is_in(["activity", "talk"])) |
                       ((pl.col("variant") == "F2") & (pl.col("channel") == "content"))).select("pt_date", "channel", "g")
    j = api.join(low, on=["pt_date", "channel"]).drop_nulls()
    R["api_check"] = {ch: float((j.filter(pl.col("channel") == ch)["g_api"] - j.filter(pl.col("channel") == ch)["g"]).abs().max())
                      for ch in ("activity", "talk", "content")}
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "explore.json").write_text(json.dumps(R, indent=1, default=lambda x: None if x is None or (isinstance(x, float) and not np.isfinite(x)) else (float(x) if isinstance(x, (np.floating, np.integer)) else str(x))))
    for g in sorted(daily["goal_no"].unique().to_list()):
        gd = C.RESD / C.pname(g)
        gd.mkdir(parents=True, exist_ok=True)
        daily.filter(pl.col("goal_no") == g).write_parquet(gd / "dial_daily.parquet")
        (gd / "results.json").write_text(json.dumps({"period": per.filter(pl.col("goal_no") == g).to_dicts(),
                                                      "verdict": pv.filter(pl.col("goal_no") == g).to_dicts()}, indent=1, default=str))
    C.write_provenance("explore" if C.DATA_VERSION == "r1" else "explore_r1b", "hypotheses/H25-criticality-dial/analysis/explore.py", ["(H25 inputs)"],
                       {"n_boot": N_BOOT, "n_null": N_NULL, "min_active_min": MIN_ACT, "min_talk_min": MIN_TALK, "block_min": 30,
                        "seg_min": 10, "content_window_min": 30, "n_exo_dirs": 5, "f3_dirs": 3, "seed": C.SEED},
                       extra_inputs=[{"source": str(INPV.relative_to(C.ROOT)), "tables": ["spins", "refs", "h38_masks"]},
                                     {"source": str(INP.relative_to(C.ROOT)), "tables": ["statements", "exo"]}],
                       out=C.RESD)
    print(json.dumps({k: R[k].get("verdict") if isinstance(R[k], dict) else R[k] for k in R if k.startswith("P")}, indent=1, default=str))
    print(json.dumps(R, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
