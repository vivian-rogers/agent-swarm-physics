"""H139 real-data run (exploratory, non-reserved only): O1-O5 per unit, kick inputs, per agent-unit slow shares.

    uv run python hypotheses/H139-two-rate-variance-split/analysis/run_units.py --period G51 [--B 200]
Output: data/processed/H139-two-rate-variance-split/results/units_<period>.parquet, agents_<period>.parquet,
inputs_<period>.json (checkpoint per period).

Inputs (card, O3): #51 units take H130's per-unit gamma_kick and J_K (results/units.parquet, read only; same model and
variant). Shared-week units (#37-#44) re-estimate J_K here with H130's read-jump estimator (copied into h139lib);
gamma_kick there is not re-estimated (Amendment A2): 0.15, H130's pooled value.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h139lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

RES = L.DATA / "results"
H130 = L.ROOT / "data/processed/H130-ou-private-wells-51/results/units.parquet"
COMBOS = [("bge_small", "style_resid_period"), ("bge_small", "white32"), ("gte_modernbert", "style_resid_period")]
GK_POOLED = 0.15
J_POOLED = {"bge_small": 0.044, "gte_modernbert": 0.049}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", required=True)
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--dry-noise", action="store_true", help="code test: random vectors instead of embeddings")
    a = ap.parse_args()
    global RES
    if a.dry_noise:
        RES = Path(os.environ["H139_DRY_OUT"])
    RES.mkdir(parents=True, exist_ok=True)
    root = L.DATA / a.period
    st_all = pl.read_parquet(root / "statements.parquet").sort("agent", "t")
    assert not any(holdout_mask(st_all["pt_date"].to_list(), [int(a.period[1:])] * st_all.height))
    rd_all = pl.read_parquet(root / "reads.parquet")
    calls_all = pl.read_parquet(root / "calls.parquet")
    units = sorted(st_all["unit_id"].unique().to_list())
    pu = pl.read_parquet(L.SH / "period_units.parquet").select("unit_id", "n_days")
    ndays = dict(pu.iter_rows())
    h130 = pl.read_parquet(H130) if a.period == "G51" else None
    urows, arows, inputs = [], [], {}
    for model, variant in COMBOS:
        V = np.load(L.SH / f"embeddings/statements_{L.VEC[variant]}_{model}.npy", mmap_mode="r")
        Z_all = (np.random.default_rng(0).normal(0, 1, (st_all.height, 32)) if a.dry_noise
                 else np.asarray(V[st_all["srow"].to_numpy()], dtype=np.float64))
        H_all, ok_all = L.wells(st_all, Z_all)
        primary = (model, variant) == COMBOS[0]
        if primary:
            Zr = L.roomhour_resid(type("o", (), {"st": st_all})(), Z_all)
            Hr, okr = L.wells(st_all, Zr)
        srow_pos = {s: k for k, s in enumerate(st_all["srow"].to_list())}
        for u in units:
            t0 = time.time()
            st_u = st_all.filter(pl.col("unit_id") == u)
            S = L.make_skeleton(st_u, rd_all.filter(pl.col("unit_id") == u), calls_all.filter(pl.col("unit_id") == u), u)
            rows = np.array([srow_pos[s] for s in S.st["srow"].to_list()])
            Z = Z_all[rows]
            Hok = (H_all[rows], ok_all[rows])
            F = L.Fitter(S.hist)
            nd = int(ndays.get(u, len(S.days)))
            # ---- kick inputs
            if h130 is not None:
                hr = h130.filter((pl.col("unit") == u) & (pl.col("model") == model) & (pl.col("variant") == variant))
                gk_u = float(hr["g_kick"][0]) if hr.height else np.nan
                J_u = float(hr["J"][0]) if hr.height else np.nan
                src = "H130 units.parquet"
                gk = gk_u if (np.isfinite(gk_u) and 0.03 <= gk_u <= 1.0) else GK_POOLED
                jk = {"J": J_u, "source": src}
            else:
                X = np.where(Hok[1][:, None], Z - np.nan_to_num(Hok[0]), 0.0)
                W = L.boot_weights(len(S.ad_keys), a.B, 7)
                Jd = L.read_jump(S.st, S.rd, Z, X, Hok[1], S.ad, len(S.ad_keys))
                jk = {**L.jump_stats(Jd, W), "source": "H139 read jump (H130 estimator)"}
                gk_u, gk = np.nan, GK_POOLED
            J_in = jk["J"] if np.isfinite(jk.get("J", np.nan)) else J_POOLED.get(model, 0.044)
            Apred = S.rbar * J_in ** 2 * L.kick_memory(gk)
            Apred_pooled = S.rbar * J_POOLED.get(model, 0.044) ** 2 * L.kick_memory(GK_POOLED)
            inputs[f"{u}|{model}|{variant}"] = {"g_k_unit": gk_u, "g_k_used": gk, **{k: v for k, v in jk.items()},
                                                "rbar": S.rbar, "rbar_talk": S.rbar_talk, "A_pred": Apred,
                                                "A_pred_pooled_inputs": Apred_pooled}
            # ---- unit fits
            modes = [("corrected", Hok)] + ([("raw", Hok)] if primary else [])
            for mode, hk in modes:
                acc, _ = L.accumulate(S, Z, mode, hk)
                r = L.analyze(S, acc, F, gk, Apred, B=a.B, seed=11, oof=True, free=(mode == "corrected"),
                              natives=True)
                for k in ("boot_A_k", "boot_f_s", "boot_R_fast"):
                    r.pop(k, None)
                urows.append({**r, "unit": u, "period": a.period, "n_days": nd, "model": model, "variant": variant,
                              "mode": mode, "rbar": S.rbar, "rbar_talk": S.rbar_talk, "J_in": J_in,
                              "A_pred_pooled": Apred_pooled})
            if primary:
                acc, _ = L.accumulate(S, Zr[rows], "raw", (Hr[rows], okr[rows]))
                r = L.analyze(S, acc, F, gk, Apred, B=a.B, seed=11, oof=True, free=False, natives=False)
                for k in ("boot_A_k", "boot_f_s", "boot_R_fast"):
                    r.pop(k, None)
                urows.append({**r, "unit": u, "period": a.period, "n_days": nd, "model": model, "variant": variant,
                              "mode": "roomhour", "rbar": S.rbar, "rbar_talk": S.rbar_talk, "J_in": J_in,
                              "A_pred_pooled": Apred_pooled})
                # ---- per agent-unit (P4 slow share; O6 descriptive)
                acc, _ = L.accumulate(S, Z, "corrected", Hok)
                ad_agent = np.array([k[0] for k in S.ad_keys])
                for ag in np.unique(ad_agent):
                    m = ad_agent == ag
                    ra = L.analyze(S, acc, F, gk, S.rbar_agent.get(ag, np.nan) * J_in ** 2 * L.kick_memory(gk),
                                   B=50, seed=13, ad_mask=m, oof=False, free=False, natives=False)
                    arows.append({"unit": u, "agent": int(ag), "n_ad": int(m.sum()), "ok": ra.get("ok", False),
                                  "A_k": ra.get("A_k", np.nan), "f_s": ra.get("f_s", np.nan),
                                  "p_A_k_pos": ra.get("p_A_k_pos", np.nan),
                                  "rbar_i": S.rbar_agent.get(ag, np.nan), "n_pairs": ra.get("n_pairs", 0.0)})
            print(f"{a.period} {u} {model}/{variant}: done ({time.time() - t0:.0f}s)", flush=True)
    def ser(v):
        return json.dumps(v) if isinstance(v, (list, tuple)) else v
    pl.DataFrame([{k: ser(v) for k, v in r.items()} for r in urows], infer_schema_length=None).write_parquet(
        RES / f"units_{a.period}.parquet", compression="zstd")
    pl.DataFrame(arows, infer_schema_length=None).write_parquet(RES / f"agents_{a.period}.parquet", compression="zstd")
    (RES / f"inputs_{a.period}.json").write_text(json.dumps(inputs, indent=1, default=float))


if __name__ == "__main__":
    main()
