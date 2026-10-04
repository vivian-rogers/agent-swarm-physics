"""C3 / NE41 round 1b: the erasure-coupling test on the DQ1 context ledger, with mention and reply responses.

  uv run python hypotheses/H08-context-is-the-coupling/analysis/erasure_ledger.py

Same units and linear probability model as round 1 (`erasure.py`; design and fixed-effect OLS imported unchanged), with
the inputs switched to the ledger (r1b/G<NN>/turns.parquet from scheme/build_turns_ledger.py, `context_ledger_items`):
- talk turn tau = a ledger talk call; its window opens at t_call;
- for every agent sender j, j's latest message received by the recipient (a ledger item) in the 30 min before t_call;
  its read-out call R = the call that received it; new = R is tau's own call;
- erased = a call in (R, tau] carries `reset_forced` (forced, the 41-turn cap: NE41) or `reset_consol` without
  `reset_forced` (voluntary); a reset on R itself means the message was read after the erasure (not erased), so round
  1's ambiguous units no longer exist; H15's catalog is not used;
- PC(tau): a reset on a call in the 30 min before t_call(tau); engaged: the previous talk call responded to j;
- responses: y_men (tau names j; round-1 measure) and y_auth (tau's reply parent was written by j; DQ2 reply labels).
Writes r1b/G<NN>/c3.json and r1b/ne41_pooled.json (random-effects pooling, exception (c)).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from h08lib import *  # noqa: E402,F403
from erasure import AGE_EDGES, C3_PERIODS, XN, dl_meta, fe_ols  # noqa: E402

B = 200
OUT1B = OUT / "r1b"
WIN_US = 30 * 60 * US


def units(g: int):
    tu = pl.read_parquet(OUT1B / gname(g) / "turns.parquet")
    if g == 36:
        tu = tu.filter(pl.col("pt_date") >= "2026-03-24")
    days = sorted(tu["pt_date"].unique().to_list())
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(tu["turn_id"].implode()))
             .filter(pl.col("kind").cast(pl.Utf8) == "agent").select("turn_id", "message_id", "sender").collect())
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t"])
    items = items.join(chat, on="message_id", how="left").with_columns(pl.col("t").dt.epoch("us").alias("t_m"))
    rec_of = dict(zip(tu["turn_id"].to_list(), tu["agent"].to_list()))
    items = items.with_columns(pl.col("turn_id").replace_strict(rec_of, default=-1).alias("rcpt"))
    rows = []
    for (a, d), T in tu.group_by(["agent", "pt_date"], maintain_order=True):
        a = int(a)
        T = T.sort("s_us")
        tid = T["turn_id"].to_numpy(); s = T["s_us"].to_numpy()
        talk = T["talk"].fill_null(False).to_numpy() & T["msg"].is_not_null().to_numpy()
        ment = T["ment"].to_numpy().astype(np.uint64); pa = T["par_auth"].to_numpy().astype(np.uint64)
        rf = T["reset_forced"].fill_null(False).to_numpy(); rc = T["reset_consol"].fill_null(False).to_numpy()
        pos = {int(x): q for q, x in enumerate(tid)}
        I = items.filter((pl.col("rcpt") == a) & pl.col("turn_id").is_in(list(pos))).sort("t_m")
        if not I.height:
            continue
        it_t = I["t_m"].to_numpy(); it_s = I["sender"].to_numpy().astype(int)
        it_R = np.array([pos[int(x)] for x in I["turn_id"].to_numpy()])
        rset = np.nonzero(rf | rc)[0]
        tk = np.nonzero(talk)[0]
        prev_talk = -1
        for k in tk:
            sk = s[k]
            sel = (it_R <= k) & (it_t >= sk - WIN_US) & (it_t < sk)
            if sel.any():
                last = {}
                for q in np.nonzero(sel)[0]:
                    last[it_s[q]] = (it_t[q], it_R[q])
                pc = bool(((s[rset] > sk - WIN_US) & (s[rset] <= sk)).any()) if len(rset) else False
                for j, (tmj, R) in last.items():
                    if j == a or j < 0 or j > 63:
                        continue
                    new = R == k
                    kind = ""
                    if R < k:
                        between = np.arange(R + 1, k + 1)
                        if rf[between].any():
                            kind = "CF"
                        elif rc[between].any():
                            kind = "CV"
                    age = (sk - tmj) / US / 60
                    bit = np.uint64(j)
                    eng_m = prev_talk >= 0 and bool((ment[prev_talk] >> bit) & np.uint64(1))
                    eng_a = prev_talk >= 0 and bool((pa[prev_talk] >> bit) & np.uint64(1))
                    y_m = bool((ment[k] >> bit) & np.uint64(1)); y_a = bool((pa[k] >> bit) & np.uint64(1))
                    rows.append((a, d, int(k), int(j), y_m, y_a, bool(new), kind != "", kind, pc, eng_m, eng_a, float(age)))
            prev_talk = k
    U = pl.DataFrame(rows, orient="row", schema={
        "agent": pl.Int16, "pt_date": pl.Utf8, "k": pl.Int64, "snd": pl.Int16, "y_men": pl.Boolean, "y_auth": pl.Boolean,
        "new": pl.Boolean, "erased": pl.Boolean, "kind": pl.Utf8, "PC": pl.Boolean, "eng_men": pl.Boolean,
        "eng_auth": pl.Boolean, "age": pl.Float64})
    return U, days


def fit(U: pl.DataFrame, days, W, resp: str):
    V = U.with_columns(pl.col(f"y_{resp}").alias("y"), pl.col(f"eng_{resp}").alias("engaged"))
    out = {}
    ref = V.filter(~pl.col("new") & ~pl.col("erased") & pl.col("PC"))["y"].mean()
    out["ref_rate_old_inContext_PC"] = float(ref) if ref is not None else None
    out["rates"] = {"new": float(V.filter(pl.col("new"))["y"].mean() or 0),
                    "old_kept": float(V.filter(~pl.col("new") & ~pl.col("erased"))["y"].mean() or 0),
                    "old_erased_F": float(V.filter(pl.col("kind") == "CF")["y"].mean() or 0),
                    "old_erased_V": float(V.filter(pl.col("kind") == "CV")["y"].mean() or 0)}
    if V.filter(pl.col("erased")).height >= 50:
        bt = fe_ols(V, days, W)
        out["beta"] = {n: ci(bt[:, j]) for j, n in enumerate(XN)}
        if ref:
            out["rel_F"] = ci(bt[:, 0] / ref); out["rel_V"] = ci(bt[:, 1] / ref)
        out["F_minus_V"] = ci(bt[:, 0] - bt[:, 1])
    return out


def main():
    res = {}
    for g in C3_PERIODS:
        if not (OUT1B / gname(g) / "turns.parquet").exists():
            continue
        U, days = units(g)
        nd = len(days)
        rng = np.random.default_rng(g)
        W = np.vstack([np.ones((1, nd)), rng.multinomial(nd, np.full(nd, 1 / nd), size=B)]).astype(float)
        out = {"period": gname(g), "n_days": nd, "n_units": U.height,
               "n_erased": {k: int(v) for k, v in U.filter(pl.col("erased")).group_by("kind").len().iter_rows()}}
        for resp in ("men", "auth"):
            out[resp] = fit(U, days, W, resp)
        jdump(out, OUT1B / gname(g) / "c3.json")
        res[gname(g)] = out
        bm, ba = out["men"].get("beta", {}), out["auth"].get("beta", {})
        print(f"{gname(g)}: units {U.height}, erased {out['n_erased']}, beta_F men {bm.get('erased_F')} auth {ba.get('erased_F')}; "
              f"rel_F men {out['men'].get('rel_F')} auth {out['auth'].get('rel_F')}", flush=True)
    pooled = {}
    for resp in ("men", "auth"):
        pooled[resp] = {}
        for key, kk in (("erased_F", "CF"), ("erased_V", "CV")):
            vv = [v for v in res.values() if "beta" in v[resp] and v["n_erased"].get(kk, 0) >= 50]
            pooled[resp][key] = dl_meta([v[resp]["beta"][key][0] for v in vv],
                                        [(v[resp]["beta"][key][2] - v[resp]["beta"][key][1]) / 3.92 for v in vv])
        for key in ("rel_F", "rel_V"):
            vv = [v for v in res.values() if key in v[resp]]
            pooled[resp][key] = dl_meta([v[resp][key][0] for v in vv], [(v[resp][key][2] - v[resp][key][1]) / 3.92 for v in vv])
    jdump({"periods": res, "pooled": pooled}, OUT1B / "ne41_pooled.json")
    print("POOLED", pooled, flush=True)
    write_provenance("r1b c3 (r1b/G<NN>/c3.json, r1b/ne41_pooled.json)", "hypotheses/H08-context-is-the-coupling/analysis/erasure_ledger.py",
                     ["r1b/G<NN>/turns.parquet (H08 ledger scheme)", "context_ledger_items", "context_ledger_turns (reset flags)",
                      "chat_core", "reply_pairs (via turns.par_auth)"],
                     {"B": B, "age_edges_min": AGE_EDGES, "window_min": 30, "erasure": "reset_forced / reset_consol in (R, tau]"},
                     folder=OUT1B)


if __name__ == "__main__":
    main()
