"""POST HOC (labelled; not a pre-registered test). After P1 failed with opposite-sign slopes, the concordance matrix
split the methods by spin channel rather than by the card's E/T families:
  talk channel     H03.n_talk, H03.n_all, H03.nx_fast, H04.n_week, H19.geq_talk   (mutual Spearman 0.4-0.7)
  activity channel H19.geq_active, H04.K_week (rho 0.94), H05.g2b_active
This script asks, per channel, which control parameter collapses the channel with one sign, and whether it survives
regime intercepts (within-regime slope) and beats the regime-only rival in LOPO ELPD. Candidates for round 2's
pre-registration only.

Output: data/processed/H19-loop-gain-collapse/results/posthoc_channels.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import explore as E  # noqa: E402
import h19common as C  # noqa: E402
import h19lib as L  # noqa: E402
import numpy as np  # noqa: E402

CHANNELS = {"talk": ["H03.n_talk", "H03.n_all", "H03.nx_fast", "H04.n_week", "H19.geq_talk"],
            "activity": ["H19.geq_active", "H04.K_week", "H05.g2b_active"]}
CANDS = {"talk": ["k_llm", "m_turn_llm", "m_hour", "x_att_village", "log_N_roster"],
         "activity": ["log_N_roster", "N_roster", "x_att_village", "inv_m_turn_village", "date_mid", "k_llm"]}


def main():
    est, ctr, ctrd, methods = E.load()
    out = {}
    for ch, ms in CHANNELS.items():
        out[ch] = {}
        for x in CANDS[ch]:
            per = {m: L.method_fits(methods[m]["rows"], x, models=("const", "regime", "x", "regime+x")) for m in ms}
            tot = L.elpd_totals(per)
            rec = {"elpd": tot, "x_minus_regime": tot["x"] - tot["regime"], "regimex_minus_regime": tot["regime+x"] - tot["regime"],
                   "slopes": {}, "within_regime": {}}
            for m in ms:
                c = [r for r in per[m]["x"]["coefs"] if r["name"] == x][0]
                w = [r for r in per[m]["regime+x"]["coefs"] if r["name"] == x]
                rec["slopes"][m] = {k: c[k] for k in ("b", "lo", "hi", "p")}
                rec["within_regime"][m] = {k: w[0][k] for k in ("b", "lo", "hi", "p")} if w else None
                rec.setdefault("r2_het", {})[m] = L.r2_het(per[m]["const"]["fit"]["tau2"], per[m]["x"]["fit"]["tau2"])
            sg = [np.sign(v["b"]) for v in rec["slopes"].values()]
            rec["same_sign"] = bool(abs(sum(sg)) == len(sg))
            rec["n_sig_same_sign"] = int(sum((v["lo"] > 0) if sum(sg) > 0 else (v["hi"] < 0) for v in rec["slopes"].values()))
            wsg = [np.sign(v["b"]) for v in rec["within_regime"].values() if v]
            rec["within_same_sign"] = bool(len(wsg) and abs(sum(wsg)) == len(wsg))
            out[ch][x] = rec
            print(f"{ch:8s} {x:18s} same sign {rec['same_sign']} ({rec['n_sig_same_sign']}/{len(ms)} sig) | ΔELPD x−regime "
                  f"{rec['x_minus_regime']:+.1f}, regime+x − regime {rec['regimex_minus_regime']:+.1f} | within-regime signs "
                  f"{[round(v['b'], 3) if v else None for v in rec['within_regime'].values()]}")
    (C.OUT / "results/posthoc_channels.json").write_text(json.dumps(E.jsonable(out), indent=1))
    # Freeze the channel model for analysis/confirm.py (amendment 2026-10-04, before any holdout use):
    # talk-channel methods on k_llm, activity-channel methods on x_att_village; regime-only rival per level.
    import datetime as dt
    frozen = {"frozen_at": dt.datetime.now(dt.timezone.utc).isoformat(), "status": "post hoc, frozen for confirmation",
              "channel_x": {"talk": "k_llm", "activity": "x_att_village"}, "methods": {}}
    for ch, ms in CHANNELS.items():
        x = frozen["channel_x"][ch]
        for m in ms:
            f = L.method_fits(methods[m]["rows"], x, models=("x", "regime"), do_lopo=False)
            fx = f["x"]["fit"]
            frozen["methods"][m] = {"channel": ch, "x": x, "names": f["x"]["names"], "b": fx["b"].tolist(), "tau2": fx["tau2"],
                                    "cov": (fx["cov"] * max(1.0, fx["q"])).tolist(),
                                    "regime_levels": E.regime_levels(methods[m]["rows"], f["regime"]),
                                    "median_se": float(np.median([r["s"] for r in methods[m]["rows"]]))}
    (C.OUT / "results/frozen_channel_model.json").write_text(json.dumps(E.jsonable(frozen), indent=1))


if __name__ == "__main__":
    main()
