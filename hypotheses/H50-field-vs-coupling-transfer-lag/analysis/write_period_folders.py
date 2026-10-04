"""Write the H50 period folders (G<NN>/, NE14/, NE43/) with dated predictions BEFORE the real-data run.
Replication periods get the templated prediction (labelled as such); native folders get their own designs.
Verdict and Result sections are filled later by write_period_results.py."""
from __future__ import annotations

import re
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / "hypotheses/H50-field-vs-coupling-transfer-lag"
GP = ROOT / "hypotheses/hypohypotheses/goal-periods.md"
UNITS = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/units.parquet"
STAMP = "2026-10-04 07:00 UTC"
NATIVE = {"G38", "G51", "NE14", "NE43"}

RULE = ("**Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, "
        "W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field "
        "excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% "
        "(the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.")


def titles():
    t = {}
    for line in GP.read_text().splitlines():
        m = re.match(r"### (\d+) · (.+)", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def header(name, title, period, role):
    return (f"# H50 × {name}: {title} ({period})\n\n**Verdict:** pending\n**Role:** {role}\n")


def replication(g, rows, title):
    regime = rows["regime"][0]
    units = ", ".join(f"{u} ({d} d, N={n})" for u, d, n in zip(rows["unit"], rows["n_days"], rows["N"]))
    span = f"{rows['first_day'].min()} → {rows['last_day'].max()}"
    npairs = int(rows["n_pairs"].sum())
    nh, nn = int(rows["n_human"].sum()), int(rows["n_nudge"].sum())
    pJ = 0.75 if npairs > 20000 else (0.6 if npairs > 5000 else 0.4)
    pF = 0.65 if regime == "III" else (0.45 if regime == "II" else 0.35)
    body = header(f"G{g:02d}", title, span, "replication")
    body += (f"**Period:** regime {regime} · units {units} · {npairs:,} (peer message, recipient) pairs · "
             f"{nh} human messages, {nn} nudges (non-holdout).\n\n")
    body += ("## Why this period\nReplication layer: the common H50 estimator on every eligible non-holdout unit, so the "
             "period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).\n\n")
    body += (f"## Prediction\n*Written {STAMP}, before running on this period. Templated from the card (P2, P5, P6).*\n"
             f"- Peer read-out jump J₁ (talk) > 0 at 95% [{pJ:.2f}]; onset at hop 1 (no response at the in-flight call).\n"
             f"- Activity field excess (full window) > 0.10 [{pF:.2f}]"
             + (", ≥ 0.30 expected from the day edges (H38)" if regime == "III" else ", ≤ 0.20 expected in regime I") + ".\n"
             f"- Talk coupling share f_C (CF) larger than the talk field excess [{0.6 if regime == 'III' else 0.5:.2f}].\n"
             f"- {RULE}\n\n")
    body += "## Result\n(pending)\n\n## Scorecard (period-specific axes)\n(pending)\n\n## Notes\n"
    return body


NATIVE_TEXT = {
    "NE43": dict(
        title="#51 lever switch-offs: bookends off after 08-04, nudges off after 08-20",
        period="2026-07-29 → 2026-09-04, non-holdout; segments A 07-29..08-04, B 08-05..08-20, C 08-21..09-04",
        why=("The `automated` speaker carries two inputs that switch off at different dates (found in the H50 scheme "
             "build): the daily pause/resume bookends (last on 08-04) and the nudges (last on 08-20). The scaffold's daily "
             "start and stop continue. So the input paths can be removed one at a time while the peer channel stays: an "
             "intervention on the transfer function (axis E). Confounds: the #focus room split starts 08-05 (A vs B); the "
             "rooms merge back on 08-24 (inside C); roster joins 08-28, 09-01, 09-03, 09-04."),
        pred=("- (i) The nudge path is present in B (nudge→target gate in talk or act, onset hop ≥ 2) and absent in C; its "
              "share of activity co-movement in B is small: Δf_F(nudge classes) < 0.05 (nudges hit one agent at a time).\n"
              "- (ii) Scaffold, not message: the day-start step response is unchanged when the bookend messages stop (A vs B): "
              "dispersion of agents' first calls of the day changes by < 50%, and the activity edge kernel G30 keeps its sign "
              "and stays within its A-segment CI.\n"
              "- (iii) The peer read-out jump J₁ (talk) in C lies within the B 95% CI or within ±50% of B.\n"
              "- (iv) Edge-trimmed activity per-pair co-movement ρ̄ (trim variant) in C within ±25% of B.\n"
              "- *Against:* ρ̄ falls by > 25% from B to C (the nudger carried co-movement), or J₁ collapses in C, or the "
              "edge step disappears with the bookends (agents started by the message)."),
        role="native"),
    "G51": dict(
        title="Private roles; the human-input test (#51a–l)",
        period="2026-07-06 → 2026-09-04 (non-holdout units 51a–51l)",
        why=("The most human messages of regime III (113 non-holdout; 69 name agents), a named target and many room "
             "bystanders: the place to tell a field (everyone moved at their own read-out call) from a relay (bystanders "
             "moved only after the target's visible reply). Also the replication estimator on its 12 units."),
        pred=("- Human message naming agents → target talk: read-out jump J₁ > 0 at 95% (onset hop 1).\n"
              "- Same messages → bystanders (in the room, not named): J₁ smaller than the target's (ratio < 0.5).\n"
              "- Relay: the target's reply, used as the source event for the bystanders, gives a read-out jump J₁ > 0, at "
              "least as large as the generic peer-message jump in #51 (the reply to a human is a salient peer message).\n"
              "- Plain human messages (no name) → recipients: J₁ > 0 (a field read at hop 1), with no target/bystander split.\n"
              "- Replication rule (card) on the pooled units: expected *supported*.\n"
              "- *Against:* bystander jump ≥ target jump, or no relay jump at the target's reply."),
        role="native"),
    "NE14": dict(
        title="Regime I (sessions, chat mode) vs regime III (always-on computer use)",
        period="regime I units #2–#31 vs regime III units #36b–#51 (non-holdout); the boundary bundle NE14 lies between",
        why=("HH167's premise: regime-I waits are message-triggered, so co-movement there should be coupling; regime III "
             "follows inputs at once (field). DQ1 reports that regime-I chat-mode calls are scheduled (median cadence 74 s; "
             "45% with no new message), which contradicts the premise. Exception (c) of the unit rule: the comparison of "
             "the two sides of a boundary is the object; each unit stays a separate estimate."),
        pred=("- P-R1 (premise check): after a room message arrives while the recipient is idle (in-flight call is a wait "
              "or pause), the share of next calls that start within 30 s is ≤ 1.2× the placebo share in regime I (scheduled "
              "chat calls) and in regime III (timer pauses). If > 1.5× in regime I, the premise holds.\n"
              "- P-R2: activity field excess (full window) higher in regime III than regime I (difference of unit medians "
              "≥ 0.15).\n"
              "- P-R3: talk read-out jump J₁ > 0 in both regimes (≥ 60% of units each); κ (talk) higher in regime I.\n"
              "- *Against HH167 as posed:* P-R1 fails (calls not message-triggered) or P-R3's κ ordering reverses."),
        role="native"),
    "G38": dict(
        title="Rooms with different instructions; the pause gates (#38a–e)",
        period="2026-04-02 → 2026-04-24 (units 38a–38e, 17 days)",
        why=("17 daily bookends at fixed clock times (resume 16:59:30 UTC, pause ≈ 21:00:02) in two rooms: a square-wave "
             "input. The resume arrives ≈ 1.5 min before the scaffold starts agents and the pause ≈ 1–6 min before it "
             "stops them, so it separates a scaffold field (start/stop by the platform) from a read-out response to the "
             "message and from a peer cascade. Also the replication estimator on its 5 units."),
        pred=("- (i) Resume: ≥ 80% of agents make their first call of the day before the first peer message of the day "
              "reaches their room (onsets cannot be peer-driven; zero relative lag).\n"
              "- (ii) Pause: agents read the pause message at hop 1; the number of calls after its read-out is small and set "
              "by the scaffold's stop time: Spearman ρ between peer messages read after the pause read-out and calls made "
              "after it is ≤ 0.2 (no goodbye cascade keeps agents going), and last-call times are tightly clustered "
              "(IQR across agents ≤ 2 min).\n"
              "- (iii) Talk at the pause read-out call is elevated over placebo (J₁ at the pause message > 0; low power, "
              "17 events).\n"
              "- Replication rule (card) on the pooled units: expected *supported*."),
        role="native"),
}


def native(name, rows=None):
    d = NATIVE_TEXT[name]
    body = header(name, d["title"], d["period"], d["role"])
    if rows is not None and len(rows):
        units = ", ".join(f"{u} ({dd} d, N={n})" for u, dd, n in zip(rows["unit"], rows["n_days"], rows["N"]))
        body += f"**Period:** regime {rows['regime'][0]} · units {units}.\n\n"
    else:
        body += f"**Period:** {d['period']}.\n\n"
    body += f"## Why this period\n{d['why']}\n\n## Prediction\n*Written {STAMP}, before running this test.*\n{d['pred']}\n\n"
    body += "## Result\n(pending)\n\n## Scorecard (period-specific axes)\n(pending)\n\n## Notes\n"
    return body


def main():
    u = pl.read_parquet(UNITS).filter(pl.col("eligible"))
    t = titles()
    pu = u.filter(pl.col("kind") == "period_unit")
    for g in sorted(pu["goal_no"].unique().to_list()):
        rows = pu.filter(pl.col("goal_no") == g).sort("first_day")
        name = f"G{g:02d}"
        d = H / "goalperiod-subhypotheses" / name
        (d / "figures").mkdir(parents=True, exist_ok=True)
        if (d / "README.md").exists():
            continue  # never overwrite a written prediction
        if name in NATIVE:
            text = native(name, rows)
        else:
            text = replication(g, rows, t.get(g, f"goal {g}"))
        (d / "README.md").write_text(text)
    for name in ("NE14", "NE43"):
        d = H / "goalperiod-subhypotheses" / name
        (d / "figures").mkdir(parents=True, exist_ok=True)
        if not (d / "README.md").exists():
            (d / "README.md").write_text(native(name))
    print("period folders written")


if __name__ == "__main__":
    main()
