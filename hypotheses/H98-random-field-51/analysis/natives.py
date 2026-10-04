"""H98 natives (predictions in goalperiod-subhypotheses/NE32/README.md and G51/README.md, written before running).

NE32: newcomers 35 (forecaster), 36 (YouTuber), 37 (diplomat) in isolated rooms on 2026-07-09 vs their incumbent rivals
20, 18, 17. N1a: alignment of the isolated-interval state with the rival's 51a static field, as a percentile among
incumbents (exact enumeration null). N1b: change from the isolated state to the newcomer's 51c static field.
Manipulation: ledger items authored by the rival received inside the isolated interval.

G51 room split: movers 6, 29 (#focus 08-05 -> 08-21). Na: static-field change 51f -> 51g vs stayers. Nb: pull toward
the #general mean (agent_gain, surrogate-corrected), 51f vs 51g.

    uv run python hypotheses/H98-random-field-51/analysis/natives.py
Output: data/processed/H98-random-field-51/results/natives.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h98lib as L  # noqa: E402

SH = L.ROOT / "data/processed/shared"
ED = SH / "embeddings"
RES = L.DATA / "results"
NEW = {35: 20, 36: 18, 37: 17}
ISO_ROOMS = {35: 10, 36: 11, 37: 12}
MOVERS = (6, 29)
UTC = dt.timezone.utc
STMT = {"style_resid_period": "style_resid_period32", "white32": "white32"}


def static_fields(u, var, model):
    U = L.load_unit(u, var, model)
    ad = U["ad"]
    dz = L.disorder(U["S"], ad["agent"].to_numpy(), ad["day"].to_numpy())
    return {int(a): dz["phi"][k] for k, a in enumerate(dz["agents"])}, dz["mu"]


def ne32(var: str, model: str) -> dict:
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
    SV = np.load(ED / f"statements_{STMT[var]}_{model}.npy", mmap_mode="r")
    inc, mu = static_fields("51a", var, model)
    inc = {a: v for a, v in inc.items() if a not in NEW}
    new51c, _ = static_fields("51c", var, model)
    out = {"var": var, "model": model, "per_newcomer": []}
    pcts, d_align = [], []
    for nw, rv in NEW.items():
        iv = rt.filter((pl.col("agent") == nw) & (pl.col("room") == ISO_ROOMS[nw])).row(0, named=True)
        lo, hi = iv["t_start"], iv["t_end"]
        s = st.filter((pl.col("agent") == nw) & (pl.col("t") >= lo) & (pl.col("t") <= hi))
        assert not s["holdout"].any()
        rec = {"newcomer": nw, "rival": rv, "iso_min": (hi - lo).total_seconds() / 60, "n_stmts": s.height}
        if s.height < 3 or rv not in inc:
            rec["testable"] = False
            out["per_newcomer"].append(rec)
            continue
        x = L.unit(np.asarray(SV[s["srow"].to_numpy()], np.float32)).mean(0)
        xc = L.unit(x - mu)
        al = {a: float(xc @ L.unit(v - mu)) for a, v in inc.items()}
        others = [al[a] for a in al if a != rv]
        pct = float(np.mean(np.asarray(others) < al[rv]))
        rec.update({"testable": True, "align_rival": al[rv], "align_others_mean": float(np.mean(others)),
                    "pct": pct, "rank": int(1 + sum(o > al[rv] for o in others)), "n_inc": len(al)})
        pcts.append(pct)
        if nw in new51c:
            y = L.unit(new51c[nw] - mu)
            a51c = float(y @ L.unit(inc[rv] - mu))
            rec["align_51c"] = a51c
            d_align.append(a51c - al[rv])
        out["per_newcomer"].append(rec)
    if pcts:
        # exact null: each newcomer's rival rank uniform over the incumbents (independent)
        n_inc = len(inc) - 1
        grid = np.arange(n_inc + 1) / n_inc
        obs = np.mean(pcts)
        cnt = tot = 0
        for combo in itertools.product(grid, repeat=len(pcts)):
            tot += 1
            cnt += np.mean(combo) >= obs - 1e-12
        out.update({"N1a_mean_pct": float(obs), "N1a_p": cnt / tot, "N1a_k": len(pcts)})
    if d_align:
        out.update({"N1b_mean_change": float(np.mean(d_align)), "N1b_k": len(d_align)})
    return out


def ne32_manipulation() -> list:
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")
    cw = pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date") == "2026-07-09").select(
        "turn_id", "agent", "t_call").collect()
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "sender", "kind").collect()
    out = []
    for nw, rv in NEW.items():
        iv = rt.filter((pl.col("agent") == nw) & (pl.col("room") == ISO_ROOMS[nw])).row(0, named=True)
        calls = cw.filter((pl.col("agent") == nw) & (pl.col("t_call") >= iv["t_start"]) & (pl.col("t_call") <= iv["t_end"]))
        items = it.join(calls.select("turn_id"), on="turn_id", how="semi")
        out.append({"newcomer": nw, "rival": rv, "n_calls": calls.height, "items_total": items.height,
                    "items_from_rival": int((items["sender"] == rv).sum()),
                    "items_from_agents": int((items["kind"].cast(pl.String) == "agent").sum())})
    return out


def focus(var: str, model: str) -> dict:
    f_before, mu_b = static_fields("51f", var, model)
    f_after, mu_a = static_fields("51g", var, model)
    common = sorted(set(f_before) & set(f_after))
    dphi = {a: float(np.linalg.norm((f_after[a] - mu_a) - (f_before[a] - mu_b))) for a in common}
    stay = [dphi[a] for a in common if a not in MOVERS]
    q90 = float(np.percentile(stay, 90))
    out = {"var": var, "model": model, "stayers_q90": q90, "stayers_median": float(np.median(stay)),
           "movers": {int(a): {"dphi": dphi.get(a), "pct": float(np.mean(np.asarray(stay) < dphi[a])) if a in dphi else None}
                      for a in MOVERS}}
    out["Na_pass"] = all(dphi.get(a, np.inf) < q90 for a in MOVERS)
    db = {}
    for u in ("51f", "51g"):
        U = L.load_unit(u, var, model)
        wn = U["wn"]
        args = (U["X"], wn["agent"].to_numpy(), wn["day"].to_numpy(), wn["win30"].to_numpy(), wn["room"].to_numpy())
        for a in common:
            g = L.agent_gain(*args, target=a, ref_room=0)
            db.setdefault(a, {})[u] = g["b_ex"]
    delta = {a: db[a]["51g"] - db[a]["51f"] for a in db if np.isfinite(db[a].get("51g", np.nan)) and np.isfinite(db[a].get("51f", np.nan))}
    st_d = [delta[a] for a in delta if a not in MOVERS]
    out.update({"Nb_movers": {int(a): {"b_before": db[a]["51f"], "b_after": db[a]["51g"], "delta": delta.get(a)} for a in MOVERS if a in db},
                "Nb_stayers_median_delta": float(np.median(st_d)), "Nb_stayers_iqr": [float(np.percentile(st_d, 25)), float(np.percentile(st_d, 75))],
                "Nb_movers_pct": {int(a): float(np.mean(np.asarray(st_d) < delta[a])) for a in MOVERS if a in delta}})
    out["Nb_pass"] = all(delta.get(a, 1) < 0 for a in MOVERS) and abs(out["Nb_stayers_median_delta"]) <= 0.05
    return out


JOINERS = (41, 42, 43, 44, 45)
ROLE_START = {41: "2026-08-31", 42: "2026-09-01", 43: "2026-09-04", 44: "2026-09-04", 45: "2026-09-04"}  # DQ6 t_valid_from (PT)


def ne33(var: str, model: str) -> dict:
    """Own-role percentile of each late joiner on its first day (>= 3 statements) vs incumbents on the same days."""
    rv_all = L.role_table(model)
    rows = []
    first_day = {}
    for u in ("51i", "51j", "51k", "51l"):
        U = L.load_unit(u, var, model)
        ad = U["ad"]
        ro = U.get("roles")
        rmap = {a: r for a, r in zip(ro["agent"].to_list(), ro["role"].to_list())} if ro is not None else {}
        for d in sorted(ad["pt_date"].unique().to_list()):
            sel = ad.with_row_index("k").filter(pl.col("pt_date") == d)
            S = U["S"][sel["k"].to_numpy()]
            m = S.mean(0)
            ags = sel["agent"].to_list()
            have = [a for a in ags if a in rmap and (a, rmap[a]) in rv_all]
            if len(have) < 5:
                continue
            V = np.stack([rv_all[(a, rmap[a])] for a in have])
            Vc = L.unit(V - V.mean(0))
            for a in have:
                x = L.unit(S[ags.index(a)] - m)
                al = Vc @ x
                own = al[have.index(a)]
                pct = float(np.mean(np.delete(al, have.index(a)) < own))
                if a in ROLE_START and d < ROLE_START[a]:
                    continue  # role not yet assigned on this day (DQ6)
                is_join = a in JOINERS and a not in first_day
                if is_join:
                    first_day[a] = d
                rows.append({"unit": u, "pt_date": d, "agent": a, "pct": pct, "joiner_first_day": is_join,
                             "n_roles": len(have)})
    df = pl.DataFrame(rows)
    J = df.filter(pl.col("joiner_first_day"))
    days = J["pt_date"].unique().to_list()
    I = df.filter(~pl.col("agent").is_in(list(JOINERS)) & pl.col("pt_date").is_in(days))
    out = {"var": var, "model": model, "joiners": J.select("agent", "pt_date", "pct", "n_roles").to_dicts(),
           "joiners_mean_pct": float(J["pct"].mean()) if J.height else None,
           "incumbents_mean_pct": float(I["pct"].mean()) if I.height else None, "n_incumbent_days": I.height}
    if J.height:
        # exact null: each joiner's rank uniform over its n_roles - 1 competitors
        grids = [np.arange(n) / (n - 1) for n in J["n_roles"].to_list()]
        obs = J["pct"].mean()
        tot = cnt = 0
        for combo in itertools.product(*grids):
            tot += 1
            cnt += np.mean(combo) >= obs - 1e-12
        out["N3a_p"] = cnt / tot
    return out


def main():
    RES.mkdir(parents=True, exist_ok=True)
    res = {"NE32": [ne32(v, m) for v in L.VARS for m in L.MODELS], "NE32_manipulation": ne32_manipulation(),
           "focus": [focus(v, m) for v in L.VARS for m in L.MODELS],
           "NE33": [ne33(v, m) for v in L.VARS for m in L.MODELS]}
    (RES / "natives.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
