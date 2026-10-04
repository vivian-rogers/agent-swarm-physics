"""H116 G26 natives on real data (non-holdout): N1 result step, N1b in-coupling, N1c agent placebos, N2 re-election,
N3 read vs in-flight, N4 EP. Time placebos at the event's offsets on every eligible regime-I day of #24-#27.

  uv run python hypotheses/H116-election-coupling-step/analysis/run_g26.py
Writes data/processed/H116-election-coupling-step/G26/results.json. Lambda frozen by Amendment A1.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h116lib as L  # noqa: E402
import synthetic as SY  # noqa: E402  (placebo-day rule and skeletons, no simulation here)

A1 = json.loads((L.DATA / "synthetic" / "amendment_A1.json").read_text())
LAM = float(A1["lambda"])
LAM_MAG = float(A1["lambda_magnitude"])
NSKEL = int(A1["skeleton_null_reps"])
_K = {}


def _skel_init():
    calls, XR, XP, agents = L.load("G26")
    pre, post, _ = L.windows_at(calls, L.EVENT_DAY, L.T_STAR, L.T_G)
    s = calls["s"].to_numpy()
    a = calls["agent"].to_numpy()
    md = calls["mode"].to_numpy()
    side = np.where(pre, "pre", np.where(post, "post", "out"))
    keys = np.char.add(np.char.add(a.astype(str), "|"), np.char.add(side, np.char.add("|", md.astype(str))))
    h = np.zeros(calls.height)
    for k in np.unique(keys):
        sel = keys == k
        p = ((s[sel] > 0).sum() + 0.5) / (sel.sum() + 1.0)
        h[sel] = 0.5 * np.log(p / (1 - p))
    _K.update(calls=calls, agents=agents, h=h, pre=pre, post=post)


def skel_world(seed):
    """Field-only skeleton null on the real event day (A1): J = 0, real talk rate per agent x call mode x side."""
    if not _K:
        _skel_init()
    A = len(_K["agents"])
    Z = np.zeros((A, A))
    s, XRs, XPs = L.CS.simulate(_K["calls"], _K["agents"], _K["h"], lambda k: Z, np.zeros(A), seed=seed)
    f = L.fit_event(_K["calls"], XRs, XPs, _K["agents"], L.WINNER, _K["pre"], _K["post"], LAM, se=False, s_override=s)
    return f["coef"]["dJout"], f["coef"]["dJin"], f["read_minus_inflight"]


def pct(x, ref):
    ref = np.asarray([r for r in ref if np.isfinite(r)])
    return float((ref < x).mean()) if len(ref) else np.nan


def main():
    SY._init()
    G = SY._G
    res = {"lambda": LAM}
    # ---------------- time placebos (agent 17, same offsets)
    plc = []
    for (p, day, pre, post) in G["placebos"]:
        calls, XR, XP, agents = G[p]
        f = L.fit_event(calls, XR, XP, agents, L.WINNER, pre, post, LAM, se=False)
        if f is None:
            continue
        ep_pre = L.ep_multipartite(calls, pre, f["pres"], L.WINNER)
        ep_post = L.ep_multipartite(calls, post, f["pres"], L.WINNER)
        plc.append({"period": p, "day": day, "dJout": f["coef"]["dJout"], "dJin": f["coef"]["dJin"],
                    "dJoutP": f["coef"]["dJoutP"], "did": f["did"], "rmi": f["read_minus_inflight"],
                    "dEP_all": ep_post["all"] - ep_pre["all"],
                    "dEP_w": ep_post.get("winner", np.nan) - ep_pre.get("winner", np.nan)})
    res["time_placebos"] = plc
    P = {k: np.array([r[k] for r in plc], dtype=float) for k in ("dJout", "dJin", "dJoutP", "did", "rmi", "dEP_all", "dEP_w")}
    kick = [r for r in plc if r["day"] in ("2025-12-22", "2025-12-29", "2026-01-12")]
    res["n_time_placebos"] = len(plc)
    res["kickoff_placebos"] = kick
    # ---------------- event
    calls, XR, XP, agents = G["G26"]
    pre, post, tw = L.windows_at(calls, L.EVENT_DAY, L.T_STAR, L.T_G)
    f = L.fit_event(calls, XR, XP, agents, L.WINNER, pre, post, LAM, se=True)
    ep_pre = L.ep_multipartite(calls, pre, f["pres"], L.WINNER)
    ep_post = L.ep_multipartite(calls, post, f["pres"], L.WINNER)
    ev = {"windows": [str(t) for t in tw], "coef": f["coef"], "se": f["se"], "n": f["n"], "pres": f["pres"],
          "n_exposed_pre": f["n_exposed_pre"], "n_exposed_post": f["n_exposed_post"], "did": f["did"],
          "se_did": f.get("se_did"), "rmi": f["read_minus_inflight"], "se_rmi": f.get("se_read_minus_inflight"),
          "ep_pre": ep_pre, "ep_post": ep_post,
          "dEP_all": ep_post["all"] - ep_pre["all"], "dEP_w": ep_post["winner"] - ep_pre["winner"]}
    ev["pct_dJout_time"] = pct(ev["coef"]["dJout"], P["dJout"])
    ev["q95_dJout_time"] = float(np.nanpercentile(P["dJout"], 95))
    ev["q05_q95_dJin_time"] = [float(np.nanpercentile(P["dJin"], 5)), float(np.nanpercentile(P["dJin"], 95))]
    ev["pct_dJin_time"] = pct(ev["coef"]["dJin"], P["dJin"])
    ev["pct_dEP_w_time"] = pct(ev["dEP_w"], P["dEP_w"])
    ev["q95_dEP_w_time"] = float(np.nanpercentile(P["dEP_w"], 95))
    ev["pct_rmi_time"] = pct(ev["rmi"], P["rmi"])
    ev["pct_did_time"] = pct(ev["did"], P["did"])
    # ---------------- skeleton null (A1) and unpenalized magnitude
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=2, initializer=_skel_init) as ex:
        sk = np.array(list(ex.map(skel_world, range(11000, 11000 + NSKEL), chunksize=8)))
    ev["skeleton_q95_dJout"] = float(np.percentile(sk[:, 0], 95))
    ev["skeleton_mean_dJout"] = float(sk[:, 0].mean())
    ev["pct_dJout_skeleton"] = pct(ev["coef"]["dJout"], sk[:, 0])
    ev["skeleton_q05_q95_dJin"] = [float(np.percentile(sk[:, 1], 5)), float(np.percentile(sk[:, 1], 95))]
    ev["pct_rmi_skeleton"] = pct(ev["rmi"], sk[:, 2])
    ev["detect_A1"] = bool(ev["coef"]["dJout"] >= 0.05 and ev["coef"]["dJout"] > ev["q95_dJout_time"]
                           and ev["coef"]["dJout"] > ev["skeleton_q95_dJout"])
    fm = L.fit_event(calls, XR, XP, agents, L.WINNER, pre, post, LAM_MAG, se=True)
    ev["magnitude"] = {k: {"est": fm["coef"][k], "se": fm["se"][k]} for k in ("Jout", "dJout", "Jin", "dJin", "dJoutP", "dJoth")}
    ev["magnitude"]["read_minus_inflight"] = {"est": fm["read_minus_inflight"], "se": fm.get("se_read_minus_inflight")}
    ev["magnitude"]["did"] = {"est": fm["did"], "se": fm.get("se_did")}
    # ---------------- agent placebos (same T*, other agents as w)
    ag_pl = {}
    for k in f["pres"]:
        if k == L.WINNER:
            continue
        g = L.fit_event(calls, XR, XP, agents, k, pre, post, LAM, se=False)
        if g is not None:
            ag_pl[str(k)] = g["coef"]["dJout"]
    ev["agent_placebos"] = ag_pl
    ev["pct_dJout_agents"] = pct(ev["coef"]["dJout"], list(ag_pl.values()))
    ev["q90_dJout_agents"] = float(np.percentile(list(ag_pl.values()), 90))
    res["event"] = ev
    # ---------------- re-election (N2)
    r2 = L.windows_at(calls, L.RE_DAY, L.T2, L.T2_G, t0=L.win_start(L.RE_DAY), trim=False)   # Amendment A0
    if r2 is not None:
        pre2, post2, tw2 = r2
        f2 = L.fit_event(calls, XR, XP, agents, L.WINNER, pre2, post2, LAM, se=True)
        res["reelection"] = {"windows": [str(t) for t in tw2], "dJout": f2["coef"]["dJout"], "se": f2["se"]["dJout"],
                             "dJin": f2["coef"]["dJin"], "pct_time": pct(f2["coef"]["dJout"], P["dJout"]),
                             "q05_q95_time": [float(np.nanpercentile(P["dJout"], 5)),
                                              float(np.nanpercentile(P["dJout"], 95))]}
    else:
        res["reelection"] = None
    # ---------------- variant: post window = rest of the event day; additive post = term days (descriptive)
    out = L.DATA / "G26"
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: v for k, v in ev.items() if k not in ("ep_pre", "ep_post")}, indent=1, default=float))
    print("reelection", json.dumps(res["reelection"], default=float))
    print("n placebos", len(plc), "dJout placebo sd", float(np.nanstd(P["dJout"])))


if __name__ == "__main__":
    main()
