"""Fill the H32 goal-period folders with round-1 results (Verdict, Result, Scorecard), keeping each folder's dated
Prediction section verbatim. Reads data/processed/H32-information-current-leaders/{explore,segments,ne42}.json.

Verdict rules (card, as amended by A1 before the real-data run):
  general: supported = p_T < 0.05 and (split-half rho > 0 where eligible, else standout p < 0.05);
           mixed = p_T < 0.05 without that; failed = p_T >= 0.05.
  ground truth (P5 humans, P6 #26, P7 #44): if the ground-truth test passes, the general verdict stands; if it fails,
           the verdict is 'failed' unless the general verdict is 'supported', in which case 'mixed'.

Usage: uv run python hypotheses/H32-information-current-leaders/analysis/write_results.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
DATA = ROOT / "data/processed/H32-information-current-leaders"
PDIR = HYP / "goalperiod-subhypotheses"


def f3(x, s=100, nd=3):
    return "–" if x is None or not np.isfinite(x) else f"{x * s:+.{nd}f}"


def general_verdict(r):
    if r["p_T"] >= 0.05:
        return "failed", "no transfer"
    sh = r.get("split_half")
    if sh and sh.get("rho_out") is not None:
        ok = sh["rho_out"] > 0
        return ("supported" if ok else "mixed"), f"transfer, split-half ρ {sh['rho_out']:+.2f}"
    ok = r.get("p_standout", 1) < 0.05
    return ("supported" if ok else "mixed"), f"transfer, standout p {r.get('p_standout', float('nan')):.2f}"


def gt_tests(g, r, seg):
    """Returns list of (name, passed, text)."""
    out = []
    h = r.get("human")
    if h is not None and h.get("n_msgs", 0) >= 15 and h.get("rank_out") is not None:
        out.append(("P5 humans as a source", bool(h["above_median_agent"]),
                    f"human pseudo-agent Out {f3(h['out'])}% (rank {h['rank_out']} of {len(r['nodes']) + 1}; null p = {h['p']:.3f}); "
                    f"by message count it would rank {h['rank_count']}"))
    if g == 26 and seg:
        names = dict(zip([str(a) for a in r["nodes"]], r["names"]))
        o = np.array(r["out"], float); k = r["nodes"].index(17)
        rank_w = int(1 + np.sum(o > o[k]))
        out.append(("P6a DeepSeek not top over the week", rank_w > 3, f"DeepSeek-V3.2 Out rank {rank_w} of {len(o)}"))
        post = seg["G26_post"]
        srt = sorted(post.items(), key=lambda kv: -np.nan_to_num(kv[1]["dG"], nan=-9))
        rk = [a for a, _ in srt].index("17") + 1
        out.append(("P6b DeepSeek top after the decision", rk == 1,
                    f"pooled Out* after 01-09 18:59: DeepSeek rank {rk} of {len(srt)} (ΔG {f3(post['17']['dG'])}%, z {post['17']['z']:.1f}); "
                    f"top = {names.get(srt[0][0], srt[0][0])} ({f3(srt[0][1]['dG'])}%, z {srt[0][1]['z']:.1f})"))
    if g == 44 and seg:
        b = seg["G44_best_0528_29"]
        srt = sorted(b.items(), key=lambda kv: -np.nan_to_num(kv[1]["dG"], nan=-9))
        order = [a for a, _ in srt]
        agents_only = [a for a in order if a != "100"]
        rk28 = agents_only.index("28") + 1 if "28" in agents_only else None
        out.append(("P7a temporary leader not top in #best", rk28 is not None and rk28 >= 3,
                    f"agent 28 pooled Out* rank {rk28} of {len(agents_only)} #best agents (ΔG {f3(b['28']['dG'])}%, z {b['28']['z']:.1f})"))
        rkH = order.index("100") + 1
        out.append(("P7b operator top in #best", rkH == 1, f"humans rank {rkH} of {len(order)} (ΔG {f3(b['100']['dG'])}%, z {b['100']['z']:.1f})"))
        same, cross = r.get("pairs_same_room", {}), r.get("pairs_cross_room_unseen", {})
        if same.get("mean") is not None and cross.get("mean") is not None:
            ok = same["mean"] > cross["mean"] and cross["ci90"][0] <= 0 <= cross["ci90"][1]
            out.append(("P7c same-room > cross-room", ok,
                        f"same-room pairs {f3(same['mean'])}% [{f3(same['ci90'][0])}, {f3(same['ci90'][1])}] (n {same['n']}); "
                        f"cross-room (unseen) {f3(cross['mean'])}% [{f3(cross['ci90'][0])}, {f3(cross['ci90'][1])}] (n {cross['n']})"))
    return out


def period_text(g, r, seg):
    v, why = general_verdict(r)
    gts = gt_tests(g, r, seg)
    decisive = [t for t in gts if not t[0].startswith("P6a")]
    if decisive:
        allpass = all(t[1] for t in decisive)
        if not allpass:
            v = "mixed" if v == "supported" else "failed"
    cent = r["cent_nullvar"] if "cent_nullvar" in r else r["cent"]
    lc = r["leader_call"]
    rows = []
    rows.append(("P1 transfer T > 0 (p_T < 0.05)", f"T = {f3(r['T'])}% (null 95th pct {f3(r['T_null_q'][2])}%)", f"p_T = {r['p_T']:.3f}",
                 "pass" if r["p_T"] < 0.05 else "fail"))
    wd = r.get("withinday", {})
    if wd:
        rows.append(("N1w within-day null (A1c)", f"T = {f3(wd['T'])}%", f"p_T = {wd['p_T']:.3f}",
                     "pass" if wd["p_T"] < 0.05 else "fail"))
    sh = r.get("split_half")
    if sh and sh.get("rho_out") is not None:
        rows.append(("P3 split-half ρ(Out) > 0", f"ρ = {sh['rho_out']:+.2f} (n = {sh['n']}); top odd/even = {sh['top_odd']}/{sh['top_even']}",
                     "ρ = 0", "pass" if sh["rho_out"] > 0 else "fail"))
    rows.append(("Leader call (standout, A1)", f"top = {lc['top_out_name']} (z_out {lc['z_top']:.1f}); standout p = {r.get('p_standout', float('nan')):.3f}",
                 "null replicas", "called" if r.get("p_standout", 1) < 0.05 else "none"))
    rows.append(("Net current", f"top net source = {lc['top_net_name']}", "–", "descriptive"))
    if r["p_T"] < 0.05:
        rows.append(("Φ (centralization)", f"Φ = {cent['phi']:.2f}; Gini(Out⁺) = {cent['gini']:.2f}; top share = {cent['top_share']:.2f}",
                     "0 = equal, 1 = star", "descriptive"))
    if "T_unseen" in r:
        rows.append(("P8 exposure contrast", f"seen beyond unseen {f3(r['T_seen_beyond_unseen'])}% (p {r['p_T_seen_beyond_unseen']:.3f}); "
                     f"unseen {f3(r['T_unseen'])}% (p {r['p_T_unseen']:.3f})", "shift null",
                     "pass" if (r["p_T_seen_beyond_unseen"] < 0.05 and r["p_T_unseen"] >= 0.05) else "fail"))
    a2 = DATA / f"G{g:02d}" / "result_A2.json"
    if a2.exists():
        q = json.loads(a2.read_text())
        rows.append(("A2 post hoc (folds with ≥ 20 training messages)", f"T = {f3(q['T'])}%; 10%-trimmed T = {f3(q['T_trim'])}%",
                     f"p_T = {q['p_T']:.3f}; trimmed p = {q['p_T_trim']:.3f}", "post hoc"))
    for name, ok, txt in gts:
        rows.append((name, txt, "–", "pass" if ok else "fail"))
    rho = r.get("rho", {})
    rows.append(("Rivals: Spearman ρ of Out with", "count {}; mention in-degree {}; artifact adoption {}; H02 timing {}".format(
        *[("–" if rho.get(k) is None else f"{rho[k]:+.2f}") for k in ("count", "mention_indeg", "artifact_adopt", "h02_zI")]),
        "–", "descriptive"))
    tab = "| Test | Observed | Null / reference | Outcome |\n| --- | --- | --- | --- |\n" + "\n".join(
        f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    ranking = sorted(zip(r["names"], r["out"], r["in"], r["net"], r["z_out"]), key=lambda x: -np.nan_to_num(x[1], nan=-9))
    rk = "| Agent | Out (%) | In (%) | Net (%) | z_out |\n| --- | --- | --- | --- | --- |\n" + "\n".join(
        f"| {n} | {f3(o)} | {f3(i)} | {f3(ne)} | {z:.1f} |" for n, o, i, ne, z in ranking)
    vtext = f"{v} ({why}" + (("; " + ", ".join(f"{t[0].split(' ')[0]} {'pass' if t[1] else 'fail'}" for t in gts)) if gts else "") + ")"
    sc = []
    wdp = r.get("withinday", {}).get("p_T", 1.0)
    sc.append(f"| C adequacy | {2 if (r['p_T'] < 0.05 and wdp < 0.05) else 1 if r['p_T'] < 0.05 else 0} | p_T = {r['p_T']:.3f} (cross-day N1), "
              f"{wdp:.3f} (within-day N1w); held-out days |")
    if sh and sh.get("rho_out") is not None:
        sc.append(f"| D unfitted | {1 if sh['rho_out'] > 0 else 0} | split-half ρ = {sh['rho_out']:+.2f} |")
    if gts:
        sc.append(f"| G ground truth | {2 if all(t[1] for t in gts) else 1 if any(t[1] for t in gts) else 0} | " +
                  "; ".join(f"{t[0]}: {'pass' if t[1] else 'fail'}" for t in gts) + " |")
    if "T_unseen" in r:
        ok = r["p_T_seen_beyond_unseen"] < 0.05 and r["p_T_unseen"] >= 0.05
        sc.append(f"| H comparative (vs common drive) | {1 if ok else 0} | exposure contrast {'passes' if ok else 'fails'} |")
    scorecard = "| Axis | Score | Evidence |\n| --- | --- | --- |\n" + "\n".join(sc)
    return v, vtext, tab, rk, scorecard


def fill(g, r, seg):
    d = PDIR / f"G{g:02d}" / "README.md"
    txt = d.read_text()
    v, vtext, tab, rk, scorecard = period_text(g, r, seg)
    txt = re.sub(r"^\*\*Verdict:\*\*.*$", f"**Verdict:** {vtext}", txt, count=1, flags=re.M)
    res = (f"*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G{g:02d}/` "
           f"(`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* "
           f"Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.\n\n"
           f"{tab}\n\n**Agent currents** (sorted by Out):\n\n{rk}\n")
    txt = re.sub(r"## Result\n.*?(?=\n## Scorecard)", "## Result\n" + res.replace("\\", "\\\\"), txt, count=1, flags=re.S)
    txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?(?=\n## Notes)", "## Scorecard (period-specific axes)\n" + scorecard + "\n",
                 txt, count=1, flags=re.S)
    if "round 1 run" not in txt:
        txt = txt.rstrip() + f"\n- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).\n"
    d.write_text(txt)
    return v


def main():
    E = json.loads((DATA / "explore.json").read_text())["periods"]
    seg = json.loads((DATA / "segments.json").read_text()) if (DATA / "segments.json").exists() else {}
    verdicts = {}
    for g, r in sorted(E.items(), key=lambda kv: int(kv[0])):
        verdicts[int(g)] = fill(int(g), r, seg)
    (DATA / "period_verdicts.json").write_text(json.dumps(verdicts, indent=1))
    print(verdicts)


if __name__ == "__main__":
    main()
