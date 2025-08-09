import streamlit as st
from datetime import datetime
from main import get_clean_answer

# ---------- تنظیمات اولیه (کاملاً مشابه کد شما) ----------
st.set_page_config(page_title="NRI help bot", page_icon="💬", layout="centered")


# ---------- استایل‌ها (کاملاً مشابه کد شما) ----------
def apply_theme(theme):
    font_url = "https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css"
    st.markdown(f'<link href="{font_url}" rel="stylesheet">', unsafe_allow_html=True)

    if theme == "روشن":
        st.markdown("""
        <style>
        h1 { color: #a40000 !important; }
        * { font-family: Vazir, sans-serif !important; }
        .chat-bubble-user { background-color: rgb(164, 0, 0 , 1); color: #f0f0f0; }
        .chat-bubble-bot { background-color: #f0f0f0; color: black; }
        .stApp, .stTextInput label, .stSelectbox label { color: black !important; }
        .stButton>button { background-color: #f0f0f0; color: black; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        * { font-family: Vazir, sans-serif !important; }
        .stApp { background-color: #5E5E5E; color: #f1f1f1; }
        .chat-bubble-user { background-color: #0a84ff; color: white; }
        .chat-bubble-bot { background-color: #2c2c2c; color: white; }
        .stTextInput label, .stSelectbox label { color: #f1f1f1 !important; }
        .stButton>button { background-color: white; color: #5E5E5E; }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    body { direction: rtl; text-align: right; }
    .chat-bubble-user, .chat-bubble-bot {
        text-align: right; direction: rtl; padding: 10px; border-radius: 12px; margin: 8px 50px 8px 10px;
    }
    .msg-container { display: flex; align-items: flex-start; }
    .msg-container.user { justify-content: flex-end; }
    .msg-container.bot { justify-content: flex-start; }
    .timestamp { font-size: 10px; color: gray; margin-top: 4px; text-align: left; }
    </style>
    """, unsafe_allow_html=True)


# ---------- سایدبار (کاملاً مشابه کد شما) ----------
with st.sidebar:
    theme = st.selectbox("🎨 انتخاب تم", ["روشن", "تیره"])
apply_theme(theme)

# ---------- بدنه اصلی (کاملاً مشابه کد شما) ----------
st.title("NRI help bot")

# ---------- مدیریت حالت جلسه (کاملاً مشابه کد شما) ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

# ---------- نمایش تاریخچه گفتگو (کاملاً مشابه کد شما) ----------
for msg in st.session_state.chat_history:
    is_user = msg["sender"] == "user"
    bubble_class = "chat-bubble-user" if is_user else "chat-bubble-bot"
    container_class = "msg-container user" if is_user else "msg-container bot"
    with st.container():
        st.markdown(f"""
        <div class="{container_class}">
            <div>
                <div class="{bubble_class}">{msg['text']}</div>
                <div class="timestamp">{msg['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ---------- ورودی کاربر و دکمه‌ها (کاملاً مشابه کد شما) ----------
def on_input_change():
    st.session_state.input_text = st.session_state.input_box


user_input = st.text_input(
    "✍️ سوال خود را وارد کنید:",
    key="input_box",
    value="" if st.session_state.clear_input else st.session_state.input_text,
    on_change=on_input_change
)

if st.session_state.clear_input:
    st.session_state.clear_input = False

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("📨 ارسال") and user_input.strip():
        timestamp = datetime.now().strftime("%H:%M")

        # ذخیره سوال کاربر (کاملاً مشابه کد شما)
        st.session_state.chat_history.append({
            "sender": "user",
            "text": user_input,
            "time": timestamp
        })

        # دریافت پاسخ از بک‌اند (تنها تغییر اصلی)
        bot_answer = get_clean_answer(user_input)

        # ذخیره پاسخ ربات (کاملاً مشابه کد شما)
        st.session_state.chat_history.append({
            "sender": "bot",
            "text": bot_answer,
            "time": timestamp
        })

        st.session_state.input_text = ""
        st.session_state.clear_input = True
        st.rerun()

with col2:
    if st.button("🗑️ پاک‌کردن گفتگو"):
        st.session_state.chat_history = []
        st.session_state.input_text = ""
        st.session_state.clear_input = True
        st.rerun()