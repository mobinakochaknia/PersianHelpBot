import streamlit as st
from datetime import datetime
from main import get_clean_answer
import uuid
import os, warnings
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # فقط CPU
os.environ["OMP_NUM_THREADS"] = str(min(8, os.cpu_count() or 8))
os.environ["MKL_NUM_THREADS"] = str(min(8, os.cpu_count() or 8))

# هشدارهای بی‌مصرف
warnings.filterwarnings("ignore", message="`encoder_attention_mask` is deprecated", category=FutureWarning)

# ---------- تنظیمات اولیه ----------
st.set_page_config(page_title="NRI help bot", page_icon="💬", layout="centered")

# ---------- استایل‌ها ----------
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
        .stApp { background-color: rgb(0,0,0,0.7); color: #f1f1f1; }
        .chat-bubble-user { background-color: #0a84ff; color: white; }
        .chat-bubble-bot { background-color: #2c2c2c; color: white; }
        .stTextInput label, .stSelectbox label { color: #f1f1f1 !important; }
        .stButton>button { background-color: white; color: #5E5E5E; }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    body { direction: rtl; text-align: right; }
    h1 { text-align: center !important; width: 100% !important; }
    .chat-bubble-user, .chat-bubble-bot {
        text-align: right; direction: rtl; padding: 10px; border-radius: 12px; margin: 8px 10px 8px 50px;
        white-space: normal !important; word-break: break-word !important; overflow-wrap: break-word !important;
    }
    .msg-container { display: flex; align-items: flex-start; }
    .msg-container.user { justify-content: flex-start; }
    .msg-container.bot { justify-content: flex-end; }
    .timestamp { font-size: 10px; color: gray; margin-top: 4px; text-align: left; }
    .chat-bubble-user ol, .chat-bubble-user ul,
    .chat-bubble-bot ol, .chat-bubble-bot ul {
        margin: 0 0 0 1.2em; padding-left: 1em; list-style-position: inside;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- مخفی‌کردن کامل پیام‌های Enter/Submit در تمام ورژن‌ها ---
    st.markdown("""
    <style>
    /* پیام راهنمای ویجت‌ها مثل "Press Enter to apply/submit" */
    [data-testid="stWidgetInstructions"] { display: none !important; }
    /* برخی نسخه‌ها کنار text_input پیام aria-live می‌گذارند */
    [data-testid="stTextInput"] [aria-live="polite"] { display: none !important; }
    /* اگر جایی از فرم استفاده شد، پیام submit فرم را هم مخفی کن */
    [data-testid="stFormSubmitterMessage"] { display: none !important; }
    .stForm [data-testid="stFormSubmitter"] > div:nth-child(2) { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# ---------- مدیریت حالت جلسه ----------
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
    st.session_state.current_conversation_id = None

# اگر هیچ مکالمه‌ای وجود ندارد، یک مکالمه جدید ایجاد کنید
if not st.session_state.conversations:
    new_conv_id = str(uuid.uuid4())
    st.session_state.conversations[new_conv_id] = {
        "messages": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "title": "مکالمه جدید"
    }
    st.session_state.current_conversation_id = new_conv_id

# ---------- سایدبار ----------
with st.sidebar:
    theme = st.selectbox("🎨 انتخاب تم", ["روشن", "تیره"])

    if st.button("💬 مکالمه جدید"):
        new_conv_id = str(uuid.uuid4())
        st.session_state.conversations[new_conv_id] = {
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": "مکالمه جدید"  # عنوان موقت
        }
        st.session_state.current_conversation_id = new_conv_id
        st.rerun()

    # نمایش لیست مکالمات
    st.markdown("### مکالمات")
    for conv_id, conv_data in st.session_state.conversations.items():
        if st.button(f"{conv_data['title']}", key=f"conv_{conv_id}"):
            st.session_state.current_conversation_id = conv_id
            st.rerun()

apply_theme(theme)

@st.cache_resource(show_spinner=False)
def get_app_state():
    # فقط یک‌بار در طول عمر اپ اجرا می‌شود
    from search_similarity import load_components  # مدل SBERT + متادیتا + FAISS
    from hybrid_search import build_bm25           # BM25 و سوال‌ها
    model, metadata, index = load_components()
    bm25, questions, _ = build_bm25(metadata)
    return {"model": model, "metadata": metadata, "index": index, "bm25": bm25, "questions": questions}

STATE = get_app_state()

# ---------- بدنه اصلی ----------
st.title("NRI help bot")

# نمایش تاریخچه مکالمه فعلی
current_conv = st.session_state.conversations[st.session_state.current_conversation_id]
for msg in current_conv["messages"]:
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

# ---------- ورودی کاربر ----------
def on_input_change():
    st.session_state.input_text = st.session_state.input_box

user_input = st.text_input(
    "سوال",                             # لیبل مخفی می‌شود
    key="input_box",
    value="" if st.session_state.get("clear_input", False) else st.session_state.get("input_text", ""),
    placeholder="سوال خود را وارد کنید",  # فقط placeholder دیده می‌شود
    label_visibility="collapsed",       # عدم نمایش لیبل
    on_change=on_input_change
)

if st.session_state.get("clear_input", False):
    st.session_state.clear_input = False

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("📨 ارسال") and user_input.strip():
        user_ts = datetime.now().strftime("%H:%M")

        if len(current_conv["messages"]) == 0:
            current_conv["title"] = user_input[:30] + "..." if len(user_input) > 30 else user_input

        current_conv["messages"].append({"sender": "user", "text": user_input, "time": user_ts})

        # ⬅️ با کش
        with st.spinner("در حال تهیه پاسخ..."):
            bot_answer = get_clean_answer(user_input, state=STATE)

        bot_ts = datetime.now().strftime("%H:%M")
        current_conv["messages"].append({"sender": "bot", "text": bot_answer, "time": bot_ts})

        st.session_state.input_text = ""
        st.session_state.clear_input = True
        st.rerun()

with col2:
    if st.button("🗑️ پاک‌کردن گفتگو"):
        current_conv["messages"] = []
        st.session_state.input_text = ""
        st.session_state.clear_input = True
        st.rerun()
