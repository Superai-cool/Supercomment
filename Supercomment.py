import streamlit as st
import openai
import os
import random

# Try to import langdetect, fallback if not available
try:
    from langdetect import detect
    lang_detect_available = True
except ImportError:
    lang_detect_available = False

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Page config
st.set_page_config(page_title="Review Reply GPT", layout="centered")

# Modern CSS for styling
st.markdown("""
    <style>
        body {
            background-color: #f4f6f8;
            font-family: 'Segoe UI', sans-serif;
        }
        .block-container {
            max-width: 750px;
            margin: auto;
            padding-top: 2rem;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            font-size: 2.4rem;
        }
        .stTextArea textarea, .stTextInput input {
            font-size: 1rem !important;
            padding: 0.75rem;
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #1a73e8;
            color: white;
            font-size: 1rem;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            border: none;
        }
        .response-box {
            background-color: #ffffff;
            padding: 1.5rem;
            margin-top: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            font-size: 1.05rem;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .small-text {
            font-size: 0.9rem;
            color: #888;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("💬 Review Reply GPT")

st.markdown("Craft short, human-like replies to Google Reviews (20–50 words only).")

# Session state for response
if "reply" not in st.session_state:
    st.session_state.reply = ""
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

# Inputs
review = st.text_area("📝 Paste Google Review", height=150, placeholder="E.g., Amazing coffee and kind staff!")
tone = st.selectbox("🎯 Choose Reply Tone", ["Professional", "Friendly", "Empathetic", "Apologetic", "Appreciative"])

# Optional: language detection
if review.strip() and lang_detect_available:
    detected_lang = detect(review)
    if detected_lang != "en":
        st.markdown(f"🌐 Detected Language: **{detected_lang.upper()}** (reply will be in English unless specified otherwise)")
        st.markdown("<span class='small-text'>Mention in your review if you'd like the reply translated.</span>", unsafe_allow_html=True)

# Simple sentiment logic
def guess_sentiment(text):
    text = text.lower()
    if any(x in text for x in ["bad", "worst", "disappointed", "rude", "problem"]):
        return "Negative"
    elif any(x in text for x in ["okay", "decent", "average"]):
        return "Neutral"
    return "Positive"

sentiment = guess_sentiment(review) if review.strip() else None
if sentiment:
    st.markdown(f"🧠 **Detected Sentiment:** `{sentiment}`")

# Prompt builder
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

# Generate GPT reply
def generate_reply():
    try:
        prompt = build_prompt(review, tone)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=random.uniform(0.6, 0.8),
            max_tokens=150
        )
        st.session_state.reply = response['choices'][0]['message']['content'].strip()
        st.session_state.prompt = prompt
    except Exception as e:
        st.error(f"Error generating reply: {e}")
        st.session_state.reply = ""

# Buttons
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("✨ Generate Reply"):
        if not review.strip():
