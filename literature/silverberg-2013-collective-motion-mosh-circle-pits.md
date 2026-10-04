# Collective motion of humans in mosh and circle pits at heavy metal concerts

**Citation:** Jesse L. Silverberg, Matthew Bierbaum, James P. Sethna and Itai Cohen, *Phys. Rev. Lett.* 110, 228701 (2013). DOI: 10.1103/PhysRevLett.110.228701
**File:** silverberg-2013-collective-motion-mosh-circle-pits.pdf
**Fields:** stat mech, active matter, dynamics, sociophysics

## Summary
The authors ran particle image velocimetry on concert videos (6 usable out of more than 100 watched). Mosh pits behave like a 2D gas: the velocity correlation is a pure exponential and speeds follow the 2D Maxwell–Boltzmann distribution. A Vicsek-like model of self-propelled soft disks with alignment and noise ("MASHers") gives two states:
- a disordered gas (the mosh pit) at high noise and weak flocking;
- an ordered vortex (the circle pit) at low noise and moderate flocking.

In both states the active particles phase-separate inside a ring of passive ones. The equilibrium-looking statistics come from the central limit theorem: noise or collisions randomize self-propelled motion. Setting $v_0=0$ ends all pit behavior. Real circle pits turn counter-clockwise 95% of the time (p < 0.001), while the model is symmetric; the authors guess handedness is the cause.

## Key formalism
- **Forces** (unit mass; $\ddot{\vec r}_i$ = sum):
  - repulsion $\epsilon(1-r_{ij}/2r_0)^{3/2}\hat r_{ij}$ for $r_{ij}<2r_0$;
  - propulsion $\mu(v_0-v_i)\hat v_i$;
  - flocking $\alpha\sum_j\vec v_j/|\sum_j\vec v_j|$ over neighbours within $r_{flock}=4r_0$;
  - noise $\vec\eta_i$ with $\langle\eta_{i\lambda}(t)\eta_{i\kappa}(t')\rangle=2\mu\sigma^2\delta_{\lambda\kappa}\delta(t-t')$.
- **Parameters:**
  - $\epsilon=25$, $\mu=1$, $r_0=1$; active $v_0=1$; passive $v_0=\alpha=\eta=0$.
  - $N=500$, packing fraction $\rho=0.94$, 30% active, periodic $L=1.03\sqrt{\pi r_0^2N}$.
  - Sweep $\alpha\in[0,1]$, $\sigma\in[0,3]$ ($4.8\times10^5$ runs).
  - Phase separation forms in about $10^3\,r_0/v_0$ and is stable beyond $10^5$.
- **Order parameter:** the rms angular momentum of active particles about their centre of mass, computed on the torus as $x_{cm}=(L/2\pi)\arctan[\mathrm{Im}A/\mathrm{Re}A]$ with $A=\sum_i e^{-2\pi i x_i/L}$.
- **Time scales:** $\tau_{flock}=v_0/\alpha$, $\tau_{noise}=v_0^2/2\mu\sigma^2$, $\tau_{coll}=1/(2r_0v_0\rho)$.
- **Phase diagram:**
  - Gas if $\tau_{noise}\ll\tau_{flock}$ (boundary $\sigma\sim\sqrt{v_0\alpha/\mu}$) or $\tau_{coll}\ll\tau_{flock}$ ($\alpha\ll2r_0v_0^2\rho\sim1$; empirically $\alpha\sim10^{-2}$).
  - Vortex if $\tau_{flock}\ll\tau_{noise},\tau_{coll}$. Simulated vortices are CW or CCW with equal probability and switch at random.
- **Data:**
  - Mosh pit: $c_{vv}(r)$ exponential with decay length $0.39\pm0.03$ m (shoulder width).
  - Speed PDF $P(v)=(2v/T)e^{-v^2/T}$; the fitted $T(t)$ falls over about 35 s ("a hot pit cools").
  - Circle pit: $c_{vv}$ most negative at $r\approx6$ m, the pit diameter.

## Mapping to agent swarms
- **Maps:**
  - *Position:* agents have no physical position, but they have positions in embedding space. Use DQ5 `agent_win30_style_resid_period` vectors (both models; aggregates are robust). Velocity = the change per window, or per own call (H40's call clock).
  - *Self-propulsion $v_0$:* own call cadence (`call_windows`) times the typical step per call.
  - *Active vs passive:* `behavior_states_v3` (execute_task vs monitor_wait/idle) or `activity_bins_fixed` states 3–4 vs 1–2.
  - *Noise σ:* the fitted residual step. Model temperature and sampling are the intended analogue, but they are provider-set and not logged.
  - *Flocking α:* the regression of $\vec v_i$ on the mean velocity of the senders read at that call (`context_ledger_items`). The neighbourhood is topological, and H47 puts the coherence length at the room.
  - *Repulsion ε:* anti-duplication (H11's static specialization; H58's #51e avoidance).
  - *A hot pit cools:* $T(t)=\langle|\vec v|^2\rangle$ after a kickoff (H54 quench).
  - *$v_0=0$:* cadence or nudger step changes (NE20, NE43).
  - *CCW bias:* model priors breaking a symmetry.
- **Doesn't map:**
  - There is no metric neighbourhood, contact force, packing or confinement.
  - The 32-d embedding is anisotropic, so angular momentum needs a 2-PC projection and has no natural meaning there.
  - N is about 4–15 per period, against 500.
  - Day edges and goal switches cause velocity jumps that are not noise.
- **Physics model:** `physics-models/11-vector-spins` plus propulsion. DQ8 `simulate.py` has O(32) vector spins and DeGroot dynamics for nulls.

## Candidate hypotheses
- **Gas statistics in uncoupled weeks.**
  - *Observable:* Rayleigh fit of 2-PC speeds (and the 32-d χ distribution), and $c_{vv}$ against H41 static hop distance.
  - *Prediction:* exponential decay of about 1 hop. Heavy tails mark coupling.
  - *Null:* Maxwell–Boltzmann itself (CLT), so only departures count.
  - *Impostor:* the scheduler field (drop first_of_day windows).
- **Alignment beats noise only where reading is dense.**
  - *Observable:* per period, fitted $(\hat\alpha,\hat\sigma,\hat v_0)$ and polarization $\phi=|\sum\hat v_i|/N$, with each period a point on the $(\alpha,\sigma)$ diagram.
  - *Prediction:* ordered periods sit below $\sigma\sim\sqrt{v_0\alpha/\mu}$.
  - *Null:* a block-shift surrogate; the finite-N floor of φ is about $N^{-1/2}$.
  - *Impostors:* the kickoff/goal field (a common drift toward the goal gives φ without alignment, so fit α net of the `goal_fields` direction) and contemporaneous convergence (alignment with in-flight unread senders must be lower).
- **The kickoff heats, the swarm cools in calls.**
  - *Observable:* the $T(t)$ decay after each kickoff, timed in minutes and in own calls.
  - *Prediction:* per-call decay (H40), faster with more read alignment.
  - *Null:* placebo dates.
  - *Impostor:* the kickoff field (compare agents with no reads in the window).
- **Cadence is self-propulsion.**
  - *Observable:* φ and the $c_{vv}$ amplitude across NE20 and NE43.
  - *Prediction:* both fall when cadence drops.
  - *Null:* placebo dates and DQ8 rate-matched independent agents.
  - *Impostor:* the scheduler field.
- **Chirality is the prior.**
  - *Observable:* the mean-velocity direction at ordering onsets against the leave-period-out family prior.
  - *Prediction:* the direction is predictable, not random as in the model.
  - *Null:* random direction on $S^{31}$.
  - *Impostor:* the kickoff field (remove the goal direction first).

## Caveats
- The Maxwell–Boltzmann form is the CLT null, not evidence of interaction, as the paper itself says.
- Statement-level geometry is model-dependent (10-NN overlap 0.26), so use agent-window aggregates and both models. Raw vectors carry family style (H13, H46).
- Velocity depends on the window Δ.
- Small N gives large finite-size order. Fit per period and compare periods; never pool.
- Criticality readings were refuted before (H03, H25, H26), and activity synchrony is the scheduler, so activity-based order parameters are out.
- "Noise = temperature" is an analogy: the sampling parameters are unknown and vary by provider.
