# Q&A transcript: Kolchinsky–Wolpert semantic information, related frameworks, estimation

Pasted into the project by Vivian Rogers on 2026-10-03; source not recorded. Kept verbatim except for the **Q:** markers added before the questions. Claims and citations are **not verified here**. One answer ("Direct answer on the thermodynamics…") responds to a question that isn't included, and it refers to a "growth-rate bound from last time" from an earlier exchange that also isn't included.

Notation warning: the transcript writes 𝒮 for the viability drop under scrambling. Kolchinsky & Wolpert (2018) call that quantity the **value of information** ΔV, and reserve "stored semantic information" S for the mutual information kept by the optimal (viability-preserving) intervention. See `../architecture.md`.

---

**Q:** Explain um, Artem Kolchinsky's uh, semantic entropy thing. Is that basically a scheme to identify a life form or an agent just from like information statistics?

Small terminology flag first: the thing Artemy Kolchinsky is known for (with David Wolpert, in a 2018 Interface Focus paper) is semantic information, not "semantic entropy." "Semantic entropy" usually refers to a separate, unrelated 2024 method for detecting LLM hallucinations by clustering sampled answers by meaning and measuring entropy over the clusters. I'll assume you mean the Kolchinsky–Wolpert framework.

The basic move is this. Shannon's mutual information tells you how correlated a system is with its environment, but it says nothing about whether those correlations matter. Kolchinsky and Wolpert add a second ingredient: a viability function, some measure of how well the system maintains itself in an improbable, low-entropy state over time. Then they ask which parts of the system–environment mutual information are actually doing the work of keeping it viable.

The test is interventional. You take the joint distribution over system and environment and scramble portions of the correlation, then run the dynamics forward under that counterfactual and see whether viability drops. Correlations you can destroy for free were syntactic but meaningless. Correlations whose destruction costs the system its persistence are the semantic ones. The maximal scrambling you can get away with defines the system's "semantic content," and the viability cost of full scrambling gives you a quantity of semantic information. They also derive related measures, like what fraction of a system's total correlation with its environment is semantic, which behaves a bit like a measure of autonomy.

To your actual question: not really, no, at least not as a standalone detector. Three things stop it.

You have to supply the system/environment boundary yourself. Nothing in the statistics tells you where to cut.

You have to supply the viability function. "Maintaining its own existence" sounds objective but requires choosing what counts as the system continuing to exist and over what timescale. Negative entropy of the state distribution is the usual default, but it's a modeling decision.

Most importantly, you need a causal model, not just observed statistics. The whole framework rests on counterfactual interventions, and you can't compute "what would happen if I scrambled this correlation" from a passive data stream. You need to know the dynamics.

And even granting all that, it doesn't cleanly separate life from non-life. A hurricane comes out with nonzero semantic information, because it really does maintain itself through correlations with sea surface temperature. That's a feature as the authors present it: the output is a graded quantity, not a binary agency verdict. Follow-up work has applied it to agent-based models of chemotaxis and resource gathering, where you can look for thresholds in that graded quantity as agents become more capable.

So it's better read as a formalization of what it means for information to be meaningful to a self-maintaining system, than as an agent-detection algorithm you could point at a signal.

**Q:** Is there, what other ideas that are running on like quantitative stuff and information theory exist uh, that sort of get at similar things?

Quite a few, and they cluster into a handful of families.

Closest in spirit — viability/usefulness of information. Susanne Still, David Sivak, Anthony Bell and Gavin Crooks' "Thermodynamics of prediction" (2012) shows that memory a system keeps about its environment which doesn't predict the future carries an unavoidable dissipation cost. That's a physically grounded version of the same intuition: useless correlation is literally wasteful. Still's earlier "optimal causal inference" work pushes the information bottleneck in the same direction. The free energy principle (Friston) belongs here too, with Markov blankets and variational free energy as the self-maintenance quantity, though it's much more contested and the Markov-blanket formalism has taken real technical criticism from Biehl, Pollock and Kanai.

Agent-centric quantities with no external utility function. Empowerment (Klyubin, Polani, Nehaniv) defines an agent's situation by the channel capacity from its actuators to its later sensors — how much it can causally impose on its own future. Tishby and Polani's "relevant information" applies the bottleneck to perception-action loops. These are attractive because they're intrinsic: nobody hands the system a goal.

Individuality and autonomy. Krakauer, Bertschinger, Olbrich, Flack and Ay's "information theory of individuality" (2020) locates an individual as a region that propagates information from its own past to its own future beyond what the environment supplies, and it yields a spectrum — organismal, colonial, environmentally scaffolded — rather than a yes/no. Bertschinger, Olbrich, Ay and Jost's earlier autonomy paper is the direct ancestor.

Causal structure and emergence. Integrated information theory (Tononi, Albantakis, Oizumi) with Φ; Erik Hoel's causal emergence, where effective information is computed under interventions and a coarse-grained macro scale can beat the micro one; Rosas, Mediano and colleagues' synergy-based emergence criteria and their "software in the natural world" work; Barnett and Seth's dynamical independence. All of these share Kolchinsky–Wolpert's reliance on interventions rather than passive statistics.

Detecting agents outright. Kenton, Everitt and coauthors at DeepMind have a causal-discovery approach where a system counts as an agent if its policy adapts when you intervene on the environment's mechanisms — arguably the most direct answer to what you originally asked, though it still needs a causal model. Orseau, McGill and Legg's "Agents and Devices" does a Bayesian version.

Life detection from measurements. Assembly theory (Cronin, Walker) is the one framework here actually built to be run on data — assembly index plus copy number, measured by mass spectrometry, with the claim that high-assembly molecules in abundance require selection. It's genuinely operational and genuinely disputed.

Structure and memory in processes. Crutchfield's computational mechanics gives causal states, ε-machines and statistical complexity — how much memory a process must carry to predict itself. Lizier's local information dynamics (active information storage, transfer entropy, separable information) was used to identify gliders in cellular automata as coherent information-processing structures, which is about as close as anyone has gotten to finding "agents" in raw spatiotemporal data.

One historical note: "semantic information" also names a much older logical tradition, Bar-Hillel and Carnap in 1953 and later Floridi, where meaning is tied to truth and logical content rather than to function. Kolchinsky and Wolpert are deliberately doing the functional thing instead.

If you want one paper to read next after Kolchinsky–Wolpert, the Krakauer individuality paper is the most natural companion, and the Still prediction paper is the one that anchors the intuition in physics.

*(Question not included in the paste.)*

Direct answer on the thermodynamics: partly yes, and the part that's yes is more exact than you'd guess.

The demon structure

The growth-rate bound from last time, $\Delta\Lambda \le I(S;Y)$, is formally identical to Sagawa–Ueda's bound on measurement-based work extraction, $W_{\text{ext}} \le k_BT\, I(S;Y)$. Kelly gambling and Maxwell's demon are the same mathematics — Vinkler, Permuter and Merhav worked out the explicit dictionary in 2016 — with growth rate playing the role of extracted work and the environment playing the heat bath. So the framing does let you say: a self-maintaining system extracts persistence from environmental correlations at a rate bounded by the information it holds about them, and that sentence is a theorem rather than a metaphor.

What's not thermodynamic is the physical content. For a cell, the demon story is literal: the bits cost $k_BT\ln 2$ to erase and the work is joules. For an ideology, the "free energy" is host attention and cognitive effort, there's no conservation law, and the isomorphism is structural rather than physical. Still et al.'s dissipation bound is the only piece that stays literally thermodynamic across all cases, and it only covers one term (useless memory costs heat).

What it actually gets you

Three things, in order of how much I'd bet on them.

A decomposition of persistence. This is the real product. Any system that lasts is paying for it somehow — by being rigid (the crystal), by hedging (the spore bank), or by knowing things (the cell that chemotaxes). The framework separates the informational component of persistence from the rest and puts a number on it. Nothing else does this cleanly. "How much of your continued existence is purchased with knowledge" is a well-posed question about hurricanes, bacteria, doctrines and robots, on a single axis, and the answers are comparable.

Load-bearing meaning without teleology. "This system knows $X$" becomes an interventional claim — scramble $X$ and watch viability — with no appeal to purposes, representations or an interpreter. That's the philosophical payoff, and it's not nothing: it's what makes the word meaning usable in a physics paper.

Real diagnostics, given a model. $\eta \to 0$ flags a system that persists without tracking anything. $\mathcal{S} < 0$ identifies correlations selection should strip, and predicts the direction of drift. Semantic content tells you which environmental variables the system's survival hangs on, i.e. what to intervene on if you want to kill it or keep it. In the population form, the bet-hedging-versus-sensing crossover and the error threshold are quantitative predictions that have actually been tested in microbes.

What it doesn't do, which I think is what you're circling

It doesn't explain selfness. It presupposes it. The viability function is the self: you have to say what counts as this thing continuing before you can ask what it knows. Kolchinsky–Wolpert measure the epistemic relationship between an already-given self and its world; they say nothing about how a self comes to exist or where its boundary is. If "self-propagating selfness" is the question, that's the individuality problem (Krakauer et al., autopoiesis, Kauffman's autocatalytic closure), and semantic information sits downstream of it.

It also isn't an agent detector, and it says nothing about experience or intrinsic meaning. The $\mathcal{S}$ of a thermostat is positive.

Curiosity or tool

Split by domain. In microbial ecology and synthetic biology the population-growth version is already a working tool: people design switching strategies with it and measure the value of environmental cues in fitness units. In artificial life and agent design it's a usable criterion for what a minimal agent needs to sense versus what it can discard. In Kolchinsky–Wolpert's own general form it has so far been mostly conceptual, with a handful of toy-model follow-ups.

For ideologies specifically, right now it's a lens that generates sharp, falsifiable hypotheses and tells you exactly what data would settle them. It becomes a diagnostic the day someone fits a fitness function to prevalence data, which is difficult but not exotic. So: not just a curiosity, but a tool whose edge is only as sharp as the dynamics you can bring to it. The framing's lasting contribution is that it turns "does this thing know anything" from a rhetorical question into a measurement you're not yet able to make.

**Q:** Oh God, I can't test causality in this one system, but say that I have a really good probe of causality or like I model of cause like causal relationships. And I have the full simulation um, oh God, what else could be done? to like um, sort of effectively uh, make a dynamical heuristic for cause, causal, causal modeling for the semantic information est estimation.

With a full simulation you already own $K_\tau$, so the counterfactuals aren't the bottleneck. Two things are: the combinatorics of semantic content (which subsets to scramble), and the fact that scrambling puts probability mass where your observational data has none. Most of the useful heuristics attack one of those two.

The main trick: compute the landscape once, then everything is linear algebra

For survival-type viability, let $a(x_\tau)$ be the alive-indicator. Run the kernel backward once (Kolmogorov backward equation / adjoint):

$$v(x_0,y_0) = (K_\tau^\dagger a)(x_0,y_0) = \mathbb{E}\big[a(X_\tau)\mid x_0,y_0\big]$$

That's the viability landscape: one backward pass, or one forward ensemble from a broad reference distribution with importance reweighting. Then every intervention is an inner product, no re-simulation:

$$\mathcal{V}_I = \langle I[p],\, v\rangle \qquad \mathcal{S}_\mathcal{A} = \langle p - I_\mathcal{A}[p],\, v\rangle$$

Semantic-content search over subsets $\mathcal{A}$ becomes cheap enough for greedy or Shapley-style attribution. For entropic $\mathcal{V}$ the same works to first order with the landscape $v^{(1)}(x_0,y_0) = \mathbb{E}[\ln p_{X_\tau}(X_\tau) + 1 \mid x_0,y_0]$, and exactly at the cost of one push of the intervened distribution through the precomputed marginal kernel.

A local decomposition that falls out of this

Writing the scramble as a reweighting gives

$$\mathcal{S} = \mathbb{E}_p\Big[\big(1 - e^{-i(x;y)}\big)\, v(x,y)\Big], \qquad i(x;y) = \ln\frac{p(x,y)}{p(x)p(y)}$$

so semantic information is expected viability weighted by $1 - e^{-\text{PMI}}$. The pointwise term $s(x,y) = (1-e^{-i})\,v$ is a local semantic map: which environment states, paired with which system states, are actually carrying the survival. That's the direct analogue of Lizier's local information dynamics, and it tells you where in state space to look before you scramble anything. High-PMI cells with low $v$ are correlations the system has but doesn't need; negative-PMI cells with high $v$ are where misinformation lives.

Structural shortcuts from the causal graph

If you have the DAG, don't search over all of $\mathcal{Y}$:

Only ancestors of the viability node within horizon $\tau$ can carry semantic information. Read that off the graph.
The semantic content's support is the Markov boundary of the future-viability variable restricted to initial environment variables: scrambling anything outside it leaves viability unchanged by conditional independence. So the graph gives you the support for free and the simulation is only needed for magnitudes.
Coarse-grain first with a causal-emergence criterion (Hoel's effective information, or Barnett–Seth dynamical independence) so the scramble runs on a macro state space.
Cheap observational filters, before any intervention

Two things are computable from time series alone and bound what intervention can find.

Syntactic bound. For $v \in [0,1]$, Pinsker gives

$$|\mathcal{S}| \le \mathrm{TV}\big(p,\ p_X\!\otimes\!p_Y\big) \le \sqrt{I(X_0;Y_0)/2}$$

so if the mutual information is tiny you're done. Small $I$ cannot hide large $\mathcal{S}$.

Predictive filter. Still's nonpredictive information $I(X_t;Y_t) - I(X_t;Y_{t+1})$ is observational. Information that doesn't predict the environment's future can't be load-bearing for viability under it, so the predictive part of the system's memory is a necessary-condition envelope for the semantic part. Compute the $I(X_t;Y_{t+k})$ profile in $k$ to see over what horizons anything semantic could exist at all.

When you genuinely can't intervene

This is your "I have a causal model but not the real system" case, and it's better than it sounds. Scrambling is a soft intervention: replace $p(x_0\mid y_0)$ with $p(x_0)$. That's a stochastic policy intervention in the sense of Correa and Bareinboim, and with the right graph it's identifiable from observational data. For a single confounder,

$$\mathcal{V}_{\mathrm{scr}} = \mathcal{V}\Big[\textstyle\sum_{x_0} p(x_0)\sum_{y_0} p(y_0)\, P(X_\tau \mid x_0,y_0)\Big]$$

which is all observational conditionals. The sequential version (randomize the cue at every step) is Robins' g-formula with the cue mechanism replaced — the standard machinery for exactly this kind of question, given no unmeasured time-varying confounding.

The catch is positivity. When correlation is strong, the mismatched $(x_0,y_0)$ cells are precisely the ones you never observe, and they're precisely the ones the scramble populates. Semantic information estimation is an off-support extrapolation problem. The causal model or simulation isn't just convenient here, it's what fills those cells, and $\mathcal{S}$ is exactly as trustworthy as that extrapolation and no more. That's the honest failure mode: a confident $\mathcal{S}$ whose value is entirely determined by how your model behaves in regions it was never fit on.

Time-resolved version

Scramble at intermediate time $t$ rather than $0$ and plot $\mathcal{S}(t) = \mathcal{V}[p] - \mathcal{V}[\mathrm{scr}_t\, p]$ against $t$. All cheap with the landscape trick. The profile tells you when the system is spending its information, and the drop rate $-d\mathcal{S}/dt$ is a semantic-information-flow rate you can compare across systems or against transfer entropy from $Y$ to $X$.

If I had to pick three: backward landscape, local map, Pinsker filter. Those turn the problem from "run a combinatorial number of simulations" into "run one and do linear algebra."
