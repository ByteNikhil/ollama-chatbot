# streamlit_app.py (final fixed version for Streamlit >=1.27)
import os
import html
import streamlit as st
import requests

# ---------------------
# CONFIG
# ---------------------
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/chat")  # FastAPI endpoint
RESET_URL = os.getenv("RESET_URL", "http://127.0.0.1:8000/reset")
REQUEST_TIMEOUT = 30  # seconds

st.set_page_config(page_title="Ollama Chatbot", page_icon="🤖", layout="wide")

# ---------------------
# SESSION STATE
# ---------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": "..."}

# ---------------------
# STYLING
# ---------------------
st.markdown(
    """
    <style>
    .chat-row { display: flex; margin: 8px 0; }
    .chatbox {
        padding: 12px;
        border-radius: 12px;
        max-width: 70%;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    .user {
        background-color: #0084ff;
        color: white;
        margin-left: auto;
    }
    .assistant {
        background-color: #e4e6eb;
        color: black;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 Ollama Chatbot")
st.markdown("Ask anything! Powered by **Ollama LLM**.")

# ---------------------
# RESET CHAT
# ---------------------
col1, col2 = st.columns([1, 6])
with col1:
    if st.button("Reset Chat"):
        try:
            # call reset endpoint (if available)
            try:
                requests.post(RESET_URL, timeout=REQUEST_TIMEOUT)
            except Exception:
                pass  # ignore network errors for reset

            st.session_state.messages = []
            st.success("Chat reset.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to reset chat: {e}")

with col2:
    st.write("")  # spacing alignment

# ---------------------
# USER INPUT (form)
# ---------------------
with st.form(key="input_form", clear_on_submit=True):
    user_text = st.text_input(
        "You:",
        key="chat_input",
        placeholder="Type your message and press Send...",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Send")

if submitted and user_text.strip():
    message_text = user_text.strip()

    # append user message
    st.session_state.messages.append({"role": "user", "content": message_text})

    # call backend
    assistant_reply = ""
    try:
        with st.spinner("Contacting model..."):
            resp = requests.post(API_URL, json={"message": message_text}, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()

            try:
                resp_json = resp.json()
            except ValueError:
                resp_json = None

            if isinstance(resp_json, dict):
                assistant_reply = (
                    resp_json.get("reply")
                    or resp_json.get("response")
                    or resp_json.get("answer")
                    or resp_json.get("message")
                    or str(resp_json)
                )
            else:
                assistant_reply = resp.text.strip() or "(empty response)"
    except requests.exceptions.Timeout:
        assistant_reply = "Error: request timed out."
    except requests.exceptions.RequestException as e:
        assistant_reply = f"Error: {e}"
    except Exception as e:
        assistant_reply = f"Unexpected error: {e}"

    # append assistant reply
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    st.rerun()

# ---------------------
# DISPLAY CHAT
# ---------------------
if not st.session_state.messages:
    st.info("No messages yet — say hi 👋")

for msg in st.session_state.messages:
    safe_content = html.escape(msg["content"] or "")
    safe_content = safe_content.replace("\n", "<br>")  # keep line breaks
    if msg["role"] == "user":
        st.markdown(
            f'<div class="chat-row"><div class="chatbox user">{safe_content}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="chat-row"><div class="chatbox assistant">{safe_content}</div></div>',
            unsafe_allow_html=True,
        )
