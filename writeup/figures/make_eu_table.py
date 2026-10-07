"""All scored hypotheses ranked by estimated usefulness -> writeup/paper/sections/eu_table.tex

Source: hypotheses/H*/summary/meta.json, field v2 (claim scoring v2): credence p, value_if_true V,
expected_usefulness EU (= pV), mechanism_level M, fragile, original_verdict (the verdict column).
The hypothesis column is the card title (first line of the card README, after "H<NN>:").
Sorted by EU descending, then p descending, then card number. 44 rows per table* block.

Usage: uv run python writeup/figures/make_eu_table.py
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dashboard"))
import collect  # noqa: E402

OUT = ROOT / "writeup/paper/sections/eu_table.tex"
PER = 44
TITLE_MAX = 95
VERDICT_MAX = 40

# Hand-shortened titles for cards whose title exceeds TITLE_MAX (2026-10-07). Others are cut automatically.
SHORT_TITLE = {
    "H10": "Goals are Legendre pushes: the response to a goal is predictable from unforced fluctuations",
    "H12": "Groupthink is dimensional collapse: few collective modes, shrinking participation ratio",
    "H14": "Entropy production of behavior sequences: per-family arrows of time, collective irreversibility",
    "H15": "Semantic information through natural scrambles: what keeps agents and the swarm viable",
    "H17": "Behavior is a Markov state model with few metastable sets; its mixing time is an order parameter",
    "H18": "Attention dilutes as 1/k: response to a message falls with the messages waiting at the turn",
    "H19": "One curve for all periods: loop gains collapse onto one function of a control parameter",
    "H24": "Forecast week (#21): switching from independent drafts to comparison switches the coupling on",
    "H106": "A finite magnet wanders as 1/N: the slow mode's decay time should grow with village size",
    "H108": "Goldstone wandering: a spontaneous room direction should drift, a fielded one stay pinned",
    "H122": "A batch join is a spin addition: do incumbents respond as fitted couplings say? (NE27, NE33)",
    "H123": "Regime I's turn order is a sweep: equilibrium-looking statistics, nonzero entropy production",
    "H124": "Four agents for weeks: an exact kinetic Ising benchmark for mean-field approximations (#4, #6)",
    "H130": "#51 agents are OU particles in private wells: reads kick them; kicks decay at the well's rate",
    "H131": "Assigned antagonism switches off one read-out after the prize goes: a field quench, no remanence",
}

# Unicode -> LaTeX (text mode). Math symbols become inline math.
MATH = {"−": "-", "×": r"\times", "≈": r"\approx", "≤": r"\leq", "≥": r"\geq", "±": r"\pm", "→": r"\to", "∪": r"\cup",
        "÷": r"\div", "<": "<", ">": ">", "|": "|", "~": r"\sim",
        "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda", "Γ": r"\Gamma", "Π": r"\Pi", "Φ": r"\Phi",
        "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta", "ζ": r"\zeta", "η": r"\eta", "θ": r"\theta",
        "κ": r"\kappa", "λ": r"\lambda", "π": r"\pi", "ρ": r"\rho", "σ": r"\sigma", "τ": r"\tau", "φ": r"\phi",
        "χ": r"\chi", "₀": "_0", "₁": "_1", "₂": "_2", "²": "^2", "³": "^3", "⁵": "^5", "⁺": "^+", "⁻": "^-"}
TEXT = {"–": "--", "—": "---", "#": r"\#", "_": r"\_", "%": r"\%", "&": r"\&", "$": r"\$", "{": r"\{", "}": r"\}",
        "^": r"\^{}", "\\": r"\textbackslash{}", "Ĵ": r"$\hat{J}$", "“": "``", "…": r"\ldots{}", "”": "''", "’": "'", "‘": "`"}


def _math(s: str) -> str:
    return "".join(MATH.get(c, TEXT.get(c, c)) + (" " if c in MATH and MATH[c][-1].isalpha() else "") for c in s).strip()


GREEK_SUB = re.compile(r"([Α-ω])_(\w+)")   # χ_op -> $\chi_{\mathrm{op}}$
POWER = re.compile(r"\^\(([^)]*)\)|\^([0-9.]+)")      # k^(1−β), k^0.34 -> $^{...}$


def tex(s: str) -> str:
    """Escape text for LaTeX; runs of math symbols share one $...$; powers and Greek subscripts become math."""
    parts, last = [], 0
    for m in sorted(list(GREEK_SUB.finditer(s)) + list(POWER.finditer(s)), key=lambda m: m.start()):
        if m.start() < last:
            continue
        parts.append(_tex_plain(s[last:m.start()]))
        if m.re is GREEK_SUB:
            parts.append(f"${MATH[m.group(1)]}_{{\\mathrm{{{m.group(2)}}}}}$")
        else:
            parts.append("$^{" + _math(m.group(1) or m.group(2)) + "}$")
        last = m.end()
    parts.append(_tex_plain(s[last:]))
    return "".join(parts)


def _tex_plain(s: str) -> str:
    s = s.replace("k̂", "$\\hat{k}$").replace("̂", "")
    out, math = [], []
    for ch in s:
        if ch in MATH:
            math.append(MATH[ch] + (" " if MATH[ch][-1].isalpha() and MATH[ch].startswith("\\") else ""))
            continue
        if math:
            out.append("$" + "".join(math).strip() + "$"); math = []
        out.append(TEXT.get(ch, ch))
    if math:
        out.append("$" + "".join(math).strip() + "$")
    return "".join(out)


def house(s: str) -> str:
    """No 'holdout' and no 'gate' in the paper."""
    s = re.sub(r"\bnon-holdout\b", "non-reserved", s)
    s = s.replace("Holdout", "Reserved").replace("holdout", "reserved")
    s = s.replace("address-gated", "address-dependent").replace("read-out-gated", "read-out-coupled")
    s = re.sub(r"\bgating\b", "coupling", s); s = re.sub(r"\bgated\b", "filtered", s)
    s = re.sub(r"\bGated\b", "Filtered", s); s = re.sub(r"\bgates?\b", "filter", s)
    return s


def title_for(r) -> str:
    t = house(SHORT_TITLE.get(r["id"], r["title"]))
    return shorten(t, TITLE_MAX)


def shorten(s: str, n: int) -> str:
    """Cut at a clause boundary if it keeps at least half, else at a word boundary with an ellipsis."""
    if len(s) <= n:
        return s
    cut = max(s.rfind(sep, 0, n) for sep in ("; ", ", "))
    if cut >= n // 2:
        return s[:cut]
    w = s[:n - 2].rsplit(" ", 1)[0].rstrip(",;:")
    return w + "…"


def short_verdict(v: str) -> str:
    v = house(v).strip()
    if len(v) > VERDICT_MAX:
        v = re.sub(r"\s*\([^)]*\)", "", v).strip()
    if len(v) > VERDICT_MAX:
        v = v[:VERDICT_MAX - 1].rsplit(" ", 1)[0] + "…"
    return v


def load_rows() -> list[dict]:
    rows = []
    for mp in sorted(collect.HYP.glob("H*/summary/meta.json")):
        meta = json.loads(mp.read_text())
        v = meta.get("v2")
        if not v:
            continue
        hdir = mp.parent.parent
        text = (hdir / "README.md").read_text(errors="replace")
        title = text.splitlines()[0].lstrip("# ").strip().split(":", 1)[-1].strip()
        rows.append({"id": hdir.name.split("-")[0], "num": int(hdir.name.split("-")[0][1:]), "title": title,
                     "p": v["credence"], "V": v["value_if_true"], "EU": v["expected_usefulness"],
                     "M": v.get("mechanism_level", "M0"), "fragile": bool(v.get("fragile")),
                     "verdict": v.get("original_verdict", ""), "claim": v.get("claim", ""), "scope": v.get("scope")})
    rows.sort(key=lambda r: (-r["EU"], -r["p"], r["num"]))
    return rows


def pfmt(r):
    return f"{r['p']:.2f}" + (r"$^\ast$" if r["fragile"] else "")


def main():
    rows = load_rows()
    n = len(rows)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = [f"% Generated by writeup/figures/make_eu_table.py on {now} from hypotheses/H*/summary/meta.json (v2).",
         "% Do not edit by hand; edit meta.json or the script and re-run.",
         "% Verdict column: meta.json v2.original_verdict (house wording: 'reserved' data; parentheses dropped if > 40 chars).",
         r"\section{All hypotheses by estimated usefulness}\label{app:eu}",
         f"All {n} hypotheses, sorted by estimated usefulness EU $=pV$. $p$: credence (faithfulness); $V$: value if true (0--5); "
         "D: mechanism depth, how far the test reaches beyond a fit (0: a pattern that repeats across goal periods; "
         "1: the model's own signature is predicted and a rival model fails; 2: in addition, a natural experiment agrees "
         "and synthetic data recover the effect); $^\\ast$fragile; verdict: the hypothesis as originally posed, at its latest round. "
         "The scored claim for each is on its two-page summary in the compendium."]
    for b in range(0, n, PER):
        chunk = rows[b:b + PER]
        lo, hi = b + 1, b + len(chunk)
        cont = "" if b == 0 else " (continued)"
        L += [r"\begin{table}[!htbp]",  # appendix is one-column: a plain table can share the page with the heading
              rf"\caption{{Hypotheses ranked by estimated usefulness{cont}, ranks {lo}--{hi}.}}",
              r"\label{tab:eu}" if b == 0 else "",
              r"\scriptsize\renewcommand{\arraystretch}{0.95}",
              r"\begin{tabular}{@{}r l p{0.51\textwidth} c c c c l@{}}",
              r"\toprule \# & ID & hypothesis & $p$ & $V$ & EU & D & verdict\\ \midrule"]
        for k, r in enumerate(chunk, start=lo):
            L.append(f"{k} & {r['id']} & {tex(title_for(r))} & {pfmt(r)} & {r['V']:.2f} & "
                     f"{r['EU']:.2f} & {r['M'][1:]} & {tex(short_verdict(r['verdict']))}\\\\")
        L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    OUT.write_text("\n".join(L) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {n} cards in {(n + PER - 1) // PER} blocks")
    for k, r in enumerate(rows[:20], 1):
        print(k, r["id"], r["p"], r["V"], r["EU"], r["M"], "fragile" if r["fragile"] else "", "|", r["verdict"])


if __name__ == "__main__":
    main()
