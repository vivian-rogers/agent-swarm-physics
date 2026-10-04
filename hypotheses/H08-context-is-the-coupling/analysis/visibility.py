"""C9: visibility discontinuity. Does a recipient's turn respond to a room message only once a call that started after
the message produces it?

  uv run python hypotheses/H08-context-is-the-coupling/analysis/visibility.py [--period 38 ...]

Reads data/processed/H08-context-is-the-coupling/G<NN>/readout.parquet (scheme/build_turns.py). For units whose o = 0
turn is in flight: G(o) = mean y_o(real) - mean y_o(pseudo-message), o = -2..3, for talk and for addressing the sender.
D = G(1) - G(0). Day-cluster bootstrap (B = 200). Writes G<NN>/c9.json.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403

OFFS = list(range(-2, 4))
B = 200


def day_sums(df: pl.DataFrame, ycol: str, vcol: str, ndays: int):
    """Per day and offset: (sum y, count valid). df has column 'dix'."""
    y = df[ycol].to_numpy().astype(np.int64); v = df[vcol].to_numpy().astype(np.int64); d = df["dix"].to_numpy()
    num = np.zeros((ndays, len(OFFS))); den = np.zeros((ndays, len(OFFS)))
    for j, o in enumerate(OFFS):
        b = 1 << (o + 2)
        vv = (v & b) > 0
        np.add.at(num[:, j], d[vv], ((y[vv] & b) > 0).astype(float))
        np.add.at(den[:, j], d[vv], 1.0)
    return num, den


def gcurve(real: pl.DataFrame, pseudo: pl.DataFrame, kind: str, ndays: int, W: np.ndarray):
    nr, dr = day_sums(real, f"y{kind}", "yvalid", ndays)
    npn, dp = day_sums(pseudo, f"y{kind}p", "yvalidp", ndays)
    with np.errstate(invalid="ignore", divide="ignore"):
        pr = (W @ nr) / (W @ dr); pp = (W @ npn) / (W @ dp)
    G = pr - pp
    return G, pr, pp, dr.sum(0)


def summarize_set(real, pseudo, ndays, W, kinds=("talk", "addr")):
    out = {"n_real": real.height, "n_pseudo": pseudo.height}
    if real.height < 200 or pseudo.height < 200:
        out["underpowered"] = True
        return out
    for k in kinds:
        G, pr, pp, n = gcurve(real, pseudo, k, ndays, W)
        out[k] = {"G": {o: ci(G[:, j]) for j, o in enumerate(OFFS)},
                  "p_real": {o: float(pr[0, j]) for j, o in enumerate(OFFS)},
                  "p_pseudo": {o: float(pp[0, j]) for j, o in enumerate(OFFS)},
                  "n_valid": {o: float(n[j]) for j, o in enumerate(OFFS)},
                  "D": ci(G[:, OFFS.index(1)] - G[:, OFFS.index(0)]),
                  "pre": ci(G[:, OFFS.index(0)] - G[:, OFFS.index(-1)]),
                  "decay_21": ci(G[:, OFFS.index(2)] / G[:, OFFS.index(1)]),
                  "G2_lt_G1": ci(G[:, OFFS.index(1)] - G[:, OFFS.index(2)]),
                  "rel_jump": ci((pr[:, OFFS.index(1)] - pp[:, OFFS.index(1)]) / pp[:, OFFS.index(1)])}
    return out


def run_period(g: int, chat_day: dict, seed: int = 0, folder: Path | None = None) -> dict | None:
    folder = folder or (OUT / gname(g))
    f = folder / "readout.parquet"
    if not f.exists():
        return None
    ro = pl.read_parquet(f)
    days = sorted({chat_day[int(m)] for m in ro["msg"].unique().to_list()})
    dix = {d: i for i, d in enumerate(days)}
    ro = ro.with_columns(pl.col("msg").map_elements(lambda m: dix[chat_day[int(m)]], return_dtype=pl.Int64).alias("dix"))
    nd = len(days)
    W = np.vstack([np.ones((1, nd)), np.random.default_rng(seed).multinomial(nd, np.full(nd, 1 / nd), size=B)]).astype(float)
    own = ro.filter(~pl.col("placebo"))
    oth = ro.filter(pl.col("placebo"))
    out = {"period": gname(g), "n_days": nd, "n_pairs_own": own.height, "n_pairs_other": oth.height}
    ag = own.filter(pl.col("sender") >= 0)
    out["primary"] = summarize_set(ag.filter(pl.col("inflight")), ag.filter(pl.col("inflp")), nd, W)
    out["all_senders_talk"] = summarize_set(own.filter(pl.col("inflight")), own.filter(pl.col("inflp")), nd, W, ("talk",))
    out["guard5s"] = summarize_set(ag.filter(pl.col("inflight") & (pl.col("gap_s") >= 5)),
                                   ag.filter(pl.col("inflp") & (pl.col("gapp_s") >= 5)), nd, W)
    # POST HOC (added 2026-10-04 after seeing the o = -1 elevation and the o = 0 dip): recipients that did not talk at
    # o = -2 or -1 (so the sender's message is not a reply to the recipient's own talk, and o = 0 is not refractory)
    clean_r = ag.filter(pl.col("inflight") & ((pl.col("ytalk") & 3) == 0) & ((pl.col("yvalid") & 3) == 3))
    clean_p = ag.filter(pl.col("inflp") & ((pl.col("ytalkp") & 3) == 0) & ((pl.col("yvalidp") & 3) == 3))
    out["posthoc_clean"] = summarize_set(clean_r, clean_p, nd, W)
    if oth.height:
        oa = oth.filter(pl.col("sender") >= 0)
        out["other_room"] = summarize_set(oa.filter(pl.col("inflight")), oa.filter(pl.col("inflp")), nd, W)
    # wake units: the read-out call starts at a pause expiry (no in-flight turn); o = 1 vs pseudo at o = 1 (any status)
    wk = ag.filter(pl.col("wake"))
    if wk.height >= 200:
        G, pr, pp, n = gcurve(wk, ag, "talk", nd, W)
        Ga, _, _, _ = gcurve(wk, ag, "addr", nd, W)
        out["wake"] = {"n": wk.height, "G_talk_o1": ci(G[:, OFFS.index(1)]), "G_addr_o1": ci(Ga[:, OFFS.index(1)])}
    act = own.filter(pl.col("inflight") & pl.col("W_s").is_not_nan())
    allw = own.filter(pl.col("W_s").is_not_nan())
    q = lambda s: [float(x) for x in np.percentile(s, [25, 50, 75, 90])] if len(s) else None
    out["W_active_s"] = q(act["W_s"].to_numpy())
    out["W_all_s"] = q(allw["W_s"].to_numpy())
    out["share_inflight"] = float(own["inflight"].mean())
    out["share_wake"] = float(own["wake"].mean())
    jdump(out, folder / "c9.json")
    p = out["primary"]
    if "talk" in p:
        print(f"{gname(g)}: D_talk {p['talk']['D'][0]:+.4f} [{p['talk']['D'][1]:+.4f},{p['talk']['D'][2]:+.4f}] "
              f"D_addr {p['addr']['D'][0]:+.4f} [{p['addr']['D'][1]:+.4f},{p['addr']['D'][2]:+.4f}] "
              f"W_act med {out['W_active_s'][1]:.0f}s", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    a = ap.parse_args()
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["pt_date"]).with_row_index("msg")
    chat_day = dict(zip(chat["msg"].to_list(), chat["pt_date"].to_list()))
    res = {}
    for g in (a.period or sorted(PERIODS)):
        r = run_period(g, chat_day, seed=g)
        if r:
            res[gname(g)] = r
    write_provenance("c9 (G<NN>/c9.json)", "hypotheses/H08-context-is-the-coupling/analysis/visibility.py",
                     ["G<NN>/readout.parquet (H08 scheme)", "chat_core"], {"B": B, "offsets": OFFS,
                                                                           "primary": "own room, agent senders, in-flight o=0"})


if __name__ == "__main__":
    main()
