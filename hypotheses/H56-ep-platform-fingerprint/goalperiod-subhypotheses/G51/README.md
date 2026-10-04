# H56 × G51: private roles, one long period with many step changes (2026-07-06 → 2026-09-04 non-holdout)

**Verdict:** mixed
**Role:** native (exploratory, round 1, non-holdout; also carries the period's replication numbers)
**Period:** regime III · private individual goals · 21 → 32 agents (31 test agents) · 45 non-holdout active days. Step changes inside: roster joins (07-09 isolated GPT-5.6 trio, 07-10, 07-17, 07-24, 08-28, 09-01, 09-03/04), NE38 role reassignment (07-29), #focus room opens (08-05) and closes (08-24), NE43 (nudges end 08-20; bookends end 08-04). **No documented scaffold change** after 07-03. The #51 tail (09-07 →) is held out.

## Why this period
Nine weeks in which the platform, by the changelog, did not change, while the roster, rooms and operator did. For H56 it is a negative control (EP should not move at roster or room changes) and a search space for undocumented platform changes (EP change-points not explained by any catalogued event, with the platform signature: most agents and every provider shifting the same way).

## Prediction
*Written 2026-10-04 06:00 UTC (card P10, P4 second part), before any real-data EP.* Within #51, blind change-points are not enriched near roster joins or room changes (≤ 1.5× chance) [0.6]; within-agent daily EP has no trend over the nine weeks (|Spearman ρ| < 0.3) [0.6]. Unexplained change-points are candidate undocumented platform changes; one shows the platform signature (f₊ ≥ 0.8 or ≤ 0.2, all providers the same sign) [0.4].

## Result
- **Negative control holds.** Roster, room and operator events (10 in the period) have 2 change-points within ±1 day against 2.9 expected by circular shifts (enrichment 0.69, p 0.93; V1). On V5 and the coarse chains, 0.7–1.4×, all p > 0.6. Per-event statistics (V1): joins t between −2.52 (Opus 5, 07-24; p 0.06) and −0.25; room 08-05 t −2.05 (p 0.047, the only nominal hit, not on V5: t −1.33, p 0.27); NE38 t 0.91; NE43 t −0.47; room 08-24 t 0.55.
- **Trend fails on the full chain.** The agent-demeaned daily EP declines over the nine weeks on V1 (ρ −0.40, p 0.006). It is weaker and not significant on the agent-only chains (V2 −0.28, p 0.06; V5 −0.25, p 0.09) and absent on coarse states (V3 +0.11). Part of the drift is in scaffold records.
- **Candidates.** Two V1 change-points have no catalogued event within ±1 day: **07-31** (t 2.03, f₊ 0.70, every provider positive), two active days after the **undocumented 07-29 change of the history-search tool's date fields** (found in the NE40 scan; also the NE38 day), and **08-10** (t 2.62, f₊ 0.59, every provider positive; also on V2 and V5). Neither reaches the pre-set signature (f₊ ≥ 0.8). With a 10% alarm budget, about 4 false alarms are expected in 45 days, so neither is evidence on its own.
- **Phase-diagram point:** median per-agent EP V1 0.042, V5 0.025, V3 0.009 nats/transition; scaffold share of the fine EP 0.17 (range −0.18 to 0.94). Family η² V1 0.22 (p 0.26), V5 0.20 (p 0.35). Google agents have the highest fine-chain EP (0.16 vs Anthropic 0.06, OpenAI 0.11).

Figure: `figures/g51_tday.pdf` (t(d) on V1 and V5 with every event). Data: `data/processed/H56-ep-platform-fingerprint/native/G51.json`, `replication/`.

## Scorecard (period-specific axes)
- **C (adequacy):** the null-enrichment test is calibrated by circular shifts within the period.
- **D (unfitted signature):** 0. No candidate shows the pre-set platform signature.
- **G (ground truth):** an undocumented tool-schema change (07-29) exists in the logs; the nearest EP change-point is two days later and not distinguishable from the false-alarm rate.

## Notes
- The #51 kickoff (07-06) is not scored: its pre-window lies in the NE21+NE23 holdout.
- **2026-10-04, ep_newton recheck (post hoc; card "Recheck (ep_newton fix)").** Held-out Newton bound. Enrichment 0.69× → 0.92× (p 0.71): held. The within-agent daily trend falls to V1 ρ −0.40 → −0.24 (p 0.12) and V5 −0.25 → −0.12 (p 0.43), so **the V1 trend failure is withdrawn**. The daily O1 values (n₀ = 120, d = 55) carry a legacy bias of about +0.04 nats/transition (synthetic). The 07-31 unexplained change-point is gone; 08-10 stays (f₊ 0.56). No #51 change-point shows the platform signature. The verdict stays **mixed**: P10 holds in both parts, and the signature search (P4, second part) found nothing.
