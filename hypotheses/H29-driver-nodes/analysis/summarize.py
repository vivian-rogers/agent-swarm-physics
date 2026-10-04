"""H29: cross-unit scoring of the pre-registered predictions (P1-P10), post hoc (Amendment 2) tables, scaling fits,
pooled human-message test, and the per-period results consumed by period_cards.py.

  uv run python hypotheses/H29-driver-nodes/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402
from explore import COUNTED, DESCRIPTIVE  # noqa: E402

ALL = COUNTED + DESCRIPTIVE


def load(u, kind):
    return json.loads((L.OUT / u / ("results.json" if kind == "pre" else "results_posthoc.json")).read_text())


def ci_str(ci, nd=3):
    return "—" if not ci else f"[{ci[0]:.{nd}f}, {ci[1]:.{nd}f}]"


def f(x, nd=2):
    return "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}f}"


def pooled_rho(rhos, ns):
    z, w = [], []
    for r, n in zip(rhos, ns):
        if r is None or not np.isfinite(r) or n <= 3:
            continue
        z.append(np.arctanh(np.clip(r, -0.999, 0.999)))
        w.append(n - 3)
    if not z:
        return None, None
    z, w = np.array(z), np.array(w)
    m = (w * z).sum() / w.sum()
    se = 1 / np.sqrt(w.sum())
    return float(np.tanh(m)), [float(np.tanh(m - 1.96 * se)), float(np.tanh(m + 1.96 * se))]


def scaling(Ns, Es, B=2000, seed=L.SEED):
    x, y = np.log(np.array(Ns, float)), np.log(np.array(Es, float))
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    eta = float(np.polyfit(x, y, 1)[0])
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        i = rng.integers(len(x), size=len(x))
        if np.std(x[i]) > 0:
            bs.append(np.polyfit(x[i], y[i], 1)[0])
    return dict(eta=eta, ci90=[float(np.percentile(bs, 5)), float(np.percentile(bs, 95))], n=int(len(x)))


def main():
    pre = {u: load(u, "pre") for u in ALL}
    post = {u: load(u, "post") for u in ALL}
    S = {}
    # P1
    p1 = {u: (pre[u]["kappa"]["kappa"], pre[u]["kappa"].get("kappa_ci")) for u in ALL}
    pos = [u for u in COUNTED if p1[u][1] and p1[u][1][0] > 0]
    neg = [u for u in COUNTED if p1[u][1] and p1[u][1][1] < 0]
    S["P1"] = dict(pos=pos, neg=neg, verdict="failed (opposite direction)" if len(pos) <= 3 else "supported")
    # post hoc boundary test
    rdpos = [u for u in COUNTED if post[u]["rd"]["ci"] and post[u]["rd"]["ci"][0] > 0]
    S["A2_boundary"] = dict(pos=rdpos, pos_all=[u for u in ALL if post[u]["rd"]["ci"] and post[u]["rd"]["ci"][0] > 0])
    named_pos = [u for u in ALL if post[u]["rd_named_ll"]["ci"] and post[u]["rd_named_ll"]["ci"][0] > 0]
    unnamed_pos = [u for u in ALL if post[u]["rd_unnamed_ll"]["ci"] and post[u]["rd_unnamed_ll"]["ci"][0] > 0]
    fin = lambda v: [x for x in v if x is not None and np.isfinite(x)]
    S["A2_named"] = dict(named_pos=named_pos, unnamed_pos=unnamed_pos,
                         named={u: (post[u]["rd_named_ll"]["jump"], post[u]["rd_named_ll"]["ci"]) for u in ALL},
                         unnamed={u: (post[u]["rd_unnamed_ll"]["jump"], post[u]["rd_unnamed_ll"]["ci"]) for u in ALL},
                         named_med=float(np.median(fin([post[u]["rd_named_ll"]["jump"] for u in ALL]))),
                         unnamed_med=float(np.median(fin([post[u]["rd_unnamed_ll"]["jump"] for u in ALL]))),
                         named_any_control_pos=[u for u in ALL if post[u]["rd_named"]["ci"] and post[u]["rd_named"]["ci"][0] > 0])
    # P2
    ratios = {u: pre[u]["kappa"]["contamination"] / pre[u]["kappa"]["kappa_x"] if pre[u]["kappa"]["kappa_x"] else None
              for u in COUNTED}
    med_ratio = float(np.median([r for r in ratios.values() if r is not None]))
    S["P2"] = dict(ratios=ratios, median=med_ratio, verdict="supported (exceeded)" if med_ratio >= 0.5 else
                   ("failed" if med_ratio < 0.25 else "mixed"))
    # P3
    dec = [u for u in COUNTED if np.isfinite(pre[u]["dilution"]["kappa_bins"][0] or np.nan)
           and pre[u]["dilution"]["kappa_bins"][0] > pre[u]["dilution"]["kappa_bins"][-1]]
    S["P3"] = dict(declining=dec, betas={u: pre[u]["dilution"]["beta"] for u in COUNTED},
                   verdict="inconclusive: kappa changes sign so the power-law slope is undefined; kappa(k=1) > kappa(k>=16) "
                           f"in {len(dec)}/9, confounded with message age")
    # P4
    p4a = [u for u in COUNTED if pre[u]["lsb_self"]["N_D"] <= len([k for k, v in pre[u]["room_sizes"].items() if v >= 1]) + 2]
    p4b = [u for u in COUNTED if pre[u]["lsb"]["N_D"] / pre[u]["n_agents"] >= 0.3]
    jac = {u: pre[u].get("lsb_jaccard") for u in COUNTED}
    p4c = [u for u in COUNTED if jac[u] is not None and jac[u] >= 0.5]
    S["P4"] = dict(a_pass=p4a, b_pass=p4b, jaccard=jac, jaccard_ge05=p4c,
                   nd_frac={u: pre[u]["lsb"]["N_D"] / pre[u]["n_agents"] for u in COUNTED},
                   verdict="mixed: (a) failed (sparse significant-edge graph, many isolated roots); (b) passed 9/9; "
                           f"(c) Jaccard >= 0.5 in {len(p4c)}/9, but only because N_D ~ N (nearly every agent is a driver "
                           "in both halves); structural controllability uninformative, as predicted")
    # P5
    sh = {u: (pre[u].get("split_half") or {}).get("D") for u in COUNTED}
    shp = {u: (post[u].get("split_half") or {}).get("D") for u in COUNTED}
    shv = {u: (pre[u].get("split_half") or {}).get("vol") for u in COUNTED}
    med = float(np.median([x for x in sh.values() if x is not None]))
    big = [sh[u] for u in ("G38", "G51b", "G51c")]
    S["P5"] = dict(split=sh, median=med, split_posthoc=shp, median_posthoc=float(np.median([x for x in shp.values() if x is not None])),
                   split_vol=shv, median_vol=float(np.median([x for x in shv.values() if x is not None])),
                   verdict="failed" if (med <= 0 or all(b < 0.4 for b in big)) else "supported")
    # P6
    ns = [pre[u]["n_agents"] for u in COUNTED]
    v2 = {k: {u: (pre[u].get("V") or {}).get(k) for u in COUNTED} for k in ("V2_D", "V2_vol", "V2_out", "V2_net", "V2_expo", "V1")}
    v2p = {k: {u: (post[u].get("V") or {}).get(k) for u in COUNTED} for k in ("V2_D", "V2_vol", "V2_out", "V2_net", "V2_expo", "V1")}
    pooled = {k: pooled_rho([v[u] for u in COUNTED], ns) for k, v in v2.items()}
    pooledp = {k: pooled_rho([v[u] for u in COUNTED], ns) for k, v in v2p.items()}
    npos = sum(1 for u in COUNTED if (v2["V2_D"][u] or 0) > 0)
    hsplit = {u: pre[u].get("H_split_half") for u in COUNTED}
    S["P6"] = dict(V=v2, V_posthoc=v2p, pooled=pooled, pooled_posthoc=pooledp, n_pos=npos, H_split=hsplit,
                   H_split_median=float(np.median([x for x in hsplit.values() if x is not None])),
                   verdict=("failed (pooled rho < 0.3; the validator itself does not replicate across halves, median "
                            f"{np.median([x for x in hsplit.values() if x is not None]):.2f})"))
    # P7
    p7a = {u: pre[u]["rho_D_net"] for u in COUNTED}
    two = [u for u in COUNTED if "top_in_larger_room" in pre[u]]
    p7b = {u: pre[u]["top_in_larger_room"] for u in two}
    p7bp = {u: post[u].get("top_in_larger_room") for u in COUNTED + ["G37"] if "top_in_larger_room" in post[u]}
    p7c = {}
    for u in two + (["G37"] if "per_room" in pre["G37"] else []):
        pr = pre[u]["per_room"]
        rooms = sorted(pr, key=lambda r: pr[r]["n_agents"])
        p7c[u] = bool(pr[rooms[0]]["kappa"] > pr[rooms[-1]]["kappa"])
    p7cp = {}
    for u in [u for u in ALL if "per_room" in post[u]]:
        pr = post[u]["per_room"]
        rooms = sorted(pr, key=lambda r: pr[r]["n_agents"])
        p7cp[u] = bool(pr[rooms[0]]["rd_jump"] > pr[rooms[-1]]["rd_jump"])
    base = {u: max(post[u]["room_sizes"].values()) / sum(post[u]["room_sizes"].values()) for u in two}
    S["P7"] = dict(a=p7a, b=p7b, b_posthoc=p7bp, c=p7c, c_posthoc=p7cp, larger_room_base_rate=base,
                   verdict=(f"(a) passed (rho 0.93-1.00; by construction, Amendment 1.4); (b) {sum(p7b.values())}/"
                            f"{len(p7b)} (base rate {np.mean(list(base.values())):.2f}; weak); (c) {sum(p7c.values())}/"
                            f"{len(p7c)} pre-registered, {sum(p7cp.values())}/{len(p7cp)} post hoc (room composition confound)"))
    # P8 scaling
    Ns = [pre[u]["n_agents"] for u in ALL]
    S["P8"] = dict(pre_Estar=scaling(Ns, [pre[u]["E_star"] for u in ALL]),
                   pre_Emed=scaling(Ns, [pre[u]["E_med"] for u in ALL]),
                   post_Estar=scaling(Ns, [post[u]["E_star"] for u in ALL]),
                   post_Emed=scaling(Ns, [post[u]["E_med"] for u in ALL]),
                   post_Estar_51=scaling([post[u]["n_agents"] for u in ALL if u.startswith("G51")],
                                         [post[u]["E_star"] for u in ALL if u.startswith("G51")]),
                   post_Estar_2room=scaling([post[u]["n_agents"] for u in ALL if not u.startswith("G51")],
                                            [post[u]["E_star"] for u in ALL if not u.startswith("G51")]),
                   N={u: pre[u]["n_agents"] for u in ALL}, Estar_pre={u: pre[u]["E_star"] for u in ALL},
                   Estar_post={u: post[u]["E_star"] for u in ALL}, Emed_post={u: post[u]["E_med"] for u in ALL})
    # P9
    hn = {u: (pre[u]["human_named"]["kappa_x"], pre[u]["human_named"]["n_V"], pre[u]["human_bystander"]["kappa_x"],
              pre[u]["human_bystander"]["n_V"]) for u in ALL}
    usable = [u for u in ALL if hn[u][1] >= 5 and np.isfinite(hn[u][0] or np.nan) and np.isfinite(hn[u][2] or np.nan)]
    ge2 = [u for u in usable if hn[u][0] >= 2 * max(hn[u][2], 1e-9)]
    hum = [h for u in ALL for h in pre[u].get("humans", []) if h.get("spread_norm") is not None]
    pct = np.array([h["pct"] for h in hum])
    sp = np.array([h["spread_norm"] for h in hum])
    top, bot = sp[pct > 2 / 3], sp[pct < 1 / 3]
    rng = np.random.default_rng(L.SEED)
    rb = []
    for _ in range(2000):
        a, b = rng.choice(top, len(top)), rng.choice(bot, len(bot))
        rb.append(a.mean() - b.mean())
    S["P9"] = dict(named_vs_bystander=hn, usable=usable, named_ge2x=ge2, n_human_msgs=len(hum),
                   rho_spread_pct=L.spearman(pct, sp), top_mean=float(top.mean()) if len(top) else None,
                   bottom_mean=float(bot.mean()) if len(bot) else None, n_top=int(len(top)), n_bottom=int(len(bot)),
                   diff_ci=[float(np.percentile(rb, 2.5)), float(np.percentile(rb, 97.5))] if len(top) and len(bot) else None)
    # P10
    nu = {u: (pre[u]["named_agent"]["kappa_x"], pre[u]["unnamed_agent"]["kappa_x"], pre[u]["unnamed_agent"]["kappa"])
          for u in COUNTED}
    ge = [u for u in COUNTED if nu[u][0] >= 2 * max(nu[u][1], 1e-9)]
    unn_le0 = [u for u in COUNTED if nu[u][2] <= 0]
    S["P10"] = dict(named_unnamed=nu, named_ge2x=ge, unnamed_kappa_le0=unn_le0,
                    unnamed_rd_pos=[u for u in COUNTED if post[u]["rd_unnamed"]["ci"] and post[u]["rd_unnamed"]["ci"][0] > 0])
    # synthetic + recovery summaries
    S["synthetic"] = json.loads((L.OUT / "synthetic/synthetic_summary.json").read_text())
    S["posthoc_recovery"] = json.loads((L.OUT / "synthetic/posthoc_recovery_summary.json").read_text())
    L.jdump(S, L.OUT / "summary.json")
    period_results(pre, post, S)
    print(json.dumps({k: v.get("verdict") for k, v in S.items() if isinstance(v, dict) and "verdict" in v}, indent=1))
    print("boundary pos (counted):", rdpos, "| named pos:", named_pos, "| unnamed pos:", unnamed_pos)
    print("P6 pooled pre:", {k: v for k, v in pooled.items()}, "\nP6 pooled post:", pooledp)
    print("P8:", {k: S["P8"][k] for k in ("pre_Estar", "pre_Emed", "post_Estar", "post_Emed", "post_Estar_51", "post_Estar_2room")})
    print("P9:", {k: S["P9"][k] for k in ("usable", "named_ge2x", "n_human_msgs", "rho_spread_pct", "top_mean", "bottom_mean",
                                           "n_top", "n_bottom", "diff_ci")})
    print("P10:", ge, unn_le0, S["P10"]["unnamed_rd_pos"])


def period_results(pre, post, S):
    out = {}
    for u in ALL:
        a, b = pre[u], post[u]
        k = a["kappa"]
        rd, rn, ru = b["rd"], b["rd_named_ll"], b["rd_unnamed_ll"]
        sh, shp = a.get("split_half") or {}, b.get("split_half") or {}
        V, Vp = a.get("V") or {}, b.get("V") or {}
        desc = u in DESCRIPTIVE
        infl = bool(rd["ci"] and rd["ci"][0] > 0)
        if desc:
            verdict = "descriptive"
        elif infl:
            verdict = "mixed"
        else:
            verdict = "failed"
        rows = [
            "| Prediction | Observed | Null / reference | Verdict |", "| --- | --- | --- | --- |",
            f"| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = {k['kappa']:.4f} {ci_str(k.get('kappa_ci'), 4)}; "
            f"field-corrected visible pull {k['kappa_x']:.4f}, invisible-placebo pull {k['contamination']:.4f} | 0 | "
            f"{'pass' if k.get('kappa_ci') and k['kappa_ci'][0] > 0 else ('fail (negative)' if k.get('kappa_ci') and k['kappa_ci'][1] < 0 else 'fail (n.s.)')} |",
            f"| *post hoc* visibility jump at matched time-to-reply | {rd['jump']:.4f} {ci_str(rd.get('ci'), 4)}; like-for-like: named "
            f"{f(rn['jump'], 3)} {ci_str(rn.get('ci'))}, unnamed {f(ru['jump'], 3)} {ci_str(ru.get('ci'))} | 0 | "
            f"{'influence detected' if infl else 'not detected'} |",
            f"| P5 split-half Spearman of D_k | pre-registered {f(sh.get('D'))}; post hoc {f(shp.get('D'))}; message volume "
            f"{f(sh.get('vol'))} | synthetic true model 0.3–0.85 | {'pass' if (sh.get('D') or -1) >= 0.4 else 'fail'} |",
            f"| P6 held-out V2: ρ(D_k, H_k) | pre {f(V.get('V2_D'))}, post hoc {f(Vp.get('V2_D'))}; volume {f(V.get('V2_vol'))}, "
            f"out-strength {f(V.get('V2_out'))} | validator split-half {f(a.get('H_split_half'))} | "
            f"{'> 0' if (V.get('V2_D') or 0) > 0 else '≤ 0'} (uninformative where the validator does not replicate) |",
            f"| P4 structural drivers | LSB N_D {a['lsb']['N_D']}/{a['n_agents']} (significant edges {a['n_sig_edges']}/"
            f"{a['n_pairs_est']}); post hoc dense network N_D (self-loops) {b['lsb_dense_self']['N_D']}; split-half Jaccard "
            f"{f(a.get('lsb_jaccard'))} | rooms {len(a['room_sizes'])} | uninformative |",
            f"| P10 named vs unnamed | field-corrected pull named {a['named_agent']['kappa_x']:.3f} vs unnamed "
            f"{a['unnamed_agent']['kappa_x']:.3f} | ratio ≥ 2 | {'pass' if a['named_agent']['kappa_x'] >= 2 * max(a['unnamed_agent']['kappa_x'], 1e-9) else 'fail'} |",
            f"| Driver ranking (post hoc network) | top 3: {', '.join(b['top3'])}; highest volume: {b['top_vol']} | ρ(D, volume) "
            f"{f(b['rho_D_vol'])} | — |",
            f"| Scaling inputs | N = {a['n_agents']}, E* = {b['E_star']:.3g} (post hoc), median E = {b['E_med']:.3g} | — | — |",
        ]
        if "top_in_larger_room" in a:
            pr = a["per_room"]
            prp = b.get("per_room", {})
            rr = "; ".join(f"room {r} (n={v['n_agents']}): κ {v['kappa']:.3f}, post hoc jump {prp.get(r, {}).get('rd_jump', float('nan')):.3f}"
                           for r, v in pr.items())
            rows.append(f"| P7b/c rooms | top driver in larger room: {a['top_in_larger_room']} (post hoc "
                        f"{b.get('top_in_larger_room')}); {rr} | — | — |")
        hn = S["P9"]["named_vs_bystander"][u]
        rows.append(f"| P9a humans named vs bystanders | {f(hn[0], 3)} (n = {hn[1]} rows) vs {f(hn[2], 3)} (n = {hn[3]}) | — | "
                    f"{'descriptive (n < 5)' if hn[1] < 5 else ('pass' if hn[0] >= 2 * max(hn[2], 1e-9) else 'fail')} |")
        table = "\n".join(rows)
        fig = ("Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/" + u +
               "/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).")
        sc = (f"- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test "
              f"{'passes' if infl else 'does not pass'}; ranking split-half {f(sh.get('D'))} / {f(shp.get('D'))}.\n"
              f"- **D** (unfitted): held-out spread V2 {f(V.get('V2_D'))} (validator replicates at {f(a.get('H_split_half'))}).\n"
              f"- **G** (ground truth): naming effect {'present' if rn['ci'] and rn['ci'][0] > 0 else 'not significant'} "
              f"(the H04 named-agent structure).")
        notes = ("- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. "
                 f"Invisible rows from call windows > 30 s: {f(rd.get('frac_inv_long_window'))} (the H18 visibility rule "
                 "misclassifies messages that arrive during a PAUSE or a long tool call).")
        out[u] = dict(verdict=verdict, table=table, figure=fig, scorecard=sc, notes=notes,
                      key=(f"κ {k['kappa']:.3f} {ci_str(k.get('kappa_ci'))}; post hoc jump {rd['jump']:.3f} "
                           f"{ci_str(rd.get('ci'))} (named {f(rn['jump'])}, unnamed {f(ru['jump'], 3)}); split-half D {f(sh.get('D'))}/{f(shp.get('D'))}; "
                           f"V2 {f(V.get('V2_D'))}"))
    L.jdump(out, L.OUT / "period_results.json")


if __name__ == "__main__":
    main()
