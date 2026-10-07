# 16 · Langevin relaxation: Ornstein–Uhlenbeck wells, damped oscillators and two-rate kicks

**Fields:** stat mech, dynamics, stochastic processes
**References:** Uhlenbeck & Ornstein, *Phys. Rev.* 36, 823 (1930)† (the OU process; autocorrelation e^(−γτ)); Kubo, *Rep. Prog. Phys.* 29, 255 (1966)† (fluctuation–dissipation: for a linear Langevin system the impulse response equals the normalized autocorrelation); Landau & Lifshitz, *Mechanics* §25† (damped oscillations, logarithmic decrement); Glauber, *J. Math. Phys.* 4, 294 (1963)† (the attempt rate sets the relaxation time); Brown, Barbieri, Ventura, Kass & Frank, *Neural Comput.* 14, 325 (2002)† (time rescaling); Friedkin & Johnsen, *J. Math. Sociol.* 15, 193 (1990)† (opinion dynamics anchored to an initial position: a social analog of a private well).

Added 2026-10-07. Before that date the cards below named model 11 (vector spins) as primary and 02 as secondary. This folder collects the relaxation dynamics they share. Card verdicts did not change.

**Name clash.** Model 11's mean-field section uses the *Langevin function* L(x) = coth x − 1/x, the mean-field magnetization of n = 3 spins. That is a static equation of state. This folder is about *Langevin dynamics*: a state that relaxes in a potential well with noise. The two have only a name in common.

## The model

An agent's state x (a content vector, a style vector, a memory size, a collective mode) sits in a potential well with centre c(t). Noise ξ pushes it away; the well pulls it back.

**1. Overdamped well (Ornstein–Uhlenbeck).**

$$\dot x = -\gamma\,(x - c) + \xi(t), \qquad \langle \xi(t)\,\xi(t') \rangle = 2D\,\delta(t-t')$$

- Stationary variance σ² = D/γ. Autocorrelation C(τ) = σ² e^(−γ|τ|).
- On a discrete clock (one step per model call n): x(n+1) − c = (1 − γ)(x(n) − c) + ξ(n). This is an AR(1) process with φ = 1 − γ.
- **Vector form:** ẋ = −Γ(x − c) + ξ with a stiffness matrix Γ. Different eigenvalues of Γ give different rates along different directions (an anisotropic well). The eigenmodes of Γ are the dynamic modes of [17](../17-collective-modes/).
- **Step response:** if the centre jumps from c₀ to c₁ at t = 0, then ⟨x(t)⟩ − c₁ = (x(0) − c₁) e^(−γt). The displacement is linear in the starting distance and passes through the origin.
- **Moving well:** if c moves at speed v, x trails it with lag v/γ.

**2. Damped oscillator (underdamped Langevin).**

$$\ddot x + 2\zeta\omega_0\,\dot x + \omega_0^2\,(x - c) = \xi(t)$$

- With ζ < 1 a step response overshoots the new centre and then undershoots it. The ratio of successive extremes gives ζ (logarithmic decrement δ, ζ = δ/√(π² + δ²)).
- With ζ ≥ 1 there is no undershoot.
- Inertia in the swarm would be agents carrying plans and open tasks past the target.

**3. Overdamped well under a fading field.** The centre itself decays after a step: c(t) = c_∞ + c₁ e^(−t/τ_f). The response is a sum of two decaying exponentials. It can rise above c_∞ (an overshoot) and decay back from above. A sum of two exponentials crosses the settled level at most once, so it gives no undershoot.

**4. Two-rate form: a fast kick on a slow well.** The state has two parts, x = s + k.
- s is a slow OU process with rate γ_s (the agent's own well).
- k is a fast part with rate γ_k ≫ γ_s. Inputs (reads, kickoff text) enter k, not s.
- A one-rate OU model predicts γ_kick = γ_auto: the impulse response and the autocorrelation decay at the same rate (Kubo). The two-rate form breaks that relation.
- A **two-timescale homeostat** (H71) is the same idea for a regulated quantity: fast correction around a slowly drifting set point.

## Interesting behavior

- **One rate sets both fluctuation and response.** For a linear Langevin system the decay of the autocorrelation and the decay of the response to a kick have the same rate. This is an unfitted consistency check (Onsager regression; model 02's fluctuation–dissipation section). Two different rates mean the input acts through a second channel.
- **An overdamped particle cannot overshoot a fixed target.** An overshoot needs inertia (ζ < 1, which predicts an undershoot) or a target that moves or fades (which does not). The undershoot is the test that separates them.
- **The clock is part of the model.** If the well acts once per attempt (a model call), relaxation curves collapse when time is counted in calls (Glauber). If it acts in wall time, they collapse in hours.
- **A step on the centre gives a linear law through the origin.** Each agent's displacement is χ_i times its starting distance, with χ_i = 1 − e^(−γ_i τ). A nonzero intercept means overshoot or a common jump.
- **Two timescales leave a signature in the autocorrelation:** ρ₂ > ρ₁² (an AR(2) term), and the one-exponential fit depends on the lag window.

## Mapping to the village

| Model quantity | Village variable | Cards |
| --- | --- | --- |
| state x | agent content vector (unit, regime-whitened, d = 32; DEFINITIONS "Agent state", vector variant) | H97, H125, H127, H130 |
| state x | agent style vector (H46's 17-d style) | H46 |
| state x | post-compression memory size x⁺ | H71 |
| state x | the regime-I collective slow mode u_b | H81, H106 |
| well centre c | the kickoff target (a step field along k̂, model 11) | H97, H125, H127 |
| well centre c | a private well h_i: role, own project, model prior (H98's static random field) | H130 |
| well centre c | the agent's own style mean; the memory set point | H46, H71 |
| kick | a read at the read-out call (model 02's read-out coupling); a kickoff read; a forced erasure (reset) | H130, H127, H46 |
| clock | call clock (H40); active-hour clock (H103); calendar days | all |

## How to fit (or measure)

1. **Autocorrelation per lag.** Fit C(τ) = A e^(−γτ) + B on lags ≥ 1 (statement noise adds only at τ = 0). B absorbs a slowly drifting centre. Correct for common drives first (H130's drive-corrected γ_auto).
2. **Event-triggered response.** Average the state after kicks that happened. Subtract a placebo that shares every time-local field: messages posted during the producing call cannot be read by it (the in-flight placebo, H130, H67).
3. **Step response at kickoffs.** Use ordinary day boundaries of the same agents along the same direction as the placebo (H97). Use the disattenuated cross-agent correlation ρ, not the regression slope β, for unit-normalized vectors (H97 Amendment 1).
4. **Model-free shape tests before fits.** The undershoot U = (days 4–5 level − days 2–3 level) separates oscillator from fading field (H125). The share of agents whose rise ends inside the read-out call separates relaxation from a jump (H127).
5. **The rate ratio.** ρ_γ = γ_kick / γ_auto. The one-rate model predicts ρ_γ ∈ [0.5, 2].
6. **Clock tests start at the read-out call.** With a t₀ origin, the call clock wins even under pure read-out jumps (H127).
7. **Per period.** Fit within a goal period. Combine kickoffs or units with a random-effects meta-analysis and report the per-unit values beside it (exception (d)).

## Nulls and controls

- **Placebo boundaries:** ordinary day-to-day memory of the same agents (H97 N0; weekend-matched variant).
- **In-flight placebo at matched posting age:** removes echo and common drive from the read kick (H130).
- **Decoy kickoffs:** the generic pull of any kickoff text (H125's genericness correction).
- **Rivals to state in every card:** pure translation (a push with no well), common target / full reset, constant speed, fading field, context-held kick, random walk (φ = 1), static field only (κ = 0).
- **Synthetic worlds on the real skeleton** with each rival planted. Every estimator in H97, H125, H127 and H130 was replaced or amended after such a run, before real data.

## Pitfalls

- **Unit-normalized vectors fake forgetting** (H97): a day where everyone talks about one thing compresses every agent's deviation. The IV slope β then passes the restoring-force test under pure translation in 45–90% of replicates. Use the disattenuated correlation ρ (false-positive rate 0.025–0.05).
- **SSE model comparison on day series is liberal** (H125): the oscillator wins 18–19 of 27 single kickoffs, close to the 56–59% that heavy day noise alone gives. Decide with the model-free undershoot U.
- **Clock tests from t₀ favour calls under read-out jumps** (H127): the read-out sits at call 1 but at an agent-specific hour. Start the clock at the read-out call.
- **Restatement inflates the day-1 spike** (H125, H127): the first statements after a kickoff copy its text. Drop copies of the kickoff before reading the amplitude; U should not change.
- **Mixed sampling phases fake an overshoot** (H71): `memory_stats` writes an append snapshot, then a compress snapshot, at each consolidation. The mixed series gives φ < 0 in 10/10 regime-III periods while φ⁺ > 0.
- **A fast kick rests on few lags** (H130): γ_kick comes from the first 2–3 lag bins, so its CI spans ×4. Test the one-rate claim with the lower bound of ρ_γ.
- **One slow trajectory is one sample** (H106): regime I spans about 13 decay times of the slow mode. Comparing two segments of that one path cannot test a size law (oracle SD of the exponent 0.45).
- **A slow outside drift is also OU-shaped** (H81): a calendar-time OU mode with no reading effect reproduces the shape. State the drift rival and the clock; H81 could not identify the clock.
- **A one-exponential fit of a pair cross-correlation reads ≈ 0.6–0.8 γ** (H130 model): the cross-correlation of two OU particles is (1 + γ|τ|) e^(−γ|τ|), not one exponential.
- **Style drift is not OU here** (H46 round 2): the style variance does not grow reliably with context position, and the within-segment style overlap ΔC(l) does not decay over eight messages. ΔC(1) is already 0.64 [0.35, 0.95] at the first message after a reset. A per-segment offset, drawn at the reset and held, fits instead (post hoc). No relaxation scale is identified.

## Cards that test it

**Primary (the OU form is the card's model):**

| Card | Form tested | Latest verdict | Key numbers |
| --- | --- | --- | --- |
| [H97](../../hypotheses/H97-quench-restoring-force/README.md) | overdamped well centred by the kickoff; scalar χ_i per agent | supported (restoring force); the literal law fails | extra forgetting Δρ +0.26 ± 0.04 over 18 kickoffs, 16/18 positive; along k̂ 0.63 vs transverse 0.25 (anisotropic); day-1 overshoot intercept +0.12 ± 0.02; agent constancy inconclusive (r 0.30, p 0.14; power 0.30) |
| [H125](../../hypotheses/H125-kickoff-damped-oscillator/README.md) | damped oscillator vs overdamped well under a fading field | failed (overdamped) | undershoot U −0.006 [−0.020, +0.008] (bge), −0.002 [−0.017, +0.013] (gte), 27 kickoffs; power 1.00 at ζ ≤ 0.5; overshoot E₁ +0.055 ± 0.012 (22/27); day profile +0.059, +0.019, +0.001 on days 1–3 |
| [H127](../../hypotheses/H127-content-trails-goal-call-clock/README.md) | overdamped catch-up to a moved well, rate set by the call rate | not supported; slope inconclusive | 74% of 152 rising agents reach their day-1 plateau within the read-out call (synthetic relaxation worlds ≤ 0.20); spike 2.4× the plateau at the read-out call, 1× after about 64 calls (about 1 h); call-rate slope +0.59 [−0.45, +1.75] (power ≈ 0.35) |
| [H130](../../hypotheses/H130-ou-private-wells-51/README.md) | vector OU in private wells with read kicks, one rate (#51) | failed (kill K1) | read jump J_K 0.044 [0.038, 0.050] (11/12 units); well γ_auto 0.0094 [0.0076, 0.0115] per call (1/γ ≈ 100 calls ≈ 1 h; I² 0); kick γ_kick ≈ 0.13–0.17 per call (≈ 6–8 calls); ρ_γ 14.8 [7.2, 30.4] (bge), 20.2 [6.8, 59.9] (gte) |

**OU forms inside other cards:**

| Card | Where the OU form appears | Outcome |
| --- | --- | --- |
| [H46](../../hypotheses/H46-style-conserved-charge/README.md) | round 2: an OU drift-and-reset of style around the agent's charge | the OU form fails (kill rule fired; ΔC(l) 0.70, 0.70, 0.83, 1.02 for l = 1–4: no decay); a per-segment offset redrawn at each erasure fits (post hoc; ΔC(1) ≈ 5% of style variance) |
| [H71](../../hypotheses/H71-memory-homeostat/README.md) | first-order relaxation of memory size to a set point | set point yes (φ⁺ 0.67 [0.63, 0.71] per cycle, CI excludes 1 in 37/37); first order no (AR(2) median +0.19); a two-timescale homeostat fits (post hoc; slow set point ρ_s ≈ 0.82 per cycle) |
| [H81](../../hypotheses/H81-culture-beyond-composition/README.md) | an OU collective slow mode in regime-I content | supported in regime I: τ_u ≈ 23–28 days; one OU mode also fits H82's boundary trace (joint τ 20.9 ± 2.8 / 15.5 ± 2.2 d); inside #51 the common mode lives about 3 active days; the clock is not identifiable |
| [H106](../../hypotheses/H106-slow-mode-finite-size/README.md) | rotational diffusion of a finite magnet: the slow mode's rate should fall as 1/N | inconclusive: α_k +0.40 [−1.62, 2.41] (bge), +1.22 [−1.45, 3.88] (gte); power 0.00 against α = −1 |

**Related, under model 02:** [H44](../../hypotheses/H44-erasure-reacquisition-thrash/README.md) finds a forced erasure gives a one-call re-reading spike, then a tail of 8.2 [5.8, 11.8] calls (G51). That fast scale is close to H130's read kick.

## Combined result (2026-10-07)

1. **The kickoff is a well.** It erases each agent's position faster than an ordinary night does (H97, Δρ +0.26 ± 0.04). The well is stiffer along the kickoff direction than across it.
2. **The response is overdamped.** Day 1 overshoots the settled level (H97 +0.12; H125 E₁ +0.055), but days 2–3 do not undershoot (H125 U ≈ 0, powered for ζ ≤ 0.5). The overshoot is a field that fades, not inertia. Damping between 0.5 and 1 is not excluded.
3. **The field arrives in one call, then fades.** An agent's alignment jumps at its read-out call of the kickoff (74% of rising agents) and decays from 2.4× to 1× its plateau over about 64 calls (H127). There is no per-agent catch-up time.
4. **Two rates, not one.** In #51 a read kicks the next statement (J_K 0.044), and the kick decays in about 7 calls. The agent's own well relaxes in about 100 calls. The kick decays about 15 times faster than the well (ρ_γ 14.8, lower 90% bound 7.2).
5. **Every one-rate form fails.** H130 (ρ_γ ≈ 15), H46 (no OU decay of style), H71 (not first order), H127 (no relaxation to time) and H125 (no oscillation). The form that describes the data is a fast kick on a slow well (two-rate, post hoc in H130 and H71).
6. **A slow collective scale exists in regime I only** (H81, τ_u ≈ 23–28 d). Its size law is untestable in one village (H106).

**Status:** partly useful. The overdamped two-rate form describes every card. It was chosen after the data in H130 and H71, so it still needs a pre-registered test.

## Hypothesis seeds

- **Two-rate kernel at 1-call resolution** (H130-R1): fit the read-response kernel over 0–10 calls. Test whether the fast kick ends at the agent's next talk call or decays smoothly.
- **The fading field's time constant** (H125-R1): fit the decay of the kickoff read-out spike on the call and hour clocks. Compare it with H130's kick rate (≈ 7 calls) and well rate (≈ 100 calls).
- **Kick vs reply** (H130-R2): split reads by whether the next statement is a reply to the sender.
- **Well formation** (H130-R3): fit joiners' approach to their well over days as a third, slower rate.
- **Transfer** (H130-R4): measure the two rates in shared-goal regime-III periods (#38–#44), where wells are weaker.
- **A pre-registered two-rate test:** predict ρ_γ ≈ 15 and the 64-call spike decay on reserved periods before running them.
