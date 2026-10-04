"""C10 (HH91): do longer sessions run hotter?

  uv run python hypotheses/H08-context-is-the-coupling/analysis/sessions.py [--hawkes]

L1: backlog k per talk turn (H18's talks.parquet, read only) vs session hour (hours since the day's window start):
    Spearman rho and the within-agent-day OLS slope of log(1 + k) on hour; day bootstrap B = 200.
L2 (--hawkes): H04's Hawkes fitter (imported, agent chat, 10 s bins) on the first vs the second half of each day's
    window; paired day bootstrap (B = 30) of the difference in n.
L3 (--hawkes): #51 per-week n vs mean k.
Writes G<NN>/c10.json and c10_hawkes.json.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403
from scipy.stats import spearmanr  # noqa: E402

H18 = ROOT / "data/processed/H18-attention-dilution"
B = 200
NB_H = 30
C10_PERIODS = [37, 38, 39, 40, 41, 42, 44, 51]
HAWKES_PERIODS = [38, 51]


def l1(g: int):
    f = H18 / gname(g) / "talks.parquet"
    if not f.exists():
        return None
    tk = pl.read_parquet(f, columns=["agent", "pt_date", "t_us", "k", "gap_s"])
    days = sorted(set(tk["pt_date"].to_list()) & set(period_days(g)))
    tk = tk.filter(pl.col("pt_date").is_in(days))
    win = windows(days)
    tk = tk.with_columns(pl.struct("pt_date", "t_us").map_elements(lambda r: (r["t_us"] - win[r["pt_date"]][0]) / US / 3600,
                                                                   return_dtype=pl.Float64).alias("hour"))
    nd = len(days); dix = {d: i for i, d in enumerate(days)}
    rng = np.random.default_rng(g)
    W = np.vstack([np.ones((1, nd)), rng.multinomial(nd, np.full(nd, 1 / nd), size=B)]).astype(float)
    x = tk["hour"].to_numpy(); y = np.log1p(tk["k"].to_numpy().astype(float))
    grp = (tk["agent"].cast(pl.Int64) * 10000 + tk["pt_date"].replace_strict(dix, return_dtype=pl.Int64)).to_numpy()
    _, gi = np.unique(grp, return_inverse=True)
    cnt = np.bincount(gi).astype(float)
    xd = x - (np.bincount(gi, x) / cnt)[gi]; yd = y - (np.bincount(gi, y) / cnt)[gi]
    di = tk["pt_date"].replace_strict(dix, return_dtype=pl.Int64).to_numpy()
    sxy = np.bincount(di, xd * yd, minlength=nd); sxx = np.bincount(di, xd * xd, minlength=nd)
    out = {"period": gname(g), "n_talks": tk.height, "n_days": nd,
           "rho_k_hour": float(spearmanr(x, tk["k"].to_numpy()).statistic),
           "slope_logk_per_hour": ci((W @ sxy) / (W @ sxx)),
           "k_by_hour": {int(hh): float(tk.filter(pl.col("hour").floor() == hh)["k"].mean())
                         for hh in range(0, 9) if tk.filter(pl.col("hour").floor() == hh).height >= 30},
           "gap_by_hour_s": {int(hh): float(tk.filter(pl.col("hour").floor() == hh)["gap_s"].median())
                             for hh in range(0, 9) if tk.filter(pl.col("hour").floor() == hh).height >= 30}}
    # also from the H08 turns: per-call new messages by hour (all calls, not only talk turns)
    tf = OUT / gname(g) / "turns.parquet"
    if tf.exists():
        tu = pl.read_parquet(tf, columns=["pt_date", "t_us", "n_new"]).filter(pl.col("pt_date").is_in(days))
        tu = tu.with_columns(pl.struct("pt_date", "t_us").map_elements(lambda r: (r["t_us"] - win[r["pt_date"]][0]) / US / 3600,
                                                                       return_dtype=pl.Float64).alias("hour"))
        out["new_per_call_by_hour"] = {int(hh): float(tu.filter(pl.col("hour").floor() == hh)["n_new"].mean())
                                       for hh in range(0, 9) if tu.filter(pl.col("hour").floor() == hh).height >= 100}
    jdump(out, OUT / gname(g) / "c10.json")
    print(f"{gname(g)}: rho(k, hour) {out['rho_k_hour']:+.3f}, slope {out['slope_logk_per_hour']}", flush=True)
    return out


def hawkes_halves(g: int):
    sys.path.insert(0, str(ROOT / "hypotheses/H04-reversible-forcing/analysis"))
    import hawkes as hk  # H04's fitter (imported, not modified)
    days = period_days(g)
    ser = hk.build_series(days)

    def half(ser, which):
        out = hk.Series([], [], [], [], [])
        for i, d in enumerate(ser.days):
            n = len(ser.y[i]); m = n // 2
            sl = slice(0, m) if which == 0 else slice(m, n)
            L = sl.stop - sl.start
            out.days.append(d); out.y.append(ser.y[i][sl]); out.xh.append(ser.xh[i][sl]); out.xn.append(ser.xn[i][sl])
            out.q.append((np.arange(L) * hk.NQ // max(L, 1)).astype(int))
        return out
    s0, s1 = half(ser, 0), half(ser, 1)
    m0, m1 = hk.fit_suite(s0), hk.fit_suite(s1)
    res = {"period": gname(g), "n_days": len(ser.days), "n_first": m0.summary()["n"], "n_second": m1.summary()["n"],
           "events_first": s0.n_events, "events_second": s1.n_events}
    rng = np.random.default_rng(g)
    diffs = []
    for _ in range(NB_H):
        idx = list(rng.integers(0, len(ser.days), len(ser.days)))
        a = hk.Model(s0.subset(idx), m0.free).fit(x0=m0.theta).summary()["n"]
        b = hk.Model(s1.subset(idx), m1.free).fit(x0=m1.theta).summary()["n"]
        diffs.append(b - a)
    res["delta_n"] = [res["n_second"] - res["n_first"]] + [float(x) for x in np.percentile(diffs, [2.5, 97.5])]
    print(f"{gname(g)} Hawkes halves: n1 {res['n_first']:.3f} n2 {res['n_second']:.3f} delta {res['delta_n']}", flush=True)
    return res


def hawkes_weeks_51():
    sys.path.insert(0, str(ROOT / "hypotheses/H04-reversible-forcing/analysis"))
    import hawkes as hk
    days = period_days(51)
    tk = pl.read_parquet(H18 / "G51" / "talks.parquet", columns=["pt_date", "k"])
    weeks = {}
    for d in days:
        wk = dt.date.fromisoformat(d).isocalendar()[1]
        weeks.setdefault(wk, []).append(d)
    rows = []
    for wk, ds in sorted(weeks.items()):
        if len(ds) < 3:
            continue
        m = hk.fit_suite(hk.build_series(ds))
        kk = tk.filter(pl.col("pt_date").is_in(ds))["k"].mean()
        rows.append({"week": wk, "days": len(ds), "n": m.summary()["n"], "mean_k": float(kk) if kk is not None else None})
        print(f"week {wk}: n {rows[-1]['n']:.3f} mean k {rows[-1]['mean_k']}", flush=True)
    n = np.array([r["n"] for r in rows]); k = np.array([r["mean_k"] for r in rows], float)
    ok = np.isfinite(n) & np.isfinite(k)
    return {"weeks": rows, "rho_n_k": float(spearmanr(n[ok], k[ok]).statistic) if ok.sum() >= 4 else None,
            "n_weeks": int(ok.sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hawkes", action="store_true")
    a = ap.parse_args()
    for g in C10_PERIODS:
        l1(g)
    if a.hawkes:
        out = {"halves": {gname(g): hawkes_halves(g) for g in HAWKES_PERIODS}, "weeks_51": hawkes_weeks_51()}
        jdump(out, OUT / "c10_hawkes.json")
    write_provenance("c10 (G<NN>/c10.json, c10_hawkes.json)", "hypotheses/H08-context-is-the-coupling/analysis/sessions.py",
                     ["H18 G<NN>/talks.parquet", "H08 turns.parquet", "chat_core (via H04 hawkes)", "calendar"],
                     {"B": B, "hawkes_boot": NB_H, "hawkes": "H04 hawkes.py (imported)"})


if __name__ == "__main__":
    main()
