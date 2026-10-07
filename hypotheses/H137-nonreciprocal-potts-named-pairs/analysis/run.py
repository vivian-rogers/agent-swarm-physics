"""H137 round 1 on exploration data (non-reserved units only; reserved rows masked in h137lib.load_skeleton and
asserted in real_labels). Computes O1-O5 per unit and pooled, the card's estimators and the amended ones (A1-A3 in
the card's Round 1 section), the natives (G51 pooled, G38 rooms, G44 rooms) and the impostor variants.

Writes data/processed/H137-nonreciprocal-potts-named-pairs/{follows.parquet, pairs.parquet, results/round1.json,
results/units.parquet} and _provenance.json. Agent ids and call indices only; no project names, no text.

Usage: uv run python hypotheses/H137-nonreciprocal-potts-named-pairs/analysis/run.py [--nboot 1000 --nnull 2000]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h137lib as L  # noqa: E402
import real_labels as RL  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import REVISION, git_commit  # noqa: E402

REAL_D = L.D


def modal_room(S: dict) -> np.ndarray:
    """Each agent's modal room over its calls in the unit (ledger turns)."""
    t = (pl.scan_parquet(L.SH / "context_ledger_turns.parquet").filter(pl.col("turn_id").is_in(S["turn"].tolist()))
         .select("agent", "room").collect())
    out = np.full(S["A"], -1, dtype=np.int64)
    for a, g in t.drop_nulls("room").group_by("agent"):
        a = a[0] if isinstance(a, tuple) else a
        if a in S["aidx"]:
            out[S["aidx"][a]] = int(g["room"].mode().sort()[0])
    return out


def kickoff_drop_mask(S: dict, lab: dict, hours: float = 4.0) -> np.ndarray:
    """Exogenous-field variant: True for hop calls to drop (first `hours` after the goal's first window start, or onto
    a kickoff-named project)."""
    import replicator_hosts as RH  # noqa: E402
    cal = pl.read_parquet(L.SH / "calendar.parquet", columns=["pt_date", "goal_no", "win_start"])
    d = cal.filter(pl.col("goal_no") == S["goal_no"]).sort("pt_date")
    t0 = d["win_start"][0].timestamp() if d.height else -np.inf
    names = lab["names"]
    try:
        kn = RH.kickoff_named(S["goal_no"], names)
    except Exception:  # noqa: BLE001
        kn = {}
    named_codes = {k for k, n in enumerate(names) if kn.get(n, False)}
    early = S["tc"] < t0 + hours * 3600
    onto = np.array([x in named_codes for x in lab["label"]])
    return lab["hop"] & (early | onto)


def unit_data(u: str, variant: str = "e100", drop_kickoff: bool = False):
    S = L.load_skeleton(u)
    lab = RL.labels_for(S, variant=variant, keep_names=drop_kickoff)
    hop = lab["hop"].copy()
    if drop_kickoff:
        hop &= ~kickoff_drop_mask(S, lab)
    fh = L.follow_hops(S, lab["cur"], lab["label"], hop)
    pt = L.pair_table(S, fh)
    P = pt["pairs"].with_columns(pl.lit(u).alias("unit"))
    R = L.hop_rows(S, fh, pt["pairs"]).with_columns(pl.lit(u).alias("unit"))
    O = L.readout_rows(S, lab["cur"], lab["label"], hop).with_columns(pl.lit(u).alias("unit"))
    Q = L.sigma_pairs(P)
    fw = L.fh_row_weights(fh, u)
    return S, lab, fh, P, R, O, Q, fw


def install_dry_labels():
    """Dry run (code test without real outcomes): labels come from a W0 simulation calibrated on structural counts."""
    import synthetic as SY  # noqa: E402
    real = RL.labels_for
    cache = {}

    def fake(S, variant="e100", keep_names=False):
        u = S["unit"]
        if u not in cache:
            lab = real(S)
            vals, cnt = np.unique(lab["label"][lab["label"] >= 0], return_counts=True)
            hk = np.bincount(S["ag"][lab["hop"]], minlength=S["A"]).astype(float)
            ck = np.bincount(S["ag"], minlength=S["A"]).astype(float)
            cal = {"hops": int(lab["hop"].sum()), "pop": {int(a): int(b) for a, b in zip(vals, cnt)},
                   "p_agent": (hk / np.maximum(ck, 1)).tolist(), "mix": (0.1, 0.0)}
            cur, label, hop = SY.simulate(S, cal, {}, np.random.default_rng(7))
            cache[u] = {"label": label, "cur": cur, "hop": hop, "n_projects": len(cal["pop"]) or 2}
        out = dict(cache[u])
        if keep_names:
            out["names"] = [f"p{k}" for k in range(max(out["label"].max() + 1, 1))]
        return out

    RL.labels_for = fake


def theta_block(R, rng, nb, nn, n2=True):
    out = {}
    for name, ctl in (("theta", True), ("theta_act", "act"), ("theta_raw", False)):
        est = L.theta_fit(R, ctl)
        lo, hi = L.theta_boot(R, rng, B=nb, controls=ctl)
        p = L.theta_n2(R, rng, draws=nn, controls=ctl) if (n2 and ctl is not False) else None
        out[name] = {"est": est, "lo": lo, "hi": hi, "p_n2": p}
    out["n_rows"] = R.height
    out["n_rows_z"] = int((R["z"] != 0).sum()) if R.height else 0
    out["n_pairs_z"] = int(R.filter(pl.col("z") != 0).select("unit", "a", "b").unique().height) if R.height else 0
    return out


def sigma_block(R, Q, fw, rng, nb, nn):
    out = {}
    nul = L.flip_null(Q, rng, draws=nn, fh_rows=fw)
    adj = L.adj_null(R, Q, rng, draws=nn)
    one = Q.filter(pl.col("cls") == "one")
    unit = one["unit"].to_numpy() if one.height else np.array([])
    A = one["A"].to_numpy() if one.height else np.array([])
    m, lo, hi = L.mean_boot(A, unit, rng, B=nb)
    out["A_one"] = {"est": m, "lo": lo, "hi": hi, "n_pairs": int(one.height),
                    "p_flip": float((np.sum(nul["A_one"] >= m) + 1) / (nn + 1)) if one.height else None,
                    "p_adj": float((np.sum(adj["A_one"] >= m) + 1) / (np.isfinite(adj["A_one"]).sum() + 1)) if one.height else None,
                    "null_flip_mean": float(np.nanmean(nul["A_one"])) if one.height else None,
                    "null_adj_mean": float(np.nanmean(adj["A_one"])) if one.height else None}
    for c in ("one", "mutual", "none", "weak"):
        q = Q.filter(pl.col("cls") == c)
        if not q.height:
            out[f"sig_{c}"] = {"est": None, "n_pairs": 0}
            continue
        v = q["sigma"].to_numpy()
        m, lo, hi = L.mean_boot(v, q["unit"].to_numpy(), rng, B=nb)
        d = {"est": m, "lo": lo, "hi": hi, "n_pairs": int(q.height),
             "p_flip": float((np.sum(nul[f"sig_{c}"] >= m) + 1) / (nn + 1)),
             "null_flip_mean": float(np.nanmean(nul[f"sig_{c}"]))}
        if c != "weak":
            fin = np.isfinite(adj[f"sig_{c}"])
            d["p_adj"] = float((np.sum(adj[f"sig_{c}"][fin] >= m) + 1) / (fin.sum() + 1))
            d["null_adj_mean"] = float(np.nanmean(adj[f"sig_{c}"]))
        out[f"sig_{c}"] = d
    e, lo, hi = L.pair_boot_contrast(Q, rng, B=nb)
    fin = np.isfinite(adj["contrast"])
    out["contrast"] = {"est": e, "lo": lo, "hi": hi,
                       "p_adj": float((np.sum(adj["contrast"][fin] >= e) + 1) / (fin.sum() + 1)) if np.isfinite(e) else None,
                       "null_adj_mean": float(np.nanmean(adj["contrast"])) if fin.any() else None}
    if np.isfinite(e) and fin.any():
        # A3 (amended): contrast of null-centred class means, bootstrap CI shifted by the N1b null mean
        out["contrast_excess"] = {"est": e - float(np.nanmean(adj["contrast"])), "lo": lo - float(np.nanmean(adj["contrast"])),
                                  "hi": hi - float(np.nanmean(adj["contrast"]))}
    return out


def dl_pool(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if est.size < 2:
        return {"est": None, "lo": None, "hi": None, "k": int(est.size)}
    w = 1 / se ** 2
    m = np.sum(w * est) / w.sum()
    Qs = np.sum(w * (est - m) ** 2)
    tau2 = max(0.0, (Qs - (est.size - 1)) / (w.sum() - np.sum(w ** 2) / w.sum()))
    ws = 1 / (se ** 2 + tau2)
    mm = np.sum(ws * est) / ws.sum()
    s = np.sqrt(1 / ws.sum())
    return {"est": float(mm), "lo": float(mm - 1.96 * s), "hi": float(mm + 1.96 * s), "k": int(est.size), "tau2": float(tau2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nboot", type=int, default=1000)
    ap.add_argument("--nnull", type=int, default=2000)
    ap.add_argument("--units", default="")
    ap.add_argument("--dry", default="", help="dry run: replace real labels by a W0 simulation; outputs to this dir")
    a = ap.parse_args()
    if a.dry:
        install_dry_labels()
        L.D = Path(a.dry)
    t0 = time.time()
    rng = np.random.default_rng(20261007)
    st = pl.read_parquet(REAL_D / "results/structure.parquet")
    units = a.units.split(",") if a.units else st.filter(pl.col("follow_rows") > 0)["unit"].to_list()
    testable = set(st.filter(pl.col("testable"))["unit"].to_list())
    Rs, Qs, Os, FWs, Ps, FHs, unit_rows = [], [], [], {}, [], [], []
    rooms = {}
    for u in units:
        S, lab, fh, P, R, O, Q, fw = unit_data(u)
        Rs.append(R); Qs.append(Q); Os.append(O); FWs.update(fw); Ps.append(P)
        FHs.append(fh.with_columns(pl.lit(u).alias("unit"),
                                   pl.Series("hopper_agent", [S["agents"][k] for k in fh["hopper"].to_list()], dtype=pl.Int16),
                                   pl.Series("target_agent", [S["agents"][k] for k in fh["target"].to_list()], dtype=pl.Int16)))
        if S["goal_no"] in (38, 44):
            rooms[u] = modal_room(S)
        row = {"unit": u, "goal_no": S["goal_no"], "testable": u in testable}
        if u in testable:
            tb = theta_block(R, rng, a.nboot // 2, a.nnull // 4)
            sb = sigma_block(R, Q, fw, rng, a.nboot // 2, a.nnull // 2)
            e4, lo4, hi4, n1, n0 = L.readout_contrast(O, rng, B=a.nboot // 2)
            for k in ("theta", "theta_act", "theta_raw"):
                row.update({f"{k}": tb[k]["est"], f"{k}_lo": tb[k]["lo"], f"{k}_hi": tb[k]["hi"], f"{k}_p": tb[k]["p_n2"]})
            row.update(n_rows=tb["n_rows"], n_rows_z=tb["n_rows_z"], n_pairs_z=tb["n_pairs_z"])
            row.update(A_one=sb["A_one"]["est"], A_one_lo=sb["A_one"]["lo"], A_one_hi=sb["A_one"]["hi"],
                       A_one_p_flip=sb["A_one"]["p_flip"], A_one_p_adj=sb["A_one"]["p_adj"])
            for c in ("one", "mutual", "none"):
                d = sb[f"sig_{c}"]
                row.update({f"sig_{c}": d.get("est"), f"sig_{c}_lo": d.get("lo"), f"sig_{c}_hi": d.get("hi"),
                            f"sig_{c}_p_flip": d.get("p_flip"), f"sig_{c}_p_adj": d.get("p_adj"),
                            f"sig_{c}_n": d.get("n_pairs", 0)})
            row.update(contrast=sb["contrast"]["est"], contrast_lo=sb["contrast"]["lo"], contrast_hi=sb["contrast"]["hi"],
                       contrast_p_adj=sb["contrast"]["p_adj"],
                       o4=e4, o4_lo=lo4, o4_hi=hi4, o4_n_read=n1, o4_n_if=n0)
        unit_rows.append(row)
        print(f"{u} {time.time() - t0:.0f}s rows {R.height}", flush=True)
    R = pl.concat(Rs); Q = pl.concat(Qs); O = pl.concat(Os)
    res = {"units": units, "testable": sorted(testable & set(units))}
    # ---- pooled over all units (common theta; covariates within unit)
    res["pooled"] = {**theta_block(R, rng, a.nboot, a.nnull), **sigma_block(R, Q, FWs, rng, a.nboot, a.nnull)}
    e4, lo4, hi4, n1, n0 = L.readout_contrast(O, rng, B=a.nboot)
    res["pooled"]["o4"] = {"est": e4, "lo": lo4, "hi": hi4, "n_read": n1, "n_if": n0,
                           "rate_read": float(O.filter(pl.col("read") == 1)["y"].mean()) if n1 else None,
                           "rate_if": float(O.filter(pl.col("read") == 0)["y"].mean()) if n0 else None}
    U = pl.DataFrame(unit_rows, infer_schema_length=None)
    tu = U.filter(pl.col("testable"))
    for k in ("theta", "theta_act"):
        se = (tu[f"{k}_hi"] - tu[f"{k}_lo"]) / (2 * 1.96)
        res["pooled"][f"{k}_dl"] = dl_pool(tu[k].to_numpy(), se.to_numpy())
    # ---- natives
    nat = {}
    R51 = R.filter(pl.col("unit").str.starts_with("51"))
    Q51 = Q.filter(pl.col("unit").str.starts_with("51"))
    fw51 = {k: v for k, v in FWs.items() if str(k[0]).startswith("51")}
    nat["N1_G51"] = {**theta_block(R51, rng, a.nboot, a.nnull), **sigma_block(R51, Q51, fw51, rng, a.nboot, a.nnull)}
    for g, label in ((38, "N2_G38"), (44, "N3_G44")):
        rr = []
        for u, mr in rooms.items():
            if not u.startswith(str(g)):
                continue
            Ru = R.filter(pl.col("unit") == u)
            ra, rb = mr[Ru["a"].to_numpy()], mr[Ru["b"].to_numpy()]
            rr.append(Ru.with_columns(pl.Series("room_a", ra), pl.Series("room_b", rb)))
        if not rr:
            continue
        Rg = pl.concat(rr)
        d = {}
        if g == 38:
            parts = {"same_room": Rg.filter(pl.col("room_a") == pl.col("room_b")),
                     "cross_room": Rg.filter(pl.col("room_a") != pl.col("room_b"))}
        else:
            parts = {"best": Rg.filter((pl.col("room_a") == 2) & (pl.col("room_b") == 2)),
                     "rest": Rg.filter((pl.col("room_a") == 3) & (pl.col("room_b") == 3)),
                     "cross": Rg.filter(pl.col("room_a") != pl.col("room_b"))}
        for k, Rk in parts.items():
            d[k] = theta_block(Rk, rng, a.nboot, a.nnull // 2) if Rk.height >= 3 else {"n_rows": Rk.height}
            d[k]["raw_share_a_joins_b_given_z+"] = (float((Rk.filter(pl.col("z") == 1)["y"] * Rk.filter(pl.col("z") == 1)["w"]).sum()
                                                    / max(Rk.filter(pl.col("z") == 1)["w"].sum(), 1e-9)) if Rk.height else None)
        nat[label] = d
    res["natives"] = nat
    # ---- impostor variants (pooled theta_act)
    lab_of = L.lab_of()
    var = {}
    # same-lab vs cross-lab (needs agent ids): recover from follows
    FH = pl.concat(FHs)
    pair_lab = {}
    for row in FH.select("unit", "hopper", "target", "hopper_agent", "target_agent").unique().iter_rows():
        u, h, t, ha, ta = row
        a_, b_ = min(h, t), max(h, t)
        pair_lab[(u, a_, b_)] = lab_of.get(ha) == lab_of.get(ta)
    same = np.array([pair_lab.get((u, a_, b_), False) for u, a_, b_ in R.select("unit", "a", "b").iter_rows()])
    var["same_lab"] = theta_block(R.filter(pl.Series(same)), rng, a.nboot // 2, a.nnull // 4)
    var["cross_lab"] = theta_block(R.filter(pl.Series(~same)), rng, a.nboot // 2, a.nnull // 4)
    for v in ("e50", "e300"):
        Rv = pl.concat([unit_data(u, variant=v)[4] for u in units])
        var[v] = theta_block(Rv, rng, a.nboot // 2, a.nnull // 4)
    Rk = pl.concat([unit_data(u, drop_kickoff=True)[4] for u in units])
    var["kickoff_drop"] = theta_block(Rk, rng, a.nboot // 2, a.nnull // 4)
    res["variants"] = var
    # ---- write
    out = L.D / "results"
    out.mkdir(parents=True, exist_ok=True)
    U.write_parquet(out / "units.parquet")
    FH.select("unit", "hopper_agent", "target_agent", "call", "w").write_parquet(L.D / "follows.parquet", compression="zstd")
    pl.concat(Ps).write_parquet(L.D / "pairs.parquet", compression="zstd")
    (out / "round1.json").write_text(json.dumps(res, indent=1, default=lambda x: None if x is None or (isinstance(x, float) and not np.isfinite(x)) else float(x)))
    prov = {"built_by": "hypotheses/H137-nonreciprocal-potts-named-pairs/analysis/run.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["project_calls", "call_windows", "context_ledger_items", "context_ledger_turns",
                                   "chat_core", "chat_mentions_clean", "period_units", "roster", "calendar"]}],
            "params": {"read_window_calls": L.READ_WIN, "present_s": L.PRESENT_S, "label": "project_calls E100 (E50, E300 variants)",
                       "nboot": a.nboot, "nnull": a.nnull, "reserved": "masked (holdout_mask) and asserted"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (L.D / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
