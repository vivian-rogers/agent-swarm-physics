"""H05 round 1b (2026-10-04): ledger read counts as the mediator of the room effect (HH248), and the native tests
R1b-N2 (#51g #focus) and R1b-N3 (NE42 split, attention reallocation). Non-holdout only.

Reads: for recipient i, sender j and PT day d, the number of j's agent messages that entered i's model calls
(`context_ledger_items` kind == agent, joined to `context_ledger_turns` for the recipient and day; DQ1 visibility
rule). Pair-day reads = reads(i <- j) + reads(j <- i). The ledger excludes held-out days (holdout flag) and this script
asserts that none of the pair-days it uses is held out.

Inputs: data/processed/H05-rooms-cut/r1b[/trim]/pair_day_bin1.parquet (explore_rooms.py with H05_DATA=r1b), r1b
mf_blocks.json, shared context ledger. Outputs: data/processed/H05-rooms-cut/r1b/r1b_reads.json and
pair_day_reads.parquet (pair-day reads, no text).

Predictions: card, "Round 1b" -> "Round-1b predictions for the new tests" (written 2026-10-04 08:35 UTC).
Usage: uv run python hypotheses/H05-rooms-cut/analysis/r1b_reads.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pairs import twfe  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
R1B = ROOT / "data/processed/H05-rooms-cut/r1b"
RNG = np.random.default_rng(20261004)
FOCUS = (6, 29)   # Gemini 2.5 Pro, Claude Opus 4.8 (left #general for #focus 08-05 -> 08-24)


def holdout_days() -> set:
    cal = pl.read_parquet(SH / "calendar.parquet")
    h = json.loads((ROOT / "hypotheses/holdout.json").read_text())
    held = set(cal.filter(pl.col("holdout") | pl.col("goal_no").is_in(h["goal_periods_held_out"]))["pt_date"].to_list())
    for w in h["ne_windows"]:
        held |= {d for d in cal["pt_date"].to_list() if w["start"] <= d < w["end"]}
    return held


def pair_reads(days: list) -> pl.DataFrame:
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind") == "agent").select("turn_id", "sender")
    tu = pl.scan_parquet(SH / "context_ledger_turns.parquet").select("turn_id", "agent", "pt_date", "holdout")
    r = (it.join(tu, on="turn_id").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
         .group_by("pt_date", "agent", "sender").agg(pl.len().alias("n")).collect())
    calls = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
             .group_by("pt_date", "agent").agg(pl.len().alias("calls"), pl.col("n_agent").sum().alias("reads_all")).collect())
    a = r.with_columns(pl.min_horizontal("agent", "sender").alias("i"), pl.max_horizontal("agent", "sender").alias("j"),
                       (pl.col("agent") < pl.col("sender")).alias("i_recv"))
    out = (a.filter(pl.col("agent") != pl.col("sender")).group_by("pt_date", "i", "j")
           .agg(pl.col("n").filter(pl.col("i_recv")).sum().alias("reads_i_from_j"),
                pl.col("n").filter(~pl.col("i_recv")).sum().alias("reads_j_from_i")))
    return out.with_columns(pl.col("i").cast(pl.Int8), pl.col("j").cast(pl.Int8)), calls


def attach_reads(pdf: pl.DataFrame, rd: pl.DataFrame) -> pl.DataFrame:
    t = pdf.join(rd, on=["pt_date", "i", "j"], how="left").with_columns(
        pl.col("reads_i_from_j").fill_null(0), pl.col("reads_j_from_i").fill_null(0))
    return t.with_columns((pl.col("reads_i_from_j") + pl.col("reads_j_from_i")).alias("reads"),
                          (pl.col("reads_i_from_j") + pl.col("reads_j_from_i") + 1).log().alias("lreads"),
                          ((pl.col("reads_i_from_j") + pl.col("reads_j_from_i")) > 0).cast(pl.Float64).alias("read_any"))


def fe_models(t: pl.DataFrame, y: str) -> dict:
    tt = t.filter(pl.col("coloc").is_not_null() & (pl.col("known") > 0.5) & pl.col(y).is_not_null())
    pk = (tt["i"].cast(pl.Int32) * 100 + tt["j"].cast(pl.Int32)).to_numpy()
    dk = tt["pt_date"].to_numpy()
    v = tt[y].to_numpy().astype(float)
    x = tt["coloc"].to_numpy().astype(float)
    ctrl = np.column_stack([(tt["act_i"] + tt["act_j"]).to_numpy(), (tt["act_i"] * tt["act_j"]).to_numpy()]).astype(float)
    lr = tt["lreads"].to_numpy().astype(float)
    ra = tt["read_any"].to_numpy().astype(float)
    out = {"n": int(len(v)), "share_coloc_with_reads": float(np.mean(ra[x >= 0.75] > 0)) if (x >= 0.75).any() else None,
           "share_cross_with_reads": float(np.mean(ra[x <= 0.25] > 0)) if (x <= 0.25).any() else None,
           "corr_coloc_lreads": float(np.corrcoef(x, lr)[0, 1])}

    def pack(r, names):
        return {nm: {"beta": r[nm]["beta"], "se": r[nm]["se"], "z": r[nm]["beta"] / r[nm]["se"] if r[nm]["se"] else None}
                for nm in names}

    def fit(X, names):
        r = twfe(v, X[:, 0], pk, dk, controls=np.column_stack([X[:, 1:], ctrl]) if X.shape[1] > 1 else ctrl)
        res = {names[0]: {"beta": r.get("beta"), "se": r.get("se_twoway")}}
        if X.shape[1] > 1:  # second coefficient: refit with the order swapped (twfe reports the first column)
            r2 = twfe(v, X[:, 1], pk, dk, controls=np.column_stack([X[:, :1], ctrl]))
            res[names[1]] = {"beta": r2.get("beta"), "se": r2.get("se_twoway")}
        return pack(res, names)

    out["M0_coloc"] = fit(np.column_stack([x]), ["coloc"])
    out["M1_coloc_plus_lreads"] = fit(np.column_stack([x, lr]), ["coloc", "lreads"])
    out["M2_lreads_only"] = fit(np.column_stack([lr]), ["lreads"])
    out["M3_coloc_plus_read_any_posthoc"] = fit(np.column_stack([x, ra]), ["coloc", "read_any"])
    b0, b1 = out["M0_coloc"]["coloc"]["beta"], out["M1_coloc_plus_lreads"]["coloc"]["beta"]
    out["coloc_shrink_frac"] = float(1 - b1 / b0) if b0 else None
    # (c) dose-response inside rooms
    m = x >= 0.75
    r = twfe(v[m], lr[m], pk[m], dk[m], controls=ctrl[m])
    out["dose_response_same_room"] = {"beta": r.get("beta"), "se": r.get("se_twoway"),
                                      "z": r["beta"] / r["se_twoway"] if r.get("se_twoway") else None, "n": int(m.sum())}
    return out


def hh248(t: pl.DataFrame) -> dict:
    res = {}
    t3 = t.filter(pl.col("regime") == "III")
    for spin in ("talk", "active"):
        ts = t3.filter(pl.col("spin") == spin)
        res[spin] = {"all_III": {y: fe_models(ts, y) for y in ("kappa_x", "c0_x")},
                     "two_room_era_37_44": {y: fe_models(ts.filter(pl.col("goal_no") <= 44), y) for y in ("kappa_x",)}}
    return res


def verdict_hh248(r: dict) -> dict:
    m0 = r["talk"]["all_III"]["kappa_x"]["M0_coloc"]["coloc"]
    m1 = r["talk"]["all_III"]["kappa_x"]["M1_coloc_plus_lreads"]
    dr = r["talk"]["all_III"]["kappa_x"]["dose_response_same_room"]
    a = m0["beta"] > 0 and m0["z"] > 1.96
    b = (m1["lreads"]["z"] > 1.96) and (abs(m1["coloc"]["z"]) < 1.96) and (r["talk"]["all_III"]["kappa_x"]["coloc_shrink_frac"] >= 0.5)
    c = dr["z"] is not None and dr["z"] > 1.96
    return {"a_replicates": bool(a), "b_reads_absorb_room": bool(b), "c_dose_response": bool(c),
            "HH248": "holds" if b else "fails"}


def focus_test(t: pl.DataFrame) -> dict:
    pre = [d for d in t["pt_date"].unique().to_list() if "2026-07-27" <= d <= "2026-08-04"]
    dur = [d for d in t["pt_date"].unique().to_list() if "2026-08-06" <= d <= "2026-08-21"]
    post = [d for d in t["pt_date"].unique().to_list() if "2026-08-25" <= d <= "2026-09-04" and d != "2026-08-27"]
    tt = t.filter(pl.col("spin") == "talk")
    arm = pl.col("i").is_in(list(FOCUS)) ^ pl.col("j").is_in(list(FOCUS))
    both = pl.col("i").is_in(list(FOCUS)) & pl.col("j").is_in(list(FOCUS))
    out = {}
    for nm, ds in (("pre", pre), ("during", dur), ("post", post)):
        w = tt.filter(pl.col("pt_date").is_in(ds))
        out[nm] = {"cut_arm_reads_per_pair_day": float(w.filter(arm)["reads"].mean()),
                   "stay_reads_per_pair_day": float(w.filter(~arm & ~both)["reads"].mean()),
                   "focus_pair_reads_per_day": float(w.filter(both)["reads"].mean()) if w.filter(both).height else None,
                   "days": len(ds)}
    out["cut_arm_read_drop_frac"] = 1 - out["during"]["cut_arm_reads_per_pair_day"] / out["pre"]["cut_arm_reads_per_pair_day"]
    return out


def ne42_test(t: pl.DataFrame, goal_days: dict, lab39: dict) -> dict:
    """Stay pairs = both agents in the #39 partition, same room in #39 and #41 (and together in #40's merged room)."""
    out = {}
    for spin in ("talk",):
        tt = t.filter((pl.col("spin") == spin) & pl.col("i").is_in(list(lab39)) & pl.col("j").is_in(list(lab39)))
        per = {}
        for g in (39, 40, 41):
            w = tt.filter(pl.col("pt_date").is_in(goal_days[g]))
            per[g] = w.group_by("i", "j").agg(pl.col("kappa_x").mean(), pl.col("c0_x").mean(), pl.col("reads").mean(),
                                              pl.col("coloc").mean())
        m = per[39].join(per[40], on=["i", "j"], suffix="_40").join(per[41], on=["i", "j"], suffix="_41")
        m = m.with_columns(pl.struct("i", "j").map_elements(lambda s: lab39[s["i"]] == lab39[s["j"]], return_dtype=pl.Boolean).alias("same"))
        st = m.filter(pl.col("same") & (pl.col("coloc") >= 0.75) & (pl.col("coloc_41") >= 0.75) & (pl.col("coloc_40") >= 0.75))
        res = {"n_stay_pairs": st.height}
        for y in ("reads", "kappa_x", "c0_x"):
            d1 = (st[f"{y}_40"] - st[y]).to_numpy()          # merge (#39 -> #40)
            d2 = (st[f"{y}_41"] - st[f"{y}_40"]).to_numpy()  # split (#40 -> #41)
            ok = np.isfinite(d1) & np.isfinite(d2)
            d1, d2 = d1[ok], d2[ok]
            bs = np.array([RNG.choice(d2, len(d2)).mean() for _ in range(4000)]) if len(d2) else np.array([np.nan])
            bs12 = np.array([(lambda k: d2[k].mean() - d1[k].mean())(RNG.integers(0, len(d2), len(d2))) for _ in range(4000)]) if len(d2) else np.array([np.nan])
            res[y] = {"level_39": float(st[y].mean()), "level_40": float(st[f"{y}_40"].mean()), "level_41": float(st[f"{y}_41"].mean()),
                      "d_merge_mean": float(d1.mean()), "d_split_mean": float(d2.mean()),
                      "d_split_ci95_pairboot": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                      "split_minus_merge": float(d2.mean() - d1.mean()),
                      "split_minus_merge_ci95": [float(np.percentile(bs12, 2.5)), float(np.percentile(bs12, 97.5))]}
        out[spin] = res
    return out


def main():
    held = holdout_days()
    out = {"built_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}
    tabs = {}
    for mask in ("none", "trim"):
        p = R1B / ("" if mask == "none" else mask) / "pair_day_bin1.parquet"
        if not p.exists():
            print("missing", p); continue
        pdf = pl.read_parquet(p)
        days = sorted(pdf["pt_date"].unique().to_list())
        assert not (set(days) & held), "held-out day in the pair-day table"
        if mask == "none":
            rd, calls = pair_reads(days)
        t = attach_reads(pdf, rd)
        tabs[mask] = t
        out[f"HH248_{mask}"] = hh248(t)
        out[f"HH248_{mask}_verdict"] = verdict_hh248(out[f"HH248_{mask}"])
        out[f"focus_{mask}"] = focus_test(t)
        print(mask, json.dumps(out[f"HH248_{mask}_verdict"]), flush=True)
    rd.write_parquet(R1B / "pair_day_reads.parquet", compression="zstd")
    # NE42 (untrimmed and trimmed), labels from #39 as in MF2 (GPT-5, agent 10, excluded)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import mf_blocks as M  # noqa: E402
    ad = pl.read_parquet(R1B / "agent_day.parquet")
    goal = dict(ad.group_by("pt_date").agg(pl.col("goal_no").first()).iter_rows())
    gd = {g: sorted(d for d in goal if goal[d] == g) for g in (39, 40, 41)}
    lab39 = M.labels_from_agent_day(ad, gd[39], exclude=(10,))
    for mask, t in tabs.items():
        out[f"NE42_{mask}"] = ne42_test(t, gd, lab39)
        mf = R1B / ("" if mask == "none" else mask) / "mf_blocks.json"
        if mf.exists():
            m2 = json.loads(mf.read_text())["MF2"]["talk"]
            out[f"NE42_{mask}"]["MF_J_in_39partition"] = {k: m2[k]["J_in"] for k in ("#39", "#40", "#41")}
            out[f"NE42_{mask}"]["MF_J_in_ci95"] = {k: m2[k]["J_in_ci95"] for k in ("#39", "#40", "#41")}
    (R1B / "r1b_reads.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k.startswith(("NE42", "focus"))}, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
