"""Build the one-page hypothesis summaries and the compendium.

For each hypotheses/H<NN>-*/:
  summary/periods.pdf   goal-period diagram generated from the G<NN>/ and NE<NN>/ folders
  summary/summary.tex   generated: header (card title/status, ratings from meta.json) + content.tex
  summary/summary.pdf   compiled one-page summary (warns if it runs over one page)
Then writeup/hypotheses-compendium.pdf: color-coded table of contents + every summary page appended.

Content (content.tex) and suggested ratings (meta.json) are written by hypothesis owners;
rules and rubric in writeup/hypothesis-pages/RUBRIC.md.

Usage: uv run python infra/summaries/build_summaries.py [--only H05] [--no-compendium]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
HYP = ROOT / "hypotheses"
PAGES = ROOT / "writeup/hypothesis-pages"
sys.path.insert(0, str(ROOT / "dashboard"))
import collect  # noqa: E402  (reuse the card / period-folder parsers)

VCOL = {"supported": ("#0ca30c", "white", "✓"), "failed": ("#d03b3b", "white", "✗"), "mixed": ("#fab219", "#0b0b0b", "~"),
        "descriptive": ("#86b6ef", "#0b0b0b", "d"), "pending": ("#ecebe6", "#85847e", "…"), "n/a": ("#ffffff", "#85847e", "–"),
        "other": ("#ffffff", "#85847e", "?")}
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95"]
DIV = {0: "#a32b2b", 0.5: "#c43a3a", 1: "#e34948", 1.5: "#ee8584", 2: "#f5bcbb", 2.5: "#e9e7e1",
       3: "#b7d3f6", 3.5: "#86b6ef", 4: "#5598e7", 4.5: "#2a78d6", 5: "#1c5cab"}


GREEK = dict(zip("αβγδεζηθικλμνξπρστυφχψωΓΔΘΛΞΠΣΦΨΩ",
                 [r"\alpha", r"\beta", r"\gamma", r"\delta", r"\epsilon", r"\zeta", r"\eta", r"\theta", r"\iota", r"\kappa",
                  r"\lambda", r"\mu", r"\nu", r"\xi", r"\pi", r"\rho", r"\sigma", r"\tau", r"\upsilon", r"\phi", r"\chi",
                  r"\psi", r"\omega", r"\Gamma", r"\Delta", r"\Theta", r"\Lambda", r"\Xi", r"\Pi", r"\Sigma", r"\Phi",
                  r"\Psi", r"\Omega"]))
SYMS = {"≥": r"\geq", "≤": r"\leq", "→": r"\to", "←": r"\leftarrow", "↔": r"\leftrightarrow", "⟷": r"\leftrightarrow",
        "⇒": r"\Rightarrow", "×": r"\times", "≈": r"\approx", "≠": r"\neq", "±": r"\pm", "∈": r"\in", "∝": r"\propto",
        "∞": r"\infty", "√": r"\surd", "∑": r"\sum", "∫": r"\int", "∂": r"\partial", "⟨": r"\langle", "⟩": r"\rangle",
        "‖": r"\|", "∼": r"\sim", "≲": r"\lesssim", "≳": r"\gtrsim", "≪": r"\ll", "≫": r"\gg", "·": r"\cdot", "∩": r"\cap",
        "∪": r"\cup", "⊂": r"\subset", "∀": r"\forall", "∃": r"\exists", "ℓ": r"\ell", "✓": r"\checkmark", "✗": r"\times",
        "°": r"^\circ"}
SUPSUB = {"⁰": "^0", "¹": "^1", "²": "^2", "³": "^3", "⁴": "^4", "⁵": "^5", "⁶": "^6", "⁷": "^7", "⁸": "^8", "⁹": "^9",
          "⁻": "^-", "⁺": "^+", "₀": "_0", "₁": "_1", "₂": "_2", "₃": "_3", "₄": "_4", "₅": "_5", "₆": "_6", "₇": "_7",
          "₈": "_8", "₉": "_9"}
TEXT = {"−": "-", "′": "'", "″": "''", "…": "...", "🔒": "(held out)", "“": "``", "”": "''", "‘": "`", "’": "'"}


def tex_escape(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFC", s)
    rep = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
           "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    out = []
    for c in s:
        if c in rep:
            out.append(rep[c])
        elif c in GREEK:
            out.append(f"${GREEK[c]}$")
        elif c in SYMS:
            out.append(f"${SYMS[c]}$")
        elif c in SUPSUB:
            out.append(f"${SUPSUB[c]}$")
        elif c in TEXT:
            out.append(TEXT[c])
        elif ord(c) < 128 or c in "–—éèêëàâäôöûüçñÉÈÀÖÜáíóúÁÍÓÚ":
            out.append(c)
        else:
            base = unicodedata.normalize("NFKD", c)
            base = "".join(b for b in base if not unicodedata.combining(b) and ord(b) < 128)
            out.append(base)  # drop anything else rather than break the build
    return "".join(out)


def seq_color(pct: float):
    i = max(0, min(len(SEQ) - 1, round(pct / 100 * (len(SEQ) - 1))))
    return SEQ[i], ("#ffffff" if i >= 6 else "#0b0b0b")


def div_color(v: float):
    k = min(DIV, key=lambda x: abs(x - v))
    return DIV[k], ("#ffffff" if v <= 0.5 or v >= 4.0 else "#0b0b0b")


def ratings(meta: dict):
    c, f, u = meta.get("complete"), meta.get("faithfulness"), meta.get("usefulness")
    return c, f, u


def badges(meta: dict) -> str:
    c, f, u = ratings(meta)
    out = []
    if c is not None:
        bg, fg = seq_color(c); out.append(rf"\hbadge{{Complete}}{{{c:.0f}\%}}{{{bg[1:]}}}{{{fg[1:]}}}")
    if f is not None:
        bg, fg = div_color(f); out.append(rf"\hbadge{{Faithfulness}}{{{f:g}/5}}{{{bg[1:]}}}{{{fg[1:]}}}")
    if u is not None:
        bg, fg = div_color(u); out.append(rf"\hbadge{{Usefulness}}{{{u:g}/5}}{{{bg[1:]}}}{{{fg[1:]}}}")
    return r"\ ".join(out) if out else r"{\scriptsize\color{inkmuted}\itshape not yet rated}"


# ----------------------------------------------------------------------------------------- period diagram

def goal_span(scope: str):
    """Goal range a spanning test covers: the min and max over every #NN and #NN–#MM mentioned."""
    gs = [int(x) for a, b in re.findall(r"#(\d{1,2})\s*[–-]\s*#?(\d{1,2})", scope) for x in (a, b)]
    gs += [int(g) for g in re.findall(r"#(\d{1,2})\b", scope)]
    gs = [g for g in gs if 1 <= g <= 51]
    return (min(gs), max(gs)) if gs else None


def period_diagram(h: dict, out: Path):
    cal = collect.calendar_meta()
    held = set(json.loads((HYP / "holdout.json").read_text())["goal_periods_held_out"])
    fig, ax = plt.subplots(figsize=(7.4, 1.12), dpi=150)
    # regime bands
    reg = [(g, (cal.get(g) or {}).get("regime")) for g in range(1, 52)]
    spans, cur = [], None
    for g, r in reg:
        if cur and cur[0] == r:
            cur[2] = g
        else:
            cur = [r, g, g]; spans.append(cur)
    shade = {"I": "#f6f5f2", "II": "#eceae4", "III": "#f6f5f2"}
    gs = [p for p in h["periods"] if collect.PERIOD_RE.match(p["period"]).group(2)]
    nes = [p for p in h["periods"] if not collect.PERIOD_RE.match(p["period"]).group(2)]
    rows = {}
    for p in gs:
        g = int(collect.PERIOD_RE.match(p["period"]).group(2)); rows.setdefault(g, []).append(p)
    top = max([len(v) for v in rows.values()] + [1])
    ymax = top + 0.35
    for r, a, b in spans:
        if r:
            ax.add_patch(Rectangle((a - 0.5, -0.15 - 0.9 * max(len(nes), 0)), b - a + 1, ymax + 0.15 + 0.9 * max(len(nes), 0) + 0.45,
                                   color=shade.get(r, "#f6f5f2"), lw=0, zorder=0))
            ax.text((a + b) / 2, ymax + 0.12, f"regime {r}", ha="center", va="bottom", fontsize=6.5, color="#85847e", zorder=5,
                    bbox=dict(facecolor=shade.get(r, "#f6f5f2"), edgecolor="none", pad=0.6))
    ybot = -0.15 - 0.9 * max(len(nes), 0) - (0.35 if nes else 0)
    for g in range(1, 52):
        if g in held:  # held-out goal periods: hatched full-height columns
            ax.add_patch(Rectangle((g - 0.5, ybot), 1.0, ymax + 0.45 - ybot, facecolor="none", edgecolor="#c2c0b8",
                                   hatch="//////", lw=0, zorder=1))
    for g, ps in rows.items():
        for k, p in enumerate(sorted(ps, key=lambda x: x["period"])):
            bg, fg, sym = VCOL.get(p["verdict"], VCOL["other"])
            conf = p["role"] == "confirmatory"
            ax.add_patch(Rectangle((g - 0.42, k), 0.84, 0.84, facecolor=bg, edgecolor="#0b0b0b" if conf else ("#c9c7c0" if p["verdict"] in ("pending", "n/a", "other") else bg),
                                   lw=1.6 if conf else 0.6, ls="--" if p["verdict"] == "pending" else "-", zorder=3))
            ax.text(g, k + 0.42, sym, ha="center", va="center", fontsize=6.5, color=fg, zorder=4, fontweight="bold")
            if len(ps) > 1:
                suf = collect.PERIOD_RE.match(p["period"]).group(3)
                if suf:
                    ax.text(g + 0.47, k + 0.06, suf, fontsize=4.5, color="#52514e", zorder=4)
    for i, p in enumerate(nes):
        span = goal_span(p.get("scope", "")) or (None)
        y = -0.45 - 0.9 * i
        bg, fg, sym = VCOL.get(p["verdict"], VCOL["other"])
        if span:
            a, b = span
            ax.plot([a - 0.4, b + 0.4], [y, y], color=bg if p["verdict"] not in ("pending", "n/a") else "#85847e", lw=3, solid_capstyle="butt", zorder=3)
            ax.plot([a - 0.4, a - 0.4], [y, y + 0.18], color="#52514e", lw=0.8); ax.plot([b + 0.4, b + 0.4], [y, y + 0.18], color="#52514e", lw=0.8)
            x = (a + b) / 2
        else:
            x = None
        ax.text(x if x is not None else 51.2, y - 0.12, f"{p['period']} {sym}" + ("  (confirmatory)" if p["role"] == "confirmatory" else ""),
                ha="center" if x is not None else "right", va="top", fontsize=6, color="#0b0b0b", zorder=4)
    ax.set_xlim(0.4, 51.6)
    ax.set_ylim(-0.25 - 0.9 * len(nes) - (0.35 if nes else 0), ymax + 0.6)
    ax.set_yticks([])
    ax.set_xticks([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 51])
    ax.set_xticklabels([f"#{t}" for t in [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 51]], fontsize=6.5, color="#52514e")
    ax.tick_params(axis="x", length=2, color="#c9c7c0")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#c9c7c0")
    if not h["periods"]:
        ax.text(26, ymax / 2, "no goal-period folders yet", ha="center", va="center", fontsize=8, color="#85847e")
    fig.tight_layout(pad=0.2)
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------------------------------- pages

def period_summary(h: dict) -> str:
    c = {k: v for k, v in h["verdicts"].items() if v}
    if not c:
        return "none yet"
    order = ["supported", "failed", "mixed", "descriptive", "pending", "n/a"]
    s = ", ".join(f"{c[k]} {k}" for k in order if k in c)
    conf = h["confirm_verdicts"]
    if conf:
        s += "; holdout: " + ", ".join(f"{x['period']} {x['verdict']}" for x in conf)
    return tex_escape(s)


def stage_text(h: dict, meta: dict) -> str:
    return tex_escape(f"level: {h['level']}  ·  pipeline checks {h['progress']}%  ·  updated {meta.get('updated', '—')}")


def write_stub(sdir: Path, h: dict):
    card = (HYP / h["slug"] / "README.md").read_text(errors="replace")
    sec = collect.sections(card)
    model = collect.strip_md(sec.get("Model", "")).replace("\n", " ")
    model = re.sub(r"\s+", " ", model)[:420]
    q = re.sub(r"\s+", " ", collect.strip_md(sec.get("Question", "")))[:700]
    (sdir / "content.tex").write_text(
        "% AUTO STUB: replace with a written summary (see writeup/hypothesis-pages/RUBRIC.md). Keep this marker line out of written versions.\n"
        rf"\hwhat{{\textit{{Not yet summarized. The question:}} {tex_escape(q)}}}" "\n"
        rf"\hmodel{{{tex_escape(model)}}}" "\n")



AXIS_NAMES = {"A": "mapping", "B": "assumptions", "C": "adequacy", "D": "unfitted predictions", "E": "interventional",
              "F": "identifiability", "G": "ground truth", "H": "comparative", "I": "transfer"}


def period_table(h: dict, max_rows: int = 16) -> str:
    ps = sorted(h["periods"], key=lambda p: (p["role"] != "confirmatory", p["verdict"] in ("pending", "other", "n/a"), p["period"]))
    if not ps:
        return r"\textit{No goal-period folders yet.}"
    sym = {"supported": r"$\checkmark$", "failed": r"$\times$", "mixed": r"$\sim$", "descriptive": "d", "pending": r"$\cdots$", "n/a": "--", "other": "?"}
    rows = []
    for p in ps[:max_rows]:
        txt = p.get("verdict_text") or p["verdict"]
        txt = txt if len(txt) < 95 else txt[:92] + "..."
        conf = r" \textbf{(holdout)}" if p["role"] == "confirmatory" else ""
        rows.append(rf"{tex_escape(p['period'])} & {sym.get(p['verdict'], '?')} & {tex_escape(txt)}{conf} \\")
    more = rf"\multicolumn{{3}}{{l}}{{\textit{{+{len(ps) - max_rows} more periods: see the card.}}}} \\" if len(ps) > max_rows else ""
    return r"\noindent\begin{tabular}{@{}l@{\ }c@{\ }p{0.76\columnwidth}@{}}" + "\n".join(rows) + more + r"\end{tabular}"


def score_table(h: dict) -> str:
    cells = []
    for a in "ABCDEFGHI":
        v = h["scores"].get(a)
        cells.append(rf"{a} {AXIS_NAMES[a]} & {'--' if v is None else v} \\")
    half = (len(cells) + 1) // 2
    left, right = cells[:half], cells[half:]
    body = "\n".join(l.replace(r" \\", "") + " & " + (right[i].replace(r" \\", "") if i < len(right) else " & ") + r" \\" for i, l in enumerate(left))
    return (r"\noindent\begin{tabular}{@{}lr@{\qquad}lr@{}}" + body + r"\end{tabular}" +
            rf"\par\smallskip Level: \textbf{{{tex_escape(h['level'])}}}. Scale 0 not done or failed, 1 partial, 2 passed (\texttt{{writeup/paper.tex}}).")


def round_two(slug: str) -> str:
    card = (HYP / slug / "README.md").read_text(errors="replace")
    if "## Round 2 redirects" not in card:
        return r"\textit{No round-2 redirects yet.}"
    sec = card[card.index("## Round 2 redirects"):]
    nxt = sec.find("\n## ", 5)
    sec = sec[:nxt] if nxt > 0 else sec
    items = []
    ess = re.search(r"\*\*What the direction is really after:\*\*\s*(.+)", sec)
    if ess:
        e = re.sub(r"\*\*", "", ess.group(1)).strip()
        items.append(r"\textbf{Essence.} " + tex_escape(e if len(e) < 330 else e[:327] + "..."))
    for m in re.finditer(r"^- \*\*(H\d{2}-R\d+)\.?\s*(.*?)\*\*\s*(.*)$", sec, re.M):
        rid, head, rest = m.group(1), m.group(2).strip(), m.group(3).strip()
        if "superseded" in (head + rest).lower():
            continue
        text = (head + " " + rest).strip() if head else rest
        first = re.split(r"(?<=[.!?])\s", re.sub(r"\*\*|`", "", text), maxsplit=1)[0]
        items.append(rf"\textbf{{{rid}}} {tex_escape(first[:240])}")
    return r"\begin{itemize}\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}" + "".join(rf"\item {x}" for x in items) + r"\end{itemize}"


def build_page(h: dict) -> dict:
    hdir = HYP / h["slug"]
    sdir = hdir / "summary"
    sdir.mkdir(exist_ok=True)
    if not (sdir / "content.tex").exists():
        write_stub(sdir, h)
    stub = "AUTO STUB" in (sdir / "content.tex").read_text(errors="replace")[:200]
    meta = json.loads((sdir / "meta.json").read_text()) if (sdir / "meta.json").exists() else {}
    period_diagram(h, sdir / "periods.pdf")
    rel = Path("../../../writeup/hypothesis-pages/hpage.tex")
    footer = tex_escape(f"{h['slug']} · generated {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} by infra/summaries/build_summaries.py · "
                        f"card hypotheses/{h['slug']}/README.md · ratings: {meta.get('rated_by', 'not rated')}"
                        + (" · DRAFT: auto stub, not yet written" if stub else ""))
    status = h["status"] if len(h["status"]) < 260 else h["status"][:257] + "…"
    tex = rf"""\documentclass[aps,pre,reprint,10pt,nofootinbib]{{revtex4-2}}
\input{{{rel.as_posix()}}}
\def\hID{{{h['id']}}}
\def\hTitle{{{tex_escape(h['title'])}}}
\def\hStatus{{{tex_escape(status)}}}
\def\hStage{{{stage_text(h, meta)}}}
\def\hBadges{{{badges(meta)}}}
\def\hPeriodSummary{{{period_summary(h)}}}
\def\hDate{{Updated {meta.get('updated', dt.date.today().isoformat())}}}
\def\hFooter{{{footer}}}
\def\hPeriodTable{{{period_table(h)}}}
\def\hScoreTable{{{score_table(h)}}}
\def\hRoundTwo{{{round_two(h['slug'])}}}
\input{{content.tex}}
\begin{{document}}
\makehpage
\end{{document}}
"""
    (sdir / "summary.tex").write_text(tex)
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "summary.tex"], cwd=sdir,
                       capture_output=True, text=True, timeout=120)
    log = (sdir / "summary.log").read_text(errors="replace") if (sdir / "summary.log").exists() else r.stdout
    m = re.search(r"Output written on summary\.pdf \((\d+) page", log)
    pages = int(m.group(1)) if m else 0
    err = None if r.returncode == 0 else (re.findall(r"^! .*", log, re.M) or ["pdflatex failed"])[0]
    for ext in (".aux", ".log", ".out", "Notes.bib", ".bbl", ".blg"):
        (sdir / f"summary{ext}").unlink(missing_ok=True)
    return {"id": h["id"], "pages": pages, "error": err, "stub": stub, "meta": meta}


# ----------------------------------------------------------------------------------------- compendium

def compendium(hs: list[dict], results: dict):
    """RevTeX compendium: color-coded table of contents, then every one-page summary appended."""
    def cell(v, fn, fmt):
        if v is None:
            return r"\textcolor{gray}{--}"
        bg, fg = fn(v)
        return rf"\colorbox[HTML]{{{bg[1:]}}}{{\makebox[2.6em]{{\textcolor[HTML]{{{fg[1:]}}}{{{fmt(v)}}}}}}}"

    built = [h for h in hs if (HYP / h["slug"] / "summary/summary.pdf").exists()]
    rows = []
    for i, h in enumerate(built):
        r = results.get(h["id"], {})
        meta = r.get("meta") or (json.loads((HYP / h["slug"] / "summary/meta.json").read_text())
                                 if (HYP / h["slug"] / "summary/meta.json").exists() else {})
        stub = r.get("stub", "AUTO STUB" in (HYP / h["slug"] / "summary/content.tex").read_text(errors="replace")[:200])
        c, f, u = ratings(meta)
        line = meta.get("one_line") or h["status"]
        line = line if len(line) < 120 else line[:117] + "..."
        title = h["title"] if len(h["title"]) < 72 else h["title"][:69] + "..."
        draft = r" \textcolor{gray}{\scriptsize(draft)}" if stub else ""
        rows.append(rf"\textbf{{{h['id']}}} & {tex_escape(title)}{draft}\newline"
                    rf"{{\scriptsize\color{{gray}}{tex_escape(line)}}} & {cell(c, seq_color, lambda v: f'{v:.0f}' + chr(92) + '%')} & "
                    rf"{cell(f, div_color, lambda v: f'{v:g}')} & {cell(u, div_color, lambda v: f'{v:g}')} & @@PAGE{i}@@ \\")
    head = r"\textbf{ID} & \textbf{Hypothesis} & \textbf{Complete} & \textbf{Faithful} & \textbf{Useful} & \textbf{p.}\\ \hline"
    chunks = [rows[i:i + 12] for i in range(0, len(rows), 12)]
    tables = "\n".join(r"\begin{center}\begin{tabular}{lp{0.6\textwidth}cccr}\hline " + head + "\n" + "\n".join(ch)
                       + "\n\\hline\\end{tabular}\\end{center}" for ch in chunks)
    legend_seq = " ".join(rf"\colorbox[HTML]{{{seq_color(x)[0][1:]}}}{{\textcolor[HTML]{{{seq_color(x)[1][1:]}}}{{\scriptsize {x}\%}}}}" for x in (5, 25, 50, 75, 100))
    legend_div = " ".join(rf"\colorbox[HTML]{{{div_color(v)[0][1:]}}}{{\textcolor[HTML]{{{div_color(v)[1][1:]}}}{{\scriptsize {v:g}}}}}" for v in (0, 1, 2, 2.5, 3, 4, 5))
    includes = "\n".join(rf"\includepdf[pages=1,link,linkname={h['id']}]{{../../hypotheses/{h['slug']}/summary/summary.pdf}}" for h in built)
    date = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    template = rf"""\documentclass[aps,pre,onecolumn,10pt,nofootinbib]{{revtex4-2}}
\usepackage{{xcolor}}
\usepackage[hidelinks]{{hyperref}}
\renewcommand{{\arraystretch}}{{1.2}}
\begin{{document}}
\title{{Agent-swarm physics: hypothesis compendium}}
\author{{Vivian Rogers, with Claude Opus 5.5}}
\date[]{{Living status document, regenerated {date}. Not the paper.}}
\begin{{abstract}}
Two RevTeX pages per hypothesis follow; click a row to jump to it. Ratings are estimates calibrated across hypotheses by the coordinator (rubric: \texttt{{writeup/hypothesis-pages/RUBRIC.md}}).
\textbf{{Completion}}: estimated progress of the research direction (idea 5\%, round 1 done 35--50\%, holdout run 55--65\%, robustness and causal designs 70--85\%, settled 90--100\%). {legend_seq}
\textbf{{Faithfulness}} (0--5, scoped): how well the model holds for what it claims (3 = descriptive or primary holdout passed; 4 = supported; 5 = faithful and mechanistic).
\textbf{{Usefulness}} (0--5, unscoped): what an operator or alignment researcher can do with it, true or not (1 = vocabulary only; 2 = a diagnostic; 3 = a validated monitor or design rule; 4 = a steering lever; 5 = a transferable control knob). {legend_div}
\end{{abstract}}
\maketitle
{{\footnotesize
@@TABLES@@
}}
\end{{document}}
"""

    def compile_with(toc_pages: int) -> int:
        tex = template.replace("@@TABLES@@", tables)
        for i in range(len(built)):
            tex = tex.replace(f"@@PAGE{i}@@", str(toc_pages + 1 + 2 * i))
        (PAGES / "compendium.tex").write_text(tex)
        for _ in range(2):
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "compendium.tex"], cwd=PAGES,
                               capture_output=True, text=True, timeout=300)
        log = (PAGES / "compendium.log").read_text(errors="replace")
        if r.returncode != 0:
            print("compendium FAILED:", (re.findall(r"^! .*", log, re.M) or ["?"])[0])
            return -1
        m = re.search(r"Output written on compendium\.pdf \((\d+) page", log)
        return int(m.group(1)) if m else 0

    toc = compile_with(1)
    if toc < 0:
        return
    if toc != 1:
        compile_with(toc)
    # merge: RevTeX contents pages + every summary page; then link each contents row to its page
    from pypdf import PdfReader, PdfWriter
    from pypdf.annotations import Link
    w = PdfWriter()
    for pg in PdfReader(PAGES / "compendium.pdf").pages:
        w.add_page(pg)
    starts = {}
    for h in built:
        starts[h["id"]] = len(w.pages)
        for pg in PdfReader(HYP / h["slug"] / "summary/summary.pdf").pages[:2]:
            w.add_page(pg)
    ids = starts  # 0-based index of each hypothesis' first page
    bbox = subprocess.run(["pdftotext", "-bbox", "-f", "1", "-l", str(toc), str(PAGES / "compendium.pdf"), "-"],
                          capture_output=True, text=True).stdout
    page_i, seen = -1, set()
    for line in bbox.splitlines():
        if "<page " in line:
            page_i += 1
            ph = float(re.search(r'height="([\d.]+)"', line).group(1))
            pw = float(re.search(r'width="([\d.]+)"', line).group(1))
        m = re.search(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(H\d{2})</word>', line)
        if m and m.group(5) in ids and m.group(5) not in seen:
            seen.add(m.group(5))
            x0, y0, x1, y1 = (float(m.group(k)) for k in range(1, 5))
            rect = (x0 - 2, ph - y1 - 12, pw - x0, ph - y0 + 2)  # whole row, two text lines tall
            w.add_annotation(page_number=page_i, annotation=Link(rect=rect, target_page_index=ids[m.group(5)]))
    for h in built:
        w.add_outline_item(f"{h['id']}: {h['title'][:60]}", starts[h["id"]])
    with open(ROOT / "writeup/hypotheses-compendium.pdf", "wb") as f:
        w.write(f)
    total = len(w.pages)
    for ext in (".aux", ".log", ".out", "Notes.bib", ".bbl", ".blg"):
        (PAGES / f"compendium{ext}").unlink(missing_ok=True)
    print(f"compendium: {total} pages ({toc} contents, {len(seen)} linked rows) → writeup/hypotheses-compendium.pdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="build one hypothesis page, e.g. H05 (skips the compendium)")
    ap.add_argument("--no-compendium", action="store_true")
    args = ap.parse_args()
    hs = collect.hypotheses()
    results = {}
    for h in hs:
        if args.only and h["id"] != args.only:
            continue
        r = build_page(h)
        results[h["id"]] = r
        flag = "ERROR " + r["error"] if r["error"] else (f"WARNING {r['pages']} pages" if r["pages"] != 2 else "ok")
        print(f"{h['id']}: {flag}{'  (stub)' if r['stub'] else ''}")
    if not args.only and not args.no_compendium:
        compendium(hs, results)


if __name__ == "__main__":
    main()
