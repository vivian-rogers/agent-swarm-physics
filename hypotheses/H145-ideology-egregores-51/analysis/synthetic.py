"""H145 synthetic validation (axis F) on the real #51 skeleton (2-h bins: real presence, agent vocabularies and
agent-bin activity of all 2,011 real elements; planted elements appended). Run before any H145 test on real data.

Stages
  disc   discovery: planted recovery under the card's PPMI expectation (agent-constant) and under Amendment A1
         (activity-adjusted expectation, BH-FDR 0.05 edges); P1 count against 20 null pipelines (A2: each element's
         series rotated within the agent's present bins) at gamma 1 (A3); proof that the card's within-agent,
         within-day time shuffle leaves the graph unchanged.
  tests  P2 (as written: rho_K(5) - J_K(5); amended A4: renewal contrast D_K(5)) against 200 frequency-matched
         pseudo-patterns, and P3 (colonial A excess and integration Delta, Besag-Clifford h 10, n_max 60, >= 30 draws)
         on the planted memeplexes (instrument power) and on the discovered match (end-to-end).

Usage: uv run python hypotheses/H145-ideology-egregores-51/analysis/synthetic.py --stage disc|tests --worlds W0,W_field
       [--reps 20] [--tag a]
Writes data/processed/H145-ideology-egregores-51/synthetic/<stage>_<tag>.jsonl (one row per replicate).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h145lib as L  # noqa: E402
import individuality as IND  # noqa: E402
import memeplex as MP  # noqa: E402
import build as B  # noqa: E402

SYN = L.OUT / "synthetic"
GAMMA = 1.0
FDR = 0.05
N_NULL_PIPE = 20
N_PSEUDO_P2 = 200
BC = dict(h=10, n_max=60, min_draws=30)
WORLDS = {
    "W0": dict(kind="W0"),
    "W_field": dict(kind="W_field"),
    "W_field_noisy": dict(kind="W_field", field_noise=0.7),
    "W_hub": dict(kind="W_hub"),
    "W_prior": dict(kind="W_prior"),
    "W_sticky": dict(kind="W_sticky"),
    "W_egr_0.2": dict(kind="W_egr3", rho=0.2),
    "W_egr_0.4": dict(kind="W_egr3", rho=0.4),
}


def js(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def graph_A1(panel):
    return MP.ppmi_graph(panel, 3, activity=True, fdr=FDR)


def null_pipeline(panel, rng, n=N_NULL_PIPE, scope="agent"):
    """P1 null (A2): each element's series circularly shifted within the agent's present bins (scope 'agent'; 'day'
    = within agent-day, descriptive), A1 graph, gamma 1, Louvain 1 seed. Returns qualifying hub-free counts."""
    counts = []
    for i in range(n):
        pn = MP.rotate_elements(panel, np.random.default_rng(int(rng.integers(1 << 31))), scope=scope)
        res = MP.discover(pn, GAMMA, W=graph_A1(pn), n_seeds=1)
        counts.append(int(res["n_qualify_hub_free"]))
    return counts


def stage_disc(sk, name, spec, rep, rng):
    w = L.world(sk, spec["kind"], rng, rho=spec.get("rho", 0.0), field_noise=spec.get("field_noise", 0.0))
    pn = w["panel"]
    row = {"world": name, "rep": rep}
    variants = {"card": dict(activity=False, p_edge=0.01, fdr=None), "act": dict(activity=True, p_edge=0.01, fdr=None),
                "A1": dict(activity=True, p_edge=None, fdr=FDR)}
    for vn, kw in variants.items():
        W = MP.ppmi_graph(pn, 3, **kw)
        r = MP.discover(pn, GAMMA, W=W)
        row[vn] = {"n_qualify_hub_free": r["n_qualify_hub_free"], "edges": int((W > 0).sum() // 2),
                   "max_size": max([c["n_elements"] for c in r["communities"]] or [0]),
                   "planted": [L.planted_match(r["communities"], K) for K in w["planted_all"]]}
        if vn == "card" and rep == 0:
            Wsh = MP.ppmi_graph(MP.rotate_agent_bins(pn, rng), 3, **kw)
            row["timeshuffle_graph_identical"] = bool(np.allclose(Wsh, W))
    nc = null_pipeline(pn, rng)
    row["A1"]["null_counts"] = nc
    if rep < 5:
        row["A1"]["null_counts_day"] = null_pipeline(pn, rng, n=5, scope="day")
    k = row["A1"]["n_qualify_hub_free"]
    row["A1"]["P1_pass"] = bool(k >= 3 and k > np.quantile(nc, 0.95))
    return row


def p2_test(pn, K, es, rng, m=2):
    obs = L.renewal(pn, K, m)
    obs["R"] = L.host_memory(pn, K, m)
    pools = L.matched_pool(es, K)
    null = []
    for _ in range(N_PSEUDO_P2):
        P = L.draw_pseudo(pools, rng)
        r = L.renewal(pn, P, m)
        r["R"] = L.host_memory(pn, P, m)
        null.append(r)
    out = {"obs": obs}
    v = np.array([x["R"] for x in null], float)
    v = v[np.isfinite(v)]
    q05 = float(np.quantile(v, 0.05)) if len(v) else np.nan
    out["R"] = {"obs": obs["R"], "q05": q05, "null_mean": float(v.mean()) if len(v) else np.nan,
                "pass": bool(np.isfinite(obs["R"]) and obs["R"] < q05)}
    for key in ("diff", "D"):
        v = np.array([x[key] for x in null], float)
        v = v[np.isfinite(v)]
        q95 = float(np.quantile(v, 0.95)) if len(v) else np.nan
        out[key] = {"obs": obs[key], "q95": q95, "pass": bool(np.isfinite(obs[key]) and obs[key] > q95 and
                                                             (obs[key] > 0 if key == "diff" else True))}
    return out


def p3_test(pn, K, eb, es, rng):
    ks = L.krakauer_pattern(pn, K, eb)
    if ks is None:
        return {"ok": False}
    pools = L.matched_pool(es, K)
    cache = {}

    def draw_stat(stat):
        def f():
            key = len(cache)
            P = L.draw_pseudo(pools, rng)
            r = L.krakauer_pattern(pn, P, eb)
            if r is None:
                return np.nan
            cache[key] = r
            return getattr(r, stat)
        return f
    ra = IND.besag_clifford(ks.A, draw_stat("A"), **BC)
    # Delta: reuse the same pseudo draws (their Delta) and extend if needed
    dvals = [c.Delta for c in cache.values() if np.isfinite(c.Delta)]
    it = iter(dvals)

    def draw_d():
        try:
            return next(it)
        except StopIteration:
            P = L.draw_pseudo(pools, rng)
            r = L.krakauer_pattern(pn, P, eb)
            return np.nan if r is None else r.Delta
    rd = IND.besag_clifford(ks.Delta, draw_d, **BC)
    return {"ok": True, "A": ks.A, "A_star": ks.A_star, "nC": ks.nC, "Delta": ks.Delta,
            "A_z": ra["z"], "A_p": ra["p"], "A_n": ra["n"], "A_mu": ra["mu"],
            "D_z": rd["z"], "D_p": rd["p"], "D_n": rd["n"], "D_mu": rd["mu"],
            "pass_A": bool(np.isfinite(ra["z"]) and ra["z"] >= 2), "pass_D": bool(np.isfinite(rd["z"]) and rd["z"] >= 2)}


def stage_tests(sk, name, spec, rep, rng):
    w = L.world(sk, spec["kind"], rng, rho=spec.get("rho", 0.0), field_noise=spec.get("field_noise", 0.0))
    pn = w["panel"]
    es = L.element_stats(pn)
    eb = L.env_base_synthetic(pn, field=w["field"])
    row = {"world": name, "rep": rep, "patterns": []}
    W1 = graph_A1(pn)
    r1 = MP.discover(pn, GAMMA, W=W1)
    if True:
        targets = []
        for j, K in enumerate(w["planted_all"]):
            targets.append((f"planted{j}", K))
            m = L.planted_match(r1["communities"], K)
            if m["jaccard"] >= 0.5 and m["jaccard"] < 1.0 and m.get("qualifies"):
                best = max(r1["communities"], key=lambda c: len(set(c["elements"]) & set(K)) / len(set(c["elements"]) | set(K)))
                targets.append((f"discovered{j}", best["elements"]))
            row.setdefault("recovered", []).append({"jaccard": m["jaccard"], "qualifies": m.get("qualifies"),
                                                    "hub_free": m.get("hub_free")})
            if spec["kind"] != "W_egr3":
                break
    for lab, K in targets:
        ps = MP.pattern_stats(pn, K, 2)
        row["patterns"].append({"target": lab, "n_el": len(K), "h_K": ps["h_K"], "n_hosts": ps["n_hosts"],
                                "qualifies": MP.qualifies(ps), "P2": p2_test(pn, K, es, rng), "P3": p3_test(pn, K, eb, es, rng)})
    return row


def main():
    a = sys.argv
    stage = a[a.index("--stage") + 1]
    worlds = a[a.index("--worlds") + 1].split(",") if "--worlds" in a else list(WORLDS)
    reps = int(a[a.index("--reps") + 1]) if "--reps" in a else 20
    tag = a[a.index("--tag") + 1] if "--tag" in a else "a"
    SYN.mkdir(parents=True, exist_ok=True)
    P = B.load_panel(120)
    sk = L.skeleton(P)
    out = SYN / f"{stage}_{tag}.jsonl"
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            r = json.loads(line)
            done.add((r["world"], r["rep"]))
    for name in worlds:
        spec = WORLDS[name]
        for rep in range(reps):
            if (name, rep) in done:
                continue
            t = time.time()
            rng = np.random.default_rng([20261009, list(WORLDS).index(name), rep, 0 if stage == "disc" else 1])
            row = stage_disc(sk, name, spec, rep, rng) if stage == "disc" else stage_tests(sk, name, spec, rep, rng)
            row["sec"] = round(time.time() - t, 1)
            with open(out, "a") as f:
                f.write(json.dumps(row, default=js) + "\n")
            L.log(name, rep, f"{row['sec']}s")


if __name__ == "__main__":
    main()
