"""H147 round 1: apply the pre-registered rules (card + Amendments A1-A3 + Targets) to results/ and write
results/summary.json. Usage: uv run python hypotheses/H147-egregore-value-and-hosts-51/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h147common as C  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

RES = C.OUT / "results"
DIST_MAX = 0.5


def load():
    pats = {}
    for f in sorted(RES.glob("pattern_*.json")):
        r = json.loads(f.read_text())
        pats[r["pattern"]["id"]] = r
    return pats, pl.read_parquet(RES / "patterns.parquet")


def main():
    pats, df = load()
    mem = df.filter(pl.col("source") == "H145")
    out = {}
    # K1
    k1 = json.loads((RES / "k1_selfdip.json").read_text())
    out["K1"] = {k: {"dV": v["dV_rel"], "ci": v["ci"]} for k, v in k1.items()}
    out["K1"]["passes"] = all(v["ci"][1] < 0 for v in k1.values())
    # P1
    dist = mem.filter(pl.col("h_K") < DIST_MAX)
    dv = dist["dV_rate"].to_numpy()
    rng = np.random.default_rng(0)
    bm = [np.median(rng.choice(dv, len(dv))) for _ in range(2000)]
    nf = int(dist["P1_falsifier"].sum())
    out["P1"] = {"n_distributed": dist.height, "n_falsifiers": nf, "falsifiers": dist.filter(pl.col("P1_falsifier"))["id"].to_list(),
                 "median_dV": float(np.median(dv)), "median_ci": [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))],
                 "n_ci_below0_boot": int((dist["dV_hi"] < 0).sum()), "n_ci_above0_boot": int((dist["dV_lo"] > 0).sum()),
                 "n_above0_both": int(((dist["dV_lo"] > 0) & (dist["dV_pq_lo"] > 0)).sum()),
                 "above0_both": dist.filter((pl.col("dV_lo") > 0) & (pl.col("dV_pq_lo") > 0))["id"].to_list(),
                 "n_I_identified": int(dist["I_identified"].sum()),
                 "I_identified": dist.filter(pl.col("I_identified"))["id"].to_list(),
                 "others_ci_excl0": int(((dist["oth_lo"] > 0) | (dist["oth_hi"] < 0)).sum()),
                 "falsified": nf >= dist.height / 2}
    # P2 / O2 (A3: HL2 testable; others descriptive)
    hub = {}
    for pid, r in pats.items():
        if r["pattern"]["source"] != "H145":
            continue
        for eid, h in r["events"]["hub"].items():
            if h.get("reported"):
                hub.setdefault(eid, []).append({"id": pid, "h_K": r["pattern"]["h_K"], "s": h["s"], "L": h["L"],
                                                "L_own": h["L_own"], "L_others": h["L_others"], "beta": h["beta_allwd"],
                                                "band": h["beta_band95_allwd"], "exceeds": h["exceeds_allwd"],
                                                "beta_sameweekday": h["beta"], "n_placebo": h["n_placebo_allwd"]})
    out["P2"] = {"hub_centred_patterns": int((mem["h_K"] >= 0.6).sum()), "events": hub,
                 "HL2_summary": None}
    if "HL2" in hub:
        b = np.array([x["beta"] for x in hub["HL2"]])
        out["P2"]["HL2_summary"] = {"n": len(b), "median_beta": float(np.median(b)), "n_exceeds": int(sum(x["exceeds"] for x in hub["HL2"])),
                                    "n_beta_lt_0.5": int((b < 0.5).sum())}
    # P3 (A3: prevalence descriptive; colonial A before/after computed)
    p3 = {}
    for pid, r in pats.items():
        p = r["pattern"]
        if p["source"] != "H145" or p["top_host"] != 17:
            continue
        p3[pid] = {e: {"net": r["events"]["op"][e]["net_allwd"], "rel": r["events"]["op"][e]["rel_change"],
                       "exceeds": r["events"]["op"][e]["exceeds_allwd"],
                       "dA": r["colonial_split"][e]["dA"], "ci_dA": r["colonial_split"][e]["ci_dA"],
                       "A_before": r["colonial_split"][e]["A_before"], "A_after": r["colonial_split"][e]["A_after"]}
                   for e in ("OP1", "OP2")}
    nets = {e: [v[e]["net"] for v in p3.values()] for e in ("OP1", "OP2")}
    dA_in = {e: sum(1 for v in p3.values() if v[e]["ci_dA"][0] <= 0 <= v[e]["ci_dA"][1]) for e in ("OP1", "OP2")}
    out["P3"] = {"patterns": p3, "n": len(p3),
                 "n_net_le_-0.20": {e: int(sum(x <= -0.2 for x in nets[e])) for e in nets},
                 "median_net": {e: float(np.median(nets[e])) for e in nets},
                 "n_exceeds": {e: int(sum(v[e]["exceeds"] for v in p3.values())) for e in ("OP1", "OP2")},
                 "n_dA_ci_includes0": dA_in}
    # P4
    tgt = mem.filter((pl.col("top_host") == 17) & pl.col("label").is_in(["frameworks", "governance"]))
    ver = mem.filter(pl.col("label").is_in(["verify", "onboarding"]))
    beyond = mem.filter(((pl.col("host_c_lo") > 0.05) | (pl.col("host_c_hi") < -0.05)
                         | (pl.col("host_a_lo") > 0.05) | (pl.col("host_a_hi") < -0.05)))
    out["P4"] = {"targets": dict(zip(tgt["id"], tgt["class"])), "targets_exc": dict(zip(tgt["id"], tgt["class_exc"])),
                 "n_parasitic_targets": int((tgt["class"] == "parasitic").sum()), "n_targets": tgt.height,
                 "verification": dict(zip(ver["id"], ver["class"])), "verification_exc": dict(zip(ver["id"], ver["class_exc"])),
                 "classes": dict(zip(mem["id"], mem["class"])), "classes_exc": dict(zip(mem["id"], mem["class_exc"])),
                 "classes_card": dict(zip(mem["id"], mem["class_card"])),
                 "n_beyond5_ci": beyond.height, "beyond5": beyond["id"].to_list(),
                 "pseudo_median": {pid: r["host"]["A2"]["pseudo_median"] for pid, r in pats.items()}}
    out["K2_fires"] = beyond.height == 0
    # P5
    ok = mem.filter(pl.col("host_c").is_not_nan() & pl.col("A_excess").is_not_null())
    rho, p = spearmanr(ok["host_c"].to_numpy(), ok["A_excess"].to_numpy())
    br = []
    x, y = ok["host_c"].to_numpy(), ok["A_excess"].to_numpy()
    for _ in range(2000):
        i = rng.integers(0, len(x), len(x))
        if len(np.unique(i)) > 3:
            br.append(spearmanr(x[i], y[i])[0])
    out["P5"] = {"n": ok.height, "rho": float(rho), "p": float(p), "ci": [float(np.nanpercentile(br, 2.5)), float(np.nanpercentile(br, 97.5))],
                 "falsified": bool(rho <= 0 and ok.height >= 6)}
    # role-text controls
    rt = df.filter(pl.col("source") != "H145")
    out["role_controls"] = {r["id"]: {"dV": r["dV_rate"], "ci": [r["dV_lo"], r["dV_hi"]], "align": r["host_a"],
                                      "align_ci": [r["host_a_lo"], r["host_a_hi"]], "commits": r["host_c"], "A_z": r["A_z"]}
                            for r in rt.iter_rows(named=True)}
    (RES / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k not in ("role_controls",)}, indent=1, default=float)[:9000])


if __name__ == "__main__":
    main()
