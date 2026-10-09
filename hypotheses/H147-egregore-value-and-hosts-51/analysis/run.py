"""H147 round 1 on exploration data (#51, 07-06 -> 09-04; 51m reserved and absent): wipe value (O1), hub-loss beta
(O2), operator-action prevalence and colonial A (O3), host relation (O4), and P5, per memeplex of H145.

Patterns: H145's frozen memeplexes (data/processed/H145-ideology-egregores-51/memeplexes.json) over H145's element
table. Element events (agent, t, eid) are rebuilt with memeplex.build_elements (H145's parameters) and checked
key-for-key against H145's elements.parquet; they are cached in data/processed/H147-.../elem_events.parquet.

Estimators: analysis/h147lib.py (Amendments A1-A3 in the card). Pseudo-patterns: frequency-matched element sets
(+-25% events, +-1 host agents; draw_pseudo), the same for every statistic. Colonial A: individuality.krakauer_discrete
on memeplex.pattern_state symbols at 2 h with E = (bin in day) x (any human, operator or relayed-human message in the
bin) (a coarse form of H145's E: e1 + e2; H147's own computation, used for P3 and P5 only).

Usage: uv run python hypotheses/H147-egregore-value-and-hosts-51/analysis/run.py [--n-pseudo 100] [--B 200]
Output: data/processed/H147-egregore-value-and-hosts-51/results/
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h147lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

C = L.C
import memeplex as MP  # noqa: E402  (infra/shared)
import individuality as IND  # noqa: E402  (infra/shared)

RES = C.OUT / "results"
T0 = time.time()
CI_FORM = "boot"          # wipe CI form for b_rate fixed by the synthetic check (card, Round 1, Amendment A1)
OTH_FORM = "comb"         # CI form for the others' response b_oth (size 0.05 in the synthetic check)
HOST_FORM = "A2"          # host relation form fixed by the synthetic check (Amendment A2)
HUB_SHARE_MIN = 0.05      # beta is reported for a pattern only if the lost agent held >= 5% of its expressions before
DIST_MAX, HUB_MIN = 0.5, 0.6


def log(*a):
    print(f"[{time.time() - T0:7.0f}s]", *a, flush=True)


# ================================================================================================ inputs
def element_events() -> tuple[pl.DataFrame, pl.DataFrame]:
    p = C.OUT / "elem_events.parquet"
    tab = pl.read_parquet(C.H145_OUT / "elements.parquet")
    if p.exists():
        ev = pl.read_parquet(p)
    else:
        el = MP.build_elements(C.GOAL, k=80, model="bge", seed=0)
        mine = el.table.select("eid", "key").sort("eid")
        theirs = tab.select("eid", "key").sort("eid")
        assert mine.equals(theirs), "element table differs from H145's frozen elements.parquet"
        ev = el.events.with_columns(pl.col("agent").cast(pl.Int16), pl.col("eid").cast(pl.Int32))
        ev.write_parquet(p, compression="zstd")
        C.provenance("elem_events", "hypotheses/H147-egregore-value-and-hosts-51/analysis/run.py",
                     ["H145 elements.parquet (key check)", "memeplex.build_elements (k 80, bge, seed 0)"],
                     params={"k": 80, "model": "bge", "seed": 0}, extra={"rows": ev.height})
    ev = ev.filter(pl.col("t").dt.date().cast(pl.String) <= C.LAST)
    return ev, tab


def load_patterns() -> list[dict]:
    mj = json.loads((C.H145_OUT / "memeplexes.json").read_text())
    pats = []
    for i, m in enumerate(mj["memeplexes"]):
        pats.append({"id": m.get("id", f"K{i:02d}"), "label": m.get("label"), "candidate": m.get("candidate"),
                     "eids": [int(e) for e in m["elements"]], "h_K": m.get("h_K"), "top_host": m.get("top_host"),
                     "n_hosts": m.get("n_hosts"), "labs": m.get("labs"), "source": "H145"})
    for i, m in enumerate(mj.get("role_text_patterns", []) or []):
        pats.append({"id": m.get("id", f"R{i:02d}"), "label": m.get("label"), "candidate": "role_text",
                     "eids": [int(e) for e in m["elements"]], "h_K": m.get("h_K"), "top_host": m.get("top_host"),
                     "n_hosts": m.get("n_hosts"), "labs": m.get("labs"), "source": "H145 role-text control"})
    return pats


class Store:
    """Element events in time order with per-element index arrays (fast Hits for any element set)."""

    def __init__(self, ev: pl.DataFrame, sk: L.Skeleton):
        ev = ev.sort("t")
        self.agent = ev["agent"].to_numpy().astype(np.int16)
        self.t = ev["t"].dt.epoch("us").to_numpy()
        self.e = ev["eid"].to_numpy().astype(np.int32)
        b = C.assign_bins(ev.select("t"))["bin"].fill_null(-1).to_numpy().astype(np.int32)
        self.bin = b
        o = np.argsort(self.e, kind="stable")
        self.by_e = np.split(o, np.flatnonzero(np.diff(self.e[o])) + 1)
        self.e_ids = self.e[[x[0] for x in self.by_e]]
        self.idx = {int(e): x for e, x in zip(self.e_ids, self.by_e)}
        self.freq = {int(e): len(x) for e, x in zip(self.e_ids, self.by_e)}
        self.hosts = {int(e): int(len(np.unique(self.agent[x]))) for e, x in zip(self.e_ids, self.by_e)}

    def hits(self, eids) -> L.Hits:
        ix = np.concatenate([self.idx[int(e)] for e in eids if int(e) in self.idx]) if len(eids) else np.zeros(0, int)
        ix = np.sort(ix)
        return L.Hits(self.agent[ix], self.t[ix], self.e[ix], self.bin[ix])


# ================================================================================================ colonial A
class Colonial:
    def __init__(self, ev: pl.DataFrame, nE: int):
        self.bins = C.mbins()
        self.panel = MP.make_panel(ev, self.bins, nE)
        exo = pl.read_parquet(C.H145_OUT / "exo.parquet").filter(pl.col("src").is_in(["human", "relayed"])
                                                                 | (pl.col("kind").cast(pl.String) == "nudge"))
        _, b = self.bins.locate(np.full(exo.height, self.bins.agents[0]), exo["t"].to_numpy())
        x = np.zeros(self.bins.nB, np.int64)
        x[b[b >= 0]] = 1
        self.E = self.bins.bin_in_day.astype(np.int64) * 2 + x
        self.Ke = int(self.bins.bin_in_day.max() + 1) * 2
        self.dob = self.bins.day_of_bin
        self.b0 = IND.transitions(self.dob)

    def sym(self, K):
        return MP.pattern_state(self.panel, K, m=L.M_HOST)["sym"]

    def A(self, K, days_mask: np.ndarray | None = None, sym=None) -> dict:
        s = self.sym(K) if sym is None else sym
        b0 = self.b0 if days_mask is None else self.b0[days_mask[self.dob[self.b0]]]
        r = IND.krakauer_discrete(s[b0 + 1], s[b0], self.E[b0], self.dob[b0], 13, self.Ke)
        return {k: r.get(k) for k in ("ok", "A", "A_star", "nC", "NTIC", "n")}

    def A_boot(self, K, days_mask, B=200, seed=0) -> np.ndarray:
        s = self.sym(K)
        rng = np.random.default_rng(seed)
        days = np.flatnonzero(days_mask)
        b0 = self.b0[days_mask[self.dob[self.b0]]]
        by_day = {int(d): b0[self.dob[b0] == d] for d in days}
        out = []
        for _ in range(B):
            pick = rng.choice(days, len(days), replace=True)
            idx = np.concatenate([by_day[int(d)] for d in pick])
            dlab = np.concatenate([np.full(len(by_day[int(d)]), j) for j, d in enumerate(pick)])
            r = IND.krakauer_discrete(s[idx + 1], s[idx], self.E[idx], dlab, 13, self.Ke)
            out.append(r["A"] if r.get("ok") else np.nan)
        return np.array(out, float)


# ================================================================================================ per pattern
def wipe_block(sk, store, K, pseudo, B, seed):
    h = store.hits(K)
    wf = L.wipe_frame(sk, h)
    v = L.value_fit(sk, wf)
    inf = L.info_fit(sk, wf, n_perm=100)
    bv, bi = L.boot_value_info(sk, wf, B=B, seed=seed)
    pv = {k: [] for k in L.VALUE_KEYS}
    pi_ = []
    for P in pseudo:
        wfp = L.wipe_frame(sk, store.hits(P))
        vp = L.value_fit(sk, wfp)
        for k in L.VALUE_KEYS:
            pv[k].append(vp[k])
        pi_.append(L.info_fit(sk, wfp, n_perm=20)["I_K"])
    out = {"n_host_events": v["n_host_events"], "n_F": v["n_F"], "n_P": v["n_P"], "n_rate_events": v["n_rate_events"]}
    for k in L.VALUE_KEYS:
        out[k] = {"raw": float(np.exp(v[k]) - 1), **L.excess_ci(v[k], bv[k], pv[k])}
    ii = np.asarray(pi_, float)
    ii = ii[np.isfinite(ii)]
    med = float(np.median(ii)) if len(ii) else 0.0
    ci_i = L.q(bi - np.nanmean(bi) + inf["I_K"] - med)
    dV = out["b_rate"]["excess"]
    out["I"] = {"I_F": inf["I_F"], "I_P": inf["I_P"], "I_K_raw": inf["I_K"], "I_excess": float(inf["I_K"] - med),
                "ci": ci_i, "identified": bool(np.isfinite(ci_i[0]) and ci_i[0] > 0)}
    out["kappa"] = float(dV / out["I"]["I_excess"]) if out["I"]["identified"] else None
    return out


def host_block(sk, hp, store, K, pseudo, B, seed):
    HA = L.host_matrix(sk, store.hits(K))
    res = {}
    for form, act in (("A2", True), ("card", False)):
        est = L.host_fit(hp, HA, activity=act)
        ps = [L.host_fit(hp, L.host_matrix(sk, store.hits(P)), activity=act, outcomes=("commits", "align_bge"))
              for P in pseudo]
        pc = np.array([p["commits"] for p in ps], float)
        pa = np.array([p["align_bge"] for p in ps], float)
        bt = L.host_boot(hp, HA, B=B, seed=seed, activity=act)
        ci = {o: L.q(bt[o]) for o in bt}
        pmc, pma = float(np.nanmedian(pc)), float(np.nanmedian(pa))
        exc_c = (1 + est["commits"]) / (1 + pmc) - 1
        exc_a = est["align_bge"] - pma
        res[form] = {"est": est, "ci": ci, "pseudo_median": {"commits": pmc, "align_bge": pma},
                     "pseudo_q": {"commits": L.q(pc), "align_bge": L.q(pa)},
                     "excess": {"commits": float(exc_c), "align_bge": float(exc_a)},
                     "class_raw": L.classify(est["commits"], est["align_bge"], ci["commits"], ci["align_bge"]),
                     "class_point": L.classify(est["commits"], est["align_bge"], require_ci=False),
                     "class_exc": L.classify(exc_c, exc_a,
                                             [float((1 + x) / (1 + pmc) - 1) for x in ci["commits"]],
                                             [float(x - pma) for x in ci["align_bge"]])}
    return res


def event_blocks(sk, store, K, pat, col: Colonial):
    h = store.hits(K)
    out = {"hub": {}, "op": {}}
    for e in sk.sev["events"]:
        if e["kind"] == "hub_loss":
            r = L.hub_beta(sk, h, e["id"])
            rv = L.hub_beta(sk, h, e["id"], same_weekday=False)
            if not (np.isfinite(r["s"]) and r["s"] >= HUB_SHARE_MIN):
                out["hub"][e["id"]] = {"reported": False, "s": r["s"], "V_before": r["V_before"]}
                continue
            out["hub"][e["id"]] = {"reported": True, **{k: r[k] for k in ("V_before", "V_after", "own_before",
                                                                            "own_after", "L", "s", "L_own", "L_others",
                                                                            "L_placebo_mean", "n_placebo", "beta",
                                                                            "beta_band95", "exceeds_placebo95")},
                                   "beta_allwd": rv["beta"], "beta_band95_allwd": rv["beta_band95"],
                                   "exceeds_allwd": rv["exceeds_placebo95"], "n_placebo_allwd": rv["n_placebo"]}
        else:
            r = L.prevalence_change(sk, h, e["id"])
            rv = L.prevalence_change(sk, h, e["id"], same_weekday=False)
            out["op"][e["id"]] = {**{k: r[k] for k in ("rel_change", "hosts_before", "hosts_after", "placebo_mean",
                                                       "n_placebo", "net", "exceeds_placebo95")},
                                  "net_allwd": rv["net"], "exceeds_allwd": rv["exceeds_placebo95"],
                                  "n_placebo_allwd": rv["n_placebo"]}
    return out


def colonial_split(col: Colonial, K, day_str: str, B: int, seed: int):
    """Colonial A before vs after an operator action (whole-day split at the event day; the event day goes after)."""
    days = np.array(col.bins.days)
    before = days < day_str
    after = days >= day_str
    rb, ra = col.A(K, before), col.A(K, after)
    bb, ba = col.A_boot(K, before, B, seed), col.A_boot(K, after, B, seed + 1)
    d = ba - bb
    return {"A_before": rb["A"], "A_after": ra["A"], "n_before": rb["n"], "n_after": ra["n"],
            "ci_before": L.q(bb), "ci_after": L.q(ba), "dA": (ra["A"] - rb["A"]) if rb["ok"] and ra["ok"] else None,
            "ci_dA": L.q(d)}


# ================================================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-pseudo", type=int, default=100)
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--only", default=None, help="comma list of pattern ids")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    sk = L.load_skeleton()
    ev, tab = element_events()
    L.set_base(sk, ev["agent"].to_numpy(), ev["t"].dt.epoch("us").to_numpy())
    store = Store(ev, sk)
    pats = load_patterns()
    if a.only:
        pats = [p for p in pats if p["id"] in a.only.split(",")]
    log("patterns:", len(pats), "elements:", tab.height, "element events:", ev.height)
    col = Colonial(ev.select("agent", "t", "eid"), int(tab["eid"].max()) + 1)
    hp = L.HostPanel(sk)
    # K1 positive control (pattern-free)
    k1 = L.output_selfdip(sk, B=a.B)
    (RES / "k1_selfdip.json").write_text(json.dumps(k1, indent=1, default=float))
    log("K1 self-dip:", {k: (round(v["dV_rel"], 3), [round(x, 3) for x in v["ci"]]) for k, v in k1.items()})
    pool = [int(e) for e in store.e_ids]
    rows = []
    for j, p in enumerate(pats):
        t1 = time.time()
        K = [e for e in p["eids"] if e in store.idx]
        rng = np.random.default_rng(147_000 + j)
        pseudo = L.draw_pseudo(store.freq, store.hosts, K, a.n_pseudo, rng, pool=pool)
        r = {"pattern": p, "n_elements_present": len(K)}
        r["wipe"] = wipe_block(sk, store, K, pseudo, a.B, seed=j)
        r["host"] = host_block(sk, hp, store, K, pseudo, a.B, seed=j)
        r["events"] = event_blocks(sk, store, K, p, col)
        A = col.A(K)
        pa = [col.A(P)["A"] for P in pseudo[:min(len(pseudo), 100)]]
        pa = np.array([x for x in pa if x is not None and np.isfinite(x)])
        r["colonial"] = {**A, "pseudo_mean": float(pa.mean()) if len(pa) else None,
                         "pseudo_sd": float(pa.std(ddof=1)) if len(pa) > 1 else None,
                         "z": float((A["A"] - pa.mean()) / pa.std(ddof=1)) if len(pa) > 1 and pa.std() > 0 else None,
                         "excess": float(A["A"] - pa.mean()) if len(pa) else None}
        r["colonial_split"] = {"OP1": colonial_split(col, K, "2026-08-05", a.B, 10 * j),
                               "OP2": colonial_split(col, K, "2026-08-24", a.B, 10 * j + 2),
                               "OP3": colonial_split(col, K, "2026-08-20", a.B, 10 * j + 4)}
        (RES / f"pattern_{p['id']}.json").write_text(json.dumps(r, indent=1, default=float))
        w, hh = r["wipe"], r["host"][HOST_FORM]
        rows.append({"id": p["id"], "label": p["label"], "candidate": p["candidate"], "source": p["source"],
                     "h_K": p["h_K"], "top_host": p["top_host"], "n_el": len(K),
                     "n_host_events": w["n_host_events"],
                     "dV_rate": w["b_rate"]["excess"], "dV_lo": w["b_rate"][CI_FORM][0], "dV_hi": w["b_rate"][CI_FORM][1],
                     "dV_raw": w["b_rate"]["raw"], "oth": w["b_oth"]["excess"], "oth_lo": w["b_oth"][OTH_FORM][0],
                     "oth_hi": w["b_oth"][OTH_FORM][1], "dV_dose_card": w["b_dose"]["excess"],
                     "I_excess": w["I"]["I_excess"], "I_identified": w["I"]["identified"], "kappa": w["kappa"],
                     "host_c": hh["est"]["commits"], "host_c_lo": hh["ci"]["commits"][0],
                     "host_c_hi": hh["ci"]["commits"][1], "host_a": hh["est"]["align_bge"],
                     "host_a_lo": hh["ci"]["align_bge"][0], "host_a_hi": hh["ci"]["align_bge"][1],
                     "host_talk": hh["est"].get("talk"), "class": hh["class_raw"], "class_exc": hh["class_exc"],
                     "class_card": r["host"]["card"]["class_raw"],
                     "A": r["colonial"]["A"], "A_z": r["colonial"]["z"], "A_excess": r["colonial"]["excess"]})
        log(f"{p['id']} ({p['label']}): dV {w['b_rate']['excess']:+.3f} {w['b_rate'][CI_FORM]}, host_c "
            f"{hh['est']['commits']:+.3f} {hh['ci']['commits']} -> {hh['class_raw']}; A z {r['colonial']['z']}; "
            f"{time.time() - t1:.0f}s")
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(RES / "patterns.parquet")
    C.provenance("results", "hypotheses/H147-egregore-value-and-hosts-51/analysis/run.py",
                 ["H145 memeplexes.json", "H145 elements.parquet", "H145 exo.parquet", "H147 scheme outputs"],
                 params={"n_pseudo": a.n_pseudo, "B": a.B, "ci_form": CI_FORM, "host_form": HOST_FORM,
                         "hub_share_min": HUB_SHARE_MIN, "m": L.M_HOST})
    log("done")


if __name__ == "__main__":
    main()
