"""C9 round 1b: the read-out discontinuity on the DQ1 context ledger, with a non-mention response.

  uv run python hypotheses/H08-context-is-the-coupling/analysis/visibility_ledger.py [--period 38 ...]

Reads data/processed/H08-context-is-the-coupling/r1b/G<NN>/readout.parquet (scheme/build_turns_ledger.py) and writes
r1b/G<NN>/c9.json. Same estimator as round 1 (`visibility.py`, imported unchanged): units whose o = 0 call is in flight
(its first record after the message); G(o) = mean y_o(real) - mean y_o(pseudo); D = G(1) - G(0); day-cluster bootstrap.
Responses: talk; addressing (mention, round-1 measure); reply author (`yauth`: the talk's reply parent was written by
the sender; possible at any offset); content (`cos`: cosine of the talk at offset o with the message, among talking
calls, real minus pseudo; a non-mention, message-specific response). The message-specific reply bit (`yrep`) is 0 at
o <= 0 by construction (the message is not a visible candidate there) and is reported as a descriptive decay only.
Also: the clean-recipient subset, the other-room placebo, the NE03 split by batch rank (#10), and read-out delays.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from h08lib import *  # noqa: E402,F403
from visibility import OFFS, day_sums, gcurve, summarize_set  # noqa: E402

B = 200
OUT1B = OUT / "r1b"
CN = [f"m{-o}" if o < 0 else f"p{o}" for o in OFFS]


def cos_curve(real: pl.DataFrame, pseudo: pl.DataFrame, ndays: int, W: np.ndarray):
    """G_cos(o) = mean cos(talk_o, m) over talking calls (real) - the same for the pseudo message."""
    def sums(df, pre):
        d = df["dix"].to_numpy()
        num = np.zeros((ndays, len(OFFS))); den = np.zeros((ndays, len(OFFS)))
        for j, c in enumerate(CN):
            x = df[f"{pre}_{c}"].cast(pl.Float32).to_numpy()
            v = np.isfinite(x)
            np.add.at(num[:, j], d[v], x[v]); np.add.at(den[:, j], d[v], 1.0)
        return num, den
    nr, dr = sums(real, "cos"); npn, dp = sums(pseudo, "cosp")
    with np.errstate(invalid="ignore", divide="ignore"):
        G = (W @ nr) / (W @ dr) - (W @ npn) / (W @ dp)
    return {"G": {int(o): ci(G[:, j]) for j, o in enumerate(OFFS)}, "n_talk": {int(o): float(dr[:, j].sum()) for j, o in enumerate(OFFS)},
            "D": ci(G[:, list(OFFS).index(1)] - G[:, list(OFFS).index(0)]),
            "pre": ci(G[:, list(OFFS).index(0)] - G[:, list(OFFS).index(-1)])}


def summarize_all(real, pseudo, nd, W):
    out = summarize_set(real, pseudo, nd, W, ("talk", "addr", "auth"))
    if real.height >= 200 and pseudo.height >= 200:
        out["cos"] = cos_curve(real, pseudo, nd, W)
        G, pr, pp, n = gcurve(real, pseudo, "rep", nd, W)
        out["rep_decay"] = {int(o): ci(G[:, j]) for j, o in enumerate(OFFS)}
    return out


def prep(ro: pl.DataFrame) -> pl.DataFrame:
    # alias the new bit columns to the names gcurve expects (y<kind> / y<kind>p)
    return ro.with_columns(pl.col("yauth").alias("yauth"), pl.col("yauthp").alias("yauthp"),
                           pl.col("yrep").alias("yrep"), pl.col("yrepp").alias("yrepp"))


def run_period(g: int, chat_day: dict, seed: int = 0) -> dict | None:
    folder = OUT1B / gname(g)
    f = folder / "readout.parquet"
    if not f.exists():
        return None
    ro = prep(pl.read_parquet(f))
    if g == 36:
        pass   # whole period, as round 1 (C9 is not regime-III only)
    days = sorted({chat_day[int(m)] for m in ro["msg"].unique().to_list()})
    dix = {d: i for i, d in enumerate(days)}
    ro = ro.with_columns(pl.col("msg").map_elements(lambda m: dix[chat_day[int(m)]], return_dtype=pl.Int64).alias("dix"))
    nd = len(days)
    W = np.vstack([np.ones((1, nd)), np.random.default_rng(seed).multinomial(nd, np.full(nd, 1 / nd), size=B)]).astype(float)
    own = ro.filter(~pl.col("placebo"))
    oth = ro.filter(pl.col("placebo"))
    out = {"period": gname(g), "n_days": nd, "n_pairs_own": own.height, "n_pairs_other": oth.height,
           "design": "ledger calls (t_call), receiving call = o = 1"}
    ag = own.filter(pl.col("sender") >= 0)
    out["primary"] = summarize_all(ag.filter(pl.col("inflight")), ag.filter(pl.col("inflp")), nd, W)
    clean_r = ag.filter(pl.col("inflight") & ((pl.col("ytalk") & 3) == 0) & ((pl.col("yvalid") & 3) == 3))
    clean_p = ag.filter(pl.col("inflp") & ((pl.col("ytalkp") & 3) == 0) & ((pl.col("yvalidp") & 3) == 3))
    out["posthoc_clean"] = summarize_all(clean_r, clean_p, nd, W)
    # all units (o = 0 in flight or not): the ledger makes o = 1 exact for every pair
    out["all_units"] = summarize_set(ag, ag.filter(pl.col("yvalidp") > 0), nd, W, ("talk", "addr", "auth"))
    if oth.height:
        oa = oth.filter(pl.col("sender") >= 0)
        out["other_room"] = summarize_set(oa.filter(pl.col("inflight")), oa.filter(pl.col("inflp")), nd, W, ("talk", "addr"))
    if g == 10:   # NE03 native split by batch rank and side (10a = 08-18/19, 10b = 08-20..)
        side = {d: ("10a" if d < "2025-08-20" else "10b") for d in days}
        out["ne03"] = {}
        for s_ in ("10a", "10b"):
            dd = [dix[d] for d in days if side[d] == s_]
            Ws = W[:, dd]
            sub = ag.filter(pl.col("dix").is_in(dd)).with_columns(
                pl.col("dix").replace_strict({v: i for i, v in enumerate(dd)}, return_dtype=pl.Int64).alias("dix"))
            for lab, cond in (("rank_le3", pl.col("rank") <= 3), ("rank_gt10", pl.col("rank") > 10), ("all", pl.lit(True))):
                r_ = sub.filter(cond)
                out["ne03"][f"{s_}_{lab}"] = summarize_all(r_, r_.filter(pl.col("yvalidp") > 0), len(dd), Ws) | {"n": r_.height}
    q = lambda s: [float(x) for x in np.nanpercentile(s, [25, 50, 75, 90])] if len(s) else None
    act = own.filter(pl.col("inflight") & pl.col("W_s").is_not_nan())
    out["W_active_s"] = q(act["W_s"].to_numpy())
    out["Wc_active_s"] = q(act["Wc_s"].drop_nans().to_numpy())
    out["W_all_s"] = q(own["W_s"].drop_nans().to_numpy())
    out["Wc_all_s"] = q(own["Wc_s"].drop_nans().to_numpy())
    out["share_inflight"] = float(own["inflight"].mean())
    out["share_wake"] = float(own["wake"].mean())
    jdump(out, folder / "c9.json")
    p = out["primary"]
    if "talk" in p:
        cz = p.get("cos", {}).get("D", (np.nan,) * 3)
        print(f"{gname(g)}: D_talk {p['talk']['D'][0]:+.4f} [{p['talk']['D'][1]:+.4f},{p['talk']['D'][2]:+.4f}] "
              f"D_addr {p['addr']['D'][0]:+.4f} [{p['addr']['D'][1]:+.4f},{p['addr']['D'][2]:+.4f}] "
              f"D_auth {p['auth']['D'][0]:+.4f} D_cos {cz[0]:+.4f} [{cz[1]:+.4f},{cz[2]:+.4f}] "
              f"Wc_act med {out['Wc_active_s'][1] if out['Wc_active_s'] else float('nan'):.0f}s", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    a = ap.parse_args()
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["pt_date"]).with_row_index("msg")
    chat_day = dict(zip(chat["msg"].to_list(), chat["pt_date"].to_list()))
    for g in (a.period or (sorted(PERIODS) + [10])):
        run_period(g, chat_day, seed=g)
    write_provenance("r1b c9 (r1b/G<NN>/c9.json)", "hypotheses/H08-context-is-the-coupling/analysis/visibility_ledger.py",
                     ["r1b/G<NN>/readout.parquet (H08 ledger scheme)", "chat_core"],
                     {"B": B, "offsets": OFFS, "responses": ["talk", "addr (mention)", "auth (reply parent author)", "cos", "rep (descriptive)"]},
                     folder=OUT1B)


if __name__ == "__main__":
    main()
