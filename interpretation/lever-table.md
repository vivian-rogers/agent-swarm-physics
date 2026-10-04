# Lever table (working file, 2026-10-04)

Reconciles the round-1b results of H29, H30, H35, H39, H43, H50 and H04 (RE-V1). Assembled by RE-V2 and the coordinator. All numbers are exploratory (non-holdout). H59, the one-lever model, starts from this table.

**Terms:**
- **Field:** a lever changes *which* state agents occupy.
- **Catalytic:** it changes transition *rates*, i.e. how fast agents leave a state.
- **Read-out:** the lever acts at the recipient's next model call.

| Lever | Field (what changes) | Catalytic (rates) | Read-out delay / gating |
|---|---|---|---|
| Nudge (leading @) | Yes: idle/wait share −5 to −8 points while it acts (H39, both state spaces) | Yes: escape ×1.3–1.6, K +0.13 to +0.25 (H39); a glance, not sustained work (H43) and not commits (H35 r1b) | Read at the next call (median 122 s in #51); response immediate at the receiving call (RE-V1, H43); no refractory beyond one read-out (H43) |
| Nudge size | ≈ 1 extra active minute: H30 0.98 / 1.07, H04 1.16 [0.75, 1.57]; ≈ 0.4% of commits (H35) | First ≈ 1.2–1.4, repeats 0.4–0.9 | 1.42 bits per nudge; best used once early in a pause chain (H35) |
| Nudge context | Works better under the 5-min pause default than the 12-h one (NE44: H30, H39); no early wakes either side (RE-V1) | Works in swarm-wide lulls (1.74 vs 0.72; round 1's warning was a data artifact) | Not a novelty effect (NE10) |
| Nudger switched off (NE43) | No occupancy field; swarm work unchanged (H35) | Catalytic loss: escape at the bottom of placebos (H39) | Bookend messages are not a lever: the runner starts agents (H38, H50) |
| Human message | Field: work vs chat in regime I; content pull +0.024 (room-mates), +0.041 (named) (H30) | ≈ 0 | Onset at the first read-out call (H50); per-message pull falls over 1–7 messages read together (#5) |
| Operator message to one agent (NE38) | Strong content field on the named agent (H29, H10) | – | Does not relay to bystanders within 2 h |
| @-mention / naming | Content field: drift toward the message +0.33 SD (H39); named ≫ unnamed, unnamed ≈ 0 in regime III (H29; H50 J₁ 0.17 vs 0.004) | Small K (+0.04), no behavioral direction | Gated at exactly one read-out call (H50); unaddressed messages couple only in regime I |
| Relay choice | – | – | Rank by net reply current (held-out ρ ≈ 0.1–0.2), not by volume or content-pull "driver" score (H29) |
| Designated or elected leader | Gets attention (replies ×1.4, #35) but no extra broadcast reach in regime II; the elected leader's broadcast pull rose in regime I (#26) | – | – |
| Context erasure | Field toward work in both state spaces (H39) | K depends on the state space (−0.15 B4, +0.27 V4); costs ~10% of a segment's committed output (H15, H44) | – |
| Document sharing (forecast week) | Reading a teammate's document moves an agent toward them (H24 G21 DiD, +0.03; fades under style residualization) | – | – |
| One-lever test (H59) | At the read-out (0–2 calls) every class acts as a talk-ward field with small catalysis (G51: nudge κ 0.33, h 3.97; @-mention κ 0.14, h 3.77; named human κ 0.60, h 4.39; broadcast human κ −0.12, h 1.77) | Class differences live in the tails (nudge 30-call tail ≈ nudger selection; regime-I mentions act on the work↔wait edge); leave-one-class-out fails in 4/4 periods | Class levers invariant across NE43; one read = one kick (#5 dose saturates) |

**Reading.**
- Nudges are cheap attention levers (a glance and about one active minute) that barely move committed work.
- Naming is the content lever, and it acts in one hop: it reaches the named agent and does not spread to bystanders.
- Erasure is the only lever with a material output cost.

None of this is holdout-confirmed.
