from hybrid_pipeline import retrieve_hybrid
from useAPI import call_gemini
import re

def answer_user_query(query: str, state=None):
    # دریافت نتایج با هیبرید و کشِ از قبل آماده
    similar_items = retrieve_hybrid(query, state=state, k_emb=40, k_fuzzy=80, k_final=5)
    if not similar_items:
        return "هیچ مورد مشابهی یافت نشد. لطفاً با شماره 6060 تماس بگیرید."
    return call_gemini(query, similar_items)

def clean_response(text):
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'(?<=[\w])\s+(?=\u200c)', '', text)
    text = re.sub(r'(?<=\u200c)\s+(?=[\w])', '', text)
    text = text.replace('\xa0', ' ').replace('\r', '').replace('\u202c', '')
    text = re.sub(r'\s+([.,،])', r'\1', text)
    return text.strip()

def get_clean_answer(user_query: str, state=None):
    raw = answer_user_query(user_query, state=state)
    return clean_response(raw)

if __name__ == "__main__":
    user_question = input("📝 لطفاً سوال خود را وارد کنید:\n> ")
    print("\n✅ پاسخ نهایی:\n", get_clean_answer(user_question))
