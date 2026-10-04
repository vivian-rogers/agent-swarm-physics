"""H103 replication and natives on real (non-holdout) data.

O1 kickoff-remanence clock comparison per eligible goal period; O2 previous-centroid series per transition;
O3 two-time night step per period unit. Natives: N1 G51 NE43 (before/after 2026-08-05), N2 reset clock (regime III
units), N3 G04/G06 village-off midday breaks.
Usage: uv run python hypotheses/H103-nights-demagnetize/analysis/run.py [--models ...] [--parts o1,o2,o3,natives]
Writes data/processed/H103-nights-demagnetize/results/*.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h103lib as L  # noqa: E402
from embed_models import agent_vectors  # noqa: E402

RES = L.DATA / "results"


def j(x):
    return json.dumps(x, indent=1, default=lambda o: None if (isinstance(o, float) and not np.isfinite(o)) else float(o))


def o1(S, n_boot=200, slots=True):
    out = {}
    for rec in S.periods.to_dicts():
        r = L.o1_period(S, rec, n_boot=n_boot, seed=rec["goal_no"], slots=slots)
        r.pop("series_full", None)
        out[f"G{rec['goal_no']:02d}"] = r
        print("O1", rec["goal_no"], r["winner"], r["verdict"], flush=True)
    return out


def card_o1(res):
    dec = {k: r for k, r in res.items() if r["verdict"] != "descriptive"}
    lam = [(np.log(max(r["nested"]["lam"], 1e-3)), (np.log(max(r["lam_ci"][1], 1e-3)) - np.log(max(r["lam_ci"][0], 1e-3))) / 3.92)
           for r in dec.values() if np.all(np.isfinite(r["lam_ci"]))]
    sn = [(r["steps"]["S_N"] - r["steps"]["S_mid"], (r["SN_minus_Smid_ci"][1] - r["SN_minus_Smid_ci"][0]) / 3.92)
          for r in res.values() if np.all(np.isfinite(r["SN_minus_Smid_ci"])) and np.isfinite(r["steps"]["S_N"])
          and np.isfinite(r["steps"]["S_mid"])]
    return {"n_periods": len(res), "n_with_decay": len(dec),
            "winner_share_decay": {c: float(np.mean([r["winner"] == c for r in dec.values()])) if dec else None
                                   for c in L.CLOCKS},
            "share_H_le_N_decay": float(np.mean([r["sse"]["H"] <= r["sse"]["N"] for r in dec.values()])) if dec else None,
            "share_H_le_N_all": float(np.mean([r["sse"]["H"] <= r["sse"]["N"] for r in res.values()])),
            "winner_share_all": {c: float(np.mean([r["winner"] == c for r in res.values()])) for c in L.CLOCKS},
            "log_lambda_RE": L.re_mean([a for a, b in lam], [b for a, b in lam]),
            "SN_minus_Smid_RE": L.re_mean([a for a, b in sn], [b for a, b in sn]),
            "verdicts": {v: sum(r["verdict"] == v for r in res.values()) for v in ("supported", "failed", "mixed", "descriptive")}}


# ------------------------------------------------------------------------------------------- O2
def o2(S, n_boot=200):
    ad = pl.read_parquet(L.OUT / "embeddings/agent_day.parquet").with_row_index("ri")
    AV = L.unit(agent_vectors("day", S.model, S.variant).astype(np.float32))
    days = S.days
    elig = sorted(days["goal_no"].unique().to_list())
    ad = ad.filter(pl.col("pt_date").is_in(days["pt_date"].to_list()) & ((pl.col("n_chat") + pl.col("n_intent")) >= 3)
                   & ~pl.col("agent").is_in([19, 28, 30]))
    def late(g, reg):
        dd = days.filter((pl.col("goal_no") == g) & (pl.col("regime") == reg)).sort("pt_date")["pt_date"].to_list()[-3:]
        sub = ad.filter(pl.col("pt_date").is_in(dd))
        return sub["agent"].to_numpy(), AV[sub["ri"].to_numpy()]
    def lo_dirs(A, V, agents):
        tot = V.sum(0)
        return {a: L.unit(tot - V[A == a].sum(0)) for a in agents}
    out = {}
    for rec in S.periods.to_dicts():
        P, reg = rec["goal_no"], rec["regime"]
        if P - 1 not in elig:
            continue
        pre_reg = days.filter(pl.col("goal_no") == P - 1).sort("pt_date")["regime"].to_list()
        if not pre_reg or pre_reg[-1] != reg:
            continue
        plac = [q for q in elig if q not in range(P - 2, P + 2)
                and days.filter((pl.col("goal_no") == q) & (pl.col("regime") == reg)).height >= 1]
        if len(plac) < 3:
            continue
        fg = S.goals.filter((pl.col("goal_no") == P) & pl.col("kind").is_in(["kickoff", "goal", "kickoff_room"]))["gid"]
        F = S.G[reg][fg.to_list()]
        qm, _ = np.linalg.qr(F.T.astype(np.float64)); qm = qm.astype(np.float32)
        perp = lambda v: v - (v @ qm) @ qm.T
        w = L.period_windows(S, rec)
        agents = sorted(set(w["agent"].to_list()))
        A0, V0 = late(P - 1, reg)
        old = lo_dirs(A0, V0, agents)
        pls = []
        for q in plac:
            Aq, Vq = late(q, reg)
            if len(Vq):
                pls.append(lo_dirs(Aq, Vq, agents))
        def scorer(ww, rows):
            ag = ww["agent"].to_numpy(); X = S.V[rows]
            eo = L.unit(perp(np.stack([old[a] for a in ag])))
            s0 = (X * eo).sum(1)
            sq = np.stack([(X * L.unit(perp(np.stack([pl_[a] for a in ag])))).sum(1) for pl_ in pls], 1)
            return s0 - np.median(sq, 1)
        r = L.o1_period(S, rec, n_boot=n_boot, seed=P, scorer=scorer)
        out[f"G{P:02d}"] = {k: r[k] for k in ("goal_no", "regime", "n_windows", "n_agents", "winner", "sse", "nested",
                                               "steps", "level_day1", "level_day1_ci", "dA_best_ci", "lam_ci",
                                               "p_N_beats_H", "verdict", "series", "rate", "dA")}
        out[f"G{P:02d}"]["n_placebos"] = len(pls)
        print("O2", P, r["level_day1"], r["level_day1_ci"], r["winner"], flush=True)
    return out


# ------------------------------------------------------------------------------------------- O3
def o3_units(S):
    pu = pl.read_parquet(L.OUT / "period_units.parquet")
    have = S.days.group_by("unit_id").agg(pl.len().alias("n"), pl.col("regime").n_unique().alias("nr"))
    ok = have.filter((pl.col("n") >= 3) & (pl.col("nr") == 1))["unit_id"].to_list()
    return [u for u in pu["unit_id"].to_list() if u in ok]


def o3(S, n_boot=200, with_reset=False, units=None):
    out = {}
    for u in units or o3_units(S):
        w = S.w.with_row_index("ri").filter(pl.col("unit_id") == u)
        if w.height < 30:
            continue
        p = L.unit_pairs(S, w)
        if p is None or (p["N"] == 1).sum() < 20:
            continue
        reg = w["regime"][0]
        f = L.o3_fit(p, n_boot=n_boot, seed=len(u), with_reset=with_reset and reg == "III")
        f.update({"unit": u, "goal_no": int(w["goal_no"][0]), "regime": reg,
                  "first_day": w["pt_date"].min(), "last_day": w["pt_date"].max()})
        out[u] = f
        print("O3", u, {k: round(f[k]["est"], 4) for k in ("beta_N", "beta_G", "beta_gap") if np.isfinite(f[k]["est"])},
              flush=True)
    return out


def card_o3(res, key="beta_N"):
    v = [r[key] for r in res.values() if np.isfinite(r[key]["est"]) and np.isfinite(r[key]["se"])]
    return {"RE": L.re_mean([x["est"] for x in v], [x["se"] for x in v]),
            "n_neg_ci": int(sum(x["hi"] < 0 for x in v)), "n_pos_ci": int(sum(x["lo"] > 0 for x in v)),
            "n_neg_point": int(sum(x["est"] < 0 for x in v)), "k": len(v),
            "by_regime": {reg: L.re_mean([r[key]["est"] for r in res.values() if r["regime"] == reg and np.isfinite(r[key]["se"])],
                                         [r[key]["se"] for r in res.values() if r["regime"] == reg and np.isfinite(r[key]["se"])])
                          for reg in ("I", "II", "III")}}


# ------------------------------------------------------------------------------------------- natives
def n1_ne43(S, n_boot=200):
    w51 = S.w.with_row_index("ri").filter(pl.col("goal_no") == 51)
    halves = {"before": w51.filter(pl.col("pt_date") <= "2026-08-04"), "after": w51.filter(pl.col("pt_date") >= "2026-08-05")}
    res = {}
    for k, w in halves.items():
        p = L.unit_pairs(S, w)
        res[k] = L.o3_fit(p, n_boot=n_boot, seed=43)
    d = res["after"]["beta_N"]["est"] - res["before"]["beta_N"]["est"]
    se = np.hypot(res["after"]["beta_N"]["se"], res["before"]["beta_N"]["se"])
    res["delta_beta_N"] = {"est": d, "lo": d - 1.96 * se, "hi": d + 1.96 * se, "se": se}
    res["verdict"] = "supported" if res["delta_beta_N"]["lo"] <= 0 <= res["delta_beta_N"]["hi"] else "failed"
    return res


def n2_reset(S, n_boot=200):
    units = [u for u in o3_units(S) if S.w.filter(pl.col("unit_id") == u)["regime"][0] == "III"]
    res = o3(S, n_boot=n_boot, with_reset=True, units=units)
    v = [r["beta_R"] for r in res.values() if "beta_R" in r and np.isfinite(r["beta_R"]["se"])]
    re_ = L.re_mean([x["est"] for x in v], [x["se"] for x in v])
    verdict = "supported" if (re_["lo"] <= 0 <= re_["hi"] and abs(re_["est"]) < 0.005) else (
        "failed" if re_["hi"] < 0 else "mixed")
    return {"units": res, "beta_R_RE": re_, "verdict": verdict}


def n3_midday(S):
    o = pl.read_parquet(L.OUT / "outages_fixed/outages.parquet").filter(
        pl.col("pt_date").is_in(["2025-06-18", "2025-06-29"]) & pl.col("village_off") & (pl.col("dur_min") >= 60))
    out = {}
    for ev in o.iter_rows(named=True):
        d = ev["pt_date"]
        g = ev["goal_no"]
        w = S.w.with_row_index("ri").filter(pl.col("goal_no") == g)
        days = sorted(w["pt_date"].unique().to_list())
        k = days.index(d) if d in days else None
        if k is None:
            continue
        sel = days[max(0, k - 1): k + 2]
        ww = w.filter(pl.col("pt_date").is_in(sel)).sort("agent", "t_mid")
        rows = []
        for (a,), wa in ww.group_by(["agent"]):
            X = S.V[wa["ri"].to_numpy()]; t = wa["t_mid"].to_numpy(); dd = wa["pt_date"].to_numpy()
            h = wa["hcum"].to_numpy(); di = wa["day_idx"].to_numpy()
            C = X @ X.T
            for i in range(len(t)):
                for jj in range(i + 1, len(t)):
                    if dd[i] == d and dd[jj] == d:
                        ts, te = np.datetime64(ev["t_start"].replace(tzinfo=None)), np.datetime64(ev["t_end"].replace(tzinfo=None))
                        across = (t[i] < ts) and (t[jj] > te)
                        dh = (h[jj] - h[i]) - (ev["dur_min"] / 60 if across else 0)
                        rows.append(("across_break" if across else "same_side", dh, C[i, jj]))
                    elif di[jj] - di[i] == 1:
                        rows.append(("cross_night", h[jj] - h[i], C[i, jj]))
        df = pl.DataFrame(rows, schema=["kind", "dH", "C"], orient="row")
        summ = df.group_by("kind").agg(pl.col("C").mean().alias("C_mean"), pl.col("C").std().alias("C_sd"),
                                       pl.col("dH").median().alias("dH_med"), pl.len().alias("n"))
        # matched-lag same-day comparison: same-side pairs with dH within the across-break dH range
        ab = df.filter(pl.col("kind") == "across_break")
        if ab.height:
            lo, hi = ab["dH"].quantile(0.1), ab["dH"].quantile(0.9)
            ss = df.filter((pl.col("kind") == "same_side") & pl.col("dH").is_between(lo, hi))
            cn = df.filter((pl.col("kind") == "cross_night") & pl.col("dH").is_between(lo, hi))
            matched = {"same_side_matched": float(ss["C"].mean()) if ss.height else None, "n_same": ss.height,
                       "cross_night_matched": float(cn["C"].mean()) if cn.height else None, "n_cross": cn.height,
                       "across_break": float(ab["C"].mean()), "n_across": ab.height}
        else:
            matched = None
        out[d] = {"goal_no": g, "dur_min": ev["dur_min"], "summary": summ.to_dicts(), "matched": matched}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="bge_small,gte_modernbert")
    ap.add_argument("--parts", default="o1,o2,o3,natives")
    ap.add_argument("--variant", default="style_resid")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    parts = a.parts.split(",")
    for model in a.models.split(","):
        S = L.Store(model, a.variant)
        tag = f"{model}_{a.variant}"
        cardp = RES / f"card_{tag}.json"
        card = json.loads(cardp.read_text()) if cardp.exists() else {}
        if "o1" in parts:
            r = o1(S); (RES / f"o1_{tag}.json").write_text(j(r)); card["o1"] = card_o1(r)
            print("card o1", j(card["o1"]), flush=True)
        if "o1noslot" in parts:
            r = o1(S, slots=False); (RES / f"o1noslot_{tag}.json").write_text(j(r)); card["o1_noslot"] = card_o1(r)
        if "o2" in parts:
            r = o2(S); (RES / f"o2_{tag}.json").write_text(j(r))
            card["o2"] = {"n": len(r), "n_day1_pos": int(sum((x["level_day1_ci"][0] or -1) > 0 for x in r.values())),
                          "verdicts": {v: sum(x["verdict"] == v for x in r.values()) for v in ("supported", "failed", "mixed", "descriptive")}}
            print("card o2", j(card["o2"]), flush=True)
        if "o3" in parts:
            r = o3(S); (RES / f"o3_{tag}.json").write_text(j(r))
            card["o3"] = {k: card_o3(r, k) for k in ("beta_N", "beta_G", "beta_gap")}
            print("card o3", j(card["o3"]), flush=True)
        if "natives" in parts:
            nat = {"NE43": n1_ne43(S), "NE41": n2_reset(S), "midday": n3_midday(S)}
            (RES / f"natives_{tag}.json").write_text(j(nat))
            card["natives"] = {"NE43": {k: nat["NE43"][k] for k in ("delta_beta_N", "verdict")},
                               "NE41": {k: nat["NE41"][k] for k in ("beta_R_RE", "verdict")},
                               "midday": {d: v["matched"] for d, v in nat["midday"].items()}}
            print("card natives", j(card["natives"]), flush=True)
        cardp.write_text(j(card))


if __name__ == "__main__":
    main()
