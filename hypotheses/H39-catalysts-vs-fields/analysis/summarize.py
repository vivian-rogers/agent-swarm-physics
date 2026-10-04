"""H39 cross-period synthesis: class verdicts, class probabilities, prediction scoring, lever taxonomy.

Reads data/processed/H39-catalysts-vs-fields/G<NN>/results.json (+ boot_draws.npz) and steps/steps_results.json.
Writes data/processed/H39-catalysts-vs-fields/summary.json and prints the taxonomy.
Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h39lib as L  # noqa: E402

RNG = np.random.default_rng(L.SEED)
B4 = ["work", "chat", "idle", "consolidate"]
B6 = ["browse", "type", "shell", "chat", "idle", "consolidate"]


def load_periods():
    out = {}
    for d in sorted(L.OUT.glob("G*/results.json")):
        r = json.loads(d.read_text())
        bd = d.parent / "boot_draws.npz"
        if bd.exists():
            z = np.load(bd)
            for key in z.files:
                c, k = key.split("__")
                if c.startswith("erasure_"):
                    tgt = r.get("erasure", {}).get(c[len("erasure_"):])
                else:
                    tgt = r.get("b4", {}).get(c)
                if tgt is not None:
                    tgt.setdefault("_boot", {})[k] = z[key]
        out[r["period"]] = r
    return out


def pooled_boot(units, R=2000):
    """Bootstrap over powered units of the precision-weighted pooled K and phi_exc (and dpi)."""
    pw = [u for u in units if u.get("status") == "ok" and "_boot" in u and "phi_exc" in u["_boot"]]
    if not pw:
        return {}
    Ks, Ps = [], []
    for _ in range(R):
        pick = RNG.integers(0, len(pw), len(pw))
        k_, p_, w_ = [], [], []
        for i in pick:
            u = pw[i]
            j = RNG.integers(0, len(u["_boot"]["K"]))
            k_.append(u["_boot"]["K"][j])
            p_.append(u["_boot"]["phi_exc"][j])
            w_.append(1 / max(u["K_boot_se"], 1e-3) ** 2)
        w_ = np.array(w_)
        Ks.append(np.sum(w_ * np.array(k_)) / w_.sum())
        Ps.append(np.sum(w_ * np.array(p_)) / w_.sum())
    Ks, Ps = np.array(Ks), np.array(Ps)
    w = np.array([1 / max(u["K_boot_se"], 1e-3) ** 2 for u in pw])
    return dict(K=float(np.sum(w * [u["K"] for u in pw]) / w.sum()), K_ci=np.percentile(Ks, [2.5, 97.5]).tolist(),
                phi_exc=float(np.sum(w * [u["phi_exc"] for u in pw]) / w.sum()),
                phi_exc_ci=np.percentile(Ps, [2.5, 97.5]).tolist(), n_units=len(pw))


def unit_table(P, getter):
    rows = []
    for p, r in sorted(P.items()):
        u = getter(r)
        if u is None or "n_ep" not in u:
            continue
        rows.append(dict(period=p, n_ep=u.get("n_ep"), status=u.get("status"), K=u.get("K"), K_ci=u.get("K_ci"),
                         phi_exc=u.get("phi_exc"), p_F=u.get("p_F"), dpi=u.get("dpi"), dpi_ci=u.get("dpi_ci"),
                         esc=u.get("esc"), docc=u.get("docc"), cls=L.unit_class(u), u=u))
    return rows


def content_pool(P, c):
    us = [r["content"][c] for r in P.values() if isinstance(r.get("content"), dict) and isinstance(r["content"].get(c), dict)
          and r["content"][c].get("status") == "ok"]
    if not us:
        return {}
    mf = L.dl_meta([u["field_c_std"] for u in us], [u["field_c_se"] / max(u["sd_par_ctrl"], 1e-9) for u in us])
    mc = L.dl_meta([u["cat_c"] for u in us], [u["cat_c_se"] for u in us])
    return dict(n_units=len(us), n_ep=int(sum(u["n_ep"] for u in us)), field_std=mf, cat=mc,
                stouffer_field=L.stouffer([u["p_field_c"] if u["field_c"] > 0 else 1 - u["p_field_c"] / 2 for u in us]))


def main():
    P = load_periods()
    S = dict(periods=sorted(P), classes={}, erasure={}, content={}, steps={})
    # ---------------- point classes on B4
    for c in ("N_tgt", "H_any", "H_men", "H_und", "A_men"):
        rows = unit_table(P, lambda r: r.get("b4", {}).get(c))
        units = [x["u"] for x in rows]
        v = L.class_verdict(units)
        v["probabilities"] = L.class_probabilities(units, RNG, R=2000)
        v["pooled_boot"] = pooled_boot(units)
        v["units"] = [{k: x[k] for k in x if k != "u"} for x in rows]
        # B6 pooled dpi
        rows6 = [r.get("b6", {}).get(c) for r in P.values()]
        rows6 = [u for u in rows6 if u and u.get("status") == "ok"]
        if rows6:
            v["b6_dpi_meta"] = [L.dl_meta([u["dpi"][s] for u in rows6], [u["dpi_boot_se"][s] for u in rows6]) for s in range(6)]
        # W sensitivity
        sens = {}
        for Ws in (15, 60):
            us = [r["sens"].get(f"{c}_W{Ws}") for r in P.values() if r.get("sens", {}).get(f"{c}_W{Ws}")]
            us = [u for u in us if u.get("status") == "ok"]
            if us:
                sens[f"W{Ws}"] = dict(n=len(us), K_mean=float(np.mean([u["K"] for u in us])),
                                      phi_exc_mean=float(np.mean([u["phi_exc"] for u in us])),
                                      dpi_mean=np.mean([u["dpi"] for u in us], 0).tolist())
        v["sensitivity"] = sens
        S["classes"][c] = v
        print(f"{c}: {v['cls']} powered {v['n_powered']}/{v['n_units']} K {v.get('K_meta', {}).get('est', np.nan):.3f} "
              f"{v.get('K_meta', {}).get('ci')} phi_exc_mean {v.get('phi_exc_mean', np.nan):.3f} stoufferF {v.get('stouffer_pF', np.nan):.3g} "
              f"probs {v['probabilities']}")
        for s in range(4):
            m = v.get("dpi_meta", [{}] * 4)[s]
            e = v.get("esc_meta", [{}] * 4)[s]
            if m.get("k"):
                print(f"    {B4[s]:12s} dpi {m['est']:+.3f} [{m['ci'][0]:+.3f},{m['ci'][1]:+.3f}]  esc {e['est']:+.3f} [{e['ci'][0]:+.3f},{e['ci'][1]:+.3f}]")
    # ---------------- erasure
    for key in ("CF_b4", "CV_b4", "CF_b4_nocons", "CV_b4_nocons", "CF_b6", "CV_b6", "CF_b6_nocons", "CV_b6_nocons"):
        rows = unit_table(P, lambda r: r.get("erasure", {}).get(key))
        units = [x["u"] for x in rows]
        if not units:
            continue
        v = L.class_verdict(units)
        v["probabilities"] = L.class_probabilities(units, RNG, R=2000) if "b4" in key else {}
        v["units"] = [{k: x[k] for k in x if k != "u"} for x in rows]
        pw = [u for u in units if u.get("status") == "ok"]
        if "b6" in key and pw:
            ks = pw[0].get("keep_states", list(range(6)))
            names = [B6[k] for k in ks]
            iw = [i for i, n in enumerate(names) if n in ("type", "shell")]
            v["dpi_type_shell"] = L.dl_meta([sum(u["dpi"][i] for i in iw) for u in pw],
                                            [np.sqrt(sum(u["dpi_boot_se"][i] ** 2 for i in iw)) for u in pw])
            v["state_names"] = names
        S["erasure"][key] = v
        print(f"erasure {key}: {v['cls']} K {v.get('K_meta', {}).get('est', np.nan):.3f} {v.get('K_meta', {}).get('ci')} phi_exc {v.get('phi_exc_mean', np.nan):.3f}")
    # ---------------- content drift
    for c in ("N_tgt", "H_any", "H_men", "A_men"):
        S["content"][c] = content_pool(P, c)
        cp = S["content"][c]
        if cp:
            print(f"content {c}: units {cp['n_units']} field_std {cp['field_std'].get('est', np.nan):.3f} {cp['field_std'].get('ci')} cat {cp['cat'].get('est', np.nan):.3f} {cp['cat'].get('ci')}")
    # ---------------- steps
    sp = L.OUT / "steps" / "steps_results.json"
    if sp.exists():
        st = json.loads(sp.read_text())["steps"]
        S["steps"] = summarize_steps(st)
    L.jdump(S, L.OUT / "summary.json")
    print("written", L.OUT / "summary.json")


def summarize_steps(st):
    out = {"kickoffs": {}, "list": []}
    for r in st:
        row = dict(id=r["id"], cls=r["cls"], kind=r["kind"], label=r["label"], folder=r["folder"], flag=r.get("flag", ""),
                   era=r.get("era"), shape=r.get("shape"), n_agents=r.get("n_agents"), placebo_pool=r.get("placebo_pool"),
                   n_placebo=r.get("n_placebo"), pre=r.get("pre"), post=r.get("post"))
        for fam in ("b4", "b6", "c6"):
            if fam in r and f"judge_{fam}" in r:
                j = r[f"judge_{fam}"]
                row[fam] = dict(K=r[fam]["K"], K_ci=r[fam].get("K_ci"), phi=r[fam]["phi"], dpi=r[fam]["dpi"],
                                dpi_ci=r[fam].get("dpi_ci"), esc=r[fam].get("esc"), **{k: j.get(k) for k in
                                ("phi_pct", "K_pct", "phi_p95", "K_p025", "K_p975", "phi_exc", "field", "catalyst", "cls", "p_F", "p_K")})
        out["list"].append(row)
    ks = [x for x in out["list"] if x["cls"] == "kickoff" and "b4" in x]
    kc = [x for x in ks if "c6" in x]
    if ks:
        out["kickoffs"] = dict(
            n=len(ks), n_content=len(kc),
            b4_field_share=float(np.mean([x["b4"]["field"] for x in ks])),
            b4_K_inside_share=float(np.mean([x["b4"]["K_p025"] <= x["b4"]["K"] <= x["b4"]["K_p975"] for x in ks])),
            b4_cat_share=float(np.mean([x["b4"]["catalyst"] for x in ks])),
            b4_phi_above_p95_share=float(np.mean([x["b4"]["phi_pct"] >= 95 for x in ks])),
            c6_field_share=float(np.mean([x["c6"]["field"] for x in kc])) if kc else None,
            c6_phi_above_p95_share=float(np.mean([x["c6"]["phi_pct"] >= 95 for x in kc])) if kc else None,
            c6_K_above_median_share=float(np.mean([x["c6"]["K_pct"] > 50 for x in kc])) if kc else None,
            c6_cat_share=float(np.mean([x["c6"]["catalyst"] for x in kc])) if kc else None,
            b4_stouffer_F=L.stouffer([x["b4"]["p_F"] for x in ks]),
            c6_stouffer_F=L.stouffer([x["c6"]["p_F"] for x in kc]) if kc else None,
            b4_dpi_mean=np.mean([x["b4"]["dpi"] for x in ks], 0).tolist(),
            b4_K_pct_mean=float(np.mean([x["b4"]["K_pct"] for x in ks])),
            c6_K_pct_mean=float(np.mean([x["c6"]["K_pct"] for x in kc])) if kc else None,
            b4_phi_exc_mean=float(np.mean([x["b4"]["phi_exc"] for x in ks])),
            c6_phi_exc_mean=float(np.mean([x["c6"]["phi_exc"] for x in kc])) if kc else None)
        print("kickoffs:", out["kickoffs"])
    for x in out["list"]:
        if x["cls"] != "kickoff":
            b = x.get("b4", {})
            c = x.get("c6", {})
            print(f"  {x['id']:10s} b4 {b.get('cls')} K {b.get('K', np.nan):+.3f} (pct {b.get('K_pct')}) phi pct {b.get('phi_pct')} | c6 {c.get('cls')} phi pct {c.get('phi_pct')} K pct {c.get('K_pct')}")
    return out


if __name__ == "__main__":
    main()
