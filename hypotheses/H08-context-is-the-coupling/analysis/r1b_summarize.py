"""H08 round 1b: per-period old-vs-new table, verdicts (1b) by the round-1 rule, per-period estimates, summary figure.

  uv run python hypotheses/H08-context-is-the-coupling/analysis/r1b_summarize.py [--write-estimates]

Reads round-1 G<NN>/c9.json, c3.json and round-1b r1b/G<NN>/c9.json, c3.json, r1b/ne41_pooled.json, r1b/NE32*.json.
Verdict rule (fixed in each G card before round 1, applied unchanged): supported = C9's talk and addressing
discontinuities both pass (CI excluding 0) and no other applicable test fails (C3 where >= 300 forced-erased units:
beta_F CI excludes 0 or is negative in sign; C8 only for #51); failed = the C9 test fails; mixed = C9 passes but another
test fails. Round 1b reads C9 on the ledger with the mention response (as pre-registered); the reply-author and content
responses are reported next to it.
Writes r1b/summary_r1b.json and figures/r1b_c9.pdf.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403

OUT1B = OUT / "r1b"
GS = sorted(PERIODS) + [10]


def load(p):
    return json.loads(p.read_text()) if p.exists() else None


def D(c9, kind, sub="primary"):
    try:
        return c9[sub][kind]["D"]
    except (KeyError, TypeError):
        return None


def passes(d):
    return d is not None and d[1] is not None and d[1] > 0


def fmt(d, scale=100):
    if not d or d[0] is None:
        return "—"
    return f"{d[0] * scale:+.2f} [{d[1] * scale:+.2f}, {d[2] * scale:+.2f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-estimates", action="store_true")
    a = ap.parse_args()
    rows = []
    for g in GS:
        gp = gname(g)
        o9, n9 = load(OUT / gp / "c9.json"), load(OUT1B / gp / "c9.json")
        o3, n3 = load(OUT / gp / "c3.json"), load(OUT1B / gp / "c3.json")
        if n9 is None:
            continue
        r = {"period": gp, "regime": (PERIODS.get(g) or {}).get("regime", "I"),
             "old": {"D_talk": D(o9, "talk"), "D_addr": D(o9, "addr"), "D_addr_clean": D(o9, "addr", "posthoc_clean")} if o9 else None,
             "new": {"D_talk": D(n9, "talk"), "D_addr": D(n9, "addr"), "D_auth": D(n9, "auth"),
                     "D_cos": (n9.get("primary", {}).get("cos") or {}).get("D"), "D_addr_clean": D(n9, "addr", "posthoc_clean"),
                     "D_addr_other": D(n9, "addr", "other_room"), "W_active_s": n9.get("W_active_s"),
                     "Wc_active_s": n9.get("Wc_active_s"), "share_inflight": n9.get("share_inflight"),
                     "n_pairs": n9.get("n_pairs_own")}}
        c3_old = (o3 or {}).get("beta", {}).get("erased_F")
        nF = (n3 or {}).get("n_erased", {}).get("CF", 0)
        c3_new = (n3 or {}).get("men", {}).get("beta", {}).get("erased_F")
        c3_new_auth = (n3 or {}).get("auth", {}).get("beta", {}).get("erased_F")
        r["c3"] = {"old": c3_old, "new_men": c3_new, "new_auth": c3_new_auth, "n_forced": nF}
        c9ok = passes(r["new"]["D_talk"]) and passes(r["new"]["D_addr"])
        c3fail = nF >= 300 and c3_new is not None and c3_new[0] > 0 and c3_new[1] > 0
        r["verdict_1b"] = "failed" if not c9ok else ("mixed" if c3fail else "supported")
        r["verdict_old"] = None
        card = GP / gp / "README.md"
        if card.exists():
            for line in card.read_text().splitlines()[:4]:
                if line.startswith("**Verdict:**"):
                    r["verdict_old"] = line.split("**Verdict:**")[1].strip()
        rows.append(r)
    ne41 = load(OUT1B / "ne41_pooled.json")
    ne32 = load(OUT1B / "NE32_mentions.json")
    summ = {"periods": rows, "ne41_pooled": (ne41 or {}).get("pooled"), "ne32": {k: (ne32 or {}).get(k) for k in ("N32a", "N32b", "N32c")}}
    jdump(summ, OUT1B / "summary_r1b.json")
    for r in rows:
        o = r["old"] or {}
        print(f"| {r['period']} | {r['regime']} | {fmt(o.get('D_talk'))} → {fmt(r['new']['D_talk'])} | {fmt(o.get('D_addr'))} → {fmt(r['new']['D_addr'])} | "
              f"{fmt(r['new']['D_auth'])} | {fmt(r['new']['D_cos'])} | {fmt(o.get('D_addr_clean'))} → {fmt(r['new']['D_addr_clean'])} | "
              f"{r['verdict_old']} → {r['verdict_1b']} |")
    # figure: D_addr old vs new and D_cos per period
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    xs = np.arange(len(rows))
    for j, (key, lab, col) in enumerate((("D_addr", "addressing (mention)", "#1f77b4"), ("D_auth", "reply author", "#2ca02c"))):
        v = [r["new"][key] for r in rows]
        axs[0].errorbar(xs + 0.15 * j, [x[0] * 100 if x else np.nan for x in v],
                        yerr=[[ (x[0] - x[1]) * 100 if x else 0 for x in v], [(x[2] - x[0]) * 100 if x else 0 for x in v]],
                        fmt="o", ms=3, color=col, label=f"{lab}, ledger", lw=0.8)
    vo = [(r["old"] or {}).get("D_addr") for r in rows]
    axs[0].plot(xs - 0.15, [x[0] * 100 if x else np.nan for x in vo], "x", color="gray", ms=4, label="addressing, round 1 rule")
    axs[0].axhline(0, color="k", lw=0.5)
    axs[0].set_xticks(xs); axs[0].set_xticklabels([r["period"] for r in rows], rotation=90, fontsize=7)
    axs[0].set_ylabel("jump at read-out D (pp)"); axs[0].legend(fontsize=6, frameon=False)
    v = [r["new"]["D_cos"] for r in rows]
    axs[1].errorbar(xs, [x[0] if x else np.nan for x in v], yerr=[[(x[0] - x[1]) if x else 0 for x in v], [(x[2] - x[0]) if x else 0 for x in v]],
                    fmt="o", ms=3, color="#d62728", lw=0.8)
    axs[1].axhline(0, color="k", lw=0.5)
    axs[1].set_xticks(xs); axs[1].set_xticklabels([r["period"] for r in rows], rotation=90, fontsize=7)
    axs[1].set_ylabel("content jump D_cos (cosine)")
    axs[1].set_title("non-mention response: similarity of the talk to the message", fontsize=8)
    axs[0].set_title("read-out discontinuity on the context ledger", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "r1b_c9.pdf")
    plt.close(fig)
    if a.write_estimates:
        sys.path.insert(0, str(ROOT / "infra/shared"))
        import estimates as E
        est = []
        for r in rows:
            g = int(r["period"][1:])
            for key, ch, meth in (("D_addr", "addressing (mention)", "C9 read-out jump G(1)-G(0) on ledger calls, in-flight units, pseudo-message null; day bootstrap"),
                                  ("D_talk", "talk", "C9 read-out jump G(1)-G(0) on ledger calls, in-flight units, pseudo-message null; day bootstrap"),
                                  ("D_auth", "reply author", "C9 read-out jump G(1)-G(0) on ledger calls (DQ2 reply-parent author), in-flight units; day bootstrap"),
                                  ("D_cos", "content cosine", "C9 read-out jump in bge cosine(talk, message) among talking calls, real minus pseudo; day bootstrap")):
                d = r["new"][key]
                if not d or d[0] is None:
                    continue
                est.append(dict(period_unit=E.map_unit(g), goal_no=g, statistic="c9_readout_jump", ci_kind="percentile", channel=ch, estimate=float(d[0]),
                                ci_lo=float(d[1]), ci_hi=float(d[2]), n=float(r["new"]["n_pairs"] or 0), n_kind="(message, recipient) pairs",
                                method=meth, null="pseudo-message (same pair, +-20-60 min)", role="native" if g == 10 else "replication",
                                source="data/processed/H08-context-is-the-coupling/r1b/G%02d/c9.json" % g, status="round 1b"))
            c = r["c3"]
            if c.get("new_auth"):
                est.append(dict(period_unit=E.map_unit(g), goal_no=g, statistic="ne41_beta_forced_erasure", ci_kind="percentile", channel="reply author",
                                estimate=float(c["new_auth"][0]), ci_lo=float(c["new_auth"][1]), ci_hi=float(c["new_auth"][2]),
                                n=float(c["n_forced"]), n_kind="forced-erased units",
                                method="LPM with agent x day effects, age bins, engaged, post-consolidation, new; ledger reset_forced; day bootstrap",
                                null="old in-context sender at the same age", role="native",
                                source="data/processed/H08-context-is-the-coupling/r1b/G%02d/c3.json" % g, status="round 1b"))
        E.write_estimates(est, hypothesis="H08")
        print(f"wrote {len(est)} estimates")


if __name__ == "__main__":
    main()
