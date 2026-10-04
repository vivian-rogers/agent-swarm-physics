# 09 · Hawkes processes (self-exciting point processes)

**Fields:** dynamics, stat mech, sociophysics
**References:** Hawkes, *Biometrika* 58, 83 (1971)†; Crane & Sornette, "Robust dynamic classes revealed by measuring the response function of a social system", *PNAS* 105, 15649 (2008)†; Hardiman, Bercot & Bouchaud, "Critical reflexivity in financial markets", *EPL* 103, 18008 (2013)†; Filimonov & Sornette, "Apparent criticality and calibration issues in the Hawkes self-excited point process model", *Quant. Finance* 15, 1293 (2015)†; Bacry, Mastromatteo & Muzy, "Hawkes processes in finance", *Market Microstructure and Liquidity* 1, 1550005 (2015)†.

## The model

Events arrive in continuous time. Each event temporarily raises the rate of future events. For agents i = 1…N with event times t_k^j:

$$\lambda_i(t) = \mu_i(t) + \sum_j \sum_{t_k^j < t} \phi_{ij}(t - t_k^j)$$

- μ_i(t) is the **exogenous** baseline: events that would happen anyway.
- φ_ij(τ) ≥ 0 is the **kernel**: how much an event by agent j raises agent i's rate τ later. Common choices are exponential (α e^{−βτ}) or power law (∝ τ^{−(1+θ)}).
- The **branching matrix** K_ij = ∫ φ_ij(τ) dτ is the expected number of i-events directly triggered by one j-event.

**Cluster (branching) picture.** Every Hawkes process can be read as: "immigrant" events arrive at rate μ, and each event independently has children according to the kernel, and so on. That makes each cascade a Galton–Watson branching process, the same object as an SIR outbreak in model 03.

**Branching ratio.** n = spectral radius of K (in one dimension, n = ∫φ). The process is stationary only if n < 1. In a stationary process, n is exactly the fraction of events that are **endogenous** (triggered by earlier events) rather than exogenous.

## Interesting behavior

- **Endogeneity has one number.** n = 0 is pure response to outside input; n → 1 is a system whose activity is almost entirely self-generated. Financial markets measured this way sit close to n ≈ 1 ("critical reflexivity").
- **Criticality without fine tuning?** n near 1 is a critical branching process: power-law cascade sizes (s^{−3/2}) and long memory. It's the point-process version of model 03's epidemic threshold.
- **Shocks from outside vs. from inside decay differently.** With a power-law kernel φ ∝ τ^{−(1+θ)}, Crane & Sornette predict three response classes for activity after a burst:
  - exogenous shock, near-critical: A(t) ∝ t^{−(1−θ)}
  - endogenous burst, near-critical: A(t) ∝ t^{−(1−2θ)}
  - exogenous shock, subcritical: A(t) ∝ t^{−(1+θ)}

  So the shape of the decay tells you where a burst came from, and the system's distance from criticality.
- **Directed influence from timing alone.** The multivariate branching matrix K is a who-triggers-whom network. It is the point-process analog of model 02's asymmetric couplings.

## Mapping to the village

- **Events:** per agent, `AGENT_TALK` times first. Then all agent actions in `events`, or computer-use turns. Marks (event type, room) can be added.
- **Exogenous inputs, which can be modeled explicitly as external kernels:**
  - human messages (`USER_TALK`)
  - auto-nudger messages
  - goal changes (`village_goals`)
  - village-hours start
- **Time:** activity stops outside village hours and on weekends. Either give μ(t) the daily schedule, or work in active time with the gaps removed. See Clock time and Activity time in `../DEFINITIONS.md`.
- **Inhibition:** an agent waiting on its own model call, or choosing to `WAIT`, can't act. That is self-inhibition, which plain Hawkes (φ ≥ 0) cannot represent. Use a nonlinear Hawkes process (rate = f(μ + Σφ) with signed kernels) if fits show it.

## How to fit

1. **Exponential kernels, maximum likelihood.** Fast, because the likelihood is computable recursively. A good first pass.
2. **EM on the branching structure.** Treat "which event caused which" as latent. It also gives each event a probability of being exogenous or triggered by a particular agent, i.e. a reconstructed transmission tree (useful for models 03 and 08).
3. **Nonparametric kernels.** Wiener–Hopf / moment methods recover φ_ij(τ) without assuming a shape. They need more data.
4. **Goodness of fit: time-rescaling theorem.** Transform inter-event times by the fitted cumulative intensity; if the model is right they are Exponential(1). KS test and QQ plot.

## Nulls and controls

- **Inhomogeneous Poisson** with the same time-varying baseline (daily schedule, goal periods) but no excitation. Hawkes must beat it on held-out likelihood.
- **Shuffled cross-agent timing:** keep each agent's events but shift them relative to each other. Off-diagonal K should vanish.

## Pitfalls

- **Model the recipient's call clock before comparing kernels** (H42, 2026-10-04): talk is locked to each agent's own call starts, so a call-clock baseline beats H03-style models in 57/57 units, and inside it cross-excitation nearly vanishes (median n_cross 0.004 vs 0.061 exponential). Exponential kernels overstate cross-triggering by counting schedule co-movement. Shift and day-block nulls do not control a shared 15-min field. Only messages naming the recipient excite talk (regime III, ~0.15 events each, post hoc).
- **At N ≤ 25 a fitted cascade exponent does not estimate 3/2** (H34): with a cutoff the fit is biased (0.5–2.9), and the apparent exponent is a monotone function of the branching ratio (ρ = −0.95 with R̂), so it carries no extra information. Activity Hawkes n̂ does not predict idea spread (ρ = 0.06).
- **Endogenous turn timing fakes attention dilution** (H18): with reactive turn timing and no attention budget, the per-message response rate still falls with the backlog (β̂ ≈ 0.78). Identify dilution from exogenous batch sizes (timer wakes), and count only messages visible in the agent's room.
- **Do not calibrate n against the equal-time dial** (H67, 2026-10-04): the 1-min dial reads fast shared fields as gain (regime I: g_eq − g_lag +0.17 where read-out coupling is ≈ 0). The read-out loop gain g_lag = m̄ r̄ J₁\* is the branching ratio of talk through reading. It ranks periods like H42's read-out n_cross (Spearman 0.55, 35 periods).

- **Nonstationarity fakes criticality.** If the true baseline varies (time of day, goal changes) but μ is fitted as constant, the fit attributes the variation to self-excitation and n is pushed toward 1 (Filimonov & Sornette 2015). Model the baseline seriously before believing any n near 1.
- **Scheduler regularity.** If the scaffolding polls agents on a fixed cadence, event times inherit that clock. Check the inter-event-time distribution for spikes at fixed lags first.
- **Small N, many parameters.** N² kernels for N ≈ 10–30 agents; regularize, or group agents by model family.
- **A flexible baseline doesn't identify n either** (H03, 2026-10-03). A Poisson process with a 10-min rate profile gives n̂ ≈ 0.5 under a smooth within-day baseline. Report a bracket over baselines (constant → smooth → per-day cells), not a single n.
- **Jitter tests can be unpowered.** Jittering event times by ~10 min barely moves n̂ for a true n = 0.6 process (Δ ≈ 0.025). Calibrate a jitter test's power on synthetic data before reading anything into it.
- **Slow cross-kernels mimic shared modulation.** Cross-excitation with timescales of 10–30 min is indistinguishable from a common rate drive. Only fast cross terms (seconds to a few minutes) beat agent-shift nulls cleanly.
- **Day windows with gaps.** Days containing two sessions with a long silence distort the within-day baseline shape. Split days at silences longer than about 1 h.

## Hypothesis seeds

- Most agent activity is endogenous: n > 0.5 for chat, with a time-varying baseline already accounted for.
- n is higher (closer to critical) in collaborative goal periods than in "pick your own goal" periods.
- Responses to human messages decay like the exogenous class, and spontaneous chat bursts like the endogenous class, with exponents consistent with a single θ.
- The branching matrix K agrees with model 02's antisymmetric couplings on who leads and who follows.
