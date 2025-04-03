import streamlit as st
import openai
import os
import random

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Streamlit app settings
st.set_page_config(page_title="Supercomment", layout="centered")

# 🌟 Custom CSS for responsive and aesthetic UI
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
        .sentiment {
            font-weight: bold;
            color: #10b981;
        }
        @media (max-width: 500px) {
            .btn-row {
                flex-direction: column;
            }
        }
    </style>
""", unsafe_allow_html=True)

# 🧠 Sentiment detection
def detect_sentiment(text):
    text = text.lower()
    if any(word in text for word in ["bad", "worst", "rude", "disappointed", "issue", "wait", "problem"]):
        return "Negative"
    elif any(word in text for word in ["okay", "average", "decent", "not bad", "could be better"]):
        return "Neutral"
    return "Positive"

# ✨ Prompt builder
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
- Reflect tone and sentiment of review.
- Stay authentic and specific.
- If review is not relevant, reply:
  "This GPT is designed only to generate short replies to Google Reviews. Please paste a review and select a tone to receive a reply."
"""

# 🔁 GPT call
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

# 🧼 Clear state
def clear_all():
    st.session_state.review = ""
    st.session_state.tone = "Professional"
    st.session_state.reply = ""

# 🎯 Session state init
if "review" not in st.session_state:
    st.session_state.review = ""
if "tone" not in st.session_state:
    st.session_state.tone = "Professional"
if "reply" not in st.session_state:
    st.session_state.reply = ""

# 🏷️ Title
st.markdown("<h1>💬 Supercomment</h1>", unsafe_allow_html=True)
st.markdown("Reply to Google Reviews like a pro — in under 50 words.")

# 📝 Input area
st.session_state.review = st.text_area("📝 Paste Google Review", value=st.session_state.review, height=140)
st.session_state.tone = st.selectbox("🎯 Choose Reply Tone", ["Professional", "Friendly", "Empathetic", "Apologetic", "Appreciative"], index=["Professional", "Friendly", "Empathetic", "Apologetic", "Appreciative"].index(st.session_state.tone))

# 📊 Sentiment display
if st.session_state.review.strip():
    sentiment = detect_sentiment(st.session_state.review)
    st.markdown(f"🔍 **Detected Sentiment:** <span class='sentiment'>{sentiment}</span>", unsafe_allow_html=True)

# 🚀 Button row
st.markdown('<div class="btn-row">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("✨ Generate Reply", key="generate"):
        if st.session_state.review.strip():
            generate_reply()
        else:
            st.warning("Please paste a review first.")
with col2:
    if st.button("🔄 Regenerate", key="regenerate"):
        if st.session_state.reply:
            generate_reply()
        else:
            st.warning("Please generate a reply first.")
with col3:
    if st.button("🧹 Clear", key="clear"):
        clear_all()
st.markdown('</div>', unsafe_allow_html=True)

# ✅ Display reply
if st.session_state.reply:
    st.markdown("### ✅ Suggested Reply")
    st.markdown(f"<div class='response-box'>{st.session_state.reply}</div>", unsafe_allow_html=True)
