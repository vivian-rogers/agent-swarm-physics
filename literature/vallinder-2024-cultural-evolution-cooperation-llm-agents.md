# Cultural Evolution of Cooperation among LLM Agents

**Citation:** Aron Vallinder and Edward Hughes, arXiv:2412.10270 (2024); an extended abstract appeared at AAMAS 2025.
**File:** vallinder-2024-cultural-evolution-cooperation-llm-agents.pdf (arXiv v1, 19 pp.)
**Fields:** cultural evolution, multi-agent LLM systems, game theory

## Summary
The paper asks whether a society of LLM agents can evolve norms of indirect reciprocity across generations. Twelve agents of one model play the Donor Game (a donor gives x units, the recipient gets 2x) for 12 rounds in random pairings that never repeat, so only reputation can support cooperation. Each donor sees a trace of the recipient's last donation and its partner's earlier donations (up to three steps back). Each agent writes a one-sentence strategy at the start of a generation. The top half by final resources survive; six new agents write their strategies after reading the survivors' strategies and scores. This runs for 10 generations, 5 seeds per model. Claude 3.5 Sonnet populations evolve cooperation (more so with costly punishment), Gemini 1.5 Flash weakly, GPT-4o populations decline toward defection. Outcomes vary across seeds: in Claude runs, an initial mean donation of 50–54% led to cooperation and 44–47% did not.

## Key formalism and results
- **Evolution conditions** (Lewontin): variation from sampling temperature (0.8), transmission by prompting new agents with survivors' strategies, selection of the top 50%. Each generation is played twice so every agent is a final-round recipient once.
- **Maximum mean final resources** if all donate 100%: 30,720. Claude runs reach thousands; Gemini hundreds; GPT-4o tens.
- **Costly punishment** (spend x to remove 2x): raises Claude's outcome, lowers Gemini's (it punishes in 14.29% of encounters vs 1.65% for GPT-4o and 0.06% for Claude).
- **Ablations:** donation multipliers 1.5 and 3 do not change the ranking; a trace of length 1 instead of 3 weakens Claude's cooperation and removes Gemini's, so second-order reputation information matters.
- **Strategy complexity** grows across generations, most for Claude (weighted averages over the trace, caps, forgiveness factors).
- **Mutation bias:** new Claude agents tend to be more generous than survivors, new GPT-4o agents less, suggesting a model-specific bias in how strategies are rewritten.

## Mapping to paper 2
- This is the main LLM study of norms under cultural selection, and it is a designed setting: one model per population, a fixed game, explicit generations, operator-defined selection. The village has none of these. Our norms ("verify and correct", "consent and protection") emerge in a mixed-lab population with no payoff and no explicit selection.
- The strategy-transmission step (read survivors, write own) matches the village's context erasure: after a wipe an agent rebuilds its plan from its notes and the chat. That is a natural generation boundary per agent, and it is where we test whether a pattern is re-expressed.
- The model dependence and the rewrite bias are attractor effects (Perez et al.). In a mixed-lab village they are our "shared model prior" impostor.
- The paper's safety framing (cooperation can turn into collusion against humans) is the essay's misaligned-swarm question; our parasitic/mutualist measure asks the same thing of a pattern.

## Caveats
- Homogeneous populations, one game, short runs (10 generations), five seeds; no test of whether cooperation norms are carried by the text of strategies or by the base model alone.
- The AAMAS version is an extended abstract; cite the arXiv paper.
