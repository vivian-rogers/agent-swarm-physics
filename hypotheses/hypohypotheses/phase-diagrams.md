# Phase diagrams: idle speculation

Which "phase diagrams" could we actually draw from the AI Village data, and which would be easiest? Nothing here has been computed.

## What a phase diagram means here

We can't sweep control parameters. Each **goal period** (51 of them), each **regime**, and each **room** within a period is one sample of the system at some setting. A phase diagram is then a scatter of those samples in a 2D control plane, colored by an order parameter. Theory curves are overlaid where a model predicts a boundary.

**Control parameters the data gives us for free.** Per goal period, from [goal-periods.md](goal-periods.md):
- N (4–32 agents);
- hours per day (2, 3, 4, 8);
- coupling mode (C/K/M/I/F, our coding);
- who wrote the goal (O/D/F/A/P);
- regime (I/II/III);
- number of rooms;
- family mix;
- nudger on or off;
- time since kickoff (within a period).

**Confounds.** N, regime and calendar time all rise together. Natural experiments break some of these links:
- NE21 (hours 4 → 8 → 4 → 8 h) separates hours from date;
- NE12 (rooms) cuts coupling at fixed N;
- batch joins (NE27, NE33) step N at fixed regime;
- #51 is a 55-day window in which N grows from 21 to 32 under a single goal, a *path* through the diagram rather than a point.

## Ranked by ease, easiest first

1. **Criticality map: Hawkes branching ratio (model 09).** *Easiest.*
   - Order parameter: branching ratio n (the endogenous fraction) per goal period. Control plane: N × hours/day, colored by coupling mode.
   - Needs only event timestamps (`AGENT_TALK`, or all agent events). No text processing.
   - Expected picture: free weeks and holidays subcritical; shared-objective weeks near n ≈ 1; #51 creeping toward criticality as N grows.
   - Theory line: n = 1 (critical).
   - Ideas: HH30, HH32, HH46. Periods: holidays #3, #5, #7, #9 vs. shared-objective weeks; #51 as a trajectory; NE21 as a reversible cut.
2. **Spin-glass placement: inverse Ising (models 01/02).**
   - Fit couplings J_ij on binary active/silent spins per goal period. Compute the mean coupling J₀ = N·mean(J) and the spread J = √N·std(J). Place each period on the classic Sherrington–Kirkpatrick plane (J₀/J vs. T/J), with its paramagnet / ferromagnet / spin-glass regions.
   - Needs binned activity per agent; no text.
   - Expected picture: null weeks (#10, #14, #49) in the paramagnet; competitive weeks toward glassy, frustrated territory; shared-objective weeks ferromagnetic.
   - Ideas: HH01 (temperature dropping: a heat-capacity peak per period), HH44 (null weeks).
2b. **Susceptibility map (models 01/02, 09, 11).** *About as easy as #2.*
   - Order parameter: χ per goal period, from three sources:
     - **fluctuations:** N·Var(m) and the top eigenvalue of the correlation matrix, from the same binned activity as #2;
     - **response:** event-triggered averages after nudges, human messages and kickoffs;
     - **Hawkes:** total response 1/(1 − n).
   - Control plane: N × hours/day, colored by coupling mode. Peaks mark near-critical periods.
   - Second layer: the ratio of response to fluctuation (the fluctuation–dissipation violation, i.e. an effective temperature). That turns the same plot into a *nonequilibrium* map.
   - Needs: binned activity plus kick timestamps (nudger messages, `USER_TALK`, kickoffs). Still no text processing.
   - Ideas: HH01, HH18 (the nudger), HH30–HH32. Periods: all; NE23 (nudger off/on) and NE21 (hours reversal) as checks. Details in models 01, 02, 11 (susceptibility sections).
3. **Neutral cooperative dynamics (model 06).** *The best theory-vs-data diagram.*
   - The Piñero et al. paper gives **analytic boundaries** in the (μ, N) plane: bimodal below μ_B = e⁻²/√(2πN), log-series above μ_L = √(2/(πN)).
   - Order parameter: Simpson index λ, or bimodality of project abundances. μ is the rate at which new topics appear.
   - Needs project or topic labels: cluster session goals and `CONSOLIDATE` `nextSessionGoal` once (short texts). Medium effort.
   - Ideas: HH16, HH42. Periods: free weeks #11, #16, #22, #31, #37, and #51.
4. **Consensus diagram: Potts (model 10).**
   - Order parameter: largest share among agents' project labels, plus the jump size at consensus.
   - Control: coupling mode × N, or time since kickoff × mode.
   - The interesting boundary is between continuous and first-order consensus (q ≥ 3).
   - Same topic labels as #3, so cheap once those exist.
   - Ideas: HH22, HH25, HH26. Periods: #19, #26, #31, #40.
5. **Irreversibility map: nonequilibrium Ising (model 02).**
   - Order parameter: lower bound on entropy production per agent-hour (Aguilera estimator).
   - Control: regime × number of rooms, or hours/day.
   - Needs binned activity; the estimator is more work than a Hawkes fit.
   - Ideas: HH19, HH33, HH45. Natural experiments: NE12, NE14.
6. **Quench response: vector spins (model 11).**
   - Order parameter: polarization along the goal direction. Control: time since kickoff × coupling mode, which gives a dynamic phase diagram: how fast order forms and decays per mode.
   - Needs embeddings of chat and goal texts. Medium-hard: watch for anisotropy.
   - Ideas: HH27–HH29. Periods: #8, #21, #41, #44.
7. **Contagion threshold (model 03).**
   - Order parameter: final outbreak size of memes. Control: effective R₀ (exposures × rate) × spontaneous-adoption field ε. Expected shape: an absorbing-state transition smeared by the field.
   - Needs a meme catalog plus transmission trees. Hard.
   - Ideas: HH09, HH35–HH37.
8. **Superagent phase diagram (H01, D3).**
   - Order parameter: semantic entropy of group positions, vs. coupling mode × group size.
   - Depends on the D3 order parameter, so it comes last. It's the one we most want.

## Recommendation

Start with **1** (timestamps only, a day of work), **2** (binned activity only) and **2b** (the same data plus kick timestamps). Together they give a first physical portrait of all 51 periods, including how close each sits to criticality and to equilibrium, using no text.

Then **3**: the one with a published theory curve to beat. It also produces the topic labels that **4** reuses, and that **8** eventually needs.

Draw every diagram twice: once per goal period, and once as the #51 trajectory. Overlay the NE21 reversal as a check that the axes, not the calendar, drive the picture.
