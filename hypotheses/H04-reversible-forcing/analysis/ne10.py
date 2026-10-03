"""H04 exploratory check of NE10 (auto-nudger switched on 2026-02-10), P9 on the card.

Pre = non-holdout days 2026-01-12 .. 02-09 (#27 and #30 day 1; #28-#29 are held out and dropped);
post = 02-10 .. 02-20 (#30, #31). Agents present in both periods. Day-bootstrap CIs (periods resampled separately).
Hawkes n per period comes from hawkes_explore.py (suites NE10_pre / NE10_post).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h04lib import *  # noqa: E402,F403

PRE = ("2026-01-12", "2026-02-10")
POST = ("2026-02-10", "2026-02-21")
B = 2000


def day_metrics(d: Day, agents: set[int]) -> dict:
    rows = [i for i, a in enumerate(d.agents) if int(a) in agents]
    st = d.state[rows]
    n = st >= 3
    out = {"min": st.size, "idle": int((st == 2).sum()), "active": int(n.sum()), "silent": int((st == 1).sum()),
           "exit10": 0, "expo10": 0, "runs": 0, "run_len": 0, "exit30": 0, "expo30": 0}
    for r in n:
        # inactive runs (n = 0); a run ends with an exit if followed by an active minute inside the day
        x = np.concatenate([[1], r.astype(int), [1]])
        starts = np.nonzero((x[1:-1] == 0) & (x[:-2] == 1))[0]
        ends = np.nonzero((x[1:-1] == 0) & (x[2:] == 1))[0]
        for s0, e0 in zip(starts, ends):
            L = e0 - s0 + 1
            exited = e0 + 1 < len(r)
            out["runs"] += 1; out["run_len"] += L
            for thr, ke, kx in ((10, "exit10", "expo10"), (30, "exit30", "expo30")):
                if L > thr:
                    out[kx] += L - thr
                    out[ke] += int(exited)
    return out


def boot(pre: list[dict], post: list[dict], f, rng) -> list:
    def agg(ds):
        return {k: sum(d[k] for d in ds) for k in ds[0]}
    pt = f(agg(post)) / f(agg(pre)) - 1
    bs = []
    for _ in range(B):
        a = [pre[i] for i in rng.integers(0, len(pre), len(pre))]
        b = [post[i] for i in rng.integers(0, len(post), len(post))]
        bs.append(f(agg(b)) / f(agg(a)) - 1)
    return [float(pt), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
            float(f(agg(pre))), float(f(agg(post)))]


def analyse(dpre, dpost):
    Dpre, Dpost = load_days(dpre), load_days(dpost)
    common = set(int(a) for d in Dpre for a in d.agents) & set(int(a) for d in Dpost for a in d.agents)
    mpre = [day_metrics(d, common) for d in Dpre]
    mpost = [day_metrics(d, common) for d in Dpost]
    rng = np.random.default_rng(RNG_SEED)
    msgs = load_messages(dpre + dpost)
    nud = msgs.filter(pl.col("kind") == "nudge").group_by("pt_date").len().sort("pt_date")
    out = {"pre_days": dpre, "post_days": dpost, "common_agents": sorted(common),
           "nudges_per_day": dict(nud.iter_rows()),
           "idle_fraction_rel_change": boot(mpre, mpost, lambda a: a["idle"] / a["min"], rng),
           "active_fraction_rel_change": boot(mpre, mpost, lambda a: a["active"] / a["min"], rng),
           "silent_fraction_rel_change": boot(mpre, mpost, lambda a: a["silent"] / a["min"], rng),
           "escape_hazard_after10_rel_change": boot(mpre, mpost, lambda a: a["exit10"] / max(1, a["expo10"]), rng),
           "escape_hazard_after30_rel_change": boot(mpre, mpost, lambda a: a["exit30"] / max(1, a["expo30"]), rng),
           "mean_inactive_run_rel_change": boot(mpre, mpost, lambda a: a["run_len"] / max(1, a["runs"]), rng),
           "format": "[rel. change point, 2.5%, 97.5%, pre value, post value]"}
    return out


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    cal = calendar()
    out = analyse(select_days(cal, date_from=PRE[0], date_to=PRE[1]), select_days(cal, date_from=POST[0], date_to=POST[1]))
    # labelled variant (after seeing the data): the first nudges appear on 02-13, so 02-10..02-12 are nudge-free
    out["onset_0213"] = analyse(select_days(cal, date_from=PRE[0], date_to="2026-02-13"),
                                select_days(cal, date_from="2026-02-13", date_to=POST[1]))
    hk = OUT / "explore_hawkes.json"
    if hk.exists():
        h = json.loads(hk.read_text())
        out["hawkes_n"] = {k: h[k].get("n_ci", h[k]["fit"]["n"]) for k in ("NE10_pre", "NE10_post") if k in h}
    jdump(out, OUT / "explore_ne10.json")
    write_provenance("explore_ne10.json", "hypotheses/H04-reversible-forcing/analysis/ne10.py",
                     ["calendar", "activity_bins", "chat_core", "exposure", "roster"],
                     {"pre": PRE, "post": POST, "boot": B, "holdout": "excluded (#28, #29 dropped)"})
    for k, v in out.items():
        if k not in ("pre_days", "post_days"):
            print(k, v)
