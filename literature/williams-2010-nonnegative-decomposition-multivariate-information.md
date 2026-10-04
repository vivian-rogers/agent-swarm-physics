# Nonnegative decomposition of multivariate information

**Citation:** Paul L. Williams and Randall D. Beer, arXiv:1004.2515 [cs.IT] (2010).
**File:** williams-2010-nonnegative-decomposition-multivariate-information.pdf
**Fields:** info theory

## Summary
The paper that started partial information decomposition (PID). It asks how the information that sources $R=\{R_1..R_{n-1}\}$ carry about a target $S$ splits into unique, redundant and synergistic parts. It defines redundancy $I_{min}$ as the minimum specific information any source gives about each outcome $s$, averaged over $s$. The ways sources can share information form a lattice, and Möbius inversion of $I_{min}$ on that lattice gives nonnegative atoms. Interaction (co-)information turns out to be synergy minus redundancy, which explains why it can be negative. PID is asymmetric: one variable must be named the target.

## Key formalism
- Specific information: $I(S{=}s;A)=\sum_a p(a|s)[\log\frac{1}{p(s)}-\log\frac{1}{p(s|a)}]\ge0$, and $I(S;A)=\sum_s p(s)I(S{=}s;A)$.
- $I_{min}(S;\{A_1..A_k\})=\sum_s p(s)\min_i I(S{=}s;A_i)$. It is nonnegative, at most each $I(S;A_i)$, and equals $I(S;A)$ for a single source. It is monotone on the lattice.
- Lattice: antichains of sources (no source contains another), ordered by $\alpha\preceq\beta\iff\forall B\in\beta\,\exists A\in\alpha:A\subseteq B$. Sizes are 1, 4, 18, 166, 7579 for 1–5 sources.
- Atoms: $I_{min}(S;\alpha)=\sum_{\beta\preceq\alpha}\Pi(S;\beta)$, with closed form $\Pi(S;\alpha)=I_{min}(S;\alpha)-\sum_s p(s)\max_{\beta\in\alpha^-}\min_{B\in\beta}I(S{=}s;B)$. All atoms are ≥ 0.
- **Two sources (4 atoms):** Rdn $=\{1\}\{2\}=I_{min}$; Unq$_1=I(S;R_1)-I_{min}$; Syn $=I(S;R_1R_2)-I(S;R_1)-I(S;R_2)+I_{min}$.
- **Three sources (18 atoms):** 3 unique $\{i\}$; 3 pairwise Rdn $\{i\}\{j\}$; 3 pairwise Syn $\{ij\}$; $\{1\}\{2\}\{3\}$; $\{123\}$; 3 $\{i\}\{jk\}$ (one variable alone or the other two jointly); 3 $\{ij\}\{ik\}$; $\{12\}\{13\}\{23\}$.
- **Interaction information:**
  - With 3 variables: $I(S;R_1;R_2)=I(S;R_1|R_2)-I(S;R_1)=\text{Syn}-\text{Rdn}$.
  - With 4 variables it adds $\{123\}$ and $\{1\}\{2\}\{3\}$ and subtracts the mixed atoms, so 3-parity (pure synergy) and three copies of $S$ (pure redundancy) both give +1 bit.
- **Examples:**
  - XOR: Syn = 1 bit, everything else 0.
  - Fig. 4A: Unq$_1$ = Unq$_2$ = Syn = 1/3 bit and Rdn $=\log_23-1\approx0.585$ bit, so the co-information is negative although synergy is present.
  - Fig. 4B: Rdn = Syn = ½ bit, co-information 0.
- **Known problems with $I_{min}$ (later work, from memory †):**
  - It measures "same amount", not "same information": two independent bits copied into $S=(R_1,R_2)$ get 1 bit of redundancy. So it overstates redundancy and violates the identity axiom (Harder, Salge & Polani, PRE 2013†).
  - Fixes:
    - $I_{red}$ (Harder et al.†);
    - **BROJA** (unique information minimized over distributions with fixed $(S,R_i)$ marginals; Bertschinger et al., Entropy 2014†);
    - **$I_{ccs}$** (pointwise common change in surprisal; local atoms can be negative; Ince, Entropy 2017†);
    - $I_{dep}$ (James et al. 2018†) and $I^{sx}$ (Makkeh et al. 2021†);
    - Gaussian MMI, Rdn $=\min_i I(S;R_i)$ (Barrett, PRE 2015†).
  - With 3 or more sources, nonnegativity, identity and local positivity cannot all hold (Rauh et al. 2014†).
  - The lattice is reused to split transfer entropy (Williams & Beer 2011†), to define modification as synergy (Lizier et al. 2013†) and in ΦID (Mediano et al.†).

## Mapping to agent swarms
- **Target $S$:**
  - the next-bin repo, i.e. H58's which-artifact unit state $x_G(b{+}1)$ or own DQ4 `work_commits` allocation;
  - a marker adoption (H34/H41);
  - the next `behavior_states_v3` state, sampled from `p_*`.
- **Sources:**
  - $R_{own}$: the agent's own last state or repo (the agent + own artifact null unit);
  - $R_{read}$: what entered context at the call (`context_ledger_items` joined to chat `artifact_mentions`);
  - $R_{field}$: goal naming (`goal_fields`, H54), the scheduler (`call_windows.gap_kind`) and the leave-period-out agent prior (DQ5 `style_resid_period`).
- **HH299:**
  - Storage = $I(S;R_{own})$.
  - TE $=I(S;R_{read}|R_{own})$ = Unq$_{read}$ (state-independent transfer, i.e. copying) + Syn$_{read,own}$ (state-dependent transfer, i.e. modification).
- **HH298:**
  - $\Omega_3=\text{Rdn}-\text{Syn}$, which is minus Williams–Beer interaction information. A shared field adds Rdn that can mask Syn.
  - Ω < 0 shows net synergy; Ω ≥ 0 does not rule synergy out.
- **H41:** $R_{read}$ exists only in-cone. Posted-but-unread (in-flight) messages at matched lag are a placebo source, and co-generation appears as their redundancy with $R_{read}$.
- **Estimators:** Gaussian PID on DQ5 `agent_win30_style_resid_period` (both models). Plug-in estimates on small alphabets (H58: ≤ 7 symbols; 11 Jev states).

## Candidate hypotheses
- **Transfer is unique, not synergistic (HH299).**
  - *Observable:* Unq$_{read}$ vs Syn$_{read,own}$ about the next-bin repo per goal period (BROJA and $I_{ccs}$).
  - *Prediction:* Syn/Unq < 0.2 outside merge or election periods.
  - *Null:* read items permuted across the same agent's calls within a day.
  - *Impostor:* kickoff/goal field. With $R_{field}$ added as a third source, the $\{read\}$ atom must survive and not move into $\{read\}\{field\}$.
- **Day-1 transfer is redundant with the field.**
  - *Observable:* the $\{read\}\{field\}$ atom in the first 48 h of each goal versus later.
  - *Null:* placebo mid-period dates.
  - *Impostor:* contemporaneous convergence. Unq$_{read}$ must exceed the unique atom of an in-flight placebo source at matched lag.
- **Synergy lives at merges (HH298).**
  - *Observable:* Syn of two read parents about the adopted repo or convention: NE42, #26 election rounds, DQ2 `reply_pairs` with opposing stance.
  - *Null:* DQ8 `simulate.py` copy-only dynamics (Potts herding, DeGroot) on the real schedules.
  - *Impostor:* shared model priors. The effect must hold for cross-family parent pairs.
- **After erasure the artifact holds the unique information (H44/H58).**
  - *Observable:* target = first post-reset repo (`context_ledger_turns.reset_forced`). Sources = artifact re-read (`artifact_mentions` read verbs), last memory, and peer chat read.
  - *Prediction:* Unq$_{artifact}$ > Unq$_{memory}$ ≈ 0 (H15).
  - *Null:* placebo calls without a reset.
  - *Impostor:* the scheduler field (first_of_day calls re-read too).

## Caveats
- $I_{min}$ inflates redundancy, which is exactly the copier answer HH299 predicts. Report BROJA and $I_{ccs}$, and trust a conclusion only if they agree.
- Samples per period are small (hundreds of agent-bins). Keep ≤ 3 sources, bundle the impostors into one field source or condition on them, and shuffle-correct the bias. Large repo alphabets need top-k plus "other".
- Fit within goal periods and compare atoms across periods. Never pool.
- PID about agent i's next state is not group synergy. HH298's Ω is target-free and needs its own estimator.
- Linear residualization removes only the linear field. Gaussian MMI zeroes the weaker source's unique information by construction.
- Measure sources at `t_call`. Behavior windows (5 min) are coarser than calls, and 21% of ledger items are `uncertain`.
- Mask the holdout.
