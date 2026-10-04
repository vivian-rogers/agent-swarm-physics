"""H88 natives (non-holdout only): N1 closed village (G05), N2 NE27 newcomers (G10), N3 carrier loss (NE28 folder).

  uv run python hypotheses/H88-collective-memory-decay/analysis/natives.py
Output: data/processed/H88-collective-memory-decay/natives/natives.json
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h88lib as H  # noqa: E402

OUTD = H.DATA / "natives"
B = 2000


def closed_village(daily):
    out = {}
    for P in (4, 5, 6, 7):
        for kind in ("art", "term"):
            s = daily.filter((pl.col("P") == P) & (pl.col("kind") == kind) & (pl.col("group") == "vet")
                             & pl.col("observed") & (pl.col("O") > 0) & (pl.col("pt_date") <= "2025-08-15")).sort("k")
            k, y, O = (s["k"].to_numpy().astype(float), s["y"].to_numpy().astype(float), s["O"].to_numpy().astype(float))
            if y.sum() < 30 or len(k) < 15:
                out[f"{P}/{kind}"] = {"n_uses": int(y.sum()), "n_days": len(k), "fit": None}
                continue
            f = H.fit_all(k, y, O)
            out[f"{P}/{kind}"] = {"n_uses": int(y.sum()), "n_days": len(k), "best": f["best"], "dq_M1_M2": f["dq_M1_M2"],
                                  "biexp": f["biexp"], "M2": f["M2_params"], "M1": f["M1_params"], "M1c": f["M1c_params"]}
    per_P = {}
    for P in (4, 5, 6, 7):
        per_P[P] = any(v.get("biexp") for k_, v in out.items() if k_.startswith(f"{P}/") and v.get("fit", 1) is not None)
    n_bi = sum(per_P.values())
    fitted = {P: [v.get("best") for k_, v in out.items() if k_.startswith(f"{P}/") and v.get("best")] for P in (4, 5, 6, 7)}
    n_m1 = sum(1 for P, b in fitted.items() if b and all(x == "M1" for x in b))
    verdict = "supported" if n_bi >= 2 else ("failed" if n_m1 >= 3 else "mixed")
    return {"fits": out, "n_periods_biexp": n_bi, "n_periods_M1": n_m1, "n_periods_fitted": sum(1 for b in fitted.values() if b),
            "verdict": verdict}


def ne27(uses, periods):
    """Newcomers (9, 10, 11) vs veterans (0, 5, 6, 8), 08-18 -> 09-19, items of #2-#8, by item age."""
    cal = pl.read_parquet(H.SH / "calendar.parquet").select("pt_date").sort("pt_date")["pt_date"].to_list()
    newc, vets = [9, 10, 11], [0, 5, 6, 8]
    pos = {d: i for i, d in enumerate(cal)}
    lastday = dict(zip(periods["P"].to_list(), periods["last_day"].to_list()))
    res = {}
    for kind in ("term", "art"):
        u = uses.filter((pl.col("kind") == kind) & (pl.col("speaker") == "agent") & (pl.col("pt_date") >= "2025-08-18")
                        & (pl.col("pt_date") <= "2025-09-19"))
        # offsets: all uses of the kind by each group per day (all periods' items + others): use all-agent uses table
        d_all = pl.read_parquet(H.DATA / "daily.parquet").filter((pl.col("kind") == kind) & (pl.col("group") == "all"))
        rows = []
        days = sorted(set(u["pt_date"].to_list()))
        for d in days:
            ud = u.filter(pl.col("pt_date") == d)
            Onew = ud.filter(pl.col("agent").is_in(newc)).height
            Ovet = ud.filter(pl.col("agent").is_in(vets)).height
            for P in range(2, 9):
                if P not in lastday:
                    continue
                age = pos[d] - pos[lastday[P]]
                up = ud.filter(pl.col("P") == P)
                rows.append((d, P, age, up.filter(pl.col("agent").is_in(newc)).height,
                             up.filter(pl.col("agent").is_in(vets)).height, Onew, Ovet))
        df = pl.DataFrame(rows, schema=["d", "P", "age", "yn", "yv", "On", "Ov"], orient="row")
        del d_all
        # NOTE: offsets here are the groups' uses of items of all followed periods (O of the shared daily table is per P
        # and group); restrict to items of followed periods for both groups, so the share is within that pool.
        tot = df.group_by("d").agg(pl.col("yn").sum().alias("Tn"), pl.col("yv").sum().alias("Tv"))
        df = df.join(tot, on="d")
        bands = {"<=15": (0, 15), "16-40": (16, 40), ">40": (41, 10 ** 6)}

        def R_of(sub):
            out = {}
            for b, (lo, hi) in bands.items():
                s = sub.filter((pl.col("age") >= lo) & (pl.col("age") <= hi) & (pl.col("Tv") > 0) & (pl.col("Tn") > 0))
                exp = (s["Tn"] * s["yv"] / s["Tv"]).sum()
                out[b] = float(s["yn"].sum() / exp) if exp > 0 else None
            return out
        est = R_of(df)
        rng = np.random.default_rng(27)
        dd = sorted(set(df["d"].to_list()))
        parts = {d: df.filter(pl.col("d") == d) for d in dd}
        bs = []
        for _ in range(B // 4):
            pick = rng.choice(dd, len(dd))
            bs.append(R_of(pl.concat([parts[d] for d in pick])))
        ci = {b: [float(np.nanquantile([x[b] if x[b] is not None else np.nan for x in bs], q)) for q in (.025, .975)]
              for b in bands}
        res[kind] = {"R": est, "R_ci": ci, "n_days": len(dd), "uses_new": int(df["yn"].sum()), "uses_vet": int(df["yv"].sum())}
    t = res["term"]
    p1 = t["R"]["<=15"] is not None and t["R_ci"]["<=15"][1] < 1
    p2 = (t["R"][">40"] or 0) > (t["R"]["<=15"] or np.inf)
    against = (t["R"]["<=15"] is not None and t["R"]["<=15"] >= 1) or not p2
    res["verdict"] = "supported" if (p1 and p2) else ("failed" if against else "mixed")
    return res


def carrier_loss(uses):
    cal = pl.read_parquet(H.SH / "calendar.parquet").select("pt_date", "holdout").sort("pt_date")
    days = cal["pt_date"].to_list()
    exits = [("Grok 4", [11], "2025-10-29"), ("NE28 o3 + Opus 4.1", [5, 9], "2025-12-01"),
             ("NE29 Claude 3.7 Sonnet", [0], "2026-02-19")]
    u = uses.filter(pl.col("speaker") == "agent").with_columns(
        (pl.col("kind") + ":" + pl.col("item").cast(pl.String)).alias("key"))
    out = {}
    pooled_c, pooled_0 = [], []
    for name, ret, ex in exits:
        i = days.index(next(d for d in days if d >= ex))
        pre = days[max(0, i - 10):i]; post = days[i:i + 10]
        up = u.filter(pl.col("pt_date").is_in(pre))
        st = up.group_by("key").agg(pl.len().alias("n"), pl.col("agent").is_in(ret).sum().alias("nr"))
        st = st.filter(pl.col("n") >= 5).with_columns((pl.col("nr") / pl.col("n")).alias("fr"))
        if st.height == 0:
            continue
        q = np.quantile(st["n"].to_numpy(), [1 / 3, 2 / 3])
        st = st.with_columns(pl.col("n").map_elements(lambda x: int(np.searchsorted(q, x)), return_dtype=pl.Int64).alias("ter"))
        oth_pre = up.filter(~pl.col("agent").is_in(ret)).group_by("key").len().rename({"len": "a"})
        oth_post = (u.filter(pl.col("pt_date").is_in(post) & ~pl.col("agent").is_in(ret)).group_by("key").len()
                    .rename({"len": "b"}))
        st = st.join(oth_pre, on="key", how="left").join(oth_post, on="key", how="left").fill_null(0)
        car = st.filter(pl.col("fr") >= 0.4); con = st.filter(pl.col("fr") < 0.1)
        # weight controls to the carried items' tercile mix
        w = {t: car.filter(pl.col("ter") == t).height for t in range(3)}
        con = con.with_columns(pl.col("ter").replace_strict(w, default=0).alias("w"))
        out[name] = {"n_carried": car.height, "n_control": con.height, "post_observed_days": len(post),
                     "carried": car.select("a", "b").rows(), "control": con.select("a", "b", "w").rows()}
        pooled_c += out[name]["carried"]; pooled_0 += out[name]["control"]

    def ror(c, z):
        c = np.array(c, float); z = np.array(z, float)
        if len(c) == 0 or len(z) == 0 or c[:, 0].sum() == 0 or (z[:, 0] * z[:, 2]).sum() == 0:
            return np.nan
        rc = c[:, 1].sum() / c[:, 0].sum()
        r0 = (z[:, 1] * z[:, 2]).sum() / (z[:, 0] * z[:, 2]).sum()
        return rc / r0 if r0 > 0 else np.nan
    rng = np.random.default_rng(29)
    res = {"per_exit": {}}
    for name, v in list(out.items()) + [("pooled", {"carried": pooled_c, "control": pooled_0})]:
        c, z = v["carried"], v["control"]
        est = ror(c, z)
        bs = []
        for _ in range(B):
            cc = [c[j] for j in rng.integers(0, len(c), len(c))] if c else []
            zz = [z[j] for j in rng.integers(0, len(z), len(z))] if z else []
            bs.append(ror(cc, zz))
        bs = np.array(bs); bs = bs[np.isfinite(bs)]
        res["per_exit"][name] = {"ror": float(est), "ci": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))]
                                 if len(bs) else None, "n_carried": len(c), "n_control": len(z),
                                 "carried_pre_others": int(sum(x[0] for x in c)), "carried_post_others": int(sum(x[1] for x in c))}
    p = res["per_exit"]["pooled"]
    ok = p["ci"] is not None and 0.5 <= p["ror"] <= 2 and p["ci"][0] <= 1 <= p["ci"][1]
    res["verdict"] = "supported" if ok else ("failed" if (p["ci"] and p["ci"][1] < 1) else "mixed")
    return res


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    daily = H.load_daily(); uses = pl.read_parquet(H.DATA / "uses.parquet")
    periods = pl.read_parquet(H.DATA / "periods.parquet")
    out = {"run_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "G05": closed_village(daily), "NE27": ne27(uses, periods), "NE28": carrier_loss(uses)}
    (OUTD / "natives.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
