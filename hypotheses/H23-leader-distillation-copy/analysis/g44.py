"""H23 x G44 (exploratory): run the observables on the 16 messages of kimi-leader-v7-aug-64 in #44 and score P1-P4.

Usage: uv run python hypotheses/H23-leader-distillation-copy/analysis/g44.py
Reads data/processed/H23-leader-distillation-copy/G44/*, writes G44/results.json, G44/verdicts.json,
G44/features.parquet and G44/results_sensitivity.json (corpus + unplaced samples; all Kimi-checkpoint messages).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h23lib as L  # noqa: E402
from h23run import run_period, _np  # noqa: E402

PDIR = L.OUT / "G44"
ALPHA = 0.10


def verdicts(R: dict) -> dict:
    t1, t3 = R["O1"]["tests"], R["O3"]["tests"]
    v = {}
    # P1 vocabulary copied beyond controls and base
    a = t1["r_corpus:leader>CTRL"]
    kim = R["O1"]["means"]["K_same"]["r_corpus"][0] if R["n"]["K_same"] else float("nan")
    p1a = "supported" if (a["diff"] > 0 and a["p"] < ALPHA and a["mean_a"] > kim) else (
        "failed" if a["diff"] <= 0 else "inconclusive")
    b = t1["c2:leader>CTRL"]
    p1b = "supported" if (b["diff"] > 0 and b["p"] < ALPHA) else ("failed" if b["diff"] <= 0 else "inconclusive")
    v["P1a"] = {"verdict": p1a, "leader": a["mean_a"], "ctrl": a["mean_b"], "kimi_same": kim, "p": a["p"]}
    v["P1b"] = {"verdict": p1b, "leader": b["mean_a"], "ctrl": b["mean_b"], "p": b["p"]}
    # P2 plans not copied but transformed
    ds = R["O2"]["directive_share"]
    dl, dc = ds["leader"][0], ds["corpus"][0]
    jl, j95 = R["O2"]["jsd"]["leader"], R["O2"]["jsd_corpus_self_n"]["p95"]
    p2a = "supported" if (dl <= dc - 0.25 and jl > j95) else ("failed" if abs(dl - dc) <= 0.10 else "inconclusive")
    v["P2a"] = {"verdict": p2a, "directive_leader": dl, "directive_corpus": dc, "jsd_leader_corpus": jl,
                "jsd_self_p95": j95}
    for alph in ("fine", "coarse"):
        ch = R["O2"]["corpus_channel"]["leader"][alph]
        if ch is None:
            v[f"P2b_{alph}"] = {"verdict": "n/a"}
            continue
        if ch["c_ex"] >= 0.20:
            verd = "failed (plans copied)"
        elif ch["c_ex"] <= 0.10 and ch["I_transform_p"] < ALPHA:
            verd = "supported (transformed)"
        elif ch["c_ex"] <= 0.10:
            verd = "failed (not transmitted: I_transform within null)"
        else:
            verd = "inconclusive"
        v[f"P2b_{alph}"] = {"verdict": verd, "c_ex": ch["c_ex"], "I_copy_ex": ch["I_copy_ex"],
                            "I_transform_ex": ch["I_transform_ex"], "I_transform_p": ch["I_transform_p"],
                            "c_p": ch["c_p"], "perfect_copy_ref": ch.get("perfect_copy_ref"),
                            "copy_efficiency": ch.get("copy_efficiency")}
    # P3 closer to corpus than base
    d = t3["d:leader>CTRL"]
    dk = R["O3"]["d"]["K_same"][0] if "K_same" in R["O3"]["d"] else float("nan")
    p3a = "supported" if (d["diff"] > 0 and d["p"] < ALPHA and d["mean_a"] > dk) else (
        "failed" if d["diff"] <= 0 else "inconclusive")
    v["P3a"] = {"verdict": p3a, "leader": d["mean_a"], "ctrl": d["mean_b"], "kimi_same": dk, "p": d["p"]}
    F = R["O3"]["field"]
    v["P3b"] = {"verdict": "supported" if F["invariance_pass"] else "failed",
                "kimi_split_half_cos": F["kimi_split_half_cos"],
                "max_cross_agent_cos": max(F["cross_agent_cos"].values()) if F["cross_agent_cos"] else None}
    if F["invariance_pass"] and "diff" in F:
        p3c = "supported" if (F["diff"] > 0 and F["p_diff_le_0"] < ALPHA) else (
            "failed" if F["diff"] <= 0 else "inconclusive")
        v["P3c"] = {"verdict": p3c, "cos_hL_hC": F["cos_hL_hC"], "cos_hL_hK": F["cos_hL_hK"], "diff_ci": F["diff_ci"]}
    else:
        v["P3c"] = {"verdict": "not evaluated (invariance check failed)",
                    "cos_hL_hC": F.get("cos_hL_hC"), "cos_hL_hK": F.get("cos_hL_hK")}
    # P4 rivals
    v["P4_R1_rejected"] = bool(p1a == "supported" and p3a == "supported")
    conv = R["O2"]["conversation"]
    cl = conv.get("leader", {}).get("fine", {}).get("c", float("nan"))
    cv = conv.get("V_same", {}).get("fine", {}).get("c", float("nan"))
    cvp = conv.get("village_period", {}).get("fine", {}).get("c", float("nan"))
    r2 = R["R2"]["test_ctx_c2:leader>CTRL"]
    jctx = R["O2"]["jsd_leader"].get("leader_ctx", float("nan"))
    jcorp = R["O2"]["jsd_leader"].get("corpus", float("nan"))
    r2_rej = bool(cl <= cv and r2["diff"] <= 0 and jcorp < jctx)
    v["P4_R2"] = {"rejected": r2_rej, "leader_conv_c": cl, "village_same_conv_c": cv, "village_period_conv_c": cvp,
                  "leader_ctx_c2": r2["mean_a"], "ctrl_ctx_c2": r2["mean_b"], "p_ctx": r2["p"],
                  "jsd_leader_corpus": jcorp, "jsd_leader_ctx": jctx}
    return v


def main():
    cfg = {"checkpoints": ["kimi-v7-aug-64"], "corpus_unplaced": False}
    R = run_period(PDIR, cfg)
    V = verdicts(R)
    (PDIR / "verdicts.json").write_text(json.dumps(V, indent=1, default=_np))
    print(json.dumps(V, indent=1, default=_np))
    # sensitivity 1: corpus + unplaced base-Kimi samples
    import shutil
    sdir = PDIR / "sens_unplaced"
    sdir.mkdir(exist_ok=True)
    for f in ("messages.parquet", "vectors.npz"):
        shutil.copy(PDIR / f, sdir / f)
    R1 = run_period(sdir, {"checkpoints": ["kimi-v7-aug-64"], "corpus_unplaced": True})
    V1 = verdicts(R1)
    # sensitivity 2: all Kimi-based checkpoints of the temporary leader (adds 2 messages from 05-28, outside the
    # live window, so 'live' is widened to every leader message for this run)
    s2 = PDIR / "sens_allkimi"
    s2.mkdir(exist_ok=True)
    M = pl.read_parquet(PDIR / "messages.parquet")
    M = M.with_columns(pl.when((pl.col("group") == "leader") & pl.col("checkpoint").str.starts_with("kimi"))
                       .then(True).otherwise(pl.col("live")).alias("live"))
    M.write_parquet(s2 / "messages.parquet")
    shutil.copy(PDIR / "vectors.npz", s2 / "vectors.npz")
    R2 = run_period(s2, {"checkpoints": ["kimi-v2", "kimi-v4-curated56", "kimi-v7-aug-64"]})
    V2 = verdicts(R2)
    # negative control: the Qwen v10 checkpoint (different base, different corpus), live = its own messages
    s3 = PDIR / "neg_qwen"
    s3.mkdir(exist_ok=True)
    M = pl.read_parquet(PDIR / "messages.parquet")
    t0, t1 = L.CHECKPOINTS[1][1], L.CHECKPOINTS[2][1]
    M = M.with_columns((((pl.col("t") >= t0) & (pl.col("t") < t1)) & (pl.col("set") == "period")).alias("live"))
    M.write_parquet(s3 / "messages.parquet")
    shutil.copy(PDIR / "vectors.npz", s3 / "vectors.npz")
    R3 = run_period(s3, {"checkpoints": ["qwen-v10"]})
    sens = {"unplaced_corpus": V1, "all_kimi_checkpoints": V2, "negative_control_qwen_v10": verdicts(R3),
            "qwen_n": R3["n"]}
    (PDIR / "results_sensitivity.json").write_text(json.dumps(sens, indent=1, default=_np))
    print("sensitivity written")


if __name__ == "__main__":
    main()
