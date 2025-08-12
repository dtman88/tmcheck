import re
from typing import List, Set, Optional


# Allow unicode word characters so tokens like "Nestlé" are captured.
# Tokens may contain internal dashes or apostrophes.
TOKEN_RE = re.compile(r"[\w]+(?:['’\-][\w]+)*", re.UNICODE)

# quoted phrases should be preserved verbatim
QUOTE_RE = re.compile(r'"([^"\n]+)"')

# common stopwords that do not carry trademark meaning on their own
STOPWORDS = {
    "the",
    "a",
    "an",
    "of",
    "for",
    "and",
    "or",
    "to",
    "with",
    "in",
    "christmas",
    "vs",
    "by",
    "tribute",
}

# words that are too generic to be useful when standing alone
GENERIC_SINGLE = {
    "gift",
    "t-shirt",
    "logo",
    "decal",
    "era",
    "tour",
    "tee",
    "gaming",
    "keyboard",
    "lovers",
    "case",
    "ornament",
    "program",
    "nightgown",
    "sweatshirt",
    "bundle",
    "quote",
    "chocolate",
    "space",
    "drone",
    "controller",
    "art",
    "shirt",
    "action",
    "shoes",
    "hoodie",
    "custom",
    "outfit",
    "mug",
    "wars",
    "endgame",
    "meme",
    "cola",
    "wallet",
    "sports",
    "fan",
    "club",
    "inspired",
    "legend",
    "racing",
    "parody",
    "mom",
    "dog",
    "version",
    "cute",
    "adult",
}

# tokens that often indicate a trademark‑relevant phrase when used as the
# second word of a bigram
RISK_TERMS = {
    "lovers",
    "logo",
    "decal",
    "tour",
    "keyboard",
    "princess",
    "ornament",
    "case",
    "program",
    "quote",
    "controller",
    "shirt",
    "action",
    "shoes",
    "hoodie",
    "outfit",
    "tee",
    "mug",
    "club",
    "legend",
    "mat",
    "mom",
}

# words that are ignored when appearing as the first token
GENERIC_FIRST = {"swift", "star", "coca"}

# words following a capitalised run that indicate the run should not emit
# individual tokens (e.g. "Harry Potter inspired").
RUN_FOLLOWERS = {"inspired", "fan"}

# bigrams should not be produced when starting with these generic words
BIGRAM_SKIP_FIRST = {"inspired", "cute"}


def extract_trademark_phrases(
    text: str,
    stopwords: Optional[Set[str]] = None,
    generic_single: Optional[Set[str]] = None,
    risk_terms: Optional[Set[str]] = None,
) -> List[str]:
    """Break *text* into a list of phrases for trademark inspection.

    The heuristic focuses on simple lexical cues: stopword removal, detection
    of uppercase/acronym tokens, and a handful of product keywords that
    commonly appear in risky phrases.  The function is intentionally light on
    dependencies so it can run in constrained environments.
    """

    def norm_token(t: str) -> str:
        # strip possessive/apostrophe endings
        if t.lower().endswith("'s") or t.lower().endswith("’s"):
            t = t[:-2]
        return t

    stopwords = stopwords or STOPWORDS
    generic_single = generic_single or GENERIC_SINGLE
    risk_terms = risk_terms or RISK_TERMS

    # capture and remove quoted phrases first
    quoted_phrases = [m.group(1).strip() for m in QUOTE_RE.finditer(text) if m.group(1).strip()]
    text = QUOTE_RE.sub(" ", text)

    tokens_raw = [m.group(0) for m in TOKEN_RE.finditer(text)]
    tokens = [norm_token(t) for t in tokens_raw]
    phrases: List[str] = []
    seen = set()

    def is_generic(word: str) -> bool:
        lw = word.lower()
        lw_singular = lw[:-1] if lw.endswith("s") and not lw.endswith("ss") else lw
        return lw in generic_single or lw_singular in generic_single

    def add(phrase: str) -> None:
        key = phrase.lower()
        if key not in seen and key not in stopwords:
            phrases.append(phrase)
            seen.add(key)

    def add_with_prefix(token: str) -> None:
        if '-' in token:
            prefix = token.split('-')[0]
            if prefix.isupper():
                add(prefix)
        add(token)

    n = len(tokens)
    has_cap_after_first = any(any(c.isupper() for c in t) for t in tokens[1:])

    # phrases of the form "X of Y" where X and Y are capitalised
    skip = set()
    for i in range(n - 2):
        if (
            tokens[i][0].isupper()
            and tokens[i + 1].lower() in {"of", "the"}
            and tokens[i + 2][0].isupper()
        ):
            add(f"{tokens[i]} {tokens[i + 1]} {tokens[i + 2]}")
            skip.update({i, i + 1, i + 2})

    # detect runs of consecutive capitalised words (allow digits in the run)
    i = 0
    while i < n:
        if i in skip:
            i += 1
            continue
        if (
            (
                tokens[i][0].isupper()
                and not tokens[i].isupper()
                or any(c.isupper() for c in tokens[i][1:])
            )
            and i + 1 < n
            and (tokens[i + 1][0].isupper() or tokens[i + 1].isdigit())
            and tokens[i + 1].lower() not in stopwords
        ):
            j = i + 2
            while (
                j < n
                and (tokens[j][0].isupper() or tokens[j].isdigit())
                and tokens[j].lower() not in stopwords
            ):
                j += 1
            run = tokens[i:j]
            # allow generic+risk bigrams to be handled later
            if (
                len(run) == 2
                and is_generic(run[0])
                and run[1].lower() in risk_terms
            ):
                i += 1
                continue
            prev_tok = tokens[i - 1].lower() if i else ""
            if any(t.isdigit() for t in run):
                if run[0].isupper() and len(run) >= 3:
                    add_with_prefix(run[0])
                    sub_run = run[1:]
                    add(" ".join(sub_run))
                    if len(sub_run) >= 2:
                        add(f"{sub_run[0]} {sub_run[1]}")
                else:
                    add(" ".join(run))
                skip.update(range(i, j))
                i = j
                continue
            else:
                # choose bigram from run
                if len(run) == 2:
                    if not is_generic(run[0]):
                        add(f"{run[0]} {run[1]}")
                else:
                    if run[0].lower() in GENERIC_FIRST or is_generic(run[0]):
                        if run[-1].lower() not in stopwords:
                            add(f"{run[0]} {run[1]}")
                    else:
                        add(f"{run[-2]} {run[-1]}")
            # add single tokens unless preceded by 'by' or follower word
            if prev_tok != "by" and not (j < n and tokens[j].lower() in RUN_FOLLOWERS):
                if len(run) == 2:
                    t = run[1]
                    if not is_generic(t):
                        add_with_prefix(t)
                else:
                    for offset, t in enumerate(run):
                        if is_generic(t):
                            continue
                        if i == 0 and offset == 0 and t.lower() in GENERIC_FIRST:
                            continue
                        add_with_prefix(t)
            skip.update(range(i, j))
            i = j
        else:
            i += 1

    for i, tok in enumerate(tokens):
        if i in skip:
            continue
        lower = tok.lower()
        prev_tok = tokens[i - 1] if i else ""
        next_tok = tokens[i + 1] if i + 1 < n else ""
        lower_singular = lower[:-1] if lower.endswith("s") and not lower.endswith("ss") else lower
        if lower in stopwords or is_generic(lower):
            continue

        if tok.isdigit():
            continue

        if i == 0 and lower in GENERIC_FIRST:
            continue

        if (
            next_tok
            and is_generic(next_tok)
            and next_tok.lower() not in risk_terms
            and not next_tok[0].isupper()
        ):
            add_with_prefix(tok)
            continue

        # include obvious acronyms
        if tok.isupper():
            add_with_prefix(tok)
            continue

        # include tokens with internal capitalisation (e.g. "iPhone")
        if any(c.isupper() for c in tok[1:]):
            add_with_prefix(tok)
            continue

        if i == 0 and tok[0].isupper() and not has_cap_after_first:
            if not (next_tok and next_tok.isdigit()):
                add_with_prefix(tok)
            continue

        if prev_tok.lower() in {"for", "and", "vs", "by"}:
            add_with_prefix(tok)
            continue

        if prev_tok and prev_tok[0].isupper() and not is_generic(lower):
            add_with_prefix(tok)
        elif tok[0].isupper() and prev_tok and not prev_tok[0].isupper():
            add_with_prefix(tok)

    # examine bigrams for notable combinations
    for i in range(n - 1):
        if i in skip and i + 1 in skip:
            continue
        t1, t2 = tokens[i], tokens[i + 1]
        t1_raw, t2_raw = tokens_raw[i], tokens_raw[i + 1]
        l1, l2 = t1.lower(), t2.lower()
        if l1 in BIGRAM_SKIP_FIRST:
            continue

        if l2 in stopwords:
            continue

        if l2 == "inspired" and i == 0 and t1[0].isupper():
            phrase = f"{t1_raw} {t2_raw}"
            if is_generic(l1):
                phrase = phrase.lower()
            add(phrase)
            continue

        if l2 == "version" and i == 0 and t1[0].isupper():
            phrase = f"{t1_raw} {t2_raw}"
            if is_generic(l1):
                phrase = phrase.lower()
            add(phrase)
            continue

        include = False

        # product keyword at the end (e.g. "logo decal", "cat lovers")
        if l2 in risk_terms:
            if not (l2 == "tee" and is_generic(l1) and not t1[0].isupper()):
                include = True

        elif t1[0].isupper() and t2.isdigit():
            include = True

        if include:
            phrase = f"{t1_raw} {t2_raw}"
            if i == 0 and is_generic(l1):
                phrase = phrase.lower()
            add(phrase)

    # detect phrases of the form "X vs Y" where X can be multi-word
    for i, tok in enumerate(tokens):
        if tok.lower() == "vs" and i > 0 and i + 1 < n:
            right = tokens[i + 1]
            if right[0].isupper():
                left_start = i - 1
                while (
                    left_start - 1 >= 0
                    and tokens[left_start - 1][0].isupper()
                    and not tokens[left_start - 1].isupper()
                ):
                    left_start -= 1
                left_phrase = " ".join(tokens[left_start:i])
                add(f"{left_phrase} vs {right}")

    for qp in quoted_phrases:
        add(qp)

    phrases = [p for p in phrases if p.lower() not in stopwords]
    return phrases

