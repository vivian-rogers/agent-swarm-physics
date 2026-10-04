"""Round-1 reflection: diagnosis + redirected round-2 sub-hypotheses per completed hypothesis.

Single source for (a) the RevTeX document writeup/round1-reflection/round1-reflection.tex and
(b) the "Round 2 redirects" section appended to each completed card.
Usage: uv run python writeup/round1-reflection/redirects.py [--cards]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "infra/summaries"))
from build_summaries import tex_escape  # noqa: E402

E = {  # cross-cutting essence conjectures (also appended as HH131-HH135)
 "E1": ("The harness is the Hamiltonian",
        "The scaffold (turn cadence, timers, consolidation, room visibility, prompts) sets the fields and rates; agents add only weak, context-mediated coupling on top. Corollary: the strongest steering knobs are scaffold parameters, not message wording."),
 "E2": ("Self-reinforcement, not exchange, is the essential physics",
        "Loops, aging traps and herding are Pólya-urn-like: an agent's own output fills its context and raises the odds of repeating; a popular project gathers links and attracts more agents. Urn and preferential-attachment models, not Ising exchange, should be the default."),
 "E3": ("Stigmergy beats chat",
        "Coordination and memory live in shared artifacts (repos, documents, sites); chat is a weak side channel. Influence and persistence should be measured through artifact edits and reads."),
 "E4": ("Swarms relax to their priors",
        "Without a strong field, swarm content relaxes toward the models' joint prior, as in iterated learning; a goal is a quench away from the prior, and the week is relaxation back."),
 "E5": ("Attention is the conserved quantity",
        "Coupling is an allocation of a fixed attention budget per turn (H18: uptake ∝ backlog^-0.6). Who influences whom is an attention market set by salience (mentions, recency, novelty) and backlog."),
}

H = [  # (id, title, what went sideways, essence, [(R-id, claim)])
 ("H01", "Emergent superagents exist",
  "Ideological order was measured as embedding-cluster entropy, which mostly tracked room instructions and topic. Superagency itself was never measured.",
  "Does a group behave more like one agent than its members do?",
  [("R1", "Causal emergence: a room's macro-state (its next behavior distribution, from Jev states) is more predictable from room-level state than from members' states (Hoel-style effective information)."),
   ("R2", "The artifact is the superagent's body: a shared repo's edit stream has a lower entropy rate than any contributor's own stream, so the group acts through the artifact (E3)."),
   ("R3", "Organs: inside a superagent, agents specialize into stable builder, verifier and reporter roles whose actions carry mutual information above chance.")]),
 ("H02", "Inferred couplings reflect real influence",
  "Influence was inferred from when agents are active, but the turn scheduler sets activity timing, so the couplings measured scheduling, not influence.",
  "Who changes whose mind?",
  [("R1", "Influence is the change in j's next decision when i's message is in j's context (context ledger), compared with matched turns where it is not."),
   ("R2", "The #45 leader influenced plans, not activity: assignment-acceptance events (Jev-labeled) show its authority."),
   ("R3", "Influence follows authority markers (operator endorsement, titles, a leader role), not model family.")]),
 ("H03", "Swarm activity is self-exciting",
  "A branching ratio on event timestamps mostly measured scaffold modulation. Criticality of timing is not the question that matters.",
  "How autonomous is the swarm: what fraction of its activity is self-generated rather than driven by the scaffold or humans?",
  [("R1", "Autonomy fraction: classify every turn's trigger (scheduled, external message, peer message, self-continuation) from the context ledger; autonomy = peer + self share, tracked across regimes."),
   ("R2", "The swarm dies without drive: during outages and nudger-off sessions, peer-driven activity decays with a measurable lifetime."),
   ("R3", "Criticality, if anywhere, lives in content cascades (H34), not in timing.")]),
 ("H04", "External forcing reshapes the response kernel",
  "Messages were treated as fields on activity and searched for linear kernels; the kernel turned out to be the turn schedule.",
  "The scaffold is the propagator: the response to any input is when the agent next looks, times whether it attends.",
  [("R1", "The response kernel equals the turn-interval survival function convolved with an uptake probability, with no free parameters (HH92, tested in H08)."),
   ("R2", "The steering knob is the scheduler: shortening turn cadence raises susceptibility more than rewording or repeating a message (E1)."),
   ("R3", "A salience law: uptake rises with mention, position and novelty in context and falls with backlog (E5).")]),
 ("H05", "Rooms are coupled blocks",
  "\"Rooms decouple chat\" is close to the scaffold's definition of a room, and entropy production on 1-min spins measured nothing.",
  "Through which channels does information actually move?",
  [("R1", "Rooms matter only insofar as they also split artifacts: cross-room pairs sharing a repo stay coupled through edits (E3)."),
   ("R2", "The ×6 rise in within-room coupling after the split is attention reallocation, predicted in size by N_room^-0.6 (E5)."),
   ("R3", "Information leaks across rooms through history search and artifacts at a measurable rate (a leak conductance).")]),
 ("H07", "The RPG forks diverge",
  "Forks were treated as passive copying; the interesting signal was nucleation by a single agent.",
  "Does culture in shared artifacts change by gradual drift or by rare rewrites from a few agents?",
  [("R1", "Content change in every shared artifact is heavy-tailed, dominated by a few nucleator agents, and nucleators are consistent across artifacts (a trait; HH96)."),
   ("R2", "Mutation per file-touch is universal across artifacts and agents (HH95)."),
   ("R3", "Forks re-converge when the same models meet the same bugs: the rate of convergent evolution is set by the shared prior (E4).")]),
 ("H09", "Agent swarms have an effective thermodynamics",
  "Thermodynamic words were mapped onto scheduler mechanics (timers, consolidation). Energy was never defined in agent terms.",
  "Tokens are the energy, progress is the work, and context resets are the heat.",
  [("R1", "Token thermodynamics: power = tokens per hour; efficiency = progress (work ledger) per token; loops waste tokens at zero efficiency."),
   ("R2", "Consolidation is Landauer-like erasure: tokens spent consolidating vs information kept."),
   ("R3", "The swarm is a driven-dissipative steady state whose throughput is limited by attention, not compute (E5).")]),
 ("H10", "Goals are Legendre pushes",
  "A small-push, linear-response picture was tested on continuous alignment, but goals are large quenches.",
  "How does a new goal propagate: as a field acting on everyone at once, or as contagion from early adopters?",
  [("R1", "Adoption onsets after a kickoff: a field predicts simultaneous onsets; contagion predicts onsets ordered by exposure to early adopters."),
   ("R2", "Goals act on a two-state on-goal/off-goal occupancy (HH130)."),
   ("R3", "During the week, goal-specific content relaxes back toward family-prior directions (E4).")]),
 ("H11", "Division of labor vs herding",
  "The sign of the Potts coupling was tied to goal mode, but herding appears regardless of mode, which points to a mechanism.",
  "Why do agents pile on: imitation, or attraction to where the work already is?",
  [("R1", "Preferential attachment: P(join X) ∝ (recent activity on X)^α. With α near 1 this is a Yule process, which predicts the project-size distribution (E2)."),
   ("R2", "Herding is stigmergic, not social: artifact activity predicts joining better than chat mentions of X (E3, vs H28)."),
   ("R3", "Herding is a coordination solution that raises output; own-artifact spread duplicates effort (test against the work ledger).")]),
 ("H12", "Groupthink is dimensional collapse",
  "Using the participation ratio as a groupthink proxy was wrong, but the analysis found the real phenomenon: loops.",
  "Loops are fixed points of an agent's self-conditioned generation.",
  [("R1", "Loop onset is predicted by the share of an agent's context filled with its own recent output; crossing a threshold is a bifurcation to a fixed point (E2)."),
   ("R2", "Only novel external input breaks a loop, and the escape probability scales with the input's novelty (embedding distance), not with who sent it."),
   ("R3", "Swarm groupthink never forms because each agent is its own echo chamber: self-echo dominates cross-echo.")]),
 ("H13", "Model families carry their own fields",
  "Family alignment in embeddings turned out to be writing style, which was close to trivial.",
  "Do vendors differ in decisions, not prose?",
  [("R1", "Policy fingerprint: P(next behavior state | current state, context features) differs by family beyond agent identity."),
   ("R2", "Families differ in susceptibility: who listens to whom (HH98)."),
   ("R3", "Mixed-vendor periods out-produce single-vendor ones (descriptive, confounded; work ledger).")]),
 ("H14", "Entropy production of behavior sequences",
  "Entropy production on action classes measured the scaffold's consolidation cycle.",
  "The arrow of time of work: progress is irreversible, chatter is reversible.",
  [("R1", "Entropy production on work states (plan, build, verify, ship; Jev) correlates with output: useful irreversibility."),
   ("R2", "Loops are near-reversible cycles with zero progress; productive phases produce entropy. Efficiency = progress per unit of entropy produced."),
   ("R3", "The scaffold contributes a fixed entropy-production floor (the consolidation clock); subtracting it leaves agent-generated irreversibility (E1).")]),
 ("H15", "Semantic information via natural scrambles",
  "Memory turned out to be irrelevant at day scale; the context carries the load.",
  "Where does the swarm keep its knowledge? In artifacts and history, not in agents.",
  [("R1", "Stigmergic memory: after a memory loss, agents re-acquire state from artifacts (file reads, history search) within a few turns; richer artifact trails mean faster recovery (E3)."),
   ("R2", "Semantic information is concentrated in the few items read first after a reset (the goal and the last messages)."),
   ("R3", "Memory notes are performative: their content rarely reappears in later actions.")]),
 ("H16", "Metastable traps and Kramers escape",
  "The Kramers barrier on a smoothed activity coordinate was an artifact; the aging was real.",
  "Traps deepen by self-reinforcement as the context fills with the agent's own output.",
  [("R1", "Pólya urn: P(repeat) ∝ the share of the context that is own repeats. This predicts the aging exponent (about −0.8 in #51) from the measured context composition (E2)."),
   ("R2", "One directed message works because it dilutes the urn; repeated messages add little once the context is diluted."),
   ("R3", "Trap depth is a model trait: some models loop more.")]),
 ("H17", "Behavior is a Markov state model",
  "A Markov state model on action classes recovered tool modes, i.e. the scaffold.",
  "What are the metastable cognitive modes (planning, building, debugging, existential talk), and what switches them?",
  [("R1", "A soft Jev-state MSM recovers slow cognitive modes, and switches are driven by external input."),
   ("R2", "Debugging is the slowest mode and the main sink of time."),
   ("R3", "Mode switches synchronize across agents only through shared artifacts (E3).")]),
 ("H18", "Attention dilution",
  "The result is good, but responses were measured through mentions, which are contaminated.",
  "Attention is the scarce resource, and coupling is its allocation.",
  [("R1", "A salience law, uptake = f(mention, recency, novelty, sender status), is fit and predicts held-out uptake (E5)."),
   ("R2", "Total attention per turn is conserved; re-test with reply-threading labels."),
   ("R3", "An optimal room size maximizes total useful uptake (HH111).")]),
 ("H19", "One curve for all periods",
  "Collapsing heterogeneous estimators failed because they measure different channels.",
  "The swarm has two order parameters, talk and work, that trade off.",
  [("R1", "Talk and work anticorrelate: periods and agents sit in talky or worky phases on a (talk, work) phase diagram."),
   ("R2", "Goal type (shared vs individual) moves the swarm between the two phases."),
   ("R3", "Messages per LLM step is the control parameter; pre-register the post-hoc collapse.")]),
 ("H20", "Content aging",
  "No aging appeared: content dynamics are Markov.",
  "The swarm has no long-term internal memory; all persistence is stored outside the agents.",
  [("R1", "Persistent content order is explained entirely by persistent fields (goal prompt, artifacts); without them content decorrelates within a day (E3, E4)."),
   ("R2", "The ~2–4 day kickoff relaxation is set by artifact build-up, not agent memory.")]),
 ("H21", "Debate as an antiferromagnet",
  "Antiferromagnetic order was sought in embeddings, but debates are topic fields.",
  "LLM agents don't form coalitions; assigned roles leave no lasting imprint.",
  [("R1", "Role imprint lifetime: roles bias stance only while active, then reverse (HH127); measure across all role periods."),
   ("R2", "Agreement is the default stance (sycophancy as ferromagnetic stance coupling); disagreement appears only when assigned.")]),
 ("H22", "Private goals make a spin glass",
  "Topic co-movement cannot see conflict.",
  "Do conflicting incentives produce conflict behavior at all?",
  [("R1", "Cooperation default: agents help rivals at rates comparable to aligned pairs (Jev-labeled help acts)."),
   ("R2", "A quantitative random-field fit (HH129): roles as fields plus weak positive coupling.")]),
 ("H23", "Leader distillation",
  "The premise was wrong: the leader was self-distilled, not distilled from village text.",
  "What does fine-tuning transmit, compared with prompting?",
  [("R1", "Style transmits through weights, decisions through context: the leader's influence came from its role prompt and position, not its fine-tune.")]),
 ("H24", "Forecast-week coupling switch",
  "The alignment-step test missed the real story, which is pairwise copying.",
  "Information aggregation in swarms is copying from the first or most confident agent, not averaging.",
  [("R1", "Anchoring cascade: first-posted numbers dominate the final consensus (a founder effect) in every estimation-like task."),
   ("R2", "Copy fidelity vs transformation of shared numbers (H07 machinery).")]),
]


def tex_doc() -> str:
    out = [r"""\documentclass[aps,pre,reprint,10pt,nofootinbib]{revtex4-2}
\usepackage{amsmath,amssymb}
\usepackage[hidelinks]{hyperref}
\begin{document}
\title{Round 1 in hindsight: where the hypotheses went sideways, and redirects toward the essence}
\author{Vivian Rogers, with Claude Opus 5.5}
\affiliation{Agent-swarm physics project}
\date[]{Written 2026-10-04 after round 1 of H01--H24. Not the paper.}
\begin{abstract}
Most round-1 hypotheses measured the scaffold (turn scheduler, timers, consolidation clock, room visibility) or embedding style and topic, then mapped a physics model onto that literally. The positive results all point elsewhere: coupling is mediated by the context window, agents get stuck in self-reinforcing loops, herding is the default, memory barely matters at day scale, and influence is invisible in activity timing. This note diagnoses each completed hypothesis in one line, states what its research direction is really after, and proposes bolder round-2 sub-hypotheses (\texttt{H<NN>-R<k>}). Five cross-cutting conjectures close it.
\end{abstract}
\maketitle
\section*{Four ways round 1 went sideways}
\textbf{Measuring the scaffold.} One-minute activity, action classes and event timing are set mostly by the turn scheduler, timers and consolidation (H02, H03, H05, H14, H16, H17, H19).
\textbf{Measuring style and topic.} Embedding cosine mixes topic, style, format and self-repetition (H01, H13, H21, H22).
\textbf{Literal physics.} Barriers, aging and spin glasses were imposed on proxies whose mechanism we already know: what is in the context, and when the agent looks.
\textbf{Responses by proxy.} Mentions stood in for replies, and they are contaminated (H18).
\section*{Redirects by hypothesis}
"""]
    for hid, title, side, ess, rs in H:
        out.append(rf"\paragraph{{{hid}: {tex_escape(title)}.}} \emph{{Sideways:}} {tex_escape(side)} \emph{{Essence:}} {tex_escape(ess)}")
        out.append(r"\begin{itemize}\setlength{\itemsep}{0pt}")
        for rid, claim in rs:
            out.append(rf"\item \textbf{{{hid}-{rid}}} {tex_escape(claim)}")
        out.append(r"\end{itemize}")
    out.append(r"\section*{Five conjectures about the essence}")
    for k, (t, d) in E.items():
        out.append(rf"\paragraph{{{k}. {tex_escape(t)}.}} {tex_escape(d)}")
    out.append(r"""\section*{What round 2 needs}
Most redirects depend on four pipeline pieces: a turn-level context ledger (what each agent had seen before each turn), reply-threading and stance labels, Jev behavior states kept as probability vectors, and a work-output ledger from repository histories. A shared ground-truth table of known roles, leaders and teams would let leader, faction and saboteur detectors be validated.
\end{document}""")
    return "\n".join(out)


def card_section(hid, side, ess, rs) -> str:
    lines = [f"\n## Round 2 redirects (2026-10-04)", f"*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*",
             f"- **Where round 1 went sideways:** {side}", f"- **What the direction is really after:** {ess}"]
    lines += [f"- **{hid}-{rid}.** {c}" for rid, c in rs]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cards", action="store_true"); a = ap.parse_args()
    d = ROOT / "writeup/round1-reflection"
    (d / "round1-reflection.tex").write_text(tex_doc())
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "round1-reflection.tex"], cwd=d, capture_output=True, text=True)
    print((r.stdout.splitlines() or [""])[-2] if r.returncode == 0 else [l for l in r.stdout.splitlines() if l.startswith("!")][:3])
    for ext in (".aux", ".log", ".out", "Notes.bib"):
        (d / f"round1-reflection{ext}").unlink(missing_ok=True)
    if a.cards:
        for hid, title, side, ess, rs in H:
            card = next((ROOT / "hypotheses").glob(f"{hid}-*/README.md"))
            t = card.read_text()
            if "## Round 2 redirects" not in t:
                card.write_text(t.rstrip("\n") + "\n" + card_section(hid, side, ess, rs))
        hh = ROOT / "hypotheses/hypohypotheses/HYPOHYPOTHESES.md"; t = hh.read_text()
        if "HH131" not in t:
            add = ["\n## Essence conjectures from the round-1 reflection (2026-10-04)"]
            for i, (k, (title, desc)) in enumerate(E.items()):
                add.append(f"- **HH{131 + i} · {title}.** {desc} *Check:* see the redirected sub-hypotheses that cite {k} in `writeup/round1-reflection/round1-reflection.pdf`.\n  *Models:* cross-cutting · *Periods:* all")
            hh.write_text(t.rstrip("\n") + "\n" + "\n".join(add) + "\n")
        print("cards updated:", len(H))


if __name__ == "__main__":
    main()
