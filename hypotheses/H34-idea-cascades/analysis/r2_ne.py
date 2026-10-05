"""H34 round 2, R2: room changes as natural experiments (predictions in the card, "Round 2 / R2", written before running).

Source-based branching ratio of an agent group in a period: R_src = sum of tree offspring of the group's first uses /
number of the group's first uses (round-1b trees, ledger visibility). Groups: agents present on both sides of a goal
boundary, keyed by (modal room before, modal room after). Prediction: d ln R_src = 0.451 ln[(N_a - 1)/(N_b - 1)].

  uv run python hypotheses/H34-idea-cascades/analysis/r2_ne.py
Outputs: data/processed/H34-idea-cascades/r2/ne/{groups.parquet, summary.json}
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(HERE))
import h34core as C  # noqa: E402
sys.path.insert(0, str(C.ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = C.SH
R1B = C.OUT / "r1b"
OUTN = C.OUT / "r2" / "ne"
B_EXP = 0.451            # round-1 dilution fit: R ~ (N - 1)^0.451, r_pair ~ (N - 1)^-0.549
BOUNDARIES = [(36, 37), (37, 38), (38, 39), (39, 40), (40, 41), (41, 42)]
MIN_FU = 50
CC_AGENT = 19
B = 2000
FOCUS = (15, 0, "2026-08-05", "2026-08-25")   # #focus, #general, window [start, end)


def chat_nonholdout() -> pl.DataFrame:
    ch = pl.read_parquet(SH / "chat_core.parquet", columns=["t", "pt_date", "goal_no", "room", "speaker_kind", "agent"]).with_row_index("msg")
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "holdout"])
    ch = ch.join(cal, on="pt_date", how="left")
    hm = np.array(holdout_mask(ch["pt_date"].to_list(), ch["goal_no"].to_list()))
    return ch.filter(pl.Series(~hm & ~ch["holdout"].fill_null(False).to_numpy())).drop("holdout")


def modal_rooms(ch: pl.DataFrame, g: int) -> dict[int, int]:
    a = ch.filter((pl.col("goal_no") == g) & (pl.col("speaker_kind") == "agent") & (pl.col("agent") != CC_AGENT)
                  & pl.col("room").is_in([2, 3, 4]))
    cnt = a.group_by("agent", "room").len().sort(["agent", "len", "room"], descending=[False, True, False])
    return {int(r["agent"]): int(r["room"]) for r in cnt.group_by("agent", maintain_order=True).first().iter_rows(named=True)}


def load_fu(g: int) -> pl.DataFrame:
    return pl.read_parquet(R1B / f"G{g:02d}" / "first_uses.parquet")


def idea_sums(fu: pl.DataFrame, members: list[int]) -> tuple[np.ndarray, np.ndarray]:
    """Offspring sum and node count of the group's first uses, per idea of the period (aligned to the period's sorted ideas)."""
    ideas = np.unique(fu["idea"].to_numpy())
    f = fu.filter(pl.col("agent").is_in(members)).group_by("idea").agg(pl.col("offspring").sum().alias("o"), pl.len().alias("n"))
    o = np.zeros(len(ideas)); n = np.zeros(len(ideas))
    j = np.searchsorted(ideas, f["idea"].to_numpy())
    o[j] = f["o"].to_numpy(); n[j] = f["n"].to_numpy()
    return o, n


def boot_lnR(o: np.ndarray, n: np.ndarray, g: int) -> np.ndarray:
    """Poisson idea bootstrap with one weight draw per period (shared by every group of that period, so groups of the same
    period are resampled jointly)."""
    W = np.random.default_rng(1000 + g).poisson(1.0, size=(B, len(o))).astype(np.float32)
    num, den = W @ o.astype(np.float32), W @ n.astype(np.float32)
    return np.log(np.maximum(num, 1e-9) / np.maximum(den, 1e-9))


def main():
    ch = chat_nonholdout()
    rooms = {g: modal_rooms(ch, g) for g in range(36, 43)}
    fus = {g: load_fu(g) for g in range(36, 43)}
    rng = np.random.default_rng(20261005)
    df, summ = estimate(fus, rooms, rng)
    OUTN.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUTN / "groups.parquet")
    summ["rho40"] = partition_contrast(fus[40], rooms[39], rooms[40], rng)
    summ["focus51"] = focus51(ch, rng)
    (OUTN / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    with pl.Config(tbl_rows=40, tbl_cols=20, tbl_width_chars=250, float_precision=3):
        print(df.drop("members"))
    print(json.dumps(summ, indent=1, default=float))


def estimate(fus: dict, rooms: dict, rng, B_: int | None = None):
    global B
    if B_ is not None:
        B = B_
    Nroom = {g: {r: sum(1 for v in rooms[g].values() if v == r) for r in set(rooms[g].values())} for g in rooms}
    rows, boots = [], {}
    for (g0, g1) in BOUNDARIES:
        both = sorted(set(rooms[g0]) & set(rooms[g1]))
        keys = sorted({(rooms[g0][a], rooms[g1][a]) for a in both})
        for (rb, ra) in keys:
            mem = [a for a in both if (rooms[g0][a], rooms[g1][a]) == (rb, ra)]
            nb, na = Nroom[g0][rb], Nroom[g1][ra]
            if nb < 2 or na < 2:
                continue
            o0, n0 = idea_sums(fus[g0], mem)
            o1, n1 = idea_sums(fus[g1], mem)
            d_pred = B_EXP * math.log((na - 1) / (nb - 1))
            r = dict(boundary=f"{g0}->{g1}", g0=g0, g1=g1, room_before=rb, room_after=ra, members=json.dumps(mem), n_members=len(mem),
                     N_before=nb, N_after=na, fu_before=int(n0.sum()), fu_after=int(n1.sum()), d_pred=d_pred,
                     dpair_pred=(B_EXP - 1) * math.log((na - 1) / (nb - 1)))
            if n0.sum() >= MIN_FU and n1.sum() >= MIN_FU and o0.sum() > 0 and o1.sum() > 0:
                R0, R1 = o0.sum() / n0.sum(), o1.sum() / n1.sum()
                b0, b1 = boot_lnR(o0, n0, g0), boot_lnR(o1, n1, g1)
                d = math.log(R1 / R0)
                db = b1 - b0
                r.update(R_before=R0, R_after=R1, d_obs=d, d_lo=float(np.percentile(db, 2.5)), d_hi=float(np.percentile(db, 97.5)),
                         rpair_before=R0 / (nb - 1), rpair_after=R1 / (na - 1),
                         dpair_obs=d - math.log((na - 1) / (nb - 1)), used=True)
                boots[(g0, rb, ra)] = db
            else:
                r.update(used=False)
            rows.append(r)
    df = pl.DataFrame(rows, infer_schema_length=None)
    u = df.filter(pl.col("used"))
    # boundary fixed effects: within-boundary demeaning
    bnd = u["boundary"].to_list()
    x = u["d_pred"].to_numpy(); y = u["d_obs"].to_numpy()
    keys = [(int(a), int(b), int(c)) for a, b, c in zip(u["g0"], u["room_before"], u["room_after"])]
    Yb = np.stack([boots[k] for k in keys], 1)          # (B, n)

    def demean(v, labels):
        v = np.asarray(v, float).copy()
        for lab in set(labels):
            m = np.array([l_ == lab for l_ in labels])
            v[..., m] = v[..., m] - v[..., m].mean(-1, keepdims=True)
        return v
    multi = [b for b in set(bnd) if bnd.count(b) >= 2]
    sel = np.array([b in multi for b in bnd])
    xs, ys, Ybs, ls = x[sel], y[sel], Yb[:, sel], [b for b, s in zip(bnd, sel) if s]
    xt, yt = demean(xs, ls), demean(ys, ls)
    beta = float((xt @ yt) / (xt @ xt))
    Ybt = demean(Ybs, ls)
    bb = (Ybt @ xt) / (xt @ xt)
    res = yt - beta * xt
    dof = len(ys) - len(set(ls)) - 1
    se_res = math.sqrt((res @ res) / max(dof, 1) / (xt @ xt))
    tq = stats.t.ppf(0.975, max(dof, 1))
    ci_boot = (float(np.percentile(bb, 2.5)), float(np.percentile(bb, 97.5)))
    ci_res = (beta - tq * se_res, beta + tq * se_res)
    ci = (min(ci_boot[0], ci_res[0]), max(ci_boot[1], ci_res[1]))
    summ = dict(beta=beta, beta_ci_boot=ci_boot, beta_ci_resid=ci_res, beta_ci=ci, b_implied=B_EXP * beta,
                b_implied_ci=(B_EXP * ci[0], B_EXP * ci[1]), n_groups=int(sel.sum()), n_boundaries=len(set(ls)), dof=dof,
                dropped=[(r["boundary"], r["room_before"], r["room_after"], r["fu_before"], r["fu_after"]) for r in df.filter(~pl.col("used")).iter_rows(named=True)])
    summ["P1"] = "supported" if (ci[0] > 0 and ci[0] <= 1 <= ci[1]) else ("failed" if ci[1] < 0.3 else "mixed")
    # NE42 A-B-A: D = DiD(merge) - DiD(split); DiD = d(#best) - d(#rest)
    def get(g0, rb, ra):
        k = (g0, rb, ra)
        row = u.filter((pl.col("g0") == g0) & (pl.col("room_before") == rb) & (pl.col("room_after") == ra))
        return (float(row["d_obs"][0]), boots[k]) if row.height else (np.nan, None)
    mb, mbb = get(39, 2, 4); mr, mrb = get(39, 3, 4); sb, sbb = get(40, 4, 2); sr, srb = get(40, 4, 3)
    if all(v is not None for v in (mbb, mrb, sbb, srb)):
        Dm, Ds = mb - mr, sb - sr
        Dmb, Dsb = mbb - mrb, sbb - srb
        Db = Dmb - Dsb
        summ["NE42"] = dict(DiD_merge=Dm, DiD_merge_ci=list(np.percentile(Dmb, [2.5, 97.5])), DiD_split=Ds,
                            DiD_split_ci=list(np.percentile(Dsb, [2.5, 97.5])), D=Dm - Ds, D_ci=list(np.percentile(Db, [2.5, 97.5])),
                            D_pred=2 * B_EXP * (math.log(13 / 3) - math.log(13 / 10)))
    else:
        summ["NE42"] = dict(missing=[k for k, v in (("merge_best", mbb), ("merge_rest", mrb), ("split_best", sbb), ("split_rest", srb)) if v is None])
    # P4: per-pair direction for groups with |d_pred| >= 0.1
    big = u.filter(pl.col("d_pred").abs() >= 0.1)
    ok = int(((np.sign(big["dpair_obs"].to_numpy()) == np.sign(big["dpair_pred"].to_numpy()))).sum())
    summ["P4"] = [ok, big.height]
    return df, summ


def partition_contrast(fu: pl.DataFrame, old: dict, new: dict, rng) -> dict:
    """Per-pair transmission rate in #40 for pairs that shared a room in #39 (old-same) vs not (old-cross)."""
    merged = {a for a, r in new.items() if r == 4}
    f = fu.filter(pl.col("agent").is_in(list(merged))).sort("idea", "t_us")
    per = {}
    for idea, grp in f.group_by("idea", maintain_order=True):
        ag = grp["agent"].to_list(); tt = grp["t_us"].to_list(); par = grp["parent"].to_list(); st = grp["status"].to_list()
        first = {a: t for a, t in zip(ag, tt)}
        ts, os_, tc, oc = 0, 0, 0, 0
        for a, t in zip(ag, tt):
            others = [b for b in merged if b != a and first.get(b, np.inf) > t]
            same = [b for b in others if old.get(b) == old.get(a)]
            os_ += len(same); oc += len(others) - len(same)
        for a, p, s in zip(ag, par, st):
            if s == 1 and p in first and p in merged:
                if old.get(p) == old.get(a):
                    ts += 1
                else:
                    tc += 1
        per[idea[0] if isinstance(idea, tuple) else idea] = (ts, os_, tc, oc)
    A = np.array(list(per.values()), float)
    if A[:, 1].sum() == 0 or A[:, 3].sum() == 0:
        return {}
    r_s, r_c = A[:, 0].sum() / A[:, 1].sum(), A[:, 2].sum() / A[:, 3].sum()
    k = len(A)
    w = rng.multinomial(k, np.full(k, 1 / k), size=B).astype(float)
    S_ = w @ A
    rb = (S_[:, 2] / S_[:, 3]) / np.maximum(S_[:, 0] / S_[:, 1], 1e-12)
    return dict(r_same=r_s, r_cross=r_c, rho=r_c / r_s, rho_ci=list(np.percentile(rb, [2.5, 97.5])), trans_same=int(A[:, 0].sum()),
                trans_cross=int(A[:, 2].sum()), opp_same=int(A[:, 1].sum()), opp_cross=int(A[:, 3].sum()), n_ideas=k)


def focus51(ch: pl.DataFrame, rng) -> dict:
    meta = json.loads((R1B / "G51" / "meta.json").read_text())
    days = meta["days"]
    rows = ch.filter((pl.col("goal_no") == 51) & pl.col("pt_date").is_in(days)).sort("msg")
    room = rows["room"].to_numpy(); pdate = rows["pt_date"].to_numpy()
    fu = load_fu(51)
    pos = fu["pos"].to_numpy()
    fr, fd = room[pos], pdate[pos]
    inwin = (fd >= FOCUS[2]) & (fd < FOCUS[3])
    w = rows.filter(pl.col("pt_date").is_between(FOCUS[2], FOCUS[3], closed="left") & (pl.col("speaker_kind") == "agent")
                    & (pl.col("agent") != CC_AGENT))
    N = {r: int(w.filter(pl.col("room") == r)["agent"].n_unique()) for r in (FOCUS[0], FOCUS[1])}
    out = dict(N_focus=N[FOCUS[0]], N_general=N[FOCUS[1]], pred_ratio=((N[FOCUS[0]] - 1) / (N[FOCUS[1]] - 1)) ** (B_EXP - 1) if N[FOCUS[0]] > 1 else np.nan)
    ideas = fu["idea"].to_numpy(); off = fu["offspring"].to_numpy().astype(float)
    for lab, r in (("focus", FOCUS[0]), ("general", FOCUS[1])):
        m = inwin & (fr == r)
        out[f"fu_{lab}"] = int(m.sum())
        out[f"R_{lab}"] = float(off[m].mean()) if m.any() else np.nan
        out[f"rpair_{lab}"] = out[f"R_{lab}"] / max(N[r] - 1, 1)
    if out["fu_focus"] >= MIN_FU:
        # idea bootstrap of the per-pair ratio
        mf, mg = inwin & (fr == FOCUS[0]), inwin & (fr == FOCUS[1])
        ui, inv = np.unique(ideas[mf | mg], return_inverse=True)
        sub_off, sub_f = off[mf | mg], mf[mf | mg]
        Of = np.bincount(inv, weights=sub_off * sub_f, minlength=len(ui)); Nf = np.bincount(inv, weights=sub_f.astype(float), minlength=len(ui))
        Og = np.bincount(inv, weights=sub_off * ~sub_f, minlength=len(ui)); Ng = np.bincount(inv, weights=(~sub_f).astype(float), minlength=len(ui))
        k = len(ui)
        W = rng.multinomial(k, np.full(k, 1 / k), size=B).astype(float)
        rb = ((W @ Of) / np.maximum(W @ Nf, 1e-9) / max(N[FOCUS[0]] - 1, 1)) / np.maximum((W @ Og) / np.maximum(W @ Ng, 1e-9) / max(N[FOCUS[1]] - 1, 1), 1e-12)
        out.update(ratio=out["rpair_focus"] / out["rpair_general"], ratio_ci=list(np.percentile(rb, [2.5, 97.5])))
    return out


# ============================================================================================ synthetic (skeleton beta)
_SINP = {}


def _sinit():
    sh = C.Shared()
    for g in range(36, 43):
        empty = pl.DataFrame(schema={"msg": pl.UInt32, "marker": pl.Int64, "cls": pl.UInt8})
        _SINP[g] = C.period_inputs(sh, g, uses=empty)


def synth_task(task):
    import zlib
    from r2_mixture import simulate_ideas_het
    q, eps, rep = task
    fus = {}
    for g in range(36, 43):
        inp = dict(_SINP[g])
        rng = np.random.default_rng(zlib.crc32(repr((q, eps, rep, g)).encode()))
        n_ideas = 900
        upos, umk = simulate_ideas_het(inp, n_ideas, np.full(n_ideas, q), eps, rng)
        inp.update(use_pos=upos, use_marker=umk, use_cls=np.full(len(upos), 2, dtype=np.int8))
        fus[g] = C.assemble(inp, atrisk_cap=1, seed=rep, with_null=False)["first_uses"]
    return task, fus


def synth():
    from multiprocessing import Pool
    assert not C.R1B
    ch = chat_nonholdout()
    rooms = {g: modal_rooms(ch, g) for g in range(36, 43)}
    tasks = [(q, eps, rep) for q, eps in ((0.015, 0.0005), (0.04, 0.0005), (0.0, 0.002)) for rep in range(3)]
    with Pool(2, initializer=_sinit) as pool:
        outs = pool.map(synth_task, tasks, chunksize=1)
    rows = []
    for (q, eps, rep), fus in outs:
        rng = np.random.default_rng(rep)
        df, summ = estimate(fus, rooms, rng, B_=300)
        ne = summ.get("NE42", {})
        rh = partition_contrast(fus[40], rooms[39], rooms[40], rng)
        big = df.filter(pl.col("used") & (pl.col("d_pred").abs() >= 0.1))
        p4 = int((np.sign(big["dpair_obs"].to_numpy()) == np.sign(big["dpair_pred"].to_numpy())).sum())
        rows.append(dict(rho=rh.get("rho", np.nan), rho_lo=rh.get("rho_ci", [np.nan, np.nan])[0], rho_hi=rh.get("rho_ci", [np.nan, np.nan])[1],
                         p4=f"{p4}/{big.height}", q=q, eps=eps, rep=rep, beta=summ["beta"], beta_lo=summ["beta_ci"][0], beta_hi=summ["beta_ci"][1],
                         n_groups=summ["n_groups"], D=ne.get("D", np.nan), D_lo=(ne.get("D_ci") or [np.nan, np.nan])[0],
                         D_hi=(ne.get("D_ci") or [np.nan, np.nan])[1], dropped=len(summ["dropped"])))
        print(rows[-1], flush=True)
    OUTN.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(rows).write_parquet(OUTN / "synth.parquet")
    with pl.Config(tbl_rows=40, tbl_cols=20, float_precision=3):
        print(pl.DataFrame(rows))


if __name__ == "__main__":
    synth() if len(sys.argv) > 1 and sys.argv[1] == "synth" else main()
