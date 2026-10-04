"""H10 P5 (descriptive): kickoff event study across non-holdout, within-regime goal changes (NE34).

For each transition old -> new (both non-holdout, #23 excluded, same regime on the last old day, the first new day and
the old period's last <= 5 active days): along g_new,
  jump      Dm_k = mean over agents (>= 2 eligible windows on both days) of mu_i(first new day) - mu_i(last old day)
  pre-fluct v_k  = mean_i k2_i over the old period's last <= 5 active days (noise-deconvolved, >= 6 windows)
  push      lam_k = Dm_k / v_k (the effective field in units of the pre-period fluctuations)
Also the window-level time course of the swarm mean alignment from 2 days before to 3 days after each change.

Outputs data/processed/H10-goals-are-legendre-pushes/NE34/kickoffs.json and NE34/figures/kickoffs.pdf.
Usage: uv run python kickoffs.py
"""
from __future__ import annotations

import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

import h10data  # noqa: E402
from h10data import DATA, HERE, ROOT, UNTOUCHED, goal_direction, save_json, statements  # noqa: E402
from h10lib import agent_stats, aggregate, random_transverse  # noqa: E402
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import load_holdout  # noqa: E402

HYP = HERE.parent


def modes():
    t = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    out = {}
    for m in re.finditer(r"^\| (\d+) \| [^|]+\| [^|]+\| [^|]+\| [^|]+\| (I{1,3}) \| (\w) \| (\w) \|", t, re.M):
        out[int(m.group(1))] = m.group(4)
    return out


def unit_vectors(rows, Z, n=32):
    X = np.asarray(Z[np.sort(rows)][:, :n], dtype=np.float64)[np.argsort(np.argsort(rows))]
    return X / np.linalg.norm(X, axis=1, keepdims=True)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    # round 1b (2026-10-04): corrected inputs; defaults reproduce round 1
    ap.add_argument("--emb", default="bge_small", choices=["bge_small", "gte_modernbert"])
    ap.add_argument("--goals", default="h10", choices=["h10", "shared"])
    ap.add_argument("--dedupe", default="none", choices=["none", "copies", "restate"])
    ap.add_argument("--style", action="store_true")
    args = ap.parse_args()
    h10data.configure(args.emb, args.goals, args.dedupe, args.style)
    out_dir = h10data.out_root() / "NE34"
    st, Z = statements()
    st = st.filter(pl.col("win30").is_not_null())
    held = set(load_holdout()["goal_periods_held_out"]) | UNTOUCHED
    md = modes()
    goals = sorted(set(st["goal_no"].unique().to_list()) - held)
    rows_out, course = [], []
    for old, new in zip(goals[:-1], goals[1:]):
        if new != old + 1:
            continue
        so, sn = st.filter(pl.col("goal_no") == old), st.filter(pl.col("goal_no") == new)
        dold, dnew = sorted(so["pt_date"].unique().to_list()), sorted(sn["pt_date"].unique().to_list())
        if not dold or not dnew:
            continue
        pre_days = dold[-5:]
        regs = set(so.filter(pl.col("pt_date").is_in(pre_days))["regime"].unique().to_list()) | \
            set(sn.filter(pl.col("pt_date") == dnew[0])["regime"].unique().to_list())
        if len(regs) != 1:
            continue
        reg = regs.pop()
        g = goal_direction(new, reg)
        U = random_transverse(g, 1, np.random.default_rng(0))
        # pre-period fluctuations along g_new
        pre = so.filter(pl.col("pt_date").is_in(pre_days))
        dmap = {d: k for k, d in enumerate(pre_days)}
        X = unit_vectors(pre["row"].to_numpy(), Z)
        day = np.array([dmap[d] for d in pre["pt_date"].to_list()])
        seg = aggregate(X, pre["agent"].to_numpy(), day, day * 1000 + pre["win30"].to_numpy(), U)
        stp = agent_stats(seg)
        v = float(np.mean(stp.k2[:, 0])) if len(stp.agents) else np.nan
        # last old day vs first new day
        def day_means(s, d):
            q = s.filter(pl.col("pt_date") == d)
            Xd = unit_vectors(q["row"].to_numpy(), Z)
            y = Xd @ g
            ag, w = q["agent"].to_numpy(), q["win30"].to_numpy()
            out = {}
            for a in np.unique(ag):
                ws = [y[(ag == a) & (w == k)].mean() for k in np.unique(w[ag == a]) if ((ag == a) & (w == k)).sum() >= 2]
                if len(ws) >= 2:
                    out[int(a)] = float(np.mean(ws))
            return out
        mo, mn = day_means(so, dold[-1]), day_means(sn, dnew[0])
        common = sorted(set(mo) & set(mn))
        if len(common) < 3:
            continue
        dm = float(np.mean([mn[a] - mo[a] for a in common]))
        rows_out.append({"old": old, "new": new, "regime": reg, "mode_old": md.get(old), "mode_new": md.get(new),
                         "N": len(common), "Dm": dm, "v": v, "lam": dm / v if v and v > 0 else np.nan,
                         "sd_pre": float(np.sqrt(v)) if v and v > 0 else np.nan,
                         "eps": dm / np.sqrt(v) if v and v > 0 else np.nan, "last_old": dold[-1], "first_new": dnew[0]})
        # time course: swarm mean alignment per window, last 2 old days and first 3 new days
        tc = []
        for s, ds, sign in ((so, dold[-2:], -1), (sn, dnew[:3], 1)):
            for k, d in enumerate(ds):
                q = s.filter(pl.col("pt_date") == d)
                y = unit_vectors(q["row"].to_numpy(), Z) @ g
                w = q["win30"].to_numpy()
                for ww in np.unique(w):
                    tc.append(((k - len(ds)) if sign < 0 else k, int(ww), float(y[w == ww].mean())))
        course.append({"old": old, "new": new, "tc": tc})
        print(rows_out[-1], flush=True)
    df = pl.DataFrame(rows_out)
    res = {"transitions": rows_out}
    into_assigned = df.filter(pl.col("mode_new").is_in(["C", "I", "K", "M", "D"]))
    res["frac_positive_into_assigned"] = float((into_assigned["Dm"] > 0).mean()) if into_assigned.height else np.nan
    res["n_into_assigned"] = into_assigned.height
    for reg in ("I", "III"):
        d = df.filter((pl.col("regime") == reg) & pl.col("v").is_finite() & (pl.col("v") > 0))
        if d.height >= 4:
            rho, p = spearmanr(d["v"].to_numpy(), d["Dm"].to_numpy())
            res[f"spearman_{reg}"] = {"rho": float(rho), "p_two_sided": float(p), "n": d.height}
    print({k: v for k, v in res.items() if k != "transitions"})
    save_json({**res, "course": course}, out_dir / "kickoffs.json")
    if out_dir != DATA / "NE34":
        return

    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9))
    for reg, col in (("I", "#2a78d6"), ("II", "#eb6834"), ("III", "#1baf7a")):
        d = df.filter(pl.col("regime") == reg)
        if d.height:
            ax[0].scatter(d["v"], d["Dm"], color=col, label=f"regime {reg}", s=18)
            for r in d.iter_rows(named=True):
                ax[0].annotate(f"{r['old']}→{r['new']}", (r["v"], r["Dm"]), fontsize=5)
    ax[0].axhline(0, color="k", lw=0.5)
    ax[0].set_xlabel("pre-period fluctuation v̄ along ĝ_new (κ2)"); ax[0].set_ylabel("kickoff jump Δm (first new − last old day)")
    ax[0].legend(fontsize=6)
    # average time course (each transition centered on its last-old-day mean, scaled by its pre-period sd)
    acc = {}
    for c, r in zip(course, rows_out):
        if not np.isfinite(r["sd_pre"]):
            continue
        base = np.mean([t[2] for t in c["tc"] if t[0] == -1])
        for dd, ww, y in c["tc"]:
            acc.setdefault((dd, ww), []).append((y - base) / r["sd_pre"])
    keys = sorted(acc)
    xs = np.arange(len(keys))
    ax[1].plot(xs, [np.median(acc[k]) for k in keys], "-", color="k", lw=1)
    ax[1].fill_between(xs, [np.quantile(acc[k], 0.25) for k in keys], [np.quantile(acc[k], 0.75) for k in keys], color="0.8")
    b = [i for i, k in enumerate(keys) if k[0] == 0]
    if b:
        ax[1].axvline(b[0] - 0.5, color="#eb6834", lw=1)
    ax[1].set_xlabel("30-min windows (2 old days | 3 new days)"); ax[1].set_ylabel("alignment − last old day, in pre-period SDs")
    ax[1].set_title("median and IQR over transitions", fontsize=8)
    fig.tight_layout()
    (HYP / "goalperiod-subhypotheses" / "NE34" / "figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(HYP / "goalperiod-subhypotheses" / "NE34" / "figures" / "kickoffs.pdf")


if __name__ == "__main__":
    main()
