"""H16 round 2 synthetic validation on the real skeletons (axis F). Run before any round-2 outcome statistic.

Gate worlds (G51, G38 gate rows; outcomes simulated sequentially within traps: stop at the first escape, censor at the
real trap end):
  W0 null            logit = alpha_i
  W1 intrinsic       alpha_i - 0.5 ln a
  W2 urn             P = c (1 - f_call)          (the strongest urn ruler; f missing -> 0)
  W3 frailty         alpha_i + z_trap, z ~ N(0, 1.5^2), no conditional aging
  W4 reset step      W1 + 0.7 at a forced reset (no dose)
  W5 address kick    W1 + 0.7 for a directed read at the gate (undirected 0)
  W6 urn kick        W1 + 1.0 x dk_entry (dilution scaling, coefficient 1)
TS1r worlds (deep skeleton, per-row draws): WM pure mixture (cell hazard per agent x kind_start x last_kind, no aging);
  WA within-cell aging (-0.5 per ln elapsed).
R3 worlds (real agent x period depth cells): u_agent SD 0.5 or 0, period-cell noise SD 0.3, sampling noise 1/sqrt(n).
Output: data/processed/H16-metastable-traps-kramers/r2/synthetic/*.json
Usage: uv run python hypotheses/H16-metastable-traps-kramers/analysis/synthetic_r2.py [--part gates|ts1r|r3] [--reps N]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OUT = R.R2 / "synthetic"


def world_p(name, g, rng):
    ag = g["agent"].to_numpy()
    ua = np.unique(ag)
    alpha = dict(zip(ua, 0.0 + 0.5 * rng.standard_normal(len(ua))))
    a = np.array([alpha[x] for x in ag])
    la = np.log(np.maximum(g["a_sus"].to_numpy(), 10.0) / 60.0)
    la = la - np.median(la)
    if name == "W0":
        eta = a
    elif name in ("W1", "W4", "W5", "W6"):
        eta = a - 0.5 * la
        if name == "W4":
            eta = eta + 0.7 * g["forced"].to_numpy()
        if name == "W5":
            eta = eta + 0.7 * g["dir1"].to_numpy()
        if name == "W6":
            eta = eta + 1.0 * g["dk_entry"].to_numpy()
    elif name == "W3":
        tr = g.select((pl.col("agent").cast(pl.Utf8) + pl.col("pt_date") + pl.col("trap").cast(pl.Utf8)).alias("k"))["k"].to_numpy()
        _, code = np.unique(tr, return_inverse=True)
        z = 1.5 * rng.standard_normal(code.max() + 1)
        eta = a + z[code]
    elif name == "W2":
        f = np.nan_to_num(g["f_call"].to_numpy().astype(float), nan=0.0)
        return R.urn_prob(f, ag, 0.5)
    return R.expit(eta)


def run_gates(reps):
    rng = np.random.default_rng(R.SEED + 1)
    res = {}
    for goal, nrep in ((51, reps), (38, reps * 2)):
        g = R.prep_gates(pl.read_parquet(R.R2 / "gates_r2.parquet").filter(pl.col("goal_no") == goal))
        st, en = R.trap_index(g)
        res[f"G{goal}"] = {}
        for w in ("W0", "W1", "W2", "W3", "W4", "W5", "W6"):
            rows = []
            t0 = time.time()
            for _ in range(nrep):
                p = world_p(w, g, rng)
                keep, y = R.simulate_traps(rng, p, st, en)
                gs = g.filter(pl.Series(keep))
                try:
                    o = R.flat(R.gate_models(gs, y[keep], urn_cols=("f_tok", "f_call")))
                except Exception as e:  # noqa: BLE001
                    print("fail", w, e, flush=True)
                    continue
                rows.append(o)
            res[f"G{goal}"][w] = summarize(rows)
            print(f"G{goal} {w} {nrep} reps {time.time() - t0:.0f}s", {k: res[f'G{goal}'][w][k] for k in KEYS if k in res[f'G{goal}'][w]}, flush=True)
            R.jdump(res, OUT / "gates.json")
    return res


KEYS = ["beta_a0", "abs_f_call.beta_f", "abs_f_call.rho", "abs_f_tok.beta_f", "reset.forced", "reset.dose_du_call",
        "kick.dir", "kick.undir", "kick.diff", "kick.coef_dk_entry", "kick.coef_dk_tok"]


def summarize(rows):
    out = {}
    if not rows:
        return out
    for k in rows[0]:
        v = np.array([r[k][0] for r in rows], float)
        se = np.array([r[k][1] for r in rows], float)
        z = v / se
        out[k] = {"mean": float(np.nanmean(v)), "sd": float(np.nanstd(v)), "rej_pos": float(np.nanmean(z > 1.96)) if np.isfinite(z).any() else None,
                  "rej_neg": float(np.nanmean(z < -1.96)) if np.isfinite(z).any() else None, "n": int(np.isfinite(v).sum())}
    return out


def run_ts1r(reps, null_sims):
    rng = np.random.default_rng(R.SEED + 2)
    res = {}
    for per, nrep in (("G51", reps), ("G38", reps * 2)):
        H = R.ts1r_deep(per)
        cells = R.cell_codes(H)
        pause = H["kind_start"] == "pause"
        kcode = R.cell_codes(H, cols=("kind_start",))
        res[per] = {"rows": int(len(H["lnel"])), "cells": int(cells.max() + 1)}
        for w in ("WM", "WA"):
            rec = {"pooled": [], "within_kind": [], "pause": [], "pause_se": [], "null_p": []}
            for _ in range(nrep):
                al = np.log(0.02) + rng.standard_normal(cells.max() + 1)
                eta = al[cells] + (-0.5 * (H["lnel"] - np.log(10.0)) if w == "WA" else 0.0)
                h = -np.expm1(-np.exp(np.clip(eta, -30, 3)))
                y = (rng.random(len(h)) < h).astype(np.int8)
                rec["pooled"].append(R.slope_cloglog(y, H["lnel"], H["agent"])[0])
                rec["within_kind"].append(R.slope_cloglog(y, H["lnel"], kcode)[0])
                b, s = R.slope_cloglog(y[pause], H["lnel"][pause], H["agent"][pause])
                rec["pause"].append(b); rec["pause_se"].append(s)
                nul = R.mixture_null(rng, H, y, cells, sims=null_sims)
                rec["null_p"].append(float(np.mean(nul <= rec["pooled"][-1])))
            b = np.array(rec["pause"]); s = np.array(rec["pause_se"])
            res[per][w] = {"pooled_mean": float(np.nanmean(rec["pooled"])), "within_kind_mean": float(np.nanmean(rec["within_kind"])),
                           "pause_mean": float(np.nanmean(b)), "MP1_rej": float(np.nanmean((b < -0.3) & (b + 1.96 * s < 0))),
                           "MP2_rej": float(np.mean(np.array(rec["null_p"]) < 0.025)), "reps": nrep}
            print(per, w, res[per][w], flush=True)
            R.jdump(res, OUT / "ts1r.json")
    return res


def depth_cells():
    """Real agent x period deep-window cells: escapes and exposure (only counts are used here)."""
    rows = []
    for per in ("G27", "G30", "G31", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"):
        H = R.ts1r_deep(per)
        d = pl.DataFrame({"agent": H["agent"], "y": H["y"]}).group_by("agent").agg(pl.col("y").sum().alias("ev"), pl.len().alias("bins"))
        rows.append(d.with_columns(pl.lit(per).alias("period")))
    d = pl.concat(rows)
    return d.filter(pl.col("ev") >= 5).with_columns(D=-(pl.col("ev") / (pl.col("bins") * 0.5)).log(), v=1.0 / pl.col("ev"))


def r3_stats(d: pl.DataFrame, rng, B=200, n_perm=200, label="agent"):
    """Invariance (leave-period-out correlation, agent bootstrap) and the agent variance share (permutation)."""
    d = d.with_columns(Dc=pl.col("D") - pl.col("D").mean().over("period"))
    multi = d.group_by("agent").agg(pl.col("period").n_unique().alias("np")).filter(pl.col("np") >= 2)["agent"]
    dm = d.filter(pl.col("agent").is_in(multi))

    def lpo_r(df):
        s = df.group_by("agent").agg(pl.col("Dc").sum().alias("S"), pl.len().alias("n"))
        x = df.join(s, on="agent").with_columns(other=(pl.col("S") - pl.col("Dc")) / (pl.col("n") - 1))
        a, b = x["Dc"].to_numpy(), x["other"].to_numpy()
        return float(np.corrcoef(a, b)[0, 1]) if len(a) > 3 else float("nan")
    r = lpo_r(dm)
    ags = dm["agent"].unique().to_numpy()
    bs = []
    for _ in range(B):
        pick = rng.choice(ags, len(ags))
        parts = [dm.filter(pl.col("agent") == a).with_columns(pl.lit(i).alias("agent")) for i, a in enumerate(pick)]
        bs.append(lpo_r(pl.concat(parts)))
    share = var_share(d, label)
    perm = []
    for _ in range(n_perm):
        lab = d[label].to_numpy().copy()
        for per in d["period"].unique().to_list():
            m = (d["period"] == per).to_numpy()
            lab[m] = rng.permutation(lab[m])
        perm.append(var_share(d.with_columns(pl.Series(label, lab)), label))
    return {"r_lpo": r, "r_ci": R.pct_ci(bs), "share": share, "perm_p": float(np.mean(np.array(perm) >= share)),
            "n_cells": d.height, "n_multi_agents": int(len(ags))}


def var_share(d, label):
    """Method-of-moments share of the non-sampling variance of period-centred depth that sits between `label` groups:
    tau2 = Var(group means) - mean(within-group variance / n_group), over groups with >= 2 cells; total = Var(Dc) - mean(v)."""
    x = d.with_columns(Dc=pl.col("D") - pl.col("D").mean().over("period"))
    tot = float(x["Dc"].var()) - float(x["v"].mean())
    m = x.group_by(label).agg(pl.col("Dc").mean().alias("mu"), pl.col("Dc").var().alias("s2"), pl.len().alias("n")).filter(pl.col("n") >= 2)
    if m.height < 3 or tot <= 0:
        return float("nan")
    tau2 = float(m["mu"].var()) - float((m["s2"] / m["n"]).mean())
    return float(np.clip(tau2 / tot, -1, 1))


def run_r3(reps):
    rng = np.random.default_rng(R.SEED + 3)
    d = depth_cells()
    ags = d["agent"].unique().to_numpy()
    res = {"n_cells": d.height}
    for sd in (0.0, 0.5):
        rec = []
        for _ in range(reps):
            u = dict(zip(ags, sd * rng.standard_normal(len(ags))))
            Dsim = np.array([u[a] for a in d["agent"].to_numpy()]) + 0.3 * rng.standard_normal(d.height) + rng.standard_normal(d.height) * np.sqrt(d["v"].to_numpy())
            ds = d.with_columns(pl.Series("D", Dsim))
            st = r3_stats(ds, rng, B=60, n_perm=60)
            rec.append(st)
        res[f"sd_{sd}"] = {"inv_rej": float(np.mean([s["r_ci"][0] > 0 for s in rec])), "share_mean": float(np.nanmean([s["share"] for s in rec])),
                           "perm_rej": float(np.mean([s["perm_p"] < 0.05 for s in rec])), "r_mean": float(np.nanmean([s["r_lpo"] for s in rec])), "reps": reps}
        print("R3", sd, res[f"sd_{sd}"], flush=True)
    R.jdump(res, OUT / "r3.json")
    return res


def main():
    part = sys.argv[sys.argv.index("--part") + 1] if "--part" in sys.argv else "all"
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 30
    OUT.mkdir(parents=True, exist_ok=True)
    if part in ("gates", "all"):
        run_gates(reps)
    if part in ("ts1r", "all"):
        run_ts1r(max(reps // 3, 8), null_sims=40)
    if part in ("r3", "all"):
        run_r3(max(reps, 40))


if __name__ == "__main__":
    main()
