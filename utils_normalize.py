import re
ARABIC_TO_PERSIAN = str.maketrans({"ي":"ی","ك":"ک","ؤ":"و","أ":"ا","إ":"ا","ۀ":"ه"})
DIACRITICS_PATTERN = re.compile(r"[\u064B-\u065F\u0670\u06D6-\u06ED]")

def normalize_fa(text: str) -> str:
    if not text: return ""
    text = text.replace("\u200c", " ").replace("\xa0"," ").strip()
    text = text.translate(ARABIC_TO_PERSIAN)
    text = DIACRITICS_PATTERN.sub("", text)           # حذف اعراب
    text = re.sub(r"ـ+", "", text)                    # کشیده
    text = re.sub(r"\s+", " ", text)                  # فاصله‌های اضافی
    text = re.sub(r"\s+([.,،:;?!»])", r"\1", text)    # فاصله قبل علائم
    text = re.sub(r"([«(])\s+", r"\1", text)          # فاصله بعد از « یا (
    return text
