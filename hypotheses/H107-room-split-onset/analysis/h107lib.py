"""H107 estimators (card Observables O1-O7): onset ratio r1, disattenuated onset cosine c1, onset projection pi1,
growth profile, half-day profile, inherited repo field u_repo and f_repo, carried-content field u_prev, work persistence
kappa_w, and the G41 re-split memory test. Built on rslib (joint-relabel excess cross-products)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rslib as R  # noqa: E402

DATA = R.ROOT / "data/processed/H107-room-split-onset"


def load_inputs():
    st = pl.read_parquet(DATA / "statements.parquet")
    return st


def final_block(n_days: int) -> list[int]:
    k = max(1, math.ceil(n_days / 3))
    return list(range(n_days - k, n_days))


def onset(pday: R.Panel, phalf: R.Panel | None, n_perm: int = 2000, seed: int = 0) -> dict:
    """O1-O4 on a day panel (and the half-day panel for O4)."""
    nd = len(pday.bins)
    PI = R.perms(pday.lab, n_perm, seed)
    F = final_block(nd)
    xF, mF = R.block(pday, F)
    xs = [pday.X[b] for b in range(nd)] + [xF]
    ms = [pday.M[b] for b in range(nd)] + [mF]
    C, obs, Z, Pv = R.excess_matrix(xs, ms, pday.lab, PI)
    E = np.diag(C)[:nd]; EF = C[nd, nd]; pF = Pv[nd, nd]
    out = {"n_days": nd, "final_block": [pday.bins[b][0] for b in F], "E_day": E.tolist(),
           "p_day": np.diag(Pv)[:nd].tolist(), "E_F": float(EF), "p_F": float(Pv[nd, nd]), "z_F": float(Z[nd, nd]),
           "n_best": pday.info["n_best"], "n_rest": pday.info["n_rest"]}
    E1, C1F, p1 = E[0], C[0, nd], Pv[0, 0]
    out.update(E1=float(E1), p1=float(p1), C1F=float(C1F))
    out["r1"] = float(E1 / EF) if EF > 0 else np.nan
    out["pi1"] = float(C1F / EF) if EF > 0 else np.nan
    out["c1"] = float(C1F / np.sqrt(E1 * EF)) if (E1 > 0 and EF > 0 and p1 < 0.2) else np.nan
    out["c1_raw"] = float(C1F / np.sqrt(E1 * EF)) if (E1 > 0 and EF > 0) else np.nan
    prof = E / EF if EF > 0 else np.full(nd, np.nan)
    out["profile"] = prof.tolist()
    if nd >= 3 and np.all(np.isfinite(E)):
        rk = lambda v: np.argsort(np.argsort(v))  # noqa: E731
        out["spearman_growth"] = float(np.corrcoef(rk(np.arange(nd)), rk(E))[0, 1])
    else:
        out["spearman_growth"] = np.nan
    out["monotone"] = bool(np.isfinite(out["spearman_growth"]) and out["spearman_growth"] >= 0.5 and E[-1] > E[0])
    out["kill_onset"] = bool(pF < 0.05 and np.isfinite(out["r1"]) and np.isfinite(out["c1"]) and out["r1"] >= 0.8
                             and out["c1"] >= 0.7)
    out["ssb_onset"] = bool(pF < 0.05 and np.isfinite(out["r1"]) and out["r1"] <= 0.3)
    out["ssb_onset_growth"] = bool(out["ssb_onset"] and out["monotone"])
    if phalf is not None:
        # first half-day bin of day 1 vs the same final block (built from the day panel, same agents)
        assert list(phalf.agents) == list(pday.agents)
        h0 = 0  # bins sorted (pt_date, half): the first is day 1, half 0 when it exists
        if phalf.bins[0][0] == pday.bins[0][0] and phalf.bins[0][1] == 0:
            e = R.excess(phalf.X[h0], phalf.M[h0], phalf.X[h0], phalf.M[h0], pday.lab, PI)
            c = R.excess(phalf.X[h0], phalf.M[h0], xF, mF, pday.lab, PI)
            out["E_h0"] = e["C"]; out["p_h0"] = e["p"]
            out["r_h0"] = float(e["C"] / EF) if EF > 0 else np.nan
            out["pi_h0"] = float(c["C"] / EF) if EF > 0 else np.nan
            hp = []
            for b in range(len(phalf.bins)):
                eb = R.excess(phalf.X[b], phalf.M[b], phalf.X[b], phalf.M[b], pday.lab, PI)
                hp.append(float(eb["C"] / EF) if EF > 0 and np.isfinite(eb["C"]) else np.nan)
            out["half_profile"] = hp
            out["half_bins"] = [f"{d}|{h}" for d, h in phalf.bins]
    return out


def onset_boot(pday, phalf, n_boot: int = 200, n_perm: int = 200, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    keys = ["r1", "pi1", "c1_raw", "r_h0", "pi_h0", "E_F", "E1"]
    acc = {k: [] for k in keys}
    for b in range(n_boot):
        ix_state = rng.bit_generator.state
        q = R.resample_agents(pday, rng)
        rng2 = np.random.default_rng(seed + 1000 + b)
        qh = None
        if phalf is not None:
            # resample the half-day panel with the same agent draw
            rng_h = np.random.default_rng(); rng_h.bit_generator.state = ix_state
            qh = R.resample_agents(phalf, rng_h)
        o = onset(q, qh, n_perm=n_perm, seed=int(rng2.integers(1 << 30)))
        for k in keys:
            acc[k].append(o.get(k, np.nan))
    ci = {}
    for k, v in acc.items():
        v = np.array(v, dtype=float); v = v[np.isfinite(v)]
        ci[k] = [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) >= 20 else None
    return ci


# ------------------------------------------------------------------------------------------ inherited fields
def repo_vectors(st: pl.DataFrame, V, rm: pl.DataFrame, t0, regime: str) -> dict[str, np.ndarray]:
    """Mean unit statement vector per repo over statements naming it that are dated before t0, same regime."""
    s = st.select("srow", "t", "regime").filter((pl.col("t") < t0) & (pl.col("regime") == regime))
    j = rm.join(s.select("srow"), on="srow", how="semi")
    out = {}
    for repo, g in j.group_by("repo"):
        rows = g["srow"].to_numpy()
        out[repo[0]] = np.asarray(V[rows], dtype=np.float64).mean(0)
    return out


def inherited_repo_field(st, V, rm, arp, P: int, agents, lab, min_members: int = 2):
    """u_repo = unit(h_best - h_rest); h_r = mean over members of sum_sigma w_i(sigma) v_sigma (pre-period work shares)."""
    Pm = R.PRE[P]
    t0 = st.filter(pl.col("goal_no") == P)["t"].min()
    rv = repo_vectors(st, V, rm, t0, R.regime_of(P))
    w = arp.filter(pl.col("goal_no") == Pm)
    h = {R.BEST: [], R.REST: []}
    info = {"pre": Pm, "n_repo_vectors": len(rv), "members_with_field": {}}
    for a, r in zip(agents, lab):
        g = w.filter(pl.col("agent") == int(a))
        g = g.filter(pl.col("repo").is_in(list(rv)))
        if g.height == 0:
            continue
        ww = g["n_commits"].to_numpy().astype(float); ww /= ww.sum()
        h[int(r)].append(sum(wi * rv[rp] for wi, rp in zip(ww, g["repo"].to_list())))
    info["members_with_field"] = {"best": len(h[R.BEST]), "rest": len(h[R.REST])}
    if len(h[R.BEST]) < min_members or len(h[R.REST]) < min_members:
        return None, info
    d = np.mean(h[R.BEST], 0) - np.mean(h[R.REST], 0)
    return d / np.linalg.norm(d), info


def carried_content_field(ad, Xc, consts, P: int, agents, lab, min_members: int = 2):
    """u_prev: members' pre-period means (day-centred agent-day vectors minus a_i) grouped by their P rooms."""
    Pm = R.PRE[P]
    m = ((ad["goal_no"] == Pm) & (ad["regime"] == R.regime_of(P))).to_numpy()
    sub = ad.filter(pl.Series(m)).with_columns(pl.Series("ix", np.nonzero(m)[0]))
    h = {R.BEST: [], R.REST: []}
    for a, r in zip(agents, lab):
        g = sub.filter(pl.col("agent") == int(a))
        if g.height == 0:
            continue
        v = Xc[g["ix"].to_numpy()].mean(0) - consts.get(int(a), 0)
        h[int(r)].append(v)
    info = {"pre": Pm, "best": len(h[R.BEST]), "rest": len(h[R.REST])}
    if len(h[R.BEST]) < min_members or len(h[R.REST]) < min_members:
        return None, info
    d = np.mean(h[R.BEST], 0) - np.mean(h[R.REST], 0)
    return d / np.linalg.norm(d), info


def field_alignment(pday: R.Panel, u: np.ndarray, n_null: int = 2000, seed: int = 1) -> dict:
    """f(X) for X = period (alternating-day halves) and day 1 (statement-parity halves), with the direction null."""
    out = {}
    isb = (pday.lab == R.BEST)[None, :]
    H1, H2, ok = R.alt_day_halves(pday)
    d1 = R.deltas(H1, ok, isb)[0]; d2 = R.deltas(H2, ok, isb)[0]
    xbar, okb = R.block(pday, list(range(len(pday.bins))))
    xw = xbar[okb].copy(); lw = pday.lab[okb]
    for r in (R.BEST, R.REST):
        xw[lw == r] -= xw[lw == r].mean(0)
    f, S = R.split_share(d1, d2, u)
    out["f_period"], out["S_period"] = f, S
    if np.isfinite(f):
        nul = R.direction_null(xw, d1, d2, n_null, seed)
        out["p_period"] = float((1 + (nul >= f).sum()) / (1 + n_null)); out["null_mean_period"] = float(nul.mean())
    if pday.X1 is not None:
        e1 = R.deltas(pday.X1[0], pday.M12[0], isb)[0]; e2 = R.deltas(pday.X2[0], pday.M12[0], isb)[0]
        f1, S1 = R.split_share(e1, e2, u)
        out["f_day1"], out["S_day1"] = f1, S1
        if np.isfinite(f1):
            nul = R.direction_null(xw, e1, e2, n_null, seed + 1)
            out["p_day1"] = float((1 + (nul >= f1).sum()) / (1 + n_null)); out["null_mean_day1"] = float(nul.mean())
    out["rule_period"] = bool(np.isfinite(out.get("f_period", np.nan)) and out["f_period"] >= 0.15
                              and out.get("p_period", 1) < 0.05)
    out["rule_day1"] = bool(np.isfinite(out.get("f_day1", np.nan)) and out["f_day1"] >= 0.15
                            and out.get("p_day1", 1) < 0.05)
    return out


def kappa_w(arp: pl.DataFrame, P: int, agents, lab) -> dict:
    """O7: share of a room's P work in repos its own members worked in during P-, minus the share in repos only the
    other room's members worked in; mean over the two rooms."""
    Pm = R.PRE[P]
    pre = arp.filter(pl.col("goal_no") == Pm); cur = arp.filter(pl.col("goal_no") == P)
    room = {int(a): int(r) for a, r in zip(agents, lab)}
    inh = {r: set(pre.filter(pl.col("agent").is_in([a for a, rr in room.items() if rr == r]))["repo"].to_list())
           for r in (R.BEST, R.REST)}
    vals = {}
    for r, o in ((R.BEST, R.REST), (R.REST, R.BEST)):
        c = cur.filter(pl.col("agent").is_in([a for a, rr in room.items() if rr == r]))
        tot = c["n_commits"].sum()
        if tot == 0 or not inh[r] and not inh[o]:
            vals[r] = None; continue
        own = c.filter(pl.col("repo").is_in(list(inh[r])))["n_commits"].sum() / tot
        oth = c.filter(pl.col("repo").is_in(list(inh[o] - inh[r])))["n_commits"].sum() / tot
        vals[r] = float(own - oth)
    v = [x for x in vals.values() if x is not None]
    return {"kappa_w": float(np.mean(v)) if v else np.nan, "by_room": {str(k): v for k, v in vals.items()},
            "n_inherited": {str(k): len(s) for k, s in inh.items()}}


def resplit_memory(st, V, consts41, consts39, n_perm: int = 2000, seed: int = 41) -> dict:
    """G41 native (P7): excess cross-product of #41 day 1 with the #39 period difference, joint relabel over agents
    eligible in both periods with the same room in both."""
    p41 = R.build_panel(st, V, 41, "day", consts41)
    p39 = R.build_panel(st, V, 39, "day", consts39)
    common = [a for a in p41.agents if a in set(p39.agents)]
    i41 = {a: k for k, a in enumerate(p41.agents)}; i39 = {a: k for k, a in enumerate(p39.agents)}
    same = [a for a in common if p41.lab[i41[a]] == p39.lab[i39[a]]]
    k41 = [i41[a] for a in same]; k39 = [i39[a] for a in same]
    lab = p41.lab[k41]
    x1, m1 = p41.X[0][k41], p41.M[0][k41]
    x39, m39 = R.block(p39, list(range(len(p39.bins))))
    x39, m39 = x39[k39], m39[k39]
    PI = R.perms(lab, n_perm, seed)
    c = R.excess(x1, m1, x39, m39, lab, PI)
    e1 = R.excess(x1, m1, x1, m1, lab, PI); e39 = R.excess(x39, m39, x39, m39, lab, PI)
    cosd = c["C"] / np.sqrt(e1["C"] * e39["C"]) if (e1["C"] > 0 and e39["C"] > 0) else np.nan
    return {"n_common_same_room": len(same), "n_best": int((lab == R.BEST).sum()), "n_rest": int((lab == R.REST).sum()),
            "C": c["C"], "z": c["z"], "p_one": c["p"], "E_day1": e1["C"], "E_39": e39["C"], "cos_dis": float(cosd)}
