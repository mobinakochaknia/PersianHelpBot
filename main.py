from hybrid_pipeline import retrieve_hybrid   # ⬅️ به جای search_similarity
from useAPI import call_gemini
import re


def answer_user_query(query: str):
    # قبلاً: similar_items = find_similar_questions(query)
    similar_items = retrieve_hybrid(query, k_emb=50, k_fuzzy=100, k_final=5)  # ⬅️ هیبرید
    if not similar_items:
        return "هیچ مورد مشابهی یافت نشد. لطفاً با شماره 6060 تماس بگیرید."
    
    # خروجی retrieve_hybrid همون question/answer ها رو برمی‌گردونه
    return call_gemini(query, similar_items)


def clean_response(text):
    # حذف فاصله‌های بیش از یکی (اما نیم‌فاصله رو دست نزن)
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # حذف فاصله اشتباه بین حروف، فقط وقتی بینش نیم‌فاصله هست و فاصله افتاده
    text = re.sub(r'(?<=[\w])\s+(?=\u200c)', '', text)  # فاصله قبل نیم‌فاصله
    text = re.sub(r'(?<=\u200c)\s+(?=[\w])', '', text)  # فاصله بعد نیم‌فاصله

    # جایگزینی NBSP با فاصله معمولی
    text = text.replace('\xa0', ' ')

    # حذف کاراکترهای اضافی کنترلی
    text = text.replace('\r', '')
    text = text.replace('\u202c', '')

    # حذف فاصله قبل از نقطه یا ویرگول
    text = re.sub(r'\s+([.,،])', r'\1', text)

    return text.strip()


# گرفتن سوال از کاربر در زمان اجرا
if __name__ == "__main__":
    user_question = input("📝 لطفاً سوال خود را وارد کنید:\n> ")
    raw_output = answer_user_query(user_question)
    cleaned_output = clean_response(raw_output)
    print(cleaned_output)


def get_clean_answer(user_query: str):
    raw = answer_user_query(user_query)
    return clean_response(raw)
