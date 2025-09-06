import re
LATIN_LETTER_TO_FA = {
    'a':'ای','b':'بی','c':'سی','d':'دی','e':'ای','f':'اف','g':'جی','h':'اچ','i':'آی',
    'j':'جی','k':'کی','l':'اِل','m':'اِم','n':'اِن','o':'او','p':'پی','q':'کیو',
    'r':'آر','s':'اِس','t':'تی','u':'یو','v':'وی','w':'دابلیو','x':'اکس','y':'وای','z':'زِد'
}
SHORT_FA = {'s':'اس','m':'ام','n':'ان','r':'ار','b':'ب','p':'پ','c':'سی','t':'ت','h':'اچ'}

def latin_acronym_to_fa(token: str):
    if not re.fullmatch(r"[A-Za-z0-9\-_/\.]+", token or ""):
        return []
    letters = [ch.lower() for ch in re.sub(r"[^A-Za-z]", "", token)]
    if not letters: return []
    long_form  = "‌".join(LATIN_LETTER_TO_FA.get(ch, ch) for ch in letters)  # با نیم‌فاصله
    short_form = " ".join(SHORT_FA.get(ch, LATIN_LETTER_TO_FA.get(ch, ch)) for ch in letters)
    variants = {
        long_form, long_form.replace("‌"," "), long_form.replace("‌",""),
        short_form, short_form.replace(" ",""), short_form.replace(" ","‌")
    }
    return [v for v in variants if v]

def expand_latin_acronyms(query: str):
    tokens = re.split(r"\s+", query.strip())
    out = []
    for tok in tokens:
        out += latin_acronym_to_fa(tok)
    # یکتا
    seen, uniq = set(), []
    for v in out:
        if v not in seen:
            uniq.append(v); seen.add(v)
    return uniq
