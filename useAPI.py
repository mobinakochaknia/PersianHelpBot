import requests

API_KEY = "AIzaSyApv9j5S6ZgwxOA1LnGi-lN1JNDnCHPsuw"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def generate_payload(user_question, context_qa_list):
    if not context_qa_list:
        # فقط پیام مستقیم بده اگر هیچ داده‌ای نیست
        fallback_prompt = f"""کاربر پرسیده:
«{user_question}»

متاسفانه اطلاعات کافی برای پاسخ دقیق به این سوال در اختیار ندارم. لطفاً برای دریافت راهنمایی با شماره 60 60 تماس بگیرید."""
        return {
            "contents": [
                {
                    "parts": [
                        {"text": fallback_prompt}
                    ]
                }
            ]
        }

    # اگر context داریم → پرامپت کامل بساز
    context_text = "\n".join(
        [f"- سوال: {item['question']}\n  پاسخ: {item['answer']}" for item in context_qa_list]
    )

    prompt = f"""تو نقش یک اپراتور پاسخ‌گوی اداری در یک شرکت هستی و باید به سوالات کارکنان درباره فرآیندها، فرم‌ها و مشکلات رایج پاسخ بدی. کاربر ازت پرسیده:

«{user_question}»

با توجه به اطلاعات زیر، یک پاسخ دقیق، رسمی و قابل‌فهم تولید کن. اگر سوال پیرو سؤال قبلی یا ابهام در پاسخ‌های قبلی بود (مثل «منظورت چیه؟» یا «منوی کشویی کجاست؟»)، سعی کن واضح‌تر، ساده‌تر و مرحله‌به‌مرحله توضیح بدی.

اگر باز هم اطلاعات کافی برای پاسخ نداری، محترمانه بگو که بهتره با شماره 60 60 تماس بگیرن.

اطلاعات موجود:
{context_text}

در پایان پاسخ حتماً بنویس:
«برای اطلاعات بیشتر می‌تونی به این لینک مراجعه کنی.»

هدف: کمک به کارمند برای درک بهتر، با پاسخ ساده و کاربردی.
"""
    return {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }


def call_gemini(user_question, context_qa_list):
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": API_KEY
    }

    payload = generate_payload(user_question, context_qa_list)
    response = requests.post(GEMINI_URL, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "⚠️ ساختار پاسخ غیرمنتظره بود."
    else:
        return f"❌ خطای API: {response.status_code}\n{response.text}"



