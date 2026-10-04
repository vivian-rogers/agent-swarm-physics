"""H49 period-native tests (layer 2). Needs run_unit.py outputs for the native windows and the #51 / regime-III units.

NE43  (#51; windows W1 07-27..08-04 bookends on, W2 08-05..08-20 bookend messages off, W3 08-21..09-04 nudges off too;
       fixed population): edge-induced excess E_raw - E_edge per window with a day bootstrap (N43a); conditioned bond
       persistence W1<->W2<->W3, disattenuated by split-half (even / odd 30-min blocks) reliabilities, QAP p (N43b);
       co-nudged pairs (named together in a nudge while the nudger ran) vs other pairs (N43c).
G44   (#best team = agents 24-27; 4 days merged, fixed population, leader excluded): team-pair mean z vs every 4-agent
       label set (exact enumeration), significant team pairs, team connectivity, share of excess covariance;
       checkpoint sensitivity (minutes within +-30 min of the five checkpoint starts dropped like off-schedule minutes).
G51   (#51 head units): adjacent-unit bond persistence; enrichment of bonds on same-lab, rival, opposed and same-room
       pairs (Mantel-Haenszel OR over units; mean-z differences); percolation per unit. R2 (same lab) across all
       regime-III units.
NE14  (II side #35+#36a, III side #36b+#36c+#37; fixed population): raw vs conditioned significant bonds across the
       boundary; disattenuated cross-boundary correlation; persistence of significant bonds.

Output: data/processed/H49-dilute-ferromagnet/native/<test>.json
Usage: uv run python hypotheses/H49-dilute-ferromagnet/analysis/native.py [--only NE43,G44,G51,NE14]
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
import argparse  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h49lib as L  # noqa: E402
import run_unit as RU  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

OUT = L.DATA / "native"
SEED = L.SEED + 4343


def unit_json(uid):
    units = pl.read_parquet(L.DATA / "units.parquet")
    g = units.filter(pl.col("unit") == uid)["group"][0]
    return json.loads((L.DATA / g / f"{uid}.json").read_text())


def bonds(uid, variant="scaffold", channel="activity"):
    return (pl.read_parquet(L.DATA / "bonds" / f"{uid}.parquet")
            .filter((pl.col("variant") == variant) & (pl.col("channel") == channel)))


def zmat(b: pl.DataFrame, agents):
    idx = {a: k for k, a in enumerate(agents)}
    Z = np.full((len(agents), len(agents)), np.nan)
    for a, c, z in zip(b["a"].to_list(), b["b"].to_list(), b["z"].to_list()):
        Z[idx[a], idx[c]] = Z[idx[c], idx[a]] = z
    return Z


def qap_corr(Z1, Z2, rng, n=2000):
    iu = np.triu_indices(Z1.shape[0], 1)
    x, y = Z1[iu], Z2[iu]
    ok = np.isfinite(x) & np.isfinite(y)
    r = float(stats.pearsonr(x[ok], y[ok])[0]) if ok.sum() > 3 else np.nan
    N = Z1.shape[0]
    null = []
    for _ in range(n):
        p = rng.permutation(N)
        y2 = Z2[np.ix_(p, p)][iu]
        ok2 = np.isfinite(x) & np.isfinite(y2)
        null.append(np.corrcoef(x[ok2], y2[ok2])[0, 1])
    null = np.array(null)
    return r, float((1 + (null >= r).sum()) / (1 + n))


def split_half(uid, n_surr=100):
    """z of conditioned bonds on even and odd 30-min blocks separately (each with its own surrogates)."""
    m = np.load(L.DATA / "mats" / f"{uid}.npz")
    par = L.h02.block_ids(m["day"], m["minute"]) % 2 == 0
    out = []
    for k, rows in enumerate((par, ~par)):
        o, b = RU.run(uid, n_surr=n_surr, n_boot=0, rows=rows, tag=f"half{k}", seed_off=11 + k)
        out.append(b.filter((pl.col("variant") == "scaffold") & (pl.col("channel") == "activity")))
    agents = m["agents"].astype(int).tolist()
    zA, zB = zmat(out[0], agents), zmat(out[1], agents)
    iu = np.triu_indices(len(agents), 1)
    r = float(np.corrcoef(zA[iu], zB[iu])[0, 1])
    rel = 2 * r / (1 + r) if r > -1 else np.nan  # Spearman-Brown, full-window reliability
    return {"r_half": r, "rel_full": rel}


def disatt(r, rel1, rel2):
    if not (np.isfinite(rel1) and np.isfinite(rel2)) or rel1 <= 0 or rel2 <= 0:
        return np.nan
    return float(r / np.sqrt(rel1 * rel2))


# --------------------------------------------------------------------------------------------- NE43
def edge_excess_boot(uid, n_boot=500, rng=None):
    """Day bootstrap of g_raw - g_edge and g_raw - g_scaffold (null means fixed from the unit's surrogates)."""
    j = unit_json(uid)
    m = np.load(L.DATA / "mats" / f"{uid}.npz")
    S, R, day, minute, sched = m["S"], m["R"], m["day"], m["minute"], m["sched"]
    days = np.unique(day)
    per = {}
    for v in ("raw", "edge", "scaffold"):
        S2, av, bid, _, keep = L.prep(S, R, sched, day, minute, v)
        x, st, *_ = L.center(S2, av, bid)
        d2 = day[keep]
        nb = np.diff(np.r_[st, x.shape[0]])
        okb = np.repeat(nb >= L.MIN_BLOCK_N, nb)
        per[v] = []
        for d in days:
            rr = (d2 == d) & okb
            xs = x[rr]
            C = xs.T @ xs
            per[v].append((C.sum(), np.trace(C)))
        per[v] = np.array(per[v])
    nullmean = {v: j["variants"][v]["g"] - j["variants"][v]["E"] for v in ("raw", "edge", "scaffold")}
    def E(v, pick):
        s = per[v][pick].sum(0)
        return (1 - s[1] / s[0]) - nullmean[v]
    allp = np.arange(days.size)
    obs = {"E_raw": E("raw", allp), "E_edge": E("edge", allp), "E_scaffold": E("scaffold", allp)}
    bo = []
    for _ in range(n_boot):
        p = rng.integers(0, days.size, days.size)
        bo.append([E("raw", p) - E("edge", p), E("raw", p) - E("scaffold", p), E("raw", p), E("scaffold", p)])
    bo = np.array(bo)
    obs["edge_ex"] = obs["E_raw"] - obs["E_edge"]
    obs["scaf_ex"] = obs["E_raw"] - obs["E_scaffold"]
    obs["boot"] = bo
    return obs


def ne43(rng):
    W = ["NE43_W1", "NE43_W2", "NE43_W3"]
    out = {"windows": {}}
    ee = {}
    for w in W:
        j = unit_json(w)
        e = edge_excess_boot(w, rng=rng)
        ee[w] = e
        v = j["variants"]
        out["windows"][w] = {
            "days": j["meta"]["n_days"], "N": j["N"],
            **{f"g_{k}": v[k]["g"] for k in v}, **{f"E_{k}": v[k]["E"] for k in v}, **{f"z_g_{k}": v[k]["z_g"] for k in v},
            "edge_ex": e["edge_ex"], "edge_ex_ci": np.quantile(e["boot"][:, 0], [0.025, 0.975]).tolist(),
            "scaf_ex": e["scaf_ex"], "scaf_ex_ci": np.quantile(e["boot"][:, 1], [0.025, 0.975]).tolist(),
            **{f"n_pos_{k}": v[k]["bonds"]["n_pos"] for k in v}, **{f"kappa_{k}": v[k]["graph"]["kappa"] for k in v},
            "cv_c10": v["scaffold"]["cv_c10"], "n_pairs": j["n_pairs"]}
    b1 = ee["NE43_W1"]["boot"][:, 0]
    for w in ("NE43_W2", "NE43_W3"):
        ratio = ee[w]["edge_ex"] / ee["NE43_W1"]["edge_ex"] if ee["NE43_W1"]["edge_ex"] != 0 else np.nan
        bw = ee[w]["boot"][:, 0]
        rb = bw / b1
        out["windows"][w]["edge_ratio_vs_W1"] = ratio
        out["windows"][w]["edge_ratio_ci"] = np.quantile(rb[np.isfinite(rb)], [0.025, 0.975]).tolist()
    # N43b persistence
    agents = unit_json("NE43_W1")["agents"]
    Z = {w: zmat(bonds(w), agents) for w in W}
    rel = {w: split_half(w) for w in W}
    out["split_half"] = rel
    pers = {}
    for a, b in (("NE43_W1", "NE43_W2"), ("NE43_W2", "NE43_W3"), ("NE43_W1", "NE43_W3")):
        r, p = qap_corr(Z[a], Z[b], rng)
        pers[f"{a[-2:]}-{b[-2:]}"] = {"r": r, "p_qap": p, "r_disatt": disatt(r, rel[a]["rel_full"], rel[b]["rel_full"])}
    out["persistence"] = pers
    # raw-variant persistence for contrast
    Zr = {w: zmat(bonds(w, "raw"), agents) for w in W}
    out["persistence_raw"] = {"W1-W3": qap_corr(Zr["NE43_W1"], Zr["NE43_W3"], rng)[0]}
    # N43c co-nudged pairs
    k = pl.read_parquet(L.SH / "kicks_classified.parquet").filter(
        (pl.col("kind") == "nudge") & (pl.col("pt_date") >= "2026-07-27") & (pl.col("pt_date") <= "2026-08-20")
        & (pl.col("n_targets") >= 2))
    aset = set(agents)
    pairs = {}
    for tg in k["targets"].to_list():
        tg = sorted({int(t) for t in tg if int(t) in aset})
        for a, b in itertools.combinations(tg, 2):
            pairs[(a, b)] = pairs.get((a, b), 0) + 1
    out["co_nudged"] = {"n_nudges": k.height, "n_pairs": len(pairs)}
    for w in W:
        for var in ("scaffold", "raw"):
            bd = bonds(w, var)
            co = np.array([(min(a, b), max(a, b)) in pairs for a, b in zip(bd["a"].to_list(), bd["b"].to_list())])
            z = bd["z"].to_numpy()
            d = float(z[co].mean() - z[~co].mean()) if co.any() else np.nan
            null = []
            for _ in range(2000):
                pm = rng.permutation(co)
                null.append(z[pm].mean() - z[~pm].mean())
            out["co_nudged"][f"{w}_{var}"] = {"dz": d, "p_perm": float((1 + (np.array(null) >= d).sum()) / 2001),
                                              "n_co": int(co.sum()),
                                              "sig_co": int(bd["sig_pos"].to_numpy()[co].sum())}
    return out


# --------------------------------------------------------------------------------------------- G44
def team_stats(b: pl.DataFrame, agents, team, dC=None):
    Z = zmat(b, agents)
    idx = [agents.index(a) for a in team if a in agents]
    tp = [(i, j) for i, j in itertools.combinations(idx, 2)]
    mean_team = float(np.mean([Z[i, j] for i, j in tp]))
    null = []
    for comb in itertools.combinations(range(len(agents)), len(idx)):
        null.append(np.mean([Z[i, j] for i, j in itertools.combinations(comb, 2)]))
    null = np.array(null)
    p = float((null >= mean_team).mean())
    sig = b.filter(pl.col("sig_pos"))
    sigp = {(min(a, c), max(a, c)) for a, c in zip(sig["a"].to_list(), sig["b"].to_list())}
    tset = {(min(agents[i], agents[j]), max(agents[i], agents[j])) for i, j in tp}
    tz = {f"{a}-{c}": float(Z[agents.index(a), agents.index(c)]) for a, c in sorted(tset)}
    is_team = np.array([(min(a, c), max(a, c)) in tset for a, c in zip(b["a"].to_list(), b["b"].to_list())])
    rest = [a for a in agents if a not in team]
    is_rest = np.array([(a in rest) and (c in rest) for a, c in zip(b["a"].to_list(), b["b"].to_list())])
    zz = b["z"].to_numpy()
    out = {"team_in_pop": [a for a in team if a in agents], "mean_z_team": mean_team, "p_label": p,
           "n_label_sets": int(null.size), "team_pair_z": tz, "n_sig_team": len(tset & sigp),
           "n_sig_total": len(sigp), "mean_z_rest_rest": float(zz[is_rest].mean()),
           "mean_z_cross": float(zz[~is_team & ~is_rest].mean())}
    if "dC" in b.columns:
        dc = b["dC"].to_numpy()
        out["share_dC_team"] = float(dc[is_team].sum() / dc.sum()) if dc.sum() > 0 else np.nan
        out["frac_pairs_team"] = float(is_team.mean())
    return out


def g44(rng):
    uid = "G44_all"
    j = unit_json(uid)
    agents = j["agents"]
    team = [24, 25, 26, 27]
    out = {"N": j["N"], "days": j["meta"]["n_days"], "variants": {}}
    for v in ("scaffold", "edge", "raw"):
        b = bonds(uid, v)
        out["variants"][v] = team_stats(b, agents, team)
        out["variants"][v]["graph"] = j["variants"][v]["graph"]
        out["variants"][v]["g"] = j["variants"][v]["g"]; out["variants"][v]["E"] = j["variants"][v]["E"]
        out["variants"][v]["z_g"] = j["variants"][v]["z_g"]
    # team connectivity in the significant scaffold graph
    b = bonds(uid)
    sig = b.filter(pl.col("sig_pos"))
    from scipy.sparse import csr_matrix  # noqa: PLC0415
    from scipy.sparse.csgraph import connected_components  # noqa: PLC0415
    ix = {a: k for k, a in enumerate(agents)}
    Adj = np.zeros((len(agents), len(agents)), bool)
    for a, c in zip(sig["a"].to_list(), sig["b"].to_list()):
        Adj[ix[a], ix[c]] = Adj[ix[c], ix[a]] = True
    _, lab = connected_components(csr_matrix(Adj), directed=False)
    comps = [sorted(agents[k] for k in np.flatnonzero(lab == c)) for c in np.unique(lab) if (lab == c).sum() >= 2]
    out["components"] = comps
    out["team_one_component"] = any(set(team) <= set(c) for c in comps)
    out["team_largest_component_overlap"] = max([len(set(team) & set(c)) for c in comps], default=0)
    # checkpoint sensitivity
    gt = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 44) & (pl.col("label_kind") == "checkpoint"))
    cps = gt["t_valid_from"].to_list()
    m = np.load(L.DATA / "mats" / f"{uid}.npz")
    sm = pl.read_parquet(L.SH / "stall_minutes.parquet", columns=["pt_date", "minute", "t"])
    days = [str(d) for d in m["days"]]
    tmap = sm.filter(pl.col("pt_date").is_in(days)).with_columns(
        pl.col("pt_date").replace_strict({d: i for i, d in enumerate(days)}, return_dtype=pl.Int16).alias("day"))
    key = pl.DataFrame({"day": m["day"], "minute": m["minute"]}).join(tmap.select("day", "minute", "t"),
                                                                      on=["day", "minute"], how="left")
    t = key["t"].to_numpy()
    near = np.zeros(t.size, bool)
    for c in cps:
        c64 = np.datetime64(c.replace(tzinfo=None), "us")
        tt = t.astype("datetime64[us]")
        near |= np.abs(tt - c64) <= np.timedelta64(30, "m")
    out["checkpoint_minutes_dropped"] = int(near.sum())
    o2, b2 = RU.run(uid, n_surr=200, n_boot=0, extra_sched=near, tag="ckpt", seed_off=44)
    bs2 = b2.filter((pl.col("variant") == "scaffold") & (pl.col("channel") == "activity"))
    ts2 = team_stats(bs2, agents, team)
    out["checkpoint_drop"] = {"mean_z_team": ts2["mean_z_team"], "p_label": ts2["p_label"],
                              "n_sig_team": ts2["n_sig_team"], "team_pair_z": ts2["team_pair_z"],
                              "g": o2["variants"]["scaffold"]["g"], "E": o2["variants"]["scaffold"]["E"],
                              "z_g": o2["variants"]["scaffold"]["z_g"],
                              "reduction": 1 - ts2["mean_z_team"] / out["variants"]["scaffold"]["mean_z_team"]}
    # talk channel (team share of talk bonds)
    bt = bonds(uid, "scaffold", "talk")
    if bt.height:
        ta = sorted(set(bt["a"].to_list()) | set(bt["b"].to_list()))
        if sum(a in ta for a in team) >= 2:
            out["talk"] = team_stats(bt, ta, [a for a in team if a in ta])
    return out


# --------------------------------------------------------------------------------------------- G51
def pair_attrs(goal, a, b, room=None):
    gt = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter(pl.col("goal_no") == goal)
    rival = {(min(x, y), max(x, y)) for x, y in gt.filter(pl.col("label_kind") == "rival_pair").select("agent_a", "agent_b").iter_rows()}
    opp = {(min(x, y), max(x, y)) for x, y in gt.filter(pl.col("label_kind") == "opposed_pair").select("agent_a", "agent_b").iter_rows()}
    lab = dict(pl.read_parquet(L.SH / "roster.parquet").select("agent", "lab").iter_rows())
    out = {"same_lab": [], "rival": [], "opposed": [], "same_room": []}
    for x, y in zip(a, b):
        k = (min(x, y), max(x, y))
        out["same_lab"].append(lab.get(x) == lab.get(y))
        out["rival"].append(k in rival)
        out["opposed"].append(k in opp)
        out["same_room"].append(None if room is None or x not in room or y not in room else room[x] == room[y])
    return out


def room_majority_51g():
    """Majority room (#focus vs #general) per agent over unit 51g's days (08-05..08-21), from room_presence labels."""
    gt = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 51) & (pl.col("label_kind") == "room_presence") & pl.col("preferred"))
    lo = np.datetime64("2026-08-05T16:00")
    hi = np.datetime64("2026-08-22T00:10")
    dur = {}
    for ag, val, a, b in gt.select("agent", "value", "t_valid_from", "t_valid_to").iter_rows():
        a = np.datetime64(a.replace(tzinfo=None), "m"); b = np.datetime64(b.replace(tzinfo=None), "m")
        ov = (min(b, hi) - max(a, lo)).astype(int)
        if ov > 0 and val in ("focus", "general"):
            dur.setdefault(ag, {}).setdefault(val, 0)
            dur[ag][val] += ov
    return {ag: max(d, key=d.get) for ag, d in dur.items()}


def mh_or(tables):
    """Mantel-Haenszel common odds ratio over 2x2 tables [[a, b], [c, d]] (a = attr & sig)."""
    num = den = 0.0
    for a, b, c, d in tables:
        n = a + b + c + d
        if n == 0:
            continue
        num += a * d / n; den += b * c / n
    return num / den if den > 0 else np.nan


def enrichment(units, goal_of, room=None, rng=None):
    rows = []
    for u in units:
        b = bonds(u)
        at = pair_attrs(goal_of[u], b["a"].to_list(), b["b"].to_list(), room if u == "51g" else None)
        rows.append(b.select("a", "b", "z", "sig_pos").with_columns(
            pl.lit(u).alias("unit"), pl.Series("same_lab", at["same_lab"]), pl.Series("rival", at["rival"]),
            pl.Series("opposed", at["opposed"]), pl.Series("same_room", at["same_room"], dtype=pl.Boolean)))
    df = pl.concat(rows)
    out = {}
    for attr in ("same_lab", "rival", "opposed", "same_room"):
        d = df.filter(pl.col(attr).is_not_null())
        if d.filter(pl.col(attr)).height == 0:
            continue
        tabs = []
        dz = []
        for u in d["unit"].unique().to_list():
            x = d.filter(pl.col("unit") == u)
            A = x[attr].to_numpy(); s = x["sig_pos"].to_numpy(); z = x["z"].to_numpy()
            tabs.append(((A & s).sum(), (A & ~s).sum(), (~A & s).sum(), (~A & ~s).sum()))
            if A.any() and (~A).any():
                dz.append((z[A].mean() - z[~A].mean(), A.sum()))
        A = d[attr].to_numpy(); z = d["z"].to_numpy(); u_ = d["unit"].to_numpy()
        obs = float(np.average([x for x, _ in dz], weights=[w for _, w in dz])) if dz else np.nan
        # permutation of the attribute within unit
        null = []
        for _ in range(1000):
            Ap = A.copy()
            for u in np.unique(u_):
                ii = np.flatnonzero(u_ == u)
                Ap[ii] = rng.permutation(A[ii])
            vals = []
            for u in np.unique(u_):
                ii = u_ == u
                if Ap[ii].any() and (~Ap[ii]).any():
                    vals.append((z[ii][Ap[ii]].mean() - z[ii][~Ap[ii]].mean(), Ap[ii].sum()))
            null.append(np.average([x for x, _ in vals], weights=[w for _, w in vals]))
        out[attr] = {"n_attr_pairs": int(A.sum()), "n_sig_attr": int((A & d["sig_pos"].to_numpy()).sum()),
                     "n_sig_total": int(d["sig_pos"].sum()), "OR_MH": mh_or(tabs), "dz": obs,
                     "p_perm": float((1 + (np.array(null) >= obs).sum()) / 1001)}
    return out


def g51(rng):
    units_df = pl.read_parquet(L.DATA / "units.parquet").filter(pl.col("kind") == "replication")
    u51 = units_df.filter(pl.col("goal_no") == 51).sort("first_day")["unit"].to_list()
    out = {"units": u51, "per_unit": {}, "adjacent": {}}
    for u in u51:
        j = unit_json(u)
        v = j["variants"]["scaffold"]
        out["per_unit"][u] = {"N": j["N"], "days": j["meta"]["n_days"], "n_pos": v["bonds"]["n_pos"],
                              "frac_pos": v["bonds"]["n_pos"] / j["n_pairs"], "kappa": v["graph"]["kappa"],
                              "S1": v["graph"]["S1"], "clusters": v["graph"]["clusters"], "z_g": v["z_g"],
                              "cv_c10": v["cv_c10"], "n_pos_raw": j["variants"]["raw"]["bonds"]["n_pos"]}
    rec_hits = rec_n = 0
    for a, b in zip(u51[:-1], u51[1:]):
        ba, bb = bonds(a), bonds(b)
        jn = ba.select("a", "b", pl.col("z").alias("za"), pl.col("sig_pos").alias("sa")).join(
            bb.select("a", "b", pl.col("z").alias("zb"), pl.col("sig_pos").alias("sb")), on=["a", "b"])
        r = float(np.corrcoef(jn["za"].to_numpy(), jn["zb"].to_numpy())[0, 1])
        s = jn.filter(pl.col("sa"))
        hits = int((s["zb"] > 1).sum())
        rec_hits += hits; rec_n += s.height
        out["adjacent"][f"{a}-{b}"] = {"r": r, "n_common_pairs": jn.height, "n_sig_a": s.height, "hits_z_gt1": hits}
    out["median_adjacent_r"] = float(np.median([x["r"] for x in out["adjacent"].values()]))
    out["recurrence"] = rec_hits / rec_n if rec_n else np.nan
    out["recurrence_n"] = rec_n
    room = room_majority_51g()
    out["room_51g"] = {str(k): v for k, v in room.items()}
    out["enrichment_51"] = enrichment(u51, {u: 51 for u in u51}, room, rng)
    u3 = units_df.filter(pl.col("regime") == "III")
    out["enrichment_regime3_lab"] = enrichment(u3["unit"].to_list(), dict(zip(u3["unit"], u3["goal_no"])), None, rng)
    return out


# --------------------------------------------------------------------------------------------- NE14
def ne14(rng):
    A, B = "NE14_II", "NE14_III"
    ja, jb = unit_json(A), unit_json(B)
    agents = ja["agents"]
    out = {"N": ja["N"], "days": [ja["meta"]["n_days"], jb["meta"]["n_days"]], "sides": {}}
    for uid, j in ((A, ja), (B, jb)):
        out["sides"][uid] = {f"n_pos_{v}": j["variants"][v]["bonds"]["n_pos"] for v in j["variants"]}
        out["sides"][uid].update({f"g_{v}": j["variants"][v]["g"] for v in j["variants"]})
        out["sides"][uid].update({f"E_{v}": j["variants"][v]["E"] for v in j["variants"]})
        out["sides"][uid].update({f"kappa_{v}": j["variants"][v]["graph"]["kappa"] for v in j["variants"]})
        out["sides"][uid]["mean_z_scaffold"] = j["variants"]["scaffold"]["bonds"]["mean_z"]
        out["sides"][uid]["mean_z_raw"] = j["variants"]["raw"]["bonds"]["mean_z"]
    for v in ("raw", "edge", "scaffold"):
        out[f"delta_n_pos_{v}"] = out["sides"][B][f"n_pos_{v}"] - out["sides"][A][f"n_pos_{v}"]
    rel = {u: split_half(u) for u in (A, B)}
    out["split_half"] = rel
    for v in ("scaffold", "raw"):
        Za, Zb = zmat(bonds(A, v), agents), zmat(bonds(B, v), agents)
        r, p = qap_corr(Za, Zb, rng)
        out[f"cross_r_{v}"] = r; out[f"cross_p_{v}"] = p
    out["cross_r_disatt"] = disatt(out["cross_r_scaffold"], rel[A]["rel_full"], rel[B]["rel_full"])
    # persistence of significant bonds
    ba, bb = bonds(A), bonds(B)
    jn = ba.select("a", "b", pl.col("z").alias("za"), pl.col("sig_pos").alias("sa"), pl.col("sig_neg").alias("na")).join(
        bb.select("a", "b", pl.col("z").alias("zb"), pl.col("sig_pos").alias("sb"), pl.col("sig_neg").alias("nb")), on=["a", "b"])
    sig = jn.filter(pl.col("sa") | pl.col("sb") | pl.col("na") | pl.col("nb"))
    keep = 0
    for r in sig.iter_rows(named=True):
        if r["sa"] or r["na"]:
            sgn = 1 if r["sa"] else -1
            keep += int(sgn * r["zb"] > 1)
        if r["sb"] or r["nb"]:
            sgn = 1 if r["sb"] else -1
            keep += int(sgn * r["za"] > 1)
    nsig = int(sig.select((pl.col("sa") | pl.col("na")).cast(pl.Int32).sum() + (pl.col("sb") | pl.col("nb")).cast(pl.Int32).sum()).item())
    out["persist_frac"] = keep / nsig if nsig else np.nan
    out["persist_n"] = nsig
    out["sig_pairs"] = sig.to_dicts()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="NE43,G44,G51,NE14")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    fns = {"NE43": ne43, "G44": g44, "G51": g51, "NE14": ne14}
    for k in a.only.split(","):
        r = fns[k](rng)
        (OUT / f"{k}.json").write_text(json.dumps(r, indent=1, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else (o.item() if hasattr(o, "item") else str(o))))
        print(k, "done", flush=True)


if __name__ == "__main__":
    main()
