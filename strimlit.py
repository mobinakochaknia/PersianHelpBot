# app.py
import streamlit as st
from datetime import datetime
from main import get_clean_answer  # بک‌اند خودت

st.set_page_config(page_title="🤖 NRI Help Bot", page_icon="💬", layout="centered")

# ---------- استایل ساده ----------
st.markdown("""
<style>
    body { direction: rtl; text-align: right; }
    .chat-bubble { border-radius: 12px; padding: 10px; margin: 10px 0; }
    .user-msg { background-color: #d1ecf1; }
    .bot-msg { background-color: #e2f0cb; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 دستیار پاسخگوی کارمندان")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- نمایش پیام‌ها ----------
for msg in st.session_state.chat_history:
    msg_type = "user-msg" if msg["sender"] == "user" else "bot-msg"
    st.markdown(
        f"<div class='chat-bubble {msg_type}'>{msg['text']}</div>",
        unsafe_allow_html=True
    )

# ---------- ورودی کاربر ----------
user_input = st.text_input("✍️ سوال خود را بنویسید:")

if st.button("📨 ارسال") and user_input.strip():
    timestamp = datetime.now().strftime("%H:%M")

    # اضافه به تاریخچه
    st.session_state.chat_history.append({"sender": "user", "text": user_input, "time": timestamp})

    # پاسخ از بک‌اند
    bot_answer = get_clean_answer(user_input)

    st.session_state.chat_history.append({"sender": "bot", "text": bot_answer, "time": timestamp})

    st.rerun()

# ---------- دکمه پاک کردن ----------
if st.button("🗑️ پاک کردن گفتگو"):
    st.session_state.chat_history = []
    st.rerun()
