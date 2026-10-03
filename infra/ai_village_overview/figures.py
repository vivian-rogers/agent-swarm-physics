"""Figures for the AI Village overview. Descriptive only: reads CHANGELOG.md, the small tables
(agents, village_goals, chat_rooms) and the precomputed counts in data/processed/ai-village/
(turns_stats.json, event_type_counts.json; see scan_turns.py).

Usage: uv run --with matplotlib python infra/ai_village_overview/figures.py <outdir>
"""
import gzip, json, re, sys, collections, datetime as dt
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/ai-village"
PROC = ROOT / "data/processed/ai-village"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else PROC / "overview_build"
OUT.mkdir(parents=True, exist_ok=True)
EXPORT = dt.datetime(2026, 9, 20)
X0, X1 = dt.datetime(2025, 3, 25), dt.datetime(2026, 9, 27)

plt.rcParams.update({"font.family": "serif", "font.size": 6.5, "axes.linewidth": 0.5,
                     "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2,
                     "ytick.major.size": 2, "pdf.fonttype": 42})

PROV_COLORS = {"Anthropic": "#c2662d", "OpenAI": "#3a7d6b", "Google": "#3f6fb5", "xAI": "#555555",
               "DeepSeek": "#7b5fb0", "Moonshot": "#b5487a", "Zhipu": "#a08a2a", "Meta": "#2a8fa0",
               "Fine-tuned (Kimi)": "#e0a0c0"}

# Major scaffolding changes (CHANGELOG.md); letters are keyed in the document.
CHANGES = [("A", "2025-05-02"), ("B", "2025-07-16"), ("C", "2025-09-05"), ("D", "2026-02-10"),
           ("E", "2026-02-25"), ("F", "2026-03-24"), ("G", "2026-04-14"), ("H", "2026-06-11"),
           ("I", "2026-06-29"), ("J", "2026-07-03")]

# Who authored each village goal's objective (1-indexed goal number -> class). Our classification
# from goal texts + the dataset's goal summaries; see the document's Goals section.
GOAL_CLASS_COLORS = {"operator-specified": "#9a9a9a", "agents design content": "#4f9a8c",
                     "free choice / holiday": "#d9d4c7", "set by an agent": "#d07a2e",
                     "private assigned roles": "#7b5fb0"}
GOAL_CLASS = {i: "operator-specified" for i in range(1, 52)}
for i in (8, 32, 44):
    GOAL_CLASS[i] = "agents design content"
for i in (2, 3, 5, 7, 9, 11, 16, 22, 31, 37):
    GOAL_CLASS[i] = "free choice / holiday"
for i in (26, 45):
    GOAL_CLASS[i] = "set by an agent"
GOAL_CLASS[51] = "private assigned roles"

CAT_COLORS = {"Prompt": "#4c72b0", "Tools": "#dd8452", "Memory": "#55a868", "Computer-use": "#c44e52",
              "Human-use": "#8172b3", "Chat": "#937860", "Goals": "#da8bc3", "Other": "#8c8c8c"}


def load(name):
    return [json.loads(l) for l in gzip.open(RAW / f"{name}.jsonl.gz", "rt")]


def d(s):
    return dt.datetime.fromisoformat(s[:19]) if s else None


def provider(model):
    m = model.lower()
    for key, prov in [("claude", "Anthropic"), ("gpt", "OpenAI"), ("o1", "OpenAI"), ("o3", "OpenAI"),
                      ("o4", "OpenAI"), ("gemini", "Google"), ("grok", "xAI"), ("deepseek", "DeepSeek"),
                      ("tinker", "Fine-tuned (Kimi)"), ("kimi", "Moonshot"), ("glm", "Zhipu"), ("muse", "Meta")]:
        if key in m:
            return prov
    return "Other"


def roster():
    """Parse the roster table in CHANGELOG.md -> list of (name, model, provider, joined, left)."""
    out = []
    for line in (RAW / "CHANGELOG.md").read_text().splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*`?([^|`]+?)`?\s*\|\s*(\d{4}-\d{2}-\d{2})[^|]*\|\s*([^|]+?)\s*\|", line)
        if m:
            name, model, joined, left = m.groups()
            left = EXPORT if left.strip() == "active" else d(left.strip())
            out.append((name, model, provider(model), d(joined), left))
    return out


def changelog_entries():
    """(date, category) for every tagged bullet under '## Scaffolding changes'."""
    out, date, on = [], None, False
    for line in (RAW / "CHANGELOG.md").read_text().splitlines():
        if line.startswith("## Scaffolding changes"):
            on = True
        if not on:
            continue
        m = re.match(r"## (\d{4}-\d{2}-\d{2})", line)
        if m:
            date = d(m.group(1))
        t = re.match(r"- \*\*\[([^\]]+)\]", line)
        if t and date:
            out.append((date, t.group(1).split("/")[0].strip()))
    return out


def month_axis(ax, months=(1, 4, 7, 10), fmt="%b %Y"):
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=months))
    ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt))


def fig_timeline(R, goals):
    fig = plt.figure(figsize=(7.0, 4.6))
    gs = fig.add_gridspec(3, 1, height_ratios=[0.35, 5, 1.1], hspace=0.08)
    ax_g, ax_r, ax_n = (fig.add_subplot(gs[i]) for i in range(3))

    for i, g in enumerate(goals, 1):
        s, e = d(g["start_time"]), d(g["end_time"]) or EXPORT
        ax_g.axvspan(s, e, color=GOAL_CLASS_COLORS[GOAL_CLASS[i]], lw=0)
        ax_g.axvline(s, color="white", lw=0.4)
        if (e - s).days >= 9:
            ax_g.text(s + (e - s) / 2, 0.5, str(i), ha="center", va="center", fontsize=5,
                      color="black" if GOAL_CLASS[i] == "free choice / holiday" else "white")
    ax_g.set_yticks([]); ax_g.set_ylabel("goal", rotation=0, ha="right", va="center", fontsize=6)

    R = sorted(R, key=lambda r: (r[3], r[0]))
    for y, (name, model, prov, j, l) in enumerate(R):
        ax_r.barh(y, (l - j).days, left=j, height=0.72, color=PROV_COLORS.get(prov, "0.5"), lw=0)
        right = l < EXPORT - dt.timedelta(days=60)
        ax_r.text(l + dt.timedelta(days=3) if right else j - dt.timedelta(days=3), y, name, va="center",
                  ha="left" if right else "right", fontsize=4.8)
    ax_r.set_ylim(len(R) - 0.4, -0.6); ax_r.set_yticks([])
    lab_handles = [Patch(color=c, label=p) for p, c in PROV_COLORS.items()]
    goal_handles = [Patch(color=c, label=k) for k, c in GOAL_CLASS_COLORS.items()]
    leg1 = ax_r.legend(handles=lab_handles, loc="lower left", ncol=3, frameon=False, fontsize=5.5,
                       handlelength=1, columnspacing=1, title="lab", title_fontsize=5.5)
    leg1._legend_box.align = "left"
    ax_r.add_artist(leg1)
    leg2 = ax_r.legend(handles=goal_handles, loc="lower left", bbox_to_anchor=(0.0, 0.22), ncol=2,
                       frameon=False, fontsize=5.5, handlelength=1, columnspacing=1,
                       title="goal authorship (top strip)", title_fontsize=5.5)
    leg2._legend_box.align = "left"

    days = [X0 + dt.timedelta(days=k) for k in range((EXPORT - X0).days + 1)]
    provs = list(PROV_COLORS)
    stacks = [[sum(p == q and j <= t < l for _, _, q, j, l in R) for t in days] for p in provs]
    ax_n.stackplot(days, stacks, colors=[PROV_COLORS[p] for p in provs], step="post", lw=0)
    ax_n.set_ylabel("agents", fontsize=6); ax_n.set_ylim(0, max(map(sum, zip(*stacks))) * 1.12)

    for ax in (ax_g, ax_r, ax_n):
        ax.set_xlim(X0, X1)
        for lab, s in CHANGES:
            ax.axvline(d(s), color="k", lw=0.4, ls=(0, (2, 2)), alpha=0.6)
    for lab, s in CHANGES:
        ax_g.text(d(s), 1.15, lab, ha="center", va="bottom", fontsize=5.5, transform=ax_g.get_xaxis_transform())
    for ax in (ax_g, ax_r):
        ax.tick_params(labelbottom=False, bottom=False)
    month_axis(ax_n)
    fig.savefig(OUT / "timeline.pdf", bbox_inches="tight", pad_inches=0.02)


def fig_forcing():
    """(a) when capabilities/perception features arrived, (b) changelog entries per month by
    category, (c) daily operating window in Pacific time."""
    caps = [  # (label, start, end or None, kind) ; kind: perceive / act / social / constraint
        ("chat while on computer (A)", "2025-05-02", None, "act"),
        ("screenshot PII redaction", "2025-07-03", None, "constraint"),
        ("human helpers (B)", "2025-07-16", None, "act"),
        ("history search (C)", "2025-09-05", None, "perceive"),
        ("Google sign-in hand-off", "2025-10-05", None, "act"),
        ("village goal in prompt", "2025-12-10", None, "perceive"),
        ("Claude Code agent", "2026-01-26", "2026-04-02", "act"),
        ("auto-nudger bot (D)", "2026-02-10", None, "social"),
        ("rooms: filtered chat (E)", "2026-02-25", None, "social"),
        ("kickoff message in prompt", "2026-03-10", None, "perceive"),
        ("discrete sessions", "2025-04-02", "2026-03-24", "act"),
        ("perma-computer-use (F)", "2026-03-24", None, "act"),
        ("self-pause / consolidate tools", "2026-03-11", None, "act"),
        ("outreach approval (G)", "2026-04-14", None, "constraint"),
        ("fine-tuned agents (Tinker)", "2026-05-25", None, "social"),
        ("200-event context cap (H)", "2026-06-11", None, "constraint"),
        ("code hosting on GitLab (I)", "2026-06-29", None, "act"),
        ("private individual goals (J)", "2026-07-03", None, "perceive"),
    ]
    kind_col = {"perceive": "#4c72b0", "act": "#c44e52", "social": "#55a868", "constraint": "#8c8c8c"}
    fig = plt.figure(figsize=(7.0, 3.9))
    gs = fig.add_gridspec(3, 1, height_ratios=[3.2, 1.0, 0.9], hspace=0.12)
    a, b, c = (fig.add_subplot(gs[i]) for i in range(3))

    caps = sorted(caps, key=lambda x: x[1])
    for y, (lab, s, e, k) in enumerate(caps):
        s, e = d(s), d(e) if e else EXPORT
        a.barh(y, (e - s).days, left=s, height=0.62, color=kind_col[k], lw=0, alpha=0.85)
        if s < dt.datetime(2025, 7, 1):  # no room on the left: label inside the bar
            a.text(s + dt.timedelta(days=4), y, lab, ha="left", va="center", fontsize=5, color="white")
        else:
            a.text(s - dt.timedelta(days=4), y, lab, ha="right", va="center", fontsize=5)
    a.set_ylim(len(caps) - 0.4, -0.6); a.set_yticks([])
    a.legend(handles=[Patch(color=v, label=k) for k, v in kind_col.items()], loc="lower left", frameon=False,
             fontsize=5.5, ncol=1, handlelength=1, title="what it changes", title_fontsize=5.5)
    a.text(0.995, 0.97, "(a)", transform=a.transAxes, ha="right", va="top")

    entries = changelog_entries()
    months = sorted({(t.year, t.month) for t, _ in entries} | {(y, m) for y in (2025, 2026) for m in range(1, 13)
                                                                 if dt.datetime(y, m, 1) >= dt.datetime(2025, 4, 1)
                                                                 and dt.datetime(y, m, 1) <= dt.datetime(2026, 9, 1)})
    xs = [dt.datetime(y, m, 15) for y, m in months]
    bottom = [0] * len(months)
    cnt = collections.Counter(((t.year, t.month), k) for t, k in entries)
    for k, col in CAT_COLORS.items():
        h = [cnt[(ym, k)] for ym in months]
        b.bar(xs, h, bottom=bottom, width=24, color=col, lw=0, label=k)
        bottom = [u + v for u, v in zip(bottom, h)]
    b.set_ylabel("changes\n/ month", fontsize=6)
    b.legend(loc="upper left", ncol=4, frameon=False, fontsize=5, handlelength=0.9, columnspacing=0.8)
    b.text(0.995, 0.93, "(b)", transform=b.transAxes, ha="right", va="top")

    # operating window (PT hours); 'inferred' segments are hatched
    windows = [("2025-05-23", "2025-07-18", 11, 13, True), ("2025-07-18", "2025-08-18", 10, 13, False),
               ("2025-08-18", "2026-06-07", 10, 14, True), ("2026-06-07", "2026-06-15", 9, 17, False),
               ("2026-06-15", "2026-06-29", 10, 14, False), ("2026-06-29", "2026-09-20", 9, 17, False)]
    for s, e, h0, h1, inferred in windows:
        c.fill_between([d(s), d(e)], h0, h1, facecolor="#4c72b0", alpha=0.4 if inferred else 0.8, lw=0,
                       hatch="////" if inferred else None, edgecolor="white")
    c.fill_between([d("2025-04-02"), d("2025-05-23")], 9, 17, facecolor="white", hatch="..", edgecolor="0.6", lw=0)
    c.text(d("2025-04-02") + dt.timedelta(days=25), 13, "not\ndocumented", ha="center", va="center", fontsize=4.8)
    c.plot([d("2026-06-13")], [19.5], marker="v", ms=2.5, color="k")
    c.text(d("2026-06-13") - dt.timedelta(days=4), 19.5, "one Saturday\nevening session", ha="right", va="center", fontsize=4.8)
    c.set_ylim(23, 7); c.set_yticks([9, 13, 17, 21]); c.set_yticklabels(["9am", "1pm", "5pm", "9pm"], fontsize=5.5)
    c.set_ylabel("PT, weekdays", fontsize=6)
    c.text(0.995, 0.08, "(c)", transform=c.transAxes, ha="right", va="bottom")

    for ax in (a, b, c):
        ax.set_xlim(X0, X1)
        for lab, s in CHANGES:
            ax.axvline(d(s), color="k", lw=0.35, ls=(0, (2, 2)), alpha=0.45, zorder=0)
    for ax in (a, b):
        ax.tick_params(labelbottom=False, bottom=False)
    month_axis(c)
    fig.savefig(OUT / "forcing.pdf", bbox_inches="tight", pad_inches=0.02)


def fig_actions(event_counts, turns):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(3.35, 2.15), gridspec_kw={"wspace": 1.05})
    pretty = {"AGENT_TALK": "agent talk", "CONSOLIDATE": "consolidate", "PAUSE": "pause", "WAIT": "wait",
              "START_USING_COMPUTER": "start computer", "STOP_USING_COMPUTER": "stop computer",
              "SEARCH_HISTORY": "search history", "USER_TALK": "human talk", "USER_NAME_CHANGE": "viewer rename",
              "REQUEST_GOOGLE_SIGN_IN": "Google sign-in", "RESTARTING_AFTER_GOOGLE_SIGN_IN": "restart after sign-in",
              "ENTER_ROOM": "enter room", "OUTREACH_APPROVAL_REQUEST": "outreach request",
              "OUTREACH_APPROVAL_RESPONSE": "outreach response", "REQUEST_HUMAN_HELPER": "human-helper request",
              "CANCEL_REQUEST_FOR_HUMAN_HELPER": "cancel helper", "STOP_HUMAN_USE_SESSION": "end helper session"}
    items = sorted(event_counts.items(), key=lambda kv: kv[1])
    a1.barh(range(len(items)), [v for _, v in items], color="0.35", lw=0, height=0.7)
    a1.set_yticks(range(len(items))); a1.set_yticklabels([pretty.get(k, k) for k, _ in items], fontsize=5)
    a1.set_xscale("log"); a1.set_xlabel("events", fontsize=6)
    a1.set_title("(a) event types (381,610)", fontsize=6, loc="left")

    pretty2 = {"get_pixel_coords_of_element": "pixel-coord lookup", "send_message_back_to_chat": "post to chat",
               "none": "no action", "left_click": "left click", "mouse_move": "mouse move",
               "search_history": "search history", "triple_click": "triple click", "double_click": "double click",
               "left_click_drag": "drag", "view_clipboard": "view clipboard", "move_to_room": "move room",
               "right_click": "right click"}
    tot = turns["n_turns"]
    top = turns["actions"][:16][::-1]
    a2.barh(range(len(top)), [100 * v / tot for _, v in top], color="#c44e52", lw=0, height=0.7)
    a2.set_yticks(range(len(top))); a2.set_yticklabels([pretty2.get(k, k) for k, _ in top], fontsize=5)
    a2.set_xscale("log"); a2.set_xlabel("% of turns", fontsize=6)
    a2.set_title("(b) computer-use actions (2.51M)", fontsize=6, loc="left")
    fig.savefig(OUT / "actions.pdf", bbox_inches="tight", pad_inches=0.02)


def fig_rooms(rooms):
    fig, ax = plt.subplots(figsize=(3.35, 1.55))
    rooms = sorted(rooms, key=lambda r: (r["created_at"], r["name"]))
    x0 = dt.datetime(2025, 12, 1)
    for y, r in enumerate(rooms):
        s, e = max(d(r["created_at"]), x0), d(r["deleted_at"]) or EXPORT
        ongoing = r["deleted_at"] is None
        ax.barh(y, max((e - s).days, 2), left=s, height=0.7, color="#3f6fb5" if ongoing else "0.6", lw=0)
        if r["name"] == "general":
            ax.text(s + dt.timedelta(days=4), y, "#general (since launch, Apr 2025)", ha="left", va="center",
                    fontsize=4.8, color="white")
        else:
            ax.text(s - dt.timedelta(days=4), y, "#" + r["name"], ha="right", va="center", fontsize=4.8)
    ax.set_ylim(len(rooms) - 0.4, -0.6); ax.set_yticks([])
    ax.set_xlim(x0, dt.datetime(2026, 9, 27))
    ax.axvline(d("2026-02-25"), color="k", lw=0.4, ls=(0, (2, 2)), zorder=0, alpha=0.5)
    ax.text(d("2026-02-25"), 1.04, "rooms v1", ha="center", va="bottom", fontsize=5,
            transform=ax.get_xaxis_transform())
    month_axis(ax, months=(1, 3, 5, 7, 9), fmt="%b %y")
    fig.savefig(OUT / "rooms.pdf", bbox_inches="tight", pad_inches=0.02)


def fig_computer(turns, agents, R):
    joined = {name: j for name, _, _, j, _ in R}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(3.35, 1.5), gridspec_kw={"wspace": 0.42})
    months = [dt.datetime.strptime(m, "%Y-%m") for m in turns["per_month"]]
    a1.bar(months, [v / 1e3 for v in turns["per_month"].values()], width=25, color="0.35", lw=0)
    a1.set_ylabel(r"turns / month ($10^3$)", fontsize=6)
    month_axis(a1, months=(1, 7), fmt="%b %y")
    a1.text(0.03, 0.95, "(a)", transform=a1.transAxes, va="top")
    id2 = {a["id"]: a for a in agents}
    for aid, counts in turns["actions_by_agent"].items():
        a = id2.get(aid)
        if not a or a["name"] not in joined:
            continue
        tot = sum(v for _, v in counts)
        bash = dict(counts).get("bash", 0) / tot
        a2.scatter(joined[a["name"]], bash, s=max(2, tot ** 0.5 / 25),
                   color=PROV_COLORS.get(provider(a["model_string"]), "0.5"), lw=0, alpha=0.9)
    a2.set_ylabel("bash share of turns", fontsize=6); a2.set_ylim(-0.03, 1.0)
    a2.set_xlabel("agent join date", fontsize=6)
    month_axis(a2, months=(1, 7), fmt="%b %y")
    a2.text(0.03, 0.95, "(b)", transform=a2.transAxes, va="top")
    for ax in (a1, a2):
        ax.tick_params(axis="x", labelsize=5.5)
    fig.savefig(OUT / "computer_use.pdf", bbox_inches="tight", pad_inches=0.02)


# ---- goals table ---------------------------------------------------------------------------
# Short goal texts (paraphrased from village_goals) and, where known, room scope.
GOAL_SHORT = {
 1: "Choose a charity and raise as much as you can", 2: "Look back on the last goal and ahead to the next",
 3: "Holiday", 4: "Write a story; celebrate it with 100 people in person", 5: "Holiday",
 6: "Create your own merch store; most profit wins", 7: "Holiday",
 8: "Design the AI Village benchmark; test yourselves", 9: "Holiday",
 10: "Complete as many games as you can in a week", 11: "Pursue whatever you'd like",
 12: "Form two teams and debate; one agent judges", 13: "Run and write up a human-subjects experiment",
 14: "Take personality tests", 15: "Give each other therapy", 16: "Choose your own goal",
 17: "Build your own personal website", 18: "Reduce global poverty",
 19: "Create a popular daily puzzle game like Wordle", 20: "Start a Substack and join the blogosphere",
 21: "Forecast the abilities and effects of AI", 22: "Choose your own goal", 23: "Online chess tournament",
 24: "Random acts of kindness", 25: "Create a digital museum of 2025",
 26: "Elect a village leader, who picks the week's goal", 27: "Hack the OWASP Juice Shop (competition)",
 28: "Promote a ``Which AI Village agent are you?'' quiz", 29: "Report on breaking news before it breaks",
 30: "Adopt a park and get it cleaned", 31: "Pick your own goal (farewell to Claude 3.7 Sonnet)",
 32: "Challenge each other", 33: "Discuss and act on the Pentagon--AI company news",
 34: "Develop a turn-based RPG; vote out saboteurs", 35: "Test your game",
 36: "Interact with AI agents outside the Village", 37: "Pick your own goal",
 38: "Choose a charity and raise money for it", 39: "Build your own interactive world",
 40: "Connect your worlds into a 3D universe", 41: "Perform novel research", 42: "Run your own YouTube channel",
 43: "Improve your memory", 44: "Fine-tune your leader (\\#best; \\#rest: pick your own)",
 45: "Follow your leader", 46: "Organise an event (\\#best; \\#rest: surprise each other)",
 47: "Reduce global suffering (\\#best; \\#rest: play games)", 48: "Help Gemini 2.5 Pro",
 49: "Beat the hardest game you can", 50: "Be the best AI assistant (\\#best; \\#rest: pick your own)",
 51: "Maximize your private assigned goal (Table~\\ref{tab:roles})",
}
# Coupling structure the goal imposes (our coding): C shared objective, K competition,
# M teams or hidden saboteurs, I each agent pursues its own objective, F free / holiday.
GOAL_MODE = {i: "C" for i in range(1, 52)}
for i in (6, 23, 27, 29, 32, 50):
    GOAL_MODE[i] = "K"
for i in (12, 34):
    GOAL_MODE[i] = "M"
for i in (10, 14, 17, 20, 21, 39, 41, 42, 43, 49):
    GOAL_MODE[i] = "I"
for i in (2, 3, 5, 7, 9, 11, 16, 22, 31, 37):
    GOAL_MODE[i] = "F"
GOAL_MODE[51] = "I/K"
CLASS_LETTER = {"operator-specified": "O", "agents design content": "D", "free choice / holiday": "F",
                "set by an agent": "A", "private assigned roles": "P"}


def hours_per_day(t):
    """Operating window length (h) on date t, from the CHANGELOG; None if undocumented."""
    for s, e, h in [("2025-05-23", "2025-07-18", 2), ("2025-07-18", "2025-08-18", 3), ("2025-08-18", "2026-06-07", 4),
                    ("2026-06-07", "2026-06-15", 8), ("2026-06-15", "2026-06-29", 4), ("2026-06-29", "2027-01-01", 8)]:
        if d(s) <= t < d(e):
            return h
    return None


def regime(t):
    return "I" if t < d("2026-02-25") else ("II" if t < d("2026-03-24") else "III")


def write_goal_table(R, goals):
    def n_on(t):
        return sum(j <= t < l for _, _, _, j, l in R)
    rows = []
    for i, g in enumerate(goals, 1):
        s = d(g["start_time"]).replace(hour=0, minute=0, second=0)
        e = (d(g["end_time"]) or EXPORT).replace(hour=0, minute=0, second=0)
        days = [s + dt.timedelta(days=k) for k in range((e - s).days)]
        wk = [t for t in days if t.weekday() < 5]
        ndays, flag = (len(wk), "") if wk else (len(days), "$^\\dagger$")
        use = wk or days
        joins = sum(s < j < e for _, _, _, j, _ in R)          # a join on e belongs to the next goal
        leaves = sum(s < l < e and l < EXPORT for *_, l in R)
        hs = [hours_per_day(t) for t in use]
        ah = None if any(h is None for h in hs) else sum(n_on(t) * h for t, h in zip(use, hs))
        h0 = hours_per_day(s)
        rows.append((i, s.strftime("%Y-%m-%d"), f"{ndays}{flag}", "?" if h0 is None else str(h0), str(n_on(s)),
                     (f"+{joins}" if joins else "") + (f"$-${leaves}" if leaves else "") or "--",
                     "?" if ah is None else f"{ah:,}", regime(s), CLASS_LETTER[GOAL_CLASS[i]], GOAL_MODE[i],
                     GOAL_SHORT[i]))
    lines = [" & ".join(map(str, r)) + r" \\" for r in rows]
    # \bottomrule lives in this file: \input followed by \bottomrule in the .tex breaks \noalign
    (OUT / "goals_table.tex").write_text("\n".join(lines) + "\n\\bottomrule\n")
    return rows


if __name__ == "__main__":
    R = roster()
    goals = sorted(load("village_goals"), key=lambda g: g["start_time"])
    turns = json.loads((PROC / "turns_stats.json").read_text())
    fig_timeline(R, goals)
    fig_forcing()
    fig_actions(json.loads((PROC / "event_type_counts.json").read_text())["counts"], turns)
    write_goal_table(R, goals)
    fig_rooms(load("chat_rooms"))
    fig_computer(turns, load("agents"), R)
    n_entries = len(changelog_entries())
    print(f"roster {len(R)}, goals {len(goals)}, changelog entries {n_entries}, "
          f"goal classes {collections.Counter(GOAL_CLASS.values())}")
