"""H17 round-1 goal periods (fixed 2026-10-03 before any real-data run; see the card)."""
REGIME3 = [37, 38, 39, 40, 41, 42, 44, 51]
REGIME2 = [33, 35]
REGIME1 = [10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31]
PERIODS = {**{g: "I" for g in REGIME1}, **{g: "II" for g in REGIME2}, **{g: "III" for g in REGIME3}}
HOLDOUT_CONFIRM = {32: "I", 45: "III"}
TAUS_MIN = [1, 2, 3, 5, 7, 10, 15, 20, 25, 30]
TAU_C = 5
