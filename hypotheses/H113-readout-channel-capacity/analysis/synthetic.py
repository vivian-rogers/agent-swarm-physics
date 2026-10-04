"""H113 synthetic validation on real read-out skeletons (axis F; run before any real uptake statistic).

Skeleton: a period's real scored talk calls (pending_sets), their real batches (agent items), real in-flight sets and
real statement times/rooms/authors. Only the 32-d vectors are synthetic:
  base statement  x = a * f_room(t) + noise          (f_room: Ornstein-Uhlenbeck topic field, tau = 30 min)
  response        y = rho * x_prev + uptake + c * f_room(t) + noise, written in time order over the real talk calls
  uptake          W2 b = 0, W3 b = 0.66, W6 b = 0.66 + field: gamma1 * k^-b * sum(batch x)
                  W4 hard capacity: gamma1 * x_J (one batch item at random); W5 recency: gamma1 * x_newest
                  W0 no uptake, no field; W1 field only (a = c = 1, no uptake); W3w: b = 0.66 at gamma1 / 3 (power)
The same scheme code (h113scheme.compute with V replaced) and estimators (h113lib.fit_b, info_curve) are applied.
Usage: uv run python hypotheses/H113-readout-channel-capacity/analysis/synthetic.py [--runs 20] [--period 38 ...]
Output: data/processed/H113-readout-channel-capacity/synthetic/{runs.parquet, summary.json}
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
import h113lib as L  # noqa: E402
import h113scheme as S  # noqa: E402

OUT = S.ROOT / "data/processed/H113-readout-channel-capacity/synthetic"
G1 = 0.15
WORLDS = {"W0": dict(a=0.0, c=0.0, mode="none"), "W1": dict(a=1.0, c=1.0, mode="none"),
          "W2": dict(a=0.3, c=0.0, mode="pow", b=0.0), "W3": dict(a=0.3, c=0.0, mode="pow", b=0.66),
          "W3w": dict(a=0.3, c=0.0, mode="pow", b=0.66, g=G1 / 3), "W4": dict(a=0.3, c=0.0, mode="one"),
          "W5": dict(a=0.3, c=0.0, mode="newest"), "W6": dict(a=1.0, c=1.0, mode="pow", b=0.66)}
TRUE_B = {"W2": 0.0, "W3": 0.66, "W3w": 0.66, "W4": 1.0, "W5": 1.0, "W6": 0.66}
SKELETONS = {18: None, 31: None, 38: None,
             51: ["2026-07-13", "2026-07-14", "2026-07-15"]}
TAU_S = 1800.0


def skeleton(g: int, days: list[str] | None):
    psd = S.SHARED / "pending_sets" / f"G{g:02d}"
    calls, items = S.build_frames_talks(g, psd)
    if days:
        calls = calls.filter(pl.col("pt_date").is_in(days))
        items = items.filter(pl.col("cid").is_in(calls["cid"].implode()))
    cr = S.chat_rows()
    items = S.at_call_items(calls, items, cr)
    dd = calls["pt_date"].unique().to_list()
    st = cr.filter(pl.col("pt_date").is_in(dd) & pl.col("srow").is_not_null() & (pl.col("speaker_kind").cast(pl.String) == "agent"))
    return calls, items, st.sort("t_us")


def synth_vectors(calls, items, st, w: dict, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n_all = S.vectors("bge_small").shape[0]
    V = np.zeros((n_all, 32), np.float32)
    # topic field per room: OU on statement times
    f_at = {}
    for (room,), g in st.group_by(["room"], maintain_order=True):
        t = g["t_us"].to_numpy() / 1e6; f = np.zeros((len(t), 32)); cur = rng.normal(0, 1 / np.sqrt(32), 32)
        for i in range(len(t)):
            if i:
                dt = max(t[i] - t[i - 1], 0); r = np.exp(-dt / TAU_S)
                cur = r * cur + np.sqrt(1 - r * r) * rng.normal(0, 1 / np.sqrt(32), 32)
            f[i] = cur
        for srow, fv in zip(g["srow"].to_numpy(), f):
            f_at[int(srow)] = fv
    srows = st["srow"].to_numpy().astype(int)
    noise = rng.normal(0, 1 / np.sqrt(32), (len(srows), 32))
    for k, s in enumerate(srows):
        V[s] = w["a"] * f_at[s] + noise[k]
    # responses in time order
    msg2srow = dict(zip(st["msg"].to_list(), st["srow"].to_list()))
    by_agent = {int(a): (g["t_us"].to_numpy(), g["srow"].to_numpy()) for (a,), g in st.group_by(["agent"], maintain_order=True)}
    it = {int(c): g for (c,), g in items.filter(pl.col("kind") == 0).group_by(["cid"], maintain_order=True)}
    gam = w.get("g", G1)
    for r in calls.sort("t_post_us").iter_rows(named=True):
        ys = msg2srow.get(int(r["resp_msg"]))
        if ys is None:
            continue
        va = by_agent.get(int(r["agent"]))
        kp = np.searchsorted(va[0], r["t_call_us"], side="left") - 1
        prev = V[int(va[1][kp])] if kp >= 0 else 0
        g = it.get(int(r["cid"]))
        bs = [msg2srow.get(int(m)) for m in (g["msg"].to_list() if g is not None else [])]
        okk = [i for i, s in enumerate(bs) if s is not None]
        X = V[[bs[i] for i in okk]] if okk else np.zeros((0, 32), np.float32)
        up = np.zeros(32)
        if len(X) and w["mode"] == "pow":
            up = gam * len(X) ** (-w["b"]) * X.sum(0)
        elif len(X) and w["mode"] == "one":
            up = gam * X[rng.integers(len(X))]
        elif len(X) and w["mode"] == "newest":
            rk = g["rank"].to_numpy()[okk]; up = gam * X[int(np.argmin(rk))]
        V[ys] = 0.5 * prev + up + w["c"] * f_at.get(int(ys), 0) + rng.normal(0, 1 / np.sqrt(32), 32)
    return V


def run_one(sk, g, world, seed):
    calls, items, st = sk
    V = synth_vectors(calls, items, st, WORLDS[world], seed)
    c, it, Y, X = S.compute(g, calls, items, "bge_small", V=V)
    row = {"period": g, "world": world, "seed": seed, "n": len(c)}
    for name, kw in (("F", {}), ("noF", {"with_F": False})):
        f = L.fit_b(c, B=100, seed=seed, **kw)
        row.update({f"b_{name}": f.get("b"), f"b_lo_{name}": f.get("b_lo"), f"b_hi_{name}": f.get("b_hi"),
                    f"g1_{name}": f.get("gamma1"), f"gF_{name}": f.get("gammaF")})
    cpc, kfi = L.placebo_corrected(c, it)
    f = L.fit_b(cpc, ys="ys_pc", with_F=False, B=100, seed=seed)
    row.update({"b_pc": f.get("b"), "b_lo_pc": f.get("b_lo"), "b_hi_pc": f.get("b_hi"), "g1_pc": f.get("gamma1"),
                "kappa_F": kfi["kappa_F"]})
    # raw (no window-field projection) variant: recompute without the field
    c2, _it2, _, _ = S.compute(g, calls, items, "bge_small", V=V, field=False)
    f = L.fit_b(c2, B=100, seed=seed)
    row.update({"b_raw": f.get("b"), "b_lo_raw": f.get("b_lo"), "b_hi_raw": f.get("b_hi")})
    c2pc, _ = L.placebo_corrected(c2, _it2)
    f = L.fit_b(c2pc, ys="ys_pc", with_F=False, B=100, seed=seed)
    row.update({"b_rawpc": f.get("b"), "b_lo_rawpc": f.get("b_lo"), "b_hi_rawpc": f.get("b_hi")})
    ic = L.info_curve(c, B=50, seed=seed)
    row["n_id_bins"] = int(sum(x["identified"] for x in ic))
    row["a_I"] = L.slope_loglog([x["k_mean"] for x in ic if x["identified"]], [x["I_bits"] for x in ic if x["identified"]],
                                [x["n"] for x in ic if x["identified"]])["slope"] if row["n_id_bins"] >= 2 else None
    row["r"] = L.redundancy(c)["r"]
    pc = L.placebo_contrast(c, it, B=100, seed=seed)
    row.update({"pc": pc.get("contrast"), "pc_lo": pc.get("lo"), "pc_hi": pc.get("hi")})
    return row


def summarize(df: pl.DataFrame) -> dict:
    out = {}
    df = df.with_columns(pl.col(pl.Float64).fill_nan(None))
    for (g, w), d in df.group_by(["period", "world"], maintain_order=True):
        tb = TRUE_B.get(w)
        s = {"runs": len(d)}
        for v in ("F", "noF", "raw", "pc", "rawpc"):
            b, lo, hi = d[f"b_{v}"], d[f"b_lo_{v}"], d[f"b_hi_{v}"]
            s[f"b_med_{v}"] = b.median()
            s[f"excl0_{v}"] = float((lo > 0).fill_null(False).mean())   # CI excludes 0 (b > 0)
            s[f"excl1_{v}"] = float((hi < 1).fill_null(False).mean())
            s[f"ci_width_{v}"] = (hi - lo).median()
            if tb is not None:
                s[f"bias_{v}"] = (b.median() - tb) if b.median() is not None else None
                s[f"cover_{v}"] = float(((lo <= tb) & (hi >= tb)).fill_null(False).mean())
        s["a_I_med"] = d["a_I"].median(); s["r_med"] = d["r"].median(); s["n_id_bins_med"] = d["n_id_bins"].median()
        s["pc_med"] = d["pc"].median(); s["pc_ci_gt0"] = float((d["pc_lo"] > 0).fill_null(False).mean())
        out[f"G{g}|{w}"] = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--worlds", default=",".join(WORLDS))
    ap.add_argument("--append", action="store_true", help="keep earlier runs (other skeletons) in runs.parquet")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    if a.append and (OUT / "runs.parquet").exists():
        old = pl.read_parquet(OUT / "runs.parquet")
        old = old.filter(~pl.col("period").is_in(a.period or list(SKELETONS)))
        rows = old.to_dicts()
    for g in (a.period or list(SKELETONS)):
        sk = skeleton(g, SKELETONS.get(g))
        print(f"G{g}: talks {len(sk[0])}", flush=True)
        for w in a.worlds.split(","):
            t0 = time.time()
            for s in range(a.runs):
                rows.append(run_one(sk, g, w, 100 * g + s))
            print(f"  {w}: {a.runs} runs {time.time() - t0:.0f}s", flush=True)
            pl.DataFrame(rows).write_parquet(OUT / "runs.parquet")
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / "runs.parquet")
    summ = summarize(df)
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    for k, v in summ.items():
        print(k, json.dumps({kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()}))


if __name__ == "__main__":
    main()
