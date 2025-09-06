from utils_normalize import normalize_fa
from utils_translit import expand_latin_acronyms
from domain_aliases import expand_domain_aliases

def generate_query_variants(q: str):
    qn = normalize_fa(q)
    variants = [qn]
    variants += expand_latin_acronyms(qn)
    variants += expand_domain_aliases(qn)
    # یکتا + حذف خیلی کوتاه‌ها
    seen, uniq = set(), []
    for v in variants:
        if len(v) >= 2 and v not in seen:
            uniq.append(v); seen.add(v)
    return uniq
