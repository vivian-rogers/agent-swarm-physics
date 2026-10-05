"""H13 round 2, R2-B: enculturation of newcomers (card: Round 2, R2-B; rules fixed in the pre-registration).

Joiner j: roster join day is a non-reserved day with >= 5 chat statements. Window = the join goal period's non-reserved
calendar days in [join, join + 9], one regime. Incumbents: agents with statements in the window who joined before the
join day. Day mean m_d: incumbents' agent-day means (>= 3 statements; >= 3 incumbents). Lab field h_g: mean over g's
incumbents of their day-demeaned agent means (>= 2 eligible days). Candidate labs: labs with such an incumbent.
Day index d: window days with >= 5 joiner statements and a day mean, d <= 6.
Statistics use 5-statement means (20 draws):
  a(d) = cos(v_jd - m_d, h_own) - mean_{g != own} cos(v_jd - m_d, h_g)
  r(d) = cos(v_jd, m^room_d) - mean_i cos(v_id, m^room_{d,-i})   (incumbents in the joiner's modal room, >= 3)
Usage: uv run python hypotheses/H13-family-fields/analysis/r2_encult.py [--synthetic] [--reps 200]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402
from common import holdout_mask  # noqa: E402

NS, NDRAW, DMAX, WIN = 5, 20, 6, 10


def load_all():
    st = pl.read_parquet(R.ED / "statements.parquet").with_row_index("srow").filter(pl.col("kind") == "chat")
    hm = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()), bool)
    st = st.filter(pl.Series(~hm) & ~pl.col("holdout"))
    ro = pl.read_parquet(R.SH / "roster.parquet", columns=["agent", "lab", "joined", "name"])
    cal = pl.read_parquet(R.SH / "calendar.parquet", columns=["pt_date", "goal_no", "regime", "holdout"])
    chm = np.array(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()), bool)
    cal = cal.with_columns(pl.Series("reserved", chm | cal["holdout"].to_numpy()))
    return st, ro, cal


def build(model="bge", kind="white32"):
    """Joiner records with all indices needed for the statistics (incumbent vectors fixed; joiner statements listed)."""
    st, ro, cal = load_all()
    A = np.load(R.ED / {"white32": f"statements_white32_{R.MODELS[model]}.npy",
                        "srp": f"statements_style_resid_period32_{R.MODELS[model]}.npy"}[kind], mmap_mode="r")
    lab_of = dict(zip(ro["agent"].to_list(), ro["lab"].to_list()))
    joined = dict(zip(ro["agent"].to_list(), ro["joined"].to_list()))
    out = []
    for a, J in joined.items():
        s1 = st.filter((pl.col("agent") == a) & (pl.col("pt_date") == J))
        if s1.height < NS:
            continue
        g, reg = int(s1["goal_no"][0]), s1["regime"][0]
        days = (cal.filter((pl.col("goal_no") == g) & (pl.col("pt_date") >= J) & (pl.col("regime") == reg))
                .sort("pt_date"))
        import datetime as dt
        jd = dt.date.fromisoformat(J)
        days = [d for d, rsv in zip(days["pt_date"].to_list(), days["reserved"].to_list())
                if not rsv and (dt.date.fromisoformat(d) - jd).days < WIN]
        if J not in days:
            continue
        w = st.filter(pl.col("pt_date").is_in(days))
        inc = [b for b in w["agent"].unique().to_list() if joined.get(b, "9999") < J]
        # incumbent agent-day means and day means
        V, ad = {}, {}
        for (b, d), grp in w.filter(pl.col("agent").is_in(inc)).group_by(["agent", "pt_date"]):
            if grp.height >= 3:
                Z = R.unitv(np.asarray(A[grp["srow"].to_numpy()]))
                V[(b, d)] = Z.mean(0)
                ad[(b, d)] = (Z, grp["room"].mode()[0])
        mday = {}
        for d in days:
            vs = [V[(b, d)] for b in inc if (b, d) in V]
            if len(vs) >= 3:
                mday[d] = np.mean(vs, 0)
        Hinc = {}
        for b in inc:
            ds = [V[(b, d)] - mday[d] for d in days if (b, d) in V and d in mday]
            if len(ds) >= 2:
                Hinc[b] = np.mean(ds, 0)
        cands = sorted({lab_of[b] for b in Hinc})
        own = lab_of[a]
        if own not in cands or len(cands) < 2:
            continue
        hf = {lab: np.mean([Hinc[b] for b in Hinc if lab_of[b] == lab], 0) for lab in cands}
        nlab = {lab: sum(lab_of[b] == lab for b in Hinc) for lab in cands}
        # joiner days
        jdays = []
        for d in days:
            sj = w.filter((pl.col("agent") == a) & (pl.col("pt_date") == d))
            if sj.height >= NS and d in mday:
                jdays.append((d, sj["srow"].to_numpy(), sj["room"].mode()[0]))
            if len(jdays) == DMAX:
                break
        if not jdays or jdays[0][0] != J:
            continue
        recs = []
        for d, srows, room in jdays:
            inc_room = [b for b in inc if (b, d) in ad and ad[(b, d)][1] == room]
            recs.append(dict(day=d, Z=R.unitv(np.asarray(A[srows])), room=room, m=mday[d],
                             room_inc=[(b, ad[(b, d)][0]) for b in inc_room],
                             inc_lab=[(b, lab_of[b], ad[(b, d)][0]) for b in inc if (b, d) in ad and b in Hinc]))
        out.append(dict(agent=a, lab=own, joined=J, goal_no=g, regime=reg, cands=cands, hf=hf, nlab=nlab,
                        Hinc=Hinc, inc_lab_of={b: lab_of[b] for b in Hinc}, days=recs))
    return out


def cosv(x, y):
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-12))


def draw_mean(Z, rng, ns=NS):
    return Z[rng.choice(len(Z), ns, replace=False)].mean(0) if len(Z) >= ns else None


def joiner_stats(J, rng, ndraw=NDRAW, Zover=None, excl=None):
    """Per day: mean cos to each candidate lab field (dict), a(d), r(d) and incumbents' leave-self-out a(d).
    Zover: optional list of replacement joiner statement arrays per day (synthetic)."""
    res = []
    for k, rec in enumerate(J["days"]):
        Z = rec["Z"] if Zover is None else Zover[k]
        if Z is None or len(Z) < NS:
            res.append(dict(day=rec["day"], c={g: np.nan for g in J["cands"]}, a=np.nan, r=np.nan, a_inc=np.nan))
            continue
        room_inc = [(b, z) for b, z in rec["room_inc"] if b != excl]
        c = {g: 0.0 for g in J["cands"]}
        rr, nr = 0.0, 0
        for _ in range(ndraw):
            v = draw_mean(Z, rng)
            dlt = v - rec["m"]
            for g in J["cands"]:
                c[g] += cosv(dlt, J["hf"][g]) / ndraw
            if len(room_inc) >= 3:
                Ms = np.array([z.mean(0) for _, z in room_inc])
                mr = Ms.mean(0)
                inc_c = []
                for q, (b, z) in enumerate(room_inc):
                    vi = draw_mean(z, rng)
                    if vi is None:
                        continue
                    mo = np.delete(Ms, q, 0).mean(0)
                    inc_c.append(cosv(vi, mo))
                if inc_c:
                    rr += cosv(v, mr) - np.mean(inc_c)
                    nr += 1
        own = J["lab"]
        a = c[own] - np.mean([c[g] for g in J["cands"] if g != own])
        # incumbents' leave-self-out lab alignment (same draws rule)
        ai = []
        for b, lab, z in rec["inc_lab"]:
            if b == excl:
                continue
            others = [x for x in J["Hinc"] if x != b and J["inc_lab_of"][x] == lab]
            if not others:
                continue
            hown = np.mean([J["Hinc"][x] for x in others], 0)
            oth = [g for g in J["cands"] if g != lab]
            if not oth:
                continue
            vi = draw_mean(z, rng)
            if vi is None:
                continue
            dl = vi - rec["m"]
            ai.append(cosv(dl, hown) - np.mean([cosv(dl, J["hf"][g]) for g in oth]))
        res.append(dict(day=rec["day"], c=c, a=a, r=(rr / nr) if nr else np.nan, a_inc=np.mean(ai) if ai else np.nan))
    return res


def relabel_p(C1, owns, cands, rng, nperm=10000):
    """Own-lab relabelling null for mean a(1). C1: list of dict lab -> cos."""
    def a_of(c, o):
        return c[o] - np.mean([c[g] for g in c if g != o])
    obs = np.mean([a_of(c, o) for c, o in zip(C1, owns)])
    null = np.empty(nperm)
    for k in range(nperm):
        null[k] = np.mean([a_of(c, cl[rng.integers(len(cl))]) for c, cl in zip(C1, cands)])
    return float(obs), float((1 + (null >= obs).sum()) / (1 + nperm)), float(null.mean())


def slope(y):
    y = np.asarray(y, float)
    x = np.arange(1, len(y) + 1, dtype=float)
    ok = np.isfinite(y)
    if ok.sum() < 3:
        return np.nan
    return float(np.polyfit(x[ok], y[ok], 1)[0])


def boot_mean(v, rng, n=5000):
    v = np.asarray([x for x in v if np.isfinite(x)])
    if len(v) < 2:
        return dict(mean=float(v.mean()) if len(v) else np.nan, lo=np.nan, hi=np.nan, n=int(len(v)))
    b = v[rng.integers(len(v), size=(n, len(v)))].mean(1)
    return dict(mean=float(v.mean()), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)), n=int(len(v)))


def summarize(Js, stats, rng, nperm=10000):
    C1 = [s[0]["c"] for s in stats]
    obs, p, nm = relabel_p(C1, [J["lab"] for J in Js], [J["cands"] for J in Js], rng, nperm)
    a1 = [s[0]["a"] for s in stats]
    sa = [slope([x["a"] for x in s]) for s in stats]
    si = [slope([x["a_inc"] for x in s]) for s in stats]
    did = [x - y for x, y in zip(sa, si)]
    r1 = [s[0]["r"] for s in stats]
    sr = [slope([x["r"] for x in s]) for s in stats]
    return dict(n_joiners=len(Js), a1=dict(mean=obs, p_relabel=p, null_mean=nm, boot=boot_mean(a1, rng)),
                a_slope=boot_mean(sa, rng), a_slope_inc=boot_mean(si, rng), a_slope_did=boot_mean(did, rng),
                r1=boot_mean(r1, rng), r_slope=boot_mean(sr, rng),
                per_joiner=[dict(agent=J["agent"], lab=J["lab"], goal_no=J["goal_no"], regime=J["regime"],
                                 n_days=len(s), n_cands=len(J["cands"]), a=[x["a"] for x in s], r=[x["r"] for x in s],
                                 a_inc=[x["a_inc"] for x in s], n_stmt=[len(rec["Z"]) for rec in J["days"]])
                            for J, s in zip(Js, stats)])


# ============================================================================ synthetic (real skeleton)
def syn_Z(J, world, rng, alpha=1.0, resid_pool=None):
    """Replacement joiner statements: normalize(m_d + alpha(d) h_own + q(d) + resid), resid from incumbents' real
    within-agent-day residuals; q = random direction at the median incumbent |H| (outsider: x3 at day 1, decaying)."""
    hn = np.median([np.linalg.norm(h) for h in J["Hinc"].values()])
    q0 = rng.normal(0, 1, 32)
    q0 = q0 / np.linalg.norm(q0) * hn
    out = []
    for k, rec in enumerate(J["days"]):
        n = len(rec["Z"])
        al = {"J0": 0.0, "J1": alpha, "J2": alpha * k / 5.0, "J3": 0.0}[world]
        q = q0 * (1 + 2 * np.exp(-k / 1.5)) if world == "J3" else q0
        E = resid_pool[rng.integers(len(resid_pool), size=n)]
        out.append(R.unitv(rec["m"] + al * J["hf"][J["lab"]] + q + E))
    return out


def clone_Z(J, rng):
    """J0c: an exchangeable pseudo-joiner = a real incumbent of another lab present in the joiner's room on day 1;
    its real statements replace the joiner's, and it is removed from the room incumbents."""
    c1 = [b for b, z in J["days"][0]["room_inc"] if J["inc_lab_of"].get(b) != J["lab"] and len(z) >= NS]
    if not c1:
        return None, None
    b = c1[rng.integers(len(c1))]
    Z = []
    for rec in J["days"]:
        zz = [z for bb, z in rec["room_inc"] if bb == b]
        Z.append(zz[0] if zz else None)
    return Z, b


def resid_pool_of(Js):
    pool = []
    for J in Js:
        for rec in J["days"]:
            for _, z in rec["room_inc"]:
                pool.append(z - z.mean(0))
    return np.vstack(pool)


def synthetic(Js, reps=200, seed=1):
    rng = np.random.default_rng(seed)
    pool = resid_pool_of(Js)
    out = {}
    for world, alpha in [("J0", 0), ("J0c", 0), ("J1", 0.5), ("J1", 1.0), ("J2", 1.0), ("J3", 0)]:
        key = f"{world}_a{alpha}"
        rec = {"p_a1": [], "a1": [], "a_slope_lo": [], "a_slope": [], "r1": [], "r1_hi": [], "r_slope": [], "r_slope_lo": []}
        for r in range(reps):
            if world == "J0c":
                JJ, stats = [], []
                for J in Js:
                    Z, b = clone_Z(J, rng)
                    if Z is not None:
                        JJ.append(J); stats.append(joiner_stats(J, rng, ndraw=4, Zover=Z, excl=b))
            else:
                JJ = Js
                stats = [joiner_stats(J, rng, ndraw=4, Zover=syn_Z(J, world, rng, alpha, pool)) for J in Js]
            s = summarize(JJ, stats, rng, nperm=1000)
            rec["p_a1"].append(s["a1"]["p_relabel"]); rec["a1"].append(s["a1"]["mean"])
            rec["a_slope"].append(s["a_slope"]["mean"]); rec["a_slope_lo"].append(s["a_slope"]["lo"])
            rec["r1"].append(s["r1"]["mean"]); rec["r1_hi"].append(s["r1"]["hi"])
            rec["r_slope"].append(s["r_slope"]["mean"]); rec["r_slope_lo"].append(s["r_slope"]["lo"])
        out[key] = dict(rate_a1_p05=float(np.mean(np.array(rec["p_a1"]) < 0.05)), a1_mean=float(np.mean(rec["a1"])),
                        a_slope_mean=float(np.mean(rec["a_slope"])),
                        rate_a_slope_ci_pos=float(np.mean(np.array(rec["a_slope_lo"]) > 0)),
                        r1_mean=float(np.nanmean(rec["r1"])), rate_r1_ci_neg=float(np.mean(np.array(rec["r1_hi"]) < 0)),
                        r_slope_mean=float(np.nanmean(rec["r_slope"])),
                        rate_r_slope_ci_pos=float(np.mean(np.array(rec["r_slope_lo"]) > 0)))
        print(key, out[key], flush=True)
    return out


def main():
    t0 = time.time()
    if "--synthetic" in sys.argv:
        reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 200
        Js = build("bge", "white32")
        print("joiners", [(J["agent"], J["lab"], J["goal_no"], len(J["days"]), J["cands"]) for J in Js], flush=True)
        res = dict(joiners=[dict(agent=J["agent"], lab=J["lab"], goal_no=J["goal_no"], n_days=len(J["days"]),
                                 cands=J["cands"], nlab=J["nlab"]) for J in Js], worlds=synthetic(Js, reps))
        res["seconds"] = round(time.time() - t0)
        R.dump(res, R.R2 / "synthetic_B.json")
        return
    rng = np.random.default_rng(20261005)
    out = {}
    for model, kind in (("bge", "white32"), ("gte", "white32"), ("bge", "srp"), ("gte", "srp")):
        Js = build(model, kind)
        stats = [joiner_stats(J, rng) for J in Js]
        out[f"{model}_{kind}"] = summarize(Js, stats, rng)
        s = out[f"{model}_{kind}"]
        print(model, kind, s["n_joiners"], {k: s[k] for k in ("a1", "a_slope", "a_slope_did", "r1", "r_slope")}, flush=True)
        # sensitivity: candidate labs with >= 2 incumbents only
        Js2 = []
        for J in Js:
            c2 = [g for g in J["cands"] if J["nlab"][g] >= 2]
            if J["lab"] in c2 and len(c2) >= 2:
                Js2.append(dict(J, cands=c2))
        if Js2:
            st2 = [joiner_stats(J, rng) for J in Js2]
            out[f"{model}_{kind}_cand2"] = summarize(Js2, st2, rng)
    out["seconds"] = round(time.time() - t0)
    R.dump(out, R.R2 / "encult.json")


if __name__ == "__main__":
    main()
