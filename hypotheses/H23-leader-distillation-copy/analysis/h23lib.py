"""H23 helpers: text normalization, plan-act coder, copy / transformation decomposition, lexical and embedding stats.

Copy information. Kolchinsky & Corominas-Murtra (2020), as read by H07 (`physics-models/DEFINITIONS.md`,
"Copy information (fork variant)"; not verified against the paper, which is not in literature/):
    I_copy = sum_x p(x) d( p(Y=x|X=x) || p_Y(x) ) 1[p(Y=x|X=x) > p_Y(x)],  d = binary KL (bits)
    I_transform = I(X;Y) - I_copy >= 0.
Sample-based estimates reuse H07's `mi_parts` / `decompose` (imported, not copied). `kc_joint` does the same
decomposition for a joint probability matrix (needed for the soft, situation-matched corpus -> leader channel) and is
checked against `mi_parts` in `self_test()`.

No text is written anywhere by this module.
"""
from __future__ import annotations

import datetime as dt
import math
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hypotheses/H07-rpg-forks/analysis"))
sys.path.insert(0, str(ROOT / "infra/shared"))
from h07lib import decompose, mi_parts  # noqa: E402,F401  (reused by import, per the card)

OUT = ROOT / "data/processed/H23-leader-distillation-copy"
SH = ROOT / "data/processed/shared"
UTC = dt.timezone.utc

# --------------------------------------------------------------------------------------------- time windows (#44)
# Checkpoint boundaries of the temporary leader (agent 28), from the operator's messages in #best.
CHECKPOINTS = [
    ("qwen-v3", dt.datetime(2026, 5, 26, 19, 15, 47, tzinfo=UTC)),
    ("qwen-v10", dt.datetime(2026, 5, 28, 17, 4, 46, tzinfo=UTC)),
    ("kimi-v2", dt.datetime(2026, 5, 28, 20, 4, 0, tzinfo=UTC)),
    ("kimi-v4-curated56", dt.datetime(2026, 5, 28, 20, 7, 10, tzinfo=UTC)),
    ("kimi-v7-aug-64", dt.datetime(2026, 5, 29, 18, 24, 51, tzinfo=UTC)),
]
LIVE_START = dt.datetime(2026, 5, 29, 18, 24, 51, tzinfo=UTC)   # v7-aug-64 deployed
LIVE_END = dt.datetime(2026, 5, 29, 21, 5, 0, tzinfo=UTC)       # end of the 05-29 window
FINETUNE_START = dt.datetime(2026, 5, 26, 17, 0, 33, tzinfo=UTC)
LEADER_AGENTS = {28, 30}
KIMI = 25
BEST_ROOM = 2
BASE_FIELD_GOALS = [38, 39, 40, 41, 42, 44]   # non-holdout regime-III periods with Kimi K2.6 present


def checkpoint_of(t: dt.datetime) -> str:
    name = "none"
    for n, t0 in CHECKPOINTS:
        if t >= t0:
            name = n
    return name


# --------------------------------------------------------------------------------------------- normalization
_AGENT_ALIASES = [
    "claude opus 4.8", "claude opus 4.7", "claude opus 4.6", "claude opus 4.5", "claude sonnet 4.6",
    "claude sonnet 4.5", "claude haiku 4.5", "gemini 3.5 flash", "gemini 3.1 pro", "gemini 2.5 pro", "gpt-5.5",
    "gpt-5.4", "gpt-5.2", "gpt-5.1", "gpt-5", "kimi k2.6", "deepseek-v3.2", "deepseek", "opus 4.8", "opus 4.7",
    "opus 4.6", "opus 4.5", "opus4.8", "opus4.7", "sonnet 4.6", "sonnet 4.5", "haiku 4.5", "gemini", "kimi", "k2.6",
    "claude", "opus", "flash", "[temporary] fine-tuned leader", "fine-tuned leader", "temporary leader", "leader",
]
_AGENT_RE = re.compile(r"(?<![\w.])(?:" + "|".join(re.escape(a) for a in sorted(_AGENT_ALIASES, key=len, reverse=True))
                       + r")(?![\w]|\.\d)")
_URI_RE = re.compile(r"tinker://\S+")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
_HASH_RE = re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")
_NUM_RE = re.compile(r"(?<![a-z<])\d+(?:[.,/:]\d+)*%?(?![a-z])")
_TOK_RE = re.compile(r"<agent>|<num>|<url>|<uri>|<hash>|<email>|<emoji>|[a-z][a-z0-9']*(?:[-_][a-z0-9']+)*|[@#]|—|–"
                     r"|\*\*|[!?]")
_EMOJI_RE = re.compile("[☀-➿\U0001f300-\U0001faff]")


def normalize(text: str, names: bool = True) -> str:
    s = (text or "").lower().replace("’", "'")
    s = _URI_RE.sub(" <uri> ", s)
    s = _URL_RE.sub(" <url> ", s)
    s = _EMAIL_RE.sub(" <email> ", s)
    s = _HASH_RE.sub(" <hash> ", s)
    if names:
        s = _AGENT_RE.sub(" <agent> ", s)
    s = _NUM_RE.sub(" <num> ", s)
    s = _EMOJI_RE.sub(" <emoji> ", s)
    return s


def tokens(text: str, names: bool = True) -> list[str]:
    return _TOK_RE.findall(normalize(text, names))


STOP = set("""a an the and or but if then so of to in on at for from by with as is are was were be been being it its
this that these those i me my we our us you your he she they them their what which who whom whose when where why how
all any both each few more most other some such no nor not only own same than too very can will just don't should now
do does did doing have has had having am would could ok okay also here there up down out over under again further
once into about against between through during before after above below off yes let let's i'm i'll we'll we're
you're it's that's there's <num> <url> <uri> <hash> <email> <emoji> @ # — – ** ! ?""".split())


def ngram_set(tok: list[str], n: int, content_only: bool = False) -> set:
    if n == 1:
        return {t for t in tok if (not content_only or (t not in STOP and len(t) > 2))}
    return {tuple(tok[i:i + n]) for i in range(len(tok) - n + 1)}


def ngram_counts(texts, n: int, content_only=False) -> Counter:
    c = Counter()
    for s in texts:
        tok = tokens(s)
        if n == 1:
            c.update(t for t in tok if (not content_only or (t not in STOP and len(t) > 2)))
        else:
            c.update(tuple(tok[i:i + n]) for i in range(len(tok) - n + 1))
    return c


# --------------------------------------------------------------------------------------------- plan-act coder
ACTS = ["DECIDE", "ASSIGN", "GATE", "REDIRECT", "ESCALATE", "REQUEST", "REPORT", "ACK", "STANDBY", "OTHER"]
DIRECTIVE = {"DECIDE", "ASSIGN", "GATE", "REDIRECT"}
COARSE = {"DECIDE": "DIRECT", "ASSIGN": "DIRECT", "GATE": "DIRECT", "REDIRECT": "DIRECT", "ESCALATE": "INFO",
          "REQUEST": "INFO", "REPORT": "INFO", "ACK": "SOCIAL", "STANDBY": "SOCIAL", "OTHER": "SOCIAL"}
COARSE_ACTS = ["DIRECT", "INFO", "SOCIAL"]
_VERBS = (r"take|own|draft|run|build|write|review|check|confirm|test|verify|validate|prep|prepare|pull|push|fix|"
          r"investigate|triage|start|finish|handle|create|implement|update|merge|document|log|report|ping|send|hold|"
          r"stop|pause|pair|lead|coordinate|set up|setup|add|expand|consolidate|look|sync|rebase|help|jump|focus|grab|"
          r"claim|spin up|sample|train|eval|evaluate|score|rerun|re-run|retrain|email|post|share|summarize|record|"
          r"wire|integrate|design|define|propose|keep|drop|revert|retry|debug|clear|reset|kick off|own|go|do|make|"
          r"cut|ship|block|lock|move|switch|close|open|prioriti[sz]e|split|draft|audit|diff|capture")
_P = {
    # coder v3 (2026-10-03): v1 fixed on a 40-item development set of non-leader text (corpus targets and #44 village
    # messages outside the leader's window) -> v2; v2 scored on a fresh blind 40-item test set (agreement 0.53);
    # systematic misses fixed -> v3; v3 scored on a third fresh blind 30-item set (see the card / coder_validation.json).
    "DECIDE": [r"\b(?:vote called|call(?:ing)? (?:a |the )?vote|let's vote|vote (?:now|time)|i vote|my vote|"
               r"(?:i )?(?:formally |officially )?cast (?:my|a)|keep-vote|decided|we(?:'ll| will)? go with|"
               r"going with|we ship|ship it|ship (?:conditionally|now)|we proceed|let's proceed|locked in|goal locked|"
               r"veto|final call|i'm calling|calling it|tie-?break|i (?:fully )?support|support (?:the|that|this) "
               r"(?:retrain|plan|deploy\w*|decision|proposal)|i (?:fully )?agree with the (?:consensus|plan|decision)|"
               r"approved|unanimous keep|we're going with|i recommend|recommend(?:ation)?:?\s+(?:we\s+)?(?:keep|deploy|ship|"
               r"go|use|retrain|iterate)|recommend keeping|my (?:final )?vote|(?:strongly )?support keep|"
               r"vote (?:keep|iterate|retrain|a|b)|we should (?:retrain|deploy|ship|keep|go with)|proposal:)\b",
               r"\b(?:vote|decision|recommendation)\s*:"],
    "ASSIGN": [rf"<agent>\s*(?:[,:—–-]+\s*|\s+)(?:please\s+|you\s+|can you\s+|could you\s+|go ahead and\s+|now\s+)?"
               rf"(?:{_VERBS})\b",
               rf"@\s*<agent>\s*(?:[,:—–-]+\s*)?(?:please\s+)?(?:{_VERBS})\b",
               r"\bassign(?:ment|ments|ed|ing)?\b", r"\byou're on\b", r"\btake point\b", r"\bowner\b",
               rf"(?:^|\n)\s*[•*-]?\s*<agent>\s*:\s*(?:{_VERBS})\b"],
    "GATE": [r"\b(?:hold (?:that|the|on)|on hold|blocked|pending|until|before (?:we|any|you|handoff|shipping|"
             r"deploying|sending|emailing|the|it|merging)|do not (?:send|ship|deploy|email|merge|push)|"
             r"don't (?:send|ship|deploy|email|merge|push)|no (?:deploy|handoff|ship|email)\b|(?<!-)gat(?:e|ed|ing)|"
             r"not without|only after|wait for (?:the )?(?:eval|results|validation|tests?|green))\b"],
    "REDIRECT": [r"\b(?:back to|our (?:actual |current |real )?goal|the goal is|current goal|goal check|refocus|"
                 r"focus on|re-?anchor|off-?goal|circling|going in circles|(?:in|stuck in) a (?:[\w-]+ )?loop|"
                 r"loop detected|stop (?:retrying|waiting|polling|speculating|the)|don't speculate|"
                 r"park (?:the|that|it)|parked|stay (?:aligned|on|anchored)|(?:we're|we are) drifting|goal anchor|"
                 r"restat(?:e|ing)|back on task)\b"],
    "ESCALATE": [r"^\s*admin\b[^\n]*\b(?:please|can you|could you|need|needs|restart|intervene|intervention|help)\b",
                 r"\b(?:escalat\w*|flag (?:it |this )?(?:for|to) (?:the )?admin|ask (?:the )?admin|"
                 r"admin,? (?:please|can you|could you|should))\b", r"\bemail (?:to )?<email>"],
    "REQUEST": [r"\?", r"\b(?:any (?:eta|update|updates|blockers|questions|objections)|what's your|thoughts|"
                r"let me know|can you confirm|please confirm|please (?:share|post|let)|confirm in chat)\b"],
    "REPORT": [r"<emoji>.*\b(?:pass|passing|passed|green|done|ready|complete)\b", r"<num>\s*(?:/\s*<num>|tests?\b|"
               r"passed|passing|failed|skipped|rows\b|commits?\b)",
               r"\b(?:passing|passed|pass|pushed|merged|committed|completed?|done|finished|ready|green|shipped|"
               r"deployed|validated|verified|status|update|results?|fixed|added|created|built|wrote|ran|resolved|"
               r"recorded|kicking off|kicked off|started|i've|i have|i'll|i will|i'm|we've)\b"],
    "ACK": [r"\b(?:thanks|thank you|great (?:work|job|close|catch|progress|call)|nice|well done|good (?:catch|work|call|"
            r"point)|agreed|agree|acknowledged|welcome|kudos|excellent|outstanding|brilliant|congrat\w*|"
            r"appreciate|got it|understood)\b", r"\+1"],
    "STANDBY": [r"\b(?:standing by|stand by|standby|waiting|hold(?:ing)? off|will wait|pausing|paused|idle|wound down|"
                r"wind down|watch for|monitor(?:ing)?)\b"],
}
_PC = {k: [re.compile(p) for p in v] for k, v in _P.items()}


def plan_acts(text: str) -> dict:
    """Multi-label plan acts (booleans) + 'primary' (first act in ACTS priority order that fires)."""
    s = normalize(text).replace("**", " ").replace("`", " ")
    s = re.sub(r"[ \t]+", " ", s)
    out = {a: any(p.search(s) for p in _PC[a]) for a in ACTS[:-1]}
    out["primary"] = next((a for a in ACTS[:-1] if out[a]), "OTHER")
    return out


# --------------------------------------------------------------------------------------------- copy / transform
def _bkl(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(a > 0, a * np.log2(a / b), 0.0)
        t2 = np.where(a < 1, (1 - a) * np.log2((1 - a) / (1 - b)), 0.0)
    return t1 + t2


def binary_kl(a: float, b: float) -> float:
    return float(_bkl(a, b))


def kc_joint(P: np.ndarray) -> dict:
    """K&CM decomposition for a joint distribution over a shared alphabet (rows X, cols Y)."""
    P = np.asarray(P, float)
    P = P / P.sum()
    px, py = P.sum(1), P.sum(0)
    E = np.outer(px, py)
    nz = P > 0
    I = float(np.sum(P[nz] * np.log2(P[nz] / E[nz])))
    diag = np.diag(P)
    a = np.divide(diag, px, out=np.zeros_like(px), where=px > 0)
    m = (px > 0) & (a > py)
    Ic = float(np.sum(px[m] * _bkl(a[m], py[m])))
    c = float(diag.sum())
    pe = float(np.sum(px * py))
    return {"I": I, "I_copy": Ic, "I_transform": I - Ic, "c": c, "c_chance": pe,
            "kappa": (c - pe) / (1 - pe) if pe < 1 else float("nan")}


def soft_channel(pc: np.ndarray, y: np.ndarray, k: int) -> np.ndarray:
    """Joint P(x, y) = mean_m pc[m, x] * 1[y_m = y]; pc: (n, k) rows sum to 1, y: (n,) ints in [0, k)."""
    Y = np.zeros((len(y), k))
    Y[np.arange(len(y)), y] = 1.0
    return (np.asarray(pc, float).T @ Y) / len(y)


def soft_channel_test(pc: np.ndarray, y: np.ndarray, k: int, n_null: int = 2000, seed: int = 0) -> dict:
    """Observed decomposition and shuffle null (y permuted across messages)."""
    obs = kc_joint(soft_channel(pc, y, k))
    rng = np.random.default_rng(seed)
    nul = {key: [] for key in obs}
    for _ in range(n_null):
        r = kc_joint(soft_channel(pc, rng.permutation(y), k))
        for key in obs:
            nul[key].append(r[key])
    out = dict(obs)
    for key in ("I", "I_copy", "I_transform", "c", "kappa"):
        arr = np.array(nul[key])
        out[f"{key}_null"] = float(arr.mean())
        out[f"{key}_ex"] = obs[key] - float(arr.mean())
        out[f"{key}_p"] = float((np.sum(arr >= obs[key]) + 1) / (len(arr) + 1))
    return out


def sample_channel_test(x: list, y: list, n_null: int = 2000, seed: int = 0) -> dict:
    """K&CM on paired samples via H07's decompose (+ one-sided shuffle p-values)."""
    out = decompose(x, y, n_null=0)
    codes: dict = {}
    xi = np.array([codes.setdefault(v, len(codes)) for v in x], dtype=np.int64)
    yi = np.array([codes.setdefault(v, len(codes)) for v in y], dtype=np.int64)
    rng = np.random.default_rng(seed)
    nul = np.array([mi_parts(xi, rng.permutation(yi)) for _ in range(n_null)])  # c, kappa, I, Icopy
    names = ["c", "kappa", "I", "I_copy"]
    obs = [out["c"], out["kappa"], out["I"], out["I_copy"]]
    for j, nm in enumerate(names):
        out[f"{nm}_null"] = float(np.nanmean(nul[:, j]))
        out[f"{nm}_ex"] = obs[j] - out[f"{nm}_null"]
        out[f"{nm}_p"] = float((np.sum(nul[:, j] >= obs[j]) + 1) / (len(nul) + 1))
    it = nul[:, 2] - nul[:, 3]
    out["I_transform_null"] = float(it.mean())
    out["I_transform_ex"] = out["I_transform"] - float(it.mean())
    out["I_transform_p"] = float((np.sum(it >= out["I_transform"]) + 1) / (len(it) + 1))
    return out


# --------------------------------------------------------------------------------------------- lexical
def log_odds_z(ca: Counter, cb: Counter, prior: Counter, a0: float = 1000.0) -> dict:
    """Monroe, Colaresi & Quinn (2008) log-odds with an informative Dirichlet prior; z > 0 favors A."""
    n_a, n_b = sum(ca.values()), sum(cb.values())
    n_p = sum(prior.values()) or 1
    out = {}
    for w in set(ca) | set(cb):
        al = a0 * (prior.get(w, 0) + 0.5) / n_p
        ya, yb = ca.get(w, 0), cb.get(w, 0)
        d = math.log((ya + al) / (n_a + a0 - ya - al)) - math.log((yb + al) / (n_b + a0 - yb - al))
        out[w] = d / math.sqrt(1 / (ya + al) + 1 / (yb + al))
    return out


def copy_fraction(text: str, ref: set, n: int, content_only: bool = False) -> float:
    g = ngram_set(tokens(text), n, content_only)
    return len(g & ref) / len(g) if g else float("nan")


def marker_rate(text: str, markers1: set, markers2: set) -> float:
    """Corpus-distinctive unigram + bigram occurrences per 100 tokens."""
    tok = tokens(text)
    if not tok:
        return float("nan")
    hits = sum(1 for t in tok if t in markers1) + sum(1 for i in range(len(tok) - 1) if (tok[i], tok[i + 1]) in markers2)
    return 100.0 * hits / len(tok)


# --------------------------------------------------------------------------------------------- tests
def perm_mean_diff(a: np.ndarray, b: np.ndarray, n: int = 10000, seed: int = 0) -> dict:
    """One-sided permutation test of mean(a) > mean(b)."""
    a = np.asarray(a, float)[~np.isnan(a)]
    b = np.asarray(b, float)[~np.isnan(b)]
    obs = a.mean() - b.mean()
    pool = np.r_[a, b]
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(n):
        rng.shuffle(pool)
        cnt += (pool[:len(a)].mean() - pool[len(a):].mean()) >= obs - 1e-12
    return {"diff": float(obs), "p": (cnt + 1) / (n + 1), "n_a": len(a), "n_b": len(b),
            "mean_a": float(a.mean()), "mean_b": float(b.mean())}


def jsd(p: np.ndarray, q: np.ndarray) -> float:
    p = np.asarray(p, float) / np.sum(p)
    q = np.asarray(q, float) / np.sum(q)
    m = (p + q) / 2

    def kl(u, v):
        nz = u > 0
        return float(np.sum(u[nz] * np.log2(u[nz] / v[nz])))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def profile(primaries: list[str], smooth: float = 0.0) -> np.ndarray:
    c = Counter(primaries)
    v = np.array([c.get(a, 0) for a in ACTS], float) + smooth
    return v / v.sum()


def cos(a, b) -> float:
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def cos_rows(Z: np.ndarray, v: np.ndarray) -> np.ndarray:
    Z = np.asarray(Z, float)
    return (Z @ v) / (np.linalg.norm(Z, axis=1) * np.linalg.norm(v) + 1e-12)


def self_test():
    """kc_joint agrees with H07's mi_parts on the empirical joint of paired samples."""
    rng = np.random.default_rng(3)
    x = rng.integers(0, 5, 400)
    y = np.where(rng.random(400) < 0.5, x, (x + 1) % 5)
    c, kappa, I, Ic = mi_parts(x, y)
    P = np.zeros((5, 5))
    np.add.at(P, (x, y), 1)
    r = kc_joint(P)
    assert abs(r["I"] - I) < 1e-9 and abs(r["I_copy"] - Ic) < 1e-9 and abs(r["c"] - c) < 1e-9, (r, I, Ic, c)
    # pure copy and pure permutation
    Pc = np.eye(4) / 4
    Pp = np.roll(np.eye(4), 1, axis=1) / 4
    rc, rp = kc_joint(Pc), kc_joint(Pp)
    assert abs(rc["I_copy"] - 2) < 1e-9 and abs(rc["I_transform"]) < 1e-9
    assert abs(rp["I_copy"]) < 1e-9 and abs(rp["I_transform"] - 2) < 1e-9
    acts = plan_acts("Claude Opus 4.8, run the eval now. Vote: ship after it passes?")
    assert acts["primary"] == "DECIDE" and acts["ASSIGN"] and acts["REQUEST"]
    return True


if __name__ == "__main__":
    print("self_test", self_test())
