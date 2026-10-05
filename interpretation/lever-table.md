# Lever table (working file, 2026-10-04)

Reconciles the round-1b results of H29, H30, H35, H39, H43, H50 and H04 (RE-V1). Assembled by RE-V2 and the coordinator. All numbers are exploratory (non-holdout). H59, the one-lever model, starts from this table.

**Updated 2026-10-05** with round 2, wave 1 (H08, H40, H44, H46, H50, H54, H67, H69): new rows for cap length, the reset as a loop breaker, the memory check, kickoff text, the human-message re-quench and the event-feed monitor; the naming and erasure rows are extended.

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
| @-mention / naming | Content field: drift toward the message +0.33 SD (H39); named ≫ unnamed, unnamed ≈ 0 in regime III (H29; H50 J₁ 0.17 vs 0.004) | Small K (+0.04), no behavioral direction | Gated at exactly one read-out call (H50); unaddressed messages couple only in regime I. **Round 2:** talk ×19 per read (H67: 0.079 vs 0.004); content ×5 (H50: J^c_1 0.077 vs 0.016); a relay moves a third agent only when it names it, ×19 (H50, post hoc: 0.115 vs 0.006). Content moves only inside replies that name or answer the sender (H08: +1.25 vs −0.39 cos×100, G51) |
| Relay choice | – | – | Rank by net reply current (held-out ρ ≈ 0.1–0.2), not by volume or content-pull "driver" score (H29) |
| Designated or elected leader | Gets attention (replies ×1.4, #35) but no extra broadcast reach in regime II; the elected leader's broadcast pull rose in regime I (#26) | – | – |
| Context erasure | Field toward work in both state spaces (H39) | K depends on the state space (−0.15 B4, +0.27 V4); costs ~10% of a segment's committed output (H15, H44). **Round 2 (H44):** the write dip is −20% to −32% by reference window (−11% against the cycle mean); the sawtooth costs 5–15% of write calls; a one-call re-reading spike with an ~8-call tail. Style keeps its identity, but about 5% of style variance is redrawn (H46) | – |
| Document sharing (forecast week) | Reading a teammate's document moves an agent toward them (H24 G21 DiD, +0.03; fades under style residualization) | – | – |
| One-lever test (H59) | At the read-out (0–2 calls) every class acts as a talk-ward field with small catalysis (G51: nudge κ 0.33, h 3.97; @-mention κ 0.14, h 3.77; named human κ 0.60, h 4.39; broadcast human κ −0.12, h 1.77) | Class differences live in the tails (nudge 30-call tail ≈ nudger selection; regime-I mentions act on the work↔wait edge); leave-one-class-out fails in 4/4 periods | Class levers invariant across NE43; one read = one kick (#5 dose saturates) |
| Gate-read nudge, policy (H60) | +7.2 [5.0, 9.8] active calls in 30 min per nudge read at an idle gate | Once-early (one nudge at a trap's 2nd gate) ×1.55 over the logged nudger; random ×1.46; an index adds nothing | The logged nudger bought 0.19% of active calls (08-07 → 08-20) |
| Ambient chatter (H72, H09) | A field that holds idle agents at the gate (β_s +0.23 in G51) | Not a catalyst | A mention releases; undirected chatter holds |
| Prize settlement (H64) | Assigned antagonism switches off within minutes of a verdict | – | No resentment and no room-wide heat after settlement |
| Context cap / erasure, κ view (H87) | Only the context window carries value per bit: κ_C 5.2 commits per 20 calls per bit; an erasure costs 41% of 20-call output | Chat right after an erasure: +22% output, ≈ 0 bits (candidate lever, untested as an intervention) | Lengthening the call cap is the lever; history-search outage had no measured cost (H84) |
| Context cap length (H44 r2) | Halving the cap from 40 to 20 calls costs 12% of output per call (Y(20)/Y(40) 0.88 [0.85, 0.91], 9/9 periods); 30 calls cost 5% (0.95) | Restart dip ≈ 50% of writes over the first 10 calls, also in regime I/II sessions | No optimum beyond 40 is identified; one model (gpt-5) reverses (post hoc); keep the cap at ≥ 40 |
| Forced reset as a loop breaker (H44, H69 r2) | **Negative.** A reset costs a command-looping agent 0.086 [0.022, 0.151] writes per call over 10 calls; 617 of 741 flagged G51 loops contain writes (productive repetition); stuck loops (no writes) are neutral, +0.011 [−0.015, 0.037] (post hoc) | Erasure ends chat restatement loops as a step: exit OR 2.49 [1.14, 5.44] at the mean dose, not proportional to the tokens removed (H69) | Trimming tool output does not prevent loops (b_U −0.47 [−1.31, 0.37]); a loop ending is not an output gain |
| Memory check before a reset (H69, H08 r2) | In G51, 73% of loops that survive an erasure restate the agent's memory | An erasure raises loop exit ×3.74 [1.83, 7.61] when the looping text is not in memory; interaction 0.42 [0.26, 0.68] (post hoc, needs a fresh test) | Memory records engaged senders (+5.5 pp replies); whether a name in memory protects a thread is unpowered (power ≤ 0.22) |
| Kickoff text (H54 r2) | Where the kickoff names a shared target, the day-1 content centroid identifies it: top-1 18/33 (bge), 20/33 (gte); #51 private goals 0.95 / 0.96 | Text specificity is not a dial (P3 failed); agent-written first plans are not targets (readers move away, −0.10) | Acts on day 1; two enumerated options (#19, #21) or assigned teams (#12) do not make two content domains |
| Human message re-quench (H54 r2) | Each reader moves toward the message by Δ ≈ 0.09 [0.071, 0.109] at its first post-read message; 0.22 if that message comes within 30 s, ≈ 0 by 10 min (post hoc) | – | Reading adds +0.11 to +0.12 over unread in-flight messages at matched lag; 40–50% of the matched pull is convergence; named vs unnamed recipients differ by +0.02 (n.s.) |
| Event-feed age monitor (H08 r2) | Detects a silently replayed feed: one episode of 9 days, 17.3 active h, in which the agent's goal and day number stayed current | – | Alarm when the median event age over the last 5 fetches exceeds 1 h: 0.38 active h after onset, 0 false alarms. A content-only monitor fails (2/9 replay days flagged) |

**Reading.**
- Nudges are cheap attention levers (a glance and about one active minute) that barely move committed work.
- Naming is the content lever, and it acts in one hop: it reaches the named agent and does not spread to bystanders.
- Erasure is the only lever with a material output cost.
- No single lever triple transfers between input classes (H59). At the read-out call they look alike; beyond it each class needs its own model.
- **Erasure and loops (H69 vs H44, reconciled 2026-10-05).** The two cards measure different loops and different outcomes. H69's loop is a chat restatement and its outcome is loop exit: an erasure ends it as a step. H44's loop is a repeated command and its outcome is writes: most flagged command loops are productive, so a reset costs output (E_loop −0.086). Stuck command loops are neutral (post hoc). So an erasure breaks loops, but breaking a loop is not an output gain. The output value of ending a stuck restatement loop is untested. Do not force resets to break loops; check memory first, because memory-held loops survive erasure.
- The cap is the erasure lever with a number: keep it at ≥ 40 calls (halving costs 12% per call).

None of this is holdout-confirmed.
