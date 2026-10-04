"""H99 round 2, R4: kicks aligned on each recipient's receiving call, against a matched spontaneous-regression
(Onsager) prediction on the same clock.

Kicks: nudges (leading-@ primary target only) and human messages (every recipient), from r2/kicks (kicks_receipts,
same-day receiving calls). Outcomes: activity (state >= 3) and talk of the recipient in minutes k = 0..29 after the
receiving call's minute (round-1 activity_bins grid), and talk on calls n = 0..10 after the receiving call.
Placebo: the same agent's receiving calls of the same day and class (wake vs ordinary) with no human or nudge item
read and no kick read by that agent in the previous 30 min (past-only). G(k) = kicked - placebo stratum mean.
Spontaneous regression S(k) = placebo stratum mean - agent-day mean, weighted like the kicked set.
Omega = sum_k G(k) / (G(0) sum_k S(k)/S(0)). Cluster bootstrap over agent-days (B = 400).
Also the round-1 form: A30 / (G(0) / (1 - 0.34)).

Output: data/processed/H99-glauber-fluctuation-relaxation/r2/results/kicks_r4.json (+ kernels in kicks_r4_kernels.parquet)
Usage: uv run python .../r2_kicks.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2run as RR  # noqa: E402

OUT = RR.R2 / "results"
K = 30
NC = 11
PAST_S = 1800
RHO_R1 = 0.34   # round-1 #51 activity rho_perp(1)


def unit_events(uid, kind):
    meta, calls, msgs, exo, ws = RR.load_unit(uid)
    gp = RR.BASE / "grids" / f"{uid}.npz"
    if not gp.exists():
        return None
    z = np.load(gp)
    dmap = {d: k for k, d in enumerate(meta["days"])}
    kr = pl.read_parquet(RR.R2 / "kicks" / f"{uid}.parquet")
    if kind == "nudge":
        kr = kr.filter((pl.col("kind") == "nudge") & pl.col("is_primary"))
    else:
        kr = kr.filter(pl.col("kind") == "human_message")
    allk = pl.read_parquet(RR.R2 / "kicks" / f"{uid}.parquet").filter(pl.col("kind").is_in(["nudge", "human_message"]))
    C = calls.sort("agent", "day", "t", "turn_id").with_columns(
        pl.int_range(pl.len()).over("agent", "day").alias("pos"),
        pl.col("talk").cast(pl.Float64))
    rows = []
    for k_, d in enumerate([str(x) for x in z["days"]]):
        di = dmap[d]
        T, A = z[f"talk_{k_}"], z[f"act_{k_}"]
        ags = list(z[f"agents_{k_}"])
        L = T.shape[1]
        ws_d = ws[di]
        Cd = C.filter(pl.col("day") == di)
        kd = kr.join(Cd.select("turn_id"), on="turn_id", how="semi")
        kicked_turns = set(kd["turn_id"].to_list())
        ak = allk.join(Cd.select("turn_id", "agent"), on=["turn_id", "agent"], how="semi")
        for a in ags:
            i = ags.index(a)
            Ca = Cd.filter(pl.col("agent") == a)
            if Ca.height < 5:
                continue
            ta = Ca["t"].to_numpy()
            talk_seq = Ca["talk"].to_numpy()
            akt = np.sort(ak.filter(pl.col("agent") == a)["t_call"].to_numpy())
            present = A[i] > 0
            span = np.flatnonzero(present)
            if len(span) < 10:
                continue
            lo, hi = span[0], span[-1]
            base_act = A[i, lo:hi + 1].mean()
            base_talk = T[i, lo:hi + 1].mean()
            for r in Ca.iter_rows(named=True):
                m0 = int((r["t"] - ws_d) // 60)
                if m0 < 0 or m0 >= L:
                    continue
                is_k = r["turn_id"] in kicked_turns
                if not is_k:
                    if r["E_h"] > 0 or r["E_n"] > 0:
                        continue
                    if len(akt) and ((akt < r["t"]) & (akt >= r["t"] - PAST_S)).any():
                        continue
                ya = np.full(K, np.nan)
                yt = np.full(K, np.nan)
                n = min(K, L - m0)
                ya[:n] = A[i, m0:m0 + n]
                yt[:n] = T[i, m0:m0 + n]
                p = r["pos"]
                yc = np.full(NC, np.nan)
                nn = min(NC, len(talk_seq) - p)
                yc[:nn] = talk_seq[p:p + nn]
                rows.append({"unit": uid, "day": di, "agent": a, "wake": int(r["is_wake"]), "kicked": is_k,
                             "ya": ya, "yt": yt, "yc": yc, "base_act": base_act, "base_talk": base_talk,
                             "base_call": float(talk_seq.mean())})
    return rows


def kernels(ev):
    """ev: list of dict events of one scope. Returns G and S for activity, talk (minutes) and talk (calls)."""
    from collections import defaultdict
    strata = defaultdict(lambda: {"k": [], "p": []})
    for e in ev:
        strata[(e["unit"], e["day"], e["agent"], e["wake"])]["k" if e["kicked"] else "p"].append(e)
    out = {}
    for key, nlag, bkey in (("ya", K, "base_act"), ("yt", K, "base_talk"), ("yc", NC, "base_call")):
        Gs, Ss, w = [], [], []
        for s, v in strata.items():
            if not v["k"] or len(v["p"]) < 2:
                continue
            P = np.nanmean(np.stack([e[key] for e in v["p"]]), 0)
            for e in v["k"]:
                Gs.append(e[key] - P)
                Ss.append(P - e[bkey])
        if not Gs:
            out[key] = None
            continue
        G = np.nanmean(np.stack(Gs), 0)
        S = np.nanmean(np.stack(Ss), 0)
        out[key] = (G, S, len(Gs))
    return out


def omega(G, S, calls=False):
    """Amendment B2 (2026-10-04, after the first R4 run returned G(0) <= 0 for activity): minute kernels are normalized
    at their own peak p = argmax_{k <= 2} G(k) (round 1's 'from its own peak'), and the Onsager prediction uses the
    spontaneous regression from the same lag: A_ons = G(p) sum_{k >= p} S(k)/S(p); Omega = sum_{k >= p} G(k) / A_ons.
    Call kernels (talk per call): spontaneous per-call talk memory is <= 0 in regime III (rho_s - W0 = -0.05), so
    Onsager predicts that the integrated response equals the immediate one: Omega_call = sum_n G(n) / G(0)."""
    if G is None or not np.isfinite(G[:3]).all():
        return np.nan, np.nan, np.nan, -1
    if calls:
        if G[0] <= 0:
            return np.nan, np.nan, np.nan, 0
        a = float(np.nansum(G))
        return a / float(G[0]), a, float(G[0]), 0
    p = int(np.argmax(G[:3]))
    if G[p] <= 0 or not np.isfinite(S[p]) or S[p] <= 0:
        return np.nan, np.nan, np.nan, p
    a30 = float(np.nansum(G[p:]))
    pred = float(G[p] * np.nansum(S[p:] / S[p]))
    return a30 / pred, a30, pred, p


def scope_result(ev, B=400, seed=0):
    rng = np.random.default_rng(seed)
    base = kernels(ev)
    res = {"n_kicked": int(sum(e["kicked"] for e in ev)), "n_placebo": int(sum(not e["kicked"] for e in ev))}
    clusters = {}
    for e in ev:
        clusters.setdefault((e["unit"], e["day"], e["agent"]), []).append(e)
    ck = list(clusters)
    draws = {k: [] for k in ("ya", "yt", "yc")}
    for _ in range(B):
        pick = rng.integers(0, len(ck), len(ck))
        ev_b = []
        for j, c in enumerate(pick):
            for e in clusters[ck[c]]:
                ev_b.append({**e, "agent": (e["agent"], j)})
        kb = kernels(ev_b)
        for k in draws:
            if kb[k] is not None:
                o, a30, pred, p = omega(kb[k][0], kb[k][1], calls=(k == "yc"))
                gp = kb[k][0][max(p, 0)]
                draws[k].append((o, a30, pred, gp, a30 / (gp / (1 - RHO_R1)) if gp > 0 else np.nan))
    for k in ("ya", "yt", "yc"):
        if base[k] is None:
            continue
        G, S, n = base[k]
        o, a30, pred, p = omega(G, S, calls=(k == "yc"))
        gp = G[max(p, 0)]
        r1 = a30 / (gp / (1 - RHO_R1)) if gp > 0 else np.nan
        d = np.array(draws[k], float) if draws[k] else np.full((1, 5), np.nan)
        def q(j):
            v = d[:, j]
            v = v[np.isfinite(v)]
            return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) > 0.8 * B else [None, None]
        res[k] = {"n": n, "G": [round(float(x), 5) for x in G], "S": [round(float(x), 5) for x in S],
                  "omega": o, "omega_ci": q(0), "A": a30, "A_ci": q(1), "A_ons": pred, "A_ons_ci": q(2),
                  "peak": p, "Gpeak": float(gp), "Gpeak_ci": q(3), "ratio_round1_form": r1, "ratio_round1_form_ci": q(4),
                  "sum_S_over_Speak": float(np.nansum(S[max(p, 0):] / S[max(p, 0)])) if S[max(p, 0)] > 0 else None}
    return res


def main():
    meta = pl.read_parquet(RR.R2 / "unit_meta.parquet")
    scopes = {
        "nudge_G51": (meta.filter((pl.col("goal_no") == 51) & (pl.col("n_calls_trim") > 0))["unit_id"].to_list(), "nudge"),
        "nudge_regimeI_II": (meta.filter(pl.col("regime").is_in(["I", "II"]))["unit_id"].to_list(), "nudge"),
        "human_regimeIII": (meta.filter(pl.col("regime") == "III")["unit_id"].to_list(), "human"),
        "human_regimeI": (meta.filter(pl.col("regime") == "I")["unit_id"].to_list(), "human"),
        "human_G04": (["4a", "4b", "4c", "4d"], "human"),
    }
    out = {}
    for name, (units, kind) in scopes.items():
        ev = []
        for u in units:
            r = unit_events(u, kind)
            if r:
                ev += r
        if not ev or not any(e["kicked"] for e in ev):
            out[name] = None
            continue
        out[name] = scope_result(ev, seed=len(name))
        print(name, out[name]["n_kicked"], {k: (round(out[name][k]["omega"], 3) if out[name].get(k) else None) for k in ("ya", "yt", "yc")}, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "kicks_r4.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
