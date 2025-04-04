import streamlit as st
import openai
import os
import random

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Configure Streamlit app
st.set_page_config(page_title="EasyReply", layout="centered")

# ✅ CSS for modern, responsive UI
st.markdown("""
    <style>
        body {
            background-color: #f9fafb;
            font-family: 'Segoe UI', sans-serif;
        }
        .block-container {
            max-width: 700px;
            margin: auto;
            padding-top: 2rem;
        }
        h1 {
            text-align: center;
            color: #111827;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .stTextArea textarea, .stSelectbox div {
            font-size: 1rem !important;
        }
        .response-box {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            font-size: 1.05rem;
            line-height: 1.6;
            white-space: pre-wrap;
            margin-top: 1rem;
        }
        .btn-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1.25rem;
        }
        .btn-row button {
            width: 100%;
            flex: 1;
            padding: 0.7rem;
            font-size: 1rem;
            border-radius: 8px;
            border: none;
            color: white;
        }
        .generate-btn {
            background-color: #1d4ed8;
        }
        .regen-btn {
            background-color: #0ea5e9;
        }
        .clear-btn {
            background-color: #ef4444;
        }
        @media (max-width: 500px) {
            .btn-row {
                flex-direction: column;
            }
        }
    </style>
""", unsafe_allow_html=True)

# 🧠 Prompt Builder
def build_prompt(review, tone):
    return f"""
You are a specialized GPT assistant designed solely for generating short, professional replies to Google Reviews.

ONLY respond with a reply (no explanations). Use the tone: {tone}.

REVIEW:
\"\"\"{review}\"\"\"

Rules:
- Only generate a short reply (20–50 words).
- No emojis.
- Don't use generic intros like "Dear Customer" unless it fits.
- Reflect tone and content of review.
- Stay authentic and specific.
- If review is not relevant, reply:
  "This GPT is designed only to generate short replies to Google Reviews. Please paste a review and select a tone to receive a reply."
"""

# 🚀 GPT Generator
def generate_reply():
    prompt = build_prompt(st.session_state.review, st.session_state.tone)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=random.uniform(0.6, 0.8),
            max_tokens=150
        )
        st.session_state.reply = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.reply = ""

# 🧼 Clear App State and Rerun
def clear_app():
    for key in ["review", "tone", "reply"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()  # ✅ Correct API

# 🔄 Session Defaults
if "review" not in st.session_state:
    st.session_state.review = ""
if "tone" not in st.session_state:
    st.session_state.tone = "Professional"
if "reply" not in st.session_state:
    st.session_state.reply = ""

# 🏷️ Title
st.markdown("<h1>💬 EasyReply</h1>", unsafe_allow_html=True)
st.markdown("""EasyReply uses AI to craft thoughtful, personalized responses to Google reviews.  
Turn every review into a relationship — easily and professionally.""")

# ✍️ Input Fields
st.session_state.review = st.text_area("📝 Paste Google Review", value=st.session_state.review, height=140)
st.session_state.tone = st.selectbox(
    "🎯 Choose Reply Tone",
    ["Professional", "Friendly", "Empathetic", "Apologetic", "Appreciative"],
    index=["Professional", "Friendly", "Empathetic", "Apologetic", "Appreciative"].index(st.session_state.tone)
)

# 🚦 Action Buttons
st.markdown('<div class="btn-row">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("✨ Generate Reply"):
        if st.session_state.review.strip():
            generate_reply()
        else:
            st.warning("Please paste a review.")
with col2:
    if st.button("🔄 Regenerate"):
        if st.session_state.reply:
            generate_reply()
        else:
            st.warning("Generate a reply first.")
with col3:
    if st.button("🧹 Clear"):
        clear_app()
st.markdown('</div>', unsafe_allow_html=True)

# ✅ Show GPT Reply
if st.session_state.reply:
    st.markdown("### ✅ Suggested Reply")
    st.markdown(f"<div class='response-box'>{st.session_state.reply}</div>", unsafe_allow_html=True)
