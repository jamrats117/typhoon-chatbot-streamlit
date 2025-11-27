import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Typhoon Chatbot", page_icon="🌪️")

st.title("🌪️ Typhoon Chatbot – Streamlit Cloud")

# connect Typhoon API
client = OpenAI(
    api_key=st.secrets["TYPHOON_API_KEY"],
    base_url="https://api.opentyphoon.ai/v1"
)

# chat history
if "history" not in st.session_state:
    st.session_state.history = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant named Typhoon created by SCB 10X. "
                "Be helpful, harmless, honest. "
                "Do NOT begin responses with filler phrases like 'Certainly', "
                "'Of course', 'Sure', etc. "
                "Always respond in the same language the user uses."
            )
        }
    ]

# show previous messages
for msg in st.session_state.history[1:]:   # skip system message
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# input area
user_msg = st.chat_input("ถามอะไรก็ได้…")

if user_msg:
    # add user message to history
    st.session_state.history.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.write(user_msg)

    # streaming response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        stream = client.chat.completions.create(
            model="typhoon-v2.5-30b-a3b-instruct",
            messages=st.session_state.history,
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9,
            repetition_penalty=1.1,
            stream=True,
        )

        for chunk in stream:
            token = chunk.choices[0].delta.get("content", "")
            full_reply += token
            placeholder.write(full_reply)

        # add assistant reply to history
        st.session_state.history.append(
            {"role": "assistant", "content": full_reply}
        )
