"""H138 round 1, POST HOC (after seeing the negative pooled eps_q): does a window-level co-activity drive explain it?
O1 plus ln N_active(w) (agents with >= 1 own call in the window) on every testable unit-channel; DL pools by channel and
by own-role #51 units vs the rest. Writes results/posthoc.json. Not a pre-registered test.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h138lib as L  # noqa: E402
import run as RUN  # noqa: E402


def main():
    out = {}
    for ch in ("work", "attention"):
        data = RUN.load_channel(ch)
        rows = []
        for u, d in data.items():
            if int(d["leave"].sum()) < L.MIN_LEAVES:
                continue
            dp = L.prep(d).with_columns(pl.col("n_active").cast(pl.Float64).clip(lower_bound=1).log().alias("lnN"))
            r0 = L.fit(dp, "O1")
            r1 = L.fit(dp, "O1", extra=["lnN"])
            c0, c1, cn = L.coef(r0, "lnq"), L.coef(r1, "lnq"), L.coef(r1, "lnN")
            corr = float(np.corrcoef(np.log1p(dp["q_live"].to_numpy()), dp["lnN"].to_numpy())[0, 1])
            rows.append({"unit": u, "eps_o1": c0["est"], "eps_o1_se": c0["se"], "eps_lnN": c1["est"], "eps_lnN_se": c1["se"],
                         "b_lnN": cn["est"], "b_lnN_se": cn["se"], "corr_lnq_lnN": corr})
        pools = {}
        for name, sel in (("all", lambda x: True), ("51", lambda x: x.startswith("51")),
                          ("non51", lambda x: not x.startswith("51"))):
            s = [r for r in rows if sel(r["unit"])]
            pools[name] = {k: L.dl_pool([r[k] for r in s], [r[k + "_se"] for r in s]) for k in ("eps_o1", "eps_lnN", "b_lnN")}
            pools[name]["mean_corr_lnq_lnN"] = float(np.nanmean([r["corr_lnq_lnN"] for r in s])) if s else None
        out[ch] = {"units": rows, "pools": pools}
    (L.D / "results" / "posthoc.json").write_text(json.dumps(out, indent=1))
    for ch in out:
        for k, v in out[ch]["pools"].items():
            print(ch, k, {kk: (round(vv["est"], 2), round(vv["lo"], 2), round(vv["hi"], 2)) if isinstance(vv, dict) and vv.get("est") is not None else vv
                          for kk, vv in v.items()})


if __name__ == "__main__":
    main()
