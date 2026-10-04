"""Post hoc step test (prediction P9 in G51/README.md): the automated speaker goes silent from 2026-08-21 in #51.

Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/run_autooff.py
Writes data/processed/H39-catalysts-vs-fields/steps/autooff_results.json
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h39lib as L  # noqa: E402
import run_steps as RS  # noqa: E402


def main():
    D = RS.Data()
    days = sorted(D.goal_days(51))
    i = days.index("2026-08-21")
    out = {}
    for n in (2, 5):
        pre, post = days[i - n:i], days[i:i + n]
        post = [d for d in post if d < "2026-09-03"]   # NE33 batch join on 09-03/04
        r = RS.compare(D, pre, post, 300)
        excl = set(days[i - n:i + n])
        pl_ = []
        for g, a, b in RS.all_boundaries(D, (len(pre), len(post)), excl):
            if g != 51:
                continue
            rr = RS.compare(D, a, b, 2, content=False)
            if rr.get("status") == "ok":
                pl_.append(rr)
        r["judge_b4"] = L.judge_step(r["b4"], [p["b4"] for p in pl_])
        idle_esc = [p["b4"]["esc"][2] for p in pl_]
        r["idle_esc_pct"] = float(sum(x < r["b4"]["esc"][2] for x in idle_esc) / max(len(idle_esc), 1) * 100)
        dpi_idle = [p["b4"]["dpi"][2] for p in pl_]
        r["dpi_idle_pct"] = float(sum(x < r["b4"]["dpi"][2] for x in dpi_idle) / max(len(dpi_idle), 1) * 100)
        r["n_placebo"] = len(pl_)
        out[f"{len(pre)}x{len(post)}"] = r
        b = r["b4"]
        print(n, pre, post, "agents", r["n_agents"], "K", round(b["K"], 3), "dpi", [round(x, 3) for x in b["dpi"]],
              "esc idle", round(b["esc"][2], 3), "judge", r["judge_b4"].get("cls"), "phi pct", r["judge_b4"].get("phi_pct"),
              "K pct", r["judge_b4"].get("K_pct"), "dpi_idle pct", r["dpi_idle_pct"], "idle esc pct", r["idle_esc_pct"], "n_pl", len(pl_))
    L.jdump(out, L.OUT / "steps" / "autooff_results.json")


if __name__ == "__main__":
    main()
