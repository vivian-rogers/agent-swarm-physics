"""H36 round 2, R5 (2026-10-05): scaffold detector from action-mix change points (pre-registered in the card, Round 2,
with Amendment R5-A1).

Channels per agent-day, against the agent's own pooled previous <= 10 active non-holdout days (>= 5 needed):
  tool  : tokens = computer-use action type (actions.action, top 20 + other) plus non-computer-use call kinds
          (call_windows.kind in talk, pause, wait, search, room_move, request)
  bash  : tokens = bash_head_fixed on bash turns (top 40 + other + none)
  bnd   : context-boundary rate = (consolidate + session_start calls) / all calls
u-score: JSD to the baseline standardized by 50 multinomial draws from the (smoothed) baseline at the day's count; for
bnd the binomial z. Agent-days need >= 20 tokens (calls). Day score = median u over >= 3 agents. Channel z =
h36lib.trailing_z of the day score; z_R5 = max(z_tool, z_bash, |z_bnd|). Alarm z_R5 >= 4.

Evaluation: H74's rule (days.parquet read as data; shared event_catalog + evaluation_catalog; window -1..+1; placebo
= has_baseline, not gap_return, >= 3 calendar active days from every catalogued event; AUC of window max vs placebo
windows with a 1,000-draw bootstrap; random-date null 2,000 draws in the same regime). Compared channels: R5 and its
three sub-channels, H74's S (shared schema_diff_daily.z_S), H74's M and fused F (H74 scores.parquet, read as data),
and the union max(S, R5).

Synthetic (--synthetic): the real agent-day skeleton (agents, days, token counts per channel) with agent baselines
drawn around the real pooled mix and Dirichlet-multinomial day noise calibrated to the real within-agent dispersion;
planted synchronous steps on 10 random days each (new tool token at 5%, one bash token halved, boundary rate x1.5)
and roster nuisance (newcomer agents with a different mix).

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r2_scaffold.py [--synthetic]
Outputs: data/processed/H36-reorganization-alarm/r2/scaffold_{agentday,days}.parquet, scaffold.json, scaffold_synthetic.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R2 = L.OUT / "r2"
H74D = L.ROOT / "data/processed/H74-change-detector"
PT = "America/Los_Angeles"
TAU, MIN_TOK, BASE, MIN_BASE, NDRAW = 4.0, 20, 10, 5, 50
KINDS_TOOL = ["talk", "pause", "wait", "search", "room_move", "request"]
STEP = {"new": 0.05, "halve": 0.5, "bnd": 1.5}   # pre-registered step sizes; --big (post hoc power check): 0.20, 0.0, 3.0
CLASSES = ["scaffold_tool", "scaffold_prompt", "scaffold_family", "operator", "operator_schedule", "goal", "roster", "room"]


def jsd(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    """JSD (nats) between rows of p (k x V) and q (V)."""
    m = 0.5 * (p + q[None, :])
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.where(p > 0, p * np.log(p / m), 0.0).sum(1)
        b = np.where(q[None, :] > 0, q[None, :] * np.log(q[None, :] / m), 0.0).sum(1)
    return 0.5 * (a + b)


def load_tokens():
    """Agent-day token count matrices (non-holdout days only): tool (A x V1), bash (A x V2), boundary (k, n)."""
    cal = pl.read_parquet(L.SH / "calendar.parquet").select("pt_date", "goal_no", "holdout")
    nh = set(cal.filter(~pl.col("holdout"))["pt_date"].to_list())
    act = (pl.scan_parquet(L.SH / "actions.parquet").select("t", "agent", "action").with_row_index("row")
           .with_columns(pl.col("t").dt.convert_time_zone(PT).dt.date().cast(pl.String).alias("pt_date"))
           .filter(pl.col("pt_date").is_in(list(nh))).collect())
    bh = pl.scan_parquet(L.SH / "actions_bash_head_fixed.parquet").select("row", "bash_head_fixed").collect()
    act = act.join(bh.with_columns(pl.col("row").cast(pl.UInt32)), on="row", how="left")
    act = act.with_columns(pl.col("action").cast(pl.String), pl.col("bash_head_fixed").cast(pl.String))
    cw = (pl.scan_parquet(L.SH / "call_windows.parquet").filter(~pl.col("holdout")).select("agent", "pt_date", "kind")
          .with_columns(pl.col("kind").cast(pl.String)).collect())
    used = cal.filter(pl.col("pt_date").is_in(sorted(set(act["pt_date"].to_list()) | set(cw["pt_date"].to_list()))))
    assert not any(L.holdout_mask(used["pt_date"].to_list(), used["goal_no"].to_list()))
    top_a = act.group_by("action").len().sort("len", descending=True).head(20)["action"].to_list()
    tool = pl.concat([
        act.select("agent", "pt_date", pl.when(pl.col("action").is_in(top_a)).then("a:" + pl.col("action")).otherwise(pl.lit("a:other")).alias("tok")),
        cw.filter(pl.col("kind").is_in(KINDS_TOOL)).select("agent", "pt_date", ("k:" + pl.col("kind")).alias("tok"))])
    b = act.filter(pl.col("action") == "bash")
    top_b = b.filter(pl.col("bash_head_fixed").is_not_null()).group_by("bash_head_fixed").len().sort("len", descending=True).head(40)["bash_head_fixed"].to_list()
    bash = b.select("agent", "pt_date", pl.when(pl.col("bash_head_fixed").is_null()).then(pl.lit("none"))
                    .when(pl.col("bash_head_fixed").is_in(top_b)).then(pl.col("bash_head_fixed")).otherwise(pl.lit("other")).alias("tok"))
    bnd = cw.group_by("agent", "pt_date").agg(pl.col("kind").is_in(["consolidate", "session_start"]).sum().alias("k"), pl.len().alias("n"))
    return tool, bash, bnd


def pivot(tok: pl.DataFrame):
    c = tok.group_by("agent", "pt_date", "tok").len()
    vocab = sorted(c["tok"].unique().to_list())
    keys = c.select("agent", "pt_date").unique().sort("agent", "pt_date")
    vi = {v: i for i, v in enumerate(vocab)}
    ki = {(a, d): i for i, (a, d) in enumerate(keys.iter_rows())}
    Cm = np.zeros((keys.height, len(vocab)))
    for a, d, t, n in c.iter_rows():
        Cm[ki[(a, d)], vi[t]] = n
    return keys, Cm, vocab


def u_mix(keys: pl.DataFrame, Cm: np.ndarray, dayorder: dict, rng) -> np.ndarray:
    """Per agent-day u-score of the token mix vs the agent's pooled previous <= BASE active days."""
    u = np.full(keys.height, np.nan)
    V = Cm.shape[1]
    ag = keys["agent"].to_numpy(); dd = np.array([dayorder.get(d, -1) for d in keys["pt_date"].to_list()])
    for a in np.unique(ag):
        ix = np.flatnonzero(ag == a)
        ix = ix[np.argsort(dd[ix])]
        ix = ix[dd[ix] >= 0]
        for j in range(MIN_BASE, ix.size):
            n = Cm[ix[j]].sum()
            if n < MIN_TOK:
                continue
            base = Cm[ix[max(0, j - BASE):j]].sum(0)
            q = (base + 0.5) / (base.sum() + 0.5 * V)
            obs = jsd(Cm[ix[j]][None, :] / n, q)[0]
            draws = rng.multinomial(int(n), q, size=NDRAW) / n
            nul = jsd(draws, q)
            u[ix[j]] = (obs - nul.mean()) / max(nul.std(), 1e-9)
    return u


def u_rate(bnd: pl.DataFrame, dayorder: dict) -> np.ndarray:
    u = np.full(bnd.height, np.nan)
    ag = bnd["agent"].to_numpy(); dd = np.array([dayorder.get(d, -1) for d in bnd["pt_date"].to_list()])
    k = bnd["k"].to_numpy().astype(float); n = bnd["n"].to_numpy().astype(float)
    for a in np.unique(ag):
        ix = np.flatnonzero(ag == a); ix = ix[np.argsort(dd[ix])]; ix = ix[dd[ix] >= 0]
        for j in range(MIN_BASE, ix.size):
            if n[ix[j]] < MIN_TOK:
                continue
            b = ix[max(0, j - BASE):j]
            p0 = (k[b].sum() + 0.5) / (n[b].sum() + 1.0)
            u[ix[j]] = (k[ix[j]] - n[ix[j]] * p0) / np.sqrt(n[ix[j]] * p0 * (1 - p0))
    return u


def day_scores(frames: dict, dl: list[str]) -> dict:
    """frames: channel -> (keys with u). Returns channel z arrays over dl and the day medians."""
    out, med = {}, {}
    for ch, kf in frames.items():
        m = kf.filter(pl.col("u").is_finite()).group_by("pt_date").agg(pl.col("u").median().alias("m"), pl.len().alias("na"))
        m = m.filter(pl.col("na") >= 3)
        dm = dict(zip(m["pt_date"].to_list(), m["m"].to_list()))
        x = np.array([dm.get(d, np.nan) for d in dl], float)
        med[ch] = x
        out[ch] = L.trailing_z(x)
    with np.errstate(all="ignore"):
        out["R5"] = np.nanmax(np.vstack([out["tool"], out["bash"], np.abs(out["bnd"])]), 0)
    return out, med


# ---------------------------------------------------------------------------------------------- evaluation (H74 rule)
def window_array(score, cal_days, day_pos):
    v = np.array([score[day_pos[d]] if d in day_pos else np.nan for d in cal_days], float)
    pad = np.r_[np.nan, v, np.nan]
    W = np.vstack([pad[:-2], pad[1:-1], pad[2:]])
    with np.errstate(all="ignore"):
        return np.where(np.all(np.isnan(W), 0), np.nan, np.nanmax(W, 0))


def evaluate(scores, days, events, cal_days, classes, rng, exclude=None, n_rand=2000, n_boot=1000):
    dl = days["pt_date"].to_list(); day_pos = {d: i for i, d in enumerate(dl)}; cal_pos = {d: i for i, d in enumerate(cal_days)}
    ev = events.filter(~pl.col("held0") & pl.col("day0").is_in(dl))
    excl = events if exclude is None else pl.concat([events.select("day0"), exclude.select("day0")])
    centers = np.array(sorted({cal_pos[d] for d in excl["day0"].drop_nulls().to_list() if d in cal_pos}))
    eligible = days.filter(pl.col("has_baseline"))["pt_date"].to_list()
    gapret = set(days.filter(pl.col("gap_return"))["pt_date"].to_list())
    placebo = [d for d in eligible if d not in gapret and np.min(np.abs(centers - cal_pos[d])) >= 3]
    pc = np.array([cal_pos[d] for d in placebo], int)
    wd = dict(zip(dl, days["weekday"].to_list())); mon = np.array([wd[d] == 1 for d in placebo])
    regime_of = dict(zip(dl, days["regime"].to_list()))
    pools = {r: np.array([cal_pos[d] for d in eligible if regime_of[d] == r and d not in gapret], int) for r in set(regime_of.values())}
    res = {"n_placebo": len(placebo), "classes": {}, "far": {}}
    for ch, sc in scores.items():
        wm = window_array(sc, cal_days, day_pos)
        pday = np.array([sc[day_pos[d]] for d in placebo]); pw = wm[pc]
        res["far"][ch] = {"per_day": float(np.nanmean(pday >= TAU)), "per_day_k": int(np.nansum(pday >= TAU)),
                          "window": float(np.nanmean(pw >= TAU)),
                          "monday_per_day": float(np.nanmean(pday[mon] >= TAU)) if mon.any() else None, "n_scored": int(np.isfinite(pday).sum())}
        for cls in classes:
            e = ev.filter(pl.col("cls") == cls)
            if e.height == 0:
                continue
            cent = np.array([cal_pos[d] for d in e["day0"].to_list()], int)
            ew = wm[cent]; ok = np.isfinite(ew)
            if ok.sum() == 0:
                continue
            x = ew[ok]; hit = float(np.mean(x >= TAU)); pwf = pw[np.isfinite(pw)]
            a = L.auc(x, pwf)
            boots = [L.auc(x[rng.integers(0, x.size, x.size)], pwf[rng.integers(0, pwf.size, pwf.size)]) for _ in range(n_boot)]
            regs = [regime_of[d] for d, o in zip(e["day0"].to_list(), ok) if o]
            draws = np.column_stack([pools[r][rng.integers(0, len(pools[r]), n_rand)] for r in regs])
            W = wm[draws]
            with np.errstate(all="ignore"):
                rh = np.nanmean(W >= TAU, 1)
            res["classes"].setdefault(cls, {})[ch] = {
                "n": int(ok.sum()), "hit": hit, "auc": a,
                "auc_ci": [float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5))],
                "p_rand_hit": float((1 + np.sum(rh >= hit)) / (1 + n_rand)),
                "events": [{"day0": d, "label": lab[:60], "score": float(v) if np.isfinite(v) else None}
                           for d, lab, v in zip(e["day0"].to_list(), e["label"].to_list(), ew)]}
    return res


def load_days():
    days = pl.read_parquet(H74D / "days.parquet")
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("n_agent_events") > 0).sort("pt_date")
    cal_days = cal["pt_date"].to_list(); held = dict(zip(cal_days, cal["holdout"].to_list()))
    prev_held = {d: (i > 0 and held[cal_days[i - 1]]) for i, d in enumerate(cal_days)}
    days = days.with_columns(pl.col("pt_date").replace_strict(prev_held, return_dtype=pl.Boolean).alias("gap_return"),
                             (pl.col("idx") >= 10).alias("has_baseline"))
    assert not any(held[d] for d in days["pt_date"].to_list())
    return days, cal_days


# ---------------------------------------------------------------------------------------------- synthetic
def synthetic(keys_t, Ct, keys_b, Cb, bnd, dl, rng, roster_days=(), runs: int = 10) -> dict:
    """Real skeleton; synthetic counts. Dispersion: Dirichlet concentration fit so that the median real within-agent
    day-to-day JSD excess (u) of the tool channel is matched on clean synthetic days (a short grid search)."""
    dayorder = {d: i for i, d in enumerate(dl)}
    pool_t = Ct.sum(0) / Ct.sum(); pool_b = Cb.sum(0) / Cb.sum()
    ut_real = u_mix(keys_t, Ct, dayorder, rng)
    target = float(np.nanmedian(ut_real))

    def gen(kf, C, pool, conc, steps, *, new_tok=None, halve_tok=None, rr):
        ag = kf["agent"].to_numpy(); dd = np.array([dayorder[d] for d in kf["pt_date"].to_list()])
        n = C.sum(1).astype(int)
        base = {a: rr.dirichlet(pool * 200 + 0.05) for a in np.unique(ag)}
        out = np.zeros_like(C)
        for i in range(kf.height):
            p = base[ag[i]].copy()
            if dd[i] in steps:
                if new_tok is not None:
                    p = p * (1 - STEP["new"]); p[new_tok] += STEP["new"]
                if halve_tok is not None:
                    p[halve_tok] *= STEP["halve"]; p /= p.sum()
            pd_ = rr.dirichlet(p * conc + 1e-3)
            out[i] = rr.multinomial(n[i], pd_ / pd_.sum())
        return out

    # calibrate concentration on the tool channel (no steps)
    best = None
    for conc in (50, 100, 200, 400, 800, 1600):
        Cs = gen(keys_t, Ct, pool_t, conc, set(), rr=np.random.default_rng(1))
        m = float(np.nanmedian(u_mix(keys_t, Cs, dayorder, np.random.default_rng(2))))
        if best is None or abs(m - target) < abs(best[1] - target):
            best = (conc, m)
    conc = best[0]
    rare_t = int(np.argmin(pool_t)); mid_b = int(np.argsort(pool_b)[-3] if STEP["halve"] > 0 else np.argsort(pool_b)[-2])
    res = {"real_median_u_tool": target, "conc": conc, "syn_median_u_tool": best[1], "runs": []}
    D = len(dl)
    for r in range(runs):
        rr = np.random.default_rng([L.SEED, 55, r])
        st = set(rr.choice(np.arange(15, D - 2), 30, replace=False).tolist())
        s_tool, s_bash, s_bnd = set(list(st)[:10]), set(list(st)[10:20]), set(list(st)[20:30])
        Ct_s = gen(keys_t, Ct, pool_t, conc, s_tool, new_tok=rare_t, rr=rr)
        Cb_s = gen(keys_b, Cb, pool_b, conc, s_bash, halve_tok=mid_b, rr=rr)
        ag = bnd["agent"].to_numpy(); dd = np.array([dayorder[d] for d in bnd["pt_date"].to_list()])
        p0 = {a: max(1e-3, rr.beta(2, 30)) for a in np.unique(ag)}
        k = np.array([rr.binomial(int(n), min(0.99, p0[a] * (STEP["bnd"] if d in s_bnd else 1.0) * rr.lognormal(0, 0.25)))
                      for a, d, n in zip(ag, dd, bnd["n"].to_numpy())])
        fr = {"tool": keys_t.with_columns(pl.Series("u", u_mix(keys_t, Ct_s, dayorder, rr))),
              "bash": keys_b.with_columns(pl.Series("u", u_mix(keys_b, Cb_s, dayorder, rr))),
              "bnd": bnd.with_columns(pl.Series("k", k)).pipe(lambda f: f.with_columns(pl.Series("u", u_rate(f, dayorder))))}
        z, _ = day_scores(fr, dl)
        al = np.nan_to_num(z["R5"], nan=-9) >= TAU
        near = np.zeros(D, bool)
        for s in st:
            near[max(0, s - 1):s + 2] = True
        rec = {}
        for nm, S in (("tool", s_tool), ("bash", s_bash), ("bnd", s_bnd)):
            own = np.nan_to_num(np.abs(z[nm]) if nm == "bnd" else z[nm], nan=-9) >= TAU
            rec[f"hit_{nm}_own"] = float(np.mean([own[s] for s in S]))
            rec[f"hit_{nm}_fused"] = float(np.mean([al[s] for s in S]))
        rec["far_clean"] = float(np.mean(al[~near & np.isfinite(z["R5"])]))
        rd = [x for x in roster_days if not near[x]]
        rec["alarm_roster_days"] = float(np.mean([al[max(0, x - 1):x + 2].any() for x in rd])) if rd else None
        res["runs"].append(rec)
    keys_ = res["runs"][0].keys()
    res["mean"] = {k: float(np.mean([x[k] for x in res["runs"] if x[k] is not None])) for k in keys_}
    # roster nuisance: the real roster path is in the skeleton (newcomers have no baseline -> no u for 5 days); report
    # the fused alarm rate on real roster-join days of the synthetic streams in the evaluation step
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--big", action="store_true", help="post hoc power check: larger planted steps")
    a = ap.parse_args()
    if a.big:
        STEP.update(new=0.20, halve=0.0, bnd=3.0)
    R2.mkdir(parents=True, exist_ok=True)
    days, cal_days = load_days()
    dl = days["pt_date"].to_list(); dayorder = {d: i for i, d in enumerate(dl)}
    tool, bash, bnd = load_tokens()
    kt, Ct, vt = pivot(tool); kb, Cb, vb = pivot(bash)
    rng = np.random.default_rng(L.SEED + 5)
    if a.synthetic:
        import event_catalog as ECm  # noqa: E402
        ev = ECm.evaluation_catalog(pl.read_parquet(L.SH / "event_catalog.parquet"))
        rdays = sorted({dayorder[d] for d in ev.filter((pl.col("cls") == "roster") & ~pl.col("held0"))["day0"].to_list() if d in dayorder})
        s = synthetic(kt, Ct, kb, Cb, bnd, dl, rng, roster_days=rdays)
        s["step"] = dict(STEP)
        (R2 / ("scaffold_synthetic_big.json" if a.big else "scaffold_synthetic.json")).write_text(json.dumps(s, indent=1))
        print(json.dumps({k: v for k, v in s.items() if k != "runs"}, indent=1)); return
    fr = {"tool": kt.with_columns(pl.Series("u", u_mix(kt, Ct, dayorder, rng))),
          "bash": kb.with_columns(pl.Series("u", u_mix(kb, Cb, dayorder, rng))),
          "bnd": bnd.with_columns(pl.Series("u", u_rate(bnd, dayorder)))}
    z, med = day_scores(fr, dl)
    sd = pl.read_parquet(L.SH / "schema_diff/schema_diff_daily.parquet")
    zS = dict(zip(sd["pt_date"].to_list(), sd["z_S"].to_list()))
    h74 = pl.read_parquet(H74D / "scores.parquet")
    zM = dict(zip(h74["pt_date"].to_list(), h74["z_M"].to_list())); zF = dict(zip(h74["pt_date"].to_list(), h74["z_F"].to_list()))
    S = np.array([zS.get(d, np.nan) for d in dl], float)
    scores = {"R5": z["R5"], "tool": z["tool"], "bash": z["bash"], "bnd_abs": np.abs(z["bnd"]), "S": S,
              "M_h74": np.array([zM.get(d, np.nan) for d in dl], float), "F_h74": np.array([zF.get(d, np.nan) for d in dl], float)}
    with np.errstate(all="ignore"):
        scores["S_or_R5"] = np.fmax(S, z["R5"])
    import event_catalog as ECm  # noqa: E402  (infra/shared on sys.path via h36lib)
    events = ECm.evaluation_catalog(pl.read_parquet(L.SH / "event_catalog.parquet"))
    doc = events.filter(pl.col("cls") != "undocumented"); und = events.filter(pl.col("cls") == "undocumented")
    res = evaluate(scores, days, doc, cal_days, CLASSES, rng, exclude=und)
    ru = evaluate(scores, days, und, cal_days, ["undocumented"], rng, exclude=doc)
    res["classes"]["undocumented"] = ru["classes"].get("undocumented", {})
    # NE14b positive control and named days
    named = {"NE14b_0324": "2026-03-24", "NE17_0414": "2026-04-14", "NE45_0729": "2026-07-29", "NE40_0420": "2026-04-20"}
    res["named"] = {k: {ch: (float(v[dl.index(d)]) if d in dl and np.isfinite(v[dl.index(d)]) else None) for ch, v in scores.items()}
                    for k, d in named.items()}
    res["n_days_scored"] = {ch: int(np.isfinite(v).sum()) for ch, v in scores.items()}
    res["alarm_days"] = {ch: int(np.nansum(v >= TAU)) for ch, v in scores.items()}
    out_days = days.select("pt_date", "goal_no", "regime").with_columns(
        [pl.Series(k, v) for k, v in scores.items()] + [pl.Series("med_" + k, v) for k, v in med.items()])
    out_days.write_parquet(R2 / "scaffold_days.parquet", compression="zstd")
    pl.concat([f.select("agent", "pt_date", "u").with_columns(pl.lit(ch).alias("channel")) for ch, f in fr.items()]) \
        .write_parquet(R2 / "scaffold_agentday.parquet", compression="zstd")
    (R2 / "scaffold.json").write_text(json.dumps(res, indent=1))
    L.write_provenance("hypotheses/H36-reorganization-alarm/analysis/r2_scaffold.py",
                       ["actions", "actions_bash_head_fixed", "call_windows", "calendar", "event_catalog",
                        "schema_diff/schema_diff_daily", "(H74 days.parquet, scores.parquet as data)"],
                       {"tau": TAU, "min_tok": MIN_TOK, "base": BASE, "min_base": MIN_BASE, "ndraw": NDRAW,
                        "vocab_tool": len(vt), "vocab_bash": len(vb)}, path=R2 / "_provenance.json")
    print("placebo", res["n_placebo"])
    for ch in scores:
        f = res["far"][ch]
        print(f"FAR {ch:8s} per-day {f['per_day']:.3f} ({f['per_day_k']}/{f['n_scored']}) window {f['window']:.2f}")
    for cls in CLASSES + ["undocumented"]:
        for ch in scores:
            c = res["classes"].get(cls, {}).get(ch)
            if c:
                print(f"{cls:17s} {ch:8s} n {c['n']:2d} hit {c['hit']:.2f} AUC {c['auc']:.2f} [{c['auc_ci'][0]:.2f},{c['auc_ci'][1]:.2f}] p {c['p_rand_hit']:.3f}")
    print(json.dumps(res["named"], indent=None))


if __name__ == "__main__":
    main()
