import streamlit as st
import requests

st.set_page_config(page_title="Typhoon OCR + Chat", page_icon="🌪️")

st.title("🌪️ Typhoon OCR + Chatbot")

API_KEY = st.secrets["TYPHOON_API_KEY"]
OCR_URL = "https://api.opentyphoon.ai/v1/ocr"
CHAT_URL = "https://api.opentyphoon.ai/v1/chat/completions"
MODEL_OCR = "typhoon-ocr"
MODEL_CHAT = "typhoon-v2.5-30b-a3b-instruct"

# ---------- State ----------
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

if "history" not in st.session_state:
    # เก็บเฉพาะ user / assistant (system จะสร้างใหม่ทุกครั้ง)
    st.session_state.history = []


# ---------- ฟังก์ชันเรียก Typhoon OCR ----------
def call_typhoon_ocr(uploaded_file):
    files = {
        "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
    }

    data = {
        "model": MODEL_OCR,
        "task_type": "default",
        "max_tokens": "16000",
        "temperature": "0.1",
        "top_p": "0.6",
        "repetition_penalty": "1.1",
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    resp = requests.post(OCR_URL, headers=headers, files=files, data=data, timeout=120)
    resp.raise_for_status()
    result = resp.json()

    texts = []
    for page in result.get("results", []):
        if page.get("success") and page.get("message"):
            content = page["message"]["choices"][0]["message"]["content"]
            # พยายามดึง natural_text ถ้าเป็น JSON
            try:
                parsed = eval(content)
                content = parsed.get("natural_text", content)
            except Exception:
                pass
            texts.append(content)
    return "\n\n".join(texts)


# ---------- ฟังก์ชันเรียก Typhoon Chat ----------
def call_typhoon_chat(user_message: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # system message พื้นฐาน
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant named Typhoon created by SCB 10X. "
                "Be helpful, harmless, and honest. "
                "Avoid starting responses with filler like 'Certainly', 'Of course', etc. "
                "Always respond in the same language as the user."
            ),
        }
    ]

    # ถ้ามีข้อความ OCR ให้ส่งไปเป็น context เพิ่ม
    if st.session_state.ocr_text:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Here is text extracted from a document using OCR. "
                    "Use it as the primary context when answering questions:\n\n"
                    + st.session_state.ocr_text[:8000]  # กันยาวเกิน
                ),
            }
        )

    # ต่อด้วยประวัติเดิม
    messages.extend(st.session_state.history)

    # เติมข้อความ user รอบนี้
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": MODEL_CHAT,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
    }

    resp = requests.post(CHAT_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ---------- Layout ----------
st.subheader("ขั้นที่ 1: อัปโหลดไฟล์แล้วทำ OCR")

uploaded_file = st.file_uploader(
    "อัปโหลดภาพหรือไฟล์ PDF", type=["jpg", "jpeg", "png", "pdf"]
)

col1, col2 = st.columns(2)

with col1:
    if uploaded_file and st.button("เริ่ม OCR"):
        with st.spinner("กำลังประมวลผล OCR…"):
            try:
                ocr_text = call_typhoon_ocr(uploaded_file)
                st.session_state.ocr_text = ocr_text
                st.success("OCR เสร็จแล้ว! ใช้เป็น context ในการแชทได้เลยด้านล่าง")
            except Exception as e:
                st.error(f"OCR error: {e}")

with col2:
    if st.session_state.ocr_text:
        st.info("มีข้อความ OCR อยู่แล้ว สามารถเริ่มถามคำถามเกี่ยวกับเอกสารนี้ได้")

if st.session_state.ocr_text:
    st.text_area("ผลลัพธ์ OCR (แก้ไขได้ถ้าต้องการ)", 
                 value=st.session_state.ocr_text, 
                 key="ocr_text", 
                 height=200)

st.markdown("---")
st.subheader("ขั้นที่ 2: ถามคำถามเกี่ยวกับเอกสาร (หรือคุยทั่วไปก็ได้)")

# แสดงประวัติแชท
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_msg = st.chat_input("ถาม Typhoon ได้เลย…")

if user_msg:
    # เก็บข้อความ user
    st.session_state.history.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.write(user_msg)

    # ตอบด้วย Typhoon
    with st.chat_message("assistant"):
        with st.spinner("กำลังคิดคำตอบ…"):
            reply = call_typhoon_chat(user_msg)
        st.write(reply)

    st.session_state.history.append({"role": "assistant", "content": reply})
