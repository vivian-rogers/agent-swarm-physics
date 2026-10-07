"""H137 synthetic validation (axis F) on real skeletons.

Skeleton units: G38 (38a-38e), G31 (31a-31d), 51c, 51h. Real agents, call clocks, read sets with naming flags
(ledger), in-flight named messages and naming weights. Project hops are simulated call by call:
  - hop calls: Bernoulli(p0) per call, p0 = target hops / calls of the unit (target from --calib);
  - destination b != current: weight q_b * exp(beta_s * s_b + rho * held_before_b) * m_b (Glauber destination step;
    the stay utility is set so the hop rate stays p0 in every world, so all worlds run at the real hop count);
  - q_b: project popularity from the calibration source; s_b: share of present others on b; beta_s 2, rho 1.
Worlds:
  W0  no following (m_b = 1).
  W1  H137: m_b = prod_{j present on b} (1 + R_named[c, j])^J, J = 1.0 (W1) and 0.5 (W1h).
  W2  popularity: m_b = (1 + sum_{k present on b} pop_k)^1.0, pop_k = naming in-degree / mean (no naming effect).
  W3  co-arrival (H11): 30% of hops come in pairs that arrive at one project within the same hour in random order.
  W4  broadcast following: m_b = prod_j (1 + R_all[c, j])^1.0 (every read message of j, named or not).
Statistics per run (pooled over the 11 units; per-unit where the rule is per unit): O1 mean A (one-way) vs N1 flip
null; O2 theta_name with controls (pair bootstrap CI, N2 within-stratum permutation p) and without controls; O3 class
means vs N1 and the contrast sigma_one - sigma_none (pair bootstrap); O4 read vs in-flight rate difference.

Calibration details (calls): per-agent hop probability per call = the agent's real hops / calls; 25.7% of hops
are followed by a return to the previous project within 1-5 own calls (project_calls flicker share); destination
preferences mix each agent's own labelled-call profile with global popularity, (lambda, beta_s) tuned on a ladder in
W0 so the follow-hop fraction matches the real one (structural count, no direction).
Added statistics (candidate amendments, decided on synthetic only): theta_act = O2 with a hopper-propensity control
(leave-pair-out follow hops made by each member); N1b = propensity-adjusted direction null for O1/O3.

Calibration (--calib):
  h129     target hops and project popularity from H129's attention hops/visits (existing table; used before
           project_calls exists).
  calls    target hops and project popularity from infra/shared/project_calls.py labels (structural counts only:
           number of hops and labelled calls per project; no follow direction).

Usage: uv run python hypotheses/H137-nonreciprocal-potts-named-pairs/analysis/synthetic.py --calib h129 --runs 300
"""
from __future__ import annotations

import argparse
import os
import bisect
import datetime as dt
import json
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h137lib as L  # noqa: E402

UNITS = ["38a", "38b", "38c", "38d", "38e", "31a", "31b", "31c", "31d", "51c", "51h"]
OUT = L.D / "synthetic"
WORLDS = {"W0": {}, "W1": {"J": 1.0}, "W1h": {"J": 0.5}, "W2": {"pop": 1.0}, "W3": {"coarr": 0.3}, "W4": {"Jall": 1.0},
          "W1j2": {"J": 2.0}, "W1j3": {"J": 3.0}, "W1j5": {"J": 5.0}}  # W1j2-W1j5: added (minimum detectable J)
BETA_S, RHO = 2.0, 1.0


# ============================================================================================ skeletons
CACHE = Path(os.environ.get("H137_CACHE", str(OUT / "skeletons")))


def skeleton(unit: str) -> dict:
    p = CACHE / f"{unit}.pkl"
    if p.exists():
        return pickle.loads(p.read_bytes())
    S = L.load_skeleton(unit)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(pickle.dumps(S))
    return S


def unit_of_day(units):
    pu = L.units_table().filter(pl.col("unit_id").is_in(units))
    return {d: u for u, ds in pu.select("unit_id", "days").iter_rows() for d in ds}


def calib_h129(units) -> dict:
    """Per unit: target hops and project popularity (visit dwell sums) from H129's attention channel."""
    dmap = unit_of_day(units)
    out = {u: {"hops": 0, "pop": {}} for u in units}
    for g in sorted({int(u[:2]) for u in units}):
        base = L.ROOT / f"data/processed/H129-project-cycle-currents/G{g:02d}"
        h = pl.read_parquet(base / "hops_attention.parquet")
        v = pl.read_parquet(base / "visits_attention.parquet")
        for df, tcol in ((h, "t"), (v, "t_arr")):
            df_ = df.with_columns(pl.from_epoch((pl.col(tcol) * 1e6).cast(pl.Int64), time_unit="us")
                                  .dt.replace_time_zone("UTC").dt.convert_time_zone("America/Los_Angeles")
                                  .dt.strftime("%Y-%m-%d").alias("d"))
            df_ = df_.with_columns(pl.col("d").replace_strict(dmap, default=None).alias("u")).filter(pl.col("u").is_not_null())
            if tcol == "t":
                for u, n in df_.group_by("u").len().iter_rows():
                    out[u]["hops"] = int(n)
            else:
                for u, r, dw in df_.group_by("u", "repo").agg(pl.col("dwell").sum()).iter_rows():
                    out[u]["pop"][r] = out[u]["pop"].get(r, 0) + int(dw)
    return out


def calib_calls(units) -> dict:
    """Per unit (structural counts only, no follow direction): project hops (call) per agent, labelled calls per
    project, and the follow-hop fraction (structure.parquet). The share weight beta_s is tuned in W0 to that fraction."""
    import real_labels as RL  # noqa: E402
    st = pl.read_parquet(L.D / "results/structure.parquet")
    ff = {u: (f / h if h else 0.0) for u, f, h in st.select("unit", "follow_hops", "hops").iter_rows()}
    out = {}
    for u in units:
        S = skeleton(u)
        lab = RL.labels_for(S)
        hops = int(lab["hop"].sum())
        vals, cnt = np.unique(lab["label"][lab["label"] >= 0], return_counts=True)
        order = np.argsort(-cnt, kind="stable")
        vals, cnt = vals[order], cnt[order]
        col = {int(v): k for k, v in enumerate(vals)}
        own = np.zeros((S["A"], len(vals)))
        m = lab["label"] >= 0
        np.add.at(own, (S["ag"][m], np.array([col[int(v)] for v in lab["label"][m]], dtype=np.int64)), 1)
        hk = np.bincount(S["ag"][lab["hop"]], minlength=S["A"]).astype(float)
        ck = np.bincount(S["ag"], minlength=S["A"]).astype(float)
        out[u] = {"hops": hops, "pop": {int(a): int(b) for a, b in zip(vals, cnt)}, "own": own,
                  "p_agent": (hk / np.maximum(ck, 1)).tolist(), "follow_frac": ff.get(u, 0.0)}
    return out


LADDER = ((0.02, 0.0), (0.1, 0.0), (0.25, 0.0), (0.5, 0.0), (0.75, 0.0), (1.0, 0.0), (1.0, 1.0), (1.0, 2.0),
          (1.0, 4.0), (1.0, 8.0))


def tune_beta(S, cal, rng, grid=LADDER, reps=3) -> tuple:
    """(lambda, beta_s) on a one-dimensional ladder whose W0 follow-hop fraction is closest to the real one
    (structural count). lambda mixes agent-own project preferences (0) with global popularity (1)."""
    best, bd = (1.0, BETA_S), np.inf
    for b in grid:
        fr = []
        for _ in range(reps):
            cur, label, hop = simulate(S, cal, {}, rng, mix=b)
            fh = L.follow_hops(S, cur, label, hop)
            fr.append((fh["call"].n_unique() if fh.height else 0) / max(hop.sum(), 1))
        d = abs(np.mean(fr) - cal["follow_frac"])
        if d < bd:
            best, bd = b, d
    return best


# ============================================================================================ simulator
FLICKER, FLICKER_MAX = 0.257, 5  # project_calls: 25.7% of hops return to the previous project within 5 calls


def simulate(S: dict, cal: dict, world: dict, rng, mix: tuple | None = None) -> tuple:
    import heapq
    n, A = S["n"], S["A"]
    lam, beta_s = cal.get("mix", (1.0, BETA_S)) if mix is None else mix
    pops = np.array(sorted(cal["pop"].values(), reverse=True), dtype=float)
    if pops.size < 2:
        pops = np.array([1.0, 1.0])
    K = pops.size
    q = pops / pops.sum()
    if "own" in cal and cal["own"].shape[1] == K:
        own = cal["own"]
        rs = own.sum(axis=1, keepdims=True)
        ownn = np.where(rs > 0, own / np.maximum(rs, 1), q[None, :])
        QA = (1 - lam) * ownn + lam * q[None, :]
        QA = np.maximum(QA, 1e-12)
    else:
        QA = np.tile(q, (A, 1))
    logQA = np.log(QA)
    ag, last, present, prev = S["ag"], S["last"], S["present"], S["prev"]
    if "p_agent" in cal:
        p_call = np.asarray(cal["p_agent"])[ag]
        flick = FLICKER
    else:
        p_call = np.full(n, min(0.5, max(cal["hops"], 1) / n))
        flick = 0.0
    pos = np.empty(n, dtype=np.int64)
    for k in range(A):
        pos[S["by_agent"][k]] = np.arange(S["by_agent"][k].size)
    init = np.array([rng.choice(K, p=QA[k] / QA[k].sum()) for k in range(A)])
    hop_pos = [[] for _ in range(A)]
    hop_lab = [[] for _ in range(A)]
    held = np.zeros((A, K), dtype=bool)
    held[np.arange(A), init] = True

    def lab_at(j, c_):  # label of agent j after its call c_
        k = bisect.bisect_right(hop_pos[j], pos[c_]) - 1
        return hop_lab[j][k] if k >= 0 else init[j]

    J, Jall, popw, coarr = world.get("J", 0.0), world.get("Jall", 0.0), world.get("pop", 0.0), world.get("coarr", 0.0)
    pop_k = None
    if popw:
        ind = S["W"].sum(axis=0)
        pop_k = ind / max(ind.mean(), 1e-9)
    # the flicker returns are added hops, so base hop calls are thinned to keep the real hop count
    hop_call = rng.random(n) < p_call * (1 - coarr) / (1 + flick)
    forced = {}
    if coarr:
        n_ev = rng.poisson(coarr * cal["hops"] / 2)
        tc = S["tc"]
        for _ in range(n_ev):
            c0 = rng.integers(0, n)
            others = np.flatnonzero(present[c0])
            if others.size < 1:
                continue
            j2 = rng.choice(others)
            pair = [int(ag[c0]), int(j2)]
            b = int(rng.choice(K, p=q))
            for a in pair:
                tt = tc[c0] + rng.uniform(0, 3600)
                ix = S["by_agent"][a]
                p_ = np.searchsorted(tc[ix], tt)
                if p_ < ix.size and S["day"][ix[p_]] == S["day"][c0]:
                    forced[int(ix[p_])] = b
    heap = list(np.flatnonzero(hop_call)) + list(forced)
    heapq.heapify(heap)
    seen = set()
    dest = np.full(n, -1, dtype=np.int64)
    while heap:
        c = int(heapq.heappop(heap))
        if c in seen:
            continue
        seen.add(c)
        i = int(ag[c])
        cur = lab_at(i, prev[c]) if prev[c] >= 0 else init[i]
        if c in forced:
            b = forced[c]
            if b == cur:
                continue
        else:
            js = np.flatnonzero(present[c])
            labs = np.array([lab_at(j, last[c, j]) for j in js], dtype=np.int64)
            s = np.bincount(labs, minlength=K) / max(js.size, 1) if js.size else np.zeros(K)
            logw = logQA[i] + beta_s * s + RHO * held[i]
            if J and js.size:
                np.add.at(logw, labs, J * np.log1p(S["R_nam"][c, js]))
            if Jall and js.size:
                np.add.at(logw, labs, Jall * np.log1p(S["R_all"][c, js]))
            if popw and js.size:
                tot = np.bincount(labs, weights=pop_k[js], minlength=K)
                logw += popw * np.log1p(tot)
            logw[cur] = -np.inf
            w = np.exp(logw - logw.max())
            b = int(rng.choice(K, p=w / w.sum()))
        hop_pos[i].append(pos[c])
        hop_lab[i].append(b)
        held[i, b] = True
        dest[c] = b
        if flick and c not in forced and rng.random() < flick:
            ix = S["by_agent"][i]
            k = pos[c] + int(rng.integers(1, FLICKER_MAX + 1))
            if k < ix.size and S["day"][ix[k]] == S["day"][c]:
                forced[int(ix[k])] = cur
                heapq.heappush(heap, int(ix[k]))
    # hop_pos must be sorted per agent for lab_at; heap order is global time order, so it is
    # labels after every call, carried forward per agent
    label = np.empty(n, dtype=np.int64)
    for k in range(A):
        ix = S["by_agent"][k]
        lab = np.full(ix.size, init[k], dtype=np.int64)
        for p_, b in zip(hop_pos[k], hop_lab[k]):
            lab[p_:] = b
        label[ix] = lab
    cur = np.where(prev >= 0, label[np.clip(prev, 0, None)], init[ag])
    hop = (dest >= 0) & (label != cur)
    return cur, label, hop


# ============================================================================================ statistics
def unit_stats(S, cur, label, hop):
    fh = L.follow_hops(S, cur, label, hop)
    pt = L.pair_table(S, fh)
    P = pt["pairs"].with_columns(pl.lit(S["unit"]).alias("unit"))
    R = L.hop_rows(S, fh, pt["pairs"]).with_columns(pl.lit(S["unit"]).alias("unit"))
    O = L.readout_rows(S, cur, label, hop).with_columns(pl.lit(S["unit"]).alias("unit"))
    Q = L.sigma_pairs(P)
    fw = L.fh_row_weights(fh, S["unit"])
    one = Q.filter(pl.col("cls") == "one")
    pre = {"follow_one": float(one["n_follow"].sum()), "pairs_one": int(one.height),
           "testable": bool(one["n_follow"].sum() >= 20 and one.height >= 8),
           "hops": int(hop.sum()), "follow": int(fh["call"].n_unique()) if fh.height else 0}
    return R, Q, O, fw, pre


def run_stats_light(per_unit, rng, nd=200, nb=100):
    """Power check at the pooled real counts: only P1 (A1) and P4."""
    R = pl.concat([x[0] for x in per_unit])
    O = pl.concat([x[2] for x in per_unit])
    th_a = L.theta_fit(R, controls="act")
    lo_a, hi_a = L.theta_boot(R, rng, B=nb, controls="act")
    p2_a = L.theta_n2(R, rng, draws=nd, controls="act")
    e, lo4, hi4, n1, n0 = L.readout_contrast(O, rng, B=nb)
    return {"pre": [x[4] for x in per_unit], "theta_act": th_a, "theta_act_lo": lo_a, "theta_act_hi": hi_a,
            "theta_act_p": p2_a, "o4": e, "o4_lo": lo4, "o4_hi": hi4, "o4_n_read": n1, "o4_n_if": n0, "n_rows": R.height}


def run_stats(per_unit, rng, nd=500, nb=200):
    R = pl.concat([x[0] for x in per_unit])
    Q = pl.concat([x[1] for x in per_unit])
    O = pl.concat([x[2] for x in per_unit])
    fw = {}
    for x in per_unit:
        fw.update(x[3])
    res = {"pre": [x[4] for x in per_unit]}
    th = L.theta_fit(R)
    lo, hi = L.theta_boot(R, rng, B=nb)
    p2 = L.theta_n2(R, rng, draws=nd)
    th_raw = L.theta_fit(R, controls=False)  # card's raw direction (no controls); CI below
    lo_r, hi_r = L.theta_boot(R, rng, B=nb, controls=False)
    th_a = L.theta_fit(R, controls="act")
    lo_a, hi_a = L.theta_boot(R, rng, B=nb, controls="act")
    p2_a = L.theta_n2(R, rng, draws=nd, controls="act")
    res.update(theta_act=th_a, theta_act_lo=lo_a, theta_act_hi=hi_a, theta_act_p=p2_a)
    res.update(theta=th, theta_lo=lo, theta_hi=hi, theta_p=p2, theta_raw=th_raw, theta_raw_lo=lo_r, theta_raw_hi=hi_r,
               n_rows=R.height, n_rows_z=int((R["z"] != 0).sum()) if R.height else 0)
    nul = L.flip_null(Q, rng, draws=nd, fh_rows=fw)
    one = Q.filter(pl.col("cls") == "one")
    A_obs = float(one["A"].mean()) if one.height else np.nan
    res["A_one"] = A_obs
    res["A_one_p"] = float((np.sum(nul["A_one"] >= A_obs) + 1) / (nd + 1)) if one.height else np.nan
    res["A_one_null_mean"] = float(np.nanmean(nul["A_one"])) if one.height else np.nan
    for c in L.CLASSES:
        m = Q.filter(pl.col("cls") == c)
        v = float(m["sigma"].mean()) if m.height else np.nan
        res[f"sig_{c}"] = v
        res[f"sig_{c}_p"] = float((np.sum(nul[f"sig_{c}"] >= v) + 1) / (nd + 1)) if m.height else np.nan
        res[f"sig_{c}_null"] = float(np.nanmean(nul[f"sig_{c}"])) if m.height else np.nan
    est, clo, chi = L.pair_boot_contrast(Q, rng, B=nb)
    res.update(contrast=est, contrast_lo=clo, contrast_hi=chi)
    an = L.adj_null(R, Q, rng, draws=nd)
    for k in ("sig_one", "sig_mutual", "sig_none", "A_one", "contrast"):
        v = res[k]
        res[f"{k}_padj"] = float((np.sum(an[k] >= v) + 1) / (np.sum(np.isfinite(an[k])) + 1)) if np.isfinite(v) else np.nan
    # per-unit symmetry tests for P2 (sigma_mutual, sigma_none inside their flip nulls), testable units only
    p2u = []
    for x in per_unit:
        if not x[4]["testable"]:
            continue
        q_ = x[1]
        nu = L.flip_null(q_, rng, draws=200, fh_rows=x[3])
        na = L.adj_null(x[0], q_, rng, draws=200)
        out = {}
        for c in ("mutual", "none"):
            m = q_.filter(pl.col("cls") == c)
            if m.height:
                v = float(m["sigma"].mean())
                out[c] = float((np.sum(nu[f"sig_{c}"] >= v) + 1) / 201)
                out[c + "_adj"] = float((np.sum(na[f"sig_{c}"] >= v) + 1) / (np.sum(np.isfinite(na[f"sig_{c}"])) + 1))
        p2u.append(out)
    res["p2_units"] = p2u
    e, lo4, hi4, n1, n0 = L.readout_contrast(O, rng, B=nb)
    res.update(o4=e, o4_lo=lo4, o4_hi=hi4, o4_n_read=n1, o4_n_if=n0)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calib", default="h129", choices=["h129", "calls"])
    ap.add_argument("--runs", type=int, default=300)
    ap.add_argument("--worlds", default=",".join(WORLDS))
    ap.add_argument("--units", default=",".join(UNITS))
    ap.add_argument("--nd", type=int, default=500)
    ap.add_argument("--nb", type=int, default=200)
    ap.add_argument("--tag", default="")
    ap.add_argument("--light", action="store_true", help="only P1 (A1) and P4 (pooled power at real counts)")
    ap.add_argument("--all-units", action="store_true", help="every non-reserved unit with follow rows (structure)")
    a = ap.parse_args()
    units = a.units.split(",")
    if a.all_units:
        st = pl.read_parquet(L.D / "results/structure.parquet")
        units = st.filter(pl.col("follow_rows") > 0)["unit"].to_list()
    t0 = time.time()
    Ss = {u: skeleton(u) for u in units}
    print(f"skeletons {time.time() - t0:.0f}s", {u: (S['n'], S['A']) for u, S in Ss.items()}, flush=True)
    cal = calib_h129(units) if a.calib == "h129" else calib_calls(units)
    if a.calib == "calls":
        trng = np.random.default_rng(20261007)
        for u in units:
            cal[u]["mix"] = tune_beta(Ss[u], cal[u], trng)
        print("mix (lambda, beta_s)", {u: cal[u]["mix"] for u in units}, flush=True)
    print("calibration", {u: (c["hops"], len(c["pop"])) for u, c in cal.items()}, flush=True)
    tag = a.tag or a.calib
    od = OUT / tag
    od.mkdir(parents=True, exist_ok=True)
    (od / "calibration.json").write_text(json.dumps({u: {"hops": c["hops"], "n_projects": len(c["pop"]),
                                                         "mix": c.get("mix"),
                                                         "follow_frac": c.get("follow_frac"),
                                                         "calls": int(Ss[u]["n"]), "agents": int(Ss[u]["A"])}
                                                     for u, c in cal.items()}, indent=1))
    for wname in a.worlds.split(","):
        world = WORLDS[wname]
        fp = od / f"{wname}.jsonl"
        done = sum(1 for _ in open(fp)) if fp.exists() else 0
        with open(fp, "a") as f:
            for r in range(done, a.runs):
                rng = np.random.default_rng([20261007, list(WORLDS).index(wname), r])
                per_unit = []
                for u in units:
                    cur, label, hop = simulate(Ss[u], cal[u], world, rng)
                    per_unit.append(unit_stats(Ss[u], cur, label, hop))
                res = (run_stats_light if a.light else run_stats)(per_unit, rng, nd=a.nd, nb=a.nb)
                res.update(world=wname, run=r)
                f.write(json.dumps(res, default=float) + "\n")
                f.flush()
                if a.light:
                    print(f"{wname} run {r} {time.time() - t0:.0f}s theta_act {res['theta_act']:.3f} o4 {res['o4']:.4f} "
                          f"[{res['o4_lo']:.4f},{res['o4_hi']:.4f}]", flush=True)
                elif r % 25 == 0:
                    print(f"{wname} run {r} {time.time() - t0:.0f}s theta {res['theta']:.2f} [{res['theta_lo']:.2f},"
                          f"{res['theta_hi']:.2f}] p {res['theta_p']:.3f}", flush=True)
    print(f"done {time.time() - t0:.0f}s {dt.datetime.now(dt.timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
