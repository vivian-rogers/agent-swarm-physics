"""H89 period-native tests (exception (c): the transition is the object). Predictions: card and the NE29 / NE32 /
G51 READMEs (written 2026-10-04 20:35 UTC, before any native statistic).

  N1 NE29 (#31): newcomer 02-18 (agent 21), retirement of agent 0 (last active 02-18).
  N2 NE32 (#51): GPT-5.6 Sol / Terra / Luna (35, 36, 37) join 07-09 in isolated rooms; merge 07-10.
  N3 G51 growth: cumulative roster-migration shares over #51's non-holdout transitions.
Output: data/processed/H89-price-equation-culture/natives/natives.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h89lib as L  # noqa: E402

OUT = L.DATA / "natives"
NEWCOMERS_NE32 = [35, 36, 37]
VETERAN_CUTOFF = "2026-07-09"   # veterans: active in #51 before NE32


def tr_share(r: dict, tag: str, grp: str) -> float:
    dz = r[tag]["dz"]
    den = L.xf(dz, dz)
    return L.xf(L.group_vec(r[tag]["terms"], grp), dz) / den if den > 0 else np.nan


def tr_rho(r: dict, tag: str) -> float:
    dz = r[tag]["dz"]
    n = (dz[1] @ dz[1]) * (dz[2] @ dz[2])
    return float(dz[1] @ dz[2] / np.sqrt(n)) if n > 0 else np.nan


def agent_mig_share(P: L.Period, d0: int, d1: int, agents: list[int], tag: str) -> tuple[float, float]:
    """Share of the transition's change carried by the entry of `agents` (their Mig_in contributions)."""
    r, _ = L.price_transition(P, d0, d1, tags=[tag])
    dz = r[tag]["dz"]
    A1 = P.active[d1]
    S = sorted(set(P.active[d0]) & set(A1))
    m1 = np.stack([L._z(P, tag, S, d1, h).mean(0) for h in range(3)])
    contrib = sum(np.stack([P.traits[tag][P.keys[(a, d1)], h] for h in range(3)]) - m1 for a in agents) / len(A1)
    den = L.xf(dz, dz)
    return (L.xf(contrib, dz) / den if den > 0 else np.nan), tr_rho(r, tag), L.xf(contrib, dz), den


def xcos(pairs: list[tuple[np.ndarray, np.ndarray]]) -> float:
    num = sum(L.xf(a, b) for a, b in pairs)
    na = sum(L.xf(a, a) for a, _ in pairs)
    nb = sum(L.xf(b, b) for _, b in pairs)
    return float(num / np.sqrt(na * nb)) if na > 0 and nb > 0 else np.nan


def n1(ad, adop, kick) -> dict:
    P31 = L.load_period(31, ad, adop, kick)
    P30 = L.load_period(30, ad, adop, kick)
    d_of = {d: i for i, d in enumerate(P31.days)}
    out = {"transitions": {}}
    ok_a = True
    for label, day in (("entry 02-18", "2026-02-18"), ("retirement 02-19", "2026-02-19")):
        d1 = d_of[day]
        d0 = max(d for d in P31.active if d < d1)
        r, dg = L.price_transition(P31, d0, d1)
        row = dict(d0=P31.days[d0], d1=day, nI_roster=dg["nI_roster"], nE_roster=dg["nE_roster"])
        for tag in L.TRAITS:
            row[f"{tag}.s_mig_roster"] = tr_share(r, tag, "mig_roster")
            row[f"{tag}.s_mig"] = tr_share(r, tag, "mig")
            row[f"{tag}.rho"] = tr_rho(r, tag)
        row["a_pass"] = bool(row["style.s_mig_roster"] > row["content_bge.s_mig_roster"])
        ok_a &= row["a_pass"]
        out["transitions"][label] = row
    # N1-b: stayers' change energy at the retirement transition vs placebo transitions of #30 and #31
    vals = []
    for P in (P30, P31):
        for d0, d1 in L.transitions(P):
            r, _ = L.price_transition(P, d0, d1, tags=["content_bge"])
            st = L.group_vec(r["content_bge"]["terms"], "sel") + L.group_vec(r["content_bge"]["terms"], "trans")
            vals.append((P.goal, P.days[d1], L.xf(st, st)))
    ret = [v for g, d, v in vals if g == 31 and d == "2026-02-19"][0]
    plc = [v for g, d, v in vals if not (g == 31 and d == "2026-02-19")]
    pct = float(np.mean([p < ret for p in plc]))
    out["b"] = dict(retirement_energy=ret, placebo_energies=[(g, d, v) for g, d, v in vals], percentile=pct,
                    n_placebo=len(plc), pass_=pct < 0.9)
    n_ok = int(ok_a) + int(pct < 0.9)
    out["verdict"] = "supported" if n_ok == 2 else ("failed" if n_ok == 0 else "mixed")
    t = out["transitions"]
    e, rt = t["entry 02-18"], t["retirement 02-19"]
    out["text"] = (
        f"**{out['verdict']}.** Single-transition energy shares (cross-fitted between message halves).\n\n"
        "| Prediction | Observed | Reference | Verdict |\n| --- | --- | --- | --- |\n"
        f"| N1-a entry (02-17 → 02-18, Sonnet 4.6 joins): style roster share > content | style {e['style.s_mig_roster']:+.3f}, content bge {e['content_bge.s_mig_roster']:+.3f}, gte {e['content_gte.s_mig_roster']:+.3f}, conventions {e['conv.s_mig_roster']:+.3f} (ρ_Δ style {e['style.rho']:.2f}, content {e['content_bge.rho']:.2f}) | 0 | {'pass' if e['a_pass'] else 'fail'} |\n"
        f"| N1-a retirement (02-18 → 02-19, Claude 3.7 Sonnet leaves): style roster share > content | style {rt['style.s_mig_roster']:+.3f}, content bge {rt['content_bge.s_mig_roster']:+.3f}, gte {rt['content_gte.s_mig_roster']:+.3f}, conventions {rt['conv.s_mig_roster']:+.3f} (ρ_Δ style {rt['style.rho']:.2f}, content {rt['content_bge.rho']:.2f}) | 0 | {'pass' if rt['a_pass'] else 'fail'} |\n"
        f"| N1-b stayers' content change at the retirement not above placebo | percentile {pct:.2f} among {len(plc)} placebo transitions of #30–#31 | < 0.9 | {'pass' if pct < 0.9 else 'fail'} |\n")
    out["scorecard"] = ("E (interventional): a single-carrier loss and a single join, each one transition; "
                        "style vs content migration shares at the event. G: roster dates from `roster`.")
    return out


def n2(ad, adop, kick) -> dict:
    P = L.load_period(51, ad, adop, kick)
    d_of = {d: i for i, d in enumerate(P.days)}
    ds = sorted(P.active)
    first = {a: min(d for d in ds if a in P.active[d]) for a in NEWCOMERS_NE32}
    out = {"first_active": {a: P.days[d] for a, d in first.items()}}
    # N2-a: per newcomer entry transition, its own Mig_in contribution share; pooled over the three entries
    rows = []
    for a, d1 in first.items():
        d0 = max(d for d in ds if d < d1)
        row = dict(agent=a, d0=P.days[d0], d1=P.days[d1])
        for tag in L.TRAITS:
            row[f"{tag}.share"], row[f"{tag}.rho"], row[f"{tag}.num"], row[f"{tag}.den"] = \
                agent_mig_share(P, d0, d1, [a], tag)
        rows.append(row)
    out["entries"] = rows
    # energy pooling over the three entry transitions (sum of numerators / sum of denominators), as in the card's
    # energy share; the per-entry ratio is undefined where a transition's cross-fitted energy is <= 0
    pooled = {tag: float(sum(r[f"{tag}.num"] for r in rows) / sum(r[f"{tag}.den"] for r in rows)) for tag in L.TRAITS}
    out["pooled_entry_share"] = pooled
    a_pass = pooled["style"] > pooled["content_bge"]
    # N2-b: newcomer change from first active day to its next active day, toward the veterans' first-day centroid
    vets_all = {a for d in ds if P.days[d] < VETERAN_CUTOFF for a in P.active[d]}
    cos = {}
    for tag in ("content_bge", "content_gte", "style"):
        pairs = []
        for a, d0 in first.items():
            nxt = [d for d in ds if d > d0 and a in P.active[d]]
            if not nxt:
                continue
            d1 = nxt[0]
            vets = [v for v in P.active[d0] if v in vets_all]
            z0 = np.stack([P.traits[tag][P.keys[(a, d0)], h] for h in range(3)])
            z1 = np.stack([P.traits[tag][P.keys[(a, d1)], h] for h in range(3)])
            vc = np.stack([L._z(P, tag, vets, d0, h).mean(0) for h in range(3)])
            pairs.append((z1 - z0, vc - z0))
        cos[tag] = xcos(pairs)
    # descriptive placebo: veterans' change over the same transitions toward the newcomer
    out["cos"] = cos
    b_pass = bool(cos["content_bge"] > 0 and cos["content_bge"] > cos["style"])
    # mechanism: newcomer social weight lambda on the first two active days
    lam = {}
    for a, d0 in first.items():
        for d in [d0] + [d for d in ds if d > d0 and a in P.active[d]][:1]:
            dprev = max([x for x in ds if x < d], default=None)
            if dprev is None:
                continue
            S = sorted(set(P.active[dprev]) & set(P.active[d]))
            if a not in S:
                lam[f"{a}@{P.days[d]}"] = None
                continue
            al_s, al_n, al_u, _ = L.parentage(P, d, S)
            lam[f"{a}@{P.days[d]}"] = float(1 - al_s[S.index(a), S.index(a)])
    out["lambda"] = lam
    n_ok = int(a_pass) + int(b_pass)
    out["a_pass"], out["b_pass"] = bool(a_pass), b_pass
    out["verdict"] = "supported" if n_ok == 2 else ("failed" if n_ok == 0 else "mixed")
    ent = "; ".join(f"agent {r['agent']} into {r['d1']}: style {r['style.share']:+.3f} (ρ {r['style.rho']:.2f}), content {r['content_bge.share']:+.3f}"
                    for r in rows)
    out["text"] = (
        f"**{out['verdict']}.** Only GPT-5.6 Terra (agent 37) passes the activity threshold on 07-09; Luna (36) and Sol (35) first pass it on {P.days[first[36]]} and {P.days[first[35]]}, so their first active days replace 07-09 (pre-registered fallback). Only Terra's next day is the merge day.\n\n"
        "| Prediction | Observed | Reference | Verdict |\n| --- | --- | --- | --- |\n"
        f"| N2-a newcomer entry share: style > content | energy-pooled over the three entries: style {pooled['style']:+.3f}, content bge {pooled['content_bge']:+.3f}, gte {pooled['content_gte']:+.3f}, conventions {pooled['conv']:+.3f} ({ent}) | 0 | {'pass' if a_pass else 'fail'} |\n"
        f"| N2-b newcomers move toward the veterans: content cos > 0 and > style cos | cross-fitted cosine: content bge {cos['content_bge']:+.2f}, gte {cos['content_gte']:+.2f}; style {cos['style']:+.2f} | 0 | {'pass' if b_pass else 'fail'} |\n"
        f"\nMechanism (descriptive): newcomer social weight λ on its first two active days: "
        + ", ".join(f"{k} {v:.2f}" if v is not None else f"{k} –" for k, v in lam.items()) + ".\n")
    out["scorecard"] = ("E (interventional): isolation then merge switches the newcomers' in-cone parentage; only one "
                        "newcomer is active across the merge. G: roster and room dates from `roster` and the NE catalog.")
    return out


def n3(ad, adop, kick) -> dict:
    P = L.load_period(51, ad, adop, kick)

    def f(Q):
        res, _ = L.run_period(Q)
        o = {}
        for tag in L.TRAITS:
            c = L.shares(res, tag, cumulative=True)
            e = L.shares(res, tag)
            o[f"{tag}.cum_roster"] = c["s_mig_roster"]
            o[f"{tag}.cum_mig"] = c["s_mig"]
            o[f"{tag}.cum_rho"] = c["rho"]
            o[f"{tag}.e_sel"] = e["s_sel"]
            o[f"{tag}.e_mig_roster"] = e["s_mig_roster"]
            o[f"{tag}.e_mig"] = e["s_mig"]
            # magnitudes of the cumulative vectors relative to the net change (cross-fitted, descriptive)
            dz = sum(r[tag]["dz"] for r in res)
            dd = L.xf(dz, dz)
            for g in ("mig_roster", "mig", "trans", "sel"):
                v = sum(L.group_vec(r[tag]["terms"], g) for r in res)
                o[f"{tag}.cum_mag_{g}"] = L.xf(v, v) / dd if dd > 0 else np.nan
            o[f"{tag}.cum_s_trans"] = c["s_trans"]
            o[f"{tag}.cum_s_sel"] = c["s_sel"]
        return o
    full = f(P)
    agents = sorted({a for v in P.active.values() for a in v})
    vals = [f(P.drop({a})) for a in agents]
    se = {}
    for k in full:
        v = np.array([x[k] for x in vals], dtype=float)
        v = v[np.isfinite(v)]
        se[k] = float(np.sqrt((len(v) - 1) / len(v) * ((v - v.mean()) ** 2).sum()))
    a_pass = full["style.cum_roster"] >= 0.5
    b_pass = full["content_bge.cum_roster"] < full["style.cum_roster"] and full["content_gte.cum_roster"] < full["style.cum_roster"]
    c_pass = all(abs(full[f"{t}.e_sel"]) <= 0.2 for t in L.TRAITS)
    n_ok = int(a_pass) + int(b_pass)
    verdict = "supported" if n_ok == 2 else ("failed" if n_ok == 0 else "mixed")

    def ci(k):
        return f"{full[k]:+.3f} [{full[k] - 1.96 * se[k]:+.3f}, {full[k] + 1.96 * se[k]:+.3f}]"
    text = (f"**{verdict}** (native N3). 44 transitions, 07-06 → 09-04; 11 joins (9 roster-entry transitions).\n\n"
            "| Prediction | Observed (cumulative cross-fitted share; jackknife 95% CI) | Reference | Verdict |\n| --- | --- | --- | --- |\n"
            f"| N3-a style roster-migration share ≥ 0.5 | {ci('style.cum_roster')} (all migration {ci('style.cum_mig')}; ρ_cum {full['style.cum_rho']:.2f}) | S0 static agents: 0.72 | {'pass' if a_pass else 'fail'} |\n"
            f"| N3-b content roster share < style's | content bge {ci('content_bge.cum_roster')}, gte {ci('content_gte.cum_roster')}; conventions {ci('conv.cum_roster')} | style | {'pass' if b_pass else 'fail'} |\n"
            f"| N3-c energy \\|s_Sel\\| ≤ 0.2 (reported) | content {full['content_bge.e_sel']:+.3f}, style {full['style.e_sel']:+.3f}, conventions {full['conv.e_sel']:+.3f} | 0.2 | {'pass' if c_pass else 'fail'} |\n")
    return dict(full=full, se=se, verdict=verdict, a_pass=bool(a_pass), b_pass=bool(b_pass), c_pass=bool(c_pass),
                text=text)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ad = pl.read_parquet(L.DATA / "agent_days.parquet")
    adop = pl.read_parquet(L.DATA / "adoptions.parquet")
    kick = np.load(L.DATA / "kickoff.npz")
    out = {"NE29": n1(ad, adop, kick), "NE32": n2(ad, adop, kick), "N3": n3(ad, adop, kick)}
    (OUT / "natives.json").write_text(json.dumps(out, indent=1, default=float))
    for k, v in out.items():
        print(f"== {k}: {v['verdict']}\n{v['text']}")


if __name__ == "__main__":
    main()
