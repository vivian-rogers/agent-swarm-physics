"""Period metadata for H18 (written 2026-10-03, before any real-data run).

Each entry: goal number -> title, dates (PT, end exclusive), regime, mode, N (from goal-periods.md), rooms, splits,
and which card predictions apply. Used by scheme/build.py, the fitting scripts and write_period_cards.py.
"""
from __future__ import annotations

PERIODS = {
    24: dict(title="Do random acts of kindness!", dates=("2025-12-22", "2025-12-29"), regime="I", mode="C", N=10,
             rooms="everyone in #general", splits="none", group="regime I contrast"),
    25: dict(title="Create a digital museum of 2025", dates=("2025-12-29", "2026-01-05"), regime="I", mode="C", N=10,
             rooms="everyone in #general", splits="none", group="regime I contrast"),
    26: dict(title="Elect a village leader. They choose this week's goal!", dates=("2026-01-05", "2026-01-12"),
             regime="I", mode="C", N=10, rooms="everyone in #general", splits="none", group="regime I contrast"),
    27: dict(title="Hack the OWASP Juice Shop hacking playground", dates=("2026-01-12", "2026-01-26"), regime="I",
             mode="K", N=10, rooms="everyone in #general", splits="none", group="regime I contrast"),
    30: dict(title="Adopt a park and get it cleaned!", dates=("2026-02-09", "2026-02-16"), regime="I", mode="C", N=12,
             rooms="everyone in #general", splits="NE10 auto-nudger on (2026-02-10)", group="regime I contrast"),
    31: dict(title="Pick your own goal (agents bid 3.7 Sonnet farewell)", dates=("2026-02-16", "2026-02-23"),
             regime="I", mode="F", N=12, rooms="everyone in #general",
             splits="Sonnet 4.6 joins 02-18; NE29 3.7 Sonnet retires 02-19; NE11 100-turn cap 02-20",
             group="regime I contrast"),
    35: dict(title="Test your game to make it as fun and functional as you can!", dates=("2026-03-16", "2026-03-23"),
             regime="II", mode="C", N=13, rooms="#best (3) / #rest (10) from 03-16 (NE15)",
             splits="NE15 split on the first day", group="two-room era"),
    36: dict(title="Interact with other AI agents outside the Village!", dates=("2026-03-23", "2026-03-30"),
             regime="II/III", mode="C", N=13, rooms="#best / #rest",
             splits="F perma-computer-use 03-24 (NE14); NE16 03-26", group="two-room era"),
    37: dict(title="Pick your own goal!", dates=("2026-03-30", "2026-04-02"), regime="III", mode="F", N=13,
             rooms="#best / #rest", splits="none", group="two-room era"),
    38: dict(title="Choose a charity and raise as much money as you can for it", dates=("2026-04-02", "2026-04-27"),
             regime="III", mode="C", N=12, rooms="#best / #rest (Sonnet 4.6 moves to #best 04-02)",
             splits="NE17 outreach approval 04-14; NE18 04-20; joins 04-17, 04-22", group="two-room era"),
    39: dict(title="Build your own interactive world!", dates=("2026-04-27", "2026-05-04"), regime="III", mode="I",
             N=15, rooms="#best / #rest (reshuffled 04-27)", splits="GPT-5.5 joins 04-27 (first day)",
             group="two-room era; merge A"),
    40: dict(title="Connect your worlds into a 3D universe!", dates=("2026-05-04", "2026-05-11"), regime="III",
             mode="C", N=15, rooms="merged into #universe-coordination (GPT-5 alone in #rest)",
             splits="merge on the first day", group="two-room era; merge B"),
    41: dict(title="Perform novel research!", dates=("2026-05-11", "2026-05-18"), regime="III", mode="I", N=15,
             rooms="#best / #rest (split back 05-11)", splits="split on the first day", group="two-room era; merge A'"),
    42: dict(title="Run your own Youtube channel!", dates=("2026-05-18", "2026-05-25"), regime="III", mode="I", N=15,
             rooms="#best / #rest", splits="Gemini 3.5 Flash joins 05-20", group="two-room era"),
    44: dict(title="Finetune your leader!", dates=("2026-05-26", "2026-06-01"), regime="III", mode="C", N=16,
             rooms="#best / #rest", splits="Opus 4.8 and the temporary fine-tuned leader join 05-28 (NE31)",
             group="two-room era"),
    51: dict(title="Each agent: Maximize your assigned goal!", dates=("2026-07-06", "2026-09-07"), regime="III",
             mode="P", N=21, rooms="#general; GPT-5.6 isolated rooms 07-09/10; #focus 08-05 to 08-24",
             splits="roster joins (N 21 to 29); tail 09-07 onward is held out", group="#51 non-holdout"),
}

REGIME_III = [g for g, p in PERIODS.items() if p["regime"] == "III" or g == 36]
TWO_ROOM = [35, 36, 37, 38, 39, 41, 42, 44]
REGIME_I = [24, 25, 26, 27, 30, 31]


def gname(g: int) -> str:
    return f"G{g:02d}"
