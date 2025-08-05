from __future__ import annotations
import re
from typing import List

STOPWORDS = {
    'the','a','an','of','for','and','or','to','with','in','on','at','by','vs','vs.','from','as','is','are','be','into','that','this','these','those','&'
}
GENERIC_SINGLE = {
    'gift','t','t-shirt','tshirt','shirt','tee','mug','case','decal','logo','nightgown','ornament','bundle','controller','skin',
    'poster','outfit','aesthetic','hoodie','wallet','keychain','mat','shoes','shoe','fan','club','legend','racing','bundle','program',
    'tour','action','running','era','lovers','gown','inspired','drone','gaming','art','quote','space','program','shirt','keepsake','parody','version','lyric'
}
ALWAYS_SINGLE = {'cat','princess','keepsake','men','women','dog','goat'}
ALLOW_SINGLE_PROPER = {'Swift','Beatles'}
RISK_ENDINGS = {
    'logo','decal','case','keyboard','controller','ornament','bundle','mug','hoodie','poster','tee','shirt','gown','skin','wallet','keychain','gift','mat','shoes','shoe',
    'club','fan','legend','decal','program','tour','action','running','lovers','keepsake','inspired','aesthetic','outfit','shirt','mug'
}
RISK_TOKENS = RISK_ENDINGS | {'fan','club','logo','parody','meme','anime'}
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*")

def singularize(token: str) -> str:
    if token.endswith("’s") or token.endswith("'s"):
        token = token[:-2]
    if token.isupper() or token[0].isupper():
        return token
    if token.endswith('s') and len(token) > 3:
        return token[:-1]
    return token

def include_single(tokens: List[str], idx: int) -> bool:
    word = tokens[idx]
    lower = word.lower()
    if lower in STOPWORDS or lower in GENERIC_SINGLE:
        if lower not in ALWAYS_SINGLE:
            return False
    if word[0].isupper():
        prev_cap = idx>0 and tokens[idx-1][0].isupper()
        next_cap = idx+1 < len(tokens) and tokens[idx+1][0].isupper()
        if (prev_cap or next_cap) and word not in ALLOW_SINGLE_PROPER:
            return False
    if word.isupper() or word[0].isupper():
        return True
    if idx == 0:
        return True
    prev = tokens[idx-1]
    if prev.lower() in {'for','vs','by','and'}:
        return True
    if prev[0].isupper() or prev.isnumeric():
        return True
    if lower in ALWAYS_SINGLE:
        return True
    return False

def include_phrase(tokens: List[str]) -> bool:
    lowers = [t.lower() for t in tokens]
    if lowers[0] in STOPWORDS or lowers[-1] in STOPWORDS:
        return False
    if all(t in STOPWORDS for t in lowers):
        return False
    if all(t in GENERIC_SINGLE for t in lowers):
        if len(lowers) == 2 and lowers[1] in RISK_ENDINGS and lowers[0] not in RISK_ENDINGS:
            return True
        return False
    if any(t[0].isupper() or t.isupper() for t in tokens):
        return True
    if any(t.lower() in RISK_TOKENS for t in tokens):
        return True
    return False

def extract_trademark_phrases(text: str) -> List[str]:
    phrases: List[str] = []
    seen = set()
    for m in re.finditer(r'"([^"\n]+)"', text):
        q = m.group(1).strip()
        if q and q.lower() not in seen:
            phrases.append(q)
            seen.add(q.lower())
    text_clean = re.sub(r'"[^"\n]+"', '', text)
    tokens = [m.group(0) for m in WORD_RE.finditer(text_clean)]
    n = len(tokens)
    for i, tok in enumerate(tokens):
        if include_single(tokens, i):
            s = singularize(tok)
            if s and s.lower() not in seen:
                phrases.append(s)
                seen.add(s.lower())
    for size in range(2,6):
        for i in range(n - size + 1):
            gram_tokens = tokens[i:i+size]
            if include_phrase(gram_tokens):
                phrase = ' '.join(gram_tokens)
                key = phrase.lower()
                if key not in seen:
                    phrases.append(phrase)
                    seen.add(key)
    return phrases

if __name__ == "__main__":
    examples = [
        ("funny t-shirt for cat lovers", ["funny", "cat", "cat lovers"]),
        ("APPLE logo decal for MacBook", ["APPLE", "APPLE logo", "MacBook", "logo decal"]),
    ]
    for text, expected in examples:
        print(text, '->', extract_trademark_phrases(text))
