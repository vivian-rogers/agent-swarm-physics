"""Does H04's isolated matched design (imported unmodified) recover a known nudge effect when the nudger re-nudges
agents that stay idle? Runs h04lib on H30's simulated swarms (G51-like and G38-like sampling), S0 (no effect) and
S1 (constant effect), next to the H30 estimator. Writes synthetic/h04_design_check.json.
Run: uv run python hypotheses/H30-operator-susceptibility/analysis/synthetic_h04check.py
"""
from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from synthetic import *  # noqa: E402,F403
import h04lib as H4  # noqa: E402


def to_h04(panels, kicks):
    D = []
    for p in panels:
        st = np.where(p.act == 1, 3, np.where(p.idle == 1, 2, 1)).astype(np.int8)
        D.append(H4.Day(p.label, "III", 4, 2, 1, None, np.asarray(p.agents), st))
    k = kicks.filter(pl.col("cls").is_in(["N_tgt", "N_by", "H_men", "H_und"]))
    role = {"N_tgt": "target", "N_by": "bystander", "H_men": "mentioned", "H_und": "unmentioned"}
    resp = k.select(pl.col("day").alias("day"), pl.col("minute"), pl.col("row"), pl.col("agent"),
                    pl.col("kind"), pl.col("cls").replace_strict(role).alias("role"), pl.col("msg"))
    return D, resp


def one(args):
    design, scen, seed = args
    panels, kicks, mm, U, st_t, st_v, par = simulate(design, scen, seed)
    truth = float(kicks.filter(pl.col("cls") == "N_tgt")["e_act"].mean())
    base = build_base(panels, kicks=kicks)
    f = fit_activity(base, kick_columns(base, kicks))
    D, resp = to_h04(panels, kicks)
    H4.attach_hits(D, resp)
    c = H4.build_cells(D, np.arange(64))
    ctl = H4.control_means(c, 64)
    sets = H4.build_sets(D, resp, c)
    out = {"design": design, "scen": scen, "seed": seed, "truth": truth, "h30": f.coef("N_tgt")}
    for k in ("nudge_target_iso", "nudge_target_all"):
        r = H4.matched_response(c, ctl, sets[k]["ids"], len(D), k, sets[k]["n_kicks"], sets[k]["nb_adjust"])
        G = H4.curves(r, np.ones((1, len(D))))
        out[k] = float(H4.amp(G, 1, 30)[0]); out[k + "_n"] = int(len(sets[k]["ids"]))
        out[k + "_pre"] = float(H4.amp(G, -30, -16)[0])
    # share of nudges followed by another directed kick to the same agent within 60 min (re-nudge)
    nt = kicks.filter(pl.col("cls") == "N_tgt").sort("day", "agent", "minute")
    gap = nt.with_columns((pl.col("minute").shift(-1).over(["day", "agent"]) - pl.col("minute")).alias("g"))
    out["renudge60"] = float((gap["g"].fill_null(999) <= 60).mean())
    # the same H30 model with H04's isolation rule applied to treated and control cells (no OTHER directed kick to
    # the agent in [m-30, m+60]), and with isolation on the past only
    dirk = kicks.filter(pl.col("cls").is_in(["N_tgt", "H_men"]))
    Kd = np.zeros(len(base.Y), np.float32); Kn = np.zeros(len(base.Y), np.float32)
    for d, (na, nmn) in base.shapes.items():
        start, m = base.offsets[d]
        if len(m) == 0:
            continue
        K = np.zeros((na, nmn), np.int32)
        gg = dirk.filter(pl.col("day") == d)
        np.add.at(K, (gg["row"].to_numpy(), gg["minute"].to_numpy()), 1)
        blk = slice(start, start + na * len(m))
        Kd[blk] = H4.window_sum(K, -30, 60)[:, m].ravel(); Kn[blk] = K[:, m].ravel()
    X = kick_columns(base, kicks)
    out["h30_iso_future"] = fit_activity(base, X, mask=(Kd - Kn) == 0).coef("N_tgt")
    Kp = H4.window_sum  # noqa
    pre_cols = len(CLASSES) + len(POST_CLASSES)
    Kpast = X[:, pre_cols + CLASSES.index("N_tgt")] + X[:, pre_cols + CLASSES.index("H_men")]
    out["h30_iso_past"] = fit_activity(base, X, mask=Kpast == 0).coef("N_tgt")
    return out


if __name__ == "__main__":
    jobs = [(d, s, r) for d in ("G51like", "G38like", "G51renudge") for s in ("S0_null", "S1_const") for r in range(8)]
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(one, jobs))
    df = pl.DataFrame(res)
    summ = (df.group_by("design", "scen", maintain_order=True)
            .agg(pl.len().alias("reps"), pl.col("truth").mean(), pl.col("h30").mean(), pl.col("h30").std().alias("h30_sd"),
                 pl.col("nudge_target_iso").mean(), pl.col("nudge_target_iso").std().alias("iso_sd"),
                 pl.col("nudge_target_iso_n").mean(), pl.col("nudge_target_iso_pre").mean(),
                 pl.col("nudge_target_all").mean(), pl.col("renudge60").mean(),
                 pl.col("h30_iso_future").mean(), pl.col("h30_iso_future").std().alias("iso_future_sd"),
                 pl.col("h30_iso_past").mean()))
    print(summ)
    jdump({"replicates": df.to_dicts(), "summary": summ.to_dicts()}, OUT / "synthetic" / "h04_design_check.json")
