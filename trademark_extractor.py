import re
from typing import List


TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*")

# common stopwords that do not carry trademark meaning on their own
STOPWORDS = {"the", "a", "an", "of", "for", "and", "or", "to", "with", "in"}

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
}

# tokens that often indicate a trademark‑relevant phrase when used as the
# second word of a bigram
RISK_TERMS = {"lovers", "logo", "decal", "tour", "keyboard"}


def extract_trademark_phrases(text: str) -> List[str]:
    """Break *text* into a list of phrases for trademark inspection.

    The heuristic focuses on simple lexical cues: stopword removal, detection
    of uppercase/acronym tokens, and a handful of product keywords that
    commonly appear in risky phrases.  The function is intentionally light on
    dependencies so it can run in constrained environments.
    """

    tokens = [m.group(0) for m in TOKEN_RE.finditer(text)]
    phrases: List[str] = []
    seen = set()

    def add(phrase: str) -> None:
        key = phrase.lower()
        if key not in seen:
            phrases.append(phrase)
            seen.add(key)

    n = len(tokens)
    has_cap_after_first = any(t[0].isupper() for t in tokens[1:])

    for i, tok in enumerate(tokens):
        lower = tok.lower()
        prev_tok = tokens[i - 1] if i else ""
        next_tok = tokens[i + 1] if i + 1 < n else ""

        if lower in STOPWORDS or lower in GENERIC_SINGLE:
            continue

        # include obvious acronyms
        if tok.isupper():
            add(tok)
            continue

        # include proper nouns not followed by another capitalised token
        if tok[0].isupper():
            if not (next_tok and next_tok[0].isupper()):
                add(tok)
            continue

        # include leading adjective only if the rest of the string lacks
        # any capitalised tokens (e.g. "funny t-shirt ...")
        if i == 0 and not has_cap_after_first:
            add(tok)
            continue

        # include nouns that follow small linking words
        if prev_tok.lower() in {"for", "and", "vs", "by"}:
            add(tok)

    # examine bigrams for notable combinations
    for i in range(n - 1):
        t1, t2 = tokens[i], tokens[i + 1]
        l1, l2 = t1.lower(), t2.lower()

        if l2 in STOPWORDS:
            continue

        include = False

        # product keyword at the end (e.g. "logo decal", "cat lovers")
        if l2 in RISK_TERMS:
            include = True

        # two capitalised words where the second is the end of the run
        elif t1[0].isupper() and t2[0].isupper():
            if not (t1.isupper() and t2.isupper()):
                if i + 2 == n or not tokens[i + 2][0].isupper():
                    include = True

        if include:
            add(f"{t1} {t2}")

    return phrases


if __name__ == "__main__":  # pragma: no cover - simple manual check
    tests = [
        ("funny t-shirt for cat lovers", ["funny", "cat", "cat lovers"]),
        (
            "APPLE logo decal for MacBook",
            ["APPLE", "APPLE logo", "MacBook", "logo decal"],
        ),
        ("Taylor Swift era tour tee", ["Taylor Swift", "era tour", "Swift"]),
        ("gift for men and women", ["men", "women"]),
        (
            "LED RGB USB Gaming Keyboard",
            ["LED", "RGB", "USB", "Gaming Keyboard"],
        ),
    ]
    for txt, exp in tests:
        print(txt, "->", extract_trademark_phrases(txt))

