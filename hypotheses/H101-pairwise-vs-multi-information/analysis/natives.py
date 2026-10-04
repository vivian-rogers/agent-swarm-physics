"""H101 period-native tests (layer 2). Predictions are in each folder's README (written before running).

  g12   #12 debates: one ensemble per debate (items = markers used inside the debate window; spins = the debate's
        team members, DQ6 `team` labels: gov / opp). K-pairwise fit per debate; mean J for same-team vs opposite-team
        pairs; permutation null (team labels shuffled within debate, sizes kept); hierarchy ratios per debate.
  ne42  #39 -> #40 -> #41 (room merge at fixed roster): field share phi, rho_F, r_HO per unit from the replication
        table; J within vs between rooms in #39 and #41 from subset fits (each pair's J averaged over the subsets
        holding it), permutation null over room labels within day.
  g51   size sweep on 51c and 51g: n = 4, 6, 8 (S = 6 subsets per day) and n = 10 (S = 2, 51g): rho_F(n), r_HO(n), z(n)
        with the latent-field reference.
Usage: uv run python hypotheses/H101-pairwise-vs-multi-information/analysis/natives.py [--only g12,ne42,g51]
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h101lib as L  # noqa: E402
import run as R  # noqa: E402

ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
BASE = ROOT / "data/processed/H101-pairwise-vs-multi-information"
OUT = BASE / "natives"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402


def J_matrix(th, n):
    J = np.zeros((n, n))
    iu, ju = np.triu_indices(n, 1)
    J[iu, ju] = th[n:n + len(iu)]
    return J + J.T


def perm_diff(J_pairs, same, rng, R_=2000, groups=None):
    """Mean J(same) - mean J(diff) with a permutation null that shuffles the same/diff labels within groups."""
    J_pairs, same = np.asarray(J_pairs, float), np.asarray(same, bool)
    obs = J_pairs[same].mean() - J_pairs[~same].mean()
    null = []
    groups = np.zeros(len(same), int) if groups is None else np.asarray(groups)
    for _ in range(R_):
        s = same.copy()
        for gid in np.unique(groups):
            ix = np.flatnonzero(groups == gid)
            s[ix] = rng.permutation(s[ix])
        null.append(J_pairs[s].mean() - J_pairs[~s].mean())
    null = np.array(null)
    return {"diff": float(obs), "p_greater": float((1 + (null >= obs).sum()) / (R_ + 1)),
            "p_less": float((1 + (null <= obs).sum()) / (R_ + 1)), "n_same": int(same.sum()), "n_diff": int((~same).sum()),
            "J_same": float(J_pairs[same].mean()), "J_diff": float(J_pairs[~same].mean())}


# --------------------------------------------------------------------------------------------- G12
def g12(rng):
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet")
    teams = gt.filter((pl.col("goal_no") == 12) & (pl.col("label_kind") == "team") & pl.col("preferred")
                      & pl.col("value").is_in(["gov", "opp"]))
    ch = pl.read_parquet(SH / "chat_core.parquet", columns=["t", "pt_date", "goal_no", "speaker_kind", "agent"]).with_row_index("msg")
    ch = ch.filter(pl.col("goal_no") == 12)
    hm = holdout_mask(ch["pt_date"].to_list(), ch["goal_no"].to_list())
    assert not any(hm)
    uses = pl.read_parquet(ROOT / "data/processed/H34-idea-cascades/markers/uses.parquet").filter(pl.col("cls") != 0)
    u = uses.join(ch.filter(pl.col("speaker_kind") == "agent"), on="msg", how="inner")
    pairs_J, pairs_same, pairs_grp, rows = [], [], [], []
    for gi, (deb, tb) in enumerate(teams.group_by("unit", maintain_order=True)):
        t0, t1 = tb["t_valid_from"].min(), tb["t_valid_to"].max()
        ag = tb["agent"].to_list()
        tm = dict(zip(ag, tb["value"].to_list()))
        x = u.filter((pl.col("t") >= t0) & (pl.col("t") < t1) & pl.col("agent").is_in(ag)).select("marker", "agent").unique()
        items = x["marker"].unique().sort().to_list()
        if len(items) < 30 or len(ag) < 4:
            continue
        pos = {m: i for i, m in enumerate(items)}
        apos = {a: j for j, a in enumerate(ag)}
        X = np.zeros((len(items), len(ag)), np.int8)
        X[[pos[m] for m in x["marker"].to_list()], [apos[a] for a in x["agent"].to_list()]] = 1
        X = L.support(X)
        c = L.counts(X)
        th = L.fit_maxent(c, len(ag), "pairK")[0]
        J = J_matrix(th, len(ag))
        for i, j in itertools.combinations(range(len(ag)), 2):
            pairs_J.append(J[i, j])
            pairs_same.append(tm[ag[i]] == tm[ag[j]])
            pairs_grp.append(gi)
        st = R.unit_stats([X], rng, n_sub=len(ag), S=1, field=True)
        rows.append({"debate": deb[0], "T": int(X.shape[0]), "n": len(ag), **{k: st.get(k) for k in
                     ("rho_F", "phi", "r_HO", "rho_raw", "I_N", "ho_excess_z", "field_r_HO")}})
    res = perm_diff(pairs_J, pairs_same, rng, groups=pairs_grp)
    df = pl.DataFrame(rows)
    agg = {"n_debates": df.height, "T_total": int(df["T"].sum()) if df.height else 0}
    if df.height:
        w = df["T"].to_numpy()
        for k in ("rho_F", "phi", "r_HO", "rho_raw"):
            v = df[k].to_numpy().astype(float)
            ok = np.isfinite(v)
            agg[k + "_wmean"] = float((w[ok] * v[ok]).sum() / w[ok].sum()) if ok.any() else None
        agg["z_ge_2.33"] = int((df["ho_excess_z"].fill_null(np.nan).to_numpy() >= 2.33).sum())
    return {"team_J": res, "debates": rows, "agg": agg}


# --------------------------------------------------------------------------------------------- NE42
def subset_J(X, rooms, rng, S=30, n=6):
    """Average J_ij over random subsets holding the pair (K-pairwise fits); returns pair lists."""
    N = X.shape[1]
    acc = np.zeros((N, N))
    cnt = np.zeros((N, N))
    for sub in R._subsets(N, min(n, N), S, rng):
        Xs = L.support(X[:, sub])
        if Xs.shape[0] < 30:
            continue
        th = L.fit_maxent(L.counts(Xs), len(sub), "pairK")[0]
        J = J_matrix(th, len(sub))
        for a, b in itertools.combinations(range(len(sub)), 2):
            acc[sub[a], sub[b]] += J[a, b]
            cnt[sub[a], sub[b]] += 1
    out = []
    for i, j in itertools.combinations(range(N), 2):
        if cnt[i, j] > 0 and rooms[i] >= 0 and rooms[j] >= 0:
            out.append((acc[i, j] / cnt[i, j], rooms[i] == rooms[j]))
    return out


def ne42(rng):
    rep = pl.read_parquet(BASE / "results" / "units_conv.parquet").filter(pl.col("variant") == "main")
    units = {u: rep.filter(pl.col("unit") == u).to_dicts() for u in ("39", "40", "41")}
    summary = {u: {k: (v[0].get(k) if v else None) for k in ("phi", "phi_lo", "phi_hi", "rho_F", "rho_F_lo", "rho_F_hi",
                                                             "r_HO", "ho_excess_z", "I_N", "field_r_HO")}
               for u, v in units.items()}
    room_tests = {}
    for u in ("39", "41"):
        mats, meta = R.load_unit(u, "conv")
        Js, same, grp = [], [], []
        for k, (X, m) in enumerate(zip(mats, meta)):
            if len(set(m["rooms"][m["rooms"] >= 0].tolist())) < 2:
                continue
            for jv, s in subset_J(X, m["rooms"], rng):
                Js.append(jv)
                same.append(s)
                grp.append(k)
        room_tests[u] = perm_diff(Js, same, rng, groups=grp) if Js and any(same) and not all(same) else None
    return {"units": summary, "room_J": room_tests}


# --------------------------------------------------------------------------------------------- G51 sweep
def g51(rng):
    rows = []
    for u in ("51c", "51g"):
        mats, _ = R.load_unit(u, "conv")
        for n, S in ((4, 6), (6, 6), (8, 6), (10, 2)):
            if n == 10 and u != "51g":
                continue
            st = R.unit_stats(mats, rng, n_sub=n, S=S, field=True)
            rows.append({"unit": u, "n": n, **{k: st.get(k) for k in ("rho_F", "phi", "r_HO", "rho_raw", "I_N",
                                                                      "ho_excess_z", "field_r_HO", "field_rho_F",
                                                                      "n_subset_days")}})
            print(rows[-1], flush=True)
    return {"sweep": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="g12,ne42,g51")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for name in a.only.split(","):
        rng = np.random.default_rng(zlib.crc32(name.encode()))
        res = {"g12": g12, "ne42": ne42, "g51": g51}[name](rng)
        (OUT / f"{name}.json").write_text(json.dumps(res, indent=1, default=float))
        print(name, json.dumps(res, default=float)[:1500])


if __name__ == "__main__":
    main()
