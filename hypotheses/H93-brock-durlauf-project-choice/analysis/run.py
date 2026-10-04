"""H93 round-1 analysis, one goal period at a time (non-holdout data built by scheme/build.py).

  uv run python hypotheses/H93-brock-durlauf-project-choice/analysis/run.py --period 31 [--period ...] [--draws 200]

Per channel (work, attention): conditional-logit fits M0, M1, M2, M4 (primary since A1), M3a, R3, impostor splits
(room, lab, seen), blind arrivals dropped, kickoff-free placebo; per testable unit + DerSimonian-Laird pool (exception
(d)), else one period fit with unit-specific NEW constants. Brock-Durlauf fixed points and P_multi at the M4 fit; order
parameter m and the fixed point m* reached from the uniform start. Writes results/G<NN>.json.
Native layers: --rooms (per-room fits and simulations: G37), --arms (per-room arms: G44), --units (per-unit equilibria:
G51).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h93lib as L  # noqa: E402
from common import holdout_mask  # noqa: E402

DATA = ROOT / "data/processed/H93-brock-durlauf-project-choice"
MODELS = ["M0", "M1", "M2", "M4", "M3a", "R3", "SPLIT_room", "SPLIT_lab", "SPLIT_seen", "SPLIT_read"]
PRIMARY = "M4"


def load(g: int, ch: str):
    p = DATA / f"G{g:02d}" / f"long_{ch}.parquet"
    if not p.exists():
        return None, None, None
    lt = pl.read_parquet(p)
    ev = pl.read_parquet(DATA / f"G{g:02d}" / f"events_{ch}.parquet")
    occ = pl.read_parquet(DATA / f"G{g:02d}" / f"occupancy_{ch}.parquet")
    # holdout guard (the scheme already dropped held-out days)
    assert not any(holdout_mask(ev["pt_date"].to_list(), [g] * ev.height)), "held-out rows in exploratory input"
    return L.add_features(lt), ev, occ


def strip(res):
    return {k: v for k, v in res.items() if not k.startswith("_")}


def nonamed(lt: pl.DataFrame) -> pl.DataFrame:
    """Kickoff-free placebo: drop named options; drop events whose chosen option was named or with < 2 options left."""
    x = lt.filter(~pl.col("named"))
    ok = x.group_by("eid").agg(pl.col("chosen").any().alias("c"), pl.len().alias("k")).filter(pl.col("c") & (pl.col("k") >= 2))
    return x.filter(pl.col("eid").is_in(ok["eid"].implode()))


def fit_scope(lt: pl.DataFrame, model: str, units_ok: list[str], **kw):
    """Per testable unit + DL pool when the period has several units and >= 1 is testable; else one period fit."""
    units = sorted(lt["unit"].unique().to_list())
    if len(units) > 1 and units_ok:
        fs = {u: L.fit(lt.filter(pl.col("unit") == u), model, **kw) for u in units_ok}
        out = {"scope": "units", "units": {u: strip(f) for u, f in fs.items()}}
        if model.startswith("SPLIT"):
            for k in range(2):
                nm = L.MODELS[model][k]
                e = [L.coef(f, nm) for f in fs.values()]
                out[f"pool_{nm}"] = L.dl_pool([x for x, _ in e], [s for _, s in e])
        else:
            nm = L.SHARE.get(model, "s")
            e = [L.coef(f, nm) for f in fs.values()]
            out["pool"] = L.dl_pool([x for x, _ in e], [s for _, s in e])
        out["_fits"] = fs
        return out
    f = L.fit(lt, model, **kw)
    out = {"scope": "period", "fit": strip(f), "_fits": {"period": f}}
    if model.startswith("SPLIT"):
        for k in range(2):
            nm = L.MODELS[model][k]
            x, s = L.coef(f, nm)
            out[f"pool_{nm}"] = None if x is None else {"est": x, "se": s, "lo": x - 1.96 * s, "hi": x + 1.96 * s, "k": 1}
    else:
        x, s = L.coef(f, L.SHARE.get(model, "s"))
        out["pool"] = None if x is None else {"est": x, "se": s, "lo": x - 1.96 * s, "hi": x + 1.96 * s, "tau2": 0.0, "k": 1}
    return out


def channel(g: int, ch: str, draws: int, lt=None, ev=None, occ=None, tag="") -> dict | None:
    if lt is None:
        lt, ev, occ = load(g, ch)
    if lt is None or lt.height == 0:
        return None
    units = sorted(lt["unit"].unique().to_list())
    units_ok = [u for u in units if L.testable(lt.filter(pl.col("unit") == u))]
    res = {"channel": ch, "events": int(lt["eid"].n_unique()), "units": units, "units_testable": units_ok,
           "testable": L.testable(lt) if not units_ok else True,
           "new_frac": float(ev["is_new"].mean()), "named_chosen_frac": float(ev["named_chosen"].mean()),
           "prev_chosen_frac": float(ev["prev_chosen"].mean()), "n_named_opts": int(lt.filter(pl.col("named"))["opt"].n_unique())}
    fits = {}
    for m in MODELS:
        try:
            fits[m] = fit_scope(lt, m, units_ok)
        except Exception as e:  # noqa: BLE001
            fits[m] = {"error": str(e)}
    if "blind" in lt.columns and lt["blind"].fill_null(False).any():
        fits["M4_noblind"] = fit_scope(lt, "M4", units_ok, drop_blind=True)
    nn = nonamed(lt)
    if nn.height:
        uok = [u for u in units_ok if L.testable(nn.filter(pl.col("unit") == u), 20, 5)]
        try:
            fits["M4_nonamed"] = fit_scope(nn, "M4_nonamed", uok)
        except Exception as e:  # noqa: BLE001
            fits["M4_nonamed"] = {"error": str(e)}
    # R3 vs M4: log-likelihood per event (same parameter count)
    def ll(m):
        return sum(f["ll"] for f in fits[m]["_fits"].values()), sum(f["n_events"] for f in fits[m]["_fits"].values())
    if "_fits" in fits["M4"] and "_fits" in fits["R3"]:
        l4, n4 = ll("M4")
        l3, _ = ll("R3")
        res["dLL_M4_minus_R3_per_event"] = (l4 - l3) / max(n4, 1)
    # Brock-Durlauf equilibria at the M4 fit
    eq = {}
    for key, f in fits["M4"].get("_fits", {}).items():
        sub = lt if key == "period" else lt.filter(pl.col("unit") == key)
        try:
            pm = L.p_multi(sub, f, None if key == "period" else key, draws=draws)
            H, an, opts, agents = L.bd_fields(sub, f, None if key == "period" else key)
            fps = L.bd_fixed_points(H, an, f.get("gamma", 0.0), n_random=0, corners=0)
            pm["m_star_uniform"] = fps[0][1] if fps else None
            eq[key] = pm
        except Exception as e:  # noqa: BLE001
            eq[key] = {"error": str(e)}
    res["equilibria"] = eq
    # order parameter
    o = occ.filter(pl.col("nhost") >= 3).with_columns((pl.col("top") / pl.col("nhost")).alias("m"))
    res["m"] = float(o["m"].mean()) if o.height else None
    res["m_units"] = {str(u): float(gg["m"].mean()) for (u,), gg in o.group_by(["unit"])} if o.height else {}
    res["fits"] = {m: {k: v for k, v in f.items() if k != "_fits"} for m, f in fits.items()}
    pr = fits[PRIMARY].get("pool")
    res["primary"] = pr
    return res


def rooms_layer(g: int, draws: int) -> dict:
    """Per-room fits (chooser's room at the choice); options restricted to the period's options (both rooms)."""
    out = {}
    for ch in ("work", "attention"):
        lt, ev, occ = load(g, ch)
        if lt is None:
            continue
        rt = pl.read_parquet(ROOT / "data/processed/shared/rooms_timeline.parquet")
        sys.path.insert(0, str(HERE.parent / "scheme"))
        import h93scheme as S  # noqa: E402
        room_of = S.rooms_lookup(rt)
        ev = ev.with_columns(pl.Series("room", [room_of(a, t) for a, t in ev.select("agent", "t").iter_rows()], dtype=pl.Int16))
        res = {}
        for (rm,), e2 in ev.group_by(["room"]):
            if rm is None:
                continue
            ids = e2["eid"]
            sub = lt.filter(pl.col("eid").is_in(ids.implode()))
            r = {"events": e2.height, "new_frac": float(e2["is_new"].mean()),
                 "m_events": float((e2.filter(pl.col("nact") >= 3)["top"] / e2.filter(pl.col("nact") >= 3)["nact"]).mean())
                 if e2.filter(pl.col("nact") >= 3).height else None}
            # one fit over the room's events (unit-specific NEW); periods with one unit only
            try:
                f = L.fit(sub, "M4")
                r["M4"] = strip(f)
                pm = L.p_multi(sub, f, None, draws=draws)
                r["p_multi"] = pm
                f2 = L.fit(sub, "M2")
                r["M2"] = strip(f2)
            except Exception as e:  # noqa: BLE001
                r["error"] = str(e)
            res[str(rm)] = r
        out[ch] = res
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append", required=True)
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--rooms", action="store_true")
    a = ap.parse_args()
    (DATA / "results").mkdir(parents=True, exist_ok=True)
    for g in a.period:
        res = {"goal_no": g}
        for ch in ("work", "attention"):
            res[ch] = channel(g, ch, a.draws)
        if a.rooms:
            res["rooms"] = rooms_layer(g, a.draws)
        (DATA / "results" / f"G{g:02d}.json").write_text(json.dumps(res, indent=1, default=float))
        w = res["work"] or {}
        at = res["attention"] or {}
        def fmt(x):
            p = (x or {}).get("primary")
            return "n/a" if not p else f"{p['est']:.2f} [{p['lo']:.2f}, {p['hi']:.2f}] k={p.get('k')}"
        print(g, "work", fmt(w), "att", fmt(at), flush=True)


if __name__ == "__main__":
    main()
