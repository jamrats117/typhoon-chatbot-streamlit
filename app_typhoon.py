import streamlit as st
import requests

st.set_page_config(page_title="Typhoon Chatbot", page_icon="🌪️")

st.title("🌪️ Typhoon Chatbot – Streamlit Cloud")

API_KEY = st.secrets["TYPHOON_API_KEY"]
API_URL = "https://api.opentyphoon.ai/v1/chat/completions"
MODEL_NAME = "typhoon-v2.5-30b-a3b-instruct"

def call_typhoon(messages):
    """เรียก Typhoon API แบบ non-stream แล้วคืนข้อความตอบกลับ"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ---------- Chat UI & memory ----------

if "history" not in st.session_state:
    st.session_state.history = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant named Typhoon created by SCB 10X "
                "to be helpful, harmless, and honest. "
                "Avoid starting responses with filler like 'Certainly', 'Of course', etc. "
                "Always answer in the same language as the user."
            ),
        }
    ]

# แสดงประวัติแชท (ข้าม system)
for msg in st.session_state.history[1:]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_msg = st.chat_input("พิมพ์ถาม Typhoon ได้เลย…")

if user_msg:
    # เก็บข้อความ user
    st.session_state.history.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.write(user_msg)

    # เรียก Typhoon
    with st.chat_message("assistant"):
        with st.spinner("กำลังคิดคำตอบ…"):
            reply = call_typhoon(st.session_state.history)
        st.write(reply)

    # เก็บคำตอบ
    st.session_state.history.append({"role": "assistant", "content": reply})
