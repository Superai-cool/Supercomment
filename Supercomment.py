import streamlit as st
import openai
import os
import random

# Set your OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Page config
st.set_page_config(page_title="Supercomment", layout="centered")

# --- Styling ---
st.markdown("""
    <style>
        body {
            background-color: #f4f6f8;
            font-family: 'Segoe UI', sans-serif;
        }
        .block-container {
            max-width: 700px;
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
        .generate-btn {
            background-color: #1a73e8 !important;
            color: white !important;
        }
        .clear-btn {
            background-color: #e63946 !important;
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
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "copied" not in st.session_state:
    st.session_state.copied = False

# --- Inputs ---
review = st.text_area("📝 Paste Google Review", height=140, placeholder="E.g., Great service but the wait was a bit long.")
tone = st.selectbox("🎯 Choose Reply Tone", ["Professional", "Friendly", "Empathetic", "Apologetic", "Appreciative"])

# --- Sentiment Detection (simple keywords) ---
def detect_sentiment(text):
    text = text.lower()
    if any(word in text for word in ["bad", "worst", "rude", "disappointed", "issue", "wait", "problem"]):
        return "Negative"
    elif any(word in text for word in ["okay", "average", "decent", "not bad", "could be better"]):
        return "Neutral"
    return "Positive"

sentiment = detect_sentiment(review) if review.strip() else None
if sentiment:
    st.markdown(f"🧠 **Detected Sentiment:** `{sentiment}`")

# --- Prompt Builder ---
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

# --- GPT Call ---
def generate_reply():
    prompt = build_prompt(review, tone)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=random.uniform(0.6, 0.8),
            max_tokens=150
        )
        st.session_state.reply = response['choices'][0]['message']['content'].strip()
        st.session_state.prompt = prompt
        st.session_state.copied = False
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.reply = ""

# --- Clear App State ---
def clear_state():
    st.session_state.reply = ""
    st.session_state.prompt = ""
    st.session_state.copied = False

# --- Buttons ---
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("✨ Generate Reply", key="generate", help="Generate reply from GPT", type="primary"):
        if review.strip():
            generate_reply()
        else:
            st.warning("Please paste a review first.")

with col2:
    if st.button("🔄 Regenerate", key="regen", help="Get another version"):
        if st.session_state.prompt:
            generate_reply()
        else:
            st.warning("Generate a reply first before regenerating.")

with col3:
    if st.button("🧹 Clear", key="clear", help="Clear everything", type="secondary"):
        clear_state()

# --- Output Section ---
if st.session_state.reply:
    st.markdown("### ✅ Suggested Reply")
    st.markdown(f"<div class='response-box'>{st.session_state.reply}</div>", unsafe_allow_html=True)

    # --- Copy to Clipboard JS with dynamic change ---
    copy_label = "📋 Copy Reply" if not st.session_state.copied else "✅ Copied!"
    copy_script = f"""
    <script>
    function copyToClipboard(text) {{
        navigator.clipboard.writeText(text).then(function() {{
            const btn = document.getElementById("copy-btn");
            btn.innerText = "✅ Copied!";
        }});
    }}
    </script>
    <button id="copy-btn" onclick="copyToClipboard(`{st.session_state.reply}`)"
            style="margin-top: 10px; padding: 8px 16px; font-size: 16px;
            border-radius: 8px; background-color: #1a73e8;
            color: white; border: none;">{copy_label}</button>
    """
    st.markdown(copy_script, unsafe_allow_html=True)
    st.session_state.copied = True
