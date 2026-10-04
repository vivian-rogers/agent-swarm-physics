"""Compose the native result texts for the period READMEs (reads natives.json; writes its "texts" key)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h88lib as H  # noqa: E402

p = H.DATA / "natives" / "natives.json"
n = json.loads(p.read_text())
g = n["G05"]
rows = []
for k, v in g["fits"].items():
    if v.get("best"):
        m2 = v["M2"]; c = v["M1c"]
        rows.append(f"| #{k.split('/')[0]} {k.split('/')[1]} | {v['n_uses']} | {v['best']} | {v['dq_M1_M2']:+.1f} | "
                    f"{c['tau']:.1f} | {c['c'] / c['A']:.3f} |")
    else:
        rows.append(f"| #{k.split('/')[0]} {k.split('/')[1]} | {v['n_uses']} | too few uses | | | |")
t05 = ("**N1 (closed village, follow-up truncated at 2025-08-15).**\n\n| Items | Veteran uses | Best | ΔQAIC(M1−M2) | M1c τ (days) | floor c/A |\n"
       "| --- | --- | --- | --- | --- | --- |\n" + "\n".join(rows) +
       f"\n\n- **Verdict: mixed.** No period is biexponential (0 of {g['n_periods_fitted']} fitted); none is a single exponential "
       "either. Attention to #4–#6's terms decays with the roster fixed, as a power law (#4, #5) or to a floor (#6). So decay "
       "does not need carrier turnover (kill 2 fails here), but its form is not Candia's. Artifacts of #4–#7 are almost never "
       "used after their period (7 uses).")
x = n["NE27"]["term"]; a = n["NE27"]["art"]
t10 = ("**N2 (NE27: three newcomers vs four veterans, 2025-08-18 → 09-19; shares within the pool of #2–#8 items).**\n\n"
       "| Item age (village days since its period ended) | R terms [day-bootstrap CI] |\n| --- | --- |\n" +
       "\n".join(f"| {b} | {x['R'][b]:.2f} [{x['R_ci'][b][0]:.2f}, {x['R_ci'][b][1]:.2f}] |" if x['R'][b] is not None else f"| {b} | – |"
                 for b in ("<=15", "16-40", ">40")) +
       f"\n\n- Uses: newcomers {x['uses_new']}, veterans {x['uses_vet']} (terms); artifacts {a['uses_new']} / {a['uses_vet']} (too few)."
       "\n- **Verdict: mixed.** The newcomers use the most recent period's (#8) terms at the veterans' rate (R 0.98, CI 0.0–2.7: "
       "uninformative), not below it. R does not rise clearly with age (0.98 → 0.65 → 1.02). Within weeks the newcomers carry "
       "the old terms as much as the veterans who coined them. Design note: the share is taken within the pool of #2–#8 "
       "items for both groups (the card's offset was all uses of the kind); this was fixed before the run.")
c = n["NE28"]["per_exit"]
t28 = ("**N3 (carrier loss; other agents' uses of retiree-carried items, 10 village days after vs before, relative to "
       "matched control items).**\n\n| Exit | Carried items | Others' uses before → after | Ratio of ratios [item bootstrap] |\n"
       "| --- | --- | --- | --- |\n" +
       "\n".join(f"| {k} | {v['n_carried']} | {v['carried_pre_others']} → {v['carried_post_others']} | {v['ror']:.2f} "
                 f"[{v['ci'][0]:.2f}, {v['ci'][1]:.2f}] |" for k, v in c.items()) +
       "\n\n- The literal rule (pooled ratio in [0.5, 2], CI including 1) is met, but the pooled CI spans 0.01–2.2, so the "
       "test cannot tell survival from loss. Two of three exits show total loss: after Grok 4 and Claude 3.7 Sonnet left, no "
       "other agent used the items they had carried (27 and 89 uses before, 0 after). After NE28 the carried items fell less "
       "than the controls, but both collapsed with the #21 goal switch on the same day.\n"
       "- **Verdict: mixed** (rule met only through an uninformative CI; per exit, items carried by one agent die with it in "
       "2 of 3 cases). This reading of the CI width is post hoc.")
n["texts"] = {
    "G05": {"verdict": "mixed", "text": t05, "scorecard": "- E (interventional): 1. Decay with a closed roster rules out departure-driven decay for #4–#6; it does not pick Candia's form.\n- D: 1."},
    "G10": {"verdict": "mixed", "text": t10, "scorecard": "- E: 0 (no newcomer deficit for recent items; CI uninformative)."},
    "NE28": {"verdict": "mixed", "text": t28, "scorecard": "- E: 1 (two retirements end their carried items; one is confounded with a goal switch)."},
}
p.write_text(json.dumps(n, indent=1, default=float))
print("ok")
