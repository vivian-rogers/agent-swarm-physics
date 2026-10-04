# Decomposing information into copying versus transformation

**Citation:** Artemy Kolchinsky and Bernat Corominas-Murtra, *J. R. Soc. Interface* 17, 20190623 (2020). arXiv:1903.10693 (v3, 2020-01-11).
**File:** kolchinsky-2020-copying-versus-transformation.pdf
**Fields:** info theory, thermodynamics

## Summary
Mutual information cannot tell a perfect copier (cat→cat) from a perfect permutation (cat→snake), although the two have the same I(X;Y). From four axioms, the paper derives the unique split of each specific mutual information (more generally, each Bayesian surprise) into non-negative copy and transformation parts. Copy information depends only on how much more often the output equals the input than the prior predicts. The measure generalizes to any loss function (graded similarity, different alphabets, continuous variables) as a minimum-cross-entropy problem related to rate–distortion. Copy information is also the minimal thermodynamic work to make exact copies, and transformation information lower-bounds the extra work. In a PAM amino-acid substitution matrix, about a quarter of the transmitted information is transformation.

## Key formalism
- Channel p(y|x), source s(x), destination marginal p_Y. Specific MI I(Y:X=x) = D_KL(p_{Y|x} ‖ p_Y). The prior p_Y may be **any** distribution (Bayesian-surprise form), not only the channel marginal.
- **Copy information** (unique under Axioms 1–4): D_x^copy = d(p(x|x), p_Y(x)) if p(x|x) > p_Y(x), else 0. Here d(a,b) = a log(a/b) + (1−a) log((1−a)/(1−b)) is the binary KL. Transformation: D_x^trans = D_KL(p_{Y|x}‖p_Y) − D_x^copy ≥ 0.
- Totals: I(Y:X) = I^copy(X→Y) + I^trans(X→Y), and H(Y) = I^copy + I^trans + H(Y|X). Copying efficiency η = I^copy/I ∈ [0,1] (per message or per channel). Any channel with p(x|x) ≤ p_Y(x) for all x has I^copy = 0 at any level of MI.
- Properties that differ from MI: directional (I^copy(X→Y) ≠ I^copy(Y→X)); **no data-processing inequality** (encrypt then decrypt raises copy information); **not additive** over independent sub-channels, because "copy" means the whole message is reproduced. A vector-valued loss restores additivity (App. C3).
- Binary symmetric channel: all MI is copy for error ε ≤ 1/2 and all transformation for ε ≥ 1/2.
- **Generalized copy information** for loss ℓ(x,y): G_x^copy = min_r D_KL(r‖p_Y) s.t. E_r[ℓ(x,Y)] ≤ E_{p(·|x)}[ℓ(x,Y)]. The solution is w(y) ∝ p_Y(y) e^{−λℓ(x,y)}, so G_x^copy = −λ E_{p(·|x)}[ℓ] − log Z(λ), found by a 1-D sweep in λ ≥ 0. 0–1 loss recovers D^copy; squared error handles continuous outputs.
- Thermodynamics (nats): W_min^exact(x) = kT D_x^copy(p_{Y|x}‖π_Y), and W − W_min^exact ≥ kT D_x^trans. When π_Y = p_Y, the efficiency ⟨W_min⟩/⟨W⟩ = η.
- PAM example (Le–Gascuel matrix, τ = 1): I ≈ 1.2 bits = 0.88 copy + 0.32 transformation, with H(Y|X) ≈ 2.97 bits. Copy information correlates with physico-chemical "outlierness" (Spearman 0.57, p = 0.009) but transformation does not (0.22, p = 0.35).
- Stated open problem: a copy/transformation split of conditional MI, and hence of transfer entropy.

## Mapping to agent swarms
- **Channel = one read hop.** x = an identifiable item in a read (context ledger `context_ledger_items`: a repo, URL, H34 marker or number). y = the same-alphabet item in the reader's next output: the repo of its next DQ4 `work_commits` row, or the marker in its next statement. Exact identity gives D^copy; a repo→repo remap (fork, sibling, "the other one") is transformation.
- **Graded content.** Let ℓ = 1 − cos between the source statement and the reproduction (DQ5, both embedding models, style residuals). G^copy then measures near-copying, and DQ5 `cross_echo_cos`/`cross_echo_src` give candidate pairs. Prefer the vector-valued loss when one message carries several items, so copy information adds up across items.
- **Self-channel = storage.** For an agent's own allocation chain X_t → X_{t+1} (DQ4 which-repo per call, or `behavior_states_v3`), copy = staying put and transformation = systematic switching (e.g. build → test → deploy cycles). This splits active information storage into persistence and computation, and gives model 08 a per-agent η.
- **Impostors handled by the prior.** Because the prior can be any distribution:
  - *Contemporaneous convergence:* use as prior the reproductions by agents who had **not** read x at matched lag (in-flight placebo, H57). D^copy(p(·|read) ‖ p(·|unread)) is the copy information that reading adds.
  - *Kickoff/goal field:* items the kickoff names have high p_Y(x), so their copy information is small even when everyone reproduces them. Estimate p_Y within the goal period, never pooled.
  - *Shared model priors:* a transformation that is the same across families and also appears without a read is the prior, not the channel (iterated learning). Report I^trans per family.
  - *Scheduler:* count hops on the per-call clock (one read → next call), so day edges carry no weight.

## Candidate hypotheses
- **Identifiers copy and ideas transform.** Copy efficiency η ≥ 0.8 for repo names and URLs across a read hop, and η ≤ 0.3 for H34 content markers. *Kill:* similar η across types.
- **Copy beyond convergence is small for content.** H57 found unread pairs within 15 s are near-copies as often as read pairs, so D^copy against the unread prior should be ≈ 0 for content at short lag but > 0 for identifiers. That would locate the read effect in pointers, not prose.
- **Telephone threshold.** If each of L units copies with fidelity q, exact-copy probability is q^L and copy information vanishes when q^L ≤ p_Y(x). Prediction: multi-hop chains (H41 light cone) keep identifiers for ≥ 3 hops and lose whole-plan copy information after 1–2 hops. Converged chains should drift toward the family prior (model 08).
- **HH299 split without PID.** Measure copy vs transformation for the read→next-output channel directly. This is a lower-bound complement to the PID split, which cannot tell a systematic remap (unique information, no copying) from copying.

## Caveats
- The measure needs a shared alphabet or a defensible loss. With embeddings, the loss choice is the result; report both models.
- Whole-message copy information is fragile: one changed token zeroes D^copy under 0–1 loss. Use per-item or vector losses.
- No data-processing inequality, so copy information along a chain can rise again (re-reading the original repo restores the identity). Chains must be defined by reads, not by time.
- The thermodynamic reading (minimal work) has no token-cost analogue unless redefined; treat it as a metaphor.
- The paper does not give a copy/transformation split of transfer entropy. Any conditional version (prior = p(y|own past)) is our extension and needs synthetic checks.
- Agent narration of "copying" is a claim; use logged reads and outputs only.
