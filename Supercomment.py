import streamlit as st
import openai
import os
import random

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Streamlit config
st.set_page_config(page_title="Supercomment", layout="centered")

# --- CSS for styling ---
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
            color: #1a202c;
            font-size: 2.4rem;
        }
        .stTextArea textarea, .stTextInput input {
            font-size: 1rem !important;
            padding: 0.75rem;
            border-radius: 10px;
        }
        .stButton>button {
            font-size: 1rem;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            border: none;
        }
        .stButton>button:focus {
            outline: none;
            box-shadow: none;
        }
        .generate-btn {
            background-color: #ef4444 !important;
            color: white !important;
        }
        .regen-btn {
            background-color: #3b82f6 !important;
            color: white !important;
        }
        .clear-btn {
            background-color: #6b7280 !important;
            color: white !important;
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
        .copy-btn {
            margin-top: 10px;
            padding: 8px 16px;
            font-size: 16px;
            border-radius: 8px;
            background-color: #10b981;
            color: white;
            border: none;
        }
        .copy-btn:hover {
            background-color: #059669;
        }
        .sentiment {
            font-weight: bold;
            color: #10b981;
        }
        @media (max-width: 768px) {
            h1 { font-size: 2rem; }
            .response-box { font-size: 1rem; }
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("💬 Supercomment")
st.markdown("Reply to Google Reviews like a pro — in under 50 words.")

# --- Session State ---
if "reply" not in st.session_state:
    st.session_state.reply = ""
if "copied" not in st.session_state:
    st.session_state.copied = False
if "review" not in st.session_state:
    st.session_state.review = ""
if "tone" not in st.session_state:
    st.session_state.tone = "Professional"

# --- Sentiment Detector ---
def detect_sentiment(text):
    text = text.lower()
    if any(word in text for word in ["bad", "worst", "rude", "disappointed", "issue", "wait", "problem"]):
        return "Negative"
    elif any(word in text for word in ["okay", "average", "decent", "not bad", "could be better"]):
        return "Neutral"
    return "Positive"

# --- GPT Prompt Builder ---
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

# --- GPT Generation ---
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
        st.session_state.copied = False
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.reply = ""

# --- UI Elements ---
st.session_state.review = st.text_area("📝 Paste Google Review", value=st.session_state.review, height=140)

st.session_state.tone = st.selectbox("🎯 Choose Reply Tone", ["Professional", "Friendly", "Empathetic", "Apologetic", "Appreciative"], index=["Professional", "Friendly", "Empathetic", "Apologetic", "Appreciative"].index(st.session_state.tone))

# Show sentiment if review present
if st.session_state.review.strip():
    sentiment = detect_sentiment(st.session_state.review)
    st.markdown(f"🔍 **Detected Sentiment:** <span class='sentiment'>{sentiment}</span>", unsafe_allow_html=True)

# Buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("✨ Generate Reply", type="primary"):
        if st.session_state.review.strip():
            generate_reply()
        else:
            st.warning("Please enter a review.")
with col2:
    if st.button("🔄 Regenerate"):
        if st.session_state.reply:
            generate_reply()
        else:
            st.warning("Generate a reply first.")
with col3:
    if st.button("🧹 Clear"):
        st.session_state.reply = ""
        st.session_state.review = ""
        st.session_state.tone = "Professional"
        st.session_state.copied = False

# --- Show reply and copy functionality ---
if st.session_state.reply:
    st.markdown("### ✅ Suggested Reply")
    st.markdown(f"<div class='response-box'>{st.session_state.reply}</div>", unsafe_allow_html=True)

    copy_label = "✅ Copied!" if st.session_state.copied else "📋 Copy Reply"

    if st.button(copy_label, key="copy_reply_btn"):
        st.session_state.copied = True
        st.code(st.session_state.reply, language='')

