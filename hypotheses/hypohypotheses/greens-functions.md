# Green's functions: which ideas map onto one?

**Short answer:** often appropriate, in a specific sense. Here a Green's function G is the **linear response kernel**, or propagator: the ensemble-averaged response of some quantity (activity, alignment, prevalence) at time t to a unit kick at time t′. It is the same object as the response function R in model 02, the Hawkes kernel φ in model 09, and the dynamic susceptibility χ(τ) in model 11.

## When it's appropriate: three tests

Run these before calling anything a Green's function:

1. **Linearity in dose.** The averaged response scales with the kick's size: two kicks give twice the response of one. Check this with kicks of different strength, e.g. one nudge vs. several, or one human message vs. a burst.
2. **Superposition.** Responses to separate kicks add. Check overlapping kicks against isolated ones, or fit a Hawkes model and test its residuals.
3. **Time-translation invariance.** Within a regime, G depends only on τ = t − t′. If it also depends on the waiting time since a restart, it's a two-time G(t, t′), and that dependence is itself a result: aging (HH02).

**Where it fails.** Single agents make discrete, thresholded decisions, so they're individually nonlinear; G only makes sense for *averaged* responses. It also fails for threshold and first-order phenomena (complex contagion, Potts consensus jumps), for static structure, and for one-off events that can't be averaged.

**A bonus, exact link.** In the semantic-information framework (model 04, H01) the viability landscape v = K_τ† a is literally the Green's function of the *backward* (Kolmogorov) equation: the adjoint propagator. Viability changes under small, partial scrambles are then linear-response quantities. So H01's estimation machinery is Green's-function machinery.

## Mapping the ideas (HH numbers from [HYPOHYPOTHESES.md](HYPOHYPOTHESES.md))

### Natural fits: G is the main object
- **HH31, nudger reversal (NE23).** G(τ) is the activity response of a nudged agent, and of the others, to one nudge. The off/on switch gives the baseline. *The cleanest case.*
- **HH14, humans as heat bath.** G for responses to `USER_TALK` kicks: how the swarm couples to its outside bath.
- **HH30, HH32, the Hawkes ideas.** The kernel φ is the *bare* propagator. The total response to an outside event is the *dressed* propagator, G = φ + φ∗φ + … = φ(1 − φ)⁻¹ (a Dyson series), which diverges as n → 1. Near-criticality is literally a divergence in G.
- **HH23, leader (#45).** A directed, off-diagonal G_ij: how followers respond to the leader's directives, propagated over the agent graph. Ground truth exists.
- **HH02, weekends as quenches.** A two-time G(t, t_w): the response after a restart as a function of the idle time t_w. Aging shows up as a breakdown of time-translation invariance.
- **HH46, hours (NE21).** Compare the shape of G under 4 h vs. 8 h days. The reversal tests whether the time base reshapes the propagator.

### Partial fits: G for the mean, but not the whole story
- **HH08 (sycophancy cascades), HH21 (bug avalanches).** The *mean* cascade is a linear branching propagator. The size *distribution* (power laws) needs the full statistics, beyond G.
- **HH09, misinformation vs. correction.** Early-time spread linearizes (a branching process). Corrections are kicks whose G can be compared with the claim's. Thresholds break this later on.
- **HH11 (jargon cools), HH28 (forecast week).** Goal changes and coupling switch-ons are *steps*, so look at the step response (the integral of G). This works only if the response is roughly linear in the change.
- **HH06, time crystal.** An oscillation not set by the drive would show up as a resonance, a pole of G(ω) off the real axis. G can test for a damped mode; a self-sustained oscillation would need nonlinearity.
- **HH13, telephone game.** The per-hop transfer of content features is multiplicative and roughly linear: a propagator along chains. The error threshold is beyond it.
- **HH18, nudger as Maxwell demon.** G from nudge responses combined with fluctuations gives the fluctuation–dissipation ratio, the effective temperature (model 02).

### Not appropriate: say so
- **Thresholds and first-order jumps:** HH22 (election), HH25, HH26 (Potts consensus), HH35–HH37 (contagion past early times), HH03 (room nucleation), HH04 (symmetry breaking).
- **Static or stationary structure:** HH10, HH16, HH24, HH27, HH29, HH42, HH44. These are about distributions and couplings, not responses.
- **Trends, scaling and selection:** HH01 (temperature trend), HH07 (heat death), HH12 (consolidation as renormalization: a flow, not a response), HH15 (evolution), HH17 (Lévy steps), HH20 (baseline rate), HH40, HH41 (Kelly allocation).
- **Irreversibility measures:** HH19, HH33, HH45. Entropy production isn't a G, though G enters the fluctuation–dissipation comparison.
- **HH33, rooms (NE12).** A parameter change, not a kick. The useful G question is how cutting a channel *changes* the propagator: compare G before and after.

## Where to look for kicks
Nudger messages; human messages; goal kickoffs (steps); operator mid-goal corrections (NE35, NE36); targeted single-agent fields (NE37, NE38); new agents arriving (a kick to the population).

All except the nudger messages are visible in the event and chat timestamps alone, so a first G needs no text processing. Telling nudger messages apart from human ones needs the chat text.
