def expand_domain_aliases(query: str):
    q = query.lower()
    ALIASES = {
        "bpms": ["بی‌پی‌ام‌اس","بی پی ام اس","سامانه فرایندها","سیستم مدیریت فرایند"],
        "crm": ["سی آر ام","سی‌آر‌ام","مدیریت ارتباط با مشتری"],
        "hr": ["اچ آر","اچ‌آر","منابع انسانی","سیستم منابع انسانی"],
    }
    extra = []
    for k, vals in ALIASES.items():
        if k in q or any(v in q for v in vals):
            extra += vals
    # یکتا
    seen, uniq = set(), []
    for v in extra:
        if v not in seen:
            uniq.append(v); seen.add(v)
    return uniq
