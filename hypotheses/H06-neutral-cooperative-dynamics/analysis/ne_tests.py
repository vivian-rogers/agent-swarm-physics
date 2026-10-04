"""H06 spanning tests at the batch joins NE27 (2025-08-18, #8 -> #10) and NE33 (2026-09-03/04, inside #51).

(a) Fit before, predict after (axis E): each model is fitted (profile synthetic likelihood, intention clusters km24)
    on the pre side; its (mu, k) then predicts the post side's Simpson lambda at the post side's N and label mask.
    The observed post lambda is scored by its posterior-predictive p-value under each model, and each model's
    prediction is compared with its own post-side refit.
(b) Newcomer kernel (O9): for each newcomer, every label it adopts on its first active day that is held by another
    labelled slot in the previous window is a choice among the projects held then. Single-step kernels:
      NCD w(x) = x(1-x), Hubbell w(x) = x, conformist w(x) = x(x + 0.2(1-x)),
    with x = n_i/(n_others + 1) (the newcomer counted in the population). Log-likelihood ratios pooled over joins.
    Incumbents' choices in the same windows are scored the same way as a reference.

Reads round1_<scope>.json from explore.py for the pre/post fits. Writes data/processed/.../NE<NN>_round1.json.
Usage: uv run python hypotheses/H06-neutral-cooperative-dynamics/analysis/ne_tests.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("POLARS_MAX_THREADS", "1")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import explore as X  # noqa: E402
import ncd_core as M  # noqa: E402

DATA = X.DATA
NE = {
    "NE27": {"pre": "G08", "post": "G10", "newcomers": [9, 10, 11], "join": ["2025-08-18"]},
    "NE33": {"pre": "NE33pre", "post": "NE33post", "newcomers": [43, 44, 45], "join": ["2026-09-03", "2026-09-04"]},
}
KERNELS = {"ncd": lambda x: x * (1 - x), "hubbell": lambda x: x, "conformist": lambda x: x * (x + M.P_D * (1 - x))}


def fit_predict(pre: str, post: str, labelset=X.PRIMARY):
    out = {}
    _, day_pre, remap_pre, _, li_pre, _ = X.load_scope(pre)
    _, day_post, remap_post, _, li_post, _ = X.load_scope(post)
    lab_pre, _ = X.matrix(li_pre, labelset, remap_pre, len(day_pre))
    lab_post, _ = X.matrix(li_post, labelset, remap_post, len(day_post))
    bpre = M.Bank(lab_pre >= 0, day_pre, seed=M._seed(pre, "ne"))
    bpost = M.Bank(lab_post >= 0, day_post, seed=M._seed(post, "ne"))
    st_post = M.label_stats(lab_post, day_post, bpost.m_core)
    c, f, *_ = M.moments(lab_pre, day_pre)
    st_pre = M.label_stats(lab_pre, day_pre, bpre.m_core)
    t_pre = np.array([c, f] + [st_pre[k] for k in M.STAT_NAMES[:7]])
    folder = "G51" if pre.startswith("NE33") else pre
    r_pre = json.loads((DATA / folder / f"round1_{pre}.json").read_text())["sets"][labelset]
    for m in M.MODELS:
        mu, k = r_pre["fits"][m]["mu"], r_pre["fits"][m]["k"]  # explore.py's profile fit on the pre side
        Mp, _, _, _, _ = bpost.predictive(m, mu, k, R=400, tag=M._seed(post, m, "ne"))
        li = M.STAT_NAMES.index("lam")
        lam = Mp[:, li]
        out[m] = {"mu_pre": mu, "k_pre": k, "lam_pred_post": [float(np.nanmean(lam)), float(np.nanpercentile(lam, 2.5)),
                  float(np.nanpercentile(lam, 97.5))], "ppc_post_lam": M.ppc_p(st_post["lam"], lam),
                  "abs_err": float(abs(np.nanmean(lam) - st_post["lam"]))}
    out["obs"] = {"lam_pre": st_pre["lam"], "lam_post": st_post["lam"], "N_pre": lab_pre.shape[1], "N_post": lab_post.shape[1]}
    return out


def kernel_events(scope: str, focal_agents, first_day_only=True, labelset=X.PRIMARY):
    wins, day, remap, _, li, _ = X.load_scope(scope)
    lab, agents = X.matrix(li, labelset, remap, len(day))
    ai = {a: i for i, a in enumerate(agents)}
    pt = wins["pt_date"].to_list()
    events, n_novel_or_self, n_first = [], 0, 0
    for a in focal_agents:
        if a not in ai:
            continue
        j = ai[a]
        obs_w = np.flatnonzero(lab[:, j] >= 0)
        if not len(obs_w):
            continue
        d0 = day[obs_w[0]]
        for w in range(1, len(day)):
            if first_day_only and day[w] != d0:
                continue
            if day[w] != day[w - 1] or lab[w, j] < 0:
                continue
            new = lab[w, j]
            prev = lab[w - 1, j]
            if new == prev:
                continue
            others = [lab[w - 1, i] for i in range(lab.shape[1]) if i != j and lab[w - 1, i] >= 0]
            if not others:
                continue
            u, cnt = np.unique(others, return_counts=True)
            keep = u != prev
            u, cnt = u[keep], cnt[keep]
            n_first += 1
            if new not in u:
                n_novel_or_self += 1
                continue
            x = cnt / (len(others) + 1.0)
            if len(u) >= 2:
                events.append((x, int(np.flatnonzero(u == new)[0])))
    return events, n_novel_or_self, n_first


def kernel_ll(events):
    ll = {}
    for m, w in KERNELS.items():
        s = 0.0
        for x, c in events:
            ww = w(x)
            s += float(np.log(ww[c] / ww.sum()))
        ll[m] = s
    return ll


def main():
    res = {}
    pooled = []
    for ne, spec in NE.items():
        r = {"fit_predict": fit_predict(spec["pre"], spec["post"])}
        ev, nn, nf = kernel_events(spec["post"], spec["newcomers"])
        _, _, _, _, li, _ = X.load_scope(spec["post"])
        incumbents = sorted(set(li["agent"].to_list()) - set(spec["newcomers"]))
        ev_inc, nn_inc, nf_inc = kernel_events(spec["post"], incumbents, first_day_only=True)
        r["newcomers"] = {"n_choice_windows": nf, "n_novel_or_self": nn, "n_events_multi_option": len(ev), "ll": kernel_ll(ev),
                          "beta": M._beta_mle(ev)[:2] if len(ev) >= 3 else None}
        r["incumbents_firstday"] = {"n_choice_windows": nf_inc, "n_novel_or_self": nn_inc, "n_events_multi_option": len(ev_inc),
                                    "ll": kernel_ll(ev_inc), "beta": M._beta_mle(ev_inc)[:2] if len(ev_inc) >= 3 else None}
        pooled += ev
        res[ne] = r
        (DATA / f"{ne}_round1.json").write_text(json.dumps(r, indent=1, default=float))
        print(ne, json.dumps(r, indent=1, default=float))
    res["pooled_newcomers"] = {"n_events": len(pooled), "ll": kernel_ll(pooled)}
    (DATA / "NE_pooled_round1.json").write_text(json.dumps(res["pooled_newcomers"], indent=1, default=float))
    print("pooled", res["pooled_newcomers"])


if __name__ == "__main__":
    main()
