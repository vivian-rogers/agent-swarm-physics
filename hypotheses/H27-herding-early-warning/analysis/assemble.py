"""H27 round-1 assembly: operator base rates and lift, rate-matched nulls for every rule, precursor categories,
per-period false alarms. Items marked POST HOC were added after the round-1 run (card, Amendment 2).

Usage: uv run python hypotheses/H27-herding-early-warning/analysis/assemble.py
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ews_core as E  # noqa: E402
import explore as X  # noqa: E402

DATA = X.DATA


def trigger_check(periods, W=15, p=E.P0, pre_min=30, base=None):
    """POST HOC (Amendment 2): is a herding onset preceded (previous 30 min, onset window excluded) by a human message,
    an automated (nudger / pause) message, or a chat link to that project, more often than matched placebo windows?
    Rival R1 (field steps) predicts yes. Counts only; no text is read."""
    import polars as pl
    from scipy.stats import fisher_exact
    sys.path.insert(0, str(X.ROOT / "hypotheses/H27-herding-early-warning/scheme"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("h27build", X.ROOT / "hypotheses/H27-herding-early-warning/scheme/build.py")
    B = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(B)
    H = B._h11_build()
    cal = pl.read_parquet(X.ROOT / "data/processed/shared/calendar.parquet").select("pt_date", "win_start")
    kicks = pl.read_parquet(X.ROOT / "data/processed/shared/kicks.parquet")
    hum = np.sort(kicks.filter(pl.col("kind") == "human_message")["t"].dt.epoch("s").to_numpy())
    aut = np.sort(kicks.filter(pl.col("kind") == "automated_message")["t"].dt.epoch("s").to_numpy())
    pm = H.project_map()
    am = (pl.scan_parquet(X.ROOT / "data/processed/shared/artifact_mentions.parquet")
          .filter((pl.col("source").cast(pl.String) == "chat") & pl.col("how").cast(pl.String).is_in(["url", "output", "bare"]))
          .select("artifact", "t").collect().join(pm, on="artifact", how="inner")
          .with_columns(pl.col("t").dt.epoch("s").alias("ts")))
    links = {nm: np.sort(d["ts"].to_numpy()) for (nm,), d in am.group_by(["project"])}

    def any_in(arr, lo, hi):
        if arr is None or len(arr) == 0:
            return False
        i = np.searchsorted(arr, lo, side="left")
        return i < len(arr) and arr[i] < hi

    base = base or DATA
    rows = []
    for g in periods:
        k, n, win, day, s = X.load_series(g, W, base)
        on = E.find_onsets(k, n, win, day, p)
        ind = E.all_window_indicators(k, n, p)
        watch = ind["valid"] & ind["matched"]
        sj = s.join(cal, on="pt_date", how="left")
        t0 = (sj["win_start"].dt.epoch("s").to_numpy() + sj["win"].to_numpy().astype(np.int64) * W * 60)
        projs = pl.read_parquet(base / f"G{g:02d}" / f"projects_w{W}.parquet")
        names = dict(zip(projs["label"].to_list(), projs["project"].to_list()))
        T, q = k.shape
        onset_set = {(o["project"], o["w0"]) for o in on}
        for a in range(q):
            lk = links.get(names.get(a + 1))
            w0s = [o["w0"] for o in on if o["project"] == a]
            for t in range(T):
                is_on = (a, t) in onset_set
                if not is_on:
                    if not watch[t, a] or any(t - 4 < w0 <= t + p.horizon for w0 in w0s):
                        continue
                lo, hi = t0[t] - pre_min * 60, t0[t]
                rows.append(dict(goal=g, onset=is_on, human=any_in(hum, lo, hi), automated=any_in(aut, lo, hi), link=any_in(lk, lo, hi)))
    df = pl.DataFrame(rows)
    res = {}
    for col in ("human", "automated", "link"):
        a_ = int(df.filter(pl.col("onset"))[col].sum())
        n1 = int(df["onset"].sum())
        b_ = int(df.filter(~pl.col("onset"))[col].sum())
        n0 = int((~df["onset"]).sum())
        orr, pv = fisher_exact([[a_, n1 - a_], [b_, n0 - b_]]) if n1 else (np.nan, np.nan)
        # period-stratified (Mantel-Haenszel) odds ratio over periods with onsets, and a within-period permutation p
        num = den = 0.0
        strata = []
        for (g,), d in df.group_by(["goal"]):
            if not d["onset"].any():
                continue
            on_ = d["onset"].to_numpy().astype(bool)
            x = d[col].to_numpy().astype(bool)
            a1, b1 = int((on_ & x).sum()), int((on_ & ~x).sum())
            c1, d1 = int((~on_ & x).sum()), int((~on_ & ~x).sum())
            nn = a1 + b1 + c1 + d1
            num += a1 * d1 / nn
            den += b1 * c1 / nn
            strata.append((on_, x))
        if not strata:
            res[col] = dict(onsets_with=a_, onsets=n1, mh_odds_ratio=None, perm_p_within_period=None)
            continue
        obs = sum(int((o & x).sum()) for o, x in strata)
        rng = np.random.default_rng(11)
        perm = np.array([sum(int((rng.permutation(o) & x).sum()) for o, x in strata) for _ in range(2000)])
        res[col] = dict(onsets_with=a_, onsets=n1, placebo_rate=b_ / max(n0, 1), placebo_n=n0, odds_ratio=float(orr), fisher_p=float(pv),
                        mh_odds_ratio=float(num / den) if den else None, perm_p_within_period=float((1 + (perm >= obs).sum()) / 2001),
                        perm_mean=float(perm.mean()))
    return res


def main():
    warnings.simplefilter("ignore")
    tau = X.load_tau_star()
    R = json.loads((DATA / "results_round1.json").read_text())
    out = {}
    rng = np.random.default_rng(20261005)
    for arm, W, p in (("W15", 15, E.P0), ("W30", 30, E.P_W30)):
        periods = R[arm]["periods"]
        tot = {r: dict(watched=0, pos=0, alarms=0, true_alarms=0, hits=0, onsets=0, shift=np.zeros(500)) for r in ("ews", "level", "momentum")}
        prec = dict(total=0, never_seen=0, zero_prev_1h=0, zero_prev_6h=0, day_start=0, last_day=0)
        per = {}
        for g in periods:
            k, n, win, day, s = X.load_series(g, W)
            on = E.find_onsets(k, n, win, day, p)
            ind = E.all_window_indicators(k, n, p)
            per[g] = dict(days=int(len(np.unique(day))))
            for rule in tot:
                al, watch = E.alarms(ind, k, rule, tau, p)
                sc = E.score_alarms(al, watch, on, p)
                T, q = al.shape
                pos = 0
                for a in range(q):
                    w0s = np.array([o["w0"] for o in on if o["project"] == a], int)
                    for t in np.where(watch[:, a])[0]:
                        pos += bool(((w0s > t) & (w0s <= t + p.horizon)).any()) if len(w0s) else 0
                d = tot[rule]
                d["watched"] += int(watch.sum())
                d["pos"] += pos
                d["alarms"] += sc["n_alarms"]
                d["true_alarms"] += sc["true_alarms"]
                d["hits"] += sc["hits"]
                d["onsets"] += sc["n_onsets"]
                d["shift"] += E.shifted_hits(al, watch, on, rng, 500, p)  # POST HOC for level / momentum
                per[g][f"{rule}_false_alarms"] = sc["false_alarms"]
                per[g][f"{rule}_false_alarms_per_day"] = sc["false_alarms"] / max(per[g]["days"], 1)
                per[g][f"{rule}_hits"] = sc["hits"]
            for o in on:
                a, w0 = o["project"], o["w0"]
                prec["total"] += 1
                prec["never_seen"] += int(k[:w0, a].sum() == 0)
                prec["zero_prev_1h"] += int(k[max(0, w0 - 60 // W):w0, a].sum() == 0)
                prec["zero_prev_6h"] += int(k[max(0, w0 - 360 // W):w0, a].sum() == 0)
                prec["day_start"] += int(o["day_start"])
                prec["last_day"] += int(o["last_day"])
        ops = {}
        for rule, d in tot.items():
            base = d["pos"] / max(d["watched"], 1)
            ppv = d["true_alarms"] / max(d["alarms"], 1)
            ops[rule] = dict(watched=d["watched"], base_rate=base, alarms=d["alarms"], alarm_rate=d["alarms"] / max(d["watched"], 1),
                             ppv=ppv, lift=ppv / base if base else None, hits=d["hits"], onsets=d["onsets"],
                             N2_mean_hits=float(d["shift"].mean()),
                             N2_p=float((1 + (d["shift"] >= d["hits"]).sum()) / (1 + len(d["shift"]))))
        out[arm] = dict(operator=ops, precursors=prec, per_period=per)
        print(arm, json.dumps(ops, indent=1, default=float))
        print(arm, prec)
    out["W15"]["triggers_posthoc"] = trigger_check(R["W15"]["periods"])
    print("triggers (W15, post hoc):", json.dumps(out["W15"]["triggers_posthoc"], indent=1))
    (DATA / "assemble_round1.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
