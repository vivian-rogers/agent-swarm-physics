"""H120 post hoc checks (labelled post hoc in the card; run after the round-1 results):
  (a) J-only drift: the same score tests with the drift restricted to J (h_i held constant across days);
  (b) G38 before the first roster join (04-02 -> 04-16, 11 days; no joiner outside the core);
  (c) h-only drift (J held constant).
Writes data/processed/H120-period-ness-stationarity/results/posthoc.json
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h120lib as L  # noqa: E402


def tests(F, n, rng, R=1000):
    nulls = L.random_splits(n, R, rng)
    t1 = L.perm_test(F, L.contiguous_tau(n), nulls)
    perms = [L.trend_tau(n)[rng.permutation(n)] for _ in range(R)]
    t2 = L.perm_test(F, L.trend_tau(n), perms)
    return {"T1_R": t1["R"], "T1_p": t1["p"], "T2_R": t2["R"], "T2_p": t2["p"]}


def main():
    rng = np.random.default_rng(20261007)
    out = {}
    for w in ("G38", "38a", "51main", "51g", "19a", "27", "8"):
        for ch in ("act", "talk"):
            win = L.load_window(w, ch)
            des = L.design(win)
            F = L.fit(des)
            n = len(des["days"])
            N = F["N"]
            FJ = dict(F, drift_idx=np.arange(1, N + 1))
            Fh = dict(F, drift_idx=np.array([0]))
            out[f"{w}|{ch}|J_only"] = tests(FJ, n, rng)
            out[f"{w}|{ch}|h_only"] = tests(Fh, n, rng)
            print(w, ch, "J-only", out[f"{w}|{ch}|J_only"], "h-only", out[f"{w}|{ch}|h_only"], flush=True)
    for ch in ("act", "talk"):
        win = L.load_window("G38", ch)
        keep = [i for i, d in enumerate(win["days"]) if d <= "2026-04-16"]
        win = dict(win, days=[win["days"][i] for i in keep], S=[win["S"][i] for i in keep],
                   weekday=win["weekday"][keep], trim_len=win["trim_len"][keep])
        des = L.design(win)
        F = L.fit(des)
        out[f"G38_prejoin|{ch}|h_and_J"] = tests(F, len(des["days"]), rng)
        print("G38 pre-join", ch, out[f"G38_prejoin|{ch}|h_and_J"], flush=True)
    (L.DATA / "results" / "posthoc.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
