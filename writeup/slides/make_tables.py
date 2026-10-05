"""Slide frames for the paper's appendix tables (goal periods, EU ranking) and the matrix pages.

Reads writeup/paper/sections/{goals_table,eu_table}.tex; writes writeup/slides/tables/*.tex.
Usage: python3 writeup/slides/make_tables.py
"""
import re
from pathlib import Path

SEC = Path("writeup/paper/sections"); OUT = Path("writeup/slides/tables"); OUT.mkdir(exist_ok=True)


def trunc(t, n):
    plain = re.sub(r"\$[^$]*\$|\\[a-zA-Z]+|[{}]", "", t)
    if len(plain) <= n or "$" in t:
        return t
    return t[: n - 1].rstrip() + "\\ldots"


# ---- goal periods: 2 frames
rows = [l.strip() for l in (SEC / "goals_table.tex").read_text().splitlines() if l.strip().endswith("\\\\")]
head = r"\# & start & d & h & N & $\pm$ & AH & reg & by & mode & goal \\ \hline"
key = (r"{\tiny\color{muted}d: active weekdays ($^\dagger$over a weekend). h: hours/day. N: agents at start; $\pm$: joins/retirements. "
       r"AH: agent-hours. by: O operator, D agents design, F free, A an agent, P private roles. "
       r"mode: C shared objective, K competition, M teams, I each for itself, F none.}")
gper = 17
frames = []
chunks = [rows[i:i + gper] for i in range(0, len(rows), gper)]
for k, chunk in enumerate(chunks):
    frames.append(
        f"\\begin{{frame}}{{The 51 goal periods ({k + 1}/{len(chunks)})}}\n\\relax{{\\scriptsize\\renewcommand{{\\arraystretch}}{{0.95}}\\setlength{{\\tabcolsep}}{{4pt}}\n"
        f"\\begin{{tabular}}{{@{{}}rlrrrlrlccl@{{}}}}\n{head}\n" + "\n".join(chunk) + "\n\\end{tabular}}\\par\\vspace{0.3em}\n" + key + "\n\\end{frame}\n")
(OUT / "goals.tex").write_text("\n".join(frames))

# ---- EU ranking: frames of 22
eu = []
for l in (SEC / "eu_table.tex").read_text().splitlines():
    m = re.match(r"^(\d+) & (H\d+) & (.*) & ([0-9.]+(?:\$\^\\ast\$)?) & ([0-9.]+) & ([0-9.]+) & (M\d) & (.*)\\\\$", l.strip())
    if m:
        eu.append(m.groups())
per = 22
frames = []
for k in range(0, len(eu), per):
    chunk = eu[k:k + per]
    body = "\n".join(
        f"{r} & {h} & {trunc(t, 60)} & {p} & {v} & \\textbf{{{e}}} & {mm} & {trunc(vd, 30)}\\\\" for r, h, t, p, v, e, mm, vd in chunk)
    frames.append(
        f"\\begin{{frame}}{{All hypotheses by estimated usefulness (ranks {k + 1}--{k + len(chunk)})}}\n"
        "\\relax{\\scriptsize\\renewcommand{\\arraystretch}{0.92}\\setlength{\\tabcolsep}{3pt}\n"
        "\\begin{tabular}{@{}rl>{\\raggedright\\arraybackslash}p{0.48\\textwidth}ccccl@{}}\n"
        "\\# & ID & hypothesis & $p$ & $V$ & EU & M & verdict\\\\ \\hline\n" + body + "\n\\end{tabular}}\\par\\vspace{0.2em}\n"
        "{\\tiny\\color{muted}$p$ credence; $V$ value if true (0--5); EU $=pV$; M mechanism depth (M0 pattern; M1 + model signature, rival fails; M2 + natural experiment and synthetic recovery); $^\\ast$fragile.}\n\\end{frame}\n")
(OUT / "eu.tex").write_text("\n".join(frames))

# ---- matrix pages
pages = sorted(Path("writeup/figures").glob("matrix_slide_*.pdf"))
frames = [
    f"\\begin{{frame}}{{Hypothesis $\\times$ physics-model table ({i + 1}/{len(pages)})}}\n\\centering\\includegraphics[width=\\linewidth,height=0.86\\textheight,keepaspectratio]{{{p.stem}.pdf}}\n\\end{{frame}}\n"
    for i, p in enumerate(pages)]
(OUT / "matrix.tex").write_text("\n".join(frames))
print(len(rows), "goal rows;", len(eu), "EU rows;", len(pages), "matrix pages")
