"""H18 per-period analysis (exploratory, non-holdout only).

  uv run python hypotheses/H18-attention-dilution/analysis/fit_periods.py --period G38 [--boot 200]
  uv run python hypotheses/H18-attention-dilution/analysis/fit_periods.py --all

Reads data/processed/H18-attention-dilution/G<NN>/{talks,pending,invisible,wakes,wake_pending}.parquet and writes
G<NN>/fits.json, G<NN>/curves.parquet. Every observable in the card is computed here, within the period:
D1 model ladder (full-data fits, within-day-block CV, day-blocked CV), M_pow beta and the bypass variant with a day
bootstrap, S elasticity, binned curves, D2 (timer wakes, 60 s window; 300 s and stint variants), invisible-message
placebo, content-reply excess, room-size contrast (two-room periods), segments at step changes.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse
import json
import math
import re
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from h18lib import K_BINS, K_LABELS, Units, cv, fit, kbin, paired_day_boot, s_elasticity  # noqa: E402
from periods import PERIODS, TWO_ROOM, gname  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H18-attention-dilution"
PRIMARY = ["const", "inv", "sat", "rec"]
SECONDARY = ["pow", "recbud"]
D2_WINDOW = 300.0   # amended 2026-10-03 after synthetic B, before any real-data fit (card, A1)
MIN_UNITS = 300
MIN_D2 = 200


def load(gp: str, base: Path | None = None):
    d = (base or DATA) / gp
    out = {}
    for k in ("talks", "pending", "invisible", "wakes", "wake_pending"):
        f = d / f"{k}.parquet"
        out[k] = pl.read_parquet(f) if f.exists() else None
    return out


def d2_units(wakes, wp, window_s=D2_WINDOW):
    if window_s is not None:
        ok = wakes.filter(pl.col("talked") & (pl.col("delay_s") <= window_s)).select("wake_id")
        wp = wp.with_columns((pl.col("resp") & pl.col("wake_id").is_in(ok["wake_id"].implode())).alias("resp"))
    return Units(wakes, wp, "wake_id")


def strip(fr):
    return {k: v for k, v in fr.items() if k not in ("u", "u_full")}


def ladder(U: Units, boot_B: int, rng, label: str, do_cv=True, bypass=True):
    res = {"n_units": U.n, "n_days": int(len(np.unique(U.day))), "rate": float(U.r.mean()),
           "n_resp": int(U.r.sum()), "n_mention_units": U.n_mention_units}
    fits = {m: fit(m, U) for m in PRIMARY + SECONDARY + (["bypass"] if bypass and U.n_mention_units >= 30 else [])}
    res["fits"] = {m: strip(f) for m, f in fits.items()}
    res["aic_best_primary"] = min(PRIMARY, key=lambda m: fits[m]["aic"])
    if do_cv:
        for scheme in ("block", "day"):
            if scheme == "day" and len(U.days) < 3:
                continue
            t0 = time.time()
            ll = cv(PRIMARY + SECONDARY, U, scheme)
            mean = {m: float(np.nanmean(v)) for m, v in ll.items()}
            best = max(PRIMARY, key=lambda m: mean[m])
            comp = {}
            # effective winner (card amendment A2): M_sat with k0 >= k_q90 is const-like, k0 < 3 budget-like
            k0 = math.exp(fits["sat"]["params"]["logk0"])
            kq90 = float(np.quantile(U.k, 0.9))
            rho = 1 / (1 + math.exp(-fits["rec"]["params"]["lrho"]))
            eff = best
            if best == "sat":
                eff = "sat~const" if k0 >= kq90 else ("sat~inv" if k0 < 3 else "sat")
            elif best == "rec" and rho ** max(1.0, kq90 - 1) >= 0.5:
                eff = "rec~const"   # rho -> 1: recency weights flat over the data range
            for m in PRIMARY + SECONDARY:
                if m != "const":
                    comp[f"{m}_vs_const"] = paired_day_boot(ll[m], ll["const"], U.day)
            rivals = [m for m in PRIMARY if m != best]
            second = max(rivals, key=lambda m: mean[m])
            comp["best_vs_second"] = paired_day_boot(ll[best], ll[second], U.day)
            comp["inv_vs_rec"] = paired_day_boot(ll["inv"], ll["rec"], U.day)
            comp["recbud_vs_rec"] = paired_day_boot(ll["recbud"], ll["rec"], U.day)
            res[f"cv_{scheme}"] = dict(mean=mean, best=best, effective=eff, k0=k0, rho=rho, kq90=kq90, second=second, comp=comp,
                                       n_eval=int(np.sum(~np.isnan(ll["const"]))), secs=round(time.time() - t0, 1))
    # bootstrap
    bs = {"beta": [], "gamma": [], "beta_byp": [], "betaM_byp": []}
    start_pow = [fits["pow"]["params"]["g"], fits["pow"]["params"]["beta"]]
    for b in range(boot_B):
        Ub = U.resample_days(rng)
        if Ub.r.sum() < 5:
            continue
        fp = fit("pow", Ub, start=start_pow)
        bs["beta"].append(fp["params"]["beta"])
        bs["gamma"].append(fp["params"]["g"])
        if "bypass" in fits and b < max(30, boot_B // 2):
            fb = fit("bypass", Ub, start=[fits["bypass"]["params"][k] for k in ("g", "beta", "betaM")])
            bs["beta_byp"].append(fb["params"]["beta"])
            bs["betaM_byp"].append(fb["params"]["betaM"])
    res["boot"] = {k: (summ(v) if v else None) for k, v in bs.items()}
    res["boot_B"] = boot_B
    res["beta"] = fits["pow"]["params"]["beta"]
    res["gamma"] = fits["pow"]["params"]["g"]
    return res, fits


def summ(v):
    v = np.asarray(v, float)
    return dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else None, lo=float(np.quantile(v, 0.025)),
                hi=float(np.quantile(v, 0.975)), n=int(len(v)))


def talk_level(U: Units, talks: pl.DataFrame):
    """S per talk (number of scored pending senders addressed), with k and agent x day cluster."""
    u = U.df.select("talk_id", "r", "k", "agent", "pt_date").group_by("talk_id").agg(
        pl.col("r").sum().alias("S"), pl.len().alias("ks"), pl.col("k").first(), pl.col("agent").first(),
        pl.col("pt_date").first())
    return u


def eps_S(tl: pl.DataFrame, rng, B: int):
    S = tl["S"].cast(pl.Float64).to_numpy()
    k = tl["k"].cast(pl.Float64).to_numpy()
    key = tl["agent"].cast(pl.Int64).to_numpy() * 10000 + np.unique(tl["pt_date"].to_numpy(), return_inverse=True)[1]
    _, c = np.unique(key, return_inverse=True)
    e = s_elasticity(S, k, c)
    days = tl["pt_date"].to_numpy()
    ud = np.unique(days)
    byd = [np.where(days == d)[0] for d in ud]
    bs = []
    for _ in range(B):
        draw = rng.integers(len(ud), size=len(ud))
        idx = np.concatenate([byd[i] for i in draw])
        rep = np.concatenate([np.full(len(byd[i]), j) for j, i in enumerate(draw)])
        kk = tl["agent"].cast(pl.Int64).to_numpy()[idx] * 10000 + rep
        _, cc = np.unique(kk, return_inverse=True)
        bs.append(s_elasticity(S[idx], k[idx], cc))
    return dict(eps=e, boot=summ(bs) if bs else None)


def curves(U: Units, fits, tl: pl.DataFrame, rng, B=200):
    """Binned P(r|k) for n_j = 1 units, O/E under M_const (agent x day), S per k bin; day-bootstrap CIs."""
    kb = kbin(U.k)
    one = U.nj == 1
    # expected under M_const fit
    th = [fits["const"]["params"]["g"]]
    from h18lib import shape
    Sx = np.maximum(shape("const", th, U), 1e-300)
    pexp = -np.expm1(-np.exp(fits["const"]["u"][U.c]) * Sx)
    rows = []
    days = U.day
    nd = int(days.max()) + 1
    tk = kbin(tl["k"].to_numpy())
    tS = tl["S"].cast(pl.Float64).to_numpy()
    tdays = np.unique(tl["pt_date"].to_numpy(), return_inverse=True)[1]
    for b, lab in enumerate(K_LABELS):
        m1 = (kb == b) & one
        ma = kb == b
        mt = tk == b
        if ma.sum() == 0:
            continue
        rate = U.r[m1].mean() if m1.sum() else np.nan
        oe = U.r[ma].sum() / max(1e-9, pexp[ma].sum())
        Sm = tS[mt].mean() if mt.sum() else np.nan
        bs_rate, bs_oe, bs_S = [], [], []
        for _ in range(B):
            draw = rng.integers(nd, size=nd)
            w = np.bincount(draw, minlength=nd)[days]
            wt = np.bincount(draw, minlength=nd)[tdays]
            if (w * m1).sum() > 0:
                bs_rate.append((U.r * w * m1).sum() / (w * m1).sum())
            if (w * ma).sum() > 0:
                bs_oe.append((U.r * w * ma).sum() / max(1e-9, (pexp * w * ma).sum()))
            if (wt * mt).sum() > 0:
                bs_S.append((tS * wt * mt).sum() / (wt * mt).sum())
        q = lambda v: (float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))) if len(v) > 5 else (None, None)
        rows.append(dict(kbin=lab, k_lo=K_BINS[b][0], n1=int(m1.sum()), n=int(ma.sum()), n_talks=int(mt.sum()),
                         rate1=float(rate), rate1_lo=q(bs_rate)[0], rate1_hi=q(bs_rate)[1],
                         oe=float(oe), oe_lo=q(bs_oe)[0], oe_hi=q(bs_oe)[1],
                         S=float(Sm), S_lo=q(bs_S)[0], S_hi=q(bs_S)[1],
                         kmean=float(U.k[ma].mean())))
    return rows


def placebo(talks, inv, U: Units):
    pend_rate = float(U.r.mean())
    inv_rate = float(inv["resp"].cast(pl.Float64).mean()) if inv is not None and inv.height else float("nan")
    t = talks
    nonp = float(t["n_ment_nonpend"].sum() / max(1, t["n_cand_nonpend"].sum()))
    # pending rate at the same talks that have invisible senders
    if inv is not None and inv.height:
        ids = inv["talk_id"].unique()
        same = U.df.filter(pl.col("talk_id").is_in(ids.implode()))
        pend_same = float(same["r"].cast(pl.Float64).mean()) if same.height else float("nan")
    else:
        pend_same = float("nan")
    return dict(pending=pend_rate, invisible=inv_rate, n_invisible=int(inv.height) if inv is not None else 0,
                nonpending=nonp, pending_same_talks=pend_same)


def content(pend: pl.DataFrame, talks: pl.DataFrame):
    if "cos" not in pend.columns:
        return None
    p = pend.filter(pl.col("cos").is_not_null() & pl.col("cos_null").is_not_null()).join(
        talks.select("talk_id", "k"), on="talk_id")
    if p.height < 200:
        return None
    thr = float(np.quantile(p["cos_null"].to_numpy(), 0.95))
    p = p.with_columns((pl.col("cos") > thr).alias("hit"), (pl.col("cos_null") > thr).alias("hit0"))
    kb = kbin(p["k"].to_numpy())
    hit, hit0 = p["hit"].to_numpy(), p["hit0"].to_numpy()
    rows = []
    for b, lab in enumerate(K_LABELS):
        m = kb == b
        if m.sum() < 30:
            continue
        rows.append(dict(kbin=lab, kmean=float(p["k"].to_numpy()[m].mean()), n=int(m.sum()),
                         rate=float(hit[m].mean()), rate0=float(hit0[m].mean()),
                         excess=float(hit[m].mean() - hit0[m].mean())))
    ok = [r for r in rows if r["excess"] > 0]
    slope = None
    if len(ok) >= 3:
        x = np.log([r["kmean"] for r in ok])
        y = np.log([r["excess"] for r in ok])
        w = np.array([r["n"] for r in ok], float)
        X = np.vstack([np.ones_like(x), x]).T
        W = np.diag(w)
        coef = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
        slope = float(coef[1])
    return dict(threshold=thr, overall_excess=float(hit.mean() - hit0.mean()), bins=rows, slope=slope)


def room_contrast(U: Units, talks: pl.DataFrame, rng, B=200):
    """Two-room days: clusters = day x room; room effect = mean over days of (u_small - u_large), under M_const and
    M_pow. Also raw per-day ratios of k-bar, p-bar and S."""
    t = talks.select("talk_id", "room", "n_room", "pt_date")
    df = U.df.join(t, on="talk_id")
    rooms = df.group_by("pt_date", "room").agg(pl.col("n_room").median().alias("nr"), pl.len().alias("n"),
                                                pl.col("r").cast(pl.Float64).mean().alias("p"))
    # days with exactly two rooms with data
    good = rooms.filter(pl.col("n") >= 20).group_by("pt_date").agg(pl.len().alias("nrooms")).filter(pl.col("nrooms") == 2)
    if good.height == 0:
        return None
    rooms = rooms.join(good, on="pt_date").sort("pt_date", "nr")
    small = rooms.group_by("pt_date", maintain_order=True).first().select("pt_date", pl.col("room").alias("small_room"))
    df = df.join(small, on="pt_date").with_columns((pl.col("room") == pl.col("small_room")).alias("small"))
    keep = df["pt_date"].is_in(good["pt_date"].implode()).to_numpy() if False else np.isin(U.df["talk_id"].to_numpy(), df["talk_id"].to_numpy())
    Us = U.subset(keep)
    dsub = df.sort("uid")
    small_flag = dsub["small"].to_numpy()
    dayc = np.unique(dsub["pt_date"].to_numpy(), return_inverse=True)[1]
    key = dayc * 2 + small_flag.astype(int)
    ukeys, Us.c = np.unique(key, return_inverse=True)

    def eff(model):
        f = fit(model, Us)
        u = f["u"]
        dd = {}
        for kk, uu in zip(ukeys, u):
            dd.setdefault(kk // 2, {})[kk % 2] = uu
        diffs = [v[1] - v[0] for v in dd.values() if 0 in v and 1 in v]
        return float(np.mean(diffs)) if diffs else float("nan"), f

    e_const, fc = eff("const")
    e_pow, fp = eff("pow")
    # raw per-day ratios
    tl = talks.join(small, on="pt_date").with_columns((pl.col("room") == pl.col("small_room")).alias("small"))
    tl = tl.filter(pl.col("k") >= 1)
    kb = tl.group_by("pt_date", "small").agg(pl.col("k").mean().alias("kbar"), pl.col("n_room").mean().alias("nroom"))
    pb = dsub.group_by("pt_date", "small").agg(pl.col("r").cast(pl.Float64).mean().alias("pbar"), pl.len().alias("n"))
    Sb = dsub.group_by("talk_id", "pt_date", "small").agg(pl.col("r").sum().alias("S")).group_by("pt_date", "small").agg(
        pl.col("S").cast(pl.Float64).mean().alias("Sbar"))
    perday = kb.join(pb, on=["pt_date", "small"]).join(Sb, on=["pt_date", "small"]).sort("pt_date", "small")
    rows = []
    for d, sub in perday.group_by("pt_date", maintain_order=True):
        if sub.height != 2:
            continue
        s1 = sub.filter(pl.col("small")).row(0, named=True)
        s0 = sub.filter(~pl.col("small")).row(0, named=True)
        rows.append(dict(day=d[0], k_ratio=s0["kbar"] / max(1e-9, s1["kbar"]), p_ratio=s1["pbar"] / max(1e-9, s0["pbar"]),
                         S_ratio=s1["Sbar"] / max(1e-9, s0["Sbar"]), n_small=s1["nroom"], n_large=s0["nroom"],
                         units_small=s1["n"], units_large=s0["n"]))
    # bootstrap over days for the room effects
    bs_c, bs_p = [], []
    days = np.unique(dayc)
    for _ in range(B if Us.n < 50000 else 50):
        draw = rng.choice(days, size=len(days))
        idx = np.concatenate([np.where(dayc == d)[0] for d in draw])
        rep = np.concatenate([np.full((dayc == d).sum(), j) for j, d in enumerate(draw)])
        Ub = Us.subset(np.ones(Us.n, bool))
        Ub = Ub.subset(np.isin(np.arange(Us.n), idx)) if False else None
        # direct construction
        sub = object.__new__(Units)
        for a in ("r", "k", "n0", "nM", "nj", "block", "agent", "ac"):
            setattr(sub, a, getattr(Us, a)[idx])
        kk2 = rep * 2 + small_flag[idx].astype(int)
        uk2, sub.c = np.unique(kk2, return_inverse=True)
        sub.day, sub.days, sub.ckeys, sub.ac_keys = rep, np.arange(len(draw)), uk2, Us.ac_keys
        sub.m_uid = sub.m_rank = sub.m_ment = np.zeros(0)
        sub.n, sub.n_mention_units, sub.df = len(idx), int((sub.nM > 0).sum()), None
        for model, store in (("const", bs_c), ("pow", bs_p)):
            f = fit(model, sub)
            dd = {}
            for kk, uu in zip(uk2, f["u"]):
                dd.setdefault(kk // 2, {})[kk % 2] = uu
            diffs = [v[1] - v[0] for v in dd.values() if 0 in v and 1 in v]
            if diffs:
                store.append(np.mean(diffs))
    med = lambda key: float(np.median([r[key] for r in rows])) if rows else None
    return dict(n_days=len(rows), effect_const=e_const, effect_const_ci=summ(bs_c) if bs_c else None,
                effect_pow=e_pow, effect_pow_ci=summ(bs_p) if bs_p else None, beta_roomfe=fp["params"]["beta"],
                median_k_ratio=med("k_ratio"), median_p_ratio=med("p_ratio"), median_S_ratio=med("S_ratio"),
                per_day=rows)


# ------------------------------------------------------------------------------------------- segments
def step_changes() -> list[str]:
    """Same rule as H03's segments.py (proposed for infra/): NE dates, roster joins/leaves, goal-periods scaffold dates."""
    dates = set()
    txt = (ROOT / "hypotheses/natural-experiments.md").read_text()
    for line in txt.splitlines():
        m = re.match(r"^\| (NE\d+) \| ([^|]+) \| ([^|]+) \|", line)
        if not m:
            continue
        full = re.findall(r"(\d{4})-(\d{2})-(\d{2})", m.group(2))
        if not full:
            continue
        y = full[0][0]
        dates |= {f"{a}-{b}-{c}" for a, b, c in full}
        rest = re.sub(r"\d{4}-\d{2}-\d{2}", "", m.group(2))
        for mm, dd in re.findall(r"(\d{2})-(\d{2})", rest):
            dates.add(f"{y}-{mm}-{dd}")
        for dd in re.findall(r"/(\d{2})(?!-)", rest):
            dates.add(f"{y}-{full[0][1]}-{dd}")
    ros = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet")
    for r in ros.iter_rows(named=True):
        for k in ("joined", "left"):
            if r[k]:
                dates.add(r[k])
    gp = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    for line in gp.splitlines():
        if line.startswith("- **Scaffold changes inside:**"):
            dates |= set(re.findall(r"\((\d{4}-\d{2}-\d{2})\)", line))
    return sorted(dates)


def segments_of(days: list[str], changes: list[str]) -> list[list[str]]:
    segs, cur, prev = [], [], None
    for d in sorted(days):
        if cur and any(prev < c <= d for c in changes):
            segs.append(cur)
            cur = []
        cur.append(d)
        prev = d
    if cur:
        segs.append(cur)
    return segs


def dl_pool(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) < 2:
        return None
    w = 1 / se ** 2
    mfe = (w * est).sum() / w.sum()
    Q = (w * (est - mfe) ** 2).sum()
    df = len(est) - 1
    tau2 = max(0.0, (Q - df) / (w.sum() - (w ** 2).sum() / w.sum()))
    wr = 1 / (se ** 2 + tau2)
    m = (wr * est).sum() / wr.sum()
    I2 = max(0.0, (Q - df) / Q) if Q > 0 else 0.0
    return dict(mean=float(m), se=float(math.sqrt(1 / wr.sum())), tau2=float(tau2), I2=float(I2), Q=float(Q), k=len(est))


def segment_fits(U: Units, talks: pl.DataFrame, rng, B=50):
    changes = step_changes()
    days = sorted(set(talks["pt_date"].to_list()))
    segs = segments_of(days, changes)
    if len(segs) < 2:
        return None
    out = []
    tl = talks.filter(pl.col("k") >= 1)
    for s in segs:
        m = np.isin(U.days[U.day], s)
        if m.sum() < 100 or U.r[m].sum() < 5:
            out.append(dict(days=s, n_units=int(m.sum()), beta=None))
            continue
        Us = U.subset(m)
        fp = fit("pow", Us)
        bs = []
        if len(s) >= 2:
            for _ in range(B):
                Ub = Us.resample_days(rng)
                if Ub.r.sum() >= 3:
                    bs.append(fit("pow", Ub, start=[fp["params"]["g"], fp["params"]["beta"]])["params"]["beta"])
        tls = tl.filter(pl.col("pt_date").is_in(s))
        u = Us.df if Us.df is not None else None
        S_mean = None
        out.append(dict(days=s, start=s[0], end=s[-1], n_days=len(s), n_units=int(Us.n), rate=float(Us.r.mean()),
                        beta=fp["params"]["beta"], beta_se=float(np.std(bs, ddof=1)) if len(bs) > 5 else None,
                        beta_ci=summ(bs) if len(bs) > 5 else None, n_room=float(tls["n_room"].mean()),
                        kbar=float(tls["k"].mean())))
    pooled = dl_pool([o["beta"] for o in out if o.get("beta_se")], [o["beta_se"] for o in out if o.get("beta_se")])
    return dict(segments=out, pooled=pooled)


def segment_S(U: Units, talks, segs_res):
    """Per-segment p-bar, B-hat (mean S per talk with >= 1 scored sender), N (for #51 / P9)."""
    if segs_res is None:
        return None
    tl = talk_level(U, talks)
    nr = talks.select("talk_id", "n_room")
    tl = tl.join(nr, on="talk_id")
    out = []
    for s in segs_res["segments"]:
        sub = tl.filter(pl.col("pt_date").is_in(s["days"]))
        uu = U.df.filter(pl.col("pt_date").is_in(s["days"]))
        if sub.height == 0:
            continue
        out.append(dict(start=s["days"][0], end=s["days"][-1], n_talks=sub.height, B_hat=float(sub["S"].mean()),
                        p_bar=float(uu["r"].cast(pl.Float64).mean()), n_room=float(sub["n_room"].mean()),
                        kbar=float(sub["k"].mean())))
    return out


# ------------------------------------------------------------------------------------------- main
def select_response(D: dict, resp: str) -> dict:
    """Round-1b switch: score the units with another response column of the ledger scheme (resp_reply, resp_auth,
    p_reply). Round-1 files have only `resp` (mention), which stays the default."""
    if resp == "resp":
        return D
    D = dict(D)
    D["pending"] = D["pending"].with_columns(pl.col(resp).cast(pl.Boolean) if resp != "p_reply" else (pl.col(resp) >= 0.5),
                                             ).with_columns(pl.col(resp if resp != "p_reply" else "p_reply").alias("resp")
                                                            if resp != "p_reply" else (pl.col("p_reply") >= 0.5).alias("resp"))
    if D.get("wake_pending") is not None and "resp_reply" in D["wake_pending"].columns:
        D["wake_pending"] = D["wake_pending"].with_columns(pl.col("resp_reply").alias("resp"), pl.col("resp_reply5").alias("resp5"))
    return D


def run(gp: str, boot_B: int, seed: int = 18, base: Path | None = None, two_room: bool | None = None,
        resp: str = "resp", tag: str | None = None):
    t0 = time.time()
    rng = np.random.default_rng(seed)
    g = int(gp[1:]) if gp[1:].isdigit() else None
    D = select_response(load(gp, base), resp)
    talks, pend = D["talks"], D["pending"]
    out = {"period": gp, "meta": PERIODS.get(g), "d2_window_s": D2_WINDOW, "response": resp}
    U = Units(talks, pend, "talk_id")
    out["n_talks"] = talks.height
    out["n_talks_k1"] = talks.filter(pl.col("k") >= 1).height
    out["k_median"] = float(talks.filter(pl.col("k") >= 1)["k"].median())
    out["k_mean"] = float(talks.filter(pl.col("k") >= 1)["k"].mean())
    out["k_q90"] = float(talks.filter(pl.col("k") >= 1)["k"].quantile(0.9))
    out["n_room_mean"] = float(talks["n_room"].mean())
    out["n_agents"] = int(talks["agent"].n_unique())
    out["n_days"] = int(talks["pt_date"].n_unique())
    out["after_pause_share"] = float(talks["after_pause"].mean())
    print(f"{gp}: {U.n} D1 units, rate {U.r.mean():.3f}", flush=True)
    if U.n < MIN_UNITS:
        out["descriptive_only"] = True
    d1, fits = ladder(U, boot_B, rng, "D1")
    out["D1"] = d1
    print(f"  D1 ladder done {time.time() - t0:.0f}s beta={d1['beta']:.2f} best={d1.get('cv_block', {}).get('best')}", flush=True)
    tl = talk_level(U, talks)
    out["B_hat"] = float(tl["S"].mean())
    out["p_bar"] = float(U.r.mean())
    out["eps_S"] = eps_S(tl, rng, min(boot_B, 100))
    out["curves"] = curves(U, fits, tl, rng)
    out["placebo"] = placebo(talks, D["invisible"], U)
    out["content"] = content(pend, talks)
    # D2
    wk, wp = D["wakes"], D["wake_pending"]
    if wk is not None and wp is not None and wp.filter(pl.col("scored")).height >= 50:
        out["D2_struct"] = dict(n_wakes=wk.height, talked=float(wk["talked"].mean()),
                                talk60=float((wk["talked"] & (wk["delay_s"] <= 60)).mean()),
                                talk300=float((wk["talked"] & (wk["delay_s"] <= 300)).mean()),
                                k_median=float(wk.filter(pl.col("k") >= 1)["k"].median()) if wk.filter(pl.col("k") >= 1).height else None,
                                k_mean=float(wk.filter(pl.col("k") >= 1)["k"].mean()) if wk.filter(pl.col("k") >= 1).height else None)
        U2 = d2_units(wk, wp, D2_WINDOW)
        out["D2"] = {"n_units": U2.n, "n_resp": int(U2.r.sum())}
        if U2.n >= MIN_D2 and U2.r.sum() >= 10:
            d2, _ = ladder(U2, boot_B, rng, "D2", do_cv=U2.r.sum() >= 30, bypass=False)
            out["D2"] = d2
        for lab, W in (("D2w60", 60.0), ("D2stint", None)):
            Uv = d2_units(wk, wp, W)
            if Uv.n >= MIN_D2 and Uv.r.sum() >= 10:
                fv = fit("pow", Uv)
                bs = []
                for _ in range(min(100, boot_B)):
                    Ub = Uv.resample_days(rng)
                    if Ub.r.sum() >= 3:
                        bs.append(fit("pow", Ub, start=[fv["params"]["g"], fv["params"]["beta"]])["params"]["beta"])
                out[lab] = dict(n_units=Uv.n, n_resp=int(Uv.r.sum()), beta=fv["params"]["beta"],
                                boot=summ(bs) if len(bs) > 5 else None)
        print(f"  D2 done {time.time() - t0:.0f}s", flush=True)
    if (g in TWO_ROOM) if two_room is None else two_room:
        out["rooms"] = room_contrast(U, talks, rng, B=min(boot_B, 100))
    segs = segment_fits(U, talks, rng, B=min(50, boot_B) if U.n < 200000 else 20)
    out["segments"] = segs
    out["segment_S"] = segment_S(U, talks, segs)
    out["secs"] = round(time.time() - t0, 1)
    ((base or DATA) / gp / (f"fits_{tag}.json" if tag else "fits.json")).write_text(json.dumps(out, indent=1, default=float))
    print(f"{gp} done in {out['secs']}s", flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--period")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--skip", default="")
    ap.add_argument("--dir", default=None, help="run on a folder of scheme outputs (e.g. synthetic stand-ins)")
    ap.add_argument("--two-room", action="store_true")
    ap.add_argument("--resp", default="resp", help="round 1b: resp (mention), resp_reply, resp_auth or p_reply")
    ap.add_argument("--tag", default=None, help="round 1b: write fits_<tag>.json instead of fits.json")
    ap.add_argument("--only", default=None, help="comma-separated periods for --dir --all")
    a = ap.parse_args()
    if a.dir and not a.all:
        base = Path(a.dir)
        run(a.period, a.boot, base=base, two_room=a.two_room, resp=a.resp, tag=a.tag)
        raise SystemExit
    if a.dir and a.all:   # round 1b: every period folder under --dir
        base = Path(a.dir)
        gps = sorted(p.name for p in base.iterdir() if p.is_dir() and (p / "pending.parquet").exists())
        if a.only:
            gps = [x for x in gps if x in set(a.only.split(","))]
        skip = set(a.skip.split(",")) if a.skip else set()
        for gp in gps:
            if gp in skip:
                continue
            run(gp, a.boot if gp != "G51" else min(a.boot, 40), base=base, resp=a.resp, tag=a.tag)
        raise SystemExit
    gps = [gname(g) for g in PERIODS] if a.all else [a.period]
    skip = set(a.skip.split(",")) if a.skip else set()
    for gp in gps:
        if gp in skip:
            continue
        run(gp, a.boot if gp != "G51" else min(a.boot, 60))
