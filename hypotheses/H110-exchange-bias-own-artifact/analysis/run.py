"""H110 round-1 real-data run (non-holdout). Writes data/processed/H110-exchange-bias-own-artifact/results/results.json.

Per model: old-state remanence m and own-state remanence o per agent x transition x window; group persistence and
decay ratio (pooled, switcher fixed effects; pinned_own primary, pinned_any variant; day 1 primary, day 2 variant);
offset end (O3); transition-level Spearman (O5); natives G40 (continuing vs stopping) and G39 (own-room memory by
continued #38-repo commits). bge white32 variant.
Usage: uv run python hypotheses/H110-exchange-bias-own-artifact/analysis/run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h110lib as L  # noqa: E402

OUT = L.D / "results"


def transition_R1(rem: pl.DataFrame) -> dict:
    w = rem.pivot(index=["P", "agent"], on="window", values="m")
    out = {}
    for (P,), s in w.group_by(["P"]):
        s = s.filter(pl.col("pre").is_not_null() & pl.col("d1").is_not_null())
        if s.height >= 3:
            out[int(P)] = float(s["d1"].sum() / s["pre"].sum())
    return out


def g40_native(rem, pin, nboot=2000, seed=0):
    p = pin.filter((pl.col("P") == 40) & pl.col("pinned_own"))
    cont = [r["agent"] for r in p.iter_rows(named=True) if sum(c > 0 for c in r["post_commits"][:3]) >= 2]
    stop = [r["agent"] for r in p.iter_rows(named=True) if sum(r["post_commits"][:3]) == 0]
    r = rem.filter((pl.col("P") == 40) & pl.col("window").is_in(["d1", "d2", "d3"])).group_by("agent").agg(pl.col("m").mean())
    mc = r.filter(pl.col("agent").is_in(cont))["m"].to_numpy()
    ms = r.filter(pl.col("agent").is_in(stop))["m"].to_numpy()
    out = {"n_cont": int(len(mc)), "n_stop": int(len(ms)), "agents_cont": cont, "agents_stop": stop}
    if len(mc) >= 2 and len(ms) >= 2:
        rng = np.random.default_rng(seed)
        bs = [rng.choice(mc, len(mc)).mean() - rng.choice(ms, len(ms)).mean() for _ in range(nboot)]
        out.update({"m_cont": float(mc.mean()), "m_stop": float(ms.mean()), "diff": float(mc.mean() - ms.mean()),
                    "diff_ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]})
    return out


def g39_native(tr, win, X, proj, pin, nboot=2000, seed=0):
    """Own-room old-state memory for #38 veterans (H96's G39 construction), by continued commits to a #38 repo."""
    st = pl.read_parquet(L.ED / "statements.parquet", columns=["room"]).with_row_index("srow")
    w = win.with_row_index("wr").join(st, on="srow", how="left").filter(pl.col("P") == 39)
    old = w.filter((pl.col("window") == "old") & pl.col("room").is_in([2, 3]))
    home = old.group_by("agent").agg(pl.col("room").mode().first().alias("home"), pl.len())
    home = dict(zip(home["agent"].to_list(), home["home"].to_list()))
    Pp = proj[39]["Pperp"]
    adv = {}
    for (a, d), s in old.group_by(["agent", "pt_date"]):
        if s.height >= L.MIN_AD:
            adv.setdefault(int(a), []).append(L.unit(X[s["wr"].to_numpy()].mean(0)))
    rows = []
    for a in home:
        own = [v for b, vs in adv.items() if b != a and home.get(b) == home[a] for v in vs]
        oth = [v for b, vs in adv.items() if b != a and home.get(b) not in (None, home[a]) for v in vs]
        if not own or not oth:
            continue
        eo, ex = L.unit(Pp @ L.unit(np.mean(own, 0))), L.unit(Pp @ L.unit(np.mean(oth, 0)))
        rec = {"agent": int(a), "home": int(home[a])}
        for wn in ("pre", "d1"):
            s = w.filter((pl.col("agent") == a) & (pl.col("window") == wn))
            if s.height >= (L.MIN_PRE if wn == "pre" else L.MIN_POST):
                v = L.unit(X[s["wr"].to_numpy()].mean(0))
                rec[wn] = float(v @ eo - v @ ex)
        rows.append(rec)
    pp = pin.filter(pl.col("P") == 39)
    kept = {r["agent"]: sum(r["post_commits_any"][:3]) > 0 for r in pp.iter_rows(named=True)}
    t = [r for r in rows if "pre" in r and "d1" in r]
    k = np.array([r["d1"] for r in t if kept.get(r["agent"], False)])
    n = np.array([r["d1"] for r in t if not kept.get(r["agent"], False)])
    out = {"rows": rows, "kept": {str(a): v for a, v in kept.items()}, "n_kept": int(len(k)), "n_not": int(len(n))}
    if len(k) >= 2 and len(n) >= 2:
        rng = np.random.default_rng(seed)
        bs = [rng.choice(k, len(k)).mean() - rng.choice(n, len(n)).mean() for _ in range(nboot)]
        out.update({"d1_kept": float(k.mean()), "d1_not": float(n.mean()), "diff": float(k.mean() - n.mean()),
                    "diff_ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]})
    return out


def block(tr, win, X, proj, pin):
    rem = L.remanence(tr, win, X, proj)
    o = {"n_rows": rem.height}
    for pc in ("pinned_own", "pinned_any"):
        pan = L.panel(rem, pin, "m", pc)
        o[pc] = {"pooled": L.persistence(pan), "switch": L.persistence(pan, switchers=True),
                 "pooled_d2": L.persistence(pan, post="d2"), "offset": L.offset_end(pan)}
    pan_o = L.panel(rem, pin, "o", "pinned_own")
    o["own_state"] = {"pooled": L.persistence(pan_o), "switch": L.persistence(pan_o, switchers=True)}
    R1 = transition_R1(rem)
    share = {int(P): float(s["pinned_own"].mean()) for (P,), s in pin.group_by(["P"])}
    Ps = sorted(set(R1) & set(share))
    o["transition"] = {"R1": R1, "pinned_share": share,
                       "spearman": L.spearman([share[P] for P in Ps], [R1[P] for P in Ps]), "n": len(Ps)}
    o["g40"] = g40_native(rem, pin)
    o["g39"] = g39_native(tr, win, X, proj, pin)
    # activity audit: statements per window by group
    act = rem.join(pin.select("P", "agent", "pinned_own").with_columns(pl.col("P").cast(rem["P"].dtype)), on=["P", "agent"])
    o["activity"] = act.group_by("pinned_own", "window").agg(pl.col("n").median().alias("n_med"), pl.len()).sort("window").to_dicts()
    return o, rem


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tr, win, pin = L.load_tables()
    res = {}
    for model in L.MODELS:
        X = L.load_X(win["srow"].to_numpy(), model)
        proj = L.field_projectors(tr, model)
        res[model], rem = block(tr, win, X, proj, pin)
        rem.write_parquet(OUT / f"remanence_{model}.parquet")
        if model == "bge_small":
            Xw = L.load_X(win["srow"].to_numpy(), model, "white32")
            res["bge_white32"], _ = block(tr, win, Xw, proj, pin)
        print(model, "done", flush=True)
    (OUT / "results.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)))
    for m in ("bge_small", "gte_modernbert", "bge_white32"):
        r = res[m]["pinned_own"]
        for v in ("pooled", "switch", "pooled_d2"):
            x = r[v]
            print(m, v, {k: x.get(k) for k in ("transitions", "nP", "nU", "R1_P", "R1_P_ci", "R1_U", "R1_U_ci", "ratio", "ratio_ci", "preP_ci", "preU_ci")})
        print(m, "offset", r["offset"])
        print(m, "any", {k: r and res[m]["pinned_any"]["pooled"].get(k) for k in ("transitions", "nP", "nU", "R1_P", "R1_U", "ratio", "ratio_ci")})
        print(m, "own", {k: res[m]["own_state"]["pooled"].get(k) for k in ("nP", "nU", "R1_P", "R1_U", "ratio", "ratio_ci")})
        print(m, "transition", res[m]["transition"])
        print(m, "g40", {k: v for k, v in res[m]["g40"].items()}, "\n g39", {k: v for k, v in res[m]["g39"].items() if k != "rows"})
        print(m, "per-transition", res[m]["pinned_own"]["pooled"]["per_transition"])


if __name__ == "__main__":
    main()
