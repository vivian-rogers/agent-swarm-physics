"""Fill the native-test results (NE43, G51, NE14, G38) with verdicts and figures."""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / "hypotheses/H50-field-vs-coupling-transfer-lag"
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
BLUE, ORANGE, AQUA, GRAY, INK, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b", "#4a3aa7"


def f(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{d}f}"


def ci(v, d=3):
    return f"{f(v[0], d)} [{f(v[1], d)}, {f(v[2], d)}]"


def style(ax):
    ax.tick_params(labelsize=6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def put(name, verdict, native_md, score_md=None):
    p = H / "goalperiod-subhypotheses" / name / "README.md"
    t = p.read_text()
    t = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict}", t, count=1)
    if "### Native test\n" in t:
        t = re.sub(r"### Native test\n.*?\n## Scorecard", "### Native test\n" + native_md + "\n## Scorecard", t, flags=re.S)
    else:
        t = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + native_md + "\n## Scorecard", t, flags=re.S)
    if score_md:
        t = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" + score_md + "\n## Notes", t, flags=re.S)
    p.write_text(t)


def ne43():
    n = json.loads((OUT / "NE43" / "native.json").read_text())
    A, B, C, ck = n["NE43A"], n["NE43B"], n["NE43C"], n["checks"]
    # figure
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.2))
    segs = ["A\nbookends+nudges", "B\nnudges only", "C\nneither"]
    x = np.arange(3)
    J = np.array([s["J1_talk"] for s in (A, B, C)])
    axes[0].errorbar(x, J[:, 0], yerr=[J[:, 0] - J[:, 1], J[:, 2] - J[:, 0]], fmt="o", color=ORANGE, ms=4, capsize=0)
    axes[0].set_title("peer read-out jump $J_1$ (talk)", fontsize=7)
    axes[0].set_ylim(0, None)
    axes[1].plot(x, [s["rho_trim"] for s in (A, B, C)], "o-", color=INK, ms=4, label="trim")
    axes[1].plot(x, [s["rho_span"] for s in (A, B, C)], "s--", color=GRAY, ms=3, label="span")
    axes[1].plot(x, [s["rho_full"] for s in (A, B, C)], "^:", color=BLUE, ms=3, label="full")
    axes[1].set_title("activity per-pair co-movement $\\bar\\rho$", fontsize=7)
    axes[1].legend(fontsize=5.5, frameon=False)
    E = np.array([[s["edge_G30_A"], s["edge_G30_A_ci"][0], s["edge_G30_A_ci"][1]] for s in (A, B, C)], float)
    axes[2].errorbar(x, E[:, 0], yerr=[E[:, 0] - E[:, 1], E[:, 2] - E[:, 0]], fmt="o", color=INK, ms=4, capsize=0)
    ax2 = axes[2].twinx()
    ax2.plot(x, [s["onset_iqr_s_median"] for s in (A, B, C)], "s", color=AQUA, ms=4)
    ax2.set_ylabel("onset IQR (s)", fontsize=6, color=AQUA)
    ax2.tick_params(labelsize=6)
    ax2.set_ylim(0, 40)
    axes[2].set_title("day-start step: FIR G30 (black), onset IQR (aqua)", fontsize=6.5)
    for a in axes:
        a.set_xticks(x)
        a.set_xticklabels(segs, fontsize=5.5)
        style(a)
    fig.tight_layout()
    (H / "goalperiod-subhypotheses/NE43/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(H / "goalperiod-subhypotheses/NE43/figures/NE43_switchoffs.pdf")
    plt.close(fig)
    nt = B["nudge_target"]
    md = (f"Data: `data/processed/H50-field-vs-coupling-transfer-lag/NE43/` (`NE43A/B/C.json`, `native.json`). Figure: "
          f"[`figures/NE43_switchoffs.pdf`](figures/NE43_switchoffs.pdf). Segments: A = {A['days']} days, N = {A['N']}; B = {B['days']} days, "
          f"N = {B['N']}; C = {C['days']} days, N = {C['N']}.\n\n"
          "| prediction | observed | verdict |\n| --- | --- | --- |\n"
          f"| (i) nudge path present in B, gone in C | nudge → target, talk J₁ = {f(nt['J_talk'][0])} [CI lo {f(nt['J_talk_lo'][0])}], onset hop {nt['onset_talk']}; "
          f"C has no nudges | yes |\n"
          f"| (i) nudge share of activity co-movement in B < 0.05 | Δf_F(nudge classes): span {f(ck['i_nudge_share_span'], 3)}, trim {f(ck['i_nudge_share_trim'], 3)}, "
          f"talk {f(ck['i_nudge_share_talk'], 3)} | partly (span, talk yes; trim no) |\n"
          f"| (ii) day-start step unchanged when the bookends stop (A → B) | first-call onset IQR {f(A['onset_iqr_s_median'], 1)} s → {f(B['onset_iqr_s_median'], 1)} s "
          f"(ratio {f(ck['ii_onset_iqr_ratio_B_over_A'], 2)}; {f(A['onset_iqr_cc'], 1)} → {f(B['onset_iqr_cc'], 1)} call cycles); activity edge G30 "
          f"{ci([A['edge_G30_A']] + A['edge_G30_A_ci'], 2)} → {ci([B['edge_G30_A']] + B['edge_G30_A_ci'], 2)} → C {ci([C['edge_G30_A']] + C['edge_G30_A_ci'], 2)} | yes |\n"
          f"| (iii) peer J₁ in C within B's CI or ±50% | B {ci(B['J1_talk'])}, C {ci(C['J1_talk'])}; ratio {f(ck['iii_J1_C_over_B'], 2)} | yes (±50%) |\n"
          f"| (iv) edge-trimmed activity ρ̄ in C within ±25% of B | trim {f(B['rho_trim'], 4)} → {f(C['rho_trim'], 4)} (ratio {f(ck['iv_rho_trim_C_over_B'], 2)}); "
          f"span {f(B['rho_span'], 4)} → {f(C['rho_span'], 4)}; full {f(B['rho_full'], 4)} → {f(C['rho_full'], 4)} | no on the locked variant (rose 41% from a near-zero base); span and full within ±10% |\n\n"
          f"**Reading.** The nudger is a targeted field: a nudged agent talks more at the call that reads the nudge (hop 1), but nudges move one agent at a time and carry "
          f"at most a few percent of activity co-movement, so switching them off leaves co-movement where it was (it did not fall; the trim variant even rose from "
          f"a near-zero base). The daily bookend messages are announcements, not inputs: when they stop (A → B) agents still start within about 22 s of each other "
          f"(1.6–1.9 call cycles) and the day-start step response keeps its size. The scaffold, not the message, starts agents. Peer coupling persists without either "
          f"lever (C's jump is 0.69 × B's, inside ±50%). Against: Δf_F(nudge) on the trim variant is 0.08, above the 0.05 bound, and the trim ρ̄ bound is missed in the "
          f"direction opposite to the 'against' clause. Confounds: #focus split on 08-05 (A vs B), merge on 08-24 and roster joins in C. A's J₁ is lower (0.009) than B's (0.019).\n")
    score = ("- **E (interventional):** two input switch-offs inside one period. The model's predictions (nudge path vanishes, coupling persists, schedule field "
             "persists without its message) hold qualitatively; two numeric bounds missed on the trim variant.\n"
             "- **G (ground truth):** the bookend stop date (08-04) and nudge stop date (08-20) are read off the data; the scaffold keeps starting agents at "
             "16:01 UTC every day.")
    put("NE43", "mixed (core supported: the nudge path is gone after 08-20, peer coupling and the day-start field persist; two locked numeric bounds missed on the trim variant)", md, score)
    return dict(verdict="mixed")


def g51():
    n = json.loads((OUT / "G51" / "native.json").read_text())

    def j(k):
        return [n[k]["jumps"][0], n[k]["j_lo"][0], n[k]["j_hi"][0]]
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    labs = [("target", "named target"), ("bystander", "bystanders\n(named msg)"), ("plain", "recipients\n(plain msg)"),
            ("reply_by", "bystanders at\ntarget's reply"), ("peer", "any peer\nmessage")]
    for i, (k, lab) in enumerate(labs):
        v = j(k)
        ax.errorbar([i], [v[0]], yerr=[[v[0] - v[1]], [v[2] - v[0]]], fmt="o", color=[BLUE, AQUA, ORANGE, VIOLET, GRAY][i], ms=4, capsize=0)
    ax.axhline(0, color=GRAY, lw=0.6)
    ax.set_xticks(range(len(labs)))
    ax.set_xticklabels([l for _, l in labs], fontsize=5)
    ax.set_ylabel("read-out jump $J_1$ (talk)", fontsize=6.5)
    style(ax)
    fig.tight_layout()
    fig.savefig(H / "goalperiod-subhypotheses/G51/figures/G51_human_relay.pdf")
    plt.close(fig)
    md = (f"Data: `data/processed/H50-field-vs-coupling-transfer-lag/G51/native.json`. Figure: [`figures/G51_human_relay.pdf`](figures/G51_human_relay.pdf). "
          f"Pooled over the 12 non-holdout units (day stats concatenated, day bootstrap). Messages: {n['messages']['mention']} naming agents "
          f"({n['messages']['replied']} answered by a target within 30 min; reply latency median {f(n['reply_latency_s']['q50'], 0)} s, IQR "
          f"{f(n['reply_latency_s']['q25'], 0)}–{f(n['reply_latency_s']['q75'], 0)} s), {n['messages']['plain']} plain. Pairs: target {n['counts']['target']}, "
          f"bystander {n['counts']['bystander']}, plain {n['counts']['plain']}, reply→bystander {n['counts']['reply_by']}.\n\n"
          "| prediction | observed J₁ (talk) [95% CI] | verdict |\n| --- | --- | --- |\n"
          f"| named target jumps at hop 1 | {ci(j('target'))} (only {int(n['target']['n_rows'])} calls near the read-out boundary) | no (underpowered) |\n"
          f"| bystanders < 0.5 × target | {ci(j('bystander'))}; ratio {f(n['ratio_bystander_target'], 2)} | no |\n"
          f"| relay: jump at the target's reply ≥ generic peer jump | reply {ci(j('reply_by'))} vs peer {ci(j('peer'))} | no (point estimate 2×, CI includes 0) |\n"
          f"| plain human messages: jump at hop 1 (field) | {ci(j('plain'))} | yes |\n\n"
          "**Reading.** Plain human messages act as a field read at hop 1: recipients' next call is about 0.19 more likely to be a talk call than the in-flight one. "
          "The target/relay design is too thin to read: named targets are rarely mid-loop when the message lands (119 calls near the boundary), and the "
          "reply-relay jump is twice the generic peer jump but not significant. Round 2: widen the window (3W), pool regime-I human-rich periods (#4–#6), "
          "or use the hop-2..4 kernel for bystanders.\n")
    put("G51", "mixed (replication supported; native: plain human messages are a hop-1 field, the target/relay tests are underpowered)", md)
    return dict(verdict="mixed")


def ne14():
    n = json.loads((OUT / "NE14" / "native.json").read_text())
    P, S = n["pooled"], n["summary"]
    df = pl.DataFrame(n["per_unit"])
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.3))
    keys = [("I_chat", "I chat-mode"), ("I_wait", "I wait"), ("I_busy_gap", "I busy gap"), ("II_chat", "II chat"), ("III_pause", "III pause"),
            ("III_busy_gap", "III busy gap")]
    for i, (k, lab) in enumerate(keys):
        if k in P:
            v = P[k]
            axes[0].errorbar([i], [v["ratio"]], yerr=[[v["ratio"] - v["lo"]], [v["hi"] - v["ratio"]]], fmt="o", ms=4, capsize=0,
                             color=BLUE if k.startswith("I_") else (VIOLET if k.startswith("II") else ORANGE))
    axes[0].axhline(1, color=GRAY, lw=0.6)
    axes[0].axhline(1.5, color=GRAY, lw=0.6, ls=":")
    axes[0].set_xticks(range(len(keys)))
    axes[0].set_xticklabels([l for _, l in keys], fontsize=5, rotation=45, ha="right")
    axes[0].set_ylabel("next call within 30 s:\nobserved / uniform arrival", fontsize=6)
    axes[0].set_title("are calls message-triggered?", fontsize=7)
    for j, (col, lab) in enumerate((("fFex_A_full", "activity field excess"), ("J1", "peer jump $J_1$ (talk)"))):
        ax = axes[1 + j]
        for k, reg in enumerate(("I", "II", "III")):
            v = df.filter(pl.col("regime") == reg)[col].drop_nulls().to_numpy()
            ax.scatter(np.full(len(v), k) + np.random.default_rng(k).uniform(-0.15, 0.15, len(v)), v, s=6,
                       color=[BLUE, VIOLET, ORANGE][k], alpha=0.7, lw=0)
            if len(v):
                ax.plot([k - 0.25, k + 0.25], [np.median(v)] * 2, color=INK, lw=1.2)
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(["I", "II", "III"], fontsize=6)
        ax.set_title(lab, fontsize=7)
        ax.axhline(0, color=GRAY, lw=0.6)
    for a in axes:
        style(a)
    fig.tight_layout()
    fig.savefig(H / "goalperiod-subhypotheses/NE14/figures/NE14_regimes.pdf")
    plt.close(fig)
    t = S["tests"]
    md = (f"Data: `data/processed/H50-field-vs-coupling-transfer-lag/NE14/native.json`. Figure: [`figures/NE14_regimes.pdf`](figures/NE14_regimes.pdf). "
          f"Units: regime I {S['I']['n_units']}, II {S['II']['n_units']}, III {S['III']['n_units']} (each unit its own estimate; regime summaries are medians).\n\n"
          "| prediction | observed | verdict |\n| --- | --- | --- |\n"
          f"| P-R1: regime-I calls not message-triggered (ratio ≤ 1.2) | chat-mode {ci([P['I_chat']['ratio'], P['I_chat']['lo'], P['I_chat']['hi']], 3)}, "
          f"wait {ci([P['I_wait']['ratio'], P['I_wait']['lo'], P['I_wait']['hi']], 3)} (n = {P['I_wait']['n']:,}); regime-III pauses "
          f"{ci([P['III_pause']['ratio'], P['III_pause']['lo'], P['III_pause']['hi']], 3)} | yes: HH167's premise fails |\n"
          f"| P-R2: activity field excess III − I ≥ 0.15 | medians I {f(S['I']['fFex_A_full_median'], 2)}, III {f(S['III']['fFex_A_full_median'], 2)}; "
          f"difference {f(t['fFex_III_minus_I'], 2)} (Mann–Whitney p {f(t['fFex_MW_p'], 2)}) | no |\n"
          f"| P-R3: talk J₁ > 0 in ≥ 60% of units in both regimes | I {S['I']['J1_pos']}/{S['I']['n_units']}, III {S['III']['J1_pos']}/{S['III']['n_units']}; "
          f"no unit < 0 | yes |\n"
          f"| P-R3: κ (talk) higher in regime I | medians I {f(S['I']['kappa_median'], 2)}, III {f(S['III']['kappa_median'], 2)} (p {f(t['kappa_MW_p'], 2)}) | no |\n\n"
          "**Reading.** HH167's regime split does not hold. Regime-I calls are not message-triggered: a message arriving while an agent waits shortens the wait "
          "by a few percent at most (DQ1: chat-mode calls are scheduled). Both regimes look the same in kind: activity co-movement is a schedule field (field "
          "excess ≈ 0.5 in both), and talk carries a gated coupling with a step at hop 1. What differs is the shape of the coupling. Regime III's response decays "
          "at hop 2 (J₂ < 0 in 8/27 units), and regime I's keeps rising (J₂ > 0 in 13/41, kernel at hop 6 > 0 in 22/41). Regime-I coupling is also larger per "
          "message (pooled J₁ 0.034 vs 0.019), but smaller relative to the base talk rate (+25% vs +44%).\n")
    put("NE14", "mixed (HH167's premise and regime split rejected; gated talk coupling present in both regimes)", md)
    return dict(verdict="mixed")


def g38():
    n = json.loads((OUT / "G38" / "native.json").read_text())
    r, p = n["resume"], n["pause"]
    stp = pl.read_parquet(OUT / "G38" / "pause_stops.parquet")
    fig, ax = plt.subplots(figsize=(3.4, 2.1))
    v = stp["last_end_off_s"].to_numpy()
    ax.hist(np.clip(v, -600, 300), bins=np.arange(-600, 310, 15), color=GRAY)
    ax.axvline(0, color=ORANGE, lw=1)
    ax.set_xlabel("agent's last call end − pause message (s)", fontsize=6.5)
    ax.set_ylabel("agent-days", fontsize=6.5)
    ax.set_title("#38: agents stop at the pause message", fontsize=7)
    style(ax)
    fig.tight_layout()
    fig.savefig(H / "goalperiod-subhypotheses/G38/figures/G38_pause_stops.pdf")
    plt.close(fig)
    q = p["last_end_off_q"]
    md = (f"Data: `data/processed/H50-field-vs-coupling-transfer-lag/G38/native.json`, `pause_stops.parquet`. Figure: "
          f"[`figures/G38_pause_stops.pdf`](figures/G38_pause_stops.pdf). 17 days, {r['n_agent_days']} agent-days.\n\n"
          "| prediction | observed | verdict |\n| --- | --- | --- |\n"
          f"| (i) ≥ 80% of agents start before the first peer message reaches them | {f(100 * r['share_first_before_peer'], 0)}%; first-call onsets have IQR "
          f"{f(r['onset_iqr_s_median'], 0)} s across agents (≈ 0.7 call cycles) | yes |\n"
          f"| (ii) stop set by the scaffold, not by reading goodbyes: few calls after read-out, ρ ≤ 0.2, last-call IQR ≤ 2 min | only {f(100 * p['share_read'], 0)}% of "
          f"agents make any call after the pause message (median {f(p['n_calls_after_median'], 0)}); last-call end relative to the message: quantiles 10/25/50/75/90% = "
          f"{', '.join(f(x, 0) for x in q)} s; per-day IQR {f(p['last_end_iqr_s_median'], 0)} s; ρ not computable (too few readers) | yes for the stop; the predicted "
          f"mechanism (read at hop 1, then stop) is wrong: agents are halted without reading it |\n"
          f"| (iii) talk at the pause read-out elevated | not testable (no read-out calls near the boundary) | n/a |\n\n"
          "**Reading.** Both gates are scaffold fields with zero relative lag. At the resume, agents start within seconds of each other (IQR ≈ 9 s, under one call "
          "cycle), and most start before any peer message exists, so there is no start-up cascade. At the pause, in-flight calls finish (90% of last calls end "
          "within 23 s after the message) and no new call starts. The message is posted as agents are halted, so it is an announcement, not an input they "
          "respond to. This is the mechanism behind H38's regime-III edge co-activation.\n")
    put("G38", "supported (replication supported; native: resume and pause are scaffold fields with zero relative lag; agents stop without reading the pause message)", md)
    return dict(verdict="supported")


def main():
    out = dict(NE43=ne43(), G51=g51(), NE14=ne14(), G38=g38())
    (OUT / "native_verdicts.json").write_text(json.dumps(out, indent=1))
    print(out)


if __name__ == "__main__":
    main()
