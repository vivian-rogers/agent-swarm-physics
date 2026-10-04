"""Shared helpers for H24 (scheme, analysis, confirmatory script).

Everything that defines an observable lives here, so the exploratory analysis and the confirmatory
script use the same rules. No agent text is ever written to committed files; text is only read from
the gitignored sidecars under data/.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT, mention_regexes  # noqa: E402,F401

H24 = ROOT / "data/processed/H24-forecast-coupling-switch"
CARD = ROOT / "hypotheses/H24-forecast-coupling-switch"

# ---------------------------------------------------------------------------------------------
# Switch-on rule (fixed 2026-10-03 from the #21 record, before any alignment outcome was computed)
# ---------------------------------------------------------------------------------------------
# tau_intent: start of the agent's first computer session whose self-written intention says it will
#             read / review / compare teammates' work (or check its mail for teammates' shared docs).
# tau_record: first computer-use turn whose reasoning names another present agent in the same
#             sentence as a document word and an access verb (contemporaneous with the screenshot).
# tau_i     : tau_intent if a record event follows within CONFIRM_MIN minutes; else the first record
#             event after tau_intent... else None (agent never coupled through documents).
READ_RE = re.compile(
    r"(?i)\b(review|read|compar|divergen|look (?:at|over)|go through|analy[sz])\w*\b[^.;]{0,60}"
    r"\b(teammates?'?|team'?s?|others'?|colleagues?|shared|their)\b"
    r"|\b(begin|start|continue|resume)\w*\b[^.;]{0,30}\bphase 3\b"
    r"|\bcheck\w* (?:e-?mail|gmail|inbox)[^.;]{0,60}\b(shared|teammates?'?|from (?:the )?team)\b"
    r"|\bdivergence matrix\b")
ACCESS_RE = re.compile(r"(?i)\b(I can see|I see|show\w*|display\w*|open\w*|read\w*|view\w*|review\w*|"
                       r"scroll\w*|search\w*|find|found|locat\w*|access\w*|load\w*)\b")
DOC_RE = re.compile(r"(?i)(forecast|prediction|calibration|divergence|matrix|scenario|probabilit)")
STALE_RE = re.compile(r"(?i)(substack|repository|schr.dinger|comment|blog|post-mortem|farewell)")
CONFIRM_MIN = 60
# Clauses that defer or negate reading (reading planned for later) or describe outgoing sharing.
NEG_CLAUSE_RE = re.compile(r"(?i)\b(before|independen\w*|privat\w*|later|prepar\w*|without|avoid\w*|don'?t|do not|"
                           r"share my|sharing my|send my|email my|grant)\b")
CLAUSE_SPLIT = re.compile(r"(?:[.;:]\s+|,\s+|\s+and\s+|\s+then\s+|\s+-\s+|\(\w\)\s*)")
OUTGOING_RE = re.compile(r"(?i)(\bmy (?:own )?(?:doc|document|forecast|link|sheet|tracker|file)|\bgrant|share (?:the |my |a )?link|"
                         r"copy (?:the |its |my )?(?:share )?link|\bsend (?:my|the|a)\b|email (?:[\w.]+ ){0,4}(?:my|the|a) "
                         r"(?:doc|link)|\breply|\brespond)")


def intention_reads(text: str) -> bool:
    """True if a self-written intention plans to read/review/compare teammates' work (a non-negated clause)."""
    for clause in CLAUSE_SPLIT.split(text or ""):
        if clause and READ_RE.search(clause) and not NEG_CLAUSE_RE.search(clause):
            return True
    return False


def record_reads(sentence: str) -> bool:
    """A reasoning sentence that describes accessing a document-like object (names checked by the caller)."""
    return bool(DOC_RE.search(sentence) and ACCESS_RE.search(sentence) and not STALE_RE.search(sentence)
                and not OUTGOING_RE.search(sentence))

# ---------------------------------------------------------------------------------------------
# Statement flags
# ---------------------------------------------------------------------------------------------
PCT_RE = re.compile(r"\b\d{1,3}(?:\.\d+)?\s?%")
FORECAST_RE = re.compile(r"(?i)(forecast|predict|probabilit|scenario|\bAGI\b|superintellig|\bASI\b|\bTAI\b|"
                         r"p\(doom\)|timeline|by 20[2-9]\d|resolv)")
COMPARISON_RE = re.compile(r"(?i)(divergen|consensus|converg|team'?s?\b|teammates?|compar|matrix|average|median|"
                           r"weighted|aggregat|\bvs\.?\b|versus|spread|cross-framework)")


def other_agent_hits(text: str, me: int, pats: dict, present: list[int]) -> list[int]:
    return [b for b in present if b != me and b in pats and pats[b].search(text)]


# ---------------------------------------------------------------------------------------------
# Numeric forecast extraction (anchor questions shared across agents)
# ---------------------------------------------------------------------------------------------
QUESTIONS = {
    # question: (topic regex, year regex or None). Topic regexes avoid \b so that "AGI_by_2035" matches.
    "AGI2035": (r"(?<![A-Za-z])AGI(?![A-Za-z])", r"2035"),
    "SI2050": (r"(?<![A-Za-z])A?SI(?![A-Za-z])|(?i:superintellig)", r"2050"),
    "DOOM2100": (r"(?i:p\(doom|doom|extinction|existential|x-risk)", None),
    "DEPLOY2026": (r"(?i:deploy|F500|Fortune 500|enterprise)", r"2026"),
    "SECINC2026": (r"(?i:security incident|secincident)", r"2026"),
    "TREATY2030": (r"(?i:treaty)", r"2030"),
    "BREAK2030": (r"(?i:breakthrough)", r"2030"),
}
ANCHORS = ["AGI2035", "SI2050", "DOOM2100"]
TIER1 = ["AGI2035", "SI2050", "DOOM2100", "DEPLOY2026", "SECINC2026", "TREATY2030", "BREAK2030"]
# A sentence is attributed to its author only if it carries no marker of someone else's number.
OTHER_MARK_RE = re.compile(
    r"(?i)(\b(GA|TH|FR|CA|CEA)\b|consensus|\bteam\b|average|weighted|their|\bvs\.?\b|versus|spread|"
    r"\brange\b|divergen|metaculus|\bOrd\b|christiano|cotra|shulman|forecasters|experts?\b|survey|leaders|lecun|"
    r"yudkowsky|amodei|yampolskiy|altman|hassabis|kokotajlo|ai 2027|\|\s*[A-Za-z]|\bgiven\b|conditional|\bif\b|"
    r"scenario [a-d1-9]\b|lens|\bpp\b|[+−]\d+(?:\.\d+)?\s?pp)")
ARROW_RE = re.compile(r"(→|->|⇒|\bto\s+(?=\d{1,3}(?:\.\d+)?\s?%)|\bnow\s+(?=\d)|increas\w* to|decreas\w* to|moves? to)")
SELF_MARK_RE = re.compile(r"(?i)\b(my|I|I'm|I've|mine|me|our own)\b")
NUM_RE = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d+)?)(?:\s?[-–]\s?(\d{1,3}(?:\.\d+)?))?\s?%")
SENT_SPLIT = re.compile(r"(?:\n+|(?<=[.;!?])\s+(?=[A-Z*#(])|\s+[-•*]\s+|\s\|\s|\*\*)")


def _pairs(part: str):
    """(question, value, is_range) pairs in one comma-free part."""
    out = []
    for q, (topic, year) in QUESTIONS.items():
        mt = re.search(topic, part)
        if not mt:
            continue
        if year:
            ys = [m.start() for m in re.finditer(year, part)]
            if not ys:
                continue
            anchor = min(ys, key=lambda y: abs(y - mt.end()))
        else:
            if re.search(r"\b20[2-9]\d\b", part) and "2100" not in part:
                continue
            anchor = mt.end()
        nums = list(NUM_RE.finditer(part))
        if not nums:
            continue
        arrow = ARROW_RE.search(part)
        if arrow:  # an update: take the first number after the arrow
            after = [m for m in nums if m.start() >= arrow.start()]
            if not after:
                continue
            m = after[0]
        else:
            after = [m for m in nums if m.start() >= anchor]
            m = after[0] if after else min(nums, key=lambda mm: abs(mm.start() - anchor))
        lo = float(m.group(1)); hi = float(m.group(2)) if m.group(2) else lo
        if not (0 <= lo <= hi <= 100):
            continue
        out.append((q, (lo + hi) / 2, hi > lo, bool(arrow)))
    return out


# Amendment A1 (2026-10-03, after the first real-data run and a hand audit of the first/last values):
# short agent names ("Opus's", "Haiku's") were missed by the strict roster aliases, and thresholds,
# complements and worked examples were read as forecasts. The amended extractor (strict=True) adds the
# markers below; the pre-registered extractor (strict=False) is kept and reported alongside.
FAMILY_TOKENS = {"Claude 3.7 Sonnet": r"3\.7", "Gemini 2.5 Pro": r"Gemini 2\.5|2\.5 Pro", "GPT-5": r"GPT-?5(?![.\d])",
                 "Claude Sonnet 4.5": r"Sonnet 4\.5|(?<!3\.7 )Sonnet(?! 4\.5)", "Claude Haiku 4.5": r"Haiku",
                 "GPT-5.1": r"GPT-?5\.1", "Gemini 3 Pro": r"Gemini 3|Gemini(?! 2)", "Claude Opus 4.5": r"Opus",
                 "DeepSeek-V3.2": r"DeepSeek"}
STRICT_MARK_RE = re.compile(
    r"(?i)(example|e\.g\.|target|threshold|below|above|at least|more than|less than|over \d|under \d|[<>≥≤]|"
    r"\d%\+|without|navigat|success rate|chance of no|\bno\b|assum|trigger|would|could|suppose|hypothetic|"
    r"\bvs\b|compared|between|your\b|you\b)")


def loose_other_pats(me_name: str, present_names: list[str]) -> list:
    """Short-name patterns for the other present agents (Opus, Haiku, ...), excluding the speaker's own tokens."""
    out = []
    for nm in present_names:
        if nm == me_name or nm not in FAMILY_TOKENS:
            continue
        out.append(re.compile(FAMILY_TOKENS[nm]))
    return out


def extract_numbers(text: str, other_pats: list, strict: bool = False) -> list[dict]:
    """Numeric anchor forecasts in one message or typed chunk.

    attribution, per sentence:
      'self'      no marker of another source in the sentence, and either the whole message names no other
                  present agent or the sentence has a first-person marker;
      'other'     the sentence names another present agent or carries an aggregate / external / conditional marker;
      'ambiguous' otherwise (the message names other agents, the sentence has no first-person marker).
    """
    msg_names_other = any(p.search(text) for p in other_pats)
    out = []
    for sent in SENT_SPLIT.split(text):
        if not sent or "%" not in sent or len(sent) > 800:
            continue
        names_other = any(p.search(sent) for p in other_pats)
        marked = bool(OTHER_MARK_RE.search(sent)) or (strict and bool(STRICT_MARK_RE.search(sent)))
        selfm = bool(SELF_MARK_RE.search(sent))
        if names_other or marked:
            attr = "other"
        elif msg_names_other and not selfm:
            attr = "ambiguous"
        else:
            attr = "self"
        for part in re.split(r",\s+|;\s+|\s+and\s+(?=P\()", sent):
            for q, v, is_range, upd in _pairs(part):
                out.append({"question": q, "value": v, "is_range": is_range, "is_update": upd,
                            "attribution": attr, "self_marker": selfm})
    return out


# ---------------------------------------------------------------------------------------------
# Content statistics
# ---------------------------------------------------------------------------------------------
def unit(x, axis=-1):
    n = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.where(n > 0, n, 1)


def project_out(X, G):
    """Remove the span of the rows of G (k x n, orthonormalized here) from each row of X."""
    if G is None or len(G) == 0:
        return X
    Q, _ = np.linalg.qr(np.asarray(G, dtype=np.float64).T)
    return X - (X @ Q) @ Q.T


def alignment_stats(V):
    """V: agents x n segment vectors (already unit). Returns mean pairwise cosine and polarization |m|."""
    V = unit(V)
    N = len(V)
    C = V @ V.T
    A = (C.sum() - np.trace(C)) / (N * (N - 1))
    m = np.linalg.norm(V.mean(0))
    return float(A), float(m)


def betaJ_snapshot(A, N):
    """Mean-field O(n) linear response for a snapshot of N unit spins with mean pairwise cosine A
    (field removed): N<|m|^2> = 1 + (N-1)A = 1/(1 - betaJ0/n)  =>  betaJ0/n = 1 - 1/(1 + (N-1)A).
    Negative A gives a negative (antiferro-like) value; reported as is."""
    R = 1 + (N - 1) * A
    return float(1 - 1 / R) if R > 0 else float("-inf")
