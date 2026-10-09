"""DRAFT theses table -> writeup/papers/thermodynamics/sections/theses_table.tex

The 20 claims with the highest estimated usefulness among those with credence >= 0.6, from
hypotheses/H*/summary/meta.json v2 (sorted by EU, then p, then card number; same order as eu_table.tex).
The thesis text is a hand-compressed form (<= 30 words) of v2.claim, written 2026-10-07 and kept in THESES
below. Each entry stores the start of the claim it was written from; when meta.json's claim no longer starts
that way, or a card enters the top 20 without an entry, the row falls back to the raw claim cut to 30 words
and a "% CHECK" comment marks it. Edit the .tex by hand after generating; re-running overwrites it.

Usage: uv run python writeup/figures/make_theses_table.py
"""
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_eu_table as eu  # noqa: E402

OUT = eu.ROOT / "writeup/papers/thermodynamics/sections/theses_table.tex"
N, PMIN, MAXW = 20, 0.6, 30

# id: (start of the v2.claim it compresses, thesis in LaTeX)
THESES = {
    "H44": ("In regime III (9 non-reserved periods), a forced context wipe",
            r"Regime III (9 periods): a forced context wipe gives a one-call re-reading spike, $\sim$8-call tail ($\Theta_c$ +0.106 [0.089, 0.122]), 20--32\% write dip; a 20-call cap costs 12\% output per call."),
    "H38": ("Regime-III co-activation is 70–80% the runner's",
            r"In regime III, joint silences are operator-scheduled day edges, not platform stalls: day-edge conditioning removes most co-activation excess (G38 0.149 $\to$ 0.026); 70--80\% of co-activation is the runner's start/stop."),
    "H46": ("An agent's style is a stable identity charge",
            r"Regime III: style is an identity charge plus context-held offset that forced erasures redraw (T 0.546 [0.522, 0.564], content flat); it identifies agents across goal switches at 0.85 (chance 0.15)."),
    "H54": ("Where a kickoff names a shared target",
            r"Over 33 kickoffs naming a shared target, day-1 content identifies its own kickoff (top-1 18/33 bge, 20/33 gte); \#51 agents sit on private goals; human messages pull readers by $\Delta\approx 0.09$."),
    "H69": ("Restatement loops copy what the agent's context still holds",
            r"Regime III: restatement loops copy what the context still holds (in-context OR 3.38 [2.56, 4.46], 4/4 periods); an erasure ends them as a step, not a dose."),
    "H16": ("In #51, pause-chain traps are held by the agent's context",
            r"In \#51, a forced erasure inside a pause-chain trap raises escape at next wake from 0.47 to 0.84 (log OR +2.68 [2.31, 3.16]); directed reads work by address, not dilution."),
    "H02": ("Activity-timing pairwise couplings sit at the null floor",
            r"Activity-timing pairwise Ising couplings sit at the null floor; the regime-III collective coupling was the operator's day edges (significant in 2/8 chunks under the corrected null, 7/13 in regime I)."),
    "H08": ("On the context ledger, a recipient's naming and replying",
            r"Naming and replying jump at the call that receives the message (mention 14/17, reply 17/17 periods); content moves toward it only within addressed replies (G51 +1.25 [0.98, 1.60] cos$\times$100)."),
    "H67": ("In regime III the read-out talk loop gain is subcritical",
            r"In regime III the read-out talk loop gain is subcritical, $g_{\rm lag}$ 0.13 (25 units), matching Fano-implied gain 0.149 [0.123, 0.175]; regime I has no read-out gain on the chat clock."),
    "H42": ("In regime III, a read message that names the recipient",
            r"In regime III, a read naming the recipient raises its talk at the read-out call by 0.076 [0.066, 0.086] (26 units); the named kernel survives a fitted Cox field (0.90)."),
    "H74": ("On 282 non-reserved days, a three-channel monitor",
            r"On 282 days, a three-channel monitor with leave-one-period-out thresholds has per-day false-alarm rate 0.085 [0.04, 0.17], hits 0.57 of goal kickoffs and 6/6 room changes."),
    "H52": ("Humans get a status-weighted attention premium",
            r"Matched on salience, human messages get about twice the agent reply rate (+0.030 [0.019, 0.042], 17 periods), a quarter of the naming effect; agent leaders share the premium (not deference)."),
    "H29": ("Content influence is address-gated",
            r"Content influence depends on address (named 0.05--0.08 per message, unnamed $\approx$ 0 in \#51); content-pull driver rankings fail held out; net reply current predicts spread weakly ($\rho\approx$ 0.1--0.2)."),
    "H40": ("In the computer-use scaffold (regimes II–III), a talk call",
            r"In regimes II--III agents couple per call: a talk call's reply hazard barely depends on wall time its last call spanned ($\eta$ $-$0.11 [$-$0.16, $-$0.06]); the wall clock is excluded."),
    "H36": ("A topic-shift alarm fires within the first 30 min",
            r"A topic-shift alarm fires within the first 30 min of talk on 82--85\% of 33 goal kickoffs against 7--9\% of placebo day starts (AUC 0.92--0.94), robust across both embedding models."),
    "H28": ("Links co-move with project switches",
            r"Links co-move with project switches in attention and work (HR $\approx$ 2.6) but mark bursts, not cause them: recipients switch at 6.5$\times$ baseline before they can read the link."),
    "H50": ("In regime III, content couples at the recipient's read-out call",
            r"In regime III, content couples at the recipient's read-out call, as talk does: jump 0.033 [0.027, 0.039] (bge), CI $>$ 0 in 10/16 units, none below; named messages $\times$5."),
    "H43": ("No refractory window beyond one read-out",
            r"One read is one kick: in \#51 a second directed item read in the same call adds 0.11 [0.01, 0.21] of the first; a next-call kick keeps $\sim$0.7."),
    "H11": ("Herding is not stigmergic",
            r"Herding is not stigmergic: in 24 attention units, read chat mentions predict joins (OR 3.0) better than others' commits (1.26; held-out $\Delta$LL $-$0.047 [$-$0.070, $-$0.024])."),
    "H72": ("In #51, trap aging is carried by the context's self-share",
            r"In \#51 trap aging is carried by the context's self-share, not input starvation: own idle share carries 65\% [59, 71] of the aging clocks' held-out information (starvation $-$1\%)."),
}


def words(latex: str) -> int:
    t = re.sub(r"\$[^$]*\$", "x", latex)
    return len(t.split())


def main():
    rows = [r for r in eu.load_rows() if r["p"] >= PMIN][:N]
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = [f"% DRAFT -- generated by writeup/figures/make_theses_table.py on {now} from hypotheses/H*/summary/meta.json (v2).",
         "% DRAFT: thesis texts are hand compressions (<= 30 words) of v2.claim; edit freely. Re-running the script overwrites this file.",
         "% Selection: the 20 highest EU among claims with credence >= 0.6; ties broken by p, then card number.",
         r"\begin{table*}[t]",
         r"\caption{The 20 research theses with the highest estimated usefulness among those with credence $\geq 0.6$ "
         r"(Claude-judged, Sec.~\ref{sec:method}). $p$: credence (faithfulness); $V$: value if true (0--5); EU $=pV$; "
         r"D: mechanism depth, how far the test reaches beyond a fit (0: a pattern that repeats across goal periods; "
         r"1: the model's own signature is predicted and a rival model fails; 2: in addition, a natural experiment agrees "
         r"and synthetic data recover the effect); $^\ast$fragile. No thesis has passed a confirmation test on reserved data.}",
         r"\label{tab:theses}",
         r"\scriptsize\renewcommand{\arraystretch}{1.05}",
         r"\begin{tabular}{@{}l p{0.70\textwidth} c c c c@{}}",
         r"\toprule",
         r"ID & thesis (scored claim, short form) & $p$ & $V$ & EU & D\\ \midrule"]
    for r in rows:
        ent = THESES.get(r["id"])
        claim = r["claim"]
        if ent and claim.startswith(ent[0]):
            text = ent[1]
        else:
            text = eu.tex(eu.house(" ".join(r["claim"].split()[:MAXW])))
            L.append(f"% CHECK {r['id']}: no hand-written thesis for the current claim; raw claim cut to {MAXW} words")
        if words(text) > MAXW:
            L.append(f"% CHECK {r['id']}: {words(text)} words")
        L.append(f"{r['id']} & {text} & {eu.pfmt(r)} & {r['V']:.2f} & {r['EU']:.2f} & {r['M'][1:]}\\\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
    OUT.write_text("\n".join(L) + "\n")
    checks = [l for l in L if l.startswith("% CHECK")]
    print(f"wrote {OUT.relative_to(eu.ROOT)}: {len(rows)} theses; {len(checks)} checks")
    for l in checks:
        print(l)
    for r in rows:
        print(r["id"], r["p"], r["V"], r["EU"], r["M"], words(THESES.get(r["id"], ("", ""))[1]))


if __name__ == "__main__":
    main()
