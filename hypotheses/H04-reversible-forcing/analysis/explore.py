"""H04 exploratory round 1: Green's functions, linearity tests, FD ratios and kickoff step responses.

Non-holdout days only (asserted). Writes data/processed/H04-reversible-forcing/explore_*.json and
figures/*.pdf. Run: uv run python hypotheses/H04-reversible-forcing/analysis/explore.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h04lib import *  # noqa: E402,F403

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

B = 1000
G_SETS = ["nudge_target_iso", "nudge_target_strict", "nudge_target_all", "nudge_bystander_iso", "nudge_bystander_strict",
          "human_all_iso", "human_all_strict", "human_all_all", "human_mentioned_iso", "human_unmentioned_iso"]
FD_SETS = ["nudge_target_iso", "human_all_iso", "human_mentioned_iso"]


def suite_days(cal):
    base = dict(allow_holdout=False)
    return {
        "I": select_days(cal, regimes=["I"], **base),
        "II": select_days(cal, regimes=["II"], **base),
        "III": select_days(cal, regimes=["III"], **base),
        "III_4h": select_days(cal, regimes=["III"], hours=[4], **base),
        "III_8h": select_days(cal, regimes=["III"], hours=[8], **base),
    }


def run_suite(label: str, days: list[str], keep_rows: bool = False) -> dict:
    t0 = time.time()
    D = load_days(days)
    msgs = load_messages(days)
    resp = responder_rows(D, msgs)
    attach_hits(D, resp)
    n_codes = 64
    c = build_cells(D, np.arange(n_codes))
    ctl = control_means(c, n_codes)
    sets = build_sets(D, resp, c)
    W = boot_weights(len(D), B)
    nd = len(D)
    out = {"label": label, "n_days": nd, "date_range": [days[0], days[-1]],
           "n_messages": {k: int(v) for k, v in msgs.group_by("kind").len().iter_rows()},
           "n_cells": int(len(c.day)), "control_eligible_share": float(c.eligible.mean()),
           "set_sizes": {k: {"cells": int(len(v["ids"])), "kicks": v["n_kicks"]} for k, v in sets.items()}}
    R = {k: matched_response(c, ctl, v["ids"], nd, k, v["n_kicks"], v["nb_adjust"]) for k, v in sets.items()}
    Gb = {k: curves(r, W) for k, r in R.items()}
    out["G"] = {k: summarize(R[k], W) for k in G_SETS if k in R}

    # talk-only variant for the main sets
    ct = build_cells(D, np.arange(n_codes), var="talk")
    ctlt = control_means(ct, n_codes)
    out["G_talk"] = {}
    for k in ("nudge_target_iso", "human_all_iso", "human_mentioned_iso", "nudge_bystander_iso"):
        if k in sets:
            ids = ct.lookup(c.day[sets[k]["ids"]], c.row[sets[k]["ids"]], c.minute[sets[k]["ids"]])
            out["G_talk"][k] = summarize(matched_response(ct, ctlt, ids, nd, k, sets[k]["n_kicks"], sets[k]["nb_adjust"]), W)
            out["G_talk"][k].pop("G_lo", None); out["G_talk"][k].pop("G_hi", None)

    # ---------------- predictions P1-P3 helpers
    def a60(k):
        return amp(Gb[k], 1, 60) if k in Gb else None
    t = {}
    if "nudge_bystander_iso" in Gb and "nudge_target_iso" in Gb:
        with np.errstate(invalid="ignore", divide="ignore"):
            t["bystander_over_target_A60"] = ci(a60("nudge_bystander_iso") / a60("nudge_target_iso"))
    if "human_mentioned_iso" in Gb and "human_unmentioned_iso" in Gb:
        with np.errstate(invalid="ignore", divide="ignore"):
            t["mentioned_over_unmentioned_A60"] = ci(a60("human_mentioned_iso") / a60("human_unmentioned_iso"))
    out["contrasts"] = t

    # ---------------- linearity
    lin = {}
    A = lambda k, lo=1, hi=30: amp(Gb[k], lo, hi)
    # dose
    for kind in ("human", "nudge"):
        k1 = f"dose_{kind}_1"
        if k1 not in sets or len(sets[k1]["ids"]) == 0:
            continue
        for lab in ("2", "3to4", "5plus"):
            kn = f"dose_{kind}_{lab}"
            if kn not in sets or len(sets[kn]["ids"]) < 10:
                lin[f"dose_{kind}_{lab}"] = {"n_cells": int(len(sets.get(kn, {"ids": []})["ids"])), "verdict": "inconclusive (too few)"}
                continue
            nbar = float(np.mean(sets[kn]["dose"]))
            res = ratio_test(A(kn, 1, 30), nbar * A(k1, 1, 30))
            res.update({"n_cells": int(len(sets[kn]["ids"])), "mean_dose": nbar})
            lin[f"dose_{kind}_{lab}"] = res
    # superposition
    for kind, ref in (("human", "dose_human_1"), ("nudge", "nudge_target_iso")):
        kp = f"pair_{kind}"
        if kp not in sets or len(sets[kp]["ids"]) < 10 or ref not in Gb:
            lin[f"superposition_{kind}"] = {"n_cells": int(len(sets.get(kp, {"ids": []})["ids"])), "verdict": "inconclusive (too few)"}
            continue
        deltas = sets[kp]["delta"]
        G1 = Gb[ref]
        pred = np.zeros(len(W))
        for dlt in deltas:
            pred += A(ref, 1, 40) + np.nansum(G1[:, L0 + 1 - dlt:L0 + 41 - dlt], axis=1)
        pred /= len(deltas)
        res = ratio_test(A(kp, 1, 40), pred)
        res.update({"n_cells": int(len(deltas)), "median_delta": float(np.median(deltas))})
        lin[f"superposition_{kind}"] = res
    # time translation
    for g in ("nudge_target", "human_all", "human_mentioned"):
        for num, den in (("late", "early"), ("mid", "early"), ("mon", "midweek"), ("fri", "midweek")):
            kn, kd = f"{g}_iso_{num}", f"{g}_iso_{den}"
            if kn not in sets or kd not in sets or len(sets[kn]["ids"]) < 10 or len(sets[kd]["ids"]) < 10:
                lin[f"tt_{g}_{num}_over_{den}"] = {"verdict": "inconclusive (too few)",
                                                   "n": [int(len(sets.get(kn, {"ids": []})["ids"])), int(len(sets.get(kd, {"ids": []})["ids"]))]}
                continue
            res = ratio_test(A(kn), A(kd))
            res["n"] = [int(len(sets[kn]["ids"])), int(len(sets[kd]["ids"]))]
            lin[f"tt_{g}_{num}_over_{den}"] = res
    out["linearity"] = lin

    # ---------------- fluctuation vs response
    fd = {}
    for k in FD_SETS:
        if k not in sets or len(sets[k]["ids"]) < 30:
            fd[k] = {"note": "too few kicks"}
            continue
        ids = sets[k]["ids"]
        ag, cnt = np.unique(c.agent[ids], return_counts=True)
        C = autocorr(D, {int(a): float(n) for a, n in zip(ag, cnt)})
        e = ckp(R[k], W, C)
        e["shape"] = fdt_shape(R[k], W, C)
        e["onsager"] = onsager(c, ctl, ids, nd, W, nb_adjust=sets[k]["nb_adjust"])
        fd[k] = e
    out["fd"] = fd

    # ---------------- H04-MF (HH81): mean-field forward prediction of the kernel decay time
    mf = mean_field(D, W)
    tp = mf.pop("_tau_pred_rows")
    k_rows = mf.pop("_K_rows")
    x_rows = {k: e["onsager"].pop("_X30_rows", None) for k, e in fd.items() if isinstance(e, dict) and "onsager" in e}
    mf["kernels"] = {}
    for k in ("human_all_iso", "nudge_target_iso", "human_mentioned_iso"):
        if k not in Gb or len(sets[k]["ids"]) < 10:
            continue
        rel, wid = decay_rows(Gb[k])
        with np.errstate(invalid="ignore", divide="ignore"):
            mf["kernels"][k] = {"tau_G_relax": ci(rel), "tau_G_width": ci(wid), "ratio_relax": ci(rel / tp),
                                "ratio_width": ci(wid / tp), "n_cells": int(len(sets[k]["ids"]))}
    out["mf"] = mf
    if keep_rows:  # bootstrap rows (row 0 = point) for cross-segment ratios in the confirmatory script
        rows = {f"A30:{k}": amp(Gb[k], 1, 30) for k in ("nudge_target_iso", "human_all_iso", "human_mentioned_iso") if k in Gb}
        rows["tau_pred"] = tp
        rows["K"] = k_rows
        for k, v in x_rows.items():
            if v is not None:
                rows[f"X30:{k}"] = v
        for k in ("nudge_target_iso", "human_all_iso"):
            if k in Gb and len(sets[k]["ids"]) >= 10:
                rows[f"tauG_relax:{k}"] = decay_rows(Gb[k])[0]
        out["_rows"] = rows
    out["runtime_s"] = time.time() - t0
    print(f"[{label}] {nd} days, {len(c.day)} cells, {time.time() - t0:.1f}s", flush=True)
    return out


# ----------------------------------------------------------------------------- goal kickoffs (step response)

def kickoff_suite(label: str, days: list[str], W_B: int = B) -> dict:
    D = load_days(days)
    cal = calendar().filter(pl.col("pt_date").is_in(days)).sort("pt_date")
    first = cal.group_by("goal_no").agg(pl.col("pt_date").min().alias("d1"))
    # a goal's first active day counts as a kickoff day only if the goal started on/after the previous active day
    kicks = pl.read_parquet(S / "kicks.parquet").filter(pl.col("kind") == "goal_kickoff").with_columns(
        pl.col("ref").str.strip_chars("#").cast(pl.Int64).alias("goal_no"),
        pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("kick_date"))
    first = first.join(kicks.select(pl.col("goal_no").cast(pl.Int8), "kick_date"), on="goal_no", how="left")
    # require the kickoff to fall within 3 days before the first active day (else the goal began in the holdout)
    first = first.filter(pl.col("kick_date").is_not_null() & (pl.col("d1") >= pl.col("kick_date")))
    first = first.with_columns((pl.col("d1").str.to_date() - pl.col("kick_date").str.to_date()).dt.total_days().alias("lag_d"))
    first = first.filter(pl.col("lag_d") <= 3)
    kdays = set(first["d1"].to_list())
    # day index within goal
    gi = {}
    for g, grp in cal.group_by("goal_no"):
        for j, d in enumerate(sorted(grp["pt_date"].to_list())):
            gi[d] = j + 1
    prof = []
    for d in D:
        n = (d.state >= 3).mean(axis=0)
        prof.append({"pt_date": d.pt_date, "kick": d.pt_date in kdays, "weekday": d.weekday, "hours": d.hours,
                     "day_in_goal": gi.get(d.pt_date), "first60": float(n[:60].mean()), "m60_120": float(n[60:120].mean()) if len(n) > 60 else np.nan,
                     "after120": float(n[120:].mean()) if len(n) > 120 else np.nan, "whole": float(n.mean()),
                     "curve": np.pad(n[:240], (0, max(0, 240 - len(n[:240]))), constant_values=np.nan)})
    out = {"label": label, "n_kick_days": int(sum(p["kick"] for p in prof)), "n_days": len(prof)}
    rng = np.random.default_rng(RNG_SEED)
    for mode in ("same_hours", "same_hours_weekday"):
        res = {}
        for win in ("first60", "m60_120", "after120", "whole"):
            kv, cv = [], []
            for p in prof:
                if not p["kick"]:
                    continue
                ctrl = [q[win] for q in prof if not q["kick"] and q["hours"] == p["hours"] and np.isfinite(q[win])
                        and (mode == "same_hours" or q["weekday"] == p["weekday"])]
                if len(ctrl) >= 3 and np.isfinite(p[win]):
                    kv.append(p[win]); cv.append(ctrl)
            if len(kv) < 3:
                res[win] = {"n": len(kv), "rel_excess": None}
                continue
            kv = np.array(kv)
            cm = np.array([np.mean(x) for x in cv])
            pt = kv.mean() / cm.mean() - 1
            bs = []
            for _ in range(W_B):
                ii = rng.integers(0, len(kv), len(kv))
                cmb = np.array([np.mean(rng.choice(cv[i], len(cv[i]))) for i in ii])
                bs.append(kv[ii].mean() / cmb.mean() - 1)
            res[win] = {"n": len(kv), "rel_excess": ci(np.r_[pt, bs])}
        out[mode] = res
    # day-in-goal relaxation (activity relative to the goal's days 2-5 mean)
    rel = {}
    for p in prof:
        g = cal.filter(pl.col("pt_date") == p["pt_date"])["goal_no"][0]
        rel.setdefault(int(g), {})[p["day_in_goal"]] = p["whole"]
    by_idx = {j: [] for j in range(1, 6)}
    for g, dd in rel.items():
        base = [dd[j] for j in (2, 3, 4, 5) if j in dd]
        if 1 in dd and len(base) >= 2 and np.mean(base) > 0:
            for j in range(1, 6):
                if j in dd:
                    by_idx[j].append(dd[j] / np.mean(base) - 1)
    out["day_in_goal_rel"] = {j: (float(np.mean(v)), float(np.std(v) / max(1, np.sqrt(len(v)))), len(v)) for j, v in by_idx.items() if v}
    kc = np.array([p["curve"] for p in prof if p["kick"]])
    cc = np.array([p["curve"] for p in prof if not p["kick"]])
    out["curve_kick"] = np.nanmean(kc, 0).tolist() if len(kc) else None
    out["curve_ctrl"] = np.nanmean(cc, 0).tolist() if len(cc) else None
    return out


# ----------------------------------------------------------------------------- figures

def fig_kernels(res: dict):
    tau = LAGS
    panels = [("nudge_target_iso", "nudge → target"), ("nudge_bystander_iso", "nudge → bystanders"),
              ("human_all_iso", "human msg → room"), ("human_mentioned_iso", "human msg → mentioned")]
    cols = {"I": "#1f77b4", "II": "#9467bd", "III": "#d62728", "III_4h": "#ff7f0e", "III_8h": "#2ca02c"}
    fig, axs = plt.subplots(2, 2, figsize=(9, 6), sharex=True)
    for ax, (k, title) in zip(axs.ravel(), panels):
        for lab in ("I", "III"):
            g = res[lab]["G"].get(k)
            if not g or g.get("n_cells", 0) < 20:
                continue
            ax.plot(tau, g["G"], color=cols[lab], lw=1.2, label=f"regime {lab} (n={g['n_cells']})")
            ax.fill_between(tau, g["G_lo"], g["G_hi"], color=cols[lab], alpha=0.15, lw=0)
        ax.axhline(0, color="k", lw=0.5); ax.axvline(0, color="k", lw=0.5, ls=":")
        ax.set_title(title, fontsize=10); ax.legend(fontsize=7, frameon=False)
    for ax in axs[1]:
        ax.set_xlabel("τ (min after kick)")
    for ax in axs[:, 0]:
        ax.set_ylabel("G(τ) = Δ P(active)")
    fig.suptitle("H04 exploratory: matched event-triggered responses (non-holdout; 95% day-bootstrap bands)", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "kernels.pdf"); plt.close(fig)


def fig_fd(res: dict):
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
    for lab, col in (("I", "#1f77b4"), ("III", "#d62728")):
        for k, ls in (("nudge_target_iso", "-"), ("human_all_iso", "--")):
            e = res[lab]["fd"].get(k, {})
            if "chi" not in e:
                continue
            G_ = np.array(res[lab]["G"][k]["G"])[L0 + 1:L0 + 31]
            cg = np.cumsum(G_); C_ = np.array(e["C"])
            dc = C_[0] - C_[1:31]
            axs[0].plot(dc / dc[-1], cg / cg[-1], ls, color=col, marker=".", ms=3, label=f"{lab} {k.split('_')[0]}")
            Cn = np.array(e["C"]) / e["C0"]
            axs[1].plot(np.arange(len(Cn)), Cn, ls, color=col, label=f"{lab} {k.split('_')[0]}")
            o = e.get("onsager", {})
            if o.get("kicked_traj"):
                axs[2].plot(np.arange(1, 31), o["kicked_traj"], ls, color=col, label=f"{lab} {k.split('_')[0]} kicked")
                axs[2].plot(np.arange(1, 31), o["spont_traj"], ls, color=col, alpha=0.45, lw=0.8, label=f"{lab} spontaneous")
                axs[2].plot(np.arange(1, 31), o["non_traj"], ls, color=col, alpha=0.25, lw=0.8, label=f"{lab} no activation")
    axs[0].set_xlabel("C(0) − C(τ)  (normalized)"); axs[0].set_ylabel("Σ_{s≤τ} G(s)  (normalized)")
    axs[0].set_title("h-free shape: FDT ⇒ the diagonal", fontsize=9)
    axs[0].plot([0, 1], [0, 1], "k:", lw=0.8, label="FDT (any field units)")
    axs[1].set_xlabel("τ (min)"); axs[1].set_ylabel("C(τ)/C(0)"); axs[1].set_title("autocorrelation (kick-free minutes)", fontsize=9)
    axs[2].set_xlabel("minutes after activation"); axs[2].set_ylabel("P(active)"); axs[2].set_title("Onsager: kicked vs spontaneous activations", fontsize=9)
    for ax in axs:
        ax.legend(fontsize=6, frameon=False)
    fig.tight_layout(); fig.savefig(FIG / "fd.pdf"); plt.close(fig)


def fig_kickoff(ko: dict):
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    for lab, col in (("I", "#1f77b4"), ("III", "#d62728")):
        k = ko.get(lab)
        if not k or not k.get("curve_kick"):
            continue
        axs[0].plot(k["curve_kick"], color=col, label=f"{lab} kickoff days (n={k['n_kick_days']})")
        axs[0].plot(k["curve_ctrl"], color=col, alpha=0.4, label=f"{lab} other days")
        j = sorted(int(x) for x in k["day_in_goal_rel"])
        m = [k["day_in_goal_rel"][x][0] for x in j]; s = [k["day_in_goal_rel"][x][1] for x in j]
        axs[1].errorbar(j, m, yerr=s, color=col, marker="o", label=lab)
    axs[0].set_xlabel("minute of day window"); axs[0].set_ylabel("mean P(active)"); axs[0].legend(fontsize=7, frameon=False)
    axs[1].axhline(0, color="k", lw=0.5); axs[1].set_xlabel("day within goal"); axs[1].set_ylabel("activity vs. days 2–5 (rel.)")
    axs[1].legend(fontsize=7, frameon=False)
    fig.tight_layout(); fig.savefig(FIG / "kickoff_step.pdf"); plt.close(fig)


if __name__ == "__main__":
    import h04lib
    OUT.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
    cal = calendar()
    suites = suite_days(cal)
    # sensitivity (labelled, decided after the primary run): isolation window [-30, +30]; only A30 is clean
    h04lib.ISO_POST = 30
    sens = {k: run_suite(k + "_iso30", v) for k, v in suites.items() if k in ("I", "III") and len(v) >= 3}
    for v in sens.values():
        for g in v["G"].values():
            g.pop("A60", None)
    jdump(sens, OUT / "explore_kernels_iso30.json")
    h04lib.ISO_POST = 60
    res = {k: run_suite(k, v) for k, v in suites.items() if len(v) >= 3}
    ko = {k: kickoff_suite(k, v) for k, v in suites.items() if k in ("I", "II", "III") and len(v) >= 3}
    jdump(res, OUT / "explore_kernels.json")
    jdump(ko, OUT / "explore_kickoff.json")
    fig_kernels(res); fig_fd(res); fig_kickoff(ko)
    write_provenance("explore_kernels.json + explore_kickoff.json", "hypotheses/H04-reversible-forcing/analysis/explore.py",
                     ["calendar", "activity_bins", "chat_core", "exposure", "roster", "kicks"],
                     {"holdout": "excluded (calendar.holdout)", "PRE": PRE, "POST": POST, "HIST": HIST, "MIN_CTRL": MIN_CTRL,
                      "bootstrap": B, "seed": RNG_SEED, "suites": {k: [v[0], v[-1], len(v)] for k, v in suites.items() if v}})
    print("done")
